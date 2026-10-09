"""An agent's hand-back is checked by code before anyone else sees it: well formed passes, every malformation is named."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, fence  # noqa: E402

GOOD_REVIEW = {"previous_step": {"did": ["Split the issue into four stories."], "decided": [], "open": ["Three questions."]},
               "stage": "plan", "round": 1, "verdict": "block", "summary": "One test is missing.",
               "blockers": [{"id": "B1", "criterion": "9.1", "test": None, "problem": "No good-case test.",
                             "evidence": "18 passed against a stub.", "fix": "Add one.", "fixer": "worker"}],
               "notes": [], "outside_plan": [], "resolved": []}
GOOD_WORK = {"summary": "Cause and change.", "criteria": {"9.1": "dokima/x.py, parse()"},
             "evidence": "pytest -q: 12 passed", "replies": [{"blocker": "B1", "answer": "fixed", "why": "Added it."}]}


def test_a_good_review_passes_and_each_malformation_is_named(record_property):
    """A well-formed review has no problems; an approve with blockers, a block without, a bad stage and a bare blocker are each named."""
    record_property("proves", "agent.1")
    assert agent.problems_review(GOOD_REVIEW) == []
    assert agent.problems_review({**GOOD_REVIEW, "verdict": "approve"}) == ["an approve has no blockers"]
    assert agent.problems_review({**GOOD_REVIEW, "blockers": []}) == ["a block needs at least one blocker"]
    found = [{"title": "Board ignores closed PRs", "why": "cards go stale", "evidence": "board.py:40"}]
    assert agent.problems_review({**GOOD_REVIEW, "issues_found": found}) == []
    assert agent.problems_review({**GOOD_REVIEW, "issues_found": [{"title": "x"}]}) == ["issue found 1 needs a title, why and evidence"]
    assert "1. Board ignores closed PRs: cards go stale" in agent.render(rec("reviewer", "plan", {**GOOD_REVIEW, "issues_found": found}))
    bare = agent.problems_review({**GOOD_REVIEW, "blockers": [{"id": "B1"}]})
    assert {"blocker B1 has no criterion", "blocker B1 has no evidence", "blocker B1 has no fix"} <= set(bare)
    assert agent.problems_review({**GOOD_REVIEW, "notes": [{"text": "n", "evidence": "e"}] * 4}) == ["at most three notes"]


def test_a_good_work_passes_and_each_malformation_is_named(record_property):
    """A well-formed work.json has no problems; missing criteria, missing evidence and a reply without a reason are each named."""
    record_property("proves", "agent.2")
    assert agent.problems_work(GOOD_WORK) == []
    assert agent.problems_work({**GOOD_WORK, "criteria": {}}) == ["criteria must give one line per criterion"]
    assert "evidence is empty" in agent.problems_work({**GOOD_WORK, "evidence": " "})[0]
    assert "reply to B1" in agent.problems_work({**GOOD_WORK, "replies": [{"blocker": "B1", "answer": "maybe"}]})[0]


def test_check_fails_closed_on_missing_or_broken_files(record_property, tmp_path, capsys):
    """A missing file or invalid JSON is a failure with its reason, never a pass; a good file passes."""
    record_property("proves", "agent.3")
    assert agent.check("review", str(tmp_path / "none.json")) == 1
    (tmp_path / "bad.json").write_text("{not json")
    assert agent.check("work", str(tmp_path / "bad.json")) == 1
    (tmp_path / "ok.json").write_text(json.dumps(GOOD_REVIEW))
    assert agent.check("review", str(tmp_path / "ok.json")) == 0
    assert "missing" in capsys.readouterr().out


def test_the_fence_reads_scope_from_plan_json(record_property, tmp_path, monkeypatch):
    """Given plan.json, the fence uses its scope list exactly."""
    record_property("proves", "agent.4")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"scope": ["app.py"]}))
    seen = {}
    monkeypatch.setattr(fence, "fence", lambda base, scope: seen.setdefault("scope", scope) and [])
    fence.main(["fence", "BASE", str(plan)])
    assert seen["scope"] == ["app.py"]


def test_only_the_planner_asks_and_its_questions_are_checked(record_property):
    """A question with its assumption passes; anything else is named; review and work may not ask."""
    record_property("proves", "agent.5")
    q = {"question": "Should a failed run move its card to Needs you?", "assumption": "The plan assumes it does."}
    assert agent.problems_questions([q, {"question": "Which board view?", "assumption": "The default one."}]) == []
    assert agent.problems_questions(["Split it?"]) and agent.problems_questions(["Split it?"])[0].startswith("question 1")
    assert agent.problems_questions([{"question": "Split it.", "assumption": "Yes."}])[0].startswith("question 1")
    assert agent.problems_review({**GOOD_REVIEW, "questions": [q]}) == ["the reviewer never asks the owner; escalate on round three instead"]
    assert agent.problems_work({**GOOD_WORK, "questions": [q]}) == ["the worker never asks the owner; the plan is the contract"]


def comment(rec, who="dokima-runtime", t="2026-10-06T10:00:00Z"):
    """A comment as GitHub returns it, carrying a record rendered by code."""
    return {"author": {"login": who}, "body": agent.render(rec), "createdAt": t, "where": "issue #7"}


def rec(role, stage="", handback=None, passed=True, problems=""):
    """A record built the way the workflow builds one, from a temp hand-back folder."""
    import tempfile
    out = tempfile.mkdtemp()
    json.dump(handback or {}, open(os.path.join(out, agent.HANDBACK[role]), "w"))
    return agent.build_record(role, stage, out, problems, passed, {"run_id": "1", "run": "https://x/run/1"})


def test_a_record_survives_its_comment_and_only_the_bot_counts(record_property):
    """A record rendered into a comment reads back exactly; the same text posted by anyone else, or broken JSON, is not a record."""
    record_property("proves", "agent.6")
    r = rec("planner", handback={"kind": "user_story", "user_story": "first",
                                 "questions": [{"question": "Split it?", "assumption": "The plan assumes not."}]})
    assert agent.records([comment(r)]) == [r]
    assert agent.records([comment(r, who="someone")]) == [], "a pasted record from a person was trusted"
    broken = comment(r)
    broken["body"] = broken["body"].replace('"role"', '"role', 1)
    assert agent.records([broken]) == []
    body = agent.render(r)
    assert body.startswith(agent.MARK) and "first" in body and "Split it?" in body and "<details>" in body


def test_only_passed_plans_count_and_rejections_are_kept(record_property):
    """A rejected plan stays in the trail with its problems but is never the plan; a passed record lists no problems."""
    record_property("proves", "agent.7")
    ok = rec("planner", handback={"kind": "user_story", "user_story": "first"}, problems="feature\n")
    bad = rec("planner", handback={"kind": "user_story", "user_story": "second"}, passed=False, problems="criterion 7.2 has no test\n")
    recs = agent.records([comment(ok), comment(bad)])
    assert ok["check"]["problems"] == [], "a passed record listed the checker's normal output as a problem"
    assert agent.latest(recs, "planner")["handback"]["user_story"] == "first"
    assert agent.latest(recs, "planner", passed=False)["check"]["problems"] == ["criterion 7.2 has no test"]
    assert "hand-back rejected by code" in agent.render(bad)


def test_a_missing_hand_back_is_recorded_as_missing(record_property, tmp_path):
    """A run that handed back nothing still leaves a record saying so, never an empty or invented hand-back."""
    record_property("proves", "agent.8")
    r = agent.build_record("worker", "", str(tmp_path), "work.json is missing\n", False, {})
    assert "work.json" in r["handback"]["missing"] and r["check"] == {"passed": False, "problems": ["work.json is missing"]}


def test_the_models_used_come_from_the_session_log(record_property, tmp_path):
    """The record names every model that appears in the run's session log, so a wrong model is visible and can fail the run."""
    record_property("proves", "agent.9")
    log = tmp_path / "logs" / ".claude" / "proj"
    log.mkdir(parents=True)
    (log / "s.jsonl").write_text("\n".join(json.dumps(x) for x in [
        {"message": {"model": "claude-opus-5-5"}}, {"type": "user"}, {"message": {"model": "claude-sonnet-5-5"}}]) + "\nnot json\n")
    assert agent.models_used(str(tmp_path / "logs")) == ["claude-opus-5-5", "claude-sonnet-5-5"]
    assert agent.models_used(str(tmp_path / "none")) == []


def test_the_worker_starts_only_on_a_plan_the_reviewer_approved(record_property):
    """No review, a blocking review, or an approval of an older plan keeps the worker out; an approval of the newest plan lets it in."""
    record_property("proves", "agent.10")
    plan = rec("planner", handback={"kind": "user_story"})
    block = rec("reviewer", "plan", GOOD_REVIEW)
    ok = rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    assert not agent.approved([plan])
    assert not agent.approved([plan, block])
    assert agent.approved([plan, block, ok])
    assert not agent.approved([plan, ok, plan]), "an approval of an older plan let the worker in on a newer one"


def test_a_pack_missing_anything_its_role_needs_is_refused(record_property, tmp_path):
    """A complete pack passes for each role; a missing plan, an empty issue, no comments section, a broken record or a PR pack without the worker's log is named."""
    record_property("proves", "agent.11")
    d = tmp_path / "pack"
    (d / "in").mkdir(parents=True)
    (d / "issue.md").write_text("# Issue #9: t\n\nbody\n\n## Comments\n")
    assert agent.problems_pack("planner", "", str(d)) == []
    assert agent.problems_pack("worker", "", str(d)) == ["plan.json is missing"]
    (d / "plan.json").write_text(json.dumps({"kind": "user_story"}))
    assert agent.problems_pack("reviewer", "plan", str(d)) == []
    assert agent.problems_pack("worker", "", str(d)) == []
    (d / "diff.patch").write_text("+x\n")
    (d / "tests.txt").write_text("1 passed\n")
    (d / "tests.xml").write_text("<testsuite/>\n")
    assert agent.problems_pack("reviewer", "pr", str(d)) == ["worker-run is missing"]
    (d / "worker-run" / "p").mkdir(parents=True)
    assert agent.problems_pack("reviewer", "pr", str(d)) == ["worker-run holds no session log"]
    (d / "worker-run" / "home" / ".claude" / "p").mkdir(parents=True)
    (d / "worker-run" / "home" / ".claude" / "p" / "s.jsonl").write_text("{}\n")
    assert agent.problems_pack("reviewer", "pr", str(d)) == []
    (d / "in" / "01-planner.json").write_text("{not json")
    assert agent.problems_pack("planner", "", str(d)) == ["record 01-planner.json is not valid JSON"]
    (d / "in" / "01-planner.json").write_text(json.dumps({"role": "planner"}))
    assert agent.problems_pack("planner", "", str(d)) == ["record 01-planner.json lacks role, handback or check"]
    (d / "in" / "01-planner.json").unlink()
    (d / "issue.md").write_text("   \n")
    assert agent.problems_pack("planner", "", str(d)) == ["issue.md is empty", "issue.md has no comments section"]


def test_the_pack_reads_the_issue_and_its_pr_as_one_conversation(record_property, tmp_path, monkeypatch):
    """Comments from the issue, its PR, PR reviews and line notes on the code arrive in time order, each labeled with where it was written; records come from both."""
    record_property("proves", "agent.12")
    plan = rec("planner", handback={"kind": "user_story", "user_story": "s"})
    def fake_gh(*args):
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": 7, "title": "T", "body": "B", "comments": [
                {"author": {"login": "owner"}, "body": "/plan first", "createdAt": "2026-01-01T00:00:01Z"},
                {"author": {"login": "dokima-runtime"}, "body": agent.render(plan), "createdAt": "2026-01-01T00:00:03Z"}]})
        if args[:2] == ("pr", "list"):
            return json.dumps([{"number": 9}] if "try/issue-7" in args else [])
        if args[:2] == ("pr", "view"):
            return json.dumps({"comments": [{"author": {"login": "owner"}, "body": "/work change it", "createdAt": "2026-01-01T00:00:04Z"}],
                               "reviews": [{"author": {"login": "owner"}, "body": "line note", "submittedAt": "2026-01-01T00:00:02Z", "state": "COMMENTED"}]})
        if args[0] == "api" and args[1].endswith("/pulls/9/comments"):
            return json.dumps([{"user": {"login": "owner"}, "body": "rename this", "created_at": "2026-01-01T00:00:05Z", "path": "x.py", "line": 3}])
        raise AssertionError(args)
    monkeypatch.setattr(agent, "gh", fake_gh)
    assert agent.pack("o/r", 7, "reviewer", "plan", str(tmp_path / "p"))
    text = (tmp_path / "p" / "issue.md").read_text()
    order = [text.index(x) for x in ("/plan first", "line note", "dokima-record", "/work change it", "rename this")]
    assert order == sorted(order), "the conversation is not in time order"
    assert "on PR #9 review (commented)" in text and "on issue #7" in text and "on PR #9 line note on x.py:3" in text
    assert json.load(open(tmp_path / "p" / "plan.json")) == {"kind": "user_story", "user_story": "s"}
    assert (tmp_path / "p" / "in" / "01-planner.json").exists()


def test_a_command_starts_its_stage_and_anything_else_starts_nothing(record_property):
    """/plan, /work and /review on the first line route to their stage with the right issue; prose, a later-line command or an unlinked PR start nothing."""
    record_property("proves", "agent.13")
    assert agent.route("/plan tighten story 2\nmore words", False, 139) == {"role": "planner", "stage": "", "issue": "139"}
    assert agent.route("/review", False, 139) == {"role": "reviewer", "stage": "plan", "issue": "139"}
    assert agent.route("/review look at x.py", True, 150, "try/issue-139") == {"role": "reviewer", "stage": "pr", "issue": "139"}
    assert agent.route("/WORK fix the line notes", True, 150, "feature-x", "Closes #42") == {"role": "worker", "stage": "", "issue": "42"}
    assert agent.route("looks good to me", False, 139) is None
    assert agent.route("thoughts first\n/plan later", False, 139) is None, "a command not on the first line started a stage"
    assert agent.route("/planner", False, 139) is None
    assert agent.route("/work", True, 150, "feature-x", "no link here") is None, "a PR with no issue started a stage"
    assert agent.route("", False, 139) is None


def test_each_round_answers_every_open_blocker(record_property, tmp_path):
    """Planner and worker must answer every open blocker by id; the reviewer must resolve or keep each earlier one."""
    record_property("proves", "agent.14")
    (tmp_path / "open_blockers.json").write_text(json.dumps([{"id": "B1"}, {"id": "B2"}]))
    assert agent.problems_round("worker", {"replies": [{"blocker": "B1"}, {"blocker": "B2"}]}, str(tmp_path)) == []
    (tmp_path / "issue.md").write_text("# Issue #9: T\n\n## Comments\n")
    (tmp_path / "open_issues.json").write_text("[]")
    links = {"blocked_by": [], "blocks": [], "relates_to": []}
    assert agent.problems_round("planner", {"replies": [{"blocker": "B1"}], "links": links}, str(tmp_path)) == ["blocker B2 is not answered"]
    assert agent.problems_round("reviewer", {"resolved": ["B1"], "blockers": [{"id": "B2"}]}, str(tmp_path)) == []
    assert agent.problems_round("reviewer", {"resolved": ["B1"], "blockers": []}, str(tmp_path)) == ["earlier blocker B2 is neither resolved nor still listed"]
    assert agent.problems_round("worker", {}, str(tmp_path / "none")) == []


def test_open_blockers_come_from_the_newest_review_at_that_stage(record_property):
    """A blocking review leaves its blockers open; a later approval clears them; another stage's review never counts."""
    record_property("proves", "agent.15")
    plan = rec("planner", handback={"kind": "user_story"})
    block = rec("reviewer", "plan", GOOD_REVIEW)
    ok = rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    assert [b["id"] for b in agent.open_blockers([plan, block], "plan")] == ["B1"]
    assert agent.open_blockers([plan, block, ok], "plan") == []
    assert agent.open_blockers([plan, block], "pr") == []


def test_dokimas_own_code_always_runs_from_main(record_property):
    """The runtime is copied from main before any branch is checked out, every Dokima step runs from that copy, and only tests use the branch's code."""
    record_property("proves", "agent.19")
    wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
    assert wf.index("cp -r dokima /tmp/runtime/dokima") < wf.index("name: Starting branch")
    assert "PYTHONPATH: /tmp/runtime" in wf and 'PYTHONSAFEPATH: "1"' in wf
    assert "cat /tmp/runtime/dokima/roles/" in wf and "cat dokima/roles/" not in wf
    for line in wf.splitlines():
        if "python3 -m pytest" in line:
            assert "PYTHONPATH= PYTHONSAFEPATH=" in line, f"tests would run Dokima from main instead of the branch: {line.strip()}"


def test_the_review_sums_up_the_previous_step_in_at_most_five_lines(record_property):
    """A review without a summary of what the planner or worker did, or with more than five lines of it, is named."""
    record_property("proves", "agent.16")
    assert agent.problems_review({**GOOD_REVIEW, "previous_step": {}}) == ["previous_step must sum up what the planner or worker did, decided and left open"]
    long = {"did": ["a", "b", "c"], "decided": ["d", "e"], "open": ["f"]}
    assert agent.problems_review({**GOOD_REVIEW, "previous_step": long}) == ["previous_step holds at most five lines"]


def test_the_conversation_is_saved_readable_and_without_secrets(record_property, tmp_path):
    """The transcript shows what the agent said, the tools it used and their results, and every secret value is removed."""
    record_property("proves", "agent.17")
    log = tmp_path / ".claude" / "p"
    log.mkdir(parents=True)
    secret = "sk-ant-oat01-SECRETSECRET"
    lines = [{"message": {"role": "assistant", "content": [{"type": "text", "text": "Reading the issue."},
                                                         {"type": "tool_use", "name": "Bash", "input": {"command": f"echo {secret}"}}]}},
             {"message": {"role": "user", "content": [{"type": "tool_result", "content": f"token {secret}"}]}}]
    (log / "s.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    t = agent.transcript(str(tmp_path), [secret])
    assert "**Agent:** Reading the issue." in t and "1. Bash" in t and "> token" in t
    assert secret not in t and "[secret removed]" in t
    assert agent.scrub("abc", ["short"]) == "abc"


def test_the_footnote_reports_claudes_own_numbers_and_links_the_conversation(record_property, tmp_path):
    """Time, turns, tokens and cost come from Claude's end-of-run report; a missing report shows none of them, never a guess."""
    record_property("proves", "agent.18")
    (tmp_path / "claude.json").write_text(json.dumps({"duration_ms": 240000, "num_turns": 23, "total_cost_usd": 3.2,
                                                       "usage": {"input_tokens": 1000, "cache_read_input_tokens": 400000, "output_tokens": 18000}}))
    r = {"models": ["claude-opus-5-5"], "report": agent.run_report(str(tmp_path / "claude.json")), "log": "https://g/log.md", "run": "https://g/run"}
    f = agent.footnote(r)
    assert all(x in f for x in ("Opus 5.5", "4.0 min", "23 turns", "401,000 tokens in, 18,000 out", "$3.20 at API prices", "[conversation](https://g/log.md)"))
    bare = agent.footnote({"models": ["claude-opus-5-5"], "report": agent.run_report(str(tmp_path / "none.json"))})
    assert "min" not in bare and "$" not in bare and "tokens" not in bare


SPLIT = {"kind": "feature", "feature": "f", "stories": [
    {"title": "First", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://x/1"}], "non_functional": [], "depends_on": []},
    {"title": "Second", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://x/2"}], "non_functional": [], "depends_on": [0]}]}


def test_an_approved_split_is_filed_as_sub_issues_with_their_order(record_property, monkeypatch):
    """Each story becomes a sub-issue of the parent, in order, with blocked-by links to the stories it depends on; filing twice files nothing."""
    record_property("proves", "agent.20")
    calls = []
    def fake_gh(*args):
        calls.append(args)
        if args[:2] == ("issue", "view"):
            return json.dumps({"title": "Parent"})
        if args[:2] == ("issue", "create"):
            return f"https://github.com/o/r/issues/{200 + sum(1 for c in calls if c[:2] == ('issue', 'create'))}\n"
        if args[0] == "api" and args[1].startswith("repos/o/r/issues/2"):
            return json.dumps({"id": 9000 + int(args[1].split("/")[-1])})
        return "{}"
    monkeypatch.setattr(agent, "gh", fake_gh)
    recs = [rec("planner", handback=SPLIT), rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})]
    r = agent.file_split("o/r", 139, recs)
    assert [(f["story"], f["issue"], f["blocked_by"]) for f in r["handback"]["stories"]] == [(1, 201, []), (2, 202, [1])]
    titles = [c[c.index("--title") + 1] for c in calls if c[:2] == ("issue", "create")]
    assert titles == ["First", "Second"]
    assert ("api", "-X", "POST", "repos/o/r/issues/139/sub_issues", "-F", "sub_issue_id=9201") in calls
    assert ("api", "-X", "POST", "repos/o/r/issues/202/dependencies/blocked_by", "-F", "issue_id=9201") in calls
    body = [c[c.index("--body") + 1] for c in calls if c[:2] == ("issue", "create")][1]
    assert "Part of:** #139 Parent" in body and "u2" in body and "[source](https://x/2)" in body
    card = agent.render(r)
    words = re.sub(r"<img [^>]*>\s*", "", card)  # the field icons code draws (issue #234) are not words
    assert "#202 Second (blocked by #201)" in words and "no model" in words
    calls.clear()
    again = agent.file_split("o/r", 139, recs + [r])
    assert again == r and not [c for c in calls if c[:2] == ("issue", "create")], "filing twice filed new issues"


def test_a_worker_handed_a_split_refuses(record_property, tmp_path):
    """The worker's pack check names a split plan, so no worker ever builds a whole feature."""
    record_property("proves", "agent.21")
    d = tmp_path / "p"
    (d / "in").mkdir(parents=True)
    (d / "issue.md").write_text("# Issue #9: t\n\nbody\n\n## Comments\n")
    (d / "plan.json").write_text(json.dumps(SPLIT))
    assert agent.problems_pack("worker", "", str(d)) == ["plan.json is a split: /work files its stories as sub-issues, no worker builds it"]
    assert agent.problems_pack("reviewer", "plan", str(d)) == []


def test_a_replan_checks_tests_against_where_the_branch_left_main(record_property):
    """On every planning round the plan check compares against the branch's split from main, so earlier rounds' tests still count."""
    record_property("proves", "agent.22")
    wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
    assert 'PLANNER_BASE=$(git merge-base HEAD origin/main)' in wf
    assert "PLANNER_BASE: ${{ env.BASE }}" not in wf, "a step still compares against the branch head"


def test_the_river_hands_each_stage_to_the_next_until_it_needs_the_owner(record_property):
    """Planner to reviewer, worker to reviewer, a block back to the doer; questions, approvals, escalations and rejected hand-backs stop and mention the owner."""
    record_property("proves", "agent.23")
    plan = rec("planner", handback={"kind": "user_story"})
    asks = rec("planner", handback={"kind": "user_story", "questions": ["Which? I planned for A."]})
    work = rec("worker", handback=GOOD_WORK)
    block = rec("reviewer", "plan", GOOD_REVIEW)
    pr_block = rec("reviewer", "pr", GOOD_REVIEW)
    ok = rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    pr_ok = rec("reviewer", "pr", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    esc = rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "escalate"})
    bad = rec("planner", handback={}, passed=False, problems="criterion 9.1 has no test\n")
    assert agent.next_step([], plan, ["owner"]) == ("start", "reviewer", "plan")
    assert agent.next_step([], work, ["owner"]) == ("start", "reviewer", "pr")
    assert agent.next_step([], block, ["owner"]) == ("start", "planner", "")
    assert agent.next_step([], pr_block, ["owner"]) == ("start", "worker", "")
    for r, word in ((asks, "questions"), (ok, "/work"), (pr_ok, "Merge"), (esc, "escalated"), (bad, "rejected by code")):
        step = agent.next_step([], r, ["owner"])
        assert step[0] == "stop" and word in step[1], (r["role"], step)
    assert agent.next_line(("stop", "Your turn."), ["owner"]) == "**Next:** @owner Your turn."
    assert agent.next_line(("start", "reviewer", "plan"), ["owner"]) == "**Next:** The reviewer starts now."


def test_three_blocks_in_a_row_since_the_owner_spoke_go_to_the_owner(record_property):
    """Two earlier blocks at the same stage plus this one stop the river; an owner comment in between resets the count; another stage's blocks never count."""
    record_property("proves", "agent.24")
    block = rec("reviewer", "plan", GOOD_REVIEW)
    pr_block = rec("reviewer", "pr", GOOD_REVIEW)
    owner = {"author": {"login": "owner"}, "body": "/plan try again", "createdAt": "t", "where": "issue #7"}
    two = [comment(block), comment(rec("planner", handback={"kind": "user_story"})), comment(block)]
    step = agent.next_step(two, block, ["owner"])
    assert step[0] == "stop" and "3 blocking reviews in a row" in step[1]
    assert agent.next_step(two[:1] + [owner] + two[2:], block, ["owner"]) == ("start", "planner", "")
    assert agent.next_step([comment(pr_block), comment(pr_block)], block, ["owner"]) == ("start", "planner", "")


def test_the_rivers_signal_comes_only_from_dokimas_bot(record_property):
    """The workflow listens for the bot's dokima-next signal, lets only that bot skip the code-owner gate, and starts the next stage after posting."""
    record_property("proves", "agent.25")
    wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
    assert "types: [dokima-next]" in wf
    assert '[ "$EVENT" = repository_dispatch ] && [ "$SENDER" = "dokima-runtime[bot]" ] && exit 0' in wf
    assert wf.index("name: Decide what follows") < wf.index("name: Post the record as a comment") < wf.index("name: Start the next stage")
    assert "group: agent-${{ (inputs.issue || github.event.client_payload.issue) }}" in wf


def test_the_card_shows_the_running_stage_and_needs_you_only_when_it_is_the_owners_turn(record_property, monkeypatch):
    """Each step puts the issue and its open PR in the running stage's column, with the Needs you pill exactly when the river stops."""
    record_property("proves", "agent.26")
    plan = rec("planner", handback={"kind": "user_story"})
    ok = rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    pr_ok = rec("reviewer", "pr", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})
    assert agent.board_place(plan, ("start", "reviewer", "plan")) == ("Plan", False)
    assert agent.board_place(rec("worker", handback=GOOD_WORK), ("start", "reviewer", "pr")) == ("Review", False)
    assert agent.board_place(rec("reviewer", "pr", GOOD_REVIEW), ("start", "worker", "")) == ("Work", False)
    assert agent.board_place(ok, ("stop", "x")) == ("Plan", True)
    assert agent.board_place(pr_ok, ("stop", "x")) == ("Review", True)
    moves = []
    class FakeBoard:
        def __init__(self, *a): pass
        def item(self, kind, n): return (kind, n)
        def set(self, iid, field, option): moves.append((iid, field, option))
    from dokima import board
    monkeypatch.setattr(board, "Board", FakeBoard)
    monkeypatch.setattr(agent, "gh", lambda *a: "161\n")
    assert agent.move_card("o/r", "157", "Review", True, "o/1") == [("issue", 157), ("pr", 161)]
    assert (("pr", 161), "Action", "Needs you") in moves and (("issue", 157), "Status", "Review") in moves


def test_a_replan_is_judged_only_on_what_the_planner_changed_in_its_run(record_property, tmp_path, monkeypatch):
    """The worker's earlier code on the branch is never blamed on the planner; a code file the planner itself changes still is."""
    record_property("proves", "agent.27")
    from dokima import planner
    out = tmp_path / "out"
    out.mkdir()
    plan = {"kind": "user_story", "summary": "s", "user_story": "s", "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/9"}],
            "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [], "tests": {"9.1": ["tests/test_x.py::test_a"]}}
    (out / "plan.json").write_text(json.dumps(plan))
    since = {"SPLIT": ["dokima/x.py", "tests/test_x.py"], "RUN": ["tests/test_x.py"]}
    monkeypatch.setattr(planner, "changed_files", lambda base: since[base])
    monkeypatch.setenv("PLANNER_BASE", "SPLIT")
    monkeypatch.setenv("PLANNER_RUN_BASE", "RUN")
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    planner.main(["planner", "check", "9", str(out)])
    why = (out / "rejected.txt").read_text() if (out / "rejected.txt").exists() else ""
    assert "outside tests" not in why, f"the worker's code was blamed on the planner: {why}"
    since["RUN"] = ["dokima/x.py", "tests/test_x.py"]
    (out / "rejected.txt").unlink(missing_ok=True)
    planner.main(["planner", "check", "9", str(out)])
    assert "dokima/x.py is outside tests/" in (out / "rejected.txt").read_text()

"""The worker's and reviewer's hand-backs are checked against their prompt's shape and the approved plan, from outside.

Every test runs the real command the workflow runs, `python3 -m dokima.agent check review|work FILE PLAN N`, on files in
a temp folder, so it proves what a run sees: the exit code, the reasons printed, and never a crash. A plan for issue 9
with two acceptance criteria and one non-functional requirement (9.1, 9.2, 9.3) stands in for the approved plan.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STORY = {"kind": "user_story", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://x/9"}, {"text": "b", "source": "https://x/9"}],
         "non_functional": [{"text": "c", "why": "w", "principle": "Fail closed"}],
         "scope": ["dokima/x.py"], "out_of_scope": [],
         "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_c"]}}
SPLIT = {"kind": "feature", "feature": "f", "stories": [
    {"title": "One", "user_story": {"short": "u1", "full": "u1, in full."}, "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
     "non_functional": [{"text": "n", "why": "w"}], "depends_on": []},
    {"title": "Two", "user_story": {"short": "u2", "full": "u2, in full."}, "acceptance_criteria": [{"text": "b", "source": "https://x/9"}],
     "non_functional": [], "depends_on": [0]}]}

# Every ask a plan review lists, matched to the story's 9.1 or a split's S1.1: a plan review must list them, a code
# review may, so the well-formed samples pass code's check on whatever stage the machine runs (#244).
ASKS = [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"}]
SPLIT_ASKS = [dict(ASKS[0], criterion="S1.1")]
STAGES = ("", "plan", "pr")  # the stage a machine may run on: none (CI), a plan review's or a code review's

REVIEW = {"previous_step": {"did": ["Wrote three criteria."], "decided": [], "open": []},
          "verdict": "block", "summary": "One proof is missing.",
          "raises": [{"kind": "blocker", "to": "worker", "label": "9.1", "text": "No test.", "full": "The whole detail, for agents.", "evidence": "plan.json"},
                     {"kind": "issue", "text": "t: w", "full": "The whole detail, for agents.", "evidence": "e"}],
          "answers": [{"raise": "W1", "answer": "done", "why": "The test is weak."}], "asks": ASKS,
          "size": "ok",
          "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3")], "edge_cases": [{"criterion": c, "cut": [], "missing": []} for c in ("9.1", "9.2", "9.3")],
          "tests": [{"test": f"tests/test_x.py::test_{x}", "only_its_behavior": True, "why": "one result"} for x in "abc"]}
WORK = {"summary": "Cause and change.", "criteria": {"9.1": "x.py, a()", "9.2": "x.py, b()", "9.3": "x.py, c()"},
        "evidence": "pytest -q: 3 passed",
        "raises": [],
        "answers": [{"raise": "R1", "answer": "done", "why": "Added it."}]}


def on_stage(monkeypatch, stage):
    """Make this machine run on `stage`, the way the workflow sets STAGE for a reviewer: none, plan or pr."""
    if stage:
        monkeypatch.setenv("STAGE", stage)
    else:
        monkeypatch.delenv("STAGE", raising=False)


def run(tmp_path, *args):
    """Run Dokima's agent command from the repo root, the way the workflow does; return (exit code, stdout, stderr)."""
    env = {**os.environ, "PYTHONPATH": ROOT}
    # A worker's or reviewer's run sets PLANNER_BASE, and the worker's check then reads the branch's docstrings (#240);
    # these samples are judged on their own, whatever branch the tests run on.
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE"):
        env.pop(k, None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def check(tmp_path, kind, handback, plan=STORY, number="9"):
    """Write the hand-back and the plan into a temp folder and run `agent check KIND FILE PLAN N` on them."""
    f = tmp_path / f"{kind}.json"
    f.write_text(json.dumps(handback))
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    return run(tmp_path, "check", kind, str(f), str(p), number)


def assert_rejected_naming(tmp_path, kind, handback, name, crit, plan=STORY):
    """The check exits 1 without a crash and one printed reason names `name`; fails with the criterion and the case."""
    code, out, err = check(tmp_path, kind, handback, plan)
    case = json.dumps(handback)[:160]
    assert "Traceback" not in err and "Traceback" not in out, f"{crit}: the {kind} check crashed on {case}:\n{err[-600:]}"
    assert code == 1, f"{crit}: the {kind} check passed (exit {code}) a hand-back it should reject: {case}"
    assert any(name in line for line in out.splitlines()), f"{crit}: no reason names {name!r} for {case}; reasons were:\n{out}"
    return out


def test_well_formed_hand_backs_pass_and_every_malformed_field_is_named(record_property, tmp_path, monkeypatch):
    """A malformed review.json or work.json is rejected with a reason naming the field, and never crashes the check.

    A full, well-formed review and work pass first (exit 0, nothing printed), and with every optional list left out too.
    Then each required field is removed, and each field is given a value of the wrong type or an item of the wrong
    shape: a bare string where an object belongs, and an object missing any one of its fields (a note without text or
    evidence, an outside_plan or outside_scope item without its change or why, a suspect test without its test or
    evidence, a raise that is not an object or of no kind, answers that are no list). Each is rejected, the reason
    names the field, and there is no traceback.

    The good cases pass on every stage a machine may run on (STAGE unset, plan or pr), since the sample review lists
    the owner's asks as a plan review must (#244). The rule stays as strong: on a plan review, the same review with
    its asks left out is rejected naming asks, while a code review or a machine with no stage still passes it."""
    record_property("proves", "157.1")
    record_property("proves", "244.1")
    record_property("proves", "244.2")
    # A plan review must list its asks, so on that stage the bare review keeps them; every other list is optional.
    bare_review = {k: REVIEW[k] for k in ("previous_step", "verdict", "summary", "raises", "asks", "size", "behaviors", "edge_cases", "tests")}
    bare_work = {k: WORK[k] for k in ("summary", "criteria", "evidence")}
    no_asks = {k: v for k, v in REVIEW.items() if k != "asks"}
    for stage in STAGES:
        on_stage(monkeypatch, stage)
        on = f"with STAGE={stage or 'unset'}"
        for kind, good in (("review", REVIEW), ("work", WORK)):
            code, out, err = check(tmp_path, kind, good)
            assert (code, out.strip()) == (0, ""), \
                f"157.1, 244.1: a well-formed {kind}.json was rejected {on}: {out}{err[-400:]}"
        for kind, good in (("review", bare_review), ("work", bare_work)):
            code, out, err = check(tmp_path, kind, good)
            assert (code, out.strip()) == (0, ""), \
                f"157.1, 244.1: a {kind}.json with its optional lists left out was rejected {on}: {out}{err[-400:]}"
        if stage == "plan":
            assert_rejected_naming(tmp_path, "review", no_asks, "asks", "244.2: a plan review that lists no asks")
        else:
            code, out, err = check(tmp_path, "review", no_asks)
            assert (code, out.strip()) == (0, ""), \
                f"244.2: a review with no asks was rejected {on}, where only a plan review must list them: {out}{err[-400:]}"
    on_stage(monkeypatch, "")

    for field in ("previous_step", "verdict", "summary"):
        assert_rejected_naming(tmp_path, "review", {k: v for k, v in REVIEW.items() if k != field}, field, "157.1")
    for field in ("summary", "criteria", "evidence"):
        assert_rejected_naming(tmp_path, "work", {k: v for k, v in WORK.items() if k != field}, field, "157.1")

    review_cases = [("previous_step", "did it"), ("previous_step", {"did": "one line", "decided": [], "open": []}),
                    ("verdict", 5), ("summary", 5), ("raises", 5), ("answers", 5)]
    for field, value in review_cases:
        assert_rejected_naming(tmp_path, "review", {**REVIEW, field: value}, field, "157.1")
    work_cases = [("summary", 5), ("criteria", ["9.1", "9.2", "9.3"]), ("criteria", {"9.1": 5, "9.2": "b", "9.3": "c"}),
                  ("evidence", 5), ("raises", 5), ("answers", 5)]
    for field, value in work_cases:
        assert_rejected_naming(tmp_path, "work", {**WORK, field: value}, field, "157.1")
    raised = {"kind": "blocker", "to": "planner", "text": "test_a reads a file nothing writes.", "full": "The whole detail, for agents.", "evidence": "e"}
    code, out, err = check(tmp_path, "work", {**WORK, "raises": [raised]})
    assert (code, out.strip()) == (0, ""), f"157.1: a work.json raising a blocker for the planner was rejected: {out}{err[-400:]}"
    for kind, good in (("review", REVIEW), ("work", WORK)):
        for value in (["B1"], [{"to": "planner", "text": "t"}]):
            assert_rejected_naming(tmp_path, kind, {**good, "raises": value}, "raise 1", "157.1")


def test_the_round_check_never_crashes_on_a_malformed_review(record_property, tmp_path):
    """The round check a run also does never crashes on a review or work.json whose lists have the wrong shape.

    Runs `agent check-round reviewer|worker FILE PACK` with one open raise for each, on a hand-back whose answers is a
    number, and on one whose answers are bare strings. Each exits 1 with a reason, never a traceback."""
    record_property("proves", "157.1")
    pack = tmp_path / "pack"
    pack.mkdir()
    cases = [("reviewer", "review", {**REVIEW, "answers": ["W1"]}), ("reviewer", "review", {**REVIEW, "answers": 5}),
             ("worker", "work", {**WORK, "answers": 5}), ("worker", "work", {**WORK, "answers": ["R1"]})]
    for role, kind, bad in cases:
        to = {"reviewer": ("W1", "worker", "planner"), "worker": ("R1", "reviewer", "worker")}[role]
        (pack / "open_blockers.json").write_text(json.dumps([{"kind": "blocker", "to": to[2], "text": "t", "raised_by": to[1],
                                                              "id": to[0]}]))
        f = tmp_path / f"{kind}.json"
        f.write_text(json.dumps(bad))
        code, out, err = run(tmp_path, "check-round", role, str(f), str(pack))
        assert "Traceback" not in err, f"157.1: the round check crashed on {json.dumps(bad)[:160]}:\n{err[-600:]}"
        assert code == 1 and out.strip(), f"157.1: the round check gave no reason for {json.dumps(bad)[:160]}"


def test_work_gives_a_line_for_exactly_the_plans_criteria(record_property, tmp_path):
    """A work.json missing a line for one of the plan's criteria, or giving one for a criterion the plan lacks, is rejected naming it.

    The plan has 9.1 to 9.3 (two acceptance criteria, then one non-functional). One line each passes. Leaving out 9.2,
    leaving out the non-functional 9.3, leaving out two at once, and adding 9.4 or 8.1 are each rejected, and every
    criterion at fault is named in its own reason while the criteria that are fine are not. Checked as issue 8, the
    plan's criteria are 8.1 to 8.3, so the same lines for 9.1 to 9.3 are rejected naming both 8.1 and 9.1."""
    record_property("proves", "157.2")
    code, out, err = check(tmp_path, "work", WORK)
    assert (code, out.strip()) == (0, ""), f"157.2: a line for every criterion was rejected: {out}{err[-400:]}"
    lines = WORK["criteria"]
    for missing in (["9.2"], ["9.3"], ["9.1", "9.3"]):
        crit = {k: v for k, v in lines.items() if k not in missing}
        out = assert_rejected_naming(tmp_path, "work", {**WORK, "criteria": crit}, missing[0], "157.2")
        for m in missing:
            assert m in out, f"157.2: no line for {m}, and no reason names it:\n{out}"
        for ok in set(lines) - set(missing):
            assert ok not in out, f"157.2: {ok} has its line but a reason names it:\n{out}"
    for extra in ("9.4", "8.1"):
        assert_rejected_naming(tmp_path, "work", {**WORK, "criteria": {**lines, extra: "x.py, d()"}}, extra, "157.2")
    code, out, err = check(tmp_path, "work", WORK, number="8")
    assert "Traceback" not in err, f"157.2: the work check crashed when checked as issue 8:\n{err[-600:]}"
    assert code == 1 and "9.1" in out and "8.1" in out, \
        f"157.2: checked as issue 8, a work.json with lines for 9.1 to 9.3 was not rejected naming 8.1 and 9.1:\n{out}"


def rejected_comment(tmp_path, role, kind, handback):
    """Run the workflow's check and record steps on a bad hand-back; return the reasons printed and the comment written."""
    out_dir = tmp_path / role
    out_dir.mkdir()
    (out_dir / f"{kind}.json").write_text(json.dumps(handback))
    (tmp_path / "plan.json").write_text(json.dumps(STORY))
    code, reasons, err = run(tmp_path, "check", kind, str(out_dir / f"{kind}.json"), str(tmp_path / "plan.json"), "9")
    assert code == 1 and "Traceback" not in err, f"157.4: the {kind} check did not reject cleanly (exit {code}):\n{err[-400:]}"
    (out_dir / "check.txt").write_text(reasons)
    logs = tmp_path / "logs"
    logs.mkdir(exist_ok=True)
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "42"}
    env.pop("PYTHONSAFEPATH", None)
    stage = "pr" if role == "reviewer" else ""
    subprocess.run([sys.executable, "-m", "dokima.agent", "record", role, stage, str(out_dir), str(out_dir / "check.txt"),
                    "false", str(logs)], cwd=ROOT, env=env, check=True, capture_output=True, text=True, timeout=30)
    return [l for l in reasons.splitlines() if l.strip()], (out_dir / "comment.md").read_text()


def test_a_rejected_hand_back_posts_one_comment_with_every_reason_and_the_run(record_property, tmp_path):
    """A rejected worker or reviewer hand-back leaves one comment listing every reason, with a link to the run.

    Runs the workflow's own check and record steps on a work.json missing 9.2 with the old replies field, and on a
    review.json whose old notes field is a number. The comment written is one record with no traceback,
    says the hand-back was rejected, lists each reason the check printed (including the plan-aware ones), and links the run. The workflow
    posts that comment on every run, pass or fail, from exactly one step."""
    record_property("proves", "157.4")
    work = {**WORK, "criteria": {"9.1": "a", "9.3": "c"}, "replies": [{"blocker": "B1", "answer": "fixed"}]}
    review = {**REVIEW, "raises": [], "notes": 5}
    for role, kind, bad, must in (("worker", "work", work, ("9.2", "replies")), ("reviewer", "review", review, ("notes",))):
        reasons, body = rejected_comment(tmp_path, role, kind, bad)
        for m in must:
            assert any(m in r for r in reasons), f"157.4: the {kind} check gave no reason naming {m}:\n" + "\n".join(reasons)
        assert body.count("<!-- dokima-record -->") == 1, f"157.4: the {role} comment does not hold exactly one record"
        assert "Traceback" not in body, f"157.4: the {role} comment shows a crash instead of the reasons:\n{body[:600]}"
        assert "hand-back rejected by code" in body, f"157.4: the {role} comment does not say the hand-back was rejected"
        for r in reasons:
            assert f"- {r}" in body, f"157.4: the {role} comment does not list the reason {r!r}"
        assert "](https://github.com/o/r/actions/runs/42)" in body, f"157.4: the {role} comment has no link to the run"
    wf = open(os.path.join(ROOT, ".github", "workflows", "agent.yml")).read()
    steps = re.split(r"\n      - ", wf)
    posting = [s for s in steps if re.search(r"gh (issue|pr) comment[^\n]*comment\.md", s)]
    assert len(posting) == 1, f"157.4: {len(posting)} workflow steps post the record comment; expected one"
    assert "if: always()" in posting[0], "157.4: the record comment is not posted when the hand-back is rejected"


def test_a_check_without_a_readable_plan_rejects_the_hand_back(record_property, tmp_path):
    """A check given a plan that is missing, not JSON or not an object rejects even a good hand-back, and says so.

    Runs `agent check work|review FILE PLAN N` with a well-formed hand-back but a plan.json that does not exist, holds
    broken JSON, or holds a list: each exits 1 with a reason naming plan.json, never a pass and never a traceback.
    Given no plan and no issue number at all, the old way of calling it, the check also exits 1 with a reason."""
    record_property("proves", "157.5")
    for kind, good in (("work", WORK), ("review", REVIEW)):
        f = tmp_path / f"{kind}.json"
        f.write_text(json.dumps(good))
        for content in (None, "{not json", "[]"):
            p = tmp_path / "plan.json"
            if p.exists():
                p.unlink()
            if content is not None:
                p.write_text(content)
            code, out, err = run(tmp_path, "check", kind, str(f), str(p), "9")
            assert "Traceback" not in err, f"157.5: the {kind} check crashed on plan.json {content!r}:\n{err[-600:]}"
            assert code == 1, f"157.5: the {kind} check passed with plan.json {'missing' if content is None else repr(content)}"
            assert "plan.json" in out, f"157.5: the reason does not name plan.json:\n{out}"
        code, out, err = run(tmp_path, "check", kind, str(f))
        assert "Traceback" not in err, f"157.5: the {kind} check crashed when given no plan at all:\n{err[-600:]}"
        assert code == 1 and out.strip(), f"157.5: the {kind} check passed (exit {code}) when given no plan at all"


def test_every_worker_and_reviewer_run_checks_against_the_plan_and_issue(record_property):
    """Every worker and reviewer run checks its hand-back against the plan in its pack and the issue's number.

    Reads the check command agent.yml gives the plan review, the pull request review and the worker, the same command
    the agent runs on itself and code runs again: each passes $PACK/plan.json and $N after the hand-back file."""
    record_property("proves", "157.5")
    wf = open(os.path.join(ROOT, ".github", "workflows", "agent.yml")).read()
    for key, kind, file in (("reviewerplan)", "review", "review.json"), ("reviewerpr)", "review", "review.json"), ("worker)", "work", "work.json")):
        line = next((l for l in wf.splitlines() if l.strip().startswith(key)), "")
        want = rf"dokima\.agent check {kind} \$OUT/{re.escape(file)} \$PACK/plan\.json \$N\b"
        assert re.search(want, line), f"157.5: the {key[:-1]} run does not check against the plan and issue number: {line.strip()}"

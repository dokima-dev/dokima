"""Every run comment is a short card the owner skims, with the long parts folded (issue #182).

A run comment is what code posts when a planner, worker or reviewer run ends (dokima/agent.py render). These tests draw
those comments from records built the way the workflow builds them, then read them the way the owner does: the opening
sentence, the short part on top (everything above the first fold), and the folds below it. The folds must come from the
same code that folds the issue card (dokima/card.py fold), and the full JSON record must stay folded on every comment.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

RECORD_FOLD = "<details><summary>Full record</summary>"
FOLD = re.compile(r"<details>(.*?)</details>", re.S)


def rec(role, stage="", handback=None, passed=True, problems=""):
    """A record built the way the workflow builds one, from a temp hand-back folder."""
    import tempfile
    out = tempfile.mkdtemp()
    json.dump(handback or {}, open(os.path.join(out, agent.HANDBACK[role]), "w"))
    return agent.build_record(role, stage, out, problems, passed, {"run_id": "1", "run": "https://x/run/1"})


def top(body):
    """The short part the owner reads first: everything above the first fold."""
    return body.split("<details")[0]


def folds(body):
    """The text inside every fold except the full record."""
    return "\n".join(f for f in FOLD.findall(body) if not f.lstrip().startswith("<summary>Full record</summary>"))


def opening(body):
    """The comment's first line after the record marker, as plain words: no images, links' markup or bold."""
    lines = [l for l in body.split(agent.MARK, 1)[-1].splitlines() if l.strip()]
    first = lines[0] if lines else ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", first).replace("**", "").replace("`", "")).strip()


PLAN = {"kind": "user_story", "user_story": "Slow calls return a job id at once.",
        "acceptance_criteria": [{"text": "A slow call returns a job id within 2 s.", "source": "https://x/9"},
                                {"text": "The job's result is kept for a day.", "source": "https://x/9"}],
        "non_functional": [{"text": "Jobs survive a restart-zq.", "why": "Work is never lost-zq.", "principle": "Fail closed"}],
        "scope": ["dokima/jobs_zq.py"], "out_of_scope": ["Cancelling a job-zq."],
        "tests": {"9.1": ["tests/test_jobs.py::test_a"], "9.2": ["tests/test_jobs.py::test_b"], "9.3": ["tests/test_jobs.py::test_c"]},
        "test_changes": {"tests/test_old.py::test_sync": "Calls are async now-zq."}}
QUESTIONS = [{"question": "Should a job expire after a day?", "assumption": "The plan assumes it does."}]
SPLIT = {"kind": "feature", "feature": "Slow calls run as jobs.", "stories": [
    {"title": "Jobs are queued-zq", "user_story": "u1", "acceptance_criteria": [], "non_functional": [], "depends_on": []},
    {"title": "Jobs report back-zq", "user_story": "u2", "acceptance_criteria": [], "non_functional": [], "depends_on": [0]}]}
WORK = {"summary": "They now run as jobs-zq.",
        "criteria": {"9.1": "dokima/jobs.py, submit() returns the id-zq", "9.2": "dokima/jobs.py, keep() stores it-zq"},
        "evidence": "python3 -m pytest -q: 12 passed in 3.1s",
        "outside_scope": [{"file": "dokima/extra.py", "why": "A shared helper needed one line-zq."}],
        "suspect_tests": [{"test": "tests/test_jobs.py::test_b", "evidence": "It waits a real day-zq."}],
        "replies": [{"blocker": "B1", "answer": "disagree", "why": "The id is returned in 0.1 s-zq."}]}
PREVIOUS = {"did": ["Built the jobs queue-zq."], "decided": ["Kept the old endpoint-zq."], "open": []}
ASKS = [{"ask": f"ask {k}-zq", "source": "https://x/9", "criterion": f"9.{k}"} for k in (1, 2, 3, 4)]


def blocker(i, crit, problem, fixer="worker"):
    """One reviewer blocker on criterion `crit`."""
    return {"id": i, "criterion": crit, "test": None, "problem": problem, "evidence": f"evidence of {i}-zq",
            "fix": f"fix for {i}-zq", "fixer": fixer}


def review(verdict, *blockers, **kw):
    """A well-formed review hand-back with every long part filled in."""
    return {"previous_step": PREVIOUS, "verdict": verdict, "summary": "The reviewer read the work.",
            "blockers": list(blockers), "notes": [{"text": "A note on naming-zq.", "evidence": "jobs.py:3"}],
            "outside_plan": [{"file": "dokima/extra.py", "change": "one helper line-zq"}], "resolved": [],
            "asks": ASKS, **kw}


BLOCK = review("block", blocker("B1", "9.2", "The day is never checked."), blocker("B2", "9.3", "Restarts are not tried."))
APPROVE = review("approve", issues_found=[{"title": "Board ignores closed PRs", "why": "cards go stale", "evidence": "board.py:40"}])

# Every kind of run comment, with the word its opening sentence must use and a word it must not.
OPENINGS = [
    ("plan", lambda: rec("planner", handback=PLAN), r"\bplan", r"question|split"),
    ("plan with questions", lambda: rec("planner", handback=dict(PLAN, questions=QUESTIONS)), r"question", None),
    ("split", lambda: rec("planner", handback=SPLIT), r"split", r"question"),
    ("work", lambda: rec("worker", handback=WORK), r"They now run as jobs-zq\.", r"reject|\bbuilt\b|server-zq"),
    ("plan review that passes", lambda: rec("reviewer", "plan", APPROVE), r"\bpass", r"block|escalat"),
    ("code review that blocks", lambda: rec("reviewer", "pr", BLOCK), r"\bblock", r"\bpass|escalat"),
    ("escalation", lambda: rec("reviewer", "pr", review("escalate")), r"escalat", r"\bpass|\bblock"),
    ("rejected hand-back", lambda: rec("planner", handback=PLAN, passed=False, problems="criterion 9.2 has no test\n"),
     r"reject", r"\bpass"),
    ("run that never started", lambda: agent.not_started("worker", "", "The pack was incomplete.", {"run": "https://x/run/1"}),
     r"before any agent started", None),
    ("cancelled run", lambda: agent.cancelled("planner", "", True, {"run": "https://x/run/1"}), r"cancell?ed", r"reject|fail"),
]


@pytest.mark.parametrize("name,make,must,must_not", OPENINGS, ids=[o[0] for o in OPENINGS])
def test_every_run_comment_opens_with_one_plain_sentence_saying_what_the_run_did(record_property, name, make, must, must_not):
    """Every run comment opens with one sentence that says what the run did.

    Draws the comment of each kind of run (a plan, a plan with questions, a split, a build, a review that passes, one
    that blocks, an escalation, a rejected hand-back, a run that never started and a cancelled one) and checks its first
    line, read as plain words, is exactly one sentence ending in a full stop, names what that run did and does not name
    what it did not do."""
    record_property("proves", "182.1")
    first = opening(agent.render(make()))
    assert first.endswith("."), f"182.1 ({name}): the comment does not open with one sentence ending in a full stop: {first!r}"
    assert not re.search(r"[.?!]\s", first[:-1]), f"182.1 ({name}): the opening line holds more than one sentence: {first!r}"
    assert re.search(must, first, re.I), f"182.1 ({name}): the opening sentence does not say what the run did ({must}): {first!r}"
    if must_not:
        assert not re.search(must_not, first, re.I), f"182.1 ({name}): the opening sentence says something the run did not do ({must_not}): {first!r}"


def test_the_long_parts_of_every_run_comment_are_folded(record_property):
    """The long parts of every run comment are folded, never on top.

    The long parts are non-functional requirements, test changes, the worker's findings and changes outside the plan.
    Draws a plan, a build and a review full of long parts, and checks each long part's words are absent from the
    short part on top and present inside a fold other than the full record."""
    record_property("proves", "182.1")
    cases = [("plan", rec("planner", handback=PLAN),
              ["Jobs survive a restart-zq.", "Calls are async now-zq.", "dokima/jobs_zq.py", "Cancelling a job-zq."]),
             ("work", rec("worker", handback=WORK),
              ["submit() returns the id-zq", "A shared helper needed one line-zq.",
               "It waits a real day-zq.", "The id is returned in 0.1 s-zq."]),
             ("review", rec("reviewer", "pr", BLOCK),
              ["one helper line-zq"])]
    for name, r, long_parts in cases:
        body = agent.render(r)
        for part in long_parts:
            assert part not in top(body), f"182.1 ({name}): {part!r} is on top of the comment, not in a fold:\n{top(body)}"
            assert part in folds(body), f"182.1 ({name}): {part!r} is in no fold of the comment:\n{body}"


def test_run_comments_fold_with_the_same_code_as_the_issue_card(record_property, monkeypatch):
    """The run comments and the issue card fold their long parts with one shared piece of code.

    Replaces dokima/card.py's fold with a stand-in that marks what it folds, then draws a run comment of each role and
    the issue card: every long-part fold on the comments and the issue card's non-functional fold must come out marked,
    and no other fold is left on the comments but the full record."""
    record_property("proves", "182.1")
    if not callable(getattr(card, "fold", None)):
        pytest.fail("182.1: dokima/card.py has no fold(title, lines), the code that folds the long parts of every card")
    monkeypatch.setattr(card, "fold", lambda title, lines: [f"[FOLD {title}]", *lines, "[/FOLD]"])
    for name, r in (("plan", rec("planner", handback=PLAN)), ("work", rec("worker", handback=WORK)),
                    ("review", rec("reviewer", "pr", BLOCK))):
        body = agent.render(r)
        assert "[FOLD " in body, f"182.1 ({name}): the run comment does not fold with card.fold:\n{body}"
        left = [f for f in FOLD.findall(body) if not f.lstrip().startswith("<summary>Full record</summary>")]
        assert not left, f"182.1 ({name}): the run comment builds folds of its own instead of card.fold:\n{left}"
    found = {"recs": [rec("planner", handback=PLAN)], "pr": None, "check_runs": [], "reviews": [], "owners": [],
             "tests": {}, "worker": None}
    issue_card = card.render("o/r", {"number": 9, "url": "https://github.com/o/r/issues/9"}, found)
    assert "[FOLD " in issue_card and "Jobs survive a restart-zq." in issue_card.split("[FOLD ", 1)[1], \
        f"182.1: the issue card does not fold its non-functional requirements with card.fold:\n{issue_card}"


def test_the_planner_card_shows_the_plan_or_its_questions_or_the_split_on_top(record_property):
    """The planner's card shows on top the plan, or its questions beside the plan, or the proposed split.

    Draws a plan's comment and checks its user story and both acceptance criteria are in the short part on top. Then
    draws a plan with a question and checks the question and its assumption share a line on top, beside the plan's
    criteria; then a split, and checks the feature and both story titles are on top. Last, a rejected plan's card
    shows why it was rejected."""
    record_property("proves", "182.2")
    short = top(agent.render(rec("planner", handback=PLAN)))
    for text in [PLAN["user_story"]] + [c["text"] for c in PLAN["acceptance_criteria"]]:
        assert text in short, f"182.2: the planner card does not show {text!r} on top:\n{short}"
    short = top(agent.render(rec("planner", handback=dict(PLAN, questions=QUESTIONS))))
    q = QUESTIONS[0]
    assert any(q["question"] in l and q["assumption"] in l for l in short.splitlines()), \
        f"182.2: the planner card does not show the question with its assumption on top:\n{short}"
    for text in [PLAN["user_story"]] + [c["text"] for c in PLAN["acceptance_criteria"]]:
        assert text in short, f"182.2: the planner card with a question does not show {text!r} on top:\n{short}"
    short = top(agent.render(rec("planner", handback=SPLIT)))
    for text in [SPLIT["feature"]] + [s["title"] for s in SPLIT["stories"]]:
        assert text in short, f"182.2: the split card does not show {text!r} on top:\n{short}"
    bad = top(agent.render(rec("planner", handback=PLAN, passed=False, problems="criterion 9.2 has no test\n")))
    assert "criterion 9.2 has no test" in bad, f"182.2: a rejected plan's card does not show why:\n{bad}"


PR = "https://github.com/o/r/pull/7"


def shown(body):
    """The lines of the short part on top, below the record marker, that hold any words."""
    return [l for l in top(body).split(agent.MARK, 1)[-1].splitlines() if l.strip()]


def plain(line):
    """A line as plain words: no images, bold, code marks, and links reduced to their text."""
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", re.sub(r"<[^>]+>", "", line))
    return re.sub(r"\s+", " ", line.replace("**", "").replace("`", "")).strip()


def test_the_worker_card_shows_one_sentence_with_its_pull_request_and_no_test_result(record_property):
    """The worker's card shows on top only its own sentence on what it changed, with a link to its pull request.

    Draws a build's comment with its pull request known and checks the short part on top is exactly one line holding
    the change sentence of the worker's own summary word for word, not its cause sentence and not a generic line
    from code (no "built"), with a link to the pull request and no test result (no passed or failed, no test count).
    A worker whose summary is a single sentence shows that sentence. The worker's own test run stays only in a fold."""
    record_property("proves", "182.3")
    for summary, said, unsaid in ((WORK["summary"], "They now run as jobs-zq.", "The calls blocked the server-zq."),
                                  ("Slow calls now return a job id-zq.", "Slow calls now return a job id-zq.", None)):
        body = agent.render(rec("worker", handback=dict(WORK, summary=summary)), pr=PR)
        lines = shown(body)
        assert len(lines) == 1, f"182.3: the top of a finished worker card should hold only its one sentence:\n{top(body)}"
        words = plain(lines[0])
        assert said in words, f"182.3: the worker card's sentence is not the worker's own words on what it changed ({said!r}): {words!r}"
        if unsaid:
            assert unsaid not in words, f"182.3: the worker card's sentence holds the cause, not only what it changed: {words!r}"
        assert not re.search(r"\bbuilt\b", words, re.I), \
            f"182.3: the worker card's sentence is a generic line from code, not the worker's own words: {words!r}"
        assert f"]({PR})" in lines[0], f"182.3: the worker card's sentence does not link its pull request {PR}:\n{lines[0]}"
        assert not re.search(r"\b(passed|failed|tests?)\b|\d+ passed", words, re.I), \
            f"182.3: the worker card shows a test result on top; the criteria and their verdicts belong on the main card:\n{top(body)}"
        assert "12 passed in 3.1s" in folds(body), f"182.3: the worker's own test run is in no fold:\n{body}"


def test_the_worker_card_says_why_it_stopped_when_it_stopped_early(record_property):
    """When the worker stops early, its card says so in its sentence and shows why, right below it.

    Draws the comment of a worker whose hand-back code rejected, once with no work.json at all and once with a bad
    one, and checks the sentence says the worker stopped early, never that it built, and that every reason code found
    is on top. A worker that finished shows no such reason."""
    record_property("proves", "182.3")
    for name, handback, why in (
            ("no hand-back", {"missing": "work.json: [Errno 2] No such file"}, "work.json is missing (/tmp/dokima-out/work.json)"),
            ("bad hand-back", dict(WORK, evidence=""), "evidence is empty: name the last test command and its result line")):
        body = agent.render(rec("worker", handback=handback, passed=False, problems=why + "\n"), pr=PR)
        first = opening(body)
        assert re.search(r"\bstopped\b", first, re.I), f"182.3 ({name}): the worker card does not say it stopped early: {first!r}"
        assert not re.search(r"\bbuilt\b", first, re.I), f"182.3 ({name}): a worker that stopped early is said to have built: {first!r}"
        assert why in top(body), f"182.3 ({name}): the worker card does not show why it stopped on top:\n{top(body)}"
    done = top(agent.render(rec("worker", handback=WORK), pr=PR))
    assert "stopped" not in done.lower(), f"182.3: a worker that finished is said to have stopped:\n{done}"


def test_the_worker_card_links_the_pull_request_code_opened_after_the_run(record_property, tmp_path, monkeypatch):
    """The worker's card links its pull request even on the first round, when code opens the pull request after the record.

    Writes a worker's record and comment the way the run does, then runs the step that decides what follows
    (agent next) with GitHub faked to say the open pull request of try/issue-9 is #7, and checks the posted comment's
    sentence now links that pull request, still ends with the Next line and still reads back as the same record."""
    record_property("proves", "182.3")
    r = rec("worker", handback=WORK)
    (tmp_path / "record.json").write_text(json.dumps(r))
    (tmp_path / "comment.md").write_text(agent.render(r))
    calls = []

    def gh(*args):
        calls.append(args)
        return "7\n" if args[:2] == ("pr", "list") and "try/issue-9" in args else "[]"
    monkeypatch.setattr(agent, "gh", gh)
    monkeypatch.setattr(agent, "conversation", lambda repo, number: ({}, []))
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("OWNERS", "owner")
    agent.main(["agent", "next", "9", str(tmp_path)])
    body = (tmp_path / "comment.md").read_text()
    lines = shown(body)
    assert lines and f"]({PR})" in lines[0], f"182.3: after the run the worker card's sentence does not link pull request #7:\n{body}"
    assert body.rstrip().splitlines()[-1].startswith("**Next:**"), f"182.3: the worker card lost its Next line:\n{body}"
    got = agent.records([{"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T10:00:00Z"}])
    assert got == [r], f"182.3: the worker card no longer reads back as its record: {got}"


def test_the_worker_card_folds_what_it_built_found_and_raised(record_property):
    """What the worker built, what it found and any blocker it raised are in folds, not on top.

    Draws a build's comment and checks its per-criterion lines (built), its out-of-scope change (found), and its
    suspect test and disagreement (raised) are each absent from the top and present in a fold."""
    record_property("proves", "182.3")
    body = agent.render(rec("worker", handback=WORK))
    for what, text in (("built", "keep() stores it-zq"),
                       ("found", "A shared helper needed one line-zq."), ("raised", "It waits a real day-zq."),
                       ("raised", "The id is returned in 0.1 s-zq.")):
        assert text not in top(body), f"182.3: what the worker {what} ({text!r}) is on top, not in a fold:\n{top(body)}"
        assert text in folds(body), f"182.3: what the worker {what} ({text!r}) is in no fold:\n{body}"


def test_the_reviewer_card_shows_pass_or_only_the_criteria_it_blocks_on(record_property):
    """The reviewer's card says it passed, or shows why it blocks, and its proposed issues.

    Draws a plan review that approves, with asks on 9.1 to 9.4 and one proposed issue, and checks the short part on top
    says pass in words and names no criterion, and the proposed issue shows outside every fold (after the change
    outside the plan, in the owner's order of issue #236). Then draws a code review that blocks on 9.2
    and 9.3 with the same asks, and checks the top shows each blocker's problem and never a criterion number or a
    blocker code (issue #236)."""
    record_property("proves", "182.4")
    short = top(agent.render(rec("reviewer", "plan", APPROVE)))
    words = re.sub(r"<[^>]+>", "", short)
    assert re.search(r"\bpass", words, re.I), f"182.4: the passing reviewer card does not say pass on top, in words:\n{short}"
    assert not re.search(r"\b9\.\d\b", short), f"182.4: the passing reviewer card lists criteria on top:\n{short}"
    unfolded = FOLD.sub("", agent.render(rec("reviewer", "plan", APPROVE)))
    assert "1. Board ignores closed PRs: cards go stale" in unfolded, \
        f"182.4: the reviewer card does not show its proposed issue outside its folds:\n{unfolded}"
    short = top(agent.render(rec("reviewer", "pr", BLOCK)))
    for problem in ("The day is never checked.", "Restarts are not tried."):
        assert problem in short, f"182.4: the reviewer card does not show why it blocks ({problem!r}) on top:\n{short}"
    assert not re.search(r"\b9\.\d\b|\bB\d\b", short), f"182.4: the reviewer card shows a criterion number or a blocker code:\n{short}"


def test_agents_md_has_the_human_brain_bottleneck_principle(record_property):
    """AGENTS.md lists the principle: match the output to the human brain bottleneck, and fold the rest.

    Reads the Principles section of AGENTS.md and checks one of its bullets names the human brain bottleneck, what the
    owner needs at a glance, and folds."""
    record_property("proves", "182.5")
    text = open(os.path.join(os.path.dirname(__file__), "..", "AGENTS.md")).read()
    section = text.split("## Principles", 1)[-1].split("\n## ", 1)[0] if "## Principles" in text else ""
    assert section, "182.5: AGENTS.md has no Principles section"
    bullets = [l for l in section.splitlines() if l.startswith("- ")]
    hits = [b for b in bullets if "human brain bottleneck" in b.lower() and "glance" in b.lower() and "fold" in b.lower()]
    assert hits, f"182.5: no principle in AGENTS.md says to match the output to the human brain bottleneck and fold the rest:\n{section}"


def test_the_full_json_record_stays_folded_on_every_run_comment(record_property):
    """Every run comment keeps the full JSON record in its own fold, the last one, and it reads back exactly.

    Draws the comment of each kind of run and checks it holds exactly one Full record fold, that no other fold comes
    after it, and that reading the comment back as a record gives the very record it was drawn from. For a plan, a
    build and a review it also checks the long parts sit in folds of their own above the record, never inside it."""
    record_property("proves", "182.6")
    for name, make, _, _ in OPENINGS:
        r = make()
        body = agent.render(r)
        assert body.count(RECORD_FOLD) == 1, f"182.6 ({name}): the comment does not hold exactly one Full record fold:\n{body}"
        after = body.split(RECORD_FOLD, 1)[1]
        assert "<details" not in after, f"182.6 ({name}): a fold comes after the full record, which must be the last fold:\n{body}"
        got = agent.records([{"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T10:00:00Z"}])
        assert got == [r], f"182.6 ({name}): the record read back from its comment is not the record it was drawn from: {got}"
        if name in ("plan", "work", "code review that blocks"):
            above = body.split(RECORD_FOLD, 1)[0]
            assert "<details" in above and "```json" not in above, \
                f"182.6 ({name}): the long parts are not in folds of their own above the full record:\n{body}"

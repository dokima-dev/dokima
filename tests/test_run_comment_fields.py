"""Run comments show only what has something, in plain words, with no codes (#236).

A run comment is what code posts when a planner, worker or reviewer run ends: `agent record ROLE STAGE OUT CHECK PASSED
LOGS` in dokima/agent.py writes OUT/record.json and OUT/comment.md. These tests run that command the way the workflow
does, from the repo root of the run, and read the comment the way the owner does:

    the planner's comment  lists each criterion as the issue card does: its status circle, its sentence, Verified by
                           with the first docstring line of each of its tests (read from the test files in the folder
                           the command runs in), then its Source link
    a review's comment     opens with its verdict, then, in the owner's order, lists only what fails, read against
                           the plan in $PACK/plan.json: each failing criterion's sentence, why it fails (its blockers'
                           problems) and its Source link; each ask of the owner's no criterion keeps: the ask,
                           "Nothing covers this" and its Source link; its changes outside the plan; the plan's
                           questions whose assumption it could not confirm; and the issues it found
    a shared field         looks the same whichever agent shows it: the worker's and a review's changes outside the
                           plan, and the planner's questions and a review's unconfirmed ones
    the worker's comment   names the files it changed since $BASE (committed, uncommitted or new) on one line
    every comment          folds its stats right above the Full record fold, which stays the last fold

"Visible" below means the comment without its Full record fold: the record holds every code and number by design.
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

REPO = "o/r"
SRC1 = "https://github.com/o/r/issues/77"
SRC2 = "https://github.com/o/r/issues/77#issuecomment-501"
SRC3 = "https://github.com/o/r/issues/77#issuecomment-502"
RECORD_FOLD = "<details><summary>Full record</summary>"
DETAILS = re.compile(r"<details>.*?</details>", re.S)

PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id.",
        "user_story": "Callers get a job id for a slow call.",
        "acceptance_criteria": [{"text": "A slow call returns a job id within 2 s.", "source": SRC1},
                                {"text": "The job's result is kept for a day.", "source": SRC2},
                                {"text": "A finished job says done on its page.", "source": SRC3}],
        "non_functional": [{"text": "Jobs survive a restart of the server.", "why": "work is never lost",
                            "principle": "Fail closed"}],
        "scope": ["app/jobs.py"], "out_of_scope": ["Cancelling a job."],
        "tests": {"77.1": ["tests/test_jobs.py::test_fast"],
                  "77.2": ["tests/test_jobs.py::test_kept", "tests/test_jobs.py::test_kept_twice"],
                  "77.3": ["tests/test_jobs.py::test_done"], "77.4": ["tests/test_jobs.py::test_restart"]},
        "test_changes": {}}
TESTS = '''"""Tests of the jobs."""


def test_fast():
    """A slow call hands back its job id at once.

    More words the owner never sees."""


def test_kept():
    """The result is still there a day later."""


def test_kept_twice():
    """Two results kept side by side both survive."""


def test_done():
    """The page of a finished job says done."""


def test_restart():
    """A job queued before a restart still runs after it."""
'''
DOCS = {"77.1": ["A slow call hands back its job id at once."],
        "77.2": ["The result is still there a day later.", "Two results kept side by side both survive."],
        "77.3": ["The page of a finished job says done."],
        "77.4": ["A job queued before a restart still runs after it."]}
SENTENCES = [c["text"] for c in PLAN["acceptance_criteria"]] + [n["text"] for n in PLAN["non_functional"]]
PREVIOUS = {"did": ["Built the jobs queue zq."], "decided": ["Kept the old endpoint zq."], "open": ["The retry rule zq."]}
REPORT = {"duration_ms": 240000, "num_turns": 23, "total_cost_usd": 3.2,
          "usage": {"input_tokens": 1000, "cache_read_input_tokens": 400000, "output_tokens": 18000}}


def blocker(i, crit, problem, fixer="worker"):
    """One reviewer blocker on criterion `crit`."""
    return {"id": i, "criterion": crit, "test": None, "problem": problem, "evidence": f"evidence of {i} zq",
            "fix": f"fix for {i} zq", "fixer": fixer}


ASKS = [{"ask": "Give back a job id at once", "source": SRC1, "criterion": "77.1"},
        {"ask": "Keep each result for a day", "source": SRC2, "criterion": "77.2"},
        {"ask": "Email me when a job fails", "source": SRC3, "criterion": "missing"}]
BLOCK = {"previous_step": PREVIOUS, "verdict": "block", "summary": "The plan misses an ask and two proofs are weak zq.",
         "blockers": [blocker("B1", "77.2", "The test never waits a day, so a result dropped at noon still passes."),
                      blocker("B2", "77.2", "Only one result is ever stored, so side by side is not tried.", "planner"),
                      blocker("B3", "77.4", "No restart happens in the test, so a lost queue still passes.")],
         "notes": [{"text": "A note on naming zq.", "evidence": "jobs.py:3"}],
         "outside_plan": [], "resolved": ["B7"], "issues_found": [], "asks": ASKS}
APPROVE = {"previous_step": PREVIOUS, "verdict": "approve", "summary": "Every ask is kept and proven zq.",
           "blockers": [], "notes": [{"text": "A note on naming zq.", "evidence": "jobs.py:3"}],
           "outside_plan": [], "resolved": [], "issues_found": [], "asks": ASKS[:2]}
WORK = {"summary": "The calls blocked the server. They now run as jobs.",
        "criteria": {"77.1": "submit() returns the id at once"}, "evidence": "python3 -m pytest -q: 12 passed in 3.1s",
        "outside_scope": [], "suspect_tests": [], "replies": []}
QA = {"question": "Should a job expire after a day?", "assumption": "The plan assumes it does, as you said zq."}
QB = {"question": "Should a failed job retry by itself?", "assumption": "The plan assumes it retries once zq."}
ACCEPT_A = {"question": QA["question"], "accepted": True, "changes": False, "matched": "expire after a day zq",
            "source": SRC1}
DOUBT_B = {"question": QB["question"], "accepted": False, "changes": False, "why": "You never said how often zq."}
FOUND = [{"title": "Retries are missing zq", "why": "A failed job never retries zq.", "evidence": "jobs.py:9"}]
OUTSIDE = "A shared helper needed one line zq."


def git(cwd, *args):
    """Run git in `cwd` and return what it printed."""
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def run(tmp_path, monkeypatch):
    """A run's machine: a git checkout with tests, a pack and a hand-back folder.

    Set up as the workflow sets them; returns a function that writes a record the way the workflow does and gives
    back its comment and record."""
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_jobs.py").write_text(TESTS)
    (repo / "app").mkdir()
    for name in ("jobs.py", "keep.py", "page.py"):
        (repo / "app" / name).write_text(f"# {name}\n")
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "start")
    pack = tmp_path / "pack"
    (pack / "in").mkdir(parents=True)
    (pack / "plan.json").write_text(json.dumps(PLAN))
    for k, v in {"GITHUB_REPOSITORY": REPO, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "1",
                 "PACK": str(pack), "BASE": git(repo, "rev-parse", "HEAD"), "LOG_URL": "https://g/log.md"}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.chdir(repo)
    count = [0]

    def record(role, stage, handback, passed=True, problems=""):
        count[0] += 1
        out, logs = tmp_path / f"out{count[0]}", tmp_path / f"logs{count[0]}"
        out.mkdir()
        logs.mkdir()
        (logs / "s.jsonl").write_text(json.dumps({"message": {"model": "claude-opus-5-5"}}) + "\n")
        (out / agent.HANDBACK[role]).write_text(json.dumps(handback))
        (out / "claude.json").write_text(json.dumps(REPORT))
        (out / "check.txt").write_text(problems)
        agent.main(["agent", "record", role, stage, str(out), str(out / "check.txt"), "true" if passed else "false", str(logs)])
        return (out / "comment.md").read_text(), json.load(open(out / "record.json"))
    record.repo, record.pack, record.tmp = repo, pack, tmp_path
    return record


def visible(body):
    """The comment as the owner reads it: everything but the Full record fold."""
    head, _, rest = body.partition(RECORD_FOLD)
    return head + rest.partition("</details>")[2]


def plain(text):
    """Text as plain words: no tags, bold, code marks or link targets."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text.replace("**", "").replace("`", "")).strip()


def first_line(body):
    """The comment's first line after its marker, as plain words."""
    lines = [l for l in body.split(agent.MARK, 1)[-1].splitlines() if l.strip()]
    return plain(lines[0]) if lines else ""


def img(field):
    """The field's icon exactly as code draws it."""
    return card.field_icon(REPO, field)


def segment(text, sentence, others):
    """The part of `text` from `sentence` to the next of `others`; empty without the sentence."""
    if sentence not in text:
        return ""
    start = text.index(sentence)
    ends = [text.find(o, start + len(sentence)) for o in others if o != sentence]
    ends = [e for e in ends if e > 0]
    return text[start:min(ends)] if ends else text[start:]


# 236.1: Plan review and Code review

def test_review_runs_are_called_plan_review_and_code_review(record_property, run):
    """A review's live card and run comment say Plan review or Code review.

    Draws the live card of a plan review and a code review in every state, and the run comment of each review that
    passes, blocks, escalates, is rejected, is cancelled and never starts; each names its own review and never the
    other, Reviewer (...) or The reviewer. A planner's and a worker's live cards keep their names. Proves 236.1."""
    record_property("proves", "236.1")
    for stage, name, other in (("plan", "Plan review", "Code review"), ("pr", "Code review", "Plan review")):
        for state, ahead in (("queued", None), ("queued", "https://x/run/0"), ("handoff", None), ("setup", None),
                             ("working", None), ("checking", None)):
            live = agent.live_card("reviewer", stage, state, ahead)
            assert f"**{name}**" in live, f"236.1: the {state} live card of a {stage} review does not say {name}:\n{live}"
            assert "Reviewer (" not in live and other not in live, \
                f"236.1: the {state} live card of a {stage} review still says Reviewer (...) or {other}:\n{live}"
        meta = {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1"}
        bodies = [("passing", run("reviewer", stage, APPROVE)[0]), ("blocking", run("reviewer", stage, BLOCK)[0]),
                  ("escalating", run("reviewer", stage, dict(BLOCK, verdict="escalate"))[0]),
                  ("rejected", run("reviewer", stage, BLOCK, passed=False, problems="a problem\n")[0]),
                  ("cancelled", agent.render(agent.cancelled("reviewer", stage, True, meta))),
                  ("never started", agent.render(agent.not_started("reviewer", stage, "the pack failed", meta)))]
        for what, body in bodies:
            first = first_line(body)
            assert name in first, f"236.1: the {what} {stage} review's comment does not open naming {name}: {first!r}"
            words = plain(visible(body))
            for wrong in ("Reviewer (", "The reviewer", "the reviewer", other):
                assert wrong not in words, f"236.1: the {what} {stage} review's comment still says {wrong!r}:\n{words}"
    assert "**Planner**" in agent.live_card("planner", "", "working"), "236.1: the planner's live card lost its name"
    assert "**Worker**" in agent.live_card("worker", "", "working"), "236.1: the worker's live card lost its name"


# 236.2: only what has something; a review drops What the previous step did, Details and Notes

EMPTY_FOLD = re.compile(r"<summary>.*?</summary>\s*</details>", re.S)
BARE_HEADING = re.compile(r"^[^\w\n]*(?:<img [^>]*>\s*)?\*\*[^*\n]+\*\*:?\s*$", re.M)


def no_blank_parts(body, k, what):
    """Fail naming criterion k on an empty fold or a bare heading."""
    text = visible(body)
    assert not EMPTY_FOLD.search(text), f"{k}: {what} holds an empty fold:\n{text}"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if BARE_HEADING.match(line):
            rest = [l for l in lines[i + 1:] if l.strip()]
            assert rest and not BARE_HEADING.match(rest[0]) and not rest[0].startswith("</details>"), \
                f"{k}: {what} shows the heading {line!r} with nothing under it:\n{text}"


def test_a_run_comment_shows_each_optional_part_only_when_it_has_something(record_property, run):
    """Each optional part of a run comment shows only when it has something.

    Draws a worker, a plan review, a code review and a planner whose optional parts are missing, empty or blank, and
    checks none of them shows, with no empty fold or bare heading; then fills each part and checks its words show.
    The parts: suspect tests, outside scope, replies, test result, outside the plan, questions. Proves 236.2."""
    record_property("proves", "236.2")
    for blank in (None, [], ""):
        hb = {k: v for k, v in WORK.items() if k not in ("outside_scope", "suspect_tests", "replies")}
        if blank is not None:
            hb.update(outside_scope=blank, suspect_tests=blank, replies=blank)
        for evidence in ("", "   "):
            body = run("worker", "", dict(hb, evidence=evidence), passed=False, problems="evidence is empty\n")[0]
            words = plain(visible(body))
            for gone in ("Suspect", "Outside the plan", "outside scope", "What it found", "What it raised",
                         "Its own test run", "test run"):
                assert gone not in words, f"236.2: a worker with nothing for {gone!r} still shows it (blank {blank!r}):\n{words}"
            no_blank_parts(body, "236.2", f"a worker's comment with blank parts ({blank!r})")
        for stage in ("plan", "pr"):
            body = run("reviewer", stage, dict(APPROVE, outside_plan=blank) if blank is not None else
                       {k: v for k, v in APPROVE.items() if k != "outside_plan"})[0]
            assert "Outside the plan" not in plain(visible(body)), \
                f"236.2: a {stage} review with no change outside the plan still shows Outside the plan:\n{body}"
            no_blank_parts(body, "236.2", f"a {stage} review's comment with nothing outside the plan")
        body = run("planner", "", dict(PLAN, questions=blank) if blank is not None else PLAN)[0]
        assert "Questions" not in plain(visible(body)), f"236.2: a plan with no questions still shows Questions:\n{body}"
        no_blank_parts(body, "236.2", "a plan's comment with no questions")
    full = dict(WORK, outside_scope=[{"file": "app/extra.py", "why": "A shared helper needed one line zq."}],
                suspect_tests=[{"test": "tests/test_jobs.py::test_kept", "evidence": "It waits a real day zq."}],
                replies=[{"blocker": "B1", "answer": "disagree", "why": "The id comes back in 0.1 s zq."}])
    words = plain(visible(run("worker", "", full)[0]))
    for said in ("A shared helper needed one line zq.", "It waits a real day zq.", "The id comes back in 0.1 s zq.",
                 "python3 -m pytest -q: 12 passed in 3.1s"):
        assert said in words, f"236.2: the worker's comment does not show {said!r}, which it has:\n{words}"
    words = plain(visible(run("reviewer", "pr", dict(APPROVE, outside_plan=[{"file": "app/extra.py", "change": "one helper line zq"}]))[0]))
    assert "one helper line zq" in words, f"236.2: a code review's change outside the plan is not shown:\n{words}"
    q = {"question": "Should a job expire after a day?", "assumption": "The plan assumes it does."}
    words = plain(visible(run("planner", "", dict(PLAN, questions=[q]))[0]))
    assert q["question"] in words and q["assumption"] in words, f"236.2: the plan's question is not shown:\n{words}"
    (run.pack / "plan.json").write_text(json.dumps(dict(PLAN, questions=[QA])))
    for judged in (None, [], [ACCEPT_A]):
        hb = dict(APPROVE, issues_found=[]) if judged is None else dict(APPROVE, issues_found=[], assumptions=judged)
        body = run("reviewer", "plan", hb)[0]
        text = visible(body)
        for gone, mark in (("Questions", "question"), ("Issues found", "issue found")):
            assert gone not in plain(text) and img(mark) not in text, \
                f"236.2: a plan review with nothing for {gone} (assumptions {judged!r}) still shows it:\n{text}"
        assert QA["question"] not in text, f"236.2: a plan review shows a question whose assumption it accepted:\n{text}"
        no_blank_parts(body, "236.2", f"a plan review's comment with no question left and no issue found ({judged!r})")
    words = plain(visible(run("reviewer", "plan", dict(APPROVE, assumptions=[dict(DOUBT_B, question=QA["question"])],
                                                       issues_found=FOUND))[0]))
    for said in (QA["question"], "Retries are missing zq"):
        assert said in words, f"236.2: a plan review does not show {said!r}, which it has:\n{words}"


def test_a_review_comment_drops_the_previous_step_details_and_notes(record_property, run):
    """A review's comment no longer shows What the previous step did, Details or Notes.

    Draws a plan review and a code review that approve and that block, each with a previous step, a summary, notes and
    resolved blockers, and checks none of those headings or their words show; the escalation's summary still shows.
    Proves 236.2."""
    record_property("proves", "236.2")
    for stage in ("plan", "pr"):
        for name, hb in (("passing", APPROVE), ("blocking", BLOCK)):
            body = run("reviewer", stage, hb)[0]
            words = plain(visible(body))
            for gone in ("What the previous step did", "Details", "Notes", "Still open", "Built the jobs queue zq.",
                         "Kept the old endpoint zq.", "The retry rule zq.", "A note on naming zq.", hb["summary"],
                         "Resolved", "evidence of B1 zq", "fix for B1 zq"):
                assert gone not in words, f"236.2: the {name} {stage} review's comment still shows {gone!r}:\n{words}"
            assert img("note") not in visible(body), f"236.2: the {name} {stage} review's comment still shows the note icon"
    body = run("reviewer", "pr", dict(BLOCK, verdict="escalate"))[0]
    assert BLOCK["summary"] in plain(visible(body)), f"236.2: an escalation lost its summary, the reason it reaches you:\n{body}"


def section(text, field, label):
    """The part of a comment one field draws: its fold, or its heading and lines.

    A field drawn in a fold gives that whole fold; one drawn open gives its heading line and the lines under it, up
    to the next blank line. Empty when the field's icon and label show nowhere."""
    head = re.compile(re.escape(img(field)) + r"\s*(?:\*\*|<b>)?\s*" + re.escape(label))
    for fold in DETAILS.findall(text):
        summary = re.search(r"<summary>(.*?)</summary>", fold, re.S)
        if summary and head.search(summary.group(1)):
            return fold
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if head.search(line):
            part = [line]
            for rest in lines[i + 1:]:
                if not rest.strip():
                    break
                part.append(rest)
            return "\n".join(part)
    return ""


def test_a_field_two_agents_show_looks_the_same_from_both(record_property, run):
    """A field two agents show has the same icon, label and layout from both.

    Draws the worker's change outside its scope beside a plan review's and a code review's change outside the plan,
    with the same file and words, and checks all three draw the very same Outside the plan part; then draws a plan
    with one question beside a plan review that could not confirm that question's assumption, and checks both draw
    the very same Questions for you part, holding the question and its assumption. Proves 236.2."""
    record_property("proves", "236.2")
    parts = [("the worker", section(visible(run("worker", "", dict(WORK, outside_scope=[{"file": "app/extra.py", "why": OUTSIDE}]))[0]),
                                    "outside the plan", "Outside the plan"))]
    for stage in ("plan", "pr"):
        body = run("reviewer", stage, dict(APPROVE, outside_plan=[{"file": "app/extra.py", "change": OUTSIDE}]))[0]
        parts.append((f"a {stage} review", section(visible(body), "outside the plan", "Outside the plan")))
    for who, part in parts:
        assert "app/extra.py" in part and OUTSIDE in part, \
            f"236.2: {who}'s comment has no Outside the plan part, behind its icon, naming the file and why:\n{part}"
    for who, part in parts[1:]:
        assert part == parts[0][1], \
            f"236.2: {who} draws Outside the plan unlike the worker:\n--- worker\n{parts[0][1]}\n--- {who}\n{part}"
    planner = section(visible(run("planner", "", dict(PLAN, questions=[QB]))[0]), "question", "Questions for you")
    assert QB["question"] in planner and QB["assumption"] in planner, \
        f"236.2: the plan's comment has no Questions for you part, behind its icon, with its question:\n{planner}"
    (run.pack / "plan.json").write_text(json.dumps(dict(PLAN, questions=[QA, QB])))
    review = section(visible(run("reviewer", "plan", dict(APPROVE, assumptions=[ACCEPT_A, DOUBT_B]))[0]),
                     "question", "Questions for you")
    assert review == planner, \
        f"236.2: the plan review draws Questions for you unlike the planner:\n--- planner\n{planner}\n--- review\n{review}"


# 236.3: the planner's criteria with their circle, Verified by and Source

def test_the_planners_comment_lists_each_criterion_with_its_circle_verified_by_and_source(record_property, run):
    """The plan's comment shows each criterion with its circle, Verified by and Source.

    Writes the planner's record from a checkout holding its tests, and checks every criterion's sentence follows the
    not started circle, and is followed, before the next criterion, by Verified by, each of its tests' docstring first
    line (never a later line or another criterion's) and, for an acceptance criterion, a link to its source.
    Proves 236.3."""
    record_property("proves", "236.3")
    body = run("planner", "", PLAN)[0]
    text = visible(body)
    circle = card.circle(REPO, "not started")
    for k, sentence in enumerate(SENTENCES, 1):
        key = f"77.{k}"
        assert sentence in text, f"236.3: the plan's comment does not show {key} {sentence!r}:\n{text}"
        assert re.search(re.escape(circle) + r"(?:\s|<[^>]+>|-)*" + re.escape(sentence), text), \
            f"236.3: {key} {sentence!r} does not follow its status circle (not started):\n{text}"
        part = segment(text, sentence, SENTENCES + [RECORD_FOLD, "<details"])
        assert "Verified by" in part, f"236.3: {key} has no Verified by under it:\n{part}"
        for doc in DOCS[key]:
            assert doc in part and part.index("Verified by") < part.index(doc), \
                f"236.3: {key}'s Verified by does not show its test's docstring {doc!r}:\n{part}"
        others = [d for kk, ds in DOCS.items() if kk != key for d in ds] + ["More words the owner never sees."]
        assert not [d for d in others if d in part], f"236.3: {key}'s Verified by shows words that are not its tests' first lines:\n{part}"
        if k <= len(PLAN["acceptance_criteria"]):
            src = PLAN["acceptance_criteria"][k - 1]["source"]
            assert f"({src})" in part or f'href="{src}"' in part, f"236.3: {key} has no Source link to {src}:\n{part}"
            assert "Source" in part and part.index(DOCS[key][-1]) < part.index("Source"), \
                f"236.3: {key}'s Source line does not come after its Verified by:\n{part}"


# 236.4: a blocking review lists only what fails, in words, with no codes

def test_a_blocking_review_lists_only_the_failing_criteria_with_why_and_source(record_property, run):
    """A blocking plan review lists only failing criteria, each with why and its Source.

    Blocks 77.2 twice and 77.4 once, with one ask nothing covers, and checks each failing sentence shows once after the
    failed circle, followed by each of its problems behind the blocker icon, then its Source link; the ask shows with
    Nothing covers this and its Source; passing criteria and covered asks never show, nor Verified by, B1 or 77.2.
    Proves 236.4."""
    record_property("proves", "236.4")
    body = run("reviewer", "plan", BLOCK)[0]
    text = visible(body)
    marks = SENTENCES + ["Email me when a job fails", RECORD_FOLD, "<details"]
    for sentence, problems, src in ((SENTENCES[1], [b["problem"] for b in BLOCK["blockers"][:2]], SRC2),
                                    (SENTENCES[3], [BLOCK["blockers"][2]["problem"]], None)):
        assert text.count(sentence) == 1, f"236.4: the failing criterion {sentence!r} does not show exactly once:\n{text}"
        assert re.search(re.escape(card.circle(REPO, "failed")) + r"(?:\s|<[^>]+>|-)*" + re.escape(sentence), text), \
            f"236.4: the failing criterion {sentence!r} does not follow the failed circle:\n{text}"
        part = segment(text, sentence, marks)
        for p in problems:
            assert p in part, f"236.4: {sentence!r} does not show why it fails ({p!r}) under it:\n{part}"
            assert re.search(re.escape(img("blocker")) + r"\s*(?:\*\*|<b>)?\s*" + re.escape(p), part), \
                f"236.4: why {sentence!r} fails ({p!r}) has no blocker icon in front:\n{part}"
        if src:
            assert (f"({src})" in part or f'href="{src}"' in part) and "Source" in part \
                and part.index(problems[-1]) < part.index("Source"), \
                f"236.4: {sentence!r} has no Source link to {src} after why it fails:\n{part}"
    ask = segment(text, "Email me when a job fails", marks)
    assert "Nothing covers this" in ask and (f"({SRC3})" in ask or f'href="{SRC3}"' in ask) and "Source" in ask, \
        f"236.4: the ask no criterion keeps does not show Nothing covers this and its Source:\n{ask}"
    for passed in (SENTENCES[0], SENTENCES[2], "Give back a job id at once", "Keep each result for a day"):
        assert passed not in text, f"236.4: the review's comment lists {passed!r}, which passed:\n{text}"
    assert "Verified by" not in text, f"236.4: the review shows Verified by; why it fails takes its place:\n{text}"
    assert not re.search(r"\bB\d+\b", text), f"236.4: the review's comment shows a blocker code like B1:\n{text}"
    assert not re.search(r"\b77\.\d+\b", plain(text)), f"236.4: the review's comment shows a criterion number like 77.2:\n{text}"


def test_a_code_review_and_a_pass_list_nothing_that_passed(record_property, run):
    """A blocking code review lists only what fails; a passing review lists nothing.

    Blocks the work on 77.3 alone and checks only that sentence shows, with why and its Source and no codes; then a
    plan review and a code review that approve show none of the plan's sentences or the owner's asks. Proves 236.4."""
    record_property("proves", "236.4")
    hb = dict(BLOCK, asks=[], blockers=[blocker("B4", "77.3", "The page is never opened in the test zq.")])
    text = visible(run("reviewer", "pr", hb)[0])
    part = segment(text, SENTENCES[2], SENTENCES + [RECORD_FOLD, "<details"])
    assert "The page is never opened in the test zq." in part and (f"({SRC3})" in part or f'href="{SRC3}"' in part), \
        f"236.4: the code review does not show its failing criterion with why and its Source:\n{text}"
    for passed in (SENTENCES[0], SENTENCES[1], SENTENCES[3]):
        assert passed not in text, f"236.4: the code review lists {passed!r}, which passed:\n{text}"
    assert not re.search(r"\bB\d+\b", text) and not re.search(r"\b77\.\d+\b", plain(text)), \
        f"236.4: the code review shows a blocker code or a criterion number:\n{text}"
    for stage in ("plan", "pr"):
        text = visible(run("reviewer", stage, APPROVE)[0])
        for passed in SENTENCES + [a["ask"] for a in ASKS]:
            assert passed not in text, f"236.4: a passing {stage} review lists {passed!r}:\n{text}"


VERDICT_WORDS = ("passed", "blocked", "escalated")


def test_a_review_comment_opens_with_its_verdict_then_the_owners_order(record_property, run):
    """A review's comment opens with its verdict, then shows its parts in the owner's order.

    Draws a plan review and a code review that pass, block and escalate, and checks each opens saying passed,
    blocked or escalated and neither of the others, while a rejected one claims no verdict. Then draws a blocking
    plan review with two failing criteria, an ask nothing covers, a change outside the plan, one assumption it
    accepted and one it could not confirm, and an issue found, and checks they show in that order (failing
    criteria, the ask, the change, the unconfirmed question, the issue) and the accepted question not at all.
    Proves 236.4."""
    record_property("proves", "236.4")
    for stage in ("plan", "pr"):
        for verdict, word in (("approve", "passed"), ("block", "blocked"), ("escalate", "escalated")):
            first = first_line(run("reviewer", stage, APPROVE if verdict == "approve" else dict(BLOCK, verdict=verdict))[0])
            assert re.search(rf"\b{word}\b", first), f"236.4: a {stage} review that says {verdict} does not open with {word!r}: {first!r}"
            for other in VERDICT_WORDS:
                assert other == word or not re.search(rf"\b{other}\b", first), \
                    f"236.4: a {stage} review that says {verdict} opens saying {other!r}: {first!r}"
        first = first_line(run("reviewer", stage, BLOCK, passed=False, problems="a problem\n")[0])
        assert not any(re.search(rf"\b{w}\b", first) for w in VERDICT_WORDS), \
            f"236.4: a {stage} review code rejected opens with a verdict it never gave: {first!r}"
    (run.pack / "plan.json").write_text(json.dumps(dict(PLAN, questions=[QA, QB])))
    hb = dict(BLOCK, outside_plan=[{"file": "app/extra.py", "change": OUTSIDE}], assumptions=[ACCEPT_A, DOUBT_B],
              issues_found=FOUND)
    text = visible(run("reviewer", "plan", hb)[0])
    order = [("the first failing criterion", SENTENCES[1]), ("the second failing criterion", SENTENCES[3]),
             ("the ask nothing covers", "Email me when a job fails"), ("the change outside the plan", OUTSIDE),
             ("the question it could not confirm", QB["question"]), ("the issue it found", "Retries are missing zq")]
    for name, words in order:
        assert text.count(words) == 1, f"236.4: the review's comment does not show {name} ({words!r}) exactly once:\n{text}"
    for (a, wa), (b, wb) in zip(order, order[1:]):
        assert text.index(wa) < text.index(wb), f"236.4: the review's comment shows {b} before {a}:\n{text}"
    for gone in (QA["question"], "Accepted on your words", "expire after a day zq", "Not accepted"):
        assert gone not in text, f"236.4: the review's comment shows {gone!r}, from an assumption it accepted or its judging:\n{text}"


# 236.5: the worker's files on one line

def test_the_files_the_worker_changed_show_on_one_line(record_property, run):
    """The worker's comment names every file it changed on one line.

    Changes one file in a commit, one left uncommitted and adds a new one, writes the worker's record, and checks one
    line below the top sentence names all three with the files changed icon and no unchanged file; the comment
    redrawn from record.json elsewhere, as after the pull request opens, still shows it. With no change, no line.
    Proves 236.5."""
    record_property("proves", "236.5")
    body = run("worker", "", WORK)[0]
    text = visible(body)
    assert "Files changed" not in plain(text) and img("files changed") not in text, \
        f"236.5: a worker that changed nothing shows a files changed line:\n{text}"
    repo = run.repo
    (repo / "app" / "jobs.py").write_text("# jobs, now async\n")
    git(repo, "commit", "-q", "-am", "jobs")
    (repo / "app" / "keep.py").write_text("# keep, a day\n")
    (repo / "app" / "queue.py").write_text("# new\n")
    body, rec = run("worker", "", WORK)
    changed = ["app/jobs.py", "app/keep.py", "app/queue.py"]
    text = visible(body)
    lines = [l for l in text.splitlines() if any(f in l for f in changed)]
    assert len(lines) == 1, f"236.5: the comment names the changed files on {len(lines)} lines, not one:\n{text}"
    line = lines[0]
    assert all(f in line for f in changed), f"236.5: the files changed line misses one of {changed}: {line}"
    assert "app/page.py" not in text, f"236.5: the comment names app/page.py, which the worker did not change:\n{text}"
    assert img("files changed") in line, f"236.5: the files changed line has no files changed icon: {line}"
    assert line not in text.split("<details", 1)[0].splitlines(), \
        f"236.5: the files changed line sits on top, where only the worker's sentence goes:\n{text}"
    os.chdir(run.tmp)
    again = visible(agent.render(rec, "https://github.com/o/r/pull/7"))
    lines = [l for l in again.splitlines() if any(f in l for f in changed)]
    assert len(lines) == 1 and all(f in lines[0] for f in changed), \
        f"236.5: the comment redrawn from its record with the pull request lost the files changed line:\n{again}"


# 236.6: stats folded at the bottom

def test_the_stats_sit_in_a_fold_at_the_bottom_of_every_run_comment(record_property, run):
    """The stats sit in a fold right above the full record, not a footnote.

    Draws the comment of a plan, a build, a plan review, a code review, a rejected run, a cancelled run and a filed
    split, and checks the last fold before the full record opens with the stats icon and holds the stats, and that
    no stats line is left outside a fold. Proves 236.6."""
    record_property("proves", "236.6")
    meta = {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1", "models": ["claude-opus-5-5"],
            "report": {"duration_ms": 240000, "turns": 23, "cost_usd": 3.2, "tokens_in": 401000, "tokens_out": 18000},
            "log": "https://g/log.md"}
    split = {"role": "split", "stage": None, "check": {"passed": True, "problems": []},
             "run": "https://github.com/o/r/actions/runs/1",
             "handback": {"stories": [{"story": 1, "issue": 201, "title": "First", "blocked_by": []}]}}
    bodies = [("plan", run("planner", "", PLAN)[0]), ("build", run("worker", "", WORK)[0]),
              ("plan review", run("reviewer", "plan", BLOCK)[0]), ("code review", run("reviewer", "pr", APPROVE)[0]),
              ("rejected run", run("planner", "", PLAN, passed=False, problems="criterion 77.2 has no test\n")[0]),
              ("cancelled run", agent.render(agent.cancelled("worker", "", True, meta))),
              ("split", agent.render(split))]
    for name, body in bodies:
        head = body.split(RECORD_FOLD, 1)[0]
        folds = DETAILS.findall(head)
        assert folds, f"236.6: the {name} comment has no fold above its full record:\n{body}"
        last = folds[-1]
        assert not head.split(last, 1)[1].strip(), f"236.6: the {name} comment's stats fold is not right above the full record:\n{body}"
        summary = re.search(r"<summary>(.*?)</summary>", last, re.S)
        assert summary and img("stats") in summary.group(1), f"236.6: the {name} comment's last fold is not the stats fold:\n{last}"
        if name == "split":
            assert "no model" in last, f"236.6: the split's stats fold does not say no model ran:\n{last}"
        else:
            for stat in ("Opus 5.5", "4.0 min", "23 turns", "401,000 tokens in, 18,000 out", "$3.20"):
                assert stat in last, f"236.6: the {name} comment's stats fold does not hold {stat!r}:\n{last}"
            outside = DETAILS.sub("", head)
            for stat in ("Opus 5.5", "23 turns", "tokens in", "at API prices"):
                assert stat not in outside, f"236.6: the {name} comment shows {stat!r} outside its stats fold:\n{outside}"
        assert "[conversation](https://g/log.md)" in body or name == "split", \
            f"236.6: the {name} comment lost its link to the run's conversation:\n{body}"


# 236.7: the record stays in its last fold

def test_the_full_record_stays_the_last_fold_under_the_stats_and_reads_back(record_property, run):
    """The full record stays the last fold, right under the stats, and reads back exactly.

    Writes the record of a plan, a build that changed a file, a blocking plan review and a code review the way the
    workflow does, and checks the stats fold comes right before the full record fold, no fold after it, and that
    reading the comment back as a record gives exactly record.json. Proves 236.7."""
    record_property("proves", "236.7")
    (run.repo / "app" / "keep.py").write_text("# changed\n")
    for name, (body, rec) in (("plan", run("planner", "", PLAN)), ("build", run("worker", "", WORK)),
                              ("plan review", run("reviewer", "plan", BLOCK)), ("code review", run("reviewer", "pr", APPROVE))):
        assert body.count(RECORD_FOLD) == 1, f"236.7: the {name} comment does not hold exactly one Full record fold:\n{body}"
        head, after = body.split(RECORD_FOLD, 1)
        assert "<details" not in after, f"236.7: a fold comes after the {name} comment's full record:\n{body}"
        folds = DETAILS.findall(head)
        assert folds and img("stats") in folds[-1] and not head.split(folds[-1], 1)[1].strip(), \
            f"236.7: the {name} comment's full record is not right under its stats fold:\n{body}"
        got = agent.records([{"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T10:00:00Z"}])
        assert got == [rec], f"236.7: the {name} record read back from its comment is not record.json: {got}"


# 236.8: a blocker the plan cannot place still shows

def test_a_blocker_the_plan_cannot_place_still_shows_why(record_property, run):
    """A blocker the plan cannot place still shows why it fails, with no code.

    Blocks on 77.9, which the plan does not have, beside a blocker on 77.2, and checks both problems show; then removes
    the pack's plan and checks a blocking review still shows every problem, without a blocker code. Proves 236.8."""
    record_property("proves", "236.8")
    hb = dict(BLOCK, blockers=[blocker("B1", "77.9", "Nothing proves the queue is emptied zq."),
                               blocker("B2", "77.2", "The day is never waited zq.")])
    text = plain(visible(run("reviewer", "pr", hb)[0]))
    for p in ("Nothing proves the queue is emptied zq.", "The day is never waited zq."):
        assert p in text, f"236.8: the review hides the blocker {p!r}:\n{text}"
    os.remove(run.pack / "plan.json")
    body = run("reviewer", "plan", BLOCK)[0]
    text = plain(visible(body))
    for b in BLOCK["blockers"]:
        assert b["problem"] in text, f"236.8: with no plan to read, the review hides the blocker {b['problem']!r}:\n{text}"
    assert not re.search(r"\bB\d+\b", text), f"236.8: with no plan to read, the review shows a blocker code:\n{text}"


# 236.9: no new raise-type field

FIELDS_READ_ON_MAIN = {
    "BASE", "BODY", "CARD_ID", "DOKIMA_BOARD", "DOKIMA_BOT", "GITHUB_ACTOR", "GITHUB_REPOSITORY", "GITHUB_RUN_ID",
    "GITHUB_SERVER_URL", "HEAD", "LOG_URL", "NUMBER", "ON_PR", "OWNERS", "PACK", "PLANNER_BASE", "ROLE", "STAGE",
    "acceptance_criteria", "accepted", "agent_started", "answer", "ask", "asks", "assumption", "assumptions", "attempt",
    "author", "base", "blocked_by", "blocker", "blockers", "body", "cache_creation_input_tokens",
    "cache_read_input_tokens", "change", "changes", "check", "check_runs", "command", "comments", "concerns",
    "conclusion", "content", "context", "cost_usd", "createdAt", "created_at", "criteria", "criterion", "depends_on",
    "dropped_by_fence", "duration_ms", "evidence", "feature", "file", "file_path", "filename", "files", "fix", "fixer",
    "handback", "headRefName", "id", "input", "input_tokens", "issue", "issues_found", "kind", "labels", "line",
    "links", "log", "login", "matched", "merge", "merged_pr", "message", "model", "models", "name", "non_functional",
    "notes", "num_turns", "number", "original_line", "out_of_scope", "output_tokens", "outside_plan", "outside_scope",
    "passed", "path", "pattern", "pr", "previous_step", "principle", "problem", "problems", "question", "questions",
    "replies", "report", "resolved", "reviews", "role", "run", "run_id", "scope", "source", "stage", "state", "status",
    "statuses", "stories", "story", "submittedAt", "summary", "suspect_tests", "test", "test_changes", "tests", "text",
    "title", "tokens_in", "tokens_out", "total_cost_usd", "turns", "type", "url", "usage", "user", "user_story",
    "verdict", "where", "why"}
RECORD_FIELDS_THIS_STORY_ADDS = {"files_changed", "verified_by"}


def fields_read(path):
    """Every field name dokima/agent.py reads by name: x["name"] or x.get("name")."""
    import ast
    out = set()
    for n in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
            out.add(n.args[0].value)
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
            out.add(n.slice.value)
    return out


def test_no_hand_back_gains_a_new_raise_type_field(record_property, run):
    """Run comments are drawn from the fields agents hand back today, never a new one.

    Reads every field name dokima/agent.py reads and checks the only new ones since main are the two this story keeps
    in the record (the worker's files changed and each test's Verified by line), so no raise-type field is added
    ahead of #289's raises and answers. Then hands back a planner, a worker and a review that also carry raises and
    answers, and checks those never show while today's question, blocker and issue found still do. Proves 236.9."""
    record_property("proves", "236.9")
    path = os.path.join(os.path.dirname(__file__), "..", "dokima", "agent.py")
    new = fields_read(path) - FIELDS_READ_ON_MAIN
    assert not new - RECORD_FIELDS_THIS_STORY_ADDS, \
        f"236.9: dokima/agent.py reads fields main never had, so a hand-back gained a field: {sorted(new - RECORD_FIELDS_THIS_STORY_ADDS)}"
    assert RECORD_FIELDS_THIS_STORY_ADDS <= new, \
        f"236.9: the record does not yet keep the worker's files changed and each test's Verified by line " \
        f"(files_changed, verified_by); dokima/agent.py reads only {sorted(new)} beyond main's fields"
    extra = {"raises": [{"kind": "question", "text": "A raise nobody may read zr."}],
             "answers": [{"raise": "R1", "answer": "done", "why": "An answer nobody may read zr."}]}
    review = dict(BLOCK, issues_found=FOUND, **extra)
    for role, stage, hb, kept in (("planner", "", dict(PLAN, questions=[QA], **extra), QA["question"]),
                                  ("worker", "", dict(WORK, **extra), WORK["summary"].split(".")[0]),
                                  ("reviewer", "plan", review, BLOCK["blockers"][0]["problem"]),
                                  ("reviewer", "pr", review, FOUND[0]["title"])):
        text = plain(visible(run(role, stage, hb)[0]))
        assert kept in text, f"236.9: the {role} {stage} comment lost {kept!r}, drawn from a field it has today:\n{text}"
        for gone in ("A raise nobody may read zr.", "An answer nobody may read zr."):
            assert gone not in text, f"236.9: the {role} {stage} comment shows a field no hand-back has today: {gone!r}"

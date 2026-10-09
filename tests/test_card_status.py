"""The card says what the issue is, where it stands, its children, and what the owner must do.

Issue #181 (story 3 of #143). Every plan.json carries a one-sentence "summary" of what the issue is about, and the
planner's check rejects a plan without one. The card (`dokima/card.py`) opens with that sentence, then one small
status line, never a heading:

    card.status(issue, found) -> (stage, todo)
        stage  "Backlog", "Plan", "Work", "Review" (the board's columns) or "Merged"
        todo   None when nothing is the owner's to do, else the owner's to-do, word for word one of TODO below:
               a plan with questions, an approved plan, three blocks in a row, a rejected hand-back, a run that never
               started, an escalation, approved work with every check green ("Ready for approval"), and approved work
               whose checks have not all passed
        `found` is what card.render takes (see tests/test_card_records.py), plus
                "items":    the conversation the records come from (dokima.agent.conversation), oldest first
                "children": for a filed split, [{"number", "title", "stage"}] in the split's order

The stage and the Needs you pill follow the board's own rule, dokima.agent.board_place() on the newest record and
dokima.agent.next_step() as it was decided when that record was posted (the conversation before it), so the card and
the board never disagree. Three cases come before the rule: a merged PR is Merged, an issue with no records is in
Backlog, and a filed split (its newest record is a "split") is in Work with nothing for the owner, as
`python3 -m dokima.agent split` places it on the board.

Layout, as these tests read it: inside the card's markers the first line is the plan's summary sentence and the next
is the status line (with no plan, the status line comes first). The status line starts with the stage word (HTML tags,
'*' and '_' aside), says "Needs you" followed by the to-do exactly when there is one, and never starts with '#'. A
filed split lists each child on its own line with a link to https://github.com/<repo>/issues/<n> and its stage, or
"unknown" when its stage could not be read.

`python3 dokima/card.py gallery DIR` draws the card of every situation the owner looks at on a real throwaway issue
and PR, one file each: planned.md, building.md, checks-failing.md, ready.md, merged.md, split.md, no-plan.md.
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card, plan, planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
SRC = "https://github.com/o/r/issues/40"
BOT = "dokima-runtime"
OWNER = "boss"
SUMMARY = "Slow calls hand back a job id instead of timing out."
STAGES = ("Backlog", "Plan", "Work", "Review", "Merged")
PLAN = {"kind": "user_story", "summary": SUMMARY,
        "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": "First thing works", "source": SRC},
                                {"text": "Second thing works", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks out", "why": "safety", "principle": "Fail closed"}],
        "scope": ["dokima/card.py", "tests/test_a.py"], "out_of_scope": ["The board stays as it is."],
        "tests": {"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_two"],
                  "40.3": ["tests/test_a.py::test_three"]},
        "test_changes": {}}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}


def rec(role, stage=None, passed=True, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": passed, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}", "run_id": str(n)}


PLANNED = rec("planner", n=11, **PLAN)
ASKS = rec("planner", n=11, **dict(PLAN, questions=[{"question": "Which one?", "assumption": "The first."}]))
PLAN_OK = rec("reviewer", "plan", n=12, verdict="approve", blockers=[])
PLAN_BLOCK = rec("reviewer", "plan", n=12, verdict="block", blockers=[{"id": "B1", "fixer": "planner"}])
BUILT = rec("worker", n=13)
CODE_OK = rec("reviewer", "pr", n=14, verdict="approve", blockers=[])
CODE_BLOCK = rec("reviewer", "pr", n=14, verdict="block", blockers=[{"id": "B1", "fixer": "worker"}])
ESCALATED = rec("reviewer", "pr", n=14, verdict="escalate", blockers=[])
REJECTED = rec("planner", passed=False, n=15, **PLAN)
CANCELLED = {"role": "cancelled", "attempt": "worker", "stage": None, "handback": {},
             "check": {"passed": False, "problems": []}, "run": "https://github.com/o/r/actions/runs/16"}
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40"}


def run(name, status="completed", conclusion="success", n=7):
    """One GitHub check run on the PR's latest commit."""
    return {"name": name, "status": status, "conclusion": conclusion,
            "html_url": f"https://github.com/o/r/actions/runs/2/job/{n}"}


GREEN = [run("40.1 · First thing works", n=1), run("40.2 · Second thing works", n=2),
         run("40.3 · Nothing leaks out", n=3), run("All tests", n=4)]


def comment(login, body, i):
    """One comment of the conversation, as dokima.agent.conversation lists it."""
    return {"author": {"login": login}, "body": body, "createdAt": f"2026-10-08T{i:02d}:00:00Z", "where": "issue #40"}


def said(*steps, start=0):
    """The conversation of a run of records and owner comments (a str is the owner's words), from hour `start` on."""
    items = []
    for i, s in enumerate(steps, start):
        if isinstance(s, str):
            items.append(comment(OWNER, s, i))
        else:
            items.append(comment(BOT, f"{agent.MARK}\n**Card**\n\n```json\n{json.dumps(s)}\n```\n", i))
    return items


def found_for(steps, pr=None, check_runs=(), **kw):
    """What the card is drawn from for issue #40 after these steps."""
    items = said(*steps)
    f = {"recs": agent.records(items), "items": items, "pr": pr, "check_runs": list(check_runs), "reviews": [],
         "owners": {OWNER}, "tests": {}, "worker": DONE, "children": []}
    return dict(f, **kw)


def status(found, k):
    """card.status for issue #40, or a plain failure naming criterion k while it does not exist."""
    if not hasattr(card, "status"):
        pytest.fail(f"{k}: the card has no status yet: card.status(issue, found) does not exist")
    return card.status(ISSUE, found)


def draw(found, page="issue"):
    return card.render(REPO, ISSUE, found, page=page)


def lines_of(text):
    """The card's non-empty lines between its markers."""
    assert plan.CARD_START in text and plan.CARD_END in text, "the text holds no card between its markers"
    inside = text[text.index(plan.CARD_START) + len(plan.CARD_START):text.index(plan.CARD_END)]
    return [l.strip() for l in inside.splitlines() if l.strip()]


def bare(line):
    """A line without its HTML tags, '*', '_' and backticks."""
    return re.sub(r"[*_`]", "", re.sub(r"<[^>]+>", "", line)).strip()


def status_line(text, planned=True):
    """The status line: the second line of the card when it has a plan, the first when it has none."""
    found = lines_of(text)
    return found[1 if planned else 0]


def board(items, k):
    """The board's (column, Needs you) for the newest record, decided as the river decided it when it was posted."""
    at = max(i for i, c in enumerate(items) if agent.is_record(c))
    newest = agent.records([items[at]])[0]
    return agent.board_place(newest, agent.next_step(items[:at], newest, [OWNER]))


@pytest.fixture(autouse=True)
def bot(monkeypatch):
    monkeypatch.setattr(agent, "BOT", BOT)


# 181.1: plan.json carries a one-sentence summary; the prompt asks for it and the check rejects a plan without it

STORY_PLAN = {"kind": "user_story", "summary": SUMMARY, "user_story": "Slow calls return a job id.",
              "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": "https://github.com/o/r/issues/9"}],
              "non_functional": [], "scope": ["dokima/jobs.py"], "out_of_scope": [],
              "tests": {"9.1": ["tests/test_jobs.py::test_id"]}, "test_changes": {}}
FEATURE_PLAN = {"kind": "feature", "summary": SUMMARY, "feature": "Slow calls run as jobs.", "stories": [
    {"title": t, "user_story": f"Owners get {t}.", "acceptance_criteria": [{"text": f"{t} works.", "source": "https://github.com/o/r/issues/9"}],
     "non_functional": [], "depends_on": []} for t in ("Jobs", "Results")]}


@pytest.mark.parametrize("good", [STORY_PLAN, FEATURE_PLAN], ids=["user_story", "feature"])
def test_a_plan_without_a_summary_is_rejected_naming_the_field(record_property, tmp_path, good):
    """A user story or a feature handed back without its one-sentence summary is rejected, and the reason names summary.

    Reads plan.json the way the planner check does: with the summary it is accepted; with the summary missing, empty,
    blank or not text it is rejected, and the reason says summary."""
    record_property("proves", "181.1")
    (tmp_path / "plan.json").write_text(json.dumps(good))
    try:
        planner.read_output(str(tmp_path))
    except planner.Garbled as e:
        pytest.fail(f"181.1: a {good['kind']} with its summary was rejected: {e}")
    for name, breaks in (("missing", lambda p: p.pop("summary")), ("empty", lambda p: p.update(summary="")),
                         ("blank", lambda p: p.update(summary="   ")), ("not text", lambda p: p.update(summary=["a"]))):
        bad = json.loads(json.dumps(good))
        breaks(bad)
        (tmp_path / "plan.json").write_text(json.dumps(bad))
        with pytest.raises(planner.Garbled) as e:
            planner.read_output(str(tmp_path))
            pytest.fail(f"181.1: a {good['kind']} whose summary is {name} was accepted")
        assert "summary" in str(e.value), f"181.1: the rejection of a {name} summary does not name the field: {e.value}"


def test_the_planner_check_command_rejects_a_split_without_a_summary(record_property, tmp_path):
    """Running the planner check on a split with no summary fails and says summary; with one, it passes.

    Runs `python3 -m dokima.planner check` from the repo root on a hand-back folder holding a feature without its
    summary, then on the same feature with it."""
    record_property("proves", "181.1")
    bad = {k: v for k, v in FEATURE_PLAN.items() if k != "summary"}
    env = dict(os.environ, GITHUB_REPOSITORY="o/r", GITHUB_SERVER_URL="https://github.com", PYTHONPATH=ROOT)
    env.pop("PYTHONSAFEPATH", None)
    (tmp_path / "plan.json").write_text(json.dumps(bad))
    out = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)], cwd=ROOT,
                         env=env, capture_output=True, text=True, timeout=60)
    assert out.returncode != 0, "181.1: the planner check passed a split with no summary"
    assert "summary" in out.stdout + out.stderr, f"181.1: the check's reason does not name summary: {out.stdout}{out.stderr}"
    os.remove(tmp_path / "rejected.txt") if (tmp_path / "rejected.txt").exists() else None
    (tmp_path / "plan.json").write_text(json.dumps(FEATURE_PLAN))
    out = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)], cwd=ROOT,
                         env=env, capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"181.1: the planner check rejected a split with its summary: {out.stdout}{out.stderr}"


def test_the_planner_prompt_asks_for_the_summary_in_both_kinds(record_property):
    """The planner's prompt shows the summary field in the user story's shape and in the feature's shape.

    Reads 'What you hand back' in dokima/roles/planner.md and checks the user story's JSON shape and the feature's
    JSON shape each hold "summary", and that the prompt says it is one sentence on what the issue is about."""
    record_property("proves", "181.1")
    text = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
    assert "# What you hand back" in text, "181.1: the planner prompt has no 'What you hand back' section"
    section = text[text.index("# What you hand back"):]
    story = section[section.index('{"kind": "user_story"'):section.index("- A feature:")]
    feature = section[section.index('{"kind": "feature"'):]
    feature = feature[:feature.index("2 to 5 stories")]
    assert '"summary"' in story, "181.1: the user story's shape in the planner prompt has no summary"
    assert '"summary"' in feature, "181.1: the feature's shape in the planner prompt has no summary"
    words = " ".join(section.split()).lower()
    assert re.search(r"summary[^.]*one[^.]*sentence|one[^.]*sentence[^.]*summary", words), \
        "181.1: the planner prompt never says the summary is one sentence"


# 181.2: the card opens with the sentence, then a small status line: the stage and the owner's to-do, as the board has it

def test_the_card_opens_with_the_summary_then_a_status_line(record_property):
    """The card opens with the plan's one-sentence summary, then a status line that is not a heading.

    Draws the card of an approved plan and checks its first line is the summary, its second the status line naming
    the stage and what the owner must do, and that no line of the card is a heading."""
    record_property("proves", "181.2")
    text = draw(found_for([PLANNED, PLAN_OK]))
    first = lines_of(text)[0]
    assert bare(first) == SUMMARY, f"181.2: the card does not open with the summary sentence: “{first}”"
    line = status_line(text)
    assert bare(line).startswith("Plan"), f"181.2: the status line does not start with the stage Plan: “{line}”"
    assert "Needs you" in line, f"181.2: the status line does not say what the owner must do: “{line}”"
    for l in lines_of(text):
        assert not l.startswith("#"), f"181.2: the card has a heading: “{l}”"


def test_the_status_line_is_empty_of_todos_when_nothing_is_the_owners(record_property):
    """When nothing is the owner's to do, the status line names only the stage and never says Needs you.

    Draws the card while the reviewer grades a fresh plan and while the worker fixes a blocked build, and checks the
    status line names Plan and then Work, with no Needs you."""
    record_property("proves", "181.2")
    for steps, stage in (([PLANNED], "Plan"), ([PLANNED, PLAN_OK, "/work", BUILT, CODE_BLOCK], "Work")):
        line = status_line(draw(found_for(steps, pr=PR, check_runs=GREEN)))
        assert bare(line).startswith(stage), f"181.2: the status line does not start with {stage}: “{line}”"
        assert "Needs you" not in line, f"181.2: the status line says Needs you when nothing is the owner's: “{line}”"


NOT_STARTED = {"role": "not-started", "attempt": "worker", "stage": None, "handback": {},
               "check": {"passed": False, "problems": []}, "run": "https://github.com/o/r/actions/runs/19"}
RED = [dict(r, conclusion="failure") if r["name"].startswith("40.2") else r for r in GREEN]

# The owner's to-do at each stop, word for word (backticks, '*' and '_' aside), as 181.2 names them.
TODO = {"questions": "Answer the questions with /plan, or say /review",
        "plan approved": "Say /work to build the plan",
        "three blocks": "Three blocks in a row: your call",
        "rejected": "Fix the rejected hand-back",
        "not started": "Fix why nothing ran",
        "escalated": "Settle the escalation",
        "ready": "Ready for approval",
        "not every check passed": "See why not every check passed"}

CASES = [
    ("a fresh plan goes to the reviewer", [PLANNED], ("Plan", False), None, GREEN),
    ("a plan with questions waits for the owner", [ASKS], ("Plan", True), TODO["questions"], GREEN),
    ("an approved plan waits for /work", [PLANNED, PLAN_OK], ("Plan", True), TODO["plan approved"], GREEN),
    ("a blocked plan goes back to the planner", [PLANNED, PLAN_BLOCK], ("Plan", False), None, GREEN),
    ("a second block in a row still goes back", [PLANNED, PLAN_BLOCK, PLANNED, PLAN_BLOCK], ("Plan", False), None, GREEN),
    ("a third block in a row waits for the owner", [PLANNED, PLAN_BLOCK, PLANNED, PLAN_BLOCK, PLANNED, PLAN_BLOCK],
     ("Plan", True), TODO["three blocks"], GREEN),
    ("a third code block in a row waits for the owner",
     [PLANNED, PLAN_OK, "/work", BUILT, CODE_BLOCK, BUILT, CODE_BLOCK, BUILT, CODE_BLOCK],
     ("Review", True), TODO["three blocks"], GREEN),
    ("the owner speaking resets the count", [PLANNED, PLAN_BLOCK, PLANNED, PLAN_BLOCK, "/plan go on", PLANNED, PLAN_BLOCK],
     ("Plan", False), None, GREEN),
    ("a rejected hand-back waits for the owner", [REJECTED], ("Plan", True), TODO["rejected"], GREEN),
    ("a run that never started waits for the owner", [PLANNED, PLAN_OK, "/work", NOT_STARTED], ("Work", True),
     TODO["not started"], GREEN),
    ("a build goes to the code reviewer", [PLANNED, PLAN_OK, "/work", BUILT], ("Review", False), None, GREEN),
    ("a blocked build goes back to the worker", [PLANNED, PLAN_OK, "/work", BUILT, CODE_BLOCK], ("Work", False), None, GREEN),
    ("an escalation waits for the owner", [PLANNED, PLAN_OK, "/work", BUILT, ESCALATED], ("Review", True),
     TODO["escalated"], GREEN),
    ("approved work with every check green waits for the owner", [PLANNED, PLAN_OK, "/work", BUILT, CODE_OK],
     ("Review", True), TODO["ready"], GREEN),
    ("approved work with a failed check waits for the owner", [PLANNED, PLAN_OK, "/work", BUILT, CODE_OK],
     ("Review", True), TODO["not every check passed"], RED),
    ("a cancelled run waits for no one", [PLANNED, PLAN_OK, "/work", CANCELLED], ("Work", False), None, GREEN),
]


@pytest.mark.parametrize("name,steps,want,todo_want,checks_", CASES, ids=[c[0] for c in CASES])
def test_the_status_agrees_with_the_boards_needs_you_pill(record_property, name, steps, want, todo_want, checks_):
    """The card's stage and Needs you are exactly the board's column and pill, and the to-do says what the owner must do.

    For each situation the river can stop or go on in, works out the board's column and pill with the river's own
    code (dokima.agent.board_place and next_step, as decided when the newest record was posted) and checks the card
    gives the same stage, has a to-do exactly when the board shows Needs you, and that the to-do is the one named for
    that stop (answer the questions, say /work, your call after three blocks, fix the rejected hand-back, fix why
    nothing ran, settle the escalation, Ready for approval, or see why not every check passed), on the status line."""
    record_property("proves", "181.2")
    built = any(s is BUILT for s in steps)
    f = found_for(steps, pr=PR if built else None, check_runs=checks_ if built else ())
    assert board(f["items"], "181.2") == want, f"181.2: the river itself no longer places “{name}” at {want}"
    stage, todo = status(f, "181.2")
    assert (stage, todo is not None) == want, \
        f"181.2: {name}: the card says {stage} with to-do {todo!r}; the board has {want[0]} with Needs you {want[1]}"
    if todo_want is not None:
        assert bare(todo) == todo_want, f"181.2: {name}: the owner's to-do is “{todo}”, not “{todo_want}”"
    line = status_line(draw(f), planned=agent.latest(f["recs"], "planner") is not None)
    assert ("Needs you" in line) == want[1], f"181.2: {name}: the status line “{line}” disagrees with the board's pill"
    if todo_want is not None:
        assert todo_want in bare(line), f"181.2: {name}: the status line “{line}” does not say the to-do “{todo_want}”"


def test_an_issue_with_no_records_is_in_backlog_and_a_filed_split_is_in_work(record_property):
    """An issue no agent has touched shows Backlog, and a parent whose split was filed shows Work, neither needing you.

    Draws the status with no records at all, then after the split's stories were filed, and checks Backlog and Work,
    both without a to-do, as the board places them."""
    record_property("proves", "181.2")
    assert status(found_for([]), "181.2") == ("Backlog", None), "181.2: an untouched issue is not in Backlog"
    line = status_line(draw(found_for([])), planned=False)
    assert bare(line).startswith("Backlog") and "Needs you" not in line, f"181.2: wrong status line with no records: “{line}”"
    split = rec("split", n=20, stories=[{"story": 1, "issue": 41, "title": "One", "blocked_by": []},
                                        {"story": 2, "issue": 42, "title": "Two", "blocked_by": [1]}])
    feature = rec("planner", n=18, **dict(FEATURE_PLAN, summary=SUMMARY))
    got = status(found_for([feature, PLAN_OK, "/work", split]), "181.2")
    assert got == ("Work", None), f"181.2: a filed split shows {got}, not Work with nothing for the owner"


def test_the_card_opens_with_the_status_line_when_there_is_no_plan(record_property):
    """With no plan yet, the card opens with the status line and says there is no plan yet.

    Draws the card with no records and with only a rejected plan, and checks the first line is the status line
    (no heading) and that the card says it has no plan yet."""
    record_property("proves", "181.2")
    for steps in ([], [REJECTED]):
        text = draw(found_for(steps))
        first = lines_of(text)[0]
        assert not first.startswith("#") and any(bare(first).startswith(s) for s in STAGES), \
            f"181.2: the card with no plan does not open with its status line: “{first}”"
        assert "no plan yet" in text, "181.2: the card with no plan does not say so"


# 181.3: a split lists each child with its link and its current stage

CHILDREN = [{"number": 41, "title": "First child", "stage": "Plan"},
            {"number": 42, "title": "Second child", "stage": "Merged"},
            {"number": 43, "title": "Third child", "stage": "Review"}]
SPLIT = rec("split", n=20, stories=[{"story": i, "issue": c["number"], "title": c["title"], "blocked_by": []}
                                    for i, c in enumerate(CHILDREN, 1)])
FEATURE = rec("planner", n=18, **FEATURE_PLAN)


def child_line(text, n, k):
    """The one line of the card linking child issue n; fails naming criterion k when there is not exactly one."""
    url = f"https://github.com/o/r/issues/{n}"
    found = [l for l in lines_of(text) if url in l]
    assert len(found) == 1, f"{k}: expected one line linking child #{n} ({url}), found {len(found)}"
    return found[0]


def test_a_split_lists_each_child_with_its_link_and_stage(record_property):
    """A split's card lists every child, in order, each with a link to its issue and its own current stage.

    Draws the card of a parent whose split was filed into three children at three different stages, and checks
    each child has one line with its link, its title and its own stage, in the split's order; the card of a story
    that was not split links no other issue."""
    record_property("proves", "181.3")
    text = draw(found_for([FEATURE, PLAN_OK, "/work", SPLIT], children=CHILDREN))
    at = []
    for c in CHILDREN:
        line = child_line(text, c["number"], "181.3")
        assert c["title"] in line, f"181.3: child #{c['number']}'s line does not show its title: “{line}”"
        words = re.findall(r"\b(" + "|".join(STAGES) + r"|unknown)\b", bare(line))
        assert words == [c["stage"]], f"181.3: child #{c['number']} should show {c['stage']}, shows {words}: “{line}”"
        at.append(lines_of(text).index(line))
    assert at == sorted(at), "181.3: the children are not listed in the split's order"
    plain = draw(found_for([PLANNED, PLAN_OK]))
    assert not re.search(r"https://github\.com/o/r/issues/(?!40\b)\d+", plain), "181.3: a story that was not split lists children"


def fake_github(monkeypatch, tmp_path, broken=()):
    """Fake GitHub for parent #40, filed into children #41 to #45, serving card.gh, agent.gh and plan.gh.

    #41 has no records (Backlog). #42 has a plan with questions (Plan). #43 was built: the worker's record sits on its
    open PR #8 (Review). #44's PR #9 is merged after an approving code review (Merged). Every read about the issues
    in `broken` fails, as GitHub fails when an issue cannot be read. It serves the ways Dokima reads GitHub today: the
    REST API (`gh api repos/...`), `gh issue view`, `gh pr view` and `gh pr list`; anything else fails naming 181.3.
    """
    stories = [{"story": i, "issue": n, "title": f"Child {n}", "blocked_by": []} for i, n in enumerate(range(41, 46), 1)]
    split = rec("split", n=20, stories=stories)
    feature = rec("planner", n=18, **dict(FEATURE_PLAN, stories=FEATURE_PLAN["stories"] * 2 + FEATURE_PLAN["stories"][:1]))
    issue_comments = {40: said(feature, PLAN_OK, "/work", split), 41: [], 42: said(ASKS), 43: said(PLANNED, PLAN_OK, "/work"),
                      44: said(PLANNED, PLAN_OK, "/work"), 45: said(PLANNED)}
    prs = {8: {"issue": 43, "merged": False, "state": "open", "comments": said(BUILT, start=5)},
           9: {"issue": 44, "merged": True, "state": "closed", "comments": said(BUILT, CODE_OK, start=5)}}

    def pr_of(n):
        return [p for p, v in prs.items() if v["issue"] == n]

    def rest_comment(c):
        return {"user": {"login": c["author"]["login"] + ("[bot]" if c["author"]["login"] == BOT else ""), "type": "User"},
                "body": c["body"], "created_at": c["createdAt"], "html_url": SRC}

    def pull(p):
        v = prs[p]
        return {"number": p, "state": v["state"], "merged": v["merged"], "merged_at": "2026-10-08T09:00:00Z" if v["merged"] else None,
                "body": f"Closes #{v['issue']}", "html_url": f"https://github.com/o/r/pull/{p}", "title": f"Child {v['issue']}",
                "head": {"sha": f"sha{p}", "ref": f"try/issue-{v['issue']}"}, "base": {"ref": "main", "sha": "base0"}}

    def touches(args):
        return any(a == str(n) or f"issue-{n}" in a or f"issue-{n}%" in a or re.search(rf"/issues/{n}\b", a)
                   or (a in {str(p) for p in pr_of(n)}) or re.search(rf"/pulls/({'|'.join(map(str, pr_of(n))) or 'x'})\b", a)
                   for n in broken for a in args)

    def gh(*args, **kw):
        args = [str(a) for a in args]
        if touches(args):
            raise subprocess.CalledProcessError(1, ["gh", *args], "", "HTTP 404: Not Found")
        if args[:2] == ["issue", "view"]:
            n = int(args[2])
            return json.dumps({"number": n, "title": f"Child {n}" if n != 40 else "Parent", "body": "ask", "state": "OPEN",
                               "url": f"https://github.com/o/r/issues/{n}", "comments": issue_comments[n]})
        if args[:2] == ["pr", "view"]:
            p = int(args[2])
            v = pull(p)
            return json.dumps({"number": p, "body": v["body"], "headRefOid": v["head"]["sha"], "headRefName": v["head"]["ref"],
                               "state": "MERGED" if prs[p]["merged"] else "OPEN", "mergedAt": v["merged_at"],
                               "comments": prs[p]["comments"], "reviews": [], "url": v["html_url"]})
        if args[:2] == ["pr", "list"]:
            head = next((a for a in args if re.fullmatch(r"(try|work)/issue-\d+", a)), "")
            n = int(head.rsplit("-", 1)[1]) if head.startswith("try/") else None
            open_only = "open" in args and "all" not in args
            return json.dumps([{"number": p} for p in pr_of(n) if not (open_only and prs[p]["state"] != "open")] if n else [])
        if args[0] != "api":
            raise AssertionError(f"181.3: card.gather asked GitHub something the fake does not serve: {args}")
        target = next(a for a in args[1:] if a.startswith("repos/") or a.startswith("/repos/")).lstrip("/")
        path, _, query = target.partition("?")
        query = query.replace("%2F", "/").replace("%3A", ":")
        if path == "repos/o/r/contents/.github/CODEOWNERS":
            return f"* @{OWNER}\n"
        if path == "repos/o/r/pulls":
            m = re.search(r"head=o:try/issue-(\d+)", query)
            return json.dumps([pull(p) for p in pr_of(int(m.group(1)))] if m else [])
        m = re.fullmatch(r"repos/o/r/pulls/(\d+)(/\w+)?", path)
        if m and int(m.group(1)) in prs:
            p = int(m.group(1))
            return json.dumps({None: pull(p), "/reviews": [], "/comments": [], "/files": []}[m.group(2)])
        m = re.fullmatch(r"repos/o/r/issues/(\d+)(/comments)?", path)
        if m:
            n = int(m.group(1))
            if m.group(2):
                return json.dumps([rest_comment(c) for c in issue_comments.get(n) or
                                   next((prs[p]["comments"] for p in prs if p == n), [])])
            return json.dumps({"number": n, "title": f"Child {n}", "body": "ask", "state": "open",
                               "html_url": f"https://github.com/o/r/issues/{n}"})
        m = re.fullmatch(r"repos/o/r/commits/sha(\d+)/(check-runs|pulls)", path)
        if m:
            return json.dumps({"total_count": 0, "check_runs": []} if m.group(2) == "check-runs" else [pull(int(m.group(1)))])
        if path == "repos/o/r/actions/workflows/worker.yml/runs":
            return json.dumps({"workflow_runs": []})
        raise AssertionError(f"181.3: card.gather asked GitHub something the fake does not serve: {args}")

    (tmp_path / ".github").mkdir(exist_ok=True)
    (tmp_path / ".github" / "CODEOWNERS").write_text(f"* @{OWNER}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    for module in (card, agent, plan):
        monkeypatch.setattr(module, "gh", gh)


def test_the_card_reads_each_childs_stage_from_its_own_records_and_pr(record_property, monkeypatch, tmp_path):
    """Each child's stage on the parent's card comes from that child's own records and PR.

    Runs the real card.gather for a parent split into four children against a faked GitHub, and checks it lists them
    in order with their titles and stages: Backlog with no records, Plan with a plan waiting on questions, Review once
    built, Merged once its PR merged."""
    record_property("proves", "181.3")
    fake_github(monkeypatch, tmp_path)
    found = card.gather(REPO, 40, None)
    kids = [(c.get("number"), c.get("title"), c.get("stage")) for c in found.get("children") or []]
    want = [(41, "Child 41", "Backlog"), (42, "Child 42", "Plan"), (43, "Child 43", "Review"), (44, "Child 44", "Merged")]
    assert kids[:4] == want, f"181.3: the children read from GitHub are {kids}, not {want}"
    text = card.render(REPO, ISSUE, found, page="issue")
    for n, _, stage in want:
        assert stage in bare(child_line(text, n, "181.3")), f"181.3: child #{n} is not shown as {stage}"


# 181.4: Ready for approval only when every criterion has a passing check; Merged once the PR is merged

APPROVED_WORK = [PLANNED, PLAN_OK, "/work", BUILT, CODE_OK]


def test_ready_for_approval_when_every_criterion_and_all_tests_passed(record_property):
    """Approved work whose every criterion's check and All tests passed says Ready for approval, and needs the owner.

    Draws the status after an approving code review with every check green, and checks it is Review with the to-do
    Ready for approval, and that the status line says it."""
    record_property("proves", "181.4")
    f = found_for(APPROVED_WORK, pr=PR, check_runs=GREEN)
    assert status(f, "181.4") == ("Review", "Ready for approval"), \
        f"181.4: approved work with every check green shows {status(f, '181.4')}, not Review, Ready for approval"
    line = status_line(draw(f))
    assert "Ready for approval" in line and "Needs you" in line, f"181.4: the status line does not ask for approval: “{line}”"


def without(name):
    return [r for r in GREEN if not r["name"].startswith(name)]


def swap(name, **kw):
    return [dict(r, **kw) if r["name"].startswith(name) else r for r in GREEN]


NOT_READY = [
    ("a criterion's check failed", swap("40.2", conclusion="failure")),
    ("a criterion has no check", without("40.1")),
    ("a criterion's check is still running", swap("40.1", status="in_progress", conclusion=None)),
    ("a criterion's check was skipped", swap("40.2", conclusion="skipped")),
    ("a non-functional requirement has no check", without("40.3")),
    ("a non-functional requirement's check failed", swap("40.3", conclusion="failure")),
    ("All tests failed", swap("All tests", conclusion="failure")),
    ("All tests has not run", without("All tests")),
    ("no check ran at all", []),
]


@pytest.mark.parametrize("name,checks_", NOT_READY, ids=[c[0] for c in NOT_READY])
def test_never_ready_for_approval_unless_every_check_passed(record_property, name, checks_):
    """Approved work never says Ready for approval while any criterion's check, or All tests, has not passed.

    Draws the status after an approving code review with one check missing, running, skipped or failed, and checks
    the owner is still needed (the river stopped) but the card never says Ready for approval."""
    record_property("proves", "181.4")
    f = found_for(APPROVED_WORK, pr=PR, check_runs=checks_)
    stage, todo = status(f, "181.4")
    assert todo is not None, f"181.4: {name}: the river stopped for the owner but the card has no to-do"
    assert todo != "Ready for approval", f"181.4: {name}: the card says Ready for approval"
    assert bare(todo) == TODO["not every check passed"], f"181.4: {name}: the owner's to-do is “{todo}”"
    assert "Ready for approval" not in draw(f), f"181.4: {name}: the card says Ready for approval"


def test_never_ready_for_approval_before_the_code_review_approves(record_property):
    """Green checks alone never say Ready for approval: the code review must have approved the latest build.

    Draws the card with every check green after the worker built, after a blocking code review, and after an
    approval followed by a new build, and checks none says Ready for approval."""
    record_property("proves", "181.4")
    for steps in ([PLANNED, PLAN_OK, "/work", BUILT], [PLANNED, PLAN_OK, "/work", BUILT, CODE_BLOCK],
                  [PLANNED, PLAN_OK, "/work", BUILT, ESCALATED], [PLANNED, PLAN_OK, "/work", BUILT, CODE_OK, rec("worker", n=17)]):
        f = found_for(steps, pr=PR, check_runs=GREEN)
        assert status(f, "181.4")[1] != "Ready for approval", "181.4: the card is Ready for approval without a current code review approval"
        assert "Ready for approval" not in draw(f), "181.4: the card says Ready for approval without a current approval"


def test_merged_once_the_pr_is_merged(record_property):
    """Once the PR is merged the status says Merged with nothing for the owner; before that it never says Merged.

    Draws the card of approved work with its PR merged (with a failing check left over), and checks the status is
    Merged with no to-do and no Ready for approval; then with the PR open and closed unmerged, and checks neither says
    Merged."""
    record_property("proves", "181.4")
    f = found_for(APPROVED_WORK, pr=dict(PR, merged=True, state="closed"), check_runs=swap("40.2", conclusion="failure"))
    assert status(f, "181.4") == ("Merged", None), f"181.4: a merged PR shows {status(f, '181.4')}, not Merged"
    line = status_line(draw(f))
    assert bare(line).startswith("Merged") and "Needs you" not in line and "Ready for approval" not in line, \
        f"181.4: the merged card's status line is “{line}”"
    for pr in (PR, dict(PR, state="closed")):
        f = found_for(APPROVED_WORK, pr=pr, check_runs=GREEN)
        assert status(f, "181.4")[0] != "Merged", f"181.4: a PR that is {pr['state']} and not merged shows Merged"
        assert "Merged" not in bare(status_line(draw(f))), f"181.4: a PR that is {pr['state']} and not merged says Merged"


# 181.5 (manual, with this automated part): every situation is drawn for the owner to put on a throwaway issue and PR

SITUATIONS = ["planned", "building", "checks-failing", "ready", "merged", "split", "no-plan"]


def test_the_gallery_draws_every_situation_for_the_owner_to_look_at(record_property, tmp_path):
    """One command draws the card of every situation the owner will look at on a throwaway issue and PR.

    Runs `python3 dokima/card.py gallery DIR` from the repo root and checks it writes one card per situation, each
    showing that situation: planned, building, checks failing, ready, merged, split with children at different
    stages, and an issue with no plan."""
    record_property("proves", "181.5")
    env = dict(os.environ, REPO=REPO, PYTHONPATH=ROOT)
    env.pop("PYTHONSAFEPATH", None)
    out = subprocess.run([sys.executable, os.path.join("dokima", "card.py"), "gallery", str(tmp_path)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=60)
    said_ = (out.stderr.strip().splitlines() or [""])[-1]
    assert out.returncode == 0, f"181.5: `python3 dokima/card.py gallery DIR` did not draw the gallery (exit {out.returncode}): {said_}"
    cards = {}
    for s in SITUATIONS:
        path = tmp_path / f"{s}.md"
        assert path.exists(), f"181.5: the gallery did not draw the {s} situation ({s}.md)"
        cards[s] = path.read_text()
        lines_of(cards[s])
    def line(s):
        return bare(status_line(cards[s], planned=s != "no-plan"))
    assert line("planned").startswith("Plan"), f"181.5: the planned card's status is “{line('planned')}”"
    assert line("building").startswith("Work") and "Needs you" not in line("building"), \
        f"181.5: the building card's status is “{line('building')}”"
    assert 'alt="failed"' in cards["checks-failing"] and "Ready for approval" not in cards["checks-failing"], \
        "181.5: the checks-failing card shows no failed check, or says Ready for approval"
    assert "Ready for approval" in line("ready"), f"181.5: the ready card's status is “{line('ready')}”"
    assert line("merged").startswith("Merged"), f"181.5: the merged card's status is “{line('merged')}”"
    assert "no plan yet" in cards["no-plan"], "181.5: the no-plan card does not say there is no plan yet"
    kids = [l for l in lines_of(cards["split"]) if re.search(r"https://github\.com/[^/]+/[^/]+/issues/\d+", l)]
    stages = {w for l in kids for w in re.findall(r"\b(" + "|".join(STAGES) + r")\b", bare(l))}
    assert len(kids) >= 2 and len(stages) >= 2, f"181.5: the split card does not list children at different stages: {kids}"


# 181.6: a child whose stage cannot be read shows as unknown, never as done

def test_a_child_that_cannot_be_read_shows_as_unknown(record_property, monkeypatch, tmp_path):
    """A child GitHub cannot read shows as unknown on the parent's card, never as merged or done.

    Runs the real card.gather against a faked GitHub where every read about child #45 fails, and checks #45 is
    listed as unknown while the other children keep their stages."""
    record_property("proves", "181.6")
    fake_github(monkeypatch, tmp_path, broken=(45,))
    found = card.gather(REPO, 40, None)
    kids = {c.get("number"): c.get("stage") for c in found.get("children") or []}
    assert kids.get(45) == "unknown", f"181.6: a child that cannot be read shows as {kids.get(45)!r}, not unknown"
    assert kids.get(44) == "Merged" and kids.get(41) == "Backlog", f"181.6: one unreadable child changed the others: {kids}"
    line = child_line(card.render(REPO, ISSUE, found, page="issue"), 45, "181.6")
    assert "unknown" in line.lower() and not re.search(r"\b(Merged|Done)\b", bare(line)), \
        f"181.6: the unreadable child's line is “{line}”"


def test_a_child_with_no_stage_never_shows_as_done(record_property):
    """A child listed without a readable stage is drawn as unknown, never as merged or done.

    Draws the card of a split whose children's stages are missing, empty or unknown, and checks each line says
    unknown and never Merged or Done."""
    record_property("proves", "181.6")
    kids = [{"number": 41, "title": "First child"}, {"number": 42, "title": "Second child", "stage": None},
            {"number": 43, "title": "Third child", "stage": "unknown"}]
    text = draw(found_for([FEATURE, PLAN_OK, "/work", SPLIT], children=kids))
    for c in kids:
        line = child_line(text, c["number"], "181.6")
        assert "unknown" in line.lower(), f"181.6: child #{c['number']} with no stage is not shown as unknown: “{line}”"
        assert not re.search(r"\b(Merged|Done)\b", bare(line)), f"181.6: child #{c['number']} with no stage shows as done: “{line}”"

"""Raises leave the card; its status line says what needs the owner (#455).

Story 4 of #416. The owner wants the card to stop listing raises: questions, blockers and issues found stay only in
the run comment that raised them. When the river stops for questions or blockers sent to the owner, the card's status
line says so with the count, such as "Needs you: answer 2 questions", and those words link to the comment that raised
them. A plan whose questions are raises (not the retired `questions` field, #401) shows that to-do instead of "See the
newest record below", and the same raise is counted once however many records carry it (#388's card showed one
question twice). It is checked on GitHub's own rendering of the card too, not only on the raw text.

What the code these tests run must do, as the plan pins it:
- `card.render(repo, issue, found, page)` draws no Raised section, no raise's text or label and no raise icon
  (question, blocker, issue found) on the issue's or the pull request's card.
- When the river stops on a record because it raised questions or blockers for the owner (a planner's or a review's),
  the status line reads "Needs you: " and then a link whose words are exactly "answer N question(s)", "answer N
  blocker(s)" or "answer N question(s) and M blocker(s)", whose target is the address ("url") of the comment that
  holds that record, as dokima.agent.conversation lists it; the words after the link are free.
- A raise is counted once: the same raise carried by two records (the same ID, or the same kind and words) is one.
- Any other stop keeps its to-do as today, and a run that raised nothing for the owner shows no such link.

How the tests read a card: the status line is the line inside the card that opens with the stage in bold, icons
allowed in front. A link is markdown `[words](url)` or HTML `<a href="url">words</a>`.
"""
import html as htmllib
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, card  # noqa: E402

REPO = "o/r"
OWNER = "boss"
ISSUE = {"number": 455, "url": "https://github.com/o/r/issues/455"}
SRC = "https://github.com/o/r/issues/455"
STAGES = ("Backlog", "Plan", "Work", "Review", "Merged")

PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "Owners get a job id.",
        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks.", "why": "safety", "principle": "Fail closed"}],
        "scope": ["dokima/agent.py"], "out_of_scope": ["The board."],
        "tests": {"455.1": ["tests/test_a.py::test_one"]}, "test_changes": {},
        "links": {"blocked_by": [], "blocks": [], "relates_to": []}}


def raised(kind, to, by, rid, text, label=None):
    """One raise as code stamps it: who raised it and its ID."""
    r = {"kind": kind, "text": text, "evidence": "dokima/card.py", "raised_by": by, "id": rid}
    if to:
        r["to"] = to
    if label:
        r["label"] = label
    return r


Q1 = raised("question", "owner", "planner", "P1", "Should a cancelled run keep its column?", "Board column")
Q2 = raised("question", "owner", "planner", "P2", "Is twenty seconds the right timeout?", "Timeout")
Q3 = raised("question", "owner", "planner", "P6", "Should the job id expire after a day?", "Expiry")
QB = raised("blocker", "owner", "planner", "P3", "The ask contradicts the approval rule in AGENTS.md.", "Contradiction")
PI = raised("issue", None, "planner", "P4", "The wiki page on labels is out of date.", "Wiki")
WB = raised("blocker", "planner", "worker", "W5", "The test reads a file that never exists.", "Test cannot pass")
RQ = raised("question", "owner", "reviewer", "R6", "Should a failed job be retried once?", "Retry")
RB = raised("blocker", "owner", "reviewer", "R7", "Only you can grant the bot workflow permission.", "Permission")
RW = raised("blocker", "worker", "reviewer", "R8", "The job id is never returned.", "Criterion 455.1")
RI = raised("issue", None, "reviewer", "R9", "The README still names the old command.", "Docs")
EVERY = (Q1, Q2, Q3, QB, PI, WB, RQ, RB, RW, RI)


def rec(role, stage=None, passed=True, **handback):
    """One agent record, as the record step posts it."""
    return {"role": role, "stage": stage, "handback": handback, "run": "https://github.com/o/r/actions/runs/7",
            "run_id": "7", "check": {"passed": passed, "problems": [] if passed else ["the hand-back has no tests"]}}


def planner(*raises, answers=()):
    """A planner record that raised `raises`."""
    return rec("planner", **dict(PLAN, raises=list(raises), answers=list(answers)))


PLAN_OK = rec("reviewer", "plan", verdict="approve", summary="The plan holds.", asks=[], raises=[], answers=[])
BUILT = rec("worker", summary="Built the job id.", criteria={"455.1": "returns a job id"}, evidence="1 passed",
            raises=[], answers=[])


def review(*raises, verdict="block"):
    """A code review record that raised `raises`."""
    return rec("reviewer", "pr", verdict=verdict, summary="The job id is missing.", asks=[], raises=list(raises),
               answers=[])


def url(i):
    """The address of the conversation's i-th comment."""
    return f"https://github.com/o/r/issues/455#issuecomment-{4000 + i}"


def conversation(*steps):
    """The conversation as dokima.agent.conversation lists it, with each comment's address.

    A str is the owner's comment, a dict a bot record."""
    items = []
    for i, s in enumerate(steps):
        who, body = (OWNER, s) if isinstance(s, str) else \
            (agent.BOT, f"{agent.MARK}\n**Record**\n\n```json\n{json.dumps(s)}\n```\n")
        items.append({"author": {"login": who}, "body": body, "createdAt": f"2026-10-10T{i:02d}:00:00Z",
                      "where": "issue #455", "url": url(i)})
    return items


def found_for(*steps):
    """What card.render draws the card from after these steps."""
    items = conversation(*steps)
    return {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "reviews": [],
            "owners": {OWNER}, "tests": {}, "worker": None, "children": []}


def draw(found, page="issue"):
    """The card as code writes it."""
    return card.render(REPO, ISSUE, found, page=page)


STATUS = re.compile(r"(<img[^>]*>\s*)*\*\*(" + "|".join(STAGES) + r")\*\*")


def status_line(text, crit):
    """The card's status line: the line that opens with the stage in bold."""
    found = [l for l in text.splitlines() if STATUS.match(l.strip())]
    assert len(found) == 1, f"{crit}: the card must have exactly one status line, found {len(found)}:\n{text}"
    return found[0]


def links(text):
    """Every link in `text` as (words, target), markdown and HTML alike."""
    md = [(w, u) for w, u in re.findall(r"\[([^\]]+)\]\(([^)\s]+)\)", text)]
    tags = [(re.sub(r"<[^>]+>", "", w), htmllib.unescape(u))
            for u, w in re.findall(r"<a\s[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", text, re.S)]
    return md + tags


def answer_links(line):
    """The links on the status line whose words ask the owner to answer something."""
    return [(w.strip(), u) for w, u in links(line) if w.strip().lower().startswith("answer")]


def check_to_do(text, words, target, crit, case):
    """Assert the status line says Needs you, then exactly one link `words` to `target`."""
    line = status_line(text, crit)
    assert "Needs you" in line, f"{crit}: {case}: the river stops for the owner, yet the status line has no Needs you: “{line}”"
    got = answer_links(line)
    assert got == [(words, target)], (f"{crit}: {case}: the status line must link “{words}” to the comment that raised "
                                      f"them ({target}); it links {got}: “{line}”")
    assert line.index("Needs you") < line.index(words), f"{crit}: {case}: “{words}” does not follow Needs you: “{line}”"


RAISED_HEADING = re.compile(r"\*\*Raised( earlier)?:\*\*")
RAISE_ICONS = ("question", "blocker", "issue found")


# 455.1: the card lists no raises; each stays in the comment that raised it.

CARD_CASES = [
    ("after a planner raised a question and an issue", (planner(Q1, PI),), (Q1, PI)),
    ("after a planner raised a blocker for the owner", (planner(QB),), (QB,)),
    ("after a worker raised a blocker for the planner", (planner(PI), PLAN_OK, "/work", BUILT,
                                                         rec("worker", summary="Stopped.", criteria={}, evidence="",
                                                             raises=[WB], answers=[])), (PI, WB)),
    ("after a code review raised all four kinds", (planner(PI), PLAN_OK, "/work", BUILT, review(RQ, RB, RW, RI)),
     (PI, RQ, RB, RW, RI)),
]


@pytest.mark.parametrize("case, steps, shown", CARD_CASES, ids=[c[0] for c in CARD_CASES])
def test_the_card_lists_no_raise_and_each_stays_in_its_comment(record_property, case, steps, shown):
    """The card lists no raise; each still shows in the comment that raised it.

    Draws the issue's and the pull request's card after runs that raised questions, blockers and issues, for the owner,
    the planner and the worker, and checks neither card has a Raised section, any raise's words or label, or a
    question, blocker or issue icon, while the card still shows its status line and criteria. Then draws each record's
    own run comment and checks every raise it made is still there.

    Proves 455.1."""
    record_property("proves", "455.1")
    found = found_for(*steps)
    for page in ("issue", "pr"):
        text = draw(found, page)
        where = f"455.1: {case}, the {page} card"
        assert not RAISED_HEADING.search(text), f"{where} still has a Raised section:\n{text}"
        for r in shown:
            assert r["text"] not in text, f"{where} still lists the {r['kind']} “{r['text']}”:\n{text}"
            assert f"**{r['label']}:**" not in text, f"{where} still shows the label “{r['label']}”:\n{text}"
        for icon in RAISE_ICONS:
            assert card.field_icon(REPO, icon) not in text, f"{where} still draws a raise's {icon} icon:\n{text}"
        status_line(text, "455.1")
        assert "A slow call returns a job id." in text, f"{where} lost its criteria with its raises:\n{text}"
    recs = found["recs"]
    for i, r in enumerate(recs):
        comment = agent.render(r, earlier=recs[:i])
        for x in card.raises_of(r["handback"]):
            assert x["text"] in comment, f"455.1: {case}: the {r['role']}'s own comment no longer shows “{x['text']}”"


# 455.2: when the river stops for the owner's raises, the status line counts them and links to their comment.

TO_DO_CASES = [
    ("a plan with two questions for you", (planner(Q1, Q2, PI),), "answer 2 questions", 0, "Plan"),
    ("a plan with one question for you", (planner(Q1),), "answer 1 question", 0, "Plan"),
    ("a plan with one blocker for you", (planner(QB),), "answer 1 blocker", 0, "Plan"),
    ("a plan with a question and a blocker for you", (planner(Q1, QB),), "answer 1 question and 1 blocker", 0, "Plan"),
    ("a re-plan asking after you spoke", (planner(PI), "/plan use a day", planner(Q2, Q3, answers=[])),
     "answer 2 questions", 2, "Plan"),
    ("a code review with a question for you", (planner(PI), PLAN_OK, "/work", BUILT, review(RQ, RW, RI)),
     "answer 1 question", 4, "Review"),
    ("a code review with a question and a blocker for you",
     (planner(PI), PLAN_OK, "/work", BUILT, review(RQ, RB, RW)), "answer 1 question and 1 blocker", 4, "Review"),
]


@pytest.mark.parametrize("case, steps, words, at, stage", TO_DO_CASES, ids=[c[0] for c in TO_DO_CASES])
def test_the_status_line_counts_the_raises_for_you_and_links_to_their_comment(record_property, case, steps, words, at,
                                                                               stage):
    """The status line counts the raises for you and links to their comment.

    For a plan with one or two questions, a blocker, or both for the owner, a re-plan asking after the owner spoke,
    and a code review raising a question, or a question and a blocker, for the owner beside raises for others, checks
    the stage, then that the status line says Needs you followed by exactly one link, whose words count the questions
    and blockers for the owner (“answer 2 questions”, “answer 1 question and 1 blocker”) and whose target is the
    comment that raised them, on the issue's and the pull request's card alike.

    Proves 455.2."""
    record_property("proves", "455.2")
    found = found_for(*steps)
    for page in ("issue", "pr"):
        text = draw(found, page)
        line = status_line(text, "455.2")
        assert re.sub(r"<[^>]+>|\*", "", line).strip().startswith(stage), \
            f"455.2: {case}: the {page} card's status line does not start with {stage}: “{line}”"
        check_to_do(text, words, url(at), "455.2", f"{case}, on the {page} card")


OTHER_STOPS = [
    ("a plan raising only an issue goes to the reviewer", (planner(PI),), None, (planner(Q1, PI),), 0),
    ("a review blocking only the worker sends it back", (planner(PI), PLAN_OK, "/work", BUILT, review(RW, RI)), None,
     (planner(PI), PLAN_OK, "/work", BUILT, review(RW, RI, RQ)), 4),
    ("an approved plan whose question you let go waits for /work",
     (planner(Q1), "/review", PLAN_OK), card.TODO["plan approved"], (planner(Q1),), 0),
    ("a rejected plan carrying a question waits for you", (rec("planner", passed=False, **dict(PLAN, raises=[Q1])),),
     card.TODO["rejected"], (planner(Q1),), 0),
]


@pytest.mark.parametrize("case, steps, todo, beside, at", OTHER_STOPS, ids=[c[0] for c in OTHER_STOPS])
def test_only_a_stop_for_your_raises_asks_you_to_answer_them(record_property, case, steps, todo, beside, at):
    """Only a stop for raises sent to you asks you to answer them.

    Draws the card when a run raised nothing for the owner (the river goes on, so no Needs you), when the plan
    reviewer approved a plan whose question the owner let go with /review (Say /work to build the plan), and when a
    plan carrying a question was rejected (Fix the rejected hand-back), and checks none links “answer …” and each
    shows its own to-do, or none. Beside each, the same run with one question for the owner, passed and newest, does
    ask “answer 1 question”, so the check is not one that says no to everything.

    Proves 455.2."""
    record_property("proves", "455.2")
    found = found_for(*steps)
    text = draw(found)
    line = status_line(text, "455.2")
    assert not answer_links(line), f"455.2: {case}: the status line asks you to answer raises: “{line}”"
    assert card.status(ISSUE, found)[1] == todo, \
        f"455.2: {case}: the to-do is {card.status(ISSUE, found)[1]!r}, not {todo!r}: “{line}”"
    assert ("Needs you" in line) == (todo is not None), f"455.2: {case}: Needs you is wrong on “{line}”"
    check_to_do(draw(found_for(*beside)), "answer 1 question", url(at), "455.2", f"beside “{case}”, one question for you")


# 455.3: a plan whose questions are raises shows the to-do, never "See the newest record below" (#401).

@pytest.mark.parametrize("case, steps, words", [
    ("questions", (planner(Q1, Q2),), "answer 2 questions"),
    ("a blocker", (planner(QB),), "answer 1 blocker"),
], ids=["questions", "blocker"])
def test_a_plan_asking_through_raises_shows_its_to_do_not_the_newest_record(record_property, case, steps, words):
    """A plan asking through raises shows what to answer, not the newest record.

    Draws the card of a plan whose questions, or blocker, for the owner are raises rather than the retired questions
    field, and checks the to-do card.status gives and the status line both ask to answer them, with the count, and
    neither says “See the newest record below”; a plan still using the retired questions field keeps its old to-do.

    Proves 455.3."""
    record_property("proves", "455.3")
    found = found_for(*steps)
    todo = card.status(ISSUE, found)[1]
    assert todo and "See the newest record below" not in todo, \
        f"455.3: a plan with {case} for you gives the to-do {todo!r} instead of asking you to answer"
    assert words in todo, f"455.3: a plan with {case} for you gives the to-do {todo!r}, which does not say “{words}”"
    text = draw(found)
    assert "See the newest record below" not in text, f"455.3: the card of a plan with {case} says See the newest record:\n{text}"
    check_to_do(text, words, url(0), "455.3", f"a plan with {case} for you")
    old = found_for(rec("planner", **dict(PLAN, questions=[{"question": "Which one?", "assumption": "The first."}])))
    assert card.status(ISSUE, old)[1] == card.TODO["questions"], "455.3: a plan with the old questions field lost its to-do"


# 455.4: the same raise is counted once, however many records carry it.

def test_the_same_raise_is_counted_once_however_many_records_carry_it(record_property):
    """The same raise is counted once, however many records carry it.

    Draws the card when one planner record was posted twice (the same raises, the same IDs), and when a re-plan
    raised again, word for word, a question an earlier plan raised and never had answered, beside one new question;
    checks the status line counts 2 questions each time, not 4 or 3, and links to the newest comment that raised
    them. The issue card shows each question nowhere, so no question shows twice.

    Proves 455.4."""
    record_property("proves", "455.4")
    twice = planner(Q1, Q2)
    check_to_do(draw(found_for(twice, twice)), "answer 2 questions", url(1), "455.4", "a planner record posted twice")
    again = dict(Q1, id="P9")
    steps = (planner(Q1), "/plan the timeout is twenty seconds", planner(again, Q3))
    text = draw(found_for(*steps))
    check_to_do(text, "answer 2 questions", url(2), "455.4", "a re-plan raising the same question again")
    assert text.count(Q1["text"]) == 0, f"455.4: the question raised twice shows on the card:\n{text}"

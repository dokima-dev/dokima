"""Cards show what was raised and how earlier raises were answered (#299).

The owner wants every judgment an agent raised (a question, a blocker or an issue, from dokima/raises.py) drawn in one
Raised section, each line with its kind's icon and who it is for, never with an ID; a review card shows what earlier
steps raised, with the reviewer's answer, apart from what this review raises. Records posted before this change are
never redrawn, and what code detects keeps its own place.

What the code these tests run must do, as the plan pins it:
- A record's hand-back may carry "raises": stamped raises {"kind", "to", "label", "text", "evidence", "raised_by",
  "id"} (an issue has no "to"), and "answers": {"raise": ID, "answer": "done" or "disagree", "why", and, for an
  answer given for the owner on autopilot, "words" and "source": the owner's words and where they said them}.
- `agent.render(rec, pr=None, plan=None, earlier=None)`: `earlier` is the issue's records before this one, oldest
  first; an answer finds the raise it answers there by its ID. The workflow's record step,
  `python3 -m dokima.agent record ROLE STAGE OUT CHECK PASSED LOGS`, passes the records in `$PACK/in/` as `earlier`.
- `card.render(repo, issue, found)`: the issue card lists no raises since #455; they stay in the comment that raised
  them, and tests/test_card_raises_status.py pins the card.
- A rejected hand-back's raises are not drawn: its comment and the issue card stay as today, showing why it was
  rejected.

How the tests read a card:
- A section is a heading line whose bold text is exactly "Raised:" (this run's raises) or "Raised earlier:" (what
  earlier steps raised, answered here), icons allowed in front, then its list: every line after the heading up to the
  first non-empty line that is neither a list item ("- ") nor indented under one. An item is a "- " line with the
  indented lines under it.
- A raise's line opens, right after "- ", with its kind's icon: the <img> of card.field_icon for "question",
  "blocker" or "issue found". It holds the label when there is one, the text, and exactly one of: "for you", "for the
  planner", "for the worker", "filed as an issue".
- An answer's item holds "Done" or "Disagree" and the why; an answer given for the owner on autopilot also holds a
  markdown link whose text holds the owner's words and whose target is where they said them.
- The full record fold, "<details><summary>Full record</summary>...</details>", is the record itself and is not
  read as the card.
"""
import copy
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
ISSUE = {"number": 299, "url": "https://github.com/o/r/issues/299"}
SRC = "https://github.com/o/r/issues/299"
SAID = "https://github.com/o/r/issues/299#issuecomment-777"
FULL = re.compile(r"<details><summary>Full record</summary>.*?</details>", re.S)
WHO = ("for you", "for the planner", "for the worker", "filed as an issue")
ICON_OF = {"question": "question", "blocker": "blocker", "issue": "issue found"}
META = {"run_id": "7", "run": "https://github.com/o/r/actions/runs/7", "log": "https://x/log", "models": ["claude-opus-5-5"],
        "report": {"duration_ms": 120000, "turns": 9, "cost_usd": 1.5, "tokens_in": 1000, "tokens_out": 200}}

PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "Owners get a job id.",
        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks.", "why": "safety", "principle": "Fail closed"}],
        "scope": ["dokima/agent.py"], "out_of_scope": ["The board."],
        "tests": {"299.1": ["tests/test_a.py::test_one"]}, "test_changes": {},
        "links": {"blocked_by": [], "blocks": [], "relates_to": [12]}}

# Raises as code stamps them; every text, label and why is unique so a test can find its line.
P_QUESTION = {"kind": "question", "to": "owner", "label": "Board column", "text": "Should a cancelled run keep its column?",
              "evidence": "dokima/board.py", "raised_by": "planner", "id": "P17"}
P_ISSUE = {"kind": "issue", "text": "The wiki page on labels is out of date.", "raised_by": "planner", "id": "P18"}
W_BLOCKER = {"kind": "blocker", "to": "planner", "label": "Test 299.1", "text": "The test reads a file that never exists.",
             "evidence": "tests/test_a.py line 3", "raised_by": "worker", "id": "W23"}
R_TO_WORKER = {"kind": "blocker", "to": "worker", "label": "Criterion 299.1", "text": "The job id is never returned.",
               "evidence": "dokima/agent.py", "raised_by": "reviewer", "id": "R31"}
R_TO_PLANNER = {"kind": "blocker", "to": "planner", "text": "The second test proves a neighbour of the promise.",
                "raised_by": "reviewer", "id": "R32"}
R_QUESTION = {"kind": "question", "to": "owner", "label": "Timeout", "text": "Is twenty seconds the right timeout?",
              "raised_by": "reviewer", "id": "R33"}
R_ISSUE = {"kind": "issue", "label": "Docs", "text": "The README still names the old command.", "raised_by": "reviewer",
           "id": "R34"}
A_FOR_OWNER = {"raise": "P17", "answer": "done", "why": "Your words settle it: the column stays.",
               "words": "a cancelled run stays in its column", "source": SAID}
A_DISAGREE = {"raise": "W23", "answer": "disagree", "why": "The file is made by the test itself in a temp folder."}
IDS = ("P17", "P18", "W23", "R31", "R32", "R33", "R34")


def rec(role, stage=None, passed=True, problems=(), **handback):
    """One record as the record step builds it."""
    return {"role": role, "stage": stage, **META, "handback": handback,
            "check": {"passed": passed, "problems": list(problems) if not passed else []}}


# Records posted before this change: the old fields, no raises or answers.
OLD_PLANNER = rec("planner", **dict(PLAN, questions=[{"question": "Should it retry?", "assumption": "It does not."}],
                                    concerns=[{"text": "This overlaps #12.", "evidence": "dokima/board.py"}]))
OLD_REVIEW = rec("reviewer", "plan", verdict="block", summary="One criterion has no proof.",
                 blockers=[{"id": "B1", "criterion": "299.1", "fixer": "planner", "problem": "The test reads nothing.",
                            "evidence": "tests/test_a.py", "fix": "Read the job id."}],
                 notes=[{"text": "The docstring is long.", "evidence": "tests/test_a.py"}],
                 outside_plan=[{"file": "README.md", "change": "a new line"}],
                 issues_found=[{"title": "Docs are stale", "why": "The README names an old command."}],
                 assumptions=[{"question": "Should it retry?", "accepted": False, "changes": True, "why": "It costs more."}],
                 resolved=[{"blocker": "B0", "status": "fixed"}], asks=[],
                 previous_step={"did": ["planned"], "decided": [], "open": ["the timeout"]})
OLD_WORKER = rec("worker", summary="Built the job id.", criteria={"299.1": "returns a job id"}, evidence="3 passed",
                 suspect_tests=[{"test": "tests/test_a.py::test_one", "evidence": "it reads nothing"}],
                 replies=[{"blocker": "B1", "answer": "fixed", "why": "now it reads"}],
                 outside_scope=[{"file": "README.md", "why": "a typo"}])

# Records after this change.
NEW_PLANNER = rec("planner", **dict(PLAN, raises=[P_QUESTION, P_ISSUE], answers=[]))
NEW_WORKER = rec("worker", summary="Built the job id.", criteria={"299.1": "returns a job id"}, evidence="3 passed",
                 raises=[W_BLOCKER], answers=[])
NEW_REVIEW = rec("reviewer", "pr", verdict="block", summary="The job id is missing.", asks=[],
                 raises=[R_TO_WORKER, R_TO_PLANNER, R_QUESTION, R_ISSUE], answers=[A_FOR_OWNER, A_DISAGREE])


@pytest.fixture
def env(monkeypatch):
    """The repo the icons are served from, as the workflow sets it."""
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")


def img(field):
    """The <img> tag of a field's icon, as the card draws it."""
    return card.field_icon(REPO, field)


def shown(text):
    """The comment as the owner reads it: everything but the full record fold."""
    return FULL.sub("", text)


def headings(text, title):
    """The indexes of every heading line whose bold text is exactly `title`."""
    pat = re.compile(r"\s*(<img[^>]*>\s*)*\*\*" + re.escape(title) + r"\*\*\s*")
    return [i for i, l in enumerate(text.splitlines()) if pat.fullmatch(l)]


def section(text, title):
    """The items under the heading `title`, each as its lines; None without that heading."""
    lines, at = text.splitlines(), headings(text, title)
    if not at:
        return None
    items = []
    for l in lines[at[0] + 1:]:
        if l.startswith("- "):
            items.append([l])
        elif l[:1].isspace() and l.strip() and items:
            items[-1].append(l)
        elif l.strip():
            break
    return items


def item_with(items, needle):
    """The one item holding `needle`, as one string."""
    found = ["\n".join(i) for i in items if needle in "\n".join(i)]
    assert len(found) == 1, f"expected exactly one line holding {needle!r}, found {len(found)}:\n" + \
        "\n".join("\n".join(i) for i in items)
    return found[0]


def who_of(raise_):
    """Who the line of a raise must say it is for."""
    if raise_["kind"] == "issue":
        return "filed as an issue"
    return "for you" if raise_["to"] == "owner" else f"for the {raise_['to']}"


def check_raise_line(item, raise_, crit, where):
    """Assert an item shows a raise: icon first, label, text and who it is for.

    Under Raised earlier the item first says who raised it and where (#478), e.g. "Code review on [#462](...)
    raised: ", and the raise follows."""
    first = item.splitlines()[0]
    if where == "Raised earlier":
        first = re.sub(r"^- (Planner|Worker|Plan review|Code review)( on \[#\d+\]\([^)\s]+\))? raised: ", "- ", first)
    assert first.startswith("- " + img(ICON_OF[raise_["kind"]])), \
        f"{crit}: in {where}, the {raise_['kind']} line does not open with the {raise_['kind']} icon:\n{first}"
    if raise_.get("label"):
        assert raise_["label"] in item, f"{crit}: in {where}, the line does not show its label {raise_['label']!r}:\n{item}"
    else:
        assert "None" not in item, f"{crit}: in {where}, a raise with no label shows None:\n{item}"
    said = [w for w in WHO if w in item]
    assert said == [who_of(raise_)], \
        f"{crit}: in {where}, the {raise_['kind']} raised to {raise_.get('to')} must say {who_of(raise_)!r}, said {said}:\n{item}"


def draw(record, earlier=None):
    """The run comment of `record` given earlier records; a plain failure while render takes none."""
    try:
        return agent.render(record, earlier=earlier)
    except TypeError as e:
        if "earlier" in str(e):
            pytest.fail("render() takes no earlier records yet, so a review cannot show what it answered")
        raise


def found_for(recs):
    """What card.render draws the issue card from, for a card with records only."""
    return {"recs": recs, "pr": None, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": {}, "worker": None}


def record_step(tmp_path, role, stage, handback, earlier):
    """Run the workflow's record step with `earlier` records in $PACK/in; return the comment it wrote."""
    out, pack, logs = tmp_path / "out", tmp_path / "pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    for i, r in enumerate(earlier, 1):
        (pack / "in" / f"{i:02d}-{r['role']}{'-' + r['stage'] if r.get('stage') else ''}.json").write_text(json.dumps(r))
    (pack / "plan.json").write_text(json.dumps(PLAN))
    (out / {"planner": "plan.json", "worker": "work.json", "reviewer": "review.json"}[role]).write_text(json.dumps(handback))
    (out / "check.txt").write_text("")
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": REPO,
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "STAGE": stage}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "record", role, stage, str(out), str(out / "check.txt"),
                        "true", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and (out / "comment.md").exists(), \
        f"the record step failed (exit {r.returncode}):\n{r.stderr[-800:]}"
    return (out / "comment.md").read_text()


# 299.1: one Raised section, each line with its kind's icon, its label and who it is for.

@pytest.mark.parametrize("record, raises, who", [
    (NEW_PLANNER, [P_QUESTION, P_ISSUE], "the planner's comment"),
    (NEW_WORKER, [W_BLOCKER], "the worker's comment"),
    (NEW_REVIEW, [R_TO_WORKER, R_TO_PLANNER, R_QUESTION, R_ISSUE], "the review's comment"),
])
def test_a_run_comment_shows_every_raise_in_one_raised_section(record_property, env, record, raises, who):
    """A run's comment lists every raise in one Raised section, with icon, label and recipient.

    Draws the comments of a planner, a worker and a reviewer that raised questions, blockers and issues to the owner,
    the planner and the worker, and checks there is exactly one Raised section, outside every fold, with one line per
    raise: its kind's icon first, its label when it has one, its text, and for you, for the planner, for the worker or
    filed as an issue, matching who it was raised to.

    Proves 299.1."""
    record_property("proves", "299.1")
    body = shown(draw(record, earlier=[NEW_PLANNER, NEW_WORKER]))
    assert len(headings(body, "Raised:")) == 1, f"299.1: {who} must have exactly one Raised section:\n{body}"
    visible = body.split("<details", 1)[0]
    items = section(visible, "Raised:")
    assert items is not None, f"299.1: {who} shows its Raised section inside a fold, where the owner must open it:\n{body}"
    assert len(items) == len(raises), \
        f"299.1: {who} raised {len(raises)} things but its Raised section has {len(items)} lines:\n{body}"
    for r in raises:
        check_raise_line(item_with(items, r["text"]), r, "299.1", who)


def test_a_run_that_raised_nothing_shows_no_raised_section(record_property, env):
    """A run that raised nothing shows no Raised section.

    Draws the comments of a planner, a worker and a reviewer whose raises are empty, and checks none shows a Raised
    heading; then checks the same planner with one raise does show it, so the check is not passing on nothing.

    Proves 299.1."""
    record_property("proves", "299.1")
    for r in (NEW_PLANNER, NEW_WORKER, NEW_REVIEW):
        quiet = copy.deepcopy(r)
        quiet["handback"]["raises"] = []
        quiet["handback"]["answers"] = []
        body = agent.render(quiet)
        assert not headings(body, "Raised:"), f"299.1: a {r['role']} run that raised nothing shows a Raised section:\n{body}"
    assert headings(agent.render(NEW_PLANNER), "Raised:"), "299.1: a planner run with raises shows no Raised section"


def answering(answers, passed=True):
    """A review record that raised nothing and answers the given earlier raises."""
    return rec("reviewer", "plan", passed=passed, problems=["the hand-back has no verdict"], verdict="block",
               summary="Answered.", asks=[], raises=[], answers=answers)


# 299.2: no ID on any card.

def test_no_card_shows_a_raise_or_answer_id(record_property, env):
    """No card shows a raise's or an answer's ID.

    Draws the comments of runs that raised and answered things, a review's comment through the record step, and the
    issue card, and checks none of the IDs P17, P18, W23 and R31 to R34 appears anywhere the owner reads, folds
    included; only the full record keeps them.

    Proves 299.2."""
    record_property("proves", "299.2")
    drawn = {"the planner's comment": agent.render(NEW_PLANNER),
             "the worker's comment": draw(NEW_WORKER, earlier=[NEW_PLANNER]),
             "the review's comment": draw(NEW_REVIEW, earlier=[NEW_PLANNER, NEW_WORKER]),
             "the issue card": card.render(REPO, ISSUE, found_for([NEW_PLANNER, NEW_WORKER, NEW_REVIEW])),
             "the planner's issue card": card.render(REPO, ISSUE, found_for([NEW_PLANNER]))}
    for where, text in drawn.items():
        seen = [i for i in IDS if re.search(r"\b" + i + r"\b", shown(text))]
        assert not seen, f"299.2: {where} shows the IDs {seen}:\n{shown(text)}"
    assert "R31" in agent.render(NEW_REVIEW), "299.2: the full record no longer keeps the IDs the next pack reads"


# 299.3: a review card shows what earlier steps raised, with the reviewer's answer, apart from this review's raises.

def test_a_review_card_shows_earlier_raises_with_its_answers_apart_from_its_own(record_property, env):
    """A review card shows earlier raises with its answers, apart from its own raises.

    Draws a review that answered the planner's question for the owner (done) and the worker's blocker for the planner
    (disagree), and raised four things of its own; checks a Raised earlier section holds exactly the two earlier
    raises, each with its icon, who it was for, its answer and why, and the Raised section holds only the review's
    own four.

    Proves 299.3."""
    record_property("proves", "299.3")
    body = shown(draw(NEW_REVIEW, earlier=[OLD_PLANNER, NEW_PLANNER, NEW_WORKER]))
    earlier = section(body, "Raised earlier:")
    assert earlier is not None, f"299.3: the review's comment has no Raised earlier section:\n{body}"
    assert len(headings(body, "Raised earlier:")) == 1, f"299.3: the review shows Raised earlier more than once:\n{body}"
    assert len(earlier) == 2, f"299.3: the review answered 2 earlier raises but Raised earlier has {len(earlier)}:\n{body}"
    for r, a, word, not_word in ((P_QUESTION, A_FOR_OWNER, "Done", "Disagree"), (W_BLOCKER, A_DISAGREE, "Disagree", "Done")):
        item = item_with(earlier, r["text"])
        check_raise_line(item, r, "299.3", "Raised earlier")
        assert word in item and not_word not in item, \
            f"299.3: the earlier raise {r['text']!r} must show the answer {word}, and only it:\n{item}"
        assert a["why"] in item, f"299.3: the earlier raise {r['text']!r} does not show why: {a['why']!r}:\n{item}"
    own = section(body, "Raised:")
    assert own is not None and len(own) == 4, f"299.3: the review's own Raised section must hold its 4 raises:\n{body}"
    for r in (P_QUESTION, W_BLOCKER):
        assert not any(r["text"] in "\n".join(i) for i in own), \
            f"299.3: the earlier raise {r['text']!r} is mixed into the review's own Raised section:\n{body}"


def test_an_answer_given_for_you_on_autopilot_quotes_your_words_and_links_them(record_property, env):
    """An answer given for you on autopilot quotes your words, linked where said.

    Draws a review that answered the planner's question for the owner with the owner's words and the comment they
    said them in, and checks that answer's line holds a link whose text holds those words and whose target is that
    comment; the answer that carries no words of the owner shows no such link.

    Proves 299.3."""
    record_property("proves", "299.3")
    earlier = section(shown(draw(NEW_REVIEW, earlier=[NEW_PLANNER, NEW_WORKER])), "Raised earlier:")
    assert earlier is not None, "299.3: the review's comment has no Raised earlier section"
    # Since #359 the words are quoted as plain text and the comment follows as a bare link GitHub draws as a reference.
    linked = re.compile(r"^(?!.*\]\()(?!.*<a ).*\"" + re.escape(A_FOR_OWNER["words"]) + r"\".*?(?<![\w/\"=\[<])"
                        + re.escape(SAID) + r"(?![\w/#-])", re.M)
    item = item_with(earlier, P_QUESTION["text"])
    assert linked.search(item), (f"299.3: the answer given for you does not quote your words "
                                 f"{A_FOR_OWNER['words']!r} followed by where you said them, {SAID}:\n{item}")
    other = item_with(earlier, W_BLOCKER["text"])
    assert SAID not in other, f"299.3: an answer with no words of yours links your comment:\n{other}"


def test_a_review_that_answered_nothing_shows_no_section_for_earlier_raises(record_property, env):
    """A review that answered nothing shows no section for earlier raises.

    Draws the same review with no answers and checks no Raised earlier heading shows, while its own Raised section
    still does.

    Proves 299.3."""
    record_property("proves", "299.3")
    quiet = copy.deepcopy(NEW_REVIEW)
    quiet["handback"]["answers"] = []
    body = draw(quiet, earlier=[NEW_PLANNER, NEW_WORKER])
    assert not headings(body, "Raised earlier:"), f"299.3: a review that answered nothing shows Raised earlier:\n{body}"
    assert headings(body, "Raised:"), f"299.3: the review's own raises vanished with its answers:\n{body}"


def test_the_record_step_draws_earlier_raises_from_the_pack(record_property, tmp_path):
    """The review comment the workflow posts finds each earlier raise in the issue's earlier records.

    Runs the workflow's record step for a code review whose hand-back answers two raises by ID, with the planner's
    and worker's records in the starting pack, and checks the comment's Raised earlier section shows both raises'
    words with their answers, and neither ID.

    Proves 299.3."""
    record_property("proves", "299.3")
    handback = dict(NEW_REVIEW["handback"], raises=[])
    body = shown(record_step(tmp_path, "reviewer", "pr", handback, [OLD_PLANNER, NEW_PLANNER, NEW_WORKER]))
    earlier = section(body, "Raised earlier:")
    assert earlier is not None and len(earlier) == 2, \
        f"299.3: the posted review does not show the 2 raises it answered, found in the pack:\n{body}"
    for r, a in ((P_QUESTION, A_FOR_OWNER), (W_BLOCKER, A_DISAGREE)):
        item = item_with(earlier, r["text"])
        assert a["why"] in item, f"299.3: the posted review does not show why for {r['text']!r}:\n{item}"
        assert not re.search(r"\b" + r["id"] + r"\b", item), f"299.3: the posted review shows the ID {r['id']}:\n{item}"


# 299.4: records posted before this change keep their comment; the issue card still draws them.

REJECTED = rec("planner", passed=False, problems=["the hand-back has no tests for 299.1", "the merge clashed on main"],
               **dict(PLAN, raises=[P_QUESTION]))
CLASH = {"role": "updater", "stage": None, "run": "https://github.com/o/r/actions/runs/8",
         "handback": {"pr": 5, "base": "main", "merge": "abcdef123456", "merged_pr": 4, "files": ["dokima/agent.py"]},
         "check": {"passed": True, "problems": []}}
NOT_STARTED = agent.not_started("worker", "", "main is red: all tests failed on abc1234", META)
MERGE_FAILED = agent.not_started("worker", "pr", "Merging main into try/issue-299 failed with no clashed file to resolve.", META)
CANCELLED = agent.cancelled("reviewer", "pr", True, META)
TODO_TODAY = {"questions": "Answer the questions with /plan, or say /review",
              "plan approved": "Say /work to build the plan",
              "three blocks": "Three blocks in a row: your call",
              "rejected": "Fix the rejected hand-back",
              "not started": "Fix why nothing ran",
              "escalated": "Settle the escalation",
              "ready": "Ready for approval",
              "not every check passed": "See why not every check passed"}
OUTSIDE_PLAN = [{"file": "README.md", "change": "a new line"}]
OUTSIDE_SCOPE = [{"file": "setup.cfg", "why": "a typo"}]
# A plan approved, built and passed by its code review, whose checks failed on the pull request.
APPROVED = rec("reviewer", "plan", verdict="approve", summary="The plan holds.", blockers=[], asks=[])
BUILT = rec("worker", summary="Built.", criteria={"299.1": "returns a job id"}, evidence="1 passed")
PASSED_REVIEW = rec("reviewer", "pr", verdict="approve", summary="The work holds.", blockers=[], asks=[])
FAILING_RUNS = [{"name": "299.1 · A slow call returns a job id", "status": "completed", "conclusion": "failure",
                 "html_url": "https://x/check/1"},
                {"name": "299.2 · Nothing leaks", "status": "completed", "conclusion": "success",
                 "html_url": "https://x/check/2"},
                {"name": card.ALL_TESTS, "status": "completed", "conclusion": "failure", "html_url": "https://x/check/3"}]


def failing_found(review):
    """The issue card's input for a pull request whose checks failed after `review`."""
    found = found_for([rec("planner", **PLAN), APPROVED, BUILT, review])
    found["check_runs"], found["pr"] = FAILING_RUNS, {"number": 5, "merged": False}
    return found


@pytest.mark.parametrize("record, title, line, raises", [
    (NEW_REVIEW, "<img> Outside the plan", "- README.md: a new line", [R_TO_WORKER, R_TO_PLANNER, R_QUESTION, R_ISSUE]),
    (NEW_WORKER, "What it found", "- <img> Outside the plan: setup.cfg: a typo", [W_BLOCKER]),
])
def test_work_outside_the_plan_keeps_its_fold_beside_raised(record_property, env, record, title, line, raises):
    """Work outside the plan keeps its own fold and icon, and stays out of Raised.

    Draws a review that found a file changed outside the plan and a worker that changed one outside its scope, each
    also carrying raises, and checks the Outside the plan fold is drawn exactly as today's code draws it, with the
    outside the plan icon, while the Raised section holds exactly the run's raises and never names that file.

    Proves 299.5."""
    record_property("proves", "299.5")
    r = copy.deepcopy(record)
    r["handback"]["outside_plan" if r["role"] == "reviewer" else "outside_scope"] = \
        OUTSIDE_PLAN if r["role"] == "reviewer" else OUTSIDE_SCOPE
    body = shown(draw(r, earlier=[NEW_PLANNER, NEW_WORKER]))
    mark = img("outside the plan")
    fold = "\n".join(card.fold(title.replace("<img>", mark), [line.replace("<img>", mark)]))
    assert fold in body, f"299.5: the {r['role']}'s Outside the plan fold is no longer drawn as today:\n{fold}\n--- in ---\n{body}"
    items = section(body, "Raised:")
    assert items is not None and len(items) == len(raises), \
        f"299.5: the {r['role']}'s Raised section must hold exactly its {len(raises)} raises:\n{body}"
    text = "\n".join("\n".join(i) for i in items)
    for f in ("README.md", "setup.cfg", "Outside the plan"):
        assert f not in text, f"299.5: work outside the plan ({f}) is listed in the Raised section:\n{text}"


def test_failing_tests_keep_their_marks_and_to_do_beside_raised(record_property, env):
    """Failing tests keep their red marks and to-do, and stay out of Raised.

    Draws the issue card of a pull request whose code review passed but whose criterion check and All tests failed,
    and checks it shows the failed marks and Needs you:
    See why not every check passed. Then draws it again with the review raising one issue, and checks the card
    shows no Raised section and not that issue (#455), while the failed marks and the to-do stay as they were.

    Proves 299.5."""
    record_property("proves", "299.5")
    drawn = card.render(REPO, ISSUE, failing_found(PASSED_REVIEW))
    raised = card.render(REPO, ISSUE, failing_found(rec("reviewer", "pr", verdict="approve", summary="The work holds.",
                                                        blockers=[], asks=[], raises=[R_ISSUE], answers=[])))
    assert not headings(raised, "Raised:") and R_ISSUE["text"] not in raised, \
        f"299.5: the issue card lists the review's raise beside the failing tests:\n{raised}"
    for kept in ("Needs you: See why not every check passed", '<a href="https://x/check/1">', '<a href="https://x/check/3">'):
        assert drawn.count(kept) == raised.count(kept) == 1, \
            f"299.5: {kept!r} no longer shows once beside the Raised section:\n{raised}"
    failed = card.icon(REPO, card.ICON_FILE["failed"], alt="failed")
    assert raised.count(failed) == drawn.count(failed), f"299.5: the failed marks changed beside Raised:\n{raised}"


def test_what_code_detects_never_enters_the_raised_section(record_property, env, monkeypatch):
    """Rejected hand-backs, workflow file changes and three blocks in a row read as today.

    Checks the issue card of a rejected hand-back carrying a raise, after a planner that raised nothing, is byte for
    byte today's, with its to-do and no Raised section;
    that autopilot refuses to merge a pull request that changes a workflow file with today's words, so the owner
    merges it; and every to-do the card can show, three blocks in a row among them, still reads as today.

    Proves 299.5."""
    record_property("proves", "299.5")
    drawn = card.render(REPO, ISSUE, found_for([rec("planner", **PLAN), REJECTED]))
    assert not headings(drawn, "Raised:"), f"299.5: a rejected hand-back's raise is drawn in Raised:\n{drawn}"
    calls = []

    def fake_gh(*args):
        calls.append(args)
        if "pulls/5/files" in " ".join(args):
            return json.dumps([{"filename": "dokima/agent.py"}, {"filename": ".github/workflows/ci.yml"}])
        raise AssertionError(f"299.5: autopilot went on past a workflow file change: gh {args}")
    monkeypatch.setattr(agent, "gh", fake_gh)
    assert agent.try_merge(REPO, 5) == (False, "it changes a workflow file (.github/workflows/ci.yml), and only the owner "
                                               "merges those"), "299.5: a workflow file change that needs you reads differently"
    assert card.TODO == TODO_TODAY, f"299.5: the owner's to-dos for what code detects changed: {card.TODO}"

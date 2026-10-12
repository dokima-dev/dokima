"""Plans carry no out of scope list: the criteria already bound the work.

Issue #527, story 2 of #524. The owner asked to "drop "out of scope" field since with our strict requirements for
meeting acceptance criteria and delivering only what is asked they become unnecessary". So the planner's prompt no
longer asks for the field, and no card, prompt, word cap or check mentions it. Older records still hold the field, so
the card tests draw from such a record and check it is not shown. The fence's file scope is untouched and keeps its own
tests (tests/test_fence.py).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card, planner, words  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
ROLES = os.path.join(ROOT, "dokima", "roles")
REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
SRC = ISSUE["url"]
MENTION = re.compile(r"out[ _-]of[ _-]scope|non[ _-]goals", re.I)
OLD_LINE = "The board stays exactly as it is today."
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "Slow calls return a job id.",
         "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": SRC}],
         "non_functional": [], "scope": ["dokima/jobs.py"], "tests": {"40.1": ["tests/test_jobs.py::test_id"]}}


def planner_prompt():
    """The planner's whole prompt, as agent.yml joins it: style.md, plan-grade.md, then planner.md."""
    return "\n".join(open(os.path.join(ROLES, f)).read() for f in ("style.md", "plan-grade.md", "planner.md"))


def old_record():
    """A planner record posted before #527, still holding an out of scope list."""
    return {"role": "planner", "stage": None, "handback": dict(STORY, out_of_scope=[OLD_LINE]),
            "check": {"passed": True, "problems": []}, "run": "https://github.com/o/r/actions/runs/1"}


def cards(rec):
    """The issue card and the PR description drawn from one planner record."""
    found = {"recs": [rec], "pr": None, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": {},
             "worker": None}
    issue_card = card.render(REPO, ISSUE, found, page="issue")
    drawn = card.render(REPO, ISSUE, dict(found, pr={"number": 5, "merged": False, "state": "open"}), page="pr")
    return {"issue card": issue_card, "PR card": card.pr_body(drawn, "Closes #40", "My ask.", issue_url=SRC)}


def test_the_planner_hands_back_no_out_of_scope_field(record_property):
    """The planner is never asked for an out of scope list; a plan keeps none.

    Proves 527.1. Reads the planner's whole prompt and checks its plan.json shape names no out_of_scope field; then
    reads a hand-back with no such field and checks the plan code keeps no out of scope part (today it adds an empty
    one)."""
    record_property("proves", "527.1")
    prompt = planner_prompt()
    assert '"out_of_scope"' not in prompt, \
        "527.1: the planner's prompt still asks for an out_of_scope field in plan.json"
    kind, plan = planner.from_kind(json.loads(json.dumps(STORY)))
    assert kind == "plan", f"527.1: a plan with no out of scope field was not read as a plan: {kind}"
    left = sorted(k for k in plan if MENTION.search(k))
    assert not left, f"527.1: the plan read from a hand-back with no out of scope still holds {left}"


def test_no_card_prompt_word_cap_or_check_mentions_out_of_scope(record_property):
    """No card, prompt, word cap or check mentions out of scope.

    Proves 527.2. Draws the issue and PR cards and a record's folds from an older plan that still holds an out of
    scope line and checks neither the heading nor the line shows; checks no prompt names it; holds a 40-word out of
    scope line to the word caps and checks nothing is flagged; hands the check a malformed out of scope field and
    checks it is not named; and checks no file of Dokima's code or prompts mentions out of scope at all."""
    record_property("proves", "527.2")
    for where, text in cards(old_record()).items():
        assert not MENTION.search(text), f"527.2: the {where} still shows Out of scope:\n{text}"
        assert OLD_LINE not in text, f"527.2: the {where} still shows an out of scope line: {OLD_LINE!r}"
    folds = "\n".join(agent.details_as_posted(old_record()))
    assert not MENTION.search(folds), f"527.2: a record's folds still show Out of scope:\n{folds}"
    for name in sorted(os.listdir(ROLES)):
        found = MENTION.findall(open(os.path.join(ROLES, name)).read())
        assert not found, f"527.2: the prompt {name} still mentions out of scope: {found}"
    assert not any(MENTION.search(k) for k in list(words.CAPS) + list(words.PLAIN)), \
        "527.2: the word caps still hold an out of scope field"
    listed, rejected = words.style({"out_of_scope": [" ".join(["word"] * 40)]})
    assert not listed and not rejected, f"527.2: the word cap check still judges out of scope: {listed + rejected}"
    try:
        planner.from_kind(dict(STORY, out_of_scope="No retries."))
    except planner.Garbled as e:
        assert not MENTION.search(str(e)), f"527.2: the plan check still names out of scope: {e}"
    left = []
    for top, _, files in os.walk(os.path.join(ROOT, "dokima")):
        for f in files:
            if f.endswith((".py", ".md")):
                path = os.path.join(top, f)
                left += [f"{os.path.relpath(path, ROOT)}:{n}" for n, line in enumerate(open(path), 1)
                         if MENTION.search(line)]
    assert not left, f"527.2: Dokima's code or prompts still mention out of scope at {left}"

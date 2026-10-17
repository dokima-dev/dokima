"""Tests for #818: the reviewer's prompt spells out its duties and boxes.

The owner wrote the duties in the comment of 2026-10-15 on #741 and the boxes in the comment after it. Each test
builds the reviewer's prompt the way agent.yml builds it, `python3 -m dokima.prompt reviewer GRADE`, at both moments
the reviewer works: with the plan grade and with the result grade. A duty must be said in one sentence of the built
prompt; the boxes must be shown as the owner shaped them. Code that checks the boxes is #819, not this issue.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRADES = ("plan-grade", "result-grade")


def built(tmp, grade):
    """The reviewer's prompt agent.yml builds with GRADE, with no settings file.

    Runs `python3 -m dokima.prompt reviewer GRADE` in a temp folder, Dokima's code first on the path; fails the test,
    with the error, when the prompt is not built."""
    folder = os.path.join(str(tmp), grade)
    os.makedirs(folder, exist_ok=True)
    env = dict(os.environ, PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, "-m", "dokima.prompt", "reviewer", grade], cwd=folder, env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.strip(), \
        f"the reviewer's prompt ({grade}) was not built: exit {r.returncode}\n{r.stderr}"
    return r.stdout


def flat(text):
    """TEXT on one line, spaces squeezed and curly quotes made straight."""
    return " ".join(text.replace("’", "'").replace("“", '"').replace("”", '"').split())


def sentences(text):
    """TEXT's sentences and list items, each on one line."""
    parts = []
    for block in re.split(r"\n\s*(?:- |\d+\. |\n)", text):
        parts += re.split(r"(?<=[.!?])\s+", flat(block))
    return [p for p in parts if p]


def said(tmp, patterns):
    """For each grade, whether one sentence of the reviewer's prompt matches every regex in PATTERNS."""
    return {grade: any(all(re.search(p, s, re.I) for p in patterns) for s in sentences(built(tmp, grade)))
            for grade in GRADES}


def missing_from(found):
    """The grades whose prompt lacks the sentence, as a readable list."""
    return [f"the reviewer's prompt ({grade})" for grade, ok in found.items() if not ok]


# 818.1 ------------------------------------------------------------------------------------------------------------

def test_the_reviewers_prompt_says_every_owner_sentence_maps_or_is_not_a_requirement(record_property, tmp_path):
    """The reviewer's prompt says owner sentences map to a criterion or are not requirements.

    Proves 818.1. Builds the reviewer's prompt for plan review and for code review and looks, in each, for one
    sentence that names the owner's sentences, a criterion, "not a requirement" and a reason."""
    record_property("proves", "818.1")
    gone = missing_from(said(tmp_path, [r"\bowner", r"\bsentences?\b", r"\bcriteri(on|a)\b", r"not a requirement",
                                        r"\breason\b"]))
    assert not gone, ("818.1: no sentence says every owner sentence maps to a criterion or is marked not a "
                      "requirement with a reason, in: " + ", ".join(gone))


# 818.2 ------------------------------------------------------------------------------------------------------------

def test_the_reviewers_prompt_says_later_owner_words_win(record_property, tmp_path):
    """The reviewer's prompt says the owner's later words win over older ones.

    Proves 818.2. Builds the reviewer's prompt for plan review and for code review and looks, in each, for one
    sentence that names the owner's words, says later (or newer) ones win, and names older ones."""
    record_property("proves", "818.2")
    gone = missing_from(said(tmp_path, [r"\bowner", r"\bwords?\b", r"\b(later|newer)\b", r"\bwins?\b", r"\bolder\b"]))
    assert not gone, "818.2: no sentence says later owner words win over older ones, in: " + ", ".join(gone)


# 818.3 ------------------------------------------------------------------------------------------------------------

def test_the_reviewers_prompt_says_it_confirms_or_retires_a_stale_criterion(record_property, tmp_path):
    """The reviewer's prompt says it confirms or retires a criterion code flags as stale.

    Proves 818.3. Builds the reviewer's prompt for plan review and for code review and looks, in each, for one
    sentence that names a criterion code flags as stale, and both confirming it and retiring it."""
    record_property("proves", "818.3")
    gone = missing_from(said(tmp_path, [r"\bcriteri(on|a)\b", r"\bstale\b", r"\bflag", r"\bcode\b", r"\bconfirm",
                                        r"\bretir"]))
    assert not gone, ("818.3: no sentence says the reviewer confirms or retires a criterion code flags as stale, in: "
                      + ", ".join(gone))


# 818.4 ------------------------------------------------------------------------------------------------------------

def test_the_reviewers_prompt_says_it_asks_the_owner_and_never_picks(record_property, tmp_path):
    """The reviewer's prompt says unsettled owner disagreements go to the owner; it never picks.

    Proves 818.4. Builds the reviewer's prompt for plan review and for code review and looks, in each, for one
    sentence that names owner sources that disagree, no later word settling it, asking the owner, and never picking."""
    record_property("proves", "818.4")
    gone = missing_from(said(tmp_path, [r"\bsources?\b", r"\bdisagree", r"\bsettle", r"\bask", r"\bowner\b",
                                        r"\bnever picks?\b"]))
    assert not gone, ("818.4: no sentence says that when two owner sources disagree unsettled, the reviewer asks the "
                      "owner and never picks, in: " + ", ".join(gone))


# 818.5 ------------------------------------------------------------------------------------------------------------

def test_the_reviewers_prompt_says_a_change_serving_no_criterion_blocks(record_property, tmp_path):
    """The reviewer's prompt says any change that serves no criterion blocks.

    Proves 818.5. Builds the reviewer's prompt for plan review and for code review and looks, in each, for one
    sentence that names a change, says it serves no criterion, and says it blocks."""
    record_property("proves", "818.5")
    gone = missing_from(said(tmp_path, [r"\bchanges?\b", r"\bserves? no criterion\b", r"\bblock"]))
    assert not gone, "818.5: no sentence says any change serving no criterion blocks, in: " + ", ".join(gone)


# 818.6 ------------------------------------------------------------------------------------------------------------

BOXES = [
    'dropped: none | [{words: "...", source: comment:N}]',
    'added: none | [{what: "...", kind: creep | needed, serves: criterion id}] # needed is not a blocker',
    'superseded: none | [{old: "...", new: comment:N, retired: criterion id}]',
    'conflicts: none | [{a: "...", b: "...", ask: "question for the owner"}]',
    'edges: per criterion: covered | missing: <named case>',
    'poor_tests: none | [{test: file::name, passes_with: "<the wrong code that still passes>", fix: "..."}]',
]


def test_the_reviewers_prompt_shows_the_six_required_boxes_and_their_shapes(record_property, tmp_path):
    """The reviewer's prompt shows the six required boxes with the owner's entry shapes.

    Proves 818.6. Builds the reviewer's prompt for plan review and for code review and checks each holds, on a line
    of its own, every one of the owner's six box lines (dropped, added, superseded, conflicts, edges, poor_tests) as
    the owner wrote them, spacing aside. Each failure names the prompt and the boxes it lacks."""
    record_property("proves", "818.6")
    gone = {}
    for grade in GRADES:
        lines = {flat(line) for line in built(tmp_path, grade).splitlines()}
        lacks = [box.split(":")[0] for box in BOXES if box not in lines]
        if lacks:
            gone[grade] = lacks
    assert not gone, "818.6: the reviewer's prompt does not show every required box with its shape:\n" + \
        "\n".join(f"  the reviewer's prompt ({grade}) lacks: {', '.join(lacks)}" for grade, lacks in gone.items())

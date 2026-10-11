"""The planner check caps criteria and docstrings; a little over never fails a run.

Issue #239 (story 1 of #229). The owner set the caps: 25 words for a criterion's first sentence, 15 words for the
first line of every docstring the planner adds in its tests. A text up to 20% over its cap (30 words for 25, 18 for 15)
passes, and the check lists it; a text past that is rejected, naming it and its word count. Every new test's docstring
names the criteria it proves by number, below its first line.

Every test here runs `python3 -m dokima.planner check 9 OUT` through planner.main, in the temp git repo of the `check`
fixture of tests/test_plan_check.py (issue #9, one older test at the start, the planner's tests on top). Each test
rewrites the planner's tests/test_jobs.py and plan.json there, runs the check, and reads back the exit code, the reason
saved for the issue, and what the check printed.
"""
import copy
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.test_plan_check import FEATURE, STORY, check  # noqa: E402,F401


def words(n, end="."):
    """A sentence of exactly n words, ending in the given mark."""
    return " ".join(f"w{i}" for i in range(1, n + 1)) + end


ID_DOC = "A slow call returns a job id."
UNIQUE_DOC = "Job ids never repeat."


def jobs(id_doc=ID_DOC, unique_doc=UNIQUE_DOC, id_rest="Proves 9.1.", unique_rest="Proves 9.2 and 9.3.",
         helper_doc=None, module_doc=None):
    """The planner's tests/test_jobs.py: test_id and test_unique (as STORY files them), both failing today.

    Each docstring is its first line, a blank line, then its paragraph (none when the paragraph is empty). A helper
    function, make_job, and a module docstring are added only when their docstrings are given.
    """
    def doc(first, rest):
        return f'    """{first}\n\n    {rest}\n    """\n' if rest else f'    """{first}"""\n'
    text = f'"""{module_doc}"""\n\n\n' if module_doc else ""
    if helper_doc:
        text += f'def make_job():\n    """{helper_doc}"""\n    return None\n\n\n'
    text += ("def test_id(record_property):\n" + doc(id_doc, id_rest)
             + '    record_property("proves", "9.1")\n    assert False, "9.1: no job id yet"\n\n\n'
             + "def test_unique(record_property):\n" + doc(unique_doc, unique_rest)
             + '    record_property("proves", "9.2")\n    assert False, "9.2: no job ids yet"\n')
    return text


def run(check, capsys, plan, tests_text, crit):
    """Write the planner's tests, run the check, and return its exit code, reason and output."""
    with open("tests/test_jobs.py", "w") as f:
        f.write(tests_text)
    capsys.readouterr()
    rc, why = check({"plan.json": plan}, crit)
    printed = capsys.readouterr()
    return rc, why, printed.out + printed.err


def with_criteria(ac=None, nfr=None):
    """The good story with its first criterion and first requirement rewritten, each only when given."""
    s = copy.deepcopy(STORY)
    if ac is not None:
        s["acceptance_criteria"][0]["text"] = ac
    if nfr is not None:
        s["non_functional"][0]["text"] = nfr
    return s


def feature_with(ac):
    """The good feature with story 2's first criterion rewritten."""
    f = copy.deepcopy(FEATURE)
    f["stories"][1]["acceptance_criteria"][0]["text"] = ac
    return f


def test_a_criterion_over_25_words_in_its_first_sentence_is_held_to_the_cap(record_property, check, capsys):
    """A criterion's first sentence is held to 25 words; a paragraph may follow it.

    Proves 239.1. A 25-word first sentence followed by a 40-word paragraph passes and is not listed, in an acceptance
    criterion, a non-functional requirement and a split's story. A 31-word first sentence (with or without an end mark)
    is rejected in each of the three, naming it.
    """
    record_property("proves", "239.1")
    at_cap = words(25) + " " + words(40)
    for plan in (with_criteria(ac=at_cap, nfr=at_cap), feature_with(at_cap)):
        rc, why, printed = run(check, capsys, plan, jobs(), "239.1")
        assert rc == 0 and not why, f"239.1: a 25-word first sentence with a paragraph after it was rejected: {why!r}"
        assert "criterion" not in printed and "requirement" not in printed, \
            f"239.1: a criterion within its cap was listed as over it: {printed!r}"
    cases = [(with_criteria(ac=words(31) + " " + words(5)), "acceptance criterion 1"),
             (with_criteria(ac=words(31, end="")), "acceptance criterion 1"),
             (with_criteria(nfr=words(31) + " " + words(5)), "non-functional requirement 1"),
             (feature_with(words(31) + " " + words(5)), "story 2: acceptance criterion 1")]
    for plan, where in cases:
        rc, why, _ = run(check, capsys, plan, jobs(), "239.1")
        assert rc == 1, f"239.1: {where} opening with a 31-word sentence was accepted; the cap is 25 (30 at most)"
        assert where in why and "31 words" in why, f"239.1: the reason does not name {where} and its 31 words: {why!r}"


def test_a_docstring_the_planner_adds_is_held_to_15_words_in_its_first_line(record_property, check, capsys):
    """Every docstring the planner adds, helpers included, opens with at most 15 words.

    Proves 239.2. Docstrings of 15 words pass unlisted. A 19-word first line is rejected by name in a new test, a
    helper and the module docstring; the words of the paragraph below never count. A docstring that opens with a line
    break is measured by its first line of text, so a helper or module docstring written that way is held to 15 too.
    """
    record_property("proves", "239.2")
    for good in (jobs(id_doc=words(15), id_rest=words(40) + " Proves 9.1.", helper_doc=words(15), module_doc=words(15)),
                 jobs(helper_doc="\n    " + words(15) + "\n    " + words(40) + "\n    ",
                      module_doc="\n" + words(15) + "\n\n" + words(40) + "\n")):
        rc, why, printed = run(check, capsys, STORY, good, "239.2")
        assert rc == 0 and not why, f"239.2: docstrings of 15 words, with long paragraphs below, were rejected: {why!r}"
        assert "tests/test_jobs.py" not in printed, f"239.2: a docstring within its cap was listed: {printed!r}"
    cases = [(jobs(id_doc=words(19)), "tests/test_jobs.py::test_id"),
             (jobs(helper_doc=words(19)), "tests/test_jobs.py::make_job"),
             (jobs(module_doc=words(19)), "tests/test_jobs.py"),
             (jobs(helper_doc="\n    " + words(19) + "\n    "), "tests/test_jobs.py::make_job"),
             (jobs(module_doc="\n" + words(19) + "\n"), "tests/test_jobs.py")]
    for text, where in cases:
        rc, why, _ = run(check, capsys, STORY, text, "239.2")
        assert rc == 1, f"239.2: {where} with a 19-word docstring first line was accepted; the cap is 15 (18 at most)"
        assert where in why and "19 words" in why, f"239.2: the reason does not name {where} and its 19 words: {why!r}"


@pytest.fixture
def older(check, monkeypatch):
    """The check fixture, with an older helper whose docstring opens with 25 words."""
    with open("tests/test_jobs.py", "w") as f:
        f.write(f'def old_helper():\n    """{words(25)}"""\n    return None\n')
    for args in (("add", "tests/test_jobs.py"), ("commit", "-qm", "an older helper with a long docstring")):
        subprocess.run(["git", *args], check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PLANNER_BASE", head)
    monkeypatch.setenv("PLANNER_RUN_BASE", head)
    return check


def test_an_older_docstring_the_planner_left_alone_is_not_held_to_the_cap(record_property, older, capsys):
    """An older long docstring the planner did not touch is neither rejected nor listed.

    Proves 239.2. The file already held old_helper with a 25-word first line; the planner adds its tests below it and
    the check passes without naming old_helper. Rewritten by the planner to 19 words, it is rejected by name.
    """
    record_property("proves", "239.2")
    old = f'def old_helper():\n    """{words(25)}"""\n    return None\n\n\n'
    rc, why, printed = run(older, capsys, STORY, old + jobs(), "239.2")
    assert rc == 0 and not why, f"239.2: an older docstring the planner never touched got the plan rejected: {why!r}"
    assert "old_helper" not in printed, f"239.2: an older docstring the planner never touched was listed: {printed!r}"
    changed = old.replace(words(25), words(19))
    rc, why, _ = run(older, capsys, STORY, changed + jobs(), "239.2")
    assert rc == 1 and "old_helper" in why and "19 words" in why, \
        f"239.2: an older docstring the planner rewrote to 19 words was not rejected by name: {why!r}"


@pytest.mark.parametrize("id_rest, missing", [
    ("", "9.1"),
    ("Proves the job id.", "9.1"),
    ("Proves 9.2.", "9.1"),
    ("Proves 9.10.", "9.1"),
], ids=["no paragraph", "no number", "another number", "a longer number"])
def test_a_new_test_must_name_its_criterion_by_number(record_property, check, capsys, id_rest, missing):
    """A new test whose docstring does not name its criterion's number is rejected.

    Proves 239.3. "Proves 9.1." below the first line passes. Missing, wrong, longer (9.10) or only in the first line
    is rejected naming the test and the number. A test proving 9.2 and 9.3 must name both.
    """
    record_property("proves", "239.3")
    rc, why, _ = run(check, capsys, STORY, jobs(), "239.3")
    assert rc == 0 and not why, f"239.3: new tests naming their criteria below the first line were rejected: {why!r}"
    rc, why, _ = run(check, capsys, STORY, jobs(id_rest=id_rest), "239.3")
    assert rc == 1, f"239.3: test_id with the paragraph {id_rest!r} was accepted; it must name {missing}"
    assert "test_id" in why and missing in why, f"239.3: the reason does not name test_id and {missing}: {why!r}"
    assert "test_unique" not in why, f"239.3: the reason also names test_unique, which names its criteria: {why!r}"


def test_the_number_must_sit_below_the_first_line_and_name_every_criterion(record_property, check, capsys):
    """A number only in the first line, or one of two missing, is rejected.

    Proves 239.3. test_id with "9.1" only in its first line, and test_unique naming 9.2 but not 9.3, are each rejected.
    """
    record_property("proves", "239.3")
    rc, why, _ = run(check, capsys, STORY, jobs(id_doc="Proves 9.1 with a slow call.", id_rest="A job id."), "239.3")
    assert rc == 1 and "test_id" in why, f"239.3: test_id naming 9.1 only in its first line was accepted: {why!r}"
    rc, why, _ = run(check, capsys, STORY, jobs(unique_rest="Proves 9.2."), "239.3")
    assert rc == 1 and "test_unique" in why and "9.3" in why, \
        f"239.3: test_unique, filed under 9.2 and 9.3, named only 9.2 and was not rejected naming 9.3: {why!r}"


def test_any_text_past_20_percent_rejects_the_plan_naming_each(record_property, check, capsys):
    """Any text more than 20% over its cap rejects the plan, naming each one.

    Proves 239.5. Beside texts within 20%, a 31-word criterion and a 19-word docstring are both named in the reason.
    """
    record_property("proves", "239.5")
    plan = with_criteria(ac=words(31), nfr=words(30))
    rc, why, _ = run(check, capsys, plan, jobs(id_doc=words(19), unique_doc=words(18)), "239.5")
    assert rc == 1, "239.5: a plan with a 31-word criterion and a 19-word docstring was accepted"
    for where, n in (("acceptance criterion 1", 31), ("tests/test_jobs.py::test_id", 19)):
        assert where in why and f"{n} words" in why, f"239.5: the reason does not name {where} and its {n} words: {why!r}"

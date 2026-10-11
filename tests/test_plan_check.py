"""The planner check (#154): only real plans, sources on this issue, named tests that exist under this plan's criteria.

Every test here runs the check the way the agent workflow runs it, `python3 -m dokima.planner check N OUT`, through
planner.main, inside a temp git repo that holds one older test at the starting commit and the planner's new tests on
top. A good plan passes (exit 0); each broken one fails (exit 1) and its reason, saved to OUT/rejected.txt for the
issue, is read back. GITHUB_REPOSITORY is set to o/r and the issue is #9, so this issue's link is
https://github.com/o/r/issues/9.
"""
import copy
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
ISSUE = "https://github.com/o/r/issues/9"
OLD_TESTS = ('def test_old(record_property):\n    """An older test, already in the repo."""\n'
             '    record_property("proves", "50.1")\n    assert True\n')
# The planner's new tests fail today, as every new test must (#155): the job code they need does not exist yet.
NEW_TESTS = ('def test_id(record_property):\n    """A slow call returns a job id.\n\n    Proves 9.1.\n    """\n'
             '    record_property("proves", "9.1")\n    assert False, "9.1: no job id yet"\n\n\n'
             'def test_unique(record_property):\n    """Job ids never repeat.\n\n    Proves 9.2 and 9.3.\n    """\n'
             '    record_property("proves", "9.2")\n    assert False, "9.2: no job ids yet"\n')
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id instead of timing out.", "user_story": "Slow calls return a job id.",
         "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": ISSUE},
                                 {"text": "Job ids never repeat.", "source": ISSUE + "#issuecomment-123456"}],
         "non_functional": [{"text": "A failed call says why.", "why": "the owner is never left guessing",
                             "principle": "fail closed"}],
         "scope": ["dokima/jobs.py"], "out_of_scope": ["No retries."],
         "tests": {"9.1": ["tests/test_jobs.py::test_id"], "9.2": ["tests/test_jobs.py::test_unique"],
                   "9.3": ["tests/test_jobs.py::test_unique"]},
         "test_changes": {}}
FEATURE = {"kind": "feature", "summary": "Slow calls hand back a job id instead of timing out.", "feature": "Slow calls run as jobs.",
           "stories": [{"title": "Job ids", "user_story": "Slow calls return a job id.",
                        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": ISSUE},
                                                {"text": "A fast call returns its result.", "source": ISSUE}],
                        "non_functional": [], "depends_on": []},
                       {"title": "Job status", "user_story": "Owners see each job's status.",
                        "acceptance_criteria": [{"text": "A job's status is shown.", "source": ISSUE},
                                                {"text": "A finished job shows its result.", "source": ISSUE}],
                        "non_functional": [], "depends_on": [0]}]}


@pytest.fixture
def check(tmp_path, monkeypatch):
    """A function that hands back the given files and runs the check on issue #9: returns (exit code, reason).

    Each call empties the hand-back folder first, so one test can run the check on a good plan and then a broken one.
    """
    repo, out = tmp_path / "repo", tmp_path / "out"
    repo.mkdir()
    out.mkdir()
    git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, text=True).stdout
    git("init", "-q")
    git("config", "user.name", "t")
    git("config", "user.email", "t@t")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_old.py").write_text(OLD_TESTS)
    git("add", "-A")
    git("commit", "-qm", "base")
    # The planner's run starts at this commit too, so the check sees the new tests as its own (as a real run does).
    monkeypatch.setenv("PLANNER_BASE", git("rev-parse", "HEAD").strip())
    monkeypatch.setenv("PLANNER_RUN_BASE", git("rev-parse", "HEAD").strip())
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    (repo / "tests" / "test_jobs.py").write_text(NEW_TESTS)
    monkeypatch.chdir(repo)

    def run(files, crit):
        for old in out.iterdir():
            old.unlink()
        for name, content in files.items():
            (out / name).write_text(content if isinstance(content, str) else json.dumps(content))
        try:
            rc = planner.main(["x", "check", "9", str(out)])
        except Exception as e:  # a crash posts nothing on the issue
            pytest.fail(f"{crit}: the check crashed with {type(e).__name__}: {e}, instead of rejecting with a reason")
        rejected = out / "rejected.txt"
        return rc, rejected.read_text() if rejected.exists() else ""
    return run


def story(change):
    """A copy of the good story with one change applied."""
    s = copy.deepcopy(STORY)
    change(s)
    return s


def feature(change):
    """A copy of the good feature with one change applied."""
    f = copy.deepcopy(FEATURE)
    change(f)
    return f


# 154.1: only a plan, a user_story or a feature, is a hand-back

@pytest.mark.parametrize("files", [
    {},
    {"question.md": "Split it into two issues?"},
    {"plan.json": {"objective": "Slow calls return a job id.", "criteria": ["A job id within 20 s.", "Ids never repeat."],
                   "non_goals": [], "scope": ["dokima/jobs.py"]}},
    {"plan.json": {"kind": "question", "question": "Split it?", "options": ["Yes", "No"], "recommendation": "Yes"}},
    {"plan.json": story(lambda s: s.update(kind="question", question="Split it?"))},
    {"plan.json": story(lambda s: s.update(kind="essay"))},
], ids=["nothing", "question.md", "no kind", "question kind", "story marked question", "unknown kind"])
def test_anything_but_a_story_or_a_feature_is_rejected_saying_the_planner_always_hands_back_a_plan(record_property, check, files):
    """A question.md, a plan.json with no kind or of kind question is rejected: the planner always hands back a plan.

    First checks a good user_story, a good feature and a story raising a question for the owner all still pass. Then
    hands back one of the wrong kinds, runs the check, and checks it fails with a reason that says the planner always
    hands back a plan, a user_story or a feature.
    """
    record_property("proves", "154.1")
    for good in (STORY, FEATURE, dict(STORY, raises=[{"kind": "question", "to": "owner", "text": "Should ids be numbers? The plan assumes strings."}])):
        rc, why = check({"plan.json": good}, "154.1")
        assert rc == 0 and not why, f"154.1: a good {good['kind']} was rejected: {why!r}"
    rc, why = check(files, "154.1")
    assert rc == 1, f"154.1: {sorted(files) or 'an empty hand-back'} was accepted; only a user_story or a feature may pass"
    for words in ("always hands back", "user_story", "feature"):
        assert words in why, f"154.1: the reason does not say the planner always hands back a user_story or a feature ({words!r} missing): {why!r}"


def test_the_prompt_and_the_workflow_no_longer_offer_a_lone_question(record_property):
    """The planner's prompt offers only the user_story and feature kinds, and the planner workflow never looks for question.md.

    Reads dokima/roles/planner.md: every "kind" it shows is user_story or feature (both still shown), the line naming the
    kinds and the line saying how the planner ends never offer a question, no heading offers "one question" for the owner,
    no line says a question is shown as handed back, and raising a question is still taught. The shared section on
    raising and answering, whose example raises have kinds of their own, is left out of the kinds read.
    Reads .github/workflows/planner.yml and checks question.md and "one question for the owner" appear nowhere while
    plan.json is still shown.
    """
    record_property("proves", "154.1")
    text = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
    flat = " ".join(text.split())
    own = re.sub(r"(?ms)^# Raising and answering\n.*?(?=^# |\Z)", "", text)
    shown = set(re.findall(r'"kind":\s*"(\w+)"', own))
    assert shown == {"user_story", "feature"}, f"154.1: the prompt shows the kinds {sorted(shown)}, not exactly user_story and feature"
    kinds = re.search(r"Exactly one kind:[^.]*\.", flat)
    assert kinds and "question" not in kinds.group(0), f"154.1: the prompt still offers a question kind: {kinds and kinds.group(0)!r}"
    ends = re.search(r"End with exactly one of[^.]*\.", flat)
    assert ends and "question" not in ends.group(0), f"154.1: the prompt still lets the planner end with a question: {ends and ends.group(0)!r}"
    headings = [line for line in text.splitlines() if line.startswith("#") and "one question" in line.lower()]
    assert not headings, f"154.1: the prompt still has a section offering one question for the owner: {headings}"
    assert "or a question is shown" not in flat, "154.1: the prompt still says a question is shown to the owner as handed back"
    assert '"raises"' in flat and "question" in flat, "154.1: the prompt no longer teaches raising a question for the owner"
    wf = open(os.path.join(ROOT, ".github", "workflows", "planner.yml")).read()
    assert "question.md" not in wf, "154.1: the planner workflow still looks for question.md"
    assert "one question for the owner" not in " ".join(wf.replace("#", " ").split()), "154.1: the planner workflow still says the planner may end with one question for the owner"
    assert "/tmp/dokima-out/plan.json" in wf, "154.1: the planner workflow no longer shows plan.json"


# 154.2: every criterion's source is this issue or one of its comments

@pytest.mark.parametrize("source", [
    "https://github.com/o/r/issues/139",
    "https://github.com/o/r/issues/91",
    "https://github.com/o/r/issues/9139#issuecomment-1",
    "https://github.com/o/x/issues/9",
    "https://github.com/o/r/pull/9",
    "https://example.com/o/r/issues/9",
    "#9 above",
    "the owner said so",
], ids=["parent issue", "longer number", "other issue's comment", "other repo", "pull request", "other host", "bare number", "prose"])
def test_a_source_outside_this_issue_is_rejected_and_named(record_property, check, source):
    """A criterion whose source is not this issue's link or one of its comment links is rejected, and the reason names it.

    First checks a story sourced to issue #9's own link, and one sourced to two of its comment links, both pass. Then
    puts one wrong source on the second criterion, runs the check, and checks it fails with that source in the reason.
    """
    record_property("proves", "154.2")
    for sources in ([ISSUE, ISSUE], [ISSUE + "#issuecomment-1", ISSUE + "#issuecomment-987654321"]):
        good = story(lambda s: [c.update(source=src) for c, src in zip(s["acceptance_criteria"], sources)])
        rc, why = check({"plan.json": good}, "154.2")
        assert rc == 0 and not why, f"154.2: sources {sources} on issue #9 were rejected: {why!r}"
    rc, why = check({"plan.json": story(lambda s: s["acceptance_criteria"][1].update(source=source))}, "154.2")
    assert rc == 1, f"154.2: a criterion sourced to {source!r} was accepted on issue #9"
    assert source in why, f"154.2: the reason does not name the source {source!r}: {why!r}"


@pytest.mark.parametrize("source", [
    "https://github.com/o/r/issues/139",
    "https://github.com/o/r/issues/91",
    "https://github.com/o/r/issues/9139#issuecomment-1",
    "https://github.com/o/x/issues/9",
    "https://github.com/o/r/pull/9",
    "https://example.com/o/r/issues/9",
    "#9 above",
    "the owner said so",
], ids=["parent issue", "longer number", "other issue's comment", "other repo", "pull request", "other host", "bare number", "prose"])
def test_a_source_outside_this_issue_inside_a_split_is_rejected_and_named(record_property, check, source):
    """A split is no exception: a criterion in any of its stories sourced outside this issue is rejected, and named.

    First checks a split whose stories' criteria cite issue #9's own link, and one citing two of its comment links,
    both pass. Then puts one wrong source on the second story's criterion, runs the check, and checks it fails with
    that source in the reason; then the same on the first story's criterion.
    """
    record_property("proves", "154.2")
    for sources in ([ISSUE, ISSUE], [ISSUE + "#issuecomment-1", ISSUE + "#issuecomment-987654321"]):
        good = feature(lambda f: [st["acceptance_criteria"][0].update(source=src) for st, src in zip(f["stories"], sources)])
        rc, why = check({"plan.json": good}, "154.2")
        assert rc == 0 and not why, f"154.2: a split with sources {sources} on issue #9 was rejected: {why!r}"
    for k in (1, 0):
        rc, why = check({"plan.json": feature(lambda f: f["stories"][k]["acceptance_criteria"][0].update(source=source))}, "154.2")
        assert rc == 1, f"154.2: a split whose story {k + 1} has a criterion sourced to {source!r} was accepted on issue #9"
        assert source in why, f"154.2: the reason does not name the split's source {source!r}: {why!r}"


# 154.3: every named test exists and is filed under one of this plan's criteria

@pytest.mark.parametrize("name", ["tests/test_jobs.py::test_ghost", "tests/test_nowhere.py::test_id"],
                         ids=["no such test", "no such file"])
def test_a_named_test_that_is_not_in_the_repo_is_rejected_and_named(record_property, check, name):
    """A test the plan names that is not in the repo is rejected, and the reason names it.

    Adds a missing test (no such test in a real file, or no such file) beside a real one under the first criterion,
    runs the check, and checks it fails naming the missing test.
    """
    record_property("proves", "154.3")
    rc, why = check({"plan.json": story(lambda s: s["tests"]["9.1"].append(name))}, "154.3")
    assert rc == 1, f"154.3: the plan names {name}, which is not in the repo, and was accepted"
    assert name in why, f"154.3: the reason does not name the missing test {name}: {why!r}"


@pytest.mark.parametrize("key, name", [
    ("139.1", "tests/test_jobs.py::test_id"),
    ("9.4", "tests/test_jobs.py::test_id"),
    ("139.1", "tests/test_old.py::test_old"),
    ("9.4", "tests/test_old.py::test_old"),
], ids=["another issue, new test", "past the last, new test", "another issue, older test", "past the last, older test"])
def test_a_test_filed_under_a_key_that_is_not_a_criterion_is_rejected_and_named(record_property, check, key, name):
    """A test filed under a key that is not one of this plan's three criteria is rejected, and the reason names the key.

    Files a new test, then an older test, under another issue's number (139.1) and under 9.4 (past the last of the
    three criteria), runs the check, and checks it fails with that key in the reason.
    """
    record_property("proves", "154.3")
    rc, why = check({"plan.json": story(lambda s: s["tests"].update({key: [name]}))}, "154.3")
    assert rc == 1, f"154.3: {name} filed under {key}, which is not a criterion of this plan, was accepted"
    assert key in why, f"154.3: the reason does not name the key {key}: {why!r}"


# 154.4: an older test already in the repo counts as proof

def test_a_criterion_proven_only_by_an_older_test_counts_as_proven(record_property, check):
    """A criterion proven only by an older test already in the repo counts as proven, not as 'has no test'.

    Files the unchanged older test tests/test_old.py::test_old as the only test of the third criterion, runs the
    check, and checks it passes with no 'has no test' reason.
    """
    record_property("proves", "154.4")
    rc, why = check({"plan.json": story(lambda s: s["tests"].update({"9.3": ["tests/test_old.py::test_old"]}))}, "154.4")
    assert "9.3 has no test" not in why, f"154.4: a criterion proven by an older test was called 'has no test': {why!r}"
    assert rc == 0 and not why, f"154.4: a plan proving 9.3 with an older test was rejected: {why!r}"


# 154.5: a value of the wrong type is rejected naming the field, never a crash

@pytest.mark.parametrize("change, field", [
    (lambda s: s["acceptance_criteria"][0].update(text=5), "text"),
    (lambda s: s["acceptance_criteria"][0].update(source=9), "source"),
    (lambda s: s["non_functional"][0].update(text=3), "text"),
    (lambda s: s["non_functional"][0].update(why=3), "why"),
    (lambda s: s.update(acceptance_criteria={"text": "x", "source": ISSUE}), "acceptance_criteria"),
    (lambda s: s.update(non_functional="none"), "non_functional"),
    (lambda s: s.update(user_story=5), "user_story"),
    (lambda s: s.update(scope="dokima/jobs.py"), "scope"),
    (lambda s: s.update(out_of_scope="No retries."), "out_of_scope"),
    (lambda s: s["tests"].update({"9.1": "tests/test_jobs.py::test_id"}), "tests"),
    (lambda s: s.update(test_changes=["tests/test_old.py::test_old"]), "test_changes"),
    (lambda s: s.update(questions="Why?"), "questions"),
    (lambda s: s.update(kind=5), "kind"),
    (feature(lambda f: f["stories"][1]["acceptance_criteria"][0].update(source=9)), "source"),
    (feature(lambda f: f["stories"][0].update(acceptance_criteria="A job id.")), "acceptance_criteria"),
    (feature(lambda f: f["stories"][1].update(non_functional="none")), "non_functional"),
    (feature(lambda f: f["stories"][1].update(non_functional=[5])), "non-functional requirement 1"),
    (feature(lambda f: f["stories"][1].update(non_functional=[{"text": 3, "why": "w"}])), "its text is not"),
    (feature(lambda f: f["stories"][1].update(non_functional=[{"text": "t", "why": 3}])), "its why is not"),
    ([], "plan.json"),
    ("a plan", "plan.json"),
    (5, "plan.json"),
], ids=["criterion text", "criterion source", "requirement text", "requirement why", "criteria not a list",
        "requirements not a list", "user_story", "scope", "out_of_scope", "tests", "test_changes", "questions", "kind",
        "split's criterion source", "split's criteria not a list", "split's requirements not a list",
        "split's requirement not an object", "split's requirement text", "split's requirement why", "plan.json a list", "plan.json a string", "plan.json a number"])
def test_a_value_of_the_wrong_type_is_rejected_naming_the_field(record_property, check, change, field):
    """A plan.json with a number where text belongs, or a string where a list belongs, is rejected naming the field.

    Breaks one field's type at a time in a good story or a split's story (or makes the whole plan.json a list, a string
    or a number), runs the check, and checks it fails with a reason naming that field (or plan.json); a crash fails the
    test instead.
    """
    record_property("proves", "154.5")
    rc, why = check({"plan.json": story(change) if callable(change) else json.dumps(change)}, "154.5")
    assert rc == 1, f"154.5: a wrong type in {field} was accepted"
    assert field in why, f"154.5: the reason does not name the field {field}: {why!r}"



"""The planner's check on a proposed split: every story is well formed and its dependencies form no loop.

Covers #156. A feature (a split into stories) reaches the owner only when every story has its title, user story,
acceptance criteria and a depends_on list, every criterion of a story has its text and source link, and every dependency points at another story of the same split with
no loop. Stories are named by their number counting from 1 ("story 2"), the way the split's card numbers them;
depends_on holds story indices counting from 0, the way /work files them as sub-issues.
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = "https://github.com/o/r/issues/9"


def story(title, deps):
    """One well-formed story with the given title and dependencies."""
    return {"title": title, "user_story": f"Owners get {title}.",
            "acceptance_criteria": [{"text": f"{title} works {k}.", "source": SRC} for k in (1, 2, 3)],
            "non_functional": [], "depends_on": deps}


def feature(*stories):
    """A feature holding the given stories."""
    return {"kind": "feature", "summary": "Slow calls run as jobs.", "feature": "A split.", "stories": list(stories)}


def hand_back(tmp_path, content):
    """Write plan.json into a temp hand-back folder and read it as the planner check does."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def rejected(tmp_path, content, criterion):
    """The reason a hand-back was rejected; fails naming the criterion when it was accepted."""
    try:
        hand_back(tmp_path, content)
    except planner.Garbled as e:
        return str(e)
    pytest.fail(f"{criterion}: a broken feature was accepted: {json.dumps(content['stories'])[:300]}")


def names(reason, n):
    """True when the reason names story n (counting from 1) and not, say, story 12."""
    return re.search(rf"\bstory {n}\b", reason, re.IGNORECASE) is not None


@pytest.mark.parametrize("field,breaks", [
    ("title", lambda s: s.pop("title")),
    ("title", lambda s: s.update(title="  ")),
    ("user_story", lambda s: s.pop("user_story")),
    ("user_story", lambda s: s.update(user_story="")),
    ("acceptance_criteria", lambda s: s.pop("acceptance_criteria")),
    ("acceptance_criteria", lambda s: s.update(acceptance_criteria=[])),
    ("acceptance_criteria", lambda s: s.update(acceptance_criteria="a works")),
    ("depends_on", lambda s: s.pop("depends_on")),
    ("depends_on", lambda s: s.update(depends_on=0)),
    ("depends_on", lambda s: s.update(depends_on=None)),
])
def test_a_story_missing_a_field_is_rejected_naming_story_and_field(record_property, tmp_path, field, breaks):
    """A story with no title, user story, acceptance criteria or depends_on list is rejected, naming the story and the field.

    Breaks one field of the second of three stories at a time (missing, empty or not a list) and checks the
    rejection names "story 2" and the field, and not the other stories.
    """
    record_property("proves", "156.1")
    f = feature(story("First", []), story("Second", [0]), story("Third", [1]))
    breaks(f["stories"][1])
    reason = rejected(tmp_path, f, "156.1")
    assert names(reason, 2), f"156.1: the reason does not name story 2: {reason!r}"
    assert not names(reason, 1) and not names(reason, 3), f"156.1: the reason names the wrong story: {reason!r}"
    assert field in reason, f"156.1: the reason does not name the field {field}: {reason!r}"


@pytest.mark.parametrize("field,breaks", [
    ("text", lambda c: c.pop("text")),
    ("text", lambda c: c.update(text=" ")),
    ("source", lambda c: c.pop("source")),
    ("source", lambda c: c.update(source="")),
])
def test_a_story_criterion_missing_its_text_or_source_is_rejected(record_property, tmp_path, field, breaks):
    """A story whose acceptance criterion has no text or no source link is rejected, naming the story and what is missing.

    Gives the second of three stories two criteria and breaks the second one (missing or blank text, missing or
    blank source), then checks the rejection names "story 2" and the missing field, and not the other stories.
    The owner asked for this on #156: story criteria need sources too.
    """
    record_property("proves", "156.1")
    f = feature(story("First", []), story("Second", [0]), story("Third", [1]))
    f["stories"][1]["acceptance_criteria"].append({"text": "Second also works.", "source": SRC})
    breaks(f["stories"][1]["acceptance_criteria"][1])
    reason = rejected(tmp_path, f, "156.1")
    assert names(reason, 2), f"156.1: the reason does not name story 2: {reason!r}"
    assert not names(reason, 1) and not names(reason, 3), f"156.1: the reason names the wrong story: {reason!r}"
    assert field in reason, f"156.1: the reason does not say the criterion lacks its {field}: {reason!r}"


def test_a_well_formed_feature_passes(record_property, tmp_path):
    """A feature whose every story has its title, user story, criteria and an empty or filled depends_on list is accepted.

    Hands back two, three and five well-formed stories and checks each is read as a feature, unchanged.
    """
    record_property("proves", "156.1")
    for f in (feature(story("A", []), story("B", [])),
              feature(story("A", []), story("B", [0]), story("C", [])),
              feature(*[story(f"S{i}", []) for i in range(5)])):
        try:
            kind, text = hand_back(tmp_path, f)
        except planner.Garbled as e:
            pytest.fail(f"156.1: a well-formed feature was rejected: {e}")
        assert kind == "feature", f"156.1: a well-formed feature was read as {kind}"
        assert json.loads(text) == f, "156.1: the feature shown to the owner is not the one handed back"


def test_the_check_command_rejects_a_broken_feature_and_says_why(record_property, tmp_path):
    """Running the planner check on a story with no title fails and writes why, naming the story and the field.

    Runs `python3 -m dokima.planner check` from the repo root on a hand-back folder, then on the fixed feature.
    """
    record_property("proves", "156.1")
    bad = feature(story("First", []), story("Second", [0]))
    bad["stories"][1].pop("title")
    (tmp_path / "plan.json").write_text(json.dumps(bad))
    run = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)],
                         cwd=ROOT, env=dict(os.environ, GITHUB_REPOSITORY="o/r"), capture_output=True, text=True, timeout=30)
    assert run.returncode == 1, f"156.1: the check passed a story with no title (exit {run.returncode}): {run.stdout}{run.stderr}"
    why = (tmp_path / "rejected.txt").read_text() if (tmp_path / "rejected.txt").exists() else ""
    assert names(why, 2) and "title" in why, f"156.1: rejected.txt does not say story 2 lacks its title: {why!r}"
    (tmp_path / "rejected.txt").unlink()
    (tmp_path / "plan.json").write_text(json.dumps(feature(story("First", []), story("Second", [0]))))
    run = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)],
                         cwd=ROOT, env=dict(os.environ, GITHUB_REPOSITORY="o/r"), capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, f"156.1: the check rejected a well-formed feature: {run.stdout}{run.stderr}"


@pytest.mark.parametrize("deps,bad", [
    ([[], [1], []], {2}),                 # story 2 depends on itself
    ([[], [], [0, 2]], {3}),              # story 3 depends on itself among others
    ([[], [5], []], {2}),                 # story 2 depends on a story the feature does not have
    ([[], [], [3]], {3}),                 # one past the last story
    ([[], [-1], []], {2}),                # a negative index is not a story
    ([[], ["0"], []], {2}),               # a string is not a story index
    ([[], [None], []], {2}),              # nor is null
    ([[], [2], [1]], {2, 3}),             # stories 2 and 3 depend on each other
    ([[], [2], [3], [1]], {2, 3, 4}),     # a loop through three stories
    ([[1], [2], [3], [4], [0]], {1, 2, 3, 4, 5}),  # every story in one loop
])
def test_a_bad_dependency_is_rejected_naming_the_story(record_property, tmp_path, deps, bad):
    """A story that depends on itself, on a story the split does not have, or on others in a loop is rejected, naming it.

    Builds features with one bad dependency each (self, out of range, negative, not a number, two- three- and
    five-story loops) and checks the rejection names a story at fault and no story outside the fault.
    """
    record_property("proves", "156.2")
    reason = rejected(tmp_path, feature(*[story(f"S{i}", d) for i, d in enumerate(deps)]), "156.2")
    named = {n for n in range(1, len(deps) + 1) if names(reason, n)}
    assert named & bad, f"156.2: the reason names none of stories {sorted(bad)}: {reason!r}"
    assert named <= bad, f"156.2: the reason names stories {sorted(named - bad)} that did nothing wrong: {reason!r}"


def test_the_check_command_rejects_a_loop_and_says_why(record_property, tmp_path):
    """Running the planner check on a split whose stories wait on each other fails and writes why, naming a story in the loop.

    Runs `python3 -m dokima.planner check` from the repo root on stories 2 and 3 depending on each other, then on
    the same split with the loop broken into a chain, which passes.
    """
    record_property("proves", "156.2")
    (tmp_path / "plan.json").write_text(json.dumps(feature(story("First", []), story("Second", [2]), story("Third", [1]))))
    run = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)],
                         cwd=ROOT, env=dict(os.environ, GITHUB_REPOSITORY="o/r"), capture_output=True, text=True, timeout=30)
    assert run.returncode == 1, f"156.2: the check passed a loop (exit {run.returncode}): {run.stdout}{run.stderr}"
    why = (tmp_path / "rejected.txt").read_text() if (tmp_path / "rejected.txt").exists() else ""
    assert (names(why, 2) or names(why, 3)) and not names(why, 1), \
        f"156.2: rejected.txt does not name story 2 or 3 (and only them) in the loop: {why!r}"
    (tmp_path / "rejected.txt").unlink()
    (tmp_path / "plan.json").write_text(json.dumps(feature(story("First", []), story("Second", [0]), story("Third", [1]))))
    run = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(tmp_path)],
                         cwd=ROOT, env=dict(os.environ, GITHUB_REPOSITORY="o/r"), capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, f"156.2: the check rejected a valid chain: {run.stdout}{run.stderr}"


@pytest.mark.parametrize("deps", [
    [[], [0], [1], [2], [3]],             # a chain: each story waits on the one before
    [[], [0], [0], [1, 2]],               # a diamond: two paths to the same story
    [[1], [], [0, 1]],                    # a story may depend on a later one
    [[], [], [], []],                     # nothing depends on anything
])
def test_a_valid_chain_of_dependencies_passes(record_property, tmp_path, deps):
    """A feature whose dependencies form chains or diamonds with no loop is accepted.

    Hands back a five-story chain, a diamond, a dependency on a later story and no dependencies, and checks
    each is read as a feature.
    """
    record_property("proves", "156.2")
    try:
        kind, _ = hand_back(tmp_path, feature(*[story(f"S{i}", d) for i, d in enumerate(deps)]))
    except planner.Garbled as e:
        pytest.fail(f"156.2: a valid chain of dependencies {deps} was rejected: {e}")
    assert kind == "feature", f"156.2: a valid feature was read as {kind}"


@pytest.mark.parametrize("item", ["just a sentence", 3, None, ["title"]])
def test_a_story_that_is_not_an_object_is_rejected_not_crashed(record_property, tmp_path, item):
    """A story that is not an object at all is rejected naming the story, never a crash with no reason.

    Puts a sentence, a number, null and a list where the second story belongs and checks the check rejects it
    with a reason naming story 2 instead of raising some other error.
    """
    record_property("proves", "156.3")
    f = feature(story("First", []), item)
    try:
        hand_back(tmp_path, f)
    except planner.Garbled as e:
        assert names(str(e), 2), f"156.3: the reason does not name story 2: {e}"
        return
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"156.3: a story that is not an object crashed the check with {type(e).__name__}: {e}")
    pytest.fail(f"156.3: a story that is not an object ({item!r}) was accepted")


@pytest.mark.parametrize("item", ["just a sentence", 3, None, ["text", "source"]])
def test_a_story_criterion_that_is_not_an_object_is_rejected_not_crashed(record_property, tmp_path, item):
    """A story criterion that is not an object at all is rejected naming the story, never a crash with no reason.

    Puts a sentence, a number, null and a list where the second story's criterion belongs and checks the check
    rejects it with a reason naming story 2 instead of raising some other error.
    """
    record_property("proves", "156.3")
    f = feature(story("First", []), story("Second", [0]))
    f["stories"][1]["acceptance_criteria"] = [item]
    try:
        hand_back(tmp_path, f)
    except planner.Garbled as e:
        assert names(str(e), 2) and not names(str(e), 1), f"156.3: the reason does not name story 2 alone: {e}"
        return
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"156.3: a criterion that is not an object crashed the check with {type(e).__name__}: {e}")
    pytest.fail(f"156.3: a story criterion that is not an object ({item!r}) was accepted")

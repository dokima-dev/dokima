"""A plan's scope comes from its criteria's files, with no separate scope field.

Covers #666 (story 2 of #661). The worker may change exactly the files the criteria list, plus the tests the plan
names. The plan check reads the scope from each criterion's `files` and the test files in `tests`, writes it under the
issue's Scope heading, and rejects a plan still carrying its own `scope`. The fence, run as the worker's workflow runs
it on the plan's hand-back, keeps changes to listed files and undoes every other change.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = "https://github.com/o/r/issues/9"


def story(**extra):
    """A well-formed story with no scope field, two criteria and two test files."""
    p = {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls hand back a job id.",
         "user_story": "Slow calls return a job id.",
         "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC,
                                  "files": ["dokima/jobs.py", "dokima/queue.py"], "no_edge_cases": "a sample"}],
         "non_functional": [{"text": "Job ids never repeat.", "why": "two jobs would share results", "source": SRC,
                             "files": ["dokima/ids.py", "dokima/jobs.py"], "no_edge_cases": "a sample"}],
         "tests": {"9.1": ["tests/test_jobs.py::test_id"], "9.2": ["tests/test_ids.py::test_unique"]}}
    p.update(extra)
    return p


def hand_back(tmp_path, content):
    """Write plan.json into a temp hand-back folder and read it as the planner check does."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def posted_scope(tmp_path, content):
    """The scope the plan check records for this hand-back."""
    kind, p = hand_back(tmp_path, content)
    assert kind == "plan", f"the sample story was read as {kind}"
    return p["scope"]


def test_scope_is_the_criteria_files_plus_the_tests(record_property, tmp_path):
    """The issue's Scope lists every file the criteria list, plus the plan's test files.

    Hands back a story with no scope field, whose two criteria list three code files between them and whose tests sit
    in two files, then reads the Scope heading the plan check writes on the issue. It must hold exactly those five
    files, each once. Proves 666.1.
    """
    record_property("proves", "666.1")
    try:
        scope = posted_scope(tmp_path, story())
    except planner.Garbled as e:
        pytest.fail(f"666.1: a plan with no scope field was rejected: {e}")
    want = ["dokima/ids.py", "dokima/jobs.py", "dokima/queue.py", "tests/test_ids.py", "tests/test_jobs.py"]
    assert sorted(scope) == want, f"666.1: the issue's Scope should be {want}, the criteria's files plus the tests; it is {scope}"


def test_a_plan_with_a_scope_field_is_rejected(record_property, tmp_path):
    """The plan check rejects a plan that still carries its own scope field.

    Hands back the same story twice: without a scope field it is accepted, and with one, even empty, it is rejected
    with a reason naming scope. Proves 666.2.
    """
    record_property("proves", "666.2")
    try:
        assert hand_back(tmp_path, story())[0] == "plan", "666.2: a story with no scope field was not read as a plan"
    except planner.Garbled as e:
        pytest.fail(f"666.2: a story with no scope field was rejected: {e}")
    for scope in (["dokima/jobs.py"], []):
        with pytest.raises(planner.Garbled) as e:
            hand_back(tmp_path, story(scope=scope))
        assert "scope" in str(e.value), f"666.2: a plan carrying scope {scope} was rejected without naming scope: {e.value}"


def test_the_planner_is_not_told_to_write_a_scope_field(record_property):
    """The planner's instructions no longer ask for the rejected scope field.

    Reads the planner's instructions and checks the hand-back shape they show has no scope field. Proves 666.2.
    """
    record_property("proves", "666.2")
    text = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
    assert '"scope":' not in text, "666.2: the planner's instructions still ask for a scope field the plan check rejects"


def repo(tmp_path):
    """A committed temp git repo with listed, unlisted and test files; its base commit."""
    (tmp_path / "tests").mkdir()
    for name, text in (("app.py", "x = 1\n"), ("other.py", "y = 1\n"), ("ids.py", "z = 1\n"),
                       ("tests/test_app.py", "def test_x():\n    assert False\n")):
        (tmp_path / name).write_text(text)
    for a in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@e.com"], ["add", "-A"],
              ["commit", "-qm", "base"]):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()


def run_fence(tmp_path, base):
    """Run the fence as the worker's workflow does, on a scopeless plan; its dropped paths."""
    plan = tmp_path.parent / f"{tmp_path.name}-plan.json"
    plan.write_text(json.dumps(story(
        acceptance_criteria=[{"text": "A slow call returns a job id.", "source": SRC, "files": ["app.py"]}],
        non_functional=[{"text": "Job ids never repeat.", "why": "two jobs would share results", "source": SRC,
                         "files": ["ids.py"]}],
        tests={"9.1": ["tests/test_app.py::test_x"], "9.2": ["tests/test_app.py::test_x"]})))
    env = dict(os.environ, PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, "-m", "dokima.fence", base, str(plan)], cwd=tmp_path, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"the fence failed: {r.stderr}"
    return r.stdout.split()


def test_the_fence_undoes_files_no_criterion_lists(record_property, tmp_path):
    """The fence undoes changes to files no criterion lists, keeping listed ones.

    Builds a temp repo, changes a file each criterion lists and one no criterion lists, then runs the fence on a plan
    with no scope field. The listed changes must survive; the other is put back and named as dropped. Proves 666.3.
    """
    record_property("proves", "666.3")
    work = tmp_path / "repo"
    work.mkdir()
    base = repo(work)
    (work / "app.py").write_text("x = 2\n")
    (work / "ids.py").write_text("z = 2\n")
    (work / "other.py").write_text("y = 2\n")
    dropped = run_fence(work, base)
    assert (work / "app.py").read_text() == "x = 2\n", "666.3: the change to a file a criterion lists was undone"
    assert (work / "ids.py").read_text() == "z = 2\n", (
        "666.3: the change to a file only a non-functional requirement lists was undone")
    assert (work / "other.py").read_text() == "y = 1\n", "666.3: the change to a file no criterion lists survived"
    assert dropped == ["other.py"], f"666.3: the fence should name only other.py as dropped; it named {dropped}"


def test_the_fence_removes_a_new_file_no_criterion_lists(record_property, tmp_path):
    """The fence removes a new file no criterion lists, keeping listed changes.

    Builds a temp repo, changes a listed file and adds a new unlisted one, then runs the fence on a plan with no scope
    field. Proves 666.3.
    """
    record_property("proves", "666.3")
    work = tmp_path / "repo"
    work.mkdir()
    base = repo(work)
    (work / "app.py").write_text("x = 2\n")
    (work / "stray.py").write_text("s = 1\n")
    dropped = run_fence(work, base)
    assert (work / "app.py").read_text() == "x = 2\n", "666.3: the change to a file a criterion lists was undone"
    assert not (work / "stray.py").exists(), "666.3: a new file no criterion lists survived the fence"
    assert dropped == ["stray.py"], f"666.3: the fence should name only stray.py as dropped; it named {dropped}"

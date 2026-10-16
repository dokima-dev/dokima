import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

WORKFLOWS = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows")
PLAN = {"objective": "Slow calls return a job id", "criteria": ["A slow call returns a job id within 20 s", "The job id is unique"],
        "scope": ["dokima/jobs.py"]}
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id instead of timing out.", "user_story": "Slow calls return a job id",
         "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s", "source": "https://github.com/o/r/issues/9",
                                  "no_edge_cases": "a sample criterion", "files": ["dokima/jobs.py"]}],
         "tests": {"9.1": ["tests/test_jobs.py::test_id"]}}
TAGS = {"tests/test_jobs.py::test_id": ["9.1"], "tests/test_jobs.py::test_unique": ["9.2"]}


def write(tmp_path, name, content):
    (tmp_path / name).write_text(content if isinstance(content, str) else json.dumps(content))
    return str(tmp_path)


# 80.2: tests come with the plan, each tagged with a criterion of the plan

def tc(added=None, changed=None, deleted=None):
    return {"added": added if added is not None else dict(TAGS), "changed": changed or {}, "deleted": deleted or {}}


def test_good_plan_with_a_test_per_criterion_passes(record_property):
    record_property("proves", "80.2")
    assert planner.problems("9", dict(PLAN, test_changes={}), ["tests/test_jobs.py"], tc()) == []


def test_criterion_without_a_test_is_rejected(record_property):
    record_property("proves", "80.2")
    bad = planner.problems("9", dict(PLAN, test_changes={}), ["tests/test_jobs.py"], tc({"tests/test_jobs.py::test_id": ["9.1"]}))
    assert bad == ["criterion 9.2 has no test"], f"80.2: got {bad}"


def test_test_for_a_criterion_not_in_the_plan_is_rejected(record_property):
    record_property("proves", "80.2")
    bad = planner.problems("9", dict(PLAN, test_changes={}), ["tests/test_jobs.py"], tc(dict(TAGS, **{"tests/test_jobs.py::test_x": ["9.3", "4.1"]})))
    assert "tests/test_jobs.py::test_x proves 9.3, which is not a criterion of this plan" in bad
    assert "tests/test_jobs.py::test_x proves 4.1, which is not a criterion of this plan" in bad


def test_changes_outside_tests_or_no_tests_are_rejected(record_property):
    record_property("proves", "80.2")
    plan_ = dict(PLAN, test_changes={})
    assert "dokima/jobs.py is outside tests/; the planner may only write tests" in planner.problems("9", plan_, ["tests/t.py", "dokima/jobs.py"], tc())
    assert "the plan came with no tests" in planner.problems("9", plan_, [], tc({}))


def test_tags_are_read_from_each_test(record_property):
    record_property("proves", "80.2")
    src = 'def test_a(record_property):\n    record_property("proves", "9.1")\n\ndef test_b(record_property):\n    record_property("proves", "9.2")\n'
    assert {n: keys for n, (_, keys) in planner.test_functions(src).items()} == {"test_a": ["9.1"], "test_b": ["9.2"]}


def test_changed_files_counts_committed_and_new_files_since_the_start(record_property, tmp_path, monkeypatch):
    record_property("proves", "80.2")
    git = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout
    git("init", "-q"); git("config", "user.name", "t"); git("config", "user.email", "t@t")
    (tmp_path / "a.py").write_text("x"); git("add", "-A"); git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "tests").mkdir(); (tmp_path / "tests/t1.py").write_text("x"); git("add", "-A"); git("commit", "-qm", "c")
    (tmp_path / "tests/t2.py").write_text("x")
    monkeypatch.chdir(tmp_path)
    assert planner.changed_files(base) == ["tests/t1.py", "tests/t2.py"], "80.2: committed or new test files missed"


# 80.3: the planner ends with a plan; anything else posts nothing (#154: a lone question is no longer a hand-back)

def test_a_plan_is_read_as_a_plan(record_property, tmp_path):
    record_property("proves", "80.3")
    kind, p = planner.read_output(write(tmp_path, "plan.json", STORY))
    assert kind == "plan", "80.3: a plan was not read as a plan"


@pytest.mark.parametrize("files, why", [
    ({"plan.json": "{not json"}, "not valid JSON"),
    ({"plan.json": dict(STORY, acceptance_criteria=[])}, "acceptance_criteria"),
    ({"plan.json": dict(STORY, scope="dokima/jobs.py")}, "scope"),
    ({"plan.json": dict(STORY, user_story=" ")}, "user_story"),
])
def test_garbled_output_is_rejected_with_its_reason(record_property, tmp_path, files, why):
    record_property("proves", "80.3")
    for name, content in files.items():
        write(tmp_path, name, content)
    with pytest.raises(planner.Garbled, match=why):
        planner.read_output(str(tmp_path))


def test_rejected_output_fails_the_run_and_posts_nothing(record_property, tmp_path, capsys):
    record_property("proves", "80.3")
    assert planner.main(["x", "check", "9", write(tmp_path, "question.md", "no question here")]) == 1
    assert "::error title=Planner output rejected::" in capsys.readouterr().out


def test_no_one_line_command_is_cut_short_by_a_yaml_comment(record_property):
    record_property("proves", "80.1")
    for workflow in sorted(os.listdir(WORKFLOWS)):
        for line in open(os.path.join(WORKFLOWS, workflow)):
            value = line.strip()[len("run:"):] if line.strip().startswith("run:") else ""
            assert " #" not in value, f"80.1: in {workflow}, YAML reads everything after ' #' as a comment: {line.strip()}"


# 100.1: the check judges only the tests the planner touched

OLD_FILE = ('def test_a(record_property):\n    record_property("proves", "58.1")\n    assert 1\n\n'
            'def test_b(record_property):\n    record_property("proves", "74.1")\n    assert "old guard"\n')


def test_untouched_older_tests_in_a_touched_file_are_ignored(record_property):
    record_property("proves", "100.1")
    new_file = OLD_FILE + '\n\ndef test_new(record_property):\n    record_property("proves", "9.1")\n'
    got = planner.test_changes(["tests/t.py"], lambda p: OLD_FILE, lambda p: new_file)
    assert got == {"added": {"tests/t.py::test_new": ["9.1"]}, "changed": {}, "deleted": {}}, f"100.1: got {got}"
    plan_ = dict(PLAN, criteria=["one"], test_changes={})
    assert planner.problems("9", plan_, ["tests/t.py"], got) == [], "100.1: untouched older tests were judged"


def test_replay_of_the_first_live_run_on_87(record_property, tmp_path, monkeypatch):
    record_property("proves", "100.1")
    git = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout
    git("init", "-q"); git("config", "user.name", "t"); git("config", "user.email", "t@t")
    (tmp_path / "tests").mkdir(); (tmp_path / "tests/test_card.py").write_text(OLD_FILE)
    git("add", "-A"); git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "tests/test_card.py").write_text(OLD_FILE.replace('"old guard"', '"types"'))
    (tmp_path / "tests/test_guard.py").write_text('def test_bot_issue(record_property):\n    record_property("proves", "87.1")\n')
    monkeypatch.chdir(tmp_path)
    files = planner.changed_files(base)
    got = planner.test_changes([f for f in files if f.endswith(".py")], planner.read_at(base), planner.read_now)
    assert list(got["changed"]) == ["tests/test_card.py::test_b"] and "tests/test_card.py::test_a" not in got["changed"], f"100.1: got {got}"
    plan_ = {"objective": "o", "criteria": ["c"], "non_goals": [], "scope": ["s"],
             "test_changes": {"tests/test_card.py::test_b": "it checked the old guard's exact words"}}
    assert planner.problems("87", plan_, files, got) == [], "100.1: the #87 plan would still be rejected"


# 100.2: older tests may change or go, each with a reason the owner sees

def test_changed_or_deleted_older_test_needs_a_reason(record_property):
    record_property("proves", "100.2")
    touched = tc(changed={"tests/t.py::test_b": (["74.1"], ["74.1"])}, deleted={"tests/t.py::test_c": ["58.2"]})
    bad = planner.problems("9", dict(PLAN, test_changes={}), ["tests/t.py"], touched)
    assert "tests/t.py::test_b is an older test the planner changed or deleted, with no reason in test_changes" in bad
    assert "tests/t.py::test_c is an older test the planner changed or deleted, with no reason in test_changes" in bad
    ok = dict(PLAN, test_changes={"tests/t.py::test_b": "why b", "tests/t.py::test_c": "why c"})
    assert planner.problems("9", ok, ["tests/t.py"], touched) == [], "100.2: reasons given but still rejected"


def test_a_changed_older_test_may_not_take_on_a_stranger_criterion(record_property):
    record_property("proves", "100.2")
    touched = tc(changed={"tests/t.py::test_b": (["74.1"], ["74.1", "61.3"])})
    bad = planner.problems("9", dict(PLAN, test_changes={"tests/t.py::test_b": "why"}), ["tests/t.py"], touched)
    assert any("now proves 61.3" in b for b in bad), f"100.2: got {bad}"


def test_bad_test_changes_shape_is_rejected(record_property, tmp_path):
    record_property("proves", "100.2")
    with pytest.raises(planner.Garbled, match="test_changes"):
        planner.read_output(write(tmp_path, "plan.json", dict(STORY, test_changes={"tests/t.py::test_b": ""})))

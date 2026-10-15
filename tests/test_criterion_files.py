"""Each criterion of a plan lists the code files it changes.

Code can later split and fence work by these files.

Covers #665 (story 1 of #661). Every acceptance criterion and non-functional requirement, in a user story or in a
split's stories, carries a non-empty `files` list. The plan check rejects a criterion with no files, naming it, and
accepts a path that does not exist yet, since the worker creates it. The planner's instructions (plan-grade.md and
planner.md, joined as the planner reads them) say a criterion lists every file its behavior needs and that work which
can be written as code is a criterion like any other.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = "https://github.com/o/r/issues/9"


def instructions():
    """The planner's instructions as one line of text: plan-grade.md, then planner.md, whitespace collapsed."""
    roles = os.path.join(ROOT, "dokima", "roles")
    return " ".join(" ".join(open(os.path.join(roles, f)).read() for f in ("plan-grade.md", "planner.md")).split())


def story(*files):
    """A well-formed user story: one acceptance criterion and one non-functional requirement, each with its files."""
    return {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls hand back a job id.",
            "user_story": "Slow calls return a job id.",
            "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC, "files": list(files[0]),
                                     "no_edge_cases": "a sample criterion"}],
            "non_functional": [{"text": "Job ids never repeat.", "why": "two jobs would share results", "source": SRC,
                                "files": list(files[1]), "no_edge_cases": "a sample criterion"}],
            "tests": {"9.1": ["tests/test_jobs.py::test_id"], "9.2": ["tests/test_jobs.py::test_unique"]}}


def feature(files):
    """A well-formed split of two stories, the second story's only criterion carrying the given files."""
    def one(title, f):
        return {"title": title, "user_story": f"Owners get {title}.", "non_functional": [], "depends_on": [],
                "acceptance_criteria": [{"text": f"{title} works.", "source": SRC, "files": f}]}
    return {"kind": "feature", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "feature": "A split.", "stories": [one("Jobs", ["dokima/jobs.py"]), one("Ids", files)]}


def hand_back(tmp_path, content):
    """Write plan.json into a temp hand-back folder and read it as the planner check does."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def test_each_criterion_carries_its_files(record_property, tmp_path):
    """Each criterion of a plan keeps the list of code files it changes.

    Hands back a story whose acceptance criterion lists two files and whose non-functional requirement lists one, and
    checks the read plan holds each criterion's files, in criterion order, as handed back. Proves 665.1.
    """
    record_property("proves", "665.1")
    kind, p = hand_back(tmp_path, story(["dokima/jobs.py", "dokima/queue.py"], ["dokima/jobs.py"]))
    assert kind == "plan", f"665.1: a well-formed story was read as {kind}"
    assert p.get("files") == [["dokima/jobs.py", "dokima/queue.py"], ["dokima/jobs.py"]], (
        f"665.1: the read plan does not hold each criterion's files in order; it holds {p.get('files')!r}")


@pytest.mark.parametrize("content,names", [
    (lambda: story(["dokima/jobs.py"], ["dokima/jobs.py"]) | {"acceptance_criteria": [
        {"text": "A slow call returns a job id.", "source": SRC, "no_edge_cases": "a sample criterion"}]},
     "acceptance criterion 1"),
    (lambda: story([], ["dokima/ids.py"]), "acceptance criterion 1"),
    (lambda: story(["dokima/jobs.py"], []), "non-functional requirement 1"),
    (lambda: story(["dokima/jobs.py"], ["dokima/jobs.py"]) | {"non_functional": [
        {"text": "Job ids never repeat.", "why": "two jobs would share results", "source": SRC,
         "files": "dokima/ids.py", "no_edge_cases": "a sample criterion"}]},
     "non-functional requirement 1"),
    (lambda: feature([]), "story 2: acceptance criterion 1"),
])
def test_a_criterion_with_no_files_is_rejected_by_name(record_property, tmp_path, content, names):
    """The plan check rejects a plan where a criterion lists no file, naming that criterion.

    Hands back plans whose one criterion has no files field, an empty list, or a bare string instead of a list, in a
    story's criteria, its non-functional requirements and a split's story. Each must be rejected with a reason naming
    that criterion and the files. The same plans with files listed are accepted, so the check is not a blanket refusal. Proves 665.2.
    """
    record_property("proves", "665.2")
    assert hand_back(tmp_path, story(["dokima/jobs.py"], ["dokima/jobs.py"]))[0] == "plan", (
        "665.2: a story whose every criterion lists its files was rejected")
    assert hand_back(tmp_path, feature(["dokima/ids.py"]))[0] == "feature", (
        "665.2: a split whose every criterion lists its files was rejected")
    try:
        hand_back(tmp_path, content())
    except planner.Garbled as e:
        reason = str(e)
    else:
        pytest.fail(f"665.2: a plan where {names} lists no file was accepted")
    assert names in reason and "file" in reason, (
        f"665.2: the rejection does not name {names!r} and its missing files: {reason}")


def test_a_file_that_does_not_exist_yet_is_accepted(record_property, tmp_path):
    """The plan check accepts a criterion listing a file that does not exist yet.

    Hands back a story whose criterion lists a path no repo holds, and checks the plan is accepted with that path kept
    as the criterion's file, so the worker can create it. Proves 665.3.
    """
    record_property("proves", "665.3")
    new = "dokima/not_written_yet_665.py"
    assert not os.path.exists(os.path.join(ROOT, new)), "665.3: the sample new file already exists"
    kind, p = hand_back(tmp_path, story([new], [new]))
    assert kind == "plan", f"665.3: a story listing a new file was read as {kind}"
    assert (p.get("files") or [None])[0] == [new], (
        f"665.3: the plan did not keep the new file {new} as its criterion's file: {p.get('files')!r}")


def test_instructions_say_list_every_file_never_just_one(record_property):
    """The planner's instructions say a criterion lists every file its behavior needs, never just one.

    Reads the planner's instructions as the planner gets them and looks for that rule in the owner's own words. Proves 665.4.
    """
    record_property("proves", "665.4")
    text = instructions()
    assert "every file its behavior needs, never just one" in text, (
        "665.4: the planner's instructions never say a criterion lists every file its behavior needs, never just one")


def test_instructions_say_code_work_is_a_criterion(record_property):
    """The planner's instructions say work written as code is a criterion like any other.

    Reads the planner's instructions as the planner gets them and looks for that rule in the owner's own words. Proves 665.5.
    """
    record_property("proves", "665.5")
    text = instructions()
    assert "can be written as code" in text and "a criterion like any other" in text, (
        "665.5: the planner's instructions never say work that can be written as code is a criterion like any other")

"""Code groups a plan's criteria into stories by the code files they share.

Covers #667 (story 3 of #661). Criteria that share a code file, directly or through another criterion, belong to one
story; criteria with no code file in common belong to separate stories. Markdown files never join criteria, and edge
cases never change the groups. The plan check holds every plan to these groups: a user story whose criteria form more
than one group is rejected with a reason saying "separate stories", and a split that puts criteria sharing a code file
into different stories is rejected with a reason naming that file and saying "same story". No count of criteria or
stories refuses a plan any more, and the instructions no longer state the old count rules.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = "https://github.com/o/r/issues/9"


def crit(text, files, edge=None):
    """One acceptance criterion changing these files, with its edge case test if given."""
    c = {"text": text, "source": SRC, "files": list(files)}
    if edge:
        c["edge_cases"] = [{"case": f"{text} on empty input", "test": edge}]
    else:
        c["no_edge_cases"] = "a sample criterion"
    return c


def story(*criteria):
    """A well-formed user story of issue #9 holding these criteria, each with its test."""
    tests = {}
    for k, c in enumerate(criteria, 1):
        tests[f"9.{k}"] = [c["edge_cases"][0]["test"]] if c.get("edge_cases") else [f"tests/test_jobs.py::test_{k}"]
    return {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "user_story": "Slow calls return a job id.", "acceptance_criteria": list(criteria), "non_functional": [],
            "scope": sorted({f for c in criteria for f in c["files"]}), "tests": tests}


def feature(*stories):
    """A well-formed split of issue #9, one story per list of criteria given."""
    return {"kind": "feature", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "feature": "A split.",
            "stories": [{"title": f"Story {n}", "user_story": f"Owners get part {n}.", "acceptance_criteria": list(cs),
                         "non_functional": [], "depends_on": []} for n, cs in enumerate(stories, 1)]}


def hand_back(tmp_path, content):
    """Write plan.json into a temp hand-back folder and read it as the planner check does."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def rejected(tmp_path, content):
    """The reason the plan check rejects the plan, or None when it is accepted."""
    try:
        hand_back(tmp_path, content)
    except planner.Garbled as e:
        return str(e)
    return None


def test_criteria_sharing_a_code_file_are_put_in_the_same_story(record_property, tmp_path):
    """Criteria sharing a code file must sit in one story, even through a third criterion.

    A user story whose two criteria share `dokima/jobs.py` is accepted. A split putting those two criteria in different
    stories is rejected, naming `dokima/jobs.py` and saying "same story". A split where criterion A changes `x.py`,
    B changes `x.py` and `y.py`, and C (in another story) changes `y.py` is rejected naming `y.py`, since C joins A
    through B. The same split with C on its own file is accepted, so the check is not a blanket refusal. Proves 667.1.
    """
    record_property("proves", "667.1")
    a, b = crit("A slow call returns a job id.", ["dokima/jobs.py"]), crit("Job ids never repeat.", ["dokima/jobs.py"])
    assert rejected(tmp_path, story(a, b)) is None, "667.1: a story whose criteria share a code file was rejected"
    why = rejected(tmp_path, feature([a], [b]))
    assert why and "dokima/jobs.py" in why and "same story" in why, (
        f"667.1: a split with two criteria sharing dokima/jobs.py in different stories was not rejected naming the "
        f"file and saying 'same story': {why!r}")
    x, xy = crit("A runs.", ["dokima/x.py"]), crit("B runs.", ["dokima/x.py", "dokima/y.py"])
    why = rejected(tmp_path, feature([x, xy], [crit("C runs.", ["dokima/y.py"])]))
    assert why and "dokima/y.py" in why and "same story" in why, (
        f"667.1: criteria joined through a third criterion were allowed in different stories: {why!r}")
    assert rejected(tmp_path, feature([x, xy], [crit("C runs.", ["dokima/z.py"])])) is None, (
        "667.1: a split whose stories share no code file was rejected")


def test_criteria_with_no_code_file_in_common_become_separate_stories(record_property, tmp_path):
    """Criteria with no code file in common must sit in separate stories.

    A user story whose two criteria change different code files is rejected with a reason saying "separate stories";
    so is one story of a split holding two such criteria. The same two criteria handed back as a split, one per story,
    are accepted. Proves 667.2.
    """
    record_property("proves", "667.2")
    a, b = crit("A slow call returns a job id.", ["dokima/jobs.py"]), crit("Status shows.", ["dokima/status.py"])
    why = rejected(tmp_path, story(a, b))
    assert why and "separate stories" in why, (
        f"667.2: a story whose criteria share no code file was not rejected saying 'separate stories': {why!r}")
    why = rejected(tmp_path, feature([a, b], [crit("C runs.", ["dokima/c.py"])]))
    assert why and "separate stories" in why, (
        f"667.2: a split's story holding criteria with no code file in common was accepted: {why!r}")
    assert rejected(tmp_path, feature([a], [b])) is None, (
        "667.2: a split with one story per group of criteria was rejected")


def test_no_count_of_criteria_or_stories_refuses_a_plan(record_property, tmp_path, monkeypatch):
    """No count of criteria or stories refuses a plan, and the count rules are gone.

    A user story of 6 criteria on one code file is accepted (today refused for holding over 5). A story of a parent,
    whose criteria form two file groups, hands back a split of two stories and is accepted (today refused as never
    splitting again). The planner's and reviewer's instructions, the rules and the reviewer's size message no longer
    say "1 to 5 criteria", "criteria / 5", "never splits again" or "more than five criteria". Proves 667.3.
    """
    record_property("proves", "667.3")
    six = [crit(f"Rule {k} holds.", ["dokima/jobs.py"]) for k in range(1, 7)]
    assert rejected(tmp_path, story(*six)) is None, (
        f"667.3: a story of 6 criteria sharing one code file was refused: {rejected(tmp_path, story(*six))!r}")
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "parent.json").write_text(json.dumps({"number": 330}))
    for k, v in {"PACK": str(pack), "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com"}.items():
        monkeypatch.setenv(k, v)
    mine = "https://github.com/o/r/issues/331"
    split = feature([dict(crit("A runs.", ["dokima/a.py"]), source=mine)], [dict(crit("B runs.", ["dokima/b.py"]), source=mine)])
    (tmp_path / "plan.json").write_text(json.dumps(split))
    try:
        kind = planner.read_output(str(tmp_path), 331)[0]
    except planner.Garbled as e:
        pytest.fail(f"667.3: a story of a parent splitting by its files was refused: {e}")
    assert kind == "feature", f"667.3: a story of a parent splitting by its files was read as {kind}"
    texts = {f: open(os.path.join(ROOT, f)).read() for f in (
        "dokima/roles/planner.md", "dokima/roles/plan-grade.md", "dokima/roles/reviewer.md", "rules/splitting.md")}
    texts["the reviewer's size message"] = " ".join(agent.problems_size({"verdict": "approve"}))
    rules = ("1 to 5 criteria", "criteria / 5", "never splits again", "more than five criteria")
    stale = [f"{where}: {rule!r}" for where, text in texts.items() for rule in rules if rule in " ".join(text.split())]
    assert not stale, "667.3: the old count rules are still stated in " + "; ".join(stale)


def test_criteria_sharing_only_a_markdown_file_stay_in_separate_stories(record_property, tmp_path):
    """Two criteria sharing only a markdown file stay in separate stories.

    A user story whose two criteria share only `rules/splitting.md`, each with its own code file, is rejected saying
    "separate stories"; so is one whose two criteria list only that markdown file. The same two criteria handed back
    as a split, one per story, are accepted. Proves 667.4.
    """
    record_property("proves", "667.4")
    a = crit("A slow call returns a job id.", ["dokima/jobs.py", "rules/splitting.md"])
    b = crit("Status shows.", ["dokima/status.py", "rules/splitting.md"])
    why = rejected(tmp_path, story(a, b))
    assert why and "separate stories" in why, (
        f"667.4: criteria sharing only a markdown file were grouped into one story: {why!r}")
    why = rejected(tmp_path, story(crit("Docs say A.", ["README.md"]), crit("Docs say B.", ["README.md"])))
    assert why and "separate stories" in why, (
        f"667.4: criteria listing only the same markdown file were grouped into one story: {why!r}")
    assert rejected(tmp_path, feature([a], [b])) is None, (
        "667.4: criteria sharing only a markdown file were refused in separate stories")


def test_edge_cases_stay_under_their_criterion_and_never_change_the_groups(record_property, tmp_path):
    """Edge cases stay under their criterion and never join criteria into one story.

    Two criteria on different code files, whose edge cases are covered by tests in the same test file, are rejected
    as one user story saying "separate stories". Handed back as a split, one per story, they are accepted, and each
    story still holds its own criterion's edge case. Proves 667.5.
    """
    record_property("proves", "667.5")
    a = crit("A slow call returns a job id.", ["dokima/jobs.py"], edge="tests/test_jobs.py::test_1")
    b = crit("Status shows.", ["dokima/status.py"], edge="tests/test_jobs.py::test_2")
    why = rejected(tmp_path, story(a, b))
    assert why and "separate stories" in why, (
        f"667.5: edge cases in one test file joined criteria with no code file in common: {why!r}")
    kind, text = hand_back(tmp_path, feature([a], [b]))
    stories = json.loads(text)["stories"]
    assert [s["acceptance_criteria"][0]["edge_cases"] for s in stories] == [a["edge_cases"], b["edge_cases"]], (
        f"667.5: the split's stories do not keep each criterion's own edge case: {stories!r}")

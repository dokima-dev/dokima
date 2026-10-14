"""Code groups a plan's criteria into stories by the code files they share.

Covers #667 (story 3 of #661). `planner.story_groups(criteria)` computes the stories from a list of criteria, each with
its `files`: it returns one list per story, each the 0-based indexes of its criteria in ascending order, the stories in
the order of their first criterion. Criteria that share a code file, directly or through another criterion, are one
story; criteria with no code file in common are separate stories. Files ending in `.md` never join criteria, and edge
cases never change the groups. The plan check holds every plan to code's groups: a user story, or one story of a split,
whose criteria form more than one group is rejected with a reason saying "separate stories"; a split that puts criteria
of one group into different stories is rejected with a reason naming the shared file and saying "same story". No count
of criteria or stories refuses a plan any more, and the instructions no longer state the old count rules.
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


def nfr(text, files):
    """One non-functional requirement changing these files."""
    return dict(crit(text, files), why="It matters.")


def story(*criteria, nfrs=()):
    """A well-formed user story of issue #9 holding these criteria and requirements."""
    tests = {}
    for k, c in enumerate([*criteria, *nfrs], 1):
        tests[f"9.{k}"] = [c["edge_cases"][0]["test"]] if c.get("edge_cases") else [f"tests/test_jobs.py::test_{k}"]
    return {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "user_story": "Slow calls return a job id.", "acceptance_criteria": list(criteria),
            "non_functional": list(nfrs), "scope": sorted({f for c in [*criteria, *nfrs] for f in c["files"]}),
            "tests": tests}


def feature(*stories):
    """A well-formed split of issue #9, one story per list of criteria given.

    A story given as a pair (criteria, requirements) also holds those non-functional requirements."""
    def parts(cs):
        return cs if isinstance(cs, tuple) else (cs, [])
    return {"kind": "feature", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "feature": "A split.",
            "stories": [{"title": f"Story {n}", "user_story": f"Owners get part {n}.",
                         "acceptance_criteria": list(parts(cs)[0]), "non_functional": list(parts(cs)[1]),
                         "depends_on": []} for n, cs in enumerate(stories, 1)]}


def hand_back(tmp_path, content):
    """Write plan.json into a temp hand-back folder and read it as the planner check does."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def groups(criteria, k):
    """Code's stories for these criteria, failing under criterion K when code cannot group them."""
    assert hasattr(planner, "story_groups"), f"{k}: code has no way to group criteria into stories by their files"
    return planner.story_groups(criteria)


def rejected(tmp_path, content):
    """The reason the plan check rejects the plan, or None when it is accepted."""
    try:
        hand_back(tmp_path, content)
    except planner.Garbled as e:
        return str(e)
    return None


def test_criteria_sharing_a_code_file_are_put_in_the_same_story(record_property, tmp_path):
    """Code puts criteria sharing a code file in one story, even through a third criterion.

    Code's groups of A (`x.py`), B (`x.py`, `y.py`) and C (`y.py`) are one story, since C joins A through B. A user
    story holding all three is accepted. A split putting C in another story is rejected naming `dokima/y.py` and saying
    "same story". A non-functional requirement counts as a criterion: one sharing `dokima/x.py` with A is grouped with
    it and accepted beside it in one user story; a split putting a requirement on `dokima/d.py` and `dokima/x.py` in
    another story than A is rejected naming `dokima/x.py`.
    Proves 667.1.
    """
    record_property("proves", "667.1")
    a, b = crit("A runs.", ["dokima/x.py"]), crit("B runs.", ["dokima/x.py", "dokima/y.py"])
    c = crit("C runs.", ["dokima/y.py"])
    got = groups([a, b, c], "667.1")
    assert got == [[0, 1, 2]], f"667.1: code did not put criteria sharing a code file in one story: {got!r}"
    why = rejected(tmp_path, story(a, b, c))
    assert why is None, f"667.1: a story whose criteria share code files was rejected: {why!r}"
    why = rejected(tmp_path, feature([a, b], [c]))
    assert why and "dokima/y.py" in why and "same story" in why, (
        f"667.1: a split putting criteria joined by dokima/y.py in different stories was not rejected naming the "
        f"file and saying 'same story': {why!r}")
    n = nfr("Nothing leaks.", ["dokima/x.py"])
    got = groups([a, n], "667.1")
    assert got == [[0, 1]], f"667.1: code did not put a requirement sharing a code file with a criterion in one story: {got!r}"
    why = rejected(tmp_path, story(a, nfrs=[n]))
    assert why is None, f"667.1: a story whose criterion and requirement share a code file was rejected: {why!r}"
    d, n2 = crit("D runs.", ["dokima/d.py"]), nfr("D leaks nothing.", ["dokima/d.py", "dokima/x.py"])
    why = rejected(tmp_path, feature([a], ([d], [n2])))
    assert why and "dokima/x.py" in why and "same story" in why, (
        f"667.1: a split putting a requirement apart from the criterion it shares dokima/x.py with was not rejected "
        f"naming the file and saying 'same story': {why!r}")


def test_criteria_with_no_code_file_in_common_become_separate_stories(record_property, tmp_path):
    """Criteria with no code file in common go in separate stories, whatever their edge cases.

    Code's groups of two criteria on different code files are two stories, even when their edge cases are covered by
    tests in one test file. As one user story they are rejected saying "separate stories"; so is one story of a split
    holding both. Handed back as a split, one per story, they are accepted, each story keeping its own criterion's edge
    case. A markdown file is not a code file: two criteria sharing only `rules/splitting.md`, each with its own code
    file, are two stories, and so are two listing only `README.md`; as one user story both pairs are rejected saying
    "separate stories", and the first pair as a split is accepted. Proves 667.2.
    """
    record_property("proves", "667.2")
    a = crit("A slow call returns a job id.", ["dokima/jobs.py"], edge="tests/test_jobs.py::test_1")
    b = crit("Status shows.", ["dokima/status.py"], edge="tests/test_jobs.py::test_2")
    got = groups([a, b], "667.2")
    assert got == [[0], [1]], f"667.2: code did not put criteria with no code file in common in separate stories: {got!r}"
    why = rejected(tmp_path, story(a, b))
    assert why and "separate stories" in why, (
        f"667.2: a story whose criteria share no code file was not rejected saying 'separate stories': {why!r}")
    why = rejected(tmp_path, feature([a, b], [crit("C runs.", ["dokima/c.py"])]))
    assert why and "separate stories" in why, (
        f"667.2: a split's story holding criteria with no code file in common was accepted: {why!r}")
    kind, text = hand_back(tmp_path, feature([a], [b]))
    stories = json.loads(text)["stories"]
    assert [s["acceptance_criteria"][0]["edge_cases"] for s in stories] == [a["edge_cases"], b["edge_cases"]], (
        f"667.2: the split's stories do not keep each criterion's own edge case: {stories!r}")
    a = crit("A slow call returns a job id.", ["dokima/jobs.py", "rules/splitting.md"])
    b = crit("Status shows.", ["dokima/status.py", "rules/splitting.md"])
    docs = [crit("Docs say A.", ["README.md"]), crit("Docs say B.", ["README.md"])]
    for pair in ([a, b], docs):
        got = groups(pair, "667.2")
        assert got == [[0], [1]], f"667.2: criteria sharing only a markdown file were put in one story: {got!r}"
        why = rejected(tmp_path, story(*pair))
        assert why and "separate stories" in why, (
            f"667.2: criteria sharing only a markdown file were accepted as one story: {why!r}")
    assert rejected(tmp_path, feature([a], [b])) is None, (
        "667.2: criteria sharing only a markdown file were refused in separate stories")


def test_no_count_of_criteria_or_stories_refuses_a_plan(record_property, tmp_path, monkeypatch):
    """No count of criteria or stories refuses a plan; an empty story still is.

    A user story of 6 criteria on one code file is accepted (today refused for holding over 5), and so is the same
    story when the issue is already a story of a parent. A split of 7 stories of one criterion each, on 7 code files,
    is accepted. A split with a story of no criteria is still rejected. Proves 667.3.
    """
    record_property("proves", "667.3")
    six = [crit(f"Rule {k} holds.", ["dokima/jobs.py"]) for k in range(1, 7)]
    why = rejected(tmp_path, story(*six))
    assert why is None, f"667.3: a story of 6 criteria sharing one code file was refused: {why!r}"
    seven = [[crit(f"Part {k} runs.", [f"dokima/part{k}.py"])] for k in range(1, 8)]
    why = rejected(tmp_path, feature(*seven))
    assert why is None, f"667.3: a split of 7 stories, one per code file, was refused: {why!r}"
    empty = feature([crit("A runs.", ["dokima/a.py"])], [])
    assert rejected(tmp_path, empty), "667.3: a split with a story of no criteria was accepted"
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "parent.json").write_text(json.dumps({"number": 330}))
    for k, v in {"PACK": str(pack), "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com"}.items():
        monkeypatch.setenv(k, v)
    mine = "https://github.com/o/r/issues/331"
    nested = story(*[dict(c, source=mine) for c in six])
    nested["tests"] = {k.replace("9.", "331."): v for k, v in nested["tests"].items()}
    (tmp_path / "plan.json").write_text(json.dumps(nested))
    try:
        kind = planner.read_output(str(tmp_path), 331)[0]
    except planner.Garbled as e:
        pytest.fail(f"667.3: a story of a parent holding 6 criteria on one code file was refused: {e}")
    assert kind == "plan", f"667.3: a story of a parent holding 6 criteria was read as {kind}"


def test_the_old_count_rules_are_gone_from_the_instructions(record_property):
    """The planner's and reviewer's instructions and the rules no longer state the old count rules.

    Reads the planner's, plan grade's and reviewer's instructions, the splitting rules and the reviewer's size message,
    and checks none still says "1 to 5 criteria", "criteria / 5", "more than five criteria", "at most 5" or "at most five
    criteria". Proves 667.4.
    """
    record_property("proves", "667.4")
    texts = {f: open(os.path.join(ROOT, f)).read() for f in (
        "dokima/roles/planner.md", "dokima/roles/plan-grade.md", "dokima/roles/reviewer.md", "rules/splitting.md")}
    texts["the reviewer's size message"] = " ".join(agent.problems_size({"verdict": "approve"}))
    rules = ("1 to 5 criteria", "criteria / 5", "more than five criteria", "at most 5", "at most five criteria")
    stale = [f"{where}: {rule!r}" for where, text in texts.items() for rule in rules if rule in " ".join(text.split())]
    assert not stale, "667.4: the old count rules are still stated in " + "; ".join(stale)


def test_a_story_of_a_split_never_splits_again(record_property, tmp_path, monkeypatch):
    """A story of a split whose criteria share no code file is refused, not split.

    In an issue that is already a story of a parent, a user story of two criteria on different code files is rejected
    saying "never splits again", and so is the same pair handed back as a split of two stories. The same story with
    both criteria on one code file is accepted. Proves 667.5.
    """
    record_property("proves", "667.5")
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "parent.json").write_text(json.dumps({"number": 330}))
    for k, v in {"PACK": str(pack), "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com"}.items():
        monkeypatch.setenv(k, v)
    mine = "https://github.com/o/r/issues/331"

    def nested(content):
        """Why the check refuses this plan of issue 331, a story of 330, or None."""
        content = json.loads(json.dumps(content).replace(SRC, mine).replace('"9.', '"331.'))
        (tmp_path / "plan.json").write_text(json.dumps(content))
        try:
            planner.read_output(str(tmp_path), 331)
        except planner.Garbled as e:
            return str(e)
        return None

    a, b = crit("A runs.", ["dokima/a.py"]), crit("B runs.", ["dokima/b.py"])
    why = nested(story(a, b))
    assert why and "never splits again" in why, (
        f"667.5: a story of a split whose criteria share no code file was not refused saying 'never splits again': "
        f"{why!r}")
    why = nested(feature([a], [b]))
    assert why and "never splits again" in why, (
        f"667.5: a story of a split handed back as a split was not refused saying 'never splits again': {why!r}")
    why = nested(story(a, crit("B runs.", ["dokima/a.py"])))
    assert why is None, f"667.5: a story of a split whose criteria share a code file was refused: {why!r}"

"""User: The plan check locks the owner's tests and holds new tests to one shape.

Agent: Every test here runs the check the way the agent workflow runs it, `python3 -m dokima.planner check 9 OUT`,
through `planner.main`, inside a temp git repo built like a real branch: a starting commit (PLANNER_BASE) holding one
older test in the old docstring shape, then a commit by the owner (author "Owner", not `dokima-runtime[bot]`) adding
`tests/test_owner.py::test_owner_id`, at which the planner's run starts (PLANNER_RUN_BASE). The planner then writes its
own tests on top, uncommitted. A good plan passes (exit 0); each broken one fails (exit 1) and its reason, saved to
OUT/rejected.txt, is read back and split on "; " into one problem each, so a test can check one problem names both
the test and what is wrong with it. Word caps: the User, Verified by and Edge lines each hold 15 words, not counting
their label, the cap the owner set for a docstring's first line in #239, with that issue's 20% leeway (rejected past
18); the Agent paragraph has no cap. Issue #707.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ISSUE = "https://github.com/o/r/issues/9"
OWNER_TEST = "tests/test_owner.py::test_owner_id"
OLD = "tests/test_old.py::test_old"

# An older test in the old shape: one summary line, no User, Verified by or Agent part.
OLD_TESTS = ('def test_old(record_property):\n    """An older test, already in the repo."""\n'
             '    record_property("proves", "50.1")\n    assert True\n')


def doc(user="A slow call returns a job id.", verified="running the job code and checking the id it returns.",
        edge=None, agent="Proves 9.2. Calls the job code and fails while it does not exist yet.", head=None):
    """A test docstring in the new shape; pass None to leave a part out."""
    lines = [] if head is None else [head]
    lines += [f"User: {user}"] if user is not None else []
    lines += [f"Verified by: {verified}"] if verified is not None else []
    lines += [f"Edge: {edge}"] if edge is not None else []
    if agent is not None:
        lines += ["", f"Agent: {agent}"]
    return '    """' + "\n    ".join(lines) + '\n    """\n'


def fn_src(name, key, docstring=None, body=None):
    """One test function that fails today, with the given docstring (the good shape by default)."""
    docstring = docstring if docstring is not None else doc(agent=f"Proves {key}. Fails until the feature exists.")
    body = body or f'    assert False, "{key}: the feature is missing"\n'
    return f'\n\ndef {name}(record_property):\n{docstring}    record_property("proves", "{key}")\n{body}'


FILE_DOC = '"""User: Sample tests for slow calls.\n\nAgent: Each test fails until the job code exists.\n"""\n'
OWNER_FILE = FILE_DOC + fn_src("test_owner_id", "9.1")
PLANNER_FILE = FILE_DOC + fn_src("test_unique", "9.2")

PLAN = {"kind": "user_story", "title": "Slow calls hand back a job id",
        "summary": "Slow calls hand back a job id instead of timing out.", "user_story": "Slow calls return a job id.",
        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": ISSUE, "no_edge_cases": "a sample",
                                 "files": ["dokima/jobs.py"]},
                                {"text": "Job ids never repeat.", "source": ISSUE, "no_edge_cases": "a sample",
                                 "files": ["dokima/jobs.py"]}],
        "non_functional": [],
        "tests": {"9.1": [OWNER_TEST], "9.2": ["tests/test_jobs.py::test_unique"]},
        "test_changes": {}}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A temp branch holding the owner's test; returns a function that runs the check.

    The returned function takes the planner's test files (path -> text, written into the repo uncommitted) and the
    plan, and returns (exit code, list of problems). The owner's commit is authored by "Owner"; the starting commit is
    authored by someone else, before PLANNER_BASE, so it is not on the branch.
    """
    root, out = tmp_path / "repo", tmp_path / "out"
    root.mkdir()
    out.mkdir()
    git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, text=True).stdout
    git("init", "-q")
    git("config", "user.name", "Main")
    git("config", "user.email", "main@example.com")
    (root / "tests").mkdir()
    (root / "tests" / "test_old.py").write_text(OLD_TESTS)
    git("add", "-A")
    git("commit", "-qm", "base")
    monkeypatch.setenv("PLANNER_BASE", git("rev-parse", "HEAD").strip())
    (root / "tests" / "test_owner.py").write_text(OWNER_FILE)
    git("add", "-A")
    git("-c", "user.name=Owner", "-c", "user.email=owner@example.com", "commit", "-qm", "owner: my test")
    monkeypatch.setenv("PLANNER_RUN_BASE", git("rev-parse", "HEAD").strip())
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.chdir(root)

    def run(files, plan, crit):
        for old in out.iterdir():
            old.unlink()
        for path, text in files.items():
            if text is None:
                os.remove(path)
            else:
                with open(path, "w") as f:
                    f.write(text)
        (out / "plan.json").write_text(json.dumps(plan))
        try:
            rc = planner.main(["x", "check", "9", str(out)])
        except Exception as e:  # a crash posts nothing on the issue
            pytest.fail(f"{crit}: the check crashed with {type(e).__name__}: {e}, instead of rejecting with a reason")
        rejected = out / "rejected.txt"
        return rc, (rejected.read_text().split("; ") if rejected.exists() else [])
    return run


def naming(problems, *parts):
    """The problems that name every one of the given parts (compared lower case)."""
    return [p for p in problems if all(x.lower() in p.lower() for x in parts)]


def good(repo, crit):
    """Run the check on the good plan and fail unless it passes."""
    rc, why = repo({"tests/test_jobs.py": PLANNER_FILE}, PLAN, crit)
    assert rc == 0 and not why, f"{crit}: a good plan that keeps the owner's test unchanged was rejected: {why!r}"


def test_a_plan_that_changes_the_owners_test_is_rejected_naming_it(record_property, repo):
    """User: A plan that changes a test the owner committed is rejected, naming that test.
    Verified by: running the real plan check on a temp branch after editing the owner's test.

    Agent: Proves 707.1. First checks the good plan, which leaves `tests/test_owner.py` as the owner committed it,
    passes. Then the planner rewrites the owner's test body (a different assertion message) and still files it under
    9.1; the check must fail with a problem that names `test_owner_id` and says it was changed.
    """
    record_property("proves", "707.1")
    good(repo, "707.1")
    changed = FILE_DOC + fn_src("test_owner_id", "9.1", body='    assert False, "9.1: rewritten by the planner"\n')
    rc, why = repo({"tests/test_jobs.py": PLANNER_FILE, "tests/test_owner.py": changed}, PLAN, "707.1")
    assert rc == 1, "707.1: a plan that changes a test the owner committed was accepted"
    assert naming(why, "test_owner_id", "chang"), \
        f"707.1: no problem names the owner's test test_owner_id and says the plan changed it: {why!r}"


def test_a_plan_that_deletes_the_owners_test_is_rejected_naming_it(record_property, repo):
    """User: A plan that deletes a test the owner committed is rejected, naming that test.
    Verified by: running the real plan check on a temp branch after removing the owner's test.

    Agent: Proves 707.2. First checks the good plan passes. Then the planner deletes `test_owner_id` from
    `tests/test_owner.py`, proving 9.1 with its own new test instead, so nothing else is wrong; the check must fail with
    a problem that names `test_owner_id` and says it was deleted.
    """
    record_property("proves", "707.2")
    good(repo, "707.2")
    plan = json.loads(json.dumps(PLAN))
    plan["tests"]["9.1"] = ["tests/test_jobs.py::test_id"]
    files = {"tests/test_jobs.py": PLANNER_FILE + fn_src("test_id", "9.1"), "tests/test_owner.py": FILE_DOC}
    rc, why = repo(files, plan, "707.2")
    assert rc == 1, "707.2: a plan that deletes a test the owner committed was accepted"
    assert naming(why, "test_owner_id", "delet"), \
        f"707.2: no problem names the owner's test test_owner_id and says the plan deleted it: {why!r}"


def test_a_plan_that_files_no_criterion_for_the_owners_test_is_rejected_naming_it(record_property, repo):
    """User: A plan filing the owner's test under no criterion is rejected, naming it.
    Verified by: running the real plan check with the owner's test left out of the plan.

    Agent: Proves 707.3. First checks the good plan, which files `test_owner_id` under 9.1, passes. Then the plan
    files 9.1 under the planner's own new test and names `test_owner_id` nowhere in its tests map, leaving the owner's
    file untouched; the check must fail with a problem that names `test_owner_id` and says it has no criterion.
    """
    record_property("proves", "707.3")
    good(repo, "707.3")
    plan = json.loads(json.dumps(PLAN))
    plan["tests"]["9.1"] = ["tests/test_jobs.py::test_id"]
    rc, why = repo({"tests/test_jobs.py": PLANNER_FILE + fn_src("test_id", "9.1")}, plan, "707.3")
    assert rc == 1, "707.3: a plan that files no criterion for a test the owner committed was accepted"
    assert naming(why, "test_owner_id", "criterion"), \
        f"707.3: no problem names the owner's test test_owner_id and says it is filed under no criterion: {why!r}"


def missing_part(repo, crit, part, docstring, changed):
    """Check a test missing one part is rejected, naming it and the part.

    First the good plan passes. Then either a new test `test_unique` or the older `test_old`, rewritten, carries the
    broken docstring; the check must fail with a problem naming that test and the missing part.
    """
    good(repo, crit)
    if changed:
        files = {"tests/test_jobs.py": PLANNER_FILE,
                 "tests/test_old.py": fn_src("test_old", "50.1", docstring, '    assert True\n').lstrip("\n")}
        plan = json.loads(json.dumps(PLAN))
        plan["test_changes"] = {OLD: "rewritten to the new docstring shape"}
        name = "test_old"
    else:
        files = {"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", docstring)}
        plan, name = PLAN, "test_unique"
    rc, why = repo(files, plan, crit)
    kind = "changed" if changed else "new"
    assert rc == 1, f"{crit}: a {kind} test with no {part} part in its docstring was accepted"
    assert naming(why, name, part), f"{crit}: no problem names the {kind} test {name} and its missing {part}: {why!r}"


@pytest.mark.parametrize("changed", [False, True], ids=["new test", "changed older test"])
def test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it(record_property, repo, changed):
    """User: A new or changed test with no User line is rejected, naming the test.
    Verified by: running the real plan check on a new, then a rewritten, test missing it.
    Edge: an older test the planner rewrites is held to the shape like a new one.

    Agent: Proves 707.4. Uses `missing_part`: the docstring keeps its Verified by line and Agent paragraph and drops
    only the User line, so the problem must be the User line, named with the test.
    """
    record_property("proves", "707.4")
    missing_part(repo, "707.4", "User", doc(user=None, head="A slow call returns a job id."), changed)


@pytest.mark.parametrize("changed", [False, True], ids=["new test", "changed older test"])
def test_a_new_or_changed_test_with_no_verified_by_line_is_rejected_naming_it(record_property, repo, changed):
    """User: A new or changed test lacking a Verified by line is rejected, naming it.
    Verified by: running the real plan check on a new, then a rewritten, test missing it.
    Edge: an older test the planner rewrites is held to the shape like a new one.

    Agent: Proves 707.5. Uses `missing_part`: the docstring keeps its User line and Agent paragraph and drops only
    the Verified by line.
    """
    record_property("proves", "707.5")
    missing_part(repo, "707.5", "Verified by", doc(verified=None), changed)


@pytest.mark.parametrize("changed", [False, True], ids=["new test", "changed older test"])
def test_a_new_or_changed_test_with_no_agent_paragraph_is_rejected_naming_it(record_property, repo, changed):
    """User: A new or changed test with no Agent paragraph is rejected, naming the test.
    Verified by: running the real plan check on a new, then a rewritten, test missing it.
    Edge: an older test the planner rewrites is held to the shape like a new one.

    Agent: Proves 707.6. Uses `missing_part`: the docstring keeps its User and Verified by lines, and keeps "Proves
    9.2." in a plain paragraph with no "Agent:" label, so only the Agent paragraph is missing.
    """
    record_property("proves", "707.6")
    docstring = doc(agent=None).replace('\n    """\n', '\n\n    Proves 9.2.\n    """\n')
    missing_part(repo, "707.6", "Agent", docstring, changed)


def test_an_agent_paragraph_of_any_length_that_names_code_passes(record_property, repo):
    """User: A long Agent paragraph that names code passes the check.
    Verified by: running the real plan check on a 300-word Agent paragraph full of code.

    Agent: Proves 707.7. First checks the shape check is live: the same test with its Agent paragraph removed is
    rejected naming it. Then gives `test_unique` an Agent paragraph of about 300 words naming files, functions and code
    spans (`dokima/planner.py`, `problems()`, `tests/test_x.py::test_y`); the check must pass with no reason.
    """
    record_property("proves", "707.7")
    rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(agent=None))}, PLAN, "707.7")
    assert rc == 1 and naming(why, "test_unique", "Agent"), \
        f"707.7: setup: a new test with no Agent paragraph was not rejected naming it, so the shape check is not live: {why!r}"
    long = ("Proves 9.2. " + "Reads `dokima/planner.py`, calls `problems()` and compares `tests/test_x.py::test_y`. " * 30)
    rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(agent=long))}, PLAN, "707.7")
    assert rc == 0 and not why, f"707.7: a test whose Agent paragraph is long and names code was rejected: {why!r}"


def over_cap(repo, crit, label, field):
    """Check a 15-word line passes and a 25-word one is rejected, naming test and count.

    The words counted are those after the label. The good case puts exactly 15 words in the line; the bad case 25,
    past the 20% a text may run over its cap before it is rejected.
    """
    fifteen = " ".join(["word"] * 14) + " end."
    rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(**{field: fifteen},
                    agent="Proves 9.2. A line at its cap."))}, PLAN, crit)
    assert rc == 0 and not why, f"{crit}: a test's {label} line of 15 words, at its cap, was rejected: {why!r}"
    long = " ".join(["word"] * 24) + " end."
    rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(**{field: long},
                    agent="Proves 9.2. A line over its cap."))}, PLAN, crit)
    assert rc == 1, f"{crit}: a test's {label} line of 25 words, over its cap of 15, was accepted"
    assert naming(why, "test_unique", label, "25"), \
        f"{crit}: no problem names test_unique, its {label} line and its count of 25 words: {why!r}"


def test_a_user_line_over_its_cap_is_rejected_naming_the_test_and_count(record_property, repo):
    """User: An overlong User line is rejected, naming the test and its word count.
    Verified by: running the real plan check on a 15-word User line, then a 25-word one.

    Agent: Proves 707.8. Uses `over_cap`: the cap is 15 words after "User:"; 15 passes, 25 must be rejected with a
    problem naming `test_unique`, "User" and 25.
    """
    record_property("proves", "707.8")
    over_cap(repo, "707.8", "User", "user")


def test_a_verified_by_line_over_its_cap_is_rejected_naming_the_test_and_count(record_property, repo):
    """User: An overlong Verified by line is rejected, naming the test and its word count.
    Verified by: running the real plan check on a 15-word Verified by line, then a 25-word one.

    Agent: Proves 707.9. Uses `over_cap`: the cap is 15 words after "Verified by:"; 15 passes, 25 must be rejected
    with a problem naming `test_unique`, "Verified by" and 25.
    """
    record_property("proves", "707.9")
    over_cap(repo, "707.9", "Verified by", "verified")


def test_an_edge_line_over_its_cap_is_rejected_naming_the_test_and_count(record_property, repo):
    """User: An overlong Edge line is rejected, naming the test and its word count.
    Verified by: running the real plan check on a 15-word Edge line, then a 25-word one.
    Edge: a test with no Edge line passes, since the line is optional.

    Agent: Proves 707.10. The good plan's tests carry no Edge line and must pass. Then uses `over_cap`: the cap is 15
    words after "Edge:"; 15 passes, 25 must be rejected with a problem naming `test_unique`, "Edge" and 25.
    """
    record_property("proves", "707.10")
    good(repo, "707.10")
    over_cap(repo, "707.10", "Edge", "edge")


FILE_TEST = fn_src("test_unique", "9.2")


@pytest.mark.parametrize("opening", ["", '"""\n"""\n'], ids=["no docstring", "empty docstring"])
def test_a_new_test_file_with_no_user_line_is_rejected(record_property, repo, opening):
    """User: A new test file whose opening docstring has no user line is rejected.
    Verified by: running the real plan check on a new file with no, then an empty, docstring.
    Edge: the file has no opening docstring at all.

    Agent: Proves 707.11. First checks the good plan, whose `tests/test_jobs.py` opens with a User line and agent
    detail, passes. Then the new file opens with no docstring, or an empty one; its tests are in the good shape, so the
    check must fail with a problem naming `tests/test_jobs.py` and its missing user line.
    """
    record_property("proves", "707.11")
    good(repo, "707.11")
    rc, why = repo({"tests/test_jobs.py": opening + FILE_TEST}, PLAN, "707.11")
    assert rc == 1, "707.11: a new test file whose opening docstring has no user line was accepted"
    assert naming(why, "tests/test_jobs.py", "user"), \
        f"707.11: no problem names tests/test_jobs.py and its missing user line: {why!r}"


def test_a_new_test_file_with_no_agent_detail_is_rejected(record_property, repo):
    """User: A new test file whose opening docstring has no agent detail is rejected.
    Verified by: running the real plan check on a new file whose docstring is one user line.

    Agent: Proves 707.12. First checks the good plan passes. Then `tests/test_jobs.py` opens with only
    "User: Sample tests for slow calls." and nothing after it; the check must fail with a problem naming the file and
    its missing agent detail.
    """
    record_property("proves", "707.12")
    good(repo, "707.12")
    rc, why = repo({"tests/test_jobs.py": '"""User: Sample tests for slow calls."""\n' + FILE_TEST}, PLAN, "707.12")
    assert rc == 1, "707.12: a new test file whose opening docstring has no agent detail was accepted"
    assert naming(why, "tests/test_jobs.py", "agent"), \
        f"707.12: no problem names tests/test_jobs.py and its missing agent detail: {why!r}"


def test_an_older_test_left_unchanged_is_not_held_to_the_new_shape(record_property, repo):
    """User: An older test left unchanged passes without the new docstring shape.
    Verified by: running the real plan check beside an untouched older test in the old shape.

    Agent: Proves 707.13. The repo's `tests/test_old.py::test_old` has only a summary line. First checks the shape
    check is live: a new test with no User line is rejected naming it, and no problem names `test_old`. Then the good
    plan, which leaves `test_old` untouched, must pass.
    """
    record_property("proves", "707.13")
    bad = FILE_DOC + fn_src("test_unique", "9.2", doc(user=None, head="Job ids never repeat."))
    rc, why = repo({"tests/test_jobs.py": bad}, PLAN, "707.13")
    assert rc == 1 and naming(why, "test_unique", "User"), \
        f"707.13: setup: a new test with no User line was not rejected naming it, so the shape check is not live: {why!r}"
    assert not naming(why, "test_old"), f"707.13: the untouched older test test_old was named: {why!r}"
    good(repo, "707.13")


def test_any_plain_sentence_passes_as_a_verified_by_line(record_property, repo):
    """User: Any plain sentence passes as a Verified by line, with no test kinds.
    Verified by: running the real plan check on Verified by lines written in several unrelated ways.

    Agent: Proves 707.14. First checks the shape check is live: a test with no Verified by line is rejected naming it.
    Then, one at a time, `test_unique` carries a Verified by line from a different kind of repo (a web page, a data
    job, a phone app, a hand check); none uses a fixed category word. Each plan must pass with no reason.
    """
    record_property("proves", "707.14")
    rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(verified=None))}, PLAN, "707.14")
    assert rc == 1 and naming(why, "test_unique", "Verified by"), \
        f"707.14: setup: a test with no Verified by line was not rejected naming it, so the shape check is not live: {why!r}"
    for line in ("loading the sign-up page in a headless browser and reading the error it shows.",
                 "feeding last month's sales file through the nightly job and comparing totals.",
                 "tapping through the app on a simulated phone",
                 "Someone reads the report by hand."):
        rc, why = repo({"tests/test_jobs.py": FILE_DOC + fn_src("test_unique", "9.2", doc(verified=line))},
                       PLAN, "707.14")
        assert rc == 0 and not why, f"707.14: the plain Verified by line {line!r} was rejected: {why!r}"

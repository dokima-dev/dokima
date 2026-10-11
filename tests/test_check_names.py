"""The criteria workflow and its checks are named Acceptance criteria, and done-when is gone.

Story 1 of #262. The owner left every check rename, all tests included, to #262, so main's branch rule only changes
once. This story renames only the workflow that holds the criteria checks, from done-whens in done-whens.yml to
Acceptance criteria in acceptance-criteria.yml, and takes the word done-when out of every other place a person reads.
The card and the board start through `workflow_run` by workflow name, so the tests read those names out of card.yml and
board.yml and match them against the workflows the repo really has. One test reads every file in the repo for the old
word; the exceptions are the owner's older "Done when:" plan lines Dokima still reads, and copies of past records in tests/samples.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, checks  # noqa: E402

import test_card_records as tcr  # noqa: E402
import test_start as ts  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
CRITERIA = "Acceptance criteria"
ALL_TESTS, GATE, LIST = "all tests", "Acceptance criteria", "list acceptance criteria"
OLD_WORD = re.compile(r"done[\s_-]*whens?", re.I)


def workflows():
    """Every workflow file of the repo, as {file name: parsed workflow}."""
    out = {}
    for name in sorted(os.listdir(WORKFLOWS)):
        if name.endswith((".yml", ".yaml")):
            out[name] = ts.load_yaml(open(os.path.join(WORKFLOWS, name)).read())
    return out


def job_names(flow):
    """The names GitHub shows for a workflow's jobs, in file order."""
    return [j.get("name") for j in (flow.get("jobs") or {}).values() if isinstance(j, dict)]


def triggers(flow):
    """The events a workflow runs on."""
    on = flow.get("on") or {}
    return set([on] if isinstance(on, str) else on)


def started_by(file_name):
    """The workflow names whose finishing starts the workflow in `file_name` (its workflow_run trigger)."""
    on = workflows()[file_name].get("on") or {}
    listed = (on.get("workflow_run") or {}).get("workflows") or []
    return [listed] if isinstance(listed, str) else list(listed)


def criteria_workflow(k):
    """The workflow in acceptance-criteria.yml, parsed; fails naming criterion k when the file is missing."""
    path = os.path.join(WORKFLOWS, "acceptance-criteria.yml")
    assert os.path.exists(path), (f"{k}: .github/workflows/acceptance-criteria.yml does not exist; the workflow files are "
                                  f"{sorted(workflows())}")
    return ts.load_yaml(open(path).read())


# 291.1: the criteria workflow is named Acceptance criteria, in acceptance-criteria.yml, and still works the same

def test_the_criteria_workflow_is_named_acceptance_criteria_in_its_own_file(record_property):
    """The criteria checks run in a workflow named Acceptance criteria, in acceptance-criteria.yml, working as before.

    Proves 291.1. Reads .github/workflows/acceptance-criteria.yml: its workflow is named Acceptance criteria with no number, it runs on
    pull_request_target and in the merge queue, one job gives each criterion its own check named from the plan, and the
    gate waits on that job and passes only when it succeeded. done-whens.yml is gone, and no other workflow is named
    Acceptance criteria or done-whens. Each criterion's check is still named by its number and words, and the code that
    reruns the checks once a plan is approved never looks for the workflow under its old name: either it reruns every
    check on the head, or the one workflow file it reruns (agent.PLAN_CHECK) is this file."""
    record_property("proves", "291.1")
    flow = criteria_workflow("291.1")
    assert flow.get("name") == CRITERIA, f"291.1: acceptance-criteria.yml's workflow is named {flow.get('name')!r}, not {CRITERIA!r}"
    assert {"pull_request_target", "merge_group"} <= triggers(flow), \
        f"291.1: the Acceptance criteria workflow no longer runs on pull requests and in the merge queue: {sorted(triggers(flow))}"
    jobs = {k: j for k, j in (flow.get("jobs") or {}).items() if isinstance(j, dict)}
    per = [k for k, j in jobs.items() if j.get("name") == "${{ matrix.name }}"]
    assert len(per) == 1, f"291.1: no single job gives each criterion its own check named from the plan: {job_names(flow)}"
    gates = [k for k, j in jobs.items() if j.get("name") == GATE]
    assert len(gates) == 1, f"291.1: the Acceptance criteria workflow has no single gate check {GATE!r}: {job_names(flow)}"
    needs = jobs[gates[0]].get("needs") or []
    assert per[0] in ([needs] if isinstance(needs, str) else needs), \
        f"291.1: the gate does not wait on each criterion's check (needs: {needs})"
    text = open(os.path.join(WORKFLOWS, "acceptance-criteria.yml")).read()
    assert 'if [ -z "$TESTS" ]' in text and 'test "$RESULT" = "success"' in text, \
        "291.1: the gate no longer passes only when every criterion's check passed, or an untested criterion no longer fails"
    assert not os.path.exists(os.path.join(WORKFLOWS, "done-whens.yml")), "291.1: .github/workflows/done-whens.yml is still there"
    others = [f for f, w in workflows().items() if f != "acceptance-criteria.yml" and w.get("name") in (CRITERIA, "done-whens")]
    assert not others, f"291.1: another workflow is still named Acceptance criteria or done-whens: {others}"
    rows = checks.build_matrix(40, tcr.RECS)
    assert [r["name"] for r in rows] == ["40.1 · First thing works", "40.2 · Second thing works", "40.3 · Nothing leaks out"], \
        f"291.1: each criterion's check is no longer named by its number and words: {[r['name'] for r in rows]}"
    rerun = getattr(agent, "PLAN_CHECK", "acceptance-criteria.yml")
    assert rerun == "acceptance-criteria.yml", \
        f"291.1: approving a plan reruns the workflow file {rerun!r}, not acceptance-criteria.yml"
    source = open(os.path.join(ROOT, "dokima", "agent.py")).read()
    assert "done-whens.yml" not in source and '"done-whens"' not in source, \
        "291.1: dokima/agent.py still looks for the criteria workflow under its old name, so an approval would not rerun it"


def test_the_card_and_the_board_update_when_the_acceptance_criteria_workflow_finishes(record_property):
    """The card and the board update when Acceptance criteria finishes, and wait on nothing missing.

    Proves 291.1. Reads the workflow_run trigger of card.yml and of board.yml: each must list Acceptance criteria, card.yml must still list
    the workflow of the all tests check, and every name either lists must be a workflow the repo has, since GitHub
    silently never starts on a name no workflow has."""
    record_property("proves", "291.1")
    have = {w.get("name"): f for f, w in workflows().items()}
    for f in ("card.yml", "board.yml"):
        listed = started_by(f)
        assert CRITERIA in listed, f"291.1: {f} does not start when Acceptance criteria finishes; it waits on {listed}"
        for n in listed:
            assert n in have, f"291.1: {f} waits on a workflow named {n!r}, and no workflow has that name: {sorted(have)}"
    suite = [w.get("name") for w in workflows().values() if ALL_TESTS in job_names(w)]
    assert suite and suite[0] in started_by("card.yml"), \
        f"291.1: the card no longer redraws when the all tests check finishes; card.yml waits on {started_by('card.yml')}"


# 291.3: no text a person reads says done-when, outside the named exceptions

def repo_files():
    """Every file of the repo on this machine, tracked or new, by its path."""
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True,
                         check=True).stdout.splitlines()
    return sorted(p for p in set(out) if os.path.isfile(os.path.join(ROOT, p)))


def allowed(path, line, match):
    """Whether this one use of the old word is one of the exceptions.

    In the tests, the owner's older plan lines ("Done when: ...") that Dokima still reads, and a check that the word is gone
    ("done when" not in ...)."""
    word, before, after = match.group(0), line[:match.start()], line[match.end():]
    if path.startswith("tests/") and path.endswith(".py"):
        if word == "Done when" and after.startswith(":"):
            return True
        if before.endswith('"') and re.match(r'"\s+not in\b', after):
            return True
    return False


def scan_self_check():
    """Fail unless the scan flags the old word and lets only the named exceptions through.

    Feeds the scan's rule lines it must flag (a workflow name, a step, an error message, a parameter, a test name, a
    docstring, a constant, a README line and an AGENTS.md line) and lines it must pass (the two check names, a test's
    Done when: plan line and a "not in" check), so a scan that flags nothing or everything fails here."""
    flag = [(".github/workflows/x.yml", "name: done-whens"),
            (".github/workflows/x.yml", "      - name: Run this done-when's tests"),
            (".github/workflows/x.yml", '          echo "::error title=No done-whens::Link an issue with done-whens"'),
            ("dokima/checks.py", "def annotations(junit_xml, repo, sha, done_when):"),
            ("tests/test_x.py", "def test_long_done_whens_get_short_check_names(record_property):"),
            ("tests/test_x.py", '    """Reads the issue in the old done-when format."""'),
            ("tests/test_x.py", '        DONE_WHENS = "Acceptance criteria"'),
            ("README.md", "Every Done when is checked."),
            ("AGENTS.md", "Each done-when has its check.")]
    keep = [(".github/workflows/x.yml", "    name: Acceptance criteria"),
            (".github/workflows/x.yml", "    name: list acceptance criteria"),
            ("AGENTS.md", "main's branch rule requires all tests and Acceptance criteria."),
            ("tests/test_x.py", '    "  - [ ] Done when: first thing works\\n"'),
            ("tests/test_x.py", '    assert "done when" not in text.lower()')]
    for path, line in flag:
        assert not all(allowed(path, line, m) for m in OLD_WORD.finditer(line)), f"291.3: the scan lets through {path}: {line}"
    for path, line in keep:
        assert all(allowed(path, line, m) for m in OLD_WORD.finditer(line)), f"291.3: the scan flags an exception in {path}: {line}"


def test_no_text_a_person_reads_says_done_when(record_property):
    """No file a person reads says done-when, outside the named exceptions.

    Proves 291.3. Reads every file in the repo, its path and every line, for done-when, done-whens, done when and done_when in any
    case. Skipped: dokima/plan.py, which still reads an owner's older Done when: lines, copies of past records in
    tests/samples, and this test. Allowed: the names of the checks Acceptance criteria and list acceptance criteria, which keep
    them until #262, and in the tests the Done when: plan lines and their "not in" checks. Each leftover is listed with
    its file and line. The scan's rule is first tried on lines it must flag and lines it must pass, so a scan that flags
    nothing proves nothing."""
    record_property("proves", "291.3")
    scan_self_check()
    skip = {"dokima/plan.py", "tests/test_check_names.py"}
    left = []
    for path in repo_files():
        if path in skip or path.startswith("tests/samples/"):
            continue
        if OLD_WORD.search(path):
            left.append(f"{path}: the file's name")
        try:
            text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if not all(allowed(path, line, m) for m in OLD_WORD.finditer(line)):
                left.append(f"{path} line {i}: {line.strip()[:120]}")
    assert not left, "291.3: the old word done-when is still where a person reads it:\n" + "\n".join(left)

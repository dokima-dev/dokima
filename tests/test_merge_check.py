"""The merge check reads its criteria and their tests from the newest plan the reviewer approved (issue #168).

Every test here runs the real command the Acceptance criteria workflow runs, `python3 -m dokima.checks matrix`, from the repo
root, with GitHub faked: a stub `gh` on PATH answers from a JSON file in a temp folder, and the pull request event is a
temp file. The issue's records are real record comments, drawn by dokima.agent.render, so the check reads exactly what
the bot posts. Nothing here touches the network.

The last test reads the Acceptance criteria workflow itself (issue #168, the owner's later comment): the merge check must run
main's copy of its workflow and of Dokima's code, so a pull request can never change the check that judges it.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BOT = "dokima-runtime"
REPO = "o/r"

STUB_GH = '''#!/usr/bin/env python3
"""A stand-in for the GitHub CLI: answers from $STUB_DATA."""
import json, os, sys
data = json.load(open(os.environ["STUB_DATA"]))
a = sys.argv[1:]
if a[:2] == ["issue", "view"]:
    print(json.dumps(data["issues"][a[2]]))
elif a[:2] == ["api", "graphql"]:
    print(json.dumps({"data": {"repository": {"pullRequest": {"closingIssuesReferences": {"nodes": []}}}}}))
elif a[:2] == ["pr", "view"]:
    print(json.dumps({"comments": [], "reviews": [], "headRefName": "", "body": ""}))
else:
    print("[]")
'''

PLAN = {"kind": "user_story", "user_story": "Owners merge without an override.",
        "acceptance_criteria": [{"text": "First thing works", "source": "#168"},
                                {"text": "Second thing works", "source": "#168"}],
        "non_functional": [{"text": "Only records count", "why": "public repo", "principle": "fail closed"}],
        "scope": ["dokima/checks.py"], "out_of_scope": [],
        "tests": {"168.1": ["tests/test_a.py::test_one"],
                  "168.2": ["tests/test_a.py::test_two", "tests/test_b.py::test_three"],
                  "168.3": ["tests/test_c.py::test_four"]}}
OTHER_PLAN = {**PLAN, "acceptance_criteria": [{"text": "Older thing works", "source": "#168"}], "non_functional": [],
              "tests": {"168.1": ["tests/test_old.py::test_old"]}}
APPROVE = {"stage": "plan", "verdict": "approve", "summary": "Good.", "blockers": []}
BLOCK = {"stage": "plan", "verdict": "block", "summary": "No.",
         "blockers": [{"id": "B1", "criterion": "168.1", "problem": "p", "evidence": "e", "fix": "f"}]}


def record(role, handback, stage=None, passed=True, author=BOT, at="2026-10-07T20:00:00Z"):
    """One record comment exactly as the bot posts it, by the given author."""
    rec = {"role": role, "stage": stage, "handback": handback, "check": {"passed": passed, "problems": [] if passed else ["bad"]}}
    return {"author": {"login": author}, "body": agent.render(rec), "createdAt": at}


def planned(handback, **kw):
    """A planner record."""
    return record("planner", handback, **kw)


def reviewed(handback, **kw):
    """A plan reviewer record."""
    return record("reviewer", handback, stage="plan", **kw)


def stamp(comments):
    """Give comments increasing times, oldest first, as GitHub would."""
    return [{**c, "createdAt": f"2026-10-07T20:{i:02d}:00Z"} for i, c in enumerate(comments)]


def run_matrix(tmp_path, comments=(), head="try/issue-168", body="", number=168, issue_body="rough ask"):
    """Run the merge check's matrix command against a faked GitHub; return (exit code, rows or None, output)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(STUB_GH)
    gh.chmod(0o755)
    issue = {"number": number, "title": "t", "body": issue_body, "comments": stamp(list(comments))}
    (tmp_path / "data.json").write_text(json.dumps({"issues": {str(number): issue}}))
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"number": 900, "head": {"ref": head}, "body": body}}))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": REPO,
           "GITHUB_EVENT_PATH": str(event), "STUB_DATA": str(tmp_path / "data.json"), "GH_TOKEN": "x",
           "DOKIMA_BOT": BOT, "PYTHONPATH": ROOT}
    p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=30)
    rows = None
    for line in p.stdout.splitlines():
        if line.startswith("matrix="):
            rows = json.loads(line[len("matrix="):])
    return p.returncode, rows, p.stdout + p.stderr


def no_plan_row(rows, name):
    """True when the rows are exactly one check with the given name and no tests, so it can only fail."""
    return rows is not None and len(rows) == 1 and rows[0]["name"] == name and rows[0]["tests"] == ""


def test_one_check_per_criterion_of_the_approved_plan_running_exactly_its_tests(record_property, tmp_path):
    """The merge check makes one check per criterion of the approved plan, each running exactly the plan's tests for it.

    The issue holds a plan and an approving plan review, both posted by the bot. The check list must name 168.1, 168.2
    and 168.3 (acceptance criteria, then the non-functional one) with their words, and run exactly the tests the plan
    lists for each, in order: no more, no fewer. Then the same plan is checked on the records a real issue holds at
    merge time: the owner's `/work`, the worker's record, and code reviews (a block, then an approval) after the plan
    approval. None of those replaces or overturns the approved plan, so the same three checks come out."""
    record_property("proves", "168.1")
    real = [planned(PLAN), reviewed(APPROVE),
            {"author": {"login": "owner"}, "body": "/work", "createdAt": ""},
            record("worker", {"summary": "Built it.", "replies": []}),
            record("reviewer", {**BLOCK, "stage": "pr"}, stage="pr"),
            record("worker", {"summary": "Fixed B1.", "replies": [{"blocker": "B1", "answer": "fixed", "why": "w"}]}),
            record("reviewer", {**APPROVE, "stage": "pr"}, stage="pr")]
    code, rows, out = run_matrix(tmp_path, real)
    assert rows is not None and [r["id"] for r in rows] == ["168.1", "168.2", "168.3"] \
        and rows[0]["tests"] == "tests/test_a.py::test_one", \
        f"168.1: the worker's and code reviews' records after the plan approval lost the approved plan: {rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, real[:5])
    assert rows is not None and [r["id"] for r in rows] == ["168.1", "168.2", "168.3"], \
        f"168.1: a blocking code review was taken as overturning the approved plan: {rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, [planned(PLAN), reviewed(APPROVE)])
    assert code == 0, f"168.1: the matrix command failed on an issue with an approved plan:\n{out}"
    assert rows is not None, f"168.1: the matrix command printed no 'matrix=' line:\n{out}"
    assert [r["name"] for r in rows] == ["168.1 · First thing works", "168.2 · Second thing works",
                                         "168.3 · Only records count"], f"168.1: wrong checks for the approved plan: {rows}"
    assert [r["id"] for r in rows] == ["168.1", "168.2", "168.3"], f"168.1: wrong criterion ids: {rows}"
    assert [r["tests"] for r in rows] == ["tests/test_a.py::test_one",
                                          "tests/test_a.py::test_two tests/test_b.py::test_three",
                                          "tests/test_c.py::test_four"], f"168.1: checks do not run the plan's tests: {rows}"


def test_the_newest_plan_is_checked_only_once_approved_and_issue_text_is_ignored(record_property, tmp_path):
    """The newest plan is the one checked, and only once the reviewer approved it; the issue's text is ignored.

    An older plan is approved, then a newer plan is approved: the checks follow the newer plan, even though the issue's
    text holds criteria in an older format. Then a newer plan is handed back and not yet reviewed: the merge
    check fails with "No approved plan found for issue #168" until it is approved, never falling back to the older
    approved plan (the owner's answer, option B). A newer hand-back that code rejected is not a plan, so the approved
    plan still stands."""
    record_property("proves", "168.1")
    text = ("- [ ] Goal: g\n  - [ ] Done when: issue text thing\n    Verified by: a test\n"
            "  - [ ] Done when: another issue text thing\n    Verified by: a test\n")
    two = [planned(OTHER_PLAN), reviewed(APPROVE), planned(PLAN), reviewed(APPROVE)]
    code, rows, out = run_matrix(tmp_path, two, issue_body=text)
    assert rows is not None and [r["name"] for r in rows] == ["168.1 · First thing works", "168.2 · Second thing works",
                                                              "168.3 · Only records count"], \
        f"168.1: the newest approved plan was not the one checked (or the issue's text was used):\n{rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, two + [planned(OTHER_PLAN)], issue_body=text)
    assert no_plan_row(rows, "No approved plan found for issue #168"), \
        f"168.1: a newer plan not yet reviewed did not stop the merge check; it used an older plan: {rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, two + [planned(OTHER_PLAN, passed=False)], issue_body=text)
    assert rows is not None and [r["id"] for r in rows] == ["168.1", "168.2", "168.3"] \
        and rows[0]["tests"] == "tests/test_a.py::test_one", \
        f"168.1: a hand-back code rejected replaced the approved plan: {rows}\n{out}"


def test_a_criterion_without_tests_gets_a_check_that_can_only_fail(record_property, tmp_path):
    """A criterion the approved plan gives no test still gets its own named check, and that check can only fail.

    The plan lists no test for 168.2. Its check must still be there by name, with no tests, and the workflow fails any
    check with no tests and holds the merge gate until every criterion's check succeeds."""
    record_property("proves", "168.2")
    thin = {**PLAN, "tests": {"168.1": ["tests/test_a.py::test_one"], "168.3": ["tests/test_c.py::test_four"]}}
    code, rows, out = run_matrix(tmp_path, [planned(thin), reviewed(APPROVE)])
    assert rows is not None, f"168.2: the matrix command printed no 'matrix=' line:\n{out}"
    by_id = {r["id"]: r for r in rows}
    assert set(by_id) == {"168.1", "168.2", "168.3"}, f"168.2: a criterion without tests lost its check: {rows}"
    assert by_id["168.2"]["name"] == "168.2 · Second thing works" and by_id["168.2"]["tests"] == "", \
        f"168.2: the untested criterion's check is not named for it or runs tests: {by_id['168.2']}"
    assert by_id["168.1"]["tests"] == "tests/test_a.py::test_one", f"168.2: the tested criterion lost its tests: {rows}"
    workflow = open(os.path.join(ROOT, ".github/workflows/acceptance-criteria.yml")).read()
    assert 'if [ -z "$TESTS" ]' in workflow and 'test "$RESULT" = "success"' in workflow, \
        "168.2: the workflow no longer fails an untested criterion or no longer gates on every criterion"


def test_a_pull_request_with_no_approved_plan_gets_one_failing_check_saying_so(record_property, tmp_path):
    """A pull request whose issue has no approved plan fails, with a check named "No approved plan found for issue #168".

    Checked for every way a plan can be missing: no records at all, a plan never reviewed, a plan the reviewer blocked,
    an approval later overturned by a block, a newer plan not yet reviewed or blocked after an older one was approved,
    and a plan whose hand-back code rejected. Each must give exactly that one
    check, with no tests, so it fails; never an empty list and never the criteria of a plan that was not approved."""
    record_property("proves", "168.3")
    cases = {"no records": [],
             "never reviewed": [planned(PLAN)],
             "blocked": [planned(PLAN), reviewed(BLOCK)],
             "approval overturned": [planned(PLAN), reviewed(APPROVE), reviewed(BLOCK)],
             "newer plan not yet reviewed": [planned(OTHER_PLAN), reviewed(APPROVE), planned(PLAN)],
             "newer plan blocked": [planned(OTHER_PLAN), reviewed(APPROVE), planned(PLAN), reviewed(BLOCK)],
             "plan rejected by code": [planned(PLAN, passed=False), reviewed(APPROVE)]}
    for why, comments in cases.items():
        code, rows, out = run_matrix(tmp_path, comments)
        assert no_plan_row(rows, "No approved plan found for issue #168"), \
            f"168.3 ({why}): expected one failing check 'No approved plan found for issue #168', got {rows}\n{out}"


def test_a_hand_built_pull_request_with_no_issue_fails_saying_so(record_property, tmp_path):
    """A hand-built pull request that names no issue fails, with a check named "No approved plan found: no issue linked".

    The branch is not work/ or try/issue-N and the body closes no issue. A hand-built pull request that closes #168,
    whose plan is approved, gets that plan's checks instead."""
    record_property("proves", "168.3")
    code, rows, out = run_matrix(tmp_path, [planned(PLAN), reviewed(APPROVE)], head="my-fix", body="A quick fix.")
    assert no_plan_row(rows, "No approved plan found: no issue linked"), \
        f"168.3: a pull request with no issue did not fail with 'No approved plan found: no issue linked': {rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, [planned(PLAN), reviewed(APPROVE)], head="my-fix", body="Closes #168")
    assert rows is not None and [r["id"] for r in rows] == ["168.1", "168.2", "168.3"], \
        f"168.3: a pull request closing #168 did not get the approved plan's checks: {rows}\n{out}"


def test_records_pasted_by_anyone_but_the_bot_do_not_count(record_property, tmp_path):
    """A plan and approval pasted by a person, not posted by the bot, do not count: the check says no approved plan.

    The same record comments the bot would post, written by another account, must give the "No approved plan found"
    check. The same comments from the bot pass, so the check does not simply refuse everything."""
    record_property("proves", "168.4")
    fake = [planned(PLAN, author="mallory"), reviewed(APPROVE, author="mallory")]
    code, rows, out = run_matrix(tmp_path, fake)
    assert no_plan_row(rows, "No approved plan found for issue #168"), \
        f"168.4: records pasted by a person counted as an approved plan: {rows}\n{out}"
    mixed = [planned(PLAN), reviewed(APPROVE, author="mallory")]
    code, rows, out = run_matrix(tmp_path, mixed)
    assert no_plan_row(rows, "No approved plan found for issue #168"), \
        f"168.4: an approval pasted by a person counted: {rows}\n{out}"
    code, rows, out = run_matrix(tmp_path, [planned(PLAN), reviewed(APPROVE)])
    assert rows is not None and len(rows) == 3, f"168.4: the bot's own records did not count: {rows}\n{out}"



def workflow_jobs(text):
    """Each job of a workflow as (name, job-level text before its steps, [step texts]), read without a YAML library."""
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"(?m)^  ([A-Za-z0-9_-]+):\n", body)
    for name, job in zip(parts[1::2], parts[2::2]):
        head, _, steps = job.partition("\n    steps:\n")
        yield name, head, [s for s in re.split(r"(?m)^      - ", steps) if s.strip()]


def setting(text, key):
    """The value of the first `key:` line in a piece of workflow text, or None."""
    m = re.search(rf"(?m)^\s+{re.escape(key)}:\s*(.+?)\s*$", text)
    return m.group(1).strip("'\"") if m else None


def folder(path):
    """A checkout or working-directory path made comparable: '', '.', './' and None all mean the repo root."""
    return (path or ".").strip().rstrip("/").removeprefix("./") or "."


def permissions_read_only(inline, block):
    """Whether a `permissions:` setting grants only read or none: `read-all`, `{}`, or a list of read/none entries."""
    if inline:
        return inline in ("read-all", "{}")
    entries = [line.split(":", 1) for line in block.splitlines() if line.strip() and not line.strip().startswith("#")]
    return bool(entries) and all(len(e) == 2 and e[1].split("#")[0].strip() in ("read", "none") for e in entries)


def test_the_merge_check_runs_mains_code_and_judges_the_pull_requests_code(record_property):
    """The merge check runs main's own copy of its workflow and of Dokima's code; only the tests come from the pull request.

    Walks the Acceptance criteria workflow step by step. GitHub runs main's copy of a workflow only on `pull_request_target`, so
    that must be its trigger, and never `pull_request`. Every checkout that names the pull request's head marks its
    folder as the pull request's; every other checkout is main's. Every `python3 -m dokima` step must run in one of
    main's folders, with no PYTHONPATH of its own, and the step that runs pytest must run in the pull request's folder,
    so the tests still judge the pull request's code and not main's. Since the workflow now runs main's copy while it
    runs the pull request's code, it must name no key and ask for no write permission: it needs a top-level
    `permissions:` list of only read or none (without one, pull_request_target hands out the repo's default token, which
    can write), and any job's own `permissions:` may only say read or none."""
    record_property("proves", "168.5")
    text = open(os.path.join(ROOT, ".github/workflows/acceptance-criteria.yml")).read()
    on = re.split(r"(?m)^[a-z]", text.split("\non:\n", 1)[1], 1)[0]
    assert re.search(r"(?m)^  pull_request_target:", on), \
        "168.5: the merge check is not triggered by pull_request_target, so GitHub runs the pull request's copy of it"
    assert not re.search(r"(?m)^  pull_request:", on), \
        "168.5: the merge check still runs on pull_request, where the pull request's own copy of it judges it"
    assert "secrets." not in text and not re.search(r"(?m)^\s+[a-z-]+:\s*write\b", text), \
        "168.5: the merge check runs the pull request's code but names a key or asks for write permission"
    top = re.search(r"(?m)^permissions:[ \t]*(\S*)[ \t]*\n((?:[ \t]+.*\n)*)", text)
    assert top and permissions_read_only(top.group(1), top.group(2)), \
        "168.5: the merge check does not limit its token to read, so the pull request's tests could get write access"
    for name, head, _ in workflow_jobs(text):
        job = re.search(r"(?m)^    permissions:[ \t]*(\S*)[ \t]*\n((?:      .*\n)*)", head + "\n")
        assert not job or permissions_read_only(job.group(1), job.group(2)), \
            f"168.5: job '{name}' does not limit its token to read, so the pull request's tests could get write access"
    dokima_steps = pytest_steps = 0
    for name, head, steps in workflow_jobs(text):
        default = folder(setting(head, "working-directory"))
        main_dirs, pr_dirs = set(), set()
        for step in steps:
            if "actions/checkout" in step:
                where, ref = folder(setting(step, "path")), setting(step, "ref") or ""
                if "pull_request.head" in ref or "github.head_ref" in ref:
                    pr_dirs.add(where)
                    main_dirs.discard(where)
                else:
                    main_dirs.add(where)
                    pr_dirs.discard(where)
                continue
            run = step.split("run:", 1)[1] if "run:" in step else ""
            where = folder(setting(step, "working-directory") or default)
            if "python3 -m dokima" in run:
                dokima_steps += 1
                assert where in main_dirs, \
                    f"168.5: job '{name}' runs Dokima's code from the pull request's checkout, not main's: {run.strip()}"
                assert "PYTHONPATH" not in step, f"168.5: job '{name}' points a Dokima step elsewhere with PYTHONPATH"
            if re.search(r"(?m)^\s*(python3 -m )?pytest\s", run):
                pytest_steps += 1
                assert where in pr_dirs, \
                    f"168.5: job '{name}' runs the tests on main's code, not on the pull request's: {run.strip()}"
    assert dokima_steps >= 2, f"168.5: the merge check no longer runs its list and annotate steps ({dokima_steps} found)"
    assert pytest_steps >= 1, "168.5: the merge check no longer runs any criterion's tests"

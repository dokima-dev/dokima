"""Pull requests with no approved plan pass unless Dokima opened them (#857, from #744).

The required Acceptance criteria check used to fail every pull request without an approved Dokima plan, so a person's
or Dependabot's pull request could never merge. The `merge.unplanned_prs` setting, `allow` by default, lets them
through; only Dokima's own pull requests are held to the plan, and any other value keeps today's failing check.

Each test runs the real command the Acceptance criteria workflow runs, `python3 -m dokima.checks matrix`, from a temp
git repo (with or without its own settings file) and GitHub faked by a stub `gh`: the pull request changes
`app/main.py`, so the text-only shortcut never applies, and issue #77, when named, has no plan. It then runs that
workflow's own "Run this criterion's tests" step for every row it got, with a passing fake `pytest` on PATH, and its
"gate" step. The check passes only when every step does. Nothing here touches the network.
"""
import json
import os
import subprocess
import sys

from test_test_settings import make_repo
from test_text_only import ROOT, STUB_GH, step_script

PR = 902
PERSON = "octocat"
DEPENDABOT = "dependabot[bot]"
DOKIMA = "dokima-runtime[bot]"


def run_step(tmp_path, name, env):
    """Run one Acceptance criteria workflow step with a passing fake pytest; return (exit code, output)."""
    bin_dir = tmp_path / "stepbin"
    bin_dir.mkdir(exist_ok=True)
    fake = bin_dir / "pytest"
    fake.write_text("#!/bin/sh\nexit 0\n")
    fake.chmod(0o755)
    base = {k: v for k, v in os.environ.items() if k != "TESTS_RUN_ONE"}
    p = subprocess.run(["bash", "-e", "-c", step_script(name)], cwd=tmp_path, capture_output=True, text=True,
                       timeout=30, env={**base, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", **env})
    return p.returncode, p.stdout + p.stderr


def acceptance_check(tmp_path, author, head, body="", settings=None):
    """Run the Acceptance criteria check for AUTHOR's code change from branch HEAD.

    The repo holds SETTINGS as its settings file, or none. Returns (True when the check passes, the rows the matrix
    command printed, everything it printed)."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    repo = make_repo(tmp_path, settings)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(STUB_GH)
    gh.chmod(0o755)
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"pr": PR, "pages": [[{"filename": "app/main.py", "status": "modified"}]]}))
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"number": PR, "head": {"ref": head}, "body": body,
                                                  "user": {"login": author}}}))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": "o/r",
           "GITHUB_EVENT_PATH": str(event), "STUB_DATA": str(data), "GH_TOKEN": "x", "PYTHONPATH": ROOT}
    env.pop("DOKIMA_BOT", None)
    p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=30)
    out = f"matrix exit {p.returncode}\n{p.stdout}{p.stderr}"
    rows = next((json.loads(line[len("matrix="):]) for line in p.stdout.splitlines() if line.startswith("matrix=")),
                None)
    if p.returncode != 0 or rows is None:
        return False, rows, out
    passed = True
    for row in rows:
        code, step = run_step(tmp_path, "Run this criterion's tests", {"ID": row["id"], "TESTS": row["tests"]})
        out += f"\nrow {row['id']} exit {code}\n{step}"
        passed = passed and code == 0
    code, step = run_step(tmp_path, "gate", {"MATRIX": json.dumps(rows), "RESULT": "success" if passed else "failure"})
    out += f"\ngate exit {code}\n{step}"
    return passed and code == 0, rows, out


def no_plan_named(rows):
    """True when some row says no approved plan was found."""
    return any("No approved plan found" in r["name"] for r in rows or [])


def test_a_persons_pull_request_with_no_plan_passes(record_property, tmp_path):
    """A person's pull request with no approved plan passes the Acceptance criteria check.

    Proves 857.1. In a repo with no settings file, so the default holds, a person opens a code change with no linked
    issue: the check must pass and no row may say no approved plan was found. The same must hold when the pull request
    says "Closes #77" and issue #77 has no approved plan.
    """
    record_property("proves", "857.1")
    passed, rows, out = acceptance_check(tmp_path / "a", PERSON, "octocat/fix-typo")
    assert passed and not no_plan_named(rows), \
        f"857.1: a person's pull request with no linked issue still fails the Acceptance criteria check: {rows}\n{out}"
    passed, rows, out = acceptance_check(tmp_path / "b", PERSON, "octocat/fix-typo", body="Closes #77")
    assert passed and not no_plan_named(rows), \
        f"857.1: a person's pull request naming an issue with no approved plan still fails the check: {rows}\n{out}"


def test_dependabots_pull_request_with_no_plan_passes(record_property, tmp_path):
    """A Dependabot pull request with no approved plan passes the Acceptance criteria check.

    Proves 857.2. In a repo with no settings file, Dependabot opens a dependency bump from its own branch with no
    linked issue: the check must pass and no row may say no approved plan was found.
    """
    record_property("proves", "857.2")
    passed, rows, out = acceptance_check(tmp_path, DEPENDABOT, "dependabot/pip/pyyaml-6.0.2")
    assert passed and not no_plan_named(rows), \
        f"857.2: Dependabot's pull request with no plan still fails the Acceptance criteria check: {rows}\n{out}"


def test_dokimas_pull_request_with_no_plan_still_fails(record_property, tmp_path):
    """Dokima's own pull request for an issue with no approved plan still fails the check.

    Proves 857.3. In a repo with no settings file, so unplanned pull requests are allowed, Dokima's app opens issue
    #77's pull request from try/issue-77, and #77 has no approved plan: the check must fail with one row saying no
    approved plan was found for issue #77. A person's same pull request must pass, so the failure is Dokima's alone.
    """
    record_property("proves", "857.3")
    passed, rows, out = acceptance_check(tmp_path / "a", DOKIMA, "try/issue-77", body="Closes #77")
    assert not passed, f"857.3: Dokima's own pull request with no approved plan passed the check: {rows}\n{out}"
    assert [r["name"] for r in rows or []] == ["No approved plan found for issue #77"], \
        f"857.3: Dokima's own unplanned pull request did not fail saying no approved plan was found: {rows}\n{out}"
    passed, rows, out = acceptance_check(tmp_path / "b", PERSON, "try/issue-77", body="Closes #77")
    assert passed, f"857.3: a person's same pull request failed too, so the check fails everyone: {rows}\n{out}"


def test_a_setting_other_than_allow_fails_a_persons_unplanned_pull_request(record_property, tmp_path):
    """When the unplanned pull requests setting is not allow, a person's unplanned pull request fails.

    Proves 857.4. In a repo whose settings say `merge.unplanned_prs: block`, a person's code change with no linked
    issue must fail the check with "No approved plan found: no issue linked", and one saying "Closes #77" must fail
    with "No approved plan found for issue #77". The same change in a repo whose settings say `allow` must pass.
    """
    record_property("proves", "857.4")
    block = {"merge": {"unplanned_prs": "block"}}
    passed, rows, out = acceptance_check(tmp_path / "a", PERSON, "octocat/fix-typo", settings=block)
    assert not passed and [r["name"] for r in rows or []] == ["No approved plan found: no issue linked"], \
        f"857.4: with unplanned_prs set to block, a person's pull request with no issue did not fail: {rows}\n{out}"
    passed, rows, out = acceptance_check(tmp_path / "b", PERSON, "octocat/fix-typo", body="Closes #77", settings=block)
    assert not passed and [r["name"] for r in rows or []] == ["No approved plan found for issue #77"], \
        f"857.4: with unplanned_prs set to block, a person's pull request naming #77 did not fail: {rows}\n{out}"
    allow = {"merge": {"unplanned_prs": "allow"}}
    passed, rows, out = acceptance_check(tmp_path / "c", PERSON, "octocat/fix-typo", settings=allow)
    assert passed, f"857.4: with unplanned_prs set to allow, a person's pull request failed: {rows}\n{out}"

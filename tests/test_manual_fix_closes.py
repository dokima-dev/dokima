"""A merged manual fix closes the issue its branch names, as a planned build closes its own (#837).

fix.yml opens a manual fix only from a branch fix/issue-N or fix/issue-N-<what>, as a planned build's is try/issue-N.
The card rewrites a pull request's description (#373), so the issue is read from the branch, never the text.
card.yml's close step runs here with a fake `gh`.
"""
import os
import re
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent_github as ag  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_a_manual_fix_s_branch_names_its_issue(record_property):
    """The issue is read from fix/issue-N and fix/issue-N-<what>; any other branch names none."""
    record_property("proves", "837.1")
    assert ag.manual_fix_issue("fix/issue-837") == 837
    assert ag.manual_fix_issue("fix/issue-837-branch-names-issue") == 837
    for other in ("fix/typo", "fix/issue-x", "try/issue-5", "fix/issue-837/x", "", None):
        assert ag.manual_fix_issue(other) is None, f"837.1: {other!r} named an issue"


def close_step():
    jobs = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/card.yml")))["jobs"]
    for job in jobs.values():
        for s in job.get("steps") or []:
            if s.get("name") == "Close the issue a merged pull request was built for":
                return s
    raise AssertionError("card.yml has no close step")


def run_close(tmp_path, head):
    tmp_path.mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh.log"
    (bin_dir / "gh").write_text(f"#!/bin/sh\necho \"$@\" >> '{log}'\n")
    (bin_dir / "gh").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "HEAD": head, "PR": "840",
           "GITHUB_REPOSITORY": "o/r"}
    subprocess.run(["bash", "-e", "-c", close_step()["run"]], env=env, check=True, cwd=tmp_path)
    return log.read_text() if log.exists() else ""


def test_a_merged_manual_fix_closes_its_issue(record_property, tmp_path):
    """card.yml's close step closes a manual fix's issue, still closes a planned build's, and nothing else."""
    record_property("proves", "837.2")
    assert re.search(r"issue close 837 ", run_close(tmp_path / "a", "fix/issue-837-closes")), \
        "837.2: the manual fix's issue stayed open"
    assert re.search(r"issue close 57 ", run_close(tmp_path / "b", "try/issue-57")), \
        "837.2: a planned build's issue no longer closes"
    assert run_close(tmp_path / "c", "fix/manual-fix-closes") == "", "837.2: a branch naming no issue closed one"

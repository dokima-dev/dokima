"""A merged manual fix closes the issue it names, as a planned build closes its own (#830 follow-up).

fix.yml opens a manual fix whose description starts `Fixes #N. A manual fix from the branch`. The card then rewrites
the description and disarms the `#` (#373), and card.yml closed an issue on merge only for try/issue-N branches, so a
manual fix's issue never closed. `agent_github.manual_fix_issue` reads the issue back for the app's own manual fixes
only; card.yml's close step runs here with a fake `gh`.
"""
import os
import re
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent_github as ag  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
APP = f"{ag.BOT}[bot]"
WRITTEN = "Fixes #832. A manual fix from the branch `fix/x`, opened by Dokima's app."
DISARMED = "<!-- dokima-card -->\nFixes &#35;832. A manual fix from the branch `fix/x`, opened by Dokima's app."


def test_the_app_s_manual_fix_names_its_issue_raw_or_disarmed(record_property):
    """The issue is read from the app's manual fix as fix.yml wrote it and as the card shows it; nobody else's words count."""
    record_property("proves", "832.1")
    assert ag.manual_fix_issue(WRITTEN, APP) == 832
    assert ag.manual_fix_issue(DISARMED, APP) == 832
    assert ag.manual_fix_issue(WRITTEN, "someone") is None, "832.1: a person's PR text closed an issue"
    assert ag.manual_fix_issue("Fixes #832 by hand", APP) is None, "832.1: words that are not fix.yml's closed an issue"


def close_step():
    steps = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/card.yml")))["jobs"]
    for job in steps.values():
        for s in job.get("steps") or []:
            if s.get("name") == "Close the issue a merged pull request was built for":
                return s
    raise AssertionError("card.yml has no close step")


def run_close(tmp_path, head, body, author):
    tmp_path.mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh.log"
    (bin_dir / "gh").write_text(f"#!/bin/sh\necho \"$@\" >> '{log}'\n")
    (bin_dir / "gh").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "PYTHONPATH": ROOT, "HEAD": head,
           "PR": "833", "BODY": body, "AUTHOR": author, "GITHUB_REPOSITORY": "o/r"}
    subprocess.run(["bash", "-e", "-c", close_step()["run"]], env=env, check=True, cwd=tmp_path)
    return log.read_text() if log.exists() else ""


def test_a_merged_manual_fix_closes_its_issue(record_property, tmp_path):
    """card.yml's close step closes a manual fix's issue, still closes a planned build's, and nothing else."""
    record_property("proves", "832.2")
    assert re.search(r"issue close 832 ", run_close(tmp_path / "a", "fix/x", DISARMED, APP)), "832.2: the manual fix's issue stayed open"
    assert re.search(r"issue close 57 ", run_close(tmp_path / "b", "try/issue-57", "", APP)), "832.2: a planned build's issue no longer closes"
    assert run_close(tmp_path / "c", "fix/x", WRITTEN, "someone") == "", "832.2: a person's PR closed an issue"

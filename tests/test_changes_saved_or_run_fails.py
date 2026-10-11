"""A run's changes reach its branch, or the run fails before its record says it passed (#441, #391, #397).

Plays the real "Push the planner's tests or the worker's code" step of agent.yml with bash, against a local copy of
GitHub where try/issue-7 moved while the run worked, as when main is merged into it.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_start import load_yaml  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AGENT_YML = os.path.join(ROOT, ".github", "workflows", "agent.yml")
STEP = "Push the planner's tests or the worker's code to try/issue-N"
URL = "https://x-access-token:T@github.com/o/r.git"


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout


def save_step():
    """The step's shell, with GitHub's ${{ }} expressions filled in."""
    wf = load_yaml(open(AGENT_YML).read())
    step = next(s for s in wf["jobs"]["run"]["steps"] if s.get("name") == STEP)
    return re.sub(r"\$\{\{\s*github\.run_id\s*\}\}", "1", step["run"])


def play(tmp_path, clash):
    """try/issue-7 moves on GitHub while the planner edits tests/t.py; returns (exit code, output, env, check, origin log)."""
    origin, other, run = tmp_path / "origin.git", tmp_path / "other", tmp_path / "run"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(tmp_path, "clone", "-q", str(origin), str(other))
    (other / "tests").mkdir()
    (other / "tests" / "t.py").write_text("a = 1\n")
    git(other, "add", "-A"); git(other, "commit", "-qm", "start"); git(other, "push", "-q", "origin", "HEAD:try/issue-7")
    git(tmp_path, "clone", "-q", "-b", "try/issue-7", str(origin), str(run))
    # Meanwhile the branch moves on GitHub.
    (other / ("tests/t.py" if clash else "other.py")).write_text("a = 2\n")
    git(other, "add", "-A"); git(other, "commit", "-qm", "merge main"); git(other, "push", "-q", "origin", "HEAD:try/issue-7")
    # The planner's own edit.
    (run / "tests" / "t.py").write_text("a = 3\n")
    bin_dir, out = tmp_path / "bin", tmp_path / "out"
    bin_dir.mkdir(); out.mkdir()
    (bin_dir / "gh").write_text("#!/bin/sh\necho 1\n"); (bin_dir / "gh").chmod(0o755)
    env_file = tmp_path / "github_env"; env_file.write_text("")
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "ROLE": "planner", "N": "7",
           "OUT": str(out), "GITHUB_ENV": str(env_file), "GITHUB_REPOSITORY": "o/r", "GH_TOKEN": "T", "SLUG": "bot",
           "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": f"url.{origin}.insteadOf", "GIT_CONFIG_VALUE_0": URL}
    p = subprocess.run(["bash", "-e", "-c", save_step()], cwd=run, env=env, capture_output=True, text=True, timeout=60)
    check = (out / "check.txt").read_text() if (out / "check.txt").exists() else ""
    return p.returncode, p.stdout + p.stderr, env_file.read_text(), check, git(origin, "log", "--format=%s", "try/issue-7")


def test_a_run_whose_branch_moved_still_saves_its_changes(tmp_path):
    """The branch moved during the run with no clash: the run catches up and its commit reaches the branch."""
    code, out, env, check, log = play(tmp_path, clash=False)
    assert code == 0, out
    assert any(l.startswith("planner for #7") for l in log.splitlines()), \
        f"#441: the planner's commit never reached try/issue-7 after the branch moved:\n{log}\n{out}"
    assert "PASSED=false" not in env and not check, f"#441: a saved run was marked failed: {env!r} {check!r}"


def test_a_run_whose_changes_cannot_be_saved_fails_before_its_record(tmp_path):
    """The branch moved with a clash: nothing reaches the branch, and the run is marked failed, saying why."""
    code, out, env, check, log = play(tmp_path, clash=True)
    assert code == 0, out
    assert not any(l.startswith("planner for #7") for l in log.splitlines()), f"#441: a clashing commit was pushed:\n{log}"
    assert "PASSED=false" in env, f"#441: changes that were never saved still leave the run passed: {env!r}\n{out}"
    assert "could not be saved" in check, f"#441: the record will not say why the run failed: {check!r}"


def test_the_record_is_written_only_after_the_changes_are_saved():
    """The save step comes before the step that writes the run's record, so the record knows whether it saved."""
    names = [s.get("name") or s.get("id") for s in load_yaml(open(AGENT_YML).read())["jobs"]["run"]["steps"]]
    assert names.index(STEP) < names.index("Write this run's record"), f"#441: the record is written before saving: {names}"

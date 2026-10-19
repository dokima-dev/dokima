"""Seeding records on a test's logs remote leaves nothing running or shared behind (#915).

A detached git maintenance left writing to the remote after the seed's push, or a scratch clone in the temp folder all
pytest-xdist workers share, let one test's setup fail at random with `unable to write file ./objects/...`.
"""
import os
import subprocess
import tempfile

import record_seed


def test_seeding_a_remote_starts_no_background_git_and_keeps_its_scratch_in_the_tests_folder(tmp_path, monkeypatch):
    """The push starts no background git, the shared temp folder stays empty, records land."""
    shared = tmp_path / "shared-tmp"
    shared.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(shared))
    trace = tmp_path / "trace.txt"
    monkeypatch.setenv("GIT_TRACE2", str(trace))
    remote = tmp_path / "own" / "logs.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)

    record_seed.seed(7, [{"role": "planner"}, {"role": "reviewer"}], str(remote))

    started = [l for l in trace.read_text().splitlines() if "child_start" in l]
    assert started, "the trace caught no git child process, so it proves nothing"
    assert not [l for l in started if " maintenance " in l or " gc " in l], \
        f"seeding left git tidying the remote in the background: {started}"
    assert os.listdir(shared) == [], f"seeding wrote to the temp folder every worker shares: {os.listdir(shared)}"
    assert os.listdir(remote.parent) == ["logs.git"], f"seeding left its scratch clone behind: {os.listdir(remote.parent)}"
    files = subprocess.run(["git", "ls-tree", "-r", "--name-only", "logs"], cwd=remote, capture_output=True, text=True,
                           check=True).stdout.split()
    assert files == ["logs/7/records/seed-0001-planner.json", "logs/7/records/seed-0002-reviewer.json"], files

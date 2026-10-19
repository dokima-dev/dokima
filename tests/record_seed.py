"""Saves agent records as files on a logs branch, as runs save them since #610.

Since #610 a run reads earlier records only from files under `logs/N/records/` on the `logs` branch of the logs remote
(DOKIMA_LOGS_REMOTE in tests), oldest saved first, never from the bot's comments. Older tests that faked an issue whose
comments carried records seed the same records here, so the pack still finds them.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
# No background gc or maintenance: a detached one left writing to the remote after a push races the test's next write.
# A push's receive side never sees `-c`, so seed sets these in the remote's own config too.
QUIET = ("-c", "gc.auto=0", "-c", "receive.autogc=false", "-c", "maintenance.auto=false")


def _git(*args, cwd=None):
    """Run git with an identity and no background tidying; a failure shows git's own words."""
    r = subprocess.run(["git", *QUIET, *args], cwd=cwd, env={**os.environ, **IDENTITY}, capture_output=True, text=True)
    assert r.returncode == 0, f"test setup: git {' '.join(args)} failed: {r.stderr}"
    return r.stdout


def seed(number, recs, remote=None):
    """Save each record as its own file on the remote's logs branch, oldest first.

    One commit per record; returns the remote. With no remote, a fresh bare repo is made. A remote that already has a logs branch keeps it and gains the files.
    The scratch clone lives beside the remote, in the test's own folder, and is removed once pushed."""
    if remote is None:
        remote = os.path.join(tempfile.mkdtemp(prefix="dokima-seed-"), "logs.git")
        _git("init", "-q", "--bare", remote)
    for setting in QUIET[1::2]:
        _git("--git-dir", str(remote), "config", *setting.split("="))
    work = tempfile.mkdtemp(prefix="dokima-seed-work-", dir=os.path.dirname(os.path.abspath(str(remote))))
    if _git("ls-remote", "--heads", str(remote), "logs").strip():
        _git("clone", "-q", "-b", "logs", str(remote), work)
    else:
        _git("init", "-q", work)
        _git("checkout", "-q", "--orphan", "logs", cwd=work)
    folder = os.path.join(work, "logs", str(number), "records")
    os.makedirs(folder, exist_ok=True)
    start = len(os.listdir(folder))
    for i, r in enumerate(recs, start + 1):
        name = f"seed-{i:04d}-{r.get('role')}.json"
        with open(os.path.join(folder, name), "w") as f:
            json.dump(r, f, indent=1)
        _git("add", "-A", cwd=work)
        _git("commit", "-qm", f"record {name}", cwd=work)
    if recs:
        _git("push", "-q", str(remote), "HEAD:logs", cwd=work)
    shutil.rmtree(work, ignore_errors=True)
    return str(remote)


def use(monkeypatch, number, recs):
    """Seed these records on a fresh logs remote and point DOKIMA_LOGS_REMOTE at it."""
    remote = seed(number, recs)
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", remote)
    return remote


def in_comments(comments, bot="dokima-runtime"):
    """The records the bot's comments carry, oldest first, with each comment's link.

    Only for seeding: tests that build an issue from record comments save the same records as files."""
    out = []
    for c in comments:
        if not isinstance(c, dict) or (c.get("author") or {}).get("login") != bot:
            continue
        m = re.search(r"```json\n(.*?)\n```", c.get("body") or "", re.S)
        if not m:
            continue
        try:
            r = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(r, dict):
            out.append({**r, "url": c["url"]} if isinstance(c.get("url"), str) and "url" not in r else r)
    return out

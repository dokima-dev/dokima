"""The fence takes its scope only from the plan file (#762, story 3 of #739).

Every run of the worker's workflow hands the fence the plan's plan.json, so the old reader of a Scope heading in the
issue's text is dead code. These tests run the fence from outside on a temp git repo, and check that the reader and
every test of it are gone from the repo.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = "https://github.com/o/r/issues/9"
OLD_READER = "scope" + "_of"  # split so this file does not name it


def repo(where):
    """A committed temp git repo holding app.py; its base commit."""
    where.mkdir()
    (where / "app.py").write_text("x = 1\n")
    for a in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@e.com"], ["add", "-A"],
              ["commit", "-qm", "base"]):
        subprocess.run(["git", *a], cwd=where, check=True, capture_output=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=where, check=True, capture_output=True,
                          text=True).stdout.strip()


def run_fence(where, base, plan):
    """Run the fence as the worker's workflow does, with this plan file; the finished process."""
    return subprocess.run([sys.executable, "-m", "dokima.fence", base, str(plan)], cwd=where,
                          env=dict(os.environ, PYTHONPATH=ROOT), capture_output=True, text=True, timeout=30)


def test_the_fence_ignores_a_scope_in_the_issue_text(record_property, tmp_path):
    """The fence no longer lets a file through because the issue's text lists it.

    Proves 762.1. Changes app.py in a temp repo and runs the fence on an issue text whose Scope heading lists app.py:
    the fence must not finish with that change kept, so the text's Scope let nothing through. Then runs it on a
    plan.json whose criterion lists app.py: the change is kept and nothing is dropped, so plans still work.
    """
    record_property("proves", "762.1")
    work = tmp_path / "repo"
    base = repo(work)
    (work / "app.py").write_text("x = 2\n")
    issue = tmp_path / "issue.md"
    issue.write_text("Plan text.\n\n**Scope:**\n- `app.py`\n\n**Out of scope:** nothing.\n")
    r = run_fence(work, base, issue)
    kept = (work / "app.py").read_text() == "x = 2\n"
    assert not (r.returncode == 0 and kept), (
        "762.1: the fence still read its scope from the issue's text: it passed and kept app.py, which only that "
        "text listed")
    (work / "app.py").write_text("x = 3\n")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"acceptance_criteria": [{"text": "A change.", "source": SRC, "files": ["app.py"]}],
                                "non_functional": [], "tests": {}}))
    r = run_fence(work, base, plan)
    assert r.returncode == 0, f"762.1: the fence failed on a plan.json: {r.stderr}"
    assert (work / "app.py").read_text() == "x = 3\n", "762.1: the fence undid app.py, which the plan.json lists"
    assert r.stdout.split() == [], f"762.1: the fence dropped files the plan.json lists: {r.stdout.split()}"


def test_the_issue_text_reader_and_its_tests_are_gone(record_property):
    """No code or test of the repo still holds the fence's old issue text reader.

    Proves 762.2. A test that only checks the old reader has to call it by name, so once no file under dokima/ or
    tests/ names it, every such test is gone. Fails today because the fence still defines it.
    """
    record_property("proves", "762.2")
    left = []
    for top in ("dokima", "tests"):
        for d, _, files in os.walk(os.path.join(ROOT, top)):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(d, f)
                    if OLD_READER in open(path, errors="replace").read():
                        left.append(os.path.relpath(path, ROOT))
    assert left == [], f"762.2: the old issue text reader, or a test of it, is still in {sorted(left)}"

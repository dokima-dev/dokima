"""The fence keeps only the worker's in-scope changes and puts every test back as the planner committed it."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import fence  # noqa: E402

SCOPE = ["app.py", "tests/test_app.py"]


def repo(tmp_path, monkeypatch):
    """A temp git repo with an app file, a planner test and a README, committed; returns the base commit."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / "README.md").write_text("readme\n")
    (tmp_path / "tests" / "test_app.py").write_text("def test_x():\n    assert False\n")
    for a in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@e.com"], ["add", "-A"], ["commit", "-qm", "base"]):
        subprocess.run(["git", *a], check=True, capture_output=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def test_tampering_is_undone_and_in_scope_work_survives(record_property, tmp_path, monkeypatch):
    """An edited test, a new conftest, an edited out-of-scope file and a new stray file are all undone; the in-scope edit stays.

    Simulates a worker that changes the app (allowed) and also edits the planner's test, adds a conftest that would
    skip everything, edits the README and adds a stray file, then checks what survives the fence and what it names."""
    record_property("proves", "fence.1")
    record_property("proves", "527.3")
    base = repo(tmp_path, monkeypatch)
    (tmp_path / "app.py").write_text("x = 2\n")
    (tmp_path / "tests" / "test_app.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "conftest.py").write_text("collect_ignore_glob = ['*']\n")
    (tmp_path / "README.md").write_text("changed\n")
    (tmp_path / "stray.py").write_text("y = 1\n")
    dropped = fence.fence(base, SCOPE)
    assert (tmp_path / "app.py").read_text() == "x = 2\n", "the in-scope change was lost"
    assert "assert False" in (tmp_path / "tests" / "test_app.py").read_text(), "the planner's test was not restored"
    assert not (tmp_path / "conftest.py").exists() and not (tmp_path / "stray.py").exists(), "new files outside scope survived"
    assert (tmp_path / "README.md").read_text() == "readme\n", "an out-of-scope edit survived"
    assert dropped == ["README.md", "conftest.py", "stray.py", "tests/test_app.py"], f"wrong dropped list: {dropped}"


def test_an_honest_build_is_untouched(record_property, tmp_path, monkeypatch):
    """A worker that changes only in-scope, non-test files loses nothing and nothing is named."""
    record_property("proves", "fence.2")
    base = repo(tmp_path, monkeypatch)
    (tmp_path / "app.py").write_text("x = 3\n")
    assert fence.fence(base, SCOPE) == [], "an honest build had changes dropped"
    assert (tmp_path / "app.py").read_text() == "x = 3\n"


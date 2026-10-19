"""Tests for #896: the settings may name only the agent keys entry.yml declares.

GitHub hands a workflow in another account's repo only the secrets it declares by name, so a key outside that list
never reaches the jobs. The audit reports it in one line, and a job naming it fails with that same line.
"""
import os
import subprocess
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from dokima import agents  # noqa: E402
from test_audit import REPO, GitHub, audit  # noqa: E402

SETTINGS = ("agents:\n  subscriptions:\n    mine:\n      agent: claude\n      key: {key}\n"
            "  roles:\n    worker:\n      subscription: mine\n      model: claude-opus-5-5\n")
LINE = ("The settings name the agent key `MY_KEY`, which will never reach the jobs: use a declared name "
        "(`CLAUDE_CODE_OAUTH_TOKEN`, `CODEX_API_KEY`, `KIMI_API_KEY`), or ask for `MY_KEY` to be declared in a release.")


def write(root, key):
    os.makedirs(root / ".dokima", exist_ok=True)
    (root / ".dokima" / "settings.yaml").write_text(SETTINGS.format(key=key))


def worker_key(root):
    env = {**os.environ, "PYTHONPATH": ROOT}
    env.pop("DOKIMA_SETTINGS", None)
    return subprocess.run([sys.executable, "-m", "dokima.agents", "key", "worker"], cwd=root, env=env,
                          capture_output=True, text=True)


def test_the_declared_keys_are_the_ones_entry_yml_declares():
    """The list the settings are held to is exactly the agent keys entry.yml declares."""
    with open(os.path.join(ROOT, ".github", "workflows", "entry.yml")) as f:
        entry = yaml.safe_load(f)
    declared = set((entry.get("on") or entry.get(True))["workflow_call"]["secrets"]) - {"DOKIMA_APP_KEY"}
    assert set(agents.DECLARED) == declared, f"896: settings allow {agents.DECLARED}, entry.yml declares {declared}"


def test_a_job_naming_an_undeclared_key_fails_with_the_audit_line(tmp_path):
    """A job naming an undeclared key stops with that line, not a missing key."""
    write(tmp_path, "MY_KEY")
    p = worker_key(tmp_path)
    assert p.returncode == 1 and p.stderr.strip() == LINE, f"896: exit {p.returncode}, said {p.stderr!r}"


def test_a_job_naming_a_declared_key_runs(tmp_path):
    """A declared key other than Claude's passes."""
    write(tmp_path, "KIMI_API_KEY")
    p = worker_key(tmp_path)
    assert p.returncode == 0 and p.stdout.strip() == "KIMI_API_KEY", f"896: exit {p.returncode}, said {p.stderr!r}"


def test_the_audit_reports_an_undeclared_key_in_one_line(tmp_path):
    """The audit gives that same line even when set; nothing for a declared key."""
    a = audit("896")
    g = GitHub()
    g.secret_names = {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "MY_KEY", "CODEX_API_KEY"}
    write(tmp_path, "MY_KEY")
    lines = [l for l in a.compare(g, REPO, root=str(tmp_path)) if "MY_KEY" in l]
    assert lines == [LINE], f"896: the audit said {lines}"
    write(tmp_path, "CODEX_API_KEY")
    lines = [l for l in a.compare(g, REPO, root=str(tmp_path)) if "key" in l.lower()]
    assert lines == [], f"896: a declared key that is set was reported: {lines}"

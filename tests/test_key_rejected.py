"""Tests for #907: a rejected key is reported as such, not a missing plan.

When the agent cannot log in (its provider answers 401 or 403, or says the token is invalid or expired), the run
leaves no hand-back, and the record used to blame the agent ("found no plan.json"). These tests write a run's record
the way the agent workflow does, from a fake agent output in the run's folder, and check what the owner reads. The
setup audit's key check is run against a fake `claude` on the PATH, so no real provider is ever called.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from test_audit import REPO, GitHub, audit  # noqa: E402
from test_start import load_yaml  # noqa: E402

MISSING_PLAN = ("found no plan.json: the planner always hands back a plan, a plan.json of kind user_story or feature, "
                "raising its questions for the owner in raises")
REJECTED_401 = "Failed to authenticate. API Error: 401 OAuth access token is invalid."
KEY = "sk-ant-oat01-907secretvalueABCDEFGHIJKLMNOP"


def claude_output(text, error=True):
    """Claude Code's printed report (claude.json) for a run that ended with TEXT."""
    return json.dumps({"type": "result", "subtype": "success", "is_error": error, "result": text, "num_turns": 1,
                       "duration_ms": 500, "total_cost_usd": 0, "usage": {"input_tokens": 0, "output_tokens": 0}})


def write_record(tmp_path, output, settings=None, extra_env=None):
    """Write the planner's record after a run that left OUTPUT and no plan.

    Returns (comment.md, record.json) as text. The code check found no plan.json, as it does today."""
    out, pack, logs = tmp_path / "out", tmp_path / "pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    if output is not None:
        (out / "claude.json").write_text(output)
    (out / "check.txt").write_text(MISSING_PLAN + "\n")
    settings_file = tmp_path / "settings.yaml"
    if settings:
        settings_file.write_text(settings)
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "DOKIMA_SETTINGS": str(settings_file), **(extra_env or {})}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE", "BASE", "LOG_URL"):
        env.pop(k, None)
    for k in [k for k in env if k.startswith("SCRUB_")]:
        env.pop(k)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "record", "planner", "", str(out), str(out / "check.txt"),
                        "false", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"the record step failed:\n{(p.stdout + p.stderr)[-800:]}"
    return (out / "comment.md").read_text(), (out / "record.json").read_text()


def assert_key_rejected(comment, criterion, what):
    """Fail naming CRITERION unless the comment reports a rejected key and not a missing plan."""
    assert "Model key rejected" in comment, \
        f"{criterion}: {what} did not end the run as \"Model key rejected\":\n{comment[:600]}"
    assert "found no plan.json" not in comment and "hand-back rejected" not in comment, \
        f"{criterion}: {what} is still reported as a missing or rejected hand-back:\n{comment[:600]}"


def test_a_401_from_the_provider_reads_model_key_rejected(record_property, tmp_path):
    """A 401 reads "Model key rejected"; a plain missing plan still says so.

    Writes the record of a planner run whose agent printed the provider's 401 and left no plan, and checks the card
    says "Model key rejected" with no word of a missing plan. Then writes one whose agent ran fine but left no plan,
    and checks that one still says the plan is missing.

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path / "bad-key", claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.1", "a 401 from the provider")
    comment, _ = write_record(tmp_path / "no-plan", claude_output("I finished.", error=False))
    assert "found no plan.json" in comment and "Model key rejected" not in comment, \
        f"907.1: a run that really left no plan no longer says the plan is missing:\n{comment[:600]}"


def test_a_403_from_the_provider_reads_model_key_rejected(record_property, tmp_path):
    """A run whose agent was refused with a 403 ends as "Model key rejected".

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path, claude_output("API Error: 403 Forbidden: this key may not use this model."))
    assert_key_rejected(comment, "907.1", "a 403 from the provider")


def test_an_expired_token_reads_model_key_rejected(record_property, tmp_path):
    """A run whose agent says its token expired ends as "Model key rejected".

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path, claude_output("OAuth token has expired. Please obtain a new token."))
    assert_key_rejected(comment, "907.1", "an expired token")


def test_the_record_names_the_secret_the_settings_use(record_property, tmp_path):
    """The rejected-key card names the repo secret the planner's settings use for its key.

    With no settings it must name `CLAUDE_CODE_OAUTH_TOKEN`, today's secret; with settings naming `MY_KEY` for the
    planner, it must name `MY_KEY` instead.

    Proves 907.2."""
    record_property("proves", "907.2")
    comment, _ = write_record(tmp_path / "default", claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.2", "a 401 from the provider")
    assert "CLAUDE_CODE_OAUTH_TOKEN" in comment, \
        f"907.2: the card does not name the secret CLAUDE_CODE_OAUTH_TOKEN the settings use:\n{comment[:600]}"
    mine = ("agents:\n  subscriptions:\n    mine:\n      agent: claude\n      key: MY_KEY\n"
            "  roles:\n    planner:\n      subscription: mine\n      model: claude-opus-5-5\n")
    comment, _ = write_record(tmp_path / "mine", claude_output(REJECTED_401), settings=mine)
    assert "MY_KEY" in comment and "CLAUDE_CODE_OAUTH_TOKEN" not in comment, \
        f"907.2: with settings naming MY_KEY, the card does not name that secret alone:\n{comment[:600]}"


def test_the_record_says_to_make_a_new_key_and_replace_the_repo_secret(record_property, tmp_path):
    """The card says the provider refused the key: make a new one, replace the secret.

    Proves 907.3."""
    record_property("proves", "907.3")
    comment, _ = write_record(tmp_path, claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.3", "a 401 from the provider")
    low = comment.lower()
    missing = [w for w in ("refused", "new one", "replace", "repo secret") if w not in low]
    assert not missing, (f"907.3: the card does not tell the owner the provider refused the key and to make a new one "
                         f"and replace the repo secret; it lacks {missing}:\n{comment[:600]}")


def test_the_record_never_prints_any_part_of_the_key(record_property, tmp_path):
    """No piece of the key reaches the rejected-key card or its record.

    The key sits in the run's environment under both names the agent step uses; the card and record must not hold
    any 8 characters of it in a row.

    Proves 907.4."""
    record_property("proves", "907.4")
    comment, record = write_record(tmp_path, claude_output(REJECTED_401),
                                   extra_env={"DOKIMA_AGENT_KEY": KEY, "CLAUDE_CODE_OAUTH_TOKEN": KEY})
    assert_key_rejected(comment, "907.4", "a 401 from the provider")
    pieces = {KEY[i:i + 8] for i in range(len(KEY) - 7)}
    leaked = sorted(p for p in pieces if p in comment or p in record)
    assert not leaked, f"907.4: part of the key was printed on the card or its record: {leaked[:3]}"


def fake_claude(tmp_path, monkeypatch, text, error):
    """Put a fake `claude` printing TEXT first on the PATH; return its call log."""
    bin_dir, calls = tmp_path / "bin", tmp_path / "calls.txt"
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "claude"
    script.write_text(f"#!/bin/sh\necho called >> '{calls}'\ncat <<'EOF'\n{claude_output(text, error)}\nEOF\n"
                      f"exit {1 if error else 0}\n")
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("DOKIMA_SETTINGS", str(tmp_path / "none.yaml"))
    for k in [k for k in os.environ if k.startswith("DOKIMA_KEY_")]:
        monkeypatch.delenv(k)
    if calls.exists():
        calls.unlink()
    return calls


def calls_made(calls):
    """How many times the fake agent was started."""
    return len(calls.read_text().splitlines()) if calls.exists() else 0


def rejected_lines(lines):
    """The audit's lines that report a rejected key."""
    return [l for l in lines if "rejected" in l.lower()]


def test_the_audit_tries_a_present_key_once(record_property, tmp_path, monkeypatch):
    """The setup audit starts the agent once when the key is given, never without it.

    Every role runs on the same secret by default, so one call checks it. The audit reads the key's value from
    `DOKIMA_KEY_CLAUDE_CODE_OAUTH_TOKEN`, the name the audit workflow gives it; the test also checks the audit
    workflow installs the agent and passes that key, and an adopter's entry workflow passes the secret on.

    Proves 907.5."""
    record_property("proves", "907.5")
    a = audit("907.5")
    calls = fake_claude(tmp_path, monkeypatch, "OK", error=False)
    a.compare(GitHub(), REPO, root=str(tmp_path))
    assert calls_made(calls) == 0, "907.5: with no key given, the audit still started the agent"
    monkeypatch.setenv("DOKIMA_KEY_CLAUDE_CODE_OAUTH_TOKEN", KEY)
    lines = a.compare(GitHub(), REPO, root=str(tmp_path))
    assert calls_made(calls) == 1, \
        f"907.5: with the key given, the audit started the agent {calls_made(calls)} times, not once"
    assert rejected_lines(lines) == [], f"907.5: a key the provider accepted is reported as rejected: {lines}"
    audit_wf = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "audit.yml")).read())
    steps = audit_wf["jobs"]["audit"]["steps"]
    run_audit = next(s for s in steps if "python3 -m dokima.audit" in str(s.get("run", "")))
    assert "secrets.CLAUDE_CODE_OAUTH_TOKEN" in str((run_audit.get("env") or {}).get("DOKIMA_KEY_CLAUDE_CODE_OAUTH_TOKEN")), \
        "907.5: the audit workflow never gives the audit the key as DOKIMA_KEY_CLAUDE_CODE_OAUTH_TOKEN"
    assert any("dokima.agents install" in str(s.get("run", "")) for s in steps[:steps.index(run_audit)]), \
        "907.5: the audit workflow never installs the agent before the audit runs, so no call can be made"
    entry = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "entry.yml")).read())
    assert "CLAUDE_CODE_OAUTH_TOKEN" in str(entry["jobs"]["audit"].get("secrets")), \
        "907.5: an adopter's audit is never passed the agent key, so it cannot check it"


def test_the_audit_reports_a_rejected_key_as_one_line(record_property, tmp_path, monkeypatch):
    """A key refused at setup is reported as one audit line naming its secret.

    The line names `CLAUDE_CODE_OAUTH_TOKEN` and holds no part of the key.

    Proves 907.6."""
    record_property("proves", "907.6")
    a = audit("907.6")
    fake_claude(tmp_path, monkeypatch, REJECTED_401, error=True)
    monkeypatch.setenv("DOKIMA_KEY_CLAUDE_CODE_OAUTH_TOKEN", KEY)
    lines = rejected_lines(a.compare(GitHub(), REPO, root=str(tmp_path)))
    assert len(lines) == 1, f"907.6: a rejected key is not reported as exactly one line: {lines}"
    assert "CLAUDE_CODE_OAUTH_TOKEN" in lines[0], f"907.6: the rejected-key line does not name its secret: {lines[0]}"
    assert not any(KEY[i:i + 8] in lines[0] for i in range(len(KEY) - 7)), \
        "907.6: the rejected-key line prints part of the key"

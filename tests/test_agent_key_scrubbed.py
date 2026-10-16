"""Tests for #706: the role's agent key never reaches a public card or record.

A role can run on an agent whose key lives in a secret other than Claude's (the settings file picks it). Every
workflow step that removes Claude's token from what it publishes must remove that agent key too, and the run's record
(its card and the file saved on the logs branch) must come out with every secret its step was given removed.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "agent.yml")
AGENT_KEY = "${{ secrets[env.AGENT_KEY || 'CLAUDE_CODE_OAUTH_TOKEN'] }}"
SECRET = "kimi-sign-in-706-abcdefghijklmnop"


def steps():
    """Each step of the agent workflow, as its name and its env."""
    out, name, env, in_env = [], None, None, False
    for line in open(WORKFLOW).read().splitlines():
        start = re.match(r"^      - (?:name|id|uses): *(.*)$", line)
        if start:
            if env is not None:
                out.append((name, env))
            name, env, in_env = start.group(1).strip(), {}, False
            continue
        if env is None:
            continue
        named = re.match(r"^        name: *(.*)$", line)
        if named:
            name = named.group(1).strip()
        if re.match(r"^        env:\s*$", line):
            in_env = True
            continue
        if in_env:
            pair = re.match(r"^          ([A-Z_]+): *(.*)$", line)
            if pair:
                env[pair.group(1)] = pair.group(2).strip()
            elif not line.startswith("          "):
                in_env = False
    if env is not None:
        out.append((name, env))
    return out


def run_record(tmp_path, scrub_agent):
    """Write the planner's record as the workflow does, its plan quoting SECRET."""
    out, pack, logs = tmp_path / "out", tmp_path / "pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    (out / "plan.json").write_text(json.dumps({"kind": "user_story", "title": "Keys stay hidden",
                                               "summary": f"The agent printed {SECRET} here."}))
    (out / "check.txt").write_text("")
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "DOKIMA_SETTINGS": str(tmp_path / "none.yml"),
           "SCRUB_AGENT": scrub_agent}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE", "BASE", "LOG_URL"):
        env.pop(k, None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "record", "planner", "", str(out), str(out / "check.txt"),
                        "true", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"the record step failed:\n{(p.stdout + p.stderr)[-800:]}"
    return out


def test_every_step_that_hides_claudes_token_hides_the_agent_key(record_property):
    """Every step that hides Claude's token also hides the role's agent key.

    Reads each step of the agent workflow and checks that every one given Claude's token to remove is also given the
    key of the secret the settings file names for the role.

    Proves 706.1."""
    record_property("proves", "706.1")
    hiding = [(n, e) for n, e in steps() if "SCRUB_CLAUDE" in e]
    assert len(hiding) >= 6, f"706.1: found only {len(hiding)} steps hiding Claude's token; the workflow was misread"
    missing = [n for n, e in hiding if e.get("SCRUB_AGENT") != AGENT_KEY]
    assert not missing, ("706.1: these steps hide Claude's token but not the role's agent key, so another key could "
                         f"be posted: {missing}")


def test_the_runs_record_card_hides_the_agent_key(record_property, tmp_path):
    """The run's record card shows the role's agent key as removed.

    Checks the workflow gives the record step the role's agent key to remove, then writes a record whose plan quotes
    that key: the card shows [secret removed] in its place and keeps the rest. With no key set, the record is still
    written and keeps its text.

    Proves 706.2."""
    record_property("proves", "706.2")
    record = [e for n, e in steps() if n == "Write this run's record"]
    assert record, "706.2: the workflow has no step named Write this run's record"
    assert record[0].get("SCRUB_AGENT") == AGENT_KEY, \
        "706.2: the record step is not given the role's agent key to remove, so its card could show it"
    card = (run_record(tmp_path, SECRET) / "comment.md").read_text()
    assert SECRET not in card, "706.2: the record card shows the role's agent key"
    assert "The agent printed [secret removed] here." in card, \
        f"706.2: the record card does not show the key as removed in its place:\n{card[:800]}"
    plain = (run_record(tmp_path / "empty", "") / "comment.md").read_text()
    assert f"The agent printed {SECRET} here." in plain, \
        "706.2: with no agent key set, the record card lost its own text"


def test_the_saved_record_file_hides_the_agent_key(record_property, tmp_path):
    """The record file saved on the logs branch shows the agent key as removed.

    Writes a record whose plan quotes the role's agent key and reads the record file the logs branch keeps: the key
    is gone and [secret removed] stands in its place.

    Proves 706.3."""
    record_property("proves", "706.3")
    saved = (run_record(tmp_path, SECRET) / "record.json").read_text()
    assert SECRET not in saved, "706.3: the saved record file holds the role's agent key"
    assert "The agent printed [secret removed] here." in saved, \
        f"706.3: the saved record file does not show the key as removed in its place:\n{saved[:800]}"

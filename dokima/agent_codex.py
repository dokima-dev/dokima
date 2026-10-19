"""Codex CLI behind the one agent interface (dokima/agents.py) (#700).

It installs Codex's command line with npm, starts unattended as `codex exec` with the role's model and write access
to the repo (`--full-auto`; Codex is read-only otherwise), and keeps its event stream (`--json`) as `codex.jsonl` in
the run's folder, where its stats and transcript are read from.

The run's key arrives in DOKIMA_AGENT_KEY, the subscription's API key, and reaches Codex as CODEX_API_KEY.
"""
import json
import os
import subprocess

from dokima.agent_records import scrub

STREAM = "codex.jsonl"
MODEL = "codex-model.txt"


def install():
    """Install Codex CLI; return npm's exit code."""
    return subprocess.run(["npm", "install", "-g", "@openai/codex"]).returncode


def run(prompt, model, out):
    """Start Codex on PROMPT with MODEL, its stream into OUT/codex.jsonl; return Codex's exit code."""
    env = dict(os.environ)
    if "DOKIMA_AGENT_KEY" in env:
        env["CODEX_API_KEY"] = env.pop("DOKIMA_AGENT_KEY")
    with open(os.path.join(str(out), MODEL), "w") as f:
        f.write(model)
    with open(os.path.join(str(out), STREAM), "w") as f:
        return subprocess.run(["codex", "exec", "--model", model, "--full-auto", "--json", prompt],
                              stdout=f, env=env).returncode


def events(out):
    """Every event in Codex's stream, oldest first."""
    try:
        lines = open(os.path.join(str(out), STREAM)).read().splitlines()
    except OSError:
        return []
    found = []
    for line in lines:
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(e, dict):
            found.append(e)
    return found


def models(out, log_dir):
    """The model Codex was started with; its stream does not name one."""
    try:
        return sorted({open(os.path.join(str(out), MODEL)).read().strip()} - {""})
    except OSError:
        return []


def report(out):
    """Codex's stats: turns and tokens its stream shows; empty when it printed none."""
    turns = [e for e in events(out) if e.get("type") == "turn.completed"]
    if not turns:
        return {}
    usage = [e.get("usage") if isinstance(e.get("usage"), dict) else {} for e in turns]
    return {"turns": len(turns),
            "tokens_in": sum((u.get("input_tokens") or 0) for u in usage),
            "tokens_out": sum((u.get("output_tokens") or 0) for u in usage)}


def error(out):
    """Every error Codex's stream ended with, one per line; empty when there was none."""
    said = []
    for e in events(out):
        if e.get("type") == "error":
            said.append(str(e.get("message") or ""))
        elif e.get("type") == "turn.failed" and isinstance(e.get("error"), dict):
            said.append(str(e["error"].get("message") or ""))
    return "\n".join(said)


def transcript(log_dir, secrets):
    """The readable transcript of Codex's stream, secrets removed."""
    lines = []
    for e in events(log_dir):
        item = e.get("item")
        if e.get("type") == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                lines.append(f"**Agent:** {text.strip()}")
    return scrub("\n\n".join(lines) + "\n", secrets)

"""Claude Code behind the one agent interface (dokima/agents.py), unchanged (#698).

It installs with npm, starts with today's command and flags, keeps its printed report as `claude.json` in the run's
folder, and reads its models, stats and transcript from its own session logs and that report.
"""
import os
import subprocess

from dokima.agent_records import models_used, run_report, transcript as session_transcript


def install():
    """Install Claude Code; return npm's exit code."""
    return subprocess.run(["npm", "install", "-g", "@anthropic-ai/claude-code"]).returncode


def run(prompt, model, out):
    """Start Claude Code on PROMPT with MODEL, its report into OUT/claude.json; return its exit code.

    The run's key, given in DOKIMA_AGENT_KEY, reaches Claude Code as CLAUDE_CODE_OAUTH_TOKEN."""
    env = dict(os.environ)
    if "DOKIMA_AGENT_KEY" in env:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = env.pop("DOKIMA_AGENT_KEY")
    with open(os.path.join(str(out), "claude.json"), "w") as f:
        return subprocess.run(["claude", "-p", prompt, "--model", model, "--dangerously-skip-permissions",
                               "--max-turns", os.environ.get("DOKIMA_MAX_TURNS") or "100", "--output-format", "json"], stdout=f, env=env).returncode


def models(out, log_dir):
    """Every model Claude's session logs name."""
    return models_used(log_dir)


def report(out):
    """Claude's end-of-run report: time, turns, tokens and cost; empty when it printed none."""
    return run_report(os.path.join(str(out), "claude.json"))


def transcript(log_dir, secrets):
    """The readable transcript of Claude's session, secrets removed."""
    return session_transcript(log_dir, secrets)

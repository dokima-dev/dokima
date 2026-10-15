"""Kimi Code CLI behind the one agent interface (dokima/agents.py) (#699).

It installs Kimi's command line, puts the stored sign-in back under the home folder, starts with the owner's tested
command `kimi -p PROMPT --output-format stream-json` and the role's model, and keeps the stream as `kimi.jsonl` in the
run's folder, where its models and transcript are read from.

The run's key arrives in DOKIMA_AGENT_KEY: what `python3 -m dokima.setup add ... --sign-in` stored, the base64 text of
a gzip tar of the files Kimi's login saved, each named by its path under the home folder.
"""
import base64
import binascii
import io
import json
import os
import subprocess
import sys
import tarfile

from dokima.agent_records import scrub

STREAM = "kimi.jsonl"
MODEL = "kimi-model.txt"


def install():
    """Install Kimi Code CLI (npm package @moonshot-ai/kimi-code, its `kimi` command); return the install's exit code.

    Not the deprecated Python kimi-cli: that one keeps its sign-in elsewhere and takes other flags."""
    return subprocess.run(["npm", "install", "-g", "@moonshot-ai/kimi-code"]).returncode


def restore_sign_in(key):
    """Unpack the stored sign-in KEY into the home folder; False, saying why, when it cannot."""
    try:
        data = base64.b64decode(key, validate=True)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
            t.extractall(os.path.expanduser("~"), filter="data")
    except (binascii.Error, ValueError, tarfile.TarError, OSError) as e:
        print(f"The stored Kimi sign-in could not be put back, so Kimi was not started: {e}", file=sys.stderr)
        return False
    return True


def run(prompt, model, out):
    """Put the sign-in back, then start Kimi on PROMPT with MODEL, its stream into OUT/kimi.jsonl.

    Returns Kimi's exit code, or 1 when the sign-in cannot be put back."""
    env = dict(os.environ)
    key = env.pop("DOKIMA_AGENT_KEY", "")
    if key and not restore_sign_in(key):
        return 1
    with open(os.path.join(str(out), MODEL), "w") as f:
        f.write(model)
    with open(os.path.join(str(out), STREAM), "w") as f:
        return subprocess.run(["kimi", "-p", prompt, "--model", model, "--output-format", "stream-json"],
                              stdout=f, env=env).returncode


def messages(out):
    """Every message in Kimi's stream, oldest first."""
    try:
        lines = open(os.path.join(str(out), STREAM)).read().splitlines()
    except OSError:
        return []
    found = []
    for line in lines:
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(m, dict):
            found.append(m)
    return found


def models(out, log_dir):
    """Every model Kimi's stream names, else the model it was started with."""
    seen = {m["model"] for m in messages(out) if isinstance(m.get("model"), str) and m["model"]}
    if not seen:
        try:
            seen = {open(os.path.join(str(out), MODEL)).read().strip()} - {""}
        except OSError:
            pass
    return sorted(seen)


def report(out):
    """Kimi's stats: the turns its stream shows; empty when it printed none."""
    turns = sum(1 for m in messages(out) if m.get("role") == "assistant")
    return {"turns": turns} if turns else {}


def transcript(log_dir, secrets):
    """The readable transcript of Kimi's stream, secrets removed."""
    lines = []
    for m in messages(log_dir):
        content = m.get("content")
        if isinstance(content, list):
            content = " ".join(b.get("text", "") for b in content if isinstance(b, dict))
        if m.get("role") == "assistant" and isinstance(content, str) and content.strip():
            lines.append(f"**Agent:** {content.strip()}")
    return scrub("\n\n".join(lines) + "\n", secrets)

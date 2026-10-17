"""The one agent interface: each role runs the agent and model the settings name (#698).

The settings are the agents section of `.dokima/settings.yaml` under the current folder (or of the file at the path
in DOKIMA_SETTINGS, where the workflow keeps main's copy, so a branch never picks its own agent or secret) (#794):

    agents:
      subscriptions:
        SUB:
          agent: AGENT      # the adapter dokima/agent_AGENT.py runs it
          key: SECRET       # the repo secret holding the subscription's key or sign-in
      roles:
        ROLE:               # planner, worker or reviewer
          subscription: SUB
          model: MODEL

When that file has no agents section, the old `agents.yml` beside it is read instead, holding the same two groups at
its top. With neither, or for a role they leave out, the role runs on Claude Code with today's model and secret.
There is no fallback: a bad name stops the run before any agent starts, and a failed agent fails it. Any model name
passes; the agent itself refuses one it lacks.

    python3 -m dokima.agents model ROLE
    python3 -m dokima.agents key ROLE
    python3 -m dokima.agents install ROLE
    python3 -m dokima.agents run ROLE PROMPT_FILE OUT

An agent's adapter is the module dokima.agent_AGENT, offering install(), run(prompt, model, out), models(out, log_dir),
report(out) and transcript(log_dir, secrets). Claude Code's is dokima/agent_claude.py.
"""
import importlib
import os
import re
import sys

import yaml

from dokima.setup import SETTINGS, read_settings

TODAY = {"agent": "claude", "model": "claude-opus-5-5", "key": "CLAUDE_CODE_OAUTH_TOKEN"}
ADAPTER = ("install", "run", "models", "report", "transcript")


class Stop(Exception):
    """The settings name something Dokima cannot run; the message names it."""


def settings_path():
    """Where the settings file is read from."""
    return os.environ.get("DOKIMA_SETTINGS") or SETTINGS


def read_file(path):
    """The settings in the file at PATH, empty when missing; Stop when unreadable."""
    if not os.path.exists(path):
        return {}
    try:
        return read_settings(open(path).read())
    except (ValueError, yaml.YAMLError) as e:
        raise Stop(f"{path} cannot be read: {e}")


def agents_section():
    """The agents section and its file; else the old agents file beside it."""
    path = settings_path()
    section = read_file(path).get("agents")
    if section is None:
        old = os.path.join(os.path.dirname(path), "agents.yml")
        return read_file(old), old
    if not isinstance(section, dict):
        raise Stop(f"The agents section of {path} must hold subscriptions and roles.")
    return section, path


def role_settings(role):
    """The role's agent, model and key secret; today's when the settings leave the role out."""
    settings, path = agents_section()
    roles = settings.get("roles")
    given = roles.get(role) if isinstance(roles, dict) else None
    if given is None:
        return dict(TODAY)
    given = given if isinstance(given, dict) else {}
    if not given.get("model"):
        raise Stop(f"The {role} in {path} has no model line, so it cannot start.")
    sub = given.get("subscription", "")
    subs = settings.get("subscriptions")
    found = subs.get(sub) if isinstance(subs, dict) and sub else None
    if not isinstance(found, dict):
        raise Stop(f"The {role} names the subscription '{sub}', which {path} does not list.")
    if not found.get("agent") or not found.get("key"):
        raise Stop(f"The subscription '{sub}' in {path} needs both an agent and a key line.")
    return {"agent": str(found["agent"]), "model": str(given["model"]), "key": str(found["key"])}


def adapter(role):
    """The role's agent adapter and its settings, or Stop naming an agent with no adapter."""
    s = role_settings(role)
    name = s["agent"]
    m = None
    if re.fullmatch(r"[a-z0-9_]+", name):
        try:
            m = importlib.import_module(f"dokima.agent_{name}")
        except ImportError:
            m = None
    if m is None or not all(callable(getattr(m, f, None)) for f in ADAPTER):
        raise Stop(f"The {role}'s subscription names the agent '{name}', which Dokima has no adapter for.")
    return m, s


def model(role):
    """The model the role runs on."""
    return adapter(role)[1]["model"]


def key(role):
    """The name of the secret holding the role's key."""
    return adapter(role)[1]["key"]


def install(role):
    """Install the role's agent; return the install's exit code."""
    return adapter(role)[0].install()


def run(role, prompt, out):
    """Start the role's agent on PROMPT with its model, into OUT; return its exit code."""
    m, s = adapter(role)
    return m.run(prompt, s["model"], out)


def models(role, out, log_dir):
    """Every model the role's agent says it ran."""
    return adapter(role)[0].models(out, log_dir)


def report(role, out):
    """The role's agent's own stats: time, turns, tokens and cost."""
    return adapter(role)[0].report(out)


def transcript(role, log_dir, secrets=()):
    """The role's agent's readable transcript, secrets removed."""
    return adapter(role)[0].transcript(log_dir, list(secrets))


def main(argv):
    """model|key|install ROLE, or run ROLE PROMPT_FILE OUT; exits 1 naming a bad name."""
    usage = "usage: python3 -m dokima.agents model|key|install ROLE, or run ROLE PROMPT_FILE OUT"
    if len(argv) < 3 or argv[1] not in ("model", "key", "install", "run") or (argv[1] == "run" and len(argv) < 5):
        print(usage, file=sys.stderr)
        return 1
    cmd, role = argv[1], argv[2]
    try:
        if cmd == "model":
            print(model(role))
            return 0
        if cmd == "key":
            print(key(role))
            return 0
        if cmd == "install":
            return install(role)
        prompt = open(argv[3]).read()
        return run(role, prompt, argv[4])
    except Stop as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

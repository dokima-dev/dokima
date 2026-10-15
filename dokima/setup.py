"""Setup: the owner gives a subscription's inputs once, and each goes where runs find it.

The owner runs it on their own machine. Agent runs start on a fresh machine, so nothing saved on the owner's
machine reaches them except through a repo secret.
A key goes into a repo secret. A sign-in is done once by the agent's own login, with the region the owner gives, and
the files that login saved go into a repo secret too: the base64 text of a gzip tar, each file named by its path under
the home folder, so a run can unpack it into its own home before the agent starts. The settings file
`.dokima/agents.yml` names each subscription's agent and secret (never the secret itself), and each role's subscription
and model.

    python3 -m dokima.setup needs
    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE [--role ROLE ...] --key
    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE --sign-in --region REGION
"""
import argparse
import base64
import io
import os
import subprocess
import sys
import tarfile

SETTINGS = os.path.join(".dokima", "agents.yml")

# Per agent: its login command (the region follows it) and where that login saves the sign-in, under the home folder.
LOGIN = {"kimi": ["kimi", "login", "--region"]}
SIGN_IN = {"kimi": [".kimi/credentials", ".kimi/config.toml"]}

NEEDS = """A subscription needs:
- membership: the plan you pay for, and the agent it runs (for example kimi or codex).
- region: where the agent's login signs you in (for a sign-in only, for example global).
- sign-in or key: sign in once through the agent's own login, or give an API key; either is stored as a repo secret.
- model: the model each role you name runs on.
"""


class Failed(Exception):
    """A step of setup failed; the message says why."""


def store_secret(name, value):
    """Set the repo secret NAME to VALUE with `gh secret set`, or fail naming it."""
    p = subprocess.run(["gh", "secret", "set", name], input=value, capture_output=True, text=True)
    if p.returncode:
        raise Failed(f"Could not store the repo secret {name}: {p.stderr.strip() or p.stdout.strip()}")


def sign_in(agent, region):
    """Run AGENT's own login with REGION; return its saved files as base64 gzip tar."""
    if agent not in LOGIN:
        raise Failed(f"Setup cannot sign in {agent}; it knows {', '.join(sorted(LOGIN))}. Give a key instead.")
    if subprocess.run([*LOGIN[agent], region]).returncode:
        raise Failed(f"The {agent} login failed, so no sign-in was stored.")
    home = os.path.expanduser("~")
    saved = [p for p in SIGN_IN[agent] if os.path.exists(os.path.join(home, p))]
    if not saved:
        raise Failed(f"The {agent} login saved none of {', '.join(SIGN_IN[agent])}, so no sign-in was stored.")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for p in saved:
            t.add(os.path.join(home, p), arcname=p)
    return base64.b64encode(buf.getvalue()).decode()


def read_settings(text):
    """Read the settings file's block maps (`subscriptions` and `roles`, two levels down) into nested dicts."""
    root, stack = {}, [(-1, None)]
    stack[0] = (-1, root)
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, rest = line.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        if rest.strip():
            stack[-1][1][key.strip()] = rest.strip().strip("'\"")
        else:
            stack[-1][1][key.strip()] = {}
            stack.append((indent, stack[-1][1][key.strip()]))
    return root


def write_settings(settings):
    """The settings as block-style YAML text."""
    lines = []
    for top in ("subscriptions", "roles"):
        lines.append(f"{top}:")
        for name, fields in settings.get(top, {}).items():
            lines.append(f"  {name}:")
            lines += [f"    {k}: {v}" for k, v in fields.items()]
    return "\n".join(lines) + "\n"


def add(a):
    """Store the key or sign-in as a repo secret, then write the settings file."""
    if a.key:
        value = sys.stdin.read().strip()
        if not value:
            raise Failed("No key given on standard input, so nothing was stored.")
    else:
        if not a.region:
            raise Failed("A sign-in needs --region, the region the agent's login signs you in to.")
        value = sign_in(a.agent, a.region)
    store_secret(a.secret, value)
    settings = read_settings(open(SETTINGS).read()) if os.path.exists(SETTINGS) else {}
    settings.setdefault("subscriptions", {})[a.name] = {"agent": a.agent, "key": a.secret}
    for role in a.role:
        settings.setdefault("roles", {})[role] = {"subscription": a.name, "model": a.model}
    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w") as f:
        f.write(write_settings(settings))
    print(f"Stored {a.secret} and wrote {a.name} into {SETTINGS}.")


def main(argv):
    """needs | add SUB ...: list a subscription's inputs, or store one.

    Exits 1 saying why a step failed."""
    parser = argparse.ArgumentParser(prog="python3 -m dokima.setup")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("needs", help="list the inputs a subscription needs")
    p = sub.add_parser("add", help="store a subscription's key or sign-in and write the settings file")
    p.add_argument("name")
    p.add_argument("--agent", required=True)
    p.add_argument("--secret", required=True, help="the repo secret's name")
    p.add_argument("--model", required=True)
    p.add_argument("--role", action="append", required=True)
    how = p.add_mutually_exclusive_group(required=True)
    how.add_argument("--key", action="store_true", help="read the key from standard input")
    how.add_argument("--sign-in", action="store_true", help="sign in through the agent's own login")
    p.add_argument("--region")
    a = parser.parse_args(argv)
    if a.cmd == "needs":
        print(NEEDS, end="")
        return 0
    try:
        add(a)
    except Failed as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

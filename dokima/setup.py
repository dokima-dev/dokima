"""Setup: the owner gives a subscription's inputs once, and each goes where runs find it.

The owner runs it on their own machine. Agent runs start on a fresh machine, so nothing saved on the owner's
machine reaches them except through a repo secret.
A key goes into a repo secret. A sign-in is done once by the agent's own login, with the region the owner gives, and
the files that login saved go into a repo secret too: the base64 text of a gzip tar, each file named by its path under
the home folder, so a run can unpack it into its own home before the agent starts. The agents section of the settings
file `.dokima/settings.yaml` names each subscription's agent and secret (never the secret itself), and each role's
subscription and model (#794). Setup changes only those lines: every other setting and every comment stays. A file
with no agents section yet gets one, starting from the old `.dokima/agents.yml` when the repo still has it.

    python3 -m dokima.setup needs
    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE [--role ROLE ...] --key
    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE --sign-in --region REGION
    python3 -m dokima.setup auto-approve OWNER/REPO

auto-approve turns on `merge.auto_approve` (#934): it lets Dokima's app bypass the required review of `branch.default`
(main when empty), keeping its required checks, then saves the setting.
"""
import argparse
import base64
import copy
import io
import json
import os
import re
import subprocess
import sys
import tarfile

import yaml

from dokima import settings
from dokima.settings import REPO_FILE as SETTINGS

OLD_SETTINGS = os.path.join(".dokima", "agents.yml")  # where the agents section lived before #794

# Per agent: its login command (the region follows it) and where that login saves the sign-in, under the home folder.
LOGIN = {"kimi": ["kimi", "login", "--region"]}
SIGN_IN = {"kimi": [".kimi-code/credentials", ".kimi-code/config.toml", ".kimi-code/device_id", ".kimi-code/region"]}

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
    """The settings file's text read as YAML: a map, empty when the text is."""
    got = yaml.safe_load(text)
    if got is None:
        return {}
    if not isinstance(got, dict):
        raise ValueError(f"it must hold a map of settings, not {type(got).__name__}")
    return got


KEY_LINE = re.compile(r"""^( *)([A-Za-z0-9_][^:#]*?|'[^']*'|"[^"]*") *:( .*|)$""")


def content(line):
    """Whether LINE holds a setting, not only blanks or a comment."""
    return bool(line.strip()) and not line.lstrip().startswith("#")


def indent(line):
    """LINE's indent in spaces."""
    return len(line) - len(line.lstrip(" "))


def value_and_comment(rest):
    """The text after a key's colon, split into its value and its comment."""
    start = len(rest) - len(rest.lstrip())
    i = start
    if rest[start:start + 1] in ("'", '"'):
        end = rest.find(rest[start], start + 1)
        i = end + 1 if end > 0 else len(rest)
    m = re.search(r"(^|\s)#", rest[i:])
    if not m:
        return rest.strip(), ""
    cut = i + m.start()
    while cut > 0 and rest[cut - 1] == " ":
        cut -= 1
    return rest[:cut].strip(), rest[cut:]


def scalar(value):
    """VALUE written so YAML reads it back as the same string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    plain = str(value)
    try:
        if plain.strip() == plain and yaml.safe_load(f"k: {plain}") == {"k": plain}:
            return plain
    except yaml.YAMLError:
        pass
    return json.dumps(plain)


def block_end(lines, at):
    """Where the block under the key at line AT ends: after its last setting line."""
    end = at + 1
    for i in range(at + 1, len(lines)):
        if not content(lines[i]):
            continue
        if indent(lines[i]) < indent(lines[at]) or (indent(lines[i]) == indent(lines[at])
                                                     and not lines[i].lstrip().startswith("-")):
            break
        end = i + 1
    return end


def set_line(lines, path, value):
    """Set PATH to the string VALUE in the file's LINES, adding missing keys; comments stay."""
    start, end, depth = 0, len(lines), 0
    for n, key in enumerate(path):
        inside = [i for i in range(start, end) if content(lines[i])]
        at_indent = indent(lines[inside[0]]) if inside else depth
        found = None
        for i in inside:
            m = KEY_LINE.match(lines[i])
            if m and len(m.group(1)) == at_indent and m.group(2).strip("'\"") == key:
                found = (i, m)
                break
        if found is None:
            new = [" " * (at_indent + 2 * k) + f"{name}:" for k, name in enumerate(path[n:])]
            new[-1] += f" {scalar(value)}"
            lines[end:end] = new
            return
        i, m = found
        old, comment = value_and_comment(m.group(3))
        head = lines[i][:len(m.group(1)) + len(m.group(2))] + ":"
        if n == len(path) - 1:
            lines[i] = f"{head} {scalar(value)}{comment}"
            return
        if old:
            if yaml.safe_load(old) not in (None, {}):
                raise Failed(f"Setup cannot save into {'.'.join(path[:n + 1])} in {SETTINGS}: it is written on one "
                             "line. Write it one setting per line and run setup again.")
            lines[i] = head + comment
        start, end, depth = i + 1, block_end(lines, i), at_indent + 2


def saved_text(text, changes):
    """TEXT with each (path, value) of CHANGES set; fails if another setting would change."""
    want = copy.deepcopy(read_settings(text))
    lines = text.splitlines()
    for path, value in changes:
        here = want
        for key in path[:-1]:
            if not isinstance(here.get(key), dict):
                here[key] = {}
            here = here[key]
        here[path[-1]] = value
        set_line(lines, path, value)
    out = "\n".join(lines) + "\n"
    if read_settings(out) != want:
        raise Failed(f"Setup could not save into {SETTINGS} without changing other settings, so nothing was stored. "
                     "Add the lines by hand.")
    return out


def add(a):
    """Store the key or sign-in as a repo secret, then save the agents section."""
    if a.key:
        value = sys.stdin.read().strip()
        if not value:
            raise Failed("No key given on standard input, so nothing was stored.")
    else:
        if not a.region:
            raise Failed("A sign-in needs --region, the region the agent's login signs you in to.")
        value = sign_in(a.agent, a.region)
    text = open(SETTINGS).read() if os.path.exists(SETTINGS) else ""
    try:
        changes = []
        if "agents" not in read_settings(text) and os.path.exists(OLD_SETTINGS):
            before = read_settings(open(OLD_SETTINGS).read())
            for top in ("subscriptions", "roles"):
                for name, fields in (before.get(top) if isinstance(before.get(top), dict) else {}).items():
                    for k, v in (fields if isinstance(fields, dict) else {}).items():
                        changes.append((["agents", top, str(name), str(k)], str(v)))
        changes += [(["agents", "subscriptions", a.name, "agent"], a.agent),
                    (["agents", "subscriptions", a.name, "key"], a.secret)]
        for role in a.role:
            changes += [(["agents", "roles", role, "subscription"], a.name),
                        (["agents", "roles", role, "model"], a.model)]
        text = saved_text(text, changes)
    except (ValueError, yaml.YAMLError) as e:
        raise Failed(f"Setup could not read {SETTINGS}, so nothing was stored: {e}")
    store_secret(a.secret, value)
    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w") as f:
        f.write(text)
    print(f"Stored {a.secret} and wrote {a.name} into {SETTINGS}.")


def gh_json(*args, stdin=None):
    """`gh api ARGS` read as JSON, or fail with GitHub's reason."""
    p = subprocess.run(["gh", "api", *args], input=stdin, capture_output=True, text=True)
    if p.returncode:
        raise Failed(f"GitHub refused `gh api {' '.join(args)}`: {p.stderr.strip() or p.stdout.strip()}")
    return json.loads(p.stdout or "{}")


def auto_approve(repo):
    """Let Dokima's app bypass the default branch's required review, then save `merge.auto_approve: true`.

    Only the rule's review part is written, so the checks the branch requires stay."""
    got = settings.read()
    branch = (got.get("branch") or {}).get("default") or "main"
    app = (got.get("bot") or {}).get("slug") or "dokima-runtime"
    path = f"repos/{repo}/branches/{branch}/protection/required_pull_request_reviews"
    allowed = gh_json(path).get("bypass_pull_request_allowances") or {}
    bypass = {"users": [u["login"] for u in allowed.get("users") or []],
              "teams": [t["slug"] for t in allowed.get("teams") or []],
              "apps": [a["slug"] for a in allowed.get("apps") or []]}
    if app not in bypass["apps"]:
        bypass["apps"].append(app)
        gh_json("-X", "PATCH", path, "--input", "-", stdin=json.dumps({"bypass_pull_request_allowances": bypass}))
    text = open(SETTINGS).read() if os.path.exists(SETTINGS) else ""
    try:
        text = saved_text(text, [(["merge", "auto_approve"], True)])
    except (ValueError, yaml.YAMLError) as e:
        raise Failed(f"Setup could not read {SETTINGS}, so auto approve was not saved: {e}")
    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w") as f:
        f.write(text)
    print(f"{app} may now bypass {branch}'s required review, and {SETTINGS} turns auto approve on.")


def main(argv):
    """needs | add SUB ... | auto-approve REPO: list inputs, store one, or opt in.

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
    p = sub.add_parser("auto-approve", help="let Dokima approve and merge its own pull requests")
    p.add_argument("repo", help="OWNER/REPO")
    a = parser.parse_args(argv)
    if a.cmd == "needs":
        print(NEEDS, end="")
        return 0
    try:
        auto_approve(a.repo) if a.cmd == "auto-approve" else add(a)
    except Failed as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

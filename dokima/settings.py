"""Dokima's settings: the shipped defaults with a repo's own settings file merged over them (#779).

`python3 -m dokima.settings`, run in a repo, prints the merged settings as JSON on standard output;
`python3 -m dokima.settings setup` prints the setup group as `name=value` lines for a workflow's GITHUB_OUTPUT, so
each test workflow sets up the repo's Python, test tools and install command as they say (#794);
`python3 -m dokima.settings env` prints the test commands, test folder, branches, bot, co-author and owner docs file as `NAME=value` lines for a
workflow's GITHUB_ENV, so workflows run and push as the repo's settings say (#795, #796). The defaults are
`dokima/defaults.yaml`, beside this file; the repo's file is `.dokima/settings.yaml`, and names only what differs.
Groups merge key by key, the repo winning; a list replaces the default list whole, except gates and prompt additions,
which merge with the default ones by name. An unknown setting is left out with a warning suggesting the closest known
name. A locked setting fails the run, naming it.
"""
import difflib
import json
import os
import shlex
import subprocess
import sys

import yaml

DEFAULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.yaml")
REPO_FILE = os.path.join(".dokima", "settings.yaml")
LOCKED = "integrity"  # the group a repo may never set
BY_NAME = {"gates.required", "prompts.append"}  # lists that merge with the default ones by name


class Locked(Exception):
    """A repo's settings file sets a locked setting."""


def load(path):
    """The settings map in the YAML file at PATH; empty when missing or empty."""
    if not os.path.isfile(path):
        return {}
    with open(path) as f:
        got = yaml.safe_load(f)
    if got is None:
        return {}
    if not isinstance(got, dict):
        raise ValueError(f"{path} must hold a map of settings, not {type(got).__name__}")
    return got


def entry_name(entry):
    """An entry's name: the text itself, or a map's name field."""
    return entry.get("name") if isinstance(entry, dict) else entry


def by_name(base, mine):
    """BASE's entries with MINE's merged in by name, a same-named one taking its place."""
    out = list(base)
    for entry in mine:
        at = next((i for i, e in enumerate(out) if entry_name(e) == entry_name(entry)), None)
        if at is None:
            out.append(entry)
        else:
            out[at] = entry
    return out


def merge(base, mine, warn, path=""):
    """BASE with MINE merged over it key by key; unknown keys warned of, dropped."""
    out = dict(base)
    for key, value in mine.items():
        name = f"{path}{key}"
        if key not in base:
            near = difflib.get_close_matches(str(key), [str(k) for k in base], n=1)
            hint = f"; did you mean {path}{near[0]}?" if near else "."
            warn(f"Dokima does not know the setting {name}{hint} It is ignored.")
        elif isinstance(base[key], dict) and isinstance(value, dict):
            out[key] = merge(base[key], value, warn, f"{name}.")
        elif name in BY_NAME and isinstance(base[key], list) and isinstance(value, list):
            out[key] = by_name(base[key], value)
        else:
            out[key] = value
    return out


def read(repo=".", warn=None):
    """The merged settings for the repo at REPO; raises Locked on a locked setting."""
    warn = warn or (lambda message: print(f"::warning title=Unknown setting::{message}", file=sys.stderr))
    mine = load(os.path.join(repo, REPO_FILE))
    locked = mine.get(LOCKED)
    if locked is not None:
        names = [f"{LOCKED}.{k}" for k in locked] if isinstance(locked, dict) and locked else [LOCKED]
        raise Locked(f"{REPO_FILE} sets the locked setting {', '.join(names)}; a repo may not change it.")
    return merge(load(DEFAULTS), mine, warn)


def shown_as(name, got=None):
    """The name GitHub shows for the gate NAME in this repo (#846).

    Its `shown_as` in the merged settings GOT, else NAME."""
    got = read() if got is None else got
    for entry in (got.get("gates") or {}).get("required") or []:
        if isinstance(entry, dict) and entry.get("name") == name:
            return entry.get("shown_as") or name
    return name


def shown_prefix(name, got=None):
    """What GitHub puts before a check named beside the gate NAME (#846).

    E.g. `dokima / acceptance-criteria / `; empty when GitHub shows that gate by its plain name."""
    shown = shown_as(name, got)
    return shown[:-len(name)] if shown != name and shown.endswith(name) else ""


def setup_lines(got):
    """The setup group as `name=value` lines; a value on several lines fails."""
    lines = []
    for name, value in got["setup"].items():
        value = "" if value is None else str(value)
        if "\n" in value:
            raise ValueError(f"setup.{name} in {REPO_FILE} must be one line")
        lines.append(f"{name}={value}")
    return "\n".join(lines)


def github_default_branch():
    """The repo's default branch as GitHub names it, from the event file or `gh` (#787).

    Raises ValueError when GitHub gives none."""
    try:
        with open(os.environ["GITHUB_EVENT_PATH"]) as f:
            name = ((json.load(f) or {}).get("repository") or {}).get("default_branch")
    except (KeyError, OSError, ValueError, AttributeError):
        name = None
    if not name:
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        try:
            name = subprocess.run(["gh", "api", f"repos/{repo}", "--jq", ".default_branch"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as e:
            why = " ".join((getattr(e, "stderr", None) or str(e)).split())
            raise ValueError(f"the default branch is unknown: branch.default is empty and GitHub did not give "
                             f"{repo or 'the repo'}'s default branch ({why})") from e
    if not name:
        raise ValueError("the default branch is unknown: branch.default is empty and GitHub gave no default branch")
    return name


def env_lines(got):
    """The settings workflows run and push by, as `NAME=value` lines; multi-line values fail.

    The all-tests command leaves out each test on the exclude list; the per-criterion command must name {test}. An
    empty default branch is GitHub's own default branch (#787)."""
    tests = got["tests"]
    run_all = " ".join([str(tests["run_all"])] + [f"--deselect {shlex.quote(str(t))}" for t in tests.get("exclude") or []])
    if "{test}" not in str(tests["run_one"]):
        raise ValueError(f"tests.run_one in {REPO_FILE} must name {{test}}, where each criterion's tests go")
    values = {"TESTS_RUN_ALL": run_all, "TESTS_RUN_ONE": tests["run_one"], "TESTS_AFFECTED": tests["affected"],
              "TESTS_DIR": tests["dir"], "DEFAULT_BRANCH": got["branch"]["default"] or github_default_branch(),
              "RECORDS_BRANCH": got["records"]["branch"], "BOT_SLUG": got["bot"]["slug"],
              "CO_AUTHOR": got["co_author"], "OWNER_DOCS": got["owner_docs"]}
    lines = []
    for name, value in values.items():
        value = "" if value is None else str(value)
        if "\n" in value:
            raise ValueError(f"{name.lower()} in {REPO_FILE} must be one line")
        lines.append(f"{name}={value}")
    return "\n".join(lines)


def main(argv=()):
    """Prints the merged settings as JSON, or one mode's lines; exits 1 saying why."""
    try:
        got = read()
        if list(argv) == ["setup"]:
            print(setup_lines(got))
            return 0
        if list(argv) == ["env"]:
            print(env_lines(got))
            return 0
    except Locked as e:
        print(f"::error title=Locked setting::{e}", file=sys.stderr)
        return 1
    except (OSError, ValueError, yaml.YAMLError) as e:
        print(f"::error title=Settings not read::{e}", file=sys.stderr)
        return 1
    print(json.dumps(got, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

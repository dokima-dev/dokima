"""Dokima's settings: the shipped defaults with a repo's own settings file merged over them (#779).

`python3 -m dokima.settings`, run in a repo, prints the merged settings as JSON on standard output. The defaults are
`dokima/defaults.yaml`, beside this file; the repo's file is `.dokima/settings.yaml`, and names only what differs.
Groups merge key by key, the repo winning; a list replaces the default list whole, except gates and prompt additions,
which merge with the default ones by name. An unknown setting is left out with a warning suggesting the closest known
name. A locked setting fails the run, naming it.
"""
import difflib
import json
import os
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


def main():
    """Prints the merged settings as JSON; exits 1, saying why, when they cannot be used."""
    try:
        got = read()
    except Locked as e:
        print(f"::error title=Locked setting::{e}", file=sys.stderr)
        return 1
    except (OSError, ValueError, yaml.YAMLError) as e:
        print(f"::error title=Settings not read::{e}", file=sys.stderr)
        return 1
    print(json.dumps(got, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

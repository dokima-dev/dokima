"""The fence: after the worker stops, only in-scope changes survive and the planner's tests are exactly as committed.

The judges (all tests, each criterion's check) run on fresh machines from what gets pushed, so nothing the worker does to
its own machine reaches them. What gets pushed is decided here, by code: every test file and test setup file is put back
to the build's starting commit, and every other change outside the plan's scope is undone. The dropped paths are listed
so the owner sees them.
"""
import json
import os
import re
import subprocess
import sys

TEST_SETUP = {"conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"}


def scope_from(plan):
    """A plan's scope: every file its criteria list, plus its tests' files, sorted."""
    files = {f.strip() for c in plan.get("acceptance_criteria", []) + plan.get("non_functional", [])
             for f in c.get("files", [])}
    return sorted(files | {t.split("::")[0].strip() for names in plan.get("tests", {}).values() for t in names})


def is_test(path):
    """Say whether a path is a test or test setup file, which the worker may never change."""
    name = os.path.basename(path)
    return path.startswith("tests/") or "/tests/" in path or name.startswith("test_") or name in TEST_SETUP


def git(*args):
    """Run git in the current repo and return its output."""
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def fence(base, scope, clashed=()):
    """Undo every change since base that is a test file or outside scope; return the dropped paths, sorted.

    `clashed` are the files that clashed when main was merged into base: the worker's resolution of one is kept even
    outside scope, since base holds it with conflict markers; main's own changes are part of base and never dropped."""
    changed = set(git("diff", "--name-only", base).split()) | set(git("ls-files", "--others", "--exclude-standard").split())
    allowed = set(scope) | set(clashed)
    dropped = sorted(p for p in changed if (is_test(p) and p not in TEST_SETUP & set(scope)) or p not in allowed)
    for p in dropped:
        if subprocess.run(["git", "cat-file", "-e", f"{base}:{p}"], capture_output=True).returncode == 0:
            git("checkout", base, "--", p)
        elif os.path.exists(p):
            os.remove(p)
    return dropped


MARKERS = re.compile(r"(?m)^(<<<<<<<|=======|>>>>>>>)( |$)")


def marked(paths):
    """The paths that still hold a conflict marker line, sorted."""
    return sorted(p for p in paths if os.path.isfile(p) and MARKERS.search(open(p, errors="replace").read()))


def main(argv):
    """fence BASE PLAN [CLASHED]: apply the fence and print each dropped path.

    PLAN is plan.json; CLASHED lists the files that clashed with main, when that file exists. Exits 1 saying which
    clashed files still hold conflict markers."""
    scope = scope_from(json.load(open(argv[2])))
    clashed = open(argv[3]).read().split() if len(argv) > 3 and os.path.exists(argv[3]) else []
    dropped = fence(argv[1], scope, clashed) if clashed else fence(argv[1], scope)
    for p in dropped:
        print(p)
    left = marked(clashed)
    if left:
        print(f"Conflict markers are still in {', '.join(left)}: the clash with main is not resolved.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""One command draws a card demo with swapped functions and shows what changed (#585).

Story 1 of #584. The owner's words: "One command renders any issue's card with the real card code, with named card
functions swapped for a run only, writes nothing to the repo or to GitHub, and shows the lines that differ from the
unchanged card."

The command, run from the repo root:

    REPO=owner/name python3 -m dokima.demo N --swap NAME=PATH [--swap NAME=PATH ...]

It reads issue N the way the card code does, draws its card twice with the real card code (`dokima.card.render`, put
above the owner's part with `dokima.body.redraw`): once unchanged, once with each named function of `dokima.card`
replaced, for that run only, by the same-named function in the draft file PATH. It prints only the lines that differ,
as a unified diff with no context lines (`-` the unchanged card, `+` the swapped one), and exits 0. A draft file
without the named function stops the command with an error naming it.

How the tests run it. A fake `gh` on PATH answers only the reads the card code makes (the issue, its comments and
events, its pull request, checks and reviews, its blocked-by links, the worker's runs and files, which it has none of)
and logs every call. A call that would change anything on GitHub is logged as a write and answered as done, so a test
can say which write was sent. A call it does not know fails loudly, naming the call. `dokima.demo.main(argv)` is also
called in-process, with the same fake on PATH, to check the card code is put back after the run.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from dokima import card  # noqa: E402

REPO = "acme/app"
NUMBER = 7
ASK = "Make the card shine."

FAKE_GH = r'''#!/usr/bin/env python3
"""A fake gh for the card demo's tests: answers the card code's reads, logs every call."""
import json, os, sys

args = sys.argv[1:]
repo, n, pr_n = os.environ["FAKE_REPO"], os.environ["FAKE_NUMBER"], os.environ.get("FAKE_PR")
log = os.environ["FAKE_GH_LOG"]


def out(kind, value=None, code=0, err=""):
    with open(log, "a") as f:
        f.write(json.dumps({"kind": kind, "argv": args}) + "\n")
    if value is not None:
        print(json.dumps(value))
    if err:
        print(err, file=sys.stderr)
    sys.exit(code)


def has(*words):
    return all(w in args for w in words)


method = args[args.index("-X") + 1].upper() if "-X" in args else "GET"
if args[:2] in (["issue", "edit"], ["issue", "comment"], ["pr", "edit"], ["pr", "comment"], ["issue", "close"]):
    out("write", {})
if args[:1] == ["api"] and method != "GET":
    out("write", {})
if args[:1] == ["api"] and any(a.startswith(("-f", "-F", "--input", "--field", "--raw-field")) for a in args[2:]) \
        and args[1] != "graphql":
    out("write", {})
pr = {"number": int(pr_n), "title": "Make the card shine", "body": "Closes #" + n, "state": "open",
      "merged": False, "draft": False, "head": {"sha": "abc123", "ref": "try/issue-" + n},
      "html_url": "https://github.com/" + repo + "/pull/" + pr_n, "user": {"login": "dokima-runtime[bot]"},
      "labels": []} if pr_n else None
if args[:2] == ["api", "graphql"]:
    q = next((a for a in args if a.startswith("query=")), "")
    if "mutation" in q:
        out("write", {})
    if "issue(number:" in q:
        out("read", {"data": {"repository": {"issue": {
            "number": int(n), "title": "Make the card shine", "body": os.environ["FAKE_BODY"],
            "url": "https://github.com/" + repo + "/issues/" + n, "userContentEdits": {"nodes": []}}}}})
    out("unknown", code=1, err="fake gh: unknown graphql query (HTTP 400)")
if args[:2] == ["issue", "view"]:
    out("read", {"number": int(n), "title": "Make the card shine", "body": os.environ["FAKE_BODY"], "comments": []})
if args[:2] == ["pr", "list"]:
    head = args[args.index("--head") + 1]
    out("read", [{"number": int(pr_n)}] if pr_n and head == "try/issue-" + n else [])
if args[:2] == ["pr", "view"]:
    out("read", {"comments": [], "reviews": []})
if args[:1] == ["api"]:
    path = args[1]
    base = "repos/" + repo + "/"
    if path.startswith(base + "contents/"):
        out("read", code=1, err="gh: Not Found (HTTP 404)")
    if path.startswith(base + "issues/" + n + "/events"):
        out("read", [])
    if path.startswith(base + "issues/") and "/dependencies/" in path:
        out("read", [])
    if path.startswith(base + "actions/workflows/worker.yml/runs"):
        out("read", {"workflow_runs": []})
    if path.startswith(base + "pulls?head="):
        out("read", [pr] if pr and path.split("head=")[1].startswith(repo.split("/")[0] + ":try/issue-" + n + "&") else [])
    if pr and path == base + "pulls/" + pr_n:
        out("read", pr)
    if pr and path.startswith(base + "pulls/" + pr_n + "/reviews"):
        out("read", [])
    if pr and path.startswith(base + "pulls/" + pr_n + "/comments"):
        out("read", [])
    if path.startswith(base + "commits/abc123/check-runs"):
        out("read", {"total_count": 0, "check_runs": []})
out("unknown", code=1, err="fake gh: unknown call " + " ".join(args) + " (HTTP 400)")
'''

DRAFT = '''"""A draft status line for the card demo's tests."""


def status_line(repo, stage, todo):
    """The stage, drafted."""
    return "**Drafted " + stage + "**"
'''

SAME = '''"""A draft that draws the status line exactly as the card code does."""


def status_line(repo, stage, todo):
    """The stage, as today."""
    return "**" + stage + "**" + (" · Needs you: " + todo if todo else "")
'''

NONE = '''"""A draft file without the function it is named for."""


def something_else():
    """Not a card function."""
    return None
'''

RAISES = '''"""A draft whose status line fails while the card is drawn."""


def status_line(repo, stage, todo):
    """Fails on purpose."""
    raise RuntimeError("draft broke")
'''


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A fake GitHub on PATH holding issue 7, its call log and a draft folder."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "FAKE_GH_LOG": str(log), "FAKE_REPO": REPO,
           "FAKE_NUMBER": str(NUMBER), "FAKE_BODY": ASK, "REPO": REPO, "PYTHONDONTWRITEBYTECODE": "1"}
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("FAKE_PR", raising=False)
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    return {"log": log, "drafts": drafts, "tmp": tmp_path}


def draft(world, name, text):
    """Write a draft file and return its path."""
    p = world["drafts"] / name
    p.write_text(text)
    return str(p)


def run(*argv):
    """Run the demo command from the repo root, as the owner does."""
    return subprocess.run([sys.executable, "-m", "dokima.demo", *argv], cwd=ROOT, capture_output=True, text=True,
                          env=dict(os.environ), timeout=60)


def calls(world):
    """Every gh call the fake logged."""
    if not world["log"].exists():
        return []
    return [json.loads(line) for line in world["log"].read_text().splitlines() if line.strip()]


def diff_lines(stdout):
    """The output's lines that are not a unified diff's headers."""
    return [line for line in stdout.splitlines() if line and not line.startswith(("---", "+++", "@@"))]


def repo_state():
    """What git sees changed or untracked in the repo, and the card code's text."""
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True,
                            text=True, check=True).stdout
    with open(os.path.join(ROOT, "dokima", "card.py"), "rb") as f:
        return status, f.read()


def test_demo_shows_changed_lines(world, record_property):
    """The demo prints only the card lines the swapped function changed.

    Proves 585.1. Swaps the status line for a draft on an issue in Backlog and checks the output holds the real card's line as a
    minus line, the draft's as a plus line, and no unchanged line of the card or the owner's ask."""
    record_property("proves", "585.1")
    r = run(str(NUMBER), "--swap", f"status_line={draft(world, 'draft.py', DRAFT)}")
    assert r.returncode == 0, f"585.1: the demo did not finish (exit {r.returncode}): {r.stdout}{r.stderr}"
    lines = diff_lines(r.stdout)
    assert "-**Backlog**" in lines, f"585.1: the unchanged card's status line is not shown as removed: {r.stdout!r}"
    assert "+**Drafted Backlog**" in lines, f"585.1: the swapped card's status line is not shown as added: {r.stdout!r}"
    extra = [line for line in lines if not line.startswith(("+", "-"))]
    assert not extra, f"585.1: the demo shows lines that did not change: {extra}"
    assert not any(ASK in line for line in lines), f"585.1: the owner's unchanged ask is shown: {r.stdout!r}"


def test_demo_same_function_shows_no_lines(world, record_property):
    """A draft that draws the same card shows no changed lines.

    Proves 585.1. Swaps the status line for one that draws it as today and checks the demo finishes with no plus or minus line."""
    record_property("proves", "585.1")
    r = run(str(NUMBER), "--swap", f"status_line={draft(world, 'same.py', SAME)}")
    assert r.returncode == 0, f"585.1: the demo did not finish (exit {r.returncode}): {r.stdout}{r.stderr}"
    changed = [line for line in diff_lines(r.stdout) if line.startswith(("+", "-"))]
    assert not changed, f"585.1: a swap that changes nothing still shows changed lines: {changed}"


def test_demo_draft_missing_function(world, record_property):
    """A draft file without the named function stops the demo with an error naming it.

    Proves 585.1. Names status_line in a draft file that has no such function and checks the demo exits non-zero and says
    status_line, while a draft that has it finishes."""
    record_property("proves", "585.1")
    ok = run(str(NUMBER), "--swap", f"status_line={draft(world, 'draft.py', DRAFT)}")
    assert ok.returncode == 0, f"585.1: the demo did not finish with a good draft: {ok.stdout}{ok.stderr}"
    r = run(str(NUMBER), "--swap", f"status_line={draft(world, 'none.py', NONE)}")
    assert r.returncode != 0, f"585.1: a draft without status_line did not stop the demo: {r.stdout!r}"
    assert "status_line" in r.stdout + r.stderr, \
        f"585.1: the error does not name the missing function: {r.stdout}{r.stderr}"


def main_in_process(argv):
    """Run dokima.demo.main(argv) here, returning its exit code or the error it raised."""
    from dokima import demo
    try:
        return demo.main(argv) or 0
    except SystemExit as e:
        return e.code or 0
    except Exception as e:  # noqa: BLE001 - a draft's error may surface as is
        return e


def test_demo_puts_card_back(world, capsys, record_property):
    """After the demo, the card code draws with its own functions again.

    Proves 585.2. Runs the demo in this process with a swapped status line, checks the swap showed in its output, then checks
    every function of the card code is the one it was before the run."""
    record_property("proves", "585.2")
    before = {k: v for k, v in vars(card).items() if callable(v)}
    original = card.status_line
    got = main_in_process([str(NUMBER), "--swap", f"status_line={draft(world, 'draft.py', DRAFT)}"])
    out = capsys.readouterr().out
    assert got == 0, f"585.2: the demo did not finish: {got!r} {out}"
    assert "+**Drafted Backlog**" in out, f"585.2: the swapped function was not used in the run: {out!r}"
    assert card.status_line is original, "585.2: the drafted status line was left in the card code after the run"
    after = {k: v for k, v in vars(card).items() if callable(v)}
    changed = sorted(k for k in set(before) | set(after) if before.get(k) is not after.get(k))
    assert not changed, f"585.2: card functions differ after the run: {changed}"


def test_demo_puts_card_back_after_draft_fails(world, capsys, record_property):
    """A draft that fails mid-run still leaves the card code as it was.

    Proves 585.2. Runs the demo with a status line that raises, and checks the card's own status line is back afterwards."""
    record_property("proves", "585.2")
    original = card.status_line
    got = main_in_process([str(NUMBER), "--swap", f"status_line={draft(world, 'raises.py', RAISES)}"])
    capsys.readouterr()
    assert got != 0, "585.2: a draft that raised did not fail the demo"
    assert card.status_line is original, "585.2: a failed run left the drafted status line in the card code"


def assert_writes_nothing(world):
    """Run the demo; check it sent no GitHub write and left the repo alone."""
    before = repo_state()
    r = run(str(NUMBER), "--swap", f"status_line={draft(world, 'draft.py', DRAFT)}")
    assert r.returncode == 0, f"585.3: the demo did not finish (exit {r.returncode}): {r.stdout}{r.stderr}"
    got = calls(world)
    assert got, "585.3: the demo never read the issue from GitHub"
    writes = [c["argv"] for c in got if c["kind"] == "write"]
    assert not writes, f"585.3: the demo sent writes to GitHub: {writes}"
    unknown = [c["argv"] for c in got if c["kind"] == "unknown"]
    assert not unknown, f"585.3: the demo made calls the fake does not know: {unknown}"
    assert repo_state() == before, "585.3: the demo changed files in the repo"


def test_demo_writes_nothing(world, record_property):
    """The demo reads GitHub but writes nothing to it or to the repo.

    Proves 585.3. Runs the demo on an issue with no pull request, with every gh call logged, and compares the repo's git status
    and the card code before and after."""
    record_property("proves", "585.3")
    assert_writes_nothing(world)


def test_demo_writes_nothing_with_pull_request(world, monkeypatch, record_property):
    """On an issue with a pull request, the demo writes nothing there either.

    Proves 585.3. Gives the issue an open pull request and checks no gh write was sent and the repo is unchanged."""
    record_property("proves", "585.3")
    monkeypatch.setenv("FAKE_PR", "12")
    assert_writes_nothing(world)

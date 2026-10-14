"""The command shows what a branch changes; real GitHub checks run only at night.

#626.

Story 3 of #584. Builds on `tools/visuals.py draw` (#624) and `preview` (#625).

1. A new subcommand, run from the root of a checkout:

       python3 tools/visuals.py diff ISSUE --branch BRANCH --repo OWNER/NAME

   draws the issue exactly as `draw` does twice, once with main's code and once with BRANCH's, and prints only the
   lines that differ as a unified diff: main's lines start with `-`, BRANCH's with `+`, every line both drawings share
   is left unmarked or out. When nothing differs it prints `No line differs from main.` and exits 0. An issue GitHub
   cannot give, or a BRANCH that does not exist, ends it with a non-zero exit and one plain message naming it, never a
   traceback.

2. Checks that post to or read from real GitHub (the card-gallery previews) live in `nightly/`, outside `tests/`, so
   the all tests check (`pytest tests`, in full-suite.yml) never runs them. `.github/workflows/visuals-nightly.yml`
   runs them on a schedule (and on Run workflow), never on a pull request, push or merge queue, with a GitHub token.
   They call the real `gh`: when GitHub refuses, they fail and say GitHub's reason; they never skip.

3. The tool stays ours: nothing in the `dokima/` package names it, and no workflow but the nightly one runs it.

How the tests prove it: the throwaway checkout, its `visual-test` branch and the fake GitHub of #624's tests
(`tests/test_visuals_draw.py`) are reused for the diff. The nightly checks are run from a throwaway copy of the repo
with a fake `gh` that logs every call and refuses it, so no test here reaches real GitHub. Workflows are read with the
repo's own YAML reader (tests/test_start.py's load_yaml).
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_start as ts  # noqa: E402
from tests import test_visuals_draw as story1  # noqa: E402
from tests.test_visuals_draw import ISSUE, PLAN_SUMMARY, REPO  # noqa: E402

WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
NIGHTLY_FLOW = os.path.join(WORKFLOWS, "visuals-nightly.yml")
NIGHTLY = os.path.join(ROOT, "nightly")
SAME = "No line differs from main."
GALLERY = "dokima-dev/card-gallery"

# Logs every call and refuses it, as GitHub does a bad token.
REFUSING_GH = r'''#!/usr/bin/env python3
import json, os, sys
with open(os.environ["VISUALS_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
sys.stderr.write("gh: Bad credentials (HTTP 401)\n")
sys.exit(1)
'''


@pytest.fixture(scope="module")
def place(tmp_path_factory):
    """#624's throwaway checkout, its `visual-test` branch and its fake `gh`."""
    base = tmp_path_factory.mktemp("diff")
    repo = base / "checkout"
    shutil.copytree(os.path.join(ROOT, "dokima"), repo / "dokima", ignore=shutil.ignore_patterns("__pycache__"))
    if os.path.isdir(os.path.join(ROOT, "tools")):
        shutil.copytree(os.path.join(ROOT, "tools"), repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    story1.git(repo, "init", "-q", "-b", "main")
    story1.git(repo, "config", "user.name", "Test")
    story1.git(repo, "config", "user.email", "test@example.com")
    story1.git(repo, "add", "-A")
    story1.git(repo, "commit", "-q", "-m", "main")
    story1.git(repo, "checkout", "-q", "-b", "visual-test")
    with open(repo / "dokima" / "card.py", "a") as f:
        f.write(story1.BRANCH_CARD)
    with open(repo / "dokima" / "agent.py", "a") as f:
        f.write(story1.BRANCH_AGENT)
    story1.git(repo, "commit", "-q", "-am", "branch drawing")
    story1.git(repo, "checkout", "-q", "main")
    bin_dir = base / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(story1.FAKE_GH)
    (bin_dir / "gh").chmod(0o755)
    (base / "world.json").write_text(json.dumps(story1.world()))
    return {"repo": repo, "bin": bin_dir, "world": base / "world.json", "log": base / "gh.log"}


def diff(place, number, branch):
    """Run `diff` from the throwaway checkout's root; returns the finished process."""
    if not (place["repo"] / "tools" / "visuals.py").exists():
        pytest.fail("626.1: tools/visuals.py does not exist, so there is no command to compare drawings with")
    env = {k: v for k, v in os.environ.items() if k not in ("DOKIMA_BOT", "GITHUB_REPOSITORY", "REPO")}
    env.update(PATH=f"{place['bin']}{os.pathsep}{env.get('PATH', '')}", VISUALS_WORLD=str(place["world"]),
               VISUALS_LOG=str(place["log"]))
    return subprocess.run([sys.executable, "tools/visuals.py", "diff", str(number), "--branch", branch, "--repo", REPO],
                          cwd=place["repo"], env=env, capture_output=True, text=True, timeout=180)


def marked(out):
    """The diff's changed lines as (sign, text), headers left out."""
    return [(line[0], line[1:]) for line in out.splitlines()
            if line[:1] in "-+" and not line.startswith(("---", "+++"))]


def test_diff_shows_changed_lines(place, record_property):
    """Only the lines a branch changes are shown, main's beside the branch's.

    Compares issue 7 drawn by a branch that marks the card and rewords the autopilot lines with main's drawing.
    Checks the branch's new lines show with `+`, main's old lines with `-`, and no line both share is marked. Proves 626.1."""
    record_property("proves", "626.1")
    r = diff(place, ISSUE, "visual-test")
    out = r.stdout
    assert r.returncode == 0, f"626.1: comparing #{ISSUE} from visual-test with main exited {r.returncode}:\n{out}\n{r.stderr}"
    lines = marked(out)
    assert ("+", "BRANCH-CARD") in lines, f"626.1: the branch's new card line is not shown as added:\n{out}"
    assert ("+", "Autopilot: BRANCH work line") in lines, \
        f"626.1: the branch's reworded autopilot line is not shown as added:\n{out}"
    assert ("-", "Autopilot: plan approved, starting work") in lines, \
        f"626.1: main's autopilot line the branch replaced is not shown as removed:\n{out}"
    shared = [t for _, t in lines if PLAN_SUMMARY in t]
    assert not shared, f"626.1: a line both drawings share is shown as changed: {shared}\n{out}"
    assert SAME not in out, f"626.1: the diff says nothing differs while the branch changed lines:\n{out}"


def test_diff_same_as_main_says_so(place, record_property):
    """A branch that draws exactly as main says no line differs.

    Compares issue 7 drawn from main with itself and checks the command says so, marks no line and exits 0. Proves 626.1."""
    record_property("proves", "626.1")
    r = diff(place, ISSUE, "main")
    out = r.stdout
    assert r.returncode == 0, f"626.1: comparing main with itself exited {r.returncode}:\n{out}\n{r.stderr}"
    assert SAME in out, f"626.1: comparing main with itself does not say {SAME!r}:\n{out}"
    assert not marked(out), f"626.1: comparing main with itself marks lines as changed:\n{out}"


def test_diff_unreadable_issue_says_so(place, record_property):
    """An issue GitHub refuses ends the comparison with a plain message naming the issue.

    Asks for issue 8, which the fake GitHub answers with a server error, and checks the command fails naming the
    issue and GitHub's reason, with no traceback. Proves 626.1."""
    record_property("proves", "626.1")
    r = diff(place, 8, "visual-test")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"626.1: comparing an unreadable issue did not fail:\n{said}"
    assert "#8" in said and "HTTP 502" in said, f"626.1: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"626.1: an unreadable issue crashed the command instead of saying why:\n{said}"


def test_diff_unknown_branch_says_so(place, record_property):
    """A missing branch ends the comparison with a plain message naming the branch.

    Asks to compare a misspelled branch with main and checks the command fails naming it, with no traceback.
    Proves 626.1."""
    record_property("proves", "626.1")
    r = diff(place, ISSUE, "no-such-branch")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"626.1: comparing a missing branch with main did not fail:\n{said}"
    assert "no-such-branch" in said, f"626.1: the message does not name the missing branch:\n{said}"
    assert "Traceback" not in said, f"626.1: a missing branch crashed the command instead of saying why:\n{said}"


def nightly_flow(criterion="626.2"):
    """The nightly workflow, read; fails naming the criterion when it is missing."""
    if not os.path.exists(NIGHTLY_FLOW):
        pytest.fail(f"{criterion}: there is no .github/workflows/visuals-nightly.yml to run the real GitHub checks at night")
    return ts.load_yaml(open(NIGHTLY_FLOW).read())


def runs(wf):
    """Every step of every job: (its run text, its env)."""
    out = []
    for job in (wf.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            out.append((step.get("run") or "", step.get("env") or {}))
    return out


def suite_paths():
    """The paths the all tests check hands pytest, read from full-suite.yml."""
    wf = ts.load_yaml(open(os.path.join(WORKFLOWS, "full-suite.yml")).read())
    paths = []
    for text, _ in runs(wf):
        for line in text.splitlines():
            words = line.split()
            if "pytest" in words:
                after = words[words.index("pytest") + 1:]
                skip = False
                for w in after:
                    if skip:
                        skip = False
                    elif w in ("-p", "-n", "-k", "-m"):
                        skip = True
                    elif not w.startswith("-"):
                        paths.append(w.rstrip("/"))
    return paths


def test_nightly_runs_real_checks_on_schedule_only(record_property):
    """Real GitHub checks run at night, and never in each pull request's tests.

    Reads the nightly workflow: it starts on a schedule with a cron time, on no pull request, push or merge queue,
    and one step runs pytest on `nightly/` with a GitHub token. Checks `nightly/` holds checks and lies outside every
    path the all tests check runs. Proves 626.2."""
    record_property("proves", "626.2")
    wf = nightly_flow()
    on = wf.get("on")
    on = {k: v for k, v in on.items()} if isinstance(on, dict) else {e: {} for e in ([on] if isinstance(on, str) else on or [])}
    assert "schedule" in on, f"626.2: the nightly workflow has no schedule: it starts on {sorted(on)}"
    crons = [c.get("cron") for c in on["schedule"] or [] if isinstance(c, dict)]
    assert any(crons), "626.2: the nightly workflow's schedule names no cron time"
    extra = set(on) - {"schedule", "workflow_dispatch"}
    assert not extra, f"626.2: the nightly workflow also starts on {sorted(extra)}, so real checks run outside the night"
    steps = [(t, e) for t, e in runs(wf) if "pytest" in t and "nightly" in t]
    assert steps, "626.2: no step of the nightly workflow runs pytest on nightly/"
    assert any("GH_TOKEN" in e for _, e in steps), "626.2: the step running nightly/ holds no GH_TOKEN to reach GitHub"
    checks = [f for f in (os.listdir(NIGHTLY) if os.path.isdir(NIGHTLY) else []) if f.startswith("test_") and f.endswith(".py")]
    assert checks, "626.2: nightly/ holds no check file"
    for p in suite_paths():
        full = os.path.abspath(os.path.join(ROOT, p))
        assert not (NIGHTLY + os.sep).startswith(full + os.sep), \
            f"626.2: the all tests check runs {p!r}, which holds nightly/, so real checks run on every pull request"


def test_nightly_checks_fail_when_github_refuses(tmp_path, record_property):
    """The nightly checks really call GitHub, and fail saying why when it refuses.

    Runs nightly/ from a throwaway copy of the repo with a fake `gh` that logs and refuses every call. Checks the
    checks ran (none skipped), called `gh` on the card-gallery repo, failed, and their output names GitHub's refusal. Proves 626.2."""
    record_property("proves", "626.2")
    if not os.path.isdir(NIGHTLY):
        pytest.fail("626.2: there is no nightly/ folder holding the real GitHub checks")
    repo = tmp_path / "checkout"
    for d in ("dokima", "tools", "nightly"):
        if os.path.isdir(os.path.join(ROOT, d)):
            shutil.copytree(os.path.join(ROOT, d), repo / d, ignore=shutil.ignore_patterns("__pycache__"))
    story1.git(repo, "init", "-q", "-b", "main")
    story1.git(repo, "config", "user.name", "Test")
    story1.git(repo, "config", "user.email", "test@example.com")
    story1.git(repo, "add", "-A")
    story1.git(repo, "commit", "-q", "-m", "main")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(REFUSING_GH)
    (bin_dir / "gh").chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    env = {k: v for k, v in os.environ.items() if k not in ("DOKIMA_BOT", "GITHUB_REPOSITORY", "REPO")}
    env.update(PATH=f"{bin_dir}{os.pathsep}{env.get('PATH', '')}", VISUALS_LOG=str(log), GH_TOKEN="fake-token",
               PYTHONPATH=str(repo))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", "nightly"], cwd=repo,
                       env=env, capture_output=True, text=True, timeout=300)
    said = r.stdout + r.stderr
    assert r.returncode != 5, f"626.2: pytest found no check in nightly/:\n{said}"
    assert "skipped" not in said.lower(), f"626.2: a nightly check skipped instead of calling GitHub:\n{said}"
    calls = log.read_text().strip()
    assert calls, f"626.2: the nightly checks never called gh, so they do not reach real GitHub:\n{said}"
    assert GALLERY in calls, \
        f"626.2: no nightly check called gh on {GALLERY}, so none reads or posts the gallery previews:\n{calls}"
    assert r.returncode == 1, f"626.2: the nightly checks did not fail when GitHub refused every call (exit {r.returncode}):\n{said}"
    assert "HTTP 401" in said, f"626.2: the failing nightly checks do not say GitHub's reason:\n{said}"


def test_tool_is_never_part_of_dokima(record_property):
    """The tool is ours alone: Dokima's code never names it; only the nightly workflow does.

    Reads every file of the dokima package, prompts and settings included, and checks none names the tool or its
    nightly checks. Reads every workflow and checks only the nightly one names them, and that one does. Proves 626.3."""
    record_property("proves", "626.3")
    named = []
    for folder, dirs, files in os.walk(os.path.join(ROOT, "dokima")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            path = os.path.join(folder, f)
            try:
                text = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            if "visuals" in text or "tools/" in text or "nightly/" in text:
                named.append(os.path.relpath(path, ROOT))
    assert not named, f"626.3: Dokima's own code names our tool, so it ships with the product: {named}"
    nightly_flow("626.3")
    naming = sorted(f for f in os.listdir(WORKFLOWS) if f.endswith((".yml", ".yaml"))
                    and any(w in open(os.path.join(WORKFLOWS, f)).read() for w in ("visuals", "nightly/", "tools/")))
    assert naming == ["visuals-nightly.yml"], \
        f"626.3: the workflows naming our tool are {naming}, not only visuals-nightly.yml"

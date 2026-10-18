"""Tests for #858: the audit spares the repo's own checks and runs with no board.

An adopter's own CI checks on the branch rule are not drift, and boards are optional (they only exist for
organizations). Each test runs `python3 -m dokima.audit OWNER/REPO` from outside, the way the audit workflow does, with
the fake `gh` of tests/fake_gh.py first on PATH (wired by tests/test_audit_cli.py's Audit). With no board, DOKIMA_BOARD
is empty, as the workflow passes an unset repo variable, or not set at all, as on a person's machine.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from dokima import manifest  # noqa: E402
from test_audit_cli import REPO, Audit, clean  # noqa: E402

NEEDED = list(manifest.BRANCH_RULES["main"]["required_checks"])


def run(a, criterion, board):
    """Run the audit command with the given board setting; None leaves it unset."""
    env = dict(os.environ, PATH=f"{a.bin}{os.pathsep}{os.environ.get('PATH', '')}", PYTHONPATH=ROOT,
               FAKE_GH_STATE=str(a.file), GH_TOKEN="fake", GITHUB_TOKEN="fake", GITHUB_REPOSITORY=REPO)
    env.pop("DOKIMA_BOARD", None)
    if board is not None:
        env["DOKIMA_BOARD"] = board
    p = subprocess.run([sys.executable, "-m", "dokima.audit", REPO], cwd=a.root, env=env, capture_output=True,
                       text=True, timeout=60)
    assert "Traceback" not in p.stderr, f"{criterion}: the audit command crashed:\n{p.stderr}"
    return p


def setup_issue(a, criterion, p):
    """The one Setup issue the command opened, or a failure saying what the command said."""
    s = a.state()
    made = [w["number"] for w in s["writes"] if w["kind"] == "create"]
    assert len(made) == 1, (f"{criterion}: the audit should open exactly one Setup issue, it opened {made}\n"
                            f"exit {p.returncode}\nstdout: {p.stdout}\nstderr: {p.stderr}\n{a.why()}")
    return s["issues"][str(made[0])]


def bullets(issue):
    """The listed lines of a Setup issue's body."""
    return [l[2:].strip() for l in issue["body"].splitlines() if l.startswith("- ")]


def no_board_drift():
    """A fake repo with board fields, views and one label off."""
    s = clean()
    del s["labels"]["filed-by-dokima"]
    del s["fields"]["Action"]
    s["views"]["Autopilot"]["filter"] = "label:autopilot"
    return s


# 858.1: a required check the repo added is not drift

def test_a_check_the_repo_added_gets_no_line(record_property, tmp_path):
    """A required check the repo added gets no line on the Setup issue.

    Proves 858.1. The board is set and main's rule requires the repo's own lint check besides Dokima's checks, but
    lacks Acceptance criteria. The audit opens a Setup issue that names the missing Acceptance criteria check, so the
    rule was read, and no line names lint."""
    record_property("proves", "858.1")
    s = clean()
    s["protection"]["main"] = [c for c in NEEDED if c != "Acceptance criteria"] + ["lint"]
    a = Audit(tmp_path, s)
    p = run(a, "858.1", "acme/1")
    lines = bullets(setup_issue(a, "858.1", p))
    assert any("Acceptance criteria" in l for l in lines), \
        f"858.1: the missing Acceptance criteria check is not listed, so the rule was not read: {lines}"
    flagged = [l for l in lines if "lint" in l]
    assert not flagged, f"858.1: the repo's own lint check is still listed as drift: {flagged}"


# 858.2: with no board, the audit finishes with exit code 0

def test_the_audit_with_no_board_exits_0(record_property, tmp_path):
    """With no board set, the audit finishes with exit code 0 and still reports drift.

    Proves 858.2. The repo is missing the filed-by-dokima label. The command runs once with DOKIMA_BOARD empty, as the
    workflow passes an unset variable, and once with it not set at all. Each run exits 0 and the Setup issue lists the
    missing label, so the audit really ran."""
    record_property("proves", "858.2")
    for board, how in (("", "empty"), (None, "not set")):
        s = clean()
        del s["labels"]["filed-by-dokima"]
        a = Audit(tmp_path / how.replace(" ", "-"), s)
        p = run(a, "858.2", board)
        assert p.returncode == 0, (f"858.2: with DOKIMA_BOARD {how}, the audit exited {p.returncode}, not 0\n"
                                   f"stdout: {p.stdout}\nstderr: {p.stderr}")
        lines = bullets(setup_issue(a, "858.2", p))
        assert any("filed-by-dokima" in l for l in lines), \
            f"858.2: with DOKIMA_BOARD {how}, the missing label is not listed: {lines}"


# 858.3: with no board, no line about board fields or views

def test_the_audit_with_no_board_lists_no_board_lines(record_property, tmp_path):
    """With no board set, the Setup issue lists no line about board fields or views.

    Proves 858.3. DOKIMA_BOARD is empty. The fake GitHub would answer a board read with a board lacking the Action field
    and with a wrong Autopilot view filter; the repo is also missing the filed-by-dokima label. The Setup issue lists
    the missing label, and no line names a board, a board field or a view."""
    record_property("proves", "858.3")
    a = Audit(tmp_path, no_board_drift())
    p = run(a, "858.3", "")
    lines = bullets(setup_issue(a, "858.3", p))
    assert any("filed-by-dokima" in l for l in lines), f"858.3: the missing label is not listed: {lines}"
    about = [l for l in lines if "board" in l.lower() or "view" in l.lower() or "Action" in l]
    assert not about, f"858.3: with no board set, the Setup issue still lists board lines: {about}"


# 858.4: with no board, a check Dokima needs that the rule lacks is still listed

def test_the_audit_with_no_board_lists_a_missing_needed_check(record_property, tmp_path):
    """With no board set, a needed check the rule lacks is still listed.

    Proves 858.4. DOKIMA_BOARD is empty and main's rule requires all of Dokima's checks but Acceptance criteria.
    The audit opens a Setup issue with one line naming main and Acceptance criteria."""
    record_property("proves", "858.4")
    s = clean()
    s["protection"]["main"] = [c for c in NEEDED if c != "Acceptance criteria"]
    a = Audit(tmp_path, s)
    p = run(a, "858.4", "")
    lines = bullets(setup_issue(a, "858.4", p))
    hits = [l for l in lines if "Acceptance criteria" in l and "main" in l]
    assert len(hits) == 1, f"858.4: the missing Acceptance criteria check should be on one line naming main: {lines}"

"""Tests for #820: an adopter's audit wants Dokima's checks as GitHub names them.

An adopter's repo runs Dokima through the one thin workflow the install ships (`dokima/install/dokima.yml`): its job
`dokima` calls `entry.yml`, whose jobs `full-suite` and `acceptance-criteria` call the workflows holding the checks.
GitHub names a called job's check after every caller above it, so there the checks show as
`dokima / full-suite / all tests` and `dokima / acceptance-criteria / Acceptance criteria`, never as plain `all tests`
and `Acceptance criteria`. A branch rule requiring the plain names waits forever for checks that never come.

Each test copies the settings file the install ships (`dokima/install/settings.yaml`) into a temp repo as
`.dokima/settings.yaml`, the way an adopter installs it, and runs the real audit command
(`python3 -m dokima.audit OWNER/REPO`) from outside against the fake `gh` of tests/fake_gh.py, through
tests/test_audit_cli.py's Audit helper. One label's color always drifts, so every run opens a Setup issue whose lines can
be read. Dokima's own repo, with no settings file, keeps the plain names; older tests already prove that.
"""
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from test_audit_cli import Audit, body_lines, clean  # noqa: E402

INSTALL_SETTINGS = os.path.join(ROOT, "dokima", "install", "settings.yaml")
ALL_TESTS = "dokima / full-suite / all tests"
ACCEPTANCE = "dokima / acceptance-criteria / Acceptance criteria"


def setup_lines(tmp_path, name, required, criterion):
    """Runs the audit in an adopter's repo whose main requires REQUIRED; returns Setup issue lines.

    The repo holds the settings file the install ships, and one label's color drifted, so a Setup issue always opens."""
    s = clean()
    s["protection"]["main"] = list(required)
    s["labels"]["filed-by-dokima"]["color"] = "000000"
    a = Audit(tmp_path / name, s)
    (a.root / ".dokima").mkdir()
    shutil.copy(INSTALL_SETTINGS, a.root / ".dokima" / "settings.yaml")
    a.run(criterion)
    st = a.state()
    made = [w["number"] for w in st["writes"] if w["kind"] == "create"]
    assert len(made) == 1, f"{criterion}: a drifted label should open one Setup issue, it opened {made}\n{a.why()}"
    return [l for l in body_lines(st["issues"][str(made[0])]["body"]) if l], a


def mentioning(lines, check):
    """The lines naming CHECK, as a whole name."""
    return [l for l in lines if re.search(rf"(?<![\w-]){re.escape(check)}(?![\w-])", l)]


# 820.1: in an adopter's repo the audit wants all tests under the name GitHub shows there

def test_adopter_audit_wants_all_tests_as_github_shows_it(record_property, tmp_path):
    """An adopter's audit wants main to require all tests as GitHub names it there.

    With the install's settings file, main requiring `dokima / full-suite / all tests` (and the acceptance check as
    GitHub shows it) gets no line about all tests on the Setup issue. Main requiring the plain `all tests`, which never
    shows in that repo, gets a line saying main does not require `dokima / full-suite / all tests`. Proves 820.1."""
    record_property("proves", "820.1")
    lines, a = setup_lines(tmp_path, "shown", [ALL_TESTS, ACCEPTANCE], "820.1")
    flagged = mentioning(lines, "all tests")
    assert not flagged, (f"820.1: main requires all tests as GitHub shows it in an adopter's repo ({ALL_TESTS!r}), "
                         f"yet the audit flagged it: {flagged}\n{a.why()}")

    lines, a = setup_lines(tmp_path, "plain", ["all tests", ACCEPTANCE], "820.1")
    asked = [l for l in mentioning(lines, ALL_TESTS) if "does not require" in l]
    assert len(asked) == 1, (f"820.1: main requires the plain 'all tests', a name GitHub never shows in an adopter's "
                             f"repo, but the audit did not say, on one line, that main does not require {ALL_TESTS!r}: "
                             f"{lines}\n{a.why()}")


# 820.2: in an adopter's repo the audit wants Acceptance criteria under the name GitHub shows there

def test_adopter_audit_wants_acceptance_criteria_as_github_shows_it(record_property, tmp_path):
    """An adopter's audit wants main to require Acceptance criteria as GitHub names it.

    With the install's settings file, main requiring `dokima / acceptance-criteria / Acceptance criteria` (and all
    tests as GitHub shows it) gets no line about Acceptance criteria on the Setup issue. Main requiring the plain
    `Acceptance criteria`, which never shows in that repo, gets a line saying main does not require
    `dokima / acceptance-criteria / Acceptance criteria`. Proves 820.2."""
    record_property("proves", "820.2")
    lines, a = setup_lines(tmp_path, "shown", [ALL_TESTS, ACCEPTANCE], "820.2")
    flagged = mentioning(lines, "Acceptance criteria")
    assert not flagged, (f"820.2: main requires Acceptance criteria as GitHub shows it in an adopter's repo "
                         f"({ACCEPTANCE!r}), yet the audit flagged it: {flagged}\n{a.why()}")

    lines, a = setup_lines(tmp_path, "plain", [ALL_TESTS, "Acceptance criteria"], "820.2")
    asked = [l for l in mentioning(lines, ACCEPTANCE) if "does not require" in l]
    assert len(asked) == 1, (f"820.2: main requires the plain 'Acceptance criteria', a name GitHub never shows in an "
                             f"adopter's repo, but the audit did not say, on one line, that main does not require "
                             f"{ACCEPTANCE!r}: {lines}\n{a.why()}")

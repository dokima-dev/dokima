"""Tests for #283: `python3 -m dokima.audit OWNER/REPO` audits the live repo through `gh`.

The in-memory tests in tests/test_audit.py prove what the audit decides. These prove it really reads and writes GitHub:
each runs the command from outside, the way a workflow does, with a fake `gh` (tests/fake_gh.py) first on PATH that
keeps GitHub in a JSON file and logs every call. The command is run from a folder holding .github/CODEOWNERS, with
DOKIMA_BOARD naming the org's board ("acme/1") and the dokima package on PYTHONPATH. The fake's docstring lists every
call it answers; any other call is logged as unsupported and refused, and the failure message shows it.

How the command is expected to read GitHub:
    labels              gh api repos/OWNER/REPO/labels
    board fields, views gh api graphql, organization(login:){projectV2(number:){fields views}}
    main's rule         gh api repos/OWNER/REPO/branches/main/protection (404 "Branch not protected": no rule)
    the app's permissions  gh api repos/OWNER/REPO/installation, its "permissions"
and to write only the Setup issue: open, edit, comment, close and pin it (gh api or gh issue), and mark its card Needs
you through GraphQL (addProjectV2ItemById, then updateProjectV2ItemFieldValue on the Action field).
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import manifest  # noqa: E402

REPO = "acme/widgets"
FORBIDDEN = "Resource not accessible by integration (HTTP 403)"
BROKEN = "Server Error (HTTP 502)"


def clean():
    """A fake GitHub whose settings match the manifest, with no issues."""
    return {"repo": REPO, "labels": copy.deepcopy(manifest.LABELS), "fields": copy.deepcopy(manifest.FIELDS),
            "views": copy.deepcopy(manifest.VIEWS),
            "protection": {b: list(r["required_checks"]) for b, r in manifest.BRANCH_RULES.items()},
            "permissions": copy.deepcopy(manifest.PERMISSIONS), "fail": {}, "issues": {}, "next": 100,
            "items": {}, "calls": [], "writes": []}


def drifted():
    """A fake GitHub off in one setting of each kind the audit reads."""
    s = clean()
    del s["labels"]["plan"]
    s["labels"]["work"]["description"] = "Old words"
    del s["fields"]["Action"]["Autopilot"]
    s["fields"]["Priority"]["High"]["color"] = "RED"
    s["views"]["Autopilot"]["filter"] = "label:autopilot"
    s["protection"]["main"] = ["all tests"]
    s["permissions"]["issues"] = "read"
    return s


class Audit:
    """One repo root with CODEOWNERS and a fake gh, where the audit command runs."""

    def __init__(self, tmp_path, state, owners="* @alice\n"):
        self.root = tmp_path / "repo"
        (self.root / ".github").mkdir(parents=True)
        (self.root / ".github" / "CODEOWNERS").write_text(owners)
        self.bin = tmp_path / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(f"#!{sys.executable}\n" + open(os.path.join(ROOT, "tests", "fake_gh.py")).read())
        gh.chmod(0o755)
        self.file = tmp_path / "github.json"
        self.save(state)

    def save(self, state):
        """Replace the fake GitHub's state."""
        self.file.write_text(json.dumps(state))

    def state(self):
        """The fake GitHub's state now."""
        return json.loads(self.file.read_text())

    def run(self, criterion):
        """Run the audit command once; fail naming the criterion if it is missing or crashed."""
        env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}", PYTHONPATH=ROOT,
                   DOKIMA_BOARD="acme/1", FAKE_GH_STATE=str(self.file), GH_TOKEN="fake", GITHUB_TOKEN="fake",
                   GITHUB_REPOSITORY=REPO)
        p = subprocess.run([sys.executable, "-m", "dokima.audit", REPO], cwd=self.root, env=env, capture_output=True,
                           text=True, timeout=60)
        if "No module named dokima.audit" in p.stderr:
            pytest.fail(f"{criterion}: there is no audit command, python3 -m dokima.audit")
        assert "Traceback" not in p.stderr, f"{criterion}: the audit command crashed:\n{p.stderr}"
        return p

    def why(self):
        """What the command said and every call the fake could not answer, for failure messages."""
        s = self.state()
        return f"unsupported calls: {s.get('unsupported', [])}\nwrites: {s['writes']}"


def created(a, criterion):
    """The one issue the command opened, or a failure."""
    s = a.state()
    made = [w["number"] for w in s["writes"] if w["kind"] == "create"]
    assert len(made) == 1, f"{criterion}: the command should open exactly one Setup issue, it opened {made}\n{a.why()}"
    return made[0], s["issues"][str(made[0])]


def body_lines(text):
    """The lines of an issue body, without list bullets."""
    return [l.strip().lstrip("-*").strip() for l in text.splitlines()]


def one_line(lines, criterion, what, *words):
    """The one line holding every word, or a failure saying what was not reported once."""
    hits = [l for l in lines if all(re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", l) for w in words)]
    assert len(hits) == 1, f"{criterion}: {what} should be on exactly one line naming {words}, found {hits} in {lines}"
    return hits[0]


# 283.1: the audit compares the manifest with the repo's live settings

def test_the_audit_command_reads_every_live_setting_through_gh(record_property, tmp_path):
    """The audit command reads labels, board, main's rule and app permissions from GitHub.

    Proves 283.1. Runs `python3 -m dokima.audit acme/widgets` against a fake gh whose repo is off in one setting of each kind: a
    missing plan label, the work label's description, the Action field's missing Autopilot option, the High option's
    color, the Autopilot view's filter, main's missing required check and the app's issues permission. Each can only
    be found by reading it through gh, and each must be its own line on the Setup issue the command opens."""
    record_property("proves", "283.1")
    a = Audit(tmp_path, drifted())
    a.run("283.1")
    n, issue = created(a, "283.1")
    lines = body_lines(issue["body"])
    one_line(lines, "283.1", "the missing plan label", "plan", "1d76db")
    one_line(lines, "283.1", "the work label's description", "work", "Old words", "Starts the worker on the approved plan")
    one_line(lines, "283.1", "the missing Autopilot option of the Action field", "Action", "Autopilot", "PURPLE")
    one_line(lines, "283.1", "the High option's color", "High", "RED", "ORANGE")
    one_line(lines, "283.1", "the Autopilot view's filter", "label:autopilot is:open")
    one_line(lines, "283.1", "main's missing required check", "main", "Acceptance criteria")
    one_line(lines, "283.1", "the app's issues permission", "issues", "read", "write")


# 283.2: drift goes on one pinned Setup issue marked Needs you, and later runs update it

def test_the_audit_command_pins_the_setup_issue_and_marks_it_needs_you(record_property, tmp_path):
    """On drift, the command opens one pinned Setup issue marked Needs you on the board.

    Proves 283.2. Runs the command against the drifted fake repo with no Setup issue. Exactly one issue opens, titled Setup; it is
    pinned; its card is added to the board and its Action field set to the Needs you option."""
    record_property("proves", "283.2")
    a = Audit(tmp_path, drifted())
    a.run("283.2")
    n, issue = created(a, "283.2")
    assert "Setup" in issue["title"], f"283.2: the issue opened is titled {issue['title']!r}, not Setup"
    assert issue["pinned"], f"283.2: the Setup issue was not pinned on GitHub\n{a.why()}"
    card = a.state()["items"].get(f"PVTI_I_{n}", {})
    assert card.get("Action") == manifest_option("Action", "Needs you"), \
        f"283.2: the Setup issue's card is not marked Needs you on the board: {card}\n{a.why()}"


def manifest_option(field, option):
    """The fake board's id of an option."""
    return f"O_{field}_{option.replace(' ', '_')}"


def test_a_second_audit_command_updates_the_same_setup_issue(record_property, tmp_path):
    """A second run updates the Setup issue it opened instead of opening another.

    Proves 283.2. Runs the command on the drifted repo, then puts the plan label back, changes the high label's color and runs it
    again. Still only one issue was ever opened; it lists the high label and no longer the plan label, and its card is
    still Needs you."""
    record_property("proves", "283.2")
    a = Audit(tmp_path, drifted())
    a.run("283.2")
    n, _ = created(a, "283.2")
    s = a.state()
    s["labels"]["plan"] = copy.deepcopy(manifest.LABELS["plan"])
    s["labels"]["high"]["color"] = "000000"
    s["items"].get(f"PVTI_I_{n}", {}).pop("Action", None)
    a.save(s)
    a.run("283.2")
    n2, issue = created(a, "283.2")
    assert n2 == n and issue["state"] == "open", f"283.2: the Setup issue #{n} was not kept open\n{a.why()}"
    one_line(body_lines(issue["body"]), "283.2", "the high label's new color", "high", "000000")
    assert "1d76db" not in issue["body"], f"283.2: the fixed plan label is still listed:\n{issue['body']}"
    card = a.state()["items"].get(f"PVTI_I_{n}", {})
    assert card.get("Action") == manifest_option("Action", "Needs you"), \
        f"283.2: the updated Setup issue's card is not marked Needs you: {card}\n{a.why()}"


# 283.3: a clean run writes nothing; a Setup issue left open is closed with one line

def test_the_audit_command_writes_nothing_on_a_clean_repo(record_property, tmp_path):
    """On a repo matching the manifest, the command writes nothing to GitHub.

    Proves 283.3. Runs the command against a clean fake repo with no Setup issue: no issue, comment, pin or board write is made,
    and every call it made was one the fake answers (so it did read the repo)."""
    record_property("proves", "283.3")
    a = Audit(tmp_path, clean())
    a.run("283.3")
    s = a.state()
    assert s["calls"], "283.3: the command made no call to GitHub at all"
    assert not s.get("unsupported"), f"283.3: the command made calls the fake gh does not answer\n{a.why()}"
    assert s["writes"] == [], f"283.3: a clean run wrote to GitHub: {s['writes']}"


def test_the_audit_command_closes_its_setup_issue_once_clean(record_property, tmp_path):
    """Once clean, the command closes its Setup issue with one line saying nothing is off.

    Proves 283.3. Runs the command on the drifted repo, then makes the repo match the manifest and runs it again: the Setup issue
    gets exactly one comment, a single line saying nothing is off, and is closed; no other issue opens."""
    record_property("proves", "283.3")
    a = Audit(tmp_path, drifted())
    a.run("283.3")
    n, _ = created(a, "283.3")
    s = a.state()
    fixed = clean()
    for k in ("issues", "next", "items", "calls", "writes"):
        fixed[k] = s[k]
    a.save(fixed)
    a.run("283.3")
    n2, issue = created(a, "283.3")
    comments = issue["comments"]
    assert len(comments) == 1, f"283.3: closing the Setup issue should leave one comment, it left {comments}"
    assert "\n" not in comments[0].strip() and "nothing is off" in comments[0].lower(), \
        f"283.3: the closing comment should be one line saying nothing is off: {comments[0]!r}"
    assert issue["state"] == "closed", f"283.3: the Setup issue was left open on a clean repo\n{a.why()}"


# 283.4: only the code owners are mentioned, and nothing is written outside the repo

def test_the_audit_command_mentions_the_code_owners_and_writes_only_to_its_repo(record_property, tmp_path):
    """The Setup issue mentions exactly the code owners, and every call stays on its repo.

    Proves 283.4. CODEOWNERS in the folder it runs from names alice and bob for `*` and carol for docs/. The Setup issue mentions
    alice and bob and no one else, every write is on acme/widgets, and no call named another repo."""
    record_property("proves", "283.4")
    a = Audit(tmp_path, drifted(), "* @alice @bob\ndocs/ @carol\n")
    a.run("283.4")
    n, issue = created(a, "283.4")
    said = set(re.findall(r"(?<![\w.])@([A-Za-z0-9][A-Za-z0-9-]*)", issue["body"]))
    assert said == {"alice", "bob"}, f"283.4: the Setup issue mentions {said}, not exactly alice and bob"
    s = a.state()
    assert all(w["repo"] == REPO for w in s["writes"]), f"283.4: a write left the repo: {s['writes']}"
    away = [c for c in s["calls"] for arg in c if re.search(r"repos/(?!acme/widgets/)[^/\s]+/[^/\s]+", arg)]
    assert not away, f"283.4: the command called GitHub about another repo: {away}"


# 283.5: each setting the app cannot read gets its own line

def test_the_audit_command_reports_unreadable_rule_and_permissions(record_property, tmp_path):
    """Refused reads of main's rule and the app's permissions each say could not be verified.

    Proves 283.5. The fake repo is clean except that GitHub answers 403 to main's protection and to the app's installation. The
    command opens a Setup issue with one line naming main and one naming the permissions, each saying it could not
    be verified with GitHub's reason."""
    record_property("proves", "283.5")
    s = clean()
    s["fail"] = {"protection": FORBIDDEN, "permissions": FORBIDDEN}
    a = Audit(tmp_path, s)
    a.run("283.5")
    n, issue = created(a, "283.5")
    lines = [l for l in body_lines(issue["body"]) if "could not be verified" in l.lower()]
    assert len(lines) == 2, f"283.5: two unreadable settings should give two lines, got {lines}\n{a.why()}"
    rule = [l for l in lines if re.search(r"(?<![\w-])main(?![\w-])", l)]
    assert len(rule) == 1, f"283.5: main's rule should be on exactly one line: {lines}"
    perms = [l for l in lines if l not in rule]
    assert "permission" in perms[0].lower(), f"283.5: the other line should name the app's permissions: {perms[0]!r}"
    for line in lines:
        assert "Resource not accessible by integration" in line, f"283.5: the line does not give GitHub's reason: {line!r}"


# 283.6: a failed GitHub call is reported as not verified, never skipped

def test_the_audit_command_reports_failed_calls_as_not_verified(record_property, tmp_path):
    """Failed reads of the labels and main's rule each say could not be verified.

    Proves 283.6. The fake repo is clean except that reading the labels and main's protection answers 502. The command opens a
    Setup issue instead of posting nothing, with one line naming the labels and one naming main, each saying it could
    not be verified with GitHub's reason."""
    record_property("proves", "283.6")
    s = clean()
    s["fail"] = {"labels": BROKEN, "protection": BROKEN}
    a = Audit(tmp_path, s)
    a.run("283.6")
    n, issue = created(a, "283.6")
    lines = [l for l in body_lines(issue["body"]) if "could not be verified" in l.lower()]
    assert len(lines) == 2, f"283.6: two failed calls should give two lines, got {lines}\n{a.why()}"
    rule = [l for l in lines if re.search(r"(?<![\w-])main(?![\w-])", l)]
    labels = [l for l in lines if l not in rule]
    assert len(rule) == 1 and "label" in labels[0].lower(), \
        f"283.6: one line should name main's rule and the other the labels: {lines}"
    for line in lines:
        assert BROKEN in line, f"283.6: the line does not give GitHub's reason: {line!r}"

"""Tests for #283: the drift audit reports on one pinned Setup issue, else stays silent.

The audit is `dokima/audit.py`. It compares the manifest (`dokima/manifest.py`) with the repo's live settings and
reports the difference on one Setup issue. Everything it reads from or writes to GitHub goes through one object it is
given, so these tests hand it a faked GitHub kept in memory. What the audit is expected to offer:

    audit.compare(github, repo) -> [str, ...]
        one plain line per setting that differs from the manifest or could not be read; empty when all match
    audit.run(github, repo, root=".") -> issue number or None
        compares, then reports on the Setup issue: opens it (pinned, Needs you) or updates the open one when something
        is off; closes an open one with one line when nothing is; does nothing at all when nothing is off and none is
        open. Code owners are read from root/.github/CODEOWNERS. Returns the Setup issue it touched, or None.

What the faked GitHub offers, and the audit is expected to use (a read may raise subprocess.CalledProcessError, as
`gh` does, carrying GitHub's reason in stderr):
    labels(repo)              {name: {"color": "rrggbb", "description": str}}
    fields()                  the board's {field: {option: {"color": COLOR, "description": str}}}
    views()                   the board's {view: {"layout": str, "filter": str}}
    branch_rule(repo, branch) {"required_checks": [name, ...]}, or None when the branch has no rule
    permissions(repo)         the app's {permission: "read" | "write"}
    setup_issue(repo)         the open Setup issue as {"number": n, "body": str}, or None
    create_issue(repo, title, body) -> n
    edit_issue(repo, n, body)
    comment(repo, n, text)
    close_issue(repo, n)
    pin_issue(repo, n)
    needs_you(repo, n)        marks the issue's card Needs you on the board
"""
import copy
import importlib
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import manifest  # noqa: E402

REPO = "acme/widgets"
FORBIDDEN = "gh: Resource not accessible by integration (HTTP 403)"
BROKEN = "gh: Server Error (HTTP 502)"


def audit(criterion):
    """The audit module, or a failure naming the criterion when it is missing."""
    try:
        return importlib.import_module("dokima.audit")
    except ModuleNotFoundError as e:
        if e.name != "dokima.audit":
            raise
        pytest.fail(f"{criterion}: there is no audit module, dokima/audit.py")


def refused(reason):
    """The error `gh` raises when GitHub refuses a call, with GitHub's reason."""
    return subprocess.CalledProcessError(1, ["gh", "api"], output="", stderr=reason)


class GitHub:
    """A faked GitHub whose settings match the manifest until a test changes them.

    Every write the audit makes is kept, with the repo it named."""

    def __init__(self, fail=None, issues=None):
        self.label_list = copy.deepcopy(manifest.LABELS)
        self.field_map = copy.deepcopy(manifest.FIELDS)
        self.view_map = copy.deepcopy(manifest.VIEWS)
        self.rules = copy.deepcopy(manifest.BRANCH_RULES)
        self.perms = copy.deepcopy(manifest.PERMISSIONS)
        self.fail = dict(fail or {})
        self.issues = {n: dict(i) for n, i in (issues or {}).items()}
        self.writes = []
        self.next = 100

    def _read(self, what, value):
        if what in self.fail:
            raise refused(self.fail[what])
        return copy.deepcopy(value)

    def labels(self, repo):
        return self._read("labels", self.label_list)

    def fields(self):
        return self._read("fields", self.field_map)

    def views(self):
        return self._read("views", self.view_map)

    def branch_rule(self, repo, branch):
        return self._read("branch_rule", self.rules.get(branch))

    def permissions(self, repo):
        return self._read("permissions", self.perms)

    def setup_issue(self, repo):
        for n, i in sorted(self.issues.items()):
            if i["state"] == "open":
                return {"number": n, "body": i["body"]}
        return None

    def create_issue(self, repo, title, body):
        self.next += 1
        self.issues[self.next] = {"title": title, "body": body, "state": "open", "pinned": False, "needs_you": False,
                                  "comments": []}
        self.writes.append(("create_issue", repo, self.next))
        return self.next

    def edit_issue(self, repo, n, body):
        self.issues[n]["body"] = body
        self.writes.append(("edit_issue", repo, n))

    def comment(self, repo, n, text):
        self.issues[n]["comments"].append(text)
        self.writes.append(("comment", repo, n))

    def close_issue(self, repo, n):
        self.issues[n]["state"] = "closed"
        self.writes.append(("close_issue", repo, n))

    def pin_issue(self, repo, n):
        self.issues[n]["pinned"] = True
        self.writes.append(("pin_issue", repo, n))

    def needs_you(self, repo, n):
        self.issues[n]["needs_you"] = True
        self.writes.append(("needs_you", repo, n))

    def kinds(self):
        return [w[0] for w in self.writes]


def open_setup(body="Old drift\n"):
    """One Setup issue left open by an earlier run, as #7."""
    return {7: {"title": "Setup", "body": body, "state": "open", "pinned": True, "needs_you": True, "comments": []}}


def drifted():
    """A repo with seven differences from the manifest, one of each kind."""
    g = GitHub()
    del g.label_list["plan"]
    g.label_list["work"]["color"] = "000000"
    del g.field_map["Action"]["Autopilot"]
    g.field_map["Priority"]["High"]["color"] = "RED"
    g.view_map["Autopilot"]["filter"] = "label:autopilot"
    g.rules["main"]["required_checks"] = ["all tests"]
    g.perms["issues"] = "read"
    return g


def one_line(lines, criterion, what, *words):
    """The one line holding every word, or a failure saying what was not reported once."""
    hits = [l for l in lines if all(re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", l) for w in words)]
    assert len(hits) == 1, f"{criterion}: {what} should be on exactly one line naming {words}, found {hits} in {lines}"
    return hits[0]


def body_lines(text):
    """The lines of an issue body, without list bullets."""
    return [l.strip().lstrip("-*").strip() for l in text.splitlines()]


def codeowners(tmp_path, text):
    """A repo root whose CODEOWNERS holds the text."""
    os.makedirs(tmp_path / ".github", exist_ok=True)
    (tmp_path / ".github" / "CODEOWNERS").write_text(text)
    return str(tmp_path)


# 283.1: each difference gets one plain line saying what is off and what Dokima needs

def test_each_difference_gets_one_line_saying_what_is_off_and_what_dokima_needs(record_property):
    """Each setting that differs gets one line saying what is off and what Dokima needs.

    Proves 283.1. The faked repo differs in seven ways: the plan label is missing, the work label's color is 000000, the Action field
    has no Autopilot option, the High priority option is RED, the Autopilot view filters on label:autopilot, main's
    rule lacks the Acceptance criteria check, and the app has issues: read. The audit returns seven single lines, one
    per difference, each naming the setting and the value Dokima needs (with the live value where there is one; a
    missing option's line gives the color Dokima needs)."""
    record_property("proves", "283.1")
    a = audit("283.1")
    lines = a.compare(drifted(), REPO)
    assert all("\n" not in l and l.strip() for l in lines), f"283.1: every difference must be one plain line: {lines}"
    one_line(lines, "283.1", "the missing plan label", "plan", "1d76db")
    one_line(lines, "283.1", "the work label's color", "work", "000000", "0e8a16")
    one_line(lines, "283.1", "the missing Autopilot option of the Action field", "Action", "Autopilot", "PURPLE")
    one_line(lines, "283.1", "the High option's color", "High", "RED", "ORANGE")
    one_line(lines, "283.1", "the Autopilot view's filter", "label:autopilot is:open")
    one_line(lines, "283.1", "main's missing required check", "main", "Acceptance criteria")
    one_line(lines, "283.1", "the app's issues permission", "issues", "read", "write")
    assert len(lines) == 7, f"283.1: seven differences gave {len(lines)} lines: {lines}"


def test_too_much_is_a_difference_too(record_property):
    """A broader permission, a missing one and an extra required check each get a line.

    Proves 283.1. The faked app has administration: write where Dokima needs read, and no workflows permission; main's rule also
    requires a lint check Dokima does not declare. The audit returns three lines, one for each."""
    record_property("proves", "283.1")
    a = audit("283.1")
    g = GitHub()
    g.perms["administration"] = "write"
    del g.perms["workflows"]
    g.rules["main"]["required_checks"] = ["all tests", "Acceptance criteria", "lint"]
    lines = a.compare(g, REPO)
    one_line(lines, "283.1", "the broader administration permission", "administration", "write", "read")
    one_line(lines, "283.1", "the missing workflows permission", "workflows", "write")
    one_line(lines, "283.1", "the extra required check", "main", "lint")
    assert len(lines) == 3, f"283.1: three differences gave {len(lines)} lines: {lines}"


def test_a_missing_branch_rule_and_a_missing_view_are_reported(record_property):
    """A branch with no rule and a missing Autopilot view each get one line.

    Proves 283.1. The faked repo has no rule on main and no Autopilot view. The audit returns two lines: one naming main and its
    required checks, one naming the Autopilot view with the layout and filter Dokima needs."""
    record_property("proves", "283.1")
    a = audit("283.1")
    g = GitHub()
    del g.rules["main"]
    del g.view_map["Autopilot"]
    lines = a.compare(g, REPO)
    one_line(lines, "283.1", "main's missing rule", "main", "all tests", "Acceptance criteria")
    one_line(lines, "283.1", "the missing Autopilot view", "Autopilot", "table", "label:autopilot is:open")
    assert len(lines) == 2, f"283.1: two differences gave {len(lines)} lines: {lines}"


def test_descriptions_and_layouts_are_compared_too(record_property):
    """A changed label description, option description and view layout each get one line.

    Proves 283.1. The faked repo matches the manifest except that the work label's description reads "Old words", the Status field's
    Plan option's description reads "Old words", and the Autopilot view is a board. The audit returns three lines,
    each naming the setting, what it is now and what Dokima needs."""
    record_property("proves", "283.1")
    a = audit("283.1")
    g = GitHub()
    g.label_list["work"]["description"] = "Old words"
    g.field_map["Status"]["Plan"]["description"] = "Old words"
    g.view_map["Autopilot"]["layout"] = "board"
    lines = a.compare(g, REPO)
    one_line(lines, "283.1", "the work label's description", "work", "Old words",
             manifest.LABELS["work"]["description"])
    one_line(lines, "283.1", "the Plan option's description", "Plan", "Old words",
             manifest.FIELDS["Status"]["Plan"]["description"])
    one_line(lines, "283.1", "the Autopilot view's layout", "Autopilot", "board", "table")
    assert len(lines) == 3, f"283.1: three differences gave {len(lines)} lines: {lines}"


def test_matching_and_undeclared_settings_get_no_line(record_property):
    """A matching repo gives no lines, even with labels, options and views Dokima never declared.

    Proves 283.1. The faked repo matches the manifest and also has a bug label, a Someday priority option and a Mine view, which
    belong to the owner. The audit returns no lines."""
    record_property("proves", "283.1")
    a = audit("283.1")
    g = GitHub()
    g.label_list["bug"] = {"color": "ffffff", "description": "Something is broken"}
    g.field_map["Priority"]["Someday"] = {"color": "GRAY", "description": ""}
    g.view_map["Mine"] = {"layout": "board", "filter": "assignee:@me"}
    assert a.compare(g, REPO) == [], "283.1: a repo matching the manifest was reported as off"


# 283.2: drift goes on one pinned Setup issue, marked Needs you, and later runs update that same issue

def test_drift_opens_one_pinned_setup_issue_marked_needs_you(record_property, tmp_path):
    """Drift opens one pinned Setup issue, marked Needs you, listing each difference.

    Proves 283.2. Runs the audit on the seven-difference repo with no Setup issue open. Exactly one issue is opened, titled Setup;
    every line the audit found is a line of its body; it is pinned and marked Needs you; the run returns its number."""
    record_property("proves", "283.2")
    a = audit("283.2")
    g = drifted()
    lines = a.compare(drifted(), REPO)
    n = a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    assert g.kinds().count("create_issue") == 1, f"283.2: drift should open one Setup issue, the writes were {g.writes}"
    assert n in g.issues and n != 7, f"283.2: the run returned {n!r}, not the Setup issue it opened"
    issue = g.issues[n]
    assert "Setup" in issue["title"], f"283.2: the issue opened is titled {issue['title']!r}, not Setup"
    missing = [l for l in lines if l not in body_lines(issue["body"])]
    assert not missing, f"283.2: the Setup issue does not list these differences on their own line: {missing}"
    assert issue["pinned"], "283.2: the Setup issue was not pinned"
    assert issue["needs_you"], "283.2: the Setup issue was not marked Needs you on the board"


def test_a_later_run_updates_the_same_setup_issue(record_property, tmp_path):
    """A later run updates the open Setup issue with what is off now.

    Proves 283.2. A first run opens the Setup issue for a missing plan label. The label is then put back and the high label's
    color changes. The second run opens no issue; the same issue now lists the high label and no longer the plan label,
    and is still marked Needs you."""
    record_property("proves", "283.2")
    a = audit("283.2")
    root = codeowners(tmp_path, "* @alice\n")
    g = GitHub()
    del g.label_list["plan"]
    n = a.run(g, REPO, root)
    g.label_list["plan"] = copy.deepcopy(manifest.LABELS["plan"])
    g.label_list["high"]["color"] = "000000"
    g.issues[n]["needs_you"] = False
    again = a.run(g, REPO, root)
    assert g.kinds().count("create_issue") == 1, f"283.2: the second run opened another issue: {g.writes}"
    assert again == n, f"283.2: the second run returned {again!r}, not the open Setup issue #{n}"
    body = g.issues[n]["body"]
    one_line(body_lines(body), "283.2", "the high label's new color", "high", "000000")
    assert "1d76db" not in body, f"283.2: the plan label, now fixed, is still listed on the Setup issue:\n{body}"
    assert g.issues[n]["needs_you"], "283.2: the updated Setup issue is not marked Needs you"


def test_a_setup_issue_left_open_is_updated_not_duplicated(record_property, tmp_path):
    """A Setup issue left open by an earlier run is updated; no second one opens.

    Proves 283.2. Setup issue #7 is open from an earlier run listing old drift. The audit runs on the seven-difference repo: it opens
    no issue, #7's body lists today's differences and no longer the old line, and #7 is marked Needs you."""
    record_property("proves", "283.2")
    a = audit("283.2")
    g = drifted()
    g.issues = open_setup("Old drift\n")
    g.issues[7]["needs_you"] = False
    n = a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    assert "create_issue" not in g.kinds(), f"283.2: an open Setup issue was there, yet another was opened: {g.writes}"
    assert n == 7, f"283.2: the run returned {n!r}, not the open Setup issue #7"
    lines = body_lines(g.issues[7]["body"])
    assert "Old drift" not in lines, "283.2: the Setup issue still lists drift from an earlier run"
    missing = [l for l in a.compare(drifted(), REPO) if l not in lines]
    assert not missing, f"283.2: the updated Setup issue misses these differences: {missing}"
    assert g.issues[7]["needs_you"], "283.2: the updated Setup issue is not marked Needs you"


# 283.3: a clean run posts nothing, and closes a Setup issue left open with one line

def test_a_clean_run_posts_nothing(record_property, tmp_path):
    """A clean run with no Setup issue open writes nothing at all to GitHub.

    Proves 283.3. The faked repo matches the manifest and has no Setup issue. The run returns None and makes no write: no issue,
    comment, pin or board change."""
    record_property("proves", "283.3")
    a = audit("283.3")
    g = GitHub()
    assert a.run(g, REPO, codeowners(tmp_path, "* @alice\n")) is None, "283.3: a clean run returned a Setup issue"
    assert g.writes == [], f"283.3: a clean run wrote to GitHub: {g.writes}"


def test_a_clean_run_closes_the_setup_issue_with_one_line(record_property, tmp_path):
    """A clean run closes the open Setup issue with one line saying nothing is off.

    Proves 283.3. Setup issue #7 is open; the faked repo now matches the manifest. The run leaves exactly one comment on #7, a single
    line saying nothing is off, closes #7, opens no issue and marks nothing Needs you."""
    record_property("proves", "283.3")
    a = audit("283.3")
    g = GitHub(issues=open_setup())
    n = a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    comments = g.issues[7]["comments"]
    assert len(comments) == 1, f"283.3: closing the Setup issue should leave one comment, it left {comments}"
    text = comments[0].strip()
    assert "\n" not in text and "nothing is off" in text.lower(), \
        f"283.3: the closing comment should be one line saying nothing is off, it was {text!r}"
    assert g.issues[7]["state"] == "closed", "283.3: the Setup issue was left open though nothing is off"
    assert "create_issue" not in g.kinds() and "needs_you" not in g.kinds(), \
        f"283.3: a clean run opened an issue or marked one Needs you: {g.writes}"
    assert n == 7, f"283.3: the run returned {n!r}, not the Setup issue it closed"


# 283.4: the Setup issue mentions only the repo's own code owners, and nothing is posted outside the repo

def mentions(g):
    """Every @name in every issue body and comment the audit wrote."""
    text = " ".join([i["body"] for i in g.issues.values()] + [c for i in g.issues.values() for c in i["comments"]])
    return set(re.findall(r"(?<![\w.])@([A-Za-z0-9][A-Za-z0-9-]*)", text))


def test_the_setup_issue_mentions_only_the_code_owners(record_property, tmp_path):
    """The Setup issue mentions exactly the code owners of `*` in CODEOWNERS, nobody else.

    Proves 283.4. CODEOWNERS names alice and bob for `*` and carol for docs/ only. The audit opens the Setup issue on acme/widgets:
    it mentions alice and bob and no one else. A second repo whose CODEOWNERS names only dana mentions only dana."""
    record_property("proves", "283.4")
    a = audit("283.4")
    g = drifted()
    a.run(g, REPO, codeowners(tmp_path / "one", "* @alice @bob\ndocs/ @carol\n"))
    assert mentions(g) == {"alice", "bob"}, f"283.4: the Setup issue mentions {mentions(g)}, not exactly alice and bob"
    g = drifted()
    a.run(g, REPO, codeowners(tmp_path / "two", "* @dana\n"))
    assert mentions(g) == {"dana"}, f"283.4: with dana as the only code owner, the Setup issue mentions {mentions(g)}"


def test_the_audit_posts_only_on_the_repo_it_runs_on(record_property, tmp_path):
    """Every write the audit makes goes to the repo it runs on.

    Proves 283.4. Runs the audit on acme/widgets three times: opening the Setup issue, updating it, and closing it once clean. Every
    write names acme/widgets; then the same on other/place names only other/place."""
    record_property("proves", "283.4")
    a = audit("283.4")
    for repo in (REPO, "other/place"):
        g = drifted()
        root = codeowners(tmp_path / repo.replace("/", "-"), "* @alice\n")
        a.run(g, repo, root)
        g.label_list["plan"] = copy.deepcopy(manifest.LABELS["plan"])
        a.run(g, repo, root)
        clean = GitHub(issues={n: i for n, i in g.issues.items()})
        a.run(clean, repo, root)
        writes = g.writes + clean.writes
        assert writes, f"283.4: the audit on {repo} wrote nothing"
        elsewhere = [w for w in writes if w[1] != repo]
        assert not elsewhere, f"283.4: the audit on {repo} wrote outside it: {elsewhere}"


# 283.5: each setting the app cannot read gets its own line saying it could not be verified and why

def test_an_unreadable_branch_rule_is_never_shown_as_fine(record_property, tmp_path):
    """An unreadable branch rule gets a line saying it could not be verified and why.

    Proves 283.5. It is never shown as fine: the Setup issue stays open. GitHub refuses main's rule with 403; everything else matches. The audit returns one line naming main, saying it
    could not be verified, with GitHub's reason. The run with Setup issue #7 open does not close it: it lists that line
    and stays marked Needs you."""
    record_property("proves", "283.5")
    a = audit("283.5")
    g = GitHub(fail={"branch_rule": FORBIDDEN})
    lines = a.compare(g, REPO)
    assert len(lines) == 1, f"283.5: one unreadable branch rule should give one line, got {lines}"
    line = lines[0]
    assert "main" in line and "could not be verified" in line.lower() and "Resource not accessible by integration" in line, \
        f"283.5: the line should name main, say it could not be verified and give GitHub's reason: {line!r}"
    g = GitHub(fail={"branch_rule": FORBIDDEN}, issues=open_setup())
    g.issues[7]["needs_you"] = False
    a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    assert g.issues[7]["state"] == "open", "283.5: an unreadable branch rule was shown as fine: the Setup issue closed"
    assert line in body_lines(g.issues[7]["body"]), "283.5: the Setup issue does not list the unverified branch rule"
    assert g.issues[7]["needs_you"], "283.5: the Setup issue with an unverified setting is not marked Needs you"


def test_each_unreadable_setting_gets_its_own_line(record_property, tmp_path):
    """Two settings the app cannot read get two lines and open the Setup issue.

    Proves 283.5. GitHub refuses both main's rule and the app's permissions with 403; everything else matches. The audit returns two
    lines, one naming main and one naming permissions, each saying it could not be verified with GitHub's reason, and
    the run opens a Setup issue listing both."""
    record_property("proves", "283.5")
    a = audit("283.5")
    g = GitHub(fail={"branch_rule": FORBIDDEN, "permissions": FORBIDDEN})
    lines = a.compare(g, REPO)
    assert len(lines) == 2, f"283.5: two unreadable settings should give two lines, got {lines}"
    rule = [l for l in lines if "main" in l]
    assert len(rule) == 1, f"283.5: main's rule should be on exactly one line: {lines}"
    other = [l for l in lines if l not in rule]
    assert "permission" in other[0].lower(), f"283.5: the other line should name the app's permissions: {other[0]!r}"
    for what, hits in (("main", rule), ("permissions", other)):
        assert "could not be verified" in hits[0].lower() and "Resource not accessible by integration" in hits[0], \
            f"283.5: the {what} line should say it could not be verified and why: {hits[0]!r}"
    n = a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    assert n in g.issues, "283.5: unverified settings opened no Setup issue"
    assert all(l in body_lines(g.issues[n]["body"]) for l in lines), "283.5: the Setup issue misses an unverified setting"


# 283.6: a failed GitHub call is reported as not verified, never skipped

def test_a_failed_github_call_is_reported_as_not_verified(record_property, tmp_path):
    """A failed GitHub call is reported as not verified with GitHub's reason, never skipped.

    Proves 283.6. GitHub answers 502 when the audit reads the labels and the board's fields; everything else matches. The audit
    returns two lines, one naming the labels and one the fields, each saying it could not be verified with GitHub's
    words, and the run opens a Setup issue listing both instead of posting nothing."""
    record_property("proves", "283.6")
    a = audit("283.6")
    g = GitHub(fail={"labels": BROKEN, "fields": BROKEN})
    lines = a.compare(g, REPO)
    assert len(lines) == 2, f"283.6: two failed calls should give two lines, got {lines}"
    fields = [l for l in lines if "field" in l.lower()]
    assert len(fields) == 1, f"283.6: the failed fields read should be on exactly one line: {lines}"
    labels = [l for l in lines if l not in fields]
    assert "label" in labels[0].lower(), f"283.6: the other line should name the labels: {labels[0]!r}"
    for what, hits in (("label", labels), ("field", fields)):
        assert "could not be verified" in hits[0].lower() and "Server Error (HTTP 502)" in hits[0], \
            f"283.6: the {what} line should say it could not be verified and give GitHub's reason: {hits[0]!r}"
    n = a.run(g, REPO, codeowners(tmp_path, "* @alice\n"))
    assert n in g.issues and g.issues[n]["state"] == "open", "283.6: failed calls were skipped: no Setup issue opened"
    assert all(l in body_lines(g.issues[n]["body"]) for l in lines), "283.6: the Setup issue misses a failed call"

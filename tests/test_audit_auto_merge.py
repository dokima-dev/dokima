"""Tests for #588: the Setup issue says whether auto-merge is on, from GitHub's rules.

Auto-merge is on when Dokima's app sits on both of main's pull-request-only exemption lists: the branch rule's review
exemption (`required_pull_request_reviews.bypass_pull_request_allowances.apps`) and the merge queue ruleset's bypass
actors with `bypass_mode` `pull_request`. On neither, it is off: the default, and not drift. No repo variable is read.

Each test runs `python3 -m dokima.audit acme/widgets` from outside, as the audit workflow does, against the fake `gh`
of tests/fake_gh.py (through tests/test_audit_cli.py's Audit helper). The fake's app id is 1. What the tests expect
the Setup issue to say:
    on        a line saying "auto-merge is on"
    off       a line saying "auto-merge is off" and that this is the default
    half on   one listed line, naming only the list that lacks the app: "review exemption" when the branch rule lacks
              it, "merge queue" when the merge queue ruleset lacks it; it says neither "is on" nor "is off"
    unknown   a line about auto-merge saying it is not verified, with GitHub's reason; neither "is on" nor "is off"
On and off are not drift: on their own they open no Setup issue, so the on and off tests put one other setting off
(a missing label) to make the audit write one.
"""
import copy
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from test_audit_cli import Audit, FORBIDDEN, body_lines, clean, created  # noqa: E402

APP = 1
APP_BYPASS = {"actor_id": APP, "actor_type": "Integration", "bypass_mode": "pull_request"}
ADMIN_BYPASS = {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
ON = re.compile(r"auto-merge is on\b", re.I)
OFF = re.compile(r"auto-merge is off\b", re.I)


def merge_queue(*bypass):
    """main's merge queue ruleset, as GitHub answers it, with the given bypass actors."""
    return {"id": 11, "name": "main merge queue", "target": "branch", "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
            "rules": [{"type": "merge_queue", "parameters": {"merge_method": "SQUASH"}}, {"type": "pull_request"}],
            "bypass_actors": [dict(b) for b in bypass]}


def repo(review, queue, drift=True):
    """A fake repo with the app on each list as asked, maybe one label missing."""
    s = clean()
    s["review_bypass_apps"] = [APP] if review else [42]
    s["rulesets"] = [merge_queue(ADMIN_BYPASS, *([APP_BYPASS] if queue else []))]
    if drift:
        del s["labels"]["plan"]
    return s


def auto_merge_lines(issue):
    """Every line of the Setup issue's body that talks about auto-merge."""
    return [l for l in body_lines(issue["body"]) if "auto-merge" in l.lower()]


def setup(tmp_path, state, criterion, name):
    """Run the audit on the state; the Setup issue it opened and its auto-merge lines."""
    a = Audit(tmp_path / name, state)
    a.run(criterion)
    n, issue = created(a, criterion)
    return a, issue, auto_merge_lines(issue)


# 588.1: with the app on both exemption lists, the Setup issue says auto-merge is on

def test_with_the_app_on_both_lists_the_setup_issue_says_auto_merge_is_on(record_property, tmp_path):
    """With the app on both exemption lists, the Setup issue says auto-merge is on.

    Proves 588.1. The fake repo lists the app on the branch rule's review exemption and as a pull-request bypass of
    the merge queue ruleset; one label is missing so a Setup issue opens. Its body must say auto-merge is on and never
    that it is off. With the app on only one list, the issue opens even with nothing else off and names only the list
    that lacks the app. When GitHub refuses to show the rulesets, the issue says auto-merge is not verified, with
    GitHub's reason, and claims neither on nor off."""
    record_property("proves", "588.1")
    a, issue, lines = setup(tmp_path, repo(True, True), "588.1", "on")
    assert any(ON.search(l) for l in lines), \
        f"588.1: with the app on both lists, no line says auto-merge is on: {lines}\n{issue['body']}\n{a.why()}"
    assert not any(OFF.search(l) for l in lines), f"588.1: with the app on both lists, a line says it is off: {lines}"

    for name, review, queue, lacking, other in (("no-review", False, True, "review exemption", "merge queue"),
                                                ("no-queue", True, False, "merge queue", "review exemption")):
        a, issue, lines = setup(tmp_path, repo(review, queue, drift=False), "588.1", name)
        named = [l for l in lines if lacking in l.lower()]
        assert len(named) == 1, (f"588.1: with the app missing only from the {lacking}, one line should name it, got "
                                 f"{lines}\n{issue['body']}\n{a.why()}")
        assert other not in named[0].lower(), \
            f"588.1: the line should name only the list that lacks the app ({lacking}), not the {other}: {named[0]!r}"
        assert not ON.search(named[0]) and not OFF.search(named[0]), \
            f"588.1: with the app on one list only, auto-merge is neither on nor off: {named[0]!r}"

    s = repo(True, True)
    s["fail"] = {"rulesets": FORBIDDEN}
    a, issue, lines = setup(tmp_path, s, "588.1", "unknown")
    unknown = [l for l in lines if "not verified" in l.lower()]
    assert len(unknown) == 1 and "Resource not accessible by integration" in unknown[0], \
        (f"588.1: when GitHub will not show the rulesets, one auto-merge line should say not verified with GitHub's "
         f"reason, got {lines}\n{a.why()}")
    assert not any(ON.search(l) or OFF.search(l) for l in lines), \
        f"588.1: when a list cannot be read, the audit must not claim auto-merge is on or off: {lines}"


# 588.2: with the app on neither exemption list, the Setup issue says auto-merge is off, the default

def test_with_the_app_on_neither_list_the_setup_issue_says_auto_merge_is_off(record_property, tmp_path):
    """With the app on neither exemption list, the Setup issue says auto-merge is off.

    Proves 588.2. The fake repo lists another app on the review exemption and only the admin role on the merge queue
    ruleset; one label is missing so a Setup issue opens. Its body must say auto-merge is off and that this is the
    default, and never that it is on. With nothing else off, auto-merge off is not drift: the audit opens no Setup
    issue."""
    record_property("proves", "588.2")
    a, issue, lines = setup(tmp_path, repo(False, False), "588.2", "off")
    off = [l for l in lines if OFF.search(l)]
    assert off, f"588.2: with the app on neither list, no line says auto-merge is off: {lines}\n{issue['body']}\n{a.why()}"
    assert any("default" in l.lower() for l in off), f"588.2: the off line should say off is the default: {off}"
    assert not any(ON.search(l) for l in lines), f"588.2: with the app on neither list, a line says it is on: {lines}"

    quiet = Audit(tmp_path / "quiet", repo(False, False, drift=False))
    quiet.run("588.2")
    made = [w for w in quiet.state()["writes"] if w["kind"] == "create"]
    assert made == [], f"588.2: auto-merge off is the default, not drift, yet a Setup issue was opened\n{quiet.why()}"


# 588.3: Dokima's app no longer asks for permission to read repo variables

def test_the_app_no_longer_asks_to_read_repo_variables(record_property, tmp_path):
    """Dokima's app no longer asks to read repo variables, and the audit reads none.

    Proves 588.3. `dokima/app.json`'s permissions and the manifest's must both leave out `actions_variables`, while
    still asking for administration read, which the audit needs to read main's rule. Then the audit runs against a
    repo whose `DOKIMA_AUTO_MERGE` variable is set, and must make no call to the repo's Actions variables."""
    record_property("proves", "588.3")
    from dokima import manifest
    app = json.load(open(os.path.join(ROOT, "dokima", "app.json")))["default_permissions"]
    assert "actions_variables" not in app, f"588.3: dokima/app.json still asks to read repo variables: {app}"
    assert "actions_variables" not in manifest.PERMISSIONS, \
        f"588.3: the manifest still declares the repo variables permission: {manifest.PERMISSIONS}"
    assert app.get("administration") == "read", f"588.3: dokima/app.json lost administration read: {app}"

    s = repo(True, True)
    s["variables"] = {"DOKIMA_AUTO_MERGE": "on"}
    s["permissions"] = copy.deepcopy(manifest.PERMISSIONS)
    a = Audit(tmp_path, s)
    a.run("588.3")
    calls = [c for c in a.state()["calls"] if "actions/variables" in json.dumps(c)]
    assert calls == [], f"588.3: the audit still reads a repo variable: {calls}"

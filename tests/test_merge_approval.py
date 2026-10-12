"""A repo setting lets a passed code review merge through a narrow bypass (#557).

By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
`DOKIMA_MERGE_APPROVAL`, set to `true`, turns the setting on: once a code review passes, Dokima's app merges the pull
request as a bypass actor of the branch rule, a bypass the owner limits to pull requests (never direct pushes to main).
The bot never approves its own pull request. A pull request that changes a workflow file still waits for the owner,
whatever the setting.

These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
GitHub of test_automerge_confirmed.py where #60 is protected the way main is: a plain `gh pr merge` only turns on
auto-merge waiting on an approval ("accepts": "approval"). This file teaches that fake three more things:
  - the setting: `gh api repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL` (with or without -q/--jq `.value`) and
    `gh variable get DOKIMA_MERGE_APPROVAL` answer the value the test chose, 404 when it is unset, or a failure;
  - the bypass: when the test makes Dokima's app a bypass actor ("bypass": true), a merge it asks past the rule, by
    `gh pr merge --admin` or `gh api -X PUT repos/o/r/pulls/N/merge`, merges, as GitHub lets a bypass actor merge a
    pull request; when it is not one, GitHub refuses with its rule's words;
  - approving reviews, as GitHub answers them: the app may not approve the pull request it opened ("Can not approve
    your own pull request"), and no other key may either. Every one asked is recorded, so a test sees it was tried.
"""
import json
import os

import pytest

import test_automerge as ta
import test_automerge_confirmed as tc
from test_start import OWNER, PR

SETTING = "DOKIMA_MERGE_APPROVAL"
WAITS = f"Autopilot: PR #{PR} waits for your approval before it merges"
MERGED = f"Autopilot: merged PR #{PR}"
RULE = "At least 1 approving review is required by reviewers with write access"

APPROVAL_GH = r'''
SETTING = json.loads(SETTING_JSON)
def setting_answer():
    if SETTING.get("fail"):
        sys.stderr.write(SETTING["fail"] + "\n")
        sys.exit(1)
    if "value" not in SETTING:
        sys.stderr.write("HTTP 404: Not Found (https://api.github.com/repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL)\n")
        sys.exit(1)
_var_api = a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL", x) for x in a[1:])
_var_cli = a[:2] == ["variable", "get"] and "DOKIMA_MERGE_APPROVAL" in a
if _var_api or _var_cli:
    setting_answer()
    if _var_cli:
        print(SETTING["value"])
    else:
        out({"name": "DOKIMA_MERGE_APPROVAL", "value": SETTING["value"], "created_at": "2026-10-01T00:00:00Z",
             "updated_at": "2026-10-01T00:00:00Z"})
    sys.exit(0)
def approve(n, args):
    # GitHub never lets the app approve the pull request it opened, nor the workflow's own token approve at all.
    open(os.path.join(d, "approvals.jsonl"), "a").write(json.dumps({"pr": int(n), "args": args, "token": token}) + "\n")
    sys.stderr.write("HTTP 422: Unprocessable Entity: Can not approve your own pull request\n" if token == "fake-token"
                     else "HTTP 403: Resource not accessible by integration\n")
    sys.exit(1)
def review_fields():
    f = {}
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(a) and "=" in a[i + 1]:
            k, v = a[i + 1].split("=", 1)
            f[k] = v
    if "--input" in a:
        src = flag("--input")
        f.update(json.load(sys.stdin if src == "-" else open(src)) or {})
    return f
if a[:2] == ["pr", "review"]:
    n = pr_sel()
    if n is None:
        sys.stderr.write("no pull requests found\n")
        sys.exit(1)
    if "--approve" in a or "-a" in a:
        approve(n, a)
    print(f"Reviewed pull request o/r#{n}")
    sys.exit(0)
_m_rev = re.fullmatch(r"repos/o/r/pulls/(\d+)/reviews", PAPI or "")
if _m_rev and _m_rev.group(1) in PRS:
    n = _m_rev.group(1)
    f = review_fields()
    if (flag("-X", "--method") or ("POST" if f else "GET")).upper() == "POST":
        if str(f.get("event", "")).upper() == "APPROVE":
            approve(n, a)
        print(json.dumps({"id": 900, "state": str(f.get("event", "COMMENTED")).upper()}))
    else:
        print(json.dumps([]))
    sys.exit(0)
BYPASS = json.loads(BYPASS_JSON)
_m_put = re.fullmatch(r"repos/o/r/pulls/(\d+)/merge", PAPI or "")
_past = _m_put.group(1) if _m_put and (flag("-X", "--method") or "").upper() == "PUT" else (
    pr_sel() if a[:2] == ["pr", "merge"] and "--admin" in a else None)
if _past in PRS and token == "fake-token" and PRS[_past].get("accepts") == "approval" and not PRS[_past].get("merged"):
    if BYPASS:
        # Dokima's app is a bypass actor of the rule for pull requests: GitHub lets it merge this one past the rule.
        del PRS[_past]["accepts"]
        save_prs()
    else:
        merge_log(_past, "squash", flag("--match-head-commit"), "rule refused the bypass")
        sys.stderr.write(f"GraphQL: Repository rule violations found\n\n{RULE_TEXT}\n (mergePullRequest)\n")
        sys.exit(1)
'''


def fake_gh(setting, bypass):
    """test_automerge_confirmed.py's fake GitHub, taught the setting (`setting`), the app's bypass (`bypass`) and reviews."""
    fake = tc.fake_gh()
    head = f"SETTING_JSON = {json.dumps(setting)!r}\nBYPASS_JSON = {json.dumps(bypass)!r}\nRULE_TEXT = {RULE!r}\n"
    taught = fake.replace(tc.ACCEPTS_GH, head + APPROVAL_GH + tc.ACCEPTS_GH, 1)
    assert taught != fake and APPROVAL_GH in taught, "test setup: could not teach the fake GitHub the merge approval setting"
    return taught


class Approval:
    """Builds test_automerge's machines with this file's fake GitHub, #60 waiting on an approval to merge."""

    def __init__(self, setting, bypass):
        self.setting, self.bypass = setting, bypass

    def __enter__(self):
        self.saved = ta.fake_gh, ta.pr_state
        plain = ta.pr_state

        def state(issue, checks, files=None, refuse="", moves=False):
            st = plain(issue, checks, files, refuse, moves)
            st["accepts"] = "approval"
            return st
        ta.fake_gh, ta.pr_state = (lambda: fake_gh(self.setting, self.bypass)), state
        return self

    def __exit__(self, *exc):
        ta.fake_gh, ta.pr_state = self.saved


class SettingReview(ta.Review):
    """One code review of #60 on #57, with the given setting and bypass.

    `setting` is {} for unset, {"value": "..."} for a set variable, or {"fail": "message"} for a read GitHub fails."""

    def __init__(self, tmp, review, labels, checks, setting, bypass, files=None):
        with Approval(setting, bypass):
            super().__init__(tmp, review, labels, checks, files=files)

    def approvals(self):
        """Every approving review asked of GitHub: [{pr, args, token}]."""
        path = f"{self.tmp}/gh/approvals.jsonl"
        return [json.loads(l) for l in open(path)] if os.path.exists(path) else []

    def lines(self):
        """Every comment on #57 since the test began that starts `Autopilot:`."""
        return [b.strip() for b in self.new_comments("issue", 57) if b.strip().startswith("Autopilot:")]

    def said(self):
        """What the owner reads of every new comment on #57 and #60."""
        return [ta.visible(b) for b in self.new_comments("issue", 57) + self.new_comments("pr", PR)]


RUNS = {}
# name: (the review, the setting, whether Dokima's app is a bypass actor, the files #60 changes)
CASES = {
    "unset": (ta.PR_APPROVE, {}, True, None),
    "false": (ta.PR_APPROVE, {"value": "false"}, True, None),
    "unreadable": (ta.PR_APPROVE, {"fail": "HTTP 502: Bad Gateway"}, True, None),
    "on": (ta.PR_APPROVE, {"value": "true"}, True, None),
    "on-block": (ta.PR_BLOCK, {"value": "true"}, True, None),
    "on-refused": (ta.PR_APPROVE, {"value": "true"}, False, None),
    "on-workflow": (ta.PR_APPROVE, {"value": "true"}, True, ["x57.py", ta.WORKFLOW_FILE]),
}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Each code review run, run once on first use and shared between tests."""
    def get(name):
        if name not in RUNS:
            review, setting, bypass, files = CASES[name]
            RUNS[name] = SettingReview(tmp_path_factory.mktemp(name), review, ta.ON, ta.GREEN, setting, bypass, files)
        return RUNS[name]
    return get


def started(m, crit, case):
    """Fails naming the criterion when the code review never ran, so the test proves nothing."""
    assert m.agent_started(), f"{crit} ({case}): test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"


def merged_alone(m, crit, case):
    """#60 merged at its green head with Dokima's app key, and #57 says so once."""
    assert m.merged() == ta.HEAD, (f"{crit} ({case}): with the setting on and the code review passed, Dokima did not "
                                   f"merge #60 at its green head (merged: {m.merged()}, merges tried: "
                                   f"{[(t['args'], t['result']) for t in m.tried()]})\n{m.tail()}")
    assert all(t["token"] == "fake-token" for t in m.tried()), \
        f"{crit} ({case}): a merge was asked with a key other than Dokima's app key: {[t['token'] for t in m.tried()]}"
    assert m.lines() == [MERGED], f"{crit} ({case}): #57 did not get exactly one line {MERGED!r}: {m.lines()}"


def test_by_default_a_pull_request_waits_for_the_owners_approval(record_property, runs):
    """By default, a passed code review leaves the pull request waiting for your approval.

    Proves 557.1.
    Runs the code review approving #60 on autopilot, every check green, on a branch that needs an approval to merge,
    with Dokima's app able to bypass that rule, three ways the setting is not on: unset, set to `false`, and
    unreadable because GitHub fails the read. Each time #60 must stay open and #57 must get exactly the line
    `Autopilot: PR #60 waits for your approval before it merges`: the bypass is used only when the setting says so.
    A default means something only when there is a setting to change it: beside them, the same run with the setting
    `true` must merge #60, or the test fails as proving nothing."""
    record_property("proves", "557.1")
    for case in ("unset", "false", "unreadable"):
        m = runs(case)
        started(m, "557.1", case)
        assert m.merged() is None, (f"557.1 ({case}): #60 merged with no owner approval though the setting is not on "
                                    f"(merges tried: {[(t['args'], t['result']) for t in m.tried()]})")
        assert m.lines() == [WAITS], (f"557.1 ({case}): #57 did not get exactly one line reading {WAITS!r}, as today: "
                                      f"{m.lines()}\n{m.tail()}")
    c = runs("on")
    assert c.merged() == ta.HEAD, ("557.1: test setup: with the setting `true` Dokima did not merge #60, so there is no "
                                   "setting and waiting by default proves nothing")


def test_with_the_setting_on_a_passed_code_review_approves_and_autopilot_merges(record_property, runs):
    """With the setting on, Dokima's app merges a passed pull request through its bypass.

    Proves 557.2.
    Runs the code review approving #60 on autopilot, every check green, with `DOKIMA_MERGE_APPROVAL` set to `true`, on a
    branch whose rule needs an approval and lets Dokima's app bypass it for pull requests. #60 must merge at its green
    head with the app's key, and #57 must get exactly one line `Autopilot: merged PR #60`. GitHub refuses the bot's
    approval of its own pull request, so the merge must come from the bypass, not an approval. Beside it, a code
    review that blocks merges nothing; and when GitHub refuses the bypass (the app is not a bypass actor), #60 stays
    open and a comment mentioning the owner gives GitHub's reason."""
    record_property("proves", "557.2")
    m = runs("on")
    started(m, "557.2", "on")
    merged_alone(m, "557.2", "on")
    b = runs("on-block")
    started(b, "557.2", "on, review blocks")
    assert b.merged() is None, "557.2 (on, review blocks): #60 merged though its code review blocked"
    assert not any(l.startswith("Autopilot: merged") for l in b.lines()), \
        f"557.2 (on, review blocks): #57 says #60 merged: {b.lines()}"
    r = runs("on-refused")
    started(r, "557.2", "on, bypass refused")
    assert r.merged() is None, "557.2 (on, bypass refused): #60 merged though GitHub refused the bypass"
    assert not any(l.startswith("Autopilot: merged") for l in r.lines()), \
        f"557.2 (on, bypass refused): #57 says #60 merged: {r.lines()}"
    assert any(f"@{OWNER}" in s and RULE in s for s in r.said()), \
        (f"557.2 (on, bypass refused): no comment on #57 or #60 mentions @{OWNER} and gives GitHub's reason {RULE!r}: "
         f"{[s[-400:] for s in r.said()]}\n{r.tail()}")


def test_a_pull_request_changing_a_workflow_file_still_waits_whatever_the_setting(record_property, runs):
    """A pull request changing a workflow file never merges by itself and waits for you.

    Proves 557.3.
    Runs the code review approving #60 on autopilot, every check green, the setting on and Dokima's app able to bypass
    the rule, where #60 changes .github/workflows/ci.yml. #60 must stay open, no `Autopilot: merged` line may be
    posted, and #60 must get a comment naming .github/workflows and mentioning the owner. Beside it, the same run on a
    pull request with no workflow file merges."""
    record_property("proves", "557.3")
    m = runs("on-workflow")
    started(m, "557.3", "on, workflow file")
    assert m.merged() is None, "557.3: #60 merged though it changes a workflow file"
    assert not any(l.startswith("Autopilot: merged") for l in m.lines()), f"557.3: #57 says #60 merged: {m.lines()}"
    on_pr = [ta.visible(b) for b in m.new_comments("pr", PR)]
    assert any(f"@{OWNER}" in b and ".github/workflows" in b for b in on_pr), \
        f"557.3: no comment on #60 names .github/workflows and mentions @{OWNER}: {[b[-400:] for b in on_pr]}\n{m.tail()}"
    c = runs("on")
    assert c.merged() == ta.HEAD, \
        "557.3: test setup: with no workflow file and the setting on, #60 did not merge, so this proves nothing"

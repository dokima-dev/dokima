"""A repo setting lets a passed code review approve the pull request (#557).

By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
`DOKIMA_MERGE_APPROVAL`, set to `true`, turns the setting on: a code review that passes then approves the pull request
on GitHub as Dokima's bot, and autopilot merges it with no owner step. A pull request that changes a workflow file
still waits for the owner, whatever the setting.

These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
GitHub of test_automerge_confirmed.py where #60 is protected the way main is: `gh pr merge` only turns on auto-merge
waiting on an approval ("accepts": "approval"). This file teaches that fake three more things:
  - the setting: `gh api repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL` (with or without -q/--jq `.value`) and
    `gh variable get DOKIMA_MERGE_APPROVAL` answer the value the test chose, 404 when it is unset, or a failure;
  - an approving review: `gh pr review 60 --approve` and `gh api -X POST repos/o/r/pulls/60/reviews` with event APPROVE
    (as -f/-F fields or --input JSON) record it in approvals.jsonl; only Dokima's app key (fake-token) may approve;
  - once Dokima's bot approved #60, GitHub's protection is met: `gh pr merge` merges it for real.
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
    open(os.path.join(d, "approvals.jsonl"), "a").write(json.dumps({"pr": int(n), "args": args, "token": token}) + "\n")
    if token != "fake-token":
        sys.stderr.write("HTTP 403: Resource not accessible by integration\n")
        sys.exit(1)
    PRS[n].setdefault("approved_by", [])
    PRS[n]["approved_by"].append(token)
    save_prs()
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
        print(json.dumps([{"id": 900, "state": "APPROVED", "user": {"login": "dokima-runtime[bot]"},
                           "commit_id": PRS[n]["head"]} for _ in PRS[n].get("approved_by", [])]))
    sys.exit(0)
for _p in PRS.values():
    # Dokima's bot approved it: the protection that waited on an approval is met, so a merge merges.
    if _p.get("approved_by") and _p.get("accepts") == "approval":
        del _p["accepts"]
'''


def fake_gh(setting):
    """test_automerge_confirmed.py's fake GitHub, taught the merge approval setting (`setting`) and approving reviews."""
    fake = tc.fake_gh()
    taught = fake.replace(tc.ACCEPTS_GH, f"SETTING_JSON = {json.dumps(setting)!r}\n" + APPROVAL_GH + tc.ACCEPTS_GH, 1)
    assert taught != fake and APPROVAL_GH in taught, "test setup: could not teach the fake GitHub the merge approval setting"
    return taught


class Approval:
    """Builds test_automerge's machines with this file's fake GitHub, #60 waiting on an approval to merge."""

    def __init__(self, setting):
        self.setting = setting

    def __enter__(self):
        self.saved = ta.fake_gh, ta.pr_state
        plain = ta.pr_state

        def state(issue, checks, files=None, refuse="", moves=False):
            st = plain(issue, checks, files, refuse, moves)
            st["accepts"] = "approval"
            return st
        ta.fake_gh, ta.pr_state = (lambda: fake_gh(self.setting)), state
        return self

    def __exit__(self, *exc):
        ta.fake_gh, ta.pr_state = self.saved


class SettingReview(ta.Review):
    """One code review of #60 on #57, with the merge approval setting as `setting` says.

    `setting` is {} for unset, {"value": "..."} for a set variable, or {"fail": "message"} for a read GitHub fails."""

    def __init__(self, tmp, review, labels, checks, setting, files=None):
        with Approval(setting):
            super().__init__(tmp, review, labels, checks, files=files)

    def approvals(self):
        """Every approving review asked of GitHub: [{pr, args, token}]."""
        path = f"{self.tmp}/gh/approvals.jsonl"
        return [json.loads(l) for l in open(path)] if os.path.exists(path) else []

    def lines(self):
        """Every comment on #57 since the test began that starts `Autopilot:`."""
        return [b.strip() for b in self.new_comments("issue", 57) if b.strip().startswith("Autopilot:")]


RUNS = {}
CASES = {
    "unset": (ta.PR_APPROVE, {}, None),
    "false": (ta.PR_APPROVE, {"value": "false"}, None),
    "unreadable": (ta.PR_APPROVE, {"fail": "HTTP 502: Bad Gateway"}, None),
    "on": (ta.PR_APPROVE, {"value": "true"}, None),
    "on-block": (ta.PR_BLOCK, {"value": "true"}, None),
    "on-workflow": (ta.PR_APPROVE, {"value": "true"}, ["x57.py", ta.WORKFLOW_FILE]),
}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Each code review run, run once on first use and shared between tests."""
    def get(name):
        if name not in RUNS:
            review, setting, files = CASES[name]
            RUNS[name] = SettingReview(tmp_path_factory.mktemp(name), review, ta.ON, ta.GREEN, setting, files)
        return RUNS[name]
    return get


def started(m, crit, case):
    """Fails naming the criterion when the code review never ran, so the test proves nothing."""
    assert m.agent_started(), f"{crit} ({case}): test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"


def waits_today(m, crit, case):
    """#60 is not approved or merged, and #57 says it waits for the owner."""
    started(m, crit, case)
    assert m.approvals() == [], f"{crit} ({case}): Dokima approved #60 though the setting is not on: {m.approvals()}"
    assert m.merged() is None, f"{crit} ({case}): #60 merged with no owner approval though the setting is not on"
    assert m.lines() == [WAITS], (f"{crit} ({case}): #57 did not get exactly one line reading {WAITS!r}, as today: "
                                  f"{m.lines()}\n{m.tail()}")


def test_by_default_a_pull_request_waits_for_the_owners_approval(record_property, runs):
    """By default, a passed code review leaves the pull request waiting for your approval.

    Proves 557.1.
    Runs the code review approving #60 on autopilot, every check green, on a branch that needs an approval to merge,
    three ways the setting is not on: unset, set to `false`, and unreadable because GitHub fails the read. Each time
    Dokima must submit no approving review, #60 must stay open, and #57 must get exactly the line
    `Autopilot: PR #60 waits for your approval before it merges`. A default means something only when there is a
    setting to change it: beside them, the same run with the setting `true` must be approved by Dokima, or the test
    fails as proving nothing."""
    record_property("proves", "557.1")
    for case in ("unset", "false", "unreadable"):
        waits_today(runs(case), "557.1", case)
    c = runs("on")
    assert c.approvals(), ("557.1: test setup: with the setting `true` Dokima approved nothing, so there is no setting "
                           "and waiting by default proves nothing")


def test_with_the_setting_on_a_passed_code_review_approves_and_autopilot_merges(record_property, runs):
    """With the setting on, a passed review approves the pull request and autopilot merges it.

    Proves 557.2.
    Runs the code review approving #60 on autopilot, every check green, with `DOKIMA_MERGE_APPROVAL` set to `true`, on a
    branch that needs an approval to merge. Dokima's bot must approve #60 on GitHub with its app key, #60 must merge at
    its green head without --admin, and #57 must get exactly one line `Autopilot: merged PR #60` and no waiting line.
    Beside it, a code review that blocks with the setting on approves nothing and merges nothing."""
    record_property("proves", "557.2")
    m = runs("on")
    started(m, "557.2", "on")
    assert m.approvals(), f"557.2 (on): the passed code review did not approve #60 on GitHub with the setting on:\n{m.tail()}"
    assert all(r["token"] == "fake-token" for r in m.approvals()), \
        f"557.2 (on): #60 was approved with a key other than Dokima's app key: {[r['token'] for r in m.approvals()]}"
    assert m.merged() == ta.HEAD, (f"557.2 (on): #60 was approved but autopilot did not merge it at its green head "
                                   f"(merged: {m.merged()}, merges tried: {[(t['args'], t['result']) for t in m.tried()]})\n{m.tail()}")
    assert not any("--admin" in t["args"] for t in m.tried()), \
        f"557.2 (on): the merge went past branch protection with --admin instead of through the approval: {m.tried()}"
    assert m.lines() == [MERGED], f"557.2 (on): #57 did not get exactly one line {MERGED!r}: {m.lines()}"
    b = runs("on-block")
    started(b, "557.2", "on, review blocks")
    assert b.approvals() == [], f"557.2 (on, review blocks): a blocking code review approved #60: {b.approvals()}"
    assert b.merged() is None, "557.2 (on, review blocks): #60 merged though its code review blocked"


def test_a_pull_request_changing_a_workflow_file_still_waits_whatever_the_setting(record_property, runs):
    """A pull request changing a workflow file is never approved and waits for you.

    Proves 557.3.
    Runs the code review approving #60 on autopilot, every check green, the setting on, where #60 changes
    .github/workflows/ci.yml. Dokima must submit no approving review, #60 must stay open, no `Autopilot: merged` line may
    be posted, and #60 must get a comment naming .github/workflows and mentioning the owner. Beside it, the same run on
    a pull request with no workflow file is approved and merges."""
    record_property("proves", "557.3")
    m = runs("on-workflow")
    started(m, "557.3", "on, workflow file")
    assert m.approvals() == [], f"557.3: Dokima approved #60 though it changes a workflow file: {m.approvals()}"
    assert m.merged() is None, "557.3: #60 merged though it changes a workflow file"
    assert not any(l.startswith("Autopilot: merged") for l in m.lines()), f"557.3: #57 says #60 merged: {m.lines()}"
    on_pr = [ta.visible(b) for b in m.new_comments("pr", PR)]
    assert any(f"@{OWNER}" in b and ".github/workflows" in b for b in on_pr), \
        f"557.3: no comment on #60 names .github/workflows and mentions @{OWNER}: {[b[-400:] for b in on_pr]}\n{m.tail()}"
    c = runs("on")
    assert c.approvals() and c.merged() == ta.HEAD, \
        f"557.3: test setup: with no workflow file and the setting on, #60 was not approved and merged, so this proves nothing"

"""A repo setting lets a passed code review merge through a narrow bypass (#557).

By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
`DOKIMA_AUTO_MERGE`, set to `on`, turns the setting on; unset or `off`, it is off. With it on, once a code review
passes, Dokima's app merges the pull request directly, as a bypass actor of the branch rule, a bypass the owner limits
to pull requests (never direct pushes to main); only when every check on its head is green and its branch contains
main's newest commit, and never when it changes a workflow file. The bot never approves its own pull request.

These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
GitHub of test_automerge_confirmed.py where #60 is protected the way main is: a plain `gh pr merge` only turns on
auto-merge waiting on an approval ("accepts": "approval"). This file teaches that fake four more things:
  - the setting: `gh api repos/o/r/actions/variables/DOKIMA_AUTO_MERGE` (with or without -q/--jq `.value`) and
    `gh variable get DOKIMA_AUTO_MERGE` answer the value the test chose, 404 when it is unset, or a failure;
  - the bypass: when the test makes Dokima's app a bypass actor ("bypass": true), a merge it asks past the rule, by
    `gh pr merge --admin` or `gh api -X PUT repos/o/r/pulls/N/merge`, merges, as GitHub lets a bypass actor merge a
    pull request, whatever its checks or base; when it is not one, GitHub refuses with its rule's words;
  - a branch behind main: `gh api repos/o/r/compare/main...HEAD` (HEAD the head commit or the branch) answers
    `behind_by` 1 and `status` "diverged", the pull request's `mergeStateStatus` is BEHIND and its REST
    `mergeable_state` is "behind"; a branch that contains main's newest commit answers `behind_by` 0, "ahead",
    BLOCKED and "blocked";
  - approving reviews, as GitHub answers them: the app may not approve the pull request it opened ("Can not approve
    your own pull request"), and no other key may either. Every one asked is recorded, so a test sees it was tried.
"""
import json
import os

import pytest

import test_automerge as ta
import test_automerge_confirmed as tc
from test_start import OWNER, PR

SETTING = "DOKIMA_AUTO_MERGE"
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
        sys.stderr.write("HTTP 404: Not Found (https://api.github.com/repos/o/r/actions/variables/DOKIMA_AUTO_MERGE)\n")
        sys.exit(1)
_var_api = a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/actions/variables/DOKIMA_AUTO_MERGE", x) for x in a[1:])
_var_cli = a[:2] == ["variable", "get"] and "DOKIMA_AUTO_MERGE" in a
if _var_api or _var_cli:
    setting_answer()
    if _var_cli:
        print(SETTING["value"])
    else:
        out({"name": "DOKIMA_AUTO_MERGE", "value": SETTING["value"], "created_at": "2026-10-01T00:00:00Z",
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


BEHIND_GH = r'''
_acc_pr_obj, _acc_rest_pr = pr_obj, rest_pr
def pr_obj(n):
    o = _acc_pr_obj(n)
    if PRS[n].get("behind"):
        o["mergeStateStatus"] = "BEHIND"
    return o
def rest_pr(n):
    o = _acc_rest_pr(n)
    o["mergeable_state"] = "behind" if PRS[n].get("behind") else "blocked" if PRS[n].get("accepts") else "clean"
    return o
_m_cmp = (re.fullmatch(r"/?repos/o/r/compare/(?:refs/heads/)?main\.\.\.?(.+)", next((x for x in a[1:] if "/compare/" in x), "").split("?")[0])
          if a[:1] == ["api"] else None)
if _m_cmp:
    _n = next((k for k, p in PRS.items() if _m_cmp.group(1) in (p["head"], p["branch"], "refs/heads/" + p["branch"])), None)
    if _n is None:
        sys.stderr.write("HTTP 404: Not Found\n")
        sys.exit(1)
    _b = 1 if PRS[_n].get("behind") else 0
    pick({"status": "diverged" if _b else "ahead", "ahead_by": 1, "behind_by": _b, "total_commits": 1,
          "base_commit": {"sha": "d4" * 20}, "merge_base_commit": {"sha": ("e5" if _b else "d4") * 20}})
    sys.exit(0)
'''


def fake_gh(setting, bypass):
    """test_automerge_confirmed.py's fake GitHub, taught the setting (`setting`), the app's bypass (`bypass`), reviews
    and branches behind main."""
    fake = tc.fake_gh()
    head = f"SETTING_JSON = {json.dumps(setting)!r}\nBYPASS_JSON = {json.dumps(bypass)!r}\nRULE_TEXT = {RULE!r}\n"
    taught = fake.replace(tc.ACCEPTS_GH, head + APPROVAL_GH + tc.ACCEPTS_GH + BEHIND_GH, 1)
    assert taught != fake and APPROVAL_GH in taught and BEHIND_GH in taught, \
        "test setup: could not teach the fake GitHub the auto-merge setting"
    return taught


class Approval:
    """Builds test_automerge's machines with this file's fake GitHub, #60 waiting on an approval to merge."""

    def __init__(self, setting, bypass, behind=False):
        self.setting, self.bypass, self.behind = setting, bypass, behind

    def __enter__(self):
        self.saved = ta.fake_gh, ta.pr_state
        plain, behind = ta.pr_state, self.behind

        def state(issue, checks, files=None, refuse="", moves=False):
            st = plain(issue, checks, files, refuse, moves)
            st["accepts"] = "approval"
            st["behind"] = behind
            return st
        ta.fake_gh, ta.pr_state = (lambda: fake_gh(self.setting, self.bypass)), state
        return self

    def __exit__(self, *exc):
        ta.fake_gh, ta.pr_state = self.saved


class SettingReview(ta.Review):
    """One code review of #60 on #57, with the given setting, bypass, checks and base.

    `setting` is {} for unset, {"value": "..."} for a set variable, or {"fail": "message"} for a read GitHub fails;
    `behind` makes #60's branch miss main's newest commit."""

    def __init__(self, tmp, review, labels, checks, setting, bypass, files=None, behind=False):
        with Approval(setting, bypass, behind):
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
ON_VALUE = {"value": "on"}
# name: (the review, the setting, whether Dokima's app is a bypass actor, #60's checks, the files #60 changes,
#        whether #60's branch misses main's newest commit)
CASES = {
    "unset": (ta.PR_APPROVE, {}, True, ta.GREEN, None, False),
    "off": (ta.PR_APPROVE, {"value": "off"}, True, ta.GREEN, None, False),
    "unreadable": (ta.PR_APPROVE, {"fail": "HTTP 502: Bad Gateway"}, True, ta.GREEN, None, False),
    "on": (ta.PR_APPROVE, ON_VALUE, True, ta.GREEN, None, False),
    "on-block": (ta.PR_BLOCK, ON_VALUE, True, ta.GREEN, None, False),
    "on-refused": (ta.PR_APPROVE, ON_VALUE, False, ta.GREEN, None, False),
    "on-red": (ta.PR_APPROVE, ON_VALUE, True, ta.RED, None, False),
    "on-behind": (ta.PR_APPROVE, ON_VALUE, True, ta.GREEN, None, True),
    "on-workflow": (ta.PR_APPROVE, ON_VALUE, True, ta.GREEN, ["x57.py", ta.WORKFLOW_FILE], False),
}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Each code review run, run once on first use and shared between tests."""
    def get(name):
        if name not in RUNS:
            review, setting, bypass, checks, files, behind = CASES[name]
            RUNS[name] = SettingReview(tmp_path_factory.mktemp(name), review, ta.ON, checks, setting, bypass, files,
                                       behind)
        return RUNS[name]
    return get


def started(m, crit, case):
    """Fails naming the criterion when the code review never ran, so the test proves nothing."""
    assert m.agent_started(), f"{crit} ({case}): test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"


def tried(m):
    """The merges asked of GitHub, as (args, result), for a failure message."""
    return [(t["args"], t["result"]) for t in m.tried()]


def merged_alone(m, crit, case):
    """#60 merged at its green head with Dokima's app key, and #57 says so once."""
    assert m.merged() == ta.HEAD, (f"{crit} ({case}): with the setting on and the code review passed, Dokima did not "
                                   f"merge #60 at its green head (merged: {m.merged()}, merges tried: {tried(m)})\n"
                                   f"{m.tail()}")
    assert all(t["token"] == "fake-token" for t in m.tried()), \
        f"{crit} ({case}): a merge was asked with a key other than Dokima's app key: {[t['token'] for t in m.tried()]}"
    assert m.lines() == [MERGED], f"{crit} ({case}): #57 did not get exactly one line {MERGED!r}: {m.lines()}"


def not_merged(m, crit, case, why):
    """#60 is still open and nothing claims it merged."""
    assert m.merged() is None, f"{crit} ({case}): #60 merged though {why} (merges tried: {tried(m)})"
    assert not any(l.startswith("Autopilot: merged") for l in m.lines()), f"{crit} ({case}): #57 says #60 merged: {m.lines()}"


def owner_told(m, crit, case, *words):
    """A comment on #57 or #60 mentions the owner and holds every word given."""
    assert any(f"@{OWNER}" in s and all(w in s for w in words) for s in m.said()), \
        (f"{crit} ({case}): no comment on #57 or #60 mentions @{OWNER} and says {words}: "
         f"{[s[-400:] for s in m.said()]}\n{m.tail()}")


def test_by_default_a_pull_request_waits_for_the_owners_approval(record_property, runs):
    """By default, a passed code review leaves the pull request waiting for your approval.

    Proves 557.1.
    Runs the code review approving #60 on autopilot, every check green, on a branch that needs an approval to merge,
    with Dokima's app able to bypass that rule, three ways the setting is not on: `DOKIMA_AUTO_MERGE` unset, set to
    `off`, and unreadable because GitHub fails the read. Each time #60 must stay open and #57 must get exactly the line
    `Autopilot: PR #60 waits for your approval before it merges`: the bypass is used only when the setting says so.
    A default means something only when there is a setting to change it: beside them, the same run with the setting
    `on` must merge #60, or the test fails as proving nothing."""
    record_property("proves", "557.1")
    for case in ("unset", "off", "unreadable"):
        m = runs(case)
        started(m, "557.1", case)
        assert m.merged() is None, (f"557.1 ({case}): #60 merged with no owner approval though the setting is not on "
                                    f"(merges tried: {tried(m)})")
        assert m.lines() == [WAITS], (f"557.1 ({case}): #57 did not get exactly one line reading {WAITS!r}, as today: "
                                      f"{m.lines()}\n{m.tail()}")
    c = runs("on")
    assert c.merged() == ta.HEAD, ("557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so "
                                   "waiting by default proves nothing")


def test_with_the_setting_on_dokima_merges_a_passed_green_up_to_date_pull_request_directly(record_property, runs):
    """With the setting on, Dokima merges a passed, green, up-to-date pull request by itself.

    Proves 557.2.
    Runs the code review approving #60 on autopilot, every check green, its branch holding main's newest commit, with
    `DOKIMA_AUTO_MERGE` set to `on`, on a branch whose rule needs an approval and lets Dokima's app bypass it for pull
    requests. #60 must merge at its green head with the app's key, and #57 must get exactly one line
    `Autopilot: merged PR #60`. GitHub refuses the bot's approval of its own pull request, so the merge must come from
    the bypass. The fake lets the bypass merge anything, so each case below proves Dokima checks it itself. #60 must
    stay open, with no merged line, when: the code review blocks; GitHub refuses the bypass (a comment mentioning the
    owner gives GitHub's reason); a check on its head is red (a comment mentioning the owner names the red check);
    its branch misses main's newest commit (a comment mentioning the owner names main); it changes a workflow file
    (a comment on #60 mentioning the owner names .github/workflows)."""
    record_property("proves", "557.2")
    m = runs("on")
    started(m, "557.2", "on")
    merged_alone(m, "557.2", "on")
    b = runs("on-block")
    started(b, "557.2", "on, review blocks")
    not_merged(b, "557.2", "on, review blocks", "its code review blocked")
    r = runs("on-refused")
    started(r, "557.2", "on, bypass refused")
    not_merged(r, "557.2", "on, bypass refused", "GitHub refused the bypass")
    owner_told(r, "557.2", "on, bypass refused", RULE)
    red = runs("on-red")
    started(red, "557.2", "on, red check")
    not_merged(red, "557.2", "on, red check", f"the check {ta.RED_NAME} failed on its head")
    owner_told(red, "557.2", "on, red check", ta.RED_NAME)
    behind = runs("on-behind")
    started(behind, "557.2", "on, behind main")
    not_merged(behind, "557.2", "on, behind main", "its branch does not contain main's newest commit")
    owner_told(behind, "557.2", "on, behind main", "main")
    w = runs("on-workflow")
    started(w, "557.2", "on, workflow file")
    not_merged(w, "557.2", "on, workflow file", "it changes a workflow file")
    on_pr = [ta.visible(x) for x in w.new_comments("pr", PR)]
    assert any(f"@{OWNER}" in x and ".github/workflows" in x for x in on_pr), \
        (f"557.2 (on, workflow file): no comment on #60 names .github/workflows and mentions @{OWNER}: "
         f"{[x[-400:] for x in on_pr]}\n{w.tail()}")

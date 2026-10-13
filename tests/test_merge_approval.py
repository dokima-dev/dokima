"""Autopilot only asks GitHub to merge; GitHub merges it or holds it (#587).

Before, a repo variable, `DOKIMA_AUTO_MERGE`, said whether Dokima's app merged past main's approval rule (#557). The app
cannot read repo variables, so the switch did nothing, while GitHub let the app merge anyway. Now no variable is read:
Dokima asks GitHub to merge, and GitHub's own rules decide. When GitHub lets the app merge without approval, the pull
request merges and the issue says so; when GitHub needs the owner's approval, it stays open and the issue says it waits.

These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
GitHub of test_automerge_confirmed.py where #60 is protected the way main is: a plain `gh pr merge` only turns on
auto-merge waiting on an approval ("accepts": "approval"). This file teaches that fake five more things:
  - a repo variable: `gh api repos/o/r/actions/variables/...` and `gh variable ...` answer the value the test chose,
    or 404 when unset, and every such read is recorded, so a test sees Dokima asked;
  - the bypass: when the test makes Dokima's app a bypass actor of main's rules for pull requests ("bypass": true),
    a merge asked of GitHub directly (`gh api -X PUT repos/o/r/pulls/N/merge` or `gh pr merge --admin`) merges, as
    GitHub lets a bypass actor merge, whatever its checks or base; a plain `gh pr merge` still only turns on
    auto-merge, as gh does when the pull request shows blocked. When the app is no bypass actor, GitHub refuses a
    direct merge with its rule's words;
  - a plain merge GitHub refuses outright for a missing approval ("refuse_plain": true), as gh does when auto-merge
    is not turned on; `gh pr merge --auto` then turns auto-merge on, waiting on the approval;
  - a branch behind main: `gh api repos/o/r/compare/main...HEAD` (HEAD the head commit or the branch) answers
    `behind_by` 1 and `status` "diverged", the pull request's `mergeStateStatus` is BEHIND and its REST
    `mergeable_state` is "behind"; a branch that contains main's newest commit answers `behind_by` 0, "ahead",
    BLOCKED and "blocked";
  - approving reviews, as GitHub answers them: the app may not approve the pull request it opened ("Can not approve
    your own pull request"), and no other key may either.
"""
import json
import os
import re

import pytest

import test_automerge as ta
import test_automerge_confirmed as tc
from test_start import OWNER, PR

WAITS = f"Autopilot: PR #{PR} waits for your approval before it merges"
MERGED = f"Autopilot: merged PR #{PR}"
RULE = "At least 1 approving review is required by reviewers with write access"

APPROVAL_GH = r'''
GH = json.loads(GH_JSON)
if (a[:1] == ["api"] and any("actions/variables" in x for x in a[1:])) or a[:1] == ["variable"]:
    # Every read of a repo variable is recorded: Dokima's merge must read none (#587).
    open(os.path.join(d, "variables.jsonl"), "a").write(json.dumps(a) + "\n")
    v = GH.get("variable") or {}
    if "value" not in v:
        sys.stderr.write("HTTP 404: Not Found (https://api.github.com/repos/o/r/actions/variables/DOKIMA_AUTO_MERGE)\n")
        sys.exit(1)
    if a[:1] == ["variable"]:
        print(v["value"])
    else:
        out({"name": "DOKIMA_AUTO_MERGE", "value": v["value"], "created_at": "2026-10-01T00:00:00Z",
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
_m_put = re.fullmatch(r"repos/o/r/pulls/(\d+)/merge", PAPI or "")
_direct = _m_put.group(1) if _m_put and (flag("-X", "--method") or "").upper() == "PUT" else (
    pr_sel() if a[:2] == ["pr", "merge"] and "--admin" in a else None)
_plain = pr_sel() if a[:2] == ["pr", "merge"] and "--admin" not in a else None
_n = _direct or _plain
if _n in PRS and token == "fake-token" and PRS[_n].get("accepts") == "approval" and not PRS[_n].get("merged"):
    if _direct and GH.get("bypass"):
        # Dokima's app is a bypass actor of main's rules for pull requests: GitHub lets it merge this one directly.
        del PRS[_n]["accepts"]
        save_prs()
    elif _direct:
        merge_log(_n, "squash", flag("--match-head-commit"), "rule refused the bypass")
        sys.stderr.write(f"GraphQL: Repository rule violations found\n\n{RULE_TEXT}\n (mergePullRequest)\n")
        sys.exit(1)
    elif "--auto" in a:
        PRS[_n]["auto"] = True
        save_prs()
        merge_log(_n, "squash", flag("--match-head-commit"), "auto-merge turned on")
        print(f"Pull request o/r#{_n} will be automatically merged when all requirements are met")
        sys.exit(0)
    elif GH.get("refuse_plain"):
        merge_log(_n, "squash", flag("--match-head-commit"), "refused: approval")
        sys.stderr.write(f"X Pull request o/r#{_n} is not mergeable: the base branch policy prohibits the merge. "
                         f"{RULE_TEXT}\n")
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


def fake_gh(gh):
    """test_automerge_confirmed.py's fake GitHub, taught repo variables, the app's bypass, refused plain merges,
    reviews and branches behind main, as `gh` sets them."""
    fake = tc.fake_gh()
    head = f"GH_JSON = {json.dumps(gh)!r}\nRULE_TEXT = {RULE!r}\n"
    taught = fake.replace(tc.ACCEPTS_GH, head + APPROVAL_GH + tc.ACCEPTS_GH + BEHIND_GH, 1)
    assert taught != fake and APPROVAL_GH in taught and BEHIND_GH in taught, \
        "test setup: could not teach the fake GitHub how its rules decide a merge"
    return taught


class Approval:
    """Builds test_automerge's machines with this file's fake GitHub, #60 waiting on an approval to merge."""

    def __init__(self, gh, behind=False):
        self.gh, self.behind = gh, behind

    def __enter__(self):
        self.saved = ta.fake_gh, ta.pr_state
        plain, behind = ta.pr_state, self.behind

        def state(issue, checks, files=None, refuse="", moves=False):
            st = plain(issue, checks, files, refuse, moves)
            st["accepts"] = "approval"
            st["behind"] = behind
            return st
        ta.fake_gh, ta.pr_state = (lambda: fake_gh(self.gh)), state
        return self

    def __exit__(self, *exc):
        ta.fake_gh, ta.pr_state = self.saved


class RuleReview(ta.Review):
    """One code review of #60 on #57 on autopilot, under the rules the test gives.

    `gh` is {"bypass": bool, "refuse_plain": bool, "variable": {} unset or {"value": "..."}}; `behind` makes #60's
    branch miss main's newest commit."""

    def __init__(self, tmp, review, checks, gh, behind=False):
        with Approval(gh, behind):
            super().__init__(tmp, review, ta.ON, checks)

    def variable_reads(self):
        """Every read of a repo variable asked of GitHub, as its arguments."""
        path = f"{self.tmp}/gh/variables.jsonl"
        return [json.loads(l) for l in open(path)] if os.path.exists(path) else []

    def lines(self):
        """Every comment on #57 since the test began that starts `Autopilot:`."""
        return [b.strip() for b in self.new_comments("issue", 57) if b.strip().startswith("Autopilot:")]

    def said(self):
        """What the owner reads of every new comment on #57 and #60."""
        return [ta.visible(b) for b in self.new_comments("issue", 57) + self.new_comments("pr", PR)]


RUNS = {}
# name: (#60's checks, GitHub's rules and the repo variable, whether #60's branch misses main's newest commit)
CASES = {
    "variable-on-held": (ta.GREEN, {"bypass": False, "variable": {"value": "on"}}, False),
    "variable-off-bypass": (ta.GREEN, {"bypass": True, "variable": {"value": "off"}}, False),
    "bypass": (ta.GREEN, {"bypass": True}, False),
    "bypass-red": (ta.RED, {"bypass": True}, False),
    "bypass-behind": (ta.GREEN, {"bypass": True}, True),
    "held": (ta.GREEN, {"bypass": False}, False),
    "held-refused": (ta.GREEN, {"bypass": False, "refuse_plain": True}, False),
}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Each code review run, run once on first use and shared between tests."""
    def get(name):
        if name not in RUNS:
            checks, gh, behind = CASES[name]
            RUNS[name] = RuleReview(tmp_path_factory.mktemp(name), ta.PR_APPROVE, checks, gh, behind)
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
    assert m.merged() == ta.HEAD, (f"{crit} ({case}): GitHub lets Dokima's app merge without approval, yet #60 did not "
                                   f"merge at its green head (merged: {m.merged()}, merges tried: {tried(m)})\n{m.tail()}")
    assert all(t["token"] == "fake-token" for t in m.tried()), \
        f"{crit} ({case}): a merge was asked with a key other than Dokima's app key: {[t['token'] for t in m.tried()]}"
    assert m.lines() == [MERGED], f"{crit} ({case}): #57 did not get exactly one line {MERGED!r}: {m.lines()}"


def waits(m, crit, case):
    """#60 is still open and #57 got exactly the line saying it waits."""
    assert m.merged() is None, (f"{crit} ({case}): #60 merged though GitHub requires the owner's approval "
                                f"(merges tried: {tried(m)})")
    assert m.lines() == [WAITS], (f"{crit} ({case}): #57 did not get exactly one line reading {WAITS!r}: "
                                  f"{m.lines()}\n{m.tail()}")


def not_merged(m, crit, case, why):
    """#60 is still open and nothing claims it merged."""
    assert m.merged() is None, f"{crit} ({case}): #60 merged though {why} (merges tried: {tried(m)})"
    assert not any(l.startswith("Autopilot: merged") for l in m.lines()), f"{crit} ({case}): #57 says #60 merged: {m.lines()}"


def owner_told(m, crit, case, *words):
    """A comment on #57 or #60 mentions the owner and holds every word given."""
    assert any(f"@{OWNER}" in s and all(w in s for w in words) for s in m.said()), \
        (f"{crit} ({case}): no comment on #57 or #60 mentions @{OWNER} and says {words}: "
         f"{[s[-400:] for s in m.said()]}\n{m.tail()}")


BEHIND_WORDS = re.compile(r"behind|newest commit|latest commit|out of date|up to date", re.I)


def plain(s):
    """A comment as words the owner reads: no HTML tags, links or addresses.

    Every record's icons are links under `/main/`, so `main` counts only in the words left after this."""
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"\]\([^)]*\)", "] ", s)
    return re.sub(r"https?://\S+", " ", s)


def says_behind(s):
    """The comment mentions the owner and its words say the branch misses main's newest commit."""
    t = plain(s)
    return f"@{OWNER}" in t and re.search(r"\bmain\b", t) is not None and BEHIND_WORDS.search(t) is not None


def told_behind(m, crit, case):
    """A comment mentioning the owner says, in words, that #60 misses main's newest commit."""
    assert any(says_behind(s) for s in m.said()), \
        (f"{crit} ({case}): no comment on #57 or #60 mentions @{OWNER} and says its branch misses main's newest "
         f"commit (words such as 'behind main' or 'main's newest commit', outside links): "
         f"{[plain(s)[-400:] for s in m.said()]}\n{m.tail()}")


def test_autopilots_merge_reads_no_repo_variable(record_property, runs):
    """Setting or clearing a repo variable changes nothing: GitHub alone decides whether autopilot merges.

    Proves 587.1.
    Runs the code review approving #60 on autopilot, every check green, twice. Once with the old switch
    `DOKIMA_AUTO_MERGE` set to `on` while GitHub requires the owner's approval: #60 must stay open and #57 must get
    exactly the line `Autopilot: PR #60 waits for your approval before it merges`. Once with it set to `off` while
    GitHub lets Dokima's app merge without approval: #60 must merge and #57 must get `Autopilot: merged PR #60`. In
    neither run may Dokima ask GitHub for any repo variable."""
    record_property("proves", "587.1")
    held = runs("variable-on-held")
    started(held, "587.1", "variable on, GitHub requires approval")
    waits(held, "587.1", "variable on, GitHub requires approval")
    free = runs("variable-off-bypass")
    started(free, "587.1", "variable off, GitHub lets the app merge")
    merged_alone(free, "587.1", "variable off, GitHub lets the app merge")
    for case, m in (("variable on", held), ("variable off", free)):
        assert m.variable_reads() == [], f"587.1 ({case}): autopilot's merge read a repo variable: {m.variable_reads()}"


def test_when_github_lets_the_app_merge_autopilot_merges_and_says_so(record_property, runs):
    """When GitHub lets Dokima's app merge without approval, autopilot merges and says so.

    Proves 587.2.
    Runs the code review approving #60 on autopilot, every check green, its branch holding main's newest commit, with
    no repo variable set, while main's rules need an approval and let Dokima's app bypass them for pull requests. #60
    must merge at its green head with the app's key, and #57 must get exactly one line `Autopilot: merged PR #60`.
    GitHub refuses the bot's approval of its own pull request, so the merge must come from GitHub's bypass. The fake
    lets the bypass merge anything, so each case below proves Dokima still checks it itself. #60 must stay open, with
    no merged line, when a check on its head is red (a comment mentioning the owner names the red check), and when its
    branch misses main's newest commit (a comment mentioning the owner says so in words, not in a link, and the
    red-check case's comments do not)."""
    record_property("proves", "587.2")
    m = runs("bypass")
    started(m, "587.2", "bypass")
    merged_alone(m, "587.2", "bypass")
    red = runs("bypass-red")
    started(red, "587.2", "bypass, red check")
    not_merged(red, "587.2", "bypass, red check", f"the check {ta.RED_NAME} failed on its head")
    owner_told(red, "587.2", "bypass, red check", ta.RED_NAME)
    behind = runs("bypass-behind")
    started(behind, "587.2", "bypass, behind main")
    not_merged(behind, "587.2", "bypass, behind main", "its branch does not contain main's newest commit")
    told_behind(behind, "587.2", "bypass, behind main")
    assert not any(says_behind(s) for s in red.said()), \
        (f"587.2 (bypass, red check): a comment on a branch that holds main's newest commit says it is behind main, so "
         f"saying so proves nothing: {[plain(s)[-400:] for s in red.said()]}")


def test_when_github_requires_approval_the_pull_request_waits_and_the_issue_says_so(record_property, runs):
    """When GitHub requires your approval, the pull request waits and the issue says so.

    Proves 587.3.
    Runs the code review approving #60 on autopilot, every check green, with no repo variable set, while main's rules
    need the owner's approval and Dokima's app is on no exemption list. Two ways GitHub holds it: it turns on
    auto-merge waiting on the approval, and it refuses the merge outright for the missing approval. Each time #60
    must stay open and #57 must get exactly one line `Autopilot: PR #60 waits for your approval before it merges`:
    a merge held for approval is a wait, not a failure."""
    record_property("proves", "587.3")
    for case in ("held", "held-refused"):
        m = runs(case)
        started(m, "587.3", case)
        assert m.tried(), f"587.3 ({case}): autopilot never asked GitHub to merge #60, so GitHub never decided:\n{m.tail()}"
        waits(m, "587.3", case)

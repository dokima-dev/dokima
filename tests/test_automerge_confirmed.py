"""Autopilot says it merged a pull request only once GitHub reports it merged (#412).

With a merge queue, or branch protection that waits on the owner's approval, `gh pr merge --squash` only puts the pull
request in the queue, or turns on auto-merge, and exits 0 with nothing merged. Autopilot used to post
`Autopilot: merged PR #N` on that exit code alone, so the issue said merged while its card said Needs you.

These tests run the code review (agent.yml) and `/autopilot start` (commands.yml) the way test_automerge.py does, on its
fake GitHub, taught three more ways a merge can go. A pull request in prs.json may carry "accepts":
  - "queue": `gh pr merge` with a method exits 0 saying the pull request was added to the merge queue; it stays open,
    and GitHub then reports isInMergeQueue true, autoMergeRequest set and reviewDecision APPROVED (GitHub's API),
    and auto_merge set with merged false (`gh api repos/o/r/pulls/N`);
  - "approval": `gh pr merge` exits 0 saying it will be merged when all requirements are met; it stays open, out of the
    queue, with autoMergeRequest set and reviewDecision REVIEW_REQUIRED;
  - "silent": `gh pr merge` exits 0 and nothing changes: open, out of the queue, no auto-merge, no review required.
Asked through `gh api -X PUT repos/o/r/pulls/N/merge`, such a pull request is refused as GitHub refuses it (405). With
"unreadable" set too, once a merge was asked GitHub fails every read of that pull request (`gh pr view`,
`gh api repos/o/r/pulls/N`, `gh pr list`) with "HTTP 502: Bad Gateway". A pull request without "accepts" merges as in
test_automerge.py, and GitHub then reports it MERGED.

The issue card and the board work the river's state out again from the issue's history (dokima.card.status and
dokima.agent.waits_on_owner); those are run directly on a conversation as test_card_status.py builds it.
"""
import json
import re

import pytest

import test_automerge as ta
import test_card_status as tcs
from dokima import agent, card
from test_start import OWNER, PR

QUEUED = "Autopilot: PR #{pr} joined the merge queue"
WAITS = "Autopilot: PR #{pr} waits for your approval before it merges"
MERGED = "Autopilot: merged PR #{pr}"
BAD_GATEWAY = "HTTP 502: Bad Gateway"
PLAIN_FAKE = ta.fake_gh

ACCEPTS_GH = r'''
def accepted(n, how, pinned):
    """A merge GitHub takes without merging: queued, auto-merge waiting on approval, or nothing at all; exits 0."""
    p = PRS[n]
    mode = p.get("accepts")
    if p.get("unreadable") and token == "fake-token":
        p["asked"] = True
        save_prs()
    if not mode or token != "fake-token" or (pinned and pinned != p["head"]) or p.get("merged"):
        return
    p["asked"] = True
    p["queued"] = mode == "queue"
    p["auto"] = mode in ("queue", "approval")
    save_prs()
    merge_log(n, how, pinned, "accepted: " + mode)
    print({"queue": f"Pull request o/r#{n} will be added to the merge queue for main when ready",
           "approval": f"Pull request o/r#{n} will be automatically merged when all requirements are met",
           "silent": ""}[mode])
    sys.exit(0)
_pr_obj, _rest_pr = pr_obj, rest_pr
def pr_obj(n):
    o, p = _pr_obj(n), PRS[n]
    o.update({"isInMergeQueue": bool(p.get("queued")), "autoMergeRequest": {"mergeMethod": "SQUASH"} if p.get("auto") else None,
              "reviewDecision": {"queue": "APPROVED", "approval": "REVIEW_REQUIRED"}.get(p.get("accepts"), ""),
              "mergeStateStatus": "BLOCKED" if p.get("accepts") else "CLEAN",
              "mergedAt": "2026-10-10T10:00:00Z" if p.get("merged") else None})
    return o
def rest_pr(n):
    o, p = _rest_pr(n), PRS[n]
    o.update({"auto_merge": {"merge_method": "squash"} if p.get("auto") else None,
              "merged_at": "2026-10-10T10:00:00Z" if p.get("merged") else None})
    return o
_m_one = re.fullmatch(r"repos/o/r/pulls/(\d+)", PAPI or "")
_read = pr_sel() if a[:2] == ["pr", "view"] else _m_one.group(1) if _m_one and not flag("-X", "--method") else None
if a[:2] == ["pr", "list"]:
    _read = pr_by_branch(flag("--head", "-H") or "")
if _read in PRS and PRS[_read].get("unreadable") and PRS[_read].get("asked"):
    sys.stderr.write("HTTP 502: Bad Gateway\n")
    sys.exit(1)
_m_put = re.fullmatch(r"repos/o/r/pulls/(\d+)/merge", PAPI or "")
if _m_put and _m_put.group(1) in PRS and PRS[_m_put.group(1)].get("accepts"):
    sys.stderr.write({"queue": "HTTP 405: Changes must be made through the merge queue",
                      "approval": "HTTP 405: At least 1 approving review is required by reviewers with write access"}
                     .get(PRS[_m_put.group(1)]["accepts"], "HTTP 405: Pull Request is not mergeable") + "\n")
    sys.exit(1)
'''


def fake_gh():
    """test_automerge.py's fake GitHub, taught merges that GitHub takes without merging, and reads that fail."""
    base = PLAIN_FAKE()
    anchor = 'if a[:2] == ["pr", "list"]:'
    fake = base.replace(anchor, ACCEPTS_GH + anchor, 1)
    hook = '    why = merge(n, how, flag("--match-head-commit"), admin="--admin" in a)\n'
    fake = fake.replace(hook, '    accepted(n, how, flag("--match-head-commit"))\n' + hook, 1)
    assert fake.count("    accepted(n, how, flag(") == 1 and ACCEPTS_GH in fake, \
        "test setup: could not teach the fake GitHub merges that only queue or wait"
    return fake


def pr_with(issue, accepts=None, unreadable=False):
    """A pull request for `issue`, every check green, taking merges as `accepts` says."""
    st = ta.pr_state(issue, ta.GREEN)
    if accepts:
        st["accepts"] = accepts
    if unreadable:
        st["unreadable"] = True
    return st


class Taught:
    """Builds test_automerge's machines with this file's fake GitHub and pull request state."""

    def __init__(self, accepts=None, unreadable=False):
        self.accepts, self.unreadable = accepts, unreadable

    def __enter__(self):
        self.saved = ta.fake_gh, ta.pr_state
        plain = ta.pr_state

        def state(issue, checks, files=None, refuse="", moves=False):
            st = plain(issue, checks, files, refuse, moves)
            if self.accepts:
                st["accepts"] = self.accepts
            if self.unreadable:
                st["unreadable"] = True
            return st
        ta.fake_gh, ta.pr_state = fake_gh, state
        return self

    def __exit__(self, *exc):
        ta.fake_gh, ta.pr_state = self.saved


RUNS = {}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Each workflow run, run once on first use and shared between tests."""
    def get(name):
        if name not in RUNS:
            tmp = tmp_path_factory.mktemp(name)
            kind, accepts, unreadable = {
                "review-merged": ("review", None, False), "review-queue": ("review", "queue", False),
                "review-approval": ("review", "approval", False), "review-silent": ("review", "silent", False),
                "review-unreadable": ("review", None, True), "command-queue": ("command", "queue", False),
                "command-approval": ("command", "approval", False)}[name]
            with Taught(accepts, unreadable):
                if kind == "review":
                    m = ta.Review(tmp, ta.PR_APPROVE, ta.ON, ta.GREEN)
                else:
                    m = ta.Command(tmp, {60: pr_with(57, accepts, unreadable)}, {57: "approve"})
                    m.listen("/autopilot start")
            RUNS[name] = m
        return RUNS[name]
    return get


def autopilot_lines(m, issue=57):
    """Every comment on the issue since the test began that starts `Autopilot:`."""
    return [b.strip() for b in m.new_comments("issue", issue) if b.strip().startswith("Autopilot:")]


def started(m, crit, case):
    """Fails naming the criterion when the code review never ran, so the test proves nothing."""
    if isinstance(m, ta.Review):
        assert m.agent_started(), f"{crit} ({case}): test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"
    assert m.tried(PR), f"{crit} ({case}): test setup: autopilot never asked GitHub to merge #60, so this proves nothing:\n{m.tail()}"


def no_merged_claim(m, crit, case):
    """Nothing on the issue, the pull request or the review's card says #60 merged.

    When GitHub fails every read after the merge, #60 may really have merged, but nothing could confirm it."""
    if case != "review-unreadable":
        assert m.merged() is None, f"{crit} ({case}): test setup: #60 really merged at {m.merged()}"
    claims = [b for b in m.new_comments("issue", 57) + m.new_comments("pr", PR)
              if re.search(r"merged PR #60", ta.visible(b), re.I)]
    assert not claims, (f"{crit} ({case}): GitHub never reported #60 merged, yet a comment says it merged: "
                        f"{[c[-300:] for c in claims]}")


def test_the_merged_line_is_posted_only_once_github_reports_the_pull_request_merged(record_property, runs):
    """`Autopilot: merged PR #60` appears only once GitHub reports the PR merged.

    Proves 412.1.
    Runs the code review approving #60 on autopilot, every check green, four ways where `gh pr merge` exits 0 and
    nothing merges (added to the merge queue, auto-merge waiting on the owner's approval, nothing at all, and GitHub
    failing to say afterwards), and `/autopilot start` on the same where it only queues or waits. None may post
    `Autopilot: merged PR #60` on #57 or say #60 merged anywhere, and the review's card may not end on a Next line saying
    it merged, nor put the card in Done. Beside them, a merge GitHub reports MERGED still posts the line exactly once."""
    record_property("proves", "412.1")
    for name in ("review-queue", "review-approval", "review-silent", "review-unreadable", "command-queue", "command-approval"):
        m = runs(name)
        started(m, "412.1", name)
        no_merged_claim(m, "412.1", name)
        if name.startswith("review"):
            nxt = m.next_line()
            assert not re.search(r"merged PR #60|Autopilot merged", nxt, re.I), f"412.1 ({name}): the review's card says it merged though nothing did: {nxt!r}"
            assert not m.board().startswith("Done"), f"412.1 ({name}): the card went to Done though nothing merged: {m.board()!r}"
    m = runs("review-merged")
    started(m, "412.1", "merged")
    assert m.merged() == ta.HEAD, f"412.1 (merged): test setup: #60 did not merge:\n{m.tail()}"
    assert autopilot_lines(m) == [MERGED.format(pr=PR)], \
        f"412.1 (merged): GitHub reports #60 merged, but #57 did not get exactly one '{MERGED.format(pr=PR)}': {autopilot_lines(m)}"


def test_a_merge_that_only_queued_says_so_in_one_line_and_the_card_agrees(record_property, runs):
    """A queued merge says so in one line, and no card asks you anything.

    Proves 412.2.
    By the code review and by `/autopilot start`, a merge GitHub only queues must post exactly one Autopilot comment on
    #57, the single line `Autopilot: PR #60 joined the merge queue` (the wording #378 settled). The review's
    card must end on a Next line naming the merge queue without mentioning the owner, and leave the board card in Review
    with no Needs you. Read back from the issue's history with that line after the approving review, the issue card and
    the board must show Review with nothing for the owner; without the line, both still show Needs you."""
    record_property("proves", "412.2")
    want = QUEUED.format(pr=PR)
    for name in ("review-queue", "command-queue"):
        m = runs(name)
        started(m, "412.2", name)
        assert autopilot_lines(m) == [want], \
            f"412.2 ({name}): #57 did not get exactly one Autopilot line reading {want!r}: {autopilot_lines(m)}\n{m.tail()}"
    m = runs("review-queue")
    nxt = m.next_line()
    assert "merge queue" in nxt.lower() and f"@{OWNER}" not in nxt, \
        f"412.2: the review's card does not end on a Next line naming the merge queue without mentioning the owner: {nxt!r}"
    assert m.board() == "Review none", f"412.2: a queued pull request's card is not in Review without Needs you: {m.board()!r}"
    approved = (tcs.PLANNED, tcs.PLAN_OK, "/work", tcs.BUILT, tcs.CODE_OK)
    items = tcs.said(*approved) + [tcs.comment(tcs.BOT, QUEUED.format(pr=tcs.PR["number"]), 9)]
    found = dict(tcs.found_for(approved, pr=tcs.PR, check_runs=tcs.GREEN), items=items, recs=agent.records(items))
    assert card.status(tcs.ISSUE, found) == ("Review", None), \
        f"412.2: the issue card still asks the owner for something while the PR is in the merge queue: {card.status(tcs.ISSUE, found)}"
    assert agent.waits_on_owner(items, {tcs.OWNER}, lambda: True, "", "40") is False, \
        "412.2: the board still shows Needs you while the PR is in the merge queue"
    plain = tcs.found_for(approved, pr=tcs.PR, check_runs=tcs.GREEN)
    assert card.status(tcs.ISSUE, plain)[1] == card.TODO["ready"], \
        f"412.2: without the queue line the issue card no longer says Ready for approval: {card.status(tcs.ISSUE, plain)}"
    assert agent.waits_on_owner(tcs.said(*approved), {tcs.OWNER}, lambda: True, "", "40") is True, \
        "412.2: without the queue line the board no longer shows Needs you for approved work"


def test_a_merge_waiting_on_your_approval_says_so_in_one_line_and_the_card_agrees(record_property, runs):
    """A merge awaiting your approval says so in one line; the card says Needs you.

    Proves 412.3.
    By the code review and by `/autopilot start`, a merge GitHub only turns into auto-merge waiting on a required review
    must post exactly one Autopilot comment on #57, the single line `Autopilot: PR #60 waits for your approval before it
    merges`. The review's card must end on a Next line that mentions the owner and asks for their approval, and leave
    the board card in Review with Needs you. Read back from the issue's history with that line after the approving
    review, the issue card must say Needs you: Ready for approval, and the board Needs you."""
    record_property("proves", "412.3")
    want = WAITS.format(pr=PR)
    for name in ("review-approval", "command-approval"):
        m = runs(name)
        started(m, "412.3", name)
        assert autopilot_lines(m) == [want], \
            f"412.3 ({name}): #57 did not get exactly one Autopilot line reading {want!r}: {autopilot_lines(m)}\n{m.tail()}"
    m = runs("review-approval")
    nxt = m.next_line()
    assert f"@{OWNER}" in nxt and "approv" in nxt.lower() and "merge queue" not in nxt.lower(), \
        f"412.3: the review's card does not end on a Next line asking the owner for their approval: {nxt!r}"
    assert m.board() == "Review needs", f"412.3: a pull request waiting on the owner's approval is not Review with Needs you: {m.board()!r}"
    approved = (tcs.PLANNED, tcs.PLAN_OK, "/work", tcs.BUILT, tcs.CODE_OK)
    items = tcs.said(*approved) + [tcs.comment(tcs.BOT, WAITS.format(pr=tcs.PR["number"]), 9)]
    found = dict(tcs.found_for(approved, pr=tcs.PR, check_runs=tcs.GREEN), items=items, recs=agent.records(items))
    assert card.status(tcs.ISSUE, found) == ("Review", card.TODO["ready"]), \
        f"412.3: the issue card does not say Needs you: Ready for approval while the PR waits on you: {card.status(tcs.ISSUE, found)}"
    assert agent.waits_on_owner(items, {tcs.OWNER}, lambda: True, "", "40") is True, \
        "412.3: the board does not show Needs you while the PR waits on the owner's approval"


def test_a_merge_github_cannot_confirm_stops_for_you_and_says_why_on_the_pull_request(record_property, runs):
    """A merge GitHub cannot confirm stops for you and says why on the PR.

    Proves 412.4.
    Runs the code review approving #60 on autopilot two ways: `gh pr merge` exits 0 and nothing changes at all, and it
    merges but GitHub then fails every read of #60 with HTTP 502. Each must post no Autopilot line on #57, write on #60
    a comment that mentions the owner (with HTTP 502 in it when GitHub failed to answer), end the review's card on a
    Next line mentioning the owner, and show Needs you."""
    record_property("proves", "412.4")
    for name, reason in (("review-silent", ""), ("review-unreadable", BAD_GATEWAY)):
        m = runs(name)
        started(m, "412.4", name)
        assert autopilot_lines(m) == [], f"412.4 ({name}): an Autopilot line was posted though GitHub never confirmed anything: {autopilot_lines(m)}"
        on_pr = [ta.visible(b) for b in m.new_comments("pr", PR)]
        assert any(f"@{OWNER}" in b and reason in b and "did not merge" in b.lower() or
                   f"@{OWNER}" in b and reason in b and "could not" in b.lower() for b in on_pr), \
            (f"412.4 ({name}): no comment on #60 mentions @{OWNER} and says why (wanted {reason or 'any reason'!r}): "
             f"{[b[-400:] for b in on_pr]}\n{m.tail()}")
        assert f"@{OWNER}" in m.next_line(), f"412.4 ({name}): the review's card does not end on a Next line for the owner: {m.next_line()!r}"
        assert m.board().endswith("needs"), f"412.4 ({name}): the card does not show Needs you: {m.board()!r}"

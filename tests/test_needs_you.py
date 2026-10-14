"""Needs you shows only while the river waits on the owner; Autopilot otherwise (#297).

Before this, the board put Needs you where nothing waited on the owner: every time the criteria checks finished on a
pull request (even one already merged), on closed issues a run stopped on after the owner had merged, and on parent
issues left with the pill from before their split was filed. A Needs you the river did set was wiped by the next new
commit, yet stayed for the whole run after the owner answered with a command. Nothing ever cleared old wrong pills.

Most tests fake dokima.board.Board and agent's `gh` against one in-memory world, so they read the board's end state:
each card's Status and Action ("Needs you", "Autopilot" or none), each item's labels and whether it is closed, each
issue's open pull request, sub-issues and history (the bot's records and the owner's words, read through
`gh issue view`). On top of test_autopilot_board's fake Board, the board offers two more reads the code is expected
to use:

    .state(kind, n) -> "open" | "closed"    a merged pull request is closed; raises subprocess.CalledProcessError
                                             when GitHub cannot say
    .cards() -> [{"kind", "number", "action", "closed", "autopilot"}, ...]
                                             every issue and pull request on the board: its Action ("Needs you",
                                             "Autopilot" or None), whether it is closed (merged counts) and whether
                                             it carries the autopilot label

Whether an item is closed may also be read through `gh` (`gh api repos/o/r/issues/N`, `gh issue view N --json state`,
`gh pr view N --json state`); the fake answers all of them alike, and fails alike for an item GitHub cannot read. A
pull request's issue is read from its branch (try/issue-N) or its "Closes #N". An item waits on the owner when the
river's last word on its issue stopped for the owner and no code owner has answered with a command since.
Code owners are the people CODEOWNERS names (dokima.plan.repo_approvers). Since #331 the pills follow the issue's
history, so each world holds the records and words behind them: a comment lands in the history before its event
reaches the board, a run's end is `agent board N OUT`, and a closed item shows no pill at all. The last two tests run
the real Board's new reads against a faked GitHub.
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import test_autopilot_board as tab  # noqa: E402
from dokima import agent, board, card, plan  # noqa: E402
from dokima import agent_github  # noqa: E402
from test_agent import GOOD_REVIEW, GOOD_WORK, SPLIT, rec  # noqa: E402

LABEL = "autopilot"
SPEC, REPO = "o/1", "o/r"
OWNER = sorted(plan.repo_approvers("o"))[0]
NEEDS, AUTO = "Needs you", "Autopilot"


def split_filed(stories=(201, 202)):
    """The Split filed record code posts on a parent once its stories are filed."""
    return {"role": "split", "stage": None, "check": {"passed": True, "problems": []},
            "handback": {"stories": [{"story": i, "issue": n, "title": f"Story {i}", "id": f"I_{n}", "blocked_by": []}
                                     for i, n in enumerate(stories, 1)]}}


def split_planned():
    """A parent's records up to an approved split not filed yet, waiting for `/work`."""
    return [rec("planner", handback=SPLIT), rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})]


def plan_approved():
    """Records up to an approved plan, so the river waits for `/work` off autopilot."""
    return [rec("planner", handback={"kind": "user_story"}), rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})]


def plan_blocked():
    """Records up to a plan review's first block, which goes back to the planner."""
    return [rec("planner", handback={"kind": "user_story"}), rec("reviewer", "plan", GOOD_REVIEW)]


def code_approved():
    """Records up to an approving code review, so the pull request waits to be merged."""
    return plan_approved() + ["/work", rec("worker", handback=GOOD_WORK),
                              rec("reviewer", "pr", {**GOOD_REVIEW, "stage": "pr", "verdict": "approve", "blockers": []})]


def escalated(stage="pr"):
    """Records ending in a reviewer's escalation, which stops for the owner even on autopilot."""
    return [rec("planner", handback={"kind": "user_story"}), rec("reviewer", stage, {**GOOD_REVIEW, "stage": stage, "verdict": "escalate"})]


class World(tab.World):
    """test_autopilot_board's world, plus which items are closed, which GitHub cannot read, sub-issues, records and
    the code owner's pull request reviews."""

    def __init__(self, closed=(), unreadable=(), subs=None, records=None, reviews=None, **kw):
        super().__init__(**kw)
        self.reviews = {k: list(v) for k, v in (reviews or {}).items()}  # pr -> [(state, summary[, login])], the code owner's by default
        self.closed = set(closed)  # (kind, n)
        self.unreadable = set(unreadable)  # numbers whose state GitHub will not give
        self.subs = {k: list(v) for k, v in (subs or {}).items()}
        self.records = {k: list(v) for k, v in (records or {}).items()}

    def is_closed(self, n):
        return ("issue", n) in self.closed or ("pr", n) in self.closed

    def refuse(self, n, args):
        if n in self.unreadable:
            raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr="HTTP 502: Bad Gateway")


def fake_board(world):
    """test_autopilot_board's fake Board, reading this world, with the two new reads."""
    base = tab.fake_board(world)

    class FakeBoard(base):
        def state(self, kind, n):
            world.refuse(int(n), ["api", f"state {kind} {n}"])
            return "closed" if (kind, int(n)) in world.closed else "open"

        def cards(self):
            return [{"kind": k, "number": n, "action": c.get("Action"), "closed": (k, n) in world.closed,
                     "autopilot": world.has(k, n)} for (k, n), c in sorted(world.cards.items())]

        def view_nodes(self):
            return []

        def set_view_filter(self, view_id, filter):
            pass

    return FakeBoard


def fake_gh(world):
    """agent.gh, answering from the world: pull requests, states, labels, sub-issues and records."""

    def gh(*args):
        world.calls.append(args)
        a = [str(x) for x in args]
        if a[:2] == ["pr", "list"]:
            head = a[a.index("--head") + 1]
            n = int(head.rsplit("-", 1)[1])
            pr = world.prs.get(n) if head.startswith("try/") else None
            want_open = "--state" not in a or a[a.index("--state") + 1] == "open"
            found = [pr] if pr and (not want_open or ("pr", pr) not in world.closed) else []
            if "-q" in a or "--jq" in a:
                return f"{found[0]}\n" if found else "\n"
            return json.dumps([{"number": p} for p in found])
        if a[:2] == ["issue", "view"]:
            n = int(a[2])
            world.refuse(n, a)
            steps = world.records.get(n, [])
            # A (login, words) pair is a comment by that person; a plain string is the code owner's words.
            items = [{"author": {"login": st[0]}, "body": st[1]} if isinstance(st, tuple) else card.as_items([st], OWNER)[0]
                     for st in steps]
            comments = [{**c, "createdAt": f"2026-10-09T00:00:{i:02d}Z"} for i, c in enumerate(items)]
            return json.dumps({"number": n, "title": f"Issue {n}", "body": "", "comments": comments,
                               "state": "CLOSED" if ("issue", n) in world.closed else "OPEN",
                               "labels": [{"name": x} for x in sorted(world.labels.get(("issue", n), set()))]})
        if a[:2] == ["pr", "view"]:
            n = int(a[2])
            world.refuse(n, a)
            issue = next((i for i, p in world.prs.items() if p == n), None)
            return json.dumps({"number": n, "state": "CLOSED" if ("pr", n) in world.closed else "OPEN",
                               "headRefName": f"try/issue-{issue}" if issue else f"feature-{n}",
                               "body": f"Closes #{issue}" if issue else "", "comments": [],
                               "reviews": [{"author": {"login": (r[2] if len(r) > 2 else OWNER)}, "body": r[1], "state": r[0],
                                            "submittedAt": f"2026-10-09T01:00:{i:02d}Z"}
                                           for i, r in enumerate(world.reviews.get(n, []))],
                               "labels": [{"name": x} for x in sorted(world.labels.get(("pr", n), set()))]})
        if a[:1] == ["api"]:
            path = next((x for x in a[1:] if x.lstrip("/").startswith("repos/")), "").lstrip("/")
            method = a[a.index("-X") + 1].upper() if "-X" in a else ("POST" if any(x in ("-f", "-F") for x in a) else "GET")
            m = re.fullmatch(r"repos/o/r/(?:issues|pulls)/(\d+)(/.*)?", path.split("?")[0])
            if m:
                n, rest = int(m.group(1)), m.group(2) or ""
                kind = "pr" if ("pr", n) in world.cards or n in world.prs.values() else "issue"
                if rest == "/sub_issues":
                    return json.dumps([{"number": c, "state": "closed" if world.is_closed(c) else "open"}
                                       for c in world.subs.get(n, [])])
                if rest.startswith("/labels"):
                    if method == "DELETE":
                        world.put(kind, n, False)
                    elif LABEL in " ".join(a):
                        world.put(kind, n, True)
                    return "[]"
                if rest == "/comments":
                    return "[]"
                if rest == "" and method == "GET":
                    world.refuse(n, a)
                    issue = next((i for i, p in world.prs.items() if p == n), None)
                    head = {"head": {"ref": f"try/issue-{issue}"}, "body": f"Closes #{issue}"} if kind == "pr" and issue else {}
                    return json.dumps({**head, "id": 9000 + n, "number": n, "state": "closed" if world.is_closed(n) else "open",
                                       "merged": ("pr", n) in world.closed,
                                       "labels": [{"name": x} for x in sorted(world.labels.get((kind, n), set()))]})
            return "{}"
        return ""

    return gh


@pytest.fixture
def make(monkeypatch):
    """Wire a world into dokima.board.Board and dokima.agent.gh, and return it."""

    def wire(**kw):
        world = World(**kw)
        monkeypatch.setattr(board, "Board", fake_board(world))
        monkeypatch.setattr(agent_github, "gh", fake_gh(world))
        return world

    return wire


def comment(n, body, login=OWNER, kind="User", pr_body=None, labels=(), state="open"):
    """An issue_comment payload on issue n, or on pull request n when pr_body is given."""
    issue = {"number": n, "labels": [{"name": x} for x in labels], "state": state, "body": pr_body or ""}
    if pr_body is not None:
        issue["pull_request"] = {"url": f"https://api.github.com/repos/o/r/pulls/{n}"}
    return {"action": "created", "issue": issue, "comment": {"user": {"login": login, "type": kind}, "body": body}}


def pr_event(action, number, issue, merged=False):
    """A pull_request_target payload for pull request `number`, built for `issue`."""
    return {"action": action, "pull_request": {"number": number, "body": f"Closes #{issue}", "merged": merged,
                                               "head": {"ref": f"try/issue-{issue}"}, "labels": []}}


def checks_done(*prs):
    """The criteria checks finished on these pull requests."""
    return {"action": "completed", "workflow_run": {"pull_requests": [{"number": n} for n in prs]}}


def review(n, body, state="commented", login=OWNER, kind="User", issue=None):
    """A pull_request_review payload for pull request n, built for `issue`, with this summary."""
    return {"action": "submitted", "review": {"state": state, "body": body, "user": {"login": login, "type": kind}},
            "pull_request": {"number": n, "body": f"Closes #{issue}" if issue else "",
                             "head": {"ref": f"try/issue-{issue}" if issue else f"feature-{n}"}, "labels": []}}


def run_ends(n, monkeypatch, tmp_path):
    """Run `agent board N OUT` on issue n, for a run that decided what follows.

    The run's own board.txt says Backlog with no pill, which must not count: since #331 a run that decided is placed
    from GitHub's state, and only a run that failed is placed by itself (#132)."""
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    (tmp_path / "board.txt").write_text("Backlog none\n")
    return agent.main(["agent", "board", str(n), str(tmp_path)])


def said(w, n, words, login=OWNER):
    """Someone's comment lands in issue n's history before its event reaches the board."""
    w.records.setdefault(n, []).append(words if login == OWNER else (login, words))


def pills(w, *items):
    """Each item's pill, keyed "issue #N" or "pr #N"."""
    return {f"{k} #{n}": w.action(k, n) for k, n in items}


# 297.1: Needs you appears only where the river stops for the owner, and stays until it is answered

def test_a_check_finishing_never_marks_a_pull_request_for_the_owner(record_property, make):
    """Finished checks never put Needs you on a pull request.

    Proves 297.1. The criteria checks finish on PR #60 (for #57 on autopilot, whose plan review sent it back to the
    planner by itself), PR #61 (for #58, nothing waits) and PR #62 (for #59, whose approving code review waits for the
    owner to merge, showing Needs you). Afterwards #60 shows Autopilot, #61 nothing and #62 still Needs you."""
    record_property("proves", "297.1")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60, 58: 61, 59: 62},
             records={57: plan_blocked(), 59: code_approved()},
             cards={("pr", 60): {"Status": "Review", "Action": AUTO}, ("pr", 61): {"Status": "Review"},
                    ("pr", 62): {"Status": "Review", "Action": NEEDS}})
    board.sync("workflow_run", checks_done(60, 61, 62), SPEC, REPO)
    got = pills(w, ("pr", 60), ("pr", 61), ("pr", 62))
    assert got == {"pr #60": AUTO, "pr #61": None, "pr #62": NEEDS}, \
        f"297.1: after the checks finished, the pull requests show {got}; a finished check must not mark one for the owner"


def test_needs_you_set_by_the_river_stays_through_new_commits_and_checks(record_property, make, monkeypatch, tmp_path):
    """A Needs you the river set stays through new commits and finished checks.

    Proves 297.1. The good case first: #59's code review approved and the run ends (`agent board`), so #59 and its open
    PR #62 show Needs you. Then a new commit reaches PR #62 (as when main is merged into it) and its checks finish:
    both cards must still show Needs you, because nothing answered it. Beside it, PR #60 for #57 on autopilot, whose
    river goes on, gets a new commit and keeps Autopilot, so a card never ends with neither."""
    record_property("proves", "297.1")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60, 59: 62},
             records={57: plan_blocked(), 59: code_approved()},
             cards={("pr", 60): {"Status": "Review", "Action": AUTO}, ("issue", 57): {"Status": "Review", "Action": AUTO}})
    run_ends(59, monkeypatch, tmp_path)
    got = pills(w, ("issue", 59), ("pr", 62))
    assert got == {"issue #59": NEEDS, "pr #62": NEEDS}, f"297.1: the river stopped for the owner on #59 but the cards show {got}"
    board.sync("pull_request_target", pr_event("synchronize", 62, 59), SPEC, REPO)
    got = pills(w, ("issue", 59), ("pr", 62))
    assert got == {"issue #59": NEEDS, "pr #62": NEEDS}, \
        f"297.1: a new commit on PR #62 took Needs you away though the owner answered nothing: {got}"
    board.sync("workflow_run", checks_done(62), SPEC, REPO)
    assert w.action("pr", 62) == NEEDS, f"297.1: finished checks took Needs you off PR #62: {w.action('pr', 62)!r}"
    board.sync("pull_request_target", pr_event("synchronize", 60, 57), SPEC, REPO)
    got = pills(w, ("issue", 57), ("pr", 60))
    assert got == {"issue #57": AUTO, "pr #60": AUTO}, f"297.1: a new commit on PR #60, on autopilot, left {got}, not Autopilot"


# 297.2: Needs you clears the moment a code owner answers with a command

def test_a_code_owners_command_clears_needs_you_at_once_and_nothing_else_does(record_property, make):
    """A code owner's command clears Needs you at once; no other comment does.

    Proves 297.2. #57 (on autopilot, with PR #60, its reviewer escalated), #58 (with PR #61, its code review approved)
    and #59 (no PR, its plan approved) all wait on the owner and show Needs you. First, comments that answer nothing,
    each landing in #57's history: someone who is not a code owner says /work, the bot says /work, and the code owner
    writes a plain comment; all five cards still show Needs you. Then the code owner says /work on #57: #57 and PR #60
    show Autopilot. The code owner says /review on PR #61 (whose description closes #58): #61 and #58 show nothing.
    The code owner says /plan with an answer on #59: #59 shows nothing."""
    record_property("proves", "297.2")
    every = (("issue", 57), ("pr", 60), ("issue", 58), ("pr", 61), ("issue", 59))
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60, 58: 61},
             records={57: escalated(), 58: code_approved(), 59: plan_approved()},
             cards={k: {"Status": "Review", "Action": NEEDS} for k in every})
    stranger = "someone-else" if OWNER != "someone-else" else "another-person"
    for body, login, kind in (("/work", stranger, "User"), ("/work", "dokima-runtime[bot]", "Bot"),
                              ("Thanks, that reads right.", OWNER, "User")):
        said(w, 57, body, login)
        board.sync("issue_comment", comment(57, body, login, kind, labels=[LABEL]), SPEC, REPO)
        got = pills(w, *every)
        assert set(got.values()) == {NEEDS}, \
            f"297.2: {login}'s comment {body!r} on #57 answered nothing, yet the pills changed to {got}"
    said(w, 57, "/work")
    board.sync("issue_comment", comment(57, "/work", labels=[LABEL]), SPEC, REPO)
    got = pills(w, ("issue", 57), ("pr", 60))
    assert got == {"issue #57": AUTO, "pr #60": AUTO}, \
        f"297.2: the code owner said /work on #57, on autopilot, and the cards show {got}, not Autopilot"
    said(w, 58, "/review")
    board.sync("issue_comment", comment(61, "/review", pr_body="Closes #58"), SPEC, REPO)
    got = pills(w, ("pr", 61), ("issue", 58))
    assert got == {"pr #61": None, "issue #58": None}, f"297.2: the code owner said /review on PR #61 and the cards show {got}"
    said(w, 59, "/plan Yes, keep the old name.")
    board.sync("issue_comment", comment(59, "/plan Yes, keep the old name."), SPEC, REPO)
    assert w.action("issue", 59) is None, f"297.2: the code owner answered with /plan on #59 and it shows {w.action('issue', 59)!r}"


def test_a_code_owners_command_in_a_review_summary_clears_needs_you_at_once(record_property, make):
    """A code owner's command in a review summary clears Needs you at once.

    Proves 297.2. #58 with PR #61 and #57 (on autopilot, its reviewer escalated) with PR #60 wait on the owner and all
    four cards show Needs you. First, reviews on PR #61 that answer nothing: someone who is not a code owner reviews
    with /work, the code owner approves with /work in the summary (an Approve only ever means merge), and the code
    owner requests changes with no command; all four cards still show Needs you. Then the code owner reviews PR #61 as
    a comment starting /review: #61 and #58 show nothing. The code owner requests changes on PR #60 starting /work:
    #60 and #57 show Autopilot."""
    record_property("proves", "297.2")
    every = (("issue", 58), ("pr", 61), ("issue", 57), ("pr", 60))
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60, 58: 61},
             records={57: escalated(), 58: code_approved()},
             cards={k: {"Status": "Review", "Action": NEEDS} for k in every})
    stranger = "someone-else" if OWNER != "someone-else" else "another-person"
    for body, state, login in (("/work", "commented", stranger), ("/work", "approved", OWNER),
                               ("Please rename the helper.", "changes_requested", OWNER)):
        w.reviews.setdefault(61, []).append((state.upper(), body, login))
        board.sync("pull_request_review", review(61, body, state, login, issue=58), SPEC, REPO)
        got = pills(w, *every)
        assert set(got.values()) == {NEEDS}, \
            f"297.2: {login}'s {state} review {body!r} on PR #61 answered nothing, yet the pills changed to {got}"
    w.reviews[61].append(("COMMENTED", "/review Look again at the parser."))
    board.sync("pull_request_review", review(61, "/review Look again at the parser.", issue=58), SPEC, REPO)
    got = pills(w, ("pr", 61), ("issue", 58))
    assert got == {"pr #61": None, "issue #58": None}, \
        f"297.2: the code owner's review summary said /review on PR #61 and the cards show {got}"
    w.reviews.setdefault(60, []).append(("CHANGES_REQUESTED", "/work Rename the helper."))
    board.sync("pull_request_review", review(60, "/work Rename the helper.", "changes_requested", issue=57), SPEC, REPO)
    got = pills(w, ("pr", 60), ("issue", 57))
    assert got == {"pr #60": AUTO, "issue #57": AUTO}, \
        f"297.2: the code owner's change request said /work on PR #60, on autopilot, and the cards show {got}, not Autopilot"


def test_the_board_runs_when_a_pull_request_review_is_submitted(record_property):
    """The board's workflow runs whenever a pull request review is submitted.

    Proves 297.2. Since #396 board.yml no longer runs on pull_request_review itself (that runs the pull request's own
    copy of board.yml with the keys): it runs, as main's copy, when a workflow that runs on pull_request_review
    submitted completes. Reads board.yml's workflow_run trigger and that workflow's triggers."""
    record_property("proves", "297.2")
    import test_review_relay as trr
    names, types = trr.run_on(open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "board.yml")).read())
    heard = [f for f, (name, text) in trr.workflows().items()
             if f != "board.yml" and name in names and "submitted" in trr.triggers(text).get("pull_request_review", set())]
    assert heard, "297.2: board.yml runs after no workflow that runs on a submitted review, so a review's command never reaches the board"
    assert "completed" in types, f"297.2: board.yml runs after {heard} only on {sorted(types)}, not when they complete"


# 297.3: Needs you clears when the item closes and never lands on a closed item

def test_needs_you_never_lands_on_a_closed_issue_or_pull_request(record_property, make, monkeypatch, tmp_path):
    """Closing clears Needs you, and nothing puts it on a closed item.

    Proves 297.3. Closing: #57 (on autopilot, its reviewer escalated) closes; merged PR #60 and its #56 (code review
    approved) lose Needs you. A closed item shows no pill at all, Autopilot included (#330). Then a run ends on #57
    after it closed (a run that ended after the owner merged) and #57 must still show nothing; it ends on closed #58,
    and #58 must show nothing; and a bot comment saying a plan is ready lands on closed #58 and must not mark it.
    Beside them, a run ends on open #59 (code review approved) and #59 and its PR #62 show Needs you. Checks that
    finish after PR #60 merged must not mark it either."""
    record_property("proves", "297.3")
    w = make(labels={("issue", 57): {LABEL}}, prs={56: 60, 59: 62},
             records={57: escalated(), 56: code_approved(), 58: code_approved(), 59: code_approved()},
             cards={("issue", 57): {"Status": "Review", "Action": NEEDS}, ("issue", 56): {"Status": "Review", "Action": NEEDS},
                    ("pr", 60): {"Status": "Review", "Action": NEEDS}, ("issue", 58): {"Status": "Done"}})
    w.closed |= {("issue", 57)}
    board.sync("issues", {"action": "closed", "issue": {"number": 57, "labels": [{"name": LABEL}], "state": "closed"}}, SPEC, REPO)
    assert w.action("issue", 57) is None, f"297.3: #57, on autopilot, closed and shows {w.action('issue', 57)!r}, not nothing"
    w.closed |= {("pr", 60), ("issue", 56)}
    board.sync("pull_request_target", pr_event("closed", 60, 56, merged=True), SPEC, REPO)
    got = pills(w, ("pr", 60), ("issue", 56))
    assert got == {"pr #60": None, "issue #56": None}, f"297.3: PR #60 merged and the cards still show {got}"
    board.sync("workflow_run", checks_done(60), SPEC, REPO)
    assert w.action("pr", 60) is None, f"297.3: checks finishing after PR #60 merged marked it {w.action('pr', 60)!r}"
    w.closed |= {("issue", 58)}
    run_ends(57, monkeypatch, tmp_path)
    assert w.action("issue", 57) is None, f"297.3: a run ended on closed #57 and it shows {w.action('issue', 57)!r}"
    run_ends(58, monkeypatch, tmp_path)
    assert w.action("issue", 58) is None, f"297.3: a run ended on closed #58 and it shows {w.action('issue', 58)!r}"
    board.sync("issue_comment", comment(58, "Plan written above, tests on `work/issue-58`.", "dokima-runtime[bot]", "Bot",
                                        state="closed"), SPEC, REPO)
    assert w.action("issue", 58) is None, f"297.3: a bot comment marked closed #58 with {w.action('issue', 58)!r}"
    run_ends(59, monkeypatch, tmp_path)
    got = pills(w, ("issue", 59), ("pr", 62))
    assert got == {"issue #59": NEEDS, "pr #62": NEEDS}, f"297.3: the river stopped on open #59 and the cards show {got}"


# 297.4: a parent shows Needs you only when the parent itself waits on the owner

def test_a_parent_shows_needs_you_only_for_its_own_stop(record_property, make, monkeypatch, tmp_path):
    """A parent shows Needs you only when its own split waits for /work.

    Proves 297.4. #139 (on autopilot) has its split filed into #201 and #202. #201's river stops for the owner (its reviewer
    escalated) and #202's pull request merges: #201 shows Needs you, #139 keeps Autopilot. #141, not on autopilot, has
    an approved split not filed yet, so its river stops for /work: #141 shows Needs you, and keeps it through another
    merge. Then a board left with old pills: #139
    (on autopilot) and #140 (not), both with filed splits, show Needs you; after the next merge #139 shows Autopilot,
    #140 nothing, and #141, still waiting for /work, keeps Needs you. Today the old pills on #139 and #140 stay."""
    record_property("proves", "297.4")
    parents = dict(labels={("issue", 139): {LABEL}, ("issue", 201): {LABEL}},
                   subs={139: [201, 202], 140: [203]}, parents={201: 139, 202: 139, 203: 140}, prs={202: 210},
                   records={139: split_planned() + [split_filed((201, 202))], 140: split_planned() + [split_filed((203,))],
                            141: split_planned(), 201: escalated("plan")})
    w = make(cards={("issue", 139): {"Status": "Work", "Action": AUTO}, ("issue", 201): {"Status": "Plan", "Action": AUTO},
                    ("issue", 141): {"Status": "Plan"}}, **parents)
    run_ends(201, monkeypatch, tmp_path)
    w.closed |= {("pr", 210), ("issue", 202)}
    board.sync("pull_request_target", pr_event("closed", 210, 202, merged=True), SPEC, REPO)
    got = pills(w, ("issue", 201), ("issue", 139))
    assert got == {"issue #201": NEEDS, "issue #139": AUTO}, f"297.4: a story stopped and another merged, and the cards show {got}"
    run_ends(141, monkeypatch, tmp_path)
    w.closed |= {("pr", 211), ("issue", 300)}
    board.sync("pull_request_target", pr_event("closed", 211, 300, merged=True), SPEC, REPO)
    assert w.action("issue", 141) == NEEDS, \
        f"297.4: #141's own split waits for /work, yet it shows {w.action('issue', 141)!r}, not Needs you"
    w = make(cards={("issue", 139): {"Status": "Work", "Action": NEEDS}, ("issue", 140): {"Status": "Work", "Action": NEEDS},
                    ("issue", 141): {"Status": "Plan", "Action": NEEDS}}, closed={("pr", 70), ("issue", 71)}, **parents)
    board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    got = pills(w, ("issue", 139), ("issue", 140), ("issue", 141))
    assert got == {"issue #139": AUTO, "issue #140": None, "issue #141": NEEDS}, \
        f"297.4: after a merge, parents with their stories in progress or waiting for /work show {got}"


# 297.5: right after this merges, a sweep sets every pill on the board by these rules

def test_a_merge_sweeps_every_pill_on_the_board_to_what_it_should_be(record_property, make):
    """A merge's board run sets every pill on the board by the rules.

    Proves 297.5. The board holds every kind of wrong and right pill when PR #70 (closing #71) merges:
    closed #57 and merged PR #64 (both on autopilot), closed #58 and closed PR #61 all show Needs you; open #65 (on
    autopilot, with PR #73) and #68 show Needs you though their plan review sent them back to the planner by itself;
    #72 shows Needs you though the code owner already answered its approved plan with /work; #66 (on autopilot) shows
    no pill; #67, not on autopilot, shows Autopilot; #69 (on autopilot), whose reviewer escalated, lost its Needs you;
    and #59, whose approved plan waits for /work, shows Needs you with its PR #62. Afterwards: #65, #73 and #66 show
    Autopilot; #57, #64, #58, #61, #68, #72, #67, #70 and #71 show nothing, since a closed item shows no pill whatever
    its labels (#330); #69, #59 and #62 show Needs you."""
    record_property("proves", "297.5")
    want = {"issue #57": None, "pr #64": None, "issue #58": None, "pr #61": None, "issue #65": AUTO, "pr #73": AUTO,
            "issue #68": None, "issue #72": None, "issue #66": AUTO, "issue #67": None, "issue #69": NEEDS,
            "issue #59": NEEDS, "pr #62": NEEDS, "pr #70": None, "issue #71": None}
    shown = {("issue", 57): NEEDS, ("pr", 64): NEEDS, ("issue", 58): NEEDS, ("pr", 61): NEEDS, ("issue", 65): NEEDS,
             ("pr", 73): NEEDS, ("issue", 68): NEEDS, ("issue", 72): NEEDS, ("issue", 66): None, ("issue", 67): AUTO,
             ("issue", 69): None, ("issue", 59): NEEDS, ("pr", 62): NEEDS}
    w = make(labels={k: {LABEL} for k in (("issue", 57), ("pr", 64), ("issue", 65), ("pr", 73), ("issue", 66), ("issue", 69))},
             prs={59: 62, 65: 73}, closed={("issue", 57), ("issue", 58), ("pr", 64), ("pr", 61), ("pr", 70), ("issue", 71)},
             records={59: plan_approved(), 65: plan_blocked(), 68: plan_blocked(), 72: plan_approved() + ["/work"],
                      69: escalated()},
             cards={k: {"Status": "Review", **({"Action": a} if a else {})} for k, a in shown.items()})
    board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    got = {key: w.action(key.split(" #")[0], int(key.split(" #")[1])) for key in want}
    wrong = {k: f"{got[k]!r}, not {want[k]!r}" for k in want if got[k] != want[k]}
    assert not wrong, f"297.5: after the merge's sweep these cards show the wrong pill: {wrong}"


def test_every_later_merge_sweeps_again(record_property, make):
    """A pill that drifts after one merge is put right again at the next merge.

    Proves 297.5. PR #70 (closing #71) merges and its sweep sets #66 (on autopilot, nothing waits) to Autopilot and
    #67 (not on autopilot) to nothing. Then both drift: #66 shows Needs you and #67 shows Autopilot. PR #74 (closing
    #75) merges, and its sweep must put #66 back to Autopilot and #67 back to nothing. A sweep that runs only once,
    at the first merge, leaves both wrong. Today neither merge sweeps."""
    record_property("proves", "297.5")
    w = make(labels={("issue", 66): {LABEL}}, closed={("pr", 70), ("issue", 71), ("pr", 74), ("issue", 75)},
             cards={("issue", 66): {"Status": "Plan"}, ("issue", 67): {"Status": "Plan", "Action": AUTO}})
    board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    got = pills(w, ("issue", 66), ("issue", 67))
    assert got == {"issue #66": AUTO, "issue #67": None}, f"297.5: after the first merge's sweep the cards show {got}"
    w.cards[("issue", 66)]["Action"] = NEEDS
    w.cards[("issue", 67)]["Action"] = AUTO
    board.sync("pull_request_target", pr_event("closed", 74, 75, merged=True), SPEC, REPO)
    got = pills(w, ("issue", 66), ("issue", 67))
    assert got == {"issue #66": AUTO, "issue #67": None}, \
        f"297.5: after a second merge, drifted pills were not swept again: {got}"


def test_an_approve_starting_with_a_command_never_clears_needs_you_in_the_sweep(record_property, make):
    """In the merge's sweep, an Approve starting with a command never clears Needs you.

    Proves 297.5. Three issues each wait for the owner to merge their pull request after an approving code review, and
    all six cards show Needs you. On PR #62 (for #59) the code owner submits an Approve whose summary is "/work looks
    good"; on PR #61 (for #58) a comment review "/work looks good"; on PR #60 (for #57) a change request "/review".
    PR #70 merges. #59 and PR #62 must keep Needs you, since an Approve only ever means merge and the owner has not
    merged; #58, PR #61, #57 and PR #60 must show nothing, since those reviews are commands that answered."""
    record_property("proves", "297.5")
    w = make(prs={57: 60, 58: 61, 59: 62}, closed={("pr", 70), ("issue", 71)},
             records={n: code_approved() for n in (57, 58, 59)},
             reviews={62: [("APPROVED", "/work looks good")], 61: [("COMMENTED", "/work looks good")],
                      60: [("CHANGES_REQUESTED", "/review")]},
             cards={k: {"Status": "Review", "Action": NEEDS} for k in (("issue", 57), ("issue", 58), ("issue", 59),
                                                                       ("pr", 60), ("pr", 61), ("pr", 62))})
    board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    got = pills(w, ("issue", 59), ("pr", 62))
    assert got == {"issue #59": NEEDS, "pr #62": NEEDS}, \
        f"297.5: the owner's Approve starting with /work was taken as an answer: after the sweep #59 and PR #62 show {got}, not Needs you"
    got = pills(w, ("issue", 58), ("pr", 61), ("issue", 57), ("pr", 60))
    assert got == {"issue #58": None, "pr #61": None, "issue #57": None, "pr #60": None}, \
        f"297.5: the owner's comment review /work and change request /review did not count as answers in the sweep: {got}"


# 297.6: an item on autopilot shows exactly one pill, Autopilot or Needs you

def test_an_item_on_autopilot_always_shows_exactly_one_pill(record_property, make, monkeypatch, tmp_path):
    """An open item on autopilot shows Autopilot, or Needs you while it waits.

    Proves 297.6. #57 (on autopilot) and its PR #60 go through every moment the board changes: a run ends and the river
    goes on (its plan review sent it back to the planner), a new commit, finished checks, a run ends and the river
    stops for the owner (its code review approved), another new commit and finished checks, and the code owner's
    /review. After each one both cards must show Autopilot, or Needs you exactly while the river waits on the owner.
    Beside it #58, not on autopilot, with PR #61, never shows Autopilot. Once merged, both show no pill (#330)."""
    record_property("proves", "297.6")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60, 58: 61},
             records={57: plan_blocked(), 58: plan_blocked()})
    on, off = (("issue", 57), ("pr", 60)), (("issue", 58), ("pr", 61))

    def expect(moment, pill, other=None):
        got = pills(w, *on)
        assert got == {"issue #57": pill, "pr #60": pill}, f"297.6: after {moment}, #57 and PR #60 on autopilot show {got}, not {pill}"
        got = pills(w, *off)
        assert AUTO not in got.values() and (other is None or got == {"issue #58": other, "pr #61": other}), \
            f"297.6: after {moment}, #58 and PR #61, not on autopilot, show {got}"

    for n in (57, 58):
        run_ends(n, monkeypatch, tmp_path)
    expect("the river went on", AUTO, None)
    for pr, n in ((60, 57), (61, 58)):
        board.sync("pull_request_target", pr_event("synchronize", pr, n), SPEC, REPO)
    board.sync("workflow_run", checks_done(60, 61), SPEC, REPO)
    expect("a new commit and finished checks", AUTO, None)
    for n in (57, 58):
        w.records[n] = code_approved()
        run_ends(n, monkeypatch, tmp_path)
    expect("the river stopped for the owner", NEEDS, NEEDS)
    for pr, n in ((60, 57), (61, 58)):
        board.sync("pull_request_target", pr_event("synchronize", pr, n), SPEC, REPO)
    board.sync("workflow_run", checks_done(60, 61), SPEC, REPO)
    expect("a new commit and finished checks while the owner is waited on", NEEDS, NEEDS)
    for pr, n in ((60, 57), (61, 58)):
        said(w, n, "/review")
        board.sync("issue_comment", comment(pr, "/review", pr_body=f"Closes #{n}", labels=[LABEL] if n == 57 else []), SPEC, REPO)
    expect("the code owner's /review", AUTO, None)
    w.closed |= {("pr", 60), ("issue", 57)}
    board.sync("pull_request_target", pr_event("closed", 60, 57, merged=True), SPEC, REPO)
    assert pills(w, *on) == {"issue #57": None, "pr #60": None}, f"297.6: after the merge, #57 and PR #60 show {pills(w, *on)}"


# 297.7: a sweep that cannot read an item leaves its pill and says so

def test_a_sweep_that_cannot_read_an_item_leaves_its_pill_and_fails_naming_it(record_property, make):
    """A sweep that cannot read an item keeps its pill and fails naming it.

    Proves 297.7. #63 shows Needs you and GitHub answers nothing about it; #65 (on autopilot) shows Needs you though its
    plan review sent it back to the planner by itself. PR #70 merges. #63 must keep Needs you, #65 must show Autopilot,
    and the board run must fail with a reason that names #63, so a waiting item is never hidden silently. Today the
    merge neither fixes #65 nor says anything about #63."""
    record_property("proves", "297.7")
    w = make(labels={("issue", 65): {LABEL}}, unreadable={63}, closed={("pr", 70), ("issue", 71)},
             records={65: plan_blocked()},
             cards={("issue", 63): {"Status": "Plan", "Action": NEEDS}, ("issue", 65): {"Status": "Plan", "Action": NEEDS}})
    with pytest.raises(RuntimeError) as e:
        board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    assert "#63" in str(e.value), f"297.7: the board run failed without naming #63: {e.value}"
    got = pills(w, ("issue", 63), ("issue", 65))
    assert got == {"issue #63": NEEDS, "issue #65": AUTO}, \
        f"297.7: after a sweep that could not read #63, the cards show {got}; #63 must keep Needs you and #65 show Autopilot"


def test_a_sweep_that_reads_everything_passes(record_property, make):
    """A sweep that reads every item finishes without failing the board run.

    Proves 297.7. The good case beside the failing one: the same board without the unreadable #63. The merge's board run
    returns normally and #65 shows Autopilot."""
    record_property("proves", "297.7")
    w = make(labels={("issue", 65): {LABEL}}, closed={("pr", 70), ("issue", 71)}, records={65: plan_blocked()},
             cards={("issue", 65): {"Status": "Plan", "Action": NEEDS}})
    board.sync("pull_request_target", pr_event("closed", 70, 71, merged=True), SPEC, REPO)
    assert w.action("issue", 65) == AUTO, f"297.7: after the sweep #65 shows {w.action('issue', 65)!r}, not Autopilot"


# The real dokima.board.Board's two new reads, against a faked GitHub

class GitHub:
    """GitHub as the real Board reads it: a two-page project, issues and pull requests.

    Every query about the organization's project answers its id, its Status and Action fields and, page by page, its
    items: each with its id, type, content (number, state, closed, merged, labels, __typename), its Action value both as
    fieldValueByName and in fieldValues. The second page is answered when any variable or the query text carries the first page's endCursor.
    Every query about the repository answers the issue or pull request asked for, with its state; the REST reads of
    repos/dokima-dev/dokima/issues/N and pulls/N answer the same."""

    STATES = {("issue", 57): "CLOSED", ("issue", 58): "OPEN", ("issue", 59): "OPEN",
              ("pr", 60): "MERGED", ("pr", 61): "CLOSED", ("pr", 62): "OPEN"}
    AUTOPILOT = {("issue", 57), ("issue", 58), ("pr", 60)}

    def __init__(self):
        self.pages = [[("issue", 57, NEEDS), ("issue", 58, AUTO), ("pr", 61, None), ("draft", None, NEEDS)],
                      [("pr", 60, NEEDS), ("issue", 59, NEEDS)]]

    def node(self, kind, n, action):
        content = {"__typename": "DraftIssue", "title": "An idea"} if kind == "draft" else \
            {"__typename": "Issue" if kind == "issue" else "PullRequest", "number": n, "state": self.STATES[(kind, n)],
             "closed": self.STATES[(kind, n)] != "OPEN", "merged": self.STATES[(kind, n)] == "MERGED",
             "labels": {"nodes": [{"name": LABEL}] if (kind, n) in self.AUTOPILOT else [{"name": "high"}]}}
        values = [{"name": "Review", "field": {"name": "Status"}}] + ([{"name": action, "field": {"name": "Action"}}] if action else [])
        return {"id": f"ITEM_{kind}_{n}", "type": {"issue": "ISSUE", "pr": "PULL_REQUEST", "draft": "DRAFT_ISSUE"}[kind],
                "content": content, "fieldValueByName": {"name": action} if action else None, "fieldValues": {"nodes": values}}

    def q(self, query, **v):
        text = " ".join(query.split())
        if "organization" in text:
            second = any(str(x) == "c1" for x in v.values()) or '"c1"' in text
            page = self.pages[1 if second else 0]
            return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": [
                {"id": "S", "name": "Status", "options": [{"id": "s-" + o, "name": o} for o in ("Backlog", "Plan", "Work", "Review", "Done")]},
                {"id": "W", "name": "Action", "options": [{"id": "w-you", "name": NEEDS}, {"id": "w-auto", "name": AUTO}]}]},
                "items": {"totalCount": 6, "pageInfo": {"hasNextPage": not second, "endCursor": None if second else "c1"},
                          "nodes": [self.node(*x) for x in page]},
                "views": {"nodes": []}}}}
        if "repository" in text:
            n = next((x for x in v.values() if isinstance(x, int)), None)
            if n is None:
                n = int(re.search(r"(?:issue|pullRequest)\s*\(\s*number:\s*(\d+)", text).group(1))
            out = {}
            for field, kind in (("issue", "issue"), ("pullRequest", "pr")):
                if re.search(field + r"\s*\(", text):
                    st = self.STATES[(kind, n)]
                    out[field] = {"id": f"N_{n}", "number": n, "state": st, "closed": st != "OPEN", "merged": st == "MERGED",
                                  "labels": {"nodes": []}, "projectItems": {"nodes": []}}
            return {"repository": out}
        return {}

    def rest(self, method, path, **fields):
        m = re.fullmatch(r"repos/dokima-dev/dokima/(issues|pulls)/(\d+)", path.lstrip("/"))
        if m and method.upper() == "GET":
            n = int(m.group(2))
            st = self.STATES.get(("issue", n)) or self.STATES.get(("pr", n))
            return {"number": n, "state": "open" if st == "OPEN" else "closed", "merged": st == "MERGED"}
        return {}


def real(gh):
    """The real Board, reading the faked GitHub."""
    return board.Board("dokima-dev/1", "dokima-dev/dokima", q=gh.q, rest=gh.rest)


def test_the_real_board_lists_every_card_with_its_pill_state_and_label(record_property):
    """The board lists every card with its pill, closed state and autopilot label.

    Proves 297.5. The real Board reads a project of two pages: closed #57 (on autopilot) shows Needs you, open #58 (on autopilot)
    Autopilot, closed PR #61 nothing and a draft item Needs you on the first; merged PR #60 (on autopilot) and open #59
    show Needs you on the second. It must list exactly those five issues and pull requests with what each shows,
    skipping the draft, which is no issue or pull request."""
    record_property("proves", "297.5")
    if not callable(getattr(board.Board, "cards", None)):
        pytest.fail("297.5: the real Board cannot list its cards for the sweep yet (it has no cards)")
    got = sorted(real(GitHub()).cards(), key=lambda c: (c["kind"], c["number"]))
    want = [{"kind": "issue", "number": 57, "action": NEEDS, "closed": True, "autopilot": True},
            {"kind": "issue", "number": 58, "action": AUTO, "closed": False, "autopilot": True},
            {"kind": "issue", "number": 59, "action": NEEDS, "closed": False, "autopilot": False},
            {"kind": "pr", "number": 60, "action": NEEDS, "closed": True, "autopilot": True},
            {"kind": "pr", "number": 61, "action": None, "closed": True, "autopilot": False}]
    got = [{k: c.get(k) for k in ("kind", "number", "action", "closed", "autopilot")} for c in got]
    assert got == want, f"297.5: the board listed {got}, not {want}"


def test_the_real_board_tells_a_closed_item_from_an_open_one(record_property):
    """The board reads whether an issue or pull request is closed; merged counts as closed.

    Proves 297.3. The real Board reads closed #57, open #58, merged PR #60, closed PR #61 and open PR #62."""
    record_property("proves", "297.3")
    if not callable(getattr(board.Board, "state", None)):
        pytest.fail("297.3: the real Board cannot read whether an issue or pull request is closed yet (it has no state)")
    b = real(GitHub())
    got = {f"{k} #{n}": b.state(k, n) for k, n in (("issue", 57), ("issue", 58), ("pr", 60), ("pr", 61), ("pr", 62))}
    want = {"issue #57": "closed", "issue #58": "open", "pr #60": "closed", "pr #61": "closed", "pr #62": "open"}
    assert got == want, f"297.3: the board read the states as {got}, not {want}"

"""One scan names every card that does not match its issue's state now (#333).

Story 3 of #330. The owner's test of #330: after it ships, a scan of the whole board finds no closed card outside Done
or with a pill, no open card in the wrong column, and the PR cards of #246 and #312 show Merged with every check passed.
This scan is that test, made a command the owner can run any time:

    DOKIMA_BOARD=org/number REPO=owner/name python3 -m dokima.scan

It prints one line for each card that does not match its state, naming it ("issue #N" or "PR #N") and saying what is
wrong, then exits 1; when every card matches, it prints `All N cards on the board match their state.` (N the number of
issue and pull request cards it checked) and exits 0. It only reads: it never moves a card, sets a pill or edits a body.

How the tests run it. dokima.scan.main() is called in-process with DOKIMA_BOARD and REPO set; it returns the exit code
(or raises SystemExit with it). GitHub is faked in one World:
- dokima.board.Board is replaced by a fake whose cards() lists every issue and pull request card as
  {kind, number, status, action, closed, autopilot}, as the real Board.cards() does on main (#339). Every write the
  fake board offers (set, label, add_view, set_view_filter, and item() for something not on the board) is logged.
- The `gh` helper of every dokima module that has one (dokima.agent, dokima.body, dokima.card, dokima.plan, and
  dokima.scan if it defines its own) answers from the World: issues and pull requests with their state, body, records
  and checks, the `gh api` REST reads the card code makes, and the GraphQL issue and closing-issue queries. Writes are
  logged. A call the fake does not know fails loudly, naming the call, so a test that fails on it says why.
The column an open card's state gives is the one the board code puts it in now (dokima.board.where, #339): no record is
Backlog, a plan waiting for /work or sent back to the planner is Plan, an approving code review is Review, and a pull
request follows its issue. A closed issue or a merged or closed pull request belongs in Done with no pill
(dokima.board.DONE).
The card a state gives is the one Dokima's card code writes when it redraws the issue now (dokima.card.draw, the part
above the marker, the same on the PR); dokima.scan.card_now(repo, kind, number) returns it, and a card is stale when
its body does not already show it, as card.draw's own changed_only check decides (#347).
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent, board, body, card, plan  # noqa: E402
from dokima import agent_github  # noqa: E402
from test_agent import GOOD_REVIEW, GOOD_WORK, rec  # noqa: E402

try:
    from dokima import scan
except ImportError:  # the scan does not exist yet; each test fails saying so
    scan = None

REPO, SPEC = "o/r", "o/1"
OWNER = sorted(plan.repo_approvers("o"))[0]
NEEDS, AUTO = "Needs you", "Autopilot"
CODEOWNERS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".github", "CODEOWNERS")).read()
WRITE_VERBS = {("issue", "edit"), ("issue", "comment"), ("issue", "close"), ("issue", "reopen"), ("pr", "edit"),
               ("pr", "comment"), ("pr", "merge"), ("pr", "close"), ("label", "create")}


def plan_approved(summary="Scan the board."):
    """Records up to an approved plan waiting for /work: the card belongs in Plan."""
    return [rec("planner", handback={"kind": "user_story", "summary": summary}),
            rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})]


def plan_blocked():
    """Records up to a plan review's block: the card belongs in Plan."""
    return [rec("planner", handback={"kind": "user_story", "summary": "Scan the board."}), rec("reviewer", "plan", GOOD_REVIEW)]


def code_approved():
    """Records up to an approving code review: the issue and its PR belong in Review."""
    return plan_approved() + ["/work", rec("worker", handback=GOOD_WORK),
                              rec("reviewer", "pr", {**GOOD_REVIEW, "stage": "pr", "verdict": "approve", "blockers": []})]


class World:
    """GitHub as the scan sees it: cards, issues, PRs, records, checks and every write."""

    def __init__(self):
        self.cards = {}  # (kind, n) -> {"Status": column, "Action": pill or None}
        self.issues = {}  # n -> {"state", "body", "records", "labels"}
        self.prs = {}  # n -> {"issue", "state" (OPEN, MERGED, CLOSED), "body", "sha", "checks"}
        self.refused = set()  # numbers GitHub will not answer about
        self.writes, self.calls, self.unknown = [], [], []
        self.opened = []  # (board spec, repo) each time a board was opened

    def issue(self, n, state="open", records=(), card=None, labels=()):
        self.issues[n] = {"state": state, "records": list(records), "labels": list(labels),
                          "body": (card + "\n\n" if card else "") + f"<!-- dokima-ask -->\nThe owner's ask for #{n}."}

    def pr(self, n, issue, state="OPEN", card=None, checks=("all tests",)):
        self.prs[n] = {"issue": issue, "state": state, "sha": f"sha{n}",
                       "body": (card + "\n\n" if card else "") + f"Closes #{issue}",
                       "checks": [{"name": c, "status": "completed", "conclusion": "success", "html_url": f"https://x/{c}",
                                   "head_sha": f"sha{n}"} for c in checks]}

    def place(self, kind, n, status, action=None):
        self.cards[(kind, n)] = {"Status": status, "Action": action}

    def closed(self, n):
        if n in self.prs:
            return self.prs[n]["state"] != "OPEN"
        return self.issues[n]["state"] == "closed"

    def pr_of(self, n):
        return next((p for p, v in self.prs.items() if v["issue"] == n), None)

    def comments(self, n):
        items = card.as_items(self.issues[n]["records"], OWNER) if n in self.issues else []
        return [{**c, "createdAt": f"2026-10-09T00:{i // 60:02d}:{i % 60:02d}Z"} for i, c in enumerate(items)]


def fake_board(world):
    """A stand-in for dokima.board.Board that reads the World's cards and logs every write."""

    class FakeBoard:
        def __init__(self, spec=None, repo=None, *a, **k):
            world.opened.append((spec, repo))
            self.fields = {"Status": ("S", {o: "s-" + o for o in ("Backlog", "Plan", "Work", "Review", "Done")}),
                           "Action": ("W", {NEEDS: "w-1", AUTO: "w-2"}), "Priority": ("P", {})}

        def cards(self):
            return [{"kind": k, "number": n, "status": c.get("Status"), "action": c.get("Action"),
                     "closed": world.closed(n), "autopilot": AUTO.lower() in (world.issues.get(n) or {}).get("labels", [])}
                    for (k, n), c in sorted(world.cards.items())]

        def item(self, kind, n):
            if (kind, int(n)) not in world.cards:
                world.writes.append(("board add", kind, n))
            return (kind, int(n))

        def value(self, iid, field):
            return world.cards.get(iid, {}).get(field)

        def state(self, kind, n):
            return "closed" if world.closed(int(n)) else "open"

        def autopilot(self, kind, n):
            return AUTO.lower() in (world.issues.get(int(n)) or {}).get("labels", [])

        def open_pr(self, n):
            p = world.pr_of(int(n))
            return p if p and not world.closed(p) else None

        def set(self, iid, field, option):
            world.writes.append(("board set", iid, field, option))

        def label(self, kind, n, on):
            world.writes.append(("board label", kind, n, on))

        def add_view(self, *a):
            world.writes.append(("board add view",) + a)

        def set_view_filter(self, *a):
            world.writes.append(("board view filter",) + a)

    return FakeBoard


def fake_gh(world):
    """The `gh` helper, answering from the World, logging writes and refusing unknown calls loudly."""

    def refuse(n, a):
        if n in world.refused:
            raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr="gh: HTTP 502: Bad Gateway")

    def unknown(a):
        world.unknown.append(a)
        raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr=f"fake GitHub does not know: gh {' '.join(a)}")

    def rest_issue(n):
        if n in world.prs:
            p = world.prs[n]
            return {"number": n, "state": "closed" if world.closed(n) else "open", "body": p["body"], "title": f"PR {n}",
                    "comments": 0, "labels": [], "pull_request": {"merged_at": "2026-10-09T02:00:00Z" if p["state"] == "MERGED" else None}}
        i = world.issues[n]
        return {"number": n, "state": i["state"], "body": i["body"], "title": f"Issue {n}", "comments": len(i["records"]),
                "labels": [{"name": x} for x in i["labels"]], "html_url": f"https://github.com/o/r/issues/{n}"}

    def rest_pr(n):
        p = world.prs[n]
        return {"number": n, "state": "closed" if world.closed(n) else "open", "merged": p["state"] == "MERGED",
                "merged_at": "2026-10-09T02:00:00Z" if p["state"] == "MERGED" else None, "body": p["body"],
                "head": {"sha": p["sha"], "ref": f"try/issue-{p['issue']}"}, "base": {"ref": "main"},
                "user": {"login": agent.BOT}, "merged_by": {"login": OWNER} if p["state"] == "MERGED" else None,
                "html_url": f"https://github.com/o/r/pull/{n}"}

    def gh(*args, **kw):
        a = [str(x) for x in args]
        world.calls.append(a)
        if tuple(a[:2]) in WRITE_VERBS:
            world.writes.append(("gh",) + tuple(a))
            return ""
        if a[:2] == ["issue", "view"]:
            n = int(a[2])
            refuse(n, a)
            if n not in world.issues:
                unknown(a)
            d = rest_issue(n)
            return json.dumps({"number": n, "title": d["title"], "body": d["body"], "comments": world.comments(n),
                               "state": d["state"].upper(), "labels": d["labels"], "url": d["html_url"]})
        if a[:2] == ["pr", "view"]:
            n = int(a[2])
            refuse(n, a)
            if n not in world.prs:
                unknown(a)
            p = world.prs[n]
            return json.dumps({"number": n, "state": p["state"], "body": p["body"], "headRefName": f"try/issue-{p['issue']}",
                               "comments": [], "reviews": [], "labels": [], "mergedAt": rest_pr(n)["merged_at"]})
        if a[:2] == ["pr", "list"]:
            head = a[a.index("--head") + 1] if "--head" in a else ""
            m = re.fullmatch(r"try/issue-(\d+)", head)
            p = world.pr_of(int(m.group(1))) if m else None
            state = a[a.index("--state") + 1] if "--state" in a else "open"
            found = [{"number": p}] if p and (state == "all" or (state == "open") != world.closed(p)) else []
            if "-q" in a or "--jq" in a:
                return f"{found[0]['number']}\n" if found else "\n"
            return json.dumps(found)
        if a[:1] != ["api"]:
            unknown(a)
        method = a[a.index("-X") + 1].upper() if "-X" in a else ("POST" if any(x in ("-f", "-F") for x in a) and "graphql" not in a else "GET")
        if "graphql" in a:
            query = next(x for x in a if x.startswith("query="))
            if "mutation" in query:
                world.writes.append(("gh",) + tuple(a))
                return json.dumps({"data": {}})
            nums = [int(x.split("=", 1)[1]) for x in a if re.fullmatch(r"[ip]=\d+", x)]
            if not nums:
                unknown(a)
            n = nums[0]
            refuse(n, a)
            if "closingIssuesReferences" in query:
                issue = world.prs[n]["issue"] if n in world.prs else None
                return json.dumps({"data": {"repository": {"pullRequest": {"closingIssuesReferences": {"nodes": [{"number": issue}] if issue else []}}}}})
            if n not in world.issues:
                unknown(a)
            d = rest_issue(n)
            return json.dumps({"data": {"repository": {"issue": {"number": n, "title": d["title"], "body": d["body"],
                                                                 "url": d["html_url"], "state": d["state"].upper(),
                                                                 "userContentEdits": {"nodes": []}}}}})
        path = next((x for x in a[1:] if x.lstrip("/").startswith("repos/")), "").lstrip("/")
        if method != "GET":
            world.writes.append(("gh",) + tuple(a))
            return "{}"
        bare = path.split("?")[0]
        if bare == "repos/o/r/contents/.github/CODEOWNERS":
            return CODEOWNERS
        if bare.startswith("repos/o/r/contents/"):
            raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr="gh: Not Found (HTTP 404)")
        if bare.startswith("repos/o/r/actions/workflows/"):
            return json.dumps({"total_count": 0, "workflow_runs": []})
        if bare == "repos/o/r/pulls":
            m = re.search(r"head=o:(?:try|work)/issue-(\d+)", path)
            p = world.pr_of(int(m.group(1))) if m else None
            return json.dumps([rest_pr(p)] if p else [] if m else [rest_pr(x) for x in world.prs])
        if bare == "repos/o/r/issues":
            return json.dumps([rest_issue(n) for n in sorted(set(world.issues) | set(world.prs))])
        m = re.fullmatch(r"repos/o/r/commits/(\w+)/(check-runs|pulls|status|check-suites)", bare)
        if m:
            p = next((x for x, v in world.prs.items() if v["sha"] == m.group(1)), None)
            if m.group(2) == "check-runs":
                return json.dumps({"total_count": len(world.prs[p]["checks"]) if p else 0, "check_runs": world.prs[p]["checks"] if p else []})
            if m.group(2) == "pulls":
                return json.dumps([rest_pr(p)] if p else [])
            return json.dumps({"state": "success", "statuses": [], "check_suites": [], "total_count": 0})
        m = re.fullmatch(r"repos/o/r/(issues|pulls)/(\d+)(/[\w/]+)?", bare)
        if not m:
            unknown(a)
        n, rest = int(m.group(2)), m.group(3) or ""
        refuse(n, a)
        if n not in world.issues and n not in world.prs:
            unknown(a)
        if rest == "":
            return json.dumps(rest_pr(n) if m.group(1) == "pulls" else rest_issue(n))
        if rest == "/comments" and m.group(1) == "issues":
            return json.dumps([{"user": {"login": c["author"]["login"]}, "body": c["body"], "created_at": c["createdAt"]}
                               for c in world.comments(n)])
        if rest in ("/comments", "/reviews", "/files", "/events", "/timeline", "/sub_issues", "/labels",
                    "/dependencies/blocked_by", "/dependencies/blocking", "/commits"):
            return "[]"
        unknown(a)

    return gh


@pytest.fixture
def world(monkeypatch):
    """A fresh World wired into the board and every `gh` helper, with the scan's settings."""
    w = World()
    monkeypatch.setattr(board, "Board", fake_board(w))
    for mod in (agent_github, body, card, plan, scan):
        if mod is not None and hasattr(mod, "gh"):
            monkeypatch.setattr(mod, "gh", fake_gh(w))
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    return w


def need_scan(criterion):
    """Fail, naming the criterion, while dokima/scan.py does not exist."""
    if scan is None:
        pytest.fail(f"{criterion}: there is no scan yet (dokima/scan.py is missing)")
    for name in ("main", "card_now"):
        if not callable(getattr(scan, name, None)):
            pytest.fail(f"{criterion}: dokima/scan.py has no {name}()")


def true_card(w, kind, n):
    """The card Dokima draws now for this issue or PR, as the scan sees it."""
    return scan.card_now(REPO, kind, n).strip()


def make_true(w, *items):
    """Write the card Dokima draws now into each body, saved the way Dokima saves it."""
    for kind, n in items:
        text = scan.card_now(REPO, kind, n)
        if kind == "pr":
            # The PR carries its issue's Original issue fold below the card (#373), read from the issue's body, and
            # closes its issue by the issue's full address (#452).
            issue = w.prs[n]["issue"]
            w.prs[n]["body"] = card.pr_body(text, w.prs[n]["body"], body.ask(w.issues[issue]["body"]),
                                            issue_url=f"https://github.com/o/r/issues/{issue}")
        else:
            w.issues[n]["body"] = body.redraw(w.issues[n]["body"], text)


def drawn(w, n, pr_number, monkeypatch, tmp_path):
    """The card Dokima's card code writes when it redraws issue n, caught before saving."""
    caught = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(body, "save", lambda repo, number, current, top: caught.append(top) or False)
    card.draw(REPO, n, pr_number)
    assert caught, f"test setup: Dokima's card code wrote no card for #{n}"
    return caught[-1].strip()


def run(w, capsys):
    """Run the scan once; (exit code, the lines it printed)."""
    try:
        code = scan.main()
    except SystemExit as e:
        code = e.code
    out = capsys.readouterr()
    lines = [x for x in (out.out + out.err).splitlines() if x.strip()]
    return (0 if code is None else code), lines


def named(lines, kind, n):
    """The lines naming this card: "issue #N" or "PR #N" as a whole word."""
    label = r"\bissue #" if kind == "issue" else r"\b(?:PR|pull request) #"
    return [x for x in lines if re.search(label + str(n) + r"\b", x, re.I)]


OLD_CARD = "<!-- dokima-card -->\n**Review**\n\nAn old card drawn before the state changed.\n<!-- /dokima-card -->"


# 333.1: the scan names every closed card outside Done or with a pill

def test_the_scan_names_every_closed_card_outside_done_or_with_a_pill(world, capsys, record_property):
    """The scan names every closed card outside Done or with a pill, and fails.

    Proves 333.1.
    Closed #57 sits in Review; closed #58 sits in Done with Autopilot; merged PR #64 (for closed #65) sits in Done with
    Needs you; closed PR #66 (for closed #67) sits in Work. Closed #59, #65 and #67 sit in Done with no pill, the way
    they should. Every card's body is the card Dokima draws now. The scan must name #57 with Review, #58 with Autopilot,
    PR #64 with Needs you and PR #66 with Work, name none of #59, #65 and #67, and exit 1."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    for n in (57, 58, 59, 65, 67):
        w.issue(n, state="closed", records=plan_approved(), labels=["autopilot"] if n == 58 else [])
    w.pr(64, 65, state="MERGED")
    w.pr(66, 67, state="CLOSED")
    w.place("issue", 57, "Review")
    w.place("issue", 58, "Done", AUTO)
    w.place("pr", 64, "Done", NEEDS)
    w.place("pr", 66, "Work")
    for n in (59, 65, 67):
        w.place("issue", n, "Done")
    make_true(w, *[("issue", n) for n in (57, 58, 59, 65, 67)], ("pr", 64), ("pr", 66))
    code, lines = run(w, capsys)
    for kind, n, word in (("issue", 57, "Review"), ("issue", 58, AUTO), ("pr", 64, NEEDS), ("pr", 66, "Work")):
        got = named(lines, kind, n)
        assert got, f"333.1: closed {kind} #{n} is in the wrong place or has a pill, but the scan did not name it: {lines}"
        assert any(word in x for x in got), f"333.1: the scan named {kind} #{n} without saying it shows {word}: {got}"
    wrong = {n: named(lines, "issue", n) for n in (59, 65, 67) if named(lines, "issue", n)}
    assert not wrong, f"333.1: the scan named closed cards that sit in Done with no pill: {wrong}"
    assert code == 1, f"333.1: the scan named wrong cards but exited {code}, not 1"


# 333.1: the scan names every open card in the wrong column

def test_the_scan_names_every_open_card_in_the_wrong_column(world, capsys, record_property):
    """The scan names every open card in a column its state does not give.

    Proves 333.1.
    Open #71 has no record yet (Backlog) but sits in Plan; open #72's plan review sent it back to the planner (Plan) but
    it sits in Backlog; open #73's code review approved (Review), and #73 sits in Review while its PR #74 sits in Work.
    Open #75 waits for /work in Plan with Needs you, and open #76 has no record and sits in Backlog, both right. Every
    body is the card Dokima draws now. The scan must name #71 (saying Plan and Backlog), #72 (Backlog and Plan) and
    PR #74 (Work and Review), and none of #73, #75 and #76, and exit 1."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    w.issue(71)
    w.issue(72, records=plan_blocked())
    w.issue(73, records=code_approved())
    w.pr(74, 73)
    w.issue(75, records=plan_approved())
    w.issue(76)
    w.place("issue", 71, "Plan")
    w.place("issue", 72, "Backlog")
    w.place("issue", 73, "Review", NEEDS)
    w.place("pr", 74, "Work", NEEDS)
    w.place("issue", 75, "Plan", NEEDS)
    w.place("issue", 76, "Backlog")
    make_true(w, *[("issue", n) for n in (71, 72, 73, 75, 76)], ("pr", 74))
    code, lines = run(w, capsys)
    for kind, n, shown, want in (("issue", 71, "Plan", "Backlog"), ("issue", 72, "Backlog", "Plan"), ("pr", 74, "Work", "Review")):
        got = named(lines, kind, n)
        assert got, f"333.1: open {kind} #{n} sits in {shown} though its state gives {want}, but the scan did not name it: {lines}"
        assert any(shown in x and want in x for x in got), \
            f"333.1: the scan named {kind} #{n} without saying it sits in {shown} and belongs in {want}: {got}"
    wrong = {n: named(lines, "issue", n) for n in (73, 75, 76) if named(lines, "issue", n)}
    assert not wrong, f"333.1: the scan named open cards that sit in the right column: {wrong}"
    assert code == 1, f"333.1: the scan named wrong cards but exited {code}, not 1"


# 333.1: the scan names every stale card

def test_the_card_the_scan_expects_is_drawn_from_the_state_now(world, monkeypatch, tmp_path, record_property):
    """The card the scan compares with is the one Dokima draws from GitHub's state now.

    Proves 333.1.
    #312 has no record and its card is the old one: the card the scan expects says Backlog and shows no plan.
    Once a plan is recorded on #312, the card it expects says the plan's summary and no longer says there is
    no plan. Merged PR #260 of #246, with every check passed: the card it expects for the PR says Merged, with All tests
    passed (shown as Test suite, as on the approved card of #557), and is the same card it expects on #246 but for the PR's link back to #246 (#452). For both issues it is exactly the card Dokima's card code writes
    when it redraws them. A scan that trusted the card already on the issue, or drew one fixed card, would fail here."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    w.issue(312, card=OLD_CARD)
    first = true_card(w, "issue", 312)
    assert "Backlog" in first and "Every card says what is true." not in first, \
        f"333.1: for #312 with no record, the scan expects this card, not one in Backlog with no plan: {first}"
    w.issues[312]["records"] = plan_approved(summary="Every card says what is true.")
    second = true_card(w, "issue", 312)
    assert "Every card says what is true." in second and "This issue has no plan yet." not in second, \
        f"333.1: after #312's plan was recorded, the scan still expects a card without it: {second}"
    w.issue(246, state="closed", records=code_approved(), card=OLD_CARD)
    w.pr(260, 246, state="MERGED", card=OLD_CARD)
    pr_card = true_card(w, "pr", 260)
    assert "**Merged**" in pr_card, f"333.1: for merged PR #260 the scan expects a card that does not say Merged: {pr_card}"
    assert re.search(r'alt="passed"></a> Test suite', pr_card), \
        f"333.1: for PR #260, whose every check passed, the scan expects a card without All tests passed: {pr_card}"
    # Since #452 the PR's card links back to its issue in its top row, and the issue's own card does not.
    url = re.escape("https://github.com/o/r/issues/246")
    assert re.sub(rf"^{url} · | · {url}(?= · |$)", "", pr_card, count=1, flags=re.M) == true_card(w, "issue", 246), \
        "333.1: the scan expects a different card on PR #260 than on #246, besides the PR's link back to #246"
    for n, pr_number in ((312, None), (246, 260)):
        assert true_card(w, "issue", n) == drawn(w, n, pr_number, monkeypatch, tmp_path), \
            f"333.1: the card the scan expects for #{n} is not the one Dokima's card code writes on a redraw"


def test_the_scan_names_every_stale_issue_card_and_pr_card(world, capsys, record_property):
    """The scan names every issue and PR card that does not show its state now.

    Proves 333.1.
    Board columns and pills are all right. #312's card is from before its plan; merged PR #260 of #246 still shows an
    old open card while #246's own card is true; open #320's card is true and its open PR #321's body holds no card at
    all. The scan must name #312, PR #260 and PR #321, name neither #246 nor #320, and exit 1."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    w.issue(312, records=plan_approved(), card=OLD_CARD)
    w.issue(246, state="closed", records=code_approved())
    w.pr(260, 246, state="MERGED", card=OLD_CARD)
    w.issue(320, records=code_approved())
    w.pr(321, 320)
    w.place("issue", 312, "Plan", NEEDS)
    w.place("issue", 246, "Done")
    w.place("pr", 260, "Done")
    w.place("issue", 320, "Review", NEEDS)
    w.place("pr", 321, "Review", NEEDS)
    make_true(w, ("issue", 246), ("issue", 320))
    code, lines = run(w, capsys)
    for kind, n in (("issue", 312), ("pr", 260), ("pr", 321)):
        assert named(lines, kind, n), f"333.1: {kind} #{n}'s card does not show its state now, but the scan did not name it: {lines}"
    wrong = {n: named(lines, "issue", n) for n in (246, 320) if named(lines, "issue", n)}
    assert not wrong, f"333.1: the scan named issue cards that show their state now: {wrong}"
    assert code == 1, f"333.1: the scan named stale cards but exited {code}, not 1"


# 333.1: when everything matches, the scan says so and exits 0

def test_the_scan_of_a_true_board_exits_0_saying_all_is_true(world, capsys, record_property):
    """When every card matches its state, the scan says all match and exits 0.

    Proves 333.1.
    Open #71 (Backlog), #75 waiting for /work (Plan, Needs you), #73 with an approved code review and its PR #74
    (Review, Needs you), closed #246 and its merged PR #260 (Done, no pill): six cards in the right column with the right
    pill, each body the card Dokima draws now. The scan must print `All 6 cards on the board match their state.`,
    name no card, and exit 0."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    w.issue(71)
    w.issue(75, records=plan_approved())
    w.issue(73, records=code_approved())
    w.pr(74, 73)
    w.issue(246, state="closed", records=code_approved())
    w.pr(260, 246, state="MERGED")
    w.place("issue", 71, "Backlog")
    w.place("issue", 75, "Plan", NEEDS)
    w.place("issue", 73, "Review", NEEDS)
    w.place("pr", 74, "Review", NEEDS)
    w.place("issue", 246, "Done")
    w.place("pr", 260, "Done")
    make_true(w, ("issue", 71), ("issue", 75), ("issue", 73), ("pr", 74), ("issue", 246), ("pr", 260))
    code, lines = run(w, capsys)
    assert "All 6 cards on the board match their state." in lines, \
        f"333.1: on a board where every card is true the scan did not say all 6 match: {lines}"
    wrong = [x for kind, n in (("issue", 71), ("issue", 75), ("issue", 73), ("pr", 74), ("issue", 246), ("pr", 260))
             for x in named(lines, kind, n)]
    assert not wrong, f"333.1: on a board where every card is true the scan named: {wrong}"
    assert code == 0, f"333.1: on a board where every card is true the scan exited {code}, not 0"


def test_the_scan_names_an_open_card_with_no_column(world, capsys, record_property):
    """An open card in no column at all is named as in the wrong column.

    Proves 333.1.
    Open #72 with no record is on the board with no Status; open #76 with no record sits in Backlog, both bodies the
    card Dokima draws now. The scan must name #72, not name #76, and exit 1."""
    record_property("proves", "333.1")
    need_scan("333.1")
    w = world
    for n, column in ((72, None), (76, "Backlog")):
        w.issue(n)
        w.place("issue", n, column)
    make_true(w, ("issue", 72), ("issue", 76))
    code, lines = run(w, capsys)
    assert named(lines, "issue", 72) and code == 1, f"333.1: open #72 in no column was not named (exit {code}): {lines}"
    assert not named(lines, "issue", 76), f"333.1: the scan named #76, which matches its state: {lines}"


# 333.3 (manual, with this automated part): the scan reads the board and repo the owner names

def test_the_scan_checks_the_board_and_repo_the_owner_names(world, capsys, monkeypatch, record_property):
    """The scan checks exactly the board and repo the owner names when running it.

    Proves 333.3. The live scan itself is manual: after #330 ships, the owner runs
    `DOKIMA_BOARD=dokima-dev/N REPO=dokima-dev/dokima python3 -m dokima.scan` once, sees it find nothing, and opens the
    PRs of #246 and #312 to see Merged with every check passed. This part runs the scan with DOKIMA_BOARD set to o/9
    and then o/4 and checks it opens exactly that board for repo o/r each time, and says all 1 card matches."""
    record_property("proves", "333.3")
    need_scan("333.3")
    w = world
    w.issue(76)
    w.place("issue", 76, "Backlog")
    make_true(w, ("issue", 76))
    for spec in ("o/9", "o/4"):
        monkeypatch.setenv("DOKIMA_BOARD", spec)
        w.opened.clear()
        code, lines = run(w, capsys)
        assert w.opened and set(w.opened) == {(spec, REPO)}, \
            f"333.3: with DOKIMA_BOARD={spec} and REPO={REPO} the scan opened {w.opened}"
        assert code == 0 and any(re.fullmatch(r"All 1 cards? on the board match(es)? their state\.", x) for x in lines), \
            f"333.3: the scan of board {spec} with one true card gave exit {code}: {lines}"


# 333.4: the scan only reads

def test_the_scan_never_moves_a_card_or_edits_a_body(world, capsys, record_property):
    """The scan only reads: on a board of wrong cards it writes nothing.

    Proves 333.4.
    Closed #57 in Review with Needs you, open #71 with no record in Work, #312 with an old card and merged PR #260 with
    an old card, and PR #262 of open #261 that is not on the board. The scan must name what is wrong, and GitHub must
    log no write: no card moved, no pill set, no item added to the board, no label, no body edited and no comment."""
    record_property("proves", "333.4")
    need_scan("333.4")
    w = world
    w.issue(57, state="closed", card=OLD_CARD)
    w.issue(71, card=OLD_CARD)
    w.issue(312, records=plan_approved(), card=OLD_CARD)
    w.issue(246, state="closed", records=code_approved(), card=OLD_CARD)
    w.pr(260, 246, state="MERGED", card=OLD_CARD)
    w.issue(261, records=code_approved(), card=OLD_CARD)
    w.pr(262, 261, card=OLD_CARD)
    w.place("issue", 57, "Review", NEEDS)
    w.place("issue", 71, "Work")
    w.place("issue", 312, "Backlog")
    w.place("issue", 246, "Review")
    w.place("pr", 260, "Review", NEEDS)
    w.place("issue", 261, "Review", NEEDS)
    code, lines = run(w, capsys)
    assert code == 1 and named(lines, "issue", 57) and named(lines, "issue", 71), \
        f"333.4: the scan did not name the wrong cards it was given (exit {code}): {lines}"
    assert not w.writes, f"333.4: the scan changed what it checks: {w.writes}"


# 333.5: a card the scan cannot read is named, and the scan fails

def test_a_card_the_scan_cannot_read_is_named_and_the_scan_fails(world, capsys, record_property):
    """A card GitHub will not give is named as unread, and the scan exits 1.

    Proves 333.5.
    #63 sits in Plan and GitHub answers HTTP 502 for anything about it; #71 has no record and sits in Plan; #76 has no
    record and sits in Backlog. The scan must name #63 with GitHub's reason (502), still name #71, not name #76, and
    exit 1, never saying all cards match."""
    record_property("proves", "333.5")
    need_scan("333.5")
    w = world
    for n in (63, 71, 76):
        w.issue(n)
    w.place("issue", 63, "Plan")
    w.place("issue", 71, "Plan")
    w.place("issue", 76, "Backlog")
    make_true(w, ("issue", 71), ("issue", 76))
    w.issues[63]["body"] = OLD_CARD
    w.refused.add(63)
    code, lines = run(w, capsys)
    got = named(lines, "issue", 63)
    assert got and any("502" in x for x in got), f"333.5: the scan did not name #63 with GitHub's reason: {lines}"
    assert named(lines, "issue", 71), f"333.5: one unreadable card stopped the scan naming #71: {lines}"
    assert not named(lines, "issue", 76), f"333.5: the scan named #76, which matches its state: {lines}"
    assert not any("match their state" in x for x in lines), f"333.5: the scan said all cards match though #63 was unread: {lines}"
    assert code == 1, f"333.5: the scan exited {code} with an unread card, not 1"


def test_a_scan_that_reads_every_card_does_not_fail_for_it(world, capsys, record_property):
    """Beside the unread card: the same board with #63 readable and true passes.

    Proves 333.5.
    #63 (no record, in Backlog) and #76 (no record, in Backlog), both bodies the card Dokima draws now. The scan must
    say all 2 cards match and exit 0."""
    record_property("proves", "333.5")
    need_scan("333.5")
    w = world
    for n in (63, 76):
        w.issue(n)
        w.place("issue", n, "Backlog")
    make_true(w, ("issue", 63), ("issue", 76))
    code, lines = run(w, capsys)
    assert "All 2 cards on the board match their state." in lines and code == 0, \
        f"333.5: a board of two true cards gave exit {code}: {lines}"


# 333.2: the PR cards of #246 and #312 pass only when they show Merged with every check passed

def test_the_owners_two_pr_cards_pass_only_showing_merged_with_every_check_passed(world, capsys, record_property):
    """PR cards of #246 and #312 pass only showing Merged with every check passed.

    Proves 333.2. Closed #246 with merged PR #260 and closed #312 with merged PR #314, every check passed, all four in
    Done with no pill and both issue cards true. First PR #260 still shows its old open card and PR #314 holds no card,
    as on GitHub today: the scan must name both PRs and exit 1. Then both PR bodies get the card Dokima draws now: each
    says Merged with All tests passed (shown as Test suite, as on the approved card of #557), and the scan says all 4
    cards match and exits 0."""
    record_property("proves", "333.2")
    need_scan("333.2")
    w = world
    for issue, pr in ((246, 260), (312, 314)):
        w.issue(issue, state="closed", records=code_approved())
        w.pr(pr, issue, state="MERGED", card=OLD_CARD if pr == 260 else None)
        w.place("issue", issue, "Done")
        w.place("pr", pr, "Done")
    make_true(w, ("issue", 246), ("issue", 312))
    code, lines = run(w, capsys)
    missing = [p for p in (260, 314) if not named(lines, "pr", p)]
    assert not missing and code == 1, \
        f"333.2: PR cards not showing Merged were not named: {missing} (exit {code}): {lines}"
    make_true(w, ("pr", 260), ("pr", 314))
    for p in (260, 314):
        shown = w.prs[p]["body"]
        assert "**Merged**" in shown and re.search(r'alt="passed"></a> Test suite', shown), \
            f"333.2: PR #{p}'s true card does not show Merged with All tests passed: {shown}"
    code, lines = run(w, capsys)
    assert "All 4 cards on the board match their state." in lines and code == 0, \
        f"333.2: with both PR cards showing Merged the scan gave exit {code}: {lines}"

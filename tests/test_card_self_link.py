"""The issue card drops its self-link; a PR closes its issue by full address.

Issue #452, story 1 of #416. On the issue's own page GitHub shortens a link to that same page to a bare #N, and it
adds nothing there, so the issue's card leaves it out of its top row; the PR's card keeps it. At the bottom of a PR,
`Closes #N` shows as a bare #N, while `Closes https://github.com/o/r/issues/N` still closes the issue (the owner
tested it on dokima-dev/card-gallery), so the PR's description ends with that line, and it is the only closing
reference in it.

How the tests reach the code:
- card.render(repo, issue, found, page="issue" | "pr") draws the card for either page; its top row is the line that
  links the latest run, or, with no run, the one that links the PR.
- card.draw(repo, number, pr_number) saves the issue's card and writes the PR's description, with GitHub faked by
  tests/test_body.py's recorder.
- card.pr_body(card, text, ask, issue_url=...) builds the PR's description: the PR's card, the owner's Original issue
  fold, then the closing line by the issue's full address `issue_url`.
- agent.issue_of_pr(head, body) and board.issue_of read which issue a PR was built for; scan.card_now and scan.main
  compare cards with the ones Dokima draws now, faked by tests/test_scan.py's World.
"""
import os
import re
import sys


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dokima import agent, board, body, card, plan  # noqa: E402
from test_body import github, text_of  # noqa: E402,F401
from test_scan import (REPO as SCAN_REPO, World, code_approved, fake_board, fake_gh, make_true, named,  # noqa: E402,F401
                       need_scan, run, scan, world)

REPO = "o/r"
URL = "https://github.com/o/r/issues/40"
PR_URL = "https://github.com/o/r/pull/5"
FILES = "https://github.com/o/r/pull/5/files"
RUN = "https://github.com/o/r/actions/runs/1"
ISSUE = {"number": 40, "title": "t", "url": URL}
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": PR_URL, "merged_by": None,
      "head": {"sha": "abc", "ref": "try/issue-40"}}
MERGED = dict(PR, merged=True, state="closed", merged_by={"login": "boss"})
WORKER = {"status": "completed", "conclusion": "success", "html_url": RUN}
PLAN = {"kind": "user_story", "summary": "Cards link what matters.", "user_story": "The owner sees one card.",
        "acceptance_criteria": [{"text": "The card shows its links.", "source": URL}], "non_functional": [],
        "scope": ["dokima/card.py"], "out_of_scope": [], "tests": {}}
RECS = [{"role": "planner", "stage": None, "handback": PLAN, "check": {"passed": True, "problems": []},
         "run": "https://github.com/o/r/actions/runs/8"}]
# Every closing reference GitHub reads: a keyword, an optional colon, then #N, owner/repo#N or an issue's full address.
CLOSING = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+(?:(?:[\w.-]+/[\w.-]+)?#\d+"
                     r"|https://github\.com/[\w.-]+/[\w.-]+/issues/\d+)", re.I)


def found(**kw):
    """What the card is drawn from: a plan, an open PR and a run.

    Any of them can be replaced through `kw`."""
    return dict({"recs": RECS, "pr": PR, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": {},
                 "worker": WORKER, "children": []}, **kw)


def top_row(text, repo=REPO):
    """The card's top row: the line opening with the latest run, an issue or a PR.

    None when the card has no such line."""
    for line in (text or "").splitlines():
        first = line.split(" · ")[0].strip()
        if first.startswith("[latest run](") or re.fullmatch(rf"https://github\.com/{re.escape(repo)}/(?:issues|pull)/\d+", first):
            return line
    return None


def bare(row, url):
    """True when the URL stands alone as one item of the row."""
    return url in [part.strip() for part in row.split(" · ")]


def draw(monkeypatch, github, pr, current="My ask.", pr_text="Closes #40", worker=WORKER, changed_only=False):
    """Run card.draw on issue 40 and its PR 5 against a faked GitHub.

    Returns (the issue body saved, the PR description written), each None when not written."""
    issue = dict(ISSUE, approved_at=None, changes=[], plan=None, current_body=current, body=current)
    pr = dict(pr, body=pr_text) if pr else None
    monkeypatch.setattr(card.plan, "fetch_issue", lambda repo, n: issue)
    monkeypatch.setattr(card, "gather", lambda repo, n, p: found(pr=pr, worker=worker))
    monkeypatch.setattr(card, "github_links", lambda repo, n, cache: {"blocked_by": [], "blocks": [], "loop": []})
    monkeypatch.setattr(card, "their_links", lambda *a, **k: {"relates_to": []})
    saves, calls = len(github.saves), len(github.calls)
    card.draw(REPO, 40, pr["number"] if pr else None, changed_only=changed_only)
    written = [text_of(c, {}) for c in github.calls[calls:] if "PATCH" in c and any(str(a).endswith("pulls/5") for a in c)]
    return (github.saves[-1] if len(github.saves) > saves else None), (written[-1] if written else None)


def card_part(text):
    """The card between its two markers, markers included."""
    assert text and plan.CARD_START in text and plan.CARD_END in text, f"the text holds no card: {text!r}"
    return text[text.index(plan.CARD_START):text.index(plan.CARD_END) + len(plan.CARD_END)]


# 452.1: on the issue's own page, the card's top row leaves out the link to that issue

def test_the_issue_cards_top_row_leaves_out_its_own_link(record_property):
    """The issue's card no longer links to itself; the run, PR and files changed stay.

    Proves 452.1. Draws the issue's card with an open PR and a finished run, and checks its top row reads exactly the latest run,
    the PR written out bare, then files changed, with no link to issue #40 and no #40 in any form; with no PR the
    row is the latest run alone, and with no PR and no run the card has no top row at all."""
    record_property("proves", "452.1")
    text = card.render(REPO, ISSUE, found(), page="issue")
    row = top_row(text)
    assert row is not None, f"452.1: the issue card has no top row:\n{text}"
    assert URL not in row and not re.search(r"#40\b", row), f"452.1: the issue card's top row still links issue #40 itself: {row}"
    plain = re.sub(r"<img [^>]*>\s*", "", row)
    assert plain == f"[latest run]({RUN}) · {PR_URL} · [files changed]({FILES})", \
        f"452.1: the issue card's top row should be the latest run, PR #5 and files changed, and nothing else: {plain}"
    alone = top_row(card.render(REPO, ISSUE, found(pr=None), page="issue"))
    assert alone == f"[latest run]({RUN})", f"452.1: with no PR the issue card's top row should be the latest run alone: {alone}"
    bare_card = card.render(REPO, ISSUE, found(pr=None, worker=None), page="issue")
    assert top_row(bare_card) is None, \
        f"452.1: with no PR and no run the issue card should have no top row, it has: {top_row(bare_card)}"


def test_drawing_the_card_saves_the_issue_card_without_its_own_link(record_property, monkeypatch, github):
    """Redrawing the card saves an issue card with no link to the issue itself.

    Proves 452.1. Runs the card's draw on issue #40 with its PR open, then merged, and checks the card saved on the issue has a top
    row that keeps the latest run, PR #5 and files changed, but not issue #40's own address."""
    record_property("proves", "452.1")
    for pr in (PR, MERGED):
        saved, _ = draw(monkeypatch, github, pr)
        assert saved is not None, "452.1: the card saved nothing on the issue"
        row = top_row(card_part(saved))
        assert row is not None, f"452.1: the saved issue card has no top row:\n{saved}"
        assert not bare(row, URL) and URL not in row, f"452.1: the saved issue card's top row links issue #40 itself: {row}"
        for kept in (f"[latest run]({RUN})", PR_URL, f"[files changed]({FILES})"):
            assert kept in row, f"452.1: the saved issue card's top row lost {kept}: {row}"


# 452.2: on the PR, the top row still links the issue, and the rest of the card is the same as on the issue

def test_the_pr_card_is_the_issue_card_plus_the_issues_link(record_property, monkeypatch, github):
    """The PR shows the issue's very card, with only the issue's link added.

    Proves 452.2. Draws the PR's card and checks its top row reads exactly the latest run, issue #40's full address, PR #5, then
    files changed. Then runs the card's draw on issue #40 with its PR open, then merged, and checks the card on the PR
    differs from the one saved on the issue in exactly one line, the top row, and that line is the issue's row with
    issue #40's full address added right after the latest run."""
    record_property("proves", "452.2")
    row = top_row(card.render(REPO, ISSUE, found(), page="pr"))
    plain = re.sub(r"<img [^>]*>\s*", "", row or "")
    assert plain == f"[latest run]({RUN}) · {URL} · {PR_URL} · [files changed]({FILES})", \
        f"452.2: the PR card's top row should link the latest run, issue #40, PR #5 and files changed: {plain}"
    for pr in (PR, MERGED):
        saved, written = draw(monkeypatch, github, pr)
        assert saved and written, "452.2: the card was not written on both the issue and the PR"
        a, b = card_part(saved).splitlines(), card_part(written).splitlines()
        assert len(a) == len(b), f"452.2: the issue and PR cards have different lengths:\n{a}\n---\n{b}"
        differ = [(x, y) for x, y in zip(a, b) if x != y]
        assert len(differ) == 1, f"452.2: the issue and PR cards should differ only in their top row, they differ in: {differ}"
        x, y = differ[0]
        assert x == top_row(card_part(saved)) and y == top_row(card_part(written)), \
            f"452.2: the line that differs is not the top row: {differ}"
        assert y == x.replace(f"[latest run]({RUN}) · ", f"[latest run]({RUN}) · {URL} · ", 1) and URL in y, \
            f"452.2: the PR's top row should be the issue's with issue #40 added after the latest run: {x} vs {y}"


# 452.3: the PR's description ends with Closes and the issue's full address, its only closing reference

def test_the_pr_issue_is_read_from_the_closing_line_by_full_address_or_number(record_property):
    """Dokima reads a PR's issue from its closing line, by full address or #N.

    Proves 452.5. With no branch to read it from, checks agent.issue_of_pr and board.issue_of find issue 77 from Closes with
    issue #77's full address and from Closes #77, find issue 40 from a description the card code built for an ask
    full of the owner's own closing words, and still prefer the branch when it names the issue."""
    record_property("proves", "452.5")
    for text in ("Closes https://github.com/o/r/issues/77", "Closes #77", "card\n\nCloses https://github.com/o/r/issues/77\n"):
        got = agent.issue_of_pr("", text)
        assert str(got) == "77", f"452.5: Dokima read issue {got!r}, not 77, from the closing line {text!r}"
        got = board.issue_of(REPO, 5, head="", body=text)
        assert got == 77, f"452.5: the board read issue {got!r}, not 77, from the closing line {text!r}"
    assert str(agent.issue_of_pr("try/issue-12", "Closes https://github.com/o/r/issues/77")) == "12", \
        "452.5: the branch no longer comes first when it names the issue"
    assert agent.issue_of_pr("", "See https://github.com/o/r/issues/77 for more.") is None, \
        "452.5: Dokima read an issue from a full address no closing keyword names"


# 452.6: the board scan expects the issue's card without its own link, the PR's with it and the full-address line

def test_the_scan_expects_the_issue_card_without_its_link_and_the_pr_card_with_it(world, capsys, record_property):
    """The scan expects the issue's card without its own link, the PR's with it.

    Proves 452.6. The PR's must also close by full address. Open #73 with an approved code review and its open PR #74, in the right columns. The cards the scan expects: #73's
    top row has no link to #73, PR #74's has it. Each body the card Dokima draws now: the scan names neither. Then each
    wrong in one way: #73 showing the PR's card, PR #74 showing the issue's card, PR #74 closing by #73 instead of its
    full address. The scan names each, and exits 1."""
    record_property("proves", "452.6")
    need_scan("452.6")
    w, url = world, "https://github.com/o/r/issues/73"
    w.issue(73, records=code_approved())
    w.pr(74, 73)
    w.place("issue", 73, "Review", "Needs you")
    w.place("pr", 74, "Review", "Needs you")
    issue_card, pr_card = scan.card_now(SCAN_REPO, "issue", 73), scan.card_now(SCAN_REPO, "pr", 74)
    assert top_row(issue_card) and url not in top_row(issue_card), \
        f"452.6: the scan expects #73's card to link #73 itself: {top_row(issue_card)}"
    assert url in (top_row(pr_card) or ""), f"452.6: the scan expects PR #74's card without its link to #73: {top_row(pr_card)}"
    make_true(w, ("issue", 73), ("pr", 74))
    good_issue, good_pr = w.issues[73]["body"], w.prs[74]["body"]
    code, lines = run(w, capsys)
    assert not named(lines, "issue", 73) and not named(lines, "pr", 74), \
        f"452.6: the scan named cards that show what Dokima draws now: {lines}"
    assert code == 0, f"452.6: with every card true the scan exited {code}: {lines}"
    ask = body.ask(good_issue)
    wrong = [("issue", 73, body.redraw(good_issue, pr_card), good_pr),
             ("pr", 74, good_issue, card.pr_body(issue_card, "Closes #73", ask, issue_url=url)),
             ("pr", 74, good_issue, good_pr.rstrip()[:-len(f"Closes {url}")] + "Closes #73")]
    for kind, n, issue_text, pr_text in wrong:
        w.issues[73]["body"], w.prs[74]["body"] = issue_text, pr_text
        code, lines = run(w, capsys)
        assert named(lines, kind, n), f"452.6: {kind} #{n} shows a card the scan should call stale, but it was not named: {lines}"
        assert code == 1, f"452.6: the scan named a stale card but exited {code}"

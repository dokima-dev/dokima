"""Cards are rewritten only when they change (#534, story 2 of #380).

GitHub's GraphQL budget (5,000 calls an hour, shared by every Dokima workflow) ran out on 2026-10-09, and card.yml
used about a fifth of it. The owner asked on #380: "Same rule for card.yml where it applies: a card is redrawn only
when something it shows changed."

card.yml keeps running on every event, because GitHub sends no event for a blocked-by link a person adds by hand and
the card must still show it at once. What changes is the write: `card.main` saves the issue's card, and writes the
pull request's description, only when what code draws now differs from what is there. Until now that held only when
the bot's own change started the run (card.yml sets `BY_BOT`); a person's comment or change rewrote both every time.

These tests run `card.main` as card.yml runs it for a person's change (`BY_BOT` "false" or unset), with GitHub faked
by tests/test_body.py's recorder, and count the writes it makes.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dokima import card  # noqa: E402
from test_body import github, text_of  # noqa: E402,F401
from test_card_self_link import ISSUE, PR, found  # noqa: E402

REPO = "o/r"


def run(monkeypatch, github, issue_text, pr_text, by_bot):
    """Run `card.main` on issue 40 and PR 5; return (issue saved, PR written).

    Each is the text written, or None when nothing was written. `by_bot` is card.yml's BY_BOT, None for unset."""
    issue = dict(ISSUE, approved_at=None, changes=[], plan=None, current_body=issue_text, body=issue_text)
    pr = dict(PR, body=pr_text)
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.delenv("BY_BOT", raising=False)
    if by_bot is not None:
        monkeypatch.setenv("BY_BOT", by_bot)
    monkeypatch.setattr(card, "find_work", lambda repo: (40, 5))
    monkeypatch.setattr(card, "follow", lambda *a, **k: 0)
    monkeypatch.setattr(card.plan, "fetch_issue", lambda repo, n: issue)
    monkeypatch.setattr(card, "gather", lambda repo, n, p: found(pr=pr))
    monkeypatch.setattr(card, "github_links", lambda repo, n, cache: {"blocked_by": [], "blocks": [], "loop": []})
    monkeypatch.setattr(card, "their_links", lambda *a, **k: {"relates_to": []})
    saves, calls = len(github.saves), len(github.calls)
    card.main()
    written = [text_of(c, {}) for c in github.calls[calls:] if "PATCH" in c and any(a.endswith("pulls/5") for a in c)]
    return (github.saves[-1] if len(github.saves) > saves else None), (written[-1] if written else None)


def test_a_card_is_written_only_when_what_code_draws_differs(record_property, monkeypatch, github):
    """A person's change rewrites neither card when both already show what code draws.

    Proves 534.1. First draws the cards of issue 40 and its PR 5 from a fresh ask, which must write both. Then, for a
    person's change (card.yml's BY_BOT "false", and unset), runs the card again on those very bodies: nothing may be
    written. Then makes only the issue's card stale, which must rewrite the issue alone, and only the PR's
    description stale, which must rewrite the PR alone."""
    record_property("proves", "534.1")
    issue_now, pr_now = run(monkeypatch, github, "My ask.", "Closes #40", "false")
    assert issue_now is not None, "534.1: a fresh ask with no card got no card written"
    assert pr_now is not None, "534.1: a PR with no card got no card written"
    for by_bot in ("false", None):
        who = "BY_BOT unset" if by_bot is None else f"BY_BOT={by_bot}"
        issue_w, pr_w = run(monkeypatch, github, issue_now, pr_now, by_bot)
        assert issue_w is None, f"534.1: a person's change ({who}) rewrote the issue's card, though it already showed what code draws"
        assert pr_w is None, f"534.1: a person's change ({who}) rewrote the PR's card, though it already showed what code draws"
    stale = issue_now.replace(card.plan.CARD_START, card.plan.CARD_START + "\nAn older line.", 1)
    issue_w, pr_w = run(monkeypatch, github, stale, pr_now, "false")
    assert issue_w == issue_now, "534.1: the issue's card was stale and was not rewritten to what code draws"
    assert pr_w is None, "534.1: only the issue's card was stale, yet the PR's card was rewritten"
    issue_w, pr_w = run(monkeypatch, github, issue_now, pr_now + "\nAn older line.", "false")
    assert issue_w is None, "534.1: only the PR's card was stale, yet the issue's card was rewritten"
    assert pr_w == pr_now, "534.1: the PR's card was stale and was not rewritten to what code draws"

"""Name every card on the board that does not match its issue's state now (#333).

    DOKIMA_BOARD=org/number REPO=owner/name python3 -m dokima.scan

One line for each closed card outside Done or with a pill, each open card in the wrong column (or in none), each issue
or PR card that does not show the card Dokima draws for its issue now, and each card GitHub will not give, then exit 1.
When every card matches, it says so and exits 0. It only reads: it never moves a card, sets a pill or edits a body.
The column comes from dokima.board's rules and the card from dokima.card's, as they are.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import board, body, card, plan  # noqa: E402

UNREAD = (subprocess.CalledProcessError, RuntimeError, ValueError, KeyError, TypeError, AttributeError)


def label(kind, n):
    return f"issue #{n}" if kind == "issue" else f"PR #{n}"


def drawn(repo, number, pr_number):
    """(issue, everything gathered, card) as dokima.card.draw would write it on issue `number` now, without saving."""
    issue = plan.fetch_issue(repo, number)
    found = card.gather(repo, number, pr_number)
    found["sources"] = card.linked_from(issue["current_body"])
    cache = {}
    now = card.github_links(repo, int(number), cache)
    found["blocking"] = now
    if now.get("unread"):
        found["unread"] = card.reason(card.blocking(repo, int(number), cache))
    found["linked"] = {"relates_to": card.their_links(repo, number, found["sources"])["relates_to"],
                       "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
    return issue, found, card.render(repo, issue, found)


def card_now(repo, kind, number):
    """The card Dokima writes on this issue or PR when redrawing its issue now."""
    if kind == "issue":
        return drawn(repo, number, card.issue_pr(repo, number))[2]
    issue, found, _ = drawn(repo, board.issue_of(repo, number), number)
    return card.render(repo, issue, found, page="pr")


def why(e):
    return str(e) if isinstance(e, RuntimeError) else card.reason(e)


def check(b, repo, owners, c, places):
    """The lines naming what is wrong with one card; [] when it matches its state."""
    kind, n, status, action = c["kind"], c["number"], c.get("status"), c.get("action")
    shown = (status or "no column") + (f" with {action}" if action else "")
    out = []
    if c["closed"] and (status, action) != board.DONE:
        out.append(f"{label(kind, n)} is closed but sits in {shown}; it belongs in Done with no pill.")
    issue = n if kind == "issue" else board.issue_of(repo, n)
    if not issue:
        return out
    if issue not in places:
        closed = b.state("issue", issue) == "closed"
        column = board.DONE[0] if closed else board.where(repo, owners, issue, b.autopilot("issue", issue))[0]
        pr = n if kind == "pr" else card.issue_pr(repo, issue)
        places[issue] = (column, pr, drawn(repo, issue, pr))
    column, pr, (got, found, top) = places[issue]
    if kind == "pr" and pr != n:
        got, found, top = drawn(repo, issue, n)
    if not c["closed"] and status != column:
        out.append(f"{label(kind, n)} sits in {status or 'no column'} but its state puts it in {column}.")
    if kind == "issue":
        stale = not card.shows(got["current_body"] or "", top)
    else:
        # The PR's card also links its issue, and closes it by the issue's full address (#452).
        current = (found["pr"] or {}).get("body") or ""
        top = card.render(repo, got, found, page="pr")
        stale = card.pr_body(top, current, body.ask(got["current_body"]), issue_url=got["url"]) != current
    if stale:
        out.append(f"{label(kind, n)} does not show the card Dokima draws for it now.")
    return out


def main():
    spec, repo = os.environ.get("DOKIMA_BOARD", "").strip(), (os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY") or "").strip()
    if not spec or not repo:
        print("Set DOKIMA_BOARD (org/number or user:login/number) and REPO (owner/name) to say which board and repo to scan.")
        return 1
    try:
        b = board.Board(spec, repo)
        cards = b.cards()
    except UNREAD as e:
        print(f"GitHub would not give the cards of board {spec} ({why(e)}), so nothing was checked.")
        return 1
    owners, places, wrong = plan.repo_approvers(repo.split("/")[0]), {}, 0
    for c in cards:
        try:
            lines = check(b, repo, owners, c, places)
        except UNREAD as e:
            lines = [f"{label(c['kind'], c['number'])} could not be checked: GitHub would not give its state ({why(e)})."]
        for line in lines:
            print(line)
        wrong += bool(lines)
    if wrong:
        print(f"{wrong} of {len(cards)} cards on the board are wrong.")
        return 1
    print(f"All {len(cards)} cards on the board match their state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

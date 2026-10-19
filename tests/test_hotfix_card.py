"""A hotfix's card is one line with its state, ask, pull request, verdict and gate.

Issue #864.

Each test runs the card's own draw (dokima/card.py draw) on issue #57 of repo o/r, labeled hotfix and never planned,
with GitHub faked: the issue's text is the owner's ask, the issue carries the hotfix label on every read (GraphQL,
REST and gh), and what the card is drawn from (records, comments, pull request #60) is given. The card saved on the
issue is the part between the card's markers; its lines are read with hidden comment lines and blank lines left out.

The line's words are read loosely, so the code may dress them: the review verdict as "code review" then "approved"
or "blocked", the gate as "merge gate" then "passed" or "failed", with only punctuation or spaces between.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent, agent_github, body, card, plan  # noqa: E402
from dokima.agent_records import GATE_FAILED  # noqa: E402

REPO = "o/r"
N = 57
PR = 60
HOTFIX = "hotfix"
ASK = "The page title says Dokma; make it say Dokima."
URL = f"https://github.com/{REPO}/issues/{N}"
PR_URL = f"https://github.com/{REPO}/pull/{PR}"
GATE_PASSED = "All tests passed with main's newest commit. Approve the pull request on GitHub to merge it."
REVIEW = re.compile(r"code review\W*(approved|blocked)", re.I)
GATE = re.compile(r"merge gate\W*(passed|failed)", re.I)


def rec(role, stage=None, **handback):
    """A passed record of `role` at `stage`, the way the workflow writes one."""
    return {"role": role, "stage": stage, "run_id": "3", "run": f"https://github.com/{REPO}/actions/runs/3",
            "models": ["claude-opus-5-5"], "handback": handback, "check": {"passed": True, "problems": []}}


def posted(r, t, nxt=""):
    """The bot's comment carrying record `r`, with its Next line when given."""
    return {"author": {"login": agent.BOT}, "body": agent.render(r) + (f"\n\n**Next:** {nxt}" if nxt else ""),
            "createdAt": t, "url": f"{URL}#issuecomment-{len(t)}"}


WORKED = rec("worker", summary="Fixed the page title.", criteria={"ask": "`app.py` now says Dokima."},
             evidence="pytest -q: 2 passed", raises=[], answers=[])
APPROVED = rec("reviewer", "pr", verdict="approve", summary="The fix does exactly what the issue asks.", raises=[],
               answers=[], previous_step={"did": ["Fixed the title."], "decided": [], "open": []}, round=1)
BLOCKED = rec("reviewer", "pr", verdict="block", summary="The fix misses one file.", answers=[],
              raises=[{"kind": "blocker", "to": "worker", "label": "Missed", "text": "The footer still says Dokma.",
                       "evidence": "`footer.py`"}],
              previous_step={"did": ["Fixed the title."], "decided": [], "open": []}, round=1)


def comments(*review, nxt=""):
    """The issue's comments: the worker's record, then the code review given, with its Next line."""
    out = [posted(WORKED, "2026-10-18T10:00:00Z")]
    for r in review:
        out.append(posted(r, "2026-10-18T11:00:00Z", nxt))
    return out


def draw(monkeypatch, tmp_path, items=None, pr=True, labels=(HOTFIX,), ask=ASK, blocks=()):
    """Draw #57's card; return its lines, the saved body and what it was drawn from.

    `items` are the issue's comments, `pr` whether pull request #60 is open, `labels` the issue's labels, `ask` the
    issue's current body and `blocks` the issues #57 blocks on GitHub."""
    monkeypatch.chdir(tmp_path)
    items = comments() if items is None else items
    names = [{"name": l} for l in labels]
    issue = {"number": N, "title": "Page title typo", "url": URL, "body": ask, "current_body": ask,
             "labels": names, "state": "OPEN"}
    head = {"sha": "ab" * 20, "ref": f"try/issue-{N}"}
    pull = {"number": PR, "merged": False, "state": "open", "body": f"Closes #{N}", "html_url": PR_URL,
            "head": head, "merged_by": None, "labels": names} if pr else None
    found = {"recs": agent.records(items), "items": items, "pr": pull, "check_runs": [], "reviews": [],
             "owners": {"boss"}, "tests": {}, "children": [], "worker": None}

    def fake(*args, **kw):
        a = [str(x) for x in args]
        joined = " ".join(a)
        if a[:2] == ["issue", "view"]:
            return json.dumps(issue)
        if "graphql" in a:
            return json.dumps({"data": {"repository": {"issue": issue, "pullRequest": {
                "closingIssuesReferences": {"nodes": [{"number": N}]}, "labels": {"nodes": names}}}}})
        if re.search(rf"repos/{REPO}/issues/{N}/labels", joined):
            return json.dumps(names)
        if re.search(rf"repos/{REPO}/issues/{N}(\s|$|\?)", joined):
            return json.dumps({**issue, "state": "open"})
        return "[]" if "--paginate" in a or "pulls?" in joined else "{}"

    saved = []
    monkeypatch.setattr(plan, "fetch_issue", lambda repo, n: dict(issue))
    monkeypatch.setattr(card, "gather", lambda repo, n, p: dict(found))
    monkeypatch.setattr(card, "github_links", lambda repo, n, cache: {"blocked_by": [], "blocks": list(blocks), "loop": []})
    monkeypatch.setattr(card, "their_links", lambda *a, **k: {"relates_to": []})
    monkeypatch.setattr(card, "required_rows", lambda *a, **k: [])
    monkeypatch.setattr(card, "gh", fake)
    monkeypatch.setattr(agent_github, "gh", fake)
    monkeypatch.setattr(body, "gh", fake, raising=False)
    monkeypatch.setattr(body, "save", lambda repo, n, current, top: saved.append(body.redraw(current, top)) or True)
    card.draw(REPO, N, PR if pr else None)
    assert saved, "the card saved nothing on the issue"
    whole = saved[-1]
    inside = whole.split(plan.CARD_START, 1)[1].split(plan.CARD_END, 1)[0]
    return card_lines(inside), whole, found


def card_lines(text):
    """The card's lines in `text`, hidden comment lines and blank lines left out."""
    return [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("<!--")]


def pr_card(tmp_path):
    """The card's lines on pull request #60, as the last draw wrote them.

    None when the draw wrote no description."""
    path = tmp_path / "pr.md"
    if not path.exists():
        return None
    text = path.read_text()
    return card_lines(text.split(body.MARKER, 1)[0].split(plan.CARD_START, 1)[-1].split(plan.CARD_END, 1)[0])


def ask_line(lines, k):
    """The one card line holding the ask, failing naming criterion k when there is none."""
    held = [l for l in lines if "Dokma" in l]
    assert held, f"{k}: no card line shows the ask {ASK!r}: {lines}"
    return held[0]


def test_a_hotfix_card_shows_its_state_in_one_line(record_property, monkeypatch, tmp_path):
    """A hotfix's card is one line, and that line shows the issue's state.

    Proves 864.4. Draws #57's card, labeled hotfix, built by its worker with pull request #60 open. The card must
    hold exactly one line, and it must show the stage the card's own status gives (as the board shows it); the copy on #60 is one line too. A hotfix
    that blocks another issue on GitHub still shows one line. Beside it, the same issue without the hotfix label is
    drawn as today's card, with more than one line."""
    record_property("proves", "864.4")
    lines, _, found = draw(monkeypatch, tmp_path)
    assert len(lines) == 1, f"864.4: the hotfix card is not one line: {lines}"
    stage = card.status({"number": N}, found)[0]
    assert stage in lines[0], f"864.4: the hotfix card's line does not show its state {stage!r}: {lines[0]!r}"
    on_pr = pr_card(tmp_path)
    assert on_pr is not None and len(on_pr) == 1, f"864.4: the hotfix card on pull request #{PR} is not one line: {on_pr}"
    blocking, _, _ = draw(monkeypatch, tmp_path, blocks=[50])
    assert len(blocking) == 1, f"864.4: a hotfix that blocks #50 has a card of more than one line: {blocking}"
    plain, _, _ = draw(monkeypatch, tmp_path, labels=())
    assert len(plain) > 1, f"864.4: an issue without the hotfix label lost its normal card: {plain}"


def test_a_hotfix_card_line_shows_the_ask(record_property, monkeypatch, tmp_path):
    """A hotfix's card line shows the owner's ask.

    Proves 864.5. Draws #57's card, labeled hotfix, its text the ask. The card's one line must carry the ask word for
    word. Drawn again on the body the first draw saved (the ask now folded below the card), the line still carries
    it. An ask written on two lines shows both lines' words in the one line."""
    record_property("proves", "864.5")
    lines, whole, _ = draw(monkeypatch, tmp_path)
    assert len(lines) == 1 and ASK in lines[0], f"864.5: the hotfix card's one line does not carry the ask {ASK!r}: {lines}"
    again, _, _ = draw(monkeypatch, tmp_path, ask=whole)
    assert len(again) == 1 and ASK in again[0], f"864.5: redrawn on its saved body, the card line lost the ask: {again}"
    two = "The page title says Dokma.\nMake it say Dokima."
    split, _, _ = draw(monkeypatch, tmp_path, ask=two)
    assert len(split) == 1 and "The page title says Dokma." in split[0] and "Make it say Dokima." in split[0], \
        f"864.5: an ask on two lines is not shown whole in the one card line: {split}"


def test_a_hotfix_card_line_links_its_pull_request(record_property, monkeypatch, tmp_path):
    """A hotfix's card line links its pull request.

    Proves 864.6. Draws #57's card with pull request #60 open: the line showing the ask must also link #60. Beside
    it, with no pull request yet, the card is still one line and links no pull request."""
    record_property("proves", "864.6")
    lines, _, _ = draw(monkeypatch, tmp_path)
    line = ask_line(lines, "864.6")
    assert PR_URL in line or f"#{PR}" in line, f"864.6: the hotfix card line does not link pull request #{PR}: {line!r}"
    none, _, _ = draw(monkeypatch, tmp_path, items=[], pr=False)
    assert len(none) == 1 and "/pull/" not in none[0], f"864.6: with no pull request the card links one, or is not one line: {none}"


def test_a_hotfix_card_line_shows_the_review_verdict(record_property, monkeypatch, tmp_path):
    """A hotfix's card line shows the code review's verdict.

    Proves 864.7. Draws #57's card after its code review approved it: the line showing the ask must say code review
    approved. After a code review that blocked it, the line says code review blocked. Before any code review, the
    line names no verdict."""
    record_property("proves", "864.7")
    lines, _, _ = draw(monkeypatch, tmp_path, items=comments(APPROVED))
    found = REVIEW.findall(ask_line(lines, "864.7"))
    assert [v.lower() for v in found] == ["approved"], f"864.7: an approved hotfix's card line does not say code review approved: {lines}"
    lines, _, _ = draw(monkeypatch, tmp_path, items=comments(BLOCKED))
    found = REVIEW.findall(ask_line(lines, "864.7"))
    assert [v.lower() for v in found] == ["blocked"], f"864.7: a blocked hotfix's card line does not say code review blocked: {lines}"
    lines, _, _ = draw(monkeypatch, tmp_path)
    assert not REVIEW.findall(ask_line(lines, "864.7")), f"864.7: before any code review the card line names a verdict: {lines}"


def test_a_hotfix_card_line_shows_the_gate_result(record_property, monkeypatch, tmp_path):
    """A hotfix's card line shows the merge gate's result.

    Proves 864.8. Draws #57's card after its code review approved it and the merge gate passed: the line showing the
    ask must say merge gate passed. After an approval whose merge gate failed, it says merge gate failed. Before the
    gate runs, the line names no gate result."""
    record_property("proves", "864.8")
    lines, _, _ = draw(monkeypatch, tmp_path, items=comments(APPROVED, nxt=GATE_PASSED))
    found = GATE.findall(ask_line(lines, "864.8"))
    assert [v.lower() for v in found] == ["passed"], f"864.8: a hotfix that passed the merge gate does not say so: {lines}"
    lines, _, _ = draw(monkeypatch, tmp_path, items=comments(APPROVED, nxt=f"{GATE_FAILED}: tests/test_app.py failed. The worker starts now."))
    found = GATE.findall(ask_line(lines, "864.8"))
    assert [v.lower() for v in found] == ["failed"], f"864.8: a hotfix that failed the merge gate does not say so: {lines}"
    lines, _, _ = draw(monkeypatch, tmp_path)
    assert not GATE.findall(ask_line(lines, "864.8")), f"864.8: before the gate ran the card line names a result: {lines}"

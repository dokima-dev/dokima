"""The issue card and the planner's run comment show the links, each with its icon.

Issue #251, story 2 of #231. The planner hands back `links`: three lists of open issue numbers, `blocked_by`, `blocks` and `relates_to` (#250).
This story draws them. Each kind with at least one link gets one line: its fixed field icon from card.FIELD_ICONS
("blocked by" -> blocked-by.svg, "blocks" -> blocks.svg, "related" -> related.svg, all added by #234), right in front
of its label (Blocked by, Blocks, Relates to), then its issue numbers as #N. A kind with no links has no line, and an
older plan with no links field draws exactly as one with three empty lists.

The issue card (dokima/card.py render, on the issue and on its pull request) draws them from the newest plan. The
planner's run comment no longer shows them: the owner keeps the links on the card at the top of the page (#236).
"""
import json
import os
import re
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

REPO = "o/r"
OWNER = "boss"
BOT = "dokima-runtime"
N = 251
ISSUE = {"number": N, "url": f"https://github.com/o/r/issues/{N}"}
SRC = f"https://github.com/o/r/issues/{N}"
LINKS = {"blocked_by": [12, 13], "blocks": [15], "relates_to": [18]}
NONE = {"blocked_by": [], "blocks": [], "relates_to": []}
# kind of link -> (its field, its label on the line)
KINDS = {"blocked_by": ("blocked by", "Blocked by"), "blocks": ("blocks", "Blocks"), "relates_to": ("related", "Relates to")}
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "Callers get a job id.",
         "acceptance_criteria": [{"text": "First thing works", "source": SRC}], "non_functional": [],
         "scope": ["app/jobs.py"], "out_of_scope": ["Retrying jobs."], "tests": {f"{N}.1": ["tests/test_a.py::test_one"]},
         "test_changes": {}}
SPLIT = {"kind": "feature", "summary": "Jobs, in two stories.", "feature": "Jobs.", "stories": [
    {"title": "A", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": SRC}], "non_functional": [],
     "depends_on": []},
    {"title": "B", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": SRC}], "non_functional": [],
     "depends_on": [0]}]}
PR = {"number": 5, "merged": False, "state": "open", "body": f"Closes #{N}"}
FOLD = re.compile(r"<details>.*?</details>", re.S)
# Each kind's own icon file in dokima/icons, fixed here so a changed icon map cannot move the test with it.
LINK_ICON = {"blocked by": "blocked-by", "blocks": "blocks", "related": "related"}
# The verdict and run icons, which no link line may carry.
VERDICT_ICONS = {"passed", "failed", "queued", "running", "cancelled", "none", *card.ICON_FILE.values()}
ICON_URL = re.compile(r"/dokima/icons/([\w-]+)\.svg")


def img(field):
    """The link kind's own icon exactly as the card draws it."""
    return card.icon(REPO, LINK_ICON[field], alt=field)


def with_links(plan, links):
    """The plan with these links, or with no links field at all when None."""
    return dict(plan, **({"links": links} if links is not None else {}))


def comment(login, body, i):
    """One comment of the conversation, as dokima.agent.conversation lists it."""
    return {"author": {"login": login}, "body": body, "createdAt": f"2026-10-08T{i:02d}:00:00Z", "where": f"issue #{N}"}


def rec(handback, n=1):
    """A planner record that passed its check."""
    return {"role": "planner", "stage": None, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}", "run_id": str(n)}


def draw(handbacks, page="issue"):
    """The card for #251 after these plans, oldest first, on the issue or its PR."""
    items = [comment(BOT, f"{agent.MARK}\n**Card**\n\n```json\n{json.dumps(rec(h, i))}\n```\n", i)
             for i, h in enumerate(handbacks, 1)]
    found = {"recs": agent.records(items), "items": items, "pr": PR if page == "pr" else None, "check_runs": [],
             "reviews": [], "owners": {OWNER}, "tests": {}, "worker": None, "children": []}
    return card.render(REPO, ISSUE, found, page=page)


def comment_for(handback):
    """The planner's run comment for this hand-back, built as the workflow does, folds removed."""
    out = tempfile.mkdtemp()
    json.dump(handback, open(os.path.join(out, agent.HANDBACK["planner"]), "w"))
    r = agent.build_record("planner", "", out, "", True, {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1"})
    r["models"], r["report"] = ["claude-opus-5-5"], {"duration_ms": 60000, "turns": 3, "tokens_in": 10, "tokens_out": 5,
                                                     "cost_usd": 0.1}
    return FOLD.sub("", agent.render(r))


def link_blocks(text):
    """Each link label of `text` with the bullets under it: (the label line and its bullets as one line, the raw lines).

    Since #416 each linked issue is a bullet of its own under its label, so GitHub shows its title."""
    icons = [img(f) for f, _ in KINDS.values()]
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        if any(c in lines[i] for c in icons):
            raw, j = [lines[i]], i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith("- ")):
                if lines[j].startswith("- "):
                    raw.append(lines[j])
                elif j + 1 < len(lines) and not lines[j + 1].startswith("- "):
                    break
                j += 1
            out.append((" ".join(raw), raw))
            i = j
        else:
            i += 1
    return out


def link_lines(text):
    """Every link label of `text`, with the bullets under it read as one line."""
    return [joined for joined, _ in link_blocks(text)]


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_RUN_ID", "1")


def without_link_lines(text):
    """`text` without its link lines and with blank runs collapsed.

    Used to compare a card that has links with one that has none."""
    raw = {l for _, ls in link_blocks(text) for l in ls}
    keep = [l for l in text.splitlines() if l not in raw]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(keep)).strip()


def check_lines(text, links, k, where):
    """Fail naming criterion k unless `text` shows one right line per kind with links."""
    lines = link_lines(text)
    shown = [kind for kind in KINDS if links.get(kind)]
    assert len(lines) == len(shown), \
        f"{k}: {where} shows {len(lines)} link lines, not one each for {shown}:\n" + "\n".join(lines or [text[:3000]])
    for kind in shown:
        field, label = KINDS[kind]
        pattern = re.compile(re.escape(img(field)) + r"\s*(?:\*\*|<b>)?\s*" + re.escape(label) + r"\b")
        mine = [l for l in lines if pattern.search(l)]
        assert len(mine) == 1, f"{k}: {where} has no line with the {field} icon right in front of “{label}”:\n" + "\n".join(lines)
        line = mine[0]
        others = [img(f) for kk, (f, _) in KINDS.items() if kk != kind]
        assert not any(o in line for o in others), f"{k}: {where}'s {label} line carries another kind's icon: {line}"
        files = ICON_URL.findall(line)
        assert files == [LINK_ICON[field]], \
            f"{k}: {where}'s {label} line draws the icons {files}, not only {LINK_ICON[field]}.svg: {line}"
        assert not VERDICT_ICONS & set(files), f"{k}: {where}'s {label} line carries a verdict or run icon: {line}"
        numbers = sorted(int(x) for x in re.findall(r"/issues/(\d+)\b", line))
        assert numbers == sorted(links[kind]), \
            f"{k}: {where}'s {label} line shows issues {numbers}, not exactly {sorted(links[kind])}: {line}"


def test_the_issue_card_shows_each_kind_of_link_on_its_own_line_with_its_own_icon(record_property):
    """The issue and PR card show each kind of link on its own line.

    Proves 251.1. Draws the card from a plan blocked by #12 and #13, blocking #15 and relating to #18, on the issue and on the pull
    request, for a plan and for a split: each kind is one line, its fixed icon right in front of its label, holding
    exactly its own issue numbers and no other kind's icon; each kind draws exactly its own file (blocked-by.svg,
    blocks.svg, related.svg), never a verdict or run icon such as passed, failed, queued, running or cancelled."""
    record_property("proves", "251.1")
    for field, name in LINK_ICON.items():
        assert os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "dokima", "icons", f"{name}.svg")), \
            f"251.1: the {field} icon dokima/icons/{name}.svg is missing"
    for plan in (STORY, SPLIT):
        for page in ("issue", "pr"):
            check_lines(draw([with_links(plan, LINKS)], page), LINKS, "251.1", f"the {page} card of a {plan['kind']}")


def test_the_issue_card_shows_no_line_for_a_kind_with_no_links(record_property):
    """A kind with no links has no line on the card; older plans draw unchanged.

    Proves 251.1. Draws the card from a plan that only blocks #15 (only the Blocks line), only relates to #18 (only Relates to) and
    is only blocked by #12 (only Blocked by); then from three empty lists and from a plan with no links field: neither
    shows a link line or label, both still show the plan, and they are drawn exactly alike; and the card of a plan with
    links, its link lines taken out, is exactly the card of the plan with no links field, so nothing else is added."""
    record_property("proves", "251.1")
    for kind, n in (("blocks", 15), ("relates_to", 18), ("blocked_by", 12)):
        links = dict(NONE, **{kind: [n]})
        for page in ("issue", "pr"):
            check_lines(draw([with_links(STORY, links)], page), links, "251.1", f"the {page} card of a plan with only {kind}")
    for page in ("issue", "pr"):
        empty, old = draw([with_links(STORY, NONE)], page), draw([with_links(STORY, None)], page)
        for name, text in (("three empty lists", empty), ("no links field", old)):
            assert "First thing works" in text, f"251.1: the {page} card of a plan with {name} no longer shows the plan:\n{text}"
            assert not link_lines(text), f"251.1: the {page} card of a plan with {name} shows link lines: {link_lines(text)}"
            for label in ("Blocked by", "Relates to"):
                assert label not in text, f"251.1: the {page} card of a plan with {name} says {label}:\n{text}"
        assert empty == old, f"251.1: on the {page} card a plan with no links field draws unlike one with no links"
        full = draw([with_links(STORY, LINKS)], page)
        assert link_lines(full) and without_link_lines(full) == without_link_lines(old), \
            (f"251.1: on the {page} card the link lines are not the only difference from a plan with no links field:\n"
             f"{without_link_lines(full)}\n---\n{without_link_lines(old)}")


def test_the_issue_card_shows_the_links_of_the_newest_plan(record_property):
    """When the planner re-plans, the card shows only the newest plan's links.

    Proves 251.1. Draws the card after two plans, the first blocking #15, the newer relating to #18: the card shows the Relates to
    line with #18 and nothing of the older plan's Blocks line or #15."""
    record_property("proves", "251.1")
    older, newer = dict(NONE, blocks=[15]), dict(NONE, relates_to=[18])
    for page in ("issue", "pr"):
        text = draw([with_links(STORY, older), with_links(STORY, newer)], page)
        check_lines(text, newer, "251.1", f"the {page} card after a re-plan")
        assert not re.search(r"#15\b", text), f"251.1: the {page} card still shows the older plan's link to #15:\n{text}"

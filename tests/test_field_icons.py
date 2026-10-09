"""Every field on a card has its own GitHub icon, fixed by code (issue #234, story 1 of #230).

The owner named 23 fields. Each gets one Octicon (GitHub's own icon set, MIT) in dokima/icons/, drawn in the same
16-by-16 style as today's status circles, and one fixed table in dokima/card.py maps each field to its icon:

    card.FIELD_ICONS    {field: file name in dokima/icons/ without ".svg"}; the file name is the field's words joined
                        by "-" (so "plan review" -> "plan-review"), and passed and failed keep today's passed.svg and
                        failed.svg

Each field is pinned below to the Octicon it uses (its 16px version, primer/octicons), by the SHA-256 of the icon's
path data, so an icon that is not that Octicon fails. A field's icon is drawn exactly as today's icons are,
`card.icon(repo, FIELD_ICONS[field], alt=field)`: an <img> served from the repo's own main branch, with the field's
name as its alt text. "In front of" means the icon comes right before the field's words, with only a space, `**` or
`<b>` between them.

Where each field is shown today and gets its icon:
    issue and PR card (dokima/card.py render): Needs you and Merged on the status line, Merged on a child's row,
        files changed in the links row, the Acceptance criteria heading, Verified by under a criterion, and Code
        review and Owner approval in the Definition of Done (after their verdict circle)
    live run card (dokima/agent.py live_card): the run's role (planner, worker, plan review or code review) after
        its state icon, in front of the role's name
    run comment (dokima/agent.py render): the run's role right after the verdict icon on the first line (also on a
        cancelled or stopped run, for the role it attempted); Acceptance criteria and Questions for you on a plan;
        every blocker's id, the Notes and Outside the plan folds and Issues found outside this one on a review;
        Outside the plan in the worker's What it found; Still open in What the previous step did; blocked by on a
        filed split; and stats at the start of the footnote
"""
import hashlib
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
ICONS = os.path.join(ROOT, "dokima", "icons")
REPO = "o/r"
OWNER = "boss"
BOT = "dokima-runtime"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
SRC = "https://github.com/o/r/issues/40"

# field -> (its Octicon, SHA-256 of the Octicon's 16px path data, each path's d joined by a newline)
OCTICONS = {
    "planner": ("light-bulb", "2d14fc1d88b25498f39113b80a9fbb06980a7f32d8d75df9b94e05b10ff04ec6"),
    "worker": ("tools", "c9d83d86b01099a25554da49200c48db32d6851d13ee486bb6b97ab245ff3d39"),
    "plan review": ("checklist", "566d501da179422536e56968bd9ae8676a6f81eb464ec821b86d36480fd07445"),
    "code review": ("code-review", "853444c70e0f92c752828a4f9e069e90f8931c7e6397f3f919b37e6b01e7d1fc"),
    "autopilot": ("rocket", "d7f23d3e2aa0e452671e9cf39c3cb0a86b8d34fd50ca1014db9614e6316b6b53"),
    "passed": ("check-circle-fill", "44ccca3f27e1452633da1533d7e47d95e011a96255edf7009b4712330aeaabe8"),
    "failed": ("x-circle-fill", "7987d7a871388266595b3a8dcbf086e7db7138ac824a25ebe1245deb00e2fc8b"),
    "needs you": ("bell", "f322f212155a346ab01c84b5459954e69444116f579d2739c2872ad6a36b7764"),
    "owner approval": ("person", "3a360deeebbc6e59eb8b2f0aab2c00407ba38b9a12b073c3afc282f4164db289"),
    "merged": ("git-merge", "4f03fb89e0685072839e422a04f7e66a31fd61be0419ea72fdf1d1cd0a79edde"),
    "still open": ("issue-opened", "8a045f63767e25c88d02a4f1a687a704fbc5fc329b2bfa423b5b0cec25ed582c"),
    "acceptance criterion": ("tasklist", "9e458b35be49254fc28fcd1c51cc4fd4a79a7f6e03c3802dfba35e9586aac587"),
    "verified by": ("verified", "64dc3a6e42153dec04c5bf7d11d24dd61903223e0b2c2c321570a10661b9db7b"),
    "files changed": ("file-diff", "72eece4b9022c1c0c7cbd812f0581ebf23858c595e725c11185d8231f57aa99b"),
    "question": ("question", "1a77b49e420560418d616cb46f5c4cd90de36a4c8c383c7796b400094d78d098"),
    "blocker": ("blocked", "3c8b225e2be716d6b9927567d49af2f69da87ea530134ff1246747d3c87a5309"),
    "note": ("note", "12746c2d89c932ffff992f6e50389152c2522f4e402f39d9d9ee1a244796ead8"),
    "outside the plan": ("alert", "d4036a26a0080e71c2a188a38f6e3e587b50e43ecba63222a82b4034c16467ac"),
    "issue found": ("bug", "2cfb61927e81914932dc6c95a7da3a542bffcd71a82d8f72e6968af91dd878a5"),
    "related": ("link", "23ebb55c9ad1928699bb36439d3e38a7a85923b357a3ac38c5b4df8e9d5112cb"),
    "blocked by": ("issue-tracked-by", "04f6eac8e559d4c8888f160fb1ef924f7211e79e5c465b21e8ecdc2a5e1fe1f1"),
    "blocks": ("issue-tracks", "a40f73ef7691393c3adcbbdba4586c2e627c049448c86081fe96a65416b8eb4f"),
    "stats": ("graph", "1312503e3e7433babde39ecdf2a997eb6de1640ce5fd64a6d0682601bf7a6998"),
}
FIELDS = list(OCTICONS)
# passed and failed keep today's passed.svg and failed.svg; the table test checks them, the rest are new.
NEW = [f for f in FIELDS if f not in ("passed", "failed")]
SLUG = {f: f.replace(" ", "-") for f in FIELDS}
# The colors today's status circles use: green, red, yellow and gray.
PALETTE = {"#2da44e", "#cf222e", "#bf8700", "#8c959f"}
SVG = "{http://www.w3.org/2000/svg}"
RECORD = re.compile(r"<details><summary>Full record</summary>.*?</details>", re.S)
IMG = re.compile(r"<img [^>]*>")


def img(field, repo=REPO):
    """The field's icon exactly as the card draws today's icons: served from main, the field's name as its alt."""
    return (f'<img src="https://raw.githubusercontent.com/{repo}/main/dokima/icons/{SLUG[field]}.svg" width="16" '
            f'height="16" align="absmiddle" alt="{field}">')


def in_front(field, label):
    """A pattern for the field's icon right before its words, with only a space, `**` or `<b>` between."""
    return re.compile(re.escape(img(field)) + r"\s*(?:\*\*|<b>)?\s*" + re.escape(label))


def shows(text, field, label, k, where):
    """Fail naming criterion k unless the field's icon stands in front of `label` in `text`."""
    assert in_front(field, label).search(text), \
        f"{k}: {where} shows “{label}” without the {field} icon right in front of it:\n{text[:3000]}"


def comment(login, body, i):
    """One comment of the conversation, as dokima.agent.conversation lists it."""
    return {"author": {"login": login}, "body": body, "createdAt": f"2026-10-08T{i:02d}:00:00Z", "where": "issue #40"}


def rec(role, stage=None, passed=True, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": passed, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}", "run_id": str(n)}


PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id.",
        "user_story": "Callers get a job id for a slow call.",
        "acceptance_criteria": [{"text": "First thing works", "source": SRC},
                                {"text": "Second thing works", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks out", "why": "safety", "principle": "Fail closed"}],
        "scope": ["app/jobs.py"], "out_of_scope": ["Retrying jobs."],
        "tests": {"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_two"],
                  "40.3": ["tests/test_a.py::test_three"]}, "test_changes": {}}
TESTS = {"tests/test_a.py::test_one": {"verified_by": "The first thing works end to end.", "url": "https://x/a#L3"}}
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40"}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
GREEN = [{"name": n, "status": "completed", "conclusion": "success", "html_url": f"https://github.com/o/r/actions/runs/2/job/{i}"}
         for i, n in enumerate(["40.1 · First thing works", "40.2 · Second thing works", "40.3 · Nothing leaks out",
                                "all tests"])]
OWNER_OK = [{"state": "APPROVED", "user": {"login": OWNER}, "html_url": "https://github.com/o/r/pull/5#review-1"}]


def found_for(steps, **kw):
    """What the card is drawn from for issue #40 after these steps (a str is the owner's words)."""
    items = [comment(OWNER, s, i) if isinstance(s, str) else
             comment(BOT, f"{agent.MARK}\n**Card**\n\n```json\n{json.dumps(s)}\n```\n", i) for i, s in enumerate(steps)]
    f = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "reviews": [],
         "owners": {OWNER}, "tests": TESTS, "worker": DONE, "children": []}
    return dict(f, **kw)


APPROVED = [rec("planner", n=11, **PLAN), rec("reviewer", "plan", n=12, verdict="approve", blockers=[]), "/work",
            rec("worker", n=13), rec("reviewer", "pr", n=14, verdict="approve", blockers=[])]


def draw(found, page="issue"):
    return card.render(REPO, ISSUE, found, page=page)


def built(role, stage="", handback=None, passed=True, problems=""):
    """A run's record built the way the workflow builds one, from a temp hand-back folder; a split's as code files it."""
    if role == "split":
        return {"role": "split", "stage": None, "handback": handback, "check": {"passed": True, "problems": []},
                "run": "https://github.com/o/r/actions/runs/1"}
    out = tempfile.mkdtemp()
    json.dump(handback or {}, open(os.path.join(out, agent.HANDBACK[role]), "w"))
    r = agent.build_record(role, stage, out, problems, passed, {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1"})
    r["models"], r["report"] = ["claude-opus-5-5"], {"duration_ms": 60000, "turns": 3, "tokens_in": 10, "tokens_out": 5,
                                                     "cost_usd": 0.1}
    return r


def first_line(body):
    """The comment's first line after its marker."""
    lines = [l for l in body.split(agent.MARK, 1)[-1].splitlines() if l.strip()]
    return lines[0] if lines else ""


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_RUN_ID", "1")


QUESTIONS = [{"question": "Should a job expire after a day?", "assumption": "The plan assumes it does."}]
PREVIOUS = {"did": ["Built the queue."], "decided": ["Kept the endpoint."], "open": ["The retry rule."]}


def blocker(i, crit):
    return {"id": i, "criterion": crit, "test": None, "problem": f"problem {i}", "evidence": f"evidence {i}",
            "fix": f"fix {i}", "fixer": "worker"}


REVIEW = {"previous_step": PREVIOUS, "verdict": "block", "summary": "The reviewer read the work.",
          "blockers": [blocker("B1", "9.1"), blocker("B2", "9.2")],
          "notes": [{"text": "A note on naming.", "evidence": "jobs.py:3"}],
          "outside_plan": [{"file": "dokima/extra.py", "change": "one helper line"}], "resolved": [],
          "asks": [{"ask": "ask 1", "source": "https://x/9", "criterion": "9.1"}],
          "issues_found": [{"title": "Retries are missing", "why": "A failed job never retries."}]}
WORK = {"summary": "The calls blocked the server. They now run as jobs.",
        "criteria": {"9.1": "dokima/jobs.py, submit() returns the id"}, "evidence": "12 passed",
        "outside_scope": [{"file": "dokima/extra.py", "why": "A shared helper needed one line."}],
        "suspect_tests": [], "replies": [], "previous_step": PREVIOUS}
SPLIT = {"stories": [{"story": 1, "issue": 201, "title": "First", "blocked_by": []},
                     {"story": 2, "issue": 202, "title": "Second", "blocked_by": [1]}]}


# 234.1: one Octicon per field in dokima/icons/, 16 by 16 like today's status icons

def drawn_as(field):
    """The SHA-256 of an icon file's path data, or None when it is missing or unreadable."""
    try:
        root = ET.parse(os.path.join(ICONS, SLUG[field] + ".svg")).getroot()
    except (OSError, ET.ParseError):
        return None
    return hashlib.sha256("\n".join(p.get("d") for p in root.iter() if p.tag == SVG + "path").encode()).hexdigest()


@pytest.mark.parametrize("field", NEW)
def test_every_field_has_its_own_octicon_in_the_status_icon_style(record_property, field):
    """Each of the 23 fields has its own GitHub Octicon in dokima/icons/, 16 by 16 like today's status icons.

    Reads dokima/icons/<field>.svg and checks it is a single SVG drawn exactly like today's circles (16 by 16, a
    0 0 16 16 view box, one fill color from today's palette set on the icon itself) and that its drawing is the
    Octicon pinned for that field, by the SHA-256 of its path data. A missing file, another size or a drawing that is
    not that Octicon fails, naming the field."""
    record_property("proves", "234.1")
    name, digest = OCTICONS[field]
    path = os.path.join(ICONS, SLUG[field] + ".svg")
    assert os.path.isfile(path), f"234.1: dokima/icons/{SLUG[field]}.svg, the {field} icon, does not exist"
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        pytest.fail(f"234.1: dokima/icons/{SLUG[field]}.svg is not a readable SVG: {e}")
    assert root.tag == SVG + "svg", f"234.1: the {field} icon is not an SVG: its root is {root.tag}"
    attrs = dict(root.attrib)
    assert set(attrs) == {"fill", "width", "height", "viewBox"}, \
        f"234.1: the {field} icon is not drawn like today's status icons: its <svg> carries {sorted(attrs)}"
    assert (attrs["width"], attrs["height"], attrs["viewBox"]) == ("16", "16", "0 0 16 16"), \
        f"234.1: the {field} icon is not 16 by 16: width {attrs['width']}, height {attrs['height']}, viewBox {attrs['viewBox']}"
    assert attrs["fill"] in PALETTE, f"234.1: the {field} icon's color {attrs['fill']} is not one of today's: {sorted(PALETTE)}"
    paths = [e for e in root.iter() if e.tag == SVG + "path"]
    assert paths and all(set(p.attrib) == {"d"} for p in paths), \
        f"234.1: the {field} icon must be plain paths with no style of their own: {[p.attrib.keys() for p in paths]}"
    got = hashlib.sha256("\n".join(p.get("d") for p in paths).encode()).hexdigest()
    assert got == digest, f"234.1: the {field} icon is not the {name} Octicon (16px): its path data differs"


# 234.2: one fixed table maps the 23 fields to their icons, and every card and run comment shows them

def test_one_fixed_table_in_code_maps_every_field_to_its_icon(record_property):
    """One fixed table in code maps each of the 23 fields, and nothing else, to its own icon file.

    Reads card.FIELD_ICONS and checks it names exactly the 23 fields, each to its own file in dokima/icons/ holding
    the field's own Octicon (passed and failed keep today's circles), no two fields sharing a drawing, and that
    card.icon draws a field's icon from it served from main with the field's name as its alt text."""
    record_property("proves", "234.2")
    table = getattr(card, "FIELD_ICONS", None)
    assert isinstance(table, dict), "234.2: there is no fixed table of field icons: card.FIELD_ICONS does not exist"
    assert set(table) == set(FIELDS), \
        f"234.2: the table's fields differ: missing {sorted(set(FIELDS) - set(table))}, extra {sorted(set(table) - set(FIELDS))}"
    for f in FIELDS:
        assert table[f] == SLUG[f], f"234.2: the table maps {f} to {table[f]!r}, not {SLUG[f]!r}"
        assert os.path.isfile(os.path.join(ICONS, table[f] + ".svg")), f"234.2: {f} maps to a missing icon {table[f]}.svg"
        assert card.icon(REPO, table[f], alt=f) == img(f), f"234.2: the {f} icon is drawn as {card.icon(REPO, table[f], alt=f)}"
        assert drawn_as(f) == OCTICONS[f][1], f"234.2: {table[f]}.svg, the {f} icon, is not the {OCTICONS[f][0]} Octicon"
    drawings = [drawn_as(f) for f in FIELDS]
    assert len(set(drawings)) == len(FIELDS), "234.2: two fields share one icon; every field must have its own"


def test_the_issue_and_pr_card_show_each_fields_icon_in_front_of_it(record_property):
    """On the issue and PR card, every field shown has its icon right in front of it.

    Draws the card of approved work with every check green, a test with a Verified by and the owner's approval, on
    the issue and on the PR, and checks Needs you, files changed, Acceptance criteria, Verified by, Code review and
    Owner approval each have their icon right in front; then a merged PR's card and a split's card with a merged
    child, and checks Merged has its icon on the status line and on the child's row."""
    record_property("proves", "234.2")
    f = found_for(APPROVED, pr=PR, check_runs=GREEN, reviews=OWNER_OK)
    for page in ("issue", "pr"):
        text = draw(f, page)
        where = f"the {page} card"
        shows(text, "needs you", "Needs you", "234.2", where)
        shows(text, "files changed", "[files changed]", "234.2", where)
        shows(text, "acceptance criterion", "Acceptance criteria", "234.2", where)
        shows(text, "verified by", "Verified by", "234.2", where)
        shows(text, "code review", "Code review", "234.2", where)
        shows(text, "owner approval", "Owner approval", "234.2", where)
        assert re.search(r'alt="passed"[^>]*>(?:</a>)?\s*' + re.escape(img("code review")), text), \
            f"234.2: on {where} the Code review icon does not follow its verdict circle:\n{text}"
    merged = draw(found_for(APPROVED, pr=dict(PR, merged=True, state="closed"), check_runs=GREEN), "issue")
    shows(merged, "merged", "Merged", "234.2", "a merged PR's status line")
    split = [rec("planner", n=11, kind="feature", summary="Jobs, in two stories.", feature="Jobs.",
                 stories=[{"title": "A"}, {"title": "B"}]),
             rec("reviewer", "plan", n=12, verdict="approve", blockers=[]), "/work",
             rec("split", n=13, stories=[{"story": 1, "issue": 41, "title": "A", "blocked_by": []},
                                         {"story": 2, "issue": 42, "title": "B", "blocked_by": []}])]
    text = draw(found_for(split, children=[{"number": 41, "title": "A", "stage": "Merged"},
                                           {"number": 42, "title": "B", "stage": "Plan"}]))
    row = next((l for l in text.splitlines() if "/issues/41)" in l), "")
    shows(row, "merged", "Merged", "234.2", "a merged child's row")
    other = next((l for l in text.splitlines() if "/issues/42)" in l), "")
    assert img("merged") not in other, f"234.2: a child still in Plan shows the merged icon: {other}"


def test_the_card_shows_no_field_icon_where_the_field_is_not_shown(record_property):
    """A field the card does not show brings no icon: no stray Needs you, Merged, files changed or Verified by.

    Draws the card of a plan with no PR, nothing for the owner and no test docstrings, and checks it holds the
    Acceptance criteria icon but none of the Needs you, Merged, files changed or Verified by icons; and a card with
    no plan holds no Acceptance criteria icon."""
    record_property("proves", "234.2")
    text = draw(found_for([rec("planner", n=11, **PLAN)], tests={}, worker=None))
    assert img("acceptance criterion") in text, f"234.2: the planned card has no Acceptance criteria icon:\n{text}"
    for f in ("needs you", "merged", "files changed", "verified by"):
        assert img(f) not in text, f"234.2: the card shows the {f} icon where it shows no {f}:\n{text}"
    empty = draw(found_for([], tests={}, worker=None))
    assert img("acceptance criterion") not in empty, f"234.2: a card with no plan shows the Acceptance criteria icon:\n{empty}"


ROLES = [("planner", "", "planner", "Planner"), ("worker", "", "worker", "Worker"),
         ("reviewer", "plan", "plan review", "Plan review"), ("reviewer", "pr", "code review", "Code review")]


@pytest.mark.parametrize("role,stage,field,head", ROLES)
def test_the_live_card_shows_the_runs_role_icon_in_front_of_its_name(record_property, env, role, stage, field, head):
    """While a run is going, its live card shows the role's icon (planner, worker, plan or code review) before its name.

    Draws the live card of the run in every state (queued, waiting, setting up, working, checking) and checks each
    shows the state icon, then the role's icon right in front of the role's name; and no other role's icon."""
    record_property("proves", "234.2")
    for state, ahead in (("queued", None), ("queued", "https://x/run/0"), ("handoff", None), ("setup", None),
                         ("working", None), ("checking", None)):
        body = agent.live_card(role, stage, state, ahead)
        line = next((l for l in body.splitlines() if f"**{head}**" in l), "")
        assert re.search(r'alt="(?:queued|running)">\s*' + re.escape(img(field)) + r"\s*\*\*" + re.escape(head), line), \
            f"234.2: the {state} card of the {head} run does not show its state icon then the {field} icon before its name: {line}"
        others = [f for _, _, f, _ in ROLES if f != field and img(f) in body]
        assert not others, f"234.2: the {head} run's card shows another role's icon: {others}"


@pytest.mark.parametrize("role,stage,field,head", ROLES)
def test_a_run_comment_opens_with_its_verdict_then_its_roles_icon(record_property, env, role, stage, field, head):
    """Every run comment's first line shows the verdict circle, then the icon of the role that ran.

    Draws the comment of a passed run, a rejected run, a cancelled run and a run that stopped before its agent, for
    the role, and checks each first line starts with its verdict icon followed right away by the role's icon."""
    record_property("proves", "234.2")
    hb = {"planner": dict(PLAN), "worker": dict(WORK), "reviewer": dict(REVIEW, verdict="approve", blockers=[])}[role]
    meta = {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1"}
    bodies = [("passed", "passed", agent.render(built(role, stage, hb))),
              ("rejected", "failed", agent.render(built(role, stage, hb, passed=False, problems="a problem"))),
              ("cancelled", "cancelled", agent.render(agent.cancelled(role, stage, True, meta))),
              ("stopped", "failed", agent.render(agent.not_started(role, stage, "the pack failed", meta)))]
    for name, verdict, body in bodies:
        line = first_line(body)
        assert re.match(r'<img [^>]*alt="' + verdict + r'">\s*' + re.escape(img(field)), line), \
            f"234.2: the {name} {head} comment does not open with its {verdict} icon, then the {field} icon: {line}"


def test_the_plan_comment_shows_criteria_and_question_icons(record_property, env):
    """A plan's comment shows the Acceptance criteria icon and, only when it asks, the question icon.

    Draws a plan's comment with questions and checks Acceptance criteria and Questions for you each have their icon
    right in front; then the same plan with no questions, and checks no question icon is shown."""
    record_property("proves", "234.2")
    body = agent.render(built("planner", "", dict(PLAN, questions=QUESTIONS)))
    shows(body, "acceptance criterion", "Acceptance criteria", "234.2", "the plan's comment")
    shows(body, "question", "Questions for you", "234.2", "the plan's comment")
    plain = agent.render(built("planner", "", PLAN))
    assert img("question") not in plain, f"234.2: a plan with no questions shows the question icon:\n{plain}"


def test_the_review_comment_shows_blocker_outside_and_issue_icons(record_property, env):
    """A review's comment shows the blocker, outside the plan and issue found icons.

    Draws a blocking review with two blockers, a change outside the plan and an issue found, and checks each
    blocker's problem, the Outside the plan fold and Issues found outside this one have their icon right in front;
    then an approving review with none of them, and checks none of those icons is shown."""
    record_property("proves", "234.2")
    body = agent.render(built("reviewer", "pr", REVIEW))
    for b in ("B1", "B2"):
        shows(body, "blocker", f"problem {b}", "234.2", "the review's comment")
    shows(body, "outside the plan", "Outside the plan", "234.2", "the review's comment")
    shows(body, "issue found", "Issues found outside this one", "234.2", "the review's comment")
    clean = agent.render(built("reviewer", "pr", dict(REVIEW, verdict="approve", blockers=[], notes=[], outside_plan=[],
                                                      issues_found=[])))
    for f in ("blocker", "outside the plan", "issue found"):
        assert img(f) not in clean, f"234.2: a review with no {f} shows the {f} icon:\n{clean}"


def test_the_worker_comment_shows_outside_the_plan_and_still_open_icons(record_property, env):
    """A worker's comment shows the outside the plan icon on each file it changed outside the plan, and Still open's icon.

    Draws a worker's comment that changed a file outside the plan and whose previous step left something open, and
    checks Outside the plan and Still open each have their icon right in front; with neither, neither icon shows."""
    record_property("proves", "234.2")
    body = agent.render(built("worker", "", WORK))
    shows(body, "outside the plan", "Outside the plan", "234.2", "the worker's comment")
    shows(body, "still open", "Still open", "234.2", "the worker's comment")
    clean = agent.render(built("worker", "", dict(WORK, outside_scope=[], previous_step={"did": ["x"], "decided": [], "open": []})))
    for f in ("outside the plan", "still open"):
        assert img(f) not in clean, f"234.2: a worker's comment with no {f} shows the {f} icon:\n{clean}"


def test_the_split_comment_shows_the_blocked_by_icon(record_property, env):
    """A filed split's comment shows the blocked by icon in front of every story's blocked by, and nowhere else.

    Draws the comment of a split whose second story is blocked by the first, and checks blocked by has its icon right
    in front, once; the first story's line has none."""
    record_property("proves", "234.2")
    body = agent.render(built("split", "", SPLIT))
    shows(body, "blocked by", "blocked by #201", "234.2", "the split's comment")
    first = next((l for l in body.splitlines() if "#201 First" in l), "")
    assert img("blocked by") not in first, f"234.2: a story blocked by nothing shows the blocked by icon: {first}"
    assert body.count(img("blocked by")) == 1, f"234.2: the split shows the blocked by icon {body.count(img('blocked by'))} times"


@pytest.mark.parametrize("role,stage", [("planner", ""), ("worker", ""), ("reviewer", "plan"), ("reviewer", "pr"),
                                        ("split", "")])
def test_every_run_comments_stats_fold_starts_with_the_stats_icon(record_property, env, role, stage):
    """The stats fold at the bottom of every run comment starts with the stats icon.

    Draws the comment of each kind of run and checks the title of its last fold before the full record, the fold
    with model, time, turns, tokens and cost, opens with the stats icon."""
    record_property("proves", "234.2")
    hb = {"planner": PLAN, "worker": WORK, "reviewer": REVIEW, "split": SPLIT}[role]
    body = agent.render(built(role, stage, hb))
    titles = re.findall(r"<summary>(.*?)</summary>", body.split("<details><summary>Full record</summary>", 1)[0], re.S)
    last = titles[-1] if titles else ""
    assert re.match(r"(?:<b>|\*\*)?\s*" + re.escape(img("stats")), last), \
        f"234.2: the {role} comment's stats fold does not open with the stats icon: {last}"


# 234.3: no hand-back can choose, change or drop an icon

NAMED = {"icon": "failed", "icons": {f: "passed" for f in FIELDS}, "field_icons": {}, "no_icons": True,
         "emoji": ":rocket:"}


def without_record(body):
    return RECORD.sub("", body)


@pytest.mark.parametrize("role,stage,hb", [("planner", "", dict(PLAN, questions=QUESTIONS)), ("worker", "", WORK),
                                           ("reviewer", "pr", REVIEW), ("split", "", SPLIT)])
def test_a_handback_that_names_its_own_icons_changes_no_icon_on_its_comment(record_property, env, role, stage, hb):
    """A hand-back that names icons of its own, or asks for none, shows exactly the same icons as one that names none.

    Draws the comment of a hand-back, then of the same hand-back carrying icon, icons, field_icons and no_icons keys
    (on the hand-back and on each of its listed items), and checks every icon on the two comments is the same, in
    the same order, and the field icons are there."""
    record_property("proves", "234.3")
    plain = without_record(agent.render(built(role, stage, hb)))
    named = dict(hb, **NAMED)
    for key in ("acceptance_criteria", "questions", "blockers", "notes", "outside_plan", "issues_found", "outside_scope",
                "stories"):
        if isinstance(named.get(key), list):
            named[key] = [dict(x, **NAMED) if isinstance(x, dict) else x for x in named[key]]
    other = without_record(agent.render(built(role, stage, named)))
    assert img("stats") in plain, f"234.3: setup: the {role} comment shows no field icon to protect:\n{plain}"
    assert IMG.findall(other) == IMG.findall(plain), \
        f"234.3: a {role} hand-back naming its own icons changed the icons shown: {IMG.findall(plain)} became {IMG.findall(other)}"


def test_a_plan_that_names_its_own_icons_changes_no_icon_on_the_card(record_property):
    """A plan that names icons of its own shows exactly the same card as one that names none.

    Draws the issue card of approved work from a plan, then from the same plan carrying icon, icons, field_icons and
    no_icons keys on the plan and on each criterion, and checks the two cards are identical and show field icons."""
    record_property("proves", "234.3")
    named = dict(PLAN, **NAMED, acceptance_criteria=[dict(c, **NAMED) for c in PLAN["acceptance_criteria"]])
    steps = lambda p: [rec("planner", n=11, **p)] + APPROVED[1:]
    a = draw(found_for(steps(PLAN), pr=PR, check_runs=GREEN, reviews=OWNER_OK))
    b = draw(found_for(steps(named), pr=PR, check_runs=GREEN, reviews=OWNER_OK))
    assert img("acceptance criterion") in a, f"234.3: setup: the card shows no field icon to protect:\n{a}"
    assert a == b, f"234.3: a plan naming its own icons changed the card:\n{a}\n---\n{b}"


# 234.4: icons are served from the repo's own main branch, so the work under review cannot change how it is shown

def test_every_field_icon_is_served_from_the_repos_own_main_branch(record_property, env):
    """Every field icon on the cards and run comments is served from the repo's own main branch.

    Draws the PR card and the comments of a plan, a review and a worker, collects every field icon they show, and
    checks there are field icons and each one's address is dokima/icons/ on the main branch of this repo, never a
    branch or another repo, and that file exists."""
    record_property("proves", "234.4")
    texts = [draw(found_for(APPROVED, pr=PR, check_runs=GREEN, reviews=OWNER_OK), "pr"),
             agent.render(built("planner", "", dict(PLAN, questions=QUESTIONS))),
             agent.render(built("reviewer", "pr", REVIEW)), agent.render(built("worker", "", WORK))]
    seen = set()
    for text in texts:
        for tag in IMG.findall(text):
            alt = re.search(r'alt="([^"]*)"', tag)
            if not alt or alt.group(1) not in FIELDS or alt.group(1) in ("passed", "failed"):
                continue
            src = re.search(r'src="([^"]*)"', tag).group(1)
            m = re.fullmatch(r"https://raw\.githubusercontent\.com/o/r/main/dokima/icons/([a-z-]+)\.svg", src)
            assert m, f"234.4: the {alt.group(1)} icon is not served from this repo's main branch: {src}"
            assert os.path.isfile(os.path.join(ICONS, m.group(1) + ".svg")), f"234.4: {src} names no file in dokima/icons/"
            seen.add(alt.group(1))
    assert len(seen) >= 8, f"234.4: the cards show too few field icons to check: {sorted(seen)}"

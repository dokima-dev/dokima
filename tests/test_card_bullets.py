"""The issue and PR card list criteria as bullets, count the owner's merge and match.

Issue #235, story 2 of #230.

The card is drawn by `dokima/card.py` (render, from `found`; main writes it on the issue and its PR). The layout these
tests read, with markdown links `[text](url)` and HTML links `<a href="url">text</a>` treated alike:

    - <status icon> **Acceptance criterion:** <the criterion's sentence, linked to its check when it has one>
      - *Verified by: <the test's docstring first line>*      one line per test with a docstring; only the words
                                                              Verified by link, to that test (the Verified by field
                                                              icon may sit in front of the words, inside the link)
      - Source                                                the word Source links to where the owner asked

The status icon is an <img> whose alt is its state (not started, running, passed, failed), never inside a link. A
criterion's lines are its bullet and the indented lines under it, up to the next line that is not indented.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import card, plan  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
ASK_1 = "https://github.com/o/r/issues/40#issuecomment-111"
ASK_2 = "https://github.com/o/r/issues/40"
PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": "First thing works", "source": ASK_1},
                                {"text": "Second thing works", "source": ASK_2}],
        "non_functional": [],
        "scope": ["dokima/card.py"], "out_of_scope": ["The board stays as it is."],
        "tests": {"40.1": ["tests/test_a.py::test_one", "tests/test_a.py::test_one_more"],
                  "40.2": ["tests/test_a.py::test_two"]},
        "test_changes": {}}
TESTS = {"tests/test_a.py::test_one": {"verified_by": "The first thing runs.",
                                       "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L3"},
         "tests/test_a.py::test_one_more": {"verified_by": "The first thing runs twice.",
                                            "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L9"},
         "tests/test_a.py::test_two": {"verified_by": "The second thing runs.",
                                       "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L15"}}
STATES = {"passed", "failed", "running", "not started"}
ICON_FILE = {"passed": "passed", "failed": "failed", "running": "running", "not started": "none"}


def rec(role, stage=None, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


RECS = [rec("planner", n=11, **PLAN), rec("reviewer", "plan", n=12, verdict="approve"), rec("worker", n=13),
        rec("reviewer", "pr", n=14, verdict="approve")]
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
      "merged_by": None}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}


def job(n):
    return f"https://github.com/o/r/actions/runs/2/job/{n}"


def run(name, status="completed", conclusion="success", n=7):
    """One GitHub check run on the PR's latest commit."""
    return {"name": name, "status": status, "conclusion": conclusion, "html_url": job(n)}


GREEN = [run("40.1 · First thing works", n=1), run("40.2 · Second thing works", n=2), run("All tests", n=4)]
FOUND = {"recs": RECS, "pr": PR, "check_runs": GREEN, "reviews": [], "owners": {"boss"}, "tests": TESTS,
         "worker": DONE, "children": []}


def review(state, login="boss"):
    """One GitHub review of the PR."""
    return {"user": {"login": login}, "state": state, "html_url": "https://github.com/o/r/pull/5#pullrequestreview-1",
            "submitted_at": "2026-10-08T10:00:00Z"}


def draw(**kw):
    return card.render(REPO, ISSUE, dict(FOUND, **kw))


def links_as_html(text):
    """The text with every markdown link written as HTML, so both forms read alike."""
    return re.sub(r"\[((?:<img [^>]*>|[^\]])*)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)


def plain(html):
    """The words a reader sees: no images, tags, italic or bold markers."""
    text = re.sub(r"<img [^>]*>", "", html)
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("*", "").replace("_", "")).strip()


def block(text):
    assert plan.CARD_START in text and plan.CARD_END in text, "the text holds no card between its markers"
    return text[text.index(plan.CARD_START):text.index(plan.CARD_END) + len(plan.CARD_END)]


def item(text, words, k):
    """The bullet line of the criterion whose sentence is `words`, and the lines under it.

    Links are written as HTML.

    Fails naming criterion k unless exactly one top-level bullet holds the sentence."""
    lines = links_as_html(block(text)).splitlines()
    at = [i for i, l in enumerate(lines) if l.startswith("- ") and words in l]
    assert len(at) == 1, f"{k}: expected one bullet line “- ...” holding “{words}”, found {len(at)}:\n{text}"
    under = []
    for line in lines[at[0] + 1:]:
        if not re.match(r"\s+\S", line):
            break
        under.append(line)
    return lines[at[0]], under


def head(text, words, k):
    """The state on a criterion's status icon, and the link on its sentence or None.

    Fails naming criterion k unless the bullet is the status icon, then **Acceptance criterion:**, then the sentence,
    with the status icon outside any link."""
    line, _ = item(text, words, k)
    m = re.fullmatch(r'- (<img [^>]*alt="([^"]*)"[^>]*>)\s*\*\*Acceptance criterion:\*\*\s+(.*)', line)
    assert m, f"{k}: the bullet of “{words}” is not the status icon, then **Acceptance criterion:**, then its sentence: {line}"
    icon, st, rest = m.groups()
    assert st in STATES, f"{k}: the bullet of “{words}” opens with “{st}”, not a status icon"
    assert f"/icons/{ICON_FILE[st]}.svg" in icon, f"{k}: the {st} status icon of “{words}” is not {ICON_FILE[st]}.svg"
    linked = re.fullmatch(r'<a href="([^"]+)">(.*)</a>', rest.strip())
    if linked:
        assert linked.group(2) == words, f"{k}: the link on “{words}” holds more than its sentence: {rest}"
        return st, linked.group(1)
    assert rest.strip() == words, f"{k}: the bullet of “{words}” holds more than its sentence: {rest}"
    return st, None


def verified(line):
    """The link on the words Verified by, and the sentence after them, or None.

    None when the line is not a Verified by line.

    The line must be an indented bullet in italics holding exactly one link, whose words are Verified by."""
    m = re.fullmatch(r"\s+- (.*)", line)
    if not m or "Verified by" not in line:
        return None
    body = m.group(1).strip()
    body = re.sub(r"^(<img [^>]*>\s*)", "", body)
    italic = re.fullmatch(r"\*(.+)\*|_(.+)_|<em>(.+)</em>|<i>(.+)</i>", body)
    assert italic, f"the Verified by line is not in italics: {line}"
    links = re.findall(r'<a href="([^"]+)">(.*?)</a>', body)
    assert len(links) == 1, f"the Verified by line holds {len(links)} links, not one on the words Verified by: {line}"
    url, words = links[0]
    assert plain(words) == "Verified by", f"the link on the Verified by line is on “{plain(words)}”, not on Verified by: {line}"
    seen = plain(body)
    assert seen.startswith("Verified by:"), f"the Verified by line does not read “Verified by: ...”: {seen}"
    return url, seen[len("Verified by:"):].strip()


# 235.1: criteria are an indented bullet list; Verified by in italics, only its words linking to the exact test

def test_each_criterion_is_a_bullet_with_its_verified_by_under_it_in_italics(record_property):
    """Each criterion is a bullet with its status icon, sentence and Verified by under it.

    Draws the card of a plan whose first criterion has two tests and checks there is no table, each criterion is a
    bullet reading status icon, **Acceptance criterion:**, sentence, and under it, indented and in italics, one
    Verified by line per test, where only the words Verified by link to that exact test and the test's sentence
    follows unlinked. Proves 235.1."""
    record_property("proves", "235.1")
    text = draw()
    assert "<table" not in block(text) and "<tr" not in block(text), "235.1: the card still draws the criteria as a table"
    for words in ("First thing works", "Second thing works"):
        head(text, words, "235.1")
    want = {"40.1": ("First thing works", ["tests/test_a.py::test_one", "tests/test_a.py::test_one_more"]),
            "40.2": ("Second thing works", ["tests/test_a.py::test_two"])}
    for key, (words, tests) in want.items():
        _, under = item(text, words, "235.1")
        got = [v for v in (verified(l) for l in under) if v]
        expect = [(TESTS[t]["url"], TESTS[t]["verified_by"]) for t in tests]
        assert got == expect, f"235.1: under “{words}” Verified by shows {got}, not {expect} (link on the words, sentence after)"


def test_verified_by_is_left_out_for_a_test_with_no_docstring(record_property):
    """A test with no docstring gets no Verified by line; other criteria keep theirs.

    Draws the card where criterion 2's only test has no docstring and checks no line under criterion 2 says Verified
    by, while criterion 1 still shows both of its lines. Proves 235.1."""
    record_property("proves", "235.1")
    tests = dict(TESTS, **{"tests/test_a.py::test_two": {"verified_by": None, "url": TESTS["tests/test_a.py::test_two"]["url"]}})
    text = draw(tests=tests)
    _, under = item(text, "Second thing works", "235.1")
    assert not any("Verified by" in l for l in under), f"235.1: Verified by shown for a test with no docstring: {under}"
    _, under = item(text, "First thing works", "235.1")
    assert len([l for l in under if verified(l)]) == 2, f"235.1: criterion 1 lost a Verified by line: {under}"


# 235.2: the status icon shows empty, running, passed or failed; the sentence, not the icon, links to the check

@pytest.mark.parametrize("check, want", [
    (None, "not started"),
    (run("40.1 · First thing works", "queued", None, n=1), "not started"),
    (run("40.1 · First thing works", "in_progress", None, n=1), "running"),
    (run("40.1 · First thing works", n=1), "passed"),
    (run("40.1 · First thing works", conclusion="failure", n=1), "failed"),
])
def test_the_status_icon_follows_the_check_and_the_sentence_links_to_it(record_property, check, want):
    """The status icon follows the check, and the sentence links to the check.

    Draws the card with criterion 1's check missing, queued, in progress, passed and failed, and checks its status
    icon shows that state, never sits inside a link, and the criterion's sentence links to its check whenever the
    check exists (and to nothing when it does not). Proves 235.2."""
    record_property("proves", "235.2")
    st, link = head(draw(check_runs=[check] if check else []), "First thing works", "235.2")
    assert st == want, f"235.2: a check {check and (check['status'], check['conclusion'])} shows {st}, not {want}"
    assert link == (job(1) if check else None), f"235.2: the sentence links to {link}, not {job(1) if check else 'nothing'}"


def test_each_sentence_links_to_its_own_check(record_property):
    """Each criterion's sentence links to its own check, not a neighbour's.

    Draws the card with both criteria's checks and checks each sentence links to its own check run. Proves 235.2."""
    record_property("proves", "235.2")
    text = draw()
    assert head(text, "First thing works", "235.2") == ("passed", job(1)), "235.2: criterion 1 does not link its own check"
    assert head(text, "Second thing works", "235.2") == ("passed", job(2)), "235.2: criterion 2 does not link its own check"


# 235.3: a code owner's merge counts as the owner's approval

def approval(text):
    """The state on the Owner approval circle in the Definition of Done line."""
    line = next(l for l in block(text).splitlines() if "Definition of Done" in l)
    alts = [a for a in re.findall(r'<img [^>]*alt="([^"]*)"', line) if a in STATES]
    assert len(alts) == 3, f"the Definition of Done line does not hold three verdict circles: {line}"
    return alts[2]


def merged(login):
    return dict(PR, merged=True, state="closed", merged_by={"login": login, "type": "User"})


def test_only_a_code_owners_merge_shows_owner_approval_passed(record_property):
    """A code owner's merge shows Owner approval passed, even with no Approve review.

    Draws the card of a PR the code owner merged with no review at all, and one they merged after asking for
    changes, and checks Owner approval shows passed both times; then a PR merged by a stranger, one merged by
    Dokima's bot on autopilot, and an open PR, all with no review, and checks none of them shows it passed. Proves 235.3."""
    record_property("proves", "235.3")
    assert approval(draw(pr=merged("boss"), reviews=[])) == "passed", \
        "235.3: a code owner's merge with no Approve review leaves Owner approval unchecked"
    assert approval(draw(pr=merged("boss"), reviews=[review("CHANGES_REQUESTED")])) == "passed", \
        "235.3: a code owner's merge after asking for changes does not show Owner approval passed"
    for login in ("someone", "dokima-runtime[bot]"):
        assert approval(draw(pr=merged(login), reviews=[])) != "passed", f"235.3: a merge by {login} showed Owner approval passed"
    assert approval(draw(reviews=[])) == "not started", "235.3: an open PR with no review shows Owner approval started"


# 235.4: the issue card and the PR card are identical, each linking back to its own page

def write_main(monkeypatch, tmp_path, found):
    """Run the card for issue #40 and PR #5 against a faked GitHub.

    Returns the issue body saved and the PR body written, or None for either."""
    from dokima import body
    saved = {}

    def gh(*args, **kw):
        args = [str(a) for a in args]
        for i, a in enumerate(args):
            if a == "--body-file" and args[i + 1] == "-":
                saved["issue"] = kw.get("input")
            if a.startswith("body=@") and any("pulls/5" in x for x in args):
                saved["pr"] = open(a[len("body=@"):]).read()
        return ""

    issue = {"number": 40, "title": "t", "url": ISSUE["url"], "approved_at": None, "changes": [],
             "plan": plan.parse("My ask."), "current_body": "My ask.", "body": "My ask."}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.setattr(card, "gh", gh)
    monkeypatch.setattr(body, "gh", gh)
    monkeypatch.setattr(card, "find_work", lambda repo: (40, 5))
    monkeypatch.setattr(plan, "fetch_issue", lambda repo, n: issue)
    monkeypatch.setattr(card, "gather", lambda repo, n, pr: found)
    card.main()
    return saved.get("issue"), saved.get("pr")


def code_review(text):
    """The state on the Code review circle in the Definition of Done line."""
    line = next(l for l in block(text).splitlines() if "Definition of Done" in l)
    return [a for a in re.findall(r'<img [^>]*alt="([^"]*)"', line) if a in STATES][1]


@pytest.mark.parametrize("pr", [PR, merged("boss"), dict(PR, state="closed")], ids=["open", "merged", "closed"])
def test_the_issue_and_pr_cards_are_identical_and_link_both_pages(record_property, monkeypatch, tmp_path, pr):
    """The issue and PR cards are identical, each linking to the issue and the PR.

    Runs the card for an issue whose code review passed, with its PR open, merged and closed, and checks the card
    is written on both pages, the two are identical, both link to issue #40 and PR #5, and both show the code review
    passed. Proves 235.4."""
    record_property("proves", "235.4")
    on_issue, on_pr = write_main(monkeypatch, tmp_path, dict(FOUND, pr=pr))
    assert on_issue, "235.4: the card was not written on the issue"
    assert on_pr, f"235.4: the card was not written on the {pr['state']} PR, so it keeps an older card than the issue"
    a, b = block(on_issue), block(on_pr)
    assert a == b, f"235.4: the issue and PR cards differ:\n{a}\n---\n{b}"
    html = links_as_html(a)
    assert f'<a href="{ISSUE["url"]}">issue #40</a>' in html, "235.4: the card does not link back to issue #40"
    assert '<a href="https://github.com/o/r/pull/5">PR #5</a>' in html, "235.4: the card does not link back to PR #5"
    assert code_review(a) == code_review(b) == "passed", "235.4: a code review that passed does not show passed on both"
    assert "Closes #40" in on_pr, "235.4: the PR lost its line closing the issue"


# 235.5: under each criterion, Source links to where the owner asked for it, the most recent time

def source(under):
    """The link on the Source line among a criterion's lines, or None.

    Fails if the line says more than the word Source."""
    found = [l for l in under if re.match(r"\s+- ", l) and "Source" in plain(l) and "Verified by" not in l]
    if not found:
        return None
    assert len(found) == 1, f"more than one Source line: {found}"
    links = re.findall(r'<a href="([^"]+)">(.*?)</a>', found[0])
    assert len(links) == 1 and plain(links[0][1]) == "Source" and plain(re.sub(r"^\s+- ", "", found[0])) == "Source", \
        f"the Source line is not the one word Source linking to the ask: {found[0]}"
    return links[0][0]


def test_each_criterion_has_a_source_line_after_verified_by(record_property):
    """Under each criterion, after Verified by, Source links to where the owner asked.

    Draws the card of a plan whose criteria come from two different places and checks each criterion's last line is
    the word Source linking to that criterion's own source, after its Verified by lines, and that the card holds no
    separate list of the owner's asks. Proves 235.5."""
    record_property("proves", "235.5")
    text = draw()
    for words, url in (("First thing works", ASK_1), ("Second thing works", ASK_2)):
        _, under = item(text, words, "235.5")
        assert source(under) == url, f"235.5: under “{words}” Source links to {source(under)}, not {url}"
        assert under and source(under[-1:]) == url, f"235.5: the Source line of “{words}” is not after its Verified by"
    assert "asks" not in plain(block(text)).lower(), "235.5: the card shows the owner's asks as a list of their own"


def test_the_planner_links_each_criterion_to_the_most_recent_ask(record_property):
    """The planner is told to link each source to the owner's most recent ask.

    Reads the planner's prompt and checks one of its sentences names the criterion's source and says it is the
    most recent (newest, latest) place the owner asked for it. Proves 235.5."""
    record_property("proves", "235.5")
    text = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
    hits = [s for s in sentences if "source" in s.lower() and re.search(r"most recent|newest|latest", s, re.I)
            and re.search(r"\bask|\bsaid|\bwords", s, re.I)]
    assert hits, "235.5: the planner's prompt never says a criterion's source is the most recent place the owner asked"

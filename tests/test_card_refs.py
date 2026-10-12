"""Every issue and pull request a card names shows as GitHub's own reference.

Issue #359. GitHub draws a reference to an issue, a pull request or a comment on one with its status icon, its title
and its number, but only when the markdown leaves the reference bare: `#N`, or the page's own link written out on
its own (`https://github.com/o/r/issues/N`, `.../pull/N`, `.../issues/N#issuecomment-M`). A reference wrapped in a
link of its own, `[issue #40](...)` or `<a href="...">Source</a>`, shows only the wrapped words, with no icon and no
title. These tests draw cards with `dokima/card.py`, and the agents' run comments with `dokima/agent.py`, and read
the markdown: every issue or pull request a card or run comment names must be a bare reference, and none may sit
inside a link with words of its own. A link around an image only (a verdict circle linked to its proof) names
nothing and is left alone, as are links to other pages: the latest run, the files changed, a test, AGENTS.md.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest

from dokima import agent, card, plan  # noqa: E402

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
COMMENT = "https://github.com/o/r/issues/40#issuecomment-111"
PARENT = "https://github.com/o/r/issues/30"
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
      "merged_by": None}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": "First thing works", "source": COMMENT},
                                {"text": "Second thing works", "source": ISSUE["url"]},
                                {"text": "Third thing works", "source": PARENT}],
        "non_functional": [{"text": "Fourth thing holds", "why": "it must", "principle": "Fail closed"}],
        "scope": ["dokima/card.py"], "out_of_scope": ["Filing raises; story 3 (#300) does that."],
        "tests": {"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_two"],
                  "40.3": ["tests/test_a.py::test_three"], "40.4": ["tests/test_a.py::test_four"]},
        "links": {"blocked_by": [50], "blocks": [51], "relates_to": [52]}}
TESTS = {f"tests/test_a.py::test_{w}": {"verified_by": f"The {w} thing runs.",
                                        "url": f"https://github.com/o/r/blob/abc/tests/test_a.py#L{i}"}
         for i, w in enumerate(("one", "two", "three", "four"), 1)}


def rec(role, stage=None, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


RECS = [rec("planner", n=11, **PLAN), rec("reviewer", "plan", n=12, verdict="approve"), rec("worker", n=13)]
CHILDREN = [{"number": 41, "title": "First child", "stage": "Plan"},
            {"number": 42, "title": "Second child", "stage": "Merged"},
            {"number": 43, "title": "Third child", "stage": "Review"}]
FEATURE = {"kind": "feature", "summary": "Slow calls run as jobs.", "feature": "Slow calls run as jobs.",
           "stories": [{"title": c["title"], "user_story": "x", "acceptance_criteria": [], "non_functional": [],
                        "depends_on": []} for c in CHILDREN]}
SPLIT_RECS = [rec("planner", n=18, **FEATURE), rec("reviewer", "plan", n=19, verdict="approve"),
              rec("split", n=20, stories=[{"story": i, "issue": c["number"], "title": c["title"], "blocked_by": []}
                                          for i, c in enumerate(CHILDREN, 1)])]
FOUND = {"recs": RECS, "pr": PR, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": TESTS, "worker": DONE,
         "children": []}
STAGES = ("Backlog", "Plan", "Work", "Review", "Merged", "Done", "unknown")

# A link to an issue or a pull request, or to a comment on one; never to its files, a review or a run.
REF_URL = r"https://github\.com/o/r/(?:issues|pull)/(\d+)(?:#issuecomment-\d+)?(?![\w/#-])"
LINKS = re.compile(r"\[((?:<img [^>]*>|[^\]])*)\]\(([^)\s]+)\)|<a\s+href=\"([^\"]*)\"[^>]*>(.*?)</a>", re.S)


def draw(page="issue", **kw):
    """The card's markdown between its markers."""
    text = card.render(REPO, ISSUE, dict(FOUND, **kw), page=page)
    assert plan.CARD_START in text and plan.CARD_END in text, "the card has no markers"
    return text[text.index(plan.CARD_START) + len(plan.CARD_START):text.index(plan.CARD_END)]


def plain(html):
    """The words a reader sees: no images, tags, bold or italic markers."""
    text = re.sub(r"<img [^>]*>", "", html)
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("*", "")).strip()


def wrapped(line):
    """Links on the line to an issue, PR or comment with words of their own.

    Each comes back as (url, words)"""
    out = []
    for m in LINKS.finditer(line):
        url, words = (m.group(2), m.group(1)) if m.group(2) is not None else (m.group(3), m.group(4))
        if re.fullmatch(REF_URL, url) and plain(words):
            out.append((url, plain(words)))
    return out


def refs(line):
    """The issue and PR numbers the line names as GitHub references.

    A reference is `#N` or a bare link.

    Anything inside a link of its own, a tag or a code span is not a reference GitHub draws, so it is taken out
    first."""
    text = re.sub(r"`[^`]*`", " ", LINKS.sub(" ", line))
    text = re.sub(r"<[^>]+>", " ", text)
    found = [int(n) for n in re.findall(r"(?<![\w&/#\[\"=])#(\d+)\b", text)]
    found += [int(n) for n in re.findall(r"(?<![\w/\"=\[<])" + REF_URL, text)]
    return found


def bare_urls(line):
    """The links to issues, PRs or comments written out bare on the line."""
    text = LINKS.sub(" ", line)
    return [m.group(0) for m in re.finditer(r"(?<![\w/\"=\[<])" + REF_URL, text)]


def under(text, words):
    """The indented lines under the criterion whose sentence is `words`."""
    lines = text.splitlines()
    at = [i for i, l in enumerate(lines) if l.startswith("- ") and words in plain(l)]
    assert len(at) == 1, f"the card has {len(at)} criteria saying “{words}”"
    out = []
    for l in lines[at[0] + 1:]:
        if not l.startswith("  "):
            break
        out.append(l)
    return out


def links_row(text):
    """The card's row of links near its top: the one that links the latest run."""
    rows = [l for l in text.splitlines() if "latest run" in plain(l)]
    assert len(rows) == 1, f"the card has {len(rows)} rows linking the latest run"
    return rows[0]


# 359.1: Source shows as a GitHub reference to wherever the ask is

def test_each_source_shows_as_a_github_reference_to_where_the_ask_is(record_property):
    """Each Source shows its comment, issue or parent story as a GitHub reference.

    Draws the card of a plan whose criteria point to a comment and to the parent story, and checks
    each such criterion's last line reads Source: followed by its own link written out bare, so GitHub draws it with its
    icon and title, that no Source is the word Source linked to a page, and that a criterion with no source shows no
    Source line. Proves 359.1, and 526.2: a source on a comment or the parent still shows."""
    record_property("proves", "359.1")
    record_property("proves", "526.2")
    for page in ("issue", "pr"):
        text = draw(page=page)
        # The criterion sourced from the issue itself shows no Source line since #526.
        for words, url in (("First thing works", COMMENT), ("Third thing works", PARENT)):
            lines = under(text, words)
            assert lines, f"359.1: “{words}” has no lines under it on the {page} card"
            last = lines[-1]
            assert not wrapped(last) and "<a " not in last and "](" not in last, \
                f"359.1: the Source of “{words}” is a link with words of its own, not a GitHub reference: {last.strip()}"
            assert bare_urls(last) == [url], \
                f"359.1: the Source of “{words}” should be {url} written out bare, the line is: {last.strip()}"
            said = re.sub(r"^\s*-\s*", "", plain(last))
            assert said == f"Source: {url}", \
                f"359.1: the Source line of “{words}” should read “Source: {url}”, it reads “{said}”"
        assert "Source</a>" not in text and "[Source]" not in text, f"359.1: the {page} card still links the word Source"
    no_source = dict(PLAN, acceptance_criteria=[{"text": "First thing works"}], non_functional=[])
    assert not [l for l in under(draw(recs=[rec("planner", n=11, **no_source)]), "First thing works") if "Source" in l], \
        "359.1: a criterion with no source shows a Source line"


# 359.2: the issue and its pull request at the top show as GitHub references

def test_the_issue_and_pr_at_the_top_show_as_github_references(record_property):
    """The issue and its PR at the top show as GitHub references.

    Draws the card of an issue with an open pull request on the issue and on the pull request, and checks the links
    row names PR #5, and on the pull request issue #40 too, as GitHub references, never as words like “issue #40” or
    “PR #5” linked to the page, while the latest run and the files changed stay links. Since #452 the issue's own
    card leaves out its link to itself. Proves 359.2."""
    record_property("proves", "359.2")
    for page, want in (("issue", [5]), ("pr", [5, 40])):
        row = links_row(draw(page=page))
        assert not wrapped(row), f"359.2: the {page} card links the issue or PR with words of its own: {wrapped(row)}"
        got = refs(row)
        assert sorted(got) == want, f"359.2: the {page} card's top row should name {want} as references once each, names {got}: {row}"
        assert "issue #40" not in plain(row) and "PR #5" not in plain(row), \
            f"359.2: the {page} card's top row still writes the words issue #40 or PR #5: {plain(row)}"
        assert any("latest run" in plain(m.group(0)) for m in LINKS.finditer(row)), "359.2: latest run is no longer a link"
        assert any("files changed" in plain(m.group(0)) and "/pull/5/files" in m.group(0) for m in LINKS.finditer(row)), \
            "359.2: files changed is no longer a link to the PR's files"


def test_with_no_pr_the_top_row_names_only_the_issue(record_property):
    """With no pull request, the issue's top row names no issue or pull request.

    Draws the card of an issue with no pull request and checks the row names nothing, unwrapped: since #452 the
    issue's own card leaves out its link to itself. Proves 359.2."""
    record_property("proves", "359.2")
    row = links_row(draw(pr=None))
    assert not wrapped(row), f"359.2: the issue is linked with words of its own: {wrapped(row)}"
    assert refs(row) == [], f"359.2: with no PR the issue's top row should name nothing, it names {refs(row)}: {row}"


# 359.3: each story of a split shows as a GitHub reference, then its stage

def test_each_story_shows_as_a_github_reference_then_its_stage(record_property):
    """Each story of a split shows as a GitHub reference, then its stage.

    Draws the card of a parent split into three stories at three stages, and checks each story's line names it as
    a GitHub reference, is not a link with words of its own, does not repeat the title GitHub already shows, and
    ends with the story's own stage, in the split's order. Proves 359.3."""
    record_property("proves", "359.3")
    text = draw(recs=SPLIT_RECS, children=CHILDREN, pr=None)
    at = []
    lines = text.splitlines()
    for c in CHILDREN:
        found = [i for i, l in enumerate(lines) if l.startswith("- ") and c["number"] in refs(l)]
        assert len(found) == 1, f"359.3: expected one line naming story #{c['number']} as a GitHub reference, found {len(found)}"
        line = lines[found[0]]
        assert not wrapped(line), f"359.3: story #{c['number']} is a link with words of its own: {line}"
        assert c["title"] not in line, f"359.3: story #{c['number']}'s line repeats its title, which GitHub already shows: {line}"
        words = re.findall(r"\b(" + "|".join(STAGES) + r")\b", plain(line))
        assert words == [c["stage"]], f"359.3: story #{c['number']} should show {c['stage']}, shows {words}: {line}"
        at.append(found[0])
    assert at == sorted(at), "359.3: the stories are not listed in the split's order"


# 359.4: everywhere else a card names an issue or pull request, it is a GitHub reference

def test_no_issue_or_pr_on_a_card_is_a_link_with_words_of_its_own(record_property):
    """No issue or PR on a card is linked under words of its own.

    Draws a full card (sources, top row, Blocked by, Blocks, Relates to, Out of scope), a split's card with its
    stories, and a card whose issues block each other in a loop, on the issue and on the pull request, and checks
    no line links an issue, pull request or comment under words of its own, and every issue and pull request the
    card names shows as a GitHub reference; the issue's own card need not name #40, since #452 leaves out its link
    to itself. Proves 359.4."""
    record_property("proves", "359.4")
    cases = [(dict(), {40, 5, 30, 50, 51, 52, 300}),
             (dict(recs=SPLIT_RECS, children=CHILDREN), {40, 5, 41, 42, 43}),
             (dict(blocking={"blocked_by": [60], "blocks": [], "loop": [60, 61]}), {40, 5, 52, 60, 61})]
    for kw, want in cases:
        for page in ("issue", "pr"):
            text = draw(page=page, **kw)
            bad = [w for l in text.splitlines() for w in wrapped(l)]
            assert not bad, f"359.4: the {page} card links issues or PRs under words of their own: {bad}"
            named = {n for l in text.splitlines() for n in refs(l)}
            need = want - {40} if page == "issue" else want
            assert need <= named, f"359.4: the {page} card does not show {sorted(need - named)} as GitHub references"


def test_a_merged_pr_card_still_names_both_as_references(record_property):
    """A merged PR's card still names the issue and the PR as references.

    Draws the card once the owner merged the pull request, and checks it links no issue or PR under words of its
    own (the owner approval circle may still link to the merge), and names #40 and #5 as references. Proves 359.4."""
    record_property("proves", "359.4")
    merged = dict(PR, merged=True, state="closed", merged_by={"login": "boss"})
    for page in ("issue", "pr"):
        text = draw(page=page, pr=merged)
        bad = [w for l in text.splitlines() for w in wrapped(l)]
        assert not bad, f"359.4: the merged {page} card links issues or PRs under words of their own: {bad}"
        named = {n for l in text.splitlines() for n in refs(l)}
        assert {40, 5} <= named, f"359.4: the merged {page} card does not show {sorted({40, 5} - named)} as references"


# 359.5: the agents' run comments name every issue, pull request and comment as a GitHub reference too

AGENTS_MD = "https://github.com/o/r/blob/main/AGENTS.md"
META = {"run_id": "7", "run": "https://github.com/o/r/actions/runs/7", "log": "https://x/log", "models": ["claude-opus-5-5"],
        "report": {"duration_ms": 60000, "turns": 3, "cost_usd": 0.5, "tokens_in": 100, "tokens_out": 20}}
QUESTION = {"kind": "question", "to": "owner", "label": "Board column", "text": "Should a cancelled run keep its column?",
            "evidence": "dokima/board.py", "raised_by": "planner", "id": "P17"}
SAID = "a cancelled run stays in its column"
SAID_MD = "Fail closed."
Q_COMMENT, A_COMMENT, M_COMMENT = "Should a failed run move its card?", "The plan assumes it does.", "a failed run lands in Needs you"
Q_MD, A_MD = "Should a broken check block?", "The plan assumes it blocks."
WORK = {"summary": "Slow calls now return a job id.", "criteria": {"40.1": "returns a job id"}, "evidence": "3 passed",
        "raises": [], "answers": []}


def run_rec(role, stage=None, **handback):
    """One passed run's record, as the record step builds it."""
    return {"role": role, "stage": stage, **META, "handback": handback, "check": {"passed": True, "problems": []}}


@pytest.fixture
def env(monkeypatch):
    """The repo and server the run comments are drawn for, as the workflow sets them."""
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")


def shown_lines(body):
    """The lines of a run comment, without its Full record fold.

    That fold's JSON is data, not drawn text."""
    body = re.sub(r"<details><summary>Full record</summary>.*?</details>", "", body, flags=re.S)
    return body.splitlines()


def comments():
    """A run comment of every kind that names an issue, pull request or comment.

    Each comes back as (name, markdown)."""
    planner = run_rec("planner", **PLAN)
    asked = dict(PLAN, questions=[{"question": Q_COMMENT, "assumption": A_COMMENT},
                                  {"question": Q_MD, "assumption": A_MD}])
    plan_review = run_rec("reviewer", "plan", verdict="approve", summary="The plan holds.", blockers=[], notes=[],
                          issues_found=[], asks=[{"ask": "One card.", "source": COMMENT, "criterion": "40.1"}],
                          assumptions=[{"question": Q_COMMENT, "accepted": True, "changes": False,
                                        "matched": M_COMMENT, "source": COMMENT},
                                       {"question": Q_MD, "accepted": True, "changes": False,
                                        "matched": SAID_MD, "source": "AGENTS.md"}])
    asker = run_rec("planner", **dict(PLAN, raises=[QUESTION], answers=[]))
    code_review = run_rec("reviewer", "pr", verdict="approve", summary="The work holds.", asks=[], raises=[],
                          answers=[{"raise": "P17", "answer": "done", "why": "Your words settle it.",
                                    "words": SAID, "source": COMMENT}])
    split = run_rec("split", stories=[{"story": i, "issue": c["number"], "title": c["title"],
                                       "blocked_by": [] if i == 1 else [1]} for i, c in enumerate(CHILDREN, 1)])
    return [("the planner's record", agent.render(planner)),
            ("the plan review's record", agent.render(plan_review, plan=asked)),
            ("the code review's record", agent.render(code_review, earlier=[asker])),
            ("the worker's record", agent.render(run_rec("worker", **WORK), PR["html_url"])),
            ("the split's record", agent.render(split))]


def test_the_workers_comment_names_its_pull_request_as_a_github_reference(record_property, env):
    """The worker's comment names its pull request as a GitHub reference.

    Draws a finished worker's comment with its pull request known, and checks its opening line still holds the
    worker's own sentence, then the pull request's own link written out bare, so GitHub draws it with its icon and
    title, and no link with words of its own such as “pull request #5”. Proves 359.5."""
    record_property("proves", "359.5")
    first = shown_lines(agent.render(run_rec("worker", **WORK), PR["html_url"]))[1]
    assert WORK["summary"] in plain(first), f"359.5: the worker's sentence is gone from its opening line: {first}"
    assert not wrapped(first) and "](" not in first and "<a " not in first, \
        f"359.5: the worker's comment links its pull request under words of its own: {first}"
    assert bare_urls(first) == [PR["html_url"]], \
        f"359.5: the worker's opening line should name {PR['html_url']} written out bare, once: {first}"
    assert "pull request #5" not in first.lower(), f"359.5: the worker's line still writes the words pull request #5: {first}"


def test_a_review_quotes_the_owners_words_then_the_reference_to_where_they_said_them(record_property, env):
    """A review quotes the owner's words, then GitHub's reference to where they said them.

    Draws a plan review that answered a question on the owner's comment and another on AGENTS.md, and a code review
    that answered an earlier raise on the owner's comment. Each Your words line must show the quoted words as plain
    text, not as a link, followed by the comment's own link written out bare; words from AGENTS.md, which is no issue
    or pull request, still link to AGENTS.md on the main branch. Proves 359.5."""
    record_property("proves", "359.5")
    drawn = dict(comments())
    for name, words in (("the plan review's record", M_COMMENT), ("the code review's record", SAID)):
        lines = [l for l in shown_lines(drawn[name]) if "Your words" in l and words in l]
        assert len(lines) == 1, f"359.5: {name} should have one Your words line quoting “{words}”, has {len(lines)}"
        line = lines[0]
        assert not wrapped(line) and "](" not in line and "<a " not in line, \
            f"359.5: {name} links the owner's comment under the quoted words, not as a GitHub reference: {line}"
        assert f'"{words}"' in line, f"359.5: {name} no longer quotes the owner's words “{words}”: {line}"
        assert line.index(f'"{words}"') < line.index(COMMENT), \
            f"359.5: in {name} the reference should follow the quoted words: {line}"
        assert bare_urls(line) == [COMMENT], f"359.5: {name} should name {COMMENT} written out bare, once: {line}"
    md = [l for l in shown_lines(drawn["the plan review's record"]) if "Your words" in l and SAID_MD in l]
    assert len(md) == 1 and re.search(r"\[[^\]]*" + re.escape(SAID_MD) + r"[^\]]*\]\(" + re.escape(AGENTS_MD) + r"\)", md[0]), \
        f"359.5: words quoted from AGENTS.md should still link to {AGENTS_MD}: {md}"


def test_no_run_comment_links_an_issue_or_pr_under_words_of_its_own(record_property, env):
    """No run comment links an issue, pull request or comment under words of its own.

    Draws the planner's, the plan review's, the code review's, the worker's and the split's records, and checks no
    line of any of them links an issue, pull request or comment under words of its own, while each still names what
    it names as a GitHub reference: the reviews the owner's comment, the worker its pull request and the split each
    story it filed. The planner's comment names no issue, since its link lines stay on the card (236.2). Proves 359.5."""
    record_property("proves", "359.5")
    want = {"the planner's record": set(), "the plan review's record": {40}, "the code review's record": {40},
            "the worker's record": {5}, "the split's record": {41, 42, 43}}
    for name, body in comments():
        lines = shown_lines(body)
        bad = [w for l in lines for w in wrapped(l)]
        assert not bad, f"359.5: {name} links issues, PRs or comments under words of their own: {bad}"
        named = {n for l in lines for n in refs(l)}
        assert want[name] <= named, f"359.5: {name} does not show {sorted(want[name] - named)} as GitHub references"

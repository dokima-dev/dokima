"""The issue and PR card shows the plan and its proof, drawn only from the agents' records and GitHub's checks.

Issue #180 (story 2 of #143). The card is drawn by `dokima/card.py` from what GitHub holds, never from the issue's text:

    card.render(repo, issue, found, page="issue")
        issue  {"number": 40, "url": ...}
        found  {"recs":       the agents' records, oldest first (dokima.agent.records),
                "pr":         the PR (GitHub's pulls API) or None,
                "check_runs": GitHub's check runs on the PR's latest commit,
                "reviews":    GitHub's reviews of the PR, oldest first,
                "owners":     the code owners' logins,
                "tests":      {"path::name": {"verified_by": first docstring line or None, "url": link to the test}},
                "worker":     the latest worker run or None}
    card.test_entry(repo, ref, path, source, name)   one entry of found["tests"], read from a test file's source
    card.gather(repo, number, pr_number)             fetches `found` from GitHub; main draws the card from it
        It reads GitHub only through `gh` (card.gh, or agent.gh / plan.gh when it reuses their helpers): the REST API
        (`gh api repos/...`, files through `contents/<path>?ref=<sha>`), `gh issue view`, `gh pr view`, `gh pr list`.
        The code owners are the ones named on the default branch, never on the PR's own commit.
    card.find_work(repo)                             the issue and its PR, asked of GitHub through card.gh

The plan is the newest planner record whose check passed. Criterion k is <issue>.k, the acceptance criteria first and
then the non-functional requirements, and its check is the check run named "<issue>.k · ...".

Layout, as the tests read it (issue #235): each criterion is one bullet line "- " opening with its verdict circle (an
<img> whose alt is its state, never inside a link), then its label, linked to its check when one exists (#354),
then its words; under it,
indented, one "Verified by" line per test with a docstring, where the words Verified by link to the test and the
docstring's first line follows. Markdown links and HTML links read alike. The non-functional requirements sit inside
a <details> fold. The Definition of Done is one line, the last with a circle
on the card: All tests, then review, then owner approval, each a circle (linked when there is a verdict) and its words.
Every circle's alt is one of: passed, failed, running, not started.
"""
import inspect
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import body, card, checks, plan  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
SRC = "https://github.com/o/r/issues/40"
PLAN = {"kind": "user_story",
        "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": "First thing works", "source": SRC},
                                {"text": "Second thing works", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks out", "why": "safety", "principle": "Fail closed"}],
        "scope": ["dokima/card.py", "tests/test_a.py"],
        "out_of_scope": ["The board stays as it is."],
        "tests": {"40.1": ["tests/test_a.py::test_one", "tests/test_a.py::test_one_more"],
                  "40.2": ["tests/test_a.py::test_two"],
                  "40.3": ["tests/test_a.py::test_three"]},
        "test_changes": {}}
TESTS = {"tests/test_a.py::test_one": {"verified_by": "The first thing runs.",
                                       "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L3"},
         "tests/test_a.py::test_one_more": {"verified_by": "The first thing runs twice.",
                                            "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L9"},
         "tests/test_a.py::test_two": {"verified_by": None, "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L15"},
         "tests/test_a.py::test_three": {"verified_by": "Nothing leaks from the run.",
                                         "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L21"}}


def rec(role, stage=None, passed=True, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": passed, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


PLANNED = rec("planner", n=11, **PLAN)
PLAN_OK = rec("reviewer", "plan", n=12, verdict="approve")
BUILT = rec("worker", n=13)
REVIEW_RUN = "https://github.com/o/r/actions/runs/14"
CODE_OK = rec("reviewer", "pr", n=14, verdict="approve")
CODE_BLOCK = rec("reviewer", "pr", n=14, verdict="block", blockers=[])
RECS = [PLANNED, PLAN_OK, BUILT, CODE_OK]
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40"}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
APPROVAL = "https://github.com/o/r/pull/5#pullrequestreview-1"
CHANGES = "https://github.com/o/r/pull/5#pullrequestreview-2"


def review(state, login="boss", url=APPROVAL):
    """One GitHub review of the PR."""
    return {"user": {"login": login}, "state": state, "html_url": url, "submitted_at": "2026-10-08T10:00:00Z"}


def run(name, status="completed", conclusion="success", n=7):
    """One GitHub check run on the PR's latest commit."""
    return {"name": name, "status": status, "conclusion": conclusion,
            "html_url": f"https://github.com/o/r/actions/runs/2/job/{n}"}


def job(n):
    return f"https://github.com/o/r/actions/runs/2/job/{n}"


GREEN = [run("40.1 · First thing works", n=1), run("40.2 · Second thing works", n=2),
         run("40.3 · Nothing leaks out", n=3), run("all tests", n=4)]
FOUND = {"recs": RECS, "pr": PR, "check_runs": GREEN, "reviews": [review("APPROVED")], "owners": {"boss"},
         "tests": TESTS, "worker": DONE}
STATES = {"passed", "failed", "running", "not started"}


def draw(page="issue", **kw):
    """The card for issue #40 with FOUND, any of its parts replaced by `kw`; a plain failure while the card cannot
    be drawn from the records."""
    if list(inspect.signature(card.render).parameters)[:3] != ["repo", "issue", "found"]:
        pytest.fail("the card is not drawn from the records yet: card.render(repo, issue, found) does not exist")
    return card.render(REPO, ISSUE, dict(FOUND, **kw), page=page)


def block(text):
    """The card itself: from its start marker to its end marker."""
    assert plan.CARD_START in text and plan.CARD_END in text, "the text holds no card between its markers"
    done = "\n" + text.rsplit(body.DONE, 1)[1].strip().split("\n")[0] if body.DONE in text else ""
    # Since #416 the Definition of Done sits after the Original issue fold; read it as the card's last line.
    return text[text.index(plan.CARD_START):text.index(plan.CARD_END)] + (done.lstrip("\n") + "\n" if done else "") + plan.CARD_END


def links_as_html(text):
    """The text with every markdown link written as HTML, so both forms read alike."""
    return re.sub(r"\[((?:<img [^>]*>|[^\]])*)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)


def row_of(text, words, k):
    """The bullet line of the criterion whose words are `words`, and the lines under it.

    Links are written as HTML.

    Fails naming criterion k when not exactly one bullet line holds the words."""
    lines = links_as_html(text).splitlines()
    at = [i for i, l in enumerate(lines) if l.startswith("- ") and words in l]
    assert len(at) == 1, f"{k}: expected one bullet line for “{words}”, found {len(at)}"
    under = []
    for line in lines[at[0] + 1:]:
        if not re.match(r"\s+\S", line):
            break
        under.append(line)
    return lines[at[0]], "\n".join(under)


# The icons code draws in front of a field (issue #234), which are never a verdict circle.
FIELD_ICONS = {"planner", "worker", "plan review", "code review", "autopilot", "needs you", "owner approval", "merged",
               "still open", "acceptance criterion", "verified by", "files changed", "question", "blocker", "note",
               "outside the plan", "issue found", "related", "blocked by", "blocks", "stats"}


def alts(html):
    """The states of the verdict circles in `html`, leaving out the field icons."""
    return [a for a in re.findall(r'<img [^>]*alt="([^"]*)"', html) if a not in FIELD_ICONS]


def circle(text, words, k):
    """The state on a criterion's circle, and the link on its label or None.

    Since #354 the only link on the bullet sits on its label (Acceptance criterion or Non-functional requirement),
    never on the criterion's words."""
    first, second = row_of(text, words, k)
    assert len(alts(first)) == 1, f"{k}: the bullet of “{words}” does not hold exactly one circle"
    assert first.index("<img") < first.index(words) and not alts(second), f"{k}: the circle of “{words}” is not its bullet"
    assert not re.search(r'<a href="[^"]+"[^>]*>\s*<img', first), f"{k}: the circle of “{words}” sits inside a link"
    links = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', first)
    assert len(links) <= 1, f"{k}: the bullet of “{words}” holds more than one link: {first}"
    assert not links or links[0][1] in ("Acceptance criterion", "Non-functional requirement"), \
        f"{k}: the link on the bullet of “{words}” is on “{links[0][1]}”, not on its label: {first}"
    return alts(first)[0], links[0][0] if links else None


def dod(text, k):
    """The one Definition of Done line; fails naming criterion k unless it is the last line on the card with a circle."""
    lines = block(text).splitlines()
    found = [i for i, l in enumerate(lines) if "Definition of Done" in l]
    assert len(found) == 1, f"{k}: expected one Definition of Done row, found {len(found)}"
    assert not any("<img" in l for l in lines[found[0] + 1:]), f"{k}: the Definition of Done row is not at the bottom"
    return lines[found[0]]


def write_main(monkeypatch, tmp_path, current, found=FOUND):
    """Run the card's main for issue #40 and its PR #5 against a faked GitHub; the saved issue body and PR body.

    The issue's text is `current`; everything the card is drawn from comes from card.gather, faked to return `found`.
    """
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
             "plan": plan.parse(current), "current_body": current, "body": current}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.setattr(card, "gh", gh)
    monkeypatch.setattr(body, "gh", gh)
    monkeypatch.setattr(card, "find_work", lambda repo: (40, 5))
    monkeypatch.setattr(card, "latest_worker_run", lambda repo, n: DONE)
    monkeypatch.setattr(plan, "fetch_issue", lambda repo, n: issue)
    if not hasattr(card, "gather"):
        pytest.fail("180.1: the card is not drawn from the records yet: card.gather does not exist")
    monkeypatch.setattr(card, "gather", lambda repo, n, pr: found)
    card.main()
    return saved.get("issue"), saved.get("pr")


BOT_LOGIN = "dokima-runtime"
HEAD, OLD = "head1", "old0"
HEAD_SOURCE = ('import os\n\n\ndef test_one(record_property):\n    """The first thing runs.\n\n    More words."""\n'
               '    assert True\n')
MAIN_SOURCE = 'def test_one(record_property):\n    """An old sentence from main."""\n    assert True\n'
HEAD_RUNS = [run("40.1 · First thing works", n=1), run("all tests", n=4)]
OLD_RUNS = [run("40.1 · First thing works", conclusion="failure", n=91), run("all tests", conclusion="failure", n=94)]


def record_comment(login, r, at):
    """A comment holding an agent record, as the bot posts it (or as a person might paste it)."""
    return {"login": login, "at": at,
            "body": f"<!-- dokima-record -->\n**Card**\n\n<details><summary>Full record</summary>\n\n```json\n{json.dumps(r)}\n```\n\n</details>"}


def fake_github(monkeypatch, tmp_path, issue_text, reviews):
    """Fake GitHub for issue #40 and its PR #5, serving card.gh, agent.gh and plan.gh; returns the calls it saw.

    It answers the REST API (`gh api repos/o/r/...`) and `gh issue view` / `gh pr view` / `gh pr list`, the ways
    Dokima reads GitHub today, and fails naming 180.1 on anything else. The issue's text holds a plan of its own; its
    comments hold the planner's and plan reviewer's records, and a person's comment pasting an approving code review;
    the PR's comments hold the worker's and code reviewer's records. The PR's head commit has passing checks; an older
    commit has failing ones. CODEOWNERS names boss and second on main, and intruder on the PR's head. The test file
    reads one way at the PR's head and another on main.
    """
    import base64
    from dokima import agent
    issue_comments = [record_comment(BOT_LOGIN, dict(PLANNED, run_id="11"), "2026-10-08T01:00:00Z"),
                      record_comment(BOT_LOGIN, dict(PLAN_OK, run_id="12"), "2026-10-08T02:00:00Z"),
                      record_comment("mallory", dict(CODE_OK, run_id="66"), "2026-10-08T05:00:00Z")]
    pr_comments = [record_comment(BOT_LOGIN, dict(BUILT, run_id="13"), "2026-10-08T03:00:00Z"),
                   record_comment(BOT_LOGIN, dict(CODE_BLOCK, run_id="14"), "2026-10-08T04:00:00Z")]
    files = {(".github/CODEOWNERS", "main"): "* @boss @second\n", (".github/CODEOWNERS", HEAD): "* @intruder\n",
             ("tests/test_a.py", HEAD): HEAD_SOURCE, ("tests/test_a.py", "main"): MAIN_SOURCE}
    pr = {"number": 5, "state": "open", "merged": False, "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
          "head": {"sha": HEAD, "ref": "try/issue-40"}, "base": {"ref": "main", "sha": "base0"}}
    issue = {"number": 40, "title": "t", "body": issue_text, "html_url": ISSUE["url"], "state": "open"}

    def rest(c):
        return {"user": {"login": c["login"] + ("[bot]" if c["login"] == BOT_LOGIN else ""), "type": "User"},
                "body": c["body"], "created_at": c["at"], "html_url": ISSUE["url"]}

    def cli(c):
        return {"author": {"login": c["login"]}, "body": c["body"], "createdAt": c["at"]}

    def content(path, ref, raw):
        if (path, ref) not in files:
            raise AssertionError(f"180.1: the fake has no {path} at {ref}")
        text = files[(path, ref)]
        return text if raw else json.dumps({"path": path, "encoding": "base64", "content": base64.b64encode(text.encode()).decode()})

    seen = []

    def gh(*args, **kw):
        args = [str(a) for a in args]
        seen.append(args)
        if args[:2] == ["issue", "view"] and args[2] == "40":
            return json.dumps({"number": 40, "title": "t", "body": issue_text, "url": ISSUE["url"],
                               "comments": [cli(c) for c in issue_comments]})
        if args[:2] == ["pr", "view"] and args[2] == "5":
            return json.dumps({"number": 5, "body": pr["body"], "headRefOid": HEAD, "comments": [cli(c) for c in pr_comments],
                               "reviews": [{"author": r["user"], "state": r["state"], "body": "", "submittedAt": r["submitted_at"]}
                                           for r in reviews]})
        if args[:2] == ["pr", "list"]:
            return json.dumps([{"number": 5}] if "try/issue-40" in args else [])
        if args[0] != "api":
            raise AssertionError(f"180.1: card.gather asked GitHub something the fake does not serve: {args}")
        target = next(a for a in args[1:] if a.startswith("repos/") or a.startswith("/repos/")).lstrip("/")
        path, _, query = target.partition("?")
        params = dict(q.split("=", 1) for q in query.split("&") if "=" in q)
        for i, a in enumerate(args):
            if a in ("-f", "-F", "--field", "--raw-field") and args[i + 1].startswith("ref="):
                params["ref"] = args[i + 1][4:]
        raw = any("vnd.github.raw" in a for a in args)
        if path.startswith("repos/o/r/contents/"):
            return content(path[len("repos/o/r/contents/"):], params.get("ref", "main"), raw)
        answers = {"repos/o/r/issues/40": issue, "repos/o/r/issues/40/comments": [rest(c) for c in issue_comments],
                   "repos/o/r/issues/5/comments": [rest(c) for c in pr_comments], "repos/o/r/pulls/5": pr,
                   "repos/o/r/pulls/5/reviews": reviews, "repos/o/r/pulls/5/comments": [],
                   f"repos/o/r/commits/{HEAD}/check-runs": {"total_count": 2, "check_runs": HEAD_RUNS},
                   f"repos/o/r/commits/{OLD}/check-runs": {"total_count": 2, "check_runs": OLD_RUNS},
                   "repos/o/r/pulls": [{"number": 5}] if "try/issue-40" in query.replace("%2F", "/") else [],
                   "repos/o/r/actions/workflows/worker.yml/runs": {"workflow_runs": [
                       {"display_title": "worker for #40", "status": "completed", "conclusion": "success",
                        "html_url": "https://github.com/o/r/actions/runs/13"}]}}
        if path not in answers:
            raise AssertionError(f"180.1: card.gather asked GitHub something the fake does not serve: {args}")
        return json.dumps(answers[path])

    (tmp_path / ".github").mkdir(exist_ok=True)
    (tmp_path / ".github" / "CODEOWNERS").write_text("* @boss @second\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.setattr(agent, "BOT", BOT_LOGIN)
    for module in (card, agent, plan):
        monkeypatch.setattr(module, "gh", gh)
    return seen


def gather(monkeypatch, tmp_path, issue_text="My ask.", reviews=(), k="180.1"):
    """What the real card.gather fetches for issue #40 and PR #5 from the faked GitHub; a plain failure naming
    criterion k while it does not exist."""
    if not hasattr(card, "gather"):
        pytest.fail(f"{k}: the card is not drawn from the records yet: card.gather does not exist")
    fake_github(monkeypatch, tmp_path, issue_text, list(reviews))
    return card.gather(REPO, 40, 5)


def run_ids(recs):
    return [str(r.get("run_id")) for r in recs]


# 180.1: the same card on the issue and its PR, drawn only from the records and the checks

def test_the_issue_text_never_changes_the_card(record_property, monkeypatch, tmp_path):
    """Changing the issue's text never changes the card: it shows the plan from the records, whatever the issue says.

    Runs the card on two issues with the same records but different text, one holding an old plan of its own above
    the marker, and checks both get the same card, showing the records' criteria and none of the issue's words."""
    record_property("proves", "180.1")
    from dokima import body
    old = body.redraw("Ask one.", "- [ ] Objective: an old goal\n  - [ ] Acceptance criteria: old thing works\n"
                                  "    Verified by: an old test\n")
    one, _ = write_main(monkeypatch, tmp_path, old)
    two, _ = write_main(monkeypatch, tmp_path, "A completely different ask.\n- [ ] Goal: another goal\n")
    assert one and two, "180.1: the card saved nothing on the issue"
    assert block(one) == block(two), "180.1: changing the issue's text changed the card"
    assert "First thing works" in block(one), "180.1: the card does not show the plan from the records"
    assert "old thing works" not in block(one) and "another goal" not in block(two), \
        "180.1: the card shows plan words taken from the issue's text"


def test_the_issue_and_its_pr_show_the_same_card(record_property, monkeypatch, tmp_path):
    """The issue and its PR show the same card; only the links row differs, so neither links to its own page.

    Runs the card for an issue with an open PR and checks the card saved on the issue and the one written on the PR
    match line for line, except the links row, and that the PR keeps its line closing the issue."""
    record_property("proves", "180.1")
    record_property("proves", "344.1")
    on_issue, on_pr = write_main(monkeypatch, tmp_path, "My ask.")
    assert on_issue and on_pr, "180.1: the card was not written on both the issue and its PR"
    a, b = block(on_issue).splitlines(), block(on_pr).splitlines()
    assert len(a) == len(b), "180.1: the issue and the PR show cards of different lengths"
    for x, y in zip(a, b):
        # Since #452 the links row differs only by the issue's own link, which the PR's row keeps.
        assert x == y or x == y.replace(" · " + ISSUE["url"] + " · ", " · ", 1), \
            f"180.1: the issue and PR cards differ: “{x}” vs “{y}”"
    assert "Closes" not in on_pr, "180.1: the PR still carries a Closes line (#416 dropped it)"


def test_the_card_finds_the_pr_on_either_branch(record_property, monkeypatch):
    """The card finds the issue's PR whether the worker built it on try/issue-N or on work/issue-N.

    Fakes GitHub so only one of the two branches has a PR, and checks the card finds it each time, so the card
    reaches the PR the agents open today."""
    record_property("proves", "180.1")
    monkeypatch.setenv("ISSUE_NUMBER", "40")
    for branch in ("try/issue-40", "work/issue-40"):
        monkeypatch.setattr(card, "gh", lambda *a, b=branch: '[{"number": 7}]' if any(f"head=o:{b}" in x for x in a) else "[]")
        assert card.find_work(REPO) == (40, 7), f"180.1: the card did not find the PR built on {branch}"



def test_the_card_fetches_only_the_bots_records_and_the_latest_commits_checks(record_property, monkeypatch, tmp_path):
    """The card fetches only the bot's records and the checks of the PR's latest commit, never the issue's text.

    Runs the real card.gather against a faked GitHub where the issue's text holds a plan of its own, a person pasted
    an approving review record, and an older commit has failing checks. Checks it holds exactly the bot's four
    records from the issue and the PR in order, only the latest commit's checks, each test's Verified by read at that
    commit, and that a different issue text changes nothing it fetched."""
    record_property("proves", "180.1")
    own_plan = ("**User story:** an issue text story\n\n**Acceptance criteria:**\n- Issue text thing works\n"
                "- [ ] Objective: issue text goal\n")
    found = gather(monkeypatch, tmp_path, own_plan)
    assert run_ids(found["recs"]) == ["11", "12", "13", "14"], \
        f"180.1: expected only the bot's records 11, 12, 13, 14 in order, got {run_ids(found['recs'])}"
    assert "Issue text thing" not in json.dumps(found, default=str), "180.1: the card fetched plan words from the issue's text"
    urls = sorted(r["html_url"] for r in found["check_runs"])
    assert urls == sorted(r["html_url"] for r in HEAD_RUNS), f"180.1: the checks are not the PR's latest commit's: {urls}"
    assert found["pr"]["number"] == 5, "180.1: the card did not fetch the PR"
    entry = found["tests"].get("tests/test_a.py::test_one")
    assert entry == {"verified_by": "The first thing runs.", "url": "https://github.com/o/r/blob/head1/tests/test_a.py#L4"}, \
        f"180.1: Verified by was not read from the test at the PR's latest commit: {entry}"
    again = gather(monkeypatch, tmp_path, "A completely different ask, with no plan at all.")
    assert json.dumps(again, default=sorted, sort_keys=True) == json.dumps(found, default=sorted, sort_keys=True), \
        "180.1: changing the issue's text changed what the card is drawn from"
    text = card.render(REPO, ISSUE, found, page="issue")
    assert "First thing works" in text and "Issue text thing" not in text, "180.1: the card is not drawn from the records"


# 180.2: the user story, then each criterion with its circle hanging outside it, linked, and its Verified by

def test_the_user_story_comes_first_then_the_criteria(record_property):
    """The card shows the user story first, then the acceptance criteria in the plan's order.

    Draws the card and checks the user story, labelled, sits above the first criterion, and the criteria follow in
    the order the plan lists them."""
    record_property("proves", "180.2")
    text = draw()
    assert "User story" in text and PLAN["user_story"] in text, "180.2: the card does not show the user story"
    first, second = text.find("First thing works"), text.find("Second thing works")
    assert 0 <= text.find(PLAN["user_story"]) < first < second, "180.2: the user story and criteria are not in order"


def test_each_criterion_has_its_circle_as_its_bullet_and_its_label_links_its_check(record_property):
    """Each criterion's verdict circle opens its bullet, and its label links to its check.

    Draws the card with one criterion passed and one failed, and checks each criterion's circle opens its own bullet
    outside any link, shows that criterion's own verdict, and its label links to that criterion's own check."""
    record_property("proves", "180.2")
    checks_ = [run("40.1 · First thing works", n=1), run("40.2 · Second thing works", conclusion="failure", n=2)]
    text = draw(check_runs=checks_)
    assert circle(text, "First thing works", "180.2") == ("passed", job(1)), "180.2: criterion 1's circle is wrong"
    assert circle(text, "Second thing works", "180.2") == ("failed", job(2)), "180.2: criterion 2's circle is wrong"


def test_verified_by_is_each_tests_first_docstring_line_and_links_to_the_test(record_property):
    """Under each criterion, Verified by shows each test's sentence and links to the test.

    Draws the card for a criterion proved by two tests and checks both sentences are under the criterion, each on
    its own Verified by line whose words Verified by link to its own test."""
    record_property("proves", "180.2")
    _, words = row_of(draw(), "First thing works", "180.2")
    assert "Verified by" in words, "180.2: the criterion does not say Verified by"
    for t in ("tests/test_a.py::test_one", "tests/test_a.py::test_one_more"):
        line = next((l for l in words.splitlines() if TESTS[t]["verified_by"] in l), "")
        link = re.search(rf'<a href="{re.escape(TESTS[t]["url"])}"[^>]*>(.*?)</a>', line)
        assert link and "Verified by" in link.group(1), f"180.2: Verified by does not link “{TESTS[t]['verified_by']}” to {t}"


def test_verified_by_is_hidden_when_there_is_none(record_property):
    """Verified by is hidden for a criterion whose tests have no docstring, or that has no test at all.

    Draws the card where criterion 2's only test has no docstring, then where it has no test listed, and checks its
    cell never says Verified by, while criterion 1's still does."""
    record_property("proves", "180.2")
    _, words = row_of(draw(), "Second thing works", "180.2")
    assert "Verified by" not in words, "180.2: Verified by shown for a test with no docstring"
    bare = dict(PLAN, tests={k: v for k, v in PLAN["tests"].items() if k != "40.2"})
    text = draw(recs=[rec("planner", n=11, **bare), PLAN_OK])
    assert "Verified by" not in row_of(text, "Second thing works", "180.2")[1], "180.2: Verified by shown with no test"
    assert "Verified by" in row_of(text, "First thing works", "180.2")[1], "180.2: Verified by hidden where there is one"


def test_a_tests_verified_by_is_its_first_docstring_line(record_property):
    """A test's Verified by is the first line of its docstring, and its link points at the test's line.

    Reads a test file's source and checks the entry holds the docstring's first line only and a link to the line the
    test starts on at the given commit; a test with no docstring, or not in the file, has none."""
    record_property("proves", "180.2")
    source = ('import os\n\n\ndef test_one(record_property):\n    """The first thing runs.\n\n    More words."""\n'
              '    assert True\n\n\ndef test_two():\n    assert True\n')
    assert hasattr(card, "test_entry"), "180.2: the card cannot read a test's Verified by yet: card.test_entry does not exist"
    one = card.test_entry(REPO, "abc123", "tests/test_a.py", source, "test_one")
    assert one == {"verified_by": "The first thing runs.",
                   "url": "https://github.com/o/r/blob/abc123/tests/test_a.py#L4"}, f"180.2: wrong entry for a test: {one}"
    assert card.test_entry(REPO, "abc123", "tests/test_a.py", source, "test_two")["verified_by"] is None, \
        "180.2: a test with no docstring got a Verified by"
    assert card.test_entry(REPO, "abc123", "tests/test_a.py", source, "test_gone")["verified_by"] is None, \
        "180.2: a test missing from its file got a Verified by"


# 180.3: every check shows exactly one of passed, failed, running or not started, as GitHub reports it

def test_each_criterion_shows_the_state_github_reports(record_property):
    """Each criterion's circle shows passed, failed, running or not started, exactly as GitHub reports its check.

    Draws the card with criterion 1's check in each of GitHub's states and checks the circle: missing or queued is
    not started, in progress is running, success is passed, failure is failed."""
    record_property("proves", "180.3")
    cases = [(None, "not started"), (run("40.1 · First thing works", "queued", None, n=1), "not started"),
             (run("40.1 · First thing works", "in_progress", None, n=1), "running"),
             (run("40.1 · First thing works", n=1), "passed"),
             (run("40.1 · First thing works", conclusion="failure", n=1), "failed")]
    for check, want in cases:
        got, link = circle(draw(check_runs=[check] if check else []), "First thing works", "180.3")
        assert got == want, f"180.3: GitHub's {check and (check['status'], check['conclusion'])} showed as {got}, not {want}"
        if check and want != "not started":
            assert link == job(1), f"180.3: the {want} circle does not link to its check"


def test_all_tests_shows_the_state_github_reports(record_property):
    """The All tests check in the Definition of Done row shows the same four states as GitHub reports.

    Draws the card with the all tests check missing, queued, in progress, passed and failed, and checks the row's first
    circle each time."""
    record_property("proves", "180.3")
    record_property("proves", "344.2")
    cases = [(None, "not started"), (run("all tests", "queued", None, n=4), "not started"),
             (run("all tests", "in_progress", None, n=4), "running"), (run("all tests", n=4), "passed"),
             (run("all tests", conclusion="failure", n=4), "failed")]
    for check, want in cases:
        row = dod(draw(check_runs=[check] if check else []), "180.3")
        assert alts(row)[:1] == [want], f"180.3: All tests showed {alts(row)[:1]} for GitHub's {check and check['status']}, not {want}"


def test_every_circle_is_one_of_the_four_states(record_property):
    """Every circle on the card is one of passed, failed, running or not started, and its icon exists.

    Draws cards with checks in every state and checks every circle's state is one of the four and its icon file is
    one of Dokima's own."""
    record_property("proves", "180.3")
    mixed = [run("40.1 · First thing works", "in_progress", None, n=1), run("40.2 · Second thing works", conclusion="failure", n=2)]
    for text in (draw(), draw(check_runs=mixed, reviews=[], recs=RECS[:3]), draw(check_runs=[], recs=[])):
        for alt in alts(block(text)):
            assert alt in STATES, f"180.3: a circle shows “{alt}”, not one of the four states"
        for src in re.findall(r'<img [^>]*src="[^"]*/icons/([^"/]+)"', text):
            assert os.path.exists(os.path.join(ROOT, "dokima", "icons", src)), f"180.3: the circle icon {src} does not exist"
    assert sorted(set(alts(draw(check_runs=mixed, reviews=[], recs=RECS[:3])))) == ["failed", "not started", "running"], \
        "180.3: the card does not show running, failed and not started where GitHub reports them"


# 180.4: non-functional in a fold, Scope and Out of scope once planned, one Definition of Done row at the bottom

def test_non_functional_requirements_sit_in_a_fold(record_property):
    """Non-functional requirements sit in a fold, with their own circles; the acceptance criteria stay outside it.

    Draws the card and checks the non-functional requirement is inside a <details> fold with its verdict circle,
    and no acceptance criterion is inside any fold."""
    record_property("proves", "180.4")
    text = draw(check_runs=GREEN[:2] + [run("40.3 · Nothing leaks out", conclusion="failure", n=3)] + GREEN[3:])
    folds = re.findall(r"<details.*?</details>", block(text), re.S)
    assert any("Nothing leaks out" in f for f in folds), "180.4: the non-functional requirement is not in a fold"
    assert not any("First thing works" in f or "Second thing works" in f for f in folds), \
        "180.4: an acceptance criterion is folded away"
    assert circle(text, "Nothing leaks out", "180.4") == ("failed", job(3)), "180.4: the folded requirement lost its circle"


def test_scope_and_out_of_scope_appear_once_planned(record_property):
    """Scope and Out of scope appear once there is a plan, and not before.

    Draws the card with no plan, with only a plan that failed its check, and with a passed plan, and checks Scope and
    Out of scope with their entries show only in the last."""
    record_property("proves", "180.4")
    for recs in ([], [rec("planner", passed=False, n=11, **PLAN)]):
        text = block(draw(recs=recs, check_runs=[], reviews=[]))
        assert "Scope" not in text and "Out of scope" not in text and "dokima/card.py" not in text, \
            "180.4: Scope shows before there is a plan"
    text = block(draw())
    assert "Scope" in text and "Out of scope" in text, "180.4: the planned card has no Scope or Out of scope"
    for entry in PLAN["scope"] + PLAN["out_of_scope"]:
        assert entry in text, f"180.4: the planned card does not list “{entry}”"


def test_definition_of_done_row_shows_all_tests_review_and_owner_approval(record_property):
    """One Definition of Done row at the bottom shows All tests, review and owner approval, each with its verdict and link.

    Draws the card three ways and checks the one row at the bottom names the three in order, each circle shows
    that item's own verdict (passed, failed or not started), and each verdict links to its proof."""
    record_property("proves", "180.4")
    row = dod(draw(recs=[PLANNED, PLAN_OK, BUILT, CODE_BLOCK], reviews=[review("APPROVED")]), "180.4")
    words = row.lower()
    assert 0 <= row.find("All tests") < words.find("review") < words.find("approval"), \
        "180.4: the row does not show All tests, review and owner approval in order"
    assert alts(row) == ["passed", "failed", "passed"], f"180.4: wrong verdicts {alts(row)} for passed, blocked, approved"
    for url in (job(4), REVIEW_RUN, APPROVAL):
        assert url in row, f"180.4: the Definition of Done row does not link {url}"
    row = dod(draw(check_runs=[run("all tests", conclusion="failure", n=4)], recs=RECS,
                   reviews=[review("CHANGES_REQUESTED", url=CHANGES)]), "180.4")
    assert alts(row) == ["failed", "passed", "failed"], f"180.4: wrong verdicts {alts(row)} for failed, approved, changes asked"
    assert CHANGES in row and REVIEW_RUN in row, "180.4: a verdict in the row does not link to its proof"
    row = dod(draw(check_runs=[], recs=[PLANNED, PLAN_OK], reviews=[]), "180.4")
    assert alts(row) == ["not started"] * 3, f"180.4: wrong verdicts {alts(row)} before anything ran"


# 180.5: the words are acceptance criteria, user story and All tests, never Objective or Full suite

def test_the_card_and_check_names_use_the_agreed_words(record_property):
    """The card says User story, Acceptance criteria and All tests, and never Objective or Full suite; neither do checks.

    Draws the card with and without a plan and checks its words, then checks the names GitHub gives the criterion
    checks and the all tests check."""
    record_property("proves", "180.5")
    planned = block(draw())
    for want in ("User story", "Acceptance criteria", "All tests"):
        assert want in planned, f"180.5: the card does not say {want}"
    for text in (planned, block(draw(recs=[], check_runs=[], reviews=[]))):
        for banned in ("objective", "full suite"):
            assert banned not in text.lower(), f"180.5: the card says “{banned}”"
    names = [r["name"] for r in checks.build_matrix(40, RECS) + checks.build_matrix(40, [])]
    yml = open(os.path.join(ROOT, ".github", "workflows", "full-suite.yml")).read()
    jobs = re.findall(r"^    name:\s*(.+)$", yml, re.M)
    assert [j.lower() for j in jobs] == ["all tests"], f"180.5: the all tests check is named {jobs}"
    for name in names + jobs:
        assert "objective" not in name.lower() and "full suite" not in name.lower(), f"180.5: a check is named “{name}”"


# 180.6: a missing or failed check never shows as passed

def test_a_missing_or_failed_check_never_shows_as_passed(record_property):
    """A missing check, or one GitHub finished without success, never shows as passed.

    Draws the card with criterion 1's and the all tests checks missing, then finished as each kind of non-success
    GitHub reports, and checks neither ever shows passed."""
    record_property("proves", "180.6")
    assert circle(draw(check_runs=[]), "First thing works", "180.6")[0] != "passed", "180.6: a missing check showed passed"
    assert alts(dod(draw(check_runs=[]), "180.6"))[0] != "passed", "180.6: a missing All tests showed passed"
    for end in ("failure", "neutral", "skipped", "cancelled", "timed_out", "action_required", "stale", None):
        runs = [run("40.1 · First thing works", conclusion=end, n=1), run("all tests", conclusion=end, n=4)]
        assert circle(draw(check_runs=runs), "First thing works", "180.6")[0] == "failed", \
            f"180.6: a check that ended {end} did not show failed"
        assert alts(dod(draw(check_runs=runs), "180.6"))[0] == "failed", f"180.6: All tests that ended {end} did not show failed"


def test_a_missing_stale_or_unproven_review_never_shows_as_passed(record_property):
    """The review and the owner's approval show passed only on a current approval by the reviewer and a code owner.

    Draws the card with the code review older than the latest build, with an approval whose record failed its check,
    with an approval from someone who is not a code owner, and with an owner's approval later withdrawn by asking for
    changes, and checks none shows passed."""
    record_property("proves", "180.6")
    record_property("proves", "344.2")
    stale = dod(draw(recs=[PLANNED, PLAN_OK, BUILT, CODE_OK, rec("worker", n=15)]), "180.6")
    assert alts(stale)[1] != "passed", "180.6: a review of an older build showed passed"
    unproven = dod(draw(recs=[PLANNED, PLAN_OK, BUILT, rec("reviewer", "pr", passed=False, n=14, verdict="approve")]), "180.6")
    assert alts(unproven)[1] != "passed", "180.6: a review whose record failed its check showed passed"
    stranger = dod(draw(reviews=[review("APPROVED", login="someone")]), "180.6")
    assert alts(stranger)[2] != "passed", "180.6: an approval by someone not a code owner showed passed"
    withdrawn = dod(draw(reviews=[review("APPROVED"), review("CHANGES_REQUESTED", url=CHANGES)]), "180.6")
    assert alts(withdrawn)[2] == "failed", "180.6: an owner's approval withdrawn by asking for changes did not show failed"
    assert alts(dod(draw(), "180.6"))[1:] == ["passed", "passed"], "180.6: a current approval did not show passed"


def test_only_a_code_owner_on_main_makes_the_approval_pass(record_property, monkeypatch, tmp_path):
    """Only an approval by a code owner named on main shows passed; anyone else's, even one the PR names, never does.

    Runs the real card.gather against a faked GitHub whose CODEOWNERS names boss and second on main, while the PR's
    own commit names intruder. Checks the owners fetched are boss and second, that approvals by someone and by
    intruder leave the owner approval not passed on the card, and that boss's approval makes it pass."""
    record_property("proves", "180.6")
    others = [review("APPROVED", login="someone"), review("APPROVED", login="intruder")]
    found = gather(monkeypatch, tmp_path, reviews=others, k="180.6")
    assert set(found["owners"]) == {"boss", "second"}, f"180.6: the code owners fetched are {found['owners']}, not boss and second from main"
    assert [r["user"]["login"] for r in found["reviews"]] == ["someone", "intruder"], "180.6: the PR's reviews were not fetched"
    assert alts(dod(card.render(REPO, ISSUE, found, page="pr"), "180.6"))[2] != "passed", \
        "180.6: an approval by someone who is not a code owner showed passed"
    found = gather(monkeypatch, tmp_path, reviews=[review("APPROVED")], k="180.6")
    assert alts(dod(card.render(REPO, ISSUE, found, page="pr"), "180.6"))[2] == "passed", \
        "180.6: a code owner's approval did not show passed"

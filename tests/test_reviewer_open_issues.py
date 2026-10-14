"""The reviewer starts with every open issue, and names only those as searched (#621).

Story 1 of #615. Before the reviewer files an issue it must search the open issues for the same cause; the owner asked
that code build what this needs before the run: the open issues with their titles, summaries and links, and which ones
Dokima filed, so the reviewer searches that and not GitHub live.

What the code these tests run must do, as the plan pins it:
- `agent.pack(repo, n, "reviewer", stage, dest)`, for the plan review (stage "plan") and the code review (stage "pr"),
  writes dest/open_issues.json: a list with one object per open issue of the repo (pull requests left out, every page),
  each with "number", "title", "summary", "link" (the issue's page on GitHub) and "filed_by_dokima" (true or false).
- An issue's summary is the sentence its card opens with, the plan's summary, when its card has one; otherwise the
  user story of a split's story; otherwise the first sentence of the owner's ask; an empty body gives "".
- An issue counts as filed by Dokima when Dokima's bot opened it (its author is `dokima-runtime[bot]`).
- When GitHub cannot list the open issues, the reviewer's pack fails with GitHub's error and writes no open_issues.json.
- An issue raise in a review may carry "searched", a list of issue numbers. `agent check review FILE PLAN N` accepts
  it, and `agent check-round reviewer FILE PACK` rejects (exit 1) a review whose "searched" names a number that is
  not in PACK/open_issues.json, naming that number and saying it is not in the pack; it rejects "searched" that is not
  a list of numbers, naming the field, and a review naming searched issues against a pack with no open_issues.json,
  naming that file.

GitHub is faked: `gh issue view` and `gh pr list` answer for issue 9, the parent lookup finds none, and
`gh api repos/o/r/issues` serves the open issues (and one pull request) the way GitHub's API does, paging at
`per_page` unless `--paginate` is given. Any other GitHub call fails the test naming it.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import agent  # noqa: E402
from dokima import agent_github  # noqa: E402
from tests.test_raise_handbacks import FOUND, check_handback, review, run_agent  # noqa: E402

N = 9
BOT = {"login": "dokima-runtime[bot]", "type": "Bot"}
OWNER = {"login": "owner", "type": "User"}

# A planned issue, its body as the card draws it on GitHub: the plan's summary opens the card.
PLANNED = ("<!-- dokima-card -->\n<!-- dokima-blocking: {\"blocked_by\": [], \"blocks\": [], \"loop\": []} -->\n"
           "Slow calls hand back a job id instead of timing out.\n\n**Plan** · Needs you: Say /work to build the plan\n\n"
           "**Scope:**\n\n<!-- dokima-folded -->\n<!-- /dokima-card -->\n\n<!-- dokima-ask -->\n"
           "<details><summary>Original issue</summary>\n\nMake slow calls fast. Nobody should wait.\n\n</details>\n\n"
           "<!-- dokima-done -->\n**Definition of Done:** All tests · Code review · Owner approval")
# An issue Dokima filed from a reviewer's raise, as `agent.file_issues` writes it, before any card.
FILED = ("The README still names the old command. It moved last week.\n\n**Evidence:** README.md\n\n"
         "The reviewer found it on #9.")
# A story filed by a split, its body as `agent.story_body` writes it, with the card drawn above it.
STORY_BODY = ("<!-- dokima-card -->\n**Backlog**\n\n<!-- /dokima-card -->\n\n<!-- dokima-ask -->\n"
              "<details><summary>Original issue</summary>\n\n<!-- dokima-card -->\n<!-- /dokima-card -->\n\n"
              "<details open><summary>From the approved plan of #20, story 1</summary>\n\n"
              "**Part of:** #20 Slow calls\n\n**User story:** The owner sees each slow call's job on its card.\n\n"
              "**Acceptance criteria:**\n- A slow call shows its job. ([source](https://github.com/o/r/issues/20))\n\n"
              "</details>\n\n</details>\n\n<!-- dokima-done -->\n**Definition of Done:** All tests")
# An owner's fresh ask, never redrawn, so it has no marker yet.
FRESH = "Paint the door blue. It is red now.\n\nThe paint is in the shed."

ISSUES = {12: ("Slow calls", PLANNED, OWNER), 13: ("The README names the old command", FILED, BOT),
          16: ("Slow call jobs", STORY_BODY, BOT), 15: ("Paint the door", FRESH, OWNER), 18: ("Empty", None, OWNER)}
SUMMARIES = {12: "Slow calls hand back a job id instead of timing out.", 13: "The README still names the old command.",
             16: "The owner sees each slow call's job on its card.", 15: "Paint the door blue.", 18: ""}
FILLER = range(100, 230)  # more open issues than one page of GitHub's answer holds


def api_issue(n):
    """One open issue as GitHub's REST API lists it."""
    title, body, user = ISSUES.get(n, (f"Issue title {n}", f"Issue body {n}.", OWNER))
    return {"number": n, "title": title, "body": body, "user": user, "state": "open", "labels": [],
            "html_url": f"https://github.com/o/r/issues/{n}"}


def fake_github(monkeypatch, fail=False):
    """Fake GitHub for agent.gh: issue 9 alone, and the open issues above.

    Issue 9 has no comments, no pull request and no parent.

    With fail set, listing the open issues fails as a GitHub outage would."""
    numbers = sorted([*ISSUES, *FILLER])

    def gh(*args):
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": N, "title": "T", "body": "Paint the door blue.", "comments": []})
        if args[:2] == ("pr", "list"):
            return "[]"
        if args[0] == "api" and "/parent" in args[1]:
            raise subprocess.CalledProcessError(1, "gh", stderr="HTTP 404: Not Found")
        if args[0] == "api" and re.match(r"/?repos/o/r/issues(\?|$)", args[1]):
            if fail:
                raise subprocess.CalledProcessError(1, ["gh", *args], "", "HTTP 502: Bad Gateway")
            items = [api_issue(n) for n in numbers] + [dict(api_issue(300), pull_request={"url": "u"})]
            if "--paginate" in args:
                return json.dumps([items] if "--slurp" in args else items)
            q = parse_qs(urlparse(args[1]).query)
            per, page = int(q.get("per_page", ["30"])[0]), int(q.get("page", ["1"])[0])
            return json.dumps(items[(page - 1) * per:page * per])
        raise AssertionError(f"unexpected GitHub call: gh {' '.join(map(str, args))}")
    monkeypatch.setattr(agent_github, "gh", gh)


def reviewer_pack(monkeypatch, where, stage):
    """Build the reviewer's starting pack for issue 9 at this stage, as a run does."""
    fake_github(monkeypatch)
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    dest = str(where / f"pack-{stage}")
    agent.pack("o/r", N, "reviewer", stage, dest)
    return dest


def listed(pack, criterion):
    """The open issues the pack lists, by number; fails naming the criterion without one."""
    path = os.path.join(pack, "open_issues.json")
    assert os.path.isfile(path), f"{criterion}: the reviewer's pack has no open_issues.json listing the open issues"
    got = json.load(open(path))
    assert isinstance(got, list) and all(isinstance(i, dict) for i in got), \
        f"{criterion}: open_issues.json is not a list of issues, one object each"
    return {i.get("number"): i for i in got}


@pytest.mark.parametrize("stage", ["plan", "pr"])
def test_the_reviewers_pack_lists_every_open_issue_with_its_title_summary_and_link(record_property, tmp_path,
                                                                                   monkeypatch, stage):
    """The reviewer starts with every open issue, its title, summary and link.

    Builds the plan review's and the code review's pack from a faked repo with 135 open issues (more than one page)
    and one pull request, and reads open_issues.json: it lists exactly the open issues and no pull request, each with
    its own title and its link on GitHub. Each summary is the right sentence for the issue's shape: the sentence a
    planned issue's card opens with (never its ask), a split story's user story, the first sentence of an issue Dokima
    filed from a raise, the first sentence of a fresh ask with no card, and nothing for an empty issue.

    Proves 621.1."""
    record_property("proves", "621.1")
    by_number = listed(reviewer_pack(monkeypatch, tmp_path, stage), "621.1")
    want = sorted([*ISSUES, *FILLER])
    assert 300 not in by_number, "621.1: open_issues.json lists pull request #300"
    assert sorted(by_number) == want, (f"621.1: the {stage} review's pack lists {len(by_number)} issues, not all "
                                       f"{len(want)} open ones (missing e.g. {sorted(set(want) - set(by_number))[:5]})")
    for n, i in by_number.items():
        assert i.get("title") == api_issue(n)["title"], f"621.1: #{n} is listed with the title {i.get('title')!r}"
        assert i.get("link") == f"https://github.com/o/r/issues/{n}", f"621.1: #{n} is listed with the link {i.get('link')!r}"
        assert isinstance(i.get("summary"), str), f"621.1: #{n} is listed with no summary: {i}"
    for n, summary in SUMMARIES.items():
        assert by_number[n]["summary"] == summary, \
            f"621.1: #{n}'s summary in the {stage} review's pack is {by_number[n]['summary']!r}, not {summary!r}"
    assert by_number[150]["summary"] == "Issue body 150.", \
        f"621.1: a plain ask's summary is {by_number[150]['summary']!r}, not its first sentence"


def test_the_reviewers_pack_fails_when_github_cannot_list_the_open_issues(record_property, tmp_path, monkeypatch):
    """When GitHub cannot list open issues, the reviewer's pack fails, never lists none.

    Fakes GitHub answering 502 to the open issues list: building the plan review's pack must fail with GitHub's error
    and leave no open_issues.json behind, so the reviewer never searches a list that is silently empty.

    Proves 621.1."""
    record_property("proves", "621.1")
    fake_github(monkeypatch, fail=True)
    dest = tmp_path / "pack"
    try:
        agent.pack("o/r", N, "reviewer", "plan", str(dest))
    except AssertionError:
        raise
    except Exception as e:  # noqa: BLE001
        assert isinstance(e, subprocess.CalledProcessError) or "502" in str(e), \
            f"621.1: the reviewer's pack failed without GitHub's error: {e!r}"
    else:
        pytest.fail("621.1: the reviewer's pack was built though GitHub could not list the open issues")
    assert not (dest / "open_issues.json").exists(), \
        "621.1: the reviewer's pack wrote open_issues.json though GitHub could not list the open issues"


@pytest.mark.parametrize("stage", ["plan", "pr"])
def test_each_open_issue_in_the_reviewers_pack_says_whether_dokima_filed_it(record_property, tmp_path, monkeypatch,
                                                                            stage):
    """Each open issue in the reviewer's pack says whether Dokima filed it.

    Builds the plan review's and the code review's pack from a faked repo where Dokima's bot opened #13 (from a raise)
    and #16 (a split's story) and the owner opened the rest. Each listed issue must carry filed_by_dokima as true or
    false: true for exactly #13 and #16, false for every other one.

    Proves 621.2."""
    record_property("proves", "621.2")
    by_number = listed(reviewer_pack(monkeypatch, tmp_path, stage), "621.2")
    for n, i in by_number.items():
        assert isinstance(i.get("filed_by_dokima"), bool), \
            f"621.2: #{n} in the {stage} review's pack does not say whether Dokima filed it: {i}"
    filed = sorted(n for n, i in by_number.items() if i["filed_by_dokima"])
    assert filed == [13, 16], f"621.2: the {stage} review's pack says Dokima filed {filed}, not exactly #13 and #16"


def searched_review(searched):
    """A code review raising one issue, with its searched issues and verdict."""
    return review("approve", "pr", raises=[{**FOUND, "searched": searched, "verdict": "new"}])


def both_checks(tmp_path, handback, pack):
    """Run a review run's two checks, its own then the round check; return (code, output)."""
    code, out = check_handback(tmp_path, "review", handback)
    if code:
        return code, out
    f = os.path.join(tempfile.mkdtemp(dir=tmp_path), "review.json")
    json.dump(handback, open(f, "w"))
    return run_agent("check-round", "reviewer", f, pack)


def test_a_review_naming_a_searched_issue_not_in_its_pack_is_rejected_saying_why(record_property, tmp_path,
                                                                                 monkeypatch):
    """A review naming a searched issue not in its pack is rejected, saying why.

    Builds the code review's pack, then runs the checks a review's run does on a review that raises an issue: naming
    searched issues #12 and #15, both in the pack, passes (exit 0). Naming #12 and #999, which is no open issue, is
    rejected (exit 1) naming 999 and saying it is not in the pack; naming pull request #300 is rejected the same way.

    Proves 621.3."""
    record_property("proves", "621.3")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    code, out = both_checks(tmp_path, searched_review([12, 15]), pack)
    assert code == 0, f"621.3: a review naming searched issues #12 and #15, both in its pack, was rejected:\n{out}"
    for bad in (999, 300):
        code, out = both_checks(tmp_path, searched_review([12, bad]), pack)
        assert "Traceback" not in out, f"621.3: the check crashed on a searched issue #{bad}:\n{out[-600:]}"
        assert code == 1, f"621.3: a review naming searched issue #{bad}, not in its pack, passed"
        assert re.search(rf"\b{bad}\b", out) and "pack" in out, \
            f"621.3: the rejection of searched issue #{bad} does not name it and say it is not in the pack:\n{out}"
        assert not re.search(r"(?<!\d)(12)(?!\d)", out), f"621.3: the rejection also names #12, which is in the pack:\n{out}"


def test_searched_issues_that_are_not_a_list_of_numbers_are_rejected(record_property, tmp_path, monkeypatch):
    """Searched issues not written as a list of numbers are rejected, naming the field.

    Builds the code review's pack, then runs the checks on a review whose issue raise names its searched issues as one
    number, as a number written as text and as true: each is rejected (exit 1) naming searched, never with a crash,
    while the same review naming them as a list of numbers passes.

    Proves 621.3."""
    record_property("proves", "621.3")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    code, out = both_checks(tmp_path, searched_review([12]), pack)
    assert code == 0, f"621.3: a review naming searched issue #12 as a list of numbers was rejected:\n{out}"
    for name, searched in (("one number", 12), ("a number written as text", ["12"]), ("true as a number", [True])):
        code, out = both_checks(tmp_path, searched_review(searched), pack)
        assert "Traceback" not in out, f"621.3: the check crashed on searched as {name}:\n{out[-600:]}"
        assert code == 1 and "searched" in out, \
            f"621.3: searched as {name} was not rejected naming the field (exit {code}):\n{out}"


def test_searched_issues_are_rejected_when_the_pack_has_no_open_issues(record_property, tmp_path, monkeypatch):
    """Searched issues are rejected, naming open_issues.json, when the pack lists no open issues.

    Builds the code review's pack and removes its open_issues.json, then runs the checks on a review naming searched
    issue #12: with nothing to check it against, it is rejected (exit 1) naming open_issues.json.

    Proves 621.3."""
    record_property("proves", "621.3")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    path = os.path.join(pack, "open_issues.json")
    if os.path.exists(path):
        os.remove(path)
    code, out = both_checks(tmp_path, searched_review([12]), pack)
    assert "Traceback" not in out, f"621.3: the check crashed on a pack with no open issues:\n{out[-600:]}"
    assert code == 1 and "open_issues.json" in out, \
        f"621.3: a review naming searched issues against a pack with no open_issues.json was not rejected naming it (exit {code}):\n{out}"

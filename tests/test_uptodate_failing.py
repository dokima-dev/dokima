"""A pull request whose tests already fail is not updated on every merge (#523).

After every merge to main, `dokima.uptodate.run(repo, base, sha, rest=...)` calls GitHub's Update branch on every open
PR behind main. On Oct 11 it merged main into #316 22 times, though that PR's all tests check failed on its head every
time for reasons main could not fix, and every merge reran its checks. These tests fake GitHub through the same
`rest(method, path, **fields)` seam as tests/test_uptodate.py and run several merges in a row against one fake.

The PRs are Dokima's own: PR 10*N is built from branch try/issue-N of this repo, so its issue is N.

The fake GitHub answers:
  - GET .../pulls: the open PRs; GET .../compare/BASE...HEAD: behind by one commit;
  - GET .../commits/SHA/check-runs (check_name= honoured, empty past page 1): the check runs on that commit;
  - PUT .../pulls/N/update-branch (expected_head_sha): 202, and records it;
  - GET .../issues/N/comments (empty past page 1): the comments on issue or PR N, REST-shaped, oldest first;
  - POST .../issues/N/comments, PATCH and DELETE .../issues/comments/ID: kept as GitHub would;
  - GET .../issues/N: an open issue with no labels; GET .../commits/SHA/pulls: no PR.
"""
import os
import re
import sys
from urllib.parse import parse_qs, unquote

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dokima import agent  # noqa: E402

REPO = "o/r"
BOT = f"{agent.BOT}[bot]"
M1, M2, M3 = "a1b2c3d" + "1" * 33, "b2c3d4e" + "2" * 33, "c3d4e5f" + "3" * 33


def uptodate():
    """The module under test; a missing module fails only the test that asked."""
    try:
        from dokima import uptodate as mod
    except ImportError as e:
        pytest.fail(f"523: dokima/uptodate.py is missing ({e})")
    return mod


def run(name, conclusion):
    """One completed check run on a commit, as GitHub lists it."""
    return {"name": name, "status": "completed", "conclusion": conclusion}


class GitHub:
    """GitHub's REST API for one repo, keeping comments, check runs and updates.

    heads maps an issue number to its PR's head sha; checks maps a sha to the check runs on it."""

    def __init__(self, heads, checks):
        self.heads, self.checks, self.calls, self.comments, self.next_id = dict(heads), dict(checks), [], {}, 1000

    def pr(self, issue):
        """Issue `issue`'s open PR, number 10 * issue, as GitHub lists it."""
        return {"number": 10 * issue, "draft": False, "state": "open", "base": {"ref": "main"},
                "head": {"sha": self.heads[issue], "ref": f"try/issue-{issue}", "label": f"o:try/issue-{issue}",
                         "repo": {"full_name": REPO}}}

    def __call__(self, method, path, **fields):
        method, bare = method.upper(), path.split("?")[0].lstrip("/")
        query = {k: v[0] for k, v in parse_qs(path.partition("?")[2]).items()}
        query.update({k: str(v) for k, v in fields.items()})
        self.calls.append((method, bare, fields))
        first = query.get("page", "1") == "1"
        if method == "GET" and bare == f"repos/{REPO}/pulls":
            return [self.pr(i) for i in self.heads] if first else []
        if method == "GET" and bare.startswith(f"repos/{REPO}/compare/"):
            return {"behind_by": 1, "ahead_by": 1, "status": "diverged"}
        m = re.fullmatch(rf"repos/{REPO}/commits/([^/]+)/check-runs", bare)
        if method == "GET" and m:
            runs = [r for r in self.checks.get(m[1], []) if unquote(query.get("check_name", r["name"])) == r["name"]]
            return {"total_count": len(runs), "check_runs": [dict(r) for r in runs] if first else []}
        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[^/]+/pulls", bare):
            return []
        m = re.fullmatch(rf"repos/{REPO}/pulls/(\d+)/update-branch", bare)
        if method == "PUT" and m:
            return {"message": "Updating pull request branch."}
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)/comments", bare)
        if method == "GET" and m:
            return [dict(c) for c in self.comments.get(int(m[1]), [])] if first else []
        if method == "POST" and m:
            self.next_id += 1
            c = {"id": self.next_id, "user": {"login": BOT, "type": "Bot"}, "body": fields.get("body", ""),
                 "created_at": f"2026-10-12T10:{self.next_id % 60:02d}:00Z"}
            self.comments.setdefault(int(m[1]), []).append(c)
            return dict(c)
        m = re.fullmatch(rf"repos/{REPO}/issues/comments/(\d+)", bare)
        if method in ("PATCH", "DELETE") and m:
            for items in self.comments.values():
                for c in items:
                    if c["id"] == int(m[1]):
                        if method == "DELETE":
                            items.remove(c)
                            return {}
                        c["body"] = fields.get("body", c["body"])
                        return dict(c)
            raise AssertionError(f"523: a call named comment {m[1]}, which does not exist")
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)", bare)
        if method == "GET" and m:
            return {"number": int(m[1]), "state": "open", "labels": []}
        raise AssertionError(f"523: unexpected GitHub call {method} {path} {fields}")

    def merge(self, sha):
        """One merge to main, run as uptodate.yml runs it."""
        uptodate().run(REPO, "main", sha, rest=self)

    def updates(self):
        """[(PR number, expected head sha)] of every Update branch call, in order."""
        return [(int(re.search(r"pulls/(\d+)/update-branch", p)[1]), f.get("expected_head_sha"))
                for m, p, f in self.calls if m == "PUT" and p.endswith("/update-branch")]

    def posted(self, n):
        """The bodies of the comments the bot posted on issue or PR n, in order."""
        return [f.get("body", "") for m, p, f in self.calls if m == "POST" and p == f"repos/{REPO}/issues/{n}/comments"]


# 523.1: after a merge, a PR whose all tests check failed on its head is not brought up to date

def test_a_pr_whose_all_tests_failed_on_its_head_is_not_brought_up_to_date(record_property):
    """A pull request whose all tests failed on its head is not updated.

    Proves 523.1. Fakes two Dokima pull requests behind main: #70, whose all tests check failed on its head, and #80, whose all
    tests check passed. One merge runs; #80 must be updated as before and #70 must get no Update branch call."""
    record_property("proves", "523.1")
    gh = GitHub({7: "aa" * 20, 8: "bb" * 20},
                {"aa" * 20: [run("all tests", "failure")], "bb" * 20: [run("all tests", "success")]})
    gh.merge(M1)
    updated = [n for n, _ in gh.updates()]
    assert 80 in updated, f"523.1: #80, whose all tests passed, was not brought up to date; updates {gh.updates()}"
    assert 70 not in updated, \
        f"523.1: #70's all tests check failed on its head, yet it was brought up to date; updates {gh.updates()}"


# 523.2: the skipped PR says so once on its issue, however many merges skip it

def test_a_skipped_pr_says_so_once_on_its_issue_over_three_merges(record_property):
    """A pull request skipped for failing tests says so once on its issue.

    Proves 523.2. Fakes Dokima pull request #70 for issue #7, its all tests check failed on its head, beside #80 for issue #8, whose
    tests passed. Three merges run with #70's head unchanged; issue #7 must get exactly one comment, naming #70 and
    saying it is not brought up to date, and issue #8 none."""
    record_property("proves", "523.2")
    gh = GitHub({7: "aa" * 20, 8: "bb" * 20},
                {"aa" * 20: [run("all tests", "failure")], "bb" * 20: [run("all tests", "success")]})
    for sha in (M1, M2, M3):
        gh.merge(sha)
    said = gh.posted(7)
    assert len(said) == 1, f"523.2: issue #7 got {len(said)} comments over three merges, expected exactly one: {said}"
    assert "#70" in said[0], f"523.2: the comment on issue #7 does not name its pull request #70: {said[0]!r}"
    assert "up to date" in said[0].lower(), \
        f"523.2: the comment on issue #7 does not say #70 is not brought up to date: {said[0]!r}"
    assert not gh.posted(8), f"523.2: issue #8, whose tests passed, got a comment: {gh.posted(8)}"


# 523.3: once all tests pass on a new head, the PR is brought up to date as before

def test_once_all_tests_pass_on_a_new_head_the_pr_is_brought_up_to_date_again(record_property):
    """Once all tests pass on a new head, the pull request is updated again.

    Proves 523.3. Fakes Dokima pull request #70 whose all tests check failed on head A, so one merge skips it. Its head then moves to
    B, where all tests passed, and a second merge runs; #70 must get exactly one Update branch call, for head B."""
    record_property("proves", "523.3")
    a, b = "aa" * 20, "cc" * 20
    gh = GitHub({7: a}, {a: [run("all tests", "failure")], b: [run("all tests", "success")]})
    gh.merge(M1)
    gh.heads[7] = b
    gh.merge(M2)
    assert gh.updates() == [(70, b)], \
        f"523.3: after all tests passed on new head {b[:7]}, #70 was not brought up to date once on it; updates {gh.updates()}"

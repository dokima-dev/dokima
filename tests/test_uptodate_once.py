"""A PR that cannot be updated with main carries one comment, edited in place (#408).

After every merge to main, `dokima.uptodate.run(repo, base, sha, rest=...)` tries GitHub's Update branch on every open
PR behind main. Before #408, every refusal posted a new "could not be updated" comment, so PR #287 got 23 identical
ones in a day. These tests fake GitHub through the same `rest(method, path, **fields)` seam as tests/test_uptodate.py,
but keep each PR's comments as GitHub would, so several merges in a row can be run against one PR and the comments it
ends up carrying can be counted. One test runs the real module from outside against a fake `gh` on PATH.

The fake GitHub answers:
  - GET .../pulls: the open PRs; GET .../compare/BASE...HEAD: behind by one commit;
  - PUT .../pulls/N/update-branch: 202, or 422 with GitHub's refusal for that PR (set per run in `refuse`);
  - GET .../issues/N/comments (paged with page=): the PR's comments as REST returns them, oldest first;
  - POST .../issues/N/comments, PATCH .../issues/comments/ID, DELETE .../issues/comments/ID;
  - GET .../commits/SHA/check-runs: no check runs yet (#523 skips a PR whose all tests check failed).
"""
import json
import os
import re
import stat
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dokima import agent  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = "o/r"
BOT = f"{agent.BOT}[bot]"
M1, M2, M3 = "a1b2c3d" + "1" * 33, "b2c3d4e" + "2" * 33, "c3d4e5f" + "3" * 33
CONFLICT = "merge conflict between base and head"
WORKFLOW_REFUSED = "refusing to allow a GitHub App to create or update workflow `.github/workflows/ci.yml` without `workflows` permission"
OTHER = "Head branch was modified. Review and try the merge again."
REFUSED = "could not be updated"


def uptodate():
    """The module under test; a missing module fails only the test that asked."""
    try:
        from dokima import uptodate as mod
    except ImportError as e:
        pytest.fail(f"408: dokima/uptodate.py is missing ({e})")
    return mod


def pr(n):
    """One open PR into main, as GitHub lists it."""
    return {"number": n, "draft": False, "state": "open", "base": {"ref": "main"},
            "head": {"sha": f"{n:02d}" * 20, "ref": f"work/issue-{n}-x", "label": f"o:work/issue-{n}-x",
                     "repo": {"full_name": "someone/fork"}}}


def legacy(sha, why):
    """A refusal comment in the words uptodate.py posted before #408, as on PR #287."""
    return f"This pull request could not be updated with `main` ({sha[:7]}). GitHub said: {why}"


class GitHub:
    """GitHub's REST API for one repo, keeping every PR's comments.

    refuse maps a PR number to GitHub's refusal message for the current merge."""

    def __init__(self, prs, comments=None):
        self.prs, self.refuse, self.calls, self.next_id = [pr(n) for n in prs], {}, [], 1000
        self.comments = {n: [] for n in prs}
        for n, items in (comments or {}).items():
            for login, body in items:
                self.add(n, login, body)

    def add(self, n, login, body):
        """Adds one comment to PR n and returns it."""
        self.next_id += 1
        c = {"id": self.next_id, "user": {"login": login, "type": "Bot" if login.endswith("[bot]") else "User"},
             "body": body, "created_at": f"2026-10-10T10:{self.next_id % 60:02d}:00Z"}
        self.comments.setdefault(n, []).append(c)
        return c

    def find(self, cid):
        """The PR number and comment with this id."""
        for n, items in self.comments.items():
            for c in items:
                if c["id"] == int(cid):
                    return n, c
        raise AssertionError(f"408: a call named comment {cid}, which this PR does not have")

    def __call__(self, method, path, **fields):
        method, bare = method.upper(), path.split("?")[0].lstrip("/")
        self.calls.append((method, bare, fields))
        if method == "GET" and bare == f"repos/{REPO}/pulls":
            page = str(fields.get("page") or (re.search(r"[?&]page=(\d+)", path) or [None, "1"])[1])
            return [dict(p) for p in self.prs] if page == "1" else []
        if method == "GET" and bare.startswith(f"repos/{REPO}/compare/"):
            return {"behind_by": 1, "ahead_by": 1, "status": "diverged"}
        m = re.fullmatch(rf"repos/{REPO}/pulls/(\d+)/update-branch", bare)
        if method == "PUT" and m:
            if int(m[1]) in self.refuse:
                msg = self.refuse[int(m[1])]
                raise subprocess.CalledProcessError(1, ["gh", "api"], output=json.dumps({"message": msg}),
                                                    stderr=f"gh: {msg} (HTTP 422)\n")
            return {"message": "Updating pull request branch."}
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)/comments", bare)
        if method == "GET" and m:
            page = str(fields.get("page") or (re.search(r"[?&]page=(\d+)", path) or [None, "1"])[1])
            return [dict(c) for c in self.comments.get(int(m[1]), [])] if page == "1" else []
        if method == "POST" and m:
            return dict(self.add(int(m[1]), BOT, fields.get("body", "")))
        m = re.fullmatch(rf"repos/{REPO}/issues/comments/(\d+)", bare)
        if method == "PATCH" and m:
            n, c = self.find(m[1])
            c["body"] = fields.get("body", c["body"])
            return dict(c)
        if method == "DELETE" and m:
            n, c = self.find(m[1])
            self.comments[n].remove(c)
            return {}
        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[^/]+/check-runs", bare):
            return {"total_count": 0, "check_runs": []}
        raise AssertionError(f"408: unexpected GitHub call {method} {path} {fields}")

    def merge(self, sha, refuse):
        """One merge to main: GitHub refuses the PRs in `refuse` and updates the rest."""
        self.refuse = dict(refuse)
        uptodate().run(REPO, "main", sha, rest=self)

    def bot(self, n):
        """The bot's comments on PR n, oldest first."""
        return [c for c in self.comments.get(n, []) if c["user"]["login"] == BOT]

    def posts(self, n):
        """How many comments were posted on PR n."""
        return sum(1 for m, p, f in self.calls if m == "POST" and p == f"repos/{REPO}/issues/{n}/comments")

    def touched(self, cid):
        """The PATCH or DELETE calls made on comment cid."""
        return [(m, f) for m, p, f in self.calls if m in ("PATCH", "DELETE") and p == f"repos/{REPO}/issues/comments/{cid}"]


# 408.1: refused on several merges in a row, a PR carries one refusal comment showing the newest main commit

def test_a_pr_refused_on_three_merges_carries_one_comment_with_the_newest_commit(record_property):
    """A PR refused three merges in a row carries one comment showing the newest commit.

    Proves 408.1.
    Two PRs are refused by GitHub on three merges to main in a row, each time with a different reason. Each PR must end
    with exactly one comment from the bot, posted once on the first refusal and edited in place after; it must say
    the PR could not be updated, name the third merge's commit and GitHub's third reason, and no longer name the
    first two commits."""
    record_property("proves", "408.1")
    gh = GitHub([81, 82])
    for sha, why in ((M1, CONFLICT), (M2, WORKFLOW_REFUSED), (M3, OTHER)):
        gh.merge(sha, {81: why, 82: why})
    for n in (81, 82):
        said = gh.bot(n)
        assert gh.posts(n) == 1, f"408.1: PR {n} got {gh.posts(n)} comments posted over three refusals, expected one"
        assert len(said) == 1, f"408.1: PR {n} carries {len(said)} bot comments, expected one: {[c['body'] for c in said]}"
        body = said[0]["body"]
        assert REFUSED in body, f"408.1: PR {n}'s comment no longer says it could not be updated: {body!r}"
        assert M3[:7] in body, f"408.1: PR {n}'s comment does not show the newest main commit {M3[:7]}: {body!r}"
        assert OTHER in body, f"408.1: PR {n}'s comment does not carry GitHub's newest reason {OTHER!r}: {body!r}"
        for old in (M1, M2):
            assert old[:7] not in body, f"408.1: PR {n}'s comment still names the older commit {old[:7]}: {body!r}"


# 408.2: a PR that already carries several refusal comments from before keeps only one

def test_older_refusal_comments_are_folded_into_the_newest(record_property):
    """A PR already carrying several refusal comments keeps only the newest, edited.

    Proves 408.2, the case of PR #287.
    The PR starts with a person's comment, the bot's clash note and three refusal comments in the old wording. GitHub
    refuses it again: no new comment may be posted, the newest old refusal comment must be edited to the newest
    commit and reason, the two older ones deleted, and the person's comment and the clash note left as they were."""
    record_property("proves", "408.2")
    clash_note = "This pull request clashes with `main` since 0a0a0a0 (#300) merged, in:\n\n- `app.py`\n"
    gh = GitHub([83], comments={83: [("alice", "Looks close, thanks."), (BOT, legacy(M1, CONFLICT)), (BOT, clash_note),
                                     (BOT, legacy(M1, CONFLICT)), (BOT, legacy(M2, CONFLICT))]})
    alice, first, note, second, newest = [c["id"] for c in gh.comments[83]]
    gh.merge(M3, {83: OTHER})
    assert gh.posts(83) == 0, f"408.2: a new comment was posted on a PR that already had refusal comments"
    refusals = [c for c in gh.bot(83) if REFUSED in c["body"]]
    assert [c["id"] for c in refusals] == [newest], \
        f"408.2: expected only the newest refusal comment {newest} left, got {[(c['id'], c['body']) for c in refusals]}"
    assert M3[:7] in refusals[0]["body"] and OTHER in refusals[0]["body"], \
        f"408.2: the kept comment does not show the newest commit {M3[:7]} and reason: {refusals[0]['body']!r}"
    left = {c["id"]: c["body"] for c in gh.comments[83]}
    assert first not in left and second not in left, "408.2: the older refusal comments were not deleted"
    assert left.get(alice) == "Looks close, thanks." and not gh.touched(alice), "408.2: the person's comment was changed"
    assert left.get(note) == clash_note and not gh.touched(note), "408.2: the bot's clash note was changed"


# 408.3: a PR that updates cleanly after a refusal gets no new comment; its refusal comment says it is up to date

def test_a_clean_update_after_a_refusal_edits_the_comment_and_posts_none(record_property):
    """A PR updated cleanly after a refusal gets no new comment, only an edit.

    Proves 408.3.
    PR 84 is refused on one merge and updates cleanly on the next. Exactly one comment may ever be posted on it, and
    that same comment must now say the PR is up to date with main at the newest commit, no longer that it could not
    be updated. PR 85, never refused, updates cleanly on both merges and gets no comment and no edit at all."""
    record_property("proves", "408.3")
    gh = GitHub([84, 85])
    gh.merge(M1, {84: CONFLICT})
    assert len(gh.bot(84)) == 1, f"408.3: the refusal posted {len(gh.bot(84))} comments, expected one"
    cid = gh.bot(84)[0]["id"]
    gh.merge(M2, {})
    said = gh.bot(84)
    assert gh.posts(84) == 1, f"408.3: the clean update posted a new comment on PR 84 ({gh.posts(84)} posted in all)"
    assert [c["id"] for c in said] == [cid], f"408.3: PR 84's refusal comment was not kept and edited in place: {said}"
    body = said[0]["body"]
    assert REFUSED not in body, f"408.3: after a clean update the comment still says it could not be updated: {body!r}"
    assert "up to date" in body.lower(), f"408.3: after a clean update the comment does not say it is up to date: {body!r}"
    assert M2[:7] in body, f"408.3: the comment does not name the commit it was updated with, {M2[:7]}: {body!r}"
    assert gh.posts(85) == 0 and gh.comments[85] == [], f"408.3: PR 85, never refused, got a comment: {gh.comments[85]}"
    assert not [c for c in gh.calls if c[0] in ("PATCH", "DELETE") and str(c[1]).endswith("/85")], \
        "408.3: PR 85, never refused, had a comment edited or deleted"


# 408.4: refused again after a clean update, the PR still carries one comment

def test_a_pr_refused_again_after_a_clean_update_still_carries_one_comment(record_property):
    """A PR refused again after a clean update still carries one comment.

    Proves 408.4.
    PR 86 is refused on the first merge, updates cleanly on the second and is refused on the third. It must carry
    exactly one bot comment, posted once, that says it could not be updated and shows the third commit and reason."""
    record_property("proves", "408.4")
    gh = GitHub([86])
    gh.merge(M1, {86: CONFLICT})
    gh.merge(M2, {})
    gh.merge(M3, {86: WORKFLOW_REFUSED})
    said = gh.bot(86)
    assert gh.posts(86) == 1 and len(said) == 1, \
        f"408.4: expected one comment posted and carried, got {gh.posts(86)} posted: {[c['body'] for c in said]}"
    body = said[0]["body"]
    assert REFUSED in body and M3[:7] in body and WORKFLOW_REFUSED in body, \
        f"408.4: the comment does not show the newest refusal at {M3[:7]}: {body!r}"
    assert "up to date" not in body.lower(), f"408.4: the comment still says the PR is up to date: {body!r}"


# 408.5: only the bot's own refusal comment is ever edited or deleted

def test_a_persons_comment_in_the_same_words_is_never_edited(record_property):
    """A person's comment worded like a refusal is never edited or deleted.

    Proves 408.5.
    PR 87 starts with a comment by a person that copies the refusal's words. GitHub refuses the PR on two merges, then
    updates it cleanly. The person's comment must never be edited or deleted; the bot must post exactly one comment
    of its own and edit only that one, which ends up saying the PR is up to date."""
    record_property("proves", "408.5")
    fake = legacy(M1, CONFLICT)
    gh = GitHub([87], comments={87: [("mallory", fake)]})
    theirs = gh.comments[87][0]["id"]
    gh.merge(M1, {87: CONFLICT})
    gh.merge(M2, {87: CONFLICT})
    gh.merge(M3, {})
    assert not gh.touched(theirs), f"408.5: the person's comment was edited or deleted: {gh.touched(theirs)}"
    assert [c["body"] for c in gh.comments[87] if c["id"] == theirs] == [fake], "408.5: the person's comment changed"
    said = gh.bot(87)
    assert gh.posts(87) == 1 and len(said) == 1, \
        f"408.5: expected the bot to post and keep one comment of its own, got {gh.posts(87)} posted: {said}"
    assert "up to date" in said[0]["body"].lower() and REFUSED not in said[0]["body"], \
        f"408.5: the bot's own comment was not the one edited after the clean update: {said[0]['body']!r}"


# 408.6: when GitHub cannot list or change a PR's comments, the others still go on and the run fails naming that PR

FAKE_GH = r'''#!PYTHON
"""A stand-in for `gh api`: answers from gh.json and logs every call as [method, path, fields]."""
import json, os, re, sys
d = json.load(open(os.environ["FAKE_GH_JSON"]))
args, method, fields, path = sys.argv[1:], None, {}, None
assert args and args[0] == "api", args
i = 1
while i < len(args):
    a = args[i]
    if a in ("-X", "--method"):
        method = args[i + 1].upper(); i += 2
    elif a in ("-f", "-F", "--field", "--raw-field"):
        k, _, v = args[i + 1].partition("="); fields[k] = v; i += 2
    elif a == "--input":
        src = sys.stdin if args[i + 1] == "-" else open(args[i + 1]); fields.update(json.load(src)); i += 2
    elif a.startswith("-"):
        i += 2 if a in ("-H", "--header", "-q", "--jq") else 1
    else:
        path = path or a; i += 1
method = method or ("POST" if fields else "GET")
open(os.environ["FAKE_GH_LOG"], "a").write(json.dumps([method, path, fields]) + "\n")
bare, repo = path.split("?")[0].lstrip("/"), d["repo"]
def out(x):
    print(json.dumps(x)); sys.exit(0)
def fail(msg, code):
    print(json.dumps({"message": msg})); sys.stderr.write(f"gh: {msg} (HTTP {code})\n"); sys.exit(1)
if method == "GET" and bare == f"repos/{repo}/pulls":
    out(d["prs"] if "page=2" not in path and fields.get("page") not in ("2", 2) else [])
if method == "GET" and bare.startswith(f"repos/{repo}/compare/"):
    out({"behind_by": 1, "ahead_by": 1, "status": "diverged"})
m = re.fullmatch(f"repos/{repo}/pulls/(\\d+)/update-branch", bare)
if method == "PUT" and m:
    if m[1] in d["refuse"]:
        fail(d["refuse"][m[1]], 422)
    out({"message": "Updating pull request branch."})
m = re.fullmatch(f"repos/{repo}/issues/(\\d+)/comments", bare)
if m and m[1] in d["broken"]:
    fail("Server Error", 502)
if method == "GET" and m:
    out(d["comments"].get(m[1], []) if "page=2" not in path and fields.get("page") not in ("2", 2) else [])
if method == "POST" and m:
    out({"id": 1, "body": fields.get("body", "")})
m = re.fullmatch(f"repos/{repo}/issues/comments/(\\d+)", bare)
if m and method in ("PATCH", "DELETE"):
    if m[1] in d["broken_edit"]:
        fail("Server Error", 502)
    out({"id": int(m[1]), "body": fields.get("body", "")} if method == "PATCH" else {})
sys.stderr.write("gh: Not Found (HTTP 404)\n"); sys.exit(1)
'''


def run_module(tmp_path, broken, broken_edit=()):
    """Runs the real module with a fake gh: PR 91 refused, PR 92 updated.

    PR 91 already carries one refusal comment of the bot's, id 501. The comments of every PR in `broken` answer 502
    when listed or posted; editing or deleting a comment whose id is in `broken_edit` answers 502."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    mine = {"id": 501, "user": {"login": BOT, "type": "Bot"}, "body": legacy(M1, WORKFLOW_REFUSED),
            "created_at": "2026-10-10T09:00:00Z"}
    data = {"repo": REPO, "prs": [pr(91), pr(92)], "refuse": {"91": WORKFLOW_REFUSED}, "broken": list(broken),
            "comments": {"91": [mine]}, "broken_edit": [str(c) for c in broken_edit]}
    (tmp_path / "gh.json").write_text(json.dumps(data))
    fake = tmp_path / "bin" / "gh"
    fake.parent.mkdir()
    fake.write_text(FAKE_GH.replace("#!PYTHON", f"#!{sys.executable}"))
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.jsonl"
    env = dict(os.environ, PATH=f"{fake.parent}{os.pathsep}{os.environ['PATH']}", GITHUB_REPOSITORY=REPO,
               GITHUB_SHA=M2, GITHUB_REF_NAME="main", GITHUB_REF="refs/heads/main", GH_TOKEN="fake-token",
               PYTHONPATH=ROOT, FAKE_GH_JSON=str(tmp_path / "gh.json"), FAKE_GH_LOG=str(log))
    env.pop("PYTHONSAFEPATH", None)
    done = subprocess.run([sys.executable, "-m", "dokima.uptodate"], cwd=ROOT, env=env, capture_output=True,
                          text=True, timeout=30)
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return done, calls


def errors_naming(done, n):
    """The run's `::error::` lines that name PR n."""
    return [line for line in (done.stdout + done.stderr).splitlines()
            if line.startswith("::error::") and re.search(rf"#{n}\b", line)]


def check_broken_run(done, calls, what):
    """PR 92 still updates, and the run fails with an error naming #91."""
    said = f"gh calls {calls}\noutput {done.stdout}{done.stderr}"
    puts = [p for m, p, f in calls if m == "PUT" and "update-branch" in (p or "")]
    assert any((p or "").rstrip("/").endswith("pulls/92/update-branch") for p in puts), \
        f"408.6: PR 92 was not updated after PR 91's comments could not be {what}\n{said}"
    assert done.returncode != 0, f"408.6: the run succeeded although PR 91's comments could not be {what}\n{said}"
    assert errors_naming(done, 91), f"408.6: no ::error:: line names #91 after its comments could not be {what}\n{said}"


def test_a_pr_whose_comments_github_cannot_list_fails_the_run_by_name(record_property, tmp_path):
    """When a PR's comments cannot be read, the others update and the run names it.

    Proves 408.6.
    Runs the real module as the workflow does, with a fake `gh`: GitHub refuses PR 91 and then answers 502 for its
    comments, while PR 92, after it, updates. PR 92 must still get its Update branch, and the run must exit non-zero
    with an `::error::` line naming #91 (the `::warning::` line every refused PR already gets does not count). The
    same run with PR 91's comments readable must exit 0 with no error line."""
    record_property("proves", "408.6")
    done, calls = run_module(tmp_path / "broken", ["91"])
    check_broken_run(done, calls, "listed")
    done, calls = run_module(tmp_path / "fine", [])
    said = f"gh calls {calls}\noutput {done.stdout}{done.stderr}"
    assert done.returncode == 0 and not errors_naming(done, 91), \
        f"408.6: with every comment readable the run failed or named #91 in an error\n{said}"


def test_a_pr_whose_refusal_comment_github_cannot_edit_fails_the_run_by_name(record_property, tmp_path):
    """When a refusal comment cannot be edited, the others update and the run names it.

    Proves 408.6.
    Runs the real module with a fake `gh`: PR 91 already carries the bot's refusal comment, GitHub refuses PR 91
    again and answers 502 to every edit or delete of that comment, while PR 92, after it, updates. The module must
    try to change that comment, PR 92 must still get its Update branch, and the run must exit non-zero with an
    `::error::` line naming #91."""
    record_property("proves", "408.6")
    done, calls = run_module(tmp_path / "edit", [], broken_edit=[501])
    tried = [(m, p) for m, p, f in calls if m in ("PATCH", "DELETE") and (p or "").rstrip("/").endswith("issues/comments/501")]
    assert tried, f"408.6: the bot's refusal comment on PR 91 was never edited, so its failure was never met\ngh calls {calls}"
    check_broken_run(done, calls, "changed")

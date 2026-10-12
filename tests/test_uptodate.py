"""Open PRs are brought up to date after every merge to main (#189).

After a merge to main, `.github/workflows/uptodate.yml` runs `python3 -m dokima.uptodate`, which calls GitHub's own
Update branch for every open PR whose branch fell behind main. The rules live in `dokima.uptodate.run(repo, base, sha,
rest=...)`, where `rest(method, path, **fields)` is one GitHub REST call shaped like `dokima.board.api`: it returns the
parsed JSON and raises `subprocess.CalledProcessError` (GitHub's answer as JSON on `output`, gh's one-line message on
`stderr`) when GitHub refuses. These tests fake GitHub through that seam, one test runs the real module from outside
against a fake `gh` on PATH, and the workflow is read as text.

The fake GitHub answers:
  - GET .../pulls (any query or fields; an empty page past the first): the open PRs, drafts included;
  - GET .../compare/BASE...HEAD, where HEAD is a PR's head sha, its ref or its "owner:ref" label: behind_by, ahead_by;
  - PUT .../pulls/N/update-branch (expected_head_sha): 202, or GitHub's refusal for that PR, 422 with its message;
  - GET .../issues/N/comments: no comments yet (#408 looks for its earlier refusal comment);
  - POST .../issues/N/comments (body): a comment on PR N;
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

ROOT = os.path.join(os.path.dirname(__file__), "..")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "uptodate.yml")
REPO = "o/r"
MERGE = "f00d" * 10
CONFLICT = "merge conflict between base and head"
WORKFLOW_REFUSED = "refusing to allow a GitHub App to create or update workflow `.github/workflows/ci.yml` without `workflows` permission"


def uptodate():
    """The module under test; a missing module fails the test that asked for it, not the whole file."""
    try:
        from dokima import uptodate as mod
    except ImportError as e:
        pytest.fail(f"189: dokima/uptodate.py is missing ({e})")
    return mod


def pr(n, behind, ahead=1, draft=False):
    """One open PR as GitHub lists it, with how far its branch is behind and ahead of main."""
    return {"number": n, "draft": draft, "state": "open", "base": {"ref": "main"},
            "head": {"sha": f"{n:02d}" * 20, "ref": f"work/issue-{n}-x", "label": f"o:work/issue-{n}-x"},
            "_behind": behind, "_ahead": ahead}


class FakeGitHub:
    """GitHub's REST API for one repo, recording every call; refuse maps a PR number to GitHub's refusal message."""

    def __init__(self, prs, refuse=None, moved=None):
        self.prs, self.refuse, self.moved = prs, refuse or {}, moved or {}
        self.calls = []

    def __call__(self, method, path, **fields):
        self.calls.append((method.upper(), path, fields))
        method, bare = method.upper(), path.split("?")[0].lstrip("/")
        if method == "GET" and re.fullmatch(rf"repos/{REPO}/pulls", bare):
            page = str(fields.get("page") or (re.search(r"[?&]page=(\d+)", path) or [None, "1"])[1])
            listed = [{k: v for k, v in p.items() if not k.startswith("_")} for p in self.prs]
            return listed if page == "1" else []
        m = re.fullmatch(rf"repos/{REPO}/compare/([^.]+)\.\.\.(.+)", bare)
        if method == "GET" and m:
            for p in self.prs:
                if m[2] in (p["head"]["sha"], p["head"]["ref"], p["head"]["label"]):
                    return {"behind_by": p["_behind"], "ahead_by": p["_ahead"],
                            "status": "behind" if p["_behind"] and not p["_ahead"] else "diverged" if p["_behind"] else "ahead"}
            raise AssertionError(f"189: compare asked for an unknown head {m[2]!r}")
        m = re.fullmatch(rf"repos/{REPO}/pulls/(\d+)/update-branch", bare)
        if method == "PUT" and m:
            n = int(m[1])
            head = self.moved.get(n) or next(p["head"]["sha"] for p in self.prs if p["number"] == n)
            if "expected_head_sha" in fields and fields["expected_head_sha"] != head:
                self.fail("expected head sha didn't match current head ref.")
            if n in self.refuse:
                self.fail(self.refuse[n])
            return {"message": "Updating pull request branch.", "url": f"https://github.com/{REPO}/pull/{n}"}
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)/comments", bare)
        if method == "GET" and m:
            return []
        if method == "POST" and m:
            return {"id": len(self.calls), "body": fields.get("body", "")}
        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[^/]+/check-runs", bare):
            return {"total_count": 0, "check_runs": []}
        raise AssertionError(f"189: unexpected GitHub call {method} {path} {fields}")

    @staticmethod
    def fail(message):
        out = json.dumps({"message": message, "documentation_url": "https://docs.github.com/rest"})
        raise subprocess.CalledProcessError(1, ["gh", "api"], output=out, stderr=f"gh: {message} (HTTP 422)\n")

    def updated(self):
        """The PR numbers Update branch was called for, in order."""
        return [int(re.search(r"pulls/(\d+)/update-branch", p)[1]) for m, p, f in self.calls if m == "PUT" and "update-branch" in p]

    def puts(self):
        return [(int(re.search(r"pulls/(\d+)/update-branch", p)[1]), f) for m, p, f in self.calls if m == "PUT" and "update-branch" in p]

    def comments(self):
        """{PR number: [comment bodies]} for every comment posted."""
        out = {}
        for m, p, f in self.calls:
            hit = re.search(r"issues/(\d+)/comments", p)
            if m == "POST" and hit:
                out.setdefault(int(hit[1]), []).append(f.get("body", ""))
        return out


# 189.1: every open PR behind main, drafts included, gets GitHub's Update branch

def test_every_open_pr_behind_main_is_updated_drafts_included(record_property):
    """After a merge to main, every open PR that fell behind, a draft too, is updated with GitHub's Update branch.

    Fakes GitHub with three open PRs behind main (one of them a draft, one behind by many commits) and runs the
    update; each of the three must get exactly one Update branch call and no comment."""
    record_property("proves", "189.1")
    gh = FakeGitHub([pr(11, behind=1), pr(12, behind=3, draft=True), pr(13, behind=40, ahead=0)])
    uptodate().run(REPO, "main", MERGE, rest=gh)
    assert sorted(gh.updated()) == [11, 12, 13], f"189.1: expected PRs 11, 12 (draft) and 13 updated, got {gh.updated()}"
    assert gh.comments() == {}, f"189.1: a successful update posted a comment: {gh.comments()}"


def test_the_workflow_runs_the_update_on_every_push_to_main(record_property):
    """A workflow starts the update every time main changes, and only then.

    Reads .github/workflows/uptodate.yml: it must trigger on a push to main, on no pull request event, and run
    `python3 -m dokima.uptodate`."""
    record_property("proves", "189.1")
    assert os.path.exists(WORKFLOW), "189.1: .github/workflows/uptodate.yml is missing"
    text = open(WORKFLOW).read()
    on = re.split(r"(?m)^[a-z]", text.split("\non:\n", 1)[1], 1)[0] if "\non:\n" in text else ""
    assert re.search(r"(?m)^  push:\s*\n\s+branches:\s*\[\s*main\s*\]", on), "189.1: the workflow does not run on a push to main"
    assert "pull_request" not in on, "189.1: the workflow also runs on pull request events"
    assert "python3 -m dokima.uptodate" in text, "189.1: the workflow never runs python3 -m dokima.uptodate"


def test_the_real_module_updates_behind_prs_through_gh(record_property, tmp_path):
    """Run from outside the way the workflow runs it, the update calls GitHub's Update branch for a PR behind main.

    Runs `python3 -m dokima.uptodate` with GITHUB_REPOSITORY, GITHUB_SHA and GITHUB_REF_NAME set and a fake `gh` first
    on PATH that answers `gh api` (-X/--method, -f/-F/--field/--raw-field, --paginate) for one PR behind and one up
    to date; the behind one must get PUT .../pulls/21/update-branch, the other none."""
    record_property("proves", "189.1")
    assert os.path.exists(os.path.join(ROOT, "dokima", "uptodate.py")), "189.1: dokima/uptodate.py is missing"
    log = tmp_path / "calls.jsonl"
    data = {"prs": [pr(21, behind=2), pr(22, behind=0)], "repo": REPO}
    (tmp_path / "gh.json").write_text(json.dumps(data))
    fake = tmp_path / "bin" / "gh"
    fake.parent.mkdir()
    fake.write_text(f"""#!{sys.executable}
import json, re, sys
d = json.load(open({str(tmp_path / 'gh.json')!r}))
args, method, fields, path = sys.argv[1:], None, {{}}, None
assert args and args[0] == "api", args
i = 1
while i < len(args):
    a = args[i]
    if a in ("-X", "--method"):
        method = args[i + 1].upper(); i += 2
    elif a in ("-f", "-F", "--field", "--raw-field"):
        k, _, v = args[i + 1].partition("="); fields[k] = v; i += 2
    elif a.startswith("-"):
        i += 2 if a in ("-H", "--header", "-q", "--jq", "--input") else 1
    else:
        path = path or a; i += 1
method = method or ("POST" if fields else "GET")
open({str(log)!r}, "a").write(json.dumps([method, path, fields]) + "\\n")
bare = path.split("?")[0].lstrip("/")
prs = d["prs"]
if method == "GET" and bare == "repos/" + d["repo"] + "/pulls":
    print(json.dumps([{{k: v for k, v in p.items() if not k.startswith("_")}} for p in prs])); sys.exit(0)
m = re.fullmatch("repos/" + d["repo"] + r"/compare/([^.]+)\\.\\.\\.(.+)", bare)
if method == "GET" and m:
    for p in prs:
        if m[2] in (p["head"]["sha"], p["head"]["ref"], p["head"]["label"]):
            print(json.dumps({{"behind_by": p["_behind"], "ahead_by": p["_ahead"]}})); sys.exit(0)
if method == "PUT" and re.fullmatch("repos/" + d["repo"] + r"/pulls/\\d+/update-branch", bare):
    print(json.dumps({{"message": "Updating pull request branch."}})); sys.exit(0)
if method == "GET" and bare.endswith("/comments"):
    print(json.dumps([])); sys.exit(0)
if method == "POST" and bare.endswith("/comments"):
    print(json.dumps({{"id": 1}})); sys.exit(0)
sys.stderr.write("gh: Not Found (HTTP 404)\\n"); sys.exit(1)
""")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=f"{fake.parent}{os.pathsep}{os.environ['PATH']}", GITHUB_REPOSITORY=REPO,
               GITHUB_SHA=MERGE, GITHUB_REF_NAME="main", GITHUB_REF="refs/heads/main", GH_TOKEN="fake-token",
               PYTHONPATH=os.path.abspath(ROOT))
    env.pop("PYTHONSAFEPATH", None)
    done = subprocess.run([sys.executable, "-m", "dokima.uptodate"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    puts = [p for m, p, f in calls if m == "PUT" and "update-branch" in (p or "")]
    assert any(p.rstrip("/").endswith(f"repos/{REPO}/pulls/21/update-branch") for p in puts), \
        f"189.1: PR 21 (behind main) was not updated; gh calls {calls}; output {done.stdout}{done.stderr}"
    assert not any("pulls/22/" in p for p in puts), "189.1: PR 22 (up to date) got an Update branch call"


# 189.2: PRs already up to date get no call

def test_prs_up_to_date_with_main_get_no_update_call(record_property):
    """Open PRs that already hold main's newest commit get no Update branch call; the one behind still does.

    Fakes three open PRs: one behind main, one only ahead of it, one identical to it; only the behind one is updated."""
    record_property("proves", "189.2")
    gh = FakeGitHub([pr(31, behind=0, ahead=4), pr(32, behind=2), pr(33, behind=0, ahead=0, draft=True)])
    uptodate().run(REPO, "main", MERGE, rest=gh)
    assert gh.updated() == [32], f"189.2: expected only PR 32 (behind main) updated, got {gh.updated()}"


# 189.3: a refused update says why on that PR, and the others still go through

def test_a_refused_update_comments_once_with_githubs_reason_and_the_rest_go_on(record_property):
    """When GitHub refuses an update, that PR gets one comment with GitHub's reason, and every other PR is still updated.

    Fakes four PRs behind main: GitHub refuses the first (a merge conflict) and the third (a workflow file the app may
    not push). Each refused PR must get exactly one comment saying it could not be updated, with GitHub's own message;
    the second and fourth must still be updated and get no comment."""
    record_property("proves", "189.3")
    gh = FakeGitHub([pr(41, behind=1), pr(42, behind=1), pr(43, behind=2), pr(44, behind=5)],
                    refuse={41: CONFLICT, 43: WORKFLOW_REFUSED})
    uptodate().run(REPO, "main", MERGE, rest=gh)
    assert sorted(gh.updated()) == [41, 42, 43, 44], f"189.3: every PR behind main should be tried, got {gh.updated()}"
    said = gh.comments()
    assert sorted(said) == [41, 43], f"189.3: expected comments on PRs 41 and 43 only, got {sorted(said)}"
    for n, reason in ((41, CONFLICT), (43, WORKFLOW_REFUSED)):
        assert len(said[n]) == 1, f"189.3: PR {n} got {len(said[n])} comments, expected one"
        assert "could not be updated" in said[n][0], f"189.3: PR {n}'s comment does not say it could not be updated: {said[n][0]!r}"
        assert reason in said[n][0], f"189.3: PR {n}'s comment does not carry GitHub's reason {reason!r}: {said[n][0]!r}"


def test_a_run_with_nothing_refused_comments_nowhere(record_property):
    """When every update goes through, no PR gets a comment.

    Fakes two PRs behind main that GitHub updates; no comment may be posted."""
    record_property("proves", "189.3")
    gh = FakeGitHub([pr(51, behind=1), pr(52, behind=1, draft=True)])
    uptodate().run(REPO, "main", MERGE, rest=gh)
    assert gh.updated() and gh.comments() == {}, f"189.3: comments posted without a refusal: {gh.comments()}"


# 189.4: the update is made with the Dokima app's token, never github.token

def test_the_workflow_updates_with_the_apps_token(record_property):
    """The workflow makes its GitHub calls with the Dokima app's token, never with github.token.

    Reads .github/workflows/uptodate.yml: the job opens the keys environment, mints a token with
    actions/create-github-app-token from DOKIMA_APP_ID and DOKIMA_APP_KEY, hands that step's token to GH_TOKEN, and
    names neither github.token nor GITHUB_TOKEN anywhere."""
    record_property("proves", "189.4")
    assert os.path.exists(WORKFLOW), "189.4: .github/workflows/uptodate.yml is missing"
    text = open(WORKFLOW).read()
    assert re.search(r"(?m)^    environment: keys\s*$", text), "189.4: the job does not open the keys environment"
    m = re.search(r"(?ms)^      - id: (\S+)\n\s+uses: actions/create-github-app-token@\S+.*?(?=^      - )", text)
    assert m, "189.4: no step mints the Dokima app's token with actions/create-github-app-token (as `- id: NAME`)"
    assert "vars.DOKIMA_APP_ID" in m[0] and "secrets.DOKIMA_APP_KEY" in m[0], "189.4: the token is not the Dokima app's"
    assert re.search(rf"GH_TOKEN:\s*\$\{{\{{\s*steps\.{re.escape(m[1])}\.outputs\.token\s*\}}\}}", text), \
        "189.4: GH_TOKEN is not the app token step's output"
    for banned in ("github.token", "GITHUB_TOKEN"):
        assert banned not in text, f"189.4: the workflow names {banned}"


# 189.5: the update passes the PR head it read

def test_every_update_passes_the_head_it_read(record_property):
    """Every Update branch call carries the PR head it read, so a PR pushed to meanwhile is not updated over.

    Fakes two PRs behind main; a worker pushes to the second between the read and the update. Every call must
    carry expected_head_sha equal to the head GitHub listed, the moved PR is then refused by GitHub, and the other
    is updated."""
    record_property("proves", "189.5")
    gh = FakeGitHub([pr(61, behind=1), pr(62, behind=1)], moved={62: "99" * 20})
    uptodate().run(REPO, "main", MERGE, rest=gh)
    puts = gh.puts()
    assert sorted(n for n, _ in puts) == [61, 62], f"189.5: expected both PRs tried, got {puts}"
    for n, fields in puts:
        assert fields.get("expected_head_sha") == f"{n:02d}" * 20, \
            f"189.5: PR {n}'s update did not pass the head it read as expected_head_sha: {fields}"

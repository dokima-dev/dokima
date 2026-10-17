"""A clash with main goes to the planner, on the record (#190).

After a merge to main, `dokima.uptodate.run(repo, base, sha, rest=..., on_clash=...)` calls `on_clash(pr, sha)` for
every PR GitHub refuses to update with a merge conflict (#189). This story fills that hook with
`dokima.uptodate.clash(repo, base, sha, pr, rest=api, files=None, owners=None)`, and `python3 -m dokima.uptodate`
wires it in:
  - `pr` is the PR as GitHub lists it; `sha` is the merge on main (the push's head sha);
  - `files(pr, sha)` returns the paths that clashed; by default a trial merge in the git checkout the module runs in,
    fetching what it needs from its `origin` remote;
  - `owners` are the code owners' logins; by default those of the checkout's CODEOWNERS;
  - every GitHub call goes through `rest(method, path, **fields)`, shaped like `dokima.board.api`.

A Dokima PR is one whose branch is try/issue-N in this same repo. Its clash leaves a record on issue N (a bot comment
carrying agent.MARK with the JSON record folded below, role "updater") and starts the planner for N with the river's
own `dokima-next` signal, unless a clash record is already waiting for its planner. Any other PR gets a comment that
mentions the owners and starts nothing.

The worker side runs the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin
where main and try/issue-57 clash, the worker's edits, the fence and the push.

The fake GitHub (in-process) answers:
  - GET repos/o/r/commits/SHA/pulls: the PRs that merge brought in;
  - GET repos/o/r/issues/N/comments (any query; empty past page 1): the issue's comments, REST-shaped;
  - GET repos/o/r/pulls/N: the PR;
  - GET repos/o/r/issues/N: the issue with its labels, the `autopilot` label by default (#369), or GitHub's refusal;
  - POST repos/o/r/issues/N/comments (body): a new comment, kept;
  - POST repos/o/r/dispatches (event_type, client_payload as a dict or as client_payload[key] fields).
"""
import json
import os
import re
import shutil
import stat
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, card  # noqa: E402
import test_start as ts  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = "o/r"
MERGE = "c1a5" * 10
OWNERS = ["alice", "bob"]
FILES = ["dokima/app.py", "docs/notes.md"]
BOT_REST = "dokima-runtime[bot]"
WORKER = {"role": "worker", "stage": None, "run_id": "3", "run": "https://github.com/o/r/actions/runs/3",
          "models": ["claude-opus-5-5"], "handback": {"summary": "Rebuilt the pull request on main.", "criteria": {"7.1": "done"},
                       "evidence": "pytest -q: 3 passed"},
          "check": {"passed": True, "problems": []}}
MARKERS = re.compile(r"(?m)^(<<<<<<<|=======|>>>>>>>)( |$)")


def uptodate():
    """The module under test; a missing clash() fails only the test that asked."""
    from dokima import uptodate as mod
    if not hasattr(mod, "clash"):
        pytest.fail("190: dokima.uptodate.clash(repo, base, sha, pr, rest, files, owners) is missing")
    return mod


def pr(n, ref, repo=REPO):
    """One open PR as GitHub lists it, from branch `ref` of `repo`."""
    return {"number": n, "state": "open", "draft": False, "base": {"ref": "main"},
            "head": {"sha": f"{n:02d}" * 20, "ref": ref, "label": f"{repo.split('/')[0]}:{ref}",
                     "repo": {"full_name": repo}}}


def rest_comment(login, body, t):
    """A comment as GitHub's REST API returns it."""
    return {"id": abs(hash((login, body, t))) % 10**8, "user": {"login": login, "type": "Bot" if login.endswith("[bot]") else "User"},
            "body": body, "created_at": t}


class FakeGitHub:
    """GitHub's REST API for one repo, recording every call."""

    def __init__(self, merged=(300,), comments=None, prs=(), labels=("autopilot",), unreadable=False):
        self.merged, self.comments, self.prs = list(merged), {k: list(v) for k, v in (comments or {}).items()}, list(prs)
        self.labels, self.unreadable = list(labels), unreadable
        self.calls = []

    def __call__(self, method, path, **fields):
        method, bare = method.upper(), path.split("?")[0].lstrip("/")
        self.calls.append((method, bare, fields))
        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[0-9a-f]+/pulls", bare):
            return [{"number": n, "state": "closed", "merged_at": "2026-10-08T10:00:00Z", "merge_commit_sha": MERGE}
                    for n in self.merged]
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)/comments", bare)
        if method == "GET" and m:
            page = str(fields.get("page") or (re.search(r"[?&]page=(\d+)", path) or [None, "1"])[1])
            return list(self.comments.get(int(m[1]), [])) if page == "1" else []
        if method == "POST" and m:
            c = rest_comment(BOT_REST, fields.get("body", ""), f"2026-10-08T12:{len(self.calls):02d}:00Z")
            self.comments.setdefault(int(m[1]), []).append(c)
            return c
        m = re.fullmatch(rf"repos/{REPO}/issues/(\d+)", bare)
        if method == "GET" and m:
            if self.unreadable:
                raise subprocess.CalledProcessError(1, ["gh", "api", path], output='{"message": "Server Error"}',
                                                    stderr="gh: Server Error (HTTP 502)")
            return {"number": int(m[1]), "state": "open", "labels": [{"name": l} for l in self.labels]}
        m = re.fullmatch(rf"repos/{REPO}/pulls/(\d+)", bare)
        if method == "GET" and m:
            return next(p for p in self.prs if p["number"] == int(m[1]))
        if method == "POST" and bare == f"repos/{REPO}/dispatches":
            return {}
        raise AssertionError(f"190: unexpected GitHub call {method} {path} {fields}")

    def posted(self):
        """[(issue or PR number, body)] of every comment posted, in order."""
        return [(int(re.search(r"issues/(\d+)/", p)[1]), f.get("body", "")) for m, p, f in self.calls
                if m == "POST" and p.endswith("/comments")]

    def dispatches(self):
        """[(event_type, payload)] of every signal sent, payload as a dict of strings."""
        out = []
        for m, p, f in self.calls:
            if m == "POST" and p == f"repos/{REPO}/dispatches":
                payload = f.get("client_payload") if isinstance(f.get("client_payload"), dict) else \
                    {k[len("client_payload["):-1]: v for k, v in f.items() if k.startswith("client_payload[")}
                out.append((f.get("event_type"), {k: str(v) for k, v in payload.items()}))
        return out

    def index(self, kind):
        """Where in the call list the first comment post ('comment') or dispatch ('dispatch') came."""
        for i, (m, p, f) in enumerate(self.calls):
            if m == "POST" and ((kind == "comment" and p.endswith("/comments")) or (kind == "dispatch" and p.endswith("/dispatches"))):
                return i
        return None


def clash(gh, the_pr, files=FILES, sha=MERGE):
    """Run the clash handler for one PR with fixed files and owners."""
    uptodate().clash(REPO, "main", sha, the_pr, rest=gh, files=lambda p, s: list(files), owners=list(OWNERS))


def the_record(body):
    """The record a comment carries, read as the river reads a bot comment."""
    recs = agent.records([{"author": {"login": agent.BOT}, "body": body}])
    assert len(recs) == 1, f"190.1: the clash comment carries {len(recs)} records the river can read, expected one:\n{body}"
    return recs[0]


def visible(body):
    """The part of a comment the owner sees without opening a fold."""
    return re.sub(r"(?s)<details.*?</details>", "", body)


# 190.1: a clash on a Dokima PR leaves one record on its issue, naming the merge and every clashed file

def test_a_clash_leaves_one_record_naming_the_merge_its_pr_and_every_clashed_file(record_property):
    """A clash leaves one record naming the merge, its PR and every clashed file.

    Proves 190.1.
    Fakes PR #70 from try/issue-7 clashing with merge c1a5... (which merged PR #300) in two files. Exactly one comment
    must be posted on issue #7; the river must read it as one bot record of role "updater" whose hand-back holds the
    merge sha, merged_pr 300, pr 70 and exactly the two files; and the comment's visible text must name the short sha,
    #300 and both files. A second case where the merge came with no PR must record merged_pr as null."""
    record_property("proves", "190.1")
    gh = FakeGitHub(merged=(300,))
    clash(gh, pr(70, "try/issue-7"))
    on7 = [b for n, b in gh.posted() if n == 7]
    assert len(on7) == 1, f"190.1: expected one record on issue #7, got {len(on7)}: {gh.posted()}"
    assert {n for n, _ in gh.posted()} <= {7, 70}, f"190.1: comments went beyond issue #7 and PR #70: {gh.posted()}"
    rec = the_record(on7[0])
    h = rec.get("handback") or {}
    assert rec.get("role") == "updater", f"190.1: the record's role is {rec.get('role')!r}, expected 'updater'"
    assert h.get("merge") == MERGE, f"190.1: the record does not name the merge {MERGE}: {h}"
    assert h.get("merged_pr") == 300, f"190.1: the record does not name PR #300 as the merge's PR: {h}"
    assert h.get("pr") == 70, f"190.1: the record does not name PR #70 as the one that clashed: {h}"
    assert sorted(h.get("files") or []) == sorted(FILES), f"190.1: the record's files are {h.get('files')}, expected {FILES}"
    shown = visible(on7[0])
    for word in (MERGE[:7], "#300", *FILES):
        assert word in shown, f"190.1: the record's visible text does not name {word!r}:\n{shown}"

    gh = FakeGitHub(merged=())
    clash(gh, pr(70, "try/issue-7"))
    h = the_record([b for n, b in gh.posted() if n == 7][0]).get("handback") or {}
    assert h.get("merge") == MERGE and h.get("merged_pr") is None, \
        f"190.1: a merge with no PR should record merged_pr null and the merge sha, got {h}"


def test_the_clash_record_reaches_the_planner_through_its_pack(record_property, tmp_path):
    """The clash record is a record the planner's starting pack accepts.

    Proves 190.1.
    Builds a planner pack holding the clash record the way agent.pack writes records (in/NN-role.json) and runs
    the pack check; it must raise no problem about the record."""
    record_property("proves", "190.1")
    gh = FakeGitHub()
    clash(gh, pr(70, "try/issue-7"))
    rec = the_record([b for n, b in gh.posted() if n == 7][0])
    os.makedirs(tmp_path / "in")
    (tmp_path / "issue.md").write_text("# Issue #7: x\n\nbody\n\n## Comments\n")
    (tmp_path / "open_blockers.json").write_text("[]")
    (tmp_path / "in" / f"01-{rec['role']}.json").write_text(json.dumps(rec))
    bad = [p for p in agent.problems_pack("planner", "", str(tmp_path)) if "record" in p]
    assert not bad, f"190.1: the planner's pack check refuses the clash record: {bad}"


# 190.2: right after the record, the planner starts by itself; no worker

def test_right_after_the_record_the_planner_starts_and_no_worker(record_property):
    """Right after the clash record, the planner starts by itself; no worker does.

    Proves 190.2.
    Fakes PR #70 from try/issue-7 clashing, on an issue with no earlier record. Exactly one dokima-next signal must be
    sent, for role planner on issue 7, after the record was posted; no signal may name the worker."""
    record_property("proves", "190.2")
    gh = FakeGitHub()
    clash(gh, pr(70, "try/issue-7"))
    sent = gh.dispatches()
    assert len(sent) == 1, f"190.2: expected one signal starting the planner, got {sent}"
    event, payload = sent[0]
    assert event == "dokima-next", f"190.2: the signal is {event!r}, not the river's dokima-next"
    assert payload.get("role") == "planner" and payload.get("issue") == "7", f"190.2: the signal does not start the planner for #7: {payload}"
    assert gh.index("comment") is not None and gh.index("comment") < gh.index("dispatch"), \
        "190.2: the planner was started before the clash record was posted"
    assert not any(p.get("role") == "worker" for _, p in sent), f"190.2: the clash started a worker: {sent}"


def test_the_issue_card_shows_plan_and_not_needs_you_after_a_clash_record(record_property):
    """After a clash record, the card shows Plan and asks nothing of the owner.

    Proves 190.2.
    Feeds the card the issue's history ending with the clash record and asks for its status: it must be Plan with
    nothing for the owner to do, since the planner starts by itself."""
    record_property("proves", "190.2")
    gh = FakeGitHub()
    clash(gh, pr(70, "try/issue-7"))
    body = [b for n, b in gh.posted() if n == 7][0]
    items = [{"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T12:00:00Z"}]
    found = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "owners": set(OWNERS)}
    got = card.status({"number": 7}, found)
    assert got == ("Plan", None), f"190.2: after a clash record the card should be in Plan with nothing for the owner, got {got}"


# 190.3: a clash on a PR Dokima didn't build pings the owner and starts nothing

def test_a_clash_on_a_pr_dokima_did_not_build_pings_the_owner_and_starts_nothing(record_property):
    """A clash on a PR Dokima didn't build pings the owners and starts nothing.

    Proves 190.3.
    Two such PRs: #41 from a person's branch, and #42 from a fork whose branch happens to be named try/issue-7. Each
    must get one comment on the PR naming the short sha, #300 and every clashed file and mentioning @alice and @bob; no
    signal may be sent and no other issue may get a comment. Beside them, Dokima's own PR #70 does send its signal."""
    record_property("proves", "190.3")
    for the_pr in (pr(41, "fix-typo"), pr(42, "try/issue-7", repo="someone/r")):
        n = the_pr["number"]
        gh = FakeGitHub(prs=[the_pr])
        clash(gh, the_pr)
        assert gh.dispatches() == [], f"190.3: a clash on PR #{n} (not built by Dokima) started an agent: {gh.dispatches()}"
        where = {k for k, _ in gh.posted()}
        assert where == {n}, f"190.3: PR #{n}'s clash commented on {sorted(where)}, expected only on PR #{n}"
        pings = [b for k, b in gh.posted() if all(w in b for w in (MERGE[:7], "#300", *FILES, "@alice", "@bob"))]
        assert len(pings) == 1, \
            f"190.3: PR #{n} should get one comment naming the merge, #300, every file and mentioning @alice and @bob, got {gh.posted()}"
    gh = FakeGitHub()
    clash(gh, pr(70, "try/issue-7"))
    assert len(gh.dispatches()) == 1, "190.3: Dokima's own PR from try/issue-7 should still start its planner"


# 190.4: a worker on a branch that still clashes starts, and pushes main merged with no conflict markers

class Clash(ts.Machine):
    """A worker run on #57 from checkout to push, its branch clashing with main.

    main and try/issue-57 both change app.py and lib.py; main also changes other.py and adds fresh.py, outside the
    plan's scope. The worker resolves app.py (in scope, to 'a = 4') and lib.py (out of scope), and also writes
    stray.py, outside scope. With clash=False the branch changes only app.py's neighbour, so it merges cleanly."""

    def __init__(self, tmp, clash=True):
        super().__init__(tmp, [])
        t, src = self.tmp, f"{self.tmp}/src"

        def commit(files, message):
            for path, text in files.items():
                os.makedirs(os.path.dirname(f"{src}/{path}") or src, exist_ok=True)
                open(f"{src}/{path}", "w").write(text)
            ts.sh(src, "git", "add", "-A")
            ts.sh(src, "git", "commit", "-qm", message)
        commit({"app.py": "a = 1\n", "lib.py": "l = 1\n", "other.py": "o = 1\n", "near.py": "n = 1\n"}, "base")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        ts.sh(src, "git", "checkout", "-q", "-b", f"try/issue-{ts.N}")
        mine = {"app.py": "a = 2\n", "lib.py": "l = 2\n"} if clash else {"near.py": "n = 2\n"}
        commit({**mine, "tests/test_x.py": 'def test_a():\n    """A."""\n'}, "the branch's work")
        ts.sh(src, "git", "push", "-q", "origin", f"try/issue-{ts.N}")
        ts.sh(src, "git", "checkout", "-q", "main")
        commit({"app.py": "a = 3\n", "lib.py": "l = 3\n", "other.py": "o = 2\n", "fresh.py": "f = 1\n"}, "another merge")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        self.main_sha = ts.sh(src, "git", "rev-parse", "HEAD")
        plan = json.dumps({"kind": "user_story", "acceptance_criteria": [{"files": ["app.py", "near.py"]}]})
        edits = (f"mkdir -p \"$PACK\" \"$OUT\" && echo '{plan}' > \"$PACK/plan.json\"\n"
                 "printf 'a = 4\\n' > app.py\nprintf 'l = 4\\n' > lib.py\nprintf 's = 1\\n' > stray.py\n")
        wf = ts.workflow("agent.yml")
        job = wf["jobs"]["run"]
        steps = job["steps"]
        named = {s.get("name"): s for s in steps}
        app = next(i for i, s in enumerate(steps) if s.get("id") == "app")
        end = next(i for i, s in enumerate(steps) if str(s.get("name", "")).startswith("Save the conversation"))
        fence = next(s for s in steps if str(s.get("name", "")).startswith("Fence"))
        # Dokima's code comes from the checkout of Dokima's own repo, played before the copy step (#812).
        picked = [named["Dokima's code from Dokima's own repo"], named["Copy the runtime from main before touching any branch"],
                  named["Starting branch"],
                  {"name": "The worker resolves and edits", "run": edits}, fence] + steps[app:end]
        open(f"{t}/event.json", "w").write('{"inputs": {"role": "worker", "stage": "", "issue": "%s"}}' % ts.N)
        ctx = {"inputs": ts.Ctx(role="worker", stage="", issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42", run_attempt="1",
                                server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        job = {**job, "env": {**(job.get("env") or {}), "PASSED": "true", "STARTED": "true"}, "steps": picked}
        self.result, _ = self.run_job("run", job, ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))

    def pushed(self, path):
        """A file's text on the pushed try/issue-57, or None when absent."""
        p = subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", "show", f"try/issue-{ts.N}:{path}"],
                           capture_output=True, text=True)
        return p.stdout if p.returncode == 0 else None

    def pushed_files(self):
        """Every file on try/issue-57 in the origin after the run."""
        return ts.sh(self.tmp, "git", "--git-dir", f"{self.tmp}/origin.git", "ls-tree", "-r", "--name-only", f"try/issue-{ts.N}").split()

    def has_main(self):
        """True when main's newest commit is part of what was pushed to try/issue-57."""
        return subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", "merge-base", "--is-ancestor", self.main_sha,
                               f"try/issue-{ts.N}"]).returncode == 0

    def dropped(self):
        """The paths the fence listed as dropped."""
        path = os.path.join(self.env.get("OUT", ""), "dropped.txt")
        return open(path).read().split() if self.env.get("OUT") and os.path.exists(path) else []


def test_a_worker_on_a_branch_that_clashes_starts_and_pushes_main_merged_with_no_markers(record_property, tmp_path):
    """A worker on a clashing branch starts and pushes main merged, with no markers.

    Proves 190.4.
    Runs the agent workflow's real steps for a worker on try/issue-57, which clashes with main in app.py and lib.py: the
    checkout, the worker's edits (it resolves both files), the fence and the push. The run must succeed; the pushed
    branch must contain main's newest commit, no file in it may hold a conflict marker line, and app.py (in scope) must
    hold the worker's resolution. Beside it, a branch that merges cleanly must still start and push with main merged."""
    record_property("proves", "190.4")
    clean = Clash(tmp_path / "clean", clash=False)
    assert clean.result == "success", f"190.4: a worker on a branch that merges cleanly failed at {clean.failed_step!r}:\n{clean.tail()}"
    assert clean.has_main(), "190.4: a cleanly merging branch was pushed without main merged in"
    m = Clash(tmp_path / "clash")
    assert m.result == "success", f"190.4: a worker on a branch that clashes with main failed at {m.failed_step!r}:\n{m.tail()}"
    assert m.has_main(), "190.4: what the worker pushed does not have main merged in"
    marked = [f for f in m.pushed_files() if MARKERS.search(m.pushed(f) or "")]
    assert not marked, f"190.4: the pushed branch still holds conflict markers in {marked}"
    assert m.pushed("app.py") == "a = 4\n", f"190.4: app.py does not hold the worker's resolution: {m.pushed('app.py')!r}"


# 190.5: main's own changes are never dropped by the fence; only the worker's own out-of-scope changes are

def test_the_fence_keeps_mains_changes_and_drops_only_the_workers_out_of_scope_ones(record_property, tmp_path):
    """Main's changes survive the fence; the worker's own out-of-scope file does not.

    Proves 190.5.
    Runs the same clashing worker run. other.py (changed on main) and fresh.py (added on main), both outside the plan's
    scope, must be pushed exactly as main has them and not be listed as dropped; stray.py, which the worker wrote
    outside scope, must be dropped and not pushed."""
    record_property("proves", "190.5")
    m = Clash(tmp_path)
    assert m.result == "success", f"190.5: the clashing worker run failed at {m.failed_step!r}:\n{m.tail()}"
    assert m.pushed("other.py") == "o = 2\n", f"190.5: main's change to other.py was not kept: {m.pushed('other.py')!r}"
    assert m.pushed("fresh.py") == "f = 1\n", f"190.5: main's new fresh.py was not kept: {m.pushed('fresh.py')!r}"
    assert not {"other.py", "fresh.py"} & set(m.dropped()), f"190.5: the fence listed main's own files as dropped: {m.dropped()}"
    assert m.pushed("stray.py") is None, "190.5: the worker's out-of-scope stray.py was pushed"
    assert "stray.py" in m.dropped(), f"190.5: the fence did not list the worker's stray.py as dropped: {m.dropped()}"


# 190.6: further merges while the clash's planner waits or runs start no second planner

def test_a_second_clash_while_the_planner_waits_records_but_starts_no_second_planner(record_property):
    """A clash while the planner waits starts no second planner.

    Proves 190.6.
    Issue #7's newest bot record is a clash record (its planner has not posted yet, though its live card may be up). A
    second clash must send no signal; since #369 it posts nothing more on #7 either, the clash being sent back already."""
    record_property("proves", "190.6")
    first = FakeGitHub()
    clash(first, pr(70, "try/issue-7"))
    record = first.comments[7][-1]
    live = rest_comment(BOT_REST, f"{agent.LIVE}\nPlanner · working", "2026-10-08T12:59:00Z")
    gh = FakeGitHub(merged=(301,), comments={7: [record, live]})
    clash(gh, pr(70, "try/issue-7"), sha="d00d" * 10)
    assert [n for n, _ in gh.posted()].count(7) == 0, f"190.6: the second clash posted again on #7: {gh.posted()}"
    assert gh.dispatches() == [], f"190.6: a second planner was started while the first was waiting: {gh.dispatches()}"


def test_a_clash_after_the_planner_answered_starts_it_again(record_property):
    """After the worker rebuilt, the next clash starts the planner again; pasted records don't count.

    Proves 190.6.
    Two histories of issue #7: a clash record followed by the bot's planner and worker records (the clash was answered
    and rebuilt, #369), and a planner record followed by a clash record pasted by someone other than the bot. In both,
    a new clash must send exactly one signal for the planner."""
    record_property("proves", "190.6")
    first = FakeGitHub()
    clash(first, pr(70, "try/issue-7"))
    record = first.comments[7][-1]
    planned = rest_comment(BOT_REST, agent.render(ts.planner_record(ts.STORY)), "2026-10-08T13:00:00Z")
    built = rest_comment(BOT_REST, agent.render(WORKER), "2026-10-08T13:30:00Z")
    pasted = rest_comment("mallory", record["body"], "2026-10-08T14:00:00Z")
    for case, history in (("after the planner and worker records", [record, planned, built]), ("with a pasted clash record", [planned, pasted])):
        gh = FakeGitHub(merged=(302,), comments={7: history})
        clash(gh, pr(70, "try/issue-7"), sha="beef" * 10)
        roles = [p.get("role") for _, p in gh.dispatches()]
        assert roles == ["planner"], f"190.6: {case}, a new clash should start the planner once, got signals {gh.dispatches()}"


# 190.1 and 190.2, from outside: the real module, a real trial merge and gh

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
bare, repo, p = path.split("?")[0].lstrip("/"), d["repo"], d["pr"]
def out(x):
    print(json.dumps(x)); sys.exit(0)
if method == "GET" and bare == f"repos/{repo}/pulls":
    out([p] if "page=2" not in path and fields.get("page") not in ("2", 2) else [])
if method == "GET" and bare.startswith(f"repos/{repo}/compare/"):
    out({"behind_by": 1, "ahead_by": 1, "status": "diverged"})
if method == "PUT" and bare.endswith("/update-branch"):
    print(json.dumps({"message": "merge conflict between base and head"}))
    sys.stderr.write("gh: merge conflict between base and head (HTTP 422)\n"); sys.exit(1)
if method == "GET" and re.fullmatch(f"repos/{repo}/commits/[0-9a-f]+/pulls", bare):
    out([{"number": 300, "state": "closed", "merged_at": "2026-10-08T10:00:00Z"}])
if method == "GET" and re.fullmatch(f"repos/{repo}/issues/\\d+/comments", bare):
    out([])
if method == "GET" and re.fullmatch(f"repos/{repo}/issues/\\d+", bare):
    out({"number": int(bare.rsplit("/", 1)[1]), "state": "open", "labels": [{"name": "autopilot"}]})
if method == "GET" and bare == f"repos/{repo}/pulls/{p['number']}":
    out(p)
if method == "POST" and bare.endswith("/comments"):
    out({"id": 1, "body": fields.get("body", "")})
if method == "POST" and bare == f"repos/{repo}/dispatches":
    sys.exit(0)
sys.stderr.write("gh: Not Found (HTTP 404)\n"); sys.exit(1)
'''


def test_the_real_module_records_the_files_a_trial_merge_finds_and_starts_the_planner(record_property, tmp_path):
    """Run as the workflow runs it, a real clash is recorded and starts the planner.

    Proves 190.1 and 190.2.
    Builds a temp origin where main and try/issue-7 (also at refs/pull/70/head) both change app.py and lib.py while
    main alone changes other.py, checks out main from it, and runs `python3 -m dokima.uptodate` there with a fake
    `gh` whose Update branch answers 422 merge conflict. Issue #7 must get one record naming the merge and exactly
    app.py and lib.py, and one dokima-next signal must start the planner for #7."""
    record_property("proves", "190.1")
    record_property("proves", "190.2")
    origin, src, work = tmp_path / "origin.git", tmp_path / "src", tmp_path / "work"
    ts.sh(str(tmp_path), "git", "init", "-q", "--bare", "-b", "main", str(origin))
    os.makedirs(src / ".github")
    ts.sh(str(src), "git", "init", "-q", "-b", "main")
    (src / ".github" / "CODEOWNERS").write_text("* @alice\n")
    for name, text in (("app.py", "a = 1\n"), ("lib.py", "l = 1\n"), ("other.py", "o = 1\n")):
        (src / name).write_text(text)
    ts.sh(str(src), "git", "add", "-A")
    ts.sh(str(src), "git", "commit", "-qm", "base")
    ts.sh(str(src), "git", "checkout", "-q", "-b", "try/issue-7")
    (src / "app.py").write_text("a = 2\n")
    (src / "lib.py").write_text("l = 2\n")
    ts.sh(str(src), "git", "commit", "-qam", "branch")
    head = ts.sh(str(src), "git", "rev-parse", "HEAD")
    ts.sh(str(src), "git", "checkout", "-q", "main")
    for name, text in (("app.py", "a = 3\n"), ("lib.py", "l = 3\n"), ("other.py", "o = 2\n")):
        (src / name).write_text(text)
    ts.sh(str(src), "git", "commit", "-qam", "merge on main")
    sha = ts.sh(str(src), "git", "rev-parse", "HEAD")
    ts.sh(str(src), "git", "push", "-q", str(origin), "main", "try/issue-7", f"{head}:refs/pull/70/head")
    ts.sh(str(tmp_path), "git", "clone", "-q", "--single-branch", "-b", "main", str(origin), str(work))
    the_pr = {**pr(70, "try/issue-7"), "head": {**pr(70, "try/issue-7")["head"], "sha": head}}
    (tmp_path / "gh.json").write_text(json.dumps({"repo": REPO, "pr": the_pr}))
    fake = tmp_path / "bin" / "gh"
    fake.parent.mkdir()
    fake.write_text(FAKE_GH.replace("#!PYTHON", f"#!{sys.executable}"))
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    log = tmp_path / "calls.jsonl"
    env = ts.git_env(dict(os.environ, PATH=f"{fake.parent}{os.pathsep}{os.environ['PATH']}", GITHUB_REPOSITORY=REPO,
                          GITHUB_SHA=sha, GITHUB_REF_NAME="main", GITHUB_REF="refs/heads/main", GH_TOKEN="fake-token",
                          PYTHONPATH=ROOT, FAKE_GH_JSON=str(tmp_path / "gh.json"), FAKE_GH_LOG=str(log)))
    env.pop("PYTHONSAFEPATH", None)
    done = subprocess.run([sys.executable, "-m", "dokima.uptodate"], cwd=str(work), env=env, capture_output=True, text=True, timeout=60)
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    said = f"gh calls {calls}\noutput {done.stdout}{done.stderr}"
    posts = [f.get("body", "") for m, p, f in calls if m == "POST" and re.search(r"issues/7/comments$", p or "")]
    records = [r for b in posts for r in agent.records([{"author": {"login": agent.BOT}, "body": b}])]
    assert len(records) == 1, f"190.1: expected one record on issue #7, got {len(records)}\n{said}"
    h = records[0].get("handback") or {}
    assert h.get("merge") == sha, f"190.1: the record does not name the merge {sha}: {h}"
    assert sorted(h.get("files") or []) == ["app.py", "lib.py"], f"190.1: the trial merge's clashed files are {h.get('files')}, expected app.py and lib.py\n{said}"
    sent = [f for m, p, f in calls if m == "POST" and (p or "").lstrip("/") == f"repos/{REPO}/dispatches"]
    roles = [f.get("client_payload[role]") or (f.get("client_payload") or {}).get("role") for f in sent]
    issues = [str(f.get("client_payload[issue]") or (f.get("client_payload") or {}).get("issue")) for f in sent]
    assert roles == ["planner"] and issues == ["7"], f"190.2: expected one signal starting the planner for #7\n{said}"

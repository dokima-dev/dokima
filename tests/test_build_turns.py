"""Stories sharing a code file take turns to build (#668, story 4 of #661).

A split files its stories as sub-issues of one parent, and each goes through the river on its own. Before #668 no
build waited on another, so two stories changing the same code file could build it at once and clash. Now a story's
build waits while another open story of the same parent that shares a code file with it holds the turn: its build has
started (a worker ran on it, or its pull request is open) and its pull request has not merged. The turn ends when that
pull request merges. Planning and plan review never wait, and markdown files never count. The files compared are each
story's own newest plan's files, so a story whose own planner added files is checked on its final list.

Every test runs the real commands as subprocesses against a fake GitHub, the one of tests/test_plan_links_recorded.py,
taught here to answer what a tree of stories needs: each issue's parent (`repos/o/r/issues/N/parent` and the REST
issue's `parent_issue_url`), a parent's sub-issues, the label filter of the issue list, and pull requests from
`try/issue-N` (`gh pr list`, `gh pr view`, `repos/o/r/pulls/N`), open or merged. Records are put both where the
river reads them (the bot's record comments) and where a run's pack reads them (record files on a logs branch,
tests/record_seed.py). The moments are the ones agent.yml and autopilot.yml run:

- `python3 -m dokima.agent next N OUT`: what follows a run, given its record (a plan, or the plan review approving it).
- `python3 -m dokima.agent pack N ROLE STAGE DIR`: the starting pack; for the worker it is the owner's `/work`.
- `python3 -m dokima.agent closed N`: what autopilot does once issue N closes, as when its pull request merges.

The tree: parent #700 on autopilot with stories #701, #702 and #703, all on autopilot. #701 is building
`dokima/shared.py` (a worker ran and its pull request from try/issue-701 is open). #702 is the story under test.
"""
import json
import os
import subprocess
import sys

import record_seed
import test_plan_links_recorded as pl
from dokima import agent

ROOT = pl.ROOT
P, A, B, C = 700, 701, 702, 703
PARENT = f"https://github.com/o/r/issues/{P}"
SHARED, OWN_A, OWN_B, DOC = "dokima/shared.py", "dokima/a_only.py", "dokima/b_only.py", "rules/flow.md"
ERROR = "HTTP 502: Server Error (sub_issues)"

# The fake GitHub of test_plan_links_recorded, with a tree of issues and pull requests on top. Each name it redefines
# is looked up when called, so its own routes below use these.
TREE = r'''
_flat_obj = obj


def obj(n):
    o = _flat_obj(n)
    up = S.get("parents", {}).get(str(n))
    o["parent_issue_url"] = f"https://api.github.com/repos/o/r/issues/{up}" if up else None
    subs = S.get("subs", {}).get(str(n), [])
    o["sub_issues_summary"] = {"total": len(subs), "completed": sum(1 for m in subs if issue(m).get("state") == "closed"),
                               "percent_completed": 0}
    o["state_reason"] = "completed" if o["state"] == "closed" else None
    return o


def prs():
    return S.setdefault("prs", [])


def gh_pr(p):
    return {"number": p["number"], "state": p["state"], "headRefName": p["head"], "baseRefName": "main",
            "mergedAt": "2026-10-15T01:00:00Z" if p["state"] == "MERGED" else None, "title": p["head"],
            "url": f"https://github.com/o/r/pull/{p['number']}", "isDraft": p["state"] == "OPEN",
            "comments": [], "reviews": [], "body": ""}


def rest_pr(p):
    return {"number": p["number"], "state": "open" if p["state"] == "OPEN" else "closed",
            "merged": p["state"] == "MERGED", "merged_at": gh_pr(p)["mergedAt"], "draft": p["state"] == "OPEN",
            "head": {"ref": p["head"], "sha": "abc"}, "base": {"ref": "main"}, "title": p["head"], "body": "",
            "html_url": gh_pr(p)["url"]}


def wanted(p, state):
    state = (state or "open").lower()
    return state == "all" or (state == "open" and p["state"] == "OPEN") or (state == "merged" and p["state"] == "MERGED") \
        or (state == "closed" and p["state"] in ("CLOSED", "MERGED"))


if a[:2] == ["issue", "view"]:
    n = number(a[2])
    o = obj(n)
    o["state"] = o["state"].upper()
    o["comments"] = issue(n).get("comments", [])
    out(o)
    sys.exit(0)
if a[:2] == ["pr", "list"]:
    head = flag("--head", "-H")
    out([gh_pr(p) for p in prs() if (head is None or p["head"] == head) and wanted(p, flag("--state", "-s"))])
    sys.exit(0)
if a[:2] == ["pr", "view"]:
    n = number(a[2])
    found = [p for p in prs() if p["number"] == n]
    if not found:
        fail(f"GraphQL: Could not resolve to a PullRequest with the number of {n}.")
    out(gh_pr(found[0]))
    sys.exit(0)
if a[:1] == ["api"]:
    _pos = positional()
    _path = (_pos[0] if _pos else "").lstrip("/")
    _route, _, _query = _path.partition("?")
    _method = (flag("-X", "--method") or "GET").upper()
    if _method == "GET":
        _m = re.fullmatch(r"repos/o/r/issues/(\d+)/parent", _route)
        if _m:
            up = S.get("parents", {}).get(_m.group(1))
            if not up:
                fail("HTTP 404: Not Found (parent)")
            out(obj(up))
            sys.exit(0)
        _m = re.fullmatch(r"repos/o/r/issues/(\d+)/sub_issues", _route)
        if _m:
            if int(_m.group(1)) in S.get("fail_subs", []):
                fail("HTTP 502: Server Error (sub_issues)")
            out([obj(m) for m in S.get("subs", {}).get(_m.group(1), [])])
            sys.exit(0)
        if _route == "repos/o/r/issues":
            q = dict(x.partition("=")[::2] for x in _query.split("&") if x)
            st, label = q.get("state", "open"), q.get("labels")
            found = [obj(int(k)) for k in sorted(S["issues"], key=int)]
            found = [o for o in found if (st == "all" or o["state"] == st)
                     and (not label or label in [l["name"] for l in o["labels"]])]
            out(found)
            sys.exit(0)
        _m = re.fullmatch(r"repos/o/r/pulls/(\d+)", _route)
        if _m:
            found = [p for p in prs() if p["number"] == int(_m.group(1))]
            if not found:
                fail("HTTP 404: Not Found (pull)")
            out(rest_pr(found[0]))
            sys.exit(0)
        if _route == "repos/o/r/pulls":
            q = dict(x.partition("=")[::2] for x in _query.split("&") if x)
            head = q.get("head", "").split(":")[-1] or None
            st = q.get("state", "open")
            out([rest_pr(p) for p in prs() if (head is None or p["head"] == head)
                 and (st == "all" or (st == "open") == (p["state"] == "OPEN"))])
            sys.exit(0)
'''
ANCHOR = 'if a[:2] == ["issue", "view"]:'
assert pl.FAKE_GH.count(ANCHOR) == 1, "test setup: the fake GitHub of test_plan_links_recorded changed shape"
FAKE_GH = pl.FAKE_GH.replace(ANCHOR, TREE + "\n\n" + ANCHOR, 1)


def criterion(files, k=1):
    """One acceptance criterion of a story, changing these files."""
    return {"text": f"Criterion {k}.", "source": PARENT, "words": "the owner's words", "files": list(files)}


def plan(files):
    """A story's plan that passed its check, whose one criterion changes these files."""
    h = {"kind": "user_story", "summary": "A story.", "user_story": "A story.",
         "acceptance_criteria": [criterion(files)], "non_functional": [], "tests": {}, "test_changes": {},
         "links": {"blocked_by": [], "blocks": [], "relates_to": []}}
    return {"role": "planner", "stage": None, "handback": h, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/1", "run_id": "1"}


def review():
    """A plan review that approved the plan and passed its check."""
    return {"role": "reviewer", "stage": "plan", "handback": {"verdict": "approve", "summary": "Graded.", "blockers": [],
            "resolved": []}, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/2", "run_id": "2"}


def worker():
    """A worker's record that passed its check: its build started and finished."""
    return {"role": "worker", "stage": None, "handback": {"summary": "Built it."}, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/3", "run_id": "3"}


def split(assigned):
    """The parent's approved split: one story per issue, each with its assigned files."""
    stories = [{"title": f"Story {n}", "user_story": f"Story {n}.", "acceptance_criteria": [criterion(fs)],
                "non_functional": [], "depends_on": []} for n, fs in assigned.items()]
    h = {"kind": "feature", "summary": "A feature.", "feature": "A feature.", "stories": stories,
         "links": {"blocked_by": [], "blocks": [], "relates_to": []}}
    return {"role": "planner", "stage": None, "handback": h, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/9", "run_id": "9"}


class Tree:
    """A fake GitHub holding parent #700 and stories #701 to #703, and Dokima's commands."""

    def __init__(self, tmp, assigned=None, autopilot=True):
        self.dir = str(tmp)
        bin_dir = os.path.join(self.dir, "bin")
        os.makedirs(bin_dir)
        gh = os.path.join(bin_dir, "gh")
        open(gh, "w").write(f"#!{sys.executable}\nBOT_LOGIN = {pl.BOT!r}\nOWNER_LOGIN = {pl.OWNER!r}\n" + FAKE_GH)
        os.chmod(gh, 0o755)
        labels = ["autopilot"] if autopilot else []
        issues = {str(n): {"title": f"Story {n}", "labels": list(labels), "comments": [],
                           "body": f"<!-- dokima-card -->\n<!-- /dokima-card -->\n\nStory {n} of #{P}."} for n in (A, B, C)}
        issues[str(P)] = {"title": "The feature", "labels": list(labels), "comments": [], "body": "The owner's ask."}
        self.state = {"issues": issues, "deps": {}, "fail": [], "writes": [], "prs": [],
                      "parents": {str(n): P for n in (A, B, C)}, "subs": {str(P): [A, B, C]}}
        self.save()
        self.remote = os.path.join(self.dir, "logs.git")
        subprocess.run(["git", "init", "-q", "--bare", self.remote], check=True)
        self.env = {**os.environ, "PATH": bin_dir + os.pathsep + os.environ.get("PATH", ""), "FAKE_GH_DIR": self.dir,
                    "GITHUB_REPOSITORY": "o/r", "REPO": "o/r", "OWNERS": pl.OWNER, "GH_TOKEN": "fake",
                    "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "3", "DOKIMA_LOGS_REMOTE": self.remote}
        for k in ("DOKIMA_BOARD", "ISSUE_NUMBER", "PACK"):
            self.env.pop(k, None)
        self.post(P, split(assigned or {A: [SHARED], B: [OWN_B], C: [OWN_A]}))

    def save(self):
        """Write the fake GitHub's state to its file."""
        json.dump(self.state, open(os.path.join(self.dir, "state.json"), "w"), indent=1)

    def load(self):
        """Read the fake GitHub's state back, as the commands left it."""
        self.state = json.load(open(os.path.join(self.dir, "state.json")))
        return self.state

    def post(self, n, rec):
        """Put a record on #n as agent.yml does: a comment and a logs file."""
        s = self.load()
        comments = s["issues"][str(n)]["comments"]
        comments.append(pl.record_comment(rec, len(comments) + 1))
        self.save()
        record_seed.seed(n, [rec], self.remote)

    def planned(self, n, files):
        """#n's own plan changes these files and its review approved it."""
        self.post(n, plan(files))
        self.post(n, review())

    def building(self, n, files):
        """#n's plan changes these files, a worker built it, and its pull request is open."""
        self.planned(n, files)
        self.post(n, worker())
        s = self.load()
        s["prs"].append({"number": n + 100, "head": f"try/issue-{n}", "state": "OPEN"})
        self.save()

    def merged(self, n):
        """#n's pull request merged, which closed #n."""
        s = self.load()
        for p in s["prs"]:
            if p["head"] == f"try/issue-{n}":
                p["state"] = "MERGED"
        s["issues"][str(n)]["state"] = "closed"
        self.save()

    def fail_subs(self, n):
        """Every read of #n's sub-issues fails, as GitHub does when it errs."""
        s = self.load()
        s["fail_subs"] = [n]
        self.save()

    def next(self, n, rec):
        """Run `agent next n OUT` on a record; returns (last line, OUT/comment.md, OUT)."""
        out = os.path.join(self.dir, f"out{len(os.listdir(self.dir))}")
        os.makedirs(out)
        json.dump(rec, open(os.path.join(out, "record.json"), "w"))
        p = subprocess.run([sys.executable, "-m", "dokima.agent", "next", str(n), out], cwd=ROOT, env=self.env,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, f"test setup: `agent next` crashed: {p.stderr[-2000:]}"
        path = os.path.join(out, "comment.md")
        return (p.stdout.strip().splitlines() or [""])[-1], open(path).read() if os.path.exists(path) else "", out

    def approve(self, n, files):
        """Run `next` on #n's plan changing these files, then on its approval; returns the latter.

        The plan review's record is posted after, as agent.yml posts it."""
        rec = plan(files)
        self.post(n, rec)
        step, _, _ = self.next(n, rec)
        assert step == "start reviewer plan", f"test setup: #{n}'s plan did not go to its review, the river said {step!r}"
        said = self.next(n, review())
        self.post(n, review())
        return said

    def pack(self, n, role, stage=""):
        """Run `agent pack n ROLE STAGE DIR`, as agent.yml does; returns (exit code, stderr)."""
        dest = os.path.join(self.dir, f"pack{len(os.listdir(self.dir))}")
        p = subprocess.run([sys.executable, "-m", "dokima.agent", "pack", str(n), role, stage, dest], cwd=ROOT,
                           env=self.env, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stderr

    def closed(self, n):
        """Run `python3 -m dokima.agent closed n`, what autopilot.yml runs once #n closes; returns its output."""
        p = subprocess.run([sys.executable, "-m", "dokima.agent", "closed", str(n)], cwd=ROOT, env=self.env,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, f"test setup: `agent closed` crashed: {p.stderr[-2000:]}"
        return p.stdout

    def dispatches(self, n, role=None):
        """The stages signalled to start on #n, as client_payload fields."""
        out = []
        for w in self.load()["writes"]:
            f = w.get("fields") or {}
            if w["op"] == "dispatch" and f.get("client_payload[issue]") == str(n) \
                    and (role is None or f.get("client_payload[role]") == role):
                out.append(f)
        return out

    def comments(self, n):
        """The comments on #n that are not records."""
        return [c["body"].strip() for c in self.load()["issues"][str(n)]["comments"] if agent.MARK not in c["body"]]


def next_line(comment):
    """The card's Next line."""
    return next((l for l in comment.splitlines() if l.startswith("**Next:**")), "")


def assert_waits(t, n, holder, said, crit, case):
    """#n's approval started no build, and its Next line names the holder of the turn."""
    step, comment, out = said
    assert not step.startswith("start"), f"{crit} ({case}): #{n}'s build started while #{holder} holds the turn: {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), \
        f"{crit} ({case}): the Autopilot line that starts #{n}'s worker was still written"
    assert t.dispatches(n, "worker") == [], f"{crit} ({case}): #{n}'s worker was signalled to start"
    nxt = next_line(comment)
    assert f"#{holder}" in nxt, f"{crit} ({case}): #{n}'s Next line does not name #{holder}, whose turn it waits for: {nxt!r}"
    assert "@" not in nxt, f"{crit} ({case}): #{n}'s Next line mentions someone while it only waits its turn: {nxt!r}"


def assert_builds(said, crit, case):
    """The approval on autopilot started the worker, with its Autopilot line."""
    step, _, out = said
    assert step == "start worker", f"{crit} ({case}): the worker should start, the river said {step!r}"
    assert os.path.exists(os.path.join(out, "autopilot.md")), f"{crit} ({case}): the worker's Autopilot line is missing"


# 668.1 ---------------------------------------------------------------------------------------------------------------

def test_a_story_sharing_a_code_file_builds_only_after_the_other_story_merges(tmp_path, record_property):
    """A story waits while another story builds a shared code file, then goes on.

    #701 is building `dokima/shared.py`; #702's approved plan changes it too. On autopilot the approval starts no
    worker and the card's Next line names #701, mentioning no one; the owner's `/work` builds no pack for the worker,
    and says #701. Once #701's pull request merges and #701 closes, autopilot's close run starts #702 again (its
    planner, so no plan goes stale), and `/work` builds the pack. Beside it, normal cases: #703 shares the file but its
    build never started, so it holds no turn; an issue with no parent builds as usual; and when GitHub cannot list the
    parent's stories nothing builds and the card quotes GitHub's error. Proves 668.1."""
    record_property("proves", "668.1")
    crit = "668.1"
    t = Tree(tmp_path / "turn")
    t.building(A, [SHARED, OWN_A])
    assert_waits(t, B, A, t.approve(B, [SHARED, OWN_B]), crit, "autopilot")
    code, err = t.pack(B, "worker")
    assert code != 0, f"{crit} (/work): the worker's pack was built while #{A} holds the turn on {SHARED}"
    assert f"#{A}" in err.strip().splitlines()[-1], \
        f"{crit} (/work): the reason the build did not start does not name #{A}: {err[-600:]!r}"

    t.merged(A)
    t.closed(A)
    assert t.dispatches(B, "planner"), f"{crit} (merged): #{B} did not go on by itself after #{A}'s pull request merged"
    assert t.dispatches(B, "worker") == [], f"{crit} (merged): #{B}'s old plan was built instead of planned again"
    code, err = t.pack(B, "worker")
    assert code == 0, f"{crit} (merged): `/work` still refused #{B}'s build after #{A} merged: {err[-600:]!r}"

    t = Tree(tmp_path / "not-started")
    t.planned(C, [SHARED])
    assert_builds(t.approve(B, [SHARED]), crit, f"#{C} shares the file but never started building")

    h = pl.Hub(tmp_path / "no-parent", autopilot=True)
    h.post(pl.plan(pl.links()))
    step, _, _ = h.next(pl.review())
    assert step == "start worker", f"{crit} (no parent): an issue that is no story should build as usual, not {step!r}"

    t = Tree(tmp_path / "unreadable")
    t.building(A, [SHARED])
    t.fail_subs(P)
    step, comment, out = t.approve(B, [SHARED])
    assert not step.startswith("start"), f"{crit} (unreadable): #{B} built though GitHub could not list its siblings"
    assert t.dispatches(B, "worker") == [], f"{crit} (unreadable): #{B}'s worker was signalled to start"
    assert ERROR in comment, f"{crit} (unreadable): the card does not quote GitHub's error: {comment[-800:]!r}"


# 668.2 ---------------------------------------------------------------------------------------------------------------

def test_planning_and_plan_review_never_wait_on_another_story(tmp_path, record_property):
    """Planning and plan review go on while another story holds the turn on shared files.

    #701 is building `dokima/shared.py`, and #702's plan changes it too. The planner's and the plan reviewer's packs
    for #702 build as usual (`/plan` and `/review`), and #702's plan goes to its review by itself. To show the clash is
    real, the same plan's approval then waits for #701 and builds nothing. Proves 668.2."""
    record_property("proves", "668.2")
    crit = "668.2"
    t = Tree(tmp_path)
    t.building(A, [SHARED])
    code, err = t.pack(B, "planner")
    assert code == 0, f"{crit}: the planner's pack for #{B} failed while #{A} holds the turn: {err[-600:]!r}"
    rec = plan([SHARED])
    t.post(B, rec)
    code, err = t.pack(B, "reviewer", "plan")
    assert code == 0, f"{crit}: the plan reviewer's pack for #{B} failed while #{A} holds the turn: {err[-600:]!r}"
    step, _, _ = t.next(B, rec)
    assert step == "start reviewer plan", f"{crit}: #{B}'s plan did not go to its review by itself: {step!r}"
    said = t.next(B, review())
    assert not said[0].startswith("start"), \
        f"{crit} (setup): #{B}'s build was not held, so this test cannot show that only the build waits: {said[0]!r}"


# 668.3 ---------------------------------------------------------------------------------------------------------------

def test_a_shared_markdown_file_never_makes_a_build_wait(tmp_path, record_property):
    """Two stories sharing only a markdown file build without waiting for each other.

    #701 is building `dokima/a_only.py` and `rules/flow.md`; #702's plan changes `dokima/b_only.py` and the same
    markdown file. On autopilot its approval starts the worker. Beside it, the same story also sharing a code file
    with #701 waits. Proves 668.3."""
    record_property("proves", "668.3")
    crit = "668.3"
    t = Tree(tmp_path / "markdown")
    t.building(A, [OWN_A, DOC])
    assert_builds(t.approve(B, [OWN_B, DOC]), crit, "only a markdown file is shared")

    t = Tree(tmp_path / "code")
    t.building(A, [OWN_A, DOC, SHARED])
    assert_waits(t, B, A, t.approve(B, [OWN_B, DOC, SHARED]), crit, "a code file is shared too")


# 668.5 ---------------------------------------------------------------------------------------------------------------

def test_a_story_whose_plan_adds_files_is_checked_again_before_it_builds(tmp_path, record_property):
    """A story whose own plan adds a file another story is building waits for it.

    The parent's split assigned #702 only `dokima/b_only.py` and #701 `dokima/shared.py`; #701 is building. #702's own
    plan adds `dokima/shared.py`, so its approval waits for #701. Beside it, #702's plan keeping to its assigned file
    builds. Its split never gave it that file. Proves 668.5."""
    record_property("proves", "668.5")
    crit = "668.5"
    assigned = {A: [SHARED], B: [OWN_B], C: [OWN_A]}
    t = Tree(tmp_path / "added", assigned)
    t.building(A, [SHARED])
    assert_waits(t, B, A, t.approve(B, [OWN_B, SHARED]), crit, f"#{B}'s plan added {SHARED}")

    t = Tree(tmp_path / "kept", assigned)
    t.building(A, [SHARED])
    assert_builds(t.approve(B, [OWN_B]), crit, f"#{B}'s plan kept to its assigned file")

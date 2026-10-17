"""The merge gate tests the pull request with main's newest commit, then the owner approves.

Today a code review's approval stops for the owner at once, and autopilot merges once the head's required checks
pass, even when the branch misses main's newest commit, so the code that lands was never tested as it lands. The
merge gate runs right after a code review approves: it brings the branch up to date with main when it is behind
(GitHub's Update branch), then waits for main's required checks on that combined head. Green, the owner is asked to
approve (on autopilot, Dokima merges that head); any check red, the worker starts again on the pull request.

These tests run `python3 -m dokima.agent next 57 OUT` in-process on a passed code review that approves pull request
#60, built for issue #57 from `try/issue-57`, against a fake GitHub in memory that stands in for `dokima.agent_github.gh`:

- the issue, its records (plan, plan review, the owner's `/work`, the worker's record) and its `autopilot` label,
  through `gh issue view` and `gh api repos/o/r/issues/57`;
- the pull request through `gh pr list`, `gh pr view` (any `--json` fields) and `gh api repos/o/r/pulls/60`, its
  files (`dokima/x.py`), and GraphQL's merge state;
- main's branch rule, requiring `all tests` and `Acceptance criteria`, through `gh api repos/o/r/branches/main`;
- a branch behind main: `gh api repos/o/r/compare/main...X` answers `behind_by` 1, the REST pull request's
  `mergeable_state` is "behind" and GraphQL's `mergeStateStatus` is BEHIND; Update branch (`gh pr update-branch 60`
  or `gh api -X PUT repos/o/r/pulls/60/update-branch`) moves the head to a new commit that holds main's newest one;
  GitHub may refuse Update branch with its words for a clash with main, when a test says so;
- the check runs and commit statuses on each head commit, as each test gives them;
- merging (`gh pr merge` or `gh api -X PUT repos/o/r/pulls/60/merge`), recorded with the head it was pinned to.

Time is faked: `time.sleep` only moves a clock `time.time` and `time.monotonic` read, so a 45-minute wait costs
nothing. What the run decided is what `next` printed (the workflow reads it as NEXT), the Next line it wrote on the
record (OUT/comment.md) and where it put the card (OUT/board.txt).
"""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent  # noqa: E402
from dokima import agent_github  # noqa: E402

REPO = "o/r"
N = "57"
PR = 60
OWNER = "owner-person"
OLD = "a1" * 20  # the head the code review approved
NEW = "b2" * 20  # the head after Update branch: the pull request combined with main's newest commit
REQUIRED = ["all tests", "Acceptance criteria"]
APPROVE_ASK = re.compile(r"\bapprove\b", re.I)
# A Next line that tells the owner to merge, the way today's does ("Merge the pull request").
MERGE_ASK = re.compile(r"\bmerge (the|this) pull request\b|\bmerge it\b", re.I)
UPDATE_REFUSED = "HTTP 422: merge conflict between base and head"

STORY = {"kind": "user_story", "title": "t", "summary": "s", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/57", "files": ["dokima/x.py"]}],
         "non_functional": [], "tests": {"57.1": ["tests/test_x.py::test_a"]}}
PLANNER = {"role": "planner", "stage": None, "run_id": "1", "run": "https://github.com/o/r/actions/runs/1",
           "models": ["claude-opus-5-5"], "handback": STORY, "check": {"passed": True, "problems": []}}
APPROVAL = {"verdict": "approve", "summary": "Every criterion is proven.", "raises": [], "answers": [],
            "previous_step": {"did": ["Checked the work."], "decided": [], "open": []}}
PLAN_REVIEW = {"role": "reviewer", "stage": "plan", "run_id": "2", "run": "https://github.com/o/r/actions/runs/2",
               "models": ["claude-opus-5-5"], "handback": APPROVAL, "check": {"passed": True, "problems": []}}
WORKER = {"role": "worker", "stage": None, "run_id": "3", "run": "https://github.com/o/r/actions/runs/3",
          "models": ["claude-opus-5-5"], "handback": {"summary": "Built it.", "criteria": {"57.1": "done"},
                                                      "evidence": "pytest -q: 3 passed"},
          "check": {"passed": True, "problems": []}}
CODE_REVIEW = {"role": "reviewer", "stage": "pr", "run_id": "4", "run": "https://github.com/o/r/actions/runs/4",
               "models": ["claude-opus-5-5"], "handback": APPROVAL, "check": {"passed": True, "problems": []}}


def run(name, sha, conclusion="success", status="completed"):
    """One check run as GitHub's check-runs API gives it."""
    return {"name": name, "head_sha": sha, "status": status, "conclusion": conclusion if status == "completed" else None}


def green(sha):
    """Every check main requires, passed on the commit."""
    return [run(c, sha) for c in REQUIRED]


def red(sha, failing="all tests"):
    """Every check main requires on the commit, with one of them failed."""
    return [run(c, sha, "failure" if c == failing else "success") for c in REQUIRED]


def running(sha):
    """Every check main requires on the commit, still running."""
    return [run(c, sha, status="in_progress") for c in REQUIRED]


class FakeGitHub:
    """GitHub for one `next` run after the code review approved #60."""

    def __init__(self, checks, behind=False, autopilot=False, refuse_update=False):
        """Sets up #60 at its old head, with the checks each head commit carries.

        checks maps a head commit to its check runs; behind says the branch misses main's newest commit, and
        refuse_update makes GitHub refuse Update branch, as on a clash with main."""
        self.checks, self.behind, self.head, self.refuse_update = checks, behind, OLD, refuse_update
        self.labels = [{"name": "autopilot"}] if autopilot else []
        self.merges, self.updates, self.comments, self.calls = [], [], [], []
        self.clock = 1_800_000_000.0
        at = iter(f"2026-10-13T10:{m:02d}:00Z" for m in range(0, 60, 5))
        posted = lambda who, body: {"author": {"login": who}, "body": body, "createdAt": next(at)}
        self.issue = {"number": int(N), "title": "Fix it", "body": "Fix it.", "labels": self.labels,
                      "comments": [posted(OWNER, "/plan"), posted(agent.BOT, agent.render(PLANNER)),
                                   posted(agent.BOT, agent.render(PLAN_REVIEW)), posted(OWNER, "/work"),
                                   posted(agent.BOT, agent.render(WORKER))]}

    def sleep(self, seconds):
        """Moves the fake clock on instead of waiting."""
        self.clock += max(float(seconds), 1.0)

    def pr(self):
        """The pull request as GitHub's REST and `gh pr view` give it."""
        return {"number": PR, "state": "open", "title": "Fix it", "headRefOid": self.head,
                "headRefName": f"try/issue-{N}", "baseRefName": "main", "comments": [], "reviews": [],
                "mergeStateStatus": "BEHIND" if self.behind else "BLOCKED", "isDraft": False, "draft": False,
                "mergeable_state": "behind" if self.behind else "blocked", "mergeable": "MERGEABLE",
                "head": {"sha": self.head, "ref": f"try/issue-{N}"}, "base": {"ref": "main"},
                "files": [{"path": "dokima/x.py"}], "labels": self.labels}

    def gh(self, *args):
        """Answers one `gh` call the way GitHub would."""
        a = [str(x) for x in args]
        self.calls.append(a)
        if len(self.calls) > 2000:
            raise RuntimeError("the run kept calling GitHub: over 2000 calls in one decision")
        flag = lambda *names: next((a[i + 1] for i, x in enumerate(a[:-1]) if x in names), None)
        path = next((x.split("?")[0].strip("/") for x in a[1:] if x.startswith(("repos/", "/repos/"))), "")
        method = (flag("-X", "--method") or "").upper()
        if path == "rate_limit" or "rate_limit" in a:
            return json.dumps({"resources": {"core": {"remaining": 4000, "reset": 0}, "graphql": {"remaining": 4000, "reset": 0}}})
        if a[:2] == ["issue", "view"]:
            return self.shaped(a, self.issue)
        if a[:2] == ["issue", "comment"] or a[:2] == ["pr", "comment"]:
            self.comments.append(a)
            return ""
        if a[:2] == ["pr", "list"]:
            return self.shaped(a, [{"number": PR, "headRefName": f"try/issue-{N}", "state": "OPEN"}])
        if a[:2] == ["pr", "view"]:
            return self.shaped(a, self.pr())
        if a[:2] == ["pr", "update-branch"] or (path == f"repos/o/r/pulls/{PR}/update-branch" and method == "PUT"):
            return self.update()
        if a[:2] == ["pr", "merge"]:
            return self.merge(flag("--match-head-commit"))
        if path == f"repos/o/r/pulls/{PR}/merge" and method == "PUT":
            fields = dict(x.split("=", 1) for x in a if "=" in x and not x.startswith("repos"))
            return self.merge(fields.get("sha"))
        if "graphql" in a:
            st = {"state": "MERGED" if self.merges else "OPEN", "isInMergeQueue": False, "autoMergeRequest": None,
                  "reviewDecision": None, "mergeStateStatus": "BEHIND" if self.behind else "CLEAN",
                  "headRefOid": self.head}
            return json.dumps({"data": {"repository": {"pullRequest": st}}})
        if path == f"repos/o/r/issues/{N}":
            return self.shaped(a, {"number": int(N), "id": 5700, "state": "open", "labels": self.labels})
        if path.startswith("repos/o/r/actions/variables/"):
            raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr="HTTP 404: Not Found")
        if path == f"repos/o/r/pulls/{PR}/files":
            return json.dumps([{"filename": "dokima/x.py"}])
        if path == f"repos/o/r/pulls/{PR}/comments":
            return "[]"
        if path == f"repos/o/r/pulls/{PR}":
            return self.shaped(a, self.pr())
        if path == "repos/o/r":
            # The repo itself names its default branch, as GitHub does (#787).
            return json.dumps({"full_name": "o/r", "default_branch": "main"})
        if path == "repos/o/r/branches/main":
            inner = {"strict": False, "contexts": REQUIRED, "checks": [{"context": c, "app_id": None} for c in REQUIRED]}
            return json.dumps({"name": "main", "protection": {"enabled": True, "required_status_checks": inner}})
        if path.startswith("repos/o/r/compare/"):
            b = 1 if self.behind else 0
            return json.dumps({"status": "diverged" if b else "ahead", "ahead_by": 1, "behind_by": b, "total_commits": 1})
        m = re.fullmatch(r"repos/o/r/commits/([^/]+)/(check-runs|status)", path)
        if m:
            sha = self.head if m.group(1) in (f"try/issue-{N}", "HEAD") else m.group(1)
            if m.group(2) == "status":
                return json.dumps({"state": "success", "statuses": []})
            runs = self.checks.get(sha, [])
            return json.dumps({"total_count": len(runs), "check_runs": runs})
        return self.shaped(a, [])

    def update(self):
        """GitHub's Update branch: the head becomes a commit holding main's newest one."""
        self.updates.append(self.head)
        if self.refuse_update:
            raise subprocess.CalledProcessError(1, ["gh"], output="", stderr=UPDATE_REFUSED + "\n")
        if self.behind:
            self.behind, self.head = False, NEW
        return json.dumps({"message": "Updating pull request branch.", "url": f"https://github.com/o/r/pull/{PR}"})

    def merge(self, pinned):
        """Merges #60, remembering the head the merge was pinned to."""
        self.merges.append({"head": self.head, "pinned": pinned})
        return ""

    @staticmethod
    def shaped(args, value):
        """The JSON answer, cut to the fields or simple path the call asks for."""
        fields = next((args[i + 1] for i, x in enumerate(args[:-1]) if x == "--json"), None)
        if fields and isinstance(value, dict):
            value = {k: value.get(k) for k in fields.split(",")}
        path = next((args[i + 1] for i, x in enumerate(args[:-1]) if x in ("--jq", "-q")), None)
        if path and path.startswith("."):
            for key in [k for k in re.split(r"[.\[\]]", path) if k]:
                if isinstance(value, list):
                    value = value[int(key)] if key.isdigit() and int(key) < len(value) else None
                else:
                    value = value.get(key) if isinstance(value, dict) else None
            return "" if value is None else (json.dumps(value) if isinstance(value, (dict, list)) else f"{value}\n")
        return json.dumps(value)


def decide(tmp_path, monkeypatch, capsys, fake, name="out"):
    """Runs `next 57` on the code review's approval against the fake.

    Returns what it printed, its Next line, where it put the card and any error that escaped it."""
    out = tmp_path / name
    out.mkdir()
    json.dump(CODE_REVIEW, open(out / "record.json", "w"))
    (out / "comment.md").write_text(agent.render(CODE_REVIEW))
    monkeypatch.setattr(agent_github, "gh", fake.gh)
    monkeypatch.setattr(time, "sleep", fake.sleep)
    monkeypatch.setattr(time, "time", lambda: fake.clock)
    monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("OWNERS", OWNER)
    escaped = None
    capsys.readouterr()
    try:
        agent.main(["dokima.agent", "next", N, str(out)])
    except Exception as e:  # noqa: BLE001 - any escape is reported by the test that asked
        escaped = f"{type(e).__name__}: {(getattr(e, 'stderr', None) or str(e)).strip()}"
    finally:
        monkeypatch.undo()
    text = (out / "comment.md").read_text()
    line = next((l for l in text.splitlines() if l.startswith("**Next:**")), "")
    board = (out / "board.txt").read_text().strip() if (out / "board.txt").exists() else ""
    return capsys.readouterr().out.strip().splitlines()[-1:] or [""], line, board, escaped


def printed(result):
    """What `next` printed last: what the workflow starts, or stop."""
    return result[0][0].strip()


def test_autopilot_merges_only_the_head_tested_with_the_newest_main(record_property, tmp_path, monkeypatch, capsys):
    """Autopilot merges only once all tests passed with main's newest commit.

    Proves 596.1.
    The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
    date, and merge only the new head, once every required check passed there; today it merges the old head, never
    tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
    one whose new head's checks never finish within the wait must not merge, one GitHub refuses to bring up to date
    must not merge and must stop for the owner with GitHub's reason, `/autopilot start`'s merge (`automerge`) must not
    take the old head of a branch behind main either, and one already up to date and green must merge as it is, so
    the gate is not just "never merge"."""
    record_property("proves", "596.1")
    fake = FakeGitHub({OLD: green(OLD), NEW: green(NEW)}, behind=True, autopilot=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "behind-green")
    assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
    assert fake.merges and all(m["head"] == NEW for m in fake.merges), \
        (f"596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: "
         f"merges={fake.merges}, branch updates asked at {fake.updates}; it should merge {NEW[:7]} only")
    assert all(m["pinned"] in (None, NEW) for m in fake.merges), \
        f"596.1: the merge was pinned to a head other than the tested one: {fake.merges}"

    fake = FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True, autopilot=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "behind-red")
    assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
    assert fake.merges == [], \
        f"596.1: autopilot merged though All tests failed on the pull request combined with main: {fake.merges}"

    fake = FakeGitHub({OLD: green(OLD)}, behind=True, autopilot=True, refuse_update=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "update-refused")
    assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
    assert fake.merges == [], f"596.1: autopilot merged a branch GitHub could not bring up to date with main: {fake.merges}"
    assert printed(r) == "stop" and f"@{OWNER}" in r[1] and "merge conflict between base and head" in r[1], \
        (f"596.1: GitHub refused to bring the branch up to date, and the run did not stop for the owner with "
         f"GitHub's reason: printed {printed(r)!r}, Next {r[1]!r}")

    fake = FakeGitHub({OLD: green(OLD)}, behind=True, autopilot=True)
    monkeypatch.setattr(agent_github, "gh", fake.gh)
    monkeypatch.setattr(time, "sleep", fake.sleep)
    monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    try:
        agent.automerge(REPO, N)  # `/autopilot start` merges an approved pull request this way
    except Exception as e:  # noqa: BLE001 - a crash is reported with its criterion
        raise AssertionError(f"596.1: `/autopilot start`'s merge crashed on a branch behind main: {e}") from e
    finally:
        monkeypatch.undo()
    assert OLD not in [m["head"] for m in fake.merges], \
        f"596.1: `/autopilot start`'s merge took a head never tested with main's newest commit: {fake.merges}"

    fake = FakeGitHub({OLD: green(OLD)}, behind=False, autopilot=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "current-green")
    assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
    assert [m["head"] for m in fake.merges] == [OLD], \
        f"596.1: an up-to-date pull request with every check green did not merge once at its head: {fake.merges}"

    fake = FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True, autopilot=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "behind-running")
    assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
    assert fake.merges == [], f"596.1: autopilot merged while tests still ran on the combined head: {fake.merges}"


def test_a_failing_test_at_the_merge_gate_starts_the_worker_again(record_property, tmp_path, monkeypatch, capsys):
    """A test failing at the merge gate starts the worker again on that pull request.

    Proves 596.2.
    The code review approved #60, off autopilot, and All tests failed on its head, which holds main's newest commit.
    `next` must print `start worker`, so the workflow starts the worker, and not stop for the owner; today it
    stops and asks the owner to merge. Beside it, the same pull request with every check green must not start the
    worker, so the gate sends back only on a failure. On autopilot, a branch behind main, green on its old head, whose
    Acceptance criteria check fails once brought up to date, must start the worker too, and merge nothing."""
    record_property("proves", "596.2")
    fake = FakeGitHub({OLD: red(OLD)})
    r = decide(tmp_path, monkeypatch, capsys, fake, "red")
    assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
    assert printed(r) == "start worker", \
        f"596.2: All tests failed at the merge gate, and the run printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})"
    fake = FakeGitHub({OLD: green(OLD)})
    r = decide(tmp_path, monkeypatch, capsys, fake, "green")
    assert printed(r) != "start worker", f"596.2: the worker started again though every check passed at the gate ({r[1]!r})"



    fake = FakeGitHub({OLD: green(OLD), NEW: red(NEW, "Acceptance criteria")}, behind=True, autopilot=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "combined-red")
    assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
    assert printed(r) == "start worker", \
        (f"596.2: Acceptance criteria failed on the pull request combined with main, on autopilot, and the run "
         f"printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})")
    assert fake.merges == [], f"596.2: autopilot merged a pull request whose test failed at the merge gate: {fake.merges}"


def test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed(record_property, tmp_path, monkeypatch, capsys):
    """The owner is asked to approve only once the merge gate passed.

    Proves 596.3.
    Off autopilot, the code review approved #60. With every check green on the head combined with main, the run must
    stop for the owner with a Next line asking them to approve, and show Needs you; today its Next line only says to
    merge. With the checks on the combined head still running past the wait, its Next line must neither ask them to
    approve nor tell them to merge. With All tests failed on the combined head, it must neither ask them to approve,
    tell them to merge, nor show Needs you."""
    record_property("proves", "596.3")
    fake = FakeGitHub({OLD: green(OLD), NEW: green(NEW)}, behind=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "passed")
    assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
    assert printed(r) == "stop" and APPROVE_ASK.search(r[1]) and f"@{OWNER}" in r[1], \
        f"596.3: the merge gate passed, and the owner was not asked to approve: printed {printed(r)!r}, Next {r[1]!r}"
    assert r[2].endswith("needs"), f"596.3: the merge gate passed, and the card does not show Needs you: {r[2]!r}"
    assert fake.updates, "596.3: the owner was asked to approve a branch never brought up to date with main"

    fake = FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "running")
    assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
    assert not APPROVE_ASK.search(r[1]) and not MERGE_ASK.search(r[1]), \
        f"596.3: the owner was asked to approve or merge while tests still ran on the combined head: Next {r[1]!r}"

    fake = FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True)
    r = decide(tmp_path, monkeypatch, capsys, fake, "failed")
    assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
    assert not APPROVE_ASK.search(r[1]) and not MERGE_ASK.search(r[1]) and not r[2].endswith("needs"), \
        f"596.3: the owner was asked to approve or merge though the merge gate failed: Next {r[1]!r}, card {r[2]!r}"
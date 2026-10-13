"""Worker check, code review, merge gate: each starts only after the one before passed (#597).

The order: the worker's end check runs the plan's tests, the code review starts only once that check passed, and the
merge gate runs the tests on the combined code. Nothing runs beside anything else: no test run races the code review,
and no merge is tried while tests still run.

Two machines play it, both on issue #57 and its pull request #60 in repo o/r, nothing leaving the machine:

- The worker's run is the real `agent.yml` job, run step by step on test_start.py's machine with a stand-in worker.
  The planner committed `tests/test_x.py::test_a`, the plan's one test, which needs `x.py` to return 1. A git hook on
  the local origin notes every push, so the run's GitHub calls and its pushes are seen in the order they happened.
- The river after it is a fake GitHub (`River`, built on test_merge_gate.py's) that starts the two test workflows,
  `full-suite.yml` and `acceptance-criteria.yml`, the way GitHub would: for each pull request event it reads the
  workflow's own `on:` and each job's `if:` (with test_start.py's expression reader) against the pull request as it
  stands then (its head, draft flag and labels). A job that runs is a test run: it starts at that moment on that
  head and ends 20 minutes later; a job whose `if:` is false leaves a skipped check, as GitHub does. The pull request
  starts as the worker's run opened it, events follow the calls Dokima makes (`gh pr ready`, its `--undo`, Update
  branch, labels, GitHub's draft mutations), and `python3 -m dokima.agent next 57 OUT` decides what follows the code
  review, in-process, on a fake clock.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_merge_gate as mg  # noqa: E402
import test_start as ts  # noqa: E402

TEST_WORKFLOWS = ("full-suite.yml", "acceptance-criteria.yml")
DEFAULT_TYPES = ("opened", "synchronize", "reopened")  # GitHub's pull_request_target types when none are listed
TEST_TIME = 20 * 60  # how long a test run takes, in seconds
REVIEW = 10 * 60  # how long the code review runs
MID = "c3" * 20  # the head after main moved during the review and the branch was brought up to date
SECOND = "d4" * 20  # the head of the worker's second build

PLANNER_TEST = ('import os, sys\n'
                'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n\n'
                'def test_a():\n    """x.value() is 1."""\n    import x\n    assert x.value() == 1\n')

WORKER = r'''#!/usr/bin/env python3
"""A stand-in worker: builds x.py (build) or rewrites the planner's test to pass (cheat), then hands back."""
import json, os
mode = open(os.environ["FAKE_WORKER_MODE"]).read().strip()
if mode == "cheat":
    open("tests/test_x.py", "w").write('def test_a():\n    """Always passes."""\n')
else:
    open("x.py", "w").write("def value():\n    return 1\n")
json.dump({"summary": "Built it.", "criteria": {"57.1": "x.py, value()"}, "evidence": "pytest -q: 1 passed",
           "raises": [], "answers": []}, open(os.path.join(os.environ["OUT"], "work.json"), "w"))
logs = os.path.join(os.environ["HOME"], ".claude", "projects", "p")
os.makedirs(logs, exist_ok=True)
open(os.path.join(logs, "s.jsonl"), "w").write(json.dumps({"message": {"model": os.environ["MODEL"], "role": "assistant", "content": "Done."}}) + "\n")
open(os.environ["FAKE_CLAUDE_MARK"], "w").write("started")
print(json.dumps({"num_turns": 1, "duration_ms": 1000, "usage": {}}))
'''


class WorkerRun(ts.Machine):
    """One whole worker run of `agent.yml` on #57, its worker building (build) or cheating (cheat).

    With pr_open the issue already has its pull request #60, as on a second build."""

    def __init__(self, tmp, mode, pr_open=False):
        super().__init__(tmp, ts.STORY_APPROVED, try_branch=True, options={"pr_open": True} if pr_open else None)
        t, src = self.tmp, f"{self.tmp}/src"
        open(f"{t}/bin/claude", "w").write(WORKER.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
        open(f"{t}/mode", "w").write(mode)
        open(f"{src}/tests/test_x.py", "w").write(PLANNER_TEST)
        ts.sh(src, "git", "add", "-A")
        ts.sh(src, "git", "commit", "-qm", "the planner's test")
        ts.sh(src, "git", "push", "-q", "origin", f"try/issue-{ts.N}")
        # Every push to the issue's branch is noted among the run's GitHub calls, in order.
        hook = f"{t}/origin.git/hooks/post-receive"
        open(hook, "w").write(f"#!/bin/sh\nwhile read old new ref; do [ \"$ref\" = refs/heads/try/issue-{ts.N} ] && "
                              f"echo '[\"<push>\"]' >> '{t}/gh/calls.jsonl'; done; exit 0\n")
        os.chmod(hook, 0o755)
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": "worker", "stage": "", "issue": ts.N}}))
        ctx = {"inputs": ts.Ctx(role="worker", stage="", issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42",
                                run_attempt="1", server_url="https://github.com", repository="o/r",
                                token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        wf = ts.workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))

    def base_env(self, event_name):
        """The machine's environment, with the stand-in worker told its mode."""
        return {**super().base_env(event_name), "FAKE_WORKER_MODE": f"{self.tmp}/mode"}

    def review_started(self):
        """True when the run sent the signal that starts the code review."""
        return any("client_payload[role]=reviewer" in c for c in self.dispatches())


class River(mg.FakeGitHub):
    """GitHub after the worker's run: #60, its test runs and the merges asked for.

    `outcome` maps a head to how its test runs end (success unless named); `draft` and `labels` are the pull
    request's, as the worker's run left them."""

    def __init__(self, outcome=None, autopilot=False, draft=False, labels=(), test_time=TEST_TIME):
        super().__init__({}, autopilot=autopilot)
        self.outcome, self.draft, self.pr_labels, self.test_time = outcome or {}, draft, list(labels), test_time
        self.runs, self.events, self.unsafe, self.opened = [], [], [], True

    def pr(self):
        """The pull request, with its draft flag and labels as they stand."""
        return {**super().pr(), "isDraft": self.draft, "draft": self.draft,
                "labels": self.labels + [{"name": n} for n in self.pr_labels]}

    @staticmethod
    def shaped(args, value):
        """The answer cut as `gh` cuts it, booleans printed as `gh -q` prints them."""
        out = mg.FakeGitHub.shaped(args, value)
        return {"True\n": "true\n", "False\n": "false\n"}.get(out, out)

    def payload(self, action):
        """The pull_request_target event GitHub sends for the pull request as it stands."""
        pr = {"number": mg.PR, "draft": self.draft, "state": "open", "labels": [{"name": n} for n in self.pr_labels],
              "head": {"sha": self.head, "ref": f"try/issue-{mg.N}", "repo": {"full_name": mg.REPO}},
              "base": {"ref": "main", "repo": {"full_name": mg.REPO}}, "merged": False}
        return {"action": action, "number": mg.PR, "pull_request": pr}

    def event(self, action):
        """GitHub's part on one pull request event: the test jobs it starts or skips."""
        self.events.append((self.clock, action, self.head))
        event = self.payload(action)
        github = ts.Ctx(event_name="pull_request_target", event=event, repository=mg.REPO, sha=self.head,
                        actor="dokima-runtime[bot]", ref="refs/heads/main")
        for name in TEST_WORKFLOWS:
            wf = ts.workflow(name)
            on = wf.get("on") or wf.get(True) or {}
            if "pull_request_target" not in on:
                continue
            spec = on.get("pull_request_target") or {}
            types = spec.get("types") if isinstance(spec, dict) and spec.get("types") else DEFAULT_TYPES
            if isinstance(types, str):
                types = [types]
            if action not in types:
                continue
            results = {}
            jobs = wf["jobs"]
            while len(results) < len(jobs):
                for job, spec_ in jobs.items():
                    needs = spec_.get("needs") or []
                    needs = [needs] if isinstance(needs, str) else needs
                    if job in results or any(n not in results for n in needs):
                        continue
                    status = {"failed": any(results[n] == "failure" for n in needs),
                              "success": all(results[n] == "success" for n in needs)}
                    ctx = {"github": github, "inputs": ts.Ctx(), "vars": ts.Ctx(), "secrets": ts.Ctx(),
                           "matrix": ts.Ctx(name="57.1 · a", id="57.1", tests="tests/test_x.py::test_a"),
                           "needs": ts.Ctx({n: {"result": results[n],
                                                "outputs": {"matrix": '[{"id": "57.1"}]'} if results[n] == "success" else {}}
                                            for n in needs})}
                    runs = ts.evaluate(ts.condition(spec_.get("if")), ctx, status)
                    check = ts.fill(spec_.get("name") or job, ctx, status)
                    end = self.outcome.get(self.head, "success")
                    self.runs.append({"workflow": name, "name": check, "head_sha": self.head, "event": action,
                                      "start": self.clock, "end": self.clock + (self.test_time if runs else 0),
                                      "conclusion": end if runs else "skipped", "ran": bool(runs)})
                    results[job] = ("failure" if end == "failure" else "success") if runs else "skipped"

    def started(self, since, until, head=None):
        """The test runs that started from `since` up to `until`, on `head` when given."""
        return [r for r in self.runs if r["ran"] and since <= r["start"] <= until and head in (None, r["head_sha"])]

    def check_runs(self, sha):
        """The check runs on a commit, as GitHub gives them at this moment."""
        out = []
        for r in self.runs:
            if r["head_sha"] != sha:
                continue
            done = self.clock >= r["end"]
            out.append({"name": r["name"], "head_sha": sha, "status": "completed" if done else "in_progress",
                        "conclusion": r["conclusion"] if done else None})
        return out

    def push(self, sha):
        """A push to the pull request's branch: a new head, and GitHub's synchronize event."""
        self.head = sha
        self.event("synchronize")

    def gh(self, *args):
        """Answers one `gh` call, turning draft, label and branch changes into the events GitHub sends."""
        a = [str(x) for x in args]
        path = next((x.split("?")[0].strip("/") for x in a[1:] if x.startswith(("repos/", "/repos/"))), "")
        m = re.fullmatch(r"repos/o/r/commits/([^/]+)/check-runs", path)
        if m:
            self.calls.append(a)
            sha = self.head if m.group(1) in (f"try/issue-{mg.N}", "HEAD") else m.group(1)
            runs = self.check_runs(sha)
            return json.dumps({"total_count": len(runs), "check_runs": runs})
        if a[:2] == ["pr", "ready"]:
            self.calls.append(a)
            undo = "--undo" in a
            if self.draft != undo:
                self.draft = undo
                self.event("converted_to_draft" if undo else "ready_for_review")
            return ""
        if a[:2] == ["pr", "edit"]:
            self.calls.append(a)
            for i, x in enumerate(a[:-1]):
                if x == "--add-label" and a[i + 1] not in self.pr_labels:
                    self.pr_labels.append(a[i + 1])
                    self.event("labeled")
                if x == "--remove-label" and a[i + 1] in self.pr_labels:
                    self.pr_labels.remove(a[i + 1])
                    self.event("unlabeled")
            return ""
        if "graphql" in a and any("markPullRequestReadyForReview" in x or "convertPullRequestToDraft" in x for x in a):
            self.calls.append(a)
            undo = any("convertPullRequestToDraft" in x for x in a)
            if self.draft != undo:
                self.draft = undo
                self.event("converted_to_draft" if undo else "ready_for_review")
            return json.dumps({"data": {}})
        return super().gh(*args)

    def update(self):
        """GitHub's Update branch: a new head holding main's newest commit, then synchronize."""
        old = self.head
        out = super().update()
        if self.head != old:
            self.event("synchronize")
        return out

    def merge(self, pinned):
        """Merges #60, noted as unsafe unless every required check finished and passed."""
        sha = pinned or self.head
        runs = self.check_runs(sha)
        for name in mg.REQUIRED:
            mine = [r for r in runs if r["name"] == name]
            if not mine or any(r["status"] != "completed" for r in mine) or \
                    not any(r["conclusion"] == "success" for r in mine) or \
                    any(r["conclusion"] not in ("success", "skipped") for r in mine):
                self.unsafe.append({"head": sha[:7], "check": name, "runs": mine})
        return super().merge(pinned)


def replay(river, run, head):
    """Plays the worker's run on the river, in the order it happened.

    A push to the issue's branch moves the head to `head` (synchronize, once #60 is open); `gh pr create` opens #60
    with the draft flag and labels it gives; draft and label calls change #60 as GitHub would."""
    for c in run.calls():
        if c == ["<push>"]:
            if river.opened:
                river.push(head)
            else:
                river.head = head
        elif c[:2] == ["pr", "create"]:
            river.draft = "--draft" in c or "-d" in c
            river.pr_labels = [l for i, x in enumerate(c[:-1]) if x in ("--label", "-l") for l in c[i + 1].split(",")]
            river.opened = True
            river.event("opened")
        elif river.opened and (c[:2] in (["pr", "ready"], ["pr", "edit"]) or ("graphql" in c and any(
                "markPullRequestReadyForReview" in x or "convertPullRequestToDraft" in x for x in c))):
            river.gh(*c)


def decide(tmp_path, monkeypatch, capsys, river, name):
    """Runs `next 57` on the code review's approval: what it printed, its Next line."""
    r = mg.decide(tmp_path, monkeypatch, capsys, river, name)
    assert r[3] is None, f"test setup: deciding what follows the code review failed: {r[3]}"
    return mg.printed(r), r[1]


def test_code_review_starts_only_after_the_workers_test_check_passed(record_property, tmp_path):
    """The code review starts only once the plan's own tests passed on the worker's code.

    Proves 597.1.
    Runs the worker's whole `agent.yml` run on #57, whose planner committed `tests/test_x.py::test_a`. A worker that
    builds `x.py` must start the code review, so the review is not simply never started. A worker that skips the work
    and rewrites the planner's test so it passes must not: today its end check runs on the edited test and passes,
    and the review starts though the planner's own test, put back by the fence, still fails."""
    record_property("proves", "597.1")
    build = WorkerRun(tmp_path / "build", "build")
    assert build.review_started(), \
        f"597.1: the worker built what the plan asked, and the code review did not start:\n{build.tail()}"
    cheat = WorkerRun(tmp_path / "cheat", "cheat")
    assert not cheat.review_started(), \
        ("597.1: the code review started though the planner's own test still fails on the worker's code: the worker "
         "had edited that test, and its check ran on the edited copy")


def test_no_test_run_starts_while_the_code_review_runs(record_property, tmp_path, monkeypatch, capsys):
    """No test runs while the code review runs; the merge gate then runs them.

    Proves 597.2.
    The worker's real run opens #60, then the code review runs ten minutes; halfway, main moves and the branch is
    brought up to date. No test run may start in that time; today both test workflows start when #60 opens and again
    on the update. Once the review approves, the merge gate must start the tests on the head, so they are moved, not
    dropped. The gate's tests fail, the worker's real run builds again and pushes, and the second code review runs:
    no test may start from that push until it approved, and that gate must test the new head."""
    record_property("proves", "597.2")
    river = River({MID: "failure"})
    river.opened = False
    replay(river, WorkerRun(tmp_path / "first", "build"), mg.OLD)
    assert river.opened, "test setup: the worker's run did not open #60"
    t0 = river.clock
    river.clock += REVIEW // 2
    river.push(MID)  # main moved and the branch was brought up to date with it
    river.clock = t0 + REVIEW
    early = river.started(t0, river.clock)
    assert not early, (f"597.2: tests started on the pull request while its code review ran: "
                       f"{sorted({(r['workflow'], r['name'], r['event']) for r in early})}")
    approved = river.clock
    step, _ = decide(tmp_path, monkeypatch, capsys, river, "first-gate")
    assert river.started(approved, river.clock, MID), \
        f"597.2: after the code review approved, the merge gate started no test run on its head; events: {river.events}"
    assert step == "start worker", f"597.2: the merge gate's tests failed, and the run printed {step!r}, not 'start worker'"

    river.clock += 60
    pushed = river.clock
    replay(river, WorkerRun(tmp_path / "second", "build", pr_open=True), SECOND)
    assert river.head == SECOND, "test setup: the worker's second build pushed nothing"
    river.clock = pushed + REVIEW
    early = river.started(pushed, river.clock)
    assert not early, (f"597.2: the worker's second build started tests while its code review ran: "
                       f"{sorted({(r['workflow'], r['name'], r['event']) for r in early})}")
    approved = river.clock
    decide(tmp_path, monkeypatch, capsys, river, "second-gate")
    assert river.started(approved, river.clock, SECOND), \
        f"597.2: after the second code review approved, the merge gate started no test run on {SECOND[:7]}"


def test_no_merge_is_tried_while_tests_still_run(record_property, tmp_path, monkeypatch, capsys):
    """Autopilot tries a merge only once every required test finished and passed on the head.

    Proves 597.3.
    On autopilot the code review approves #60 and `next` runs the merge gate. A merge counts as tried while tests
    still run when a required check on the merged head is still running, or has no finished run that passed. First
    the worker's real run opens #60 and nothing else happens: autopilot must merge, safely, so the gate is not just
    "never merge". Then #60 is a draft whose required checks were only skipped: today the gate counts skipped as
    passed and merges code no test ran on. Then tests that fail, and tests that outlast the gate's wait: no merge."""
    record_property("proves", "597.3")
    river = River(autopilot=True)
    river.opened = False
    replay(river, WorkerRun(tmp_path / "opens", "build"), mg.OLD)
    river.clock += REVIEW
    decide(tmp_path, monkeypatch, capsys, river, "fresh")
    assert not river.unsafe, f"597.3: a merge was tried while tests still ran on the pull request: {river.unsafe}"
    assert river.merges, "597.3: every test passed at the merge gate, and autopilot never merged"

    river = River(autopilot=True, draft=True)
    river.runs = [{"workflow": "", "name": n, "head_sha": mg.OLD, "event": "opened", "start": river.clock,
                   "end": river.clock, "conclusion": "skipped", "ran": False} for n in mg.REQUIRED]
    river.clock += REVIEW
    decide(tmp_path, monkeypatch, capsys, river, "skipped")
    assert not river.unsafe, \
        f"597.3: autopilot merged a head whose required checks were only skipped, before any test ran: {river.unsafe}"

    river = River({mg.OLD: "failure"}, autopilot=True)
    river.event("opened")
    river.clock += REVIEW
    decide(tmp_path, monkeypatch, capsys, river, "failed")
    assert not river.merges, f"597.3: autopilot merged though a test failed at the merge gate: {river.merges}"

    river = River(autopilot=True, test_time=60 * 60)
    river.event("opened")
    river.clock += REVIEW
    decide(tmp_path, monkeypatch, capsys, river, "slow")
    assert not river.unsafe, f"597.3: a merge was tried while tests outlasting the gate's wait still ran: {river.unsafe}"

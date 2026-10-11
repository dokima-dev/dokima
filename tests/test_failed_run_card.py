"""A failed run puts its card in Needs you, in the column of the stage that ran (#132).

Two layers. The first runs the agent workflow (.github/workflows/agent.yml) step by step the way GitHub runs it, using
the machine from tests/test_start.py, with a board set (vars.DOKIMA_BOARD), so its "Move the card on the board" step
really runs `python3 -m dokima.agent board`. The fake `gh` also answers the board's GraphQL calls and records every
field it sets, so each test reads back where the card ended up: its Status column and whether it shows Needs you. The
fake Claude Code can be told to crash, and the fake `gh` can be told to fail every read of the issue once the agent
has started, which is how the run's own "Decide what follows" step fails in real life (GitHub answering 502).

The second layer runs `python3 -m dokima.agent board N OUT` alone, the way the board step does, with a fake `gh` on
PATH: when the run left no decision behind (no board.txt, or nothing at all in OUT), the card must still land in the
column of the stage the run was for, with Needs you.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import test_start as T  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Answers the board's GraphQL calls and records every field set or cleared; fails reads of the issue after the agent.
GH_EXTRA = r'''
if os.path.exists(os.path.join(d, "fail-after-agent")) and os.path.exists(os.environ.get("FAKE_CLAUDE_MARK", "/nonexistent")) \
        and a[:2] in (["issue", "view"], ["pr", "view"]):
    sys.stderr.write("HTTP 502: Bad Gateway (https://api.github.com/graphql)\n")
    sys.exit(1)
if a[:2] == ["api", "graphql"]:
    vals = [a[i + 1] for i in range(len(a) - 1) if a[i] in ("-f", "-F")]
    q = next(v[6:] for v in vals if v.startswith("query="))
    v = dict(x.split("=", 1) for x in vals if not x.startswith("query="))
    if "organization" in q:
        data = {"organization": {"projectV2": {"id": "P", "fields": {"nodes": [
            {"id": "S", "name": "Status", "options": [{"id": "s-" + o, "name": o} for o in ("Backlog", "Plan", "Work", "Review", "Done")]},
            {"id": "A", "name": "Action", "options": [{"id": "needs", "name": "Needs you"}]}]}}}}
    elif q.startswith("query") and "node(" in q:
        # The card's current pill, read since #210: none, as GitHub answers for a card without one.
        data = {"node": {"fieldValueByName": None, "fieldValues": {"nodes": []}}}
    elif q.startswith("query"):
        kind = "issue" if "issue(" in q else "pullRequest"
        iid = f"{kind}-{v.get('n')}"
        # Labels and open pull requests, read since #210: none, so nothing here is on autopilot.
        data = {"repository": {kind: {"id": iid, "projectItems": {"nodes": [{"id": iid, "project": {"id": "P"}}]},
                                      "labels": {"nodes": []}}, "pullRequests": {"nodes": []}}}
    else:
        name = "set" if "updateProjectV2ItemFieldValue" in q else "clear" if "clearProjectV2ItemFieldValue" in q else "other"
        open(os.path.join(d, "board.jsonl"), "a").write(json.dumps({"op": name, **v}) + "\n")
        data = {}
    print(json.dumps({"data": data}))
    sys.exit(0)
'''

CLAUDE_CRASH = '''import sys
if os.path.exists(os.path.join(os.environ["FAKE_GH_DIR"], "crash")):
    sys.stderr.write("API Error: 529 Overloaded\\n")
    sys.exit(1)
'''

BLOCK = {"previous_step": {"did": ["Planned one criterion."], "decided": [], "open": []},
         "stage": "plan", "round": 1, "verdict": "block", "summary": "One test proves nothing.",
         "raises": [{"kind": "blocker", "to": "planner", "label": "57.1", "text": "It asserts nothing.", "evidence": "test_a has no assert."}],
         "asks": [{"ask": "Fix it.", "source": "https://github.com/o/r/issues/57", "criterion": "57.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")]}


def board_state(path):
    """Where each card ended up, read from the recorded field changes: {item: (Status column, shows Needs you)}."""
    status, action = {}, {}
    if os.path.exists(path):
        for line in open(path):
            c = json.loads(line)
            target = status if c.get("f") == "S" else action if c.get("f") == "A" else None
            if target is None:
                continue
            target[c["i"]] = c.get("o") if c["op"] == "set" else None
    return {i: ((status.get(i) or "")[2:] or None, action.get(i) == "needs") for i in set(status) | set(action)}


class BoardRun(T.Machine):
    """One run of agent.yml with a board set; the agent may crash, and reading the issue may fail once it has run."""

    def __init__(self, tmp, role, stage, comments, try_branch=False, crash=False, decide_fails=False, review=None):
        super().__init__(tmp, comments, try_branch)
        t = self.tmp
        if crash:
            open(f"{t}/gh/crash", "w").close()
        if decide_fails:
            open(f"{t}/gh/fail-after-agent", "w").close()
        if review is not None:
            json.dump(review, open(f"{t}/review.json", "w"))
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": role, "stage": stage, "issue": T.N}}))
        ctx = {"inputs": T.Ctx(role=role, stage=stage, issue=T.N),
               "github": T.Ctx(event_name="workflow_dispatch", actor=T.OWNER, event=T.Ctx(), run_id="42", run_attempt="1",
                               server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": T.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": T.Ctx(DOKIMA_APP_ID="1", DOKIMA_BOARD="o/1"), "needs": T.Ctx()}
        wf = T.workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))

    def card(self):
        """The issue's card: (Status column, shows Needs you), or None when the run never touched it."""
        return board_state(f"{self.tmp}/gh/board.jsonl").get(f"issue-{T.N}")


def fakes(monkeypatch):
    """Give the test machine a gh that also plays the board and a Claude Code that can crash."""
    monkeypatch.setattr(T, "FAKE_GH", T.FAKE_GH.replace('if a[:2] == ["issue", "view"]:', GH_EXTRA + 'if a[:2] == ["issue", "view"]:', 1))
    monkeypatch.setattr(T, "FAKE_CLAUDE", T.FAKE_CLAUDE.replace('write("started")\n', 'write("started")\n' + CLAUDE_CRASH, 1))


def test_a_failed_run_lands_in_its_stage_column_with_needs_you(record_property, tmp_path, monkeypatch):
    """A planner, plan review or worker run that fails leaves its card in that stage's column showing Needs you.

    Runs the whole agent workflow with a board set. Failures: the planner's and the worker's agent crash (code then
    rejects the missing hand-back), each once with the rest of the run working and once with the run's own "Decide
    what follows" step failing too because GitHub answers 502; and a plan review whose agent hands back a good approval
    but whose deciding step fails. Each must end with the issue's card in Plan or Work as the stage says, showing Needs
    you. Beside them the good case: a plan review that blocks hands back to the planner, so the card sits in Plan with
    the Needs you pill cleared."""
    record_property("proves", "132.1")
    fakes(monkeypatch)
    cases = [("planner crashed", "planner", "", T.STORY_PLANNED[:1], False, True, False, None, ("Plan", True)),
             ("worker crashed", "worker", "", T.STORY_APPROVED, True, True, False, None, ("Work", True)),
             ("planner crashed and deciding what follows failed", "planner", "", T.STORY_PLANNED[:1], False, True, True, None, ("Plan", True)),
             ("worker crashed and deciding what follows failed", "worker", "", T.STORY_APPROVED, True, True, True, None, ("Work", True)),
             ("plan review passed but deciding what follows failed", "reviewer", "plan", T.STORY_PLANNED, True, False, True, None, ("Plan", True)),
             ("plan review blocked and the planner starts again", "reviewer", "plan", T.STORY_PLANNED, True, False, False, BLOCK, ("Plan", False))]
    for i, (name, role, stage, comments, branch, crash, decide, review, want) in enumerate(cases):
        r = BoardRun(tmp_path / str(i), role, stage, comments, try_branch=branch, crash=crash, decide_fails=decide, review=review)
        got = r.card()
        assert got == want, (f"132.1: {name}: the card ended at {got} (column, Needs you), expected {want}; "
                             f"the run stopped at '{r.failed_step}':\n{r.tail()}")


def run_board_step(tmp_path, files, role, stage, pr=""):
    """Run `python3 -m dokima.agent board 57 OUT` with OUT holding only `files`, as the workflow's board step does."""
    out, gh = tmp_path / "out", tmp_path / "gh"
    out.mkdir(parents=True)
    gh.mkdir()
    for name, text in files.items():
        (out / name).write_text(text)
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    fake = T.FAKE_GH.replace('if a[:2] == ["issue", "view"]:', GH_EXTRA + 'if a[:2] == ["issue", "view"]:', 1)
    if pr:
        fake = fake.replace('print("" if (flag("-q") or flag("--jq")) else "[]")', f'print("{pr}" if (flag("-q") or flag("--jq")) else "[]")', 1)
    (bin_ / "gh").write_text(fake.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    os.chmod(bin_ / "gh", 0o755)
    env = {**os.environ, "PATH": f"{bin_}:{os.environ['PATH']}", "FAKE_GH_DIR": str(gh), "PYTHONPATH": ROOT,
           "GITHUB_REPOSITORY": "o/r", "DOKIMA_BOARD": "o/1", "N": T.N, "OUT": str(out), "ROLE": role, "STAGE": stage}
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "board", T.N, str(out)], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=60)
    return p, board_state(str(gh / "board.jsonl"))


def rejected_review():
    """The record of a code review whose hand-back code rejected, as the workflow writes it."""
    return {"role": "reviewer", "stage": "pr", "run_id": "42", "models": ["claude-opus-5-5"], "handback": {},
            "check": {"passed": False, "problems": ["review.json is missing"]}}


def test_a_failed_code_review_marks_the_issue_and_its_pr_even_when_deciding_failed(record_property, tmp_path):
    """A failed code review whose deciding step failed still puts the issue and its open PR in Review with Needs you.

    Runs the board step alone on what such a run leaves behind: its rejected record and no decision (no board.txt),
    with pull request #60 open. Both cards must end in Review showing Needs you. A run that decided what follows is
    placed from GitHub's state since #331, never from its own board.txt; tests/test_board_state.py proves that case."""
    record_property("proves", "132.1")
    p, cards = run_board_step(tmp_path / "failed", {"record.json": json.dumps(rejected_review())}, "reviewer", "pr", pr="60")
    want = {f"issue-{T.N}": ("Review", True), "pullRequest-60": ("Review", True)}
    assert cards == want, (f"132.1: a failed code review that could not decide what follows left the cards at {cards}, "
                           f"expected {want}:\n{p.stdout}{p.stderr}")


def test_a_run_that_left_nothing_behind_still_marks_its_card(record_property, tmp_path):
    """A run that left no record and no decision still puts its card in its own stage's column with Needs you.

    Runs the board step alone with an empty hand-back folder, as when even writing the record failed, once for a worker
    and once for a code review. The card must end in Work, then Review, showing Needs you, and the step must exit 0 so
    the run's own failure, not the board, is what the owner reads."""
    record_property("proves", "132.2")
    for role, stage, column in (("worker", "", "Work"), ("reviewer", "pr", "Review")):
        p, cards = run_board_step(tmp_path / role, {}, role, stage)
        got = cards.get(f"issue-{T.N}")
        assert got == (column, True), (f"132.2: a {role} run that left nothing behind put the card at {got}, "
                                       f"expected ({column!r}, Needs you):\n{p.stdout}{p.stderr}")
        assert p.returncode == 0, f"132.2: the board step exited {p.returncode} for a {role} run that left nothing behind:\n{p.stderr}"

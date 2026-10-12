"""A run that dies unrecorded still gets a record, and autopilot restarts its stage (#514).

#433's planner run died at 00:30 UTC: every step after the agent failed (the call counter fixed in #513 broke `gh`),
so its live card kept saying "agent working since 00:21", the board showed nothing for the owner, and
`/autopilot start` answered "already on autopilot, no stage started" because the live card read as a run going on.

The first two tests run every job of the agent workflow (.github/workflows/agent.yml) the way GitHub runs them, in the
order their `needs` allow, on the machine from tests/test_start.py with the board fakes of
tests/test_failed_run_card.py. In the broken run, every `gh` call made inside the `run` job after the agent started
fails with exit 127, the way the broken counter failed them; jobs that run afterwards are on fresh machines, so their
calls work. The good run is the same plan review with nothing broken.

The third test runs the command listener (.github/workflows/commands.yml) on `/autopilot start`, with the fake GitHub
of tests/test_autopilot_close.py, which says a run is still going only when the test lists it as running.
"""
import json
import os
import re

import pytest

import test_autopilot_close as tac
import test_failed_run_card as frc
import test_start as ts
from dokima import agent
from test_start import N, OWNER, Ctx, condition, evaluate

ISSUE = int(N)
RUN_URL = "https://github.com/o/r/actions/runs/42"
LABEL = "autopilot"

# Every gh call made inside the run job once the agent has started fails, as the broken counter made them fail (#513).
BREAK = '''a = sys.argv[1:]
if os.path.exists(os.environ.get("FAKE_CLAUDE_MARK", "/nonexistent")) and "/jobs/run/" in os.getcwd() + "/" \\
        and os.path.exists(os.path.join(os.environ["FAKE_GH_DIR"], "broken")):
    sys.stderr.write("gh: line 1: /tmp/ghcount/gh: No such file or directory\\n")
    sys.exit(127)
'''


class WholeRun(ts.Machine):
    """Runs every job of agent.yml for one plan review of #57, with a board.

    With `broken`, gh fails inside the run job once the agent has started."""

    def __init__(self, tmp, broken):
        super().__init__(tmp, ts.STORY_PLANNED, try_branch=True)
        t = self.tmp
        fake = ts.FAKE_GH.replace("a = sys.argv[1:]\n", BREAK, 1)
        fake = fake.replace('if a[:2] == ["issue", "view"]:', frc.GH_EXTRA + 'if a[:2] == ["issue", "view"]:', 1)
        assert "/jobs/run/" in fake and "board.jsonl" in fake, "test setup: could not teach the fake gh to break and play the board"
        open(f"{t}/bin/gh", "w").write(fake.replace("#!/usr/bin/env python3", f"#!{ts.sys.executable}"))
        if broken:
            open(f"{t}/gh/broken", "w").close()
        # A blocking plan review: when its record is posted the planner starts again and nothing waits on the owner.
        json.dump(frc.BLOCK, open(f"{t}/review.json", "w"))
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": "reviewer", "stage": "plan", "issue": N}}))
        github = Ctx(event_name="workflow_dispatch", actor=OWNER, event=Ctx(), run_id="42", run_attempt="1",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        wf = ts.workflow("agent.yml")
        jobs = wf["jobs"]
        self.results, outputs = {}, {}
        while len(self.results) < len(jobs):
            progressed = False
            for name, job in jobs.items():
                needs = job.get("needs") or []
                needs = [needs] if isinstance(needs, str) else needs
                if name in self.results or any(n not in self.results for n in needs):
                    continue
                progressed = True
                res = [self.results[n] for n in needs]
                status = {"failed": "failure" in res, "success": all(r == "success" for r in res)}
                ctx = {"github": github, "inputs": Ctx(role="reviewer", stage="plan", issue=N),
                       "vars": Ctx(DOKIMA_APP_ID="1", DOKIMA_BOARD="o/1"),
                       "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                       "needs": Ctx({n: {"result": self.results[n], "outputs": outputs.get(n, {})} for n in needs})}
                if not evaluate(condition(job.get("if")), ctx, status):
                    self.results[name] = "skipped"
                    continue
                tmp_of = f"{t}/" if name == "run" else f"{t}/jobs/{name}/tmp/"
                self.results[name], outputs[name] = self.run_job(
                    name, job, ctx, "workflow_dispatch",
                    [("/tmp/", tmp_of), ("/home/runner/", f"{t}/home/" if name == "run" else f"{t}/jobs/{name}/home/")],
                    wf.get("defaults"))
            assert progressed, "test setup: the jobs of agent.yml wait on each other"

    def on_issue(self):
        """Every comment the bot wrote on #57 during the run, as it stands now."""
        return [c["versions"][-1] for c in self.comments() if c["kind"] == "issue" and c["number"] == ISSUE
                and c["author"] == agent.BOT]

    def records(self):
        """Every record on #57 now, as code reads records."""
        return agent.records([{"author": {"login": agent.BOT}, "body": b} for b in self.on_issue()])

    def card(self):
        """The issue's board card: (Status column, shows Needs you), or None when nothing touched it."""
        return frc.board_state(f"{self.tmp}/gh/board.jsonl").get(f"issue-{N}")


@pytest.fixture(scope="module")
def runs(tmp_path_factory, request):
    """The broken plan review and the good one, each run once for the module."""
    mp = pytest.MonkeyPatch()
    request.addfinalizer(mp.undo)
    frc.fakes(mp)
    return {"broken": WholeRun(tmp_path_factory.mktemp("broken"), True),
            "good": WholeRun(tmp_path_factory.mktemp("good"), False)}


def test_a_run_that_dies_before_its_record_gets_a_failed_record_linking_the_run(record_property, runs):
    """A run that dies before posting its record gets a failed record linking the run.

    Proves 514.1.
    Runs a plan review whose every GitHub call fails once the agent has started, so the run cannot post its record.
    Afterwards no comment on the issue may still be a live card short of a record (it said "agent working"), and the
    issue must hold a record, read by code as records are read, whose check failed and whose text links the run.
    Beside it, the same plan review with nothing broken must leave exactly its own passing record and no other."""
    record_property("proves", "514.1")
    r = runs["broken"]
    tail = "\n".join(r.log[-6:])[-4000:]
    live = [b for b in r.on_issue() if agent.LIVE in b and agent.MARK not in b]
    assert not live, ("514.1: the run died before its record, and its live card still stands, never turned into a "
                      f"record:\n{live[0]}\n--- last steps ---\n{tail}")
    failed = [(rec, b) for b in r.on_issue() for rec in agent.records([{"author": {"login": agent.BOT}, "body": b}])
              if not (rec.get("check") or {}).get("passed")]
    assert failed, ("514.1: the run died before its record, and the issue holds no failed record; its bot comments:\n"
                    f"{r.on_issue()}\n--- last steps ---\n{tail}")
    assert any(RUN_URL in b for _, b in failed), \
        f"514.1: the failed record does not link the run ({RUN_URL}):\n{failed[0][1]}"

    g = runs["good"]
    recs = g.records()
    assert len(recs) == 1 and recs[0].get("role") == "reviewer" and (recs[0].get("check") or {}).get("passed"), \
        (f"514.1: a plan review that posted its own record must leave exactly that one passing record; found "
         f"{[(x.get('role'), (x.get('check') or {}).get('passed')) for x in recs]}\n" + "\n".join(g.log[-4:])[-3000:])


def test_a_run_that_dies_before_its_record_shows_needs_you(record_property, runs):
    """A run that dies before posting its record leaves its issue's card showing Needs you.

    Proves 514.2.
    The same broken plan review: its card must end in Plan with the Needs you pill, though the run's own board step
    could not reach GitHub. Beside it, the good plan review hands back to the planner by itself, so its card sits in
    Plan with no Needs you."""
    record_property("proves", "514.2")
    r, g = runs["broken"], runs["good"]
    assert r.card() == ("Plan", True), (f"514.2: the run died before its record, and the card ended at {r.card()} "
                                        "(column, Needs you), expected ('Plan', True)\n" + "\n".join(r.log[-6:])[-4000:])
    assert g.card() == ("Plan", False), (f"514.2: a plan review that posted its record and restarted the planner left the "
                                         f"card at {g.card()}, expected ('Plan', False)")


def dead_card(role, stage, run, cid, monkeypatch):
    """A live card on #57, drawn as agent.yml draws it while the agent works."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_RUN_ID", str(run))
    return tac.bot_comment("issue", ISSUE, agent.live_card(role, stage, "working"), cid)


def started_signals(m):
    """Every signal that starts agent.yml: (role, stage, issue)."""
    return [(s["payload"].get("role"), s["payload"].get("stage"), s["payload"].get("issue"))
            for s in m.signals() if s["event_type"] == "dokima-next" and s["token"] == "fake-token"]


def test_autopilot_start_restarts_the_stage_whose_run_ended_unrecorded(record_property, tmp_path, monkeypatch):
    """`/autopilot start` restarts the stage whose last run ended with no record.

    Proves 514.3.
    Two issues #57 already on autopilot, each with its run's live card still standing though GitHub says the run has
    completed: a planner run (after the Autopilot line that started it, as on #433) must start the planner once; a plan
    review run (after a plan) must start the plan review once. Neither may say "No stage was started". Beside them, the
    same planner card whose run GitHub says is still going must start nothing, so code that always restarts fails."""
    record_property("proves", "514.3")
    start_line = tac.bot_comment("issue", ISSUE, "Autopilot: switched on, starting plan", 4000)
    cases = (("planner ended", [start_line, dead_card("planner", "", 78, 4001, monkeypatch)], [], [("planner", N)]),
             ("plan review ended", [tac.planned(ISSUE, 4000), dead_card("reviewer", "plan", 79, 4001, monkeypatch)], [],
              [("reviewer:plan", N)]),
             ("planner still going", [start_line, dead_card("planner", "", 78, 4001, monkeypatch)], [78], []))
    for case, seed, running, want in cases:
        m = tac.Repo(tmp_path / re.sub(r"\W", "-", case), {}, {ISSUE: [LABEL]}, seed=seed, running_runs=running)
        m.listen("/autopilot start")
        assert not m.failed, f"514.3 ({case}): the listener failed on /autopilot start:\n{m.tail()}"
        got = [(f"{role}:{stage}" if role == "reviewer" else role, issue) for role, stage, issue in started_signals(m)]
        assert got == want, (f"514.3 ({case}): /autopilot start started {got}, expected {want}; its comments: "
                             f"{m.new_comments(ISSUE)}\n{m.tail()}")
        said = [b for b in m.new_comments(ISSUE) if b.strip().startswith(("Autopilot is", f"#{N} and every issue"))]
        if want:
            assert said and "No stage was started" not in said[0], \
                f"514.3 ({case}): the stage started again, but the switch comment says nothing started: {said}"

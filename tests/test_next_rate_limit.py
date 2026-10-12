"""Deciding what runs next says why GitHub failed, and waits out its rate limit (#417).

agent.yml runs `python3 -m dokima.agent next N OUT` as `NEXT=$(...) || NEXT=stop`, so before #417 a GitHub call that
failed inside it (on 10-10, "GraphQL: API rate limit already exceeded for installation ID ...") became a stop with no
Next line and no word on the issue. These tests run the same `next` command in-process on a passed planner record,
whose decision is to start the plan reviewer, against a fake GitHub that stands in for `dokima.agent.gh`:

- `gh issue view` gives the issue and its comments, `gh pr list` gives no pull requests, and `gh api rate_limit`
  gives GitHub's rate limit answer (`resources.graphql.reset` and `resources.core.reset`, epoch seconds), the one
  call GitHub answers even when the limit has run out.
- A fake clock replaces `time.time`, and `time.sleep` only moves it forward, so a wait of an hour takes no time.
- Every other call fails, the way gh fails (CalledProcessError with GitHub's words on stderr), while the fake clock
  is before the reset of the limit that ran out, or always, or never, as each test says.

What the run decided is what `next` printed (the workflow reads it as NEXT) and the Next line it added to the
record (OUT/comment.md, which the workflow posts on the issue). Where the card lands is what the workflow's board step,
`python3 -m dokima.agent board`, does with what the run left behind, run against a fake board as tests/test_failed_run_card.py
does.
So the fakes reach the code, `next` reads GitHub only through `dokima.agent.gh` and reads the clock and waits only
through `time.time()` and `time.sleep()`.
"""
import json
import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent  # noqa: E402

N = "57"
OWNER = "owner-person"
NOW = 1_800_000_000
GRAPHQL_RESET = NOW + 1500
CORE_RESET = NOW + 300
GRAPHQL_LIMIT = "GraphQL: API rate limit already exceeded for installation ID 168252268"
REST_LIMIT = "API rate limit exceeded for installation ID 168252268. (HTTP 403)"
SERVER_ERROR = "HTTP 502: Server Error (https://api.github.com/repos/o/r/issues/57)"

STORY = {"kind": "user_story", "summary": "s", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/57"}],
         "non_functional": [], "scope": ["x.py"], "out_of_scope": [], "tests": {"57.1": ["tests/test_x.py::test_a"]}}
PLANNER = {"role": "planner", "stage": None, "run_id": "1", "run": "https://github.com/o/r/actions/runs/1",
           "models": ["claude-opus-5-5"], "handback": STORY, "check": {"passed": True, "problems": []}}
APPROVAL = {"verdict": "approve", "summary": "The plan proves every ask.", "raises": [], "answers": [],
            "previous_step": {"did": ["Wrote a plan."], "decided": [], "open": []}}
PLAN_REVIEW = {"role": "reviewer", "stage": "plan", "run_id": "2", "run": "https://github.com/o/r/actions/runs/2",
               "models": ["claude-opus-5-5"], "handback": APPROVAL, "check": {"passed": True, "problems": []}}
ISSUE_READ = ["api", f"repos/o/r/issues/{N}"]
BLOCKED_BY_READ = ["api", f"repos/o/r/issues/{N}/dependencies/blocked_by"]


def every_call(args):
    """Every call GitHub may refuse: all of them."""
    return True


def only(read):
    """GitHub refuses only this read, by its first two words, and answers the rest."""
    return lambda args: [a for a in args if not a.startswith("-")][:2] == read


class FakeGitHub:
    """GitHub for one `next` run: answers its reads, and fails as told."""

    def __init__(self, failure, until, failing=every_call, earlier=(), labels=()):
        """Calls failing picks fail with failure's words while the clock is before until.

        earlier are the records already posted after the planner's, and labels the issue's labels."""
        self.clock = NOW
        self.slept = []
        self.failure = failure
        self.until = until
        self.failing = failing
        self.calls = []
        comments = [{"author": {"login": OWNER}, "body": "/plan", "createdAt": "2026-10-07T10:00:00Z"},
                    {"author": {"login": agent.BOT}, "body": agent.render(PLANNER), "createdAt": "2026-10-07T10:10:00Z"}]
        comments += [{"author": {"login": agent.BOT}, "body": agent.render(r), "createdAt": "2026-10-07T10:20:00Z"}
                     for r in earlier]
        self.labels = [{"name": l} for l in labels]
        self.issue = {"number": int(N), "title": "Stuck issue", "body": "Fix it.", "comments": comments,
                      "labels": self.labels}

    def time(self):
        """The fake clock, in epoch seconds."""
        return self.clock

    def sleep(self, seconds):
        """A wait that only moves the fake clock forward."""
        self.slept.append(seconds)
        self.clock += max(0, seconds)

    def gh(self, *args):
        """Answer one gh call, or refuse it as gh does."""
        args = [str(a) for a in args]
        self.calls.append(args)
        if len(self.calls) > 300:
            raise RuntimeError("the run kept calling GitHub: over 300 calls in one decision")
        if args[:1] == ["api"] and any(a.split("?")[0].strip("/") == "rate_limit" for a in args[1:]):
            limits = {"resources": {"graphql": {"limit": 5000, "remaining": 0 if self.failure == GRAPHQL_LIMIT else 4000,
                                                "reset": GRAPHQL_RESET},
                                    "core": {"limit": 5000, "remaining": 0 if self.failure == REST_LIMIT else 4000,
                                             "reset": CORE_RESET}}}
            limits["rate"] = limits["resources"]["core"]
            return self.shaped(args, limits)
        if self.failure and self.clock < self.until and self.failing(args):
            raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr=f"{self.failure}\n")
        if args[:2] == ["issue", "view"]:
            return self.shaped(args, self.issue)
        if args[:2] == ["pr", "list"]:
            return self.shaped(args, [])
        if args[:1] == ["api"] and any(a.split("?")[0].strip("/") == f"repos/o/r/issues/{N}" for a in args[1:]):
            return self.shaped(args, {"number": int(N), "id": 5700, "state": "open", "labels": self.labels})
        return self.shaped(args, [])

    @staticmethod
    def shaped(args, value):
        """The JSON answer, or the part a simple --jq / -q path asks for."""
        path = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in ("--jq", "-q")), None)
        if path and path.startswith("."):
            for key in [k for k in path.split(".") if k]:
                value = value.get(key) if isinstance(value, dict) else None
            return "" if value is None else (json.dumps(value) if isinstance(value, (dict, list)) else f"{value}\n")
        return json.dumps(value)


def decide(tmp_path, monkeypatch, capsys, failure=None, until=0, name="out", rec=PLANNER, failing=every_call,
           labels=()):
    """Run `next 57` on the record rec, the passed planner's by default, against the fake.

    Returns what it printed, the record's text, the board line, the fake and any GitHub error that escaped it; the
    fake's `autopilot` is the Autopilot line the run left for the workflow to post, empty when none."""
    out = tmp_path / name
    out.mkdir()
    json.dump(rec, open(out / "record.json", "w"))
    (out / "comment.md").write_text(agent.render(rec))
    hub = FakeGitHub(failure, until, failing, labels=labels)
    monkeypatch.setattr(agent, "gh", hub.gh)
    monkeypatch.setattr(time, "time", hub.time)
    monkeypatch.setattr(time, "sleep", hub.sleep)
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("OWNERS", OWNER)
    escaped = None
    capsys.readouterr()
    try:
        agent.main(["dokima.agent", "next", N, str(out)])
    except (subprocess.CalledProcessError, RuntimeError) as e:
        escaped = (getattr(e, "stderr", None) or str(e)).strip()
    finally:
        monkeypatch.undo()
    board = (out / "board.txt").read_text().strip() if (out / "board.txt").exists() else ""
    hub.autopilot = (out / "autopilot.md").read_text().strip() if (out / "autopilot.md").exists() else ""
    return capsys.readouterr().out.strip(), (out / "comment.md").read_text(), board, hub, escaped


def next_lines(text):
    """The Next lines of a record."""
    return [l for l in text.splitlines() if l.startswith("**Next:**")]


def lines_with(text, words):
    """The lines of a record that hold these words."""
    return [l for l in text.splitlines() if words in l]


def test_a_decision_github_refuses_says_so_in_one_line_with_githubs_reason(record_property, tmp_path, monkeypatch, capsys):
    """A refused decision puts one line with GitHub's reason on the record.

    Proves 417.1.
    GitHub answers every call of the run with "HTTP 502: Server Error". The run's record must then hold exactly one
    line carrying GitHub's words, and start no stage: before #417 the error escaped `next`, the record got no line at
    all, and the workflow's `|| NEXT=stop` stopped the river with nothing on the issue. The same run with GitHub
    answering every call must add only its Next line, the reviewer starting, so the line shows only on a failure."""
    record_property("proves", "417.1")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, name="answered")
    assert escaped is None, f"417.1: deciding what runs next failed though GitHub answered every call: {escaped}"
    assert printed == "start reviewer plan", f"417.1: with GitHub answering, the run printed {printed!r}, not 'start reviewer plan'"
    assert text == agent.with_next(agent.render(PLANNER), "**Next:** The reviewer starts now."), \
        f"417.1: with GitHub answering, the record gained more than its Next line:\n{text[len(agent.render(PLANNER)):]}"
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, SERVER_ERROR, until=float("inf"), name="refused")
    said = lines_with(text, SERVER_ERROR)
    assert len(said) == 1, (f"417.1: GitHub refused a call while deciding what runs next, and the record holds "
                            f"{len(said)} lines with GitHub's reason {SERVER_ERROR!r}, not one"
                            f"{' (the error escaped the step: ' + escaped + ')' if escaped else ''}:\n{text[-1200:]}")
    assert not printed.startswith("start"), f"417.1: a stage started though deciding what runs next failed: {printed!r}"


@pytest.mark.parametrize("failure,reset", [(GRAPHQL_LIMIT, GRAPHQL_RESET), (REST_LIMIT, CORE_RESET)],
                         ids=["graphql", "rest"])
def test_a_rate_limited_decision_waits_for_the_reset_and_starts_the_step(record_property, tmp_path, monkeypatch, capsys,
                                                                         failure, reset):
    """A rate-limited step waits for the reset, then starts what it would have.

    Proves 417.2.
    GitHub refuses every call with its rate-limit words until its reset time: the GraphQL limit's reset for the
    GraphQL words, the REST (core) limit's reset for the REST words, which differ. The run must wait on the fake
    clock until that reset, no more than a minute past it, and then start the plan reviewer, with the same Next line
    as a run GitHub answered. A run that never retries, retries before the reset of the limit that ran out, or waits
    on the other limit's reset stops instead."""
    record_property("proves", "417.2")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, failure, until=reset)
    assert escaped is None, f"417.2: the rate-limited decision was never tried again; GitHub's error escaped: {escaped}"
    assert printed == "start reviewer plan", (f"417.2: after GitHub's rate limit reset, the run printed {printed!r}, "
                                              f"not 'start reviewer plan' (it waited {sum(hub.slept)} s for a reset "
                                              f"{reset - NOW} s away)")
    assert reset <= hub.clock <= reset + 60, (f"417.2: the run waited until {hub.clock - NOW} s, not until the "
                                              f"limit's reset at {reset - NOW} s (within a minute)")
    assert next_lines(text) == ["**Next:** The reviewer starts now."], \
        f"417.2: after the wait, the record's Next lines are {next_lines(text)!r}, not the reviewer starting"
    assert board == "Plan none", f"417.2: after the wait, the card is placed {board!r}, not in Plan (the plan review) without Needs you"


def test_a_failure_that_is_not_the_rate_limit_does_not_wait(record_property, tmp_path, monkeypatch, capsys):
    """A failure other than the rate limit is said at once, with no wait.

    Proves 417.2.
    GitHub answers with a server error for the first 30 minutes on the fake clock. The run must not wait for any
    rate-limit reset: it waits less than a minute in all, and says the failure on the record instead."""
    record_property("proves", "417.2")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, SERVER_ERROR, until=NOW + 1800)
    assert sum(hub.slept) < 60, f"417.2: a failure that is not the rate limit waited {sum(hub.slept)} s for a reset"
    assert lines_with(text, SERVER_ERROR), f"417.2: the server error was not said on the record:\n{text[-800:]}"


def board_step(tmp_path, out, failure):
    """Run the workflow's board step on what `next` left in out.

    The step is `python3 -m dokima.agent board 57 OUT`.

    The board step runs right after `next` in agent.yml, in the same hour, so GitHub still refuses reads of the issue
    (`gh issue view`, `gh pr view` and the issue's REST read) with failure's words; the board's own GraphQL calls are
    answered by the fake board of tests/test_failed_run_card.py, which records every field set. Returns the step and
    where the issue's card ended: (Status column, shows Needs you), or None when the step never touched it."""
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    import test_start as T
    from test_failed_run_card import GH_EXTRA, board_state
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gh, bin_ = tmp_path / "board-gh", tmp_path / "board-bin"
    gh.mkdir()
    bin_.mkdir()
    refuse = (f'if a[:2] in (["issue", "view"], ["pr", "view"]) or (a[:1] == ["api"] and any(x.split("?")[0].strip("/") '
              f'== "repos/o/r/issues/{N}" for x in a[1:])):\n'
              f'    sys.stderr.write({failure + chr(10)!r})\n'
              f'    sys.exit(1)\n')
    anchor = 'if a[:2] == ["issue", "view"]:'
    fake = T.FAKE_GH.replace(anchor, refuse + GH_EXTRA + anchor, 1)
    (bin_ / "gh").write_text(fake.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    os.chmod(bin_ / "gh", 0o755)
    env = {**os.environ, "PATH": f"{bin_}:{os.environ['PATH']}", "FAKE_GH_DIR": str(gh), "PYTHONPATH": root,
           "GITHUB_REPOSITORY": "o/r", "DOKIMA_BOARD": "o/1", "N": N, "OUT": str(out), "ROLE": "planner", "STAGE": ""}
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "board", N, str(out)], cwd=tmp_path, env=env,
                       capture_output=True, text=True, timeout=60)
    return p, board_state(str(gh / "board.jsonl")).get(f"issue-{N}")


@pytest.mark.parametrize("failure", [GRAPHQL_LIMIT, SERVER_ERROR], ids=["rate-limit-again", "server-error"])
def test_a_failed_decision_stops_for_the_owner(record_property, tmp_path, monkeypatch, capsys, failure):
    """A decision that still fails stops for the owner, and its card shows Needs you.

    Proves 417.3.
    GitHub refuses every call for good, with its rate-limit words (so the try after the reset fails too) or a server
    error. The planner's run must start nothing and end the record with one Next line mentioning the owner. Then the
    workflow's board step runs on what the run left behind, with GitHub still refusing reads of the issue, and the
    issue's card must end in Plan, the planner's column, showing Needs you. A run that only writes 'needs' in its
    board line, so the board step tries to rebuild the card from GitHub and leaves it as it was, fails here."""
    record_property("proves", "417.3")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, failure, until=float("inf"))
    assert escaped is None, f"417.3: the error escaped the step, so the record has no Next line: {escaped}"
    assert printed == "stop", f"417.3: a failed decision printed {printed!r}, not 'stop'"
    nexts = next_lines(text)
    assert len(nexts) == 1 and nexts[0].startswith(f"**Next:** @{OWNER}"), \
        f"417.3: a failed decision's Next lines do not mention the owner once: {nexts!r}"
    p, card = board_step(tmp_path, tmp_path / "out", failure)
    assert card == ("Plan", True), (f"417.3: after a failed decision, with GitHub still refusing, the board step left "
                                    f"the issue's card at {card} (column, Needs you), not ('Plan', True):\n"
                                    f"{p.stdout}{p.stderr}")


def test_a_rate_limit_that_does_not_lift_waits_once_and_never_hangs(record_property, tmp_path, monkeypatch, capsys):
    """A rate limit that does not lift is waited for once, then the step stops.

    Proves 417.4.
    GitHub refuses every call with its GraphQL rate-limit words, even after the reset time it reports (now in the
    past). The run must wait once, to the reset, try again, and then say so and stop: the fake clock ends within a
    minute past the reset, and the run makes at most 300 calls to GitHub, so a loop retrying with no wait fails too."""
    record_property("proves", "417.4")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, GRAPHQL_LIMIT, until=float("inf"))
    assert escaped is None, f"417.4: the rate-limited run did not end with a decision: {escaped}"
    assert hub.clock >= GRAPHQL_RESET, f"417.4: the run never waited for the reset ({hub.clock - NOW} s of {GRAPHQL_RESET - NOW} s)"
    assert hub.clock <= GRAPHQL_RESET + 60, f"417.4: the run kept waiting, to {hub.clock - NOW} s, past the one reset"
    assert lines_with(text, GRAPHQL_LIMIT), f"417.4: the run that still failed after the reset did not say why:\n{text[-800:]}"
    assert printed == "stop", f"417.4: the run that still failed after the reset printed {printed!r}, not 'stop'"


@pytest.mark.parametrize("read", [ISSUE_READ, BLOCKED_BY_READ], ids=["autopilot-label-read", "blocked-by-read"])
def test_a_rate_limit_on_a_later_autopilot_read_waits_and_starts_the_worker(record_property, tmp_path, monkeypatch,
                                                                            capsys, read):
    """A rate limit after an approved plan on autopilot is waited out; the worker starts.

    Proves 417.2.
    The owner's 15:12Z case: a plan review approves the plan on an issue on autopilot. GitHub answers the issue and
    its comments, then refuses one later read with its REST rate-limit words until the REST limit's reset: the
    issue's labels (is it on autopilot?) or its blocked-by links (is it waiting on an open blocker?). The run must
    wait until that reset, no more than a minute past it, then start the worker with the line
    'Autopilot: plan approved, starting work', exactly as a run GitHub answered. Waiting only around the first read
    of the issue, or stopping at once on these later reads as before #417, fails this test."""
    record_property("proves", "417.2")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, name="answered", rec=PLAN_REVIEW,
                                                labels=[agent.AUTOPILOT])
    assert escaped is None and printed == "start worker", \
        f"417.2: with GitHub answering, an approved plan on autopilot printed {printed!r}, not 'start worker': {escaped}"
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, REST_LIMIT, until=CORE_RESET,
                                                rec=PLAN_REVIEW, failing=only(read), labels=[agent.AUTOPILOT])
    assert any(c[:2] == read for c in hub.calls), f"417.2: the run never made the read {' '.join(read)!r} this test refuses"
    assert escaped is None, f"417.2: the rate-limited read {' '.join(read)!r} was never tried again; GitHub's error escaped: {escaped}"
    assert printed == "start worker", (f"417.2: after GitHub's rate limit on {' '.join(read)!r} reset, the run printed "
                                       f"{printed!r}, not 'start worker' (it waited {sum(hub.slept)} s for a reset "
                                       f"{CORE_RESET - NOW} s away); its Next lines: {next_lines(text)!r}")
    assert CORE_RESET <= hub.clock <= CORE_RESET + 60, (f"417.2: the run waited until {hub.clock - NOW} s, not until "
                                                        f"the REST limit's reset at {CORE_RESET - NOW} s (within a minute)")
    assert hub.autopilot == "Autopilot: plan approved, starting work", \
        f"417.2: after the wait, the run left the Autopilot line {hub.autopilot!r}, not 'Autopilot: plan approved, starting work'"
    assert next_lines(text) == ["**Next:** The worker starts now."], \
        f"417.2: after the wait, the record's Next lines are {next_lines(text)!r}, not the worker starting"
    assert board == "Work none", f"417.2: after the wait, the card is placed {board!r}, not in Work without Needs you"


def test_a_later_autopilot_read_github_refuses_says_githubs_reason(record_property, tmp_path, monkeypatch, capsys):
    """A refused autopilot read after a plan review puts GitHub's reason on the record.

    Proves 417.1.
    A plan review approves the plan on an issue on autopilot; GitHub answers the issue and its comments, then
    answers the read of the issue's labels with "HTTP 502: Server Error" every time. Before #417 that read became
    'Autopilot could not be read from GitHub' with no word of GitHub's reason. The record must now hold exactly one
    line with GitHub's words, start no stage, leave no Autopilot line, and wait less than a minute, since a server
    error is not the rate limit."""
    record_property("proves", "417.1")
    printed, text, board, hub, escaped = decide(tmp_path, monkeypatch, capsys, SERVER_ERROR, until=float("inf"),
                                                rec=PLAN_REVIEW, failing=only(ISSUE_READ), labels=[agent.AUTOPILOT])
    assert any(c[:2] == ISSUE_READ for c in hub.calls), "417.1: the run never read the issue's labels this test refuses"
    said = lines_with(text, SERVER_ERROR)
    assert len(said) == 1, (f"417.1: GitHub refused the autopilot read after a plan review, and the record holds "
                            f"{len(said)} lines with GitHub's reason {SERVER_ERROR!r}, not one"
                            f"{' (the error escaped the step: ' + escaped + ')' if escaped else ''}:\n{text[-1200:]}")
    assert printed == "stop", f"417.1: a stage started though GitHub refused the autopilot read: {printed!r}"
    assert hub.autopilot == "", f"417.1: the run left the Autopilot line {hub.autopilot!r} though the read failed"
    assert sum(hub.slept) < 60, f"417.1: a server error on the autopilot read waited {sum(hub.slept)} s"

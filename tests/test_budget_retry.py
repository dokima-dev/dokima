"""Board and card updates the API budget stopped run again once it is back (#429).

On 2026-10-09 the Dokima app's GraphQL budget hit zero at about 22:10Z and reset at 22:29Z. Board and card runs that
fell in that window failed, and #330 and PR #327 stayed in the wrong columns until a comment forced a redraw. Now
every board update (board.yml's event runs and 15-minute sweeps, and the board step at the end of an agent run) and
every card update (card.yml's redraws and sweeps) that fails while a budget is empty waits for GitHub's reported reset
time, then runs once more from scratch, so its cards show the state on GitHub then. Any other failure fails as today.

The code under test is reached through three seams in dokima/retry.py, which every update must call through the
module, so a test can replace them:
    retry.rate_limit()  GitHub's `GET /rate_limit` answer as JSON ({"resources": {"core": {...}, "graphql": {...}}});
                        raises subprocess.CalledProcessError when GitHub refuses.
    retry.sleep(s)      waits s seconds.
    retry.now()         the time now, in epoch seconds.
Budget below fakes all three on one clock: a budget is empty until its reset time, and GitHub refuses the reads the
test names while any budget is empty, with GitHub's own words ("API rate limit already exceeded"). time.sleep is
made to fail, so a real wait can never hang the suite. The board is test_needs_you's in-memory world, as in
tests/test_board_state.py; the card's own drawing and sweep are faked at card.draw and card.sweep, which card.main calls.
"""
import importlib
import json
import os
import stat
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import test_needs_you as tny  # noqa: E402
from dokima import agent, board, card  # noqa: E402
from dokima import agent_github  # noqa: E402

SPEC, REPO, NEEDS = tny.SPEC, tny.REPO, tny.NEEDS
T0 = 1760047800  # 2026-10-09T22:10:00Z, when the GraphQL budget hit zero
RATE_LIMITED = "GraphQL: API rate limit already exceeded for installation ID 168252268"
BAD_GATEWAY = "HTTP 502: Bad Gateway"


def retry_module(criterion):
    """dokima.retry, or a failure naming the criterion when it does not exist yet."""
    try:
        return importlib.import_module("dokima.retry")
    except ImportError as e:
        pytest.fail(f"{criterion}: there is no dokima/retry.py with rate_limit(), sleep() and now() to wait for "
                    f"GitHub's budget to reset ({e})")


class Budget:
    """GitHub's two API budgets and the clock, faked as one.

    Each budget is empty until its reset, then full again.

    `empty` maps "graphql" or "core" to the seconds after T0 when that budget resets; a budget not named is never
    empty and reports a reset `later` seconds after T0. Each function in `during_wait` changes GitHub while the
    update waits. `again` names budgets that, once reset, are empty again at
    once with a reset an hour later, as when the budget runs out a second time. `readable=False` makes GitHub
    refuse to report the budget."""

    def __init__(self, empty=None, later=3000, again=(), readable=True):
        self.t = T0
        self.resets = dict(empty or {})
        self.later, self.again, self.readable = later, set(again), readable
        self.slept, self.reads, self.during_wait = [], 0, []

    def reset_of(self, name):
        r = self.resets[name]
        return T0 + (r + 3600 if name in self.again and self.t >= T0 + r else r)

    def is_empty(self, name):
        return name in self.resets and (self.t < T0 + self.resets[name] or name in self.again)

    def empty(self):
        return any(self.is_empty(n) for n in ("graphql", "core"))

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.t += seconds
        for change in self.during_wait:
            change()

    def message(self):
        """GitHub's words when it refuses a call because a budget is empty."""
        if self.is_empty("graphql"):
            return RATE_LIMITED
        return "API rate limit exceeded for installation ID 168252268. (HTTP 403)"

    def rate_limit(self):
        self.reads += 1
        if not self.readable:
            raise subprocess.CalledProcessError(1, ["gh", "api", "rate_limit"], output="", stderr=BAD_GATEWAY)
        res = {}
        for name in ("core", "graphql"):
            if self.is_empty(name):
                res[name] = {"limit": 5000, "used": 5000, "remaining": 0, "reset": self.reset_of(name)}
            elif name in self.resets:
                res[name] = {"limit": 5000, "used": 0, "remaining": 5000, "reset": self.reset_of(name) + 3600}
            else:
                res[name] = {"limit": 5000, "used": 1000, "remaining": 4000, "reset": T0 + self.later}
        return {"resources": res, "rate": res["core"]}


@pytest.fixture
def budget(monkeypatch):
    """Wire a Budget into dokima.retry's seams, and make a real wait fail the test."""

    def wire(criterion, **kw):
        retry = retry_module(criterion)
        b = Budget(**kw)
        monkeypatch.setattr(retry, "rate_limit", b.rate_limit)
        monkeypatch.setattr(retry, "sleep", b.sleep)
        monkeypatch.setattr(retry, "now", b.now)

        def real_sleep(seconds):
            raise AssertionError(f"{criterion}: the update waited {seconds} s with time.sleep, not dokima.retry.sleep")

        monkeypatch.setattr(time, "sleep", real_sleep)
        return b

    return wire


@pytest.fixture
def make(monkeypatch):
    """Wire a board world into dokima.board.Board and dokima.agent.gh, and return it."""

    def wire(**kw):
        world = tny.World(**kw)
        monkeypatch.setattr(board, "Board", tny.fake_board(world))
        monkeypatch.setattr(agent_github, "gh", tny.fake_gh(world))
        return world

    return wire


def refuse_while_empty(w, b, numbers, monkeypatch, on_board=False):
    """GitHub refuses every read of `numbers` while a budget is empty.

    With `on_board` it also refuses the board's first read.

    Each update opens the board once, so w.runs counts how many times the update ran."""
    w.runs = 0
    base = w.refuse

    def refuse(n, args):
        if n in numbers:
            if b.empty():
                raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr=b.message())
        base(n, args)

    w.refuse = refuse
    fake = board.Board

    class Board(fake):
        def __init__(self, *a, **kw):
            w.runs += 1
            if on_board and b.empty():
                raise subprocess.CalledProcessError(1, ["gh", "api", "graphql"], output="", stderr=b.message())
            super().__init__(*a, **kw)

    monkeypatch.setattr(board, "Board", Board)


def board_main(event, payload, tmp_path, monkeypatch):
    """Run board.yml's sync step, `python3 -m dokima.board`, on one event; returns its exit code."""
    path = tmp_path / "event.json"
    path.write_text(json.dumps(payload))
    monkeypatch.setenv("GITHUB_EVENT_NAME", event)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    return board.main(["board"])


def run_ends(n, monkeypatch, tmp_path):
    """Run agent.yml's board step, `agent board N OUT`, for a run on issue n.

    The run decided what follows, so the board is placed from GitHub's state."""
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    out = tmp_path / f"out-{n}"
    out.mkdir(exist_ok=True)
    (out / "board.txt").write_text("Backlog none\n")
    return agent.main(["agent", "board", str(n), str(out)])


def card_main(monkeypatch, event, number=None):
    """Run card.yml's step, `python3 dokima/card.py`; returns its exit code (0 when it ends without one).

    An exception it lets out counts as a failed run and is returned as is."""
    monkeypatch.setenv("REPO", REPO)
    monkeypatch.setenv("GITHUB_EVENT_NAME", event)
    if number:
        monkeypatch.setenv("ISSUE_NUMBER", str(number))
    else:
        monkeypatch.delenv("ISSUE_NUMBER", raising=False)
    try:
        card.main()
    except SystemExit as e:
        return e.code or 0
    except subprocess.CalledProcessError as e:
        return e
    return 0


def place(w, kind, n):
    return w.status(kind, n), w.action(kind, n)


# 429.1: a board update a budget stopped runs again after the reset, and its cards end where their state says

def test_a_board_event_run_the_budget_stopped_runs_again_after_the_reset(record_property, make, budget, monkeypatch, tmp_path):
    """A board run the empty budget stopped runs again after the reset.

    It puts the card where its state says then.

    Proves 429.1. Twice, a comment on #57 reaches the board while the GraphQL budget is empty until 22:29Z (19
    minutes): once GitHub refuses the board's own first read, once it refuses #57's state. #57's card is in Work.
    While the run waits, #57 is closed. The run must end with exit 0 and #57 in Done with no pill, read after the
    reset: GitHub refuses every read until then, so an update run again too early fails."""
    record_property("proves", "429.1")
    for case, on_board in (("the board's first read", True), ("#57's state", False)):
        b = budget("429.1", empty={"graphql": 19 * 60})
        w = make(cards={("issue", 57): {"Status": "Work"}})
        refuse_while_empty(w, b, {57}, monkeypatch, on_board=on_board)
        b.during_wait.append(lambda w=w: w.closed.add(("issue", 57)))
        code = board_main("issue_comment", tny.comment(57, "Any news?", "someone-else"), tmp_path, monkeypatch)
        assert code == 0, f"429.1: GitHub refused {case} while the budget was empty, and the board run exited {code}, " \
                          "not 0 after the budget reset"
        assert place(w, "issue", 57) == ("Done", None), \
            f"429.1: #57 closed while the run waited for the budget, yet its card ended at {place(w, 'issue', 57)}, " \
            "not Done with no pill"


def test_a_board_sweep_the_budget_stopped_runs_again_after_the_reset(record_property, make, budget, monkeypatch, tmp_path):
    """A board sweep the empty budget stopped runs again after the reset.

    It puts every card right.

    Proves 429.1. The sweep rechecks every card. #57 (no record yet) sits in Work and #58 (no record) in Review with
    Needs you; GitHub refuses #57's reads while the GraphQL budget is empty until 22:29Z. While the sweep waits, #58 is
    closed. The run must exit 0 with #57 in Backlog with no pill and #58 in Done with no pill."""
    record_property("proves", "429.1")
    b = budget("429.1", empty={"graphql": 19 * 60})
    w = make(cards={("issue", 57): {"Status": "Work"}, ("issue", 58): {"Status": "Review", "Action": NEEDS}})
    refuse_while_empty(w, b, {57}, monkeypatch)
    monkeypatch.setattr(board, "changed", lambda repo: None)
    b.during_wait.append(lambda: w.closed.add(("issue", 58)))
    code = board_main("schedule", {"schedule": "*/15 * * * *"}, tmp_path, monkeypatch)
    assert code == 0, f"429.1: the sweep was stopped by the empty budget and exited {code}, not 0 after the reset"
    got = {"#57": place(w, "issue", 57), "#58": place(w, "issue", 58)}
    assert got == {"#57": ("Backlog", None), "#58": ("Done", None)}, \
        f"429.1: after the budget reset the sweep left the cards at {got}, not #57 in Backlog and #58 in Done, both with no pill"


def test_the_board_step_at_the_end_of_a_run_runs_again_after_the_reset(record_property, make, budget, monkeypatch, tmp_path):
    """The end-of-run board step the empty budget stopped runs again after the reset.

    Proves 429.1. A run ends on #57, whose plan was approved and waits for the owner's /work, so it belongs in Plan
    with Needs you; its card is in Backlog. GitHub refuses #57's reads while the GraphQL budget is empty until 22:29Z.
    The step must exit 0 and leave #57 in Plan with Needs you."""
    record_property("proves", "429.1")
    b = budget("429.1", empty={"graphql": 19 * 60})
    w = make(records={57: tny.plan_approved()}, cards={("issue", 57): {"Status": "Backlog"}})
    refuse_while_empty(w, b, {57}, monkeypatch)
    code = run_ends(57, monkeypatch, tmp_path)
    assert code == 0, f"429.1: the end-of-run board step was stopped by the empty budget and exited {code}, not 0"
    assert place(w, "issue", 57) == ("Plan", NEEDS), \
        f"429.1: after the budget reset #57's card is at {place(w, 'issue', 57)}, not Plan with Needs you"


def test_the_board_step_after_a_failed_run_shows_needs_you_after_the_reset(record_property, make, budget, monkeypatch, tmp_path):
    """After a failed run, a budget-stopped board step shows Needs you once the budget resets.

    Proves 429.1. A worker run on #57 fails its check, so the river stops for the owner: the step must put #57 and its
    open pull request #70 in Work with Needs you. Their cards sit in Backlog and Review. GitHub refuses the board's
    first read while the GraphQL budget is empty until 22:29Z, so a step that gives up at once leaves both cards where
    they were. The step must exit 0, open the board twice (before and after the wait), and leave both in Work with
    Needs you."""
    record_property("proves", "429.1")
    b = budget("429.1", empty={"graphql": 19 * 60})
    w = make(prs={57: 70}, cards={("issue", 57): {"Status": "Backlog"}, ("pr", 70): {"Status": "Review"}})
    refuse_while_empty(w, b, {57, 70}, monkeypatch, on_board=True)
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    out = tmp_path / "out-57"
    out.mkdir()
    # The run failed its check, so it decided nothing: no board.txt, and the record says the check did not pass.
    (out / "record.json").write_text(json.dumps({"role": "worker", "stage": "", "check": {"passed": False}}))
    code = agent.main(["agent", "board", "57", str(out)])
    assert code == 0, f"429.1: the board step after a failed run was stopped by the empty budget and exited {code}, not 0"
    got = {"#57": place(w, "issue", 57), "PR #70": place(w, "pr", 70)}
    assert got == {"#57": ("Work", NEEDS), "PR #70": ("Work", NEEDS)}, \
        f"429.1: after the budget reset the failed run's cards are at {got}, not both in Work with Needs you: " \
        "the board step after a failed run gave up instead of waiting for the reset"
    assert w.runs == 2, f"429.1: the board step after a failed run opened the board {w.runs} times, not twice"
    assert sum(b.slept) >= 19 * 60, f"429.1: the step waited {b.slept} s, less than the 1140 s until the reset"


# 429.2: a card redraw a budget stopped is redrawn after the reset, showing the issue's state then

def test_a_card_redraw_the_budget_stopped_is_redrawn_after_the_reset(record_property, budget, monkeypatch):
    """A card redraw the empty budget stopped is redrawn after the reset.

    It shows the issue as it is then.

    Proves 429.2. A person comments on #57 and card.yml redraws its card, but GitHub refuses the read while the GraphQL
    budget is empty until 22:29Z. While the run waits, #57 is closed. The run must exit 0, having drawn #57's card
    exactly once, after the reset, showing it closed."""
    record_property("proves", "429.2")
    b = budget("429.2", empty={"graphql": 19 * 60})
    issue, drawn = {"state": "open"}, []

    def draw(repo, number, pr_number, **kw):
        if b.empty():
            raise subprocess.CalledProcessError(1, ["gh", "issue", "view", str(number)], output="", stderr=RATE_LIMITED)
        drawn.append((int(number), issue["state"], b.t))
        return {}, {}

    b.during_wait.append(lambda: issue.update(state="closed"))
    monkeypatch.setattr(card, "find_work", lambda repo: (57, None))
    monkeypatch.setattr(card, "draw", draw)
    monkeypatch.setattr(card, "follow", lambda *a, **kw: 0)
    code = card_main(monkeypatch, "issue_comment", 57)
    assert code == 0, f"429.2: the card redraw was stopped by the empty budget and the run ended with {code!r}, not 0"
    assert [(n, s) for n, s, _ in drawn] == [(57, "closed")], \
        f"429.2: #57's card was drawn as {drawn}, not once after the reset showing it closed"
    assert drawn[0][2] >= T0 + 19 * 60, f"429.2: #57's card was drawn at {drawn[0][2]}, before the budget reset at {T0 + 19 * 60}"


def test_a_card_sweep_the_budget_stopped_runs_again_after_the_reset(record_property, budget, monkeypatch):
    """A card sweep the empty budget stopped runs again after the reset.

    Proves 429.2. card.yml's scheduled run finds two cards it cannot redraw while the REST budget is empty until
    22:29Z. The run must exit 0 after sweeping once more, after the reset, with nothing failed."""
    record_property("proves", "429.2")
    b = budget("429.2", empty={"core": 19 * 60})
    swept = []

    def sweep(repo):
        swept.append(b.t)
        return 2 if b.empty() else 0

    monkeypatch.setattr(card, "sweep", sweep)
    code = card_main(monkeypatch, "schedule")
    assert code == 0, f"429.2: the card sweep was stopped by the empty budget and the run ended with {code!r}, not 0"
    assert len(swept) == 2 and swept[1] >= T0 + 19 * 60, \
        f"429.2: the sweep ran at {swept}, not once before and once after the budget reset at {T0 + 19 * 60}"


# 429.3: any other failure fails as today and is not treated as a budget failure

def test_a_board_update_failing_for_another_reason_fails_as_today(record_property, make, budget, monkeypatch, tmp_path, capsys):
    """A board update failing for another reason fails at once, as today.

    No wait and no second run.

    Proves 429.3. GitHub answers HTTP 502 about #57, whose card is in Plan with Needs you. Three times: with both
    budgets well above zero, and with GitHub refusing to report the budget, a comment on #57 reaches the board; and
    the end of a run on #57. Each must exit 1 with an ::error line naming #57, run once, wait for nothing and
    leave its card where it was."""
    record_property("proves", "429.3")
    for case, readable, run in (("a comment, budget left", True, "board"), ("a comment, budget unreadable", False, "board"),
                                ("the end of a run, budget left", True, "agent")):
        b = budget("429.3", readable=readable)
        w = make(cards={("issue", 57): {"Status": "Plan", "Action": NEEDS}})
        refuse_while_empty(w, b, {57}, monkeypatch)
        base = w.refuse

        def refuse(n, args, base=base):
            base(n, args)
            if n == 57:
                raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr=BAD_GATEWAY)

        w.refuse = refuse
        capsys.readouterr()
        if run == "board":
            code = board_main("issue_comment", tny.comment(57, "Any news?", "someone-else"), tmp_path, monkeypatch)
        else:
            code = run_ends(57, monkeypatch, tmp_path)
        out = capsys.readouterr()
        assert code == 1, f"429.3: {case}: GitHub answered 502 and the run exited {code}, not 1 as today"
        assert "::error" in out.out and "#57" in out.out, f"429.3: {case}: the run did not fail naming #57: {out.out!r}"
        assert not b.slept, f"429.3: {case}: a 502 is not a budget failure, yet the run waited {b.slept} s"
        assert w.runs == 1, f"429.3: {case}: the update ran {w.runs} times, not once"
        assert place(w, "issue", 57) == ("Plan", NEEDS), f"429.3: {case}: #57's card moved to {place(w, 'issue', 57)}"


def test_a_card_update_failing_for_another_reason_fails_as_today(record_property, budget, monkeypatch):
    """A card update failing for another reason fails at once, as today.

    No wait and no second run.

    Proves 429.3. With both budgets well above zero, then with GitHub refusing to report the budget: a redraw of #57
    whose read GitHub answers with HTTP 502 must fail, drawing once; a sweep that could not redraw one card must exit
    1, sweeping once. Neither may wait."""
    record_property("proves", "429.3")
    for case, readable in (("budget left", True), ("budget unreadable", False)):
        b = budget("429.3", readable=readable)
        drawn, swept = [], []

        def draw(repo, number, pr_number, **kw):
            drawn.append(number)
            raise subprocess.CalledProcessError(1, ["gh", "issue", "view", str(number)], output="", stderr=BAD_GATEWAY)

        def sweep(repo):
            swept.append(repo)
            return 1

        monkeypatch.setattr(card, "find_work", lambda repo: (57, None))
        monkeypatch.setattr(card, "draw", draw)
        monkeypatch.setattr(card, "follow", lambda *a, **kw: 0)
        monkeypatch.setattr(card, "sweep", sweep)
        code = card_main(monkeypatch, "issue_comment", 57)
        assert code != 0, f"429.3: {case}: GitHub answered 502 to #57's redraw and the run passed"
        assert len(drawn) == 1, f"429.3: {case}: #57's card was drawn {len(drawn)} times, not once"
        code = card_main(monkeypatch, "schedule")
        assert code == 1, f"429.3: {case}: a sweep that could not redraw a card ended with {code!r}, not 1 as today"
        assert len(swept) == 1, f"429.3: {case}: the sweep ran {len(swept)} times, not once"
        assert not b.slept, f"429.3: {case}: a 502 is not a budget failure, yet the run waited {b.slept} s"


# 429.4: a retry waits for GitHub's reported reset time instead of retrying in a loop

def test_the_retry_waits_for_the_reset_of_the_budget_that_ran_out(record_property, make, budget, monkeypatch, tmp_path):
    """The retry waits until GitHub's reported reset of the empty budget.

    The update runs exactly twice.

    Proves 429.4. A comment on #57 reaches the board while GitHub refuses #57's reads. Three cases: only GraphQL is
    empty, resetting in 10 minutes while REST would reset in 50; only REST is empty, resetting in 25 minutes; both are
    empty, GraphQL resetting in 10 and REST in 25 minutes, so it must wait for the later. Each time the run must wait
    from 0 to 60 s past that reset, never less, run the update exactly twice, and exit 0."""
    record_property("proves", "429.4")
    for case, empty, wait in (("only GraphQL empty", {"graphql": 600}, 600), ("only REST empty", {"core": 1500}, 1500),
                              ("both empty", {"graphql": 600, "core": 1500}, 1500)):
        b = budget("429.4", empty=empty, later=3000)
        w = make(cards={("issue", 57): {"Status": "Work"}})
        refuse_while_empty(w, b, {57}, monkeypatch)
        code = board_main("issue_comment", tny.comment(57, "Any news?", "someone-else"), tmp_path, monkeypatch)
        waited = sum(b.slept)
        assert wait <= waited <= wait + 60, \
            f"429.4: {case}: GitHub said the budget resets in {wait} s, and the run waited {waited} s ({b.slept})"
        assert w.runs == 2, f"429.4: {case}: the update ran {w.runs} times, not twice (once before the wait, once after)"
        assert code == 0, f"429.4: {case}: the run exited {code}, not 0 after the reset"


def test_a_second_budget_failure_fails_the_run_instead_of_waiting_again(record_property, make, budget, monkeypatch, tmp_path, capsys):
    """An update whose budget runs out again after the reset fails, never waiting twice.

    Proves 429.4. GraphQL is empty until 22:20Z and, once reset, runs out again at once. A comment on #57 reaches the
    board, and once more a card redraw of #57 runs. Each must wait once, until 22:20Z, try exactly twice and fail."""
    record_property("proves", "429.4")
    b = budget("429.4", empty={"graphql": 600}, again={"graphql"})
    w = make(cards={("issue", 57): {"Status": "Work"}})
    refuse_while_empty(w, b, {57}, monkeypatch)
    code = board_main("issue_comment", tny.comment(57, "Any news?", "someone-else"), tmp_path, monkeypatch)
    assert code == 1, f"429.4: the budget ran out again after the reset and the board run exited {code}, not 1"
    assert w.runs == 2, f"429.4: the board update ran {w.runs} times, not twice: it did not stop"
    assert 600 <= sum(b.slept) <= 660, f"429.4: the board run waited {b.slept} s, not once until the reset 600 s away"

    b = budget("429.4", empty={"graphql": 600}, again={"graphql"})
    drawn = []

    def draw(repo, number, pr_number, **kw):
        drawn.append(b.t)
        raise subprocess.CalledProcessError(1, ["gh", "issue", "view", str(number)], output="", stderr=RATE_LIMITED)

    monkeypatch.setattr(card, "find_work", lambda repo: (57, None))
    monkeypatch.setattr(card, "draw", draw)
    monkeypatch.setattr(card, "follow", lambda *a, **kw: 0)
    code = card_main(monkeypatch, "issue_comment", 57)
    assert code != 0, "429.4: the budget ran out again after the reset and the card run passed"
    assert len(drawn) == 2, f"429.4: #57's card was tried {len(drawn)} times, not twice: the card run did not stop"
    assert 600 <= sum(b.slept) <= 660, f"429.4: the card run waited {b.slept} s, not once until the reset 600 s away"


def test_the_budget_is_read_from_githubs_rate_limit_endpoint(record_property, tmp_path, monkeypatch):
    """The budget and its reset come from GitHub's free rate-limit endpoint.

    That endpoint costs nothing from either budget.

    Proves 429.4. A stand-in `gh` on PATH logs its arguments and answers as GitHub's GET /rate_limit does.
    dokima.retry.rate_limit() must call exactly `gh api rate_limit` and return GitHub's answer, resets included; when
    GitHub refuses, it must raise subprocess.CalledProcessError."""
    record_property("proves", "429.4")
    retry = retry_module("429.4")
    answer = {"resources": {"core": {"limit": 5000, "used": 1000, "remaining": 4000, "reset": T0 + 3000},
                            "graphql": {"limit": 5000, "used": 5000, "remaining": 0, "reset": T0 + 1140}},
              "rate": {"limit": 5000, "used": 1000, "remaining": 4000, "reset": T0 + 3000}}
    bin_dir, log = tmp_path / "bin", tmp_path / "calls.txt"
    bin_dir.mkdir()
    (tmp_path / "answer.json").write_text(json.dumps(answer))
    gh = bin_dir / "gh"
    gh.write_text("#!/bin/sh\n"
                  f"echo \"$*\" >> '{log}'\n"
                  f"if [ -e '{tmp_path}/refuse' ]; then echo 'gh: HTTP 502: Bad Gateway' >&2; exit 1; fi\n"
                  f"cat '{tmp_path}/answer.json'\n")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    got = retry.rate_limit()
    assert log.read_text().splitlines() == ["api rate_limit"], \
        f"429.4: the budget was read with `gh {log.read_text().strip()}`, not `gh api rate_limit`"
    assert got == answer, f"429.4: rate_limit() returned {got}, not GitHub's answer"
    (tmp_path / "refuse").write_text("")
    with pytest.raises(subprocess.CalledProcessError):
        retry.rate_limit()

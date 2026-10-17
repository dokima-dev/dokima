"""The board hears every review and line note, never through a PR's own keyed copy (#396).

GitHub runs a workflow triggered by pull_request, pull_request_review, pull_request_review_comment, push to a branch
or workflow_dispatch from the copy of the workflow file on that branch or pull request, so a pull request that edits
board.yml would change how its own board run behaves while that run holds the keys environment. Only issues,
issue_comment, schedule, pull_request_target and workflow_run always run the default branch's copy.

So board.yml runs only on those, and a review or a line note reaches it in two steps: a keyless workflow (the relay)
runs on the review or line note, and board.yml runs, as main's copy and with the keys, when that relay finishes
(workflow_run). The relay may be the pull request's own copy, so it must hold no key at all.

These tests read the workflow files without a YAML library, and run dokima.board on the workflow_run event GitHub
sends when the relay finishes, against test_needs_you's in-memory world.
"""
import glob
import os
import re
import sys

import pytest
import yaml

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import test_needs_you as tny  # noqa: E402
from dokima import agent, board  # noqa: E402
from dokima import agent_github  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
BOARD = os.path.join(WORKFLOWS, "board.yml")
SPEC, REPO, OWNER, NEEDS, AUTO, LABEL = tny.SPEC, tny.REPO, tny.OWNER, tny.NEEDS, tny.AUTO, tny.LABEL
STRANGER = "someone-else" if OWNER != "someone-else" else "another-person"

# The triggers whose runs always use the default branch's copy of the workflow file.
MAINS_COPY = {"issues", "issue_comment", "schedule", "pull_request_target", "workflow_run"}


def triggers(text):
    """{event: {type, ...}} from a workflow's on: block."""
    block = re.split(r"(?m)^\S", text.split("\non:\n", 1)[1], maxsplit=1)[0]
    out = {}
    for m in re.finditer(r"(?m)^  (\w+):[^\n]*\n?((?:    [^\n]*\n?)*)", block):
        types = re.search(r"types:\s*\[([^\]]*)\]", m.group(2))
        out[m.group(1)] = {t.strip() for t in types.group(1).split(",")} if types else set()
    return out


def run_on(text):
    """The workflow names board.yml's workflow_run trigger runs on, and its types, from its on: block."""
    block = re.split(r"(?m)^\S", text.split("\non:\n", 1)[1], maxsplit=1)[0]
    m = re.search(r"(?m)^  workflow_run:[^\n]*\n((?:    [^\n]*\n?)*)", block)
    if not m:
        return set(), set()
    names = re.search(r"workflows:\s*\[([^\]]*)\]", m.group(1))
    types = re.search(r"types:\s*\[([^\]]*)\]", m.group(1))
    return ({n.strip().strip("\"'") for n in names.group(1).split(",")} if names else set(),
            {t.strip() for t in types.group(1).split(",")} if types else set())


def workflows():
    """{file name: (workflow name, text)} of every workflow in .github/workflows."""
    out = {}
    for path in glob.glob(os.path.join(WORKFLOWS, "*.yml")) + glob.glob(os.path.join(WORKFLOWS, "*.yaml")):
        text = open(path).read()
        name = re.search(r"(?m)^name:\s*(.+?)\s*$", text)
        out[os.path.basename(path)] = (name.group(1).strip("\"'") if name else None, text)
    return out


def review_relays():
    """The workflows board.yml runs after that run on a review and a line note.

    {file: (name, text)}, only for workflows that run on a submitted review and on a created line note."""
    names, _ = run_on(open(BOARD).read())
    out = {}
    for file, (name, text) in workflows().items():
        if file == "board.yml" or name not in names:
            continue
        on = triggers(text)
        if "submitted" in on.get("pull_request_review", set()) and "created" in on.get("pull_request_review_comment", set()):
            out[file] = (name, text)
    return out


def finished(name, event, pr, issue):
    """The workflow_run payload GitHub sends when workflow `name` completes on pull request pr.

    `event` is what started that workflow."""
    return {"action": "completed", "workflow_run": {"name": name, "event": event, "conclusion": "success",
                                                    "head_branch": f"try/issue-{issue}",
                                                    "pull_requests": [{"number": pr, "head": {"ref": f"try/issue-{issue}"}}]}}


@pytest.fixture
def make(monkeypatch):
    """Wire test_needs_you's world into dokima.board.Board and dokima.agent.gh, and return it."""

    def wire(**kw):
        world = tny.World(**kw)
        monkeypatch.setattr(board, "Board", tny.fake_board(world))
        monkeypatch.setattr(agent_github, "gh", tny.fake_gh(world))
        return world

    return wire


# 396.1: board.yml runs only on events that use main's copy of itself

def test_board_yml_runs_only_on_events_that_use_mains_copy(record_property):
    """board.yml never runs a pull request's own copy of itself.

    Proves 396.1. Reads board.yml's triggers. Every one must be an event GitHub always runs from the default branch's copy (issues,
    issue_comment, schedule, pull_request_target, workflow_run). Today it also runs on pull_request_review and
    pull_request_review_comment, which run the pull request's own copy while the job opens the keys environment; any
    other trigger that runs a branch's copy (pull_request, push, workflow_dispatch) fails it the same way. A call
    (workflow_call, #812) counts only when entry.yml makes it on main's-copy events alone."""
    record_property("proves", "396.1")
    text = open(BOARD).read()
    assert "environment: keys" in text, "396.1: board.yml no longer opens the keys environment, so it cannot set the board"
    on = triggers(text)
    assert on, "396.1: no triggers could be read from board.yml"
    own_copy = sorted(set(on) - MAINS_COPY - {"workflow_call"})
    assert not own_copy, (
        f"396.1: board.yml holds the keys and runs on {own_copy}, where GitHub runs the pull request's or branch's own "
        "copy of board.yml, so a pull request that edits board.yml changes its own keyed run")
    for kept in ("issues", "issue_comment", "schedule", "pull_request_target", "workflow_run"):
        assert kept in on, f"396.1: board.yml no longer runs on {kept}, which runs main's copy and must stay"
    # Since #812 an adopter's one workflow calls board.yml at a release tag through entry.yml: only on main's-copy events.
    if "workflow_call" in on:
        entry = yaml.safe_load(open(os.path.join(WORKFLOWS, "entry.yml")).read())
        called = set(re.findall(r"github\.event_name == '(\w+)'", str(entry["jobs"]["board"].get("if"))))
        assert called and called <= MAINS_COPY, (
            f"396.1: entry.yml calls board.yml on {sorted(called - MAINS_COPY)}, where GitHub runs the pull request's "
            "own copy of the calling workflow, so a pull request could change its own keyed run")


# 396.2: a review or a line note still puts both cards where their state says

def test_a_review_and_a_line_note_reach_the_board_through_a_relay(record_property):
    """A review and a line note still start the board through a relay.

    Proves 396.2. Reads the workflows. board.yml's workflow_run trigger must list, with the type completed, a workflow that runs on
    pull_request_review submitted and on pull_request_review_comment created. Today no such workflow exists: board.yml
    hears a review only by running the pull request's own copy of itself."""
    record_property("proves", "396.2")
    names, types = run_on(open(BOARD).read())
    relays = review_relays()
    assert relays, (
        f"396.2: board.yml runs after {sorted(names)}, and none of them runs on a submitted review and a created line "
        "note, so a review or a line note never reaches the board from main's copy")
    assert "completed" in types, f"396.2: board.yml runs after {sorted(names)} only on {sorted(types)}, not when they complete"
    assert "Acceptance criteria" in names, "396.2: board.yml no longer runs when the criteria checks complete"


def test_a_code_owners_review_command_clears_needs_you_through_the_relay(record_property, make):
    """A code owner's review command clears Needs you on both cards when the relay finishes.

    Proves 396.2. #58 with PR #61 waits on the owner and both cards show Needs you. Someone who is not a code owner reviews PR #61
    with /work: when the relay that ran on that review finishes, both cards still show Needs you. The code owner then
    reviews PR #61 as a comment starting /review: when the relay finishes, both cards show no pill, and the run waits
    in #58's own board queue. Fails today because no relay exists."""
    record_property("proves", "396.2")
    relays = review_relays()
    assert relays, "396.2: no workflow board.yml runs after runs on a submitted review, so the board never hears it"
    name = next(iter(relays.values()))[0]
    w = make(prs={58: 61}, records={58: tny.code_approved()},
             cards={("issue", 58): {"Status": "Review", "Action": NEEDS}, ("pr", 61): {"Status": "Review", "Action": NEEDS}})
    payload = finished(name, "pull_request_review", 61, 58)
    assert board.queue("workflow_run", payload) == "board-58", \
        f"396.2: the board run after {name!r} on PR #61 waits in {board.queue('workflow_run', payload)!r}, not #58's queue"
    w.reviews.setdefault(61, []).append(("COMMENTED", "/work", STRANGER))
    board.sync("workflow_run", payload, SPEC, REPO)
    got = tny.pills(w, ("pr", 61), ("issue", 58))
    assert got == {"pr #61": NEEDS, "issue #58": NEEDS}, \
        f"396.2: {STRANGER}, not a code owner, reviewed PR #61 with /work and after {name!r} finished the cards show {got}"
    w.reviews[61].append(("COMMENTED", "/review Look again at the parser."))
    board.sync("workflow_run", payload, SPEC, REPO)
    got = tny.pills(w, ("pr", 61), ("issue", 58))
    assert got == {"pr #61": None, "issue #58": None}, \
        f"396.2: the code owner's review said /review on PR #61 and after {name!r} finished the cards show {got}"


def test_a_line_note_puts_both_cards_where_their_state_says_through_the_relay(record_property, make):
    """A line note puts both cards where their state says once the relay finishes.

    Proves 396.2. #57's code review approved, so it waits on the owner: its card and its PR #60's belong in Review with Needs you,
    but both sit in Work with no pill. Someone leaves a line note on PR #60; when the relay that ran on it finishes,
    both cards are in Review with Needs you. #59's wrong card, which the note is not about, stays as it was. Fails
    today because no relay exists."""
    record_property("proves", "396.2")
    relays = review_relays()
    assert relays, "396.2: no workflow board.yml runs after runs on a created line note, so the board never hears it"
    name = next(iter(relays.values()))[0]
    w = make(prs={57: 60}, records={57: tny.code_approved(), 59: tny.code_approved()},
             cards={("issue", 57): {"Status": "Work"}, ("pr", 60): {"Status": "Work"},
                    ("issue", 59): {"Status": "Done", "Action": AUTO}})
    board.sync("workflow_run", finished(name, "pull_request_review_comment", 60, 57), SPEC, REPO)
    got = {f"{k} #{n}": (w.status(k, n), w.action(k, n)) for k, n in (("issue", 57), ("pr", 60))}
    assert got == {"issue #57": ("Review", NEEDS), "pr #60": ("Review", NEEDS)}, \
        f"396.2: after a line note on PR #60 and {name!r} finished, the cards are at {got}, not Review with Needs you"
    assert (w.status("issue", 59), w.action("issue", 59)) == ("Done", AUTO), \
        "396.2: a line note on PR #60 moved #59's card, which it is not about"


# 396.3: the workflow that runs on a review holds no key

def test_the_review_relay_holds_no_key(record_property):
    """The workflow that runs on a review or line note holds no key.

    Proves 396.3. GitHub runs it from the pull request's own copy, so it must name no secret, open no environment, mint no app
    token and call no other workflow file of the branch (which could hold keys). Each relay board.yml runs after is
    read; a relay holding any of these fails, and so does finding none (today)."""
    record_property("proves", "396.3")
    relays = review_relays()
    assert relays, "396.3: no workflow runs on a review for board.yml, so there is no keyless relay to check"
    for file, (name, text) in relays.items():
        for held, why in (("secrets.", "names a secret"), ("environment:", "opens an environment"),
                          ("create-github-app-token", "mints the app's token"), ("uses: ./", "calls a workflow of the branch")):
            assert held not in text, f"396.3: {file} ({name}) runs the pull request's own copy on a review and {why}"

"""Hotfix pull requests carry the label; a design choice sends the issue back.

Issue #864: the design choice sends it back to planning.

These tests run the agent workflow (.github/workflows/agent.yml) for the worker of hotfix issue #57, the way
tests/test_hotfix.py does, with its machine and fakes. Its fake `gh` notes every call, so a test can read how the
pull request was opened and which labels were put on it; its signals list the agents started next; its comments list
what was said on the issue.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_hotfix as th  # noqa: E402
import test_start as ts  # noqa: E402
from dokima import agent  # noqa: E402

DESIGN = "The ask can be read two ways: rename the product everywhere, or fix only the page title."
WORK_BACK = {"summary": "Stopped: the ask needs a design choice.", "criteria": {"ask": "Nothing built: the ask needs a design choice."},
             "evidence": "pytest -q: 1 passed",
             "raises": [{"kind": "blocker", "to": "planner", "label": "Design choice", "text": DESIGN,
                         "evidence": "`app.py` holds the title; the name also shows in other files."}],
             "answers": []}
PLANNED_WORK = {"summary": "Fixed the page title.", "criteria": {"57.1": "`app.py` now says Dokima."},
                "evidence": "pytest -q: 2 passed", "raises": [], "answers": []}


def pr_labels(r, pr=ts.PR):
    """Every label the run put on its pull request, by any of three calls.

    The calls: `gh pr create`, `gh pr edit` or the REST labels call."""
    out = []
    for c in r.calls():
        if c[:2] == ["pr", "create"] or (c[:2] == ["pr", "edit"] and str(pr) in c):
            out += [c[i + 1] for i, x in enumerate(c[:-1]) if x in ("--label", "-l", "--add-label")]
        if c[:1] == ["api"] and any(x.split("?")[0].rstrip("/").endswith(f"issues/{pr}/labels") for x in c):
            out += [x.split("=", 1)[1] for x in c if x.startswith("labels[]=") or x.startswith("labels=")]
    return [l for x in out for l in x.split(",")]


def test_a_hotfix_pull_request_carries_the_hotfix_label(record_property, tmp_path, monkeypatch):
    """A hotfix worker's pull request opens with the hotfix label on it.

    Proves 864.1. Runs the hotfix worker on #57, labeled hotfix and never planned, which opens pull request #60. The
    run must put the hotfix label on #60, when opening it or right after. Beside it, the worker of an unlabeled issue
    with an approved plan, handing back a planned worker's hand-back, opens its pull request without the hotfix label."""
    record_property("proves", "864.1")
    r = th.Hotfix(tmp_path / "hotfix", "worker")
    assert not r.failed, f"864.1: the hotfix worker's run failed; {r.why()}"
    opened = [c for c in r.calls() if c[:2] == ["pr", "create"]]
    assert len(opened) == 1, f"864.1: the hotfix worker did not open one pull request: {opened}"
    assert th.HOTFIX in pr_labels(r), \
        f"864.1: the hotfix pull request was opened without the hotfix label; pr create: {opened[0]}"
    monkeypatch.setattr(th, "WORK", PLANNED_WORK)
    plain = th.Hotfix(tmp_path / "plain", "worker", labels=(), comments=ts.STORY_APPROVED, try_branch=True)
    assert any(c[:2] == ["pr", "create"] for c in plain.calls()), \
        f"864.1: the planned worker opened no pull request to compare with; {plain.why()}"
    assert th.HOTFIX not in pr_labels(plain), "864.1: an unlabeled issue's pull request got the hotfix label"


def test_a_hotfix_worker_finding_a_design_choice_starts_the_planner(record_property, tmp_path, monkeypatch):
    """A hotfix worker that finds a design choice starts the planner on the issue.

    Proves 864.2. Runs the hotfix worker on #57, which hands back a blocker for the planner: the ask needs a design
    choice. Exactly one signal with Dokima's app key must start the planner for #57, and no code review starts.
    The worker's prompt must tell it to raise a blocker for the planner when the ask needs a design choice. Beside
    it, a hotfix worker that raises nothing still starts code review, not the planner."""
    record_property("proves", "864.2")
    monkeypatch.setattr(th, "WORK", WORK_BACK)
    r = th.Hotfix(tmp_path / "back", "worker")
    assert r.agent_started(), f"864.2: the hotfix worker never started; {r.why()}"
    recs = r.records()
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("worker", True)], \
        f"864.2: the worker's hand-back raising a design choice did not pass its check: {[x.get('check') for x in recs]}; {r.why()}"
    roles = [s[0] for s in r.signals()]
    assert roles == ["planner"], f"864.2: a hotfix needing a design choice did not start the planner once: {r.signals()}"
    prompt = r.prompt().lower()
    assert "design choice" in prompt and "blocker for the planner" in prompt, \
        "864.2: the hotfix worker's prompt never tells it to raise a blocker for the planner on a design choice"
    monkeypatch.undo()
    plain = th.Hotfix(tmp_path / "plain", "worker")
    assert [s[0] for s in plain.signals()] == ["reviewer"], \
        f"864.2: a hotfix worker raising nothing did not start code review: {plain.signals()}"


def test_a_hotfix_worker_sending_it_back_says_why_on_the_issue(record_property, tmp_path, monkeypatch):
    """A hotfix the worker sends back to planning says why on the issue.

    Proves 864.3. Runs the hotfix worker on #57, which hands back a blocker for the planner whose text says the ask
    needs a design choice. Issue #57 must get a new comment, not a run record, that carries that text and says the
    hotfix goes back to planning. Beside it, a hotfix worker that raises nothing posts no such comment."""
    record_property("proves", "864.3")
    monkeypatch.setattr(th, "WORK", WORK_BACK)
    r = th.Hotfix(tmp_path / "back", "worker")
    assert r.agent_started(), f"864.3: the hotfix worker never started; {r.why()}"
    told = [c["versions"][-1] for c in r.comments() if c["kind"] == "issue" and c["number"] == th.ISSUE
            and not agent.is_record({"author": {"login": agent.BOT}, "body": c["versions"][-1]})
            and agent.LIVE not in c["versions"][-1]]
    said = [b for b in told if DESIGN in b]
    assert said, f"864.3: issue #57 got no comment saying why the hotfix went back to planning: {told}"
    assert "planning" in said[0].lower(), f"864.3: the comment does not say the hotfix goes back to planning: {said[0]!r}"
    monkeypatch.undo()
    plain = th.Hotfix(tmp_path / "plain", "worker")
    assert not any("planning" in b.lower() for b in plain.on("issue", th.ISSUE)
                   if not agent.is_record({"author": {"login": agent.BOT}, "body": b}) and agent.LIVE not in b), \
        "864.3: a hotfix worker raising nothing still said on the issue it went back to planning"

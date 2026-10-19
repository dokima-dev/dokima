"""A worker hand-back with no change and no branch starts no code review (#909)."""
from dokima import agent

WORK = {"summary": "No change: the ask needs your decision.", "criteria": {"ask": "Nothing built."},
        "evidence": "pytest -q: 1 passed", "raises": [], "answers": []}


def worker(files):
    """A passed worker record that changed `files`."""
    return {"role": "worker", "stage": None, "handback": WORK, "check": {"passed": True, "problems": []},
            "files_changed": files, "branch": "try/issue-57"}


def test_a_worker_with_no_change_and_no_branch_starts_no_reviewer():
    """No change and no branch waits for the owner.

    Beside it, a hand-back with a branch still starts code review."""
    step = agent.next_step([], worker([]), {"owner"}, autopilot=lambda: True)
    assert step[0] == "stop", f"a worker with no change and no branch started {step}"
    assert agent.next_step([], worker(["app.py"]), {"owner"}, autopilot=lambda: True) == ("start", "reviewer", "pr")


def test_a_worker_with_no_change_on_an_existing_branch_still_starts_code_review():
    """A later round with no change on a pushed branch is still reviewed."""
    earlier = {"author": {"login": agent.BOT}, "body": agent.render(worker(["app.py"]))}
    assert agent.next_step([earlier], worker([]), {"owner"}, autopilot=lambda: True) == ("start", "reviewer", "pr")

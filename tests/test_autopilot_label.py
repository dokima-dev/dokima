"""A person adding the autopilot label by hand switches that issue on, as `/autopilot start` does.

Before this, autopilot.yml woke only when an issue closed, so an issue labeled by hand with nothing blocking it sat
idle until someone posted `/plan`. These tests add the label the way GitHub tells of it (`issues: labeled`) and run
every workflow GitHub starts on that event, on the machine of test_autopilot_close.py.
"""
from dokima.agent_autopilot import AUTOPILOT_START_LINE
from test_autopilot_close import Repo, LABEL, planned


def start_lines(m, n):
    """How many new comments on issue n read exactly the switched-on Autopilot line."""
    return sum(1 for b in m.new_comments(n) if b.strip() == AUTOPILOT_START_LINE)


def test_a_label_added_by_hand_starts_an_issue_nothing_blocks(record_property, tmp_path):
    """#101 waits on nothing and has nothing started: adding the label by hand starts its planner once, with one line."""
    m = Repo(tmp_path / "hand", {57: [101]}, {})
    m.add_label(101)
    assert not m.failed, f"a workflow failed when the label was added: {m.failures}\n{m.tail()}"
    assert m.planners_started("label") == {101: 1}, f"started: {m.planners_started('label')}\n{m.tail()}"
    assert start_lines(m, 101) == 1, f"#101's new comments: {m.new_comments(101)}"


def test_a_label_added_to_a_blocked_issue_starts_nothing(record_property, tmp_path):
    """#102 is blocked by #101, still open: the label goes on, but no planner starts until #101 closes."""
    m = Repo(tmp_path / "blocked", {57: [101, 102]}, {}, deps={102: [101]})
    m.add_label(102)
    assert not m.failed, f"a workflow failed: {m.failures}\n{m.tail()}"
    assert m.planners_started("label") == {}, f"started: {m.planners_started('label')}"
    assert start_lines(m, 102) == 0


def test_a_label_added_to_an_issue_already_planned_starts_nothing_again(record_property, tmp_path):
    """#104 already has a plan record: adding the label never starts its planner a second time."""
    m = Repo(tmp_path / "planned", {57: [104]}, {}, seed=[planned(104, 4001)])
    m.add_label(104)
    assert not m.failed, f"a workflow failed: {m.failures}\n{m.tail()}"
    assert m.planners_started("label") == {}, f"started: {m.planners_started('label')}"


def test_the_label_added_by_dokimas_app_starts_nothing_here(record_property, tmp_path):
    """`/autopilot start` adds the label as Dokima's app and starts what it should itself, so that label starts nothing."""
    m = Repo(tmp_path / "bot", {57: [101]}, {})
    m.add_label(101, sender_type="Bot")
    assert m.planners_started("label") == {}, f"started: {m.planners_started('label')}"
    assert start_lines(m, 101) == 0


def test_another_label_starts_nothing(record_property, tmp_path):
    """Adding some other label by hand never starts a planner."""
    m = Repo(tmp_path / "other", {57: [101]}, {})
    m.add_label(101, name="bug")
    assert m.planners_started("label") == {}, f"started: {m.planners_started('label')}"

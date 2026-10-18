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


def test_a_label_run_also_starts_issues_whose_own_label_run_github_dropped(record_property, tmp_path):
    """#101 and #103 were labeled together; GitHub dropped #101's run. #103's run starts both, once each; #102, blocked,
    and #104, already planned, still start nothing (#843)."""
    record_property("proves", "843.1")
    m = Repo(tmp_path / "dropped", {57: [101, 102, 103, 104]}, {101: [LABEL], 102: [LABEL], 104: [LABEL]},
             deps={102: [101]}, seed=[planned(104, 4001)])
    m.add_label(103)
    assert not m.failed, f"843.1: a workflow failed: {m.failures}\n{m.tail()}"
    assert m.planners_started("843.1") == {101: 1, 103: 1}, \
        f"843.1: a label run did not pick up the issue whose own run was dropped: {m.planners_started('843.1')}\n{m.tail()}"
    assert start_lines(m, 101) == 1 and start_lines(m, 103) == 1


# The repo calls its autopilot label something else in its settings file (#811).
RENAMED = "on-autopilot"
RENAMED_SETTINGS = {".dokima/settings.yaml": f"labels:\n  autopilot: {RENAMED}\n"}


def test_a_renamed_label_added_by_hand_starts_the_issue(record_property, tmp_path):
    """Adding the repo's renamed autopilot label by hand starts the issue's planner.

    Proves 811.1. The repo's settings file names the autopilot label `on-autopilot`. A person adds `on-autopilot` to #101, which
    waits on nothing, the way GitHub tells of it, and every workflow GitHub starts on that event runs. Checks #101's
    planner started once, with one switched-on Autopilot line. Today autopilot.yml only wakes for a label named
    `autopilot`, so nothing starts."""
    record_property("proves", "811.1")
    m = Repo(tmp_path / "renamed", {57: [101]}, {}, files=RENAMED_SETTINGS)
    m.add_label(101, name=RENAMED)
    assert not m.failed, f"811.1: a workflow failed when the renamed label was added: {m.failures}\n{m.tail()}"
    assert m.planners_started("811.1") == {101: 1}, \
        (f"811.1: adding the renamed label {RENAMED!r} by hand did not start #101's planner once: "
         f"{m.planners_started('811.1')}\n{m.tail()}")
    assert start_lines(m, 101) == 1, f"811.1: #101 did not get one switched-on Autopilot line: {m.new_comments(101)}"


def test_the_old_label_name_starts_nothing_once_the_label_is_renamed(record_property, tmp_path):
    """When the repo renames its autopilot label, adding a label still called `autopilot` starts nothing.

    Proves 811.1. The settings file names the label `on-autopilot`; a person adds a label named `autopilot` to #101. Checks no
    planner starts and no Autopilot line is written, so only the repo's own label name switches an issue on."""
    record_property("proves", "811.1")
    m = Repo(tmp_path / "old-name", {57: [101]}, {}, files=RENAMED_SETTINGS)
    m.add_label(101, name=LABEL)
    assert not m.failed, f"811.1: a workflow failed when the old label name was added: {m.failures}\n{m.tail()}"
    assert m.planners_started("811.1") == {}, \
        f"811.1: the old name 'autopilot' started a planner though the repo renamed its label: {m.planners_started('811.1')}"
    assert start_lines(m, 101) == 0, f"811.1: #101 got an Autopilot line from the old label name: {m.new_comments(101)}"

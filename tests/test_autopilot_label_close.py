"""A label run that replaces a waiting close run still does its work (#853).

A person adding the autopilot label starts a run in autopilot.yml's one queue for the repo, the same queue every close
waits in. GitHub keeps one waiting run there and cancels the rest, so a label added while a close waits drops that
close's run. Before #853 the label run only started planners, so the dropped close never closed its done parent, never
switched its done tree off autopilot and never planned again an issue whose blockers it merged.

Each test closes an issue the way a dropped run leaves it (closed on GitHub, its workflows never run), then a person
adds the autopilot label to another issue, on the machine of test_autopilot_close.py, and checks the close's work done.
"""
import test_blocked_worker as bw
from test_autopilot_close import Repo, LABEL


def dropped_close(tmp):
    """#301 closes with its run dropped, then a person labels #60 by hand."""
    m = Repo(tmp, {59: [301]}, {59: [LABEL], 301: [LABEL]})
    m.close_quietly(301)
    m.add_label(60)
    assert not m.failed, f"test setup: a workflow failed when #60 was labeled: {m.failures}\n{m.tail()}"
    return m


def test_a_label_run_closes_the_done_parent_of_a_dropped_close(record_property, tmp_path):
    """A label run closes a parent whose last sub-issue closed with its run dropped.

    Proves 853.1.
    #59 on autopilot holds only #301. #301 closes but its run is dropped; then a person labels #60. #59 must be closed
    as completed with exactly one comment saying its tree is done. With #59 still holding an open #302, the same steps
    leave #59 open with no new comment."""
    record_property("proves", "853.1")
    m = dropped_close(tmp_path / "done")
    assert m.state(59) == ("closed", "completed"), \
        f"853.1: #59 is {m.state(59)} after the label run, though its only sub-issue #301 closed; the dropped close's work was lost\n{m.tail()}"
    said = m.new_comments(59)
    assert len(said) == 1 and "tree" in said[0].lower() and "done" in said[0].lower(), \
        f"853.1: #59 should get exactly one comment saying its tree is done: {said}"

    m = Repo(tmp_path / "not-yet", {59: [301, 302]}, {59: [LABEL], 301: [LABEL], 302: [LABEL]})
    m.close_quietly(301)
    m.add_label(60)
    assert not m.failed, f"853.1 (one left): a workflow failed when #60 was labeled: {m.failures}\n{m.tail()}"
    assert m.state(59)[0] == "open", "853.1 (one left): #59 closed while its sub-issue #302 is still open"
    assert m.new_comments(59) == [], f"853.1 (one left): #59 got comments while #302 is still open: {m.new_comments(59)}"


def test_a_label_run_switches_a_dropped_closes_done_tree_off_autopilot(record_property, tmp_path):
    """A label run takes a tree a dropped close finished off autopilot.

    Proves 853.2.
    #59 on autopilot holds only #301, and #61 is a lone issue on autopilot; both #301 and #61 close but their runs are
    dropped. Then a person labels #60. #59, #301 and #61 must be off autopilot; #60, just labeled, and #57 with its
    open #101 must stay on."""
    record_property("proves", "853.2")
    m = Repo(tmp_path / "off", {59: [301], 57: [101]}, {n: [LABEL] for n in (59, 301, 61, 57, 101)})
    m.close_quietly(301)
    m.close_quietly(61)
    m.add_label(60)
    assert not m.failed, f"853.2: a workflow failed when #60 was labeled: {m.failures}\n{m.tail()}"
    left = m.on_autopilot() & {59, 301, 61}
    assert left == set(), \
        f"853.2: these issues of done trees stayed on autopilot after the label run, so the dropped closes were lost: {sorted(left)}\n{m.tail()}"
    kept = {57, 101, 60} - m.on_autopilot()
    assert kept == set(), f"853.2: these open issues went off autopilot, though their trees are not done: {sorted(kept)}"


def test_a_label_run_plans_again_an_issue_a_dropped_close_unblocked(record_property, tmp_path):
    """A label run plans again, once, an issue a dropped close unblocked.

    Proves 853.3.
    #57 is on autopilot, blocked by #101 and #102 (#102 closed), its plan approved while #101 was open, so nothing was
    built. #101 closes but its run is dropped; then a person labels #60. #57's planner must start exactly once, with
    exactly one `Autopilot: blockers merged, starting plan`, and no worker. With #102 still open, nothing starts on #57."""
    record_property("proves", "853.3")
    m = bw.repo(tmp_path / "unblocked", bw.APPROVED)
    m.close_quietly(101)
    m.add_label(60)
    bw.assert_plans_again_once(m, "853.3", "label run after a dropped close")

    m = bw.repo(tmp_path / "still-blocked", bw.APPROVED, closed=())
    m.close_quietly(101)
    m.add_label(60)
    bw.assert_starts_nothing(m, "853.3", "one blocker still open")

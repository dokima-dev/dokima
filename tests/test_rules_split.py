"""The rules file splits into a short index and topic files, losing no test (#638).

Story 3 of #581. Issues that change different rules kept clashing on `AGENTS.md`, one file of 29 KB, so the owner
decided it becomes a short index linking topic files, all read by the word check (#581, comment 6157254121). Story 2
(#637) already made the word check and agent.yml's runtime copy read every repo markdown file `AGENTS.md` links.

The index keeps its opening and the "Working in this repo" rules, which every agent must see first since `CLAUDE.md`
loads only `AGENTS.md`; each other section moves, under its own `## ` heading, to a file the index links. Tests that
read a rule find it through `tests/rules_files.py`, wherever the split puts it.

The last two tests hold "after both splits": each first checks the rules file is split, then proves its promise.
"""
import os
import subprocess
import sys
from collections import Counter

from rules_files import ROOT, rules_files

# Every section of AGENTS.md before the split, except "Working in this repo", which stays in the index.
TOPICS = ("The picture", "The core rule", "Principles", "Roles", "The flow (the river)", "Commands",
          "Raising and answering", "Where specs go", "The board", "The issue body", "Agent records and cards",
          "Splitting and the graph", "Changing scope", "Identity and safety", "Decisions log")
SHORT = 4000  # bytes; the rules file was 29 KB before the split.

# The tests that read the rules, each of which the split could break.
RULE_TESTS = (
    "tests/test_design.py::test_agents_md_holds_the_design",
    "tests/test_issue_refs_rule.py",
    "tests/test_where_specs_go.py",
    "tests/test_rules_topics.py",
    "tests/test_raise_design.py",
    "tests/test_open_until_planned.py::test_agents_md_says_the_text_shows_open_until_planned",
    "tests/test_board_state.py::test_agents_md_says_a_closed_item_shows_no_pill_whatever_its_labels",
    "tests/test_blocked_worker.py::test_agents_md_says_a_blocked_issue_plans_only_after_its_blockers_merge",
    "tests/test_card_folds.py::test_agents_md_says_the_owners_text_is_folded",
    "tests/test_autopilot.py::test_agents_md_tells_how_autopilot_works",
    "tests/test_run_cards.py::test_agents_md_has_the_human_brain_bottleneck_principle",
    "tests/test_automerge.py::test_agents_md_says_autopilot_merges_what_the_reviewer_approved",
    "tests/test_autopilot_river.py::test_an_assumption_is_accepted_only_on_words_the_owner_really_said",
)

# Every test on main before the first split (#636), at 61faa9e, one line per test case.
BEFORE = os.path.join(ROOT, "tests", "samples", "tests_before_split.txt")
# Tests another issue renamed after 61faa9e, old name to new, with the issue that did it. A later issue that renames
# or drops one of the tests above adds it here, with its reason.
MOVED = {
    # #645: stories hold up to five criteria, so the refused sizes and the test's name changed.
    "tests/test_size_rule.py::test_too_big_too_small_or_too_many_is_refused":
        "tests/test_size_rule.py::test_a_story_over_five_or_empty_is_refused",
}


def topic_files():
    """Each linked topic file's lines by its path; the rules file itself is left out."""
    return {f: open(os.path.join(ROOT, f), encoding="utf-8").read().splitlines() for f in rules_files()[1:]}


def require_split(key):
    """Fails naming the criterion when the rules file links no topic file yet."""
    assert len(rules_files()) > 1, f"{key}: the rules file is not split yet: AGENTS.md links no topic file"


def test_the_rules_file_is_a_short_index_linking_one_file_per_topic(record_property):
    """The rules file is a short index linking one file per topic.

    Reads `AGENTS.md` and every repo markdown file it links. Each of the 15 topics the rules file held must open
    exactly one linked file, under its own heading, with the topic's text below it and no other topic in the same
    file; a link to a file that does not exist does not count. The rules file itself must hold none of those topics
    and be under 4,000 bytes. On today's single rules file this fails: no topic file is linked. Proves 638.1."""
    record_property("proves", "638.1")
    index = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
    kept = [t for t in TOPICS if f"## {t}" in index.splitlines()]
    assert not kept, f"638.1: the rules file still holds these topics instead of linking them: {kept}"
    files = topic_files()
    for topic in TOPICS:
        homes = [f for f, lines in files.items() if lines and lines[0].strip() == f"## {topic}"]
        assert len(homes) == 1, \
            f"638.1: the topic '{topic}' should open exactly one file the rules file links, found {homes or 'none'}"
        lines = files[homes[0]]
        assert any(l.strip() for l in lines[1:]), f"638.1: {homes[0]} holds the heading of '{topic}' and no text"
        others = [l for l in lines[1:] if l.startswith("## ")]
        assert not others, f"638.1: {homes[0]} holds more than one topic: {others}"
    size = os.path.getsize(os.path.join(ROOT, "AGENTS.md"))
    assert size < SHORT, f"638.1: the rules file is {size} bytes, not a short index (under {SHORT})"


def test_the_tests_that_read_the_rules_pass_after_the_split(record_property):
    """Every test that reads the rules still passes once the rules file is split.

    Checks the rules file links its topic files, then runs every test that reads a rule (the sections the old tests
    check, the word check and the runtime copy) in a fresh pytest from the repo root, and fails with its output
    unless all of them pass. The All tests check on the pull request runs every other test. Proves 638.2."""
    record_property("proves", "638.2")
    require_split("638.2")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *RULE_TESTS], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, f"638.2: tests that read the rules fail after the split:\n{r.stdout[-3000:]}{r.stderr[-800:]}"


def collected():
    """Every test case pytest collects from the repo root now, one node id each."""
    r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests"],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"638.3: pytest cannot collect the tests:\n{r.stdout[-2000:]}{r.stderr[-800:]}"
    return [l.strip() for l in r.stdout.splitlines() if "::" in l]


def test_every_test_from_before_the_first_split_still_runs(record_property):
    """Every test that ran on main before the first split still runs after both splits.

    Checks the rules file is split, then collects every test as pytest would run them and compares with the 1,127
    test cases on main before the first split. Each test there must still be collected, with at least as many cases
    as before; a test another issue renamed counts when its new name runs. Tests added since do not count against
    it. Proves 638.3."""
    record_property("proves", "638.3")
    require_split("638.3")
    before = Counter(l.strip().split("[")[0] for l in open(BEFORE) if l.strip())
    now = Counter(n.split("[")[0] for n in collected())
    lost = [f"{t} ({k} before, {now[t]} now)" for t, k in sorted(before.items()) if t not in MOVED and now[t] < k]
    lost += [f"{t}, renamed {new}, (none now)" for t, new in MOVED.items() if not now[new]]
    assert not lost, "638.3: these tests no longer run as they did before the first split:\n" + "\n".join(lost)

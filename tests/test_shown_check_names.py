"""Tests for #846: adopters' card and branch updates find checks by shown names.

An adopter's repo runs Dokima through the one thin workflow the install ships (`dokima/install/dokima.yml`): its job
`dokima` calls `entry.yml`, whose jobs `full-suite` and `acceptance-criteria` call the workflows holding the checks.
GitHub names a called job's check after every caller above it, so there the checks show as
`dokima / full-suite / all tests`, `dokima / acceptance-criteria / Acceptance criteria` and
`dokima / acceptance-criteria / 846.1 · ...`, never by their plain names. #820 makes the audit want those names; these
tests ask the card and the branch updates to find the checks by them too.

Each test copies the settings file the install ships (`dokima/install/settings.yaml`) into a temp repo as
`.dokima/settings.yaml`, the way an adopter installs it, and runs from that repo, as the card and update workflows do.
The card is drawn by `dokima.card.render` from records and check runs; branch updates run `dokima.uptodate.run`
against the fake GitHub of tests/test_uptodate_failing.py. Dokima's own repo, with plain names, is already covered by
older tests (tests/test_card_criterion_label.py, tests/test_uptodate_failing.py).
"""
import os
import re
import shutil
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from dokima import card, plan  # noqa: E402
from test_uptodate_failing import M1, GitHub, run as update_run  # noqa: E402

INSTALL_SETTINGS = os.path.join(ROOT, "dokima", "install", "settings.yaml")
ALL_TESTS = "dokima / full-suite / all tests"
ACCEPTANCE = "dokima / acceptance-criteria / Acceptance criteria"
CRITERION = "dokima / acceptance-criteria / 40.1 · First thing works"

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
ASK = "https://github.com/o/r/issues/40"
PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": "First thing works", "source": ASK}],
        "non_functional": [],
        "tests": {"40.1": ["tests/test_a.py::test_one"]},
        "test_changes": {}}
TESTS = {"tests/test_a.py::test_one": {"verified_by": "The one thing runs.",
                                       "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L1"}}
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
      "merged_by": None}


def rec(role, stage=None, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


RECS = [rec("planner", n=11, **PLAN), rec("reviewer", "plan", n=12, verdict="approve"), rec("worker", n=13)]


def job(n):
    """The link of job n of a check run."""
    return f"https://github.com/o/r/actions/runs/2/job/{n}"


def check(name, conclusion="success", n=7):
    """One completed GitHub check run on the PR's latest commit."""
    return {"name": name, "status": "completed", "conclusion": conclusion, "html_url": job(n)}


@pytest.fixture
def adopter(tmp_path, monkeypatch):
    """Runs the test from an adopter's repo holding the settings file the install ships."""
    (tmp_path / ".dokima").mkdir()
    shutil.copy(INSTALL_SETTINGS, tmp_path / ".dokima" / "settings.yaml")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def draw(check_runs):
    """The card for issue 40, planned, with its PR's latest commit carrying CHECK_RUNS."""
    found = {"recs": RECS, "pr": PR, "check_runs": check_runs, "reviews": [], "owners": {"boss"}, "tests": TESTS,
             "worker": {"status": "completed", "conclusion": "success",
                        "html_url": "https://github.com/o/r/actions/runs/1"},
             "children": []}
    return card.render(REPO, ISSUE, found)


def done_verdict(text, field, k):
    """The verdict and link the Definition of Done shows for FIELD, e.g. ("passed", url)."""
    line = next((l for l in text.splitlines() if l.startswith("**Definition of Done:**")), None)
    assert line, f"{k}: the card has no Definition of Done line:\n{text}"
    for part in line[len("**Definition of Done:**"):].split(" · "):
        if part.strip().endswith(field):
            alt = re.search(r'alt="([^"]+)"', part)
            url = re.search(r'<a href="([^"]+)">', part)
            return alt and alt[1], url and url[1]
    raise AssertionError(f"{k}: the Definition of Done shows no {field}: {line}")


def criterion_verdict(text, words, k):
    """The verdict and link the card shows on the bullet of the criterion reading WORDS."""
    block = text[text.index(plan.CARD_START):text.index(plan.CARD_END)]
    found = [l for l in block.splitlines() if l.startswith("- ") and words in l]
    assert len(found) == 1, f"{k}: expected one bullet for “{words}”, found {len(found)}:\n{block}"
    alt = re.search(r'alt="([^"]+)"', found[0])
    url = re.search(r'<a href="([^"]+)">', found[0])
    return alt and alt[1], url and url[1]


# 846.1: in an adopter's repo, the card's Definition of Done finds all tests by the name GitHub shows

def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
    """In an adopter's repo, the card shows Test suite passed when all tests passed.

    Draws a planned card whose PR carries `dokima / full-suite / all tests`, as GitHub names it in an adopter's repo.
    Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
    failed. Proves 846.1."""
    record_property("proves", "846.1")
    st, url = done_verdict(draw([check(ALL_TESTS, n=4)]), "Test suite", "846.1")
    assert (st, url) == ("passed", job(4)), (
        f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
        f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
    st, _ = done_verdict(draw([check(ALL_TESTS, "failure", n=4)]), "Test suite", "846.1")
    assert st == "failed", (f"846.1: all tests failed in an adopter's repo as {ALL_TESTS!r}, but the Definition of "
                            f"Done shows Test suite {st!r}, not failed")


# 846.2: in an adopter's repo, the card's Definition of Done finds Acceptance criteria by the name GitHub shows

def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
    """In an adopter's repo, the card shows Acceptance tests passed when that check passed.

    Draws a planned card whose PR carries `dokima / acceptance-criteria / Acceptance criteria`, as GitHub names it in
    an adopter's repo. Passed, the Definition of Done must show Acceptance tests passed and link that check; failed,
    it must show Acceptance tests failed. Proves 846.2."""
    record_property("proves", "846.2")
    st, url = done_verdict(draw([check(ACCEPTANCE, n=5)]), "Acceptance tests", "846.2")
    assert (st, url) == ("passed", job(5)), (
        f"846.2: Acceptance criteria passed in an adopter's repo as {ACCEPTANCE!r}, but the Definition of Done shows "
        f"Acceptance tests {st!r}, linked to {url!r}, not passed and linked to {job(5)}")
    st, _ = done_verdict(draw([check(ACCEPTANCE, "failure", n=5)]), "Acceptance tests", "846.2")
    assert st == "failed", (f"846.2: Acceptance criteria failed in an adopter's repo as {ACCEPTANCE!r}, but the "
                            f"Definition of Done shows Acceptance tests {st!r}, not failed")


# 846.3: in an adopter's repo, the card finds each criterion's check by the name GitHub shows

def test_adopter_card_shows_a_criterion_passed_by_its_shown_name(record_property, adopter):
    """In an adopter's repo, the card shows a criterion passed when its check passed.

    Draws a planned card whose PR carries criterion 40.1's check as GitHub names it in an adopter's repo,
    `dokima / acceptance-criteria / 40.1 · First thing works`. Passed, the criterion's bullet must show passed and
    link that check; failed, it must show failed. Proves 846.3."""
    record_property("proves", "846.3")
    st, url = criterion_verdict(draw([check(CRITERION, n=1)]), "First thing works", "846.3")
    assert (st, url) == ("passed", job(1)), (
        f"846.3: criterion 40.1's check passed in an adopter's repo as {CRITERION!r}, but its bullet shows {st!r}, "
        f"linked to {url!r}, not passed and linked to {job(1)}")
    st, _ = criterion_verdict(draw([check(CRITERION, "failure", n=1)]), "First thing works", "846.3")
    assert st == "failed", (f"846.3: criterion 40.1's check failed in an adopter's repo as {CRITERION!r}, but its "
                            f"bullet shows {st!r}, not failed")


# 846.4: in an adopter's repo, branch updates find all tests by the name GitHub shows

def test_adopter_pr_whose_all_tests_failed_is_not_brought_up_to_date(record_property, adopter):
    """In an adopter's repo, a pull request whose all tests failed stays un-updated.

    Fakes two pull requests behind main, their checks named as GitHub shows them in an adopter's repo:
    #70, whose `dokima / full-suite / all tests` failed on its head, and #80, whose same check passed. One merge runs;
    #80 must be brought up to date and #70 must get no Update branch call. Proves 846.4."""
    record_property("proves", "846.4")
    gh = GitHub({7: "aa" * 20, 8: "bb" * 20},
                {"aa" * 20: [update_run(ALL_TESTS, "failure")], "bb" * 20: [update_run(ALL_TESTS, "success")]})
    gh.merge(M1)
    updated = [n for n, _ in gh.updates()]
    assert 80 in updated, (f"846.4: #80's all tests passed in an adopter's repo, yet it was not brought up to date; "
                           f"updates {gh.updates()}")
    assert 70 not in updated, (f"846.4: #70's all tests failed in an adopter's repo as {ALL_TESTS!r}, yet it was "
                               f"brought up to date; updates {gh.updates()}")

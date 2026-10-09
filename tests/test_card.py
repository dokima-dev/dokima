import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import card, plan  # noqa: E402

REPO = "o/r"
BODY = ("- [ ] Goal: show a card\n"
        "  - [ ] Done when: first thing works\n"
        "    Verified by: a test that runs the first thing\n"
        "  - [ ] Done when: second thing works\n"
        "    Verified by: another test\n\n"
        "**Not checked:** speed.\n\n"
        "Requested in chat.\n")
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
PR = {"number": 5, "merged": False, "state": "open"}
WORDS = plan.parse(BODY)
PLAN = {"kind": "user_story", "user_story": "Owners see a card.",
        "acceptance_criteria": [{"text": "first thing works", "source": ISSUE["url"]},
                                {"text": "second thing works", "source": ISSUE["url"]}],
        "non_functional": [], "scope": ["dokima/card.py"], "out_of_scope": [],
        "tests": {"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_two"]}}
TESTS = {"tests/test_a.py::test_one": {"verified_by": "a test that runs the first thing", "url": "https://github.com/o/r/blob/a/tests/test_a.py#L1"},
         "tests/test_a.py::test_two": {"verified_by": "another test", "url": "https://github.com/o/r/blob/a/tests/test_a.py#L5"}}
PLANNED = {"role": "planner", "stage": None, "handback": PLAN, "check": {"passed": True}, "run": "https://github.com/o/r/actions/runs/8"}
APPROVED = [PLANNED, {"role": "reviewer", "stage": "plan", "handback": {"verdict": "approve"}, "check": {"passed": True},
                      "run": "https://github.com/o/r/actions/runs/9"}]
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
READY = APPROVED + [{"role": "worker", "stage": None, "handback": {}, "check": {"passed": True},
                     "run": "https://github.com/o/r/actions/runs/10"},
                    {"role": "reviewer", "stage": "pr", "handback": {"verdict": "approve"}, "check": {"passed": True},
                     "run": "https://github.com/o/r/actions/runs/11"}]
BUILDING = {"status": "in_progress", "conclusion": None, "html_url": "https://github.com/o/r/actions/runs/1"}


def run(name, status="completed", conclusion="success", n=7):
    return {"name": name, "status": status, "conclusion": conclusion,
            "html_url": f"https://github.com/o/r/actions/runs/2/job/{n}"}


GREEN = [run("40.1 · first thing works", n=1), run("40.2 · second thing works", n=2), run("All tests", n=3)]


def render(checks=GREEN, worker=DONE, pr=PR, recs=APPROVED, page="issue"):
    found = {"recs": recs, "pr": pr, "check_runs": checks, "reviews": [], "owners": set(), "tests": TESTS, "worker": worker}
    return card.render(REPO, ISSUE, found, page=page)


def status(body):
    """The card's status line: its first line, as the card has no summary sentence here."""
    lines = [l for l in body.splitlines()[1:] if l.strip()]
    return lines[0]


def links(body):
    """The card's links row."""
    return next(l for l in body.splitlines() if l.startswith("[latest run]"))


def icon(name):
    return card.icon(REPO, name)


def test_title_asks_for_approval_when_all_checks_passed(record_property):
    """Approved work with every check passed says Ready for approval on its status line."""
    record_property("proves", "58.1")
    assert "Ready for approval" in status(render(recs=READY))


def test_links_row():
    # The field icons code draws in front of a field (issue #234) are not part of the links.
    assert re.sub(r"<img [^>]*>\s*", "", links(render())) == ("[latest run](https://github.com/o/r/actions/runs/1) · [issue #40](https://github.com/o/r/issues/40)"
                                        " · [PR #5](https://github.com/o/r/pull/5)"
                                        " · [files changed](https://github.com/o/r/pull/5/files)")


def test_latest_run_links_the_worker_running_or_finished(record_property):
    record_property("proves", "76.1")
    for worker in (BUILDING, DONE):
        row = links(render(worker=worker))
        assert row.startswith("[latest run](https://github.com/o/r/actions/runs/1)")
        assert "live run" not in row


def test_unrelated_running_check_is_ignored(record_property):
    record_property("proves", "76.2")
    body = render(checks=GREEN + [run("card", status="in_progress", conclusion=None, n=9)], recs=READY)
    assert "Ready for approval" in status(body)
    assert "job/9" not in body


def test_no_footer_and_no_gap(record_property):
    record_property("proves", "74.3")
    body = render()
    assert "Built by the card workflow" not in body
    lines = body.splitlines()
    shown = [i for i, line in enumerate(lines) if "Verified by" in line]
    assert shown
    for i in shown:
        assert lines[i].startswith("  - ")
        above = next(line for line in reversed(lines[:i]) if line.startswith("- "))
        assert "first thing works" in above or "second thing works" in above


def test_card_says_criteria_and_is_read_back_as_the_plan(record_property):
    record_property("proves", "74.5")
    body = render()
    assert "Done when" not in body and "first thing works" in body
    text = plan.as_text(40, "T", WORDS)
    assert "Criterion 40.1: first thing works" in text and "Done when" not in text


def test_same_card_on_issue_and_pr_and_only_icons_change(record_property):
    record_property("proves", "67.6")
    assert render(checks=[], pr=None) != render()
    assert card.pr_body(render(), "Closes #40.\n\nSome prose.") == render() + "\n\nCloses #40"
    src = open(os.path.join(os.path.dirname(__file__), "..", "dokima", "card.py")).read()
    assert 'f"repos/{repo}/pulls/{pr_number}", "-F", "body=@pr.md"' in src
    yml = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "card.yml")).read()
    assert "types: [opened, edited]" in yml and "github.event.sender.type != 'Bot'" in yml


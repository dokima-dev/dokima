"""Every issue the reviewer files names the open issues it searched and its verdict (#622).

Story 2 of #615. Before an issue is filed from a raise, the owner wants the reviewer to record two decisions in its
JSON hand-back, and code to reject a filing without them: the open issues it searched for the same cause, and its
verdict, one of symptom (of a known cause), root cause (found) or new. The verdict and its evidence then show on the
filed issue, so the owner sees why it was filed.

What the code these tests run must do, as the plan pins it:
- A reviewer's own issue raise carries "searched", a non-empty list of open issue numbers from its pack (#621 already
  checks each number is in the pack), and "verdict", exactly one of "symptom", "root cause" or "new".
- A review that answers done to an issue the planner or the worker raised files that issue, so its answer carries the
  same two fields; an answer of disagree files nothing and needs neither.
- The checks a review's run does (`agent check review FILE PLAN N`, then `agent check-round reviewer FILE PACK`) reject
  (exit 1) a review that files an issue without them, naming the missing or wrong field, and never crash. A review
  that files nothing needs neither field.
- The issue code files shows the verdict on a line naming it ("Symptom of a known cause", "Root cause found" or "New"),
  the searched issues as #N on a line naming them, and the raise's evidence.

The checks run as subprocesses against a pack built from a faked GitHub (see test_reviewer_open_issues). The filing
runs the real `agent next` against the fake GitHub of test_reviewer_settles.
"""
import json
import os
import re

import pytest

from tests.test_raise_handbacks import FOUND, review
from tests.test_reviewer_open_issues import both_checks, reviewer_pack
from tests import test_reviewer_settles as settles

SEARCHED = [12, 15]  # both open issues in the faked pack
LINKS = {"symptom": {"cause": 12}, "root cause": {"symptoms": SEARCHED}, "new": {}}  # what each verdict names (#623)
NAMES = {"symptom": "symptom of a known cause", "root cause": "root cause found", "new": "new"}
WORKER_ISSUE = {"kind": "issue", "label": "Docs", "text": "The wiki page on labels is out of date.",
                "evidence": "wiki/Labels.md", "raised_by": "worker", "id": "W1", "to": "reviewer"}


def own(**fields):
    """A code review raising one issue of its own, with these fields added."""
    return review("approve", "pr", raises=[{**FOUND, **fields}])


def confirming(word="done", **fields):
    """A code review answering the worker's issue W1, with these extra fields on the answer."""
    return review("approve", "pr", answers=[{"raise": "W1", "answer": word, "why": "It is real.", **fields}])


def with_worker_issue(pack):
    """The pack, now listing the worker's issue W1 for the reviewer to confirm."""
    json.dump([WORKER_ISSUE], open(os.path.join(pack, "open_blockers.json"), "w"))
    return pack


def rejected(tmp_path, handback, pack, field, criterion, what):
    """Assert the review's checks reject it, naming the field, without a crash."""
    code, out = both_checks(tmp_path, handback, pack)
    assert "Traceback" not in out, f"{criterion}: the check crashed on {what}:\n{out[-600:]}"
    assert code == 1, f"{criterion}: {what} passed the review's checks"
    assert field in out, f"{criterion}: the rejection of {what} does not name {field}:\n{out}"


def passed(tmp_path, handback, pack, criterion, what):
    """Assert the review's checks pass it."""
    code, out = both_checks(tmp_path, handback, pack)
    assert code == 0, f"{criterion}: {what} was rejected:\n{out}"


# 622.1 -----------------------------------------------------------------------------------------------------------------

def test_a_review_filing_its_own_issue_without_the_issues_it_searched_is_rejected(record_property, tmp_path,
                                                                                 monkeypatch):
    """A review filing an issue without naming the open issues it searched is rejected.

    Builds the code review's pack, then runs a review's checks: a review raising an issue with its verdict and the
    issues it searched passes, and so does a review raising no issue at all. The same issue with no searched field is
    rejected naming searched, and so is one whose searched list is empty.

    Proves 622.1."""
    record_property("proves", "622.1")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    passed(tmp_path, own(searched=SEARCHED, verdict="new"), pack, "622.1", "a review naming the issues it searched")
    passed(tmp_path, review("approve", "pr"), pack, "622.1", "a review that files no issue")
    rejected(tmp_path, own(verdict="new"), pack, "searched", "622.1", "an issue raise with no searched issues")
    rejected(tmp_path, own(searched=[], verdict="new"), pack, "searched", "622.1", "an issue raise searching none")


def test_a_review_confirming_a_workers_issue_without_the_issues_it_searched_is_rejected(record_property, tmp_path,
                                                                                       monkeypatch):
    """A review confirming another agent's issue must name the open issues it searched.

    The pack lists the worker's issue W1 for the reviewer to confirm. A review answering it done with its verdict and
    the issues it searched passes; answering it disagree files nothing, so it passes with neither. Answering it done
    with no searched field is rejected naming searched.

    Proves 622.1."""
    record_property("proves", "622.1")
    pack = with_worker_issue(reviewer_pack(monkeypatch, tmp_path, "pr"))
    passed(tmp_path, confirming(searched=SEARCHED, verdict="new"), pack, "622.1",
           "a review confirming W1 with the issues it searched")
    passed(tmp_path, confirming("disagree"), pack, "622.1", "a review disagreeing with W1, filing nothing")
    rejected(tmp_path, confirming(verdict="new"), pack, "searched", "622.1",
             "a review confirming W1 with no searched issues")


# 622.2 -----------------------------------------------------------------------------------------------------------------

def test_a_review_filing_its_own_issue_without_one_of_the_three_verdicts_is_rejected(record_property, tmp_path,
                                                                                    monkeypatch):
    """A review filing an issue without one of the three verdicts is rejected.

    Builds the code review's pack, then runs a review's checks on an issue raise naming the issues it searched: each
    of the three verdicts passes, a symptom naming its cause and a root cause its symptoms (#623). No verdict at all is rejected naming verdict, and so is a verdict outside the
    three, such as maybe.

    Proves 622.2."""
    record_property("proves", "622.2")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    for verdict in NAMES:
        passed(tmp_path, own(searched=SEARCHED, verdict=verdict, **LINKS[verdict]), pack, "622.2",
               f"the verdict {verdict!r}")
    rejected(tmp_path, own(searched=SEARCHED), pack, "verdict", "622.2", "an issue raise with no verdict")
    rejected(tmp_path, own(searched=SEARCHED, verdict="maybe"), pack, "verdict", "622.2", "the verdict 'maybe'")


def test_a_review_confirming_a_workers_issue_without_a_verdict_is_rejected(record_property, tmp_path, monkeypatch):
    """A review confirming another agent's issue must give one of the three verdicts.

    The pack lists the worker's issue W1 for the reviewer to confirm. Answering it done with the issues searched and
    the verdict root cause, naming its symptoms (#623), passes; with no verdict, or the verdict maybe, it is rejected naming verdict.

    Proves 622.2."""
    record_property("proves", "622.2")
    pack = with_worker_issue(reviewer_pack(monkeypatch, tmp_path, "pr"))
    passed(tmp_path, confirming(searched=SEARCHED, verdict="root cause", symptoms=SEARCHED), pack, "622.2",
           "a review confirming W1 as a root cause")
    rejected(tmp_path, confirming(searched=SEARCHED), pack, "verdict", "622.2", "a review confirming W1 with no verdict")
    rejected(tmp_path, confirming(searched=SEARCHED, verdict="maybe"), pack, "verdict", "622.2",
             "a review confirming W1 with the verdict 'maybe'")


# 622.3 -----------------------------------------------------------------------------------------------------------------

def shows(body, verdict, searched, evidence):
    """What a filed issue's body lacks: its verdict, searched issues or evidence."""
    lines = body.splitlines()
    problems = []
    said = [l for l in lines if re.search(r"verdict", l, re.I)]
    if not any(re.search(rf"\b{NAMES[verdict]}\b", l, re.I) for l in said):
        problems.append(f"no line shows the verdict {NAMES[verdict]!r} (verdict lines: {said})")
    looked = [l for l in lines if re.search(r"searched", l, re.I)]
    if not any(all(re.search(rf"(?:#|/issues/){n}\b", l) for n in searched) for l in looked):
        problems.append(f"no line shows the searched issues {searched} (searched lines: {looked})")
    if evidence not in body:
        problems.append(f"the evidence {evidence!r} is missing")
    return problems


def test_the_reviewers_own_filed_issue_shows_its_verdict_searched_issues_and_evidence(tmp_path, record_property):
    """An issue the reviewer files shows its verdict, the issues it searched and its evidence.

    A code review raises an issue with the verdict new, searched issues #12 and #15, and its evidence. Its run files
    the issue on a faked GitHub; the new issue's body has a line showing the verdict New, a line showing #12 and #15
    as searched, and the evidence.

    Proves 622.3."""
    record_property("proves", "622.3")
    hub = settles.Hub(tmp_path)
    for r in (settles.plan_rec(), settles.plan_review_rec(), settles.work_rec()):
        hub.post(r)
    found = {**settles.issue_raise("reviewer", "R1"), "searched": SEARCHED, "verdict": "new"}
    hub.run(settles.code_review_rec("approve", raised=[found]))
    created = hub.created()
    assert len(created) == 1, f"622.3: the reviewer's issue should file exactly one issue, filed {created}"
    (_, filed), = created.items()
    problems = shows(filed["body"], "new", SEARCHED, settles.FOUND_EVIDENCE)
    assert not problems, f"622.3: the filed issue does not show why it was filed: {problems}\n{filed['body']}"


def test_a_confirmed_workers_issue_shows_the_reviewers_verdict_and_searched_issues(tmp_path, record_property):
    """An issue the reviewer confirms for the worker shows the reviewer's verdict and search.

    The worker raises an issue with its evidence; the code review answers it done with the verdict root cause and
    searched issues #12 and #15. The issue filed on a faked GitHub shows the verdict Root cause found, #12 and #15 as
    searched, and the worker's evidence.

    Proves 622.3."""
    record_property("proves", "622.3")
    hub = settles.Hub(tmp_path)
    for r in (settles.plan_rec(), settles.plan_review_rec()):
        hub.post(r)
    hub.run(settles.work_rec([settles.issue_raise("worker", "W1")]))
    yes = {**settles.answer("W1", "done", "Real: closed PRs stay in Review."), "searched": SEARCHED,
           "verdict": "root cause"}
    hub.run(settles.code_review_rec("approve", [yes]))
    created = hub.created()
    assert len(created) == 1, f"622.3: the confirmed worker issue should file exactly one issue, filed {created}"
    (_, filed), = created.items()
    problems = shows(filed["body"], "root cause", SEARCHED, settles.FOUND_EVIDENCE)
    assert not problems, f"622.3: the filed issue does not show why it was filed: {problems}\n{filed['body']}"

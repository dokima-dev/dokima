"""A symptom joins its cause as a comment; a root cause files one issue (#623).

Story 3 of #615. The reviewer already records, on every issue it files, the open issues it searched and its verdict:
symptom, root cause or new (#622). This story makes the first two verdicts do what the owner asked:
- A raise judged a symptom names its cause, an open issue from the pack, in "cause". Code posts it as a comment on
  that issue, with the raise's words and evidence, and files no new issue. A symptom naming no cause is rejected.
- A raise judged a root cause names the open issues it explains in "symptoms". Code files one issue whose title starts
  "Root cause found", in place of the raise, and its body names each symptom as #N on a line naming them, so GitHub
  links both ways. No symptom becomes a sub-issue. A root cause naming no symptoms is rejected.
The same holds for an issue the planner or the worker raised that the reviewer answers done: the fields are on its
answer, as #622 put searched and verdict there.

The checks run as subprocesses against a pack built from a faked GitHub (see test_reviewer_open_issues), whose open
issues include #12 and #15. The filing runs the real `agent next` against the fake GitHub of test_reviewer_settles,
with #12 and #15 added as open issues.
"""
import json
import os
import re

from tests.test_raise_handbacks import FOUND, review
from tests.test_reviewer_open_issues import both_checks, reviewer_pack
from tests import test_reviewer_settles as settles

CAUSE = 12
SYMPTOMS = [12, 15]
SEARCHED = [12, 15]
WORKER_ISSUE = {"kind": "issue", "label": "Docs", "text": "The wiki page on labels is out of date.",
                "evidence": "wiki/Labels.md", "raised_by": "worker", "id": "W1", "to": "reviewer"}


def hub_with_open_issues(tmp_path):
    """The fake GitHub of test_reviewer_settles, also holding open issues #12 and #15."""
    hub = settles.Hub(tmp_path)
    s = hub.state()
    for n, title in ((12, "Slow calls time out"), (15, "Paint the door")):
        s["issues"][str(n)] = {"title": title, "body": "An open issue.", "labels": [], "comments": []}
    json.dump(s, open(os.path.join(hub.dir, "state.json"), "w"))
    return hub


def reviewed(hub, **fields):
    """After a build, a code review raises one issue with these fields."""
    for r in (settles.plan_rec(), settles.plan_review_rec(), settles.work_rec()):
        hub.post(r)
    found = {**settles.issue_raise("reviewer", "R1"), "searched": SEARCHED, **fields}
    hub.run(settles.code_review_rec("approve", raised=[found]))


def confirmed(hub, **fields):
    """The worker raises an issue; the code review answers it done with these fields."""
    for r in (settles.plan_rec(), settles.plan_review_rec()):
        hub.post(r)
    hub.run(settles.work_rec([settles.issue_raise("worker", "W1")]))
    yes = {**settles.answer("W1", "done", "Real: closed PRs stay in Review."), "searched": SEARCHED, **fields}
    hub.run(settles.code_review_rec("approve", [yes]))


def comments_on(hub, n):
    """The bodies of every comment on issue #n in the fake GitHub."""
    return [c.get("body") or "" for c in hub.state()["issues"][str(n)].get("comments", [])]


def sub_issue_calls(hub):
    """Every call to GitHub that made a sub-issue."""
    return [c for c in hub.state().get("calls", []) if any("sub_issue" in str(x) for x in c)]


def symptoms_lines(body):
    """The lines of a body that name symptoms."""
    return [l for l in body.splitlines() if re.search(r"symptom", l, re.I)]


def own(**fields):
    """A code review raising one issue of its own, with these fields added."""
    return review("approve", "pr", raises=[{**FOUND, **fields}])


def check(tmp_path, handback, pack):
    """The review's two checks on this hand-back: exit code and output, asserting no crash."""
    code, out = both_checks(tmp_path, handback, pack)
    assert "Traceback" not in out, f"the review's check crashed:\n{out[-600:]}"
    return code, out


# 623.1 -----------------------------------------------------------------------------------------------------------------

def test_a_symptom_becomes_a_comment_on_its_cause_and_files_no_issue(tmp_path, record_property):
    """A symptom becomes a comment on its cause, with its evidence, and files no issue.

    A code review raises an issue judged a symptom of open issue #12. Its run on a faked GitHub files no issue, and
    #12 gets a comment holding the raise's words and its evidence.

    Proves 623.1."""
    record_property("proves", "623.1")
    hub = hub_with_open_issues(tmp_path)
    reviewed(hub, verdict="symptom", cause=CAUSE)
    assert hub.created() == {}, f"623.1: a symptom was filed as a new issue: {hub.created()}"
    said = [c for c in comments_on(hub, CAUSE) if settles.FOUND_EVIDENCE in c and settles.FOUND in c]
    assert said, f"623.1: cause #{CAUSE} has no comment with the symptom's words and evidence: {comments_on(hub, CAUSE)}"


def test_a_confirmed_workers_symptom_becomes_a_comment_on_its_cause(tmp_path, record_property):
    """A worker's issue confirmed as a symptom joins its cause as a comment too.

    The worker raises an issue; the code review answers it done, judged a symptom of #12. No issue is filed, and #12
    gets a comment with the worker's words and evidence.

    Proves 623.1."""
    record_property("proves", "623.1")
    hub = hub_with_open_issues(tmp_path)
    confirmed(hub, verdict="symptom", cause=CAUSE)
    assert hub.created() == {}, f"623.1: a confirmed symptom was filed as a new issue: {hub.created()}"
    said = [c for c in comments_on(hub, CAUSE) if settles.FOUND_EVIDENCE in c and settles.FOUND in c]
    assert said, f"623.1: cause #{CAUSE} has no comment with the symptom's words and evidence: {comments_on(hub, CAUSE)}"


def test_a_symptom_naming_no_cause_is_rejected(record_property, tmp_path, monkeypatch):
    """A symptom naming no cause is rejected; one naming its cause passes.

    Builds the code review's pack, then runs the review's checks on an issue raise judged a symptom: with cause #12,
    an open issue in the pack, it passes; with no cause it is rejected, and the rejection names cause.

    Proves 623.1."""
    record_property("proves", "623.1")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    code, out = check(tmp_path, own(searched=SEARCHED, verdict="symptom", cause=CAUSE), pack)
    assert code == 0, f"623.1: a symptom naming its cause #{CAUSE} was rejected:\n{out}"
    code, out = check(tmp_path, own(searched=SEARCHED, verdict="symptom"), pack)
    assert code == 1, "623.1: a symptom naming no cause passed the review's checks"
    assert "cause" in out, f"623.1: the rejection of a symptom with no cause does not name cause:\n{out}"


# 623.2 -----------------------------------------------------------------------------------------------------------------

def test_a_root_cause_files_one_issue_marked_root_cause_found(tmp_path, record_property):
    """A root cause files exactly one issue, its title marked Root cause found.

    A code review raises an issue judged a root cause of #12 and #15. Its run on a faked GitHub files exactly one
    issue, and its title starts with Root cause found. Beside it, an issue judged new is filed as today, titled with
    the raise's first sentence, so the mark means only a root cause.

    Proves 623.2."""
    record_property("proves", "623.2")
    hub = hub_with_open_issues(tmp_path / "new")
    reviewed(hub, verdict="new")
    (_, filed), = hub.created().items()
    assert filed["title"].strip().rstrip(".") == settles.FOUND_TITLE, \
        f"623.2: an issue judged new should keep the raise's title {settles.FOUND_TITLE!r}, got {filed['title']!r}"
    hub = hub_with_open_issues(tmp_path / "root")
    reviewed(hub, verdict="root cause", symptoms=SYMPTOMS)
    created = hub.created()
    assert len(created) == 1, f"623.2: a root cause should file exactly one issue, filed {created}"
    (_, filed), = created.items()
    assert re.match(r"\s*root cause found\b", filed["title"], re.I), \
        f"623.2: the root cause issue is not marked root cause found in its title: {filed['title']!r}"


def test_a_confirmed_workers_root_cause_files_one_marked_issue(tmp_path, record_property):
    """A worker's issue confirmed as a root cause files one marked issue.

    The worker raises an issue; the code review answers it done, judged a root cause of #12 and #15. Exactly one
    issue is filed, and its title starts with Root cause found.

    Proves 623.2."""
    record_property("proves", "623.2")
    hub = hub_with_open_issues(tmp_path)
    confirmed(hub, verdict="root cause", symptoms=SYMPTOMS)
    created = hub.created()
    assert len(created) == 1, f"623.2: a confirmed root cause should file exactly one issue, filed {created}"
    (_, filed), = created.items()
    assert re.match(r"\s*root cause found\b", filed["title"], re.I), \
        f"623.2: the root cause issue is not marked root cause found in its title: {filed['title']!r}"


# 623.3 -----------------------------------------------------------------------------------------------------------------

def test_the_root_cause_issue_links_each_symptom_and_makes_no_sub_issue(tmp_path, record_property):
    """The root cause issue links each symptom, and none becomes a sub-issue.

    A code review raises an issue judged a root cause of #12 and #15. The filed issue's body has a line naming its
    symptoms that links both #12 and #15, and no call to GitHub made a sub-issue.

    Proves 623.3."""
    record_property("proves", "623.3")
    hub = hub_with_open_issues(tmp_path)
    reviewed(hub, verdict="root cause", symptoms=SYMPTOMS)
    created = hub.created()
    assert len(created) == 1, f"623.3: a root cause should file exactly one issue, filed {created}"
    (_, filed), = created.items()
    lines = symptoms_lines(filed["body"])
    assert any(all(re.search(rf"(?:#|/issues/){n}\b", l) for n in SYMPTOMS) for l in lines), \
        f"623.3: no line of the root cause issue links its symptoms {SYMPTOMS} (symptom lines: {lines})"
    assert sub_issue_calls(hub) == [], f"623.3: a symptom was made a sub-issue: {sub_issue_calls(hub)}"


def test_a_root_cause_naming_no_symptoms_is_rejected(record_property, tmp_path, monkeypatch):
    """A root cause naming no symptoms is rejected; one naming them passes.

    Builds the code review's pack, then runs the review's checks on an issue raise judged a root cause: naming #12
    and #15, open issues in the pack, as its symptoms it passes; naming none it is rejected, naming symptoms.

    Proves 623.3."""
    record_property("proves", "623.3")
    pack = reviewer_pack(monkeypatch, tmp_path, "pr")
    code, out = check(tmp_path, own(searched=SEARCHED, verdict="root cause", symptoms=SYMPTOMS), pack)
    assert code == 0, f"623.3: a root cause naming its symptoms {SYMPTOMS} was rejected:\n{out}"
    code, out = check(tmp_path, own(searched=SEARCHED, verdict="root cause"), pack)
    assert code == 1, "623.3: a root cause naming no symptoms passed the review's checks"
    assert "symptoms" in out, f"623.3: the rejection of a root cause with no symptoms does not name symptoms:\n{out}"

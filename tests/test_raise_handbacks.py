"""Every agent's hand-back raises and answers through two fields, and nothing raised is skipped (#300).

The owner wants the planner, the worker and the reviewer to raise what they judge only as raises (a question, a
blocker or an issue, dokima/raises.py from #298) and to answer what was raised to them only as answers, with every
old field for this gone; each agent starts with the exact list it must answer, and code rejects a hand-back that
skips one; the river routes by raises; and on autopilot the reviewer may answer a planner's question for the owner
only with the owner's own words, checked by code.

What the code these tests run must do, as the plan pins it:
- The old fields are questions, concerns, replies, suspect_tests, outside_scope, blockers, notes, assumptions,
  issues_found, outside_plan and resolved. A planner hand-back (`python3 -m dokima.planner check N OUT`, a story or a
  split) or a worker or reviewer hand-back (`python3 -m dokima.agent check work|review FILE PLAN N`) holding any of
  them, even empty, is rejected with a reason naming each one it holds. Its "raises" are checked with
  raises.check_raises for its role; "raises" and "answers" are lists and may be left out when empty.
- A review that blocks raises at least one blocker; one that approves raises none.
- `python3 -m dokima.agent record ROLE STAGE OUT CHECK PASSED LOGS` stamps the hand-back's raises in record.json
  (raises.stamp): each gets "raised_by" and an ID that no raise or old blocker in the records of $PACK/in/ has.
- `agent.pack(repo, n, role, stage, dest)` writes dest/open_blockers.json: exactly the raises still open on the issue
  whose raises.sent_to is that role, oldest first, each as stamped. A raise is open from the passed record that
  raised it until a passed record answers its ID. Before this change a review listed "blockers"; the open ones of
  the newest review at each stage (unless it approved, and unless a later record answered or replied to them by ID)
  are listed as raises {"kind": "blocker", "to": its fixer, "raised_by": "reviewer", "id": its old ID, "text": holding
  its problem}.
- `python3 -m dokima.agent check-round ROLE FILE PACK` exits 1 and names the ID of every raise in
  PACK/open_blockers.json that the hand-back's "answers" leave unanswered, and rejects an answer that is not done or
  disagree with a why; it exits 0 when every one is answered. A reviewer may also answer a question for the owner
  still open in the records of PACK/in/: that answer carries "words" (the owner's words), "source" (where they said
  them: the issue's link, one of its comments' links or AGENTS.md) and "changes" (true or false: whether the reading
  changes how the system works or what it costs), or the check rejects it.
- `agent.next_step` routes a review by its raises: any blocker for the planner starts the planner, blockers only for
  the worker start the worker, and any question or blocker for the owner stops; a planner's blocker for the owner
  stops, and its question stops off autopilot and goes to the plan reviewer on autopilot. On autopilot, a plan review
  lets the plan go on only when it answered each of the plan's questions done, with changes false and with words
  the owner really said where the source says; otherwise it stops and names the question left.
- dokima/roles/planner.md, worker.md and reviewer.md each hold one section headed exactly "# Raising and answering",
  running to the next line that starts with "# " or the end of the file, word for word the same in all three.
"""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, raises  # noqa: E402
from tests.test_plan_check import FEATURE, STORY as PLAN_STORY, check  # noqa: E402,F401

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OLD = ("questions", "concerns", "replies", "suspect_tests", "outside_scope", "blockers", "notes", "assumptions",
       "issues_found", "outside_plan", "resolved")
OWNER = "owner"
ISSUE = "https://github.com/o/r/issues/9"
LINKS = {"blocked_by": [], "blocks": [], "relates_to": []}
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": ISSUE}, {"text": "b", "source": ISSUE}],
         "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
         "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"]}, "links": LINKS}
WORK = {"summary": "Built the job id.", "criteria": {"9.1": "x.py, a()", "9.2": "x.py, b()"},
        "evidence": "pytest -q: 2 passed"}
ASKS = [{"ask": "Paint the door blue", "source": ISSUE, "criterion": "9.1"}]
APPROVE = {"previous_step": {"did": ["Planned one story."], "decided": [], "open": []}, "verdict": "approve",
           "summary": "Every promise has a proof.", "asks": ASKS}

# Raises as an agent writes them, and as code stamps them on the issue.
DOUBT = {"kind": "question", "to": "owner", "label": "Doubt about the ask",
         "text": "Is this already fixed? The board draws the column from the record since #339.",
         "evidence": "dokima/board.py, column(), line 120"}
TO_PLANNER = {"kind": "blocker", "to": "planner", "label": "Weak test", "text": "The test for 9.1 passes on a stub.",
              "evidence": "tests/test_x.py::test_a"}
TO_WORKER = {"kind": "blocker", "to": "worker", "label": "Criterion 9.2", "text": "The job id is never returned.",
             "evidence": "dokima/x.py line 4"}
FOUND = {"kind": "issue", "label": "Docs", "text": "The README still names the old command.", "evidence": "README.md"}


def stamped(r, by, rid):
    """A raise as code stamps it on the issue."""
    return {**r, "raised_by": by, "id": rid}


P1 = stamped({"kind": "question", "to": "owner", "text": "Should a failed run move to Needs you? Assumed: it does."},
             "planner", "P1")
P2 = stamped({"kind": "question", "to": "owner", "text": "Should the card name the step? Assumed: it does."},
             "planner", "P2")
P3 = stamped(FOUND, "planner", "P3")
R1 = stamped(TO_PLANNER, "reviewer", "R1")
W1 = stamped({"kind": "blocker", "to": "planner", "text": "Test 9.2 can never pass: it reads a file nothing writes.",
              "evidence": "tests/test_x.py::test_b"}, "worker", "W1")
R2 = stamped(TO_WORKER, "reviewer", "R2")
R3 = stamped({"kind": "blocker", "to": "planner", "text": "The second test proves a neighbour of the promise."},
             "reviewer", "R3")
R4 = stamped({"kind": "question", "to": "owner", "text": "Is twenty seconds the right timeout?"}, "reviewer", "R4")
WX = stamped({"kind": "blocker", "to": "planner", "text": "A raise in a hand-back code rejected."}, "worker", "W9")


def rec(role, stage="", handback=None, passed=True):
    """A record as the record step builds it."""
    return {"role": role, "stage": stage or None, "run_id": "1", "run": "https://x/run/1", "handback": handback or {},
            "check": {"passed": passed, "problems": [] if passed else ["rejected"]}}


def review(verdict="block", stage="plan", **more):
    """A review hand-back with the new fields."""
    return {**APPROVE, "verdict": verdict, "summary": f"The review {verdict}s.", **more,
            **({} if stage == "plan" else {"asks": []})}


def comment(r, who="dokima-runtime", url=None):
    """A comment as GitHub returns it, carrying a record rendered by code."""
    c = {"author": {"login": who}, "body": agent.render(r), "createdAt": "2026-10-09T10:00:00Z", "where": "issue #9"}
    if url:
        c["url"] = url
    return c


def env(**more):
    """The environment a workflow step runs in, with the repo on the path."""
    e = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
         "GITHUB_RUN_ID": "42", **more}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE"):
        if k not in more:
            e.pop(k, None)
    return e


def run_agent(*args, **more):
    """Run `python3 -m dokima.agent ARGS` from the repo root; return (exit code, stdout + stderr)."""
    p = subprocess.run([sys.executable, "-m", "dokima.agent", *args], cwd=ROOT, env=env(**more), capture_output=True,
                       text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr


def check_handback(tmp_path, kind, handback):
    """Run `agent check work|review FILE PLAN 9` on the hand-back, the plan being STORY."""
    d = tempfile.mkdtemp(dir=tmp_path)
    f, p = os.path.join(d, f"{kind}.json"), os.path.join(d, "plan.json")
    json.dump(handback, open(f, "w"))
    json.dump(STORY, open(p, "w"))
    return run_agent("check", kind, f, p, "9")


def fake_github(monkeypatch, recs, body="B"):
    """Fake GitHub so issue #9's conversation holds these records, all posted by the bot."""
    comments = [comment(r) for r in recs]

    def gh(*args):
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": 9, "title": "T", "body": body, "comments": comments})
        if args[:2] == ("pr", "list"):
            return "[]"
        if args[:2] == ("run", "download"):
            return ""  # the worker's session log, which a code review's pack downloads
        if args[0] == "api" and "/parent" in args[1]:
            raise subprocess.CalledProcessError(1, "gh", stderr="HTTP 404: Not Found")
        if args[0] == "api" and args[1].lstrip("/").startswith("repos/o/r/issues"):
            return "[]"
        raise AssertionError(f"unexpected gh call {args}")
    monkeypatch.setattr(agent, "gh", gh)


def listed(monkeypatch, tmp_path, recs, role, stage=""):
    """The open_blockers.json a starting pack for `role` holds, built from these records."""
    fake_github(monkeypatch, recs)
    dest = tempfile.mkdtemp(dir=tmp_path)
    agent.pack("o/r", 9, role, stage, dest)
    path = os.path.join(dest, "open_blockers.json")
    assert os.path.exists(path), "300.2: the starting pack holds no open_blockers.json listing the open raises"
    return json.load(open(path))


# 300.1: two fields, no old ones; a doubt about the ask is a question with its evidence.

def test_every_old_field_is_rejected_by_name_in_every_agents_hand_back(record_property, tmp_path, check):
    """The checker rejects every old field in a planner, worker or reviewer hand-back, naming it.

    First checks good hand-backs that raise and answer only through raises and answers pass: a planner's story and
    split raising a question, a blocker and an issue, a worker raising a blocker for the planner, and a review raising
    to the worker and the owner. Then adds each of the eleven old fields, once with something in it and once empty,
    to each agent's hand-back, and checks each is rejected with a reason naming that field.

    Proves 300.1."""
    record_property("proves", "300.1")
    plan_raises = [DOUBT, FOUND]
    goods = {"story": {**PLAN_STORY, "raises": plan_raises, "answers": []},
             "split": {**FEATURE, "raises": plan_raises, "answers": []}}
    for name, p in goods.items():
        rc, why = check({"plan.json": p}, "300.1")
        assert rc == 0, f"300.1: the planner's {name} raising a question and an issue was rejected: {why}"
    good_work = {**WORK, "raises": [TO_PLANNER, FOUND], "answers": [{"raise": "R2", "answer": "done", "why": "Fixed."}]}
    good_review = review("block", "pr", raises=[TO_WORKER, {**DOUBT, "label": "Timeout"}, FOUND],
                         answers=[{"raise": "W1", "answer": "disagree", "why": "The test writes the file first."}])
    for kind, h in (("work", good_work), ("review", good_review)):
        code, out = check_handback(tmp_path, kind, h)
        assert code == 0, f"300.1: a good {kind} hand-back raising and answering through the two fields was rejected:\n{out}"
    filled = {"questions": [{"question": "Q?", "assumption": "A."}], "concerns": [{"text": "t", "evidence": "e"}],
              "replies": [{"blocker": "B1", "answer": "fixed", "why": "w"}],
              "suspect_tests": [{"test": "tests/test_x.py::test_a", "evidence": "e"}],
              "outside_scope": [{"file": "a.py", "why": "w"}],
              "blockers": [{"id": "B1", "criterion": "9.1", "test": None, "problem": "p", "evidence": "e", "fix": "f",
                            "fixer": "worker"}],
              "notes": [{"text": "t", "evidence": "e"}],
              "assumptions": [{"question": "Q?", "accepted": False, "changes": False, "why": "w"}],
              "issues_found": [{"title": "t", "why": "w", "evidence": "e"}],
              "outside_plan": [{"file": "a.py", "change": "c"}], "resolved": ["B0"]}
    for field in OLD:
        for value in (filled[field], []):
            how = "empty" if value == [] else "filled"
            for name, p in goods.items():
                rc, why = check({"plan.json": {**p, field: value}}, "300.1")
                assert rc == 1 and field in why, \
                    f"300.1: the planner's {name} with {field} ({how}) was not rejected naming {field}: {rc} {why!r}"
            for kind, h in (("work", good_work), ("review", good_review)):
                code, out = check_handback(tmp_path, kind, {**h, field: value})
                assert code == 1 and field in out, \
                    f"300.1: a {kind} hand-back with {field} ({how}) was not rejected naming {field}: exit {code}\n{out}"


def test_raises_in_every_hand_back_are_checked_against_the_kinds_and_the_table(record_property, tmp_path, check):
    """A raise of an unknown kind or outside the table is rejected for every agent.

    Hands back a planner's story with a note, a worker raising a question for the owner, and a review raising a
    concern, and checks each is rejected; the same hand-backs with the raise put right pass.

    Proves 300.1."""
    record_property("proves", "300.1")
    rc, why = check({"plan.json": {**PLAN_STORY, "raises": [{**FOUND, "kind": "note"}]}}, "300.1")
    assert rc == 1 and "note" in why, f"300.1: the planner's raise of kind note was not rejected: {rc} {why!r}"
    rc, why = check({"plan.json": {**PLAN_STORY, "raises": [FOUND]}}, "300.1")
    assert rc == 0, f"300.1: the planner's issue raise was rejected: {why!r}"
    for kind, base, bad, good in (
            ("work", WORK, {**DOUBT}, TO_PLANNER),
            ("review", review("approve", "pr"), {**FOUND, "kind": "concern"}, FOUND)):
        code, out = check_handback(tmp_path, kind, {**base, "raises": [bad]})
        assert code == 1, f"300.1: a {kind} hand-back raising {bad['kind']} for {bad.get('to')} passed:\n{out}"
        code, out = check_handback(tmp_path, kind, {**base, "raises": [good]})
        assert code == 0, f"300.1: a {kind} hand-back raising a {good['kind']} it may raise was rejected:\n{out}"


def test_a_doubt_about_the_ask_reaches_you_as_a_question_with_its_evidence(record_property, tmp_path, check):
    """A doubt about the ask reaches you as a question with its evidence.

    Hands back a plan whose doubt is a question for the owner carrying its evidence: the check passes it. Runs the
    record step on it: the record keeps the question with its evidence, and the planner's comment, above its folds,
    shows the question for you with the evidence. Off autopilot the river then stops for the owner.

    Proves 300.1."""
    record_property("proves", "300.1")
    plan = {**PLAN_STORY, "raises": [DOUBT]}
    rc, why = check({"plan.json": plan}, "300.1")
    assert rc == 0, f"300.1: a plan raising its doubt as a question with evidence was rejected: {why!r}"
    out, pack, logs = tmp_path / "record-out", tmp_path / "record-pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    (out / "plan.json").write_text(json.dumps(plan))
    (out / "check.txt").write_text("")
    code, said = run_agent("record", "planner", "", str(out), str(out / "check.txt"), "true", str(logs), PACK=str(pack))
    assert code == 0, f"300.1: the record step failed on a plan with a question:\n{said[-800:]}"
    rec_ = json.load(open(out / "record.json"))
    kept = [r for r in rec_["handback"].get("raises") or [] if r.get("kind") == "question"]
    assert len(kept) == 1 and kept[0].get("evidence") == DOUBT["evidence"] and kept[0].get("to") == "owner", \
        f"300.1: the record does not keep the doubt as a question for the owner with its evidence: {kept}"
    shown = (out / "comment.md").read_text().split("<details", 1)[0]
    # Since #470 a #N in a raise shows as a short plain link, so GitHub does not draw its title.
    assert DOUBT["text"].replace("#339", "[#339](https://github.com/o/r/issues/339)") in shown and "for you" in shown, \
        f"300.1: the planner's comment does not show the doubt as a question for you:\n{shown}"
    assert DOUBT["evidence"] in shown, f"300.1: the planner's comment does not show the doubt's evidence:\n{shown}"
    step = agent.next_step([], rec_, [OWNER], autopilot=lambda: False)
    assert step[0] == "stop", f"300.1: a plan with a doubt for the owner did not stop for them off autopilot: {step}"


# 300.2: the exact list to answer, each by its ID; nothing skipped; old records still read.

def test_the_record_step_stamps_every_raise_with_who_raised_it_and_a_new_id(record_property, tmp_path):
    """Code stamps each raise with who raised it and an ID new on the issue.

    Runs the record step for a worker raising two things, with earlier records in the pack holding raises P1 and R1
    and an old review's blocker B1, and checks record.json gives each raise raised_by worker and an ID of its own.

    Proves 300.2."""
    record_property("proves", "300.2")
    out, pack, logs = tmp_path / "out", tmp_path / "pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    old = rec("reviewer", "pr", {"verdict": "block", "summary": "s", "blockers": [
        {"id": "B1", "criterion": "9.1", "problem": "p", "evidence": "e", "fix": "f", "fixer": "worker"}]})
    for i, r in enumerate([rec("planner", "", {**STORY, "raises": [P1]}), rec("reviewer", "plan", review(raises=[R1])),
                           old], 1):
        (pack / "in" / f"{i:02d}-{r['role']}.json").write_text(json.dumps(r))
    (out / "work.json").write_text(json.dumps({**WORK, "raises": [TO_PLANNER, FOUND]}))
    (out / "check.txt").write_text("")
    code, said = run_agent("record", "worker", "", str(out), str(out / "check.txt"), "true", str(logs), PACK=str(pack))
    assert code == 0, f"300.2: the record step failed:\n{said[-800:]}"
    got = json.load(open(out / "record.json"))["handback"].get("raises") or []
    ids = [r.get("id") for r in got]
    assert len(got) == 2 and all(r.get("raised_by") == "worker" for r in got), \
        f"300.2: the worker's raises were not stamped with who raised them: {got}"
    assert all(isinstance(i, str) and i for i in ids) and len(set(ids)) == 2 and not set(ids) & {"P1", "R1", "B1"}, \
        f"300.2: the worker's raises got IDs {ids}, not two new IDs unlike P1, R1 and B1 already on the issue"


def test_each_starting_pack_lists_exactly_the_open_raises_for_that_agent(record_property, tmp_path, monkeypatch):
    """Each agent's starting pack lists exactly its open raises, each with its ID.

    Builds packs from a faked issue as it goes: a plan raising a question and an issue, a plan review blocking with a
    blocker for the planner, a re-plan answering it, an approval, a worker raising a blocker for the planner, a
    rejected worker hand-back raising another, and a code review answering the worker and blocking for the worker,
    the planner and the owner. At each point every agent's list must be exactly what is open for it: the planner's
    blocker after the plan review and none once answered; the worker's raise for the planner on the reviewer's list,
    not the planner's; after the code review, the worker's and the planner's blockers on their lists, and on the
    planner's also the worker's raise the review answered done, passed on as the reviewer's blocker (#301: a review's
    own blocker for the planner never hides a raise it confirmed). Lists are compared in any order.

    Proves 300.2."""
    record_property("proves", "300.2")
    plan = rec("planner", "", {**STORY, "raises": [P1, P3]})
    block = rec("reviewer", "plan", review(raises=[R1]))
    replan = rec("planner", "", {**STORY, "answers": [{"raise": "R1", "answer": "done", "why": "Made it real."}]})
    ok = rec("reviewer", "plan", review("approve"))
    work = rec("worker", "", {**WORK, "raises": [W1]})
    rejected = rec("worker", "", {**WORK, "raises": [WX]}, passed=False)
    code_review = rec("reviewer", "pr", review(stage="pr", raises=[R2, R3, R4],
                                               answers=[{"raise": "W1", "answer": "done", "why": "It never passes."}]))
    expect = [
        ([plan, block], {"planner": [R1], "worker": [], "reviewer": []}),
        ([plan, block, replan, ok], {"planner": [], "worker": [], "reviewer": []}),
        ([plan, block, replan, ok, work, rejected], {"planner": [], "worker": [], "reviewer": [W1]}),
        ([plan, block, replan, ok, work, rejected, code_review], {"planner": [R3, CONFIRMED], "worker": [R2],
                                                                 "reviewer": []}),
    ]
    for recs, want in expect:
        for role, raised in want.items():
            stage = "pr" if role == "reviewer" else ""
            got = listed(monkeypatch, tmp_path, recs, role, stage)
            if CONFIRMED in raised:
                passed_on = [g for g in got if isinstance(g, dict) and confirmed_w1(g)]
                assert len(passed_on) == 1, (f"300.2: after the code review answered W1 done, the planner's pack should "
                                             f"list it once as the reviewer's blocker, lists:\n{json.dumps(got)[:600]}")
                got = [g for g in got if g is not passed_on[0]] + [CONFIRMED]
            assert sorted(got, key=json.dumps) == sorted(raised, key=json.dumps), (
                f"300.2: after {[r['role'] + ('-' + r['stage'] if r['stage'] else '') for r in recs]}"
                f" the {role}'s pack lists {[g.get('id', g.get('confirmed')) for g in got if isinstance(g, dict)]}, "
                f"not exactly {[r.get('id', r.get('confirmed')) for r in raised]}:\n{json.dumps(got)[:600]}")


CONFIRMED = {"confirmed": "W1"}


def confirmed_w1(g):
    """Whether this raise is W1 passed on as the reviewer's blocker for the planner."""
    return (g.get("kind") == "blocker" and g.get("to") == "planner" and g.get("raised_by") == "reviewer"
            and W1["text"] in str(g.get("text") or "") and bool(g.get("id")) and g.get("id") != "W1")


def round_pack(tmp_path, items, earlier=()):
    """A pack folder for the round check holding these open raises.

    It also holds earlier records in in/, the issue and its open issues."""
    d = tempfile.mkdtemp(dir=tmp_path)
    json.dump(list(items), open(os.path.join(d, "open_blockers.json"), "w"))
    json.dump([], open(os.path.join(d, "open_issues.json"), "w"))
    json.dump({"number": None}, open(os.path.join(d, "parent.json"), "w"))
    open(os.path.join(d, "issue.md"), "w").write("# Issue #9: T\n\nPaint the door blue.\n\n## Comments\n")
    os.makedirs(os.path.join(d, "in"))
    for i, r in enumerate(earlier, 1):
        json.dump(r, open(os.path.join(d, "in", f"{i:02d}-{r['role']}.json"), "w"))
    return d


def round_check(tmp_path, role, handback, pack):
    """Run `agent check-round ROLE FILE PACK`; return (exit code, output)."""
    f = os.path.join(tempfile.mkdtemp(dir=tmp_path), "h.json")
    json.dump(handback, open(f, "w"))
    return run_agent("check-round", role, f, pack)


def test_the_round_check_rejects_a_hand_back_that_skips_a_raise_naming_each_one(record_property, tmp_path):
    """Code rejects a hand-back that skips a raise on its list, naming each one.

    For the planner (blockers R1 and R3), the worker (R2 and an old blocker B2) and the reviewer (the worker's W1
    passing through it), answering every one passes; skipping one is rejected naming that ID and not the answered
    one; skipping all names each; an answer that is neither done nor disagree, or has no why, is rejected.

    Proves 300.2."""
    record_property("proves", "300.2")
    b2 = {"kind": "blocker", "to": "worker", "text": "Old blocker.", "raised_by": "reviewer", "id": "B2"}
    cases = (("planner", [R1, R3], {"links": LINKS}), ("worker", [R2, b2], {}), ("reviewer", [W1], {}))
    for role, items, extra in cases:
        pack = round_pack(tmp_path, items)
        ans = [{"raise": r["id"], "answer": "done" if i % 2 == 0 else "disagree", "why": f"Because {r['id']}."}
               for i, r in enumerate(items)]
        code, out = round_check(tmp_path, role, {**extra, "answers": ans}, pack)
        assert code == 0, f"300.2: the {role} answered every raise on its list and was rejected:\n{out}"
        if len(items) > 1:
            code, out = round_check(tmp_path, role, {**extra, "answers": ans[:1]}, pack)
            assert code == 1 and items[1]["id"] in out and items[0]["id"] not in out, \
                f"300.2: the {role} skipped {items[1]['id']} and the check did not name only it (exit {code}):\n{out}"
        code, out = round_check(tmp_path, role, {**extra, "answers": []}, pack)
        assert code == 1 and all(r["id"] in out for r in items), \
            f"300.2: the {role} answered nothing and the check did not name every raise (exit {code}):\n{out}"
        for bad in ({**ans[0], "answer": "maybe"}, {k: v for k, v in ans[0].items() if k != "why"}):
            code, out = round_check(tmp_path, role, {**extra, "answers": [bad] + ans[1:]}, pack)
            assert code == 1, f"300.2: the {role}'s answer {bad} was accepted, though it is not done or disagree with why"


OLD_BLOCK = rec("reviewer", "pr", {
    "previous_step": {"did": ["Built it."], "decided": [], "open": []}, "verdict": "block", "summary": "s",
    "blockers": [{"id": "B1", "criterion": "9.1", "test": None, "problem": "The test asserts nothing.", "evidence": "e",
                  "fix": "f", "fixer": "planner"},
                 {"id": "B2", "criterion": "9.2", "test": None, "problem": "The job id is never returned.",
                  "evidence": "e", "fix": "f", "fixer": "worker"}],
    "notes": [], "outside_plan": [], "resolved": [], "asks": []})
OLD_PLAN = rec("planner", "", {**STORY, "questions": [{"question": "Should it retry?", "assumption": "It does not."}],
                               "concerns": [{"text": "This overlaps #12.", "evidence": "dokima/board.py"}]})
OLD_WORK = rec("worker", "", {**WORK, "suspect_tests": [], "replies": []})


def test_records_from_before_this_change_are_read_and_their_open_blockers_listed_under_old_ids(record_property, tmp_path, monkeypatch):
    """Old records stay as posted, and their open blockers are listed by old ID.

    Builds packs from an issue whose plan, work and code review were posted with the old fields: the pack copies each
    record into in/ exactly as posted and its own check passes it. The planner's list holds B1 and the worker's B2,
    each a blocker with its old ID and problem. Once a new planner answers B1, it leaves the planner's list and B2
    stays on the worker's; an old reply to B2 takes it off too.

    Proves 300.2."""
    record_property("proves", "300.2")
    recs = [OLD_PLAN, rec("reviewer", "plan", {"verdict": "approve", "summary": "s", "blockers": []}), OLD_WORK,
            OLD_BLOCK]
    fake_github(monkeypatch, recs)
    dest = tmp_path / "planner"
    agent.pack("o/r", 9, "planner", "", str(dest))
    kept = [json.load(open(dest / "in" / n)) for n in sorted(os.listdir(dest / "in"))]
    assert kept == recs, "300.2: the pack did not keep the records posted before this change exactly as they were"
    assert agent.problems_pack("planner", "", str(dest)) == [], \
        f"300.2: the pack check rejects a pack of old records: {agent.problems_pack('planner', '', str(dest))}"
    for role, want, text in (("planner", "B1", "The test asserts nothing."), ("worker", "B2", "The job id is never returned.")):
        got = listed(monkeypatch, tmp_path, recs, role)
        assert [g.get("id") for g in got] == [want], f"300.2: the {role}'s list holds {got}, not exactly the old {want}"
        g = got[0]
        assert g.get("kind") == "blocker" and g.get("to") == role and g.get("raised_by") == "reviewer" \
            and text in (g.get("text") or ""), f"300.2: the old {want} is not listed as a blocker for the {role}: {g}"
    answered = recs + [rec("planner", "", {**STORY, "answers": [{"raise": "B1", "answer": "done", "why": "Fixed."}]})]
    assert listed(monkeypatch, tmp_path, answered, "planner") == [], "300.2: B1, answered by the planner, is still listed"
    assert [g.get("id") for g in listed(monkeypatch, tmp_path, answered, "worker")] == ["B2"], \
        "300.2: B2, not answered, left the worker's list"
    replied = answered + [rec("worker", "", {**WORK, "replies": [{"blocker": "B2", "answer": "fixed", "why": "w"}]})]
    assert listed(monkeypatch, tmp_path, replied, "worker") == [], "300.2: B2, answered by an old reply, is still listed"


# 300.3: the river routes by raises.

def test_the_river_sends_each_blocker_to_the_agent_it_names_and_stops_for_yours(record_property):
    """A blocker goes to the agent it names; one for you stops.

    Asks the river what follows: a code review blocking for the worker starts the worker; for the planner, alone or
    beside one for the worker, starts the planner; a plan review blocking for the planner starts the planner. A review
    raising a question or a blocker for the owner stops, even on autopilot, while one raising only an issue goes on.
    A planner's blocker for the owner stops even on autopilot, a planner raising only an issue goes to the plan
    reviewer, and a worker's raise for the planner goes to the code reviewer first.

    Proves 300.3."""
    record_property("proves", "300.3")
    plan = rec("planner", "", STORY)
    items = [comment(plan), comment(rec("reviewer", "plan", review("approve"))),
             comment(rec("worker", "", WORK))]
    nxt = lambda r, on=False, its=items: agent.next_step(its, r, [OWNER], autopilot=lambda: on, body="b", number="9")
    for raised, who in (([R2], "worker"), ([R3], "planner"), ([R2, R3], "planner")):
        step = nxt(rec("reviewer", "pr", review(stage="pr", raises=raised)))
        assert step == ("start", who, ""), f"300.3: a code review blocking with {[r['to'] for r in raised]} gave {step}, not the {who}"
    step = nxt(rec("reviewer", "plan", review(raises=[R1])), its=items[:1])
    assert step == ("start", "planner", ""), f"300.3: a plan review blocking for the planner gave {step}"
    for_owner = stamped({**TO_WORKER, "to": "owner"}, "reviewer", "R5")
    for verdict, raised in (("block", [R2, for_owner]), ("block", [R2, R4]), ("approve", [R4]), ("approve", [for_owner])):
        for on in (False, True):
            step = nxt(rec("reviewer", "plan", review(verdict, raises=raised)), on, items[:1])
            assert step[0] == "stop", \
                f"300.3: a plan review ({verdict}, autopilot {on}) raising a {raised[-1]['kind']} for the owner did not stop: {step}"
    step = nxt(rec("reviewer", "plan", review("approve", raises=[stamped(FOUND, "reviewer", "R6")])), True, items[:1])
    assert step[:2] == ("start", "worker"), f"300.3: an approving plan review raising only an issue did not go on: {step}"
    step = nxt(rec("planner", "", {**STORY, "raises": [stamped({**TO_PLANNER, "to": "owner"}, "planner", "P4")]}), True, [])
    assert step[0] == "stop", f"300.3: a planner's blocker for the owner did not stop on autopilot: {step}"
    step = nxt(rec("planner", "", {**STORY, "raises": [P3]}), False, [])
    assert step == ("start", "reviewer", "plan"), f"300.3: a plan raising only an issue did not go to the plan reviewer: {step}"
    step = nxt(rec("worker", "", {**WORK, "raises": [W1]}), False, items[:2])
    assert step == ("start", "reviewer", "pr"), f"300.3: a worker's raise for the planner did not go to the code reviewer: {step}"


def test_three_blocking_reviews_in_a_row_still_stop_for_you(record_property):
    """Three blocking reviews in a row at one stage still stop for you.

    Asks the river what follows a third blocking code review after two others since the owner last spoke, each
    blocking only through a raise for the planner: it stops for the owner. After one earlier block, or after the
    owner spoke in between, the block goes back to the planner it names.

    Proves 300.3."""
    record_property("proves", "300.3")
    plan = rec("planner", "", STORY)
    base = [{"author": {"login": OWNER}, "body": "/work", "createdAt": "2026-10-09T09:00:00Z", "where": "issue #9"},
            comment(plan), comment(rec("reviewer", "plan", review("approve"))), comment(rec("worker", "", WORK))]
    blocked = lambda: comment(rec("reviewer", "pr", review(stage="pr", raises=[R3])))
    owner = {"author": {"login": OWNER}, "body": "/review", "createdAt": "2026-10-09T11:00:00Z", "where": "issue #9"}
    this = rec("reviewer", "pr", review(stage="pr", raises=[R3]))
    step = agent.next_step(base + [blocked(), blocked()], this, [OWNER])
    assert step[0] == "stop" and "3" in step[1], f"300.3: the third blocking review in a row did not stop for the owner: {step}"
    for case, items in (("one earlier block", base + [blocked()]), ("the owner spoke", base + [blocked(), owner, blocked()])):
        step = agent.next_step(items, this, [OWNER])
        assert step == ("start", "planner", ""), f"300.3 ({case}): the block did not go back to the planner: {step}"


# 300.4: on autopilot the reviewer answers a question for you only with your own words, checked by code.

SAID = {"author": {"login": OWNER}, "body": "Every failure should name the step that failed, nothing vaguer.",
        "createdAt": "2026-10-09T09:50:00Z", "url": ISSUE + "#issuecomment-77", "where": "issue #9"}
STRANGER = {"author": {"login": "stranger"}, "body": "A failed run should move to Needs you.",
            "createdAt": "2026-10-09T09:55:00Z", "url": ISSUE + "#issuecomment-78", "where": "issue #9"}
BODY = "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<!-- dokima-ask -->\nA failed run moves to Needs you.\n"
Q_PLAN = rec("planner", "", {**STORY, "raises": [P1, P2]})


def for_owner(rid, words, source, answer="done", changes=False):
    """A reviewer's answer to a question for the owner, quoting their words."""
    return {"raise": rid, "answer": answer, "why": "Your words settle it.", "words": words, "source": source,
            "changes": changes}


GOOD_1 = for_owner("P1", "A failed run moves to Needs you.", ISSUE)
GOOD_2 = for_owner("P2", "Every failure should name the step that failed", ISSUE + "#issuecomment-77")


def test_the_reviewers_answer_for_you_must_quote_your_words_and_where(record_property, tmp_path):
    """The reviewer's answer for you must quote your words and say where.

    Runs the round check of a plan review whose pack holds the plan with two questions for the owner: answering both
    with the owner's words, their source and changes passes, as does answering neither. An answer with no words, no
    source, a source on another issue, or no changes is rejected.

    Proves 300.4."""
    record_property("proves", "300.4")
    pack = round_pack(tmp_path, [], earlier=[Q_PLAN])
    base = review("approve")
    for answers in ([GOOD_1, GOOD_2], []):
        code, out = round_check(tmp_path, "reviewer", {**base, "answers": answers}, pack)
        assert code == 0, f"300.4: a plan review answering {len(answers)} questions with the owner's words was rejected:\n{out}"
    bad = (("no words", {k: v for k, v in GOOD_2.items() if k != "words"}),
           ("no source", {k: v for k, v in GOOD_2.items() if k != "source"}),
           ("another issue", {**GOOD_2, "source": "https://github.com/o/r/issues/8#issuecomment-77"}),
           ("no changes", {k: v for k, v in GOOD_2.items() if k != "changes"}))
    for case, a in bad:
        code, out = round_check(tmp_path, "reviewer", {**base, "answers": [GOOD_1, a]}, pack)
        assert code == 1 and "P2" in out, f"300.4 ({case}): an answer for the owner with {case} was not rejected naming P2:\n{out}"


def test_on_autopilot_only_your_real_words_let_a_question_go_on_and_off_autopilot_every_question_waits(record_property, monkeypatch):
    """On autopilot only your real words let a question go on; others wait.

    Asks the river what follows an approving plan review of a plan with two questions. On autopilot, both answered
    done with words really in the issue's text and in a code owner's comment, and changing nothing, the worker starts.
    Every other case stops and names the question left, not the other: one not answered, answered disagree, words not
    in the comment, a comment by someone who is not a code owner, and a reading that changes how the system works or
    what it costs. Off autopilot the plan with questions stops right after the planner, and on autopilot it goes to
    the plan reviewer.

    Proves 300.4."""
    record_property("proves", "300.4")
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    items = [SAID, STRANGER, {**comment(Q_PLAN), "url": ISSUE + "#issuecomment-79"}]
    decide = lambda answers, on=True: agent.next_step(items, rec("reviewer", "plan", review("approve", answers=answers)),
                                                      [OWNER], autopilot=lambda: on, body=BODY, number="9")
    step = decide([GOOD_1, GOOD_2])
    assert step[:2] == ("start", "worker"), f"300.4: both questions answered with the owner's real words did not go on: {step}"
    bad = (("not answered", [GOOD_1]),
           ("disagree", [GOOD_1, {**GOOD_2, "answer": "disagree"}]),
           ("words not there", [GOOD_1, {**GOOD_2, "words": "Show the cost of every run."}]),
           ("not a code owner", [GOOD_1, {**GOOD_2, "words": "A failed run should move to Needs you.",
                                          "source": ISSUE + "#issuecomment-78"}]),
           ("changes", [GOOD_1, {**GOOD_2, "changes": True}]))
    for case, answers in bad:
        step = decide(answers)
        assert step[0] == "stop", f"300.4 ({case}): the question went on without the owner: {step}"
        assert P2["text"] in step[1] and P1["text"] not in step[1], \
            f"300.4 ({case}): the stop does not name only the question left ({P2['text']!r}): {step[1]!r}"
    on = agent.next_step(items[:2], Q_PLAN, [OWNER], autopilot=lambda: True)
    off = agent.next_step(items[:2], Q_PLAN, [OWNER], autopilot=lambda: False)
    assert on == ("start", "reviewer", "plan"), f"300.4: on autopilot a plan with questions did not go to the plan reviewer: {on}"
    assert off[0] == "stop", f"300.4: off autopilot a plan with questions did not stop for the owner: {off}"


# 300.5: one shared section on raising and answering, with an example of each kind.

ROLE_FILES = ("planner", "worker", "reviewer")
HEADING = "# Raising and answering"


def section(role):
    """The shared section of a role prompt, or None without one.

    It runs from its heading to the next top-level heading."""
    lines = open(os.path.join(ROOT, "dokima", "roles", f"{role}.md")).read().splitlines()
    at = [i for i, l in enumerate(lines) if l.strip() == HEADING]
    if len(at) != 1:
        return None
    end = next((j for j in range(at[0] + 1, len(lines)) if lines[j].startswith("# ")), len(lines))
    return "\n".join(lines[at[0]:end]).strip()


def examples(text):
    """Every JSON object in the text that opens with a "kind" key, parsed.

    One that does not parse fails the test."""
    found, dec = [], json.JSONDecoder()
    for m in re.finditer(r'\{\s*"kind"\s*:', text):
        try:
            found.append(dec.raw_decode(text[m.start():])[0])
        except json.JSONDecodeError as e:
            pytest.fail(f"300.5: an example raise in the shared section is not valid JSON ({e}): {text[m.start():][:160]}")
    return found


def test_the_three_prompts_share_one_section_on_raising_and_answering(record_property):
    """The three role prompts share one section on raising and answering, word for word.

    Reads dokima/roles/planner.md, worker.md and reviewer.md: each has exactly one "# Raising and answering" section,
    the three are the same text, and it names both fields, raises and answers.

    Proves 300.5."""
    record_property("proves", "300.5")
    found = {role: section(role) for role in ROLE_FILES}
    for role, text in found.items():
        assert text, f"300.5: dokima/roles/{role}.md has no single '{HEADING}' section"
    assert len(set(found.values())) == 1, "300.5: the shared section is not the same text in the planner, worker and reviewer prompts"
    text = found["planner"]
    for field in ('"raises"', '"answers"'):
        assert field in text, f"300.5: the shared section does not name the field {field}"


def test_the_shared_section_shows_a_real_example_of_each_kind(record_property):
    """The shared section shows a question, a blocker and an issue code accepts.

    Parses every example raise in the shared section as JSON and checks there is a question, a blocker and an issue,
    and that each one passes code's check for some agent allowed to raise it, so no example teaches a wrong raise.
    It also checks no role prompt still asks for an old field.

    Proves 300.5."""
    record_property("proves", "300.5")
    text = section("planner")
    assert text, f"300.5: dokima/roles/planner.md has no '{HEADING}' section"
    found = examples(text)
    kinds = {e.get("kind") for e in found}
    for kind in ("question", "blocker", "issue"):
        assert kind in kinds, f"300.5: the shared section has no example of a {kind}; it has {sorted(map(str, kinds))}"
    for e in found:
        ok = [role for role in ROLE_FILES if not raises.check_raises(role, [e])]
        assert ok, f"300.5: the example {e} is rejected by code for every agent: {raises.check_raises('reviewer', [e])}"
    for role in ROLE_FILES:
        prompt = open(os.path.join(ROOT, "dokima", "roles", f"{role}.md")).read()
        for field in OLD:
            assert f'"{field}"' not in prompt, f"300.5: dokima/roles/{role}.md still asks for the old field \"{field}\""

"""Three kinds of raise and one table of who raises to whom (#298).

The owner wants every judgment an agent raises to be a question, a blocker or an issue, sent only where a fixed table
in code allows, stamped by code with who raised it and an ID, and answered by whoever it was sent to. This story adds
that shared model alone, in dokima/raises.py; no hand-back, card or prompt changes yet (story 3, #300, wires it in).

The module these tests run, as the plan fixes it:
- `KINDS`: the tuple ("question", "blocker", "issue").
- `TABLE`: a read-only mapping from each raiser to the tuple of whom it may send a question or blocker:
  planner -> owner; worker -> planner; reviewer -> planner, worker, owner. An issue is for no one.
- `check_raises(role, raises)`: the problems with the raises an agent of that role wrote, as plain sentences; empty
  when they are fine. A raise is {"kind", "to", "label", "text", "full", "evidence"}; label and evidence are optional and an
  issue has no "to".
- `sent_to(raise_)`: the one who must answer a raise first: its "to", except the reviewer for a worker's raise to the
  planner (it goes through the reviewer); None for an issue.
- `stamp(role, raises, taken)`: copies of the raises with "raised_by" set to the role and an "id" unique among
  `taken` (the IDs already on the issue) and each other.
- `check_answers(role, answers, open_raises)`: the problems with an agent's answers, each {"raise": ID, "answer":
  "done" or "disagree", "why": text}, given the stamped raises still open on the issue; empty when they are fine.

Each test imports the module through `raises_module()`, so today every test fails saying the module is missing.
"""
import importlib
import itertools
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ROLES = ("planner", "worker", "reviewer")
WHO = ("owner", "planner", "worker", "reviewer")
ROWS = {"planner": {"owner"}, "worker": {"planner"}, "reviewer": {"planner", "worker", "owner"}}


def raises_module():
    """dokima.raises, or a failure saying it does not exist yet."""
    try:
        return importlib.import_module("dokima.raises")
    except ModuleNotFoundError as e:
        if e.name in ("dokima.raises",):
            pytest.fail("dokima/raises.py does not exist yet: the kinds, the table and their checks are missing")
        raise


def one(kind, to=None, **more):
    """One raise as an agent would write it."""
    r = {"kind": kind, "text": f"A {kind} with something to say.", "full": f"The whole {kind}, for agents.", **more}
    if to is not None:
        r["to"] = to
    return r


def stamped(rid, raised_by, kind, to=None):
    """One raise as it sits on the issue after code stamped it."""
    return {**one(kind, to), "raised_by": raised_by, "id": rid}


# 298.1: closed kinds, free labels.

def test_only_question_blocker_and_issue_are_kinds(record_property):
    """Only a question, a blocker or an issue can be raised.

    Sends a note, a concern and an empty kind from every role and checks each is rejected with a sentence naming the
    bad kind and question, blocker and issue; then checks one good raise of each of the three kinds passes.

    Proves 298.1."""
    record_property("proves", "298.1")
    m = raises_module()
    for role in ROLES:
        for bad in ("note", "concern", "Question", ""):
            problems = m.check_raises(role, [one(bad, sorted(ROWS[role])[0])])
            assert problems, f"298.1: a {bad!r} raise from the {role} passed, but only question, blocker or issue may"
            said = " ".join(problems)
            for word in ("question", "blocker", "issue"):
                assert word in said, f"298.1: rejecting a {bad!r} raise did not name the allowed kind {word}: {said}"
            if bad:
                assert bad in said, f"298.1: rejecting a {bad!r} raise did not name the kind it was given: {said}"
        to = sorted(ROWS[role])[0]
        good = [one("question", to), one("blocker", to), one("issue")]
        assert m.check_raises(role, good) == [], f"298.1: good raises from the {role} were rejected"


def test_any_label_passes_and_changes_nothing(record_property):
    """Any label passes, and the label never changes how a raise is checked or routed.

    Gives the same raises the labels weak test, missing ask, a made-up label and none, and checks each set gets the
    same verdict, the same problems and the same first answerer, for good raises and for raises outside the table.

    Proves 298.1."""
    record_property("proves", "298.1")
    m = raises_module()
    labels = (None, "weak test", "missing ask", "zebra crossing")
    cases = [("worker", "blocker", "planner"), ("reviewer", "question", "owner"), ("planner", "issue", None),
             ("worker", "blocker", "owner"), ("planner", "question", "worker")]
    for role, kind, to in cases:
        results, routes = set(), set()
        for label in labels:
            r = one(kind, to) if label is None else one(kind, to, label=label)
            results.add(tuple(m.check_raises(role, [r])))
            routes.add(m.sent_to({**r, "raised_by": role, "id": "x1"}))
        assert len(results) == 1, f"298.1: the {role}'s {kind} to {to} was checked differently by label: {results}"
        assert len(routes) == 1, f"298.1: the {role}'s {kind} to {to} was routed differently by label: {routes}"
        if role in ROWS and (to is None) == (kind == "issue") and (to is None or to in ROWS[role]):
            assert results == {()}, f"298.1: a labelled {kind} from the {role} to {to} was rejected: {results}"


# 298.2: the table.

def test_every_row_of_the_table_passes(record_property):
    """Every row of the table passes, and each raise goes to whoever answers it first.

    Sends a question and a blocker along every row and an issue for no one from every role, and checks none is
    rejected; checks a worker's raise to the planner goes to the reviewer first and every other raise to its target.

    Proves 298.2."""
    record_property("proves", "298.2")
    m = raises_module()
    for role, targets in ROWS.items():
        for to, kind in itertools.product(sorted(targets), ("question", "blocker")):
            assert m.check_raises(role, [one(kind, to)]) == [], f"298.2: the {role}'s {kind} to the {to} was rejected"
            first = "reviewer" if (role, to) == ("worker", "planner") else to
            got = m.sent_to(stamped("x1", role, kind, to))
            assert got == first, f"298.2: the {role}'s {kind} to the {to} goes first to {got}, not the {first}"
        assert m.check_raises(role, [one("issue")]) == [], f"298.2: an issue from the {role} for no one was rejected"
        assert m.sent_to(stamped("x2", role, "issue")) is None, f"298.2: an issue from the {role} was sent to someone"


def test_a_raise_outside_the_table_is_rejected_naming_who_kind_and_whom(record_property):
    """A raise outside the table is rejected, naming who raised it, its kind and whom.

    Tries every pair the table does not hold, for both kinds, and checks each is rejected with a sentence naming the
    raiser, the kind and the target.

    Proves 298.2."""
    record_property("proves", "298.2")
    m = raises_module()
    for role in ROLES:
        for to in WHO:
            if to in ROWS[role]:
                continue
            for kind in ("question", "blocker"):
                problems = m.check_raises(role, [one(kind, to)])
                assert problems, f"298.2: the {role}'s {kind} to the {to} passed, but the table does not allow it"
                said = " ".join(problems)
                for word in (role, kind, to):
                    assert word in said, f"298.2: rejecting the {role}'s {kind} to the {to} did not name {word}: {said}"
        problems = m.check_raises(role, [one("question", "the team")])
        assert problems and "the team" in " ".join(problems), f"298.2: the {role} raised to 'the team' unnamed"


def test_a_blocker_or_question_for_no_one_and_an_issue_for_someone_are_rejected(record_property):
    """A blocker or question for no one, or an issue for someone, is rejected.

    Sends from every role a blocker and a question with no target or an empty one, and an issue addressed to the
    owner, and checks each is rejected; the blocker's and question's rejections name the raiser, the kind and no one.

    Proves 298.2."""
    record_property("proves", "298.2")
    m = raises_module()
    for role in ROLES:
        for kind in ("blocker", "question"):
            for r in (one(kind), {**one(kind), "to": ""}):
                problems = m.check_raises(role, [r])
                assert problems, f"298.2: the {role}'s {kind} naming no one passed"
                said = " ".join(problems)
                for word in (role, kind, "no one"):
                    assert word in said, f"298.2: rejecting the {role}'s {kind} for no one did not say {word!r}: {said}"
        assert m.check_raises(role, [one("issue", "owner")]), f"298.2: the {role}'s issue sent to the owner passed"


# 298.3: code stamps who raised it and an ID.

def test_code_stamps_the_raiser_from_the_agent_that_ran(record_property):
    """Code stamps each raise with the agent that ran, keeping everything the agent wrote.

    Stamps the same raises as the worker and as the reviewer and checks every copy says that role raised it, keeps its
    kind, target, label, text and evidence, and leaves the agent's own list untouched.

    Proves 298.3."""
    record_property("proves", "298.3")
    m = raises_module()
    written = [one("blocker", "planner", label="weak test", evidence="tests/test_x.py:12"), one("issue")]
    before = [dict(r) for r in written]
    for role in ("worker", "reviewer"):
        out = m.stamp(role, written, set())
        assert len(out) == len(written), f"298.3: stamping as the {role} gave {len(out)} raises for {len(written)}"
        for got, mine in zip(out, written):
            assert got["raised_by"] == role, f"298.3: a raise stamped as the {role} says {got.get('raised_by')}"
            assert {k: v for k, v in got.items() if k not in ("raised_by", "id")} == mine, \
                f"298.3: stamping changed what the agent wrote: {got}"
    assert written == before, "298.3: stamping changed the agent's own list"


def test_every_id_is_unique_on_the_issue(record_property):
    """Every ID code gives is new on the issue, never one already taken.

    Stamps five rounds of three raises, each against every ID taken so far plus IDs a counter would pick (r1, R1, 1
    and more), and checks every ID is non-empty text and none repeats or reuses a taken one.

    Proves 298.3."""
    record_property("proves", "298.3")
    m = raises_module()
    taken = {f"{p}{n}" for p in ("r", "R", "", "raise-") for n in range(1, 20)}
    for role in ("planner", "worker", "reviewer", "worker", "reviewer"):
        out = m.stamp(role, [one("issue"), one("issue"), one("issue")], set(taken))
        ids = [r["id"] for r in out]
        assert all(isinstance(i, str) and i.strip() for i in ids), f"298.3: an ID is not non-empty text: {ids}"
        assert len(set(ids)) == len(ids), f"298.3: one round gave two raises the same ID: {ids}"
        assert not set(ids) & taken, f"298.3: an ID was already on the issue: {sorted(set(ids) & taken)}"
        taken |= set(ids)


def test_a_raiser_or_id_written_by_the_model_is_rejected(record_property):
    """A raise that carries its own raiser or ID is rejected; only code writes them.

    Sends good raises with raised_by, with id, and with both, as the raiser itself would name them, and checks each
    is rejected naming the field; the same raise without them passes.

    Proves 298.3."""
    record_property("proves", "298.3")
    m = raises_module()
    base = one("blocker", "planner")
    assert m.check_raises("worker", [base]) == [], "298.3: a good raise was rejected"
    for extra in ({"raised_by": "worker"}, {"id": "R7"}, {"raised_by": "worker", "id": "R7"}, {"raised_by": "owner"}):
        problems = m.check_raises("worker", [{**base, **extra}])
        assert problems, f"298.3: a raise carrying {sorted(extra)} written by the model passed"
        said = " ".join(problems)
        for field in extra:
            assert re.search(rf"\b{field}\b", said), f"298.3: rejecting a model-written {field} did not name it: {said}"


# 298.4: answers.

OPEN = [stamped("a1", "reviewer", "blocker", "worker"), stamped("a2", "reviewer", "question", "worker"),
        stamped("a3", "reviewer", "blocker", "planner"), stamped("a4", "worker", "blocker", "planner"),
        stamped("a5", "planner", "question", "owner"), stamped("a6", "worker", "issue")]


def test_a_well_formed_answer_to_every_raise_passes(record_property):
    """A turn that answers every raise sent to its agent passes.

    Has the worker answer both raises sent to it, once done and once disagree, and the reviewer answer the worker's
    raise for the planner that passes through it, and checks both turns pass.

    Proves 298.4."""
    record_property("proves", "298.4")
    m = raises_module()
    worker = [{"raise": "a1", "answer": "done", "why": "Fixed the off-by-one."},
              {"raise": "a2", "answer": "disagree", "why": "The plan already says strings."}]
    assert m.check_answers("worker", worker, OPEN) == [], "298.4: the worker's good answers were rejected"
    reviewer = [{"raise": "a4", "answer": "done", "why": "The test can never pass as written."}]
    assert m.check_answers("reviewer", reviewer, OPEN) == [], "298.4: the reviewer's good answer was rejected"


def test_a_malformed_answer_is_rejected_naming_it(record_property):
    """A malformed answer is rejected, naming the answer by its place.

    Puts one bad answer second after a good one, for each way it can be wrong (no ID, an ID no open raise has, fixed
    or empty instead of done or disagree, no why, an empty why, not an object), and checks each is rejected naming
    answer 2; and that the good answer alone, with the other raise answered, passes.

    Proves 298.4."""
    record_property("proves", "298.4")
    m = raises_module()
    good = {"raise": "a1", "answer": "done", "why": "Fixed."}
    other = {"raise": "a2", "answer": "done", "why": "Done."}
    assert m.check_answers("worker", [good, other], OPEN) == [], "298.4: two good answers were rejected"
    bads = [{"answer": "done", "why": "Fixed."}, {"raise": "zz9", "answer": "done", "why": "Fixed."},
            {"raise": "a2", "answer": "fixed", "why": "Fixed."}, {"raise": "a2", "answer": "", "why": "Fixed."},
            {"raise": "a2", "answer": "done"}, {"raise": "a2", "answer": "disagree", "why": "  "}, "a2 done"]
    for bad in bads:
        problems = m.check_answers("worker", [good, bad, other], OPEN)
        assert problems, f"298.4: the answer {bad!r} passed"
        assert "answer 2" in " ".join(problems), f"298.4: rejecting the answer {bad!r} did not name answer 2: {problems}"


def test_a_turn_that_skips_a_raise_sent_to_it_is_rejected_naming_it(record_property):
    """A turn that skips a raise sent to its agent is rejected, naming that raise.

    Has the worker answer one of its two raises, then none; the reviewer skip the worker's raise passing through it;
    and the planner skip its own; checks each is rejected naming every skipped ID, while raises sent to others are not
    asked of it.

    Proves 298.4."""
    record_property("proves", "298.4")
    m = raises_module()
    cases = [("worker", [{"raise": "a1", "answer": "done", "why": "Fixed."}], {"a2"}, {"a1", "a3", "a4", "a5", "a6"}),
             ("worker", [], {"a1", "a2"}, {"a3", "a4", "a5", "a6"}),
             ("reviewer", [], {"a4"}, {"a1", "a2", "a3", "a5", "a6"}),
             ("planner", [], {"a3"}, {"a1", "a2", "a4", "a5", "a6"})]
    for role, answers, skipped, not_asked in cases:
        said = " ".join(m.check_answers(role, answers, OPEN))
        for rid in skipped:
            assert rid in said, f"298.4: the {role} left raise {rid} unanswered and was not told: {said!r}"
        for rid in not_asked:
            assert rid not in said, f"298.4: the {role} was asked to answer raise {rid}, which was not sent to it"
    full = [{"raise": "a3", "answer": "done", "why": "Rewrote the test."}]
    assert m.check_answers("planner", full, OPEN) == [], "298.4: the planner answered its only raise and was rejected"


# 298.5: one place in code.

def test_the_kinds_and_table_live_in_one_place_no_hand_back_can_change(record_property):
    """The kinds and the table live in one place no hand-back can change.

    Checks the module holds exactly the three kinds and the owner's table, that neither can be changed at run time,
    and that raises carrying their own kinds, table or route are still rejected and leave both as they were.

    Proves 298.5."""
    record_property("proves", "298.5")
    m = raises_module()
    assert tuple(m.KINDS) == ("question", "blocker", "issue"), f"298.5: the kinds are {m.KINDS!r}"
    assert {k: set(v) for k, v in m.TABLE.items()} == ROWS, f"298.5: the table is {dict(m.TABLE)!r}"
    with pytest.raises((TypeError, AttributeError)):
        m.KINDS.append("note")
    with pytest.raises(TypeError):
        m.TABLE["worker"] = ("owner",)
    with pytest.raises((TypeError, AttributeError)):
        m.TABLE["worker"].append("owner")
    tries = [{**one("note", "planner"), "kinds": ["question", "blocker", "issue", "note"]},
             {**one("blocker", "owner"), "table": {"worker": ["owner"]}},
             {**one("blocker", "owner"), "via": "reviewer"}]
    for r in tries:
        assert m.check_raises("worker", [r]), f"298.5: a hand-back widened the kinds or the table with {r}"
    assert tuple(m.KINDS) == ("question", "blocker", "issue"), "298.5: a hand-back changed the kinds"
    assert {k: set(v) for k, v in m.TABLE.items()} == ROWS, "298.5: a hand-back changed the table"

"""Code checks the reviewer's six required boxes at plan and code review.

Issue #819, story 3 of #741.

The owner shaped the boxes in the comment of 2026-10-15 on #741 and answered on 2026-10-17 that every box is required
at both stages, a box with nothing to check saying none. In review.json they sit in "boxes", beside asks, edge_cases and
tests:
    dropped:    "none" | [{"words", "source"}]
    added:      "none" | [{"what", "kind": "creep" | "needed", "serves"}]   (needed is not a blocker)
    superseded: "none" | [{"old", "new", "retired"}]
    conflicts:  "none" | [{"a", "b", "ask"}]
    edges:      {"N.k": "covered" | "missing: <named case>"} for every criterion of the plan
    poor_tests: "none" | [{"test", "passes_with", "fix"}]
Every entry is a blocker unless noted, so an approve holds none.

Every check runs the real commands the workflow runs on a review, through tests/test_review_asks.py's helpers, on a
plan for issue 9 with criteria 9.1 to 9.3 (or a two-story split with S1.1 and S2.1), with STAGE set to the plan review's
or the code review's.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_review_asks as ra  # noqa: E402

STAGES = ("plan", "pr")
NONE = {"dropped": "none", "added": "none", "superseded": "none", "conflicts": "none",
        "edges": {"9.1": "covered", "9.2": "covered", "9.3": "covered"}, "poor_tests": "none"}
ENTRIES = {"dropped": {"words": "Oil the hinges", "source": "https://github.com/o/r/issues/9#issuecomment-12"},
           "added": {"what": "A bell on the door", "kind": "creep", "serves": "9.1"},
           "superseded": {"old": "Paint the door red", "new": "https://github.com/o/r/issues/9#issuecomment-12",
                          "retired": "9.1"},
           "conflicts": {"a": "Paint the door blue", "b": "Paint the door green", "ask": "Which colour should it be?"},
           "poor_tests": {"test": "tests/test_x.py::test_a", "passes_with": "a door painted any colour",
                          "fix": "assert the colour is blue"}}
NEEDED = {"what": "A helper that reads the colour", "kind": "needed", "serves": "9.1"}


def boxed(review, **boxes):
    """The review with every box none and every criterion covered, `boxes` merged in."""
    return {**review, "boxes": {**NONE, **boxes}}


def without(review, box):
    """The review with one box left out of its boxes."""
    return {**review, "boxes": {k: v for k, v in review["boxes"].items() if k != box}}


def reasons(review, **kw):
    """The check's exit code and every printed reason, failing when it crashes."""
    code, out, err = ra.check_review(kw.pop("tmp_path"), review, **kw)
    assert "Traceback" not in err and "Traceback" not in out, f"the review check crashed:\n{err[-600:]}{out[-600:]}"
    return code, [line for line in out.splitlines() if line.strip()]


def test_a_review_missing_any_of_the_six_boxes_is_rejected_naming_the_box(record_property, tmp_path):
    """A review missing any of the six boxes is rejected, naming the box.

    Proves 819.1. At plan review and at code review, a review holding all six boxes passes. Taking out each box in turn (dropped,
    added, superseded, conflicts, edges, poor_tests) is rejected with a reason naming that box; so is a review with
    no boxes at all, its reason naming boxes."""
    record_property("proves", "819.1")
    for stage in STAGES:
        ra.assert_passes(tmp_path, boxed(ra.APPROVE), "819.1", f"a review holding all six boxes ({stage})", stage=stage)
        for box in NONE:
            ra.assert_rejected(tmp_path, without(boxed(ra.APPROVE), box), rf"\b{box}\b", "819.1",
                               f"a review with no {box} box ({stage})", stage=stage)
        bare = {k: v for k, v in ra.APPROVE.items() if k != "boxes"}
        ra.assert_rejected(tmp_path, bare, r"\bboxes\b", "819.1", f"a review with no boxes at all ({stage})",
                           stage=stage)


def test_a_box_entry_missing_a_field_its_shape_needs_is_rejected_naming_the_field(record_property, tmp_path):
    """A box entry missing a field its shape needs is rejected, naming the field.

    Proves 819.2. A blocking review whose dropped, added, superseded, conflicts and poor_tests boxes each hold one whole entry passes,
    at plan review and at code review. Then, for each box and each field of its shape, the same entry with that field
    left out, or blank, is rejected: one reason names the box and the field, and differs from the reason given when
    another field is left out, so the field named is the one missing. An added entry whose kind is neither creep nor
    needed is rejected naming kind, and an entry that is a bare line instead of an object is rejected naming its box."""
    record_property("proves", "819.2")
    for stage in STAGES:
        whole = {box: [entry] for box, entry in ENTRIES.items()}
        ra.assert_passes(tmp_path, boxed(ra.BLOCK, **whole), "819.2", f"a block whose boxes hold whole entries ({stage})",
                         stage=stage)
        for box, entry in ENTRIES.items():
            named = {}
            for field in entry:
                for value in (None, "", "  "):
                    part = {k: v for k, v in entry.items() if k != field} if value is None else {**entry, field: value}
                    code, out = reasons(boxed(ra.BLOCK, **{box: [part]}), tmp_path=tmp_path, stage=stage)
                    why = f"a {box} entry {'without' if value is None else 'with a blank'} {field} ({stage})"
                    assert code == 1, f"819.2: {why} was let through; it must be rejected"
                    lines = {line for line in out if re.search(rf"\b{box}\b", line)
                             and re.search(rf"(?<![\w-]){re.escape(field)}(?![\w-])", line)}
                    assert lines, f"819.2: {why} was rejected, but no reason names {box} and {field}:\n" + "\n".join(out)
                    named.setdefault(field, set()).update(lines)
            for field, lines in named.items():
                others = set().union(*(v for k, v in named.items() if k != field))
                assert lines - others, (f"819.2: the {box} box gives the same reason whichever field is missing, so it "
                                        f"does not name {field}: {sorted(lines)}")
        ra.assert_rejected(tmp_path, boxed(ra.BLOCK, added=[{**ENTRIES["added"], "kind": "extra"}]),
                           r"\badded\b.*\bkind\b|\bkind\b.*\badded\b", "819.2",
                           f"an added entry whose kind is extra, neither creep nor needed ({stage})", stage=stage)
        ra.assert_rejected(tmp_path, boxed(ra.BLOCK, dropped=["Oil the hinges"]), r"\bdropped\b", "819.2",
                           f"a dropped entry that is a bare line ({stage})", stage=stage)


def test_a_weak_test_entry_naming_no_wrong_code_that_still_passes_is_rejected(record_property, tmp_path):
    """A weak test entry that names no wrong code still passing is rejected.

    Proves 819.3. At plan review and at code review, a blocking review whose poor_tests entry names its test, the wrong code that
    still passes and the fix passes. The same entry with passes_with left out, empty or blank is rejected, the reason
    naming poor_tests and passes_with."""
    record_property("proves", "819.3")
    entry = ENTRIES["poor_tests"]
    for stage in STAGES:
        ra.assert_passes(tmp_path, boxed(ra.BLOCK, poor_tests=[entry]), "819.3",
                         f"a weak test entry naming the wrong code that still passes ({stage})", stage=stage)
        for value in (None, "", "  "):
            part = {k: v for k, v in entry.items() if k != "passes_with"} if value is None else {**entry, "passes_with": value}
            why = "without" if value is None else f"with {value!r} as"
            ra.assert_rejected(tmp_path, boxed(ra.BLOCK, poor_tests=[part]),
                               r"poor_tests.*passes_with|passes_with.*poor_tests", "819.3",
                               f"a weak test entry {why} the wrong code that still passes ({stage})", stage=stage)


def test_a_review_that_approves_while_a_box_holds_a_blocking_entry_is_rejected(record_property, tmp_path):
    """An approve is rejected while any box holds a blocking entry, naming the box.

    Proves 819.4. At plan review and at code review, an approve with every box none and every criterion covered passes. For each
    box in turn (a dropped ask, an added creep, a superseded criterion, a conflict, an edges line reading missing, a
    weak test), the same approve is rejected naming that box, while a block holding the same entry passes."""
    record_property("proves", "819.4")
    blocking = {**{box: [entry] for box, entry in ENTRIES.items()},
                "edges": {**NONE["edges"], "9.2": "missing: the issue has no comments"}}
    for stage in STAGES:
        ra.assert_passes(tmp_path, boxed(ra.APPROVE), "819.4", f"an approve with every box clear ({stage})", stage=stage)
        for box, value in blocking.items():
            ra.assert_passes(tmp_path, boxed(ra.BLOCK, **{box: value}), "819.4",
                             f"a block whose {box} box holds a blocking entry ({stage})", stage=stage)
            ra.assert_rejected(tmp_path, boxed(ra.APPROVE, **{box: value}), rf"\b{box}\b", "819.4",
                               f"an approve whose {box} box holds a blocking entry ({stage})", stage=stage)


def test_an_added_entry_of_kind_needed_does_not_stop_a_review_from_approving(record_property, tmp_path):
    """An approve passes when its added box holds only an entry of kind needed.

    Proves 819.5. At plan review and at code review, an approve whose added box holds one entry of kind needed passes. Beside it,
    the same approve whose entry is of kind creep is rejected naming added, so the pass comes from the kind needed and
    not from an added box code ignores."""
    record_property("proves", "819.5")
    for stage in STAGES:
        ra.assert_passes(tmp_path, boxed(ra.APPROVE, added=[NEEDED]), "819.5",
                         f"an approve whose added box holds only a needed entry ({stage})", stage=stage)
        ra.assert_rejected(tmp_path, boxed(ra.APPROVE, added=[{**NEEDED, "kind": "creep"}]), r"\badded\b", "819.5",
                           f"an approve whose added box holds a creep entry ({stage})", stage=stage)


def test_a_review_whose_edges_box_leaves_out_a_plan_criterion_is_rejected_naming_it(record_property, tmp_path):
    """A review whose edges box leaves out a plan criterion is rejected, naming it.

    Proves 819.6. At plan review and at code review, a review whose edges box gives every criterion passes. Leaving out 9.2 is
    rejected with a reason naming edges and 9.2; an empty edges box is rejected naming 9.1, 9.2 and 9.3; an edges box
    written none, though the plan has criteria, is rejected naming edges. On a two-story split, an edges box giving
    S1.1 but not S2.1 is rejected naming S2.1."""
    record_property("proves", "819.6")
    for stage in STAGES:
        ra.assert_passes(tmp_path, boxed(ra.APPROVE), "819.6", f"a review whose edges box gives every criterion ({stage})",
                         stage=stage)
        gap = {k: v for k, v in NONE["edges"].items() if k != "9.2"}
        ra.assert_rejected(tmp_path, boxed(ra.APPROVE, edges=gap), r"edges.*9\.2|9\.2.*edges", "819.6",
                           f"a review whose edges box leaves out 9.2 ({stage})", stage=stage)
        code, out = reasons(boxed(ra.APPROVE, edges={}), tmp_path=tmp_path, stage=stage)
        assert code == 1, f"819.6: a review with an empty edges box was let through ({stage})"
        for k in ("9.1", "9.2", "9.3"):
            assert any("edges" in line and k in line for line in out), \
                f"819.6: a review with an empty edges box was rejected, but no reason names {k} ({stage}):\n" + "\n".join(out)
        ra.assert_rejected(tmp_path, boxed(ra.APPROVE, edges="none"), r"\bedges\b", "819.6",
                           f"a review whose edges box says none on a plan with criteria ({stage})", stage=stage)
        split = boxed(ra.APPROVE, edges={"S1.1": "covered"})
        split["asks"] = [{**ra.ASKS[0], "criterion": "S1.1"}, {**ra.ASKS[1], "criterion": "S2.1"}]
        ra.assert_rejected(tmp_path, split, r"edges.*S2\.1|S2\.1.*edges", "819.6",
                           f"a review of a split whose edges box leaves out S2.1 ({stage})", plan=ra.SPLIT, stage=stage)

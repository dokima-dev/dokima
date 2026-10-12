"""Every plan review judges each criterion's edge cases: exotic ones cut, normal-use ones missing.

Covers #537, story 2 of #531. The reviewer's prompt teaches the same guiding kinds as the planner's (error, timeout,
bad data, empty), with examples, saying other kinds count too. A plan review hands back `edge_cases` in review.json:
one row per criterion of the plan, {"criterion": "N.k", "cut": [...], "missing": [...]}, each list holding plain
lines (empty when there are none). Code rejects a plan review that skips a criterion, naming it.

Every check runs the real commands the workflow runs on a review, through tests/test_review_asks.py's helpers, on a
plan for issue 9 with criteria 9.1 to 9.3, or a two-story split with S1.1 and S2.1.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_review_asks as ra  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROMPT = open(os.path.join(ROOT, "dokima", "roles", "reviewer.md")).read()
STORY_IDS = ("9.1", "9.2", "9.3")


def section(text, title):
    """The markdown section under the heading starting with title, up to the next heading."""
    found = re.search(rf"^#+ {re.escape(title)}[^\n]*\n(.*?)(?=^#|\Z)", text, re.S | re.M)
    return found.group(1) if found else None


def rows(ids, **change):
    """One edge case judgment per criterion, nothing cut or missing, with `change` merged in."""
    return [{"criterion": c, "cut": [], "missing": [], **change} for c in ids]


def test_the_reviewers_prompt_gives_the_guiding_kinds_with_examples_and_says_other_kinds_count(record_property):
    """The reviewer's prompt gives four guiding edge case kinds with examples, and says others count.

    Proves 537.1. Reads the Edge cases section of the reviewer's prompt and checks it holds one bullet per kind,
    starting with the kind in bold and giving an example after "Example:", and a line saying other kinds count too.
    """
    record_property("proves", "537.1")
    body = section(PROMPT, "Edge cases")
    assert body is not None, "537.1: the reviewer's prompt has no Edge cases section"
    for kind in ["Error", "Timeout", "Bad data", "Empty"]:
        bullet = re.search(rf"^- \*\*{kind}[^*]*\*\*(.*)$", body, re.M)
        assert bullet, f"537.1: the reviewer's Edge cases section has no bullet for {kind}"
        example = bullet.group(1).partition("Example:")[2].strip()
        assert example, f"537.1: the reviewer's {kind} bullet gives no example after 'Example:'"
    assert re.search(r"other kinds count", body, re.I), \
        "537.1: the reviewer's Edge cases section never says other kinds count too"


def test_a_plan_review_lists_the_exotic_cases_it_cuts_and_the_normal_use_cases_missing(record_property, tmp_path):
    """Each plan review lists, per criterion, the exotic edge cases cut and normal-use ones missing.

    Proves 537.2. The reviewer's prompt shows the review.json shape with an edge_cases list of rows holding criterion,
    cut and missing. A plan review whose rows list a cut case and a missing case passes the real check, and so does
    one with nothing cut or missing (empty lists). A row whose cut or missing is not a list of plain lines (a bare
    string, left out, or a blank line) is rejected, naming edge_cases and that criterion.
    """
    record_property("proves", "537.2")
    shape = PROMPT.partition("# What you hand back")[2]
    assert re.search(r'"edge_cases"\s*:\s*\[\s*\{\s*"criterion"\s*:[^}]*"cut"\s*:\s*\[[^}]*"missing"\s*:\s*\[', shape), \
        ('537.2: the review.json shape in reviewer.md has no edge_cases list of '
         '{"criterion": "N.k", "cut": [...], "missing": [...]}')
    judged = rows(STORY_IDS)
    judged[0] = {"criterion": "9.1", "cut": ["The disk fills up while the test runs."],
                 "missing": ["The issue has no comments."]}
    ra.assert_passes(tmp_path, {**ra.BLOCK, "edge_cases": judged}, "537.2",
                     "a plan review listing a cut case and a missing case")
    ra.assert_passes(tmp_path, {**ra.APPROVE, "edge_cases": rows(STORY_IDS)}, "537.2",
                     "a plan review with nothing cut and nothing missing")
    for why, bad in (("cut given as a bare string", {"cut": "The disk fills up."}),
                     ("missing given as a bare string", {"missing": "No comments."}),
                     ("a blank line in missing", {"missing": [" "]})):
        judged = rows(STORY_IDS)
        judged[1] = {**judged[1], **bad}
        ra.assert_rejected(tmp_path, {**ra.APPROVE, "edge_cases": judged}, r"edge_cases.*9\.2|9\.2.*edge_cases",
                           "537.2", f"a plan review with {why} for 9.2")
    judged = rows(STORY_IDS)
    del judged[2]["missing"]
    ra.assert_rejected(tmp_path, {**ra.APPROVE, "edge_cases": judged}, r"edge_cases.*9\.3|9\.3.*edge_cases",
                       "537.2", "a plan review whose row for 9.3 leaves out missing")


def test_a_plan_review_that_skips_a_criterions_edge_cases_is_rejected_naming_it(record_property, tmp_path):
    """A plan review that skips a criterion's edge cases is rejected, naming that criterion.

    Proves 537.3. A plan review judging all of 9.1 to 9.3 passes; one with no row for 9.2 is rejected naming 9.2;
    one with no edge_cases at all is rejected naming 9.1. On a split, a review judging S1.1 but not S2.1 is rejected
    naming S2.1. A code review needs no edge_cases, so one without them still passes.
    """
    record_property("proves", "537.3")
    ra.assert_passes(tmp_path, {**ra.APPROVE, "edge_cases": rows(STORY_IDS)}, "537.3",
                     "a plan review judging every criterion's edge cases")
    ra.assert_rejected(tmp_path, {**ra.APPROVE, "edge_cases": rows(("9.1", "9.3"))}, r"edge_cases.*9\.2|9\.2.*edge_cases",
                       "537.3", "a plan review that skips 9.2's edge cases")
    no_edges = {k: v for k, v in ra.APPROVE.items() if k != "edge_cases"}
    ra.assert_rejected(tmp_path, no_edges, r"edge_cases.*9\.1|9\.1.*edge_cases",
                       "537.3", "a plan review with no edge_cases at all")
    split = {**ra.APPROVE, "asks": [{**ra.ASKS[0], "criterion": "S1.1"}, {**ra.ASKS[1], "criterion": "S2.1"}],
             "tests": [], "edge_cases": rows(("S1.1",))}
    ra.assert_rejected(tmp_path, split, r"edge_cases.*S2\.1|S2\.1.*edge_cases",
                       "537.3", "a plan review of a split that skips S2.1's edge cases", plan=ra.SPLIT)
    ra.assert_passes(tmp_path, no_edges, "537.3", "a code review with no edge_cases", stage="pr")

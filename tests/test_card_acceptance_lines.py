"""A criterion's card shows one Acceptance test line per test that proves it, never an edge case's own test.

Since #655 every test filed under a criterion showed as an Acceptance test line, so an edge case's own test showed
twice: as an Acceptance test and again in the Edge cases fold. The card draws an edge case's own test only in the fold.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from test_card_not_verified import ASK, draw, story, under  # noqa: E402

import test_card_not_verified as base  # noqa: E402

MAIN, EDGE = "tests/test_a.py::test_one", "tests/test_a.py::test_empty"
base.TESTS[EDGE] = {"verified_by": "An empty input is refused.", "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L9"}


def with_edge(test):
    """A plan whose first criterion has one edge case covered by `test`, filed under it beside its own test."""
    h = story({"40.1": [MAIN] + ([test] if test != MAIN else []), "40.2": [MAIN]})
    h["acceptance_criteria"][0]["edge_cases"] = [{"case": "An empty input is refused.", "test": test}]
    return h


def test_an_edge_cases_own_test_is_not_an_acceptance_test_line():
    """A criterion with its own test and an edge case's own test shows one Acceptance test line, its own."""
    seen = under(draw(with_edge(EDGE)), "First thing works", "card")
    assert seen.count("Acceptance test") == 1, f"the edge case's own test also shows as an Acceptance test: {seen}"
    assert "The first thing runs." in seen, f"the criterion's own test is missing: {seen}"


def test_a_test_shared_with_an_edge_case_stays_the_acceptance_test():
    """When the criterion's only test also covers its edge case, that test still shows as its Acceptance test."""
    seen = under(draw(with_edge(MAIN)), "First thing works", "card")
    assert seen.count("Acceptance test") == 1 and "The first thing runs." in seen, \
        f"the shared test does not show once as the Acceptance test: {seen}"

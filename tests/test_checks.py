import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import checks  # noqa: E402


def test_long_criteria_get_short_check_names(record_property):
    record_property("proves", "29.1")
    assert checks.check_name("40.1", "x" * 100) == "40.1 · " + "x" * 57 + "..."


def test_annotation_links_permanently_to_the_tests_first_line(record_property):
    record_property("proves", "29.2")
    xml = ('<testsuites><testsuite>'
           '<testcase file="tests/t.py" line="4" name="test_ok"/>'
           '<testcase file="tests/t.py" line="9" name="test_bad"><failure/></testcase>'
           '</testsuite></testsuites>')
    ok, bad = checks.annotations(xml, "o/r", "abc123", "40.1")
    assert ok.startswith("::notice file=tests/t.py,line=5,title=40.1 passed::")
    assert ok.endswith("view the test: https://github.com/o/r/blob/abc123/tests/t.py#L5")
    assert bad.startswith("::error file=tests/t.py,line=10,title=40.1 failed::")


def test_full_suite_runs_every_test_on_every_pull_request(record_property):
    """The merge gate still runs every test, in parallel, exactly as today.

    Proves 29.4 and 539.3. Reads full-suite.yml and checks it still installs only pytest and pytest-xdist, still
    runs every test spread over all cores with `-n auto`, and never uses testmon, which only code reviews use."""
    record_property("proves", "29.4")
    record_property("proves", "539.3")
    path = os.path.join(os.path.dirname(__file__), "..", ".github/workflows/full-suite.yml")
    lines = [line.strip() for line in open(path)]
    assert "name: full suite" in lines
    assert "pull_request_target:" in lines
    assert "name: all tests" in lines
    assert any(line.startswith("- run: pytest") and line.endswith(" tests") for line in lines)
    assert "- run: pip install -q pytest pytest-xdist" in lines, "539.3: the merge gate no longer installs exactly pytest and pytest-xdist"
    assert "- run: pytest -q -p no:cacheprovider -n auto tests" in lines, \
        "539.3: the merge gate no longer runs every test in parallel with -n auto"
    assert not any("testmon" in line for line in lines), "539.3: the merge gate uses testmon, so it may skip tests"

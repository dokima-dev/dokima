"""Tests for #600: the Setup issue says when main lets a branch behind it merge.

GitHub only stops a merge of code tested against an older main when main's rule demands an up-to-date branch (the
"strict" flag of its required checks). Dokima cannot set that rule itself, so its audit must name it on the Setup issue
when it is off. The test runs `python3 -m dokima.audit acme/widgets` from outside, against the fake `gh` of
tests/fake_gh.py (through tests/test_audit_cli.py's Audit helper), whose state key "strict" sets that flag per branch.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from test_audit_cli import Audit, body_lines, clean, created  # noqa: E402

UP_TO_DATE = re.compile(r"up[ -]to[ -]date", re.I)


def up_to_date_lines(issue):
    """Every line of the Setup issue's body that talks about being up to date."""
    return [l for l in body_lines(issue["body"]) if UP_TO_DATE.search(l)]


def test_setup_issue_names_main_not_demanding_an_up_to_date_branch(record_property, tmp_path):
    """The Setup issue says when main's rule does not demand an up-to-date branch.

    Proves 600.1. Runs the audit twice. First main's rule demands an up-to-date branch and one label is missing, so a Setup issue
    opens: none of its lines may talk about being up to date. Then main's rule drops that demand and nothing else is
    off: the audit must open a Setup issue with exactly one line naming `main` and being up to date."""
    record_property("proves", "600.1")
    good = clean()
    good["strict"] = {"main": True}
    del good["labels"]["plan"]
    a = Audit(tmp_path / "good", good)
    a.run("600.1")
    _, issue = created(a, "600.1")
    assert not up_to_date_lines(issue), \
        f"600.1: main's rule demands an up-to-date branch, yet the Setup issue says {up_to_date_lines(issue)}"

    bad = clean()
    bad["strict"] = {"main": False}
    b = Audit(tmp_path / "bad", bad)
    b.run("600.1")
    made = [w["number"] for w in b.state()["writes"] if w["kind"] == "create"]
    assert made, ("600.1: main's rule lets a branch behind main merge, but the audit opened no Setup issue saying so"
                  f"\n{b.why()}")
    _, issue = created(b, "600.1")
    lines = [l for l in up_to_date_lines(issue) if re.search(r"(?<![\w-])main(?![\w-])", l)]
    assert len(lines) == 1, ("600.1: the Setup issue should have one line saying main's rule must demand an up-to-date "
                             f"branch, found {lines} in {body_lines(issue['body'])}")

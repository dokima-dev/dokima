from pathlib import Path

WIKI = Path(__file__).parent.parent / "docs" / "wiki"


def read(name):
    return (WIKI / name).read_text()


def test_writing_issues(record_property):
    """The wiki says the planner writes the criteria, in today's wording.

    Proves 72.1."""
    record_property("proves", "72.1")
    text = read("Writing-issues.md")
    assert "criteria" in text
    assert "done when" not in text.lower()
    assert "`work` label" not in text


def test_the_card(record_property):
    """The card page covers issues and pull requests and names `/work` as the plan approval.

    Proves 72.2."""
    record_property("proves", "72.2")
    text = read("The-card.md")
    assert "issue" in text and "PR" in text
    assert "/work" in text


def test_home(record_property):
    """Home names `/work`, not the retired `work` label, as how a plan is approved.

    Proves 72.3."""
    record_property("proves", "72.3")
    text = read("Home.md")
    assert "/work" in text
    assert "`work` label" not in text

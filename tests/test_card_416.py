"""#416: code shows as written, Done comes last, stats come last, and lists name issues by full address."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, body, card  # noqa: E402


def test_code_shows_as_written_and_other_words_stay_escaped():
    """Text inside inline code or a code block keeps <, > and &; text outside is escaped."""
    out = card.escape("a <b> `x<y>` &\n```\n<z>\n```")
    assert "`x<y>`" in out and "\n<z>\n" in out and "&lt;b&gt;" in out and "&amp;" in out


def test_definition_of_done_is_the_last_line_below_the_fold():
    """A planned card puts its Definition of Done after the Original issue fold."""
    top = "<!-- dokima-card -->\ncard\n" + body.FOLDED + "\n<!-- /dokima-card -->\n\n" + body.DONE + "\n**Definition of Done:** x"
    new = body.redraw("My ask.", top)
    assert new.rstrip().endswith("**Definition of Done:** x")
    assert new.index("Original issue") < new.index("**Definition of Done:**")
    assert body.ask(new) == "My ask."


def test_the_stats_line_comes_last_below_next():
    """Next goes right above the stats line, which ends the comment."""
    text = agent.with_next("record\n\n" + agent.STATS + "\nstats", "**Next:** go")
    assert text.rstrip().splitlines()[-1] == "stats" and "**Next:** go\n\n" + agent.STATS in text


def test_lists_name_issues_by_full_address(monkeypatch):
    """Link lines and Sources name issues by full address, not #N."""
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    line = card.link_lines("o/r", {"blocked_by": [7]})[0]
    assert "https://github.com/o/r/issues/7" in line and "#7" not in line
    assert card.full_refs("o/r", "#9") == "https://github.com/o/r/issues/9"

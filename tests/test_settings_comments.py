"""Tests for #721: a comment after a settings value is not part of it.

The settings file (`.dokima/agents.yml`) is read by `dokima/setup.py` `read_settings()`. A line like
`agent: codex  # the fast one` used to read as `codex  # the fast one`, so the role named an agent that does not exist.

Each test writes a settings file into a temp folder, points `DOKIMA_SETTINGS` at it and asks `dokima.agents.role_settings()`
what the role runs on, the same call a run makes before it starts its agent.
"""
import textwrap

from dokima import agents


def _role(tmp_path, monkeypatch, text, role="planner"):
    """The role's settings as a run reads them from the given text."""
    path = tmp_path / "agents.yml"
    path.write_text(textwrap.dedent(text))
    monkeypatch.setenv("DOKIMA_SETTINGS", str(path))
    return agents.role_settings(role)


def test_inline_comment_not_in_value(tmp_path, monkeypatch, record_property):
    """Comments after the agent, key and model lines are left out of the values.

    Writes a settings file whose agent, key and model lines each end in a `# ...` comment, and checks the role reads
    the bare agent, key and model, the same as lines with no comment. Proves 721.1."""
    record_property("proves", "721.1")
    got = _role(tmp_path, monkeypatch, """\
        subscriptions:
          fast:
            agent: codex  # the fast one
            key: CODEX_KEY # stored by setup
        roles:
          planner:
            subscription: fast
            model: gpt-5  # newest
        """)
    assert got == {"agent": "codex", "model": "gpt-5", "key": "CODEX_KEY"}, (
        f"721.1: a comment after a value was kept as part of it; the planner reads {got}")


def test_quoted_value_with_comment(tmp_path, monkeypatch, record_property):
    """A quoted agent name followed by a comment reads as the bare name.

    Writes `agent: "codex"  # note` and checks the role's agent is `codex`, with no quote or comment left on it. Proves 721.1."""
    record_property("proves", "721.1")
    got = _role(tmp_path, monkeypatch, """\
        subscriptions:
          fast:
            agent: "codex"  # note
            key: CODEX_KEY
        roles:
          planner:
            subscription: fast
            model: gpt-5
        """)
    assert got["agent"] == "codex", (
        f"721.1: a quoted agent with a comment after it reads as {got['agent']!r}, not 'codex'")


def test_comment_on_section_line(tmp_path, monkeypatch, record_property):
    """A comment on a section line still lets the roles under it be read.

    Writes `roles:  # who runs what` above a planner on Codex, and checks the planner runs on Codex rather than
    falling back to the default agent because the comment was read as the section's value. Proves 721.1."""
    record_property("proves", "721.1")
    got = _role(tmp_path, monkeypatch, """\
        subscriptions:  # where keys live
          fast:
            agent: codex
            key: CODEX_KEY
        roles:  # who runs what
          planner:
            subscription: fast
            model: gpt-5
        """)
    assert got == {"agent": "codex", "model": "gpt-5", "key": "CODEX_KEY"}, (
        f"721.1: a comment on a section line hid the roles under it; the planner reads {got}")

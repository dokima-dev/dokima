import os
from rules_files import rules_text

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_agents_md_holds_the_design(record_property):
    record_property("proves", "78.1")
    text = rules_text()
    for heading in ("## The picture", "## The core rule", "## Principles", "## Roles", "## The flow", "## Decisions log"):
        assert heading in text, f"78.1: AGENTS.md is missing {heading}"
    assert "remote engineers" in text and "never edits what another stage owns" in text
    assert not os.path.exists(os.path.join(ROOT, "DESIGN.md")), "78.1: the design must live only in AGENTS.md"


def test_other_agents_files_point_to_agents_md(record_property):
    record_property("proves", "78.2")
    assert open(os.path.join(ROOT, "CLAUDE.md")).read().strip() == "@AGENTS.md", "78.2: CLAUDE.md must only point to AGENTS.md"

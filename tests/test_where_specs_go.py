"""AGENTS.md tells every session, human or agent, where the owner's specs go.

Issue #336 asks for a short rule with an example in AGENTS.md: every spec, answer or scope change lands on GitHub,
on an existing issue as a comment, an issue's original text stays frozen, and a new idea becomes a new issue. These
tests read the `## Where specs go` section of AGENTS.md and check each promise is written there, in plain words.
Matching ignores case, line breaks and repeated spaces, so the worker may wrap lines freely.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
HEADING = "## Where specs go"


def section():
    """Returns the lines of the specs section of AGENTS.md, or None when missing."""
    lines = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read().splitlines()
    if HEADING not in [line.strip() for line in lines]:
        return None
    start = [line.strip() for line in lines].index(HEADING) + 1
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return lines[start:end]


def flat(lines):
    """Joins the section into one lower-case line with single spaces, so wrapping never matters."""
    return re.sub(r"\s+", " ", " ".join(lines)).lower()


def require(criterion, phrases):
    """Fails naming the criterion and every phrase the section lacks."""
    lines = section()
    assert lines is not None, f"{criterion}: AGENTS.md has no section headed '{HEADING}'"
    text = flat(lines)
    missing = [p for p in phrases if p.lower() not in text]
    assert not missing, f"{criterion}: the '{HEADING}' section of AGENTS.md does not say: {missing}"


def test_section_is_a_short_rule_with_an_example(record_property):
    """AGENTS.md has a short "Where specs go" section with a rule and an example.

    Finds the section by its heading, and checks it holds at most 12 non-empty lines and at least one line that
    starts with "Example:". Proves 336.1."""
    record_property("proves", "336.1")
    lines = section()
    assert lines is not None, f"336.1: AGENTS.md has no section headed '{HEADING}'"
    filled = [line for line in lines if line.strip()]
    assert filled, "336.1: the 'Where specs go' section is empty"
    assert len(filled) <= 12, f"336.1: the 'Where specs go' section has {len(filled)} non-empty lines, more than 12"
    examples = [line for line in filled if re.sub(r"^[\s>*_-]*", "", line).lower().startswith("example:")]
    assert examples, "336.1: the 'Where specs go' section has no line starting with 'Example:'"


def test_every_spec_lands_on_github(record_property):
    """AGENTS.md says every spec, answer or scope change lands on GitHub, never in chat.

    Checks the section names all three kinds of words and both halves of the rule. Proves 336.2."""
    record_property("proves", "336.2")
    require("336.2", ["every spec, answer or scope change", "lands on github", "never only in chat"])


def test_existing_issue_gets_a_comment(record_property):
    """AGENTS.md says words on an existing issue go in as a comment.

    Checks the section says "as a comment", names a `/plan` comment for when the planner should pick it up, and a
    plain comment on an issue left for later. Proves 336.3."""
    record_property("proves", "336.3")
    require("336.3", ["existing issue", "as a comment", "a `/plan` comment when the planner should pick it up",
                      "a plain comment on an issue left for later"])


def test_original_text_is_frozen(record_property):
    """AGENTS.md says an issue's original text is frozen: nobody edits it, and changes are comments.

    Checks the section says all three parts of the rule. Proves 336.4."""
    record_property("proves", "336.4")
    require("336.4", ["an issue's original text is frozen", "nobody edits it", "changes are comments"])


def test_new_idea_is_a_new_issue(record_property):
    """AGENTS.md says a new idea becomes a new issue, with the spec in its body.

    Checks the section says both parts of the rule. Proves 336.5."""
    record_property("proves", "336.5")
    require("336.5", ["a new idea becomes a new issue", "with the spec in its body"])

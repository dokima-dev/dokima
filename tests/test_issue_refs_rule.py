"""AGENTS.md tells agents to name an issue with a link and a few plain words.

Issue #355 asks for a rule in AGENTS.md: whenever an agent or assistant refers the owner to an issue or pull request,
it writes the number as a clickable link followed by a few plain words saying what it is about, never a bare number,
with the owner's example. These tests read AGENTS.md and look for one paragraph or bullet that states the whole rule,
and for the example as a real markdown link. Matching ignores case, line breaks and repeated spaces inside a
paragraph, so the worker may wrap lines freely.
"""
import os
import re
from rules_files import rules_text

ROOT = os.path.join(os.path.dirname(__file__), "..")
EXAMPLE = "[#289](https://github.com/dokima-dev/dokima/issues/289) (raises and answers)"


def blocks():
    """Returns AGENTS.md split into paragraphs and bullets, each flattened to one lower-case line."""
    text = rules_text()
    parts = re.split(r"\n\s*\n|\n(?=\s*[-*] )", text)
    return [re.sub(r"\s+", " ", part).strip().lower() for part in parts if part.strip()]


def test_rule_says_link_plus_plain_words_never_bare(record_property):
    """AGENTS.md says every issue reference is a link plus plain words, never a bare number.

    Looks for one paragraph or bullet of AGENTS.md that says, together, that an agent or assistant referring the owner
    to an issue or pull request writes the number as a clickable link, followed by a few plain words saying what it is
    about, and never a bare number. A rule split over unrelated places, or missing any part, fails. Proves 355.1."""
    record_property("proves", "355.1")
    phrases = ["agent or assistant", "refers the owner to an issue or pull request", "clickable link",
               "a few plain words", "what it is about", "never a bare number"]
    best = max(blocks(), key=lambda b: sum(p in b for p in phrases))
    missing = [p for p in phrases if p not in best]
    assert not missing, ("355.1: no single paragraph or bullet of AGENTS.md states the whole rule; "
                         f"the closest one lacks: {missing}")


def test_rule_carries_the_owners_example(record_property):
    """AGENTS.md shows the owner's example: a link to #289 with "(raises and answers)".

    Checks the paragraph that states the rule holds the example written exactly as a markdown link whose text and
    address name the same issue, followed by its plain words, so the example renders as a working link. Proves 355.2."""
    record_property("proves", "355.2")
    rule = [b for b in blocks() if "never a bare number" in b]
    assert rule, "355.2: AGENTS.md has no paragraph saying 'never a bare number', so the example has no rule to sit in"
    assert any(EXAMPLE.lower() in b for b in rule), (
        f"355.2: the rule's paragraph in AGENTS.md does not show the example {EXAMPLE}")
    link = re.search(r"\[#(\d+)\]\(https://github\.com/dokima-dev/dokima/issues/(\d+)\) \(([a-z][a-z ]+)\)",
                     next(b for b in rule if EXAMPLE.lower() in b))
    assert link and link.group(1) == link.group(2), "355.2: the example's link text and address name different issues"

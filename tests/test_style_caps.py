"""#470: every text the owner reads is held to its cap, plain fields hold no code, and the prompt states the same caps."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import words  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
NAMES = {"summary": "summary", "user_story": "user_story", "criterion": "criterion (acceptance or non-functional)",
         "nfr_why": "a non-functional requirement's why", "out_of_scope": "an out_of_scope line", "feature": "feature",
         "story_title": "a story's title", "story_user_story": "a story's user_story", "raise_label": "a raise's label",
         "question": "a question for the owner", "blocker": "a blocker", "issue": "an issue found",
         "evidence": "evidence", "answer_why": "an answer's why", "previous_step": "a previous_step line",
         "work_evidence": "the worker's own test run (evidence)", "test_change": "a test change reason"}


def test_the_prompt_states_exactly_the_caps_code_checks():
    """style.md lists every field with the same cap as code, so no agent is caught off guard."""
    text = open(os.path.join(ROOT, "dokima", "roles", "style.md")).read()
    rows = dict(re.findall(r"^\| (.+?) \| (\d+) \|$", text, re.M))
    assert {k: int(v) for k, v in rows.items()} == {NAMES[f]: c for f, c in words.CAPS.items()}


def test_a_text_over_its_cap_or_naming_code_is_rejected(monkeypatch):
    """Over the cap, or code in a plain field, is rejected; evidence may name files."""
    monkeypatch.delenv("STYLE_SOFT", raising=False)
    long = " ".join(["word"] * 21)
    assert words.style({"acceptance_criteria": [{"text": long}]})[1]
    assert words.style({"acceptance_criteria": [{"text": "Edits redraw `card.py` output."}]})[1]
    assert not words.style({"raises": [{"kind": "blocker", "label": "Weak test", "text": "Fails.",
                                        "evidence": "`tests/test_x.py::test_a` passes on a stub."}]})[1]
    assert not words.style({"acceptance_criteria": [{"text": "Editing an issue redraws its card.",
                                                     "words": " ".join(["owner"] * 80)}]})[1]


def test_the_final_check_flags_instead_of_rejecting(monkeypatch):
    """With STYLE_SOFT, as the workflow's last check runs, a long text is listed, not rejected."""
    monkeypatch.setenv("STYLE_SOFT", "1")
    listed, rejected = words.style({"user_story": " ".join(["word"] * 30)})
    assert listed and not rejected


def test_short_references_in_bullet_prose_stay_short():
    """#N in a raise becomes a plain link, so GitHub does not draw its title; code spans are untouched."""
    from dokima import card
    out = card.short_refs("o/r", "see #438 and `#9` today")
    assert "[#438](https://github.com/o/r/issues/438)" in out and "`#9`" in out

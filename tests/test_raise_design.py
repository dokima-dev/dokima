"""AGENTS.md records the raise design; the shared prompt section teaches it by example (#302).

The owner wants one place in AGENTS.md that says what code raises by itself and what agents raise by judgment, with
code's who-can-address-whom table copied row for row and the two tiers of autonomy, and wants the one section the
planner, worker and reviewer prompts share ("# Raising and answering", word for word the same in all three, from
#300) to teach raising with an example of every kind and every common instance, to ask agents to speak up, and to end
with a short checklist.

What these tests pin, so the worker knows the exact shape:
- AGENTS.md holds exactly one "## Raising and answering" section (running to the next "## " heading) and no
  "## Questions" section any more: today's Questions section folds into it.
- Both that section and the shared prompt section hold one bullet per thing code raises by itself, each starting
  with its name in bold, exactly as in CODE_RAISES, and holding "Example:" followed by an example.
- The AGENTS.md section holds a Markdown table whose header starts "| Raised by | To |"; each body row names one role
  in its first cell and the ones it may send a question or blocker to in its second, separated by commas, "or" or
  "and"; words in parentheses are not names, and a route through someone (raises.THROUGH) is written there as
  "(through the reviewer)". The rows must be exactly raises.TABLE.
- The AGENTS.md section holds a bullet starting "**Always on:**" and one starting "**On autopilot only:**".
- The shared prompt section holds an example raise (JSON, opening with "kind") for every instance in INSTANCES, by
  its exact label, each one code accepts and each carrying evidence; it says "never raise them yourself" about what
  code raises; it asks agents not to stay quiet; and its last five lines are the checklist, one "- " item each ending
  with "?", after its last example.
"""
import json
import os
import re

import pytest

from dokima import raises

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROLE_FILES = ("planner", "worker", "reviewer")
PROMPT_HEADING = "# Raising and answering"
AGENTS_HEADING = "## Raising and answering"

# What code detects and raises itself, by the name each bullet opens with, and words that name it in a plain list.
CODE_RAISES = {
    "Work outside the plan": "outside the plan",
    "A failing test": "failing test",
    "Red main": "red main",
    "A merge conflict": "merge conflict",
    "A rejected hand-back": "hand-back",
    "A workflow file change": "workflow file",
    "Three blocks in a row": "three blocks in a row",
}

# Every instance the owner named: (kind, to, label).
INSTANCES = [
    ("question", "owner", "Two readings"),
    ("question", "owner", "Doubt: already fixed"),
    ("question", "owner", "Doubt: patches a symptom"),
    ("question", "owner", "Doubt: overlaps an open issue"),
    ("blocker", "planner", "Weak test"),
    ("blocker", "planner", "Test cannot pass"),
    ("blocker", "planner", "Wrong plan"),
    ("blocker", "planner", "No criterion"),
    ("issue", None, "Outside this issue"),
]

# The checklist the owner named, in order: words each item must hold.
CHECKLIST = ("weak test", "cannot pass", "no criterion", "doubt", "outside this issue")


def prompt_section(role):
    """The shared section of a role prompt, or None without one."""
    lines = open(os.path.join(ROOT, "dokima", "roles", f"{role}.md")).read().splitlines()
    at = [i for i, l in enumerate(lines) if l.strip() == PROMPT_HEADING]
    if len(at) != 1:
        return None
    end = next((j for j in range(at[0] + 1, len(lines)) if lines[j].startswith("# ")), len(lines))
    return "\n".join(lines[at[0]:end]).strip()


def agents_section(text=None):
    """The raising section of AGENTS.md, or None without exactly one.

    It runs from its heading to the next "## " heading."""
    if text is None:
        text = open(os.path.join(ROOT, "AGENTS.md")).read()
    lines = text.splitlines()
    at = [i for i, l in enumerate(lines) if l.strip() == AGENTS_HEADING]
    if len(at) != 1:
        return None
    end = next((j for j in range(at[0] + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return "\n".join(lines[at[0]:end]).strip()


def examples(text):
    """Every example raise in the text, parsed, with where it ends.

    One that does not parse fails the test."""
    found, dec = [], json.JSONDecoder()
    for m in re.finditer(r'\{\s*"kind"\s*:', text):
        try:
            obj, end = dec.raw_decode(text, m.start())
        except json.JSONDecodeError as e:
            pytest.fail(f"302.3: an example raise in the shared section is not valid JSON ({e}): {text[m.start():][:160]}")
        found.append((obj, end))
    return found


def table_rows(section):
    """The who-can-address-whom table in a section, as {role: (recipients, raw second cell)}.

    Finds the Markdown table whose header starts "| Raised by | To |" and reads each body row."""
    lines = section.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if [c.strip().lower() for c in l.strip().strip("|").split("|")][:2] == ["raised by", "to"]), None)
    if start is None:
        return None
    rows = {}
    for line in lines[start + 2:]:
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        role = re.sub(r"[*`]", "", cells[0]).strip().lower()
        cell = cells[1] if len(cells) > 1 else ""
        bare = re.sub(r"\([^)]*\)", " ", re.sub(r"[*`]", "", cell)).lower()
        names = tuple(w for w in re.split(r",|\bor\b|\band\b|\s+", bare) if w.strip() and w.strip() != "the")
        rows[role] = (tuple(n.strip() for n in names), cell)
    return rows


def table_problems(section):
    """How the table in a section differs from raises.TABLE and raises.THROUGH; empty when it matches."""
    rows = table_rows(section)
    if rows is None:
        return ["there is no table whose header starts '| Raised by | To |'"]
    problems = []
    for role, allowed in raises.TABLE.items():
        if role not in rows:
            problems.append(f"no row for the {role}")
        elif sorted(rows[role][0]) != sorted(allowed):
            problems.append(f"the {role}'s row says {list(rows[role][0])}, code says {list(allowed)}")
    for role in rows:
        if role not in raises.TABLE:
            problems.append(f"a row for {role!r}, which code's table does not have")
    for (src, dst), via in raises.THROUGH.items():
        if src in rows and f"through the {via}" not in rows[src][1].lower():
            problems.append(f"the {src}'s row does not say its raise to the {dst} goes through the {via}")
    return problems


def code_raise_bullets(section, crit):
    """Fails the test unless each thing code raises has one bullet with an example."""
    for name in CODE_RAISES:
        hits = [l for l in section.splitlines() if l.strip().startswith(f"- **{name}")]
        assert len(hits) == 1, f"{crit}: there is not exactly one bullet '- **{name}**' (found {len(hits)})"
        after = hits[0].split("Example:", 1)
        assert len(after) == 2 and len(after[1].strip()) >= 20, \
            f"{crit}: the bullet for '{name}' gives no example after 'Example:': {hits[0]}"


def test_agents_md_has_one_section_listing_what_code_raises_and_the_three_kinds(record_property):
    """AGENTS.md has one raising section: what code raises, the three kinds, doubt as a question.

    Reads AGENTS.md: exactly one "## Raising and answering" section and no separate "## Questions" one; it names all
    seven things code detects and raises itself, the three kinds (question, blocker, issue), and on one line names
    doubt about the ask as a question that carries its evidence.

    Proves 302.1."""
    record_property("proves", "302.1")
    text = open(os.path.join(ROOT, "AGENTS.md")).read()
    section = agents_section(text)
    assert section, f"302.1: AGENTS.md does not have exactly one '{AGENTS_HEADING}' section"
    assert not any(l.strip() == "## Questions" for l in text.splitlines()), \
        "302.1: AGENTS.md still has a separate '## Questions' section; raising must live in one section"
    low = section.lower()
    for name, words in CODE_RAISES.items():
        assert words in low, f"302.1: the raising section does not name '{name}' among what code raises itself"
    for kind in raises.KINDS:
        assert re.search(rf"\b{kind}\b", low), f"302.1: the raising section does not name the kind '{kind}'"
    lines = [l.lower() for l in section.splitlines() if "doubt about the ask" in l.lower()]
    assert any("question" in l and "evidence" in l for l in lines), \
        "302.1: the raising section does not name doubt about the ask as a question that carries its evidence"


def test_agents_md_table_matches_codes_table_row_for_row(record_property):
    """AGENTS.md's table says who may raise to whom, exactly as code's table does.

    Reads the table out of AGENTS.md and compares it with dokima/raises.py's TABLE and THROUGH, so the doc can never
    drift from code; then drops a row and changes another in a copy, and checks the comparison catches both.

    Proves 302.2."""
    record_property("proves", "302.2")
    section = agents_section()
    assert section, f"302.2: AGENTS.md does not have exactly one '{AGENTS_HEADING}' section"
    problems = table_problems(section)
    assert not problems, "302.2: the table in AGENTS.md differs from code's: " + "; ".join(problems)
    lines = section.splitlines()
    worker = next(i for i, l in enumerate(lines) if l.strip().startswith("|") and "worker" in l.split("|")[1].lower())
    dropped = "\n".join(lines[:worker] + lines[worker + 1:])
    assert table_problems(dropped), "302.2: the comparison did not notice a missing row"
    planner = next(i for i, l in enumerate(lines) if l.strip().startswith("|") and "planner" in l.split("|")[1].lower())
    widened = "\n".join(lines[:planner] + ["| planner | owner, worker |"] + lines[planner + 1:])
    assert table_problems(widened), "302.2: the comparison did not notice a widened row"


def test_agents_md_gives_the_two_tiers_of_autonomy(record_property):
    """AGENTS.md gives both tiers of the reviewer's autonomy: always on, and autopilot only.

    Reads the raising section: an "Always on:" bullet says the reviewer settles what is addressed to an agent and
    confirms issues before they are filed; an "On autopilot only:" bullet says it answers a question for you only
    with your own words as evidence.

    Proves 302.2."""
    record_property("proves", "302.2")
    section = agents_section()
    assert section, f"302.2: AGENTS.md does not have exactly one '{AGENTS_HEADING}' section"
    lines = [l.strip() for l in section.splitlines()]
    always = [l.lower() for l in lines if l.startswith("- **Always on:**")]
    auto = [l.lower() for l in lines if l.startswith("- **On autopilot only:**")]
    assert len(always) == 1, "302.2: the raising section has no single '- **Always on:**' bullet"
    assert len(auto) == 1, "302.2: the raising section has no single '- **On autopilot only:**' bullet"
    for word in ("reviewer", "settles", "agent", "confirms", "issue", "filed"):
        assert word in always[0], f"302.2: the Always on tier does not say '{word}': {always[0]}"
    for word in ("reviewer", "question", "own words", "evidence"):
        assert word in auto[0], f"302.2: the On autopilot only tier does not say '{word}': {auto[0]}"


def test_the_shared_prompt_section_has_an_example_of_every_kind_and_instance(record_property):
    """The shared prompt section shows an example of every kind and instance you named.

    Parses every example raise in the section the three prompts share and checks one exists for each of: a question
    about two readings; doubts about the ask (already fixed, patches a symptom, overlaps an open issue); blockers for a
    weak test, a test that cannot pass, a wrong plan and an ask with no criterion; and an issue outside this one. Each
    must be accepted by code for some agent and carry its evidence.

    Proves 302.3."""
    record_property("proves", "302.3")
    found = {role: prompt_section(role) for role in ROLE_FILES}
    for role, text in found.items():
        assert text, f"302.3: dokima/roles/{role}.md has no single '{PROMPT_HEADING}' section"
    assert len(set(found.values())) == 1, "302.3: the shared section is not the same text in all three prompts"
    exs = [e for e, _ in examples(found["planner"])]
    for kind, to, label in INSTANCES:
        hits = [e for e in exs if e.get("kind") == kind and e.get("label") == label and e.get("to") == to]
        want = f"a {kind}" + (f" to the {to}" if to else "") + f" labelled '{label}'"
        assert hits, f"302.3: the shared section has no example of {want}"
        for e in hits:
            assert str(e.get("evidence") or "").strip(), f"302.3: the example {want} carries no evidence"
            assert any(not raises.check_raises(r, [e]) for r in ROLE_FILES), \
                f"302.3: code rejects the example {want} for every agent"


def test_the_shared_prompt_section_asks_agents_to_speak_up_and_ends_with_the_checklist(record_property):
    """The shared prompt section asks agents to speak up and ends with your five-question checklist.

    Reads the shared section: it tells agents not to stay quiet, and its last five lines, after its last example, are
    the checklist in your order: a weak test, a test that cannot pass, an ask with no criterion, a doubt about what
    you meant, a problem outside this issue, each a question.

    Proves 302.4."""
    record_property("proves", "302.4")
    text = prompt_section("planner")
    assert text, f"302.4: dokima/roles/planner.md has no single '{PROMPT_HEADING}' section"
    assert re.search(r"stay(ing)? quiet", text, re.I), "302.4: the shared section does not ask agents not to stay quiet"
    lines = text.splitlines()
    last = lines[-5:]
    for line, words in zip(last, CHECKLIST):
        assert line.strip().startswith("- ") and line.strip().endswith("?"), \
            f"302.4: the section does not end with five '- ...?' checklist items; found: {line!r}"
        assert words in line.lower(), f"302.4: the checklist item {line!r} should ask about '{words}'"
    exs = examples(text)
    assert exs, "302.4: the shared section has no example raises"
    tail_start = len("\n".join(lines[:-5]))
    assert exs[-1][1] <= tail_start, "302.4: the checklist does not come after the section's last example"


def test_agents_md_and_the_prompt_give_an_example_of_everything_code_raises(record_property):
    """AGENTS.md and the shared prompt section each show an example of everything code raises.

    Checks both for one bullet per thing code raises (work outside the plan, a failing test, red main, a merge
    conflict, a rejected hand-back, a workflow file change, three blocks in a row), each with an example, and that
    the prompt tells agents never to raise these themselves.

    Proves 302.5."""
    record_property("proves", "302.5")
    section = agents_section()
    assert section, f"302.5: AGENTS.md does not have exactly one '{AGENTS_HEADING}' section"
    code_raise_bullets(section, "302.5 (AGENTS.md)")
    text = prompt_section("planner")
    assert text, f"302.5: dokima/roles/planner.md has no single '{PROMPT_HEADING}' section"
    code_raise_bullets(text, "302.5 (shared prompt section)")
    assert "never raise them yourself" in text.lower(), \
        "302.5: the shared prompt section does not tell agents never to raise these themselves"


def test_every_example_raise_in_agents_md_and_the_prompts_is_one_code_accepts(record_property):
    """No example teaches a raise that code would reject.

    Parses every example raise in AGENTS.md's raising section and in the shared prompt section, needs at least nine
    in the prompt, and checks each passes dokima/raises.py's check for at least one agent; a copy with a kind code
    does not have is caught.

    Proves 302.6."""
    record_property("proves", "302.6")
    text = prompt_section("planner")
    assert text, f"302.6: dokima/roles/planner.md has no single '{PROMPT_HEADING}' section"
    exs = [e for e, _ in examples(text)]
    assert len(exs) >= len(INSTANCES), f"302.6: the shared section has {len(exs)} example raises, fewer than {len(INSTANCES)}"
    section = agents_section() or ""
    for e in exs + [e for e, _ in examples(section)]:
        ok = [r for r in ROLE_FILES if not raises.check_raises(r, [e])]
        assert ok, f"302.6: code rejects the example {e} for every agent: {raises.check_raises('reviewer', [e])}"
    bad = {**exs[0], "kind": "concern"}
    assert all(raises.check_raises(r, [bad]) for r in ROLE_FILES), "302.6: the check let a made-up kind through"

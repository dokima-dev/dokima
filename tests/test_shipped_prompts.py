"""Tests for #817: shipped prompts fit any repo; the planner knows when to ask.

Each prompt is built the way agent.yml builds it: `python3 -m dokima.prompt ROLE GRADE`, run in a folder whose
`.dokima/settings.yaml` holds the settings a test names (none for Dokima's defaults). Four prompts are built: the
planner with the plan grade, the worker with the result grade, and the reviewer with each grade.

The shipped prompts are every file in dokima/roles/. Dokima's own code files are every file under dokima/, tests/,
.github/ and tools/, less markdown, caches and the test data under tests/samples/ and tests/fixtures/. The settings
these tests set are planner.max_questions and river.max_blocks, the two limits the prompts state.
"""
import difflib
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROLES = os.path.join(ROOT, "dokima", "roles")
RAISING = os.path.join(ROLES, "raising.md")
PROMPTS = (("planner", "plan-grade"), ("worker", "result-grade"), ("reviewer", "plan-grade"),
           ("reviewer", "result-grade"))
CODE_DIRS = ("dokima", "tests", ".github", "tools")
NOT_CODE = (os.path.join("tests", "samples"), os.path.join("tests", "fixtures"))


def built(tmp, role, grade, settings=None):
    """The prompt agent.yml builds for ROLE with GRADE, under the repo settings SETTINGS.

    Runs `python3 -m dokima.prompt ROLE GRADE` in a temp folder, Dokima's code first on the path; fails the test,
    with the error, when the prompt is not built."""
    folder = os.path.join(str(tmp), f"{role}-{grade}")
    os.makedirs(os.path.join(folder, ".dokima"), exist_ok=True)
    if settings is not None:
        with open(os.path.join(folder, ".dokima", "settings.yaml"), "w") as f:
            f.write(settings)
    env = dict(os.environ, PYTHONPATH=ROOT)
    r = subprocess.run([sys.executable, "-m", "dokima.prompt", role, grade], cwd=folder, env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.strip(), \
        f"the {role}'s prompt ({grade}) was not built: exit {r.returncode}\n{r.stderr}"
    return r.stdout


def flat(text):
    """TEXT on one line, spaces squeezed and curly quotes made straight."""
    return " ".join(text.replace("’", "'").replace("“", '"').replace("”", '"').split())


def sentences(text):
    """TEXT's sentences and list items, each on one line."""
    parts = []
    for block in re.split(r"\n\s*(?:- |\d+\. |\n)", text):
        parts += re.split(r"(?<=[.!?])\s+", flat(block))
    return [p for p in parts if p]


def code_names():
    """Every file name of Dokima's own code, by path and by bare name."""
    names = set()
    for top in CODE_DIRS:
        for here, dirs, files in os.walk(os.path.join(ROOT, top)):
            rel = os.path.relpath(here, ROOT)
            dirs[:] = [d for d in dirs if d != "__pycache__" and os.path.join(rel, d) not in NOT_CODE]
            for name in files:
                if name.endswith((".md", ".pyc")):
                    continue
                names.add(os.path.join(rel, name).replace(os.sep, "/"))
                names.add(name)
    return names


def named_files(text, names):
    """The Dokima code file names TEXT holds, and any path into the dokima folder."""
    found = {n for n in names if re.search(r"(?<![\w.-])" + re.escape(n) + r"(?![\w-])", text)}
    found |= set(re.findall(r"(?<![\w./-])dokima/[\w./-]*\w", text))
    return sorted(found)


# 817.1 ------------------------------------------------------------------------------------------------------------

def test_no_shipped_prompt_names_a_file_of_dokimas_own_code(record_property, tmp_path):
    """No shipped prompt names a file from Dokima's own code.

    Proves 817.1. Lists every file of Dokima's code (dokima/, tests/, .github/, tools/), by path and by bare name, and
    scans every file in dokima/roles/, the raising rules file among them, for any of them or any path into the
    dokima/ folder. Then builds the planner's, worker's and both reviewer's prompts with no settings file, as an
    adopter's repo gets them, and scans each the same way. Each failure names the prompt and the file names found."""
    record_property("proves", "817.1")
    names = code_names()
    assert "dokima/card.py" in names and "card.py" in names, \
        f"817.1: the scan could not list Dokima's own code files under {ROOT}"
    assert os.path.isfile(RAISING), "817.1: dokima/roles/raising.md, the shared raising rules, is not there to scan"
    hits = {}
    for name in sorted(os.listdir(ROLES)):
        if name.endswith(".md"):
            found = named_files(open(os.path.join(ROLES, name)).read(), names)
            if found:
                hits[f"dokima/roles/{name}"] = found
    for role, grade in PROMPTS:
        found = named_files(built(tmp_path, role, grade), names)
        if found:
            hits[f"the built {role} prompt ({grade})"] = found
    assert not hits, "817.1: shipped prompts still name files from Dokima's own code:\n" + \
        "\n".join(f"  {where}: {', '.join(found)}" for where, found in hits.items())


# 817.2 ------------------------------------------------------------------------------------------------------------

def test_the_raising_rules_are_written_once_in_one_shared_file(record_property):
    """The raising rules live in one shared file; no role prompt keeps a copy.

    Proves 817.2. Reads dokima/roles/raising.md: it holds the "# Raising and answering" rules, naming the raises and
    answers fields. Then reads every other file in dokima/roles/: none has a "# Raising and answering" heading, and
    none repeats any line of raising.md 40 characters or longer."""
    record_property("proves", "817.2")
    assert os.path.isfile(RAISING), "817.2: there is no dokima/roles/raising.md holding the shared raising rules"
    shared = open(RAISING).read()
    assert re.search(r"^# Raising and answering\s*$", shared, re.M), \
        "817.2: dokima/roles/raising.md has no '# Raising and answering' heading"
    for field in ('"raises"', '"answers"'):
        assert field in shared, f"817.2: dokima/roles/raising.md does not name the field {field}"
    long_lines = {line.strip() for line in shared.splitlines() if len(line.strip()) >= 40}
    assert long_lines, "817.2: dokima/roles/raising.md holds no rules to share"
    copies = {}
    for name in sorted(os.listdir(ROLES)):
        if not name.endswith(".md") or name == "raising.md":
            continue
        text = open(os.path.join(ROLES, name)).read()
        own = {line.strip() for line in text.splitlines()}
        if re.search(r"^# Raising and answering\s*$", text, re.M):
            copies[name] = ["its own '# Raising and answering' heading"]
        repeated = sorted(long_lines & own)
        if repeated:
            copies.setdefault(name, []).extend(repeated[:3])
    assert not copies, "817.2: role prompts still hold their own copy of the raising rules:\n" + \
        "\n".join(f"  dokima/roles/{name}: {found}" for name, found in copies.items())


# 817.3 ------------------------------------------------------------------------------------------------------------

def carried(line, own):
    """Whether some prompt line matches LINE, at least nine tenths the same."""
    return any(difflib.SequenceMatcher(None, line, other).ratio() >= 0.9 for other in own if other.strip())


def test_every_role_prompt_carries_the_shared_raising_rules(record_property, tmp_path):
    """The planner's, worker's and reviewer's prompts each carry the shared raising rules.

    Proves 817.3. Builds the planner's, worker's and both reviewer's prompts with no settings file. Each must hold
    exactly one "# Raising and answering" heading and every line of dokima/roles/raising.md, at least ten: word for
    word, or nearly so where a setting's value is drawn in. A prompt that leaves the rules out, or holds them twice,
    fails, naming it."""
    record_property("proves", "817.3")
    assert os.path.isfile(RAISING), "817.3: there is no dokima/roles/raising.md for the prompts to carry"
    lines = [line.rstrip() for line in open(RAISING).read().splitlines() if line.strip()]
    assert len(lines) >= 10, f"817.3: dokima/roles/raising.md holds only {len(lines)} lines of rules"
    for role, grade in PROMPTS:
        text = built(tmp_path, role, grade)
        heads = re.findall(r"^# Raising and answering\s*$", text, re.M)
        assert len(heads) == 1, \
            f"817.3: the {role}'s prompt ({grade}) holds {len(heads)} '# Raising and answering' sections, not one"
        own = {line.rstrip() for line in text.splitlines()}
        missing = [line for line in lines if line not in own and not carried(line, own)]
        assert not missing, \
            f"817.3: the {role}'s prompt ({grade}) lacks {len(missing)} lines of the shared raising rules, e.g. {missing[0]!r}"


# 817.4 ------------------------------------------------------------------------------------------------------------

def question_limits(text):
    """Every number the prompt gives in 'more than N questions', as written."""
    return re.findall(r"\bmore than (\w+) questions\b", flat(text), re.I)


def test_the_planners_prompt_states_the_question_limit_the_settings_name(record_property, tmp_path):
    """The planner's prompt states the question limit the repo's settings name.

    Proves 817.4. The settings set planner.max_questions to 5. Builds the planner's prompt and checks it says "more
    than 5 questions", and never more than 3 or three. Then no settings file: the prompt says more than 3."""
    record_property("proves", "817.4")
    said = question_limits(built(tmp_path / "set", "planner", "plan-grade", "planner:\n  max_questions: 5\n"))
    assert "5" in said, \
        f"817.4: with the questions setting at 5, the planner's prompt never says 'more than 5 questions'; it says {said}"
    wrong = [n for n in said if n != "5"]
    assert not wrong, f"817.4: with the questions setting at 5, the planner's prompt still says more than {wrong} questions"
    said = question_limits(built(tmp_path / "default", "planner", "plan-grade"))
    assert said and all(n.lower() in ("3", "three") for n in said), \
        f"817.4: with no settings file, the planner's prompt does not say more than 3 questions; it says {said}"


# 817.5 ------------------------------------------------------------------------------------------------------------

def blocks_lines(text):
    """The prompt's lines that speak of blocks in a row."""
    return [line for line in text.splitlines() if re.search(r"\bblocks? in a row\b", line, re.I)]


def test_every_prompt_states_the_blocks_in_a_row_limit_the_settings_name(record_property, tmp_path):
    """Every prompt states the blocks-in-a-row limit the repo's settings name.

    Proves 817.5. The settings set river.max_blocks to 7. Builds the planner's, worker's and both reviewer's prompts
    and checks each has a line on blocks in a row that names 7, and that no such line still says three, third or 3.
    Then no settings file: each prompt's line names 3."""
    record_property("proves", "817.5")
    for role, grade in PROMPTS:
        found = blocks_lines(built(tmp_path / "set", role, grade, "river:\n  max_blocks: 7\n"))
        assert found, f"817.5: the {role}'s prompt ({grade}) has no line on blocks in a row"
        assert any(re.search(r"\b7\b", line) for line in found), \
            f"817.5: with the blocks setting at 7, the {role}'s prompt ({grade}) never names 7: {found}"
        stale = [line for line in found if re.search(r"\b(three|third|3)\b", line, re.I)]
        assert not stale, f"817.5: with the blocks setting at 7, the {role}'s prompt ({grade}) still says three: {stale}"
        found = blocks_lines(built(tmp_path / "default", role, grade))
        assert any(re.search(r"\b(3|three)\b", line, re.I) for line in found), \
            f"817.5: with no settings file, the {role}'s prompt ({grade}) does not name 3 blocks in a row: {found}"


# 817.6 ------------------------------------------------------------------------------------------------------------

def test_the_planners_prompt_gives_when_x_y_as_the_default_criterion_style(record_property, tmp_path):
    """The planner's prompt gives "When X, Y" as the default way to write a criterion.

    Proves 817.6. Builds the planner's prompt with no settings file and checks one sentence names "When X, Y" and
    calls it the default, and that the prompt no longer forbids a formula for criteria."""
    record_property("proves", "817.6")
    text = built(tmp_path, "planner", "plan-grade")
    style = [s for s in sentences(text) if '"When X, Y"' in s and re.search(r"\bdefault\b", s, re.I)]
    assert style, "817.6: no sentence of the planner's prompt gives \"When X, Y\" as the default criterion style"
    assert "never a formula" not in flat(text).lower(), \
        "817.6: the planner's prompt still says criteria are never a formula, against the \"When X, Y\" default"


# 817.7 ------------------------------------------------------------------------------------------------------------

def test_the_planners_prompt_says_each_criterion_needs_a_source_a_result_and_a_test(record_property, tmp_path):
    """The planner's prompt says each criterion needs a source, an observable result and a test.

    Proves 817.7. Builds the planner's prompt with no settings file and looks for one sentence that names a
    criterion, its source, a result a test can observe, and its test, all together."""
    record_property("proves", "817.7")
    text = built(tmp_path, "planner", "plan-grade")
    need = [s for s in sentences(text) if re.search(r"\bcriteri(on|a)\b", s, re.I) and re.search(r"\bsource\b", s, re.I)
            and re.search(r"\bresult\b", s, re.I) and re.search(r"\bobserv", s, re.I) and re.search(r"\btest\b", s, re.I)]
    assert need, ("817.7: no sentence of the planner's prompt says each criterion needs a source, an observable "
                  "result and a test")


# 817.8 ------------------------------------------------------------------------------------------------------------

def test_the_planners_prompt_turns_each_unfilled_blank_into_one_question(record_property, tmp_path):
    """The planner's prompt says each blank it cannot fill becomes one question to the owner.

    Proves 817.8. Builds the planner's prompt with no settings file and looks for one sentence that names a blank,
    one question, and the owner."""
    record_property("proves", "817.8")
    text = built(tmp_path, "planner", "plan-grade")
    rule = [s for s in sentences(text) if re.search(r"\bblanks?\b", s, re.I) and re.search(r"\bone question\b", s, re.I)
            and re.search(r"\bowner\b", s, re.I)]
    assert rule, "817.8: no sentence of the planner's prompt says each blank it cannot fill becomes one question to the owner"


# 817.9 ------------------------------------------------------------------------------------------------------------

EXAMPLES = [
    ("No observable result", "Make it faster", "faster by how much, measured where?"),
    ("No trigger", "Cards fold long text", "on every card, or only past N lines?"),
    ("Two readings", "Skip review for hotfixes", "skip code review too, or only planning?"),
    ("Owner's words conflict", "body says sub-issues, a comment says no sub-issues", "Which?"),
    ("Cannot be tested", "Looks cleaner", "manual sign-off, or is there a measurable version?"),
    ("Bad-input result unstated", "settings name an unknown model", "stop, or fall back?"),
    ("Scope edge", "All PRs", "Dependabot's too?"),
]


def test_the_planners_prompt_shows_the_owners_seven_question_examples(record_property, tmp_path):
    """The planner's prompt shows all seven of the owner's clarifying question examples.

    Proves 817.9. Builds the planner's prompt with no settings file and checks it holds each example the owner gave:
    its kind, the ask and the question it raises, in that order on one line, from no observable result to scope edge."""
    record_property("proves", "817.9")
    lines = [flat(line).lower() for line in built(tmp_path, "planner", "plan-grade").splitlines()]
    missing = []
    for kind, ask, question in EXAMPLES:
        parts = [kind.lower(), ask.lower(), question.lower()]
        if not any(all(p in line for p in parts) and line.index(parts[0]) < line.index(parts[1]) < line.rindex(parts[2])
                   for line in lines):
            missing.append(f"{kind}: {ask}: {question}")
    assert not missing, "817.9: the planner's prompt lacks the owner's question examples:\n  " + "\n  ".join(missing)

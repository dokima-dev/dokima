"""Tests for the wiki pages under docs/wiki/, which wiki.yml mirrors to the GitHub wiki.

The reference pages of #308 (Commands and labels, The card, Configuration) are checked against the code itself:
the commands come from dokima/agent.py COMMANDS, the labels, board fields, views, branch rule and app permissions from
dokima/manifest.py, the card's stages and circle states from dokima/card.py, and the secrets and variables from what
the workflows read. When the code gains or renames one of these, the page must follow or these tests go red.

On the Commands and labels page each command and label has its own entry: one table row or bullet whose first
backticked word is its name, for example "| `/plan` | ..." or "- `parked`: ...".
"""
import re
from pathlib import Path

from dokima import agent, card, manifest

ROOT = Path(__file__).parent.parent
WIKI = ROOT / "docs" / "wiki"
COMMANDS_PAGE = "Commands-and-labels.md"
CARD_PAGE = "The-card.md"
CONFIG_PAGE = "Configuration.md"
REFERENCE = (COMMANDS_PAGE, CARD_PAGE, CONFIG_PAGE)
STALE_PIN = "`work`" + " label"


def read(name, criterion="308"):
    """The text of one wiki page; a missing page fails naming its criterion."""
    path = WIKI / name
    assert path.exists(), f"{criterion}: docs/wiki/{name} does not exist yet"
    return path.read_text()


def commands():
    """Every command the code reads today, with /issue (planned) last."""
    return list(agent.COMMANDS) + ["/autopilot start", "/autopilot stop", "/issue"]


def entry(text, name):
    """The row or bullet whose first backticked word is `name`, or None."""
    for line in text.splitlines():
        m = re.match(r"\s*(?:\||[-*])\s*(?:\*\*)?`([^`]+)`", line)
        if m and m.group(1) == name:
            return line
    return None


def entries(text):
    """The name of every row or bullet that starts with a backticked word."""
    out = []
    for line in text.splitlines():
        m = re.match(r"\s*(?:\||[-*])\s*(?:\*\*)?`([^`]+)`", line)
        if m:
            out.append(m.group(1))
    return out


# What each entry must say it does today, from the code: (words that must all appear in the entry, case-insensitive).
COMMAND_FACTS = {
    "/plan": ["planner"],
    "/work": ["worker", "split"],
    "/review": ["reviewer"],
    "/autopilot start": ["autopilot", "sub-issue"],
    "/autopilot stop": ["autopilot"],
    "/issue": ["planned"],
}
LABEL_FACTS = {
    "plan": ["planner", "code owner"],
    "work": ["worker", "code owner"],
    "autopilot": ["/autopilot start"],
    "blocker": ["priority"],
    "high": ["priority"],
    "parked": ["priority"],
}

# Labels whose workflow does not check the sender: anyone who can label an issue (triage or write access) adds them.
# The plan and work labels count only from a code owner (planner.yml and worker.yml, "Only a code owner's label counts").
ANYONE_LABELS = ("autopilot", "blocker", "high", "parked")


def command_problems(text):
    """Every command or label the page misses or misstates; empty when none."""
    problems = []
    for name in commands():
        line = entry(text, name)
        if line is None:
            problems.append(f"command {name} has no entry")
            continue
        for word in COMMAND_FACTS.get(name, []):
            if word.lower() not in line.lower():
                problems.append(f"command {name}'s entry does not mention {word!r}")
    for name in manifest.LABELS:
        line = entry(text, name)
        if line is None:
            problems.append(f"label {name} has no entry")
            continue
        for word in LABEL_FACTS.get(name, []):
            if word.lower() not in line.lower():
                problems.append(f"label {name}'s entry does not mention {word!r}")
        if name in ANYONE_LABELS and not re.search(r"triage|write access", line, re.I):
            problems.append(f"label {name}'s entry does not say who may add it (triage or write access)")
    known = set(commands()) | set(manifest.LABELS)
    for name in entries(text):
        if name not in known:
            problems.append(f"entry `{name}` is neither a command nor a label the code has")
    for token in set(re.findall(r"`(/[a-z]+(?: (?:start|stop))?)`", text)):
        if token not in commands():
            problems.append(f"command {token} is not one the code reads")
    return problems


def test_commands_and_labels(record_property):
    """Commands and labels lists every command and label the code has, and what each does.

    Reads the commands from dokima/agent.py and the labels from dokima/manifest.py, finds each one's row or bullet on
    the page, checks it names what it starts or sets, that /issue is marked planned, that no command or label the code
    lacks is listed, and that the page says only a code owner's commands count. Each label's entry says who may add
    it: the plan and work entries say only a code owner's label counts, the others say triage or write access.
    Proves 308.1."""
    record_property("proves", "308.1")
    text = read(COMMANDS_PAGE, "308.1")
    problems = command_problems(text)
    assert not problems, "308.1: Commands and labels page: " + "; ".join(problems)
    assert "code owner" in text.lower() and "CODEOWNERS" in text, \
        "308.1: the page does not say only a code owner (from CODEOWNERS) may use the commands"
    assert "approv" not in entry(text, "work").lower(), \
        "308.1: the work label's entry still says it approves a plan; /work does"


def test_the_card(record_property):
    """The card page explains every field on the card and run records today.

    Takes the stages, circle states and every named field (FIELD_ICONS) from dokima/card.py and checks each is on the
    page, with the Next line, the Needs you and Autopilot pills, Verified by, the Definition of Done row and the run
    record's footnote; then checks the old work-label approval and the old Before/After example are gone, and that
    /work approves. The stats icon marks the footnote, so the footnote's model, turns, tokens and cost stand for it.
    Proves 308.2."""
    record_property("proves", "308.2")
    text = read(CARD_PAGE, "308.2")
    for field in card.FIELD_ICONS:
        if field == "stats":
            continue
        pattern = r"\s+".join(rf"{re.escape(w)}s?" for w in field.split())
        assert re.search(rf"\b{pattern}\b", text, re.I), f"308.2: the card page does not explain {field}"
    missing = [s for s in sorted(card.STAGES) if s not in text]
    assert not missing, f"308.2: the card page does not name the stages {missing}"
    missing = [s for s in card.ICON_FILE if s not in text.lower()]
    assert not missing, f"308.2: the card page does not explain the circle states {missing}"
    for word in ("Next", "Needs you", "Autopilot", "circle", "Verified by", "Definition of Done", "All tests",
                 "Code review", "Owner approval", "/work"):
        assert word in text, f"308.2: the card page does not explain {word!r}"
    for word in ("model", "turns", "tokens", "cost"):
        assert word in text.lower(), f"308.2: the card page does not explain the run record's {word}"
    assert not re.search(r"`?work`? label", text), "308.2: the card page still says the work label approves a plan"
    assert "Objective:" not in text, "308.2: the card page still shows the old Before/After example"


def workflow_settings():
    """(secrets, variables) the workflows read, GitHub's own token left out."""
    secrets, variables = set(), set()
    for path in (ROOT / ".github" / "workflows").glob("*.yml"):
        text = path.read_text()
        secrets |= set(re.findall(r"secrets\.([A-Z0-9_]+)", text)) - {"GITHUB_TOKEN"}
        variables |= set(re.findall(r"vars\.([A-Z0-9_]+)", text))
    return secrets, variables


def permission_line(text, perm):
    """The row or bullet starting with the app permission's code or GitHub name, or None."""
    for name in {perm, perm.replace("_", " ")}:
        pattern = rf"\s*(?:\||[-*])\s*(?:\*\*)?`?{re.escape(name)}`?(?:\*\*)?\s*[|:]"
        for line in text.splitlines():
            if re.match(pattern, line, re.I):
                return line
    return None


def test_configuration(record_property):
    """Configuration lists every secret, variable, check, permission and board setting Dokima needs.

    Collects the secrets and variables every workflow reads, the branch rule, required checks, app permissions,
    board fields and Autopilot view from dokima/manifest.py, and checks each is on the page, each permission as its
    own row or bullet (starting with its name, then | or :) with its own level, the board marked optional.
    Proves 308.3."""
    record_property("proves", "308.3")
    text = read(CONFIG_PAGE, "308.3")
    secrets, variables = workflow_settings()
    assert secrets and variables, "308.3: found no secrets or variables in the workflows to check against"
    missing = sorted(s for s in secrets | variables if s not in text)
    assert not missing, f"308.3: the Configuration page does not list {missing}"
    assert "CODEOWNERS" in text, "308.3: the Configuration page does not explain the CODEOWNERS file"
    for branch, rule in manifest.BRANCH_RULES.items():
        assert f"`{branch}`" in text or f" {branch} " in text, f"308.3: the page does not name the branch {branch}"
        for check in rule["required_checks"]:
            assert check in text, f"308.3: the page does not list the required check {check!r}"
    for perm, level in manifest.PERMISSIONS.items():
        line = permission_line(text, perm)
        assert line, f"308.3: the page does not list the app permission {perm}"
        if level == "write":
            assert "write" in line.lower(), f"308.3: the page does not give {perm} write: {line!r}"
        else:
            assert "read" in line.lower() and "write" not in line.lower(), \
                f"308.3: the page does not give {perm} read only: {line!r}"
    for field, options in manifest.FIELDS.items():
        assert field in text, f"308.3: the page does not name the board field {field}"
        missing = [o for o in options if o not in text]
        assert not missing, f"308.3: the page does not name the {field} options {missing}"
    for view in manifest.VIEWS.values():
        assert view["filter"] in text, f"308.3: the page does not give the view filter {view['filter']!r}"
    assert "optional" in text.lower(), "308.3: the page does not say the project board is optional"


def test_wiki_tests_catch_a_missing_command_or_label(record_property):
    """Taking any command or label off Commands and labels turns its test red.

    Runs the page's checks on the real page (it must pass), then on copies with one entry removed at a time, each of
    which must fail naming that entry; and checks this file no longer pins the stale work-label wording.
    Proves 308.4."""
    record_property("proves", "308.4")
    text = read(COMMANDS_PAGE, "308.4")
    assert not command_problems(text), "308.4: the real Commands and labels page does not pass its own checks"
    for name in commands() + list(manifest.LABELS):
        line = entry(text, name)
        assert line is not None, f"308.4: no entry for {name}"
        cut = "\n".join(l for l in text.splitlines() if l != line)
        assert any(f" {name} has no entry" in p for p in command_problems(cut)), \
            f"308.4: removing {name} from the page did not fail the check"
    assert STALE_PIN not in Path(__file__).read_text(), "308.4: tests/test_wiki.py still pins the work-label wording"


HYPE = ("powerful", "seamless", "production-grade", "simply")
OTHER_NAMES = ("maintainer", "approver", "implementer", "status card", "the user")


def prose(text):
    """The page without code blocks or inline code, so names are not judged as words."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", text)


def test_reference_pages_follow_the_style(record_property):
    """Each reference page opens with one sentence and reads plain, terse and second person.

    For each of the three pages: the first paragraph under the title is one sentence; the page says "you"; no hype
    word, no "river", no other name for the owner, reviewer or card, no "will", and no sentence over 40 words.
    Proves 308.5."""
    record_property("proves", "308.5")
    for name in REFERENCE:
        text = read(name, "308.5")
        lines = text.splitlines()
        assert lines and lines[0].startswith("# "), f"308.5: {name} does not start with a title"
        first = []
        for line in lines[1:]:
            if line.strip():
                first.append(line.strip())
            elif first:
                break
        opening = " ".join(first)
        assert len(re.findall(r"[.!?](?:\s|$)", opening)) == 1 and opening.endswith("."), \
            f"308.5: {name} does not open with exactly one sentence: {opening!r}"
        words = prose(text).lower()
        assert re.search(r"\byou(r)?\b", words), f"308.5: {name} is not written in the second person"
        for word in HYPE + ("river",) + OTHER_NAMES:
            assert not re.search(rf"\b{re.escape(word)}\b", words), f"308.5: {name} uses {word!r}"
        assert not re.search(r"\bwill\b", words), f"308.5: {name} is not in the present tense (uses 'will')"
        for sentence in re.split(r"(?<=[.!?])\s+|\n", prose(text)):
            assert len(sentence.split()) <= 40, f"308.5: {name} has a sentence over 40 words: {sentence[:80]!r}"


# Things AGENTS.md marks planned: a line on a reference page that mentions one must say planned.
PLANNED = (r"`/issue`", r"co-author", r"one[- ]command")


def test_reference_pages_mark_what_is_planned(record_property):
    """Each reference page marks unbuilt behaviour planned and claims no merge outside autopilot.

    For each page, every line that mentions /issue, co-author credit or a one-command setup must say planned, and a
    line saying a pull request merges by itself must be about autopilot. Proves 308.6."""
    record_property("proves", "308.6")
    for name in REFERENCE:
        text = read(name, "308.6")
        for line in text.splitlines():
            low = line.lower()
            for pattern in PLANNED:
                if re.search(pattern, low):
                    assert "planned" in low, f"308.6: {name} describes unbuilt behaviour without 'planned': {line!r}"
            if re.search(r"merges? (?:by itself|on its own|automatically)", low):
                assert "autopilot" in low, f"308.6: {name} says pull requests merge by themselves: {line!r}"


def test_writing_issues(record_property):
    """The Writing issues page talks about criteria and Verified by, never done-whens."""
    record_property("proves", "72.1")
    text = read("Writing-issues.md")
    assert "criteria" in text
    assert "Verified by" in text
    assert "done when" not in text.lower()

"""The wiki install page asks for one workflow and one settings file, never Dokima's code.

Issue #815, story 4 of #742. An adopter's repo holds only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`;
all Dokima code runs from Dokima's own repo. These tests read `docs/wiki/Installing.md`, the page adopters follow.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
PAGE = ROOT / "docs" / "wiki" / "Installing.md"
WORKFLOW = ".github/workflows/dokima.yml"
SETTINGS = ".dokima/settings.yaml"
ADD = re.compile(r"\b(add|adds|added|create|commit|put)\b", re.I)


def page():
    """Returns the install page's text."""
    return PAGE.read_text()


def dokimas_own_workflows():
    """Returns the names of Dokima's own workflow files, every one but the thin `dokima.yml`."""
    return sorted(p.name for p in (ROOT / ".github" / "workflows").glob("*.yml") if p.name != "dokima.yml")


def test_the_install_page_never_tells_adopters_to_put_dokimas_folders_in_their_repo(record_property):
    """The install page never tells adopters to add Dokima's workflows folder or code folder.

    Fails on any line naming the whole `.github/workflows/` folder or the `dokima/` folder (or package), whatever
    the verb, as the page's step 4 does today. A single file inside them, like `dokima.yml`, is fine.

    Proves 815.1."""
    record_property("proves", "815.1")
    folders = re.compile(
        r"\.github/workflows/?(?![\w./-])|(?<![\w./-])dokima/(?![\w.-])|`dokima` package|the dokima package", re.I
    )
    bad = [line for line in page().splitlines() if folders.search(line)]
    assert not bad, f"815.1: the install page still names Dokima's workflows or code folder: {bad}"


def test_the_install_page_tells_adopters_to_add_the_thin_workflow(record_property):
    """The install page tells adopters to add the one workflow, `.github/workflows/dokima.yml`.

    Looks for a line naming that exact path with a verb like add or create.

    Proves 815.2."""
    record_property("proves", "815.2")
    lines = [line for line in page().splitlines() if WORKFLOW in line and ADD.search(line)]
    assert lines, f"815.2: no line of the install page tells adopters to add `{WORKFLOW}`"


def test_the_install_page_tells_adopters_to_add_the_settings_file(record_property):
    """The install page tells adopters to add the settings file, `.dokima/settings.yaml`.

    Looks for a line naming that exact path with a verb like add or create.

    Proves 815.3."""
    record_property("proves", "815.3")
    lines = [line for line in page().splitlines() if SETTINGS in line and ADD.search(line)]
    assert lines, f"815.3: no line of the install page tells adopters to add `{SETTINGS}`"


def test_the_install_page_says_the_two_files_are_the_whole_install(record_property):
    """The install page says the workflow and the settings file are the whole install.

    Looks for one line naming both paths and saying "only" or "nothing else", so adopters know nothing more lands
    in their repo.

    Proves 815.4."""
    record_property("proves", "815.4")
    whole = re.compile(r"\bonly\b|nothing else", re.I)
    lines = [line for line in page().splitlines() if WORKFLOW in line and SETTINGS in line and whole.search(line)]
    assert lines, f"815.4: no line says `{WORKFLOW}` and `{SETTINGS}` are the only files an adopter adds"


def test_the_install_page_lists_none_of_dokimas_own_workflows_to_add(record_property):
    """The install page no longer lists Dokima's own workflows, like `playthrough.yml` and `wiki.yml`, to add.

    Takes every workflow in Dokima's `.github/workflows/` but `dokima.yml` and fails on any page line naming one.
    A line that points at Dokima's own repo (`dokima-dev/dokima`) or says "never" is allowed: it does not ask the
    adopter to add the file.

    Proves 815.5."""
    record_property("proves", "815.5")
    own = dokimas_own_workflows()
    assert "playthrough.yml" in own and "wiki.yml" in own, f"815.5: expected Dokima's own workflows, found {own}"
    bad = [
        line
        for line in page().splitlines()
        if any(re.search(rf"(?<![\w.-]){re.escape(name)}", line) for name in own)
        and "dokima-dev/dokima" not in line
        and not re.search(r"\bnever\b", line, re.I)
    ]
    assert not bad, f"815.5: the install page still lists Dokima's own workflows to add: {bad}"


def test_the_install_page_never_lists_the_code_owners_file_to_add(record_property):
    """The install page never lists the code owners file among the files to add.

    Fails when a heading makes code owners an install step, as step 3 does today, or when a line naming
    `CODEOWNERS` does not call it optional. The owner allows one optional mention, so a page with none, or one line
    saying it is optional, passes; a second mention fails.

    Proves 815.6."""
    record_property("proves", "815.6")
    lines = page().splitlines()
    steps = [line for line in lines if line.startswith("#") and re.search(r"code ?owners", line, re.I)]
    assert not steps, f"815.6: the install page makes code owners an install step: {steps}"
    named = [line for line in lines if "CODEOWNERS" in line]
    required = [line for line in named if not re.search(r"\boptional\b", line, re.I)]
    assert not required, f"815.6: the install page names `CODEOWNERS` without calling it optional: {required}"
    assert len(named) <= 1, f"815.6: the install page mentions `CODEOWNERS` more than once: {named}"

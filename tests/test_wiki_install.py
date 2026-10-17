"""The wiki's install page never tells adopters to copy Dokima's workflows or code.

Issue #815, story 4 of #742. An adopter's repo holds only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`;
all Dokima code runs from Dokima's own repo. This test reads `docs/wiki/Installing.md`, the page adopters follow.
"""

import re
from pathlib import Path

PAGE = Path(__file__).parent.parent / "docs" / "wiki" / "Installing.md"


def page():
    """Returns the install page's text."""
    return PAGE.read_text()


def test_the_install_page_never_tells_adopters_to_copy_dokimas_workflows_or_code(record_property):
    """The install page never tells adopters to copy Dokima's workflows folder or its code.

    Finds every line of the page that says to copy something and fails on any that names the whole workflows folder
    or the `dokima/` folder (or package), as the page's step 4 does today. Copying the single `dokima.yml` is fine.

    Proves 815.1."""
    record_property("proves", "815.1")
    folders = re.compile(r"`\.github/workflows/?`|`dokima/?`(?!\S)|`dokima/?` package|the dokima package", re.I)
    bad = [line for line in page().splitlines() if "copy" in line.lower() and folders.search(line)]
    assert not bad, f"815.1: the install page still tells adopters to copy Dokima's workflows or code: {bad}"


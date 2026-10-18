"""The repo's changelog lists what v0.1.0 does (#849).

The owner moved the changelog out of the release story (#755) into this issue. That story's release workflow reads
CHANGELOG.md at the repo root and uses the section under the heading naming v0.1.0 as the release notes, so this test
reads the same file the same way: a heading naming v0.1.0, then the lines up to the next heading as high. The section
must list at least one thing, as a markdown list item; a heading with nothing listed under it fails.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")


def changelog_section(text, version):
    """The lines under the heading naming version, up to the next as high, else None."""
    lines = text.splitlines()
    heading = re.compile(r"^(#{1,6})\s+.*" + re.escape(version) + r"(?![0-9])")
    for i, line in enumerate(lines):
        m = heading.match(line)
        if m:
            out = []
            for later in lines[i + 1:]:
                h = re.match(r"^(#{1,6})\s", later)
                if h and len(h.group(1)) <= len(m.group(1)):
                    break
                out.append(later)
            return out
    return None


def test_changelog_lists_v010(record_property):
    """The changelog has a v0.1.0 section listing what that version does.

    849.1: reads CHANGELOG.md at the repo root, finds the heading naming v0.1.0 the way the release reads it, and
    checks at least one list item sits under it. A missing file, a missing heading or an empty section each fail and
    say which."""
    record_property("proves", "849.1")
    assert os.path.isfile(CHANGELOG), "849.1: CHANGELOG.md is missing from the repo root"
    with open(CHANGELOG) as f:
        text = f.read()
    section = changelog_section(text, "v0.1.0")
    assert section is not None, "849.1: CHANGELOG.md has no heading naming v0.1.0"
    items = [line for line in section if re.match(r"^\s*([-*+]|\d+\.)\s+\S", line)]
    assert items, "849.1: the v0.1.0 section of CHANGELOG.md lists nothing that version does"

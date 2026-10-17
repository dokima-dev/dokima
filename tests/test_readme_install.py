"""Tests for #814: the README's install steps use the thin workflow, not Dokima's code.

Since #813 an install adds only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`, taken from
`dokima/install/`. These tests read the README's Install section, up to the next top-level heading, and check its
numbered setup steps tell adopters to add those two files and never to copy Dokima's whole workflows or code folders.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Whole-folder references that mean "copy Dokima": its workflows folder and its code folder.
WHOLE_FOLDERS = {".github/workflows", ".github/workflows/", "dokima", "dokima/"}


def install_section():
    """The README's Install section, from its heading to the next top-level heading."""
    text = open(os.path.join(ROOT, "README.md")).read()
    match = re.search(r"^## Install\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, "814: README.md has no '## Install' section"
    return match.group(1)


def steps():
    """The numbered setup steps of the Install section, one string each."""
    return [line for line in install_section().splitlines() if re.match(r"\s*\d+\.\s", line)]


def references(line):
    """Every markdown link target and code span in LINE."""
    return re.findall(r"\]\(([^)]+)\)", line) + re.findall(r"`([^`]+)`", line)


def test_install_steps_add_the_two_files_not_dokima(record_property):
    """README install steps add the thin workflow and settings file, never copying Dokima.

    Proves 814.1. Reads the README's Install section. It fails on any link or code span naming the whole `.github/workflows/` or
    `dokima/` folder, which the old copy step pointed at. It also fails unless a numbered step adds
    `dokima/install/dokima.yml` as `.github/workflows/dokima.yml` and one adds `dokima/install/settings.yaml` as
    `.dokima/settings.yaml`, so deleting the old step alone does not pass."""
    record_property("proves", "814.1")
    bad = [line.strip() for line in install_section().splitlines()
           if any(ref.strip() in WHOLE_FOLDERS for ref in references(line))]
    assert not bad, f"814.1: the README's install steps still point adopters at a whole Dokima folder to copy: {bad}"
    found = [s for s in steps() if ".github/workflows/dokima.yml" in s and "dokima/install/dokima.yml" in s]
    assert found, ("814.1: no README install step tells adopters to add `dokima/install/dokima.yml` "
                   "as `.github/workflows/dokima.yml`")
    found = [s for s in steps() if ".dokima/settings.yaml" in s and "dokima/install/settings.yaml" in s]
    assert found, ("814.1: no README install step tells adopters to add `dokima/install/settings.yaml` "
                   "as `.dokima/settings.yaml`")

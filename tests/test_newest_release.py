"""Tests for #867: each release takes its version from the changelog's newest version heading.

Before #867 the release command knew one version, v0.1.0, so Dokima could release nothing newer and adopters, whose
install file calls Dokima at a release tag, never got a fix merged after it. Now the newest version heading of
CHANGELOG.md (the top-most heading naming a version like v0.1.1) names the release, so adding a `## v0.1.1` section
and merging it makes v0.1.1. The install file and the install docs name that same newest version.

The release tests run the command release.yml runs, against the fake `gh` of tests/test_release.py, in a temp folder
holding a changelog, so nothing leaves the machine. The other tests read the repo's own CHANGELOG.md, install file,
README and wiki install page, and check they agree on the newest version.
"""
import os
import re

import yaml

from tests.test_release import SHA, run_release

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = re.compile(r"v(\d+)\.(\d+)\.(\d+)(?![0-9])")
HEADING = re.compile(r"^(#{1,6})\s+.*?\b(v\d+\.\d+\.\d+)(?![0-9])")
TWO = ("# Changelog\n\n## v0.1.1\n\n- Card updates find checks by the names GitHub shows.\n\n"
       "## v0.1.0\n\n- Dokima's first version.\n")


def read(rel):
    """The text of a file in the repo, by its path from the root."""
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def newest_version(crit):
    """The version named by CHANGELOG.md's top-most version heading."""
    for line in read("CHANGELOG.md").splitlines():
        m = HEADING.match(line)
        if m:
            return m.group(2)
    raise AssertionError(f"{crit}: CHANGELOG.md has no heading naming a version")


def made(state):
    """The tags the fake GitHub was asked to make, each with its commit."""
    return [(c["tag"], c["target"]) for c in state["created"]]


def test_release_names_newest_version(tmp_path, record_property):
    """With v0.2.0 newest in the changelog, a push to main releases v0.2.0.

    867.1: runs the command release.yml runs on a changelog whose sections are v0.2.0, v0.1.1 and v0.1.0, with the
    two older ones already released, and checks it made exactly one release, v0.2.0, at the pushed commit. A version
    other than v0.1.1 proves the release follows the changelog, not one more hardcoded version."""
    record_property("proves", "867.1")
    changelog = TWO.replace("# Changelog\n\n", "# Changelog\n\n## v0.2.0\n\n- A later fix.\n\n")
    done, state = run_release(tmp_path, "867.1", releases=["v0.1.0", "v0.1.1"], changelog=changelog)
    assert not state["unsupported"], f"867.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"867.1: the release command failed: {done.stderr[-800:]}"
    assert made(state) == [("v0.2.0", SHA)], \
        f"867.1: the changelog's newest version is v0.2.0, yet the release command made {made(state)}, not v0.2.0"


def test_release_v011_newest(tmp_path, record_property):
    """With v0.1.1 newest in the changelog, a push to main releases v0.1.1.

    867.1, edge case: the issue's own example. Runs the command on a changelog whose newest section is v0.1.1, with
    v0.1.0 already released, and checks it made exactly one release, v0.1.1, at the pushed commit."""
    record_property("proves", "867.1")
    done, state = run_release(tmp_path, "867.1", releases=["v0.1.0"], changelog=TWO)
    assert not state["unsupported"], f"867.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"867.1: the release command failed: {done.stderr[-800:]}"
    assert made(state) == [("v0.1.1", SHA)], \
        f"867.1: the changelog's newest version is v0.1.1, yet the release command made {made(state)}, not v0.1.1"


def test_release_newest_below_unreleased(tmp_path, record_property):
    """An Unreleased section above v0.1.1 still makes v0.1.1, not a release named Unreleased.

    867.1, edge case: a changelog often holds draft lines under an Unreleased heading on top; the newest version
    heading is the first one naming a version, so the command makes v0.1.1 and its notes leave the draft line out."""
    record_property("proves", "867.1")
    changelog = TWO.replace("# Changelog\n\n", "# Changelog\n\n## Unreleased\n\n- A draft line not yet released.\n\n")
    done, state = run_release(tmp_path, "867.1", releases=["v0.1.0"], changelog=changelog)
    assert not state["unsupported"], f"867.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"867.1: the release command failed: {done.stderr[-800:]}"
    assert made(state) == [("v0.1.1", SHA)], \
        f"867.1: with Unreleased above v0.1.1, the release command made {made(state)}, not v0.1.1"
    assert "A draft line not yet released." not in state["created"][0]["notes"], \
        "867.1: the v0.1.1 release notes carry a line from the changelog's Unreleased section"


def test_release_newest_already_released(tmp_path, record_property):
    """Once the newest version is released, a later push makes nothing, not an older version.

    867.1, edge case: every push to main runs the command; with v0.1.1 released, the command must make no release
    and still succeed, even though the older v0.1.0 below it has none."""
    record_property("proves", "867.1")
    done, state = run_release(tmp_path, "867.1", releases=["v0.1.1"], changelog=TWO)
    assert not state["unsupported"], f"867.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"867.1: the release command failed when v0.1.1 already exists: {done.stderr[-800:]}"
    assert made(state) == [], f"867.1: v0.1.1, the newest version, is already released, yet the command made {made(state)}"


def section(crit, version):
    """CHANGELOG.md's version headings in order, and the text of VERSION's section."""
    lines = read("CHANGELOG.md").splitlines()
    heads = [(i, m.group(1), m.group(2)) for i, line in enumerate(lines) if (m := HEADING.match(line))]
    names = [v for _, _, v in heads]
    assert version in names, f"{crit}: CHANGELOG.md has no {version} section; its headings are {names}"
    i, level, _ = heads[names.index(version)]
    body = []
    for later in lines[i + 1:]:
        h = re.match(r"^(#{1,6})\s", later)
        if h and len(h.group(1)) <= len(level):
            break
        body.append(later)
    return names, "\n".join(body)


def unnamed(text, numbers):
    """The issue numbers TEXT never names."""
    return [n for n in numbers if not re.search(re.escape(n) + r"(?![0-9])", text)]


def test_changelog_has_v011_on_top(record_property):
    """The changelog's v0.1.1 section, above v0.1.0, names the fixes #852, #856 and #861.

    867.2: reads CHANGELOG.md, checks its v0.1.1 section sits above v0.1.0 and names each fix the issue lists as
    merged since v0.1.0 by its number: #852, #856 and #861. Since #890, v0.1.2 sits above it as the newest."""
    record_property("proves", "867.2")
    names, text = section("867.2", "v0.1.1")
    assert "v0.1.0" in names and names.index("v0.1.0") > names.index("v0.1.1"), \
        f"867.2: CHANGELOG.md's v0.1.0 section is not below v0.1.1; its headings are {names}"
    missing = unnamed(text, ("#852", "#856", "#861"))
    assert not missing, f"867.2: the v0.1.1 section does not name {missing}, fixes merged since v0.1.0"


def test_changelog_has_v012_on_top():
    """The changelog's v0.1.2 section sits right above v0.1.1, naming the onboarding fixes #890 lists."""
    names, text = section("890", "v0.1.2")
    i = names.index("v0.1.2")
    assert names[i + 1:i + 2] == ["v0.1.1"], f"890: CHANGELOG.md's v0.1.2 section is not right above v0.1.1: {names}"
    missing = unnamed(text, ("#874", "#876", "#877", "#886", "#887"))
    assert not missing, f"890: the v0.1.2 section does not name {missing}, fixes merged since v0.1.1"


def test_changelog_has_v013_on_top():
    """The changelog's v0.1.3 section sits right above v0.1.2, naming the secrets fix #894."""
    names, text = section("894", "v0.1.3")
    i = names.index("v0.1.3")
    assert names[i + 1:i + 2] == ["v0.1.2"], f"894: CHANGELOG.md's v0.1.3 section is not right above v0.1.2: {names}"
    assert not unnamed(text, ("#894",)), "894: the v0.1.3 section does not name #894"


def test_changelog_has_v014_on_top():
    """The changelog's v0.1.4 section sits right above v0.1.3, naming the inner secrets fix #897."""
    names, text = section("897", "v0.1.4")
    i = names.index("v0.1.4")
    assert names[i + 1:i + 2] == ["v0.1.3"], f"897: CHANGELOG.md's v0.1.4 section is not right above v0.1.3: {names}"
    assert not unnamed(text, ("#897",)), "897: the v0.1.4 section does not name #897"


def test_changelog_has_v015_on_top():
    """The changelog's newest section is v0.1.5, above v0.1.4, naming every fix merged since v0.1.4."""
    names, text = section("919", "v0.1.5")
    assert names[:2] == ["v0.1.5", "v0.1.4"], f"919: CHANGELOG.md's newest headings are not v0.1.5 then v0.1.4: {names}"
    missing = unnamed(text, ("#916", "#908", "#910", "#906", "#905", "#873"))
    assert not missing, f"919: the v0.1.5 section does not name {missing}, fixes merged since v0.1.4"


def test_install_file_calls_newest_version(record_property):
    """The install file calls Dokima at the changelog's newest version, newer than v0.1.0.

    867.3: reads the tag `dokima/install/dokima.yml` calls Dokima's entry workflow at, and checks it is the version of
    CHANGELOG.md's top-most version heading and newer than v0.1.0, so adopters get the fixes merged since."""
    record_property("proves", "867.3")
    flow = yaml.safe_load(read("dokima/install/dokima.yml"))
    uses = [job.get("uses", "") for job in (flow.get("jobs") or {}).values()]
    tags = [u.split("@", 1)[1] for u in uses if u.startswith("dokima-dev/dokima/.github/workflows/entry.yml@")]
    assert tags, f"867.3: the install file never calls Dokima's entry workflow; its jobs use {uses}"
    newest = newest_version("867.3")
    assert tags[0] == newest, f"867.3: the install file calls Dokima at {tags[0]}, not {newest}, the changelog's newest"
    m = VERSION.fullmatch(tags[0])
    assert m and tuple(map(int, m.groups())) > (0, 1, 0), \
        f"867.3: the install file still calls Dokima at {tags[0]}, so adopters miss every fix merged since v0.1.0"


def doc_names_newest(crit, text, where):
    """Fails unless TEXT names the changelog's newest version, and no other version."""
    newest = newest_version(crit)
    named = sorted({m.group(0) for m in VERSION.finditer(text)})
    assert newest in named, f"{crit}: {where} never names {newest}, the newest release the install file calls"
    assert named == [newest], f"{crit}: {where} names {named}, other releases beside the newest, {newest}"


def test_readme_names_newest_release(record_property):
    """The README's install steps name the newest release, the one the install file calls.

    867.4: reads the README's Install section and checks it names the version of CHANGELOG.md's top-most version
    heading, and no other version."""
    record_property("proves", "867.4")
    match = re.search(r"^## Install\s*$(.*?)(?=^## |\Z)", read("README.md"), re.S | re.M)
    assert match, "867.4: README.md has no '## Install' section"
    doc_names_newest("867.4", match.group(1), "the README's Install section")


def test_wiki_names_newest_release(record_property):
    """The wiki's install page names the newest release, the one the install file calls.

    867.5: reads `docs/wiki/Installing.md` and checks it names the version of CHANGELOG.md's top-most version
    heading, and no other version."""
    record_property("proves", "867.5")
    doc_names_newest("867.5", read("docs/wiki/Installing.md"), "the wiki's Installing page")

"""Tests for #813: installing Dokima adds only its one workflow and its settings file.

Installing is the play-through's `Sandbox.install` (dokima/playthrough.py), the one installer Dokima has. Each test
installs this checkout of Dokima into a temp git repo standing in for the adopter's, then reads what landed there.
The stand-in's remote is a local bare repo, so nothing leaves the machine.
"""
import os
import subprocess

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = ".github/workflows/dokima.yml"
SETTINGS = ".dokima/settings.yaml"
# Fake values for every secret a Dokima run or the play-through can hold, set in the installer's environment.
SECRETS = {"SANDBOX_TOKEN": "sandbox-secret-value-813", "GH_TOKEN": "gh-secret-value-813",
           "CLAUDE_CODE_OAUTH_TOKEN": "claude-secret-value-813", "CLAUDE_TOKEN": "claude-token-value-813",
           "KIMI_API_KEY": "kimi-secret-value-813", "KIMI_SIGN_IN": "kimi-sign-in-value-813",
           "DOKIMA_APP_KEY": "app-key-value-813"}
PUSH_KEY = "push-key-value-813"
GIT_ID = ["-c", "user.name=Test Owner", "-c", "user.email=owner@example.com"]


def git(cwd, *args):
    """Run git in CWD with a test identity; its output."""
    return subprocess.run(["git", *GIT_ID, *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def adopter(tmp_path, seeded=True):
    """A bare repo standing in for the adopter's, holding one README unless SEEDED is false."""
    bare = tmp_path / "adopter.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    if seeded:
        seed = tmp_path / "seed"
        subprocess.run(["git", "init", "-q", "-b", "main", str(seed)], check=True)
        (seed / "README.md").write_text("An adopter's repo.\n")
        git(seed, "add", "-A")
        git(seed, "commit", "-qm", "first")
        git(seed, "push", "-q", str(bare), "main")
    return bare


def branch(bare):
    """The one branch of BARE; None when it has none."""
    refs = git(bare, "for-each-ref", "--format=%(refname)", "refs/heads").split()
    return refs[0] if refs else None


def files(bare):
    """Every file on BARE's branch, by path; empty when it has no branch."""
    ref = branch(bare)
    return set(git(bare, "ls-tree", "-r", "--name-only", ref).split()) if ref else set()


def install(bare, crit):
    """Install this checkout of Dokima into BARE with the play-through's installer, failing naming CRIT."""
    from dokima.playthrough import Sandbox
    sb = Sandbox("owner/adopter", ROOT, "0123abcd4567", PUSH_KEY)
    sb.url = str(bare)
    try:
        sb.install()
    except Exception as e:
        pytest.fail(f"{crit}: installing Dokima into a plain repo failed: {e}")


def added(bare, crit):
    """Install into BARE; the paths the install added and their text."""
    before = files(bare)
    install(bare, crit)
    ref = branch(bare)
    return {p: git(bare, "show", f"{ref}:{p}") for p in files(bare) - before}


def calls_entry(text):
    """True when the workflow TEXT calls Dokima's shared entry workflow from Dokima's own repo."""
    wf = yaml.safe_load(text) or {}
    uses = [str(j.get("uses", "")) for j in (wf.get("jobs") or {}).values() if isinstance(j, dict)]
    return any(u.startswith("dokima-dev/dokima/.github/workflows/entry.yml@") for u in uses)


def check_two_files(got, crit, what):
    """Fail naming CRIT unless GOT is exactly the thin workflow and the settings file."""
    assert set(got) == {WORKFLOW, SETTINGS}, \
        f"{crit}: installing into {what} should add exactly {WORKFLOW} and {SETTINGS}, not {sorted(got)[:12]}"
    assert calls_entry(got[WORKFLOW]), \
        f"{crit}: the installed {WORKFLOW} is not the one short workflow calling Dokima's shared entry workflow"


def test_installing_adds_exactly_the_one_workflow_and_the_settings_file(record_property, tmp_path):
    """Installing Dokima adds just two files: its one workflow and its settings file.

    Proves 813.1. Installs this checkout, which holds Dokima's code and all its workflows, into a repo holding one
    README, and checks the install added exactly `.github/workflows/dokima.yml` and `.dokima/settings.yaml`, the
    workflow being the short one that calls Dokima's shared workflows. Any Python file or other workflow added fails."""
    record_property("proves", "813.1")
    check_two_files(added(adopter(tmp_path), "813.1"), "813.1", "a repo holding one README")


def test_installing_into_an_empty_repo_adds_exactly_the_two_files(record_property, tmp_path):
    """Installing Dokima into an empty repo adds just the same two files.

    Proves 813.1, for the empty repo an owner starts from. Installs into a repo with no commits and checks its new
    branch holds exactly the one workflow and the settings file."""
    record_property("proves", "813.1")
    check_two_files(added(adopter(tmp_path, seeded=False), "813.1"), "813.1", "an empty repo")


def test_installing_writes_no_secrets_value_into_any_file_it_adds(record_property, tmp_path, monkeypatch):
    """No file the install adds holds the value of any secret.

    Proves 813.2. Sets fake values for every secret Dokima reads (the model keys, the app key, the push key and
    GitHub's token) where the installer runs, installs into a plain repo, and checks the settings file was added and
    that no added file holds any of those values."""
    record_property("proves", "813.2")
    for name, value in SECRETS.items():
        monkeypatch.setenv(name, value)
    got = added(adopter(tmp_path), "813.2")
    assert SETTINGS in got, f"813.2: installing added no {SETTINGS}, so there is no settings file to check: {sorted(got)[:12]}"
    for path, text in got.items():
        for name, value in list(SECRETS.items()) + [("the push key", PUSH_KEY)]:
            assert value not in text, f"813.2: installing wrote the value of {name} into {path}"


def test_the_installed_settings_file_never_ships_the_owners_co_author_line(record_property, tmp_path):
    """The settings file the install adds never carries Dokima's owner as co-author.

    Proves 813.3. Dokima's own settings file names its owner as co-author on every commit; an adopter must get the
    shipped default instead. Installs into a plain repo and checks the added settings file exists and does not hold
    the co-author line Dokima's own settings file names."""
    record_property("proves", "813.3")
    got = added(adopter(tmp_path), "813.3")
    assert SETTINGS in got, f"813.3: installing added no {SETTINGS}: {sorted(got)[:12]}"
    mine = str((yaml.safe_load(open(os.path.join(ROOT, SETTINGS))) or {}).get("co_author") or "")
    assert mine and "{bot}" not in mine, f"813.3: Dokima's own {SETTINGS} names no owner as co-author to compare with"
    assert mine not in got[SETTINGS], f"813.3: the installed {SETTINGS} ships the owner's co-author line {mine!r}"

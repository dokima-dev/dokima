"""Dokima's own commits are credited to its bot, never to the unrelated GitHub user "dokima".

GitHub maps a `<name>@users.noreply.github.com` address to the account called `<name>`, so a commit made as
`dokima@users.noreply.github.com` credits the stranger at github.com/dokima as a contributor (#567). These tests
check every place Dokima commits: the worker's merge of main, the play-through, and every other file in the repo.
"""

import os
import re
import subprocess
import tempfile

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
BOT_NAMES = {"dokima-runtime[bot]", "${SLUG}[bot]"}
BOT_EMAILS = {"337511017+dokima-runtime[bot]@users.noreply.github.com",
              "${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"}
REZA_EMAIL = "34189616+RezaSoleymanifar@users.noreply.github.com"
NOREPLY = re.compile(r"[^\s\"'<>=`(),:;]+@users\.noreply\.github\.com")


def starting_branch_step():
    """Returns the lines of agent.yml's step that merges main into the worker's branch."""
    text = open(os.path.join(ROOT, ".github/workflows/agent.yml")).read()
    start = text.index("- name: Starting branch")
    end = text.index("\n      - name:", start + 1)
    return text[start:end].splitlines()


def identity_in_effect(lines, i):
    """Returns the git name and email in effect for line i of the step.

    Either is None when the step never sets it. A `-c user.name=` / `-c user.email=` on the line itself wins; otherwise the last `git config user.name/email`
    above it in the step counts."""
    def value(key, line):
        m = re.search(rf'-c\s+{key}=("([^"]*)"|(\S+))', line)
        return (m.group(2) if m.group(2) is not None else m.group(3)) if m else None

    def configured(key):
        for line in reversed(lines[:i]):
            m = re.search(rf'git\s+config\s+{key}\s+("([^"]*)"|(\S+))', line)
            if m:
                return m.group(2) if m.group(2) is not None else m.group(3)
        return None

    line = lines[i]
    return (value("user.name", line) or configured("user.name"),
            value("user.email", line) or configured("user.email"))


def git_lines(lines, word):
    """Returns the indexes of the step's lines that run `git ... <word>`."""
    return [i for i, line in enumerate(lines) if re.search(rf"\bgit\b.*\s{word}\s", line)]


def test_worker_merge_of_main_is_credited_to_the_bot(record_property):
    """Merging main into a worker's branch commits as dokima-runtime[bot], never as "dokima".

    Proves 567.1. Reads agent.yml's Starting branch step, finds its `git merge` of main, and checks the git name and email in
    effect for it are the bot's."""
    record_property("proves", "567.1")
    lines = starting_branch_step()
    merges = git_lines(lines, "merge")
    assert merges, "567.1: the Starting branch step no longer merges main, so its identity cannot be checked"
    for i in merges:
        name, email = identity_in_effect(lines, i)
        assert email in BOT_EMAILS, f"567.1: the worker's merge of main commits as {email!r}, not the bot's address"
        assert name in BOT_NAMES, f"567.1: the worker's merge of main commits as name {name!r}, not the bot's"


def test_worker_conflict_commit_is_credited_to_the_bot(record_property):
    """A clash with main is saved in a commit made as dokima-runtime[bot].

    Proves 567.1. Reads agent.yml's Starting branch step, finds the `git commit` that records the clashed merge, and checks the
    git name and email in effect for it are the bot's."""
    record_property("proves", "567.1")
    lines = starting_branch_step()
    commits = git_lines(lines, "commit")
    assert commits, "567.1: the Starting branch step no longer commits a clashed merge, so its identity cannot be checked"
    for i in commits:
        name, email = identity_in_effect(lines, i)
        assert email in BOT_EMAILS, f"567.1: the clash commit is made as {email!r}, not the bot's address"
        assert name in BOT_NAMES, f"567.1: the clash commit is made as name {name!r}, not the bot's"


def steps_that_always_run_before_starting_branch():
    """Returns the ids of steps that run before Starting branch on every run.

    A step with an `if:` may be skipped, so its outputs can be blank; a step after Starting branch has no outputs yet."""
    text = open(os.path.join(ROOT, ".github/workflows/agent.yml")).read()
    before = text[:text.index("- name: Starting branch")]
    ids = set()
    for step in re.split(r"\n      - ", before)[1:]:
        m = re.search(r"(?:^|\n\s*)id:\s*([\w-]+)", step)
        if m and not re.search(r"(?:^|\n\s*)if:", step):
            ids.add(m.group(1))
    return ids


def test_bot_identity_in_step_is_defined(record_property):
    """The bot's address in the merge step is never blank or the old one.

    Proves 567.1. When the step names the bot through ${SLUG} or ${BOT_ID}, it must set both. A `${BOT_ID}+${SLUG}[bot]`
    address with neither set would commit as `+[bot]@users.noreply.github.com`. Every step output the step reads must come
    from a step that ran before it on every run: one that runs later, such as `steps.app`, or may be skipped, is blank."""
    record_property("proves", "567.1")
    lines = starting_branch_step()
    text = "\n".join(lines)
    if "${SLUG}" in text or "${BOT_ID}" in text:
        assert re.search(r"\bSLUG[:=]", text), "567.1: the Starting branch step uses ${SLUG} but never sets it"
        assert re.search(r"\bBOT_ID[:=]", text), "567.1: the Starting branch step uses ${BOT_ID} but never sets it"
    ready = steps_that_always_run_before_starting_branch()
    for used in sorted(set(re.findall(r"\bsteps\.([\w-]+)\.outputs", text))):
        assert used in ready, (f"567.1: the Starting branch step reads steps.{used}, which runs after it or may be "
                               "skipped, so the bot's name or address comes out blank")
    assert "dokima@users.noreply.github.com" not in text, "567.1: the Starting branch step still names dokima@users.noreply.github.com"


@pytest.fixture
def sandbox(tmp_path):
    """A play-through Sandbox whose clone is a local temp git repo.

    Its commits can then be read back."""
    from dokima.playthrough import Sandbox
    sb = Sandbox("owner/sandbox", "played", "abc123", "token")
    clone = tmp_path / "sandbox"
    subprocess.run(["git", "init", "-q", str(clone)], check=True)
    sb.clone = str(clone)
    return sb


def test_playthrough_commits_as_the_bot(record_property, sandbox):
    """The play-through's commits are authored and committed by dokima-runtime[bot].

    Proves 567.2. Makes a real commit through the play-through's own git helper in a temp repo and reads its author and
    committer back."""
    record_property("proves", "567.2")
    sandbox.git("commit", "-q", "--allow-empty", "-m", "play")
    who = subprocess.run(["git", "log", "-1", "--format=%an <%ae>|%cn <%ce>"], cwd=sandbox.clone,
                         capture_output=True, text=True, check=True).stdout.strip()
    bot = "dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>"
    author, committer = who.split("|")
    assert author == bot, f"567.2: the play-through's commit is authored by {author}, not {bot}"
    assert committer == bot, f"567.2: the play-through's commit is committed by {committer}, not {bot}"


def tracked_files():
    """Returns every file git tracks in the repo, except this test.

    This test names the bad addresses on purpose."""
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    me = os.path.relpath(__file__, ROOT).replace(os.sep, "/")
    return [p for p in out.splitlines() if p != me]


def noreply_addresses():
    """Returns {address: [files]} for every `@users.noreply.github.com` address in a tracked file."""
    found = {}
    for path in tracked_files():
        try:
            text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            continue
        for address in NOREPLY.findall(text):
            found.setdefault(address, []).append(path)
    return found


def test_no_file_commits_as_anyone_but_the_bot_or_reza(record_property):
    """No file names a GitHub noreply address other than the bot's or Reza's.

    Proves 567.3. Reads every tracked file and lists each `<name>@users.noreply.github.com` address that belongs to someone
    else, such as the stranger "dokima", the play-through's made-up name or GitHub Actions' own bot.
    It also checks the scan finds the bot's and Reza's addresses in agent.yml, so it never passes blind."""
    record_property("proves", "567.3")
    found = noreply_addresses()
    for mine in ("${BOT_ID}+${SLUG}[bot]@users.noreply.github.com", REZA_EMAIL):
        assert ".github/workflows/agent.yml" in found.get(mine, []), f"567.3: the scan missed {mine} in agent.yml"
    others = {a: files for a, files in found.items() if a not in BOT_EMAILS | {REZA_EMAIL}}
    assert not others, "567.3: files commit as someone other than the bot or Reza: " + "; ".join(
        f"{a} in {', '.join(sorted(set(f)))}" for a, f in sorted(others.items()))

"""Tests for #816: an empty repo reaches its first merge following only the docs.

The full proof needs real GitHub, so the owner checks it by hand (#742). What a test can prove here is the one step of
the docs that stops a first merge on its own: the branch rule. Main only merges once every check it requires has
passed, and a check GitHub never posts under that exact name never passes.

Since #812 an adopter's checks run inside the thin workflow, which calls entry.yml, which calls each shared workflow.
GitHub names such a check by the chain of calling jobs, `caller / called / job`, so `all tests` shows as
`dokima / full-suite / all tests`. The test installs the two files the README names into an empty temp repo, works
out from the installed workflow and Dokima's shared workflows the name each required check gets there, and checks the
README's Install section and the wiki's Installing page tell the owner to require that exact name.
"""
import os
import re
import shutil
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
CALL = re.compile(r"^dokima-dev/dokima/\.github/workflows/([\w.-]+\.ya?ml)@.+$")
LOCAL = re.compile(r"^\./\.github/workflows/([\w.-]+\.ya?ml)$")


def read_yaml(path):
    """The workflow at PATH, read with `on` kept as a name."""
    data = yaml.safe_load(open(path).read()) or {}
    if True in data:
        data["on"] = data.pop(True)
    return data


def readme_install():
    """The README's Install section, from its heading to the next top-level heading."""
    text = open(os.path.join(ROOT, "README.md")).read()
    match = re.search(r"^## Install\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert match, "816.1: README.md has no '## Install' section"
    return match.group(1)


def wiki_install():
    """The wiki's Installing page."""
    return open(os.path.join(ROOT, "docs", "wiki", "Installing.md")).read()


def install_from_readme(repo):
    """Follow the README's add-file steps into a new empty repo; returns the installed workflow's path.

    REPO is where the empty git repo is made.

    Every numbered step naming a `dokima/install/` file and where it goes is done by copying that file there."""
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    done = []
    for line in readme_install().splitlines():
        if not re.match(r"\s*\d+\.\s", line):
            continue
        source = re.search(r"`(dokima/install/[^`]+)`", line)
        target = re.search(r"\bas `([^`]+)`", line)
        if source and target:
            dest = os.path.join(repo, target.group(1))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(os.path.join(ROOT, source.group(1)), dest)
            done.append(target.group(1))
    workflows = [p for p in done if p.startswith(".github/workflows/")]
    assert workflows, "816.1: no README install step adds a workflow to the repo"
    return os.path.join(repo, workflows[0])


def job_label(job_id, job):
    """The name GitHub shows for JOB: its `name`, or its id when it has none."""
    return str(job.get("name") or job_id)


def posted_names(path, prefix=""):
    """Each check name the workflow at PATH posts in an adopter repo, by short name.

    A job calling one of Dokima's shared workflows adds its own label to the front, `caller / job`, as GitHub does."""
    out = {}
    for job_id, job in (read_yaml(path).get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        here = prefix + job_label(job_id, job)
        uses = str(job.get("uses") or "")
        called = CALL.match(uses) or LOCAL.match(uses)
        if called:
            out.update(posted_names(os.path.join(WORKFLOWS, called.group(1)), here + " / "))
        elif "${{" not in here:
            out.setdefault(here.rpartition(" / ")[2], here)
    return out


def test_the_docs_name_the_required_checks_as_an_adopters_repo_shows_them(record_property, tmp_path):
    """The install docs name each required check as GitHub shows it in an adopter's repo.

    Proves 816.1. Follows the README's add-file steps into an empty temp repo, then works out, from the installed
    workflow and the shared workflows it calls, the full name each check the docs require gets there (for example
    `dokima / full-suite / all tests`). It fails unless the README's Install section and the wiki's Installing page
    each name every such full name, since a required check that is never posted under its name never lets a pull
    request merge."""
    record_property("proves", "816.1")
    thin = install_from_readme(str(tmp_path / "empty"))
    posted = posted_names(thin)
    required = ["all tests", "Acceptance criteria"]
    missing = [name for name in required if name not in posted]
    assert not missing, f"816.1: the installed workflow never runs the checks the docs require: {missing}"
    for page, text in (("README.md Install section", readme_install()), ("docs/wiki/Installing.md", wiki_install())):
        unnamed = [posted[name] for name in required if posted[name] not in text]
        assert not unnamed, (f"816.1: {page} never tells the owner to require {unnamed}, the names GitHub gives "
                             "these checks in a repo with the thin install, so main's rule waits forever and the "
                             "first pull request never merges")

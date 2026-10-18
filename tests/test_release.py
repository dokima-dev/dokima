"""Tests for #755: Dokima's first release, v0.1.0, with a changelog.

The changelog is CHANGELOG.md at the repo root, with a section for v0.1.0 listing what that version does; that
section becomes the notes of the v0.1.0 GitHub release.
The tag and the GitHub release are made by code, not by hand: a workflow, .github/workflows/release.yml, runs on every
push to main and runs one command, `python3 -m dokima.release <owner/repo> <commit>`, from the repo root. That command
reads CHANGELOG.md and, when its v0.1.0 has no release yet, makes the v0.1.0 tag and GitHub release at that commit,
with the changelog's v0.1.0 section as the release notes.

The release tests read the workflow, take the command its step runs, and run it for real in a temp folder holding a
changelog, with a fake `gh` first on PATH. The fake keeps GitHub's releases in a JSON file and logs every call, so a
test sees exactly what the command asked GitHub to do. Nothing leaves the machine.

What the fake `gh` answers (any other call is logged as unsupported and exits 1, as GitHub would refuse it):
    gh release view TAG [--repo R] [...]          the release, or exit 1 "release not found"
    gh release list [--repo R] [...]              every release (JSON when --json is given)
    gh api [-X GET] repos/R/releases[?...]        every release
    gh api [-X GET] repos/R/releases/tags/TAG     the release, or 404
    gh api [-X GET] repos/R/git/ref[s]/tags/TAG   the tag, or 404
    gh release create TAG [--repo R] [--target SHA] [--notes TEXT | --notes-file FILE] [...]
                                                  makes the tag and its release, keeping its notes
    gh api [-X POST] repos/R/releases -f tag_name=TAG [-f target_commitish=SHA] [-f body=TEXT | -F body=@FILE]
                                                  the same, the API way
"""
import json
import os
import re
import shlex
import stat
import subprocess
import sys
import textwrap

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "release.yml")
REPO = "dokima-dev/dokima"
SHA = "0123456789abcdef0123456789abcdef01234567"
SAMPLE = "# Changelog\n\n## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n"

FAKE_GH = textwrap.dedent('''
    """A fake gh keeping GitHub's releases in the JSON file named by FAKE_GH_STATE."""
    import json, os, sys

    STATE = os.environ["FAKE_GH_STATE"]
    with open(STATE) as f:
        state = json.load(f)
    args = sys.argv[1:]
    state["calls"].append(args)


    def done(out=None, code=0, err=None):
        """Save the state, answer and exit."""
        with open(STATE, "w") as f:
            json.dump(state, f, indent=1)
        if out is not None:
            print(json.dumps(out))
        if err:
            print(err, file=sys.stderr)
        sys.exit(code)


    def opt(names):
        """The value of the first of these options, else None."""
        for i, a in enumerate(args):
            for n in names:
                if a == n and i + 1 < len(args):
                    return args[i + 1]
                if a.startswith(n + "="):
                    return a.split("=", 1)[1]
        return None


    def fields():
        """The -f / -F / --field / --raw-field key=value pairs of a gh api call."""
        got = {}
        for i, a in enumerate(args):
            if a in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(args):
                k, _, v = args[i + 1].partition("=")
                got[k] = v
        return got


    def notes():
        """The release notes the call sends: --notes, --notes-file / -F, or a body field; else empty."""
        if args[:1] != ["api"]:
            text = opt(["--notes", "-n"])
            if text is not None:
                return text
            path = opt(["--notes-file", "-F"])
            if path is not None:
                with open(sys.stdin.fileno() if path == "-" else path) as f:
                    return f.read()
            return ""
        body = fields().get("body", "")
        if body.startswith("@"):
            with open(sys.stdin.fileno() if body == "@-" else body[1:]) as f:
                return f.read()
        return body


    def release(tag):
        """The release of TAG, else None."""
        return next((r for r in state["releases"] if r["tag_name"] == tag), None)


    def make(tag, target):
        """Make TAG and its release, as GitHub does; refuse when the state says so."""
        if state.get("refuse_create"):
            done(code=1, err="gh: Resource not accessible by integration (HTTP 403)")
        if release(tag):
            done(code=1, err="gh: Validation Failed: tag_name already_exists (HTTP 422)")
        r = {"tag_name": tag, "tagName": tag, "name": tag, "target_commitish": target}
        state["releases"].append(r)
        state["created"].append({"tag": tag, "target": target, "notes": notes()})
        done(r)


    if args[:2] == ["release", "view"] and len(args) > 2:
        r = release(args[2])
        done(r) if r else done(code=1, err="release not found")
    if args[:2] == ["release", "list"]:
        if "--json" in args or any(a.startswith("--json=") for a in args):
            done(state["releases"])
        print("\\n".join(f"{r['tag_name']}\\tLatest\\t{r['tag_name']}\\t2026-10-18" for r in state["releases"]))
        done()
    if args[:2] == ["release", "create"] and len(args) > 2:
        make(args[2], opt(["--target"]))
    if args[:1] == ["api"]:
        path = next((a for a in args[1:] if a.startswith("repos/") or a.startswith("/repos/")), "").lstrip("/")
        method = (opt(["-X", "--method"]) or ("POST" if fields() else "GET")).upper()
        base = "repos/" + state["repo"] + "/"
        rest = path[len(base):].split("?")[0] if path.startswith(base) else None
        if rest == "releases" and method == "POST":
            f = fields()
            make(f.get("tag_name"), f.get("target_commitish"))
        if rest == "releases" and method == "GET":
            done(state["releases"])
        if rest is not None and rest.startswith("releases/tags/") and method == "GET":
            r = release(rest[len("releases/tags/"):])
            done(r) if r else done({"message": "Not Found"}, 1, "gh: Not Found (HTTP 404)")
        for p in ("git/ref/tags/", "git/refs/tags/"):
            if rest is not None and rest.startswith(p) and method == "GET":
                r = release(rest[len(p):])
                done({"ref": "refs/tags/" + r["tag_name"]}) if r else done({"message": "Not Found"}, 1, "gh: Not Found (HTTP 404)")
    state["unsupported"].append(args)
    done(code=1, err="gh: unsupported by the fake gh: " + " ".join(args))
''')


def changelog_section(text, version):
    """The lines under the changelog heading naming VERSION, up to the next such heading."""
    lines = text.splitlines()
    heading = re.compile(r"^(#{1,6})\s+.*" + re.escape(version) + r"(?![0-9])")
    for i, line in enumerate(lines):
        m = heading.match(line)
        if m:
            level = len(m.group(1))
            out = []
            for later in lines[i + 1:]:
                h = re.match(r"^(#{1,6})\s", later)
                if h and len(h.group(1)) <= level:
                    break
                out.append(later)
            return out
    return None


def release_command(crit):
    """The command release.yml runs, with the repo and commit filled in."""
    assert os.path.isfile(WORKFLOW), f"{crit}: no release workflow: .github/workflows/release.yml is missing"
    with open(WORKFLOW) as f:
        flow = yaml.safe_load(f)
    on = flow.get("on", flow.get(True)) or {}
    branches = ((on.get("push") or {}) if isinstance(on, dict) else {}).get("branches") or []
    assert "main" in branches, f"{crit}: release.yml does not run on a push to main; its triggers are {on!r}"
    runs = [s.get("run", "") for job in (flow.get("jobs") or {}).values() for s in job.get("steps") or []]
    found = [line.strip() for run in runs for line in run.splitlines() if "dokima.release" in line]
    assert found, f"{crit}: release.yml has no step running `python3 -m dokima.release`"
    line = found[0].replace("${{ github.repository }}", REPO).replace("${{ github.sha }}", SHA)
    return [sys.executable if w in ("python", "python3") else w for w in shlex.split(line)]


def run_release(tmp_path, crit, releases=(), refuse=False, changelog=SAMPLE):
    """Run release.yml's command against the fake gh, in a temp folder with an optional changelog.

    Returns the finished process and the fake GitHub's state afterwards."""
    cmd = release_command(crit)
    work = tmp_path / "repo"
    work.mkdir()
    if changelog is not None:
        (work / "CHANGELOG.md").write_text(changelog)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(f"#!{sys.executable}\n" + FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    state = tmp_path / "gh.json"
    state.write_text(json.dumps({"repo": REPO, "calls": [], "created": [], "unsupported": [],
                                 "refuse_create": refuse,
                                 "releases": [{"tag_name": t, "tagName": t, "name": t, "target_commitish": "old"}
                                              for t in releases]}))
    env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", FAKE_GH_STATE=str(state),
               PYTHONPATH=ROOT, GH_TOKEN="fake-token-755", GITHUB_TOKEN="fake-token-755", GITHUB_REPOSITORY=REPO,
               GITHUB_SHA=SHA)
    done = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=30)
    return done, json.loads(state.read_text())


def test_release_notes_are_changelog_section(tmp_path, record_property):
    """The v0.1.0 release's notes are the changelog's v0.1.0 section.

    755.3: runs the command release.yml runs on a changelog holding an Unreleased section above v0.1.0, and checks
    the notes it sends GitHub carry every v0.1.0 line and nothing from the other section."""
    record_property("proves", "755.3")
    changelog = ("# Changelog\n\n## Unreleased\n\n- A draft line not yet released.\n\n"
                 "## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n")
    done, state = run_release(tmp_path, "755.3", changelog=changelog)
    assert not state["unsupported"], f"755.3: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.3: the release command failed: {done.stderr[-800:]}"
    assert len(state["created"]) == 1, f"755.3: expected one release made, got {state['created']}"
    notes = state["created"][0]["notes"]
    missing = [i for i in ("Work starts with a comment: /plan, /work and /review.", "One card on every issue.")
               if i not in notes]
    assert not missing, f"755.3: the v0.1.0 release notes leave out these changelog lines: {missing}"
    assert "A draft line not yet released." not in notes, \
        "755.3: the v0.1.0 release notes carry a line from the changelog's Unreleased section"


def test_release_makes_tag(tmp_path, record_property):
    """When the changelog reaches main, the v0.1.0 tag is made at that commit.

    755.1: runs the command release.yml runs on a push to main against a fake GitHub with no releases, and checks it
    made exactly one tag, v0.1.0, at the pushed commit."""
    record_property("proves", "755.1")
    done, state = run_release(tmp_path, "755.1")
    assert not state["unsupported"], f"755.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.1: the release command failed: {done.stderr[-800:]}"
    tags = [(c["tag"], c["target"]) for c in state["created"]]
    assert tags == [("v0.1.0", SHA)], f"755.1: expected one v0.1.0 tag at the pushed commit, got {tags}"


def test_release_skips_when_tagged(tmp_path, record_property):
    """A later push to main makes no second v0.1.0 release once it exists.

    755.1, edge case: every push to main runs the workflow, so with v0.1.0 already released the command makes nothing
    and still succeeds."""
    record_property("proves", "755.1")
    done, state = run_release(tmp_path, "755.1", releases=["v0.1.0"])
    assert not state["unsupported"], f"755.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.1: the release command failed when v0.1.0 already exists: {done.stderr[-800:]}"
    assert state["created"] == [], f"755.1: v0.1.0 already exists, yet the command made {state['created']}"


def test_release_makes_github_release(tmp_path, record_property):
    """When the changelog reaches main, a GitHub release named v0.1.0 is made.

    755.2: runs the command release.yml runs on a push to main against a fake GitHub, and checks GitHub's releases
    then hold v0.1.0."""
    record_property("proves", "755.2")
    done, state = run_release(tmp_path, "755.2")
    assert not state["unsupported"], f"755.2: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.2: the release command failed: {done.stderr[-800:]}"
    assert [r["tag_name"] for r in state["releases"]] == ["v0.1.0"], \
        f"755.2: expected GitHub to hold one release, v0.1.0, got {state['releases']}"


def test_release_refused_fails_the_run(tmp_path, record_property):
    """When GitHub refuses the release, the run fails, so the owner sees it.

    755.2, edge case: the fake GitHub refuses to make the release; the command must exit non-zero, never pass quietly."""
    record_property("proves", "755.2")
    done, state = run_release(tmp_path, "755.2", refuse=True)
    assert not state["unsupported"], f"755.2: the release command made calls the fake gh does not know: {state['unsupported']}"
    asked = [c for c in state["calls"] if c[:2] == ["release", "create"] or (c[:1] == ["api"] and "POST" in c)
             or (c[:1] == ["api"] and any(a.startswith("tag_name=") for a in c))]
    assert asked, "755.2: the command never asked GitHub for the release"
    assert done.returncode != 0, "755.2: GitHub refused the release, yet the command exited 0"


def test_release_waits_for_changelog(tmp_path, record_property):
    """A push to main before the changelog arrives makes no tag and no release.

    755.1, edge case: main has no CHANGELOG.md yet, so the command run on every push to main must make nothing and
    still succeed. Code that tags v0.1.0 on any push fails here."""
    record_property("proves", "755.1")
    done, state = run_release(tmp_path, "755.1", changelog=None)
    assert not state["unsupported"], f"755.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.1: the release command failed when main has no changelog: {done.stderr[-800:]}"
    assert state["created"] == [], f"755.1: main has no changelog, yet the command made {state['created']}"


def test_release_waits_for_version_section(tmp_path, record_property):
    """A changelog with no v0.1.0 section yet makes no tag and no release.

    755.1, edge case: the changelog holds only an Unreleased section, so v0.1.0 has not reached main; the command must
    make nothing and still succeed."""
    record_property("proves", "755.1")
    done, state = run_release(tmp_path, "755.1", changelog="# Changelog\n\n## Unreleased\n\n- A draft line.\n")
    assert not state["unsupported"], f"755.1: the release command made calls the fake gh does not know: {state['unsupported']}"
    assert done.returncode == 0, f"755.1: the release command failed on a changelog with no v0.1.0: {done.stderr[-800:]}"
    assert state["created"] == [], f"755.1: the changelog has no v0.1.0 section, yet the command made {state['created']}"

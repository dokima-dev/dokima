"""A pull request changing only text files skips the plan and its tests (issue #358).

Most tests here run the real command the Acceptance criteria workflow runs, `python3 -m dokima.checks matrix`, from the repo
root, with GitHub faked: a stub `gh` on PATH answers the pull request's changed files (GitHub's `pulls/N/files` list,
split over two pages the way `gh api --paginate` prints them back to back) and finds no plan: either no issue is
linked, or the description says "Closes #77" and issue #77 has no comments and no pull requests.
Others run the shell of the Acceptance criteria workflow's own steps, cut out of `.github/workflows/acceptance-criteria.yml`, with a fake
`pytest` on PATH, so the workflow GitHub runs is the thing judged. Nothing here touches the network.

Text files are `.md` files outside `dokima/roles/`, `tests/` and `.github/`: AGENTS.md, README.md, the wiki under
docs/wiki/ and any other Markdown file. Anything else changed sends the pull request the full way.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "acceptance-criteria.yml")
SHORTCUT = "Text only: no plan needed"
NO_ISSUE = "No approved plan found: no issue linked"
PR = 900

STUB_GH = '''#!/usr/bin/env python3
"""A stand-in for the GitHub CLI: answers from $STUB_DATA and logs every call."""
import json, os, sys
data = json.load(open(os.environ["STUB_DATA"]))
a = sys.argv[1:]
with open(os.environ["STUB_DATA"] + ".calls", "a") as f:
    f.write(json.dumps(a) + "\\n")
if any("pulls/%d/files" % data["pr"] in x for x in a):
    if data.get("files_fail"):
        print("gh: Server Error (HTTP 502)", file=sys.stderr)
        sys.exit(1)
    for page in data["pages"]:
        print(json.dumps(page))
elif a[:2] == ["issue", "view"]:
    print(json.dumps({"number": int(a[2]), "title": "An issue with no plan", "body": "", "comments": []}))
elif a[:2] == ["api", "graphql"]:
    print(json.dumps({"data": {"repository": {"pullRequest": {"closingIssuesReferences": {"nodes": []}}}}}))
else:
    print("[]")
'''


def changed(*names, status="modified"):
    """GitHub's changed-file entries for these paths."""
    return [{"filename": n, "status": status} for n in names]


def run_matrix(tmp_path, files, files_fail=False, body=""):
    """Run the merge check's matrix command for a pull request with these files and description.

    Returns (rows or None, output)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(STUB_GH)
    gh.chmod(0o755)
    half = (len(files) + 1) // 2
    data = tmp_path / "data.json"
    data.write_text(json.dumps({"pr": PR, "pages": [files[:half], files[half:]], "files_fail": files_fail}))
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"number": PR, "head": {"ref": "owner/text-edit"}, "body": body}}))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": "o/r",
           "GITHUB_EVENT_PATH": str(event), "STUB_DATA": str(data), "GH_TOKEN": "x", "PYTHONPATH": ROOT}
    p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=30)
    rows = None
    for line in p.stdout.splitlines():
        if line.startswith("matrix="):
            rows = json.loads(line[len("matrix="):])
    return rows, f"exit {p.returncode}\n{p.stdout}{p.stderr}"


def step_script(name):
    """The shell one Acceptance criteria workflow step runs, found by step name or job key."""
    lines = open(WORKFLOW).read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() in (f"- name: {name}", f"{name}:"))
    run = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    indent = None
    body = []
    for line in lines[run + 1:]:
        if line.strip() == "":
            body.append("")
            continue
        here = len(line) - len(line.lstrip())
        if indent is None:
            indent = here
        if here < indent:
            break
        body.append(line[indent:])
    return "\n".join(body) + "\n"


def run_step(tmp_path, name, env):
    """Run a workflow step's shell with bash and a fake `pytest` that logs being run.

    Returns (exit code, output, whether pytest ran)."""
    bin_dir = tmp_path / "stepbin"
    bin_dir.mkdir(exist_ok=True)
    marker = tmp_path / "pytest-ran"
    fake = bin_dir / "pytest"
    fake.write_text(f"#!/bin/sh\necho ran > '{marker}'\nexit 1\n")
    fake.chmod(0o755)
    p = subprocess.run(["bash", "-e", "-c", step_script(name)], cwd=tmp_path, capture_output=True, text=True,
                       timeout=30, env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", **env})
    return p.returncode, p.stdout + p.stderr, marker.exists()


def is_shortcut(rows):
    """True when the check list is exactly the one text-only check, which runs no tests."""
    return rows is not None and len(rows) == 1 and rows[0]["name"] == SHORTCUT and rows[0]["id"] == "text-only" \
        and rows[0]["tests"] == ""


def test_a_pull_request_changing_only_text_files_gets_the_text_only_check(record_property, tmp_path):
    """A pull request changing only AGENTS.md, README, wiki or other .md files gets "Text only".

    Proves 358.1.
    Runs the real merge check for pull requests with no issue and no plan that change only text files: AGENTS.md
    alone, README.md alone, a wiki page, and several Markdown files at once (added, changed and removed, over two pages
    of GitHub's file list). Then a text-only pull request saying "Closes #77", for an issue with no plan. Each must get
    exactly one check, "Text only: no plan needed", in place of the failing "No approved plan found"."""
    record_property("proves", "358.1")
    cases = {
        "AGENTS.md alone": changed("AGENTS.md"),
        "README.md alone": changed("README.md"),
        "a wiki page": changed("docs/wiki/Home.md"),
        "several .md files": changed("AGENTS.md", "README.md", "docs/wiki/FAQ.md")
                             + changed("docs/notes/new.md", status="added")
                             + changed("docs/wiki/Old.md", status="removed"),
    }
    for what, files in cases.items():
        rows, out = run_matrix(tmp_path, files)
        assert is_shortcut(rows), (f"358.1: a pull request changing only text files ({what}) did not get the single "
                                   f"'{SHORTCUT}' check: {rows}\n{out}")
    rows, out = run_matrix(tmp_path, changed("AGENTS.md"), body="Closes #77")
    assert is_shortcut(rows), (f"358.1: a text-only pull request saying 'Closes #77', for an issue with no plan, did not "
                               f"get the single '{SHORTCUT}' check: {rows}\n{out}")


def test_the_text_only_check_passes_without_running_any_test(record_property, tmp_path):
    """The "Text only" check passes without running any test, and the gate goes green.

    Proves 358.2.
    Runs the Acceptance criteria workflow's own test step with the text-only check's id and no tests: it must exit 0 without
    calling pytest. The same step for a real criterion with no test must still fail saying it has no test, so the pass
    is not a step that passes everything. Then the gate step, given the text-only check list and a passing check job,
    must pass."""
    record_property("proves", "358.2")
    code, out, ran = run_step(tmp_path, "Run this criterion's tests", {"ID": "text-only", "TESTS": ""})
    assert code == 0, f"358.2: the text-only check failed in the Acceptance criteria workflow (exit {code}):\n{out}"
    assert not ran, "358.2: the text-only check ran pytest; it should pass without running any test"
    code, out, ran = run_step(tmp_path, "Run this criterion's tests", {"ID": "358.1", "TESTS": ""})
    assert code != 0 and "has no test" in out, \
        f"358.2: a real criterion with no test now passes too (exit {code}); only the text-only check may:\n{out}"
    matrix = json.dumps([{"id": "text-only", "name": SHORTCUT, "tests": ""}])
    code, out, _ = run_step(tmp_path, "gate", {"MATRIX": matrix, "RESULT": "success"})
    assert code == 0, f"358.2: the 'Acceptance criteria' gate failed on a passing text-only check (exit {code}):\n{out}"


def test_a_pull_request_touching_anything_but_text_files_goes_the_full_way(record_property, tmp_path):
    """Any code, test, workflow, role or non-Markdown file changed means no shortcut.

    Proves 358.3.
    Runs the real merge check for pull requests with no issue and no plan, each changing AGENTS.md plus one other
    file: Python code, a test, a workflow, a role file under dokima/roles/ (Markdown, but it is the agents' prompt), a
    JSON file, a file with no extension, a .md file under tests/ and one under .github/. Then a file renamed from code to
    a .md name, one deleted code file beside a text file, and a code change saying "Closes #77" for an issue with no
    plan. Each must get today's failing "No approved plan found"
    check, never the text-only one. A pull request changing only text files must still get the shortcut, so the check
    is not one that says no to everything."""
    record_property("proves", "358.3")
    others = ["dokima/checks.py", "tests/test_checks.py", ".github/workflows/full-suite.yml",
              "dokima/roles/planner.md", "dokima/app.json", "LICENSE", "tests/samples/notes.md",
              ".github/PULL_REQUEST_TEMPLATE.md"]
    for other in others:
        rows, out = run_matrix(tmp_path, changed("AGENTS.md", other))
        assert rows is not None and [r["name"] for r in rows] == [NO_ISSUE], \
            f"358.3: a pull request changing {other} took the text-only shortcut or lost its checks: {rows}\n{out}"
    renamed = [{"filename": "docs/checks.md", "status": "renamed", "previous_filename": "dokima/checks.py"}]
    rows, out = run_matrix(tmp_path, renamed)
    assert rows is not None and [r["name"] for r in rows] == [NO_ISSUE], \
        f"358.3: renaming a code file to a .md name took the text-only shortcut: {rows}\n{out}"
    rows, out = run_matrix(tmp_path, changed("README.md") + changed("dokima/trail.py", status="removed"))
    assert rows is not None and [r["name"] for r in rows] == [NO_ISSUE], \
        f"358.3: deleting a code file beside a text change took the text-only shortcut: {rows}\n{out}"
    rows, out = run_matrix(tmp_path, changed("AGENTS.md", "dokima/checks.py"), body="Closes #77")
    assert rows is not None and [r["name"] for r in rows] == ["No approved plan found for issue #77"], \
        f"358.3: a code change saying 'Closes #77', for an issue with no plan, took the text-only shortcut: {rows}\n{out}"
    rows, out = run_matrix(tmp_path, changed("README.md", "docs/wiki/Home.md"))
    assert is_shortcut(rows), f"358.3: a text-only pull request lost its shortcut: {rows}\n{out}"


def test_the_owner_still_approves_and_merges_a_text_only_pull_request(record_property, tmp_path):
    """A text-only pull request still needs both checks and the owner's approval.

    Proves 358.4.
    The shortcut lives only inside the criteria check: the text-only pull request still gets a check (so the
    "Acceptance criteria" gate still waits on it and fails when it fails), main's branch rule still requires
    "all tests" and "Acceptance criteria", and CODEOWNERS still names a code owner for every file, whose approving
    review GitHub requires before the merge."""
    record_property("proves", "358.4")
    rows, out = run_matrix(tmp_path, changed("AGENTS.md"))
    assert is_shortcut(rows), f"358.4: a text-only pull request did not get its one text-only check: {rows}\n{out}"
    code, out, _ = run_step(tmp_path, "gate", {"MATRIX": json.dumps(rows), "RESULT": "failure"})
    assert code != 0, "358.4: the 'Acceptance criteria' gate passed although the text-only check failed"
    sys.path.insert(0, ROOT)
    from dokima import manifest
    assert manifest.BRANCH_RULES["main"]["required_checks"] == ["all tests", "Acceptance criteria"], \
        f"358.4: main no longer requires both checks: {manifest.BRANCH_RULES['main']}"
    owners = [l.split() for l in open(os.path.join(ROOT, ".github", "CODEOWNERS")) if l.strip() and not l.startswith("#")]
    assert any(parts[0] == "*" and len(parts) > 1 for parts in owners), \
        f"358.4: CODEOWNERS no longer names a code owner for every file, so the owner's approval is not required: {owners}"


def test_when_github_cannot_list_the_changed_files_there_is_no_shortcut(record_property, tmp_path):
    """When GitHub cannot list the changed files, or lists none, there is no shortcut.

    Proves 358.5.
    The merge check asks GitHub for the changed files and GitHub refuses (HTTP 502): the check list must be today's
    failing "No approved plan found", never the shortcut, and the command must not crash. An empty file list gets no
    shortcut either. The stub logs every call, so the test also checks the file list was asked for at all."""
    record_property("proves", "358.5")
    rows, out = run_matrix(tmp_path, changed("AGENTS.md"), files_fail=True)
    asked = (tmp_path / "data.json.calls").read_text() if (tmp_path / "data.json.calls").exists() else ""
    assert f"pulls/{PR}/files" in asked, f"358.5: the merge check never asked GitHub for the pull request's files:\n{asked}"
    assert rows is not None and [r["name"] for r in rows] == [NO_ISSUE], \
        f"358.5: a refused file list did not fall back to the full way: {rows}\n{out}"
    rows, out = run_matrix(tmp_path, [])
    assert rows is not None and [r["name"] for r in rows] == [NO_ISSUE], \
        f"358.5: a pull request with no changed files took the text-only shortcut: {rows}\n{out}"

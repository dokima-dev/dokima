"""The old label approval and plan parser code is gone from the plan module.

Issue #760, story 1 of #739. The old label flow left code behind in dokima/plan.py: label approval (`LABEL`,
`approved_at`, `approved_version`), an unused `WORK_BRANCH` pattern, the checkbox plan parser (`parse`, `lines`,
`changes` and its patterns), the plain text writer `as_text` and the `plan issue` command. `fetch_issue` still made a
paginated events call and read the edit history on every card draw and scan. Card draws and scans read only the
issue's `current_body`, `url`, `number` and `title`, so those keys stay. GitHub is faked in every test: `plan.gh` is
replaced in process, and a fake `gh` on PATH stands in when the module runs as a command.
"""
import ast
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import plan  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = "o/r"
BODY = "My ask.\n\n- [ ] Goal: an old goal\n  - [ ] Done when: an old criterion\n"
URL = f"https://github.com/{REPO}/issues/40"
LABEL_APPROVAL = ("LABEL", "approved_at", "approved_version")
PARSER = ("parse", "lines", "changes", "CHECKBOX", "VERIFIED", "CRITERION_PREFIX", "GOAL_PREFIX", "NOT_CHECKED",
          "CARD_GOAL", "CARD_CRITERION", "CARD_VERIFIED", "BLOCK_CRITERION", "BLOCK_VERIFIED")
DELETED = LABEL_APPROVAL + ("WORK_BRANCH",) + PARSER + ("as_text",)


def fake_github(calls):
    """A fake GitHub that records every call and answers the issue read and its events."""
    def gh(*args):
        calls.append(args)
        text = " ".join(args)
        if "/events" in text:
            return "[]"
        if "graphql" in args:
            return json.dumps({"data": {"repository": {"issue": {
                "number": 40, "title": "t", "body": BODY, "url": URL, "userContentEdits": {"nodes": []}}}}})
        return json.dumps({"number": 40, "title": "t", "body": BODY, "url": f"https://api.github.com/repos/{REPO}/issues/40",
                           "html_url": URL})
    return gh


def test_fetching_an_issue_asks_github_only_for_its_text_and_link(record_property, monkeypatch, tmp_path):
    """A card or scan fetching an issue asks GitHub only for its text and link.

    Proves 760.1. Fakes GitHub, fetches issue #40 the way the card and the scan do, and checks GitHub got exactly one
    call, asking for no events and no edit history, and that the issue still carries the number, title, text and link
    the card and the scan read."""
    record_property("proves", "760.1")
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(plan, "gh", fake_github(calls))
    issue = plan.fetch_issue(REPO, 40)
    asked = [" ".join(c) for c in calls]
    assert not [a for a in asked if "/events" in a], f"760.1: fetching an issue still asks GitHub for its events: {asked}"
    assert not [a for a in asked if "userContentEdits" in a], \
        f"760.1: fetching an issue still asks GitHub for its edit history: {asked}"
    assert len(calls) == 1, f"760.1: fetching an issue should make one call to GitHub, it made {len(calls)}: {asked}"
    assert issue["current_body"] == BODY, "760.1: the fetched issue lost the text the card and the scan read"
    assert issue["url"] == URL, "760.1: the fetched issue lost the link the card and the scan read"
    assert issue["number"] == 40 and issue["title"] == "t", "760.1: the fetched issue lost its number or title"


def test_the_old_label_approval_code_is_deleted(record_property):
    """The old label approval code is gone from the plan module.

    Proves 760.2. Checks the plan module no longer defines the `work` label name or the two helpers that found when
    the label was added and what the issue said then."""
    record_property("proves", "760.2")
    left = [n for n in LABEL_APPROVAL if hasattr(plan, n)]
    assert not left, f"760.2: the old label approval code is still in dokima/plan.py: {', '.join(left)}"


def test_the_unused_work_branch_pattern_is_deleted(record_property):
    """The unused old work branch pattern is gone from the plan module.

    Proves 760.3. Checks the plan module no longer defines the pattern for old work branches, which nothing used."""
    record_property("proves", "760.3")
    assert not hasattr(plan, "WORK_BRANCH"), "760.3: the unused work branch pattern is still in dokima/plan.py"


def test_the_old_checkbox_plan_parser_is_deleted(record_property):
    """The old checkbox plan parser is gone from the plan module.

    Proves 760.4. Checks the plan module no longer defines the parser, its two helpers that compared plan versions,
    or the patterns it read checkbox and old card lines with."""
    record_property("proves", "760.4")
    left = [n for n in PARSER if hasattr(plan, n)]
    assert not left, f"760.4: the old checkbox plan parser is still in dokima/plan.py: {', '.join(left)}"


def test_the_old_plain_text_plan_writer_is_deleted(record_property):
    """The old plain text plan writer is gone from the plan module.

    Proves 760.5. Checks the plan module no longer defines the function that wrote a plan as plain text."""
    record_property("proves", "760.5")
    assert not hasattr(plan, "as_text"), "760.5: the old plain text plan writer is still in dokima/plan.py"


def test_the_old_command_that_prints_an_issues_plan_is_deleted(record_property, tmp_path):
    """The old command that printed an issue's plan prints nothing and asks GitHub nothing.

    Proves 760.6. Runs `python3 -m dokima.plan issue 40` from the repo root, as a workflow would, with a fake `gh`
    first on PATH that logs every call and answers like GitHub, then checks nothing was asked and no plan printed."""
    record_property("proves", "760.6")
    log = tmp_path / "gh.log"
    fake = tmp_path / "bin" / "gh"
    fake.parent.mkdir()
    answer = json.dumps({"data": {"repository": {"issue": {"number": 40, "title": "t", "body": BODY, "url": URL,
                                                           "userContentEdits": {"nodes": []}}}}})
    fake.write_text("#!/usr/bin/env python3\nimport sys\n"
                    f"open({str(log)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
                    f"print('[]' if any('/events' in a for a in sys.argv) else {answer!r})\n")
    fake.chmod(0o755)
    env = dict(os.environ, PATH=f"{fake.parent}{os.pathsep}{os.environ['PATH']}", GITHUB_REPOSITORY=REPO,
               GITHUB_REPOSITORY_OWNER="o")
    run = subprocess.run([sys.executable, "-m", "dokima.plan", "issue", "40"], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=30)
    asked = log.read_text() if log.exists() else ""
    assert "Issue #40" not in run.stdout, f"760.6: the old command still prints the issue's plan:\n{run.stdout}"
    assert not asked, f"760.6: the old command still asks GitHub for the issue:\n{asked}"


def test_no_test_reads_the_deleted_plan_code(record_property):
    """No test still reads the plan code this issue deletes.

    Proves 760.8. The old names must be gone from the plan module first, since a test reading a name that still
    exists cannot be told apart from one that is fine. Then it reads every test file's code, this one aside, and
    names each place that still uses one of those names from the plan module, by file and line."""
    record_property("proves", "760.8")
    still = [n for n in DELETED if hasattr(plan, n)]
    assert not still, f"760.8: the old plan code is not deleted yet, so its tests cannot be checked: {', '.join(still)}"
    here, left = os.path.basename(__file__), []
    for name in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        if not name.endswith(".py") or name == here:
            continue
        tree = ast.parse(open(os.path.join(ROOT, "tests", name), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in DELETED and \
                    isinstance(node.value, ast.Name) and node.value.id == "plan":
                left.append(f"tests/{name} line {node.lineno}: plan.{node.attr}")
            if isinstance(node, ast.ImportFrom) and node.module == "dokima.plan":
                left += [f"tests/{name} line {node.lineno}: imports {a.name}" for a in node.names if a.name in DELETED]
    assert not left, "760.8: these tests still read the deleted plan code:\n" + "\n".join(left)

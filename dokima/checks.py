"""Turn the criteria of an issue's approved plan into GitHub checks, and annotate the tests they ran.

    python3 -m dokima.checks matrix          # print the check list for this PR, or the PR queued in the merge queue
    python3 -m dokima.checks annotate r.xml  # print one annotation per test in a JUnit report

The plan is the newest one the planner handed back, once the reviewer approved it, read from the bot's own record
comments; each criterion's check runs exactly the tests that plan lists for it. A pull request with no approved plan that
changes only Markdown files outside dokima/roles/, tests/ and .github/ gets one passing "Text only" check instead.
A manual fix Dokima's app opens with no linked issue gets one "Manual fix" check that runs all tests.

A test proves a criterion by calling record_property("proves", "<issue>.<n>"),
where n counts the issue's criteria from 1, top to bottom.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from dokima import agent, plan

PROVES = re.compile(r"""record_property\(\s*["']proves["']\s*,\s*["']([\d.]+)["']\s*\)""")
TEST_DEF = re.compile(r"^def (test_\w+)\(")
QUEUE_REF = re.compile(r"^(?:refs/heads/)?gh-readonly-queue/.+/pr-(\d+)-[0-9a-f]+$")
TEXT_ONLY = [{"id": "text-only", "name": "Text only: no plan needed", "tests": ""}]
NOT_TEXT = ("dokima/roles/", "tests/", ".github/")
MANUAL_FIX = [{"id": "manual-fix", "name": "Manual fix: all tests pass", "tests": "tests"}]


def find_tests(paths):
    """Map each criterion key like '29.1' to the tests that prove it, as 'path::test'."""
    found = {}
    for path in sorted(paths):
        current = None
        with open(path) as f:
            for line in f:
                name = TEST_DEF.match(line)
                if name:
                    current = name.group(1)
                for key in PROVES.findall(line):
                    if current:
                        found.setdefault(key, []).append(f"{path}::{current}")
    return found


def check_name(key, text, limit=60):
    """The check's name on GitHub: '29.1 · <criterion, shortened>'."""
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return f"{key} · {text}"


def no_plan(name):
    """One check with no tests, so it can only fail, saying why."""
    return [{"id": "none", "name": name, "tests": ""}]


def build_matrix(number, recs, author=None):
    """One check per criterion of the approved plan (acceptance criteria, then non-functional), each running exactly
    the plan's tests for it; one failing "No approved plan found" check when there is no issue or no approved plan.
    A pull request Dokima's app opened with no linked issue is a manual fix: one check that runs all tests."""
    if not number:
        if author in (agent.BOT, f"{agent.BOT}[bot]"):
            return MANUAL_FIX
        return no_plan("No approved plan found: no issue linked")
    if not agent.approved(recs):
        return no_plan(f"No approved plan found for issue #{number}")
    h = agent.latest(recs, "planner")["handback"]
    criteria = [c for k in ("acceptance_criteria", "non_functional") for c in h.get(k) or []]
    tests = h.get("tests") or {}
    rows = []
    for k, c in enumerate(criteria, 1):
        key = f"{number}.{k}"
        rows.append({"id": key, "name": check_name(key, c["text"]), "tests": " ".join(tests.get(key, []))})
    return rows or no_plan(f"No approved plan found for issue #{number}")


def is_text(path):
    """True for a Markdown file outside dokima/roles/, tests/ and .github/."""
    return bool(path) and path.lower().endswith(".md") and not path.startswith(NOT_TEXT)


def text_only(repo, number):
    """True when every file the pull request changes, and its old name, is text.

    Any failure to list the files, or an empty list, is False: no shortcut."""
    try:
        files = [f for p in agent.pages(agent.gh("api", f"repos/{repo}/pulls/{number}/files?per_page=100", "--paginate"))
                 for f in p]
    except (subprocess.CalledProcessError, ValueError, TypeError) as e:
        print(f"Could not list the changed files of PR #{number}, so no text-only shortcut: "
              f"{agent.gh_reason(e) if isinstance(e, subprocess.CalledProcessError) else e}", file=sys.stderr)
        return False
    if not files:
        return False
    return all(isinstance(f, dict) and is_text(f.get("filename")) and
               ("previous_filename" not in f or is_text(f["previous_filename"])) for f in files)


def annotations(junit_xml, repo, sha, criterion):
    """One annotation per test that ran, with a permanent link to the test's first line at this commit."""
    lines = []
    for tc in ET.fromstring(junit_xml).iter("testcase"):
        failed = any(child.tag in ("failure", "error") for child in tc)
        kind, verdict = ("error", "failed") if failed else ("notice", "passed")
        path, line = tc.get("file"), int(tc.get("line")) + 1
        link = f"https://github.com/{repo}/blob/{sha}/{path}#L{line}"
        lines.append(f"::{kind} file={path},line={line},title={criterion} {verdict}::"
                     f"{tc.get('name')} {verdict} · {path} line {line} · view the test: {link}")
    return lines


def event_pr(repo, event):
    """This event's pull request; in the merge queue, the one its branch names."""
    if "merge_group" not in event:
        return event["pull_request"]
    ref = event["merge_group"]["head_ref"]
    m = QUEUE_REF.match(ref)
    if not m:
        sys.exit(f"Not a merge queue branch: {ref}")
    pr = json.loads(agent.gh("api", f"repos/{repo}/pulls/{m.group(1)}"))
    return {"number": pr["number"], "head": {"ref": pr["head"]["ref"]}, "body": pr.get("body"), "user": pr.get("user")}


def main(argv):
    repo = os.environ["GITHUB_REPOSITORY"]
    if argv[1] == "matrix":
        pr = event_pr(repo, json.load(open(os.environ["GITHUB_EVENT_PATH"])))
        number = agent.issue_of_pr(pr["head"]["ref"], pr.get("body")) or plan.pr_issue_number(repo, pr["number"])
        recs = agent.records(agent.conversation(repo, number)[1]) if number else []
        rows = build_matrix(number, recs, (pr.get("user") or {}).get("login"))
        if rows[0]["id"] == "none" and text_only(repo, pr["number"]):
            rows = TEXT_ONLY
        print("matrix=" + json.dumps(rows))
    elif argv[1] == "annotate":
        for line in annotations(open(argv[2]).read(), repo, os.environ["HEAD_SHA"], os.environ["ID"]):
            print(line)


if __name__ == "__main__":
    main(sys.argv)

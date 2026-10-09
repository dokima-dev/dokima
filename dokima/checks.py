"""Turn the criteria of an issue's approved plan into GitHub checks, and annotate the tests they ran.

    python3 -m dokima.checks matrix          # print the check list for this PR
    python3 -m dokima.checks annotate r.xml  # print one annotation per test in a JUnit report

The plan is the newest one the planner handed back, once the reviewer approved it, read from the bot's own record
comments; each criterion's check runs exactly the tests that plan lists for it.

A test proves a criterion by calling record_property("proves", "<issue>.<n>"),
where n counts the issue's criteria from 1, top to bottom.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from dokima import agent, plan

PROVES = re.compile(r"""record_property\(\s*["']proves["']\s*,\s*["']([\d.]+)["']\s*\)""")
TEST_DEF = re.compile(r"^def (test_\w+)\(")


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


def build_matrix(number, recs):
    """One check per criterion of the approved plan (acceptance criteria, then non-functional), each running exactly
    the plan's tests for it; one failing "No approved plan found" check when there is no issue or no approved plan."""
    if not number:
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


def main(argv):
    repo = os.environ["GITHUB_REPOSITORY"]
    if argv[1] == "matrix":
        pr = json.load(open(os.environ["GITHUB_EVENT_PATH"]))["pull_request"]
        number = agent.issue_of_pr(pr["head"]["ref"], pr.get("body")) or plan.pr_issue_number(repo, pr["number"])
        recs = agent.records(agent.conversation(repo, number)[1]) if number else []
        print("matrix=" + json.dumps(build_matrix(number, recs)))
    elif argv[1] == "annotate":
        for line in annotations(open(argv[2]).read(), repo, os.environ["HEAD_SHA"], os.environ["ID"]):
            print(line)


if __name__ == "__main__":
    main(sys.argv)

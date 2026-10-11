"""Queued pull requests are retested on the latest main, with every criterion's check, before they merge.

GitHub's merge queue tests each pull request on top of the latest main in a temporary commit and sends the
`merge_group` event, not `pull_request`. These tests prove the two required workflows (full-suite.yml and
acceptance-criteria.yml) run on that event, that `python3 -m dokima.checks matrix` finds the pull request's issue from the
queue's branch (refs/heads/gh-readonly-queue/<base>/pr-<N>-<sha>) and lists the same checks as on the pull request, and
that pull request checks are unchanged.

`dokima.checks matrix` runs for real, as a subprocess, against a fake `gh` put first on PATH. The fake knows a few pull
requests and issues (see PRS and PLANS) and answers:
  - `gh pr view N [--json ...] [-q/--jq .path]`: number, headRefName, body, comments, reviews, closingIssuesReferences;
  - `gh pr list ...`: [];
  - `gh issue view N --json ...`: the issue with its bot record comments (an approved plan);
  - `gh api repos/O/R/pulls/N`: number, head.ref, body; `gh api repos/O/R/pulls/N/comments`: [];
  - `gh api graphql ...` with the pull request number in any -F/-f field: repository.pullRequest with number,
    headRefName, body and closingIssuesReferences.nodes.
Anything else exits 1 saying the fake does not know the call.

The workflows' commit expressions are checked by evaluating them: each must be `${{ a || b ... }}` where every part is
`github.sha` or a `github.event...` path; the first non-empty part wins, as on GitHub.
"""
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
BOT = "dokima-runtime"
MARK = "<!-- dokima-record -->"
PR_SHA = "1" * 40
QUEUE_SHA = "2" * 40
BASE_SHA = "3" * 40

# Pull requests the fake gh knows: number -> branch, body, and the issue GitHub says it closes.
PRS = {
    12: {"headRefName": "try/issue-191", "body": "Builds the plan.", "closes": None},
    34: {"headRefName": "feature/x", "body": "Closes #77", "closes": None},
    56: {"headRefName": "fix-things", "body": "", "closes": 88},
    90: {"headRefName": "misc", "body": "No link here.", "closes": None},
}

# Issues with an approved plan: number -> (acceptance criteria, non-functional, tests per criterion).
PLANS = {
    191: (["First promise", "Second promise"], ["Stays safe"],
          {"191.1": ["tests/test_a.py::test_one"], "191.2": ["tests/test_a.py::test_two", "tests/test_b.py::test_x"],
           "191.3": ["tests/test_c.py::test_safe"]}),
    77: (["Only promise of seventy-seven"], [], {"77.1": ["tests/test_s.py::test_77"]}),
    88: (["Eighty-eight one", "Eighty-eight two"], [], {"88.1": ["tests/test_e.py::test_1"]}),
}

FAKE_GH = r'''#!/usr/bin/env python3
"""A fake GitHub CLI for tests/test_merge_queue.py."""
import json, os, re, sys

state = json.load(open(os.environ["FAKE_GH_STATE"]))
prs, issues = state["prs"], state["issues"]
args = sys.argv[1:]
jq = None
for flag in ("-q", "--jq"):
    if flag in args:
        jq = args[args.index(flag) + 1]


def pr_obj(n):
    p = prs[str(n)]
    return {"number": int(n), "headRefName": p["headRefName"], "body": p["body"], "comments": [], "reviews": [],
            "baseRefName": "main", "state": "OPEN",
            "closingIssuesReferences": [{"number": p["closes"]}] if p["closes"] else []}


def out(obj):
    if jq is not None:
        if not re.fullmatch(r"(\.\w+)+", jq):
            sys.stderr.write(f"fake gh: unsupported jq {jq}\n")
            sys.exit(1)
        for part in jq.split(".")[1:]:
            obj = obj.get(part) if isinstance(obj, dict) else None
        print(obj if isinstance(obj, str) else ("" if obj is None else json.dumps(obj)))
    else:
        print(json.dumps(obj))
    sys.exit(0)


def unknown():
    sys.stderr.write("fake gh: unknown call: " + " ".join(args) + "\n")
    sys.exit(1)


if args[:2] == ["pr", "view"]:
    n = re.sub(r"\D", "", args[2].split("/")[-1])
    if n not in prs:
        unknown()
    out(pr_obj(n))
if args[:2] == ["pr", "list"]:
    out([])
if args[:2] == ["issue", "view"]:
    n = args[2]
    out({"number": int(n), "title": "t", "body": "", "comments": issues.get(n, [])})
if args[:2] == ["api", "graphql"]:
    fields = [args[i + 1] for i, a in enumerate(args) if a in ("-F", "-f", "--field", "--raw-field")]
    nums = [v.split("=", 1)[1] for v in fields if "=" in v and v.split("=", 1)[1] in prs]
    if not nums:
        unknown()
    p = pr_obj(nums[0])
    p["closingIssuesReferences"] = {"nodes": p["closingIssuesReferences"]}
    out({"data": {"repository": {"pullRequest": p}}})
if len(args) >= 2 and args[0] == "api":
    m = re.fullmatch(r"/?repos/[^/]+/[^/]+/pulls/(\d+)(/comments)?", args[1].split("?")[0])
    if m and m.group(2):
        out([])
    if m and m.group(1) in prs:
        p = prs[m.group(1)]
        out({"number": int(m.group(1)), "head": {"ref": p["headRefName"], "sha": "1" * 40}, "body": p["body"]})
unknown()
'''


def record(role, handback, when, stage=None):
    """One bot record comment, as Dokima posts it."""
    rec = {"role": role, "check": {"passed": True}, "handback": handback}
    if stage:
        rec["stage"] = stage
    body = f"{MARK}\nA record.\n\n```json\n{json.dumps(rec)}\n```\n"
    return {"author": {"login": BOT}, "body": body, "createdAt": when}


def issue_comments(number):
    """The bot records of an issue with an approved plan."""
    acs, nfs, tests = PLANS[number]
    plan = {"kind": "user_story", "acceptance_criteria": [{"text": t, "source": "x"} for t in acs],
            "non_functional": [{"text": t, "why": "w"} for t in nfs], "tests": tests}
    return [record("planner", plan, "2026-01-01T00:00:00Z"),
            record("reviewer", {"verdict": "approve"}, "2026-01-02T00:00:00Z", stage="plan")]


def expected(number):
    """The check list the approved plan of an issue gives: one row per criterion, with exactly its tests."""
    acs, nfs, tests = PLANS[number]
    rows = []
    for k, text in enumerate(acs + nfs, 1):
        key = f"{number}.{k}"
        rows.append({"id": key, "name": f"{key} · {text}", "tests": " ".join(tests.get(key, []))})
    return rows


@pytest.fixture
def run_matrix(tmp_path):
    """Run `python3 -m dokima.checks matrix` for an event payload against the fake gh; return (exit code, rows, err)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(0o755)
    st = tmp_path / "state.json"
    st.write_text(json.dumps({"prs": {str(k): v for k, v in PRS.items()},
                              "issues": {str(n): issue_comments(n) for n in PLANS}}))

    def run(event):
        ev = tmp_path / "event.json"
        ev.write_text(json.dumps(event))
        env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "FAKE_GH_STATE": str(st),
               "GITHUB_REPOSITORY": REPO, "GITHUB_EVENT_PATH": str(ev), "GH_TOKEN": "x", "DOKIMA_BOT": BOT,
               "PYTHONPATH": os.path.abspath(ROOT)}
        p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=60)
        lines = [line for line in p.stdout.splitlines() if line.startswith("matrix=")]
        rows = json.loads(lines[-1][len("matrix="):]) if p.returncode == 0 and lines else None
        return p.returncode, rows, p.stderr[-2000:]
    return run


def pr_event(n):
    """The pull_request_target payload acceptance-criteria.yml gets for pull request n."""
    p = PRS[n]
    return {"action": "synchronize", "number": n,
            "pull_request": {"number": n, "head": {"ref": p["headRefName"], "sha": PR_SHA}, "body": p["body"],
                             "base": {"ref": "main", "sha": BASE_SHA}}}


def queue_event(n, base="main"):
    """The merge_group payload GitHub sends when pull request n is queued on top of the latest base branch."""
    return {"action": "checks_requested",
            "merge_group": {"head_sha": QUEUE_SHA, "head_ref": f"refs/heads/gh-readonly-queue/{base}/pr-{n}-{BASE_SHA}",
                            "base_sha": BASE_SHA, "base_ref": f"refs/heads/{base}",
                            "head_commit": {"id": QUEUE_SHA, "message": f"Merge pull request #{n}"}}}


def workflow(name):
    """The lines of a workflow file."""
    return open(os.path.join(ROOT, ".github", "workflows", name)).read().splitlines()


def triggers(lines):
    """The event names under a workflow's top-level `on:`, in block or inline form."""
    for i, line in enumerate(lines):
        m = re.match(r"""^["']?on["']?:\s*(.*)$""", line)
        if not m:
            continue
        inline = m.group(1).split("#")[0].strip()
        if inline:
            return {x.strip() for x in inline.strip("[]").split(",") if x.strip()}
        found = set()
        for nxt in lines[i + 1:]:
            if nxt.strip() and not nxt.startswith((" ", "\t")):
                break
            k = re.match(r"^ {1,4}([\w-]+):", nxt)
            if k and len(nxt) - len(nxt.lstrip()) == len(lines[i + 1]) - len(lines[i + 1].lstrip()):
                found.add(k.group(1))
        return found
    return set()


def evaluate(expr, event, sha):
    """Evaluate a `${{ a || b }}` commit expression the way GitHub would.

    Returns None when the expression is not understood."""
    m = re.fullmatch(r"\$\{\{\s*(.*?)\s*\}\}", expr.strip().strip("'\""))
    if not m:
        return None
    for part in (x.strip() for x in m.group(1).split("||")):
        if part == "github.sha":
            value = sha
        elif re.fullmatch(r"github\.event(\.\w+)+", part):
            value = event
            for key in part.split(".")[2:]:
                value = value.get(key) if isinstance(value, dict) else None
        else:
            return None
        if value:
            return value
    return ""


def commit_expressions():
    """The `ref:` of the checkout of the pull request's tests and the HEAD_SHA its annotations link to."""
    lines = workflow("acceptance-criteria.yml")
    refs, heads = [], []
    for i, line in enumerate(lines):
        if re.match(r"^\s+ref:\s", line):
            block = lines[max(0, i - 3):i + 4]
            if any(re.match(r"^\s+path:\s*pr\s*$", b) for b in block):
                refs.append(line.split(":", 1)[1].strip())
        if re.match(r"^\s+HEAD_SHA:\s", line):
            heads.append(line.split(":", 1)[1].strip())
    return refs, heads


def suite_refs():
    """The `ref:` of every checkout in full-suite.yml, the commit the all tests check runs."""
    return [line.split(":", 1)[1].strip() for line in workflow("full-suite.yml") if re.match(r"^\s+ref:\s", line)]


def test_both_required_workflows_run_in_the_merge_queue_on_the_queued_commit(record_property):
    """Both required workflows run in the merge queue, testing the queued commit.

    Proves 191.1. Reads the `on:` of full-suite.yml and acceptance-criteria.yml and checks each lists merge_group; then evaluates the commit
    the criteria check checks out and the commit its annotations link to for a merge_group event, and checks both are
    the queue's commit (the pull request on top of the latest main), not empty and not main's; and does the same for
    the commit the all tests check checks out."""
    record_property("proves", "191.1")
    for name in ("full-suite.yml", "acceptance-criteria.yml"):
        assert "merge_group" in triggers(workflow(name)), \
            f"191.1: {name} does not run on the merge queue's merge_group event; its `on:` is {sorted(triggers(workflow(name)))}"
    for expr in suite_refs():
        got = evaluate(expr, queue_event(12), QUEUE_SHA)
        assert got == QUEUE_SHA, \
            f"191.1: in the merge queue the all tests checkout `{expr}` gives {got!r}, not the queued commit {QUEUE_SHA}"
    refs, heads = commit_expressions()
    assert refs and heads, "191.1: acceptance-criteria.yml has no `ref:` on the checkout with `path: pr` or no HEAD_SHA"
    for what, exprs in (("checkout ref", refs), ("HEAD_SHA", heads)):
        for expr in exprs:
            got = evaluate(expr, queue_event(12), QUEUE_SHA)
            assert got is not None, f"191.1: acceptance-criteria.yml {what} `{expr}` is not `${{{{ a || b }}}}` of github.sha / github.event paths"
            assert got == QUEUE_SHA, \
                f"191.1: in the merge queue the Acceptance criteria {what} `{expr}` gives {got!r}, not the queued commit {QUEUE_SHA}"


@pytest.mark.parametrize("pr, issue", [(12, 191), (34, 77), (56, 88)],
                         ids=["linked-by-branch", "linked-by-closes-in-body", "linked-by-github-closing-reference"])
def test_queued_pr_gets_the_same_checks_as_on_the_pr(record_property, run_matrix, pr, issue):
    """In the queue, the criteria checks find the PR's issue and list its same checks.

    Proves 191.2. Runs `dokima.checks matrix` for a merge_group event whose branch names the pull request, for three pull requests
    linked to three different issues (by try/issue-N branch, by 'Closes #N' in the body, and by GitHub's closing
    reference only), and checks the list is exactly the one-check-per-criterion list of that issue's approved plan,
    and the same list the pull request event gives."""
    record_property("proves", "191.2")
    code, on_pr, err = run_matrix(pr_event(pr))
    assert code == 0, f"191.2: on pull request #{pr}, `dokima.checks matrix` failed:\n{err}"
    code, in_queue, err = run_matrix(queue_event(pr))
    assert code == 0, f"191.2: in the merge queue (pull request #{pr}), `dokima.checks matrix` failed:\n{err}"
    assert in_queue == expected(issue), \
        f"191.2: queued pull request #{pr} should list the checks of issue #{issue}'s plan, got {in_queue}"
    assert in_queue == on_pr, f"191.2: queued pull request #{pr} lists {in_queue}, but on the PR it lists {on_pr}"


def test_queue_branch_on_another_base_still_finds_the_pr(record_property, run_matrix):
    """A queue on a base branch with a slash still finds the PR's issue.

    Proves 191.2. Runs `dokima.checks matrix` for a merge_group event on gh-readonly-queue/release/2.0/pr-34-<sha> and checks it
    lists issue #77's checks."""
    record_property("proves", "191.2")
    code, rows, err = run_matrix(queue_event(34, base="release/2.0"))
    assert code == 0, f"191.2: in the merge queue on release/2.0, `dokima.checks matrix` failed:\n{err}"
    assert rows == expected(77), f"191.2: queued pull request #34 on release/2.0 should list issue #77's checks, got {rows}"


def test_queued_pr_with_no_linked_issue_fails_the_gate_with_the_same_reason(record_property, run_matrix):
    """A queued PR with no linked issue fails the gate as on the PR.

    Proves 191.3. Runs `dokima.checks matrix` for a pull request with no issue link (no try/issue-N branch, no 'Closes #N', no
    closing reference), on the PR and in the queue, and checks both give the one failing check 'No approved plan found:
    no issue linked' with no tests; then checks acceptance-criteria.yml still fails a check with no tests and makes the gate
    need every check to pass."""
    record_property("proves", "191.3")
    reason = [{"id": "none", "name": "No approved plan found: no issue linked", "tests": ""}]
    code, on_pr, err = run_matrix(pr_event(90))
    assert code == 0, f"191.3: on pull request #90, `dokima.checks matrix` failed:\n{err}"
    code, in_queue, err = run_matrix(queue_event(90))
    assert code == 0, f"191.3: in the merge queue (pull request #90), `dokima.checks matrix` failed:\n{err}"
    assert on_pr == reason, f"191.3: an unlinked pull request should list {reason}, got {on_pr}"
    assert in_queue == reason, f"191.3: an unlinked queued pull request should list {reason}, got {in_queue}"
    text = "\n".join(workflow("acceptance-criteria.yml"))
    assert re.search(r'if \[ -z "\$TESTS" \]; then .*exit 1; fi', text), \
        "191.3: acceptance-criteria.yml no longer fails a check that has no tests"
    assert "name: Acceptance criteria" in text and 'test "$RESULT" = "success"' in text, \
        "191.3: the 'Acceptance criteria' gate no longer needs every check to pass"


def test_pull_request_checks_behave_exactly_as_before(record_property, run_matrix):
    """Pull request checks are unchanged: same triggers, names, list and commit.

    Proves 191.4. Checks the triggers are exactly main's plus merge_group (full-suite.yml: pull_request_target, push to main,
    merge_group, as #263 left it; acceptance-criteria.yml: pull_request_target, merge_group), so nothing was dropped, swapped or
    added beyond the queue; that the required check names 'all tests' and 'Acceptance criteria' are unchanged; that
    `dokima.checks matrix` on a pull request lists its issue's plan exactly; that on a pull request the criteria
    check out and annotate the pull request's head commit, not main's; and that the all tests check still checks out
    the pull request's head on a pull request and main's commit on a push to main."""
    record_property("proves", "191.4")
    suite, dw = workflow("full-suite.yml"), workflow("acceptance-criteria.yml")
    assert triggers(suite) == {"pull_request_target", "push", "merge_group"}, \
        f"191.4: full-suite.yml should run on pull_request_target, push and merge_group only, but runs on {sorted(triggers(suite))}"
    assert "branches: [main]" in [x.strip() for x in suite], "191.4: full-suite.yml no longer runs on pushes to main"
    assert triggers(dw) == {"pull_request_target", "merge_group"}, \
        f"191.4: acceptance-criteria.yml should run on pull_request_target and merge_group only, but runs on {sorted(triggers(dw))}"
    assert "name: all tests" in [x.strip() for x in suite], "191.4: the 'all tests' check was renamed"
    assert "name: Acceptance criteria" in [x.strip() for x in dw], "191.4: the 'Acceptance criteria' check was renamed"
    code, rows, err = run_matrix(pr_event(12))
    assert code == 0, f"191.4: on pull request #12, `dokima.checks matrix` failed:\n{err}"
    assert rows == expected(191), f"191.4: pull request #12 should list issue #191's checks, got {rows}"
    refs, heads = commit_expressions()
    assert refs and heads, "191.4: acceptance-criteria.yml has no `ref:` on the checkout with `path: pr` or no HEAD_SHA"
    for expr in refs + heads:
        got = evaluate(expr, pr_event(12), BASE_SHA)
        assert got == PR_SHA, f"191.4: on a pull request `{expr}` gives {got!r}, not the pull request's head {PR_SHA}"
    assert suite_refs(), "191.4: full-suite.yml no longer names the commit it checks out, so it tests main's own copy"
    for expr in suite_refs():
        got = evaluate(expr, pr_event(12), BASE_SHA)
        assert got == PR_SHA, \
            f"191.4: on a pull request the all tests checkout `{expr}` gives {got!r}, not the pull request's head {PR_SHA}"
        got = evaluate(expr, {"ref": "refs/heads/main"}, BASE_SHA)
        assert got == BASE_SHA, f"191.4: on a push to main the all tests checkout `{expr}` gives {got!r}, not main's {BASE_SHA}"

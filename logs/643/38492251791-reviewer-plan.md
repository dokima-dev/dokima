# reviewer (plan) for #643

Run: https://github.com/dokima-dev/dokima/actions/runs/38492251791

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #643: A manual fix merges once all tests pass and the owner approves
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A manual fix opened by Dokima's app gets a merge check that runs all tests, instead of always failing.
> 
> **Plan**
> 
> **User story:** A manual fix Dokima's app opens merges once all tests pass and the owner approves, with nothing overridden.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A manual fix opened by Dokima's app gets one acceptance check that runs all tests and passes when they pass.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-643/tests/test_manual_fix_check.py#L96"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A manual fix by Dokima's app gets a check that runs all tests and passes.*
>   - Edge cases: The manual fix waits in the merge queue and gets the same check there.
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/ma

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_manual_fix_check.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps(d,indent=1)[:4000])"; git show --stat HEAD
```

> """A manual fix by Dokima's app gets a merge check that runs all tests (#643).
> 
> `.github/workflows/fix.yml` (#589) opens an agent's manual fix as Dokima's app, with no linked issue and so no plan.
> The required Acceptance criteria check then listed one failing "No approved plan found: no issue linked" row, so such a
> fix could never merge. These tests run the real command the Acceptance criteria workflow runs,
> `python3 -m dokima.checks matrix`, from the repo root with GitHub faked by a stub `gh` (the pull request changes
> `dokima/checks.py`, so the text-only shortcut never applies), then run that workflow's own "Run this criterion's tests"
> step with the row it got and a fake `pytest` on PATH that logs its arguments and passes or fails on demand.
> Nothing here touches the network.
> """
> import json
> import os
> import subprocess
> import sys
> 
> from test_text_only import ROOT, STUB_GH, step_script
> 
> APP = "dokima-runtime[bot]"
> OWNER = "RezaSoleymanifar"
> NO_ISSUE = "No approved plan found: no issue linked"
> PR = 901
> 
> QUEUE_GH = '''#!/usr/bin/env python3
> """A stand-in for the GitHub CLI that answers the queued pull request, else behaves like the text-only stub."""
> import json, os, subprocess, sys
> data = json.load(open(os.environ["STUB_DATA"]))
> a = sys.argv[1:]
> if a[:2] == ["api", "repos/o/r/pulls/%d" % data["pr"]]:
>     print(json.dumps({"number": data["pr"], "head": {"ref": "fix/typo"}, "body": data["body"],
>                       "user": {"login": data["author"]}}))
>     sys.exit(0)
> sys.exit(su

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def build_matrix" -A80 dokima/checks.py; cat .github/workflows/fix.yml | head -80
```

> 57:def build_matrix(number, recs):
> 58-    """One check per criterion of the approved plan (acceptance criteria, then non-functional), each running exactly
> 59-    the plan's tests for it; one failing "No approved plan found" check when there is no issue or no approved plan."""
> 60-    if not number:
> 61-        return no_plan("No approved plan found: no issue linked")
> 62-    if not agent.approved(recs):
> 63-        return no_plan(f"No approved plan found for issue #{number}")
> 64-    h = agent.latest(recs, "planner")["handback"]
> 65-    criteria = [c for k in ("acceptance_criteria", "non_functional") for c in h.get(k) or []]
> 66-    tests = h.get("tests") or {}
> 67-    rows = []
> 68-    for k, c in enumerate(criteria, 1):
> 69-        key = f"{number}.{k}"
> 70-        rows.append({"id": key, "name": check_name(key, c["text"]), "tests": " ".join(tests.get(key, []))})
> 71-    return rows or no_plan(f"No approved plan found for issue #{number}")
> 72-
> 73-
> 74-def is_text(path):
> 75-    """True for a Markdown file outside dokima/roles/, tests/ and .github/."""
> 76-    return bool(path) and path.lower().endswith(".md") and not path.startswith(NOT_TEXT)
> 77-
> 78-
> 79-def text_only(repo, number):
> 80-    """True when every file the pull request changes, and its old name, is text.
> 81-
> 82-    Any failure to list the files, or an empty list, is False: no shortcut."""
> 83-    try:
> 84-        files = [f for p in agent.pages(agent.gh("api", f"repos/{repo}/pulls/{number}/files?per_page=100", "--paginate"))
> 85-  

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "DOKIMA_BOT" -r dokima | head; grep -n "Run this criterion's tests" -A25 .github/workflows/*.yml | head -50; grep -n "TEXT_ONLY\s*=" -A3 dokima/checks.py; python3 -m pytest -q tests/test_manual_fix_check.py 2>&1 | tail -30
```

> dokima/agent.py:37:BOT = os.environ.get("DOKIMA_BOT", "dokima-runtime")
> .github/workflows/acceptance-criteria.yml:54:      - name: Run this criterion's tests
> .github/workflows/acceptance-criteria.yml-55-        working-directory: pr
> .github/workflows/acceptance-criteria.yml-56-        env:
> .github/workflows/acceptance-criteria.yml-57-          TESTS: ${{ matrix.tests }}
> .github/workflows/acceptance-criteria.yml-58-          ID: ${{ matrix.id }}
> .github/workflows/acceptance-criteria.yml-59-        run: |
> .github/workflows/acceptance-criteria.yml-60-          if [ "$ID" = "text-only" ] && [ -z "$TESTS" ]; then echo "::notice title=Text only::Only text files changed: no plan or tests needed."; exit 0; fi
> .github/workflows/acceptance-criteria.yml-61-          if [ -z "$TESTS" ]; then echo "::error title=$ID has no test::No test verifies this criterion yet."; exit 1; fi
> .github/workflows/acceptance-criteria.yml-62-          pytest -rA -p no:cacheprovider -o junit_family=xunit1 --junitxml=r.xml $TESTS
> .github/workflows/acceptance-criteria.yml-63-      - name: Annotate the tests that ran
> .github/workflows/acceptance-criteria.yml-64-        if: always() && matrix.tests != ''
> .github/workflows/acceptance-criteria.yml-65-        env:
> .github/workflows/acceptance-criteria.yml-66-          ID: ${{ matrix.id }}
> .github/workflows/acceptance-criteria.yml-67-          HEAD_SHA: ${{ github.event.pull_request.head.sha || github.event.merge_group.head_sha }}
> .github/workflows/acceptance-criteri

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 70,100p .github/workflows/acceptance-criteria.yml; grep -n "def issue_of_pr" -A15 dokima/agent.py
```

> gate:
>     name: Acceptance criteria
>     needs: [list, check]
>     if: always() && !github.event.pull_request.draft
>     runs-on: ubuntu-24.04
>     steps:
>       - env:
>           MATRIX: ${{ needs.list.outputs.matrix }}
>           RESULT: ${{ needs.check.result }}
>         run: |
>           if [ -z "$MATRIX" ] || [ "$MATRIX" = "[]" ]; then
>             echo "::error title=No acceptance criteria::Link an issue with acceptance criteria (Closes #N) to this pull request."
>             exit 1
>           fi
>           test "$RESULT" = "success"
> 1676:def issue_of_pr(head, body):
> 1677-    """The issue a pull request was built for: from its branch, else its closing line.
> 1678-
> 1679-    The branch is work/issue-N or try/issue-N; the closing line is 'Closes' with the issue's full address or the old
> 1680-    'Closes #N'."""
> 1681-    m = re.match(r"(?:work|try)/issue-(\d+)$", head or "") or re.search(
> 1682-        r"(?i)\b(?:closes|fixes|resolves) (?:#|https://github\.com/[\w.-]+/[\w.-]+/issues/)(\d+)\b", body or "")
> 1683-    return m.group(1) if m else None
> 1684-
> 1685-
> 1686-def autopilot_of(body):
> 1687-    """"start" or "stop" when a comment's first line begins `/autopilot start` or `/autopilot stop`; otherwise None."""
> 1688-    first = (body or "").strip().splitlines()[0].split() if (body or "").strip() else []
> 1689-    if len(first) >= 2 and first[0].lower() == "/autopilot" and first[1].lower() in ("start", "stop"):
> 1690-        return first[1].lower()
> 1691-    return None

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner planned a merge check for manual fixes opened by Dokima's app.", "The planner wrote three tests, one per criterion."], "decided": ["A manual fix with no linked issue gets one check that runs all tests.", "Every other pull request with no plan still fails as today."], "open": []},
 "verdict": "approve",
 "summary": "The plan lets a manual fix by Dokima's app merge on all tests passing, and changes nothing else.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "When I want manual work, you do it, you merge, we're done.", "source": "https://github.com/dokima-dev/dokima/issues/643", "criterion": "643.1"},
  {"ask": "a manual fix opens as Dokima's app and merges once all tests pass and the owner approves", "source": "https://github.com/dokima-dev/dokima/issues/643", "criterion": "643.1"},
  {"ask": "merges once all tests pass", "source": "https://github.com/dokima-dev/dokima/issues/643", "criterion": "643.2"},
  {"ask": "Don't override anything", "source": "https://github.com/dokima-dev/dokima/issues/643", "criterion": "643.3"}
 ],
 "behaviors": [
  {"criterion": "643.1", "one_behavior": true, "why": "One result: the app's manual fix gets a check that passes on passing tests."},
  {"criterion": "643.2", "one_behavior": true, "why": "One result: a failing test fails that check."},
  {"criterion": "643.3", "one_behavior": true, "why": "One result: anyone else's unlinked pull request still fails as before."}
 ],
 "edge_cases": [
  {"criterion": "643.1", "cut": [], "missing": []},
  {"criterion": "643.2", "cut": [], "missing": []},
  {"criterion": "643.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_manual_fix_check.py::test_a_manual_fix_by_dokimas_app_gets_a_check_that_runs_all_tests_and_passes", "only_its_behavior": true, "why": "Runs the real check command and workflow step, on the pull request and in the merge queue."},
  {"test": "tests/t
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#643](https://github.com/dokima-dev/dokima/issues/643) (a manual fix by Dokima's app can merge). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks passed.

**What the plan does:** right now the merge check fails every manual fix that Dokima's app opens, because the fix has no linked issue. The plan gives such a fix one check that runs all tests, so it can merge once they pass. Only `dokima/checks.py` changes.

**The tests:** I ran the planner's three new tests. All three fail today, and for the right reason: the app's manual fix still gets the "No approved plan found: no issue linked" check. Each test runs the real check command and the workflow's own test step, with GitHub and pytest faked. They show three things:
- **Passes:** the fix gets a check that runs all tests and passes when they do, both on the pull request and in the merge queue.
- **Fails:** a failing test makes the check fail.
- **Nothing else changes:** a pull request with no linked issue opened by anyone else still fails as before. So does one by the app that names an issue with no approved plan.

**Your asks:** each of your asks maps to one of the three criteria, and the review raises no blockers or questions.

Two of your words have no test of their own:
- **"The owner approves":** your approval comes from GitHub's own branch rule, which this plan doesn't touch.
- **"You merge":** the merge itself is the existing path from [#589](https://github.com/dokima-dev/dokima/issues/589) (manual fixes open as Dokima's app). This plan only removes the check that blocks it.

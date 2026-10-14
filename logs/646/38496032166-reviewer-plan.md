# reviewer (plan) for #646

Run: https://github.com/dokima-dev/dokima/actions/runs/38496032166

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #646: The manual fix check installs what the full suite needs
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The manual fix check fails sound fixes because it lacks a package the all tests check installs.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/95
> 
> 
> **User story:** A manual fix that passes all tests passes the manual fix check too, so it can merge.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The manual fix check installs every package the all tests check installs before running the tests.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-646/tests/test_manual_fix_installs.py#L37"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: The manual fix check installs every package all tests installs, before it runs the tests.*
>   - Edge cases: A package added to the all tests check later

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_manual_fix_installs.py; grep -n "pip install\|pytest" .github/workflows/full-suite.yml .github/workflows/acceptance-criteria.yml; python -m pytest -q tests/test_manual_fix_installs.py 2>&1 | tail -15; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:1500])"
```

> """The manual fix check installs every package the all tests check installs (#646).
> 
> The manual fix row of the Acceptance criteria workflow runs the whole suite, but its job installed only `pytest`, while
> the all tests check (`full-suite.yml`) installs `pytest pytest-xdist`. Tests that need `-n` then failed there and
> passed in all tests, so a sound manual fix could never merge. These tests read the `pip install` lines of both jobs
> and check the criteria job installs, before it runs any test, everything the all tests job installs.
> """
> import os
> import re
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> FULL = os.path.join(ROOT, ".github", "workflows", "full-suite.yml")
> CRITERIA = os.path.join(ROOT, ".github", "workflows", "acceptance-criteria.yml")
> RUN_STEP = "- name: Run this criterion's tests"
> 
> 
> def job_lines(path, job):
>     """The lines of one job of a workflow file, found by its key under `jobs:`."""
>     lines = open(path).read().splitlines()
>     start = next(i for i, l in enumerate(lines) if l == f"  {job}:")
>     end = next((i for i in range(start + 1, len(lines)) if re.match(r"^  \S", lines[i])), len(lines))
>     return lines[start:end]
> 
> 
> def installs(lines):
>     """The packages named by every `pip install` line, with their index in the lines."""
>     found = {}
>     for i, line in enumerate(lines):
>         m = re.search(r"pip install (.*)$", line)
>         if m:
>             for word in m.group(1).split():
>                 if not word.startswith("-"):
>      

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,80p .github/workflows/acceptance-criteria.yml; sed -n 15,30p .github/workflows/full-suite.yml
```

> name: Acceptance criteria
> # One GitHub check per criterion of the PR's approved plan, plus one gate check.
> # Runs main's copy of this workflow and of Dokima's code; only the tests, and the code they judge, come from the PR.
> # In the merge queue they come from the queued commit: the PR on top of the latest main.
> # A draft pull request runs none: Dokima's are drafts until the merge gate readies them, after the code review (#597).
> on:
>   pull_request_target:
>     types: [opened, synchronize, reopened, ready_for_review]
>   merge_group:
> permissions:
>   contents: read
>   issues: read
>   pull-requests: read
> jobs:
>   list:
>     name: list acceptance criteria
>     if: "!github.event.pull_request.draft"
>     runs-on: ubuntu-24.04
>     outputs:
>       matrix: ${{ steps.m.outputs.matrix }}
>     steps:
>       # Main's copy of Dokima's code: in the merge queue the default is the queued commit, so name main's branch.
>       - uses: actions/checkout@v5
>         with:
>           ref: ${{ github.event.merge_group.base_ref }}
>       - id: m
>         env:
>           GH_TOKEN: ${{ github.token }}
>         run: python3 -m dokima.checks matrix >> "$GITHUB_OUTPUT"
> 
>   check:
>     needs: list
>     if: needs.list.outputs.matrix != '[]'
>     name: ${{ matrix.name }}
>     strategy:
>       fail-fast: false
>       matrix:
>         include: ${{ fromJSON(needs.list.outputs.matrix) }}
>     runs-on: ubuntu-24.04
>     steps:
>       - uses: actions/checkout@v5
>         with:
>           ref: ${{ github.event.merge_group.base_ref }}
>           per

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner planned one criterion: the manual fix check installs every package the all tests check installs.", "The planner added one test that compares the two checks' installed packages."], "decided": ["The fix changes only the manual fix check's workflow file."], "open": []},
 "verdict": "approve",
 "summary": "The plan carries the owner's one ask, and its test fails today because the manual fix check lacks pytest-xdist.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "Done when the manual fix check installs what the full suite installs, so a manual fix that passes all tests passes this check too.", "source": "https://github.com/dokima-dev/dokima/issues/646", "criterion": "646.1"}],
 "behaviors": [{"criterion": "646.1", "one_behavior": true, "why": "One result: the check's installs cover the all tests installs before tests run."}],
 "edge_cases": [{"criterion": "646.1", "cut": [], "missing": []}],
 "tests": [{"test": "tests/test_manual_fix_installs.py::test_the_manual_fix_check_installs_what_all_tests_installs", "only_its_behavior": true, "why": "Reads both jobs' installs from the files; fails today naming pytest-xdist, passes once it is added before the run step."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 646 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`5. Bash`
```
sed -i 's/The planner planned one criterion: the manual fix check installs every package the all tests check installs./The planner planned one criterion: the manual fix check installs what all tests installs./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 646 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for #646 (manual fix check installs what the full suite needs). The approval is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

- **Your ask:** the plan has one criterion (646.1). It says the manual fix check installs every package the all tests check installs before it runs the tests. That matches the issue's "Done when" line, and nothing is dropped or added.
- **Its test fails today for the right reason:** "the manual fix check does not install pytest-xdist". The manual fix check installs only `pytest`, while all tests installs `pytest pytest-xdist`.
- **A package added later:** the test reads the all tests check's install list from its workflow file each time it runs. So if a package is added there later, the manual fix check has to install it too.
- **It will pass once fixed:** the test reads the workflow file from the pull request's own copy. Adding `pytest-xdist` to the install step makes it pass.

The fix changes only a workflow file, so even on autopilot the pull request will wait for your approval before it merges.

I raised no blockers or questions.

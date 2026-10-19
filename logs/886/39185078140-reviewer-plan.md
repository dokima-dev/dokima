# reviewer (plan) for #886

Run: https://github.com/dokima-dev/dokima/actions/runs/39185078140

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #886: The baseline passes on a repo with no tests
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 887 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo with no tests yet passes the testmon baseline, and the run says so.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/887
> 
> 
> **User story:** An owner with no tests yet sees the baseline pass, told the repo has no tests yet.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the baseline runs on a repo with no tests, it succeeds and saves an empty baseline.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-886/tests/test_no_tests_yet.py#L42"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: The testmon baseline on an empty tests folder succeeds and saves an empty baseline.*
>   <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-de

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_no_tests_yet.py; git diff main --stat; git diff main -- tests/test_testmon.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:4000])"
```

> """Tests for #886: a repo with no tests yet passes the testmon baseline.
> 
> pytest exits 5 when it collects no tests. Each test runs a real job of a workflow on a temp repo whose tests folder is
> empty, through tests/test_settings_workflows.py's machine, with real pytest. `python3 -m pytest --testmon` runs real
> pytest without testmon and leaves a baseline file, as pytest-testmon 2.2 does even when no test ran (checked by hand).
> """
> import os
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> from test_settings_workflows import Box  # noqa: E402
> 
> PYTHON = '''#!/bin/sh
> # A stand-in for python3: `-m pip` only logs; `-m pytest --testmon` runs real pytest and leaves a baseline file.
> if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then shift 2; echo "pip $*" >> "$SETUP_LOG"; exit 0; fi
> if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then shift 2; args=; mon=
>   for a in "$@"; do if [ "$a" = --testmon ]; then mon=1; else args="$args $a"; fi; done
>   [ -n "$mon" ] && echo baseline > .testmondata
>   exec {real} -m pytest -p no:testmon $args; fi
> exec {real} "$@"
> '''
> EMPTY = {"tests/.gitkeep": ""}
> ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
> BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}
> 
> 
> def box(tmp, files):
>     """A repo holding FILES whose tests run for real, as testmon runs them."""
>     b = Box(tmp, None, files=files, real_tests=True)
>     path = f"{b.tmp}/bin/python3"
>     open(path, "w").write(PYTHON.replace("{real}", sys.executable))
>    

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_no_tests_yet.py tests/test_testmon.py::test_baseline_runs_only_the_tests_folder 2>&1 | grep -E "886\.|passed|failed" | head -20; grep -n "testmon" .github/workflows/testmon.yml | head
```

> Proves 886.1. Runs the baseline job on a repo whose tests folder is empty and expects success and a saved cache; beside it, a
>         record_property("proves", "886.1")
> >       assert result == "success", f"886.1: the baseline failed on a repo with no tests yet:\n{b.tail()}"
> E       AssertionError: 886.1: the baseline failed on a repo with no tests yet:
>         Proves 886.2. Runs the baseline job on an empty tests folder and expects a `::notice` line, the run's notice, holding
>         record_property("proves", "886.2")
> >       assert notices(b), f"886.2: the baseline shows no notice that the repo has no tests yet:\n{b.tail()}"
> E       AssertionError: 886.2: the baseline shows no notice that the repo has no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder - AssertionError: 886.1: the baseline failed on a repo with no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_baseline_says_the_repo_has_no_tests_yet - AssertionError: 886.2: the baseline shows no notice that the repo has no tests yet:
> 2 failed, 1 passed in 1.81s
> 1:name: testmon baseline
> 3:# Every push to main runs every test with pytest-testmon and saves .testmondata to GitHub's cache; agent.yml restores
> 4:# the newest one before a code review's test run. Installs the same packages agent.yml does, so testmon sees the same
> 42:          else out=$(printf 'python=3.12\ntest_tools=pytest pytest-xdist pytest-testmon\ninstall=\n')
> 61:          else echo "TESTS_AFFECTED=testmon

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder 2>&1 | grep -iE "no tests ran|exit|collected|error" | head
```

> E       AssertionError: 886.1: the baseline failed on a repo with no tests yet:
> E         ## baseline: Install the test tools and the repo itself (exit 0)
> E         ## baseline: Affected tests from the settings (exit 0)
> E         ## baseline: None (exit 1)
> E         no tests ran in 0.00s
> tests/test_no_tests_yet.py:50: AssertionError
> FAILED tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder - AssertionError: 886.1: the baseline failed on a repo with no tests yet:
>   ## baseline: Install the test tools and the repo itself (exit 0)
>   ## baseline: Affected tests from the settings (exit 0)
>   ## baseline: None (exit 1)

**Agent:** Right reason. Writing the review.

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the notice test need a real run notice, not plain words."], "decided": ["The full suite part of the ask stays with its sibling issue."], "open": []},
 "verdict": "approve",
 "summary": "The plan carries every ask, and each new test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "886.1"},
  {"ask": "say on the run that the repo has no tests yet", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "886.2"},
  {"ask": "Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand.", "source": "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677", "criterion": "886.3"}
 ],
 "behaviors": [
  {"criterion": "886.1", "one_behavior": true, "why": "Baseline passes on no tests; the saved file is that same outcome."},
  {"criterion": "886.2", "one_behavior": true, "why": "One notice in one case."},
  {"criterion": "886.3", "one_behavior": true, "why": "Only the named tests folder runs."}
 ],
 "edge_cases": [
  {"criterion": "886.1", "cut": [], "missing": []},
  {"criterion": "886.2", "cut": [], "missing": []},
  {"criterion": "886.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder", "only_its_behavior": true, "why": "Fails today on exit 5; a crashing setup must still fail."},
  {"test": "tests/test_no_tests_yet.py::test_the_baseline_says_the_repo_has_no_tests_yet", "only_its_behavior": true, "why": "Needs a run notice line; fails today, and a repo with a test shows none."},
  {"test": "tests/test_testmon.py::test_baseline_runs_only_the_tests_folder", "only_its_behavior": true, "why": "Same checks as befo
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#886](https://github.com/dokima-dev/dokima/issues/886) (the baseline passes on a repo with no tests), with no blockers. Both hand-back checks passed.

- **Last round's blocker is fixed.** The notice test now needs a real run notice saying "No tests yet". Plain words in the log no longer pass it. A repo with one passing test must show no such notice.
- **The two new tests fail today because the feature is missing.** On an empty tests folder the baseline still fails, because the run collects no tests and the step only lets through a failing test. No notice appears either.
- **The tests-folder test passes today, as it should.** It is the older test for keeping the tests folder the settings name. It has the same checks as before and now also reads a step written over several lines.
- **Every ask is carried.** The three asks from [#880](https://github.com/dokima-dev/dokima/issues/880) (a repo with no tests yet passes its test checks) each map to one criterion. The full-suite part of #880 stays with the sibling issue [#887](https://github.com/dokima-dev/dokima/issues/887) (its related issue).

The review is in `/tmp/dokima-out/review.json`.

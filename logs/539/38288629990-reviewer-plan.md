# reviewer (plan) for #539

Run: https://github.com/dokima-dev/dokima/actions/runs/38288629990

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/plan.json; cat /tmp/pack/open_blockers.json
```

> # Issue #539: Code reviews run only affected tests
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [540], "loop": []} -->
> Code reviews run only the tests a change can affect, using a baseline recorded on main.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/540
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/148
> 
> 
> **User story:** Code reviews finish faster: their machine runs only the tests the change can affect.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Each code review runs only the tests its change can affect, picked by testmon from a baseline recorded on main.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-539/tests/test_testmon.py#L148"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddl

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_testmon.py; git show HEAD -- tests/test_checks.py
```

> commit d51e13cee78e5559c41d9820583d2fa9a50fb24b
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:05:42 2026 +0000
> 
>     planner for #539 (run 38287606066)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_checks.py  |   9 +++
>  tests/test_testmon.py | 208 ++++++++++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 217 insertions(+)
> """Code reviews run only affected tests, picked by testmon from main's baseline (issue #539).
> 
> Before each code review, `.github/workflows/agent.yml` runs the tests on the reviewer's machine and writes
> `$PACK/tests.txt` and `$PACK/tests.xml`. With this issue that run uses pytest-testmon: a workflow on every push to main
> (`.github/workflows/testmon.yml`) runs every test with `--testmon` and saves `.testmondata` to GitHub's cache, and
> agent.yml restores it before the run, so only the tests the change can affect run. With no usable baseline (none
> restored, or a file testmon cannot read) the machine runs every test.
> 
> CI has neither testmon nor PyYAML, so these tests read the workflow files line by line, and run the shell of the
> agent.yml step that writes `tests.txt`, cut out of the workflow GitHub runs, with a fake `python3` and `pytest` on PATH.
> The fake behaves as pytest-testmon 2.2 really does (checked by hand): with `--testmon` and a readable baseline it runs
> only the affected test; with `--testmon` and no baseline it runs eve

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_testmon.py tests/test_checks.py 2>&1 | grep -E "Error|539|passed|failed" | head -20; cat .github/workflows/full-suite.yml; grep -n -B3 -A25 "All tests, run by code" .github/workflows/agent.yml; grep -n "pip install" .github/workflows/agent.yml
```

> Proves 539.1. Checks that a workflow on every push to main runs the tests with testmon and saves `.testmondata`
>         record_property("proves", "539.1")
> E       AssertionError: .github/workflows/testmon.yml does not exist
> tests/test_testmon.py:63: AssertionError
>         Proves 539.2. Runs agent.yml's test step three times: with no baseline restored and with a `.testmondata` that is
>         record_property("proves", "539.2")
>             assert calls, f"539.2: when {why}, the test step never ran pytest\n{out}"
>                 f"539.2: when {why}, the last run did not run every test ({calls[-1]['mode']}): pytest {calls[-1]['args']}\n{out}"
>             assert txt is not None and "42 passed" in txt and "INTERNALERROR" not in txt, \
>                 f"539.2: when {why}, tests.txt does not hold the run of every test\n{txt}\n{out}"
>             assert xml, f"539.2: when {why}, tests.xml is missing\n{out}"
>             assert out.startswith("exit 0"), f"539.2: when {why}, the test step failed\n{out}"
>             f"539.2: with a readable baseline the step still runs every test, so it never picks affected tests\n{out}"
> E       AssertionError: 539.2: with a readable baseline the step still runs every test, so it never picks affected tests
> E         42 passed in 1.00s
> tests/test_testmon.py:207: AssertionError
> FAILED tests/test_testmon.py::test_code_review_runs_only_affected_tests - AssertionError: .github/workflows/testmon.yml does not exist
> FAILED tests/test_testmon.py::test_no_usable_bas

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria from the parent's story 1, each with a test.",
          "The planner extended the merge gate test to pin its install and parallel run lines."],
  "decided": ["The baseline is recorded by a new workflow on every push to main."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries all three asks of story 1, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "An agent's machine runs only the tests its change can affect, chosen by pytest-testmon from a baseline recorded on main.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "539.1"},
  {"ask": "With no usable baseline, the agent's machine runs every test", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "539.2"},
  {"ask": "The merge gate still runs every test, in parallel, unchanged.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "539.3"}
 ],
 "behaviors": [
  {"criterion": "539.1", "one_behavior": true, "why": "One result: the review runs only affected tests from main's baseline."},
  {"criterion": "539.2", "one_behavior": true, "why": "One result: with no usable baseline every test runs."},
  {"criterion": "539.3", "one_behavior": true, "why": "One result: the merge gate's full parallel run stays unchanged."}
 ],
 "tests": [
  {"test": "tests/test_testmon.py::test_code_review_runs_only_affected_tests", "only_its_behavior": true, "why": "Checks the baseline is saved on main, restored before the step, and the step picks affected tests; fails today: testmon.yml missing."},
  {"test": "tests/test_testmon.py::test_no_usable_baseline_runs_every_test", "only_its_behavior": true, "why": "Missing and broken baselines must run every test, with a good baseline beside them; fails today on the good case."},
  {"test": "tests/test_checks.py::test_full
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#539](https://github.com/dokima-dev/dokima/issues/539) (code reviews run only affected tests). The hand-back is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Asks:** the plan covers all three asks of story 1 from [#535](https://github.com/dokima-dev/dokima/issues/535) (agents run only affected tests; merge gate unchanged), one criterion each:
  - **539.1:** code reviews run only the affected tests, from a baseline recorded on main.
  - **539.2:** with no usable baseline, every test runs.
  - **539.3:** the merge gate still runs every test in parallel, as today.
- **Tests run today:**
  - The 539.1 test fails because the new baseline workflow, `testmon.yml`, doesn't exist yet.
  - The 539.2 test fails because, even with a good baseline, the review step still runs every test.
  - Both fail because the feature is missing, not because of a crash or a bad path.
  - The 539.3 test passes today. That's expected: it only pins the merge gate as it is now, which the issue's context says up front.
- **Workflow files:** the plan's scope covers two workflow files, `agent.yml` and the new `testmon.yml`. The issue asks for these changes, so that's allowed here. The pull request will still stop for your approval because it touches a workflow file.
- **Raises:** none, and there were no open blockers to answer.

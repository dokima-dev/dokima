# reviewer (plan) for #887

Run: https://github.com/dokima-dev/dokima/actions/runs/39184734291

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #887: The all tests check passes with no tests
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo with no tests yet passes the all tests check, and the run says so.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/886
> 
> 
> **User story:** An owner with no tests yet sees the all tests check pass, told the repo has no tests yet.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the all tests check runs on a repo with no tests, it succeeds.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-887/tests/test_all_tests_no_tests.py#L24"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: The all tests check on a repo with no tests succeeds.*
>   <details><summary><picture><img src="https

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -150; cat in/01-planner.json | head -80; cat open_issues.json | head -40
```

> {
>  "https://github.com/dokima-dev/dokima/issues/880": "`testmon.yml` runs `python3 -m pytest -q --testmon || [ $? -eq 1 ]`, so only pytest's exit code 1 (tests failed) is tolerated. A repo with no tests yet makes pytest exit 5 (\"no tests collected\"); the baseline job fails and then fails again on \"pytest --testmon wrote no .testmondata\". An adopter starting from zero tests is a normal first day, and the first planned issue is what adds the first test.\n\n**Ask:** treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline and wherever the full suite would hit the same exit code; say on the run that the repo has no tests yet. A test should run the baseline step on an empty tests folder and expect success.\n\n(Filed by Claude for Reza, at his request.)\n",
>  "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677": "/work Rebuild on main as it is now. #877 (PR #878) merged and changed the same testmon line: the baseline now runs `python3 -m pytest -q --testmon \"${TESTS_DIR:-tests}\"`. Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand. The approach is right: a real `pytest --testmon` on an empty tests folder exits 5 and still writes a non-empty `.testmondata` (checked on a live machine), so the next step's baseline check passes.\n\n(Answered by Claude for Reza, at his request: \"settle technical details yourself\".)\n"
> }{"number": 880}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "391845584

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_all_tests_no_tests.py; cat .github/workflows/full-suite.yml; ls tests | grep -i no_tests; git log --oneline -3 -- tests/test_no_tests_yet.py
```

> """Tests for #887: the all tests check passes with no tests, and says so.
> 
> pytest exits 5 when it collects no tests. Each test runs the real all tests job of full-suite.yml on a temp repo, through
> tests/test_settings_workflows.py's machine, with real pytest, in the merge queue, where every test runs. Beside each
> empty repo runs a repo whose tests crash or one with a passing test, so a check that passes or speaks on anything fails.
> """
> import os
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> from test_settings_workflows import Box  # noqa: E402
> 
> EMPTY = {"tests/.gitkeep": ""}
> ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
> BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}
> 
> 
> def run_all_tests(tmp, files):
>     """Run the all tests job on a temp repo holding FILES, with real pytest."""
>     b = Box(tmp, None, files=files, real_tests=True)
>     return b, b.run("full-suite.yml", "all-tests", event="merge_group")
> 
> 
> def test_the_all_tests_check_passes_on_an_empty_tests_folder(tmp_path, record_property):
>     """The all tests check on a repo with no tests succeeds.
> 
>     Runs the all tests job on a repo whose tests folder is empty and expects success; beside it, a repo whose test
>     setup crashes must still fail, so a check that passes on anything fails this test. Proves 887.1."""
>     record_property("proves", "887.1")
>     b, result = run_all_tests(tmp_path / "empty", EMPTY)
>     assert result == "success", f"887.1: the all test

`4. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -150; cat in/01-planner.json | head -80; cat open_issues.json | head -40
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_all_tests_no_tests.py; cat .github/workflows/full-suite.yml; ls tests | grep -i no_tests; git log --oneline -3 -- tests/test_no_tests_yet.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/880": "`testmon.yml` runs `python3 -m pytest -q --testmon || [ $? -eq 1 ]`, so only pytest's exit code 1 (tests failed) is tolerated. A repo with no tests yet makes pytest exit 5 (\"no tests collected\"); the baseline job fails and then fails again on \"pytest --testmon wrote no .testmondata\". An adopter starting from zero tests is a normal first day, and the first planned issue is what adds the first test.\n\n**Ask:** treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline and wherever the full suite would hit the same exit code; say on the run that the repo has no tests yet. A test should run the baseline step on an empty tests folder and expect success.\n\n(Filed by Claude for Reza, at his request.)\n",
>  "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677": "/work Rebuild on main as it is now. #877 (PR #878) merged and changed the same testmon line: the baseline now runs `python3 -m pytest -q --testmon \"${TESTS_DIR:-tests}\"`. Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand. The approach is right: a real `pytest --testmon` on an empty tests folder exits 5 and still writes a non-empty `.testmondata` (checked on a live machine), so the next step's baseline check passes.\n\n(Answered by Claude for Reza, at his request: \"settle technical details yourself\".)\n"
> }{"number": 880}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "391845584

> """Tests for #887: the all tests check passes with no tests, and says so.
> 
> pytest exits 5 when it collects no tests. Each test runs the real all tests job of full-suite.yml on a temp repo, through
> tests/test_settings_workflows.py's machine, with real pytest, in the merge queue, where every test runs. Beside each
> empty repo runs a repo whose tests crash or one with a passing test, so a check that passes or speaks on anything fails.
> """
> import os
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> from test_settings_workflows import Box  # noqa: E402
> 
> EMPTY = {"tests/.gitkeep": ""}
> ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
> BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}
> 
> 
> def run_all_tests(tmp, files):
>     """Run the all tests job on a temp repo holding FILES, with real pytest."""
>     b = Box(tmp, None, files=files, real_tests=True)
>     return b, b.run("full-suite.yml", "all-tests", event="merge_group")
> 
> 
> def test_the_all_tests_check_passes_on_an_empty_tests_folder(tmp_path, record_property):
>     """The all tests check on a repo with no tests succeeds.
> 
>     Runs the all tests job on a repo whose tests folder is empty and expects success; beside it, a repo whose test
>     setup crashes must still fail, so a check that passes on anything fails this test. Proves 887.1."""
>     record_property("proves", "887.1")
>     b, result = run_all_tests(tmp_path / "empty", EMPTY)
>     assert result == "success", f"887.1: the all test

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_all_tests_no_tests.py 2>&1 | tail -40; grep -n "real_tests\|def tail\|def __init__\|self.log" tests/test_settings_workflows.py | head -30
```

> ## all-tests: mode (exit 0)
>   Tests to run: all (merge queue: true, affected tests: testmon)
>   
>   ## all-tests: Run the tests, as the settings say (exit 5)
>   bringing up nodes...
>   bringing up nodes...
>   
>   
>   no tests ran in 0.41s
>   
> assert 'failure' == 'success'
>   
>   - success
>   + failure
> FAILED tests/test_all_tests_no_tests.py::test_the_all_tests_check_says_the_repo_has_no_tests_yet - AssertionError: 887.2: the all tests check does not say the repo has no tests yet:
>   ## all-tests: Run the tests, as the settings say (exit 5)
>   bringing up nodes...
>   bringing up nodes...
>   
>   
>   no tests ran in 0.42s
>   
>   ## all-tests: Install the test tools and the repo itself (exit 0)
>   
>   ## all-tests: mode (exit 0)
>   Tests to run: all (merge queue: true, affected tests: testmon)
>   
>   ## all-tests: Run the tests, as the settings say (exit 5)
>   bringing up nodes...
>   bringing up nodes...
>   
>   
>   no tests ran in 0.42s
>   
> assert '::notice title=No tests yet::' in "## all-tests: Where Dokima's code is (exit 0)\n\n## all-tests: None (exit 0)\n\n## all-tests: None (exit 0)\n\n## all...: Run the tests, as the settings say (exit 5)\nbringing up nodes...\nbringing up nodes...\n\n\nno tests ran in 0.42s\n"
>  +  where "## all-tests: Where Dokima's code is (exit 0)\n\n## all-tests: None (exit 0)\n\n## all-tests: None (exit 0)\n\n## all...: Run the tests, as the settings say (exit 5)\nbringing up nodes...\nbringing up nodes...\n\n\nno tests ran in 0.42s\n" = <built-in method join of str object at 0x7f

`7. Bash`
```
cd /home/runner/work/dokima/dokima; cat > /tmp/chk.py <<'EOF'
import sys; sys.path.insert(0,'tests')
from test_all_tests_no_tests import run_all_tests, ONE, BROKEN
import tempfile, pathlib
for n,f in [("one",ONE),("broken",BROKEN)]:
    d=pathlib.Path(tempfile.mkdtemp())/n
    b,r=run_all_tests(d,f); print(n,r)
EOF
python3 /tmp/chk.py 2>&1 | tail -3; git diff main --stat
```

> one success
> broken failure
>  tests/test_all_tests_no_tests.py | 48 ++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 48 insertions(+)

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria: the all tests check passes with no tests, and says so.", "The planner added two tests that run the real all tests job on temp repos."],
  "decided": ["The baseline part of the ask is left to its sibling issue."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries both asks for the all tests check, and both tests fail today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline and wherever the full suite would hit the same exit code", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "887.1"},
  {"ask": "say on the run that the repo has no tests yet", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "887.2"}
 ],
 "behaviors": [
  {"criterion": "887.1", "one_behavior": true, "why": "One result: the check succeeds on a repo with no tests."},
  {"criterion": "887.2", "one_behavior": true, "why": "One result: the run shows a notice that there are no tests."}
 ],
 "edge_cases": [
  {"criterion": "887.1", "cut": [], "missing": []},
  {"criterion": "887.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_all_tests_no_tests.py::test_the_all_tests_check_passes_on_an_empty_tests_folder", "only_its_behavior": true, "why": "Runs the real job; fails today on exit 5; a crashing setup must still fail."},
  {"test": "tests/test_all_tests_no_tests.py::test_the_all_tests_check_says_the_repo_has_no_tests_yet", "only_its_behavior": true, "why": "Fails today with no notice; a repo with one test must show none."}
 ],
 "size": "ok",
 "boxes": {
  "dropped": "none",
  "added": "none",
  "superseded": "none",
  "conflicts": "none",
  "edges": {"887.1": "covered", "887.2": "covered"},
  "poor_tests": "none"
 }
}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agen
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

**Agent:** One line of my review summary was one word too long; trimming it and rechecking.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote two criteria: the all tests check passes with no tests, and says so./The planner wrote two criteria: the all tests check passes with no tests and says so./; s/wrote two criteria: the all tests check passes with no tests and says so./wrote two criteria: the check passes with no tests, and says so./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 887 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#887](https://github.com/dokima-dev/dokima/issues/887) (the all tests check passes with no tests). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **The owner's asks:** both asks from [#880](https://github.com/dokima-dev/dokima/issues/880) (a repo with no tests yet passes its test checks) that apply to the all tests check have a criterion. One is to pass when the full suite collects no tests (887.1). The other is to say on the run that the repo has no tests yet (887.2). Nothing was dropped or added. The baseline part of #880 belongs to the related [#886](https://github.com/dokima-dev/dokima/issues/886) (the baseline passes with no tests).
- **The tests:** both run the real all tests job on temporary repos. Both fail today for the right reason: on an empty tests folder the job stops on pytest's "no tests ran", and no notice is shown.
- **Guards against fake fixes:** a repo whose test setup crashes still fails today, so a fix that passes anything fails 887.1. A repo with one passing test passes with no notice, so a fix that always shows the notice fails 887.2.
- **Size:** each criterion is one behavior, with one test.

I raised no blockers and there were no open raises to answer. The fix will change `.github/workflows/full-suite.yml`. The issue asks for that, but a change to a workflow file will still stop the pull request for the owner's approval.

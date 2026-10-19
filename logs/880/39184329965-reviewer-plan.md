# reviewer (plan) for #880

Run: https://github.com/dokima-dev/dokima/actions/runs/39184329965

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #880: A repo with no tests yet fails the test baseline
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo with no tests yet passes the baseline and the all tests check, and the run says so.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/882 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/882/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:**
> 
> <!-- dokima-folded -->
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> `testmon.yml` runs `python3 -m pytest -q --testmon || [ $? -eq 1 ]`, so only pytest's exit code 1 (tests failed) is tolerated. A repo with no tests yet makes pytest exit 5 ("no tests collected"); the baseline job fails and then fails again on "pytest --testmon wrote no .testmondata". An adopter starting from zero tests is a normal first day, and the first planned issue is what adds the first test.
> 
> **Ask:** treat "no tests collected" as an empty baseline, not a crash, in the testmon baseline and wherever the full suite would hit the same exit code; say on the run that the repo has no tests yet. A test should run the baseline step on

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main --stat; git diff 6a76a2a d72afcf; cat tests/test_no_tests_yet.py; cat .github/workflows/testmon.yml | grep -n -B3 -A10 testmon; 
```

> .github/workflows/full-suite.yml |  5 ++-
>  .github/workflows/testmon.yml    | 13 +++---
>  tests/test_no_tests_yet.py       | 91 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_testmon.py            | 30 ++++++++++---
>  4 files changed, 128 insertions(+), 11 deletions(-)
> diff --git a/tests/test_no_tests_yet.py b/tests/test_no_tests_yet.py
> index e3c5841..c76ce97 100644
> --- a/tests/test_no_tests_yet.py
> +++ b/tests/test_no_tests_yet.py
> @@ -20,6 +20,7 @@ if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then shift 2; args=; mon=
>  exec {real} "$@"
>  '''
>  EMPTY = {"tests/.gitkeep": ""}
> +ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
>  BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}
>  
>  
> @@ -33,27 +34,58 @@ def box(tmp, files):
>  
>  
>  def test_the_baseline_passes_on_an_empty_tests_folder(tmp_path):
> -    """The testmon baseline on an empty tests folder succeeds and says so.
> +    """The testmon baseline on an empty tests folder succeeds and saves an empty baseline.
>  
> -    It saves the empty baseline; a crash while collecting still fails it."""
> +    Runs the baseline job on a repo whose tests folder is empty and expects success and a saved cache; beside it, a
> +    repo whose test setup crashes must still fail, so a job that passes on anything fails this test."""
>      b = box(tmp_path / "empty", EMPTY)
>      result = b.run("testmon.yml", "baseline", event="push")
>      assert result == "success", f"the baseline failed on a repo with no tests yet:

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -8 --graph; git diff main -- .github/; timeout 600 python3 -m pytest -q tests/test_no_tests_yet.py tests/test_testmon.py 2>&1 | tail -15
```

> * d72afcf planner for #880 (run 39184056803)
> * 6a76a2a Main's tests for the planner of #880
> *   e145f87 Merge branch 'main' into try/issue-880
> |\  
> | * 2424f9c worker for #874 (run 39179884361) (#875)
> | * 058ad84 worker for #876 (run 39180349508) (#879)
> * | 3927333 worker for #880 (run 39180860390)
> |/  
> * 053f89f Each release takes its version from the changelog (#871)
> * 742a59a Hotfix issues build from their text and get reviewed (#868)
> diff --git a/.github/workflows/full-suite.yml b/.github/workflows/full-suite.yml
> index 7b5f908..a5f1623 100644
> --- a/.github/workflows/full-suite.yml
> +++ b/.github/workflows/full-suite.yml
> @@ -102,4 +102,7 @@ jobs:
>            elif [ "$MODE" = affected ]; then
>              echo "::notice title=No baseline::No testmon baseline from main was restored, so every test runs."
>            fi
> -          eval "$RUN_ALL"
> +          # No tests collected (exit 5) is a repo with no tests yet: nothing failed, said on the run (#880).
> +          code=0; eval "$RUN_ALL" || code=$?
> +          if [ "$code" -eq 5 ]; then echo "::notice title=No tests yet::The repo has no tests yet, so no test ran."; exit 0; fi
> +          exit "$code"
> diff --git a/.github/workflows/testmon.yml b/.github/workflows/testmon.yml
> index c9a35bc..bd94712 100644
> --- a/.github/workflows/testmon.yml
> +++ b/.github/workflows/testmon.yml
> @@ -61,12 +61,15 @@ jobs:
>            else echo "TESTS_AFFECTED=testmon" >> "$GITHUB_ENV"; fi
>        - if: env.TESTS_AFFECTED == 'all'
>          run: echo "::not

`4. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt HEAD && cd /tmp/wt && git checkout -q main -- .github/workflows && timeout 600 python3 -m pytest -q tests/test_no_tests_yet.py tests/test_testmon.py 2>&1 | grep -E "FAILED|passed|failed|Error:" | head -20
```

> >       assert result == "success", f"the baseline failed on a repo with no tests yet:\n{b.tail()}"
> E       AssertionError: the baseline failed on a repo with no tests yet:
> E       AssertionError: the baseline does not say the repo has no tests yet:
> >       assert result == "success", f"the all tests check failed on a repo with no tests yet:\n{b.tail()}"
> E       AssertionError: the all tests check failed on a repo with no tests yet:
> E       AssertionError: the all tests check does not say the repo has no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder - AssertionError: the baseline failed on a repo with no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_baseline_says_the_repo_has_no_tests_yet - AssertionError: the baseline does not say the repo has no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_all_tests_check_passes_on_an_empty_tests_folder - AssertionError: the all tests check failed on a repo with no tests yet:
> FAILED tests/test_no_tests_yet.py::test_the_all_tests_check_says_the_repo_has_no_tests_yet - AssertionError: the all tests check does not say the repo has no tests yet:
> 4 failed, 3 passed in 8.81s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
cd /tmp/wt && git checkout -q HEAD -- .github/workflows && sed -i 's/code=0; python3 -m pytest -q --testmon || code=\$?/code=0; python3 -m pytest -q --testmon "${TESTS_DIR:-tests}" || code=$?/' .github/workflows/testmon.yml && grep -n 'testmon "' .github/workflows/testmon.yml && timeout 600 python3 -m pytest -q tests/test_no_tests_yet.py tests/test_testmon.py 2>&1 | tail -2; cd /; git -C /home/runner/work/dokima/dokima worktree remove --force /tmp/wt
```

> 70:          code=0; python3 -m pytest -q --testmon "${TESTS_DIR:-tests}" || code=$?
> .......                                                                  [100%]
> 7 passed in 10.35s
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Tests check out: the new tests fail on main for the right reason, and they pass once both fixes are combined. Now writing the review.

`6. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('04-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39183889722",
>  "commit_before": "6a76a2abfd91647ef69022263898c08b8f04a9fa",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 72164,
>   "turns": 10,
>   "cost_usd": 0.47314120000000004,
>   "tokens_in": 381696,
>   "tokens_out": 6588
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/880/39183889722-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39183889722",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner split the work into two stories: the baseline and the all tests check."
>    ],
>    "decided": [
>     "Each check passes on a repo with no tests, showing a no tests yet notice.",
>     "A crash while collecting tests still fails both checks."
>    ],
>    "open": [
>     "The plan was written before the owner asked to keep the tests folder setting."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan drops the owner's ask to keep the tests folder setting, and two criteria name missing tests.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "S1.2, S2.2: no test",
>     "text": "Criteria S1.2 and S2.2 name tests that do not exist. Fix: add both, each also running a repo with one passing test and expecting no notice.",
>     "evidence": "`tests/test_no_tests_yet.py` holds only two tests; `grep says_the_repo tests` finds nothing.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    },
>    {
>     "kind": "blo

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner added the two missing notice tests, each also checking a repo with one test.",
          "The planner added a criterion keeping the tests folder setting with the new handling."],
  "decided": ["The tests folder test now reads the baseline step written on several lines; same checks."],
  "open": []
 },
 "verdict": "approve",
 "summary": "The plan now carries every ask, including keeping the tests folder setting, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "S1.1"},
  {"ask": "A test should run the baseline step on an empty tests folder and expect success.", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "S1.1"},
  {"ask": "say on the run that the repo has no tests yet", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "S1.2"},
  {"ask": "and wherever the full suite would hit the same exit code", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "S2.1"},
  {"ask": "say on the run that the repo has no tests yet", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "S2.2"},
  {"ask": "Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand.", "source": "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677", "criterion": "S1.3"}
 ],
 "behaviors": [
  {"criterion": "S1.1", "one_behavior": true, "why": "The baseline passing on an empty folder; the saved cache is how it passes."},
  {"criterion": "S1.2", "one_behavior": true, "why": "One notice on one case."},
  {"criterion": "S1.3", "one_behavior": true, "why": "The baseline runs over the named tests folder."},
  {"criterion": "S2.1", "one_behavior
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
cd /tmp/dokima-out && sed -i 's/The plan now carries every ask, including keeping the tests folder setting, and each test fails today for the right reason./The plan carries every ask, including keeping the tests folder setting; each new test fails today for the right reason./; s/each also checking a repo with one test/each also checking one passing test/' review.json && cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 880 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#880](https://github.com/dokima-dev/dokima/issues/880) (a repo with no tests yet fails the test baseline). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Earlier blockers fixed:** the two missing tests for the "no tests yet" notice now exist. Each also runs a repo with one passing test and expects no notice. There is now also a criterion (S1.3) that keeps the tests folder setting, as the owner asked on 2026-10-19.
- **Every ask is covered:**
  - The baseline passes on an empty tests folder.
  - The all tests check passes on an empty tests folder.
  - Both runs say the repo has no tests yet.
  - The tests folder setting stays.
- **The new tests fail today for the right reason:** with main's workflow files, all four fail because the feature is missing, not from a crash.
- **The tests folder test fails on this branch:** the old build, which clashed with main, dropped the tests folder setting. This test catches that.
- **The combined fix passes:** I applied the new handling on top of main's tests folder argument in a throwaway copy, and all 7 tests passed. I then deleted that copy; no repo file changed.
- **The one older test the plan changes is safe:** it now also reads a step written on several lines, and its checks are the same.

I found no blockers, out-of-scope changes or outside issues to raise.

The pull request will still need the owner to merge it, because it changes workflow files.

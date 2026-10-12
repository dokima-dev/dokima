# reviewer (plan) for #536

Run: https://github.com/dokima-dev/dokima/actions/runs/38288878638

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/plan.json; cat /tmp/pack/open_blockers.json
```

> # Issue #536: Plans list each criterion's edge cases
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [537, 538], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/537
> - https://github.com/dokima-dev/dokima/issues/538
> 
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> <!-- dokima-card -->
> <!-- /dokima-card -->
> 
> <details open><summary>From the approved plan of #531, story 1</summary>
> 
> **Part of:** #531 Plans list each criterion's edge cases, and reviews judge each list
> 
> **User story:** Every plan lists each criterion's edge cases with the test covering each, or says why there are none.
> 
> **Context:** Plan check: `dokima/planner.py` (`from_kind`, `problems`); criteria hold text, words, source; tests map `N.k` to test names. Add per-criterion edge cases there. Prompts: `dokima/roles/planner.md`, `dokima/roles/plan-grade.md` (its Edge cases line). The issue asks to change `dokima/roles/`.
> 
> **Acceptance criteria:**
> - A plan lists, for each criterion, its edge cases, each with the test covering it, or why there are none. ([source](https://github.com/dokima-dev/dokima/issues/531))
> - A plan with a criterion that has neither edge cases nor a reason is rejected, naming that criterion. ([source](https://github.com/dokima-dev/dokima/issues/531))
> 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_edge_cases.py; git show HEAD -- tests/test_agent.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit f97366c74c03c7936c39a88e37383f1c4ce49af4
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:07:53 2026 +0000
> 
>     planner for #536 (run 38287243382)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/samples/132/plan.json        |   6 +-
>  tests/test_agent.py                |   2 +-
>  tests/test_body.py                 |   2 +-
>  tests/test_card_status.py          |   2 +-
>  tests/test_criteria_quote_owner.py |   5 +-
>  tests/test_edge_cases.py           | 150 +++++++++++++++++++++++++++++++++++++
>  tests/test_no_out_of_scope.py      |   2 +-
>  tests/test_parent_source.py        |   3 +-
>  tests/test_plan_check.py           |   6 +-
>  tests/test_plan_shape.py           |   5 +-
>  tests/test_planner.py              |   3 +-
>  tests/test_raise_handbacks.py      |   2 +-
>  tests/test_review_asks.py          |   4 +-
>  13 files changed, 174 insertions(+), 18 deletions(-)
> """Every plan lists each criterion's edge cases with their tests, or why there are none.
> 
> Covers #536, story 1 of #531. The planner's hand-back gives each criterion either `edge_cases`, a list of
> {"case": ..., "test": "path::name"} where the test is one the plan files under that criterion, or `no_edge_cases`, the
> reason it has none. The plan check rejects a criterion with neither, naming it, and the planner's prompt teaches the
> guiding kinds (error, timeout, bad data, empty) with examples, saying other kinds cou

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/ ':!tests/test_edge_cases.py' ':!tests/test_agent.py' | head -250
```

> commit f97366c74c03c7936c39a88e37383f1c4ce49af4
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:07:53 2026 +0000
> 
>     planner for #536 (run 38287243382)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/samples/132/plan.json b/tests/samples/132/plan.json
> index cc1a5d5..ef99c6c 100644
> --- a/tests/samples/132/plan.json
> +++ b/tests/samples/132/plan.json
> @@ -5,14 +5,16 @@
>   "acceptance_criteria": [
>    {
>     "text": "When a planner, plan review, worker or code review run fails (its agent crashed, or code rejected its hand-back), the issue's card, and its open pull request's, stays in that stage's column (Plan, Plan, Work, Review) and shows Needs you. That still holds when the run's own \"Decide what follows\" step fails as well, for example because GitHub answers 502. A run that hands on to the next agent still leaves the pill cleared.",
> -   "source": "https://github.com/dokima-dev/dokima/issues/132"
> +   "source": "https://github.com/dokima-dev/dokima/issues/132",
> +   "no_edge_cases": "saved before plans listed edge cases"
>    }
>   ],
>   "non_functional": [
>    {
>     "text": "A run that left no record and no decision behind still puts its card in the column of the stage it was started for, with Needs you, and the board step exits 0.",
>     "why": "A failure the run could not even write down must not leave the card looking fine; the run's own failure, not the boar

`4. Bash`
```
cd /home/runner/work/dokima/dokima; pytest -q tests/test_edge_cases.py 2>&1 | grep -E "Error|assert|passed|failed" | head -30; pytest -q -x 2>&1 | tail -3; grep -n -i "edge" dokima/roles/planner.md dokima/planner.py | head
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bbsgfk0kt). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`5. Bash`
```
cd /home/runner/work/dokima/dokima; pytest -q tests/test_edge_cases.py 2>&1 | grep -E "^E .*53|passed|failed" | head -30; grep -n -i "edge" dokima/roles/planner.md dokima/planner.py | head
```

> E       AssertionError: 536.1: an edge case with no test was not rejected naming acceptance criterion 1: None
> E       AssertionError: 536.2 (missing): a criterion with neither edge cases nor a reason was accepted
> E       AssertionError: 536.2 (empty list): a criterion with neither edge cases nor a reason was accepted
> E       AssertionError: 536.2 (blank reason): a criterion with neither edge cases nor a reason was accepted
> E       AssertionError: 536.3: the planner's prompt has no Edge cases section
> 5 failed in 0.08s

**Agent:** The new tests all fail for the right reason; the full test suite is still running, and I'm waiting on it before writing the review.

`6. Bash`
```
sleep 100; tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output
```

> <tool_use_error>Blocked: sleep 100 followed by: tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

**Agent:** Meanwhile I'll write the review.

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned three criteria: plans list edge cases, plans missing them are rejected, the prompt teaches kinds.",
          "Wrote three tests and gave older sample plans a reason for no edge cases."],
  "decided": ["Each criterion carries either its edge cases with their tests or a reason for none."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan covers all three asks of this story, and each new test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A plan lists, for each criterion, its edge cases, each with the test covering it, or why there are none.", "source": "https://github.com/dokima-dev/dokima/issues/536", "criterion": "536.1"},
  {"ask": "A plan with a criterion that has neither edge cases nor a reason is rejected, naming that criterion.", "source": "https://github.com/dokima-dev/dokima/issues/536", "criterion": "536.2"},
  {"ask": "The planner's prompt gives error, timeout, bad data and empty as guiding kinds, with examples, and says other kinds count.", "source": "https://github.com/dokima-dev/dokima/issues/536", "criterion": "536.3"}],
 "behaviors": [
  {"criterion": "536.1", "one_behavior": true, "why": "Each criterion's edge cases are listed with their tests."},
  {"criterion": "536.2", "one_behavior": true, "why": "A criterion with neither is rejected, naming it."},
  {"criterion": "536.3", "one_behavior": true, "why": "The prompt teaches the guiding kinds with examples."}],
 "tests": [
  {"test": "tests/test_edge_cases.py::test_a_plan_lists_each_criterions_edge_cases_each_with_its_test", "only_its_behavior": true, "why": "Accepts a good list, rejects a case with no test or a test from another criterion."},
  {"test": "tests/test_edge_cases.py::test_a_criterion_with_neither_edge_cases_nor_a_reason_is_rejected_naming_it", "only_its_behavior": true, "why": "Missing, empty and blank cases each reject
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Planned three criteria: plans list edge cases, plans missing them are rejected, the prompt teaches kinds./Planned three criteria: plans list edge cases, plans missing them fail, the prompt teaches kinds./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 536 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** Now waiting on the full suite.

`9. Bash`
```
until grep -qE "passed|failed|error" <(tail -2 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output); do sleep 5; done; tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output
```

> Command did not complete within its 600s timeout and was moved to the background (ID: baakpwfgk). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/baakpwfgk.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.

`10. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output | tail -8
```

> FAILED tests/test_edge_cases.py::test_a_criterion_with_neither_edge_cases_nor_a_reason_is_rejected_naming_it[missing] - AssertionError: 536.2 (missing): a criterion with neither edge cases nor a reason was accepted
> assert None is not None
> FAILED tests/test_edge_cases.py::test_a_criterion_with_neither_edge_cases_nor_a_reason_is_rejected_naming_it[empty list] - AssertionError: 536.2 (empty list): a criterion with neither edge cases nor a reason was accepted
> assert (None)
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 418 passed in 290.43s (0:04:50)
> 
> [exited with code 0]

**Agent:** The full run stopped at the first new test, so I'm running the rest of the suite without it.

`11. Bash`
```
cd /home/runner/work/dokima/dokima; pytest -q -p no:cacheprovider --deselect tests/test_edge_cases.py --ignore=tests/test_edge_cases.py 2>&1 | tail -5
```

> Command running in background with ID: b0vwvvxe0. Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/b0vwvvxe0.output. You will be notified when it completes. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`12. TaskStop`
```
{"task_id": "baakpwfgk"}
```

> {"message":"Successfully stopped task: baakpwfgk (until grep -qE \"passed|failed|error\" <(tail -2 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output); do sleep 5; done; tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output)","task_id":"baakpwfgk","task_type":"local_bash","command":"until grep -qE \"passed|failed|error\" <(tail -2 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output); do sleep 5; done; tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/bbsgfk0kt.output"}

**Agent:** The rest of the suite is running now. I'll finish once it reports.

`13. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/b371490b-7dd0-4bf7-91b9-08777a2b3d9d/tasks/b0vwvvxe0.output
```

> ........................................................................ [ 81%]
> ........................................................................ [ 88%]
> ........................................................................ [ 95%]
> ...................................................                      [100%]
> 1059 passed in 571.94s (0:09:31)
> 
> [exited with code 0]

**Agent:** I approved the plan for [#536](https://github.com/dokima-dev/dokima/issues/536) (plans list each criterion's edge cases). The review is saved in `/tmp/dokima-out/review.json` and passes both hand-back checks.

- **The asks:** all three are covered, one criterion each. Plans list edge cases with their tests or say why there are none (536.1). A criterion with neither is rejected by name (536.2). The planner's prompt teaches error, timeout, bad data and empty, with examples, and says other kinds count (536.3).
- **New tests:** all five fail today because the feature is missing, not because of a crash or bad setup. The plan check still accepts an edge case with no test, still accepts a criterion with neither edge cases nor a reason, and the prompt has no Edge cases section yet.
- **Older tests:** the planner also edited the sample plans in about a dozen existing test files, giving each criterion a reason for having no edge cases. With those edits, the rest of the suite passes (1,059 tests).
- **Size:** each criterion is one behavior, and each test checks only its own criterion.

I raised nothing. Two things I looked at and decided not to block on:
- **Reviewer's prompt:** the parent issue [#531](https://github.com/dokima-dev/dokima/issues/531) asks for this guidance in both the planner's and the reviewer's prompts, but this story covers only the planner's. I assumed a sibling story, [#537](https://github.com/dokima-dev/dokima/issues/537) or [#538](https://github.com/dokima-dev/dokima/issues/538), covers the reviewer's prompt. The pack doesn't include them, so I couldn't check.
- **Recorded test changes:** the plan records a reason only for the change in `tests/test_agent.py`. The other changed files only add that one field to sample plans.

# reviewer (plan) for #666

Run: https://github.com/dokima-dev/dokima/actions/runs/38641474788

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> total 40
> drwxr-xr-x 2 runner runner 4096 Oct 14 21:36 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 21:36 ..
> -rw-r--r-- 1 runner runner 5832 Oct 14 21:36 01-planner.json
> -rw-r--r-- 1 runner runner 5173 Oct 14 21:36 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 1628 Oct 14 21:36 03-worker.json
> -rw-r--r-- 1 runner runner 3944 Oct 14 21:36 04-reviewer-pr.json
> -rw-r--r-- 1 runner runner 5265 Oct 14 21:36 05-planner.json
> # Issue #666: A plan's scope comes from its criteria's files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559], "loop": []} -->
> The worker may change only the files the criteria list, plus their tests.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/693 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/693/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg

`2. Bash`
```
cd /tmp/pack/in; for f in *; do echo "== $f"; cat $f; echo; done | head -300
```

> == 01-planner.json
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38629941341",
>  "commit_before": "0e584917b5d4977ca0c577986dc8b790340d2cbe",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1556753,
>   "turns": 44,
>   "cost_usd": 1.9330644,
>   "tokens_in": 3207766,
>   "tokens_out": 26925
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/666/38629941341-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38629941341",
>  "handback": {
>   "kind": "user_story",
>   "title": "A plan's scope comes from its criteria's files",
>   "summary": "The worker may change only the files the criteria list, plus their tests.",
>   "user_story": "The worker may change exactly the files the criteria list, plus their tests, with no separate scope to keep.",
>   "acceptance_criteria": [
>    {
>     "text": "A plan's scope is every file its criteria list, plus the tests the plan names.",
>     "words": "The plan's scope is all criteria's files plus their tests",
>     "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6173691734",
>     "files": [
>      "dokima/planner.py",
>      "dokima/fence.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "A file two criteria both list shows once in the scope.",
>       "test": "tests/test_scope_from_files.py::test_scope_is_the_criteria_files_plus_the_tests"
>      }
>     ]
>    },
>    {
>     "text": "The plan check rejects a plan that still carries a separate scope field.",
>    

`3. Bash`
```
cd /tmp/pack/in; for f in 03* 04* 05*; do echo "== $f"; python3 -c "import json,sys;d=json.load(open('$f'));print(json.dumps(d.get('handback'),indent=1)[:3500]);print(d.get('check'))"; done
```

> == 03-worker.json
> {
>  "summary": "The scope now comes from the criteria's files and tests; a plan carrying its own scope is rejected.",
>  "criteria": {
>   "666.1": "`scope_from` in `dokima/fence.py` joins the criteria's `files` and test files; `from_kind` and the Scope heading use it.",
>   "666.2": "`from_kind` in `dokima/planner.py` rejects any `scope` field, even empty; removed from `dokima/roles/planner.md` and the play-through stand-in.",
>   "666.3": "`dokima/fence.py` `main` reads the scope from plan.json through `scope_from`, so unlisted files are undone.",
>   "666.4": "`check_words` unchanged; its tests now pass since the sample plans no longer need a scope field."
>  },
>  "evidence": "`pytest -q tests/test_scope_from_files.py tests/test_criteria_quote_owner.py`: 11 passed.",
>  "raises": [],
>  "answers": []
> }
> {'passed': True, 'problems': []}
> == 04-reviewer-pr.json
> {
>  "previous_step": {
>   "did": [
>    "The worker made a plan's scope the files its criteria list, plus its test files.",
>    "The worker made the plan check reject a plan that still carries a scope field.",
>    "The worker made the fence read the scope from the criteria's files."
>   ],
>   "decided": [
>    "The worker removed the scope field from the planner's instructions, as the plan assumed."
>   ],
>   "open": [
>    "Two older plan check tests now fail: their sample plan still carries a scope field."
>   ]
>  },
>  "verdict": "block",
>  "summary": "The code does what the plan asks, but two older tests now fail, and only the planner ca

`4. Bash`
```
git diff main --stat && pytest -q -x 2>&1 | tail -5; rm -rf /tmp/mainsrc && mkdir /tmp/mainsrc && git archive main | tar -x -C /tmp/mainsrc && cp tests/test_scope_from_files.py tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py /tmp/mainsrc/tests/ && cd /tmp/mainsrc && pytest -q tests/test_scope_from_files.py tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py 2>&1 | grep -E "FAILED|passed|failed|Error" | head -30
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bh70xq0w9). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`5. Bash`
```
cd /home/runner/work/dokima/dokima && git diff main --stat && pytest -q -x 2>&1 | tail -5; rm -rf /tmp/mainsrc && mkdir /tmp/mainsrc && git archive main | tar -x -C /tmp/mainsrc && cp tests/test_scope_from_files.py tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py /tmp/mainsrc/tests/ && cd /tmp/mainsrc && pytest -q tests/test_scope_from_files.py tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py 2>&1 | grep -E "FAILED|passed|failed|Error" | head -30
```

**Agent:** Meanwhile, read the new test file.

`6. Bash`
```
cat tests/test_scope_from_files.py; git diff main -- tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py | head -200
```

> """A plan's scope comes from its criteria's files, with no separate scope field.
> 
> Covers #666 (story 2 of #661). The worker may change exactly the files the criteria list, plus the tests the plan
> names. The plan check reads the scope from each criterion's `files` and the test files in `tests`, writes it under the
> issue's Scope heading, and rejects a plan still carrying its own `scope`. The fence, run as the worker's workflow runs
> it on the plan's hand-back, keeps changes to listed files and undoes every other change.
> """
> import json
> import os
> import subprocess
> import sys
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from dokima import fence, planner  # noqa: E402
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> SRC = "https://github.com/o/r/issues/9"
> 
> 
> def story(**extra):
>     """A well-formed story with no scope field, two criteria and two test files."""
>     p = {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls hand back a job id.",
>          "user_story": "Slow calls return a job id.",
>          "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC,
>                                   "files": ["dokima/jobs.py", "dokima/queue.py"], "no_edge_cases": "a sample"}],
>          "non_functional": [{"text": "Job ids never repeat.", "why": "two jobs would share results", "source": SRC,
>                              "files": ["dokima/ids.py", "dokima/jobs.py"], "no_edge_cases":

**Agent:** Meanwhile, read the new test file.

`7. Bash`
```
cd /home/runner/work/dokima/dokima && cat tests/test_scope_from_files.py; git diff main -- tests/test_criteria_quote_owner.py tests/test_parent_source.py tests/test_agent.py | head -200
```

`8. Bash`
```
sleep 100; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output
```

> <tool_use_error>Blocked: sleep 100 followed by: cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`9. Bash`
```
git show --stat HEAD | head -20; git diff main --stat
```

> commit 5613fb546b8ee66c90d2de86c8f10045ade4256b
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 21:35:24 2026 +0000
> 
>     planner for #666 (run 38640018994)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_parent_source.py | 2 +-
>  1 file changed, 1 insertion(+), 1 deletion(-)
>  dokima/fence.py                    |   9 ++-
>  dokima/planner.py                  |   7 +-
>  dokima/playthrough.py              |   5 +-
>  dokima/roles/planner.md            |   1 -
>  tests/samples/132/plan.json        |   4 -
>  tests/test_agent.py                |   6 +-
>  tests/test_body.py                 |   2 +-
>  tests/test_card_status.py          |   2 +-
>  tests/test_clash.py                |   2 +-
>  tests/test_criteria_quote_owner.py |  12 ++-
>  tests/test_criterion_files.py      |   1 -
>  tests/test_edge_cases.py           |   1 -
>  tests/test_merge_gate.py           |   4 +-
>  tests/test_no_out_of_scope.py      |   2 +-
>  tests/test_parent_source.py        |   2 +-
>  tests/test_plan_check.py           |   4 +-
>  tests/test_plan_shape.py           |   1 -
>  tests/test_plan_title.py           |   2 +-
>  tests/test_planner.py              |   2 +-
>  tests/test_raise_handbacks.py      |   2 +-
>  tests/test_review_asks.py          |   2 +-
>  tests/test_scope_from_files.py     | 154 +++++++++++++++++++++++++++++++++++++
>  tests/test_start.py                |   4 +-
>  23 files changed, 196 insertions(+), 35 

`10. Bash`
```
cd /home/runner/work/dokima/dokima && git show --stat HEAD | head -20; git diff main --stat
```

`11. Monitor`
```
until grep -qE "passed|failed" /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output; do sleep 5; done; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output
```

> <tool_use_error>InputValidationError: Monitor failed due to the following issue:
> The required parameter `description` is missing
> 
> This tool's schema was not sent to the API — it was not in the discovered-tool set derived from message history. Without the schema in your prompt, typed parameters (arrays, numbers, booleans) get emitted as strings and the client-side parser rejects them. Load the tool first: call ToolSearch with query "select:Monitor", then retry this call. For reference, this tool's input schema is: {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":{"description":{"description":"Short human-readable description of what you are monitoring (shown in notifications).","type":"string"},"timeout_ms":{"description":"Kill the monitor after this deadline. Default 300000ms. Deadlines above 600000ms are capped to 600000ms. You are notified at expiry and can re-arm.","default":300000,"type":"number","minimum":1000,"maximum":3600000},"command":{"description":"Shell command or script. Each stdout line is an event; exit ends the watch.","type":"string"},"ws":{"description":"WebSocket to open. Each text frame is an event; binary frames are reported as a placeholder line. Socket close ends the watch. Cannot be combined with command.","type":"object","properties":{"url":{"type":"string"},"protocols":{"type":"array","items":{"type":"string","pattern":"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$"}}},"required":["url"],"additionalProperties":false}},"required"

`12. Bash`
```
grep -n "scope" dokima/planner.py | head -20
```

> 247:    if kind in ("feature", "user_story") and "scope" in p:
> 248:        bad.append("scope is a retired field: a plan's scope is every file its criteria list, plus the tests it names")
> 302:                    "scope": fence.scope_from(p), "test_changes": tc,
> 563:    lines += [f"- `{s.strip()}`" for s in plan["scope"]]

`13. Bash`
```
cd /home/runner/work/dokima/dokima && grep -n "scope" dokima/planner.py | head -20
```

`14. Read`
```
/tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output
```

> 1	 dokima/fence.py                    |   9 ++-
> 2	 dokima/planner.py                  |   7 +-
> 3	 dokima/playthrough.py              |   5 +-
> 4	 dokima/roles/planner.md            |   1 -
> 5	 tests/samples/132/plan.json        |   4 -
> 6	 tests/test_agent.py                |   6 +-
> 7	 tests/test_body.py                 |   2 +-
> 8	 tests/test_card_status.py          |   2 +-
> 9	 tests/test_clash.py                |   2 +-
> 10	 tests/test_criteria_quote_owner.py |  12 ++-
> 11	 tests/test_criterion_files.py      |   1 -
> 12	 tests/test_edge_cases.py           |   1 -
> 13	 tests/test_merge_gate.py           |   4 +-
> 14	 tests/test_no_out_of_scope.py      |   2 +-
> 15	 tests/test_parent_source.py        |   2 +-
> 16	 tests/test_plan_check.py           |   4 +-
> 17	 tests/test_plan_shape.py           |   1 -
> 18	 tests/test_plan_title.py           |   2 +-
> 19	 tests/test_planner.py              |   2 +-
> 20	 tests/test_raise_handbacks.py      |   2 +-
> 21	 tests/test_review_asks.py          |   2 +-
> 22	 tests/test_scope_from_files.py     | 154 +++++++++++++++++++++++++++++++++++++
> 23	 tests/test_start.py                |   4 +-
> 24	 23 files changed, 196 insertions(+), 35 deletions(-)
> 25

**Agent:** Still running the full test suite on the branch; I'll check main once it finishes.

`15. ToolSearch`
```
{"query": "select:Monitor", "max_results": 1}
```

> 

> 

`16. Bash`
```
until grep -qE "passed|failed|error" /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output; do sleep 5; done; sleep 60; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/bh70xq0w9.output | tail -40
```

> Command running in background with ID: b6kkh2kma. Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/b6kkh2kma.output. You will be notified when it completes. To check interim output, use Read on that file path.

`17. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner removed the scope field from the sample plan in the parent-source tests.",
   "The planner kept the four criteria and their tests as before."
  ],
  "decided": [
   "The planner changed no criterion and no new test this round."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "The one blocker is fixed; each ask still has one criterion and a test that fails today.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The plan's scope is all criteria's files plus their tests", "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6173691734", "criterion": "666.1"},
  {"ask": "with no separate scope field", "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6173691734", "criterion": "666.2"},
  {"ask": "The fence keeps enforcing it.", "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6173691734", "criterion": "666.3"},
  {"ask": "Each one quotes my words, which are the spec.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "666.4"}
 ],
 "behaviors": [
  {"criterion": "666.1", "one_behavior": true, "why": "One result: the scope equals the criteria files plus the test files."},
  {"criterion": "666.2", "one_behavior": true, "why": "One result: a plan with a scope field is rejected."},
  {"criterion": "666.3", "one_behavior": true, "why": "One result: changes to unlisted files are undone."},
  {"criterion": "666.4", "one_behavior": true, "why": "One result: a criterion without the owner's words is rejected."}
 ],
 "edge_cases": [
  {"criterion": "666.1", "cut": [], "missing": []},
  {"criterion": "666.2", "cut": [], "missing": []},
  {"criterion": "666.3", "cut": [], "missing": []},
  {"criterion": "666.4", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_scope_from_files.py::test_scope_is_the_criteria_files_plus_the_tests", "only_its_behavior"
```

> rc=0

**Agent:** Draft passes the check; waiting on the test runs before finalizing.

`18. Bash`
```
until [ -s /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/b6kkh2kma.output ]; do sleep 5; done; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/b6kkh2kma.output
```

> tests/test_no_out_of_scope.py      |   2 +-
>  tests/test_parent_source.py        |   2 +-
>  tests/test_plan_check.py           |   4 +-
>  tests/test_plan_shape.py           |   1 -
>  tests/test_plan_title.py           |   2 +-
>  tests/test_planner.py              |   2 +-
>  tests/test_raise_handbacks.py      |   2 +-
>  tests/test_review_asks.py          |   2 +-
>  tests/test_scope_from_files.py     | 154 +++++++++++++++++++++++++++++++++++++
>  tests/test_start.py                |   4 +-
>  23 files changed, 196 insertions(+), 35 deletions(-)
>   
> assert 128 == 0
>  +  where 128 = CompletedProcess(args=('git', 'clone', '-q', '/tmp/pytest-of-runner/pytest-0/test_the_worker_is_not_handed_0/origin.gi...ut failed.\nYou can inspect what was checked out with 'git status'\nand retry with 'git restore --source=HEAD :/'\n\n").returncode
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 1121 passed, 1 warning in 653.71s (0:10:53)
> E       AssertionError: 666.2: the planner's instructions still ask for a scope field the plan check rejects
> tests/test_scope_from_files.py:88: AssertionError
> E       AssertionError: 666.3: the change to a file a criterion lists was undone
> tests/test_scope_from_files.py:132: AssertionError
> E       AssertionError: 666.3: the change to a file a criterion lists was undone
> tests/test_scope_from_files.py:152: AssertionError
> E       AssertionError: assert [] == ['app.py']
> tests/test_agent.py:74: AssertionError
> E       AssertionError: assert 

**Agent:** Main shows each new test failing for the missing feature. One branch failure (a git clone test) needs a check against main.

`19. Bash`
```
grep -rln "def test_the_worker_is_not_handed" tests/ ; T=$(grep -rl "def test_the_worker_is_not_handed" tests/ | head -1); N=$(grep -o "def test_the_worker_is_not_handed[a-z_]*" $T | head -1 | cut -c5-); pytest -q "$T::$N" 2>&1 | tail -15; cd /tmp/mainsrc && pytest -q "$T::$N" 2>&1 | tail -3
```

> tests/test_test_clash_planner.py
> .                                                                        [100%]
> 1 passed in 0.98s
> .                                                                        [100%]
> 1 passed in 1.01s
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Main shows each new test failing for the missing feature. One branch failure (a git clone test) needs a check against main.

`20. Bash`
```
cd /home/runner/work/dokima/dokima && grep -rln "def test_the_worker_is_not_handed" tests/ ; T=$(grep -rl "def test_the_worker_is_not_handed" tests/ | head -1); N=$(grep -o "def test_the_worker_is_not_handed[a-z_]*" $T | head -1 | cut -c5-); pytest -q "$T::$N" 2>&1 | tail -15; cd /tmp/mainsrc && pytest -q "$T::$N" 2>&1 | tail -3
```

**Agent:** That clone test passes on its own on both branch and main, so it looks flaky. Running the full suite once more without stopping at the first failure.

`21. Bash`
```
pytest -q -p no:cacheprovider 2>&1 | grep -E "^FAILED|passed|failed" | tail -15
```

> Command running in background with ID: b5egb1hdj. Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/b5egb1hdj.output. You will be notified when it completes. To check interim output, use Read on that file path.

**Agent:** That clone test passes on its own on both branch and main, so it looks flaky. Running the full suite once more without stopping at the first failure.

`22. Bash`
```
cd /home/runner/work/dokima/dokima && pytest -q -p no:cacheprovider 2>&1 | grep -E "^FAILED|passed|failed" | tail -15
```

**Agent:** Waiting for the full suite run (about 11 minutes).

`23. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/3f086dd7-c2ba-4920-8f9d-255fc8dad9a3/tasks/b5egb1hdj.output
```

> 1201 passed, 1 warning in 708.60s (0:11:48)
> 
> [exited with code 0]

**Agent:** I approved the plan for [#666](https://github.com/dokima-dev/dokima/issues/666) (a plan's scope comes from its criteria's files). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last blocker fixed:** the code review on [#693](https://github.com/dokima-dev/dokima/pull/693) (the pull request for this issue) had one blocker: an older test's sample plan still had a scope field. The planner removed that field, and this round they changed nothing else.
- **On main, each new test fails because the feature is missing.** None fails from a crash or a bad path. That covers all five new tests and the reworked owner-words test.
- **On the branch, the whole suite passes:** 1201 tests. A first run stopped at one git clone test. That test passes when run alone on both the branch and main, and it passed in the full rerun, so it looks flaky.
- **Every ask is covered:** each of the owner's four asks from [#661](https://github.com/dokima-dev/dokima/issues/661) (work splits into stories by the files it changes) has one criterion and its own test. Each criterion is a single behavior, and no needed edge case is missing.

There were no open blockers to answer, and I raised nothing new.

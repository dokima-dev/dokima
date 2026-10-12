# reviewer (plan) for #514

Run: https://github.com/dokima-dev/dokima/actions/runs/38202009534

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #514: A run that dies before posting its record leaves the issue looking busy forever
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A run that dies before posting its record no longer leaves its issue looking busy forever.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/519 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/519/files)
> 
> **User story:** When a run dies silently, the owner sees it failed, and autopilot can start that stage again.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A run that dies before posting its record gets a failed record linking the run.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/00cb579b6b0208376b996ce33d66cab6b02d046b/tests/test_unrecorded_run.py#L111"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A run that dies before posting its record gets a failed r

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['02-reviewer-plan.json','05-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d, indent=1)[:5000])
"; cd /home/runner/work/dokima/dokima; git show 00cb579 --stat; git show 00cb579 -- tests/
```

> 02-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38199238136",
>  "commit_before": "628df473d1107e3e05da34ba05e6ecdf386ca259",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 58653,
>   "turns": 8,
>   "cost_usd": 0.44433079999999997,
>   "tokens_in": 341070,
>   "tokens_out": 4833
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/514/38199238136-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38199238136",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote three criteria, each with one test that runs the real workflows."
>    ],
>    "decided": [
>     "A dead run's stage starts again on autopilot start, not the stage after it.",
>     "Dead runs found by the fifteen minute sweep are left out."
>    ],
>    "open": [
>     "Two questions for the owner: which stage restarts, and whether a failed record restarts too."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan covers both asks with tests that fail today for the right reason; two questions wait for you.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.",
>     "source": "https://github.com/dokima-dev/dokima/issues/514",
>     "criterion": "514.1"
>    },
>    {
>     "ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.",
>     "sour

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show c900074 --stat | head; git diff e75f116 --stat; timeout 600 python3 -m pytest -q tests/test_unrecorded_run.py tests/test_progress_card.py 2>&1 | tail -15
```

> commit c9000746cfaccdfa7d3590640dbb95216e99c033
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 03:52:48 2026 +0000
> 
>     worker for #514 (run 38199983061)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  .github/workflows/agent.yml | 39 ++++++++++++++++++++
>  AGENTS.md                   |  4 +--
>  .github/workflows/agent.yml  |  39 +++++++++
>  AGENTS.md                    |   4 +-
>  dokima/agent.py              |  87 +++++++++++++++++++-
>  tests/test_progress_card.py  |  18 +++-
>  tests/test_unrecorded_run.py | 191 +++++++++++++++++++++++++++++++++++++++++++
>  5 files changed, 330 insertions(+), 9 deletions(-)
> ........                                                                 [100%]
> 8 passed in 13.61s

`4. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt e75f116 && cp tests/test_unrecorded_run.py tests/test_progress_card.py /tmp/wt/tests/ && cd /tmp/wt && timeout 600 python3 -m pytest -q tests/test_unrecorded_run.py tests/test_progress_card.py 2>&1 | grep -E "^(FAILED|E  .*51[4]|[0-9]+ (passed|failed))|AssertionError" | head -20; cd /home/runner/work/dokima/dokima; sed -n 1,80p .github/workflows/agent.yml | head -0; git diff e75f116 -- .github/workflows/agent.yml | head -60
```

> E       AssertionError: 514.1: the run died before its record, and its live card still stands, never turned into a record:
> tests/test_unrecorded_run.py:123: AssertionError
> E       AssertionError: 514.2: the run died before its record, and the card ended at None (column, Needs you), expected ('Plan', True)
> tests/test_unrecorded_run.py:148: AssertionError
> E           AssertionError: 514.3 (planner ended): /autopilot start started [], expected [('planner', '57')]; its comments: ['#57 and every issue under it were already on autopilot. No stage was started.\n']
> tests/test_unrecorded_run.py:186: AssertionError
> FAILED tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_gets_a_failed_record_linking_the_run - AssertionError: 514.1: the run died before its record, and its live card still stands, never turned into a record:
> FAILED tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_shows_needs_you - AssertionError: 514.2: the run died before its record, and the card ended at None (column, Needs you), expected ('Plan', True)
> FAILED tests/test_unrecorded_run.py::test_autopilot_start_restarts_the_stage_whose_run_ended_unrecorded - AssertionError: 514.3 (planner ended): /autopilot start started [], expected [('planner', '57')]; its comments: ['#57 and every issue under it were already on autopilot. No stage was started.\n']
> 3 failed, 5 passed in 13.23s
> diff --git a/.github/workflows/agent.yml b/.github/workflows/agent.yml
> index f7b1452..9f19a29 100644
> --- 

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner changed the older one-job check so a second job may run after the run fails."],
  "decided": ["The second job must wait for the run and start only when it failed.", "The three criteria and their tests stay as approved."],
  "open": []},
 "verdict": "approve",
 "summary": "The fixed test still keeps a second job off the card while the run goes; the plan is unchanged otherwise.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.1"},
  {"ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.2"},
  {"ask": "`/autopilot start` on an issue whose last run is finished but unrecorded starts the next stage instead of saying nothing started.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.3"}
 ],
 "behaviors": [
  {"criterion": "514.1", "one_behavior": true, "why": "One result: a failed record that links the run."},
  {"criterion": "514.2", "one_behavior": true, "why": "One result: the card shows Needs you."},
  {"criterion": "514.3", "one_behavior": true, "why": "One action, one result: autopilot start restarts the dead run's stage."}
 ],
 "tests": [
  {"test": "tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_gets_a_failed_record_linking_the_run", "only_its_behavior": true, "why": "Fails on main: the live card is never turned into a record."},
  {"test": "tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_shows_needs_you", "only_its_behavior": true, "why": "Fails on main: the card never reaches Plan with Needs you."},
  {"test": "tests/test_unrecorded_run.py::test_autopilot_sta
```

> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

**Agent:** Fixing one line that runs over its word cap, then re-running the check.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner changed the older one-job check so a second job may run after the run fails./The planner let the one-job check allow a second job after a failed run./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 514 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK; git worktree remove --force /tmp/wt 2>/dev/null; true
```

> OK

**Agent:** I approved the plan. The review is at `/tmp/dokima-out/review.json` and passes both checks.

- **What changed:** the planner only rewrote the older check that said the run machine must be the only job. It now lets a second job exist if that job waits for the run and starts only when the run failed. So nothing else can update the card while a run is still going. The three criteria and their tests are the same as the ones approved earlier.
- **The new tests:** with the branch's tests on main's code, all three fail because the feature is missing:
  - 514.1: the live card stays up and is never turned into a record.
  - 514.2: the card never ends in Plan with Needs you.
  - 514.3: `/autopilot start` still answers "No stage was started".
- **The changed check:** it still passes on main, which has only the one job.
- **On this branch:** `test_unrecorded_run.py` and `test_progress_card.py` all pass (8 tests), because the branch already has the worker's code. The worker's new job meets the changed check.
- **Asks:** both asks in [#514](https://github.com/dokima-dev/dokima/issues/514) (dead runs leave the issue looking busy) are covered by criteria. Each criterion is one behavior. There were no open blockers to answer.
- **The plan's two questions:** you settled them earlier by saying `/work` on the planner's assumptions. The criteria haven't changed since, so the worker should start next without waiting for you.

One small catch: the changed check looks for the exact wording `needs.run.result == 'failure'`. A second job that tests for failure another way would fail it even if it behaved correctly. I didn't block on that.

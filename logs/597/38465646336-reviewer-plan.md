# reviewer (plan) for #597

Run: https://github.com/dokima-dev/dokima/actions/runs/38465646336

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-planner.json
> 03-reviewer-plan.json
> 04-planner.json
> # Issue #597: Tests run only at the merge gate, after code review
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 595, 596 -->
> <!-- dokima-blocking: {"blocked_by": [595, 596], "blocks": [], "loop": []} -->
> Worker check, code review and merge gate run in turn, so no test races the review or a merge.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/595
> - https://github.com/dokima-dev/dokima/issues/596
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/582
> - https://github.com/dokima-dev/dokima/issues/599
> - https://github.com/dokima-dev/dokima/issues/600
> - https://github.com/dokima-dev/dokima/issues/601
> 
> 
> **User story:** Tests, code review and merge never overlap on a pull request, so no step patches another's clash.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" w

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/03-reviewer-plan.json','in/04-planner.json']:
  d=json.load(open(f)); print(f); print(json.dumps(d,indent=1)[:6000])
"; cat parent.json | head -c 3000
```

> in/03-reviewer-plan.json
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38464935000",
>  "commit_before": "1d9f7c9230ab4aa73e6b5adbcae59d4c8d28af89",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 69349,
>   "turns": 9,
>   "cost_usd": 0.5599844,
>   "tokens_in": 433427,
>   "tokens_out": 5711
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/597/38464935000-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38464935000",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote three tests, one per criterion, and changed no workflow or code.",
>     "The planner loosened one older test so the full suite may skip draft pull requests."
>    ],
>    "decided": [
>     "Tests move from pull request opening to the merge gate, after code review."
>    ],
>    "open": [
>     "The owner agreed to close #599 as a duplicate of this issue."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan keeps all three asks, and each test fails today for the right reason.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "Code review: starts only after the worker's check passed.",
>     "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718",
>     "criterion": "597.1"
>    },
>    {
>     "ask": "no test run racing the code review",
>     "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718",
>     "criterion": "597.2"
>    },
>    {
>     "ask": 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git diff main --stat; timeout 900 python3 -m pytest -q tests/test_one_order.py 2>&1 | grep -E "^(E  .*[0-9]{3}\.[0-9]|FAILED|PASSED|[0-9]+ (passed|failed))" | head -30; timeout 600 python3 -m pytest -q tests/test_fix_pr.py 2>&1 | tail -3
```

> 1d9f7c9 planner for #597 (run 38462971475)
> a9701dc The planner starts from its branch with main merged in (#607)
> 9748f5a Merge gate tests the combined code, then the owner approves (#606)
>  tests/test_fix_pr.py    |   7 +-
>  tests/test_one_order.py | 368 ++++++++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 372 insertions(+), 3 deletions(-)
> E       AssertionError: 597.1: the code review started though the planner's own test still fails on the worker's code: the worker had edited that test, and its check ran on the edited copy
> E       AssertionError: 597.2: tests started on the pull request while its code review ran: [('acceptance-criteria.yml', '57.1 · a', 'opened'), ('acceptance-criteria.yml', 'Acceptance criteria', 'opened'), ('acceptance-criteria.yml', 'Acceptance criteria', 'synchronize'), ('acceptance-criteria.yml', 'list acceptance criteria', 'opened'), ('acceptance-criteria.yml', 'list acceptance criteria', 'synchronize'), ('full-suite.yml', 'all tests', 'opened'), ('full-suite.yml', 'all tests', 'synchronize')]
> E       AssertionError: 597.3: autopilot merged a head whose required checks were only skipped, before any test ran: [{'head': 'a1a1a1a', 'check': 'all tests', 'runs': [{'name': 'all tests', 'head_sha': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'status': 'completed', 'conclusion': 'skipped'}]}, {'head': 'a1a1a1a', 'check': 'Acceptance criteria', 'runs': [{'name': 'Acceptance criteria', 'head_sha': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'status

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner kept the same three criteria and tests after the owner's answer."],
  "decided": ["The owner's answer confirms the planner's reading: #599 closes as a duplicate."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan keeps all three asks, the owner's answer matches its reading, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Code review: starts only after the worker's check passed.", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "597.1"},
  {"ask": "no test run racing the code review", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "597.2"},
  {"ask": "no merge tried while tests still run", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "597.3"},
  {"ask": "Yes: close #599 as a duplicate of this issue.", "source": "https://github.com/dokima-dev/dokima/issues/597", "criterion": "597.1"}],
 "behaviors": [
  {"criterion": "597.1", "one_behavior": true, "why": "One trigger: the review starts only after the plan's tests passed."},
  {"criterion": "597.2", "one_behavior": true, "why": "One result: no test run starts during the review."},
  {"criterion": "597.3", "one_behavior": true, "why": "One result: no merge while tests run."}],
 "edge_cases": [
  {"criterion": "597.1", "cut": [], "missing": []},
  {"criterion": "597.2", "cut": [], "missing": []},
  {"criterion": "597.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_one_order.py::test_code_review_starts_only_after_the_workers_test_check_passed", "only_its_behavior": true, "why": "Fails today: the review starts though the worker edited the planner's test."},
  {"test": "tests/test_one_order.py::test_no_test_run_starts_while_the_code_review_runs", "only_its_behavior": true, "why":
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)

`5. Bash`
```
sed -i 's/"summary": "The plan keeps all three asks, the owner.s answer matches its reading, and each test fails today for the right reason."/"summary": "The plan keeps all three asks, matches the owner'"'"'s answer, and each test fails today for the right reason."/' /tmp/dokima-out/review.json && grep summary /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 597 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> "summary": "The plan keeps all three asks, matches the owner's answer, and each test fails today for the right reason.",
> rc=0

**Agent:** I approved the plan for [#597](https://github.com/dokima-dev/dokima/issues/597) (tests run only at the merge gate, after code review). The hand-back is in `/tmp/dokima-out/review.json`, and both of code's checks on it pass.

- **What changed since the last plan review:** only your answer to the planner's question, "close #599 as a duplicate of this issue." That is the reading the plan already assumed. The planner kept the same three criteria and tests.
- **Your asks:** the plan carries all three from [#582](https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718) (worker, review, merge gate, approval in one fixed order), plus your answer about [#599](https://github.com/dokima-dev/dokima/issues/599) (the check running before the planner's tests are restored). None is missing.
- **Tests:** I ran them. All three new tests fail today for the right reason:
  - The code review starts even though the worker edited the planner's test.
  - The full suite and criteria checks start when a pull request opens or gets new commits.
  - Autopilot merges a commit whose checks were all skipped.
- **The older test the planner loosened** (`tests/test_fix_pr.py`) still passes.

There are no blockers or questions. Next, `/work` starts the build.

One thing outside the plan: the planner can't close issues, so closing [#599](https://github.com/dokima-dev/dokima/issues/599) as a duplicate still has to be done by you or by code.

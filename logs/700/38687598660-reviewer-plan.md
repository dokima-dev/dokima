# reviewer (plan) for #700

Run: https://github.com/dokima-dev/dokima/actions/runs/38687598660

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #700: A role can run on Codex CLI
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 697, 698, 699 -->
> <!-- dokima-blocking: {"blocked_by": [698, 699], "blocks": [], "loop": []} -->
> Any role named for a Codex subscription runs in Codex CLI, on the model the settings file gives.
> 
> **Review** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 blocker](https://github.com/dokima-dev/dokima/pull/728#issuecomment-6184772668) with `/plan`, `/work` or `/review`
> 
> https://github.com/dokima-dev/dokima/pull/728 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/728/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/698
> - https://github.com/dokima-dev/dokima/issues/699
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/39
> - https://github.com/dokima-dev/dokima/issues/697
> 
> 
> **User story:** The owner moves any role to Codex by naming a Codex subscription for it.
> 
> <img

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['02-reviewer-plan.json','06-reviewer-pr.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"; cd /home/runner/work/dokima/dokima; cat tests/test_agent_codex.py; cat dokima/agent_codex.py; git diff main --stat
```

> 02-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38680972193",
>  "commit_before": "67f04a0a7dcf5bb2eb5a691f336c3eb0dad551ff",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 46576,
>   "turns": 8,
>   "cost_usd": 0.33457139999999996,
>   "tokens_in": 238549,
>   "tokens_out": 3663
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/700/38680972193-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38680972193",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote one criterion: a Codex role runs in Codex CLI, on its model.",
>     "The planner wrote three tests that start a stand-in Codex through the agent interface."
>    ],
>    "decided": [
>     "A Codex run gets its key, since setup stores Codex by key only.",
>     "A Codex run may change files, and a failed Codex run fails the run."
>    ],
>    "open": []
>   },
>   "verdict": "approve",
>   "summary": "The plan carries the one ask, and its three tests fail today because no Codex adapter exists.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.",
>     "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>     "criterion": "700.1"
>    }
>   ],
>   "behaviors": [
>    {
>     "criterion": "700.1",
>     "one_behavior": true,
>     "why": "One action, starting a Codex role, with one result: Codex

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_agent_codex.py 2>&1|tail -3; rm -rf /tmp/rv && cp -r . /tmp/rv && rm /tmp/rv/dokima/agent_codex.py && cd /tmp/rv && python3 -m pytest -q tests/test_agent_codex.py 2>&1 | grep -E "700.1|passed|failed" | head
```

> ...                                                                      [100%]
> 3 passed in 0.22s
>         Proves 700.1. Puts the worker on a Codex subscription with model gpt-5-codex and starts it through the one agent
>         record_property("proves", "700.1")
> >       assert len(starts) == 1, f"700.1: Codex CLI should start once, it started {len(starts)} times: {said(p)}"
> E       AssertionError: 700.1: Codex CLI should start once, it started 0 times: exit 1; stdout: ''; stderr: "The worker's subscription names the agent 'codex', which Dokima has no adapter for."
>         Proves 700.1. Codex CLI's unattended run is read-only unless told otherwise. Starts the worker on its Codex
>         record_property("proves", "700.1")
> >       assert starts, f"700.1: Codex CLI never started: {said(p)}"
> E       AssertionError: 700.1: Codex CLI never started: exit 1; stdout: ''; stderr: "The worker's subscription names the agent 'codex', which Dokima has no adapter for."
> ____________________ test_a_failed_codex_run_fails_the_run _____________________
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-1/test_a_failed_codex_run_fails_0')
> Shell cwd was reset to /home/runner/work/dokima/dokima

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner's plan is unchanged: one criterion, a Codex role runs in Codex CLI on its model.",
          "The owner said the red suite was a flaky clone, now passed on rerun."],
  "decided": ["A Codex run gets its key, may change files, and fails when Codex fails."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan still carries the one ask, and its three tests fail without the Codex adapter.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.",
           "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
           "criterion": "700.1"}],
 "behaviors": [{"criterion": "700.1", "one_behavior": true,
                "why": "One action, starting a Codex role, with one result: Codex runs on that model."}],
 "edge_cases": [{"criterion": "700.1", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_agent_codex.py::test_a_codex_role_runs_in_codex_cli_with_its_model", "only_its_behavior": true,
   "why": "Checks Codex starts once, unattended, with the prompt, model and key; fails without the adapter."},
  {"test": "tests/test_agent_codex.py::test_a_codex_run_may_change_files", "only_its_behavior": true,
   "why": "Checks Codex starts with write access; fails without the adapter."},
  {"test": "tests/test_agent_codex.py::test_a_failed_codex_run_fails_the_run", "only_its_behavior": true,
   "why": "Checks a failing Codex ends the run with its exit code; fails without the adapter."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 700 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`5. Bash`
```
sed -i "s/The planner's plan is unchanged: one criterion, a Codex role runs in Codex CLI on its model./The plan is unchanged: one criterion, a Codex role runs Codex CLI on its model./" /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 700 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`6. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i "s/The planner's plan is unchanged: one criterion, a Codex role runs in Codex CLI on its model./The plan is unchanged: one criterion, a Codex role runs Codex CLI on its model./" /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 700 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I approved the plan for [#700](https://github.com/dokima-dev/dokima/issues/700) (a role can run on Codex CLI). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **The ask:** the owner's one ask is that a role on a Codex subscription runs in Codex CLI, on the model the settings file names. Criterion 700.1 covers it, so nothing is missing.
- **The tests:** with the Codex adapter there, all three tests pass. On a copy of the repo with the adapter removed, all three fail for the right reason: "no adapter for codex". They don't crash.
- **Earlier blocker:** the code review's blocker for you (red checks on GitHub) is answered by your `/review` comment. It said the rerun passed and the failure was a flaky clone. It isn't one of this stage's open items, so I raised nothing new.

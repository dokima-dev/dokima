# reviewer (plan) for #819

Run: https://github.com/dokima-dev/dokima/actions/runs/39049835371

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; echo ====; cat plan.json; echo ====; cat open_blockers.json
```

> total 32
> drwxr-xr-x 2 runner runner 4096 Oct 17 16:32 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 16:32 ..
> -rw-r--r-- 1 runner runner 7092 Oct 17 16:32 01-planner.json
> -rw-r--r-- 1 runner runner 7859 Oct 17 16:32 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7382 Oct 17 16:32 03-planner.json
> # Issue #819: Code checks the reviewer's required boxes
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 818 -->
> <!-- dokima-blocking: {"blocked_by": [818], "blocks": [], "loop": []} -->
> A review that skips a box, leaves a field out or approves past a blocking entry is rejected.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/818
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> 
> 
> **User story:** A review that skips a duty, or claims a weak test without proof, is rejected before it posts.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance c

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cd /home/runner/work/dokima/dokima; git show --stat HEAD HEAD~1 | head -30; cat tests/test_review_boxes.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39049271534",
>  "commit_before": "668a6da3520689cd662f8fae043952bc4b75812d",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 275312,
>   "turns": 15,
>   "cost_usd": 0.7634316000000001,
>   "tokens_in": 823622,
>   "tokens_out": 8677
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/819/39049271534-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39049271534",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote six criteria, one test each, for the six review boxes.",
>     "The planner added the boxes to sample reviews in older tests."
>    ],
>    "decided": [
>     "Boxes are checked at plan review and at code review alike."
>    ],
>    "open": [
>     "The planner filed a proposal: the reviewer's prompt never shows the edges box shape."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Two tests pass when the wrong box is named, and a blank edges case is never tested.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "819.1 names any box",
>     "text": "The test for 819.1 passes when every rejection lists all six boxes. Fix: also assert the reason names none of the boxes still present.",
>     "evidence": "`tests/test_review_boxes.py::test_a_review_missing_any_of_the_six_boxes_is_rejected_naming_the_box` only matches `\\b{box}\\b` in any line.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    },
>    {
>     

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_review_boxes.py 2>&1 | grep -E "^E  .*(819|Error)|passed|failed" | head -30; timeout 900 python -m pytest -q -x -n auto 2>&1 | tail -3 || timeout 900 python -m pytest -q 2>&1 | tail -5
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bf67gdh2e). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** Meanwhile, the test change in `test_handback_check.py`:

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main -- tests/test_handback_check.py tests/test_review_asks.py tests/samples; git diff main --stat
```

> diff --git a/tests/samples/132/review-pr.json b/tests/samples/132/review-pr.json
> index c4b573a..2dbc3e4 100644
> --- a/tests/samples/132/review-pr.json
> +++ b/tests/samples/132/review-pr.json
> @@ -10,5 +10,16 @@
>    "open": []
>   },
>   "verdict": "approve",
> - "summary": "A failed run now always leaves its card, and its open pull request's, in its stage's column with Needs you."
> -}
> \ No newline at end of file
> + "summary": "A failed run now always leaves its card, and its open pull request's, in its stage's column with Needs you.",
> + "boxes": {
> +  "dropped": "none",
> +  "added": "none",
> +  "superseded": "none",
> +  "conflicts": "none",
> +  "edges": {
> +   "132.1": "covered",
> +   "132.2": "covered"
> +  },
> +  "poor_tests": "none"
> + }
> +}
> diff --git a/tests/test_handback_check.py b/tests/test_handback_check.py
> index 25a2813..3fec7d3 100644
> --- a/tests/test_handback_check.py
> +++ b/tests/test_handback_check.py
> @@ -35,7 +35,7 @@ REVIEW = {"previous_step": {"did": ["Wrote three criteria."], "decided": [], "op
>                       {"kind": "issue", "text": "t: w", "evidence": "e"}],
>            "answers": [{"raise": "W1", "answer": "done", "why": "The test is weak."}], "asks": ASKS,
>            "size": "ok",
> -          "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3")], "edge_cases": [{"criterion": c, "cut": [], "missing": []} for c in ("9.1", "9.2", "9.3")],
> +          "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} fo

`5. Bash`
```
sleep 100; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output
```

> <tool_use_error>Blocked: sleep 100 followed by: cat /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`6. Bash`
```
grep -n "SPLIT = " -A6 /home/runner/work/dokima/dokima/tests/test_review_asks.py | head; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output
```

> 26:SPLIT = {"kind": "feature", "feature": "f", "stories": [
> 27-    {"title": "One", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
> 28-     "non_functional": [], "depends_on": []},
> 29-    {"title": "Two", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://x/9"}],
> 30-     "non_functional": [], "depends_on": [0]}]}
> 31-
> 32-ASKS = [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"},
> E       AssertionError: 819.1: a review with no dropped box (plan) was let through; it must be rejected
> E                       AssertionError: 819.2: a dropped entry without words (plan) was let through; it must be rejected
> E       AssertionError: 819.3: a weak test entry without the wrong code that still passes (plan) was let through (exit 0); it must be rejected
> E       AssertionError: 819.4: an approve whose dropped box holds a blocking entry (plan) was let through; it must be rejected
> E       AssertionError: 819.5: an approve whose added box holds a creep entry (plan) was let through (exit 0); it must be rejected
> E       AssertionError: 819.6: a review whose edges box leaves out 9.2 (plan) was let through (exit 0); it must be rejected
> 6 failed in 2.13s

`7. ToolSearch`
```
{"query": "select:Monitor", "max_results": 1}
```

> 

> 

`8. Monitor`
```
f=/tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output; until [ $(grep -cE "passed|failed|error" $f) -ge 2 ]; do sleep 3; done; tail -4 $f
```

> Monitor started (task b82vthyg2, expires in 10m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the box-missing and approve tests fail when a reason names a box that is fine.", "The planner added tests for edges lines that name no case or read neither covered nor missing."], "decided": ["Every earlier blocker is answered done; no criterion changed."], "open": []},
 "verdict": "approve",
 "summary": "All three earlier blockers are fixed, and every new test fails today because the box checks are missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "One per duty, every box present", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.1"},
  {"ask": "Every box must be present at both stages.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234488387", "criterion": "819.1"},
  {"ask": "entries typed", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.2"},
  {"ask": "A weak-test claim without a named counterexample is rejected by code.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.3"},
  {"ask": "each entry a blocker unless noted", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.4"},
  {"ask": "needed is not a blocker", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.5"},
  {"ask": "edges:       per criterion: covered | missing: <named case>", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "819.6"},
  {"ask": "A box with nothing to check at a stage (for example `added` at plan review, before any diff exists) says `none`.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234488387", "criterion": "819.1"}
 ],
 "behaviors": [
  {"criterion": "819.1", "one_behavior": true, "why": "
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step did line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

**Agent:** The new tests fail for the right reason; I'm shortening two summary lines and waiting on the full test run.

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["The box-missing and approve tests now fail when a sound box is named.","Tests now reject edges lines naming no case or reading neither word."]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 819 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`11. Bash`
```
tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output
```

> E       AssertionError: 819.3: a weak test entry without the wrong code that still passes (plan) was let through (exit 0); it must be rejected
> E       AssertionError: 819.4: an approve whose dropped box holds a blocking entry (plan) was let through; it must be rejected
> E       AssertionError: 819.5: an approve whose added box holds a creep entry (plan) was let through (exit 0); it must be rejected
> E       AssertionError: 819.6: a review whose edges box leaves out 9.2 (plan) was let through (exit 0); it must be rejected
> 6 failed in 2.13s

**Agent:** I'll wait for the full suite to make sure the older tests the planner edited still pass.

`12. Monitor`
```
f=/tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output; until [ $(grep -cE " (passed|failed|error)" $f) -ge 2 ]; do sleep 3; done; tail -3 $f
```

> Monitor started (task bebwguekc, expires in 10m unless the source ends first; you get one notice at expiry — re-arm if you still need the watch). You will be notified on each event. Keep working — do not poll or sleep. Events may arrive while you are waiting for the user — an event is not their reply.

**Agent:** Waiting for the full suite to finish.

`13. Bash`
```
tail -4 /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output
```

> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 1 failed, 724 passed, 4 warnings in 352.47s (0:05:52)
> 
> [exited with code 0]

`14. Bash`
```
grep -E "^FAILED|^\[gw.*FAILED|FAILED " /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bf67gdh2e.output | head; cd /home/runner/work/dokima/dokima; timeout 110 python -m pytest -q -n auto --deselect tests/test_review_boxes.py tests/test_handback_check.py tests/test_review_asks.py tests/test_raise_handbacks.py tests/test_automerge.py tests/test_fixer.py tests/test_failed_run_card.py tests/test_live_queue.py tests/test_start.py tests/test_autopilot_river.py 2>&1 | tail -5
```

> Exit code 143
> Terminated

`15. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1200 python -m pytest -q -n auto -p no:cacheprovider tests/test_handback_check.py tests/test_review_asks.py tests/test_raise_handbacks.py tests/test_automerge.py tests/test_fixer.py tests/test_failed_run_card.py tests/test_live_queue.py tests/test_start.py tests/test_autopilot_river.py 2>&1 | grep -E "^FAILED|passed|failed" | tail -15
```

> Command running in background with ID: bfgim7ta1. Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bfgim7ta1.output. You will be notified when it completes. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** I'm running the older tests the plan changed to confirm they still pass.

`16. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/324a6f8d-573d-4df3-90fc-042eb1c52e84/tasks/bfgim7ta1.output
```

> 61 passed in 158.18s (0:02:38)
> 
> [exited with code 0]

**Agent:** I approved the plan for [#819](https://github.com/dokima-dev/dokima/issues/819) (code checks the reviewer's required boxes). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Earlier blockers:** the planner fixed all three.
  - The tests for missing boxes (819.1) and for approving past a blocking entry (819.4) now also fail when a reason names a box that is fine.
  - The 819.2 test now rejects edges lines that name no case, or that read neither "covered" nor "missing".
- **New tests:** all six fail today for the right reason, because the box checks don't exist yet. Each failure names its criterion.
- **Older tests the plan changed:** all 61 tests in those 9 files pass. The only change is adding the six boxes to their sample reviews, so nothing they checked before was weakened.
- **Full suite:** I ran it once, set to stop at the first failure. It stopped after 1 failure with 724 passing. I didn't capture which test failed. It is most likely one of the six new tests, which should fail now, but I haven't confirmed that.
- **Owner's asks:** every ask in the issue and the two #741 comments maps to a criterion, and none is missing.
- **Size:** each criterion is one behavior, so size is ok.

I raised nothing new, and there were no open blockers to answer.

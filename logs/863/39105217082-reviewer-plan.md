# reviewer (plan) for #863

Run: https://github.com/dokima-dev/dokima/actions/runs/39105217082

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #863: Hotfix issues build from their text and get reviewed
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [864], "loop": []} -->
> An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/864
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/748
> - https://github.com/dokima-dev/dokima/issues/857
> 
> 
> **User story:** A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a code owner says work on an issue labeled hotfix, the worker starts with no plan.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-863/tests/test_hotfix.py#L239"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
d=json.load(open('02-reviewer-plan.json'))
print(json.dumps(d,indent=1)[:9000])
"; python3 -c "
import json
d=json.load(open('03-planner.json'))
print(list(d.keys())); print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])
"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39104711675",
>  "commit_before": "2a74b9455f2cd1103b65a5b5dd04f545ce62f4ae",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 113200,
>   "turns": 11,
>   "cost_usd": 0.6879514,
>   "tokens_in": 538193,
>   "tokens_out": 7790
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/863/39104711675-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39104711675",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote ten criteria for the hotfix lane, each with one test.",
>     "All ten tests fail today because a hotfix still needs a plan."
>    ],
>    "decided": [
>     "The hotfix worker and its code review read the issue text, no plan."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "Two gaps: no test shows failing tests stop a hotfix, and the any-repo prompt rule has no criterion.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "863.7: gate unproven",
>     "text": "The test for 863.7 only runs with green checks, so a hotfix that skips its tests still passes. Add a red-check run beside it that must not pass the gate.",
>     "evidence": "`tests/test_hotfix.py::test_an_approved_hotfix_passes_the_merge_gate_like_any_pull_request`; the fake gh always answers check runs `success`.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    },
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "No c

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 2a74b94 98e53c1 --stat; git diff 2a74b94 98e53c1 -- tests/ | head -400
```

> tests/test_hotfix.py | 110 +++++++++++++++++++++++++++++++++------------------
>  1 file changed, 71 insertions(+), 39 deletions(-)
> diff --git a/tests/test_hotfix.py b/tests/test_hotfix.py
> index 468b0ff..c0503ff 100644
> --- a/tests/test_hotfix.py
> +++ b/tests/test_hotfix.py
> @@ -5,7 +5,7 @@ test_start.py, with the fake GitHub of test_autopilot_close.py (labels, sub-issu
>  signals). A thin layer in front of that fake also answers what a hotfix's run needs: `gh pr create` (noted, and the
>  pull request #60 exists from then on), `gh run download` (a session log of the worker's run), the merge gate's reads
>  of pull request #60 (its head commit, its draft flag, `gh pr ready`), main's branch rule (it requires the `all tests`
> -check) and the check runs on the head commit (all green). A `--jq` filter on an issue read is applied with jq.
> +check) and the check runs on the head commit (green, or red when the test asks). A `--jq` filter on an issue read is applied with jq.
>  
>  The issue is #57 in repo o/r, labeled `hotfix`, its text the owner's ask: ASK. Main holds app.py (the title with a
>  typo), lib/ (nothing yet) and an older test, tests/test_old.py. The stand-in agent keeps a copy of its pack and its
> @@ -18,6 +18,7 @@ The autopilot test runs the close and command workflows on test_autopilot_close.
>  """
>  import json
>  import os
> +import re
>  import subprocess
>  import sys
>  
> @@ -25,6 +26,7 @@ sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
>  import test_autopilot_close as tac  # noqa

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_hotfix.py 2>&1 | grep -E "^(FAILED|ERROR|E  .*86[0-9]\.|[0-9]+ (passed|failed))|AssertionError: 863" | head -40
```

> E       AssertionError: 863.1: `/work` on a hotfix issue with no plan did not start its worker; result failure, failed step 'Starting branch':
> E       AssertionError: 863.2 (close): the unblocked hotfix #101 did not get exactly one worker; workers: []
> E       AssertionError: 863.3: the hotfix worker never started; result failure, failed step 'Starting branch':
> E       AssertionError: 863.4: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E       AssertionError: 863.5: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E       AssertionError: 863.6: code review of the hotfix never started; result failure, failed step 'Build the starting pack':
> E       AssertionError: 863.7: the approving hotfix review did not post one passed record: [('not-started', {'passed': False, 'problems': ['No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.']})]; result failure, failed step 'Build the starting pack':
> E       AssertionError: 863.8: the blocking hotfix review did not post one passed record; result failure, failed step 'Build the starting pack':
> E       AssertionError: 863.9: code review of the hotfix never started; result failure, failed step 'Build the starting pack':
> E           AssertionError: 863.10: the hotfix worker never started with the hotfix lane's prompt; result failure, failed step 'Starting branch':
> FAILED tests/test_hotfix.py::test_work_on_a_hotfix_starts_its_worker_with_no

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "GATE_FAILED" dokima tests | head; grep -rn "dokima/\|rules/\|dokima-dev\|agent.yml" dokima/roles/worker.md dokima/roles/reviewer.md | head
```

> dokima/agent_records.py:23:GATE_FAILED = "The merge gate failed"
> dokima/agent_records.py:191:    return (is_record(c, "reviewer", "pr") or QUEUE_FAILED in body) and f"**Next:** {GATE_FAILED}:" in body
> dokima/agent_roles.py:490:                        step = ("stop", f"{GATE_FAILED}: {why}. {blocks} blocks in a row without agreement. Your call: "
> dokima/agent_roles.py:493:                        step = ("start", "worker", "", "", f"{GATE_FAILED}: {why}.")
> dokima/agent_roles.py:730:    with_next, models_used, first_sentence, GATE_FAILED)
> dokima/agent_autopilot.py:974:                        f"{tag}\n{why}\n\n**Next:** {GATE_FAILED}: the worker fixes the failing tests.")
> dokima/agent_autopilot.py:981:                    f"{tag}\n{why}\n\n**Next:** {GATE_FAILED}: {mention} {stop}")
> dokima/agent_autopilot.py:1035:    filled, first_sentence, GATE_FAILED, QUEUE_FAILED)
> tests/test_hotfix.py:29:from dokima.agent_records import GATE_FAILED  # noqa: E402
> tests/test_hotfix.py:371:    assert any(GATE_FAILED in b for b in said), \

**Agent:** Every test fails for the right reason, and both earlier blockers are fixed. Writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/750"
C=I+"#issuecomment-6246479912"
T="tests/test_hotfix.py::"
tests={"863.1":"test_work_on_a_hotfix_starts_its_worker_with_no_plan","863.2":"test_autopilot_starts_a_hotfix_worker_instead_of_its_planner","863.3":"test_a_hotfix_worker_pack_gives_the_issue_text_as_the_ask","863.4":"test_a_hotfix_worker_change_stays_on_the_pull_request","863.5":"test_a_finished_hotfix_worker_starts_code_review_on_its_pull_request","863.6":"test_code_review_of_a_hotfix_gets_the_issue_text_as_the_ask","863.7":"test_an_approved_hotfix_passes_the_merge_gate_like_any_pull_request","863.8":"test_code_review_sends_a_too_big_hotfix_to_the_planner","863.9":"test_a_hotfix_sent_back_to_planning_says_why_on_the_issue","863.10":"test_hotfix_prompts_name_nothing_from_dokimas_own_repo"}
beh={"863.1":"Owner's work starts a hotfix worker.","863.2":"Autopilot starts the worker instead of the planner.","863.3":"The worker's pack holds the issue text as the ask.","863.4":"Nothing the hotfix worker changes is dropped.","863.5":"Code review starts after the worker.","863.6":"The review's pack holds the issue text as the ask.","863.7":"The merge gate judges a hotfix as any pull request.","863.8":"A too-big hotfix starts the planner.","863.9":"The issue gets a comment saying why.","863.10":"Hotfix prompts name nothing from Dokima's own repo."}
tw={"863.1":"Runs the workflow; unlabeled case beside it.","863.2":"Close and autopilot start, with blocked and unlabeled siblings.","863.3":"Reads the pack the agent found.","863.4":"Reads the pushed branch for code and test changes.","863.5":"Checks the pull request and the review signal.","863.6":"Reads the review pack.","863.7":"Green check passes the gate; red check fails it.","863.8":"Checks the planner signal and the replanned worker.","863.9":"Checks the issue comment text.","863.10":"Scans both real prompts for Dokima's own names."}
r={"pre
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#863](https://github.com/dokima-dev/dokima/issues/863) (hotfix issues build from their text and get reviewed). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Earlier blockers:** both from my last review are fixed.
  - **Merge gate:** the gate test now has a second run where the required check fails. In that run the gate must fail and the worker must start again.
  - **Prompts:** new criterion 863.10 keeps both hotfix prompts free of anything from Dokima's own repo. Its test reads the real worker and reviewer prompts.
- **Tests today:** I ran all 10 tests on the branch and all 10 fail for the right reason: a hotfix still needs a plan, so the worker or review never starts. None fails on a crash or a bad path.
- **Owner's asks:** each of the 10 asks from [#750](https://github.com/dokima-dev/dokima/issues/750) (hotfix label builds a small fix without planning) and its comment matches a criterion. None is missing.
- **One change to note:** the planner merged "worker changes a code file" and "worker changes a test" into one criterion, 863.4. I counted it as one behavior, since nothing the worker changes gets dropped. Its single test checks all four kinds of change.

I raised no new blockers or questions.

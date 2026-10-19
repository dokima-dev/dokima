# reviewer (plan) for #912

Run: https://github.com/dokima-dev/dokima/actions/runs/39268820898

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #912: An agent run's work is lost when its branch moved during the run
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A run whose branch or logs branch moved while it ran catches up and keeps its work and log.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/912#issuecomment-6269268491) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/442
> - https://github.com/dokima-dev/dokima/issues/825
> 
> 
> **User story:** A run whose branch moved while it worked still saves its work and log, and names any clashing files.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the run's branch moved during the run, the run's commit still ends on top of it.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-912/tests/test_push_

`2. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python -m pytest -q tests/test_push_moved_remote.py 2>&1 | tail -15; cat /tmp/pack/in/02-planner.json | head -c 1500
```

> +         'POST',
>   +         'repos/o/r/dispatches',
>   +         '-f',
>   +         'event_type=dokima-next',
>   +         '-f',
>   +         'client_payload[role]=planner',
>   +         '-f',
>   +         'client_payload[stage]=plan',
>   +         '-f',
>   +         'client_payload[issue]=57',
>   +         '-f',
>   +         'client_payload[card]=5002',
>   +     ],
>   + ]
> 10 failed in 15.34s
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39266741003",
>  "commit_before": "5695a04e7410571b3dc1bb3f11295a78131e5c35",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 723676,
>   "turns": 48,
>   "cost_usd": 3.055097800000001,
>   "tokens_in": 4739822,
>   "tokens_out": 50139
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/912/39266741003-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39266741003",
>  "handback": {
>   "kind": "user_story",
>   "title": "A run keeps its work when its branch moved",
>   "summary": "A run whose branch or logs branch moved while it ran catches up and keeps its work and log.",
>   "user_story": "A run whose branch moved while it worked still saves its work and log, and names any clashing files.",
>   "acceptance_criteria": [
>    {
>     "text": "When the run's branch moved during the run, the run's commit still ends on top of it.",
>     "words": "When a push of the run's branch or of `logs` is rejected because the remote moved, fetch, rebase the run's own commits onto the new tip, and pu

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote four criteria and ten tests for pushes that catch up after the branch moved."],
  "decided": ["The plan changes the agent workflow and holds the next run until its pushes land."],
  "open": ["The planner asks the owner whether the workflow may change.", "The planner asks whether a failed push should start nothing."]},
 "verdict": "block",
 "summary": "The owner withdrew this ask as a wrong diagnosis and closed the issue; nothing here should be built.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Ask withdrawn",
   "text": "The owner said the race diagnosis was wrong and the real fix is #914, then closed this issue. All four criteria rest on the withdrawn ask. Smallest fix: drop the plan and build nothing here.",
   "evidence": "Owner comment of 2026-10-19T14:24:29Z on #912: \"Wrong diagnosis, mine... The real fix is 914.\""}
 ],
 "answers": [
  {"raise": "W1", "answer": "disagree", "why": "Moot: the owner withdrew the ask as a wrong diagnosis, so no workflow change is due here."}
 ],
 "asks": [
  {"ask": "When a push of the run's branch or of `logs` is rejected because the remote moved, fetch, rebase the run's own commits onto the new tip, and push again (a few tries).", "source": "https://github.com/dokima-dev/dokima/issues/912", "criterion": "912.1"},
  {"ask": "Only if the rebase conflicts does the run fail, and then the record names the conflicting files.", "source": "https://github.com/dokima-dev/dokima/issues/912", "criterion": "912.2"},
  {"ask": "the log push likewise", "source": "https://github.com/dokima-dev/dokima/issues/912", "criterion": "912.3"},
  {"ask": "The run that dispatches the next agent does so only after its own pushes have landed.", "source": "https://github.com/dokima-dev/dokima/issues/912", "criterion": "912.4"}
 ],
 "behaviors": [
  {"criterion": "912.1", "one_behavior": true, "why": "One result: the run's
```

> Exit code 1
> raise 1's text holds 35 words, over its cap of 30: cut 5, keep the facts
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="The owner called the race diagnosis wrong, named #914 as the real fix, and closed this issue. All four criteria rest on that withdrawn ask. Fix: drop the plan."
d['previous_step']['did'][0]="The planner wrote four criteria and ten tests for pushes catching up."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 912 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#912](https://github.com/dokima-dev/dokima/issues/912) (lost run work when the branch moved). The plan itself is sound, but you withdrew the ask after the planner wrote it, and the plan doesn't reflect that.

- **What you said:** in your comment of 14:24 today, you called the diagnosis wrong, named [#914](https://github.com/dokima-dev/dokima/issues/914) (branch check fails without credentials in a private repo) as the real fix, and closed this issue. That retires all four criteria.
- **Blocker for the planner:** drop the plan and build nothing here.
- **The worker's raise W1** (needs a workflow change): I disagreed. It's moot now that the ask is withdrawn.
- **The plan as written:** all four criteria are one behavior each and match your original words, with nothing dropped or added. All 10 new tests fail today because the feature is missing. On a live issue, it would have passed review.
- **The planner's two questions for you:** may the worker change the workflow file, and should a failed push start no next run. I left both unanswered; they no longer matter if the issue stays closed.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

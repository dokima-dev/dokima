# reviewer (plan) for #697

Run: https://github.com/dokima-dev/dokima/actions/runs/38664268406

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #697: Setup gathers and stores a subscription's inputs
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [698, 699], "loop": []} -->
> A setup command takes a subscription's inputs once and puts each where runs find it.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/698
> - https://github.com/dokima-dev/dokima/issues/699
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/700
> 
> 
> **User story:** The owner gives a subscription's inputs once; setup stores the key or sign-in and writes the settings file.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Setup lists the inputs a subscription needs: membership, region, sign-in or key, and model.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-697/tests/test_setup.py#L171"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokim

`2. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cat tests/test_setup.py; ls dokima/setup.py; python3 -m pytest -q tests/test_setup.py 2>&1 | tail -20
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38663937541",
>  "commit_before": "ac53770101a1ff7e183ba9a85c09f611e044c9a2",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 66438,
>   "turns": 9,
>   "cost_usd": 0.47355340000000007,
>   "tokens_in": 363084,
>   "tokens_out": 6386
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/697/38663937541-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38663937541",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote six criteria and ten tests for a new setup command.",
>     "All ten tests fail today because the setup command does not exist yet."
>    ],
>    "decided": [
>     "A sign-in is stored as one packed secret that a run can unpack.",
>     "The settings file holds each secret's name, never the key."
>    ],
>    "open": [
>     "Nothing was raised for the owner."
>    ]
>   },
>   "verdict": "block",
>   "summary": "One test for the subscription criterion also checks role lines, which belong to the roles criterion; move that check.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Test checks two criteria",
>     "text": "The 697.3 test `test_settings_keep_other_subscription` also asserts the planner's role line survives, which is 697.6's behavior. Fix: move that assertion into a new 697.6 test; list it as 697.6's edge case.",
>     "evidence": "`tests/test_setup.py` line 260 asserts `roles.get(\"planner\")` i

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner moved the role check out of the subscription test into a new roles test.", "All eleven tests fail today because the setup command does not exist yet."], "decided": ["Keeping earlier roles when a second subscription is added is now a roles edge case."], "open": ["Nothing was raised for the owner."]},
 "verdict": "approve",
 "summary": "Each of the six criteria now has tests that check only its own behavior; the plan is ready to build.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "grabbing the inputs a user needs for a subscription (membership, region, sign-in or key, model)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.1"},
  {"ask": "sign-in or key, model) and putting them in place (key)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.2"},
  {"ask": "`subscriptions` (agent, key)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.3"},
  {"ask": "signed in with `kimi login --region global`", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.4"},
  {"ask": "region, sign-in or key, model) and putting them in place (sign-in)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.5"},
  {"ask": "`roles` (planner, worker, reviewer: which subscription and model)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.6"}
 ],
 "behaviors": [
  {"criterion": "697.1", "one_behavior": true, "why": "One listing of the four inputs."},
  {"criterion": "697.2", "one_behavior": true, "why": "One action: the key becomes a named secret."},
  {"criterion": "697.3", "one_behavior": true, "why": "One record: what the file holds for a subscription."},
  {"cr
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`4. Bash`
```
sed -i 's/The planner moved the role check out of the subscription test into a new roles test./The planner moved the role check from the subscription test into a new roles test./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 697 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`5. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/The planner moved the role check out of the subscription test into a new roles test./The planner moved the role check from the subscription test into a new roles test./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 697 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I approved the plan for [#697](https://github.com/dokima-dev/dokima/issues/697) (setup stores a subscription's inputs). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's blocker is fixed.** The test for the subscription list (697.3) no longer checks role lines. That check is now its own test under the roles criterion (697.6).
- **Nothing the owner asked for is missing.** Each of the owner's six asks, from the parent issue [#696](https://github.com/dokima-dev/dokima/issues/696) (the settings file that picks each role's agent and model), has its own criterion.
- **Each criterion is one behavior.** Every test checks only its own criterion.
- **All 11 tests fail today for the right reason:** the setup command doesn't exist yet, not a crash or a bad path.

I raised nothing new, and there were no open blockers to answer.

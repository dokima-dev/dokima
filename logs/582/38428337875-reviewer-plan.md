# reviewer (plan) for #582

Run: https://github.com/dokima-dev/dokima/actions/runs/38428337875

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #582: The worker cannot finish until its acceptance tests pass
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Each step runs only after the one before passed: worker tests, code review, merge gate, then owner approval.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149841134) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/341
> - https://github.com/dokima-dev/dokima/issues/587
> - https://github.com/dokima-dev/dokima/issues/580
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/292
> - https://github.com/dokima-dev/dokima/issues/111
> 
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
> In Reza's words (2026-10-13): "the worker agent end of work check should 100% check the acceptance tests".
> 
> Why: the worker is only tol

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; grep -n "6149288718\|issuecomment" issue.md | head; grep -n "def problems_review\|asks\|S<s>" /home/runner/work/dokima/dokima/dokima/agent.py | head -30
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38427924536",
>  "commit_before": "507df8606bd0c0d74b549dfcb7a9bc4434b357c8",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 122668,
>   "turns": 15,
>   "cost_usd": 1.0607718,
>   "tokens_in": 928975,
>   "tokens_out": 12595
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/582/38427924536-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38427924536",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149841134"
> }
> 7:**Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149841134) with `/plan`, or say `/review`
> 684:    for a in h.get("asks") or []:
> 866:                  ("The owner's asks", bullets(h.get("asks"), lambda a: f"{a.get('ask', '')} ({a.get('criterion', '')}, {a.get('source', '')})"))]
> 888:        return f"The planner proposes a split into {n} stories" + (" and asks you questions." if h.get("questions") else ".")
> 891:        return f"The planner planned this issue and asks you {q} question{'s' if q > 1 else ''}." if q else "The planner planned this issue."
> 1241:def problems_review(r):
> 1322:def problems_asks(r, ids):
> 1323:    """Everything wrong with a plan review

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1241,1330p dokima/agent.py; sed -n 1430,1445p dokima/agent.py
```

> def problems_review(r):
>     """Everything wrong with a review.json, as plain sentences; empty when it is well formed."""
>     bad = []
>     if r.get("verdict") not in VERDICTS:
>         bad.append("verdict must be approve, block or escalate")
>     if not str(r.get("summary", "")).strip():
>         bad.append("summary is empty")
>     prev = r.get("previous_step")
>     if not isinstance(prev, dict) or not any(prev.get(k) for k in ("did", "decided", "open")):
>         bad.append("previous_step must sum up what the planner or worker did, decided and left open")
>     elif sum(len(prev.get(k) or []) for k in ("did", "decided", "open")) > 5:
>         bad.append("previous_step holds at most five lines")
>     blocks = [x for x in r.get("raises") or [] if isinstance(x, dict) and x.get("kind") == "blocker"] \
>         if isinstance(r.get("raises"), list) else []
>     if r.get("verdict") == "approve" and blocks:
>         bad.append("an approve raises no blocker")
>     if r.get("verdict") == "block" and not blocks:
>         bad.append("a block needs at least one blocker in raises")
>     return bad
> 
> 
> def problems_tests(r, plan):
>     """A plan review must judge every test the plan names: does it check only its criterion's behavior, with the edge
>     cases the owner named or normal use hits? A false one never approves."""
>     named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if isinstance(ts, list) for t in ts})
>     rows = r.get("tests") if isinstance(r.get("tests"), list) else []
>     se

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the issue into three stories: the worker's own test check, the merge gate, and one fixed order."],
  "decided": ["The merge gate story builds on the merge rewrite already planned in another issue.", "Removing the tests that start when a pull request opens waits for the first two stories."],
  "open": ["The planner asks whether the owner approves only after all tests pass on the combined code."]},
 "verdict": "approve",
 "summary": "The split keeps every ask in three stories; one question on when the owner approves waits for you.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Before the worker hands back, code runs every test the approved plan lists for its criteria on the worker's branch.", "source": "https://github.com/dokima-dev/dokima/issues/582", "criterion": "S1.1"},
  {"ask": "Any failure refuses the hand-back with the failing tests named, and the worker keeps working in the same run.", "source": "https://github.com/dokima-dev/dokima/issues/582", "criterion": "S1.2"},
  {"ask": "A worker that cannot make them pass within its run hands back as blocked, naming the failing tests, never as done.", "source": "https://github.com/dokima-dev/dokima/issues/582", "criterion": "S1.3"},
  {"ask": "Worker: its end-of-run check runs every acceptance test of the approved plan and refuses to hand back until they pass.", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "S1.1"},
  {"ask": "Code review: starts only after the worker's check passed.", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "S3.1"},
  {"ask": "Merge gate: runs the full test suite on the combined code and merges if green", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "S2.1"},
  {"ask": "if not, the work goes back to the worker", "sourc
```

> Exit code 1
> previous_step did line 1 holds 20 words, over its cap of 15: cut 5, keep the facts
> previous_step decided line 2 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`5. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r["previous_step"]={"did":["The planner split the issue into three stories.","Stories: the worker's test check, the merge gate, one fixed order."],
"decided":["The merge gate story builds on the merge rewrite planned in another issue.","Dropping tests that start when a pull request opens waits for stories one and two."],
"open":["Does the owner approve only after all tests pass on the combined code?"]}
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 582 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#582](https://github.com/dokima-dev/dokima/issues/582) (the worker cannot finish until its acceptance tests pass). One question is still yours to answer before work goes on. The hand-back is in `/tmp/dokima-out/review.json`, and Dokima's own format check on it passes.

**The plan** splits the work into three stories:
1. **The worker's end check:** it runs the approved plan's tests and refuses to hand back while any fail, naming them. A worker that can't make them pass hands back as blocked, never as done.
2. **The merge gate:** all tests run on the pull request combined with the newest main. A failure sends the work back to the worker, and you approve last.
3. **One fixed order:** code review starts only after the worker's check passed. No test run happens during a review, and no merge is tried while tests still run.

**All 10 of your asks are covered,** each by one criterion. Every criterion is a single behavior, and the size is within the limit.

**Tests and edge cases aren't judged yet.** This is a split, so no tests are written now; each story gets its own plan and tests later, and edge cases get judged then.

**Your question:** in your rescope, step 3 says the merge gate "merges if green" and step 4 says "Owner approval". The planner read that as: you're asked to approve only after all tests pass on the combined code. GitHub's merge queue wants approval before it runs, so that reading changes how the system works. That's why I left it for you rather than answering it on autopilot. Reply with `/plan` and your answer, or `/review` to go on with the planner's reading.

**One thing I didn't raise:** your rescope says it replaces #577, but the plan doesn't link #577 or close it as a duplicate.

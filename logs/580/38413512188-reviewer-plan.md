# reviewer (plan) for #580

Run: https://github.com/dokima-dev/dokima/actions/runs/38413512188

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #580: Owner approval is the default, enforced by GitHub; auto-merge is the app on main's exemption list, nothing else
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> GitHub, not a repo variable, decides whether autopilot merges without the owner's approval.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/571
> - https://github.com/dokima-dev/dokima/issues/363
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/326
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
> In Reza's words (2026-10-12): "the default should be it always wants my approval. And then, you know, your special case only comes on top of this to kind of bypass that."
> 
> Why: #557 made a repo variable (DOKIMA_AUTO_MERGE) the switch, but the app cannot read repo variables (HTTP 403), so the code counted it off; and the app sat on main's review exemption, so it merged #576 with no owner approval anyway. The default was open and the switch did nothing.
> 
> Wanted: one switch, enforced b

`2. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000]);h=d.get('handback',d);print(h.get('raises'),h.get('answers'))"; grep -n "AUTO_MERGE\|def auto_merge_on\|def try_merge\|--admin\|def behind_main" dokima/*.py | head -40; grep -n "variables\|AUTO_MERGE" dokima/app.json dokima/manifest.py dokima/audit.py | head
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38413058732",
>  "commit_before": "507df8606bd0c0d74b549dfcb7a9bc4434b357c8",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 129988,
>   "turns": 16,
>   "cost_usd": 0.9743884,
>   "tokens_in": 973647,
>   "tokens_out": 12405
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/580/38413058732-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38413058732",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/580#issuecomment-6147783694"
> }
> None None
> dokima/audit.py:120:    """With DOKIMA_AUTO_MERGE on, a line when the merge queue ruleset lacks the app's bypass.
> dokima/audit.py:123:    if (github.variable(repo, manifest.AUTO_MERGE) or "").strip().lower() != "on":
> dokima/audit.py:130:    return [f"`{manifest.AUTO_MERGE}` is `on`, but Dokima's app is not a bypass actor of the merge queue ruleset for "
> dokima/manifest.py:55:AUTO_MERGE = "DOKIMA_AUTO_MERGE"
> dokima/agent.py:2229:def auto_merge_on(repo):
> dokima/agent.py:2230:    """True when the repo's variable DOKIMA_AUTO_MERGE is `on` (#557).
> dokima/agent.py:2234:        value = gh("api", f"repos/{repo}/actions/variables/{manifest.AUTO_MERGE}", "-q", ".value")
> dokima/agent.py:2237:            print(f"::warning::{manifest.AUTO_MERGE} could not be read, so it counts as off: {gh_reason(e)}")
> dokima/agent.py:2242:def behind_main(repo, head):
> dokima/agent.p

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the issue into three stories: the merge, the setup audit and manual fixes."],
  "decided": ["GitHub's exemption lists are the only switch; the repo variable and its read permission go.",
              "Manual fixes open as Dokima's app through a workflow, which stops for the owner."],
  "open": ["Each story's own planner names its tests and edge cases."]},
 "verdict": "approve",
 "summary": "The split keeps every ask of the owner, each in exactly one story, and its stories land separately.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "the default should be it always wants my approval", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S1.3"},
  {"ask": "Default: the app is on no exemption list, so GitHub requires the owner's approval for every pull request.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S1.3"},
  {"ask": "Auto-merge on means the app is on main's pull-request-only exemption lists (branch rule and merge queue ruleset); off means it is not.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S1.2"},
  {"ask": "The repo variable goes away.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S1.1"},
  {"ask": "one switch, enforced by GitHub, nothing for Dokima to read.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S2.3"},
  {"ask": "Dokima's code only tries to merge; GitHub allows it or holds it for the owner.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S1.2"},
  {"ask": "The setup audit reports which way the switch is set.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "S2.1"},
  {"ask": "Manual fixes by an agent are opened as Dokima's app, never as the owner, so the owner can approve them with one click", "source": "https://github.com
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner split the issue into three stories: the merge, the setup audit and manual fixes./The planner split the issue into three stories: merge, setup audit, manual fixes./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 580 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#580](https://github.com/dokima-dev/dokima/issues/580) (owner approval by default, auto-merge only where GitHub allows). The review is in `/tmp/dokima-out/review.json`, and it passes both checks.

- **The split:** three stories, with 8 criteria between them. Story 1 makes autopilot only ask GitHub to merge and stop reading the repo variable. Story 2 has the setup audit say whether auto-merge is on, and needs story 1 first. Story 3 has an agent's manual fix open as Dokima's app.
- **The owner's asks:** I found 9 in the issue. Each one is kept by a criterion and none is missing.
- **The plan's notes on the code are accurate.** The merge code and the audit both read the repo variable today, and the app still asks for permission to read repo variables.
- **Raises:** I raised nothing. The plan asks no questions, and there were no open blockers to answer.

Two things I let through rather than block on, since each story's own planner writes its criteria and tests:
- Two story 1 criteria each name two results: the pull request merges or waits, and the issue says so. I counted each as one outcome.
- Story 3's second criterion, that a manual fix can't merge until all tests pass, may already be true: main already requires the tests to pass.

A split plan has no tests yet, so I had nothing to run.

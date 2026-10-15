# reviewer (plan) for #696

Run: https://github.com/dokima-dev/dokima/actions/runs/38658690120

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat plan.json; cat open_blockers.json
```

> # Issue #696: A settings file picks each role's agent and model: Kimi first, then Codex
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> One settings file per repo says which subscription and model the planner, worker and reviewer use; Kimi first, then Codex.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181294422) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/39
> - https://github.com/dokima-dev/dokima/issues/148
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
> A settings file decides which agent and model each role uses, across subscriptions.
> 
> - Any agent, any model: planner, worker and reviewer each pick theirs.
> - Usual suspects first: Kimi first, since I want to use up its credit, then Codex.
> - The file is YAML-like, a structured file.
> - It exposes a simple 

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['02-reviewer-plan.json','03-planner.json']:
  d=json.load(open(f)); print(f, list(d.keys()))
  print(json.dumps({k:v for k,v in d.items() if k not in ('handback',)},indent=1)[:3000])
"; cd /home/runner/work/dokima/dokima; grep -n "runs-on\|self-hosted\|MODEL\|secrets\." .github/workflows/agent.yml | head -30; grep -n "def setup_body" -A30 dokima/audit.py | head -50; ls dokima | head -80
```

> 02-reviewer-plan.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38657221487",
>  "commit_before": "34d301ce183b7b835c2354735099149a653f8e4c",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 56497,
>   "turns": 8,
>   "cost_usd": 0.4146632,
>   "tokens_in": 275541,
>   "tokens_out": 5733
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/696/38657221487-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38657221487",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181136593"
> }
> 03-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38658402879",
>  "commit_before": "34d301ce183b7b835c2354735099149a653f8e4c",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 104742,
>   "turns": 8,
>   "cost_usd": 0.5849139999999999,
>   "tokens_in": 365267,
>   "tokens_out": 11417
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/696/38658402879-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38658402879",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/do

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the work into six stories: setup, the file, one agent interface, Kimi, Codex, later rules.",
          "The planner put no file, a left-out role and an unknown name into the stories' context."],
  "decided": ["Keys go in as repo secrets; the other inputs go in the settings file.",
              "Kimi is built before Codex, as the owner answered."],
  "open": ["Which rules across subscriptions the later story needs, asked of the owner."]},
 "verdict": "block",
 "summary": "The plan follows the owner's agreed stories, but setup has no place for a Kimi sign-in.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "S1.2: sign-in dropped",
   "text": "The owner listed 'sign-in or key'. S1.2 only puts a key in a repo secret. Kimi uses a sign-in, and runs start on a fresh machine each time, so a Kimi run has no way in. Smallest fix: split S1.2 into one criterion for a key and one for a sign-in, saying where each lands; ask the owner if unsure.",
   "evidence": "`plan.json` S1.2; owner's comment: `kimi login --region global`; `.github/workflows/agent.yml` line 49 `runs-on: ubuntu-24.04`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Any agent, any model: planner, worker and reviewer each pick theirs.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S2.4"},
  {"ask": "Usual suspects first: Kimi first, since I want to use up its credit, then Codex.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S4.1"},
  {"ask": "The file is YAML-like, a structured file.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S2.1"},
  {"ask": "It exposes a simple interface for deciding the orchestration across subscriptions.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S3.5"},
  {"ask": "Later it may expand into other settings.", "source": "https://github.com/
```

> Exit code 1
> raise 1's text holds 60 words, over its cap of 30: cut 30, keep the facts
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`4. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']['did']=["The planner split the work into six stories, from setup to later rules.",
 "The planner put no file, a left-out role and unknown names in context."]
d['raises'][0]['text']="S1.2 stores only a key, but the owner said 'sign-in or key'. Kimi signs in, and runs start fresh. Split S1.2: say where a key and a sign-in each go."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 696 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#696](https://github.com/dokima-dev/dokima/issues/696) (settings file picks each role's agent and model). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**Why it's blocked:** you said setup gathers "sign-in or key". The plan's setup step (S1.2) only stores a key, as a repo secret. Kimi signs in through the browser, and every run starts on a fresh GitHub machine (`agent.yml` line 49, `runs-on: ubuntu-24.04`). So a role on Kimi would have no way to sign in. I asked the planner to split S1.2 into two criteria, one for where a key goes and one for where a sign-in goes. That split also fixes the size problem, since S1.2 currently has two results in one criterion.

**What's in good shape:**
- All 16 asks from your issue and your answer comment map to a criterion. None are missing.
- Kimi is built before Codex, as you answered.
- With no settings file, runs work as they do today.
- My earlier blocker (a role left out of the file, or an unknown name) is covered in the stories' notes. A left-out role runs as today; an unknown name stops the run and names it.
- This plan is a split into stories, so it has no tests yet. Each story gets its own tests when it is planned.

**Still waiting on you:** the planner asks which rules across subscriptions the "Later" story (story 6) needs. Nothing you've written settles it, so I left it for you. Answer it with `/plan`.

**Not blocked, but worth knowing:** the plan says Dokima keeps no list of models (S2.4). That means "no model runs inside another vendor's agent" (S3.4) can only hold because each subscription always starts its own vendor's tool. Dokima can't catch a role that names a model from another vendor. The story 3 planner will need to pin down a testable result for S3.4.

# reviewer (plan) for #696

Run: https://github.com/dokima-dev/dokima/actions/runs/38662908785

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-planner.json
> # Issue #696: A settings file picks each role's agent and model: Kimi first, then Codex
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> One settings file per repo says which subscription and model the planner, worker and reviewer use; Kimi first, then Codex.
> 
> **Plan**
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
> - It exposes a simple interface for deciding the orchestration across subscriptions.
> - Later it may expand into other settings.
> 
> 
> </details>

`2. Bash`
```
cd /tmp/pack; cat in/04-reviewer-plan.json | head -c 9000; echo; python3 -c "
import json;d=json.load(open('in/05-planner.json'));print(d.keys());print({k:v for k,v in d.items() if k!='handback'})" | head -c 3000; cat parent.json | head -c 1000; git -C /home/runner/work/dokima/dokima status --short
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38658690120",
>  "commit_before": "34d301ce183b7b835c2354735099149a653f8e4c",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 78279,
>   "turns": 5,
>   "cost_usd": 0.38991359999999997,
>   "tokens_in": 185948,
>   "tokens_out": 8442
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/696/38658690120-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38658690120",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner split the work into six stories, from setup to later rules.",
>     "The planner put no file, a left-out role and unknown names in context."
>    ],
>    "decided": [
>     "Keys go in as repo secrets; the other inputs go in the settings file.",
>     "Kimi is built before Codex, as the owner answered."
>    ],
>    "open": [
>     "Which rules across subscriptions the later story needs, asked of the owner."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan follows the owner's agreed stories, but setup has no place for a Kimi sign-in.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "S1.2: sign-in dropped",
>     "text": "S1.2 stores only a key, but the owner said 'sign-in or key'. Kimi signs in, and runs start fresh. Split S1.2: say where a key and a sign-in each go.",
>     "evidence": "`plan.json` S1.2; owner's comment: `kimi login --region global`; `.github/workflows/agent.yml` line 49 `runs-on: u

`3. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/01-planner.json','in/03-planner.json']:
  d=json.load(open(f))['handback']
  for i,s in enumerate(d['stories']):
    for j,c in enumerate(s['acceptance_criteria']): print(f,i+1,j+1,c['text'])
"; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'))['handback'];print(json.dumps(d['raises'],indent=1))"; cat open_issues.json | head -c 1500
```

> in/01-planner.json 1 1 The settings file is a YAML file, so the owner edits plain keys and values.
> in/01-planner.json 1 2 The planner, the worker and the reviewer each get their own agent and model in the file.
> in/01-planner.json 1 3 A role may name any model its agent takes; Dokima keeps no list of allowed models.
> in/01-planner.json 1 4 Moving a role to another subscription is a one-line edit: that role's line in the file.
> in/01-planner.json 2 1 Each run starts the agent and model the settings file gives its role.
> in/01-planner.json 2 2 A role set to Kimi runs on Kimi, with the model the file names.
> in/01-planner.json 2 3 Dokima's own settings file names Kimi for every role, so its credit is used first.
> in/01-planner.json 3 1 A role set to Codex runs on Codex, with the model the file names.
> in/03-planner.json 1 1 Setup lists each input a subscription needs: membership, region, sign-in or key, and model.
> in/03-planner.json 1 2 Setup puts each given input in place: the key as a repo secret, the rest in the settings file.
> in/03-planner.json 2 1 Each repo keeps its agent settings in one YAML file in its Dokima folder.
> in/03-planner.json 2 2 The file lists subscriptions, each naming its agent and the secret holding its key.
> in/03-planner.json 2 3 The file gives the planner, the worker and the reviewer each a subscription and a model.
> in/03-planner.json 2 4 A role may name any model its agent takes; Dokima keeps no list of allowed models.
> in/03-planner.json 3 1 Each run starts the

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n '49p;59p;253p;321p;560,570p' .github/workflows/agent.yml; ls .dokima 2>&1; grep -rn "unknown\|left out" /tmp/pack/plan.json | head
```

> runs-on: ubuntu-24.04
>       MODEL: claude-opus-5-5
>           { pip install pytest pytest-xdist pytest-testmon && npm install -g @anthropic-ai/claude-code; } 2>&1 | tee /tmp/install.txt \
>           claude -p "$(cat /tmp/runtime/dokima/roles/style.md /tmp/runtime/dokima/roles/$GRADE.md /tmp/runtime/dokima/roles/$ROLE.md)
>           echo "Started the $2${3:+ ($3)} for #$N"
>       - name: Fail closed on a bad hand-back or the wrong model
>         if: always()
>         run: |
>           [ "$STARTED" = true ] || { echo "::error title=Not started::$(cat /tmp/why.txt 2>/dev/null)"; exit 1; }
>           python3 -c "import json,sys; r=json.load(open('$OUT/record.json')); m=r.get('models') or []; bad=[x for x in m if x!='$MODEL']; sys.exit(print('models:', m) or (1 if bad or not m else 0))"
>           [ "$PASSED" = true ] || { echo "::error title=Hand-back rejected::$(paste -sd'; ' "$OUT/check.txt")"; exit 1; }
>       - name: Report this run's GitHub calls
>         if: always()
>         continue-on-error: true
>         run: |
> ls: cannot access '.dokima': No such file or directory
> /tmp/pack/plan.json:51:   "context": "Today `.github/workflows/agent.yml` fixes `MODEL: claude-opus-5-5` (line 59), installs Claude Code (line 253), runs `claude -p ... --model \"$MODEL\"` (line 321) and fails a run whose logs name another model (line 565). `dokima/agent_records.py` `models_used`, `run_report` and `transcript` read Claude's logs and `claude.json`; `dokima/agent_roles.py` calls them. New: `dokima/settings.

`5. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/696"
C1=I+"#issuecomment-6181290061"; C2=I+"#issuecomment-6181845677"
asks=[
("Any agent, any model: planner, worker and reviewer each pick theirs.",I,"S2.4"),
("Usual suspects first: Kimi first, since I want to use up its credit, then Codex.",I,"S3.1"),
("The file is YAML-like, a structured file.",I,"S2.1"),
("It exposes a simple interface for deciding the orchestration across subscriptions.",I,"S2.9"),
("Later it may expand into other settings.",I,"S2.11"),
("No model runs inside another vendor's agent.",C1,"S2.8"),
("One structured file per repo, `.dokima/agents.yml`",C1,"S2.1"),
("`subscriptions` (agent, key)",C1,"S2.2"),
("`roles` (planner, worker, reviewer: which subscription and model)",C1,"S2.3"),
("No file means today's behavior.",C1,"S2.6"),
("grabbing the inputs a user needs for a subscription (membership, region, sign-in or key, model)",C1,"S1.1"),
("and putting them in place",C1,"S1.2"),
("The file and one agent interface; Claude Code moves behind it unchanged.",C1,"S2.7"),
("Kimi Code CLI adapter.",C1,"S3.1"),
("Codex CLI adapter.",C1,"S4.1"),
("No fallback for now.",C2,"S2.10"),
("The file is just a simple declaration: which model is used for which stage.",C2,"S2.5"),
]
beh={
"S1.1":"Setup shows one list of inputs.",
"S1.2":"A given key ends up as one repo secret.",
"S1.3":"A sign-in ends up stored as one repo secret.",
"S1.4":"Setup writes one entry into the file.",
"S2.1":"One file at one place.",
"S2.2":"One section, its fields named.",
"S2.3":"One section, each role's two fields.",
"S2.4":"Any model name is accepted.",
"S2.5":"A run starts the role's agent with its model.",
"S2.6":"No file gives today's run.",
"S2.7":"Claude Code runs as today behind the interface.",
"S2.8":"A model goes only to its own subscription's agent.",
"S2.9":"One edit moves a role.",
"S2.10":"A failed agent fails the run.",
"S2.11":"Own sections, so o
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for issue [#696](https://github.com/dokima-dev/dokima/issues/696) (the settings file that picks each role's agent and model). It has one blocker for the planner. The review is in `/tmp/dokima-out/review.json`, and it passes both checks with no problems reported.

**What the planner changed:**
- Dropped the story for rules across subscriptions, as you asked.
- Added a step where setup signs in once and stores the sign-in as a repo secret. Kimi puts it back before each run. That settles my earlier blocker on the sign-in.
- Added "no fallback": when a role's agent fails, the run fails.

**Your asks:** all 17 I found in the issue and your comments match a criterion. None is missing.

**The blocker:** two cases sit only in the notes for story 2, so no test will check them. The planner said these were done in round one, but they never became criteria:
- A role left out of the file should run as today.
- A subscription or agent name the file doesn't know should stop the run and name it.

The fix is one criterion for each.

**Sizes:** every criterion is one behavior. This is the plan that splits the issue into stories, so it names no tests yet. Each story's tests come when that story is planned.

There were no open blockers to answer and no questions waiting on you.

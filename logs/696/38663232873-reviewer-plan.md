# reviewer (plan) for #696

Run: https://github.com/dokima-dev/dokima/actions/runs/38663232873

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (32.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/7ad94fdd-61e2-4c2a-9630-f18ecbc422ad/tool-results/bvrvqf64m.txt
> 
> Preview (first 2KB):
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
> 06-reviewer-plan.json
> 07-planner.json
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
> - Usual suspe

`2. Bash`
```
cd /tmp/pack; sed -n 30,400p issue.md
```

> - The file is YAML-like, a structured file.
> - It exposes a simple interface for deciding the orchestration across subscriptions.
> - Later it may expand into other settings.
> 
> 
> </details>
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Acceptance tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Code review · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Test suite · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Owner approval
> 
> ## Comments
> 
> ### RezaSoleymanifar on issue #696 (2026-10-14T23:54:34Z)
> 
> /plan
> 
> ### dokima-runtime on issue #696 (2026-10-14T23:54:53Z)
> 
> <!-- dokima-record -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/planner.svg" width="16" height="16" align="absmiddle" alt="planner"> The planner proposes a split into 3 stories.
> 
> **Feature:** The owner picks each role's agent and model in one settings file. Stories: (1) the file; (2) 

`3. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json; cat parent.json | head -50; python3 -c "
import json;d=json.load(open('in/06-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"
```

> {
>  "kind": "feature",
>  "title": "A settings file picks each role's agent and model",
>  "summary": "One settings file per repo says which subscription and model the planner, worker and reviewer use; Kimi first, then Codex.",
>  "feature": "Each role runs on the subscription and model the owner declares in one file. Stories: setup, the file with one agent interface, Kimi, Codex.",
>  "stories": [
>   {
>    "title": "Setup gathers and stores a subscription's inputs",
>    "user_story": "The owner adds a subscription by giving its inputs once; setup puts each where runs find it.",
>    "context": "All of this story lives in a new `dokima/setup.py`, a command the owner runs once per subscription on their own machine. The owner did it by hand once for Kimi (comment of 2026-10-15): Kimi Code CLI 2.2.0 installed, `kimi login --region global` approved by a browser device code, then one unattended `kimi -p ... --output-format stream-json` run. Plan: Max, model access K3, default model kimi-for-coding. Agent runs start on a fresh `ubuntu-24.04` machine (`.github/workflows/agent.yml` line 49), so nothing saved on the owner's machine reaches them except through a repo secret. Hence: a key goes into a repo secret; a sign-in is done once by the agent's own login on the owner's machine (with the region the owner gives), and the files that login saves are stored as a repo secret too; the run writes them back before the agent starts (stories 3 and 4). `dokima/setup.py` holds, per agent, where its login sa

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/06-reviewer-plan.json'));h=d['handback'];print(json.dumps({k:h[k] for k in h if k in('edge_cases','tests','size')},indent=1)); print([k for k in d])"; python3 -c "
import json;d=json.load(open('in/07-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; git -C /home/runner/work/dokima/dokima status --short; ls /home/runner/work/dokima/dokima/.dokima 2>&1
```

> Exit code 2
> {
>  "edge_cases": [
>   {
>    "criterion": "S1.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.4",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.3",
>    "cut": [],
>    "missing": [
>     "A role left out of the file."
>    ]
>   },
>   {
>    "criterion": "S2.4",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.5",
>    "cut": [],
>    "missing": [
>     "A subscription or agent name the file does not know."
>    ]
>   },
>   {
>    "criterion": "S2.6",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.7",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.8",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.9",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.10",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.11",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S4.1",
>    "cut": [],
>    "missing": []
>   }
>  ],
>  "tests": [],
>  "size": "ok"
> }
> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "386630933

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/696"
C1=I+"#issuecomment-6181290061"; C2=I+"#issuecomment-6181845677"
asks=[
("Any agent, any model: planner, worker and reviewer each pick theirs.",I,"S2.4"),
("Usual suspects first: Kimi first, since I want to use up its credit, then Codex.",I,"S3.1"),
("The file is YAML-like, a structured file.",I,"S2.1"),
("It exposes a simple interface for deciding the orchestration across subscriptions.",I,"S2.11"),
("Later it may expand into other settings.",I,"S2.13"),
("No model runs inside another vendor's agent.",C1,"S2.10"),
("One structured file per repo, `.dokima/agents.yml`",C1,"S2.1"),
("`subscriptions` (agent, key)",C1,"S2.2"),
("`roles` (planner, worker, reviewer: which subscription and model)",C1,"S2.3"),
("No file means today's behavior.",C1,"S2.6"),
("grabbing the inputs a user needs for a subscription (membership, region, sign-in or key, model)",C1,"S1.1"),
("and putting them in place",C1,"S1.2"),
("The file and one agent interface; Claude Code moves behind it unchanged.",C1,"S2.9"),
("Kimi Code CLI adapter.",C1,"S3.1"),
("Codex CLI adapter.",C1,"S4.1"),
("No fallback for now.",C2,"S2.12"),
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
"S2.7":"A left-out role gives today's run.",
"S2.8":"A bad name stops the run with one error naming it.",
"S2.9":"Claude Code runs as today behind the interface.",
"S2.10":"A model goes only to its own vendor's agent.",
"S2.11":"O
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#696](https://github.com/dokima-dev/dokima/issues/696) (settings file that picks each role's agent and model). The hand-back is in `/tmp/dokima-out/review.json`, and both required checks pass on it.

- **What the planner did:** it answered my last blocker. Story 2 now has one criterion for a role left out of the file, which runs as today, and one for an unknown name, which stops the run and names the bad name.
- **The owner's asks:** I listed 17 from the issue and the owner's two comments. Each one maps to a criterion, none is missing, and the dropped "rules across subscriptions" story stays dropped.
- **Size:** I judged all 20 criteria to be one behavior each. Two of those calls were close:
  - The unknown-name criterion covers two cases (an unknown subscription or an unknown agent) and two results (the run stops, and it names the bad name). I counted it as one behavior: the run stops with one error.
  - The criterion where setup signs in and stores the sign-in also has two steps. I counted it as one result, the sign-in saved as a repo secret.
- **One point the owner may want to check:** a left-out role running as today is the planner's reading. It follows from the owner's "No file means today's behavior", but the owner never said it for a single left-out role.
- **Not checked:** the plan names no tests yet, so I had none to run.

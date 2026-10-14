# reviewer (plan) for #696

Run: https://github.com/dokima-dev/dokima/actions/runs/38657221487

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #696: A settings file picks each role's agent and model: Kimi first, then Codex
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> One settings file says which agent and model the planner, worker and reviewer use; Kimi is supported first, then Codex.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181100495) with `/plan`, or say `/review`
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
> - It exposes a simple in

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; python3 -c "
import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; git diff main --stat
```

> ## Splitting and the graph
> 
> - Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38656913804",
>  "commit_before": "34d301ce183b7b835c2354735099149a653f8e4c",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 120277,
>   "turns": 14,
>   "cost_usd": 0.8021712000000001,
>   "tokens_in": 656438,
>   "tokens_out": 11498
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/696/38656913804-planner.md",
>  "run": "https://github.com/dokima-dev/dokim

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "split\|stories\|S<\|tests" dokima/agent.py | grep -in "review\|asks\|S\b\|split\|behav\|edge" | head -60
```

> 1:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> 2:42:    problems_raised, problems_items, problems_shape, plan_criteria, problems_plan, load, plan_tests,
> 3:43:    failing_plan_tests, check, worker_docstring_caps)
> 4:48:    story_body, file_split, AUTOPILOT, issue_tree, switch_autopilot, autopilot_comment, AUTOPILOT_LINE,

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "def problems_review\|def plan_criteria" dokima/ ; f=$(grep -rln "def problems_review" dokima/); n=$(grep -n "def problems_review" $f | cut -d: -f1); sed -n "${n},$((n+120))p" $f
```

> dokima/agent_checks.py:124:def problems_review(r):
> dokima/agent_checks.py:310:def plan_criteria(plan, number):
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
>     """A plan review must judge every test the plan names: does it check only its
>     criterion's behavior, with the edge cases the owner named or normal use hits? A false one never approves."""
>     named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "split" rules/*.md | grep -iv "^rules/splitting" | head -30; cat .github/workflows/agent.yml | grep -n -i "model\|claude\|secret" | head -40
```

> rules/commands.md:5:- `/plan`: the planner (re)plans. `/work`: the worker builds, or an approved split is filed. `/review`: the reviewer looks again; on an issue it grades the plan, on a PR the work.
> rules/commands.md:6:- `/autopilot start` / `/autopilot stop`: put the issue, or the issue a PR was built for, and every sub-issue under it at every level on or off autopilot (the `autopilot` label). It leaves one comment where it was said naming every issue it switched. `/autopilot start` picks up what is waiting: an approved plan of that issue still waiting for `/work` starts the worker, and an approved split not yet filed is filed, as on autopilot; the issue itself, with no sub-issues, no plan and nothing open to wait for, starts its planner with one line `Autopilot: switched on, starting plan` where the owner would have said `/plan`; every issue under it, at every level, with no sub-issues, no plan and nothing open to wait for starts its planner; and every pull request in the tree its code review approved merges as in step 6. When the issue's last run ended with no record (its live card still up, its run over), `/autopilot start` starts that run's stage again instead. A split filed by `/work` on autopilot puts its stories on autopilot and starts the ones with nothing to wait for.
> rules/flow.md:4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it propose

**Agent:** Checking done: the plan is a 3-story split with no tests yet. Now writing the review.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the issue into three stories: the settings file, runs on Kimi, then Codex."],
  "decided": ["Dokima's own settings file puts every role on Kimi.", "Building Kimi first means building it first, not switching when credit runs out."],
  "open": ["Three questions for the owner: what Kimi first means, workflow changes, and overlap with issue 39."]},
 "verdict": "block",
 "summary": "The split keeps every ask, but it never says what happens when a role is missing or misspelled.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "S2.1: missing cases",
   "text": "S2.1 says nothing of a role left out of the file, no file at all, or an unknown agent. Add the expected result for each, so a typo fails clearly.",
   "evidence": "Criteria S1.2 and S2.1 in `plan.json` name only roles that are set; `agent.yml` line 59 fixes one `MODEL` today."},
  {"kind": "question", "to": "owner", "label": "Kimi for every role?",
   "text": "Should Dokima's own file put every role, the reviewer too, on Kimi? The plan assumes yes, to use up its credit.",
   "evidence": "Criterion S2.3; the issue says only 'Kimi first, since I want to use up its credit'."}
 ],
 "answers": [],
 "asks": [
  {"ask": "A settings file decides which agent and model each role uses, across subscriptions.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S2.1"},
  {"ask": "Any agent, any model: planner, worker and reviewer each pick theirs.", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S1.2"},
  {"ask": "Any agent, any model", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S1.3"},
  {"ask": "Usual suspects first: Kimi first", "source": "https://github.com/dokima-dev/dokima/issues/696", "criterion": "S2.2"},
  {"ask": "since I want to use up its credit", "source": "https://github.com/dokima-dev/dokima/issues/696"
```

> Exit code 1
> raise 2's text holds 21 words, over its cap of 20: cut 1, keep the facts
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> behaviors has no judgment of criterion S1.1: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.2: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.3: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.4: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.5: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S2.1: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S2.2: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S2.3: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S3.1: say one_behavior true or false, and why in one line
> edge_cases has no judgment of criterion S1.1: list the exotic cases it cuts and the normal-use ones missing, each [] when there are none
> edge_cases has no judgment of criterion S1.2: list the exotic cases it cuts and the normal-use ones missing, each [] when there are none
> edge_cases has no judgment of criterion S1.3: list the exotic cases it cuts and the normal-use ones m

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["previous_step"]["did"]=["The planner split the issue into three stories: the file, Kimi runs, then Codex."]
r["previous_step"]["open"]=["Three owner questions: what Kimi first means, workflow changes, overlap with issue 39."]
r["raises"][1]["text"]="Should Dokima's own file put every role, the reviewer too, on Kimi? The plan assumes yes, to spend its credit."
B=lambda k,w:{"criterion":k,"one_behavior":True,"why":w}
r["behaviors"]=[B("S1.1","One result: the file reads as YAML."),
 B("S1.2","One result: each role has its own agent and model entry."),
 B("S1.3","One result: any model name is accepted."),
 B("S1.4","One result: changing one line moves one role."),
 B("S1.5","One result: roles sit under their own section."),
 B("S2.1","One result: a run starts what its role names."),
 B("S2.2","One result: a Kimi role runs on Kimi."),
 B("S2.3","One result: the repo's file names Kimi everywhere."),
 B("S3.1","One result: a Codex role runs on Codex.")]
E=lambda k,m:{"criterion":k,"cut":[],"missing":m}
r["edge_cases"]=[E("S1.1",[]),E("S1.2",["A role left out of the file."]),E("S1.3",[]),E("S1.4",[]),E("S1.5",[]),
 E("S2.1",["No settings file at all.","A role left out of the file.","An agent name Dokima does not know, with the error the owner sees."]),
 E("S2.2",["Kimi's key missing, with the error the owner sees."]),E("S2.3",[]),
 E("S3.1",["Codex's key missing, with the error the owner sees."])]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 696 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#696](https://github.com/dokima-dev/dokima/issues/696) (a settings file picks each role's agent and model). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

**What the planner did:** it split the issue into three stories: the settings file, runs on Kimi, then Codex. It also asked you three questions:
- Does "Kimi first" mean build Kimi first, or switch to Codex once Kimi's credit runs out?
- May the stories change the agent workflow and add the Kimi and Codex keys?
- Should this issue build the Kimi and Codex adapters that [#39](https://github.com/dokima-dev/dokima/issues/39) (one adapter per agent) also plans?

**What I found:**
- **Every ask is kept.** All nine of your asks match one of the plan's criteria, and each criterion is one behavior.
- **No tests yet.** This is a split, so each story's own plan will add its tests.
- **Blocker for the planner:** the plan never says what happens when the file is missing, a role is left out, or an agent name is misspelled. It needs an expected result for each, so a typo fails clearly instead of silently running the wrong agent.
- **New question for you:** the plan sets Dokima's own file to Kimi for every role, the reviewer too. Your words, "Kimi first, since I want to use up its credit", don't clearly say that.

I didn't answer any of the planner's three questions for you. Your words don't settle them, and each changes how the system works or what it costs. The issue now waits for you: answer with `/plan` and your words, or say `/review` to go on with the planner's assumptions.

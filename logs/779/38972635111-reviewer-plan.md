# reviewer (plan) for #779

Run: https://github.com/dokima-dev/dokima/actions/runs/38972635111

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (31.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/6326d574-1a24-4dc4-b65b-18bbc31de533/tool-results/bsqbpbip0.txt
> 
> Preview (first 2KB):
> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-planner.json
> # Issue #779: Settings file over shipped defaults, read by every workflow
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791], "loop": []} -->
> One settings file per repo over shipped defaults, read by every workflow, in four turns.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/780
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/782
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/784
> - https://github.com/dokima-dev/dokima/issues/785
> - https://github.com/dokima-dev/dokima/issues/786
> - https://github.com/dokima-dev/dokima/issues/787
> - https://github.com/dokima-dev/dokima/issues/788
> - https://github.com/dokima-dev/dokima/issues/789
> - https://github.com/dokima-dev/dokima/issues/790
> - https://github.com/dokima-dev/dokima/issues/791
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/do

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed -n 40,400p
```

> <details><summary>Original issue</summary>
> 
> <!-- dokima-card -->
> <!-- /dokima-card -->
> 
> <details open><summary>From the approved plan of #740, story 1</summary>
> 
> **Part of:** #740 One settings file per repo over shipped defaults
> 
> **User story:** A repo writes only what differs into one settings file, and every workflow follows it.
> 
> **Context:** New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it). Today `dokima/setup.py` `read_settings()` reads only nested maps and `write_settings()` rewrites the file; `dokima/agents.py` reads `.dokima/agents.yml`. Workflow rows of the owner's list (A13 to A19, B3, B5, C3, C4, E1, E2, E4, E8, E11, E15) live in `.github/workflows/agent.yml`, `full-suite.yml`, `acceptance-criteria.yml`, `testmon.yml`, `fix.yml`, `wiki.yml`; the co-author trailer sits at `agent.yml:408` and `wiki.yml:27`. Locked keys: app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. The owner's newer comment makes the fence's test setup files a setting (row A5); newer words win, so the fence's lock covers what it does, not that list.
> 
> **Acceptance criteria:**
> - Dokima ships one defaults file that every repo's settings fall back to. ([source](https://github.com/dokima-dev/dokima/issues/740))
> - A repo's settings file changes only the settings it names; every other keeps its default. ([source](https://github.com/dokima-dev/dokima/issues/740))
> - The defaults file holds every 

`3. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json; echo; cat owner_words.json | head -50; cat parent.json | head -c 3000; echo; cat open_issues.json | head -c 1500
```

> <persisted-output>
> Output too large (30.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/6326d574-1a24-4dc4-b65b-18bbc31de533/tool-results/b9ipenjvz.txt
> 
> Preview (first 2KB):
> {
>  "kind": "feature",
>  "title": "Settings file over shipped defaults, read by every workflow",
>  "summary": "One settings file per repo over shipped defaults, read by every workflow, in four turns.",
>  "feature": "A repo overrides shipped defaults in one settings file, and setup, agents, workflows and prompts follow it, built in four stories taking turns.",
>  "stories": [
>   {
>    "title": "Settings read from shipped defaults, merged and checked",
>    "user_story": "A repo writes only what differs, and Dokima merges it over its defaults, warning on typos.",
>    "depends_on": [],
>    "context": "New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it in #740). Defaults come from the owner's 41-row list on #740. Locked keys: app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default.",
>    "acceptance_criteria": [
>     {
>      "text": "Dokima ships one defaults file that every repo's settings fall back to.",
>      "words": "Dokima ships one defaults file.",
>      "source": "https://github.com/dokima-dev/dokima/issues/740",
>      "files": [
>       "dokima/settings.py",
>       "dokima/defaults.yaml"
>      ],
>      "no_edge_cases": "Its own planner lists its edge cases with its tests."
>     },
>  

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'))
print([k for k in p])
for i,s in enumerate(p['stories'],1):
  print('S',i,s['title'],s['depends_on'],[k for k in s])
  for j,c in enumerate(s.get('acceptance_criteria',[])+s.get('non_functional',[]),1):
    print(' ',j,c['text'],'|',c['files'],'|',c['source'][-20:], '|', {k:v for k,v in c.items() if k not in('text','files','source','words')})
print(json.dumps({k:v for k,v in p.items() if k!='stories'},indent=1))
"; cat open_blockers.json; ls in; python3 -c "
import json;d=json.load(open('in/02-planner.json'));print(list(d))"
```

> ['kind', 'title', 'summary', 'feature', 'stories', 'links', 'raises', 'answers']
> S 1 Settings read from shipped defaults, merged and checked [] ['title', 'user_story', 'depends_on', 'context', 'acceptance_criteria', 'non_functional']
>   1 Dokima ships one defaults file that every repo's settings fall back to. | ['dokima/settings.py', 'dokima/defaults.yaml'] | ev/dokima/issues/740 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}
>   2 A repo's settings file changes only the settings it names; every other keeps its default. | ['dokima/settings.py'] | ev/dokima/issues/740 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}
>   3 The defaults file holds every setting of the owner's 41-row list, each with the default the list names. | ['dokima/defaults.yaml'] | uecomment-6219928729 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}
>   4 A settings group in a repo's file merges with the defaults key by key, the repo winning. | ['dokima/settings.py'] | ev/dokima/issues/740 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}
>   5 A list in a repo's file replaces the default list whole. | ['dokima/settings.py'] | ev/dokima/issues/740 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}
>   6 Gates in a repo's file merge with the default gates by name. | ['dokima/settings.py'] | ev/dokima/issues/740 | {'no_edge_cases': 'Its own planner lists its edge cases with its tests.'}

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; grep -n -i "feature\|split" rules/flow.md | head -40
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> 4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. If the plan has

**Agent:** Reviewing the split plan for #779: checking each of its 38 criteria matches the issue's list.

`6. Bash`
```
cd /tmp/pack; python3 - <<'E'
import json,re
p=json.load(open('plan.json'))
iss=open('issue.md').read()
items=re.findall(r'^- (.*?) \(\[source\]\((.*?)\)\)$',iss,re.M)
plan={}
for i,s in enumerate(p['stories'],1):
  for j,c in enumerate(s['acceptance_criteria'],1): plan[c['text']]=(f"S{i}.{j}",c['source'])
  print(i,'nf',s['non_functional'])
print(len(items),len(plan))
for t,src in items:
  m=plan.get(t); print(m and m[0], m and m[1]==src, t[:60])
E
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check plan /tmp/pack/plan.json 779 2>&1 | tail -5
```

> 1 nf []
> 2 nf []
> 3 nf []
> 4 nf []
> 38 38
> S1.1 True Dokima ships one defaults file that every repo's settings fa
> S1.2 True A repo's settings file changes only the settings it names; e
> S1.3 True The defaults file holds every setting of the owner's 41-row 
> S2.1 True A settings file holding lists is read in full, on every mach
> S2.2 True Saving a setting through setup keeps the file's comments.
> S2.3 True Saving a setting through setup keeps comments written at the
> S2.4 True Saving one setting through setup leaves every other setting 
> S2.5 True The agents section of the settings file picks each role's ag
> S2.6 True A repo with only the old agents file still runs each role's 
> S1.4 True A settings group in a repo's file merges with the defaults k
> S1.5 True A list in a repo's file replaces the default list whole.
> S1.6 True Gates in a repo's file merge with the default gates by name.
> S1.7 True Prompt additions in a repo's file merge with the default one
> S1.8 True An unknown setting shows a warning that suggests the closest
> S1.9 True An unknown setting is ignored and the run goes on.
> S1.10 True Setting any of the five locked settings in a repo's file fai
> S2.7 True No setting in a repo's file changes the order: plan, review,
> S2.8 True The repo's own install command runs before its tests in ever
> S2.9 True The test tools each test workflow installs come from the tes
> S2.10 True The repo's tests run on the Python version the settings name
> S3.1 True The all tests check runs the all-tests command 

`7. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'E'
import json,re
p=json.load(open('plan.json'))
iss=open('issue.md').read()
items=re.findall(r'^- (.*?) \(\[source\]\((.*?)\)\)$',iss,re.M)
ids={}
for i,s in enumerate(p['stories'],1):
  for j,c in enumerate(s['acceptance_criteria'],1): ids[c['text']]=f"S{i}.{j}"
asks=[{"ask":t,"source":src,"criterion":ids[t]} for t,src in items]
allids=list(ids.values())
r={"previous_step":{"did":["The planner split the 38 criteria into four stories that take turns."],
 "decided":["Each story keeps its criteria word for word from the issue.","Each story's own planner writes its tests and edge cases."],
 "open":[]},
 "verdict":"approve",
 "summary":"The split keeps all 38 criteria word for word, in four stories of ten or fewer.",
 "raises":[],"answers":[],"asks":asks,
 "behaviors":[{"criterion":i,"one_behavior":True,"why":"One action and one result, as the approved parent plan wrote it."} for i in allids],
 "edge_cases":[{"criterion":i,"cut":[],"missing":[]} for i in allids],
 "tests":[],"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
E
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 779 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the planner's plan to split issue #779 into four stories. My review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Nothing dropped or changed:** all 38 criteria in the issue carry over word for word, with the same source links. Each one is in exactly one story.
- **Size:** the stories hold 10, 10, 10 and 8 criteria. Each later story waits on the one before, because they share files. The issue is itself a story from #740, but it may split again because it holds more than 10 criteria.
- **Tests:** none yet. A split plan has none; each story's own planner writes its tests and edge cases. So I ran no tests at this stage.
- **Raises:** I raised nothing. There were no open blockers to answer.

The four stories:
1. Settings read from shipped defaults, merged and checked
2. Setup saves safely; agents and test setup follow settings
3. Test commands, branches and the bot follow settings
4. Co-author, owner docs and prompts follow settings

Stories 2 to 4 change files under `.github/workflows/`. The issue asks for that, but any such change still stops for your approval when it is built.

# reviewer (plan) for #661

Run: https://github.com/dokima-dev/dokima/actions/runs/38618197851

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (34.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/1d9b7c72-741c-4bcf-8eee-82ecd35f5e8f/tool-results/bwmp9ek99.txt
> 
> Preview (first 2KB):
> # Issue #661: Work splits into stories by the files it changes
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Each criterion lists the code files it changes, and code groups criteria into stories by shared files, with no caps.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/553
> - https://github.com/dokima-dev/dokima/issues/232
> - https://github.com/dokima-dev/dokima/issues/573
> - https://github.com/dokima-dev/dokima/issues/551
> - https://github.com/dokima-dev/dokima/issues/384
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
> <!-- dokima-title -->**Original title:** Work splits into stories

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed -n '30,400p'
```

> Any ask, however big, is broken into acceptance criteria, and code splits those criteria into stories by the files they change. No caps.
> 
> - The planner breaks the ask into acceptance criteria. Each one quotes my words, which are the spec.
> - The planner tags each criterion with the code files it changes. A file that doesn't exist yet counts by its path.
> - Code groups criteria that share any code file into one story (a sub-issue). Criteria with no file in common become separate stories. No number decides it: no criteria cap, no story cap.
> - Stories that share a file wait their turn to build. Planning and plan review never wait; only the worker's build does.
> - Markdown files never group criteria and never make a story wait.
> - Edge cases stay under their criterion and don't affect the split.
> - A step that changes no file (clicking through a console, for example) is listed on the plan as mine to do. Nothing waits on it by itself.
> - Red first stays: every criterion's test fails on main before work starts. An ask that can't be checked becomes a question to me, or shows on the card as not verified.
> - Stories merge to main one by one. No parent branch.
> - This replaces today's count-based split rules (split above 3 criteria per story, refuse above 15 per issue).
> 
> Evidence: replaying 127 merged plans under this rule, 122 stay a single story and 5 split. A typical story is about 4 criteria, 1 to 2 code files and about 300 changed lines, tests included. One file, `agent.py`, was touched b

`3. Bash`
```
cd /tmp/pack; ls in; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'))
print(json.dumps({k:v for k,v in p.items() if k!='stories'},indent=1))
for i,s in enumerate(p['stories'],1):
  print('== S',i,s.get('title'),'|',s.get('user_story'))
  for k,v in s.items():
    if k not in('title','user_story'): print(k, json.dumps(v,indent=1))
"
```

> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-planner.json
> []{
>  "kind": "feature",
>  "title": "Work splits into stories by the files it changes",
>  "summary": "Each criterion lists the code files it changes, and code groups criteria into stories by shared files, with no caps.",
>  "feature": "Criteria list their files; code groups them into stories by shared files. Shared files take turns to build. Owner steps sit on the plan.",
>  "links": {
>   "blocked_by": [],
>   "blocks": [],
>   "relates_to": [
>    232,
>    573,
>    551,
>    384
>   ]
>  }
> }
> == S 1 Each criterion lists the code files it changes | Every plan shows which code files each criterion changes, so code can split and fence by them.
> context "Today a plan has one scope list for the whole story (`scope` in plan.json, checked in `from_kind` in `dokima/planner.py`); criteria carry no files. Add a `files` list to every criterion, in user stories and in a split's stories (`check_stories`). A path that does not exist yet is fine: the worker creates it. The planner's instructions live in `dokima/roles/planner.md` and `dokima/roles/plan-grade.md`; this issue explicitly asks to change how the planner tags criteria, so those files are in reach. Tests sit beside `tests/test_plan_shape.py` and `tests/test_planner_prompt.py`."
> acceptance_criteria [
>  {
>   "text": "Each criterion in a plan carries a list of the code files it changes.",
>   "words": "Each criterion carries a `files` list in the plan's structured output

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/05-planner.json'));print(json.dumps(d,indent=1)[:6000])"; grep -o 'issuecomment-[0-9]*' -r in issue.md | sort | uniq -c
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38617942328",
>  "commit_before": "ac5c8e79bf7783ec4664ac8ecb5fdb39e9db110f",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 26191,
>   "turns": 5,
>   "cost_usd": 0.362541,
>   "tokens_in": 194961,
>   "tokens_out": 2492
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/661/38617942328-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38617942328",
>  "handback": {
>   "kind": "feature",
>   "title": "Work splits into stories by the files it changes",
>   "summary": "Each criterion lists the code files it changes, and code groups criteria into stories by shared files, with no caps.",
>   "feature": "Criteria list their files; code groups them into stories by shared files. Shared files take turns to build. Owner steps sit on the plan.",
>   "stories": [
>    {
>     "title": "Each criterion lists the code files it changes",
>     "user_story": "Every plan shows which code files each criterion changes, so code can split and fence by them.",
>     "context": "Today a plan has one scope list for the whole story (`scope` in plan.json, checked in `from_kind` in `dokima/planner.py`); criteria carry no files. Add a `files` list to every criterion, in user stories and in a split's stories (`check_stories`). A path that does not exist yet is fine: the worker creates it. The planner's instructions live in `dokima/roles/planner.md` and `dokima/roles/plan-grade.md`; this issue 

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/05-planner.json'));h=d['handback'];print(json.dumps({k:v for k,v in h.items() if k!='stories'},indent=1)); print(json.dumps({k:v for k,v in d.items() if k not in('handback',)},indent=1)[:3000])"; python3 -c "
import json;d=json.load(open('/tmp/pack/in/04-reviewer-plan.json'));print(json.dumps(d['handback'],indent=1)[:5000])"
```

> {
>  "kind": "feature",
>  "title": "Work splits into stories by the files it changes",
>  "summary": "Each criterion lists the code files it changes, and code groups criteria into stories by shared files, with no caps.",
>  "feature": "Criteria list their files; code groups them into stories by shared files. Shared files take turns to build. Owner steps sit on the plan.",
>  "links": {
>   "blocked_by": [],
>   "blocks": [],
>   "relates_to": [
>    232,
>    573,
>    551,
>    384
>   ]
>  }
> }
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38617942328",
>  "commit_before": "ac5c8e79bf7783ec4664ac8ecb5fdb39e9db110f",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 26191,
>   "turns": 5,
>   "cost_usd": 0.362541,
>   "tokens_in": 194961,
>   "tokens_out": 2492
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/661/38617942328-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38617942328",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6175761976"
> }
> {
>  "previous_step": {
>   "did": [
>    "Criterion 4.1 now lists the normal case: the other story merges, the build starts.",
>    "New criterion 4.5: a story adding files is checked again for clashes."
>   ],
>   "decided": [
>    "The plan keeps six stories, each with its tests written by that story's planner."
>   ],
>   "open": [
>    "Three owner questions wait: big story size, when a turn ends, closing #553."
>   ]
>  }

**Agent:** Checking whether a plan can carry "close #553" before writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "relates_to\|replaces\|closes\b\|\"duplicates\"\|supersede" dokima/*.py | head -30; grep -n "553\|replace\|supersede" rules/*.md | head
```

> dokima/agent.py:53:    work_approved, CHECKS_WAIT, CHECKS_PAUSE, BOARD_WAIT, superseded, required_checks, unproven, proof, UPDATE_WAIT,
> dokima/agent_autopilot.py:131:    `has(i)` gives what GitHub has issue i blocked by. A new link a blocked by b closes a loop when b is already
> dokima/agent_autopilot.py:456:    """The comment a parent closes with when its last sub-issue closed, on autopilot or not."""
> dokima/agent_autopilot.py:457:    return f"Every issue under #{number} is closed, so its whole tree is done and it closes.\n"
> dokima/agent_autopilot.py:505:    """What autopilot does when an issue closes, worked out from GitHub's state of every issue
> dokima/agent_autopilot.py:508:    Every open parent on autopilot whose sub-issues are all closed closes as completed, saying its tree is done, and
> dokima/agent_autopilot.py:586:def superseded(run):
> dokima/agent_autopilot.py:627:                for r in p.get("check_runs", []) if not superseded(r) and r.get("name") in required]
> dokima/agent_github.py:75:        r"(?i)\b(?:closes|fixes|resolves) (?:#|https://github\.com/[\w.-]+/[\w.-]+/issues/)(\d+)\b", body or "")
> dokima/body.py:35:    Only the last DONE marker counts, and only when one line follows it and the fold closes right before it, so the
> dokima/audit.py:6:on the Setup issue (opened, pinned and marked Needs you, or updated), closes it with one line once nothing is off, and
> dokima/audit.py:201:            + "\nEach audit updates this issue, and closes it once nothing is off.\n"

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/w.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/661"
C1=I+"#issuecomment-6173691734"; C2=I+"#issuecomment-6173871465"; C3=I+"#issuecomment-6175675553"
asks=[
("The planner tags each criterion with the code files it changes.",I,"S1.1"),
("Each criterion carries a `files` list in the plan's structured output: the code files it changes, at least one.",C1,"S1.1"),
("Code rejects a plan where a criterion lists none.",C1,"S1.2"),
("A file it creates counts by its path.",C1,"S1.3"),
("A criterion lists every file its behavior needs, never just one, so a behavior is never cut across stories.",C1,"S1.4"),
("if it can be written as code (infrastructure as code, a setup script), it's a criterion like any other.",C1,"S1.5"),
("The plan's scope is all criteria's files plus their tests",C1,"S2.1"),
("with no separate scope field.",C1,"S2.2"),
("The fence keeps enforcing it.",C1,"S2.3"),
("Each one quotes my words, which are the spec.",I,"S2.4"),
("Code groups criteria that share any code file into one story (a sub-issue).",I,"S3.1"),
("Criteria with no file in common become separate stories.",I,"S3.2"),
("No number decides it: no criteria cap, no story cap.",I,"S3.3"),
("This replaces today's count-based split rules (split above 3 criteria per story, refuse above 15 per issue).",I,"S3.3"),
("Markdown files never group criteria",I,"S3.4"),
("Edge cases stay under their criterion and don't affect the split.",I,"S3.5"),
("Stories that share a file wait their turn to build.",I,"S4.1"),
("A story's turn ends when its PR merges.",C3,"S4.1"),
("Planning and plan review never wait; only the worker's build does.",I,"S4.2"),
("and never make a story wait.",I,"S4.3"),
("Stories merge to main one by one. No parent branch.",I,"S4.4"),
("a story whose plan changes files beyond the ones it was assigned is checked again for clashes before it builds.",C2,"S4.5"),
("A step that changes no file (clicking through a console, for example) is
```

> 0

**Agent:** I approved the plan for [#661](https://github.com/dokima-dev/dokima/issues/661) (splitting work into stories by the files it changes), and the review passed both checks.

- **Your latest comments are all in the plan:**
  - A story's turn to build now ends when its pull request merges.
  - The card no longer names a crowded file.
  - A story that adds files gets checked again for clashes before it builds.
- **Every ask has a criterion.** All 28 of your asks match one of the plan's 25 criteria, across 6 stories. None is missing.
- **No tests were run.** Each story's own planner writes its tests after the split, so none exist yet. Tests will be checked when each story's plan comes back for review.
- **#553 stays open.** The plan only drops the link to [#553](https://github.com/dokima-dev/dokima/issues/553) (at most 3 criteria per story). Nothing in it closes that issue, so you'll need to close it yourself, as you said you wanted.

I raised no blockers. There were no earlier ones left to answer.

The review is in `/tmp/dokima-out/review.json`.

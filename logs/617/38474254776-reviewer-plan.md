# reviewer (plan) for #617

Run: https://github.com/dokima-dev/dokima/actions/runs/38474254776

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #617: An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A split approved again after its stories were filed now files the new stories.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/553
> 
> 
> **User story:** When the owner rescopes a split parent and approves the new split, its new stories get filed.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A split approved after its earlier stories were filed files its new stories as sub-issues.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-617/tests/test_agent.py#L428"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A split approved again after filing files its new s

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json | head -50; git show --stat HEAD; sed -n 360,460p dokima/agent.py; grep -n "test_a_split_approved_after" -A80 tests/test_agent.py | head -130
```

> {"number": null}commit 69167c3bbe796e418d55f281a415c44a2ac9bcd3
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 21:56:00 2026 +0000
> 
>     planner for #617 (run 38474064913)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_agent.py | 35 +++++++++++++++++++++++++++++++++++
>  1 file changed, 35 insertions(+)
> 
> 
> def story_body(parent, i, story, parent_title):
>     """A story's issue body, drawn by code from the approved plan, so the child planner starts from exactly what was agreed."""
>     lines = ["<!-- dokima-card -->", "<!-- /dokima-card -->", "",
>              f"<details open><summary>From the approved plan of #{parent}, story {i}</summary>", "",
>              f"**Part of:** #{parent} {parent_title}", "", f"**User story:** {story.get('user_story', '')}", ""]
>     if story.get("context"):
>         lines += [f"**Context:** {story['context']}", ""]
>     lines += ["**Acceptance criteria:**"]
>     lines += [f"- {c.get('text', '')} ([source]({c.get('source', '')}))" for c in story.get("acceptance_criteria", [])]
>     if story.get("non_functional"):
>         lines += ["", "**Non-functional:**"] + [f"- {n.get('text', '')} ({n.get('why', '')})" for n in story["non_functional"]]
>     return "\n".join(lines + ["", "</details>"]) + "\n"
> 
> 
> def file_split(repo, parent, recs, labels=()):
>     """File the stories of the newest approved split as sub-issues of the parent, in order, with their 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_agent.py -k split 2>&1 | tail -20; git log --oneline -5 -S"file_split" ; grep -rn "file_split\|\"split\", passed" dokima/*.py | head -20; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:1500])"
```

> E         
> E         Full diff:
> E         + []
> E         - [
> E         -     'Third',
> E         - ]
> 
> tests/test_agent.py:454: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_agent.py::test_a_split_approved_after_its_stories_were_filed_files_its_new_stories - AssertionError: 617.1: the approved re-plan filed [], not its new story Third
> assert [] == ['Third']
>   
>   Right contains one more item: 'Third'
>   
>   Full diff:
>   + []
>   - [
>   -     'Third',
>   - ]
> 1 failed, 2 passed, 24 deselected in 0.25s
> 69167c3 planner for #617 (run 38474064913)
> 78fe9eb /work on an approved split files its stories as sub-issues (#153)
> dokima/agent.py:376:def file_split(repo, parent, recs, labels=()):
> dokima/agent.py:381:    done = latest(recs, "split", passed=True)
> dokima/agent.py:2819:        rec = file_split(repo, parent, recs, [AUTOPILOT] if on else [])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38474064913",
>  "commit_before": "a9701dcd1c18343e8c700132dc6cc7d5d53232bd",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 44178,
>   "turns": 9,
>   "cost_usd": 0.494225,
>   "tokens_in": 421086,
>   "tokens_out": 4381
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/617/38474064913-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38474064913",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/61

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner planned one criterion: a split approved again after filing files its new stories.", "The planner added one test that files a split, then a re-plan, then the re-plan again."], "decided": ["The planner read new stories as every story of the newer split."], "open": []},
 "verdict": "block",
 "summary": "The plan never says what happens to a story the re-plan keeps, so it could be filed twice.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Missing normal case", "text": "617.1's test re-plans with only brand-new stories. A rescope that keeps a filed story is normal; code filing every story again passes. Add that case, or ask the owner which reading.", "evidence": "`tests/test_agent.py:448` the re-plan holds only story `Third`; the first split's stories never reappear."}
 ],
 "answers": [],
 "asks": [{"ask": "An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.", "source": "https://github.com/dokima-dev/dokima/issues/617", "criterion": "617.1"}],
 "behaviors": [{"criterion": "617.1", "one_behavior": true, "why": "One action, approving a re-plan, with one result, its new stories filed."}],
 "edge_cases": [{"criterion": "617.1", "cut": [], "missing": ["A re-plan that keeps a story already filed and adds a new one."]}],
 "tests": [{"test": "tests/test_agent.py::test_a_split_approved_after_its_stories_were_filed_files_its_new_stories", "only_its_behavior": true, "why": "Checks only that the re-plan files its stories once; fails today for the right reason."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 617 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`5. Bash`
```
cd /tmp/dokima-out; sed -i 's/A rescope that keeps a filed story is normal; code/A rescope keeping a filed story is normal; code/; s/The planner added one test that files a split, then a re-plan, then the re-plan again./The planner added one test filing a split, then a re-plan, then the re-plan again./' review.json; cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 617 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#617](https://github.com/dokima-dev/dokima/issues/617) (a split approved again files nothing) and sent it back to the planner. The hand-back is at `/tmp/dokima-out/review.json` and passes both checks.

- **What's fine:** the plan has one criterion, which traces to your words in the issue, and it has one test. That test fails today for the right reason: approving the split again files nothing.
- **Why I blocked:** the test only tries a new split made entirely of new stories. Rescoping a parent often keeps a story that was already filed, and code that files every story again would still pass. That would file the kept story twice.
- **Fix:** the planner either adds that case to the test, or asks you whether "new stories" means only the ones not filed yet.

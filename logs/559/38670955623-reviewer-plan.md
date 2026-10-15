# reviewer (plan) for #559

Run: https://github.com/dokima-dev/dokima/actions/runs/38670955623

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #559: Tests are the spec: I write tests, the planner maps them, every text is a short and full pair
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 560, 667, 668 -->
> <!-- dokima-blocking: {"blocked_by": [666, 667, 668, 670], "blocks": [], "loop": []} -->
> The owner's tests lead the plan, stay locked, and every text the owner reads comes short with full detail folded.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/559#issuecomment-6182937950) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/667
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/670
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/470
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/184
> - https://github.com/dokima-dev/dokima/issues/335
> - https://github.com/dokima-dev/d

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(list(d.keys()));print(json.dumps({k:v for k,v in d.items() if k not in('handback','plan')},indent=1)[:3000])"; ls /home/runner/work/dokima/dokima/tests | grep -E "owner_tests|test_docstrings|parent_detail|text_pairs|card_pairs"; git -C /home/runner/work/dokima/dokima log --oneline -3 main..HEAD
```

> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38670512560",
>  "commit_before": "c5c273b6069b0c983dc85f48268f990fcb278d0b",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 250104,
>   "turns": 20,
>   "cost_usd": 1.4696690000000001,
>   "tokens_in": 1269114,
>   "tokens_out": 25946
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/559/38670512560-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38670512560",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/559#issuecomment-6182937950"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; grep -n -i "split" rules/flow.md rules/raising.md | head -40; cat dokima/roles/plan-grade.md | head -5
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria, and no count of criteria or stories decides it.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> rules/flow.md:4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. If the plan has questions, the river stops and mentions the owner, who answers with `/plan` and their words, or says `/review` to go on 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "split" rules/specs.md rules/records.md | head; grep -n -i "split\|stories" dokima/roles/planner.md | head -30
```

> rules/records.md:3:Every agent run posts one comment, written by code: one plain sentence on top saying what the run did, then only what that run changed, decided or raised, never repeating the card above it (the planner's raises, answers and changes to older tests, or the split's stories; the worker's files changed, as links on one line, and its test result, or why it stopped; a review's verdict, then only what fails: each failing criterion's sentence with why it fails and its Source, each ask nothing covers, then what it raised, its blockers, questions and issues, with no criterion numbers or raise IDs, and an escalation's reason), the long parts in folds drawn by the same code as the issue card, a Stats fold with the model, time, turns, tokens (short: 950, 12K, 3M), API-equivalent cost and one-click links to the run's whole conversation and its run, and the full JSON record in the last fold, right under it. A field shows only when it has something, and a field two agents share, such as answers to earlier raises, is drawn the same from each. Review runs are called Plan review and Code review. Each run also saves its record as its own new file on the logs branch, never edited, whether the run passed, failed, was cancelled or died. A starting pack reads earlier records only from those files, never from a comment, and stops saying why when it cannot read them. The card and the river still read the record comments until #613; only comments the bot posted count. The card on top 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 35,140p dokima/roles/planner.md; sed -n 195,240p dokima/roles/planner.md
```

> The plan grade comes first in this prompt. Walk its list yourself before you finish; the reviewer grades your plan
> against the same list and sends it back on 1 to 5.
> 
> # The plan
> Write the plan the way a product manager writes a story, in these terms:
> - **User story:** one sentence, what changes for the owner when this is done. It replaces "Objective".
> - **Feature:** a parent issue that splits into 2 or more user stories. Each story says which other stories it depends on.
> - **Acceptance criteria:** the behaviors and features the owner asked for, numbered N.1, N.2 ... (N is the issue number).
>   Each criterion is exactly one behavior: one action, one visible result. "X and Y", two results, or "that includes A,
>   B and C" is several criteria. Bad: "Editing an issue redraws its card and its PR's card, and a merge redraws both."
>   Good: "Editing an issue redraws its card." / "Merging a pull request redraws its issue's card."
>   Product voice, third person, never "I". Natural phrasing, never a formula; "When you..." only where it's natural.
>   Each one is observable (what the owner sees, a file, an exit code, a number with its unit), never an adjective, and
>   links to where the owner said it: the issue, or a specific comment. When they asked for it more than once, its
>   source is the most recent place the owner asked for it. A bug fix is an acceptance criterion ("X no
>   longer happens"). Nothing the owner did not ask for: no states, cases or rules of your own.
> - **Non-functional requi

**Agent:** Reviewing the split plan for #559 now: checking the owner's asks against the criteria and verifying the planner's claims.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -i -A12 "starting branch" .github/workflows/agent.yml | head -40; grep -rn "worker_docstring_caps\|def docstring_caps" dokima/*.py | head
```

> 147:      - name: Starting branch
> 148-        env:
> 149-          GH_TOKEN: ${{ github.token }}
> 150-        run: |
> 151-          if git ls-remote --exit-code --heads origin "try/issue-$N" >/dev/null; then
> 152-            git fetch -q origin "try/issue-$N" && git checkout -q -B "try/issue-$N" FETCH_HEAD
> 153-            echo "BRANCH_TIP=$(git rev-parse HEAD)" >> "$GITHUB_ENV"
> 154-            # A worker's branch that clashes with main still starts: the merge is committed with its conflict markers,
> 155-            # the clashed files are listed for the fence, and the worker resolves them. Main's changes are in BASE.
> 156-            if [ "$ROLE" = worker ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" merge -q --no-edit origin/main; then
> 157-              git diff --name-only --diff-filter=U > /tmp/clashed.txt
> 158-              if [ ! -s /tmp/clashed.txt ]; then
> 159-                echo "Merging main into try/issue-$N failed with no clashed file to resolve." > /tmp/why.txt
> dokima/agent.py:43:    failing_plan_tests, check, worker_docstring_caps)
> dokima/agent_checks.py:377:        more, too_long = worker_docstring_caps(os.environ["PLANNER_BASE"])
> dokima/agent_checks.py:399:def worker_docstring_caps(base):
> dokima/planner.py:518:def docstring_caps(paths, before, after):

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner proposed a split into six stories with 29 criteria.", "It raised three questions for the owner."],
  "decided": ["Re-plans keeping the owner's commits, and the owner's work getting all checks, are left as already true."],
  "open": ["Whether to close the branch clean-up issue, how plans are edited, and where criteria live."]
 },
 "verdict": "block",
 "summary": "Three of the owner's asks have no criterion, and five criteria each hold two cases or two things.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "No criterion",
   "text": "Three asks have no criterion: a re-plan keeps my commits; my work gets the same reviews and checks; I edit then say /review. Add a criterion with a pinning test for each, or ask the owner to drop it.",
   "evidence": "Issue text: `a re-plan keeps my commits`, `My work goes through the same reviews and checks`; no criterion in stories 1 to 6 names them."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Prompt ask reworded",
   "text": "Criterion 1.6 turns the owner's prompt ask into a rejection message and bundles two prompts. Make it two criteria: planner prompt says it; worker prompt says it.",
   "evidence": "Comment 6132026430: `The planner and worker prompts say: Verified by explains how the test proves the behavior`."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Two cases in one",
   "text": "Criteria 3.1, 3.2 and 3.3 each hold two cases, no short half or no full half; 3.5 holds names code and past every cap. Split each in two.",
   "evidence": "`plan.json` story 3 criteria texts: `no short half or no full half`, `names code and runs past every cap`."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "I write tests, as many or as few as I like, or none.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "S1.3"},
  {"ask": "The planner groups te
```

> Exit code 1
> raise 1's text holds 39 words, over its cap of 30: cut 9, keep the facts
> raise 1's evidence holds 25 words, over its cap of 20: cut 5, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> behaviors has no judgment of criterion S1.1: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.2: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.3: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.4: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.5: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.6: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.7: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.8: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.9: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.10: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.11: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.12: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.13: say one_behavior true or false, and wh

`8. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['text']="No criterion carries three asks: a re-plan keeps my commits; my work gets the same checks; I edit then say /review. Pin each with a test, or ask the owner."
r['raises'][0]['evidence']="Issue: `a re-plan keeps my commits`, `My work goes through the same reviews and checks`; stories 1 to 6 name neither."
r['previous_step']['decided']=["Re-plans keeping the owner's commits, and the owner's work getting checks, are left as true."]
plan=json.load(open('/tmp/pack/plan.json'))
false={'S1.6':"Bundles a rejection message with two prompt lines.",
 'S3.1':"Two cases: no short half, or no full half.",
 'S3.2':"Two cases: no short half, or no full half.",
 'S3.3':"Two cases: no short half, or no full half.",
 'S3.5':"Two things: names code, and runs past every cap."}
b=[];e=[]
for s,st in enumerate(plan['stories'],1):
  for k,_ in enumerate(st['acceptance_criteria']+st['non_functional'],1):
    c=f"S{s}.{k}"
    b.append({"criterion":c,"one_behavior":c not in false,"why":false.get(c,"One action with one visible result.")})
    e.append({"criterion":c,"cut":[],"missing":[]})
r['behaviors']=b;r['edge_cases']=e
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 559 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> raise 1's evidence holds 21 words, over its cap of 20: cut 1, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['text']="No criterion carries three asks: a re-plan keeps my commits; my work gets the same checks; I edit then say /review. Pin each with a test, or ask the owner."
r['raises'][0]['evidence']="Issue: `a re-plan keeps my commits`, `My work goes through the same reviews and checks`; stories 1 to 6 name neither."
r['previous_step']['decided']=["Re-plans keeping the owner's commits, and the owner's work getting checks, are left as true."]
plan=json.load(open('/tmp/pack/plan.json'))
false={'S1.6':"Bundles a rejection message with two prompt lines.",
 'S3.1':"Two cases: no short half, or no full half.",
 'S3.2':"Two cases: no short half, or no full half.",
 'S3.3':"Two cases: no short half, or no full half.",
 'S3.5':"Two things: names code, and runs past every cap."}
b=[];e=[]
for s,st in enumerate(plan['stories'],1):
  for k,_ in enumerate(st['acceptance_criteria']+st['non_functional'],1):
    c=f"S{s}.{k}"
    b.append({"criterion":c,"one_behavior":c not in false,"why":false.get(c,"One action with one visible result.")})
    e.append({"criterion":c,"cut":[],"missing":[]})
r['behaviors']=b;r['edge_cases']=e
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 559 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

`10. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['evidence']="Issue: `a re-plan keeps my commits`, `My work goes through the same reviews and checks`; no story names either."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 559 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`11. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['evidence']="Issue: `a re-plan keeps my commits`, `My work goes through the same reviews and checks`; no story names either."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 559 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I blocked the split plan for [#559](https://github.com/dokima-dev/dokima/issues/559) (owner's tests lead the plan; every text has a short and full half). It goes back to the planner. The review file `/tmp/dokima-out/review.json` passes both checks.

**What the planner did:** proposed six stories with 29 criteria and asked you three questions.

**Why it's blocked:**
- **Three of your asks have no criterion:**
  - "a re-plan keeps my commits"
  - "My work goes through the same reviews and checks as agent work"
  - "I can add, change or delete tests, plan and code … then say /review"

  The planner treats the first two as already working. The workflow does reuse your branch on a re-plan, but nothing tests it. The fix is a test for each, or asking you to drop it.
- **Criterion 1.6 rewrites your ask.** You asked for the planner and worker prompts to say what "Verified by" must explain. The plan made that an error message and joined both prompts in one criterion. It should be two criteria, one for each prompt.
- **Four criteria cover two cases each:**
  - 3.1, 3.2 and 3.3 each cover "no short half" and "no full half".
  - 3.5 covers "names code" and "runs past every cap".

  Each should be split in two.

**Your three questions:** I answered none of them, so all three still wait for you:
- Should open issue [#184](https://github.com/dokima-dev/dokima/issues/184) (deletes a closed pull request's branch) be closed? It would delete your branch commits.
- How should you edit a plan, since plans aren't kept on the branch?
- Should a criterion's text live in its test's docstring?

Each one either changes how the system works or needs a call your words don't settle. Your words lean toward yes on the third, but it changes how the system works, so it stays yours.

This is a split proposal, so no tests exist yet; each story writes its own when it is planned. I found no missing edge cases.

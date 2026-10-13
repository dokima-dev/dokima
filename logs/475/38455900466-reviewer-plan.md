# reviewer (plan) for #475

Run: https://github.com/dokima-dev/dokima/actions/runs/38455900466

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-planner.json
> # Issue #475: When a pull request clashes with main, the planner re-plans on the old branch without main, so it cannot change a test that main added and the plan breaks.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [560], "loop": []} -->
> A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/560
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/389
> - https://github.com/dokima-dev/dokima/issues/602
> 
> 
> **User story:** When a pull request falls behind main, its planner sees main's tests and can change them in the same round.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance 

`2. Bash`
```
cd /tmp/pack; cat parent.json; python3 -c "
import json
for f in ['in/01-planner.json','in/03-planner.json','in/04-reviewer-plan.json','in/05-planner.json']:
  d=json.load(open(f)); print('=====',f); print(json.dumps(d,indent=1)[:5000])
"
```

> {"number": null}===== in/01-planner.json
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38453380822",
>  "commit_before": "9fd9fcb4bbb858ce36da2df25a89517ff2929b62",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 181146,
>   "turns": 20,
>   "cost_usd": 1.1382540000000003,
>   "tokens_in": 1207543,
>   "tokens_out": 16924
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/475/38453380822-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38453380822",
>  "handback": {
>   "kind": "user_story",
>   "title": "The planner starts from its branch with main merged in",
>   "summary": "A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.",
>   "user_story": "When a pull request falls behind main, its planner sees main's tests and can change them in the same round.",
>   "acceptance_criteria": [
>    {
>     "text": "On a branch that clashes with main, the planner finds the tests main added since the branch split off.",
>     "words": "When a pull request clashes with main, the planner re-plans on the old branch without main",
>     "source": "https://github.com/dokima-dev/dokima/issues/475",
>     "edge_cases": [
>      {
>       "case": "A branch that merges cleanly with main also gives the planner main's tests.",
>       "test": "tests/test_planner_starts_with_main.py::test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added"
>      }
>     ]
>    },
>    {
>     "tex

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff --stat 9fd9fcb HEAD; cat tests/test_planner_starts_with_main.py; grep -rn "602" AGENTS.md | head
```

> tests/test_planner_starts_with_main.py | 175 +++++++++++++++++++++++++++++++++
>  1 file changed, 175 insertions(+)
> """The planner starts with main merged in, so it can change tests main added (#475).
> 
> When a pull request clashes with main, its planner used to start on the old branch without main: a test main added
> was not there to change, and only the worker's later merge showed the plan broken, costing an extra round.
> 
> These tests run the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin where
> main adds tests/test_main.py after try/issue-57 split off. The planner's run is its checkout ("Starting branch"), a
> stand-in for the agent that copies what it found and changes tests/test_main.py when it is there, and the push. Then
> the worker's own "Starting branch" step runs on a fresh clone, as the next run would.
> 
> With clash=True, main and the branch both change app.py, so the branch clashes with main; with clash=False the
> branch changes only near.py and merges cleanly.
> """
> import os
> import subprocess
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> import test_start as ts  # noqa: E402
> 
> MAINS_TEST = 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
> BRANCHS_TEST = 'def test_a():\n    """A."""\n'
> PLANNERS_TEST = 'def test_m():\n    """Main\'s test, changed by the planner."""\n    assert 1 + 1 == 2\n'
> 
> 
> class Branch(ts.Machine):
>     """A planner run on #57 from checkout to push, then the worker's checkout.
> 
>     Main has m

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | grep -E "^E .*47|passed|failed" | head -20
```

> assert b.planner == "success", f"475.1: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
> E           AssertionError: 475.1: on a branch that clashes with main, the planner started without the test main added (tests/test_main.py found: None)
>             assert b.planner == "success", f"475.2: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
>             assert b.worker == "success", f"475.2: the worker's checkout after the planner failed:\n{b.tail()}"
> E           AssertionError: 475.2: on a branch that clashes with main, the worker started without the planner's change to the test main added; tests/test_main.py is 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
>         assert b.planner == "success", f"475.3: the planner on a branch that merges cleanly failed:\n{b.planner_log[-3000:]}"
> E       AssertionError: 475.3: after the planner's run on a branch that merges cleanly, its branch still lacks main's newest commit
> 3 failed in 1.26s

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "602" --include=*.md --include=*.json . 2>/dev/null | grep -v node_modules | head; git log --all --oneline | grep -i 602 | head; ls /tmp/pack/in
```

> 61bd302 Conversation of run 38326660245
> a8daf52 Conversation of run 38297456024
> f40a1e2 Conversation of run 38294602244
> b936023 Conversation of run 38291774424
> 144c51d Conversation of run 38092546022
> b5adce3 Conversation of run 38066536027
> 13e7e32 Conversation of run 38005806029
> a25b15f planner for #375 (run 38005806029)
> b817b9e Conversation of run 37952602421
> 8d7be2b Conversation of run 37857946023
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-planner.json

**Agent:** Reviewing the plan for #475. All three new tests fail today for the right reason, so I'm writing the hand-back now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner narrowed the third criterion to a branch that merges cleanly with main.",
          "The planner made its test also check a clashing branch keeps its own work."],
  "decided": ["A branch that clashes with main keeps its own work, for the worker to merge."],
  "open": ["Issue 602 still needs closing as a duplicate by the owner."]},
 "verdict": "approve",
 "summary": "The plan covers every ask, and each test fails today because the planner never takes main.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "When a pull request clashes with main, the planner re-plans on the old branch without main", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.1"},
  {"ask": "so it cannot change a test that main added and the plan breaks. The work then needs an extra round", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.2"},
  {"ask": "Yes: this fix covers both. Close #602 as a duplicate of this issue.", "source": "https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153338070", "criterion": "475.3"}
 ],
 "behaviors": [
  {"criterion": "475.1", "one_behavior": true, "why": "One result: the planner's copy holds the tests main added."},
  {"criterion": "475.2", "one_behavior": true, "why": "One result: the worker starts with the planner's change to main's test."},
  {"criterion": "475.3", "one_behavior": true, "why": "One result: a cleanly merging branch holds main's newest commit after planning."}
 ],
 "edge_cases": [
  {"criterion": "475.1", "cut": [], "missing": []},
  {"criterion": "475.2", "cut": [], "missing": []},
  {"criterion": "475.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_planner_starts_with_main.py::test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added", "only_its_behavior": true, "why": "Runs the real checkout; fails today: `tests/test_m
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#475](https://github.com/dokima-dev/dokima/issues/475) (planner re-plans without main's tests), with no blockers.

- **Last round's blocker is fixed.** The third criterion now covers only a branch that merges cleanly with main. Its test also checks that a branch that clashes with main keeps its own work for the worker.
- **Every ask has a criterion.** That includes your comment saying this fix also covers [#602](https://github.com/dokima-dev/dokima/issues/602) (the same cause as this issue). I couldn't read #602 itself from here, so I relied on your comment and the last review's check that the third criterion matches it.
- **All three new tests fail today for the right reason:** the planner never takes main. They don't fail from a crash or a broken setup:
  - On a clashing branch, the planner can't find the test main added.
  - The worker starts with main's version of that test, not the planner's change.
  - A cleanly merging branch still lacks main's newest commit after the planner's run.

One thing is still yours. The planner asked whether you'll close [#602](https://github.com/dokima-dev/dokima/issues/602) as a duplicate yourself, because no agent can close an issue. Your last `/plan` didn't answer, so it still needs closing.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

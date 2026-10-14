# reviewer (plan) for #667

Run: https://github.com/dokima-dev/dokima/actions/runs/38646702227

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (35.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/751e06fc-51ff-496a-abc6-72c1e6e332f2/tool-results/bpdzlrl06.txt
> 
> Preview (first 2KB):
> total 48
> drwxr-xr-x 2 runner runner 4096 Oct 14 22:18 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 22:18 ..
> -rw-r--r-- 1 runner runner 6680 Oct 14 22:18 01-planner.json
> -rw-r--r-- 1 runner runner 6809 Oct 14 22:18 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7497 Oct 14 22:18 03-planner.json
> -rw-r--r-- 1 runner runner 5751 Oct 14 22:18 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6624 Oct 14 22:18 05-planner.json
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6179519809) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercon

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6179519809) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/669
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/432
> 
> 
> **User story:** Any ask, however big, split

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json
```

> []
> {
>  "kind": "user_story",
>  "title": "Code groups criteria into stories by shared files",
>  "summary": "Code works out the stories from the files each criterion changes, and no count rule remains.",
>  "user_story": "Any ask, however big, splits into stories by the code files its criteria change, never by counting.",
>  "acceptance_criteria": [
>   {
>    "text": "Code puts criteria that share a code file, directly or through another criterion, into one story.",
>    "words": "Code groups criteria that share any code file into one story (a sub-issue).",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two criteria joined only through a third criterion that shares a file with each.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     },
>     {
>      "case": "A non-functional requirement shares a code file with an acceptance criterion.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     }
>    ]
>   },
>   {
>    "text": "Code puts criteria with no code file in common into separate stories.",
>    "words": "Criteria with no file in common become separate stories.",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two unrelated criteria whose edge cases are tested in one test file.",
>      "test": 

`4. Bash`
```
cd /tmp/pack; cat issue.md
```

`5. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json
```

> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6179519809) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/669
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/432
> 
> 
> **User story:** Any ask, however big, split

> []
> {
>  "kind": "user_story",
>  "title": "Code groups criteria into stories by shared files",
>  "summary": "Code works out the stories from the files each criterion changes, and no count rule remains.",
>  "user_story": "Any ask, however big, splits into stories by the code files its criteria change, never by counting.",
>  "acceptance_criteria": [
>   {
>    "text": "Code puts criteria that share a code file, directly or through another criterion, into one story.",
>    "words": "Code groups criteria that share any code file into one story (a sub-issue).",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two criteria joined only through a third criterion that shares a file with each.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     },
>     {
>      "case": "A non-functional requirement shares a code file with an acceptance criterion.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     }
>    ]
>   },
>   {
>    "text": "Code puts criteria with no code file in common into separate stories.",
>    "words": "Criteria with no file in common become separate stories.",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two unrelated criteria whose edge cases are tested in one test file.",
>      "test": 

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/05-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; git diff 0ad54df HEAD --stat; git diff 5c1ceec HEAD --stat
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38645184210",
>  "commit_before": "5c1ceecb52a04cd1a897bfd2dad98188ba3a4141",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 4419,
>   "turns": 2,
>   "cost_usd": 0.9148394000000002,
>   "tokens_in": 142109,
>   "tokens_out": 297
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/667/38645184210-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38645184210",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/667#issuecomment-6179519809"
> }
>  dokima/card.py                  |   4 +-
>  tests/test_card_not_verified.py | 109 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_plan_shape.py        |   8 ++-
>  tests/test_size_rule.py         |   2 +-
>  tests/test_story_groups.py      |  47 +++++++++++++----
>  5 files changed, 156 insertions(+), 14 deletions(-)
>  tests/test_size_rule.py    |  2 +-
>  tests/test_story_groups.py | 47 +++++++++++++++++++++++++++++++++++-----------
>  2 files changed, 37 insertions(+), 12 deletions(-)

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 5c1ceec HEAD; cat tests/test_story_groups.py
```

> diff --git a/tests/test_size_rule.py b/tests/test_size_rule.py
> index acceb63..1648e87 100644
> --- a/tests/test_size_rule.py
> +++ b/tests/test_size_rule.py
> @@ -1,4 +1,4 @@
> -"""No caps on criteria or stories, at most 3 owner questions, a size verdict per review.
> +"""No caps on stories, at most 3 owner questions, a size verdict per review.
>  
>  Since #667 no count caps a story; only an empty story is refused."""
>  import os
> diff --git a/tests/test_story_groups.py b/tests/test_story_groups.py
> index 6566f2b..f9c9989 100644
> --- a/tests/test_story_groups.py
> +++ b/tests/test_story_groups.py
> @@ -32,22 +32,33 @@ def crit(text, files, edge=None):
>      return c
>  
>  
> -def story(*criteria):
> -    """A well-formed user story of issue #9 holding these criteria, each with its test."""
> +def nfr(text, files):
> +    """One non-functional requirement changing these files."""
> +    return dict(crit(text, files), why="It matters.")
> +
> +
> +def story(*criteria, nfrs=()):
> +    """A well-formed user story of issue #9 holding these criteria and requirements."""
>      tests = {}
> -    for k, c in enumerate(criteria, 1):
> +    for k, c in enumerate([*criteria, *nfrs], 1):
>          tests[f"9.{k}"] = [c["edge_cases"][0]["test"]] if c.get("edge_cases") else [f"tests/test_jobs.py::test_{k}"]
>      return {"kind": "user_story", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
> -            "user_story": "Slow calls return a job id.", "acceptance_criteria": list(criteria), "non_functional": [],
> -       

`8. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "^(FAILED|E  .*66|[0-9]+ )|passed|failed" | head -30; python3 -m pytest -q tests/test_size_rule.py tests/test_criterion_files.py tests/test_plan_shape.py tests/test_parent_source.py tests/test_rules_split.py 2>&1 | tail -5
```

> E       AssertionError: 667.1: code has no way to group criteria into stories by their files
> E       AssertionError: 667.2: code has no way to group criteria into stories by their files
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> E       AssertionError: 667.4: the old count rules are still stated in dokima/roles/planner.md: '1 to 5 criteria'; dokima/roles/planner.md: 'criteria / 5'; dokima/roles/planner.md: 'at most 5'; dokima/roles/plan-grade.md: '1 to 5 criteria'; dokima/roles/reviewer.md: '1 to 5 criteria'; rules/splitting.md: 'more than five criteria'; the reviewer's size message: '1 to 5 criteria'
> E       AssertionError: 667.5: code has no way to group criteria into stories by their files
> FAILED tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story - AssertionError: 667.1: code has no way to group criteria into stories by their files
> FAILED tests/test_story_groups.py::test_criteria_with_no_code_file_in_common_become_separate_stories - AssertionError: 667.2: code has no way to group criteria into stories by their files
> FAILED tests/test_story_groups.py::test_no_count_of_criteria_or_stories_refuses_a_plan - AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> FAILED tests/test_story_groups.py::test_the_old_count_rules_are_gone_from_the_instructions - AssertionError: 6

**Agent:** Reviewing the plan for issue #667: all five new tests fail today for the right reason. Now checking the owner's latest comment against the plan.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "never_splits_again" -A30 tests/test_size_rule.py | head -45; grep -n "def problems_size" -A15 dokima/agent*.py | head -25
```

> 69:def test_a_story_of_a_parent_never_splits_again():
> 70-    """An issue that is already a story never becomes a feature, whatever its size."""
> 71-    planner.check_size([story(5)], nested=True)
> 72-    with pytest.raises(planner.Garbled, match="never splits again"):
> 73-        planner.check_size([story(2), story(2)], nested=True)
> dokima/agent_checks.py:160:def problems_size(r, ids=()):
> dokima/agent_checks.py-161-    """A plan review must judge each criterion one behavior or not, in `behaviors`, and say
> dokima/agent_checks.py-162-    whether the plan keeps the size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks
> dokima/agent_checks.py-163-    it; a plan that breaks it is never approved."""
> dokima/agent_checks.py-164-    bad = []
> dokima/agent_checks.py-165-    rows = r.get("behaviors") if isinstance(r.get("behaviors"), list) else []
> dokima/agent_checks.py-166-    seen = {str(b.get("criterion")): b for b in rows if isinstance(b, dict)}
> dokima/agent_checks.py-167-    for k in ids:
> dokima/agent_checks.py-168-        b = seen.get(str(k))
> dokima/agent_checks.py-169-        if not b or not isinstance(b.get("one_behavior"), bool) or not str(b.get("why") or "").strip():
> dokima/agent_checks.py-170-            bad.append(f"behaviors has no judgment of criterion {k}: say one_behavior true or false, and why in one line")
> dokima/agent_checks.py-171-    bundled = [k for k, b in seen.items() if b.get("one_behavior") is False]
> dokima/agent_checks.py-172-   

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The test for 667.1 now groups a requirement with the criterion sharing its code file.",
          "The test for 667.4 now also catches the at most five wording."],
  "decided": ["A story of a parent still never splits again, kept by an existing test, not a criterion."],
  "open": ["Asks the owner whether regrouping a grown story under its parent goes to its own issue."]},
 "verdict": "block",
 "summary": "All five tests fail today for the right reason, but the owner's one level answer has no criterion.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "One level: no criterion",
   "text": "The owner answered 'No second split, ever. A story keeps one level.' No criterion carries it; only an edited old test does. Add a criterion for it, proven by `tests/test_size_rule.py::test_a_story_of_a_parent_never_splits_again`.",
   "evidence": "Owner's comment of 2026-10-14T22:05 on #667, point 1; plan.json criteria 667.1 to 667.5 hold no such rule."},
  {"kind": "question", "to": "owner", "label": "Doubt: plan breaks own rule",
   "text": "Under the new rule this plan is two stories: 667.4 shares no code file with the rest. Keep it one story? The review assumes so.",
   "evidence": "plan.json: 667.4 lists only `dokima/agent_checks.py` and markdown; 667.1 to 667.3 and 667.5 list `dokima/planner.py`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Code groups criteria that share any code file into one story (a sub-issue).", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "Criteria with no code file in common become separate stories.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.2"},
  {"ask": "No count of criteria or stories splits or refuses a plan", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.3"},
  {"ask": "today's count rules are gone", "source": "https:/
```

> Exit code 1
> raise 2's label holds 5 words, over its cap of 4: cut 1, keep the facts
> raise 2's text holds 25 words, over its cap of 20: cut 5, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`11. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d["raises"][1]["label"]="Doubt: own rule"
d["raises"][1]["text"]="Under the new rule this plan is two stories: 667.4 shares no code file. Keep one story? Assumed yes."
d["previous_step"]["decided"]=["A story of a parent never splits again, kept by an old test only."]
d["previous_step"]["open"]=["Asks the owner whether regrouping a grown story goes to its own issue."]
json.dump(d,open(p,"w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for issue [#667](https://github.com/dokima-dev/dokima/issues/667) (code groups criteria into stories by shared files). The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What holds up**
- All five new tests fail today for the right reason: code can't group criteria yet, the six-criteria story is refused for holding over five, and the old count wording is still in the instructions.
- The 40 existing tests the plan edits all pass.
- Both blockers from my last review are fixed:
  - 667.1's test now groups a non-functional requirement with the criterion it shares a code file with.
  - 667.4's test now also catches "at most 5".
- Every criterion is one behavior and every test checks only its criterion, so size is ok.

**Why it's blocked**
- **One level, no criterion (for the planner):** you answered "No second split, ever. A story keeps one level." No criterion carries that. Only an edited old test keeps it (`tests/test_size_rule.py::test_a_story_of_a_parent_never_splits_again`). The fix is to add a criterion proven by that test.
- **Regrouping when a story grows:** I marked this ask as missing too. The planner asks you whether this goes to its own issue, and your words don't settle that, so I left it for you.

**New question for you**
- Under the rule this issue builds, this plan would be two stories. Criterion 667.4 (removing the old count wording) shares no code file with the other four criteria. Should it stay one story? I assumed yes.

**Next:** the plan waits for you on two questions, the planner's and mine, then goes back to the planner for the missing criterion.

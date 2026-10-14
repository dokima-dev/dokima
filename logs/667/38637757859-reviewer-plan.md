# reviewer (plan) for #667

Run: https://github.com/dokima-dev/dokima/actions/runs/38637757859

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6178225598) with `/plan`, or say `/review`
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
> - https://

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; cat open_issues.json | head -c 1500; echo; python3 -c "
import json
for f in ['in/02-reviewer-plan.json']:
  d=json.load(open(f)); print(json.dumps(d,indent=1)[:8000])"
```

> {"number": 661}
> [
>  {
>   "number": 692,
>   "title": "Once plans carry no scope field, the card's Scope line shows empty, since it reads that field.",
>   "summary": "Once plans carry no scope field, the card's Scope line shows empty, since it reads that field.",
>   "link": "https://github.com/dokima-dev/dokima/issues/692",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 691,
>   "title": "The run record's Scope list also reads the plan's scope field, so it goes empty unless the derived scope is kept.",
>   "summary": "The run record's Scope list also reads the plan's scope field, so it goes empty unless the derived scope is kept.",
>   "link": "https://github.com/dokima-dev/dokima/issues/691",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 689,
>   "title": "Runs resume from the last good step, and each problem goes to the stage that fixes it",
>   "summary": "In Reza's words (2026-10-14): \"add rerun from checkpoint that is a huge cost saver i think.",
>   "link": "https://github.com/dokima-dev/dokima/issues/689",
>   "filed_by_dokima": false
>  },
>  {
>   "number": 687,
>   "title": "Optional code-quality gates for customers' repos",
>   "summary": "An optional \u03b4okima feature: deterministic quality gates a repo can switch on, checked on new and changed code only so the code never gets worse: function complexity, import rules (no cycles, layering), coverage on changed lines, and mutation testing ",
>   "link": "https://github.com/dokima-dev/dokima/issues/687",
>   "filed_by_dokima": false
>  },
>  {
>   "number":

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --stat -3 | head -60; cat tests/test_story_groups.py
```

> commit 0ad54dfef24e5c358bdadd9d23acb40811ad8200
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 21:07:06 2026 +0000
> 
>     planner for #667 (run 38635830575)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_parent_source.py |  12 ++--
>  tests/test_rules_split.py   |  16 ++---
>  tests/test_size_rule.py     |  33 +++++++++-
>  tests/test_story_groups.py  | 151 +++++++++++++++++++++++---------------------
>  4 files changed, 119 insertions(+), 93 deletions(-)
> 
> commit 0e163311cc763a6f086e7be606ab474fae800247
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:45:39 2026 +0000
> 
>     planner for #667 (run 38629946648)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_card_status.py     |   2 +-
>  tests/test_criterion_files.py |  12 +--
>  tests/test_feature_check.py   |   2 +-
>  tests/test_parent_source.py   |  12 +--
>  tests/test_plan_check.py      |   4 +-
>  tests/test_plan_shape.py      |   3 +-
>  tests/test_rules_split.py     |  16 +++-
>  tests/test_size_rule.py       |  35 +--------
>  tests/test_story_groups.py    | 177 ++++++++++++++++++++++++++++++++++++++++++
>  9 files changed, 211 insertions(+), 52 deletions(-)
> 
> commit 0e584917b5d4977ca0c577986dc8b790340d2cbe
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:0

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "^(FAILED|E +(assert|AssertionError|Failed)|[0-9]+ )" | head -30; python3 -m pytest -q -x -p no:cacheprovider 2>&1 | tail -15
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bxcdxtctg). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 0e58491 HEAD -- tests/test_size_rule.py tests/test_rules_split.py tests/test_parent_source.py tests/test_criterion_files.py tests/test_plan_shape.py tests/test_card_status.py tests/test_feature_check.py tests/test_plan_check.py
```

> diff --git a/tests/test_card_status.py b/tests/test_card_status.py
> index 9d79dad..ff8d919 100644
> --- a/tests/test_card_status.py
> +++ b/tests/test_card_status.py
> @@ -164,7 +164,7 @@ STORY_PLAN = {"kind": "user_story", "title": "Slow calls return a job id", "summ
>                "non_functional": [], "scope": ["dokima/jobs.py"], "out_of_scope": [],
>                "tests": {"9.1": ["tests/test_jobs.py::test_id"]}, "test_changes": {}}
>  FEATURE_PLAN = {"kind": "feature", "title": "Slow calls run as jobs", "summary": SUMMARY, "feature": "Slow calls run as jobs.", "stories": [
> -    {"title": t, "user_story": f"Owners get {t}.", "acceptance_criteria": [{"text": f"{t} works {k}.", "source": "https://github.com/o/r/issues/9", "files": ["dokima/jobs.py"]} for k in (1, 2, 3)],
> +    {"title": t, "user_story": f"Owners get {t}.", "acceptance_criteria": [{"text": f"{t} works {k}.", "source": "https://github.com/o/r/issues/9", "files": [f"dokima/{t.lower()}.py"]} for k in (1, 2, 3)],
>       "non_functional": [], "depends_on": []} for t in ("Jobs", "Results")]}
>  
>  
> diff --git a/tests/test_criterion_files.py b/tests/test_criterion_files.py
> index 07f875b..21baaa9 100644
> --- a/tests/test_criterion_files.py
> +++ b/tests/test_criterion_files.py
> @@ -61,19 +61,19 @@ def test_each_criterion_carries_its_files(record_property, tmp_path):
>      checks the read plan holds each criterion's files, in criterion order, as handed back. Proves 665.1.
>      """
>      record_property("proves", "665.1")
> -    kind, p = 

**Agent:** I'm reviewing the plan for #667: reading the new tests and waiting on the test run.

`6. Bash`
```
sleep 60; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output | tail -30
```

> <tool_use_error>Blocked: sleep 60 followed by: cat /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output tail -30. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`7. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output | tail -30; cd /home/runner/work/dokima/dokima; grep -n "def check_size" -A30 dokima/planner.py; grep -n "def problems_size" -A15 dokima/agent*.py
```

> E       AssertionError: 667.1: code has no way to group criteria into stories by their files
> E       assert False
> E       AssertionError: 667.2: code has no way to group criteria into stories by their files
> E       assert False
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> E       assert 'story 1 holds 6 criteria; each story holds 1 to 5' is None
> E       AssertionError: 667.4: the old count rules are still stated in dokima/roles/planner.md: '1 to 5 criteria'; dokima/roles/planner.md: 'criteria / 5'; dokima/roles/plan-grade.md: '1 to 5 criteria'; dokima/roles/reviewer.md: '1 to 5 criteria'; rules/splitting.md: 'more than five criteria'; the reviewer's size message: '1 to 5 criteria'
> E       assert not ["dokima/roles/planner.md: '1 to 5 criteria'", "dokima/roles/planner.md: 'criteria / 5'", "dokima/roles/plan-grade.md:... '1 to 5 criteria'", "rules/splitting.md: 'more than five criteria'", "the reviewer's size message: '1 to 5 criteria'"]
> E       AssertionError: 667.5: code has no way to group criteria into stories by their files
> E       assert False
> FAILED tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story - AssertionError: 667.1: code has no way to group criteria into stories by their files
> FAILED tests/test_story_groups.py::test_criteria_with_no_code_file_in_common_become_separate_stories - AssertionError: 667.2: code has no way to group criteria

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -niE "five|[^0-9]5[^0-9]|PER_STORY|count" dokima/roles/planner.md dokima/roles/plan-grade.md dokima/roles/reviewer.md rules/splitting.md | head -40; grep -n "PER_STORY\|five\|1 to 5" dokima/*.py | head -30
```

> rules/splitting.md:3:- Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
> rules/splitting.md:7:- When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> dokima/roles/reviewer.md:55:with three short lists, "did", "decided" and "open", at most five lines in all. Write it the way acceptance criteria are
> dokima/roles/reviewer.md:134:things ("X and Y") is two criteria. Each story holds 1 to 5 criteria (acceptance criteria and non-functional requirements
> dokima/roles/reviewer.md:135:together), with no cap on stories; a story split from a parent never splits again. Code counts the stories; you judge, in behaviors, every criterion: is it exactly one behavior (one action, one
> dokima/roles/reviewer.md:149:These guide you; other kinds count too. A missing normal-use case is a blocker for the planner.
> dokima/roles/planner.md:22:- Does it overlap another open issue? (Size is not judged here: code counts it, see Split.)
> dokima/roles/planner.md:36:against the same list and sends it back on 1 to 5.
> dokima

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 115,124p dokima/roles/planner.md; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output | grep -vE "^E " | tail -5
```

> Current runner (the only one Dokima supports today): python3 -m pytest, tests in tests/, and each test names its criterion with
>     record_property("proves", "N.k")
> 
> # Split
> Size is checked by code: each criterion is one behavior quoting the owner, and each story holds 1 to 5 criteria.
> Criteria means acceptance criteria and non-functional requirements together. An issue needs at least criteria / 5
> stories, rounded up, and there is no cap on how many stories it splits into. A story split from a parent never splits
> again: it holds at most 5, and asks the owner which of the rest to drop. More than 3 questions for the owner means the issue is not ready: nothing
> goes on until they answer.
> List every promise of the issue, then give each to exactly one child. Each child: a title, its task in plain words,
> FAILED tests/test_story_groups.py::test_criteria_with_no_code_file_in_common_become_separate_stories - AssertionError: 667.2: code has no way to group criteria into stories by their files
> FAILED tests/test_story_groups.py::test_no_count_of_criteria_or_stories_refuses_a_plan - AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> FAILED tests/test_story_groups.py::test_the_old_count_rules_are_gone_from_the_instructions - AssertionError: 667.4: the old count rules are still stated in dokima/roles/planner.md: '1 to 5 criteria'; dokima/roles/planner.md: 'criteria / 5'; dokima/roles/plan-grade.md: '1 to 5 crite

`10. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 110 python3 -m pytest -q -p no:cacheprovider tests/test_size_rule.py tests/test_rules_split.py tests/test_parent_source.py tests/test_criterion_files.py tests/test_plan_shape.py tests/test_card_status.py tests/test_feature_check.py tests/test_plan_check.py 2>&1 | tail -5
```

> ........................................................................ [ 42%]
> ........................................................................ [ 84%]
> ...........................                                              [100%]
> 171 passed in 24.78s

`11. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Rewrote five tests: code works out the stories, and the plan check holds plans to them.",
   "Split the count criterion in two and kept the empty story refusal."
  ],
  "decided": [
   "A story of a parent still never splits again.",
   "The edge case ask is proven under the second criterion, not its own."
  ],
  "open": [
   "Asked the owner three questions: deeper splits, the folded edge case ask, who names stories."
  ]
 },
 "verdict": "block",
 "summary": "Close: one test misses an old count rule still written, and grouping never tests non-functional requirements.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "667.4: misses a rule",
   "text": "The test for 667.4 passes while the planner's instructions still say a story of a parent holds at most 5. Add `at most 5` to its phrases.",
   "evidence": "`dokima/roles/planner.md` line 122 says `it holds at most 5`; `test_the_old_count_rules_are_gone_from_the_instructions` never checks it."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "667.1: requirements untested",
   "text": "Criteria include non-functional requirements, but no test groups one sharing a code file with an acceptance criterion. Add that case to 667.1's test.",
   "evidence": "`tests/test_story_groups.py` `story()` and `feature()` always set `non_functional` to `[]`; `dokima/roles/planner.md` line 120 counts both."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "Code puts criteria that share any code file into the same story.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "the planner hands back criteria with files and code computes the groups", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "Criteria with no code file in common become separate stories.", "source": "https://github.com/dokima-dev/dokima/issues/667",
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

**Agent:** Shortening one summary line so the hand-back passes the word check.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Rewrote five tests: code works out the stories, and the plan check holds plans to them./Rewrote five tests: code works out stories, and the check holds plans to them./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#667](https://github.com/dokima-dev/dokima/issues/667) (code groups criteria into stories by shared files). It's close, but it has two gaps in its tests, and both go back to the planner. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**What I checked:**
- All five new tests fail today for the right reason: the grouping code doesn't exist yet, the five-criteria cap still applies, and the old rule text is still there.
- The eight test files the planner changed all pass today (171 tests).
- All four of my blockers from the last round are fixed. Code now works out the groups, the bundled criterion is split in two, a story of a parent still can't split again, and a story with no criteria is still refused.
- Every ask in the issue maps to a criterion. The ask "each edge case stays under its criterion and never changes how criteria group" has no criterion of its own; it's tested under 667.2. The planner asked the owner about that.

**Blockers for the planner:**
1. **667.4 misses one old rule.** The test still passes while `dokima/roles/planner.md` line 122 says a story of a parent "holds at most 5". Fix: add `at most 5` to the phrases the test looks for.
2. **667.1 never tests non-functional requirements.** The instructions count them as criteria, but every test sample leaves them empty. So grouping could ignore them and still pass. Fix: add one that shares a code file with an acceptance criterion.

**Left for the owner:** the planner asked three questions:
- Should a story of a parent ever split again?
- Is it fine to prove the edge-case ask under 667.2 instead of its own criterion?
- Is it fine that the planner still names the stories that code works out?

I didn't answer them for the owner. The first and third would change how the system works. For the second, nothing the owner wrote settles it.

`13. Bash`
```
tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/11bd75eb-1069-4b61-8fc6-ca5bcb79dba3/tasks/bxcdxtctg.output
```

> =========================== short test summary info ============================
> FAILED tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story - AssertionError: 667.1: code has no way to group criteria into stories by their files
> assert False
>  +  where False = hasattr(planner, 'story_groups')
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 1092 passed, 1 warning in 595.55s (0:09:55)
> 
> [exited with code 0]

**Agent:** The full test run finished, and it doesn't change the review.

1,092 tests passed. The run then stopped at its first failure, which is the first new test for 667.1. It fails for the expected reason: the grouping code isn't written yet. Because the run stopped there, the tests after it in the suite didn't run in this pass. The eight test files the planner changed had already passed on their own (171 tests).

The verdict is still **block**. Both fixes go back to the planner:
1. The 667.4 test should also look for "at most 5", which `dokima/roles/planner.md` line 122 still says.
2. The 667.1 test should include a non-functional requirement that shares a code file with an acceptance criterion.

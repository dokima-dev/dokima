# reviewer (plan) for #667

Run: https://github.com/dokima-dev/dokima/actions/runs/38634824382

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
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> The plan check holds every plan to stories made of criteria that share code files, with no count rules.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6177382172) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/669
> - https://github.com/dokima-dev/dokima/issues/559
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issu

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:5000])"; cat open_issues.json | head -c 2000
```

> {"number": 661}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38629946648",
>  "commit_before": "0e584917b5d4977ca0c577986dc8b790340d2cbe",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1998077,
>   "turns": 40,
>   "cost_usd": 2.3915142,
>   "tokens_in": 3605544,
>   "tokens_out": 33369
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/667/38629946648-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38629946648",
>  "handback": {
>   "kind": "user_story",
>   "title": "Code groups criteria into stories by shared files",
>   "summary": "The plan check holds every plan to stories made of criteria that share code files, with no count rules.",
>   "user_story": "Any ask, however big, splits into stories by the code files its criteria change, never by counting.",
>   "acceptance_criteria": [
>    {
>     "text": "The plan check rejects a split that puts criteria sharing a code file in different stories.",
>     "words": "Code groups criteria that share any code file into one story (a sub-issue).",
>     "source": "https://github.com/dokima-dev/dokima/issues/661",
>     "files": [
>      "dokima/planner.py",
>      "dokima/roles/planner.md",
>      "rules/splitting.md"
>     ],
>     "edge_cases": [
>      {
>       "case": "Two criteria joined only through a third criterion that shares a file with each.",
>       "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>      }
>     ]
>    },

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; cat tests/test_story_groups.py
```

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
> """Code groups a plan's criteria into stories by the code files they share.
> 
> Covers #667 (story 3 of #661). Criteria that share a code file, directly or through another criterion, belong to one
> story; criteria with no code file in common belong to separate stories. Markdown files never join criteria, and edge
> cases never change the groups. The plan check holds every plan to these groups: a user story whose criteria form more
> than one group is rejected with a reason saying "separate stories", and a split that puts criteria sharing a code file
> into different stories is rejected with a reason naming that file and saying "same story". No count of criteria or
> stories refuses a plan any more, and the instructions no longer 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; grep -n "661\|665\|group" rules/decisions.md | head -30; grep -n "PER_STORY\|def check_size\|never split\|def read_output\|def file_split" -r dokima | head
```

> ## Splitting and the graph
> 
> - Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> dokima/planner.py:51:def read_output(out, number=None):
> dokima/planner.py:131:PER_STORY = 5
> dokima/planner.py:139:def check_size(stories, nested=False):
> dokima/planner.py:145:    total, need = sum(sizes), -(-sum(sizes) // PER_STORY)
> dokima/planner.py:146:    if nested and (len(stories) > 1 or total > PER_STORY):
> dokima/planner.py:147:        raise Garbled(f"this issue is already a story of its parent, so it never splits again: hand back one story of at "
> dokima/pl

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "Error|assert|passed|failed" | head -30; python3 -m pytest -q -x 2>&1 | tail -5; git show HEAD -- tests/test_rules_split.py tests/test_size_rule.py | head -120
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bghcr690y). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/69942ab8-a701-4f49-a386-2a9f96a6c736/tasks/bghcr690y.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** Running the plan's tests now; the full suite is slow, so I'm waiting on it in the background.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 100 python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "^E .*667|passed|failed" | head -20
```

> E       AssertionError: 667.1: a split with two criteria sharing dokima/jobs.py in different stories was not rejected naming the file and saying 'same story': None
> E       AssertionError: 667.2: a story whose criteria share no code file was not rejected saying 'separate stories': None
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> E       AssertionError: 667.4: criteria sharing only a markdown file were grouped into one story: None
> E       AssertionError: 667.5: edge cases in one test file joined criteria with no code file in common: None
> 5 failed in 0.08s

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_rules_split.py tests/test_size_rule.py tests/test_parent_source.py | head -150
```

> commit 0e163311cc763a6f086e7be606ab474fae800247
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:45:39 2026 +0000
> 
>     planner for #667 (run 38629946648)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_parent_source.py b/tests/test_parent_source.py
> index 7c81cee..0645cbb 100644
> --- a/tests/test_parent_source.py
> +++ b/tests/test_parent_source.py
> @@ -56,14 +56,15 @@ def story(sources):
>  
>  def feature(sources):
>      """A two-story split of #331 whose first story's criteria cite these sources."""
> -    return {"kind": "feature", "summary": "Two stories.", "feature": "Cards show what is true now.",
> +    return {"kind": "feature", "title": "Cards show what is true now", "summary": "Two stories.",
> +            "feature": "Cards show what is true now.",
>              "stories": [{"title": "One", "user_story": "u1", "non_functional": [], "depends_on": [],
>                           "acceptance_criteria": [{"text": f"Criterion {k} holds.", "source": s, "files": ["dokima/x.py"]}
>                                                   for k, s in enumerate(sources[:3], 1)]},
>                          {"title": "Two", "user_story": "u2", "non_functional": [], "depends_on": [0],
> -                         "acceptance_criteria": [{"text": f"Criterion {k} holds.", "source": s, "files": ["dokima/x.py"]}
> +                         "acceptance_criteria": [{"text": f"Criterion {

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Wrote five tests, one per criterion; all fail today for the right reason.",
   "Dropped the old five-per-story tests and updated nine others."
  ],
  "decided": [
   "The planner still picks stories; the plan check only refuses wrong groups.",
   "A story of a parent may now split again."
  ],
  "open": [
   "Asked whether markdown-only criteria become separate stories."
  ]
 },
 "verdict": "block",
 "summary": "The plan checks the planner's stories instead of having code build them, and drops two rules unasked.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "667.1: code never groups",
   "text": "The ask is that code computes the groups from criteria; the plan only refuses the planner's wrong groups. Add a criterion and test where code builds stories, or ask the owner.",
   "evidence": "Issue Context: 'the planner hands back criteria with files and code computes the groups'; every `test_story_groups.py` test only checks refusals."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "667.3: unasked deeper splits",
   "text": "The plan lets a story of a parent split again, making a third level. No ask says so. Raise it as a question for the owner, or keep the rule.",
   "evidence": "`rules/splitting.md` says '2 or more children, one level'; `test_no_count_of_criteria_or_stories_refuses_a_plan` expects a child split accepted."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "667.3: two behaviors",
   "text": "667.3 bundles two behaviors: no count refuses a plan, and the written count rules are gone. Split it into two criteria, each with its own test.",
   "evidence": "Criterion 667.3 text joins both with 'and'; its one test checks plan refusals and instruction wording."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Empty story guard lost",
   "text": "Dropping `test_a_story_over_five_or_empty_is_
```

> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts
> rc=1

`9. Bash`
```
sed -i 's/Add a criterion and test where code builds stories, or ask the owner./Add a criterion and test where code builds stories, or ask./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`10. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/Add a criterion and test where code builds stories, or ask the owner./Add a criterion and test where code builds stories, or ask./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

**Agent:** I blocked the plan for #667 (stories grouped by the code files they change). The review is at `/tmp/dokima-out/review.json` and passes both hand-back checks.

All five new tests fail today, and each fails because the feature is missing, not because the test is broken. I didn't wait for the full test suite; it was still running in the background.

**Blockers sent back to the planner:**
- **Code never builds the groups (667.1):** the issue says "the planner hands back criteria with files and code computes the groups." In the plan, the planner still picks the stories and the check only refuses wrong ones. I marked that ask as missing.
- **Deeper splits nobody asked for (667.3):** the plan lets a story that was split off a parent split again. `rules/splitting.md` says splits go "one level", and nobody asked to change that. The planner should ask you, or keep the rule.
- **667.3 is two things in one:** "no count refuses a plan" and "the written count rules are gone" need separate criteria and tests. Because of this, the plan fails the size rule.
- **The empty-story check is lost:** removing the old five-per-story test also removes the check that refuses a story with no criteria. You asked to drop the caps, not that check.

**The planner's question:** it asked whether criteria that change only the same markdown file become separate stories. I answered yes for you, quoting the issue: "Files ending in .md are ignored when grouping."

`11. Bash`
```
grep -E "passed|failed|^FAILED|Error" /tmp/claude-1001/-home-runner-work-dokima-dokima/69942ab8-a701-4f49-a386-2a9f96a6c736/tasks/bghcr690y.output | head -20
```

> E       AssertionError: 667.1: a split with two criteria sharing dokima/jobs.py in different stories was not rejected naming the file and saying 'same story': None
> tests/test_story_groups.py:78: AssertionError
> E       AssertionError: 667.2: a story whose criteria share no code file was not rejected saying 'separate stories': None
> tests/test_story_groups.py:99: AssertionError
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> tests/test_story_groups.py:118: AssertionError
> E       AssertionError: 667.4: criteria sharing only a markdown file were grouped into one story: None
> tests/test_story_groups.py:152: AssertionError
> E       AssertionError: 667.5: edge cases in one test file joined criteria with no code file in common: None
> tests/test_story_groups.py:172: AssertionError
> FAILED tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story - AssertionError: 667.1: a split with two criteria sharing dokima/jobs.py in different stories was not rejected naming the file and saying 'same story': None
> FAILED tests/test_story_groups.py::test_criteria_with_no_code_file_in_common_become_separate_stories - AssertionError: 667.2: a story whose criteria share no code file was not rejected saying 'separate stories': None
> FAILED tests/test_story_groups.py::test_no_count_of_criteria_or_stories_refuses_a_plan - AssertionError: 667.3: a story of 6 criteria sharing one code file was

**Agent:** The background run finished, but it doesn't tell us much. It stopped at the first failure, which was one of the plan's new tests and is expected to fail today. 762 tests passed before it stopped, and everything after that point never ran, so the full suite is still unchecked.

The run backs up what the review says: all five new tests fail with the feature-missing messages for 667.1 to 667.5.

The review is unchanged: it stays blocked on the four points I sent the planner.

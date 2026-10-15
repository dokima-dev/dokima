# reviewer (plan) for #707

Run: https://github.com/dokima-dev/dokima/actions/runs/38687223408

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (34.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/eecafc6e-42fe-4a18-982e-65907757c233/tool-results/bvxjqbmkv.txt
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
> # Issue #707: The plan check locks my tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 708 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/710
> - https://github.com/dokima-dev/dokima/issues/712
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/dokima-dev/dokima/issues/714
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/708
> 
> 
> **User story:** Tests the owner commits stay exactly as written, and every new test explains itself in one shape.
> 
> <img src="https://raw.githubusercont

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #707: The plan check locks my tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 708 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/710
> - https://github.com/dokima-dev/dokima/issues/712
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/dokima-dev/dokima/issues/714
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/708
> 
> 
> **User story:** Tests the owner commits stay exactly as written, and every new test explains itself in one shape.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A plan t

`3. Bash`
```
cd /tmp/pack; cat plan.json; echo ----; cat open_blockers.json; echo ---; cat parent.json | head -50
```

> {
>  "kind": "user_story",
>  "title": "Plan check locks owner tests and checks test docstrings",
>  "summary": "The plan check keeps the owner's tests as written and holds new tests to one docstring shape.",
>  "user_story": "Tests the owner commits stay exactly as written, and every new test explains itself in one shape.",
>  "acceptance_criteria": [
>   {
>    "text": "A plan that changes a test the owner committed is rejected, naming that test.",
>    "words": "A plan built on my tests keeps every one unchanged",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One change to one test; the owner named no other case."
>   },
>   {
>    "text": "A plan that deletes a test the owner committed is rejected, naming that test.",
>    "words": "agents may propose more but never change or drop mine",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One deleted test; the owner named no other case."
>   },
>   {
>    "text": "A plan that files no criterion for a test the owner committed is rejected, naming that test.",
>    "words": "maps each to a criterion",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One test left out; the owner named no other case."
>   },
>   {
>    "text": "A new or changed test with no User line in its docstring is rejected, naming the test.",
>    "words": "

`4. Bash`
```
cd /tmp/pack; cat issue.md
```

`5. Bash`
```
cd /tmp/pack; cat plan.json; echo ----; cat open_blockers.json; echo ---; cat parent.json | head -50
```

> # Issue #707: The plan check locks my tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 708 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/710
> - https://github.com/dokima-dev/dokima/issues/712
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/dokima-dev/dokima/issues/714
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/708
> 
> 
> **User story:** Tests the owner commits stay exactly as written, and every new test explains itself in one shape.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A plan t

> {
>  "kind": "user_story",
>  "title": "Plan check locks owner tests and checks test docstrings",
>  "summary": "The plan check keeps the owner's tests as written and holds new tests to one docstring shape.",
>  "user_story": "Tests the owner commits stay exactly as written, and every new test explains itself in one shape.",
>  "acceptance_criteria": [
>   {
>    "text": "A plan that changes a test the owner committed is rejected, naming that test.",
>    "words": "A plan built on my tests keeps every one unchanged",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One change to one test; the owner named no other case."
>   },
>   {
>    "text": "A plan that deletes a test the owner committed is rejected, naming that test.",
>    "words": "agents may propose more but never change or drop mine",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One deleted test; the owner named no other case."
>   },
>   {
>    "text": "A plan that files no criterion for a test the owner committed is rejected, naming that test.",
>    "words": "maps each to a criterion",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One test left out; the owner named no other case."
>   },
>   {
>    "text": "A new or changed test with no User line in its docstring is rejected, naming the test.",
>    "words": "

`6. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['02-reviewer-plan.json']:
  d=json.load(open(f)); print(json.dumps(d,indent=1)[:8000])
"; cat ../open_issues.json | head -c 1500
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38676692581",
>  "commit_before": "1b90279db90c47195e27a721c96dd7c2eec2bf75",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 152952,
>   "turns": 14,
>   "cost_usd": 0.7057511999999999,
>   "tokens_in": 688359,
>   "tokens_out": 7832
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/707/38676692581-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38676692581",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote fourteen criteria, each with one test that fails today.",
>     "The planner moved sample tests in older test files to the new docstring shape."
>    ],
>    "decided": [
>     "Each User, Verified by and Edge line holds fifteen words, not counting its label."
>    ],
>    "open": [
>     "The planner asks whether the owner's own tests skip the new docstring rules."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan covers every ask, but the owner-test lock can still be opened by giving a reason.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "707.1 and 707.2: weak",
>     "text": "Code letting a stated reason unlock your tests passes both. Fix: also give the owner's test a reason, and still expect rejection.",
>     "evidence": "`dokima/planner.py:442` says `changed or deleted, with no reason`, which holds both `chang` and `delet`; both tests set no reason.",
>     "raised_by": "reviewer",
>   

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git diff main --stat; grep -rn "6184903296" /tmp/pack | head; cat tests/test_owner_tests_and_docstrings.py
```

> dc65277 planner for #707 (run 38685237520)
> 959fc23 Merge remote-tracking branch 'origin/main' into try/issue-707
> f71d144 A role can run on Kimi Code CLI (#726)
>  .dokima/agents.yml                       |   8 -
>  dokima/agent_kimi.py                     |   6 +-
>  dokima/setup.py                          |   2 +-
>  tests/test_agent_kimi.py                 |  10 +-
>  tests/test_body.py                       |   5 +-
>  tests/test_new_test_check.py             |  43 +--
>  tests/test_owner_tests_and_docstrings.py | 452 +++++++++++++++++++++++++++++++
>  tests/test_plan_check.py                 |   8 +-
>  tests/test_replan_check.py               |  15 +-
>  tests/test_setup.py                      |  12 +-
>  tests/test_word_caps.py                  |  17 +-
>  11 files changed, 521 insertions(+), 57 deletions(-)
> /tmp/pack/plan.json:152:   "source": "https://github.com/dokima-dev/dokima/issues/707#issuecomment-6184903296",
> /tmp/pack/plan.json:166:   "source": "https://github.com/dokima-dev/dokima/issues/707#issuecomment-6184903296",
> /tmp/pack/in/03-planner.json:170:    "source": "https://github.com/dokima-dev/dokima/issues/707#issuecomment-6184903296",
> /tmp/pack/in/03-planner.json:184:    "source": "https://github.com/dokima-dev/dokima/issues/707#issuecomment-6184903296",
> """User: The plan check locks the owner's tests and holds new tests to one shape.
> 
> Agent: Every test here runs the check the way the agent workflow runs it, `python3 -m dokima.planner check 9 OUT`,
> through `planner.main`, inside

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main...HEAD --stat; python3 -m pytest -q tests/test_owner_tests_and_docstrings.py 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed" | cut -c1-400
```

> tests/test_body.py                       |   5 +-
>  tests/test_new_test_check.py             |  43 +--
>  tests/test_owner_tests_and_docstrings.py | 452 +++++++++++++++++++++++++++++++
>  tests/test_plan_check.py                 |   8 +-
>  tests/test_replan_check.py               |  15 +-
>  tests/test_word_caps.py                  |  17 +-
>  6 files changed, 507 insertions(+), 33 deletions(-)
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_changes_the_owners_test_is_rejected_naming_it - AssertionError: 707.1: a plan that changes a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_deletes_the_owners_test_is_rejected_naming_it - AssertionError: 707.2: a plan that deletes a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_files_no_criterion_for_the_owners_test_is_rejected_naming_it - AssertionError: 707.3: a plan that files no criterion for a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it[new test] - AssertionError: 707.4: a new test with no User part in its docstring was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it[changed older test] - AssertionError: 707.4: a changed test with no User part in its docstring was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_n

**Agent:** Tests all fail today for the feature's reasons. Now checking the planner's edits to older test files.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main...HEAD -- tests/test_body.py tests/test_plan_check.py tests/test_replan_check.py tests/test_new_test_check.py tests/test_word_caps.py
```

> diff --git a/tests/test_body.py b/tests/test_body.py
> index 6d8c7ac..6b14d1d 100644
> --- a/tests/test_body.py
> +++ b/tests/test_body.py
> @@ -135,7 +135,10 @@ def run_card(monkeypatch, github, current):
>  
>  REASON = "the owner's part below the marker would change"
>  
> -PLAN_TESTS = ('def test_card(record_property):\n    """The card shows.\n\n    Proves 40.1.\n    """\n'
> +# The planner's new test file, in the docstring shape #707 asks for: User and Verified by lines, then an Agent part.
> +PLAN_TESTS = ('"""User: Sample tests for the card.\n\nAgent: They fail until the card exists.\n"""\n\n\n'
> +              'def test_card(record_property):\n    """User: The card shows.\n    Verified by: drawing the card.\n\n'
> +              '    Agent: Proves 40.1.\n    """\n'
>                '    record_property("proves", "40.1")\n    assert False\n')
>  PLAN = {"kind": "user_story", "title": "Every issue shows a card", "summary": "Every issue shows a card.", "user_story": "Owners see a card on every issue.",
>          "acceptance_criteria": [{"text": "The issue shows a card on top.", "source": f"https://github.com/{REPO}/issues/{NUMBER}", "no_edge_cases": "a sample criterion", "files": ["dokima/card.py"]}],
> diff --git a/tests/test_new_test_check.py b/tests/test_new_test_check.py
> index 4cce062..89e33a8 100644
> --- a/tests/test_new_test_check.py
> +++ b/tests/test_new_test_check.py
> @@ -19,13 +19,17 @@ from dokima import planner  # noqa: E402
>  from tests.test_plan_check import ROOT, STORY, check  # noqa: E402,

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_body.py tests/test_plan_check.py tests/test_replan_check.py tests/test_new_test_check.py tests/test_word_caps.py 2>&1 | tail -5
```

> ::warning title=Over the word cap::tests/test_jobs.py has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>   ?                                    ++++++++++++++++++
>     ::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>     plan
> 1 failed, 90 passed in 67.55s (0:01:07)

`11. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp && python3 - <<'EOF'
import json
P="tests/test_owner_tests_and_docstrings.py::"
S559="https://github.com/dokima-dev/dokima/issues/559"
C559=S559+"#issuecomment-6131843348"
C707="https://github.com/dokima-dev/dokima/issues/707#issuecomment-6184903296"
plan=json.load(open("/tmp/pack/plan.json"))
crits=plan["acceptance_criteria"]+plan["non_functional"]
asks=[]
for i,c in enumerate(crits,1):
    asks.append({"ask":c["words"],"source":c["source"],"criterion":f"707.{i}"})
asks.append({"ask":"no agent edits it","source":C707,"criterion":"707.1"})
behaviors=[{"criterion":f"707.{i}","one_behavior":True,"why":"One case, one result."} for i in range(1,17)]
edge=[{"criterion":f"707.{i}","cut":[],"missing":[]} for i in range(1,17)]
edge[13]["missing"]=["The plan raises a question for the owner about some other test."]
edge[14]["missing"]=["The plan raises a question for the owner about some other test."]
tests=[]
for k,v in plan["tests"].items():
    for t in v:
        tests.append({"test":t,"only_its_behavior":True,"why":"Runs the real check; fails today because the feature is missing."})
for t in tests:
    if t["test"].endswith(("raised_to_the_owner",)):
        t["why"]="Runs the real check, but any question for the owner unlocks it."
blk=lambda c: {"kind":"blocker","to":"planner","label":f"{c}: weak",
  "text":f"Code letting any question for the owner unlock it passes. Fix: also raise a question naming another test, and still expect rejection naming `test_owner_id`.",
  "evidence":"`owner_misses_bar` only tries no question, then one naming `test_owner_id`; nothing checks the naming."}
r={"previous_step":{"did":["The planner gave the owner's test a reason in two tests, still expecting rejection.",
   "The planner added two criteria from the owner's answer: their tests meet the same bar."],
  "decided":["An owner's test that misses the bar is raised to the owner as a question."],
  "open":[]},
 "verdict":"block",
 "summary":"The plan covers 
```

> rc=0

**Agent:** I blocked the planner's plan for [#707](https://github.com/dokima-dev/dokima/issues/707) (locks the owner's tests and checks test docstrings). It has 2 blockers, both for the planner, and the review passes both checks.

**What I found**
- Every ask is covered. That includes your answer that your tests meet the same bar as any test, are raised to you as a question when they miss it, and are never edited.
- Last round's blocker is fixed. The tests for changing or deleting your test now give a reason and still expect the plan to be rejected.
- I ran all 20 new test cases. Each fails today because the feature is missing, not because a test is broken.
- I also ran the 5 older test files the planner adjusted (91 tests). One fails today: the word-cap test, which expects the new "User:" label not to count toward the 15 words. That is the feature this issue builds.

**The two blockers (criteria 707.14 and 707.15)**
- Both tests try only two plans: one with no question for you, and one with a question that names your test.
- Code that lets *any* question for you through would pass them. Plans often raise unrelated questions, so one of your tests that misses the bar could slip through.
- The fix: also try a plan whose question names a different test, and expect it to be rejected, naming your test.

The hand-back is in `/tmp/dokima-out/review.json`.

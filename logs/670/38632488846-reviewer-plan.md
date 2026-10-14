# reviewer (plan) for #670

Run: https://github.com/dokima-dev/dokima/actions/runs/38632488846

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #670: Card shows criteria with no test as not verified
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [], "loop": []} -->
> Red first stays, untestable asks become questions, and the card marks criteria with no test as not verified.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/546
> 
> 
> **User story:** The owner sees at a glance which criteria no automated test proves.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The plan check rejects a new test that a

`2. Bash`
```
cd /tmp/pack/in; for f in *; do echo "== $f"; cat $f | head -c 6000; echo; done
```

> == 01-planner.json
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38629962249",
>  "commit_before": "0e584917b5d4977ca0c577986dc8b790340d2cbe",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 223304,
>   "turns": 27,
>   "cost_usd": 1.2216595999999997,
>   "tokens_in": 1503693,
>   "tokens_out": 18930
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/670/38629962249-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38629962249",
>  "handback": {
>   "kind": "user_story",
>   "title": "Card shows criteria with no test as not verified",
>   "summary": "Red first stays, untestable asks become questions, and the card marks criteria with no test as not verified.",
>   "user_story": "The owner sees at a glance which criteria no automated test proves.",
>   "acceptance_criteria": [
>    {
>     "text": "The plan check rejects a new test that already passes before work starts.",
>     "words": "Red first stays: every criterion's test fails on main before work starts.",
>     "source": "https://github.com/dokima-dev/dokima/issues/661",
>     "files": [
>      "dokima/planner.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "A new test that is skipped today is rejected too.",
>       "test": "tests/test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so"
>      }
>     ]
>    },
>    {
>     "text": "The planner's instructions say an ask that cannot be tested becomes a question for the owner.",
>     "

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git show --stat HEAD | head; cat tests/test_card_not_verified.py; python -m pytest -q tests/test_card_not_verified.py tests/test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so "tests/test_plan_shape.py::test_prompt_teaches_the_terms_voice_and_every_example" 2>&1 | tail -30
```

> 8cc48d9 planner for #670 (run 38629962249)
> 0e58491 Each criterion lists the code files it changes (#688)
> ac5c8e7 A clash in a test file goes to the planner (#663)
> commit 8cc48d9b7e6780b1db8ef64b25092adc92df7e68
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:15:51 2026 +0000
> 
>     planner for #670 (run 38629962249)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_card_not_verified.py | 109 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_plan_shape.py        |   8 ++-
> """A criterion with no automated test shows on the card as not verified.
> 
> Issue #670, from #661. The owner: "An ask that can't be checked becomes a question to me, or shows on the card as not
> verified."
> 
> Each test draws the issue card with `dokima/card.render` from an approved plan in which some criteria list a test and
> others list none, then reads the words under each criterion's bullet: the bullet itself and the indented lines below
> it, up to the next criterion. A criterion with no test must read "not verified" there; one with a test must not.
> """
> import os
> import re
> import sys
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from dokima import card, plan  # noqa: E402
> 
> REPO = "o/r"
> ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
> ASK = "https://github.com/o/r/issues/40"
> TESTS = {"tests/test_a.py::test_one": {"verified_by": "The first thing runs.",
>        

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_plan_shape.py; grep -n "question" dokima/roles/planner.md | head; grep -n -i "manual\|not verified" dokima/card.py | head
```

> commit 8cc48d9b7e6780b1db8ef64b25092adc92df7e68
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:15:51 2026 +0000
> 
>     planner for #670 (run 38629962249)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_plan_shape.py b/tests/test_plan_shape.py
> index c3c2e00..cb06825 100644
> --- a/tests/test_plan_shape.py
> +++ b/tests/test_plan_shape.py
> @@ -32,9 +32,15 @@ def test_prompt_teaches_the_terms_voice_and_every_example(record_property):
>      """The planner's prompt teaches the agreed terms, the product voice and an example for every rule.
>  
>      Reads the prompt and looks for each term, each of the owner's six approved examples, and one
> -    example per rule (user story, feature, bug fix, non-functional, scope, docstring, question, concern).
> +    example per rule (user story, feature, bug fix, non-functional, scope, docstring, question, concern). It also
> +    checks the prompt says an ask that cannot be tested becomes a question for the owner, never dropped (#670).
>      """
>      record_property("proves", "138.1")
> +    record_property("proves", "670.2")
> +    assert "Raise a question for the owner only where the owner's words allow two readings or an ask cannot be tested" \
> +        in PROMPT, "670.2: the prompt never says an ask that cannot be tested becomes a question for the owner"
> +    assert "Such an ask becomes a question, never dropped." in PROMPT, \
> + 

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["It kept the same plan after the owner's answer."],
  "decided": ["Red first and the question rule are only pinned; the card changes."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan does what the owner said: pin the two rules that hold, and mark untested criteria on the card.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Red first stays: every criterion's test fails on main before work starts.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.1"},
  {"ask": "An ask that can't be checked becomes a question to me", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.2"},
  {"ask": "or shows on the card as not verified.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.3"},
  {"ask": "Yes, only pin them and change the card.", "source": "https://github.com/dokima-dev/dokima/issues/670", "criterion": "670.3"}
 ],
 "behaviors": [
  {"criterion": "670.1", "one_behavior": true, "why": "One rejection: a new test that passes today."},
  {"criterion": "670.2", "one_behavior": true, "why": "One instruction in the planner's prompt."},
  {"criterion": "670.3", "one_behavior": true, "why": "One card label for a criterion with no test."}
 ],
 "edge_cases": [
  {"criterion": "670.1", "cut": [], "missing": []},
  {"criterion": "670.2", "cut": [], "missing": []},
  {"criterion": "670.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so", "only_its_behavior": true, "why": "Runs the real check; rejects passing and skipped tests, accepts failing ones."},
  {"test": "tests/test_plan_shape.py::test_prompt_teaches_the_terms_voice_and_every_example", "only_its_behavior": true, "why": "Its 670.2 lines check only the question rule and fail if it goes."},
  {"test": "tests/test_card_not_ve
```

> 0

**Agent:** I approved the plan for [#670](https://github.com/dokima-dev/dokima/issues/670) (card shows untested criteria as not verified), with no blockers. The review is saved in `/tmp/dokima-out/review.json` and passes both hand-back checks.

- **Your answer:** you said "Yes, only pin them and change the card." The planner kept the same plan, which does exactly that.
- **Tests:** I ran them on this branch.
  - The three new card tests fail today because the card has no "not verified" label yet.
  - The test for blocking a new test that already passes, and the test for the question rule, pass today. That's expected, since both only pin rules that already hold.
- **Asks:** all three asks from [#661](https://github.com/dokima-dev/dokima/issues/661) (stories split by the files they change) each have a criterion, and so does your reply.
- **Criteria and edge cases:** each criterion is one behavior, every test checks only its own criterion, and no edge cases are missing.

I linked your reply to the issue page, not to the comment itself, because the comment's link wasn't in my files.

The planner's second question, whether to allow a criterion with no test, is still yours. I read your reply as "no" but didn't settle it for you: your words and "No owner steps" don't say so outright. The plan assumes no.

There were no open blockers from earlier rounds to answer.

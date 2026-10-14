# reviewer (plan) for #670

Run: https://github.com/dokima-dev/dokima/actions/runs/38630620973

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
> # Issue #670: Red first stays and unproven criteria show on the card
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [], "loop": []} -->
> Red first stays, untestable asks become questions, and the card marks criteria with no test as not verified.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/670#issuecomment-6177384292) with `/plan`, or say `/review`
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
> - <img src="https:/

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:6000])"; grep -rn "Red first stays\|can't be checked\|not verified" parent.json | head; cat in/01-planner.json | head -c 1500
```

> {
>  "number": 661
> }
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
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/ | head -300
```

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
>  2 files changed, 116 insertions(+), 1 deletion(-)
> commit 8cc48d9b7e6780b1db8ef64b25092adc92df7e68
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 20:15:51 2026 +0000
> 
>     planner for #670 (run 38629962249)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_card_not_verified.py b/tests/test_card_not_verified.py
> new file mode 100644
> index 0000000..df56cf0
> --- /dev/null
> +++ b/tests/test_card_not_verified.py
> @@ -0,0 +1,109 @@
> +"""A criterion with no automated test shows on the card as not verified.
> +
> +Issue #670, from #661. The owner: "An ask that can't be checked becomes a question to me, or shows on the card as not
> +verified."
> +
> +Each test draws the issue card with `dokima/card.render` from an approved plan in which some criteria list a test and
> +others list none, then reads the words under each criterion's bullet: the bullet itself and the indented lines below
> +it, up to the next criterion. A criterion with no test must read "no

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "manual" dokima/*.py | head -30; grep -n "has no test" dokima/*.py; grep -n -i "not verified\|unverified" -r dokima rules | head
```

> dokima/checks.py:9:A manual fix Dokima's app opens with no linked issue gets one "Manual fix" check that runs all tests.
> dokima/checks.py:28:MANUAL_FIX = [{"id": "manual-fix", "name": "Manual fix: all tests pass", "tests": "tests"}]
> dokima/checks.py:62:    A pull request Dokima's app opened with no linked issue is a manual fix: one check that runs all tests."""
> dokima/checks.py:65:            return MANUAL_FIX
> dokima/planner.py:393:    out += [f"criterion {k} has no test" for k in sorted(keys - proven)]
> dokima/audit.py:33:def unverified(what, e):
> dokima/audit.py:131:        return [f"Auto-merge is not verified: GitHub said `{reason(e)}` when the audit read the merge queue "
> dokima/audit.py:166:            lines.append(unverified(what, e))

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 370,400p dokima/planner.py; grep -n -i "manual\|cannot be tested\|can't be checked\|not verified" rules/*.md dokima/roles/*.md | head -30
```

> def missing_tests(names):
>     """The named tests (path::name) that are not in the repo: no such file, or no such test in it."""
>     return [t for t in names if t.partition("::")[2] not in test_functions(read_now(t.partition("::")[0]))]
> 
> 
> def problems(number, plan, files, tc, declared=None):
>     """What is wrong with a plan and the tests it touched; empty when it can be posted.
> 
>     Given the tests the plan declares, each must be in the repo and filed under one of the plan's criteria, and an
>     older test already in the repo counts as proof of the criteria it is filed under.
>     """
>     out = [f"{p} is outside tests/; the planner may only write tests" for p in files if not p.startswith("tests/")]
>     if not tc["added"] and not tc["changed"]:
>         out.append("the plan came with no tests")
>     keys = {f"{number}.{k}" for k in range(1, len(plan["criteria"]) + 1)}
>     proven = {k for ks in proving(tc).values() for k in ks}
>     if declared is not None:
>         names = sorted(declared_by_test(declared))
>         out += [f"the plan names {t}, which is not in the repo" for t in missing_tests(names)]
>         out += [f"tests are filed under {k}, which is not a criterion of this plan ({number}.1 to {number}.{len(keys)})"
>                 for k in sorted(declared) if k not in keys]
>         proven |= {k for k, ts in declared.items() if ts}
>     out += [f"criterion {k} has no test" for k in sorted(keys - proven)]
>     out += [f"{t} proves {k}, which is not a criterion of this plan" for t, k

**Agent:** Reviewing the plan for #670: running its tests now to see which fail today and why.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_card_not_verified.py "tests/test_plan_shape.py::test_prompt_teaches_the_terms_voice_and_every_example" "tests/test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so" 2>&1 | tail -30
```

> """A non-functional requirement with no test reads not verified in its fold.
>     
>         Draws the card of a plan with one non-functional requirement and no test filed for it, and checks its bullet,
>         inside the Non-functional requirements fold, reads not verified. Proves 670.3."""
>         record_property("proves", "670.3")
>         text = draw(story({"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_one"]},
>                           nfr=["Nothing leaks"]))
>         seen = under(text, "Nothing leaks", "670.3")
> >       assert "not verified" in seen.lower(), \
>             f"670.3: the non-functional requirement with no test does not show as not verified on the card: {seen}"
> E       AssertionError: 670.3: the non-functional requirement with no test does not show as not verified on the card: - Non-functional requirement: Nothing leaks
> E       assert 'not verified' in '- non-functional requirement: nothing leaks'
> E        +  where '- non-functional requirement: nothing leaks' = <built-in method lower of str object at 0x7fae02131530>()
> E        +    where <built-in method lower of str object at 0x7fae02131530> = '- Non-functional requirement: Nothing leaks'.lower
> 
> tests/test_card_not_verified.py:108: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_card_not_verified.py::test_a_criterion_with_no_test_shows_as_not_verified - AssertionError: 670.3: the criterion with no test does not show as not

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 100,160p tests/test_new_test_check.py
```

> write_jobs(jobs(unique_doc=doc))
>     rc, why = legacy({"plan.json": plan}, "155.1")
>     assert rc == 1, f"155.1: a new test with the docstring {doc!r} was accepted; it needs a one-sentence first line"
>     assert "test_unique" in why, f"155.1: the reason does not name the test test_unique: {why!r}"
>     assert "test_id" not in why, f"155.1: the reason also names test_id, whose summary is good: {why!r}"
>     assert "test_legacy" not in why, \
>         f"155.1: the reason names the changed older test test_legacy, which is not new and needs no summary: {why!r}"
> 
> 
> # 155.2: every new test is run on today's code; one that passes or is skipped is rejected
> 
> @pytest.mark.parametrize("body", [
>     "assert True",
>     'pytest.skip("not yet")',
>     "@skip",
> ], ids=["passes", "skips itself", "marked skip"])
> def test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so(record_property, legacy, body):
>     """A new test that passes or is skipped on today's code is rejected, naming it and saying it passes today.
> 
>     Throughout, an older test is changed (same name, new body) and passes today: only new tests must fail, so it must
>     never be rejected or named. First checks new tests that fail today pass the check beside it: a failing assert, a
>     name the feature has not defined yet, and a whole file whose import of the missing feature errors. Then makes
>     test_unique pass or skip, runs the check, and checks the reason names test_unique (not test_id, which still fails,
>     nor the change

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three card tests that fail today, and filed two older tests that already pass."],
  "decided": ["The plan only pins red first and the question rule, and changes the card."],
  "open": ["Should the plan only pin what already holds?", "Should the plan check allow a criterion with no test?"]},
 "verdict": "approve",
 "summary": "The plan carries all three asks with sound tests; two questions wait for the owner.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Red first stays: every criterion's test fails on main before work starts.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.1"},
  {"ask": "An ask that can't be checked becomes a question to me", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.2"},
  {"ask": "or shows on the card as not verified.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "670.3"}],
 "behaviors": [
  {"criterion": "670.1", "one_behavior": true, "why": "One rejection: a new test that passes today."},
  {"criterion": "670.2", "one_behavior": true, "why": "One instruction line in the planner's prompt."},
  {"criterion": "670.3", "one_behavior": true, "why": "One card label for a criterion with no test."}],
 "edge_cases": [
  {"criterion": "670.1", "cut": [], "missing": []},
  {"criterion": "670.2", "cut": [], "missing": []},
  {"criterion": "670.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so", "only_its_behavior": true, "why": "Runs the real check; rejects passing and skipped tests, accepts failing ones."},
  {"test": "tests/test_plan_shape.py::test_prompt_teaches_the_terms_voice_and_every_example", "only_its_behavior": true, "why": "Its 670.2 lines check only the question rule, and fail if it is removed."},
  {"test": "tests/test_car
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote three card tests that fail today, and filed two older tests that already pass./It wrote three failing card tests and filed two older passing tests./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 670 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#670](https://github.com/dokima-dev/dokima/issues/670) (card shows criteria with no test as not verified), and the hand-back passes both checks.

**Tests:**
- **Card criterion (670.3):** the three new card tests fail today for the right reason. The card has no "not verified" label yet; nothing crashes.
- **Red first (670.1) and the question rule (670.2):** both already work today. Two older tests already pass and now pin them. One was moved under 670.1 as is. The other got two new lines that would fail if the question rule were removed.

**I raised no blockers.** All three asks match a criterion, each criterion is one behavior, and nothing is missing.

**Two questions from the planner still need you.** I left both unanswered because I couldn't find your words for either:
- **P1:** Red first and the question rule already work. Should the plan just pin them and change the card? The plan assumes yes.
- **P2:** Today the plan check rejects any criterion with no test. The planner's own instructions allow "(manual)" criteria, but none can get past the check. So the new "not verified" label can never show on a real card unless you allow such criteria. The plan assumes you won't. Answering yes would change how the plan check works.

Two caveats:
- I couldn't read [#661](https://github.com/dokima-dev/dokima/issues/661) (splits work into stories) itself. Its comments weren't in my files and I have no GitHub access. I matched your asks against the quotes the plan copied from it.
- The scope lists only the card file. The planner files appear only under criteria 670.1 and 670.2, which need no change, so I didn't block on it.

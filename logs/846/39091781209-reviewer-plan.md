# reviewer (plan) for #846

Run: https://github.com/dokima-dev/dokima/actions/runs/39091781209

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> total 48
> drwxr-xr-x 2 runner runner 4096 Oct 18 02:55 .
> drwxr-xr-x 3 runner runner 4096 Oct 18 02:55 ..
> -rw-r--r-- 1 runner runner 4980 Oct 18 02:55 01-planner.json
> -rw-r--r-- 1 runner runner 5312 Oct 18 02:55 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5116 Oct 18 02:55 03-planner.json
> -rw-r--r-- 1 runner runner 4681 Oct 18 02:55 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4920 Oct 18 02:55 05-planner.json
> # Issue #846: Card and branch updates find checks by shown names
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [820], "blocks": [816], "loop": []} -->
> In an adopter's repo, the card and branch updates must find Dokima's checks by the names GitHub shows there.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/820
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/785
> - https://github.com/dokima-dev/dokima/issues/786
> 
> 
> **User story:** In an adopter's repo, the card shows Dokima's checks passing, and failing pul

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['04-reviewer-plan.json','05-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:3000])
"; cd /home/runner/work/dokima/dokima; cat tests/test_shown_check_names.py
```

> 04-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39089831420",
>  "commit_before": "a5b4b37c8f8254ff3eb7876e45e2150633c76f7e",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 48659,
>   "turns": 8,
>   "cost_usd": 0.4403596,
>   "tokens_in": 343045,
>   "tokens_out": 3534
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/846/39089831420-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39089831420",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner added a criterion: adopter repo, all green and approved, card says ready.",
>     "The planner added its test; all five tests fail today."
>    ],
>    "decided": [
>     "Two related open issues keep only their other asks, as the owner said."
>    ],
>    "open": []
>   },
>   "verdict": "approve",
>   "summary": "The plan now covers every place that reads Dokima's checks, and each test fails today for the right reason.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "the card, which reads the check runs by plain name (e.g. `all tests`), so its Definition of Done never shows them passing",
>     "source": "https://github.com/dokima-dev/dokima/issues/846",
>     "criterion": "846.1"
>    },
>    {
>     "ask": "the card, which reads the check runs by plain name ... so its Definition of Done never shows them passing (Acceptance criteria)",
>     "source": "https://github.com/dokima-dev/dokima/issues/846",
>     "criterio

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "846\.|passed|failed|Error" | head -30; git show --stat c68db07 | head -30; cat dokima/install/dokima.yml; grep -n "full-suite\|acceptance-criteria\|shown\|prefix" dokima/settings.py dokima/install/settings.yaml | head -40
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
>         failed. Proves 846.1."""
>         record_property("proves", "846.1")
>         st, url = done_verdict(draw([check(ALL_TESTS, n=4)]), "Test suite", "846.1")
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> E         At index 0 diff: 'not started' != 'passed'
> E         -     'passed',
> /home/runner/work/dokima/dokima/tests/test_shown_check_names.py:117: AssertionError
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E  .*84[0-9]\.|passed|failed" | head; cat dokima/install/settings.yaml; git show c68db07 -- dokima/manifest.py; grep -n "shown_as\|required_checks" dokima/*.py | head -20
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
>         failed. Proves 846.1."""
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> # This repo's settings, over Dokima's shipped defaults. Name only what differs, and never a secret's value.
> co_author: "{bot}"
> # GitHub names a check after the workflows that call it, so here Dokima's checks show under these names (#820).
> gates:
>   required:
>     - {name: all tests, shown_as: "dokima / full-suite / all tests"}
>     - {name: Acceptance criteria, shown_as: "dokima / acceptance-criteria / Acceptance criteria"}
> commit c68db07f49b74f1109fbcbd2fa85633369cf5092
> Author: dokima-runtime[bot] <33751101

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E +(AssertionError|.*Error)|passed|failed" ; python3 -m pytest -q -x tests 2>&1 | tail -3
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bw6i490az). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** Still checking: the five new tests run, and the full suite is in the background.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 100 python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E +AssertionError|passed|failed"
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
>         failed. Proves 846.1."""
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> E         At index 0 diff: 'not started' != 'passed'
> E         -     'passed',
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Acceptance tests passed when that check passed.
>         an adopter's repo. Passed, the Definition of Done must show Acceptance tests passed and link that check; failed,
>         it must show Acceptance 

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner kept the approved plan unchanged after the blocking issue merged.", "All five tests still fail today because the checks are not found."], "decided": ["Shown names come from the settings file the install now ships."], "open": []},
 "verdict": "approve",
 "summary": "The plan still holds after the blocking issue merged; every test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "the card, which reads the check runs by plain name (e.g. `all tests`), so its Definition of Done never shows them passing", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.1"},
  {"ask": "so its Definition of Done never shows them passing (Acceptance criteria too)", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.2"},
  {"ask": "Fix: both find a check by the name GitHub shows, plain in Dokima's own repo and prefixed in an adopter's", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.3"},
  {"ask": "the branch updates (uptodate), which look for the same plain names before bringing a pull request up to date", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.4"},
  {"ask": "in an adopter repo, all green and code review approved, the card says Ready for approval", "source": "https://github.com/dokima-dev/dokima/issues/846#issuecomment-6244658830", "criterion": "846.5"}
 ],
 "behaviors": [
  {"criterion": "846.1", "one_behavior": true, "why": "One check, one card field."},
  {"criterion": "846.2", "one_behavior": true, "why": "One check, one card field."},
  {"criterion": "846.3", "one_behavior": true, "why": "One criterion check, one bullet."},
  {"criterion": "846.4", "one_behavior": true, "why": "One failed check, one skipped update."},
  {"criterion": "846.5", "one_behavior": true, "why": "All green and approved, one status line."
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#846](https://github.com/dokima-dev/dokima/issues/846) (the card and branch updates find Dokima's checks by the names GitHub shows). The review file passes both hand-back checks.

- **The plan:** the planner made no changes since the last approved round. The blocking work in [#820](https://github.com/dokima-dev/dokima/issues/820) (required checks use the names GitHub shows) has now merged. It made the install's settings file list how each required check is shown in an adopter's repo. That matches the names the tests use.
- **The tests:** all five new tests fail today, each because a check isn't found by its shown name. None fails from a crash or a bad path.
- **Asks:** every ask from the owner, including the later comment asking for "Ready for approval", maps to one criterion.
- **Each criterion:** each is a single behavior and tests both the passing and the failing case.
- **Open items:** none. Nothing is waiting on the owner.

I also started the full test suite in the background, but it ran past my wait time, so I don't have its result. A plan review doesn't need it.

The hand-back is in `/tmp/dokima-out/review.json`.

`8. Bash`
```
tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output
```

> )
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 1299 passed, 1 warning in 705.04s (0:11:45)
> 
> [exited with code 0]

`9. Bash`
```
grep -E "^FAILED|^tests/.*(FAILED|Error)" /tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output | head
```

> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_test_suite_passed_by_its_shown_name - AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name - AssertionError: 846.2: Acceptance criteria passed in an adopter's repo as 'dokima / acceptance-criteria / Acceptance criteria', but the Definition of Done shows Acceptance tests 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/5
> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_a_criterion_passed_by_its_shown_name - AssertionError: 846.3: criterion 40.1's check passed in an adopter's repo as 'dokima / acceptance-criteria / 40.1 · First thing works', but its bullet shows 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/1
> FAILED tests/test_shown_check_names.py::test_adopter_pr_whose_all_tests_failed_is_not_brought_up_to_date - AssertionError: 846.4: #70's all tests failed in an adopter's repo as 'dokima / full-suite / all tests', yet it was brought up to date; updates [(70, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), (80, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')]
> FAILED tests/test_shown_check_names.py::test_adopter_card

`10. Bash`
```
f=/tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output; grep -n "^FAILED\|^___" $f | tail -3
```

> 58:FAILED tests/test_shown_check_names.py::test_adopter_card_shows_a_criterion_passed_by_its_shown_name - AssertionError: 846.3: criterion 40.1's check passed in an adopter's repo as 'dokima / acceptance-criteria / 40.1 · First thing works', but its bullet shows 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/1
> 62:FAILED tests/test_shown_check_names.py::test_adopter_pr_whose_all_tests_failed_is_not_brought_up_to_date - AssertionError: 846.4: #70's all tests failed in an adopter's repo as 'dokima / full-suite / all tests', yet it was brought up to date; updates [(70, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), (80, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')]
> 63:FAILED tests/test_shown_check_names.py::test_adopter_card_says_ready_for_approval_by_shown_names - AssertionError: 846.5: code review approved and 'dokima / acceptance-criteria / 40.1 · First thing works' and 'dokima / full-suite / all tests' passed in an adopter's repo, but the card does not say Ready for approval:

`11. Bash`
```
f=/tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output; wc -l $f; sed -n 64,200p $f | grep -v "^ " | head -40
```

> 71 /tmp/claude-1001/-home-runner-work-dokima-dokima/55edc93b-0c34-418b-b7d0-33a49742caa5/tasks/bw6i490az.output
> 5 failed in 0.08s
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 1299 passed, 1 warning in 705.04s (0:11:45)
> 
> [exited with code 0]

`12. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 110 python3 -m pytest -q --collect-only tests 2>/dev/null | grep -n "test_shown_check_names" | head -2
```

> 1300:tests/test_shown_check_names.py::test_adopter_card_shows_test_suite_passed_by_its_shown_name
> 1301:tests/test_shown_check_names.py::test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name

**Agent:** Checking the tests that run after the new file, since the full run stopped at its first test.

`13. Bash`
```
cd /home/runner/work/dokima/dokima; ls tests/*.py | awk '$0 > "tests/test_shown_check_names.py"' | xargs timeout 500 python3 -m pytest -q 2>&1 | tail -2
```

> -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
> 167 passed, 1 warning in 157.79s (0:02:37)

**Agent:** The full suite came back clean apart from the five new tests, which are expected to fail before the work is built. My approval of the plan stands.

- The first run stopped at its first failure. That was the first new test, 846.1, after 1,299 tests passed.
- I then ran the 167 tests from the files that come after the new one, and all passed.

So every existing test passes on this branch, and the five new tests are the only failures.

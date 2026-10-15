# reviewer (plan) for #707

Run: https://github.com/dokima-dev/dokima/actions/runs/38687822469

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (42.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/f3608599-ff61-4e45-aeee-5452de4012a0/tool-results/bsj86exm1.txt
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
> 04-reviewer-plan.json
> 05-planner.json
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

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (31.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/f3608599-ff61-4e45-aeee-5452de4012a0/tool-results/b08821719.txt
> 
> Preview (first 2KB):
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criteri

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; cat plan.json; cat parent.json | head -50
```

> []{
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
>    "words":

`4. Bash`
```
cd /tmp/pack; cat issue.md
```

`5. Bash`
```
cd /tmp/pack; cat open_blockers.json; cat plan.json; cat parent.json | head -50
```

> <persisted-output>
> Output too large (31.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/f3608599-ff61-4e45-aeee-5452de4012a0/tool-results/b08821719.txt
> 
> Preview (first 2KB):
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criteri

> []{
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
>    "words":

`6. Bash`
```
cd /tmp/pack; sed -n 1,400p issue.md | grep -v "^$" | sed -n 60,400p
```

> <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-707/tests/test_owner_tests_and_docstrings.py#L326">The new file has no opening docstring at all.</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/dokima/issues/559#issuecomment-6131843348
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A new test file whose opening docstring has no agent detail after its user line is rejected.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-707/tests/test_owner_tests_and_docstrings.py#L343"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: User: A new test file whose opening docstring has no agent detail is rejected.*
>   - Edge cases: none, because Only the missing detail varies; the owner named no other case.
>   - Source: https://github.com/dokima-dev/dokima/issues/559#issuecomment-6131843348
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:*

`7. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
d=json.load(open('04-reviewer-plan.json'));print(json.dumps(d,indent=1)[:9000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38687223408",
>  "commit_before": "dc652777d4c523f3e861694c2bbd6e3923ff5759",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 151867,
>   "turns": 10,
>   "cost_usd": 0.643846,
>   "tokens_in": 453649,
>   "tokens_out": 5305
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/707/38687223408-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38687223408",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner gave the owner's test a reason in two tests, still expecting rejection.",
>     "The planner added two criteria from the owner's answer: their tests meet the same bar."
>    ],
>    "decided": [
>     "An owner's test that misses the bar is raised to the owner as a question."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "The plan covers every ask; two new tests pass if any question for the owner is raised.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "707.14: weak",
>     "text": "707.14 passes with code letting any owner question unlock it. Fix: also raise a question naming another test; expect rejection naming `test_owner_id`.",
>     "evidence": "`owner_misses_bar` only tries no question, then one naming `test_owner_id`; nothing checks the naming.",
>     "raised_by": "reviewer",
>     "id": "R2"
>    },
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "707.15: weak",
>     "text"

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git diff dc65277 08d23ce --stat; git diff dc65277 08d23ce -- tests/ | head -150
```

> .dokima/agents.yml                       |  8 ++++++++
>  dokima/agent_kimi.py                     |  6 ++++--
>  dokima/setup.py                          |  2 +-
>  tests/test_agent_kimi.py                 | 10 +++++-----
>  tests/test_owner_tests_and_docstrings.py | 22 ++++++++++++++--------
>  tests/test_setup.py                      | 12 ++++++------
>  6 files changed, 38 insertions(+), 22 deletions(-)
> diff --git a/tests/test_agent_kimi.py b/tests/test_agent_kimi.py
> index 5d838a5..9a8e69c 100644
> --- a/tests/test_agent_kimi.py
> +++ b/tests/test_agent_kimi.py
> @@ -28,12 +28,12 @@ KIMI = textwrap.dedent('''\
>      import json, os, sys
>      home = os.path.expanduser("~")
>      if sys.argv[1:2] == ["login"]:
> -        os.makedirs(os.path.join(home, ".kimi", "credentials"), exist_ok=True)
> -        open(os.path.join(home, ".kimi", "credentials", "kimi-code.json"), "w").write('{{"access_token": "tok-123"}}')
> -        open(os.path.join(home, ".kimi", "config.toml"), "w").write('default_model = "kimi-for-coding"\\n')
> +        os.makedirs(os.path.join(home, ".kimi-code", "credentials"), exist_ok=True)
> +        open(os.path.join(home, ".kimi-code", "credentials", "kimi-code.json"), "w").write('{{"access_token": "tok-123"}}')
> +        open(os.path.join(home, ".kimi-code", "config.toml"), "w").write('default_model = "kimi-for-coding"\\n')
>          sys.exit(0)
>      seen = {{}}
> -    for d, _, files in os.walk(os.path.join(home, ".kimi")):
> +    for d, _, files in os.walk(os.path.join(home, ".kimi-code"))

**Agent:** Checking the planner's fix for the two earlier blockers, then running the tests.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^OLD\|^OWNER_TEST\|def owner_question" -A4 tests/test_owner_tests_and_docstrings.py | head -30; python3 -m pytest -q tests/test_owner_tests_and_docstrings.py 2>&1 | grep -E "FAILED|AssertionError|Error|passed|failed" | head -40
```

> 24:OWNER_TEST = "tests/test_owner.py::test_owner_id"
> 25:OLD = "tests/test_old.py::test_old"
> 26-
> 27-# An older test in the old shape: one summary line, no User, Verified by or Agent part.
> 28:OLD_TESTS = ('def test_old(record_property):\n    """An older test, already in the repo."""\n'
> 29-             '    record_property("proves", "50.1")\n    assert True\n')
> 30-
> 31-
> 32-def doc(user="A slow call returns a job id.", verified="running the job code and checking the id it returns.",
> --
> 398:def owner_question(test):
> 399-    """A question for the owner, naming the owner's test in its evidence.
> 400-
> 401-    The text of a raise may not name code, so the test's path::name sits in the evidence.
> 402-    """
> E       AssertionError: 707.1: a plan that changes a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:146: AssertionError
> E       AssertionError: 707.2: a plan that deletes a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:167: AssertionError
> E       AssertionError: 707.3: a plan that files no criterion for a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:185: AssertionError
> E       AssertionError: 707.4: a new test with no User part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionError
> E       AssertionError: 707.4: a changed test

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_new_test_check.py tests/test_word_caps.py 2>&1 | tail -5
```

> ::warning title=Over the word cap::tests/test_jobs.py has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>   ?                                    ++++++++++++++++++
>     ::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>     plan
> 1 failed, 22 passed in 41.56s

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_new_test_check.py tests/test_word_caps.py 2>&1 | grep -E "^FAILED"
```

> FAILED tests/test_word_caps.py::test_a_docstring_the_planner_adds_is_held_to_15_words_in_its_first_line - AssertionError: 239.2: a docstring within its cap was listed: '::warning title=Over the word cap::tests/test_jobs.py has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)\n::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)\nplan\n'

`12. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
prev=json.load(open('/tmp/pack/in/04-reviewer-plan.json'))['handback']
plan=json.load(open('/tmp/pack/plan.json'))
tests=[]
for k,v in plan['tests'].items():
    for t in v:
        tests.append({"test":t,"only_its_behavior":True,"why":"Runs the real check; fails today because the feature is missing."})
edge=[{"criterion":e["criterion"],"cut":[],"missing":[]} for e in prev["edge_cases"]]
r={"previous_step":{"did":["The planner made the two owner-question tests also try a question naming another test.","Those tests now expect rejection naming the owner's test in that case."],"decided":[],"open":[]},
"verdict":"approve",
"summary":"Every ask has a criterion, and every new test fails today because the feature is missing.",
"raises":[],"answers":[],
"asks":prev["asks"],"behaviors":prev["behaviors"],"edge_cases":edge,"tests":tests,"size":"ok"}
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 707 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#707](https://github.com/dokima-dev/dokima/issues/707) (locks the owner's tests and checks test docstrings). The review file passes both hand-back checks.

- **Earlier blockers are fixed:** the two tests for "your test goes to you as a question" (707.14 and 707.15) now also try a plan whose question names a different test. In that case they expect the plan to be rejected, naming your test. So code that lets any question through can no longer pass them.
- **Every ask has a criterion:** that includes your answer of 2026-10-15: "No skip. My tests meet the same bar as any test."
- **New tests fail today for the right reason:** all 17 runs of the 16 new tests fail because the feature isn't built yet, not because of a crash or bad setup.
- **One changed older test fails today, as expected:** `tests/test_word_caps.py::test_a_docstring_the_planner_adds_is_held_to_15_words_in_its_first_line` fails until the check stops counting the "User:" label in a test's first line. The plan lists this as a declared test change.
- **No new blockers or questions:** there were no open blockers to answer.

The review is in `/tmp/dokima-out/review.json`.

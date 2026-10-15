# reviewer (plan) for #707

Run: https://github.com/dokima-dev/dokima/actions/runs/38693154267

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (45.7KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/976ef268-4a88-447b-aad7-5068fc1a29e9/tool-results/bgb9tji54.txt
> 
> Preview (first 2KB):
> .:
> total 136
> drwxr-xr-x  3 runner runner  4096 Oct 15 06:34 .
> drwxrwxrwt 18 root   root    4096 Oct 15 06:34 ..
> drwxr-xr-x  2 runner runner  4096 Oct 15 06:34 in
> -rw-r--r--  1 runner runner 35304 Oct 15 06:34 issue.md
> -rw-r--r--  1 runner runner     2 Oct 15 06:34 open_blockers.json
> -rw-r--r--  1 runner runner 58198 Oct 15 06:34 open_issues.json
> -rw-r--r--  1 runner runner  4732 Oct 15 06:34 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 15 06:34 parent.json
> -rw-r--r--  1 runner runner 10446 Oct 15 06:34 plan.json
> 
> in:
> total 92
> drwxr-xr-x 2 runner runner  4096 Oct 15 06:34 .
> drwxr-xr-x 3 runner runner  4096 Oct 15 06:34 ..
> -rw-r--r-- 1 runner runner 10260 Oct 15 06:34 01-planner.json
> -rw-r--r-- 1 runner runner 10615 Oct 15 06:34 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 11500 Oct 15 06:34 03-planner.json
> -rw-r--r-- 1 runner runner 12017 Oct 15 06:34 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 11706 Oct 15 06:34 05-planner.json
> -rw-r--r-- 1 runner runner 10952 Oct 15 06:34 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 11346 Oct 15 06:34 07-planner.json
> # Issue #707: Plan check locks owner tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 708 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 7

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (34.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/976ef268-4a88-447b-aad7-5068fc1a29e9/tool-results/b3fil4a3r.txt
> 
> Preview (first 2KB):
> # Issue #707: Plan check locks owner tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 708 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
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
> **User story:** Tests the owner commits stay exactly as written, and every new test explains

`3. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/976ef268-4a88-447b-aad7-5068fc1a29e9/tool-results/b3fil4a3r.txt
```

> 1	# Issue #707: Plan check locks owner tests and checks test docstrings
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 708 -->
> 5	<!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> 6	The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 7	
> 8	**Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/710
> 13	- https://github.com/dokima-dev/dokima/issues/712
> 14	- https://github.com/dokima-dev/dokima/issues/713
> 15	- https://github.com/dokima-dev/dokima/issues/714
> 16	
> 17	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 18	
> 19	- https://github.com/dokima-dev/dokima/issues/546
> 20	- https://github.com/dokima-dev/dokima/issues/559
> 21	- https://github.com/dokima-dev/dokima/issues/708
> 22	
> 23	
> 24	**User story:** Tests the owner commits stay exactly as written, and every new test explains itself in one shape.
> 25	
> 26	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height=

`4. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat owner_words.json parent.json open_blockers.json; ls in; python3 -c "
import json
for f in ['in/06-reviewer-plan.json','in/07-planner.json']:
    d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"
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

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json
a=json.load(open('in/05-planner.json'))['handback'];b=json.load(open('in/07-planner.json'))['handback'];c=json.load(open('plan.json'))
print(a==b, b==c)
for k in set(a)|set(b):
  if a.get(k)!=b.get(k): print('diff',k)
"; cd /home/runner/work/dokima/dokima; git log --oneline -8 --stat | head -60; git diff 08d23ce HEAD --stat
```

> False True
> diff answers
> 5a23e58 Merge remote-tracking branch 'origin/main' into try/issue-707
> e006997 Every role reads the parent's ask and the owner's words (#731)
>  dokima/agent_roles.py            |  34 +++++-
>  dokima/planner.py                |  11 +-
>  tests/test_agent.py              |  13 ++-
>  tests/test_story_reads_parent.py | 232 +++++++++++++++++++++++++++++++++++++++
>  4 files changed, 278 insertions(+), 12 deletions(-)
> 8f1f717 A role can run on Codex CLI (#728)
>  dokima/agent_codex.py     |  81 +++++++++++++++++++++++++++
>  tests/test_agent_codex.py | 138 ++++++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 219 insertions(+)
> 08d23ce planner for #707 (run 38687520887)
>  tests/test_owner_tests_and_docstrings.py | 22 ++++++++++++++--------
>  1 file changed, 14 insertions(+), 8 deletions(-)
> f6bd771 Merge remote-tracking branch 'origin/main' into try/issue-707
> dc65277 planner for #707 (run 38685237520)
>  tests/test_owner_tests_and_docstrings.py | 93 ++++++++++++++++++++++++++++----
>  1 file changed, 82 insertions(+), 11 deletions(-)
> 23b3df2 Manual fix: fix/kimi-code-cli (#729)
>  .dokima/agents.yml       |  8 ++++++++
>  dokima/agent_kimi.py     |  6 ++++--
>  dokima/setup.py          |  2 +-
>  tests/test_agent_kimi.py | 10 +++++-----
>  tests/test_setup.py      | 12 ++++++------
>  5 files changed, 24 insertions(+), 14 deletions(-)
> 959fc23 Merge remote-tracking branch 'origin/main' into try/issue-707
>  dokima/agent_codex.py            |  81 ++++++++++++++
>  dokima/agent_roles.p

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_owner_tests_and_docstrings.py 2>&1 | grep -E "^(FAILED|ERROR|PASSED)|passed|failed|Error" | head -40; python3 -m pytest -q "tests/test_new_test_check.py" tests/test_word_caps.py 2>&1 | tail -8
```

> E       AssertionError: 707.1: a plan that changes a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:146: AssertionError
> E       AssertionError: 707.2: a plan that deletes a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:167: AssertionError
> E       AssertionError: 707.3: a plan that files no criterion for a test the owner committed was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:185: AssertionError
> E       AssertionError: 707.4: a new test with no User part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionError
> E       AssertionError: 707.4: a changed test with no User part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionError
> E       AssertionError: 707.5: a new test with no Verified by part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionError
> E       AssertionError: 707.5: a changed test with no Verified by part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionError
> E       AssertionError: 707.6: a new test with no Agent part in its docstring was accepted
> /home/runner/work/dokima/dokima/tests/test_owner_tests_and_docstrings.py:208: AssertionE

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json
d=json.load(open('/tmp/pack/in/06-reviewer-plan.json'))['handback']
print(json.dumps({k:d[k] for k in ['edge_cases','tests','size']},indent=0))
"; timeout 900 python3 -m pytest -q -x -p no:cacheprovider --deselect tests/test_owner_tests_and_docstrings.py 2>&1 | tail -5
```

> {
> "edge_cases": [
> {
> "criterion": "707.1",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.2",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.3",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.4",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.5",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.6",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.7",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.8",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.9",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.10",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.11",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.12",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.13",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.14",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.15",
> "cut": [],
> "missing": []
> },
> {
> "criterion": "707.16",
> "cut": [],
> "missing": []
> }
> ],
> "tests": [
> {
> "test": "tests/test_owner_tests_and_docstrings.py::test_a_plan_that_changes_the_owners_test_is_rejected_naming_it",
> "only_its_behavior": true,
> "why": "Runs the real check; fails today because the feature is missing."
> },
> {
> "test": "tests/test_owner_tests_and_docstrings.py::test_a_plan_that_deletes_the_owners_test_is_rejected_naming_it",
> "only_its_behavior": true,
> "why": "Runs the real check; fails today because the feature is missing."
> },
> {
> "test": "tests/test_owner_tests_and_docstrings.py::test_a_plan_that_files_no_criterion_for_the_owners_test_is_rejected_naming_it",
> "only_its_behavior": true,
> "why": "Runs the real chec

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1200 python3 -m pytest -q -p no:cacheprovider -n auto 2>/dev/null | tail -3 || true; timeout 1500 python3 -m pytest -q -p no:cacheprovider 2>&1 | grep -E "^FAILED|passed|failed" | grep -v test_owner_tests_and_docstrings | tail -20
```

> Command did not complete within its 600s timeout and was moved to the background (ID: bhsly8y36). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/976ef268-4a88-447b-aad7-5068fc1a29e9/tasks/bhsly8y36.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 120 python3 -m pytest -q -x -p no:cacheprovider --deselect tests/test_owner_tests_and_docstrings.py 2>&1 | grep -E "^(FAILED|_____)" | head
```

> ____________ test_settings_come_from_one_file_in_the_dokima_folder _____________
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''

`10. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
p=json.load(open('plan.json'))
prev=json.load(open('in/06-reviewer-plan.json'))['handback']
ids=[f"707.{i}" for i in range(1,17)]
beh=[{"criterion":c,"one_behavior":True,"why":"One case, one result."} for c in ids]
r={"previous_step":{"did":["The planner re-planned after the blocking issue merged, with the same criteria and tests."],
 "decided":[],"open":[]},
 "verdict":"approve",
 "summary":"The plan is unchanged since its approval, and every new test still fails because the feature is missing.",
 "raises":[],"answers":[],
 "asks":prev["asks"],"behaviors":beh,"edge_cases":prev["edge_cases"],"tests":prev["tests"],"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 707 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** The review file passes its check. I'm waiting on the full test run to confirm nothing else on the branch broke.

`11. Bash`
```
sleep 1; tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/976ef268-4a88-447b-aad7-5068fc1a29e9/tasks/bhsly8y36.output
```

> ::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>     plan
> 30 failed, 1247 passed, 4 warnings in 244.34s (0:04:04)

`12. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 500 python3 -m pytest -q -p no:cacheprovider -n auto 2>&1 | grep -E "^FAILED" | grep -v test_owner_tests_and_docstrings | cut -c1-200
```

> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5
> FAILED tests/test_agents.py::test_each_role_has_its_own_subscription_and_model - AssertionError: 698.3: the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent - AssertionError: 698.4: Claude Code got model 'claude-opus-5-5', not the role's claude-unreleased-9-9
> FAILED tests/test_agents.py::test_a_role_the_file_leaves_out_starts_claude_code_as_today - AssertionError: 698.7: the worker the file names should run on claude-haiku-5-5: exit 0; stdout: 'kimi-code/k
> FAILED tests/test_agents.py::test_a_role_missing_its_model_stops_and_names_the_role - AssertionError: 698.8: a planner with no model line did not stop with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_an_unknown_agent_stops_before_any_agent - AssertionError: 698.10: an unknown agent did not stop the planner with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_a_runs_record_reads_its_agent_through_the_interface - AssertionError: 698.15: the record names models ['claude-opus-5-5'], not zeta's zeta-1
> FAILED tests/test_agents.py::test_moving_a_role_takes_one_edit_of_its_own_lines - AssertionError: 698.20: the worker should start on FIRST_KEY: exit 0; stdout

`13. Bash`
```
env | grep -iE "dokima|model" | cut -c1-80; cd /home/runner/work/dokima/dokima; git stash list | head -1; env -u DOKIMA_MODEL timeout 120 python3 -m pytest -q -p no:cacheprovider tests/test_agents.py 2>&1 | tail -1
```

> GITHUB_WORKSPACE=/home/runner/work/dokima/dokima
> LOG_URL=https://github.com/dokima-dev/dokima/blob/logs/logs/707/38693154267-revi
> GITHUB_TRIGGERING_ACTOR=dokima-runtime[bot]
> PWD=/home/runner/work/dokima/dokima
> GITHUB_WORKFLOW_REF=dokima-dev/dokima/.github/workflows/agent.yml@refs/heads/mai
> DOKIMA_SETTINGS=/tmp/runtime/.dokima/agents.yml
> MODEL=claude-opus-5-5
> GITHUB_ACTOR=dokima-runtime[bot]
> GITHUB_REPOSITORY=dokima-dev/dokima
> RUNNER_WORKSPACE=/home/runner/work/dokima
> GITHUB_REPOSITORY_OWNER=dokima-dev
> OUT=/tmp/dokima-out
> 9 failed, 16 passed in 37.84s

`14. Bash`
```
cd /home/runner/work/dokima/dokima; env -u DOKIMA_SETTINGS -u MODEL timeout 120 python3 -m pytest -q -p no:cacheprovider tests/test_agents.py 2>&1 | tail -1
```

> 25 passed in 11.13s

**Agent:** I approved the plan for [#707](https://github.com/dokima-dev/dokima/issues/707) (owner tests stay locked, new tests follow one docstring shape). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **The plan is unchanged.** You asked for a re-plan after the work it waited on merged, and the planner returned the same plan that was approved last round. The criteria, tests and the three changes to older tests all match. The planner also raised no new questions.
- **The new tests fail for the right reason.** Each of the 16 new tests fails because the feature doesn't exist yet. None fails from a crash or a bad setup. Your ask to raise your own tests to you as a question, never edited, is still covered by criteria 707.14 and 707.15.
- **The one changed older test fails as expected.** It's the word-cap test in `tests/test_word_caps.py`, and it needs the new docstring shape.
- **Nothing on the branch broke.** In the full test run the only other failures were nine tests in `tests/test_agents.py`. They come from model settings in this run's machine, not from the code: with those settings removed, all 25 pass.

Every ask maps to a criterion, I found no blockers, and there were no open items from earlier rounds to answer.

**Agent:** That notice is for the background full test run, which has now finished. I'd already read its results before approving, so the review stands. The plan for [#707](https://github.com/dokima-dev/dokima/issues/707) (owner tests stay locked, new tests follow one docstring shape) is approved, and `review.json` passes its checks.

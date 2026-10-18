# reviewer (plan) for #857

Run: https://github.com/dokima-dev/dokima/actions/runs/39105179783

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #857: Pull requests with no plan pass unless Dokima opened them
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> People and Dependabot can merge without a Dokima plan; Dokima's own pull requests still need one.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/865 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/865/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/744
> 
> 
> **User story:** People and Dependabot merge pull requests without a Dokima plan, while Dokima's own stay held to theirs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a person opens a pull request with no approved plan, the Acceptance criteria check passes.
>   *<a href="https://github.com/dokima-dev/dokima/blob/9833b6454271a4f0f3e3190bdb99c03e6e83d69d/tests/test_unplanned_prs.py#L82"><img 

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json,sys
for f in ['04-reviewer-plan.json','06-reviewer-pr.json','07-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:4000]); print('----')
"
```

> 04-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39104134707",
>  "commit_before": "0ac83904b54c6081d3e5d03f9e559df3ddb99e50",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 33052,
>   "turns": 5,
>   "cost_usd": 0.202618,
>   "tokens_in": 181818,
>   "tokens_out": 1549
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/857/39104134707-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39104134707",
>  "handback": {
>   "asks": [
>    {
>     "ask": "When a person opens a pull request with no approved plan, the Acceptance criteria check passes.",
>     "source": "https://github.com/dokima-dev/dokima/issues/857",
>     "criterion": "857.1"
>    },
>    {
>     "ask": "When Dependabot opens a pull request with no approved plan, the Acceptance criteria check passes.",
>     "source": "https://github.com/dokima-dev/dokima/issues/857",
>     "criterion": "857.2"
>    },
>    {
>     "ask": "When Dokima opens an issue's pull request with no approved plan, the Acceptance criteria check still fails.",
>     "source": "https://github.com/dokima-dev/dokima/issues/857",
>     "criterion": "857.3"
>    },
>    {
>     "ask": "When the unplanned pull requests setting is not allow, a person's unplanned pull request fails the check.",
>     "source": "https://github.com/dokima-dev/dokima/issues/857",
>     "criterion": "857.4"
>    },
>    {
>     "ask": "Add merge.unplanned_prs to dokima/defaults.yaml with allow as the defa

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main --stat; cat tests/test_unplanned_prs.py; timeout 600 python -m pytest -q -x -p no:cacheprovider 2>&1 | tail -30
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bbhrrel3w). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`4. Bash`
```
cd /home/runner/work/dokima/dokima; head -c 20000 /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output
```

> .github/workflows/acceptance-criteria.yml |   1 +
>  dokima/checks.py                          |  16 +++-
>  dokima/defaults.yaml                      |   2 +
>  tests/test_manual_fix_check.py            |  10 +--
>  tests/test_test_settings.py               |  13 +--
>  tests/test_unplanned_prs.py               | 143 ++++++++++++++++++++++++++++++
>  6 files changed, 173 insertions(+), 12 deletions(-)
> """Pull requests with no approved plan pass unless Dokima opened them (#857, from #744).
> 
> The required Acceptance criteria check used to fail every pull request without an approved Dokima plan, so a person's
> or Dependabot's pull request could never merge. The `merge.unplanned_prs` setting, `allow` by default, lets them
> through; only Dokima's own pull requests are held to the plan, and any other value keeps today's failing check.
> 
> Each test runs the real command the Acceptance criteria workflow runs, `python3 -m dokima.checks matrix`, from a temp
> git repo (with or without its own settings file) and GitHub faked by a stub `gh`: the pull request changes
> `app/main.py`, so the text-only shortcut never applies, and issue #77, when named, has no plan. It then runs that
> workflow's own "Run this criterion's tests" step for every row it got, with a passing fake `pytest` on PATH, and its
> "gate" step. The check passes only when every step does. Nothing here touches the network.
> """
> import json
> import os
> import subprocess
> import sys
> 
> from test_test_settings import make_repo
> from test_text_only import R

`5. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt 0ac8390 && cd /tmp/wt && git diff --stat main 0ac8390 && timeout 300 python -m pytest -q -p no:cacheprovider tests/test_unplanned_prs.py tests/test_manual_fix_check.py tests/test_test_settings.py 2>&1 | grep -E "FAILED|passed|failed|857" | head -30
```

> tests/test_manual_fix_check.py |  10 +--
>  tests/test_test_settings.py    |  13 ++--
>  tests/test_unplanned_prs.py    | 143 +++++++++++++++++++++++++++++++++++++++++
>  3 files changed, 156 insertions(+), 10 deletions(-)
>         Proves 857.1. In a repo with no settings file, so the default holds, a person opens a code change with no linked
>         record_property("proves", "857.1")
>         passed, rows, out = acceptance_check(tmp_path / "a", PERSON, "octocat/fix-typo")
> >       assert passed and not no_plan_named(rows), \
>             f"857.1: a person's pull request with no linked issue still fails the Acceptance criteria check: {rows}\n{out}"
> E       AssertionError: 857.1: a person's pull request with no linked issue still fails the Acceptance criteria check: [{'id': 'none', 'name': 'No approved plan found: no issue linked', 'tests': ''}]
>         Proves 857.2. In a repo with no settings file, Dependabot opens a dependency bump from its own branch with no
>         record_property("proves", "857.2")
>         passed, rows, out = acceptance_check(tmp_path, DEPENDABOT, "dependabot/pip/pyyaml-6.0.2")
> >       assert passed and not no_plan_named(rows), \
>             f"857.2: Dependabot's pull request with no plan still fails the Acceptance criteria check: {rows}\n{out}"
> E       AssertionError: 857.2: Dependabot's pull request with no plan still fails the Acceptance criteria check: [{'id': 'none', 'name': 'No approved plan found: no issue linked', 'tests': ''}]
>         Proves 857.3. In a re

**Agent:** Checking the plan's tests: all four new tests fail on main for the right reason. Now waiting on the full suite on the branch.

`6. Bash`
```
cd /tmp/wt && timeout 300 python -m pytest -q -p no:cacheprovider tests/test_unplanned_prs.py tests/test_manual_fix_check.py tests/test_test_settings.py 2>&1 | tail -8; cd /home/runner/work/dokima/dokima; git diff main -- tests/test_manual_fix_check.py tests/test_test_settings.py
```

> row none exit 1
>   ::error title=none has no test::No test verifies this criterion yet.
>   
>   gate exit 1
>   
> assert False
> 4 failed, 15 passed in 9.97s
> diff --git a/tests/test_manual_fix_check.py b/tests/test_manual_fix_check.py
> index bc9b846..5a224c4 100644
> --- a/tests/test_manual_fix_check.py
> +++ b/tests/test_manual_fix_check.py
> @@ -132,16 +132,16 @@ def test_a_manual_fix_check_fails_when_a_test_fails(record_property, tmp_path):
>  
>  
>  def test_only_dokimas_app_gets_the_manual_fix_check(record_property, tmp_path):
> -    """A pull request with no issue, opened by anyone else, still fails.
> +    """A pull request with no issue, opened by anyone else, gets no manual fix check.
>  
> -    Proves 643.3. Runs the matrix command for the same code change twice: opened by a person, it must get only the failing
> -    no-plan check; opened by Dokima's app, it must get the manual fix check instead. Since 2026-10-17 every manual fix
> +    Proves 643.3. Runs the matrix command for the same code change twice: opened by a person, it must not get the manual
> +    fix check (since #857 it may pass as an unplanned pull request); opened by Dokima's app, it must get the manual fix check instead. Since 2026-10-17 every manual fix
>      names the issue it fixes (owner, #830), so one by Dokima's app from its fix branch naming an issue still gets the
>      manual fix check; a planned build from try/issue-N with no approved plan still fails (830.7)."""
>      record_property("proves", "643.3")
>      rows, output = run

`7. Bash`
```
sleep 100; tail -30 /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output | cut -c1-300
```

> <tool_use_error>Blocked: sleep 100 followed by: tail -30 /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output cut -c1-300. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`8. Bash`
```
tail -30 /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output | cut -c1-300
```

> #77's pull request from try/issue-77, and #77 has no approved plan: the check must fail with one row saying no
>     approved plan was found for issue #77. A person's same pull request must pass, so the failure is Dokima's alone.
>     """
>     record_property("proves", "857.3")
>     passed, rows, out = acceptance_check(tmp_path / "a", DOKIMA, "try/issue-77", body="Closes #77")
>     assert not passed, f"857.3: Dokima's own pull request with no approved plan passed the check: {rows}\n{out}"
>     assert [r["name"] for r in rows or []] == ["No approved plan found for issue #77"], \
>         f"857.3: Dokima's own unplanned pull request did not fail saying no approved plan was found: {rows}\n{out}"
>     passed, rows, out = acceptance_check(tmp_path / "b", PERSON, "try/issue-77", body="Closes #77")
>     assert passed, f"857.3: a person's same pull request failed too, so the check fails everyone: {rows}\n{out}"
> 
> 
> def test_a_setting_other_than_allow_fails_a_persons_unplanned_pull_request(record_property, tmp_path):
>     """When the unplanned pull requests setting is not allow, a person's unplanned pull request fails.
> 
>     Proves 857.4. In a repo whose settings say `merge.unplanned_prs: block`, a person's code change with no linked
>     issue must fail the check with "No approved plan found: no issue linked", and one saying "Closes #77" must fail
>     with "No approved plan found for issue #77". The same change in a repo whose settings say `allow` must pass.
>     """
>     record_property("proves", "8

`9. Bash`
```
F=/tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/bbhrrel3w.output; until grep -qE "[0-9]+ (passed|failed)" $F; do sleep 5; done; tail -15 $F | cut -c1-300
```

> Command did not complete within its 600s timeout and was moved to the background (ID: b58z1kf2i). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/019eadab-609d-4559-ae7e-da585d20a522/tasks/b58z1kf2i.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.

`10. Bash`
```
pkill -f "until grep" ; cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; mkdir -p /tmp/dokima-out; python3 - <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/857"
asks=[
 ("When a person opens a pull request with no approved plan, the Acceptance criteria check passes.","857.1"),
 ("When Dependabot opens a pull request with no approved plan, the Acceptance criteria check passes.","857.2"),
 ("When Dokima opens an issue's pull request with no approved plan, the Acceptance criteria check still fails.","857.3"),
 ("When the unplanned pull requests setting is not allow, a person's unplanned pull request fails the check.","857.4"),
 ("Add merge.unplanned_prs to dokima/defaults.yaml with allow as the default","857.1"),
 ("any other value (for example block) keeps today's failing check","857.4"),
]
T="tests/test_unplanned_prs.py::"
r={
 "previous_step":{"did":["The planner answered the worker's question about pull requests with no named author."],
   "decided":["A pull request with no named author still fails with no plan.","The criteria, tests and older test changes stay as before."],
   "open":[]},
 "verdict":"approve",
 "summary":"The plan is unchanged and still proven; all four new tests fail today for the right reason.",
 "raises":[],"answers":[],
 "asks":[{"ask":a,"source":I,"criterion":c} for a,c in asks],
 "behaviors":[
  {"criterion":"857.1","one_behavior":True,"why":"One author, one result: the check passes."},
  {"criterion":"857.2","one_behavior":True,"why":"One author, one result: the check passes."},
  {"criterion":"857.3","one_behavior":True,"why":"Dokima's unplanned pull request fails; one result."},
  {"criterion":"857.4","one_behavior":True,"why":"A non-allow setting makes a person's pull request fail."}],
 "edge_cases":[{"criterion":c,"cut":[],"missing":[]} for c in ["857.1","857.2","857.3","857.4"]],
 "tests":[
  {"test":T+"test_a_persons_pull_request_with_no_plan_passes","only_its_behavior":True,"why":"Runs the 
```

> Exit code 144

`11. Bash`
```
ls /tmp/dokima-out/ /tmp/wt 2>&1 | head
```

> /tmp/dokima-out/:
> claude.json
> 
> /tmp/wt:
> AGENTS.md
> CHANGELOG.md
> CLAUDE.md
> LICENSE
> README.md
> docs

**Agent:** The tests check out, so I'm writing the approval and running the hand-back check.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; python3 - <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/857"
asks=[
 ("When a person opens a pull request with no approved plan, the Acceptance criteria check passes.","857.1"),
 ("When Dependabot opens a pull request with no approved plan, the Acceptance criteria check passes.","857.2"),
 ("When Dokima opens an issue's pull request with no approved plan, the Acceptance criteria check still fails.","857.3"),
 ("When the unplanned pull requests setting is not allow, a person's unplanned pull request fails the check.","857.4"),
 ("Add merge.unplanned_prs to dokima/defaults.yaml with allow as the default","857.1"),
 ("any other value (for example block) keeps today's failing check","857.4"),
]
T="tests/test_unplanned_prs.py::"
r={
 "previous_step":{"did":["The planner answered the worker's question about pull requests with no named author."],
   "decided":["A pull request with no named author still fails with no plan.","The criteria, tests and older test changes stay as before."],
   "open":[]},
 "verdict":"approve",
 "summary":"The plan is unchanged and still proven; all four new tests fail today for the right reason.",
 "raises":[],"answers":[],
 "asks":[{"ask":a,"source":I,"criterion":c} for a,c in asks],
 "behaviors":[
  {"criterion":"857.1","one_behavior":True,"why":"One author, one result: the check passes."},
  {"criterion":"857.2","one_behavior":True,"why":"One author, one result: the check passes."},
  {"criterion":"857.3","one_behavior":True,"why":"Dokima's unplanned pull request fails; one result."},
  {"criterion":"857.4","one_behavior":True,"why":"A non-allow setting makes a person's pull request fail."}],
 "edge_cases":[{"criterion":c,"cut":[],"missing":[]} for c in ["857.1","857.2","857.3","857.4"]],
 "tests":[
  {"test":T+"test_a_persons_pull_request_with_no_plan_passes","only_its_behavior":True,"why":"Runs the real check steps; fails on main on the no-plan row
```

> exit 0

**Agent:** I approved the plan for [#857](https://github.com/dokima-dev/dokima/issues/857) (pull requests with no plan pass unless Dokima opened them). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **What changed:** nothing in the plan. The planner only answered the worker's question: a pull request that names no author still fails without a plan. That fits the owner's ask, which frees only people and Dependabot.
- **New tests:** all four fail on the planner's commit (before any code), each for the right reason. Each one still shows the "no approved plan" failure, and the third and fourth fail on their "a person passes" step.
- **Changed older tests:** the three edits remove only the old "a person's pull request fails" promise, which the owner's ask in [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety) drops on purpose. Each still proves its shortcut rule.
- **Every ask of the owner** is matched to a criterion, there are no open blockers to answer, and I raised nothing new.

On the pull request [#865](https://github.com/dokima-dev/dokima/pull/865) (the worker's build), the issue card shows the acceptance tests and the full test suite failing. That belongs to the code stage, and the system sends it back to the worker on its own, so this plan review doesn't cover it. I tried to run the full suite on the branch myself, but it didn't finish within 10 minutes, so I can't say what is failing.

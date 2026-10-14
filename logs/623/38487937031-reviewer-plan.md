# reviewer (plan) for #623

Run: https://github.com/dokima-dev/dokima/actions/runs/38487937031

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 92
> drwxr-xr-x  3 runner runner  4096 Oct 14 00:03 .
> drwxrwxrwt 18 root   root    4096 Oct 14 00:04 ..
> drwxr-xr-x  2 runner runner  4096 Oct 14 00:03 in
> -rw-r--r--  1 runner runner 18913 Oct 14 00:03 issue.md
> -rw-r--r--  1 runner runner     2 Oct 14 00:03 open_blockers.json
> -rw-r--r--  1 runner runner 47839 Oct 14 00:03 open_issues.json
> -rw-r--r--  1 runner runner    15 Oct 14 00:03 parent.json
> -rw-r--r--  1 runner runner  3782 Oct 14 00:03 plan.json
> 
> in:
> total 40
> drwxr-xr-x 2 runner runner 4096 Oct 14 00:03 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 00:03 ..
> -rw-r--r-- 1 runner runner 4579 Oct 14 00:03 01-planner.json
> -rw-r--r-- 1 runner runner 5314 Oct 14 00:03 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 1871 Oct 14 00:03 03-worker.json
> -rw-r--r-- 1 runner runner 3410 Oct 14 00:03 04-reviewer-pr.json
> -rw-r--r-- 1 runner runner 4510 Oct 14 00:03 05-planner.json
> # Issue #623: Symptoms join their cause instead of a new issue
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 621, 622 -->
> <!-- dokima-blocking: {"blocked_by": [622], "blocks": [], "loop": []} -->
> A symptom the reviewer finds becomes a comment on its cause; a shared cause files one issue.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/639 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/639/files)
> 
> <img src="https://raw.githubuserco

`2. Bash`
```
cd /tmp/pack; cat in/02-reviewer-plan.json in/04-reviewer-pr.json; cat parent.json; cd /home/runner/work/dokima/dokima; git log --oneline -8; git diff main --stat; git diff dc31f99 86b98ef -- tests/
```

> <persisted-output>
> Output too large (32.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tool-results/bn4svss5t.txt
> 
> Preview (first 2KB):
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38485834389",
>  "commit_before": "dc7df92430ae118188c8535490a95feca6eb72ee",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 114444,
>   "turns": 18,
>   "cost_usd": 0.7841202000000002,
>   "tokens_in": 959826,
>   "tokens_out": 8280
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/623/38485834389-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38485834389",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner planned three criteria with seven tests, all failing today."
>    ],
>    "decided": [
>     "A symptom names its cause and becomes a comment there.",
>     "A root cause issue's title starts with Root cause found.",
>     "A root cause names each symptom in one line, never as sub-issues."
>    ],
>    "open": [
>     "Two questions: how a root cause is marked, and how it links symptoms."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan carries all three asks with tests that fail for the right reason; both questions follow the owner's words.",
>   "raises": [],
>   "answers": [
>    {
>     "raise": "P1",
>     "answer": "done",
>     "why": "The owner named the issue a root cause found issue; the title carrying that mark

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main --stat; git show 86b98ef --stat; git show 86b98ef -- tests/ | head -80; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d['handback']['asks'],indent=1))"
```

> dokima/agent.py                   |  31 ++++--
>  dokima/raises.py                  |  12 ++-
>  tests/test_reviewer_verdict.py    |  10 +-
>  tests/test_symptoms_join_cause.py | 210 ++++++++++++++++++++++++++++++++++++++
>  4 files changed, 252 insertions(+), 11 deletions(-)
> commit 86b98ef6ebab7ab23fb01888d37ee31645706e93
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:03:06 2026 +0000
> 
>     planner for #623 (run 38487053530)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_reviewer_verdict.py | 10 ++++++----
>  1 file changed, 6 insertions(+), 4 deletions(-)
> commit 86b98ef6ebab7ab23fb01888d37ee31645706e93
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:03:06 2026 +0000
> 
>     planner for #623 (run 38487053530)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_reviewer_verdict.py b/tests/test_reviewer_verdict.py
> index e2add91..ad4a640 100644
> --- a/tests/test_reviewer_verdict.py
> +++ b/tests/test_reviewer_verdict.py
> @@ -30,6 +30,7 @@ from tests.test_reviewer_open_issues import both_checks, reviewer_pack
>  from tests import test_reviewer_settles as settles
>  
>  SEARCHED = [12, 15]  # both open issues in the faked pack
> +LINKS = {"symptom": {"cause": 12}, "root cause": {"symptoms": SEARCHED}, "new": {}}  # what each verdict names (#623)
>  NAMES = {"sym

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_reviewer_verdict.py tests/test_symptoms_join_cause.py 2>&1 | tail -5; git stash list; mkdir -p /tmp/mainchk && git worktree add -q /tmp/mainchk/wt main 2>&1|tail -1; cp tests/test_reviewer_verdict.py tests/test_symptoms_join_cause.py /tmp/mainchk/wt/tests/; cd /tmp/mainchk/wt && python3 -m pytest -q tests/test_reviewer_verdict.py tests/test_symptoms_join_cause.py 2>&1 | tail -12
```

> .............                                                            [100%]
> 13 passed in 2.61s
> assert None
>  +  where None = <function match at 0x7f2d7f943a60>('\\s*root cause found\\b', 'The board ignores closed pull requests.', re.IGNORECASE)
>  +    where <function match at 0x7f2d7f943a60> = re.match
>  +    and   re.IGNORECASE = re.I
> FAILED tests/test_symptoms_join_cause.py::test_the_root_cause_issue_links_each_symptom_and_makes_no_sub_issue - AssertionError: 623.3: no line of the root cause issue links its symptoms [12, 15] (symptom lines: [])
> assert False
>  +  where False = any(<generator object test_the_root_cause_issue_links_each_symptom_and_makes_no_sub_issue.<locals>.<genexpr> at 0x7f2d7dc03680>)
> FAILED tests/test_symptoms_join_cause.py::test_a_root_cause_naming_no_symptoms_is_rejected - AssertionError: 623.3: a root cause naming its symptoms [12, 15] was rejected:
>   raise 1 carries fields no raise has: symptoms
>   
> assert 1 == 0
> 8 failed, 5 passed in 2.27s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
cd /tmp/mainchk/wt && python3 -m pytest -q tests/test_reviewer_verdict.py tests/test_symptoms_join_cause.py 2>&1 | grep FAILED | cut -c1-200; cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainchk/wt; python3 -m pytest -q -x 2>&1 | tail -3
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bh7cfmxub). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** Still reviewing the plan; the full test suite is running in the background.

`6. Bash`
```
sleep 100; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output | cut -c1-200 | tail -15
```

> <tool_use_error>Blocked: sleep 100 followed by: cat /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output cut -c1-200 tail -15. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`7. Bash`
```
cut -c1-200 /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output | tail -15
```

> FAILED tests/test_reviewer_verdict.py::test_a_review_filing_its_own_issue_without_one_of_the_three_verdicts_is_rejected - AssertionError: 622.2: the verdict 'symptom' was rejected:
> FAILED tests/test_symptoms_join_cause.py::test_a_symptom_becomes_a_comment_on_its_cause_and_files_no_issue - AssertionError: 623.1: a symptom was filed as a new issue: {500: {'title': 'The board ignor
> FAILED tests/test_symptoms_join_cause.py::test_a_confirmed_workers_symptom_becomes_a_comment_on_its_cause - AssertionError: 623.1: a confirmed symptom was filed as a new issue: {500: {'title': 'The bo
> FAILED tests/test_symptoms_join_cause.py::test_a_symptom_naming_no_cause_is_rejected - AssertionError: 623.1: a symptom naming its cause #12 was rejected:
> FAILED tests/test_symptoms_join_cause.py::test_a_root_cause_files_one_issue_marked_root_cause_found - AssertionError: 623.2: the root cause issue is not marked root cause found in its title: 'The boar
> FAILED tests/test_symptoms_join_cause.py::test_a_confirmed_workers_root_cause_files_one_marked_issue - AssertionError: 623.2: the root cause issue is not marked root cause found in its title: 'The boa
> FAILED tests/test_symptoms_join_cause.py::test_the_root_cause_issue_links_each_symptom_and_makes_no_sub_issue - AssertionError: 623.3: no line of the root cause issue links its symptoms [12, 15] (symp
> FAILED tests/test_symptoms_join_cause.py::test_a_root_cause_naming_no_symptoms_is_rejected - AssertionError: 623.3: a root cause naming its symptoms [12, 15] w

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner changed two older verdict tests so a symptom names its cause and a root cause its symptoms."],
  "decided": ["The three criteria and their seven tests stay as approved."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan now fixes the two older tests that clashed with it; every criterion still has a test that fails today.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A symptom of a known cause is added as a comment on the cause, with its evidence. No new issue is filed.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831", "criterion": "623.1"},
  {"ask": "It raises that cause as a \"root cause found\" issue", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.2"},
  {"ask": "instead of filing the symptom.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.2"},
  {"ask": "with the symptoms it found linked under it", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.3"},
  {"ask": "No sub-issues: sub-issues mean a split here.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831", "criterion": "623.3"}
 ],
 "behaviors": [
  {"criterion": "623.1", "one_behavior": true, "why": "A symptom becomes a comment on its cause instead of an issue."},
  {"criterion": "623.2", "one_behavior": true, "why": "A root cause files one issue marked in its title."},
  {"criterion": "623.3", "one_behavior": true, "why": "The root cause issue links its symptoms, never as sub-issues."}
 ],
 "edge_cases": [
  {"criterion": "623.1", "cut": [], "missing": []},
  {"criterion": "623.2", "cut": [], "missing": []},
  {"criterion": "623.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_symptoms_join_cause.py::test_a_symptom_becomes_a_comment_on_its_cause_and_files_no_issue", "only_its_behavior": true, "
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['summary']="The plan now fixes the two older tests that clashed with it; every new test still fails today."
d['summary']="The plan fixes the two older tests that clashed with it; each new test still fails today."
d['previous_step']['did']=["The planner changed two older tests so symptoms name causes and causes name symptoms."]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 623 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?; tail -3 /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output | cut -c1-200
```

> 0
> FAILED tests/test_symptoms_join_cause.py::test_a_confirmed_workers_root_cause_files_one_marked_issue - AssertionError: 623.2: the root cause issue is not marked root cause found in its title: 'The boa
> FAILED tests/test_symptoms_join_cause.py::test_the_root_cause_issue_links_each_symptom_and_makes_no_sub_issue - AssertionError: 623.3: no line of the root cause issue links its symptoms [12, 15] (symp
> FAILED tests/test_symptoms_join_cause.py::test_a_root_cause_naming_no_symptoms_is_rejected - AssertionError: 623.3: a root cause naming its symptoms [12, 15] was rejected:

**Agent:** I approved the plan for [#623](https://github.com/dokima-dev/dokima/issues/623) (symptoms join their cause instead of a new issue). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **What changed:** the planner fixed only the two older tests from [#622](https://github.com/dokima-dev/dokima/issues/622) (the three verdicts on a raised issue) that this plan made fail. They now give a symptom its cause and a root cause its symptoms. The code review on [#639](https://github.com/dokima-dev/dokima/pull/639) (the pull request for this issue) asked for exactly that fix. Both tests still check that a review with no verdict, or a made-up one, is rejected.
- **Tests on this branch:** the two fixed tests and the seven new ones all pass (13 passed in those two files).
- **Tests on main:** all seven new tests fail for the right reason: the feature isn't built. For example, a symptom is still filed as a new issue, and the title has no "Root cause found" mark. One of the fixed older tests also fails on main, as expected, because main doesn't accept a symptom naming its cause yet.
- **Owner's asks:** I found five in your words on [#615](https://github.com/dokima-dev/dokima/issues/615) (the reviewer checks if a raised issue shares a known cause). Each maps to one of the three criteria, and none is missing. Each criterion is one behavior with nothing to cut or add in its edge cases, and the size is fine.

I didn't wait for the full test suite on the branch to finish, so I only ran those two test files.

`10. Bash`
```
tail -4 /tmp/claude-1001/-home-runner-work-dokima-dokima/78b66d30-c8af-4657-bbe3-370958b175b8/tasks/bh7cfmxub.output | cut -c1-300; git -C /home/runner/work/dokima/dokima worktree list
```

> ...................................................................      [100%]
> 1147 passed in 425.70s (0:07:05)
> 
> [exited with code 0]
> /home/runner/work/dokima/dokima df480c3 [try/issue-623]

**Agent:** The full test suite has now finished on this branch: all 1147 tests pass. That fills the gap I mentioned, and the approval stands. The `main` copy I tested the new tests against has been removed.

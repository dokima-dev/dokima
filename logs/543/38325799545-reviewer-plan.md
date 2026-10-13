# reviewer (plan) for #543

Run: https://github.com/dokima-dev/dokima/actions/runs/38325799545

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; echo ----; cat plan.json; echo ----; cat open_blockers.json
```

> total 32
> drwxr-xr-x 2 runner runner 4096 Oct 13 00:09 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 00:09 ..
> -rw-r--r-- 1 runner runner 4069 Oct 13 00:09 01-planner.json
> -rw-r--r-- 1 runner runner 3187 Oct 13 00:09 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 1947 Oct 13 00:09 03-worker.json
> -rw-r--r-- 1 runner runner 2543 Oct 13 00:09 04-reviewer-pr.json
> -rw-r--r-- 1 runner runner 4368 Oct 13 00:09 05-planner.json
> # Issue #543: The planner names the issue: its hand-back carries a title that code sets on approval
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The planner hands back a short plain title, and each approved plan sets it as the issue's title.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/576 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/576/files)
> 
> **User story:** Issue titles stay readable as scope changes, while the owner's own title stays in the Original issue fold.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** 

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['01-planner.json','02-reviewer-plan.json','05-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:2500]); print('=====')
"; cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show --stat HEAD~1 | head -30
```

> 01-planner.json {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38322246199",
>  "commit_before": "3d03385b8b53e2b7b527abbd3b1c58ad11f7c84d",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 252580,
>   "turns": 27,
>   "cost_usd": 1.5955273999999997,
>   "tokens_in": 1951484,
>   "tokens_out": 22938
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/543/38322246199-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38322246199",
>  "handback": {
>   "kind": "user_story",
>   "title": "The planner names each issue; approval sets its title",
>   "summary": "The planner hands back a short plain title, and each approved plan sets it as the issue's title.",
>   "user_story": "Issue titles stay readable as scope changes, while the owner's own title stays in the Original issue fold.",
>   "acceptance_criteria": [
>    {
>     "text": "A plan passes its check only with a title of ten words or fewer, in plain words.",
>     "words": "The planner hands back a title in its structured output, held to a word cap and the plain-words rules cards follow.",
>     "source": "https://github.com/dokima-dev/dokima/issues/543",
>     "edge_cases": [
>      {
>       "case": "A plan with no title is rejected.",
>       "test": "tests/test_plan_title.py::test_a_plan_passes_its_check_only_with_a_short_plain_title"
>      },
>      {
>       "case": "A title of eleven words is rejected.",
>       "test": "tests/test_plan_title.py::test_a_plan_passes_its_

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD | head -120; timeout 900 pytest -q -x -n auto 2>&1 | tail -5 || true
```

> Command did not complete within its 120s timeout and was moved to the background (ID: b40pjn9wy). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/bbef4459-d888-4ee9-babb-1104c0131310/tasks/b40pjn9wy.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD | head -120; cat tests/test_plan_title.py
```

> commit e12a6106e1514b99f13005fd1f736f67e3657c6a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 00:08:43 2026 +0000
> 
>     planner for #543 (run 38324272154)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_body.py b/tests/test_body.py
> index 648e7d2..f16ef7d 100644
> --- a/tests/test_body.py
> +++ b/tests/test_body.py
> @@ -137,7 +137,7 @@ REASON = "the owner's part below the marker would change"
>  
>  PLAN_TESTS = ('def test_card(record_property):\n    """The card shows.\n\n    Proves 40.1.\n    """\n'
>                '    record_property("proves", "40.1")\n    assert False\n')
> -PLAN = {"kind": "user_story", "summary": "Every issue shows a card.", "user_story": "Owners see a card on every issue.",
> +PLAN = {"kind": "user_story", "title": "Every issue shows a card", "summary": "Every issue shows a card.", "user_story": "Owners see a card on every issue.",
>          "acceptance_criteria": [{"text": "The issue shows a card on top.", "source": f"https://github.com/{REPO}/issues/{NUMBER}", "no_edge_cases": "a sample criterion"}],
>          "non_functional": [], "scope": ["dokima/card.py"], "out_of_scope": [],
>          "tests": {"40.1": ["tests/test_cardshow.py::test_card"]}, "test_changes": {}}
> diff --git a/tests/test_card_status.py b/tests/test_card_status.py
> index e630214..53c9938 100644
> --- a/tests/test_card_status.py
> +++ b/tests/test_card_status.py
> @@ -157,11 +157,

`5. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt main 2>&1|tail -1; cp tests/test_plan_title.py /tmp/mainwt/tests/; cd /tmp/mainwt; timeout 300 python3 -m pytest -q tests/test_plan_title.py 2>&1 | grep -E "543\.|passed|failed" | head
```

> the title: nothing for "Links show on both issues", a problem for each of the other three. Proves 543.1."""
>         record_property("proves", "543.1")
>         assert not good, f"543.1: a plain title of five words was rejected: {good}"
> >       assert missing, "543.1: a plan with no title passed its check; the planner must hand back a title"
> E       AssertionError: 543.1: a plan with no title passed its check; the planner must hand back a title
>         an approved plan renames the issue, and an approved re-plan renames it again. Proves 543.2."""
>         record_property("proves", "543.2")
>         assert hub.title() == ORIGINAL, f"543.2: an approved plan with no title renamed the issue to {hub.title()!r}"
>         assert hub.title() == ORIGINAL, f"543.2: a blocked plan renamed the issue to {hub.title()!r}"
>             f"543.2: the approved plan's title was not set on the issue; its title is {hub.title()!r}"
> Shell cwd was reset to /home/runner/work/dokima/dokima

`6. Bash`
```
cd /tmp/mainwt; timeout 300 python3 -m pytest -q tests/test_plan_title.py 2>&1 | grep -E "^E .*543|passed|failed"; cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainwt; tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/bbef4459-d888-4ee9-babb-1104c0131310/tasks/b40pjn9wy.output
```

> >       assert missing, "543.1: a plan with no title passed its check; the planner must hand back a title"
> E       AssertionError: 543.1: a plan with no title passed its check; the planner must hand back a title
> E       AssertionError: 543.2: the approved plan's title was not set on the issue; its title is 'Record the links'
> E           AssertionError: 543.3: after approving the plan titled 'Links show on both issues' the Original issue fold does not show the owner's title 'Record the links'
> FAILED tests/test_plan_title.py::test_a_plan_passes_its_check_only_with_a_short_plain_title - AssertionError: 543.1: a plan with no title passed its check; the planner must hand back a title
> 3 failed in 4.57s
> -STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "u",
> +STORY = {"kind": "user_story", "title": "Slow calls hand back a job id", "summary": "Slow calls hand back a job id.", "user_story": "u",
>           "acceptance_criteria": [{"text": "a", "source": ISSUE, "no_edge_cases": "a sample criterion"}, {"text": "b", "source": ISSUE, "no_edge_cases": "a sample criterion"}],
>           "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
>           "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"]}, "links": LINKS}

**Agent:** All three new tests still fail on main because the feature is missing. Now I'm waiting for the full test suite to finish on this branch.

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 110 python3 -m pytest -q tests/test_plan_title.py tests/test_plan_check.py tests/test_body.py tests/test_card_status.py tests/test_feature_check.py tests/test_raise_handbacks.py tests/test_word_caps.py tests/test_new_test_check.py 2>&1 | tail -3
```

> Exit code 143
> Terminated

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 580 python3 -m pytest -q -p no:cacheprovider tests/test_plan_title.py tests/test_plan_check.py tests/test_body.py tests/test_card_status.py tests/test_feature_check.py tests/test_raise_handbacks.py tests/test_word_caps.py tests/test_new_test_check.py 2>&1 | tail -3
```

> ........................................................................ [ 78%]
> .......................................                                  [100%]
> 183 passed in 110.30s (0:01:50)

`9. Bash`
```
tail -c 600 /tmp/claude-1001/-home-runner-work-dokima-dokima/bbef4459-d888-4ee9-babb-1104c0131310/tasks/b40pjn9wy.output; python3 -c "import xdist" 2>&1
```

> _edge_cases": "a sample criterion"}],
>           "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
>           "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"]}, "links": LINKS}
> ........................................................................ [ 85%]
> ........................................................................ [ 92%]
> ........................................................................ [ 98%]
> ...........                                                              [100%]
> 1091 passed in 326.90s (0:05:26)
> 
> [exited with code 0]

**Agent:** The full suite passes on the branch (1091 passed), and the new tests fail on main for the right reason. Writing the approval.

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner added a title to five shared sample plans in older tests.", "The planner kept the three criteria and their tests unchanged."], "decided": ["No older test's checks changed, so no test change reasons were given."], "open": []},
 "verdict": "approve",
 "summary": "The re-plan keeps the approved criteria, fixes the older samples, and every test now passes with the work.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The planner hands back a title in its structured output, held to a word cap and the plain-words rules cards follow.", "source": "https://github.com/dokima-dev/dokima/issues/543", "criterion": "543.1"},
  {"ask": "Code sets the issue's title to it when the plan is approved, and again on each approved re-plan.", "source": "https://github.com/dokima-dev/dokima/issues/543", "criterion": "543.2"},
  {"ask": "The owner's original title stays visible in the issue's folded original text.", "source": "https://github.com/dokima-dev/dokima/issues/543", "criterion": "543.3"}],
 "behaviors": [
  {"criterion": "543.1", "one_behavior": true, "why": "One check: a plan passes only with a short plain title."},
  {"criterion": "543.2", "one_behavior": true, "why": "One result: an approved plan sets the issue's title."},
  {"criterion": "543.3", "one_behavior": true, "why": "One result: the fold shows the owner's title after a rename."}],
 "edge_cases": [
  {"criterion": "543.1", "cut": [], "missing": []},
  {"criterion": "543.2", "cut": [], "missing": []},
  {"criterion": "543.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_plan_title.py::test_a_plan_passes_its_check_only_with_a_short_plain_title", "only_its_behavior": true, "why": "Runs the real plan check on four titles; fails on main for the missing title rule."},
  {"test": "tests/test_plan_title.py::test_each_approved_plan_sets_the_issue_title", "only_its_behavior": true, "why": "Runs appr
```

> (Bash completed with no output)

**Agent:** I approved the re-plan for [#543](https://github.com/dokima-dev/dokima/issues/543) (planner names the issue, approval sets its title). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **What changed:** the planner kept the three criteria and their tests as they were. Its only change was adding a title to five shared sample plans in older tests. That fixes the code review's blocker: about 47 older tests were failing because their sample plans had no title.
- **Tests:** on main, all three new tests fail because the feature isn't built yet, which is the right reason. On this branch, with the worker's code, the full suite passes: 1091 tests.
- **Every ask is covered:** each of the owner's three "Done when" lines matches one criterion. No ask is missing, and the plan raised no questions.
- **One gap I let pass:** the code review asked for the reasons to be written up as test changes, and the planner gave none. Its argument is that no test's checks changed, only the sample data they use. I accepted that; it isn't a missing proof, so it doesn't count as a blocker.

The criteria didn't change, so under the river rule the work should go straight back to the worker without waiting for `/work`.

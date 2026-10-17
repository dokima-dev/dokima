# reviewer (plan) for #787

Run: https://github.com/dokima-dev/dokima/actions/runs/39025922397

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; echo ----; cat open_blockers.json; echo ----; cat plan.json
```

> <persisted-output>
> Output too large (36.1KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tool-results/bvkyc94oc.txt
> 
> Preview (first 2KB):
> .:
> total 128
> drwxr-xr-x  3 runner runner  4096 Oct 17 10:42 .
> drwxrwxrwt 18 root   root    4096 Oct 17 10:43 ..
> drwxr-xr-x  2 runner runner  4096 Oct 17 10:42 in
> -rw-r--r--  1 runner runner 27827 Oct 17 10:42 issue.md
> -rw-r--r--  1 runner runner     2 Oct 17 10:42 open_blockers.json
> -rw-r--r--  1 runner runner 60534 Oct 17 10:42 open_issues.json
> -rw-r--r--  1 runner runner 11639 Oct 17 10:42 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 17 10:42 parent.json
> -rw-r--r--  1 runner runner  8076 Oct 17 10:42 plan.json
> 
> in:
> total 76
> drwxr-xr-x 2 runner runner 4096 Oct 17 10:42 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 10:42 ..
> -rw-r--r-- 1 runner runner 6552 Oct 17 10:42 01-planner.json
> -rw-r--r-- 1 runner runner 7074 Oct 17 10:42 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7483 Oct 17 10:42 03-planner.json
> -rw-r--r-- 1 runner runner 7373 Oct 17 10:42 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 8919 Oct 17 10:42 05-planner.json
> -rw-r--r-- 1 runner runner 8737 Oct 17 10:42 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 8921 Oct 17 10:42 07-planner.json
> # Issue #787: Autopilot merges by the repo's branch, method and labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 784 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 7

`2. Read`
```
/tmp/pack/issue.md
```

> 1	# Issue #787: Autopilot merges by the repo's branch, method and labels
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 779, 784 -->
> 5	<!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> 6	Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 7	
> 8	**Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/779
> 13	
> 14	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 15	
> 16	- https://github.com/dokima-dev/dokima/issues/741
> 17	- https://github.com/dokima-dev/dokima/issues/742
> 18	- https://github.com/dokima-dev/dokima/issues/744
> 19	- https://github.com/dokima-dev/dokima/issues/791
> 20	
> 21	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 22	
> 23	- https://github.com/dokima-dev/dokima/issues/783
> 24	- https://github.com/dokima-dev/dokima/issues/784
> 25	
> 26	
> 27	**User story:** Autopilot merges into my repo

`3. Read`
```
/tmp/pack/plan.json
```

> 1	{
> 2	 "kind": "user_story",
> 3	 "title": "Autopilot merges by the repo's branch, method and labels",
> 4	 "summary": "Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.",
> 5	 "user_story": "Autopilot merges into my repo's branch, my way, using my label names.",
> 6	 "acceptance_criteria": [
> 7	  {
> 8	   "text": "Autopilot merges pull requests into the default branch the settings name.",
> 9	   "words": "`branch.default: main`",
> 10	   "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
> 11	   "files": [
> 12	    "dokima/agent_autopilot.py"
> 13	   ],
> 14	   "edge_cases": [
> 15	    {
> 16	     "case": "The settings name a branch GitHub does not have: nothing merges, and the reason names it.",
> 17	     "test": "tests/test_settings_autopilot.py::test_a_default_branch_github_lacks_stops_saying_which"
> 18	    }
> 19	   ]
> 20	  },
> 21	  {
> 22	   "text": "With the default branch setting left empty, autopilot merges into the repo's default branch on GitHub.",
> 23	   "words": "better: read repo default_branch",
> 24	   "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
> 25	   "files": [
> 26	    "dokima/agent_autopilot.py",
> 27	    "dokima/settings.py"
> 28	   ],
> 29	   "edge_cases": [
> 30	    {
> 31	     "case": "The setting is empty text rather than no value.",
> 32	     "test": "tests/test_settings_autopilot.py::test_an_empty_text_default_branch_also_uses_githubs"
> 33	    }
> 34	   ]
> 35	  },
> 36	  {
> 37	   "te

`4. Read`
```
/tmp/pack/issue.md
```

`5. Read`
```
/tmp/pack/plan.json
```

> 1	# Issue #787: Autopilot merges by the repo's branch, method and labels
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 779, 784 -->
> 5	<!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> 6	Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 7	
> 8	**Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/779
> 13	
> 14	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 15	
> 16	- https://github.com/dokima-dev/dokima/issues/741
> 17	- https://github.com/dokima-dev/dokima/issues/742
> 18	- https://github.com/dokima-dev/dokima/issues/744
> 19	- https://github.com/dokima-dev/dokima/issues/791
> 20	
> 21	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 22	
> 23	- https://github.com/dokima-dev/dokima/issues/783
> 24	- https://github.com/dokima-dev/dokima/issues/784
> 25	
> 26	
> 27	**User story:** Autopilot merges into my repo

> 1	{
> 2	 "kind": "user_story",
> 3	 "title": "Autopilot merges by the repo's branch, method and labels",
> 4	 "summary": "Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.",
> 5	 "user_story": "Autopilot merges into my repo's branch, my way, using my label names.",
> 6	 "acceptance_criteria": [
> 7	  {
> 8	   "text": "Autopilot merges pull requests into the default branch the settings name.",
> 9	   "words": "`branch.default: main`",
> 10	   "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
> 11	   "files": [
> 12	    "dokima/agent_autopilot.py"
> 13	   ],
> 14	   "edge_cases": [
> 15	    {
> 16	     "case": "The settings name a branch GitHub does not have: nothing merges, and the reason names it.",
> 17	     "test": "tests/test_settings_autopilot.py::test_a_default_branch_github_lacks_stops_saying_which"
> 18	    }
> 19	   ]
> 20	  },
> 21	  {
> 22	   "text": "With the default branch setting left empty, autopilot merges into the repo's default branch on GitHub.",
> 23	   "words": "better: read repo default_branch",
> 24	   "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
> 25	   "files": [
> 26	    "dokima/agent_autopilot.py",
> 27	    "dokima/settings.py"
> 28	   ],
> 29	   "edge_cases": [
> 30	    {
> 31	     "case": "The setting is empty text rather than no value.",
> 32	     "test": "tests/test_settings_autopilot.py::test_an_empty_text_default_branch_also_uses_githubs"
> 33	    }
> 34	   ]
> 35	  },
> 36	  {
> 37	   "te

`6. Bash`
```
cd /tmp/pack; cat in/06-reviewer-plan.json; echo; python3 -c "import json;d=json.load(open('in/07-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000]); print(d.keys())"; cat parent.json; git -C /home/runner/work/dokima/dokima log --oneline -12
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39023853094",
>  "commit_before": "0f02aa83edd8aed1d65805f79b3096a9d3457fd0",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 144506,
>   "turns": 13,
>   "cost_usd": 0.6943298000000001,
>   "tokens_in": 626644,
>   "tokens_out": 6609
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/787/39023853094-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39023853094",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner added two criteria for shipping the default branch setting empty.",
>     "The planner added four tests for the empty default branch, for autopilot and for workflows.",
>     "The planner changed the shipped defaults test to expect an empty default branch."
>    ],
>    "decided": [
>     "When GitHub gives no default branch, the run stops and says so."
>    ],
>    "open": []
>   },
>   "verdict": "approve",
>   "summary": "The owner's answer is carried: the default branch ships empty, and every new test fails today for the right reason.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "`branch.default: main`",
>     "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
>     "criterion": "787.1"
>    },
>    {
>     "ask": "better: read repo default_branch",
>     "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
>     "criterion": "787.2"
>    },
>    {
>     "ask": "`mer

`7. Bash`
```
cd /home/runner/work/dokima/dokima; diff <(python3 -c "import json;print(json.dumps(json.load(open('/tmp/pack/in/05-planner.json'))['handback'],indent=1,sort_keys=True))") <(python3 -c "import json;print(json.dumps(json.load(open('/tmp/pack/plan.json')),indent=1,sort_keys=True))"); git diff main --stat; timeout 600 python3 -m pytest -q tests/test_settings_autopilot.py 2>&1 | tail -30
```

> dokima/agent_autopilot.py        |  29 +--
>  dokima/audit.py                  |  54 ++--
>  dokima/defaults.yaml             |  23 +-
>  dokima/manifest.py               |  53 +---
>  tests/test_settings_audit.py     | 393 -----------------------------
>  tests/test_settings_autopilot.py | 530 +++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_merge.py     |   4 +-
>  tests/test_start.py              |   5 +-
>  8 files changed, 563 insertions(+), 528 deletions(-)
>   
>   At index 0 diff: 'filed-by-dokima' != 'found-by-bot'
>   
>   Full diff:
>     [
>   -     'found-by-bot',
>   +     'filed-by-dokima',
>     ]
> FAILED tests/test_settings_autopilot.py::test_the_shipped_settings_leave_the_default_branch_empty - AssertionError: 787.8: the shipped default branch setting is 'main', not empty
> assert 'main' in ('', None)
> FAILED tests/test_settings_autopilot.py::test_a_repo_with_no_settings_file_merges_into_githubs_default_branch - AssertionError: 787.8: with no settings file, autopilot did not merge into GitHub's develop: HTTP 404: Not Found
> assert False
> FAILED tests/test_settings_autopilot.py::test_with_the_default_branch_empty_workflows_get_githubs_default_branch - AssertionError: 787.9: workflows were given default branch '', not GitHub's trunk
> assert '' == 'trunk'
>   
>   - trunk
> FAILED tests/test_settings_autopilot.py::test_github_giving_no_default_branch_stops_the_run_saying_why - AssertionError: 787.9: with no default branch known, workflows were given:
>   TESTS_RUN_ALL=pytest -q -p no:cacheprov

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3 origin/main main 2>&1|head; git diff origin/main --stat; git diff origin/main -- dokima/ tests/test_settings_merge.py tests/test_start.py | head -80
```

> 840c660 Required checks, labels and the audit follow settings (#809)
> 17b9275 Planner's test limits and docstrings follow settings (#808)
> 8564320 Tests are found and tagged by the test settings (#806)
>  dokima/agent_autopilot.py        |  29 +--
>  dokima/audit.py                  |  54 ++--
>  dokima/defaults.yaml             |  23 +-
>  dokima/manifest.py               |  53 +---
>  tests/test_settings_audit.py     | 393 -----------------------------
>  tests/test_settings_autopilot.py | 530 +++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_merge.py     |   4 +-
>  tests/test_start.py              |   5 +-
>  8 files changed, 563 insertions(+), 528 deletions(-)
> diff --git a/dokima/agent_autopilot.py b/dokima/agent_autopilot.py
> index 8e0b2e4..b747244 100644
> --- a/dokima/agent_autopilot.py
> +++ b/dokima/agent_autopilot.py
> @@ -8,9 +8,8 @@ import json
>  import os
>  import subprocess
>  import time
> -import urllib.parse
>  
> -from dokima import body as issue_body, card, manifest, raises, settings
> +from dokima import body as issue_body, card, raises
>  from dokima.card import field_icon
>  
>  
> @@ -153,26 +152,7 @@ def named(numbers):
>      return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]
>  
>  
> -FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268), under its name in settings (#784)
> -
> -
> -def filed_label(repo):
> -    """The filed label's name in the labels setting, created in REPO when missing.
> -
> -    It gets its color from the settings and its descri

**Agent:** Still reviewing: main moved after the plan (a new merge landed), so I'm rerunning the plan's tests against current main.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; git log -1 --format=%B origin/main | head -20; rm -rf /tmp/wt; git worktree add -q /tmp/wt origin/main 2>&1|tail -1; cp tests/test_settings_autopilot.py /tmp/wt/tests/; cd /tmp/wt; git diff origin/main..try/issue-787 -- tests/test_settings_merge.py tests/test_start.py | git apply 2>&1; timeout 600 python3 -m pytest -q -p no:cacheprovider tests/test_settings_autopilot.py 2>&1 | grep -E "FAILED|passed|failed" 
```

> Required checks, labels and the audit follow settings (#809)
> 
> * planner for #784 (run 39018821717)
> 
> * planner for #784 (run 39020520635)
> 
> * worker for #784 (run 39022732330)
> 
> Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> ---------
> 
> Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>         assert done.returncode == 0, f"787.8: the settings reader failed in a repo with no settings file:\n{done.stderr[-800:]}"
>         assert done.returncode == 0, f"787.9: the settings lines for workflows failed:\n{done.stderr[-800:]}"
> FAILED tests/test_settings_autopilot.py::test_autopilot_merges_into_the_default_branch_the_settings_name - AssertionError: 787.1: autopilot did not merge into trunk, the settings' default branch: HTTP 404: Not Found
> FAILED tests/test_settings_autopilot.py::test_a_default_branch_github_lacks_stops_saying_which - AssertionError: 787.1: autopilot merged although GitHub has no trunk branch
> FAILED tests/test_settings_autopilot.py::test_with_no_default_branch_setting_autopilot_uses_githubs_default_branch - AssertionError: 787.2: autopilot did not merge into develop, GitHub's default branch: HTTP 404: Not Found
> FAILED tests/test_settings_autopilot.py::test_an_empty_text_default_branch_also_uses_githubs - AssertionError: 787.2: an empty default branch setting did not fall back to GitHub's develop: HTTP 4

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git diff origin/main...HEAD --stat; git merge-tree --write-tree origin/main HEAD >/dev/null && echo clean-merge; cd /tmp/wt && timeout 900 python3 -m pytest -q -p no:cacheprovider -x -n auto tests 2>&1 | tail -5
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bdr1wj569). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`11. Bash`
```
cd /home/runner/work/dokima/dokima; git diff origin/main...HEAD --stat; git merge-tree --write-tree origin/main HEAD >/dev/null && echo clean-merge; grep -n "def test_issues_dokima_files_carry" -A30 tests/test_settings_autopilot.py | head -40
```

> tests/test_settings_autopilot.py | 530 +++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_merge.py     |   2 +-
>  tests/test_start.py              |   5 +-
>  3 files changed, 535 insertions(+), 2 deletions(-)
> clean-merge
> 417:def test_issues_dokima_files_carry_the_filed_label_named_in_settings(record_property, repo, monkeypatch):
> 418-    """An issue Dokima files carries the filed label the settings name.
> 419-
> 420-    With `labels.filed: found-by-bot`, the issue a review files is created with found-by-bot, not filed-by-dokima.
> 421-    Proves 787.7."""
> 422-    record_property("proves", "787.7")
> 423-    repo("labels:\n  filed: found-by-bot\n")
> 424-    gh = fake(monkeypatch)
> 425-    lines = ap.file_issues(REPO, 57, reviewer_finding(), [])
> 426-    assert gh.created, f"787.7: no issue was filed: {lines}"
> 427-    got = [args[args.index("--label") + 1] for args in gh.created]
> 428-    assert got == ["found-by-bot"], f"787.7: the filed issue carries {got}, not found-by-bot as the settings say"
> 429-
> 430-
> 431-# 787.8 ---------------------------------------------------------------------------------------------------------
> 432-
> 433-
> 434-def settings_run(where, *args, github="trunk"):
> 435-    """Runs the settings reader in WHERE against a fake GitHub with default branch GITHUB.
> 436-
> 437-    A fake `gh` first on the PATH answers `gh api repos/o/r` with that branch (honouring `--jq .default_branch`), and
> 438-    the event file names it as the repo's default branch, as GitHub's own even

`12. Bash`
```
sleep 100; tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output
```

> <tool_use_error>Blocked: sleep 100 followed by: tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`13. Bash`
```
until grep -qE "passed|failed|error" /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output; do sleep 5; done; tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output
```

> clean-merge
>   
> assert None is not None
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 1 failed, 812 passed, 4 warnings in 367.05s (0:06:07)
> 
> [exited with code 0]

`14. Bash`
```
cd /tmp/wt; grep FAILED /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output; grep -B3 "assert None is not None" /tmp/claude-1001/-home-runner-work-dokima-dokima/8fccb6b0-60bf-4f8f-a97e-298c60643a87/tasks/bdr1wj569.output|head; timeout 300 python3 -m pytest -q -p no:cacheprovider tests/test_settings_merge.py tests/test_start.py 2>&1 | tail -3; cd /home/runner/work/dokima/dokima; git diff origin/main...HEAD -- tests/test_settings_merge.py tests/test_start.py
```

> 3 files changed, 535 insertions(+), 2 deletions(-)
> clean-merge
>   
> assert None is not None
>   labels: {'autopilot': 'autopilot', 'filed': 'filed-by-dokima'}, not {'plan': 'plan', 'work': 'work', 'autopilot': 'autopilot', 'filed': 'filed-by-dokima'}
> assert not ["branch.default: 'main', not ''", "labels: {'autopilot': 'autopilot', 'filed': 'filed-by-dokima'}, not {'plan': 'plan', 'work': 'work', 'autopilot': 'autopilot', 'filed': 'filed-by-dokima'}"]
> 1 failed, 21 passed in 55.31s
> diff --git a/tests/test_settings_merge.py b/tests/test_settings_merge.py
> index 8513d8b..e7aeafa 100644
> --- a/tests/test_settings_merge.py
> +++ b/tests/test_settings_merge.py
> @@ -133,7 +133,7 @@ def test_the_shipped_defaults_hold_the_owners_list(tmp_path, record_property):
>          "setup.python": "3.12",
>          "fence.test_setup_files": ["conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"],
>          "protected_paths": [".github/"],
> -        "branch.default": "main",
> +        "branch.default": "",
>          "records.branch": "logs",
>          "owner_docs": "AGENTS.md",
>          "style.docstrings": "required",
> diff --git a/tests/test_start.py b/tests/test_start.py
> index f22c2fe..3a7260b 100644
> --- a/tests/test_start.py
> +++ b/tests/test_start.py
> @@ -52,7 +52,8 @@ version of its body, oldest first, the way GitHub keeps a comment that is edited
>  or by `gh api` on repos/o/r/issues/N/comments (creates) and repos/o/r/issues/comments/ID (reads, or edits with PATCH),
>  the body given as -f/-F/--fie

**Agent:** Nearly done: one failure came from my own patching mistake, so I'm redoing that check correctly.

`15. Bash`
```
cd /tmp/wt; git checkout -q -- tests/; cd /home/runner/work/dokima/dokima; git diff origin/main...HEAD -- tests/test_settings_merge.py tests/test_start.py | (cd /tmp/wt && git apply && echo applied); cd /tmp/wt; timeout 300 python3 -m pytest -q -p no:cacheprovider tests/test_settings_merge.py tests/test_start.py 2>&1 | grep -E "^FAILED|assert not|passed|failed"; git stash -q; timeout 300 python3 -m pytest -q -p no:cacheprovider tests/test_start.py 2>&1 | tail -1; git stash pop -q
```

> applied
> >       assert not wrong, "793.3: the shipped defaults miss or change settings of the owner's list:\n" + "\n".join(wrong)
> E       assert not ["branch.default: 'main', not ''"]
> FAILED tests/test_settings_merge.py::test_the_shipped_defaults_hold_the_owners_list - AssertionError: 793.3: the shipped defaults miss or change settings of the owner's list:
> assert not ["branch.default: 'main', not ''"]
> 1 failed, 21 passed in 42.17s
> 5 passed in 40.33s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`16. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
old=json.load(open('in/06-reviewer-plan.json'))['handback']
r={
 "previous_step":{
  "did":["The planner planned again after the overlapping issue merged, with the same plan and tests."],
  "decided":["The plan keeps all nine criteria and their tests unchanged."],
  "open":["Filed issues already carry the settings' filed label on main, from the overlapping issue."]},
 "verdict":"approve",
 "summary":"The plan is unchanged and holds against today's main; one criterion is already met there and its test pins it.",
 "raises":[],"answers":[],
 "asks":old["asks"],"behaviors":old["behaviors"],"edge_cases":old["edge_cases"],"tests":old["tests"],"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 787 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?; git worktree remove --force /tmp/wt
```

> rc=0

**Agent:** I approved the plan for [#787](https://github.com/dokima-dev/dokima/issues/787) (autopilot merges by the repo's branch, method and labels). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **What the planner did:** it planned again after [#784](https://github.com/dokima-dev/dokima/issues/784) (labels and audit follow settings) merged. The plan and its tests are the same as the version approved last round. No blockers were open, so nothing needed an answer.
- **One criterion is already met on current main:** criterion 787.7, that issues Dokima files carry the filed label named in settings. [#784](https://github.com/dokima-dev/dokima/issues/784) built that, and it reached main after this branch's last update from main. On this branch its test still fails, as it should without the feature. On main it passes, so it now only guards behavior that already works. I didn't block on this.
- **Tests on current main with the plan's tests added:**
  - The other 18 new tests all fail because the feature is missing, each naming its criterion. None fails from a crash or a bad path.
  - The changed shipped-settings test fails only on the default branch still being "main". The owner asked to ship it empty.
  - The fake GitHub test file still passes after its change.
  - The branch merges into main with no conflict.
- **Every ask is covered:** each of the owner's asks, from [#740](https://github.com/dokima-dev/dokima/issues/740) and from the two comments on [#787](https://github.com/dokima-dev/dokima/issues/787), maps to a criterion. Every criterion is one behavior.

I didn't rerun the full test suite on current main. My first full run stopped at the first failure, which came from a mistake in how I applied the plan's test changes. When I applied them correctly, the shipped-settings test failed only on the default branch, as expected. I didn't repeat the full run after that.

# reviewer (plan) for #557

Run: https://github.com/dokima-dev/dokima/actions/runs/38307707581

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; echo ----; cat plan.json; echo ----; cat open_blockers.json
```

> total 64
> drwxr-xr-x 2 runner runner 4096 Oct 12 20:59 .
> drwxr-xr-x 3 runner runner 4096 Oct 12 20:59 ..
> -rw-r--r-- 1 runner runner 4231 Oct 12 20:59 01-planner.json
> -rw-r--r-- 1 runner runner 4705 Oct 12 20:59 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4533 Oct 12 20:59 03-planner.json
> -rw-r--r-- 1 runner runner 5917 Oct 12 20:59 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5669 Oct 12 20:59 05-planner.json
> -rw-r--r-- 1 runner runner 5156 Oct 12 20:59 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5347 Oct 12 20:59 07-planner.json
> # Issue #557: A repo setting lets a passed code review approve the merge; owner approval stays the default
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo setting lets Dokima merge a pull request whose code review passed, with owner approval still the default.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/363
> - https://github.com/dokima-dev/dokima/issues/375
> - https://github.com/dokima-dev/dokima/issues/378
> 
> 
> **User story:** Owners choose per repo whether autopilot merges alone or waits for their approval, which stays the default.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Accepta

`2. Bash`
```
cd /tmp/pack; python3 -c "import json;d=json.load(open('in/06-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; cd /home/runner/work/dokima/dokima; git diff main --stat; cat tests/test_merge_approval.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38307146338",
>  "commit_before": "5956e831f6912de4bf13ceb54b6b0490d5b057aa",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 94202,
>   "turns": 10,
>   "cost_usd": 0.6684580000000001,
>   "tokens_in": 561219,
>   "tokens_out": 6603
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/557/38307146338-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38307146338",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner added an audit criterion for the app's missing merge queue bypass.",
>     "The planner added cases for a red check and a branch behind main.",
>     "The planner renamed the setting to the owner's name, turned on by on."
>    ],
>    "decided": [
>     "A setting GitHub cannot read counts as off, so the pull request waits."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "One weak proof: the behind-main case passes today on any comment, so the owner may never be told.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Weak test",
>     "text": "557.2's behind-main case only checks a comment mentioning the owner contains `main`, which every record does via its icon links. Check words saying the branch misses main's newest commit.",
>     "evidence": "Today the `on-behind` run's record holds `raw.githubusercontent.com/o/r/main/dokima/icons/`, so `owner_told(behind, ..., \"main\")` passes.",

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main...HEAD --stat; git diff main...HEAD -- tests/test_audit.py tests/fake_gh.py tests/test_quiet_board.py
```

> tests/fake_gh.py             |  14 +-
>  tests/test_audit.py          |  69 +++++++++
>  tests/test_merge_approval.py | 345 +++++++++++++++++++++++++++++++++++++++++++
>  3 files changed, 426 insertions(+), 2 deletions(-)
> diff --git a/tests/fake_gh.py b/tests/fake_gh.py
> index cd74b3d..0a0b278 100644
> --- a/tests/fake_gh.py
> +++ b/tests/fake_gh.py
> @@ -10,7 +10,8 @@ What it answers (OWNER/REPO is the state's repo; any other repo is logged as uns
>      gh api [-X GET] repos/OWNER/REPO/labels[?...]                       labels, as GitHub's REST list
>      gh api [-X GET] repos/OWNER/REPO/branches/main/protection[/required_status_checks]
>                                                                          main's rule; 404 "Branch not protected" if none
> -    gh api [-X GET] repos/OWNER/REPO/installation                       the app's {"permissions": {...}}
> +    gh api [-X GET] repos/OWNER/REPO/installation                       the app's {"app_id": 1, "permissions": {...}}
> +    gh api [-X GET] repos/OWNER/REPO/actions/variables/NAME             the state's "variables"[NAME]; 404 when unset
>      gh api [-X GET] repos/OWNER/REPO/issues[?state=...&labels=...]      issues (open unless state says otherwise)
>      gh api [-X GET] repos/OWNER/REPO/issues/N[/comments]
>      gh api [-X POST] repos/OWNER/REPO/issues -f title=.. -f body=.. [-f labels[]=..]   opens an issue
> @@ -196,7 +197,16 @@ def rest(state, method, path, fields):
>      if method == "GET" and rest_path == "installation":
>          if

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x --no-header -p no:cacheprovider tests/test_audit.py::test_with_auto_merge_on_the_audit_reports_the_app_missing_from_the_merge_queue_bypass 2>&1 | tail -15; timeout 1200 python3 -m pytest -q --no-header -p no:cacheprovider tests/test_merge_approval.py 2>&1 | grep -E "^E  .*55|passed|failed" | head -20
```

> lines = a.compare(repo("on", ADMIN_BYPASS), REPO)
> >       assert len(lines) == 1, (f"557.3: with the setting on and Dokima's app missing from the merge queue ruleset's "
>                                  f"bypass list, the audit should give one line, got {lines}")
> E       AssertionError: 557.3: with the setting on and Dokima's app missing from the merge queue ruleset's bypass list, the audit should give one line, got []
> E       assert 0 == 1
> E        +  where 0 = len([])
> 
> tests/test_audit.py:534: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_audit.py::test_with_auto_merge_on_the_audit_reports_the_app_missing_from_the_merge_queue_bypass - AssertionError: 557.3: with the setting on and Dokima's app missing from the merge queue ruleset's bypass list, the audit should give one line, got []
> assert 0 == 1
>  +  where 0 = len([])
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed in 0.15s
>         """By default, a passed code review leaves the pull request waiting for your approval.
> E       AssertionError: 557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so waiting by default proves nothing
> _ test_with_the_setting_on_dokima_merges_a_passed_green_up_to_date_pull_request_directly _
>     def test_with_the_setting_on_dokima_merges_a_passed_green_up_to_date_pull_request_directly(record_property, runs):
>         """With the setting on, Dokima merges a passed,

`5. Bash`
```
cd /home/runner/work/dokima/dokima/tests; cat > /tmp/chk.py <<'EOF'
import sys; sys.path.insert(0,'.')
import tempfile, pathlib
import test_merge_approval as t
for name in ("on-behind","on-red"):
    review, setting, bypass, checks, files, behind = t.CASES[name]
    m=t.SettingReview(pathlib.Path(tempfile.mkdtemp()), review, t.ta.ON, checks, setting, bypass, files, behind)
    print(name, m.merged(), [t.says_behind(s) for s in m.said()], m.lines())
EOF
python3 /tmp/chk.py 2>&1 | tail -5
```

> on-behind None [False, False] ['Autopilot: PR #60 waits for your approval before it merges']
> on-red None [False] []

**Agent:** Checking is done: every new test fails today for the right reason, and the previous blocker is fixed. Writing the hand-back now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the behind-main case need plain words saying the branch is behind main.", "The planner made the red-check case prove those words appear only when the branch is behind."], "decided": [], "open": []},
 "verdict": "approve",
 "summary": "The plan covers every ask, and each test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "thats why i thought default behavior is hitl and you can turn on autopilot approval setting", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "With the repo variable DOKIMA_AUTO_MERGE unset or off (the default), a pull request waits for the owner's approval, as today.", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "allow bot approve for me with some narrow privilege", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.2"},
  {"ask": "With DOKIMA_AUTO_MERGE=on, a pull request whose code review passed, whose required checks are green on its head and whose branch contains main's newest commit is merged by Dokima's app directly", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.2"},
  {"ask": "with the setting on and the code review passed, Dokima's app merges as a bypass actor limited to pull requests only (never direct pushes to main)", "source": "https://github.com/dokima-dev/dokima/issues/557#issuecomment-6132201738", "criterion": "557.2"},
  {"ask": "one that changes a workflow file still waits for the owner", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.2"},
  {"ask": "Workflow-file pull requests still wait for me.", "source": "https://github.com/dokima-dev/dokima/issues/557#issuecomment-6132201738", "criterion": "557.2"},
  {"ask": "With DOKIMA_AUTO_MERGE=on, the setup audit reports when the app is mi
```

> Exit code 1
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/The planner made the red-check case prove those words appear only when the branch is behind./The planner made the red-check case prove those words appear only when behind./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 557 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#557](https://github.com/dokima-dev/dokima/issues/557) (a repo setting that lets a passed code review merge without the owner's approval). It now goes to the owner, who starts the build with `/work`. Autopilot is off on this issue, so nothing starts on its own.

- **Last round's blocker is fixed.** The "branch behind main" check used to pass on any comment. It now needs plain words saying the branch is behind main, and links don't count. I ran the behind-main and red-check cases on today's code: nothing claims the branch is behind in either one, so the check can no longer pass by accident.
- **Every new test fails today, and for the right reason.** The default case fails because, with the setting on, Dokima still doesn't merge, so there is no setting yet. The setting-on case fails because the merge still waits for the owner's approval. The audit case fails because nothing reports the missing merge queue bypass.
- **Every ask is covered.** I matched each of the owner's asks to a criterion, including their later comment: use GitHub's narrow bypass instead of the bot approving its own pull request, and pull requests that change a workflow file still wait for them.
- **Size is fine.** There are three criteria, each one behavior with its own test, and no edge cases missing.

There were no open blockers to answer, and I raised nothing new. The review is in `/tmp/dokima-out/review.json`, and it passes both hand-back checks.

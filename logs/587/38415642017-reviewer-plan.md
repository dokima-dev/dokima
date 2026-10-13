# reviewer (plan) for #587

Run: https://github.com/dokima-dev/dokima/actions/runs/38415642017

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #587: Autopilot only tries to merge; GitHub decides
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 589 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [588], "loop": []} -->
> Autopilot stops reading a repo variable and lets GitHub's own rules merge the pull request or hold it.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/588
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/589
> 
> 
> **User story:** Autopilot asks GitHub to merge, and GitHub merges it or holds it for the owner's approval.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Autopilot's merge reads no repo variable, so setting or clearing one changes nothing.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-5

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {"number": 580}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38413800739",
>  "commit_before": "507df8606bd0c0d74b549dfcb7a9bc4434b357c8",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 700270,
>   "turns": 24,
>   "cost_usd": 1.9383712000000002,
>   "tokens_in": 2040145,
>   "tokens_out": 32406
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/587/38413800739-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38413800739",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/587#issuecomment-6147887878"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests | head -400
```

> commit 58cc776827ff46800f7f3e4cdf1a2198b7209070
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 14:41:55 2026 +0000
> 
>     planner for #587 (run 38413800739)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_automerge.py      |  17 ++-
>  tests/test_merge_approval.py | 270 ++++++++++++++++++++++---------------------
>  2 files changed, 148 insertions(+), 139 deletions(-)
> commit 58cc776827ff46800f7f3e4cdf1a2198b7209070
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 14:41:55 2026 +0000
> 
>     planner for #587 (run 38413800739)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_automerge.py b/tests/test_automerge.py
> index 56584ce..5925644 100644
> --- a/tests/test_automerge.py
> +++ b/tests/test_automerge.py
> @@ -656,15 +656,15 @@ def test_without_autopilot_an_approved_pull_request_waits_for_the_owner(record_p
>  def test_a_refused_merge_stops_for_the_owner_and_says_why(record_property, tmp_path):
>      """A merge that cannot happen leaves the pull request open, says why on it, mentions the owner and shows Needs you.
>  
> -    Runs the code review of #60 on autopilot, approving, four ways: a red check, no checks at all, GitHub refusing the
> -    merge for a conflict, and GitHub refusing it for branch protection. Each must leave #60 open, post no Autopilot
> -    

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_merge_approval.py | sed -n 400,600p; grep -n "AUTO_MERGE\|auto_merge_on\|def try_merge\|behind_main\|admin" dokima/agent.py | head -50; grep -rln "AUTO_MERGE\|auto_merge" tests dokima .github | head
```

> 2185:    Read from the branch itself, which any token that reads the repo may see; the protection endpoint needs admin
> 2229:def auto_merge_on(repo):
> 2230:    """True when the repo's variable DOKIMA_AUTO_MERGE is `on` (#557).
> 2234:        value = gh("api", f"repos/{repo}/actions/variables/{manifest.AUTO_MERGE}", "-q", ".value")
> 2237:            print(f"::warning::{manifest.AUTO_MERGE} could not be read, so it counts as off: {gh_reason(e)}")
> 2242:def behind_main(repo, head):
> 2247:def try_merge(repo, pr):
> 2249:    check on that head has passed. With DOKIMA_AUTO_MERGE on, Dokima's app merges it directly, past the rule's
> 2263:        bypass = auto_merge_on(repo)
> 2264:        if bypass and behind_main(repo, head):
> 2267:        gh("pr", "merge", str(pr), "-R", repo, "--squash", "--match-head-commit", head, *(["--admin"] if bypass else []))
> tests/test_merge_approval.py
> tests/test_autopilot_checks.py
> tests/test_required_checks.py
> tests/test_audit.py
> dokima/manifest.py
> dokima/agent.py
> dokima/audit.py
> tests/test_automerge_confirmed.py

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 335,420p tests/test_merge_approval.py; sed -n 2225,2310p dokima/agent.py
```

> told_behind(behind, "587.2", "bypass, behind main")
>     assert not any(says_behind(s) for s in red.said()), \
>         (f"587.2 (bypass, red check): a comment on a branch that holds main's newest commit says it is behind main, so "
>          f"saying so proves nothing: {[plain(s)[-400:] for s in red.said()]}")
> 
> 
> def test_when_github_requires_approval_the_pull_request_waits_and_the_issue_says_so(record_property, runs):
>     """When GitHub requires your approval, the pull request waits and the issue says so.
> 
>     Proves 587.3.
>     Runs the code review approving #60 on autopilot, every check green, with no repo variable set, while main's rules
>     need the owner's approval and Dokima's app is on no exemption list. Two ways GitHub holds it: it turns on
>     auto-merge waiting on the approval, and it refuses the merge outright for the missing approval. Each time #60
>     must stay open and #57 must get exactly one line `Autopilot: PR #60 waits for your approval before it merges`:
>     a merge held for approval is a wait, not a failure."""
>     record_property("proves", "587.3")
>     for case in ("held", "held-refused"):
>         m = runs(case)
>         started(m, "587.3", case)
>         assert m.tried(), f"587.3 ({case}): autopilot never asked GitHub to merge #60, so GitHub never decided:\n{m.tail()}"
>         waits(m, "587.3", case)
>                     f"{', '.join(missing)}")
>         time.sleep(pause)
> 
> 
> def auto_merge_on(repo):
>     """True when the repo's variable DOKIMA_AUTO_MERGE is `on` 

**Agent:** Checking the plan's tests now: running them to confirm each fails today for the right reason.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x --no-header tests/test_merge_approval.py 2>&1 | tail -40
```

> E         
> E         ## run: Fail closed on a bad hand-back or the wrong model (exit 0)
> E         models: ['claude-opus-5-5']
> E         
> E         ## run: Report this run's GitHub calls (exit 0)
> E         ::notice title=GitHub calls::none
> E         
> E       assert [] == ['Autopilot: ...re it merges']
> E         
> E         Right contains one more item: 'Autopilot: PR #60 waits for your approval before it merges'
> E         
> E         Full diff:
> E         + []
> E         - [
> E         -     'Autopilot: PR #60 waits for your approval before it merges',
> E         - ]
> 
> tests/test_merge_approval.py:249: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_merge_approval.py::test_autopilots_merge_reads_no_repo_variable - AssertionError: 587.1 (variable on, GitHub requires approval): #57 did not get exactly one line reading 'Autopilot: PR #60 waits for your approval before it merges': []
>   ## run: Post the record as a comment, on the PR once there is one (exit 0)
>   r-person\",\n \"models\": [\n  \"claude-opus-5-5\"\n ],\n \"report\": {\n  \"duration_ms\": 1000,\n  \"turns\": 1,\n  \"cost_usd\": null,\n  \"tokens_in\": 0,\n  \"tokens_out\": null\n },\n \"log\": \"https://github.com/o/r/blob/logs/logs/57/42-reviewer-pr.md\",\n \"run\": \"https://github.com/o/r/actions/runs/42\",\n \"handback\": {\n  \"previous_step\": {\n   \"did\": [\n    \"Built the fix.\"\n   ],\n   \"decided\": [],\n   \"open\": []\n  },\n  \"verdict\": \"ap

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q --no-header tests/test_merge_approval.py tests/test_automerge.py tests/test_autopilot_checks.py tests/test_required_checks.py tests/test_audit.py tests/test_automerge_confirmed.py 2>&1 | grep -E "^(FAILED|ERROR|[0-9]+ (passed|failed))" | cut -c1-400
```

> FAILED tests/test_merge_approval.py::test_autopilots_merge_reads_no_repo_variable - AssertionError: 587.1 (variable on, GitHub requires approval): #57 did not get exactly one line reading 'Autopilot: PR #60 waits for your approval before it merges': []
> FAILED tests/test_merge_approval.py::test_when_github_lets_the_app_merge_autopilot_merges_and_says_so - AssertionError: 587.2 (bypass): GitHub lets Dokima's app merge without approval, yet #60 did not merge at its green head (merged: None, merges tried: [(['pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'], 'accepted: approval')])
> FAILED tests/test_merge_approval.py::test_when_github_requires_approval_the_pull_request_waits_and_the_issue_says_so - AssertionError: 587.3 (held-refused): #57 did not get exactly one line reading 'Autopilot: PR #60 waits for your approval before it merges': []
> 3 failed, 33 passed in 62.26s (0:01:02)

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "WORKFLOW_FILE\|PR_BLOCK" tests/test_automerge.py | head; grep -n "AUTO_MERGE" dokima/audit.py dokima/manifest.py tests/test_autopilot_checks.py tests/test_required_checks.py | head
```

> 57:WORKFLOW_FILE = ".github/workflows/ci.yml"
> 523:PR_BLOCK = review_pr("block")
> 707:    files = ["x57.py", WORKFLOW_FILE]
> dokima/audit.py:120:    """With DOKIMA_AUTO_MERGE on, a line when the merge queue ruleset lacks the app's bypass.
> dokima/audit.py:123:    if (github.variable(repo, manifest.AUTO_MERGE) or "").strip().lower() != "on":
> dokima/audit.py:130:    return [f"`{manifest.AUTO_MERGE}` is `on`, but Dokima's app is not a bypass actor of the merge queue ruleset for "
> tests/test_autopilot_checks.py:61:        if "actions/variables/DOKIMA_AUTO_MERGE" in joined:
> tests/test_required_checks.py:81:        if path == f"repos/{REPO}/actions/variables/DOKIMA_AUTO_MERGE":
> dokima/manifest.py:55:AUTO_MERGE = "DOKIMA_AUTO_MERGE"

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned three criteria: no repo variable read, merge when GitHub allows, wait when GitHub needs approval.",
          "Rewrote the merge approval tests to fake GitHub's rules instead of the repo variable."],
  "decided": ["A merge GitHub refuses for a missing approval now waits instead of stopping as a failure.",
              "Dropped the old tests that needed the repo variable."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries all three asks, and each test fails today because the repo variable still decides.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The repo variable goes away.", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "587.1"},
  {"ask": "Dokima's code only tries to merge; GitHub allows it", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "587.2"},
  {"ask": "or holds it for the owner", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "587.3"}
 ],
 "behaviors": [
  {"criterion": "587.1", "one_behavior": true, "why": "One result: the merge reads no repo variable."},
  {"criterion": "587.2", "one_behavior": true, "why": "One case: GitHub allows it, so it merges and says so."},
  {"criterion": "587.3", "one_behavior": true, "why": "One case: GitHub needs approval, so it waits and says so."}
 ],
 "edge_cases": [
  {"criterion": "587.1", "cut": [], "missing": []},
  {"criterion": "587.2", "cut": [], "missing": []},
  {"criterion": "587.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_merge_approval.py::test_autopilots_merge_reads_no_repo_variable", "only_its_behavior": true, "why": "Flips the variable against GitHub's rule both ways and records every variable read; fails today on the refused bypass."},
  {"test": "tests/test_merge_approval.py::test_when_github_lets_the_app_merge_autopilot_merges_and_says_so", "only_its_behavior": true
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Planned three criteria: no repo variable read, merge when GitHub allows, wait when GitHub needs approval./Planned three criteria: no variable read, merge when GitHub allows, wait when it needs approval./; s/A merge GitHub refuses for a missing approval now waits instead of stopping as a failure./A merge GitHub refuses for a missing approval now waits, not fails./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 587 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#587](https://github.com/dokima-dev/dokima/issues/587) (autopilot only tries to merge; GitHub decides). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** each of the three things the owner asked for in [#580](https://github.com/dokima-dev/dokima/issues/580) (approval by default; auto-merge only where GitHub allows) has its own criterion. The repo variable goes away, GitHub merges when it allows it, and otherwise the pull request waits for the owner's approval. I couldn't open #580 from here, so the owner's wording is as quoted in this issue's text.
- **Tests:** I ran all three. Each fails today for the right reason, because the repo variable still decides:
  - With the old switch on while GitHub needs approval, no line appears saying the pull request waits for approval.
  - With no variable set while GitHub would let Dokima's app merge, nothing merges.
  - When GitHub refuses the merge outright for a missing approval, no line says it waits.
- **Other tests:** the other 33 tests in the related files pass. The cases the planner dropped (a blocking review, a change to a workflow file) are still tested in `tests/test_automerge.py`.
- **Size:** fine. Each criterion is one behavior with one test.

I raised no blockers or questions. One thing for you: the setup audit (`dokima/audit.py:123`) still reads the repo variable. This plan only covers the merge itself, and the audit may belong to [#588](https://github.com/dokima-dev/dokima/issues/588) (the issue this one blocks), but I couldn't confirm that.

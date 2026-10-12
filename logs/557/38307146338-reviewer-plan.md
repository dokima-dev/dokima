# reviewer (plan) for #557

Run: https://github.com/dokima-dev/dokima/actions/runs/38307146338

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 52
> drwxr-xr-x  3 runner runner  4096 Oct 12 20:53 .
> drwxrwxrwt 18 root   root    4096 Oct 12 20:54 ..
> drwxr-xr-x  2 runner runner  4096 Oct 12 20:53 in
> -rw-r--r--  1 runner runner 20657 Oct 12 20:53 issue.md
> -rw-r--r--  1 runner runner     2 Oct 12 20:53 open_blockers.json
> -rw-r--r--  1 runner runner    16 Oct 12 20:53 parent.json
> -rw-r--r--  1 runner runner  4901 Oct 12 20:53 plan.json
> 
> in:
> total 48
> drwxr-xr-x 2 runner runner 4096 Oct 12 20:53 .
> drwxr-xr-x 3 runner runner 4096 Oct 12 20:53 ..
> -rw-r--r-- 1 runner runner 4231 Oct 12 20:53 01-planner.json
> -rw-r--r-- 1 runner runner 4705 Oct 12 20:53 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4533 Oct 12 20:53 03-planner.json
> -rw-r--r-- 1 runner runner 5917 Oct 12 20:53 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5669 Oct 12 20:53 05-planner.json
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
> - https://github.com/dokima-dev/dok

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('04-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; cd /home/runner/work/dokima/dokima; git log --stat -3 | head -40; wc -l tests/test_merge_approval.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38306094382",
>  "commit_before": "5760440d39de8fe04e00864206e862bd7f2b33c1",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 70902,
>   "turns": 8,
>   "cost_usd": 0.561641,
>   "tokens_in": 401895,
>   "tokens_out": 5709
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/557/38306094382-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38306094382",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner rewrote the merge criterion: Dokima's app merges through its pull request bypass.",
>     "The planner added a case where GitHub refuses the bypass and the owner sees why."
>    ],
>    "decided": [
>     "The bot never approves its own pull request.",
>     "The setting is a repo variable named merge approval, turned on by true."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "The plan misses two asks in the issue's Done-when and its tests use a different setting name than the owner's.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "No criterion",
>     "text": "The owner asks the setup audit to report when the app is missing from the merge-queue ruleset's pull-request-only bypass list. No criterion carries it; `dokima/audit.py` is not in scope.",
>     "evidence": "Issue #557 Done when, third line; `dokima/audit.py` compares live settings with the manifest; plan scope lacks it.",
>     "raised_by

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_merge_approval.py; git diff 5760440 5956e83 -- tests/fake_gh.py tests/test_audit.py
```

> """A repo setting lets a passed code review merge through a narrow bypass (#557).
> 
> By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
> `DOKIMA_AUTO_MERGE`, set to `on`, turns the setting on; unset or `off`, it is off. With it on, once a code review
> passes, Dokima's app merges the pull request directly, as a bypass actor of the branch rule, a bypass the owner limits
> to pull requests (never direct pushes to main); only when every check on its head is green and its branch contains
> main's newest commit, and never when it changes a workflow file. The bot never approves its own pull request.
> 
> These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
> GitHub of test_automerge_confirmed.py where #60 is protected the way main is: a plain `gh pr merge` only turns on
> auto-merge waiting on an approval ("accepts": "approval"). This file teaches that fake four more things:
>   - the setting: `gh api repos/o/r/actions/variables/DOKIMA_AUTO_MERGE` (with or without -q/--jq `.value`) and
>     `gh variable get DOKIMA_AUTO_MERGE` answer the value the test chose, 404 when it is unset, or a failure;
>   - the bypass: when the test makes Dokima's app a bypass actor ("bypass": true), a merge it asks past the rule, by
>     `gh pr merge --admin` or `gh api -X PUT repos/o/r/pulls/N/merge`, merges, as GitHub lets a bypass actor merge a
>     pull request, whatever its checks or base; when it is

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x tests/test_merge_approval.py tests/test_audit.py::test_with_auto_merge_on_the_audit_reports_the_app_missing_from_the_merge_queue_bypass 2>&1 | grep -E "^(E  |FAILED|PASSED|[0-9]+ (passed|failed))|557" | head -40
```

> Proves 557.1.
>         record_property("proves", "557.1")
>             started(m, "557.1", case)
>             assert m.merged() is None, (f"557.1 ({case}): #60 merged with no owner approval though the setting is not on "
>             assert m.lines() == [WAITS], (f"557.1 ({case}): #57 did not get exactly one line reading {WAITS!r}, as today: "
> >       assert c.merged() == ta.HEAD, ("557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so "
> E       AssertionError: 557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so waiting by default proves nothing
> E       assert None == 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'
> E        +  where None = merged()
> E        +    where merged = <test_merge_approval.SettingReview object at 0x7f91de820620>.merged
> E        +  and   'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1' = ta.HEAD
> FAILED tests/test_merge_approval.py::test_by_default_a_pull_request_waits_for_the_owners_approval - AssertionError: 557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so waiting by default proves nothing
> 1 failed in 10.70s

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_merge_approval.py tests/test_audit.py::test_with_auto_merge_on_the_audit_reports_the_app_missing_from_the_merge_queue_bypass 2>&1 | grep -E "^(E   |FAILED)" | head -20
```

> E       AssertionError: 557.1: with the setting `on` Dokima did not merge #60: there is no setting yet, so waiting by default proves nothing
> E       assert None == 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'
> E        +  where None = merged()
> E        +    where merged = <test_merge_approval.SettingReview object at 0x7f026a96c5c0>.merged
> E        +  and   'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1' = ta.HEAD
> E       AssertionError: 557.2 (on): with the setting on and the code review passed, Dokima did not merge #60 at its green head (merged: None, merges tried: [(['pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'], 'accepted: approval')])
> E         ## run: Post the record as a comment, on the PR once there is one (exit 0)
> E         \"stage\": \"pr\",\n \"run_id\": \"42\",\n \"commit_before\": \"a35d64c0c5ad8a0b677805d079f0f02cc83b9946\",\n \"started_by\": \"owner-person\",\n \"models\": [\n  \"claude-opus-5-5\"\n ],\n \"report\": {\n  \"duration_ms\": 1000,\n  \"turns\": 1,\n  \"cost_usd\": null,\n  \"tokens_in\": 0,\n  \"tokens_out\": null\n },\n \"log\": \"https://github.com/o/r/blob/logs/logs/57/42-reviewer-pr.md\",\n \"run\": \"https://github.com/o/r/actions/runs/42\",\n \"handback\": {\n  \"previous_step\": {\n   \"did\": [\n    \"Built the fix.\"\n   ],\n   \"decided\": [],\n   \"open\": []\n  },\n  \"verdict\": \"approve\",\n  \"summary\": \"Every criterion's test passes.\",\n  \"raises\": [],\n  \"answers\": [

**Agent:** Tests fail today for the right reason. Now checking whether the "behind main" case is too loose.

`6. Bash`
```
cd /home/runner/work/dokima/dokima/tests; cat > /tmp/chk.py <<'EOF'
import sys; sys.path.insert(0,'.')
import tempfile, test_merge_approval as t, test_automerge as ta
from test_start import OWNER
for name in ("on-behind","on-red","on-refused"):
    review, setting, bypass, checks, files, behind = t.CASES[name]
    m = t.SettingReview(tempfile.mkdtemp(), review, ta.ON, checks, setting, bypass, files, behind)
    hits=[s for s in m.said() if f"@{OWNER}" in s]
    print(name, "merged", m.merged())
    for s in hits:
        i=s.find("main"); print("  main@",i, repr(s[max(0,i-60):i+40]) if i>=0 else "")
        print("  red", ta.RED_NAME in s, "rule", t.RULE in s)
EOF
timeout 600 python3 /tmp/chk.py 2>&1 | tail -20
```

> on-behind merged None
>   main@ 71 '-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16"'
>   red False rule False
> on-red merged None
>   main@ 71 '-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16"'
>   red True rule False
> on-refused merged None
>   main@ 71 '-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16"'
>   red False rule False

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "waits for your approval\|def .*merge" dokima/agent.py | head; grep -n "merge\b\|autopilot" .github/workflows/agent.yml | head
```

> 2185:def try_merge(repo, pr):
> 2216:                   "waits": "Autopilot: PR #{pr} waits for your approval before it merges"}
> 2223:def merge_outcome(repo, pr):
> 2250:def automerge(repo, number):
> 2278:def merge_tree(repo, number, owners):
> 2753:                            step = ("stop", f"PR #{pr} waits for your approval before it merges. Approve it on GitHub, or "
> 10:# agent's, the bot sends a dokima-next signal that starts it here. On autopilot an approved plan starts the worker and
> 144:            # A worker's branch that clashes with main still starts: the merge is committed with its conflict markers,
> 146:            if [ "$ROLE" = worker ] && ! git -c user.name=dokima -c user.email=dokima@users.noreply.github.com merge -q --no-edit origin/main; then
> 164:          echo "PLANNER_BASE=$(git merge-base HEAD origin/main)" >> "$GITHUB_ENV"
> 331:               && ! { git fetch -q "$R" "try/issue-$N" && git merge -q --no-edit FETCH_HEAD && git push -q "$R" "HEAD:try/issue-$N"; }; then
> 403:      # On autopilot, a code review's approval with every check green merges the pull request here, so this step
> 405:      - name: Decide what follows, merge on autopilot, and say it on the card
> 451:          # On autopilot, one line on the issue where the owner would have typed `/work`.
> 452:          if [ -s "$OUT/autopilot.md" ]; then gh issue comment "$N" -R "$GITHUB_REPOSITORY" --body-file "$OUT/autopilot.md"; fi

**Agent:** Scope looks right: the merge lives in `dokima/agent.py`. Writing the review.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner added an audit criterion for the app's missing merge queue bypass.",
   "The planner added cases for a red check and a branch behind main.",
   "The planner renamed the setting to the owner's name, turned on by on."
  ],
  "decided": [
   "A setting GitHub cannot read counts as off, so the pull request waits."
  ],
  "open": []
 },
 "verdict": "block",
 "summary": "One weak proof: the behind-main case passes today on any comment, so the owner may never be told.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Weak test",
   "text": "557.2's behind-main case checks only that a comment mentioning the owner contains `main`, which every record already does through its icon links. Check the words that say the branch misses main's newest commit.",
   "evidence": "Today the `on-behind` run's record holds `raw.githubusercontent.com/o/r/main/dokima/icons/`, so `owner_told(behind, ..., \"main\")` passes."
  },
  {
   "kind": "issue",
   "label": "Close duplicate",
   "text": "The owner said to close #413 as a duplicate of #557; no step of this plan does it.",
   "evidence": "Owner's comment https://github.com/dokima-dev/dokima/issues/557#issuecomment-6132201738: \"Yes, close #413 as a duplicate.\""
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "thats why i thought default behavior is hitl and you can turn on autopilot approval setting", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "With the repo variable DOKIMA_AUTO_MERGE unset or off (the default), a pull request waits for the owner's approval, as today.", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "allow bot approve for me with some narrow privilege", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.2"},
  {"ask": "With DOKIMA_AUTO_MERGE=on, a pull request w
```

> Exit code 1
> raise 1's text holds 33 words, over its cap of 30: cut 3, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="557.2's behind-main case only checks a comment mentioning the owner contains `main`, which every record does via its icon links. Check words saying the branch misses main's newest commit."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 557 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I blocked the plan for issue [#557](https://github.com/dokima-dev/dokima/issues/557) (owner can let a passed code review merge) and sent it back to the planner. One test is too weak to count as proof. The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**Since the last review:** the planner fixed all three blockers.
- The audit now has its own criterion, 557.3, with its own test.
- Criterion 557.2 now has test cases for a red check and for a branch that is behind main.
- The setting uses your name for it, `DOKIMA_AUTO_MERGE`. The tests set it to `on`, set it to `off`, and leave it unset.

All three new tests fail today for the right reason: the feature isn't built yet. Every ask in the issue and in your comment maps to a criterion.

**The blocker:** the behind-main case in `test_with_the_setting_on_dokima_merges_a_passed_green_up_to_date_pull_request_directly` checks only that some comment mentioning you contains the text `main`.
- Every record already contains it, because its icon links point to `.../o/r/main/dokima/icons/...`.
- So the "you are told" part of that case passes today. Code that never tells you the branch is behind main would still pass.
- The fix is to check for wording that says the branch is missing main's newest commit.

**One thing outside the plan:** you said to close [#413](https://github.com/dokima-dev/dokima/issues/413) (the same setting, asked earlier) as a duplicate. No step in this plan does that, so I raised it as a separate issue for you to act on.

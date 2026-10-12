# reviewer (plan) for #557

Run: https://github.com/dokima-dev/dokima/actions/runs/38306094382

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 40
> drwxr-xr-x  3 runner runner  4096 Oct 12 20:44 .
> drwxrwxrwt 18 root   root    4096 Oct 12 20:44 ..
> drwxr-xr-x  2 runner runner  4096 Oct 12 20:44 in
> -rw-r--r--  1 runner runner 14311 Oct 12 20:44 issue.md
> -rw-r--r--  1 runner runner     2 Oct 12 20:44 open_blockers.json
> -rw-r--r--  1 runner runner    16 Oct 12 20:44 parent.json
> -rw-r--r--  1 runner runner  3805 Oct 12 20:44 plan.json
> 
> in:
> total 32
> drwxr-xr-x 2 runner runner 4096 Oct 12 20:44 .
> drwxr-xr-x 3 runner runner 4096 Oct 12 20:44 ..
> -rw-r--r-- 1 runner runner 4231 Oct 12 20:44 01-planner.json
> -rw-r--r-- 1 runner runner 4705 Oct 12 20:44 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4533 Oct 12 20:44 03-planner.json
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
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/561
> 
> 
> **User story:** Owners choose per repo whether autopilot merges alone or waits for their approval, which stays the default.
> 
> <img src="https://raw.githubusercont

`2. Bash`
```
cd /tmp/pack; cat parent.json; python3 -c "
import json
for f in ['in/01-planner.json','in/02-reviewer-plan.json','in/03-planner.json']:
  print('=====',f); print(json.dumps(json.load(open(f)),indent=1)[:6000])
"
```

> {"number": null}===== in/01-planner.json
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38302101193",
>  "commit_before": "3e1116e05ab2b4b35003f6aeacaeaa7cbd6a1f4b",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 392314,
>   "turns": 29,
>   "cost_usd": 1.725108,
>   "tokens_in": 2189218,
>   "tokens_out": 26124
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/557/38302101193-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38302101193",
>  "handback": {
>   "kind": "user_story",
>   "summary": "A repo setting lets a passed code review approve the pull request, so autopilot can merge alone.",
>   "user_story": "Owners choose per repo whether autopilot merges alone or waits for their approval, which stays the default.",
>   "acceptance_criteria": [
>    {
>     "text": "With the setting off, a pull request whose code review passed waits for the owner's approval, as today.",
>     "words": "By default a pull request waits for the owner's approval before it merges, as today.",
>     "source": "https://github.com/dokima-dev/dokima/issues/557",
>     "edge_cases": [
>      {
>       "case": "The setting was never set.",
>       "test": "tests/test_merge_approval.py::test_by_default_a_pull_request_waits_for_the_owners_approval"
>      },
>      {
>       "case": "The setting is set to false.",
>       "test": "tests/test_merge_approval.py::test_by_default_a_pull_request_waits_for_the_owners_approval"
>      },
>      {
>       "case

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3 -- tests/test_merge_approval.py; cat tests/test_merge_approval.py
```

> 5760440 planner for #557 (run 38305475633)
> 7f41440 planner for #557 (run 38302101193)
> """A repo setting lets a passed code review merge through a narrow bypass (#557).
> 
> By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
> `DOKIMA_MERGE_APPROVAL`, set to `true`, turns the setting on: once a code review passes, Dokima's app merges the pull
> request as a bypass actor of the branch rule, a bypass the owner limits to pull requests (never direct pushes to main).
> The bot never approves its own pull request. A pull request that changes a workflow file still waits for the owner,
> whatever the setting.
> 
> These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
> GitHub of test_automerge_confirmed.py where #60 is protected the way main is: a plain `gh pr merge` only turns on
> auto-merge waiting on an approval ("accepts": "approval"). This file teaches that fake three more things:
>   - the setting: `gh api repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL` (with or without -q/--jq `.value`) and
>     `gh variable get DOKIMA_MERGE_APPROVAL` answer the value the test chose, 404 when it is unset, or a failure;
>   - the bypass: when the test makes Dokima's app a bypass actor ("bypass": true), a merge it asks past the rule, by
>     `gh pr merge --admin` or `gh api -X PUT repos/o/r/pulls/N/merge`, merges, as GitHub lets a bypass actor merge a
>     pull request; when it is not one, GitHub

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_merge_approval.py -x 2>&1 | tail -30; grep -rn "DOKIMA_AUTO_MERGE\|DOKIMA_MERGE_APPROVAL\|bypass" dokima/*.py | head; ls dokima | grep -i -E "audit|setup|doctor"
```

> unreadable because GitHub fails the read. Each time #60 must stay open and #57 must get exactly the line
>         `Autopilot: PR #60 waits for your approval before it merges`: the bypass is used only when the setting says so.
>         A default means something only when there is a setting to change it: beside them, the same run with the setting
>         `true` must merge #60, or the test fails as proving nothing."""
>         record_property("proves", "557.1")
>         for case in ("unset", "false", "unreadable"):
>             m = runs(case)
>             started(m, "557.1", case)
>             assert m.merged() is None, (f"557.1 ({case}): #60 merged with no owner approval though the setting is not on "
>                                         f"(merges tried: {[(t['args'], t['result']) for t in m.tried()]})")
>             assert m.lines() == [WAITS], (f"557.1 ({case}): #57 did not get exactly one line reading {WAITS!r}, as today: "
>                                           f"{m.lines()}\n{m.tail()}")
>         c = runs("on")
> >       assert c.merged() == ta.HEAD, ("557.1: test setup: with the setting `true` Dokima did not merge #60, so there is no "
>                                        "setting and waiting by default proves nothing")
> E       AssertionError: 557.1: test setup: with the setting `true` Dokima did not merge #60, so there is no setting and waiting by default proves nothing
> E       assert None == 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'
> E        +  where None = merged()
> E    

`5. Bash`
```
cd /home/runner/work/dokima/dokima; head -30 dokima/audit.py; grep -n "ruleset\|bypass" dokima/audit.py | head; grep -n "up to date\|behind\|contains main\|BEHIND" dokima/agent.py .github/workflows/agent.yml | head
```

> """Compare the repo's live settings with the manifest; report drift on one pinned Setup issue.
> 
>     python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number") and .github/CODEOWNERS where it runs
> 
> compare() gives one plain line per setting that differs from dokima/manifest.py or could not be read; run() puts them
> on the Setup issue (opened, pinned and marked Needs you, or updated), closes it with one line once nothing is off, and
> writes nothing when nothing is off and none is open. Both take a GitHub object for every read and write; GitHub below
> is the real one, through gh.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> from dokima import board, manifest
> 
> TITLE = "Setup"
> MARK = "<!-- dokima-setup -->"
> NOTHING_OFF = "Nothing is off: every setting matches what Dokima needs."
> RANK = {"read": 1, "write": 2, "admin": 3}
> FAILED = (subprocess.CalledProcessError, RuntimeError)
> 
> 
> def reason(e):
>     """GitHub's reason for refusing a call, on one line."""
>     if isinstance(e, subprocess.CalledProcessError):
>         said = " ".join(str(e.stderr or "").split())
>         return re.sub(r"^gh:\s*", "", said) or f"gh exited with {e.returncode}"
>     return " ".join(str(e).split())

**Agent:** I've read the plan and its tests, run them, and checked the issue as it stands now. Writing the review.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner rewrote the merge criterion: Dokima's app merges through its pull request bypass.",
   "The planner added a case where GitHub refuses the bypass and the owner sees why."
  ],
  "decided": [
   "The bot never approves its own pull request.",
   "The setting is a repo variable named merge approval, turned on by true."
  ],
  "open": []
 },
 "verdict": "block",
 "summary": "The issue's Done-when now asks for more: a setup audit check and an up-to-date branch. The plan's tests use another setting name.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "No criterion",
   "text": "The owner asks the setup audit to report when the app is missing from the merge-queue ruleset's pull-request-only bypass list. No criterion or test carries it, and `dokima/audit.py` is not in scope.",
   "evidence": "Issue #557 Done when, third line; `dokima/audit.py` compares live settings with the manifest; plan scope lacks it."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "No criterion",
   "text": "The owner merges only when required checks are green on the head and the branch contains main's newest commit. 557.2 has no case for a branch behind main or a red check.",
   "evidence": "Issue #557 Done when, second line; `CASES` in `tests/test_merge_approval.py` uses only `ta.GREEN`, never a branch behind main."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Wrong setting name",
   "text": "The owner names the setting `DOKIMA_AUTO_MERGE`, turned on by `on`. The tests read `DOKIMA_MERGE_APPROVAL` set to `true`, so code built to the issue fails them. Rename, and test `off` too.",
   "evidence": "`tests/test_merge_approval.py` `SETTING = \"DOKIMA_MERGE_APPROVAL\"`, cases `true`/`false`; issue says `DOKIMA_AUTO_MERGE=on`, `unset or off`."
  }
 ],
 "answers": [],
 "asks": [
  {
   "ask": "thats why i thought default behavior is 
```

> Exit code 1
> summary holds more than one sentence: make it one sentence of at most 20 words saying what the run did
> raise 1's text holds 32 words, over its cap of 30: cut 2, keep the facts
> raise 2's text holds 32 words, over its cap of 30: cut 2, keep the facts

`7. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['summary']="The plan misses two asks in the issue's Done-when and its tests use a different setting name than the owner's."
r['raises'][0]['text']="The owner asks the setup audit to report when the app is missing from the merge-queue ruleset's pull-request-only bypass list. No criterion carries it; `dokima/audit.py` is not in scope."
r['raises'][1]['text']="The owner merges only when required checks are green on the head and the branch contains main's newest commit. 557.2 tests neither a branch behind main nor a red check."
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 557 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for issue #557 (letting autopilot merge alone) with 3 blockers for the planner. The review is in `/tmp/dokima-out/review.json` and passes both checks.

Since the last planner run, the issue's "Done when" list asks for more than the plan covers:

1. **Setup audit (no criterion).** The issue asks the setup audit to report when Dokima's app is missing from the merge-queue rule's bypass list. No criterion or test covers it, and `dokima/audit.py` isn't in the plan's scope.
2. **Branch must be current (no criterion).** The issue says Dokima merges only when the required checks are green and the branch contains main's newest commit. The tests only try green checks. None tries a red check or a branch that's behind main.
3. **Wrong setting name.** The issue calls the setting `DOKIMA_AUTO_MERGE`, switched on with `on` and off with `off`. The tests read `DOKIMA_MERGE_APPROVAL` with `true` and `false`. Code built the way the issue says would fail those tests.

The rest of the plan is sound:
- The planner fixed both of my earlier blockers: the bot no longer approves its own pull request, and the case where GitHub refuses the merge is now tested.
- Each criterion is one behavior.
- I ran the new tests and they fail today because the feature is missing, not because of a setup problem.

One thing I didn't turn into a blocker: you asked for [#413](https://github.com/dokima-dev/dokima/issues/413) (the same setting, asked for earlier) to close as a duplicate. The planner dropped it from the plan's related issues, but nothing in the plan closes it. It's a manual step for you.

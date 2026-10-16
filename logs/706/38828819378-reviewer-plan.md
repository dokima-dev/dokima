# reviewer (plan) for #706

Run: https://github.com/dokima-dev/dokima/actions/runs/38828819378

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 96
> drwxr-xr-x  3 runner runner  4096 Oct 16 00:19 .
> drwxrwxrwt 18 root   root    4096 Oct 16 00:19 ..
> drwxr-xr-x  2 runner runner  4096 Oct 16 00:19 in
> -rw-r--r--  1 runner runner  7402 Oct 16 00:19 issue.md
> -rw-r--r--  1 runner runner     2 Oct 16 00:19 open_blockers.json
> -rw-r--r--  1 runner runner 57736 Oct 16 00:19 open_issues.json
> -rw-r--r--  1 runner runner   592 Oct 16 00:19 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 16 00:19 parent.json
> -rw-r--r--  1 runner runner  2523 Oct 16 00:19 plan.json
> 
> in:
> total 12
> drwxr-xr-x 2 runner runner 4096 Oct 16 00:19 .
> drwxr-xr-x 3 runner runner 4096 Oct 16 00:19 ..
> -rw-r--r-- 1 runner runner 3235 Oct 16 00:19 01-planner.json
> # Issue #706: Public logs scrub only Claude's token, so a key from another secret could leak into transcripts and cards.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 680, 699 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [746], "loop": []} -->
> Public cards and records hide the key of whichever agent ran, not only Claude's.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/706#issuecomment-6205038882) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - http

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/owner_words.json /tmp/pack/parent.json; cat tests/test_agent_key_scrubbed.py; grep -n "SCRUB" .github/workflows/agent.yml; grep -rn "SCRUB" dokima/*.py | head -40
```

> {
>  "https://github.com/dokima-dev/dokima/issues/706": "Public logs scrub only Claude's token, so a key from another secret could leak into transcripts and cards.\n\n**Evidence:** `.github/workflows/agent.yml` sets `SCRUB_CLAUDE` from `CLAUDE_CODE_OAUTH_TOKEN` only (lines 115, 140, 299, 438, 462).\n\n**Verdict:** New\n\n**Open issues searched:** #680, #696, #699, #700\n\nThe planner raised it and the reviewer confirmed it on #698 ([run](https://github.com/dokima-dev/dokima/actions/runs/38673225960)).",
>  "https://github.com/dokima-dev/dokima/issues/706#issuecomment-6205033715": "/plan"
> }{"number": null}"""Tests for #706: the role's agent key never reaches a public card or record.
> 
> A role can run on an agent whose key lives in a secret other than Claude's (the settings file picks it). Every
> workflow step that removes Claude's token from what it publishes must remove that agent key too, and the run's record
> (its card and the file saved on the logs branch) must come out with every secret its step was given removed.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> WORKFLOW = os.path.join(ROOT, ".github", "workflows", "agent.yml")
> AGENT_KEY = "${{ secrets[env.AGENT_KEY || 'CLAUDE_CODE_OAUTH_TOKEN'] }}"
> SECRET = "kimi-sign-in-706-abcdefghijklmnop"
> 
> 
> def steps():
>     """Each step of the agent workflow, as its name and its env."""
>     out, name, env, in_env = [], None, None, False
>     for line in ope

`3. Bash`
```
cd /home/runner/work/dokima/dokima; for l in 100 140 290 340 440 465; do sed -n "$((l)),$((l+40))p" .github/workflows/agent.yml | grep -n "name:\|SCRUB\|run:" | head; echo ---; done; sed -n 340,420p dokima/agent_roles.py; grep -n "AGENT_KEY" .github/workflows/agent.yml | head
```

> 1:      - name: The role's agent, model and key from the settings file
> 3:        run: |
> 5:            || { echo "The settings file stopped the run: $(paste -sd' ' /tmp/agents-err.txt)" > /tmp/why.txt
> 21:      - name: Put up the run's card, queued
> 25:          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
> 26:          SCRUB_GITHUB: ${{ github.token }}
> 27:        run: |
> ---
> 6:      - name: The card says setting up
> 10:          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
> 11:          SCRUB_GITHUB: ${{ github.token }}
> 12:        run: |
> 17:      - name: Starting branch
> 20:        run: |
> ---
> 1:      - name: Code checks the pack has everything this role needs
> 2:        run: |
> 15:      - name: The card says working
> 19:          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
> 20:          SCRUB_GITHUB: ${{ github.token }}
> 21:        run: |
> 26:      - name: The agent starts now
> 27:        run: echo "STARTED=true" >> "$GITHUB_ENV"
> 29:      - name: The agent (Claude Code)
> 32:        run: |
> ---
> 15:      - name: The card says checking
> 19:          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
> 20:          SCRUB_GITHUB: ${{ github.token }}
> 21:        run: |
> 26:      - name: Fence - only in-scope changes, the planner's tests as committed
> 28:        run: |
> 36:      - name: Code checks the hand-back
> 41:        run: |
> ---
> 6:      - name: Remove secrets from the raw session files before they are uploaded
> 9:          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "Write this run's record" -A25 .github/workflows/agent.yml; grep -n '"record"' dokima/agent_roles.py; grep -n "def scrub" -A12 dokima/*.py
```

> 425:      - name: Write this run's record
> 426-        if: always()
> 427-        env:
> 428-          GH_TOKEN: ${{ github.token }}
> 429-          JOB_STATUS: ${{ job.status }}
> 430-        run: |
> 431-          if [ "$JOB_STATUS" = cancelled ]; then
> 432-            # Someone cancelled the run: its card says so, mentions no one, and nothing starts after it.
> 433-            mkdir -p "$OUT"
> 434-            python3 -m dokima.agent cancelled "$ROLE" "$STAGE" "$OUT" "${STARTED:-false}" /home/runner/.claude/projects
> 435-          elif [ "$STARTED" = true ]; then
> 436-            python3 -m dokima.agent record "$ROLE" "$STAGE" "$OUT" "$OUT/check.txt" "${PASSED:-false}" /home/runner/.claude/projects
> 437-          else
> 438-            # No agent started: a step with no reason of its own is named by GitHub's record of this run.
> 439-            mkdir -p "$OUT"
> 440-            [ -s /tmp/why.txt ] || gh api "repos/$GITHUB_REPOSITORY/actions/runs/${{ github.run_id }}/attempts/${{ github.run_attempt }}/jobs" \
> 441-              --jq '.jobs[].steps[] | select(.conclusion == "failure") | "The step \(.name) failed."' > /tmp/why.txt || true
> 442-            python3 -m dokima.agent not-started "$ROLE" "$STAGE" "$OUT" /tmp/why.txt
> 443-          fi
> 444-          cat "$OUT/comment.md" >> "$GITHUB_STEP_SUMMARY"
> 445-      - name: Remove secrets from the raw session files before they are uploaded
> 446-        if: always()
> 447-        env:
> 448-          SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
> 449-  

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 310,340p dokima/agent_roles.py; grep -n "record.json\|logs branch" .github/workflows/agent.yml | head -20; python -m pytest -q tests/test_agent_key_scrubbed.py 2>&1 | tail -30
```

> bad = problems_pack(argv[2], argv[3], argv[4])
>         for b in bad:
>             print(b)
>         return 1 if bad else 0
>     if argv[1] == "record":
>         role, stage, out, check_file, passed, log_dir = argv[2:8]
>         meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "commit_before": os.environ.get("BASE"),
>                 "started_by": os.environ.get("GITHUB_ACTOR"), "models": agents.models(role, out, log_dir),
>                 "report": agents.report(role, out), "log": os.environ.get("LOG_URL"),
>                 "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
>         text = open(check_file).read() if os.path.exists(check_file) else ""
>         earlier = []
>         folder = os.path.join(os.environ.get("PACK", ""), "in")
>         for name in sorted(os.listdir(folder)) if os.environ.get("PACK") and os.path.isdir(folder) else []:
>             try:
>                 earlier.append(json.load(open(os.path.join(folder, name))))
>             except (OSError, json.JSONDecodeError):
>                 print(f"::warning title=Record not read::{name} in the pack could not be read")
>         # Code stamps each raise with who raised it and an ID no raise on the issue has yet.
>         rec = stamp_record(build_record(role, stage, out, text, passed == "true", meta), earlier)
>         note = os.path.join(os.environ.get("PACK", ""), "no-baseline.txt")
>         if role == "reviewer" and s

**Agent:** Tests all fail for the right reason. Checking the logs-branch save step, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n '"save-record"' -A12 dokima/agent_roles.py | head -20
```

> 291:    if argv[1] == "save-record":
> 292-        print(save_record(os.environ["GITHUB_REPOSITORY"], argv[2], argv[3]))
> 293-        return 0
> 294-    if argv[1] == "pack":
> 295-        try:
> 296-            has_plan = pack(os.environ["GITHUB_REPOSITORY"], argv[2], argv[3], argv[4], argv[5])
> 297-        except RecordsUnreadable as e:
> 298-            sys.stderr.write(f"The pack has no history: {e}\n")
> 299-            return 1
> 300-        except TurnHeld as e:
> 301-            sys.stderr.write(f"The worker did not start: {e}\n")
> 302-            return 1
> 303-        return 0 if has_plan or argv[3] == "planner" else 3

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def save_record" -A15 dokima/*.py | grep -n "record.json\|open(" 
```

> 2:dokima/agent_records.py-108-    """Save OUT/record.json as one new file under logs/N/records/ on the logs branch and push it.
> 7:dokima/agent_records.py-113-    rec = json.load(open(os.path.join(out, "record.json")))
> 9:dokima/agent_records.py-115-    if os.path.exists(url) and open(url).read().strip():
> 10:dokima/agent_records.py-116-        rec["url"] = open(url).read().strip()

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote three criteria: every hiding step, the record card, and the saved record file.",
          "The planner wrote one failing test for each criterion."],
  "decided": ["Transcripts already hide the agent key, so only cards and records are fixed."],
  "open": ["The planner asks the owner whether fixing only cards and records is right."]
 },
 "verdict": "approve",
 "summary": "The plan covers the ask, and each test fails today because the agent key is not yet hidden.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Public logs scrub only Claude's token", "source": "https://github.com/dokima-dev/dokima/issues/706", "criterion": "706.1"},
  {"ask": "a key from another secret could leak into transcripts and cards", "source": "https://github.com/dokima-dev/dokima/issues/706", "criterion": "706.2"},
  {"ask": "Public logs scrub only Claude's token, so a key from another secret could leak", "source": "https://github.com/dokima-dev/dokima/issues/706", "criterion": "706.3"}
 ],
 "behaviors": [
  {"criterion": "706.1", "one_behavior": true, "why": "Each step hiding Claude's token also hides the agent key."},
  {"criterion": "706.2", "one_behavior": true, "why": "The record card shows the agent key as removed."},
  {"criterion": "706.3", "one_behavior": true, "why": "The saved record file shows the agent key as removed."}
 ],
 "edge_cases": [
  {"criterion": "706.1", "cut": [], "missing": []},
  {"criterion": "706.2", "cut": [], "missing": []},
  {"criterion": "706.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_agent_key_scrubbed.py::test_every_step_that_hides_claudes_token_hides_the_agent_key", "only_its_behavior": true, "why": "Fails today naming the four card steps that lack the agent key."},
  {"test": "tests/test_agent_key_scrubbed.py::test_the_runs_record_card_hides_the_agent_key", "only_its_behavior": true, "why": "Fails today: th
```

> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> rc=1

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote three criteria: every hiding step, the record card, and the saved record file./The planner wrote three criteria: hiding steps, the record card, the saved record./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 706 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#706](https://github.com/dokima-dev/dokima/issues/706) (hide every agent's key, not only Claude's). The hand-back is in `/tmp/dokima-out/review.json`, and both checks pass on it.

- **The ask is fully covered:** I matched each of the owner's asks to a criterion:
  - 706.1: every workflow step that hides Claude's token also hides the agent key.
  - 706.2: the record card shows the agent key as removed.
  - 706.3: the record file saved on the logs branch shows the agent key as removed.
- **Each criterion is one behavior with one test.** The record card test also runs once with no key set, to show the card keeps its text.
- **All three tests fail today for the right reason:**
  - 706.1 lists the four card steps that are not given the agent key.
  - 706.2 fails because the record step hides no secrets at all, not even Claude's.
  - 706.3 finds the key in the record file, which the logs branch saves unchanged.
- **One question still waits for the owner:** the planner asks whether to fix only cards and records, since transcripts already hide the agent key since [#719](https://github.com/dokima-dev/dokima/issues/719) (agent key in transcripts). The owner's words don't settle it, so I left it open, and the river stops there until they answer.
- **This needs the owner's approval later:** the work has to change the workflow file. Here the issue itself asks for it, but such a pull request always stops for the owner.

I raised no blockers and found no problems outside this issue.

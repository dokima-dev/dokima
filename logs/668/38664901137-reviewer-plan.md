# reviewer (plan) for #668

Run: https://github.com/dokima-dev/dokima/actions/runs/38664901137

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-worker.json
> 04-reviewer-pr.json
> 05-planner.json
> # Issue #668: Stories sharing a code file take turns to build
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 667 -->
> <!-- dokima-blocking: {"blocked_by": [667], "blocks": [559], "loop": []} -->
> A story's build waits while another story sharing a code file is building, until that one merges.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/701 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/701/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/667
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/665
> 
> 
> **User story:** Two stories never build th

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/04-reviewer-pr.json','in/05-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"; cat parent.json | head -50; cd /home/runner/work/dokima/dokima; git show --stat HEAD HEAD~1 | head -40
```

> in/04-reviewer-pr.json {
>  "role": "reviewer",
>  "stage": "pr",
>  "run_id": "38663754465",
>  "commit_before": "84d132d64b094ef72c110682ca817212c875b6fc",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 405597,
>   "turns": 19,
>   "cost_usd": 0.7807073999999999,
>   "tokens_in": 1005283,
>   "tokens_out": 7647
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/668/38663754465-reviewer-pr.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38663754465",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The worker made a story's build wait while a sibling sharing a code file builds.",
>     "The worker made a waiting story plan again once that sibling merges."
>    ],
>    "decided": [
>     "A story holds the turn once a worker ran or its pull request opened.",
>     "Asking for work on a waiting story builds nothing and names the other story."
>    ],
>    "open": [
>     "Nothing was left open."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Two stories can still build a shared file at once while the first story's worker is running.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "668.1 test too weak",
>     "text": "A story counts as building only once its worker finishes. While its worker runs, a sibling sharing its file starts building too. Add that case to the 668.1 test.",
>     "evidence": "`dokima/turns.py` `building()` sees only a record or open pull request; `agent.yml` writes both af

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD; cat dokima/turns.py; git show HEAD~1 -- dokima/agent_roles.py dokima/agent_autopilot.py; python -m pytest -q tests/test_build_turns.py tests/test_worker_pr.py 2>&1 | tail -30
```

> commit 43278041a6b1971b0ccb0adab4d8182dcdfaa763
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 01:17:47 2026 +0000
> 
>     planner for #668 (run 38664665504)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_build_turns.py b/tests/test_build_turns.py
> index 562e43f..9731cec 100644
> --- a/tests/test_build_turns.py
> +++ b/tests/test_build_turns.py
> @@ -35,6 +35,10 @@ P, A, B, C = 700, 701, 702, 703
>  PARENT = f"https://github.com/o/r/issues/{P}"
>  SHARED, OWN_A, OWN_B, DOC = "dokima/shared.py", "dokima/a_only.py", "dokima/b_only.py", "rules/flow.md"
>  ERROR = "HTTP 502: Server Error (sub_issues)"
> +# What the bot puts on a story when its worker starts on autopilot, and the run's live card while the agent works.
> +AUTOPILOT_START = "Autopilot: plan approved, starting work"
> +LIVE_WORKER = (agent.LIVE + "\n**Worker** · agent working since 2026-10-15 01:00 UTC\n\nThe agent is working; "
> +               "[watch it live](https://github.com/o/r/actions/runs/77) on GitHub.\n")
>  
>  # The fake GitHub of test_plan_links_recorded, with a tree of issues and pull requests on top. Each name it redefines
>  # is looked up when called, so its own routes below use these.
> @@ -235,6 +239,18 @@ class Tree:
>          s["prs"].append({"number": n + 100, "head": f"try/issue-{n}", "state": "OPEN"})
>          self.save()
>  
> +    def running(self, n, files):
> +        """#n's plan changes these fi

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "LIVE\b\|LIVE =" dokima/*.py | head; grep -rn "agent working since\|plan approved, starting work" dokima .github | head
```

> dokima/agent.py:29:    VERDICTS, FIXERS, OLD_FIELDS, PLAN_TEST_FAILS, MARK, LIVE, HANDBACK, name_of, records, LOGS_BRANCH,
> dokima/agent_next.py:281:    card = who in (BOT, f"{BOT}[bot]") and re.match(re.escape(LIVE) + r"[^*]*\*\*(Planner|Worker|Reviewer) ?\(?(\w*)", body)
> dokima/agent_next.py:316:from dokima.agent_records import LIVE, records, latest, approved, is_record, settled, owner_raises, for_planner, gate_failed
> dokima/agent_autopilot.py:372:                MARK in body or LIVE in body or body.strip() in (AUTOPILOT_LINE, AUTOPILOT_START_LINE)):
> dokima/agent_autopilot.py:423:        if (who in owners and command_of(said)) or (who in (BOT, f"{BOT}[bot]") and (LIVE in said or said in lines)):
> dokima/agent_autopilot.py:847:    MARK, LIVE, HANDBACK, records, latest, approved_plan, is_record, open_raises, settled, owner_raises, plan_links,
> dokima/board.py:200:            return bool(agent.command_of(words) or agent.autopilot_of(words) or agent.MARK in words or agent.LIVE in words
> dokima/agent_records.py:27:LIVE = "<!-- dokima-live -->"
> dokima/agent_records.py:359:    live = LIVE + ("\n<!-- **Reviewer (pr)** -->" if role == "reviewer" and stage == "pr" else "")
> dokima/agent_records.py:403:            if (c.get("user") or {}).get("login") in (BOT, f"{BOT}[bot]") and (MARK in body or LIVE in body):
> dokima/agent_records.py:348:    of it), setting up, agent working since the agent started, then checking the hand-back.
> dokima/agent_records.py:370:        line = f"{icon(repo, 'runn

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 340,380p dokima/agent_records.py; sed -n 270,300p dokima/agent_next.py
```

> """The record of a run someone cancelled: what it was and whether its agent had
>     started. Nothing it handed back is used, and the river starts nothing after it."""
>     return {"role": "cancelled", "attempt": role, "stage": stage or None, "agent_started": started, **meta,
>             "handback": {}, "check": {"passed": False, "problems": []}}
> 
> 
> def live_card(role, stage, state, ahead=None):
>     """The run's card while it is still running: queued (or waiting for the run `ahead`
>     of it), setting up, agent working since the agent started, then checking the hand-back.
> 
>     It carries its own marker and no JSON fold, so it never reads as a record; at the end of the run code edits this
>     same comment into the run's record. A hand-off's queued card is put up before its run exists, so it links none.
>     While the agent works the card is not edited, so it links the run's live page for detail."""
>     head = {"planner": "Planner", "reviewer": review_name(stage), "worker": "Worker",
>             "split": "Filing the split"}.get(role, "Command")
>     repo = os.environ.get("GITHUB_REPOSITORY", "")
>     run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
>     head = role_icon(repo, role, stage) + f"**{head}**"
>     # The card and card.yml still find a code review running by its old name, kept where the owner never reads it.
>     live = LIVE + ("\n<!-- **Reviewer (pr)** -->" if role == "reviewer" and stage == "pr" el

**Agent:** The new running-worker case fails today for the right reason, so I'm writing the review.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner added a case to the 668.1 test: a story whose worker is still running."],
  "decided": ["A story holds the turn from the moment its worker starts, before any pull request."],
  "open": ["Nothing was left open."]},
 "verdict": "approve",
 "summary": "The plan now proves a story waits while another story's worker is still running; ready to build.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A story's build waits until another open story sharing a code file has its pull request merged.", "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6175675553", "criterion": "668.1"},
  {"ask": "Planning and plan review of a story never wait on another story's files.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "668.2"},
  {"ask": "A shared markdown file never makes a story's build wait.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "668.3"},
  {"ask": "Each story merges to main on its own pull request, with no parent branch.", "source": "https://github.com/dokima-dev/dokima/issues/661", "criterion": "668.4"},
  {"ask": "A story whose plan adds files beyond those it was assigned is checked again for clashes before it builds.", "source": "https://github.com/dokima-dev/dokima/issues/661#issuecomment-6173871465", "criterion": "668.5"}
 ],
 "behaviors": [
  {"criterion": "668.1", "one_behavior": true, "why": "One wait on a shared code file, ended by a merge."},
  {"criterion": "668.2", "one_behavior": true, "why": "Planning steps never wait."},
  {"criterion": "668.3", "one_behavior": true, "why": "Markdown files never cause a wait."},
  {"criterion": "668.4", "one_behavior": true, "why": "Each story has its own pull request into main."},
  {"criterion": "668.5", "one_behavior": true, "why": "The final file list is checked again before building."}
 ],
 "edge_cases": [
  {"criterion": "668
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner added a case to the 668.1 test: a story whose worker is still running./The planner added a case to the 668.1 test: a worker still running./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 668 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#668](https://github.com/dokima-dev/dokima/issues/668) (stories sharing a code file take turns to build), and the review passed both checks.

- **What the planner did:** It answered the code reviewer's blocker. The build test now also covers a story whose worker is still running and has no pull request yet. In that case the other story must wait.
- **That case fails today, which is correct:** The other story's build still starts while the first story's worker runs. That is the gap the code reviewer found on [#701](https://github.com/dokima-dev/dokima/pull/701) (this issue's pull request). The other 5 tests pass on this branch, because the worker's code from the last round is already there.
- **Every ask has a criterion:** All five of your asks, from [#661](https://github.com/dokima-dev/dokima/issues/661) (the parent issue), map to criteria 668.1 to 668.5. Each criterion is one behavior with one test, and the size rule holds.
- **Nothing raised:** There were no open blockers to answer. I raised no new blockers or questions.

The review is in `/tmp/dokima-out/review.json`.

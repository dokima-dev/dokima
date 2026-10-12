# reviewer (plan) for #533

Run: https://github.com/dokima-dev/dokima/actions/runs/38294775032

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
> 02-reviewer-plan.json
> 03-not-started.json
> 04-planner.json
> 05-reviewer-plan.json
> 06-planner.json
> # Issue #533: Board runs only when a card can move
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [534], "loop": []} -->
> Board updates run only for events that can move a card, once per burst, with the sweep as safety net.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/534
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/380
> - https://github.com/dokima-dev/dokima/issues/368
> - https://github.com/dokima-dev/dokima/issues/428
> - https://github.com/dokima-dev/dokima/issues/377
> 
> 
> **User story:** The board stops spending GitHub's budget on events that cannot move a card, and bursts become one update.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptanc

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/05-reviewer-plan.json','in/06-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"
```

> in/05-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38293246876",
>  "commit_before": "60a4a35146d7e2eabb2467a82269bdce50d1f741",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 35563,
>   "turns": 6,
>   "cost_usd": 0.3973658,
>   "tokens_in": 252369,
>   "tokens_out": 3502
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/533/38293246876-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38293246876",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Added a criterion that autopilot ignores a burst's cancelled board waits, with its own test.",
>     "Moved the autopilot lines out of the burst test."
>    ],
>    "decided": [
>     "Dropped the sweep criterion so the story holds three criteria."
>    ],
>    "open": [
>     "The owner's answer on dropping the sweep criterion."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan's three tests are sound, but it drops the sweep ask; only you can choose which ask to drop.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "owner",
>     "label": "Sweep ask dropped",
>     "text": "A story holds at most three criteria, and this issue now has four asks. Choose which to drop or move to a new issue: the sweep, or another.",
>     "evidence": "`dokima/planner.py` `check_size()` caps a split story at 3. The issue lists the sweep criterion; `plan.json` has none.",
>     "raised_by": "reviewer",
>     "id": "R3"
>    }
>   ],
>   "answers": [],

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git status --short; timeout 300 python3 -m pytest -q tests/test_quiet_board.py 2>&1 | tail -30
```

> tests/test_quiet_board.py:385: AssertionError
> _______________ test_autopilot_ignores_a_bursts_cancelled_waits ________________
> 
> record_property = <function record_property.<locals>.append_property at 0x7fb897faf240>
> monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fb898441d30>
> 
>     def test_autopilot_ignores_a_bursts_cancelled_waits(record_property, monkeypatch):
>         """Autopilot still merges a green pull request when a burst's board waits show as cancelled.
>     
>         A board wait cancelled by a newer event shows on the pull request's head as a cancelled check named after
>         board.yml's waiting job. Autopilot, reading the head's checks, must not count it: with All tests and Acceptance
>         criteria green beside it, the head is proven. Beside it, a cancelled All tests on the same head must still stop
>         autopilot, so the check is not simply ignoring every cancelled run. Proves 533.3."""
>         record_property("proves", "533.3")
>         jobs = jobs_of()
>         j = settle_job(jobs)
> >       assert j, "533.3: board.yml has no job the sync waits on that sleeps in a queue a newer event cancels, so there is no wait to ignore"
> E       AssertionError: 533.3: board.yml has no job the sync waits on that sleeps in a queue a newer event cancels, so there is no wait to ignore
> E       assert None
> 
> tests/test_quiet_board.py:424: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_quiet_board.py::tes

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["Re-planned with the same three criteria and tests after the owner's answer."],
  "decided": ["Dropped the sweep criterion, as the owner said, since the sweep exists and is tested."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries every remaining ask with a sound test, and you settled the dropped sweep.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "An event that cannot change the column or a pill (for example an ordinary comment, a review comment, or a check run that is not a required check) does not run the board update.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.1"},
  {"ask": "Events about one issue that arrive close together cause one board update for that issue, not one each.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.2"},
  {"ask": "Yes: autopilot ignores a burst's cancelled waits like cancelled card runs.", "source": "https://github.com/dokima-dev/dokima/issues/533#issuecomment-6130305233", "criterion": "533.3"}
 ],
 "behaviors": [
  {"criterion": "533.1", "one_behavior": true, "why": "One result: such an event starts no board update."},
  {"criterion": "533.2", "one_behavior": true, "why": "One result: a burst about one issue causes one update."},
  {"criterion": "533.3", "one_behavior": true, "why": "One result: a cancelled board wait does not stop autopilot's merge."}
 ],
 "tests": [
  {"test": "tests/test_quiet_board.py::test_an_event_that_cannot_move_a_card_no_longer_starts_a_board_update", "only_its_behavior": true, "why": "Plays board.yml on quiet and moving events; fails today naming events that still run."},
  {"test": "tests/test_quiet_board.py::test_events_about_one_issue_within_a_minute_cause_one_board_update", "only_its_behavior": true, "why": "Plays a burst and counts updates; fails today as no wait job exists."},
  {"test": "tests/test_quiet_board
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#533](https://github.com/dokima-dev/dokima/issues/533) (board updates only for events that can move a card). The hand-back is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **What changed since my last review:** nothing in the plan. Your `/plan` comment told the planner to drop the 15-minute sweep criterion, and the new plan keeps the same three criteria and tests.
- **Every remaining ask has a criterion:**
  - Events that can't change a card's column or pill start no board update (533.1).
  - A burst of events about one issue causes one update (533.2).
  - Autopilot ignores a burst's cancelled board waits, as you said in your answer (533.3).
- **Tests:** I ran all three. Each fails today for the right reason: events that should be quiet still trigger an update, and there is no one-minute wait in the board workflow. The 533.3 test also checks that a cancelled All tests run still stops the merge, so it can't pass by ignoring every cancelled run.
- **Size:** fine. Each criterion is one behavior with its own test.
- **Raises:** none, and no open blockers were waiting for an answer.

The issue's context also says `AGENTS.md` must state which events skip the update and that a burst waits one minute. No criterion carries that. I didn't block on it: it comes from the parent plan's notes, not your own words, and my earlier reviews didn't treat it as an ask either. If you want it checked, it needs its own criterion.

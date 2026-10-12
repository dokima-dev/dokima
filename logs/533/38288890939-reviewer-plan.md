# reviewer (plan) for #533

Run: https://github.com/dokima-dev/dokima/actions/runs/38288890939

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat plan.json; cat open_blockers.json
```

> # Issue #533: Board runs only when a card can move
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [534], "loop": []} -->
> Board updates run only for events that can move a card, once per burst, with the sweep as safety net.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/533#issuecomment-6129470209) with `/plan`, or say `/review`
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
> - <img src="https://raw.githubusercontent.com/do

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head; wc -l tests/test_quiet_board.py; sed -n 1,80p tests/test_quiet_board.py; sed -n 330,600p tests/test_quiet_board.py
```

> commit b7f28988879e983cc23b227dec0723c9e0eaffe7
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:08:01 2026 +0000
> 
>     planner for #533 (run 38285898763)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_quiet_board.py | 468 ++++++++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 468 insertions(+)
> 468 tests/test_quiet_board.py
> """The board updates only when a card can move, once per burst (#533, from #380).
> 
> GitHub's GraphQL budget (5,000 calls an hour, shared by every Dokima workflow) ran out on 2026-10-09, and board.yml
> alone used about 56% of it: it recomputed an issue's cards on every comment, line note, new commit and finished
> check, though none of those can move a card. These tests hold the fix to the owner's words on #380:
> 
> - `python3 -m dokima.board queue`, the step that already names each event's board queue from its payload alone,
>   also writes `run=true` or `run=false` to GITHUB_OUTPUT: false exactly for an event that cannot change a card's
>   column or pill, true for every other one (and for any event it cannot read). board.yml's sync job runs only on
>   true, so a skipped event spends no GraphQL call at all.
> - A review or line note reaches board.yml only as reviews.yml's run completing, which carries no summary, so the
>   step reads it from the run's event and name: reviews.yml names its run from the review (`run-name:`), and a run
>   named any

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_quiet_board.py 2>&1 | grep -E "Error|assert|passed|failed" | head -30; sed -n 80,330p tests/test_quiet_board.py
```

> >       assert not wrong_run, f"533.1: these events cannot change a card's column or pill, yet board.yml still updates the board: {wrong_run}"
> E       AssertionError: 533.1: these events cannot change a card's column or pill, yet board.yml still updates the board: ["a stranger's comment on the issue", "the code owner's comment that is no command", "the code owner's comment naming a command later in it", 'a comment on the pull request', 'a bot comment that is no record, run card or Autopilot line', 'a line note', 'a review that only comments', 'an Approve with no summary', 'an Approve with a summary that is no command', 'new commits on the pull request', 'the Acceptance criteria checks passing', 'the Acceptance criteria checks failing', 'the label bug added', 'the label bug removed', 'the card redrawn above the marker', 'the first card drawn on a fresh ask', 'the title edited']
> E       assert not ["a stranger's comment on the issue", "the code owner's comment that is no command", "the code owner's comment naming ...t", 'a comment on the pull request', 'a bot comment that is no record, run card or Autopilot line', 'a line note', ...]
> tests/test_quiet_board.py:369: AssertionError
> >       assert j, "533.2: board.yml has no job the sync waits on that sleeps in a queue a newer event cancels, so every event is its own update"
> E       AssertionError: 533.2: board.yml has no job the sync waits on that sleeps in a queue a newer event cancels, so every event is its own update
> E       as

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Wrote three criteria from the parent issue's words, each with one new test.",
          "Raised one question: should autopilot ignore a cancelled board wait?"],
  "decided": ["Planned that autopilot ignores a cancelled board wait, as it ignores replaced card runs."],
  "open": ["The owner's answer on cancelled board waits."]},
 "verdict": "block",
 "summary": "The plan covers the three asks, but its burst test also checks autopilot, which no criterion carries.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion",
   "text": "The issue asks to check that a cancelled board wait does not stop autopilot, and no criterion carries it. The 533.2 test checks it instead. Smallest fix: give it its own criterion and move those last lines into its own test.",
   "evidence": "The issue's Context: 'may show as a cancelled check and stop autopilot ... check that'. `tests/test_quiet_board.py:437-442` calls `agent.unproven`."},
  {"kind": "blocker", "to": "planner", "label": "533.2 test too wide",
   "text": "The 533.2 test checks two behaviors: one update per burst, and autopilot ignoring a cancelled wait. A failure in either fails 533.2. Smallest fix: drop the autopilot lines from it.",
   "evidence": "`tests/test_quiet_board.py::test_events_about_one_issue_within_a_minute_cause_one_board_update`, lines 437-442."}
 ],
 "answers": [],
 "asks": [
  {"ask": "An event that cannot change the column or a pill (for example an ordinary comment, a review comment, or a check run that is not a required check) does not run the board update.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.1"},
  {"ask": "Events about one issue that arrive close together cause one board update for that issue, not one each.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.2"},
  {"ask": "The 15-minute sweep stays as the safety
```

> Exit code 1
> raise 1's text holds 41 words, over its cap of 30: cut 11, keep the facts

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r['raises'][0]['text']="The issue asks to check that a cancelled board wait does not stop autopilot; no criterion carries it. Fix: give it its own criterion and test."
r['raises'][1]['text']="The 533.2 test also checks autopilot ignoring a cancelled wait, so it proves two behaviors. Fix: move those lines into the new criterion's test."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 533 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for [#533](https://github.com/dokima-dev/dokima/issues/533) (board updates only when a card can move). It goes back to the planner. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**What's fine:** the three criteria follow the parent issue's words. I ran all three new tests and each fails today because the feature is missing:
- **533.1:** comments, line notes, new commits, finished checks and other labels still start a board update.
- **533.2:** the board doesn't yet wait one minute and merge a burst of events into one update.
- **533.3:** a stranger's comment still starts an update, so there's no skipped event yet for the sweep to fix.

**Why I blocked (two blockers for the planner):**
- **No criterion:** the issue says to check that a cancelled board wait doesn't stop autopilot, and no criterion covers that.
- **One test checks two things:** the 533.2 test also checks that autopilot ignores a cancelled wait (`tests/test_quiet_board.py:437-442`). The fix is to give that check its own criterion and test.

**Your call:** I left the planner's question unanswered. It asks whether autopilot should ignore cancelled board waits, the way it ignores replaced card runs. The plan assumes yes. Your words in the issue ("check that") lean that way, but saying yes changes how autopilot treats failed checks, so only you can decide. Answer with `/plan` and your words, or say `/review` to go on with the planner's reading.

I didn't list the issue's line that `AGENTS.md` must describe the change as a missing ask. It came from the parent's plan, not your own words, and it's a doc update rather than something a test can check.

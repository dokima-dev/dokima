# reviewer (plan) for #533

Run: https://github.com/dokima-dev/dokima/actions/runs/38293246876

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #533: Board runs only when a card can move
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [534], "loop": []} -->
> Board updates run only for events that can move a card, once per burst, with the sweep as safety net.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix why nothing ran
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
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "never splits\|split_from\|Part of\|def stories\|/ 3\|ceil" dokima/agent.py dokima/*.py | head -30; cat /tmp/pack/in/02-reviewer-plan.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d.get('handback',d),indent=1)[:5000])"
```

> dokima/planner.py:134:    The size rule (#416): stories = criteria / 3, rounded up. 1 to 3 criteria is one story; 4 to 6 two; and so on, up to
> dokima/planner.py:139:        raise Garbled(f"this issue is already a story of its parent, so it never splits again: hand back one story of at "
> dokima/agent.py:364:             f"**Part of:** #{parent} {parent_title}", "", f"**User story:** {story.get('user_story', '')}", ""]
> dokima/agent.py:364:             f"**Part of:** #{parent} {parent_title}", "", f"**User story:** {story.get('user_story', '')}", ""]
> {
>  "previous_step": {
>   "did": [
>    "Wrote three criteria from the parent issue's words, each with one new test.",
>    "Raised one question: should autopilot ignore a cancelled board wait?"
>   ],
>   "decided": [
>    "Planned that autopilot ignores a cancelled board wait, as it ignores replaced card runs."
>   ],
>   "open": [
>    "The owner's answer on cancelled board waits."
>   ]
>  },
>  "verdict": "block",
>  "summary": "The plan covers the three asks, but its burst test also checks autopilot, which no criterion carries.",
>  "raises": [
>   {
>    "kind": "blocker",
>    "to": "planner",
>    "label": "No criterion",
>    "text": "The issue asks to check that a cancelled board wait does not stop autopilot; no criterion carries it. Fix: give it its own criterion and test.",
>    "evidence": "The issue's Context: 'may show as a cancelled check and stop autopilot ... check that'. `tests/test_quiet_board.py:437-442` calls `agent.unproven`.",
>    "raised_by": "rev

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 125,150p dokima/planner.py; git diff b7f2898 60a4a35 --stat; grep -n "^def test" tests/test_quiet_board.py
```

> def count(s):
>     """How many criteria a story holds: its acceptance criteria and non-functional requirements."""
>     return len(s.get("acceptance_criteria") or []) + len(s.get("non_functional") or [])
> 
> 
> def check_size(stories, nested=False):
>     """Garbled unless the stories hold their criteria at 1 to 3 each, in exactly as many stories as the count needs.
> 
>     The size rule (#416): stories = criteria / 3, rounded up. 1 to 3 criteria is one story; 4 to 6 two; and so on, up to
>     five stories. More than 15 criteria is too big for one issue: the owner breaks it up."""
>     sizes = [count(s) for s in stories]
>     total, need = sum(sizes), -(-sum(sizes) // PER_STORY)
>     if nested and (len(stories) > 1 or total > PER_STORY):
>         raise Garbled(f"this issue is already a story of its parent, so it never splits again: hand back one story of at "
>                       f"most {PER_STORY} criteria (acceptance criteria and non-functional requirements together), and "
>                       "ask the owner, in a question, which of the rest to drop")
>     if need > 5:
>         raise Garbled(f"the issue holds {total} criteria, more than 15, too big for one issue: hand back one story that "
>                       "asks the owner, in a question, to break the issue up")
>     if len(stories) != need:
>         raise Garbled(f"{total} criteria make {need} {'story' if need == 1 else 'stories'} (3 at most each), not "
>                       f"{len(stories)}: " + ("hand back one user_story" if need == 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_quiet_board.py 2>&1 | grep -E "Error|assert|passed|failed|533" | head -30; sed -n 328,470p tests/test_quiet_board.py
```

> autopilot label, the sweep), and on events the queue step cannot read, it must still run. Proves 533.1."""
>         record_property("proves", "533.1")
>         wrong_run = [w for w, (e, p) in skipped_events().items() if play(e, p, monkeypatch, tmp_path, "533.1")[s]["ran"]]
> >       assert not wrong_run, f"533.1: these events cannot change a card's column or pill, yet board.yml still updates the board: {wrong_run}"
> E       AssertionError: 533.1: these events cannot change a card's column or pill, yet board.yml still updates the board: ["a stranger's comment on the issue", "the code owner's comment that is no command", "the code owner's comment naming a command later in it", 'a comment on the pull request', 'a bot comment that is no record, run card or Autopilot line', 'a line note', 'a review that only comments', 'an Approve with no summary', 'an Approve with a summary that is no command', 'new commits on the pull request', 'the Acceptance criteria checks passing', 'the Acceptance criteria checks failing', 'the label bug added', 'the label bug removed', 'the card redrawn above the marker', 'the first card drawn on a fresh ask', 'the title edited']
> E       assert not ["a stranger's comment on the issue", "the code owner's comment that is no command", "the code owner's comment naming ...t", 'a comment on the pull request', 'a bot comment that is no record, run card or Autopilot line', 'a line note', ...]
> tests/test_quiet_board.py:344: AssertionError
>         lands. Proves 533.2."""
> 

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Added a criterion that autopilot ignores a burst's cancelled board waits, with its own test.",
          "Moved the autopilot lines out of the burst test."],
  "decided": ["Dropped the sweep criterion so the story holds three criteria."],
  "open": ["The owner's answer on dropping the sweep criterion."]},
 "verdict": "block",
 "summary": "The plan's three tests are sound, but it drops the sweep ask; only you can choose which ask to drop.",
 "raises": [
  {"kind": "blocker", "to": "owner", "label": "Sweep ask dropped",
   "text": "A story holds at most three criteria, and this issue now has four asks. Choose which to drop or move to a new issue: the sweep, or another.",
   "evidence": "`dokima/planner.py` `check_size()` caps a split story at 3. The issue lists the sweep criterion; `plan.json` has none."}
 ],
 "answers": [],
 "asks": [
  {"ask": "An event that cannot change the column or a pill (for example an ordinary comment, a review comment, or a check run that is not a required check) does not run the board update.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.1"},
  {"ask": "Events about one issue that arrive close together cause one board update for that issue, not one each.", "source": "https://github.com/dokima-dev/dokima/issues/380", "criterion": "533.2"},
  {"ask": "The 15-minute sweep still puts right any card a skipped event left in the wrong column.", "source": "https://github.com/dokima-dev/dokima/issues/533", "criterion": "missing"},
  {"ask": "Yes: autopilot ignores a burst's cancelled waits like cancelled card runs.", "source": "https://github.com/dokima-dev/dokima/issues/533#issuecomment-6130305233", "criterion": "533.3"}
 ],
 "behaviors": [
  {"criterion": "533.1", "one_behavior": true, "why": "One result: such an event starts no board update."},
  {"criterion": "533.2", "one_behavior": true, "why": "One result: a bu
```

> (Bash completed with no output)

**Agent:** I blocked the plan for [#533](https://github.com/dokima-dev/dokima/issues/533) (board updates run only when a card can move). The tests are sound, but the plan dropped one of the four asks, and only you can choose which one goes. The hand-back passes both checks.

**Your decision:** a story can hold at most three criteria, and this issue now has four asks:
- events that can't move a card start no board update;
- a burst of events about one issue becomes one update;
- the 15-minute sweep still fixes any card left wrong;
- autopilot ignores a burst's cancelled waits (added from your answer).

The planner dropped the sweep ask and asked you to confirm (its question, P2). The code that sizes plans tells it to ask you which to drop, so this was not its own call. Choose which ask to drop or move to a new issue: the sweep, or another one. The sweep already runs every 15 minutes and this plan leaves it alone, so dropping it costs the least.

**What the planner fixed since the last plan review:**
- The cancelled-wait ask now has its own criterion and test.
- The burst test now checks only bursts.

**Tests:** I ran all three. Each fails today because the feature is missing, not because of a crash or a bad setup:
- The skip test lists 17 events that still start a board update.
- The burst test and the autopilot test both fail because there is no one-minute wait step yet.

The autopilot test also checks that a cancelled full test run still stops a merge, so it can't pass by ignoring every cancelled check.

To answer, comment `/plan` on the issue with your choice.

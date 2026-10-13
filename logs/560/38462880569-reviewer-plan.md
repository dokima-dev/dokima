# reviewer (plan) for #560

Run: https://github.com/dokima-dev/dokima/actions/runs/38462880569

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
> # Issue #560: Agent records live as files, comments are just the readable view, and my words are kept exactly as I wrote them
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 475 -->
> <!-- dokima-blocking: {"blocked_by": [475], "blocks": [548], "loop": []} -->
> Agent records move from comments to files, and cards and the board redraw only when a stage changes.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/560#issuecomment-6154484159) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/475
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/548
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/487
> - https://github.com/dokima-dev/dokima/issues/541
> 
> 
> <img src

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -50; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k not in('handback','plan')},indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; grep -rn "15\b" dokima/plan*.py dokima/split*.py 2>/dev/null | head; grep -rn "issue carries\|MAX_CRITERIA\|max_criteria" dokima | head
```

> {"number": null}dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38462497299",
>  "commit_before": "a9701dcd1c18343e8c700132dc6cc7d5d53232bd",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 117527,
>   "turns": 12,
>   "cost_usd": 0.7847976,
>   "tokens_in": 658263,
>   "tokens_out": 10629
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/560/38462497299-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38462497299",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6154484159"
> }
> dokima/planner.py:34:DOCSTRING_CAP = 15  # words in the first line of a docstring the planner adds
> dokima/planner.py:135:    five stories. More than 15 criteria is too big for one issue: the owner breaks it up."""
> dokima/planner.py:143:        raise Garbled(f"the issue holds {total} criteria, more than 15, too big for one issue: hand back one story that "

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 120,170p dokima/planner.py; grep -n "too big\|Too big" prompts/*.md dokima/roles/* 2>/dev/null | head
```

> "or a comment on either")
> 
> 
> PER_STORY = 3
> 
> 
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
>                       f"{len(stories)}:

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "S<s>\|\"S\"\|f\"S{" dokima/agent.py dokima/review*.py 2>/dev/null | head
```

> 1436:    """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each story of a split."""
> 1440:        return [f"S{s}.{k}" for s, st in enumerate(stories, 1) if isinstance(st, dict) for k in range(1, count(st) + 1)]

**Agent:** Now I'll write the review.

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner splits the issue into five stories of three criteria each."],
  "decided": ["The plan drops four asks to stay within fifteen criteria.", "The plan keeps the card in the issue's text, not a comment."],
  "open": ["Two questions wait for the owner: what to drop, and where the card lives."]
 },
 "verdict": "block",
 "summary": "The plan drops seven of the owner's asks but names only four, and narrows two others.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Asks dropped", "text": "Seven asks have no criterion, but question P1 names four. Name all seven in P1, or ask the owner to break the issue up, as the size rule says.", "evidence": "Missing besides P1's four: split stories stay in the planner's record; latest comment wins; content tests kept, trigger tests deleted. `dokima/planner.py:142`."},
  {"kind": "blocker", "to": "planner", "label": "S4.2 narrowed", "text": "The owner counts an owner command starting a stage as a stage change; S4.2 leaves it out. Add it to S4.2's text.", "evidence": "Comment 6133834391: \"or an owner command starts a stage\"; S4.2 names only a stage start, finish or stop."},
  {"kind": "blocker", "to": "planner", "label": "S4.1 two behaviors", "text": "S4.1 bundles two behaviors: built with no GitHub reads, and saved in one write. Split it, or drop one and say which in P1.", "evidence": "S4.1 text: \"with no reads from GitHub, and saved in one write\"."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Each agent's JSON hand-back is saved as its own file on a protected branch (one file per record, never edited)", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S1.1"},
  {"ask": "Starting packs build every earlier record from record files with no API call", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S1.2"},
  {"ask":
```

> Exit code 1
> raise 1's evidence holds 21 words, over its cap of 20: cut 1, keep the facts

`6. Bash`
```
sed -i 's/Missing besides P1.s four: split stories stay in the planner.s record; latest comment wins; content tests kept, trigger tests deleted. `dokima\/planner.py:142`./Beyond P1: split stories stay in the planner record; latest comment wins; trigger tests deleted. `dokima\/planner.py:142`./' /tmp/dokima-out/review.json && grep -c "Beyond P1" /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 560 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> 1

**Agent:** I blocked the plan for issue [#560](https://github.com/dokima-dev/dokima/issues/560) (agent records as files, cards redrawn only at stage changes). The review is in `/tmp/dokima-out/review.json` and passes both checks.

The planner split the issue into five stories of three criteria each. That makes 15, the most one issue may hold. To fit, the plan leaves out some of the owner's asks.

**Three blockers, all sent back to the planner:**
- **Asks dropped:** seven of the owner's asks have no criterion, but the planner's question P1 names only four. The three it doesn't name are:
  - split stories stay in the planner's record;
  - the owner's latest comment wins;
  - tests for the old triggers and the sweep are deleted, not ported.

  The fix is to name all seven in P1, or to ask the owner to break the issue up. That second option is what the size rule's own error message says (`dokima/planner.py:142`).
- **S4.2 is narrower than the ask:** the owner counts "an owner command starts a stage" as a stage change, and S4.2 leaves that out.
- **S4.1 holds two behaviors:** "no reads from GitHub" and "saved in one write" need to be separate criteria, or one has to go.

The planner's two questions still wait for the owner. The issue is on autopilot, so I could have answered them myself, but only with the owner's own words, and nothing they wrote settles either one:
- **P1:** drop the left-out asks, or file them later?
- **P2:** the owner wrote "The card stays a comment on the issue", but the card actually lives in the issue's text. The plan assumes it stays in the text. That goes against the owner's literal words, so only they can decide.

The split has no tests to run yet; each story's planner writes its own tests and edge cases.

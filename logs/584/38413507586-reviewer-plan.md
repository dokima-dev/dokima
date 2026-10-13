# reviewer (plan) for #584

Run: https://github.com/dokima-dev/dokima/actions/runs/38413507586

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
> # Issue #584: Approved card demos become fixtures the card code must reproduce exactly
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A command draws card demos with the real card code, and approved ones become fixtures that tests hold exactly.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/545
> - https://github.com/dokima-dev/dokima/issues/517
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:**
> 
> <!-- dokima-folded -->
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> In Reza's words (2026-10-13): "you show me demos and then I confirm them, they turn into fixtures. And the tests should exactly produce what I like."
> 
> Why: on 2026-10-12/13 card changes only reached the layout Reza wanted once every demo was rendered by the real card code (not hand-edited text), checked by code against the unchanged output, and approved by Reza in the GitHub app. The approved card for #545 is saved on branch fixture/card-557 (see #545).
> 
> Done when
> - One command renders any issue's card with the real card c

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -50; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback' and k!='plan'},indent=1)[:2000])"; cd /home/runner/work/dokima/dokima; ls tests/fixtures 2>/dev/null; git branch -a | grep fixture; grep -n "^def \(draw\|render\|gather\|github_links\|their_links\)" dokima/card.py
```

> {"number": null}dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38413056740",
>  "commit_before": "507df8606bd0c0d74b549dfcb7a9bc4434b357c8",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 130499,
>   "turns": 16,
>   "cost_usd": 0.9583448,
>   "tokens_in": 925048,
>   "tokens_out": 12081
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/584/38413056740-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38413056740",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6147783363"
> }
>   remotes/origin/fixture/card-557
> 116:def their_links(repo, number, sources, plans=None):
> 190:def github_links(repo, number, cache):
> 504:def render(repo, issue, found, page="issue"):
> 668:def gather(repo, number, pr_number):
> 928:def draw(repo, number, pr_number, plans=None, noted=None, cache=None, changed_only=False):

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git ls-tree -r --name-only origin/fixture/card-557 | grep -i fixture; git show origin/fixture/card-557:tests/fixtures/cards/557.inputs.json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(list(d.keys()), list(d.get('found',{}).keys()))"
```

> tests/fixtures/cards/557.card.md
> tests/fixtures/cards/557.inputs.json
> ['edge_case_sources', 'found', 'issue', 'repo'] ['blocking', 'check_runs', 'children', 'items', 'linked', 'owners', 'pr', 'recs', 'reviews', 'sources', 'tests', 'worker']

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner split the issue into two stories: drawing a card demo, then freezing approved demos into fixtures."],
  "decided": ["The demo command leaves the card code untouched and swaps functions for one run only.", "The approved card for #545 stays with #545, since today's card code does not reproduce it yet."],
  "open": []},
 "verdict": "approve",
 "summary": "The split carries every ask of the owner in six one-behavior criteria across two stories, in the right order.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "One command renders any issue's card with the real card code", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S1.1"},
  {"ask": "shows the lines that differ from the unchanged card", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S1.1"},
  {"ask": "with named card functions swapped for a run only", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S1.2"},
  {"ask": "writes nothing to the repo or to GitHub", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S1.3"},
  {"ask": "One command freezes an approved render: the card markdown", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S2.1"},
  {"ask": "the issue, records, checks and links it came from, saved under tests/fixtures/cards/", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S2.2"},
  {"ask": "A fixture test renders a card from its frozen inputs, offline, and fails on any byte that differs from the approved card, naming the first differing line.", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "S2.3"}
 ],
 "behaviors": [
  {"criterion": "S1.1", "one_behavior": true, "why": "One result: the lines that differ after a swap."},
  {"criterion": "S1.2", "one_behavior": true, "why": "One result: card code unchanged a
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step decided line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

`5. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']['did']=["The planner split the issue into two stories: card demos, then fixtures from approved demos."]
d['previous_step']['decided'][1]="The approved card for #545 stays with #545; today's card code cannot reproduce it."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 584 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for issue [#584](https://github.com/dokima-dev/dokima/issues/584) (approved card demos become fixtures). The verdict is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **The split:** two stories with three criteria each. That is six in all, which code counts as two stories, so the size is fine. The second story waits on the first, which matches the order of the work.
- **What the owner asked for:** each of the owner's asks has its own criterion. Story 1 covers drawing any issue's card with the real card code, showing the lines that differ, swapping card functions for one run only, and writing nothing to the repo or GitHub. Story 2 covers saving the card markdown, saving the inputs it came from under `tests/fixtures/cards/`, and a test that fails offline on any differing byte and names the first differing line.
- **Each criterion:** each one does exactly one thing. The edge cases are normal ones, such as no function swapped, a mistyped function name, or GitHub refusing a read. None is missing and none needed cutting.
- **Checked against the repo:** the card functions the plan names (`render`, `gather`, `github_links`, `their_links`) exist in `dokima/card.py`. The plan's fixture layout matches the existing approved card on branch `fixture/card-557`, which has `557.card.md` and `557.inputs.json`. The plan leaves that card with [#545](https://github.com/dokima-dev/dokima/issues/545) (related card change) because today's card code can't reproduce it yet. I accepted that and did not re-check the mismatch myself.
- **Tests:** there are none to run yet. A split plan has no tests; each story gets its own tests when it is planned.

I raised no blockers and left no questions open.

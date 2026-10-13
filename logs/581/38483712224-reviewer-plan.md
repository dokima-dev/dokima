# reviewer (plan) for #581

Run: https://github.com/dokima-dev/dokima/actions/runs/38483712224

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 88
> drwxr-xr-x  3 runner runner  4096 Oct 13 23:21 .
> drwxrwxrwt 18 root   root    4096 Oct 13 23:21 ..
> drwxr-xr-x  2 runner runner  4096 Oct 13 23:21 in
> -rw-r--r--  1 runner runner 11213 Oct 13 23:21 issue.md
> -rw-r--r--  1 runner runner     2 Oct 13 23:21 open_blockers.json
> -rw-r--r--  1 runner runner 47644 Oct 13 23:21 open_issues.json
> -rw-r--r--  1 runner runner    16 Oct 13 23:21 parent.json
> -rw-r--r--  1 runner runner  5770 Oct 13 23:21 plan.json
> 
> in:
> total 32
> drwxr-xr-x 2 runner runner 4096 Oct 13 23:21 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 23:21 ..
> -rw-r--r-- 1 runner runner 6204 Oct 13 23:21 01-planner.json
> -rw-r--r-- 1 runner runner 4254 Oct 13 23:21 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6484 Oct 13 23:21 03-planner.json
> # Issue #581: Split agent.py and AGENTS.md so issues stop queueing on the same file
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [580, 582], "blocks": [599, 600], "loop": []} -->
> The two files most issues touch become smaller files, so parallel work stops queueing on them.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/580
> - https://github.com/dokima-dev/dokima/issues/582
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; cat parent.json; cd /home/runner/work/dokima/dokima; wc -l dokima/agent.py AGENTS.md; git log --oneline -1; grep -n "AGENTS" .github/workflows/agent.yml | head
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38482863663",
>  "commit_before": "61faa9edeb3dd8e4b351252c742cfbe198fb7ce7",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 87894,
>   "turns": 5,
>   "cost_usd": 0.447305,
>   "tokens_in": 210637,
>   "tokens_out": 6536
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/581/38482863663-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38482863663",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner proposes a split into two stories: the agent code, then the rules file."
>    ],
>    "decided": [
>     "The rules file story waits for the agent code story.",
>     "The test count for the rules story is taken after the agent code story lands."
>    ],
>    "open": [
>     "Should the rules file become an index of topic files the word check reads?",
>     "Should one helper carry every module's GitHub calls, or only the agent code's?"
>    ]
>   },
>   "verdict": "block",
>   "summary": "The split is sound, but the last story bundles two results and can miss tests the first story drops.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "S2.2 two results",
>     "text": "S2.2 bundles two results, tests pass and count unchanged, and counts after story 1, missing tests it drops. Fix: split it; count against main before story 1.",
>     "evidence": "Story 2 context: \"The count of tests is taken after story 1 lands.\"",
>     "ra

`3. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'))
for i in (d if isinstance(d,list) else d.get('issues',[])):
  n=i.get('number')
  if n in (381,599,600,580,582,39): print(n,i.get('title'))
"; cd /home/runner/work/dokima/dokima; grep -n "def agents_text" -A12 dokima/agent.py; python3 -m dokima.agent check 2>&1 | head -3
```

> 600 The owner can still merge after main moved past the tested code: main's rule does not demand an up-to-date branch.
> 381 Issues run in parallel only when they change different functions; otherwise the later one waits
> 39 Agent-neutral: AGENTS.md and one adapter per agent
> 2508:def agents_text():
> 2509-    """AGENTS.md as the runtime has it, from main; empty when there is none."""
> 2510-    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AGENTS.md")
> 2511-    try:
> 2512-        return open(path).read()
> 2513-    except OSError:
> 2514-        return ""
> 2515-
> 2516-
> 2517-def said_there(words, source, items, body, owners, number, parent=None):
> 2518-    """True when the words appear word for word where the source says: the issue's own text, a code owner's comment on
> 2519-    this issue, or AGENTS.md; given the parent (parent_words), also the parent's own text or a code owner's comment on
> 2520-    it. Anything else, a comment by anyone else (the bot included) or one not found, is False."""
> the check needs plan.json and the issue number: agent check review|work FILE PLAN N

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the test promise in two: all tests pass, and no test from before the first split is lost.",
          "The planner wrote the owner's three answers into the plan."],
  "decided": ["The rules file becomes a short index of topic files the word check reads.",
              "Only the agent code's calls to GitHub go through the one helper."],
  "open": []},
 "verdict": "block",
 "summary": "The plan carries every ask, but the rules story's first promise bundles two results and must split.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "S2.1 two results",
   "text": "S2.1 bundles two results: the index of topic files, and the word check reading them. A split could pass while quotes from topic files fail. Fix: make them two criteria; seven criteria need three stories.",
   "evidence": "S2.1: \"becomes a short index linking one file per topic, and the word check reads them all\"; `agents_text()` at `dokima/agent.py:2508` reads only `AGENTS.md`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "agent.py is split into modules by job (autopilot and merging, records, Next lines, checks, GitHub helpers, roles), a pure move with no behavior change", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "S1.1"},
  {"ask": "`agent` keeps re-exporting every name so its 146 importers keep working", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "S1.2"},
  {"ask": "GitHub calls go through one helper module that tests patch in one place", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "S1.3"},
  {"ask": "Only the agent code's GitHub calls. Other modules stay as they are.", "source": "https://github.com/dokima-dev/dokima/issues/581#issuecomment-6157254121", "criterion": "S1.3"},
  {"ask": "AGENTS.md is split by topic.", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion
```

> Exit code 1
> raise 1's text holds 35 words, over its cap of 30: cut 5, keep the facts
> raise 1's evidence holds 23 words, over its cap of 20: cut 3, keep the facts
> previous_step did line 1 holds 21 words, over its cap of 15: cut 6, keep the facts

`5. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json;d=json.load(open('review.json'))
d['previous_step']['did'][0]="The planner split the test promise in two: all tests pass, and none is lost."
r=d['raises'][0]
r['text']="S2.1 bundles two results: the topic index, and the word check reading it. Quotes from topic files could fail unseen. Fix: two criteria, so three stories."
r['evidence']="S2.1 says \"index linking one file per topic, and the word check reads them all\"; `dokima/agent.py:2508` reads only `AGENTS.md`."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 581 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#581](https://github.com/dokima-dev/dokima/issues/581) (split the big agent file and the rules file), sending one blocker back to the planner. The review is in `/tmp/dokima-out/review.json`, and both checks pass.

- **Fixed since the last round:** the planner split the old S2.2 into two promises: all tests pass (S2.2), and no test that ran on main before the first split is lost (S2.3). Your three answers are also in the plan: the rules file becomes an index of topic files, only the agent code's GitHub calls go through the one helper, and story 2 may change the copy step in `agent.yml`.
- **New blocker, S2.1:** this promise now holds two results. One is that the rules file becomes an index linking topic files. The other is that the word check reads all of them. Today the word check reads only `AGENTS.md` (`dokima/agent.py:2508`), so a build could split the file while quotes from topic files quietly stop being found. The fix is two separate promises. That gives seven in all, which by the size rule means three stories instead of two.
- **Asks:** every ask in the issue and in your comment matches a promise, and none is missing.

The plan is a split, so no tests are written yet. Each story writes its own when it is planned.

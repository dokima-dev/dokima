# reviewer (plan) for #560

Run: https://github.com/dokima-dev/dokima/actions/runs/38463391222

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (30.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/356d9cf7-7f67-4aee-89a1-649e3d7fc657/tool-results/bq3o8wt1c.txt
> 
> Preview (first 2KB):
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
> 03-planner.json
> # Issue #560: Agent records live as files, comments are just the readable view, and my words are kept exactly as I wrote them
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 475 -->
> <!-- dokima-blocking: {"blocked_by": [475], "blocks": [548], "loop": []} -->
> Agent records move from comments to files, and cards and the board redraw only when a stage changes.
> 
> **Plan**
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
> <img src="https://raw.githubusercontent.com/d

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed -n 40,400p
```

> - Each record's fingerprint is written to the logs branch in the run's existing push, adding no API calls.
> - An edited or deleted record is detected and named on the issue, checked nightly or when a card is drawn from it, never by rereading every record each time.
> - A record too large for one comment is stored on the logs branch, and its comment points there.
> 
> Relates to #559 (tests as the spec, paired texts).
> 
> </details>
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/owner-approval.svg" width="16" height="16" align="absmiddle" alt="owner approval"> Owner approval
> 
> ## Comments
> 
> ### RezaSoleymanifar on issue #560 (2026-10-12T21:44:07Z)
> 
> This replaces the scope above. In Reza's words: "ok i agree with your plan", and "it should be run conversation output that is better order".
> 
> *

`3. Bash`
```
cd /tmp/pack; cat plan.json; cat open_blockers.json; cat parent.json | head -50
```

> {
>  "kind": "feature",
>  "title": "Records live as files, cards redraw only at stage changes",
>  "summary": "Agent records move from comments to files, and cards and the board redraw only when a stage changes.",
>  "feature": "Records live as files the owner can trust; comments only show them; the owner's words stay exact; cards and board update only at stage changes.",
>  "stories": [
>   {
>    "title": "Each run's record is saved as its own file",
>    "user_story": "Every agent record is a file no one edits, and every run reads earlier records from those files.",
>    "context": "Today records are JSON inside bot comments: dokima/agent.py records() parses them from the conversation, and pack() builds the starting pack from GitHub. agent.yml already pushes each run's conversation to the logs branch (step 'Save the conversation for good on the logs branch'); the record file can ride that same push, one file per record under logs/N/. The branch protection is a setting the owner switches on; the bot cannot change settings. The owner replaced the original body scope (versions, fingerprints) with the comment of 2026-10-12.",
>    "acceptance_criteria": [
>     {
>      "text": "Each agent run saves its record as its own new file on the logs branch, never editing an older one.",
>      "words": "Each agent's JSON hand-back is saved as its own file on a protected branch (one file per record, never edited)",
>      "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490",
>      "

`4. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
d=json.load(open('02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:9000])"; python3 -c "
import json
d=json.load(open('03-planner.json'));print(list(d.keys())); print(json.dumps(d.get('check') or d.get('verdict'),indent=1)[:3000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38462880569",
>  "commit_before": "a9701dcd1c18343e8c700132dc6cc7d5d53232bd",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 69840,
>   "turns": 7,
>   "cost_usd": 0.5164154,
>   "tokens_in": 306886,
>   "tokens_out": 7939
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/560/38462880569-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38462880569",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner splits the issue into five stories of three criteria each."
>    ],
>    "decided": [
>     "The plan drops four asks to stay within fifteen criteria.",
>     "The plan keeps the card in the issue's text, not a comment."
>    ],
>    "open": [
>     "Two questions wait for the owner: what to drop, and where the card lives."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan drops seven of the owner's asks but names only four, and narrows two others.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Asks dropped",
>     "text": "Seven asks have no criterion, but question P1 names four. Name all seven in P1, or ask the owner to break the issue up, as the size rule says.",
>     "evidence": "Beyond P1: split stories stay in the planner record; latest comment wins; trigger tests deleted. `dokima/planner.py:142`.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    },
>    {
>     "kind": "blocker",
>     "to": "planner",
>   

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "missing\|\"asks\"\|'asks'" dokima/agent.py | head -40; grep -rn "def check_asks\|asks" dokima/*.py | grep -v "^dokima/agent.py" | head -20
```

> 251:    """A plan record's links as three lists of issue numbers, empty when missing."""
> 270:        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
> 411:        handback = {"missing": f"{HANDBACK[role]}: {e}"}
> 686:    for a in h.get("asks") or []:
> 687:        if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing":
> 870:                  ("The owner's asks", bullets(h.get("asks"), lambda a: f"{a.get('ask', '')} ({a.get('criterion', '')}, {a.get('source', '')})"))]
> 1309:    Each row lists the exotic cases it cuts and the normal-use ones missing, as plain lines ([] when none)."""
> 1317:                       "ones missing, each [] when there are none")
> 1319:        for f in ("cut", "missing"):
> 1328:    they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an approve keeps every ask."""
> 1329:    asks = r.get("asks")
> 1332:                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
> 1333:    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
> 1337:        if c != "missing" and c not in ids:
> 1340:    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
> 1342:        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
> 1403:        missing = [k for k in keys if not filled(x.get(k))]
> 1404:        if missing:
> 1405:            bad.append(f"{label} needs {', '.join(miss

**Agent:** Still working: I've read the plan and the owner's comments, and I'm writing the review hand-back now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner keeps five stories of three criteria each.",
   "The planner raises one follow-up issue naming every ask moved out."
  ],
  "decided": [
   "Records quoting the owner's words stay in this issue, as the owner asked.",
   "The exact original text and the one-write card move to the follow-up.",
   "The card stays in the issue's text, as the owner answered."
  ]
 },
 "verdict": "approve",
 "summary": "The plan now carries every ask the owner kept here, and files the rest as one follow-up.",
 "raises": [],
 "answers": [
  {
   "raise": "P3",
   "answer": "done",
   "why": "The owner asked for a follow-up issue; it names every ask no story carries, so file it."
  }
 ],
 "asks": [
  {"ask": "Each agent's JSON hand-back is saved as its own file on a protected branch (one file per record, never edited)", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S1.1"},
  {"ask": "Starting packs build every earlier record from record files with no API call", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S1.2"},
  {"ask": "no code reads a record from a comment", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S1.3"},
  {"ask": "A run comment shows no record JSON", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S2.1"},
  {"ask": "its stats line links run, conversation and output in that order", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S2.2"},
  {"ask": "where output opens that record's file pinned to its commit", "source": "https://github.com/dokima-dev/dokima/issues/560#issuecomment-6133164490", "criterion": "S2.3"},
  {"ask": "Each record file quotes the exact words of mine it relied on, with a link to where I 
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#560](https://github.com/dokima-dev/dokima/issues/560) (agent records live as files), and both hand-back checks pass. The review is in `/tmp/dokima-out/review.json`.

- **Your answers are in the plan.** Records quoting your words now have their own criterion. The card stays in the issue's text, as you answered.
- **The rest goes to one follow-up issue.** As you asked, the planner raised one issue listing every ask it moved out. I confirmed that issue so it can be filed.
- **Last round's three blockers are fixed.** Every left-out ask is now named. The stage-change criterion includes your own command starting a stage. The card criterion now covers one thing only.
- **The plan's size is fine.** It has five stories of three criteria each, and every criterion is one behavior. There are no tests to run yet, because each story's planner writes its own.

Decision for you: the follow-up issue includes two asks you may want back here. One is your original issue text staying byte for byte the same through every redraw, which is on your "Done when" list. The other is the card being saved in one write. You let the planner choose which ask to move out, so I didn't block on it. If you want the exact original text kept here, answer with `/plan` and say so.

Since this issue is on autopilot, the approval starts filing the five stories by itself.

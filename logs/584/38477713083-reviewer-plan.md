# reviewer (plan) for #584

Run: https://github.com/dokima-dev/dokima/actions/runs/38477713083

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> <persisted-output>
> Output too large (35.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/1b7a7524-aee6-4c64-ae8e-4fa2a96a18d1/tool-results/bmvnepp5e.txt
> 
> Preview (first 2KB):
> # Issue #584: Our own tool previews every visual and freezes approved fixtures
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 585 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> An internal tool previews any visual Dokima posts, and approved previews become fixtures a test holds exactly.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> **Stories:**
> 
> - https://github.com/dokima-dev/dokima/issues/585 · Plan
> - https://github.com/dokima-dev/dokima/issues/586 · Backlog
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/545
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-dev/dokima/issues/611
> - https://github.com/dokima-dev/dokima/issues/613
> - https://github.com/dokima-dev/dokima/issues/585
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance 

`2. Bash`
```
cat /tmp/pack/issue.md
```

> # Issue #584: Our own tool previews every visual and freezes approved fixtures
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 585 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> An internal tool previews any visual Dokima posts, and approved previews become fixtures a test holds exactly.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> **Stories:**
> 
> - https://github.com/dokima-dev/dokima/issues/585 · Plan
> - https://github.com/dokima-dev/dokima/issues/586 · Backlog
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/545
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-dev/dokima/issues/611
> - https://github.com/dokima-dev/dokima/issues/613
> - https://github.com/dokima-dev/dokima/issues/585
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
> <!-- dokima-title -->**Original title:** Approved card d

`3. Bash`
```
ls /tmp/pack /tmp/pack/in; cat /tmp/pack/open_blockers.json
```

> /tmp/pack:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> /tmp/pack/in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-split.json
> 04-planner.json
> 05-reviewer-plan.json
> 06-planner.json
> 07-reviewer-plan.json
> 08-planner.json
> []

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('plan.json'));print(json.dumps(d,indent=1))"; python3 -c "
import json;d=json.load(open('in/08-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:3000])"
```

> {
>  "kind": "feature",
>  "title": "Our own tool previews every visual and freezes approved fixtures",
>  "summary": "An internal tool previews any visual Dokima posts, and approved previews become fixtures a test holds exactly.",
>  "feature": "Our visual preview tool. Stories: (1) draw. (2) preview on the gallery. (3) compare, nightly checks. (4) freeze fixtures. (5) test them.",
>  "stories": [
>   {
>    "title": "One command draws Dokima's posts from any branch",
>    "user_story": "We see exactly what Dokima would post on a real issue, drawn by any branch's code.",
>    "context": "Owner widened the scope on 2026-10-13: every visual, not only the card. Internal tool, outside the `dokima/` package (for example `tools/visuals.py`). The top card is `card.render(repo, issue, found)` with `found` from `card.gather`; run comments are `agent.render(rec, ...)` (`dokima/agent.py:772`); autopilot comments are `agent.autopilot_comment` and the `AUTOPILOT_*` lines. Take the code from a branch with a git worktree of that branch, so this checkout is untouched. `card.gallery()` draws made-up situations only; this draws a real issue. The owner's newest words ask for any branch's code, which replaces the older patch file of swapped functions.",
>    "acceptance_criteria": [
>     {
>      "text": "The command draws a real issue's top card with the drawing code of a chosen branch.",
>      "words": "using the real drawing code from any branch and the real records of a real issue",
>      "source": "https://github.

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/07-reviewer-plan.json'));print(json.dumps(d.get('handback'),indent=1)[:5000]); print(d.keys())"; python3 -c "
import json;d=json.load(open('in/08-planner.json'));print(json.dumps(d.get('check') or d.get('verdict'),indent=1)[:2000]); print(d.keys())"; cat parent.json | head -50
```

> {
>  "previous_step": {
>   "did": [
>    "The planner re-planned the widened ask as five stories: draw, compare, preview, freeze, test."
>   ],
>   "decided": [
>    "The tool draws from a chosen branch instead of a patch file.",
>    "Today's card code changes until the approved 557 card matches."
>   ],
>   "open": [
>    "Whether approving this split can file new stories at all.",
>    "Which issue gets the fixture record comment."
>   ]
>  },
>  "verdict": "approve",
>  "summary": "The plan carries every ask of the widened scope; three questions wait for you, first whether the split can file.",
>  "raises": [
>   {
>    "kind": "issue",
>    "label": "Split never refiled",
>    "text": "An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.",
>    "evidence": "`dokima/agent.py:381` `file_split()` returns the old split record; #591 is closed, code unchanged.",
>    "raised_by": "reviewer",
>    "id": "R2"
>   }
>  ],
>  "answers": [],
>  "asks": [
>   {
>    "ask": "the tool previews any visual change, not just the card. That covers the top card, run comments and autopilot comments.",
>    "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768",
>    "criterion": "S1.2"
>   },
>   {
>    "ask": "one command draws what Dokima would post, using the real drawing code from any branch and the real records of a real issue",
>    "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768",
>    "criterion": "S1.1"
>   },
>   {
>    "ask": "autopilot comme

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -1 71e8ad3 --stat | head; grep -n "def file_split" -A40 dokima/agent.py | head -60; git branch -a | grep -i fixture; ls tools 2>/dev/null; ls .github/workflows
```

> 71e8ad3 A re-approved split files its new stories (#618)
>  dokima/agent.py     | 25 +++++++++++++++++++------
>  tests/test_agent.py | 36 ++++++++++++++++++++++++++++++++++++
>  2 files changed, 55 insertions(+), 6 deletions(-)
> 376:def file_split(repo, parent, recs, labels=()):
> 377-    """File the stories of the newest approved split as sub-issues of the parent, in order, with their blocked-by links,
> 378-    each created with the given labels.
> 379-
> 380-    Returns the record of what was filed. Filing twice files nothing new: a split record newer than the plan is returned
> 381-    instead. A re-plan approved after an earlier split was filed files only its new stories; a story already filed under
> 382-    the same title is kept as it is, marked kept."""
> 383-    splits = [i for i, r in enumerate(recs) if r.get("role") == "split" and r.get("check", {}).get("passed")]
> 384-    plans = [i for i, r in enumerate(recs) if r.get("role") == "planner" and r.get("check", {}).get("passed")]
> 385-    if splits and (not plans or splits[-1] > plans[-1]):
> 386-        return recs[splits[-1]]
> 387-    plan = latest(recs, "planner")["handback"]
> 388-    earlier = {f["title"]: f for i in splits for f in recs[i]["handback"].get("stories", [])}
> 389-    title = json.loads(gh("issue", "view", str(parent), "-R", repo, "--json", "title"))["title"]
> 390-    filed = []
> 391-    for i, st in enumerate(plan["stories"], 1):
> 392-        if st["title"] in earlier:
> 393-            old = earlier[st["title"]]
> 394-            

**Agent:** Checked the plan and the repo: the split-filing fix has landed (#618), and the owner's answers are in the plan. One criterion contradicts another, so I'm writing the review now.

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner re-planned the widened ask as five stories: draw, preview, compare, freeze, test."],
  "decided": ["The tool draws from a chosen branch instead of a patch file.", "Previews that touch real GitHub run nightly; pull request tests fake GitHub.", "Today's card code changes until the approved 557 card matches."],
  "open": []
 },
 "verdict": "block",
 "summary": "The plan carries every ask, but one rule bans the nightly job another rule needs.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "S3.3 clashes with S3.2",
   "text": "S3.3 says the tool is never a workflow, but S3.2 needs a nightly workflow to run its GitHub checks. Fix: drop 'workflow', keeping the owner's words.",
   "evidence": "S3.3 text: 'never a Dokima command, workflow or shipped feature'; owner's words: 'This tool is for us, never a product feature.'"
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "S1.1 missing edge case",
   "text": "S1.1 covers a missing branch but not a mistyped or unreadable issue. Add the case: it stops with GitHub's reason.",
   "evidence": "S1.1 edge_cases list only 'The branch does not exist'; S1 reads a real issue from GitHub."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "the tool previews any visual change, not just the card. That covers the top card, run comments and autopilot comments.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.2"},
  {"ask": "one command draws what Dokima would post, using the real drawing code from any branch and the real records of a real issue", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.1"},
  {"ask": "autopilot comments", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.3"},
  {"ask": "it posts that rendering as one comment on an 
```

> Exit code 1
> raise 1's evidence holds 21 words, over its cap of 20: cut 1, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['evidence']="S3.3 says 'never a Dokima command, workflow or shipped feature'; the owner said 'This tool is for us, never a product feature.'"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 584 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> raise 1's evidence holds 22 words, over its cap of 20: cut 2, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['evidence']="S3.3: 'never a Dokima command, workflow or shipped feature'. Owner: 'This tool is for us, never a product feature.'"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 584 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for #584 (our internal visual preview tool) and sent it back to the planner. Both checks on the hand-back pass. The review is at `/tmp/dokima-out/review.json`.

The plan covers everything you asked for: all 15 of your asks map to a criterion, the split has the right size, and each criterion is a single behavior. It also has your answers in it: #585 and #586 stay closed and new stories get filed, and today's card code must reproduce the approved 557 card exactly. The code that files a re-approved split as new stories is now on main ([#618](https://github.com/dokima-dev/dokima/pull/618), re-approved split files its new stories), so approving this plan will actually file the new stories.

The two blockers are both small:
- **One criterion contradicts another (story 3).** S3.3 says the tool is "never a Dokima command, workflow or shipped feature", but S3.2 needs a nightly workflow to run the checks that touch real GitHub. You never said "workflow"; you said "This tool is for us, never a product feature." The fix is to drop "workflow" and use your words.
- **A missing everyday failure (story 1).** S1.1 says what happens when the branch doesn't exist, but not when the issue number is wrong or GitHub refuses the read. The fix is to add that case: the command stops and gives GitHub's reason.

The plan raises no questions for you this round. It went with drawing from any branch instead of the earlier patch file of swapped functions. You never answered that question directly, but your newest description of the render step says "from any branch", so I let it stand.

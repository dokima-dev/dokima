# reviewer (plan) for #584

Run: https://github.com/dokima-dev/dokima/actions/runs/38478445723

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (45.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/1703fdfa-5a7b-4f79-b234-eded8f8e2b50/tool-results/bq7xbt6r0.txt
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
> 03-split.json
> 04-planner.json
> 05-reviewer-plan.json
> 06-planner.json
> 07-reviewer-plan.json
> 08-planner.json
> 09-reviewer-plan.json
> 10-planner.json
> 11-reviewer-plan.json
> 12-planner.json
> 13-split.json
> # Issue #584: Our own tool previews every visual and freezes approved fixtures
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 585 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> An internal tool previews any visual Dokima posts, and approved previews become fixtures a test holds exactly.
> 
> **Work**
> 
> **Stories:**
> 
> - https://github.com/dokima-dev/dokima/issues/624 · Backlog
> - https://github.com/dokima-dev/dokima/issues/625 · Backlog
> - https://github.com/dokima-dev/dokima/issues/626 · Backlog
> - https://github.com/dokima-dev/dokima/issues/627 · Backlog
> - https://github.com/dokima-dev/dokima/issues/628 · Backlog
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/545
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-d

`2. Bash`
```
cd /tmp/pack; sed -n 50,400p issue.md
```

> - A fixture test renders a card from its frozen inputs, offline, and fails on any byte that differs from the approved card, naming the first differing line.
> 
> 
> </details>
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/owner-approval.svg" width="16" height="16" align="absmiddle" alt="owner approval"> Owner approval
> 
> ## Comments
> 
> ### RezaSoleymanifar on issue #584 (2026-10-13T14:23:50Z)
> 
> /autopilot start
> 
> ### dokima-runtime on issue #584 (2026-10-13T14:24:16Z)
> 
> Autopilot: switched on, starting plan
> 
> ### dokima-runtime on issue #584 (2026-10-13T14:24:18Z)
> 
> Autopilot is on for #584. Planning started for #584, which wait on nothing open.
> 
> 
> ### dokima-runtime on issue #584 (2026-10-13T14:24:33Z)
> 
> <!-- dokima-record -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main

`3. Bash`
```
cd /tmp/pack; sed -n 400,700p issue.md; echo ====; cat open_blockers.json; cat parent.json | head -50
```

> (full record: in/08-planner.json)
> 
> </details>
> 
> **Next:** The reviewer starts now.
> 
> <!-- dokima-stats -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/stats.svg" width="16" height="16" align="absmiddle" alt="stats"> Opus 5.5 · 1.2 min · 7 turns · 373K tokens in, 7K out · $0.60 at API prices · [conversation](https://github.com/dokima-dev/dokima/blob/logs/logs/584/38477438038-planner.md) · [run](https://github.com/dokima-dev/dokima/actions/runs/38477438038)
> 
> 
> ### dokima-runtime on issue #584 (2026-10-13T22:23:46Z)
> 
> Autopilot is on for #584, #585, #586. No stage was started.
> 
> 
> ### dokima-runtime on issue #584 (2026-10-13T22:25:35Z)
> 
> <!-- dokima-record -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/plan-review.svg" width="16" height="16" align="absmiddle" alt="plan review"> Plan review blocked the plan with 2 blockers.
> 
> **Raised:**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocker.svg" width="16" height="16" align="absmiddle" alt="blocker"> **S3.3 clashes with S3.2:** S3.3 says the tool is never a workflow, but S3.2 needs a nightly workflow to run its GitHub checks. Fix: drop 'workflow', keeping the owner's words. · for the planner
>   - Evidence: S3.3: 'never a Dokima command, workflow or shipped feature'. Owner: 'This tool is

`4. Bash`
```
cd /tmp/pack; python3 - <<'E'
import json
p=json.load(open('plan.json'))
print(json.dumps(p,indent=1)[:20000])
E

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
cd /tmp/pack/in; python3 - <<'E'
import json
a=json.load(open('10-planner.json')); b=json.load(open('12-planner.json'))
print(a.keys())
def plan(r):
    for k in ('plan','handback','output'):
        if k in r: return r[k]
    return r
import difflib
x=json.dumps(plan(a),indent=1,sort_keys=True).splitlines(); y=json.dumps(plan(b),indent=1,sort_keys=True).splitlines()
print("\n".join(difflib.unified_diff(x,y,lineterm='')))
s=json.load(open('13-split.json')); print(json.dumps(s,indent=1)[:3000])
r=json.load(open('11-reviewer-plan.json')); print(json.dumps(r,indent=1)[:6000])
E
```

> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> --- 
> +++ 
> @@ -1,16 +1,5 @@
>  {
> - "answers": [
> -  {
> -   "answer": "done",
> -   "raise": "R3",
> -   "why": "The requirement now says never a Dokima command or shipped feature, so the nightly job fits."
> -  },
> -  {
> -   "answer": "done",
> -   "raise": "R4",
> -   "why": "Criterion one now covers a mistyped or unreadable issue: it stops with GitHub's reason."
> -  }
> - ],
> + "answers": [],
>   "feature": "Our visual preview tool. Stories: (1) draw. (2) preview on the gallery. (3) compare, nightly checks. (4) freeze fixtures. (5) test them.",
>   "kind": "feature",
>   "links": {
> {
>  "role": "split",
>  "stage": null,
>  "handback": {
>   "stories": [
>    {
>     "story": 1,
>     "issue": 624,
>     "title": "One command draws Dokima's posts from any branch",
>     "id": 5838721322,
>     "blocked_by": []
>    },
>    {
>     "story": 2,
>     "issue": 625,
>     "title": "The command previews its drawing on the gallery repo",
>     "id": 5838721721,
>     "blocked_by": [
>      1
>     ]
>    },
>    {
>     "story": 3,
>     "issue": 626,
>     "title": "The command shows what changed, and real checks run nightly",
>     "id": 5838722216,
>     "blocked_by": [
>      1,
>      2
>     ]
>    },
>    {
>     "story": 4,
>     "issue": 627,
>     "title": "Approving a preview freezes it as a fixture",
>     "id": 5838722759,
>     "blocked_by": [
>      2
>     ]
>    },
>    {
>     "story": 5,
>     "issue": 628,
>     "title": "A test holds the dr

**Agent:** I'm checking the newest plan. It matches the plan that was already approved and filed as stories #624–628. Next I'll check what approving it again does to the filed split.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def file_split" -A60 dokima/agent.py | head -90
```

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
> 394-            filed.append({"story": i, "issue": old["issue"], "title": st["title"], "id": old["id"],
> 395-                          "blocked_by": [d + 1 for d in st.get("depends_on", [])], "kept": True})
> 396-            continue
> 397-    

`7. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;h=json.load(open('11-reviewer-plan.json'))['handback'];print(json.dumps({k:h[k] for k in ('edge_cases','tests','size')},indent=1))"
```

> {
>  "edge_cases": [
>   {
>    "criterion": "S1.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S4.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S4.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S4.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S5.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S5.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S5.3",
>    "cut": [],
>    "missing": []
>   }
>  ],
>  "tests": [],
>  "size": "ok"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack/in; python3 - <<'E'
import json
h=json.load(open('11-reviewer-plan.json'))['handback']
asks=h['asks']+[
 {"ask":"the nightly GitHub check may be a workflow (the tool itself is still never a product feature)","source":"https://github.com/dokima-dev/dokima/issues/584","criterion":"S3.2"},
 {"ask":"add the mistyped or unreadable issue case","source":"https://github.com/dokima-dev/dokima/issues/584","criterion":"S1.1"}]
r={"previous_step":{"did":["The planner handed back the same five stories already approved and filed."],
 "decided":["The tool's rule bans only a Dokima command or shipped feature.","A mistyped or unreadable issue stops the command with GitHub's reason."],"open":[]},
 "verdict":"approve",
 "summary":"The plan matches the approved one: both fixes the owner asked for are in, and every ask has a criterion.",
 "raises":[],"answers":[],"asks":asks,"behaviors":h['behaviors'],"edge_cases":h['edge_cases'],"tests":[],"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
E
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 584 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan. Both checks on my review pass, and it's saved as `review.json` in `/tmp/dokima-out`.

- **Same plan as before:** the new plan matches, word for word, the one already approved and filed as five stories. It differs only in that it leaves out the planner's answers to the old blockers. The stories are [#624](https://github.com/dokima-dev/dokima/issues/624) (draws Dokima's posts from any branch) through [#628](https://github.com/dokima-dev/dokima/issues/628) (a test holds the drawing code to every fixture).
- **Your 22:30 `/plan` comment is done:**
  - The nightly check may be a workflow. The rule now only says the tool is never a Dokima command or shipped feature.
  - A mistyped or unreadable issue stops the command with GitHub's reason.
- **No duplicate stories:** approving it again files nothing new. When a story's title matches one already filed, the code keeps the existing story.
- **Every ask has a criterion:** that covers your comments plus your two newest points, and each criterion is one behavior. There are no tests yet, because each story writes its own when it is planned.

For those two newest points I linked the issue, not the exact comment, because the comment's own link wasn't in what I was given.

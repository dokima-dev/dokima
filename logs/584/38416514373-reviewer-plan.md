# reviewer (plan) for #584

Run: https://github.com/dokima-dev/dokima/actions/runs/38416514373

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
> 03-split.json
> 04-planner.json
> # Issue #584: Approved card demos become fixtures the card code must match
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 585 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> An internal script draws card demos for review, and approved ones become answer keys a test holds exactly.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148191448) with `/plan`, or say `/review`
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
> - https://github.com/dokima-dev/dokima/issues/585
> - https://github.com/dokima-dev/dokima/issues/586
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:

`2. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def file_split" -A40 dokima/agent.py | head -70; cat /tmp/pack/parent.json | head -50; python3 -c "
import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:3000])"
```

> 374:def file_split(repo, parent, recs, labels=()):
> 375-    """File the stories of the newest approved split as sub-issues of the parent, in order, with their blocked-by links,
> 376-    each created with the given labels.
> 377-
> 378-    Returns the record of what was filed. Filing twice files nothing new: the newest split record is returned instead."""
> 379-    done = latest(recs, "split", passed=True)
> 380-    if done:
> 381-        return done
> 382-    plan = latest(recs, "planner")["handback"]
> 383-    title = json.loads(gh("issue", "view", str(parent), "-R", repo, "--json", "title"))["title"]
> 384-    filed = []
> 385-    for i, st in enumerate(plan["stories"], 1):
> 386-        extra = [x for label in labels for x in ("--label", label)]
> 387-        url = gh("issue", "create", "-R", repo, "--title", st["title"], "--body", story_body(parent, i, st, title), *extra).strip()
> 388-        number = int(url.rstrip("/").split("/")[-1])
> 389-        node = json.loads(gh("api", f"repos/{repo}/issues/{number}"))["id"]
> 390-        gh("api", "-X", "POST", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={node}")
> 391-        filed.append({"story": i, "issue": number, "title": st["title"], "id": node,
> 392-                      "blocked_by": [d + 1 for d in st.get("depends_on", [])]})
> 393-    by_story = {f["story"]: f for f in filed}
> 394-    for f in filed:
> 395-        for d in f["blocked_by"]:
> 396-            try:
> 397-                gh("api", "-X", "POST", f"repos/{repo}/issues/{f['issu

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner re-planned the rescoped issue as four stories: draw and compare, post to the sandbox, save keys, test keys."],
  "decided": ["The script lives outside the product and is never a Dokima command.",
              "The answer key test assumes the card code changes until the issue 557 key matches."],
  "open": ["Whether the old stories are closed as replaced.",
           "Whether the card code should change to match the first key."]},
 "verdict": "approve",
 "summary": "The plan carries every rescoped ask; two questions and the refiling gap wait for you.",
 "raises": [
  {"kind": "question", "to": "owner", "label": "Split will not file",
   "text": "Approving this split files nothing new, even after closing the old stories. Should the old stories be re-planned instead? I assume you decide.",
   "evidence": "`dokima/agent.py:379` `file_split()` returns the old split record of #585 and #586 and files nothing."}
 ],
 "answers": [
  {"raise": "P3", "answer": "done", "why": "Confirmed: filing returns the first split's record, so a rescoped split is never filed."}
 ],
 "asks": [
  {"ask": "this is an internal tool for us, never shipped with Dokima and never a Dokima command or feature", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S2.2"},
  {"ask": "renders an issue's card with the real card code, with only the card functions named in a patch file swapped for that run", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S1.1"},
  {"ask": "shows which lines differ from today's card", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S1.2"},
  {"ask": "posts the render to the merge-sandbox repo for review", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S2.1"},
  {"ask"
```

> Exit code 1
> raise 1's text holds 23 words, over its cap of 20: cut 3, keep the facts
> previous_step did line 1 holds 20 words, over its cap of 15: cut 5, keep the facts

`4. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="Approving this split files nothing new, even with the old stories closed. Re-plan the old stories instead? You decide."
d['previous_step']['did'][0]="The planner re-planned the rescoped issue as four stories."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 584 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> 0

**Agent:** I approved the plan, but it still stops for you: three questions are waiting. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**What the plan does:** it turns your rescoped ask into four stories:
1. A script draws a card demo and shows the changed lines.
2. The script posts the demo to the sandbox repo for review.
3. The script saves an approved demo as an answer key.
4. A test redraws each answer key and fails on any change.

Every ask in your rescope comment maps to one criterion, and each criterion is one behavior. Nothing is missing.

**Waiting for you:**
- **Approving won't file the new stories.** I checked the code: once a split has been filed, a later approved split files nothing. Closing [#585](https://github.com/dokima-dev/dokima/issues/585) (draw a card demo) and [#586](https://github.com/dokima-dev/dokima/issues/586) (freeze demos into fixtures) won't change that, so these four stories would never be filed. I asked whether to re-plan those two old stories instead. This is also why the planner's question about closing them as replaced doesn't fix things on its own.
- **The planner asked whether to close #585 and #586 as replaced.** I left this one for you.
- **The planner asked whether the card code should change so that the issue 557 answer key matches.** Today's card code doesn't redraw that approved card. Changing the card code changes how Dokima works, so I left this one for you as well.

I also confirmed the planner's report that a split is never filed a second time; it is ready to be filed as its own issue.

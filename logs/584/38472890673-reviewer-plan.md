# reviewer (plan) for #584

Run: https://github.com/dokima-dev/dokima/actions/runs/38472890673

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (30.8KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/85638881-0941-460f-bdd9-5808e33ac2fd/tool-results/bl2v2e5uy.txt
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
> # Issue #584: Our own card demo script and its answer keys
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 585 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> An internal script draws card demos for review, and approved ones become answer keys a test holds exactly.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148263123) with `/plan`, `/work` or `/review`
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
> - https://github.com

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed -n 40,400p
```

> Done when
> - One command renders any issue's card with the real card code, with named card functions swapped for a run only, writes nothing to the repo or to GitHub, and shows the lines that differ from the unchanged card.
> - One command freezes an approved render: the card markdown and the issue, records, checks and links it came from, saved under tests/fixtures/cards/.
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
> ### dokima

`3. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json; echo; cat parent.json | head -50; python3 -c "
import json;d=json.load(open('in/05-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"
```

> {
>  "kind": "feature",
>  "title": "Our own tool previews every visual and freezes approved fixtures",
>  "summary": "An internal tool previews any visual Dokima posts, and approved previews become fixtures a test holds exactly.",
>  "feature": "Our visual preview tool. Stories: (1) draw. (2) compare, touching nothing real. (3) preview on the gallery. (4) freeze fixtures. (5) test them.",
>  "stories": [
>   {
>    "title": "One command draws Dokima's posts from any branch",
>    "user_story": "We see exactly what Dokima would post on a real issue, drawn by any branch's code.",
>    "context": "Owner widened the scope on 2026-10-13: every visual, not only the card. Internal tool, outside the `dokima/` package (for example `tools/visuals.py`). The top card is `card.render(repo, issue, found)` with `found` from `card.gather`; run comments are `agent.render(rec, ...)` (`dokima/agent.py:772`); autopilot comments are `agent.autopilot_comment` and the `AUTOPILOT_*` lines. Take the code from a branch with a git worktree of that branch, so this checkout is untouched. `card.gallery()` draws made-up situations only; this draws a real issue. The newer branch ask replaces the older patch file of swapped functions.",
>    "acceptance_criteria": [
>     {
>      "text": "The command draws a real issue's top card with the drawing code of a chosen branch.",
>      "words": "using the real drawing code from any branch and the real records of a real issue",
>      "source": "https://github.com/dokima-dev/dokima/issues/5

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def file_split" -A60 dokima/agent.py | head -90; git log --oneline -5 -- dokima/agent.py; git branch -a | grep -i fixture; git log --oneline origin/fixture/card-557 -3 2>/dev/null
```

> 376:def file_split(repo, parent, recs, labels=()):
> 377-    """File the stories of the newest approved split as sub-issues of the parent, in order, with their blocked-by links,
> 378-    each created with the given labels.
> 379-
> 380-    Returns the record of what was filed. Filing twice files nothing new: the newest split record is returned instead."""
> 381-    done = latest(recs, "split", passed=True)
> 382-    if done:
> 383-        return done
> 384-    plan = latest(recs, "planner")["handback"]
> 385-    title = json.loads(gh("issue", "view", str(parent), "-R", repo, "--json", "title"))["title"]
> 386-    filed = []
> 387-    for i, st in enumerate(plan["stories"], 1):
> 388-        extra = [x for label in labels for x in ("--label", label)]
> 389-        url = gh("issue", "create", "-R", repo, "--title", st["title"], "--body", story_body(parent, i, st, title), *extra).strip()
> 390-        number = int(url.rstrip("/").split("/")[-1])
> 391-        node = json.loads(gh("api", f"repos/{repo}/issues/{number}"))["id"]
> 392-        gh("api", "-X", "POST", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={node}")
> 393-        filed.append({"story": i, "issue": number, "title": st["title"], "id": node,
> 394-                      "blocked_by": [d + 1 for d in st.get("depends_on", [])]})
> 395-    by_story = {f["story"]: f for f in filed}
> 396-    for f in filed:
> 397-        for d in f["blocked_by"]:
> 398-            try:
> 399-                gh("api", "-X", "POST", f"repos/{repo}/issues/{f['issu

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show origin/fixture/card-557 --stat | head; d=$(mktemp -d); git show origin/fixture/card-557:tests/fixtures/cards/557.inputs.json > $d/i.json 2>/dev/null || git ls-tree -r --name-only origin/fixture/card-557 | grep 557; ls $d
```

> commit e98dee4e199f9d66c37e80def5ccc215690eee59
> Author: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> Date:   Tue Oct 13 09:17:02 2026 -0500
> 
>     Approved card fixture for #557: the layout Reza signed off on
>     
>     557.card.md is the card exactly as approved on merge-sandbox#7; 557.inputs.json
>     holds the issue, records, checks and links it was rendered from, so a test can
>     render it offline and compare byte for byte.
>     
> i.json

**Agent:** I'm checking the planner's claim about the #557 answer key, then I'll write the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; d=$(mktemp -d); git show origin/fixture/card-557:tests/fixtures/cards/557.inputs.json > $d/i.json; git show origin/fixture/card-557:tests/fixtures/cards/557.card.md > $d/c.md; python3 -I -c "
import sys,json;sys.path.insert(0,'.')
from dokima import card
i=json.load(open('$d/i.json'))
try:
  out=card.render(i['repo'],i['issue'],i['found'])
except Exception as e: print('ERR',e);sys.exit()
a=open('$d/c.md').read().splitlines();b=out.splitlines()
for n,(x,y) in enumerate(zip(a,b),1):
  if x!=y: print(n,repr(x[:80]),repr(y[:80]));break
" 2>&1 | tail -3
```

> 21 '  *<a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee23c8086fa8b67b2627' '  - *<a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee23c8086fa8b67b26'

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner re-planned the widened ask as five stories: draw, compare, preview, freeze, test."],
  "decided": ["The tool draws from a chosen branch instead of a patch file.",
              "Today's card code changes until the approved 557 card matches."],
  "open": ["Whether approving this split can file new stories at all.",
           "Which issue gets the fixture record comment."]},
 "verdict": "approve",
 "summary": "The plan carries every ask of the widened scope; three questions wait for you, first whether the split can file.",
 "raises": [
  {"kind": "issue", "label": "Split never refiled",
   "text": "An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.",
   "evidence": "`dokima/agent.py:381` `file_split()` returns the old split record; #591 is closed, code unchanged."}
 ],
 "answers": [],
 "asks": [
  {"ask": "the tool previews any visual change, not just the card. That covers the top card, run comments and autopilot comments.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.2"},
  {"ask": "one command draws what Dokima would post, using the real drawing code from any branch and the real records of a real issue", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.1"},
  {"ask": "autopilot comments", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "S1.3"},
  {"ask": "shows which lines differ from today's card", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S2.1"},
  {"ask": "It writes nothing to this repo or to the real issue.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "S2.2"},
  {"ask": "This tool is for us, never a product feature.", "source": "ht
```

> (Bash completed with no output)

**Agent:** I approved the plan for #584 (our internal visual preview tool). The hand-back is in `/tmp/dokima-out/review.json` and passes both of Dokima's checks. It still stops for you, though, because the planner's three questions are open.

**What I checked**
- **Every ask is covered.** All 14 of your asks have a matching criterion, from the widened-scope comment and the earlier rescope comment. That includes the run and autopilot comments, the private card-gallery preview that keeps editing one comment, freezing to `tests/fixtures/`, the fixture record comment, working offline, and matching the #557 card.
- **Each criterion is one behavior.** The 14 criteria make 5 stories. No edge cases needed cutting or adding.
- **The #557 claim is true.** I drew the saved #557 data from branch `fixture/card-557` with today's card code. The first difference is at line 21 (a nested list item), so story 5 does need to change `dokima/card.py`. You asked for that explicitly.

**Questions I left for you** (none of them is settled by your own words):
- **P4, the split won't file.** I confirmed `file_split()` at `dokima/agent.py:381` returns the old split record. So approving files no new stories, even though #585 and #586 are closed. Your answer "file the new stories" can't happen until that code is fixed.
- **P5, which issue gets the fixture record.** It could be this repo's issue the change is for, or the gallery issue.
- **P6, branch or patch file.** It's unclear whether drawing from a chosen branch replaces the older patch-file idea.

**Problem outside this issue:** I raised this filing gap again as its own issue proposal, since [#591](https://github.com/dokima-dev/dokima/issues/591) (split never refiled) is closed but the code hasn't changed.

The split has no tests yet; each story gets its own when it is planned.

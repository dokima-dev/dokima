# reviewer (plan) for #627

Run: https://github.com/dokima-dev/dokima/actions/runs/38488793297

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #627: Approving a preview freezes it as a fixture
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 625 -->
> <!-- dokima-blocking: {"blocked_by": [625], "blocks": [628], "loop": []} -->
> One command saves an approved drawing with the data it came from, and records it on its issue.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/625
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/628
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/626
> - https://github.com/dokima-dev/dokima/issues/631
> - https://github.com/dokima-dev/dokima/issues/624
> 
> 
> **User story:** When the owner approves a preview, its drawing and data are kept, and the issue shows the approved drawing.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance 

`2. Bash`
```
cd /tmp/pack; python3 -c "import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cat parent.json | head -c 3000; cd /home/runner/work/dokima/dokima; cat tests/test_visuals_finalize.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38488424536",
>  "commit_before": "93c3650ee457375fc7a2b202490a9a7d16ff20db",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 72303,
>   "turns": 11,
>   "cost_usd": 0.6360388,
>   "tokens_in": 542883,
>   "tokens_out": 6952
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/627/38488424536-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38488424536",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote three criteria and eight tests for a finalize command.",
>     "Each test fails today because the command does not exist yet."
>    ],
>    "decided": [
>     "The fixture record goes on the issue itself, never the gallery issue.",
>     "Run and autopilot comments get their own inputs and drawing files."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "One test is too weak: saved autopilot comment data could be useless and the test would still pass.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Weak test",
>     "text": "627.1 promises inputs that redraw offline, but `test_finalize_saves_comment_inputs` checks autopilot posts only by link. Fix: assert each saved post equals what `draw` hands its painter.",
>     "evidence": "tests/test_visuals_finalize.py:271-275 compares only `url`; `paint` in `tools/visuals.py` needs `key`, `pr` and `args`.",
>     "raised_by": "reviewer",
>     "id": "R1

`3. Bash`
```
cd /home/runner/work/dokima/dokima; ls tools; grep -n "kind\|def \|posts" tools/visuals.py | head -80; python3 -m pytest -q tests/test_visuals_finalize.py 2>&1 | grep -E "^E .*627|passed|failed" | head -20
```

> visuals.py
> 11:`preview` posts that same drawing, with the caller's own `gh` login, as one comment on issue N of the gallery repo, so
> 36:def numbers(text):
> 40:def autopilot_post(agent, number, text):
> 44:        return {"kind": "line"}
> 46:        return {"kind": "start"}
> 49:            return {"kind": "lines", "key": key}
> 53:            return {"kind": "merge", "key": key, "pr": int(m.group(1))}
> 62:    return {"kind": "reply", "args": args} if agent.autopilot_comment(*args).strip("\n") == text else None
> 65:def read(repo, number):
> 66:    """The issue's posts, oldest first, read with this checkout's code: run records and autopilot comments."""
> 73:    posts = []
> 77:            posts.append({"kind": "record", "rec": rs[0], "url": c.get("url", "")})
> 81:                posts.append({**post, "url": c.get("url", "")})
> 82:    return posts
> 85:def commit_of(branch):
> 95:def draw(number, branch, repo, stdout=None):
> 98:    posts = read(repo, number)
> 107:                json.dump({"repo": repo, "issue": number, "posts": posts}, f)
> 115:def gallery(*args, stdin=None):
> 123:def preview(number, branch, repo, gallery_issue):
> 146:def paint(job):
> 169:    for post in job["posts"]:
> 170:        out += ["", "", f"# {'Run' if post['kind'] == 'record' else 'Autopilot'} comment {post['url']}", ""]
> 171:        if post["kind"] == "record":
> 177:        elif post["kind"] == "line":
> 179:        elif post["kind"] == "start":
> 181:        elif post["kind"] == "lines":
> 183:        elif post["kind"] == "merge":
> 190:d

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 60,112p tools/visuals.py; grep -n "def test_draw\|jobs\|json.load" tests/test_visuals_draw.py | head -20
```

> args = [number, switch, numbers(m["switched"]), numbers(m["started"]), picked]
>     # Only a reply this checkout's code would word exactly so counts.
>     return {"kind": "reply", "args": args} if agent.autopilot_comment(*args).strip("\n") == text else None
> 
> 
> def read(repo, number):
>     """The issue's posts, oldest first, read with this checkout's code: run records and autopilot comments."""
>     sys.path.insert(0, ROOT)
>     from dokima import agent, card
>     try:
>         _, items = agent.conversation(repo, number)
>     except (subprocess.CalledProcessError, ValueError, KeyError, TypeError) as e:
>         raise Stop(f"GitHub could not give #{number} of {repo}: {card.reason(e)}")
>     posts = []
>     for c in items:
>         rs = agent.records([c])
>         if rs:
>             posts.append({"kind": "record", "rec": rs[0], "url": c.get("url", "")})
>         elif (c.get("author") or {}).get("login") == agent.BOT:
>             post = autopilot_post(agent, number, c.get("body") or "")
>             if post:
>                 posts.append({**post, "url": c.get("url", "")})
>     return posts
> 
> 
> def commit_of(branch):
>     """The commit `branch` names here or on origin."""
>     for ref in (branch, f"origin/{branch}"):
>         r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=ROOT,
>                            capture_output=True, text=True)
>         if r.returncode == 0:
>             return r.stdout.strip()
>     raise Stop(f"No branch named {branch!r} here or on origin.

`5. Bash`
```
mkdir -p /tmp/rv && cat > /tmp/rv/test_probe.py <<'EOF'
import json, subprocess, sys, os
sys.path.insert(0, "/home/runner/work/dokima/dokima")
from tests.test_visuals_finalize import place, fresh, env_of, REPO, ISSUE
def test_probe(place):
    p = fresh(place, "probe")
    code = "import sys,json;sys.path.insert(0,'tools');import visuals;print(json.dumps([x for x in visuals.read(%r,%d) if x['kind']!='record']))" % (REPO, ISSUE)
    r = subprocess.run([sys.executable, "-c", code], cwd=p["repo"], env=env_of(p), capture_output=True, text=True)
    print(r.stdout, r.stderr)
    assert 0
EOF
cd /home/runner/work/dokima/dokima && python3 -m pytest -q -p no:cacheprovider /tmp/rv/test_probe.py 2>&1 | grep -A3 "Captured stdout" | head
```

> ----------------------------- Captured stdout call -----------------------------
> [{"kind": "line", "url": "https://github.com/dokima-dev/dokima/issues/7#issuecomment-102"}, {"kind": "lines", "key": "worker", "url": "https://github.com/dokima-dev/dokima/issues/7#issuecomment-105"}, {"kind": "reply", "args": [7, "start", [7], [], "No stage was started."], "url": "https://github.com/dokima-dev/dokima/issues/7#issuecomment-106"}, {"kind": "start", "url": "https://github.com/dokima-dev/dokima/issues/7#issuecomment-107"}, {"kind": "merge", "key": "merged", "pr": 9, "url": "https://github.com/dokima-dev/dokima/issues/7#issuecomment-108"}]
>  
> =========================== short test summary info ============================

**Agent:** Found a likely problem: one test expects autopilot comments in an order the existing reader doesn't give. Checking a last detail, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def render" dokima/card.py; git show origin/fixture/card-557 --stat 2>/dev/null | head; git branch -a | grep fixture
```

> 504:def render(repo, issue, found, page="issue"):
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
>   remotes/origin/fixture/card-557

`7. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the autopilot comment test check each saved post whole.", "Eight tests still fail today because the finalize command does not exist."], "decided": ["The fixture record goes on the issue itself, never the gallery issue."], "open": []},
 "verdict": "block",
 "summary": "One test expects autopilot comments in an order the issue does not have, so correct work fails it.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Test cannot pass", "text": "`test_finalize_saves_comment_inputs` for 627.1 wants autopilot posts ordered 102, 107, 105, 106, 108, but `draw` hands its painter 102, 105, 106, 107, 108. Saving what `draw` reads fails it. Fix: put the `start` post (107) after the `reply` post (106).", "evidence": "tests/test_visuals_finalize.py:265-269; `read(REPO, 7)` in the test checkout returns comments 102, 105, 106, 107, 108."}
 ],
 "answers": [
  {"raise": "R1", "answer": "done", "why": "The test now compares each saved autopilot post whole, but its expected order is wrong; raised again."}
 ],
 "asks": [
  {"ask": "Finalizing saves the drawing's inputs under the fixtures folder.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.1"},
  {"ask": "Finalizing saves the drawing's output beside its inputs.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.2"},
  {"ask": "Finalizing posts the final drawing on its issue here as a comment marked as its fixture record.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156486728", "criterion": "627.3"}
 ],
 "behaviors": [
  {"criterion": "627.1", "one_behavior": true, "why": "Saving the inputs needed to redraw offline is one result."},
  {"criterion": "627.2", "one_behavior": true, "why": "Saving the drawing as the branch drew it is one result."},
  {"criterion": "627.3", 
```

> Exit code 1
> raise 1's text holds 39 words, over its cap of 30: cut 9, keep the facts

`8. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="`test_finalize_saves_comment_inputs` (627.1) expects autopilot posts ordered 102, 107, 105, 106, 108; `draw` reads 102, 105, 106, 107, 108. Fix: move post 107 after 106."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 627 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> answer 1 names 'R1', which no open raise has
> 1

`9. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p));d['answers']=[];json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 627 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> 0

**Agent:** I blocked the plan for [#627](https://github.com/dokima-dev/dokima/issues/627) (saving an approved preview as a fixture). It has one blocker, sent back to the planner.

**Blocker (test cannot pass):** `test_finalize_saves_comment_inputs`, which tests criterion 627.1, expects the issue's autopilot comments in this order: 102, 107, 105, 106, 108. The existing `draw` reads them oldest first: 102, 105, 106, 107, 108. I checked this by running `read()` against the test's fake GitHub. So a finalize command that saves exactly what `draw` reads would fail the test. The fix is to move comment 107 after 106 in the test's expected list.

The rest of the plan holds up:
- **Last round's blocker is fixed.** That test now checks each saved autopilot comment in full, not just its link.
- **All eight tests fail today for the right reason.** The `finalize` command doesn't exist yet, so each run exits with code 2.
- **No ask is missing.** Each of the three asks from the parent story in [#584](https://github.com/dokima-dev/dokima/issues/584) (previewing visuals and freezing approved fixtures) has its own criterion.
- **Size is ok.** Each criterion covers one behaviour, each test checks only its own criterion, and no edge cases needed cutting or adding.

The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

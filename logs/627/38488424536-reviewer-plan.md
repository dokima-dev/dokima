# reviewer (plan) for #627

Run: https://github.com/dokima-dev/dokima/actions/runs/38488424536

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.gi

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:6000])"; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"; head -c 1500 open_issues.json
```

> {
>  "number": null
> }
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38487909960",
>  "commit_before": "a582346d2600cca5a72a2db43ee59f4bc2ff41f9",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 256971,
>   "turns": 18,
>   "cost_usd": 1.364555,
>   "tokens_in": 1279279,
>   "tokens_out": 23250
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/627/38487909960-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38487909960",
>  "handback": {
>   "kind": "user_story",
>   "title": "Approving a preview freezes it as a fixture",
>   "summary": "One command saves an approved drawing with the data it came from, and records it on its issue.",
>   "user_story": "When the owner approves a preview, its drawing and data are kept, and the issue shows the approved drawing.",
>   "acceptance_criteria": [
>    {
>     "text": "Finalizing saves the drawing's inputs in the fixtures folder, enough to draw it again offline.",
>     "words": "when I approve, it freezes the inputs and output under tests/fixtures/",
>     "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768",
>     "edge_cases": [
>      {
>       "case": "The run and autopilot comments' inputs are saved too, not only the card's.",
>       "test": "tests/test_visuals_finalize.py::test_finalize_saves_comment_inputs"
>      },
>      {
>       "case": "An issue GitHub cannot give saves nothing and says why.",
>       "test": "tests/test_visuals_finalize.py:

`3. Bash`
```
cd /home/runner/work/dokima/dokima; gh api repos/dokima-dev/dokima/issues/comments/6155799768 --jq .body 2>&1 | head -50; gh api repos/dokima-dev/dokima/issues/comments/6156486728 --jq .body 2>&1 | head -50
```

> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}
> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; wc -l tools/visuals.py tests/test_visuals_finalize.py; ls tests/fixtures | head; git ls-remote origin 'fixture/*' 2>&1|head
```

> commit 93c3650ee457375fc7a2b202490a9a7d16ff20db
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:08:10 2026 +0000
> 
>     planner for #627 (run 38487909960)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_visuals_finalize.py | 380 +++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 380 insertions(+)
>   220 tools/visuals.py
>   380 tests/test_visuals_finalize.py
>   600 total
> ls: cannot access 'tests/fixtures': No such file or directory
> e98dee4e199f9d66c37e80def5ccc215690eee59	refs/heads/fixture/card-557

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat tools/visuals.py; cat tests/test_visuals_finalize.py
```

> """Draw what Dokima would post on a real issue, with any branch's code.
> 
>     python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME
>     python3 tools/visuals.py preview ISSUE --branch BRANCH --repo OWNER/NAME --gallery-issue N
> 
> Run from the root of a checkout. The issue is read from GitHub through `gh`, and nothing is written there. The
> drawing code is taken from BRANCH through a git worktree of it in a temporary folder, so this checkout is left as it
> is. Printed to stdout: the issue's top card, every run comment drawn again from its record, and every autopilot
> comment drawn again as BRANCH's code would word it. Autopilot comments are recognised by this checkout's own lines.
> 
> `preview` posts that same drawing, with the caller's own `gh` login, as one comment on issue N of the gallery repo, so
> GitHub renders it. A hidden marker names the real issue, so a later preview of it edits that comment instead of posting
> another. Nothing is written to OWNER/NAME.
> """
> import argparse
> import json
> import os
> import re
> import subprocess
> import sys
> import tempfile
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> GALLERY = "dokima-dev/card-gallery"
> REPLY = re.compile(r"(?:Autopilot is (?P<on>on|off) for (?P<switched>#\d+(?:, #\d+)*)\."
>                    r"|#\d+ and every issue under it were already on autopilot\.(?P<none_on>)"
>                    r"|No issue in #\d+'s tree was on autopilot\.(?P<none_off>))"
>                    r"(?: Planning started for (?P<sta

**Agent:** Reviewing the plan for #627: I've read the plan and tests; now running them and checking the fixture branch's shape.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git fetch -q origin fixture/card-557 2>&1|tail -2; git show --stat FETCH_HEAD | head -20; timeout 600 python3 -m pytest -q tests/test_visuals_finalize.py 2>&1 | tail -15
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
>     Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
>     Claude-Session: https://claude.ai/code/session_01RwApTMqmVLpXvPk8iiYke3
> 
>  tests/fixtures/cards/557.card.md     |   55 +
>  tests/fixtures/cards/557.inputs.json | 4561 ++++++++++++++++++++++++++++++++++
>  2 files changed, 4616 insertions(+)
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'finalize', '7', '--...raw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)\n").returncode
> FAILED tests/test_visuals_finalize.py::test_finalize_posts_fixture_record - AssertionError: 627.3: finalizing #7 from visual-test exited 2:
>   
>   usage: tools/visuals.py [-h] {draw,preview} ...
>   tools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)
>   
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'finalize', '7', '--...raw,preview} ..

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git show FETCH_HEAD:tests/fixtures/cards/557.inputs.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.keys());print(d.get('edge_case_sources'))"; grep -n "def render\b\|def render(" dokima/card.py; grep -rn "edge_case_sources" dokima/ | head
```

> dict_keys(['edge_case_sources', 'found', 'issue', 'repo'])
> {'It changes a workflow file: it still waits for the owner.': 'https://github.com/dokima-dev/dokima/issues/557#issuecomment-6132201738'}
> 504:def render(repo, issue, found, page="issue"):

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def world\|def records\|Autopilot\|\"8\"\|502\|role\|BRANCH_AGENT\|pr\b" tests/test_visuals_draw.py | head -50
```

> 72:if method.upper() != "GET" or argv[:2] in (["issue", "comment"], ["issue", "edit"], ["pr", "comment"], ["pr", "edit"]):
> 77:if argv[:2] == ["pr", "list"]:
> 79:if argv[:2] == ["pr", "view"]:
> 125:BRANCH_AGENT = '''
> 143:AUTOPILOT_LINE = "Autopilot: BRANCH blockers line"
> 144:AUTOPILOT_LINES = {"worker": "Autopilot: BRANCH work line", "split": "Autopilot: BRANCH split line"}
> 145:AUTOPILOT_START_LINE = "Autopilot: BRANCH switch line"
> 146:AUTOPILOT_MERGE = {"merged": "Autopilot: BRANCH merged PR #{pr}", "queued": "Autopilot: BRANCH PR #{pr} queued",
> 147:                   "waits": "Autopilot: BRANCH PR #{pr} waits"}
> 158:def records():
> 162:    planner = {"role": "planner", "stage": None, "run": run, "check": {"passed": True, "problems": []},
> 168:    review = {"role": "reviewer", "stage": "plan", "run": run, "check": {"passed": True, "problems": []},
> 179:def world():
> 185:                comment(2, BOT, "Autopilot: blockers merged, starting plan"),
> 186:                comment(7, BOT, "Autopilot: switched on, starting plan"),
> 189:                comment(5, BOT, "Autopilot: plan approved, starting work"),
> 190:                comment(6, BOT, f"Autopilot is on for #{ISSUE}. No stage was started.\n"),
> 191:                comment(8, BOT, "Autopilot: merged PR #9")]
> 196:            "refused": {"8": "Server Error (HTTP 502)"}}
> 218:        f.write(BRANCH_AGENT)
> 285:    assert "#8" in said and "HTTP 502" in said, f"624.1: the message does not name the issue and GitHub's reason:\n{said}"
> 339:   

**Agent:** All 8 tests fail today for the right reason (no `finalize` command). One weak test found; writing the review.

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria and eight tests for a finalize command.",
          "Each test fails today because the command does not exist yet."],
  "decided": ["The fixture record goes on the issue itself, never the gallery issue.",
              "Run and autopilot comments get their own inputs and drawing files."],
  "open": []},
 "verdict": "block",
 "summary": "One test is too weak: saved autopilot comment data could be useless and the test would still pass.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Weak test",
   "text": "627.1 promises inputs enough to redraw offline, but `test_finalize_saves_comment_inputs` checks autopilot posts only by link, so posts missing their kind, line key, pull request or reply details still pass. Fix: assert each saved autopilot post equals what `draw` hands its painter.",
   "evidence": "tests/test_visuals_finalize.py:271-275 compares only `url`; `paint` in `tools/visuals.py` needs `key`, `pr` and `args`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Finalizing saves the drawing's inputs under the fixtures folder.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.1"},
  {"ask": "Finalizing saves the drawing's output beside its inputs.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.2"},
  {"ask": "Finalizing posts the final drawing on its issue here as a comment marked as its fixture record.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156486728", "criterion": "627.3"}
 ],
 "behaviors": [
  {"criterion": "627.1", "one_behavior": true, "why": "Saving the inputs needed to redraw offline is one result."},
  {"criterion": "627.2", "one_behavior": true, "why": "Saving the drawing as the branch drew it is one result."},
  {"criterion": "627.3", "one_behavior": true, "why": "Pos
```

> Exit code 1
> raise 1's text holds 41 words, over its cap of 30: cut 11, keep the facts

`10. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['raises'][0]['text']="627.1 promises inputs that redraw offline, but `test_finalize_saves_comment_inputs` checks autopilot posts only by link. Fix: assert each saved post equals what `draw` hands its painter."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 627 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for #627 (saving an approved preview as a fixture) and sent it back to the planner because of one weak test. The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**The blocker:** criterion 627.1 promises saved inputs that are enough to draw the issue's posts again offline. But `test_finalize_saves_comment_inputs` checks the saved autopilot comments only by their links. If finalize saved those comments without what the drawing step needs to draw them again, the test would still pass. The fix I asked for: check each saved autopilot comment against exactly what `draw` hands its drawing step.

**What passed:**
- **Tests fail for the right reason:** all 8 tests fail today only because there is no `finalize` command yet. Nothing crashes, no tool is missing and no path is bad.
- **Owner's asks:** the issue's three asks each map to one criterion (627.1 to 627.3). I couldn't open the #584 comments the issue quotes, because there is no GitHub access here, so I matched against the asks as written in this issue.
- **Size:** each criterion is one behavior. No edge cases needed cutting or adding.

**Noted but not blocking:**
- The approved #557 fixture (the example on branch `fixture/card-557`) also saves an `edge_case_sources` key, which the plan doesn't save. Today's card drawing code doesn't read that key, so nothing is lost.
- Finalizing the same issue twice would post a second fixture record rather than edit the first. The owner never said which they want, so I didn't raise it.

# reviewer (plan) for #818

Run: https://github.com/dokima-dev/dokima/actions/runs/39044206979

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #818: The reviewer's prompt spells out its duties and boxes
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 817 -->
> <!-- dokima-blocking: {"blocked_by": [817], "blocks": [819], "loop": []} -->
> The reviewer's prompt names its four duties and the six boxes it fills for them.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/817
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/819
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/743
> 
> 
> **User story:** The reviewer's prompt names its four duties and the boxes it fills for each.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -c 20000; echo; cat open_issues.json | head -c 3000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:4000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/741": "Phase 1 of #272. Replaces #42 (closed, superseded by the YAML settings decision).\n\n**What**\n- Role prompts ship with Dokima and contain no example from Dokima's own code. Today every example uses `dokima/card.py` or `dokima/board.py` (`roles/planner.md:99-170`), the planner says pytest in `tests/` is the only runner (`planner.md:115`), and AGENTS.md is assumed in `planner.md:146`, `worker.md:58`, `reviewer.md:49,75`.\n- The 50-line \"raising\" block copied into planner, worker and reviewer moves to one shared `roles/raising.md` with neutral examples.\n- Numbers written into prompts (\"more than 3 questions\", \"three blocks in a row\", word caps) are read from settings.\n- A repo appends house rules through `prompts.append` in `settings.yaml`, per role or for all. Appending only; a repo never replaces a shipped prompt, so Dokima upgrades do not break it.\n- Default criterion style in the planner prompt: \"When X, Y\". A style convention, not a rule code enforces. Repos may override it in house rules.\n- Rewrite size: planner about 45%, worker about 55%, reviewer about 40%; the two grade prompts stay as they are.\n\n**Done when:** acceptance items 5 and 6 on #272 pass: a scan finds no Dokima file name in any shipped prompt; a repo's house rules appear after the shipped prompt for each role.\n",
>  "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975": "Owner 2026-10-15: the reviewer's four duties, writ

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_reviewer_duties.py; git show --stat HEAD | head -20; python -m pytest -q tests/test_reviewer_duties.py 2>&1 | tail -30
```

> """Tests for #818: the reviewer's prompt spells out its duties and boxes.
> 
> The owner wrote the duties in the comment of 2026-10-15 on #741 and the boxes in the comment after it. Each test
> builds the reviewer's prompt the way agent.yml builds it, `python3 -m dokima.prompt reviewer GRADE`, at both moments
> the reviewer works: with the plan grade and with the result grade. A duty must be said in one sentence of the built
> prompt; the boxes must be shown as the owner shaped them. Code that checks the boxes is #819, not this issue.
> """
> import os
> import re
> import subprocess
> import sys
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> GRADES = ("plan-grade", "result-grade")
> 
> 
> def built(tmp, grade):
>     """The reviewer's prompt agent.yml builds with GRADE, with no settings file.
> 
>     Runs `python3 -m dokima.prompt reviewer GRADE` in a temp folder, Dokima's code first on the path; fails the test,
>     with the error, when the prompt is not built."""
>     folder = os.path.join(str(tmp), grade)
>     os.makedirs(folder, exist_ok=True)
>     env = dict(os.environ, PYTHONPATH=ROOT)
>     r = subprocess.run([sys.executable, "-m", "dokima.prompt", "reviewer", grade], cwd=folder, env=env,
>                        capture_output=True, text=True, timeout=60)
>     assert r.returncode == 0 and r.stdout.strip(), \
>         f"the reviewer's prompt ({grade}) was not built: exit {r.returncode}\n{r.stderr}"
>     return r.stdout
> 
> 
> def flat(text):
>     """TEXT on one line, spaces squeezed and curl

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline --all | grep -i "741\|817\|819" | head; ls; grep -rn "blocker unless\|every box" --include=*.py --include=*.md . | head
```

> 34ae13a Record of run 39040031341 for #817
> 8d5254c Record of run 39039471106 for #817
> e93f602 Record of run 39039243707 for #817
> 701daa6 Record of run 39037543606 for #817
> e71f072 Record of run 39037417694 for #741
> dd1eb77 Conversation of run 39037417694
> 797796a Record of run 39037335667 for #741
> 43a572e Record of run 39037173766 for #741
> d7f0f64 Record of run 39037042766 for #741
> f565041 Record of run 39036631238 for #741
> AGENTS.md
> CLAUDE.md
> LICENSE
> README.md
> docs
> dokima
> rules
> tests
> tools

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat e71f072 | head; git show e71f072 --name-only --format= | head; 
```

> commit e71f072980c22e72b53abda08d510cb0a5b84111
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 13:40:07 2026 +0000
> 
>     Record of run 39037417694 for #741
> 
>  ...20261017T134006Z-39037417694-reviewer-plan.json | 397 +++++++++++++++++++++
>  1 file changed, 397 insertions(+)
> logs/741/records/20261017T134006Z-39037417694-reviewer-plan.json

**Agent:** Still reviewing the plan; checking the parent #741 review to see how its asks were split across stories.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show e71f072:logs/741/records/20261017T134006Z-39037417694-reviewer-plan.json | python3 -c "
import json,sys;d=json.load(sys.stdin);h=d.get('handback',d)
print(h.get('verdict'));
for a in h.get('asks',[]): print(a['criterion'],'|',a['ask'][:150])"
```

> approve
> S1.1 | Role prompts ship with Dokima and contain no example from Dokima's own code.
> S1.1 | a scan finds no Dokima file name in any shipped prompt
> S1.2 | The 50-line "raising" block copied into planner, worker and reviewer moves to one shared `roles/raising.md` with neutral examples.
> S1.3 | moves to one shared `roles/raising.md`
> S1.4 | Numbers written into prompts ("more than 3 questions", ...) are read from settings.
> S1.5 | Numbers written into prompts (... "three blocks in a row", ...) are read from settings.
> S1.6 | Default criterion style in the planner prompt: "When X, Y".
> S1.10 | A repo appends house rules through `prompts.append` in `settings.yaml`, per role or for all.
> S1.10 | a repo's house rules appear after the shipped prompt for each role
> S1.7 | The planner tries to write each criterion with a source, a result ... and a test.
> S1.8 | Each blank it cannot fill becomes one question to the owner, kind `question`.
> S1.9 | Examples for the prompt:
> S2.1 | Nothing dropped. Every sentence of the owner's maps to a criterion or is marked "not a requirement" with a reason.
> S2.2 | No stale criteria. Sources are append-only and later words win.
> S2.3 | the reviewer confirms or retires it.
> S2.4 | Conflicts handled. When two owner sources disagree and no later word settles it, the reviewer asks the owner. It never picks.
> S2.5 | Nothing added. Every change in the diff serves a criterion.
> S2.6 | **Reviewer: required boxes.** One per duty
> S3.1 | every box present
> S3.2 | entries 

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote six criteria, one per duty line and one for the six boxes.",
          "The planner wrote six tests that build the reviewer's prompt for plan and code review."],
  "decided": ["Each duty must be said at both review stages.",
              "The boxes must appear as the owner shaped them."],
  "open": ["Code checking the boxes stays with issue 819."]},
 "verdict": "approve",
 "summary": "The plan carries all four duties and the six boxes, each with a test that fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Every sentence of the owner's maps to a criterion or is marked \"not a requirement\" with a reason.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975", "criterion": "818.1"},
  {"ask": "Sources are append-only and later words win.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975", "criterion": "818.2"},
  {"ask": "the reviewer confirms or retires it.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975", "criterion": "818.3"},
  {"ask": "When two owner sources disagree and no later word settles it, the reviewer asks the owner. It never picks.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975", "criterion": "818.4"},
  {"ask": "anything that serves no criterion blocks", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975", "criterion": "818.5"},
  {"ask": "**Reviewer: required boxes.** One per duty", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6205062350", "criterion": "818.6"},
  {"ask": "both, plan review and code review.", "source": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234488387", "criterion": "818.6"}
 ],
 "behaviors": [
  {"criterion": "818.1", "one_behavior": true, "why": "One duty sent
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)

`8. Bash`
```
sed -i 's/"summary": "The plan carries all four duties and the six boxes, each with a test that fails today for the right reason."/"summary": "The plan carries all four duties and the six boxes, each with a test that fails today as it should."/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 818 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`9. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/"summary": "The plan carries all four duties and the six boxes, each with a test that fails today for the right reason."/"summary": "The plan carries all four duties and the six boxes, each with a test that fails today as it should."/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 818 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

**Agent:** I approved the plan for [#818](https://github.com/dokima-dev/dokima/issues/818) (reviewer prompt duties and boxes). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** each of the owner's four duties, from [#741's comment of 2026-10-15](https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975), maps to its own criterion, 818.1 to 818.5. The six required boxes map to 818.6. So does the owner's later answer that the boxes apply at both plan and code review. None are missing.
- **Split:** I compared this with the approved plan for [#741](https://github.com/dokima-dev/dokima/issues/741) (prompts that fit any repo). This issue is its story 2. Code enforcing the boxes, including "each entry a blocker unless noted", belongs to [#819](https://github.com/dokima-dev/dokima/issues/819) (code checks the boxes), so leaving it out here is right.
- **Tests:** I ran all six. They all fail today as they should: the prompt builds at both stages, but the duty wording and the box lines aren't in it yet. The box test checks the owner's six box lines word for word.
- **Raises:** none, and no earlier blockers were open.

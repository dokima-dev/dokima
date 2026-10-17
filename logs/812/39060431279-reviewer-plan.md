# reviewer (plan) for #812

Run: https://github.com/dokima-dev/dokima/actions/runs/39060431279

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (86.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/20e2389b-12ba-4103-b8b5-4fa1f2abe331/tool-results/bw2mr8irx.txt
> 
> Preview (first 2KB):
> total 184
> drwxr-xr-x 2 runner runner  4096 Oct 17 18:59 .
> drwxr-xr-x 3 runner runner  4096 Oct 17 18:59 ..
> -rw-r--r-- 1 runner runner  9145 Oct 17 18:59 01-planner.json
> -rw-r--r-- 1 runner runner  8034 Oct 17 18:59 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner  9572 Oct 17 18:59 03-planner.json
> -rw-r--r-- 1 runner runner  7845 Oct 17 18:59 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner  9548 Oct 17 18:59 05-planner.json
> -rw-r--r-- 1 runner runner  7407 Oct 17 18:59 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner  5474 Oct 17 18:59 07-worker.json
> -rw-r--r-- 1 runner runner  3238 Oct 17 18:59 08-reviewer-pr.json
> -rw-r--r-- 1 runner runner 14037 Oct 17 18:59 09-planner.json
> -rw-r--r-- 1 runner runner 13639 Oct 17 18:59 10-reviewer-plan.json
> -rw-r--r-- 1 runner runner  2723 Oct 17 18:59 11-worker.json
> -rw-r--r-- 1 runner runner  2421 Oct 17 18:59 12-worker.json
> -rw-r--r-- 1 runner runner  2169 Oct 17 18:59 13-worker.json
> -rw-r--r-- 1 runner runner  2928 Oct 17 18:59 14-reviewer-pr.json
> -rw-r--r-- 1 runner runner 13624 Oct 17 18:59 15-planner.json
> -rw-r--r-- 1 runner runner 13865 Oct 17 18:59 16-reviewer-plan.json
> -rw-r--r-- 1 runner runner  3069 Oct 17 18:59 17-worker.json
> -rw-r--r-- 1 runner runner  2346 Oct 17 18:59 18-reviewer-pr.json
> -rw-r--r-- 1 runner runn

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (72.7KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/20e2389b-12ba-4103-b8b5-4fa1f2abe331/tool-results/bqqx4ym94.txt
> 
> Preview (first 2KB):
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/824 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; cat plan.json
```

> []{
>  "kind": "user_story",
>  "title": "Dokima's workflows run from Dokima's own repo",
>  "summary": "Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.",
>  "user_story": "An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.",
>  "acceptance_criteria": [
>   {
>    "text": "A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.",
>    "words": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
>    "source": "https://github.com/dokima-dev/dokima/issues/742",
>    "files": [
>     "dokima/install/dokima.yml",
>     ".github/workflows/entry.yml",
>     ".github/workflows/acceptance-criteria.yml",
>     ".github/workflows/agent.yml",
>     ".github/workflows/assign.yml",
>     ".github/workflows/audit.yml",
>     ".github/workflows/autopilot.yml",
>     ".github/workflows/board.yml",
>     ".github/workflows/card.yml",
>     ".github/workflows/commands.yml",
>     ".github/workflows/fix.yml",
>     ".github/workflows/full-suite.yml",
>     ".github/workflows/reviews.yml",
>     ".github/workflows/testmon.yml",
>     ".github/workflows/uptodate.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An adopter's repo holding no Dokima code at all",
>      "test": "tests/test_thin_install.py::test_a_run_starts_in_a_repo_holding_no_dokima_code"
>     },
>     {
>      "case": "An adopter's repo holding its own copy of Dokima's code",
>      "test": "tests/test_thin_inst

`4. Bash`
```
cd /tmp/pack; cat issue.md
```

`5. Bash`
```
cd /tmp/pack; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (72.7KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/20e2389b-12ba-4103-b8b5-4fa1f2abe331/tool-results/bqqx4ym94.txt
> 
> Preview (first 2KB):
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/824 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/

> []{
>  "kind": "user_story",
>  "title": "Dokima's workflows run from Dokima's own repo",
>  "summary": "Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.",
>  "user_story": "An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.",
>  "acceptance_criteria": [
>   {
>    "text": "A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.",
>    "words": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
>    "source": "https://github.com/dokima-dev/dokima/issues/742",
>    "files": [
>     "dokima/install/dokima.yml",
>     ".github/workflows/entry.yml",
>     ".github/workflows/acceptance-criteria.yml",
>     ".github/workflows/agent.yml",
>     ".github/workflows/assign.yml",
>     ".github/workflows/audit.yml",
>     ".github/workflows/autopilot.yml",
>     ".github/workflows/board.yml",
>     ".github/workflows/card.yml",
>     ".github/workflows/commands.yml",
>     ".github/workflows/fix.yml",
>     ".github/workflows/full-suite.yml",
>     ".github/workflows/reviews.yml",
>     ".github/workflows/testmon.yml",
>     ".github/workflows/uptodate.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An adopter's repo holding no Dokima code at all",
>      "test": "tests/test_thin_install.py::test_a_run_starts_in_a_repo_holding_no_dokima_code"
>     },
>     {
>      "case": "An adopter's repo holding its own copy of Dokima's code",
>      "test": "tests/test_thin_inst

`6. Bash`
```
cd /tmp/pack; grep -n "^## \|^### \|comment" issue.md | head -80; wc -l issue.md
```

> 54:  - Source: https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528
> 58:  - Source: https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528
> 66:  - Source: https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528
> 110:## Comments
> 112:### dokima-runtime on issue #812 (2026-10-17T13:34:18Z)
> 116:### dokima-runtime on issue #812 (2026-10-17T13:34:40Z)
> 145:### dokima-runtime on issue #812 (2026-10-17T14:01:12Z)
> 152:- Planner on [#812](https://github.com/dokima-dev/dokima/issues/812#issuecomment-6234501883) raised: <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/issue-found.svg" width="16" height="16" align="absmiddle" alt="issue found"> **Check names in adopters:** In an adopter's repo the checks run inside a called workflow, so GitHub prefixes their names; the required check names will not match. · filed as an issue
> 176:### dokima-runtime on issue #812 (2026-10-17T14:05:26Z)
> 183:- Plan review on [#812](https://github.com/dokima-dev/dokima/issues/812#issuecomment-6234800119) raised: <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocker.svg" width="16" height="16" align="absmiddle" alt="blocker"> **Test off its criterion:** `test_every_event_dokima_acts_on_starts_the_adopters_workflow` proves the one workflow starts on every event, not where code comes from (812.1). Give it its own criterion from the owner's 'One thin workflow', or drop it. · for the planner
> 205:### doki

`7. Bash`
```
cd /tmp/pack; sed -n 30,110p issue.md; sed -n 490,560p issue.md; sed -n 700,782p issue.md
```

> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.
>   *<a href="https://github.com/dokima-dev/dokima/blob/a0fb4c6ad558cabffee11e9f4dd8583d5bae99e0/tests/test_thin_install.py#L139"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: No job of any shared workflow runs Dokima code from the adopter's repo.*
>   <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/a0fb4c6ad558cabffee11e9f4dd8583d5bae99e0/tests/test_thin_install.py#L125">An adopter's repo holding no Dokima code at all</a></em></li><li><em><a href="https://github.com/dokima-dev/dokima/blob/a0fb4c6ad558cabffee11e9f4dd8583d5bae99e0/tests/test_thin_install.py#L107">An adopter's repo holding its own copy of Dokima's code</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/dokima/issues/742
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started">

`8. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['16-reviewer-plan.json','18-reviewer-pr.json','17-worker.json']:
  d=json.load(open(f)); print(f); print(json.dumps(d,indent=1)[:5000]); print('-----')
"
```

> 16-reviewer-plan.json
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39056872436",
>  "commit_before": "a8c77ef230df88dadb93c89171a617f648f459a6",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 576815,
>   "turns": 16,
>   "cost_usd": 0.6625922000000001,
>   "tokens_in": 755282,
>   "tokens_out": 4593
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/812/39056872436-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39056872436",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Added a check that each shared workflow fetches Dokima's code at the called commit."
>    ],
>    "decided": [
>     "The check fills in the values GitHub sets when an adopter calls a shared workflow."
>    ],
>    "open": [
>     "The shared workflows still fetch Dokima's code from main; the worker fixes this next."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan now proves the adopter's tag picks the code that runs; the new check fails today for that reason.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
>     "source": "https://github.com/dokima-dev/dokima/issues/742",
>     "criterion": "812.1"
>    },
>    {
>     "ask": "live only in GitHub secrets on the repo (the `keys` environment)",
>     "source": "https://github.com/dokima-dev/dokima/issues/742",
>     "criterion": "812.2"
>    },
>    {
>     "ask": "`settings.yaml` only names wh

**Agent:** Checking the planner's latest change and running its tests.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; git show fd19bfa --stat; git show fd19bfa -- tests/ | head -80; timeout 600 python -m pytest -q -p no:cacheprovider tests/test_queue_judge.py tests/test_thin_install.py 2>&1 | tail -15
```

> commit fd19bfaf04b92bcd7bee5eab53538d60b5fde58f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 18:58:11 2026 +0000
> 
>     planner for #812 (run 39059633295)
>     
>     Co-authored-by: {bot}
> 
>  tests/test_queue_judge.py | 5 +++--
>  1 file changed, 3 insertions(+), 2 deletions(-)
> commit fd19bfaf04b92bcd7bee5eab53538d60b5fde58f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 18:58:11 2026 +0000
> 
>     planner for #812 (run 39059633295)
>     
>     Co-authored-by: {bot}
> 
> diff --git a/tests/test_queue_judge.py b/tests/test_queue_judge.py
> index 0611079..2d4576a 100644
> --- a/tests/test_queue_judge.py
> +++ b/tests/test_queue_judge.py
> @@ -14,8 +14,8 @@ Every job of the real acceptance-criteria.yml (list, check once per row of the l
>  by default on pull_request_target), other `uses:` steps are skipped, every `run:` script runs with bash, its `${{ }}`
>  filled in, with a `pip` that does nothing and a `pytest` that runs this machine's pytest. The repo is Dokima's own, so
>  a checkout of dokima-dev/dokima (#812) copies these trees too, only the folders a sparse checkout names; the commit
> -of the workflow file that runs (`github.workflow_sha`, and `github.job_workflow_sha` as no other repo calls it) is the
> -event's own commit, as GitHub gives it. Each step
> +of the workflow file that runs (`github.workflow_sha`, and the called file's own `job.workflow_sha` as no other repo
> +calls it) is the eve

`10. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -p no:cacheprovider -n auto -x 2>&1 | tail -8
```

> tests/test_test_clash_planner.py:33
> tests/test_test_clash_planner.py:33
> tests/test_test_clash_planner.py:33
>   /home/runner/work/dokima/dokima/tests/test_test_clash_planner.py:33: PytestCollectionWarning: cannot collect test class 'TestClash' because it has a __init__ constructor (from: tests/test_test_clash_planner.py)
>     class TestClash(ts.Machine):
> 
> -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
> 1437 passed, 4 warnings in 353.55s (0:05:53)

`11. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
old=json.load(open('in/16-reviewer-plan.json'))['handback']
plan=json.load(open('plan.json'))
tests={t['test']:t for t in old['tests']}
out=[]
for c,ts in plan['tests'].items():
    for t in ts:
        out.append(tests.get(t,{"test":t,"only_its_behavior":True,"why":"Checks only its criterion's behavior."}))
r={
 "previous_step":{"did":["Gave the queue judge's fake run the called commit, as GitHub sets it."],
   "decided":["The plan's criteria and tests stay as approved before."],
   "open":["The worker reruns the queue judge tests against the built code."]},
 "verdict":"approve",
 "summary":"The planner fixed the queue test that could not pass; the whole suite is green on this branch.",
 "raises":[],"answers":[],
 "asks":old['asks'],"behaviors":old['behaviors'],"edge_cases":old['edge_cases'],
 "tests":out,"size":"ok",
 "boxes":{"dropped":"none","added":"none","superseded":"none","conflicts":"none",
   "edges":{c:"covered" for c in plan['tests']},"poor_tests":"none"}}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
print(len(out))
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> 13
> rc=0

**Agent:** I approved the plan for [#812](https://github.com/dokima-dev/dokima/issues/812) (Dokima's workflows run from Dokima's own repo).

- **What changed:** the planner fixed one helper in `tests/test_queue_judge.py`. Its fake run now supplies the called commit the way GitHub does. That clears the earlier "test cannot pass" blocker. Nothing the test proves was weakened.
- **Rest of the plan:** the 10 criteria and their tests are the same as the plan approved last time. Every ask from the owner still maps to a criterion.
- **Test run:** the full suite passes on this branch, 1437 tests.
- **Not re-checked:** I didn't rerun the new tests on main to confirm they fail there today. The earlier plan review confirmed that, and those tests haven't changed since.
- **Raises:** none were open for me to answer, and I raised none.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

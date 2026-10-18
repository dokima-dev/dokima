# reviewer (plan) for #863

Run: https://github.com/dokima-dev/dokima/actions/runs/39108927315

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (36.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/df8bfc4e-b80f-4775-91de-fff3342c4b77/tool-results/b8dow98qo.txt
> 
> Preview (first 2KB):
> # Issue #863: Hotfix issues build from their text and get reviewed
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [864], "loop": []} -->
> An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/868 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/868/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/864
> - https://github.com/dokima-dev/dokima/issues/869
> - https://github.com/dokima-dev/dokima/issues/870
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/748
> 
> 
> **User story:** A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-crit

`2. Bash`
```
cd /tmp/pack; sed -e 's/<img[^>]*>//g' issue.md | head -c 20000
```

> # Issue #863: Hotfix issues build from their text and get reviewed
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [864], "loop": []} -->
> An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/868 ·  [files changed](https://github.com/dokima-dev/dokima/pull/868/files)
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/864
> - https://github.com/dokima-dev/dokima/issues/869
> - https://github.com/dokima-dev/dokima/issues/870
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/748
> 
> 
> **User story:** A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** When a code owner says work on an issue labeled hotfix, the worker starts with no plan.
>   *<a href="https://github.com/dokima-dev/dokima/blob/e3ac23ccbc031c74929ed71ec16956d0a5bcd02c/tests/test_hotfix.py#L239"> Acceptance test</a>: A code owner's `/work` on a hotfix issue with no plan starts its worker.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/e3ac23ccbc031c74929ed71ec16956d0a5bcd02c/tests/test_hotfix.py#L239">An issue without the label and with no plan still starts no worker.</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246479912
> -  **Acceptance criteri

`3. Bash`
```
cd /tmp/pack; ls in; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1)[:12000])"
```

> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-worker.json
> 06-reviewer-pr.json
> 07-planner.json
> []{
>  "kind": "user_story",
>  "title": "Hotfix issues build from their text and get reviewed",
>  "summary": "An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.",
>  "user_story": "A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.",
>  "acceptance_criteria": [
>   {
>    "text": "When a code owner says work on an issue labeled hotfix, the worker starts with no plan.",
>    "words": "By hand, the owner's `/work` starts a hotfix's worker.",
>    "source": "https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246479912",
>    "files": [
>     ".github/workflows/agent.yml",
>     "dokima/agent_roles.py",
>     "dokima/hotfix.py",
>     "dokima/defaults.yaml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An issue without the label and with no plan still starts no worker.",
>      "test": "tests/test_hotfix.py::test_work_on_a_hotfix_starts_its_worker_with_no_plan"
>     }
>    ]
>   },
>   {
>    "text": "When an issue labeled hotfix has no open blocker on autopilot, its worker starts instead of its planner.",
>    "words": "When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text",
>    "source": "https://github.com/dokima-dev/dokima/issues/750",
>    "files": [
>     "dokima/agent_autopilot.py",
>     "dokima/hotfix.py",
>     "dokima/default

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/07-planner.json'));print(json.dumps(d,indent=1)[:4000])"; cd /home/runner/work/dokima/dokima; git log --oneline -8 --stat | head -60; git diff main --stat
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39108653998",
>  "commit_before": "e3ac23ccbc031c74929ed71ec16956d0a5bcd02c",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 163153,
>   "turns": 9,
>   "cost_usd": 0.5356168,
>   "tokens_in": 453979,
>   "tokens_out": 3121
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/863/39108653998-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39108653998",
>  "handback": {
>   "kind": "user_story",
>   "title": "Hotfix issues build from their text and get reviewed",
>   "summary": "An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.",
>   "user_story": "A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.",
>   "acceptance_criteria": [
>    {
>     "text": "When a code owner says work on an issue labeled hotfix, the worker starts with no plan.",
>     "words": "By hand, the owner's `/work` starts a hotfix's worker.",
>     "source": "https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246479912",
>     "files": [
>      ".github/workflows/agent.yml",
>      "dokima/agent_roles.py",
>      "dokima/hotfix.py",
>      "dokima/defaults.yaml"
>     ],
>     "edge_cases": [
>      {
>       "case": "An issue without the label and with no plan still starts no worker.",
>       "test": "tests/test_hotfix.py::test_work_on_a_hotfix_starts_its_worker_with_no_plan"
>      }
>     ]
>    },
>    {
>     "text": "When

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline main -5; git merge-base main HEAD; git show main --stat | head -30; git diff HEAD main -- dokima/checks.py dokima/defaults.yaml .github/workflows/acceptance-criteria.yml
```

> 250a847 Pull requests with no plan pass unless Dokima opened them (#865)
> 3dca75c The card follows the repo's own CI (#866)
> 8db728a The audit spares the repo's checks and a missing board (#861)
> ccbebe2 An empty repo reaches its first merge from the docs (#856)
> 8f381b7 Card and branch updates find checks by shown names (#852)
> 3dca75cbcd8d9c6d02ebcdc957d77da09ebdc4bc
> commit 250a847648496540fb72f45b2c1449e1c24f2e9f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 07:32:26 2026 +0000
> 
>     Pull requests with no plan pass unless Dokima opened them (#865)
>     
>     * planner for #857 (run 39102757741)
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
>     
>     * worker for #857 (run 39104217454)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     ---------
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  .github/workflows/acceptance-criteria.yml |   1 +
>  dokima/checks.py                          |  16 +++-
>  dokima/defaults.yaml                      |   2 +
>  tests/test_manual_fix_check.py            |  10 +--
>  tests/test_test_settings.py               |  13 +--
>  tests/test_unplanned_prs.py               | 143 ++++++++++++++++++++++++++++++
>  6 files changed, 173 insertions(+), 12 deletio

**Agent:** Re-plan after a merge conflict. Comparing the new plan to the approved one, then running the tests.

`6. Bash`
```
cd /tmp/pack; python3 - <<'E'
import json
a=json.load(open('in/03-planner.json'))['handback'];b=json.load(open('plan.json'))
for k in b:
    if a.get(k)!=b.get(k): print("DIFF",k)
for x,y in zip(a['acceptance_criteria'],b['acceptance_criteria']):
    if x!=y: print(json.dumps(x)[:600]);print(json.dumps(y)[:600])
E
python3 -c "
import json;d=json.load(open('in/04-reviewer-plan.json'));print(json.dumps(d['handback'].get('asks'),indent=0))"
```

> DIFF links
> DIFF answers
> [
> {
> "ask": "An issue labeled `hotfix` skips planning and plan review.",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.2"
> },
> {
> "ask": "By hand, the owner's `/work` starts a hotfix's worker.",
> "source": "https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246479912",
> "criterion": "863.1"
> },
> {
> "ask": "When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.2"
> },
> {
> "ask": "the text is the whole ask.",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.3"
> },
> {
> "ask": "Code review still runs and judges the diff against the issue's text",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.6"
> },
> {
> "ask": "All tests and the merge gate still run, as for any pull request.",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.7"
> },
> {
> "ask": "The worker may add or change a small test that pins the fix",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.4"
> },
> {
> "ask": "When code review finds the change bigger than the ask",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.8"
> },
> {
> "ask": "it goes back to normal planning, saying why.",
> "source": "https://github.com/dokima-dev/dokima/issues/750",
> "criterion": "863.9"
> },
> {
> "ask": "keep the p

`7. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt main 2>&1|tail -1; cp tests/test_hotfix.py /tmp/mainwt/tests/; cd /tmp/mainwt && timeout 600 python3 -m pytest -q tests/test_hotfix.py -x -q 2>&1 | tail -5; timeout 600 python3 -m pytest -q tests/test_hotfix.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | head -20
```

> assert False
>  +  where False = agent_started()
>  +    where agent_started = <test_hotfix.Hotfix object at 0x7fe6760e3530>.agent_started
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> E       AssertionError: 863.1: `/work` on a hotfix issue with no plan did not start its worker; result failure, failed step 'Starting branch':
>         assert not m.failed, f"863.2 (close): a workflow failed when #110 closed: {m.failures}\n{m.tail()}"
> E       AssertionError: 863.3: the hotfix worker never started; result failure, failed step 'Starting branch':
> >       assert not r.failed, f"863.4: the hotfix worker's run failed; {r.why()}"
> E       AssertionError: 863.4: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E        +  where True = <test_hotfix.Hotfix object at 0x7fd878de5fd0>.failed
> >       assert not r.failed, f"863.5: the hotfix worker's run failed; {r.why()}"
> E       AssertionError: 863.5: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E        +  where True = <test_hotfix.Hotfix object at 0x7fd87a568500>.failed
> E       AssertionError: 863.6: code review of the hotfix never started; result failure, failed step 'Build the starting pack':
> E         ::error title=No pack::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
> E         ::error title=Not started::No passed plan on the issue yet, or (for the worker) no plan review approving the newest pla

`8. Bash`
```
cd /tmp/mainwt && timeout 900 python3 -m pytest -q tests/test_hotfix.py -rA 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed" | tail -15
```

> +  where True = <test_hotfix.Hotfix object at 0x7fce735f7230>.failed
> FAILED tests/test_hotfix.py::test_code_review_of_a_hotfix_gets_the_issue_text_as_the_ask - AssertionError: 863.6: code review of the hotfix never started; result failure, failed step 'Build the starting pack':
>   ::error title=No pack::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
>   ::error title=Not started::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
> FAILED tests/test_hotfix.py::test_an_approved_hotfix_passes_the_merge_gate_like_any_pull_request - AssertionError: 863.7: the approving hotfix review did not post one passed record: [('not-started', {'passed': False, 'problems': ['No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.']})]; result failure, failed step 'Build the starting pack':
>   ::error title=No pack::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
>   ::error title=Not started::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
> FAILED tests/test_hotfix.py::test_code_review_sends_a_too_big_hotfix_to_the_planner - AssertionError: 863.8: the blocking hotfix review did not post one passed record; result failure, failed step 'Build the starting pack':
>   ::error title=No pack::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
>   :

`9. Bash`
```
timeout 900 python3 -m pytest -q tests/test_hotfix.py 2>&1 | tail -3; git worktree remove --force /tmp/mainwt
```

> ..........                                                               [100%]
> 10 passed in 69.13s (0:01:09)

`10. Bash`
```
cd /home/runner/work/dokima/dokima && timeout 900 python3 -m pytest -q tests/test_hotfix.py 2>&1 | tail -3; git worktree remove --force /tmp/mainwt
```

`11. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'E'
import json
asks=json.load(open('in/04-reviewer-plan.json'))['handback']['asks']
p=json.load(open('plan.json'))
ids=[f"863.{i+1}" for i in range(len(p['acceptance_criteria']))]
why={"863.1":"One action, owner's work command; one result, the worker starts.",
"863.2":"One case, an unblocked hotfix on autopilot; one result, worker not planner.",
"863.3":"One result: the worker's pack holds the issue text as the ask.",
"863.4":"One result: the worker's changes stay on the pull request.",
"863.5":"One result: code review starts when the worker finishes.",
"863.6":"One result: the review pack holds the issue text as the ask.",
"863.7":"One result: an approved hotfix with passing checks passes the gate.",
"863.8":"One result: a too big hotfix starts the planner.",
"863.9":"One result: a comment saying why on the issue.",
"863.10":"One result: both hotfix prompts name nothing of Dokima's repo."}
tests=[{"test":p['tests'][i][0],"only_its_behavior":True,"why":"Runs the real flow and checks only "+i+"'s result, with its named edge cases."} for i in ids]
r={"previous_step":{"did":["The planner planned the issue again after main changed under its pull request.","It kept the same ten criteria and the same tests."],
"decided":["The hotfix gate still passes only for approved hotfixes, beside main's new unplanned rule."],
"open":["The worker must bring the hotfix gate in line with main's new unplanned check."]},
"verdict":"approve",
"summary":"The plan is unchanged after the clash with main; all ten tests still fail on main for the missing feature.",
"raises":[],"answers":[],"asks":asks,
"behaviors":[{"criterion":i,"one_behavior":True,"why":why[i]} for i in ids],
"edge_cases":[{"criterion":i,"cut":[],"missing":[]} for i in ids],
"tests":tests,"size":"ok",
"boxes":{"dropped":"none","added":"none","superseded":"none","conflicts":"none",
"edges":{i:"covered" for i in ids},"poor_tests":"none"}}
json.dump(r,open('/tmp/dokima-out/rev
```

> (Bash completed with no output)

`12. Bash`
```
cd /tmp/pack; python3 -c "
import json;a=json.load(open('in/03-planner.json'))['handback'];print(a['links'],a['answers'])"
```

> {'blocked_by': [], 'blocks': [864], 'relates_to': [748, 857]} [{'raise': 'R1', 'answer': 'done', 'why': 'The gate test now also runs a red check, which must fail the gate and restart the worker.'}, {'raise': 'R2', 'answer': 'done', 'why': "New criterion 863.10 checks both hotfix prompts name nothing from Dokima's own repo."}]
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Fixing one summary line so it only states what the planner actually did, then rechecking.

`13. Bash`
```
cd /tmp/dokima-out; python3 - <<'E'
import json
r=json.load(open('review.json'))
r['previous_step']['decided']=["It now lists the two issues the worker filed as waiting on this one."]
r['previous_step']['open']=["The worker must merge its hotfix check with main's new check for unplanned pull requests."]
json.dump(r,open('review.json','w'),indent=1)
E
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 863 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan, and the hand-back is in `/tmp/dokima-out/review.json`. Both checks on the hand-back pass.

- **What changed:** after main moved, the planner planned again because of the clash in `dokima/checks.py`. It kept the same ten criteria and tests. The only change is that the plan now says [#869](https://github.com/dokima-dev/dokima/issues/869) (switch comment says planning) and [#870](https://github.com/dokima-dev/dokima/issues/870) (rules omit the hotfix lane) wait on this issue.
- **Tests on main:** all 10 tests in `tests/test_hotfix.py` fail because the hotfix feature is missing, not because of a crash or a bad path. For example: "No passed plan on the issue yet", and "`/work` on a hotfix issue with no plan did not start its worker".
- **Tests on this branch:** all 10 pass with the worker's earlier code.
- **Owner's asks:** each of the 10 asks from [#750](https://github.com/dokima-dev/dokima/issues/750) (the hotfix label) still maps to one criterion. Nothing was dropped or added.
- **Plan's size:** every criterion is one behavior, and no edge cases are missing.
- **Open questions:** none; I raised nothing new.

When the worker rebuilds, it has to fit its hotfix check into `dokima/checks.py` alongside main's new rule for pull requests with no plan, from [#865](https://github.com/dokima-dev/dokima/pull/865) (unplanned pull requests pass).

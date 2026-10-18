# reviewer (plan) for #857

Run: https://github.com/dokima-dev/dokima/actions/runs/39104134707

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #857: Pull requests with no plan pass unless Dokima opened them
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> People and Dependabot can merge without a Dokima plan; Dokima's own pull requests still need one.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/744
> 
> 
> **User story:** People and Dependabot merge pull requests without a Dokima plan, while Dokima's own stay held to theirs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a person opens a pull request with no approved plan, the Acceptance criteria check passes.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-857/tests/test_unplanned_prs.py#L82"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: A person's pull request with no approved plan passes the Acceptance criteria check.*
>   <details><summary><picture><img src="https://r

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cd /home/runner/work/dokima/dokima; cat tests/test_unplanned_prs.py; git diff main --stat
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39103909518",
>  "commit_before": "0ac83904b54c6081d3e5d03f9e559df3ddb99e50",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 81180,
>   "turns": 10,
>   "cost_usd": 0.44487079999999996,
>   "tokens_in": 396072,
>   "tokens_out": 5051
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/857/39103909518-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39103909518",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote four criteria and four new tests, one per criterion.",
>     "The planner loosened three older tests so unplanned pull requests may pass."
>    ],
>    "decided": [
>     "Only the value allow lets unplanned pull requests through; block is tested as another value."
>    ],
>    "open": [
>     "The plan names no change to the merge check's workflow file."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The tests are right, but the plan leaves out the workflow file the issue says must change.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Scope misses a file",
>     "text": "For 857.1 and 857.2, a passing no-plan row needs its own exit in the workflow, as the issue says. Add `.github/workflows/acceptance-criteria.yml` to those criteria's files.",
>     "evidence": "`.github/workflows/acceptance-criteria.yml:118` fails any row with no tests except `text-only` and `manual-fix`.",
>     "raised_by": "r

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main -- tests/test_manual_fix_check.py tests/test_test_settings.py; pytest -q tests/test_unplanned_prs.py 2>&1 | grep -E "^(FAILED|E  +AssertionError|[0-9]+ )|passed|failed" | head -20
```

> diff --git a/tests/test_manual_fix_check.py b/tests/test_manual_fix_check.py
> index bc9b846..5a224c4 100644
> --- a/tests/test_manual_fix_check.py
> +++ b/tests/test_manual_fix_check.py
> @@ -132,16 +132,16 @@ def test_a_manual_fix_check_fails_when_a_test_fails(record_property, tmp_path):
>  
>  
>  def test_only_dokimas_app_gets_the_manual_fix_check(record_property, tmp_path):
> -    """A pull request with no issue, opened by anyone else, still fails.
> +    """A pull request with no issue, opened by anyone else, gets no manual fix check.
>  
> -    Proves 643.3. Runs the matrix command for the same code change twice: opened by a person, it must get only the failing
> -    no-plan check; opened by Dokima's app, it must get the manual fix check instead. Since 2026-10-17 every manual fix
> +    Proves 643.3. Runs the matrix command for the same code change twice: opened by a person, it must not get the manual
> +    fix check (since #857 it may pass as an unplanned pull request); opened by Dokima's app, it must get the manual fix check instead. Since 2026-10-17 every manual fix
>      names the issue it fixes (owner, #830), so one by Dokima's app from its fix branch naming an issue still gets the
>      manual fix check; a planned build from try/issue-N with no approved plan still fails (830.7)."""
>      record_property("proves", "643.3")
>      rows, output = run_matrix(tmp_path, OWNER)
> -    assert rows == [{"id": "none", "name": NO_ISSUE, "tests": ""}], \
> -        f"643.3: a pull request a person opened with

`4. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
prev=json.load(open('in/02-reviewer-plan.json'))['handback']
r={k:prev[k] for k in ['asks','behaviors','edge_cases','tests','size','boxes']}
r['previous_step']={"did":["The planner added the merge check's workflow file to criteria 857.1 and 857.2."],
 "decided":["The criteria, tests and older test changes stay as before."],"open":[]}
r['verdict']='approve'
r['summary']="The plan now names every file it needs, and all four new tests fail today for the right reason."
r['raises']=[];r['answers']=[]
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 857 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#857](https://github.com/dokima-dev/dokima/issues/857) (pull requests with no plan pass unless Dokima opened them), and the hand-back passed both checks.

- **Last round's blocker is fixed:** criteria 857.1 and 857.2 now list the merge check's workflow file. The issue asks for that change itself, so editing the workflow is allowed here.
- **New tests:** I ran all four. Each fails today for the right reason: a person's or Dependabot's pull request with no plan still gets the "No approved plan found" failure, or the setting isn't recognised yet.
- **Older tests:** the three changed tests only drop the old promise that a person's unplanned pull request must fail. The owner removed that behavior in [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety: human pull requests pass). Each test still checks what it was there for:
  - only Dokima gets the manual-fix check;
  - a file under `.github/` and the folders the settings list don't take the text-only shortcut.
- **Owner's asks:** each one maps to a criterion. Nothing is dropped, added or in conflict.

No open raises were waiting for an answer, and I raised nothing new. The review is in `/tmp/dokima-out/review.json`.

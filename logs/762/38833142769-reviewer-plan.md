# reviewer (plan) for #762

Run: https://github.com/dokima-dev/dokima/actions/runs/38833142769

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
> # Issue #762: The fence reads its scope only from the plan file
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 765 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Deletes the fence's old reader of a scope written in the issue's text.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> - https://github.com/dokima-dev/dokima/issues/761
> - https://github.com/dokima-dev/dokima/issues/765
> 
> 
> **User story:** The fence takes its scope only from the plan file, as every run already passes it.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The fence no longer reads its scope from the issue's text.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-762/tests/test_fence_plan_only.py#L34"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/owner_words.json /tmp/pack/parent.json | head -80; cat tests/test_fence_plan_only.py; git show --stat HEAD; cat dokima/fence.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/739": "Part of the portability plan (#272).\n\nCode left over from the old label flow (removed in #516) and from Dokima's own repo. Nothing on main calls it; each item was checked with a grep of dokima/, .github/workflows/ and tests/ at f71d144. Delete it, plus the tests that only exercise it.\n\n**Old label flow**\n- `dokima/plan.py:22,141-157,164-178`: label approval (`LABEL = \"work\"`, `approved_at`, `approved_version`). `fetch_issue` still makes a paginated events call and parses edit history on every card draw and scan, and no caller reads `plan`, `changes` or `approved_at`. Keep the body and url fetch.\n- `dokima/plan.py:23`: `WORK_BRANCH`, never used.\n- `dokima/plan.py:28-124,191-203,210-213`: the checkbox plan parser (`parse`, `lines`, `changes`), `as_text` and the `plan issue` command. No workflow calls them; only tests do. Keep `approvers`.\n- `dokima/planner.py:588-607,632-640,676-685`: the `post` and `rejected` actions, `render` and `plan_text`. Workflows call only `planner check`.\n- `dokima/fence.py:17-30` and the `scope_of` branch at `:80`: reads Scope from issue text; agent.yml always passes plan.json.\n- `dokima/agent_github.py:26,72`, `dokima/card.py:655`: lookups of `work/issue-N` branches. Keep `try/issue-N`.\n- `dokima/card.py:671-673,684-687,754`: `RUN_TITLE \"worker for #N\"` and the `worker.yml` runs lookup. worker.yml no longer exists, so this is a wasted API call on every redraw.\n- `dokima/manifest.p

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_fence.py tests/test_scope_from_files.py tests/samples/tests_before_split.txt; grep -rn "scope_of" --include=*.py --include=*.yml --include=*.md . | grep -v "^./logs"; python -m pytest -q tests/test_fence_plan_only.py tests/test_fence.py tests/test_scope_from_files.py 2>&1 | tail -15
```

> commit a8cc57c28e3c2220e71b52c71c3dd17cc0e252f6
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 01:04:22 2026 +0000
> 
>     planner for #762 (run 38831589302)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/samples/tests_before_split.txt b/tests/samples/tests_before_split.txt
> index 46e4e1b..b07baa3 100644
> --- a/tests/samples/tests_before_split.txt
> +++ b/tests/samples/tests_before_split.txt
> @@ -479,7 +479,6 @@ tests/test_feature_check.py::test_a_story_criterion_that_is_not_an_object_is_rej
>  tests/test_feature_check.py::test_a_story_criterion_that_is_not_an_object_is_rejected_not_crashed[item3]
>  tests/test_fence.py::test_tampering_is_undone_and_in_scope_work_survives
>  tests/test_fence.py::test_an_honest_build_is_untouched
> -tests/test_fence.py::test_scope_is_read_from_the_plan
>  tests/test_field_icons.py::test_every_field_has_its_own_octicon_in_the_status_icon_style[planner]
>  tests/test_field_icons.py::test_every_field_has_its_own_octicon_in_the_status_icon_style[worker]
>  tests/test_field_icons.py::test_every_field_has_its_own_octicon_in_the_status_icon_style[plan review]
> diff --git a/tests/test_fence.py b/tests/test_fence.py
> index 23858da..ce3fec6 100644
> --- a/tests/test_fence.py
> +++ b/tests/test_fence.py
> @@ -6,7 +6,7 @@ import sys
>  sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
>  from dokima import fence  # noqa: E402
>  
> -ISSUE = "Plan text.\

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "fence" rules/*.md .github/workflows/*.yml | head; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d,indent=1)[:2500])"
```

> .github/workflows/agent.yml:164:            # the clashed files are listed for the fence, and the worker resolves them. Main's changes are in BASE.
> .github/workflows/agent.yml:370:          if ! python3 -m dokima.fence "$BASE" "$PACK/plan.json" /tmp/clashed.txt > "$OUT/dropped.txt" 2> /tmp/fence-err.txt; then
> .github/workflows/agent.yml:371:            cat /tmp/fence-err.txt | tee -a "$OUT/check.txt"; echo "PASSED=false" >> "$GITHUB_ENV"
> .github/workflows/agent.yml:372:            echo "::error title=Fence::$(paste -sd' ' /tmp/fence-err.txt)"
> .github/workflows/agent.yml:374:          [ -s "$OUT/dropped.txt" ] && echo "::warning title=Dropped by the fence::$(paste -sd, "$OUT/dropped.txt")" || true
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38831589302",
>  "commit_before": "e05e426b73487841e18151b08976155d7ab4ae5c",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 59190,
>   "turns": 8,
>   "cost_usd": 1.1180257999999998,
>   "tokens_in": 587832,
>   "tokens_out": 2443
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/762/38831589302-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38831589302",
>  "handback": {
>   "kind": "user_story",
>   "title": "The fence reads its scope only from the plan",
>   "summary": "Deletes the fence's old reader of a scope written in the issue's text.",
>   "user_story": "The fence takes its scope only from the plan file, as every run already passes it.",
>   "accepta

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria, one test each, and both fail today.",
          "The planner deleted the one test of the old reader and moved two fence tests off it."],
  "decided": ["The fence takes its scope only from the plan file."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries both asks of story three, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "`dokima/fence.py:17-30` and the `scope_of` branch at `:80`: reads Scope from issue text; agent.yml always passes plan.json.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "762.1"},
  {"ask": "Delete it, plus the tests that only exercise it.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "762.2"}
 ],
 "behaviors": [
  {"criterion": "762.1", "one_behavior": true, "why": "One result: the issue's text no longer sets the fence's scope."},
  {"criterion": "762.2", "one_behavior": true, "why": "One result: no test of the deleted reader is left."}
 ],
 "edge_cases": [
  {"criterion": "762.1", "cut": [], "missing": []},
  {"criterion": "762.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_fence_plan_only.py::test_the_fence_ignores_a_scope_in_the_issue_text", "only_its_behavior": true, "why": "Runs the fence on issue text, fails today as it keeps the change; plan file still works."},
  {"test": "tests/test_fence_plan_only.py::test_the_issue_text_reader_and_its_tests_are_gone", "only_its_behavior": true, "why": "Fails today naming the fence file; passes only once no code or test names the reader."}
 ],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 762 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

**Agent:** Approving the plan; one summary line is two words over its cap, so I'm trimming it.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner deleted the one test of the old reader and moved two fence tests off it./The planner deleted the old reader'"'"'s one test and moved two tests off it./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 762 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#762](https://github.com/dokima-dev/dokima/issues/762) (fence reads its scope only from the plan file). I raised no blockers, and both checks on the review file pass.

- **Asks covered:** [#739](https://github.com/dokima-dev/dokima/issues/739) (delete dead code from the old label flow) asks two things for this part, and each one has a criterion:
  - stop the fence reading its scope from the issue's text (762.1);
  - delete the tests that only check that old reader (762.2).
- **New tests fail today for the right reasons:**
  - The 762.1 test fails because the fence still reads the issue's text and keeps a change only that text lists. The same test also checks that a plan file still works.
  - The 762.2 test fails because the old reader is still in the fence's code.
- **Tests the planner changed:** they deleted the one test that only checked the old reader. They switched three other tests to take the scope directly, not through the old reader. Those three still pass.
- **Size:** each criterion is one behavior with one test.

The review is in `/tmp/dokima-out/review.json`.

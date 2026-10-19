# reviewer (plan) for #886

Run: https://github.com/dokima-dev/dokima/actions/runs/39184790552

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #886: The baseline passes on a repo with no tests
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo with no tests yet passes the testmon baseline, and the run says so.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/887
> 
> 
> **User story:** An owner with no tests yet sees the baseline pass, told the repo has no tests yet.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the baseline runs on a repo with no tests, it succeeds and saves an empty baseline.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-886/tests/test_no_tests_yet.py#L36"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: The testmon baseline on an empty tests folder succeeds and saves an empty baseline.*
>   

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -200; cat open_issues.json | head -50; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:5000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/880": "`testmon.yml` runs `python3 -m pytest -q --testmon || [ $? -eq 1 ]`, so only pytest's exit code 1 (tests failed) is tolerated. A repo with no tests yet makes pytest exit 5 (\"no tests collected\"); the baseline job fails and then fails again on \"pytest --testmon wrote no .testmondata\". An adopter starting from zero tests is a normal first day, and the first planned issue is what adds the first test.\n\n**Ask:** treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline and wherever the full suite would hit the same exit code; say on the run that the repo has no tests yet. A test should run the baseline step on an empty tests folder and expect success.\n\n(Filed by Claude for Reza, at his request.)\n",
>  "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677": "/work Rebuild on main as it is now. #877 (PR #878) merged and changed the same testmon line: the baseline now runs `python3 -m pytest -q --testmon \"${TESTS_DIR:-tests}\"`. Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand. The approach is right: a real `pytest --testmon` on an empty tests folder exits 5 and still writes a non-empty `.testmondata` (checked on a live machine), so the next step's baseline check passes.\n\n(Answered by Claude for Reza, at his request: \"settle technical details yourself\".)\n"
> }{"number": 880}[
>  {
>   "number": 887,
>   "title": "The all tests check passe

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/ ; cat .github/workflows/testmon.yml
```

> commit 1bc6fdf9349e1f456c1310416340db9aa29f4f19
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 01:18:29 2026 +0000
> 
>     planner for #886 (run 39184553273)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_no_tests_yet.py | 65 ++++++++++++++++++++++++++++++++++++++++++++++
>  tests/test_testmon.py      | 38 +++++++++++++++++++++------
>  2 files changed, 95 insertions(+), 8 deletions(-)
> commit 1bc6fdf9349e1f456c1310416340db9aa29f4f19
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 01:18:29 2026 +0000
> 
>     planner for #886 (run 39184553273)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_no_tests_yet.py b/tests/test_no_tests_yet.py
> new file mode 100644
> index 0000000..c976902
> --- /dev/null
> +++ b/tests/test_no_tests_yet.py
> @@ -0,0 +1,65 @@
> +"""Tests for #886: a repo with no tests yet passes the testmon baseline.
> +
> +pytest exits 5 when it collects no tests. Each test runs a real job of a workflow on a temp repo whose tests folder is
> +empty, through tests/test_settings_workflows.py's machine, with real pytest. `python3 -m pytest --testmon` runs real
> +pytest without testmon and leaves a baseline file, as pytest-testmon 2.2 does even when no test ran (checked by hand).
> +"""
> +import os
> +import sys
> +
> +sys.path.insert(0, os.path.dirname(__file__))
> +f

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_no_tests_yet.py "tests/test_testmon.py::test_baseline_runs_only_the_tests_folder" 2>&1 | tail -30
```

> tests/test_no_tests_yet.py:59: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_no_tests_yet.py::test_the_baseline_passes_on_an_empty_tests_folder - AssertionError: 886.1: the baseline failed on a repo with no tests yet:
>   ## baseline: Install the test tools and the repo itself (exit 0)
>   
>   ## baseline: Affected tests from the settings (exit 0)
>   
>   ## baseline: None (exit 1)
>   
>   no tests ran in 0.00s
>   
> assert 'failure' == 'success'
>   
>   - success
>   + failure
> FAILED tests/test_no_tests_yet.py::test_the_baseline_says_the_repo_has_no_tests_yet - AssertionError: 886.2: the baseline does not say the repo has no tests yet:
>   ## baseline: Install the test tools and the repo itself (exit 0)
>   
>   ## baseline: Affected tests from the settings (exit 0)
>   
>   ## baseline: None (exit 1)
>   
>   no tests ran in 0.00s
>   
> assert 'No tests yet' in "## baseline: Where Dokima's code is (exit 0)\n\n## baseline: None (exit 0)\n\n## baseline: None (exit 0)\n\n## baseli... 0)\n\n## baseline: Affected tests from the settings (exit 0)\n\n## baseline: None (exit 1)\n\nno tests ran in 0.00s\n"
>  +  where "## baseline: Where Dokima's code is (exit 0)\n\n## baseline: None (exit 0)\n\n## baseline: None (exit 0)\n\n## baseli... 0)\n\n## baseline: Affected tests from the settings (exit 0)\n\n## baseline: None (exit 1)\n\nno tests ran in 0.00s\n" = <built-in method join of str object at 0x7f0ec842b720>(["## baseline: Where Dokima's code is (exit

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "::notice\|cache-saved\|def lines\|def tail\|self.log" tests/test_settings_workflows.py | head -40; grep -rn "::notice" tests/*.py | head -10
```

> 157:    def lines(self):
> 186:            keep["run"] = 'echo "cache-saved" >> "$SETUP_LOG"\n'
> 335:    assert "cache-saved" not in lines, f"795.3: with affected tests set to all, main still saved a baseline; log {lines}"
> 342:    assert "cache-saved" in box.lines(), f"795.3: with no settings file main no longer saves a baseline; log {box.lines()}"
> tests/test_checks.py:76:    assert ok.startswith("::notice file=tests/t.py,line=5,title=40.1 passed::")

**Agent:** Both new tests fail today for the right reason (the step fails on exit 5). Now checking whether the notice test only checks a word.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 100,260p tests/test_settings_workflows.py
```

> else:
>             ts.sh(src, "git", "checkout", "-q", branch)
>         for path, text in files.items():
>             os.makedirs(os.path.dirname(f"{src}/{path}") or src, exist_ok=True)
>             open(f"{src}/{path}", "w").write(text)
>         ts.sh(src, "git", "add", "-A")
>         ts.sh(src, "git", "commit", "-qm", message)
>         ts.sh(src, "git", "push", "-q", "origin", branch)
>         return ts.sh(src, "git", "rev-parse", "HEAD")
> 
>     def context(self, role="planner", stage="", event="workflow_dispatch", actor=ts.OWNER, tests="tests/test_x.py::test_a"):
>         """The GitHub contexts one run sees."""
>         pr = {"number": 60, "draft": False, "head": {"sha": ""}}
>         github = Ctx(event_name=event, actor=actor, event=Ctx(pull_request=pr), run_id="42", run_attempt="1", sha="",
>                      server_url="https://github.com", repository="o/r", repository_owner="o", token="fake-github-token",
>                      ref="refs/heads/main", ref_name="main")
>         return {"inputs": Ctx(role=role, stage=stage, issue=N, branch=f"fix/issue-{N}-typo"), "github": github,
>                 "client_payload": Ctx(), "matrix": Ctx(tests=tests, id="9.1", name="9.1"),
>                 "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
>                 "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
> 
>     def run(self, file, job, steps=None, name=None, env=None, **context):
>         """Run JOB of workflow FILE, or only STEPS, on a fresh clone; its result.
> 
>   

`7. Bash`
```
cd /tmp && rm -rf cfx && mkdir -p cfx/tests && cd cfx && echo "raise RuntimeError('x')" > tests/conftest.py && python3 -m pytest -q -p no:testmon tests >/dev/null 2>&1; echo $?; mkdir -p ../cfy/tests; cd ../cfy; python3 -m pytest -q -p no:testmon tests >/dev/null 2>&1; echo $?
```

> 4
> 5
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Planned three criteria for the baseline on a repo with no tests.", "Added two tests that run the baseline on an empty tests folder."],
  "decided": ["The full suite part of the ask is left to its sibling issue."],
  "open": ["The notice test accepts any line with the words, not a notice."]
 },
 "verdict": "block",
 "summary": "The plan fits the ask, but the notice test passes without any notice on the run.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "886.2 weak test",
   "text": "886.2 promises a notice, but its test only looks for the words in the log. A plain `echo \"No tests yet\"` passes. Fix: assert a `::notice` line holding `No tests yet`.",
   "evidence": "`tests/test_no_tests_yet.py:59` checks `\"No tests yet\" in \"\\n\".join(b.log)` only."}
 ],
 "answers": [],
 "asks": [
  {"ask": "treat \"no tests collected\" as an empty baseline, not a crash, in the testmon baseline", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "886.1"},
  {"ask": "A test should run the baseline step on an empty tests folder and expect success.", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "886.1"},
  {"ask": "say on the run that the repo has no tests yet", "source": "https://github.com/dokima-dev/dokima/issues/880", "criterion": "886.2"},
  {"ask": "Keep that tests-folder argument and add the exit-5 handling on top, so both fixes stand.", "source": "https://github.com/dokima-dev/dokima/issues/880#issuecomment-6257482677", "criterion": "886.3"}
 ],
 "behaviors": [
  {"criterion": "886.1", "one_behavior": true, "why": "Baseline passes on no tests; the saved file is that same outcome."},
  {"criterion": "886.2", "one_behavior": true, "why": "One notice on one case."},
  {"criterion": "886.3", "one_behavior": true, "why": "Only the named tests folder runs."}
 ],
 "edge_cases": [
  {"criterion": "886.1", "cut": [],
```

> Exit code 1
> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts

`9. Bash`
```
sed -i 's/886.2 promises a notice, but its test only looks/886.2 promises a notice; its test only looks/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 886 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`10. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/886.2 promises a notice, but its test only looks/886.2 promises a notice; its test only looks/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 886 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I blocked the plan for [#886](https://github.com/dokima-dev/dokima/issues/886) (the baseline passes on a repo with no tests). It sends one fix back to the planner. The hand-back passes both checks and is in `/tmp/dokima-out/review.json`.

- **The plan:** its three criteria match what the owner asked for: the baseline passes on an empty tests folder, the run says the repo has no tests yet, and the run still uses the tests folder the settings name. No ask is missing.
- **The tests:** the two new ones fail today for the right reason, because the baseline step fails when pytest finds no tests. The changed older test still passes and proves the same thing as before.
- **The blocker (criterion 886.2):** the test only looks for the words "No tests yet" anywhere in the run's output. A plain line of output with those words would pass without any notice showing on the run. The fix is to require a notice line that holds those words.
- **Left to [#887](https://github.com/dokima-dev/dokima/issues/887) (the all tests check passes with no tests):** the owner's ask to handle the full suite the same way is planned there, so I didn't count it as missing here.

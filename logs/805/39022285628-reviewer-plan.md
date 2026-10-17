# reviewer (plan) for #805

Run: https://github.com/dokima-dev/dokima/actions/runs/39022285628

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
> # Issue #805: Planner's test limits and docstrings follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 804 -->
> <!-- dokima-blocking: {"blocked_by": [804], "blocks": [], "loop": []} -->
> The planner's check reads its time limit, test files and docstring rules from the repo's settings.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/804
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/783
> 
> 
> **User story:** A repo's time limit, test file pattern and docstring rules decide what the planner's check accepts.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The check that new tests fail today stops a test after the time limit setting.
>   *<a href="http

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -80; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; cat tests/test_planner_settings.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/781": "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #740, story 3</summary>\n\n**Part of:** #740 One settings file per repo over shipped defaults\n\n**User story:** A repo's own test folder, pattern and tag decide which tests Dokima finds and checks.\n\n**Context:** Rows A1 to A4, A8 to A11, E9 of the owner's list: `dokima/checks.py` `PROVES`, `TEST_DEF`, `NOT_TEXT`, `MANUAL_FIX`; `dokima/planner.py` imports `TEST_DEF` for `test_functions()`, and holds `NEW_TEST_TIMEOUT`, `DOCSTRING_CAP`, `main_with_tests()`, `passing_today()`.\n\n**Acceptance criteria:**\n- Which call links a test to its criterion is read from the test tag setting. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))\n- Dokima finds tests written as methods of a test class. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))\n- Dokima finds tests written as async functions. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))\n- Dokima finds tests indented under another block. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))\n- Changes to Dokima's prompt folder no longer stop the text-only shortcut. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))\n- The folders that stop the text-only shortcut come from settings. ([source](https://github.com/dokima-

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_planner_settings.py 2>&1 | grep -E "805\.|passed|failed|Error" | head -30; grep -n "def make_repo\|def run_check\|def named\|^JOBS\|^STORY" -A25 tests/test_test_settings.py | head -120
```

> Proves 805.1. The repo's run-one command is a runner that waits, then fails. With a time limit of 1 s and a 3 s
>         record_property("proves", "805.1")
>                     f"805.1: a test running 3 s was not stopped at the 1 s time limit setting: {why}"
> E               AssertionError: 805.1: a test running 3 s was not stopped at the 1 s time limit setting: 
> tests/test_planner_settings.py:49: AssertionError
>         Proves 805.2. The settings name `checks` as the test folder and `check_*.py` as the pattern. The planner adds
>         record_property("proves", "805.2")
> >       assert rc == 0, f"805.2: a helper outside the file pattern setting was read as a test file: {why}"
> E       AssertionError: 805.2: a helper outside the file pattern setting was read as a test file: checks/helpers.py::test_like_value is a new test with no one-sentence summary: the first line of its docstring must be one sentence on one line, ending in '.', '?' or '!'; checks/helpers.py::test_like_value is a new test that passes today (or is skipped); every new test must fail on today's code
> tests/test_planner_settings.py:76: AssertionError
>         Proves 805.3. The planner adds two failing tests with no docstrings. With `docstrings: off` written in the settings
>         record_property("proves", "805.3")
> >       assert rc == 0, f"805.3: with docstrings off in settings, the planner's check still required them: {why}"
> E       AssertionError: 805.3: with docstrings off in settings, the planner's check still req

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_planner_settings.py -k "time_limit or cap_comes" 2>&1 | grep -E "^E " | head; grep -n "NEW_TEST_TIMEOUT\|DOCSTRING_CAP\|startswith(\"tests/\")\|def unsummarized\|def unnumbered\|def docstring_caps\|settings" dokima/planner.py | head -40; grep -n "docstring\|new_test_timeout\|file_pattern\|dir:" dokima/defaults.yaml
```

> E               AssertionError: 805.1: a test running 3 s was not stopped at the 1 s time limit setting: 
> E                 [output] plan
> E                 
> E               assert (0 == 1)
> E               AssertionError: 805.4: a 7-word docstring passed a docstring cap setting of 5: 
> E                 [output] plan
> E                 
> E               assert (0 == 1)
> 26:from dokima import settings
> 31:NEW_TEST_TIMEOUT = 60  # seconds one new test may run on today's code before it is stopped and rejected
> 33:DOCSTRING_CAP = 15  # words in the first line of a docstring the planner adds
> 404:    return settings.read()["tests"]["dir"].rstrip("/") + "/"
> 436:    lines, tag = (text or "").splitlines(), proves(settings.read()["tests"]["tag"])
> 529:def unsummarized(added):
> 581:def docstring_caps(paths, before, after):
> 590:    return words.check(texts, DOCSTRING_CAP, "has a docstring whose first line holds")
> 593:def unnumbered(added):
> 624:    folder = settings.read()["tests"]["dir"]
> 642:    one = shlex.split(str(settings.read()["tests"]["run_one"]))
> 650:                                   capture_output=True, text=True, timeout=NEW_TEST_TIMEOUT)
> 652:                out.append(f"{t} is a new test still running after {NEW_TEST_TIMEOUT} s on today's code; it was stopped")
> 5:  dir: tests
> 6:  file_pattern: test_*.py
> 9:  new_test_timeout_s: 60
> 30:  docstrings: required
> 31:  docstring_cap: 15
> 32:  code_docstring_cap: 15

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "docstring" -r dokima/settings.py dokima/defaults.yaml rules/*.md | head -20; sed -n 25,35p dokima/defaults.yaml; sed -n 395,410p dokima/planner.py; sed -n 615,660p dokima/planner.py; grep -n "startswith\|endswith(\".py\")" dokima/planner.py
```

> dokima/defaults.yaml:30:  docstrings: required
> dokima/defaults.yaml:31:  docstring_cap: 15
> dokima/defaults.yaml:32:  code_docstring_cap: 15
>   branch: logs
> owner_docs: AGENTS.md
> # The Co-authored-by line on Dokima's commits, e.g. Ann Example <ann@example.com>; empty for none.
> co_author: ""
> style:
>   docstrings: required
>   docstring_cap: 15
>   code_docstring_cap: 15
>   caps:
>     summary: 20
>     user_story: 20
>     by_test = declared_by_test(declared)
>     added = {t: by_test.get(t, []) for t in tc["added"]}
>     renamed = tc.get("renamed", {})
>     changed = {t: (old, by_test.get(renamed.get(t, t), old)) for t, (old, _) in tc["changed"].items()}
>     return dict(tc, added=added, changed=changed)
> 
> 
> def tests_dir():
>     """The test folder setting, as a path prefix ending in '/'."""
>     return settings.read()["tests"]["dir"].rstrip("/") + "/"
> 
> 
> def test_nodes(tree):
>     """Each test in a parsed file, as (its name, its node).
> 
>     Tests are `test_*` functions, async or not, at any depth outside a function, and methods of `Test*` classes,
>     On a re-plan the branch may already hold the worker's code, so new tests are judged on main's code instead. The
>     copy lives outside the repo, so the branch, its worktrees and its files stay exactly as they were.
>     """
>     tar = subprocess.run(["git", "archive", "--format=tar", base], check=True, capture_output=True).stdout
>     with tempfile.TemporaryFile() as f:
>         f.write(tar)
>         f.seek(0)
>         with tarfile.open(fileobj=f) as t:
>     

**Agent:** Checking how the docstrings setting values are defined, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "docstrings" rules/ dokima/*.py docs 2>/dev/null | grep -v "^dokima/planner.py" | head; grep -n "off\|bool\|False" dokima/settings.py | head
```

> dokima/agent_checks.py:402:    Older docstrings whose first line is unchanged are left alone; a base git cannot read fails closed.
> dokima/agent_checks.py:408:        return [], [f"the docstrings the worker added can't be read: git can't compare with {base} ({e.stderr.strip()})"]

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote five criteria, one per ask from the parent plan.", "The planner wrote one test per criterion, each running the real check in a small repo."], "decided": ["Each test checks the setting's good case beside its bad case."], "open": []},
 "verdict": "approve",
 "summary": "The plan carries all five asks, each with one test that fails today because the setting is not read yet.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The check that new tests fail today stops a test after the time limit setting.", "source": "https://github.com/dokima-dev/dokima/issues/781", "criterion": "805.1"},
  {"ask": "The planner's test files are found by the test folder and file pattern settings.", "source": "https://github.com/dokima-dev/dokima/issues/781", "criterion": "805.2"},
  {"ask": "Turning docstrings off in settings stops the planner's check requiring them.", "source": "https://github.com/dokima-dev/dokima/issues/781", "criterion": "805.3"},
  {"ask": "The planner's test docstring cap comes from settings.", "source": "https://github.com/dokima-dev/dokima/issues/781", "criterion": "805.4"},
  {"ask": "An empty planner test docstring cap turns that cap off.", "source": "https://github.com/dokima-dev/dokima/issues/781", "criterion": "805.5"}
 ],
 "behaviors": [
  {"criterion": "805.1", "one_behavior": true, "why": "One limit, one result: the slow test is stopped."},
  {"criterion": "805.2", "one_behavior": true, "why": "One result: which files count as test files."},
  {"criterion": "805.3", "one_behavior": true, "why": "One switch, one result: docstrings no longer required."},
  {"criterion": "805.4", "one_behavior": true, "why": "One value read: the cap."},
  {"criterion": "805.5", "one_behavior": true, "why": "One case: an empty cap means no cap."}
 ],
 "edge_cases": [
  {"criterion": "805.1", "cut": [], "missing": []},
  {"criterion": "805.2", "cut": [], "missing
```

> Exit code 1
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
sed -i 's/each running the real check in a small repo/each running the real check/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 805 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`9. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/each running the real check in a small repo/each running the real check/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 805 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I approved the plan for [#805](https://github.com/dokima-dev/dokima/issues/805) (planner's test limits and docstrings follow settings). The hand-back passes both checks and is saved as `/tmp/dokima-out/review.json`.

- **Asks:** The parent issue [#781](https://github.com/dokima-dev/dokima/issues/781) (test settings) lists five asks for this issue. Each one is a criterion, word for word, and none is missing.
- **Size:** Each criterion is one behavior with one test.
- **Tests fail today, for the right reason:** I ran all five. Each fails because the planner's check doesn't read the setting yet, not because of a crash or a bad path.
  - **805.1:** A test that runs 3 s isn't stopped at a 1 s limit.
  - **805.2:** A helper file outside the file pattern is still read as a test file.
  - **805.3:** With docstrings turned off, the check still requires them.
  - **805.4:** A 7-word first line passes a cap of 5.
  - **805.5:** A 29-word first line is rejected even when the cap is left empty.
- **Good cases too:** Each test also checks the case that should pass, such as a fast test or a line under the cap. So code that ignores the setting can't pass it.

I raised no blockers or questions, and there were no open blockers to answer.

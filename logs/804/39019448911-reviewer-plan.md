# reviewer (plan) for #804

Run: https://github.com/dokima-dev/dokima/actions/runs/39019448911

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #804: Tests are found and tagged by the test settings
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [805], "loop": []} -->
> Dokima finds, links and runs tests by the repo's test settings instead of fixed values.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/805
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/718
> 
> 
> **User story:** A repo's test tag, folder and run command decide which tests Dokima finds, links and runs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The repo's test tag setting decides which call links a test to its criterion.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-804/tests/test_test_settings.py#L118"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" w

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/test_text_only.py; cat -n tests/test_test_settings.py
```

> commit affa747a456355237569db6d617d2566657233fa
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 08:59:48 2026 +0000
> 
>     planner for #804 (run 39019073768)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_test_settings.py | 346 ++++++++++++++++++++++++++++++++++++++++++++
>  tests/test_text_only.py     |  10 +-
>  2 files changed, 351 insertions(+), 5 deletions(-)
> commit affa747a456355237569db6d617d2566657233fa
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 08:59:48 2026 +0000
> 
>     planner for #804 (run 39019073768)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_text_only.py b/tests/test_text_only.py
> index c651935..9f159f6 100644
> --- a/tests/test_text_only.py
> +++ b/tests/test_text_only.py
> @@ -7,7 +7,8 @@ linked, or the description says "Closes #77" and issue #77 has no comments and n
>  Others run the shell of the Acceptance criteria workflow's own steps, cut out of `.github/workflows/acceptance-criteria.yml`, with a fake
>  `pytest` on PATH, so the workflow GitHub runs is the thing judged. Nothing here touches the network.
>  
> -Text files are `.md` files outside `dokima/roles/`, `tests/` and `.github/`: AGENTS.md, README.md, the wiki under
> +Text files are `.md` files outside the folders the text_only.not_text setting names (`tests/` and `.git

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_test_settings.py 2>&1 | grep -E "^(FAILED|E  .*80[0-9]\.|[0-9]+ (passed|failed))|AssertionError: 804" | head -40; cat dokima/defaults.yaml | head -60
```

> E       AssertionError: 804.1: an older test linked to 50.1 by the tag setting's call was changed with no reason and not caught: 
> E       AssertionError: 804.2: tests written as methods of a test class were not found: the plan came with no tests; the plan names tests/test_jobs.py::TestJobs::test_id, which is not in the repo; the plan names tests/test_jobs.py::TestJobs::test_unique, which is not in the repo
> E       AssertionError: 804.2: a class method test with no docstring was not held to the summary rule: the plan came with no tests; the plan names tests/test_jobs.py::TestJobs::test_id, which is not in the repo; the plan names tests/test_jobs.py::TestJobs::test_unique, which is not in the repo
> E           AssertionError: 804.3: tests written as async functions were not found ('which is not in the repo'): the plan came with no tests; the plan names tests/test_jobs.py::test_id, which is not in the repo; the plan names tests/test_jobs.py::test_unique, which is not in the repo
> E       AssertionError: 804.4: tests indented under another block were not found: the plan came with no tests; the plan names tests/test_jobs.py::test_id, which is not in the repo; the plan names tests/test_jobs.py::test_unique, which is not in the repo
> E       AssertionError: 804.5: a prompt-only change did not get the text-only check: [{'id': 'none', 'name': 'No approved plan found: no issue linked', 'tests': ''}]
> E       AssertionError: 804.6: a Markdown file under a folder the settings list took the s

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def passing_today\|def main_with_tests\|def problems\|def test_functions\|tests/\|PROVES\|TEST_DEF" dokima/planner.py | head -40; grep -n "PROVES\|TEST_DEF\|NOT_TEXT\|MANUAL_FIX" dokima/checks.py | head
```

> 6:dokima/roles/planner.md), raising its questions for the owner in its raises, plus its tests in tests/. Every
> 26:from dokima.checks import PROVES, TEST_DEF
> 400:def test_functions(text):
> 407:            out[name] = (src, PROVES.findall(src))
> 409:        found = TEST_DEF.match(line)
> 453:def problems(number, plan, files, tc, declared=None):
> 459:    out = [f"{p} is outside tests/; the planner may only write tests" for p in files if not p.startswith("tests/")]
> 580:def main_with_tests(base, into):
> 581:    """Lay main's code (`base`) into the folder `into`, with the branch's tests/ as they stand now on top.
> 601:def passing_today(added, base="HEAD"):
> 655:            paths = [p for p in files if p.startswith("tests/") and p.endswith(".py")]
> 23:PROVES = re.compile(r"""record_property\(\s*["']proves["']\s*,\s*["']([\d.]+)["']\s*\)""")
> 24:TEST_DEF = re.compile(r"^def (test_\w+)\(")
> 27:NOT_TEXT = ("dokima/roles/", "tests/", ".github/")
> 28:MANUAL_FIX = [{"id": "manual-fix", "name": "Manual fix: all tests pass", "tests": "tests"}]
> 49:            return MANUAL_FIX
> 65:    return bool(path) and path.lower().endswith(".md") and not path.startswith(NOT_TEXT)

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,40p dokima/settings.py | grep -n "def \|git\|cwd" ; grep -n "def read" -A15 dokima/settings.py | head -30; sed -n 595,640p dokima/planner.py; ls .dokima 2>&1
```

> 31:def load(path):
> 79:def read(repo=".", warn=None):
> 80-    """The merged settings for the repo at REPO; raises Locked on a locked setting."""
> 81-    warn = warn or (lambda message: print(f"::warning title=Unknown setting::{message}", file=sys.stderr))
> 82-    mine = load(os.path.join(repo, REPO_FILE))
> 83-    locked = mine.get(LOCKED)
> 84-    if locked is not None:
> 85-        names = [f"{LOCKED}.{k}" for k in locked] if isinstance(locked, dict) and locked else [LOCKED]
> 86-        raise Locked(f"{REPO_FILE} sets the locked setting {', '.join(names)}; a repo may not change it.")
> 87-    return merge(load(DEFAULTS), mine, warn)
> 88-
> 89-
> 90-def setup_lines(got):
> 91-    """The setup group as `name=value` lines; a value on several lines fails."""
> 92-    lines = []
> 93-    for name, value in got["setup"].items():
> 94-        value = "" if value is None else str(value)
>     for p in listed:
>         if p and os.path.isfile(p):
>             os.makedirs(os.path.dirname(os.path.join(into, p)), exist_ok=True)
>             shutil.copyfile(p, os.path.join(into, p))
> 
> 
> def passing_today(added, base="HEAD"):
>     """Run each new test (path::name) on main's code (`base`) with the planner's tests on top; the ones that pass or
>     are skipped, or run past the limit."""
>     out = []
>     if not added:
>         return out
>     with tempfile.TemporaryDirectory() as into:
>         main_with_tests(base, into)
>         for t in sorted(added):
>             try:
>                 r = subprocess.run([sys.executable, "-m", 

**Agent:** I've confirmed all 11 new tests fail today for the right reasons; checking the repo's own settings, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat .dokima/settings.yaml; timeout 600 python -m pytest -q tests/test_text_only.py 2>&1 | tail -2
```

> # This repo's own settings, over Dokima's shipped defaults (dokima/defaults.yaml).
> co_author: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> .....                                                                    [100%]
> 5 passed in 2.50s

`7. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
S="https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729"
asks=[("Which call links a test to its criterion is read from the test tag setting.","804.1"),
("Dokima finds tests written as methods of a test class.","804.2"),
("Dokima finds tests written as async functions.","804.3"),
("Dokima finds tests indented under another block.","804.4"),
("Changes to Dokima's prompt folder no longer stop the text-only shortcut.","804.5"),
("The folders that stop the text-only shortcut come from settings.","804.6"),
("The manual-fix check runs the tests in the test folder setting.","804.7"),
("The planner's check refuses files outside the test folder setting.","804.8"),
("The planner's check lays the branch's test folder, from settings, over main.","804.9"),
("The check that new tests fail today runs each with the run-one command setting.","804.10")]
T="tests/test_test_settings.py::"
tests={"804.1":"test_the_test_tag_setting_decides_which_call_links_a_test",
"804.2":"test_tests_written_as_methods_of_a_test_class_are_found",
"804.2b":"test_a_class_method_test_still_needs_its_summary",
"804.3":"test_tests_written_as_async_functions_are_found",
"804.4":"test_tests_indented_under_another_block_are_found",
"804.5":"test_prompt_folder_changes_take_the_text_only_shortcut",
"804.6":"test_the_folders_that_stop_the_text_only_shortcut_come_from_settings",
"804.7":"test_the_manual_fix_check_runs_the_test_folder_setting",
"804.8":"test_the_planners_check_refuses_files_outside_the_test_folder_setting",
"804.9":"test_the_new_test_check_lays_the_test_folder_setting_over_main",
"804.10":"test_the_new_test_check_runs_each_test_with_the_run_one_setting"}
r={"previous_step":{"did":["Wrote ten criteria, one per ask, with eleven failing tests.",
 "Dropped the prompt folder case from one older text-only test."],
 "decided":["Each setting is proven from a small repo with its own settings file."],"open":[]},
"ver
```

> (Bash completed with no output)

**Agent:** I approved the plan for issue [#804](https://github.com/dokima-dev/dokima/issues/804) (tests are found and tagged by the test settings). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks passed.

- **Asks:** the owner made ten asks in the [#740 comment](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729). Each one has its own criterion, 804.1 to 804.10, and none is missing.
- **Tests:** all 11 new tests in `tests/test_test_settings.py` fail today for the right reason. Each failure shows the feature is missing, not a crash or a bad path.
- **Pass and fail cases:** every test that checks a rejection also has a case that should pass.
- **How the tests run:** each one runs the real check against a small repo with its own settings file.
- **Changed older test:** one older text-only test no longer lists the prompt folder as a change that loses the shortcut. That is exactly what the owner asked for in criterion 804.5. The rest of that test is unchanged, and `tests/test_text_only.py` still passes.
- **Size and edge cases:** every criterion is one behavior. No edge cases needed cutting and no normal-use cases are missing.

There were no open blockers to answer, and I raised none.

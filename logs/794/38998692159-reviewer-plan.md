# reviewer (plan) for #794

Run: https://github.com/dokima-dev/dokima/actions/runs/38998692159

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (57.1KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/a9acd21c-2012-4e48-b58f-c70eff81ecf6/tool-results/bwesy7k0r.txt
> 
> Preview (first 2KB):
> # Issue #794: Setup saves safely; agents and test setup follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 793 -->
> <!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/801 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/801/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/793
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/795
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com

`2. Bash`
```
cd /tmp/pack; sed 's/<img[^>]*>//g' issue.md | head -c 30000
```

> # Issue #794: Setup saves safely; agents and test setup follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 793 -->
> <!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/801 ·  [files changed](https://github.com/dokima-dev/dokima/pull/801/files)
> 
>  **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/793
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/795
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/780
> - https://github.com/dokima-dev/dokima/issues/727
> 
> 
> **User story:** Setup keeps a settings file intact, agents come from it, and test workflows install what it names.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** A settings file holding lists is read in full, on every machine that runs Dokima.
>   *<a href="https://github.com/dokima-dev/dokima/blob/d53791310b9c727bca5c2a7440292f7b9a6f1011/tests/test_settings_setup.py#L162"> Acceptance test</a>: A settings file with lists on one line is read with every item.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/d53791310b9c727bca5c2a7440292f7b9a6f1011/tests/test_settings_setup.py#L183">Lists written 

`3. Bash`
```
cd /tmp/pack; sed 's/<img[^>]*>//g' issue.md | tail -c +30000 | head -c 15000; echo ====; ls in; cat open_blockers.json
```

> **No test: old reader:** The owner asked for a test running the setup step against an old settings reader without setup mode. Add one for 794.8: it must fall back to the old list. · for the planner
>   - Evidence: Owner's /work comment of 2026-10-17T03:06Z; `grep -rl setup_lines tests/` finds nothing.
> 
> <details><summary>Full record</summary>
> 
> (full record: in/, from the record files)
> 
> </details>
> 
> **Next:** The planner starts now.
> 
> <!-- dokima-stats -->
>  Opus 5.5 · 0.6 min · 11 turns · 392K tokens in, 3K out · $0.37 at API prices · [conversation](https://github.com/dokima-dev/dokima/blob/logs/logs/794/38997755074-reviewer-pr.md) · [run](https://github.com/dokima-dev/dokima/actions/runs/38997755074)
> 
> 
> ### dokima-runtime on issue #794 (2026-10-17T03:12:37Z)
> 
> <!-- dokima-record -->
>   The planner planned this issue.
> 
> **Raised earlier:**
> 
> - Code review on [#801](https://github.com/dokima-dev/dokima/pull/801#issuecomment-6228883156) raised:  **No test: old reader:** The owner asked for a test running the setup step against an old settings reader without setup mode. Add one for 794.8: it must fall back to the old list. · for the planner
>   - Done: Added a test under 794.8: each test workflow with an old settings reader installs the old list.
> - A raise not found in this issue's earlier records
>   - Done: Same test: it runs every test workflow's setup against a reader without the setup mode.
> 
> <details><summary><b>Test changes</b></summary>
> 
> - `tests/test_setup.py::test_settings_name_key_se

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1)[:20000])"; python3 -c "
import json;p=json.load(open('in/14-planner.json'));print(json.dumps(p,indent=1)[:6000])"
```

> {
>  "kind": "user_story",
>  "title": "Setup saves safely; agents and test setup follow settings",
>  "summary": "Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.",
>  "user_story": "Setup keeps a settings file intact, agents come from it, and test workflows install what it names.",
>  "acceptance_criteria": [
>   {
>    "text": "A settings file holding lists is read in full, on every machine that runs Dokima.",
>    "words": "A settings file holding lists is read in full, on every machine that runs Dokima.",
>    "source": "https://github.com/dokima-dev/dokima/issues/779",
>    "files": [
>     "dokima/setup.py",
>     ".github/workflows/acceptance-criteria.yml",
>     ".github/workflows/agent.yml",
>     ".github/workflows/assign.yml",
>     ".github/workflows/audit.yml",
>     ".github/workflows/autopilot.yml",
>     ".github/workflows/board.yml",
>     ".github/workflows/commands.yml",
>     ".github/workflows/playthrough.yml",
>     ".github/workflows/uptodate.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "Lists written one item per line",
>      "test": "tests/test_settings_setup.py::test_a_list_written_one_item_per_line_is_read_in_full"
>     },
>     {
>      "case": "A workflow job that runs Dokima before installing the reader",
>      "test": "tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file"
>     }
>    ]
>   },
>   {
>    "text": "Saving a setting through setup keeps the file's comments.",
>    "words": "Sa

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3 --stat | head -30; grep -n "def test_a_reader_without" -A80 tests/test_settings_test_setup.py
```

> 9fbc85f planner for #794 (run 38997904965)
>  tests/test_settings_test_setup.py | 63 +++++++++++++++++++++++++++++++++++++--
>  1 file changed, 61 insertions(+), 2 deletions(-)
> d537913 worker for #794 (run 38997482807)
>  .github/workflows/acceptance-criteria.yml | 7 ++++---
>  .github/workflows/agent.yml               | 5 +++++
>  .github/workflows/full-suite.yml          | 7 ++++---
>  .github/workflows/testmon.yml             | 7 ++++---
>  4 files changed, 17 insertions(+), 9 deletions(-)
> a914b88 worker for #794 (run 38992393139)
>  .github/workflows/acceptance-criteria.yml |  22 +++-
>  .github/workflows/agent.yml               |  27 ++++-
>  .github/workflows/assign.yml              |   1 +
>  .github/workflows/audit.yml               |   1 +
>  .github/workflows/autopilot.yml           |   1 +
>  .github/workflows/board.yml               |   2 +
>  .github/workflows/commands.yml            |   5 +
>  .github/workflows/full-suite.yml          |  20 +++-
>  .github/workflows/playthrough.yml         |   1 +
>  .github/workflows/testmon.yml             |  19 +++-
>  .github/workflows/uptodate.yml            |   1 +
>  dokima/agents.py                          |  65 +++++++----
>  dokima/defaults.yaml                      |   3 +
>  dokima/settings.py                        |  24 +++-
>  dokima/setup.py                           | 180 +++++++++++++++++++++++-------
>  15 files changed, 297 insertions(+), 75 deletions(-)
> 203:def test_a_reader_without_the_setup_mode_falls_back_to_the_old_install_list(record_property, tmp

**Agent:** Reviewing the planner's new fallback test for 794.8; running it on the branch and against main's workflows now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,202p tests/test_settings_test_setup.py
```

> """Tests for #794: every test workflow sets up the repo's tests as the settings say.
> 
> The settings group is `setup:` in `.dokima/settings.yaml`, over the shipped defaults in `dokima/defaults.yaml`:
> 
>     setup:
>       python: "3.12"                                  # the Python the repo's tests run on
>       test_tools: pytest pytest-xdist pytest-testmon  # what each test workflow installs for the tests
>       install: ""                                     # the repo's own install command, run before its tests
> 
> The test workflows are the all tests check (full-suite.yml), each criterion's check (acceptance-criteria.yml), the
> testmon baseline (testmon.yml) and an agent's run (agent.yml), whose agent runs the repo's tests. Each test runs one
> job's own steps the way GitHub runs them, through tests/test_start.py's machine: `if:` evaluated, `${{ }}` filled,
> each script run with bash in a clone of a temp repo whose main holds the settings file. Here `pip`, `pip3`,
> `pytest`, `python3 -m pip` and `python3 -m pytest` only log their arguments; a `setup-python` step logs the version it
> was given (its `python-version`, expressions filled); the fake Claude Code logs when the agent starts. The log, in
> order, shows what was installed, on which Python, before the repo's tests first ran. Nothing leaves the machine.
> """
> import os
> import shutil
> import sys
> 
> import pytest
> 
> sys.path.insert(0, os.path.dirname(__file__))
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from test_start i

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q -x -k "reader_without" tests/test_settings_test_setup.py 2>&1 | tail -5; git diff origin/main --stat -- dokima/settings.py 2>/dev/null | tail -2; git show origin/main:dokima/settings.py | grep -n "setup\|def main\|__main__" | head
```

> ....                                                                     [100%]
> 4 passed, 12 deselected in 6.86s
>  dokima/settings.py | 24 ++++++++++++++++++++----
>  1 file changed, 20 insertions(+), 4 deletions(-)
> 85:def main():
> 99:if __name__ == "__main__":

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git show origin/main:dokima/settings.py | sed -n 80,105p; echo ===; sed -n '/def setup_lines/,$p' dokima/settings.py; echo ===; git diff a914b88 d537913 -- .github/workflows/full-suite.yml
```

> names = [f"{LOCKED}.{k}" for k in locked] if isinstance(locked, dict) and locked else [LOCKED]
>         raise Locked(f"{REPO_FILE} sets the locked setting {', '.join(names)}; a repo may not change it.")
>     return merge(load(DEFAULTS), mine, warn)
> 
> 
> def main():
>     """Prints the merged settings as JSON; exits 1, saying why, when they cannot be used."""
>     try:
>         got = read()
>     except Locked as e:
>         print(f"::error title=Locked setting::{e}", file=sys.stderr)
>         return 1
>     except (OSError, ValueError, yaml.YAMLError) as e:
>         print(f"::error title=Settings not read::{e}", file=sys.stderr)
>         return 1
>     print(json.dumps(got, indent=1))
>     return 0
> 
> 
> if __name__ == "__main__":
>     sys.exit(main())
> ===
> def setup_lines(got):
>     """The setup group as `name=value` lines; a value on several lines fails."""
>     lines = []
>     for name, value in got["setup"].items():
>         value = "" if value is None else str(value)
>         if "\n" in value:
>             raise ValueError(f"setup.{name} in {REPO_FILE} must be one line")
>         lines.append(f"{name}={value}")
>     return "\n".join(lines)
> 
> 
> def main(argv=()):
>     """Prints the merged settings as JSON, or the setup group; exits 1 saying why."""
>     try:
>         got = read()
>         if list(argv) == ["setup"]:
>             print(setup_lines(got))
>             return 0
>     except Locked as e:
>         print(f"::error title=Locked setting::{e}", file=sys.stderr)
>         return 1
>     except (OSError, ValueError

`9. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt HEAD 2>&1|tail -1; cd /tmp/wt; git checkout -q a914b88 -- .github/workflows; timeout 600 python -m pytest -q -k "reader_without" tests/test_settings_test_setup.py 2>&1 | grep -E "^E .*794|passed|failed" | head -12
```

> E       AssertionError: 794.8: with a settings reader that has no setup mode, full-suite.yml job all-tests did not install the old test tools ['pytest', 'pytest-xdist']; got ['pyyaml']
> E       AssertionError: 794.8: with a settings reader that has no setup mode, acceptance-criteria.yml job check did not install the old test tools ['pytest', 'pytest-xdist']; got ['pyyaml']
> E       AssertionError: 794.8: with a settings reader that has no setup mode, testmon.yml job baseline did not install the old test tools ['pytest', 'pytest-testmon', 'pytest-xdist']; got ['pyyaml']
> E       AssertionError: 794.8: with a settings reader that has no setup mode, agent.yml job run did not install the old test tools ['pytest', 'pytest-testmon', 'pytest-xdist']; got ['pyyaml']
> 4 failed, 12 deselected in 6.16s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; timeout 900 python -m pytest -q -n auto tests/test_settings_test_setup.py tests/test_settings_setup.py tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | tail -3; python3 -c "
import json;[print(f, json.load(open('/tmp/pack/in/'+f)).get('verdict') or list(json.load(open('/tmp/pack/in/'+f)).keys())) for f in ['13-reviewer-pr.json','14-planner.json']]"
```

> .....................................................................    [100%]
> 69 passed in 26.44s
> 13-reviewer-pr.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 14-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']

`11. Bash`
```
cd /home/runner/work/dokima/dokima; git show 9fbc85f | grep -E "^[-+]" | grep -v "^+++\|^---" | grep "^-"; python3 -c "
import json;h=json.load(open('/tmp/pack/in/09-reviewer-plan.json'))['handback'];print(json.dumps(h['asks'],indent=0));print(json.dumps(h['behaviors'])[:300]);print(h.get('raises'))
h=json.load(open('/tmp/pack/in/13-reviewer-pr.json'));print(h['url'])"
```

> -    def __init__(self, tmp, file, job, settings):
> -        """Run JOB of workflow FILE with SETTINGS as main's settings file (None for none)."""
> [
> {
> "ask": "A settings file holding lists is read in full, on every machine that runs Dokima.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.1"
> },
> {
> "ask": "Saving a setting through setup keeps the file's comments.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.2"
> },
> {
> "ask": "Saving a setting through setup keeps comments written at the end of a line.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.3"
> },
> {
> "ask": "Saving one setting through setup leaves every other setting as it was.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.4"
> },
> {
> "ask": "The agents section of the settings file picks each role's agent and model.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.5"
> },
> {
> "ask": "A repo with only the old agents file still runs each role's agent as named there.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.6"
> },
> {
> "ask": "No setting in a repo's file changes the order: plan, review, build, review, merge.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "794.10"
> },
> {
> "ask": "The repo's own install command runs before its tests in every test workflow.",
> "source": "https://github.com/dokima-dev/dokima/issues/7

**Agent:** The new test fails on the broken workflows for the right reason and passes on the fix. Now writing the review.

`12. Bash`
```
cd /tmp/pack; grep -oh "https://github.com/dokima-dev/dokima/issues/794#issuecomment-[0-9]*" in/*.json issue.md | sort | uniq -c; grep -o '"evidence": "[^"]*03:06[^"]*"' in/*.json | head; python3 -c "
import json;h=json.load(open('in/09-reviewer-plan.json'))['handback'];print(json.dumps({k:h[k] for k in ['behaviors','edge_cases','tests']}))"
```

> 3 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6226902956
>       2 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227160150
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227259900
>       2 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227301779
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227325962
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227504576
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6227549215
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6228069054
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6228116558
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6228137567
>       1 https://github.com/dokima-dev/dokima/issues/794#issuecomment-6228903331
> in/13-reviewer-pr.json:"evidence": "Owner's /work comment of 2026-10-17T03:06Z; `grep -rl setup_lines tests/` finds nothing."
> in/12-worker.json:"evidence": "Owner's comment of 2026-10-17T03:06Z on #794; the setup step in `full-suite.yml` now probes `setup_lines`, checked by hand only."
> {"behaviors": [{"criterion": "794.1", "one_behavior": true, "why": "One result: lists are read whole wherever Dokima runs."}, {"criterion": "794.2", "one_behavior": true, "why": "One result: comment lines survive a save."}, {"criterion": "794.3", "one_behavior": true, "why": "One result: end-of-line comments survive a save."}, {"criterio

`13. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
prev=json.load(open('in/09-reviewer-plan.json'))['handback']
asks=prev['asks']+[{"ask":"Make every workflow that reads the setup group fall back to the old install list unless the settings reader really supports `setup` (check for the mode, not the file), and add a test that runs the step against a settings.py that lacks it.","source":"https://github.com/dokima-dev/dokima/issues/794","criterion":"794.8"}]
tests=prev['tests'][:]
i=[t['test'] for t in tests].index("tests/test_settings_test_setup.py::test_the_test_tools_installed_come_from_the_test_tools_setting")
tests.insert(i+1,{"test":"tests/test_settings_test_setup.py::test_a_reader_without_the_setup_mode_falls_back_to_the_old_install_list","only_its_behavior":True,"why":"Fails on the file-only check that broke the queue; passes with the mode check."})
r={"previous_step":{"did":["The planner added a test: each test workflow with an old settings reader installs the old list.","The planner kept every other criterion and test as approved."],"decided":["The old reader is today's reader with its setup mode taken out, as main has it."],"open":[]},
"verdict":"approve","summary":"The plan now proves the fallback the owner asked for; the new test catches the merge queue break.",
"raises":[],"answers":[],"asks":asks,"behaviors":prev['behaviors'],"edge_cases":prev['edge_cases'],"tests":tests,"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 794 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`14. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';r=json.load(open(p))
r['previous_step']['did'][0]="The planner added a test: test workflows with an old settings reader install the old list."
r['previous_step']['did'][0]="The planner added a test: an old settings reader makes workflows install the old list."
r['previous_step']['decided'][0]="The old reader is today's reader without its setup mode, as main has it."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 794 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#794](https://github.com/dokima-dev/dokima/issues/794) (setup saves safely; agents and test setup follow settings), and the review passes both checks.

**What the planner changed:** it added one test under 794.8, the criterion that the test tools come from the settings. The test runs each of the four test workflows twice:
- once with the current settings reader, where the workflow must install the tools the settings name;
- once with the reader that has no setup mode, as main has it now, where the workflow must install the old list on Python 3.12.

Everything else in the plan is unchanged from the version approved earlier.

**What I ran:**
- **On the branch, with the worker's fix:** the new test passes in all 4 workflows.
- **With the workflows from before the fix**, which only checked that the reader file exists (the merge queue break): it fails in all 4. The message names the missing old tools, e.g. "did not install the old test tools ['pytest', 'pytest-xdist']; got ['pyyaml']". So it fails for the right reason.
- **The other plan tests and the older tests the plan changed:** 69 passed.

**Your last request:** your `/work` comment asked for a fallback that checks for the setup mode, not the file, plus a test that runs the step against a reader without that mode. The new test covers both, and I matched that ask to 794.8.

I raised no blockers and no questions, and there were no open raises for me to answer. The review is in `/tmp/dokima-out/review.json`.

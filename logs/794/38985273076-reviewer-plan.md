# reviewer (plan) for #794

Run: https://github.com/dokima-dev/dokima/actions/runs/38985273076

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #794: Setup saves safely; agents and test setup follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 793 -->
> <!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/794#issuecomment-6226902956) with `/plan`, or say `/review`
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
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/780
> - https://github.com/dokima-dev/dokima/issues/727
> 
> 
> **User story:** Setup keeps a settings file intact, agents come from it,

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit c7876019cd8ef67ba7e736231fa0f4ed73087564
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 00:11:53 2026 +0000
> 
>     planner for #794 (run 38983675129)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_checks.py              |   4 +-
>  tests/test_manual_fix_installs.py |  50 ++----
>  tests/test_settings_setup.py      | 361 ++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_test_setup.py | 169 ++++++++++++++++++
>  tests/test_setup.py               |  36 ++--
>  tests/test_testmon.py             |  15 +-
>  6 files changed, 574 insertions(+), 61 deletions(-)
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38983675129",
>  "commit_before": "ab0642737a03557232fbfa03901dc90ee3932637",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 43496,
>   "turns": 3,
>   "cost_usd": 4.452412800000001,
>   "tokens_in": 606435,
>   "tokens_out": 1421
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/794/38983675129-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38983675129",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/794#issuecomment-6226902956"
> }

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_settings_setup.py tests/test_settings_test_setup.py tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | tail -40
```

> Full diff:
>     [
>   -     'zeta-1',
>   +     'claude-opus-5-5',
>     ]
> FAILED tests/test_agents.py::test_moving_a_role_takes_one_edit_of_its_own_lines - AssertionError: 698.20: the worker should start on FIRST_KEY: exit 0; stdout: 'CLAUDE_CODE_OAUTH_TOKEN'; stderr: ''
> assert (0 == 0 and 'CLAUDE_CODE_OAUTH_TOKEN' == 'FIRST_KEY'
>  +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python', '-m', 'dokima.agents', 'key', 'worker'], returncode=0, stdout='CLAUDE_CODE_OAUTH_TOKEN\n', stderr='').returncode
>   
>   - FIRST_KEY
>   + CLAUDE_CODE_OAUTH_TOKEN)
> FAILED tests/test_agents.py::test_other_sections_can_join_the_settings_file - AssertionError: 698.22: another section changed the planner's model: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> assert (0 == 0 and 'claude-opus-5-5' == 'claude-sonnet-5-5'
>  +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python', '-m', 'dokima.agents', 'model', 'planner'], returncode=0, stdout='claude-opus-5-5\n', stderr='').returncode
>   
>   - claude-sonnet-5-5
>   ?         -----
>   + claude-opus-5-5
>   ?        +++)
> FAILED tests/test_setup.py::test_settings_name_key_secret - AssertionError: 697.3: setup wrote no agents section into .dokima/settings.yaml.
>   exit 0
>   stdout: Stored CODEX_KEY and wrote codex-pro into .dokima/agents.yml.
>   
>   stderr: 
> assert None is not None
> FAILED tests/test_setup.py::test_settings_keep_other_subscription - AssertionError: 697.3: adding Codex dropped or changed the Kimi s

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_settings_setup.py tests/test_settings_test_setup.py tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | tail -40
```

> commit c7876019cd8ef67ba7e736231fa0f4ed73087564
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 00:11:53 2026 +0000
> 
>     planner for #794 (run 38983675129)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_checks.py              |   4 +-
>  tests/test_manual_fix_installs.py |  50 ++----
>  tests/test_settings_setup.py      | 361 ++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_test_setup.py | 169 ++++++++++++++++++
>  tests/test_setup.py               |  36 ++--
>  tests/test_testmon.py             |  15 +-
>  6 files changed, 574 insertions(+), 61 deletions(-)
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38983675129",
>  "commit_before": "ab0642737a03557232fbfa03901dc90ee3932637",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 43496,
>   "turns": 3,
>   "cost_usd": 4.452412800000001,
>   "tokens_in": 606435,
>   "tokens_out": 1421
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/794/38983675129-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38983675129",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/794#issuecomment-6226902956"
> }

> Full diff:
>     [
>   -     'zeta-1',
>   +     'claude-opus-5-5',
>     ]
> FAILED tests/test_agents.py::test_moving_a_role_takes_one_edit_of_its_own_lines - AssertionError: 698.20: the worker should start on FIRST_KEY: exit 0; stdout: 'CLAUDE_CODE_OAUTH_TOKEN'; stderr: ''
> assert (0 == 0 and 'CLAUDE_CODE_OAUTH_TOKEN' == 'FIRST_KEY'
>  +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python', '-m', 'dokima.agents', 'key', 'worker'], returncode=0, stdout='CLAUDE_CODE_OAUTH_TOKEN\n', stderr='').returncode
>   
>   - FIRST_KEY
>   + CLAUDE_CODE_OAUTH_TOKEN)
> FAILED tests/test_agents.py::test_other_sections_can_join_the_settings_file - AssertionError: 698.22: another section changed the planner's model: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> assert (0 == 0 and 'claude-opus-5-5' == 'claude-sonnet-5-5'
>  +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python', '-m', 'dokima.agents', 'model', 'planner'], returncode=0, stdout='claude-opus-5-5\n', stderr='').returncode
>   
>   - claude-sonnet-5-5
>   ?         -----
>   + claude-opus-5-5
>   ?        +++)
> FAILED tests/test_setup.py::test_settings_name_key_secret - AssertionError: 697.3: setup wrote no agents section into .dokima/settings.yaml.
>   exit 0
>   stdout: Stored CODEX_KEY and wrote codex-pro into .dokima/agents.yml.
>   
>   stderr: 
> assert None is not None
> FAILED tests/test_setup.py::test_settings_keep_other_subscription - AssertionError: 697.3: adding Codex dropped or changed the Kimi s

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_settings_setup.py tests/test_settings_test_setup.py tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | grep -E "^(FAILED|ERROR)" | cut -c1-220; git diff HEAD~1 --stat; git log --oneline -3 -- tests/test_agents.py tests/test_setup.py
```

> FAILED tests/test_settings_setup.py::test_a_settings_file_holding_lists_is_read_in_full - AssertionError: 794.1: the settings file's lists were not read in full; got {'protected_paths': '[.github/, ops/, "docs/private/"]
> FAILED tests/test_settings_setup.py::test_a_list_written_one_item_per_line_is_read_in_full - AssertionError: 794.1: lists written one item per line were not read in full; got {'protected_paths': {'- .github/': {}, '- ops
> FAILED tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file - AssertionError: 794.1: these jobs run Dokima before installing PyYAML, so they cannot read a settings file holding lis
> FAILED tests/test_settings_setup.py::test_saving_a_setting_keeps_the_files_comments - AssertionError: 794.2: setup did not save the team subscription and the planner into the agents section of .dokima/settings.yaml; the 
> FAILED tests/test_settings_setup.py::test_saving_a_setting_keeps_comments_at_the_end_of_lines - AssertionError: 794.3: setup did not save the team subscription and the planner into the agents section of .dokima/settings.
> FAILED tests/test_settings_setup.py::test_saving_one_setting_leaves_every_other_setting_as_it_was - AssertionError: 794.4: setup did not save the team subscription and the planner into the agents section of .dokima/setti
> FAILED tests/test_settings_setup.py::test_saving_into_a_file_with_no_agents_section_leaves_the_rest - AssertionError: 794.4: setup did not save the team subscription and the 

`7. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt HEAD~1 && cd /tmp/mainwt && timeout 600 python -m pytest -q tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | cut -c1-200
```

> _____________ test_any_model_the_role_names_is_passed_to_its_agent _____________
>     def test_any_model_the_role_names_is_passed_to_its_agent(record_property, tmp_path):
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5
> FAILED tests/test_agents.py::test_each_role_has_its_own_subscription_and_model - AssertionError: 698.3: the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent - AssertionError: 698.4: Claude Code got model 'claude-opus-5-5', not the role's claude-unreleased-9-9
> FAILED tests/test_agents.py::test_a_role_the_file_leaves_out_starts_claude_code_as_today - AssertionError: 698.7: the worker the file names should run on claude-haiku-5-5: exit 0; stdout: 'claude-opus
> FAILED tests/test_agents.py::test_a_role_missing_its_model_stops_and_names_the_role - AssertionError: 698.8: a planner with no model line did not stop with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_an_unknown_agent_stops_before_any_agent - AssertionError: 698.10: an unknown agent did not stop the planner with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_a_runs_record_reads_its_agent_through_the_interface - AssertionError: 698.15: the record names models ['claude-opus-5-5'], not ze

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,80p dokima/agents.py; env | grep -i -E "dokima|github_" | cut -c1-100; ls .dokima
```

> """The one agent interface: each role runs the agent and model the settings name (#698).
> 
> The settings file is `.dokima/agents.yml` under the current folder (or the path in DOKIMA_SETTINGS, where the
> workflow keeps main's copy, so a branch never picks its own agent or secret):
> 
>     subscriptions:
>       SUB:
>         agent: AGENT      # the adapter dokima/agent_AGENT.py runs it
>         key: SECRET       # the repo secret holding the subscription's key or sign-in
>     roles:
>       ROLE:               # planner, worker or reviewer
>         subscription: SUB
>         model: MODEL
> 
> With no file, or for a role the file leaves out, the role runs on Claude Code with today's model and secret. There is
> no fallback: a bad name stops the run before any agent starts, and a failed agent fails it. Any model name passes;
> the agent itself refuses one it lacks.
> 
>     python3 -m dokima.agents model ROLE
>     python3 -m dokima.agents key ROLE
>     python3 -m dokima.agents install ROLE
>     python3 -m dokima.agents run ROLE PROMPT_FILE OUT
> 
> An agent's adapter is the module dokima.agent_AGENT, offering install(), run(prompt, model, out), models(out, log_dir),
> report(out) and transcript(log_dir, secrets). Claude Code's is dokima/agent_claude.py.
> """
> import importlib
> import os
> import re
> import sys
> 
> from dokima.setup import SETTINGS, read_settings
> 
> TODAY = {"agent": "claude", "model": "claude-opus-5-5", "key": "CLAUDE_CODE_OAUTH_TOKEN"}
> ADAPTER = ("install", "run", "models", "report", "transcript")
> 
> 
> class S

**Agent:** Running the plan's tests now without a leaked environment setting that breaks older tests.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; unset DOKIMA_SETTINGS; timeout 600 python -m pytest -q tests/test_settings_setup.py tests/test_settings_test_setup.py tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | cut -c1-330; cd /tmp/mainwt; timeout 600 python -m pytest -q tests/test_agents.py tests/test_setup.py tests/test_testmon.py tests/test_checks.py tests/test_manual_fix_installs.py 2>&1 | tail -2
```

> E       AssertionError: 794.1: these jobs run Dokima before installing PyYAML, so they cannot read a settings file holding lists: acceptance-criteria.yml job list (first Dokima step: 'python3 -m dokima.checks matrix >> "$GITHUB_OUTPUT"'); agent.yml job run (first Dokima step: 'Only a code owner starts an agent'); agent.yml job u
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert r.agent_started(), f"794.5: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
>         assert first.returncode == 0, f"697.3: adding the first subscription failed.\n{said(first)}"
>         assert p.returncode == 0, f"697.3: adding a second subscription failed.\n{said(p)}"
>         assert first.returncode == 0, f"697.6: adding the first subscription failed.\n{said(first)}"
>         assert p.returncode == 0, f"697.6: adding a second subscription failed.\n{said(p)}"
> FAILED tests/test_settings_setup.py::test_a_settings_file_holding_lists_is_read_in_full - AssertionError: 794.1: the settings file's lists were not read in full; got {'protected_paths': '[.github/, ops/, "docs/private/"]', 'gates': {'required': '[all tests, Lint]'}, 'fence': {'test_setup_files': '[

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1 -- tests/test_setup.py tests/test_checks.py tests/test_testmon.py tests/test_manual_fix_installs.py
```

> diff --git a/tests/test_checks.py b/tests/test_checks.py
> index 770493e..a088cfe 100644
> --- a/tests/test_checks.py
> +++ b/tests/test_checks.py
> @@ -81,8 +81,7 @@ def test_annotation_links_permanently_to_the_tests_first_line(record_property):
>  def test_full_suite_runs_every_test_on_every_pull_request(record_property):
>      """The merge gate still runs every test, in parallel, exactly as today.
>  
> -    Proves 29.4, 539.3 and 716.1. Reads full-suite.yml and checks it still installs only pytest and pytest-xdist,
> -    still runs every test spread over all cores with `-n auto`, and never uses testmon, which only code reviews use.
> +    Proves 29.4, 539.3 and 716.1. Reads full-suite.yml and checks it still runs every test spread over all cores with `-n auto`, and never uses testmon, which only code reviews use.
>      For 716.1 it plays GitHub's part on a new push to a ready Dokima pull request, once by Dokima's bot and once by
>      the owner, and checks the all tests job runs for both: no trigger filter or condition on who pushed skips the
>      owner. The owner is played by their real login from `.github/CODEOWNERS`, as the repository's owner, so a rule
> @@ -102,7 +101,6 @@ def test_full_suite_runs_every_test_on_every_pull_request(record_property):
>      assert "pull_request_target:" in lines
>      assert "name: all tests" in lines
>      assert any(line.startswith("- run: pytest") and line.endswith(" tests") for line in lines)
> -    assert "- run: pip install -q pytest pytest-xdist" in lines, 

`11. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_settings_test_setup.py; cat dokima/defaults.yaml | head -80
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

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,361p tests/test_settings_setup.py
```

> """Tests for #794: setup saves settings safely; the agents section picks each role's agent.
> 
> A repo's settings file is `.dokima/settings.yaml`; its `agents:` section holds what `.dokima/agents.yml` held:
> 
>     agents:
>       subscriptions:
>         SUB:
>           agent: AGENT
>           key: SECRET
>       roles:
>         ROLE:
>           subscription: SUB
>           model: MODEL
> 
> `python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE --key` stores the key read
> from standard input as a repo secret (through `gh secret set`) and saves the subscription and the role into that
> section. These tests run the real commands from outside in a temp repo folder, with a stub `gh` first on PATH that
> logs every call, and stub `claude`, `npm`, `kimi` and `codex` commands that log every call. Nothing leaves the machine.
> The workflow test reads every file in .github/workflows/ and checks each job that runs Dokima installs PyYAML first.
> """
> import glob
> import json
> import os
> import re
> import subprocess
> import sys
> import textwrap
> 
> import yaml
> 
> sys.path.insert(0, os.path.dirname(__file__))
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from test_start import Run, SPLIT_PROPOSED  # noqa: E402
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> 
> STUB = textwrap.dedent('''\
>     #!{python}
>     """A stand-in for `{name}` that logs each call and exits 0."""
>     import json, os, sys
>     with open(os.environ["FAKE_LOG"], "a") as f:
>         f.wr

`13. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote nine criteria and their tests, and changed five older tests.",
          "The planner asked whether every Dokima job should install the YAML library."],
  "decided": ["The planner left out the rule that no setting changes the order of steps."],
  "open": ["The owner's rule on the order of steps has no criterion."]
 },
 "verdict": "block",
 "summary": "The tests are sound, but one ask is dropped: no setting may change the order of steps.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion: order",
   "text": "The owner asked that no setting change the order plan, review, build, review, merge, and no criterion carries it. Keep it, with a test that pins it.",
   "evidence": "Issue #794 lists this ask; plan.json has nine criteria and none for it."},
  {"kind": "issue", "label": "Leaked settings path",
   "text": "Older agent tests read the runner's own settings path, so nine fail on an agent's machine though green on GitHub's checks.",
   "evidence": "`tests/test_agents.py` fails 9 with `DOKIMA_SETTINGS` set, passes 42 with it unset on main."}
 ],
 "answers": [
  {"raise": "P1", "answer": "disagree", "why": "The owner asked for it; a test that pins today's order keeps it, as a doubt-already-fixed case allows."},
  {"raise": "P2", "answer": "done", "why": "The owner said every machine that runs Dokima, not only jobs that read settings.",
   "words": "A settings file holding lists is read in full, on every machine that runs Dokima.",
   "source": "https://github.com/dokima-dev/dokima/issues/794", "changes": false}
 ],
 "asks": [
  {"ask": "A settings file holding lists is read in full, on every machine that runs Dokima.", "source": "https://github.com/dokima-dev/dokima/issues/794", "criterion": "794.1"},
  {"ask": "Saving a setting through setup keeps the file's comments.", "source": "https://github.com/dokima-dev/dokima/issues/79
```

> raise 1 files an issue, so searched must list the open issues searched for the same cause, not None
> raise 1 files an issue, so verdict must be symptom, root cause or new, not None

`14. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent*.py | head -20; gh issue list --search "DOKIMA_SETTINGS" --state open 2>&1 | head
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_autopilot.py:180:        if decided.get(raises.VERDICT) == "symptom" and raises.is_numbers([cause]):
> dokima/agent_autopilot.py:181:            # A symptom joins its cause as a comment, and files no issue (#623).
> dokima/agent_autopilot.py:188:            lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), cause)} · a symptom, added as a comment")
> dokima/agent_autopilot.py:190:        symptoms = decided.get(raises.SYMPTOMS)
> dokima/agent_autopilot.py:191:        if decided.get(raises.VERDICT) == "root cause" and raises.is_numbers(symptoms) and symptoms:
> dokima/agent_autopilot.py:192:            # A root cause files one issue marked as such, naming each symptom so GitHub links both ways (#623).
> dokima/agent_autopilot.py:194:            body += ["", "**Symptoms:** " + ", ".join(f"#{n}" for n in symptoms)]
> dokima/agent_autopilot.py:198:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> gh: To use GitHub CLI in a 

`15. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 10,60p dokima/agent_checks.py; ls /tmp/pack
```

> from dokima import raises, words
> 
> 
> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(open(path)) if os.path.exists(path) else []
>     theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
>               and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
>     confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
>                  and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
>     filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
>     if not filed:
>         return []
>     bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
>     named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
>              for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numb

**Agent:** Checking the open issues list for a matching problem before filing the new one.

`16. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'))
for i in d:
  t=json.dumps(i).lower()
  if 'settings' in t and ('test' in t or 'leak' in t): print(i.get('number'), i.get('title'))
print(len(d))"
```

> 795 Test commands, branches and the bot follow settings
> 794 Setup saves safely; agents and test setup follow settings
> 782 The fence follows the test and protected path settings
> 781 Finding and checking tests follows the test settings
> 727 Nine agent interface tests fail on a runner because the runner's settings path leaks into them.
> 264 A pull request can't change how its own tests are judged through test setup files
> 186
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** #727 already covers the leaked settings path, so I'm dropping that raise.

`17. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises']=[r for r in d['raises'] if r['kind']!='issue']
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 794 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan: it drops one thing you asked for. Your rule that "No setting in a repo's file changes the order: plan, review, build, review, merge" has no criterion.

- **The dropped rule:** the planner asked you whether to leave it out, since nothing reads the order from settings today. I disagreed with that question. I sent the planner a blocker: keep the rule, with a test that pins today's order.
- **The YAML library question:** the planner asked whether every Dokima job should install it, or only jobs that read settings. Your words settle it: "on every machine that runs Dokima". So I answered it on autopilot: every job.
- **Everything else is fine.** Each of the other nine criteria is one behavior. Each has tests that run the real setup command or the real workflows, not just read code.
- **New tests fail today for the right reason:** the feature is missing. I ran the planner's tests; 26 fail, all for that reason.
- **Old tests still pass:** the 38 that pass are older tests, including the ones the plan keeps to prove the old agents file still works.
- **The five changed older tests** keep what they proved. One loses its check that the full test run installs exactly two tools. That fits your ask that tools come from the test tools setting.

On this machine, 9 older agent tests fail, on main too, because the runner's own settings path leaks into them. They all pass with it unset. That is [#727](https://github.com/dokima-dev/dokima/issues/727) (nine agent tests fail on a runner), so I filed nothing new.

The review is in `/tmp/dokima-out/review.json` and passes both checks.

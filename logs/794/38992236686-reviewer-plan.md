# reviewer (plan) for #794

Run: https://github.com/dokima-dev/dokima/actions/runs/38992236686

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (42.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/105a40fb-b3c9-40dd-acc1-bb30ceb93dd9/tool-results/bnjy4fe22.txt
> 
> Preview (first 2KB):
> total 96
> drwxr-xr-x 2 runner runner  4096 Oct 17 01:46 .
> drwxr-xr-x 3 runner runner  4096 Oct 17 01:46 ..
> -rw-r--r-- 1 runner runner 10194 Oct 17 01:46 01-planner.json
> -rw-r--r-- 1 runner runner  9039 Oct 17 01:46 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 10139 Oct 17 01:46 03-planner.json
> -rw-r--r-- 1 runner runner  9109 Oct 17 01:46 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 10452 Oct 17 01:46 05-planner.json
> -rw-r--r-- 1 runner runner  8583 Oct 17 01:46 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner  3087 Oct 17 01:46 07-worker.json
> -rw-r--r-- 1 runner runner 10594 Oct 17 01:46 08-planner.json
> # Issue #794: Setup saves safely; agents and test setup follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 793 -->
> <!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix the rejected hand-back
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" 

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (32.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/105a40fb-b3c9-40dd-acc1-bb30ceb93dd9/tool-results/bl6x40dsv.txt
> 
> Preview (first 2KB):
> # Issue #794: Setup saves safely; agents and test setup follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 793 -->
> <!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix the rejected hand-back
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
> - http

`3. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/105a40fb-b3c9-40dd-acc1-bb30ceb93dd9/tool-results/bl6x40dsv.txt
```

> 1	# Issue #794: Setup saves safely; agents and test setup follow settings
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 793 -->
> 5	<!-- dokima-blocking: {"blocked_by": [793], "blocks": [795], "loop": []} -->
> 6	Setup saves settings without losing anything, agents come from the settings file, and test workflows set up as it says.
> 7	
> 8	**Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix the rejected hand-back
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/793
> 13	
> 14	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 15	
> 16	- https://github.com/dokima-dev/dokima/issues/795
> 17	
> 18	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 19	
> 20	- https://github.com/dokima-dev/dokima/issues/779
> 21	- https://github.com/dokima-dev/dokima/issues/740
> 22	- https://github.com/dokima-dev/dokima/issues/780
> 23	- https://github.com/dokima-dev/dokima/issues/727
> 24	
> 25	
> 26	**User story:** Setup keeps a settings file intact, agents come from it, and test workflows install w

`4. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat in/07-worker.json; echo; python3 -c "
import json;d=json.load(open('in/08-planner.json'));print(json.dumps(d,indent=1)[:6000])"
```

> []
> {
>  "role": "worker",
>  "stage": null,
>  "run_id": "38987971294",
>  "commit_before": "c97f3fc8691d56d36d96c2c21f54f94291370125",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1548698,
>   "turns": 77,
>   "cost_usd": 4.3702782,
>   "tokens_in": 9590519,
>   "tokens_out": 55322
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/794/38987971294-worker.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38987971294",
>  "handback": {
>   "summary": "Setup edits only the agents lines of the settings file; agents read it; test workflows follow its setup group.",
>   "criteria": {
>    "794.1": "`dokima/setup.py` `read_settings` reads YAML; every workflow job running Dokima installs PyYAML first.",
>    "794.2": "`dokima/setup.py` `set_line` edits only the agents lines in place, so comment lines stay.",
>    "794.3": "`set_line` keeps a line's trailing comment when it changes or descends through that line.",
>    "794.4": "`saved_text` refuses to save if any other setting would change; a missing file or section is added.",
>    "794.5": "`dokima/agents.py` `agents_section` reads the agents section; `agent.yml` copies main's settings file.",
>    "794.6": "`agents_section` falls back to the old `agents.yml` beside the settings file; already green before.",
>    "794.7": "Each test workflow runs the install setting with eval after the test tools, before tests.",
>    "794.8": "Each test workflow installs the test_tools setting, re

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git diff c97f3fc HEAD -- tests/ | head -150; git log --oneline -8 --stat | head -60
```

> commit a598158769f4247aec934033d33f0f8be89db4ed
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 01:45:47 2026 +0000
> 
>     planner for #794 (run 38991862206)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_agents.py | 9 ++++++---
>  1 file changed, 6 insertions(+), 3 deletions(-)
> diff --git a/tests/test_agents.py b/tests/test_agents.py
> index 46249d0..7c4fe1a 100644
> --- a/tests/test_agents.py
> +++ b/tests/test_agents.py
> @@ -142,8 +142,11 @@ class Box:
>          f.write_text(text)
>  
>      def env(self, **extra):
> -        """The command's environment: the stubs first on PATH, this checkout's dokima importable, no real keys."""
> -        env = {k: v for k, v in os.environ.items() if k not in (TODAY_KEY, "DOKIMA_AGENT_KEY", "FAKE_EXIT")}
> +        """The command's environment: the stubs first on PATH, this checkout's dokima importable, no real keys.
> +
> +        Drops DOKIMA_SETTINGS, which an agent run's machine sets to main's settings file, so the box reads its own."""
> +        env = {k: v for k, v in os.environ.items()
> +               if k not in (TODAY_KEY, "DOKIMA_AGENT_KEY", "FAKE_EXIT", "DOKIMA_SETTINGS")}
>          env.update({"PATH": f"{self.bin}:{os.environ['PATH']}", "PYTHONPATH": ROOT, "FAKE_LOG": str(self.log)})
>          env.update(extra)
>          return env
> @@ -513,7 +516,7 @@ def test_a_runs_record_reads_its_agent_through_the_interface(record_property, tm
>      re

**Agent:** Previous review approved the plan; the only change since is the owner's fix to the 794.6 test. Checking that diff and running the tests now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json;d=json.load(open('/tmp/pack/plan.json'))
for c in d['acceptance_criteria']+d.get('non_functional',[]):
  print(c.get('test'), [e['test'] for e in c.get('edge_cases',[])])
print(d.get('test_changes'))
print([k for k in d])"; env | grep DOKIMA
```

> None ['tests/test_settings_setup.py::test_a_list_written_one_item_per_line_is_read_in_full', 'tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file']
> None ['tests/test_settings_setup.py::test_saving_a_setting_keeps_the_files_comments']
> None ['tests/test_settings_setup.py::test_saving_a_setting_keeps_comments_at_the_end_of_lines']
> None ['tests/test_settings_setup.py::test_saving_into_a_file_with_no_agents_section_leaves_the_rest', 'tests/test_settings_setup.py::test_saving_with_no_settings_file_yet_creates_it']
> None ['tests/test_settings_setup.py::test_the_agents_section_picks_each_roles_agent_and_model', 'tests/test_settings_setup.py::test_a_run_on_github_starts_the_model_the_agents_section_names']
> None ['tests/test_agents.py::test_a_run_starts_with_the_model_the_file_names']
> None ['tests/test_settings_test_setup.py::test_the_repos_install_command_runs_before_its_tests']
> None []
> None []
> None []
> {'tests/test_setup.py::test_settings_name_key_secret': "Setup now saves into the settings file's agents section, as the owner asked.", 'tests/test_setup.py::test_settings_give_roles': "Setup now saves into the settings file's agents section, as the owner asked.", 'tests/test_testmon.py::test_code_review_runs_only_affected_tests': 'Tools now come from settings; runs both jobs to see testmon still installed.', 'tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request': 'Owner asked tools come from the test tools setting; 794.8 pro

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json;d=json.load(open('/tmp/pack/plan.json'))
print(json.dumps(d['tests'],indent=0)); print(json.dumps(d['non_functional']))"
```

> {
> "794.1": [
> "tests/test_settings_setup.py::test_a_settings_file_holding_lists_is_read_in_full",
> "tests/test_settings_setup.py::test_a_list_written_one_item_per_line_is_read_in_full",
> "tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file"
> ],
> "794.2": [
> "tests/test_settings_setup.py::test_saving_a_setting_keeps_the_files_comments"
> ],
> "794.3": [
> "tests/test_settings_setup.py::test_saving_a_setting_keeps_comments_at_the_end_of_lines"
> ],
> "794.4": [
> "tests/test_settings_setup.py::test_saving_one_setting_leaves_every_other_setting_as_it_was",
> "tests/test_settings_setup.py::test_saving_into_a_file_with_no_agents_section_leaves_the_rest",
> "tests/test_settings_setup.py::test_saving_with_no_settings_file_yet_creates_it"
> ],
> "794.5": [
> "tests/test_settings_setup.py::test_the_agents_section_picks_each_roles_agent_and_model",
> "tests/test_settings_setup.py::test_a_run_on_github_starts_the_model_the_agents_section_names"
> ],
> "794.6": [
> "tests/test_agents.py::test_each_role_has_its_own_subscription_and_model",
> "tests/test_agents.py::test_a_run_starts_with_the_model_the_file_names"
> ],
> "794.7": [
> "tests/test_settings_test_setup.py::test_the_repos_install_command_runs_before_its_tests"
> ],
> "794.8": [
> "tests/test_settings_test_setup.py::test_the_test_tools_installed_come_from_the_test_tools_setting"
> ],
> "794.9": [
> "tests/test_settings_test_setup.py::test_the_repos_tests_run_on_the_python_the_settings_name"
> ],
> "794.10": [
> "tests/test_settings_setup.py::test_no_

`8. Bash`
```
cd /home/runner/work/dokima/dokima; T="tests/test_settings_setup.py tests/test_settings_test_setup.py tests/test_agents.py::test_each_role_has_its_own_subscription_and_model tests/test_agents.py::test_a_run_starts_with_the_model_the_file_names tests/test_agents.py::test_a_runs_record_reads_its_agent_through_the_interface"; timeout 500 python3 -m pytest -q $T 2>&1 | grep -E "passed|failed|FAILED|PASSED" | tail -30; echo ---unset; env -u DOKIMA_SETTINGS timeout 500 python3 -m pytest -q $T 2>&1 | tail -3
```

> assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
>         assert r.agent_started(), f"794.5: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
>             assert r.agent_started(), f"794.10: the {step} run never started its agent; it stopped at '{r.failed_step}':\n{r.tail()}"
> FAILED tests/test_settings_setup.py::test_a_settings_file_holding_lists_is_read_in_full - AssertionError: 794.1: the settings file's lists were not read in full; got {'protected_paths': '[.github/, ops/, "docs/private/"]', 'gates': {'required': '[all tests, Lint]'}, 'fence': {'test_setup_files': '[conftest.py, pytest.ini]'}, 'tests': {'dir': 'spec'}}
> FAILED tests/test_settings_setup.py::test_a_list_written_one_item_per_line_is_read_in_full - AssertionError: 794.1: lists written one item per line were not read in full; got {'protected_paths': {'- .github/': {}, '- ops/': {}}, 'gate': {'exclude': {'- card': {}, '- board wait': {}}, 'checks_wait_min': '30'}}
> FAILED tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file - AssertionError: 794.1: these jobs run Dokima before installing PyYAML, so they cannot read a settings file holding lists: acceptance-criteria.yml job list (first Dokima step: 'python3 -m dokima.che

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_each_role_has_its_own_subscription_and_model" -A36 tests/test_agents.py | grep -nE "env|subprocess|run\(" ; grep -n "DOKIMA_SETTINGS" -r dokima | head
```

> 29:277-    p = box.run("planner")
> dokima/agents.py:3:The settings file is `.dokima/agents.yml` under the current folder (or the path in DOKIMA_SETTINGS, where the
> dokima/agents.py:44:    return os.environ.get("DOKIMA_SETTINGS") or SETTINGS

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "    def run\b\|    def run(" -A8 tests/test_agents.py | head -20
```

> 84:    def run(prompt, model, out):
> 85-        """Log the start and hand back the test's review."""
> 86-        log(call="run", model=model, prompt=prompt)
> 87-        shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(str(out), "review.json"))
> 88-        return 0
> 89-
> 90-
> 91-    def models(out, log_dir):
> 92-        """zeta always runs zeta-1."""
> --
> 159:    def run(self, role, prompt="Plan issue 1.", **extra):
> 160-        """Start ROLE's agent through the interface with PROMPT; return the finished process."""
> 161-        f = self.repo.parent / "prompt.txt"
> 162-        f.write_text(prompt)
> 163-        return self.cli("run", role, str(f), str(self.out), **extra)
> 164-
> 165-    def calls(self):
> 166-        """Every stub call, oldest first, as {cmd, argv, token}."""
> 167-        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]

**Agent:** The fix does what the owner asked; tests fail the same way with or without the settings path. Writing the review from the last approved one.

`11. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/06-reviewer-plan.json'))['handback'];print(json.dumps(d,indent=1))"
```

> {
>  "previous_step": {
>   "did": [
>    "The order test now runs the planner, the plan review and the build in turn.",
>    "Each run must start exactly the next step, with settings asking to skip reviews."
>   ],
>   "decided": [
>    "Each run first checks it used the model the settings name for its role."
>   ],
>   "open": []
>  },
>  "verdict": "approve",
>  "summary": "The order test now covers every step the owner named; all ten asks have criteria and proper tests.",
>  "raises": [],
>  "answers": [],
>  "asks": [
>   {
>    "ask": "A settings file holding lists is read in full, on every machine that runs Dokima.",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "criterion": "794.1"
>   },
>   {
>    "ask": "Saving a setting through setup keeps the file's comments.",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "criterion": "794.2"
>   },
>   {
>    "ask": "Saving a setting through setup keeps comments written at the end of a line.",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "criterion": "794.3"
>   },
>   {
>    "ask": "Saving one setting through setup leaves every other setting as it was.",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "criterion": "794.4"
>   },
>   {
>    "ask": "The agents section of the settings file picks each role's agent and model.",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "criterion": "794.5"
>   },
>   {
>    "ask": "A repo with only the old agents file still runs each role's agent as named

`12. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
d=json.load(open('in/06-reviewer-plan.json'))['handback']
d['previous_step']={"did":["The old agents file test now ignores the run machine's settings path.","The same change goes into the run record test, with the same checks."],"decided":["Every other test and criterion stays as approved before."],"open":[]}
d['summary']="The old agents file test now reads its own settings, as the owner asked; the plan is otherwise unchanged."
for t in d['tests']:
    if t['test'].startswith('tests/test_agents.py::test_each_role'):
        t['why']="Pins the old agents file; now ignores the run machine's settings path."
json.dump(d,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 794 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#794](https://github.com/dokima-dev/dokima/issues/794) (setup saves safely, agents and test setup follow settings). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **What the planner changed:** they did what you asked in your `/plan` comment. The test for 794.6, which checks that a repo with only the old agents file still works, now ignores the machine's own settings path. So it reads the settings file it wrote, not main's. The run record test got the same change, and it still checks the same things.
- **Nothing else changed:** the rest of the plan is the same as the version approved last round. All ten of your asks still have a criterion and a test. No blockers were open for me to answer.
- **Tests today:** 23 fail and 3 pass. I ran them with the settings path set and unset and got the same result both times. The 3 passing tests check the old agents file and the run record, which already work today, as they should.
- **Not checked:** the worker's earlier code is not on the branch. So I could not confirm the fixed test passes against that code. The fix is a single change: the test now drops the settings path before it runs.

The worker should get it next.

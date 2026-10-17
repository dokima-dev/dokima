# reviewer (plan) for #795

Run: https://github.com/dokima-dev/dokima/actions/runs/39005331595

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (39.8KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/ca0b4d74-9c91-4b71-9c0e-31f7f2a257b1/tool-results/b983ad8ru.txt
> 
> Preview (first 2KB):
> # Issue #795: Test commands, branches and the bot follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 794 -->
> <!-- dokima-blocking: {"blocked_by": [794], "blocks": [796], "loop": []} -->
> Workflows take their test commands, test folder, branches and bot from the repo's settings, not Dokima's own.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/795#issuecomment-6229794051) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/794
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/796
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dok

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed 's/<img[^>]*>//g'
```

> # Issue #795: Test commands, branches and the bot follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 794 -->
> <!-- dokima-blocking: {"blocked_by": [794], "blocks": [796], "loop": []} -->
> Workflows take their test commands, test folder, branches and bot from the repo's settings, not Dokima's own.
> 
> **Plan** ·  Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/795#issuecomment-6229794051) with `/plan`, or say `/review`
> 
>  **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/794
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/796
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/789
> 
> 
> **User story:** Workflows run the repo's test commands and use its branches and bot, as its settings name.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** The all tests check runs the all-tests command from settings.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-795/tests/test_settings_workflows.py#L230"> Acceptance test</a>: The all tests check runs the all-tests command the settings name.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-795/tests/test_settings_workflows.py#L230">No settings file: the default command still runs every test</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/d

`3. Bash`
```
cd /tmp/pack; ls in; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1)[:12000])"
```

> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> []{
>  "kind": "user_story",
>  "title": "Test commands, branches and the bot follow settings",
>  "summary": "Workflows take their test commands, test folder, branches and bot from the repo's settings, not Dokima's own.",
>  "user_story": "Workflows run the repo's test commands and use its branches and bot, as its settings name.",
>  "acceptance_criteria": [
>   {
>    "text": "The all tests check runs the all-tests command from settings.",
>    "words": "The all tests check runs the all-tests command from settings.",
>    "source": "https://github.com/dokima-dev/dokima/issues/779",
>    "files": [
>     "dokima/settings.py",
>     "dokima/defaults.yaml",
>     ".github/workflows/full-suite.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "No settings file: the default command still runs every test",
>      "test": "tests/test_settings_workflows.py::test_the_all_tests_check_runs_the_all_tests_command_from_settings"
>     }
>    ]
>   },
>   {
>    "text": "Each criterion's check runs the per-criterion command from settings.",
>    "words": "Each criterion's check runs the per-criterion command from settings.",
>    "source": "https://github.com/dokima-dev/dokima/issues/779",
>    "files": [
>     "dokima/settings.py",
>     "dokima/defaults.yaml",
>     ".github/workflows/acceptance-criteria.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "No settings file: the default command runs the test and writes its report",
>      "test": "tests/test_settings_workflows.py::test_eac

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show --stat HEAD~1 | head -30; python3 -c "
import json;r=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(r,indent=1)[:9000])"
```

> commit fc3224bc177742fad2f86efc5639ffc0f54e667b
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 05:10:57 2026 +0000
> 
>     planner for #795 (run 39003792359)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_settings_workflows.py | 62 ++++++++++++++++++++++++++++------------
>  1 file changed, 44 insertions(+), 18 deletions(-)
> commit 5997fbdc6c6aee308f4dad8b253522890231764b
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 04:36:45 2026 +0000
> 
>     planner for #795 (run 39001283339)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/fixtures/settings_before_795.py | 118 +++++++
>  tests/test_agent.py                   |   7 +-
>  tests/test_checks.py                  |  11 +-
>  tests/test_keys.py                    |   5 +-
>  tests/test_merge_check.py             |   3 +-
>  tests/test_settings_workflows.py      | 606 ++++++++++++++++++++++++++++++++++
>  6 files changed, 742 insertions(+), 8 deletions(-)
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39003233968",
>  "commit_before": "5997fbdc6c6aee308f4dad8b253522890231764b",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 114372,
>   "turns": 13,
>   "cost_usd": 0.8555516000000001,
>   "tokens_in": 694875,
>   "tokens_out": 9814
>  },
>  "log": "https://github.com/dokima-

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_settings_workflows.py
```

> commit fc3224bc177742fad2f86efc5639ffc0f54e667b
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 05:10:57 2026 +0000
> 
>     planner for #795 (run 39003792359)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_settings_workflows.py b/tests/test_settings_workflows.py
> index 04d29b4..7821b01 100644
> --- a/tests/test_settings_workflows.py
> +++ b/tests/test_settings_workflows.py
> @@ -489,6 +489,26 @@ def test_agents_base_their_branches_and_pull_requests_on_the_default_branch_sett
>      assert base == "trunk", f"795.7: the worker's pull request goes to {base!r}, not trunk, the default branch setting"
>  
>  
> +def test_a_planners_new_branch_starts_from_the_default_branch_setting(record_property, tmp_path):
> +    """A planner's new branch starts from the default branch the settings name.
> +
> +    Proves 795.7. The settings name trunk as the default branch; trunk has a commit main lacks, and the issue has
> +    no branch yet. Runs a planner's checkout of agent.yml and a stand-in planner that notes whether trunk's commit
> +    is in what it starts from."""
> +    record_property("proves", "795.7")
> +    box = Box(tmp_path, TRUNK)
> +    trunk = box.commit("trunk", {"trunk.txt": "only on trunk\n"}, "trunk moves on", start="main")
> +    _, steps = steps_of("agent.yml", "run")
> +    look = stand_in("The planner", f"git merge-base --is-ancestor {trunk} HEAD && echo yes > /tmp/from_trunk.t

**Agent:** Reviewing the plan's fixes for the three earlier gaps; running the new tests now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_settings_workflows.py -p no:cacheprovider 2>&1 | grep -E "^(FAILED|ERROR|E  .*79[5]\.|[0-9]+ (passed|failed))" | head -60
```

> E       AssertionError: 795.1: the all tests check did not run the all-tests command from settings; job success, log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -q -p no:cacheprovider -n auto tests']
> E       AssertionError: 795.2: the criterion's check did not run the per-criterion command from settings; job failure, log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -rA -p no:cacheprovider -o junit_family=xunit1 --junitxml=r.xml tests/test_x.py::test_a']
> E       AssertionError: 795.3: with affected tests set to all, the review still ran tests from the baseline: ['pytest -q -rA --testmon --junitxml=/tmp/pytest-of-runner/pytest-0/test_setting_affected_tests_to0/all/pack/tests.xml']
> E       AssertionError: 795.3: with affected tests set to all, main still saved a baseline; log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -q --testmon', 'cache-saved']
> E       AssertionError: 795.4: on a clash with main, the planner was not handed main's new test in the settings' test folder spec/; it saw ['spec:', 'test_x.py']
> E       AssertionError: 795.4: the planner's test in the settings' test folder spec/ was handed to the worker as a clash: ['notes.md', 'spec/test_x.py']
> E       AssertionError: 795.5: the planner's push did not hold its test in the settings'

`7. Bash`
```
cd /home/runner/work/dokima/dokima; mkdir -p /tmp/rv && sed 's/for role in ("worker", "planner"):/for role in ("planner",):/' tests/test_settings_workflows.py > /tmp/rv/test_rv.py; head -40 tests/test_settings_workflows.py | grep -n import; PYTHONPATH=tests:. timeout 300 python3 -m pytest -q /tmp/rv/test_rv.py -k merging_main -p no:cacheprovider --rootdir=. 2>&1 | grep -E "^E |passed|failed" | head; sed -n 190,240p .github/workflows/agent.yml
```

> 25:import json
> 26:import os
> 27:import subprocess
> 28:import sys
> 31:import test_start as ts  # noqa: E402
> 32:from test_start import Ctx, N  # noqa: E402
>             assert result == "success", f"795.10: the {role}'s checkout failed\n{box.tail()}"
> E           AssertionError: 795.10: the planner's merge of main is authored by 'dokima-runtime[bot]', not other-bot[bot]
> E           assert 'dokima-runtime[bot]' == 'other-bot[bot]'
> E             
> E             - other-bot[bot]
> E             + dokima-runtime[bot]
> 1 failed, 14 deselected in 0.63s
>               [ ! -s /tmp/clashed.txt ] || echo "::notice title=Clash with main::the worker resolves $(paste -sd, /tmp/clashed.txt)"
>             fi
>             # A planner starts with main merged in, so it sees and can change the tests main added (#475). A branch
>             # that clashes with main stays unmerged for the worker; it takes only main's tests the branch never
>             # touched, and its plan check's base holds every test main changed, so none counts as the plan's own
>             # unless the branch's copy differs from main's, even after an earlier round took it. A test both sides
>             # changed is handed to the planner with its clash marked, to resolve (#662); the commit names main's copy
>             # it clashed with, so the worker's merge keeps the planner's resolution instead of handing it the clash.
>             if [ "$ROLE" = planner ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtim

`8. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
p=json.load(open('/tmp/pack/plan.json'))
src="https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729"
asks=[]
for i,c in enumerate(p['acceptance_criteria'],1):
    asks.append({"ask":c['words'],"source":"https://github.com/dokima-dev/dokima/issues/740" if i==6 else src,"criterion":f"795.{i}"})
whys=["One command run by one check.","One command run by each criterion's check.","One setting value turning the baseline off; the owner's words.","Clash handling follows one folder setting.","The push is limited to one folder.","Listed tests are left out of one check.","Everything uses one default branch setting; the owner's words.","Conversations saved on one branch.","One sender allowed to send one signal.","Commits carry one identity."]
beh=[{"criterion":f"795.{i}","one_behavior":True,"why":w} for i,w in enumerate(whys,1)]
edge=[{"criterion":f"795.{i}","cut":[],"missing":[]} for i in range(1,11)]
tw={
"test_the_all_tests_check_runs_the_all_tests_command_from_settings":"Runs the job with a setting and without; fails today, right reason.",
"test_each_criterions_check_runs_the_per_criterion_command_from_settings":"Runs the check job with the setting, default and main's older reader.",
"test_setting_affected_tests_to_all_runs_every_test_before_review":"Runs the review steps; the baseline must not be used with all.",
"test_setting_affected_tests_to_all_saves_no_baseline_on_main":"Runs every baseline job on a push; none saved with all.",
"test_a_planners_clash_with_main_takes_mains_tests_from_the_settings_test_folder":"Runs the planner's clash path with spec as the folder.",
"test_a_workers_clash_with_main_keeps_the_planners_test_in_the_settings_test_folder":"Runs the worker's clash path with spec as the folder.",
"test_the_planners_push_holds_only_files_in_the_settings_test_folder":"Runs the real push and reads the pushed branch.",
"test_tests_on_the_exclude_list_stay_out_of_the_all_te
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#795](https://github.com/dokima-dev/dokima/issues/795) (test commands, branches and the bot follow settings). Both checks on the review pass.

**The three gaps from the last review are now tested:**
- **New branch:** a new test runs a planner on an issue with no branch yet. It checks the planner starts from the default branch the settings name (trunk in the test).
- **Conversation link:** the records test now also checks that each record's conversation link points to the records branch the settings name.
- **Planner's merge:** the identity test now runs the planner's merge of main as well as the worker's, and checks who made each commit.

**Tests:** I ran all 15 new tests. They all fail today for the right reason: the feature is missing, not a crash. The worker's check comes first in the identity test, so I ran the planner's part on its own too. It also fails for the right reason.

**What I found:**
- Every one of your 10 asks has its own criterion. Each criterion is one behavior.
- No blockers. No normal-use cases are missing.

**Waiting on you:** I left the planner's three questions alone. Your words so far don't settle any of them:
- Should the test exclude list be built here and left out of [#744](https://github.com/dokima-dev/dokima/issues/744) (the test exclude list)?
- Should it be a new list of tests by path, separate from the gate's list of checks?
- Should pushed commits keep the app's own name, with only the fixed names moving to settings?

The plan waits until you answer them with `/plan`.

The review is in `/tmp/dokima-out/review.json`.

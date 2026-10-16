# reviewer (plan) for #764

Run: https://github.com/dokima-dev/dokima/actions/runs/38833390305

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #764: The settings stop declaring the plan and work labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 765 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The settings drop the old plan and work labels, which nothing reads since commands replaced them.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> - https://github.com/dokima-dev/dokima/issues/515
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/765
> 
> 
> **User story:** The settings no longer list the old plan and work labels, so no repo is asked to create them.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The settings no longer declare the old plan label.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-764/tests/test_manifest.py#L654"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: The settings no

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; sed -n 1,40p dokima/manifest.py; sed -n 640,690p tests/test_manifest.py; python3 -m pytest -q tests/test_manifest.py tests/test_audit.py tests/test_audit_cli.py tests/test_up_to_date_rule.py tests/test_audit_auto_merge.py 2>&1 | tail -15
```

> commit 0e8f34f13b0661084f6deb013f9718d09d319ec1
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 01:06:55 2026 +0000
> 
>     planner for #764 (run 38831595886)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_audit.py            | 30 +++++++++++++++---------------
>  tests/test_audit_auto_merge.py |  2 +-
>  tests/test_audit_cli.py        | 18 +++++++++---------
>  tests/test_manifest.py         | 32 ++++++++++++++++++++++++++++----
>  tests/test_up_to_date_rule.py  |  2 +-
>  5 files changed, 54 insertions(+), 30 deletions(-)
> """Everything Dokima needs from GitHub, declared in one place.
> 
> Labels, board fields and options, views, required checks, branch rules and the app's permissions. Plain data; nothing
> here calls GitHub.
> 
>     python3 -m dokima.manifest [root]   # prints every setting the code or workflows rely on that is left out here
> 
> undeclared(root) reads the Python under dokima/ and the workflows under .github/workflows/ and names, with the file,
> every label, field, option, view, check or branch rule they rely on that is not declared below, and every GitHub call
> made as the app whose permission, at the level it needs, is not granted below. A call it cannot tie to a permission is
> named too, so a new kind of call never slips through.
> """
> import ast
> import os
> import re
> import sys
> 
> LABELS = {
>     "plan": {"color": "1d76db", "description": "Starts the planner"},
>     "work":

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1 -- tests/test_audit.py tests/test_audit_cli.py tests/test_up_to_date_rule.py tests/test_audit_auto_merge.py | head -150; rm -rf /tmp/cp && cp -r . /tmp/cp && cd /tmp/cp && sed -i '/^    "plan": {"color"/d;/^    "work": {"color"/d' dokima/manifest.py && python3 -m dokima.manifest . ; echo rc=$?; python3 -m pytest -q -x 2>&1 | tail -3
```

> diff --git a/tests/test_audit.py b/tests/test_audit.py
> index 64af427..a506cdc 100644
> --- a/tests/test_audit.py
> +++ b/tests/test_audit.py
> @@ -170,8 +170,8 @@ def open_setup(body="Old drift\n"):
>  def drifted():
>      """A repo with seven differences from the manifest, one of each kind."""
>      g = GitHub()
> -    del g.label_list["plan"]
> -    g.label_list["work"]["color"] = "000000"
> +    del g.label_list["filed-by-dokima"]
> +    g.label_list["autopilot"]["color"] = "000000"
>      del g.field_map["Action"]["Autopilot"]
>      g.field_map["Priority"]["Blocker"]["color"] = "ORANGE"
>      g.view_map["Autopilot"]["filter"] = "label:autopilot"
> @@ -204,7 +204,7 @@ def codeowners(tmp_path, text):
>  def test_each_difference_gets_one_line_saying_what_is_off_and_what_dokima_needs(record_property):
>      """Each setting that differs gets one line saying what is off and what Dokima needs.
>  
> -    Proves 283.1. The faked repo differs in seven ways: the plan label is missing, the work label's color is 000000, the Action field
> +    Proves 283.1. The faked repo differs in seven ways: the filed-by-dokima label is missing, the autopilot label's color is 000000, the Action field
>      has no Autopilot option, the Blocker priority option is ORANGE, the Autopilot view filters on label:autopilot, main's
>      rule lacks the Acceptance criteria check, and the app has issues: read. The audit returns seven single lines, one
>      per difference, each naming the setting and the value Dokima needs (with the live value 

`4. Bash`
```
cd /tmp/cp && python3 -m pytest -q 2>&1 | grep -E "FAILED|ERROR|passed|failed" | tail -20
```

> Command did not complete within its 600s timeout and was moved to the background (ID: b9se2y3rg). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/490f8a59-378c-4c09-8c26-450934bac1cd/tasks/b9se2y3rg.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`5. Bash`
```
cd /tmp/cp && grep -rnE "LABELS\[.(plan|work)|label_list\[.(plan|work)|labels.\]\[.(plan|work)" tests dokima | head; python3 -m pytest -q -x -p no:cacheprovider 2>&1 | grep -E "^(FAILED|ERROR)|Error" | head
```

> E       AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> tests/test_agents.py:220: AssertionError
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Plan tests are verified as failing for the right reason. Now I'm checking one unrelated failure, then I'll write the review.

`6. Bash`
```
python3 -m pytest -q -p no:cacheprovider tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder 2>&1 | tail -2
```

> ?        +++)
> 1 failed in 0.26s

**Agent:** Plan tests are verified as failing for the right reason. Now I'm checking one unrelated failure, then I'll write the review.

`7. Bash`
```
cd /home/runner/work/dokima/dokima && python3 -m pytest -q -p no:cacheprovider tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder 2>&1 | tail -2
```

`8. Bash`
```
env | grep -iE "dokima|model" | sed 's/=.*/=.../'
```

> GITHUB_WORKSPACE=...
> LOG_URL=...
> GITHUB_TRIGGERING_ACTOR=...
> PWD=...
> GITHUB_WORKFLOW_REF=...
> DOKIMA_SETTINGS=...
> MODEL=...
> GITHUB_ACTOR=...
> GITHUB_REPOSITORY=...
> RUNNER_WORKSPACE=...
> GITHUB_REPOSITORY_OWNER=...
> OUT=...

`9. Bash`
```
cd /tmp/cp && python3 -m pytest -q -p no:cacheprovider tests/test_manifest.py tests/test_audit.py tests/test_audit_cli.py tests/test_up_to_date_rule.py tests/test_audit_auto_merge.py 2>&1 | tail -2
```

> .................                                                        [100%]
> 89 passed in 14.83s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`10. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria: the settings drop the old plan label, and the old work label.",
          "The planner added one test for each and moved sample data in other tests to labels that stay."],
  "decided": ["Dropping both labels needs no change outside the settings file."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries both asks, each with one test that fails today because the label is still declared.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The settings no longer declare the old plan label.", "source": "https://github.com/dokima-dev/dokima/issues/764", "criterion": "764.1"},
  {"ask": "The settings no longer declare the old work label.", "source": "https://github.com/dokima-dev/dokima/issues/764", "criterion": "764.2"}],
 "behaviors": [
  {"criterion": "764.1", "one_behavior": true, "why": "One label leaves the settings."},
  {"criterion": "764.2", "one_behavior": true, "why": "One label leaves the settings."}],
 "edge_cases": [
  {"criterion": "764.1", "cut": [], "missing": []},
  {"criterion": "764.2", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_manifest.py::test_the_settings_no_longer_declare_the_plan_label", "only_its_behavior": true, "why": "Fails today naming 764.1; passes once the plan label is gone."},
  {"test": "tests/test_manifest.py::test_the_settings_no_longer_declare_the_work_label", "only_its_behavior": true, "why": "Fails today naming 764.2; passes once the work label is gone."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 764 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step did line 2 holds 18 words, over its cap of 15: cut 3, keep the facts

`11. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["The planner wrote two criteria: drop the old plan label, drop the work label.","It added one test each and moved other tests' sample data to kept labels."]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 764 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`12. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["The planner wrote two criteria: drop the old plan label, drop the work label.","It added one test each and moved other tests' sample data to kept labels."]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 764 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

**Agent:** I approved the plan for [#764](https://github.com/dokima-dev/dokima/issues/764) (stop declaring the old plan and work labels). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks covered:** each of the owner's two asks has its own criterion: 764.1 drops the plan label, 764.2 drops the work label. None is missing, none is added.
- **Tests fail today for the right reason:** both new tests fail only because the two labels are still in the settings.
- **The fix is enough:** on a copy with the two labels removed, `python3 -m dokima.manifest .` reports nothing missing. The five changed test files also pass there, 89 of 89.
- **Other test changes are safe:** the planner only switched sample data in other tests from plan and work to labels that stay (filed-by-dokima, autopilot). What those tests check is unchanged.

I raised nothing. One unrelated test, `tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder`, fails on this branch too. The run's environment sets `MODEL` and `DOKIMA_SETTINGS`, which likely overrides the settings file it tests. I didn't confirm that or raise it.

I also started a full-suite run on the copy. It hit the 10-minute limit and moved to the background; I didn't wait for its result.

`13. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/490f8a59-378c-4c09-8c26-450934bac1cd/tasks/b9se2y3rg.output
```

> _____________ test_any_model_the_role_names_is_passed_to_its_agent _____________
>     def test_any_model_the_role_names_is_passed_to_its_agent(record_property, tmp_path):
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_each_role_has_its_own_subscription_and_model - AssertionError: 698.3: the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent - AssertionError: 698.4: Claude Code got model 'claude-opus-5-5', not the role's claude-unreleased-9-9
> FAILED tests/test_agents.py::test_a_role_the_file_leaves_out_starts_claude_code_as_today - AssertionError: 698.7: the worker the file names should run on claude-haiku-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_a_role_missing_its_model_stops_and_names_the_role - AssertionError: 698.8: a planner with no model line did not stop with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_an_unknown_agent_stops_before_any_agent - AssertionError: 698.10: an unknown agent did not stop the planner with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_a_runs_record_reads_its_agent_through_the_interface - AssertionEr

**Agent:** The full test run finished, with the plan and work labels removed on a copy: 1,250 tests passed and 9 failed. That doesn't change my approval.

- **The 9 failures are unrelated to the labels.** All are in `tests/test_agents.py` and are about which model and token each role runs on. None touches labels or the settings in [#764](https://github.com/dokima-dev/dokima/issues/764).
- **The likely cause is this run's setup.** The tests read the planner's model from a settings file and expect `claude-sonnet-5-5`, but got `claude-opus-5-5`. This run sets `MODEL` and `DOKIMA_SETTINGS`, which probably override that file. I confirmed one of the nine fails on the branch as it stands, with the labels still in. I didn't check the other eight there or test the override.

My earlier note of one unrelated failure was incomplete: there are nine, all in that one file. I raised none of them.

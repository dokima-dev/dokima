# reviewer (plan) for #896

Run: https://github.com/dokima-dev/dokima/actions/runs/39271855844

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (32.7KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/45b79f61-6f1c-4bb3-98e4-e8d600a3fc3f/tool-results/b5wm5nz4g.txt
> 
> Preview (first 2KB):
> # Issue #896: Settings may name only declared agent keys
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [913], "loop": []} -->
> A setting naming an agent key the shared workflow never receives is refused with one clear line.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/911 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/911/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/913
> 
> 
> **User story:** Owners who name an unusable agent key learn why in one line, from the audit and the run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Settings may name only the agent keys the entry 

`2. Bash`
```
cd /tmp/pack; sed -n '/^## /,$p' issue.md | head -400; ls in
```

> ## Comments
> 
> ### dokima-runtime on issue #896 (2026-10-19T13:16:51Z)
> 
> Autopilot: switched on, starting work
> 
> ### dokima-runtime on issue #896 (2026-10-19T13:17:15Z)
> 
> <!-- dokima-record -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/worker.svg" width="16" height="16" align="absmiddle" alt="worker"> No change: refusing undeclared key names breaks earlier decided behavior, so this goes back for a decision.
> 
> **Raised:**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocker.svg" width="16" height="16" align="absmiddle" alt="blocker"> **Ask conflicts:** The ask limits keys to four declared names, but earlier criteria promise any secret name works, adopters included. Owner must pick one. · for the planner
>   - Evidence: Guard in `key()` fails `test_each_role_reads_its_model_key_from_the_secret_its_settings_name` (812.3), `test_each_role_has_its_own_subscription_and_model` (698.3).
> 
> <details><summary><b>What it built</b></summary>
> 
> - Its own test run: Guard tried in `key()`: `pytest -q` on five agent test files, 10 failed, 46 passed.
> 
> </details>
> 
> <details><summary>Full record</summary>
> 
> (full record: in/, from the record files)
> 
> </details>
> 
> **Next:** The reviewer starts now.
> 
> <!-- dokima-stats -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/doki

`3. Bash`
```
cd /tmp/pack; sed -n '1,/^## Comments/p' issue.md | sed -n '20,200p'; cat open_blockers.json; python3 -m json.tool plan.json
```

> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Settings may name only the agent keys the entry workflow declares; a job refuses any other.
>   *<a href="https://github.com/dokima-dev/dokima/blob/39c4730ea0847e0172e07b3f790becb995d4ba1e/tests/test_declared_keys.py#L63"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: Settings may name each agent key entry.yml declares, and no other.*
>   <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/39c4730ea0847e0172e07b3f790becb995d4ba1e/tests/test_declared_keys.py#L63">A declared key other than Claude's still works.</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When settings name an undeclared key, the setup audit reports it in one line saying what to do.
>   *<a href="https://github.com/dokima-dev/dokima/blob/39c4730e

`4. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('06-reviewer-plan.json'));print(json.dumps(d,indent=1)[:8000])"; python3 -c "
import json;d=json.load(open('07-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39268610652",
>  "commit_before": "7c4d1f8cb4306d06e0fd67e69de9296053d6e260",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1035531,
>   "turns": 13,
>   "cost_usd": 0.6754278,
>   "tokens_in": 638017,
>   "tokens_out": 7031
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/896/39268610652-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39268610652",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote four tests: allowed keys, the audit line, the job's failure, the docs.",
>     "Older tests now name declared keys instead of made-up ones."
>    ],
>    "decided": [
>     "The allowed keys are read from the shared workflow's own list.",
>     "The promise that any key name works is retired, as the owner said."
>    ],
>    "open": []
>   },
>   "verdict": "approve",
>   "summary": "The plan carries all four of the owner's asks, and each new test fails today for the right reason.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "The settings may name only agent keys `entry.yml` declares (today `CLAUDE_CODE_OAUTH_TOKEN`, `CODEX_API_KEY`, `KIMI_API_KEY`).",
>     "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634",
>     "criterion": "896.1"
>    },
>    {
>     "ask": "The setup audit reports, in one line, a setting that names any other key: it will never reach the jobs; use a declared name, or ask f

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD HEAD~1 | head -40; git diff main --stat; git log --oneline main -3
```

> commit 39c4730ea0847e0172e07b3f790becb995d4ba1e
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 14:45:09 2026 +0000
> 
>     planner for #896 (run 39271429699)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_thin_install.py | 16 ++++++++--------
>  1 file changed, 8 insertions(+), 8 deletions(-)
> 
> commit b5e0682bf37bcda30f70cf545f037007379dd55c
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 14:43:04 2026 +0000
> 
>     Main's tests for the planner of #896
>     
>     Clash-with-main: tests/test_thin_install.py ee05f7e306b1980e42885a9dff715e14b99aa9bc
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_hotfix_no_change.py | 26 ++++++++++++++++++++++++++
>  tests/test_keys.py             | 11 +++++++++++
>  2 files changed, 37 insertions(+)
>  .github/workflows/agent.yml     |   7 +-
>  README.md                       |   2 +-
>  docs/wiki/Installing.md         |   2 +-
>  dokima/agent_next.py            |  11 ----
>  dokima/agents.py                |  15 ++++-
>  dokima/audit.py                 |  12 +++-
>  tests/test_agent_codex.py       |   2 +-
>  tests/test_agent_kimi.py        |   2 +-
>  tests/test_agents.py            |  44 ++++++-------
>  tests/test_audit_secrets.py     |   4 +-
>  tests/test_declared_keys.py     | 142 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_comm

**Agent:** Reviewing the re-plan after the clash with main; checking the test changes and running the new tests against main now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1 HEAD; git merge-base HEAD main; git diff $(git merge-base HEAD main) HEAD --stat
```

> diff --git a/tests/test_thin_install.py b/tests/test_thin_install.py
> index ad26d221..51fdfcf4 100644
> --- a/tests/test_thin_install.py
> +++ b/tests/test_thin_install.py
> @@ -256,7 +256,7 @@ def test_a_run_with_no_bot_set_up_fails_saying_how_to_set_it_up(record_property,
>  
>      Proves 812.4. Runs agent.yml's planner run in a repo with no app id variable and no app key secret, then in one
>      with the app id but no key. Each run must fail, with an error naming the DOKIMA_APP_ID variable, the
> -    DOKIMA_APP_KEY secret and the keys environment they go in."""
> +    DOKIMA_APP_KEY secret and that they go in as repo secrets, since an environment's never reach the jobs (#884)."""
>      record_property("proves", "812.4")
>      for case, drop_secrets, drop_vars in (("no bot", ("DOKIMA_APP_KEY",), ("DOKIMA_APP_ID",)),
>                                            ("no app key", ("DOKIMA_APP_KEY",), ())):
> @@ -265,9 +265,9 @@ def test_a_run_with_no_bot_set_up_fails_saying_how_to_set_it_up(record_property,
>          result = box.run("agent.yml", "run", name="planner", role="planner")
>          assert result == "failure", f"812.4: with {case} set up, the run did not fail; job {result}"
>          errors = [l for l in "\n".join(box.log).splitlines() if "::error" in l]
> -        said = [l for l in errors if "DOKIMA_APP_ID" in l and "DOKIMA_APP_KEY" in l and "keys" in l]
> -        assert said, (f"812.4: with {case} set up, no error says to add DOKIMA_APP_ID and DOKIMA_APP_KEY to the keys "
> -               

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main HEAD -- tests/test_thin_install.py tests/test_keys.py tests/test_hotfix_no_change.py
```

> diff --git a/tests/test_thin_install.py b/tests/test_thin_install.py
> index ee05f7e3..51fdfcf4 100644
> --- a/tests/test_thin_install.py
> +++ b/tests/test_thin_install.py
> @@ -224,9 +224,9 @@ def agent_step_env(tmp, settings, secrets):
>  
>  # 812.3 ------------------------------------------------------------------------------------------------------------
>  
> -MY_KEY = """agents:
> +CODEX_API_KEY = """agents:
>    subscriptions:
> -    mine: {agent: claude, key: MY_KEY}
> +    mine: {agent: claude, key: CODEX_API_KEY}
>    roles:
>      planner: {subscription: mine, model: claude-opus-5-5}
>  """
> @@ -236,14 +236,14 @@ def test_each_role_reads_its_model_key_from_the_secret_its_settings_name(record_
>      """A role's agent gets its key from the secret the adopter's settings name.
>  
>      Proves 812.3. The adopter's repo holds no Dokima code; its settings give the planner a subscription whose key is the
> -    secret MY_KEY. Runs agent.yml's planner run up to its agent and checks the agent got MY_KEY's value, not the
> +    secret CODEX_API_KEY. Runs agent.yml's planner run up to its agent and checks the agent got CODEX_API_KEY's value, not the
>      default secret's. Then settings naming no agents: the agent gets the default secret's value."""
>      record_property("proves", "812.3")
> -    env = agent_step_env(tmp_path / "named", MY_KEY, {"MY_KEY": "fake-my-key"})
> +    env = agent_step_env(tmp_path / "named", CODEX_API_KEY, {"CODEX_API_KEY": "fake-my-key"})
>      assert env.get("CLAUDE_CODE_OAUTH_TOKEN") == "f

`8. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt main 2>&1|tail -1; cp tests/*.py /tmp/wt/tests/; cd /tmp/wt; timeout 900 python3 -m pytest -q tests/test_declared_keys.py 2>&1 | grep -E "^(FAILED|E  .*89|[0-9]+ (passed|failed))|AssertionError" | head -30
```

> E       AssertionError: 896.1: settings naming MY_KEY, which entry.yml does not declare (['CLAUDE_CODE_OAUTH_TOKEN', 'CODEX_API_KEY', 'KIMI_API_KEY']), were accepted: 'MY_KEY\n'
> tests/test_declared_keys.py:78: AssertionError
> E       AssertionError: 896.2: for settings naming MY_KEY the audit should give one line saying it will never reach the jobs, to use a declared name or ask for it to be declared in a release; it said []
> tests/test_declared_keys.py:90: AssertionError
> E       AssertionError: 896.3: the run called MY_KEY missing instead of undeclared: ["::error title=No model key::The secret MY_KEY, which holds the planner's model key, is missing: add it as a repo secret (Settings, Secrets and variables, Actions), not only in an environment, which never reaches these jobs.", "::error title=Not started::The secret MY_KEY, which holds the planner's model key, is missing: add it as a repo secret (Settings, Secrets and variables, Actions), not only in an environment, which never reaches these jobs.", "- The secret MY_KEY, which holds the planner's model key, is missing: add it as a repo secret (Settings, Secrets and variables, Actions), not only in an environment, which never reaches these jobs.", '   "The secret MY_KEY, which holds the planner\'s model key, is missing: add it as a repo secret (Settings, Secrets and variables, Actions), not only in an environment, which never reaches these jobs."']
> tests/test_declared_keys.py:110: AssertionError
> E           AssertionError: 896.4

**Agent:** All four new tests fail on main for the right reason. Now checking the older changed tests still pass on main and on the branch.

`9. Bash`
```
cd /tmp/wt; timeout 900 python3 -m pytest -q tests/test_agents.py tests/test_audit_secrets.py tests/test_settings_comments.py tests/test_settings_setup.py tests/test_thin_install.py tests/test_agent_codex.py tests/test_agent_kimi.py 2>&1 | tail -5; cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_declared_keys.py tests/test_agents.py tests/test_audit_secrets.py tests/test_settings_comments.py tests/test_settings_setup.py tests/test_thin_install.py tests/test_agent_codex.py tests/test_agent_kimi.py 2>&1 | tail -5
```

> ................................................................         [100%]
> 64 passed in 64.30s (0:01:04)
>   ## planner: Report this run's GitHub calls (exit 0)
>   ::notice title=GitHub calls::none
>   
> assert []
> 3 failed, 65 passed in 63.76s (0:01:03)

`10. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_thin_install.py 2>&1 | grep -E "^FAILED|AssertionError: " | head
```

> E           AssertionError: 812.4: with no bot set up, no error says to add DOKIMA_APP_ID and DOKIMA_APP_KEY as a repo secret; its errors: ["::error title=No bot::No bot is set up: add the app's id as the variable DOKIMA_APP_ID and its private key as the secret DOKIMA_APP_KEY, both in the repo's keys environment (Settings, Environments, keys).", "::error title=Not started::No bot is set up: add the app's id as the variable DOKIMA_APP_ID and its private key as the secret DOKIMA_APP_KEY, both in the repo's keys environment (Settings, Environments, keys)."]
> E           AssertionError: 812.5: with no CLAUDE_CODE_OAUTH_TOKEN secret, nothing the run said names CLAUDE_CODE_OAUTH_TOKEN and says to add it as a repo secret
> FAILED tests/test_thin_install.py::test_a_run_with_no_bot_set_up_fails_saying_how_to_set_it_up - AssertionError: 812.4: with no bot set up, no error says to add DOKIMA_APP_ID and DOKIMA_APP_KEY as a repo secret; its errors: ["::error title=No bot::No bot is set up: add the app's id as the variable DOKIMA_APP_ID and its private key as the secret DOKIMA_APP_KEY, both in the repo's keys environment (Settings, Environments, keys).", "::error title=Not started::No bot is set up: add the app's id as the variable DOKIMA_APP_ID and its private key as the secret DOKIMA_APP_KEY, both in the repo's keys environment (Settings, Environments, keys)."]
> FAILED tests/test_thin_install.py::test_a_run_with_no_model_key_fails_naming_the_secret_and_how_to_add_it - AssertionError: 812.5: 

`11. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_declared_keys.py tests/test_agents.py tests/test_audit_secrets.py tests/test_settings_comments.py tests/test_settings_setup.py 2>&1 | grep -E "^FAILED|passed|failed"
```

> FAILED tests/test_declared_keys.py::test_the_install_docs_say_only_declared_keys_reach_the_jobs - AssertionError: 896.4: README.md has no sentence saying settings may name only ['CLAUDE_CODE_OAUTH_TOKEN', 'CODEX_API_KEY', 'KIMI_API_KEY']
> 1 failed, 47 passed in 42.14s

`12. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_declared_keys.py; grep -n -i "declare" README.md docs/wiki/Installing.md
```

> """Tests for #896: the settings may name only the agent keys entry.yml declares.
> 
> GitHub hands a reusable workflow in another account's repo only the secrets it declares by name, so a key outside
> entry.yml's list never reaches the jobs. The setup audit reports such a key in one line, a job naming it fails with that
> same line rather than as a missing key, and the install docs say so. The declared keys are read from entry.yml itself,
> so the tests follow it when a release declares another.
> """
> import os
> import re
> import subprocess
> import sys
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> sys.path.insert(0, ROOT)
> sys.path.insert(0, os.path.join(ROOT, "tests"))
> import test_settings_workflows as sw  # noqa: E402
> from test_audit import REPO, GitHub, audit  # noqa: E402
> from test_thin_install import everything_said, read_yaml, with_context  # noqa: E402
> 
> ENTRY = os.path.join(ROOT, ".github", "workflows", "entry.yml")
> DOCS = ("README.md", os.path.join("docs", "wiki", "Installing.md"))
> 
> 
> def declared():
>     """The agent keys entry.yml declares: every secret it takes, less the app's own key."""
>     return sorted(set(read_yaml(ENTRY)["on"]["workflow_call"]["secrets"]) - {"DOKIMA_APP_KEY"})
> 
> 
> def settings(key, role="worker"):
>     """A settings file putting ROLE on a Claude subscription whose key is the secret KEY."""
>     return (f"agents:\n  subscriptions:\n    mine:\n      agent: claude\n      key: {key}\n"
>             f"  roles:\n    {role}:\n      subscription: 

**Agent:** The re-plan only adapts one older test file to main's latest change, and keeps it. Writing the hand-back.

`13. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner re-planned after main changed the install test file.",
          "That older test now keeps main's repo secret wording and uses a declared key name."],
  "decided": ["The four criteria and their tests stay as approved before."],
  "open": []},
 "verdict": "approve",
 "summary": "The re-plan keeps all four owner asks, and each new test still fails on main for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The settings may name only agent keys `entry.yml` declares (today `CLAUDE_CODE_OAUTH_TOKEN`, `CODEX_API_KEY`, `KIMI_API_KEY`).", "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634", "criterion": "896.1"},
  {"ask": "The setup audit reports, in one line, a setting that names any other key: it will never reach the jobs; use a declared name, or ask for that name to be declared in a release.", "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634", "criterion": "896.2"},
  {"ask": "A job whose settings name an undeclared key fails with that same message, not as a missing key.", "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634", "criterion": "896.3"},
  {"ask": "Docs say the same", "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634", "criterion": "896.4"},
  {"ask": "update the earlier criteria that promised any name.", "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634", "criterion": "896.1"},
  {"ask": "Settings may name any agent key, but only declared names reach jobs; others fail as a missing key.", "source": "https://github.com/dokima-dev/dokima/issues/896", "criterion": "896.3"}
 ],
 "behaviors": [
  {"criterion": "896.1", "one_behavior": true, "why": "One rule: a declared key is accepted, any other refused."},
  {"criterion": "896.2", "one_behavior": true, "why": "One audi
```

> (Bash completed with no output)

**Agent:** I approved the re-plan for [#896](https://github.com/dokima-dev/dokima/issues/896) (settings may name only declared agent keys). The hand-back passed both checks and is at `/tmp/dokima-out/review.json`.

- **What changed:** the planner re-planned because main's change in [#906](https://github.com/dokima-dev/dokima/pull/906) clashed with one install test file. That test now keeps main's new "add it as a repo secret" wording, and its made-up key name is swapped for a declared one. The four criteria are the same as the plan approved earlier.
- **Owner's asks:** all four asks in the owner's decision comment have a criterion. So does "update the earlier criteria that promised any name", which the older-test changes carry out. Nothing is missing.
- **New tests on main:** I ran all four and each fails for the right reason. Main accepts `MY_KEY`, the audit says nothing about it, the job calls it "missing", and the README doesn't state the rule.
- **Older changed tests:** all 64 pass on main.

Three tests currently fail on the branch itself, for these reasons. They don't block the plan, but the build has to fix them:
- `test_thin_install.py` 812.4 and 812.5 fail because the branch doesn't yet have main's repo-secret wording in the code. Bringing the branch up to date with main should fix them; they already pass on main.
- 896.4 fails because the branch's README has no sentence listing the declared keys. The install guide has it, but the worker will have to add it to the README.

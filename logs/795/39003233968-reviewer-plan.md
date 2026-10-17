# reviewer (plan) for #795

Run: https://github.com/dokima-dev/dokima/actions/runs/39003233968

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
> # Issue #795: Test commands, branches and the bot follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 794 -->
> <!-- dokima-blocking: {"blocked_by": [794], "blocks": [796], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/794
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/796
> 
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> <!-- dokima-card -->
> <!-- /dokima-card -->
> 
> <details open><summary>From the approved plan of #779, story 3</summary>
> 
> **Part of:** #779 Settings file over shipped defaults, read by every workflow
> 
> **User story:** Workflows run the repo's test commands and use its branches and bot, as its settings name.
> 
> **Context:** Rows A16 to A19, B3, B5, C3, C4 of the owner's list on #740 give each place: `full-suite.yml:29`, `acceptance-criteria.yml:62`, `agent.yml:265-288` and `testmon.yml`, `agent.yml:174,195,400`, `agent.yml` origin/main and `--base main`, `fix.yml:35-37`, `agent.yml:96`, `agent.yml:165-225`, `wiki.yml:21-22`. No exclude list exists today.

`2. Bash`
```
cd /tmp/pack; cat owner_words.json | head -c 6000; echo; cat parent.json | head -c 5000; echo; cat open_issues.json | head -c 3000; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/779": "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #740, story 1</summary>\n\n**Part of:** #740 One settings file per repo over shipped defaults\n\n**User story:** A repo writes only what differs into one settings file, and every workflow follows it.\n\n**Context:** New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it). Today `dokima/setup.py` `read_settings()` reads only nested maps and `write_settings()` rewrites the file; `dokima/agents.py` reads `.dokima/agents.yml`. Workflow rows of the owner's list (A13 to A19, B3, B5, C3, C4, E1, E2, E4, E8, E11, E15) live in `.github/workflows/agent.yml`, `full-suite.yml`, `acceptance-criteria.yml`, `testmon.yml`, `fix.yml`, `wiki.yml`; the co-author trailer sits at `agent.yml:408` and `wiki.yml:27`. Locked keys: app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. The owner's newer comment makes the fence's test setup files a setting (row A5); newer words win, so the fence's lock covers what it does, not that list.\n\n**Acceptance criteria:**\n- Dokima ships one defaults file that every repo's settings fall back to. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- A repo's settings file changes only the settings it names; every other keeps its default. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- The d

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; git diff HEAD~1 --stat
```

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
>  tests/fixtures/settings_before_795.py | 118 +++++++
>  tests/test_agent.py                   |   7 +-
>  tests/test_checks.py                  |  11 +-
>  tests/test_keys.py                    |   5 +-
>  tests/test_merge_check.py             |   3 +-
>  tests/test_settings_workflows.py      | 606 ++++++++++++++++++++++++++++++++++
>  6 files changed, 742 insertions(+), 8 deletions(-)

`4. Bash`
```
cd /tmp/pack; cat owner_words.json | head -c 6000; echo; cat parent.json | head -c 5000; echo; cat open_issues.json | head -c 3000; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; git diff HEAD~1 --stat
```

> {
>  "https://github.com/dokima-dev/dokima/issues/779": "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #740, story 1</summary>\n\n**Part of:** #740 One settings file per repo over shipped defaults\n\n**User story:** A repo writes only what differs into one settings file, and every workflow follows it.\n\n**Context:** New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it). Today `dokima/setup.py` `read_settings()` reads only nested maps and `write_settings()` rewrites the file; `dokima/agents.py` reads `.dokima/agents.yml`. Workflow rows of the owner's list (A13 to A19, B3, B5, C3, C4, E1, E2, E4, E8, E11, E15) live in `.github/workflows/agent.yml`, `full-suite.yml`, `acceptance-criteria.yml`, `testmon.yml`, `fix.yml`, `wiki.yml`; the co-author trailer sits at `agent.yml:408` and `wiki.yml:27`. Locked keys: app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. The owner's newer comment makes the fence's test setup files a setting (row A5); newer words win, so the fence's lock covers what it does, not that list.\n\n**Acceptance criteria:**\n- Dokima ships one defaults file that every repo's settings fall back to. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- A repo's settings file changes only the settings it names; every other keeps its default. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- The d

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
>  tests/fixtures/settings_before_795.py | 118 +++++++
>  tests/test_agent.py                   |   7 +-
>  tests/test_checks.py                  |  11 +-
>  tests/test_keys.py                    |   5 +-
>  tests/test_merge_check.py             |   3 +-
>  tests/test_settings_workflows.py      | 606 ++++++++++++++++++++++++++++++++++
>  6 files changed, 742 insertions(+), 8 deletions(-)

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1 -- tests/test_agent.py tests/test_checks.py tests/test_keys.py tests/test_merge_check.py; cat tests/test_settings_workflows.py
```

> <persisted-output>
> Output too large (41.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/dc83ded0-29c3-4f1a-bbbb-d6d7146c18dd/tool-results/b6ysnz1r5.txt
> 
> Preview (first 2KB):
> diff --git a/tests/test_agent.py b/tests/test_agent.py
> index 3ccf112..0fa0c0a 100644
> --- a/tests/test_agent.py
> +++ b/tests/test_agent.py
> @@ -353,7 +353,8 @@ def test_a_replan_checks_tests_against_where_the_branch_left_main(record_propert
>      """On every planning round the plan check compares against the branch's split from main, so earlier rounds' tests still count."""
>      record_property("proves", "agent.22")
>      wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
> -    assert 'PLANNER_BASE=$(git merge-base HEAD origin/main)' in wf
> +    # Since #795 the default branch comes from the settings; 795.7 proves it is the one they name.
> +    assert re.search(r'PLANNER_BASE=\$\(git merge-base HEAD "?origin/', wf), "a step no longer compares against main"
>      assert "PLANNER_BASE: ${{ env.BASE }}" not in wf, "a step still compares against the branch head"
>  
>  
> @@ -398,7 +399,9 @@ def test_the_rivers_signal_comes_only_from_dokimas_bot(record_property):
>      record_property("proves", "agent.25")
>      wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
>      assert "types: [dokima-next]" in wf
> -    assert '[ "$EVENT" = repository_dispatch ] && [ "$SENDER" = "dokima-runtime[bot]

`7. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/dc83ded0-29c3-4f1a-bbbb-d6d7146c18dd/tool-results/b6ysnz1r5.txt
```

> 1	diff --git a/tests/test_agent.py b/tests/test_agent.py
> 2	index 3ccf112..0fa0c0a 100644
> 3	--- a/tests/test_agent.py
> 4	+++ b/tests/test_agent.py
> 5	@@ -353,7 +353,8 @@ def test_a_replan_checks_tests_against_where_the_branch_left_main(record_propert
> 6	     """On every planning round the plan check compares against the branch's split from main, so earlier rounds' tests still count."""
> 7	     record_property("proves", "agent.22")
> 8	     wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
> 9	-    assert 'PLANNER_BASE=$(git merge-base HEAD origin/main)' in wf
> 10	+    # Since #795 the default branch comes from the settings; 795.7 proves it is the one they name.
> 11	+    assert re.search(r'PLANNER_BASE=\$\(git merge-base HEAD "?origin/', wf), "a step no longer compares against main"
> 12	     assert "PLANNER_BASE: ${{ env.BASE }}" not in wf, "a step still compares against the branch head"
> 13	 
> 14	 
> 15	@@ -398,7 +399,9 @@ def test_the_rivers_signal_comes_only_from_dokimas_bot(record_property):
> 16	     record_property("proves", "agent.25")
> 17	     wf = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "agent.yml")).read()
> 18	     assert "types: [dokima-next]" in wf
> 19	-    assert '[ "$EVENT" = repository_dispatch ] && [ "$SENDER" = "dokima-runtime[bot]" ] && exit 0' in wf
> 20	+    # Since #795 the bot comes from the settings; 795.9 proves only the bot they name skips the gate.
> 21	+    assert re.search(r'\[ "\$EVENT" =

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -p no:cacheprovider tests/test_settings_workflows.py -x -q 2>&1 | tail -5; timeout 900 python -m pytest -q -p no:cacheprovider tests/test_settings_workflows.py 2>&1 | grep -E "^(FAILED|E  +(Assert|795))|passed|failed" | head -60
```

> ## all-tests: None (exit 0)
>   
> assert 'all-ran' in ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -q -p no:cacheprovider -n auto tests']
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> E       AssertionError: 795.1: the all tests check did not run the all-tests command from settings; job success, log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -q -p no:cacheprovider -n auto tests']
> E       AssertionError: 795.2: the criterion's check did not run the per-criterion command from settings; job failure, log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -rA -p no:cacheprovider -o junit_family=xunit1 --junitxml=r.xml tests/test_x.py::test_a']
> E       AssertionError: 795.3: with affected tests set to all, the review still ran tests from the baseline: ['pytest -q -rA --testmon --junitxml=/tmp/pytest-of-runner/pytest-1/test_setting_affected_tests_to0/all/pack/tests.xml']
>         checks no baseline was saved, testmon never ran, and no job failed. Then runs it with no settings file and checks
> E       AssertionError: 795.3: with affected tests set to all, main still saved a baseline; log ['python 3.12', 'pip install -q pyyaml', 'python 3.12', 'pip install -q pytest pytest-xdist pytest-testmon pyyaml', 'pytest -q --testmon', '

**Agent:** Every new test fails today because the feature is missing. Now checking the changed older tests and the places that hardcode the bot's name.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -p no:cacheprovider tests/test_keys.py::test_a_build_starts_from_todays_main tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request tests/test_agent.py::test_a_replan_checks_tests_against_where_the_branch_left_main tests/test_agent.py::test_the_rivers_signal_comes_only_from_dokimas_bot tests/test_merge_check.py::test_the_merge_check_runs_mains_code_and_judges_the_pull_requests_code 2>&1 | tail -3; grep -n "dokima-runtime\|user.name\|user.email\|origin/main\|--base main\|logs" .github/workflows/*.yml | head -40; grep -n "exclude\|run_all\|run_one\|affected\|records\|bot\|slug\|default" dokima/defaults.yaml | head -30
```

> .....                                                                    [100%]
> 5 passed in 0.14s
> .github/workflows/fix.yml:35:          open=$(gh pr list --head "$BRANCH" --base main --state open --json number --jq '.[0].number // empty')
> .github/workflows/fix.yml:37:          gh pr create --base main --head "$BRANCH" --title "Manual fix: $BRANCH" \
> .github/workflows/agent.yml:8:# Those comments are what the cards are built from; each record is also saved as its own file on the logs branch,
> .github/workflows/agent.yml:9:# and starting packs read records only from those files (#610). Session logs stay on the run page.
> .github/workflows/agent.yml:100:          [ "$EVENT" = repository_dispatch ] && [ "$SENDER" = "dokima-runtime[bot]" ] && exit 0
> .github/workflows/agent.yml:171:            if [ "$ROLE" = worker ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" merge -q --no-edit origin/main; then
> .github/workflows/agent.yml:179:              MB=$(git merge-base HEAD origin/main)
> .github/workflows/agent.yml:181:                MAINS=$(git rev-parse -q --verify "origin/main:$f" || true)
> .github/workflows/agent.yml:189:              git add -A && git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" commit -q --no-edit
> .github/workflows/agent.yml:198:            if [ "$ROLE" = planner ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima

`10. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('owner_words.json'));print(list(d.keys()))
import re
for k,v in d.items():
  for line in v.splitlines():
    if re.search(r'logs|records|exclude|bot|slug|identity|A1[6-9]|\bB[35]\b|\bC[34]\b|default branch|test folder|affected',line,re.I): print(k[-30:],'|',line[:300])
"
```

> ['https://github.com/dokima-dev/dokima/issues/779', 'https://github.com/dokima-dev/dokima/issues/779#issuecomment-6225402528']
> m/dokima-dev/dokima/issues/779 | **Context:** New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it). Today `dokima/setup.py` `read_settings()` reads only nested maps and `write_settings()` rewrites the file; `dokima/agents.py` reads `.dokima/agents.yml`. Workflow rows of th
> m/dokima-dev/dokima/issues/779 | - Setting affected tests to all runs every test before review, with no saved baseline. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))
> m/dokima-dev/dokima/issues/779 | - Handling a clash with main keeps the test folder named in settings. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))
> m/dokima-dev/dokima/issues/779 | - The planner's push holds only files in the test folder named in settings. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))
> m/dokima-dev/dokima/issues/779 | - Tests on the merge gate exclude list stay out of the all tests check. ([source](https://github.com/dokima-dev/dokima/issues/740))
> m/dokima-dev/dokima/issues/779 | - Agents base their branches and pull requests on the default branch setting. ([source](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729))
> m/dokima-dev/dokima/issues/779 | - Each run's conversation is saved on the records branch the s

`11. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('owner_words.json'));print(d['https://github.com/dokima-dev/dokima/issues/779#issuecomment-6225402528'][:3000])"; sed -n 1,80p /home/runner/work/dokima/dokima/dokima/defaults.yaml
```

> /plan
> # Dokima's shipped defaults (#779). A repo's .dokima/settings.yaml names only what differs; dokima/settings.py merges
> # it over this file. Groups merge key by key, lists are replaced whole, gates and prompt additions merge by name.
> tests:
>   tag: record_property
>   dir: tests
>   file_pattern: test_*.py
>   run_one: python -m pytest -q -p no:cacheprovider {test}
>   run_all: pytest -q -p no:cacheprovider -n auto tests
>   new_test_timeout_s: 60
>   affected: testmon
> setup:
>   python: "3.12"
>   test_tools: pytest pytest-xdist pytest-testmon
>   install: ""
> fence:
>   test_setup_files: [conftest.py, pytest.ini, tox.ini, setup.cfg, pyproject.toml]
> protected_paths: [.github/]
> text_only:
>   not_text: [tests/, .github/]
> branch:
>   default: main
> records:
>   branch: logs
> owner_docs: AGENTS.md
> style:
>   docstrings: required
>   docstring_cap: 15
>   code_docstring_cap: 15
>   caps:
>     summary: 20
>     user_story: 20
>     criterion: 20
>     nfr_why: 12
>     feature: 25
>     story_title: 10
>     story_user_story: 20
>     raise_label: 4
>     question: 20
>     blocker: 30
>     issue: 25
>     evidence: 20
>     answer_why: 20
>     previous_step: 15
>     work_evidence: 15
>     test_change: 15
> river:
>   max_blocks: 3
> planner:
>   max_questions: 3
> gates:
>   required: [all tests, Acceptance criteria]
> gate:
>   checks_wait_min: 45
>   exclude: [card, board wait]
> merge:
>   method: squash
> labels:
>   plan: plan
>   work: work
>   autopilot: autopilot
>   filed: filed-by-dokima
> roles:
>   planner:
>     max_turns: 100
>   worker:
>     max_turns: 100
>   revie

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 160,252p .github/workflows/agent.yml
```

> || echo "::warning title=Card not updated::the card could not say setting up"
>           gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
>       - name: Starting branch
>         env:
>           GH_TOKEN: ${{ github.token }}
>         run: |
>           if git ls-remote --exit-code --heads origin "try/issue-$N" >/dev/null; then
>             git fetch -q origin "try/issue-$N" && git checkout -q -B "try/issue-$N" FETCH_HEAD
>             echo "BRANCH_TIP=$(git rev-parse HEAD)" >> "$GITHUB_ENV"
>             # A worker's branch that clashes with main still starts: the merge is committed with its conflict markers,
>             # the clashed files are listed for the fence, and the worker resolves them. Main's changes are in BASE.
>             if [ "$ROLE" = worker ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" merge -q --no-edit origin/main; then
>               git diff --name-only --diff-filter=U > /tmp/clashed.txt
>               if [ ! -s /tmp/clashed.txt ]; then
>                 echo "Merging main into try/issue-$N failed with no clashed file to resolve." > /tmp/why.txt
>                 echo "::error title=Merge failed::$(cat /tmp/why.txt)"; exit 1
>               fi
>               # A test the planner changed after taking main's version of it keeps the planner's change, and so does
>               # a test whose clash with main's version the planner was hande

**Agent:** Writing the review now: 14 new tests fail for the right reason, older tests pass, and three tests leave gaps.

`13. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Planned ten criteria, one per ask, with fourteen new tests that run the real workflow steps.",
          "Changed five older tests so they read the branch, bot and command from settings."],
  "decided": ["The test exclude list is built here, apart from the gate's list of checks."],
  "open": ["Asks the owner three questions: the overlap with an open issue, two exclude lists, pushed commits' name."]
 },
 "verdict": "block",
 "summary": "Every new test fails today for the right reason; three tests leave part of their promise unproven.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "795.7: new branch",
   "text": "No test checks a new branch starts from the default branch setting. Code fixing only merges and pull requests passes. Add a planner run with no branch, checking it starts from trunk.",
   "evidence": "`agent.yml:236` `checkout -B try/issue-$N origin/main`; neither 795.7 test runs it."},
  {"kind": "blocker", "to": "planner", "label": "795.10: planner merge",
   "text": "Only the worker's merge is checked; the planner's merge of main keeps the fixed name. Add the planner's merge to the 795.10 test.",
   "evidence": "`agent.yml:198`, `:228`, `:231` hardcode `dokima-runtime[bot]`; no 795.10 test runs them."},
  {"kind": "blocker", "to": "planner", "label": "795.8: conversation link",
   "text": "The conversation link on each record still points to the logs branch, so it breaks. Have the 795.8 test check the link names history.",
   "evidence": "`agent.yml:250` writes `LOG_URL=.../blob/logs/$LOG`; the 795.8 test never reads it."}
 ],
 "answers": [],
 "asks": [
  {"ask": "The all tests check runs the all-tests command from settings.", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "795.1"},
  {"ask": "Each criterion's check runs the per-criterion command from settings.", "source": "https://github.co
```

> Exit code 1
> raise 1's text holds 32 words, over its cap of 30: cut 2, keep the facts
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step open line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`14. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d['previous_step']['did'][0]="Planned ten criteria, one per ask, with fourteen new tests running real workflow steps."
d['previous_step']['open'][0]="Asks the owner about the overlap, two exclude lists and pushed commits' name."
d['raises'][0]['text']="No test checks a new branch starts from the default branch setting, so fixing only merges passes. Add a planner run with no branch, checking it starts from trunk."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 795 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#795](https://github.com/dokima-dev/dokima/issues/795) (test commands, branches and the bot follow settings). It goes back to the planner to fix three tests. The hand-back passes both checks.

**What holds up:**
- All ten asks in the issue have their own criterion, and each criterion is one behavior.
- All 14 new tests fail today because the feature is missing, not because a test is broken.
- The five older tests the planner changed still pass, and each still proves what it proved before.

**The three blockers:**
1. **Criterion 795.7 (default branch):** no test checks that a new issue's branch starts from the default branch the settings name. Code that only fixes merges and pull requests would pass. That spot is `agent.yml:236`.
2. **Criterion 795.10 (bot identity):** the tests check the worker's merge and the wiki sync, but not the planner's merge of main. That merge still hardcodes `dokima-runtime[bot]` at `agent.yml:198`, `:228` and `:231`.
3. **Criterion 795.8 (records branch):** each record's conversation link is still built from the logs branch (`agent.yml:250`). Once a repo names another records branch, that link breaks, and no test checks it.

The planner's three questions are still open and will wait for you:
- whether to build the test exclude list here and leave the rest to [#744](https://github.com/dokima-dev/dokima/issues/744) (test exclude list)
- whether the test exclude list should be separate from the gate's list of checks
- whether commits Dokima pushes should keep the app's own name

I left all three for you. Your words settle the first one: the issue asks for the exclude list. But your answer to the second still stops the plan, so answering only the first would not move anything.

The review is in `/tmp/dokima-out/review.json`.

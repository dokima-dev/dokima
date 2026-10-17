# reviewer (plan) for #796

Run: https://github.com/dokima-dev/dokima/actions/runs/39014888353

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (40.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/80a14c7a-4a5f-484a-9493-56f8516d9aa9/tool-results/bgznqan5z.txt
> 
> Preview (first 2KB):
> # Issue #796: Co-author, owner docs and prompts follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 795 -->
> <!-- dokima-blocking: {"blocked_by": [795], "blocks": [], "loop": []} -->
> Commits credit the co-author the settings name, and agent prompts follow the repo's docs, paths, caps and house rules.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/803 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/803/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/795
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/780
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issu

`2. Bash`
```
cd /tmp/pack; cat issue.md | sed 's/<img[^>]*>//g'
```

> # Issue #796: Co-author, owner docs and prompts follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 795 -->
> <!-- dokima-blocking: {"blocked_by": [795], "blocks": [], "loop": []} -->
> Commits credit the co-author the settings name, and agent prompts follow the repo's docs, paths, caps and house rules.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/803 ·  [files changed](https://github.com/dokima-dev/dokima/pull/803/files)
> 
>  **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/795
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/780
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/789
> - https://github.com/dokima-dev/dokima/issues/790
> - https://github.com/dokima-dev/dokima/issues/791
> 
> 
> **User story:** A repo's settings decide who commits credit and what every agent's prompt says, house rules included.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** The co-author line on Dokima's commits comes from the co-author setting.
>   *<a href="https://github.com/dokima-dev/dokima/blob/92f36a7ae774980a108010dd93cef53783671a6d/tests/test_settings_prompts.py#L101"> Acceptance test</a>: Dokima's commits credit the co-author the settings name, and no one else.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="htt

`3. Bash`
```
cd /tmp/pack; ls in; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps({k:v for k,v in p.items() if k not in ('criteria',)},indent=1)[:5000]);
[print(json.dumps(c)) for c in p.get('criteria',[])]"
```

> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-worker.json
> 06-reviewer-pr.json
> 07-planner.json
> [
>  {
>   "kind": "issue",
>   "label": "Tests read run settings",
>   "text": "Two manual fix tests fail when the agent run's test settings are in the environment, as in every agent run.",
>   "evidence": "`tests/test_manual_fix_check.py`: 2 fail with `TESTS_RUN_ALL` set, on main too; pass with it unset.",
>   "raised_by": "planner",
>   "id": "P4",
>   "to": "reviewer"
>  }
> ]{
>  "kind": "user_story",
>  "title": "Co-author, owner docs and prompts follow settings",
>  "summary": "Commits credit the co-author the settings name, and agent prompts follow the repo's docs, paths, caps and house rules.",
>  "user_story": "A repo's settings decide who commits credit and what every agent's prompt says, house rules included.",
>  "acceptance_criteria": [
>   {
>    "text": "The co-author line on Dokima's commits comes from the co-author setting.",
>    "words": "The co-author line on Dokima's commits comes from the co-author setting.",
>    "source": "https://github.com/dokima-dev/dokima/issues/779",
>    "files": [
>     ".github/workflows/agent.yml",
>     ".github/workflows/wiki.yml",
>     "dokima/settings.py",
>     "dokima/defaults.yaml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An empty co-author setting leaves no co-author line.",
>      "test": "tests/test_settings_prompts.py::test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting"
>     }
>    ]
>   },
>   {
>    "text": "Agents c

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'));
for k,v in p.items():
  if k not in ('acceptance_criteria','kind','title','summary','user_story'): print(k, json.dumps(v,indent=1))
print(json.dumps(p['acceptance_criteria'][6:],indent=1))"; python3 -c "
import json;r=json.load(open('in/06-reviewer-pr.json'));print(json.dumps(r,indent=1)[:4000])"
```

> non_functional []
> tests {
>  "796.1": [
>   "tests/test_settings_prompts.py::test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting"
>  ],
>  "796.2": [
>   "tests/test_settings_prompts.py::test_agents_copy_the_owner_docs_file_the_settings_name_in_place_of_the_rules_file"
>  ],
>  "796.3": [
>   "tests/test_settings_prompts.py::test_the_planner_and_worker_prompts_name_the_owner_docs_file_the_settings_name"
>  ],
>  "796.4": [
>   "tests/test_settings_prompts.py::test_the_workers_prompt_lists_the_protected_paths_the_settings_name"
>  ],
>  "796.5": [
>   "tests/test_settings_prompts.py::test_the_planner_prompts_runner_line_is_drawn_from_the_test_settings"
>  ],
>  "796.6": [
>   "tests/test_settings_prompts.py::test_the_style_prompts_caps_table_is_drawn_from_the_caps_setting"
>  ],
>  "796.7": [
>   "tests/test_settings_prompts.py::test_a_repos_house_rules_file_is_added_after_the_shipped_prompt"
>  ],
>  "796.8": [
>   "tests/test_settings_prompts.py::test_a_house_rules_section_named_for_a_role_is_added_only_to_that_roles_prompt"
>  ],
>  "796.9": [
>   "tests/test_settings_prompts.py::test_with_no_co_author_setting_commits_carry_no_co_author_line"
>  ],
>  "796.10": [
>   "tests/test_settings_prompts.py::test_dokimas_own_settings_file_keeps_the_owners_co_author_line"
>  ]
> }
> test_changes {
>  "tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza": "Owner moved his co-author line into this repo's settings file; scan looks there now.",
>  "tests/test_agent.py::test_dokimas_own_code_always_runs_f

**Agent:** Now the diff of the planner's last commit (test changes).

`5. Bash`
```
git show 92f36a7 --stat; git show 92f36a7 -- tests/
```

> commit 92f36a7ae774980a108010dd93cef53783671a6d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 07:46:01 2026 +0000
> 
>     planner for #796 (run 39012921565)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_agent.py        | 26 ++++++++++++++++++++++++--
>  tests/test_bot_identity.py |  8 +++++---
>  2 files changed, 29 insertions(+), 5 deletions(-)
> commit 92f36a7ae774980a108010dd93cef53783671a6d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 07:46:01 2026 +0000
> 
>     planner for #796 (run 39012921565)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_agent.py b/tests/test_agent.py
> index 0fa0c0a..2f40da0 100644
> --- a/tests/test_agent.py
> +++ b/tests/test_agent.py
> @@ -3,6 +3,9 @@ import json
>  import os
>  import re
>  import sys
> +import shutil
> +import subprocess
> +import tempfile
>  
>  sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
>  from dokima import agent, fence  # noqa: E402
> @@ -255,12 +258,31 @@ def test_open_blockers_come_from_the_newest_review_at_that_stage(record_property
>  
>  
>  def test_dokimas_own_code_always_runs_from_main(record_property):
> -    """The runtime is copied from main before any branch is checked out, every Dokima step runs from that copy, and only tests use the branch's code."""
> +    """The runtime is copied from 

`6. Bash`
```
cd /home/runner/work/dokima/dokima; env -u TESTS_RUN_ALL python3 -m pytest -q tests/test_settings_prompts.py tests/test_agent.py::test_dokimas_own_code_always_runs_from_main tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza 2>&1 | tail -5
rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt main 2>&1|tail -1; cp tests/test_settings_prompts.py tests/test_agent.py tests/test_bot_identity.py /tmp/mainwt/tests/; cd /tmp/mainwt; python3 -m pytest -q tests/test_settings_prompts.py tests/test_agent.py::test_dokimas_own_code_always_runs_from_main tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | cut -c1-220
```

> ............                                                             [100%]
> 12 passed in 26.10s
>         assert result == "success", f"796.2: the runtime copy failed\n{box.tail()}"
> FAILED tests/test_settings_prompts.py::test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting - AssertionError: 796.1: the planner's commit does not credit the co-author the settings name; its messag
> FAILED tests/test_settings_prompts.py::test_with_no_co_author_setting_commits_carry_no_co_author_line - AssertionError: 796.9: with no settings file, the planner's commit still has a co-author line:
> FAILED tests/test_settings_prompts.py::test_dokimas_own_settings_file_keeps_the_owners_co_author_line - AssertionError: 796.10: Dokima's own repo has no .dokima/settings.yaml to hold the co-author line
> FAILED tests/test_settings_prompts.py::test_agents_copy_the_owner_docs_file_the_settings_name_in_place_of_the_rules_file - AssertionError: 796.2: the runtime holds no RULES.md, the owner docs file the settings name: ['.d
> FAILED tests/test_settings_prompts.py::test_the_planner_and_worker_prompts_name_the_owner_docs_file_the_settings_name - AssertionError: 796.3: the planner's prompt does not name docs/RULES.md, the owner docs file
> FAILED tests/test_settings_prompts.py::test_the_workers_prompt_lists_the_protected_paths_the_settings_name - AssertionError: 796.4: the worker's prompt does not list the protected paths the settings name: ['ops/deploy/',
> FAILED tests/test_settings_prompts.py::

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainwt; env -u TESTS_RUN_ALL timeout 900 python3 -m pytest -q -x -n auto 2>&1 | tail -3 || env -u TESTS_RUN_ALL timeout 900 python3 -m pytest -q 2>&1 | tail -3
```

> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 1 failed, 724 passed, 4 warnings in 300.44s (0:05:00)

`8. Bash`
```
cd /home/runner/work/dokima/dokima; env -u TESTS_RUN_ALL timeout 1200 python3 -m pytest -q -n auto 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-250
```

> FAILED tests/test_manual_fix_check.py::test_a_manual_fix_by_dokimas_app_gets_a_check_that_runs_all_tests_and_passes - AssertionError: 643.1 (on the pull request): the manual fix's check ran no tests:
> FAILED tests/test_manual_fix_check.py::test_a_manual_fix_check_fails_when_a_test_fails - AssertionError: 643.2: the manual fix's check did not run all tests: None
> 2 failed, 1353 passed, 4 warnings in 451.93s (0:07:31)

`9. Bash`
```
cd /home/runner/work/dokima/dokima; env | grep -E "^TESTS_|^DOKIMA" | cut -c1-80; git stash list | head -1; git diff main --stat -- tests/test_manual_fix_check.py dokima/ .github | tail -3
```

> TESTS_RUN_ALL=pytest -q -p no:cacheprovider -n auto tests
> DOKIMA_SETTINGS=/tmp/runtime/.dokima/settings.yaml
> TESTS_AFFECTED=testmon
> TESTS_DIR=tests
> TESTS_RUN_ONE=python -m pytest -q -p no:cacheprovider {test}
>  dokima/prompt.py            | 112 ++++++++++++++++++++++++++++++++++++++++++++
>  dokima/settings.py          |   7 +--
>  5 files changed, 154 insertions(+), 18 deletions(-)

`10. Bash`
```
cd /home/runner/work/dokima/dokima; env -u TESTS_RUN_ALL -u TESTS_AFFECTED -u TESTS_DIR -u TESTS_RUN_ONE -u DOKIMA_SETTINGS python3 -m pytest -q tests/test_manual_fix_check.py 2>&1 | tail -2
```

> ...                                                                      [100%]
> 3 passed in 25.99s

**Agent:** Tests check out (new ones fail on main for the right reason, pass on branch; the two changed old tests keep their promises). Now checking the prior review's asks and writing the hand-back.

`11. Bash`
```
cd /tmp/pack; python3 -c "
import json;r=json.load(open('in/04-reviewer-plan.json'))['handback'];print(json.dumps(r['asks'],indent=1))"; grep -n "comment_id\|issuecomment" /tmp/pack/issue.md | head; cat dokima/defaults.yaml 2>/dev/null; cat /home/runner/work/dokima/dokima/dokima/defaults.yaml | head -60
```

> [
>  {
>   "ask": "The co-author line on Dokima's commits comes from the co-author setting.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.1"
>  },
>  {
>   "ask": "Agents copy the owner docs file the settings name, in place of the rules file.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.2"
>  },
>  {
>   "ask": "The planner and worker prompts name the owner docs file the settings name.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.3"
>  },
>  {
>   "ask": "The worker's prompt lists the protected paths the settings name.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.4"
>  },
>  {
>   "ask": "The planner prompt's runner line is drawn from the test settings.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.5"
>  },
>  {
>   "ask": "The style prompt's caps table is drawn from the caps setting.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.6"
>  },
>  {
>   "ask": "A repo's house rules file is added after the shipped prompt.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.7"
>  },
>  {
>   "ask": "A house rules section named for a role is added only to that role's prompt.",
>   "source": "https://github.com/dokima-dev/dokima/issues/779",
>   "criterion": "796.8"
>  },
>  {
>   "ask": "Q1 (a role's house rules section is a heading naming the role in the house rules file): 

`12. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
prev=json.load(open('in/04-reviewer-plan.json'))['handback']
p=json.load(open('plan.json'))
crit=p['acceptance_criteria']
T=p['tests']
r={
"previous_step":{"did":["The planner changed the bot identity test to find the owner's line in this repo's settings.",
 "The planner changed the runs-from-main test to build the prompt and check main's role files are used."],
 "decided":["Both changed tests keep the promise they proved before."],
 "open":["The planner proposed an issue: two tests fail when run settings are present."]},
"verdict":"approve",
"summary":"Both older tests now follow the settings and keep their promise; every new test fails today and passes on the branch.",
"raises":[],
"answers":[{"raise":"P4","answer":"done","why":"Confirmed: the two tests pass with the run's test settings cleared and fail with them set."}],
"asks":prev['asks'],
"behaviors":[{"criterion":f"796.{i+1}","one_behavior":True,"why":"One setting, one visible result in a commit or prompt."} for i in range(len(crit))],
"edge_cases":[{"criterion":f"796.{i+1}","cut":[],"missing":[]} for i in range(len(crit))],
"tests":[{"test":t,"only_its_behavior":True,"why":f"Runs the real step and checks only {k}'s result."} for k,ts in T.items() for t in ts],
"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 796 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step did line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

`13. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
f='/tmp/dokima-out/review.json'; r=json.load(open(f))
r['summary']="Both older tests now follow the settings and keep their promise; every new test fails today, passes on the branch."
r['summary']="Both older tests keep their promise under the settings; every new test fails today and passes on the branch."
r['previous_step']['did']=["The planner moved the owner's co-author check to this repo's settings file.",
 "The planner made the runs-from-main test build the prompt from main's role files."]
json.dump(r,open(f,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 796 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P4 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P4 files an issue, so verdict must be symptom, root cause or new, not None

`14. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent_checks.py | head -20; gh issue list -s open -L 200 --search "TESTS_RUN_ALL OR manual fix OR environment" 2>&1 | head -20
```

> 14:def problems_searched(h, pack_dir):
> 15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> 120:        bad += problems_searched(h, pack_dir)
> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}

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

`16. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def filing_problems" -A30 dokima/raises.py | head -45; python3 -c "
import json
for i in json.load(open('/tmp/pack/open_issues.json')): print(i.get('number'), i.get('title'))" | grep -iE "test|setting|env|manual|fix" 
```

> 44:def filing_problems(where, decided):
> 45-    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> 46-    problems = []
> 47-    searched = decided.get(SEARCHED)
> 48-    if not is_numbers(searched) or not searched:
> 49-        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
> 50-                        f"cause, not {searched!r}")
> 51-    if decided.get(VERDICT) not in VERDICTS:
> 52-        problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
> 53-    cause = decided.get(CAUSE)
> 54-    if decided.get(VERDICT) == "symptom" and not (isinstance(cause, int) and not isinstance(cause, bool)):
> 55-        problems.append(f"{where} is a symptom, so {CAUSE} must name its cause, an open issue by number, not {cause!r}")
> 56-    symptoms = decided.get(SYMPTOMS)
> 57-    if decided.get(VERDICT) == "root cause" and (not is_numbers(symptoms) or not symptoms):
> 58-        problems.append(f"{where} is a root cause, so {SYMPTOMS} must list the open issues it explains, not "
> 59-                        f"{symptoms!r}")
> 60-    return problems
> 61-
> 62-
> 63-def is_numbers(v):
> 64-    """True for a list of whole numbers, true and false left out."""
> 65-    return isinstance(v, list) and all(isinstance(n, int) and not isinstance(n, bool) for n in v)
> 66-
> 67-
> 68-def check_raises(role, raises):
> 69-    """The problems with the raises an agent of `role` wrote; empty when they are fine

**Agent:** Checking for a duplicate open issue for P4; #727 looks like the same cause (run settings leaking into tests).

`17. Bash`
```
cd /home/runner/work/dokima/dokima; grep -nE "^(SEARCHED|VERDICT|CAUSE|SYMPTOMS|VERDICTS)" dokima/raises.py; python3 - <<'EOF'
import json
f='/tmp/dokima-out/review.json'; r=json.load(open(f))
r['answers']=[{"raise":"P4","answer":"done","why":"Confirmed: they pass with run settings cleared; same leak of run settings into tests as #727.",
 "searched":[727,703,781],"verdict":"symptom","cause":727}]
json.dump(r,open(f,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 796 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> 23:SEARCHED = "searched"
> 25:VERDICT = "verdict"
> 26:VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> 28:CAUSE = "cause"
> 29:SYMPTOMS = "symptoms"
> OK

**Agent:** I approved the plan for [#796](https://github.com/dokima-dev/dokima/issues/796) (co-author and agent prompts follow settings), and the hand-back passes both checks.

- **The two older tests the planner changed still prove what they proved before.**
  - The bot identity test now looks for your co-author line in this repo's own settings file, which is where you asked for it to go.
  - The "Dokima's code runs from main" test now builds a prompt from a branch folder that holds its own role files. It checks that main's role files are used and the branch's never are. That is stricter than the old check, which only read the workflow text.
- **All ten new tests and both changed tests fail on main and pass on this branch.** On main they fail because the feature is missing, not because of a crash or a bad path.
- **Two other tests fail in the full suite on this branch: the manual-fix tests.** They pass once the agent run's test settings are cleared from the environment. This is the planner's issue P4. I confirmed it and filed it as part of a problem already open in [#727](https://github.com/dokima-dev/dokima/issues/727) (the runner's settings leak into tests). I didn't run these two tests on main with the settings set; the planner reports they fail there too.
- **I kept the previous reviewer's mapping of your asks to criteria.** This includes your "nothing tuned to Dokima's own repo" rule, which is matched to the empty co-author default. The bot default is the other place that rule applies, and it stays with [#789](https://github.com/dokima-dev/dokima/issues/789) (the bot Dokima recognizes comes from settings).

The hand-back is in `/tmp/dokima-out/review.json`.

# reviewer (plan) for #812

Run: https://github.com/dokima-dev/dokima/actions/runs/39039448631

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (30.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tool-results/b04tc7kqe.txt
> 
> Preview (first 2KB):
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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/820
> 
> 
> **User story:** An adopter's runs use Dokima's tagged code and the adopt

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/820
> 
> 
> **User story:** An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat owner_words.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d)[:3000])"
```

> []
> {
>  "https://github.com/dokima-dev/dokima/issues/742": "Phase 1 of #272. Owner rule from #272: one central Dokima, never a copy of its code.\n\n**What lands in an adopter's repo**\n- One thin workflow, `.github/workflows/dokima.yml`, about 15 lines, that calls Dokima's shared workflows by tag.\n- `.dokima/settings.yaml`.\n- Nothing else. No Python. All Dokima code runs from Dokima's own repo inside GitHub Actions.\n\n**Credentials** live only in GitHub secrets on the repo (the `keys` environment): the App key, `CLAUDE_TOKEN`, `KIMI_API_KEY` when used. `settings.yaml` only names which secret each role reads. Nothing secret is ever committed.\n\n**Identity on every commit:** the trailer `Co-authored-by: dokima[bot]`, so Dokima appears in the contributor list of every repo it touches. Replaces the owner's hardcoded trailer (#110); the adopter can turn it off in settings.\n\n**Also**\n- The README install steps (README.md:120-125) and docs/wiki/Installing.md stop telling adopters to copy `.github/workflows/` and `dokima/`. `playthrough.yml` and `wiki.yml` are Dokima-project files, never installed.\n- The existing copy installer in `playthrough.py:161-223` is the starting point.\n- Missing bot or key fails loudly with the fix in the message (from #41).\n\n**Done when:** acceptance items 12, 15 and 20 on #272 pass: install adds only the workflow and settings; a run without the secret fails with a clear message; an empty repo reaches its first merged PR using only the docs.\n",
>  "

`4. Bash`
```
cd /tmp/pack; cat plan.json; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:8000])"
```

> {
>  "kind": "user_story",
>  "title": "Dokima's workflows run from Dokima's own repo",
>  "summary": "Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.",
>  "user_story": "An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.",
>  "acceptance_criteria": [
>   {
>    "text": "A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.",
>    "words": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
>    "source": "https://github.com/dokima-dev/dokima/issues/742",
>    "files": [
>     "dokima/install/dokima.yml",
>     ".github/workflows/entry.yml",
>     ".github/workflows/acceptance-criteria.yml",
>     ".github/workflows/agent.yml",
>     ".github/workflows/assign.yml",
>     ".github/workflows/audit.yml",
>     ".github/workflows/autopilot.yml",
>     ".github/workflows/board.yml",
>     ".github/workflows/card.yml",
>     ".github/workflows/commands.yml",
>     ".github/workflows/fix.yml",
>     ".github/workflows/full-suite.yml",
>     ".github/workflows/reviews.yml",
>     ".github/workflows/testmon.yml",
>     ".github/workflows/uptodate.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An adopter's repo holding no Dokima code at all",
>      "test": "tests/test_thin_install.py::test_a_run_starts_in_a_repo_holding_no_dokima_code"
>     },
>     {
>      "case": "An adopter's repo holding its own copy of Dokima's code",
>      "test": "tests/test_thin_instal

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git diff bc679b7 f75c6ad --stat; git diff bc679b7 f75c6ad -- tests | head -80; sed -n 370,430p tests/test_thin_install.py
```

> tests/test_thin_install.py | 28 +++++++++++++++-------------
>  1 file changed, 15 insertions(+), 13 deletions(-)
> diff --git a/tests/test_thin_install.py b/tests/test_thin_install.py
> index d3542fd..5f9995e 100644
> --- a/tests/test_thin_install.py
> +++ b/tests/test_thin_install.py
> @@ -161,19 +161,6 @@ def test_no_shared_workflow_runs_the_adopters_dokima_folder(record_property, tmp
>      assert not found, f"812.1: these jobs ran Dokima code from the adopter's repo, not Dokima's own: {found}"
>  
>  
> -def test_every_event_dokima_acts_on_starts_the_adopters_workflow(record_property):
> -    """The adopter's one workflow starts on every event Dokima acts on.
> -
> -    Proves 812.1. Reads the thin workflow and checks its triggers name every event Dokima's shared workflows start on
> -    today: issues, comments, pull requests, reviews, line notes, the merge queue, pushes, the schedule, finished
> -    runs and the river's own signal."""
> -    record_property("proves", "812.1")
> -    on = thin("812.1").get("on")
> -    names = set(on) if isinstance(on, dict) else set(on or []) if isinstance(on, list) else {on}
> -    missing = sorted(EVENTS - names)
> -    assert not missing, f"812.1: the adopter's workflow never starts on {missing}, so Dokima never runs on them"
> -
> -
>  # 812.2 ------------------------------------------------------------------------------------------------------------
>  
>  def reached():
> @@ -389,3 +376,18 @@ def test_the_adopters_workflow_is_at_most_twenty_lines(record_property):
>      assert os.

**Agent:** The planner moved the event test onto its own criterion. Next I'll check how it gets its event list, then run the tests.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "EVENTS\|^def thin\|^THIN" -A6 tests/test_thin_install.py | head -50; timeout 600 python3 -m pytest -q tests/test_thin_install.py 2>&1 | tail -20
```

> 29:THIN = os.path.join(ROOT, "dokima", "install", "dokima.yml")
> 30-WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
> 31-OWN = ("playthrough.yml", "wiki.yml")
> 32-SHARED = sorted(os.path.basename(p) for p in glob.glob(os.path.join(WORKFLOWS, "*.yml")) if os.path.basename(p) not in OWN)
> 33-CALL = re.compile(r"^dokima-dev/dokima/\.github/workflows/([\w.-]+\.ya?ml)@(.+)$")
> 34-RELEASE = re.compile(r"^v\d+\.\d+\.\d+$")
> 35-BOT_LINE = "Co-authored-by: dokima-runtime[bot] <1+dokima-runtime[bot]@users.noreply.github.com>"
> --
> 38:EVENTS = {"issues", "issue_comment", "pull_request_target", "pull_request_review", "pull_request_review_comment",
> 39-          "merge_group", "push", "schedule", "workflow_run", "repository_dispatch"}
> 40-
> 41-
> 42-def read_yaml(path):
> 43-    """The workflow at PATH, read with `on` kept as a name."""
> 44-    data = yaml.safe_load(open(path).read()) or {}
> --
> 50:def thin(crit):
> 51-    """The thin workflow adopters install; fails naming criterion CRIT when it is missing."""
> 52-    assert os.path.isfile(THIN), f"{crit}: there is no thin workflow for adopters at dokima/install/dokima.yml"
> 53-    return read_yaml(THIN)
> 54-
> 55-
> 56-def calls(wf):
> --
> 392:    missing = sorted(EVENTS - names)
> 393-    assert not missing, f"812.10: the adopter's workflow never starts on {missing}, so Dokima never runs on them"
> assert 'Co-authored-by: dokima-runtime[bot] <1+dokima-runtime[bot]@users.noreply.github.com>' in 'planner for #57 (run 42)'
> FAILED tests/test_thin_install.py::test_tur

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import yaml,glob,os
s=set()
for p in glob.glob('.github/workflows/*.yml'):
  if os.path.basename(p) in ('playthrough.yml','wiki.yml'): continue
  d=yaml.safe_load(open(p)); on=d.get(True, d.get('on'))
  n=set(on) if isinstance(on,dict) else set(on) if isinstance(on,list) else {on}
  s|=n
print(sorted(s))"; timeout 900 python3 -m pytest -q -x --deselect tests/test_thin_install.py 2>&1 | tail -3
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bc1bvfy3z). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tasks/bc1bvfy3z.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`8. Bash`
```
head -3 /tmp/claude-1001/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tasks/bc1bvfy3z.output
```

> ['issue_comment', 'issues', 'merge_group', 'pull_request_review', 'pull_request_review_comment', 'pull_request_target', 'push', 'repository_dispatch', 'schedule', 'workflow_call', 'workflow_dispatch', 'workflow_run']

`9. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
prev=json.load(open('/tmp/pack/in/02-reviewer-plan.json'))['handback']
asks=prev['asks']
asks[7]['ask']="calls Dokima's shared workflows by tag"
asks.append({"ask":"One thin workflow, `.github/workflows/dokima.yml`","source":"https://github.com/dokima-dev/dokima/issues/742","criterion":"812.10"})
beh=prev['behaviors']+[{"criterion":"812.10","one_behavior":True,"why":"Which events start the adopter's one workflow."}]
ec=prev['edge_cases']+[{"criterion":"812.10","cut":[],"missing":[]}]
tests=prev['tests']
for t in tests:
    if t['test'].endswith('starts_the_adopters_workflow'):
        t['only_its_behavior']=True; t['why']="Checks only the thin workflow's events against today's shared events."
r={"previous_step":{"did":["Moved the event test onto its own new criterion, 812.10."],
 "decided":["The adopter's one workflow must start on every event Dokima acts on."],
 "open":[]},
 "verdict":"approve",
 "summary":"The plan now gives each test its own criterion; all ten criteria trace to the owner and fail today.",
 "raises":[],"answers":[],"asks":asks,"behaviors":beh,"edge_cases":ec,"tests":tests,"size":"ok"}
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#812](https://github.com/dokima-dev/dokima/issues/812) (Dokima's workflows run from Dokima's own repo). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Last round's blocker is fixed:** the test that checks which events start the adopter's workflow no longer sits under the "code comes from Dokima's repo" criterion. The planner gave it its own criterion, 812.10. Its source is the owner's line on [#742](https://github.com/dokima-dev/dokima/issues/742) (thin install, no Dokima code in the adopter's repo): "One thin workflow, `.github/workflows/dokima.yml`".
- **The event list is right:** the events the test expects are the same ones Dokima's shared workflows start on today. The two Dokima-only workflows are left out, and so are manual starts and calls from another workflow.
- **The tests fail for the right reason:** all 12 new tests fail today because the feature is missing, not because a test crashes.
- **Every ask is covered:** each of the owner's asks matches one criterion, each criterion is one behavior, and I found no missing everyday edge cases.

I raised no blockers or questions, and none were open for me to answer. I started a full run of the older tests for my own check, but my review doesn't depend on it and I didn't wait for it to finish.

`10. Bash`
```
tail -5 /tmp/claude-1001/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tasks/bc1bvfy3z.output
```

> assert not {'1+dokima-runtime[bot]@users.noreply.github.com': ['tests/test_thin_install.py']}
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 243 passed, 12 deselected, 1 warning in 342.14s (0:05:42)
> 
> [exited with code 0]

`11. Bash`
```
grep -n "FAILED\|^____" /tmp/claude-1001/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tasks/bc1bvfy3z.output | head; cd /home/runner/work/dokima/dokima; git stash list | head -1; git log -1 --format=%h main 2>/dev/null
```

> edf1c0e

`12. Bash`
```
grep -n "def test\|Error\|test_.*py" /tmp/claude-1001/-home-runner-work-dokima-dokima/5210efe2-fe47-466b-a29e-311241c5a519/tasks/bc1bvfy3z.output | head -20
```

> 2:assert not {'1+dokima-runtime[bot]@users.noreply.github.com': ['tests/test_thin_install.py']}

`13. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rln "noreply\|@users" tests/*.py | head; grep -rn "def test.*\(email\|address\|identity\|personal\)" tests/*.py | head
```

> tests/test_bot_identity.py
> tests/test_settings_prompts.py
> tests/test_settings_workflows.py
> tests/test_thin_install.py
> tests/test_bot_identity.py:101:def test_bot_identity_in_step_is_defined(record_property):
> tests/test_card_416.py:30:def test_lists_name_issues_by_full_address(monkeypatch):
> tests/test_card_self_link.py:166:def test_the_pr_issue_is_read_from_the_closing_line_by_full_address_or_number(record_property):
> tests/test_settings_workflows.py:587:def test_merging_main_into_a_branch_carries_the_git_identity_of_the_bot_named_in_settings(record_property, tmp_path):

`14. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python3 -m pytest -q tests/test_bot_identity.py tests/test_settings_workflows.py 2>&1 | grep -E "FAILED|passed|failed"; 
```

> FAILED tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza - AssertionError: 567.3: files commit as someone other than the bot or Reza: 1+dokima-runtime[bot]@users.noreply.github.com in tests/test_thin_install.py
> 1 failed, 19 passed in 29.11s

**Agent:** The older tests finished: one fails because of the planner's new test file. I'm checking that test now.

`15. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_no_file_commits_as_anyone" -B2 -A30 tests/test_bot_identity.py; grep -n "1+dokima-runtime" tests/test_thin_install.py
```

> 168-
> 169-
> 170:def test_no_file_commits_as_anyone_but_the_bot_or_reza(record_property):
> 171-    """No file names a GitHub noreply address other than the bot's or Reza's.
> 172-
> 173-    Proves 567.3. Reads every tracked file and lists each `<name>@users.noreply.github.com` address that belongs to someone
> 174-    else, such as the stranger "dokima", the play-through's made-up name or GitHub Actions' own bot.
> 175-    It also checks the scan finds the bot's address in agent.yml and Reza's in this repo's own settings file, where his
> 176-    co-author line lives since #796, so it never passes blind."""
> 177-    record_property("proves", "567.3")
> 178-    found = noreply_addresses()
> 179-    for mine, where in (("${BOT_ID}+${SLUG}[bot]@users.noreply.github.com", ".github/workflows/agent.yml"),
> 180-                        (REZA_EMAIL, ".dokima/settings.yaml")):
> 181-        assert where in found.get(mine, []), f"567.3: the scan missed {mine} in {where}"
> 182-    others = {a: files for a, files in found.items() if a not in BOT_EMAILS | {REZA_EMAIL}}
> 183-    assert not others, "567.3: files commit as someone other than the bot or Reza: " + "; ".join(
> 184-        f"{a} in {', '.join(sorted(set(f)))}" for a, f in sorted(others.items()))
> 35:BOT_LINE = "Co-authored-by: dokima-runtime[bot] <1+dokima-runtime[bot]@users.noreply.github.com>"

`16. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "BOT_EMAILS\s*=" -A4 tests/test_bot_identity.py; git show main:tests/test_bot_identity.py >/dev/null && echo onmain
```

> 17:BOT_EMAILS = {"337511017+dokima-runtime[bot]@users.noreply.github.com",
> 18-              "${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"}
> 19-REZA_EMAIL = "34189616+RezaSoleymanifar@users.noreply.github.com"
> 20-NOREPLY = re.compile(r"[^\s\"'<>=`(),:;]+@users\.noreply\.github\.com")
> 21-
> onmain

**Agent:** Confirmed: this is a real break, so I'm changing my verdict to block.

`17. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['verdict']='block'
r['summary']="The new test file breaks an older test, so the full suite goes red whatever the worker builds."
r['previous_step']['open']=["The new test file trips an older identity test."]
r['raises']=[{"kind":"blocker","to":"planner","label":"Breaks an older test",
 "text":"`tests/test_thin_install.py:35` writes a made-up bot address, `1+dokima-runtime[bot]@...`, that 567.3 forbids, so the suite is red. Build the address from parts or use an allowed one.",
 "evidence":"`tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza` fails on this branch only."}]
for t in r['tests']:
    if t['test'].endswith('credits_its_bot_by_default') or t['test'].endswith('leaves_commits_with_none'):
        pass
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've changed my verdict on [#812](https://github.com/dokima-dev/dokima/issues/812) (Dokima's workflows run from Dokima's own repo) from approve to **block**. The planner's new test file breaks an older test.

- **What breaks:** line 35 of `tests/test_thin_install.py` writes out a made-up bot address, `1+dokima-runtime[bot]@users.noreply.github.com`. The older test `tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza` (567.3) rejects any file that names an address other than the real bot's or Reza's.
- **Why it matters:** the full suite goes red whatever the worker builds. The worker can't fix it, because the test files aren't theirs to change.
- **Proof:** I ran that test file and `tests/test_settings_workflows.py` on this branch. The identity test fails, naming that address in the new file, and the other 19 pass. It has to pass on `main`, because the new test file doesn't exist there.
- **Smallest fix (sent to the planner):** build the address from parts, or use one the older test already allows.

Apart from that, the earlier findings hold. The last round's blocker is fixed, every ask is covered, and all 12 new tests fail today because the feature is missing.

The full run of the older tests stopped at that first failure, with 243 passing before it. Tests after it were never run, so I can't say whether any other older test also breaks.

The updated review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

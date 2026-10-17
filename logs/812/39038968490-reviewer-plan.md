# reviewer (plan) for #812

Run: https://github.com/dokima-dev/dokima/actions/runs/39038968490

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json; ls in
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
> 
> 
> **User story:** An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/do

`2. Bash`
```
cd /tmp/pack; cat owner_words.json | head -100; python3 -c "import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:6000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/742": "Phase 1 of #272. Owner rule from #272: one central Dokima, never a copy of its code.\n\n**What lands in an adopter's repo**\n- One thin workflow, `.github/workflows/dokima.yml`, about 15 lines, that calls Dokima's shared workflows by tag.\n- `.dokima/settings.yaml`.\n- Nothing else. No Python. All Dokima code runs from Dokima's own repo inside GitHub Actions.\n\n**Credentials** live only in GitHub secrets on the repo (the `keys` environment): the App key, `CLAUDE_TOKEN`, `KIMI_API_KEY` when used. `settings.yaml` only names which secret each role reads. Nothing secret is ever committed.\n\n**Identity on every commit:** the trailer `Co-authored-by: dokima[bot]`, so Dokima appears in the contributor list of every repo it touches. Replaces the owner's hardcoded trailer (#110); the adopter can turn it off in settings.\n\n**Also**\n- The README install steps (README.md:120-125) and docs/wiki/Installing.md stop telling adopters to copy `.github/workflows/` and `dokima/`. `playthrough.yml` and `wiki.yml` are Dokima-project files, never installed.\n- The existing copy installer in `playthrough.py:161-223` is the starting point.\n- Missing bot or key fails loudly with the fix in the message (from #41).\n\n**Done when:** acceptance items 12, 15 and 20 on #272 pass: install adds only the workflow and settings; a run without the secret fails with a clear message; an empty repo reaches its first merged PR using only the docs.\n",
>  "htt

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -30; cat tests/test_thin_install.py
```

> commit bc679b7bd8af6fb06851c290c39f65cbbf6e8254
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 14:00:51 2026 +0000
> 
>     planner for #812 (run 39037113293)
> 
>  tests/test_settings_prompts.py |  21 +--
>  tests/test_start.py            |  27 +++
>  tests/test_thin_install.py     | 391 +++++++++++++++++++++++++++++++++++++++++
>  3 files changed, 429 insertions(+), 10 deletions(-)
> """Tests for #812: Dokima's workflows run from Dokima's own repo, called by one short workflow.
> 
> An adopter's repo holds one thin workflow that calls Dokima's shared workflows at a release tag; every run takes
> Dokima's code from Dokima's own repo, its keys from the repo's `keys` environment, and fails saying how to fix a
> missing bot or model key. Dokima's commits credit Dokima's bot unless the settings turn that off.
> 
> The thin workflow adopters install is `dokima/install/dokima.yml`; the shared workflows are this repo's
> `.github/workflows/`, less the two that are Dokima's own (`playthrough.yml`, `wiki.yml`).
> 
> Most tests run real workflow steps through tests/test_settings_workflows.py's Box: a temp repo standing in for the
> adopter's, a fake GitHub and a fake Claude Code. A step checking out dokima-dev/dokima gets this checkout's Dokima
> code (tests/test_start.py's dokima_checkout). To prove the adopter's own code never runs, the adopter's repo holds a
> `dokima/` folder whose every module only writes a mark file. Nothing leaves the machine.
> """
> import glob
> i

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_settings_prompts.py tests/test_start.py; timeout 900 python3 -m pytest -q tests/test_thin_install.py -x -q 2>&1 | tail -5; timeout 900 python3 -m pytest -q tests/test_thin_install.py 2>&1 | grep -E "^(FAILED|ERROR|E   .*812)|passed|failed" | head -40
```

> commit bc679b7bd8af6fb06851c290c39f65cbbf6e8254
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 14:00:51 2026 +0000
> 
>     planner for #812 (run 39037113293)
> 
> diff --git a/tests/test_settings_prompts.py b/tests/test_settings_prompts.py
> index 67f2af2..697f0b5 100644
> --- a/tests/test_settings_prompts.py
> +++ b/tests/test_settings_prompts.py
> @@ -123,21 +123,22 @@ def test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting(
>  # 796.9 ------------------------------------------------------------------------------------------------------------
>  
>  def test_with_no_co_author_setting_commits_carry_no_co_author_line(record_property, tmp_path):
> -    """A repo that names no co-author gets commits that credit no one.
> +    """A repo that names no co-author never gets commits crediting Dokima's owner.
>  
> -    Proves 796.9. Dokima's shipped defaults reach every repo, so they credit no one. Runs agent.yml's planner push
> -    and wiki.yml's sync in a repo with no settings file, and checks neither pushed commit has a co-author line. Then
> -    a settings file that names other settings but no co-author: the planner's commit still has none."""
> +    Proves 796.9. Dokima's shipped defaults reach every repo, so they never carry the owner's own line (#812 makes
> +    Dokima's bot the shipped default instead). Runs agent.yml's planner push and wiki.yml's sync in a repo with no
> +    settings file, and checks neither pushed commit credi

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def \(stand_in\|app_step\|through\|step_named\|steps_of\)" tests/test_settings_workflows.py; grep -n "name: \(Push the planner's tests\|The agent (Claude Code)\|Starting branch\|The worker\)" .github/workflows/agent.yml; grep -ln "git commit\|git merge\|git push" .github/workflows/*.yml; for f in .github/workflows/*.yml; do python3 -c "
import yaml,sys;d=yaml.safe_load(open('$f'));on=d.get(True) or d.get('on');print('$f',list(on) if isinstance(on,dict) else on)"; done
```

> 176:def stand_ins(steps):
> 195:def steps_of(file, job):
> 201:def step_named(steps, start):
> 208:def through(steps, start):
> 213:def app_step(steps):
> 218:def stand_in(name, script):
> 186:      - name: Starting branch
> 380:      - name: The agent (Claude Code)
> 459:      - name: Push the planner's tests or the worker's code to try/issue-N
> .github/workflows/agent.yml
> .github/workflows/wiki.yml
> .github/workflows/acceptance-criteria.yml ['pull_request_target', 'merge_group']
> .github/workflows/agent.yml ['repository_dispatch', 'workflow_call', 'workflow_dispatch']
> .github/workflows/assign.yml ['issues']
> .github/workflows/audit.yml ['schedule', 'workflow_dispatch']
> .github/workflows/autopilot.yml ['issues']
> .github/workflows/board.yml ['issues', 'schedule', 'issue_comment', 'pull_request_target', 'workflow_run']
> .github/workflows/card.yml ['workflow_run', 'issues', 'issue_comment', 'pull_request_target', 'schedule']
> .github/workflows/commands.yml ['issue_comment', 'pull_request_review']
> .github/workflows/fix.yml ['workflow_dispatch']
> .github/workflows/full-suite.yml ['pull_request_target', 'push', 'merge_group']
> .github/workflows/playthrough.yml ['workflow_dispatch']
> .github/workflows/reviews.yml ['pull_request_review', 'pull_request_review_comment']
> .github/workflows/testmon.yml ['push']
> .github/workflows/uptodate.yml ['push']
> .github/workflows/wiki.yml ['push', 'workflow_dispatch']

**Agent:** Checked the new tests: all 12 fail today for the right reason. Now running the older tests the plan touched.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1200 python3 -m pytest -q -x tests/test_start.py tests/test_settings_prompts.py tests/test_settings_workflows.py 2>&1 | tail -3; git stash -q 2>/dev/null; git checkout -q HEAD~1 -- tests/test_start.py && timeout 600 python3 -m pytest -q tests/test_settings_prompts.py -k 796_9 -k no_co_author 2>&1 | tail -2; git checkout -q HEAD -- tests/test_start.py; git status --short
```

> ..............................                                           [100%]
> 30 passed in 88.00s (0:01:28)
> .                                                                        [100%]
> 1 passed, 9 deselected in 5.90s

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned nine criteria for running Dokima from its own repo, each with a failing test.",
          "Changed an older test so the bot line can be the default, never the owner's line."],
  "decided": ["The adopter's workflow lives in Dokima as an install file, under 20 lines."],
  "open": ["Check names in adopters' repos may not match, raised as its own issue."]},
 "verdict": "block",
 "summary": "One test for 812.1 proves a different promise, that the adopter's workflow starts on every event.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Test off its criterion",
   "text": "`test_every_event_dokima_acts_on_starts_the_adopters_workflow` proves the one workflow starts on every event, not where code comes from (812.1). Give it its own criterion from the owner's 'One thin workflow', or drop it.",
   "evidence": "`tests/test_thin_install.py:164` reads only the thin workflow's `on:`; criterion 812.1 says nothing about events."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "Agreed: a real problem outside this issue, worth its own issue."}
 ],
 "asks": [
  {"ask": "All Dokima code runs from Dokima's own repo inside GitHub Actions.", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "812.1"},
  {"ask": "live only in GitHub secrets on the repo (the `keys` environment)", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "812.2"},
  {"ask": "`settings.yaml` only names which secret each role reads.", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "812.3"},
  {"ask": "Missing bot or key fails loudly with the fix in the message", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "812.4"},
  {"ask": "Missing bot or key fails loudly with the fix in the message", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "812.5"},
  {"ask": "U
```

> Exit code 1
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
sed -i 's/Changed an older test so the bot line can be the default, never the owner'"'"'s line./Changed an older test so the bot line is the default, never the owner'"'"'s./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`9. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/Changed an older test so the bot line can be the default, never the owner'"'"'s line./Changed an older test so the bot line is the default, never the owner'"'"'s./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

`10. Bash`
```
cd /tmp/pack; python3 -c "import json;d=json.load(open('open_issues.json'));print(type(d), len(d)); [print(i.get('number'), i.get('title')) for i in (d if isinstance(d,list) else d.get('issues',[]))]" | grep -iE "check|required|gate|name|adopt|thin|^<|^[0-9]+ " | head -60
```

> <class 'list'> 190
> 819 Code checks the reviewer's required boxes
> 818 The reviewer's prompt spells out its duties and boxes
> 817 Generic shipped prompts and the planner's questions
> 816 An empty repo reaches its first merge from the docs
> 815 Wiki install page uses the thin workflow
> 814 README install steps use the thin workflow
> 813 Installing adds only the workflow and settings
> 812 Dokima's workflows run from Dokima's own repo
> 811 The autopilot workflow still triggers on the fixed label name, so a renamed label never starts it.
> 807 Two manual fix tests fail on main: the step runs `python -m pytest`, bypassing the test's fake `pytest`.
> 800 Any-size input: break documents into features, stories and criteria, with caps the planner knows
> 799 Leaner tests: study, fix brittle tests, one shared test surface, then reviewer rules for test quality
> 791 No shipped default value is left in Dokima's code
> 790 Word caps come from settings
> 789 The bot Dokima recognizes comes from settings
> 788 An agent's turn limit comes from settings
> 786 Updating pull requests waits on the named all tests check
> 785 The card follows the check names and icon source
> 783 Owner docs, run records and limits come from settings
> 782 The fence follows the test and protected path settings
> 780 Dokima's own repo moves its values into its settings file
> 775 The roles allow a manual criterion, but the planner's check refuses any criterion without a test.
> 771 The card shows a skipped check as failed, so a draft's unrun acceptanc

`11. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['answers'][0].update({"searched":[786,785,744],"verdict":"new","why":"Agreed: new. Open issues on check names never cover the prefix a called workflow adds."})
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`12. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['answers'][0].update({"searched":[786,785,744],"verdict":"new","why":"Agreed: new. Open issues on check names never cover the prefix a called workflow adds."})
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I blocked the plan for [#812](https://github.com/dokima-dev/dokima/issues/812) (running Dokima from its own repo). One of its tests proves something its criterion doesn't promise. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**The blocker (sent to the planner):**
- The test `test_every_event_dokima_acts_on_starts_the_adopters_workflow` is listed as proof for 812.1, "all Dokima code comes from Dokima's own repo."
- It actually checks something else: that the adopter's one workflow starts on every event Dokima acts on.
- The fix is small. Either give it a criterion of its own, based on the owner's "One thin workflow" in [#742](https://github.com/dokima-dev/dokima/issues/742) (thin install), or drop it.

**Everything else holds up:**
- Each of the nine criteria covers exactly one behavior.
- Every ask in #742 and its answers comment that this story carries maps to a criterion. None is missing.
- All 12 new tests fail today for the right reason: the feature isn't built yet, not a crash or a bad path.
- The planner changed two older tests:
  - The co-author test now checks that commits never credit the owner. The owner asked for that: the bot's line is the default, and their own line is never shipped as a default.
  - The test machine gained a stand-in for checking out Dokima's repo.
  - The older tests in those files still pass: 30 passed.

**The planner's raise P1:** I agreed it should be filed as a new issue. In an adopter's repo, GitHub renames the required checks, so the names Dokima waits on won't match. Neither of the closest open issues, [#786](https://github.com/dokima-dev/dokima/issues/786) (updates wait on the "all tests" check) and [#785](https://github.com/dokima-dev/dokima/issues/785) (card follows check names), covers this.

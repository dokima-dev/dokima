# reviewer (plan) for #741

Run: https://github.com/dokima-dev/dokima/actions/runs/39037173766

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (33.7KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/304c4599-294f-4200-8429-05a2853bbd56/tool-results/bhwjtgq2o.txt
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
> # Issue #741: Generic role prompts with repo-appended house rules
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 781, 784, 787, 793, 796 -->
> <!-- dokima-blocking: {"blocked_by": [779, 781, 784, 787], "blocks": [746], "loop": []} -->
> The shipped role prompts drop Dokima's own examples, share one raising text, and spell out planner questions and reviewer duties.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234435336) with `/plan`, `/work` or `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/784
> - https://github.com/dokima-dev/dokima/issues/787
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #741: Generic role prompts with repo-appended house rules
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 781, 784, 787, 793, 796 -->
> <!-- dokima-blocking: {"blocked_by": [779, 781, 784, 787], "blocks": [746], "loop": []} -->
> The shipped role prompts drop Dokima's own examples, share one raising text, and spell out planner questions and reviewer duties.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234435336) with `/plan`, `/work` or `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/784
> - https://github.com/dokima-dev/dokima/issues/787
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; cat owner_words.json | head -50; cat parent.json | head -30
```

> []
> {
>  "kind": "feature",
>  "title": "Shipped prompts fit any repo, with clear reviewer duties",
>  "summary": "The shipped role prompts drop Dokima's own examples, share one raising text, and spell out planner questions and reviewer duties.",
>  "feature": "Prompts fit any repo. Stories: (1) generic prompts and planner questions. (2) reviewer duties and boxes, after 1. (3) code checks the boxes, after 2.",
>  "stories": [
>   {
>    "title": "Generic shipped prompts and the planner's questions",
>    "user_story": "Any repo's agents get prompts with neutral examples, its own numbers, and clear rules for asking the owner.",
>    "context": "Already on main (#796, #803): the caps table, runner line, owner docs name and protected paths are drawn from settings by the prompt builder, and house rules are added after each role's prompt. Still open: the role files name Dokima files in their examples (planner lines 99 to 170, the raising block in all three roles), the raising block is copied three times, and the planner's 'more than 3 questions' and the 'three blocks in a row' lines are written in, while settings hold planner.max_questions and river.max_blocks. Code's own limits move to settings in #783. The two grade prompts are left out of scope. The owner's answer of 2026-10-17: the rewrite sizes are an estimate, not a requirement, so no size check; the two grade prompts staying as they are is a scope note, not a requirement. House rules per role shipped in #796; their criterion is proved by the 

`4. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['01-planner.json','02-reviewer-plan.json','03-planner.json']:
    d=json.load(open(f)); print(f, list(d.keys()))
"; python3 -c "
import json;d=json.load(open('02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:9000])"
```

> 01-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 02-reviewer-plan.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 03-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39036631238",
>  "commit_before": "edf1c0e0800fbd616670940fb81b53445a839682",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 153022,
>   "turns": 12,
>   "cost_usd": 0.7074474000000001,
>   "tokens_in": 545923,
>   "tokens_out": 11960
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/741/39036631238-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39036631238",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner proposes three stories: generic prompts, reviewer duties, code checking the boxes."
>    ],
>    "decided": [
>     "House rules per role count as already done, so no criterion carries them.",
>     "The boxes apply at both review stages."
>    ],
>    "open": [
>     "Three questions for the owner: rewrite size, house rules already done, which review stage."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Blocked: house rules from the owner's done line have no criterion, and two criteria bundle two behaviors.",
>   "rais

`5. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('02-reviewer-plan.json'));h=d['handback'];print(json.dumps({k:h[k] for k in ['edge_cases','tests','size']},indent=1)); print(json.dumps(d['check'],indent=1)[:2000])
d=json.load(open('03-planner.json'));print(json.dumps(d['check'],indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; git log --oneline -3; git status; ls tests | grep -E "review_box|role_prompt|settings_prompt"
```

> {
>  "edge_cases": [
>   {
>    "criterion": "S1.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.4",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.5",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.6",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.7",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S1.8",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.2",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.4",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S2.5",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.1",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.2",
>    "cut": [],
>    "missing": [
>     "An entry with a wrong value, such as an added kind other than creep or needed."
>    ]
>   },
>   {
>    "criterion": "S3.3",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.4",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.5",
>    "cut": [],
>    "missing": []
>   },
>   {
>    "criterion": "S3.6",
>    "cut": [],
>    "missing": []
>   }
>  ],
>  "tests": [],
>  "size": "S1.7 and S2.2 each bundle two behaviors."
> }
> {
>  "passed": true,
>  "problems": []
> }
> {
>  "passed": true,
>  "problems": []
> }
> edf1c0e Autopilot merges by the

**Agent:** I'm reviewing the planner's revised split plan for #741. Next I'll confirm the house-rules tests it cites exist and pass.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_\|796\.[78]" tests/test_settings_prompts.py | head -40; pytest -q tests/test_settings_prompts.py 2>&1 | tail -3
```

> 42:    box.commit(f"try/issue-{N}", {"tests/test_x.py": 'def test_a():\n    """A."""\n', **(branch_files or {})},
> 73:    write = sw.stand_in("The planner", "mkdir -p tests\nprintf 'def test_n():\\n    assert 0\\n' > tests/test_new.py\n")
> 101:def test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting(record_property, tmp_path):
> 125:def test_with_no_co_author_setting_commits_carry_no_co_author_line(record_property, tmp_path):
> 145:def test_dokimas_own_settings_file_keeps_the_owners_co_author_line(record_property, tmp_path):
> 167:def test_agents_copy_the_owner_docs_file_the_settings_name_in_place_of_the_rules_file(record_property, tmp_path):
> 194:def test_the_planner_and_worker_prompts_name_the_owner_docs_file_the_settings_name(record_property, tmp_path):
> 214:def test_the_workers_prompt_lists_the_protected_paths_the_settings_name(record_property, tmp_path):
> 230:def test_the_planner_prompts_runner_line_is_drawn_from_the_test_settings(record_property, tmp_path):
> 253:def test_the_style_prompts_caps_table_is_drawn_from_the_caps_setting(record_property, tmp_path):
> 270:# 796.7 ------------------------------------------------------------------------------------------------------------
> 275:def test_a_repos_house_rules_file_is_added_after_the_shipped_prompt(record_property, tmp_path):
> 278:    Proves 796.7. Main holds a house rules file with the line HOUSE-RULE-ON-MAIN. Builds the planner's prompt through
> 282:    record_property("proves", "796.7")
> 286:        f"796.7: th

`7. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/roles; grep -n "AGENTS.md\|pytest\|dokima/\|more than 3\|three blocks\|When X" dokima/roles/planner.md dokima/roles/worker.md dokima/roles/reviewer.md | head -40; grep -n "max_questions\|max_blocks\|{{" dokima/prompt.py | head
```

> plan-grade.md
> planner.md
> result-grade.md
> reviewer.md
> style.md
> worker.md
> dokima/roles/reviewer.md:49:word with where they said them: the issue's own link, the link of a code owner's comment on it, or AGENTS.md. Code
> dokima/roles/reviewer.md:75:  its comments' links, or AGENTS.md", "changes": false}
> dokima/roles/reviewer.md:84:  {"kind": "question", "to": "owner", "label": "Doubt: already fixed", "text": "The ask looks already fixed: closed pull requests already leave the board. Should the plan only add a test that pins it? The plan assumes so.", "evidence": "dokima/board.py, column() returns Done for a closed pull request."}
> dokima/roles/reviewer.md:85:  {"kind": "question", "to": "owner", "label": "Doubt: patches a symptom", "text": "Hiding the stale pill patches a symptom: the pill is stale because the sweep skips closed issues. Should the plan fix the sweep instead? The plan assumes it should.", "evidence": "dokima/board.py, sweep() reads only open issues."}
> dokima/roles/reviewer.md:89:  {"kind": "blocker", "to": "planner", "label": "Weak test", "text": "The test for 9.1 passes against a stub, so it proves nothing.", "evidence": "tests/test_x.py::test_a passes with dokima/x.py emptied."}
> dokima/roles/reviewer.md:91:  {"kind": "blocker", "to": "planner", "label": "Wrong plan", "text": "The plan changes dokima/board.py, but the pill the owner asked about is drawn in dokima/card.py, so building the plan leaves the ask undone.", "evidence": "dokima/card.py draws the pill; dokim

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "Current runner\|AGENTS.md\|owner_docs\|replace(" dokima/prompt.py | head -20; sed -n 228,252p tests/test_settings_prompts.py
```

> 4:GRADE.md, ROLE.md) with the settings drawn in: the owner docs file in place of AGENTS.md, the protected paths in the
> 27:RUNNER = re.compile(r"^Current runner .*\n.*\n", re.M)
> 47:    return (f"Current runner: `{tests['run_all']}` runs every test and `{tests['run_one']}` one, tests in "
> 58:    return text.replace("AGENTS.md", str(got["owner_docs"]))
> # 796.5 ------------------------------------------------------------------------------------------------------------
> 
> def test_the_planner_prompts_runner_line_is_drawn_from_the_test_settings(record_property, tmp_path):
>     """The planner's runner line names the repo's test command, test folder and criterion tag.
> 
>     Proves 796.5. The settings name make check-all and make check-one {test} as the test commands, checks_here as
>     the test folder and criterion_tag as the tag. Builds the planner's prompt through agent.yml and checks its
>     'Where your tests run' section names make check, checks_here and criterion_tag, and no longer says pytest in
>     tests/. Then no settings file: the section still names record_property, the default tag."""
>     record_property("proves", "796.5")
>     settings = ("tests:\n  run_all: make check-all\n  run_one: make check-one {test}\n  dir: checks_here\n"
>                 "  tag: criterion_tag\n")
>     prompt, result, box = prompt_of(tmp_path / "set", "planner", settings=settings)
>     where = section(prompt, "Where your tests run")
>     assert where, f"796.5: the planner's prompt has no 'Where your tests r

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "dokima/\|\.py\|AGENTS" dokima/roles/plan-grade.md dokima/roles/result-grade.md dokima/roles/style.md | head
```

> (Bash completed with no output)

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/741"
C1=I+"#issuecomment-6204381975"; C2=I+"#issuecomment-6205062350"; C3=I+"#issuecomment-6234488387"
asks=[
("Role prompts ship with Dokima and contain no example from Dokima's own code.",I,"S1.1"),
("a scan finds no Dokima file name in any shipped prompt",I,"S1.1"),
("The 50-line \"raising\" block copied into planner, worker and reviewer moves to one shared `roles/raising.md` with neutral examples.",I,"S1.2"),
("moves to one shared `roles/raising.md`",I,"S1.3"),
("Numbers written into prompts (\"more than 3 questions\", ...) are read from settings.",I,"S1.4"),
("Numbers written into prompts (... \"three blocks in a row\", ...) are read from settings.",I,"S1.5"),
("Default criterion style in the planner prompt: \"When X, Y\".",I,"S1.6"),
("A repo appends house rules through `prompts.append` in `settings.yaml`, per role or for all.",I,"S1.10"),
("a repo's house rules appear after the shipped prompt for each role",I,"S1.10"),
("The planner tries to write each criterion with a source, a result ... and a test.",C2,"S1.7"),
("Each blank it cannot fill becomes one question to the owner, kind `question`.",C2,"S1.8"),
("Examples for the prompt:",C2,"S1.9"),
("Nothing dropped. Every sentence of the owner's maps to a criterion or is marked \"not a requirement\" with a reason.",C1,"S2.1"),
("No stale criteria. Sources are append-only and later words win.",C1,"S2.2"),
("the reviewer confirms or retires it.",C1,"S2.3"),
("Conflicts handled. When two owner sources disagree and no later word settles it, the reviewer asks the owner. It never picks.",C1,"S2.4"),
("Nothing added. Every change in the diff serves a criterion.",C1,"S2.5"),
("**Reviewer: required boxes.** One per duty",C2,"S2.6"),
("every box present",C2,"S3.1"),
("entries typed",C2,"S3.2"),
("A weak-test claim without a named counterexample is rejected by code.",C2,"S3.3"),
("each entry a blocker unless noted
```

> rc=0

**Agent:** I blocked the plan for [#741](https://github.com/dokima-dev/dokima/issues/741) (generic role prompts with house rules) on one small gap. The hand-back passes both checks.

**What the planner fixed since the last review:**
- It added a criterion that a repo's house rules come after the shipped prompt for each role. The two existing house-rules tests prove it, and they pass on main (10 of 10 in that test file).
- It split the two criteria that each held two behaviors into four, one behavior each.
- It added the wrong-kind case for an `added` entry.
- It records the rewrite sizes and the untouched grade prompts as not requirements, as you said.

**The blocker (for the planner):**
- Criterion S3.1 rejects a review that is missing a box, but its only named case is at plan review.
- On 2026-10-17 you wrote "Every box must be present at both stages."
- As written, code that checks the boxes only at plan review would still pass.
- The fix is one more case: at code review, a review missing a box is rejected.

**What I checked and found fine:**
- Every ask in your issue and comments maps to a criterion. None is missing.
- Each criterion is one behavior, and the size is ok.
- The other two prompt files that must stay as they are (`plan-grade.md`, `result-grade.md`) name no Dokima files, so the "no Dokima file names" scan won't clash with leaving them alone.
- The plan lists no new tests yet; the split plan leaves tests to each story.

The review is in `/tmp/dokima-out/review.json`.

# reviewer (plan) for #741

Run: https://github.com/dokima-dev/dokima/actions/runs/39037417694

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (37KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/5530a55d-0191-4069-b2cb-89827f75776b/tool-results/buzo4aeao.txt
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
> 04-reviewer-plan.json
> 05-planner.json
> # Issue #741: Generic role prompts with repo-appended house rules
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 781, 784, 787, 793, 796 -->
> <!-- dokima-blocking: {"blocked_by": [779, 781, 784, 787], "blocks": [746], "loop": []} -->
> The shipped role prompts drop Dokima's own examples, share one raising text, and spell out planner questions and reviewer duties.
> 
> **Plan**
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" 

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
> **Plan**
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
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/743
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/790
> - https://github.com/dokima-dev/dokima/issues/656
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; cat in/04-reviewer-plan.json | head -c 6000
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
cd /tmp/pack; python3 -c "
import json
r=json.load(open('in/04-reviewer-plan.json'))['handback']
for k in ['asks','behaviors','edge_cases','tests','size']: print(k, json.dumps(r[k])[:3000])
"; python3 -c "
import json
a=json.load(open('in/03-planner.json'))['handback']; b=json.load(open('plan.json'))
import difflib
print('\n'.join(difflib.unified_diff(json.dumps(a,indent=1).splitlines(),json.dumps(b,indent=1).splitlines(),lineterm='')))
" | head -80; cd /home/runner/work/dokima/dokima; grep -n "def test_a_repos_house_rules_file\|def test_a_house_rules_section" tests/test_settings_prompts.py; ls tests/test_review_boxes.py tests/test_role_prompts.py 2>&1
```

> Exit code 2
> asks [{"ask": "Role prompts ship with Dokima and contain no example from Dokima's own code.", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.1"}, {"ask": "a scan finds no Dokima file name in any shipped prompt", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.1"}, {"ask": "The 50-line \"raising\" block copied into planner, worker and reviewer moves to one shared `roles/raising.md` with neutral examples.", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.2"}, {"ask": "moves to one shared `roles/raising.md`", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.3"}, {"ask": "Numbers written into prompts (\"more than 3 questions\", ...) are read from settings.", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.4"}, {"ask": "Numbers written into prompts (... \"three blocks in a row\", ...) are read from settings.", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.5"}, {"ask": "Default criterion style in the planner prompt: \"When X, Y\".", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.6"}, {"ask": "A repo appends house rules through `prompts.append` in `settings.yaml`, per role or for all.", "source": "https://github.com/dokima-dev/dokima/issues/741", "criterion": "S1.10"}, {"ask": "a repo's house rules appear after the shipped prompt for each role", "source": "https

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 270,330p tests/test_settings_prompts.py; python3 -m pytest -q tests/test_settings_prompts.py -k "house_rules" 2>&1 | tail -3
```

> # 796.7 ------------------------------------------------------------------------------------------------------------
> 
> HOUSE = ".dokima/house-rules.md"
> 
> 
> def test_a_repos_house_rules_file_is_added_after_the_shipped_prompt(record_property, tmp_path):
>     """A repo's house rules reach the agent, after the whole shipped prompt.
> 
>     Proves 796.7. Main holds a house rules file with the line HOUSE-RULE-ON-MAIN. Builds the planner's prompt through
>     agent.yml and checks the line is there, after the last line of the shipped planner prompt. Then the planner's
>     branch changes the file to HOUSE-RULE-ON-BRANCH: the prompt keeps main's line, never the branch's. Then a repo
>     with no house rules file: the prompt is still built and the agent starts."""
>     record_property("proves", "796.7")
>     shipped = open(os.path.join(ts.ROOT, "dokima", "roles", "planner.md")).read().strip().splitlines()[-1]
>     prompt, result, box = prompt_of(tmp_path / "set", "planner", files={HOUSE: "HOUSE-RULE-ON-MAIN\n"})
>     assert "HOUSE-RULE-ON-MAIN" in prompt, \
>         f"796.7: the planner's prompt does not hold the repo's house rules; job {result}\n{box.tail()}"
>     assert shipped in prompt and prompt.index("HOUSE-RULE-ON-MAIN") > prompt.index(shipped), \
>         "796.7: the house rules do not come after the shipped planner prompt"
>     prompt, result, box = prompt_of(tmp_path / "branch", "planner", files={HOUSE: "HOUSE-RULE-ON-MAIN\n"},
>                                     branch_files={HOUSE: "HOUSE-RU

**Agent:** Grading round three of the plan: the one open gap is fixed, so I'm writing an approval now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
r=json.load(open('in/04-reviewer-plan.json'))['handback']
for e in r['edge_cases']: e['missing']=[]
out={"previous_step":{"did":["The planner adds a code review case: a review missing a box is rejected, naming it."],
 "decided":["Boxes are checked at both plan review and code review, as the owner said."],
 "open":[]},
 "verdict":"approve",
 "summary":"Approved: every ask has a criterion, and the code review case for missing boxes is now listed.",
 "raises":[],"answers":[],
 "asks":r['asks'],"behaviors":r['behaviors'],"edge_cases":r['edge_cases'],"tests":[],"size":"ok"}
json.dump(out,open('/tmp/dokima-out/review.json','w'),indent=1)
print(len(out['asks']), [a['criterion'] for a in out['asks']])
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 741 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> 26 ['S1.1', 'S1.1', 'S1.2', 'S1.3', 'S1.4', 'S1.5', 'S1.6', 'S1.10', 'S1.10', 'S1.7', 'S1.8', 'S1.9', 'S2.1', 'S2.2', 'S2.3', 'S2.4', 'S2.5', 'S2.6', 'S3.1', 'S3.2', 'S3.3', 'S3.4', 'S3.5', 'S3.6', 'S3.1', 'S3.1']
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner adds a code review case: a review missing a box is rejected, naming it./The planner adds a code review case: a review missing a box is rejected./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 741 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#741](https://github.com/dokima-dev/dokima/issues/741) (shipped prompts that fit any repo). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's blocker is fixed:** the planner added the missing case. At code review, a review that leaves out one of the six boxes is now rejected, and the rejection names the box. That matches your answer that every box must be there at both stages.
- **Nothing is missing:** every ask in the issue and your comments maps to a criterion. The rewrite sizes and leaving the two grade prompts alone are recorded as not requirements, as you said.
- **House rules after each role's prompt:** this is proved by the two tests that already exist, and I ran both; they pass on this branch.
- **Size:** each criterion is one behavior.

I raised nothing new, and no blockers were waiting for an answer.

The plan's story tests aren't written yet, so I couldn't check that they fail today. That check happens when each story gets its tests.

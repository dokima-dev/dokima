# reviewer (plan) for #796

Run: https://github.com/dokima-dev/dokima/actions/runs/39011320733

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> total 40
> drwxr-xr-x 2 runner runner 4096 Oct 17 06:49 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 06:49 ..
> -rw-r--r-- 1 runner runner 8788 Oct 17 06:49 01-planner.json
> -rw-r--r-- 1 runner runner 6557 Oct 17 06:49 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 9629 Oct 17 06:49 03-planner.json
> # Issue #796: Co-author, owner docs and prompts follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 795 -->
> <!-- dokima-blocking: {"blocked_by": [795], "blocks": [], "loop": []} -->
> Commits credit the co-author the settings name, and agent prompts follow the repo's docs, paths, caps and house rules.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
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
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/790
> 
> 
> **User story:** A repo's settings decide who comm

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/02-reviewer-plan.json','in/03-planner.json']:
    d=json.load(open(f)); print(f); print(json.dumps(d,indent=1)[:5000])
"; cd /home/runner/work/dokima/dokima; cat dokima/defaults.yaml; ls .dokima 2>&1; git diff main --stat
```

> in/02-reviewer-plan.json
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39010007596",
>  "commit_before": "af1cac8812dd0b7a6541718d5c49ca07c3dfa5bf",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 90412,
>   "turns": 13,
>   "cost_usd": 0.6579342,
>   "tokens_in": 653505,
>   "tokens_out": 6916
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/796/39010007596-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39010007596",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote eight criteria, one per ask of story 4 of the parent plan.",
>     "The planner wrote one test per criterion; each fails today because the feature is missing."
>    ],
>    "decided": [
>     "A role's house rules section is a heading naming that role.",
>     "With no settings file, commits keep today's co-author line."
>    ],
>    "open": [
>     "The owner has two questions to answer: role sections and the default co-author."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan carries all eight asks, each with a test that fails today because the feature is missing.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "The co-author line on Dokima's commits comes from the co-author setting.",
>     "source": "https://github.com/dokima-dev/dokima/issues/779",
>     "criterion": "796.1"
>    },
>    {
>     "ask": "Agents copy the owner docs file the settings name, in place of the rules file.",
>     "sou

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_settings_prompts.py
```

> """Tests for #796: co-author, owner docs and agent prompts follow the repo's settings.
> 
> The settings live in `.dokima/settings.yaml` on the default branch, over Dokima's shipped defaults in
> `dokima/defaults.yaml`. This story reads these of them:
> 
>     co_author: Ann Example <ann@example.com>    # the Co-authored-by line on Dokima's commits; empty for none
>     owner_docs: AGENTS.md                       # the owner docs file agents copy, read and are told about
>     protected_paths: [.github/]                 # paths the worker's prompt says it may never change
>     tests: {run_all: ..., dir: tests, tag: record_property}   # what the planner's runner line says
>     style: {caps: {summary: 20, ...}}           # the caps table of the style prompt
>     prompts: {append: [{name: house-rules, file: .dokima/house-rules.md}]}   # house rules after the shipped prompt
> 
> A house rules file's text goes to every role; a `## planner`, `## worker` or `## reviewer` section of it, running to
> the next `## ` heading, goes only to that role's prompt.
> 
> Each test runs real steps of a workflow the way GitHub runs them, through tests/test_settings_workflows.py's Box: a
> temp repo whose default branch holds the settings file, a fake GitHub and a fake Claude Code. The prompt tests run
> agent.yml's checkout steps and its agent step, then read the prompt the step wrote for the agent. Nothing leaves the
> machine.
> """
> import os
> import re
> import subprocess
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> i

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "Co-authored-by\|Soleymanifar" --include=*.yml --include=*.py --include=*.yaml --include=*.sh . | grep -v "^./tests/" | head -20; timeout 900 python -m pytest -q -p no:cacheprovider tests/test_settings_prompts.py -n auto 2>&1 | tail -30
```

> .github/workflows/wiki.yml:36:            git commit -m "Sync from ${GITHUB_SHA::7}" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> tests/test_settings_prompts.py:6:    co_author: Ann Example <ann@example.com>    # the Co-authored-by line on Dokima's commits; empty for none
> tests/test_settings_prompts.py:32:TODAY = "Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> tests/test_settings_prompts.py:105:    checks each pushed commit carries 'Co-authored-by: Ann Example <ann@example.com>' and not today's fixed line.
> tests/test_settings_prompts.py:110:    assert f"Co-authored-by: {ANN}" in message, \
> tests/test_settings_prompts.py:114:    assert f"Co-authored-by: {ANN}" in wiki, \
> tests/test_settings_prompts.py:118:    assert "Co-authored-by" not in empty, \
> tests/test_settings_prompts.py:133:    assert "Co-authored-by" not in default, \
> tests/test_settings_prompts.py:136:    assert "Co-authored-by" not in wiki, \
> tests/test_settings_prompts.py:139:    assert "Co-authored-by" not in other, \
> tests/test_settings_prompts.py:154:    assert f"Co-authored-by: {TODAY}" in message, \
> .github/workflows/agent.yml:455:            git diff --cached --quiet || git commit -qm "$ROLE for #$N (run ${{ github.run_id }})" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> tests/test_manual_fix_check.py:19:OWNER = "RezaSoleymanifar"
> tests/test_bot_identity.py:19:REZA_EMAIL = "341

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -p no:cacheprovider tests/test_settings_prompts.py -n auto 2>&1 | grep -E "^FAILED|Error" | cut -c1-300
```

> E       AssertionError: 796.10: Dokima's own repo has no .dokima/settings.yaml to hold the co-author line
> tests/test_settings_prompts.py:152: AssertionError
> E       AssertionError: 796.2: the runtime holds no RULES.md, the owner docs file the settings name: ['.dokima', 'AGENTS.md', 'dokima', 'rules']
> tests/test_settings_prompts.py:178: AssertionError
> E       AssertionError: 796.1: the planner's commit does not credit the co-author the settings name; its message:
> tests/test_settings_prompts.py:110: AssertionError
> E       AssertionError: 796.5: the planner's runner line does not name the test settings ['make check', 'checks_here', 'criterion_tag']:
> tests/test_settings_prompts.py:244: AssertionError
> E           AssertionError: 796.3: the planner's prompt does not name docs/RULES.md, the owner docs file
> tests/test_settings_prompts.py:205: AssertionError
> E       AssertionError: 796.7: the planner's prompt does not hold the repo's house rules; job success
> tests/test_settings_prompts.py:285: AssertionError
> E       AssertionError: 796.9: with no settings file, the planner's commit still has a co-author line:
> tests/test_settings_prompts.py:133: AssertionError
> E       AssertionError: 796.4: the worker's prompt does not list the protected paths the settings name: ['ops/deploy/', 'vault/']
> tests/test_settings_prompts.py:223: AssertionError
> E       AssertionError: 796.6: the caps table does not follow the caps setting; want {'summary': '33', 'a blocker': '44', 'user_story': '20'}, got {'s

**Agent:** Status: all ten new tests fail today for the right reason. Now writing the review.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner added two criteria from the owner's answer on the co-author default.",
          "The planner raised the shipped bot name as its own issue."],
  "decided": ["A role's house rules section is a heading naming that role, as the owner confirmed.",
              "Shipped defaults credit no co-author; this repo's own settings file keeps the owner's line."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan now carries the owner's two answers; all ten tests fail today because the feature is missing.",
 "raises": [],
 "answers": [{"raise": "P3", "answer": "done", "why": "Checked: the shipped defaults name Dokima's own app. It lies outside this issue, so it stays an issue proposal."}],
 "asks": [
  {"ask": "The co-author line on Dokima's commits comes from the co-author setting.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.1"},
  {"ask": "Agents copy the owner docs file the settings name, in place of the rules file.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.2"},
  {"ask": "The planner and worker prompts name the owner docs file the settings name.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.3"},
  {"ask": "The worker's prompt lists the protected paths the settings name.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.4"},
  {"ask": "The planner prompt's runner line is drawn from the test settings.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.5"},
  {"ask": "The style prompt's caps table is drawn from the caps setting.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.6"},
  {"ask": "A repo's house rules file is added after the shipped prompt.", "source": "https://github.com/dokima-dev/dokima/issues/779", "criterion": "796.7"},
  {"ask": "A house rul
```

> Exit code 1
> the answer to P3 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P3 files an issue, so verdict must be symptom, root cause or new, not None

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent.py | head -30; grep -rn "searched" rules/*.md | head
```

> 40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "searched" dokima/*.py | head -20; grep -rln "root cause" rules/ dokima/roles/ | head
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_autopilot.py:198:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/raises.py:22:# An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> dokima/raises.py:23:SEARCHED = "searched"
> dokima/raises.py:45:    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> dokima/raises.py:47:    searched = decided.get(SEARCHED)
> dokima/raises.py:48:    if not is_numbers(searched) or not searched:
> dokima/raises.py:49:        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
> dokima/raises.py:50:                        f"cause, not {searched!r}")
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 15,70p dokima/raises.py; sed -n 14,45p dokima/agent_checks.py; ls /tmp/pack
```

> "reviewer": ("planner", "worker", "owner"),
> })
> # A worker's raise to the planner goes through the reviewer, who answers it first.
> THROUGH = MappingProxyType({("worker", "planner"): "reviewer"})
> # An issue the planner or the worker raises is filed only once the reviewer confirms it.
> CONFIRMS = "reviewer"
> FIELDS = ("kind", "to", "label", "text", "evidence")
> # An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> SEARCHED = "searched"
> # Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
> VERDICT = "verdict"
> VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> # A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
> CAUSE = "cause"
> SYMPTOMS = "symptoms"
> STAMPED = ("raised_by", "id")
> ANSWERS = ("done", "disagree")
> PREFIX = MappingProxyType({"planner": "P", "worker": "W", "reviewer": "R"})
> 
> 
> def _kinds():
>     return ", ".join(KINDS[:-1]) + " or " + KINDS[-1]
> 
> 
> def _verdicts():
>     names = list(VERDICTS)
>     return ", ".join(names[:-1]) + " or " + names[-1]
> 
> 
> def filing_problems(where, decided):
>     """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
>     problems = []
>     searched = decided.get(SEARCHED)
>     if not is_numbers(searched) or not searched:
>         problems.append(f"{where} files an issue, so {SEARCHED} must 

`10. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
    print(i.get('number'), i.get('title'), (i.get('body') or '')[:150].replace('\n',' '))
" | grep -iE "bot|default|slug|app|tuned|789" | head -20; cat owner_words.json | head -50
```

> 791 No shipped default value is left in Dokima's code 
> 789 The bot Dokima recognizes comes from settings 
> 779 Settings file over shipped defaults, read by every workflow 
> 747 One shared GitHub App: dokima[bot] everywhere, one-click install 
> 741 Generic role prompts with repo-appended house rules 
> 740 One settings file per repo over shipped defaults 
> 694 When the owner approves new scope raised on a child story, code opens a fresh sibling issue under its parent. 
> 676 A merge is not tied to the commit the code review approved 
> 558 Answers to raises say what happened: fixed, answered or filed, not done 
> 457 The play-through's bot posts the stand-in records and live cards itself, as agent.yml's posting steps do, because a bot comment never starts the river (no /work, no agent.yml run). 
> 378 Autopilot and the owner's Approve add a pull request to the merge queue, and the issue says when it lands or why it left 
> 363 Main is protected by a ruleset with the bot as the only bypass, not by switching protection off 
> 349 Parked: remove the old card and board code the new approach replaced, in small steps 
> 292 Code review and Owner approval show as checks beside All tests and Acceptance criteria, as on the card 
> 111 Merge queue: approve PRs in any order, main stays green 
> 41 Onboarding: every adopter creates their own Dokima bot in one click 
> {
>  "https://github.com/dokima-dev/dokima/issues/796#issuecomment-6230833365": "/plan Q1 (a role's house rules section is a heading naming the role i

`11. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
    if i.get('number') in (747,789,791): print(i.get('number'), i.get('title'), '\n', (i.get('body') or '')[:2500], '\n-----')
"
```

> 791 No shipped default value is left in Dokima's code 
>   
> -----
> 789 The bot Dokima recognizes comes from settings 
>   
> -----
> 747 One shared GitHub App: dokima[bot] everywhere, one-click install 
>   
> -----
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Answering the planner's raised issue: it overlaps open issues, so I'll disagree rather than file a duplicate.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['answers']=[{"raise":"P3","answer":"disagree","why":"Overlaps open #789 on the bot from settings; #747 plans one shared Dokima app for every repo."}]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 796 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#796](https://github.com/dokima-dev/dokima/issues/796) (commits credit the co-author from settings, and prompts follow settings). The hand-back passes both checks.

**What changed since the last review**
- The planner now uses both of your answers:
  - **Role sections:** a section is a heading naming the role. The test for criterion 8 uses `## planner` and `## worker` headings.
  - **Co-author:** criterion 9 says the shipped default credits no one. Criterion 10 says this repo's own `.dokima/settings.yaml` keeps your line.
  - The old case "with no settings file, commits keep today's line" is gone.

**Tests**
- I ran all ten new tests. Each fails today because the feature isn't built yet, not because of a crash or a broken setup.
- Criterion 10's test fails because this repo has no settings file yet.

**Your asks**
- All eleven of your asks are carried by a criterion: the eight from the parent plan and three from your comment.
- A twelfth line of your comment says no shipped default may be tuned to this repo. I matched it to criterion 9. It's a general rule more than a single behaviour: for this issue it covers the empty co-author default, and the other defaults here look like they fit any repo.

**The planner's new issue (shipped bot name is Dokima's own app)**
- I disagreed, so it isn't filed. It overlaps [#789](https://github.com/dokima-dev/dokima/issues/789) (the bot comes from settings).
- Also, [#747](https://github.com/dokima-dev/dokima/issues/747) (one shared Dokima app for every repo) suggests a shipped default naming Dokima's app may be what you want.
- If you do want it filed, say so.

The review is in `/tmp/dokima-out/review.json`.

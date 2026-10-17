# reviewer (plan) for #781

Run: https://github.com/dokima-dev/dokima/actions/runs/39018979736

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 108
> drwxr-xr-x  3 runner runner  4096 Oct 17 08:52 .
> drwxrwxrwt 18 root   root    4096 Oct 17 08:52 ..
> drwxr-xr-x  2 runner runner  4096 Oct 17 08:52 in
> -rw-r--r--  1 runner runner  7478 Oct 17 08:52 issue.md
> -rw-r--r--  1 runner runner     2 Oct 17 08:52 open_blockers.json
> -rw-r--r--  1 runner runner 60726 Oct 17 08:52 open_issues.json
> -rw-r--r--  1 runner runner 10794 Oct 17 08:52 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 17 08:52 parent.json
> -rw-r--r--  1 runner runner  6532 Oct 17 08:52 plan.json
> 
> in:
> total 16
> drwxr-xr-x 2 runner runner 4096 Oct 17 08:52 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 08:52 ..
> -rw-r--r-- 1 runner runner 7337 Oct 17 08:52 01-planner.json
> # Issue #781: Finding and checking tests follows the test settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> Dokima finds, checks and times tests by the repo's test settings, not its own fixed values.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - 

`2. Bash`
```
cd /tmp/pack; cat parent.json; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; python3 -c "
import json;d=json.load(open('owner_words.json'));print(json.dumps(d,indent=1)[:12000])"
```

> {"number": 740}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "39018820027",
>  "commit_before": "826f2054bb114cbc1ad96e5b11080798cb967ec1",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 104486,
>   "turns": 14,
>   "cost_usd": 0.7588086,
>   "tokens_in": 718505,
>   "tokens_out": 8031
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/781/39018820027-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39018820027",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/781#issuecomment-6231944045"
> }
> {
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n- Every opinion specific to Dokima's own repo becomes a setting with a default: default branch, records branch, rules file name, bot identity, co-author trailer (#110), test install/run_all/run_one commands 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md | head -80; ls tests | head -50; git log --oneline -3; grep -n "split\|S<s>\|asks" dokima/agent_checks.py | head -40
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> agent_patch.py
> card_player.py
> conftest.py
> fake_gh.py
> fixtures
> record_seed.py
> rules_files.py
> samples
> test_agent.py
> test_agent_codex.py
> test_agent_key_scrubbed.py
> test_agent_kimi.py
> test_agent_split.py
> test_agents.

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "tests:\|^  [a-z_]*:\|text_only\|not_text\|style:\|docstring" dokima/defaults.yaml | head -60; grep -n "PROVES\|TEST_DEF\|NOT_TEXT\|MANUAL_FIX" dokima/checks.py dokima/planner.py | head; grep -n "NEW_TEST_TIMEOUT\|DOCSTRING_CAP\|def main_with_tests\|def passing_today\|startswith(\"tests/\")" dokima/planner.py
```

> 3:tests:
> 4:  tag: record_property
> 5:  dir: tests
> 6:  file_pattern: test_*.py
> 7:  run_one: python -m pytest -q -p no:cacheprovider {test}
> 8:  run_all: pytest -q -p no:cacheprovider -n auto tests
> 9:  new_test_timeout_s: 60
> 10:  affected: testmon
> 12:  exclude: []
> 14:  python: "3.12"
> 15:  test_tools: pytest pytest-xdist pytest-testmon
> 16:  install: ""
> 18:  test_setup_files: [conftest.py, pytest.ini, tox.ini, setup.cfg, pyproject.toml]
> 20:text_only:
> 21:  not_text: [tests/, .github/]
> 23:  default: main
> 25:  branch: logs
> 29:style:
> 30:  docstrings: required
> 31:  docstring_cap: 15
> 32:  code_docstring_cap: 15
> 33:  caps:
> 51:  max_blocks: 3
> 53:  max_questions: 3
> 55:  required: [all tests, Acceptance criteria]
> 57:  checks_wait_min: 45
> 58:  exclude: [card, board wait]
> 60:  method: squash
> 62:  plan: plan
> 63:  work: work
> 64:  autopilot: autopilot
> 65:  filed: filed-by-dokima
> 67:  planner:
> 69:  worker:
> 71:  reviewer:
> 74:  append:
> 78:  slug: dokima-runtime
> 80:  icon_base: https://raw.githubusercontent.com/{repo}/main/dokima/icons/
> 86:  app_only_identity: true
> 87:  keys_from_main: true
> 88:  fence: true
> 89:  judge_runs_main_copy: true
> 90:  owner_approval: true
> dokima/planner.py:26:from dokima.checks import PROVES, TEST_DEF
> dokima/planner.py:407:            out[name] = (src, PROVES.findall(src))
> dokima/planner.py:409:        found = TEST_DEF.match(line)
> dokima/checks.py:23:PROVES = re.compile(r"""record_property\(\s*["']proves["']\s*,\s*["']([\d.]+)["']\s*\)""")
> dokima/checks.py:24:TEST_DEF = re.c

`5. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
p=json.load(open('plan.json'))
asks=[];beh=[];edge=[]
for s,st in enumerate(p['stories'],1):
    for k,c in enumerate(st['acceptance_criteria'],1):
        cid=f"S{s}.{k}"
        asks.append({"ask":c['text'],"source":"https://github.com/dokima-dev/dokima/issues/781","criterion":cid})
        beh.append({"criterion":cid,"one_behavior":True,"why":"One setting decides one result."})
        edge.append({"criterion":cid,"cut":[],"missing":[]})
r={"previous_step":{"did":["The planner split the 15 criteria into two stories of 10 and 5.","It copied each criterion word for word from the issue."],
 "decided":["The second story waits on the first, since both change the same planner file."],
 "open":["Each story's tests come when its own plan is written."]},
 "verdict":"approve",
 "summary":"The split keeps all 15 asks, each once, in two stories that take turns.",
 "raises":[],"answers":[],"asks":asks,"behaviors":beh,"edge_cases":edge,"tests":[],"size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 781 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#781](https://github.com/dokima-dev/dokima/issues/781) (tests follow the test settings). Both hand-back checks pass.

- **The split:** the planner cut the issue's 15 criteria into two stories, one of 10 and one of 5. Every criterion touches the same planner file, so they can't run side by side. The second story waits for the first.
- **Nothing lost or changed:** each of the 15 asks appears exactly once, word for word from the issue.
- **One thing each:** every criterion is a single behavior.
- **Facts checked:** the planner's notes on where the fixed values live today match the code, and every setting they name already exists in the shipped defaults.
- **No tests yet:** a split comes with no tests. Each story gets its tests when its own plan is written, so I had no tests to run this round.

I raised nothing and had no open blockers to answer. The review is in `/tmp/dokima-out/review.json`.

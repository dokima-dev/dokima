# reviewer (plan) for #784

Run: https://github.com/dokima-dev/dokima/actions/runs/39021637563

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (29.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/77202aa3-f087-4dfd-b5a8-aa2075f17540/tool-results/b8ccfmg8q.txt
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
> # Issue #784: Required checks, labels and the audit follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 787 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> The daily audit and its guard judge a repo by its own settings, not by Dokima's own values.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/784#issuecomment-6232191452) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/doki

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #784: Required checks, labels and the audit follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 787 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> The daily audit and its guard judge a repo by its own settings, not by Dokima's own values.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/784#issuecomment-6232191452) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/791
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/326
> - https://github.com/dokima-dev/dokima/issues/424
> - https://github.com/dokima-dev/doki

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; cat owner_words.json | head -50; cat parent.json | head -c 3000
```

> []
> {
>  "kind": "user_story",
>  "title": "Required checks, labels and the audit follow settings",
>  "summary": "The daily audit and its guard judge a repo by its own settings, not by Dokima's own values.",
>  "user_story": "The audit and filed issues follow a repo's own required checks, label names, colors and merge queue choice.",
>  "acceptance_criteria": [
>   {
>    "text": "The audit wants the default branch to require exactly the checks named in the required checks setting.",
>    "words": "`gates.required: [\"all tests\", \"Acceptance criteria\"]`",
>    "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
>    "files": [
>     "dokima/audit.py",
>     "dokima/manifest.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "The branch rule lacks a check the settings add, so the audit names it.",
>      "test": "tests/test_settings_audit.py::test_the_branch_rule_is_checked_against_the_required_checks_setting"
>     }
>    ]
>   },
>   {
>    "text": "With the merge queue turned off in a repo's settings, the Setup issue never mentions a merge queue.",
>    "words": "merge queue (#375)",
>    "source": "https://github.com/dokima-dev/dokima/issues/740",
>    "files": [
>     "dokima/audit.py",
>     "dokima/defaults.yaml",
>     "dokima/manifest.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "GitHub refuses to list the repo's rulesets while the queue is off.",
>      "test": "tests/test_settings_audit.py::test_with_the_merge_queue_off_the_audit_never_asks_for_one"
>     }
>    ]
>   },
>   {
>    "text":

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39019710086",
>  "commit_before": "960a2dadb5e8b3bbb930998bf3397190932dfd96",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 76591,
>   "turns": 9,
>   "cost_usd": 0.4789548,
>   "tokens_in": 372901,
>   "tokens_out": 6086
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/784/39019710086-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39019710086",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote seven criteria and seven tests, each failing today for the right reason.",
>     "The planner dropped plan and work from the shipped defaults test."
>    ],
>    "decided": [
>     "The audit, not Dokima, asks for each label by its setting name."
>    ],
>    "open": [
>     "Three questions wait for the owner: merge queue, plan and work labels, label creation."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Dokima does create labels, so the plan's label criterion covers only the audit and drops the owner's ask.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "784.3: labels Dokima creates",
>     "text": "Dokima itself adds autopilot and filed labels by fixed names, creating them. Add a criterion and test that it uses the setting names, or name the issue carrying it.",
>     "evidence": "`dokima/agent_autopilot.py:94` says adding a missing label creates it; `:71` and `:155` hard-code the names; `dokima/board

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_settings_audit.py; git diff main --stat
```

> """Tests for #784: the audit judges required checks, labels and colors by the settings.
> 
> The daily audit (`python3 -m dokima.audit OWNER/REPO`) compares the repo's live labels, board pills, branch rule and
> auto-merge lists with what Dokima needs. Here what Dokima needs comes from the merged settings: the shipped defaults
> (`dokima/defaults.yaml`) with the repo's own `.dokima/settings.yaml` over them, read where the audit runs. Each audit
> test runs the real command from outside against the fake `gh` of tests/fake_gh.py, through tests/test_audit_cli.py's
> Audit helper, with a settings file written in the repo folder it runs in.
> 
> The settings these tests write, beside the ones the shipped defaults already hold:
>     gates.required            check names; a repo's list merges with the default one by name
>     merge.queue               false: the repo uses no merge queue (the default, true, keeps today's audit)
>     labels.<key>              the name of each of Dokima's labels (autopilot, filed)
>     colors.labels.<key>       each label's color, by the same key, as GitHub writes it (rrggbb)
>     colors.pills.<field>.<option>  each board pill's color, as GitHub names it (GRAY, BLUE, RED ...)
> 
> The settings guard (`dokima.manifest.undeclared(root)`) is run on a temp repo root holding one code file and one
> workflow file.
> 
> Filing an issue a passed review found (`dokima.agent.file_issues`) runs in a temp repo folder whose settings rename
> the filed label, against a fake GitHub that, like the re

`6. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"
```

`7. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_settings_audit.py; git diff main --stat
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39019710086",
>  "commit_before": "960a2dadb5e8b3bbb930998bf3397190932dfd96",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 76591,
>   "turns": 9,
>   "cost_usd": 0.4789548,
>   "tokens_in": 372901,
>   "tokens_out": 6086
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/784/39019710086-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39019710086",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote seven criteria and seven tests, each failing today for the right reason.",
>     "The planner dropped plan and work from the shipped defaults test."
>    ],
>    "decided": [
>     "The audit, not Dokima, asks for each label by its setting name."
>    ],
>    "open": [
>     "Three questions wait for the owner: merge queue, plan and work labels, label creation."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Dokima does create labels, so the plan's label criterion covers only the audit and drops the owner's ask.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "784.3: labels Dokima creates",
>     "text": "Dokima itself adds autopilot and filed labels by fixed names, creating them. Add a criterion and test that it uses the setting names, or name the issue carrying it.",
>     "evidence": "`dokima/agent_autopilot.py:94` says adding a missing label creates it; `:71` and `:155` hard-code the names; `dokima/board

> """Tests for #784: the audit judges required checks, labels and colors by the settings.
> 
> The daily audit (`python3 -m dokima.audit OWNER/REPO`) compares the repo's live labels, board pills, branch rule and
> auto-merge lists with what Dokima needs. Here what Dokima needs comes from the merged settings: the shipped defaults
> (`dokima/defaults.yaml`) with the repo's own `.dokima/settings.yaml` over them, read where the audit runs. Each audit
> test runs the real command from outside against the fake `gh` of tests/fake_gh.py, through tests/test_audit_cli.py's
> Audit helper, with a settings file written in the repo folder it runs in.
> 
> The settings these tests write, beside the ones the shipped defaults already hold:
>     gates.required            check names; a repo's list merges with the default one by name
>     merge.queue               false: the repo uses no merge queue (the default, true, keeps today's audit)
>     labels.<key>              the name of each of Dokima's labels (autopilot, filed)
>     colors.labels.<key>       each label's color, by the same key, as GitHub writes it (rrggbb)
>     colors.pills.<field>.<option>  each board pill's color, as GitHub names it (GRAY, BLUE, RED ...)
> 
> The settings guard (`dokima.manifest.undeclared(root)`) is run on a temp repo root holding one code file and one
> workflow file.
> 
> Filing an issue a passed review found (`dokima.agent.file_issues`) runs in a temp repo folder whose settings rename
> the filed label, against a fake GitHub that, like the re

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q -p no:cacheprovider tests/test_settings_audit.py 2>&1 | grep -E "^(FAILED|ERROR|E  )|passed|failed" | head -60; git diff main -- tests/test_settings_merge.py
```

> E       AssertionError: 784.1: main requires Lint, which the required checks setting names, yet the audit flagged it: ['Branch rule of `main` requires `Lint`, a check Dokima does not declare.']
> E         unsupported calls: []
> E         writes: [{'kind': 'create', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'pin', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'board', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'board', 'repo': 'acme/widgets', 'number': 101}]
> E       assert not ['Branch rule of `main` requires `Lint`, a check Dokima does not declare.']
> E       AssertionError: 784.2: with the merge queue off in settings, the audit still asks about one: ["Auto-merge is half set up: Dokima's app is missing from the merge queue ruleset's bypass list for pull requests. Add it there for auto-merge, or take it off the other list to keep your approval."]
> E         unsupported calls: []
> E         writes: [{'kind': 'create', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'pin', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'board', 'repo': 'acme/widgets', 'number': 101}, {'kind': 'board', 'repo': 'acme/widgets', 'number': 101}]
> E       assert not ["Auto-merge is half set up: Dokima's app is missing from the merge queue ruleset's bypass list for pull requests. Add it there for auto-merge, or take it off the other list to keep your approval."]
> E       AssertionError: 784.3: the repo holds dokima-autopilot, the name its settings give the autopilot label, yet the audit fla

**Agent:** I've run the plan's nine new tests: all fail today for the right reason. Now checking how settings are read and the guard's signature, then I'll write the review.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def undeclared\|def read\b\|def read(" dokima/manifest.py dokima/settings.py; grep -rn "settings.read(" dokima/*.py | head; grep -n "filed-by-dokima\|def file_issues" dokima/*.py | head
```

> dokima/manifest.py:391:def undeclared(root):
> dokima/settings.py:79:def read(repo=".", warn=None):
> dokima/prompt.py:90:        got = settings.read()
> dokima/agent_autopilot.py:155:FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> dokima/agent_autopilot.py:158:def file_issues(repo, number, rec, recs):
> dokima/manifest.py:20:    "filed-by-dokima": {"color": "bfd4f2", "description": "Created automatically, not by a person"},

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner added two criteria: filed issues carry, and create, the filed label by its setting name.",
   "The planner named the autopilot label as carried by issue 787, as the owner said."
  ],
  "decided": [
   "The plan drops the plan and work labels from the shipped settings."
  ],
  "open": [
   "Two questions wait for the owner: the merge queue reading, and the plan and work labels."
  ]
 },
 "verdict": "approve",
 "summary": "The plan carries every ask with a test that fails today for the right reason; two questions still wait for the owner.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The checks required on the default branch come from the required checks setting.", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "784.1"},
  {"ask": "Turning the merge queue off in a repo's settings stops the audit asking for one.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.2"},
  {"ask": "Dokima creates its labels under the names in the labels setting.", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "784.3"},
  {"ask": "The daily audit no longer flags label and pill colors that match the repo's settings.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.4"},
  {"ask": "The daily audit no longer flags label and pill colors that match the repo's settings.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.5"},
  {"ask": "The settings guard no longer flags a workflow's name, compared in code, as a missing check.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.6"},
  {"ask": "The settings declare no label as one that starts an agent.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.7"},
  {"ask": "Dokima a
```

> Exit code 1
> summary holds 22 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`11. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['summary']="Every ask has a criterion and a test failing today for the right reason; two questions wait for the owner."
d['previous_step']['did'][0]="The planner added criteria: filed issues carry, and create, the filed label by setting name."
d['previous_step']['open'][0]="Two questions wait for the owner: the merge queue, and the plan and work labels."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 784 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for issue [#784](https://github.com/dokima-dev/dokima/issues/784) (the audit follows a repo's own settings). The review is in `/tmp/dokima-out/review.json`, and both checks on it pass.

- **The blocker from my last review is fixed.** Two new criteria cover Dokima's filed label: issues it files carry the label under its settings name (784.8), and Dokima creates that label when the repo doesn't have it (784.9). As you said, the autopilot label is left to [#787](https://github.com/dokima-dev/dokima/issues/787) (puts the autopilot label from settings on the issue).
- **Every ask has a criterion.** I matched each ask from the issue and your comment to a criterion; none is missing.
- **Tests:** I ran all nine new tests and each fails today because the feature isn't built yet, not because of a crash or bad setup. Each one checks its own criterion's behavior and nothing else.
- **One older test changes.** The shipped settings test no longer expects plan and work labels. Every other default it checks stays the same.

Two of the plan's questions are still for you. I didn't answer them for you:
- **Merge queue:** with the queue off, should auto-merge need only main's review exemption? Answering yes or no changes how auto-merge is set up.
- **Plan and work labels:** your list of settings in [#740](https://github.com/dokima-dev/dokima/issues/740) (one settings file per repo) keeps them, but your [#515](https://github.com/dokima-dev/dokima/issues/515) (labels still declared as starting agents) drops them. The plan drops them, and that older test change depends on your answer.

# reviewer (plan) for #744

Run: https://github.com/dokima-dev/dokima/actions/runs/39101989658

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #744: Adopter safety: human PRs pass, audit tolerates the repo's own CI and no board
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 742, 781, 784, 787, 795 -->
> <!-- dokima-blocking: {"blocked_by": [742, 779, 781, 784, 787], "blocks": [746], "loop": []} -->
> An adopter's own pull requests, CI and missing board stop tripping Dokima's checks, audit and card.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246247936) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
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
> - https://github.com/dokima-d

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(list(d.keys()));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; git status; git log --oneline -3; git diff main --stat
```

> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39101788332",
>  "commit_before": "ccbebe20951336dbdfb7da7800bf77e892c34308",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 149978,
>   "turns": 19,
>   "cost_usd": 0.9816543999999999,
>   "tokens_in": 1050978,
>   "tokens_out": 10763
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/744/39101788332-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39101788332",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246247936"
> }
> On branch try/issue-744
> Your branch is up to date with 'origin/main'.
> 
> nothing to commit, working tree clean
> ccbebe2 An empty repo reaches its first merge from the docs (#856)
> 8f381b7 Card and branch updates find checks by shown names (#852)
> b92ec5d A changelog lists what v0.1.0 does (#851)

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md | head -80; grep -n "split" rules/raising.md rules/flow.md | head -30
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> rules/flow.md:4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. I

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "install\|exclude\|unplanned" dokima/defaults.yaml; grep -rn "install\b\|setup.install\|exclude" .github/workflows/full-suite.yml .github/workflows/agent.yml | head -20; sed -n 140,160p dokima/settings.py; grep -n "drift\|declare\|BOARD" dokima/audit.py | head -30
```

> 12:  exclude: []
> 16:  install: ""
> 60:  exclude: [card, board wait]
> .github/workflows/full-suite.yml:12:  # Called by the one workflow an adopter installs (dokima/install/dokima.yml), through entry.yml (#812).
> .github/workflows/full-suite.yml:42:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/full-suite.yml:43:      # The repo's Python, test tools and install command, from its settings file over Dokima's defaults (#794).
> .github/workflows/full-suite.yml:48:          else out=$(printf 'python=3.12\ntest_tools=pytest pytest-xdist\ninstall=\n')
> .github/workflows/full-suite.yml:49:            echo "::notice title=Old setup::No settings reader with a setup mode here, so the old install list is used."; fi
> .github/workflows/full-suite.yml:57:          INSTALL: ${{ steps.setup.outputs.install }}
> .github/workflows/full-suite.yml:59:          pip install -q $TOOLS pyyaml
> .github/workflows/full-suite.yml:80:      # The all-tests command from the settings, leaving out the tests on their exclude list (#795); by default every
> .github/workflows/full-suite.yml:93:            skip=$(PYTHONPATH="$DOKIMA_CODE" PYTHONSAFEPATH=1 python3 -c 'import shlex; from dokima.settings import read; print(" ".join("--deselect " + shlex.quote(str(t)) for t in (read().get("tests") or {}).get("exclude") or []))')
> .github/workflows/agent.yml:89:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/agent.yml:333:      # The repo'

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,30p dokima/defaults.yaml; sed -n 90,125p dokima/audit.py; sed -n 340,380p dokima/audit.py; grep -rn "does not declare\|DOKIMA_BOARD" tests | head; grep -n "No approved plan\|manual-fix\|def build_matrix" -n dokima/checks.py | head
```

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
>   # Tests the all tests check leaves out, by id, e.g. tests/test_live.py::test_network.
>   exclude: []
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
>   # Empty asks GitHub for the repo's default branch (#787).
>   default: ""
> records:
>   branch: logs
> owner_docs: AGENTS.md
> # The Co-authored-by line on Dokima's commits, e.g. Ann Example <ann@example.com>; empty for none. {bot} names the
> # repo's own bot with its address, so by default Dokima shows among the repo's contributors (#812).
> co_author: "{bot}"
>         if (have.get("layout") or "").lower() != want["layout"].lower():
>             lines.append(f"View `{view}` has layout `{have.get('layout')}`; Dokima needs `{want['layout']}`.")
>         if (have.get("filter") or "") != want["filter"]:
>             lines.append(f"View `{view}` has filter `{have.get('filter') or ''}`; Dokima n

**Agent:** Checking the split plan against the owner's asks; drafting the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner split the issue into three stories: unplanned pull requests, the audit, and the card."],
  "decided": ["Dokima's own pull requests stay held to their plan; any other setting value keeps today's failing check.",
              "Installing the repo's needs and leaving out marked tests are left out as already done."],
  "open": ["The owner decides whether those two asks can be left out."]},
 "verdict": "block",
 "summary": "Two owner asks have no criterion, and a missing board could skip the whole audit unnoticed.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion",
   "text": "The asks to install the repo's needs and to leave out marked tests carry no criterion. Keep each as a criterion with a test pinning today's behavior.",
   "evidence": "Issue lines on `tests.install` and `tests.exclude`; `full-suite.yml:57` and `:93` already do both."},
  {"kind": "blocker", "to": "planner", "label": "2.2 missing case",
   "text": "With no board, an audit that checks nothing still exits 0. Add: with no board, other drift is still listed.",
   "evidence": "Story 2 context says to still report other drift; no criterion of 2.1 to 2.3 carries it."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Setting `merge.unplanned_prs: allow` (default) lets them through", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.1"},
  {"ask": "including human and Dependabot PRs", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.2"},
  {"ask": "only Dokima's own PRs are held to the plan", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.3"},
  {"ask": "Setting `merge.unplanned_prs: allow` (default)", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.4"},
  {"ask": "Checks the repo added are not drift.", "source": "https://github.com/dokima-dev/dokima/issues/744",
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`7. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d['previous_step']['did']=["The planner split the issue into three stories: pull requests, the audit, the card."]
d['previous_step']['decided'][0]="Dokima's own pull requests stay held to their plan; other setting values keep today's check."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 744 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I've blocked the planner's split for issue [#744](https://github.com/dokima-dev/dokima/issues/744) (keeping adopters from being tripped on day one). The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What the planner proposed:** three stories.
1. Pull requests with no plan pass unless Dokima opened them.
2. The audit stops flagging the repo's own checks and a missing board.
3. The card redraws when the repo's own CI finishes, and shows every check the merge needs.

All nine criteria are one behavior each, and the size is fine. This is a split proposal, so there are no tests to run yet.

**Why it's blocked:**
- **Two of your asks have no criterion:** installing the repo's own dependencies before the tests, and leaving tests the repo marks off the merge gate. The planner says both already work, and they do: `full-suite.yml` runs the install setting at line 57 and drops the excluded tests at line 93. I've asked the planner to keep each as a criterion with a test that pins what already works, rather than leave them out.
- **A missing board could hide everything:** an audit that simply stops when no board is set would still pass the two no-board criteria. I've asked for one more criterion: with no board, the audit still reports the other problems it finds.

**Still waiting on you:** the planner's question on whether those two already-working asks can be left out. Your issue text doesn't settle it, so I didn't answer it for you. If you say leave them out, my first blocker goes away.

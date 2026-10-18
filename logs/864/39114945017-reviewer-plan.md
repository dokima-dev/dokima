# reviewer (plan) for #864

Run: https://github.com/dokima-dev/dokima/actions/runs/39114945017

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #864: Hotfix pull requests labeled, linked and shown in one line
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 863 -->
> <!-- dokima-blocking: {"blocked_by": [863], "blocks": [], "loop": []} -->
> A hotfix's pull request carries its label, a design choice returns it to planning, and its card is one line.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/863
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/750
> - https://github.com/dokima-dev/dokima/issues/718
> - https://github.com/dokima-dev/dokima/issues/869
> - https://github.com/dokima-dev/dokima/issues/870
> 
> 
> **User story:** Owners spot hotfixes by label and link, see design asks go back to planning, and read one-line cards.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a hotfix worker opens its pull request, the pull request carries the hotfix label.
>   

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:9000])"; cd /home/runner/work/dokima/dokima; git diff 4b4ecc2 HEAD --stat; git diff c92ffd4 HEAD
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39113415880",
>  "commit_before": "c92ffd4a43241a0a5c696ba46d0a0a09f43dff9d",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 83496,
>   "turns": 8,
>   "cost_usd": 0.5487332,
>   "tokens_in": 368083,
>   "tokens_out": 6530
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/864/39113415880-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39113415880",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote eight criteria and one rule, each with a test.",
>     "The planner reused the existing prompt test for the repo rule."
>    ],
>    "decided": [
>     "The planner left out the ask that the pull request links its issue."
>    ],
>    "open": [
>     "The planner asks the owner whether to drop the issue link ask."
>    ]
>   },
>   "verdict": "block",
>   "summary": "One ask, linking the issue from the pull request, has no criterion; the rest is sound and fails today correctly.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "No criterion",
>     "text": "The ask that a hotfix pull request links its issue has no criterion. Keep it, proven by a test that already passes, as the plan does for 864.9.",
>     "evidence": "Issue body, second criterion; `.github/workflows/agent.yml:547` opens with `Closes #N`; 864.9 reuses a passing test.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    }
>   ],
>   "answers": [],
>   "asks": [

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_hotfix.py tests/test_hotfix_pr.py tests/test_hotfix_card.py 2>&1 | tail -20; grep -n "Closes" .github/workflows/agent.yml dokima/*.py | head
```

> Full diff:
>     [
>   -     'planner',
>   +     'reviewer',
>     ]
> FAILED tests/test_hotfix_pr.py::test_a_hotfix_worker_sending_it_back_says_why_on_the_issue - AssertionError: 864.3: issue #57 got no comment saying why the hotfix went back to planning: []
> assert []
> FAILED tests/test_hotfix_card.py::test_a_hotfix_card_shows_its_state_in_one_line - AssertionError: 864.4: the hotfix card is not one line: ['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/o/r/pull/60/files)']
> assert 2 == 1
>  +  where 2 = len(['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/fil..." width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/o/r/pull/60/files)'])
> FAILED tests/test_hotfix_card.py::test_a_hotfix_card_line_shows_the_ask - AssertionError: 864.5: the hotfix card's one line does not carry the ask 'The page title says Dokma; make it say Dokima.': ['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/o/r/pull/60/files)']
> assert (2 == 1)
>  +  where 2 = len(['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.co

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_hotfix.py tests/test_hotfix_pr.py tests/test_hotfix_card.py 2>&1 | grep -E "^(FAILED|PASSED)|passed|failed" | cut -c1-200; python -m pytest -q tests/test_hotfix.py -k "starts_code_review or name_nothing" 2>&1 | tail -3
```

> assert not r.failed, f"864.1: the hotfix worker's run failed; {r.why()}"
>         assert [(x["role"], x["check"]["passed"]) for x in recs] == [("worker", True)], \
> E       AssertionError: 864.7: no card line shows the ask 'The page title says Dokma; make it say Dokima.': ['**Review** · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/needs-you.
>         Proves 864.8. Draws #57's card after its code review approved it and the merge gate passed: the line showing the
>         ask must say merge gate passed. After an approval whose merge gate failed, it says merge gate failed. Before the
> E       AssertionError: 864.8: no card line shows the ask 'The page title says Dokma; make it say Dokima.': ['**Review** · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/needs-you.
> FAILED tests/test_hotfix_pr.py::test_a_hotfix_pull_request_carries_the_hotfix_label - AssertionError: 864.1: the hotfix pull request was opened without the hotfix label; pr create: ['pr', 'create', '-
> FAILED tests/test_hotfix_pr.py::test_a_hotfix_worker_finding_a_design_choice_starts_the_planner - AssertionError: 864.2: a hotfix needing a design choice did not start the planner once: [('reviewer', 
> FAILED tests/test_hotfix_pr.py::test_a_hotfix_worker_sending_it_back_says_why_on_the_issue - AssertionError: 864.3: issue #57 got no comment saying why the hotfix went back to planning: []
> FAILED tests/test_hotfix_card.py::test_a_hotfix_card_shows_its_state_in_one_line - AssertionError: 864.4

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "agent.yml\|def calls\|class Hotfix" tests/test_hotfix.py | head -20
```

> 3:These tests run the agent workflow (.github/workflows/agent.yml) the way GitHub runs it, on the machine from
> 152:class Hotfix(ts.Machine):
> 153:    """One whole run of agent.yml on #57 for ROLE at STAGE, the issue carrying `labels`.
> 198:        wf = ts.workflow("agent.yml")
> 242:    Proves 863.1. Runs agent.yml for the worker, as `/work` starts it, on #57: labeled hotfix, never planned, no
> 337:    Proves 863.6. Runs agent.yml for the reviewer at the pr stage on #57, whose worker built the fix on try/issue-57

**Agent:** All eight new tests fail today for the right reason, and the two reused tests pass. Writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner added criterion 864.9: a hotfix pull request links its issue.",
          "The planner proved 864.9 by a stricter check on an older passing test."],
  "decided": ["The planner renumbered the repo rule to 864.10, its checks unchanged."],
  "open": []},
 "verdict": "approve",
 "summary": "Every ask now has a criterion and a test; the eight new tests fail today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "When a hotfix worker opens its pull request, the pull request carries the hotfix label.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.1"},
  {"ask": "When a hotfix worker opens its pull request, the pull request links the issue it answers.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.9"},
  {"ask": "Keep the ask that a hotfix pull request links its issue, and give it a criterion.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.9"},
  {"ask": "When a hotfix worker finds the ask needs a design choice, the planner starts on the issue.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.2"},
  {"ask": "When a hotfix worker sends the issue back to planning, the issue gets a comment saying why.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.3"},
  {"ask": "When an issue labeled hotfix is drawn, its card shows its state in one line.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.4"},
  {"ask": "When an issue labeled hotfix is drawn, its card line shows the ask.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.5"},
  {"ask": "When a hotfix has a pull request, its card line links that pull request.", "source": "https://github.com/dokima-dev/dokima/issues/864", "criterion": "864.6"},
  {"ask": "When a hotfix 
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#864](https://github.com/dokima-dev/dokima/issues/864) (hotfix pull requests labeled, linked and shown in one line). The hand-back passes both checks.

- **Last round's blocker is fixed.** The plan now has criterion 864.9: a hotfix pull request links the issue it answers.
- **It follows your comment.** 864.9 is proven by an older test that already passes, now with one extra check that the pull request says it closes the issue. That test runs the real workflow, so it would fail if the link were dropped. Nothing it checked before was removed.
- **The repo rule was only renumbered.** It moved to 864.10 and its checks did not change.
- **Every ask has a criterion and a test.** I found nothing dropped, added or left untested.
- **The new tests fail today, as they should.** All eight fail because the feature is missing, not because the tests are broken. The two reused tests (864.9 and 864.10) pass, as you allowed.

There were no open blockers to answer and I raised nothing new. The review is in `/tmp/dokima-out/review.json`.

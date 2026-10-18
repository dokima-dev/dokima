# reviewer (plan) for #811

Run: https://github.com/dokima-dev/dokima/actions/runs/39089900933

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #811: The autopilot workflow still triggers on the fixed label name, so a renamed label never starts it.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Autopilot wakes only for a label named autopilot, so a repo that renames the label never starts it.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/791
> 
> 
> **User story:** Owners who rename the autopilot label in settings can still switch an issue on by adding that label.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a person adds the repo's renamed autopilot label to an issue, its planner starts.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-811/tests/test_autopilot_label.py#L75"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: Adding the repo's renamed autopilot label by hand starts the issue's planner.*
>   <details><summary><p

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/01-planner.json | head -80; git show --stat HEAD; git diff HEAD~1 -- tests | head -200; cat .github/workflows/autopilot.yml
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39089690209",
>  "commit_before": "c074448aa112b1826f24cc0429b50a8a69f66344",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 149522,
>   "turns": 20,
>   "cost_usd": 0.788168,
>   "tokens_in": 1007514,
>   "tokens_out": 7800
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/811/39089690209-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39089690209",
>  "handback": {
>   "kind": "user_story",
>   "title": "A renamed autopilot label starts autopilot",
>   "summary": "Autopilot wakes only for a label named autopilot, so a repo that renames the label never starts it.",
>   "user_story": "Owners who rename the autopilot label in settings can still switch an issue on by adding that label.",
>   "acceptance_criteria": [
>    {
>     "text": "When a person adds the repo's renamed autopilot label to an issue, its planner starts.",
>     "words": "The autopilot workflow still triggers on the fixed label name, so a renamed label never starts it.",
>     "source": "https://github.com/dokima-dev/dokima/issues/811",
>     "files": [
>      ".github/workflows/autopilot.yml",
>      "dokima/agent_roles.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "After a rename, a label still called autopilot starts nothing.",
>       "test": "tests/test_autopilot_label.py::test_the_old_label_name_starts_nothing_once_the_label_is_renamed"
>      }
>     ]
>    }
>   ],
>   "non_functional": [],
>   "test

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_autopilot_label.py 2>&1 | tail -40; grep -rn "autopilot" dokima/settings*.py dokima/*.py | grep -i "label" | head -30
```

> >       assert m.planners_started("811.1") == {}, \
>             f"811.1: the old name 'autopilot' started a planner though the repo renamed its label: {m.planners_started('811.1')}"
> E       AssertionError: 811.1: the old name 'autopilot' started a planner though the repo renamed its label: {101: 1}
> E       assert {101: 1} == {}
> E         
> E         Left contains 1 more item:
> E         {101: 1}
> E         
> E         Full diff:
> E         - {}
> E         + {
> E         +     101: 1,
> E         + }
> 
> tests/test_autopilot_label.py:101: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_autopilot_label.py::test_a_renamed_label_added_by_hand_starts_the_issue - AssertionError: 811.1: adding the renamed label 'on-autopilot' by hand did not start #101's planner once: {}
>   
> assert {} == {101: 1}
>   
>   Right contains 1 more item:
>   {101: 1}
>   
>   Full diff:
>   + {}
>   - {
>   -     101: 1,
>   - }
> FAILED tests/test_autopilot_label.py::test_the_old_label_name_starts_nothing_once_the_label_is_renamed - AssertionError: 811.1: the old name 'autopilot' started a planner though the repo renamed its label: {101: 1}
> assert {101: 1} == {}
>   
>   Left contains 1 more item:
>   {101: 1}
>   
>   Full diff:
>   - {}
>   + {
>   +     101: 1,
>   + }
> 2 failed, 6 passed in 6.37s
> dokima/agent_autopilot.py:73:AUTOPILOT = "autopilot"  # the autopilot label's default name; the repo's is in the labels setting (#787)
> dokima/agent_autopilot.py:76:def autopilot_label():
> dokim

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,40p tests/test_autopilot_label.py; grep -n "files" tests/test_steps.py 2>/dev/null | head; grep -rn "^import\|^from" tests/test_autopilot_label.py; sed -n 675,700p dokima/agent_roles.py
```

> """A person adding the autopilot label by hand switches that issue on, as `/autopilot start` does.
> 
> Before this, autopilot.yml woke only when an issue closed, so an issue labeled by hand with nothing blocking it sat
> idle until someone posted `/plan`. These tests add the label the way GitHub tells of it (`issues: labeled`) and run
> every workflow GitHub starts on that event, on the machine of test_autopilot_close.py.
> """
> from dokima.agent_autopilot import AUTOPILOT_START_LINE
> from test_autopilot_close import Repo, LABEL, planned
> 
> 
> def start_lines(m, n):
>     """How many new comments on issue n read exactly the switched-on Autopilot line."""
>     return sum(1 for b in m.new_comments(n) if b.strip() == AUTOPILOT_START_LINE)
> 
> 
> def test_a_label_added_by_hand_starts_an_issue_nothing_blocks(record_property, tmp_path):
>     """#101 waits on nothing and has nothing started: adding the label by hand starts its planner once, with one line."""
>     m = Repo(tmp_path / "hand", {57: [101]}, {})
>     m.add_label(101)
>     assert not m.failed, f"a workflow failed when the label was added: {m.failures}\n{m.tail()}"
>     assert m.planners_started("label") == {101: 1}, f"started: {m.planners_started('label')}\n{m.tail()}"
>     assert start_lines(m, 101) == 1, f"#101's new comments: {m.new_comments(101)}"
> 
> 
> def test_a_label_added_to_a_blocked_issue_starts_nothing(record_property, tmp_path):
>     """#102 is blocked by #101, still open: the label goes on, but no planner starts until #101 closes."""
>     m = 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_autopilot_close.py 2>&1 | tail -3
```

> ............                                                             [100%]
> 12 passed in 42.34s

**Agent:** Plan tests fail for the right reason; writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote one criterion: adding the renamed autopilot label starts the issue's planner.", "The planner added two tests: the renamed label starts the planner; the old name starts nothing."], "decided": ["After a rename, a label still called autopilot no longer switches an issue on."], "open": []},
 "verdict": "approve",
 "summary": "The plan covers the one ask, and both new tests fail today because the renamed label is ignored.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "The autopilot workflow still triggers on the fixed label name, so a renamed label never starts it.", "source": "https://github.com/dokima-dev/dokima/issues/811", "criterion": "811.1"}],
 "behaviors": [{"criterion": "811.1", "one_behavior": true, "why": "One action, adding the renamed label, and one result, the planner starts."}],
 "edge_cases": [{"criterion": "811.1", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_autopilot_label.py::test_a_renamed_label_added_by_hand_starts_the_issue", "only_its_behavior": true, "why": "Runs the real workflows on a labeled event; fails today with no planner started."},
  {"test": "tests/test_autopilot_label.py::test_the_old_label_name_starts_nothing_once_the_label_is_renamed", "only_its_behavior": true, "why": "Stops code that starts on any label; fails today as the old name starts a planner."}
 ],
 "size": "ok",
 "boxes": {
  "dropped": "none",
  "added": [{"what": "After a rename, the old label name starts nothing", "kind": "needed", "serves": "811.1"}],
  "superseded": "none",
  "conflicts": "none",
  "edges": {"811.1": "covered"},
  "poor_tests": "none"
 }
}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 811 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner added two tests: the renamed label starts the planner; the old name starts nothing./The planner added two tests: the renamed label starts it; the old name starts nothing./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 811 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#811](https://github.com/dokima-dev/dokima/issues/811) (a renamed autopilot label never starts autopilot). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **The ask is covered:** the issue makes one ask, and criterion 811.1 carries it: adding the renamed label starts the issue's planner.
- **Both new tests fail today, for the right reason:**
  - With the label renamed to `on-autopilot`, adding it starts no planner.
  - Adding a label still called `autopilot` does start one.

  Together they mean the build can't pass by starting on any label.
- **One added case, which I accepted:** after a rename, the old name `autopilot` starts nothing. Once the repo renames the label, `autopilot` is just an ordinary label.
- **Nothing else breaks:** the planner gave a shared test helper a way to put a settings file in the test repo. The 12 existing tests in `tests/test_autopilot_close.py` still pass.

No blockers, open questions or outside issues to raise.

The fix has to change `.github/workflows/autopilot.yml`, which normally waits for your approval. This issue is about that file, so the change is expected.

# reviewer (plan) for #662

Run: https://github.com/dokima-dev/dokima/actions/runs/38603507069

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json; ls in
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #662: A clash in test files goes to the planner, not the worker
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A clash with main inside a test file is resolved by the planner, so the worker's run no longer stalls.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/662#issuecomment-6173764311) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/389
> - https://github.com/dokima-dev/dokima/issues/384
> 
> 
> **User story:** When a pull request clashes with main inside a test file, the planner resolves it and the issue keeps moving.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a pull request clashes with main inside a test file, the

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_test_clash_planner.py; sed -n 130,215p .github/workflows/agent.yml; git show --stat HEAD | head
```

> """A clash inside a test file goes to the planner, not the worker (#662).
> 
> The worker may not change tests: the fence puts every test file back as the planner committed it. So when a pull
> request clashed with main inside a test file, the worker's resolution was dropped, its hand-back failed with "Conflict
> markers are still in ...", and the issue stalled until someone resolved the clash by hand (#610 on 2026-10-14).
> 
> These tests run the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin where
> main and try/issue-57 both changed tests/test_x.py after the branch split off, and, as on #610, also rules.md, a file
> that is not a test. First the planner's run: its checkout ("Starting branch"), a stand-in planner that keeps what it
> found and resolves tests/test_x.py when it holds conflict markers, and the push. Then the worker's run on a fresh
> clone: its checkout, a stand-in worker that resolves rules.md when it holds markers and touches no test, the fence and
> the push.
> 
> With tests=False the branch clashes with main only in rules.md, so no test file clashes.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> import test_start as ts  # noqa: E402
> 
> MARKERS = re.compile(r"(?m)^(<<<<<<<|=======|>>>>>>>)( |$)")
> BASE_TEST = 'def test_a():\n    """A."""\n    assert 1\n'
> BRANCHS_TEST = 'def test_a():\n    """A, as the branch has it."""\n    assert "branch"\n'
> MAINS_TEST = 'def test_a():\n    ""

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_test_clash_planner.py 2>&1 | grep -E "^E .*662|passed|failed|Error" | head -30
```

> assert m.planner == "success", f"662.1: the planner on a branch that clashes in a test file failed:\n{m.planner_log[-3000:]}"
> E       AssertionError: 662.1: the planner was not handed the clash in tests/test_x.py; it found no conflict markers holding both main's and the branch's side, but:
> tests/test_test_clash_planner.py:142: AssertionError
>         assert m.planner == "success", f"662.2: the planner's run failed:\n{m.planner_log[-3000:]}"
>         assert m.saw("worker") is not None, f"662.2: the worker's checkout failed at {m.failed_step!r}:\n{m.tail()}"
> E       AssertionError: 662.2: the worker was handed the clash inside tests/test_x.py: its clashed files are ['rules.md', 'tests/test_x.py']
> tests/test_test_clash_planner.py:163: AssertionError
>         assert m.planner == "success", f"662.3: the planner's run failed:\n{m.planner_log[-3000:]}"
>         assert m.worker == "success", f"662.3: the worker's run failed at {m.failed_step!r}:\n{m.tail()}"
> E       AssertionError: 662.3: the worker's hand-back was rejected on conflict markers:
> tests/test_test_clash_planner.py:185: AssertionError
> FAILED tests/test_test_clash_planner.py::test_the_planner_is_handed_a_clash_inside_a_test_file - AssertionError: 662.1: the planner was not handed the clash in tests/test_x.py; it found no conflict markers holding both main's and the branch's side, but:
> FAILED tests/test_test_clash_planner.py::test_the_worker_is_not_handed_a_clash_inside_a_test_file - AssertionError: 662.2: the worker was handed

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'));print(type(d), len(d))
for i in (d if isinstance(d,list) else d.values()):
  s=json.dumps(i)
  if '389' in s[:200] or '384' in s[:200]: print(s[:1500])
"; head -c 600 parent.json; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(d.keys())"
```

> <class 'list'> 127
> {"number": 389, "title": "A clash in a test file can never be resolved by the river", "summary": "Filed by Dokima from issues its agents raised during their runs and nobody filed.", "link": "https://github.com/dokima-dev/dokima/issues/389", "filed_by_dokima": true}
> {"number": 384, "title": "A plan can put files under tests/ in the worker's scope, which the fence always drops", "summary": "Filed by Dokima from issues its agents raised during their runs and nobody filed.", "link": "https://github.com/dokima-dev/dokima/issues/384", "filed_by_dokima": true}
> {"number": null}dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["Wrote three criteria and one test for each, run end to end on a test machine."],
  "decided": ["The planner gets the clash in test files; the worker keeps clashes outside tests."],
  "open": ["Asks whether the older open issue on test clashes closes when this lands.", "Asks whether the agent workflow file may change."]},
 "verdict": "approve",
 "summary": "The plan carries every ask, and each test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "When a pull request clashes with main inside a test file, the clash goes to the planner, which may edit tests", "source": "https://github.com/dokima-dev/dokima/issues/662", "criterion": "662.1"},
  {"ask": "not to the worker, which may not.", "source": "https://github.com/dokima-dev/dokima/issues/662", "criterion": "662.2"},
  {"ask": "its hand-back is rejected and the issue stalls until someone resolves the clash by hand.", "source": "https://github.com/dokima-dev/dokima/issues/662", "criterion": "662.3"}
 ],
 "behaviors": [
  {"criterion": "662.1", "one_behavior": true, "why": "The planner's checkout holds the test file's clash."},
  {"criterion": "662.2", "one_behavior": true, "why": "The worker starts from the resolved test, not the clash; one result said two ways."},
  {"criterion": "662.3", "one_behavior": true, "why": "The worker's hand-back is not rejected for conflict markers."}
 ],
 "edge_cases": [
  {"criterion": "662.1", "cut": [], "missing": []},
  {"criterion": "662.2", "cut": [], "missing": []},
  {"criterion": "662.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_test_clash_planner.py::test_the_planner_is_handed_a_clash_inside_a_test_file", "only_its_behavior": true, "why": "Runs the real planner checkout; needs markers with both sides, and none when tests did not clash."},
  {"test": "tests/test_test_clash_planner.py::test_the_worker_is_not_hand
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

**Agent:** Trimming one line that is over the word cap, then re-running the check.

`6. Bash`
```
sed -i 's/Wrote three criteria and one test for each, run end to end on a test machine./Wrote three criteria, each with one test run end to end./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 662 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#662](https://github.com/dokima-dev/dokima/issues/662) (test file clashes go to the planner), and `review.json` passes both code checks.

- **Your asks:** each of the three asks in the issue has its own criterion. Nothing is dropped or added.
- **The tests:** each one runs the real planner or worker steps on a test machine instead of reading the code. I ran all three. Each fails today because the feature is missing, not because of a crash:
  - 662.1: the planner's copy of the test file holds no clash markers.
  - 662.2: the worker's list of clashed files still names the test file.
  - 662.3: the worker's hand-back is rejected for clash markers.
- **Edge cases:** the tests also check the cases that must stay as they are. A clash only outside test files gives the planner nothing to fix, and a clash in the rules file still goes to the worker.

**Still waiting on you:** two questions from the planner, which I left for you. Your words in the issue don't settle either one.
- **P1:** should [#389](https://github.com/dokima-dev/dokima/issues/389) (a clash in a test file can never be resolved) close when this lands?
- **P2:** may the build change the agent workflow file? The rules forbid that unless the issue asks, and this issue doesn't name the file. A change to it stops for your approval anyway.

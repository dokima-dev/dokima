# reviewer (plan) for #595

Run: https://github.com/dokima-dev/dokima/actions/runs/38439937605

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #595: The worker cannot finish until its plan tests pass
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [597], "loop": []} -->
> The worker's end check runs the plan's tests, so red work never reaches review.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/597
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/341
> - https://github.com/dokima-dev/dokima/issues/596
> 
> 
> **User story:** The owner never gets work whose plan tests fail: the worker's own end check runs them first.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The worker's end check runs every test the approved plan lists for its criteria.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-595/tests/test_worker_plan_tests.py#L54"><img src="http

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_worker_plan_tests.py; cat /tmp/pack/parent.json | head -c 6000; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> """The worker's end check runs the plan's tests; a red one blocks it (#595).
> 
> The worker runs `python3 -m dokima.agent check work FILE PLAN N` itself before it stops, and agent.yml runs the same
> command again once the agent is done ("Code checks the hand-back"), both with ROLE=worker in the job's environment.
> Each test here runs that real command from outside, with ROLE=worker, from a temp folder that stands in for the
> worker's branch: it holds its own tests/ and the plan for issue 9 (criteria 9.1 to 9.3) lists tests there. Nothing of
> the repo's own suite is run by these checks, so they finish in seconds.
> 
> Outside a worker's run (ROLE unset, as tests/conftest.py makes it for every test) the check stays a shape check, so the
> older tests that check made-up plans keep passing.
> """
> import json
> import os
> import subprocess
> import sys
> 
> from dokima import agent
> from tests.test_handback_check import STORY, WORK
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> 
> # A test that notes its own name in the file named by $MARK, then passes or fails.
> PASSING = "import os\n\ndef {name}():\n    open(os.environ['MARK'], 'a').write('{name}\\n')\n\n"
> FAILING = "import os\n\ndef {name}():\n    open(os.environ['MARK'], 'a').write('{name}\\n')\n    assert False, 'red on purpose'\n\n"
> 
> 
> def branch(tmp_path, files, tests):
>     """A temp folder standing in for the worker's branch, with plan 9 and a hand-back.
> 
>     `files` maps a path under the folder to its test functions, each (nam

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_worker_plan_tests.py 2>&1 | tail -30; grep -n "def build_record\|def opening\|def next_step\|def render\|def check\b\|def check(\|def problems_work" dokima/agent.py
```

> def test_run_ending_red_hands_back_blocked(record_property, tmp_path):
>         """A worker still red at its run's end is recorded as blocked, naming the tests.
>     
>         Proves 595.3.
>         Runs the real end check on a branch where test_b fails, then builds the run's record from that check's output the
>         way agent.yml does (`agent record`, through build_record) and draws its comment. The comment's opening sentence
>         must say the worker is blocked, the comment must name the failing test, and the river must stop rather than start
>         the code review. A worker whose tests pass is not called blocked."""
>         record_property("proves", "595.3")
>         tests = {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_a"]}
>         root = branch(tmp_path, {"tests/test_x.py": [("test_a", True), ("test_b", False)]}, tests)
>         code, out, _ = run_check(root)
> >       assert code == 1, f"595.3: the end check passed a branch whose plan test fails (exit {code}):\n{out[-800:]}"
> E       AssertionError: 595.3: the end check passed a branch whose plan test fails (exit 0):
> E         
> E       assert 0 == 1
> 
> tests/test_worker_plan_tests.py:103: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_worker_plan_tests.py::test_end_check_runs_every_plan_test - AssertionError: 595.1: the worker's end check did not run the plan's tests ['test_a', 'test_b', 'test_c']; it r

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 403,470p dokima/agent.py; sed -n 690,770p dokima/agent.py
```

> def build_record(role, stage, out, check_text, passed, meta):
>     """This run's record: its hand-back, the code check's verdict and where it came from. Written by code, never the agent."""
>     hb = os.path.join(out, HANDBACK[role])
>     try:
>         handback = json.load(open(hb))
>     except (OSError, json.JSONDecodeError) as e:
>         handback = {"missing": f"{HANDBACK[role]}: {e}"}
>     rec = {"role": role, "stage": stage or None, **meta, "handback": handback,
>            "check": {"passed": passed, "problems": [l for l in check_text.splitlines() if l.strip()] if not passed else []}}
>     dropped = os.path.join(out, "dropped.txt")
>     if os.path.exists(dropped):
>         rec["dropped_by_fence"] = [l for l in open(dropped).read().splitlines() if l.strip()]
>     return rec
> 
> 
> def not_started(role, stage, why, meta):
>     """The record of a run or command that failed before its agent started: what it tried to start and why it could not."""
>     lines = [l.strip() for l in why.splitlines() if l.strip()] or ["A step before the agent failed; see the run for which."]
>     return {"role": "not-started", "attempt": role or "command", "stage": stage or None, **meta, "handback": {},
>             "check": {"passed": False, "problems": lines}}
> 
> 
> def cancelled(role, stage, started, meta):
>     """The record of a run someone cancelled: what it was and whether its agent had started. Nothing it handed back
>     is used, and the river starts nothing after it."""
>     return {"role": "cancelled", "attempt"

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^WORK\|^STORY" -A12 tests/test_handback_check.py | head -50; sed -n 1355,1400p dokima/agent.py; grep -n "blocked" dokima/agent.py | head -40
```

> 15:STORY = {"kind": "user_story", "user_story": "u",
> 16-         "acceptance_criteria": [{"text": "a", "source": "https://x/9"}, {"text": "b", "source": "https://x/9"}],
> 17-         "non_functional": [{"text": "c", "why": "w", "principle": "Fail closed"}],
> 18-         "scope": ["dokima/x.py"], "out_of_scope": [],
> 19-         "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_c"]}}
> 20-SPLIT = {"kind": "feature", "feature": "f", "stories": [
> 21-    {"title": "One", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
> 22-     "non_functional": [{"text": "n", "why": "w"}], "depends_on": []},
> 23-    {"title": "Two", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://x/9"}],
> 24-     "non_functional": [], "depends_on": [0]}]}
> 25-
> 26-# Every ask a plan review lists, matched to the story's 9.1 or a split's S1.1: a plan review must list them, a code
> 27-# review may, so the well-formed samples pass code's check on whatever stage the machine runs (#244).
> --
> 40:WORK = {"summary": "Cause and change.", "criteria": {"9.1": "x.py, a()", "9.2": "x.py, b()", "9.3": "x.py, c()"},
> 41-        "evidence": "pytest -q: 3 passed",
> 42-        "raises": [],
> 43-        "answers": [{"raise": "R1", "answer": "done", "why": "Added it."}]}
> 44-
> 45-
> 46-def on_stage(monkeypatch, stage):
> 47-    """Make this machine run on `stage`, the way the workflow sets STAGE for a reviewer: none, plan or pr

**Agent:** Tests all fail for the right reason. Now checking how agent.yml runs the worker's check, to judge whether the scope suffices.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "ROLE\|CHECK" .github/workflows/agent.yml | head -40; grep -n "def next_step" -A40 dokima/agent.py | grep -n "worker\|passed" | head
```

> 51:      ROLE: ${{ (inputs.role || github.event.client_payload.role) }}
> 111:          WHERE=$N; if [ -n "$PR" ] && { [ "$ROLE" = worker ] || [ "$STAGE" = pr ]; }; then WHERE=$PR; fi
> 112:          python3 -m dokima.agent card "$ROLE" "$STAGE" queued > /tmp/card.md
> 134:          python3 -m dokima.agent card "$ROLE" "$STAGE" setting-up > /tmp/card.md
> 146:            if [ "$ROLE" = worker ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" merge -q --no-edit origin/main; then
> 155:          elif [ "$ROLE" = planner ] || [ "$STAGE" = plan ]; then
> 160:            echo "::error title=Nothing to $ROLE::$(cat /tmp/why.txt)"; exit 1
> 167:          LOG="logs/$N/${{ github.run_id }}-$ROLE${STAGE:+-$STAGE}.md"
> 175:          python3 -m dokima.agent pack "$N" "$ROLE" "$STAGE" "$PACK" 2> /tmp/pack-err.txt || {
> 217:          python3 -m dokima.agent check-pack "$ROLE" "$STAGE" "$PACK" > /tmp/pack-check.txt \
> 236:          python3 -m dokima.agent card "$ROLE" "$STAGE" working > /tmp/card.md
> 247:          case "$ROLE$STAGE" in
> 248:            planner)      GRADE=plan-grade;   FILE=plan.json;   CHECK="python3 -m dokima.planner check $N $OUT" ;;
> 249:            reviewerplan) GRADE=plan-grade;   FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.json $N" ;;
> 250:            reviewerpr)   GRADE=result-grade; FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.jso

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "ROLE" tests/conftest.py; git show --stat HEAD | head
```

> 9:for k in ("STAGE", "ROLE", "N", "PACK", "OUT", "CARD_ID", "GITHUB_REPOSITORY", "PYTHONSAFEPATH"):
> commit 1e61b1d63f6a3d0266c92e1b9ea7157924c1cc39
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 17:35:36 2026 +0000
> 
>     planner for #595 (run 38439474744)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_worker_plan_tests.py | 117 ++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 117 insertions(+)

**Agent:** Plan looks sound. Writing the review.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria from story 1 of the parent plan, each with one test."],
  "decided": ["The worker's own check runs the plan's tests only during a worker's run.",
              "A worker still red at the end is shown as blocked and the review does not start."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan covers all three asks, and each test fails today because the check runs no tests.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Worker: its end-of-run check runs every acceptance test of the approved plan", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "595.1"},
  {"ask": "Any failure refuses the hand-back with the failing tests named, and the worker keeps working in the same run.", "source": "https://github.com/dokima-dev/dokima/issues/582", "criterion": "595.2"},
  {"ask": "A worker that cannot make them pass within its run hands back as blocked, naming the failing tests, never as done.", "source": "https://github.com/dokima-dev/dokima/issues/582", "criterion": "595.3"}],
 "behaviors": [
  {"criterion": "595.1", "one_behavior": true, "why": "One action: the check runs the plan's listed tests."},
  {"criterion": "595.2", "one_behavior": true, "why": "One result: a red test refuses the hand-back, named."},
  {"criterion": "595.3", "one_behavior": true, "why": "One result: a red end is a blocked record, never done."}],
 "edge_cases": [
  {"criterion": "595.1", "cut": [], "missing": []},
  {"criterion": "595.2", "cut": [], "missing": []},
  {"criterion": "595.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_worker_plan_tests.py::test_end_check_runs_every_plan_test", "only_its_behavior": true, "why": "Runs the real check; each test across two files must mark that it ran."},
  {"test": "tests/test_worker_plan_tests.py::test_failing_plan_test_refuses_hand_back_nami
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote three criteria from story 1 of the parent plan, each with one test./The planner wrote three criteria from the parent plan, each with one test./; s/A worker still red at the end is shown as blocked and the review does not start./A worker still red at the end is shown blocked; no review starts./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 595 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#595](https://github.com/dokima-dev/dokima/issues/595) (the worker can't finish until its plan tests pass). The hand-back is in `/tmp/dokima-out/review.json` and passes both required checks.

- **Asks:** the plan quotes three asks from the approved plan of the parent issue, [#582](https://github.com/dokima-dev/dokima/issues/582) (worker, review, merge gate and approval in one fixed order). Each has its own criterion:
  1. The worker's end check runs every test the plan lists.
  2. A failing or missing plan test refuses the worker's hand-back and names each one.
  3. A worker still failing when its run ends is shown as blocked, and no code review starts.
- **Tests:** all three new tests fail today for the right reason: the worker's end check runs no tests. Each test runs the real check command from outside, the way the worker's run does.
- **Scope:** changing `dokima/agent.py` alone is enough. The workflow already runs this check for the worker with the role set, so no workflow change is needed.
- **Raises:** none, and there were no open raises to answer.

One weak spot, not a blocker: the third test proves "blocked" mainly by finding that word in the record's first sentence. A failed worker run already stops the river today, so that part of the test passes either way. I let it through because that first sentence is what you see on the issue.

The asks are matched to the words quoted in the plan. I had no access to GitHub, so I couldn't read [#582](https://github.com/dokima-dev/dokima/issues/582) itself to look for other asks.

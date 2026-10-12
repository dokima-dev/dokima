# reviewer (plan) for #514

Run: https://github.com/dokima-dev/dokima/actions/runs/38199238136

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #514: A run that dies before posting its record leaves the issue looking busy forever
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A run that dies before posting its record no longer leaves its issue looking busy forever.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/514#issuecomment-6117064402) with `/plan`, or say `/review`
> 
> **User story:** When a run dies silently, the owner sees it failed, and autopilot can start that stage again.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A run that dies before posting its record gets a failed record linking the run.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-514/tests/test_unrecorded_run.py#L111"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A run that dies before posting its record gets a failed record linking t

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_unrecorded_run.py; python -m pytest -q tests/test_unrecorded_run.py 2>&1 | tail -40
```

> """A run that dies unrecorded still gets a record, and autopilot restarts its stage (#514).
> 
> #433's planner run died at 00:30 UTC: every step after the agent failed (the call counter fixed in #513 broke `gh`),
> so its live card kept saying "agent working since 00:21", the board showed nothing for the owner, and
> `/autopilot start` answered "already on autopilot, no stage started" because the live card read as a run going on.
> 
> The first two tests run every job of the agent workflow (.github/workflows/agent.yml) the way GitHub runs them, in the
> order their `needs` allow, on the machine from tests/test_start.py with the board fakes of
> tests/test_failed_run_card.py. In the broken run, every `gh` call made inside the `run` job after the agent started
> fails with exit 127, the way the broken counter failed them; jobs that run afterwards are on fresh machines, so their
> calls work. The good run is the same plan review with nothing broken.
> 
> The third test runs the command listener (.github/workflows/commands.yml) on `/autopilot start`, with the fake GitHub
> of tests/test_autopilot_close.py, which says a run is still going only when the test lists it as running.
> """
> import json
> import os
> import re
> 
> import pytest
> 
> import test_autopilot_close as tac
> import test_failed_run_card as frc
> import test_start as ts
> from dokima import agent
> from test_start import N, OWNER, Ctx, condition, evaluate
> 
> ISSUE = int(N)
> RUN_URL = "https://github.com/o/r/actions/runs/42"
> LABEL = "autopilot"
> 
> # Every gh call 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_unrecorded_run.py 2>&1 | grep -E "^(E  |FAILED|assert|AssertionError)" | head; python -m pytest -q tests/test_unrecorded_run.py -x 2>&1 | grep -B2 -A5 "514.1" | head -40
```

> E       AssertionError: 514.1: the run died before its record, and its live card still stands, never turned into a record:
> E         <!-- dokima-live -->
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/running.svg" width="16" height="16" align="absmiddle" alt="running"> <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/plan-review.svg" width="16" height="16" align="absmiddle" alt="plan review"> **Plan review** · agent working since 2026-10-12 03:19 UTC
> E         
> E         The agent is working; [watch it live](https://github.com/o/r/actions/runs/42) on GitHub. This card says checking when the agent ends, then becomes the run's record.
> E         
> E         --- last steps ---
> E         ## run: Decide what follows, merge on autopilot, and say it on the card (exit 0)
> E         stop
> E         
>         """A run that dies before posting its record gets a failed record linking the run.
>     
>         Proves 514.1.
>         Runs a plan review whose every GitHub call fails once the agent has started, so the run cannot post its record.
>         Afterwards no comment on the issue may still be a live card short of a record (it said "agent working"), and the
>         issue must hold a record, read by code as records are read, whose check failed and whose text links the run.
>         Beside it, the same plan review with nothing broken must leave exactly its own passing record and no other."""
>         record_property("proves", "514.1")
>         r = runs["

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^  [a-z_-]*:$\|needs:\|^    if:" .github/workflows/agent.yml | head -30; grep -n "autopilot" .github/workflows/commands.yml | head -20; grep -rn "No stage was started" dokima/ .github | head
```

> 4:# starts with /plan, /work or /review. Code gathers everything the agent needs: the issue and its PR as one
> 14:  repository_dispatch:
> 16:  workflow_call:
> 23:  workflow_dispatch:
> 46:  run:
> 9:# command first puts up one card for its run, which becomes that run's record. A code owner's `/autopilot start` or
> 10:# `/autopilot stop` starts no stage: it switches the issue's whole tree (or the tree of the issue a pull request was
> 11:# built for) on or off autopilot, the `autopilot` label, and says which issues it switched where it was written. On
> 12:# `/autopilot start`, an approved plan of that issue still waiting for `/work` starts the worker, and an approved split
> 35:      autopilot: ${{ steps.r.outputs.autopilot }}
> 170:  autopilot:
> 172:    if: needs.route.outputs.autopilot != ''
> 193:      - name: Switch the issue tree on or off autopilot, and say which issues, where it was written
> 196:          SWITCH: ${{ needs.route.outputs.autopilot }}
> 203:          python3 -m dokima.agent autopilot "$SWITCH" "$N" /tmp/pickup > /tmp/autopilot.md 2> /tmp/why.txt || { cat /tmp/why.txt >&2; exit 1; }
> 205:            gh pr comment "$NUMBER" -R "$GITHUB_REPOSITORY" --body-file /tmp/autopilot.md
> 207:            gh issue comment "$NUMBER" -R "$GITHUB_REPOSITORY" --body-file /tmp/autopilot.md
> 210:          [ -s /tmp/pickup/autopilot.md ] || exit 0
> 211:          gh issue comment "$N" -R "$GITHUB_REPOSITORY" --body-file /tmp/pickup/autopilot.md
> 235:    needs: [route, queue, split, autopilot]
> 236:    i

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat > /tmp/chk.py <<'EOF'
import sys; sys.path.insert(0,'tests')
import pytest
def test_x(runs):
    import test_unrecorded_run as t
    print("BROKEN", runs["broken"].results, runs["broken"].card())
    g=runs["good"]; print("GOOD", g.results, g.card(), [(x.get('role'),(x.get('check') or {}).get('passed')) for x in g.records()])
EOF
cp /tmp/chk.py tests/test_zz_tmp.py; sed -i '1i from test_unrecorded_run import runs' tests/test_zz_tmp.py; python -m pytest -q -s tests/test_zz_tmp.py 2>&1 | grep -E "BROKEN|GOOD|passed|failed"; rm tests/test_zz_tmp.py; git status --short
```

> BROKEN {'run': 'failure'} None
> GOOD {'run': 'success'} ('Plan', False) [('reviewer', True)]
> 1 passed in 2.51s

**Agent:** Plan's three tests fail today for the right reason and their good-case halves pass; writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria, each with one test that runs the real workflows."],
  "decided": ["A dead run's stage starts again on autopilot start, not the stage after it.",
              "Dead runs found by the fifteen minute sweep are left out."],
  "open": ["Two questions for the owner: which stage restarts, and whether the new failed record also restarts."]},
 "verdict": "approve",
 "summary": "The plan covers both asks with tests that fail today for the right reason; two questions wait for you.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.1"},
  {"ask": "A run that ends without posting its record gets a failed record and Needs you, with a link to the run.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.2"},
  {"ask": "`/autopilot start` on an issue whose last run is finished but unrecorded starts the next stage instead of saying nothing started.", "source": "https://github.com/dokima-dev/dokima/issues/514", "criterion": "514.3"}
 ],
 "behaviors": [
  {"criterion": "514.1", "one_behavior": true, "why": "One result: a failed record that links the run."},
  {"criterion": "514.2", "one_behavior": true, "why": "One result: the card shows Needs you."},
  {"criterion": "514.3", "one_behavior": true, "why": "One action, one result: autopilot start restarts the dead run's stage."}
 ],
 "tests": [
  {"test": "tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_gets_a_failed_record_linking_the_run", "only_its_behavior": true, "why": "Fails today: the live card stays; the good run keeps one passing record."},
  {"test": "tests/test_unrecorded_run.py::test_a_run_that_dies_before_its_record_shows_needs_you", "only_its_behavior": true
```

> Exit code 1
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Two questions for the owner: which stage restarts, and whether the new failed record also restarts./Two questions for the owner: which stage restarts, and whether a failed record restarts too./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 514 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> 0

**Agent:** I approved the plan for [#514](https://github.com/dokima-dev/dokima/issues/514) (a run that dies before posting its record leaves the issue looking busy). It still stops for you: the planner's two questions are yours to answer. The review is at `/tmp/dokima-out/review.json` and passes both hand-back checks.

**What the plan covers:**
- **514.1:** a run that dies before posting its record gets a failed record that links the run.
- **514.2:** that issue's card shows Needs you.
- **514.3:** `/autopilot start` on an issue whose last run ended with no record starts that run's stage again.

Each criterion is one behavior, and together they cover both "Done when" lines of your issue.

**The tests:**
- All three fail today for the right reason:
  - **514.1:** the live card still says "agent working".
  - **514.2:** the board is never touched.
  - **514.3:** autopilot start answers "No stage was started".
- The test for 514.1 or 514.2 also has a normal run with nothing broken. That run already gives the right result today: one passing record, and the card in Plan with no Needs you.
- The test for 514.3 also checks a run that is still going. `/autopilot start` must start nothing there, so code that always restarts fails.

**Your two questions:** I didn't answer either for you, because your issue's words don't settle them.
- **Which stage restarts?** Your issue says `/autopilot start` "starts the next stage". The plan reads that as the stage whose run died, so a dead planner starts the planner again. That matches what you did by hand on [#433](https://github.com/dokima-dev/dokima/issues/433) (the planner run that died).
- **Should autopilot start also restart once the failed record exists?** The plan says no and leaves that out of scope. Once 514.1 lands, almost every dead run will have a record, so `/autopilot start` would only restart runs where even posting the failed record failed. If you want it to restart after a failed record too, say so.

**One more thing:** the fix needs a new job in `.github/workflows/agent.yml`, because the run that died can't post its own record. This repo's rules say workflow files change only when an issue asks, and yours doesn't say so outright. Your ask can't be built without that change, so I didn't block on it. Any pull request that touches a workflow file stops for your approval before merging.

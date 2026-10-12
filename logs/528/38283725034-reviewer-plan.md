# reviewer (plan) for #528

Run: https://github.com/dokima-dev/dokima/actions/runs/38283725034

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #528: Autopilot refuses to merge a green pull request because superseded card redraws were cancelled
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> **Backlog**
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> Autopilot refuses to merge a green pull request because some card redraws on it were cancelled.
> 
> On #525 (for #523) every required check and all three acceptance checks passed, but autopilot stopped for the owner: "not every check passed on its head commit 9525f80: card (cancelled), card (cancelled), card (cancelled), card (cancelled)". Those card runs were cancelled by GitHub's concurrency queue because a newer redraw replaced them (#491); they judge nothing.
> 
> Done when
> - A card run cancelled on a pull request's head does not keep autopilot from merging it when every other check passed.
> - A check that failed, or one still running, still stops autopilot as today.
> 
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_autopilot_checks.py; git show HEAD -- tests/test_automerge.py
```

> commit c05c2db2a4639c11dcb979174350449c7e9122e0
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 17:21:48 2026 +0000
> 
>     planner for #528 (run 38283326405)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_automerge.py        |   8 +--
>  tests/test_autopilot_checks.py | 156 +++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 160 insertions(+), 4 deletions(-)
> """Autopilot ignores cancelled card runs and waits for checks still running (#528).
> 
> On #525 autopilot refused a green pull request because card redraws on its head were cancelled: GitHub's queue
> cancels a redraw a newer one replaces, and a card run judges nothing. On #530 it stopped for the owner while All tests
> was still running, minutes before it passed. These tests call autopilot's merge (`dokima.agent.automerge`) against a
> fake GitHub kept in memory: pull request #60 built for issue #57, its head commit, the check runs and commit statuses
> on that head, and merging. Each read of the head's check runs moves the fake on one step through the list of
> check-run states the test gives, the last state staying for good, so a check can be still running and then finish.
> Time is faked too: `time.sleep` only moves a fake clock that `time.time` and `time.monotonic` read, so waiting costs
> no real time.
> """
> import json
> import time
> 
> import pytest
> 
> from dokima import agent
> 
> REPO = "o/r"
> ISSUE = 57
> PR = 60
> HEAD = "a1

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_autopilot_checks.py tests/test_automerge.py -x -k "autopilot_checks or every_check" 2>&1 | tail -30; grep -n "def automerge\|def _checks\|still running\|not every check" dokima/agent.py | head -30
```

> record_property = <function record_property.<locals>.append_property at 0x7f42c39b6200>
> github = <function github.<locals>.make at 0x7f42c39b63e0>
> 
>     def test_cancelled_card_runs_no_longer_keep_autopilot_from_merging_a_green_pull_request(record_property, github):
>         """A pull request with cancelled card runs merges when every other check passed.
>     
>         Proves 528.1.
>         The head carries four cancelled card runs beside green All tests, criterion and plan checks, as on #525: autopilot
>         must merge it at that head and say it merged. Beside it, the same head with All tests cancelled instead must not
>         merge, so autopilot leaves out only the card runs, not every cancelled check."""
>         record_property("proves", "528.1")
>         fake = github([GREEN + CANCELLED_CARDS])
>         how, why, merges = merge(fake)
> >       assert how == "merged" and len(merges) == 1, \
>             (f"528.1: autopilot did not merge #60, whose only checks that did not pass are cancelled card runs: "
>              f"how={how!r}, why={why!r}, merges asked={merges}")
> E       AssertionError: 528.1: autopilot did not merge #60, whose only checks that did not pass are cancelled card runs: how='', why='not every check passed on its head commit a1a1a1a: card (cancelled), card (cancelled), card (cancelled), card (cancelled)', merges asked=[]
> E       assert ('' == 'merged'
> E         
> E         - merged)
> 
> tests/test_autopilot_checks.py:106: AssertionError
> =========================== shor

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_autopilot_checks.py tests/test_automerge.py 2>&1 | tail -8; sed -n 2095,2290p dokima/agent.py
```

> 'running' is contained here:
>     a check is still running on its head commit a1a1a1a: all tests
>   ?                  +++++++)
> FAILED tests/test_autopilot_checks.py::test_a_check_still_running_makes_autopilot_wait_and_merge_once_it_passes - AssertionError: 528.3: autopilot did not wait for All tests to finish and then merge #60; it stopped with how='', why='a check is still running on its head commit a1a1a1a: all tests', after reading the checks 1 time(s)
> assert ('' == 'merged'
>   
>   - merged)
> 3 failed, 8 passed in 53.70s
> WORKFLOWS = ".github/workflows/"
> PASSING = {"success", "neutral", "skipped"}
> 
> 
> def approves_work(rec):
>     """True when a passed code review approves the pull request, raising nothing for the owner."""
>     return (rec.get("role") == "reviewer" and (rec.get("stage") or "") == "pr" and bool(rec.get("check", {}).get("passed"))
>             and (rec.get("handback") or {}).get("verdict") == "approve" and not owner_raises(rec.get("handback") or {}))
> 
> 
> def work_approved(recs):
>     """True when the issue's newest planner, worker or reviewer record is a code review approving the pull request."""
>     at = next((i for i in range(len(recs) - 1, -1, -1) if recs[i].get("role") in HANDBACK), None)
>     # A review that settled a worker's raise sends the work on to an agent, so it merges nothing.
>     return at is not None and approves_work(recs[at]) and not settled(recs[:at], recs[at].get("handback") or {})
> 
> 
> def pages(text):
>     """Every JSON page `gh api --paginate` printed ba

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "PENDING\|still running\|in_progress" tests/*.py | grep -v test_autopilot_checks | head -30; grep -n "unproven(\|try_merge(\|automerge(" dokima/*.py
```

> tests/test_autopilot_close.py:23:  - `gh api repos/o/r/actions/runs/ID` says whether run ID is still going (in_progress) or completed.
> tests/test_autopilot_close.py:130:    jq({"id": int(m_run.group(1)), "status": "in_progress" if m_run.group(1) in opts.get("running_runs", []) else "completed"})
> tests/test_card_criterion_label.py:114:    run("40.1 · First thing works", "in_progress", None, n=1),
> tests/test_board_state.py:317:# Newest first: this sweep (still running), a sweep that failed, an event's run, the last sweep that succeeded, an older one.
> tests/test_board_state.py:318:BOARD_RUNS = [run(5, "schedule", "in_progress", None, "2026-10-09T15:45:00Z"),
> tests/test_card_bullets.py:209:    (run("40.1 · First thing works", "in_progress", None, n=1), "running"),
> tests/test_card_every_change.py:60:    """A workflow_run event: `workflow` on PR p started (in_progress) or was requested."""
> tests/test_card_every_change.py:63:    event["workflow_run"].update(status="in_progress" if state == "in_progress" else "queued", conclusion=None)
> tests/test_card_every_change.py:99:        "the Acceptance criteria run starts": run_started(n, p, "Acceptance criteria", "in_progress"),
> tests/test_card_every_change.py:101:        "the full suite starts": run_started(n, p, "full suite", "in_progress"),
> tests/test_card.py:35:BUILDING = {"status": "in_progress", "conclusion": None, "html_url": "https://github.com/o/r/actions/runs/1"}
> tests/test_card.py:94:    body = render(checks=GREEN + [run("card", s

**Agent:** Tests fail today for the right reasons. Writing the plan review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote three criteria and one test for each.", "The planner dropped the running-check case from an older merge test."],
  "decided": ["A check still running is waited for, then judged when it finishes.", "Only cancelled card runs are left out; other cancelled checks still stop autopilot."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan covers every ask, and each test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A card run cancelled on a pull request's head does not keep autopilot from merging it when every other check passed.", "source": "https://github.com/dokima-dev/dokima/issues/528", "criterion": "528.1"},
  {"ask": "A check that failed, or one still running, still stops autopilot as today.", "source": "https://github.com/dokima-dev/dokima/issues/528", "criterion": "528.2"},
  {"ask": "a check still running makes autopilot wait for it and decide when it finishes, not stop for the owner.", "source": "https://github.com/dokima-dev/dokima/issues/528#issuecomment-6128789765", "criterion": "528.3"}
 ],
 "behaviors": [
  {"criterion": "528.1", "one_behavior": true, "why": "Cancelled card runs no longer block a merge."},
  {"criterion": "528.2", "one_behavior": true, "why": "A failed check stops autopilot and is named."},
  {"criterion": "528.3", "one_behavior": true, "why": "A running check is waited for, then the merge goes ahead."}
 ],
 "tests": [
  {"test": "tests/test_autopilot_checks.py::test_cancelled_card_runs_no_longer_keep_autopilot_from_merging_a_green_pull_request", "only_its_behavior": true, "why": "Merges with cancelled card runs; still refuses a cancelled All tests."},
  {"test": "tests/test_autopilot_checks.py::test_a_failed_check_still_stops_autopilot_and_names_it", "only_its_behavior": true, "why": "Failed run, failed status, and a check failing after a wait each stop, named."},

```

> (Bash completed with no output)

**Agent:** I approved the plan for [#528](https://github.com/dokima-dev/dokima/issues/528) (autopilot refuses green pull requests over cancelled card redraws). Both hand-back checks passed with nothing to fix.

- **Asks:** each of the owner's three asks has its own criterion:
  - Cancelled card runs no longer stop a merge.
  - A failed check still stops autopilot, and the reason names it.
  - A check still running is waited for, then judged when it finishes.
- **Tests fail today for the right reason:** I ran all three new tests and each fails because the feature is missing:
  - The cancelled card runs block the merge.
  - Autopilot stops with "still running" instead of waiting.

  The older merge tests still pass with the running-check case removed.
- **Good case beside each bad case:** the cancelled-card test also checks that a cancelled All tests run still blocks the merge. So the worker can't pass it by ignoring every cancelled check.
- **Size:** each criterion is one behavior, so size is ok.

The failed-check test also covers a check that fails after autopilot waits for it. That belongs to the owner's "decide when it finishes", which is fine under the failed-check criterion. I raised nothing.

# reviewer (plan) for #537

Run: https://github.com/dokima-dev/dokima/actions/runs/38296622022

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
> # Issue #537: Plan reviews judge each criterion's edge cases
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 536, 538 -->
> <!-- dokima-blocking: {"blocked_by": [536], "blocks": [], "loop": []} -->
> Plan reviews judge each criterion's edge cases, and code rejects a review that skips one.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/536
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/531
> - https://github.com/dokima-dev/dokima/issues/538
> - https://github.com/dokima-dev/dokima/issues/551
> 
> 
> **User story:** Every plan review names, per criterion, the exotic edge cases it cuts and the normal-use ones missing.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The reviewer's prompt gives error, timeout, bad data and empty as guiding kinds with e

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {"number": 531}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38294602244",
>  "commit_before": "5290204bd12936b756b0103e2208349eea97a2af",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1017516,
>   "turns": 24,
>   "cost_usd": 1.1458437999999997,
>   "tokens_in": 1485447,
>   "tokens_out": 14723
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/537/38294602244-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38294602244",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/537#issuecomment-6130691191"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_review_edge_cases.py; git show HEAD -- tests/test_handback_check.py
```

> commit 398e23298c6f98c0edfcd4b2ce9b25ffbbc7d5ea
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 19:16:50 2026 +0000
> 
>     planner for #537 (run 38294602244)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_autopilot_river.py   |   2 +-
>  tests/test_failed_run_card.py   |   2 +-
>  tests/test_fixer.py             |   2 +-
>  tests/test_handback_check.py    |   4 +-
>  tests/test_live_queue.py        |   2 +-
>  tests/test_review_asks.py       |   2 +-
>  tests/test_review_edge_cases.py | 104 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_start.py             |   2 +-
>  8 files changed, 112 insertions(+), 8 deletions(-)
> """Every plan review judges each criterion's edge cases: exotic ones cut, normal-use ones missing.
> 
> Covers #537, story 2 of #531. The reviewer's prompt teaches the same guiding kinds as the planner's (error, timeout,
> bad data, empty), with examples, saying other kinds count too. A plan review hands back `edge_cases` in review.json:
> one row per criterion of the plan, {"criterion": "N.k", "cut": [...], "missing": [...]}, each list holding plain
> lines (empty when there are none). Code rejects a plan review that skips a criterion, naming it.
> 
> Every check runs the real commands the workflow runs on a review, through tests/test_review_asks.py's helpers, on a
> plan for issue 9 with criteria 9.1 to 9.3, or a two-story split with S1.1 and S2.1.
> """
> import os
> import

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_autopilot_river.py tests/test_failed_run_card.py tests/test_fixer.py tests/test_live_queue.py tests/test_review_asks.py tests/test_start.py
```

> commit 398e23298c6f98c0edfcd4b2ce9b25ffbbc7d5ea
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 19:16:50 2026 +0000
> 
>     planner for #537 (run 38294602244)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_autopilot_river.py b/tests/test_autopilot_river.py
> index dceec03..324162f 100644
> --- a/tests/test_autopilot_river.py
> +++ b/tests/test_autopilot_river.py
> @@ -37,7 +37,7 @@ QUESTIONS = [{"question": "Should a failed run move its card to Needs you?",
>  STORY_Q = {**ts.STORY, "questions": QUESTIONS}
>  APPROVE = {**ts.APPROVE, "previous_step": {"did": ["Planned one story."], "decided": [], "open": []},
>             "summary": "Every ask has a criterion and every criterion a test that breaks on any deviation.",
> -           "asks": [{"ask": "Fix it.", "source": ISSUE, "criterion": "57.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")]}
> +           "asks": [{"ask": "Fix it.", "source": ISSUE, "criterion": "57.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/te

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_review_edge_cases.py 2>&1 | grep -E "Error|assert|passed|failed" | head -30; python3 -m pytest -q -x tests/test_handback_check.py tests/test_review_asks.py tests/test_start.py tests/test_fixer.py tests/test_autopilot_river.py tests/test_live_queue.py tests/test_failed_run_card.py 2>&1 | tail -3
```

> >       assert body is not None, "537.1: the reviewer's prompt has no Edge cases section"
> E       AssertionError: 537.1: the reviewer's prompt has no Edge cases section
> E       assert None is not None
> tests/test_review_edge_cases.py:42: AssertionError
> >       assert re.search(r'"edge_cases"\s*:\s*\[\s*\{\s*"criterion"\s*:[^}]*"cut"\s*:\s*\[[^}]*"missing"\s*:\s*\[', shape), \
> E       AssertionError: 537.2: the review.json shape in reviewer.md has no edge_cases list of {"criterion": "N.k", "cut": [...], "missing": [...]}
> E       assert None
> tests/test_review_edge_cases.py:62: AssertionError
>         ra.assert_passes(tmp_path, {**ra.APPROVE, "edge_cases": rows(STORY_IDS)}, "537.3",
> >       ra.assert_rejected(tmp_path, {**ra.APPROVE, "edge_cases": rows(("9.1", "9.3"))}, r"edge_cases.*9\.2|9\.2.*edge_cases",
>     def assert_rejected(tmp_path, review, pattern, crit, why, **kw):
>         assert "Traceback" not in err and "Traceback" not in out, f"{crit}: the review check crashed on {why}:\n{err[-600:]}"
> >       assert code == 1, f"{crit}: {why} was let through (exit {code}); it must be rejected"
> E       AssertionError: 537.3: a plan review that skips 9.2's edge cases was let through (exit 0); it must be rejected
> E       assert 0 == 1
> tests/test_review_asks.py:101: AssertionError
> FAILED tests/test_review_edge_cases.py::test_the_reviewers_prompt_gives_the_guiding_kinds_with_examples_and_says_other_kinds_count - AssertionError: 537.1: the reviewer's prompt has no Edge cases section
> assert

**Agent:** I'm reviewing the plan for #537: the new tests fail today for the right reasons. Next I'm checking the owner's words in #531.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show 5290204 --stat | head -20; grep -rn "guide lines\|exotic\|bad data" dokima/ tests/*.py | head -20; sed -n 125,145p dokima/roles/reviewer.md
```

> commit 5290204bd12936b756b0103e2208349eea97a2af
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:53:22 2026 +0000
> 
>     Plans list each criterion's edge cases (#550)
>     
>     * planner for #536 (run 38287243382)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * worker for #536 (run 38291496178)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     ---------
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  dokima/planner.py                  |  24 ++++++
> tests/test_edge_cases.py:6:guiding kinds (error, timeout, bad data, empty) with examples, saying other kinds count too.
> tests/test_review_edge_cases.py:1:"""Every plan review judges each criterion's edge cases: exotic ones cut, normal-use ones missing.
> tests/test_review_edge_cases.py:4:bad data, empty), with examples, saying other kinds count too. A plan review hands back `edge_cases` in review.json:
> tests/test_review_edge_cases.py:52:def test_a_plan_review_lists_the_exotic_cases_it_cuts_and_the_normal_use_cases_missing(record_property, tmp_path):
> tests/test_review_edge_cases.py:53:    """Each plan review lists, per criterion, the exotic edge cases cut and normal-use ones missing.
> is for the plan only, and is never empty. 

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,20p tests/test_edge_cases.py; grep -n -A12 "^#* Edge cases" dokima/roles/*.md; grep -n "def problems_review\|def problems_size\|behaviors" dokima/agent.py | head
```

> """Every plan lists each criterion's edge cases with their tests, or why there are none.
> 
> Covers #536, story 1 of #531. The planner's hand-back gives each criterion either `edge_cases`, a list of
> {"case": ..., "test": "path::name"} where the test is one the plan files under that criterion, or `no_edge_cases`, the
> reason it has none. The plan check rejects a criterion with neither, naming it, and the planner's prompt teaches the
> guiding kinds (error, timeout, bad data, empty) with examples, saying other kinds count too.
> """
> import copy
> import json
> import os
> import re
> import sys
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from dokima import planner  # noqa: E402
> 
> ROOT = os.path.join(os.path.dirname(__file__), "..")
> PROMPT = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
> dokima/roles/planner.md:66:## Edge cases
> dokima/roles/planner.md-67-Every criterion lists its edge cases in `edge_cases`, each the case in plain words and the one test, filed under that
> dokima/roles/planner.md-68-criterion, that covers it. A criterion with none says why in `no_edge_cases` instead. Code rejects a criterion with
> dokima/roles/planner.md-69-neither, naming it. Kinds to look for:
> dokima/roles/planner.md-70-- **Error:** what the owner sees when a call fails. Example: GitHub answers 500 while the card is redrawn.
> dokima/roles/planner.md-71-- **Timeout:** a call that never answers. Example: the agent's run passes its time limit.
> dokima/roles/planne

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -ln '"behaviors"' tests/*.py | xargs grep -L edge_cases; grep -rn '"behaviors"' dokima/*.py | grep -v "^dokima/agent.py" | head
```

> tests/test_size_rule.py

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n 'behaviors\|stage\|def test\|check review\|run_check' tests/test_size_rule.py | head -40
```

> 19:def test_the_right_number_of_stories_passes(sizes):
> 25:def test_too_big_too_small_or_too_many_is_refused(sizes):
> 31:def test_more_than_three_questions_stops_even_on_autopilot():
> 39:def test_a_plan_review_needs_a_size_verdict_and_never_approves_a_broken_size():
> 42:    assert agent.problems_size({"verdict": "approve", "size": "story 1 bundles two behaviors"})
> 44:    assert not agent.problems_size({"verdict": "block", "size": "story 1 bundles two behaviors"})
> 47:def test_every_criterion_is_judged_one_behavior_and_a_bundle_breaks_size():
> 50:          "behaviors": [{"criterion": "7.1", "one_behavior": True, "why": "one result"}]}
> 52:    assert agent.problems_size(dict(ok, behaviors=[]), ["7.1"])
> 53:    bundled = dict(ok, behaviors=[{"criterion": "7.1", "one_behavior": False, "why": "X and Y"}])
> 57:def test_every_test_is_judged_and_a_test_checking_more_never_approves():
> 68:def test_a_story_of_a_parent_never_splits_again():

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned three criteria, each with one new test.",
          "Added an edge case judgment to every sample plan review in older tests."],
  "decided": ["A plan review hands back, per criterion, the cases it cuts and the ones missing.",
              "A code review needs no edge case judgments."],
  "open": []},
 "verdict": "approve",
 "summary": "Every ask has one criterion, and each new test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "error, timeout, bad data, empty use these as guide lines with examples for planner and reviewer prompts but don't limit to those categories", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "537.1"},
  {"ask": "The reviewer judges each criterion's list in its hand-back: exotic cases nobody would hit are cut, and missing normal-use cases are named", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "537.2"},
  {"ask": "code rejects a review that skips a criterion", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "537.3"}
 ],
 "behaviors": [
  {"criterion": "537.1", "one_behavior": true, "why": "One prompt section with four guiding kinds."},
  {"criterion": "537.2", "one_behavior": true, "why": "One judgment row per criterion in the review."},
  {"criterion": "537.3", "one_behavior": true, "why": "One rejection naming the skipped criterion."}
 ],
 "tests": [
  {"test": "tests/test_review_edge_cases.py::test_the_reviewers_prompt_gives_the_guiding_kinds_with_examples_and_says_other_kinds_count", "only_its_behavior": true, "why": "Fails today: the reviewer prompt has no Edge cases section."},
  {"test": "tests/test_review_edge_cases.py::test_a_plan_review_lists_the_exotic_cases_it_cuts_and_the_normal_use_cases_missing", "only_its_behavior": true, "why": "Checks the shape is taught, good rows pass, malformed rows are
```

> (Bash completed with no output)

**Agent:** I approved the plan for #537 (plan reviews judge each criterion's edge cases), with no blockers. The hand-back is in `/tmp/dokima-out/review.json`, and both hand-back checks pass on it.

- **Criteria:** the plan has three, one for each of the owner's asks from #531.
  - The reviewer's prompt teaches the four guiding edge case kinds (error, timeout, bad data, empty) with examples, and says other kinds count too.
  - Each plan review lists, for every criterion, the unlikely edge cases it cuts and the normal-use ones that are missing.
  - Code rejects a plan review that skips a criterion, naming that criterion.
- **New tests:** all three fail today because the feature is missing, not because of a crash or a bad path.
  - The reviewer's prompt has no Edge cases section yet.
  - The prompt doesn't show reviewers how to hand back their edge case judgments.
  - A review that skips criterion 9.2 is let through instead of rejected.
- **Weak tests:** none. Each "rejects the bad case" check has a "passes the good case" check beside it, so a version that rejects everything still fails.
- **Older tests:** the planner added an empty edge case judgment to the sample plan reviews in seven older test files. Those 40 tests still pass. Only one of those changes is listed in the plan's test changes, but they only add data and no assertions change, so I didn't block on it.
- **Protected prompts:** the plan edits two files under `dokima/roles/`, which AGENTS.md protects unless the issue asks. I counted it as asked, since the issue names the reviewer's prompt and its first criterion is about that prompt.

I couldn't open #531 because this run has no GitHub access. The owner's words in the asks list come from the planner's quotes and the story text copied into #537, not from #531 itself.

# reviewer (plan) for #859

Run: https://github.com/dokima-dev/dokima/actions/runs/39103345844

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

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
> # Issue #859: The card follows the repo's own CI
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The card redraws when the repo's own CI finishes, and shows every check the merge needs.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/785
> - https://github.com/dokima-dev/dokima/issues/771
> - https://github.com/dokima-dev/dokima/issues/292
> 
> 
> **User story:** The owner sees the repo's own checks on the card, current as soon as their CI finishes.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the repo's own CI finishes on a pull request, its issue's card redraws.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-859/tests/test_card_repo_ci.py#L141"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icon

`2. Bash`
```
cd /tmp/pack; cat in/02-reviewer-plan.json | head -c 6000; echo; cat owner_words.json | head -c 3000; cd /home/runner/work/dokima/dokima; git diff f893d73 30e790c --stat; cat tests/test_card_repo_ci.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39103111824",
>  "commit_before": "f893d73f3ce3fe93e58361989a098edfec789f47",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 57372,
>   "turns": 8,
>   "cost_usd": 0.4358818,
>   "tokens_in": 323695,
>   "tokens_out": 4284
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/859/39103111824-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39103111824",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote two criteria: redraw on the repo's CI, show required checks.",
>     "The planner wrote six tests against a fake GitHub."
>    ],
>    "decided": [
>     "A required check that has not run shows as not started.",
>     "A check reported as a commit status counts like a check run."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "The redraw test only plays a CI named ci, so listening for that one name would pass it.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "859.1 weak test",
>     "text": "The 859.1 tests play only a CI named `ci`, so listening for that name passes. Fix: also play a CI with an unguessable name.",
>     "evidence": "`tests/test_card_repo_ci.py` line 30 sets `CI = \"ci\"`; `thin_starts` checks only that name against `dokima/install/dokima.yml` line 12.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    }
>   ],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "The card redraws o

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_card_repo_ci.py 2>&1 | grep -E "^E .*859|passed|failed" | head -20
```

> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('ci') finishes, so its card is never redrawn
>         """A failed run of the repo's own CI redraws the card too.
> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('Quality gate 7f3a9 (nightly)') finishes, so its card is never redrawn
> _____________ test_a_required_repo_check_that_failed_shows_failed ______________
>     def test_a_required_repo_check_that_failed_shows_failed(tmp_path, record_property):
>         """A required check of the repo's own that failed shows as failed.
>         Main's rule requires the repo's own `lint` besides Dokima's checks; `lint` failed on the pull request's head,
>         so the card must show `lint` with the failed circle. Proves 859.2."""
> >       assert got == "failed", \
>             f"859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as {got}:\n{card[-2500:]}"
> E       AssertionError: 859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as None:
> E         - <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> **<a href="https://github.com/o/r/runs/2601">Acceptance criterion</a>:** Criterion one of #246.
> E         **Definition of Done:** <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddl

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made both redraw tests also play a CI with an unguessable name."], "decided": ["A failed run of the repo's CI is played with the unguessable name."], "open": []},
 "verdict": "approve",
 "summary": "The plan now proves the card redraws for any CI name, and shows every required check.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The card redraws only when Dokima's own workflows finish, not when the adopter's CI does.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "859.1"},
  {"ask": "The merge gate already waits on every required check; the card must show them.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "859.2"}
 ],
 "behaviors": [
  {"criterion": "859.1", "one_behavior": true, "why": "One event, the repo's CI finishing; one result, the card redraws."},
  {"criterion": "859.2", "one_behavior": true, "why": "One result: each required check shows on the card with its state."}
 ],
 "edge_cases": [
  {"criterion": "859.1", "cut": [], "missing": []},
  {"criterion": "859.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_card_repo_ci.py::test_the_repos_own_ci_finishing_redraws_the_card", "only_its_behavior": true, "why": "Checks the redraw for a common and an unguessable CI name."},
  {"test": "tests/test_card_repo_ci.py::test_the_repos_own_ci_failing_redraws_the_card", "only_its_behavior": true, "why": "Checks the redraw after a failed run of an unguessable CI."},
  {"test": "tests/test_card_repo_ci.py::test_a_required_repo_check_that_failed_shows_failed", "only_its_behavior": true, "why": "Checks one required check shows as failed."},
  {"test": "tests/test_card_repo_ci.py::test_a_required_repo_check_that_passed_shows_passed", "only_its_behavior": true, "why": "Checks one required check shows as passed."},
  {"test": "tests/test_card_repo_ci.py::test_a_required_check_not_yet_
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#859](https://github.com/dokima-dev/dokima/issues/859) (the card follows the repo's own CI), and it passed both checks.

- **Last round's blocker is fixed.** Both redraw tests now also use a CI with a made-up name, `Quality gate 7f3a9 (nightly)`. Code that only listens for a CI named `ci` would now fail them.
- **All six new tests fail today, for the right reason.** I ran them. The redraw tests fail because the repo's workflow doesn't start when the repo's own CI finishes. The check tests fail because the card doesn't list required checks like `lint` at all.
- **Nothing the owner asked for is missing.** Both asks from [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety for human pull requests) have a criterion: the card redraws when the repo's own CI finishes, and it shows every check the merge needs.

Each criterion is one behavior, no extra edge cases are needed, and there were no open questions to answer. The review is in `/tmp/dokima-out/review.json`.

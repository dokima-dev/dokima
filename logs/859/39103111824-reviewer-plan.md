# reviewer (plan) for #859

Run: https://github.com/dokima-dev/dokima/actions/runs/39103111824

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
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-859/tests/test_card_repo_ci.py#L140"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="

`2. Bash`
```
cd /tmp/pack; cat owner_words.json; head -c 3000 parent.json; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"; cat /home/runner/work/dokima/dokima/tests/test_card_repo_ci.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/744": "Phase 3 of #272 (trial blockers). Things that would bite an adopter on day one.\n\n**What**\n- The required \"Acceptance criteria\" check fails every PR without an approved Dokima plan, including human and Dependabot PRs. Setting `merge.unplanned_prs: allow` (default) lets them through; only Dokima's own PRs are held to the plan.\n- The daily audit (`audit.py:99`) reports any extra required check on the branch rule as drift, so an adopter's own CI reads as a problem. Checks the repo added are not drift.\n- The audit fails when no board is set; boards are optional and only exist for organizations. No board means nothing to report.\n- The card redraws only when Dokima's own workflows finish, not when the adopter's CI does. The merge gate already waits on every required check; the card must show them.\n- Nothing installs the target repo's own dependencies; only pytest is installed (`full-suite.yml:27`, `agent.yml:262`). The `tests.install` setting runs first.\n- `tests.exclude` keeps tests the repo marks (for example live network tests) off the merge gate. Owner note: #341 said everything runs at the gate; this is the repo's own choice in settings, default empty.\n\n**Done when:** acceptance items 16 and 17 on #272 pass: a human PR merges on a trial repo; the repo's own CI is neither flagged nor broken.\n",
>  "https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246343182": "/plan Yes: leave both out, since they alre

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_card_repo_ci.py 2>&1 | grep -E "^E .*859|passed|failed|Error" | head -30; cat /tmp/pack/open_issues.json | head -c 1500
```

> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('ci') finishes, so its card is never redrawn
> tests/test_card_repo_ci.py:124: AssertionError
>         """A failed run of the repo's own CI redraws the card too.
> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('ci') finishes, so its card is never redrawn
> tests/test_card_repo_ci.py:124: AssertionError
> _____________ test_a_required_repo_check_that_failed_shows_failed ______________
>     def test_a_required_repo_check_that_failed_shows_failed(tmp_path, record_property):
>         """A required check of the repo's own that failed shows as failed.
>         Main's rule requires the repo's own `lint` besides Dokima's checks; `lint` failed on the pull request's head,
>         so the card must show `lint` with the failed circle. Proves 859.2."""
> >       assert got == "failed", \
>             f"859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as {got}:\n{card[-2500:]}"
> E       AssertionError: 859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as None:
> E         - <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> **<a href="https://github.com/o/r/runs/2601">Acceptance criterion</a>:** Criterion one of #246.
> E         **Definition of Done:** <img src="https://raw.githubusercontent.com/o/

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_card_repo_ci.py 2>&1 | grep -E "^E +AssertionError|^FAILED|passed|failed"; grep -n -A6 "workflow_run" dokima/install/dokima.yml | head -30
```

> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('ci') finishes, so its card is never redrawn
>         """A failed run of the repo's own CI redraws the card too.
> E       AssertionError: 859.1: the adopter's workflow does not start when the repo's own CI ('ci') finishes, so its card is never redrawn
> _____________ test_a_required_repo_check_that_failed_shows_failed ______________
>     def test_a_required_repo_check_that_failed_shows_failed(tmp_path, record_property):
>         """A required check of the repo's own that failed shows as failed.
>         Main's rule requires the repo's own `lint` besides Dokima's checks; `lint` failed on the pull request's head,
>         so the card must show `lint` with the failed circle. Proves 859.2."""
> >       assert got == "failed", \
>             f"859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as {got}:\n{card[-2500:]}"
> E       AssertionError: 859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as None:
> E         - <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> **<a href="https://github.com/o/r/runs/2601">Acceptance criterion</a>:** Criterion one of #246.
> E         **Definition of Done:** <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Acce

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import yaml;j=yaml.safe_load(open('.github/workflows/entry.yml'))['jobs']['card'];print(j.get('if'))"
```

> (github.event_name == 'issues' && github.event.action != 'deleted' && github.event.action != 'transferred') || github.event_name == 'issue_comment' || (github.event_name == 'schedule' && github.event.schedule == '*/15 * * * *') || (github.event_name == 'pull_request_target' &&
>  contains(fromJSON('["opened", "edited", "synchronize", "reopened", "closed", "labeled", "unlabeled", "ready_for_review", "converted_to_draft"]'), github.event.action)) ||
> (github.event_name == 'workflow_run' &&
>  contains(fromJSON('["pull_request_target", "merge_group", "push", "pull_request_review", "pull_request_review_comment"]'), github.event.workflow_run.event))

**Agent:** The plan's six new tests all fail today for the right reason. One test is too weak, so I'm writing a blocking review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote two criteria from the parent issue: the card redraws on the repo's own CI, and shows every required check.", "The planner wrote six tests that play the adopter's workflow and the card against a fake GitHub."], "decided": ["A required check that has not run shows as not started.", "A check reported as a commit status counts like a check run."], "open": []},
 "verdict": "block",
 "summary": "The redraw test only plays a CI named ci, so listening for that one name would pass it.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "859.1 weak test", "text": "Both 859.1 tests play only a CI named `ci`. Adding `ci` to the thin workflow's list passes them, yet an adopter's CI named anything else never redraws the card. Smallest fix: also play a CI under a name nobody would guess, such as `Build and test 7f3a`, and require that it redraws too.", "evidence": "`tests/test_card_repo_ci.py` line 30 sets `CI = \"ci\"`; `thin_starts` checks only that name against `dokima/install/dokima.yml` line 12."}
 ],
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
  {"criterion": "859.1", "cut": [], "missing": ["The repo's CI has a name other than ci."]},
  {"criterion": "859.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_card_rep
```

> Exit code 1
> raise 1's text holds 53 words, over its cap of 30: cut 23, keep the facts
> previous_step did line 1 holds 22 words, over its cap of 15: cut 7, keep the facts
> previous_step did line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

`7. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json;d=json.load(open('review.json'))
d['previous_step']['did']=["The planner wrote two criteria: redraw on the repo's CI, show required checks.","The planner wrote six tests against a fake GitHub."]
d['raises'][0]['text']="The 859.1 tests play only a CI named `ci`, so listening for that name passes. Fix: also play a CI with an unguessable name."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 859 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#859](https://github.com/dokima-dev/dokima/issues/859) (the card follows the repo's own CI). One test is too weak. The hand-back passes both checks.

**Why it's blocked:**
- Both tests for the first criterion play a CI named only `ci`.
- So a build that just adds `ci` to the list of workflows the adopter's setup listens for would pass.
- An adopter whose CI has any other name would still never see the card redraw.
- The fix I sent back: also play a CI with a name nobody could guess, and require that it redraws the card too.

**What's right:**
- Both of the owner's asks from [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety) have a criterion: redraw when the repo's CI finishes, and show every check the merge needs. Nothing was dropped or added.
- Each criterion is one behavior, and the size is fine.
- I ran all 6 new tests and each fails today for the right reason:
  - The adopter's setup doesn't start when the repo's own CI finishes.
  - The card doesn't show the required checks.
- The second criterion's tests are sound. The test for a check that hasn't run yet proves the card reads the branch rule, not just the checks that already ran.

The review is in `/tmp/dokima-out/review.json`.

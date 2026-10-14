# reviewer (plan) for #628

Run: https://github.com/dokima-dev/dokima/actions/runs/38513197330

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #628: A test holds the drawing code to every fixture
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 627 -->
> <!-- dokima-blocking: {"blocked_by": [627], "blocks": [], "loop": []} -->
> A test redraws every approved fixture offline, and the card code changes to match the approved card of 557.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/627
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/584
> - https://github.com/dokima-dev/dokima/issues/545
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/624
> 
> 
> **User story:** An approved visual stays exactly as approved, because a test fails on any difference.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acce

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/02-reviewer-plan.json','in/03-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000]); print('----')
"; head -c 3000 parent.json; echo; head -c 1500 open_issues.json
```

> in/02-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38510322459",
>  "commit_before": "4023b0be8be535d3ae5c545b027ce3aa855076d5",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 2080,
>   "turns": 1,
>   "cost_usd": 1.1043788,
>   "tokens_in": 81773,
>   "tokens_out": 92
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/628/38510322459-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38510322459",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner froze the approved 557 card and its data as the first fixture.",
>     "The planner wrote three tests and changed twenty older card tests to match that card."
>    ],
>    "decided": [
>     "The card code changes to match the approved 557 card exactly, wording included."
>    ],
>    "open": [
>     "The planner asks whether the edge cases icon keeps its sandbox demo link."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan carries all three asks, each with a test that fails today for the right reason.",
>   "raises": [
>    {
>     "kind": "issue",
>     "label": "Unplanned card wording",
>     "text": "A card with no plan still says All tests, while planned cards will say Test suite after this lands.",
>     "evidence": "`tests/test_new_issue_card.py:39` expects `All tests \u00b7 Code review \u00b7 Owner approval` and is not in the plan's test changes.",
>     "searched": [
>      545,
>      546,
>      584,
>      628
>     ],
>    

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git diff a45d7cb..HEAD --stat | tail -5; ls tests/fixtures/cards/; timeout 300 python3 -m pytest -q tests/test_fixtures.py 2>&1 | tail -30; grep -c "demo-icons" tests/fixtures/cards/*
```

> 5d46eca Merge remote-tracking branch 'origin/main' into try/issue-628
> 4023b0b planner for #628 (run 38508399410)
> a45d7cb The agent code splits into files by job (#640)
>  tests/test_check_names.py            |    4 +-
>  tests/test_field_icons.py            |   13 +-
>  tests/test_fixtures.py               |  219 ++
>  tests/test_scan.py                   |    9 +-
>  13 files changed, 4913 insertions(+), 70 deletions(-)
> 557.card.md
> 557.inputs.json
>   folder = '/tmp/pytest-of-runner/pytest-0/test_the_fixture_test_runs_wit0/fixtures'
>   name = '9.comments.md'
>   
>       def redraw(folder, name):
>           """Draw the fixture `name` of `folder` again from its saved inputs, with today's code."""
>           stem = name[:-len(".comments.md")] if name.endswith(".comments.md") else name[:-len(".card.md")]
>           if name.endswith(".comments.md"):
>               with open(os.path.join(folder, f"{stem}.comments.inputs.json")) as f:
>                   inputs = json.load(f)
>               tool = visuals()
>               if not hasattr(tool, "comments"):
>   >               pytest.fail(f"{name}: tools/visuals.py cannot draw comments offline yet: it has no comments(inputs)")
>   E               Failed: 9.comments.md: tools/visuals.py cannot draw comments offline yet: it has no comments(inputs)
>   
>   tests/test_fixtures.py:81: Failed
>   =========================== short test summary info ============================
>   FAILED tests/test_fixtures.py::test_every_fixture_matches_its_approved_drawing[557.card.md] - A

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_fixtures.py; ls tools/; grep -n "def \|^[A-Z_]* =" tools/visuals.py | head -40
```

> """Every approved fixture is drawn again offline and must match byte for byte.
> 
> #628, story 5 of #584.
> 
> A fixture is what the owner approved, frozen under `tests/fixtures/cards/` by `tools/visuals.py finalize`:
> 
> - `N.card.md`, the top card exactly as `card.render` drew it, beside `N.inputs.json`, `{"repo", "issue", "found"}`,
>   the data it was drawn from;
> - `N.comments.md`, the run and autopilot comments exactly as `draw` printed them, beside `N.comments.inputs.json`,
>   `{"repo", "issue", "pr", "posts"}`.
> 
> `test_every_fixture_matches_its_approved_drawing` draws each one again with the real code and fails on any
> difference, naming the fixture and its first differing line. The card is drawn by `card.render`; the comments by
> `visuals.comments(inputs)` in `tools/visuals.py`, the same step `draw` and `finalize` use, so the test holds the very
> code that made the fixture.
> 
> The first fixture is the card of issue 557 the owner approved, from branch `fixture/card-557` (commit e98dee4). There
> it was saved as the whole issue text; here it is saved in finalize's shape: the card and its Definition of Done, as
> `card.render` draws them, without the Original issue fold (the owner's own words, which the card code never draws)
> and without the trailing blank line. Its `edge_case_sources`, which that branch kept beside `found`, sit inside
> `found`, so `card.render(repo, issue, found)` alone draws it.
> 
> The folder the test reads can be pointed elsewhere with `DOKIMA_FIXTURES`, which is how the tests

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x -p no:cacheprovider tests/test_card.py tests/test_card_records.py tests/test_card_bullets.py tests/test_card_edge_cases.py tests/test_card_merge.py tests/test_card_running.py tests/test_field_icons.py tests/test_scan.py tests/test_check_names.py 2>&1 | grep -E "^FAILED|passed|failed" | head -30
```

> FAILED tests/test_card.py::test_no_footer_and_no_gap - assert []
> 1 failed, 4 passed in 0.46s

**Agent:** Reviewing the plan for issue 628: the new tests fail for the right reason. Now I'm checking the changed older tests.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -p no:cacheprovider tests/test_card.py tests/test_card_records.py tests/test_card_bullets.py tests/test_card_edge_cases.py tests/test_card_merge.py tests/test_card_running.py tests/test_field_icons.py tests/test_scan.py tests/test_check_names.py 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-200 | head -30
```

> Draws the card with the all tests check missing, queued, in progress, passed and failed, and checks the row's Test
>                  (run("all tests", "in_progress", None, n=4), "running"), (run("all tests", n=4), "passed"),
>                  (run("all tests", conclusion="failure", n=4), "failed")]
>         verdict (passed, failed or not started), and each verdict links to its proof."""
> _____________ test_a_missing_or_failed_check_never_shows_as_passed _____________
>     def test_a_missing_or_failed_check_never_shows_as_passed(record_property):
>         """A missing check, or one GitHub finished without success, never shows as passed.
>         GitHub reports, and checks neither ever shows passed."""
>         assert circle(draw(check_runs=[]), "First thing works", "180.6")[0] != "passed", "180.6: a missing check showed passed"
> >       assert done_items(dod(draw(check_runs=[]), "180.6"))["Test suite"] != "passed", "180.6: a missing All tests showed passed"
> __________ test_only_a_code_owners_merge_shows_owner_approval_passed ___________
>     def test_only_a_code_owners_merge_shows_owner_approval_passed(record_property):
>         """A code owner's merge shows Owner approval passed, even with no Approve review.
>         changes, and checks Owner approval shows passed both times; then a PR merged by a stranger, one merged by
>         Dokima's bot on autopilot, and an open PR, all with no review, and checks none of them shows it passed. Proves 235.3."""
> >       assert approval(draw(pr=merged("

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner planned again after the owner's answer, with the same three criteria and tests."],
  "decided": ["The edge cases icon keeps its sandbox demo link, as the owner said."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan keeps the owner's answer and carries all three asks, each with a test that fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "One test makes each saved card again from its saved data with the real card code and fails, naming the first differing line, on any difference from its answer key.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "628.1"},
  {"ask": "It runs offline.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "628.2"},
  {"ask": "Yes, today's card code must reproduce the approved #557 card.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "628.3"}],
 "behaviors": [
  {"criterion": "628.1", "one_behavior": true, "why": "One result: any difference fails, naming the first differing line."},
  {"criterion": "628.2", "one_behavior": true, "why": "One condition: the fixture test passes with no network."},
  {"criterion": "628.3", "one_behavior": true, "why": "One fixed card drawn exactly."}],
 "edge_cases": [
  {"criterion": "628.1", "cut": [], "missing": []},
  {"criterion": "628.2", "cut": [], "missing": []},
  {"criterion": "628.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_fixtures.py::test_a_changed_fixture_fails_naming_its_first_differing_line", "only_its_behavior": true, "why": "Runs the real fixture test: passes on good fixtures, fails naming the changed card and comments line."},
  {"test": "tests/test_fixtures.py::test_the_fixture_test_runs_with_no_network", "only_its_behavior": true, "why": "Runs the real f
```

> summary holds 22 words, over its cap of 20 (up to 24 passes)

`8. Bash`
```
sed -i 's/"summary": "The plan keeps the owner.s answer and carries all three asks, each with a test that fails today for the right reason."/"summary": "The plan keeps the owner'"'"'s answer and carries all three asks, each with a test failing today for the right reason."/' /tmp/dokima-out/review.json && sed -i 's/each with a test failing today for the right reason/each with a test that fails today as it should/' /tmp/dokima-out/review.json && grep '"summary"' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 628 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> "summary": "The plan keeps the owner's answer and carries all three asks, each with a test that fails today as it should.",
> summary holds 21 words, over its cap of 20 (up to 24 passes)

`9. Bash`
```
sed -i 's/carries all three asks, each with a test that fails today as it should/carries all three asks, each with a test failing today as it should/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 628 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> exit 0

**Agent:** I approved the plan for issue [#628](https://github.com/dokima-dev/dokima/issues/628) (a test holds the drawing code to every fixture). The hand-back is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Your answer is followed:** after you said "yes keep that link", the planner planned again with the same three criteria and tests. The approved 557 card it saved as a fixture still links the edge cases icon from the sandbox demo branch, in 3 places.
- **Every ask is covered:** all three asks from [#584](https://github.com/dokima-dev/dokima/issues/584) (previews every visual and freezes approved fixtures) have a criterion: the test that redraws each fixture, running it offline, and matching the 557 card exactly.
- **The new tests fail today for the right reason:**
  - The 557 card first differs at line 21: today's code says "Verified by" where the approved card says "Acceptance test."
  - The offline test fails because the code can't yet draw saved comments without GitHub.
- **The older tests the plan changes now fail where the plan says:** each fails on the new card wording (for example "Test suite" instead of "All tests") or on the Definition of Done line now holding four items instead of three.

I raised nothing new and had no open items to answer. The three side issues from the first review are already filed as [#651](https://github.com/dokima-dev/dokima/issues/651) (an unplanned card still says All tests), [#652](https://github.com/dokima-dev/dokima/issues/652) (live cards never show an edge case's source) and [#653](https://github.com/dokima-dev/dokima/issues/653) (AGENTS.md still says All tests).

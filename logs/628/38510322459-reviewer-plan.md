# reviewer (plan) for #628

Run: https://github.com/dokima-dev/dokima/actions/runs/38510322459

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #628: A test holds the drawing code to every fixture
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 627 -->
> <!-- dokima-blocking: {"blocked_by": [627], "blocks": [], "loop": []} -->
> A test redraws every approved fixture offline, and the card code changes to match the approved card of 557.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/628#issuecomment-6160480578) with `/plan`, or say `/review`
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
> - 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -50; cat tests/test_fixtures.py; ls tests/fixtures tests/fixtures/*
```

> commit 4023b0be8be535d3ae5c545b027ce3aa855076d5
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 04:13:43 2026 +0000
> 
>     planner for #628 (run 38508399410)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/card_player.py                 |    6 +-
>  tests/fixtures/cards/557.card.md     |   36 +
>  tests/fixtures/cards/557.inputs.json | 4561 ++++++++++++++++++++++++++++++++++
>  tests/test_card.py                   |    4 +-
>  tests/test_card_bullets.py           |   30 +-
>  tests/test_card_edge_cases.py        |   16 +-
>  tests/test_card_merge.py             |    8 +-
>  tests/test_card_records.py           |   73 +-
>  tests/test_card_running.py           |    4 +-
>  tests/test_check_names.py            |    4 +-
>  tests/test_field_icons.py            |   13 +-
>  tests/test_fixtures.py               |  219 ++
>  tests/test_scan.py                   |    9 +-
>  13 files changed, 4913 insertions(+), 70 deletions(-)
> """Every approved fixture is drawn again offline and must match byte for byte.
> 
> #628, story 5 of #584.
> 
> A fixture is what the owner approved, frozen under `tests/fixtures/cards/` by `tools/visuals.py finalize`:
> 
> - `N.card.md`, the top card exactly as `card.render` drew it, beside `N.inputs.json`, `{"repo", "issue", "found"}`,
>   the data it was drawn from;
> - `N.comments.md`, the run and autopilot comments exactly as `draw` printed them, beside `N.comments.inputs.json`,
>   `{"rep

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_fixtures.py 2>&1 | tail -40; grep -n "def \|finalize\|comments" tools/visuals.py | head -80
```

> Reads the fixture's saved inputs, draws it with today's code and compares it with the approved drawing; any
>           difference fails, naming the fixture and its first differing line."""
>           with open(os.path.join(FOLDER, name)) as f:
>               want = f.read()
>   >       where = first_difference(want, redraw(FOLDER, name))
>                                          ^^^^^^^^^^^^^^^^^^^^
>   
>   tests/test_fixtures.py:96: 
>   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
>   
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
>   FAILED tests/test_fixt

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,45p tools/visuals.py; sed -n 95,240p tools/visuals.py
```

> """Draw what Dokima would post on a real issue, with any branch's code.
> 
>     python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME
>     python3 tools/visuals.py preview ISSUE --branch BRANCH --repo OWNER/NAME --gallery-issue N
> 
> Run from the root of a checkout. The issue is read from GitHub through `gh`, and nothing is written there. The
> drawing code is taken from BRANCH through a git worktree of it in a temporary folder, so this checkout is left as it
> is. Printed to stdout: the issue's top card, every run comment drawn again from its record, and every autopilot
> comment drawn again as BRANCH's code would word it. Autopilot comments are recognised by this checkout's own lines.
> 
> `preview` posts that same drawing, with the caller's own `gh` login, as one comment on issue N of the gallery repo, so
> GitHub renders it. A hidden marker names the real issue, so a later preview of it edits that comment instead of posting
> another. Nothing is written to OWNER/NAME.
> 
>     python3 tools/visuals.py finalize ISSUE --branch BRANCH --repo OWNER/NAME
> 
> `finalize` freezes an approved drawing in this checkout, under `tests/fixtures/cards/`: `ISSUE.inputs.json` (the top
> card's `repo`, `issue` and `found`, enough for `card.render` to draw it again offline), `ISSUE.card.md` (that card as
> BRANCH drew it), `ISSUE.comments.inputs.json` (the run and autopilot posts the painter was handed) and
> `ISSUE.comments.md` (those comments as BRANCH drew them). It then posts the whole drawing on ISSUE o

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git fetch -q origin fixture/card-557 2>&1|tail -2; git ls-tree -r --name-only FETCH_HEAD 2>/dev/null | grep -i 557; git log --oneline -3 FETCH_HEAD
```

> tests/fixtures/cards/557.card.md
> tests/fixtures/cards/557.inputs.json
> e98dee4 Approved card fixture for #557: the layout Reza signed off on
> 507df86 The planner names the issue: its hand-back carries a title that code sets on approval (#576)
> ec45283 Autopilot reads main's required checks from the branch, which the app may read (#578)

**Agent:** Checking the frozen 557 card against the approved one on its fixture branch.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show FETCH_HEAD:tests/fixtures/cards/557.card.md > /tmp/a.md; diff /tmp/a.md tests/fixtures/cards/557.card.md; git show FETCH_HEAD:tests/fixtures/cards/557.inputs.json > /tmp/a.json; python3 -c "
import json;a=json.load(open('/tmp/a.json'));b=json.load(open('tests/fixtures/cards/557.inputs.json'))
print(a.keys(),b.keys());print(b['found'].keys()-a['found'].keys()); ea=a.get('edge_case_sources'); print(ea==b['found'].get('edge_case_sources')); print({k for k in a['found'] if a['found'][k]!=b['found'].get(k)})"
```

> 35,52d34
> < <!-- dokima-ask -->
> < <details><summary>Original issue</summary>
> < 
> < In Reza's words: "yes let autopilot merge alone but what if someone wants hitl mandatory for merge gate thats why i thought default behavior is hitl and you can turn on autopilot approval setting", and "allow bot approve for me with some narrow privilege".
> < 
> < Verified on dokima-dev/merge-sandbox (same rules as main) on Oct 12:
> < - Today Dokima's app cannot merge alone: the queue path waits on "review required" and a direct merge is refused by the merge queue.
> < - With the app added to the merge-queue ruleset as a bypass actor limited to pull requests, plus its existing review bypass, the app's direct merge succeeds with no review.
> < - GitHub still refuses that merge while a required check is missing, and still refuses any direct push to main.
> < 
> < Done when
> < - With the repo variable DOKIMA_AUTO_MERGE unset or off (the default), a pull request waits for the owner's approval, as today.
> < - With DOKIMA_AUTO_MERGE=on, a pull request whose code review passed, whose required checks are green on its head and whose branch contains main's newest commit is merged by Dokima's app directly; one that changes a workflow file still waits for the owner.
> < - With DOKIMA_AUTO_MERGE=on, the setup audit reports when the app is missing from the merge-queue ruleset's pull-request-only bypass list.
> < 
> < 
> < </details>
> < 
> 54,55c36
> < **Definition of Done:** <a href="https://github.com/dokima-dev/dokima/actions/runs/383

`7. Bash`
```
cd /home/runner/work/dokima/dokima; ls /tmp/pack/in; python3 -c "
import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(d.keys())" ; grep -rl "6155799768" /tmp/pack | head; gh api repos/dokima-dev/dokima/issues/comments/6155799768 --jq .body 2>&1 | head -20
```

> 01-planner.json
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> /tmp/pack/plan.json
> /tmp/pack/issue.md
> /tmp/pack/in/01-planner.json
> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "merge-sandbox" tests/fixtures/cards/557.card.md | cut -c1-400; grep -n "edge" tests/fixtures/cards/557.card.md | head -5 | cut -c1-300; git diff HEAD~1 -- tests/card_player.py tests/test_check_names.py
```

> 22:  <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee23c8086fa8b67b26278c461593068016/tests/test_merge_approval.py#L280">The setting was never set.</a></em><
> 25:  <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee23c8086fa8b67b26278c461593068016/tests/test_merge_approval.py#L303">A code review that blocks merges not
> 28:  <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee23c8086fa8b67b26278c461593068016/tests/test_audit.py#L513">The app is on the bypass list: nothing is rep
> 22:  <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/6b28a2ee2

`9. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -x -n auto 2>&1 | tail -3 || true; timeout 1200 python -m pytest -q -p no:cacheprovider 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-200 | tail -40
```

> Command did not complete within its 600s timeout and was moved to the background (ID: bwnbpq0wp). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`10. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 500 python -m pytest -q -p no:cacheprovider tests/test_card.py tests/test_card_bullets.py tests/test_card_edge_cases.py tests/test_card_merge.py tests/test_card_records.py tests/test_card_running.py tests/test_field_icons.py tests/test_check_names.py 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-220
```

> __________ test_only_a_code_owners_merge_shows_owner_approval_passed ___________
>     def test_only_a_code_owners_merge_shows_owner_approval_passed(record_property):
>         """A code owner's merge shows Owner approval passed, even with no Approve review.
>         changes, and checks Owner approval shows passed both times; then a PR merged by a stranger, one merged by
>         Dokima's bot on autopilot, and an open PR, all with no review, and checks none of them shows it passed. Proves 235.3."""
> >       assert approval(draw(pr=merged("boss"), reviews=[])) == "passed", \
> E       AssertionError: the Definition of Done line does not hold four verdict circles: **Definition of Done:** <a href="https://github.com/o/r/actions/runs/2/job/4"><img src="https://raw.githubusercontent.com/o/r/main/d
> E        +  where 3 = len(['passed', 'passed', 'passed'])
>         with All tests, Code review and Owner approval passed, and its issue's card (#239, #283) says Merged too. Proves
> >           assert done == {"Test suite": "passed", "Code review": "passed", "Owner approval": "passed"}, \
>                 f"345.2: merged PR #{p}'s Definition of Done is not every check passed: {done}"
> E           AssertionError: 345.2: merged PR #246's Definition of Done is not every check passed: {'Code review': 'passed', 'Owner approval': 'passed'}
> E           assert {'Code review...al': 'passed'} == {'Test suite'...al': 'passed'}
> E             {'Test suite': 'passed'}
> E             -     'Test suite': 'passed',
> E  

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rln '"All tests"\|All tests\b' tests/*.py | sort; echo ---; grep -rln 'Verified by' tests/*.py | sort
```

> tests/test_autopilot_checks.py
> tests/test_card_merge.py
> tests/test_card_records.py
> tests/test_card_running.py
> tests/test_card_status.py
> tests/test_checks_rerun.py
> tests/test_merge_gate.py
> tests/test_new_issue_card.py
> tests/test_plan_shape.py
> tests/test_playthrough.py
> tests/test_quiet_board.py
> tests/test_raised_cards.py
> tests/test_required_checks.py
> tests/test_reviewer_open_issues.py
> tests/test_scan.py
> ---
> tests/test_body.py
> tests/test_card.py
> tests/test_card_bullets.py
> tests/test_card_edge_cases.py
> tests/test_card_records.py
> tests/test_field_icons.py
> tests/test_merge_check.py
> tests/test_plan.py
> tests/test_required_checks_read.py
> tests/test_terms.py
> tests/test_wiki.py

**Agent:** Looking for older tests that the card change would break but the plan doesn't list.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; for f in test_card_status test_new_issue_card test_raised_cards test_quiet_board test_body test_terms test_wiki test_plan test_merge_check test_playthrough test_reviewer_open_issues test_autopilot_checks; do echo "== $f"; grep -n 'All tests\|Verified by' tests/$f.py | cut -c1-200 | head -6; done
```

> == test_card_status
> 509:    """Approved work whose every criterion's check and All tests passed says Ready for approval, and needs the owner.
> 536:    ("All tests failed", swap("all tests", conclusion="failure")),
> 537:    ("All tests has not run", without("all tests")),
> 544:    """Approved work never says Ready for approval while any criterion's check, or All tests, has not passed.
> == test_new_issue_card
> 39:           "This issue has no plan yet.\n\n**Definition of Done:** All tests · Code review · Owner approval\n\n"
> == test_raised_cards
> 450:    Draws the issue card of a pull request whose code review passed but whose criterion check and All tests failed,
> == test_quiet_board
> 362:    Main's branch rule requires All tests and Acceptance criteria, as Dokima's own rule does (#561)."""
> 368:            inner = {"strict": True, "contexts": ["All tests", "Acceptance criteria"],
> 369:                     "checks": [{"context": c, "app_id": None} for c in ("All tests", "Acceptance criteria")]}
> 426:    board.yml's waiting job. Autopilot, reading the head's checks, must not count it: with All tests and Acceptance
> 427:    criteria green beside it, the head is proven. Beside it, a cancelled All tests on the same head must still stop
> 434:    green = [{"name": n, "status": "completed", "conclusion": "success"} for n in ("All tests", "Acceptance criteria")]
> == test_body
> 37:          "    Verified by: nothing\r\n"
> 46:            "    Verified by: a test\n\n"
> == test_terms
> 9:       "    Verified

`13. Bash`
```
sleep 240; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output | tail -5
```

> <tool_use_error>Blocked: sleep 240 followed by: cat /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output tail -5. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

`14. Monitor`
```
until grep -qE "passed|failed" /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output; do sleep 5; done; tail -60 /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output
```

> <tool_use_error>InputValidationError: Monitor failed due to the following issue:
> The required parameter `description` is missing
> 
> This tool's schema was not sent to the API — it was not in the discovered-tool set derived from message history. Without the schema in your prompt, typed parameters (arrays, numbers, booleans) get emitted as strings and the client-side parser rejects them. Load the tool first: call ToolSearch with query "select:Monitor", then retry this call. For reference, this tool's input schema is: {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":{"description":{"description":"Short human-readable description of what you are monitoring (shown in notifications).","type":"string"},"timeout_ms":{"description":"Kill the monitor after this deadline. Default 300000ms. Deadlines above 600000ms are capped to 600000ms. You are notified at expiry and can re-arm.","default":300000,"type":"number","minimum":1000,"maximum":3600000},"command":{"description":"Shell command or script. Each stdout line is an event; exit ends the watch.","type":"string"},"ws":{"description":"WebSocket to open. Each text frame is an event; binary frames are reported as a placeholder line. Socket close ends the watch. Cannot be combined with command.","type":"object","properties":{"url":{"type":"string"},"protocols":{"type":"array","items":{"type":"string","pattern":"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$"}}},"required":["url"],"additionalProperties":false}},"required"

`15. Bash`
```
F=/tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bwnbpq0wp.output; until grep -qE "[0-9]+ (passed|failed)" $F; do sleep 5; done; tail -60 $F
```

> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 2 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 2 failed, 362 passed in 171.42s (0:02:51)

`16. Bash`
```
pkill -f "pytest -q -p no:cacheprovider" ; cd /home/runner/work/dokima/dokima; timeout 590 python -m pytest -q -n auto -p no:cacheprovider 2>&1 | grep -E "^FAILED|[0-9]+ passed" | cut -c1-160
```

> Exit code 144

`17. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1500 python -m pytest -q -n auto 2>&1 | grep -E "^FAILED|[0-9]+ passed" | cut -c1-160
```

> Command running in background with ID: brbqxhy8y. Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/brbqxhy8y.output. You will be notified when it completes. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`18. Bash`
```
F=/tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/brbqxhy8y.output; until grep -qE "[0-9]+ passed" $F; do sleep 5; done; cat $F
```

> Command did not complete within its 600s timeout and was moved to the background (ID: bqgoq7p77). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/bqgoq7p77.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.

`19. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/56e64d32-ae47-45a4-8818-4f87ad175006/tasks/brbqxhy8y.output
```

> FAILED tests/test_card.py::test_no_footer_and_no_gap - assert []
> FAILED tests/test_card_bullets.py::test_each_criterion_is_a_bullet_with_its_verified_by_under_it_in_italics - AssertionError: 235.1: under “First thing works�
> FAILED tests/test_card_bullets.py::test_verified_by_is_left_out_for_a_test_with_no_docstring - AssertionError: 235.1: criterion 1 lost a Verified by line: ['  -
> FAILED tests/test_card_bullets.py::test_only_a_code_owners_merge_shows_owner_approval_passed - AssertionError: the Definition of Done line does not hold four ve
> FAILED tests/test_card_edge_cases.py::test_edge_cases_show_on_one_line_between_verified_by_and_source[issue] - AssertionError: 538.1: on the issue card the crit
> FAILED tests/test_card_edge_cases.py::test_edge_cases_show_on_one_line_between_verified_by_and_source[pr] - AssertionError: 538.1: on the pr card the criterion 
> FAILED tests/test_card_edge_cases.py::test_no_edge_cases_shows_none_because_and_the_reason[issue] - AssertionError: 538.2: on the issue card the criterion lost 
> FAILED tests/test_card_edge_cases.py::test_no_edge_cases_shows_none_because_and_the_reason[pr] - AssertionError: 538.2: on the pr card the criterion lost its Ve
> FAILED tests/test_card_records.py::test_verified_by_is_each_tests_first_docstring_line_and_links_to_the_test - AssertionError: 180.2: the criterion does not say
> FAILED tests/test_card_records.py::test_verified_by_is_hidden_when_there_is_none - AssertionError: 180.2: Verified by hidden where there is one
> FAILE

`20. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "edge_case_sources" --include=*.py . | head; grep -n "All tests running" AGENTS.md | cut -c1-80
```

> tests/test_fixtures.py:20:and without the trailing blank line. Its `edge_case_sources`, which that branch kept beside `found`, sit inside
> 130:Every agent run posts one comment, written by code: one plain sentence on to

`21. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner froze the approved 557 card and its data as the first fixture.",
          "The planner wrote three tests and changed twenty older card tests to match that card."],
  "decided": ["The card code changes to match the approved 557 card exactly, including Test suite and Acceptance test."],
  "open": ["The planner asks whether the card keeps its edge cases icon from the sandbox's demo branch."]},
 "verdict": "approve",
 "summary": "The plan carries all three asks, each with a test that fails today for the right reason.",
 "raises": [
  {"kind": "issue", "label": "Unplanned card wording", "text": "A card with no plan still says All tests, while planned cards will say Test suite after this lands.", "evidence": "`tests/test_new_issue_card.py:39` expects `All tests · Code review · Owner approval` and is not in the plan's test changes."}
 ],
 "answers": [
  {"raise": "P2", "answer": "done", "why": "Confirmed: only the saved 557 data holds edge case sources; no record carries one."},
  {"raise": "P3", "answer": "done", "why": "Confirmed: the rules file says All tests running, which no longer matches the card once this lands."}
 ],
 "asks": [
  {"ask": "One test makes each saved card again from its saved data with the real card code and fails, naming the first differing line, on any difference from its answer key.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "628.1"},
  {"ask": "It runs offline.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "628.2"},
  {"ask": "Yes, today's card code must reproduce the approved #557 card.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "628.3"}
 ],
 "behaviors": [
  {"criterion": "628.1", "one_behavior": true, "why": "One result: any difference fails, naming the first differing
```

> Exit code 1
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`22. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d["previous_step"]["decided"]=["The card code changes to match the approved 557 card exactly, wording included."]
d["previous_step"]["open"]=["The planner asks whether the edge cases icon keeps its sandbox demo link."]
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 628 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> raise 1 files an issue, so searched must list the open issues searched for the same cause, not None
> raise 1 files an issue, so verdict must be symptom, root cause or new, not None
> the answer to P2 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P2 files an issue, so verdict must be symptom, root cause or new, not None
> the answer to P3 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P3 files an issue, so verdict must be symptom, root cause or new, not None

**Agent:** The hand-back checker wants a search of open issues for each filed issue; checking its format.

`23. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched" dokima/*.py | head -20; ls /tmp/pack
```

> dokima/raises.py:22:# An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> dokima/raises.py:23:SEARCHED = "searched"
> dokima/raises.py:45:    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> dokima/raises.py:47:    searched = decided.get(SEARCHED)
> dokima/raises.py:48:    if not is_numbers(searched) or not searched:
> dokima/raises.py:49:        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
> dokima/raises.py:50:                        f"cause, not {searched!r}")
> dokima/agent.py:299:def problems_searched(h, pack_dir):
> dokima/agent.py:300:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent.py:303:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent.py:425:        bad += problems_searched(h, pack_dir)
> dokima/agent.py:1899:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json

`24. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 20,60p dokima/raises.py; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(type(d),len(d))
for i in d: print(i.get('number'), i.get('title'))" | head -80
```

> CONFIRMS = "reviewer"
> FIELDS = ("kind", "to", "label", "text", "evidence")
> # An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> SEARCHED = "searched"
> # Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
> VERDICT = "verdict"
> VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> # A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
> CAUSE = "cause"
> SYMPTOMS = "symptoms"
> STAMPED = ("raised_by", "id")
> ANSWERS = ("done", "disagree")
> PREFIX = MappingProxyType({"planner": "P", "worker": "W", "reviewer": "R"})
> 
> 
> def _kinds():
>     return ", ".join(KINDS[:-1]) + " or " + KINDS[-1]
> 
> 
> def _verdicts():
>     names = list(VERDICTS)
>     return ", ".join(names[:-1]) + " or " + names[-1]
> 
> 
> def filing_problems(where, decided):
>     """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
>     problems = []
>     searched = decided.get(SEARCHED)
>     if not is_numbers(searched) or not searched:
>         problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
>                         f"cause, not {searched!r}")
>     if decided.get(VERDICT) not in VERDICTS:
>         problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
>     cause = decided.get(

`25. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d["raises"][0].update(searched=[545,546,584,628],verdict="new")
d["answers"][0].update(searched=[545,546,551,584],verdict="new")
d["answers"][1].update(searched=[581,637,638,584],verdict="new")
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 628 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#628](https://github.com/dokima-dev/dokima/issues/628) (test that redraws every saved card offline). The review is saved and passes both checks.

**Why I approved it**
- All three of your asks have a criterion. They come from your comments on [#584](https://github.com/dokima-dev/dokima/issues/584) (preview and freeze approved cards):
  - one test redraws each saved card and names the first differing line;
  - the test runs offline;
  - today's card code draws the approved 557 card exactly.
- I ran all three new tests and each fails today for the right reason. The 557 card first differs at line 21, the comments half doesn't exist yet, and so the offline test can't pass yet.
- The first test also passes on fixtures that match the code, so it isn't a check that fails on everything.
- The saved 557 card is the same as the one you approved on the `fixture/card-557` branch, minus your own Original issue text. The card code never draws that part.
- In the full suite, 23 tests fail and 1,139 pass. All 23 failures are the new tests or the 20 older tests the plan changes on purpose. Nothing else breaks.

**Your question is still open.** The approved card loads its edge-cases icon from the sandbox repo's demo branch, and the plan keeps that link. I didn't answer this for you. Keeping it means live cards depend on another repo's demo branch, and that's your call. The work waits for you: answer with `/plan`, or say `/review` to go with the planner's assumption.

**Problems outside this issue**
- **Mine:** a card with no plan will still say "All tests" while planned cards say "Test suite". `tests/test_new_issue_card.py:39` expects the old wording and the plan doesn't change it.
- **Confirmed from the planner:** only the saved 557 data holds an edge case's source; no live record has one.
- **Confirmed from the planner:** `AGENTS.md` still says "All tests", which will no longer match the card.

The checker wanted a list of open issues searched for each of these. I chose the related ones from the pack's open-issues list by title, since I had no GitHub access. None looked like the same problem, so I marked all three as new.

**Agent:** A background wait loop hit its time limit and was stopped. It was only watching for the full test run to finish, and that run had already finished and been read, so nothing needs restarting and the review is unchanged.

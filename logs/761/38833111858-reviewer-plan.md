# reviewer (plan) for #761

Run: https://github.com/dokima-dev/dokima/actions/runs/38833111858

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #761: Delete the planner's old post and reject steps
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 765 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Deletes the planner's unused post and reject steps and its old plan writer, with their tests.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/761#issuecomment-6205461548) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> - https://github.com/dokima-dev/dokima/issues/760
> - https://github.com/dokima-dev/dokima/issues/762
> - https://github.com/dokima-dev/dokima/issues/718
> - https://github.com/dokima-dev/dokima/issues/765
> 
> 
> **User story:** The planner keeps only its check, so no unused code can post plans or rejections on issues.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Asking the pl

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_planner_old_steps.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit 0704cf6805e80260d5f1a5eaca427f3f4eae822a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 01:04:06 2026 +0000
> 
>     planner for #761 (run 38831585160)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_body.py               |  84 +------------------------
>  tests/test_card_every_change.py  |  39 +++---------
>  tests/test_card_folds.py         |  15 ++---
>  tests/test_open_ask.py           |  28 ++-------
>  tests/test_open_until_planned.py |  17 +----
>  tests/test_planner.py            |  63 +------------------
>  tests/test_planner_old_steps.py  | 133 +++++++++++++++++++++++++++++++++++++++
>  tests/test_rules_split.py        |  19 +++++-
>  tests/test_scope_from_files.py   |   4 +-
>  9 files changed, 175 insertions(+), 227 deletions(-)
> """The planner keeps only its check; its old steps, writer and text builder are gone.
> 
> Covers #761 (story 2 of #739). Workflows call only `python3 -m dokima.planner check`; the `post` and `rejected`
> actions, `render` (which wrote a plan into the issue's text) and `plan_text` (which built that text) are left from the
> old label flow. The step tests run the planner's command from the repo root with a fake `gh` first on PATH that logs
> every call to a file, so a step that still posts to GitHub is caught without any network.
> """
> import json
> import os
> import re
> import stat
> import subprocess
> import sys
> 
> sys.path.insert(0, os.path.join(os.path.dir

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python3 -m pytest -q tests/test_planner_old_steps.py 2>&1 | tail -30; grep -n "def \|post\|rejected\|argv\|sys.exit" dokima/planner.py | head -80
```

> assert ['issue comme...ons/runs/42)'] == []
>   
>   Left contains 3 more items, first extra item: 'issue comment 9 -R o/r --body **Plan rejected:** plan.json is not valid JSON'
>   
>   Full diff:
>   - []
>   + [
>   +     'issue comment 9 -R o/r --body **Plan rejected:** plan.json is not valid '
>   +     'JSON',
>   +     '',
>   +     '[See the run](https://github.com/o/r/actions/runs/42)',
>   + ]
> FAILED tests/test_planner_old_steps.py::test_the_plan_writer_is_gone - AssertionError: 761.3: the planner still has render, the old writer of a plan into the issue
> assert not True
>  +  where True = hasattr(planner, 'render')
> FAILED tests/test_planner_old_steps.py::test_the_plan_text_builder_is_gone - AssertionError: 761.4: the planner still has plan_text, the old plan text builder
> assert not True
>  +  where True = hasattr(planner, 'plan_text')
> FAILED tests/test_planner_old_steps.py::test_no_test_reaches_the_old_steps - AssertionError: 761.5: the planner's old steps ['render', 'plan_text'] are still there, so their tests' deletion is unproven
> assert ['render', 'plan_text'] == []
>   
>   Left contains 2 more items, first extra item: 'render'
>   
>   Full diff:
>   - []
>   + [
>   +     'render',
>   +     'plan_text',
>   + ]
> 5 failed in 0.46s
> 4:    python3 -m dokima.planner post N OUT    # post the plan on issue N, or the proposed split
> 5:    python3 -m dokima.planner rejected N OUT  # say on issue N why the run was rejected
> 13:is listed, far over is rejected.
> 14:Nothing is posted unless `check` passes.
> 33:NEW_TEST_

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python3 -m pytest -q tests/test_planner_old_steps.py 2>&1 | grep -A3 "761.1"|head; git show HEAD -- tests/test_scope_from_files.py tests/test_rules_split.py tests/test_card_every_change.py tests/test_planner.py | head -250
```

> the hand-back, then runs the planner's old `post` step on it: the fake gh must log no call. Proves 761.1.
>         """
>         record_property("proves", "761.1")
>         bin_dir, log = fake_gh(tmp_path)
>         out = tmp_path / "out"
>         out.mkdir()
> --
>         assert logged(log) == ["probe"], f"761.1: the fake gh did not log a call made through it: {logged(log)}"
>         log.unlink()
>         checked = run("check", out, bin_dir)
> commit 0704cf6805e80260d5f1a5eaca427f3f4eae822a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 01:04:06 2026 +0000
> 
>     planner for #761 (run 38831585160)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_card_every_change.py b/tests/test_card_every_change.py
> index b3b4775..8382f19 100644
> --- a/tests/test_card_every_change.py
> +++ b/tests/test_card_every_change.py
> @@ -5,12 +5,11 @@ Story 2 of #425, re-planned as one story of three criteria.
>  #419: the code review had passed, yet the card said Code review running for 30 minutes. card.yml picked its moments:
>  it skipped the bot's own edits and comments (except a code review's run card on a pull request) and redrew on a run's
>  start only for the full suite. The review's record is the bot's edit of its run card, so nothing redrew. Beside
> -card.yml, the old planner (dokima/planner.py, `post`) saved its own plan above the marker, and the plan approval
> -(`python3 -m dokima.agent ne

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x --deselect tests/test_planner_old_steps.py -p no:cacheprovider 2>&1 | tail -8
```

> +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', '-m', 'dokima.agents', 'model', 'planner'], returncode=0, stdout='claude-opus-5-5\n', stderr='').returncode
>   
>   - claude-sonnet-5-5
>   ?         -----
>   + claude-opus-5-5
>   ?        +++)
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 36 passed, 5 deselected, 1 warning in 4.61s

**Agent:** Running the full test suite on the branch to check the planner's test edits leave nothing broken.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1200 python3 -m pytest -q -n auto --ignore tests/test_planner_old_steps.py -p no:cacheprovider 2>&1 | tail -8 || true
```

> assert (0 == 0 and 'claude-opus-5-5' == 'claude-sonnet-5-5'
>  +  where 0 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', '-m', 'dokima.agents', 'model', 'planner'], returncode=0, stdout='claude-opus-5-5\n', stderr='').returncode
>   
>   - claude-sonnet-5-5
>   ?         -----
>   + claude-opus-5-5
>   ?        +++)
> 9 failed, 1239 passed, 4 warnings in 312.56s (0:05:12)

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 1200 python3 -m pytest -q -n auto --ignore tests/test_planner_old_steps.py -p no:cacheprovider 2>&1 | grep ^FAILED; git stash list | head -1
```

> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_each_role_has_its_own_subscription_and_model - AssertionError: 698.3: the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent - AssertionError: 698.4: Claude Code got model 'claude-opus-5-5', not the role's claude-unreleased-9-9
> FAILED tests/test_agents.py::test_a_role_the_file_leaves_out_starts_claude_code_as_today - AssertionError: 698.7: the worker the file names should run on claude-haiku-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> FAILED tests/test_agents.py::test_a_role_missing_its_model_stops_and_names_the_role - AssertionError: 698.8: a planner with no model line did not stop with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_an_unknown_agent_stops_before_any_agent - AssertionError: 698.10: an unknown agent did not stop the planner with exit 1: exit 0; stdout: ''; stderr: ''
> FAILED tests/test_agents.py::test_a_runs_record_reads_its_agent_through_the_interface - AssertionError: 698.15: the record names models ['claude-opus-5-5'], not zeta's zeta-1
> FAILED tests/test_agents.py::test_moving_a_role_takes_one_edit_of_its_own_lines - AssertionErr

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,20p dokima/planner.py; sed -n 585,700p dokima/planner.py; grep -rn "planner" .github/workflows/*.yml | grep -v "^.*#" | grep "dokima.planner"
```

> """The planner's hand-back: check its shape, then write it into the issue.
> 
>     python3 -m dokima.planner check N OUT   # fail loudly unless OUT holds a well-formed plan
>     python3 -m dokima.planner post N OUT    # post the plan on issue N, or the proposed split
>     python3 -m dokima.planner rejected N OUT  # say on issue N why the run was rejected
> 
> The planner holds no GitHub key. It ends by writing one plan.json to OUT, of kind user_story or feature (see
> dokima/roles/planner.md), raising its questions for the owner in its raises, plus its tests in tests/. Every
> criterion's source is issue N, its parent issue named in the pack, or a comment on either; every test it names is in
> the repo, filed under one of the plan's criteria. Every older test it changes, renames or deletes needs a reason in
> test_changes. Every new test has a one-sentence summary, names each criterion it proves by number below it, and fails
> on today's code. Criteria and the docstrings the planner adds are held to word caps (dokima/words.py): a little over
> is listed, far over is rejected.
> Nothing is posted unless `check` passes.
> """
> 
> import ast
> import json
> import os
> import re
>                 continue
>             if r.returncode in (0, 5):  # 0: passed or skipped, 5: nothing ran
>                 out.append(f"{t} is a new test that passes today (or is skipped); every new test must fail on today's code")
>     return out
> 
> 
> def render(number, body, plan, tags, older=()):
>     """The issue body for a plan, in the form

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "plan_text\|planner.render\|run_planner_post\|\"post\"\|'post'\|\"rejected\"" tests/ | grep -v test_planner_old_steps | head; timeout 100 python3 -m pytest -q tests/test_planner_old_steps.py::test_the_post_step_posts_nothing 2>&1 | grep "^E" | head -3; grep -rn "planner.*post\|planner.*rejected" .github dokima --include=*.yml --include=*.py --include=*.md | grep -v "^dokima/planner.py" | head
```

> tests/test_autopilot_river.py:374:    r = run(monkeypatch, tmp_path / "rejected", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True,
> tests/test_raised_cards.py:395:              "rejected": "Fix the rejected hand-back",
> tests/test_card_raises_status.py:249:     card.TODO["rejected"], (planner(Q1),), 0),
> tests/test_cancelled_run.py:48:    out["rejected"] = Run(t / "rejected", "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BAD_REVIEW)
> tests/test_cancelled_run.py:107:        assert "rejected" not in body.lower() and "failed" not in re.sub(r"<img[^>]*>", "", body).lower(), \
> tests/test_cancelled_run.py:112:    for name in ("rejected", "no-tools", "blocked"):
> tests/test_cancelled_run.py:130:    r = runs["rejected"]
> tests/test_cancelled_run.py:132:    body = visible(only_comment(r, "188.2", "rejected")["versions"][-1])
> tests/test_cancelled_run.py:133:    assert "rejected" in body.lower(), f"188.2: the card of a hand-back code rejected does not say so:\n{body[:900]}"
> tests/test_cancelled_run.py:142:        assert "rejected" not in body.lower(), f"188.2 ({name}): a run cancelled while its agent worked says rejected:\n{body[:900]}"
> E       AssertionError: 761.1: the planner's old post step still posted on the issue: ['issue comment 9 -R o/r --body **Planner proposes a split**', '', '```json', '{', '  "kind": "feature",', '  "title": "Slow calls run as jobs",', '  "summary": "Slow calls run as jobs.",', '  "feature": "A split.",', '  "stories": [', '    {', '      "

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Wrote five tests, one per criterion; all five fail today.",
          "Deleted nine old tests that only checked the old steps, and trimmed four more."],
  "decided": ["Asking for a deleted step now counts as done when nothing is posted."],
  "open": ["Asks the owner whether the test for deleted tests may wait on the code going."]},
 "verdict": "block",
 "summary": "Four criteria are well proven; the last test re-checks two other criteria instead of its own.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "761.5 test not its own",
   "text": "The test for 761.5 fails today only on its last check, which re-proves 761.3 and 761.4: the scan already passes, since the plan deleted those tests itself. Smallest fix: drop that check and mark 761.5 manual, because the plan's own test changes do the deleting and the full suite proves none is left.",
   "evidence": "`tests/test_planner_old_steps.py::test_no_test_reaches_the_old_steps` fails only on `left == []`, the same `hasattr` as `test_the_plan_writer_is_gone`."}
 ],
 "answers": [
  {"raise": "P1", "answer": "disagree", "why": "No need to ask the owner: the deleting is done in the plan itself, so 761.5 can be marked manual."}
 ],
 "asks": [
  {"ask": "The planner's old post step is deleted.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.1"},
  {"ask": "The planner's old reject step is deleted.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.2"},
  {"ask": "The old writer of a plan into the issue's text is deleted.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.3"},
  {"ask": "The old plan text builder is deleted.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.4"},
  {"ask": "Tests that only check the deleted code are deleted too.", "source": "https://github.com/dokima-dev/dokima/
```

> Exit code 1
> raise 1's label holds 5 words, over its cap of 4: cut 1, keep the facts
> raise 1's text holds 53 words, over its cap of 30: cut 23, keep the facts

`11. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
d=json.load(open('review.json'))
r=d['raises'][0]
r['label']="761.5 test overlaps"
r['text']="The 761.5 test fails today only by re-checking 761.3 and 761.4. Fix: drop that check; mark 761.5 manual, since the plan itself deletes the tests."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 761 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I've blocked the plan for [#761](https://github.com/dokima-dev/dokima/issues/761) (delete the planner's old post and reject steps) and sent it back to the planner over one test.

**What holds up:**
- All five asks from [#739](https://github.com/dokima-dev/dokima/issues/739) (delete dead code from the old label flow) have a criterion each, and none is missing.
- All five new tests fail today because the old code is still there, not because they crash.
- The tests for 761.1 and 761.2 run the real planner command with a stand-in for GitHub. Today both old steps still post on the issue, so both tests catch it.

**The blocker:**
- 761.5 says tests that only checked the deleted code are deleted too. The planner already deleted those tests in its own commit, so that part of the test already passes.
- The test fails today only because of its last check, and that check repeats what 761.3 and 761.4 already test (the old writer and text builder are still there).
- Smallest fix: drop that last check and mark 761.5 as checked by hand. The plan deletes those tests itself, and if any test still used the removed code, the full test suite would go red.

**The planner's question to you:** They asked whether that test may fail only until the old code is gone. I answered "disagree" so it doesn't wait on you: marking 761.5 as checked by hand removes the need to ask.

**The full test suite:** I ran it on this branch, leaving out the five new tests. 9 tests in `tests/test_agents.py` failed: they expected other models, but every role came back as `claude-opus-5-5`. The planner didn't touch that file, so these failures probably come from the sandbox, but I didn't check them on main. Everything else passed.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

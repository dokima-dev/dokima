# reviewer (plan) for #846

Run: https://github.com/dokima-dev/dokima/actions/runs/39089831420

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #846: Card and branch updates find Dokima's checks by the names GitHub shows
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [816], "loop": []} -->
> In an adopter's repo, the card and branch updates must find Dokima's checks by the names GitHub shows there.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/820
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/785
> - https://github.com/dokima-dev/dokima/issues/786
> 
> 
> **User story:** In an adopter's repo, the card shows Dokima's checks passing, and failing pull requests are not updated.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_shown_check_names.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"
```

> """Tests for #846: adopters' card and branch updates find checks by shown names.
> 
> An adopter's repo runs Dokima through the one thin workflow the install ships (`dokima/install/dokima.yml`): its job
> `dokima` calls `entry.yml`, whose jobs `full-suite` and `acceptance-criteria` call the workflows holding the checks.
> GitHub names a called job's check after every caller above it, so there the checks show as
> `dokima / full-suite / all tests`, `dokima / acceptance-criteria / Acceptance criteria` and
> `dokima / acceptance-criteria / 846.1 · ...`, never by their plain names. #820 makes the audit want those names; these
> tests ask the card and the branch updates to find the checks by them too.
> 
> Each test copies the settings file the install ships (`dokima/install/settings.yaml`) into a temp repo as
> `.dokima/settings.yaml`, the way an adopter installs it, and runs from that repo, as the card and update workflows do.
> The card is drawn by `dokima.card.render` from records and check runs; branch updates run `dokima.uptodate.run`
> against the fake GitHub of tests/test_uptodate_failing.py. Dokima's own repo, with plain names, is already covered by
> older tests (tests/test_card_criterion_label.py, tests/test_uptodate_failing.py).
> """
> import os
> import re
> import shutil
> import sys
> 
> import pytest
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> sys.path.insert(0, ROOT)
> sys.path.insert(0, os.path.dirname(__file__))
> from dokima import card, plan  # noqa: E402
> from test_uptodate_f

**Agent:** Run the tests and check the 846.5 test fails for the right reason.

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E .*846|passed|failed" | head -30; grep -n "all tests\|Acceptance criteria\|checks_passed\|def checks_by_key" dokima/card.py | head -30; grep -n "all tests" dokima/uptodate.py dokima/settings.py
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
>         failed. Proves 846.1."""
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> E         At index 0 diff: 'not started' != 'passed'
> E         -     'passed',
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Acceptance tests passed when that check passed.
>         an adopter's repo. Passed, the Definition of Done must show Acceptance tests passed and link that check; failed,
>         it must show Acceptance 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E   +AssertionError|passed|failed in"; sed -n 300,360p dokima/card.py; cat dokima/install/settings.yaml | head -50; ls dokima/settings.py
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> E         At index 0 diff: 'not started' != 'passed'
> E         -     'passed',
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Acceptance tests passed when that check passed.
>         an adopter's repo. Passed, the Definition of Done must show Acceptance tests passed and link that check; failed,
> >       assert (st, url) == ("passed", job(5)), (
>             f"8

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -ln '"all tests"\|ALL_TESTS\|Ready for approval' tests/*.py | head; grep -rn "Ready for approval" tests/*.py | head -5
```

> tests/card_player.py
> tests/test_audit_cli.py
> tests/test_autopilot_checks.py
> tests/test_all_tests_judge.py
> tests/test_card_bullets.py
> tests/test_card_merge.py
> tests/test_card_running.py
> tests/test_audit.py
> tests/test_automerge_confirmed.py
> tests/test_card_criterion_label.py
> tests/test_automerge_confirmed.py:237:        f"412.2: without the queue line the issue card no longer says Ready for approval: {card.status(tcs.ISSUE, plain)}"
> tests/test_automerge_confirmed.py:250:    review, the issue card must say Needs you: Ready for approval, and the board Needs you."""
> tests/test_automerge_confirmed.py:267:        f"412.3: the issue card does not say Needs you: Ready for approval while the PR waits on you: {card.status(tcs.ISSUE, found)}"
> tests/test_card.py:66:    """Approved work with every check passed says Ready for approval on its status line."""
> tests/test_card.py:68:    assert "Ready for approval" in status(render(recs=READY))

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner added criterion 846.5: in an adopter's repo, all green and approved, the card says Ready for approval.", "The planner added its test; all five tests fail today."], "decided": ["Two related open issues keep only their other asks, as the owner said."], "open": []},
 "verdict": "approve",
 "summary": "The plan now covers every place that reads Dokima's checks, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "the card, which reads the check runs by plain name (e.g. `all tests`), so its Definition of Done never shows them passing", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.1"},
  {"ask": "the card, which reads the check runs by plain name ... so its Definition of Done never shows them passing (Acceptance criteria)", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.2"},
  {"ask": "Fix: both find a check by the name GitHub shows, plain in Dokima's own repo and prefixed in an adopter's", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.3"},
  {"ask": "the branch updates (uptodate), which look for the same plain names before bringing a pull request up to date", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.4"},
  {"ask": "in an adopter repo, all green and code review approved, the card says Ready for approval", "source": "https://github.com/dokima-dev/dokima/issues/846#issuecomment-6244658830", "criterion": "846.5"}
 ],
 "behaviors": [
  {"criterion": "846.1", "one_behavior": true, "why": "One check, one card field."},
  {"criterion": "846.2", "one_behavior": true, "why": "One check, one card field."},
  {"criterion": "846.3", "one_behavior": true, "why": "One criterion check, one bullet."},
  {"criterion": "846.4", "one_behavior": true, "why": "One failed check, one skipped update."},
  
```

> Exit code 1
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/The planner added criterion 846.5: in an adopter's repo, all green and approved, the card says Ready for approval./The planner added a criterion: adopter repo, all green and approved, card says ready./" /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 846 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#846](https://github.com/dokima-dev/dokima/issues/846) (finding Dokima's checks by the names GitHub shows). It passed both hand-back checks.

- **My earlier blocker is fixed.** The planner added a fifth criterion: in an adopter's repo, with every check green and code review approved, the card says "Ready for approval." That's the one your latest comment asked for.
- **Your answer on the overlap is followed.** [#785](https://github.com/dokima-dev/dokima/issues/785) and [#786](https://github.com/dokima-dev/dokima/issues/786) (moving these names into settings) keep only their other asks.
- **All five new tests fail today for the right reason.** The card shows "not started" instead of "passed," and a pull request whose tests failed still gets brought up to date. None of them fail on a crash or a bad path.
- **Every ask maps to one criterion.** Each criterion is one behavior with one test. Nothing was dropped or added.
- **Dokima's own repo stays covered.** Older tests already check that the plain names still work there.

I raised nothing new. The review is in `/tmp/dokima-out/review.json`.

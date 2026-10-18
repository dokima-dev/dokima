# reviewer (plan) for #846

Run: https://github.com/dokima-dev/dokima/actions/runs/39089133268

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
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/846#issuecomment-6244554942) with `/plan`, or say `/review`
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acce

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_shown_check_names.py; git show --stat HEAD | head -30; cat /tmp/pack/in/01-planner.json | head -c 3000
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

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "Error|assert|846\.|passed|failed" | head -30; python -m pytest -q tests/test_card_criterion_label.py tests/test_uptodate_failing.py 2>&1 | tail -2
```

> _________ test_adopter_card_shows_test_suite_passed_by_its_shown_name __________
>     def test_adopter_card_shows_test_suite_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Test suite passed when all tests passed.
>         Passed, the Definition of Done must show Test suite passed and link that check; failed, it must show Test suite
>         failed. Proves 846.1."""
>         record_property("proves", "846.1")
>         st, url = done_verdict(draw([check(ALL_TESTS, n=4)]), "Test suite", "846.1")
> >       assert (st, url) == ("passed", job(4)), (
>             f"846.1: all tests passed in an adopter's repo as {ALL_TESTS!r}, but the Definition of Done shows Test suite "
>             f"{st!r}, linked to {url!r}, not passed and linked to {job(4)}")
> E       AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> E       assert ('not started', None) == ('passed', 'h...runs/2/job/4')
> E         At index 0 diff: 'not started' != 'passed'
> E         -     'passed',
> /home/runner/work/dokima/dokima/tests/test_shown_check_names.py:117: AssertionError
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E   |passed|failed" | head -30
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
> E         
> E         At index 0 diff: 'not started' != 'passed'
> E         
> E         Full diff:
> E           (
> E         -     'passed',
> E         -     'https://github.com/o/r/actions/runs/2/job/4',
> E         +     'not started',
> E         +     None,
> E           )
> ______ test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name _______
>     def test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name(record_property, adopter):
>         """In an adopter's repo, the card shows Acceptance tes

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_shown_check_names.py 2>&1 | grep -E "^E   .*(846|Error)|passed|failed$" | head; python -m pytest -q tests/test_shown_check_names.py 2>&1 | tail -6
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
>   +     'not started',
>   +     None,
>     )
> FAILED tests/test_shown_check_names.py::test_adopter_pr_whose_all_tests_failed_is_not_brought_up_to_date - AssertionError: 846.4: #70's all tests failed in an adopter's repo as 'dokima / full-suite / all tests', yet it was brought up to date; updates [(70, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), (80, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')]
> assert 70 not in [70, 80]
> 4 failed in 0.14s

**Agent:** Reviewing the plan for #846: all four new tests fail today. Checking the third one's reason, then the code.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_shown_check_names.py 2>&1 | grep "^FAILED"; grep -n "all tests\|Acceptance criteria\|checks_by_key\|def \|settings" dokima/card.py | head -60; grep -n "all tests\|settings\|def " dokima/uptodate.py | head -30; cat dokima/install/settings.yaml | head -60
```

> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_test_suite_passed_by_its_shown_name - AssertionError: 846.1: all tests passed in an adopter's repo as 'dokima / full-suite / all tests', but the Definition of Done shows Test suite 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/4
> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_acceptance_tests_passed_by_its_shown_name - AssertionError: 846.2: Acceptance criteria passed in an adopter's repo as 'dokima / acceptance-criteria / Acceptance criteria', but the Definition of Done shows Acceptance tests 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/5
> FAILED tests/test_shown_check_names.py::test_adopter_card_shows_a_criterion_passed_by_its_shown_name - AssertionError: 846.3: criterion 40.1's check passed in an adopter's repo as 'dokima / acceptance-criteria / 40.1 · First thing works', but its bullet shows 'not started', linked to None, not passed and linked to https://github.com/o/r/actions/runs/2/job/1
> FAILED tests/test_shown_check_names.py::test_adopter_pr_whose_all_tests_failed_is_not_brought_up_to_date - AssertionError: 846.4: #70's all tests failed in an adopter's repo as 'dokima / full-suite / all tests', yet it was brought up to date; updates [(70, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), (80, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')]
> 25:ALL_TESTS = "all tests"
> 26:ACCEPTANCE = "Acceptance cr

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "full-suite\|shown\|prefix" dokima/*.py | grep -v "^dokima/card.py.*shown_links" | head -30; git log --oneline -15 | cat; ls dokima/install; cat dokima/install/settings.yaml
```

> dokima/body.py:79:    It stays shown after a rename. A body that keeps one already, or has no marker yet, is returned as it was."""
> dokima/body.py:102:    shown = OPEN_START + head + owner if done is not None and not folded else FOLD_START + head + owner + FOLD_END
> dokima/body.py:103:    below = shown + ("" if done is None else TRAILER + done.strip("\n"))
> dokima/playthrough.py:52:def shown(text):
> dokima/playthrough.py:88:        s = shown(text)
> dokima/playthrough.py:146:        out = tempfile.mkdtemp(prefix="standin-") if step in STANDINS else None
> dokima/playthrough.py:192:        self.work = tempfile.mkdtemp(prefix="playthrough-")
> dokima/scan.py:55:    shown = (status or "no column") + (f" with {action}" if action else "")
> dokima/scan.py:58:        out.append(f"{label(kind, n)} is closed but sits in {shown}; it belongs in Done with no pill.")
> dokima/card.py:635:    shown = KEYWORD_URL.sub(r"\1&#104;", KEYWORD_HASH.sub(r"\1&#35;", ask or ""))
> dokima/card.py:637:    return (card.rstrip("\n") + "\n\n" + body.MARKER + body.FOLD_START + shown + body.FOLD_END
> dokima/raises.py:152:    prefix = PREFIX.get(role, "X")
> dokima/raises.py:156:        while f"{prefix}{n}" in used:
> dokima/raises.py:158:        rid = f"{prefix}{n}"
> dokima/planner.py:319:    N.2 ... in that order. A feature is shown to the owner as handed back, as a comment. Given this issue's link (or
> dokima/planner.py:404:    """The test folder setting, as a path prefix ending in '/'."""
> dokima/planner.py:425:    def visit

`8. Bash`
```
cd /home/runner/work/dokima/dokima; cat .dokima/settings.yaml 2>/dev/null | head -40; ls dokima/ | head -80; grep -n "check\|required" dokima/settings.py | head -30
```

> # This repo's own settings, over Dokima's shipped defaults (dokima/defaults.yaml).
> co_author: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> # Dokima's own prompts are never the worker's to change.
> protected_paths: [.github/, dokima/roles/]
> __pycache__
> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_claude.py
> agent_codex.py
> agent_github.py
> agent_kimi.py
> agent_next.py
> agent_records.py
> agent_roles.py
> agents.py
> app.json
> audit.py
> board.py
> body.py
> card.py
> checks.py
> defaults.yaml
> fence.py
> icons
> install
> manifest.py
> plan.py
> planner.py
> playthrough.py
> prompt.py
> raises.py
> retry.py
> roles
> scan.py
> settings.py
> setup.py
> turns.py
> uptodate.py
> words.py
> 25:BY_NAME = {"gates.required", "prompts.append"}  # lists that merge with the default ones by name
> 115:                                  text=True, check=True).stdout.strip()

`9. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/*.yaml dokima/defaults* 2>/dev/null; grep -rn "required_checks\|all tests" dokima/*.yaml dokima/defaults.yaml 2>/dev/null | head; grep -n "required_checks\|def " dokima/settings.py | head -40
```

> dokima/defaults.yaml
> dokima/defaults.yaml
> dokima/defaults.yaml:11:  # Tests the all tests check leaves out, by id, e.g. tests/test_live.py::test_network.
> dokima/defaults.yaml:57:  required: [all tests, Acceptance criteria]
> dokima/defaults.yaml:11:  # Tests the all tests check leaves out, by id, e.g. tests/test_live.py::test_network.
> dokima/defaults.yaml:57:  required: [all tests, Acceptance criteria]
> 32:def load(path):
> 45:def entry_name(entry):
> 50:def by_name(base, mine):
> 62:def merge(base, mine, warn, path=""):
> 80:def read(repo=".", warn=None):
> 91:def setup_lines(got):
> 102:def github_default_branch():
> 125:def env_lines(got):
> 147:def main(argv=()):

`10. Bash`
```
cd /home/runner/work/dokima/dokima; cat .dokima/settings.yaml 2>/dev/null | head -40; ls dokima/ | head -80; grep -n "check\|required" dokima/settings.py | head -30
```

`11. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/*.yaml dokima/defaults* 2>/dev/null; grep -rn "required_checks\|all tests" dokima/*.yaml dokima/defaults.yaml 2>/dev/null | head; grep -n "required_checks\|def " dokima/settings.py | head -40
```

> # This repo's own settings, over Dokima's shipped defaults (dokima/defaults.yaml).
> co_author: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> # Dokima's own prompts are never the worker's to change.
> protected_paths: [.github/, dokima/roles/]
> __pycache__
> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_claude.py
> agent_codex.py
> agent_github.py
> agent_kimi.py
> agent_next.py
> agent_records.py
> agent_roles.py
> agents.py
> app.json
> audit.py
> board.py
> body.py
> card.py
> checks.py
> defaults.yaml
> fence.py
> icons
> install
> manifest.py
> plan.py
> planner.py
> playthrough.py
> prompt.py
> raises.py
> retry.py
> roles
> scan.py
> settings.py
> setup.py
> turns.py
> uptodate.py
> words.py
> 25:BY_NAME = {"gates.required", "prompts.append"}  # lists that merge with the default ones by name
> 115:                                  text=True, check=True).stdout.strip()

> dokima/defaults.yaml
> dokima/defaults.yaml
> dokima/defaults.yaml:11:  # Tests the all tests check leaves out, by id, e.g. tests/test_live.py::test_network.
> dokima/defaults.yaml:57:  required: [all tests, Acceptance criteria]
> dokima/defaults.yaml:11:  # Tests the all tests check leaves out, by id, e.g. tests/test_live.py::test_network.
> dokima/defaults.yaml:57:  required: [all tests, Acceptance criteria]
> 32:def load(path):
> 45:def entry_name(entry):
> 50:def by_name(base, mine):
> 62:def merge(base, mine, warn, path=""):
> 80:def read(repo=".", warn=None):
> 91:def setup_lines(got):
> 102:def github_default_branch():
> 125:def env_lines(got):
> 147:def main(argv=()):

`12. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 20 gh issue view 820 2>&1 | head -60
```

> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}

`13. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 300,332p dokima/card.py; grep -n "ALL_TESTS\|ACCEPTANCE\b\|ACCEPTANCE)" dokima/card.py dokima/*.py | head -30
```

> words = "answer " + " and ".join(parts)
>     how = ("with `/plan`, `/work` or `/review`" if rec.get("role") == "reviewer" else
>            "with `/plan`" if count["blocker"] else "with `/plan`, or say `/review`")
>     return f"{f'[{words}]({url})' if url else words} {how}"
> 
> 
> def checks_by_key(check_runs):
>     """Index criterion checks by their key ('67.1') from names like '67.1 · ...'."""
>     found = {}
>     for run in check_runs:
>         key = run["name"].split(" · ")[0]
>         if re.fullmatch(r"\d+\.\d+", key):
>             found[key] = run
>     return found
> 
> 
> def as_items(steps, owner=None):
>     """Records (and an owner's words, as text) as the conversation the river reads, for a card drawn from records alone."""
>     from dokima import agent
>     return [{"author": {"login": owner}, "body": st} if isinstance(st, str) else
>             {"author": {"login": agent.BOT}, "body": f"{agent.MARK}\n```json\n{json.dumps(st)}\n```"} for st in steps]
> 
> 
> def checks_passed(number, h, check_runs):
>     """True when every criterion's check of plan `h`, and All tests, passed on the PR's latest commit."""
>     count = len(h.get("acceptance_criteria") or []) + len(h.get("non_functional") or []) if h else 0
>     by_key = checks_by_key(check_runs)
>     runs = [by_key.get(f"{number}.{k}") for k in range(1, count + 1)]
>     runs.append(next((r for r in check_runs if r["name"] == ALL_TESTS), None))
>     return count > 0 and all(state(r) == "passed" for r in runs)
> 
> 
> def todo(issue, found, rec, url=None):
> dokim

`14. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "checks_passed" dokima/ | grep -v "def "; sed -n 75,87p dokima/uptodate.py; grep -n "check_name\|check-runs" tests/test_uptodate_failing.py | head
```

> dokima/card.py:354:        return TODO["ready"] if checks_passed(issue["number"], h, found["check_runs"]) else TODO["not every check passed"]
> def tests_failed(repo, head, rest):
>     """True when every all tests run on the head finished and failed.
> 
>     False when one passed or is still running, there is none, or GitHub cannot say."""
>     try:
>         runs = (rest("GET", f"repos/{repo}/commits/{head}/check-runs?check_name={ALL_TESTS.replace(' ', '%20')}"
>                             f"&per_page={PER_PAGE}") or {}).get("check_runs") or []
>     except (subprocess.CalledProcessError, AttributeError):
>         return False
>     runs = [r for r in runs if r.get("name") == ALL_TESTS]
>     return bool(runs) and all(r.get("status") == "completed" and r.get("conclusion") in FAILED for r in runs)
> 
> 
> 12:  - GET .../commits/SHA/check-runs (check_name= honoured, empty past page 1): the check runs on that commit;
> 72:        m = re.fullmatch(rf"repos/{REPO}/commits/([^/]+)/check-runs", bare)
> 74:            runs = [r for r in self.checks.get(m[1], []) if unquote(query.get("check_name", r["name"])) == r["name"]]

**Agent:** Spotted a second plain-name reader in the card (the "ready" status). Checking it in an adopter's repo.

`15. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n '"ready"\|"not every check passed"' dokima/card.py | head -4; cd /tmp && mkdir -p adopt846/.dokima && cp /home/runner/work/dokima/dokima/dokima/install/settings.yaml adopt846/.dokima/ && cd adopt846 && python3 -c "
import sys; sys.path.insert(0,'/home/runner/work/dokima/dokima/tests'); sys.path.insert(0,'/home/runner/work/dokima/dokima')
import test_shown_check_names as t
txt=t.draw([t.check(t.ALL_TESTS,n=4),t.check(t.ACCEPTANCE,n=5),t.check(t.CRITERION,n=1)])
print([l for l in txt.splitlines() if 'Needs' in l or 'eady' in l or 'check' in l][:5])
txt=t.draw([t.check('all tests',n=4),t.check('Acceptance criteria',n=5),t.check('40.1 · First thing works',n=1)])
print([l for l in txt.splitlines() if 'Needs' in l or 'eady' in l or 'check' in l][:5])
"
```

> 35:        "ready": "Ready for approval",
> 36:        "not every check passed": "See why not every check passed"}
> 354:        return TODO["ready"] if checks_passed(issue["number"], h, found["check_runs"]) else TODO["not every check passed"]
> 787:        "ready": (approved, pr, green, done, []),
> []
> []
> Shell cwd was reset to /home/runner/work/dokima/dokima

`16. Bash`
```
cd /tmp/adopt846 && python3 -c "
import sys; sys.path.insert(0,'/home/runner/work/dokima/dokima/tests'); sys.path.insert(0,'/home/runner/work/dokima/dokima')
import test_shown_check_names as t
for names in [(t.ALL_TESTS,t.ACCEPTANCE,t.CRITERION),('all tests','Acceptance criteria','40.1 · First thing works')]:
  txt=t.draw([t.check(n,n=i) for i,n in enumerate(names,1)])
  print([l for l in txt.splitlines() if l.startswith('**')][:3])
"; sed -n 332,358p /home/runner/work/dokima/dokima/dokima/card.py
```

> ['**Review**', '**User story:** Owners see one card on every issue.', '**Scope:**']
> ['**Review**', '**User story:** Owners see one card on every issue.', '**Scope:**']
> def todo(issue, found, rec, url=None):
>     """What the owner must do now the river stopped on record `rec`, posted at `url`."""
>     from dokima import agent
>     role, h = rec.get("role"), rec.get("handback") or {}
>     if role == "not-started":
>         return TODO["not started"]
>     if not rec.get("check", {}).get("passed"):
>         return TODO["rejected"]
>     if role in ("planner", "reviewer") and asked(rec, url):
>         return asked(rec, url)
>     if role == "planner" and h.get("questions"):
>         return TODO["questions"]
>     verdict = h.get("verdict") if role == "reviewer" else None
>     if verdict == "escalate":
>         return TODO["escalated"]
>     if verdict == "block":
>         return TODO["three blocks"]
>     if verdict == "approve" and rec.get("stage") == "plan":
>         return TODO["plan approved"]
>     if verdict == "approve":
>         planned = agent.latest(found["recs"], "planner")
>         h = planned["handback"] if planned else None
>         return TODO["ready"] if checks_passed(issue["number"], h, found["check_runs"]) else TODO["not every check passed"]
>     return "See the newest record below"
> 
> 
> def status(issue, found):
> Shell cwd was reset to /home/runner/work/dokima/dokima

`17. Bash`
```
cd /tmp/adopt846 && python3 -c "
import sys; sys.path.insert(0,'/home/runner/work/dokima/dokima/tests'); sys.path.insert(0,'/home/runner/work/dokima/dokima')
import test_shown_check_names as t
t.RECS.append(t.rec('reviewer','code',n=14,verdict='approve'))
for names in [(t.ALL_TESTS,t.ACCEPTANCE,t.CRITERION),('all tests','Acceptance criteria','40.1 · First thing works')]:
  txt=t.draw([t.check(n,n=i) for i,n in enumerate(names,1)])
  print([l for l in txt.splitlines() if 'approval' in l or 'check passed' in l][:2])
"
```

> ['**Plan** · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: See why not every check passed', '**Definition of Done:** <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Acceptance tests · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Code review · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Test suite · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Owner approval']
> ['**Plan** · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Ready for approval', '**Definition of Done:** <a href="https://github.com/o/r/actions/runs/2/job/2"><img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"></a> Acceptance tests · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> Code review · <a href="https://github.com/o/r/actions/runs/2/job/1"><img src="https://raw.githubusercontent.com/o/r/m

**Agent:** Found a real gap: with every check green in an adopter's repo, the card still says "See why not every check passed". No criterion covers it. Writing the review.

`18. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote four criteria: three for the card, one for branch updates.",
          "The planner wrote one test per criterion; all four fail today."],
  "decided": ["Each criterion's own check is fixed here too."],
  "open": ["The planner asks the owner two questions: criterion checks, and overlap with two open issues."]
 },
 "verdict": "block",
 "summary": "One card reader is missed: with every check green in an adopter's repo, the card never says ready.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion: ready",
   "text": "The card's ready status also finds all tests by its plain name, and no criterion carries it. Add a criterion and test: in an adopter's repo, every check passed and the code review approved, the card says Ready for approval.",
   "evidence": "`dokima/card.py:328` in `checks_passed` compares to plain `all tests`. Drawn in an adopter's repo, all green: `See why not every check passed`."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "The owner asks every Dokima check to be found by its shown name, criterion checks included.",
   "words": "Fix: both find a check by the name GitHub shows, plain in Dokima's own repo and prefixed in an adopter's",
   "source": "https://github.com/dokima-dev/dokima/issues/846", "changes": false}
 ],
 "asks": [
  {"ask": "the card, which reads the check runs by plain name (e.g. `all tests`), so its Definition of Done never shows them passing", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.1"},
  {"ask": "the card, which reads the check runs by plain name ... so its Definition of Done never shows them passing (Acceptance criteria)", "source": "https://github.com/dokima-dev/dokima/issues/846", "criterion": "846.2"},
  {"ask": "Fix: both find a check by the name GitHub shows, plain in Dokima's own repo and prefixed in an adopter's", "source": "ht
```

> Exit code 1
> raise 1's text holds 40 words, over its cap of 30: cut 10, keep the facts
> raise 1's evidence holds 21 words, over its cap of 20: cut 1, keep the facts

`19. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
d=json.load(open("review.json"))
r=d["raises"][0]
r["text"]="The card's ready status also reads all tests by plain name; no criterion carries it. Add one: adopter repo, all green, code review approved, card says Ready for approval."
r["evidence"]="`dokima/card.py:328` `checks_passed` wants plain `all tests`. Adopter repo, all green: card says `See why not every check passed`."
json.dump(d,open("review.json","w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 846 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?; rm -rf /tmp/adopt846
```

> rc=0

**Agent:** I've blocked the plan for [#846](https://github.com/dokima-dev/dokima/issues/846) (card and branch updates find checks by shown names) and sent it back to the planner. The hand-back passes both checks.

**What's right:**
- The plan has four criteria: Test suite, Acceptance tests and each criterion's own check on the card, plus branch updates skipping a pull request whose all tests failed.
- Each criterion is one behavior with one test.
- All four new tests fail today because the feature is missing, not because of a crash.
- The older tests that cover the plain names in Dokima's own repo still pass.

**The gap:** the card's "ready" status also looks for all tests by its plain name, and no criterion covers it.
- In a test adopter repo with every check green and the code review approved, the card still says "See why not every check passed" instead of "Ready for approval".
- The cause is `dokima/card.py:328`.
- A worker could pass all four tests and leave this broken.
- The fix I asked for: one more criterion and test saying the card shows Ready for approval in that case.

**The planner's two questions:**
- **Fix each criterion's own check too?** I answered yes for you, quoting your issue: "Fix: both find a check by the name GitHub shows, plain in Dokima's own repo and prefixed in an adopter's".
- **Overlap with [#785](https://github.com/dokima-dev/dokima/issues/785) (card reads check names from settings) and [#786](https://github.com/dokima-dev/dokima/issues/786) (updates wait on all tests by its settings name):** I left this one for you. It decides what those two issues keep, and nothing you've written settles it.

# reviewer (plan) for #934

Run: https://github.com/dokima-dev/dokima/actions/runs/39363127646

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #934: Opt-in: δokima approves and merges its own PRs once code review and checks pass
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo can opt in so Dokima approves and merges its own pull requests once review and checks pass.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/934#issuecomment-6282395686) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/686
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/363
> 
> 
> **User story:** Owners who opt in see finished pull requests merge on their own, with a note saying why.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When auto approve is on, a pull request whose code review and checks passed merges with no person waited on.
>  

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_auto_approve.py; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> """Tests for #934: an opted-in repo has Dokima approve and merge its own pull requests.
> 
> With `merge: {auto_approve: true}` in `.dokima/settings.yaml`, a pull request Dokima built merges by itself once its
> code review approved and the merge gate passed (every check main requires green on its head), off autopilot too, with
> one line on the pull request naming the code review's record and the green checks. Off, the shipped default, a passed
> gate still waits for the owner's approval. A blocked review or a red check is never approved. `integrity` stays
> locked. The audit says when main's branch rule still requires a review Dokima's app cannot give, and setup applies the
> change when the owner turns the setting on.
> 
> The river's tests run `python3 -m dokima.agent next 57 OUT` in-process, on the fake GitHub of
> tests/test_merge_gate.py, from a temp folder holding the settings file. The audit's test runs the audit command from
> outside on tests/fake_gh.py, as tests/test_audit_cli.py does. The setup test runs `python3 -m dokima.setup
> auto-approve acme/widgets` from outside, with its own fake `gh` program first on the PATH that logs every call.
> Nothing leaves the machine.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> import time
> 
> import pytest
> import yaml
> 
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
> sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
> from dokima import agent, agent_github, settings  # noqa: E402
> import tes

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_auto_approve.py 2>&1 | grep -E "^E .*934|passed|failed|Error" | head -40
```

> ________ test_with_auto_approve_on_a_passed_gate_merges_with_no_person _________
>     def test_with_auto_approve_on_a_passed_gate_merges_with_no_person(record_property, tmp_path, monkeypatch, capsys):
>         assert escaped is None, f"934.1: deciding what follows the code review failed: {escaped}"
>             (f"934.1: with merge.auto_approve on, the code review passed and every check is green, yet #60 did not merge "
> E       AssertionError: 934.1: with merge.auto_approve on, the code review passed and every check is green, yet #60 did not merge once at its tested head: merges [], printed 'stop', Next "**Next:** @owner-person All tests passed with main's newest commit. Approve the pull request on GitHub to merge it, or review it with a command to send it back."
> tests/test_auto_approve.py:113: AssertionError
>         assert escaped is None, f"934.2: deciding what follows the code review failed: {escaped}"
> E       AssertionError: 934.2: Dokima's approval should leave exactly one note on #60 linking the code review record (https://github.com/o/r/actions/runs/4); found []; everything posted on #60: []
> tests/test_auto_approve.py:148: AssertionError
>         merges, so the test is not passed by a run that never approves anything."""
>         assert escaped is None, f"934.3: deciding what follows the blocking code review failed: {escaped}"
> E       AssertionError: 934.3: with the code review approving and the setting on, #60 did not merge: []
> tests/test_auto_approve.py:181: AssertionErro

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "review_bypass_apps\|code_owner\|def clean\|app_id\|\"id\": 1\|apps" tests/fake_gh.py tests/test_audit_cli.py | head -30; python3 -m pytest -q tests/test_auto_approve.py -k audit 2>&1 | grep -A15 "934.7: main" | head -30
```

> tests/fake_gh.py:16:                                        the full rule lists the state's "review_bypass_apps" (app ids) as
> tests/fake_gh.py:17:                                        required_pull_request_reviews.bypass_pull_request_allowances.apps
> tests/fake_gh.py:20:    gh api [-X GET] repos/OWNER/REPO/installation                       the app's {"app_id": 1, "permissions": {...}}
> tests/fake_gh.py:208:                                            "checks": [{"context": c, "app_id": None} for c in checks]}
> tests/fake_gh.py:219:        inner = {"strict": state.get("strict", {}).get(m.group(1), True), "contexts": list(checks), "checks": [{"context": c, "app_id": None} for c in checks]}
> tests/fake_gh.py:223:        apps = state.get("review_bypass_apps")
> tests/fake_gh.py:224:        if apps is not None:
> tests/fake_gh.py:226:                "required_approving_review_count": 1, "require_code_owner_reviews": True,
> tests/fake_gh.py:228:                                                   "apps": [{"id": a, "slug": f"app-{a}", "name": f"App {a}"}
> tests/fake_gh.py:229:                                                            for a in apps]}}
> tests/fake_gh.py:245:        reply(state, {"id": 1, "app_id": 1, "app_slug": "dokima-runtime", "permissions": state["permissions"]})
> tests/fake_gh.py:277:            reply(state, {"id": 1, "body": fields.get("body", "")})
> tests/test_audit_cli.py:36:def clean():
> tests/test_audit_cli.py:231:def test_the_audit_command_mentions_the_code_owners_and_

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,120p tests/test_audit_cli.py
```

> """Tests for #283: `python3 -m dokima.audit OWNER/REPO` audits the live repo through `gh`.
> 
> The in-memory tests in tests/test_audit.py prove what the audit decides. These prove it really reads and writes GitHub:
> each runs the command from outside, the way a workflow does, with a fake `gh` (tests/fake_gh.py) first on PATH that
> keeps GitHub in a JSON file and logs every call. The command is run from a folder holding .github/CODEOWNERS, with
> DOKIMA_BOARD naming the org's board ("acme/1") and the dokima package on PYTHONPATH. The fake's docstring lists every
> call it answers; any other call is logged as unsupported and refused, and the failure message shows it.
> 
> How the command is expected to read GitHub:
>     labels              gh api repos/OWNER/REPO/labels
>     board fields, views gh api graphql, organization(login:){projectV2(number:){fields views}}
>     main's rule         gh api repos/OWNER/REPO/branches/main/protection (404 "Branch not protected": no rule)
>     the app's permissions  gh api repos/OWNER/REPO/installation, its "permissions"
> and to write only the Setup issue: open, edit, comment, close and pin it (gh api or gh issue), and mark its card Needs
> you through GraphQL (addProjectV2ItemById, then updateProjectV2ItemFieldValue on the Action field).
> """
> import copy
> import json
> import os
> import re
> import shutil
> import subprocess
> import sys
> 
> import pytest
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> sys.path.insert(0, ROOT)
> from dokima import manife

**Agent:** Plan's 8 tests all fail today for the right reason. Now checking how merges work today and whether the plan keeps the merge queue.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,60p tests/test_merge_gate.py; grep -n "merges\|def gh\|queue\|auto" tests/test_merge_gate.py | head -40; grep -rn "owner_approval\|auto_approve\|approve" rules/*.md | head -30
```

> """The merge gate tests the pull request with main's newest commit, then the owner approves.
> 
> Today a code review's approval stops for the owner at once, and autopilot merges once the head's required checks
> pass, even when the branch misses main's newest commit, so the code that lands was never tested as it lands. The
> merge gate runs right after a code review approves: it brings the branch up to date with main when it is behind
> (GitHub's Update branch), then waits for main's required checks on that combined head. Green, the owner is asked to
> approve (on autopilot, Dokima merges that head); any check red, the worker starts again on the pull request.
> 
> These tests run `python3 -m dokima.agent next 57 OUT` in-process on a passed code review that approves pull request
> #60, built for issue #57 from `try/issue-57`, against a fake GitHub in memory that stands in for `dokima.agent_github.gh`:
> 
> - the issue, its records (plan, plan review, the owner's `/work`, the worker's record) and its `autopilot` label,
>   through `gh issue view` and `gh api repos/o/r/issues/57`;
> - the pull request through `gh pr list`, `gh pr view` (any `--json` fields) and `gh api repos/o/r/pulls/60`, its
>   files (`dokima/x.py`), and GraphQL's merge state;
> - main's branch rule, requiring `all tests` and `Acceptance criteria`, through `gh api repos/o/r/branches/main`;
> - a branch behind main: `gh api repos/o/r/compare/main...X` answers `behind_by` 1, the REST pull request's
>   `mergeable_state` is "behind" and GraphQL

**Agent:** Tests fail for the right reasons. I found three gaps: the audit test, the setup test, and one bundled criterion. Writing the review now.

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote eight criteria, each with a test that fails today."],
  "decided": ["Auto approve works off autopilot too, and owner approval stays locked for every repo."],
  "open": ["Asks the owner whether a note can stand in for the bot's own approval.", "Asks whether opted-in repos still cannot set owner approval directly."]
 },
 "verdict": "block",
 "summary": "Close plan, but two tests miss a normal case and one criterion holds two behaviors.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Audit: off not tested",
   "text": "934.7 says the audit reports only with auto approve on. Its test never runs with it off, and never with a plain review. Add both cases.",
   "evidence": "`tests/test_auto_approve.py::test_the_audit_says_when_main_needs_a_review_the_bot_cannot_give` runs both cases with `auto_approve: True`."},
  {"kind": "blocker", "to": "planner", "label": "Setup: checks kept",
   "text": "934.8: owner said protection still requires the checks. Setup could drop main's required checks and pass. Assert they are kept.",
   "evidence": "`test_setup_turns_auto_approve_on_and_lets_the_app_bypass_reviews` checks only bypass and `dokima-runtime` in the write, never `all tests`."},
  {"kind": "blocker", "to": "planner", "label": "934.6 holds two",
   "text": "934.6 bundles the lock still failing and auto approve being a known setting. Split it in two, one test each.",
   "evidence": "`test_owner_approval_stays_locked_and_auto_approve_is_the_opt_in` asserts `settings.Locked` and then a clean read of `auto_approve`."},
  {"kind": "blocker", "to": "planner", "label": "934.4 checks extra",
   "text": "The 934.4 test also asserts the worker starts again, which 934.4 does not promise. Drop that assert.",
   "evidence": "`tests/test_auto_approve.py::test_red_checks_are_never_approved` asserts `said == \"start worker\"`."}
 ],
 "answers": [
  {"raise": "
```

> Exit code 1
> the answer to P3 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P3 files an issue, so verdict must be symptom, root cause or new, not None

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent*.py | head -20; gh issue list --search "identity bot approve" --state open 2>&1 | head
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/agent_autopilot.py:225:        if decided.get(raises.VERDICT) == "symptom" and raises.is_numbers([cause]):
> dokima/agent_autopilot.py:226:            # A symptom joins its cause as a comment, and files no issue (#623).
> dokima/agent_autopilot.py:233:            lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), cause)} · a symptom, added as a comment")
> dokima/agent_autopilot.py:235:        symptoms = decided.get(raises.SYMPTOMS)
> dokima/agent_autopilot.py:236:        if decided.get(raises.VERDICT) == "root cause" and raises.is_numbers(symptoms) and symptoms:
> dokima/agent_autopilot.py:237:            # A root cause files one issue marked as such, naming each symptom so GitHub links both ways (#623).
> dokima/agent_autopilot.py:239:            body += ["", "**Symptoms:** " + ", ".join(f"#{n}" for n in symptoms)]
> dokima/agent_autopilot.py:243:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> gh: To use GitHub CLI in a 

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 10,60p dokima/agent_checks.py; ls /tmp/pack; grep -n "SEARCHED\s*=\|VERDICT\s*=" dokima/raises.py
```

> from dokima import raises, words
> 
> 
> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(open(path)) if os.path.exists(path) else []
>     theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
>               and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
>     confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
>                  and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
>     filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
>     if not filed:
>         return []
>     bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
>     named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
>              for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numb

`10. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
  t=(i.get('title','')+' '+i.get('body','')[:0]).lower()
  if any(w in t for w in ['identity','approv','bot','rule']): print(i['number'], i.get('title'))
"
```

> 934 Opt-in: δokima approves and merges its own PRs once code review and checks pass
> 901 Numbers in plan rules reach the prompts from the same setting the code checks
> 900 One rule links an issue to its branch and pull request
> 899 Dokima ignores the repo's bot name setting in Python
> 870 The flow rules and commands rules never describe the hotfix lane, so owners cannot read how it works.
> 825 The wiki sync writes the bot placeholder as it is, and commits on the logs branch credit no co-author.
> 799 Leaner tests: study, fix brittle tests, one shared test surface, then reviewer rules for test quality
> 789 The bot Dokima recognizes comes from settings
> 747 One shared GitHub App: dokima[bot] everywhere, one-click install
> 694 When the owner approves new scope raised on a child story, code opens a fresh sibling issue under its parent.
> 677 Autopilot merges changes to Dokima's own rules
> 676 A merge is not tied to the commit the code review approved
> 457 The play-through's bot posts the stand-in records and live cards itself, as agent.yml's posting steps do, because a bot comment never starts the river (no /work, no agent.yml run).
> 432 AGENTS.md says a split has one level ('2 to 5 children, one level') while the autopilot rules speak of 'every sub-issue under it at every level'; the two disagree on whether a tree can be deeper than one level.
> 378 Autopilot and the owner's Approve add a pull request to the merge queue, and the issue says when it lands or why it left
> 363 Main is protected by a 

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
for a in d['answers']:
    if a['raise']=='P3': a.update({"searched":[747,677,363],"verdict":"new"})
json.dump(d,open(p,'w'),indent=1,ensure_ascii=False)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 934 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#934](https://github.com/dokima-dev/dokima/issues/934) (Dokima approves and merges its own pull requests). It's close, but it goes back to the planner. All 8 new tests fail today, and each fails because the feature is missing. None fails from a crash or a bad path. Every request in the issue maps to a criterion, so nothing was dropped.

**Blockers for the planner:**
- **934.7, the audit line:** the test only runs with auto approve on. An audit that warns every repo, opted in or not, would still pass. It also never tries a plain required review, only a code-owner review, though you named both. The fix is to add both cases.
- **934.8, setup:** you wrote "Branch protection still requires the checks", but nothing tests that. Setup could rewrite main's protection and drop its required checks, and the test would still pass. The fix is to check that both required checks are still there afterwards.
- **934.6:** this criterion holds two behaviors: owner approval still fails as locked, and auto approve is read as a known setting. It should become two criteria, each with its own test.
- **934.4:** its test also checks that the worker starts again, which 934.4 doesn't promise. That check should be dropped.

**The planner's questions and notes:**
- **Owner approval stays locked (P2):** I answered this one, quoting your words "turning on `merge.auto_approve` is the explicit opt-in". So owner approval stays locked for every repo.
- **The bot can't approve its own pull requests (P1):** I left this for you, because the answer changes how the system works. GitHub doesn't let the author of a pull request approve it. The plan assumes Dokima's one-line note stands in for an approval.
- **The identity rules still say the bot can never approve (P3):** I agreed this needs its own issue once this lands. No open issue covers it.

The review is saved in `/tmp/dokima-out/review.json` and passes both checks.

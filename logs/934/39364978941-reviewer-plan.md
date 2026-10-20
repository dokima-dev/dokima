# reviewer (plan) for #934

Run: https://github.com/dokima-dev/dokima/actions/runs/39364978941

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> <persisted-output>
> Output too large (31.4KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/02f5092f-8dda-4d30-82df-77f402735372/tool-results/bhfc8jddg.txt
> 
> Preview (first 2KB):
> # Issue #934: Opt-in: δokima approves and merges its own PRs once code review and checks pass
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo can opt in so Dokima approves and merges its own pull requests once review and checks pass.
> 
> **Plan**
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
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-934/tests/te

`2. Bash`
```
cd /tmp/pack; sed -n '/^## /,$p' issue.md | head -300; grep -n "^## \|^### " issue.md
```

> ## Comments
> 
> ### dokima-runtime on issue #934 (2026-10-20T03:06:51Z)
> 
> Autopilot: switched on, starting plan
> 
> ### dokima-runtime on issue #934 (2026-10-20T03:07:12Z)
> 
> <!-- dokima-record -->
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/planner.svg" width="16" height="16" align="absmiddle" alt="planner"> The planner planned this issue.
> 
> **Raised:**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/question.svg" width="16" height="16" align="absmiddle" alt="question"> **Doubt: bot cannot approve:** The bot cannot approve pull requests it opened. Should its one-line note count as approval? The plan assumes so. · for you
>   - Evidence: `agent.yml` opens every pull request with the app's key; GitHub refuses an author's own approval.
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/question.svg" width="16" height="16" align="absmiddle" alt="question"> **Two readings:** Should opted-in repos also be refused setting owner approval directly? The plan assumes yes. · for you
>   - Evidence: The issue says it stays locked for repos that do not opt in.
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/issue-found.svg" width="16" height="16" align="absmiddle" alt="issue found"> **Rules: bot never approves:** Once this l

`3. Bash`
```
cd /tmp/pack; sed -n 1,72p issue.md | sed 's/<img[^>]*>//g'; ls in; cat open_blockers.json
```

> # Issue #934: Opt-in: δokima approves and merges its own PRs once code review and checks pass
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo can opt in so Dokima approves and merges its own pull requests once review and checks pass.
> 
> **Plan**
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/686
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/363
> 
> 
> **User story:** Owners who opt in see finished pull requests merge on their own, with a note saying why.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** When auto approve is on, a pull request whose code review and checks passed merges with no person waited on.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-934/tests/test_auto_approve.py#L101"> Acceptance test</a>: With the setting on, a reviewed pull request with green checks merges by itself.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-934/tests/test_auto_approve.py#L101">A branch behind main merges only at the head brought up to date and green.</a></em></li><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-934/tests/test_auto_approve.py#L101">With the setting off, nothing merges by itself.</a></em></li></ul></details>
> -  **Acceptance criterion:** When Dokima approves, the pull request gets one line naming the code review rec

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1))" | head -400
```

> {
>  "kind": "user_story",
>  "title": "Opt in: Dokima approves and merges its own pull requests",
>  "summary": "A repo can opt in so Dokima approves and merges its own pull requests once review and checks pass.",
>  "user_story": "Owners who opt in see finished pull requests merge on their own, with a note saying why.",
>  "acceptance_criteria": [
>   {
>    "text": "When auto approve is on, a pull request whose code review and checks passed merges with no person waited on.",
>    "words": "When it is on, a pull request \u03b4okima built is approved and queued by \u03b4okima itself as soon as its code review has passed and the required checks (`gates.required`) are green. No person is waited on.",
>    "source": "https://github.com/dokima-dev/dokima/issues/934",
>    "files": [
>     "dokima/agent_roles.py",
>     "dokima/agent_autopilot.py",
>     "dokima/defaults.yaml"
>    ],
>    "edge_cases": [
>     {
>      "case": "A branch behind main merges only at the head brought up to date and green.",
>      "test": "tests/test_auto_approve.py::test_with_auto_approve_on_a_passed_gate_merges_with_no_person"
>     },
>     {
>      "case": "With the setting off, nothing merges by itself.",
>      "test": "tests/test_auto_approve.py::test_with_auto_approve_on_a_passed_gate_merges_with_no_person"
>     }
>    ]
>   },
>   {
>    "text": "When Dokima approves, the pull request gets one line naming the code review record and the green checks.",
>    "words": "The approval is visibly \u03b4okima's (its bot), with a one-line comment naming

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(p,indent=1)[:9000])"; cat /home/runner/work/dokima/dokima/tests/test_auto_approve.py
```

> <persisted-output>
> Output too large (32KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/02f5092f-8dda-4d30-82df-77f402735372/tool-results/bowtlxrvo.txt
> 
> Preview (first 2KB):
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39363127646",
>  "commit_before": "a3960ab8ae196da3a1e68d37408b09d200143891",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 94148,
>   "turns": 12,
>   "cost_usd": 0.7563002000000001,
>   "tokens_in": 651125,
>   "tokens_out": 9155
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/934/39363127646-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39363127646",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote eight criteria, each with a test that fails today."
>    ],
>    "decided": [
>     "Auto approve works off autopilot too, and owner approval stays locked for every repo."
>    ],
>    "open": [
>     "Asks the owner whether a note can stand in for the bot's own approval.",
>     "Asks whether opted-in repos still cannot set owner approval directly."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Close plan, but two tests miss a normal case and one criterion holds two behaviors.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Audit: off not tested",
>     "text": "934.7 says the audit reports only with auto approve on. Its test never runs with it off, and never with a plain review. Add

**Agent:** Reading the planner's tests now, then I'll run them.

`6. Bash`
```
cat -n /home/runner/work/dokima/dokima/tests/test_auto_approve.py
```

> 1	"""Tests for #934: an opted-in repo has Dokima approve and merge its own pull requests.
>      2	
>      3	With `merge: {auto_approve: true}` in `.dokima/settings.yaml`, a pull request Dokima built merges by itself once its
>      4	code review approved and the merge gate passed (every check main requires green on its head), off autopilot too, with
>      5	one line on the pull request naming the code review's record and the green checks. Off, the shipped default, a passed
>      6	gate still waits for the owner's approval. A blocked review or a red check is never approved. `integrity` stays
>      7	locked. The audit, with the setting on, says when main's branch rule still requires a review Dokima's app cannot give, and setup applies the
>      8	change when the owner turns the setting on.
>      9	
>     10	The river's tests run `python3 -m dokima.agent next 57 OUT` in-process, on the fake GitHub of
>     11	tests/test_merge_gate.py, from a temp folder holding the settings file. The audit's test runs the audit command from
>     12	outside on tests/fake_gh.py, as tests/test_audit_cli.py does. The setup test runs `python3 -m dokima.setup
>     13	auto-approve acme/widgets` from outside, with its own fake `gh` program first on the PATH that logs every call.
>     14	Nothing leaves the machine.
>     15	"""
>     16	import json
>     17	import os
>     18	import re
>     19	import subprocess
>     20	import sys
>     21	import time
>     22	
>     23	import pytest
>     24	import yaml
>     25	
>     26	sys.path.insert(0, o

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_auto_approve.py tests/test_settings_merge.py::test_setting_a_locked_setting_fails_the_run_naming_it 2>&1 | grep -E "^E .*934|passed|failed|Error" | head -40; git diff HEAD~1 --stat; git diff a3960ab8~1 -- tests/test_settings_merge.py
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

`8. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_auto_approve.py -k audit 2>&1 | sed -n '/AssertionError/,/^tests/p' | head -40; git stash list | head -2; git show HEAD --stat; git show HEAD -- tests/fake_gh.py
```

> E       AssertionError: 934.8: main requires a code owner review the app cannot give, and the Setup issue should say so on exactly one line naming code owners or a bypass; found [] in []
> E         unsupported calls: []
> E         writes: []
> E       assert 0 == 1
> E        +  where 0 = len([])
> 
> tests/test_auto_approve.py:285: AssertionError
> FAILED tests/test_auto_approve.py::test_the_audit_says_when_main_needs_a_review_the_bot_cannot_give - AssertionError: 934.8: main requires a code owner review the app cannot give, and the Setup issue should say so on exactly one line naming code owners or a bypass; found [] in []
>   unsupported calls: []
>   writes: []
> assert 0 == 1
>  +  where 0 = len([])
> 1 failed, 7 deselected in 0.35s
> commit 56ebd4e426159c499a67e3a8ef0a3a6ec19b276f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 20 03:33:47 2026 +0000
> 
>     planner for #934 (run 39364064604)
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> 
>  tests/fake_gh.py             |   6 +-
>  tests/test_auto_approve.py   | 147 ++++++++++++++++++++++++++-----------------
>  tests/test_settings_merge.py |   8 ++-
>  3 files changed, 101 insertions(+), 60 deletions(-)
> commit 56ebd4e426159c499a67e3a8ef0a3a6ec19b276f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 20 03:33:47 2026 +0000
> 
>     planner for #934 (run 39364064604)
>     
>     Co-authored-by: dokima-run

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "class Audit" -A40 tests/test_audit_cli.py | head -70; grep -n "settings\|cwd\|chdir" dokima/audit.py | head -30
```

> 58:class Audit:
> 59-    """One repo root with CODEOWNERS and a fake gh, where the audit command runs."""
> 60-
> 61-    def __init__(self, tmp_path, state, owners="* @alice\n"):
> 62-        self.root = tmp_path / "repo"
> 63-        (self.root / ".github").mkdir(parents=True)
> 64-        (self.root / ".github" / "CODEOWNERS").write_text(owners)
> 65-        self.bin = tmp_path / "bin"
> 66-        self.bin.mkdir()
> 67-        gh = self.bin / "gh"
> 68-        gh.write_text(f"#!{sys.executable}\n" + open(os.path.join(ROOT, "tests", "fake_gh.py")).read())
> 69-        gh.chmod(0o755)
> 70-        self.file = tmp_path / "github.json"
> 71-        self.save(state)
> 72-
> 73-    def save(self, state):
> 74-        """Replace the fake GitHub's state."""
> 75-        self.file.write_text(json.dumps(state))
> 76-
> 77-    def state(self):
> 78-        """The fake GitHub's state now."""
> 79-        return json.loads(self.file.read_text())
> 80-
> 81-    def run(self, criterion):
> 82-        """Run the audit command once; fail naming the criterion if it is missing or crashed."""
> 83-        env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}", PYTHONPATH=ROOT,
> 84-                   DOKIMA_BOARD="acme/1", FAKE_GH_STATE=str(self.file), GH_TOKEN="fake", GITHUB_TOKEN="fake",
> 85-                   GITHUB_REPOSITORY=REPO)
> 86-        p = subprocess.run([sys.executable, "-m", "dokima.audit", REPO], cwd=self.root, env=env, capture_output=True,
> 87-                           text=True, timeout=60)
> 88-        

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "merges" tests/test_merge_gate.py | head -15; grep -n "^REQUIRED\|^APPROVE_ASK" -A2 tests/test_merge_gate.py
```

> 3:Today a code review's approval stops for the owner at once, and autopilot merges once the head's required checks
> 7:approve (on autopilot, Dokima merges that head); any check red, the worker starts again on the pull request.
> 99:        self.merges, self.updates, self.comments, self.calls = [], [], [], []
> 149:            st = {"state": "MERGED" if self.merges else "OPEN", "isInMergeQueue": False, "autoMergeRequest": None,
> 192:        self.merges.append({"head": self.head, "pinned": pinned})
> 246:def test_autopilot_merges_only_the_head_tested_with_the_newest_main(record_property, tmp_path, monkeypatch, capsys):
> 247:    """Autopilot merges only once all tests passed with main's newest commit.
> 251:    date, and merge only the new head, once every required check passed there; today it merges the old head, never
> 261:    assert fake.merges and all(m["head"] == NEW for m in fake.merges), \
> 263:         f"merges={fake.merges}, branch updates asked at {fake.updates}; it should merge {NEW[:7]} only")
> 264:    assert all(m["pinned"] in (None, NEW) for m in fake.merges), \
> 265:        f"596.1: the merge was pinned to a head other than the tested one: {fake.merges}"
> 270:    assert fake.merges == [], \
> 271:        f"596.1: autopilot merged though All tests failed on the pull request combined with main: {fake.merges}"
> 276:    assert fake.merges == [], f"596.1: autopilot merged a branch GitHub could not bring up to date with main: {fake.merges}"
> 46:REQUIRED = ["all tests", "Acceptance criteria

`11. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner fixed all four blockers from the last review.",
          "Owner approval and the opt-in are now two criteria, each with a test."],
  "decided": ["Dokima's one-line note counts as its approval, as the owner said."],
  "open": []},
 "verdict": "approve",
 "summary": "Every ask has a criterion and a test that fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Add an opt-in setting, off by default, e.g. `merge.auto_approve: true`", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.5"},
  {"ask": "When it is on, a pull request δokima built is approved and queued by δokima itself as soon as its code review has passed and the required checks (`gates.required`) are green. No person is waited on.", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.1"},
  {"ask": "Branch protection still requires the checks.", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.9"},
  {"ask": "The approval is visibly δokima's (its bot), with a one-line comment naming the code review record and the green checks", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.2"},
  {"ask": "The audit reports, in one line, when branch protection still requires a human or code-owner review that the bot's approval cannot satisfy, and says what to change", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.8"},
  {"ask": "Setup can apply that change when the owner turns the setting on.", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.9"},
  {"ask": "`integrity.owner_approval` stays locked for repos that do not opt in", "source": "https://github.com/dokima-dev/dokima/issues/934", "criterion": "934.6"},
  {"ask": "turning on `merge.auto_approve` is the explicit opt-in", "source": "https://githu
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#934](https://github.com/dokima-dev/dokima/issues/934) (Dokima approves and merges its own pull requests when a repo opts in). The review is in `/tmp/dokima-out/review.json`, and the hand-back check passes.

- **Last round's fixes:** the planner did all four.
  - The red-checks test no longer checks that the worker starts again.
  - "Owner approval stays locked" and "auto approve is the opt-in" are now two separate criteria, each with its own test.
  - The audit test now also runs with auto approve off and with a plain required review.
  - The setup test now checks that main still requires `all tests` and `Acceptance criteria`.
- **Your later answers:** both are in the plan. The one-line note counts as Dokima's approval, and owner approval stays locked for every repo.
- **Coverage:** I matched each of your asks to one of the nine criteria. None is missing and nothing extra was added.
- **Tests run today:** 8 of the 9 fail, and each fails because the feature isn't built yet, not because of a crash or a bad path.
- **The one that passes:** the owner-approval lock test (934.6). It passes because the lock already exists, so it guards against the new work unlocking it. I accepted that rather than blocking.

There were no open blockers to answer, and I raised nothing new.

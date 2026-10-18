# reviewer (plan) for #829

Run: https://github.com/dokima-dev/dokima/actions/runs/39087881211

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #829: The sandbox already holds the old copied Dokima code and workflows; a new install leaves them there, still running.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 816 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Installing Dokima removes the old copied Dokima code and workflows, so they stop running.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/816
> - https://github.com/dokima-dev/dokima/issues/258
> 
> 
> **User story:** After a new install, the sandbox holds no old Dokima code or workflows, so only the new install runs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When Dokima is installed over an old install, the old copy of Dokima's code is gone from the repo.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-829/tests/test_install.py#L161"><img src="https://ra

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; sed -n 1,260p tests/test_install.py; cat /tmp/pack/owner_words.json /tmp/pack/parent.json | head -50
```

> commit 45cbb1254760414b0256fd933a306f1e637f74dd
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 01:49:29 2026 +0000
> 
>     planner for #829 (run 39087756963)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_install.py | 79 ++++++++++++++++++++++++++++++++++++++++++++++++++-
>  1 file changed, 78 insertions(+), 1 deletion(-)
> """Tests for #813 and #829: installing adds only two Dokima files and clears old copies.
> 
> Installing is the play-through's `Sandbox.install` (dokima/playthrough.py), the one installer Dokima has. Each test
> installs this checkout of Dokima into a temp git repo standing in for the adopter's, then reads what landed there.
> The stand-in's remote is a local bare repo, so nothing leaves the machine.
> """
> import os
> import subprocess
> 
> import pytest
> import yaml
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> WORKFLOW = ".github/workflows/dokima.yml"
> SETTINGS = ".dokima/settings.yaml"
> # Fake values for every secret a Dokima run or the play-through can hold, set in the installer's environment.
> SECRETS = {"SANDBOX_TOKEN": "sandbox-secret-value-813", "GH_TOKEN": "gh-secret-value-813",
>            "CLAUDE_CODE_OAUTH_TOKEN": "claude-secret-value-813", "CLAUDE_TOKEN": "claude-token-value-813",
>            "KIMI_API_KEY": "kimi-secret-value-813", "KIMI_SIGN_IN": "kimi-sign-in-value-813",
>            "DOKIMA_APP_KEY": "app-key-value-813"}
> PUSH_KEY =

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_install.py 2>&1 | tail -30; grep -n "def install" -A60 dokima/playthrough.py | head -100; ls .github/workflows
```

> +  where {'.dokima/settings.yaml', '.github/workflows/acceptance-criteria.yml', '.github/workflows/agent.yml', '.github/workflows/assign.yml', '.github/workflows/audit.yml', '.github/workflows/autopilot.yml', ...} = files(PosixPath('/tmp/pytest-of-runner/pytest-0/test_installing_over_an_old_in1/sandbox.git'))
> FAILED tests/test_install.py::test_installing_over_an_old_install_removes_the_old_copies_of_dokimas_workflows - AssertionError: 829.2: after a new install, old Dokima workflows are still there: ['.github/workflows/acceptance-criteria.yml', '.github/workflows/agent.yml', '.github/workflows/assign.yml', '.github/workflows/audit.yml', '.github/workflows/autopilot.yml', '.github/workflows/board.yml', '.github/workflows/card.yml', '.github/workflows/commands.yml', '.github/workflows/dokima.yml', '.github/workflows/entry.yml', '.github/workflows/fix.yml', '.github/workflows/full-suite.yml', '.github/workflows/playthrough.yml', '.github/workflows/reviews.yml', '.github/workflows/testmon.yml', '.github/workflows/uptodate.yml', '.github/workflows/wiki.yml']
> assert ['.github/wor...ard.yml', ...] == ['.github/wor...s/dokima.yml']
>   
>   At index 0 diff: '.github/workflows/acceptance-criteria.yml' != '.github/workflows/dokima.yml'
>   Left contains 16 more items, first extra item: '.github/workflows/agent.yml'
>   
>   Full diff:
>     [
>   +     '.github/workflows/acceptance-criteria.yml',
>   +     '.github/workflows/agent.yml',
>   +     '.github/workflows/assign.yml',
>   +     '.github/workflow

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_install.py 2>&1 | grep -E "^FAILED|passed"; git log --oneline -S "def install" -- dokima/playthrough.py | head; 
```

> FAILED tests/test_install.py::test_installing_over_an_old_install_removes_the_old_copy_of_dokimas_code - AssertionError: 829.1: after a new install the old copy of Dokima's code is still there: ['dokima/card.py', 'dokima/icons/x.svg']
> FAILED tests/test_install.py::test_installing_over_an_old_install_keeps_the_repos_own_files - AssertionError: 829.1: the old copy of Dokima's card.py is still there
> FAILED tests/test_install.py::test_installing_over_an_old_install_removes_the_old_copies_of_dokimas_workflows - AssertionError: 829.2: after a new install, old Dokima workflows are still there: ['.github/workflows/acceptance-criteria.yml', '.github/workflows/agent.yml', '.github/workflows/assign.yml', '.github/workflows/audit.yml', '.github/workflows/autopilot.yml', '.github/workflows/board.yml', '.github/workflows/card.yml', '.github/workflows/commands.yml', '.github/workflows/dokima.yml', '.github/workflows/entry.yml', '.github/workflows/fix.yml', '.github/workflows/full-suite.yml', '.github/workflows/playthrough.yml', '.github/workflows/reviews.yml', '.github/workflows/testmon.yml', '.github/workflows/uptodate.yml', '.github/workflows/wiki.yml']
> FAILED tests/test_install.py::test_installing_over_an_old_install_keeps_the_repos_own_workflow - AssertionError: 829.2: the old copy of Dokima's card.yml is still there
> 4 failed, 4 passed in 0.54s
> d270c52 A play-through on a real sandbox repo checks the card after every step from issue to merge (#451)

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3 -- dokima/playthrough.py; c=$(git log --format=%h -S "install_files" -- dokima/playthrough.py | tail -1); echo $c; git show $c^:dokima/playthrough.py | grep -n "def install" -A30
```

> b7096b6 Installing adds only the workflow and settings (#830)
> 34d301c A plan's scope comes from its criteria's files (#693)
> 827ab8d Stop crediting the unrelated GitHub user "dokima" on commits (#568)
> d270c52
> fatal: path 'dokima/playthrough.py' exists on disk, but not in 'd270c52^'

**Agent:** Checking what the old install copied, to see if the test's fake old install matches it.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show b7096b6^:dokima/playthrough.py | grep -n "def install" -B30 -A25 | grep -nE "copy|COPIED|rel|shutil|for " 
```

> 7:138-    After each step it waits for its card runs and judges both cards. Returns 1 when the install or any step failed, else 0."""
> 14:145-    for step in STEPS:
> 25:156-                shutil.rmtree(out, ignore_errors=True)
> 34:165-    Keyed by path relative to the folder."""
> 36:167-    for top in ("dokima", os.path.join(".github", "workflows")):
> 37:168-        for d, _, names in os.walk(os.path.join(played, top)):
> 38:169-            for n in names:
> 43:174-                    files[os.path.relpath(path, played).replace(os.sep, "/")] = f.read()
> 59:190-    gh acts with GH_TOKEN (the app's key for the sandbox only); git pushes with SANDBOX_TOKEN."""
> 68:199-        self.env = {k: v for k, v in os.environ.items() if k not in ("SANDBOX_TOKEN", "PLAYED", "PLAYED_COMMIT")}
> 84:215-            for rel, data in install_files(self.played).items():
> 85:216-                path = os.path.join(self.clone, rel)
> 98:229-        """The record the played commit's code writes for a stand-in's hand-back.

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria: a new install removes the old Dokima code, and the old Dokima workflows.",
          "The planner added four tests that fake an old install and check what is left after a new one."],
  "decided": ["The repo's own files and own workflows stay unchanged."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan covers both asks, old code and old workflows removed, and its four tests fail today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The sandbox already holds the old copied Dokima code", "source": "https://github.com/dokima-dev/dokima/issues/829", "criterion": "829.1"},
  {"ask": "and workflows; a new install leaves them there, still running.", "source": "https://github.com/dokima-dev/dokima/issues/829", "criterion": "829.2"}
 ],
 "behaviors": [
  {"criterion": "829.1", "one_behavior": true, "why": "One action, install over an old install; one result, the old code is gone."},
  {"criterion": "829.2", "one_behavior": true, "why": "One action, install over an old install; one result, only the new workflow is left."}
 ],
 "edge_cases": [
  {"criterion": "829.1", "cut": [], "missing": []},
  {"criterion": "829.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_install.py::test_installing_over_an_old_install_removes_the_old_copy_of_dokimas_code", "only_its_behavior": true, "why": "Fails today listing `dokima/card.py` still on the branch after install."},
  {"test": "tests/test_install.py::test_installing_over_an_old_install_keeps_the_repos_own_files", "only_its_behavior": true, "why": "Fails code that wipes the whole repo; also needs the old code gone, so cannot pass idle."},
  {"test": "tests/test_install.py::test_installing_over_an_old_install_removes_the_old_copies_of_dokimas_workflows", "only_its_behavior": true, "why": "Fails today listing all sixteen old workflows still on the bra
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step did line 2 holds 19 words, over its cap of 15: cut 4, keep the facts

`8. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['summary']="The plan covers both asks, old code and old workflows removed; its four tests fail today for the right reason."
r['summary']="The plan covers both asks, old code and workflows removed; its four tests fail today as they should."
r['previous_step']['did']=["The planner wrote two criteria: a new install removes old Dokima code and workflows.","The planner added four tests that fake an old install, then check what remains."]
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 829 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#829](https://github.com/dokima-dev/dokima/issues/829) (a new install leaves the old Dokima copies running), and the hand-back passes both checks.

- **Both asks are covered.** Removing the old Dokima code is criterion 829.1, and removing the old Dokima workflows is 829.2. The issue's evidence line describes the bug and asks for nothing more.
- **The four new tests fail today for the right reason.** After an install, the old code and all sixteen old workflows are still in the repo. The other four tests in the file pass.
- **The tests would catch an install that deletes too much.** Two of them check that the repo's own README and its own `ci.yml` workflow stay unchanged.
- **The fake old install matches the real one.** The old installer copied the `dokima/` folder and the workflows folder (from `git show b7096b6^`), which is what the test stands in for.

I raised nothing, and no earlier blockers were open. The review is at `/tmp/dokima-out/review.json`.

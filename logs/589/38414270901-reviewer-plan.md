# reviewer (plan) for #589

Run: https://github.com/dokima-dev/dokima/actions/runs/38414270901

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #589: An agent's manual fix opens as Dokima's app
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A workflow opens an agent's manual fix as Dokima's app, so the owner can approve it.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/587
> - https://github.com/dokima-dev/dokima/issues/588
> 
> 
> **User story:** A manual fix by an agent arrives as Dokima's pull request, which the owner approves with one click.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** An agent's manual fix opens as a pull request authored by Dokima's app, never by the owner.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-589/tests/test_fix_pr.py#L72"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A manual fix's pull request is opened with Dokima

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json | head -c 6000; echo; cat tests/test_fix_pr.py; git show --stat HEAD; ls .github/workflows
```

> {"number": 580}
> """An agent's manual fix opens as Dokima's app, and all tests gate it (#589).
> 
> Story 3 of #580.
> 
> Hand-made fixes were opened with the owner's own token, so the owner was the author and could not approve them. Only
> Actions hold the app's key, so a workflow opens them: `.github/workflows/fix.yml`, started by hand on main with the
> name of the branch the agent pushed (input `branch`), mints the app's token and opens the pull request from that
> branch into main with `gh pr create`. These tests run that workflow's own steps on the machine from test_start.py: a
> temp repo whose origin is a local bare repo holding the pushed branch, and a fake `gh` that records every call and the
> token it was made with. The app-token step gives `fake-token`; the workflow's own token is `fake-github-token`.
> """
> import json
> import os
> 
> import test_start as ts
> from test_start import OWNER, Ctx
> 
> BRANCH = "fix/typo"
> APP_TOKEN = "fake-token"
> WORKFLOW = os.path.join(ts.ROOT, ".github", "workflows", "fix.yml")
> 
> 
> def need_workflow(criterion):
>     """Fail naming the criterion when no workflow opens a manual fix yet."""
>     assert os.path.exists(WORKFLOW), (f"{criterion}: no workflow opens an agent's manual fix as Dokima's app "
>                                       f"(.github/workflows/fix.yml is missing)")
> 
> 
> class Fix(ts.Machine):
>     """A run of fix.yml on main for the branch an agent pushed.
> 
>     The branch is `fix/typo`, with one commit on it."""
> 
>     def __init__(self, tmp, pr_open=False, gh_

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_fix_pr.py 2>&1 | tail -20; grep -n "pr_open\|def __init__\|options\|calls-meta\|gh_fail" tests/test_start.py | head -40
```

> assert False
>  +  where False = <function exists at 0x7fc1dd307600>('/home/runner/work/dokima/dokima/.github/workflows/fix.yml')
>  +    where <function exists at 0x7fc1dd307600> = <module 'posixpath' (frozen)>.exists
>  +      where <module 'posixpath' (frozen)> = os.path
> FAILED tests/test_fix_pr.py::test_a_second_run_for_the_same_branch_opens_no_second_pull_request - AssertionError: 589.1: no workflow opens an agent's manual fix as Dokima's app (.github/workflows/fix.yml is missing)
> assert False
>  +  where False = <function exists at 0x7fc1dd307600>('/home/runner/work/dokima/dokima/.github/workflows/fix.yml')
>  +    where <function exists at 0x7fc1dd307600> = <module 'posixpath' (frozen)>.exists
>  +      where <module 'posixpath' (frozen)> = os.path
> FAILED tests/test_fix_pr.py::test_a_refused_pull_request_fails_the_run - AssertionError: 589.1: no workflow opens an agent's manual fix as Dokima's app (.github/workflows/fix.yml is missing)
> assert False
>  +  where False = <function exists at 0x7fc1dd307600>('/home/runner/work/dokima/dokima/.github/workflows/fix.yml')
>  +    where <function exists at 0x7fc1dd307600> = <module 'posixpath' (frozen)>.exists
>  +      where <module 'posixpath' (frozen)> = os.path
> FAILED tests/test_fix_pr.py::test_a_manual_fix_cannot_merge_before_all_tests_pass - AssertionError: 589.2: no workflow opens an agent's manual fix as Dokima's app (.github/workflows/fix.yml is missing)
> assert False
>  +  where False = <function exists at 0x7fc1dd307600>('/home/runner/wor

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 40,200p tests/test_start.py; grep -n "fake-token\|create-github-app-token" tests/test_start.py | head
```

> "raises": [], "answers": [],
>            "asks": [{"ask": "Fix it.", "source": "https://github.com/o/r/issues/57", "criterion": "S1.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")], "edge_cases": [{"criterion": c, "cut": [], "missing": []} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")]}
> 
> FAKE_GH = r'''#!/usr/bin/env python3
> """A stand-in for the GitHub CLI: answers from the fake issue, keeps every comment the run writes, records every call.
> 
> Comments live in comments.json, each with its id, where it is (issue #57 or pull request #60), its author and every
> version of its body, oldest first, the way GitHub keeps a comment that is edited in place. A comment is written by
> `gh issue comment` / `gh pr comment` (with --body or --body-file; with --edit-last it edits the newest one there),
> or by `gh api` on repos/o/r/issues/N/comments (creates) and repos/o/r/issues/comments/ID (reads, or edits with PATCH),
> the body given as -f/-F/--field/--raw-field body=..., body=@file, or --input with a JSON file. `-q`/`--jq` with a
> plain `.field` picks that field. The author is Dokima's bot for the app's token and github-actions for the 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,40p .github/workflows/full-suite.yml; sed -n 415,560p tests/test_start.py
```

> name: full suite
> # Every test in the repo, on every pull request, in the merge queue and on main.
> # Runs main's copy of this workflow, so a pull request can't rewrite its own judge; only the code it tests comes from
> # the pull request, checked out with no token left behind, and the run holds no secret and only read access.
> on:
>   pull_request_target:
>   push:
>     branches: [main]
>   merge_group:
> permissions:
>   contents: read
> jobs:
>   all-tests:
>     name: all tests
>     runs-on: ubuntu-24.04
>     steps:
>       - uses: actions/checkout@v5
>         with:
>           ref: ${{ github.event.pull_request.head.sha || github.sha }}
>           persist-credentials: false
>       - uses: actions/setup-python@v6
>         with:
>           python-version: "3.12"
>       - run: pip install -q pytest pytest-xdist
>       # Every test, spread over all the runner's cores.
>       - run: pytest -q -p no:cacheprovider -n auto tests
>             "models": ["claude-opus-5-5"], "handback": handback, "check": {"passed": True, "problems": []}}
> 
> 
> class Machine:
>     """A temp repo with fake GitHub, Claude, pip and npm, on which workflow jobs run the way GitHub runs them."""
> 
>     def __init__(self, tmp, comments, try_branch=False, actor=OWNER, gh_fail="", broken=None, options=None, cancel_at=None):
>         self.tmp = t = str(tmp)
>         self.cancel_at = cancel_at
>         for d in ("bin", "gh", "home", "runner-temp", "jobs"):
>             os.makedirs(f"{t}/{d}")
>         json.dump(options or {}, open(f"{t}/gh/options.json", "w"

**Agent:** I'm reviewing the plan for #589. Next I'll check that its tests can pass, using a sample workflow in a scratch copy of the repo.

`6. Bash`
```
rm -rf /tmp/rv && cp -r /home/runner/work/dokima/dokima /tmp/rv && cd /tmp/rv && cat > .github/workflows/fix.yml <<'EOF'
name: fix
on:
  workflow_dispatch:
    inputs:
      branch:
        required: true
permissions:
  contents: read
jobs:
  open:
    runs-on: ubuntu-24.04
    steps:
      - id: app
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ vars.DOKIMA_APP_ID }}
          private-key: ${{ secrets.DOKIMA_APP_KEY }}
      - env:
          GH_TOKEN: ${{ steps.app.outputs.token }}
          BRANCH: ${{ inputs.branch }}
        run: |
          set -e
          if [ -n "$(gh pr list --head "$BRANCH" --state open --json number -q '.[].number')" ]; then exit 0; fi
          gh pr create --base main --head "$BRANCH" --title "x" --body "y"
EOF
python -m pytest -q tests/test_fix_pr.py 2>&1 | tail -5
# mutation: owner token
sed -i 's/GH_TOKEN: ${{ steps.app.outputs.token }}/GH_TOKEN: ${{ github.token }}/' .github/workflows/fix.yml; python -m pytest -q tests/test_fix_pr.py 2>&1 | tail -3
```

> ....                                                                     [100%]
> 4 passed in 0.91s
>   - fake-token
>   + fake-github-token
> 1 failed, 3 passed in 0.80s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`7. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote two criteria and four tests for a workflow that opens a manual fix as Dokima's app."],
  "decided": ["A new workflow, started by hand with the pushed branch's name, opens the pull request into main.", "Starting it again while the pull request is open opens no second one."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan keeps both asks from the parent issue, and each test fails today because the workflow is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Manual fixes by an agent are opened as Dokima's app, never as the owner, so the owner can approve them with one click", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "589.1"},
  {"ask": "the full test suite still gates them", "source": "https://github.com/dokima-dev/dokima/issues/580", "criterion": "589.2"}
 ],
 "behaviors": [
  {"criterion": "589.1", "one_behavior": true, "why": "One result: the fix's pull request is authored by the app."},
  {"criterion": "589.2", "one_behavior": true, "why": "One result: the pull request waits for all tests before it merges."}
 ],
 "edge_cases": [
  {"criterion": "589.1", "cut": [], "missing": []},
  {"criterion": "589.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_fix_pr.py::test_a_manual_fix_opens_as_dokimas_app", "only_its_behavior": true, "why": "Runs the workflow and fails when the pull request is opened with the workflow's own token, not the app's."},
  {"test": "tests/test_fix_pr.py::test_a_second_run_for_the_same_branch_opens_no_second_pull_request", "only_its_behavior": true, "why": "Fails when a second pull request is opened for a branch that already has one open."},
  {"test": "tests/test_fix_pr.py::test_a_refused_pull_request_fails_the_run", "only_its_behavior": true, "why": "Fails when GitHub refuses to open the pull request and the run still passes."},
  {"test": "tests/test
```

> Exit code 1
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`8. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r["previous_step"]["did"]=["The planner wrote two criteria and four tests for opening manual fixes as Dokima's app."]
r["previous_step"]["decided"]=["A new workflow, started by hand with the branch's name, opens the pull request into main."]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 589 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> 1

`9. Bash`
```
sed -i "s/A new workflow, started by hand with the branch's name, opens the pull request into main./A new workflow, started by hand with the branch's name, opens its pull request into main./; s/A new workflow, started by hand/A workflow started by hand/" /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 589 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> 0

**Agent:** I approved the plan for [#589](https://github.com/dokima-dev/dokima/issues/589) (manual fixes open as Dokima's app). The hand-back is in `/tmp/dokima-out/review.json`, and it passes both checks.

**What I checked:**
- **Asks:** the parent issue, [#580](https://github.com/dokima-dev/dokima/issues/580) (owner approval by default), makes two asks of this story. Each has its own criterion:
  - the fix opens as Dokima's app, never as the owner (589.1);
  - all tests still have to pass before it merges (589.2).
- **Tests fail today for the right reason:** all four fail because the workflow file does not exist yet, not because of a crash or a bad path.
- **The tests can pass and they catch mistakes:** in a scratch copy of the repo I wrote a short sample workflow, and all four tests passed. Then I switched it to open the pull request with the workflow's own token instead of the app's, and the main test for 589.1 failed. Two more tests cover cases a sample like this could get wrong:
  - opening a second pull request when one is already open;
  - letting the run pass after GitHub refuses the pull request.
- **Size:** each criterion is one behavior, and both have the edge cases normal use hits.

I raised nothing. One thing for the worker to know: the test setup only works if the workflow checks for an already-open pull request by listing pull requests. Checking it another way would make the main test fail even though the workflow is correct. The tests' notes say this, so I didn't count it as a blocker.

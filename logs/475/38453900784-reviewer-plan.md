# reviewer (plan) for #475

Run: https://github.com/dokima-dev/dokima/actions/runs/38453900784

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
> # Issue #475: When a pull request clashes with main, the planner re-plans on the old branch without main, so it cannot change a test that main added and the plan breaks.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [560], "loop": []} -->
> A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153241067) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/560
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/389
> - https://github.com/dokima-dev/dokima/issues/602
> 
> 
> **User story:** When a pull request falls behind main, its planner sees main's tests and can change them in the same round.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt=

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json | head -50; git show --stat HEAD; cat tests/test_planner_starts_with_main.py; grep -n "Starting branch" -A60 .github/workflows/agent.yml | head -120
```

> {"number": null}commit d922fa89391afa1c58c0ab514244bc406b25ec3c
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 19:18:55 2026 +0000
> 
>     planner for #475 (run 38453380822)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_planner_starts_with_main.py | 135 +++++++++++++++++++++++++++++++++
>  1 file changed, 135 insertions(+)
> """The planner starts with main merged in, so it can change tests main added (#475).
> 
> When a pull request clashes with main, its planner used to start on the old branch without main: a test main added
> was not there to change, and only the worker's later merge showed the plan broken, costing an extra round.
> 
> These tests run the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin where
> main adds tests/test_main.py after try/issue-57 split off. The planner's run is its checkout ("Starting branch"), a
> stand-in for the agent that copies what it found and changes tests/test_main.py when it is there, and the push. Then
> the worker's own "Starting branch" step runs on a fresh clone, as the next run would.
> 
> With clash=True, main and the branch both change app.py, so the branch clashes with main; with clash=False the
> branch changes only near.py and merges cleanly.
> """
> import os
> import sys
> 
> sys.path.insert(0, os.path.dirname(__file__))
> import test_start as ts  # noqa: E402
> 
> MAINS_TEST = 'def test_m():\n    """Main\'s 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | tail -30
```

> assert b.planner == "success", f"475.2: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
>             assert b.worker == "success", f"475.2: the worker's checkout after the planner failed:\n{b.tail()}"
>             got = b.workers("tests/test_main.py")
> >           assert got == PLANNERS_TEST, \
>                 (f"475.2: on a branch that {kind}, the worker started without the planner's change to the test main "
>                  f"added; tests/test_main.py is {got!r}")
> E           AssertionError: 475.2: on a branch that clashes with main, the worker started without the planner's change to the test main added; tests/test_main.py is 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
> E           assert 'def test_m()...assert True\n' == 'def test_m()... 1 + 1 == 2\n'
> E             
> E               def test_m():
> E             -     """Main's test, changed by the planner."""
> E             -     assert 1 + 1 == 2
> E             +     """Main's own test."""
> E             +     assert True
> 
> tests/test_planner_starts_with_main.py:130: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_planner_starts_with_main.py::test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added - AssertionError: 475.1: on a branch that clashes with main, the planner started without the test main added (tests/test_main.py found: None)
> assert None == 'def test_m():\n    """Main\'s own test."""\n    ass

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_\|planner" tests/test_start.py | head -60; grep -n "Push the planner's tests" -A40 .github/workflows/agent.yml | head -60
```

> 406:def planner_record(handback):
> 407:    """A passed planner record, the way the workflow writes one."""
> 408:    return {"role": "planner", "stage": None, "run_id": "1", "run": "https://github.com/o/r/actions/runs/1",
> 455:            open(f"{src}/tests/test_x.py", "w").write('def test_a():\n    """A."""\n')
> 645:                  record_comment(planner_record(SPLIT), "2026-10-07T10:10:00Z")]
> 647:STORY_PLANNED = [owner_comment("/plan", "2026-10-07T10:00:00Z"), record_comment(planner_record(STORY), "2026-10-07T10:10:00Z")]
> 652:def test_the_plan_reviewer_starts_on_a_split_with_no_try_branch(record_property, tmp_path):
> 653:    """The plan reviewer starts on an issue whose planner proposed a split, though the issue has no try branch.
> 678:def test_a_reviewed_split_stops_for_the_owner_and_files_nothing_before_work(record_property, tmp_path, monkeypatch, capsys):
> 679:    """A split goes planner, reviewer, then stops and mentions the owner; its child issues are filed only after `/work`.
> 724:def test_a_start_failure_says_why_on_the_issue_and_stops_for_the_owner(record_property, tmp_path):
> 758:def test_a_failed_command_says_why_and_stops_for_the_owner(record_property, tmp_path):
> 790:        f"176.4: the owner's /plan no longer just starts the planner with its one queued card: started={r.agent_run_started()} posted={cards}"
> 796:def test_a_start_failure_still_fails_the_run(record_property, tmp_path):
> 314:      - name: Push the planner's tests or the worker's code to try/issue-N
> 315-      

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rln "Starting branch" tests/ ; grep -rn "role=\"planner\"\|'planner'" tests/test_start.py | head; gh 2>/dev/null; sed -n 430,500p tests/test_start.py
```

> tests/test_clash.py
> tests/test_planner_starts_with_main.py
> tests/test_agent.py
> tests/test_bot_identity.py
> tests/test_worker_pr.py
> Work seamlessly with GitHub from the command line.
> 
> USAGE
>   gh <command> <subcommand> [flags]
> 
> CORE COMMANDS
>   auth:          Authenticate gh and git with GitHub
>   browse:        Open repositories, issues, pull requests, and more in the browser
>   codespace:     Connect to and manage codespaces
>   discussion:    Work with GitHub Discussions (preview)
>   gist:          Manage gists
>   issue:         Manage issues
>   org:           Manage organizations
>   pr:            Manage pull requests
>   project:       Work with GitHub Projects.
>   release:       Manage releases
>   repo:          Manage repositories
>   skill:         Install and manage agent skills (preview)
> 
> GITHUB ACTIONS COMMANDS
>   cache:         Manage GitHub Actions caches
>   run:           View details about workflow runs
>   workflow:      View details about GitHub Actions workflows
> 
> ALIAS COMMANDS
>   co:            Alias for "pr checkout"
> 
> ADDITIONAL COMMANDS
>   agent-task:    Work with agent tasks (preview)
>   alias:         Create command shortcuts
>   api:           Make an authenticated GitHub API request
>   attestation:   Work with artifact attestations
>   completion:    Generate shell completion scripts
>   config:        Manage configuration for gh
>   copilot:       Run the GitHub Copilot CLI (preview)
>   extension:     Manage gh extensions
>   gpg-key:       Manage GPG keys
>   label:         Manage labels

**Agent:** Reviewing the plan for #475: both new tests fail for the right reason; now checking whether a shortcut fix could still pass them.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt HEAD 2>&1; cd /tmp/wt; python3 - <<'EOF'
p='.github/workflows/agent.yml'
s=open(p).read()
old='            git fetch -q origin "try/issue-$N" && git checkout -q -B "try/issue-$N" FETCH_HEAD\n'
new=old+'            if [ "$ROLE" = planner ]; then git checkout -q -B "try/issue-$N" origin/main; fi\n'
assert old in s; open(p,'w').write(s.replace(old,new))
EOF
timeout 600 python -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | tail -5
```

> -     """Main's test, changed by the planner."""
>   -     assert 1 + 1 == 2
>   +     """Main's own test."""
>   +     assert True
> 1 failed, 1 passed in 1.35s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; git status --short; mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two tests that run the real branch setup with a branch behind main."],
  "decided": ["The planner starts from its branch with main merged in, and the worker keeps the planner's test change.",
              "A code file that clashes stays for the worker to resolve."],
  "open": ["The planner asks whether this fix also closes the overlapping issue 602."]},
 "verdict": "block",
 "summary": "The plan is right, but the first test passes when the planner drops its own branch and starts from main alone.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Weak test",
   "text": "The test for 475.1 passes when the planner starts from main alone and loses its branch's own tests. Smallest fix: also assert the planner still finds the branch's `tests/test_x.py`, in both the clashing and clean cases.",
   "evidence": "Adding `git checkout -B try/issue-$N origin/main` for the planner in `Starting branch` makes `test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added` pass."}
 ],
 "answers": [],
 "asks": [
  {"ask": "When a pull request clashes with main, the planner re-plans on the old branch without main", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.1"},
  {"ask": "so it cannot change a test that main added and the plan breaks. The work then needs an extra round", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.2"}
 ],
 "behaviors": [
  {"criterion": "475.1", "one_behavior": true, "why": "One result: the planner's copy holds main's new tests."},
  {"criterion": "475.2", "one_behavior": true, "why": "One result: the worker starts with the planner's version of main's test."}
 ],
 "edge_cases": [
  {"criterion": "475.1", "cut": [], "missing": ["The planner still finds its branch
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> raise 1's text holds 36 words, over its cap of 30: cut 6, keep the facts
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["summary"]="The plan is right, but its first test passes when the planner drops its branch and starts from main."
r["raises"][0]["text"]="The test for 475.1 passes when the planner starts from main alone, losing its branch's tests. Fix: also assert it finds the branch's `tests/test_x.py` in both cases."
r["previous_step"]["did"]=["The planner wrote two tests running the real branch setup behind main."]
r["previous_step"]["decided"]=["The planner starts from its branch with main merged in.","The worker starts with the planner's change to main's test.","A code file that clashes stays for the worker to resolve."]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 475 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#475](https://github.com/dokima-dev/dokima/issues/475) (the planner should start with main merged in). It goes back to the planner over one weak test. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**The weak test.** I tried a shortcut fix in a scratch copy: the planner simply starts from main and drops its own branch. The test for 475.1 still passed. That fix would lose the branch's earlier tests on every re-plan.
- **Smallest fix:** in both the clashing and the clean case, also check that the planner still finds the branch's own `tests/test_x.py`.
- The test for 475.2 caught the shortcut and failed, so it holds.

**What's sound:**
- Both of your asks map to a criterion: the planner sees main's new tests (475.1), and the worker starts with the planner's change without an extra round (475.2).
- Each criterion is one behavior with one test, and the size is fine.
- Both new tests fail today for the right reason: the planner finds no test from main, and the worker starts with main's version of the test, not the planner's.

**Still yours to answer:** the planner asks whether this fix should also close [#602](https://github.com/dokima-dev/dokima/issues/602) (the same root cause) as a duplicate. I couldn't find anything you'd written that settles it, so I left it for you. Your plain `/plan` after the planner's record didn't answer it either, and it has already queued a fresh planner run.

The scratch copy is removed and the repo is unchanged.

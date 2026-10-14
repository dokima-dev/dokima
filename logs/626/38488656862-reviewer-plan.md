# reviewer (plan) for #626

Run: https://github.com/dokima-dev/dokima/actions/runs/38488656862

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #626: The command shows what changed, and real checks run nightly
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 625 -->
> <!-- dokima-blocking: {"blocked_by": [624, 625], "blocks": [], "loop": []} -->
> Our drawing tool shows only the lines a branch changes, and its real GitHub checks run at night.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/624
> - https://github.com/dokima-dev/dokima/issues/625
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/627
> - https://github.com/dokima-dev/dokima/issues/631
> - https://github.com/dokima-dev/dokima/issues/258
> 
> 
> **User story:** We see only the lines a change moves, and real GitHub checks never slow a pull request.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The command shows which lines of a branch's drawing differ from what main's code draws.
>   - *<a href="htt

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_visuals_diff.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"
```

> """The command shows what a branch changes; real GitHub checks run only at night.
> 
> #626.
> 
> Story 3 of #584. Builds on `tools/visuals.py draw` (#624) and `preview` (#625).
> 
> 1. A new subcommand, run from the root of a checkout:
> 
>        python3 tools/visuals.py diff ISSUE --branch BRANCH --repo OWNER/NAME
> 
>    draws the issue exactly as `draw` does twice, once with main's code and once with BRANCH's, and prints only the
>    lines that differ as a unified diff: main's lines start with `-`, BRANCH's with `+`, every line both drawings share
>    is left unmarked or out. When nothing differs it prints `No line differs from main.` and exits 0. An issue GitHub
>    cannot give, or a BRANCH that does not exist, ends it with a non-zero exit and one plain message naming it, never a
>    traceback.
> 
> 2. Checks that post to or read from real GitHub (the card-gallery previews) live in `nightly/`, outside `tests/`, so
>    the all tests check (`pytest tests`, in full-suite.yml) never runs them. `.github/workflows/visuals-nightly.yml`
>    runs them on a schedule (and on Run workflow), never on a pull request, push or merge queue, with a GitHub token.
>    They call the real `gh`: when GitHub refuses, they fail and say GitHub's reason; they never skip.
> 
> 3. The tool stays ours: nothing in the `dokima/` package names it, and no workflow but the nightly one runs it.
> 
> How the tests prove it: the throwaway checkout, its `visual-test` branch and the fake GitHub of #624's tests
> (`tests/test_visuals_draw.py`) are re

`3. Bash`
```
cd /home/runner/work/dokima/dokima; ls tools nightly 2>&1; timeout 600 python3 -m pytest -q tests/test_visuals_diff.py 2>&1 | grep -E "Failed|626|passed|failed" | head -30
```

> ls: cannot access 'nightly': No such file or directory
> tools:
> visuals.py
>         Checks the branch's new lines show with `+`, main's old lines with `-`, and no line both share is marked. Proves 626.1."""
>         record_property("proves", "626.1")
> >       assert r.returncode == 0, f"626.1: comparing #{ISSUE} from visual-test with main exited {r.returncode}:\n{out}\n{r.stderr}"
> E       AssertionError: 626.1: comparing #7 from visual-test with main exited 2:
>         Compares issue 7 drawn from main with itself and checks the command says so, marks no line and exits 0. Proves 626.1."""
>         record_property("proves", "626.1")
> >       assert r.returncode == 0, f"626.1: comparing main with itself exited {r.returncode}:\n{out}\n{r.stderr}"
> E       AssertionError: 626.1: comparing main with itself exited 2:
>         issue and GitHub's reason, with no traceback. Proves 626.1."""
>         record_property("proves", "626.1")
>         assert r.returncode != 0, f"626.1: comparing an unreadable issue did not fail:\n{said}"
> >       assert "#8" in said and "HTTP 502" in said, f"626.1: the message does not name the issue and GitHub's reason:\n{said}"
> E       AssertionError: 626.1: the message does not name the issue and GitHub's reason:
>         Proves 626.1."""
>         record_property("proves", "626.1")
>         assert r.returncode != 0, f"626.1: comparing a missing branch with main did not fail:\n{said}"
> >       assert "no-such-branch" in said, f"626.1: the message does not name the missing bra

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_visuals_diff.py 2>&1 | grep -E "^E |exited 2" -A3 | head -40; grep -rln "visuals\|tools/\|nightly/" dokima .github/workflows
```

> E       AssertionError: 626.1: comparing #7 from visual-test with main exited 2:
> E         
> E         usage: tools/visuals.py [-h] {draw,preview} ...
> E         tools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)
> E         
> E       assert 2 == 0
> E        +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'diff', '7', '--bran...] {draw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)\n").returncode
> 
> tests/test_visuals_diff.py:113: AssertionError
> ________________________ test_diff_same_as_main_says_so ________________________
> --
> E       AssertionError: 626.1: comparing main with itself exited 2:
> E         
> E         usage: tools/visuals.py [-h] {draw,preview} ...
> E         tools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)
> E         
> E       assert 2 == 0
> E        +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'diff', '7', '--bran...] {draw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)\n").returncode
> 
> tests/test_visuals_diff.py:132: AssertionError
> ______________________ test_diff_unreadable_issue_says_so ______________________
> --
> E       AssertionError: 626.1: the message does not name the issue and GitHub's reason:
> E         usage: tools/visuals.py [-h] 

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the nightly test fail unless a check calls the card gallery repo.", "The planner added a test: a missing branch fails, names the branch, shows no crash."], "decided": [], "open": []},
 "verdict": "approve",
 "summary": "Both blockers are fixed; every test fails today because the feature is missing.",
 "raises": [],
 "answers": [
  {"raise": "R1", "answer": "done", "why": "The test now fails unless a logged call names the card gallery repo."},
  {"raise": "R2", "answer": "done", "why": "A new test checks a missing branch fails, names it and shows no crash."}
 ],
 "asks": [
  {"ask": "shows which lines differ from today's card", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "626.1"},
  {"ask": "Anything that posts to or reads from real GitHub (the card-gallery previews) runs nightly, not in the suite that runs on every pull request.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156300577", "criterion": "626.2"},
  {"ask": "never shipped with Dokima and never a Dokima command or feature", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "626.3"}
 ],
 "behaviors": [
  {"criterion": "626.1", "one_behavior": true, "why": "One command result: the lines that differ from main's drawing."},
  {"criterion": "626.2", "one_behavior": true, "why": "One rule: where the real GitHub checks run."},
  {"criterion": "626.3", "one_behavior": true, "why": "One rule: Dokima never names the tool."}
 ],
 "edge_cases": [
  {"criterion": "626.1", "cut": [], "missing": []},
  {"criterion": "626.2", "cut": [], "missing": []},
  {"criterion": "626.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_visuals_diff.py::test_diff_shows_changed_lines", "only_its_behavior": true, "why": "Checks added, removed and shared lines from a real branch ch
```

> Exit code 1
> answer 1 names 'R1', which no open raise has
> answer 2 names 'R2', which no open raise has

**Agent:** Running the hand-back check. It only fails because `R1` and `R2` are already closed, so I'm removing those two answers.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p));d['answers']=[];json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 626 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#626](https://github.com/dokima-dev/dokima/issues/626) (the drawing tool shows what changed, and real GitHub checks run nightly). The planner fixed both problems from my last review:

- **Weak nightly test:** the test now fails unless a nightly check actually calls GitHub on the card gallery repo. Before, any call to GitHub would have passed it.
- **Missing case:** a new test checks that a mistyped branch name fails, names the branch and doesn't crash.

I ran all seven tests on the branch. Each one fails today only because the work isn't built yet:
- The command has no `diff` option yet.
- The nightly workflow and the `nightly/` folder don't exist yet.

None fails from a crash or a bad path.

Each of the three asks from [#584](https://github.com/dokima-dev/dokima/issues/584) (the parent issue for the preview tool) has its own criterion and tests. No criterion bundles two things, and the size is fine.

My review passed the hand-back check and is saved in `/tmp/dokima-out/review.json`. The first check failed because I had answered two blockers that were already closed, so I took those answers out.

One thing for later: the plan adds a workflow file (`.github/workflows/visuals-nightly.yml`). Once it's built, that change will stop and wait for your approval before it can merge.

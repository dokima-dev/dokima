# reviewer (plan) for #475

Run: https://github.com/dokima-dev/dokima/actions/runs/38458451698

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 48
> drwxr-xr-x  3 runner runner  4096 Oct 13 19:53 .
> drwxrwxrwt 18 root   root    4096 Oct 13 19:54 ..
> drwxr-xr-x  2 runner runner  4096 Oct 13 19:53 in
> -rw-r--r--  1 runner runner 22996 Oct 13 19:53 issue.md
> -rw-r--r--  1 runner runner     2 Oct 13 19:53 open_blockers.json
> -rw-r--r--  1 runner runner    16 Oct 13 19:53 parent.json
> -rw-r--r--  1 runner runner  3932 Oct 13 19:53 plan.json
> 
> in:
> total 56
> drwxr-xr-x 2 runner runner 4096 Oct 13 19:53 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 19:53 ..
> -rw-r--r-- 1 runner runner 3381 Oct 13 19:53 01-planner.json
> -rw-r--r-- 1 runner runner 3297 Oct 13 19:53 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4569 Oct 13 19:53 03-planner.json
> -rw-r--r-- 1 runner runner 4020 Oct 13 19:53 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4419 Oct 13 19:53 05-planner.json
> -rw-r--r-- 1 runner runner 3368 Oct 13 19:53 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 1338 Oct 13 19:53 07-worker.json
> -rw-r--r-- 1 runner runner 2451 Oct 13 19:53 08-reviewer-pr.json
> -rw-r--r-- 1 runner runner 4674 Oct 13 19:53 09-planner.json
> # Issue #475: The planner starts from its branch with main merged in
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [560], "loop": []} -->
> A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/607 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" 

`2. Bash`
```
cd /tmp/pack/in; cat 06-reviewer-plan.json 08-reviewer-pr.json 09-planner.json; cd /home/runner/work/dokima/dokima; git log --oneline -3 --stat; git diff e33d4ba 8301a56 --stat
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38455900466",
>  "commit_before": "84cf6b24b94ff6088be8d3ad9067e190b0eab29e",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 32455,
>   "turns": 7,
>   "cost_usd": 0.47389899999999996,
>   "tokens_in": 342210,
>   "tokens_out": 3102
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/475/38455900466-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38455900466",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner narrowed the third criterion to a branch that merges cleanly with main.",
>     "The planner made its test also check a clashing branch keeps its own work."
>    ],
>    "decided": [
>     "A branch that clashes with main keeps its own work, for the worker to merge."
>    ],
>    "open": [
>     "Issue 602 still needs closing as a duplicate by the owner."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan covers every ask, and each test fails today because the planner never takes main.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "When a pull request clashes with main, the planner re-plans on the old branch without main",
>     "source": "https://github.com/dokima-dev/dokima/issues/475",
>     "criterion": "475.1"
>    },
>    {
>     "ask": "so it cannot change a test that main added and the plan breaks. The work then needs an extra round",
>     "source": "https://github.com/dokima-dev/dokima/issues/475",
>     "crit

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff e33d4ba 8301a56; cat tests/test_planner_starts_with_main.py
```

> diff --git a/tests/test_planner_starts_with_main.py b/tests/test_planner_starts_with_main.py
> index 6eced11..c236563 100644
> --- a/tests/test_planner_starts_with_main.py
> +++ b/tests/test_planner_starts_with_main.py
> @@ -9,7 +9,8 @@ stand-in for the agent that copies what it found and changes tests/test_main.py
>  the worker's own "Starting branch" step runs on a fresh clone, as the next run would.
>  
>  With clash=True, main and the branch both change app.py, so the branch clashes with main; with clash=False the
> -branch changes only near.py and merges cleanly.
> +branch changes only near.py and merges cleanly. With rounds=2 the planner runs twice, as a re-plan does; with
> +change=False it only looks and leaves main's test as main has it.
>  """
>  import os
>  import subprocess
> @@ -28,7 +29,7 @@ class Branch(ts.Machine):
>  
>      Main has moved on since the branch split off: it changed app.py and added tests/test_main.py."""
>  
> -    def __init__(self, tmp, clash=True):
> +    def __init__(self, tmp, clash=True, rounds=1, change=True):
>          super().__init__(tmp, [])
>          t, src = self.tmp, f"{self.tmp}/src"
>  
> @@ -48,11 +49,14 @@ class Branch(ts.Machine):
>          commit({"app.py": "a = 3\n", "tests/test_main.py": MAINS_TEST}, "main adds a test")
>          ts.sh(src, "git", "push", "-q", "origin", "main")
>          open(f"{t}/planners_test.py", "w").write(PLANNERS_TEST)
> -        # The stand-in planner: keeps what it found, then changes main's test when it can see it.
> +        # The stand-in pl

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "PLANNER_BASE" --include=*.py --include=*.yml . | head -30; git diff main...HEAD -- .github/workflows/agent.yml | head -120
```

> dokima/agent.py:1500:    if kind == "work" and os.environ.get("PLANNER_BASE"):
> dokima/agent.py:1501:        more, too_long = worker_docstring_caps(os.environ["PLANNER_BASE"])
> dokima/planner.py:596:            base = os.environ.get("PLANNER_BASE", "HEAD")
> tests/test_planner_starts_with_main.py:56:                 "git diff --name-only \"$PLANNER_BASE\" -- tests > /tmp/plans_tests.txt\n"
> tests/test_handback_check.py:57:    # A worker's or reviewer's run sets PLANNER_BASE, and the worker's check then reads the branch's docstrings (#240);
> tests/test_handback_check.py:59:    for k in ("PYTHONSAFEPATH", "PLANNER_BASE"):
> tests/test_word_caps.py:105:    monkeypatch.setenv("PLANNER_BASE", head)
> tests/test_raise_handbacks.py:123:    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE"):
> tests/test_plan_title.py:122:    env = {k: v for k, v in os.environ.items() if k not in ("STYLE_SOFT", "PACK", "PLANNER_BASE", "PLANNER_RUN_BASE")}
> tests/test_summary_caps.py:10:FILE PLAN N`, from a temp git repo whose base commit is PLANNER_BASE, as the workflow sets it for every run; the
> tests/test_summary_caps.py:38:    writes the hand-back and plan 9, runs `agent check KIND` with PLANNER_BASE at the base, and returns
> tests/test_summary_caps.py:56:        env = {**os.environ, "PYTHONPATH": ROOT, "PLANNER_BASE": base}
> tests/test_plan_check.py:68:    monkeypatch.setenv("PLANNER_BASE", git("rev-parse", "HEAD").strip())
> tests/test_agent.py:342:    assert 'PLANNER_BASE=$(git merge-base HEAD origin/main)' i

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | grep -E "475\.|passed|failed|Error" | head -20
```

> Proves 475.1.
>         record_property("proves", "475.1")
>                 assert b.planner == "success", f"475.1: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
>                     (f"475.1: on a branch that {kind}, the planner started without the test main added "
>                     (f"475.1: on a branch that {kind}, the planner started without the branch's own test "
>                     (f"475.1: on a branch that {kind}, the plan check counts the test main added as the plan's own "
> E               AssertionError: 475.1: on a branch that clashes with main, in its second planning round, the plan check counts the test main added as the plan's own (plan's tests: ['tests/test_main.py', 'tests/test_x.py'])
> tests/test_planner_starts_with_main.py:146: AssertionError
> FAILED tests/test_planner_starts_with_main.py::test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added - AssertionError: 475.1: on a branch that clashes with main, in its second planning round, the plan check counts the test main added as the plan's own (plan's tests: ['tests/test_main.py', 'tests/test_x.py'])
> 1 failed, 2 passed in 2.64s

**Agent:** Tests run: the new 475.1 check fails on the branch for the right reason. Checking the stand-in matches the real plan check.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 580,620p dokima/planner.py; git stash list | head -1; git worktree add -q /tmp/m main 2>&1|tail -1; cp tests/test_planner_starts_with_main.py /tmp/m/tests/; cd /tmp/m && timeout 600 python3 -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | grep -E "^E |passed|failed" | head
```

> repo = os.environ.get("GITHUB_REPOSITORY", "")
>     if action == "rejected":
>         path = os.path.join(out, "rejected.txt")
>         why = open(path).read().strip() if os.path.exists(path) else "the planner run failed before handing anything back"
>         run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
>         gh("issue", "comment", number, "-R", repo, "--body", f"**Plan rejected:** {why}\n\n[See the run]({run})")
>         return 0
>     try:
>         kind, result = read_output(out, number)
>         raw = result["raw"] if kind == "plan" else json.loads(result)
>         listed, bad = words.style({k: v for k, v in raw.items() if k != "summary"})
>         more, too_long = words.summary_caps(raw["summary"])
>         listed, bad = more + listed, too_long + bad
>         if not isinstance(raw.get("title"), str) or not raw["title"].strip():
>             bad.append("plan.json needs a title: a short plain name for the issue, set as its title once approved")
>         if kind == "plan":
>             base = os.environ.get("PLANNER_BASE", "HEAD")
>             files = changed_files(base)
>             paths = [p for p in files if p.startswith("tests/") and p.endswith(".py")]
>             broken = unreadable(paths)
>             if broken:
>                 raise Garbled("; ".join(broken))
>             tc = test_changes(paths, read_at(base), read_now)
>             if "declared" in result:
>                 tc = declared_labels(tc, result

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/m; grep -n "def changed_files" -A10 dokima/*.py | head -15
```

> dokima/planner.py:556:def changed_files(base):
> dokima/planner.py-557-    """Every file the planner added or changed since `base`, committed or not, ignoring git-ignored files."""
> dokima/planner.py-558-    run = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout.split("\n")
> dokima/planner.py-559-    return sorted({p for p in run("diff", "--name-only", base) + run("ls-files", "--others", "--exclude-standard") if p})
> dokima/planner.py-560-
> dokima/planner.py-561-
> dokima/planner.py-562-def gh(*args, **kw):
> dokima/planner.py-563-    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, **kw).stdout
> dokima/planner.py-564-
> dokima/planner.py-565-
> dokima/planner.py-566-def git(*args):

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner made the first check run a second planning round on both branches.",
          "The check now fails when a second round counts main's test as the plan's own."],
  "decided": ["In the check's rounds, the planner leaves main's test as main has it."],
  "open": []},
 "verdict": "approve",
 "summary": "The first check now covers a second planning round, and fails today exactly where the work falls short.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "When a pull request clashes with main, the planner re-plans on the old branch without main", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.1"},
  {"ask": "so it cannot change a test that main added and the plan breaks. The work then needs an extra round", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.2"},
  {"ask": "Yes: this fix covers both. Close #602 as a duplicate of this issue.", "source": "https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153338070", "criterion": "475.3"}],
 "behaviors": [
  {"criterion": "475.1", "one_behavior": true, "why": "One result: the planner's copy holds main's new tests, never counted as its own."},
  {"criterion": "475.2", "one_behavior": true, "why": "One result: the worker starts with the planner's change to main's test."},
  {"criterion": "475.3", "one_behavior": true, "why": "One result: a cleanly merging branch holds main's newest commit after planning."}],
 "edge_cases": [
  {"criterion": "475.1", "cut": [], "missing": []},
  {"criterion": "475.2", "cut": [], "missing": []},
  {"criterion": "475.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_planner_starts_with_main.py::test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added", "only_its_behavior": true, "why": "Fails on the branch: round two counts `tests/test_main.py` as the plan's own; fails on mai
```

> (Bash completed with no output)

**Agent:** I approved the plan; the review is in `/tmp/dokima-out/review.json`, and both hand-back checks passed.

**What changed this round:** the code review on [#607](https://github.com/dokima-dev/dokima/pull/607) (the PR for this issue) found that a second planning round on a branch that clashes with main counted main's test as one of the plan's own. The planner answered by making the check for the first criterion run two planning rounds, on both a clashing and a cleanly merging branch.

**What I checked:**
- **On this branch, which already has the worker's code:** that check fails, and for the right reason. In the second round on the clashing branch, the plan's own tests include `tests/test_main.py`, the test main added. That is exactly the bug the code review found. The other two checks pass.
- **On main:** all three checks fail because the feature is missing. The planner never sees main's test, and the worker gets main's version of it instead of the planner's change.
- **The fake planner in the test:** it lists the plan's tests the same way the real plan check in `dokima/planner.py` does (a `git diff` against the same base), so the check measures the real behavior.
- **The owner's three asks:** each still maps to one criterion. No open blockers were waiting for my answer.

Next, the worker fixes the second-round case.

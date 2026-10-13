# reviewer (plan) for #475

Run: https://github.com/dokima-dev/dokima/actions/runs/38454506785

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 40
> drwxr-xr-x  3 runner runner  4096 Oct 13 19:24 .
> drwxrwxrwt 18 root   root    4096 Oct 13 19:24 ..
> drwxr-xr-x  2 runner runner  4096 Oct 13 19:24 in
> -rw-r--r--  1 runner runner 13330 Oct 13 19:24 issue.md
> -rw-r--r--  1 runner runner     2 Oct 13 19:24 open_blockers.json
> -rw-r--r--  1 runner runner    16 Oct 13 19:24 parent.json
> -rw-r--r--  1 runner runner  3835 Oct 13 19:24 plan.json
> 
> in:
> total 24
> drwxr-xr-x 2 runner runner 4096 Oct 13 19:24 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 19:24 ..
> -rw-r--r-- 1 runner runner 3381 Oct 13 19:24 01-planner.json
> -rw-r--r-- 1 runner runner 3297 Oct 13 19:24 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4569 Oct 13 19:24 03-planner.json
> # Issue #475: When a pull request clashes with main, the planner re-plans on the old branch without main, so it cannot change a test that main added and the plan breaks.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [560], "loop": []} -->
> A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153344884) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt=

`2. Bash`
```
cd /tmp/pack; cat in/01-planner.json | python3 -m json.tool | head -80; cat in/02-reviewer-plan.json | python3 -m json.tool | head -40; cat parent.json; cd /home/runner/work/dokima/dokima; cat tests/test_planner_starts_with_main.py; git diff main --stat
```

> {
>     "role": "planner",
>     "stage": null,
>     "run_id": "38453380822",
>     "commit_before": "9fd9fcb4bbb858ce36da2df25a89517ff2929b62",
>     "started_by": "dokima-runtime[bot]",
>     "models": [
>         "claude-opus-5-5"
>     ],
>     "report": {
>         "duration_ms": 181146,
>         "turns": 20,
>         "cost_usd": 1.1382540000000003,
>         "tokens_in": 1207543,
>         "tokens_out": 16924
>     },
>     "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/475/38453380822-planner.md",
>     "run": "https://github.com/dokima-dev/dokima/actions/runs/38453380822",
>     "handback": {
>         "kind": "user_story",
>         "title": "The planner starts from its branch with main merged in",
>         "summary": "A re-plan on a branch behind main starts without main's tests, so its plan breaks one round later.",
>         "user_story": "When a pull request falls behind main, its planner sees main's tests and can change them in the same round.",
>         "acceptance_criteria": [
>             {
>                 "text": "On a branch that clashes with main, the planner finds the tests main added since the branch split off.",
>                 "words": "When a pull request clashes with main, the planner re-plans on the old branch without main",
>                 "source": "https://github.com/dokima-dev/dokima/issues/475",
>                 "edge_cases": [
>                     {
>                         "case": "A branch that merges cleanly with main also gives the planner main's tests.",
>                

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 20 gh issue view 602 2>&1 | head -40; timeout 20 curl -s https://api.github.com/repos/dokima-dev/dokima/issues/602 | head -30
```

> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}
> {
>   "url": "https://api.github.com/repos/dokima-dev/dokima/issues/602",
>   "repository_url": "https://api.github.com/repos/dokima-dev/dokima",
>   "labels_url": "https://api.github.com/repos/dokima-dev/dokima/issues/602/labels{/name}",
>   "comments_url": "https://api.github.com/repos/dokima-dev/dokima/issues/602/comments",
>   "events_url": "https://api.github.com/repos/dokima-dev/dokima/issues/602/events",
>   "html_url": "https://github.com/dokima-dev/dokima/issues/602",
>   "id": 5835869958,
>   "node_id": "I_kwDOU1yWRs8AAAABW9hPBg",
>   "number": 602,
>   "title": "A planner's branch never takes main's newest commit, so its test changes clash once main moves.",
>   "user": {
>     "login": "dokima-runtime[bot]",
>     "id": 337511017,
>     "node_id": "BOT_kgDOFB4CaQ",
>     "avatar_url": "https://avatars.githubusercontent.com/in/5180316?v=4",
>     "gravatar_id": "",
>     "url": "https://api.github.com/users/dokima-runtime%5Bbot%5D",
>     "html_url": "https://github.com/apps/dokima-runtime",
>     "followers_url": "https://api.github.com/users/dokima-runtime%5Bbot%5D/followers",
>     "following_url": "https://api.github.com/users/dokima-runtime%5Bbot%5D/following{/other_user}",
>     "gists_url": "https://api.github.com/users/dokima-runtime%5Bbot%5D/gists{/gist_id}",
>     "starred_url": "https://api.github.com/users/dokima-runtime%5Bbot%5D/starred{/owner}{/repo}",
>    

`4. Bash`
```
timeout 20 curl -s https://api.github.com/repos/dokima-dev/dokima/issues/602 | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['state'],d['body'][-3000:])"
```

> open <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [601], "blocks": [381], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/601
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/381
> 
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> A planner's branch never takes main's newest commit, so its test changes clash once main moves.
> 
> **Evidence:** `.github/workflows/agent.yml` merges `origin/main` only for the worker; `dokima/planner.py` `changed_files()` rejects a merge's non-test files.
> 
> The planner raised it and the reviewer confirmed it on #596 ([run](https://github.com/dokima-dev/dokima/actions/runs/38449394800)).
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Co

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_planner_starts_with_main.py 2>&1 | grep -E "Error|assert|475\.|passed|failed" | head -30
```

> Proves 475.1.
>         record_property("proves", "475.1")
>             assert b.planner == "success", f"475.1: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
> >           assert b.seen() == MAINS_TEST, \
>                 (f"475.1: on a branch that {kind}, the planner started without the test main added "
> E           AssertionError: 475.1: on a branch that clashes with main, the planner started without the test main added (tests/test_main.py found: None)
> E           assert None == 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
> tests/test_planner_starts_with_main.py:123: AssertionError
>         Proves 475.2.
>         record_property("proves", "475.2")
>             assert b.planner == "success", f"475.2: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
>             assert b.worker == "success", f"475.2: the worker's checkout after the planner failed:\n{b.tail()}"
> >           assert got == PLANNERS_TEST, \
>                 (f"475.2: on a branch that {kind}, the worker started without the planner's change to the test main "
> E           AssertionError: 475.2: on a branch that clashes with main, the worker started without the planner's change to the test main added; tests/test_main.py is 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
> E           assert 'def test_m()...assert True\n' == 'def test_m()... 1 + 1 == 2\n'
> E             -     assert 1 + 1 == 2
> E             +     assert True
> tests/test_planner_starts_with

**Agent:** Pinning down: all three new tests fail today for the right reason. Now checking whether the plan covers #602's second cause (the planner checker rejecting a merge's non-test files).

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def changed_files" -A30 dokima/planner.py; grep -n "name:\|id: app" .github/workflows/agent.yml | head -60
```

> 556:def changed_files(base):
> 557-    """Every file the planner added or changed since `base`, committed or not, ignoring git-ignored files."""
> 558-    run = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout.split("\n")
> 559-    return sorted({p for p in run("diff", "--name-only", base) + run("ls-files", "--others", "--exclude-standard") if p})
> 560-
> 561-
> 562-def gh(*args, **kw):
> 563-    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, **kw).stdout
> 564-
> 565-
> 566-def git(*args):
> 567-    return subprocess.run(["git", *args], capture_output=True, text=True)
> 568-
> 569-
> 570-def read_at(base):
> 571-    return lambda path: (lambda r: r.stdout if r.returncode == 0 else "")(git("show", f"{base}:{path}"))
> 572-
> 573-
> 574-def read_now(path):
> 575-    return open(path).read() if os.path.exists(path) else ""
> 576-
> 577-
> 578-def main(argv):
> 579-    action, number, out = argv[1], argv[2], argv[3]
> 580-    repo = os.environ.get("GITHUB_REPOSITORY", "")
> 581-    if action == "rejected":
> 582-        path = os.path.join(out, "rejected.txt")
> 583-        why = open(path).read().strip() if os.path.exists(path) else "the planner run failed before handing anything back"
> 584-        run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
> 585-        gh("issue", "comment", number, "-R", repo, "--body", f"**Plan rejected:** {why}\n\n[See the run]({run})")
> 586-        return

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 138,170p .github/workflows/agent.yml; sed -n 289,342p .github/workflows/agent.yml; grep -n "changed_files" -r dokima | head
```

> - name: Starting branch
>         env:
>           GH_TOKEN: ${{ github.token }}
>         run: |
>           if git ls-remote --exit-code --heads origin "try/issue-$N" >/dev/null; then
>             git fetch -q origin "try/issue-$N" && git checkout -q -B "try/issue-$N" FETCH_HEAD
>             # A worker's branch that clashes with main still starts: the merge is committed with its conflict markers,
>             # the clashed files are listed for the fence, and the worker resolves them. Main's changes are in BASE.
>             if [ "$ROLE" = worker ] && ! git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" merge -q --no-edit origin/main; then
>               git diff --name-only --diff-filter=U > /tmp/clashed.txt
>               if [ ! -s /tmp/clashed.txt ]; then
>                 echo "Merging main into try/issue-$N failed with no clashed file to resolve." > /tmp/why.txt
>                 echo "::error title=Merge failed::$(cat /tmp/why.txt)"; exit 1
>               fi
>               git add -A && git -c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com" commit -q --no-edit
>               echo "::notice title=Clash with main::the worker resolves $(paste -sd, /tmp/clashed.txt)"
>             fi
>           elif [ "$ROLE" = planner ] || [ "$STAGE" = plan ]; then
>             # A plan review needs no branch: a split never makes one, so it reviews from main.
>             git checkout -q -B "try/issue-

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 588,625p dokima/planner.py; sed -n 1515,1545p dokima/agent.py; grep -n "CHECK" .github/workflows/agent.yml | head
```

> kind, result = read_output(out, number)
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
>                 tc = declared_labels(tc, result["declared"])
>             # Only what the planner changed in this run counts against "tests only": on a re-plan the branch may
>             # already hold the worker's code, which is not the planner's doing.
>             run_base = os.environ.get("PLANNER_RUN_BASE")
>             own = changed_files(run_base) if run_base else files
>             bad = problems(number, result, own, tc, result.get("declared")) + bad
>             more, too_long = docstring_caps(paths, read_at(base), read_now)
>             listed, bad = listed + more, ba

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "duplicate" dokima/*.py | head; cat /tmp/pack/in/03-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:1500])"
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38454127526",
>  "commit_before": "d922fa89391afa1c58c0ab514244bc406b25ec3c",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 100981,
>   "turns": 13,
>   "cost_usd": 0.7166558,
>   "tokens_in": 703246,
>   "tokens_out": 9217
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/475/38454127526-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38454127526",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153344884"
> }

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner made the first test also check the branch's own test.",
          "The planner added a third criterion and test from the owner's answer."],
  "decided": ["After a planner run, its branch holds main's newest commit.",
              "This fix covers the overlapping issue 602 too."],
  "open": ["The planner asks whether the owner closes issue 602 as a duplicate."]},
 "verdict": "block",
 "summary": "The third promise says every branch takes main, but a clashing branch cannot, and its test checks only a clean one.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "475.3 too wide",
   "text": "475.3 promises every planner branch holds main's newest commit, but 475.2 needs a clashing branch to still clash for the worker, so both cannot hold. Its test checks only a clean branch. Fix: limit 475.3 to a branch that merges cleanly with main.",
   "evidence": "`test_the_planners_change_to_a_test_main_added_reaches_the_worker` asserts `app.py` in `clashed()`; `Starting branch` writes `/tmp/clashed.txt` only when the merge fails. `test_a_planner_run_brings_its_branch_up_to_mains_newest_commit` uses `clash=False` only."}
 ],
 "answers": [],
 "asks": [
  {"ask": "When a pull request clashes with main, the planner re-plans on the old branch without main", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.1"},
  {"ask": "so it cannot change a test that main added and the plan breaks. The work then needs an extra round", "source": "https://github.com/dokima-dev/dokima/issues/475", "criterion": "475.2"},
  {"ask": "Yes: this fix covers both. Close #602 as a duplicate of this issue.", "source": "https://github.com/dokima-dev/dokima/issues/475#issuecomment-6153338070", "criterion": "475.3"}
 ],
 "behaviors": [
  {"criterion": "475.1", "one_behavior": true, "why": "One result: the planner's copy holds main's added tests."},
  {"criterion"
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)
> raise 1's text holds 43 words, over its cap of 30: cut 13, keep the facts
> rc=1

`11. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d["summary"]="The third promise says every branch takes main, but a clashing branch cannot, and its test checks a clean one."
d["summary"]="The third promise covers every branch, but a clashing branch cannot take main, and its test checks only clean."
d["raises"][0]["text"]="475.3 says every planner branch holds main's newest commit, but 475.2 needs a clashing branch to still clash for the worker. Fix: limit 475.3 to a cleanly merging branch."
json.dump(d,open(p,"w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 475 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`12. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d["summary"]="The third promise covers every branch, but a branch that clashes with main cannot take it."
json.dump(d,open(p,"w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 475 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I blocked the plan for [#475](https://github.com/dokima-dev/dokima/issues/475) (planner starts without main's tests) and sent it back to the planner with one blocker. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**The blocker (criterion 475.3):** The third promise, added from your answer about [#602](https://github.com/dokima-dev/dokima/issues/602) (planner's branch never takes main's newest commit), says that after every planner run, its branch holds main's newest commit.
- That can't be true for a branch that clashes with main. The second promise needs that branch to still clash, so the worker resolves the clashing code file. The worker only gets that list when its own merge of main fails.
- The test for 475.3 only tries a branch that merges cleanly, so the clashing case has no proof.
- **Smallest fix:** limit 475.3 to a branch that merges cleanly with main.

**What passed:**
- I ran all three new tests. Each fails today because the feature is missing, not because the test is broken.
- My earlier blocker is fixed: the first test now also checks that the planner still finds the branch's own test.
- Every ask from your issue and comment maps to a criterion. Size is fine.

**Waiting on you:** The planner asks whether you will close [#602](https://github.com/dokima-dev/dokima/issues/602) as a duplicate yourself, since no agent can close an issue. I left that question to you. Your comment says to close it, but not who should, so autopilot can't settle it for you.

# reviewer (plan) for #596

Run: https://github.com/dokima-dev/dokima/actions/runs/38448300882

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #596: Merge gate tests the combined code, then the owner approves
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 595 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [597], "loop": []} -->
> After code review, all tests run on the pull request with the newest main before anyone approves or merges.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/597
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/595
> - https://github.com/dokima-dev/dokima/issues/378
> 
> 
> **User story:** A pull request merges only once all tests pass on it with the newest main, and the owner approves last.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A pull request merges only after all tests pass on it combined with the newest main.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-596/tests/test_merge_gate.py#L242"><img src="http

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cd /home/runner/work/dokima/dokima; git diff main --stat; wc -l tests/test_merge_gate.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38446474525",
>  "commit_before": "f27443c740ee6af832572caca2768a7164c9f97c",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 4457,
>   "turns": 2,
>   "cost_usd": 1.0053045999999999,
>   "tokens_in": 157850,
>   "tokens_out": 324
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/596/38446474525-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38446474525",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Planned three criteria: the merge gate, sending red work back, and asking approval last.",
>     "Wrote three new tests and changed six older ones to fit the gate."
>    ],
>    "decided": [
>     "A branch behind main is brought up to date before its tests are judged.",
>     "Off autopilot, the owner is asked to approve once the gate passes."
>    ],
>    "open": [
>     "Raised two problems outside this issue: stale owner merges and unlimited gate rounds."
>    ]
>   },
>   "verdict": "block",
>   "summary": "One check is too weak: asking the owner while tests still run passes it today.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "596.3 weak check",
>     "text": "For 596.3, the still-running case passes today though the owner is told to merge. Also fail when the Next line says to merge.",
>     "evidence": "`test_merge_gate.py` line 350: today's Next reads 'The work is approved. Merge the pull request', which `\\bapprov

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3 main; git diff $(git merge-base main HEAD) --stat; git diff 507df86..9be16aa --stat | tail -3
```

> 10c8ac3 Autopilot only tries to merge; GitHub decides (#592)
> 9be16aa An agent's manual fix opens as Dokima's app (#590)
> 507df86 The planner names the issue: its hand-back carries a title that code sets on approval (#576)
>  tests/test_automerge.py        |  36 +++--
>  tests/test_autopilot_checks.py |   4 +
>  tests/test_merge_approval.py   |  16 +-
>  tests/test_merge_gate.py       | 360 +++++++++++++++++++++++++++++++++++++++++
>  tests/test_required_checks.py  |   5 +-
>  5 files changed, 405 insertions(+), 16 deletions(-)
>  .github/workflows/fix.yml |  38 +++++++++++++
>  tests/test_fix_pr.py      | 136 ++++++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 174 insertions(+)

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat main | head -30; git merge-tree --write-tree main HEAD >/dev/null && echo CLEAN || git merge-tree --write-tree --name-only main HEAD
```

> Exit code 1
> commit 10c8ac39bc135205f6ec890d001e5c78989451ad
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 17:31:17 2026 +0000
> 
>     Autopilot only tries to merge; GitHub decides (#592)
>     
>     * planner for #587 (run 38413800739)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * worker for #587 (run 38423032531)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     ---------
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  AGENTS.md                    |   2 +-
>  dokima/agent.py              |  54 +++++----
>  tests/test_automerge.py      |  17 ++-
>  tests/test_merge_approval.py | 270 ++++++++++++++++++++++---------------------
>  4 files changed, 181 insertions(+), 162 deletions(-)
> 26e026be6bb1117d2eae9aef2f08a0a0c90ed666
> tests/test_automerge.py
> tests/test_merge_approval.py
> 
> Auto-merging tests/test_automerge.py
> CONFLICT (content): Merge conflict in tests/test_automerge.py
> Auto-merging tests/test_merge_approval.py
> CONFLICT (content): Merge conflict in tests/test_merge_approval.py

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_merge_gate.py 2>&1 | tail -30
```

> fake = FakeGitHub({OLD: green(OLD), NEW: green(NEW)}, behind=True)
>         r = decide(tmp_path, monkeypatch, capsys, fake, "passed")
>         assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
> >       assert printed(r) == "stop" and APPROVE_ASK.search(r[1]) and f"@{OWNER}" in r[1], \
>             f"596.3: the merge gate passed, and the owner was not asked to approve: printed {printed(r)!r}, Next {r[1]!r}"
> E       AssertionError: 596.3: the merge gate passed, and the owner was not asked to approve: printed 'stop', Next '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.'
> E       assert ('stop' == 'stop'
> E         
> E           stop and None)
> E        +  where None = <built-in method search of re.Pattern object at 0x7f47ce3d7c60>('**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.')
> E        +    where <built-in method search of re.Pattern object at 0x7f47ce3d7c60> = re.compile('\\bapprove\\b', re.IGNORECASE).search
> 
> tests/test_merge_gate.py:345: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_merge_gate.py::test_autopilot_merges_only_the_head_tested_with_the_newest_main - AssertionError: 596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: merges=[{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned

**Agent:** I'm checking the plan's tests against main, which moved after the plan was written (#592 merged).

`6. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt main 2>&1|tail -1; cp tests/test_merge_gate.py /tmp/mainwt/tests/; cd /tmp/mainwt; timeout 600 python3 -m pytest -q tests/test_merge_gate.py 2>&1 | grep -E "^(FAILED|ERROR|E  )|passed|failed" | head -20
```

> """Autopilot merges only once all tests passed with main's newest commit.
>         The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
>         date, and merge only the new head, once every required check passed there; today it merges the old head, never
>         tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
>         assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
> E       AssertionError: 596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: merges=[{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}], branch updates asked at []; it should merge b2b2b2b only
> E       assert ([{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}] and False)
> E        +  where [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}] = <test_merge_gate.FakeGitHub object at 0x7f19adbbee10>.merges
> E        +  and   False = all(<generator object test_autopilot_merges_only_the_head_tested_with_the_newest_main.<locals>.<genexpr> at 0x7f19add73ac0>)
>         The code review approved #60, off autopilot, and All tests failed on its head, which holds main's newest commit.
>         assert r[3] is None, f"596.2: deciding what follows the code review fai

`7. Bash`
```
cd /home/runner/work/dokima/dokima; B=$(git merge-base main HEAD); git diff $B HEAD -- tests/test_automerge.py tests/test_merge_approval.py; echo ======MAIN; git diff $B main -- tests/test_automerge.py | head -80
```

> diff --git a/tests/test_automerge.py b/tests/test_automerge.py
> index 56584ce..9f55fae 100644
> --- a/tests/test_automerge.py
> +++ b/tests/test_automerge.py
> @@ -18,6 +18,8 @@ pull requests, their checks and merging. It keeps them in prs.json, one entry pe
>    - `gh api repos/o/r/pulls/N` (head.sha, head.ref, state, merged, mergeable), `.../pulls/N/files`,
>      `.../pulls/N/comments` (no line notes), `repos/o/r/commits/SHA/check-runs`, `.../commits/SHA/status` and
>      `.../commits/SHA/statuses` (SHA may also be the branch name), each with or without --paginate;
> +  - `gh api repos/o/r/compare/main...HEAD` (HEAD the head commit or the branch): `behind_by` 0, as for a branch that
> +    holds main's newest commit, or 1 when the test sets "behind" on the pull request (#596);
>    - `gh api repos/o/r/branches/BRANCH/protection[/required_status_checks]`: the branch rule, requiring every check
>      of the pull request the last call about one named, so each of its checks still judges its merge (#561);
>    - `gh pr comment N` and `gh api repos/o/r/issues/N/comments` for a pull request N write on that pull request;
> @@ -305,6 +307,18 @@ if m_rule or m_branch:
>      else:
>          pick(inner if m_rule.group(2) else {"required_status_checks": inner})
>      sys.exit(0)
> +m_cmp = next((re.fullmatch(r"/?repos/o/r/compare/(?:refs/heads/)?main\.\.\.?(.+)", x.split("?")[0]) for x in a[1:]
> +              if "/compare/" in x), None) if a[:1] == ["api"] else None
> +if m_cmp:
> +    # Whether the branch holds main

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,60p tests/test_merge_gate.py; sed -n 230,359p tests/test_merge_gate.py
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
> #60, built for issue #57 from `try/issue-57`, against a fake GitHub in memory that stands in for `dokima.agent.gh`:
> 
> - the issue, its records (plan, plan review, the owner's `/work`, the worker's record) and its `autopilot` label,
>   through `gh issue view` and `gh api repos/o/r/issues/57`;
> - the pull request through `gh pr list`, `gh pr view` (any `--json` fields) and `gh api repos/o/r/pulls/60`, its
>   files (`dokima/x.py`), and GraphQL's merge state;
> - main's branch rule, requiring `all tests` and `Acceptance criteria`, through `gh api repos/o/r/branches/main`;
> - a branch behind main: `gh api repos/o/r/compare/main...X` answers `behind_by` 1, the REST pull request's
>   `mergeable_state` is "behind" and GraphQL's `mer

`9. Bash`
```
cd /tmp/mainwt; git -C /home/runner/work/dokima/dokima show HEAD:tests/test_automerge.py > tests/test_automerge.py; timeout 900 python3 -m pytest -q tests/test_automerge.py -k "refused_merge" 2>&1 | grep -E "^E  |passed|failed" | head -8
```

> E       AssertionError: 212.3 (branch protection): pull request #60 was merged though it must wait: at a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1
> E       assert 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1' is None
> E        +  where 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1' = merged('60')
> E        +    where merged = <test_automerge.Review object at 0x7f9b4a83d6a0>.merged
> 1 failed, 7 deselected in 7.54s
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Found one real problem: the plan was written on an older main, and one of its test changes cannot pass on main as it is now. Writing the review.

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainwt; mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner made the still-running and failed cases also fail when the owner is told to merge."],
  "decided": [],
  "open": ["The plan's test changes were written before main took the rewritten autopilot merge."]},
 "verdict": "block",
 "summary": "The plan's changed tests predate main's newest autopilot merge change, and one fails on main for that reason.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Stale test base",
   "text": "The plan was written on main before #592 merged. Its `test_a_refused_merge_stops_for_the_owner_and_says_why` brings back the branch protection case #592 removed, so it fails on main whatever the worker builds. Redo the test changes on main.",
   "evidence": "`git merge-tree main HEAD` conflicts in `tests/test_automerge.py` and `tests/test_merge_approval.py`; on main that test fails: '212.3 (branch protection): pull request #60 was merged'."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Merge gate: runs the full test suite on the combined code and merges if green", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.1"},
  {"ask": "if not, the work goes back to the worker", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.2"},
  {"ask": "each step starts only after the one before passes", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.3"}
 ],
 "behaviors": [
  {"criterion": "596.1", "one_behavior": true, "why": "One result: a merge happens only after tests pass with the newest main."},
  {"criterion": "596.2", "one_behavior": true, "why": "One result: a failing test starts the worker again."},
  {"criterion": "596.3", "one_behavior": true, "why": "One result: the approval ask comes only after the 
```

> Exit code 1
> raise 1's text holds 34 words, over its cap of 30: cut 4, keep the facts
> raise 1's evidence holds 22 words, over its cap of 20: cut 2, keep the facts
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["The planner made the still-running and failed cases fail when the owner is told to merge."[:0] or "The still-running and failed cases now also fail if the owner is told to merge."]
r=d["raises"][0]
r["text"]="The plan predates #592. Its `test_a_refused_merge_stops_for_the_owner_and_says_why` restores the branch protection case #592 removed, so it fails on main regardless. Redo the test changes on main."
r["evidence"]="`git merge-tree main HEAD` conflicts in `tests/test_automerge.py` and `tests/test_merge_approval.py`; on main: '212.3 (branch protection): pull request #60 was merged'."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 596 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for [#596](https://github.com/dokima-dev/dokima/issues/596) (merge gate tests the combined code, then the owner approves), with one blocker for the planner.

**Why it's blocked:** the plan was written on an older copy of main. Main has since taken [#592](https://github.com/dokima-dev/dokima/pull/592) (autopilot only tries to merge; GitHub decides), which changed two of the test files this plan also changes.
- Bringing the plan's branch up to date with main now clashes in `tests/test_automerge.py` and `tests/test_merge_approval.py`.
- The plan's version of `test_a_refused_merge_stops_for_the_owner_and_says_why` brings back a "branch protection" case that #592 removed on purpose. Run against main's code, it fails with "212.3 (branch protection): pull request #60 was merged". That failure comes from #592, not from this issue, so it would fail however good the worker's build was.
- The fix: the planner redoes its test changes on top of today's main.

**What is fine:**
- My earlier blocker (R1) is done. The "still running" and "failed" cases now also fail when the owner is told to merge too early.
- All three new tests in `tests/test_merge_gate.py` fail for the right reason, both on the plan's branch and on today's main.
- Every ask in the owner's comment on [#582](https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718) (the parent issue) maps to a criterion. Each criterion is one behavior, and the size is ok.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

# reviewer (plan) for #596

Run: https://github.com/dokima-dev/dokima/actions/runs/38449394800

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 52
> drwxr-xr-x  3 runner runner  4096 Oct 13 18:46 .
> drwxrwxrwt 18 root   root    4096 Oct 13 18:46 ..
> drwxr-xr-x  2 runner runner  4096 Oct 13 18:46 in
> -rw-r--r--  1 runner runner 20840 Oct 13 18:46 issue.md
> -rw-r--r--  1 runner runner   393 Oct 13 18:46 open_blockers.json
> -rw-r--r--  1 runner runner    15 Oct 13 18:46 parent.json
> -rw-r--r--  1 runner runner  5217 Oct 13 18:46 plan.json
> 
> in:
> total 40
> drwxr-xr-x 2 runner runner 4096 Oct 13 18:46 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 18:46 ..
> -rw-r--r-- 1 runner runner 5945 Oct 13 18:46 01-planner.json
> -rw-r--r-- 1 runner runner 4023 Oct 13 18:46 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5384 Oct 13 18:46 03-planner.json
> -rw-r--r-- 1 runner runner 3614 Oct 13 18:46 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5979 Oct 13 18:46 05-planner.json
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="rel

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/04-reviewer-plan.json | head -80; git log --oneline -3 main; git merge-tree --write-tree main HEAD >/dev/null && echo NOCONFLICT; git diff main...HEAD --stat; grep -n "agent.yml\|origin/main" .github/workflows/agent.yml | head
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38448300882",
>  "commit_before": "a68cf0be5489827609386bcd3cdd8fbd2f28317f",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 69840,
>   "turns": 12,
>   "cost_usd": 0.6243566,
>   "tokens_in": 605064,
>   "tokens_out": 5188
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/596/38448300882-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38448300882",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The still-running and failed cases now also fail if the owner is told to merge."
>    ],
>    "decided": [],
>    "open": [
>     "The plan's test changes were written before main took the rewritten autopilot merge."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan's changed tests predate main's newest autopilot merge change, and one fails on main for that reason.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Stale test base",
>     "text": "The plan predates #592. Its `test_a_refused_merge_stops_for_the_owner_and_says_why` restores the branch protection case #592 removed, so it fails on main regardless. Redo the test changes on main.",
>     "evidence": "`git merge-tree main HEAD` conflicts in `tests/test_automerge.py` and `tests/test_merge_approval.py`; on main: '212.3 (branch protection): pull request #60 was merged'.",
>     "raised_by": "reviewer",
>     "id": "R2"
>    }
>   ],
>   "answers": [],
>   "asks": [
>    {

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git merge-tree --write-tree --name-only main HEAD; echo rc=$?; git diff main HEAD --stat -- tests dokima AGENTS.md
```

> 730e0312d2019c3d279250df4c3ce1f3fea5dd65
> tests/test_automerge.py
> tests/test_merge_approval.py
> 
> Auto-merging tests/test_automerge.py
> CONFLICT (content): Merge conflict in tests/test_automerge.py
> Auto-merging tests/test_merge_approval.py
> CONFLICT (content): Merge conflict in tests/test_merge_approval.py
> rc=1
>  AGENTS.md                      |   2 +-
>  dokima/agent.py                |  54 +++----
>  tests/test_automerge.py        |  38 +++--
>  tests/test_autopilot_checks.py |   4 +
>  tests/test_merge_approval.py   |  19 ++-
>  tests/test_merge_gate.py       | 360 +++++++++++++++++++++++++++++++++++++++++
>  tests/test_required_checks.py  |   5 +-
>  7 files changed, 430 insertions(+), 52 deletions(-)

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main HEAD -- tests/test_automerge.py tests/test_merge_approval.py tests/test_autopilot_checks.py tests/test_required_checks.py; sed -n 140,165p .github/workflows/agent.yml
```

> diff --git a/tests/test_automerge.py b/tests/test_automerge.py
> index 5925644..9bed774 100644
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

`5. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/wt; git worktree add -q /tmp/wt main 2>&1; cd /tmp/wt && git checkout HEAD@{0} 2>/dev/null; git -C /tmp/wt checkout 30013b0 -- tests/test_merge_gate.py tests/test_automerge.py tests/test_merge_approval.py tests/test_autopilot_checks.py tests/test_required_checks.py && cd /tmp/wt && timeout 900 python3 -m pytest -q -x --no-header -p no:cacheprovider tests/test_merge_gate.py 2>&1 | tail -40
```

> F
> =================================== FAILURES ===================================
> _______ test_autopilot_merges_only_the_head_tested_with_the_newest_main ________
> 
> record_property = <function record_property.<locals>.append_property at 0x7f0f785bf1a0>
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_autopilot_merges_only_the0')
> monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7f0f7882ba70>
> capsys = <_pytest.capture.CaptureFixture object at 0x7f0f7882b830>
> 
>     def test_autopilot_merges_only_the_head_tested_with_the_newest_main(record_property, tmp_path, monkeypatch, capsys):
>         """Autopilot merges only once all tests passed with main's newest commit.
>     
>         Proves 596.1.
>         The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
>         date, and merge only the new head, once every required check passed there; today it merges the old head, never
>         tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
>         one whose new head's checks never finish within the wait must not merge, one GitHub refuses to bring up to date
>         must not merge and must stop for the owner with GitHub's reason, `/autopilot start`'s merge (`automerge`) must not
>         take the old head of a branch behind main either, and one already up to date and green must merge as it is, so
>         the gate is not just "never merge"."""
>         record_property("

**Agent:** Checking the plan's new tests against main's newest code; the first fails for the right reason. Running the rest now.

`6. Bash`
```
cd /tmp/wt && timeout 1200 python3 -m pytest -q --no-header -p no:cacheprovider tests/test_merge_gate.py tests/test_automerge.py tests/test_merge_approval.py tests/test_autopilot_checks.py tests/test_required_checks.py 2>&1 | grep -E "^(FAILED|ERROR|E  +AssertionError)|passed|failed" | cut -c1-400
```

> """Autopilot merges only once all tests passed with main's newest commit.
>         The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
>         date, and merge only the new head, once every required check passed there; today it merges the old head, never
>         tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
>         assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
> E       AssertionError: 596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: merges=[{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}], branch updates asked at []; it should merge b2b2b2b only
>         The code review approved #60, off autopilot, and All tests failed on its head, which holds main's newest commit.
>         assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
>             f"596.2: All tests failed at the merge gate, and the run printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})"
> E       AssertionError: 596.2: All tests failed at the merge gate, and the run printed 'stop', not 'start worker' (Next: '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.')
> _____ test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed ______
>     def test_t

`7. Bash`
```
cd /tmp/wt; sed -n 325,365p tests/test_merge_gate.py; sed -n 80,140p /tmp/pack/in/04-reviewer-plan.json
```

> assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
>     assert printed(r) == "start worker", \
>         (f"596.2: Acceptance criteria failed on the pull request combined with main, on autopilot, and the run "
>          f"printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})")
>     assert fake.merges == [], f"596.2: autopilot merged a pull request whose test failed at the merge gate: {fake.merges}"
> 
> 
> def test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed(record_property, tmp_path, monkeypatch, capsys):
>     """The owner is asked to approve only once the merge gate passed.
> 
>     Proves 596.3.
>     Off autopilot, the code review approved #60. With every check green on the head combined with main, the run must
>     stop for the owner with a Next line asking them to approve, and show Needs you; today its Next line only says to
>     merge. With the checks on the combined head still running past the wait, its Next line must neither ask them to
>     approve nor tell them to merge. With All tests failed on the combined head, it must neither ask them to approve,
>     tell them to merge, nor show Needs you."""
>     record_property("proves", "596.3")
>     fake = FakeGitHub({OLD: green(OLD), NEW: green(NEW)}, behind=True)
>     r = decide(tmp_path, monkeypatch, capsys, fake, "passed")
>     assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
>     assert printed(r) == "stop" and APPROVE_ASK.search(r[1]) and f"@{OWNER}" i

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner redid its changed tests on main's newest tests, keeping the removed branch protection case out."],
  "decided": [],
  "open": ["The branch still clashes with main in two test files; the worker resolves that when it starts."]},
 "verdict": "approve",
 "summary": "The plan carries all three asks, and each new test fails on main's newest code for the missing feature.",
 "raises": [],
 "answers": [
  {"raise": "P3", "answer": "done", "why": "Confirmed: only the worker's run takes main's newest commit, so a planner's tests can clash. Worth its own issue."}
 ],
 "asks": [
  {"ask": "Merge gate: runs the full test suite on the combined code and merges if green", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.1"},
  {"ask": "if not, the work goes back to the worker", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.2"},
  {"ask": "each step starts only after the one before passes", "source": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718", "criterion": "596.3"}
 ],
 "behaviors": [
  {"criterion": "596.1", "one_behavior": true, "why": "One result: a merge happens only after tests pass with the newest main."},
  {"criterion": "596.2", "one_behavior": true, "why": "One result: a failing test starts the worker again."},
  {"criterion": "596.3", "one_behavior": true, "why": "One result: the approval ask comes only after the gate passes."}
 ],
 "edge_cases": [
  {"criterion": "596.1", "cut": [], "missing": []},
  {"criterion": "596.2", "cut": [], "missing": []},
  {"criterion": "596.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_merge_gate.py::test_autopilot_merges_only_the_head_tested_with_the_newest_main", "only_its_behavior": true, "why": "C
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step open line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["The planner redid its changed tests on main's newest tests, without the removed case."]
d["previous_step"]["open"]=["The branch still clashes with main in two test files; the worker resolves it."]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 596 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#596](https://github.com/dokima-dev/dokima/issues/596) (merge gate tests the combined code, then the owner approves). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's blocker is fixed.** The planner's changed tests now start from main's newest tests, and the case that [#592](https://github.com/dokima-dev/dokima/issues/592) (autopilot only tries to merge) removed stays removed.
- **The new tests fail on today's code because the feature is missing.** I ran them against main's newest code with the plan's test files added:
  - **Merge after tests pass with the newest main:** autopilot merges the old head, which never ran with main.
  - **A failed test sends the work back to the worker:** today the run stops instead.
  - **The owner is asked to approve only after the gate passes:** today the next step tells the owner to merge.
  - The changed test about the owner waiting off autopilot also fails today for the right reason. The other 15 tests in those files pass.
- **The plan covers all three things the owner asked for.** Each is one behavior with its own test, and the size is fine.
- **I confirmed the planner's new raise.** Only the worker's run brings in main's newest commit, so a planner's test changes can clash with main. That's worth its own issue.

The branch still clashes with main in `tests/test_automerge.py` and `tests/test_merge_approval.py`. The two sides changed the same lines; the test content itself matches main plus the plan's changes. The worker's setup carries on through such a clash and has the worker resolve it, so I didn't block on it.

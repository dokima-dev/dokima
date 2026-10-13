# reviewer (plan) for #596

Run: https://github.com/dokima-dev/dokima/actions/runs/38446474525

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
> # Issue #596: Merge gate tests the combined code, then the owner approves
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 595 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [597], "loop": []} -->
> After code review, all tests run on the pull request with the newest main before anyone approves or merges.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/587
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
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('parent.json'));print(list(d.keys()) if isinstance(d,dict) else type(d))"; head -c 6000 parent.json; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps(d.get('verdict', d.get('check')),indent=1)[:2000])"
```

> ['number']
> {"number": 582}
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "passed": true,
>  "problems": []
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(d['report'][:3000] if isinstance(d['report'],str) else json.dumps(d['report'])[:3000]); print(type(d['log']), str(d['log'])[:500])"; grep -o "6149288718.\{0,300\}" in/01-planner.json | head
```

> {"duration_ms": 3069685, "turns": 59, "cost_usd": 3.8604878000000005, "tokens_in": 7130066, "tokens_out": 52059}
> <class 'str'> https://github.com/dokima-dev/dokima/blob/logs/logs/596/38439481446-planner.md
> 6149288718",
> 6149288718",
> 6149288718",
> Shell cwd was reset to /home/runner/work/dokima/dokima

`4. Bash`
```
curl -s -m 20 https://api.github.com/repos/dokima-dev/dokima/issues/comments/6149288718 | head -c 4000
```

> {
>   "url": "https://api.github.com/repos/dokima-dev/dokima/issues/comments/6149288718",
>   "html_url": "https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718",
>   "issue_url": "https://api.github.com/repos/dokima-dev/dokima/issues/582",
>   "id": 6149288718,
>   "node_id": "IC_kwDOU1yWRs8AAAABboazDg",
>   "user": {
>     "login": "RezaSoleymanifar",
>     "id": 34189616,
>     "node_id": "MDQ6VXNlcjM0MTg5NjE2",
>     "avatar_url": "https://avatars.githubusercontent.com/u/34189616?u=4add81f4c4e41c9c9f7a2aa432cffa96eddd5d0b&v=4",
>     "gravatar_id": "",
>     "url": "https://api.github.com/users/RezaSoleymanifar",
>     "html_url": "https://github.com/RezaSoleymanifar",
>     "followers_url": "https://api.github.com/users/RezaSoleymanifar/followers",
>     "following_url": "https://api.github.com/users/RezaSoleymanifar/following{/other_user}",
>     "gists_url": "https://api.github.com/users/RezaSoleymanifar/gists{/gist_id}",
>     "starred_url": "https://api.github.com/users/RezaSoleymanifar/starred{/owner}{/repo}",
>     "subscriptions_url": "https://api.github.com/users/RezaSoleymanifar/subscriptions",
>     "organizations_url": "https://api.github.com/users/RezaSoleymanifar/orgs",
>     "repos_url": "https://api.github.com/users/RezaSoleymanifar/repos",
>     "events_url": "https://api.github.com/users/RezaSoleymanifar/events{/privacy}",
>     "received_events_url": "https://api.github.com/users/RezaSoleymanifar/received_events",
>     "type": "User",
>     "user_view_type": "public",
>     "site_adm

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; for n in 582 595 597 587; do echo "=== $n"; curl -s -m 20 https://api.github.com/repos/dokima-dev/dokima/issues/$n | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['state'],d['title']);b=d['body'];i=b.find('dokima-ask');print(b[i:i+2500])"; done
```

> commit f27443c740ee6af832572caca2768a7164c9f97c
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 18:24:08 2026 +0000
> 
>     planner for #596 (run 38439481446)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_automerge.py        |  36 +++--
>  tests/test_autopilot_checks.py |   4 +
>  tests/test_merge_approval.py   |  16 +-
>  tests/test_merge_gate.py       | 359 +++++++++++++++++++++++++++++++++++++++++
>  tests/test_required_checks.py  |   5 +-
>  5 files changed, 404 insertions(+), 16 deletions(-)
> === 582
> open Worker, review, merge gate, approval: one fixed order
> dokima-ask -->
> <details><summary>Original issue</summary>
> 
> <!-- dokima-title -->**Original title:** The worker cannot finish until its acceptance tests pass
> 
> In Reza's words (2026-10-13): "the worker agent end of work check should 100% check the acceptance tests".
> 
> Why: the worker is only told to run the plan's tests; no code checks they pass before its session ends. Its work can then fail the Acceptance criteria check at the merge gate and cost a full extra round. From Oct 10 to 13, 4 of 32 Dokima pull requests (#308, #417, #455, #456) had a criterion's test fail at the gate at least once.
> 
> Done when
> - Before the worker hands back, code runs every test the approved plan lists for its criteria on the worker's branch.
> - Any failure refuses the hand-back with the failing tests named, and the worker keeps working in 

**Agent:** I'm reviewing the plan for issue #596; next I'll read the planner's new tests and run them.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_merge_gate.py; git show HEAD -- tests/test_automerge.py tests/test_merge_approval.py tests/test_autopilot_checks.py tests/test_required_checks.py
```

> <persisted-output>
> Output too large (36KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/f6a265b6-e671-4eaf-985a-6754f12d237d/tool-results/bh15zcn7z.txt
> 
> Preview (first 2KB):
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
> - main's branch rule, requiring `all tests` and `Accepta

`7. Read`
```
/home/runner/work/dokima/dokima/tests/test_merge_gate.py
```

> 1	"""The merge gate tests the pull request with main's newest commit, then the owner approves.
> 2	
> 3	Today a code review's approval stops for the owner at once, and autopilot merges once the head's required checks
> 4	pass, even when the branch misses main's newest commit, so the code that lands was never tested as it lands. The
> 5	merge gate runs right after a code review approves: it brings the branch up to date with main when it is behind
> 6	(GitHub's Update branch), then waits for main's required checks on that combined head. Green, the owner is asked to
> 7	approve (on autopilot, Dokima merges that head); any check red, the worker starts again on the pull request.
> 8	
> 9	These tests run `python3 -m dokima.agent next 57 OUT` in-process on a passed code review that approves pull request
> 10	#60, built for issue #57 from `try/issue-57`, against a fake GitHub in memory that stands in for `dokima.agent.gh`:
> 11	
> 12	- the issue, its records (plan, plan review, the owner's `/work`, the worker's record) and its `autopilot` label,
> 13	  through `gh issue view` and `gh api repos/o/r/issues/57`;
> 14	- the pull request through `gh pr list`, `gh pr view` (any `--json` fields) and `gh api repos/o/r/pulls/60`, its
> 15	  files (`dokima/x.py`), and GraphQL's merge state;
> 16	- main's branch rule, requiring `all tests` and `Acceptance criteria`, through `gh api repos/o/r/branches/main`;
> 17	- a branch behind main: `gh api repos/o/r/compare/main...X` answers `behind_by` 1, the REST pull request's
> 18	  `me

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_merge_gate.py 2>&1 | grep -E "596\.|passed|failed|Error" | head -30
```

> """Autopilot merges only once all tests passed with main's newest commit.
>         Proves 596.1.
>         The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
>         date, and merge only the new head, once every required check passed there; today it merges the old head, never
>         tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
>         record_property("proves", "596.1")
>         assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
>             (f"596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: "
> E       AssertionError: 596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: merges=[{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}], branch updates asked at []; it should merge b2b2b2b only
> tests/test_merge_gate.py:255: AssertionError
>         Proves 596.2.
>         The code review approved #60, off autopilot, and All tests failed on its head, which holds main's newest commit.
>         record_property("proves", "596.2")
>         assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
>             f"596.2: All tests failed at the merge gate, and the run printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})"
> E       AssertionError: 596.2: All tes

`9. Bash`
```
cd /home/runner/work/dokima/dokima; cat > /tmp/sub_test.py <<'EOF'
import sys,os
sys.path.insert(0,"tests")
from test_merge_gate import *
def test_sub(tmp_path, monkeypatch, capsys):
    for name,fake in [("running3",FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True)),
                      ("failed3",FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True)),
                      ("behindred1",FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True, autopilot=True)),
                      ("refused1",FakeGitHub({OLD: green(OLD)}, behind=True, autopilot=True, refuse_update=True)),
                      ("running1",FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True, autopilot=True)),
                      ("green2",FakeGitHub({OLD: green(OLD)}))]:
        r=decide(tmp_path,monkeypatch,capsys,fake,name)
        print(name, r, fake.merges, file=sys.stderr)
    fake = FakeGitHub({OLD: green(OLD)}, behind=True, autopilot=True)
    monkeypatch.setattr(agent, "gh", fake.gh); monkeypatch.setattr(time, "sleep", fake.sleep); monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    try: agent.automerge(REPO, N)
    except Exception as e: print("automerge crash", e, file=sys.stderr)
    monkeypatch.undo()
    print("automerge", fake.merges, file=sys.stderr)
    assert 0
EOF
cp /tmp/sub_test.py tests/zz_sub_test.py; timeout 600 python3 -m pytest -q tests/zz_sub_test.py 2>&1 | grep -E "^(running|failed|behind|refused|green|automerge)"; rm tests/zz_sub_test.py; git status --short
```

> green2 (['stop'], '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.', 'Review needs', None) []
> automerge [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}]

`10. Bash`
```
cd /home/runner/work/dokima/dokima; cp /tmp/sub_test.py tests/zz_sub_test.py; timeout 600 python3 -m pytest -q tests/zz_sub_test.py 2>&1 | grep -E "(running3|failed3|behindred1|refused1|running1) \(" ; rm tests/zz_sub_test.py; git status --short
```

> (Bash completed with no output)

`11. Bash`
```
cd /home/runner/work/dokima/dokima; cp /tmp/sub_test.py tests/zz_sub_test.py; timeout 600 python3 -m pytest -q tests/zz_sub_test.py 2>&1 | grep -n -E "running3|failed3|behindred1|refused1|running1" | cut -c1-400; rm tests/zz_sub_test.py
```

> 99:        for name,fake in [("running3",FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True)),
> 100:                          ("failed3",FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True)),
> 101:                          ("behindred1",FakeGitHub({OLD: green(OLD), NEW: red(NEW)}, behind=True, autopilot=True)),
> 102:                          ("refused1",FakeGitHub({OLD: green(OLD)}, behind=True, autopilot=True, refuse_update=True)),
> 103:                          ("running1",FakeGitHub({OLD: green(OLD), NEW: running(NEW)}, behind=True, autopilot=True)),

**Agent:** I'm checking which parts of the planner's tests pass on today's code, to see whether any part proves nothing.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; cp /tmp/sub_test.py tests/zz_sub_test.py; timeout 600 python3 -m pytest -q -s tests/zz_sub_test.py 2>&1 | grep -v "^ " | cut -c1-500 | tail -20; rm tests/zz_sub_test.py
```

> tests/test_merge_gate.py:342: AssertionError
> ___________________________________ test_sub ___________________________________
> 
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-4/test_sub0')
> monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7fdb03c6c140>
> capsys = <_pytest.capture.CaptureFixture object at 0x7fdb03c6c530>
> 
> >       assert 0
> E       assert 0
> 
> tests/zz_sub_test.py:19: AssertionError
> =========================== short test summary info ============================
> FAILED tests/zz_sub_test.py::test_autopilot_merges_only_the_head_tested_with_the_newest_main - AssertionError: 596.1: autopilot merged a head never tested with main's newest commit, or did not merge the tested one: merges=[{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}], branch updates asked at []; it should merge b2b2b2b only
> assert ([{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}] and False)
> FAILED tests/zz_sub_test.py::test_a_failing_test_at_the_merge_gate_starts_the_worker_again - AssertionError: 596.2: All tests failed at the merge gate, and the run printed 'stop', not 'start worker' (Next: '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.')
> assert 'stop' == 'start worker'
> FAILED tests/zz_sub_test.py::test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed - AssertionError: 596.3: the merge gate p

`13. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/file=sys.stderr/file=open("\/tmp\/sub.log","a")/' /tmp/sub_test.py; rm -f /tmp/sub.log; cp /tmp/sub_test.py tests/zz_sub_test.py; timeout 600 python3 -m pytest -q tests/zz_sub_test.py -k test_sub >/dev/null 2>&1; rm tests/zz_sub_test.py; cut -c1-400 /tmp/sub.log
```

> running3 (['stop'], '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.', 'Review needs', None) []
> failed3 (['stop'], '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.', 'Review needs', None) []
> behindred1 (['stop'], '**Next:** Autopilot merged PR #60; what it unblocks starts when the issue closes.', 'Done none', None) [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}]
> refused1 (['stop'], '**Next:** Autopilot merged PR #60; what it unblocks starts when the issue closes.', 'Done none', None) [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}]
> running1 (['stop'], '**Next:** Autopilot merged PR #60; what it unblocks starts when the issue closes.', 'Done none', None) [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}]
> green2 (['stop'], '**Next:** @owner-person The work is approved. Merge the pull request, or review it with a command to send it back.', 'Review needs', None) []
> automerge [{'head': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', 'pinned': 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'}]

`14. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/test_automerge.py tests/test_merge_approval.py tests/test_autopilot_checks.py tests/test_required_checks.py | cut -c1-260
```

> commit f27443c740ee6af832572caca2768a7164c9f97c
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 18:24:08 2026 +0000
> 
>     planner for #596 (run 38439481446)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
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
>          pick(inner if 

`15. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x -p no:cacheprovider -n auto 2>/dev/null | tail -3 || true; timeout 900 python3 -m pytest -q 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-250
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bcgo1xmgk). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/f6a265b6-e671-4eaf-985a-6754f12d237d/tasks/bcgo1xmgk.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`16. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "BRANCH_RULES" -A12 dokima/manifest.py | head -30; grep -n "def next_step" -A5 dokima/agent.py | head; grep -n "blocks in a row\|three\|def blocked_in_a_row\|streak" dokima/agent.py | head
```

> 49:BRANCH_RULES = {
> 50-    "main": {"required_checks": ["all tests", "Acceptance criteria"]},
> 51-}
> 52-
> 53-# The repo's Actions variable that, set to `on`, lets Dokima's app merge a pull request whose code review passed, as a
> 54-# bypass actor of the merge queue ruleset limited to pull requests (#557). Unset or `off`, the owner approves.
> 55-AUTO_MERGE = "DOKIMA_AUTO_MERGE"
> 56-
> 57-PERMISSIONS = {
> 58-    "contents": "write",
> 59-    "pull_requests": "write",
> 60-    "issues": "write",
> 61-    "checks": "read",
> --
> 224:            if branch not in BRANCH_RULES:
> 225-                self.add(path, f"branch rule of {branch!r} is not in the manifest's branch rules")
> 226-
> 227-
> 228-# Python
> 229-
> 230-class Scope:
> 231-    """String names assigned once in a function or module, read by text()."""
> 232-
> 233-    def __init__(self, body, up=None):
> 234-        self.up, self.names, seen = up, {}, set()
> 235-        for node in body:
> 236-            for n in ast.walk(node) if up else [node]:
> 2432:def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
> 2433-    """The river: what follows the run that just finished. ("start", role, stage) or ("stop", why), decided by code.
> 2434-
> 2435-    The river routes by raises. A planner hands to the reviewer unless it raises a blocker for the owner, or has
> 2436-    questions for the owner and the issue is not on autopilot. A worker hands to the reviewer. A review raising a
> 2437-    question or a blocker for the

`17. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Planned three criteria: the merge gate, sending red work back, and asking approval last.",
          "Wrote three new tests and changed six older ones to fit the gate."],
  "decided": ["A branch behind main is brought up to date before its tests are judged.",
              "Off autopilot, the owner is asked to approve once the gate passes."],
  "open": ["Raised two problems outside this issue: stale owner merges and unlimited gate rounds."]
 },
 "verdict": "block",
 "summary": "One check is too weak: asking the owner while tests still run passes it today.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "596.3 weak check",
   "text": "For 596.3, the still-running case passes today though the owner is told to merge. Also fail when the Next line says to merge.",
   "evidence": "`test_merge_gate.py` line 350: today's Next reads 'The work is approved. Merge the pull request', which `\\bapprove\\b` misses."},
  {"kind": "issue", "label": "Stale owner merge",
   "text": "The owner can still merge after main moved past the tested code: main's rule does not demand an up-to-date branch.",
   "evidence": "`dokima/manifest.py` line 50: `BRANCH_RULES` sets only required checks."},
  {"kind": "issue", "label": "Unlimited gate rounds",
   "text": "A merge gate that keeps failing sends work back to the worker forever; the three-blocks stop counts only reviews.",
   "evidence": "`dokima/agent.py` `next_step()` docstring: three blocks in a row counts review records only."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "Confirmed: main's rule requires checks only, so the owner can merge stale code. Worth its own issue."},
  {"raise": "P2", "answer": "done", "why": "Confirmed: only blocking reviews count toward the stop. Worth its own issue."}
 ],
 "asks": [
  {"ask": "Merge gate: runs the full test suite on the combined code and merges if green", "source":
```

> (Bash completed with no output)

**Agent:** The review file passes the check. I'm removing two repeated raises the planner already filed, then waiting on the full test run.

`18. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p="/tmp/dokima-out/review.json";d=json.load(open(p))
d["raises"]=[r for r in d["raises"] if r["kind"]!="issue"]
d["previous_step"]["open"]=["Raised two problems outside this issue: stale owner merges and unlimited gate rounds."]
json.dump(d,open(p,"w"),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 596 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`19. Bash`
```
sleep 1; tail -c 1500 /tmp/claude-1001/-home-runner-work-dokima-dokima/f6a265b6-e671-4eaf-985a-6754f12d237d/tasks/bcgo1xmgk.output
```

> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 1 failed, 397 passed in 48.38s

`20. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 500 python3 -m pytest -q -n auto -p no:cacheprovider 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-200
```

> request, mentioning them (#596: the merge gate passed, so approving is theirs), and the board must show Needs you.
>         assert m.agent_started(), f"212.2: test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"
>         """Autopilot merges only once all tests passed with main's newest commit.
>         The branch misses main's newest commit, and every check passed on its old head. Autopilot must bring it up to
>         date, and merge only the new head, once every required check passed there; today it merges the old head, never
>         tested with main. Beside it, the same pull request whose new head has All tests failed must not merge at all,
>         assert r[3] is None, f"596.1: deciding what follows the code review failed: {r[3]}"
>         The code review approved #60, off autopilot, and All tests failed on its head, which holds main's newest commit.
>         assert r[3] is None, f"596.2: deciding what follows the code review failed: {r[3]}"
>             f"596.2: All tests failed at the merge gate, and the run printed {printed(r)!r}, not 'start worker' (Next: {r[1]!r})"
> E       AssertionError: 596.2: All tests failed at the merge gate, and the run printed 'stop', not 'start worker' (Next: '**Next:** @owner-person The work is approved. Merge the pull request, or revie
> _____ test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed ______
>     def test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed(record_property, tmp_path, 

**Agent:** I blocked the plan for issue [#596](https://github.com/dokima-dev/dokima/issues/596) (the merge gate tests a pull request with the newest main, then the owner approves). The block is small: one check is too weak.

**Plan is sound:**
- All three criteria trace to your words in [#582](https://github.com/dokima-dev/dokima/issues/582#issuecomment-6149288718) (worker, review, merge gate, approval in one order). Each covers exactly one behavior, and no ask is missing.
- Each of the three new tests fails today because the gate doesn't exist yet. None fails from a crash or a bad setup.
- I ran the full suite: 1,095 passed and 4 failed. The four are the three new tests plus one older test the planner changed to ask for approval instead of a merge. All fail as expected.

**The blocker (sent to the planner):**
- In the test for the third criterion, one case covers tests on the combined code still running when the wait runs out. It only checks that the Next line doesn't contain the word "approve".
- Today's code passes that case while telling the owner "The work is approved. Merge the pull request". So the case would miss exactly the mistake it should catch.
- The fix: also fail when the Next line tells the owner to merge.

**The planner's two raised problems:** both checked out, so I answered them as confirmed. Each is worth its own issue:
- You can still merge after main has moved past the tested code, because main's branch rule doesn't require the branch to be up to date.
- A merge gate that keeps failing can send the work back to the worker forever. The "three blocks in a row" stop only counts reviews.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

`21. Bash`
```
grep -E "^FAILED|passed|failed" /tmp/claude-1001/-home-runner-work-dokima-dokima/f6a265b6-e671-4eaf-985a-6754f12d237d/tasks/bcgo1xmgk.output | tail -8 | cut -c1-160
```

> assert r[3] is None, f"596.3: deciding what follows the code review failed: {r[3]}"
>             f"596.3: the merge gate passed, and the owner was not asked to approve: printed {printed(r)!r}, Next {r[1]!r}"
> E       AssertionError: 596.3: the merge gate passed, and the owner was not asked to approve: printed 'stop', Next '**Next:** @owner-person The work is approved
> FAILED tests/test_automerge.py::test_without_autopilot_an_approved_pull_request_waits_for_the_owner - AssertionError: 212.2: off autopilot the card no longer as
> FAILED tests/test_merge_gate.py::test_autopilot_merges_only_the_head_tested_with_the_newest_main - AssertionError: 596.1: autopilot merged a head never tested w
> FAILED tests/test_merge_gate.py::test_a_failing_test_at_the_merge_gate_starts_the_worker_again - AssertionError: 596.2: All tests failed at the merge gate, and 
> FAILED tests/test_merge_gate.py::test_the_owner_is_asked_to_approve_only_after_the_merge_gate_passed - AssertionError: 596.3: the merge gate passed, and the own
> 4 failed, 1095 passed in 543.65s (0:09:03)

**Agent:** A second full test run finished and gave the same result: 1,095 passed and 4 failed. The four are the three new tests and the one older test the planner changed to ask for approval instead of a merge. All four fail because the merge gate isn't built yet.

So the review doesn't change. The plan for [#596](https://github.com/dokima-dev/dokima/issues/596) (merge gate, then owner approval) stays blocked on its one weak check. Today's code passes the "tests still running" case while it tells you to merge the pull request.

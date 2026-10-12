# reviewer (plan) for #523

Run: https://github.com/dokima-dev/dokima/actions/runs/38273630772

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
> # Issue #523: The up-to-date job stops re-merging main into a pull request whose tests already fail
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Stop re-merging main into a pull request whose tests already fail, which wastes runs and budget.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/376
> 
> 
> **User story:** A pull request whose tests already fail is left alone after merges, until its tests pass again.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** After a merge, a pull request whose all tests check failed on its head is not brought up to date.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-523/tests/test_uptodate_failing.py#L122"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A pull request whose all tests f

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json | head -30; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"; cat tests/test_uptodate_failing.py; wc -l dokima/uptodate.py
```

> {"number": null}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "38273244018",
>  "commit_before": "dd6e00771f3bbaf10de005755c63d6f75655da5e",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 149360,
>   "turns": 18,
>   "cost_usd": 1.056302,
>   "tokens_in": 1038376,
>   "tokens_out": 14777
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/523/38273244018-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38273244018",
>  "handback": {
>   "kind": "user_story",
>   "summary": "Stop re-merging main into a pull request whose tests already fail, which wastes runs and budget.",
>   "user_story": "A pull request whose tests already fail is left alone after merges, until its tests pass again.",
>   "acceptance_criteria": [
>    {
>     "text": "After a merge, a pull request whose all tests check failed on its head is not brought up to date.",
>     "words": "After a merge to main, an open pull request whose all tests check failed on its current head is not brought up to date again",
>     "source": "https://github.com/dokima-dev/dokima/issues/523"
>    },
>    {
>     "text": "Such a skipped pull request's issue gets one comment saying so, however many merges skip it.",
>     "words": "and says so once on its issue",
>     "source": "https://github.com/dokima-dev/dokima/issues/523"
>    },
>    {
>     "text": "Once all tests pass on a new head, the pull request is brought up to date as before.",
>     "words": "Once its all tests che

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/uptodate.py; python3 -m pytest -q tests/test_uptodate_failing.py 2>&1 | tail -20
```

> """Bring every open PR that fell behind main up to date with GitHub's own Update branch, after each merge to main.
> 
>     python3 -m dokima.uptodate     # reads GITHUB_REPOSITORY, GITHUB_REF_NAME and GITHUB_SHA
> 
> Rules live in run() and clash(); the GitHub calls go through rest(method, path, **fields), shaped like dokima.board.api.
> A clash on a Dokima PR (try/issue-N in this repo) leaves a record on issue N and starts its planner on autopilot, once
> until the worker runs again; a clash on any other PR mentions the code owners on it and starts nothing.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> from dokima import agent, plan
> from dokima.board import api
> 
> PER_PAGE = 100
> UPDATE_WORDS = ("This pull request could not be updated with ", "This pull request is up to date with ")
> 
> 
> def open_prs(repo, base, rest):
>     """Every open PR into base, drafts included."""
>     out, page = [], 1
>     while True:
>         batch = rest("GET", f"repos/{repo}/pulls?state=open&base={base}&per_page={PER_PAGE}&page={page}")
>         out += [p for p in batch if p.get("base", {}).get("ref") == base]
>         if len(batch) < PER_PAGE:
>             return out
>         page += 1
> 
> 
> def reason(e):
>     """GitHub's own reason for refusing a call: its JSON message, else gh's one-line error."""
>     try:
>         message = json.loads(e.output or "").get("message")
>     except (ValueError, AttributeError):
>         message = None
>     return message or (e.stderr or "").strip() or str(e)
> 
> 
> def refusal_comm

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "all tests" .github/workflows/*.yml | head; grep -rn "all tests\|check_name\|check-runs" dokima/*.py | head -20; python3 -m pytest -q tests/test_uptodate_failing.py 2>&1 | grep -E "^E .*523" | head
```

> .github/workflows/full-suite.yml:14:    name: all tests
> .github/workflows/agent.yml:242:          - $PACK/diff.patch: the work against main. $PACK/tests.txt and tests.xml: all tests, run by code on this machine.
> dokima/fence.py:3:The judges (all tests, each criterion's check) run on fresh machines from what gets pushed, so nothing the worker does to
> dokima/manifest.py:47:CHECKS = ["all tests", "Acceptance criteria"]
> dokima/manifest.py:50:    "main": {"required_checks": ["all tests", "Acceptance criteria"]},
> dokima/manifest.py:86:    (r"commits/[^/]+/check-runs|check-runs|check-suites", "checks"),
> dokima/checks.py:45:def check_name(key, text, limit=60):
> dokima/checks.py:70:        rows.append({"id": key, "name": check_name(key, c["text"]), "tests": " ".join(tests.get(key, []))})
> dokima/card.py:24:ALL_TESTS = "all tests"
> dokima/card.py:669:        check_runs = json.loads(gh("api", f"repos/{repo}/commits/{pr['head']['sha']}/check-runs?per_page=100"))["check_runs"]
> dokima/agent.py:2125:    runs = [r for p in pages(gh("api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100", "--paginate"))
> E       AssertionError: 523.1: #70's all tests check failed on its head, yet it was brought up to date; updates [(70, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), (80, 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')]
> E       AssertionError: 523.2: issue #7 got 0 comments over three merges, expected exactly one: []
> E       AssertionError: 523.3: after all tests passed on new head ccccccc, #70 was

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "check-runs\|unexpected\|raise AssertionError\|def __call__\|def fake\|def rest" tests/test_uptodate*.py | head -30; ls tests | grep -i uptodate
```

> tests/test_uptodate.py:16:  - GET .../commits/SHA/check-runs: no check runs yet (#523 skips a PR whose all tests check failed).
> tests/test_uptodate.py:60:    def __call__(self, method, path, **fields):
> tests/test_uptodate.py:73:            raise AssertionError(f"189: compare asked for an unknown head {m[2]!r}")
> tests/test_uptodate.py:88:        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[^/]+/check-runs", bare):
> tests/test_uptodate.py:90:        raise AssertionError(f"189: unexpected GitHub call {method} {path} {fields}")
> tests/test_uptodate_once.py:14:  - GET .../commits/SHA/check-runs: no check runs yet (#523 skips a PR whose all tests check failed).
> tests/test_uptodate_once.py:86:        raise AssertionError(f"408: a call named comment {cid}, which this PR does not have")
> tests/test_uptodate_once.py:88:    def __call__(self, method, path, **fields):
> tests/test_uptodate_once.py:118:        if method == "GET" and re.fullmatch(rf"repos/{REPO}/commits/[^/]+/check-runs", bare):
> tests/test_uptodate_once.py:120:        raise AssertionError(f"408: unexpected GitHub call {method} {path} {fields}")
> tests/test_uptodate_failing.py:12:  - GET .../commits/SHA/check-runs (check_name= honoured, empty past page 1): the check runs on that commit;
> tests/test_uptodate_failing.py:62:    def __call__(self, method, path, **fields):
> tests/test_uptodate_failing.py:72:        m = re.fullmatch(rf"repos/{REPO}/commits/([^/]+)/check-runs", bare)
> tests/test_uptodate_failing.py:100:    

**Agent:** Still reviewing #523's plan. All three new tests fail for the right reason. Now I'm checking how the planner edited the existing test fakes.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head; git show HEAD -- tests/test_uptodate.py tests/test_uptodate_once.py | head -60; python3 -m pytest -q tests/test_uptodate.py tests/test_uptodate_once.py 2>&1 | tail -2
```

> commit 04cbe1ae41f57691d964b4f3f1db33937d452e21
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 15:54:17 2026 +0000
> 
>     planner for #523 (run 38273244018)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_uptodate.py         |   5 +-
>  tests/test_uptodate_failing.py | 172 +++++++++++++++++++++++++++++++++++++++++
> commit 04cbe1ae41f57691d964b4f3f1db33937d452e21
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 15:54:17 2026 +0000
> 
>     planner for #523 (run 38273244018)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_uptodate.py b/tests/test_uptodate.py
> index 4d18a3a..d7a3427 100644
> --- a/tests/test_uptodate.py
> +++ b/tests/test_uptodate.py
> @@ -12,7 +12,8 @@ The fake GitHub answers:
>    - GET .../compare/BASE...HEAD, where HEAD is a PR's head sha, its ref or its "owner:ref" label: behind_by, ahead_by;
>    - PUT .../pulls/N/update-branch (expected_head_sha): 202, or GitHub's refusal for that PR, 422 with its message;
>    - GET .../issues/N/comments: no comments yet (#408 looks for its earlier refusal comment);
> -  - POST .../issues/N/comments (body): a comment on PR N.
> +  - POST .../issues/N/comments (body): a comment on PR N;
> +  - GET .../commits/SHA/check-runs: no check runs yet (#523 skips a PR whose all tests check failed).
>  """
>  import json
> 

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria and one test for each.",
          "The planner taught two older test fakes to answer the check runs call."],
  "decided": ["Pull requests Dokima did not build are skipped but get no note.",
              "Pull requests whose tests are still running are updated as before."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries every ask, and each new test fails today because the skip is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "After a merge to main, an open pull request whose all tests check failed on its current head is not brought up to date again", "source": "https://github.com/dokima-dev/dokima/issues/523", "criterion": "523.1"},
  {"ask": "and says so once on its issue", "source": "https://github.com/dokima-dev/dokima/issues/523", "criterion": "523.2"},
  {"ask": "Once its all tests check passes again on a new head, it is brought up to date as before.", "source": "https://github.com/dokima-dev/dokima/issues/523", "criterion": "523.3"}],
 "behaviors": [
  {"criterion": "523.1", "one_behavior": true, "why": "One result: a failed pull request gets no update."},
  {"criterion": "523.2", "one_behavior": true, "why": "One result: exactly one note on the issue."},
  {"criterion": "523.3", "one_behavior": true, "why": "One result: a passing new head is updated again."}],
 "tests": [
  {"test": "tests/test_uptodate_failing.py::test_a_pr_whose_all_tests_failed_on_its_head_is_not_brought_up_to_date", "only_its_behavior": true, "why": "Fails today: #70 is updated; the passing #80 must still be updated."},
  {"test": "tests/test_uptodate_failing.py::test_a_skipped_pr_says_so_once_on_its_issue_over_three_merges", "only_its_behavior": true, "why": "Fails today with no note; three merges catch a repeated note."},
  {"test": "tests/test_uptodate_failing.py::test_once_all_tests_pass_on_a_new_head_the_pr_is_broug
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#523](https://github.com/dokima-dev/dokima/issues/523) (stop re-merging main into pull requests whose tests already fail). The hand-back is in `/tmp/dokima-out/review.json` and passed both checks.

- **The asks:** the issue asks for three things, and each has its own criterion:
  - skip the update when the "all tests" check failed on the pull request's current head;
  - say so once on its issue;
  - update it as before once a new head passes.
- **The tests:** I ran the three new tests in `tests/test_uptodate_failing.py` and all three fail today because the skip doesn't exist yet:
  - **523.1:** #70 is still updated even though its tests failed. The test also requires #80, whose tests passed, to keep being updated.
  - **523.2:** issue #7 gets no comment. The test runs three merges, so a comment posted on every merge would also fail it.
  - **523.3:** #70 is updated at both heads. The test expects one update, on the new passing head, so a skip that never lifts would fail it too.
- **Older tests:** the planner added a reply for the test-results lookup to the fake GitHub in `tests/test_uptodate.py` and `tests/test_uptodate_once.py`. Those two files still pass (15 tests).
- **Size:** each criterion is one behavior, so size is ok. I raised no blockers.

The worker can start next. The issue is on autopilot, so the approved plan starts the worker by itself.

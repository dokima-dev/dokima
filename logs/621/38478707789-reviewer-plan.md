# reviewer (plan) for #621

Run: https://github.com/dokima-dev/dokima/actions/runs/38478707789

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #621: The reviewer's pack lists the open issues
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [622], "loop": []} -->
> The reviewer starts with every open issue listed, and may only name issues from that list as searched.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/622
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/615
> - https://github.com/dokima-dev/dokima/issues/623
> 
> 
> **User story:** The reviewer searches a list of open issues built by code, not GitHub live.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The reviewer's starting pack lists every open issue with its title, a one-sentence summary and its link.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/is

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json
for f in ['in/02-reviewer-plan.json']:
  d=json.load(open(f)); print(json.dumps(d,indent=1)[:6000])
"; cat parent.json | head -c 3000; cd /home/runner/work/dokima/dokima; git log --stat -3 | head -40
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38478345254",
>  "commit_before": "42cb7729ae4f8e34cd6096139072f1af44233410",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 73795,
>   "turns": 11,
>   "cost_usd": 0.6321134,
>   "tokens_in": 568894,
>   "tokens_out": 6434
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/621/38478345254-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38478345254",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner planned three criteria and wrote six tests for them."
>    ],
>    "decided": [
>     "The reviewer's pack lists open issues; a review may only name those as searched."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "The plan is right, but building it breaks an older test the plan neither changes nor puts in scope.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "Test cannot pass",
>     "text": "Listing open issues in the reviewer's pack breaks `tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation`. Fix: change that test in test_changes, answering the open issues list.",
>     "evidence": "Calling `agent.open_issues` in a reviewer pack fails it: `AssertionError: ('api', 'repos/o/r/issues?state=open&per_page=100', '--paginate')` at `tests/test_agent.py:189`.",
>     "raised_by": "reviewer",
>     "id": "R1"
>    }
>   ],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "The 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD; cat tests/test_reviewer_open_issues.py; python -m pytest -q tests/test_reviewer_open_issues.py tests/test_agent.py 2>&1 | tail -20
```

> commit 2518f3760ebf28f476b5b05de20660917023e548
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 22:34:18 2026 +0000
> 
>     planner for #621 (run 38478567988)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_agent.py b/tests/test_agent.py
> index 08be40e..02b07da 100644
> --- a/tests/test_agent.py
> +++ b/tests/test_agent.py
> @@ -186,6 +186,8 @@ def test_the_pack_reads_the_issue_and_its_pr_as_one_conversation(record_property
>                                 "reviews": [{"author": {"login": "owner"}, "body": "line note", "submittedAt": "2026-01-01T00:00:02Z", "state": "COMMENTED"}]})
>          if args[0] == "api" and args[1].endswith("/pulls/9/comments"):
>              return json.dumps([{"user": {"login": "owner"}, "body": "rename this", "created_at": "2026-01-01T00:00:05Z", "path": "x.py", "line": 3}])
> +        if args[0] == "api" and args[1].split("?")[0].lstrip("/") == "repos/o/r/issues":
> +            return "[]"
>          raise AssertionError(args)
>      monkeypatch.setattr(agent, "gh", fake_gh)
>      assert agent.pack("o/r", 7, "reviewer", "plan", str(tmp_path / "p"))
> """The reviewer starts with every open issue, and names only those as searched (#621).
> 
> Story 1 of #615. Before the reviewer files an issue it must search the open issues for the same cause; the owner asked
> that code build what this needs before the run: the open issues with their titles, summarie

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_reviewer_open_issues.py 2>&1 | grep -E "^FAILED" | cut -c1-250; grep -rn "pack(.*reviewer" tests/ | grep -v test_reviewer_open_issues | head
```

> FAILED tests/test_reviewer_open_issues.py::test_the_reviewers_pack_lists_every_open_issue_with_its_title_summary_and_link[plan] - AssertionError: 621.1: the reviewer's pack has no open_issues.json listing the open issues
> FAILED tests/test_reviewer_open_issues.py::test_the_reviewers_pack_lists_every_open_issue_with_its_title_summary_and_link[pr] - AssertionError: 621.1: the reviewer's pack has no open_issues.json listing the open issues
> FAILED tests/test_reviewer_open_issues.py::test_the_reviewers_pack_fails_when_github_cannot_list_the_open_issues - Failed: 621.1: the reviewer's pack was built though GitHub could not list the open issues
> FAILED tests/test_reviewer_open_issues.py::test_each_open_issue_in_the_reviewers_pack_says_whether_dokima_filed_it[plan] - AssertionError: 621.2: the reviewer's pack has no open_issues.json listing the open issues
> FAILED tests/test_reviewer_open_issues.py::test_each_open_issue_in_the_reviewers_pack_says_whether_dokima_filed_it[pr] - AssertionError: 621.2: the reviewer's pack has no open_issues.json listing the open issues
> FAILED tests/test_reviewer_open_issues.py::test_a_review_naming_a_searched_issue_not_in_its_pack_is_rejected_saying_why - AssertionError: 621.3: a review naming searched issues #12 and #15, both in its pack, was rejected:
> FAILED tests/test_reviewer_open_issues.py::test_searched_issues_that_are_not_a_list_of_numbers_are_rejected - AssertionError: 621.3: a review naming searched issue #12 as a list of numbers was rejected:
> FAIL

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "agent.pack(\|\.pack(" tests/ | grep -v test_reviewer_open_issues | head -20
```

> tests/test_issue_links.py:81:    agent.pack("o/r", N, "planner", "", dest)
> tests/test_issue_links.py:238:        agent.pack("o/r", N, "planner", "", str(dest))
> tests/test_agent.py:193:    assert agent.pack("o/r", 7, "reviewer", "plan", str(tmp_path / "p"))
> tests/test_raised_earlier_by.py:13:  `agent.pack()` built from GitHub's comments, which carry each comment's "url".
> tests/test_raised_earlier_by.py:173:    agent.pack(REPO, N, role, stage or "", str(pack))
> tests/test_raise_handbacks.py:18:- `agent.pack(repo, n, role, stage, dest)` writes dest/open_blockers.json: exactly the raises still open on the issue
> tests/test_raise_handbacks.py:168:    agent.pack("o/r", 9, role, stage, dest)
> tests/test_raise_handbacks.py:434:    agent.pack("o/r", 9, "planner", "", str(dest))
> tests/test_fixer.py:163:    agent.pack("o/r", 9, "planner", "", str(tmp_path / "p"))
> tests/test_fixer.py:169:    agent.pack("o/r", 9, "worker", "", str(tmp_path / "w"))

**Agent:** Checking whether other tests that build a reviewer pack would break once the pack lists open issues.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 120,175p tests/test_raise_handbacks.py; sed -n 130,180p tests/test_raised_earlier_by.py; grep -n "reviewer" tests/test_raised_earlier_by.py | head; grep -n "pack_for\|def .*pack" tests/test_raise_handbacks.py
```

> """The environment a workflow step runs in, with the repo on the path."""
>     e = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
>          "GITHUB_RUN_ID": "42", **more}
>     for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE"):
>         if k not in more:
>             e.pop(k, None)
>     return e
> 
> 
> def run_agent(*args, **more):
>     """Run `python3 -m dokima.agent ARGS` from the repo root; return (exit code, stdout + stderr)."""
>     p = subprocess.run([sys.executable, "-m", "dokima.agent", *args], cwd=ROOT, env=env(**more), capture_output=True,
>                        text=True, timeout=60)
>     return p.returncode, p.stdout + p.stderr
> 
> 
> def check_handback(tmp_path, kind, handback):
>     """Run `agent check work|review FILE PLAN 9` on the hand-back, the plan being STORY."""
>     d = tempfile.mkdtemp(dir=tmp_path)
>     f, p = os.path.join(d, f"{kind}.json"), os.path.join(d, "plan.json")
>     json.dump(handback, open(f, "w"))
>     json.dump(STORY, open(p, "w"))
>     return run_agent("check", kind, f, p, "9")
> 
> 
> def fake_github(monkeypatch, recs, body="B"):
>     """Fake GitHub so issue #9's conversation holds these records, all posted by the bot."""
>     comments = [comment(r) for r in recs]
> 
>     def gh(*args):
>         if args[:2] == ("issue", "view"):
>             return json.dumps({"number": 9, "title": "T", "body": body, "comments": comments})
>         if args[:2] == ("pr", "list"):
>             return "[]"
>         if args[:2] == ("run",

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 80,112p tests/test_raised_earlier_by.py
```

> return {"author": {"login": agent.BOT}, "body": agent.render(r), "createdAt": at, "url": url}
> 
> 
> def fake_github(monkeypatch):
>     """Fake GitHub: records on issue #9 and its pull request #12, each with its link.
> 
>     The issue holds the planner's and the plan review's records, the pull request the worker's and the code review's."""
>     on_issue = [posted(PLANNER, WHERE["P1"][2], "2026-10-09T10:00:00Z"),
>                 posted(PLAN_REVIEW, WHERE["R2"][2], "2026-10-09T11:00:00Z")]
>     on_pr = [posted(WORKER, WHERE["W3"][2], "2026-10-09T12:00:00Z"),
>              posted(CODE_REVIEW, WHERE["R4"][2], "2026-10-09T13:00:00Z")]
> 
>     def gh(*args):
>         if args[:2] == ("issue", "view"):
>             return json.dumps({"number": N, "title": "T", "body": "B", "comments": on_issue})
>         if args[:2] == ("pr", "list"):
>             return json.dumps([{"number": PR}] if f"try/issue-{N}" in args else [])
>         if args[:2] == ("pr", "view"):
>             return json.dumps({"comments": on_pr, "reviews": []})
>         if args[:2] == ("run", "download"):
>             return ""
>         if args[0] == "api" and "/parent" in args[1]:
>             raise subprocess.CalledProcessError(1, "gh", stderr="HTTP 404: Not Found")
>         if args[0] == "api" and "/pulls/" in args[1] and args[1].rstrip("/").endswith("/comments"):
>             return "[]"
>         if args[0] == "api" and args[1].lstrip("/").startswith(f"repos/{REPO}/issues"):
>             return "[]"
>         raise AssertionError(f"unexpected gh c

**Agent:** All new tests fail for the right reason, the old blocker is fixed, and the other reviewer-pack fakes already answer the open-issues call. Writing the approval.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner changed one older pack test so its fake GitHub answers the open issues list."],
  "decided": ["The plan's three criteria and six tests stay as they were."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries all three asks, each test fails today for the missing feature, and the older test is fixed.",
 "raises": [],
 "answers": [{"raise": "R1", "answer": "done", "why": "The older pack test now answers the open issues list and passes; checked by running it."}],
 "asks": [
  {"ask": "the open issues with their titles, summaries and links", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.1"},
  {"ask": "and which ones Dokima filed", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.2"},
  {"ask": "The reviewer searches that, not GitHub live.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.3"}],
 "behaviors": [
  {"criterion": "621.1", "one_behavior": true, "why": "One list of open issues, each entry with its fields."},
  {"criterion": "621.2", "one_behavior": true, "why": "One filed-by-Dokima flag per listed issue."},
  {"criterion": "621.3", "one_behavior": true, "why": "One rejection of a searched issue outside the pack."}],
 "edge_cases": [
  {"criterion": "621.1", "cut": [], "missing": []},
  {"criterion": "621.2", "cut": [], "missing": []},
  {"criterion": "621.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_reviewer_open_issues.py::test_the_reviewers_pack_lists_every_open_issue_with_its_title_summary_and_link", "only_its_behavior": true, "why": "Runs the real pack over two pages and checks each issue's title, summary and link."},
  {"test": "tests/test_reviewer_open_issues.py::test_the_reviewers_pack_fails_when_github_cannot_list_the_open_issues", "only_its_beh
```

> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> exit 1

`9. Bash`
```
sed -i 's/The planner changed one older pack test so its fake GitHub answers the open issues list./The planner changed an older pack test to answer the open issues list./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 621 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> answer 1 names 'R1', which no open raise has
> exit 1

**Agent:** No raises are open for me (the open-blockers list is empty), so the answer to the earlier blocker comes out.

`10. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p));d['answers']=[];json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 621 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> exit 0

**Agent:** I approved the plan for [#621](https://github.com/dokima-dev/dokima/issues/621) (the reviewer's pack lists the open issues). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Earlier blocker:** fixed. The older test `tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation` now answers the open-issues request and passes when I run it.
- **New tests:** all 8 runs of the 6 new tests fail today for the right reason. The pack has no open-issues list yet, and the review check doesn't accept a list of searched issues yet. None of them crash.
- **Other tests:** the two other test files that build a reviewer pack already answer the open-issues request, so building this plan shouldn't break them.
- **Owner's asks:** all three, from the owner's comment on [#615](https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936) (reviewer checks if a raised issue shares a known cause), each map to one criterion. Each criterion is one behavior, the edge cases are right and the size is fine.
- **Raises:** none. The plan asks the owner nothing. I first wrote an answer to the old blocker, but no raise was open for me, so the check refused it and I took it out.

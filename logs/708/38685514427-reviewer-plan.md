# reviewer (plan) for #708

Run: https://github.com/dokima-dev/dokima/actions/runs/38685514427

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 108
> drwxr-xr-x  3 runner runner  4096 Oct 15 05:12 .
> drwxrwxrwt 18 root   root    4096 Oct 15 05:12 ..
> drwxr-xr-x  2 runner runner  4096 Oct 15 05:12 in
> -rw-r--r--  1 runner runner 17702 Oct 15 05:12 issue.md
> -rw-r--r--  1 runner runner     2 Oct 15 05:12 open_blockers.json
> -rw-r--r--  1 runner runner 58106 Oct 15 05:12 open_issues.json
> -rw-r--r--  1 runner runner    15 Oct 15 05:12 parent.json
> -rw-r--r--  1 runner runner  5350 Oct 15 05:12 plan.json
> 
> in:
> total 32
> drwxr-xr-x 2 runner runner 4096 Oct 15 05:12 .
> drwxr-xr-x 3 runner runner 4096 Oct 15 05:12 ..
> -rw-r--r-- 1 runner runner 6231 Oct 15 05:12 01-planner.json
> -rw-r--r-- 1 runner runner 6881 Oct 15 05:12 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6116 Oct 15 05:12 03-planner.json
> # Issue #708: Every role reads the parent's ask and the owner's commands
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Workers and reviewers on a story read the parent's ask and the owner's comments; the owner's commits count as words.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/707
> - https://github.com/dokima-dev/dokima/issues/335
> 
> 
> **User story:** Every role on a story sees the parent's ask, and the owner's comments and commits steer the work.
> 
> <img src="h

`2. Bash`
```
cd /tmp/pack; cat in/02-reviewer-plan.json; cat parent.json; cd /home/runner/work/dokima/dokima; git diff ac36958 --stat; git diff ac36958 -- tests/test_agent.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38674488301",
>  "commit_before": "11ae9e04aba3309ef8fd8b7389327053abfef260",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 59808,
>   "turns": 10,
>   "cost_usd": 0.4950455999999999,
>   "tokens_in": 366600,
>   "tokens_out": 6468
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/708/38674488301-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38674488301",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote seven criteria from the parent story's list.",
>     "The planner wrote five new tests that fail today.",
>     "The planner pinned two already-built criteria with older tests."
>    ],
>    "decided": [
>     "Committed text counts as the owner's words only when the owner made the commit."
>    ],
>    "open": [
>     "The planner asks the owner whether two already-built asks need only the older tests."
>    ]
>   },
>   "verdict": "block",
>   "summary": "Two criteria lean on older tests that prove a neighbour or much more than their one behavior.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "708.7 wrong role",
>     "text": "The 708.7 test builds the reviewer's pack, not the planner's. Fix: a test building the planner's pack that finds the owner's /plan comment word for word.",
>     "evidence": "`tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation` calls `agent.pack(\"o/

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 175,235p tests/test_agent.py; python -m pytest -q tests/test_story_reads_parent.py tests/test_agent.py 2>&1 | tail -15
```

> def test_the_pack_reads_the_issue_and_its_pr_as_one_conversation(record_property, tmp_path, monkeypatch):
>     """Comments from the issue, its PR, PR reviews and line notes on the code arrive in time order, each labeled with where it was written; records come from both.
> 
>     Then builds the planner's pack from the same conversation and finds the owner's /plan comment in it, word for word."""
>     record_property("proves", "agent.12")
>     plan = rec("planner", handback={"kind": "user_story", "user_story": "s"})
>     def fake_gh(*args):
>         if args[:2] == ("issue", "view"):
>             return json.dumps({"number": 7, "title": "T", "body": "B", "comments": [
>                 {"author": {"login": "owner"}, "body": "/plan first", "createdAt": "2026-01-01T00:00:01Z"},
>                 {"author": {"login": "dokima-runtime"}, "body": agent.render(plan), "createdAt": "2026-01-01T00:00:03Z"}]})
>         if args[:2] == ("pr", "list"):
>             return json.dumps([{"number": 9}] if "try/issue-7" in args else [])
>         if args[:2] == ("pr", "view"):
>             return json.dumps({"comments": [{"author": {"login": "owner"}, "body": "/work change it", "createdAt": "2026-01-01T00:00:04Z"}],
>                                "reviews": [{"author": {"login": "owner"}, "body": "line note", "submittedAt": "2026-01-01T00:00:02Z", "state": "COMMENTED"}]})
>         if args[0] == "api" and args[1].endswith("/pulls/9/comments"):
>             return json.dumps([{"user": {"login": "owner"}, "body": "renam

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git diff ac36958 -- tests/test_story_reads_parent.py; sed -n 100,240p tests/test_story_reads_parent.py
```

> diff --git a/tests/test_story_reads_parent.py b/tests/test_story_reads_parent.py
> index fa463e8..0684999 100644
> --- a/tests/test_story_reads_parent.py
> +++ b/tests/test_story_reads_parent.py
> @@ -44,7 +44,11 @@ def rec(role, stage="", handback=None, run_id="1"):
>      return agent.build_record(role, stage, out, "", True, {"run_id": run_id, "run": f"https://x/run/{run_id}"})
>  
>  
> -def fake_github(monkeypatch, recs):
> +STORY_COMMENTS = [{"author": {"login": OWNER}, "body": "/work", "createdAt": "2026-10-07T09:00:00Z",
> +                   "url": "https://github.com/o/r/issues/9#issuecomment-90"}]
> +
> +
> +def fake_github(monkeypatch, recs, story_comments=STORY_COMMENTS):
>      """Fake GitHub: story 9 is split from issue 5, which the owner commented on."""
>      parent_comments = [
>          {"author": {"login": OWNER}, "body": OWNER_ON_PARENT, "createdAt": "2026-10-01T10:00:00Z",
> @@ -56,9 +60,7 @@ def fake_github(monkeypatch, recs):
>          if args[:2] == ("issue", "view") and str(args[2]) == str(PARENT):
>              return json.dumps({"number": PARENT, "title": "Parent", "body": PARENT_ASK, "comments": parent_comments})
>          if args[:2] == ("issue", "view"):
> -            return json.dumps({"number": N, "title": "Story", "body": STORY_BODY, "comments": [
> -                {"author": {"login": OWNER}, "body": "/work", "createdAt": "2026-10-07T09:00:00Z",
> -                 "url": "https://github.com/o/r/issues/9#issuecomment-90"}]})
> +            return json.dumps({"number": N, "title": "S

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner extended the older routing test with /review on a later line of a pull request.",
          "The planner extended the older pack test to build the planner's pack and find the owner's /plan comment."],
  "decided": ["The planner kept the older tests for the two already-built asks, as the owner said."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries every ask; five new tests fail for the missing feature, and two older tests pin what already works.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.1"},
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.2"},
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.3"},
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.4"},
  {"ask": "Anything I write counts as my words", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.5"},
  {"ask": "I can add, change or delete tests, plan and code on Dokima's branches, then say /review.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.6"},
  {"ask": "Yes, plans live off the branch; I edit them by comment.", "source": "https://github.com/dokima-dev/dokima/issues/559#issuecomment-6183274943", "criterion": "708.7"},
  {"as
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step did line 2 holds 18 words, over its cap of 15: cut 3, keep the facts

**Agent:** Trimming a few lines in the review that ran over the word caps, then rerunning the check.

`6. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open("review.json"))
r["summary"]="The plan carries every ask; five new tests fail for the missing feature; two older tests pin what works."
r["previous_step"]["did"]=["The planner added /review on a later line to the older routing test.",
 "The planner made the older pack test find the owner's /plan comment in the planner's pack."]
json.dump(r,open("review.json","w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 708 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open("review.json"))
r["previous_step"]["did"][1]="The planner made the older pack test find the owner's /plan comment in the planner's pack."
r["previous_step"]["did"][1]="The older pack test now finds the owner's /plan comment in the planner's pack."
json.dump(r,open("review.json","w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 708 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#708](https://github.com/dokima-dev/dokima/issues/708) (every role reads the parent's ask and the owner's commands). The review is saved to `/tmp/dokima-out/review.json`, and it passes both checks.

- **Every ask has a criterion.** All seven asks from [#559](https://github.com/dokima-dev/dokima/issues/559) (tests are the spec) are covered, plus your latest comment on #708: "Both already work, so just pin them with tests."
- **Five new tests fail today for the right reason.** The worker's and reviewers' packs are missing the parent's ask and your comments on it. A criterion quoting a line you committed is still refused. Each test also checks the opposite case where it applies, such as a stranger's committed line being refused.
- **Two things that already work are pinned by older tests, as you asked:**
  - `/review` on a pull request: the routing test now also checks that `/review` on a later line starts nothing.
  - Your `/plan` comment: the conversation test now also builds the planner's pack and finds the comment word for word.
  - Both pass today.
- **My two earlier blockers:**
  - The planner fixed the one about the wrong role (the old test only built the reviewer's pack).
  - The planner disagreed with the one about the routing test checking too much, because new tests must fail today. I let it go, since you chose to keep the older tests.

I found no other problems inside or outside this issue.

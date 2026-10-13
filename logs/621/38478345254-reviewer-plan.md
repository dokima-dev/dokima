# reviewer (plan) for #621

Run: https://github.com/dokima-dev/dokima/actions/runs/38478345254

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 36
> drwxr-xr-x  3 runner runner 4096 Oct 13 22:31 .
> drwxrwxrwt 18 root   root   4096 Oct 13 22:31 ..
> drwxr-xr-x  2 runner runner 4096 Oct 13 22:31 in
> -rw-r--r--  1 runner runner 8503 Oct 13 22:31 issue.md
> -rw-r--r--  1 runner runner    2 Oct 13 22:31 open_blockers.json
> -rw-r--r--  1 runner runner   15 Oct 13 22:31 parent.json
> -rw-r--r--  1 runner runner 4038 Oct 13 22:31 plan.json
> 
> in:
> total 16
> drwxr-xr-x 2 runner runner 4096 Oct 13 22:31 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 22:31 ..
> -rw-r--r-- 1 runner runner 4780 Oct 13 22:31 01-planner.json
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion

`2. Bash`
```
cd /tmp/pack; cat in/01-planner.json | head -c 5000; cat parent.json; cd /home/runner/work/dokima/dokima; cat tests/test_reviewer_open_issues.py
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38477882583",
>  "commit_before": "71e8ad384a11cf159da8bdefdc27f168f4342432",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 203279,
>   "turns": 24,
>   "cost_usd": 1.4816534000000001,
>   "tokens_in": 1699059,
>   "tokens_out": 21474
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/621/38477882583-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38477882583",
>  "handback": {
>   "kind": "user_story",
>   "title": "The reviewer's pack lists the open issues",
>   "summary": "The reviewer starts with every open issue listed, and may only name issues from that list as searched.",
>   "user_story": "The reviewer searches a list of open issues built by code, not GitHub live.",
>   "acceptance_criteria": [
>    {
>     "text": "The reviewer's starting pack lists every open issue with its title, a one-sentence summary and its link.",
>     "words": "the reviewer's starting pack carries what this check needs, built by code before the run: the open issues with their titles, summaries and links",
>     "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936",
>     "edge_cases": [
>      {
>       "case": "GitHub cannot list the open issues: the pack fails with its error, never an empty list.",
>       "test": "tests/test_reviewer_open_issues.py::test_the_reviewers_pack_fails_when_github_cannot_list_the_open_issues"
>      },
>      {
>       "case": "An i

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head; timeout 600 python -m pytest -q tests/test_reviewer_open_issues.py 2>&1 | tail -30; gh issue view 615 --comments 2>&1 | head -150
```

> commit 42cb7729ae4f8e34cd6096139072f1af44233410
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 22:31:00 2026 +0000
> 
>     planner for #621 (run 38477882583)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_reviewer_open_issues.py | 267 +++++++++++++++++++++++++++++++++++++
>  1 file changed, 267 insertions(+)
>  +      where <module 'posixpath' (frozen)> = os.path
> FAILED tests/test_reviewer_open_issues.py::test_the_reviewers_pack_lists_every_open_issue_with_its_title_summary_and_link[pr] - AssertionError: 621.1: the reviewer's pack has no open_issues.json listing the open issues
> assert False
>  +  where False = <function isfile at 0x7fba00d1c2c0>('/tmp/pytest-of-runner/pytest-0/test_the_reviewers_pack_lists_1/pack-pr/open_issues.json')
>  +    where <function isfile at 0x7fba00d1c2c0> = <module 'posixpath' (frozen)>.isfile
>  +      where <module 'posixpath' (frozen)> = os.path
> FAILED tests/test_reviewer_open_issues.py::test_the_reviewers_pack_fails_when_github_cannot_list_the_open_issues - Failed: 621.1: the reviewer's pack was built though GitHub could not list the open issues
> FAILED tests/test_reviewer_open_issues.py::test_each_open_issue_in_the_reviewers_pack_says_whether_dokima_filed_it[plan] - AssertionError: 621.2: the reviewer's pack has no open_issues.json listing the open issues
> assert False
>  +  where False = <function isfile at 0x7fba00d1c2c0>('/tmp/pytest-of-ru

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn '"reviewer"' tests/*.py | grep -n "pack(" | head -30; grep -n "^def pack\|def gh\b\|def gh(" dokima/agent.py
```

> 3:tests/test_agent.py:153:    assert agent.problems_pack("reviewer", "plan", str(d)) == []
> 4:tests/test_agent.py:158:    assert agent.problems_pack("reviewer", "pr", str(d)) == ["worker-run is missing"]
> 5:tests/test_agent.py:160:    assert agent.problems_pack("reviewer", "pr", str(d)) == ["worker-run holds no session log"]
> 6:tests/test_agent.py:163:    assert agent.problems_pack("reviewer", "pr", str(d)) == []
> 7:tests/test_agent.py:191:    assert agent.pack("o/r", 7, "reviewer", "plan", str(tmp_path / "p"))
> 14:tests/test_agent.py:335:    assert agent.problems_pack("reviewer", "plan", str(d)) == []
> 266:tests/test_reviewer_open_issues.py:8:- `agent.pack(repo, n, "reviewer", stage, dest)`, for the plan review (stage "plan") and the code review (stage "pr"),
> 267:tests/test_reviewer_open_issues.py:111:    agent.pack("o/r", N, "reviewer", stage, dest)
> 268:tests/test_reviewer_open_issues.py:165:        agent.pack("o/r", N, "reviewer", "plan", str(dest))
> 30:def gh(*args):
> 296:def pack_records(pack_dir):
> 309:def pack_issue(pack_dir):
> 1191:def pack_parent(*dirs):
> 1221:def pack(repo, number, role, stage, dest):

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 170,200p tests/test_agent.py; grep -rn "agent.pack(\|\.pack(\"o/r\"\|pack(repo" tests/*.py | grep -v test_reviewer_open | head -30; sed -n 1221,1300p dokima/agent.py
```

> assert agent.problems_pack("planner", "", str(d)) == ["issue.md is empty", "issue.md has no comments section"]
> 
> 
> def test_the_pack_reads_the_issue_and_its_pr_as_one_conversation(record_property, tmp_path, monkeypatch):
>     """Comments from the issue, its PR, PR reviews and line notes on the code arrive in time order, each labeled with where it was written; records come from both."""
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
>             return json.dumps([{"user": {"login": "owner"}, "body": "rename this",

**Agent:** Tests all fail for the right reason. Now checking whether existing tests that build a reviewer pack would break once it calls GitHub for open issues.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def open_issues" -A30 dokima/agent.py; sed -n 150,170p tests/test_raise_handbacks.py; sed -n 150,180p tests/test_raised_earlier_by.py; grep -n "def fake\|raise AssertionError\|unexpected" tests/test_raise_handbacks.py tests/test_raised_earlier_by.py | head
```

> 258:def open_issues(repo):
> 259-    """Every open issue of the repo, every page, with its number, title and body; pull requests are left out."""
> 260-    items = [i for p in pages(gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
> 261-    return [{"number": i["number"], "title": i["title"], "body": i.get("body") or ""} for i in items
> 262-            if "pull_request" not in i]
> 263-
> 264-
> 265-def problems_links(h, pack_dir):
> 266-    """Everything wrong with a plan's links: three lists of open issue numbers from the pack, never the issue itself,
> 267-    and no issue in two lists."""
> 268-    path = os.path.join(pack_dir, "open_issues.json")
> 269-    if not os.path.exists(path):
> 270-        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
> 271-    links = h.get("links")
> 272-    if not isinstance(links, dict):
> 273-        return ["links must be an object with three lists: " + ", ".join(LINKS)]
> 274-    issue = os.path.join(pack_dir, "issue.md")
> 275-    m = re.match(r"# Issue #(\d+)", open(issue).read()) if os.path.exists(issue) else None
> 276-    me = int(m.group(1)) if m else None
> 277-    known = {i.get("number") for i in json.load(open(path)) if isinstance(i, dict)}
> 278-    bad, seen = [], {}
> 279-    for k in LINKS:
> 280-        v = links.get(k)
> 281-        if not isinstance(v, list) or not all(isinstance(n, int) and not isinstance(n, bool) for n in v):
> 282-            bad.append(f"links.{k} must be a list of issue nu

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 83,108p tests/test_raised_earlier_by.py; grep -rln "agent.pack(\|agent\.pack(" tests/ ; grep -rn "pack(" tests/*.py | grep -v "def \|_pack\|pack_" | grep -iv planner | head -20
```

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
>         raise AssertionError(f"unexpected gh call {args}")
>     monkeypatch.setattr(agent, "gh", gh)
> tests/test_issue_links.py
> tests/test_raise

**Agent:** Found a likely conflict: an older test fakes GitHub and rejects any extra call while building a reviewer pack. Confirming it by simulating the planned change.

`8. Bash`
```
mkdir -p /tmp/rv && cat > /tmp/rv/conftest.py <<'EOF'
import pytest
from dokima import agent
_orig = agent.pack
@pytest.fixture(autouse=True)
def reviewer_lists(monkeypatch):
    def pack(repo, n, role, stage, dest):
        if role == "reviewer":
            agent.open_issues(repo)  # what the plan asks the reviewer's pack to do
        return _orig(repo, n, role, stage, dest)
    monkeypatch.setattr(agent, "pack", pack)
EOF
cd /home/runner/work/dokima/dokima; PYTHONPATH=. python -m pytest -q -p no:cacheprovider --rootdir=/tmp/rv -c /dev/null --confcutdir=/tmp/rv /tmp/rv tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation tests/test_raise_handbacks.py tests/test_raised_earlier_by.py 2>&1 | tail -8
```

> ...................                                                      [100%]
> 19 passed in 5.80s

`9. Bash`
```
cd /home/runner/work/dokima/dokima; mv /tmp/rv/conftest.py /tmp/rv/rvplug.py; PYTHONPATH=.:/tmp/rv python -m pytest -q -p no:cacheprovider -p rvplug tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation tests/test_raise_handbacks.py tests/test_raised_earlier_by.py 2>&1 | tail -8
```

> return json.dumps([{"user": {"login": "owner"}, "body": "rename this", "created_at": "2026-01-01T00:00:05Z", "path": "x.py", "line": 3}])
> >       raise AssertionError(args)
> E       AssertionError: ('api', 'repos/o/r/issues?state=open&per_page=100', '--paginate')
> 
> tests/test_agent.py:189: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation - AssertionError: ('api', 'repos/o/r/issues?state=open&per_page=100', '--paginate')
> 1 failed, 18 passed in 5.82s

**Agent:** Confirmed: that older test breaks, and the plan doesn't allow changing it. Writing the hand-back.

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner planned three criteria and wrote six tests for them."],
  "decided": ["The reviewer's pack lists open issues; a review may only name those as searched."],
  "open": []
 },
 "verdict": "block",
 "summary": "The plan is right, but building it breaks an older test the plan neither changes nor puts in scope.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Test cannot pass",
   "text": "Listing open issues in the reviewer's pack breaks `tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation`. Fix: change that test in test_changes, answering the open issues list.",
   "evidence": "Calling `agent.open_issues` in a reviewer pack fails it: `AssertionError: ('api', 'repos/o/r/issues?state=open&per_page=100', '--paginate')` at `tests/test_agent.py:189`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "The reviewer's starting pack lists every open issue with its title, summary and link.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.1"},
  {"ask": "Each open issue in the reviewer's pack says whether Dokima filed it.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.2"},
  {"ask": "A review naming a searched issue that is not in its pack is rejected, saying why.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156300936", "criterion": "621.3"}
 ],
 "behaviors": [
  {"criterion": "621.1", "one_behavior": true, "why": "One list of open issues, each entry with its fields."},
  {"criterion": "621.2", "one_behavior": true, "why": "One flag per listed issue."},
  {"criterion": "621.3", "one_behavior": true, "why": "One rejection of a searched issue outside the pack."}
 ],
 "edge_cases": [
  {"criterion": "621.1", "cut": [], "missing": []},
  {"criterion": "621.2", "cut": [], "missing": []},
  {"crite
```

> exit 0

**Agent:** I blocked the plan for [#621](https://github.com/dokima-dev/dokima/issues/621) (the reviewer's pack lists the open issues) and sent it back to the planner. The plan itself is right, but building it would break an older test that the plan neither changes nor puts in scope. The hand-back is saved and passes both checks.

**What's fine**
- All three asks from the approved plan of [#615](https://github.com/dokima-dev/dokima/issues/615) (the reviewer checks whether a raised issue has a known cause) are covered:
  - every open issue listed with its title, summary and link;
  - each one marked filed by Dokima or not;
  - a review naming a searched issue outside its pack is rejected.
- Each criterion is one behavior, and the size is OK.
- All six new tests fail today because the feature is missing, not because of a crash or a bad path.
- No test would pass on a stub: each has a passing case next to its rejecting cases.

**The blocker**
- An older test fakes GitHub and fails on any call it doesn't expect, and it builds a reviewer pack: `tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation`.
- I simulated the planned change by having the reviewer's pack list the open issues first. That test then failed at `tests/test_agent.py:189` on the open-issues call.
- The worker can't fix this, because the plan's scope is only `dokima/agent.py` and `dokima/raises.py`, and it changes no older tests.
- The fix: the planner adds a change to that test so its fake GitHub also answers the open-issues list.

There were no open raises to answer and no questions for you.

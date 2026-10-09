"""On autopilot, a pull request the reviewer approved merges by itself once every check on it is green (#212).

These tests run the workflows the way GitHub runs them, on the machine from test_start.py: every job's and step's
`if:` is evaluated and its scripts run with bash against a fake `gh`. Two ways lead to a merge:
  - the code review: agent.yml runs the reviewer at the pr stage on issue #57 (pull request #60, branch try/issue-57),
    and the fake Claude Code hands back the review the test chose;
  - `/autopilot start`: commands.yml runs on a code owner's comment, on the issue or on its pull request.

The fake GitHub of test_autopilot_close.py (issue tree, labels, states, blocked-by links, comments, signals) is taught
pull requests, their checks and merging. It keeps them in prs.json, one entry per pull request:
{issue, branch, head, checks: {sha: [{name, kind, state}]}, files, refuse, merged, merged_by, moves_to}. It answers:
  - `gh pr list` with --head BRANCH and --state open|closed|merged|all (open by default), --json any fields, and
    -q/--jq `.[0].number` or `.[].number`;
  - `gh pr view N|BRANCH|URL --json ...` (number, url, title, body "Closes #ISSUE", headRefName, headRefOid,
    baseRefName, state, merged, mergeable, files, statusCheckRollup, comments, reviews), -q/--jq with a plain `.field`;
  - `gh pr checks N` (--json name,state,bucket,link,workflow; exit 1 when one failed, 8 when one is still running,
    and "no checks reported" with exit 1 when there are none);
  - `gh api repos/o/r/pulls/N` (head.sha, head.ref, state, merged, mergeable), `.../pulls/N/files`,
    `.../pulls/N/comments` (no line notes), `repos/o/r/commits/SHA/check-runs`, `.../commits/SHA/status` and
    `.../commits/SHA/statuses` (SHA may also be the branch name), each with or without --paginate;
  - `gh pr comment N` and `gh api repos/o/r/issues/N/comments` for a pull request N write on that pull request;
  - `gh run download` puts the worker's session log where the code review's pack expects it.
A check is a check run (kind "run", from GitHub Actions) or a commit status (kind "status"), each SUCCESS, FAILURE or
PENDING; both count as checks. Only -q/--jq with a plain `.field` (or the two pr list forms above) is understood.

Merging is `gh pr merge N` with --squash, --merge or --rebase (without one gh refuses, as it does when not
interactive; --auto only turns on auto-merge and merges nothing; --match-head-commit SHA pins it), or
`gh api -X PUT repos/o/r/pulls/N/merge` (sha=SHA pins it). Like GitHub with no branch protection, the fake merges
whatever it is asked to, whatever the checks say. It refuses when the pinned commit is no longer the head ("Head branch
was modified"), when the test made GitHub refuse (a conflict, branch protection; --admin bypasses that, so a test can
see it used), and when the key is the workflow's own token: agent.yml gives that token only read access, and a merge
made with it would start none of the workflows that run when the issue closes. Only Dokima's app key (the token an
app-token step gives, fake-token) merges. With moves_to set, a new commit is pushed the moment code first reads the
checks: it becomes the head, its checks still running.
"""
import json
import os
import re

import test_autopilot_close as tac
import test_start as ts
from dokima import agent
from test_start import N, OWNER, PR, Ctx, evaluate, condition

LABEL = "autopilot"
HEAD = "a1" * 20
LATER = "b2" * 20
# The two checks autopilot requires by name (#291) sit green beside every set of checks below, so each set tests only
# what its name says.
REQUIRED = [{"name": "All tests", "kind": "run", "state": "SUCCESS"}, {"name": "Acceptance criteria", "kind": "run", "state": "SUCCESS"}]
GREEN = REQUIRED + [{"name": "pytest", "kind": "run", "state": "SUCCESS"}, {"name": "ci/lint", "kind": "status", "state": "SUCCESS"}]
RED_NAME = "pytest (3.12)"
RED = REQUIRED + [{"name": "ci/lint", "kind": "status", "state": "SUCCESS"}, {"name": RED_NAME, "kind": "run", "state": "FAILURE"}]
PENDING = REQUIRED + [{"name": "pytest", "kind": "run", "state": "PENDING"}]
RED_STATUS = REQUIRED + [{"name": "pytest", "kind": "run", "state": "SUCCESS"}, {"name": "ci/coverage", "kind": "status", "state": "FAILURE"}]
CONFLICT = "the merge commit cannot be cleanly created"
PROTECTED = "At least 1 approving review is required by reviewers with write access"
WORKFLOW_FILE = ".github/workflows/ci.yml"

PR_GH = r'''
PRS_FILE = os.path.join(d, "prs.json")
PRS = json.load(open(PRS_FILE)) if os.path.exists(PRS_FILE) else {}
def save_prs():
    json.dump(PRS, open(PRS_FILE, "w"), indent=1)
BOOL = {"--squash", "--merge", "--rebase", "--admin", "--auto", "--delete-branch", "-d", "--edit-last", "--required",
        "--watch", "--paginate", "--silent", "-s", "-m", "-r"}
def positionals():
    out_, skip = [], False
    for i, x in enumerate(a[2:]):
        if skip:
            skip = False
            continue
        if x.startswith("-"):
            skip = x not in BOOL and "=" not in x
            continue
        out_.append(x)
    return out_
def pr_by_branch(b):
    return next((n for n, p in PRS.items() if p["branch"] == b), None)
def pr_sel():
    for x in positionals():
        m = re.fullmatch(r"#?(\d+)|https://github.com/o/r/pull/(\d+)/?", x)
        if m:
            n = m.group(1) or m.group(2)
            return n if n in PRS else None
        if pr_by_branch(x):
            return pr_by_branch(x)
    return None
def pr_state(p):
    return "MERGED" if p.get("merged") else "OPEN"
def checks_of(p, sha):
    if sha == p["branch"]:
        sha = p["head"]
    return p["checks"].get(sha, [])
def reveal(n):
    p = PRS[n]
    if p.get("moves_to") and not p.get("moved"):
        p["moved"] = True
        p["head"] = p["moves_to"]
        save_prs()
def bucket(c):
    return {"SUCCESS": "pass", "FAILURE": "fail", "PENDING": "pending"}[c["state"]]
def rollup(p):
    out_ = []
    for c in checks_of(p, p["head"]):
        if c["kind"] == "status":
            out_.append({"__typename": "StatusContext", "context": c["name"], "state": c["state"],
                         "targetUrl": "https://ci.example/1"})
        else:
            done = c["state"] != "PENDING"
            out_.append({"__typename": "CheckRun", "name": c["name"], "workflowName": "tests",
                         "status": "COMPLETED" if done else "IN_PROGRESS", "conclusion": c["state"] if done else "",
                         "detailsUrl": "https://github.com/o/r/actions/runs/7"})
    return out_
def pr_obj(n):
    p = PRS[n]
    return {"number": int(n), "url": f"https://github.com/o/r/pull/{n}", "title": f"Issue {p['issue']}",
            "body": f"Closes #{p['issue']}", "headRefName": p["branch"], "headRefOid": p["head"], "baseRefName": "main",
            "state": pr_state(p), "merged": bool(p.get("merged")), "mergeable": "UNKNOWN", "isDraft": False,
            "files": [{"path": f, "additions": 1, "deletions": 0} for f in p["files"]],
            "statusCheckRollup": rollup(p), "comments": comments_on("pr", n), "reviews": []}
def rest_pr(n):
    p = PRS[n]
    return {"number": int(n), "html_url": f"https://github.com/o/r/pull/{n}", "state": "closed" if p.get("merged") else "open",
            "merged": bool(p.get("merged")), "mergeable": True, "mergeable_state": "unknown", "body": f"Closes #{p['issue']}",
            "title": f"Issue {p['issue']}", "head": {"sha": p["head"], "ref": p["branch"]}, "base": {"ref": "main"}}
def pick(obj):
    q = flag("-q", "--jq")
    if q and re.fullmatch(r"\.[A-Za-z_]+", q.strip()):
        v = obj.get(q.strip()[1:], "")
        print(v if isinstance(v, str) else json.dumps(v))
    else:
        print(json.dumps(obj))
def merge_log(n, how, pinned, result):
    open(os.path.join(d, "merges.jsonl"), "a").write(json.dumps(
        {"pr": int(n), "args": a, "how": how, "pinned": pinned, "token": token, "result": result}) + "\n")
def merge(n, how, pinned, admin=False):
    p = PRS[n]
    if p.get("merged"):
        merge_log(n, how, pinned, "already merged")
        return f"Pull request #{n} was already merged"
    if token != "fake-token":
        merge_log(n, how, pinned, "workflow token")
        return "Resource not accessible by integration"
    if pinned and pinned != p["head"]:
        merge_log(n, how, pinned, "head moved")
        return "Head branch was modified. Review and try the merge again."
    if p.get("refuse") and not admin:
        merge_log(n, how, pinned, "refused")
        return p["refuse"]
    p["merged"], p["merged_by"] = p["head"], token
    save_prs()
    merge_log(n, how, pinned, "merged")
    return ""
PAPI = next((x.lstrip("/") for x in a[1:] if re.match(r"/?repos/o/r/(pulls|commits)/", x)), None) if a[:1] == ["api"] else None
PAPI = PAPI.split("?")[0] if PAPI else None
m_icom = re.fullmatch(r"/?repos/o/r/issues/(\d+)/comments(?:\?.*)?", next((x for x in a[1:] if "/comments" in x), "")) if a[:1] == ["api"] else None
if m_icom and m_icom.group(1) in PRS:
    n = m_icom.group(1)
    body = api_body()
    if body is None and (flag("-X", "--method") or "GET").upper() == "GET":
        print(json.dumps([shown(c) for c in load() if c["kind"] == "pr" and c["number"] == int(n)]))
    else:
        out(shown(create("pr", n, body)))
    sys.exit(0)
if a[:2] == ["run", "download"]:
    dest = flag("-D", "--dir") or "."
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "s.jsonl"), "w").write(json.dumps({"message": {"role": "assistant", "content": "Built it."}}) + "\n")
    sys.exit(0)
if a[:2] == ["pr", "list"]:
    head, st = flag("--head", "-H"), (flag("--state", "-s") or "open").lower()
    rows = [pr_obj(n) for n, p in sorted(PRS.items()) if (not head or p["branch"] == head)
            and (st == "all" or (st == "open" and not p.get("merged")) or (st in ("merged", "closed") and p.get("merged")))]
    q = (flag("-q", "--jq") or "").strip()
    if q == ".[0].number":
        print(rows[0]["number"] if rows else "")
    elif q == ".[].number":
        print("\n".join(str(r["number"]) for r in rows))
    else:
        print(json.dumps(rows))
    sys.exit(0)
if a[:2] == ["pr", "view"]:
    n = pr_sel()
    if n is None:
        sys.stderr.write("no pull requests found\n")
        sys.exit(1)
    obj = pr_obj(n)
    want = (flag("--json") or "").split(",")
    pick(obj)
    if not flag("--json") or "statusCheckRollup" in want:
        reveal(n)
    sys.exit(0)
if a[:2] == ["pr", "comment"]:
    n = pr_sel()
    body = open(flag("--body-file", "-F")).read() if flag("--body-file", "-F") else flag("--body", "-b")
    print(shown(create("pr", n, body))["html_url"])
    sys.exit(0)
if a[:2] == ["pr", "checks"]:
    n = pr_sel()
    p = PRS[n]
    cs = checks_of(p, p["head"])
    reveal(n)
    if not cs:
        sys.stderr.write(f"no checks reported on the '{p['branch']}' branch\n")
        sys.exit(1)
    rows = [{"name": c["name"], "state": c["state"], "bucket": bucket(c), "link": "https://ci.example/1",
             "workflow": "tests" if c["kind"] == "run" else ""} for c in cs]
    if flag("--json"):
        print(json.dumps(rows))
    else:
        print("\n".join(f"{r['name']}\t{r['bucket']}\t1s\t{r['link']}" for r in rows))
    sys.exit(1 if any(r["bucket"] == "fail" for r in rows) else 8 if any(r["bucket"] == "pending" for r in rows) else 0)
if a[:2] == ["pr", "merge"]:
    n = pr_sel()
    if n is None:
        sys.stderr.write("no pull requests found\n")
        sys.exit(1)
    how = "squash" if "--squash" in a else "merge" if "--merge" in a else "rebase" if "--rebase" in a else None
    if "--auto" in a:
        merge_log(n, how, flag("--match-head-commit"), "auto-merge turned on")
        print(f"Pull request #{n} will be automatically merged when all requirements are met")
        sys.exit(0)
    if not how:
        merge_log(n, how, flag("--match-head-commit"), "no method")
        sys.stderr.write("--merge, --rebase, or --squash required when not running interactively\n")
        sys.exit(1)
    why = merge(n, how, flag("--match-head-commit"), admin="--admin" in a)
    if why:
        sys.stderr.write(f"X Pull request o/r#{n} is not mergeable: {why}\n")
        sys.exit(1)
    print(f"Merged pull request o/r#{n}")
    sys.exit(0)
m_merge = re.fullmatch(r"repos/o/r/pulls/(\d+)/merge", PAPI or "")
if m_merge and m_merge.group(1) in PRS:
    n = m_merge.group(1)
    if (flag("-X", "--method") or "GET").upper() != "PUT":
        sys.stderr.write("HTTP 404: Not Found\n")
        sys.exit(1)
    f = {}
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(a) and "=" in a[i + 1]:
            k, v = a[i + 1].split("=", 1)
            f[k] = v
    if "--input" in a:
        src = flag("--input")
        f.update(json.load(sys.stdin if src == "-" else open(src)) or {})
    why = merge(n, f.get("merge_method", "merge"), f.get("sha"))
    if why:
        code = "409" if why.startswith("Head branch") else "403" if "integration" in why else "405"
        sys.stderr.write(f"HTTP {code}: {why} (https://api.github.com/{PAPI})\n")
        sys.exit(1)
    pick({"sha": "c3" * 20, "merged": True, "message": "Pull Request successfully merged"})
    sys.exit(0)
m_pr = re.fullmatch(r"repos/o/r/pulls/(\d+)(/files|/comments)?", PAPI or "")
if m_pr and m_pr.group(1) in PRS:
    n, sub = m_pr.group(1), m_pr.group(2)
    if sub == "/files":
        print(json.dumps([{"filename": f, "status": "modified", "additions": 1, "deletions": 0} for f in PRS[n]["files"]]))
    elif sub == "/comments":
        print("[]")
    else:
        pick(rest_pr(n))
    sys.exit(0)
m_com = re.fullmatch(r"repos/o/r/commits/(.+?)/(check-runs|status|statuses)", PAPI or "")
if m_com:
    ref, what = m_com.group(1), m_com.group(2)
    n = next((k for k, p in PRS.items() if ref in p["checks"] or ref == p["branch"]), None)
    cs = checks_of(PRS[n], ref) if n else []
    if what == "check-runs":
        runs = [{"name": c["name"], "head_sha": ref, "status": "in_progress" if c["state"] == "PENDING" else "completed",
                 "conclusion": None if c["state"] == "PENDING" else c["state"].lower(),
                 "html_url": "https://github.com/o/r/actions/runs/7"} for c in cs if c["kind"] == "run"]
        pick({"total_count": len(runs), "check_runs": runs})
    else:
        sts = [{"context": c["name"], "state": c["state"].lower(), "target_url": "https://ci.example/1"}
               for c in cs if c["kind"] == "status"]
        states = {s["state"] for s in sts}
        overall = "failure" if "failure" in states else "pending" if "pending" in states or not sts else "success"
        if what == "statuses":
            print(json.dumps(sts))
        else:
            pick({"state": overall, "sha": ref, "total_count": len(sts), "statuses": sts})
    if n:
        reveal(n)
    sys.exit(0)
'''


def fake_gh():
    """The fake GitHub of test_autopilot_close.py, taught pull requests, their checks and merging."""
    anchor = 'if a[:2] == ["issue", "view"]:'
    fake = tac.fake_gh()
    taught = fake.replace(anchor, PR_GH + anchor, 1)
    assert taught != fake, "test setup: could not teach the fake GitHub about pull requests"
    return taught


def stored(kind, number, body, cid, author=agent.BOT, minute=0):
    """A comment already on GitHub, as the fake keeps it."""
    return {"id": cid, "kind": kind, "number": int(number), "created": f"2026-10-07T10:{minute:02d}:00.000000Z",
            "versions": [body], "author": author}


def review_pr(verdict):
    """A code review's hand-back: an approval, or a block with one blocker for the worker."""
    h = {"previous_step": {"did": ["Built the fix."], "decided": [], "open": []}, "verdict": verdict,
         "summary": "Every criterion's test passes." if verdict == "approve" else "57.1's test fails.",
         "blockers": [], "notes": [], "outside_plan": [], "resolved": [], "issues_found": []}
    if verdict == "block":
        h["blockers"] = [{"id": "B1", "criterion": "57.1", "problem": "The test fails.", "evidence": "tests/test_x.py::test_a",
                          "fix": "Make it pass.", "test": "tests/test_x.py::test_a", "fixer": "worker"}]
    return h


def worker_record():
    """A passed worker record."""
    return {"role": "worker", "stage": None, "run_id": "3", "run": "https://github.com/o/r/actions/runs/3",
            "models": ["claude-opus-5-5"], "handback": {"summary": "Built it.", "criteria": {"57.1": "x.py"},
                                                        "evidence": "pytest: 1 passed", "outside_scope": []},
            "check": {"passed": True, "problems": []}}


def code_review_record(verdict):
    """A passed code review record."""
    return {"role": "reviewer", "stage": "pr", "run_id": "4", "run": "https://github.com/o/r/actions/runs/4",
            "models": ["claude-opus-5-5"], "handback": review_pr(verdict), "check": {"passed": True, "problems": []}}


def history(issue, pr, review=None, base=0):
    """An issue's story up to its pull request: planned, plan approved, /work, built, and (when given) code reviewed.

    The plan, its review and the owner's /work are on the issue; the worker's record and the code review on the pull
    request, as the river posts them."""
    out = [stored("issue", issue, agent.render(ts.planner_record(ts.STORY)), base + 1, minute=1),
           stored("issue", issue, agent.render(ts.review_record(ts.APPROVE)), base + 2, minute=2),
           stored("issue", issue, "/work", base + 3, author=OWNER, minute=3),
           stored("pr", pr, agent.render(worker_record()), base + 4, minute=4)]
    if review:
        out.append(stored("pr", pr, agent.render(code_review_record(review)), base + 5, minute=5))
    return out


def pr_state(issue, checks, files=None, refuse="", moves=False):
    """One pull request as the fake GitHub keeps it, built for `issue` on try/issue-ISSUE."""
    head = HEAD if issue == int(N) else f"{issue:02d}" * 20
    state = {"issue": issue, "branch": f"try/issue-{issue}", "head": head, "checks": {head: list(checks)},
             "files": list(files or [f"x{issue}.py"]), "refuse": refuse, "merged": None, "merged_by": None}
    if moves:
        state["moves_to"] = LATER
        state["checks"][LATER] = list(PENDING)
    return state


class Merges:
    """What a machine's fake GitHub saw of pull requests: merges tried, pull requests merged, comments written."""

    def prs(self):
        """Every pull request as GitHub holds it now: {number: state}."""
        return {int(k): v for k, v in json.load(open(f"{self.tmp}/gh/prs.json")).items()}

    def merged(self, pr=PR):
        """The commit pull request `pr` was merged at, or None while it is open."""
        return self.prs()[int(pr)].get("merged")

    def tried(self, pr=None):
        """Every merge asked of GitHub (on `pr`, when given), whatever came of it."""
        path = f"{self.tmp}/gh/merges.jsonl"
        rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
        return [r for r in rows if pr is None or r["pr"] == int(pr)]

    def new_comments(self, kind, n):
        """The bodies of the comments written on issue or pull request n since the test began, as they stand now."""
        return [c["versions"][-1] for c in self.comments()[self.seeded:] if c["kind"] == kind and c["number"] == int(n)]

    def autopilot_lines(self, n=None):
        """Every comment written since the test began that reads `Autopilot: merged PR #...`: [(kind, number, body)]."""
        return [(c["kind"], c["number"], c["versions"][-1].strip()) for c in self.comments()[self.seeded:]
                if re.match(r"\s*Autopilot: merged", c["versions"][-1]) and (n is None or c["number"] == int(n))]


class Review(Merges, ts.Machine):
    """One code review of pull request #60 on issue #57, run through the whole agent workflow (agent.yml).

    `labels` gives each issue's labels ({57: ["autopilot"]} puts #57 on autopilot); `checks`, `files`, `refuse` and
    `moves` describe #60 as GitHub holds it. The fake Claude Code hands back `review`."""

    def __init__(self, tmp, review, labels, checks, files=None, refuse="", moves=False):
        super().__init__(tmp, [], try_branch=True, options={"pr_open": True})
        t = self.tmp
        open(f"{t}/bin/gh", "w").write(fake_gh())
        os.chmod(f"{t}/bin/gh", 0o755)
        seed = history(57, 60)
        json.dump(seed, open(f"{t}/gh/comments.json", "w"))
        self.seeded = len(seed)
        json.dump({str(k): list(v) for k, v in labels.items()}, open(f"{t}/gh/labels.json", "w"))
        json.dump({PR: pr_state(57, checks, files, refuse, moves)}, open(f"{t}/gh/prs.json", "w"))
        json.dump(review, open(f"{t}/review.json", "w"))
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": "reviewer", "stage": "pr", "issue": N}}))
        ctx = {"inputs": Ctx(role="reviewer", stage="pr", issue=N),
               "github": Ctx(event_name="workflow_dispatch", actor=OWNER, event=Ctx(), run_id="42", run_attempt="1",
                             server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf = ts.workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        self.failed = self.result == "failure"

    board = ts.Run.board

    def card(self):
        """The code review's record as it stands on GitHub: its body, or '' when none was posted."""
        for c in self.comments()[self.seeded:]:
            body = c["versions"][-1]
            recs = agent.records([{"author": {"login": c["author"]}, "body": body}])
            if recs and recs[0].get("role") == "reviewer" and recs[0].get("stage") == "pr":
                return body
        return ""

    def next_line(self):
        """The Next line the code review's card ends with, or ''."""
        lines = [l for l in self.card().splitlines() if l.startswith("**Next:**")]
        return lines[-1] if lines else ""


class Command(Merges, tac.Repo):
    """An issue tree whose issues have pull requests, on which a code owner says a command (commands.yml).

    `prs` maps each pull request's number to its state (pr_state); `reviews` maps each issue with a pull request to
    its newest code review's verdict ("approve" or "block"). The tree is #50 > #57, #58 and #57 > #101, #102, #105,
    #101 > #103, #104 unless another is given."""

    def __init__(self, tmp, prs, reviews, labels=None, tree=None):
        tree = tree or {50: [57, 58], 57: [101, 102, 105], 101: [103, 104]}
        by_issue = {p["issue"]: n for n, p in prs.items()}
        seed = []
        for issue, verdict in sorted(reviews.items()):
            seed += history(issue, by_issue[issue], verdict, base=10000 + 100 * issue)
        super().__init__(tmp, tree, labels=labels or {}, seed=seed, history=[])
        t = self.tmp
        open(f"{t}/bin/gh", "w").write(fake_gh())
        json.dump({str(k): v for k, v in prs.items()}, open(f"{t}/gh/prs.json", "w"))

    def listen(self, body, on_pr=None):
        """A code owner's comment `body` on issue #57, or on pull request `on_pr`, runs commands.yml."""
        t = self.tmp
        number = int(on_pr or N)
        issue = {"number": number, **({"pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{number}"}} if on_pr else {})}
        event = {"comment": {"body": body, "user": {"login": OWNER, "type": "User"}}, "issue": issue}
        open(f"{t}/event.json", "w").write(json.dumps(event))
        github = Ctx(event_name="issue_comment", actor=OWNER, event=event, run_id="42", run_attempt="1",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        wf = ts.workflow("commands.yml")
        jobs, results, outputs = wf["jobs"], {}, {}
        while len(results) < len(jobs):
            for name, job in jobs.items():
                needs = job.get("needs") or []
                needs = [needs] if isinstance(needs, str) else needs
                if name in results or any(x not in results for x in needs):
                    continue
                res = [results[x] for x in needs]
                status = {"failed": "failure" in res, "success": all(r == "success" for r in res)}
                ctx = {"github": github, "inputs": Ctx(), "vars": Ctx(DOKIMA_APP_ID="1"),
                       "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                       "needs": Ctx({x: {"result": results[x], "outputs": outputs.get(x, {})} for x in needs})}
                if not evaluate(condition(job.get("if")), ctx, status):
                    results[name] = "skipped"
                    continue
                if "uses" in job:
                    results[name] = "success"
                    continue
                results[name], outputs[name] = self.run_job(f"{name}-{len(self.log)}", job, ctx, "issue_comment",
                                                            [("/tmp/", f"{t}/jobs/{name}-{len(self.log)}/tmp/")], wf.get("defaults"))
        self.results = results
        self.failed = "failure" in results.values()
        return results


PR_APPROVE = review_pr("approve")
PR_BLOCK = review_pr("block")
ON = {57: [LABEL]}


def visible(body):
    """A comment without its folded JSON record: the part the owner reads."""
    return re.sub(r"```json\n.*?\n```", "", body, flags=re.S)


def no_bypass(m, crit, case):
    """No merge was asked with --admin or as auto-merge: Dokima merges itself, never past GitHub's protection."""
    for t in m.tried():
        assert "--admin" not in t["args"], f"{crit} ({case}): a merge was asked with --admin, past branch protection: {t['args']}"
        assert "--auto" not in t["args"], f"{crit} ({case}): auto-merge was turned on instead of Dokima merging: {t['args']}"


def assert_merged(m, crit, case, pr=PR, issue=N, head=HEAD):
    """Pull request `pr` merged at the head whose checks were green, with Dokima's app key, and its issue says so once."""
    tried = m.tried(pr)
    assert m.merged(pr) == head, (f"{crit} ({case}): pull request #{pr}, approved with every check green, was not merged at "
                                  f"its head (merged: {m.merged(pr)}, merges tried: {[(t['args'], t['result']) for t in tried]})"
                                  f"\n{m.tail()}")
    assert all(t["token"] == "fake-token" for t in tried), \
        (f"{crit} ({case}): a merge was asked with the workflow's own token, not Dokima's app key; a merge made with it "
         f"starts none of the workflows that run when the issue closes: {[t['token'] for t in tried]}")
    lines = m.autopilot_lines(issue)
    assert lines == [("issue", int(issue), f"Autopilot: merged PR #{pr}")], \
        f"{crit} ({case}): issue #{issue} did not get exactly one comment reading 'Autopilot: merged PR #{pr}': {lines}"
    no_bypass(m, crit, case)


def assert_waits(m, crit, case, reason, pr=PR, issue=N):
    """Pull request `pr` stayed open, nothing says Autopilot merged it, and a comment on it says why, mentioning the owner."""
    assert m.merged(pr) is None, f"{crit} ({case}): pull request #{pr} was merged though it must wait: at {m.merged(pr)}"
    assert m.autopilot_lines() == [], f"{crit} ({case}): an Autopilot line was posted though nothing merged: {m.autopilot_lines()}"
    on_pr = [visible(b) for b in m.new_comments("pr", pr)]
    assert any(f"@{OWNER}" in b and reason.lower() in b.lower() for b in on_pr), \
        (f"{crit} ({case}): no comment on pull request #{pr} gives the reason ({reason!r}) and mentions @{OWNER}: "
         f"{[b[-500:] for b in on_pr]}\n{m.tail()}")
    no_bypass(m, crit, case)


def test_on_autopilot_an_approved_pull_request_with_green_checks_merges_and_says_so(record_property, tmp_path):
    """On autopilot, the code review's approval with every check green merges the pull request and the issue says so.

    Runs the code review of #60 on issue #57, which is on autopilot, the reviewer approving and every check on #60's
    head green (a check run and a commit status). #60 must be merged at that head with Dokima's app key, #57 must get
    exactly one comment reading `Autopilot: merged PR #60`, the review's card must end with a Next line saying it merged
    without mentioning the owner, the board must show no Needs you, and no stage may be started."""
    record_property("proves", "212.1")
    m = Review(tmp_path / "merge", PR_APPROVE, ON, GREEN)
    assert m.agent_started(), f"212.1: test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"
    assert_merged(m, "212.1", "code review")
    nxt = m.next_line()
    assert "merged" in nxt.lower() and f"@{OWNER}" not in nxt, \
        f"212.1: the review's card does not end with a Next line saying it merged, without mentioning the owner: {nxt!r}"
    assert m.board().endswith("none"), f"212.1: the card shows Needs you after autopilot merged: {m.board()!r}"
    assert m.dispatches() == [], f"212.1: the run that merged started another stage: {m.dispatches()}"


def test_autopilot_start_merges_a_pull_request_already_approved(record_property, tmp_path):
    """`/autopilot start` merges the issue's pull request that its code review already approved with every check green.

    Issue #57's newest record is the code review's approval of #60, every check green. `/autopilot start` said on the
    issue must merge #60 at its head and post `Autopilot: merged PR #60` once on #57; said on pull request #60, the
    same. Said on the issue when the newest code review blocks, it merges nothing and posts no Autopilot line."""
    record_property("proves", "212.1")
    for case, on_pr in (("said on the issue", None), ("said on the pull request", PR)):
        m = Command(tmp_path / case.replace(" ", "-"), {60: pr_state(57, GREEN)}, {57: "approve"})
        m.listen("/autopilot start", on_pr=on_pr)
        assert_merged(m, "212.1", f"/autopilot start {case}")
    m = Command(tmp_path / "blocked", {60: pr_state(57, GREEN)}, {57: "block"})
    m.listen("/autopilot start")
    assert m.merged() is None and m.autopilot_lines() == [], \
        f"212.1 (/autopilot start, newest code review blocks): #60 was merged or an Autopilot line posted: {m.autopilot_lines()}"


def test_autopilot_start_merges_the_approved_pull_requests_of_the_whole_tree(record_property, tmp_path):
    """`/autopilot start` merges every approved, green pull request anywhere in the issue's tree, and nothing else.

    The tree is #57 > #101, #102, #105 and #101 > #103, #104, under #50 beside #58. Approved with every check green:
    #60 (#57), #64 (#105, one level down), #63 (#104, two levels down), and outside the tree #65 (#58) and #66 (#50).
    #61 (#102) is green but its newest code review blocks; #62 (#103) is approved with a red check. `/autopilot start`
    on #57 must merge #60, #64 and #63 and post one Autopilot line on each of #57, #105 and #104 for its own pull
    request; it must not merge #61, #62, #65 or #66, and #62 must say on itself which check is red, mentioning the owner."""
    record_property("proves", "212.1")
    prs = {60: pr_state(57, GREEN), 61: pr_state(102, GREEN), 62: pr_state(103, RED), 63: pr_state(104, GREEN),
           64: pr_state(105, GREEN), 65: pr_state(58, GREEN), 66: pr_state(50, GREEN)}
    reviews = {57: "approve", 102: "block", 103: "approve", 104: "approve", 105: "approve", 58: "approve", 50: "approve"}
    m = Command(tmp_path / "tree", prs, reviews)
    m.listen("/autopilot start")
    for pr, issue in ((60, 57), (64, 105), (63, 104)):
        assert m.merged(pr) == m.prs()[pr]["head"], \
            f"212.1 (tree): #{pr} of #{issue}, approved and green inside the tree, was not merged at its head:\n{m.tail()}"
    for pr, why in ((61, "its newest code review blocks"), (62, "it has a red check"), (65, "#58 is outside the tree"),
                    (66, "#50 is above the issue, outside its tree")):
        assert m.merged(pr) is None, f"212.1 (tree): #{pr} was merged, though {why}"
    lines = sorted(m.autopilot_lines())
    want = sorted([("issue", 57, "Autopilot: merged PR #60"), ("issue", 104, "Autopilot: merged PR #63"),
                   ("issue", 105, "Autopilot: merged PR #64")])
    assert lines == want, f"212.1 (tree): expected one Autopilot line on each of #57, #104 and #105 for its own pull request, found {lines}"
    on_62 = [visible(b) for b in m.new_comments("pr", 62)]
    assert any(f"@{OWNER}" in b and RED_NAME.lower() in b.lower() for b in on_62), \
        f"212.1 (tree): #62, approved with a red check, does not say which check is red and mention the owner: {on_62}"
    no_bypass(m, "212.1", "tree")


def test_without_autopilot_an_approved_pull_request_waits_for_the_owner(record_property, tmp_path):
    """Off autopilot, an approved pull request with green checks still waits for the owner to merge it, as today.

    Runs the code review of #60, approving with every check green, on issue #57 without the autopilot label (it carries
    only "bug"). No merge may be tried, no Autopilot line posted, the card must still say "Merge the pull request" and
    mention the owner, and the board must show Needs you. `/autopilot stop` on the issue with that approved pull
    request merges nothing either. Beside them, the same review on autopilot does merge."""
    record_property("proves", "212.2")
    m = Review(tmp_path / "off", PR_APPROVE, {57: ["bug"]}, GREEN)
    assert m.agent_started(), f"212.2: test setup: the code review never ran; it stopped at '{m.failed_step}':\n{m.tail()}"
    assert m.tried() == [] and m.merged() is None, f"212.2: a merge was tried off autopilot: {m.tried()}"
    assert m.autopilot_lines() == [], f"212.2: an Autopilot line was posted off autopilot: {m.autopilot_lines()}"
    nxt = m.next_line()
    assert "Merge the pull request" in nxt and f"@{OWNER}" in nxt, \
        f"212.2: off autopilot the card no longer says 'Merge the pull request' to the owner: {nxt!r}"
    assert m.board().endswith("needs"), f"212.2: off autopilot the card does not show Needs you: {m.board()!r}"

    m = Command(tmp_path / "stop", {60: pr_state(57, GREEN)}, {57: "approve"}, labels={57: [LABEL]})
    m.listen("/autopilot stop")
    assert m.tried() == [] and m.merged() is None and m.autopilot_lines() == [], \
        f"212.2: `/autopilot stop` tried a merge or posted an Autopilot line: {m.tried()} {m.autopilot_lines()}"

    m = Review(tmp_path / "on", PR_APPROVE, ON, GREEN)
    assert m.merged() == HEAD, f"212.2: the same review on autopilot did not merge, so this test proves nothing:\n{m.tail()}"


def test_a_refused_merge_stops_for_the_owner_and_says_why(record_property, tmp_path):
    """A merge that cannot happen leaves the pull request open, says why on it, mentions the owner and shows Needs you.

    Runs the code review of #60 on autopilot, approving, four ways: a red check, no checks at all, GitHub refusing the
    merge for a conflict, and GitHub refusing it for branch protection. Each must leave #60 open, post no Autopilot
    line, write on #60 the reason (the red check's name, that there are no checks, or GitHub's own words) mentioning
    the owner, show Needs you and start nothing; for the two GitHub refuses, the merge must have been asked. Then
    `/autopilot start` on the approved #60: with a red check, and with every check green while GitHub refuses for a
    conflict and for branch protection, each says why on #60 and mentions the owner."""
    record_property("proves", "212.3")
    cases = (("red check", RED, "", RED_NAME), ("no checks", [], "", "no check"),
             ("conflict", GREEN, CONFLICT, CONFLICT), ("branch protection", GREEN, PROTECTED, PROTECTED))
    for case, checks, refuse, reason in cases:
        m = Review(tmp_path / case.replace(" ", "-"), PR_APPROVE, ON, checks, refuse=refuse)
        assert m.agent_started(), f"212.3 ({case}): test setup: the code review never ran:\n{m.tail()}"
        assert_waits(m, "212.3", case, reason)
        assert m.board().endswith("needs"), f"212.3 ({case}): the card does not show Needs you: {m.board()!r}"
        assert m.dispatches() == [], f"212.3 ({case}): a refused merge started another stage: {m.dispatches()}"
        if refuse:
            assert m.tried(PR), f"212.3 ({case}): the merge was never asked of GitHub, so GitHub's words cannot be its reason"
    for case, checks, refuse, reason in (("red check", RED, "", RED_NAME), ("conflict", GREEN, CONFLICT, CONFLICT),
                                         ("branch protection", GREEN, PROTECTED, PROTECTED)):
        m = Command(tmp_path / f"command-{case.replace(' ', '-')}", {60: pr_state(57, checks, refuse=refuse)}, {57: "approve"})
        m.listen("/autopilot start")
        assert_waits(m, "212.3", f"/autopilot start, {case}", reason)


def test_agents_md_says_autopilot_merges_what_the_reviewer_approved(record_property):
    """AGENTS.md's flow, step 6, says that on autopilot the reviewer's approval with green checks merges by itself.

    Reads step 6 (Merge) of The flow in AGENTS.md. Beside the owner approving and merging, it must say that on
    autopilot the pull request merges by itself once the reviewer approved and every check is green: the words
    autopilot, merge, approv(e/al) and green or check must all be in that step."""
    record_property("proves", "212.4")
    text = open(os.path.join(ts.ROOT, "AGENTS.md")).read()
    m = re.search(r"^6\. \*\*Merge\.\*\*(.*?)(?=^\S|\Z)", text, re.S | re.M)
    assert m, "212.4: AGENTS.md has no step 6 (Merge) in The flow"
    step = m.group(1).lower()
    missing = [w for w in ("autopilot", "merge", "approv") if w not in step]
    if "green" not in step and "check" not in step:
        missing.append("green or check")
    assert not missing, f"212.4: AGENTS.md step 6 does not say autopilot merges what the reviewer approved with green checks; missing {missing}: {m.group(0)!r}"


def test_a_pull_request_changing_a_workflow_file_never_merges_by_autopilot(record_property, tmp_path):
    """A pull request that changes a workflow file never merges by autopilot; it waits and says so to the owner.

    Runs the code review of #60, approving with every check green on autopilot, where #60 changes
    .github/workflows/ci.yml; then `/autopilot start` on the same. Neither may merge it or post an Autopilot line, and
    each must write on #60 that it changes a workflow file (naming .github/workflows), mentioning the owner. Beside
    them, the same pull request changing only an ordinary file merges."""
    record_property("proves", "212.5")
    files = ["x57.py", WORKFLOW_FILE]
    m = Review(tmp_path / "review", PR_APPROVE, ON, GREEN, files=files)
    assert m.agent_started(), f"212.5: test setup: the code review never ran:\n{m.tail()}"
    assert_waits(m, "212.5", "code review", ".github/workflows")
    m = Command(tmp_path / "command", {60: pr_state(57, GREEN, files=files)}, {57: "approve"})
    m.listen("/autopilot start")
    assert_waits(m, "212.5", "/autopilot start", ".github/workflows")
    m = Command(tmp_path / "control", {60: pr_state(57, GREEN, files=["x57.py", "docs/ci.md"])}, {57: "approve"})
    m.listen("/autopilot start")
    assert m.merged() == HEAD, f"212.5: a pull request changing no workflow file did not merge, so this test proves nothing:\n{m.tail()}"


def test_nothing_merges_unless_every_check_on_the_merging_commit_is_green(record_property, tmp_path):
    """Nothing merges by autopilot unless every check on the very commit that merges passed; never with --admin.

    GitHub here merges whatever it is asked to, as on a repo with no branch protection. By the code review and by
    `/autopilot start`, each of these must leave #60 unmerged: a check still running, no checks at all, a red commit
    status beside a green check run, and a new commit pushed the moment the checks were read (its checks still
    running). No merge may use --admin or auto-merge. Beside them, every check green (a check run and a status) merges
    at the head that was checked."""
    record_property("proves", "212.6")
    cases = (("check still running", PENDING, False), ("no checks", [], False), ("red commit status", RED_STATUS, False),
             ("new commit after the checks were read", GREEN, True))
    for case, checks, moves in cases:
        m = Review(tmp_path / f"review-{case.replace(' ', '-')}", PR_APPROVE, ON, checks, moves=moves)
        assert m.agent_started(), f"212.6 ({case}): test setup: the code review never ran:\n{m.tail()}"
        assert m.merged() is None, f"212.6 (code review, {case}): #60 was merged at {m.merged()}, though not every check on it passed"
        assert m.autopilot_lines() == [], f"212.6 (code review, {case}): an Autopilot line was posted: {m.autopilot_lines()}"
        no_bypass(m, "212.6", f"code review, {case}")
        m = Command(tmp_path / f"command-{case.replace(' ', '-')}", {60: pr_state(57, checks, moves=moves)}, {57: "approve"})
        m.listen("/autopilot start")
        assert m.merged() is None, f"212.6 (/autopilot start, {case}): #60 was merged at {m.merged()}, though not every check on it passed"
        assert m.autopilot_lines() == [], f"212.6 (/autopilot start, {case}): an Autopilot line was posted: {m.autopilot_lines()}"
        no_bypass(m, "212.6", f"/autopilot start, {case}")
    m = Review(tmp_path / "review-green", PR_APPROVE, ON, GREEN)
    assert m.merged() == HEAD, f"212.6 (code review, all green): #60 was not merged at the checked head:\n{m.tail()}"
    no_bypass(m, "212.6", "code review, all green")
    m = Command(tmp_path / "command-green", {60: pr_state(57, GREEN)}, {57: "approve"})
    m.listen("/autopilot start")
    assert m.merged() == HEAD, f"212.6 (/autopilot start, all green): #60 was not merged at the checked head:\n{m.tail()}"

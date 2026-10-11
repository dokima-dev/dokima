"""Plays card.yml as GitHub runs it, one event at a time, against a fake GitHub.

Lifted from the tests #332's planner wrote on branch try/issue-332 (tests/test_card_now.py), so #346's tests and #332's
play card.yml the same way. For one event:
- The event starts the workflow when card.yml's `on:` lists it (and its activity type, and for workflow_run the
  workflow that finished). Then every job runs in the order its `needs` allow: a job's `if:` and every `${{ }}` are
  evaluated with tests/test_start.py's evaluator (github, vars, secrets, needs, steps, env); `uses:` steps are skipped
  (checkout is noted with the ref it would check out, and the app token step gives a fake token); `run:` steps run with
  bash, from a copy of this repo's dokima/ and .github/, with a fake `gh` first on PATH. Values a step writes to
  GITHUB_OUTPUT or GITHUB_ENV are read as KEY=value lines, and a job's `outputs:` reach later jobs through `needs`.
- Every concurrency group card.yml declares (the workflow's and each job's that runs) is evaluated for the event, and
  kept with its cancel-in-progress setting.
- An event GitHub runs from the pull request's own copy reaches card.yml through a relay: any workflow card.yml's
  workflow_run lists by name that starts on the event is played first, then card.yml for the workflow_run it sends.

The fake GitHub (repo o/r, code owner `boss` through CODEOWNERS, Dokima's bot `dokima-runtime`) keeps its state in one
JSON file. It holds issue #246 with PR #260 from try/issue-246, and issue #312 with PR #314 from try/issue-312, each
with a plan, its approval, a build and an approving code review, and a stale card on every issue and PR.
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from test_start import Ctx, Nil, condition, evaluate, fill, github_shell, load_yaml  # noqa: E402
from dokima import agent, body  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
CARD_YML = os.path.join(WORKFLOWS, "card.yml")
CARD_PY = os.path.join(ROOT, "dokima", "card.py")
OWNER = "boss"
BOT = agent.BOT
STAGES = ("Backlog", "Plan", "Work", "Review", "Merged")
# GitHub runs these events from the default branch's copy of the workflow file, whatever a pull request changes.
MAINS_COPY = {"issues", "issue_comment", "pull_request_target", "workflow_run", "schedule", "workflow_dispatch"}
# GitHub runs these from the pull request's own copy (its merge ref, or the merge queue's).
OWN_COPY = {"pull_request", "pull_request_review", "pull_request_review_comment", "merge_group"}

FAKE_GH = r'''
import json, os, re, sys
D = os.environ["FAKE_GH_DIR"]
STATE = os.path.join(D, "state.json")
S = json.load(open(STATE))
a = sys.argv[1:]
open(os.path.join(D, "calls.jsonl"), "a").write(json.dumps(a) + "\n")
REPO = "o/r"
WITH_VALUE = {"-X", "--method", "-f", "-F", "--raw-field", "--field", "-H", "--header", "--input", "-q", "--jq",
              "-R", "--repo", "--json", "--body", "--body-file", "--head", "--state", "--title", "--label", "-t",
              "--template", "--limit", "-L", "--search", "--base", "--reason", "--comment"}


def save():
    json.dump(S, open(STATE, "w"), indent=1)


def flag(*names):
    for i, x in enumerate(a):
        if x in names and i + 1 < len(a):
            return a[i + 1]
    return None


def fields():
    out = {}
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--raw-field", "--field") and i + 1 < len(a):
            k, _, v = a[i + 1].partition("=")
            if x in ("-F", "--field") and v.startswith("@"):
                v = sys.stdin.read() if v == "@-" else open(v[1:]).read()
            out[k] = v
        if x == "--input" and i + 1 < len(a):
            out.update(json.load(sys.stdin if a[i + 1] == "-" else open(a[i + 1])))
    return out


def positional():
    out, skip = [], False
    for x in a[1:]:
        if skip:
            skip = False
            continue
        if x in WITH_VALUE:
            skip = True
            continue
        if x.startswith("-"):
            continue
        out.append(x)
    return out


def fail(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(1)


def refuse(op, n):
    for r in S.get("refuse", []):
        if r["op"] == op and int(r["n"]) == int(n):
            fail(r.get("error") or f"HTTP 502: Server Error (https://api.github.com/repos/{REPO}/issues/{n})")


def tick():
    S["clock"] = S.get("clock", 0) + 1
    return "2026-10-09T%02d:%02d:00Z" % (12 + S["clock"] // 60, S["clock"] % 60)


def write(op, n):
    S.setdefault("writes", []).append({"op": op, "n": int(n)})


def jq(value, q):
    if q in (".", None):
        return value
    for part in re.findall(r"\.\w+|\[\d*\]", q):
        if part == "[]":
            continue
        try:
            value = value[int(part[1:-1])] if part.startswith("[") else (
                [v.get(part[1:]) for v in value] if isinstance(value, list) else value[part[1:]])
        except (KeyError, IndexError, TypeError, ValueError):
            return None
    return value


def only(value):
    """Keep only the fields `--json` asked for, as gh does."""
    want = flag("--json")
    if not want or a[:1] == ["api"]:
        return value
    keep = [k.strip() for k in want.split(",")]
    pick = lambda d: {k: d.get(k) for k in keep} if isinstance(d, dict) else d
    return [pick(v) for v in value] if isinstance(value, list) else pick(value)


def out(value):
    value = only(value)
    q = flag("-q", "--jq")
    if q:
        value = jq(value, q)
        if isinstance(value, list) and ".[]" in q:
            print("\n".join("" if v is None else v if isinstance(v, str) else json.dumps(v) for v in value))
            return
        print("" if value is None else value if isinstance(value, (str, int)) else json.dumps(value))
    else:
        print(value if isinstance(value, str) else json.dumps(value))


def number(x):
    return int(str(x).rstrip("/").rsplit("/", 1)[-1].lstrip("#"))


def issue(n):
    i = S["issues"].get(str(n))
    if i is None:
        fail(f"GraphQL: Could not resolve to an issue with the number of {n}. (repository.issue)")
    return i


def pr(p):
    x = S["prs"].get(str(p))
    if x is None:
        fail(f"HTTP 404: Not Found (https://api.github.com/repos/{REPO}/pulls/{p})")
    return x


def pr_state(x):
    return "closed" if x["merged"] or x["state"] == "closed" else "open"


def issue_rest(n):
    if str(n) in S["prs"]:
        x = S["prs"][str(n)]
        return {"number": int(n), "id": 800000 + int(n), "node_id": f"PR_{n}", "title": x["title"], "body": x["body"],
                "state": pr_state(x), "labels": [], "user": {"login": BOT_LOGIN, "type": "Bot"},
                "updated_at": x["updated_at"], "closed_at": x.get("closed_at"), "comments": len(x.get("comments", [])),
                "html_url": f"https://github.com/{REPO}/pull/{n}",
                "pull_request": {"url": f"https://api.github.com/repos/{REPO}/pulls/{n}",
                                 "merged_at": x.get("merged_at")}}
    i = issue(n)
    return {"number": int(n), "id": 900000 + int(n), "node_id": f"I_{n}", "title": i["title"], "body": i["body"],
            "state": i["state"], "labels": [{"name": l} for l in i.get("labels", [])],
            "user": {"login": OWNER_LOGIN, "type": "User"}, "updated_at": i["updated_at"],
            "comments": len(i.get("comments", [])),
            "closed_at": i.get("closed_at"), "html_url": f"https://github.com/{REPO}/issues/{n}"}


def comments_rest(cs):
    return [{"id": k + 1, "user": {"login": c["login"], "type": "Bot" if c["login"] == BOT_LOGIN else "User"},
             "body": c["body"], "created_at": c["at"], "updated_at": c["at"]} for k, c in enumerate(cs)]


def comments_gh(cs):
    return [{"author": {"login": c["login"]}, "body": c["body"], "createdAt": c["at"]} for c in cs]


def pr_rest(p):
    x = pr(p)
    return {"number": int(p), "id": 800000 + int(p), "node_id": f"PR_{p}", "title": x["title"], "body": x["body"],
            "state": pr_state(x), "merged": x["merged"], "merged_at": x.get("merged_at"),
            "merged_by": {"login": x["merged_by"]} if x.get("merged_by") else None, "closed_at": x.get("closed_at"),
            "head": {"ref": x["head_ref"], "sha": x["sha"]}, "base": {"ref": "main"}, "draft": False,
            "user": {"login": BOT_LOGIN, "type": "Bot"}, "updated_at": x["updated_at"],
            "html_url": f"https://github.com/{REPO}/pull/{p}"}


def pr_gh(p):
    x = pr(p)
    return {"number": int(p), "title": x["title"], "body": x["body"],
            "state": "MERGED" if x["merged"] else pr_state(x).upper(), "headRefName": x["head_ref"],
            "headRefOid": x["sha"], "baseRefName": "main", "mergedAt": x.get("merged_at"), "closed": pr_state(x) == "closed",
            "url": f"https://github.com/{REPO}/pull/{p}", "updatedAt": x["updated_at"],
            "comments": comments_gh(x.get("comments", [])),
            "reviews": [{"author": {"login": r["login"]}, "body": r["body"], "state": r["state"], "submittedAt": r["at"]}
                        for r in x.get("reviews", [])],
            "closingIssuesReferences": [{"number": x["closes"]}] if x.get("closes") else []}


def issue_gh(n):
    i = issue(n)
    return {"number": int(n), "title": i["title"], "body": i["body"], "state": i["state"].upper(),
            "comments": comments_gh(i.get("comments", [])), "labels": [{"name": l} for l in i.get("labels", [])],
            "url": f"https://github.com/{REPO}/issues/{n}", "updatedAt": i["updated_at"], "closedAt": i.get("closed_at")}


def prs(head=None, state="open"):
    found = []
    for k in sorted(S["prs"], key=int):
        x = S["prs"][k]
        if head and x["head_ref"] != head.split(":", 1)[-1]:
            continue
        st = pr_state(x)
        if state in ("all", None) or state == st or (state == "merged" and x["merged"]):
            found.append(int(k))
    return found


def text_arg():
    t = flag("--body")
    if t is None:
        p = flag("--body-file", "-F")
        t = sys.stdin.read() if p == "-" else open(p).read()
    return t


def set_issue_body(n, text):
    if str(n) in S["prs"]:
        return set_pr_body(n, text)
    refuse("write-issue", n)
    issue(n)["body"] = text
    issue(n)["updated_at"] = tick()
    write("issue-body", n)
    save()


def set_pr_body(p, text):
    refuse("write-pr", p)
    pr(p)["body"] = text
    pr(p)["updated_at"] = tick()
    write("pr-body", p)
    save()


if a[:2] == ["issue", "view"]:
    n = number(positional()[1])
    refuse("read-issue", n)
    out(issue_gh(n))
    sys.exit(0)
if a[:2] == ["issue", "edit"]:
    set_issue_body(number(positional()[1]), text_arg())
    sys.exit(0)
if a[:2] == ["issue", "comment"]:
    n = number(positional()[1])
    issue(n).setdefault("comments", []).append({"login": BOT_LOGIN, "body": text_arg(), "at": tick()})
    write("comment", n)
    save()
    sys.exit(0)
if a[:2] == ["issue", "list"]:
    st = (flag("--state", "-s") or "open").lower()
    out([issue_gh(int(k)) for k in sorted(S["issues"], key=int) if st == "all" or S["issues"][k]["state"] == st])
    sys.exit(0)
if a[:2] == ["pr", "list"]:
    out([pr_gh(p) for p in prs(flag("--head"), (flag("--state", "-s") or "open").lower())])
    sys.exit(0)
if a[:2] == ["pr", "view"]:
    out(pr_gh(number(positional()[1])))
    sys.exit(0)
if a[:2] == ["pr", "edit"]:
    set_pr_body(number(positional()[1]), text_arg())
    sys.exit(0)
if a[:1] == ["api"]:
    pos = positional()
    path = (pos[0] if pos else "").lstrip("/")
    route, _, query = path.partition("?")
    params = dict(p.partition("=")[::2] for p in query.split("&") if p)
    f = fields()
    method = (flag("-X", "--method") or ("POST" if f and route != "graphql" else "GET")).upper()
    if route == "graphql":
        q = f.get("query", "")
        if "userContentEdits" in q and "issue(" in q:
            n = int(f["i"])
            refuse("read-issue", n)
            i = issue(n)
            out({"data": {"repository": {"issue": {"number": n, "title": i["title"], "body": i["body"],
                                                   "url": f"https://github.com/{REPO}/issues/{n}",
                                                   "userContentEdits": {"nodes": []}}}}})
            sys.exit(0)
        if "closingIssuesReferences" in q:
            x = pr(int(f["p"]))
            nodes = [{"number": x["closes"]}] if x.get("closes") else []
            out({"data": {"repository": {"pullRequest": {"closingIssuesReferences": {"nodes": nodes}}}}})
            sys.exit(0)
        fail(f"fake gh: no such GraphQL query {q[:200]!r}")
    p = f"repos/{REPO}/"
    if not route.startswith(p):
        fail(f"fake gh: no such call {a}")
    r = route[len(p):]
    if r == "issues" and method == "GET":
        st = params.get("state", "open")
        nums = sorted({int(k) for k in S["issues"]} | {int(k) for k in S["prs"]})
        out([issue_rest(n) for n in nums if st == "all" or issue_rest(n)["state"] == st])
        sys.exit(0)
    m = re.fullmatch(r"issues/(\d+)", r)
    if m:
        n = int(m.group(1))
        if method == "PATCH":
            if "body" not in f:
                fail(f"fake gh: no such call {a}")
            set_issue_body(n, f["body"])
        elif str(n) not in S["prs"]:
            refuse("read-issue", n)
        out(issue_rest(n))
        sys.exit(0)
    m = re.fullmatch(r"issues/(\d+)/(comments|events|timeline|sub_issues)", r)
    if m:
        n = int(m.group(1))
        if str(n) not in S["prs"]:
            refuse("read-issue", n)
        holder = S["prs"].get(str(n)) or issue(n)
        if m.group(2) == "comments" and method == "POST":
            holder.setdefault("comments", []).append({"login": BOT_LOGIN, "body": f["body"], "at": tick()})
            write("comment", n)
            save()
            out({"id": 1})
        else:
            out(comments_rest(holder.get("comments", [])) if m.group(2) == "comments" else [])
        sys.exit(0)
    m = re.fullmatch(r"issues/(\d+)/dependencies/(blocked_by|blocking)", r)
    if m and method == "GET":
        issue(int(m.group(1)))
        out([])
        sys.exit(0)
    if r == "pulls" and method == "GET":
        out([pr_rest(n) for n in prs(params.get("head"), params.get("state", "open"))])
        sys.exit(0)
    m = re.fullmatch(r"pulls/(\d+)", r)
    if m:
        n = int(m.group(1))
        if method == "PATCH":
            if "body" not in f:
                fail(f"fake gh: no such call {a}")
            set_pr_body(n, f["body"])
        out(pr_rest(n))
        sys.exit(0)
    m = re.fullmatch(r"pulls/(\d+)/(reviews|comments|files|commits)", r)
    if m and method == "GET":
        x = pr(int(m.group(1)))
        if m.group(2) == "reviews":
            out([{"id": k + 1, "user": {"login": v["login"]}, "state": v["state"], "body": v["body"],
                  "submitted_at": v["at"], "html_url": f"https://github.com/{REPO}/pull/{m.group(1)}#review-{k + 1}"}
                 for k, v in enumerate(x.get("reviews", []))])
        else:
            out([])
        sys.exit(0)
    m = re.fullmatch(r"commits/([^/]+)/(check-runs|pulls|status|check-suites)", r)
    if m and method == "GET":
        sha, what = m.group(1), m.group(2)
        if what == "check-runs":
            runs = S.get("checks", {}).get(sha, [])
            out({"total_count": len(runs), "check_runs": runs})
        elif what == "pulls":
            out([pr_rest(int(k)) for k, x in sorted(S["prs"].items()) if x["sha"] == sha])
        elif what == "status":
            out({"state": "success", "statuses": []})
        else:
            out({"total_count": 0, "check_suites": []})
        sys.exit(0)
    if r == "contents/.github/CODEOWNERS":
        print("* @" + OWNER_LOGIN)
        sys.exit(0)
    if r.startswith("contents/"):
        fail(f"HTTP 404: Not Found (https://api.github.com/{route})")
    if r.startswith("actions/"):
        out({"total_count": 0, "workflow_runs": []})
        sys.exit(0)
fail(f"fake gh: no such call {a}")
'''


# --- the fake GitHub ---------------------------------------------------------------------------------------------

def record(rec, at):
    """A comment the bot posted holding one agent record."""
    return {"login": BOT, "body": f"{agent.MARK}\n**Record**\n\n```json\n{json.dumps(rec)}\n```\n", "at": at}


def plan_record(n, story):
    """A planner record of issue n that passed its check: one criterion and its test."""
    h = {"kind": "user_story", "summary": f"Issue {n} is planned.", "user_story": story,
         "acceptance_criteria": [{"text": f"Criterion one of #{n}.", "source": f"https://github.com/o/r/issues/{n}"}],
         "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": ["Nothing else."],
         "tests": {f"{n}.1": ["tests/test_x.py::test_one"]}, "test_changes": {},
         "links": {"blocked_by": [], "blocks": [], "relates_to": []}}
    return {"role": "planner", "stage": None, "handback": h, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/1", "run_id": "1"}


def review_record(stage):
    """An approving review record at `stage` (plan or pr) that passed its check."""
    return {"role": "reviewer", "stage": stage, "handback": {"verdict": "approve", "summary": "Approved.",
                                                             "blockers": [], "resolved": []},
            "check": {"passed": True, "problems": []}, "run": "https://github.com/o/r/actions/runs/2", "run_id": "2"}


def worker_record():
    """A worker record that passed its check."""
    return {"role": "worker", "stage": None, "handback": {"summary": "Built it.", "changed": ["dokima/x.py"]},
            "check": {"passed": True, "problems": []}, "run": "https://github.com/o/r/actions/runs/3", "run_id": "3"}


def card_of(text):
    """The card block in a body, between its two marks; None when there is none."""
    m = re.search(r"<!-- dokima-card -->.*?<!-- /dokima-card -->", text or "", re.S)
    if not m:
        return None
    # Since #416 the Definition of Done sits last, after the Original issue fold.
    done = (text.rsplit("<!-- dokima-done -->", 1)[1].strip().split("\n")[0] if "<!-- dokima-done -->" in text[m.end():]
            else "")
    return m.group(0) + ("\n" + done if done else "")


def without_issue_link(text, n):
    """The PR's card with its link back to issue n taken out of its top row.

    That is the card the issue itself shows since #452."""
    url = re.escape(f"https://github.com/o/r/issues/{n}")
    return re.sub(rf"^{url} · | · {url}(?= · |$)", "", text or "", count=1, flags=re.M)


def stage_of(text):
    """The stage a card's status line shows (Backlog, Plan, Work, Review or Merged), or None."""
    for line in (card_of(text) or "").splitlines():
        m = re.search(r"\*\*(" + "|".join(STAGES) + r")\*\*", line)
        if m and "Definition of Done" not in line:
            return m.group(1)
    return None


def done_of(text):
    """The Definition of Done a card shows: {All tests, Code review, Owner approval: passed/failed/...}."""
    line = next((l for l in (card_of(text) or "").splitlines() if l.startswith("**Definition of Done:**")), "")
    found = {}
    for part in line.split(" · "):
        alt = re.search(r'alt="([^"]+)"', part)
        for name in ("All tests", "Code review", "Owner approval"):
            if part.rstrip().endswith(name) and alt:
                found[name] = alt.group(1)
    return found


STALE_CARD = "<!-- dokima-card -->\n**Review**\n\nAn old card, drawn before the last event.\n\n<!-- /dokima-card -->"


class Hub:
    """A fake GitHub holding issues #246 and #312 and their PRs #260 and #314."""

    def __init__(self, tmp):
        self.dir = str(tmp)
        os.makedirs(os.path.join(self.dir, "bin"))
        gh = os.path.join(self.dir, "bin", "gh")
        open(gh, "w").write(f"#!{sys.executable}\nBOT_LOGIN = {BOT!r}\nOWNER_LOGIN = {OWNER!r}\n" + FAKE_GH)
        os.chmod(gh, 0o755)
        self.ws = os.path.join(self.dir, "ws")
        shutil.copytree(os.path.join(ROOT, "dokima"), os.path.join(self.ws, "dokima"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(os.path.join(ROOT, ".github"), os.path.join(self.ws, ".github"))
        self.state = {"issues": {}, "prs": {}, "checks": {}, "refuse": [], "writes": [], "clock": 0}
        for n, p in ((246, 260), (312, 314)):
            self.add_issue(n, p)
        self.save()
        self.log = ""

    def add_issue(self, n, p=None, records=True):
        """Add open issue n with a stale card and, given p, its open PR."""
        ask = f"Issue {n}: the owner's own words, kept as written."
        recs = [plan_record(n, f"The owner sees issue {n} done."), review_record("plan")]
        if p:
            recs += [worker_record(), review_record("pr")]
        self.state["issues"][str(n)] = {
            "title": f"Issue {n}", "state": "open", "labels": [], "updated_at": "2026-10-09T01:00:00Z",
            "body": f"{STALE_CARD}\n\n{body.MARKER}\n\n{ask}",
            "comments": [record(r, f"2026-10-09T0{k + 1}:00:00Z") for k, r in enumerate(recs)] if records else []}
        if p:
            sha = f"sha{p}"
            self.state["prs"][str(p)] = {
                "title": f"Issue {n}", "state": "open", "merged": False, "merged_by": None, "head_ref": f"try/issue-{n}",
                "sha": sha, "closes": n, "body": f"{STALE_CARD}\n\nCloses #{n}", "comments": [], "reviews": [],
                "updated_at": "2026-10-09T01:00:00Z"}
            self.state["checks"][sha] = [
                {"name": f"{n}.1 · Criterion one", "status": "completed", "conclusion": "success", "head_sha": sha,
                 "html_url": f"https://github.com/o/r/runs/{p}1"},
                {"name": "all tests", "status": "completed", "conclusion": "success", "head_sha": sha,
                 "html_url": f"https://github.com/o/r/runs/{p}2"}]

    def save(self):
        """Write the fake GitHub's state to its file."""
        json.dump(self.state, open(os.path.join(self.dir, "state.json"), "w"), indent=1)

    def load(self):
        """Read the fake GitHub's state back, as the run left it."""
        self.state = json.load(open(os.path.join(self.dir, "state.json")))
        return self.state

    def merge(self, n, p, by=OWNER):
        """Merge PR p and close issue n on GitHub, redrawing no card."""
        s = self.load()
        s["prs"][str(p)].update(state="closed", merged=True, merged_by=by, merged_at="2026-10-09T09:00:00Z",
                                closed_at="2026-10-09T09:00:00Z", updated_at="2026-10-09T09:00:00Z")
        s["issues"][str(n)].update(state="closed", closed_at="2026-10-09T09:00:00Z", updated_at="2026-10-09T09:00:00Z")
        self.save()

    def no_pr_card(self, p, n):
        """Leave PR p with only its closing line, as after a dropped redraw."""
        s = self.load()
        s["prs"][str(p)]["body"] = f"Closes #{n}"
        self.save()

    def refuse(self, op, n):
        """GitHub refuses `op` (read-issue, write-issue or write-pr) on n with HTTP 502."""
        s = self.load()
        s["refuse"].append({"op": op, "n": n, "error": f"HTTP 502: Server Error (https://api.github.com/repos/o/r/{n})"})
        self.save()

    def issue_body(self, n):
        """Issue n's body as it stands on GitHub."""
        return self.load()["issues"][str(n)]["body"]

    def pr_body(self, p):
        """PR p's body as it stands on GitHub."""
        return self.load()["prs"][str(p)]["body"]

    def writes(self, op=None):
        """Every body or comment the run wrote, of one kind when given."""
        return [w for w in self.load()["writes"] if op is None or w["op"] == op]

    def clear_writes(self):
        """Forget the writes so far."""
        s = self.load()
        s["writes"] = []
        self.save()

    def run(self, event_name, event, k):
        """Play card.yml for one event, directly or through its relays, and return card.yml's Run.

        When card.yml does not start on the event itself, every relay that starts on it is played, and card.yml is
        played for the workflow_run each passing relay sends; the returned Run keeps the relays' Runs in `relays`."""
        r = Run(self, event_name, event)
        if not r.started:
            relay_runs = []
            for name, wf in relays(event_name, event):
                rr = Run(self, event_name, event, wf)
                relay_runs.append(rr)
                if rr.started and not rr.failed():
                    r = Run(self, *relayed(name, event_name, event))
                    if r.started:
                        break
            r.relays = relay_runs
            r.log = "".join(x.log for x in relay_runs) + r.log
        self.log = r.log
        return r


# --- the events GitHub sends -------------------------------------------------------------------------------------

REPOSITORY = {"full_name": "o/r", "name": "r", "owner": {"login": "o"}, "default_branch": "main"}


def sender(who):
    """The sender of an event: the owner, or Dokima's bot."""
    return {"login": BOT + "[bot]", "type": "Bot"} if who == "bot" else {"login": who, "type": "User"}


def issue_event(n, action, who=OWNER):
    """An issues event on issue n."""
    return "issues", {"action": action, "issue": {"number": n, "title": f"Issue {n}", "state": "open"},
                      "sender": sender(who), "repository": REPOSITORY}


def issue_comment(n, who=OWNER, action="created", text="A thought."):
    """A comment on issue n."""
    return "issue_comment", {"action": action, "issue": {"number": n, "title": f"Issue {n}"},
                             "comment": {"body": text, "user": {"login": sender(who)["login"]}},
                             "sender": sender(who), "repository": REPOSITORY}


def pr_payload(n, p, merged=False, state="open"):
    """The pull_request object GitHub puts in a pull request event."""
    return {"number": p, "title": f"Issue {n}", "state": state, "merged": merged, "body": f"Closes #{n}",
            "head": {"ref": f"try/issue-{n}", "sha": f"sha{p}"}, "base": {"ref": "main"},
            "user": {"login": BOT + "[bot]", "type": "Bot"}, "html_url": f"https://github.com/o/r/pull/{p}"}


def pr_comment(n, p, who=OWNER, action="created", text="A thought."):
    """A comment on PR p, which GitHub sends as an issue_comment."""
    return "issue_comment", {"action": action, "issue": {"number": p, "title": f"Issue {n}",
                                                         "pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{p}"}},
                             "comment": {"body": text, "user": {"login": sender(who)["login"]}},
                             "sender": sender(who), "repository": REPOSITORY}


def pr_event(n, p, action, who="bot", merged=False):
    """A pull_request_target event on PR p."""
    state = "closed" if action == "closed" else "open"
    return "pull_request_target", {"action": action, "number": p, "pull_request": pr_payload(n, p, merged, state),
                                   "sender": sender(who), "repository": REPOSITORY}


def review_event(n, p, who=OWNER, action="submitted", state="approved"):
    """A pull_request_review event on PR p."""
    return "pull_request_review", {"action": action, "review": {"state": state, "body": "", "user": {"login": who}},
                                   "pull_request": pr_payload(n, p), "sender": sender(who), "repository": REPOSITORY}


def line_note(n, p, who=OWNER, action="created"):
    """A pull_request_review_comment event (a note on a line) on PR p."""
    return "pull_request_review_comment", {"action": action, "comment": {"body": "Here.", "user": {"login": who}},
                                           "pull_request": pr_payload(n, p), "sender": sender(who),
                                           "repository": REPOSITORY}


def checks_finished(n, p, workflow="Acceptance criteria"):
    """A workflow_run event: the checks of PR p finished."""
    run = {"name": workflow, "head_sha": f"sha{p}", "head_branch": f"try/issue-{n}", "display_title": f"Issue {n}",
           "event": "pull_request_target", "status": "completed", "conclusion": "success",
           "pull_requests": [{"number": p, "head": {"ref": f"try/issue-{n}", "sha": f"sha{p}"}, "base": {"ref": "main"}}]}
    return "workflow_run", {"action": "completed", "workflow": {"name": workflow}, "workflow_run": run,
                            "sender": sender("bot"), "repository": REPOSITORY}


def worker_finished(n):
    """A workflow_run event: the worker finished building issue n.

    Its run is named `worker for #n` and ran on main, with no pull request."""
    run = {"name": "worker", "head_sha": "mainsha", "head_branch": "main", "display_title": f"worker for #{n}",
           "event": "issues", "status": "completed", "conclusion": "success", "pull_requests": []}
    return "workflow_run", {"action": "completed", "workflow": {"name": "worker"}, "workflow_run": run,
                            "sender": sender("bot"), "repository": REPOSITORY}


def schedule():
    """The 15-minute schedule."""
    return "schedule", {"schedule": "*/15 * * * *"}


# --- playing card.yml --------------------------------------------------------------------------------------------

class Null(Nil):
    """A missing value in an expression: null, and null for anything read from it."""

    def __getattr__(self, k):
        return NIL

    def __getitem__(self, k):
        return NIL


NIL = Null()


class Context(Ctx):
    """An expression context read with dots, where a missing name is null."""

    def __getattr__(self, k):
        v = self.get(k, NIL)
        return Context(v) if isinstance(v, dict) and not isinstance(v, Ctx) else v

    def __getitem__(self, k):
        return self.__getattr__(k)


class List(list):
    """A list in an expression, where an index past its end is null."""

    def __getitem__(self, i):
        try:
            return wrap(list.__getitem__(self, i))
        except (IndexError, TypeError):
            return NIL


def wrap(v):
    """A JSON value turned into an expression context."""
    if isinstance(v, dict) and not isinstance(v, Ctx):
        return Context({k: wrap(x) for k, x in v.items()})
    if isinstance(v, list) and not isinstance(v, List):
        return List(wrap(x) for x in v)
    return v


def github_ctx(event_name, event):
    """The `github` context GitHub gives card.yml for one event."""
    ref = "refs/heads/main"
    if event_name in ("pull_request", "pull_request_review", "pull_request_review_comment"):
        ref = f"refs/pull/{event['pull_request']['number']}/merge"
    return wrap({"event_name": event_name, "event": event, "repository": "o/r", "repository_owner": "o", "ref": ref,
                 "sha": "mainsha", "run_id": "42", "run_number": "7", "server_url": "https://github.com",
                 "actor": (event.get("sender") or {}).get("login", "github"), "workflow": "card",
                 "token": "fake-workflow-token"})


def workflow():
    """card.yml, read."""
    return load_yaml(open(CARD_YML).read())


def workflows():
    """Every workflow of the repo but card.yml, read, as {file name: workflow}."""
    out = {}
    for f in sorted(os.listdir(WORKFLOWS)):
        path = os.path.join(WORKFLOWS, f)
        if f.endswith((".yml", ".yaml")) and path != CARD_YML:
            out[f] = load_yaml(open(path).read())
    return out


def listened():
    """The workflows card.yml starts after, by its workflow_run trigger, as {file name: workflow}."""
    t = triggers(workflow()).get("workflow_run")
    names = listed(t.get("workflows")) if isinstance(t, dict) else []
    return {f: wf for f, wf in workflows().items() if wf.get("name") in names}


def relays(event_name, event):
    """The workflows card.yml starts after that start on this event, as [(name, workflow)].

    Only for an event GitHub runs from the pull request's own copy, which card.yml must hear through a relay; any
    other event card.yml hears itself."""
    if event_name not in OWN_COPY:
        return []
    return [(wf.get("name"), wf) for wf in listened().values() if starts(wf, event_name, event)]


def relayed(name, event_name, event):
    """The workflow_run event GitHub sends card.yml when relay `name`, started by this event, passes."""
    x = event.get("pull_request") or {}
    head = x.get("head") or {}
    pulls = [{"number": x["number"], "head": head, "base": x.get("base") or {"ref": "main"}}] if x else []
    run = {"name": name, "head_sha": head.get("sha"), "head_branch": head.get("ref"), "display_title": x.get("title"),
           "event": event_name, "status": "completed", "conclusion": "success", "pull_requests": pulls,
           "actor": event.get("sender"), "triggering_actor": event.get("sender")}
    return "workflow_run", {"action": "completed", "workflow": {"name": name}, "workflow_run": run,
                            "sender": event.get("sender"), "repository": REPOSITORY}


def reaches(event_name, event):
    """True when the event starts card.yml, itself or through a relay."""
    return starts(workflow(), event_name, event) or bool(relays(event_name, event))


def triggers(wf):
    """card.yml's `on:` as {event name: its settings or ''}."""
    on = wf.get("on")
    if isinstance(on, str):
        return {on: ""}
    if isinstance(on, list):
        return {e: "" for e in on}
    return on or {}


def listed(value):
    """A YAML value that may be one string or a list, as a list."""
    if not value:
        return []
    return [value] if isinstance(value, str) else list(value)


def starts(wf, event_name, event):
    """True when card.yml's `on:` starts a run for this event."""
    on = triggers(wf)
    if event_name not in on:
        return False
    t = on[event_name] if isinstance(on[event_name], dict) else {}
    types = listed(t.get("types"))
    if types and event.get("action") not in types:
        return False
    if event_name == "workflow_run" and event["workflow"]["name"] not in listed(t.get("workflows")):
        return False
    return True


def group_of(conc, ctx, status):
    """The concurrency group a `concurrency:` setting gives, filled in; None when there is none."""
    if not conc:
        return None
    g = conc.get("group") if isinstance(conc, dict) else conc
    return fill(g, ctx, status) if g else None


def cancels(conc, ctx, status):
    """True when a `concurrency:` setting cancels the run already in its group (cancel-in-progress), filled in."""
    if not isinstance(conc, dict) or conc.get("cancel-in-progress") in (None, False):
        return False
    v = conc["cancel-in-progress"]
    return v is True or str(fill(v, ctx, status) if isinstance(v, str) else v).strip().lower() == "true"


def order(jobs):
    """Job names in an order their `needs` allow."""
    done, out = set(), []
    while len(out) < len(jobs):
        ready = [j for j in jobs if j not in done and set(listed(jobs[j].get("needs"))) <= done]
        assert ready, "test setup: card.yml's jobs need each other in a loop"
        for j in ready:
            done.add(j)
            out.append(j)
    return out


class Run:
    """One run of card.yml for one event, played as GitHub plays it."""

    def __init__(self, hub, event_name, event, wf=None):
        self.hub, self.event_name, self.event = hub, event_name, event
        wf = workflow() if wf is None else wf
        self.wf = wf
        self.started = starts(wf, event_name, event)
        self.jobs, self.log, self.checkouts = {}, "", []
        self.groups, self.cancelling, self.relays = {}, {}, []
        if not self.started:
            return
        base_ctx = {"github": github_ctx(event_name, event), "vars": Context(), "secrets": Context(), "inputs": Context()}
        self.groups["workflow"] = group_of(wf.get("concurrency"), {**base_ctx, "env": Context()}, {"failed": False})
        self.cancelling["workflow"] = cancels(wf.get("concurrency"), {**base_ctx, "env": Context()}, {"failed": False})
        wf_env = {k: fill(v, {**base_ctx, "env": Context()}, {"failed": False}) for k, v in (wf.get("env") or {}).items()}
        open(os.path.join(hub.dir, "event.json"), "w").write(json.dumps(event))
        jobs = wf.get("jobs") or {}
        for name in order(jobs):
            job = jobs[name]
            assert "strategy" not in job, "test setup: this player cannot run a job with a matrix"
            needs = {j: self.jobs[j] for j in listed(job.get("needs"))}
            ctx = {**base_ctx, "needs": wrap({j: {"result": v["result"], "outputs": v["outputs"]} for j, v in needs.items()}),
                   "env": Context(wf_env)}
            status = {"failed": any(v["result"] == "failure" for v in needs.values()),
                      "cancelled": False}
            cond = condition(job.get("if"))
            skipped_need = any(v["result"] == "skipped" for v in needs.values())
            if (skipped_need and "always()" not in cond) or not evaluate(cond, ctx, status):
                self.jobs[name] = {"result": "skipped", "outputs": {}, "ran_card": False, "wrote": False}
                continue
            self.groups[name] = group_of(job.get("concurrency"), ctx, status)
            self.cancelling[name] = cancels(job.get("concurrency"), ctx, status)
            self.jobs[name] = self.run_job(name, job, ctx, wf_env)

    def run_job(self, name, job, ctx, wf_env):
        """Run one job's steps in order; returns its result, outputs and whether it ran dokima/card.py."""
        hub, status, steps, added = self.hub, {"failed": False}, {}, {}
        job_env = {k: fill(v, {**ctx, "env": Context(wf_env)}, status) for k, v in (job.get("env") or {}).items()}
        base = {"PATH": os.path.join(hub.dir, "bin") + os.pathsep + os.environ["PATH"], "HOME": os.environ.get("HOME", hub.dir),
                "FAKE_GH_DIR": hub.dir, "GITHUB_EVENT_NAME": self.event_name, "GITHUB_REPOSITORY": "o/r",
                "GITHUB_REPOSITORY_OWNER": "o", "GITHUB_RUN_ID": "42", "GITHUB_SERVER_URL": "https://github.com",
                "GITHUB_EVENT_PATH": os.path.join(hub.dir, "event.json"), "GITHUB_WORKSPACE": hub.ws,
                "GITHUB_STEP_SUMMARY": os.path.join(hub.dir, "summary.md"), "RUNNER_TEMP": hub.dir,
                "GITHUB_REF": str(ctx["github"].ref), "CI": "true", "GITHUB_ACTIONS": "true"}
        ran_card, writes = False, len(hub.writes())
        for step in job.get("steps") or []:
            sctx = {**ctx, "steps": wrap(steps), "env": Context({**wf_env, **job_env, **added}),
                    "job": Context(status="failure" if status["failed"] else "success")}
            if not evaluate(condition(step.get("if")), sctx, status):
                continue
            outputs = {}
            uses = str(step.get("uses") or "")
            if "run" in step:
                env = {**base, **wf_env, **job_env, **added}
                env.update({k: fill(v, sctx, status) for k, v in (step.get("env") or {}).items()})
                env["GITHUB_ENV"], env["GITHUB_OUTPUT"] = os.path.join(hub.dir, "step-env"), os.path.join(hub.dir, "step-out")
                for f in (env["GITHUB_ENV"], env["GITHUB_OUTPUT"]):
                    open(f, "w").close()
                script = fill(step["run"], sctx, status)
                ran_card = ran_card or "dokima/card.py" in script or "dokima.card" in script
                open(os.path.join(hub.dir, "step.sh"), "w").write(script)
                p = subprocess.run(github_shell(step, job, self.wf.get("defaults")) + [os.path.join(hub.dir, "step.sh")],
                                   cwd=hub.ws, env=env, capture_output=True, text=True, timeout=300)
                self.log += f"## {name}: {step.get('name') or 'run'} (exit {p.returncode})\n{p.stdout}{p.stderr}\n"
                for path, into in ((env["GITHUB_ENV"], added), (env["GITHUB_OUTPUT"], outputs)):
                    for line in open(path).read().splitlines():
                        if "=" in line:
                            k, v = line.split("=", 1)
                            into[k] = v
                if p.returncode != 0:
                    status["failed"] = True
            elif "actions/checkout" in uses:
                ref = fill((step.get("with") or {}).get("ref") or "", sctx, status) or str(ctx["github"].ref)
                self.checkouts.append(ref)
            elif "create-github-app-token" in uses:
                outputs = {"token": "fake-token", "app-slug": "dokima-runtime"}
            if step.get("id"):
                steps[step["id"]] = {"outputs": outputs, "outcome": "failure" if status["failed"] else "success",
                                     "conclusion": "failure" if status["failed"] else "success"}
        outs = {k: fill(v, {**ctx, "steps": wrap(steps), "env": Context({**wf_env, **job_env, **added})}, status)
                for k, v in (job.get("outputs") or {}).items()}
        wrote = any(w["op"] in ("issue-body", "pr-body") for w in hub.writes()[writes:])
        return {"result": "failure" if status["failed"] else "success", "outputs": outs, "ran_card": ran_card,
                "wrote": wrote}

    def card_ran(self):
        """True when a job that runs dokima/card.py ran for this event."""
        return any(j["ran_card"] for j in self.jobs.values())

    def failed(self):
        """True when any job of the run failed."""
        return any(j["result"] == "failure" for j in self.jobs.values())

    def card_groups(self):
        """The queue each job that wrote a card waited in."""
        return {self.groups.get(name) or self.groups.get("workflow") for name, j in self.jobs.items() if j["wrote"]}

    def all_groups(self):
        """Every concurrency group this run and its relays took a place in."""
        return {g for r in [self, *self.relays] for g in r.groups.values() if g}

    def cancelling_groups(self):
        """The concurrency groups this run took that cancel the run already in them.

        Counts its relays' groups too."""
        return {r.groups[k] for r in [self, *self.relays] for k, c in r.cancelling.items() if c and r.groups.get(k)}

    def errors(self):
        """The ::error lines the run printed, where GitHub names what failed."""
        return [l for l in self.log.splitlines() if l.startswith("::error")]


def must_redraw(hub, event, k):
    """Play the event; fail naming k unless card.yml started, ran dokima/card.py and every job passed."""
    r = hub.run(*event, k)
    what = f"{event[0]} {event[1].get('action') or ''}".strip()
    assert r.started, f"{k}: card.yml does not start on {what}, so the cards are not redrawn"
    assert r.card_ran(), f"{k}: card.yml started on {what} but its card job was skipped"
    assert not r.failed(), f"{k}: card.yml's run on {what} failed:\n{r.log[-3000:]}"
    return r




def stale_again(hub):
    """Put the old card back on every issue and PR."""
    s = hub.load()
    for n, p in ((246, 260), (312, 314)):
        s["issues"][str(n)]["body"] = f"{STALE_CARD}\n\n{body.MARKER}\n\nIssue {n}: the owner's own words."
        s["prs"][str(p)]["body"] = f"{STALE_CARD}\n\nCloses #{n}"
    s["writes"] = []
    hub.save()

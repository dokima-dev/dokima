"""A command either starts its agent or says why on the issue, and a split gets its plan review (#176).

These tests run the workflows' own steps, read from .github/workflows/agent.yml and commands.yml, the way GitHub runs
them: each job's and step's `if:` is evaluated, its `${{ }}` expressions filled in, and its script run with bash in a
clone of a temp git repo whose origin is a local bare repo. Jobs run in the order their `needs` allow, each on its own
fresh clone and its own /tmp. Nothing leaves the machine: a fake `gh` answers from a fake issue, keeps every comment
with each version of it as it is edited in place, and records every call, dispatch and issue it is asked to create
(and can be told to fail one call, the way GitHub does); a fake `claude` hands back a review and notes what GitHub
showed when it started; `pip` and `npm` do nothing unless a test breaks them; pushes to github.com are redirected
to the local origin. Steps that only `uses:` an action are skipped (an app token step gives a fake token), and a job
that `uses:` another workflow is only noted as run. Values a step writes to GITHUB_ENV or GITHUB_OUTPUT are read as
single KEY=value lines.

The fake issue is #57 in repo o/r, owned by `owner-person` through CODEOWNERS, with its pull request #60;
Dokima's code is copied from this repo.
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OWNER = "owner-person"
N = "57"
PR = "60"
SPLIT = {"kind": "feature", "feature": "Stuck issues get unstuck.", "stories": [
    {"title": "First", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/57"}],
     "non_functional": [], "depends_on": []},
    {"title": "Second", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://github.com/o/r/issues/57"}],
     "non_functional": [], "depends_on": [0]}]}
STORY = {"kind": "user_story", "user_story": "u", "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/57"}],
         "non_functional": [], "scope": ["x.py"], "out_of_scope": [], "tests": {"57.1": ["tests/test_x.py::test_a"]}}
APPROVE = {"previous_step": {"did": ["Proposed a split into two stories."], "decided": [], "open": []},
           "stage": "plan", "round": 1, "verdict": "approve", "summary": "The split keeps every promise once.",
           "raises": [], "answers": [],
           "asks": [{"ask": "Fix it.", "source": "https://github.com/o/r/issues/57", "criterion": "S1.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")]}

FAKE_GH = r'''#!/usr/bin/env python3
"""A stand-in for the GitHub CLI: answers from the fake issue, keeps every comment the run writes, records every call.

Comments live in comments.json, each with its id, where it is (issue #57 or pull request #60), its author and every
version of its body, oldest first, the way GitHub keeps a comment that is edited in place. A comment is written by
`gh issue comment` / `gh pr comment` (with --body or --body-file; with --edit-last it edits the newest one there),
or by `gh api` on repos/o/r/issues/N/comments (creates) and repos/o/r/issues/comments/ID (reads, or edits with PATCH),
the body given as -f/-F/--field/--raw-field body=..., body=@file, or --input with a JSON file. `-q`/`--jq` with a
plain `.field` picks that field. The author is Dokima's bot for the app's token and github-actions for the workflow's
own token. `gh issue view` and `gh pr view` show these comments as GitHub would.

options.json, when present, can say: pr_open (the issue has open pull request #60), fail_edits (every edit fails
the way GitHub fails it), fail_card (every new comment fails until the agent has started).
FAKE_GH_FAIL, when set to 'words|message', makes every call starting with those words print the message, the way gh
prints GitHub's error, and exit 1."""
import datetime, json, os, re, sys
d = os.environ["FAKE_GH_DIR"]
a = sys.argv[1:]
opts = json.load(open(os.path.join(d, "options.json"))) if os.path.exists(os.path.join(d, "options.json")) else {}
started = os.path.exists(os.environ.get("FAKE_CLAUDE_MARK", "/nonexistent"))
token = os.environ.get("GH_TOKEN", "")
open(os.path.join(d, "calls.jsonl"), "a").write(json.dumps(a) + "\n")
open(os.path.join(d, "calls-meta.jsonl"), "a").write(json.dumps({"args": a, "token": token, "agent_started": started}) + "\n")
fail = os.environ.get("FAKE_GH_FAIL", "")
if fail and " ".join(a).startswith(fail.split("|", 1)[0]):
    sys.stderr.write(fail.split("|", 1)[1] + "\n")
    sys.exit(1)
def flag(*names):
    for name in names:
        if name in a:
            return a[a.index(name) + 1]
    return None
STORE = os.path.join(d, "comments.json")
def load():
    return json.load(open(STORE)) if os.path.exists(STORE) else []
def save(cs):
    json.dump(cs, open(STORE, "w"), indent=1)
def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
def shown(c):
    url = f"https://github.com/o/r/{'pull' if c['kind'] == 'pr' else 'issues'}/{c['number']}#issuecomment-{c['id']}"
    return {"id": c["id"], "node_id": f"IC_{c['id']}", "html_url": url, "url": url, "body": c["versions"][-1],
            "user": {"login": c["author"]}, "author": {"login": c["author"]}, "createdAt": c["created"], "created_at": c["created"]}
def out(obj):
    q = flag("-q", "--jq")
    if q and re.fullmatch(r"\.[A-Za-z_]+", q.strip()):
        print(obj.get(q.strip()[1:], ""))
    else:
        print(json.dumps(obj))
def refuse_new():
    if opts.get("fail_card") and not started:
        sys.stderr.write("HTTP 502: Server Error (https://api.github.com/repos/o/r/issues/57/comments)\n")
        sys.exit(1)
def refuse_edit():
    if opts.get("fail_edits"):
        sys.stderr.write("HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/comments)\n")
        sys.exit(1)
def create(kind, number, body):
    refuse_new()
    cs = load()
    c = {"id": 5000 + len(cs) + 1, "kind": kind, "number": int(number), "created": now(), "versions": [body],
         "author": "dokima-runtime" if token == "fake-token" else "github-actions"}
    cs.append(c)
    save(cs)
    return c
def edit(cid, body):
    refuse_edit()
    cs = load()
    for c in cs:
        if c["id"] == int(cid):
            c["versions"].append(body)
            save(cs)
            return c
    sys.stderr.write("HTTP 404: Not Found\n")
    sys.exit(1)
def api_body():
    if "--input" in a:
        p = flag("--input")
        return json.load(sys.stdin if p == "-" else open(p)).get("body")
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(a) and a[i + 1].startswith("body="):
            v = a[i + 1][5:]
            if x in ("-F", "--field") and v.startswith("@"):
                return sys.stdin.read() if v == "@-" else open(v[1:]).read()
            return v
    return None
def comments_on(kind, number):
    return [{"author": {"login": c["author"]}, "body": c["versions"][-1], "createdAt": c["created"]}
            for c in load() if c["kind"] == kind and c["number"] == int(number)]
if a[:2] == ["issue", "view"]:
    issue = json.load(open(os.path.join(d, "issue.json")))
    issue["comments"] = issue["comments"] + comments_on("issue", issue["number"])
    print(issue["title"] if flag("-q") == ".title" else json.dumps(issue))
elif a[:2] == ["pr", "view"]:
    print(json.dumps({"number": 60, "headRefName": "try/issue-57", "body": "Closes #57", "comments": comments_on("pr", 60), "reviews": []}))
elif a[:2] in (["issue", "comment"], ["pr", "comment"]):
    kind, number = a[0], a[2]
    body = open(flag("--body-file", "-F")).read() if flag("--body-file", "-F") else flag("--body", "-b")
    if "--edit-last" in a:
        mine = [c for c in load() if c["kind"] == kind and c["number"] == int(number)]
        if not mine:
            sys.stderr.write("no comments found for current user\n")
            sys.exit(1)
        c = edit(mine[-1]["id"], body)
    else:
        c = create(kind, number, body)
    print(shown(c)["html_url"])
elif a[:2] == ["issue", "create"]:
    n = 900 + sum(1 for _ in open(os.path.join(d, "calls.jsonl")) if '"create"' in _) - 1
    print(f"https://github.com/o/r/issues/{n}")
elif a[:2] == ["pr", "list"]:
    if opts.get("pr_open") and "closed" not in a and "merged" not in a:
        print("60" if (flag("-q") or flag("--jq")) else json.dumps([{"number": 60}]))
    else:
        print("" if (flag("-q") or flag("--jq")) else "[]")
elif a[:1] == ["api"] and any(x.startswith("users/") for x in a):
    print("1")
elif a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/issues/\d+/comments", x) for x in a):
    path = next(x for x in a if re.fullmatch(r"/?repos/o/r/issues/\d+/comments", x))
    n = int(path.rstrip("/").split("/")[-2])
    body = api_body()
    if body is None and (flag("-X", "--method") or "GET").upper() == "GET":
        print(json.dumps([shown(c) for c in load() if c["number"] == n]))
    else:
        out(shown(create("pr" if n == 60 else "issue", n, body)))
elif a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/issues/comments/\d+", x) for x in a):
    cid = next(x for x in a if re.fullmatch(r"/?repos/o/r/issues/comments/\d+", x)).rsplit("/", 1)[1]
    if (flag("-X", "--method") or "GET").upper() in ("PATCH", "POST"):
        out(shown(edit(cid, api_body())))
    else:
        c = next((c for c in load() if c["id"] == int(cid)), None)
        if c is None:
            sys.stderr.write("HTTP 404: Not Found\n")
            sys.exit(1)
        out(shown(c))
elif a[:1] == ["api"] and "--paginate" in a:
    print("[]")
elif a[:1] == ["api"] and len(a) == 2 and a[1].startswith("repos/o/r/issues/"):
    n = int(a[1].rsplit("/", 1)[1])
    print(json.dumps({"id": n * 10, "number": n}))
elif a[:1] == ["api"]:
    print("{}")
'''

FAKE_CLAUDE = r'''#!/usr/bin/env python3
"""A stand-in for Claude Code: hands back the review the test chose and leaves a session log naming its model.

When it starts it keeps what GitHub showed at that moment (every comment and every version, at-agent-start.json),
its own environment (agent-env.json) and the time it started (agent-started-at), so a test can see the run as the
agent found it. With FAKE_CANCELLED set, the run is being cancelled: it stops there, as Claude Code does when its step
is stopped, and hands back nothing."""
import json, os, shutil, sys, time
d = os.environ["FAKE_GH_DIR"]
store = os.path.join(d, "comments.json")
json.dump(json.load(open(store)) if os.path.exists(store) else [], open(os.path.join(d, "at-agent-start.json"), "w"))
json.dump(dict(os.environ), open(os.path.join(d, "agent-env.json"), "w"))
open(os.path.join(d, "agent-started-at"), "w").write(str(time.time()))
open(os.environ["FAKE_CLAUDE_MARK"], "w").write("started")
if os.environ.get("FAKE_CANCELLED"):
    sys.exit(143)
shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(os.environ["OUT"], "review.json"))
logs = os.path.join(os.environ["HOME"], ".claude", "projects", "p")
os.makedirs(logs, exist_ok=True)
open(os.path.join(logs, "s.jsonl"), "w").write(json.dumps({"message": {"model": os.environ["MODEL"], "role": "assistant", "content": "Done."}}) + "\n")
print(json.dumps({"num_turns": 1, "duration_ms": 1000, "usage": {}}))
'''

PIP_BROKEN = "ERROR: Could not find a version that satisfies the requirement pytest"


class Nil:
    """A missing value in a GitHub expression: falsy, equal to '' and null, printed as ''."""
    def __getattr__(self, k):
        return NIL

    def __bool__(self):
        return False

    def __eq__(self, o):
        return o in ("", None) or isinstance(o, Nil)

    __hash__ = None

    def __str__(self):
        return ""


NIL = Nil()


class Ctx(dict):
    """A GitHub expression context: dotted access, a missing key is Nil."""
    def __getattr__(self, k):
        v = self.get(k, NIL)
        return Ctx(v) if isinstance(v, dict) and not isinstance(v, Ctx) else v

    def __getitem__(self, k):
        """A name with a dash (`steps.card-key`), read the same way as a dotted one."""
        return self.__getattr__(k)


def evaluate(expr, ctx, status):
    """Evaluate one GitHub expression against the contexts and the status so far (a step's job, or a job's needs)."""
    parts = re.split(r"('[^']*')", expr)
    for i in range(0, len(parts), 2):
        p = parts[i].replace("&&", " and ").replace("||", " or ").replace("!=", "\0")
        p = re.sub(r"!", " not ", p).replace("\0", "!=")
        p = re.sub(r"\.([A-Za-z_]\w*(?:-\w+)+)", lambda m: f"[{m.group(1)!r}]", p)
        p = re.sub(r"\bnull\b", "NIL", re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", p)))
        parts[i] = p
    names = {**ctx, "NIL": NIL, "always": lambda: True,
             "success": lambda: status.get("success", not status["failed"] and not status.get("cancelled")),
             "failure": lambda: status["failed"], "cancelled": lambda: bool(status.get("cancelled")),
             "startsWith": lambda s, p: str(s).lower().startswith(str(p).lower()),
             "contains": lambda s, p: str(p).lower() in str(s).lower(),
             "format": lambda f, *xs: re.sub(r"\{(\d+)\}", lambda m: str(xs[int(m.group(1))]), f)}
    return eval("".join(parts), {"__builtins__": {}}, names)


def fill(text, ctx, status):
    """Fill every ${{ }} in a string."""
    def one(m):
        v = evaluate(m.group(1), ctx, status)
        return "" if v is None or isinstance(v, Nil) else ("true" if v is True else "false" if v is False else str(v))
    return re.sub(r"\$\{\{(.*?)\}\}", one, str(text))


def condition(cond):
    """A job's or step's `if:` the way GitHub reads it: without a status function it also needs success()."""
    cond = str(cond or "success()")
    return cond if re.search(r"\b(always|failure|success|cancelled)\(\)", cond) else f"success() && ({cond})"


def load_yaml(text):
    """A workflow file as nested dicts, lists and strings, read without a YAML library.

    Covers what workflows use: mappings, lists of mappings, `|` and `>` block text, `{a: b}` and `[a, b]` on one line,
    quoted strings and comments. Every value is kept as text."""
    lines = text.split("\n")
    pos = [0]

    def indent(l):
        return len(l) - len(l.lstrip(" "))

    def skip():
        while pos[0] < len(lines) and (not lines[pos[0]].strip() or lines[pos[0]].lstrip().startswith("#")):
            pos[0] += 1

    def scalar(v):
        v = v.strip()
        if v.startswith("{") and v.endswith("}"):
            return {k.strip(): scalar(x) for k, x in (p.split(":", 1) for p in v[1:-1].split(",") if p.strip())}
        if v.startswith("[") and v.endswith("]"):
            return [scalar(p) for p in v[1:-1].split(",") if p.strip()]
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            return v[1:-1]
        return re.sub(r"\s+#(?![^{]*\}\}).*$", "", v)

    def value(rest, at):
        rest = rest.strip()
        if rest[:1] in ("|", ">"):
            body = []
            while pos[0] < len(lines) and (not lines[pos[0]].strip() or indent(lines[pos[0]]) > at):
                body.append(lines[pos[0]])
                pos[0] += 1
            while body and not body[-1].strip():
                body.pop()
            cut = min((indent(l) for l in body if l.strip()), default=0)
            body = [l[cut:] for l in body]
            return " ".join(l.strip() for l in body) if rest[0] == ">" else "\n".join(body) + "\n"
        if rest:
            return scalar(rest)
        skip()
        if pos[0] < len(lines):
            l = lines[pos[0]]
            if indent(l) > at or (indent(l) == at and l.lstrip().startswith("- ")):
                return node()
        return ""

    def node():
        skip()
        l = lines[pos[0]]
        return seq(indent(l)) if l.lstrip().startswith("- ") else mapping(indent(l))

    def mapping(at):
        d = {}
        while True:
            skip()
            if pos[0] >= len(lines):
                return d
            l = lines[pos[0]]
            if indent(l) != at or l.lstrip().startswith("- "):
                return d
            m = re.match(r"\s*([^\s:][^:]*?):(?:\s+(.*))?$", l)
            assert m, f"test setup: cannot read workflow line {l!r}"
            pos[0] += 1
            d[m.group(1)] = value(m.group(2) or "", at)

    def seq(at):
        items = []
        while True:
            skip()
            if pos[0] >= len(lines):
                return items
            l = lines[pos[0]]
            if indent(l) != at or not l.lstrip().startswith("- "):
                return items
            rest = l[at + 2:]
            if re.match(r"[^\s:'\"][^:]*:(\s|$)", rest):
                lines[pos[0]] = " " * (at + 2) + rest
                items.append(mapping(at + 2))
            else:
                pos[0] += 1
                items.append(scalar(rest))

    return node()


def workflow(name):
    """One of this repo's workflows, read."""
    return load_yaml(open(os.path.join(ROOT, ".github", "workflows", name)).read())


def github_shell(step, job, defaults):
    """The bash command GitHub runs a step's script with, on Linux.

    A step, its job's `defaults.run` or the workflow's `defaults.run` may name a shell; the nearest one wins. With
    none, GitHub runs `bash -e {0}`, with no pipefail, so a failure inside a pipe goes unnoticed unless the script
    catches it itself. Only `shell: bash` gets `bash --noprofile --norc -eo pipefail {0}`. Any other shell is refused,
    so the tests never run a step under settings GitHub would not use."""
    shell = step.get("shell")
    for d in ((job.get("defaults") or {}).get("run") or {}, ((defaults or {}).get("run") or {})):
        shell = shell or d.get("shell")
    if not shell:
        return ["bash", "-e"]
    if shell == "bash":
        return ["bash", "--noprofile", "--norc", "-eo", "pipefail"]
    raise AssertionError(f"the tests only know how GitHub runs bash steps, not shell: {shell}")


def sh(cwd, *args):
    """Run git or another command quietly; fail loudly with its output."""
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=git_env(os.environ))
    assert p.returncode == 0, f"test setup failed: {' '.join(args)}\n{p.stdout}{p.stderr}"
    return p.stdout.strip()


def git_env(base):
    """An environment where git has an identity."""
    return {**base, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}


def record_comment(rec, t):
    """A comment the bot posted carrying a record, as GitHub returns it."""
    return {"author": {"login": agent.BOT}, "body": agent.render(rec), "createdAt": t}


def owner_comment(body, t):
    """A comment the owner wrote."""
    return {"author": {"login": OWNER}, "body": body, "createdAt": t}


def planner_record(handback):
    """A passed planner record, the way the workflow writes one."""
    return {"role": "planner", "stage": None, "run_id": "1", "run": "https://github.com/o/r/actions/runs/1",
            "models": ["claude-opus-5-5"], "handback": handback, "check": {"passed": True, "problems": []}}


def review_record(handback):
    """A passed plan review record, the way the workflow writes one."""
    return {"role": "reviewer", "stage": "plan", "run_id": "2", "run": "https://github.com/o/r/actions/runs/2",
            "models": ["claude-opus-5-5"], "handback": handback, "check": {"passed": True, "problems": []}}


class Machine:
    """A temp repo with fake GitHub, Claude, pip and npm, on which workflow jobs run the way GitHub runs them."""

    def __init__(self, tmp, comments, try_branch=False, actor=OWNER, gh_fail="", broken=None, options=None, cancel_at=None):
        self.tmp = t = str(tmp)
        self.cancel_at = cancel_at
        for d in ("bin", "gh", "home", "runner-temp", "jobs"):
            os.makedirs(f"{t}/{d}")
        json.dump(options or {}, open(f"{t}/gh/options.json", "w"))
        tools = {"gh": FAKE_GH, "claude": FAKE_CLAUDE, "pip": "#!/bin/sh\nexit 0\n", "npm": "#!/bin/sh\nexit 0\n"}
        for name, message in (broken or {}).items():
            tools[name] = f"#!/bin/sh\necho '{message}' >&2\nexit 1\n"
        for name, body in tools.items():
            open(f"{t}/bin/{name}", "w").write(body.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
            os.chmod(f"{t}/bin/{name}", 0o755)
        json.dump({"number": int(N), "title": "Stuck issue", "body": "Fix it.", "comments": comments}, open(f"{t}/gh/issue.json", "w"))
        # A plan review lists the owner's ask under one of the plan's criteria: a story's 57.1 or a split's S1.1.
        split = any('"kind": "feature"' in c.get("body", "") for c in comments if isinstance(c, dict))
        json.dump({**APPROVE, "asks": [{**APPROVE["asks"][0], "criterion": "S1.1" if split else "57.1"}]}, open(f"{t}/review.json", "w"))
        # The repo: Dokima's code from this checkout, owned by owner-person, pushed to a local origin.
        src = f"{t}/src"
        shutil.copytree(os.path.join(ROOT, "dokima"), f"{src}/dokima", ignore=shutil.ignore_patterns("__pycache__"))
        # AGENTS.md too, as on main: the river checks the owner's words a plan reviewer quotes from it.
        shutil.copy(os.path.join(ROOT, "AGENTS.md"), f"{src}/AGENTS.md")
        os.makedirs(f"{src}/.github")
        open(f"{src}/.github/CODEOWNERS", "w").write(f"* @{OWNER}\n")
        sh(t, "git", "init", "-q", "--bare", "-b", "main", f"{t}/origin.git")
        sh(src, "git", "init", "-q", "-b", "main")
        sh(src, "git", "add", "-A")
        sh(src, "git", "commit", "-qm", "main")
        sh(src, "git", "remote", "add", "origin", f"{t}/origin.git")
        sh(src, "git", "push", "-q", "origin", "main")
        self.main_sha = sh(src, "git", "rev-parse", "HEAD")
        self.try_sha = None
        if try_branch:
            sh(src, "git", "checkout", "-q", "-b", f"try/issue-{N}")
            os.makedirs(f"{src}/tests")
            open(f"{src}/tests/test_x.py", "w").write('def test_a():\n    """A."""\n')
            sh(src, "git", "add", "-A")
            sh(src, "git", "commit", "-qm", "tests")
            sh(src, "git", "push", "-q", "origin", f"try/issue-{N}")
            self.try_sha = sh(src, "git", "rev-parse", "HEAD")
        self.actor, self.gh_fail = actor, gh_fail
        self.log, self.failed_step, self.cancelled_step = [], None, None

    def base_env(self, event_name):
        """The environment every step starts from."""
        t = self.tmp
        return git_env({"PATH": f"{t}/bin:" + os.environ["PATH"], "HOME": f"{t}/home", "FAKE_GH_DIR": f"{t}/gh",
                        "FAKE_GH_FAIL": self.gh_fail, "FAKE_REVIEW": f"{t}/review.json", "FAKE_CLAUDE_MARK": f"{t}/claude-started",
                        "GITHUB_REPOSITORY": "o/r", "GITHUB_REPOSITORY_OWNER": "o", "GITHUB_RUN_ID": "42",
                        "GITHUB_SERVER_URL": "https://github.com", "GITHUB_ACTOR": self.actor, "GITHUB_EVENT_NAME": event_name,
                        "GITHUB_EVENT_PATH": f"{t}/event.json", "GITHUB_STEP_SUMMARY": f"{t}/summary.md",
                        "RUNNER_TEMP": f"{t}/runner-temp", "GIT_CONFIG_COUNT": "1",
                        "GIT_CONFIG_KEY_0": f"url.file://{t}/origin.git.insteadOf",
                        "GIT_CONFIG_VALUE_0": "https://x-access-token:fake-token@github.com/o/r.git"})

    def run_job(self, name, job, ctx, event_name, paths, defaults=None):
        """Run one job's steps in order on a fresh clone, keeping its status, env and step outputs; returns its result.

        `defaults` is the workflow's own `defaults:` block, so each step gets the shell GitHub would give it. When the
        machine was told to cancel at a step (cancel_at, its name), the run is cancelled while that step runs, the way
        the Cancel button on the Actions page does: its script runs with FAKE_CANCELLED set, so the fake agent stops
        without handing anything back, the step ends cancelled whatever its exit code, and from then on only steps
        whose `if:` holds with success() false and cancelled() true run, as GitHub runs them; job.status says
        cancelled."""
        t = self.tmp

        def moved(s):
            for a, b in paths:
                s = s.replace(a, b)
            return s
        for _, b in paths:
            os.makedirs(b, exist_ok=True)
        ws = f"{t}/jobs/{name}/ws"
        sh(t, "git", "clone", "-q", f"{t}/origin.git", ws)
        status = {"failed": False}
        steps_ctx, added = {}, {}
        job_env = {k: moved(fill(v, {**ctx, "env": Ctx()}, status)) for k, v in (job.get("env") or {}).items()}
        base = self.base_env(event_name)
        for step in job.get("steps") or []:
            job_status = "cancelled" if status.get("cancelled") else "failure" if status["failed"] else "success"
            sctx = {**ctx, "steps": Ctx(steps_ctx), "env": Ctx({**job_env, **added}), "job": Ctx(status=job_status)}
            if not evaluate(condition(step.get("if")), sctx, status):
                continue
            label = step.get("name") or step.get("uses") or step.get("id")
            outputs = {}
            cancel = bool(self.cancel_at) and label == self.cancel_at and not status.get("cancelled")
            if "run" in step:
                env = {**base, **job_env, **added, **({"FAKE_CANCELLED": "1"} if cancel else {})}
                env.update({k: moved(fill(v, sctx, status)) for k, v in (step.get("env") or {}).items()})
                env["GITHUB_ENV"], env["GITHUB_OUTPUT"] = f"{t}/step-env", f"{t}/step-output"
                for f in (env["GITHUB_ENV"], env["GITHUB_OUTPUT"]):
                    open(f, "w").close()
                open(f"{t}/step.sh", "w").write(moved(fill(step["run"], sctx, status)))
                p = subprocess.run(github_shell(step, job, defaults) + [f"{t}/step.sh"], cwd=ws,
                                   env=env, capture_output=True, text=True, timeout=120)
                self.log.append(f"## {name}: {label} (exit {p.returncode})\n{p.stdout[-1500:]}{p.stderr[-1500:]}")
                for l in open(env["GITHUB_ENV"]).read().splitlines():
                    if "=" in l:
                        k, v = l.split("=", 1)
                        added[k] = v
                for l in open(env["GITHUB_OUTPUT"]).read().splitlines():
                    if "=" in l:
                        k, v = l.split("=", 1)
                        outputs[k] = v
                if cancel:
                    self.log[-1] = self.log[-1].replace(f"(exit {p.returncode})", "(cancelled)", 1)
                elif p.returncode != 0:
                    status["failed"] = True
                    self.failed_step = self.failed_step or label
            elif "create-github-app-token" in str(step.get("uses")):
                outputs = {"token": "fake-token", "app-slug": "dokima-runtime"}
            if cancel:
                status["cancelled"], self.cancelled_step = True, label
            if step.get("id"):
                steps_ctx[step["id"]] = {"outputs": outputs, "outcome": "cancelled" if cancel else
                                         "failure" if status["failed"] else "success"}
        self.env = {**job_env, **added}
        out = {k: fill(v, {**ctx, "steps": Ctx(steps_ctx), "env": Ctx(self.env)}, status) for k, v in (job.get("outputs") or {}).items()}
        return ("cancelled" if status.get("cancelled") else "failure" if status["failed"] else "success"), out

    def calls(self):
        """Every call made to the fake gh, as argument lists."""
        path = f"{self.tmp}/gh/calls.jsonl"
        return [json.loads(l) for l in open(path)] if os.path.exists(path) else []

    def comments(self):
        """Every comment the run wrote, oldest first, as the fake GitHub keeps it: id, kind (issue or pr), number,
        author and every version of its body."""
        path = f"{self.tmp}/gh/comments.json"
        return json.load(open(path)) if os.path.exists(path) else []

    def posted(self):
        """Every comment the run wrote, as {where, author, body}: where it is and its body as it stands now, after any
        edits."""
        return [{"where": [c["kind"], "comment", str(c["number"])], "author": c["author"], "body": c["versions"][-1]}
                for c in self.comments()]

    def dispatches(self):
        """Every signal sent to start another stage."""
        return [c for c in self.calls() if c[:1] == ["api"] and any("dispatches" in x for x in c)]

    def created_issues(self):
        """Every issue the run asked GitHub to create."""
        return [c for c in self.calls() if c[:2] == ["issue", "create"]]

    def agent_started(self):
        """True when the fake Claude Code was started."""
        return os.path.exists(f"{self.tmp}/claude-started")

    def tail(self):
        """The failed step's output, then the last steps' output, for a failure message."""
        first = [l for l in self.log if self.failed_step and f": {self.failed_step} (" in l.split("\n")[0]][:1]
        return "\n".join(first + self.log[-3:])[-3000:]


class Run(Machine):
    """One run of the agent workflow (agent.yml), started by hand by the actor."""

    def __init__(self, tmp, role, stage, comments, try_branch=False, actor=OWNER, broken=None, options=None, review=None,
                 cancel_at=None):
        super().__init__(tmp, comments, try_branch, actor, broken=broken, options=options, cancel_at=cancel_at)
        if review is not None:
            json.dump(review, open(f"{self.tmp}/review.json", "w"))
        t = self.tmp
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": role, "stage": stage, "issue": N}}))
        ctx = {"inputs": Ctx(role=role, stage=stage, issue=N),
               "github": Ctx(event_name="workflow_dispatch", actor=actor, event=Ctx(), run_id="42", run_attempt="1",
                             server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf = workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        self.failed = self.result == "failure"

    def board(self):
        """Where the run put the card, as written for the board step ('Plan needs'), or '' when it wrote nothing."""
        out = self.env.get("OUT", "")
        path = os.path.join(out, "board.txt")
        return open(path).read().strip() if out and os.path.exists(path) else ""


class Listener(Machine):
    """One run of the command listener (commands.yml) on a comment, every job in the order its `needs` allow."""

    def __init__(self, tmp, body, comments, actor=OWNER, on_pr=False, gh_fail=""):
        super().__init__(tmp, comments, actor=actor, gh_fail=gh_fail)
        t = self.tmp
        number = int(PR if on_pr else N)
        issue = {"number": number, **({"pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{number}"}} if on_pr else {})}
        event = {"comment": {"body": body, "user": {"login": actor, "type": "User"}}, "issue": issue}
        open(f"{t}/event.json", "w").write(json.dumps(event))
        github = Ctx(event_name="issue_comment", actor=actor, event=event, run_id="42", run_attempt="1",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        wf = workflow("commands.yml")
        jobs = wf["jobs"]
        self.results, outputs, self.ran = {}, {}, []
        while len(self.results) < len(jobs):
            for name, job in jobs.items():
                needs = job.get("needs") or []
                needs = [needs] if isinstance(needs, str) else needs
                if name in self.results or any(n not in self.results for n in needs):
                    continue
                res = [self.results[n] for n in needs]
                status = {"failed": "failure" in res, "success": all(r == "success" for r in res)}
                ctx = {"github": github, "inputs": Ctx(), "vars": Ctx(DOKIMA_APP_ID="1"),
                       "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                       "needs": Ctx({n: {"result": self.results[n], "outputs": outputs.get(n, {})} for n in needs})}
                if not evaluate(condition(job.get("if")), ctx, status):
                    self.results[name] = "skipped"
                    continue
                self.ran.append(name)
                if "uses" in job:
                    self.results[name] = "success"
                    continue
                self.results[name], outputs[name] = self.run_job(name, job, ctx, "issue_comment",
                                                                 [("/tmp/", f"{t}/jobs/{name}/tmp/")], wf.get("defaults"))
        self.failed = "failure" in self.results.values()

    def agent_run_started(self):
        """True when the listener started the agent workflow."""
        return any("uses" in job and name in self.ran for name, job in workflow("commands.yml")["jobs"].items())


SPLIT_PROPOSED = [owner_comment("/plan", "2026-10-07T10:00:00Z"),
                  record_comment(planner_record(SPLIT), "2026-10-07T10:10:00Z")]
SPLIT_APPROVED = SPLIT_PROPOSED + [record_comment(review_record(APPROVE), "2026-10-07T10:20:00Z")]
STORY_PLANNED = [owner_comment("/plan", "2026-10-07T10:00:00Z"), record_comment(planner_record(STORY), "2026-10-07T10:10:00Z")]
STORY_APPROVED = STORY_PLANNED + [record_comment(review_record(APPROVE), "2026-10-07T10:20:00Z"),
                                  owner_comment("/work", "2026-10-07T10:30:00Z")]


def test_the_plan_reviewer_starts_on_a_split_with_no_try_branch(record_property, tmp_path):
    """The plan reviewer starts on an issue whose planner proposed a split, though the issue has no try branch.

    Runs the agent workflow for the reviewer at the plan stage on issue #57, whose newest record is a split and which
    has no try/issue-57 branch. The run must get through every step before the agent, start the agent, check its
    review and post its record on the issue, and it must start from main. Two neighbours keep their old behaviour: with
    a try branch the plan reviewer still starts on that branch, and the pull request reviewer, which has no work to
    look at without a branch, still does not start."""
    record_property("proves", "176.1")
    r = Run(tmp_path / "split", "reviewer", "plan", SPLIT_PROPOSED)
    assert r.agent_started(), (f"176.1: the plan reviewer never started on a split with no try/issue-57 branch; "
                               f"it stopped at '{r.failed_step}':\n{r.tail()}")
    assert not r.failed, f"176.1: the plan review of a split failed at '{r.failed_step}':\n{r.tail()}"
    assert r.env.get("BASE") == r.main_sha, "176.1: with no try branch the plan reviewer did not start from main"
    recs = agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in r.posted()])
    assert [(x["role"], x["stage"], x["check"]["passed"]) for x in recs] == [("reviewer", "plan", True)], \
        f"176.1: the plan review of the split did not post exactly one passed review record: {recs}"

    r = Run(tmp_path / "branch", "reviewer", "plan", SPLIT_PROPOSED, try_branch=True)
    assert r.agent_started() and r.env.get("BASE") == r.try_sha, \
        f"176.1: with a try branch the plan reviewer no longer starts on it:\n{r.tail()}"

    r = Run(tmp_path / "pr", "reviewer", "pr", SPLIT_PROPOSED)
    assert not r.agent_started(), "176.1: the pull request reviewer started with no try branch and so no work to review"


def test_a_reviewed_split_stops_for_the_owner_and_files_nothing_before_work(record_property, tmp_path, monkeypatch, capsys):
    """A split goes planner, reviewer, then stops and mentions the owner; its child issues are filed only after `/work`.

    Runs the plan review of a proposed split with no try branch, the reviewer approving. Its posted card must end with
    a Next line mentioning the owner, the card must carry the Needs you pill, no next stage may start and no issue may
    be filed. Then, as commands.yml decides what `/work` does: before the review the issue is not an approved split
    (so `/work` files nothing), and after the approving review it is one, which is what makes `/work` file the stories."""
    record_property("proves", "176.2")
    r = Run(tmp_path / "split", "reviewer", "plan", SPLIT_PROPOSED)
    assert r.agent_started(), f"176.2: the reviewer never reviewed the proposed split; it stopped at '{r.failed_step}':\n{r.tail()}"
    bodies = [p["body"] for p in r.posted()]
    assert len(bodies) == 1, f"176.2: the plan review posted {len(bodies)} comments, expected its one record"
    assert f"**Next:** @{OWNER}" in bodies[0], f"176.2: the approved split did not stop and mention the owner:\n{bodies[0][-600:]}"
    assert r.dispatches() == [], f"176.2: the approved split started another stage on its own: {r.dispatches()}"
    assert r.created_issues() == [], "176.2: child issues were filed before the owner's /work"
    assert r.board().endswith("needs"), f"176.2: the card does not show Needs you after the split was approved: {r.board()!r}"

    def kind_after(comments):
        issue = {"number": int(N), "title": "t", "body": "b", "comments": comments}
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        monkeypatch.setattr(agent, "gh", lambda *a: json.dumps(issue) if a[:2] == ("issue", "view") else "[]")
        agent.main(["agent", "kind", N])
        return capsys.readouterr().out.strip()
    assert kind_after(SPLIT_PROPOSED) == "", "176.2: /work would file the stories of a split no reviewer has approved"
    assert kind_after(SPLIT_APPROVED) == "feature", "176.2: /work would not file the stories of the approved split"


def assert_says_why_and_stops(r, reason, crit, where=N, board=True):
    """The run posted exactly one failed record where it should, naming the reason, mentioning the owner, starting nothing."""
    assert not r.agent_started(), f"{crit}: the agent started though its start should have failed"
    posts = r.posted()
    assert len(posts) == 1, f"{crit}: a failure at '{r.failed_step}' posted {len(posts)} comments, expected one:\n{r.tail()}"
    assert posts[0]["where"][1] == "comment" and where in posts[0]["where"], \
        f"{crit}: the failure was not posted on #{where}, where it belongs: {posts[0]['where']}"
    body = posts[0]["body"]
    recs = agent.records([{"author": {"login": agent.BOT}, "body": body}])
    assert len(recs) == 1, f"{crit}: the failure comment is not a record the bot can read back:\n{body[:600]}"
    assert recs[0]["check"]["passed"] is False, f"{crit}: the failure's record says it passed"
    assert reason.lower() in body.lower(), f"{crit}: the comment does not say why ({reason!r}):\n{body[:800]}"
    assert "hand-back rejected" not in body, f"{crit}: the comment blames a hand-back, but the agent never started:\n{body[:600]}"
    assert f"**Next:** @{OWNER}" in body, f"{crit}: the failure does not stop and mention the owner:\n{body[-600:]}"
    if board:
        assert r.board().endswith("needs"), f"{crit}: the card does not show Needs you after the start failure: {r.board()!r}"
    assert r.dispatches() == [], f"{crit}: a failure started another stage: {r.dispatches()}"


def test_a_start_failure_says_why_on_the_issue_and_stops_for_the_owner(record_property, tmp_path):
    """A run that fails at any step before its agent starts posts a record on the issue saying why and mentions the owner.

    Five failures before the agent, each run through the whole agent workflow: a run started by someone who is not a
    code owner fails at the code-owner gate, a worker on an issue with no try branch fails at the starting branch, a
    worker whose plan nobody approved fails building its pack, a worker whose tools fail to install fails at the
    install step, and a worker started on an approved split fails the pack check. Each must post one record on the
    issue that names its own reason (not a code owner, try/issue-57, no passed plan, the install step by name, plan.json
    is a split), end with a Next line mentioning the owner, put Needs you on the card and start no other stage. A run
    whose agent does start still posts only its own passed record, with no failure record beside it."""
    record_property("proves", "176.3")
    r = Run(tmp_path / "gate", "worker", "", STORY_APPROVED, try_branch=True, actor="stranger")
    assert r.failed_step, "176.3: setup: the run started by someone who is not a code owner did not fail"
    assert_says_why_and_stops(r, "not a code owner", "176.3")
    r = Run(tmp_path / "branch", "worker", "", STORY_APPROVED)
    assert r.failed_step, "176.3: setup: the worker with no try branch did not fail"
    assert_says_why_and_stops(r, f"try/issue-{N}", "176.3")
    r = Run(tmp_path / "pack", "worker", "", STORY_PLANNED, try_branch=True)
    assert r.failed_step, "176.3: setup: the worker with no approved plan did not fail"
    assert_says_why_and_stops(r, "no passed plan", "176.3")
    r = Run(tmp_path / "install", "worker", "", STORY_APPROVED, try_branch=True, broken={"pip": PIP_BROKEN})
    assert r.failed_step, "176.3: setup: the worker whose install failed did not fail"
    assert_says_why_and_stops(r, "Install pytest and Claude Code", "176.3")
    r = Run(tmp_path / "check", "worker", "", SPLIT_APPROVED + [owner_comment("/work", "2026-10-07T10:30:00Z")], try_branch=True)
    assert r.failed_step, "176.3: setup: the worker started on an approved split did not fail its pack check"
    assert_says_why_and_stops(r, "plan.json is a split", "176.3")

    r = Run(tmp_path / "good", "reviewer", "plan", STORY_PLANNED, try_branch=True)
    recs = agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in r.posted()])
    assert r.agent_started() and not r.failed, f"176.3: a plan review that should start did not:\n{r.tail()}"
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("reviewer", True)], \
        f"176.3: a run whose agent started posted more than its own passed record: {recs}"


def test_a_failed_command_says_why_and_stops_for_the_owner(record_property, tmp_path):
    """A code owner's command that fails in the listener before any agent starts says why where it was written.

    Runs the command listener on two failures: `/review` on pull request #60 when GitHub fails to answer which issue
    the pull request belongs to, and `/work` on an approved split when GitHub refuses to create the stories' issues.
    Each must post one record where the command was written that carries GitHub's error, ends with a Next line
    mentioning the owner, and starts no agent. Three good cases stay as they are: `/work` on an approved split that
    files fine posts only its passed "Split filed" record, `/plan` from the owner starts the agent and posts only its
    queued card (#186), which is not a record,
    and `/plan` from someone who is not a code owner gets no reply and starts nothing."""
    record_property("proves", "176.4")
    gone = "GraphQL: Could not resolve to a PullRequest with the number of 60. (repository.pullRequest)"
    r = Listener(tmp_path / "route", "/review", SPLIT_APPROVED, on_pr=True, gh_fail=f"pr view|{gone}")
    assert r.failed_step, "176.4: setup: the listener did not fail when GitHub could not find the pull request"
    assert not r.agent_run_started(), "176.4: the agent workflow started though the command could not be routed"
    assert_says_why_and_stops(r, gone, "176.4", where=PR, board=False)

    refused = "HTTP 403: Resource not accessible by integration (https://api.github.com/repos/o/r/issues)"
    r = Listener(tmp_path / "split", "/work", SPLIT_APPROVED, gh_fail=f"issue create|{refused}")
    assert r.failed_step, "176.4: setup: the listener did not fail when GitHub refused to file the stories"
    assert not r.agent_run_started(), "176.4: a worker started on an approved split"
    assert_says_why_and_stops(r, refused, "176.4", board=False)

    r = Listener(tmp_path / "filed", "/work", SPLIT_APPROVED)
    recs = agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in r.posted()])
    assert not r.failed, f"176.4: filing an approved split failed:\n{r.tail()}"
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("split", True)], \
        f"176.4: filing an approved split posted more than its own Split filed record: {recs}"
    r = Listener(tmp_path / "plan", "/plan", STORY_PLANNED)
    cards = r.posted()
    assert not r.failed and r.agent_run_started() and len(cards) == 1 and \
        not agent.records([{"author": {"login": agent.BOT}, "body": cards[0]["body"]}]), \
        f"176.4: the owner's /plan no longer just starts the planner with its one queued card: started={r.agent_run_started()} posted={cards}"
    r = Listener(tmp_path / "stranger", "/plan", STORY_PLANNED, actor="stranger")
    assert not r.failed and not r.agent_run_started() and r.posted() == [], \
        f"176.4: a stranger's /plan got a reply or started something: started={r.agent_run_started()} posted={r.posted()}"


def test_a_start_failure_still_fails_the_run(record_property, tmp_path):
    """A run or command that fails before its agent starts still ends as a failed run on GitHub, after saying why.

    Runs the worker on an issue with no try branch, and the listener on a `/work` whose split GitHub refuses to file:
    each posts its comment saying why, and the run itself still ends failed, so a failure is never shown as a success."""
    record_property("proves", "176.5")
    r = Run(tmp_path / "branch", "worker", "", STORY_PLANNED)
    assert len(r.posted()) == 1, f"176.5: the start failure posted {len(r.posted())} comments, expected one:\n{r.tail()}"
    assert r.failed, "176.5: the run that failed before its agent started ended as a success"
    r = Listener(tmp_path / "split", "/work", SPLIT_APPROVED, gh_fail="issue create|HTTP 403: Resource not accessible by integration")
    assert len(r.posted()) == 1, f"176.5: the failed command posted {len(r.posted())} comments, expected one:\n{r.tail()}"
    assert r.failed, "176.5: the command that failed before any agent started ended as a success"

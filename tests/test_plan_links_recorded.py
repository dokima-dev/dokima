"""Once a plan passes review, code records its links and redraws both cards (#252).

Story 3 of #231.

The planner's plan.json carries `links`: three lists of open issue numbers, `blocked_by`, `blocks` and `relates_to`.
When the plan reviewer approves the plan, `python3 -m dokima.agent next N OUT` (the step of agent.yml that decides
what follows a run, given the run's record in OUT/record.json) records them: each blocked_by link as GitHub's own
blocked-by link on this issue, each blocks link as the other issue blocked by this one, and it removes a blocking link
the previous approved plan had and the new one dropped. Then it redraws the card of this issue and of every issue a
link was added to or dropped from, so the other issue's card shows the link from its own side. Relates to has no
GitHub link and no comment is ever posted for it; how the other card learns of it is the worker's choice, but the
link must still show after that card is redrawn again by `python3 dokima/card.py` (card.yml's own redraw).

When recording would make issues block each other, directly or through other issues, nothing is recorded and the
river stops for the owner, saying which issues. When GitHub refuses a link, the river stops and says which link and why.

Every test runs the real commands as subprocesses against a fake GitHub: a `gh` program put first on PATH that keeps
its state in one JSON file (issues with their bodies, comments and labels, and blocked-by links) and logs every call.
It answers what Dokima calls today: `gh issue view/comment/edit`, `gh pr list`, and `gh api` for issues
(GET and PATCH), their events, comments, sub-issues, the GraphQL issue query of dokima/plan.py, pulls, contents
(only .github/CODEOWNERS exists), worker runs, commits, dispatches, and GitHub's REST dependency endpoints:
GET repos/o/r/issues/N/dependencies/blocked_by and .../blocking, POST .../blocked_by -F issue_id=<the blocker's id>,
DELETE .../blocked_by/<the blocker's id>. Any other call fails, the way an unknown GitHub path does.
"""
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import agent, body  # noqa: E402

N = 252
OWNER = "boss"
BOT = agent.BOT
SRC = f"https://github.com/o/r/issues/{N}"
NONE = {"blocked_by": [], "blocks": [], "relates_to": []}
ASK = "Once the plan passes review, record its links.\n\nThe owner's own words, kept as written."
LABELS = {"blocked_by": "Blocked by", "blocks": "Blocks", "relates_to": "Relates to"}

FAKE_GH = r'''
import json, os, re, sys
D = os.environ["FAKE_GH_DIR"]
STATE = os.path.join(D, "state.json")
S = json.load(open(STATE))
a = sys.argv[1:]
open(os.path.join(D, "calls.jsonl"), "a").write(json.dumps(a) + "\n")
WITH_VALUE = {"-X", "--method", "-f", "-F", "--raw-field", "--field", "-H", "--header", "--input", "-q", "--jq",
              "-R", "--repo", "--json", "--body", "--body-file", "--head", "--state", "--title", "--label", "-t",
              "--template", "--reason", "--comment"}


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


def write(op):
    S.setdefault("writes", []).append(op)


def issue(n):
    i = S["issues"].get(str(n))
    if i is None:
        fail(f"HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/{n})")
    return i


def obj(n):
    i = issue(n)
    return {"number": int(n), "id": 900000 + int(n), "node_id": f"I_{n}", "title": i["title"], "body": i["body"],
            "state": i.get("state", "open"), "labels": [{"name": l} for l in i.get("labels", [])],
            "html_url": f"https://github.com/o/r/issues/{n}", "url": f"https://github.com/o/r/issues/{n}"}


def deps(n):
    return S.setdefault("deps", {}).setdefault(str(n), [])


def refused(op, n, other):
    for r in S.get("fail", []):
        if r["op"] == op and r["issue"] == int(n) and r["blocked_by"] == int(other):
            fail(r["error"])


def out(value):
    q = flag("-q", "--jq")
    if q:
        for name, idx in re.findall(r"\.(\w+)|\[(\d+)\]", q):
            try:
                value = value[int(idx)] if idx else value[name]
            except (KeyError, IndexError, TypeError):
                value = None
                break
        print("" if value is None else value if isinstance(value, (str, int)) else json.dumps(value))
    else:
        print(value if isinstance(value, str) else json.dumps(value))


def number(x):
    return int(x.rstrip("/").rsplit("/", 1)[-1].lstrip("#"))


if a[:2] == ["issue", "view"]:
    n = number(a[2])
    o = obj(n)
    o["comments"] = issue(n).get("comments", [])
    out(o)
    sys.exit(0)
if a[:2] == ["issue", "comment"]:
    n = number(a[2])
    text = flag("--body")
    if text is None:
        p = flag("--body-file")
        text = sys.stdin.read() if p == "-" else open(p).read()
    issue(n).setdefault("comments", []).append({"author": {"login": BOT_LOGIN}, "body": text,
                                                "createdAt": "2026-10-09T23:59:00Z"})
    write({"op": "comment", "issue": n})
    save()
    sys.exit(0)
if a[:2] == ["issue", "edit"]:
    n = number(a[2])
    text = flag("--body")
    if text is None:
        p = flag("--body-file")
        text = sys.stdin.read() if p == "-" else open(p).read()
    issue(n)["body"] = text
    write({"op": "body", "issue": n})
    save()
    sys.exit(0)
if a[:2] == ["pr", "list"]:
    out([])
    sys.exit(0)
if a[:1] == ["api"]:
    pos = positional()
    path = (pos[0] if pos else "").lstrip("/")
    route = path.split("?", 1)[0]
    f = fields()
    method = (flag("-X", "--method") or ("POST" if f and route != "graphql" else "GET")).upper()
    if route == "graphql":
        q = f.get("query", "")
        if "issue(" in q and "body" in q:  # the issue read of dokima/plan.py fetch_issue
            o = obj(int(f["i"]))
            out({"data": {"repository": {"issue": {"number": o["number"], "title": o["title"], "body": o["body"],
                                                   "url": o["url"], "userContentEdits": {"nodes": []}}}}})
            sys.exit(0)
        out({"data": {}})
        sys.exit(0)
    m = re.fullmatch(r"repos/o/r/issues/(\d+)/dependencies/blocked_by(?:/(\d+))?", route)
    if m:
        n = int(m.group(1))
        issue(n)
        if method == "GET":
            out([obj(b) for b in deps(n)])
        elif method == "POST":
            b = int(f.get("issue_id", "0")) - 900000
            issue(b)
            refused("add", n, b)
            if b not in deps(n):
                deps(n).append(b)
            write({"op": "add", "issue": n, "blocked_by": b})
            save()
            out(obj(n))
        elif method == "DELETE" and m.group(2):
            b = int(m.group(2)) - 900000
            refused("remove", n, b)
            if b not in deps(n):
                fail("HTTP 404: Not Found")
            deps(n).remove(b)
            write({"op": "remove", "issue": n, "blocked_by": b})
            save()
            out(obj(n))
        else:
            fail(f"fake gh: no such call {a}")
        sys.exit(0)
    m = re.fullmatch(r"repos/o/r/issues/(\d+)/dependencies/blocking", route)
    if m and method == "GET":
        n = int(m.group(1))
        issue(n)
        out([obj(int(k)) for k, v in sorted(S.get("deps", {}).items()) if n in v])
        sys.exit(0)
    m = re.fullmatch(r"repos/o/r/issues/(\d+)", route)
    if m:
        n = int(m.group(1))
        if method == "PATCH":
            if "body" not in f:
                fail(f"fake gh: no such call {a}")
            issue(n)["body"] = f["body"]
            write({"op": "body", "issue": n})
            save()
        out(obj(n))
        sys.exit(0)
    m = re.fullmatch(r"repos/o/r/issues/(\d+)/(events|comments|sub_issues)", route)
    if m and method == "GET":
        out(issue(int(m.group(1))).get("comments", []) if m.group(2) == "comments" else [])
        sys.exit(0)
    if route == "repos/o/r/issues" and method == "GET":
        out([obj(int(k)) for k in sorted(S["issues"], key=int)])
        sys.exit(0)
    if route == "repos/o/r/dispatches":
        write({"op": "dispatch", "fields": f})
        save()
        sys.exit(0)
    if route == "repos/o/r/contents/.github/CODEOWNERS":
        print("* @" + OWNER_LOGIN)
        sys.exit(0)
    if route.startswith("repos/o/r/contents/"):
        fail("HTTP 404: Not Found")
    if route.startswith("repos/o/r/pulls"):
        out([])
        sys.exit(0)
    if route.startswith("repos/o/r/actions/workflows/"):
        out({"workflow_runs": []})
        sys.exit(0)
    if route.startswith("repos/o/r/commits/"):
        out({"check_runs": []} if route.endswith("check-runs") else [])
        sys.exit(0)
fail(f"fake gh: no such call {a}")
'''


def record_comment(rec, i, login=BOT):
    """One comment holding a record, the way the bot posts it."""
    return {"author": {"login": login}, "body": f"{agent.MARK}\n**Record**\n\n```json\n{json.dumps(rec)}\n```\n",
            "createdAt": f"2026-10-09T{i:02d}:00:00Z"}


def plan(links, **extra):
    """A user story plan of #252 that passed its check, with these links."""
    h = {"kind": "user_story", "summary": "Links are recorded on both issues.", "user_story": "Links show on both.",
         "acceptance_criteria": [{"text": "Links are recorded.", "source": SRC}], "non_functional": [],
         "scope": ["dokima/agent.py"], "out_of_scope": ["Hand-made links."], "tests": {}, "test_changes": {},
         "links": links, **extra}
    return {"role": "planner", "stage": None, "handback": h, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/1", "run_id": "1"}


def review(verdict="approve", **extra):
    """A plan review of #252 that passed its check, with this verdict."""
    h = {"verdict": verdict, "summary": "Graded.", "blockers": [] if verdict == "approve" else
         [{"id": "B1", "criterion": f"{N}.1", "problem": "Weak.", "evidence": "x", "fix": "y", "fixer": "planner"}],
         "resolved": [], **extra}
    return {"role": "reviewer", "stage": "plan", "handback": h, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/2", "run_id": "2"}


class Hub:
    """A fake GitHub in a temp folder, and the commands of Dokima run against it."""

    def __init__(self, tmp, others=(301, 302, 303, 304, 305), deps=None, autopilot=False, fail=()):
        self.dir = str(tmp)
        bin_dir = os.path.join(self.dir, "bin")
        os.makedirs(bin_dir)
        gh = os.path.join(bin_dir, "gh")
        open(gh, "w").write(f"#!{sys.executable}\nBOT_LOGIN = {BOT!r}\nOWNER_LOGIN = {OWNER!r}\n" + FAKE_GH)
        os.chmod(gh, 0o755)
        self.asks = {N: ASK}
        issues = {str(N): {"title": "Record the links", "labels": ["autopilot"] if autopilot else [], "comments": [],
                           "body": f"<!-- dokima-card -->\n<!-- /dokima-card -->\n\n{body.MARKER}\n\n{ASK}"}}
        for n in others:
            self.asks[n] = f"Issue {n}: the owner's own words."
            issues[str(n)] = {"title": f"Issue {n}", "labels": [], "comments": [], "body": self.asks[n]}
        self.state = {"issues": issues, "deps": {str(k): list(v) for k, v in (deps or {}).items()},
                      "fail": list(fail), "writes": []}
        self.save()
        self.env = {**os.environ, "PATH": bin_dir + os.pathsep + os.environ.get("PATH", ""), "FAKE_GH_DIR": self.dir,
                    "GITHUB_REPOSITORY": "o/r", "REPO": "o/r", "OWNERS": OWNER, "GH_TOKEN": "fake",
                    "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "3"}
        self.env.pop("DOKIMA_BOARD", None)
        self.env.pop("ISSUE_NUMBER", None)

    def save(self):
        """Write the fake GitHub's state to its file."""
        json.dump(self.state, open(os.path.join(self.dir, "state.json"), "w"), indent=1)

    def load(self):
        """Read the fake GitHub's state back, as the commands left it."""
        self.state = json.load(open(os.path.join(self.dir, "state.json")))
        return self.state

    def post(self, rec, login=BOT):
        """Put a record on #252's conversation, as the workflow posts it after the river decided."""
        s = self.load()
        comments = s["issues"][str(N)]["comments"]
        comments.append(record_comment(rec, len(comments) + 1, login))
        self.save()

    def owner_said(self, text):
        """Put a code owner's comment on #252's conversation."""
        s = self.load()
        comments = s["issues"][str(N)]["comments"]
        comments.append({"author": {"login": OWNER}, "body": text, "createdAt": f"2026-10-09T{len(comments) + 1:02d}:00:00Z"})
        self.save()

    def next(self, rec):
        """Run `python3 -m dokima.agent next 252 OUT` on this run's record; returns (stdout, OUT/comment.md, OUT)."""
        out = os.path.join(self.dir, f"out{len(os.listdir(self.dir))}")
        os.makedirs(out)
        json.dump(rec, open(os.path.join(out, "record.json"), "w"))
        p = subprocess.run([sys.executable, "-m", "dokima.agent", "next", str(N), out], cwd=ROOT, env=self.env,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, f"test setup: `agent next` crashed: {p.stderr[-2000:]}"
        path = os.path.join(out, "comment.md")
        return p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "", \
            open(path).read() if os.path.exists(path) else "", out

    def approve(self, links, verdict="approve"):
        """The planner hands back a plan with these links, then `next` runs on the review."""
        self.post(plan(links))
        rec = review(verdict)
        said = self.next(rec)
        self.post(rec)
        # card.yml redraws on the record's comment; the plan approval itself saves no card (#438).
        self.redraw(N)
        return said

    def redraw(self, n):
        """Run card.yml's own redraw, `python3 dokima/card.py`, for issue n."""
        env = {**self.env, "ISSUE_NUMBER": str(n)}
        p = subprocess.run([sys.executable, "dokima/card.py"], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=120)
        assert p.returncode == 0, f"test setup: card.py crashed on #{n}: {p.stderr[-2000:]}"

    def writes(self, op=None):
        """Every write the commands made on GitHub, of one kind when given."""
        return [w for w in self.load()["writes"] if op is None or w["op"] == op]

    def blocked_by(self, n):
        """The issues GitHub has #n blocked by, sorted."""
        return sorted(self.load()["deps"].get(str(n), []))

    def body(self, n):
        """Issue #n's body as it stands on GitHub."""
        return self.load()["issues"][str(n)]["body"]

    def comments(self, n):
        """Issue #n's comments as they stand on GitHub."""
        return self.load()["issues"][str(n)]["comments"]

    def card_links(self, n):
        """The link lines on #n's card, above the owner's part: {kind: set of issue numbers}."""
        top = self.body(n).split(body.MARKER, 1)[0]
        found = {}
        for kind, label in LABELS.items():
            nums = set()
            lines = top.splitlines()
            for i, line in enumerate(lines):
                if f"**{label}:**" in line:
                    # Since #416 each issue is a bullet of its own under the label.
                    under = [line.split(f"**{label}:**", 1)[1]]
                    for nxt in lines[i + 1:]:
                        if nxt.startswith("- "):
                            under.append(nxt)
                        elif nxt.strip():
                            break
                    nums |= {int(x) for x in re.findall(r"(?:#|/issues/)(\d+)", " ".join(under))}
            found[kind] = nums
        return found


def links(blocked_by=(), blocks=(), relates_to=()):
    """A plan's links field with these issue numbers."""
    return {"blocked_by": list(blocked_by), "blocks": list(blocks), "relates_to": list(relates_to)}


# 252.1 ---------------------------------------------------------------------------------------------------------------

def test_an_approved_plan_records_its_blocking_links_on_github(tmp_path, record_property):
    """An approved plan's blocking links become GitHub's own blocked-by links on both issues.

    The plan says #252 is blocked by #301, blocks #302 and relates to #303. After the plan review approves it, GitHub
    has #252 blocked by #301 and #302 blocked by #252, and no blocked-by link touches #303 (relates to has none). Proves 252.1."""
    record_property("proves", "252.1")
    hub = Hub(tmp_path)
    hub.approve(links([301], [302], [303]))
    assert hub.blocked_by(N) == [301], f"252.1: #252 should be blocked by #301 on GitHub, has {hub.blocked_by(N)}"
    assert hub.blocked_by(302) == [N], f"252.1: #302 should be blocked by #252 on GitHub, has {hub.blocked_by(302)}"
    assert hub.blocked_by(303) == [] and N not in hub.blocked_by(303), \
        "252.1: a relates-to link was recorded as a blocked-by link"
    added = sorted((w["issue"], w["blocked_by"]) for w in hub.writes("add"))
    assert added == [(N, 301), (302, N)], f"252.1: expected exactly two blocked-by links added, got {added}"


def test_a_plan_the_review_blocks_records_nothing(tmp_path, record_property):
    """A plan the reviewer blocks records no link on GitHub.

    The first plan, approved, says #252 is blocked by #301: that link is recorded. The re-plan says blocked by #302
    and blocks #303, and the plan review blocks it: no blocked-by link is added or removed anywhere. Proves 252.1."""
    record_property("proves", "252.1")
    hub = Hub(tmp_path)
    hub.approve(links([301]))
    assert hub.blocked_by(N) == [301], f"252.1: the approved plan's link was not recorded: {hub.blocked_by(N)}"
    writes = len(hub.writes("add")) + len(hub.writes("remove"))
    hub.approve(links([302], [303]), verdict="block")
    assert len(hub.writes("add")) + len(hub.writes("remove")) == writes, \
        f"252.1: a blocked plan recorded links: {hub.writes('add') + hub.writes('remove')}"
    assert hub.blocked_by(N) == [301] and hub.blocked_by(303) == [], "252.1: a blocked plan's links are on GitHub"


def test_a_link_github_already_has_is_not_added_twice(tmp_path, record_property):
    """A link GitHub already has is not added again; the others still are.

    GitHub already has #252 blocked by #301. The approved plan says blocked by #301 and blocks #302: only #302's
    link is added, and #252 is still blocked by #301 exactly once. Proves 252.1."""
    record_property("proves", "252.1")
    hub = Hub(tmp_path, deps={N: [301]})
    hub.approve(links([301], [302]))
    added = sorted((w["issue"], w["blocked_by"]) for w in hub.writes("add"))
    assert (N, 301) not in added, "252.1: a link GitHub already had was added again"
    assert added == [(302, N)], f"252.1: expected only #302 blocked by #252 to be added, got {added}"
    assert hub.blocked_by(N) == [301], f"252.1: #252's blocked-by links changed: {hub.blocked_by(N)}"


def test_a_blocking_link_the_new_approved_plan_dropped_is_removed(tmp_path, record_property):
    """A blocking link the new approved plan dropped is removed from GitHub.

    The first approved plan says blocked by #301 and #304, blocks #302. The re-plan, approved again, keeps only
    blocked by #304. GitHub then has #252 blocked by #304 only, #302 no longer blocked by #252, and a link a person
    made by hand (#252 blocked by #305) stays, because no approved plan ever had it. Proves 252.1."""
    record_property("proves", "252.1")
    hub = Hub(tmp_path, deps={N: [305]})
    hub.approve(links([301, 304], [302]))
    assert hub.blocked_by(N) == [301, 304, 305] and hub.blocked_by(302) == [N], \
        "252.1: the first approved plan's links were not recorded"
    hub.approve(links([304]))
    assert hub.blocked_by(N) == [304, 305], \
        f"252.1: #252 should keep #304 and the hand-made #305 and lose #301, has {hub.blocked_by(N)}"
    assert hub.blocked_by(302) == [], f"252.1: the dropped blocks link to #302 is still on GitHub: {hub.blocked_by(302)}"
    removed = sorted((w["issue"], w["blocked_by"]) for w in hub.writes("remove"))
    assert removed == [(N, 301), (302, N)], f"252.1: expected exactly the two dropped links removed, got {removed}"


def test_a_replan_the_review_blocks_removes_nothing(tmp_path, record_property):
    """A blocked re-plan that drops a link leaves it on GitHub.

    The first plan, approved, says blocked by #301. The re-plan drops it and the review blocks the re-plan: #252 is
    still blocked by #301. Proves 252.1."""
    record_property("proves", "252.1")
    hub = Hub(tmp_path)
    hub.approve(links([301]))
    hub.approve(links(), verdict="block")
    assert hub.blocked_by(N) == [301], f"252.1: a blocked re-plan removed a link: {hub.blocked_by(N)}"
    assert hub.writes("remove") == [], "252.1: a blocked re-plan removed links"


# 252.2 ---------------------------------------------------------------------------------------------------------------

def test_both_cards_show_every_new_link_from_their_own_side(tmp_path, record_property):
    """After approval, both cards show every new link, each from its own side.

    The approved plan says #252 is blocked by #301, blocks #302 and relates to #303. #252's card shows all three;
    #301's card shows Blocks #252, #302's shows Blocked by #252 and #303's shows Relates to #252. No comment is
    posted on any of them, and every owner's ask is kept as written. Proves 252.2."""
    record_property("proves", "252.2")
    hub = Hub(tmp_path)
    hub.approve(links([301], [302], [303]))
    assert hub.card_links(N) == {"blocked_by": {301}, "blocks": {302}, "relates_to": {303}}, \
        f"252.2: #252's card does not show its links: {hub.card_links(N)}"
    expected = {301: {"blocked_by": set(), "blocks": {N}, "relates_to": set()},
                302: {"blocked_by": {N}, "blocks": set(), "relates_to": set()},
                303: {"blocked_by": set(), "blocks": set(), "relates_to": {N}}}
    for n, want in expected.items():
        assert hub.card_links(n) == want, f"252.2: #{n}'s card should show {want} from its side, shows {hub.card_links(n)}"
        assert hub.comments(n) == [], f"252.2: a comment was posted on #{n} for a link"
        assert body.ask(hub.body(n)) == hub.asks[n], f"252.2: the owner's ask on #{n} changed"
    assert hub.card_links(304) == {k: set() for k in LABELS}, "252.2: an issue with no link shows one"
    assert body.ask(hub.body(N)) == ASK, "252.2: the owner's ask on #252 changed"


def test_the_other_card_keeps_the_link_after_its_own_redraw(tmp_path, record_property):
    """The other card keeps the link after card.yml redraws it.

    After the approval, `python3 dokima/card.py` redraws #302 and #303 the way card.yml does on an edit: #302 still
    shows Blocked by #252 and #303 still shows Relates to #252, and no link is added or removed by those redraws. Proves 252.2."""
    record_property("proves", "252.2")
    hub = Hub(tmp_path)
    hub.approve(links([301], [302], [303]))
    before = len(hub.writes("add")) + len(hub.writes("remove"))
    for n in (302, 303, N):
        hub.redraw(n)
    assert hub.card_links(302)["blocked_by"] == {N}, f"252.2: #302 lost Blocked by #252 on redraw: {hub.card_links(302)}"
    assert hub.card_links(303)["relates_to"] == {N}, f"252.2: #303 lost Relates to #252 on redraw: {hub.card_links(303)}"
    assert hub.card_links(N) == {"blocked_by": {301}, "blocks": {302}, "relates_to": {303}}, \
        f"252.2: #252's card changed on redraw: {hub.card_links(N)}"
    assert len(hub.writes("add")) + len(hub.writes("remove")) == before, "252.2: a card redraw recorded links"
    for n in (302, 303):
        assert body.ask(hub.body(n)) == hub.asks[n], f"252.2: the owner's ask on #{n} changed on redraw"


def test_a_dropped_link_leaves_both_cards(tmp_path, record_property):
    """When an approved re-plan drops links, neither card shows them any more.

    The first approved plan links #301, #302 and #303; the re-plan, approved, has no links. Afterwards no card of
    #301, #302 or #303 names #252, #252's card shows no link line, and no comment was posted on them. Proves 252.2."""
    record_property("proves", "252.2")
    hub = Hub(tmp_path)
    hub.approve(links([301], [302], [303]))
    assert hub.card_links(303)["relates_to"] == {N}, f"252.2: #303's card never showed the link: {hub.card_links(303)}"
    hub.approve(links())
    for n in (301, 302, 303):
        assert hub.card_links(n) == {k: set() for k in LABELS}, f"252.2: #{n}'s card still shows a dropped link: {hub.card_links(n)}"
        assert hub.comments(n) == [], f"252.2: a comment was posted on #{n} for a link"
    hub.redraw(303)
    assert hub.card_links(303)["relates_to"] == set(), "252.2: the dropped relates-to link came back on #303's redraw"
    assert hub.card_links(N) == {k: set() for k in LABELS}, f"252.2: #252's card still shows links: {hub.card_links(N)}"


def test_a_relates_to_link_switched_to_blocks_moves_on_the_other_card(tmp_path, record_property):
    """A relates-to link turned into blocks moves to Blocked by on the other card.

    The first approved plan relates #252 to #303; the re-plan, approved, says #252 blocks #303. #303's card then
    shows Blocked by #252 and no longer Relates to #252. Proves 252.2."""
    record_property("proves", "252.2")
    hub = Hub(tmp_path)
    hub.approve(links(relates_to=[303]))
    hub.approve(links(blocks=[303]))
    assert hub.card_links(303) == {"blocked_by": {N}, "blocks": set(), "relates_to": set()}, \
        f"252.2: #303's card should show only Blocked by #252, shows {hub.card_links(303)}"


def test_a_plan_the_review_blocks_redraws_no_other_card(tmp_path, record_property):
    """A plan the review blocks changes no other issue's card.

    The first plan, approved, relates #252 to #301, and #301's card shows it. The re-plan links #302 and #303 and
    the review blocks it: #301's card still shows Relates to #252, and neither #302's nor #303's card names #252. Proves 252.2."""
    record_property("proves", "252.2")
    hub = Hub(tmp_path)
    hub.approve(links(relates_to=[301]))
    assert hub.card_links(301)["relates_to"] == {N}, f"252.2: #301's card does not show the link: {hub.card_links(301)}"
    hub.approve(links([302], [303]), verdict="block")
    assert hub.card_links(301)["relates_to"] == {N}, "252.2: a blocked re-plan took the approved link off #301's card"
    for n in (302, 303):
        assert hub.card_links(n) == {k: set() for k in LABELS}, f"252.2: #{n}'s card shows a link of a blocked plan"


# 252.3 ---------------------------------------------------------------------------------------------------------------

def test_two_issues_that_would_block_each_other_record_nothing_and_stop(tmp_path, record_property):
    """Two issues that would block each other: nothing recorded, the river stops.

    GitHub already has #252 blocked by #301; the approved plan says #252 blocks #301 and relates to #303, on
    autopilot. Nothing is recorded on GitHub, no other card shows #252, the worker does not start, and the record's
    comment mentions the owner and names #252 and #301. Proves 252.3."""
    record_property("proves", "252.3")
    hub = Hub(tmp_path, deps={N: [301]}, autopilot=True)
    hub.post(plan(links(blocks=[301], relates_to=[303])))
    step, comment, out = hub.next(review())
    assert hub.writes("add") == [] and hub.writes("remove") == [], "252.3: links were recorded despite the loop"
    assert hub.blocked_by(301) == [], "252.3: #301 was made blocked by #252"
    assert hub.card_links(303)["relates_to"] == set(), "252.3: the plan's relates-to link was recorded on #303's card"
    assert step == "stop", f"252.3: the river should stop for the owner, it said {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), "252.3: autopilot still started the worker"
    assert f"@{OWNER}" in comment, "252.3: the owner is not mentioned"
    for n in (N, 301):
        assert re.search(rf"#{n}\b", comment), f"252.3: the comment does not name #{n}: {comment!r}"
    assert open(os.path.join(out, "board.txt")).read().split()[1] == "needs", "252.3: the card is not marked Needs you"


def test_a_loop_through_other_issues_records_nothing_and_stops(tmp_path, record_property):
    """A loop through other issues records nothing and names every issue in it.

    GitHub has #302 blocked by #252 and #301 blocked by #302. The approved plan says #252 is blocked by #301, which
    closes the loop #252, #301, #302. Nothing is recorded, the river stops and the comment names all three. Proves 252.3."""
    record_property("proves", "252.3")
    hub = Hub(tmp_path, deps={302: [N], 301: [302]}, autopilot=True)
    hub.post(plan(links(blocked_by=[301])))
    step, comment, out = hub.next(review())
    assert hub.writes("add") == [] and hub.writes("remove") == [], "252.3: links were recorded despite the loop"
    assert step == "stop", f"252.3: the river should stop for the owner, it said {step!r}"
    assert f"@{OWNER}" in comment, "252.3: the owner is not mentioned"
    for n in (N, 301, 302):
        assert re.search(rf"#{n}\b", comment), f"252.3: the comment does not name #{n} of the loop: {comment!r}"


def test_links_with_no_loop_are_recorded_and_autopilot_goes_on(tmp_path, record_property):
    """Links that make no loop are recorded and autopilot starts the worker.

    GitHub has #302 blocked by #301. The plan says #252 is blocked by #301 and blocks #302 (#301, then #252, then
    #302: no loop), on autopilot: both links are recorded and the worker starts. #301 is already closed, so the
    worker has nothing open to wait on (#253). Proves 252.3."""
    record_property("proves", "252.3")
    hub = Hub(tmp_path, deps={302: [301]}, autopilot=True)
    hub.state["issues"]["301"]["state"] = "closed"
    hub.save()
    hub.post(plan(links([301], [302])))
    step, comment, out = hub.next(review())
    assert hub.blocked_by(N) == [301] and hub.blocked_by(302) == sorted([301, N]), \
        f"252.3: links with no loop were not recorded: #252 {hub.blocked_by(N)}, #302 {hub.blocked_by(302)}"
    assert step == "start worker", f"252.3: autopilot should start the worker, the river said {step!r}"


def test_turning_a_link_around_is_not_a_loop(tmp_path, record_property):
    """A re-plan that turns a blocking link around is not a loop.

    The first approved plan says #252 is blocked by #301. The re-plan, approved, says #252 blocks #301: the old link
    is removed, the new one recorded, and the river does not stop for a loop. Proves 252.3."""
    record_property("proves", "252.3")
    hub = Hub(tmp_path)
    hub.approve(links(blocked_by=[301]))
    step, comment, _ = hub.approve(links(blocks=[301]))
    assert hub.blocked_by(N) == [], f"252.3: the old link #252 blocked by #301 is still there: {hub.blocked_by(N)}"
    assert hub.blocked_by(301) == [N], f"252.3: the turned-around link was not recorded: {hub.blocked_by(301)}"


# 252.4 ---------------------------------------------------------------------------------------------------------------

def test_links_come_only_from_the_approved_checked_plan(tmp_path, record_property):
    """Only the approved plan's checked links are recorded, never a review's or a pasted one.

    The approved plan says blocked by #301. Around it sit a planner record a stranger pasted (blocked by #303), and
    the review approving it carries a links field of its own (blocked by #304); a later planner hand-back that code
    rejected says blocked by #305. Only #252 blocked by #301 is recorded. Proves 252.4."""
    record_property("proves", "252.4")
    hub = Hub(tmp_path)
    hub.post(plan(links([303])), login="stranger")
    hub.post(plan(links([301])))
    rejected = plan(links([305]))
    rejected["check"] = {"passed": False, "problems": ["bad"]}
    hub.post(rejected)
    hub.next(review(links=links([304])))
    added = sorted((w["issue"], w["blocked_by"]) for w in hub.writes("add"))
    assert added == [(N, 301)], f"252.4: links not from the approved checked plan were recorded: {added}"


# 252.5 ---------------------------------------------------------------------------------------------------------------

def test_a_link_github_refuses_stops_the_river_and_says_why(tmp_path, record_property):
    """A link GitHub refuses stops the river and the issue says which and why.

    GitHub refuses #302 blocked by #252 with "HTTP 422: Validation Failed (dependency limit reached)", on autopilot.
    The worker does not start, and the record's comment mentions the owner, names #252 and #302 and quotes the reason. Proves 252.5."""
    record_property("proves", "252.5")
    why = "HTTP 422: Validation Failed (dependency limit reached)"
    hub = Hub(tmp_path, autopilot=True, fail=[{"op": "add", "issue": 302, "blocked_by": N, "error": why}])
    hub.post(plan(links([301], [302])))
    step, comment, out = hub.next(review())
    assert step == "stop", f"252.5: the river should stop for the owner, it said {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), "252.5: autopilot still started the worker"
    assert f"@{OWNER}" in comment, "252.5: the owner is not mentioned"
    assert "dependency limit reached" in comment, f"252.5: GitHub's reason is not on the issue: {comment!r}"
    assert re.search(r"#302\b", comment) and re.search(rf"#{N}\b", comment), \
        f"252.5: the comment does not name the link that failed: {comment!r}"
    assert open(os.path.join(out, "board.txt")).read().split()[1] == "needs", "252.5: the card is not marked Needs you"


def test_a_link_github_fails_to_remove_stops_the_river_and_says_why(tmp_path, record_property):
    """A link GitHub fails to remove stops the river and says which and why.

    The first approved plan says blocked by #301; the re-plan drops it, on autopilot, and GitHub answers the removal
    with "HTTP 502: Server Error". The worker does not start and the comment names #252, #301 and the reason. Proves 252.5."""
    record_property("proves", "252.5")
    hub = Hub(tmp_path)
    hub.approve(links([301]))
    s = hub.load()
    s["issues"][str(N)]["labels"] = ["autopilot"]
    s["fail"] = [{"op": "remove", "issue": N, "blocked_by": 301, "error": "HTTP 502: Server Error"}]
    hub.save()
    step, comment, out = hub.approve(links())
    assert step == "stop", f"252.5: the river should stop for the owner, it said {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), "252.5: autopilot still started the worker"
    assert f"@{OWNER}" in comment, "252.5: the owner is not mentioned"
    assert "HTTP 502: Server Error" in comment, f"252.5: GitHub's reason is not on the issue: {comment!r}"
    assert re.search(r"#301\b", comment) and re.search(rf"#{N}\b", comment), \
        f"252.5: the comment does not name the link that failed: {comment!r}"


def test_recorded_links_let_autopilot_go_on(tmp_path, record_property):
    """When every link is recorded, autopilot starts the worker as usual.

    The approved plan says blocked by #301 and blocks #302, on autopilot, and GitHub records both: the river starts
    the worker and posts its Autopilot line. #301 is already closed, so the worker has nothing open to wait on
    (#253). Proves 252.5."""
    record_property("proves", "252.5")
    hub = Hub(tmp_path, autopilot=True)
    hub.state["issues"]["301"]["state"] = "closed"
    hub.save()
    hub.post(plan(links([301], [302])))
    step, comment, out = hub.next(review())
    assert hub.blocked_by(N) == [301] and hub.blocked_by(302) == [N], \
        f"252.5: the links were not recorded: #252 {hub.blocked_by(N)}, #302 {hub.blocked_by(302)}"
    assert step == "start worker", f"252.5: autopilot should start the worker, the river said {step!r}"
    assert os.path.exists(os.path.join(out, "autopilot.md")), "252.5: the Autopilot line is missing"

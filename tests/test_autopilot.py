"""`/autopilot start` and `/autopilot stop` switch a whole issue tree on and off, and start nothing else (#209).

These tests run the command listener (.github/workflows/commands.yml) the way GitHub runs it, on the machine from
test_start.py: every job's `if:` is evaluated and its scripts run with bash against a fake `gh`. Here the fake GitHub
also knows an issue tree and its labels, kept in tree.json and labels.json:

    #50                 (a parent above the issue; never part of its tree)
    ├── #57             (the issue the command is about; its pull request is #60, branch try/issue-57)
    │   ├── #101
    │   │   └── #103
    │   │       └── #104
    │   └── #102
    └── #58             (a sibling of #57; never part of its tree)

GitHub answers sub-issues on its REST API (`gh api repos/o/r/issues/N/sub_issues`, with or without --paginate) and a
single issue (`gh api repos/o/r/issues/N`) with its labels. Labels change through `gh issue edit N... --add-label` /
`--remove-label`, or the REST API (POST or PUT on repos/o/r/issues/N/labels, DELETE on .../labels/NAME, which fails
with 404 when the issue does not carry that label, the way GitHub does). `gh label create` succeeds. Autopilot's state
is the `autopilot` label, so the tests read what each issue carries afterwards.
"""
import json
import os
import re

import test_start as ts
from test_start import N, OWNER, PR, Ctx, evaluate, condition, fill
from rules_files import rules_text


LABEL = "autopilot"
TREE = {"50": [57, 58], "57": [101, 102], "101": [103], "103": [104]}
UNDER_57 = {57, 101, 102, 103, 104}
OUTSIDE = {50, 58}
HISTORY = [ts.owner_comment("Make it so.", "2026-10-08T09:00:00Z")]

TREE_GH = r'''
TREE = json.load(open(os.path.join(d, "tree.json"))) if os.path.exists(os.path.join(d, "tree.json")) else {}
LABELS_FILE = os.path.join(d, "labels.json")
LABELS = json.load(open(LABELS_FILE)) if os.path.exists(LABELS_FILE) else {}
def save_labels():
    json.dump(LABELS, open(LABELS_FILE, "w"), indent=1)
def issue_obj(n):
    n = int(n)
    return {"id": n * 10, "node_id": f"I_{n}", "number": n, "title": f"Issue {n}", "state": "open",
            "html_url": f"https://github.com/o/r/issues/{n}", "url": f"https://api.github.com/repos/o/r/issues/{n}",
            "labels": [{"name": l} for l in LABELS.get(str(n), [])]}
def method():
    return (flag("-X", "--method") or "GET").upper()
def fields(name):
    vals = []
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(a) and a[i + 1].startswith(name + "="):
            vals.append(a[i + 1].split("=", 1)[1])
    return vals
API_PATH = next((x for x in a[1:] if re.fullmatch(r"/?repos/o/r/issues/\d+(?:/sub_issues|/labels(?:/[^?]+)?)?(?:\?.*)?", x)), None) if a[:1] == ["api"] else None
m_sub = re.fullmatch(r"/?repos/o/r/issues/(\d+)/sub_issues(?:\?.*)?", API_PATH or "")
m_lab = re.fullmatch(r"/?repos/o/r/issues/(\d+)/labels(?:\?.*)?", API_PATH or "")
m_one = re.fullmatch(r"/?repos/o/r/issues/(\d+)/labels/([^?]+)", API_PATH or "")
m_iss = re.fullmatch(r"/?repos/o/r/issues/(\d+)(?:\?.*)?", API_PATH or "")
if a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/issues/\d+/dependencies/blocked_by", x) for x in a[1:]):
    print("[]")
    sys.exit(0)
if m_sub and method() == "GET":
    print(json.dumps([issue_obj(c) for c in TREE.get(m_sub.group(1), [])]))
    sys.exit(0)
if m_lab:
    n = m_lab.group(1)
    if method() in ("POST", "PUT"):
        new = fields("labels[]") + fields("labels")
        if "--input" in a:
            p = flag("--input")
            new += (json.load(sys.stdin if p == "-" else open(p)) or {}).get("labels") or []
        new = [l["name"] if isinstance(l, dict) else l for l in new]
        have = [] if method() == "PUT" else LABELS.get(n, [])
        LABELS[n] = have + [l for l in new if l not in have]
        save_labels()
    print(json.dumps([{"name": l} for l in LABELS.get(n, [])]))
    sys.exit(0)
if m_one and method() == "DELETE":
    n, name = m_one.group(1), m_one.group(2)
    if name not in LABELS.get(n, []):
        sys.stderr.write("HTTP 404: Label does not exist (https://api.github.com/repos/o/r/issues/%s/labels/%s)\n" % (n, name))
        sys.exit(1)
    LABELS[n] = [l for l in LABELS[n] if l != name]
    save_labels()
    print(json.dumps([{"name": l} for l in LABELS.get(n, [])]))
    sys.exit(0)
if m_iss and method() == "GET":
    out(issue_obj(m_iss.group(1)))
    sys.exit(0)
if a[:2] == ["issue", "edit"]:
    nums = []
    for x in a[2:]:
        if x.startswith("-"):
            break
        nums.append(x.rstrip("/").rsplit("/", 1)[-1].lstrip("#"))
    adds = [l.strip() for v in [a[i + 1] for i, x in enumerate(a) if x == "--add-label"] for l in v.split(",") if l.strip()]
    rems = [l.strip() for v in [a[i + 1] for i, x in enumerate(a) if x == "--remove-label"] for l in v.split(",") if l.strip()]
    for n in nums:
        have = [l for l in LABELS.get(n, []) if l not in rems]
        LABELS[n] = have + [l for l in adds if l not in have]
    save_labels()
    print(f"https://github.com/o/r/issues/{nums[0] if nums else ''}")
    sys.exit(0)
'''


class Tree(ts.Machine):
    """A machine whose fake GitHub knows the issue tree under #50 and every issue's labels."""

    def __init__(self, tmp, labels, actor=OWNER):
        super().__init__(tmp, HISTORY, try_branch=True, actor=actor, options={"pr_open": True})
        t = self.tmp
        fake = ts.FAKE_GH.replace('if a[:2] == ["issue", "view"]:', TREE_GH + 'if a[:2] == ["issue", "view"]:', 1)
        assert fake != ts.FAKE_GH, "test setup: could not teach the fake GitHub about sub-issues and labels"
        open(f"{t}/bin/gh", "w").write(fake.replace("#!/usr/bin/env python3", f"#!{ts.sys.executable}"))
        json.dump(TREE, open(f"{t}/gh/tree.json", "w"))
        json.dump({str(k): list(v) for k, v in labels.items()}, open(f"{t}/gh/labels.json", "w"))

    def labels(self):
        """Every issue's labels as GitHub holds them now: {number: [names]}."""
        return {int(k): v for k, v in json.load(open(f"{self.tmp}/gh/labels.json")).items()}

    def on_autopilot(self):
        """The issues that carry the autopilot label now."""
        return {n for n, ls in self.labels().items() if LABEL in ls}

    def listen(self, body, on_pr=False, user_type="User"):
        """Run commands.yml on one comment; returns True when it called the agent workflow (a stage started)."""
        number = int(PR if on_pr else N)
        issue = {"number": number, **({"pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{number}"}} if on_pr else {})}
        event = {"comment": {"body": body, "user": {"login": self.actor, "type": user_type}}, "issue": issue}
        open(f"{self.tmp}/event.json", "w").write(json.dumps(event))
        github = Ctx(event_name="issue_comment", actor=self.actor, event=event, run_id="42", run_attempt="1",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        wf = ts.workflow("commands.yml")
        jobs = wf["jobs"]
        results, outputs, called = {}, {}, False
        while len(results) < len(jobs):
            progressed = False
            for name, job in jobs.items():
                needs = job.get("needs") or []
                needs = [needs] if isinstance(needs, str) else needs
                if name in results or any(n not in results for n in needs):
                    continue
                progressed = True
                res = [results[n] for n in needs]
                status = {"failed": "failure" in res, "success": all(r == "success" for r in res)}
                ctx = {"github": github, "inputs": Ctx(), "vars": Ctx(DOKIMA_APP_ID="1"),
                       "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                       "needs": Ctx({n: {"result": results[n], "outputs": outputs.get(n, {})} for n in needs})}
                if not evaluate(condition(job.get("if")), ctx, status):
                    results[name] = "skipped"
                    continue
                if "uses" in job:
                    called = True
                    results[name] = "success"
                    continue
                results[name], outputs[name] = self.run_job(name, job, ctx, "issue_comment",
                                                            [("/tmp/", f"{self.tmp}/jobs/{name}/tmp/")], wf.get("defaults"))
            assert progressed, "test setup: the listener's jobs wait on each other"
        self.results = results
        self.failed = "failure" in results.values()
        return called


def mentioned(body):
    """Every issue number a comment names as #N."""
    return {int(x) for x in re.findall(r"#(\d+)\b", body)}


def assert_started_nothing(m, called, crit, case):
    """No planner, worker or reviewer started: the agent workflow was not called, no signal sent, no agent run."""
    assert not called, f"{crit} ({case}): the command started the agent workflow"
    assert m.dispatches() == [], f"{crit} ({case}): the command sent a signal to start a stage: {m.dispatches()}"
    assert not m.agent_started(), f"{crit} ({case}): an agent ran"


def test_autopilot_start_puts_the_issue_and_every_sub_issue_at_every_level_on_autopilot(record_property, tmp_path):
    """`/autopilot start` on an issue, or on its pull request, puts that issue and everything under it on autopilot, and nothing else.

    Runs the listener on the code owner's `/autopilot start` on issue #57, then on its pull request #60. Each time
    #57 and every issue under it, three levels down (#101, #102, #103, #104), must carry the autopilot label, while
    the parent #50 and the sibling #58 must not. Labels an issue already had (#101's "bug") stay."""
    record_property("proves", "209.1")
    for case, on_pr in (("issue", False), ("pull request", True)):
        m = Tree(tmp_path / case.replace(" ", "-"), {101: ["bug"]})
        m.listen("/autopilot start", on_pr=on_pr)
        assert not m.failed, f"209.1 ({case}): the listener failed on /autopilot start:\n{m.tail()}"
        on = m.on_autopilot()
        assert UNDER_57 - on == set(), \
            f"209.1 ({case}): /autopilot start left these issues of #57's tree off autopilot: {sorted(UNDER_57 - on)}"
        assert on & OUTSIDE == set(), \
            f"209.1 ({case}): /autopilot start also put issues outside #57's tree on autopilot: {sorted(on & OUTSIDE)}"
        assert "bug" in m.labels().get(101, []), f"209.1 ({case}): switching autopilot on removed #101's other label"


def test_autopilot_stop_takes_the_same_tree_off_autopilot(record_property, tmp_path):
    """`/autopilot stop` on an issue, or on its pull request, takes that issue and everything under it off autopilot, and nothing else.

    Starts with #57's whole tree on autopilot except #102 (filed later, never switched on), the parent #50 on
    autopilot too, and #101 also labelled "bug". After the code owner's `/autopilot stop` on #57, then on pull request
    #60, no issue of #57's tree may carry the autopilot label, #50 must still carry it, and #101 must keep "bug"."""
    record_property("proves", "209.2")
    for case, on_pr in (("issue", False), ("pull request", True)):
        m = Tree(tmp_path / case.replace(" ", "-"),
                 {50: [LABEL], 57: [LABEL], 101: [LABEL, "bug"], 102: [], 103: [LABEL], 104: [LABEL]})
        m.listen("/autopilot stop", on_pr=on_pr)
        assert not m.failed, f"209.2 ({case}): the listener failed on /autopilot stop:\n{m.tail()}"
        on = m.on_autopilot()
        assert on & UNDER_57 == set(), \
            f"209.2 ({case}): /autopilot stop left these issues of #57's tree on autopilot: {sorted(on & UNDER_57)}"
        assert 50 in on, f"209.2 ({case}): /autopilot stop on #57 also took its parent #50 off autopilot"
        assert "bug" in m.labels().get(101, []), f"209.2 ({case}): switching autopilot off removed #101's other label"


def test_autopilot_starts_no_stage_and_says_which_issues_it_switched(record_property, tmp_path):
    """`/autopilot start` and `/autopilot stop` start no stage on the issue they were said about, and leave one comment there naming every issue switched.

    Runs the listener on the code owner's `/autopilot start` and `/autopilot stop`, each on issue #57 and on pull
    request #60. None may call the agent workflow or run an agent; `/autopilot stop` sends no start signal at all and
    `/autopilot start` none for #57 itself (it may start #57's waiting children, #213). Each must leave exactly one
    new comment where the command was written (#57, or #60 for the pull request), that names every issue it
    switched (#57, #101, #102, #103, #104 on start; #57, #101, #103, #104 on stop, #102 having never been on) and
    neither #50 nor #58."""
    record_property("proves", "209.3")
    cases = (("start-issue", "/autopilot start", False, {101: ["bug"]}, UNDER_57),
             ("start-pr", "/autopilot start", True, {101: ["bug"]}, UNDER_57),
             ("stop-issue", "/autopilot stop", False, {57: [LABEL], 101: [LABEL], 103: [LABEL], 104: [LABEL]}, UNDER_57 - {102}),
             ("stop-pr", "/autopilot stop", True, {57: [LABEL], 101: [LABEL], 103: [LABEL], 104: [LABEL]}, UNDER_57 - {102}))
    for case, body, on_pr, labels, switched in cases:
        m = Tree(tmp_path / case, labels)
        called = m.listen(body, on_pr=on_pr)
        assert not m.failed, f"209.3 ({case}): the listener failed on {body}:\n{m.tail()}"
        if body == "/autopilot stop":
            assert_started_nothing(m, called, "209.3", case)
        else:
            assert not called, f"209.3 ({case}): the command started the agent workflow"
            assert not m.agent_started(), f"209.3 ({case}): an agent ran"
            own = [d for d in m.dispatches() if any(x in (f"client_payload[issue]={N}", f"client_payload[issue]={PR}") for x in d)]
            assert own == [], f"209.3 ({case}): {body} started a stage on #{N} itself: {own}"
        where = PR if on_pr else N
        posts = [p for p in m.posted() if p["where"][2] == where]
        assert len(posts) == 1, \
            f"209.3 ({case}): {body} left {len(posts)} comments on #{where}, expected exactly one: {[p['body'][:200] for p in posts]}"
        assert posts[0]["where"] == ["pr" if on_pr else "issue", "comment", where], \
            f"209.3 ({case}): the comment went to {posts[0]['where']}, not where {body} was said (#{where})"
        named = mentioned(posts[0]["body"])
        assert switched - named == set(), \
            f"209.3 ({case}): the comment does not name these switched issues: {sorted(switched - named)}\n{posts[0]['body'][:800]}"
        assert named & OUTSIDE == set(), \
            f"209.3 ({case}): the comment names issues outside the tree: {sorted(named & OUTSIDE)}\n{posts[0]['body'][:800]}"


def test_agents_md_tells_how_autopilot_works(record_property):
    """AGENTS.md's Commands and The flow sections tell how `/autopilot start` and `/autopilot stop` work.

    Reads AGENTS.md: its Commands section must name both `/autopilot start` and `/autopilot stop`, and its The flow
    section must mention autopilot, since autopilot changes the flow."""
    record_property("proves", "209.4")
    text = rules_text()
    sections = {m.group(1).strip(): m.group(2) for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M)}
    commands = sections.get("Commands", "")
    for cmd in ("/autopilot start", "/autopilot stop"):
        assert cmd in commands, f"209.4: AGENTS.md's Commands section does not name `{cmd}`"
    flow = next((v for k, v in sections.items() if k.startswith("The flow")), "")
    assert "autopilot" in flow.lower(), "209.4: AGENTS.md's The flow section does not say how autopilot changes the flow"


def test_only_a_code_owners_autopilot_counts(record_property, tmp_path):
    """Only a code owner's `/autopilot` changes anything; a stranger's or a bot's changes no label and leaves no comment.

    Runs the listener on `/autopilot start` and `/autopilot stop` from someone who is not a code owner (on the issue
    and on its pull request) and from Dokima's own bot: no issue's labels may change, no comment may be left and no
    stage may start. Beside them, the code owner's own `/autopilot start` does switch the tree on."""
    record_property("proves", "209.5")
    before = {57: [LABEL], 101: [LABEL, "bug"], 103: [LABEL], 104: [LABEL]}
    cases = (("stranger-start", "stranger", "User", "/autopilot start", False, {101: ["bug"]}),
             ("stranger-stop-pr", "stranger", "User", "/autopilot stop", True, before),
             ("bot-start", "dokima-runtime[bot]", "Bot", "/autopilot start", False, {101: ["bug"]}),
             ("bot-stop", "dokima-runtime[bot]", "Bot", "/autopilot stop", False, before))
    for case, actor, kind, body, on_pr, labels in cases:
        m = Tree(tmp_path / case, labels, actor=actor)
        start = m.labels()
        called = m.listen(body, on_pr=on_pr, user_type=kind)
        assert m.labels() == start, f"209.5 ({case}): {body} by {actor} changed labels: {start} -> {m.labels()}"
        assert m.posted() == [], f"209.5 ({case}): {body} by {actor} left comments: {[p['body'][:200] for p in m.posted()]}"
        assert_started_nothing(m, called, "209.5", case)
    m = Tree(tmp_path / "owner", {101: ["bug"]})
    m.listen("/autopilot start")
    assert UNDER_57 <= m.on_autopilot(), \
        f"209.5 (owner): the code owner's /autopilot start did not switch #57's tree on: {sorted(m.on_autopilot())}\n{m.tail()}"

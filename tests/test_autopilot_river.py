"""On autopilot the river hands an approved plan to the worker and files an approved split itself (#211).

Wherever the owner would have typed `/work`, autopilot posts one short line instead, and the river still stops for the
owner wherever the owner must decide. A planner's questions no longer always stop on autopilot: the plan reviewer
judges each question's assumption against the owner's own words, and only a question it does not accept stops.

These tests run the real workflows the way GitHub runs them, on the machine from test_start.py (agent.yml for a run,
commands.yml for a comment), with a fake GitHub that also knows each issue's labels. Autopilot is the `autopilot`
label on the issue. GitHub gives an issue's labels three ways and the fake answers all three: `gh api
repos/o/r/issues/N` (with its labels), `gh api repos/o/r/issues/N/labels`, and `gh issue view N --json ...labels`.
With the option fail_labels, every one of those reads of issue #57 fails the way GitHub fails (HTTP 502), and nothing
else does. A signal that starts a stage is `gh api repos/o/r/dispatches` with event_type dokima-next and its
client_payload, given as -f/-F fields or as JSON through --input; the fake keeps both.
Where only the river's decision matters, the tests run `python3 -m dokima.agent next` on a record, against the same
fake GitHub.
"""
import json
import os
import re
import subprocess
import sys

import test_start as ts
from test_autopilot import TREE_GH
from test_start import N, OWNER, Ctx, evaluate, condition, fill
from dokima import agent

LINE_PLAN = "Autopilot: plan approved, starting work"
LINE_SPLIT = "Autopilot: split approved, filing its stories"
ON = {int(N): ["autopilot"]}
ISSUE = "https://github.com/o/r/issues/57"

QUESTIONS = [{"question": "Should a failed run move its card to Needs you?",
              "assumption": "It does, so the owner sees it without looking."},
             {"question": "Should the card name the step that failed?",
              "assumption": "It does, so the owner sees where it broke."}]
STORY_Q = {**ts.STORY, "questions": QUESTIONS}
APPROVE = {**ts.APPROVE, "previous_step": {"did": ["Planned one story."], "decided": [], "open": []},
           "summary": "Every ask has a criterion and every criterion a test that breaks on any deviation.",
           "asks": [{"ask": "Fix it.", "source": ISSUE, "criterion": "57.1"}]}
BLOCK = {**APPROVE, "verdict": "block", "summary": "The test for 57.1 proves nothing.",
         "blockers": [{"id": "B1", "criterion": "57.1", "problem": "The test passes against a stub.",
                       "evidence": "tests/test_x.py::test_a", "fix": "Run the real thing.", "test": None, "fixer": "planner"}]}
OWNER_SAID = {**ts.owner_comment("Every failure should name the step that failed, nothing vaguer.", "2026-10-07T09:50:00Z"),
              "url": ISSUE + "#issuecomment-77"}
STRANGER_SAID = {"author": {"login": "stranger"}, "body": "Cards should name the step that broke.",
                 "createdAt": "2026-10-07T09:55:00Z", "url": ISSUE + "#issuecomment-78"}
ACCEPT_1 = {"question": QUESTIONS[0]["question"], "accepted": True, "changes": False,
            "matched": "a failure always says why on the issue", "source": "AGENTS.md"}
ACCEPT_2 = {"question": QUESTIONS[1]["question"], "accepted": True, "changes": False,
            "matched": "Every failure should name the step that failed", "source": ISSUE + "#issuecomment-77"}
REFUSE_2 = {"question": QUESTIONS[1]["question"], "accepted": False, "changes": False,
            "why": "Nothing the owner said covers which step the card names."}
COSTLY_2 = {**ACCEPT_2, "changes": True}

STORY_WAITING = ts.STORY_PLANNED + [ts.record_comment(ts.review_record(APPROVE), "2026-10-07T10:20:00Z")]
STORY_Q_PLANNED = [OWNER_SAID, STRANGER_SAID, ts.owner_comment("/plan", "2026-10-07T10:00:00Z"),
                   {**ts.record_comment(ts.planner_record(STORY_Q), "2026-10-07T10:10:00Z"), "url": ISSUE + "#issuecomment-79"}]
SPLIT_FILED = {"role": "split", "stage": None, "run": "https://github.com/o/r/actions/runs/3",
               "handback": {"stories": [{"story": 1, "issue": 901, "title": "First", "id": 9010, "blocked_by": []},
                                        {"story": 2, "issue": 902, "title": "Second", "id": 9020, "blocked_by": [1]}]},
               "check": {"passed": True, "problems": []}}

LABEL_GH = r'''
INITIAL_LABELS = __LABELS__
LBL_FILE = os.path.join(d, "labels.json")
def current_labels():
    return json.load(open(LBL_FILE)) if os.path.exists(LBL_FILE) else INITIAL_LABELS
label_path = next((x for x in a[1:] if re.fullmatch(r"/?repos/o/r/issues/57(?:/labels)?(?:\?.*)?", x)), None) if a[:1] == ["api"] else None
reads_labels = (label_path is not None and (flag("-X", "--method") or "GET").upper() == "GET") or \
    (a[:3] == ["issue", "view", "57"] and "labels" in (flag("--json") or ""))
if opts.get("fail_labels") and reads_labels:
    sys.stderr.write("HTTP 502: Server Error (https://api.github.com/repos/o/r/issues/57)\n")
    sys.exit(1)
if a[:1] == ["api"] and any("dispatches" in x for x in a) and "--input" in a:
    p = flag("--input")
    open(os.path.join(d, "dispatch-inputs.jsonl"), "a").write(json.dumps(json.load(sys.stdin if p == "-" else open(p))) + "\n")
    print("{}")
    sys.exit(0)
if a[:2] == ["issue", "view"]:
    n = int(a[2].rstrip("/").rsplit("/", 1)[-1].lstrip("#")) if len(a) > 2 and not a[2].startswith("-") else 57
    issue = json.load(open(os.path.join(d, "issue.json")))
    if n == issue["number"]:
        issue["comments"] = issue["comments"] + comments_on("issue", n)
    else:
        issue = {"number": n, "title": f"Issue {n}", "body": "", "comments": comments_on("issue", n)}
    issue["labels"] = [{"name": l} for l in current_labels().get(str(n), [])]
    print(issue["title"] if flag("-q") == ".title" else json.dumps(issue))
    sys.exit(0)
'''


def fake_gh(labels):
    """The fake GitHub of test_start.py, taught the labels each issue starts with, sub-issues, and the label reads."""
    lit = json.dumps({str(k): list(v) for k, v in labels.items()})
    tree = TREE_GH.replace("LABELS = json.load(open(LABELS_FILE)) if os.path.exists(LABELS_FILE) else {}",
                           "LABELS = json.load(open(LABELS_FILE)) if os.path.exists(LABELS_FILE) else INITIAL_LABELS", 1)
    assert tree != TREE_GH, "test setup: could not give the fake GitHub its starting labels"
    fake = ts.FAKE_GH.replace('if a[:2] == ["issue", "view"]:', LABEL_GH.replace("__LABELS__", lit) + tree
                              + 'if a[:2] == ["issue", "view"]:', 1)
    assert fake != ts.FAKE_GH, "test setup: could not teach the fake GitHub about labels"
    return fake


def run(monkeypatch, tmp, role, stage, comments, labels, **kw):
    """One run of agent.yml on issue #57, whose issues carry these labels on GitHub."""
    monkeypatch.setattr(ts, "FAKE_GH", fake_gh(labels))
    return ts.Run(tmp, role, stage, comments, **kw)


class Listener(ts.Machine):
    """One run of commands.yml on a code owner's comment on issue #57, noting what each called workflow was given."""

    def __init__(self, monkeypatch, tmp, body, comments, labels):
        monkeypatch.setattr(ts, "FAKE_GH", fake_gh(labels))
        super().__init__(tmp, comments)
        event = {"comment": {"body": body, "user": {"login": OWNER, "type": "User"}}, "issue": {"number": int(N)}}
        open(f"{self.tmp}/event.json", "w").write(json.dumps(event))
        github = Ctx(event_name="issue_comment", actor=OWNER, event=event, run_id="42", run_attempt="1",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        wf = ts.workflow("commands.yml")
        results, outputs, self.called = {}, {}, []
        while len(results) < len(wf["jobs"]):
            progressed = False
            for name, job in wf["jobs"].items():
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
                    self.called.append({k: fill(str(v), ctx, status) for k, v in (job.get("with") or {}).items()})
                    results[name] = "success"
                    continue
                results[name], outputs[name] = self.run_job(name, job, ctx, "issue_comment",
                                                            [("/tmp/", f"{self.tmp}/jobs/{name}/tmp/")], wf.get("defaults"))
            assert progressed, "test setup: the listener's jobs wait on each other"
        self.failed = "failure" in results.values()


def starts(m):
    """Every stage the run started, as (role, issue): signals sent to agent.yml, and agent workflows a listener called."""
    out = []
    for c in m.dispatches():
        if "--input" in c:
            continue
        f = dict(x.split("=", 1) for i, x in enumerate(c) if i and c[i - 1] in ("-f", "-F", "--field", "--raw-field") and "=" in x)
        if f.get("event_type") == "dokima-next":
            out.append((f.get("client_payload[role]", ""), f.get("client_payload[issue]", "")))
    path = f"{m.tmp}/gh/dispatch-inputs.jsonl"
    for l in (open(path).read().splitlines() if os.path.exists(path) else []):
        p = json.loads(l)
        if p.get("event_type") == "dokima-next":
            out.append((str(p.get("client_payload", {}).get("role", "")), str(p.get("client_payload", {}).get("issue", ""))))
    out += [(w.get("role", ""), w.get("issue", "")) for w in getattr(m, "called", [])]
    return out


def lines(m, text):
    """The comments on issue #57 that read exactly this line."""
    return [p for p in m.posted() if p["where"] == ["issue", "comment", N] and p["body"].strip() == text]


def autopilot_lines(m):
    """Every comment the run left that is an Autopilot line."""
    return [p["body"] for p in m.posted() if p["body"].strip().startswith("Autopilot:")]


def run_records(m):
    """The records the run posted, read back the way the river reads them."""
    return agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in m.posted()])


def record_body(m, crit):
    """The one comment carrying the run's own record."""
    bodies = [p["body"] for p in m.posted() if agent.records([{"author": {"login": agent.BOT}, "body": p["body"]}])]
    assert len(bodies) == 1, f"{crit}: the run posted {len(bodies)} records, expected its one:\n{m.tail()}"
    return bodies[0]


def next_of(body):
    """The card's Next line."""
    return next((l for l in body.splitlines() if l.startswith("**Next:**")), "")


def decide(tmp, rec, comments, labels):
    """Run `python3 -m dokima.agent next 57` on a run's record against the fake GitHub; returns what it printed, the
    card with its Next line and where it put the card on the board."""
    t = str(tmp)
    os.makedirs(f"{t}/bin")
    os.makedirs(f"{t}/gh")
    os.makedirs(f"{t}/out")
    open(f"{t}/bin/gh", "w").write(fake_gh(labels).replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    os.chmod(f"{t}/bin/gh", 0o755)
    json.dump({}, open(f"{t}/gh/options.json", "w"))
    json.dump({"number": int(N), "title": "Stuck issue", "body": "Fix it.", "comments": comments}, open(f"{t}/gh/issue.json", "w"))
    json.dump(rec, open(f"{t}/out/record.json", "w"))
    open(f"{t}/out/comment.md", "w").write(agent.render(rec))
    env = {**os.environ, "PATH": f"{t}/bin:" + os.environ["PATH"], "FAKE_GH_DIR": f"{t}/gh", "GITHUB_REPOSITORY": "o/r",
           "GITHUB_SERVER_URL": "https://github.com", "OWNERS": OWNER, "GH_TOKEN": "fake-github-token",
           "PYTHONPATH": ts.ROOT}
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "next", N, f"{t}/out"], cwd=ts.ROOT, env=env,
                       capture_output=True, text=True, timeout=60)
    board = open(f"{t}/out/board.txt").read().strip() if os.path.exists(f"{t}/out/board.txt") else ""
    return p.stdout.strip(), open(f"{t}/out/comment.md").read(), board, p.stderr


def assert_stops(r, why, crit, case):
    """The run stopped for the owner: it says why, mentions the owner, sets Needs you, starts nothing, posts no Autopilot line."""
    body = record_body(r, f"{crit} ({case})")
    assert why.lower() in body.lower(), f"{crit} ({case}): the card does not say why it stopped ({why!r}):\n{body[:900]}"
    assert next_of(body).startswith(f"**Next:** @{OWNER}"), \
        f"{crit} ({case}): the card's Next line does not mention the owner: {next_of(body)!r}"
    assert r.board().endswith("needs"), f"{crit} ({case}): the card does not show Needs you: {r.board()!r}"
    assert starts(r) == [], f"{crit} ({case}): a stage started on its own on autopilot: {starts(r)}"
    assert autopilot_lines(r) == [], f"{crit} ({case}): an Autopilot line was posted where the river stops: {autopilot_lines(r)}"


def test_on_autopilot_an_approved_plan_starts_the_worker_with_one_autopilot_line(record_property, tmp_path, monkeypatch):
    """On autopilot, an approved plan starts the worker with one "Autopilot: plan approved, starting work" line.

    Runs the plan review of issue #57, on autopilot, the reviewer approving. Exactly one worker must start for #57,
    the issue must get exactly one comment reading the line, the review's card must end "Next: The worker starts now."
    and the card must go to Work without Needs you. Then a code review's approval on autopilot must still stop for the
    owner, since only the owner merges."""
    record_property("proves", "211.1")
    r = run(monkeypatch, tmp_path / "river", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=APPROVE)
    assert r.agent_started() and not r.failed, f"211.1: setup: the plan review did not run:\n{r.tail()}"
    assert starts(r) == [("worker", N)], f"211.1: the approved plan on autopilot did not start exactly one worker for #57: {starts(r)}"
    assert len(lines(r, LINE_PLAN)) == 1, \
        f"211.1: the issue did not get exactly one {LINE_PLAN!r} comment: {[p['body'][:120] for p in r.posted()]}"
    body = record_body(r, "211.1")
    assert next_of(body) == "**Next:** The worker starts now.", f"211.1: the card's Next line is {next_of(body)!r}"
    assert r.board() == "Work none", f"211.1: the card should be in Work without Needs you, not {r.board()!r}"

    pr = {**ts.review_record(APPROVE), "stage": "pr"}
    out, card, board, err = decide(tmp_path / "code-review", pr, STORY_WAITING, ON)
    assert out == "stop" and next_of(card).startswith(f"**Next:** @{OWNER}") and board.endswith("needs"), \
        f"211.1: a code review's approval on autopilot did not stop for the owner: {out!r} {next_of(card)!r} {board!r}\n{err[-800:]}"


def test_autopilot_start_starts_the_worker_on_a_plan_already_waiting_for_work(record_property, tmp_path, monkeypatch):
    """`/autopilot start` on an issue whose plan is approved and waiting for `/work` starts the worker, once.

    Runs the listener on the code owner's `/autopilot start` on #57, whose newest plan is approved and nobody has said
    `/work`. One worker must start for #57, the issue must get exactly one "Autopilot: plan approved, starting work"
    comment, and no comment may say that no stage was started. Two neighbours start nothing and post no line: the same
    plan already handed to the worker by autopilot (its line is on the issue), and one the owner already said `/work` on."""
    record_property("proves", "211.1")
    m = Listener(monkeypatch, tmp_path / "waiting", "/autopilot start", STORY_WAITING, {})
    assert not m.failed, f"211.1: the listener failed on /autopilot start:\n{m.tail()}"
    assert starts(m) == [("worker", N)], f"211.1: /autopilot start did not start exactly one worker for #57: {starts(m)}"
    assert len(lines(m, LINE_PLAN)) == 1, \
        f"211.1: /autopilot start did not post exactly one {LINE_PLAN!r} on #57: {[p['body'][:120] for p in m.posted()]}"
    said = [p["body"] for p in m.posted() if "no stage was started" in p["body"].lower()]
    assert said == [], f"211.1: a comment says no stage was started, though the worker started: {said}"

    handed = STORY_WAITING + [{"author": {"login": agent.BOT}, "body": LINE_PLAN, "createdAt": "2026-10-07T10:25:00Z"}]
    worked = STORY_WAITING + [ts.owner_comment("/work", "2026-10-07T10:30:00Z")]
    for case, comments in (("already handed over", handed), ("owner said /work", worked)):
        m = Listener(monkeypatch, tmp_path / case.replace(" ", "-").replace("/", ""), "/autopilot start", comments, {})
        assert not m.failed, f"211.1 ({case}): the listener failed on /autopilot start:\n{m.tail()}"
        assert starts(m) == [], f"211.1 ({case}): /autopilot start started a second worker: {starts(m)}"
        assert autopilot_lines(m) == [], f"211.1 ({case}): /autopilot start posted another Autopilot line: {autopilot_lines(m)}"


def assert_stories_as_work_files_them(m, case):
    """The split's stories were filed as `/work` files them on autopilot: each on autopilot, and only the unblocked one planning."""
    for c in m.created_issues():
        given = [c[j + 1] for j, x in enumerate(c[:-1]) if x in ("--label", "-l")]
        assert "autopilot" in [l.strip() for v in given for l in v.split(",")], \
            f"211.2 ({case}): a story was filed off autopilot, unlike `/work` on autopilot: {c[:6]} labels {given}"
    planners = sorted(s for s in starts(m) if s[0] == "planner")
    assert planners == [("planner", "900")], (f"211.2 ({case}): the stories did not start as `/work` on autopilot starts "
                                              f"them (only #900, which waits on nothing, plans): {planners}")


def test_on_autopilot_an_approved_split_files_its_stories_with_one_autopilot_line(record_property, tmp_path, monkeypatch):
    """On autopilot, an approved split files its stories as `/work` would, with one "Autopilot: split approved, filing its stories" line.

    Runs the plan review of a split on #57, on autopilot, the reviewer approving: both stories must be filed as issues,
    the issue must get one "Split filed" record and exactly one comment reading the line, and no worker may start.
    As `/work` on autopilot does on main (#213), both stories must be filed on autopilot and only the first, which
    waits on nothing (the second is blocked by it), may start its planner; GitHub numbers them #900 and #901.
    Then `/autopilot start` on #57 whose split is approved and not yet filed does the same, and on a split already
    filed it files nothing and posts no line."""
    record_property("proves", "211.2")
    r = run(monkeypatch, tmp_path / "river", "reviewer", "plan", ts.SPLIT_PROPOSED, ON)
    assert r.agent_started(), f"211.2: setup: the plan review of the split did not run:\n{r.tail()}"
    assert len(r.created_issues()) == 2, f"211.2: the approved split on autopilot filed {len(r.created_issues())} issues, not its 2 stories"
    assert len(lines(r, LINE_SPLIT)) == 1, \
        f"211.2: the issue did not get exactly one {LINE_SPLIT!r} comment: {[p['body'][:120] for p in r.posted()]}"
    assert [x["role"] for x in run_records(r)].count("split") == 1, \
        f"211.2: filing the split did not post its one Split filed record: {[x['role'] for x in run_records(r)]}"
    assert [s for s in starts(r) if s[0] == "worker"] == [], f"211.2: a worker started on a split: {starts(r)}"
    assert_stories_as_work_files_them(r, "the river")

    m = Listener(monkeypatch, tmp_path / "waiting", "/autopilot start", ts.SPLIT_APPROVED, {})
    assert not m.failed, f"211.2: the listener failed on /autopilot start:\n{m.tail()}"
    assert len(m.created_issues()) == 2, f"211.2: /autopilot start on an approved split filed {len(m.created_issues())} issues, not 2"
    assert len(lines(m, LINE_SPLIT)) == 1, \
        f"211.2: /autopilot start did not post exactly one {LINE_SPLIT!r}: {[p['body'][:120] for p in m.posted()]}"
    assert [s for s in starts(m) if s[0] == "worker"] == [], f"211.2: /autopilot start started a worker on a split: {starts(m)}"
    assert_stories_as_work_files_them(m, "/autopilot start")

    filed = ts.SPLIT_APPROVED + [ts.record_comment(SPLIT_FILED, "2026-10-07T10:30:00Z")]
    m = Listener(monkeypatch, tmp_path / "filed", "/autopilot start", filed, {})
    assert m.created_issues() == [] and autopilot_lines(m) == [], \
        f"211.2: /autopilot start on a split already filed filed again or posted a line: {m.created_issues()} {autopilot_lines(m)}"


def test_off_autopilot_an_approved_plan_or_split_still_stops_for_the_owner(record_property, tmp_path, monkeypatch):
    """Off autopilot, an approved plan or split still stops for the owner exactly as today, with no Autopilot line.

    Runs the approving plan review of a story and of a split on #57, which is not on autopilot though its parent #50
    is. Each must start nothing, file nothing, post no Autopilot line, and end with a Next line mentioning the owner
    with Needs you; the story's says `/work`. Beside them, the same story with #57 on autopilot does start the worker,
    so the stop comes from autopilot being off and from nothing else."""
    record_property("proves", "211.3")
    off = {50: ["autopilot"], int(N): ["bug"]}
    r = run(monkeypatch, tmp_path / "on", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=APPROVE)
    assert starts(r) == [("worker", N)], f"211.3: with #57 on autopilot the approved plan did not start the worker: {starts(r)}"

    r = run(monkeypatch, tmp_path / "story", "reviewer", "plan", ts.STORY_PLANNED, off, try_branch=True, review=APPROVE)
    assert r.agent_started(), f"211.3: setup: the plan review did not run:\n{r.tail()}"
    assert_stops(r, "/work", "211.3", "story")
    r = run(monkeypatch, tmp_path / "split", "reviewer", "plan", ts.SPLIT_PROPOSED, off)
    assert r.agent_started(), f"211.3: setup: the plan review of the split did not run:\n{r.tail()}"
    assert r.created_issues() == [], "211.3: off autopilot, the approved split filed its stories without /work"
    assert_stops(r, "", "211.3", "split")


def test_on_autopilot_the_river_still_stops_where_the_owner_must_decide(record_property, tmp_path, monkeypatch):
    """On autopilot the river still stops on an escalation, three blocks in a row, a rejected hand-back and a run that failed or never started.

    Runs, on #57 on autopilot: a plan review that escalates, a third blocking plan review in a row, a plan review whose
    hand-back code rejects, a worker that never starts (no try branch) and a worker whose install step fails. Each
    must say why on its card, mention the owner, set Needs you, start nothing and post no Autopilot line. Beside them,
    an approving plan review on autopilot starts the worker, and a first blocking review still goes back to the planner."""
    record_property("proves", "211.4")
    r = run(monkeypatch, tmp_path / "approve", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=APPROVE)
    assert starts(r) == [("worker", N)], f"211.4: an approving plan review on autopilot did not start the worker: {starts(r)}"
    r = run(monkeypatch, tmp_path / "first-block", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=BLOCK)
    assert starts(r) == [("planner", N)], f"211.4: a first blocking review on autopilot did not go back to the planner: {starts(r)}"

    escalate = {**APPROVE, "verdict": "escalate", "summary": "The plan and the owner's words disagree."}
    r = run(monkeypatch, tmp_path / "escalate", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=escalate)
    assert_stops(r, "escalated", "211.4", "escalation")

    rec = lambda h, t: ts.record_comment(ts.review_record(h) if "verdict" in h else ts.planner_record(h), t)
    twice = ts.STORY_PLANNED + [rec(BLOCK, "2026-10-07T10:20:00Z"), rec(ts.STORY, "2026-10-07T10:30:00Z"),
                                rec(BLOCK, "2026-10-07T10:40:00Z"), rec(ts.STORY, "2026-10-07T10:50:00Z")]
    r = run(monkeypatch, tmp_path / "three-blocks", "reviewer", "plan", twice, ON, try_branch=True, review=BLOCK)
    assert_stops(r, "3 blocking reviews", "211.4", "three blocks")

    r = run(monkeypatch, tmp_path / "rejected", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True,
            review={**APPROVE, "verdict": "maybe"})
    assert_stops(r, "rejected by code", "211.4", "rejected hand-back")

    r = run(monkeypatch, tmp_path / "never", "worker", "", STORY_WAITING, ON)
    assert_stops(r, f"try/issue-{N}", "211.4", "never started")
    r = run(monkeypatch, tmp_path / "failed", "worker", "", STORY_WAITING, ON, try_branch=True, broken={"pip": ts.PIP_BROKEN})
    assert_stops(r, "Install pytest and Claude Code", "211.4", "failed run")


def test_on_autopilot_a_plan_with_questions_goes_to_the_plan_reviewer(record_property, tmp_path):
    """On autopilot a plan with questions goes to the plan reviewer instead of stopping; off autopilot it stops as today.

    Decides what follows a passed plan that has two questions for the owner. On autopilot the plan reviewer must start
    now, the card saying "Next: The reviewer starts now." with no Needs you. Off autopilot the river must stop,
    mention the owner and set Needs you."""
    record_property("proves", "211.5")
    rec = ts.planner_record(STORY_Q)
    out, card, board, err = decide(tmp_path / "on", rec, STORY_Q_PLANNED, ON)
    assert out == "start reviewer plan", f"211.5: on autopilot a plan with questions did not go to the plan reviewer: {out!r}\n{err[-800:]}"
    assert next_of(card) == "**Next:** The reviewer starts now.", f"211.5: the card's Next line is {next_of(card)!r}"
    assert board == "Plan none", f"211.5: the card should be in Plan without Needs you, not {board!r}"
    out, card, board, err = decide(tmp_path / "off", rec, STORY_Q_PLANNED, {})
    assert out == "stop" and next_of(card).startswith(f"**Next:** @{OWNER}") and board == "Plan needs", \
        f"211.5: off autopilot a plan with questions no longer stops for the owner: {out!r} {next_of(card)!r} {board!r}"


def check_review(tmp, review, plan):
    """Run the code check of a plan review (`python3 -m dokima.agent check review`); returns its exit code and output."""
    t = str(tmp)
    os.makedirs(t, exist_ok=True)
    json.dump(review, open(f"{t}/review.json", "w"))
    json.dump(plan, open(f"{t}/plan.json", "w"))
    env = {**os.environ, "STAGE": "plan", "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
           "PYTHONPATH": ts.ROOT}
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "check", "review", f"{t}/review.json", f"{t}/plan.json", N],
                       cwd=ts.ROOT, env=env, capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr


def test_the_plan_reviewer_judges_every_question_against_the_owners_words(record_property, tmp_path):
    """The plan reviewer must judge every question's assumption, never accepting one that changes how the system works or what it costs.

    Runs the code check on plan reviews of a plan with two questions. Rejected: no judgements (both questions named),
    one judged and one not (the missing one named), an accepted one with no matched words, one whose source is
    neither this issue, one of its comments nor AGENTS.md (an outside site, and a comment on another issue), an
    accepted value that is not true or false, a judgement that does not say true or false whether the assumption
    changes how the system works or what it costs, an accepted one that does change them, one not accepted with no
    reason why, and a judgement of a question the plan does not ask. Passed: both judged (one accepted from AGENTS.md
    and one from an issue comment, or one accepted and one not, with its why, also when the one not accepted changes
    them), and a plan with no questions reviewed with no judgements. The reviewer's prompt must ask for these
    judgements."""
    record_property("proves", "211.5")
    q1, q2 = QUESTIONS[0]["question"], QUESTIONS[1]["question"]
    bad = (("none judged", {}, [q1, q2]),
           ("one missing", {"assumptions": [ACCEPT_1]}, [q2]),
           ("no matched words", {"assumptions": [ACCEPT_1, {k: v for k, v in ACCEPT_2.items() if k != "matched"}]}, ["matched"]),
           ("source elsewhere", {"assumptions": [ACCEPT_1, {**ACCEPT_2, "source": "https://example.com/post"}]}, ["source"]),
           ("another issue", {"assumptions": [ACCEPT_1, {**ACCEPT_2, "source": "https://github.com/o/r/issues/58#issuecomment-77"}]},
            ["source"]),
           ("changes not said", {"assumptions": [ACCEPT_1, {k: v for k, v in ACCEPT_2.items() if k != "changes"}]}, ["changes"]),
           ("changes not true or false", {"assumptions": [ACCEPT_1, {**ACCEPT_2, "changes": "no"}]}, ["changes"]),
           ("accepted though it changes them", {"assumptions": [ACCEPT_1, COSTLY_2]}, ["changes", QUESTIONS[1]["question"]]),
           ("accepted not true or false", {"assumptions": [ACCEPT_1, {**ACCEPT_2, "accepted": "yes"}]}, ["accepted"]),
           ("no why", {"assumptions": [ACCEPT_1, {k: v for k, v in REFUSE_2.items() if k != "why"}]}, ["why"]),
           ("not the plan's question", {"assumptions": [ACCEPT_1, ACCEPT_2, {**ACCEPT_2, "question": "Should it be blue?"}]},
            ["Should it be blue?"]))
    for case, extra, named in bad:
        code, out = check_review(tmp_path / case.replace(" ", "-"), {**APPROVE, **extra}, STORY_Q)
        assert code != 0, f"211.5 ({case}): the check passed a plan review that does not judge every question properly"
        for word in named:
            assert word in out, f"211.5 ({case}): the check's problems do not name {word!r}:\n{out}"
    for case, review, plan in (("both accepted", {**APPROVE, "assumptions": [ACCEPT_1, ACCEPT_2]}, STORY_Q),
                               ("one not accepted", {**APPROVE, "assumptions": [ACCEPT_1, REFUSE_2]}, STORY_Q),
                               ("not accepted, it changes them", {**APPROVE, "assumptions": [ACCEPT_1, {**REFUSE_2, "changes": True}]},
                                STORY_Q),
                               ("no questions", APPROVE, ts.STORY)):
        code, out = check_review(tmp_path / case.replace(" ", "-"), review, plan)
        assert code == 0, f"211.5 ({case}): the check rejected a well-judged plan review:\n{out}"
    prompt = open(os.path.join(ts.ROOT, "dokima", "roles", "reviewer.md")).read()
    for word in ("assumptions", "matched", "changes"):
        assert f"`{word}`" in prompt, \
            f"211.5: the reviewer's prompt does not ask for `{word}` when it judges each question's assumption"


def test_on_autopilot_an_accepted_assumption_goes_on_and_one_not_accepted_stops(record_property, tmp_path, monkeypatch):
    """On autopilot, when the reviewer accepts every assumption the river goes on; a question it does not accept stops for the owner.

    Runs the plan review of #57's plan with two questions, on autopilot. Approving with both accepted, the worker
    must start with one "Autopilot: plan approved, starting work" line. Approving with the second not accepted, and
    blocking with it not accepted, nothing may start and no line be posted, and the card's Next line must mention the
    owner and name the question not accepted, with Needs you. Approving with the second accepted though the reviewer
    says it changes how the system works or what it costs is rejected by code and stops the same way."""
    record_property("proves", "211.5")
    r = run(monkeypatch, tmp_path / "accepted", "reviewer", "plan", STORY_Q_PLANNED, ON, try_branch=True,
            review={**APPROVE, "assumptions": [ACCEPT_1, ACCEPT_2]})
    assert r.agent_started() and not r.failed, f"211.5: setup: the plan review did not pass its check:\n{r.tail()}"
    assert starts(r) == [("worker", N)], f"211.5: with every assumption accepted the worker did not start: {starts(r)}"
    assert len(lines(r, LINE_PLAN)) == 1, f"211.5: the issue did not get exactly one {LINE_PLAN!r}: {autopilot_lines(r)}"
    for case, review in (("approve", {**APPROVE, "assumptions": [ACCEPT_1, REFUSE_2]}),
                         ("block", {**BLOCK, "assumptions": [ACCEPT_1, REFUSE_2]})):
        r = run(monkeypatch, tmp_path / case, "reviewer", "plan", STORY_Q_PLANNED, ON, try_branch=True, review=review)
        assert r.agent_started() and not r.failed, f"211.5 ({case}): setup: the plan review did not pass its check:\n{r.tail()}"
        assert_stops(r, "", "211.5", case)
        nxt = next_of(record_body(r, f"211.5 ({case})"))
        assert QUESTIONS[1]["question"] in nxt, f"211.5 ({case}): the Next line does not name the question not accepted: {nxt!r}"
        assert QUESTIONS[0]["question"] not in nxt, f"211.5 ({case}): the Next line names a question that was accepted: {nxt!r}"
    r = run(monkeypatch, tmp_path / "changes", "reviewer", "plan", STORY_Q_PLANNED, ON, try_branch=True,
            review={**APPROVE, "assumptions": [ACCEPT_1, COSTLY_2]})
    assert r.agent_started(), f"211.5 (changes): setup: the plan review did not run:\n{r.tail()}"
    assert_stops(r, "rejected by code", "211.5", "accepted though it changes how the system works or what it costs")
    body = record_body(r, "211.5 (changes)")
    assert "changes" in body.split("<details>")[0], \
        f"211.5 (changes): the card does not say the accepted assumption changes how the system works or what it costs:\n{body[:900]}"


def test_an_assumption_is_accepted_only_on_words_the_owner_really_said(record_property, tmp_path):
    """On autopilot an accepted assumption goes on only when its matched words really are the owner's, where it says.

    Decides what follows an approving plan review of #57's plan with two questions, on autopilot. The worker starts
    when the matched words are word for word in AGENTS.md, in a code owner's comment on #57 that the source links,
    or in the issue's own text. Every other case stops for the owner, sets Needs you and names the question in the
    Next line (and not the other one): words that are not in the comment it links, a comment by someone who is not a
    code owner, a comment the bot posted, a comment that does not exist, words not in the issue's text, and words
    not in AGENTS.md."""
    record_property("proves", "211.5")
    q1, q2 = QUESTIONS[0]["question"], QUESTIONS[1]["question"]
    good = (("owner's comment and AGENTS.md", [ACCEPT_1, ACCEPT_2]),
            ("the issue's own text", [ACCEPT_1, {**ACCEPT_2, "matched": "Fix it.", "source": ISSUE}]))
    for case, judged in good:
        rec = ts.review_record({**APPROVE, "assumptions": judged})
        out, card, board, err = decide(tmp_path / case.replace(" ", "-").replace("'", ""), rec, STORY_Q_PLANNED, ON)
        assert out == "start worker", f"211.5 ({case}): the owner's real words did not let the worker start: {out!r} {next_of(card)!r}\n{err[-800:]}"
        assert board == "Work none", f"211.5 ({case}): the card should be in Work without Needs you, not {board!r}"
    bad = (("words not in the comment", [ACCEPT_1, {**ACCEPT_2, "matched": "Show the cost of every run."}], q2, q1),
           ("not a code owner's comment", [ACCEPT_1, {**ACCEPT_2, "matched": "Cards should name the step that broke.",
                                                      "source": ISSUE + "#issuecomment-78"}], q2, q1),
           ("the bot's comment", [ACCEPT_1, {**ACCEPT_2, "matched": QUESTIONS[1]["assumption"],
                                             "source": ISSUE + "#issuecomment-79"}], q2, q1),
           ("no such comment", [ACCEPT_1, {**ACCEPT_2, "source": ISSUE + "#issuecomment-99"}], q2, q1),
           ("words not in the issue's text", [ACCEPT_1, {**ACCEPT_2, "source": ISSUE}], q2, q1),
           ("words not in AGENTS.md", [{**ACCEPT_1, "matched": "a failed run always moves to Needs you"}, ACCEPT_2], q1, q2))
    for case, judged, named, other in bad:
        rec = ts.review_record({**APPROVE, "assumptions": judged})
        out, card, board, err = decide(tmp_path / case.replace(" ", "-").replace("'", ""), rec, STORY_Q_PLANNED, ON)
        nxt = next_of(card)
        assert out == "stop", f"211.5 ({case}): an assumption accepted on words the owner did not say there let the river go on: {out!r}"
        assert nxt.startswith(f"**Next:** @{OWNER}") and board == "Plan needs", \
            f"211.5 ({case}): the stop does not mention the owner with Needs you: {nxt!r} {board!r}\n{err[-800:]}"
        assert named in nxt and other not in nxt, \
            f"211.5 ({case}): the Next line should name only the question whose words were not found ({named!r}): {nxt!r}"


def test_when_autopilot_cannot_be_read_the_river_stops_and_says_why(record_property, tmp_path, monkeypatch):
    """When GitHub cannot say whether the issue is on autopilot, the river stops for the owner and says so.

    Runs the approving plan review of #57, on autopilot, while every read of #57's labels fails on GitHub. Nothing may
    start, no Autopilot line be posted, and the card's Next line must mention the owner, set Needs you and say
    autopilot could not be read. Beside it, the same review with the labels readable starts the worker."""
    record_property("proves", "211.6")
    r = run(monkeypatch, tmp_path / "readable", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=APPROVE)
    assert starts(r) == [("worker", N)], f"211.6: with its labels readable the approved plan on autopilot did not start the worker: {starts(r)}"
    r = run(monkeypatch, tmp_path / "unreadable", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True, review=APPROVE,
            options={"fail_labels": True})
    assert r.agent_started(), f"211.6: setup: the plan review did not run:\n{r.tail()}"
    assert_stops(r, "", "211.6", "labels unreadable")
    nxt = next_of(record_body(r, "211.6"))
    assert "autopilot" in nxt.lower(), f"211.6: the Next line does not say autopilot could not be read: {nxt!r}"

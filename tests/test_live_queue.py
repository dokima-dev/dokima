"""Every run's card goes up within seconds of what started it, says when it waits, and stays the run's one card (#186).

These tests run the workflows the way GitHub runs them, with the machine from test_start.py: the command listener
(.github/workflows/commands.yml) on a code owner's comment, then the agent workflow (.github/workflows/agent.yml) it
calls, with exactly the inputs the listener's job hands it. A hand-off runs the agent workflow, then runs it again
the way GitHub would on the dokima-next signal it sent, with exactly the payload of that signal. Between the two
halves the tests read what GitHub showed: that is the moment a run waits for its turn on the issue.

The fake GitHub here also knows runs: options.json may say "runs": {"41": "in_progress"}, and GitHub then answers
`gh api repos/o/r/actions/runs/41`, `gh run view 41` and the run lists with that status; every other run is
completed. A run another run waits for is found from GitHub's records: its card on the issue or its pull request,
which links to the run, and GitHub's word that the run is not completed. Every dokima-next signal's payload is kept.
"""
import json
import os
import re
import shutil

import pytest

import test_start as ts
from test_start import N, OWNER, PR, SPLIT_APPROVED, STORY_APPROVED, STORY_PLANNED, Ctx, evaluate, condition, fill

from dokima import agent

BOT_ACTOR = "dokima-runtime[bot]"
OTHER_RUN = "41"
OTHER_RUN_URL = f"https://github.com/o/r/actions/runs/{OTHER_RUN}"
BLOCK = {"previous_step": {"did": ["Planned one criterion."], "decided": [], "open": []},
         "stage": "plan", "round": 1, "verdict": "block", "summary": "One test is missing.",
         "raises": [{"kind": "blocker", "to": "planner", "label": "57.1", "text": "No good-case test.", "evidence": "The plan has one test for the bad case only."}],
         "asks": [{"ask": "Fix it.", "source": "https://github.com/o/r/issues/57", "criterion": f"{N}.1"}], "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3", f"{N}.1")]}
WORK = {"summary": "Made it.", "criteria": {f"{N}.1": "x.py, the change"}, "evidence": "pytest -q: 1 passed"}
ICON = re.compile(r'<img[^>]*src="https://raw\.githubusercontent\.com/[^/"]+/[^/"]+/main/dokima/icons/([A-Za-z0-9_-]+)\.svg"')
STAGE_WORDS = {"planner": ("planner",), "reviewer-plan": ("reviewer (plan)", "plan review"),
               "worker": ("worker",), "reviewer-pr": ("reviewer (pr)", "code review")}

RUNS_GH = r'''
def run_status(rid):
    return (opts.get("runs") or {}).get(str(rid), "completed")
def run_obj(rid):
    s = run_status(rid)
    return {"id": int(rid), "databaseId": int(rid), "status": s, "conclusion": "success" if s == "completed" else None,
            "html_url": f"https://github.com/o/r/actions/runs/{rid}", "url": f"https://github.com/o/r/actions/runs/{rid}",
            "name": "agent", "workflowName": "agent", "display_title": f"planner for #57", "displayTitle": f"planner for #57"}
RUNS_PATH = next((x for x in a[1:] if re.fullmatch(r"/?repos/o/r/actions/runs/\d+", x)), None) if a[:1] == ["api"] else None
LIST_PATH = next((x for x in a[1:] if re.fullmatch(r"/?repos/o/r/actions/(?:workflows/[^/]+/)?runs(?:\?.*)?", x)), None) if a[:1] == ["api"] else None
if a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/dispatches", x) for x in a):
    payload = {}
    if "--input" in a:
        p = flag("--input")
        payload = (json.load(sys.stdin if p == "-" else open(p)) or {}).get("client_payload") or {}
    for i, x in enumerate(a):
        m = re.fullmatch(r"client_payload\[([^\]]+)\]=(.*)", a[i + 1], re.S) if x in ("-f", "-F", "--field", "--raw-field") and i + 1 < len(a) else None
        if m:
            payload[m.group(1)] = m.group(2)
    ds = json.load(open(os.path.join(d, "dispatches.json"))) if os.path.exists(os.path.join(d, "dispatches.json")) else []
    ds.append(payload)
    json.dump(ds, open(os.path.join(d, "dispatches.json"), "w"))
    sys.exit(0)
if RUNS_PATH:
    out(run_obj(RUNS_PATH.rstrip("/").rsplit("/", 1)[1]))
    sys.exit(0)
if LIST_PATH:
    out({"total_count": len(opts.get("runs") or {}), "workflow_runs": [run_obj(r) for r in (opts.get("runs") or {})]})
    sys.exit(0)
if a[:2] == ["run", "view"]:
    r = run_obj(a[2])
    print(r["status"] if (flag("-q") or flag("--jq")) == ".status" else json.dumps(r))
    sys.exit(0)
if a[:2] == ["run", "list"]:
    rs = [run_obj(r) for r in (opts.get("runs") or {})]
    print(json.dumps(rs))
    sys.exit(0)
'''

FAKE_CLAUDE_ANY = r'''#!/usr/bin/env python3
"""A stand-in for Claude Code that hands back whatever files the test put in FAKE_HANDBACK_DIR, else the review.

Like test_start.py's, it keeps what GitHub showed when it started and leaves a session log naming its model."""
import json, os, shutil, time
d = os.environ["FAKE_GH_DIR"]
store = os.path.join(d, "comments.json")
json.dump(json.load(open(store)) if os.path.exists(store) else [], open(os.path.join(d, "at-agent-start.json"), "w"))
open(os.path.join(d, "agent-started-at"), "w").write(str(time.time()))
open(os.environ["FAKE_CLAUDE_MARK"], "w").write("started")
src = os.environ.get("FAKE_HANDBACK_DIR", "")
if src and os.path.isdir(src) and os.listdir(src):
    for f in os.listdir(src):
        shutil.copy(os.path.join(src, f), os.path.join(os.environ["OUT"], f))
else:
    shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(os.environ["OUT"], "review.json"))
logs = os.path.join(os.environ["HOME"], ".claude", "projects", "p")
os.makedirs(logs, exist_ok=True)
open(os.path.join(logs, "s.jsonl"), "w").write(json.dumps({"message": {"model": os.environ["MODEL"], "role": "assistant", "content": "Done."}}) + "\n")
print(json.dumps({"num_turns": 1, "duration_ms": 1000, "usage": {}}))
'''


def other_runs_card(role="planner", stage=""):
    """The live card of another run (run 41) on the same issue, the way agent.yml puts one up while it works."""
    keep = {k: os.environ.get(k) for k in ("GITHUB_RUN_ID", "GITHUB_REPOSITORY", "GITHUB_SERVER_URL")}
    os.environ.update(GITHUB_RUN_ID=OTHER_RUN, GITHUB_REPOSITORY="o/r", GITHUB_SERVER_URL="https://github.com")
    try:
        return agent.live_card(role, stage, "working")
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class River(ts.Machine):
    """A machine on which a command or a hand-off runs through, with GitHub's runs and dokima-next payloads faked.

    `seed` puts comments on GitHub before anything runs: (kind, number, body) as Dokima's bot posted them."""

    def __init__(self, tmp, comments, try_branch=False, actor=OWNER, gh_fail="", options=None, seed=(), review=None,
                 handback=None):
        super().__init__(tmp, comments, try_branch=try_branch, actor=actor, gh_fail=gh_fail, options=options)
        t = self.tmp
        fake = ts.FAKE_GH.replace('if a[:2] == ["issue", "view"]:', RUNS_GH + 'if a[:2] == ["issue", "view"]:', 1)
        assert fake != ts.FAKE_GH, "test setup: could not teach the fake GitHub about runs"
        open(f"{t}/bin/gh", "w").write(fake.replace("#!/usr/bin/env python3", f"#!{ts.sys.executable}"))
        open(f"{t}/bin/claude", "w").write(FAKE_CLAUDE_ANY.replace("#!/usr/bin/env python3", f"#!{ts.sys.executable}"))
        if review is not None:
            json.dump(review, open(f"{t}/review.json", "w"))
        os.makedirs(f"{t}/handback")
        for name, data in (handback or {}).items():
            json.dump(data, open(f"{t}/handback/{name}", "w"))
        store = [{"id": 4000 + i, "kind": kind, "number": int(number), "created": "2026-10-07T11:00:00.000000Z",
                  "versions": [body], "author": agent.BOT} for i, (kind, number, body) in enumerate(seed, 1)]
        json.dump(store, open(f"{t}/gh/comments.json", "w"), indent=1)
        self.seeded = {c["id"] for c in store}
        self.snapshots = {}

    def base_env(self, event_name):
        """The environment every step starts from, with the hand-back folder for the fake agent."""
        return {**super().base_env(event_name), "FAKE_HANDBACK_DIR": f"{self.tmp}/handback"}

    def own(self):
        """Every comment the runs wrote, leaving out what the test put on GitHub before they started."""
        return [c for c in self.comments() if c["id"] not in self.seeded]

    def dispatches(self):
        """The payload of every dokima-next signal sent so far."""
        p = f"{self.tmp}/gh/dispatches.json"
        return json.load(open(p)) if os.path.exists(p) else []

    def github(self, event_name, actor, event):
        """GitHub's own context for a run."""
        return Ctx(event_name=event_name, actor=actor, event=event, run_id="42", run_attempt="1",
                   server_url="https://github.com", repository="o/r", token="fake-github-token")

    def listen(self, body, on_pr=False):
        """Run commands.yml on a comment; returns the inputs it hands the agent workflow, or None when it calls none."""
        number = int(PR if on_pr else N)
        issue = {"number": number, **({"pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{number}"}} if on_pr else {})}
        event = {"comment": {"body": body, "user": {"login": self.actor, "type": "User"}}, "issue": issue}
        open(f"{self.tmp}/event.json", "w").write(json.dumps(event))
        github = self.github("issue_comment", self.actor, event)
        self.listener_github = github
        wf = ts.workflow("commands.yml")
        jobs = wf["jobs"]
        results, outputs, called = {}, {}, None
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
                    assert "agent.yml" in job["uses"], f"test setup: the listener calls an unknown workflow {job['uses']}"
                    called = {k: fill(v, ctx, status) for k, v in (job.get("with") or {}).items()}
                    results[name] = "success"
                    continue
                results[name], outputs[name] = self.run_job(name, job, ctx, "issue_comment",
                                                            [("/tmp/", f"{self.tmp}/jobs/{name}/tmp/")], wf.get("defaults"))
            assert progressed, "test setup: the listener's jobs wait on each other"
        self.listener_results = results
        return called

    def agent(self, name, inputs=None, payload=None, actor=None):
        """Run agent.yml's job once: called by the listener with `inputs`, or on a dokima-next signal with `payload`."""
        t = self.tmp
        for p in (f"{t}/claude-started", f"{t}/gh/at-agent-start.json"):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(f"{t}/home/.claude", ignore_errors=True)
        if payload is not None:
            self.actor = actor or BOT_ACTOR
            event = {"action": "dokima-next", "client_payload": payload}
            open(f"{t}/event.json", "w").write(json.dumps(event))
            github, event_name, inp = self.github("repository_dispatch", self.actor, event), "repository_dispatch", Ctx()
        else:
            github, event_name, inp = self.listener_github, "issue_comment", Ctx(inputs or {})
        ctx = {"inputs": inp, "github": github, "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf = ts.workflow("agent.yml")
        result, _ = self.run_job(name, wf["jobs"]["run"], ctx, event_name,
                                 [("/tmp/", f"{t}/{name}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        p = f"{t}/gh/at-agent-start.json"
        self.snapshots[name] = json.load(open(p)) if os.path.exists(p) else None
        return result

    def dispatch_run(self, name, inputs):
        """Run agent.yml by hand (workflow_dispatch) as the owner, the way test_start.py's Run does."""
        open(f"{self.tmp}/event.json", "w").write(json.dumps({"inputs": inputs}))
        self.listener_github = self.github("workflow_dispatch", self.actor, Ctx())
        return self.agent(name, inputs=inputs)


def visible(body):
    """A body without its folded JSON record: the part the owner reads."""
    return re.sub(r"```json\n.*?\n```", "", body, flags=re.S)


def is_rec(body):
    """True when a body reads as a record of a run, posted by the bot."""
    return bool(agent.records([{"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T00:00:00Z"}])) \
        or agent.is_record({"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T00:00:00Z"})


def where(c):
    """Where a fake GitHub comment is, in words."""
    return f"{'PR' if c['kind'] == 'pr' else 'issue'} #{c['number']}"


def assert_queued_card(c, crit, stage_key, kind, number):
    """One comment is a queued card for that stage, posted by Dokima's bot where it belongs, not yet a record."""
    body = c["versions"][-1]
    assert (c["kind"], str(c["number"])) == (kind, str(number)), \
        f"{crit}: the queued card for the {stage_key} is on {where(c)}, expected {kind} #{number}"
    assert c["author"] == agent.BOT, f"{crit}: the queued card was posted by {c['author']}, not Dokima's bot"
    assert not is_rec(body), f"{crit}: the queued card already reads as a record:\n{body[:600]}"
    text = visible(body).lower()
    assert "queued" in text, f"{crit}: the card does not say queued:\n{body[:600]}"
    assert any(w in text for w in STAGE_WORDS[stage_key]), \
        f"{crit}: the queued card does not name its stage ({' or '.join(STAGE_WORDS[stage_key])}):\n{body[:600]}"
    shown = ICON.findall(body)
    own = {f[:-4] for f in os.listdir(os.path.join(ts.ROOT, "dokima", "icons")) if f.endswith(".svg")}
    assert shown and set(shown) <= own, f"{crit}: the queued card shows none of Dokima's own icons: {shown}"


def assert_same_card_became_record(m, card_id, crit, role, stage=None):
    """The run left no comment of its own: the queued card, edited in place, is now its one record."""
    cs = m.own()
    assert [c["id"] for c in cs] .count(card_id) == 1, f"{crit}: the queued card is gone"
    c = next(c for c in cs if c["id"] == card_id)
    final = c["versions"][-1]
    recs = agent.records([{"author": {"login": agent.BOT}, "body": final, "createdAt": "2026-10-08T00:00:00Z"}])
    assert len(c["versions"]) >= 2 and len(recs) == 1, \
        (f"{crit}: the queued card was never edited into the run's record; its versions are:\n"
         + "\n---\n".join(v[:300] for v in c["versions"]))
    r = recs[0]
    assert (r.get("attempt") if r["role"] == "not-started" else r["role"]) == role, \
        f"{crit}: the card became the record of {r['role']}/{r.get('attempt')}, not of the {role} run that it announced"
    if stage is not None:
        assert (r.get("stage") or "") == stage, f"{crit}: the card became the record of stage {r.get('stage')}, expected {stage}"


# Each command: (comment, on a PR?, issue history, try branch?, open PR?, stage key, where the card goes, role, stage)
COMMANDS = {
    "plan": ("/plan", False, STORY_PLANNED, True, False, "planner", ("issue", N), "planner", ""),
    "review-plan": ("/review", False, STORY_PLANNED, True, False, "reviewer-plan", ("issue", N), "reviewer", "plan"),
    "work": ("/work", False, STORY_APPROVED, True, True, "worker", ("pr", PR), "worker", ""),
    "review-pr": ("/review", True, STORY_APPROVED, True, True, "reviewer-pr", ("pr", PR), "reviewer", "pr"),
}


@pytest.fixture(scope="module")
def commands(tmp_path_factory):
    """Each code owner's command run through the listener and then the agent run it calls, with what GitHub showed between."""
    base = tmp_path_factory.mktemp("commands")
    done = {}
    for key, (body, on_pr, history, branch, pr_open, *_rest) in COMMANDS.items():
        m = River(base / key, history, try_branch=branch, options={"pr_open": pr_open})
        called = m.listen(body, on_pr=on_pr)
        between = m.own()
        result = m.agent("agent", inputs=called) if called is not None else None
        done[key] = (m, called, between, result)
    return done


def test_a_code_owners_command_puts_up_a_queued_card_that_the_run_then_updates(record_property, commands):
    """Each of /plan, /review on the issue, /work and /review on the pull request puts up a queued card before its run starts, and the run updates that same card.

    Runs the command listener on each command from the code owner and reads GitHub the moment the listener is done,
    before the agent workflow it calls has run a single step: exactly one comment, by Dokima's bot, a card that names
    its stage, says queued and is not a record yet, on issue #57 for the planner and plan review and on pull request
    #60 for the worker and code review (the PR is open). Then the agent workflow runs with exactly what the listener
    handed it: it posts no comment of its own, and the queued card, edited in place, becomes that run's one record."""
    record_property("proves", "186.1")
    for key, (m, called, between, result) in commands.items():
        _, _, _, _, _, stage_key, (kind, number), role, stage = COMMANDS[key]
        crit = f"186.1 ({key})"
        assert called is not None, f"{crit}: setup: the code owner's command did not start the agent workflow:\n{m.tail()}"
        assert len(between) == 1, (f"{crit}: when the listener was done, before the run started, GitHub showed {len(between)} "
                                   f"comments, expected one queued card: {[(where(c), c['versions'][-1][:150]) for c in between]}\n{m.tail()}")
        assert_queued_card(between[0], crit, stage_key, kind, number)
        cs = m.own()
        assert len(cs) == 1, (f"{crit}: after the run there are {len(cs)} comments, expected only the one card: "
                              f"{[(where(c), c['versions'][-1][:150]) for c in cs]}\n{m.tail()}")
        assert_same_card_became_record(m, between[0]["id"], crit, role, stage)


@pytest.fixture(scope="module")
def waiting(tmp_path_factory):
    """Commands given while another run's card is up: run 41 still running on the issue, on the PR, or long finished."""
    base = tmp_path_factory.mktemp("waiting")
    cases = {
        "issue": ([("issue", N, other_runs_card())], {"runs": {OTHER_RUN: "in_progress"}}, "/review"),
        "pr": ([("pr", PR, other_runs_card("worker"))], {"runs": {OTHER_RUN: "in_progress"}, "pr_open": True}, "/plan"),
        "queued-run": ([("issue", N, other_runs_card())], {"runs": {OTHER_RUN: "queued"}}, "/review"),
        "finished": ([("issue", N, other_runs_card())], {"runs": {OTHER_RUN: "completed"}}, "/review"),
        "none": ([], {"runs": {}}, "/review"),
    }
    done = {}
    for key, (seed, options, body) in cases.items():
        m = River(base / key, STORY_PLANNED, try_branch=True, options=options, seed=seed)
        called = m.listen(body)
        between = m.own()
        if called is not None:
            m.agent("agent", inputs=called)
        done[key] = (m, called, between)
    return done


def test_a_card_says_it_is_waiting_for_the_run_ahead_of_it(record_property, waiting):
    """A command given while another run on the issue is still going gets a card that says it is waiting for that run.

    Puts the card of run 41 on issue #57 (and, in a second case, on its pull request #60), with GitHub saying run 41 is
    in progress, and in a third case only queued; then the owner gives a command. The new card says waiting and links
    run 41. Two neighbours must not say waiting: run 41's card is still up but GitHub says that run has finished, and no
    other run at all; both cards say queued. When the run itself starts, its card no longer says waiting."""
    record_property("proves", "186.2")
    for key in ("issue", "pr", "queued-run"):
        m, called, between = waiting[key]
        crit = f"186.2 ({key})"
        assert called is not None and len(between) == 1, \
            f"{crit}: the command did not put up exactly one card before its run: {len(between)}\n{m.tail()}"
        text = visible(between[0]["versions"][-1])
        assert "waiting" in text.lower(), f"{crit}: run 41 is still going, but the new card does not say it is waiting:\n{text[:600]}"
        assert OTHER_RUN_URL in text, f"{crit}: the waiting card does not link the run it waits for ({OTHER_RUN_URL}):\n{text[:600]}"
        assert not is_rec(between[0]["versions"][-1]), f"{crit}: the waiting card reads as a record"
        at_start = [c for c in (m.snapshots.get("agent") or []) if c["id"] == between[0]["id"]]
        assert at_start and "waiting" not in visible(at_start[0]["versions"][-1]).lower(), \
            f"{crit}: when the run's agent started, its card still said waiting (or was gone):\n{at_start[0]['versions'][-1][:400] if at_start else ''}\n{m.tail()}"
    for key in ("finished", "none"):
        m, called, between = waiting[key]
        crit = f"186.2 ({key})"
        assert called is not None and len(between) == 1, \
            f"{crit}: the command did not put up exactly one card before its run: {len(between)}\n{m.tail()}"
        text = visible(between[0]["versions"][-1])
        assert "waiting" not in text.lower(), f"{crit}: no other run is going, but the card says it is waiting:\n{text[:600]}"
        assert "queued" in text.lower(), f"{crit}: the card with no run ahead of it does not say queued:\n{text[:600]}"


@pytest.fixture(scope="module")
def handoffs(tmp_path_factory):
    """Hand-offs the river starts by itself, each run through to the next stage's run.

    plan-block: a plan review blocks, so the planner starts again. work-done: a worker passes, so the code review starts
    on the open PR. waiting: the same plan review blocks while run 41's card is up and GitHub says run 41 is going."""
    base = tmp_path_factory.mktemp("handoffs")
    cases = {
        "plan-block": (STORY_PLANNED, {}, (), {"review": BLOCK}, {"role": "reviewer", "stage": "plan", "issue": N}),
        "work-done": (STORY_APPROVED, {"pr_open": True}, (), {"handback": {"work.json": WORK}},
                      {"role": "worker", "stage": "plan", "issue": N}),
        "waiting": (STORY_PLANNED, {"runs": {OTHER_RUN: "in_progress"}}, [("issue", N, other_runs_card("worker"))],
                    {"review": BLOCK}, {"role": "reviewer", "stage": "plan", "issue": N}),
    }
    done = {}
    for key, (history, options, seed, kw, inputs) in cases.items():
        m = River(base / key, history, try_branch=True, options=options, seed=seed, **kw)
        m.dispatch_run("first", inputs)
        first = m.own()
        payloads = m.dispatches()
        second = None
        if len(payloads) == 1:
            open(f"{m.tmp}/review.json", "w").write(json.dumps(BLOCK))
            shutil.rmtree(f"{m.tmp}/handback")
            os.makedirs(f"{m.tmp}/handback")
            second = m.agent("second", payload=payloads[0])
        done[key] = (m, first, payloads, second)
    return done


def test_every_hand_off_and_split_uses_the_same_one_card(record_property, handoffs, tmp_path):
    """A hand-off the river starts puts up the next run's queued card, which that run updates; filing a split uses one card too.

    A plan review that blocks hands to the planner, and a worker that passes hands to the code review on pull request
    #60. When the first run is done, GitHub shows its own record and exactly one more comment: the next stage's queued
    card, by Dokima's bot, where that stage's record will go. The next run then starts on exactly the dokima-next
    signal that was sent, posts no comment of its own, and that queued card becomes its one record. `/work` on an
    approved split leaves exactly one comment, first a card that is not a record and then, edited in place, the
    "Split filed" record; and when GitHub refuses to file the stories, that one card becomes the record saying why."""
    record_property("proves", "186.3")
    for key, nxt, stage_key, (kind, number) in (("plan-block", "planner", "planner", ("issue", N)),
                                                ("work-done", "reviewer", "reviewer-pr", ("pr", PR))):
        m, first, payloads, second = handoffs[key]
        crit = f"186.3 ({key})"
        assert len(payloads) == 1, f"{crit}: setup: the river did not start the {nxt} exactly once: {payloads}\n{m.tail()}"
        recs = [c for c in first if is_rec(c["versions"][-1])]
        cards = [c for c in first if not is_rec(c["versions"][-1])]
        assert len(recs) == 1 and len(cards) == 1, \
            (f"{crit}: after the first run GitHub shows {len(recs)} records and {len(cards)} cards, expected its record and "
             f"the next stage's one queued card: {[(where(c), c['versions'][-1][:150]) for c in first]}\n{m.tail()}")
        assert_queued_card(cards[0], crit, stage_key, kind, number)
        cs = m.own()
        assert len(cs) == 2, (f"{crit}: after the {nxt}'s run there are {len(cs)} comments, expected the first run's record "
                              f"and the one card: {[(where(c), c['versions'][-1][:150]) for c in cs]}\n{m.tail()}")
        assert_same_card_became_record(m, cards[0]["id"], crit, nxt, "pr" if stage_key == "reviewer-pr" else None)

    r = River(tmp_path / "split", SPLIT_APPROVED)
    r.listen("/work")
    cs = r.own()
    assert len(cs) == 1, f"186.3 (split): filing the split left {len(cs)} comments, expected one card: {[c['versions'][-1][:150] for c in cs]}\n{r.tail()}"
    c = cs[0]
    assert len(c["versions"]) >= 2 and not is_rec(c["versions"][0]) and ICON.findall(c["versions"][0]), \
        f"186.3 (split): no card was up before the split was filed; the comment's first version was:\n{c['versions'][0][:500]}"
    recs = agent.records([{"author": {"login": agent.BOT}, "body": c["versions"][-1], "createdAt": "2026-10-08T00:00:00Z"}])
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("split", True)], \
        f"186.3 (split): the card did not become the passed Split filed record: {recs}"

    refused = "HTTP 403: Resource not accessible by integration (https://api.github.com/repos/o/r/issues)"
    r = River(tmp_path / "split-refused", SPLIT_APPROVED, gh_fail=f"issue create|{refused}")
    r.listen("/work")
    cs = r.own()
    assert len(cs) == 1, f"186.3 (split refused): the failed split left {len(cs)} comments, expected one card: {[c['versions'][-1][:150] for c in cs]}\n{r.tail()}"
    c = cs[0]
    recs = agent.records([{"author": {"login": agent.BOT}, "body": c["versions"][-1], "createdAt": "2026-10-08T00:00:00Z"}])
    assert len(c["versions"]) >= 2 and not is_rec(c["versions"][0]), \
        f"186.3 (split refused): no card was up before the split failed; the first version was:\n{c['versions'][0][:500]}"
    assert len(recs) == 1 and recs[0]["role"] == "not-started" and refused in c["versions"][-1], \
        f"186.3 (split refused): the card did not become the record saying why:\n{c['versions'][-1][:600]}"


def test_a_hand_off_card_says_when_it_waits_for_another_run(record_property, handoffs):
    """A hand-off made while another run on the issue is still going puts up a card that says it is waiting for that run.

    Run 41's card is up on issue #57 and GitHub says run 41 is in progress when a plan review blocks and hands back to
    the planner. The planner's queued card says waiting and links run 41; the same hand-off with no other run going
    (186.3's plan-block) says queued and not waiting."""
    record_property("proves", "186.2")
    m, first, payloads, _ = handoffs["waiting"]
    cards = [c for c in first if not is_rec(c["versions"][-1])]
    assert len(payloads) == 1 and len(cards) == 1, \
        f"186.2 (hand-off): setup: the hand-off did not put up exactly one card: {len(cards)} cards, {payloads}\n{m.tail()}"
    text = visible(cards[0]["versions"][-1])
    assert "waiting" in text.lower() and OTHER_RUN_URL in text, \
        f"186.2 (hand-off): run 41 is still going, but the planner's card does not say it waits for it:\n{text[:600]}"
    m, first, _, _ = handoffs["plan-block"]
    cards = [c for c in first if not is_rec(c["versions"][-1])]
    assert cards and "waiting" not in visible(cards[0]["versions"][-1]).lower(), \
        f"186.2 (hand-off): with no other run going, the planner's card says it is waiting:\n{visible(cards[0]['versions'][-1])[:600] if cards else ''}"


def test_only_a_code_owners_command_puts_up_a_card(record_property, tmp_path):
    """Only a code owner's command posts a queued card; a stranger's command or the owner's plain comment posts nothing.

    Runs the listener on /plan and on /review on pull request #60 from someone who is not a code owner, and on the
    owner's comments "/thanks" (not a command) and "Looks good" (no command at all): none of them leaves any comment or
    starts the agent workflow. Beside them, the owner's own /plan does leave exactly one card."""
    record_property("proves", "186.4")
    for name, body, actor, on_pr in (("stranger-plan", "/plan", "stranger", False), ("stranger-review", "/review", "stranger", True),
                                     ("not-command", "/thanks", OWNER, False), ("plain", "Looks good", OWNER, False)):
        m = River(tmp_path / name, STORY_PLANNED, try_branch=True, actor=actor, options={"pr_open": True})
        called = m.listen(body, on_pr=on_pr)
        assert called is None, f"186.4 ({name}): {body!r} by {actor} started the agent workflow"
        assert m.own() == [], f"186.4 ({name}): {body!r} by {actor} left comments: {[c['versions'][-1][:200] for c in m.own()]}"
    m = River(tmp_path / "owner", STORY_PLANNED, try_branch=True)
    m.listen("/plan")
    assert len(m.own()) == 1 and not is_rec(m.own()[0]["versions"][-1]), \
        f"186.4 (owner): the owner's /plan did not put up exactly one card: {[c['versions'][-1][:200] for c in m.own()]}\n{m.tail()}"

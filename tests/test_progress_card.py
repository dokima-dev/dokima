"""The run's live card shows coarse stages, set only by the run's own steps before and after the agent (#187).

The owner asked for no ticking minutes, no second job and no key on the agent's machine. So the card goes through
queued, setting up, agent working since HH:MM UTC, checking, and done (the run's record), each written by a step of the
run itself, and while the agent works it links to the run's live page on GitHub for detail.

These tests run the agent workflow (.github/workflows/agent.yml) the way GitHub runs it, with the machine from
test_start.py: a fake GitHub that keeps every version of every comment and which key made each call, and a fake
Claude Code that notes what GitHub showed when it started. To see the card at two moments of the run, each test run
also notes what GitHub showed when the step 'Install pytest and Claude Code' starts and when the step 'Code checks
the hand-back' starts (the test adds one line to the start of each step's script; the real workflow is unchanged).
Those two steps keep their names.

A card's stage is read from its first line, as the live card writes it today: `<icon> **Role** · <stage>`.
"""
import calendar
import json
import os
import re
import time

import pytest

import test_start as ts
from test_start import N, PIP_BROKEN, STORY_APPROVED, STORY_PLANNED, Run

from dokima import agent

RUN_URL = "https://github.com/o/r/actions/runs/42"
STAGE = re.compile(r"\*\*[^*\n]+\*\* · ([^\n]+)")
TIME = re.compile(r"(?:(\d{4})-(\d{2})-(\d{2})[ T])?(\d{2}):(\d{2})\s*UTC")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
MINUTES = re.compile(r"\b\d+\s*(?:min|mins|minutes?)\b|working for", re.I)
FULL = ["queued", "setting up", "working", "checking", "record"]
INSTALL = "Install pytest and Claude Code"
CHECK = "Code checks the hand-back"
BAD_REVIEW = {"verdict": "maybe"}
SECRETS = ["fake-claude-token", "fake-github-token"]
PLANTED = "https://fake-claude-token.fake-github-token.example"


def noting(name):
    """A shell line that keeps what GitHub shows now, and how many calls it has seen, under the name given."""
    return (f'cp "$FAKE_GH_DIR/comments.json" "$FAKE_GH_DIR/at-{name}.json" 2>/dev/null || echo "[]" > "$FAKE_GH_DIR/at-{name}.json"\n'
            f'(cat "$FAKE_GH_DIR/calls-meta.jsonl" 2>/dev/null || true) | wc -l > "$FAKE_GH_DIR/at-{name}-calls"\n')


class Scenario:
    """One finished run of the agent workflow, with what GitHub showed at the agent's start, at install and at the check."""

    def __init__(self, tmp, *args, **kw):
        self.t0 = time.time()
        self.run = Run(tmp, *args, **kw)
        gh = os.path.join(self.run.tmp, "gh")

        def read(name, parse=json.load):
            p = os.path.join(gh, name)
            return parse(open(p)) if os.path.exists(p) else None
        self.at_start = read("at-agent-start.json")
        self.agent_env = read("agent-env.json")
        self.agent_at = read("agent-started-at", lambda f: float(f.read()))
        self.at_install = read("at-install.json")
        self.at_check = read("at-check.json")
        self.check_calls = read("at-check-calls", lambda f: int(f.read().strip() or 0))
        self.meta = read("calls-meta.jsonl", lambda f: [json.loads(l) for l in f]) or []
        self.comments = self.run.comments()

    def tail(self):
        """The run's own log, for a failure message."""
        return self.run.tail()


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Every scenario these tests read, each run once through the whole agent workflow, noting the card at two steps."""
    real = ts.workflow
    planted = {"on": False}

    def watched(name):
        wf = real(name)
        if name == "agent.yml":
            if planted["on"]:
                wf["jobs"]["run"].setdefault("env", {})["GITHUB_SERVER_URL"] = PLANTED
            for step in wf["jobs"]["run"]["steps"]:
                if step.get("name") == INSTALL:
                    step["run"] = noting("install") + step["run"]
                if step.get("name") == CHECK:
                    step["run"] = noting("check") + step["run"]
        return wf
    t = tmp_path_factory.mktemp("stages")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(ts, "workflow", watched)
        found = {
            "pass": Scenario(t / "pass", "reviewer", "plan", STORY_PLANNED, try_branch=True),
            "fail": Scenario(t / "fail", "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BAD_REVIEW),
            "branch": Scenario(t / "branch", "worker", "", STORY_APPROVED),
            "install": Scenario(t / "install", "worker", "", STORY_APPROVED, try_branch=True, broken={"pip": PIP_BROKEN}),
            "no-edit": Scenario(t / "no-edit", "reviewer", "plan", STORY_PLANNED, try_branch=True, options={"fail_edits": True}),
        }
        planted["on"] = True
        found["secret"] = Scenario(t / "secret", "reviewer", "plan", STORY_PLANNED, try_branch=True)
        return found


def as_comment(body):
    """A body as a comment the bot posted, the way records() reads comments."""
    return {"author": {"login": agent.BOT}, "body": body, "createdAt": "2026-10-08T00:00:00Z"}


def stage_of(body):
    """The stage a version of the card shows: queued, setting up, working, checking, record, or what it says instead."""
    if agent.records([as_comment(body)]):
        return "record"
    m = STAGE.search(re.sub(r"```json\n.*?\n```", "", body, flags=re.S))
    said = m.group(1).strip() if m else body.strip()[:80]
    low = said.lower()
    for stage, words in (("queued", "queued"), ("setting up", "setting up"), ("working", "agent working since"),
                         ("checking", "checking")):
        if low.startswith(words):
            return stage
    return f"unknown: {said!r}"


def the_card(s, crit):
    """The run's one comment, checked to be the only one."""
    cs = s.comments
    assert len(cs) == 1, (f"{crit}: the run left {len(cs)} comments, expected its one card: "
                          f"{[c['versions'][-1][:150] for c in cs]}\n{s.tail()}")
    return cs[0]


def newest(snapshot, card):
    """The newest version of the card in what GitHub showed at one moment, or None when it was not up yet."""
    c = next((c for c in snapshot or [] if c["id"] == card["id"]), None)
    return c["versions"][-1] if c else None


def is_edit(args):
    """True when a gh call edits a comment."""
    method = next((args[i + 1] for i, x in enumerate(args[:-1]) if x in ("-X", "--method")), "").upper()
    return "--edit-last" in args or (args[:1] == ["api"] and method in ("PATCH", "POST")
                                     and any(re.fullmatch(r"/?repos/o/r/issues/comments/\d+", x) for x in args))


def is_revoke(args):
    """True when a gh call revokes the key it was made with."""
    method = next((args[i + 1] for i, x in enumerate(args[:-1]) if x in ("-X", "--method")), "").upper()
    return args[:1] == ["api"] and method == "DELETE" and any(re.fullmatch(r"/?installation/token", x) for x in args)


def test_the_card_goes_queued_setting_up_working_checking_done(record_property, runs):
    """The card goes queued, setting up, agent working, checking, then done, each stage once, in that order.

    Runs a plan review whose hand-back passes and one whose hand-back code rejects. Each leaves one comment whose
    versions are exactly: queued, setting up, agent working since, checking, and the run's record, nothing else and
    nothing between. When the tools start to install the card says setting up; when the agent starts it says agent
    working; when code starts checking the hand-back it says checking. Two runs that stop before their agent (no try
    branch, tools that fail to install) start at queued and go straight to their record, never saying working or
    checking; the one that reaches the install says setting up there. No second machine updates the card while the
    run goes: every job of the agent workflow other than the run waits for it and starts only when it failed (#514)."""
    record_property("proves", "187.1")
    jobs = ts.workflow("agent.yml")["jobs"]
    assert "run" in jobs, f"187.1: agent.yml should have its run job; it has {list(jobs)}"
    for name, job in jobs.items():
        if name == "run":
            continue
        needs = job.get("needs") or []
        needs = [needs] if isinstance(needs, str) else needs
        cond = str(job.get("if") or "")
        assert "run" in needs and "needs.run.result == 'failure'" in cond, \
            (f"187.1: agent.yml job '{name}' may run beside the run and update its card; a second job must wait for "
             f"the run and start only when it failed (needs: run, if: needs.run.result == 'failure'); it has "
             f"needs {needs}, if {cond!r}")
    for name in ("pass", "fail"):
        s = runs[name]
        assert s.run.agent_started(), f"187.1 ({name}): setup: the agent never started; stopped at '{s.run.failed_step}':\n{s.tail()}"
        card = the_card(s, f"187.1 ({name})")
        got = [stage_of(v) for v in card["versions"]]
        assert got == FULL, f"187.1 ({name}): the card went {got}, expected {FULL}:\n" + \
            "\n---\n".join(v[:300] for v in card["versions"])
        for moment, snap, want in (("the tools started to install", s.at_install, "setting up"),
                                   ("the agent started", s.at_start, "working"),
                                   ("code started checking the hand-back", s.at_check, "checking")):
            body = newest(snap, card)
            assert body is not None and stage_of(body) == want, \
                f"187.1 ({name}): when {moment} the card said {stage_of(body) if body else 'nothing'}, expected {want}"
    for name in ("branch", "install"):
        s = runs[name]
        assert not s.run.agent_started(), f"187.1 ({name}): setup: the agent started though the run should stop before it"
        card = the_card(s, f"187.1 ({name})")
        got = [stage_of(v) for v in card["versions"]]
        assert got[0] == "queued" and got[-1] == "record" and set(got[1:-1]) <= {"setting up"} and len(got) <= 3, \
            f"187.1 ({name}): a run that stopped before its agent went {got}, expected queued, maybe setting up, then its record"
    s = runs["install"]
    body = newest(s.at_install, the_card(s, "187.1 (install)"))
    assert body is not None and stage_of(body) == "setting up", \
        f"187.1 (install): when the tools started to install the card said {stage_of(body) if body else 'nothing'}, expected setting up"


def test_while_the_agent_works_the_card_gives_its_start_time_and_the_live_run_page_and_never_ticks(record_property, runs):
    """While the agent works, the card says since when, links to the run's live page, and is never edited.

    Reads what GitHub showed when the agent of a plan review started: the card says agent working since a time in UTC
    (HH:MM) no earlier than the minute the run began and no later than the agent's start, and holds a link to this
    run's page on GitHub (/actions/runs/42) whose words say it is live. From the agent's start until code checks its
    hand-back the card is not edited at all, and no version of any card in any run counts minutes."""
    record_property("proves", "187.2")
    s = runs["pass"]
    card = the_card(s, "187.2")
    body = newest(s.at_start, card)
    assert body is not None and stage_of(body) == "working", \
        f"187.2: when the agent started the card did not say agent working since:\n{(body or '')[:600]}"
    line = STAGE.search(body).group(1)
    m = TIME.search(line)
    assert m, f"187.2: the working card gives no start time as HH:MM UTC after 'agent working since': {line!r}"
    y, mo, d, h, mi = m.groups()
    if y:
        started = calendar.timegm((int(y), int(mo), int(d), int(h), int(mi), 0))
    else:
        day = time.gmtime(s.agent_at)
        started = calendar.timegm((day.tm_year, day.tm_mon, day.tm_mday, int(h), int(mi), 0))
    assert s.t0 // 60 * 60 <= started <= s.agent_at + 1, \
        (f"187.2: the card's start time {m.group(0)} is not when the agent started: the run began at "
         f"{time.strftime('%H:%M:%S', time.gmtime(s.t0))} UTC and the agent at {time.strftime('%H:%M:%S', time.gmtime(s.agent_at))} UTC")
    live = [text for text, url in LINK.findall(body) if url.rstrip("/") == RUN_URL and "live" in text.lower()]
    assert live, (f"187.2: the working card has no link to the run's live page ({RUN_URL}) whose words say it is live; "
                  f"its links are {LINK.findall(body)}")
    start_n = len(next(c for c in s.at_start if c["id"] == card["id"])["versions"])
    check_n = len(next(c for c in s.at_check if c["id"] == card["id"])["versions"])
    assert check_n == start_n + 1, \
        f"187.2: between the agent's start and the hand-back check the card changed {check_n - start_n - 1} times besides saying checking"
    for name, r in runs.items():
        for c in r.comments:
            for v in c["versions"]:
                assert not MINUTES.search(v.split("<details>")[0]), f"187.2 ({name}): a card counts minutes:\n{v[:400]}"


def test_no_key_is_live_while_the_agent_or_the_check_runs(record_property, runs):
    """Each key that moves the card is made for one edit and revoked before the agent starts and before the check runs.

    In a plan review: the last call made with Dokima's bot key before the agent starts revokes it, and the agent's
    environment holds no bot key. After the agent, the card is edited to checking with the bot key, and by the time
    code starts checking the hand-back the last call made with that key revoked it."""
    record_property("proves", "187.3")
    s = runs["pass"]
    before = [m for m in s.meta if not m["agent_started"] and m["token"] == "fake-token"]
    assert before and is_revoke(before[-1]["args"]), \
        f"187.3: a bot key was live when the agent started; its last call before the agent was {before[-1]['args'] if before else None}"
    leaked = sorted(k for k, v in (s.agent_env or {}).items() if "fake-token" in v and k != "GIT_CONFIG_VALUE_0")
    assert s.agent_env is not None and not leaked, f"187.3: the agent's environment holds the bot's key in {leaked}"
    assert s.check_calls is not None, f"187.3: setup: the step '{CHECK}' never ran:\n{s.tail()}"
    after = [m for m in s.meta[:s.check_calls] if m["agent_started"] and m["token"] == "fake-token"]
    assert any(is_edit(m["args"]) for m in after), \
        "187.3: no edit was made with the bot key between the agent's end and the hand-back check: the card never said checking"
    assert is_revoke(after[-1]["args"]), \
        f"187.3: the bot key was still live when code started checking the hand-back; its last call was {after[-1]['args']}"


def test_a_stage_that_cannot_be_shown_never_stops_the_run(record_property, runs):
    """When GitHub refuses every edit of the card, the run still checks the hand-back and posts its result.

    Runs a plan review with GitHub refusing every edit of a comment. The run still tried to show setting up and working
    before the agent, and checking and the record after it; the agent ran, code checked its hand-back, and Dokima's bot
    posted exactly one record: the review's passed record."""
    record_property("proves", "187.4")
    s = runs["no-edit"]
    assert s.run.agent_started(), f"187.4: the agent never started once the card could not be edited; stopped at '{s.run.failed_step}':\n{s.tail()}"
    before = [m for m in s.meta if not m["agent_started"] and is_edit(m["args"])]
    after = [m for m in s.meta if m["agent_started"] and is_edit(m["args"])]
    assert len(before) >= 2 and len(after) >= 2, \
        (f"187.4: the run tried {len(before)} edits of the card before the agent and {len(after)} after, expected at least "
         f"two each (setting up and working; checking and the record)")
    assert s.check_calls is not None, f"187.4: code never checked the hand-back once the card could not be edited:\n{s.tail()}"
    recs = [r for c in s.comments if c["author"] == agent.BOT for r in agent.records([as_comment(c["versions"][-1])])]
    assert [(r["role"], r["check"]["passed"]) for r in recs] == [("reviewer", True)], \
        f"187.4: the run's result was not posted as exactly one passed record: {[(r['role'], r['check']['passed']) for r in recs]}\n{s.tail()}"


def test_no_secret_reaches_the_card_while_the_run_moves_through_its_stages(record_property, runs):
    """Every stage the card shows passes through scrub() first, so no secret of the run ever shows on it.

    Runs a plan review whose server address (GITHUB_SERVER_URL, which the card's run link is built from, as it is
    today) holds the run's two secrets: the Claude Code token and the workflow's GitHub token. The card still goes
    queued, setting up, agent working, checking, then its record, and every one of its stage versions still links to
    the run's page (/o/r/actions/runs/42), but with each secret shown as [secret removed] and never as itself. A card
    that skips scrub() shows the secrets; a card that drops the link or the server address shows no [secret removed]."""
    record_property("proves", "187.5")
    s = runs["secret"]
    assert s.run.agent_started(), f"187.5: setup: the agent never started; stopped at '{s.run.failed_step}':\n{s.tail()}"
    card = the_card(s, "187.5")
    got = [stage_of(v) for v in card["versions"]]
    assert got == FULL, f"187.5: the card went {got}, expected {FULL}:\n" + "\n---\n".join(v[:300] for v in card["versions"])
    for v, stage in zip(card["versions"], got):
        if stage == "record":
            continue
        shown = [x for x in SECRETS if x in v]
        assert not shown, f"187.5: the card, when it said {stage}, shows the run's secrets {shown}:\n{v[:600]}"
        links = re.findall(r"\]\((https?://[^)]*/o/r/actions/runs/42[^)]*)\)", v)
        assert links and all("[secret removed]" in u for u in links), \
            (f"187.5: the card, when it said {stage}, has no link to the run built from the server address with its "
             f"secrets scrubbed (expected [secret removed] in it); its links are {re.findall(r"\]\((https?://[^)]*)\)", v)}")

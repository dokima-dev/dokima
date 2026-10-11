"""Every change on an issue or its PR redraws its card, from card.yml alone (#438).

Story 2 of #425, re-planned as one story of three criteria.

#419: the code review had passed, yet the card said Code review running for 30 minutes. card.yml picked its moments:
it skipped the bot's own edits and comments (except a code review's run card on a pull request) and redrew on a run's
start only for the full suite. The review's record is the bot's edit of its run card, so nothing redrew. Beside
card.yml, the old planner (dokima/planner.py, `post`) saved its own plan above the marker, and the plan approval
(`python3 -m dokima.agent next`, dokima/agent.py record_links) drew the cards of the issues its links touched. The
play-through (.github/workflows/playthrough.yml) ran only from the Run workflow button.

These tests play card.yml one event at a time on the fake GitHub of tests/card_player.py, run the old planner's post
and the plan approval against fakes, read .github/workflows/playthrough.yml, and run `python3 -m dokima.playthrough`
with a temp git repo standing in for a pull request. Nothing calls real GitHub.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from card_player import (BOT, OWNER, REPOSITORY, Hub, checks_finished, issue_comment, issue_event,  # noqa: E402
                         line_note, pr_comment, pr_event, review_event, sender, stale_again, worker_finished)
import card_player  # noqa: E402
from test_start import Ctx, condition, evaluate, fill, load_yaml  # noqa: E402
from dokima import agent, body  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAYTHROUGH_YML = os.path.join(ROOT, ".github", "workflows", "playthrough.yml")
N, P = 246, 260
# The activity types GitHub starts a workflow on when its `on:` names the event with no `types:`.
DEFAULT_TYPES = {"pull_request_target": ("opened", "synchronize", "reopened"),
                 "pull_request": ("opened", "synchronize", "reopened"),
                 "workflow_run": ("requested", "completed")}


# --- helpers -------------------------------------------------------------------------------------------------------

def github_starts(wf, event_name, event):
    """True when GitHub itself would start `wf` on this event, default activity types included.

    tests/card_player.py starts a workflow on any action when its `on:` lists no types; GitHub does not for
    pull_request_target and workflow_run, so this checks the types GitHub really uses."""
    if not card_player.starts(wf, event_name, event):
        return False
    t = card_player.triggers(wf)[event_name]
    types = card_player.listed(t.get("types")) if isinstance(t, dict) else []
    action = event.get("action")
    return bool(types) or event_name not in DEFAULT_TYPES or action in DEFAULT_TYPES[event_name]


def reaches_card(event_name, event):
    """True when GitHub starts card.yml on this event, itself or through a relay."""
    if github_starts(card_player.workflow(), event_name, event):
        return True
    return any(github_starts(wf, event_name, event) for _, wf in card_player.relays(event_name, event))


def run_started(n, p, workflow, state):
    """A workflow_run event: `workflow` on PR p started (in_progress) or was requested."""
    name, event = checks_finished(n, p, workflow)
    event["action"] = state
    event["workflow_run"].update(status="in_progress" if state == "in_progress" else "queued", conclusion=None)
    return name, event


def every_change(n=N, p=P):
    """Every change GitHub announces on issue n or its pull request p.

    As {what: (event name, payload)}.

    Edits, comments and labels by a person and by the bot, a run's start and its result, the pull request's own
    changes, reviews and line notes. The merge is last, so the ones before it find the pull request open."""
    live = agent.live_card("reviewer", "pr", "queued")
    return {
        "the owner opens the issue": issue_event(n, "opened"),
        "the owner edits the issue": issue_event(n, "edited"),
        "the bot edits the issue": issue_event(n, "edited", who="bot"),
        "the bot labels the issue": issue_event(n, "labeled", who="bot"),
        "the owner unlabels the issue": issue_event(n, "unlabeled"),
        "the owner closes the issue": issue_event(n, "closed"),
        "the owner reopens the issue": issue_event(n, "reopened"),
        "the owner comments on the issue": issue_comment(n),
        "the bot comments on the issue": issue_comment(n, who="bot", text="Autopilot: plan approved, starting work"),
        "the bot edits its comment on the issue": issue_comment(n, who="bot", action="edited", text="A record."),
        "the owner deletes a comment on the issue": issue_comment(n, action="deleted"),
        "the owner comments on the pull request": pr_comment(n, p),
        "the bot puts up a run card on the pull request": pr_comment(n, p, who="bot", text=live),
        "the bot posts a plain comment on the pull request": pr_comment(n, p, who="bot", text="A note from the bot."),
        "the bot edits its run card into a record on the pull request": pr_comment(n, p, who="bot", action="edited",
                                                                                   text="A record."),
        "the bot opens the pull request": pr_event(n, p, "opened"),
        "the owner edits the pull request": pr_event(n, p, "edited", who=OWNER),
        "the bot pushes a commit to the pull request": pr_event(n, p, "synchronize"),
        "the owner closes the pull request unmerged": pr_event(n, p, "closed", who=OWNER),
        "the owner reopens the pull request": pr_event(n, p, "reopened", who=OWNER),
        "the owner reviews the pull request": review_event(n, p),
        "the owner writes a note on a line": line_note(n, p),
        "the Acceptance criteria run starts": run_started(n, p, "Acceptance criteria", "in_progress"),
        "the Acceptance criteria run ends": checks_finished(n, p, "Acceptance criteria"),
        "the full suite starts": run_started(n, p, "full suite", "in_progress"),
        "the full suite ends": checks_finished(n, p, "full suite"),
        "the worker run ends": worker_finished(n),
        "the bot merges the pull request": pr_event(n, p, "closed", who="bot", merged=True),
    }


def both_redrawn(hub, n=N, p=P):
    """The cards that still hold the old card, by name; empty when both were redrawn."""
    old = "An old card, drawn before the last event."
    return [where for where, text in ((f"issue #{n}", hub.issue_body(n)), (f"PR #{p}", hub.pr_body(p))) if old in text]


def play_change(hub, what, event, k):
    """Play one change with both cards stale; card.yml's run, once it redrew both."""
    stale_again(hub)
    assert reaches_card(*event), f"{k}: card.yml does not start when {what}, so its cards keep what they showed"
    r = hub.run(*event, k)
    assert r.started and r.card_ran(), f"{k}: card.yml started when {what} but its card job did not run"
    assert not r.failed(), f"{k}: card.yml's run when {what} failed:\n{r.log[-3000:]}"
    left = both_redrawn(hub)
    assert not left, f"{k}: when {what}, card.yml left the old card on {', '.join(left)}"
    return r


# --- 438.1: every change on an issue or its pull request redraws both cards --------------------------------------

def test_every_change_on_an_issue_or_its_pull_request_redraws_both_cards(tmp_path, record_property):
    """Every change on an issue or its pull request redraws both cards.

    Proves 438.1.
    Plays card.yml on the fake GitHub for every change GitHub announces about issue #246 or its PR #260, with both
    cards stale each time: the issue opened, edited (by the owner and by the bot), labeled, closed and reopened; a
    comment posted, edited and deleted on the issue and on the pull request, the bot's included; a run card going up
    and being edited into its record; the pull request opened, edited, pushed to, closed, reopened, reviewed, noted on
    a line and merged; the Acceptance criteria and full suite runs starting and ending; the worker run ending. GitHub
    must start card.yml for each (counting only the activity types GitHub really sends), and the run must leave
    neither card old. One missed change turns it red, naming it."""
    record_property("proves", "438.1")
    hub = Hub(tmp_path)
    missed = []
    for what, event in every_change().items():
        if what == "the bot merges the pull request":
            hub.merge(N, P, by=BOT)
        try:
            play_change(hub, what, event, "438.1")
        except AssertionError as e:
            missed.append(str(e).splitlines()[0])
    assert not missed, "438.1: not every change redraws both cards:\n" + "\n".join(missed)


# --- 438.2: only card.yml writes the card ------------------------------------------------------------------------

def approval_saves_no_card(tmp_path):
    """Approving a plan saves no card; card.yml's redraw then shows its links on every card.

    Runs the plan approval (`python3 -m dokima.agent next` on an approving plan review) on the fake GitHub of
    tests/test_plan_links_recorded.py, for a plan that says #252 is blocked by #301, blocks #302 and relates to #303.
    The approval must still record the blocking links on GitHub, and must write no issue body at all. Then card.yml's
    own redraw of #252 (`python3 dokima/card.py`, as on the record's comment) must leave #252's card showing all three
    links and #301, #302 and #303 each showing its link from its own side, with every owner's ask kept."""
    import test_plan_links_recorded as tl
    hub = tl.Hub(tmp_path)
    hub.post(tl.plan(tl.links([301], [302], [303])))
    rec = tl.review("approve")
    hub.next(rec)
    saved = sorted({w["issue"] for w in hub.writes("body")})
    assert not saved, f"438.2: the plan approval saved the card of {', '.join(f'#{n}' for n in saved)} itself"
    assert hub.blocked_by(tl.N) == [301] and hub.blocked_by(302) == [tl.N], \
        f"438.2: the plan approval no longer records its blocking links: {hub.load()['deps']}"
    hub.post(rec)
    hub.redraw(tl.N)
    assert hub.card_links(tl.N) == {"blocked_by": {301}, "blocks": {302}, "relates_to": {303}}, \
        f"438.2: after card.yml's redraw, #{tl.N}'s card does not show its links: {hub.card_links(tl.N)}"
    expected = {301: {"blocked_by": set(), "blocks": {tl.N}, "relates_to": set()},
                302: {"blocked_by": {tl.N}, "blocks": set(), "relates_to": set()},
                303: {"blocked_by": set(), "blocks": set(), "relates_to": {tl.N}}}
    for n, want in expected.items():
        assert hub.card_links(n) == want, \
            f"438.2: after card.yml's redraw of #{tl.N}, #{n}'s card should show {want}, shows {hub.card_links(n)}"
        assert body.ask(hub.body(n)) == hub.asks[n], f"438.2: the owner's ask on #{n} changed"


def planner_saves_no_card(monkeypatch, tmp_path):
    """The planner saves no card of its own; it still says it planned.

    Runs the old planner's post (`dokima/planner.py`, as planner.yml does) for a good plan on an issue that already
    has a card, against tests/test_body.py's fake GitHub. It must save no issue body, and must still finish without
    error and post its comment on the issue, so the post did run."""
    import test_body as tb
    from dokima import card, planner
    fake = tb.FakeGitHub()
    monkeypatch.setenv("REPO", tb.REPO)
    monkeypatch.setattr(body, "gh", fake)
    monkeypatch.setattr(card, "gh", fake)
    monkeypatch.setattr(planner, "gh", fake)
    current = body.redraw("My ask.", tb.PLAN_TOP)
    raised = tb.run_planner_post(monkeypatch, tmp_path, fake, current)
    assert raised is None, f"438.2: the planner's post failed on a good plan: {raised!r}"
    assert fake.saves == [], f"438.2: the planner saved a card of its own above the marker: {fake.saves[0][:300]!r}"
    assert fake.comments, "438.2: the planner's post said nothing on the issue, so it did not run"


def test_only_card_yml_writes_the_card(tmp_path, monkeypatch, record_property):
    """Neither the planner nor the plan approval saves a card; card.yml shows their links.

    Proves 438.2.
    Runs the plan approval (`python3 -m dokima.agent next` on an approving plan review) on the fake GitHub of
    tests/test_plan_links_recorded.py, for a plan that says #252 is blocked by #301, blocks #302 and relates to #303:
    it must still record the blocking links and write no issue body, and card.yml's own redraw of #252 must then show
    all three links on every card involved. Then runs the old planner's post (`dokima/planner.py`, as planner.yml
    does) for a good plan against tests/test_body.py's fake GitHub: it must save no issue body and still post its
    comment, so the post did run."""
    record_property("proves", "438.2")
    approval_saves_no_card(tmp_path / "approval")
    (tmp_path / "planner").mkdir()
    planner_saves_no_card(monkeypatch, tmp_path / "planner")


# --- 438.3: the play-through runs by itself on a pull request changing card, board or workflow code -----------------

def playthrough_yml(k):
    """playthrough.yml as nested dicts; fails naming criterion k when it is missing."""
    assert os.path.exists(PLAYTHROUGH_YML), f"{k}: .github/workflows/playthrough.yml does not exist"
    return load_yaml(open(PLAYTHROUGH_YML).read())


def pr_target_event(action="opened"):
    """A pull_request_target event for PR #7, head headsha7, base basesha7."""
    pr = {"number": 7, "title": "A change", "state": "open", "merged": False,
          "head": {"ref": "try/issue-6", "sha": "headsha7", "repo": {"full_name": "o/r"}}, "base": {"ref": "main", "sha": "basesha7"},
          "user": {"login": BOT + "[bot]", "type": "Bot"}}
    return "pull_request_target", {"action": action, "number": 7, "pull_request": pr, "sender": sender("bot"),
                                   "repository": dict(REPOSITORY, full_name="dokima-dev/dokima")}


def ctx_for(event_name, event):
    """The expression context GitHub gives playthrough.yml for one event."""
    g = card_player.github_ctx(event_name, event)
    inputs = card_player.wrap(event.get("inputs") or {})
    return {"github": g, "vars": Ctx(), "secrets": Ctx(), "inputs": inputs, "env": Ctx(), "needs": Ctx(),
            "steps": Ctx(), "job": Ctx(status="success"), "matrix": Ctx()}


def jobs_for(wf, event_name, event, k):
    """The jobs of `wf` GitHub runs for this event, as [(check name, job)].

    Fails naming k when the workflow never starts on it."""
    assert github_starts(wf, event_name, event), \
        f"{k}: playthrough.yml does not start on {event_name} {event.get('action') or ''}".rstrip()
    ctx, out = ctx_for(event_name, event), []
    for key, job in (wf.get("jobs") or {}).items():
        if card_player.listed(job.get("needs")):
            continue
        if evaluate(condition(job.get("if")), ctx, {"failed": False}):
            out.append((fill(job.get("name") or key, ctx, {"failed": False}), job))
    return out


def play_step(job, ctx):
    """The step of `job` running the play-through, with its env filled in."""
    for step in job.get("steps") or []:
        if "dokima.playthrough" in str(step.get("run") or ""):
            env = {**(job.get("env") or {}), **(step.get("env") or {})}
            return step, {k: fill(v, ctx, {"failed": False}) for k, v in env.items()}
    raise AssertionError("no step runs python3 -m dokima.playthrough")


def played_checkout(job, ctx):
    """The checkout of the played commit (path `played`): its ref and fetch-depth, filled in."""
    for step in job.get("steps") or []:
        w = step.get("with") or {}
        if "actions/checkout" in str(step.get("uses") or "") and str(w.get("path") or "") == "played":
            return fill(w.get("ref") or "", ctx, {"failed": False}), fill(w.get("fetch-depth") or "1", ctx, {"failed": False})
    raise AssertionError("no checkout has path `played`")


def git(cwd, *args):
    """Run git in `cwd` as a test user; its output."""
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def pull_request(tmp_path, files):
    """A temp git repo standing in for a pull request that changes `files`.

    Returns (folder, base sha, head sha)."""
    repo = tmp_path / "played"
    (repo / "dokima").mkdir(parents=True)
    (repo / "dokima" / "__init__.py").write_text("")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD")
    for f in files:
        path = repo / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"changed {f}\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "head")
    return str(repo), base, git(repo, "rev-parse", "HEAD")


def run_module(tmp_path, played, base, head):
    """Run the play-through module for a pull request, with no sandbox key.

    Returns (exit code, output, gh calls).

    gh is a stub that logs and fails, so a play that reaches GitHub shows in the calls."""
    stub = tmp_path / "bin"
    stub.mkdir(exist_ok=True)
    log = tmp_path / "gh-calls.txt"
    (stub / "gh").write_text(f"#!/bin/sh\necho \"$@\" >> {log}\nexit 1\n")
    (stub / "gh").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("SANDBOX_TOKEN", "PLAYTHROUGH_WAIT")}
    env.update(PATH=f"{stub}{os.pathsep}{os.environ['PATH']}", REPO="dokima-dev/card-gallery", PLAYED=played,
               PLAYED_COMMIT=head, PLAYED_BASE=base, GH_TOKEN="fake", PYTHONPATH=ROOT)
    p = subprocess.run([sys.executable, "-m", "dokima.playthrough"], cwd=ROOT, env=env, capture_output=True,
                       text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr, log.read_text() if log.exists() else ""


CARD_CODE = [".github/workflows/card.yml", ".github/workflows/board.yml", "dokima/card.py", "dokima/body.py",
             "dokima/board.py"]
OTHER_CODE = ["README.md", "dokima/agent.py", "dokima/cards.py", "tests/test_card.py", "tests/test_board.py",
              ".github/CODEOWNERS", "docs/dokima/card.py"]


CARD_CODE = [".github/workflows/card.yml", ".github/workflows/board.yml", "dokima/card.py", "dokima/body.py",
             "dokima/board.py"]


def glob_matches(pattern, path):
    """True when GitHub's `paths` glob `pattern` matches `path` (`**` crosses folders, `*` does not)."""
    rx = re.escape(pattern).replace(r"\*\*", "\0").replace(r"\*", "[^/]*").replace("\0", ".*")
    return re.fullmatch(rx, path) is not None


def test_a_pull_request_changing_card_board_or_workflow_code_runs_the_play_through_by_itself(tmp_path, record_property):
    """A pull request changing card, board or workflow code plays itself on its head.

    Proves 438.3.
    Reads .github/workflows/playthrough.yml with the workflow evaluator of tests/test_start.py. A pull request
    opened, pushed to or reopened (pull_request_target, so main's copy judges it) must start it with no button, and
    when its trigger lists `paths`, every card, board and workflow file must match one. On the pull request it runs
    one job, which checks out the pull request's head commit as `played` and runs `python3 -m dokima.playthrough` with
    PLAYED_COMMIT set to that head. Then, for a temp git repo standing in for a pull request that changes each of
    .github/workflows/card.yml, .github/workflows/board.yml, dokima/card.py, dokima/body.py and dokima/board.py, the
    module run as that job runs it must try to play: with no sandbox key it fails at install, exit 1."""
    record_property("proves", "438.3")
    wf = playthrough_yml("438.3")
    for action in ("opened", "synchronize", "reopened"):
        found = jobs_for(wf, *pr_target_event(action), "438.3")
        assert len(found) == 1, f"438.3: a pull request {action} runs {len(found)} play-through jobs, not one"
    t = card_player.triggers(wf)["pull_request_target"]
    paths = card_player.listed(t.get("paths")) if isinstance(t, dict) else []
    for f in CARD_CODE if paths else []:
        assert any(glob_matches(g, f) for g in paths), \
            f"438.3: a pull request changing {f} does not start the play-through: its paths are {paths}"
    _, job = jobs_for(wf, *pr_target_event(), "438.3")[0]
    ctx = ctx_for(*pr_target_event())
    ref = played_checkout(job, ctx)[0]
    assert ref == "headsha7", f"438.3: on a pull request the play-through plays {ref!r}, not its head commit headsha7"
    _, env = play_step(job, ctx)
    assert env.get("PLAYED_COMMIT") == "headsha7", \
        f"438.3: on a pull request PLAYED_COMMIT is {env.get('PLAYED_COMMIT')!r}, not its head commit headsha7"
    for k, f in enumerate(CARD_CODE):
        played, base, head = pull_request(tmp_path / f"card{k}", ["README.md", f])
        code, out, _ = run_module(tmp_path / f"card{k}", played, base, head)
        assert code == 1 and "FAIL: install" in out and "without playing" not in out, \
            f"438.3: a pull request changing {f} should be played (and fail at install with no key); it exited {code}: {out[-500:]}"


def test_a_pull_request_from_another_copy_of_the_repo_runs_no_play_through():
    """A pull request from someone's own copy of the repo runs no play-through job, so it never opens the keys (#503).

    The same pull request from a branch of this repo runs one."""
    wf = playthrough_yml("#503")
    name, event = pr_target_event()
    event["pull_request"]["head"]["repo"] = {"full_name": "stranger/r"}
    assert jobs_for(wf, name, event, "#503") == [], "#503: a pull request from a stranger's copy runs the play-through"
    assert len(jobs_for(wf, *pr_target_event(), "#503")) == 1, "#503: a pull request from this repo runs no play-through"

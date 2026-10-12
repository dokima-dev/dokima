"""The board updates only when a card can move, once per burst (#533, from #380).

GitHub's GraphQL budget (5,000 calls an hour, shared by every Dokima workflow) ran out on 2026-10-09, and board.yml
alone used about 56% of it: it recomputed an issue's cards on every comment, line note, new commit and finished
check, though none of those can move a card. These tests hold the fix to the owner's words on #380:

- `python3 -m dokima.board queue`, the step that already names each event's board queue from its payload alone,
  also writes `run=true` or `run=false` to GITHUB_OUTPUT: false exactly for an event that cannot change a card's
  column or pill, true for every other one (and for any event it cannot read). board.yml's sync job runs only on
  true, so a skipped event spends no GraphQL call at all.
- A review or line note reaches board.yml only as reviews.yml's run completing, which carries no summary, so the
  step reads it from the run's event and name: reviews.yml names its run from the review (`run-name:`), and a run
  named any other way (a pull request whose own reviews.yml is older) still runs the update.
- Events about one issue that arrive within a minute become one update: board.yml waits one minute in a queue of
  the issue's own that a newer event cancels, and only then syncs. A wait cancelled that way is no failed check, so
  autopilot still merges a green pull request (as it already ignores superseded card runs, #528).
- The 15-minute sweep stays, so a card a skipped event could have put right is put right there.

board.yml is played with tests/test_start.py's reader and evaluator: each job's `if:`, outputs and concurrency group
are evaluated the way GitHub evaluates them, with the queue step's real outputs. The board itself runs against
tests/test_needs_you.py's in-memory world, as tests/test_board_state.py does.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import test_board_state as tbs  # noqa: E402
import test_needs_you as tny  # noqa: E402
from test_agent import GOOD_WORK, rec  # noqa: E402
from test_start import Ctx, condition, evaluate, fill, load_yaml  # noqa: E402
from dokima import agent, board, body, plan  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BOARD_YML = os.path.join(ROOT, ".github", "workflows", "board.yml")
REVIEWS_YML = os.path.join(ROOT, ".github", "workflows", "reviews.yml")
PR_TITLE = "The board is updated only when it can change"
SPEC, REPO, OWNER, LABEL = tny.SPEC, tny.REPO, tny.OWNER, tny.LABEL
NEEDS = tny.NEEDS
BOT_LOGIN = f"{agent.BOT}[bot]"
STRANGER = "someone-else" if OWNER != "someone-else" else "another-person"
ASK = "The board is updated only when it can change.\n\n- Bursts become one update.\n"


# --- payloads, as GitHub sends them -------------------------------------------------------------------------------

def issue_payload(n, action, labels=(), state="open", issue_body=ASK, **extra):
    """An `issues` event on issue n."""
    return {"action": action, "issue": {"number": n, "state": state, "body": issue_body,
                                        "labels": [{"name": x} for x in labels]}, **extra}


def labeled(n, action, name):
    """An `issues` labeled or unlabeled event for one label."""
    return issue_payload(n, action, labels=[name] if action == "labeled" else [], label={"name": name})


def comment_on_issue(n, words, login=OWNER, kind="User"):
    """A comment created on issue n."""
    return {"action": "created", "issue": {"number": n, "state": "open", "body": ASK, "labels": []},
            "comment": {"body": words, "user": {"login": login, "type": kind}}}


def comment_on_pr(pr, issue, words, login=OWNER, kind="User"):
    """A comment created on pull request `pr`, built for `issue`."""
    return {"action": "created", "issue": {"number": pr, "state": "open", "body": f"Closes #{issue}", "labels": [],
                                           "pull_request": {"url": f"https://api.github.com/repos/o/r/pulls/{pr}"}},
            "comment": {"body": words, "user": {"login": login, "type": kind}}}


def pr_payload(pr, issue, merged=False, state="open"):
    """A pull request as event payloads carry it, built for `issue` from its try branch."""
    return {"number": pr, "title": PR_TITLE, "state": state, "merged": merged, "body": f"Closes #{issue}", "labels": [],
            "head": {"ref": f"try/issue-{issue}"}}


def pr_event(action, pr, issue, merged=False):
    """A `pull_request_target` event."""
    return {"action": action, "pull_request": pr_payload(pr, issue, merged, "closed" if action == "closed" else "open")}


def reviews_run(gh_event, pr, issue, title):
    """reviews.yml's run for a review or line note on `pr`, named `title`."""
    return ("workflow_run", {"action": "completed", "workflow_run": {
        "name": "reviews", "path": ".github/workflows/reviews.yml", "event": gh_event, "display_title": title, "status": "completed", "conclusion": "success",
        "pull_requests": [{"number": pr, "head": {"ref": f"try/issue-{issue}"}}]}})


def through_reviews(gh_event, payload):
    """What board.yml receives for a review or line note, named as GitHub names it.

    A review or line note reaches board.yml only as reviews.yml's run completing (#418), which carries no summary.
    The run's name is reviews.yml's `run-name:`, filled in from the review event the way GitHub fills it, or the pull
    request's title when reviews.yml names no run (or, on a branch from before #418, does not exist)."""
    name = load_yaml(open(REVIEWS_YML).read()).get("run-name") if os.path.exists(REVIEWS_YML) else None
    ctx = Ctx({"github": Ctx({"event_name": gh_event, "event": payload, "repository": REPO})})
    title = fill(name, ctx, {"failed": False}) if name else payload["pull_request"]["title"]
    pr = payload["pull_request"]
    return reviews_run(gh_event, pr["number"], int(pr["head"]["ref"].rsplit("-", 1)[1]), title)


def review(pr, issue, state, words, login=OWNER, kind="User"):
    """A pull request review submitted with this state and summary, as it reaches board.yml."""
    return through_reviews("pull_request_review", {"action": "submitted", "pull_request": pr_payload(pr, issue),
                                                   "review": {"state": state, "body": words, "user": {"login": login, "type": kind}}})


def line_note(pr, issue, words):
    """A line note created on the pull request's diff, as it reaches board.yml."""
    return through_reviews("pull_request_review_comment", {
        "action": "created", "pull_request": pr_payload(pr, issue),
        "comment": {"body": words, "path": "dokima/board.py", "line": 3, "user": {"login": OWNER, "type": "User"}}})


def checks(pr, issue, conclusion):
    """The Acceptance criteria checks finishing on the pull request."""
    return {"action": "completed", "workflow_run": {"name": "Acceptance criteria", "path": ".github/workflows/acceptance-criteria.yml",
                                                    "event": "pull_request", "conclusion": conclusion, "pull_requests": [
        {"number": pr, "head": {"ref": f"try/issue-{issue}"}}]}}


def record_text(r):
    """A record comment's body, as code posts it."""
    return f"The run is done.\n\n{agent.MARK}\n<details><summary>Record</summary>\n\n```json\n{json.dumps(r)}\n```\n</details>"


def live_card(role="Worker"):
    """A run card the bot puts up when a run is queued."""
    return f"{agent.LIVE}\n**{role}** · queued\n\nThe machine is setting up."


def card_edit(n):
    """The bot redraws the card above the marker: the owner's ask below it is unchanged."""
    old = body.redraw(ASK, "<!-- dokima-card -->\nPlan\n<!-- /dokima-card -->")
    new = body.redraw(old, "<!-- dokima-card -->\nWork\n<!-- /dokima-card -->")
    return issue_payload(n, "edited", issue_body=new, changes={"body": {"from": old}})


def first_card(n):
    """The first card drawn on a fresh ask, keeping the whole ask below it."""
    return issue_payload(n, "edited", issue_body=body.redraw(ASK, "<!-- dokima-card -->\nBacklog\n<!-- /dokima-card -->"),
                         changes={"body": {"from": ASK}})


def ask_edit(n):
    """A person changes the owner's ask below the marker."""
    old = body.redraw(ASK, "<!-- dokima-card -->\nPlan\n<!-- /dokima-card -->")
    new = old.split(body.MARKER, 1)[0] + body.MARKER + "\n\n" + ASK + "\nAlso the cards.\n"
    return issue_payload(n, "edited", issue_body=new, changes={"body": {"from": old}})


SCHEDULE = ("schedule", {"schedule": "*/15 * * * *"})


def skipped_events(n=57, pr=60):
    """Every event about issue n or its PR that cannot move a card."""
    return {
        "a stranger's comment on the issue": ("issue_comment", comment_on_issue(n, "Looks right to me.", STRANGER)),
        "the code owner's comment that is no command": ("issue_comment", comment_on_issue(n, "Thanks, I'll look tomorrow.")),
        "the code owner's comment naming a command later in it": ("issue_comment", comment_on_issue(n, "Should I say /work now?")),
        "a comment on the pull request": ("issue_comment", comment_on_pr(pr, n, "A note on the diff.", STRANGER)),
        "a bot comment that is no record, run card or Autopilot line": (
            "issue_comment", comment_on_issue(n, "**Issue text not updated:** the owner's part would change.", BOT_LOGIN, "Bot")),
        "a line note": line_note(pr, n, "Rename this."),
        "a review that only comments": review(pr, n, "commented", "Nice."),
        "an Approve with no summary": review(pr, n, "approved", ""),
        "an Approve with a summary that is no command": review(pr, n, "approved", "Looks good."),
        "new commits on the pull request": ("pull_request_target", pr_event("synchronize", pr, n)),
        "the Acceptance criteria checks passing": ("workflow_run", checks(pr, n, "success")),
        "the Acceptance criteria checks failing": ("workflow_run", checks(pr, n, "failure")),
        "the label bug added": ("issues", labeled(n, "labeled", "bug")),
        "the label bug removed": ("issues", labeled(n, "unlabeled", "bug")),
        "the card redrawn above the marker": ("issues", card_edit(n)),
        "the first card drawn on a fresh ask": ("issues", first_card(n)),
        "the title edited": ("issues", issue_payload(n, "edited", changes={"title": {"from": "An older title"}})),
    }


def run_events(n=57, pr=60):
    """Every event about issue n or its PR that can move a card."""
    worker = rec("worker", handback=GOOD_WORK)
    out = {
        "the issue opened": ("issues", issue_payload(n, "opened")),
        "the issue closed": ("issues", issue_payload(n, "closed", state="closed")),
        "the issue reopened": ("issues", issue_payload(n, "reopened")),
        "the owner's ask edited below the marker": ("issues", ask_edit(n)),
        "an edit GitHub sends with no changes": ("issues", issue_payload(n, "edited")),
        "/plan on the issue": ("issue_comment", comment_on_issue(n, "/plan Go on with the planner's reading.")),
        "/work on the issue": ("issue_comment", comment_on_issue(n, "/work")),
        "/review on the issue": ("issue_comment", comment_on_issue(n, "/review")),
        "/autopilot start on the issue": ("issue_comment", comment_on_issue(n, "/autopilot start")),
        "/autopilot stop on the issue": ("issue_comment", comment_on_issue(n, "/autopilot stop")),
        "/review on the pull request": ("issue_comment", comment_on_pr(pr, n, "/review Look again.")),
        "a record the bot posts on the issue": ("issue_comment", comment_on_issue(n, record_text(worker), BOT_LOGIN, "Bot")),
        "a record the bot posts on the pull request": ("issue_comment", comment_on_pr(pr, n, record_text(worker), BOT_LOGIN, "Bot")),
        "a run card the bot puts up": ("issue_comment", comment_on_issue(n, live_card(), BOT_LOGIN, "Bot")),
        "a review asking for changes with /work": review(pr, n, "changes_requested", "/work Fix the name."),
        "a review the bot submits with its record": review(pr, n, "commented", record_text(worker), BOT_LOGIN, "Bot"),
        "the pull request opened": ("pull_request_target", pr_event("opened", pr, n)),
        "the pull request reopened": ("pull_request_target", pr_event("reopened", pr, n)),
        "the pull request merged": ("pull_request_target", pr_event("closed", pr, n, merged=True)),
        "the pull request closed unmerged": ("pull_request_target", pr_event("closed", pr, n)),
        "an event the board does not know": ("workflow_dispatch", {"inputs": {}}),
        "the 15-minute sweep": SCHEDULE,
    }
    for name in (LABEL,):
        out[f"the label {name} added"] = ("issues", labeled(n, "labeled", name))
        out[f"the label {name} removed"] = ("issues", labeled(n, "unlabeled", name))
    lines = (*agent.AUTOPILOT_LINES.values(), agent.AUTOPILOT_LINE, agent.AUTOPILOT_START_LINE,
             *(line.format(pr=pr) for line in agent.AUTOPILOT_MERGE.values()))
    for line in lines:
        out[f"the bot's line {line!r}"] = ("issue_comment", comment_on_issue(n, line, BOT_LOGIN, "Bot"))
    return out


# --- the queue step, run as board.yml runs it ---------------------------------------------------------------------

def queue_outputs(event, payload, monkeypatch, tmp_path, k):
    """What the queue step writes to GITHUB_OUTPUT for this event, as {key: value}."""
    d = tmp_path / f"q{len(list(tmp_path.glob('q*')))}"
    d.mkdir()
    (d / "event.json").write_text(json.dumps(payload))
    (d / "output.txt").write_text("")
    for key, value in (("GITHUB_EVENT_NAME", event), ("GITHUB_EVENT_PATH", str(d / "event.json")),
                       ("GITHUB_OUTPUT", str(d / "output.txt")), ("GITHUB_RUN_ID", "4242"), ("GITHUB_REPOSITORY", REPO)):
        monkeypatch.setenv(key, value)
    code = board.main(["board", "queue"])
    assert code == 0, f"{k}: `python3 -m dokima.board queue` exited {code} on a {event} event"
    return dict(line.split("=", 1) for line in (d / "output.txt").read_text().splitlines() if "=" in line)


def runs(event, payload, monkeypatch, tmp_path, k):
    """True when the queue step writes run=true for this event, False for run=false."""
    out = queue_outputs(event, payload, monkeypatch, tmp_path, k)
    assert out.get("run") in ("true", "false"), \
        f"{k}: the queue step wrote {out} to GITHUB_OUTPUT on a {event} event, with no run=true or run=false"
    return out["run"] == "true"


# --- board.yml, played as GitHub plays it --------------------------------------------------------------------------

def jobs_of():
    """board.yml's jobs, read."""
    return load_yaml(open(BOARD_YML).read())["jobs"]


def runs_text(job):
    """Every `run:` script of a job, joined."""
    return "\n".join(str(s.get("run", "")) for s in job.get("steps") or [] if isinstance(s, dict))


def needs_of(job):
    n = job.get("needs") or []
    return [n] if isinstance(n, str) else list(n)


def queue_job(jobs):
    found = [j for j, b in jobs.items() if "python3 -m dokima.board queue" in runs_text(b)]
    assert found, "test setup: no job in board.yml runs `python3 -m dokima.board queue`"
    return found[0]


def sync_job(jobs):
    found = [j for j, b in jobs.items() if re.search(r"(?m)^\s*python3 -m dokima\.board\s*$", runs_text(b))]
    assert found, "test setup: no job in board.yml runs `python3 -m dokima.board`"
    return found[0]


def upstream(jobs, name):
    """Every job `name` needs, directly or through others."""
    seen, todo = set(), needs_of(jobs[name])
    while todo:
        j = todo.pop()
        if j not in seen and j in jobs:
            seen.add(j)
            todo += needs_of(jobs[j])
    return seen


def play(event, payload, monkeypatch, tmp_path, k, results=None):
    """Play board.yml's jobs for one event: {job: {"ran", "group", "cancels"}}.

    The queue job's step outputs are the real queue step's for this event. A job runs when its `if:` (with GitHub's
    implied success()) holds over its needs; `results` forces a job's result (for example "cancelled", as when a
    newer event cancels it), and a job that does not run is "skipped". Each job's concurrency group and
    cancel-in-progress are filled in whether it runs or not."""
    jobs, results = jobs_of(), dict(results or {})
    q = queue_job(jobs)
    step_out = queue_outputs(event, payload, monkeypatch, tmp_path, k)
    step_ids = [s["id"] for s in jobs[q].get("steps") or [] if isinstance(s, dict) and s.get("id")]
    base = {"github": {"event_name": event, "event": payload, "run_id": "4242", "repository": REPO},
            "vars": {"DOKIMA_BOARD": SPEC, "DOKIMA_APP_ID": "1"}, "secrets": {"DOKIMA_APP_KEY": "k"}, "env": {}, "inputs": {}}
    done, outputs, got = {}, {}, {}
    while len(done) < len(jobs):
        ready = [j for j in jobs if j not in done and all(n in done for n in needs_of(jobs[j]))]
        assert ready, "test setup: board.yml's jobs need each other in a loop"
        for j in ready:
            job = jobs[j]
            ctx = Ctx({key: Ctx(v) for key, v in {**base, "needs": {n: {"result": done[n], "outputs": outputs.get(n, {})} for n in needs_of(job)},
                       "steps": {sid: {"outputs": step_out} for sid in step_ids} if j == q else {}}.items()})
            status = {"failed": any(done[n] == "failure" for n in needs_of(job)),
                      "cancelled": any(done[n] == "cancelled" for n in needs_of(job)),
                      "success": all(done[n] == "success" for n in needs_of(job))}
            cond = re.sub(r"^\$\{\{(.*)\}\}$", r"\1", str(job.get("if") or "").strip())
            ran = bool(evaluate(condition(cond), ctx, status))
            done[j] = results.get(j, "success") if ran else "skipped"
            outputs[j] = {key: fill(v, ctx, status) for key, v in (job.get("outputs") or {}).items()} if ran else {}
            conc = job.get("concurrency")
            group = fill(conc.get("group"), ctx, status) if isinstance(conc, dict) else (fill(conc, ctx, status) if conc else None)
            cancels = isinstance(conc, dict) and fill(str(conc.get("cancel-in-progress", "false")), ctx, status).strip() == "true"
            got[j] = {"ran": ran, "group": group, "cancels": cancels}
    return got


def settle_job(jobs):
    """The job the sync waits on that sleeps in a cancelling queue, or None."""
    s = sync_job(jobs)
    for j in sorted(upstream(jobs, s) - {queue_job(jobs)}):
        conc = jobs[j].get("concurrency")
        if isinstance(conc, dict) and str(conc.get("cancel-in-progress", "")).strip() not in ("", "false") \
                and re.search(r"\bsleep\s+\d+", runs_text(jobs[j])):
            return j
    return None


# --- the board's in-memory world ------------------------------------------------------------------------------------

@pytest.fixture
def make(monkeypatch):
    """Wire a world into dokima.board.Board and dokima.agent.gh, and return it (as tests/test_board_state.py does)."""

    def wire(**kw):
        world = tny.World(**kw)
        monkeypatch.setattr(board, "Board", tbs.fake_board(world))
        monkeypatch.setattr(agent, "gh", tny.fake_gh(world))
        return world

    return wire


def settle(w, n=57):
    """Put issue n's cards where its state says now, the way any board update does."""
    board.rebuild(board.Board(SPEC, REPO), REPO, plan.repo_approvers("o"), n)


# =================================================================================================================
# 533.1: an event that cannot change a card's column or pill no longer starts a board update

def test_an_event_that_cannot_move_a_card_no_longer_starts_a_board_update(record_property, monkeypatch, tmp_path):
    """Comments, line notes, new commits, finished checks and other labels start no board update.

    Plays board.yml, its jobs' `if:` evaluated as GitHub does with the queue step's real outputs, on each event about
    #57 or its PR #60 that cannot change a column or pill: a stranger's comment, the code owner's comment with no
    command, a comment on the PR, a bot comment that is no record, run card or Autopilot line, a line note, a review
    that only comments, an Approve with or without words, new commits, the Acceptance criteria checks passing or
    failing, the label bug added or removed, the card redrawn above the marker, the first card on a fresh ask and a
    title edit. On none of them may the job running `python3 -m dokima.board` run. Beside them, on every event that
    can move a card (the issue opened, closed or reopened, the owner's ask edited, each command, a record, a run card,
    each Autopilot line, a review with /work or the bot's record, the PR opened, reopened, merged or closed, the
    autopilot label, the sweep), and on events the queue step cannot read, it must still run. Proves 533.1."""
    record_property("proves", "533.1")
    jobs = jobs_of()
    s = sync_job(jobs)
    wrong_run = [w for w, (e, p) in skipped_events().items() if play(e, p, monkeypatch, tmp_path, "533.1")[s]["ran"]]
    assert not wrong_run, f"533.1: these events cannot change a card's column or pill, yet board.yml still updates the board: {wrong_run}"
    odd = {"a comment event with no comment": ("issue_comment", {"action": "created", "issue": {"number": 57}}),
           "a review whose run is named by the pull request's title": reviews_run("pull_request_review", 60, 57, PR_TITLE),
           "a reviews run that names no event": ("workflow_run", {"action": "completed", "workflow_run": {
               "name": "reviews", "path": ".github/workflows/reviews.yml",
               "pull_requests": [{"number": 60, "head": {"ref": "try/issue-57"}}]}}),
           "an edit with no changes field": ("issues", {"action": "edited", "issue": {"number": 57, "labels": []}}),
           "a label event with no label": ("issues", {"action": "labeled", "issue": {"number": 57, "labels": []}})}
    wrong_skip = [w for w, (e, p) in {**run_events(), **odd}.items() if not play(e, p, monkeypatch, tmp_path, "533.1")[s]["ran"]]
    assert not wrong_skip, f"533.1: these events can change a card (or could not be read), yet board.yml no longer updates the board: {wrong_skip}"


# =================================================================================================================
# 533.2: events about one issue or its pull request within one minute cause one board update

def checks_on_head(monkeypatch, runs):
    """Answer autopilot's reads of a head's checks with these check runs and no commit statuses."""
    def gh(*args, **kw):
        joined = " ".join(str(a) for a in args)
        if "check-runs" in joined:
            return json.dumps({"total_count": len(runs), "check_runs": runs})
        if "/status" in joined:
            return json.dumps({"state": "success", "statuses": []})
        raise AssertionError(f"test setup: unexpected gh call: gh {joined}")
    monkeypatch.setattr(agent, "gh", gh)


def test_events_about_one_issue_within_a_minute_cause_one_board_update(record_property, monkeypatch, tmp_path):
    """Events about one issue or its pull request within a minute cause one board update.

    Plays a burst as GitHub runs it: /plan on #57, the planner's record on #57, PR #60 opened and a /work review on
    PR #60, each a second or so apart. board.yml must have a job the sync waits on that sleeps one minute (`sleep 60`)
    in a concurrency group that cancels the one waiting before it. Each event's wait takes the same group; that group
    is never the sync job's own, so a newer event cancels only a waiting update, never a running one. Played with its
    wait cancelled by the next event, an update never syncs; the last one, left to wait, does: one update for the burst.
    An event about #58 waits in another group, so it never cancels #57's update; a skipped event about #57 (a comment,
    new commits, finished checks) waits in no group #57's update waits in, so the record a second before it still
    lands. A wait cancelled this way shows on the pull request as a cancelled check: autopilot, reading the head's
    checks, must not count it against an otherwise green pull request. Proves 533.2."""
    record_property("proves", "533.2")
    jobs = jobs_of()
    j, s = settle_job(jobs), sync_job(jobs)
    assert j, "533.2: board.yml has no job the sync waits on that sleeps in a queue a newer event cancels, so every event is its own update"
    sleeps = [int(x) for x in re.findall(r"\bsleep\s+(\d+)", runs_text(jobs[j]))]
    assert sleeps == [60], f"533.2: the {j!r} job waits {sleeps} seconds, not one minute (sleep 60)"
    worker = rec("worker", handback=GOOD_WORK)
    burst = [("issue_comment", comment_on_issue(57, "/plan Again.")),
             ("issue_comment", comment_on_issue(57, record_text(worker), BOT_LOGIN, "Bot")),
             ("pull_request_target", pr_event("opened", 60, 57)),
             review(60, 57, "changes_requested", "/work")]
    waiting, syncs = set(), 0
    for i, (e, p) in enumerate(burst):
        last = i == len(burst) - 1
        got = play(e, p, monkeypatch, tmp_path, "533.2", results={} if last else {j: "cancelled"})
        assert got[j]["ran"] and got[j]["cancels"], f"533.2: event {i + 1} of the burst about #57 does not wait in a queue a newer event cancels"
        assert got[j]["group"] and got[j]["group"] != got[s]["group"], \
            f"533.2: the waiting queue {got[j]['group']!r} is the sync job's own, so a newer event could cancel a running update"
        waiting.add(got[j]["group"])
        syncs += got[s]["ran"]
    assert len(waiting) == 1, f"533.2: events about #57 and its PR #60 wait in different queues, so they do not cancel each other: {waiting}"
    assert syncs == 1, f"533.2: a burst of {len(burst)} events about #57 within a minute caused {syncs} board updates, not one"
    other = play("issue_comment", comment_on_issue(58, "/work"), monkeypatch, tmp_path, "533.2")[j]["group"]
    assert other not in waiting, f"533.2: #58 waits in #57's queue {other!r}, so one issue's event would cancel another's update"
    bad = [w for w, (e, p) in skipped_events().items()
           if (got := play(e, p, monkeypatch, tmp_path, "533.2")[j])["ran"] and got["group"] in waiting]
    assert not bad, f"533.2: these skipped events take #57's waiting queue and would cancel its update: {bad}"
    name = str(jobs[j].get("name") or j)
    green = [{"name": n, "status": "completed", "conclusion": "success"} for n in ("All tests", "Acceptance criteria")]
    checks_on_head(monkeypatch, green + [{"name": name, "status": "completed", "conclusion": "cancelled"}])
    why = agent.unproven(REPO, "a1" * 20, wait=0, pause=0)
    assert why is None, f"533.2: a board wait cancelled by a newer event keeps autopilot from merging a green pull request: {why}"
    checks_on_head(monkeypatch, green + [{"name": "All tests", "status": "completed", "conclusion": "cancelled"}])
    assert agent.unproven(REPO, "a1" * 20, wait=0, pause=0), "533.2: test setup: a cancelled All tests no longer stops autopilot"


# =================================================================================================================
# 533.3: the 15-minute sweep still puts right any card a skipped event left in the wrong column

def test_the_15_minute_sweep_still_puts_right_a_card_a_skipped_event_left_wrong(record_property, make, monkeypatch, tmp_path):
    """The 15-minute sweep still puts right a card a skipped event left wrong.

    board.yml must still be scheduled every 15 minutes and, played for the schedule, still run the job running
    `python3 -m dokima.board`. Then: #57's code review approved, so its card and PR #60's belong in Review with Needs
    you, but both sit in Work with no pill. A stranger's comment on #57 arrives and board.yml skips it. The next sweep,
    with #57 updated since the last good sweep, must put both cards in Review with Needs you. Proves 533.3."""
    record_property("proves", "533.3")
    text = open(BOARD_YML).read()
    assert re.search(r"cron:\s*[\"']\*/15 \* \* \* \*[\"']", text), "533.3: board.yml is no longer scheduled every 15 minutes"
    s = sync_job(jobs_of())
    assert play(*SCHEDULE, monkeypatch, tmp_path, "533.3")[s]["ran"], f"533.3: the {s!r} job does not run on the 15-minute sweep"
    e, p = "issue_comment", comment_on_issue(57, "Looks right to me.", STRANGER)
    assert not play(e, p, monkeypatch, tmp_path, "533.3")[s]["ran"], \
        "533.3: a stranger's comment still updates the board, so no event is skipped yet for the sweep to put right"
    w = make(prs={57: 60}, records={57: tny.code_approved()},
             cards={("issue", 57): {"Status": "Work"}, ("pr", 60): {"Status": "Work"}})
    tbs.with_github_lists(w, monkeypatch, runs=tbs.BOARD_RUNS, updated={("issue", 57): "2026-10-09T15:40:00Z"})
    board.sync(*SCHEDULE, SPEC, REPO)
    got = tbs.places(w, ("issue", 57), ("pr", 60))
    assert got == {"issue #57": ("Review", NEEDS), "pr #60": ("Review", NEEDS)}, \
        f"533.3: the sweep after a skipped event left #57's cards at {got}, not Review with Needs you"

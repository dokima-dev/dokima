"""Agent records: read from an issue, built from a hand-back, and drawn.

Also the live run cards and the Stats fold. Split out of dokima/agent.py (#636).
"""
import json
import os
import re
import subprocess
import time

from dokima import card, raises
from dokima.card import field_icon, icon


VERDICTS = {"approve", "block", "escalate"}
FIXERS = {"worker", "planner"}
# The fields agents raised and answered through before #300; a hand-back holding any of them, even empty, is rejected.
OLD_FIELDS = ("questions", "concerns", "replies", "suspect_tests", "outside_scope", "blockers", "notes", "assumptions",
              "issues_found", "outside_plan", "resolved")
# How the worker's end check names each plan test still red (#595); a record whose problems hold one opens as blocked.
PLAN_TEST_FAILS = "plan test fails: "


MARK = "<!-- dokima-record -->"
LIVE = "<!-- dokima-live -->"


HANDBACK = {"planner": "plan.json", "reviewer": "review.json", "worker": "work.json"}


def name_of(r, i):
    """A record's file name in the pack's in/ folder."""
    return f"{i:02d}-{r['role']}{'-' + r['stage'] if r.get('stage') else ''}.json"


def records(items):
    """Every agent record in the conversation, oldest first. Only comments the bot posted count: anyone can paste text."""
    out = []
    for c in items:
        body = c.get("body") or ""
        if (c.get("author") or {}).get("login") != BOT or MARK not in body:
            continue
        m = re.search(r"```json\n(.*?)\n```", body, re.S)
        try:
            out.append(json.loads(m.group(1)) if m else None)
        except json.JSONDecodeError:
            continue
    return [r for r in out if isinstance(r, dict)]


# Since #610 each run's record is its own file under logs/N/records/ on the logs branch, never edited, and runs read
# earlier records only from those files.
LOGS_BRANCH = "logs"


class RecordsUnreadable(Exception):
    """The record files could not be read, so a run would start without its history."""


def logs_remote(repo):
    """The git URL holding the logs branch.

    DOKIMA_LOGS_REMOTE when set, else the repo itself on GitHub."""
    if os.environ.get("DOKIMA_LOGS_REMOTE"):
        return os.environ["DOKIMA_LOGS_REMOTE"]
    token = os.environ.get("GH_TOKEN")
    return f"https://x-access-token:{token}@github.com/{repo}.git" if token else f"https://github.com/{repo}.git"


def _git(*args, cwd=None):
    """Run git and return its output; raises CalledProcessError naming git's own words."""
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def saved_records(repo, number):
    """Every record file of the issue on the logs branch, oldest saved first.

    Read by git, with no GitHub API call. No logs branch, or no file for the issue, gives none. Files that cannot be read raise RecordsUnreadable."""
    import tempfile
    remote, folder = logs_remote(repo), f"logs/{number}/records/"
    try:
        if not _git("ls-remote", "--heads", remote, LOGS_BRANCH).strip():
            return []
        with tempfile.TemporaryDirectory(prefix="dokima-records-") as work:
            _git("init", "-q", work)
            _git("fetch", "-q", "--filter=blob:none", remote, f"refs/heads/{LOGS_BRANCH}", cwd=work)
            # The order each file was added in is the order its run saved it.
            added = _git("log", "--reverse", "--topo-order", "--diff-filter=A", "--name-only", "--format=",
                         "FETCH_HEAD", "--", folder, cwd=work).split()
            there = set(_git("ls-tree", "-r", "--name-only", "FETCH_HEAD", "--", folder, cwd=work).split())
            out = []
            for path in dict.fromkeys(p for p in added if p.endswith(".json") and p in there):
                r = json.loads(_git("show", f"FETCH_HEAD:{path}", cwd=work))
                if not isinstance(r, dict):
                    raise RecordsUnreadable(f"the record file {path} holds no record")
                out.append(r)
            return out
    except subprocess.CalledProcessError as e:
        raise RecordsUnreadable(f"the record files of #{number} on the {LOGS_BRANCH} branch could not be read: "
                                f"{scrub((e.stderr or str(e)).strip(), [os.environ.get('GH_TOKEN') or ''])}") from e
    except ValueError as e:
        raise RecordsUnreadable(f"a record file of #{number} is not JSON: {e}") from e


def save_record(repo, number, out):
    """Save OUT/record.json as one new file under logs/N/records/ on the logs branch and push it.

    Never changes a file already there, even for a run that saves twice; a remote with no logs branch gets one.
    Returns the file's path on the branch."""
    import tempfile
    rec = json.load(open(os.path.join(out, "record.json")))
    remote, folder = logs_remote(repo), f"logs/{number}/records"
    name = f"{rec.get('run_id') or 'run'}-{rec.get('role') or 'record'}{'-' + rec['stage'] if rec.get('stage') else ''}"
    with tempfile.TemporaryDirectory(prefix="dokima-save-") as tmp:
        for attempt in range(1, 4):
            work = os.path.join(tmp, str(attempt))
            if _git("ls-remote", "--heads", remote, LOGS_BRANCH).strip():
                _git("clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", "-b", LOGS_BRANCH, remote,
                     work)
                _git("reset", "-q", cwd=work)  # the index holds the branch as it is, so the commit adds one file
                taken = set(_git("ls-tree", "--name-only", "HEAD", f"{folder}/", cwd=work).split())
            else:
                _git("init", "-q", work)
                _git("checkout", "-q", "--orphan", LOGS_BRANCH, cwd=work)
                taken = set()
            stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            path, i = f"{folder}/{stamp}-{name}.json", 1
            while path in taken:
                i += 1
                path = f"{folder}/{stamp}-{name}-{i}.json"
            os.makedirs(os.path.join(work, folder), exist_ok=True)
            with open(os.path.join(work, path), "w") as f:
                json.dump(rec, f, indent=1)
            _git("add", path, cwd=work)
            _git("commit", "-qm", f"Record of run {rec.get('run_id') or 'unknown'} for #{number}", cwd=work)
            try:
                _git("push", "-q", remote, f"HEAD:refs/heads/{LOGS_BRANCH}", cwd=work)
                return path
            except subprocess.CalledProcessError:
                if attempt == 3:
                    raise  # another run pushed first each time: the step fails with git's own words


def latest(recs, role, passed=True):
    """The newest record of a role whose hand-back passed its check, or None."""
    for r in reversed(recs):
        if r.get("role") == role and (r.get("check", {}).get("passed") or not passed):
            return r
    return None


def approved(recs):
    """True when the newest passed plan has a plan review after it, and the newest
    such review approves it."""
    plans = [i for i, r in enumerate(recs) if r.get("role") == "planner" and r.get("check", {}).get("passed")]
    if not plans:
        return False
    reviews = [r for r in recs[plans[-1] + 1:] if r.get("role") == "reviewer" and r.get("stage") == "plan"
               and r.get("check", {}).get("passed")]
    return bool(reviews) and reviews[-1]["handback"].get("verdict") == "approve"


def approved_plan(recs):
    """The plan the newest approving plan review approved; None when there is none."""
    for i in range(len(recs) - 1, -1, -1):
        r = recs[i]
        if r.get("role") == "reviewer" and r.get("stage") == "plan" and r.get("check", {}).get("passed") \
                and (r.get("handback") or {}).get("verdict") == "approve":
            return latest(recs[:i], "planner")
    return None


def is_record(c, role=None, stage=None):
    """True when a comment is a record the bot posted, of the given role and stage when given."""
    if (c.get("author") or {}).get("login") != BOT or MARK not in (c.get("body") or ""):
        return False
    r = records([c])
    return bool(r) and (role is None or (r[0].get("role") == role and (r[0].get("stage") or "") == (stage or "")))


def open_blockers(recs, stage):
    """The blockers of the newest review at this stage posted before #300, unless it approved."""
    for r in reversed(recs):
        if r.get("role") == "reviewer" and (r.get("stage") or "") == stage and r.get("check", {}).get("passed"):
            return [] if r["handback"].get("verdict") == "approve" else r["handback"].get("blockers", [])
    return []


def old_blocker(b, stage):
    """An old review's blocker as the raise it stands for, under its old ID.

    A plan review's blockers are the planner's; a code review's go to the fixer they name, else the worker."""
    to = "planner" if stage == "plan" else b.get("fixer") if b.get("fixer") in FIXERS else "worker"
    text = " ".join(str(b.get(k)) for k in ("problem", "fix") if filled(b.get(k)))
    out = {"kind": "blocker", "to": to, "label": b.get("criterion"), "text": text, "evidence": b.get("evidence"),
           "raised_by": "reviewer", "id": b.get("id")}
    return {k: v for k, v in out.items() if v is not None}


def open_raises(recs):
    """Every raise on the issue still open, oldest first, each as code stamped it.

    A raise is open from the passed record that raised it until a passed record answers its ID. An issue the planner or
    the worker raised is listed for the reviewer to confirm (raises.for_review), only until the reviewer's next run.
    A reviewer's answer to a raise sent through it opens the raise it passes on (raises.passes_on), even when the
    review also sends the planner blockers of its own. A record posted before #300 still counts: the blockers of the
    newest review at each stage, unless it approved, are listed under their old IDs, and an old reply by ID answers one."""
    passed = [r for r in recs if r.get("role") in HANDBACK and (r.get("check") or {}).get("passed")
              and isinstance(r.get("handback"), dict)]
    answered = set()
    for r in passed:
        answered |= {a["raise"] for a in card.answers_of(r["handback"])}
        answered |= {x.get("blocker") for x in r["handback"].get("replies") or [] if isinstance(x, dict)}
    newest = {}
    for i, r in enumerate(passed):
        if r["role"] == "reviewer":
            newest[r.get("stage") or ""] = i
    out, by_id = [], {}
    for i, r in enumerate(passed):
        h = r["handback"]
        reviewed = any(p["role"] == "reviewer" for p in passed[i + 1:])
        for x in card.raises_of(h):
            if not x.get("id") or x["id"] in answered:
                continue
            confirm = raises.for_review(x)
            if confirm is None:
                out.append(x)
            elif not reviewed:
                out.append(confirm)
        if r["role"] == "reviewer":
            for a in card.answers_of(h):
                x = by_id.get(a["raise"]) if isinstance(a["raise"], str) else None
                on = raises.passes_on(x, a) if x else None
                if on and on["id"] not in answered:
                    out.append(on)
        by_id.update({x["id"]: x for x in card.raises_of(h) if isinstance(x.get("id"), str)})
        stage = r.get("stage") or ""
        old = h.get("blockers") if isinstance(h.get("blockers"), list) else []
        if r["role"] == "reviewer" and newest.get(stage) == i and h.get("verdict") != "approve":
            out += [old_blocker(b, stage) for b in old if isinstance(b, dict) and filled(b.get("id"))
                    and b["id"] not in answered]
    return out


def raises_for(recs, role):
    """The open raises this role must answer by ID, oldest first."""
    return [r for r in open_raises(recs) if raises.sent_to(r) == role]


def settled(recs, h):
    """The raises sent through the reviewer that a review answers, as (raise, answer) pairs.

    `recs` are the records before the review."""
    through = {x["id"]: x for x in open_raises(recs) if x.get("kind") != "issue"
               and raises.THROUGH.get((x.get("raised_by"), x.get("to"))) == "reviewer"}
    return [(through[a["raise"]], a.get("answer")) for a in card.answers_of(h)
            if isinstance(a["raise"], str) and a["raise"] in through]


def taken_ids(recs):
    """Every raise ID already on the issue, old blocker IDs included."""
    ids = set()
    for r in recs:
        h = r.get("handback") if isinstance(r, dict) else None
        if not isinstance(h, dict):
            continue
        for field in ("raises", "blockers"):
            ids |= {x.get("id") for x in h.get(field) or [] if isinstance(x, dict) and x.get("id")} \
                if isinstance(h.get(field), list) else set()
    return ids


def stamp_record(rec, earlier):
    """Stamp a record's raises with who raised them and an ID new on the issue."""
    h = rec.get("handback")
    if isinstance(h, dict) and isinstance(h.get("raises"), list) and rec.get("role") in HANDBACK:
        kept = [r for r in h["raises"] if isinstance(r, dict)]
        if len(kept) == len(h["raises"]):
            h["raises"] = raises.stamp(rec["role"], kept, taken_ids(earlier))
    return rec


def owner_raises(h):
    """The questions and blockers a hand-back raises for the owner."""
    return [r for r in card.raises_of(h) if r.get("kind") in ("question", "blocker") and r.get("to") == "owner"]


def for_planner(h):
    """True when a review sends any blocker to the planner, new or old."""
    return any(r.get("kind") == "blocker" and r.get("to") == "planner" for r in card.raises_of(h)) or \
        any(isinstance(b, dict) and b.get("fixer") == "planner" for b in h.get("blockers") or [])


LINKS = ("blocked_by", "blocks", "relates_to")


def plan_links(plan):
    """A plan record's links as three lists of issue numbers, empty when missing."""
    links = ((plan or {}).get("handback") or {}).get("links")
    links = links if isinstance(links, dict) else {}
    return {k: [n for n in links[k] if isinstance(n, int) and not isinstance(n, bool)]
            if isinstance(links.get(k), list) else [] for k in LINKS}


def build_record(role, stage, out, check_text, passed, meta):
    """This run's record: its hand-back, the code check's verdict and where it came from. Written
    by code, never the agent."""
    hb = os.path.join(out, HANDBACK[role])
    try:
        handback = json.load(open(hb))
    except (OSError, json.JSONDecodeError) as e:
        handback = {"missing": f"{HANDBACK[role]}: {e}"}
    rec = {"role": role, "stage": stage or None, **meta, "handback": handback,
           "check": {"passed": passed, "problems": [l for l in check_text.splitlines() if l.strip()] if not passed else []}}
    dropped = os.path.join(out, "dropped.txt")
    if os.path.exists(dropped):
        rec["dropped_by_fence"] = [l for l in open(dropped).read().splitlines() if l.strip()]
    return rec


def not_started(role, stage, why, meta):
    """The record of a run or command that failed before its agent started: what it
    tried to start and why it could not."""
    lines = [l.strip() for l in why.splitlines() if l.strip()] or ["A step before the agent failed; see the run for which."]
    return {"role": "not-started", "attempt": role or "command", "stage": stage or None, **meta, "handback": {},
            "check": {"passed": False, "problems": lines}}


def cancelled(role, stage, started, meta):
    """The record of a run someone cancelled: what it was and whether its agent had
    started. Nothing it handed back is used, and the river starts nothing after it."""
    return {"role": "cancelled", "attempt": role, "stage": stage or None, "agent_started": started, **meta,
            "handback": {}, "check": {"passed": False, "problems": []}}


def live_card(role, stage, state, ahead=None):
    """The run's card while it is still running: queued (or waiting for the run `ahead`
    of it), setting up, agent working since the agent started, then checking the hand-back.

    It carries its own marker and no JSON fold, so it never reads as a record; at the end of the run code edits this
    same comment into the run's record. A hand-off's queued card is put up before its run exists, so it links none.
    While the agent works the card is not edited, so it links the run's live page for detail."""
    head = {"planner": "Planner", "reviewer": review_name(stage), "worker": "Worker",
            "split": "Filing the split"}.get(role, "Command")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    head = role_icon(repo, role, stage) + f"**{head}**"
    # The card and card.yml still find a code review running by its old name, kept where the owner never reads it.
    live = LIVE + ("\n<!-- **Reviewer (pr)** -->" if role == "reviewer" and stage == "pr" else "")
    if state in ("queued", "handoff"):
        if ahead:
            line = f"{icon(repo, 'queued')} {head} · waiting for [this run]({ahead})"
            what = (f"Queued, and waiting for [this run]({ahead}) on the same issue to end; this run starts after it. "
                    "This card says working when the agent starts, then becomes the run's record.")
        else:
            line = f"{icon(repo, 'queued')} {head} · queued"
            what = "Queued: the run starts in a moment. This card says working when the agent starts, then becomes the run's record."
        return "\n".join([live, line, "", what] + ([] if state == "handoff" else ["", f"<sub>[run]({run})</sub>"])) + "\n"
    if state == "working":
        line = f"{icon(repo, 'running')} {head} · agent working since {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC"
        what = (f"The agent is working; [watch it live]({run}) on GitHub. This card says checking when the agent ends, "
                "then becomes the run's record.")
        return "\n".join([live, line, "", what]) + "\n"
    if state == "checking":
        line = f"{icon(repo, 'running')} {head} · checking"
        what = "The agent has ended and code is checking its hand-back. This card becomes the run's record next."
    else:
        line = f"{icon(repo, 'queued')} {head} · setting up"
        what = ("The machine is setting up: the branch, the starting pack and the tools. This card says working when "
                "the agent starts, then becomes the run's record.")
    return "\n".join([live, line, "", what, "", f"<sub>[run]({run})</sub>"]) + "\n"


GOING = {"queued", "in_progress", "waiting", "requested", "pending"}
CARD_HEADS = {"Planner": ("planner", ""), "Worker": ("worker", ""), "Plan review": ("reviewer", "plan"),
              "Code review": ("reviewer", "pr")}
UNRECORDED = "The run ended before posting its record: a step after the agent failed. See the run for why."


def card_stage(body):
    """The (role, stage) a live card is for; None when it names no agent."""
    m = re.search(r"\*\*(Planner|Worker|Plan review|Code review)\*\*", body)
    return CARD_HEADS[m.group(1)] if m else None


def bot_cards(repo, number):
    """Every record and live card the bot posted on the issue and its pull request."""
    places = dict.fromkeys([str(number), where_card(repo, number, "worker", "")])
    cards = []
    for n in places:
        for c in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}/comments", "--paginate") or "[]"):
            body = c.get("body") or ""
            if (c.get("user") or {}).get("login") in (BOT, f"{BOT}[bot]") and (MARK in body or LIVE in body):
                cards.append({**c, "where": n})
    return sorted(cards, key=lambda c: c.get("created_at") or "")


def unrecorded_run(repo, number):
    """The (role, stage) of the issue's last run when it ended unrecorded, else None.

    The newest run card or record the bot posted on the issue or its open pull request is still a live card, it
    links its run, and GitHub says that run has completed."""
    cards = bot_cards(repo, number)
    if not cards or MARK in cards[-1]["body"]:
        return None
    body = cards[-1]["body"]
    runs = list(dict.fromkeys(re.findall(r"/actions/runs/(\d+)", body)))
    if not runs or any(agent_github.gh("api", f"repos/{repo}/actions/runs/{rid}", "--jq", ".status").strip() in GOING for rid in runs):
        return None
    return card_stage(body)


def unrecorded(repo, number, role, stage, out):
    """A failed record linking this run, when it ended before posting its own.

    Next mentions the owner. Its live card becomes the record, or the record is posted where it would have gone. Writes OUT/record.json and
    returns True when it posted; False when the run had posted its record."""
    rid = os.environ.get("GITHUB_RUN_ID", "")
    run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{rid}"
    card = None
    for c in bot_cards(repo, number):
        if MARK in c["body"]:
            if any(str(r.get("run_id")) == rid for r in records([{"author": {"login": BOT}, "body": c["body"]}])):
                return False
        elif re.search(rf"/actions/runs/{rid}(?!\d)", c["body"]):
            card = c
    rec = {"role": role, "stage": stage or None, "run_id": rid, "run": run, "unrecorded": True, "handback": {},
           "check": {"passed": False, "problems": [UNRECORDED]}}
    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
    body = with_next(render(rec), next_line(("stop", "Give the command again to start this stage."), owners))
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
    if card:
        agent_github.gh("api", "-X", "PATCH", f"repos/{repo}/issues/comments/{card['id']}", "-f", f"body={body}", "--silent")
    else:
        agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{where_card(repo, number, role, stage)}/comments",
           "-f", f"body={body}", "--silent")
    return True


def where_card(repo, number, role, stage):
    """Where a run's card and record go: the open pull request for the worker and
    the code review, else the issue."""
    pr = agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
            "-q", ".[0].number").strip()
    return pr if pr and (role == "worker" or stage == "pr") else str(number)


def run_ahead(repo, number):
    """The link of another run still going on the issue or its pull request, found
    from GitHub's records: a live card the bot put up there, which links its run, and GitHub's word that the run has not
    completed. None when there is none."""
    own = os.environ.get("GITHUB_RUN_ID", "")
    places = {str(number), where_card(repo, number, "worker", "")}
    for n in sorted(places):
        for c in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}/comments", "--paginate") or "[]"):
            body = c.get("body") or ""
            if (c.get("user") or {}).get("login") not in (BOT, f"{BOT}[bot]") or LIVE not in body or MARK in body:
                continue
            for rid in dict.fromkeys(re.findall(r"/actions/runs/(\d+)", body)):
                if rid == own:
                    continue
                if agent_github.gh("api", f"repos/{repo}/actions/runs/{rid}", "--jq", ".status").strip() in GOING:
                    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{rid}"
    return None


def queue(role, stage, number, state):
    """Put up a run's queued card where its record will go, saying so when it
    waits for another run; returns its id."""
    repo = os.environ["GITHUB_REPOSITORY"]
    try:
        ahead = run_ahead(repo, number)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        ahead = None
    body = live_card(role, stage, state, ahead)
    return agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{where_card(repo, number, role, stage)}/comments",
              "-f", f"body={body}", "--jq", ".id").strip()


def role_icon(repo, role, stage):
    """The icon of the role a run is for, then a space; nothing for a
    run that is no agent's (a split or a command)."""
    field = {"planner": "planner", "worker": "worker"}.get(role) or (
        {"plan": "plan review", "pr": "code review"}.get(stage) if role == "reviewer" else None)
    return f"{field_icon(repo, field)} " if field else ""


HEADS = {"planner": "The planner", "reviewer": "The reviewer", "worker": "The worker", "split": "Code"}


def review_name(stage):
    """A review run's name: Plan review for the plan, Code review for the work."""
    return "Plan review" if stage == "plan" else "Code review"


def who(role, stage):
    """The name a run comment gives the run's agent."""
    return review_name(stage) if role == "reviewer" else HEADS.get(role, "The command")


def bullets(items, show):
    """One line per item, drawn by `show`; non-dict items, and a malformed field that is
    no list, are shown as they are."""
    items = items if isinstance(items, list) else [items] if items not in (None, "", {}) else []
    return [f"- {show(x) if isinstance(x, dict) else x}" for x in items]


def pairs(d):
    """One line per key and value of a field that should be a dict; nothing
    when it is not."""
    return [f"- `{k}`: {', '.join(map(str, v)) if isinstance(v, list) else v}" for k, v in d.items()] if isinstance(d, dict) else []


def files_changed(base):
    """The files changed since `base`: committed, left uncommitted or added. Empty when git cannot say."""
    if not base:
        return []
    try:
        diff = subprocess.run(["git", "diff", "--name-only", base], capture_output=True, text=True, check=True).stdout
        new = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return sorted({l.strip() for l in (diff + new).splitlines() if l.strip()})


def posted_before_raises(rec):
    """Whether the record's hand-back holds a field retired by #300.

    Such a record keeps the comment it was posted with (#299)."""
    h = rec.get("handback")
    return isinstance(h, dict) and any(f in h for f in OLD_FIELDS)


def plan_rows(plan):
    """The plan's criteria in order, keyed by their id N.k: acceptance criteria, then non-functional requirements.

    N is read from the plan's tests; without them the ids are 1, 2, ..."""
    tests = plan.get("tests") if isinstance(plan.get("tests"), dict) else {}
    keys = [k for k in tests if re.fullmatch(r"\d+\.\d+", str(k))]
    number = keys[0].split(".")[0] if keys else None
    rows = [c if isinstance(c, dict) else {"text": c} for k in ("acceptance_criteria", "non_functional")
            for c in (plan.get(k) if isinstance(plan.get(k), list) else [])]
    return {f"{number}.{i}" if number else str(i): c for i, c in enumerate(rows, 1)}


def criterion_of(r, rows):
    """The id of the plan's criterion a blocker's label names; None for none."""
    m = re.search(r"\d+\.\d+", str(r.get("label") or ""))
    return m.group(0) if m and m.group(0) in rows else None


def failed_rows(repo, text, under, source):
    """One failing item, drawn as the issue card draws a criterion.

    The failed circle and its words, the lines `under` it, then its Source when it has one."""
    return ([f"- {card.circle(repo, 'failed')} {card.escape(escape_line(text))}"] + under
            + ([f"  - Source: {source}"] if filled(source) else []))


def details(rec):
    """The long parts of a run's record, each in its own fold, drawn by the
    issue card's fold code.

    The planner's changes to older tests, with their reasons, and a split's stories in detail; nothing it repeats from
    the card above it."""
    h = rec["handback"]
    if not isinstance(h, dict) or rec["role"] != "planner":
        return []
    out = []
    for title, lines in (("Test changes", pairs(h.get("test_changes"))),
                         ("Stories in detail", bullets(h.get("stories"), lambda st: f"{st.get('title', '')}: {st.get('user_story', '')}"))):
        if lines:
            out += [""] + card.fold(title, lines)
    return out


def review_lines(repo, rec, plan):
    """What a review shows under its opening, in the owner's order.

    An escalation's reason, then each failing criterion of the plan with each of its blockers' words and its Source,
    then each ask nothing covers. Nothing that passed is listed, and no criterion number shows."""
    h = rec["handback"]
    lines = []
    if h.get("verdict") == "escalate" and filled(h.get("summary")):
        lines += ["", escape_line(h["summary"])]
    rows = plan_rows(plan) if isinstance(plan, dict) else {}
    blockers = [r for r in card.raises_of(h) if r["kind"] == "blocker"]
    failing = []
    for k, c in rows.items():
        on = [r for r in blockers if criterion_of(r, rows) == k]
        if on:
            why = [f"  - {field_icon(repo, 'blocker')} {card.escape(escape_line(r.get('text')))}" for r in on]
            failing += failed_rows(repo, c.get("text"), why, c.get("source"))
    for a in h.get("asks") or []:
        if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing":
            failing += failed_rows(repo, a.get("ask"), ["  - Nothing covers this"], a.get("source"))
    return lines + ([""] + failing if failing else [])


def opening(rec):
    """The one plain sentence a run comment opens with: what the run did."""
    role, h, passed = rec["role"], rec["handback"], rec["check"]["passed"]
    if rec.get("unrecorded"):
        return f"{who(role, rec.get('stage'))}'s run ended before posting its record."
    if not passed and role == "worker" and any(str(p).startswith(PLAN_TEST_FAILS) for p in rec["check"]["problems"]):
        return "The worker is blocked: its plan tests still fail."
    if not passed and role == "worker":
        return "The worker stopped early with its hand-back rejected by code."
    if not passed:
        return f"{who(role, rec.get('stage'))}'s run ended with its hand-back rejected by code."
    if role == "planner" and h.get("kind") == "feature":
        return f"The planner proposes a split into {len(h.get('stories') or [])} stories."
    if role == "planner":
        return "The planner planned this issue."
    if role == "reviewer":
        name, what = who(role, rec.get("stage")), "the plan" if rec.get("stage") == "plan" else "the work"
        k = sum(1 for r in card.raises_of(h) if r.get("kind") == "blocker")
        return {"approve": f"{name} passed {what}.",
                "block": f"{name} blocked {what} with {k} blocker{'s' if k != 1 else ''}." if k else f"{name} blocked {what}.",
                "escalate": f"{name} escalated {what} to you."}.get(h.get("verdict"), f"{name} judged {what}.")
    if role == "split":
        return f"Code filed the split as {len(h.get('stories') or [])} stories."
    return h["summary"].strip() if filled(h.get("summary")) else ""


def record_fold(rec):
    """The full JSON record, always the last fold of a run comment: later packs are built from it."""
    return ["", "<details><summary>Full record</summary>", "", "```json", json.dumps(rec, indent=1), "```", "", "</details>"]


def answered_lines(repo, rec, earlier):
    """A passed run's answers to earlier raises, drawn the same for every agent.

    They go in a Raised earlier section; an answer finds its raise among `earlier` by ID. No ID is ever drawn."""
    h = rec["handback"]
    if not card.answers_of(h):
        return []
    found = {}
    for r in earlier or []:
        if isinstance(r, dict) and (r.get("check") or {}).get("passed"):
            found.update({x["id"]: (x, r) for x in card.raises_of(r.get("handback")) if x.get("id")})
    lines = ["", "**Raised earlier:**", ""]
    for a in card.answers_of(h):
        r, by = found.get(a["raise"], (None, None))
        lines.append(f"- {raised_by(by)} raised: {card.raise_line(repo, r)[2:]}" if r
                     else "- A raise not found in this issue's earlier records")
        word = {"done": "Done", "disagree": "Disagree"}.get(a.get("answer"), escape_line(str(a.get("answer"))))
        lines.append(f"  - {word}: {card.short_refs(repo, escape_line(a.get('why')))}")
        if filled(a.get("words")) and filled(a.get("source")):
            lines.append(f"  - Your words: {said(a['words'], a['source'])}")
    return lines


def raised_by(rec):
    """Who raised an earlier record's raises and where, e.g. "Code review on [#462](link)".

    The link is the comment the record was posted as; just "Planner" when that comment is not known."""
    name = review_name(rec.get("stage")) if rec.get("role") == "reviewer" else \
        {"planner": "Planner", "worker": "Worker"}.get(rec.get("role"), "Code")
    m = re.fullmatch(r"https://[^\s()]+/(?:issues|pull)/(\d+)#issuecomment-\d+", str(rec.get("url") or ""))
    return f"{name} on [#{m.group(1)}]({rec['url']})" if m else name


def raised_lines(repo, rec, placed=()):
    """What a passed run raised, in a Raised section.

    A review's raises go blockers first, then questions, then issues, leaving out the blockers `placed` under their
    criterion. No ID is ever drawn."""
    raised = [r for r in card.raises_of(rec["handback"]) if not any(r is p for p in placed)]
    if rec["role"] == "reviewer":
        raised.sort(key=lambda r: ("blocker", "question", "issue").index(r["kind"]))
    lines = ["", "**Raised:**", ""] if raised else []
    for r in raised:
        lines.append(card.raise_line(repo, r))
        if filled(r.get("evidence")):
            lines.append(f"  - Evidence: {card.short_refs(repo, card.escape(escape_line(r['evidence'])))}")
    return lines


def render(rec, pr=None, plan=None, earlier=None):
    """The comment that carries a record, never repeating the card above it.

    One plain sentence saying what the run did, then only what that run changed, decided or raised; the long parts
    in folds, the Stats fold, then the full record as JSON in the last fold. `pr` is the link of the worker's pull request, once it exists; `plan` is the plan a review
    judged, whose criteria its blockers fail; `earlier` is the issue's records before this one, oldest first, where
    answers find the raises they answer. A record holding a field retired by #300 keeps the comment it was posted with."""
    role, h = rec["role"], rec["handback"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if posted_before_raises(rec):
        return render_as_posted(rec, pr, plan, earlier)
    if role == "not-started":
        a = rec.get("attempt")
        name = "Filing the split" if a == "split" else who(a, rec.get("stage"))
        lines = [MARK, f"{icon(repo, 'failed')} {role_icon(repo, a, rec.get('stage'))}{name} stopped before any agent started.", ""] + [f"- {p}" for p in rec["check"]["problems"]]
        lines += record_fold(rec) + ["", f"<sub>No agent ran · [run]({rec.get('run', '')})</sub>"]
        return "\n".join(lines) + "\n"
    if role == "cancelled":
        a = rec.get("attempt")
        name = who(a, rec.get("stage"))
        what = (f"{name} run was cancelled after its agent started, and nothing it handed back is used." if rec.get("agent_started")
                else f"{name} run was cancelled before its agent started.")
        lines = [MARK, f"{icon(repo, 'cancelled')} {role_icon(repo, a, rec.get('stage'))}{what}"]
        if rec.get("agent_started"):
            lines += record_fold(rec) + stats_tail(rec)
        else:
            lines += record_fold(rec) + ["", f"<sub>No agent ran · [run]({rec.get('run', '')})</sub>"]
        return "\n".join(lines) + "\n"
    if role == "updater":
        return render_as_posted(rec, pr, plan, earlier)
    passed = rec["check"]["passed"]
    first = f"{icon(repo, 'passed' if passed else 'failed')} {role_icon(repo, role, rec.get('stage'))}{escape_line(opening(rec))}"
    if role == "worker" and pr:
        first += f" {pr}"
    lines, placed = [MARK, first], []
    if not passed:
        lines += [""] + [f"- {p}" for p in rec["check"]["problems"]]
    elif role == "planner" and h.get("kind") == "feature":
        lines += ["", f"**Feature:** {h.get('feature', '')}", ""]
        lines += [f"{i}. {st.get('title', '')}" for i, st in enumerate(h.get("stories", []), 1)]
    elif role == "worker":
        files = [f for f in rec.get("files_changed") or [] if filled(f)]
        branch = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/blob/{rec.get('branch') or 'main'}"
        built = ([f"{field_icon(repo, 'files changed')} **Files changed:** " + ", ".join(f"[{f}]({branch}/{f})" for f in files)]
                 if files else []) + ([f"- Its own test run: {escape_line(h['evidence'])}"] if filled(h.get("evidence")) else [])
        # Its raises stay on top; what it built and its answers follow, so the top holds only its sentence otherwise.
        lines += raised_lines(repo, rec) + ([""] + card.fold("What it built", built) if built else [])
        lines += answered_lines(repo, rec, earlier)
    elif role == "reviewer":
        if filled(rec.get("no_baseline")):
            lines += ["", f"Every test ran because no baseline was usable: {escape_line(rec['no_baseline'])}."]
        lines += review_lines(repo, rec, plan)
        rows = plan_rows(plan) if isinstance(plan, dict) else {}
        placed = [r for r in card.raises_of(h) if r["kind"] == "blocker" and criterion_of(r, rows)]
    elif role == "split":
        num = {f["story"]: f["issue"] for f in h.get("stories", [])}
        lines += [""] + [f"{f['story']}. #{f['issue']} {f['title']}" + (f" ({field_icon(repo, 'blocked by')} blocked by {', '.join('#' + str(num[d]) for d in f['blocked_by'])})" if f["blocked_by"] else "")
                         for f in h.get("stories", [])]
        lines += ["", "Each story now goes through the flow on its own: comment `/plan` on it to start."]
    if passed and role != "worker":
        lines += answered_lines(repo, rec, earlier) + raised_lines(repo, rec, placed)
    lines += details(rec) + record_fold(rec) + stats_tail(rec)
    return "\n".join(lines) + "\n"


# What a record holding a field retired by #300 was posted with, kept as it was (#299).


def details_as_posted(rec):
    """The long parts of a record kept as posted, each in its own fold.

    Drawn by the issue card's fold code."""
    role, h = rec["role"], rec["handback"]
    mark = lambda field: field_icon(os.environ.get("GITHUB_REPOSITORY", ""), field)
    if not isinstance(h, dict):
        return []
    parts = []
    if role == "planner":
        parts += [("Non-functional requirements", bullets(h.get("non_functional"), lambda n: f"{n.get('text', '')} "
                                                           f"({n.get('why', '')}; {n.get('principle', '')})")),
                  ("Scope", bullets(h.get("scope"), str)),
                  ("Tests", pairs(h.get("tests"))),
                  ("Test changes", pairs(h.get("test_changes"))),
                  ("Concerns", bullets(h.get("concerns"), lambda c: f"{c.get('text', '')} ({c.get('evidence', '')})")),
                  ("Stories in detail", bullets(h.get("stories"), lambda st: f"{st.get('title', '')}: {st.get('user_story', '')}"))]
    elif role == "worker":
        parts += [("What it built", pairs(h.get("criteria"))
                   + ([f"- Its own test run: {h['evidence']}"] if h.get("evidence") else [])),
                  ("What it found", bullets(h.get("outside_scope"), lambda o: f"{mark('outside the plan')} Outside the plan: {o.get('file', '')}: {o.get('why', '')}")),
                  ("What it raised", bullets(h.get("suspect_tests"), lambda t: f"Suspect test {t.get('test', '')}: {t.get('evidence', '')}")
                   + bullets(h.get("replies"), lambda r: f"{r.get('blocker', '')} {r.get('answer', '')}: {r.get('why', '')}"))]
    elif role == "reviewer":
        parts += [("Details", ([f"- {h['summary']}"] if h.get("summary") and h.get("verdict") != "escalate" else [])
                   + bullets(h.get("blockers"), lambda b: f"{b.get('id')} on {b.get('criterion')}: {b.get('problem', '')} "
                                                          f"Evidence: {b.get('evidence', '')} Fix: {b.get('fix', '')}")
                   + bullets(h.get("resolved"), lambda r: f"Resolved: {json.dumps(r)}")),
                  (f"{mark('note')} Notes", bullets(h.get("notes"), lambda n: f"{n.get('text', '')} ({n.get('evidence', '')})")),
                  (f"{mark('outside the plan')} Outside the plan", bullets(h.get("outside_plan"), lambda o: f"{o.get('file', '')}: {o.get('change', '')}")),
                  ("The owner's asks", bullets(h.get("asks"), lambda a: f"{a.get('ask', '')} ({a.get('criterion', '')}, {a.get('source', '')})"))]
    prev = h.get("previous_step")
    if isinstance(prev, dict):
        parts.append(("What the previous step did", [f"- {mark('still open') + ' ' if k == 'open' else ''}**{label}:**{x[1:]}" for k, label in
                                                     (("did", "Did"), ("decided", "Decided"), ("open", "Still open"))
                                                     for x in bullets(prev.get(k), str)]))
    out = []
    for title, lines in parts:
        if lines:
            out += [""] + card.fold(title, lines)
    return out


def opening_as_posted(rec):
    """The one plain sentence a run comment opens with: what the run did."""
    role, h, passed = rec["role"], rec["handback"], rec["check"]["passed"]
    if not passed and role == "worker":
        return "The worker stopped early with its hand-back rejected by code."
    if not passed:
        return f"{HEADS[role]}'s run ended with its hand-back rejected by code."
    if role == "planner" and h.get("kind") == "feature":
        n = len(h.get("stories") or [])
        return f"The planner proposes a split into {n} stories" + (" and asks you questions." if h.get("questions") else ".")
    if role == "planner":
        q = len(h.get("questions") or [])
        return f"The planner planned this issue and asks you {q} question{'s' if q > 1 else ''}." if q else "The planner planned this issue."
    if role == "reviewer":
        what = "the plan" if rec.get("stage") == "plan" else "the work"
        n = len({b.get("criterion") for b in h.get("blockers") or [] if isinstance(b, dict)})
        k = sum(1 for r in card.raises_of(h) if r.get("kind") == "blocker")
        blocked = f"with {k} blocker{'s' if k != 1 else ''}" if k and not n else f"on {n} criteri{'a' if n != 1 else 'on'}"
        return {"approve": f"The reviewer passed {what}.",
                "block": f"The reviewer blocked {what} {blocked}.",
                "escalate": f"The reviewer escalated {what} to you."}.get(h.get("verdict"), f"The reviewer judged {what}.")
    if role == "split":
        return f"Code filed the split as {len(h.get('stories') or [])} stories."
    return h["summary"].strip() if filled(h.get("summary")) else ""


def render_as_posted(rec, pr=None, plan=None, earlier=None):
    """The comment a record kept as posted, or a clash, is drawn with.

    One plain sentence saying what the run did, the short version the owner needs at a glance, the long parts in
    folds, then the full record as JSON in the last fold. `pr` is the link of the worker's pull request, once it exists; `plan` is the plan a plan review judged, whose assumptions answer its
    questions; `earlier` is the issue's records before this one, oldest first, where a review's answers find the
    raises they answer."""
    role, h = rec["role"], rec["handback"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if role == "not-started":
        a = rec.get("attempt")
        who = {"planner": "The planner", "reviewer": "The reviewer", "worker": "The worker",
               "split": "Filing the split"}.get(a, "The command")
        lines = [MARK, f"{icon(repo, 'failed')} {role_icon(repo, a, rec.get('stage'))}{who} stopped before any agent started.", ""] + [f"- {p}" for p in rec["check"]["problems"]]
        lines += record_fold(rec) + ["", f"<sub>No agent ran · [run]({rec.get('run', '')})</sub>"]
        return "\n".join(lines) + "\n"
    if role == "cancelled":
        a = rec.get("attempt")
        who = {"planner": "The planner", "reviewer": "The reviewer", "worker": "The worker"}.get(a, "The command")
        what = (f"{who} run was cancelled after its agent started, and nothing it handed back is used." if rec.get("agent_started")
                else f"{who} run was cancelled before its agent started.")
        lines = [MARK, f"{icon(repo, 'cancelled')} {role_icon(repo, a, rec.get('stage'))}{what}"]
        lines += record_fold(rec) + ["", footnote(rec) if rec.get("agent_started") else f"<sub>No agent ran · [run]({rec.get('run', '')})</sub>"]
        return "\n".join(lines) + "\n"
    if role == "updater":
        # A clash with main, found by code after a merge: the merge, its PR and every file that clashed.
        by = f" (#{h['merged_pr']})" if h.get("merged_pr") else ""
        so = {True: "so the planner re-plans against the new main", False: "so the issue needs a re-plan",
              None: "so the issue needs a re-plan, but autopilot could not be read"}.get(h.get("autopilot", True))
        lines = [MARK, f"Pull request #{h.get('pr')} clashes with `{h.get('base') or 'main'}` since {str(h.get('merge', ''))[:7]}{by} "
                       f"merged, {so}. The files that clashed:", ""]
        lines += [f"- `{f}`" for f in h.get("files") or []] or [f"- {h.get('why') or 'none listed'}"]
        lines += record_fold(rec) + ["", f"<sub>Found by code, no model" + (f" · [run]({rec['run']})" if rec.get("run") else "") + "</sub>"]
        return "\n".join(lines) + "\n"
    passed = rec["check"]["passed"]
    first = f"{icon(repo, 'passed' if passed else 'failed')} {role_icon(repo, role, rec.get('stage'))}{escape_line(opening_as_posted(rec))}"
    if role == "worker" and pr:
        first += f" {pr}"
    lines = [MARK, first]
    if not passed:
        lines += [""] + [f"- {p}" for p in rec["check"]["problems"]]
    elif role == "planner" and h.get("kind") == "feature":
        lines += ["", f"**Feature:** {h.get('feature', '')}", ""]
        lines += [f"{i}. {st.get('title', '')}" for i, st in enumerate(h.get("stories", []), 1)]
    elif role == "planner":
        lines += ["", f"**User story:** {h.get('user_story') or h.get('question') or ''}"]
        criteria = [c.get("text", "") if isinstance(c, dict) else c for c in h.get("acceptance_criteria") or []]
        if criteria:
            lines += ["", f"{field_icon(repo, 'acceptance criterion')} **Acceptance criteria:**", ""] + [f"{i}. {c}" for i, c in enumerate(criteria, 1)]
    elif role == "reviewer":
        if h.get("verdict") == "escalate" and h.get("summary"):
            lines += ["", h["summary"]]
        fixes = lambda b: f", the {b['fixer']} fixes it" if b.get("fixer") in FIXERS else ""
        blocks = [f"- {field_icon(repo, 'blocker')} **{b.get('id')}** ({b.get('criterion')}{fixes(b)}): {b.get('problem')}" for b in h.get("blockers") or []]
        if blocks:
            lines += [""] + blocks
        judged = [a for a in h.get("assumptions") or [] if isinstance(a, dict)]
        answers = {q.get("question"): q.get("assumption") for q in (plan or {}).get("questions") or []
                   if isinstance(q, dict) and q.get("assumption")}
        answered = [a for a in judged if a.get("accepted") is True and a.get("matched") and a.get("source")
                    and a.get("question") in answers]
        if answered:
            lines += ["", f"{field_icon(repo, 'question')} **Answered from your words:**"]
            for a in answered:
                lines += [f"- {escape_line(a['question'])}", f"  - {escape_line(answers[a['question']])}",
                          f"  - Your words: {said(a['matched'], a['source'])}"]
        judged = [a for a in judged if a not in answered]
        if judged:
            lines += ["", "**The plan's assumptions:**"]
            lines += [f"- {a.get('question', '')} Accepted on your words \"{a.get('matched', '')}\" ({a.get('source', '')})."
                      if a.get("accepted") is True else f"- {a.get('question', '')} Not accepted: {a.get('why', '')}"
                      for a in judged]
        if h.get("issues_found"):
            lines += ["", f"{field_icon(repo, 'issue found')} **Issues found outside this one** (proposals until you file them):"]
            lines += [f"{i}. {f.get('title')}: {f.get('why')}" for i, f in enumerate(h["issues_found"], 1)]
    elif role == "split":
        num = {f["story"]: f["issue"] for f in h.get("stories", [])}
        lines += [""] + [f"{f['story']}. #{f['issue']} {f['title']}" + (f" ({field_icon(repo, 'blocked by')} blocked by {', '.join('#' + str(num[d]) for d in f['blocked_by'])})" if f["blocked_by"] else "")
                         for f in h.get("stories", [])]
        lines += ["", "Each story now goes through the flow on its own: comment `/plan` on it to start."]
    related = card.link_lines(repo, h.get("links")) if passed and role == "planner" else []
    if related:
        lines += [""] + related
    if passed and role == "planner" and h.get("questions"):
        lines += ["", f"{field_icon(repo, 'question')} **Questions for you** (it planned on the reading it names; reply with `/plan` and your words, or leave them):"]
        lines += [f"- {q.get('question', '')} Assumed: {q.get('assumption', '')}" if isinstance(q, dict) else f"- {q}"
                  for q in h["questions"]]
    if passed:
        lines += (answered_lines(repo, rec, earlier) if role == "reviewer" else []) + raised_lines(repo, rec)
    lines += details_as_posted(rec) + record_fold(rec) + ["", footnote(rec)]
    return "\n".join(lines) + "\n"


def words_link(source):
    """Where the owner said the words: the issue or comment link as given, or AGENTS.md
    on the repo's main branch."""
    if source == "AGENTS.md":
        return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/blob/main/AGENTS.md"
    return source


def said(words, source):
    """The owner's quoted words, then where they said them.

    An issue or comment follows the quote written out bare, so GitHub draws it as its own reference; words from
    AGENTS.md, which is no issue or pull request, stay linked to it."""
    if source == "AGENTS.md":
        return f"[\"{escape_line(words).replace(']', '\\]')}\"]({words_link(source)})"
    return f"\"{escape_line(words)}\" {source}"


def escape_line(text):
    """One sentence kept on one line, so the comment opens with it whole."""
    return re.sub(r"\s+", " ", text or "").strip()


def jsonl_files(root):
    """Every session log under root, hidden folders included (Claude keeps its logs under .claude)."""
    return sorted(os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs if f.endswith(".jsonl"))


def scrub(text, secrets):
    """Remove every secret value from text before it is saved anywhere public."""
    for v in sorted((x for x in secrets if len(x) >= 8), key=len, reverse=True):
        text = text.replace(v, "[secret removed]")
    return text


def transcript(log_dir, secrets=()):
    """A readable transcript of the run's session: what the agent said, each tool it used
    and a cut of each result."""
    out, n = [], 0
    for f in jsonl_files(log_dir):
        for line in open(f):
            try:
                m = json.loads(line).get("message") or {}
            except json.JSONDecodeError:
                continue
            content = m.get("content")
            for b in ([{"type": "text", "text": content}] if isinstance(content, str) else content or []):
                kind = b.get("type")
                if kind == "text" and b.get("text", "").strip() and m.get("role") == "assistant":
                    out.append(f"**Agent:** {b['text'].strip()}")
                elif kind == "tool_use":
                    n += 1
                    i = b.get("input") or {}
                    what = i.get("command") or i.get("file_path") or i.get("pattern") or json.dumps(i)
                    out.append(f"`{n}. {b.get('name')}`\n```\n{str(what)[:2000]}\n```")
                elif kind == "tool_result":
                    r = b.get("content")
                    r = r if isinstance(r, str) else " ".join(x.get("text", "") for x in (r or []) if isinstance(x, dict))
                    out.append("> " + r.strip()[:1500].replace("\n", "\n> "))
    return scrub("\n\n".join(out) + "\n", secrets)


def run_report(path):
    """Claude's own end-of-run report: time, turns, tokens and API-equivalent cost, exactly as Claude gave them."""
    try:
        d = json.load(open(path))
    except (OSError, json.JSONDecodeError):
        return {}
    u = d.get("usage") or {}
    return {"duration_ms": d.get("duration_ms"), "turns": d.get("num_turns"), "cost_usd": d.get("total_cost_usd"),
            "tokens_in": (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0),
            "tokens_out": u.get("output_tokens")}


STATS = "<!-- dokima-stats -->"


def stats_tail(rec):
    """The stats line, the last line of every run comment; `with_next` puts Next right above it."""
    stats = field_icon(os.environ.get("GITHUB_REPOSITORY", ""), "stats")
    return ["", STATS, f"{stats} {stats_line(rec)}"]


def with_next(text, line):
    """The comment with the Next line right above its stats line, which stays last."""
    i = text.rfind(STATS)
    if i < 0:
        return text.rstrip("\n") + "\n\n" + line + "\n"
    return text[:i].rstrip("\n") + "\n\n" + line + "\n\n" + text[i:].rstrip("\n") + "\n"


def short(n):
    """A token count read short, with no decimals: 950, 12K, 3M.

    As it is under a thousand, then K, then M, rounded to the nearest with halves up."""
    if n < 1000:
        return str(n)
    k = (n + 500) // 1000
    return f"{k}K" if k < 1000 else f"{(n + 500000) // 1000000}M"


def stats_line(rec):
    """The run's stats: model, time, turns, tokens, cost and its links.

    The links go to its whole conversation and its run."""
    r = rec.get("report") or {}
    if rec.get("role") == "split":
        return f"Filed by code, no model ran · [run]({rec.get('run', '')})"
    pretty = lambda m: (lambda x: f"{x.group(1).title()} {x.group(2)}.{x.group(3)}" if x else m)(re.match(r"claude-([a-z]+)-(\d+)-(\d+)", m))
    parts = [", ".join(pretty(m) for m in rec.get("models") or []) or "model unknown"]
    if r.get("duration_ms"):
        parts.append(f"{round(r['duration_ms'] / 60000, 1)} min")
    if r.get("turns"):
        parts.append(f"{r['turns']} turns")
    if r.get("tokens_in") or r.get("tokens_out"):
        parts.append(f"{short(r.get('tokens_in') or 0)} tokens in, {short(r.get('tokens_out') or 0)} out")
    if r.get("cost_usd") is not None:
        parts.append(f"${r['cost_usd']:.2f} at API prices")
    links = " · ".join(x for x in (f"[conversation]({rec['log']})" if rec.get("log") else "", f"[run]({rec['run']})" if rec.get("run") else "") if x)
    return " · ".join(parts) + (" · " + links if links else "")


def footnote(rec):
    """The stats line under the card of a record kept as posted.

    Model, time, turns, tokens and cost, and the link to the full conversation."""
    r = rec.get("report") or {}
    stats = field_icon(os.environ.get("GITHUB_REPOSITORY", ""), "stats")
    if rec.get("role") == "split":
        return f"<sub>{stats} Filed by code, no model · [run]({rec.get('run', '')})</sub>"
    pretty = lambda m: (lambda x: f"{x.group(1).title()} {x.group(2)}.{x.group(3)}" if x else m)(re.match(r"claude-([a-z]+)-(\d+)-(\d+)", m))
    parts = [", ".join(pretty(m) for m in rec.get("models") or []) or "model unknown"]
    if r.get("duration_ms"):
        parts.append(f"{round(r['duration_ms'] / 60000, 1)} min")
    if r.get("turns"):
        parts.append(f"{r['turns']} turns")
    if r.get("tokens_in") or r.get("tokens_out"):
        parts.append(f"{r.get('tokens_in', 0):,} tokens in, {r.get('tokens_out') or 0:,} out")
    if r.get("cost_usd") is not None:
        parts.append(f"${r['cost_usd']:.2f} at API prices")
    links = " · ".join(x for x in (f"[conversation]({rec['log']})" if rec.get("log") else "", f"[run]({rec['run']})" if rec.get("run") else "") if x)
    return f"<sub>{stats} " + " · ".join(parts) + (" · " + links if links else "") + "</sub>"


def models_used(log_dir):
    """Every model named in the run's session logs, so the record proves which model did the work."""
    seen = set()
    for f in jsonl_files(log_dir):
        for line in open(f):
            try:
                m = (json.loads(line).get("message") or {}).get("model")
            except json.JSONDecodeError:
                continue
            if m:
                seen.add(m)
    return sorted(seen)


def filled(v):
    """True for a non-empty string."""
    return isinstance(v, str) and bool(v.strip())


def first_sentence(text):
    """A raise's first sentence, on one line, as a filed issue's title."""
    text = escape_line(text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:250]


# The other agent job files, imported last so the job files can use each other (#636).
from dokima import agent_github
from dokima.agent_github import BOT
from dokima.agent_next import next_line

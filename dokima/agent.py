"""Packs and hand-back checks for running one agent by hand on a fresh machine.

`pack` builds the agent's starting pack from GitHub's records: the issue as it stands (body and every comment) and the
JSON hand-backs of earlier runs, downloaded from those runs. `check` is the deterministic check an agent runs on its own
hand-back before it finishes, and that code runs again after it: a malformed hand-back never reaches the next agent.
The plan's own check lives in dokima/planner.py; this module adds review.json and work.json.
"""
import contextlib
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

from dokima import card, raises, words
from dokima.card import field_icon, icon

VERDICTS = {"approve", "block", "escalate"}
FIXERS = {"worker", "planner"}
# The fields agents raised and answered through before #300; a hand-back holding any of them, even empty, is rejected.
OLD_FIELDS = ("questions", "concerns", "replies", "suspect_tests", "outside_scope", "blockers", "notes", "assumptions",
              "issues_found", "outside_plan", "resolved")


def gh(*args):
    """Run the GitHub CLI and return its output."""
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


MARK = "<!-- dokima-record -->"
LIVE = "<!-- dokima-live -->"
BOT = os.environ.get("DOKIMA_BOT", "dokima-runtime")
HANDBACK = {"planner": "plan.json", "reviewer": "review.json", "worker": "work.json"}


def linked_prs(repo, number):
    """Pull requests built for the issue: from its work or try branch."""
    found = []
    for head in (f"work/issue-{number}", f"try/issue-{number}"):
        found += json.loads(gh("pr", "list", "-R", repo, "--head", head, "--state", "all", "--json", "number"))
    return sorted({p["number"] for p in found})


def conversation(repo, number):
    """The issue and its pull requests as one list of comments, oldest first, each saying where it was written."""
    d = json.loads(gh("issue", "view", str(number), "-R", repo, "--json", "number,title,body,comments"))
    items = [{**c, "where": f"issue #{number}"} for c in d["comments"]]
    for pr in linked_prs(repo, number):
        p = json.loads(gh("pr", "view", str(pr), "-R", repo, "--json", "comments,reviews"))
        items += [{**c, "where": f"PR #{pr}"} for c in p["comments"]]
        items += [{"author": r["author"], "body": r["body"], "createdAt": r["submittedAt"], "where": f"PR #{pr} review ({r['state'].lower()})"}
                  for r in p["reviews"] if r.get("body")]
        for n in json.loads(gh("api", f"repos/{repo}/pulls/{pr}/comments", "--paginate")):
            items.append({"author": {"login": n["user"]["login"]}, "body": n["body"], "createdAt": n["created_at"],
                          "where": f"PR #{pr} line note on {n['path']}:{n.get('line') or n.get('original_line')}"})
    items.sort(key=lambda c: c["createdAt"])
    return d, items


def issue_text(d, items):
    """The issue as it stands: title, body and every comment, oldest first. A record's JSON is in in/ as its own file,
    so its comment points there instead of repeating it."""
    parts, n = [f"# Issue #{d['number']}: {d['title']}", "", d["body"] or "", "", "## Comments"], 0
    for c in items:
        b = c["body"] or ""
        if rs := records([c]):
            n += 1
            b = re.sub(r"```json\n.*?\n```", f"(full record: in/{name_of(rs[0], n)})", b, count=1, flags=re.S)
        parts += ["", f"### {c['author']['login']} on {c['where']} ({c['createdAt']})", "", b]
    return "\n".join(parts) + "\n"


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


def latest(recs, role, passed=True):
    """The newest record of a role whose hand-back passed its check, or None."""
    for r in reversed(recs):
        if r.get("role") == role and (r.get("check", {}).get("passed") or not passed):
            return r
    return None


def approved(recs):
    """True when the newest passed plan has a plan review after it, and the newest such review approves it."""
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


def open_issues(repo):
    """Every open issue of the repo, every page, with its number, title and body; pull requests are left out."""
    items = [i for p in pages(gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
    return [{"number": i["number"], "title": i["title"], "body": i.get("body") or ""} for i in items
            if "pull_request" not in i]


def problems_links(h, pack_dir):
    """Everything wrong with a plan's links: three lists of open issue numbers from the pack, never the issue itself,
    and no issue in two lists."""
    path = os.path.join(pack_dir, "open_issues.json")
    if not os.path.exists(path):
        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
    links = h.get("links")
    if not isinstance(links, dict):
        return ["links must be an object with three lists: " + ", ".join(LINKS)]
    issue = os.path.join(pack_dir, "issue.md")
    m = re.match(r"# Issue #(\d+)", open(issue).read()) if os.path.exists(issue) else None
    me = int(m.group(1)) if m else None
    known = {i.get("number") for i in json.load(open(path)) if isinstance(i, dict)}
    bad, seen = [], {}
    for k in LINKS:
        v = links.get(k)
        if not isinstance(v, list) or not all(isinstance(n, int) and not isinstance(n, bool) for n in v):
            bad.append(f"links.{k} must be a list of issue numbers")
            continue
        for n in v:
            if n == me:
                bad.append(f"links.{k} links #{n}, the issue itself")
            elif n not in known:
                bad.append(f"links.{k} links #{n}, which is not an open issue")
            seen.setdefault(n, [])
            if k not in seen[n]:
                seen[n].append(k)
    bad += [f"#{n} sits in more than one list of links: {', '.join(ks)}" for n, ks in seen.items() if len(ks) > 1]
    return bad


def pack_records(pack_dir):
    """The readable earlier records in the pack's in/ folder, oldest first."""
    out = []
    for path in sorted(glob.glob(os.path.join(pack_dir, "in", "*.json"))):
        try:
            r = json.load(open(path))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(r, dict):
            out.append(r)
    return out


def pack_issue(pack_dir):
    """The issue number the pack's issue.md is about, or None."""
    issue = os.path.join(pack_dir, "issue.md")
    m = re.match(r"# Issue #(\d+)", open(issue).read()) if os.path.exists(issue) else None
    return int(m.group(1)) if m else None


def problems_for_owner(a, number, parent):
    """Everything wrong with a reviewer's answer to a question for the owner.

    Done needs the owner's words, where they said them, and whether the reading changes how the system works or what
    it costs."""
    rid, bad = a.get("raise"), []
    if a.get("answer") != "done":
        return bad
    if not filled(a.get("words")):
        bad.append(f"the answer to {rid}, a question for the owner, needs words: the owner's own words, word for word")
    where = f"{issue_url(number)}, its parent {issue_url(parent)}, one of their comments' links" if parent \
        else f"{issue_url(number)}, one of its comments' links"
    if not filled(a.get("source")) or not owner_source(a["source"].strip(), number, parent):
        bad.append(f"the answer to {rid}, a question for the owner, needs a source: {where}, or AGENTS.md")
    if not isinstance(a.get("changes"), bool):
        bad.append(f"the answer to {rid}, a question for the owner, needs changes: true or false, whether the reading "
                   "changes how the system works or what it costs")
    return bad


def problems_round(role, h, pack_dir):
    """Everything wrong with how a hand-back answers the raises listed for its role.

    The reviewer may also answer a question for the owner still open in the pack's records, with the owner's words,
    where they said them and whether the reading changes anything; the planner's links must name open issues in the
    pack."""
    path = os.path.join(pack_dir, "open_blockers.json")
    listed = json.load(open(path)) if os.path.exists(path) else []
    listed = [r for r in listed if isinstance(r, dict)] if isinstance(listed, list) else []
    answers = h.get("answers", [])
    questions = []
    if role == "reviewer":
        questions = [r for r in open_raises(pack_records(pack_dir))
                     if r.get("kind") == "question" and r.get("to") == "owner" and r.get("raised_by") == "planner"]
    bad = raises.check_answers(role, answers, listed + questions)
    if questions and isinstance(answers, list):
        asked = {r["id"] for r in questions}
        number, parent = pack_issue(pack_dir), pack_parent(pack_dir)
        for a in answers:
            if isinstance(a, dict) and a.get("raise") in asked:
                bad += problems_for_owner(a, number, parent)
    if role == "planner":
        bad += problems_links(h, pack_dir)
    return bad


def story_body(parent, i, story, parent_title):
    """A story's issue body, drawn by code from the approved plan, so the child planner starts from exactly what was agreed."""
    lines = ["<!-- dokima-card -->", "<!-- /dokima-card -->", "",
             f"<details open><summary>From the approved plan of #{parent}, story {i}</summary>", "",
             f"**Part of:** #{parent} {parent_title}", "", f"**User story:** {story.get('user_story', '')}", ""]
    if story.get("context"):
        lines += [f"**Context:** {story['context']}", ""]
    lines += ["**Acceptance criteria:**"]
    lines += [f"- {c.get('text', '')} ([source]({c.get('source', '')}))" for c in story.get("acceptance_criteria", [])]
    if story.get("non_functional"):
        lines += ["", "**Non-functional:**"] + [f"- {n.get('text', '')} ({n.get('why', '')})" for n in story["non_functional"]]
    return "\n".join(lines + ["", "</details>"]) + "\n"


def file_split(repo, parent, recs, labels=()):
    """File the stories of the newest approved split as sub-issues of the parent, in order, with their blocked-by links,
    each created with the given labels.

    Returns the record of what was filed. Filing twice files nothing new: the newest split record is returned instead."""
    done = latest(recs, "split", passed=True)
    if done:
        return done
    plan = latest(recs, "planner")["handback"]
    title = json.loads(gh("issue", "view", str(parent), "-R", repo, "--json", "title"))["title"]
    filed = []
    for i, st in enumerate(plan["stories"], 1):
        extra = [x for label in labels for x in ("--label", label)]
        url = gh("issue", "create", "-R", repo, "--title", st["title"], "--body", story_body(parent, i, st, title), *extra).strip()
        number = int(url.rstrip("/").split("/")[-1])
        node = json.loads(gh("api", f"repos/{repo}/issues/{number}"))["id"]
        gh("api", "-X", "POST", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={node}")
        filed.append({"story": i, "issue": number, "title": st["title"], "id": node,
                      "blocked_by": [d + 1 for d in st.get("depends_on", [])]})
    by_story = {f["story"]: f for f in filed}
    for f in filed:
        for d in f["blocked_by"]:
            try:
                gh("api", "-X", "POST", f"repos/{repo}/issues/{f['issue']}/dependencies/blocked_by", "-F", f"issue_id={by_story[d]['id']}")
            except subprocess.CalledProcessError:
                f.setdefault("link_failed", []).append(by_story[d]["issue"])
    return {"role": "split", "stage": None, "handback": {"stories": filed}, "check": {"passed": True, "problems": []}}


def build_record(role, stage, out, check_text, passed, meta):
    """This run's record: its hand-back, the code check's verdict and where it came from. Written by code, never the agent."""
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
    """The record of a run or command that failed before its agent started: what it tried to start and why it could not."""
    lines = [l.strip() for l in why.splitlines() if l.strip()] or ["A step before the agent failed; see the run for which."]
    return {"role": "not-started", "attempt": role or "command", "stage": stage or None, **meta, "handback": {},
            "check": {"passed": False, "problems": lines}}


def cancelled(role, stage, started, meta):
    """The record of a run someone cancelled: what it was and whether its agent had started. Nothing it handed back
    is used, and the river starts nothing after it."""
    return {"role": "cancelled", "attempt": role, "stage": stage or None, "agent_started": started, **meta,
            "handback": {}, "check": {"passed": False, "problems": []}}


def live_card(role, stage, state, ahead=None):
    """The run's card while it is still running: queued (or waiting for the run `ahead` of it), setting up, agent
    working since the agent started, then checking the hand-back.

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


def where_card(repo, number, role, stage):
    """Where a run's card and record go: the open pull request for the worker and the code review, else the issue."""
    pr = gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
            "-q", ".[0].number").strip()
    return pr if pr and (role == "worker" or stage == "pr") else str(number)


def run_ahead(repo, number):
    """The link of another run still going on the issue or its pull request, found from GitHub's records: a live card
    the bot put up there, which links its run, and GitHub's word that the run has not completed. None when there is none."""
    own = os.environ.get("GITHUB_RUN_ID", "")
    places = {str(number), where_card(repo, number, "worker", "")}
    for n in sorted(places):
        for c in json.loads(gh("api", f"repos/{repo}/issues/{n}/comments", "--paginate") or "[]"):
            body = c.get("body") or ""
            if (c.get("user") or {}).get("login") not in (BOT, f"{BOT}[bot]") or LIVE not in body or MARK in body:
                continue
            for rid in dict.fromkeys(re.findall(r"/actions/runs/(\d+)", body)):
                if rid == own:
                    continue
                if gh("api", f"repos/{repo}/actions/runs/{rid}", "--jq", ".status").strip() in GOING:
                    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{rid}"
    return None


def queue(role, stage, number, state):
    """Put up a run's queued card where its record will go, saying so when it waits for another run; returns its id."""
    repo = os.environ["GITHUB_REPOSITORY"]
    try:
        ahead = run_ahead(repo, number)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        ahead = None
    body = live_card(role, stage, state, ahead)
    return gh("api", "-X", "POST", f"repos/{repo}/issues/{where_card(repo, number, role, stage)}/comments",
              "-f", f"body={body}", "--jq", ".id").strip()


def role_icon(repo, role, stage):
    """The icon of the role a run is for, then a space; nothing for a run that is no agent's (a split or a command)."""
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
    """One line per item, drawn by `show`; non-dict items, and a malformed field that is no list, are shown as they are."""
    items = items if isinstance(items, list) else [items] if items not in (None, "", {}) else []
    return [f"- {show(x) if isinstance(x, dict) else x}" for x in items]


def pairs(d):
    """One line per key and value of a field that should be a dict; nothing when it is not."""
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
    """The long parts of a run's record, each in its own fold, drawn by the issue card's fold code.

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
                  ("Scope", bullets(h.get("scope"), str)), ("Out of scope", bullets(h.get("out_of_scope"), str)),
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
    """Where the owner said the words: the issue or comment link as given, or AGENTS.md on the repo's main branch."""
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
    """A readable transcript of the run's session: what the agent said, each tool it used and a cut of each result."""
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


def parent_of(repo, number):
    """The issue's parent number on GitHub; None when it has none or GitHub cannot say."""
    try:
        return json.loads(gh("api", f"repos/{repo}/issues/{number}/parent")).get("number")
    except Exception as e:  # noqa: BLE001 - any failure means GitHub did not say: no parent counts
        why = gh_reason(e) if isinstance(e, subprocess.CalledProcessError) else str(e)
        print(f"No parent issue of #{number} counts as a source: {why or 'GitHub named none'}", file=sys.stderr)
        return None


def parent_words(repo, number):
    """The parent issue's number, text and comments; None when none or GitHub cannot say."""
    up = parent_of(repo, number)
    if not up:
        return None
    try:
        d = json.loads(gh("issue", "view", str(up), "-R", repo, "--json", "number,body,comments"))
    except (subprocess.CalledProcessError, ValueError):
        return None
    return {"number": up, "body": d.get("body") or "", "comments": d.get("comments") or []}


def pack_parent(*dirs):
    """The parent number in parent.json of the first folder holding one, else None."""
    for d in dirs:
        path = os.path.join(d or "", "parent.json")
        if d and os.path.exists(path):
            try:
                n = json.load(open(path)).get("number")
            except (OSError, ValueError, AttributeError):
                return None
            return n if isinstance(n, int) and not isinstance(n, bool) and n > 0 else None
    return None


def owner_words(repo, number, d, items, owners):
    """Where the owner said things, as {link: text}: the issue's own ask, each code owner's comment, and the same on
    its parent issue. Every criterion of a plan must quote words found at its source link (#416)."""
    from dokima.body import ask
    mine = lambda c: (c.get("author") or {}).get("login") in owners and c.get("url")
    from dokima.body import STORY
    # A story split from a parent holds a planner's text, not the owner's: only the parent's ask counts as theirs.
    own = ask(d.get("body") or "")
    out = {} if STORY.match(own) else {issue_url(number): own}
    out.update({c["url"]: c.get("body") or "" for c in items if mine(c)})
    up = parent_words(repo, number)
    if up:
        out[issue_url(up["number"])] = ask(up["body"])
        out.update({c["url"]: c.get("body") or "" for c in up["comments"] if mine(c)})
    return out


def pack(repo, number, role, stage, dest):
    """Build the starting pack from GitHub's records: the issue and its PRs' conversation, every agent record so far,
    the open raises this role must answer (open_blockers.json), the newest passed plan, the issue's parent on GitHub (parent.json, naming none when it has none or GitHub cannot
    say) and, for the planner, every open issue of the repo. The pull request review also gets the worker's session log from its run."""
    d, items = conversation(repo, number)
    recs = records(items)
    listed = open_issues(repo) if role == "planner" else None
    os.makedirs(os.path.join(dest, "in"), exist_ok=True)
    json.dump({"number": parent_of(repo, number)}, open(os.path.join(dest, "parent.json"), "w"))
    if listed is not None:
        json.dump(listed, open(os.path.join(dest, "open_issues.json"), "w"), indent=1)
        owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
        json.dump(owner_words(repo, number, d, items, owners), open(os.path.join(dest, "owner_words.json"), "w"), indent=1)
    # The open raises this agent must answer; the file keeps the name the workflows give it.
    json.dump(raises_for(recs, role), open(os.path.join(dest, "open_blockers.json"), "w"), indent=1)
    open(os.path.join(dest, "issue.md"), "w").write(issue_text(d, items))
    # Each record keeps the link of the comment it was posted as, so a later run can say where a raise came from.
    urls = [c.get("url") for c in items if records([c])]
    for i, r in enumerate(recs, 1):
        name = name_of(r, i)
        if len(urls) == len(recs) and isinstance(urls[i - 1], str):
            r = {**r, "url": urls[i - 1]}
        json.dump(r, open(os.path.join(dest, "in", name), "w"), indent=1)
    plan = latest(recs, "planner")
    if role == "worker" and not approved(recs):
        return False
    if plan:
        json.dump(plan["handback"], open(os.path.join(dest, "plan.json"), "w"), indent=1)
    if stage == "pr":
        work = latest(recs, "worker", passed=False)
        if work and work.get("run_id"):
            gh("run", "download", str(work["run_id"]), "-R", repo, "-n", f"worker-{number}", "-D", os.path.join(dest, "worker-run"))
    return bool(plan)


def problems_review(r):
    """Everything wrong with a review.json, as plain sentences; empty when it is well formed."""
    bad = []
    if r.get("verdict") not in VERDICTS:
        bad.append("verdict must be approve, block or escalate")
    if not str(r.get("summary", "")).strip():
        bad.append("summary is empty")
    prev = r.get("previous_step")
    if not isinstance(prev, dict) or not any(prev.get(k) for k in ("did", "decided", "open")):
        bad.append("previous_step must sum up what the planner or worker did, decided and left open")
    elif sum(len(prev.get(k) or []) for k in ("did", "decided", "open")) > 5:
        bad.append("previous_step holds at most five lines")
    blocks = [x for x in r.get("raises") or [] if isinstance(x, dict) and x.get("kind") == "blocker"] \
        if isinstance(r.get("raises"), list) else []
    if r.get("verdict") == "approve" and blocks:
        bad.append("an approve raises no blocker")
    if r.get("verdict") == "block" and not blocks:
        bad.append("a block needs at least one blocker in raises")
    return bad


def problems_tests(r, plan):
    """A plan review must judge every test the plan names: does it check only its criterion's behavior, with the edge
    cases the owner named or normal use hits? A false one never approves."""
    named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if isinstance(ts, list) for t in ts})
    rows = r.get("tests") if isinstance(r.get("tests"), list) else []
    seen = {str(x.get("test")): x for x in rows if isinstance(x, dict)}
    bad = [f"tests has no judgment of `{t}`: say only_its_behavior true or false, and why in one line"
           for t in named if not (isinstance(seen.get(t, {}).get("only_its_behavior"), bool)
                                  and str(seen.get(t, {}).get("why") or "").strip())]
    wide = [t for t, x in seen.items() if x.get("only_its_behavior") is False]
    if wide and r.get("verdict") == "approve":
        bad.append(", ".join("`" + t + "`" for t in wide) + f" check more than their criterion's behavior, so the verdict cannot be approve")
    return bad


def problems_size(r, ids=()):
    """A plan review must judge each criterion one behavior or not, in `behaviors`, and say whether the plan keeps the
    size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks it; a plan that breaks
    it is never approved."""
    bad = []
    rows = r.get("behaviors") if isinstance(r.get("behaviors"), list) else []
    seen = {str(b.get("criterion")): b for b in rows if isinstance(b, dict)}
    for k in ids:
        b = seen.get(str(k))
        if not b or not isinstance(b.get("one_behavior"), bool) or not str(b.get("why") or "").strip():
            bad.append(f"behaviors has no judgment of criterion {k}: say one_behavior true or false, and why in one line")
    bundled = [k for k, b in seen.items() if b.get("one_behavior") is False]
    size = str(r.get("size") or "").strip()
    if bundled and size.lower() == "ok":
        bad.append(f"criteria {', '.join(bundled)} bundle more than one behavior, so size cannot be ok")
    if bad:
        return bad
    if not size:
        return ['size is empty: write "ok" if every story holds 1 to 3 criteria, each one behavior, in as few stories as '
                "the count needs; otherwise say which part breaks it"]
    if size.lower() != "ok" and r.get("verdict") == "approve":
        return [f"size says the plan breaks the size rule ({size}), so the verdict cannot be approve"]
    return []


def problems_asks(r, ids):
    """Everything wrong with a plan review's asks list: every ask the owner made, in their words, with a link to where
    they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an approve keeps every ask."""
    asks = r.get("asks")
    if not isinstance(asks, list) or not asks:
        return ["asks must list every ask in the owner's issue and comments, each {\"ask\": \"the owner's words\", "
                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
    good = [a for a in asks if isinstance(a, dict) and all(filled(a.get(k)) for k in ("ask", "source", "criterion"))]
    for a in good:
        c = a["criterion"].strip()
        if c != "missing" and c not in ids:
            bad.append(f"the ask \"{a['ask']}\" is matched to {c}, which is not a criterion of the plan "
                       f"({', '.join(ids) or 'none'})")
    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
    if r.get("verdict") == "approve" and gone:
        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
    return bad


def issue_url(number):
    """The link of the issue on GitHub."""
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{number}"


def owner_source(source, number, parent=None):
    """True when a source names owner's words Dokima can check.

    That is the issue's own text, its parent's (when given), one of their comments, or AGENTS.md."""
    return source == "AGENTS.md" or any(re.fullmatch(re.escape(issue_url(n)) + r"(#issuecomment-\d+)?", source)
                                        for n in ([number, parent] if parent else [number]))


def problems_work(w):
    """Everything wrong with a work.json, as plain sentences; empty when it is well formed."""
    bad = []
    if not str(w.get("summary", "")).strip():
        bad.append("summary is empty")
    if not isinstance(w.get("criteria"), dict) or not w["criteria"]:
        bad.append("criteria must give one line per criterion")
    if not str(w.get("evidence", "")).strip():
        bad.append("evidence is empty: name the last test command and its result line")
    return bad


def problems_old(h):
    """Each field retired by #300 the hand-back still holds, even empty, named."""
    return [f"{f} is a retired field: raise and answer only through raises and answers" for f in OLD_FIELDS if f in h]


def problems_raised(role, h):
    """Everything wrong with a hand-back's raises and answers, each raise checked against the table."""
    bad = raises.check_raises(role, h["raises"]) if "raises" in h else []
    if not isinstance(h.get("answers", []), list):
        bad.append("the answers must be a list, each {\"raise\": ID, \"answer\": \"done\" or \"disagree\", \"why\": ...}")
    else:
        bad += [f"answer {i} is not an object with raise, answer and why"
                for i, a in enumerate(h.get("answers", []), 1) if not isinstance(a, dict)]
    return bad


def filled(v):
    """True for a non-empty string."""
    return isinstance(v, str) and bool(v.strip())


def problems_items(h, field, keys, name=None):
    """Everything wrong with an optional list of objects that each need some non-empty text fields, naming the field."""
    v = h.get(field, [])
    if not isinstance(v, list):
        return [f"{field} must be a list"]
    bad = []
    for i, x in enumerate(v, 1):
        label = f"{field} item {i}" + (f" ({x.get(name)})" if name and isinstance(x, dict) and filled(x.get(name)) else "")
        if not isinstance(x, dict):
            bad.append(f"{label} must be an object with {', '.join(keys)}")
            continue
        missing = [k for k in keys if not filled(x.get(k))]
        if missing:
            bad.append(f"{label} needs {', '.join(missing)}")
    return bad


def problems_shape(kind, h):
    """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
    bad = problems_old(h) + problems_raised("reviewer" if kind == "review" else "worker", h)
    if kind == "review":
        prev = h.get("previous_step")
        if not isinstance(prev, dict):
            bad.append("previous_step must be an object with did, decided and open")
        elif not all(isinstance(prev.get(k, []), list) and all(filled(x) for x in prev.get(k, [])) for k in ("did", "decided", "open")):
            bad.append("previous_step: did, decided and open must each be a list of lines")
        if h.get("verdict") not in VERDICTS:
            bad.append("verdict must be approve, block or escalate")
        if not filled(h.get("summary")):
            bad.append("summary must be one non-empty sentence")
        return bad
    if not filled(h.get("summary")):
        bad.append("summary must be one non-empty sentence")
    crit = h.get("criteria")
    if not isinstance(crit, dict) or not crit:
        bad.append("criteria must be an object giving one line per criterion")
    else:
        bad += [f"criteria: the line for {k} must be non-empty text" for k, v in crit.items() if not filled(v)]
    if not filled(h.get("evidence")):
        bad.append("evidence must name the last test command and its result line")
    return bad


def plan_criteria(plan, number):
    """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each story of a split."""
    count = lambda p: sum(len(p.get(k)) for k in ("acceptance_criteria", "non_functional") if isinstance(p.get(k), list))
    if plan.get("kind") == "feature":
        stories = plan.get("stories") if isinstance(plan.get("stories"), list) else []
        return [f"S{s}.{k}" for s, st in enumerate(stories, 1) if isinstance(st, dict) for k in range(1, count(st) + 1)]
    return [f"{number}.{k}" for k in range(1, count(plan) + 1)]


def problems_plan(kind, h, plan, number):
    """Everything in a work.json that does not match the plan: one line per criterion."""
    ids = plan_criteria(plan, number)
    bad = []
    if kind == "work":
        crit = h.get("criteria")
        if isinstance(crit, dict):
            bad += [f"criteria has no line for {c}, a criterion of the plan" for c in ids if c not in crit]
            bad += [f"criteria gives a line for {c}, which the plan does not have" for c in crit if c not in ids]
    return bad


def load(path, name):
    """Read a JSON object from a file; return (object, None) or (None, the reason naming the file)."""
    try:
        data = json.load(open(path))
    except FileNotFoundError:
        return None, f"{name} is missing ({path})"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{name} is not valid JSON ({path}): {e}"
    if not isinstance(data, dict):
        return None, f"{name} is not a JSON object ({path})"
    return data, None


def check(kind, path, plan_path=None, number=None):
    """Check one hand-back file against its prompt's shape and, when given, the approved plan and the issue's number.
    Print every problem and return 1 if there are any, else 0."""
    data, err = load(path, os.path.basename(path))
    if err:
        print(err)
        return 1
    bad = problems_shape(kind, data) or (problems_review if kind == "review" else problems_work)(data)
    listed = []
    if filled(data.get("summary")):
        listed, too_long = words.summary_caps(data["summary"])
        bad += too_long
    more, too_long = words.style({k: v for k, v in data.items() if k != "summary"})
    listed, bad = listed + more, bad + too_long
    if kind == "work" and os.environ.get("PLANNER_BASE"):
        more, too_long = worker_docstring_caps(os.environ["PLANNER_BASE"])
        listed, bad = listed + more, bad + too_long
    if plan_path is not None:
        plan, err = load(plan_path, "plan.json")
        if err:
            bad.append(f"{err}: the hand-back can't be checked against the plan")
        elif not str(number or "").isdigit():
            bad.append(f"the issue number {number!r} is not a number: the hand-back can't be checked against the plan")
        else:
            bad += problems_plan(kind, data, plan, number)
            if kind == "review" and os.environ.get("STAGE") == "plan":
                bad += problems_asks(data, plan_criteria(plan, number))
                bad += problems_size(data, plan_criteria(plan, number))
                bad += problems_tests(data, plan)
    for line in listed + bad:
        print(line)
    return 1 if bad else 0


def worker_docstring_caps(base):
    """(listed, rejected) for each Python docstring added or rewritten since `base`.

    Older docstrings whose first line is unchanged are left alone; a base git cannot read fails closed.
    """
    from dokima import planner  # planner imports this module, so it is read only when needed
    try:
        paths = [p for p in planner.changed_files(base) if p.endswith(".py")]
    except subprocess.CalledProcessError as e:
        return [], [f"the docstrings the worker added can't be read: git can't compare with {base} ({e.stderr.strip()})"]
    return planner.docstring_caps(paths, planner.read_at(base), planner.read_now)


NEEDS = {
    "planner": ["issue.md"],
    "reviewer-plan": ["issue.md", "plan.json"],
    "worker": ["issue.md", "plan.json"],
    "reviewer-pr": ["issue.md", "plan.json", "diff.patch", "tests.txt", "tests.xml", "worker-run"],
}


def problems_pack(role, stage, dest):
    """Everything missing or broken in an agent's starting pack, checked by code before the agent starts."""
    key = f"{role}-{stage}" if role == "reviewer" else role
    if key not in NEEDS:
        return [f"unknown role {key}"]
    bad = []
    for name in NEEDS[key]:
        path = os.path.join(dest, name)
        if not os.path.exists(path):
            bad.append(f"{name} is missing")
        elif os.path.isdir(path) and not jsonl_files(path):
            bad.append(f"{name} holds no session log")
        elif os.path.isfile(path) and name != "diff.patch" and not open(path).read().strip():
            bad.append(f"{name} is empty")
    issue = os.path.join(dest, "issue.md")
    if os.path.exists(issue) and "## Comments" not in open(issue).read():
        bad.append("issue.md has no comments section")
    plan_path = os.path.join(dest, "plan.json")
    if key == "worker" and os.path.isfile(plan_path):
        try:
            if json.load(open(plan_path)).get("kind") == "feature":
                bad.append("plan.json is a split: /work files its stories as sub-issues, no worker builds it")
        except (json.JSONDecodeError, AttributeError):
            pass
    for name in ("plan.json",):
        path = os.path.join(dest, name)
        if os.path.isfile(path):
            try:
                if not isinstance(json.load(open(path)), dict):
                    bad.append(f"{name} is not a JSON object")
            except json.JSONDecodeError:
                bad.append(f"{name} is not valid JSON")
    for path in sorted(glob.glob(os.path.join(dest, "in", "*.json"))):
        try:
            r = json.load(open(path))
            if not {"role", "handback", "check"} <= set(r):
                bad.append(f"record {os.path.basename(path)} lacks role, handback or check")
        except json.JSONDecodeError:
            bad.append(f"record {os.path.basename(path)} is not valid JSON")
    if key == "reviewer-pr" and os.path.isfile(os.path.join(dest, "diff.patch")) and not open(os.path.join(dest, "diff.patch")).read().strip():
        bad.append("diff.patch is empty: there is no work to review")
    return bad


COMMANDS = {"/plan": "planner", "/work": "worker", "/review": "reviewer"}


def command_of(body):
    """The stage a comment starts: its first line's first word, when that word is a command; otherwise None."""
    first = (body or "").strip().splitlines()[0].split() if (body or "").strip() else []
    return COMMANDS.get(first[0].lower()) if first else None


def issue_of_pr(head, body):
    """The issue a pull request was built for: from its branch, else its closing line.

    The branch is work/issue-N or try/issue-N; the closing line is 'Closes' with the issue's full address or the old
    'Closes #N'."""
    m = re.match(r"(?:work|try)/issue-(\d+)$", head or "") or re.search(
        r"(?i)\b(?:closes|fixes|resolves) (?:#|https://github\.com/[\w.-]+/[\w.-]+/issues/)(\d+)\b", body or "")
    return m.group(1) if m else None


def autopilot_of(body):
    """"start" or "stop" when a comment's first line begins `/autopilot start` or `/autopilot stop`; otherwise None."""
    first = (body or "").strip().splitlines()[0].split() if (body or "").strip() else []
    if len(first) >= 2 and first[0].lower() == "/autopilot" and first[1].lower() in ("start", "stop"):
        return first[1].lower()
    return None


def route(body, on_pr, number, head="", pr_body=""):
    """What a code owner's comment starts: {role, stage, issue}, or None when it starts nothing.

    /review on an issue grades the plan; on a pull request it grades the work. A pull request routes to its issue.
    `/autopilot start|stop` starts no stage: it routes to {autopilot, issue}, the issue whose tree it switches."""
    role, switch = command_of(body), autopilot_of(body)
    if not role and not switch:
        return None
    issue = issue_of_pr(head, pr_body) if on_pr else str(number)
    if not issue:
        return None
    if switch:
        return {"autopilot": switch, "issue": issue}
    stage = ("pr" if on_pr else "plan") if role == "reviewer" else ""
    return {"role": role, "stage": stage, "issue": issue}


AUTOPILOT = "autopilot"


def issue_tree(repo, number):
    """The issue and every sub-issue under it, at every level, from GitHub's native sub-issues; parents first."""
    tree, todo = [], [int(number)]
    while todo:
        n = todo.pop(0)
        if n in tree:
            continue
        tree.append(n)
        # GitHub allows at most 100 sub-issues per parent, so one page holds them all.
        todo += [c["number"] for c in json.loads(gh("api", f"repos/{repo}/issues/{n}/sub_issues?per_page=100") or "[]")]
    return tree


def switch_autopilot(repo, number, switch):
    """Put the issue's tree on autopilot ("start") or take it off ("stop"), touching no other label; returns the
    issues switched: those whose `autopilot` label was added or removed."""
    switched = []
    for n in issue_tree(repo, number):
        labels = {l["name"] for l in json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("labels", [])}
        if switch == "start" and AUTOPILOT not in labels:
            # Adding a label GitHub does not have yet creates it.
            gh("api", "-X", "POST", f"repos/{repo}/issues/{n}/labels", "-f", f"labels[]={AUTOPILOT}")
            switched.append(n)
        elif switch == "stop" and AUTOPILOT in labels:
            gh("api", "-X", "DELETE", f"repos/{repo}/issues/{n}/labels/{AUTOPILOT}")
            switched.append(n)
    return switched


def autopilot_comment(number, switch, switched, started=(), picked=""):
    """The one comment `/autopilot start|stop` leaves where it was said: every issue it switched, every issue whose
    planner it started, and what of the issue's own waiting work it picked up."""
    names = ", ".join(f"#{n}" for n in switched)
    if switch == "start":
        said = f"Autopilot is on for {names}." if switched else f"#{number} and every issue under it were already on autopilot."
    else:
        said = f"Autopilot is off for {names}." if switched else f"No issue in #{number}'s tree was on autopilot."
    if started:
        said += f" Planning started for {', '.join(f'#{n}' for n in started)}, which wait on nothing open."
    if picked:
        said += f" {picked}"
    return said + ("\n" if started or picked else " No stage was started.\n")


AUTOPILOT_LINE = "Autopilot: blockers merged, starting plan"
AUTOPILOT_START_LINE = "Autopilot: switched on, starting plan"


def sub_issues(repo, number):
    """The issue's own sub-issues, one level down, each with its state."""
    # GitHub allows at most 100 sub-issues per parent, so one page holds them all.
    return json.loads(gh("api", f"repos/{repo}/issues/{number}/sub_issues?per_page=100") or "[]")


def blocked_by(repo, number):
    """The issues blocking this one, from GitHub's native blocked-by links, each with its state."""
    return json.loads(gh("api", f"repos/{repo}/issues/{number}/dependencies/blocked_by", "--paginate") or "[]")


def link_edges(number, links):
    """A plan's blocking links as GitHub's blocked-by links: (the issue blocked, the issue blocking it)."""
    n = int(number)
    return {(n, b) for b in links["blocked_by"]} | {(x, n) for x in links["blocks"]}


def loop_through(add, drop, has):
    """The issues that would block each other after `add` and `drop`; [] when none.

    `has(i)` gives what GitHub has issue i blocked by. A new link a blocked by b closes a loop when b is already
    blocked, directly or through other issues, by a.
    """
    def blockers(i):
        return (set(has(i)) - {b for a, b in drop if a == i}) | {b for a, b in add if a == i}
    for a, b in add:
        stack, seen = [[b]], set()
        while stack:
            path = stack.pop()
            if path[-1] == a:
                return path
            if path[-1] in seen:
                continue
            seen.add(path[-1])
            stack += [path + [c] for c in sorted(blockers(path[-1]))]
    return []


def named(numbers):
    """Issue numbers as words: #1, #2 and #3."""
    ns = [f"#{n}" for n in numbers]
    return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]


def gh_reason(e):
    """GitHub's own words for a call that failed, on one line."""
    return " ".join((e.stderr or str(e)).split())


def first_sentence(text):
    """A raise's first sentence, on one line, as a filed issue's title."""
    text = escape_line(text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:250]


def file_issues(repo, number, rec, recs):
    """File every issue raise a passed review confirms as its own GitHub issue.

    It confirms its own, and each the planner or the worker raised that it answers done; `recs` are the records
    before it. Returns the record's lines naming each filed issue, or the finding and GitHub's reason when GitHub
    refuses it; a refusal never stops the run."""
    h = rec.get("handback") or {}
    if rec.get("role") != "reviewer" or not (rec.get("check") or {}).get("passed"):
        return []
    found = [x for x in card.raises_of(h) if x.get("kind") == "issue"]
    theirs = {x["id"]: x for x in open_raises(recs) if x.get("kind") == "issue" and raises.sent_to(x) == raises.CONFIRMS}
    found += [theirs[a["raise"]] for a in card.answers_of(h)
              if a.get("answer") == "done" and isinstance(a["raise"], str) and a["raise"] in theirs]
    lines = []
    for x in found:
        title = first_sentence(x.get("text") or x.get("label") or "An issue found")
        by = x.get("raised_by") or "reviewer"
        who = "The reviewer found it" if by == "reviewer" else f"The {by} raised it and the reviewer confirmed it"
        body = [x.get("text") or ""] + (["", f"**Evidence:** {x['evidence']}"] if filled(x.get("evidence")) else [])
        body += ["", f"{who} on #{number}."]
        try:
            url = gh("issue", "create", "-R", repo, "--title", title, "--body", "\n".join(body)).strip()
        except subprocess.CalledProcessError as e:
            lines.append(f"- Not filed: {card.escape(title)} GitHub refused it: {card.escape(gh_reason(e))}")
            continue
        n = url.rstrip("/").rsplit("/", 1)[-1]
        lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), n)} · the reviewer confirmed it")
    return ["", f"{field_icon(os.environ.get('GITHUB_REPOSITORY', ''), 'issue found')} **Filed as issues:**", ""] + lines \
        if lines else []


def record_links(repo, number, items):
    """Record the just approved plan's links on GitHub, then redraw the cards they touch.

    Code reads the plan from the issue's checked records only. Its blocked_by links become GitHub's own blocked-by
    links on this issue and its blocks links the other issue blocked by this one; a link GitHub already has is not
    added again, and a blocking link the previous approved plan had and this one dropped is removed first. A link
    no approved plan had, such as one a person made by hand, is left alone. Links that would make issues block each
    other record nothing. Then the card of this issue and of every issue a link was added to, dropped from or
    changed on is redrawn. Returns why the river must stop for the owner, or None when all went through.
    """
    recs = records(items)
    n = int(number)
    new, old = plan_links(latest(recs, "planner")), plan_links(approved_plan(recs))
    want, had = link_edges(n, new), link_edges(n, old)
    after = " Nothing starts by itself: fix it, then say `/work`, or `/plan` with changes."
    known = {}

    def has(i):
        if i not in known:
            known[i] = {b["number"]: b["id"] for b in blocked_by(repo, i)}
        return known[i]
    try:
        drop = [(a, b) for a, b in sorted(had - want) if b in has(a)]
        add = [(a, b) for a, b in sorted(want) if b not in has(a)]
        loop = loop_through(add, drop, has)
    except subprocess.CalledProcessError as e:
        return f"GitHub could not say which blocked-by links it has, so code recorded none of the plan's links: {gh_reason(e)}.{after}"
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return f"GitHub's blocked-by links could not be read, so code recorded none of the plan's links: {e}.{after}"
    if loop:
        return (f"The plan's links would make {named(sorted(set(loop)))} block each other, so code recorded none of "
                f"them.{after}")
    failed = []
    for a, b in drop:
        try:
            gh("api", "-X", "DELETE", f"repos/{repo}/issues/{a}/dependencies/blocked_by/{known[a][b]}")
        except subprocess.CalledProcessError as e:
            failed.append(f"GitHub failed to remove the link #{a} blocked by #{b}: {gh_reason(e)}.")
    if failed:
        # A link turned around is removed before it is added the other way, so nothing is added after a failure.
        return " ".join(failed) + " Code added none of the plan's new links." + after
    for a, b in add:
        try:
            node = json.loads(gh("api", f"repos/{repo}/issues/{b}"))["id"]
            gh("api", "-X", "POST", f"repos/{repo}/issues/{a}/dependencies/blocked_by", "-F", f"issue_id={node}")
        except subprocess.CalledProcessError as e:
            failed.append(f"GitHub refused to record the link #{a} blocked by #{b}: {gh_reason(e)}.")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            failed.append(f"GitHub's answer for #{b} could not be read, so #{a} blocked by #{b} was not recorded: {e}.")
    if failed:
        return " ".join(failed) + after
    side = lambda links: {m: k for k in LINKS for m in links[k]}
    now, before = side(new), side(old)
    changed = sorted(m for m in set(now) | set(before) if now.get(m) != before.get(m))
    for m in [n] + changed if changed else []:
        try:
            # The card's own progress lines go to the run's log, so this step's output stays the river's decision.
            with contextlib.redirect_stdout(sys.stderr):
                card.draw(repo, m, card.issue_pr(repo, m), plans={n: new}, noted={n: m in now} if m != n else None)
        except subprocess.CalledProcessError as e:
            failed.append(f"The links are recorded, but the card of #{m} could not be redrawn: {gh_reason(e)}.")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            failed.append(f"The links are recorded, but the card of #{m} could not be redrawn: {e}.")
    return " ".join(failed) + after if failed else None


PUSH_EVENTS = ("pull_request", "pull_request_target", "push")
NO_PERMISSION = "Resource not accessible by integration"


def installations_link(repo):
    """Where the repo's owner accepts the app's new permissions: the organization's or the account's page."""
    owner = repo.split("/")[0]
    kind = gh("api", f"users/{owner}", "-q", ".type").strip()
    if kind == "Organization":
        return f"https://github.com/organizations/{owner}/settings/installations"
    return "https://github.com/settings/installations"


def stop_run(repo, rid, polls=60, pause=5):
    """Stop a run still going and wait until it ends.

    Returns None, or why it did not end."""
    gh("api", "-X", "POST", f"repos/{repo}/actions/runs/{rid}/cancel")
    for i in range(polls):
        if json.loads(gh("api", f"repos/{repo}/actions/runs/{rid}")).get("status") == "completed":
            return None
        time.sleep(pause)
    return f"it was still running {polls * pause} seconds after it was stopped"


def rerun_checks(repo, number):
    """Run every check on the open pull request's head again, in full, after approval.

    A check reads the issue's records only when the pull request gets a new commit, so an approval with nothing new to
    push would keep checks that ran before it. Only the newest run of each workflow a push to the current head started
    runs again, once; one still going is stopped first, since it may have read the plan before its approval. Runs on
    older commits and runs a review, a comment or another workflow started are left alone. With no open pull request
    nothing runs. A refusal for lack of permission gets one comment naming the app's setting; any other gets one
    comment with GitHub's own words. Returns what happened, one line."""
    pr = gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
            "-q", ".[0].number").strip()
    if not pr.isdigit():
        return "No open pull request: no check to run again."
    sha = gh("pr", "view", pr, "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip()
    found = json.loads(gh("api", f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100"))
    newest = {}
    for r in found.get("workflow_runs") or []:
        if r.get("head_sha") != sha or r.get("event") not in PUSH_EVENTS:
            continue
        key = r.get("workflow_id") or r.get("path") or r.get("name")
        if key not in newest or r["id"] > newest[key]["id"]:
            newest[key] = r
    if not newest:
        return f"PR #{pr} has no check on {sha[:7]} yet: GitHub runs them on the next push."
    ran, denied, refused = [], [], []
    for run in sorted(newest.values(), key=lambda r: r["id"]):
        name = run.get("name") or run.get("path") or str(run["id"])
        url = run.get("html_url") or f"https://github.com/{repo}/actions/runs/{run['id']}"
        try:
            why = stop_run(repo, run["id"]) if run.get("status") != "completed" else None
            if why is None:
                gh("api", "-X", "POST", f"repos/{repo}/actions/runs/{run['id']}/rerun")
                ran.append(name)
                continue
        except subprocess.CalledProcessError as e:
            why = gh_reason(e)
            if NO_PERMISSION in why:
                denied.append(name)
                continue
        refused.append(f"- {name} ({url}): {why}")
    if denied:
        gh("pr", "comment", pr, "-R", repo, "--body",
           f"The plan of #{number} is approved, but GitHub refused to run its checks on {sha[:7]} again: Dokima's GitHub "
           f"App may not re-run workflows. Set the app's Actions permission to Read and write, then accept the new "
           f"permission on its installation: {installations_link(repo)}")
    if refused:
        gh("pr", "comment", pr, "-R", repo, "--body",
           f"The plan of #{number} is approved, but these checks on {sha[:7]} could not run again, in GitHub's own "
           f"words:\n\n" + "\n".join(refused))
    did = f"Ran {len(ran)} check(s) on {sha[:7]} of PR #{pr} again"
    if denied or refused:
        did += f"; {len(denied) + len(refused)} could not run again, and PR #{pr} says why"
    return did + "."


def started_before(repo, number):
    """True when GitHub's records show something already started on the issue: a record, a live card or an Autopilot
    line the bot posted there. A planned, running or finished issue is never started again."""
    d = json.loads(gh("issue", "view", str(number), "-R", repo, "--json", "comments"))
    for c in d.get("comments") or []:
        body = c.get("body") or ""
        if (c.get("author") or {}).get("login") in (BOT, f"{BOT}[bot]") and (
                MARK in body or LIVE in body or body.strip() in (AUTOPILOT_LINE, AUTOPILOT_START_LINE)):
            return True
    return False


def start_planner(repo, number, line=AUTOPILOT_LINE):
    """Start the issue's planner with the river's own signal, after one Autopilot line where the owner would have said /plan.

    The line goes first: it is the record that this issue was started, so no later close starts it again."""
    gh("issue", "comment", str(number), "-R", repo, "--body", line)
    gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next", "-f", "client_payload[role]=planner",
       "-f", "client_payload[stage]=plan", "-f", f"client_payload[issue]={number}")


def start_waiting(repo, numbers, line=AUTOPILOT_LINE):
    """Start the planner of every open issue among `numbers` with no sub-issues, nothing open blocking it and nothing
    started on it yet. Returns those started."""
    started = []
    for n in numbers:
        if json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("state") != "open" or sub_issues(repo, n):
            continue
        blockers = blocked_by(repo, n)
        if any(b.get("state") != "closed" for b in blockers):
            continue
        if started_before(repo, n):
            continue
        start_planner(repo, n, line)
        started.append(n)
    return started


def open_blockers_of(repo, number):
    """The numbers of the open issues blocking this one on GitHub, oldest first."""
    return sorted(b["number"] for b in blocked_by(repo, number) if b.get("state") != "closed")


def plans_again(items, owners, body, number):
    """True when a plan approved while blocked built nothing and nothing started since.

    Its newest record is the approving plan review, and since then no record, run card or Autopilot line started a
    stage and the owner gave no command."""
    at = max((i for i, c in enumerate(items) if is_record(c)), default=None)
    if at is None or not is_record(items[at], "reviewer", "plan"):
        return False
    rec = records([items[at]])[0]
    if not rec.get("check", {}).get("passed") or (rec.get("handback") or {}).get("verdict") != "approve":
        return False
    lines = (AUTOPILOT_LINE, AUTOPILOT_START_LINE, *AUTOPILOT_LINES.values())
    for c in items[at + 1:]:
        who, said = (c.get("author") or {}).get("login"), (c.get("body") or "").strip()
        if (who in owners and command_of(said)) or (who in (BOT, f"{BOT}[bot]") and (LIVE in said or said in lines)):
            return False
    step = next_step(items[:at], rec, owners, autopilot=lambda: True, body=body, number=number)
    return step[:2] == ("start", "worker") and step[3:] == ("autopilot",)


def start_unblocked(repo, numbers, owners):
    """Start a fresh planner on every issue among `numbers` whose blockers have all closed.

    Each was blocked, and has nothing started on it yet or a plan approved while it was blocked; its old plan's worker
    never starts. Returns (the issues started, what was done as lines). When GitHub cannot list an issue's blockers nothing
    starts and the issue says why."""
    started, did = [], []
    for n in numbers:
        if started_before(repo, n):
            d, items = conversation(repo, n)
            if not plans_again(items, owners, d.get("body") or "", n):
                continue
        try:
            blockers = blocked_by(repo, n)
        except subprocess.CalledProcessError as e:
            gh("issue", "comment", str(n), "-R", repo, "--body",
               f"Autopilot did not start the planner: GitHub could not list the issues blocking #{n}: {gh_reason(e)}.")
            did.append(f"could not list the blockers of #{n}")
            continue
        if blockers and all(b.get("state") == "closed" for b in blockers):
            start_planner(repo, n)
            started.append(n)
            did.append(f"started the planner for #{n}")
    return started, did


def tree_done_comment(number):
    """The comment a parent closes with when its last sub-issue closed, on autopilot or not."""
    return f"Every issue under #{number} is closed, so its whole tree is done and it closes.\n"


def close_if_done(repo, number):
    """Close the open issue as completed when every sub-issue under it is closed.

    It says its tree is done; a sub-issue closed as not planned counts as done. True when it closed it; an issue
    already closed is left alone."""
    if json.loads(gh("api", f"repos/{repo}/issues/{number}")).get("state") != "open":
        return False
    subs = sub_issues(repo, number)
    if not subs or any(c.get("state") != "closed" for c in subs):
        return False
    gh("issue", "close", str(number), "-R", repo, "--reason", "completed", "--comment", tree_done_comment(number))
    return True


def close_done_parents(repo, number):
    """Close the closed issue's parent when that was its last open sub-issue, in turn.

    On autopilot or not. Returns what it did, as lines."""
    did, n = [], int(number)
    while True:
        up = json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("parent_issue_url")
        if not up:
            return did
        n = int(up.rstrip("/").rsplit("/", 1)[-1])
        if not close_if_done(repo, n):
            return did
        did.append(f"closed #{n}: its whole tree is done")


def close_done_trees(repo):
    """Close every open parent whose sub-issues are all closed, one level up in turn.

    So a close whose run never went leaves no finished parent open. Returns what it did, as lines."""
    did = []
    while True:
        items = [i for p in pages(gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
        # GitHub counts each issue's sub-issues, open or closed, so only a parent is asked about them.
        parents = [i["number"] for i in items if "pull_request" not in i and (i.get("sub_issues_summary") or {}).get("total")]
        closed = [n for n in parents if close_if_done(repo, n)]
        did += [f"closed #{n}: its whole tree is done" for n in closed]
        if not closed:
            return did


def autopilot_closed(repo):
    """What autopilot does when an issue closes, worked out from GitHub's state of every issue on autopilot, so a close
    whose own run never went is still handled by the next one. Returns what it did, as lines.

    Every open parent on autopilot whose sub-issues are all closed closes as completed, saying its tree is done, and
    counts as a close one level up in turn. Every closed issue on autopilot with no parent on autopilot is the top of a
    done tree: the tree goes off autopilot. Then every open issue left on autopilot that was blocked and whose blockers
    have all closed starts a fresh planner, unless something already started on it since its plan, if any, was approved."""
    did = []
    while True:
        issues = {i["number"]: i for i in json.loads(gh(
            "api", f"repos/{repo}/issues?labels={AUTOPILOT}&state=all&per_page=100", "--paginate") or "[]")
            if "pull_request" not in i}
        subs = {n: sub_issues(repo, n) for n in sorted(issues)}
        done = [p for p, cs in subs.items() if cs and issues[p]["state"] == "open" and all(c["state"] == "closed" for c in cs)]
        if not done:
            break
        for p in done:
            gh("issue", "close", str(p), "-R", repo, "--reason", "completed", "--comment", tree_done_comment(p))
            did.append(f"closed #{p}: its whole tree is done")
    under = {c["number"] for cs in subs.values() for c in cs}
    off = set()
    for n in sorted(issues):
        if issues[n]["state"] == "closed" and n not in under:
            switched = switch_autopilot(repo, n, "stop")
            off |= set(switched)
            if switched:
                did.append("autopilot off for " + ", ".join(f"#{m}" for m in switched))
    waiting = [n for n in sorted(issues) if n not in off and issues[n]["state"] == "open" and not subs[n]]
    from dokima.plan import repo_approvers
    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o] or \
        sorted(repo_approvers(os.environ.get("GITHUB_REPOSITORY_OWNER", repo.split("/")[0])))
    # A plan approved while the issue was blocked built nothing, so the issue plans afresh.
    did += start_unblocked(repo, waiting, owners)[1]
    return did


AUTOPILOT_LINES = {"worker": "Autopilot: plan approved, starting work", "split": "Autopilot: split approved, filing its stories"}
UNREAD = "Autopilot could not be read from GitHub, so nothing starts by itself."


def on_autopilot(repo, number):
    """True or False from the issue's own labels on GitHub; None when GitHub cannot say."""
    try:
        labels = json.loads(gh("api", f"repos/{repo}/issues/{number}")).get("labels")
    except (subprocess.CalledProcessError, json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(labels, list):
        return None
    return any((l.get("name") if isinstance(l, dict) else l) == AUTOPILOT for l in labels)


WORKFLOWS = ".github/workflows/"
PASSING = {"success", "neutral", "skipped"}


def approves_work(rec):
    """True when a passed code review approves the pull request, raising nothing for the owner."""
    return (rec.get("role") == "reviewer" and (rec.get("stage") or "") == "pr" and bool(rec.get("check", {}).get("passed"))
            and (rec.get("handback") or {}).get("verdict") == "approve" and not owner_raises(rec.get("handback") or {}))


def work_approved(recs):
    """True when the issue's newest planner, worker or reviewer record is a code review approving the pull request."""
    at = next((i for i in range(len(recs) - 1, -1, -1) if recs[i].get("role") in HANDBACK), None)
    # A review that settled a worker's raise sends the work on to an agent, so it merges nothing.
    return at is not None and approves_work(recs[at]) and not settled(recs[:at], recs[at].get("handback") or {})


def pages(text):
    """Every JSON page `gh api --paginate` printed back to back."""
    out, at, dec = [], 0, json.JSONDecoder()
    while text[at:].strip():
        at += len(text[at:]) - len(text[at:].lstrip())
        page, at = dec.raw_decode(text, at)
        out.append(page)
    return out


def unproven(repo, sha):
    """Why the commit is not proven by every check on it, check runs and commit statuses alike, or None when every
    check on it has passed."""
    runs = [r for p in pages(gh("api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100", "--paginate"))
            for r in p.get("check_runs", [])]
    statuses = [s for p in pages(gh("api", f"repos/{repo}/commits/{sha}/status?per_page=100", "--paginate"))
                for s in p.get("statuses") or []]
    if not runs and not statuses:
        return f"there are no checks on its head commit {sha[:7]}"
    red = [f"{r['name']} ({r.get('conclusion')})" for r in runs if r.get("status") == "completed" and r.get("conclusion") not in PASSING]
    red += [f"{s.get('context')} ({s.get('state')})" for s in statuses if s.get("state") not in ("success", "pending")]
    running = [r["name"] for r in runs if r.get("status") != "completed"]
    running += [s.get("context") for s in statuses if s.get("state") == "pending"]
    if red:
        return f"not every check passed on its head commit {sha[:7]}: {', '.join(red)}"
    if running:
        return f"a check is still running on its head commit {sha[:7]}: {', '.join(running)}"
    return None


def try_merge(repo, pr):
    """Merge the pull request at the head whose checks were read, only when it changes no workflow file and every
    check on that head has passed. Returns (True, the merged head) or (False, why not, in GitHub's words when GitHub
    refused)."""
    try:
        files = [f["filename"] for p in pages(gh("api", f"repos/{repo}/pulls/{pr}/files?per_page=100", "--paginate")) for f in p]
        flows = [f for f in files if f.startswith(WORKFLOWS)]
        if flows:
            return False, f"it changes a workflow file ({', '.join(flows)}), and only the owner merges those"
        head = gh("pr", "view", str(pr), "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip()
        if not head:
            return False, "GitHub did not say which commit is its head"
        why = unproven(repo, head)
        if why:
            return False, why
        # Pinned to the head whose checks passed: a commit pushed since makes GitHub refuse.
        gh("pr", "merge", str(pr), "-R", repo, "--squash", "--match-head-commit", head)
        return True, head
    except subprocess.CalledProcessError as e:
        return False, " ".join((e.stderr or str(e)).split())
    except (json.JSONDecodeError, AttributeError, KeyError, TypeError) as e:
        return False, f"GitHub's answer could not be read: {e}"


def open_pr(repo, number):
    """The number of the open pull request built for the issue, or ''."""
    return gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
              "-q", ".[0].number").strip()


AUTOPILOT_MERGE = {"merged": "Autopilot: merged PR #{pr}", "queued": "Autopilot: PR #{pr} joined the merge queue",
                   "waits": "Autopilot: PR #{pr} waits for your approval before it merges"}


def merge_outcome(repo, pr):
    """What GitHub reports after a merge it took, read from the pull request.

    ("merged" | "queued" | "waits", "") or ("unconfirmed", why, in GitHub's words when it gave any). `gh pr merge` exits 0 when it only queues the pull request or turns on
    auto-merge, so only GitHub's own state says whether it merged."""
    try:
        st = json.loads(gh("pr", "view", str(pr), "-R", repo, "--json",
                           "state,isInMergeQueue,autoMergeRequest,reviewDecision,mergeStateStatus"))
    except subprocess.CalledProcessError as e:
        return "unconfirmed", f"GitHub could not say whether it merged: {gh_reason(e)}"
    except (json.JSONDecodeError, TypeError) as e:
        return "unconfirmed", f"GitHub's answer on whether it merged could not be read: {e}"
    if not isinstance(st, dict):
        return "unconfirmed", "GitHub's answer on whether it merged could not be read"
    if st.get("state") == "MERGED":
        return "merged", ""
    if st.get("isInMergeQueue"):
        return "queued", ""
    if st.get("autoMergeRequest") and st.get("reviewDecision") == "REVIEW_REQUIRED":
        return "waits", ""
    return "unconfirmed", (f"GitHub took the merge but reports it {str(st.get('state') or 'unknown').lower()}, "
                           f"not merged, not in the merge queue and not waiting on a review "
                           f"(merge state {st.get('mergeStateStatus') or 'unknown'})")


def automerge(repo, number):
    """On autopilot, merge the open pull request built for the issue.

    Once GitHub reports it merged, queued or waiting for the owner's approval, the issue gets that one Autopilot line. Returns (pull request or '', how, why): how is
    "merged", "queued" or "waits"; "unconfirmed" when GitHub took the merge but cannot confirm it, or '' when the
    merge was not made, each with why."""
    try:
        pr = open_pr(repo, number)
    except subprocess.CalledProcessError as e:
        return "", "", " ".join((e.stderr or str(e)).split())
    if not pr:
        return "", "", "there is no open pull request built for it"
    asked, why = try_merge(repo, pr)
    if not asked:
        return pr, "", why
    how, why = merge_outcome(repo, pr)
    if how in AUTOPILOT_MERGE:
        gh("issue", "comment", str(number), "-R", repo, "--body", AUTOPILOT_MERGE[how].format(pr=pr))
    return pr, how, why


def unconfirmed_comment(repo, pr, why, mention):
    """Says on the pull request that autopilot cannot confirm its merge, mentioning the owner."""
    gh("pr", "comment", str(pr), "-R", repo, "--body",
       f"Autopilot could not confirm this pull request merged: {why}. {mention} Check it on GitHub and merge it if it "
       f"did not merge.".replace("  ", " "))


def merge_tree(repo, number, owners):
    """`/autopilot start`: merge every open pull request in the issue's tree whose newest record is its code review's
    approval. One that cannot merge says why on itself and mentions the owner. Returns what merged, as (issue, pr)."""
    done, mention = [], " ".join(f"@{o}" for o in owners)
    for n in issue_tree(repo, number):
        if not open_pr(repo, n) or not work_approved(records(conversation(repo, n)[1])):
            continue
        pr, how, why = automerge(repo, n)
        if how == "merged":
            done.append((n, pr))
        elif how == "unconfirmed":
            unconfirmed_comment(repo, pr, why, mention)
        elif pr and not how:
            gh("pr", "comment", pr, "-R", repo, "--body",
               f"Autopilot did not merge this pull request: {why}. {mention} It waits for you to merge it.".replace("  ", " "))
    return done


def agents_text():
    """AGENTS.md as the runtime has it, from main; empty when there is none."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AGENTS.md")
    try:
        return open(path).read()
    except OSError:
        return ""


def said_there(words, source, items, body, owners, number, parent=None):
    """True when the words appear word for word where the source says: the issue's own text, a code owner's comment on
    this issue, or AGENTS.md; given the parent (parent_words), also the parent's own text or a code owner's comment on
    it. Anything else, a comment by anyone else (the bot included) or one not found, is False."""
    flat = lambda t: " ".join((t or "").split())
    words, source = flat(words), (source or "").strip()
    up = (parent or {}).get("number")
    if not words or not owner_source(source, number, up):
        return False
    if source == "AGENTS.md":
        return words in flat(agents_text())
    from dokima.body import ask
    if source == issue_url(number):
        return words in flat(ask(body))
    if up and source == issue_url(up):
        return words in flat(ask(parent.get("body") or ""))
    comments = items + ((parent.get("comments") or []) if up else [])
    return any(c.get("url") == source and (c.get("author") or {}).get("login") in owners and words in flat(c.get("body"))
               for c in comments)


def not_accepted(items, h, owners, body, number, parent=lambda: None):
    """The questions of the reviewed plan whose assumption the review did not accept on the owner's real words.
    `parent()` gives the parent's words (parent_words), read only when an assumption cites somewhere else."""
    plan = latest(records(items), "planner")
    qs = [q.get("question") for q in ((plan or {}).get("handback") or {}).get("questions") or [] if isinstance(q, dict)]
    up = lambda a: None if owner_source((a.get("source") or "").strip(), number) else parent()
    ok = {a.get("question") for a in h.get("assumptions") or [] if isinstance(a, dict) and a.get("accepted") is True
          and a.get("changes") is False and said_there(a.get("matched"), a.get("source"), items, body, owners, number, up(a))}
    return [q for q in qs if q not in ok]


def quoted(raised):
    """The texts of raises, each in quotes, for a Next line."""
    return " ".join(f"\"{r.get('text', '')}\"" for r in raised)


def unanswered(asked, items, h, owners, body, number, parent=lambda: None):
    """The plan's questions for the owner the review did not settle on their real words.

    A question is settled when the review answers its ID done, says the reading changes neither how the system works
    nor what it costs, and quotes words the owner really said where its source says."""
    up = lambda a: None if owner_source((a.get("source") or "").strip(), number) else parent()
    by = {a["raise"]: a for a in card.answers_of(h)}
    ok = lambda a: a.get("answer") == "done" and a.get("changes") is False and \
        said_there(a.get("words"), a.get("source"), items, body, owners, number, up(a))
    return [r.get("text", "") for r in asked if not (r.get("id") in by and ok(by[r["id"]]))]


def clash_pending(recs):
    """True when the newest clash record has no worker record after it.

    The clash was sent back and is not rebuilt yet."""
    at = max((i for i, r in enumerate(recs) if r.get("role") == "updater"), default=None)
    return at is not None and not any(r.get("role") == "worker" for r in recs[at + 1:])


# More questions for the owner than this and a plan is not ready: it stops for the owner, whatever else says go.
MAX_QUESTIONS = 3


def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
    """The river: what follows the run that just finished. ("start", role, stage) or ("stop", why), decided by code.

    The river routes by raises. A planner hands to the reviewer unless it raises a blocker for the owner, or has
    questions for the owner and the issue is not on autopilot. A worker hands to the reviewer. A review raising a
    question or a blocker for the owner stops. A blocking review sends the work back to the agent its blockers name
    (any blocker for the planner sends it to the planner), until three blocks in a row at that stage since the owner
    last spoke; then it is the owner's call. On autopilot (`autopilot()` says, None when GitHub cannot), an approved
    plan goes to the worker and an approved split is filed, each ("start", role, stage, "autopilot"), once the plan
    reviewer answered every question of the plan done, changing nothing, on the owner's real words, in the issue or,
    as `parent()` gives them, its parent (a plan posted before #300: accepted every assumption); any other stops.
    Otherwise an approval, a question, an escalation or a hand-back code rejected always stops for the owner. A
    cancelled run starts nothing and mentions no one: whoever cancelled it knows."""
    role, stage, h = rec.get("role"), rec.get("stage") or "", rec.get("handback") or {}
    if role == "cancelled":
        return ("cancelled", "Nothing starts by itself after a cancel. Give the command again to start this stage.")
    if role == "not-started":
        return ("stop", "Nothing ran, see why above. Fix the cause, then give the command again.")
    if not rec.get("check", {}).get("passed"):
        return ("stop", "The hand-back was rejected by code, see the problems above. Fix the cause, then start the stage again.")
    if role == "planner":
        stops = [r for r in owner_raises(h) if r.get("kind") == "blocker"]
        if stops:
            return ("stop", "The planner raised a blocker for you: " + quoted(stops) + " Answer with `/plan` and your words.")
        many = [r for r in owner_raises(h) if r.get("kind") == "question"]
        if len(many) > MAX_QUESTIONS:
            return ("stop", f"The plan has {len(many)} questions for you, more than {MAX_QUESTIONS}: it is not ready. "
                            "Answer them with `/plan` and your words; nothing goes on until you do.")
        if h.get("questions") or owner_raises(h):
            asked = "The plan has questions for you. Answer with `/plan` and your words, or say `/review` to go on with its assumptions."
            on = autopilot()
            if on is None:
                return ("stop", f"{UNREAD} {asked}")
            return ("start", "reviewer", "plan") if on else ("stop", asked)
        return ("start", "reviewer", "plan")
    if role == "worker":
        return ("start", "reviewer", "pr")
    if role == "updater":
        # A clash with main goes to the planner by itself only on autopilot, as its record says: the plan may not fit
        # main anymore. A record from before #369 says nothing and started the planner.
        on = h.get("autopilot", True)
        if on is None:
            return ("stop", f"{UNREAD} The pull request clashes with main and needs a re-plan: say `/plan` to re-plan it.")
        return ("start", "planner", "") if on else \
            ("stop", "The pull request clashes with main and needs a re-plan. Say `/plan` to re-plan it against the new main.")
    if role != "reviewer":
        return ("stop", "")
    verdict = h.get("verdict")
    plan = (latest(records(items), "planner") or {}).get("handback") or {}
    asked = [r for r in owner_raises(plan) if r.get("kind") == "question"]
    if stage == "plan" and len(asked) > MAX_QUESTIONS:
        return ("stop", f"The plan has {len(asked)} questions for you, more than {MAX_QUESTIONS}: it is not ready. "
                        "Answer them with `/plan` and your words.")
    if stage == "plan" and verdict in ("approve", "block") and (plan.get("questions") or asked):
        on = autopilot()
        if on is None:
            return ("stop", f"{UNREAD} The plan has questions for you. Answer with `/plan` and your words.")
        left = []
        if on:
            # A plan posted before #300 asks through its questions field, judged by the review's assumptions.
            left = not_accepted(items, h, owners, body, number, parent) if plan.get("questions") else []
            left += unanswered(asked, items, h, owners, body, number, parent)
        if left:
            return ("stop", "The reviewer did not settle the plan's question for you: " + " ".join(f"\"{q}\"" for q in left)
                    + " Answer with `/plan` and your words" + (", or say `/work` to build it on its assumptions." if verdict == "approve" else "."))
    mine = owner_raises(h)
    if mine:
        return ("stop", "The reviewer raised for you: " + quoted(mine) + " Answer with `/plan`, `/work` or `/review` and your words.")
    # A worker's raise for the planner the code review settled goes on by itself, whatever the verdict on the code:
    # confirmed, to the planner; disagreed, back to the worker with the reviewer's why.
    words_ = {w for _, w in settled(records(items), h)} if stage == "pr" and verdict in ("approve", "block") else set()
    if verdict == "approve" and words_:
        return ("start", "planner" if "done" in words_ else "worker", "")
    if verdict == "approve" and stage == "plan" and test_fix(items, owners):
        return ("start", "worker", "")
    if verdict == "approve" and stage == "plan":
        on = autopilot()
        if on:
            return ("start", "split" if plan.get("kind") == "feature" else "worker", "", "autopilot")
        why = "The plan is approved. Say `/work` to build it, or `/plan` with changes."
        if clash_pending(records(items)):
            why = "The plan is approved and the pull request clashes with main. Say `/work` to rebuild it on the new main, or `/plan` with changes."
        return ("stop", f"{UNREAD} {why}" if on is None else why)
    if verdict == "approve":
        return ("stop", "The work is approved. Merge the pull request, or review it with a command to send it back.")
    if verdict == "escalate":
        return ("stop", "The reviewer escalated this to you, see why above.")
    last_owner = max([i for i, c in enumerate(items) if (c.get("author") or {}).get("login") in owners], default=-1)
    later = [r for r in records(items[last_owner + 1:]) if r.get("role") == "reviewer" and (r.get("stage") or "") == stage]
    blocks = sum(1 for r in later if (r.get("handback") or {}).get("verdict") == "block") + 1
    if blocks >= rounds:
        return ("stop", f"{blocks} blocking reviews in a row without agreement. Your call: `/plan`, `/work` or `/review` with your words.")
    return ("start", "planner" if stage == "plan" or for_planner(h) or "done" in words_ else "worker", "")


def waiting(items, owners, body, number):
    """What `/autopilot start` picks up on the issue: "worker" for an approved plan waiting for `/work`, "split" for an
    approved split not yet filed, else None, decided by the river as if the approval came on autopilot. Nothing is
    picked up twice: not after the owner's `/work`, an Autopilot line, or a worker or split record since the approval."""
    if not approved(records(items)):
        return None
    at = max(i for i, c in enumerate(items) if is_record(c, "reviewer", "plan") and records([c])[0].get("check", {}).get("passed"))
    for c in items[at + 1:]:
        who = (c.get("author") or {}).get("login")
        if (who in owners and command_of(c.get("body")) == "worker") or (who == BOT and (c.get("body") or "").strip().startswith("Autopilot:")) \
                or is_record(c, "worker") or is_record(c, "split"):
            return None
    step = next_step(items[:at], records([items[at]])[0], owners, autopilot=lambda: True, body=body, number=number)
    if step[0] != "start" or step[3:] != ("autopilot",):
        return None
    if step[1] == "split" and latest(records(items), "split"):
        return None
    return step[1]


def queued_since(items, at):
    """True when the bot said, after record `at`, the pull request joined the merge queue.

    The merge is GitHub's to finish then, so nothing waits on the owner."""
    line = re.compile(re.escape(AUTOPILOT_MERGE["queued"]).replace(r"\{pr\}", r"\d+"))
    return any((c.get("author") or {}).get("login") in (BOT, f"{BOT}[bot]") and line.fullmatch((c.get("body") or "").strip())
               for c in items[at + 1:])


def waits_on_owner(items, owners, autopilot, body="", number=""):
    """True when the issue waits on the owner.

    The river's last word on it stopped for the owner and no code owner has answered with a command since; an Approve
    is never one. Filing a split is the river going on; a cancel mentions no one."""
    at = max((i for i, c in enumerate(items) if is_record(c)), default=None)
    if at is None:
        return False
    rec = records([items[at]])[0]
    if rec.get("role") == "split" or queued_since(items, at):
        return False
    if any((c.get("author") or {}).get("login") in owners and command_of(c.get("body"))
           and not (c.get("where") or "").endswith("review (approved)") for c in items[at + 1:]):
        return False
    return next_step(items[:at], rec, owners, autopilot=autopilot, body=body, number=number)[0] == "stop"


def criteria_texts(plan):
    """A plan's criteria as the owner approves them: every acceptance and non-functional criterion's text, in order."""
    return [[c.get("text") if isinstance(c, dict) else c for c in plan.get(k) or []] for k in ("acceptance_criteria", "non_functional")]


def test_fix(items, owners):
    """True when the newest plan is a re-plan a code review asked for with a test blocker, the owner has not spoken
    since that review, and its criteria are exactly those of the plan the owner approved with `/work`."""
    owner_at = [i for i, c in enumerate(items) if (c.get("author") or {}).get("login") in owners]
    works = [i for i in owner_at if command_of(items[i].get("body")) == "worker"]
    if not works:
        return False
    review = next((i for i in range(len(items) - 1, works[-1], -1) if is_record(items[i], "reviewer", "pr")), None)
    if review is None or any(i > review for i in owner_at):
        return False
    r = records([items[review]])[0]
    h = r.get("handback") or {}
    confirmed = any(w == "done" for _, w in settled(records(items[:review]), h))
    if not r.get("check", {}).get("passed") or h.get("verdict") != "block" or not (for_planner(h) or confirmed):
        return False
    replan = latest(records(items[review + 1:]), "planner")
    agreed = latest(records(items[:works[-1]]), "planner")
    return bool(replan and agreed) and criteria_texts(replan["handback"]) == criteria_texts(agreed["handback"])


STAGE_COLUMN = {("planner", ""): "Plan", ("reviewer", "plan"): "Plan", ("worker", ""): "Work", ("reviewer", "pr"): "Review"}


def started(c, owners):
    """Column of the stage a code owner's `/work`, or the bot's line or run card, starts."""
    who, body = (c.get("author") or {}).get("login"), (c.get("body") or "").strip()
    card = who in (BOT, f"{BOT}[bot]") and re.match(re.escape(LIVE) + r"[^*]*\*\*(Planner|Worker|Reviewer) ?\(?(\w*)", body)
    if who in owners and command_of(body) == "worker" and "(approved)" not in c.get("where", "") or who in (BOT, f"{BOT}[bot]") and body == AUTOPILOT_LINES["worker"]:
        return "Work"
    return STAGE_COLUMN.get((card[1].lower(), card[2])) if card else None


def board_place(rec, step):
    """Where the card goes after this run: the column of the stage now running, or of this stage when it stops for
    the owner, and the Needs you pill exactly when the river stops for the owner (not after a cancel)."""
    if step[0] == "start" and step[1] == "split":
        # Filing a split puts the parent in Work, as `/work` does.
        return "Work", False
    if step[0] == "start":
        return STAGE_COLUMN[(step[1], step[2] if step[1] == "reviewer" else "")], False
    if step[0] == "merged":
        return "Done", False
    return STAGE_COLUMN.get((rec.get("attempt") or rec.get("role"), rec.get("stage") or ""), "Plan"), step[0] == "stop"


def next_line(step, owners):
    """The last line of a card: what happens next, mentioning the owner when it is their turn."""
    if step[0] == "start" and step[1] == "split":
        return "**Next:** The split's stories are filed now."
    if step[0] == "start":
        who = {"planner": "The planner", "worker": "The worker", "reviewer": "The reviewer"}[step[1]]
        return f"**Next:** {who} starts now."
    if step[0] in ("cancelled", "merged", "waiting", "queued"):
        return f"**Next:** {step[1]}"
    mention = " ".join(f"@{o}" for o in owners)
    return f"**Next:** {mention} {step[1]}".strip()


def main(argv):
    """agent pack N ROLE STAGE DIR | agent check-pack ROLE STAGE DIR | agent check review|work FILE PLAN N |
    agent record ROLE STAGE OUT CHECK_FILE PASSED LOG_DIR  (writes OUT/record.json and OUT/comment.md) |
    agent not-started ROLE STAGE OUT WHY_FILE  (the same, for a run or command that failed before its agent started) |
    agent cancelled ROLE STAGE OUT STARTED LOG_DIR  (the same, for a run someone cancelled) |
    agent card ROLE STAGE ready|working  (prints the run's live card, which is not a record) |
    agent queue ROLE STAGE N [queued|handoff]  (puts up a run's queued card where its record will go, prints its id) |
    agent autopilot start|stop N [OUT]  (switches N's issue tree on or off autopilot, prints the comment naming what
    switched; with OUT, `start` writes what it picks up to OUT/next.txt and its Autopilot line to OUT/autopilot.md) |
    agent closed N  (what autopilot does now that issue N closed, for every tree on autopilot) |
    agent recheck N OUT  (once OUT's plan review approved, runs every check of N's open pull request again)"""
    if argv[1] == "pack":
        has_plan = pack(os.environ["GITHUB_REPOSITORY"], argv[2], argv[3], argv[4], argv[5])
        return 0 if has_plan or argv[3] == "planner" else 3
    if argv[1] == "check":
        if len(argv) < 6:
            print("the check needs plan.json and the issue number: agent check review|work FILE PLAN N")
            return 1
        return check(argv[2], argv[3], argv[4], argv[5])
    if argv[1] == "check-pack":
        bad = problems_pack(argv[2], argv[3], argv[4])
        for b in bad:
            print(b)
        return 1 if bad else 0
    if argv[1] == "record":
        role, stage, out, check_file, passed, log_dir = argv[2:8]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "commit_before": os.environ.get("BASE"),
                "started_by": os.environ.get("GITHUB_ACTOR"), "models": models_used(log_dir),
                "report": run_report(os.path.join(out, "claude.json")), "log": os.environ.get("LOG_URL"),
                "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
        text = open(check_file).read() if os.path.exists(check_file) else ""
        earlier = []
        folder = os.path.join(os.environ.get("PACK", ""), "in")
        for name in sorted(os.listdir(folder)) if os.environ.get("PACK") and os.path.isdir(folder) else []:
            try:
                earlier.append(json.load(open(os.path.join(folder, name))))
            except (OSError, json.JSONDecodeError):
                print(f"::warning title=Record not read::{name} in the pack could not be read")
        # Code stamps each raise with who raised it and an ID no raise on the issue has yet.
        rec = stamp_record(build_record(role, stage, out, text, passed == "true", meta), earlier)
        if role == "worker":
            # Kept in the record, so the comment redrawn once its pull request opens still names them.
            rec["files_changed"] = files_changed(os.environ.get("BASE"))
            rec["branch"] = f"try/issue-{os.environ.get('N', '')}"
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        reviewed = os.path.join(os.environ.get("PACK", ""), "plan.json")
        plan = None
        if role == "reviewer" and os.environ.get("PACK") and os.path.exists(reviewed):
            try:
                plan = json.load(open(reviewed))
            except (OSError, json.JSONDecodeError):
                plan = None
        open(os.path.join(out, "comment.md"), "w").write(render(rec, plan=plan if isinstance(plan, dict) else None,
                                                                earlier=earlier))
        return 0
    if argv[1] == "not-started":
        role, stage, out, why_file = argv[2:6]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "started_by": os.environ.get("GITHUB_ACTOR"),
                "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
        rec = not_started(role, stage, open(why_file).read() if os.path.exists(why_file) else "", meta)
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        open(os.path.join(out, "comment.md"), "w").write(render(rec))
        return 0
    if argv[1] == "cancelled":
        role, stage, out, started, log_dir = argv[2:7]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "started_by": os.environ.get("GITHUB_ACTOR"),
                "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
        if started == "true":
            meta.update({"models": models_used(log_dir), "report": run_report(os.path.join(out, "claude.json")),
                         "log": os.environ.get("LOG_URL")})
        rec = cancelled(role, stage, started == "true", meta)
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        open(os.path.join(out, "comment.md"), "w").write(render(rec))
        return 0
    if argv[1] == "card":
        # The card is public: every secret the step was given to remove (SCRUB_*) shows as [secret removed].
        secrets = [v for k, v in os.environ.items() if k.startswith("SCRUB_")]
        sys.stdout.write(scrub(live_card(argv[2], argv[3], argv[4]), secrets))
        return 0
    if argv[1] == "queue":
        print(queue(argv[2], argv[3], argv[4], argv[5] if len(argv) > 5 else "queued"))
        return 0
    if argv[1] == "check-round":
        try:
            h = json.load(open(argv[3]))
        except (OSError, json.JSONDecodeError) as e:
            print(f"{argv[3]}: {e}")
            return 1
        bad = problems_round(argv[2], h if isinstance(h, dict) else {}, argv[4])
        for b in bad:
            print(b)
        return 1 if bad else 0
    if argv[1] == "transcript":
        secrets = [v for k, v in os.environ.items() if k.startswith("SCRUB_")]
        sys.stdout.write(transcript(argv[2], secrets))
        return 0
    if argv[1] == "split":
        repo, parent = os.environ["GITHUB_REPOSITORY"], argv[2]
        _, items = conversation(repo, parent)
        recs = records(items)
        if not approved(recs) or latest(recs, "planner")["handback"].get("kind") != "feature":
            print("The newest plan is not an approved split.")
            return 1
        on = AUTOPILOT in {l["name"] for l in json.loads(gh("api", f"repos/{repo}/issues/{parent}")).get("labels", [])}
        rec = file_split(repo, parent, recs, [AUTOPILOT] if on else [])
        rec["run"] = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
        card = os.environ.get("CARD_ID", "")
        if card:
            # The command's queued card becomes the Split filed record, edited in place.
            gh("api", "-X", "PATCH", f"repos/{repo}/issues/comments/{card}", "-f", f"body={render(rec)}", "--silent")
        elif not any(r.get("role") == "split" for r in recs):
            gh("issue", "comment", parent, "-R", repo, "--body", render(rec))
        spec = os.environ.get("DOKIMA_BOARD", "").strip()
        if spec:
            from dokima import board
            b = board.Board(spec, repo, board.gql)
            for f in rec["handback"]["stories"]:
                iid = b.item("issue", f["issue"])
                b.set(iid, "Status", "Backlog")
                b.set(iid, "Action", "Autopilot" if on else None)
            iid = b.item("issue", int(parent))
            b.set(iid, "Status", "Work")
            b.set(iid, "Action", "Autopilot" if on else None)
        if on:
            # On autopilot the stories go on too, and each one with nothing to wait for starts planning.
            start_waiting(repo, [f["issue"] for f in rec["handback"]["stories"] if not f["blocked_by"]])
        return 0
    if argv[1] == "kind":
        _, items = conversation(os.environ["GITHUB_REPOSITORY"], argv[2])
        recs = records(items)
        plan = latest(recs, "planner")
        print(plan["handback"].get("kind", "") if plan and approved(recs) else "")
        return 0
    if argv[1] == "next":
        number, out = argv[2], argv[3]
        owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
        rec = json.load(open(os.path.join(out, "record.json")))
        repo = os.environ["GITHUB_REPOSITORY"]
        # A run that never started stops for the owner, and a cancelled one stops, whatever the conversation says,
        # so it is not read.
        d, items = ({}, []) if rec.get("role") in ("not-started", "cancelled") else conversation(repo, number)
        read = []

        def autopilot():
            # Read once, and only when the river's decision turns on it.
            if not read:
                read.append(on_autopilot(repo, number))
            return read[0]
        ups = []

        def parent():
            # The parent's words, read once and only when an assumption cites somewhere other than this issue.
            if not ups:
                ups.append(parent_words(repo, number))
            return ups[0]
        step = next_step(items, rec, owners, autopilot=autopilot, body=d.get("body") or "", number=number, parent=parent)
        if approves_work(rec) and step[0] != "start":
            # On autopilot the code review's approval stands in for the owner's: the pull request merges by itself.
            on = autopilot()
            if on is None:
                step = ("stop", f"{UNREAD} {step[1]}")
            elif on:
                pr, how, why = automerge(repo, number)
                if how == "merged":
                    step = ("merged", f"Autopilot merged PR #{pr}; what it unblocks starts when the issue closes.")
                elif how == "queued":
                    step = ("queued", f"PR #{pr} is in the merge queue; GitHub merges it when the queue's checks pass.")
                elif how == "waits":
                    step = ("stop", f"PR #{pr} waits for your approval before it merges. Approve it on GitHub, or "
                                    "review it with a command to send it back.")
                elif how == "unconfirmed":
                    unconfirmed_comment(repo, pr, why, " ".join(f"@{o}" for o in owners))
                    step = ("stop", f"Autopilot could not confirm PR #{pr} merged: {why}. Check it on GitHub and merge "
                                    "it if it did not merge.")
                else:
                    step = ("stop", f"Autopilot did not merge the pull request: {why}. It waits for you: merge it, or "
                                    "review it with a command to send it back.")
        if rec.get("role") == "reviewer" and (rec.get("stage") or "") == "plan" and rec.get("check", {}).get("passed") \
                and (rec.get("handback") or {}).get("verdict") == "approve":
            # Code records the approved plan's links on GitHub and redraws the cards they touch; anything that keeps
            # a link from being recorded stops the river, so autopilot never starts work that should wait.
            why = record_links(repo, number, items)
            if why:
                step = ("stop", why)
            elif step[:2] == ("start", "worker") and step[3:] == ("autopilot",):
                # On autopilot a blocked issue builds nothing; it plans afresh once every issue blocking it closes.
                try:
                    left = open_blockers_of(repo, number)
                except subprocess.CalledProcessError as e:
                    left, step = None, ("stop", f"GitHub could not list the issues blocking #{number}, so the worker "
                                                f"did not start: {gh_reason(e)}. Say `/work` once GitHub answers.")
                if left:
                    # Nothing is built from a plan written before its blockers landed: the issue plans again.
                    step = ("waiting", f"Nothing is built: the issue plans again by itself when {named(left)} close.")
        if rec.get("role") == "worker":
            # The pull request is opened after the record is written, so the worker's sentence links it only now.
            try:
                pr = gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
                        "-q", ".[0].number").strip()
            except subprocess.CalledProcessError:
                pr = ""
            if pr.isdigit():
                url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/pull/{pr}"
                open(os.path.join(out, "comment.md"), "w").write(render(rec, url))
        filed = file_issues(repo, number, rec, records(items))
        if filed:
            # The issues filed in this run go on its record, above the full record, whatever GitHub answered.
            text = open(os.path.join(out, "comment.md")).read()
            fold = "\n<details><summary>Full record</summary>"
            at = text.find(fold)
            at = len(text.rstrip("\n")) if at < 0 else at
            open(os.path.join(out, "comment.md"), "w").write(text[:at] + "\n".join(filed) + "\n" + text[at:])
        path = os.path.join(out, "comment.md")
        text = open(path).read() if os.path.exists(path) else ""
        open(path, "w").write(with_next(text, next_line(step, owners)) if text else "\n" + next_line(step, owners) + "\n")
        if step[3:] == ("autopilot",):
            # The line the owner would have typed `/work` in place of; the workflow posts it on the issue.
            open(os.path.join(out, "autopilot.md"), "w").write(AUTOPILOT_LINES[step[1]] + "\n")
        column, needs = board_place(json.load(open(os.path.join(out, "record.json"))), step)
        open(os.path.join(out, "board.txt"), "w").write(f"{column} {'needs' if needs else 'none'}\n")
        print(" ".join(step[:3]) if step[0] == "start" else "stop")
        return 0
    if argv[1] == "recheck":
        rec = json.load(open(os.path.join(argv[3], "record.json")))
        if rec.get("role") == "reviewer" and (rec.get("stage") or "") == "plan" and rec.get("check", {}).get("passed") \
                and (rec.get("handback") or {}).get("verdict") == "approve":
            print(rerun_checks(os.environ["GITHUB_REPOSITORY"], argv[2]))
        else:
            print("The plan was not approved: the checks stay as they are.")
        return 0
    if argv[1] == "board":
        from dokima import board, plan, retry
        spec, repo = os.environ.get("DOKIMA_BOARD", "").strip(), os.environ.get("GITHUB_REPOSITORY", "")
        if not spec:
            print("No board set; nothing to move.")
            return 0
        try:
            rec = json.load(open(os.path.join(argv[3], "record.json")))
        except (OSError, json.JSONDecodeError):
            rec = {"role": os.environ.get("ROLE", ""), "stage": os.environ.get("STAGE", "")}
        rec = rec if isinstance(rec, dict) else {}
        if rec.get("role") == "cancelled" or os.path.exists(os.path.join(argv[3], "board.txt")) and (rec.get("check") or {"passed": True}).get("passed"):
            # A run that decided what follows, or was cancelled, is placed from GitHub's state, never from the run.
            try:
                placed = retry.once_more("the board step", lambda: board.rebuild(
                    board.Board(spec, repo), repo, plan.repo_approvers(repo.split("/")[0]), int(argv[2])))
            except RuntimeError as e:
                print(f"::error::{e}")
                return 1
            for kind, n, column, pill in placed:
                print(f"board: {kind} #{n} -> {column}{f' · {pill}' if pill else ''}")
            return 0
        # The run failed, so the river stopped: its own stage's column with Needs you, at once.
        column = board_place(rec, ("stop",))[0]
        print(f"board: #{argv[2]} and its open pull request -> {column} · Needs you")
        errors = (subprocess.CalledProcessError, KeyError, ValueError)
        try:
            retry.once_more("the board step", lambda: board.stopped(board.Board(spec, repo), repo, argv[2], column),
                            errors=errors)
        except errors as e:
            print(f"::warning::GitHub could not be read, so the board may not show it: {gh_reason(e) if hasattr(e, 'stderr') else e}")
        return 0
    if argv[1] == "autopilot":
        switch, number = argv[2], argv[3]
        repo = os.environ["GITHUB_REPOSITORY"]
        switched = switch_autopilot(repo, number, switch)
        said_on = os.environ.get("NUMBER", "")
        if switch == "stop" and os.environ.get("ON_PR") == "true" and said_on.isdigit() and int(said_on) not in switched:
            # The pull request it was said on goes off autopilot too, even when its issue had no label.
            labels = {l["name"] for l in json.loads(gh("api", f"repos/{repo}/issues/{said_on}")).get("labels", [])}
            if AUTOPILOT in labels:
                gh("api", "-X", "DELETE", f"repos/{repo}/issues/{said_on}/labels/{AUTOPILOT}")
                switched.append(int(said_on))
        pick = None
        if switch == "start" and len(argv) > 4:
            # What is already waiting for the owner's `/work` is picked up: written to OUT for the workflow to start.
            owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
            d, items = conversation(repo, number)
            pick = waiting(items, owners, d.get("body") or "", number)
            os.makedirs(argv[4], exist_ok=True)
            if pick:
                open(os.path.join(argv[4], "autopilot.md"), "w").write(AUTOPILOT_LINES[pick] + "\n")
                open(os.path.join(argv[4], "next.txt"), "w").write(pick + "\n")
        picked = {"worker": f"#{number}'s approved plan goes to the worker now.",
                  "split": f"#{number}'s approved split files its stories now."}.get(pick, "")
        started = []
        if switch == "start":
            # The issue itself starts its planner when it waits on nothing open and nothing started on it yet.
            started = start_waiting(repo, [int(number)], line=AUTOPILOT_START_LINE)
            # `/autopilot start` picks up every issue under the issue, at every level, that waits on nothing open.
            started += start_waiting(repo, issue_tree(repo, number)[1:])
        sys.stdout.write(autopilot_comment(number, switch, switched, started, picked))
        if switch == "start":
            # What its code review already approved anywhere in the tree merges now, as on autopilot.
            merge_tree(repo, number, [o for o in os.environ.get("OWNERS", "").split(",") if o])
        return 0
    if argv[1] == "closed":
        repo = os.environ["GITHUB_REPOSITORY"]
        # A parent closes with its last sub-issue on autopilot or not; autopilot then works from what is left.
        for line in close_done_parents(repo, argv[2]) + autopilot_closed(repo) or [f"#{argv[2]} closed: nothing on autopilot to do."]:
            print(line)
        return 0
    if argv[1] == "route":
        on_pr = os.environ.get("ON_PR") == "true"
        head, pr_body = os.environ.get("HEAD", ""), ""
        if on_pr:
            p = json.loads(gh("pr", "view", os.environ["NUMBER"], "-R", os.environ["GITHUB_REPOSITORY"], "--json", "headRefName,body"))
            head, pr_body = p["headRefName"], p["body"]
        r = route(os.environ.get("BODY", ""), on_pr, os.environ.get("NUMBER", ""), head, pr_body)
        for k, v in (r or {}).items():
            print(f"{k}={v}")
        return 0
    print(main.__doc__)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except subprocess.CalledProcessError as e:
        # GitHub's own error, so the step that failed can say why.
        sys.stderr.write((e.stderr or str(e)).strip() + "\n")
        sys.exit(1)

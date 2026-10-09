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

from dokima import card, words
from dokima.card import field_icon, icon

VERDICTS = {"approve", "block", "escalate"}
FIXERS = {"worker", "planner"}
ANSWERS = {"fixed", "disagree"}


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
    """The issue as it stands: title, body and every comment with its author and where it was written, oldest first."""
    parts = [f"# Issue #{d['number']}: {d['title']}", "", d["body"] or "", "", "## Comments"]
    for c in items:
        parts += ["", f"### {c['author']['login']} on {c['where']} ({c['createdAt']})", "", c["body"]]
    return "\n".join(parts) + "\n"


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
    """The blockers of the newest review at this stage, unless it approved; these must be answered by id."""
    for r in reversed(recs):
        if r.get("role") == "reviewer" and (r.get("stage") or "") == stage and r.get("check", {}).get("passed"):
            return [] if r["handback"].get("verdict") == "approve" else r["handback"].get("blockers", [])
    return []


def blockers_for(recs, role):
    """The blockers this role must answer by id. A planner answers the test blockers of a code review that sent the work
    back to it, else the newest plan review's; a worker answers only the code blockers of the newest code review."""
    if role == "worker":
        return [b for b in open_blockers(recs, "pr") if not (isinstance(b, dict) and b.get("fixer") == "planner")]
    for r in reversed(recs):
        if r.get("role") == "reviewer" and r.get("check", {}).get("passed"):
            if (r.get("stage") or "") == "pr" and r["handback"].get("verdict") == "block":
                tests = [b for b in r["handback"].get("blockers", []) if isinstance(b, dict) and b.get("fixer") == "planner"]
                if tests:
                    return tests
            break
    return open_blockers(recs, "plan")


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


def problems_round(role, h, pack_dir):
    """Every open blocker of the newest review must be answered by id; the reviewer must resolve or keep each one, and
    the planner's links must name open issues in the pack."""
    path = os.path.join(pack_dir, "open_blockers.json")
    blockers = {b.get("id") for b in (json.load(open(path)) if os.path.exists(path) else []) if isinstance(b, dict)}
    bad = []
    if role == "reviewer":
        resolved, listed = h.get("resolved", []), h.get("blockers", [])
        if not isinstance(resolved, list) or not all(isinstance(x, str) for x in resolved):
            bad.append("resolved must be a list of blocker ids")
            resolved = []
        if not isinstance(listed, list) or not all(isinstance(b, dict) for b in listed):
            bad.append("blockers must be a list of objects")
            listed = listed if isinstance(listed, list) else []
        carried = set(resolved) | {b.get("id") for b in listed if isinstance(b, dict)}
        return bad + [f"earlier blocker {b} is neither resolved nor still listed" for b in sorted(blockers - carried)]
    replies = h.get("replies", [])
    if not isinstance(replies, list) or not all(isinstance(r, dict) for r in replies):
        bad.append("replies must be a list of objects")
        replies = replies if isinstance(replies, list) else []
    replied = {r.get("blocker") for r in replies if isinstance(r, dict)}
    if role == "planner":
        bad += problems_links(h, pack_dir)
    return bad + [f"blocker {b} is not answered" for b in sorted(blockers - replied)]


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
    if state in ("queued", "handoff"):
        if ahead:
            line = f"{icon(repo, 'queued')} {head} · waiting for [this run]({ahead})"
            what = (f"Queued, and waiting for [this run]({ahead}) on the same issue to end; this run starts after it. "
                    "This card says working when the agent starts, then becomes the run's record.")
        else:
            line = f"{icon(repo, 'queued')} {head} · queued"
            what = "Queued: the run starts in a moment. This card says working when the agent starts, then becomes the run's record."
        return "\n".join([LIVE, line, "", what] + ([] if state == "handoff" else ["", f"<sub>[run]({run})</sub>"])) + "\n"
    if state == "working":
        line = f"{icon(repo, 'running')} {head} · agent working since {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC"
        what = (f"The agent is working; [watch it live]({run}) on GitHub. This card says checking when the agent ends, "
                "then becomes the run's record.")
        return "\n".join([LIVE, line, "", what]) + "\n"
    if state == "checking":
        line = f"{icon(repo, 'running')} {head} · checking"
        what = "The agent has ended and code is checking its hand-back. This card becomes the run's record next."
    else:
        line = f"{icon(repo, 'queued')} {head} · setting up"
        what = ("The machine is setting up: the branch, the starting pack and the tools. This card says working when "
                "the agent starts, then becomes the run's record.")
    return "\n".join([LIVE, line, "", what, "", f"<sub>[run]({run})</sub>"]) + "\n"


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


HEADS = {"planner": "The planner", "worker": "The worker", "split": "Code"}


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
    return [f"- {k}: {', '.join(map(str, v)) if isinstance(v, list) else v}" for k, v in d.items()] if isinstance(d, dict) else []


def outside_fold(repo, items):
    """The Outside the plan fold, the same for the worker and a review.

    It holds the worker's changes outside its scope or a review's changes outside the plan; nothing when there are none."""
    lines = bullets(items, lambda o: f"`{o.get('file', '')}`: {o.get('why', o.get('change', ''))}")
    return [""] + card.fold(f"{field_icon(repo, 'outside the plan')} Outside the plan", lines) if lines else []


def question_lines(repo, questions):
    """The Questions for you part, the same for the planner and a review.

    Each question with the reading the plan assumed: the planner's questions, or those a review could not confirm;
    nothing when there are none."""
    lines = [f"- {escape_line(q.get('question'))}" + (f" Assumed: {escape_line(q['assumption'])}" if filled(q.get("assumption")) else "")
             if isinstance(q, dict) else f"- {escape_line(str(q))}"
             for q in (questions if isinstance(questions, list) else [])
             if filled(q.get("question") if isinstance(q, dict) else q)]
    return ["", f"{field_icon(repo, 'question')} **Questions for you:**"] + lines if lines else []


def plan_number(plan):
    """The issue number N of the plan's criteria ids N.k, from its tests.

    None when the plan has no tests to read it from."""
    keys = [k for k in (plan.get("tests") or {}) if re.fullmatch(r"\d+\.\d+", str(k))] if isinstance(plan.get("tests"), dict) else []
    return keys[0].split(".")[0] if keys else None


def plan_rows(plan):
    """The plan's criteria in order, keyed by their id: acceptance criteria, then non-functional requirements."""
    rows = [c if isinstance(c, dict) else {"text": c} for k in ("acceptance_criteria", "non_functional")
            for c in (plan.get(k) if isinstance(plan.get(k), list) else [])]
    number = plan_number(plan)
    return {f"{number}.{i}" if number else str(i): c for i, c in enumerate(rows, 1)}


def criterion_rows(repo, c, st, under):
    """One criterion as the issue card draws it: circle, sentence, lines `under` it, Source."""
    out = [f"- {card.circle(repo, st)} {card.escape(c.get('text'))}"] + under
    if filled(c.get("source")):
        out.append(f'  - <a href="{c["source"]}">Source</a>')
    return out


def verified_rows(repo, rec, key):
    """A Verified by line per test of the criterion, holding its docstring's first line.

    The docstrings are those read when the plan was recorded."""
    found = rec.get("verified_by") or {}
    tests = (rec["handback"].get("tests") or {}).get(key) or []
    return [f'  - *<a href="{t["url"]}">{field_icon(repo, "verified by")} Verified by</a>: {card.escape(t["verified_by"])}*'
            for t in (found.get(x) for x in tests if isinstance(x, str)) if t and t.get("verified_by")]


def verified_by(plan):
    """Each test of the plan with its docstring's first line and a link to it.

    Read from the test files in the folder the record is written in; the link points at the line the test starts on,
    on the branch checked out."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    try:
        ref = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip() or "HEAD"
    except OSError:
        ref = "HEAD"
    out = {}
    tests = plan.get("tests") if isinstance(plan.get("tests"), dict) else {}
    for t in (x for ts in tests.values() if isinstance(ts, list) for x in ts if isinstance(x, str) and "::" in x):
        path, name = t.split("::", 1)
        try:
            source = open(path).read()
        except OSError:
            continue
        out[t] = card.test_entry(repo, ref, path, source, name)
    return out


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


def details(rec):
    """The long parts of a run's record, each in its own fold, drawn by the issue card's fold code."""
    role, h = rec["role"], rec["handback"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not isinstance(h, dict):
        return []
    parts = []
    if role == "planner":
        # Non-functional requirements show the same rows as the criteria, without Source since they have none.
        ac = h.get("acceptance_criteria") if isinstance(h.get("acceptance_criteria"), list) else []
        nfr = list(plan_rows(h).items())[len(ac):]
        parts += [("Non-functional requirements", [l for k, n in nfr for l in
                                                   criterion_rows(repo, {"text": n.get("text")}, "not started", verified_rows(repo, rec, k))]),
                  ("Scope", bullets(h.get("scope"), str)), ("Out of scope", bullets(h.get("out_of_scope"), str)),
                  ("Tests", pairs(h.get("tests"))),
                  ("Test changes", pairs(h.get("test_changes"))),
                  ("Concerns", bullets(h.get("concerns"), lambda c: f"{c.get('text', '')} ({c.get('evidence', '')})")),
                  ("Stories in detail", bullets(h.get("stories"), lambda st: f"{st.get('title', '')}: {st.get('user_story', '')}"))]
    elif role == "worker":
        files = [f for f in rec.get("files_changed") or [] if filled(f)]
        parts += [("What it built", ([f"{field_icon(repo, 'files changed')} **Files changed:** " + ", ".join(f"`{f}`" for f in files), ""] if files else [])
                   + pairs(h.get("criteria"))
                   + ([f"- Its own test run: {escape_line(h['evidence'])}"] if filled(h.get("evidence")) else [])),
                  None,
                  ("What it raised", bullets(h.get("suspect_tests"), lambda t: f"Suspect test {t.get('test', '')}: {t.get('evidence', '')}")
                   + bullets(h.get("replies"), lambda r: f"{r.get('blocker', '')} {r.get('answer', '')}: {r.get('why', '')}"))]
    prev = h.get("previous_step")
    if role != "reviewer" and isinstance(prev, dict):
        parts.append(("What the previous step did", [f"- {field_icon(repo, 'still open') + ' ' if k == 'open' else ''}**{label}:**{x[1:]}"
                                                     for k, label in (("did", "Did"), ("decided", "Decided"), ("open", "Still open"))
                                                     for x in bullets(prev.get(k), str)]))
    out = []
    for part in parts:
        if part is None:
            out += outside_fold(repo, h.get("outside_scope"))
        elif part[1] and part[1] != [""]:
            out += [""] + card.fold(*part)
    return out


def review_lines(rec, plan):
    """What a review shows under its opening, in the owner's order.

    Each failing criterion with why it fails and its Source, each ask no criterion keeps, its changes outside the plan,
    the plan's questions whose assumption it could not confirm, and the issues it found. A blocker the plan cannot
    place still shows why it fails."""
    h = rec["handback"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    lines = []
    if h.get("verdict") == "escalate" and filled(h.get("summary")):
        lines += ["", escape_line(h["summary"])]
    rows = plan_rows(plan) if isinstance(plan, dict) else {}
    blockers = [b for b in h.get("blockers") or [] if isinstance(b, dict)]
    why = lambda b: f"{field_icon(repo, 'blocker')} {card.escape(escape_line(b.get('problem')))}"
    failing = [l for k, c in rows.items() for l in
               (criterion_rows(repo, c, "failed", [f"  - {why(b)}" for b in blockers if str(b.get("criterion", "")).strip() == k])
                if any(str(b.get("criterion", "")).strip() == k for b in blockers) else [])]
    failing += [f"- {why(b)}" for b in blockers if str(b.get("criterion", "")).strip() not in rows]
    failing += [l for a in h.get("asks") or [] if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing"
                for l in criterion_rows(repo, {"text": a.get("ask"), "source": a.get("source")}, "failed", ["  - Nothing covers this"])]
    if failing:
        lines += [""] + failing
    lines += outside_fold(repo, h.get("outside_plan"))
    assumed = {q.get("question"): q.get("assumption") for q in (plan or {}).get("questions") or [] if isinstance(q, dict)}
    lines += question_lines(repo, [{"question": a.get("question"), "assumption": assumed.get(a.get("question"))}
                                   for a in h.get("assumptions") or [] if isinstance(a, dict) and a.get("accepted") is not True])
    found = [f for f in h.get("issues_found") or [] if isinstance(f, dict)]
    if found:
        lines += ["", f"{field_icon(repo, 'issue found')} **Issues found outside this one** (proposals until you file them):"]
        lines += [f"{i}. {f.get('title')}: {f.get('why')}" for i, f in enumerate(found, 1)]
    return lines


def opening(rec):
    """The one plain sentence a run comment opens with: what the run did."""
    role, h, passed = rec["role"], rec["handback"], rec["check"]["passed"]
    if not passed and role == "worker":
        return "The worker stopped early with its hand-back rejected by code."
    if not passed:
        return f"{who(role, rec.get('stage'))}'s run ended with its hand-back rejected by code."
    if role == "planner" and h.get("kind") == "feature":
        n = len(h.get("stories") or [])
        return f"The planner proposes a split into {n} stories" + (" and asks you questions." if h.get("questions") else ".")
    if role == "planner":
        q = len(h.get("questions") or [])
        return f"The planner planned this issue and asks you {q} question{'s' if q > 1 else ''}." if q else "The planner planned this issue."
    if role == "reviewer":
        name, what = who(role, rec.get("stage")), "the plan" if rec.get("stage") == "plan" else "the work"
        n = len({b.get("criterion") for b in h.get("blockers") or [] if isinstance(b, dict)})
        return {"approve": f"{name} passed {what}.",
                "block": f"{name} blocked {what} on {n} criteri{'a' if n != 1 else 'on'}.",
                "escalate": f"{name} escalated {what} to you."}.get(h.get("verdict"), f"{name} judged {what}.")
    if role == "split":
        return f"Code filed the split as {len(h.get('stories') or [])} stories."
    return h["summary"].strip() if filled(h.get("summary")) else ""


def record_fold(rec):
    """The full JSON record, always the last fold of a run comment: later packs are built from it."""
    return ["", "<details><summary>Full record</summary>", "", "```json", json.dumps(rec, indent=1), "```", "", "</details>"]


def render(rec, pr=None, plan=None):
    """The comment that carries a record: one plain sentence saying what the run did, the short version the owner
    needs at a glance, the long parts in folds, then the full record as JSON in the last fold. `pr` is the link of the
    worker's pull request, once it exists; `plan` is the plan a plan review judged, whose assumptions answer its
    questions."""
    role, h = rec["role"], rec["handback"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
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
            lines += stats_fold(rec) + record_fold(rec)
        else:
            lines += record_fold(rec) + ["", f"<sub>No agent ran · [run]({rec.get('run', '')})</sub>"]
        return "\n".join(lines) + "\n"
    if role == "updater":
        # A clash with main, found by code after a merge: the merge, its PR and every file that clashed.
        by = f" (#{h['merged_pr']})" if h.get("merged_pr") else ""
        lines = [MARK, f"Pull request #{h.get('pr')} clashes with `{h.get('base') or 'main'}` since {str(h.get('merge', ''))[:7]}{by} "
                       "merged, so the planner re-plans against the new main. The files that clashed:", ""]
        lines += [f"- `{f}`" for f in h.get("files") or []] or [f"- {h.get('why') or 'none listed'}"]
        lines += record_fold(rec) + ["", f"<sub>Found by code, no model" + (f" · [run]({rec['run']})" if rec.get("run") else "") + "</sub>"]
        return "\n".join(lines) + "\n"
    passed = rec["check"]["passed"]
    first = f"{icon(repo, 'passed' if passed else 'failed')} {role_icon(repo, role, rec.get('stage'))}{escape_line(opening(rec))}"
    if role == "worker" and pr:
        first += f" ([pull request #{pr.rstrip('/').rsplit('/', 1)[-1]}]({pr}))"
    lines = [MARK, first]
    if not passed:
        lines += [""] + [f"- {p}" for p in rec["check"]["problems"]]
    elif role == "planner" and h.get("kind") == "feature":
        lines += ["", f"**Feature:** {h.get('feature', '')}", ""]
        lines += [f"{i}. {st.get('title', '')}" for i, st in enumerate(h.get("stories", []), 1)]
    elif role == "planner":
        lines += ["", f"**User story:** {h.get('user_story') or h.get('question') or ''}"]
        ac = h.get("acceptance_criteria") if isinstance(h.get("acceptance_criteria"), list) else []
        rows = list(plan_rows(h).items())[:len(ac)]
        if rows:
            lines += ["", f"{field_icon(repo, 'acceptance criterion')} **Acceptance criteria:**", ""]
            lines += [l for k, c in rows for l in criterion_rows(repo, c, "not started", verified_rows(repo, rec, k))]
    elif role == "reviewer":
        lines += review_lines(rec, plan)
    elif role == "split":
        num = {f["story"]: f["issue"] for f in h.get("stories", [])}
        lines += [""] + [f"{f['story']}. #{f['issue']} {f['title']}" + (f" ({field_icon(repo, 'blocked by')} blocked by {', '.join('#' + str(num[d]) for d in f['blocked_by'])})" if f["blocked_by"] else "")
                         for f in h.get("stories", [])]
        lines += ["", "Each story now goes through the flow on its own: comment `/plan` on it to start."]
    related = card.link_lines(repo, h.get("links")) if passed and role == "planner" else []
    if related:
        lines += [""] + related
    asked = question_lines(repo, h.get("questions")) if passed and role == "planner" else []
    if asked:
        lines += asked + ["", "It planned on the reading each question names; reply with `/plan` and your words, or leave them."]
    lines += details(rec) + stats_fold(rec) + record_fold(rec)
    return "\n".join(lines) + "\n"


def words_link(source):
    """Where the owner said the words: the issue or comment link as given, or AGENTS.md on the repo's main branch."""
    if source == "AGENTS.md":
        return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/blob/main/AGENTS.md"
    return source


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


def stats_fold(rec):
    """The Stats fold at the bottom of every run comment, right above the full record."""
    stats = field_icon(os.environ.get("GITHUB_REPOSITORY", ""), "stats")
    return [""] + card.fold(f"{stats} Stats", [footnote(rec)])


def footnote(rec):
    """The run's stats line: model, time, turns, tokens, cost and its links.

    The links go to the run's whole conversation and to its run."""
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
        parts.append(f"{r.get('tokens_in', 0):,} tokens in, {r.get('tokens_out') or 0:,} out")
    if r.get("cost_usd") is not None:
        parts.append(f"${r['cost_usd']:.2f} at API prices")
    links = " · ".join(x for x in (f"[conversation]({rec['log']})" if rec.get("log") else "", f"[run]({rec['run']})" if rec.get("run") else "") if x)
    return " · ".join(parts) + (" · " + links if links else "")


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


def pack(repo, number, role, stage, dest):
    """Build the starting pack from GitHub's records: the issue and its PRs' conversation, every agent record so far,
    the newest passed plan and, for the planner, every open issue of the repo. The pull request review also gets the worker's session log from its run."""
    d, items = conversation(repo, number)
    recs = records(items)
    listed = open_issues(repo) if role == "planner" else None
    os.makedirs(os.path.join(dest, "in"), exist_ok=True)
    if listed is not None:
        json.dump(listed, open(os.path.join(dest, "open_issues.json"), "w"), indent=1)
    answers = blockers_for(recs, role) if role != "reviewer" else open_blockers(recs, stage)
    json.dump(answers, open(os.path.join(dest, "open_blockers.json"), "w"), indent=1)
    open(os.path.join(dest, "issue.md"), "w").write(issue_text(d, items))
    for i, r in enumerate(recs, 1):
        name = f"{i:02d}-{r['role']}{'-' + r['stage'] if r.get('stage') else ''}.json"
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


QUESTION_SHAPE = '{"question": "...?", "assumption": "..."}'


def problems_questions(qs):
    """Everything wrong with the planner's questions for the owner: each is exactly a question (with a '?') and the
    reading the plan assumed, nothing else."""
    if not isinstance(qs, list):
        return [f"questions must be a list, each {QUESTION_SHAPE}"]
    bad = []
    for i, q in enumerate(qs, 1):
        if not isinstance(q, dict):
            bad.append(f"question {i} must be a question and its assumption, {QUESTION_SHAPE}")
            continue
        extra = sorted(str(k) for k in q if k not in ("question", "assumption"))
        if extra:
            bad.append(f"question {i} has {', '.join(extra)}: a question is only the question and its assumption, "
                       "never options or a recommendation")
        for field in ("question", "assumption"):
            if not filled(q.get(field)):
                bad.append(f"question {i} has no {field}: it must be non-empty text")
        if filled(q.get("question")) and "?" not in q["question"]:
            bad.append(f"question {i} asks nothing: its question needs a '?'")
    return bad


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
    blockers = r.get("blockers", [])
    if not isinstance(blockers, list):
        bad.append("blockers must be a list")
        blockers = []
    ids = [b.get("id") for b in blockers if isinstance(b, dict)]
    if len(ids) != len(set(ids)):
        bad.append("blocker ids repeat")
    for b in blockers:
        for field in ("id", "criterion", "problem", "evidence", "fix"):
            if not str((b or {}).get(field) or "").strip():
                bad.append(f"blocker {(b or {}).get('id', '?')} has no {field}")
    if r.get("verdict") == "approve" and blockers:
        bad.append("an approve has no blockers")
    if r.get("verdict") == "block" and not blockers:
        bad.append("a block needs at least one blocker")
    if len(r.get("notes", [])) > 3:
        bad.append("at most three notes")
    for i, f in enumerate(r.get("issues_found") or [], 1):
        if not isinstance(f, dict) or not all(str(f.get(k, "")).strip() for k in ("title", "why", "evidence")):
            bad.append(f"issue found {i} needs a title, why and evidence")
    if "questions" in r:
        bad.append("the reviewer never asks the owner; escalate on round three instead")
    return bad


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


ASSUMPTION_SHAPE = ('{"question": "the plan\'s question", "accepted": true | false, "changes": true | false, '
                    '"matched": "the owner\'s words", "source": "where they said them"} (or "why" when not accepted)')


def issue_url(number):
    """The link of the issue on GitHub."""
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{number}"


def owner_source(source, number):
    """True when a source names the owner's words Dokima can check: the issue's own text, one of its comments, or AGENTS.md."""
    return source == "AGENTS.md" or bool(re.fullmatch(re.escape(issue_url(number)) + r"(#issuecomment-\d+)?", source))


def problems_assumptions(r, plan, number):
    """Everything wrong with a plan review's judgements of the plan's questions: every question judged once, each
    saying whether its assumption is accepted and whether it changes how the system works or what it costs; one
    accepted never changes them and names the owner's words and where they said them; one not accepted says why."""
    qs = [q.get("question") for q in plan.get("questions") or [] if isinstance(q, dict)]
    judged = r.get("assumptions", [])
    if not isinstance(judged, list):
        return [f"assumptions must be a list, one per question of the plan, each {ASSUMPTION_SHAPE}"]
    bad, seen = [], []
    for i, a in enumerate(judged, 1):
        if not isinstance(a, dict):
            bad.append(f"assumptions item {i} must be an object, {ASSUMPTION_SHAPE}")
            continue
        q = a.get("question")
        label = f"the assumption of \"{q}\""
        if q not in qs:
            bad.append(f"assumptions item {i} judges \"{q}\", which is not a question of the plan")
            continue
        seen.append(q)
        if not isinstance(a.get("accepted"), bool):
            bad.append(f"{label} needs accepted: true or false")
        if not isinstance(a.get("changes"), bool):
            bad.append(f"{label} needs changes: true or false, whether it changes how the system works or what it costs")
        if a.get("accepted") is True:
            if a.get("changes") is True:
                bad.append(f"{label} is accepted though it changes how the system works or what it costs (changes is "
                           "true): only the owner accepts such an assumption")
            if not filled(a.get("matched")):
                bad.append(f"{label} is accepted with no matched words: quote the owner's words it matches")
            if not filled(a.get("source")) or not owner_source(a["source"].strip(), number):
                bad.append(f"{label} needs a source: {issue_url(number)}, one of its comments' links, or AGENTS.md")
        elif a.get("accepted") is False and not filled(a.get("why")):
            bad.append(f"{label} is not accepted and needs why")
    for q in qs:
        if seen.count(q) != 1:
            bad.append(f"the assumption of \"{q}\" must be judged exactly once in assumptions, {ASSUMPTION_SHAPE}")
    return bad


def problems_work(w):
    """Everything wrong with a work.json, as plain sentences; empty when it is well formed."""
    bad = []
    if not str(w.get("summary", "")).strip():
        bad.append("summary is empty")
    if not isinstance(w.get("criteria"), dict) or not w["criteria"]:
        bad.append("criteria must give one line per criterion")
    if not str(w.get("evidence", "")).strip():
        bad.append("evidence is empty: name the last test command and its result line")
    for r in w.get("replies", []):
        if r.get("answer") not in ANSWERS or not str(r.get("why", "")).strip() or not r.get("blocker"):
            bad.append(f"reply to {r.get('blocker', '?')} needs a blocker id, fixed or disagree, and why")
    for s in w.get("suspect_tests", []):
        if not s.get("test") or not str(s.get("evidence", "")).strip():
            bad.append("every suspect test needs the test and the evidence")
    if "questions" in w:
        bad.append("the worker never asks the owner; the plan is the contract")
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
    bad = []
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
        bad += problems_items(h, "blockers", ("id", "criterion", "problem", "evidence", "fix"), name="id")
        for i, b in enumerate(h.get("blockers") if isinstance(h.get("blockers"), list) else [], 1):
            if isinstance(b, dict) and ("test" not in b or not (b["test"] is None or isinstance(b["test"], str))):
                bad.append(f"blockers item {i}" + (f" ({b.get('id')})" if filled(b.get("id")) else "") + " needs test: a test name, or null")
            if isinstance(b, dict) and b.get("fixer") not in FIXERS:
                bad.append(f"blockers item {i}" + (f" ({b.get('id')})" if filled(b.get("id")) else "") + " needs fixer: worker or planner")
        bad += problems_items(h, "notes", ("text", "evidence"))
        bad += problems_items(h, "outside_plan", ("file", "change"))
        bad += problems_items(h, "issues_found", ("title", "why", "evidence"))
        resolved = h.get("resolved", [])
        if not isinstance(resolved, list) or not all(filled(x) for x in resolved):
            bad.append("resolved must be a list of blocker ids")
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
    bad += problems_items(h, "outside_scope", ("file", "why"))
    bad += problems_items(h, "suspect_tests", ("test", "evidence"))
    bad += problems_items(h, "replies", ("blocker", "answer", "why"), name="blocker")
    for i, r in enumerate(h.get("replies") if isinstance(h.get("replies"), list) else [], 1):
        if isinstance(r, dict) and filled(r.get("answer")) and r["answer"] not in ANSWERS:
            bad.append(f"replies item {i}: answer must be fixed or disagree")
    return bad


def plan_criteria(plan, number):
    """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each story of a split."""
    count = lambda p: sum(len(p.get(k)) for k in ("acceptance_criteria", "non_functional") if isinstance(p.get(k), list))
    if plan.get("kind") == "feature":
        stories = plan.get("stories") if isinstance(plan.get("stories"), list) else []
        return [f"S{s}.{k}" for s, st in enumerate(stories, 1) if isinstance(st, dict) for k in range(1, count(st) + 1)]
    return [f"{number}.{k}" for k in range(1, count(plan) + 1)]


def problems_plan(kind, h, plan, number):
    """Everything in a hand-back that does not match the approved plan: a work line per criterion, exactly, and every
    blocker on one of the plan's criteria, naming either no test or one of the plan's tests for that criterion."""
    ids = plan_criteria(plan, number)
    bad = []
    if kind == "work":
        crit = h.get("criteria")
        if isinstance(crit, dict):
            bad += [f"criteria has no line for {c}, a criterion of the plan" for c in ids if c not in crit]
            bad += [f"criteria gives a line for {c}, which the plan does not have" for c in crit if c not in ids]
        return bad
    tests = plan.get("tests") if isinstance(plan.get("tests"), dict) else {}
    for b in h.get("blockers") if isinstance(h.get("blockers"), list) else []:
        if not isinstance(b, dict) or not filled(b.get("criterion")):
            continue
        c, t = b["criterion"], b.get("test")
        if c not in ids:
            bad.append(f"blocker {b.get('id')} names {c}, which is not a criterion of the plan ({', '.join(ids) or 'none'})")
        elif filled(t) and t not in (tests.get(c) or []):
            bad.append(f"blocker {b.get('id')} names {t}, which is not one of the plan's tests for {c}")
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
                bad += problems_assumptions(data, plan, number)
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
    """The issue a pull request was built for: from its branch (work/issue-N or try/issue-N), else 'Closes #N'."""
    m = re.match(r"(?:work|try)/issue-(\d+)$", head or "") or re.search(r"(?i)\b(?:closes|fixes|resolves) #(\d+)", body or "")
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


PLAN_CHECK = "done-whens.yml"


def rerun_plan_check(repo, number):
    """Run the plan check again, in full, on the open pull request's head after approval.

    The plan check reads the issue's records only when the pull request gets a new commit, so an approval with
    nothing new to push would keep its stale "No approved plan found". Only the newest plan check run on the current
    head runs again; older commits and other workflows are left alone. With no open pull request, or no plan check on
    its head yet (GitHub runs it on the next push), nothing runs. When the check cannot run again, the pull request
    gets one comment saying why. Returns what happened, one line."""
    pr = gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
            "-q", ".[0].number").strip()
    if not pr.isdigit():
        return "No open pull request: no plan check to run again."
    sha = gh("pr", "view", pr, "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip()
    found = json.loads(gh("api", f"repos/{repo}/actions/workflows/{PLAN_CHECK}/runs?head_sha={sha}"))
    runs = [r for r in found.get("workflow_runs") or [] if r.get("head_sha") == sha]
    if not runs:
        return f"PR #{pr} has no plan check on {sha[:7]} yet: GitHub runs it on the next push."
    run = max(runs, key=lambda r: r["id"])
    why = None
    if run.get("status") != "completed":
        why = f"it is still running ({run.get('status')}) from the last push, so it may still read the plan before its approval"
    else:
        try:
            gh("api", "-X", "POST", f"repos/{repo}/actions/runs/{run['id']}/rerun")
        except subprocess.CalledProcessError as e:
            why = f"GitHub refused: {gh_reason(e)}"
    if why is None:
        return f"Ran the plan check on {sha[:7]} of PR #{pr} again."
    url = run.get("html_url") or f"https://github.com/{repo}/actions/runs/{run['id']}"
    gh("pr", "comment", pr, "-R", repo, "--body",
       f"The plan of #{number} is approved, but the plan check on {sha[:7]} could not run again: {why}. "
       f"Re-run all its jobs once it can, so it reads the approved plan: {url}")
    return f"The plan check on {sha[:7]} of PR #{pr} could not run again: {why}."


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


def start_waiting(repo, numbers, need_blocker=False, line=AUTOPILOT_LINE):
    """Start the planner of every open issue among `numbers` with no sub-issues, nothing open blocking it and nothing
    started on it yet; with need_blocker, only those blocked by at least one issue (all now closed). Returns those started."""
    started = []
    for n in numbers:
        if json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("state") != "open" or sub_issues(repo, n):
            continue
        blockers = blocked_by(repo, n)
        if (need_blocker and not blockers) or any(b.get("state") != "closed" for b in blockers):
            continue
        if started_before(repo, n):
            continue
        start_planner(repo, n, line)
        started.append(n)
    return started


WAIT_LINE = "Autopilot: plan approved, waiting for {} to close"
GO_LINE = "Autopilot: blockers closed, starting work"


def open_blockers_of(repo, number):
    """The numbers of the open issues blocking this one on GitHub, oldest first."""
    return sorted(b["number"] for b in blocked_by(repo, number) if b.get("state") != "closed")


def worker_waits(items, owners, body, number):
    """True when the issue's approved newest plan still waits for its worker to start.

    The river would have started its worker on autopilot, and no worker started since the approval: no `/work` from
    the owner, no worker record and no Autopilot line starting it."""
    if not approved(records(items)):
        return False
    at = max(i for i, c in enumerate(items) if is_record(c, "reviewer", "plan") and records([c])[0].get("check", {}).get("passed"))
    for c in items[at + 1:]:
        who, said = (c.get("author") or {}).get("login"), (c.get("body") or "").strip()
        if (who in owners and command_of(c.get("body")) == "worker") or is_record(c, "worker") \
                or (who in (BOT, f"{BOT}[bot]") and said in (AUTOPILOT_LINES["worker"], GO_LINE)):
            return False
    step = next_step(items[:at], records([items[at]])[0], owners, autopilot=lambda: True, body=body, number=number)
    return step[:2] == ("start", "worker") and step[3:] == ("autopilot",)


def start_worker(repo, number):
    """Start the issue's worker with the river's own signal, after one Autopilot line.

    The line stands where the owner would have said /work, and goes first: it is the record that the worker was started, so no later close starts it again."""
    gh("issue", "comment", str(number), "-R", repo, "--body", GO_LINE)
    gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next", "-f", "client_payload[role]=worker",
       "-f", "client_payload[stage]=", "-f", f"client_payload[issue]={number}")


def start_blocked_workers(repo, numbers, owners):
    """Start the worker of every waiting issue among `numbers` whose blockers have all closed.

    An issue waits with an approved plan whose worker has not started, and must have been blocked. Returns (the issues whose worker waits, what was done as lines): a waiting issue never starts
    its planner. When GitHub cannot list an issue's blockers its worker does not start and the issue says why."""
    waits, did = [], []
    for n in numbers:
        d, items = conversation(repo, n)
        if not worker_waits(items, owners, d.get("body") or "", n):
            continue
        waits.append(n)
        try:
            blockers = blocked_by(repo, n)
        except subprocess.CalledProcessError as e:
            gh("issue", "comment", str(n), "-R", repo, "--body",
               f"Autopilot did not start the worker: GitHub could not list the issues blocking #{n}: {gh_reason(e)}.")
            did.append(f"could not list the blockers of #{n}")
            continue
        if blockers and all(b.get("state") == "closed" for b in blockers):
            start_worker(repo, n)
            did.append(f"started the worker for #{n}")
    return waits, did


def tree_done_comment(number):
    """The comment a parent closes with when its last sub-issue closed on autopilot."""
    return f"Every issue under #{number} is closed, so its whole tree is done and it closes.\n"


def autopilot_closed(repo):
    """What autopilot does when an issue closes, worked out from GitHub's state of every issue on autopilot, so a close
    whose own run never went is still handled by the next one. Returns what it did, as lines.

    Every open parent on autopilot whose sub-issues are all closed closes as completed, saying its tree is done, and
    counts as a close one level up in turn. Every closed issue on autopilot with no parent on autopilot is the top of a
    done tree: the tree goes off autopilot. Then every open issue left on autopilot that was blocked and whose blockers
    have all closed starts its worker when its approved plan waits for one, else its planner, unless something already
    started on it."""
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
    # An approved plan whose worker waited on its blockers starts its worker; such an issue never plans again.
    workers, lines = start_blocked_workers(repo, waiting, owners)
    did += lines
    waiting = [n for n in waiting if n not in workers]
    did += [f"started the planner for #{n}" for n in start_waiting(repo, waiting, need_blocker=True)]
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
    """True when a record is a code review, passed by code, that approves the pull request."""
    return (rec.get("role") == "reviewer" and (rec.get("stage") or "") == "pr" and bool(rec.get("check", {}).get("passed"))
            and (rec.get("handback") or {}).get("verdict") == "approve")


def work_approved(recs):
    """True when the issue's newest planner, worker or reviewer record is a code review approving the pull request."""
    newest = next((r for r in reversed(recs) if r.get("role") in HANDBACK), None)
    return bool(newest) and approves_work(newest)


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


def automerge(repo, number):
    """On autopilot, merge the open pull request built for the issue; when it merges, the issue gets one Autopilot
    line. Returns (pull request or '', merged, why)."""
    try:
        pr = open_pr(repo, number)
    except subprocess.CalledProcessError as e:
        return "", False, " ".join((e.stderr or str(e)).split())
    if not pr:
        return "", False, "there is no open pull request built for it"
    merged, why = try_merge(repo, pr)
    if merged:
        gh("issue", "comment", str(number), "-R", repo, "--body", f"Autopilot: merged PR #{pr}")
    return pr, merged, why


def merge_tree(repo, number, owners):
    """`/autopilot start`: merge every open pull request in the issue's tree whose newest record is its code review's
    approval. One that cannot merge says why on itself and mentions the owner. Returns what merged, as (issue, pr)."""
    done, mention = [], " ".join(f"@{o}" for o in owners)
    for n in issue_tree(repo, number):
        if not open_pr(repo, n) or not work_approved(records(conversation(repo, n)[1])):
            continue
        pr, merged, why = automerge(repo, n)
        if merged:
            done.append((n, pr))
        elif pr:
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


def said_there(words, source, items, body, owners, number):
    """True when the words appear word for word where the source says: the issue's own text, a code owner's comment on
    this issue, or AGENTS.md. Anything else, a comment by anyone else (the bot included) or one not found, is False."""
    flat = lambda t: " ".join((t or "").split())
    words, source = flat(words), (source or "").strip()
    if not words or not owner_source(source, number):
        return False
    if source == "AGENTS.md":
        return words in flat(agents_text())
    if source == issue_url(number):
        from dokima.body import ask
        return words in flat(ask(body))
    return any(c.get("url") == source and (c.get("author") or {}).get("login") in owners and words in flat(c.get("body"))
               for c in items)


def not_accepted(items, h, owners, body, number):
    """The questions of the reviewed plan whose assumption the review did not accept on the owner's real words."""
    plan = latest(records(items), "planner")
    qs = [q.get("question") for q in ((plan or {}).get("handback") or {}).get("questions") or [] if isinstance(q, dict)]
    ok = {a.get("question") for a in h.get("assumptions") or [] if isinstance(a, dict) and a.get("accepted") is True
          and a.get("changes") is False and said_there(a.get("matched"), a.get("source"), items, body, owners, number)}
    return [q for q in qs if q not in ok]


def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number=""):
    """The river: what follows the run that just finished. ("start", role, stage) or ("stop", why), decided by code.

    A planner hands to the reviewer unless it has questions for the owner and the issue is not on autopilot. A worker
    hands to the reviewer. A blocking review sends the work back, until three blocks in a row at that stage since the
    owner last spoke; then it is the owner's call. On autopilot (`autopilot()` says, None when GitHub cannot), an
    approved plan goes to the worker and an approved split is filed, each ("start", role, stage, "autopilot"), once
    the plan reviewer accepted every question's assumption on the owner's real words; a question not accepted stops.
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
        if h.get("questions"):
            asked = "The plan has questions for you. Answer with `/plan` and your words, or say `/review` to go on with its assumptions."
            on = autopilot()
            if on is None:
                return ("stop", f"{UNREAD} {asked}")
            return ("start", "reviewer", "plan") if on else ("stop", asked)
        return ("start", "reviewer", "plan")
    if role == "worker":
        return ("start", "reviewer", "pr")
    if role == "updater":
        # A clash with main goes to the planner by itself: the plan may not fit main anymore.
        return ("start", "planner", "")
    if role != "reviewer":
        return ("stop", "")
    verdict = h.get("verdict")
    plan = (latest(records(items), "planner") or {}).get("handback") or {}
    if stage == "plan" and verdict in ("approve", "block") and plan.get("questions"):
        on = autopilot()
        if on is None:
            return ("stop", f"{UNREAD} The plan has questions for you. Answer with `/plan` and your words.")
        left = not_accepted(items, h, owners, body, number) if on else []
        if left:
            return ("stop", "The reviewer did not accept the plan's assumption for: " + " ".join(f"\"{q}\"" for q in left)
                    + " Answer with `/plan` and your words" + (", or say `/work` to build it on its assumptions." if verdict == "approve" else "."))
    if verdict == "approve" and stage == "plan" and test_fix(items, owners):
        return ("start", "worker", "")
    if verdict == "approve" and stage == "plan":
        on = autopilot()
        if on:
            return ("start", "split" if plan.get("kind") == "feature" else "worker", "", "autopilot")
        why = "The plan is approved. Say `/work` to build it, or `/plan` with changes."
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
    to_planner = stage == "plan" or any(isinstance(b, dict) and b.get("fixer") == "planner" for b in h.get("blockers", []))
    return ("start", "planner" if to_planner else "worker", "")


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
    if not r.get("check", {}).get("passed") or h.get("verdict") != "block" or \
            not any(isinstance(b, dict) and b.get("fixer") == "planner" for b in h.get("blockers", [])):
        return False
    replan = latest(records(items[review + 1:]), "planner")
    agreed = latest(records(items[:works[-1]]), "planner")
    return bool(replan and agreed) and criteria_texts(replan["handback"]) == criteria_texts(agreed["handback"])


STAGE_COLUMN = {("planner", ""): "Plan", ("reviewer", "plan"): "Plan", ("worker", ""): "Work", ("reviewer", "pr"): "Review"}


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


def move_card(repo, number, column, needs_you, spec, q=None):
    """Put the issue and its open pull request in that column, with the Needs you pill when the river stops for the
    owner, else the Autopilot pill while the issue is on autopilot."""
    from dokima import board
    b = board.Board(spec, repo, q or board.gql)
    targets = [("issue", int(number))]
    pr = gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number", "-q", ".[0].number").strip()
    if pr:
        targets.append(("pr", int(pr)))
    pill = "Needs you" if needs_you else "Autopilot" if b.autopilot("issue", int(number)) else None
    for kind, n in targets:
        iid = b.item(kind, n)
        b.set(iid, "Status", column)
        b.set(iid, "Action", pill)
    return targets


def next_line(step, owners):
    """The last line of a card: what happens next, mentioning the owner when it is their turn."""
    if step[0] == "start" and step[1] == "split":
        return "**Next:** The split's stories are filed now."
    if step[0] == "start":
        who = {"planner": "The planner", "worker": "The worker", "reviewer": "The reviewer"}[step[1]]
        return f"**Next:** {who} starts now."
    if step[0] in ("cancelled", "merged", "waiting"):
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
    agent recheck N OUT  (once OUT's plan review approved, runs the plan check of N's open pull request again)"""
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
        rec = build_record(role, stage, out, text, passed == "true", meta)
        if role == "planner" and isinstance(rec["handback"], dict):
            # The first docstring line of each of the plan's tests, read now from the planner's own test files.
            rec["verified_by"] = verified_by(rec["handback"])
        if role == "worker":
            # Kept in the record, so the comment redrawn once its pull request opens still names them.
            rec["files_changed"] = files_changed(os.environ.get("BASE"))
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        reviewed = os.path.join(os.environ.get("PACK", ""), "plan.json")
        plan = None
        if role == "reviewer" and os.environ.get("PACK") and os.path.exists(reviewed):
            try:
                plan = json.load(open(reviewed))
            except (OSError, json.JSONDecodeError):
                plan = None
        open(os.path.join(out, "comment.md"), "w").write(render(rec, plan=plan if isinstance(plan, dict) else None))
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
        step = next_step(items, rec, owners, autopilot=autopilot, body=d.get("body") or "", number=number)
        if approves_work(rec):
            # On autopilot the code review's approval stands in for the owner's: the pull request merges by itself.
            on = autopilot()
            if on is None:
                step = ("stop", f"{UNREAD} {step[1]}")
            elif on:
                pr, merged, why = automerge(repo, number)
                step = ("merged", f"Autopilot merged PR #{pr}; what it unblocks starts when the issue closes.") if merged else \
                    ("stop", f"Autopilot did not merge the pull request: {why}. It waits for you: merge it, or review it "
                             "with a command to send it back.")
        if rec.get("role") == "reviewer" and (rec.get("stage") or "") == "plan" and rec.get("check", {}).get("passed") \
                and (rec.get("handback") or {}).get("verdict") == "approve":
            # Code records the approved plan's links on GitHub and redraws the cards they touch; anything that keeps
            # a link from being recorded stops the river, so autopilot never starts work that should wait.
            why = record_links(repo, number, items)
            if why:
                step = ("stop", why)
            elif step[:2] == ("start", "worker") and step[3:] == ("autopilot",):
                # On autopilot the worker of a blocked issue waits until every issue blocking it closes.
                try:
                    left = open_blockers_of(repo, number)
                except subprocess.CalledProcessError as e:
                    left, step = None, ("stop", f"GitHub could not list the issues blocking #{number}, so the worker "
                                                f"did not start: {gh_reason(e)}. Say `/work` once GitHub answers.")
                if left:
                    gh("issue", "comment", str(number), "-R", repo, "--body", WAIT_LINE.format(named(left)))
                    step = ("waiting", f"The worker starts by itself when {named(left)} close.")
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
        with open(os.path.join(out, "comment.md"), "a") as f:
            f.write("\n" + next_line(step, owners) + "\n")
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
            print(rerun_plan_check(os.environ["GITHUB_REPOSITORY"], argv[2]))
        else:
            print("The plan was not approved: the plan check stays as it is.")
        return 0
    if argv[1] == "board":
        spec = os.environ.get("DOKIMA_BOARD", "").strip()
        if not spec:
            print("No board set; nothing to move.")
            return 0
        try:
            column, needs = open(os.path.join(argv[3], "board.txt")).read().split()
        except (OSError, ValueError):
            # Deciding what follows failed, so the river stopped: the run's own stage, with Needs you.
            try:
                rec = json.load(open(os.path.join(argv[3], "record.json")))
            except (OSError, json.JSONDecodeError):
                rec = {"role": os.environ.get("ROLE", ""), "stage": os.environ.get("STAGE", "")}
            column, needs = board_place(rec if isinstance(rec, dict) else {}, ("stop",))
            needs = "needs" if needs else "none"
        for kind, n in move_card(os.environ["GITHUB_REPOSITORY"], argv[2], column, needs == "needs", spec):
            print(f"board: {kind} #{n} -> {column}{' · Needs you' if needs == 'needs' else ''}")
        return 0
    if argv[1] == "autopilot":
        switch, number = argv[2], argv[3]
        repo = os.environ["GITHUB_REPOSITORY"]
        switched = switch_autopilot(repo, number, switch)
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
        for line in autopilot_closed(os.environ["GITHUB_REPOSITORY"]) or [f"#{argv[2]} closed: nothing on autopilot to do."]:
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

"""Roles and packs: each role's starting pack and the commands that start them.

Also the command line, `main`. Split out of dokima/agent.py (#636).
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse

from dokima import agents, body as issue_body, hotfix


def issue_text(d, items):
    """The issue as it stands: title, body and every comment, oldest first.

    Records come from the record files, in in/ (#610), so a record comment's JSON is never read: it points to in/
    instead."""
    parts = [f"# Issue #{d['number']}: {d['title']}", "", d["body"] or "", "", "## Comments"]
    for c in items:
        b = c["body"] or ""
        if (c.get("author") or {}).get("login") == BOT and MARK in b:
            b = re.sub(r"```json\n.*?\n```", "(full record: in/, from the record files)", b, count=1, flags=re.S)
        parts += ["", f"### {c['author']['login']} on {c['where']} ({c['createdAt']})", "", b]
    return "\n".join(parts) + "\n"


def open_issue_summary(text):
    """An issue's summary: its plan summary, story, or its ask's first sentence.

    An empty body gives none."""
    text = text or ""
    top = text.split(issue_body.MARKER, 1)[0] if issue_body.MARKER in text else ""
    m = re.search(r"<!-- dokima-card -->\n(.*?)<!-- /dokima-card -->", top, re.S)
    if m:
        first = next((l.strip() for l in m.group(1).splitlines() if l.strip() and not l.strip().startswith("<!--")), "")
        if first and not first.startswith(("**", "<")):
            return first
    owner = issue_body.ask(text)
    if issue_body.STORY.match(owner):
        story = re.search(r"^\*\*User story:\*\* (.*)$", owner, re.M)
        if story:
            return story.group(1).strip()
    return first_sentence(owner) if owner.strip() else ""


def reviewer_open_issues(repo):
    """Every open issue for the reviewer: number, title, summary, link and whether Dokima filed it.

    GitHub failing to list them fails the pack, never an empty list."""
    items = [i for p in pages(agent_github.gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    return [{"number": i["number"], "title": i["title"], "summary": open_issue_summary(i.get("body")),
             "link": i.get("html_url") or f"{server}/{repo}/issues/{i['number']}",
             "filed_by_dokima": (i.get("user") or {}).get("login") == BOT_LOGIN}
            for i in items if "pull_request" not in i]


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


def parent_words(repo, number):
    """The parent issue's number, text and comments; None when none or GitHub cannot say."""
    up = parent_of(repo, number)
    if not up:
        return None
    try:
        d = json.loads(agent_github.gh("issue", "view", str(up), "-R", repo, "--json", "number,body,comments"))
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


def committed_words(repo, number, owners):
    """The lines each code owner added on the issue's branch, as {commit link: text}.

    Text the owner commits is their words (#708). A commit by anyone else gives nothing. No branch yet, or GitHub failing, gives none, and says why."""
    out = {}
    try:
        compare = json.loads(agent_github.gh("api", f"repos/{repo}/compare/main...try/issue-{number}"))
        for c in compare.get("commits") or []:
            if (c.get("author") or {}).get("login") not in owners:
                continue
            full = json.loads(agent_github.gh("api", f"repos/{repo}/commits/{c['sha']}"))
            added = [line[1:] for f in full.get("files") or [] for line in (f.get("patch") or "").splitlines()
                     if line.startswith("+") and not line.startswith("+++")]
            out[c.get("html_url") or full.get("html_url")] = "\n".join(added)
    except Exception as e:  # noqa: BLE001 - any failure means GitHub did not say: no commit counts
        why = gh_reason(e) if isinstance(e, subprocess.CalledProcessError) else str(e)
        print(f"No commit on try/issue-{number} counts as the owner's words: {why or 'GitHub named none'}", file=sys.stderr)
        return {}
    return out


def owner_words(repo, number, d, items, owners):
    """Where the owner said things, as {link: text}: the issue's own ask, each code owner's
    comment, the lines they committed on the issue's branch, and the parent issue's ask and their comments on it. Every
    criterion of a plan must quote words found at its source link (#416)."""
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
    out.update(committed_words(repo, number, owners))
    return out


class TurnHeld(Exception):
    """The worker's pack is not built: another story holds the turn on a shared file."""


def pack(repo, number, role, stage, dest):
    """Build the starting pack for one role and stage.

    The issue and its PRs' conversation from GitHub, every agent record so far from the record files (#610),
    the open raises this role must answer (open_blockers.json), the newest passed plan, the issue's parent on GitHub (parent.json, naming none when it has none or GitHub cannot
    say), the owner's words with the parent's ask and the owner's comments on it, for every role (owner_words.json, #708) and, for the planner and the reviewer, every open issue of the repo. The pull request review also gets the worker's session log from its run."""
    d, items = conversation(repo, number)
    # Every earlier record comes from its record file on the logs branch, never from a comment (#610).
    recs = saved_records(repo, number)
    listed = open_issues(repo) if role == "planner" else reviewer_open_issues(repo) if role == "reviewer" else None
    os.makedirs(os.path.join(dest, "in"), exist_ok=True)
    json.dump({"number": parent_of(repo, number)}, open(os.path.join(dest, "parent.json"), "w"))
    if listed is not None:
        json.dump(listed, open(os.path.join(dest, "open_issues.json"), "w"), indent=1)
    # Every role on a story reads the parent's ask and the owner's words, not only the planner (#708).
    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
    json.dump(owner_words(repo, number, d, items, owners), open(os.path.join(dest, "owner_words.json"), "w"), indent=1)
    # The open raises this agent must answer; the file keeps the name the workflows give it.
    json.dump(raises_for(recs, role), open(os.path.join(dest, "open_blockers.json"), "w"), indent=1)
    open(os.path.join(dest, "issue.md"), "w").write(issue_text(d, items))
    for i, r in enumerate(recs, 1):
        json.dump(r, open(os.path.join(dest, "in", name_of(r, i)), "w"), indent=1)
    plan = latest(recs, "planner")
    if (role == "worker" or stage == "pr") and os.environ.get("HOTFIX_LABEL") == "true" and not hotfix.planned(recs):
        # A hotfix has no plan: its worker and its code review get the issue's text as the whole ask (#863). The
        # workflow read its label from GitHub before the pack.
        hotfix.write_ask(dest, d.get("body"))
        if stage == "pr":
            work = latest(recs, "worker", passed=False)
            if work and work.get("run_id"):
                agent_github.gh("run", "download", str(work["run_id"]), "-R", repo, "-n", f"worker-{number}", "-D", os.path.join(dest, "worker-run"))
        return True
    if role == "worker" and not approved(recs):
        return False
    if role == "worker":
        # A story's build waits while another story sharing a code file builds, until that one merges (#668).
        from dokima import turns
        try:
            held = turns.holder(repo, number, recs)
        except subprocess.CalledProcessError as e:
            raise TurnHeld(f"GitHub could not list the stories sharing files with #{number}: {gh_reason(e)}")
        if held:
            raise TurnHeld(turns.waits_line(held))
    if plan:
        json.dump(plan["handback"], open(os.path.join(dest, "plan.json"), "w"), indent=1)
    if stage == "pr":
        work = latest(recs, "worker", passed=False)
        if work and work.get("run_id"):
            agent_github.gh("run", "download", str(work["run_id"]), "-R", repo, "-n", f"worker-{number}", "-D", os.path.join(dest, "worker-run"))
    return bool(plan)


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
    needs = NEEDS[key]
    if key in ("worker", "reviewer-pr") and os.path.isfile(os.path.join(dest, hotfix.ASK)) \
            and not os.path.exists(os.path.join(dest, "plan.json")):
        # A hotfix's ask is the issue's text, in place of a plan (#863).
        needs = [hotfix.ASK if n == "plan.json" else n for n in needs]
    for name in needs:
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


HOTFIX_NO_PR = ("A hotfix has no plan to review. Code review starts once its pull request opens; "
                "then say `/review` here or on the pull request.")


def hotfix_route(repo, r):
    """A hotfix issue's /review goes to code review, never plan review (#892).

    A hotfix has no plan: with an open pull request, /review on the issue reviews that pull request; with none, it starts
    nothing and says why on the issue. Any other route comes back as it was."""
    if not r or r.get("role") != "reviewer" or r.get("stage") != "plan":
        return r
    number = r["issue"]
    if not hotfix.labeled(repo, number) or hotfix.planned(saved_records(repo, number)):
        return r
    if open_pr(repo, number):
        return {**r, "stage": "pr"}
    agent_github.gh("issue", "comment", str(number), "-R", repo, "--body", HOTFIX_NO_PR)
    return None


def scrubbed(value, secrets):
    """value with every secret removed from each string it holds, in the same shape."""
    if isinstance(value, str):
        return scrub(value, secrets)
    if isinstance(value, list):
        return [scrubbed(v, secrets) for v in value]
    if isinstance(value, dict):
        return {scrubbed(k, secrets): scrubbed(v, secrets) for k, v in value.items()}
    return value


def main(argv):
    """agent pack N ROLE STAGE DIR | agent check-pack ROLE STAGE DIR | agent check
    review|work FILE PLAN|- N | agent record ROLE STAGE OUT CHECK_FILE PASSED LOG_DIR  (writes OUT/record.json and
    OUT/comment.md) | agent not-started ROLE STAGE OUT WHY_FILE  (the same, for a run or command that failed before its
    agent started) | agent cancelled ROLE STAGE OUT STARTED LOG_DIR  (the same, for a run someone cancelled) | agent
    card ROLE STAGE ready|working  (prints the run's live card, which is not a record) | agent queue ROLE STAGE N
    [queued|handoff]  (puts up a run's queued card where its record will go, prints its id) | agent unrecorded ROLE
    STAGE N OUT  (a failed record for this run when it ended before posting one) | agent autopilot start|stop N [OUT]
    (switches N's issue tree on or off autopilot, prints the comment naming what switched; with OUT, `start` writes what
    it picks up to OUT/next.txt and its Autopilot line to OUT/autopilot.md) | agent closed N  (what autopilot does now
    that issue N closed, for every tree on autopilot) | agent recheck N OUT  (once OUT's plan review approved, runs
    every check of N's open pull request again) | agent save-record N OUT  (saves OUT/record.json as its own new file
    on the logs branch)"""
    if argv[1] == "save-record":
        print(save_record(os.environ["GITHUB_REPOSITORY"], argv[2], argv[3]))
        return 0
    if argv[1] == "pack":
        try:
            has_plan = pack(os.environ["GITHUB_REPOSITORY"], argv[2], argv[3], argv[4], argv[5])
        except RecordsUnreadable as e:
            sys.stderr.write(f"The pack has no history: {e}\n")
            return 1
        except TurnHeld as e:
            sys.stderr.write(f"The worker did not start: {e}\n")
            return 1
        return 0 if has_plan or argv[3] == "planner" else 3
    if argv[1] == "check":
        if len(argv) < 6:
            print("the check needs plan.json and the issue number: agent check review|work FILE PLAN N")
            return 1
        # A hotfix has no plan (#863): `-` in its place checks the hand-back's shape alone.
        return check(argv[2], argv[3], None if argv[4] == "-" else argv[4], argv[5])
    if argv[1] == "check-pack":
        bad = problems_pack(argv[2], argv[3], argv[4])
        for b in bad:
            print(b)
        return 1 if bad else 0
    if argv[1] == "record":
        role, stage, out, check_file, passed, log_dir = argv[2:8]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "commit_before": os.environ.get("BASE"),
                "started_by": os.environ.get("GITHUB_ACTOR"), "models": agents.models(role, out, log_dir),
                "report": agents.report(role, out), "log": os.environ.get("LOG_URL"),
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
        note = os.path.join(os.environ.get("PACK", ""), "no-baseline.txt")
        if role == "reviewer" and stage == "pr" and os.environ.get("PACK") and os.path.isfile(note):
            # The test step ran every test because no baseline was usable; the record says so, and why.
            rec["no_baseline"] = open(note).read().strip() or "no baseline was usable"
        if role == "worker":
            # Kept in the record, so the comment redrawn once its pull request opens still names them.
            rec["files_changed"] = files_changed(os.environ.get("BASE"))
            rec["branch"] = f"try/issue-{os.environ.get('N', '')}"
        # The record is public: every secret the step was given to remove (SCRUB_*) shows as [secret removed].
        secrets = [v for k, v in os.environ.items() if k.startswith("SCRUB_")]
        rec = scrubbed(rec, secrets)
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        reviewed = os.path.join(os.environ.get("PACK", ""), "plan.json")
        plan = None
        if role == "reviewer" and os.environ.get("PACK") and os.path.exists(reviewed):
            try:
                plan = json.load(open(reviewed))
            except (OSError, json.JSONDecodeError):
                plan = None
        open(os.path.join(out, "comment.md"), "w").write(scrub(render(rec, plan=plan if isinstance(plan, dict) else None,
                                                                      earlier=earlier), secrets))
        return 0
    if argv[1] == "not-started":
        role, stage, out, why_file = argv[2:6]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "started_by": os.environ.get("GITHUB_ACTOR"),
                "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
        rec = not_started(role, stage, open(why_file).read() if os.path.exists(why_file) else "", meta)
        rec = scrubbed(rec, [v for k, v in os.environ.items() if k.startswith("SCRUB_")])
        json.dump(rec, open(os.path.join(out, "record.json"), "w"), indent=1)
        open(os.path.join(out, "comment.md"), "w").write(render(rec))
        return 0
    if argv[1] == "cancelled":
        role, stage, out, started, log_dir = argv[2:7]
        meta = {"run_id": os.environ.get("GITHUB_RUN_ID"), "started_by": os.environ.get("GITHUB_ACTOR"),
                "run": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"}
        if started == "true":
            meta.update({"models": agents.models(role, out, log_dir), "report": agents.report(role, out),
                         "log": os.environ.get("LOG_URL")})
        rec = scrubbed(cancelled(role, stage, started == "true", meta),
                       [v for k, v in os.environ.items() if k.startswith("SCRUB_")])
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
    if argv[1] == "unrecorded":
        role, stage, number, out = argv[2:6]
        posted = unrecorded(os.environ["GITHUB_REPOSITORY"], number, role, stage, out)
        print("Posted a failed record for this run." if posted else "This run posted its record; nothing to do.")
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
        # The role's agent reads its own session (ROLE, given after the folder); with none, Claude Code's, as before.
        sys.stdout.write(agents.transcript(argv[3], argv[2], secrets) if len(argv) > 3 else transcript(argv[2], secrets))
        return 0
    if argv[1] == "split":
        repo, parent = os.environ["GITHUB_REPOSITORY"], argv[2]
        _, items = conversation(repo, parent)
        recs = records(items)
        if not approved(recs) or latest(recs, "planner")["handback"].get("kind") != "feature":
            print("The newest plan is not an approved split.")
            return 1
        name = autopilot_label()
        on = name in {l["name"] for l in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{parent}")).get("labels", [])}
        rec = file_split(repo, parent, recs, [name] if on else [])
        rec["run"] = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
        card = os.environ.get("CARD_ID", "")
        if card:
            # The command's queued card becomes the Split filed record, edited in place.
            agent_github.gh("api", "-X", "PATCH", f"repos/{repo}/issues/comments/{card}", "-f", f"body={render(rec)}", "--silent")
        elif rec not in recs:
            agent_github.gh("issue", "comment", parent, "-R", repo, "--body", render(rec))
        spec = os.environ.get("DOKIMA_BOARD", "").strip()
        if spec:
            from dokima import board
            b = board.Board(spec, repo, board.gql)
            for f in rec["handback"]["stories"]:
                if f.get("kept"):
                    continue
                iid = b.item("issue", f["issue"])
                b.set(iid, "Status", "Backlog")
                b.set(iid, "Action", "Autopilot" if on else None)
            iid = b.item("issue", int(parent))
            b.set(iid, "Status", "Work")
            b.set(iid, "Action", "Autopilot" if on else None)
        if on:
            # On autopilot the stories go on too, and each one with nothing to wait for starts planning.
            start_waiting(repo, [f["issue"] for f in rec["handback"]["stories"] if not f["blocked_by"] and not f.get("kept")])
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
        d, items, unread, undecided = {}, [], [], False
        try:
            with rate_limit_waited_once():
                d, items = ({}, []) if rec.get("role") in ("not-started", "cancelled") else conversation(repo, number)
                read, unread = [], []

                def autopilot():
                    # Read once, and only when the river's decision turns on it.
                    if not read:
                        unread.append(True)
                        read.append(on_autopilot(repo, number, strict=True))
                        unread.clear()
                    return read[0]
                ups = []

                def parent():
                    # The parent's words, read once and only when an assumption cites somewhere other than this issue.
                    if not ups:
                        ups.append(parent_words(repo, number))
                    return ups[0]
                step = next_step(items, rec, owners, autopilot=autopilot, body=d.get("body") or "", number=number, parent=parent)
                gate = ""
                if approves_work(rec) and step[0] != "start":
                    # The merge gate runs first (#596): all tests on the pull request with main's newest commit. A
                    # failure sends the work back to the worker; only a pass goes on, to the owner or to autopilot.
                    pr = open_pr(repo, number)
                    gate, tested, why = merge_gate(repo, pr) if pr else ("stopped", "", "there is no open pull request built for it")
                    blocks = blocks_since_owner(items, owners, "pr") + 1
                    if gate == "failed" and blocks >= 3:
                        # A failed gate counts toward the three-blocks stop, as a blocking code review does (#601).
                        step = ("stop", f"{GATE_FAILED}: {why}. {blocks} blocks in a row without agreement. Your call: "
                                        "`/plan`, `/work` or `/review` with your words.")
                    elif gate == "failed":
                        step = ("start", "worker", "", "", f"{GATE_FAILED}: {why}.")
                    elif gate == "stopped":
                        step = ("stop", f"The merge gate did not pass: {why}. Give `/review` to run it again, or `/work` "
                                        "to send it back to the worker.")
                    else:
                        step = ("stop", "All tests passed with main's newest commit. Approve the pull request on GitHub "
                                        "to merge it, or review it with a command to send it back.")
                if gate == "passed":
                    # On autopilot the code review's approval stands in for the owner's: the pull request merges by itself.
                    on = autopilot()
                    if on is None:
                        step = ("stop", f"{UNREAD} {step[1]}")
                    elif on:
                        pr, how, why = automerge(repo, number, tested)
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
                    # Code records the approved plan's links on GitHub, and card.yml redraws the cards they touch; anything that keeps
                    # a link from being recorded stops the river, so autopilot never starts work that should wait.
                    why = record_links(repo, number, items)
                    renamed = set_title(repo, number, items)
                    if renamed:
                        why = f"{why} {renamed}" if why else renamed + " Say `/work` to go on, or `/plan` with changes."
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
                    if step[:2] == ("start", "worker"):
                        # Stories sharing a code file take turns to build (#668); planning and review never wait.
                        from dokima import turns
                        try:
                            held = turns.holder(repo, number, records(items))
                        except subprocess.CalledProcessError as e:
                            held, step = None, ("stop", f"GitHub could not list the stories sharing files with #{number}, "
                                                        f"so the worker did not start: {gh_reason(e)}. Say `/work` once GitHub answers.")
                        if held and step[3:] == ("autopilot",):
                            step = ("waiting", f"Nothing is built: {turns.waits_line(held)} The story plans again by "
                                               f"itself once #{held[0]} merges.")
                        elif held:
                            step = ("stop", f"Nothing is built: {turns.waits_line(held)} Say `/work` once #{held[0]} merges.")
                pack_dir = os.environ.get("PACK", "")
                if step[:2] == ("start", "planner") and rec.get("role") == "reviewer" and (rec.get("stage") or "") == "pr" \
                        and pack_dir and os.path.isfile(os.path.join(pack_dir, hotfix.ASK)) \
                        and not os.path.exists(os.path.join(pack_dir, "plan.json")):
                    # A hotfix sent back to planning says why on the issue itself, not only on its pull request (#863).
                    hotfix.back_to_planning(repo, number, rec)
        except subprocess.CalledProcessError as e:
            # Deciding what runs next needs GitHub; a call it refused, after the one wait for its rate limit, stops
            # for the owner with GitHub's own words, and nothing starts.
            undecided = True
            step = ("stop", (f"{UNREAD} GitHub's reason: " if unread else "GitHub refused a call while deciding what "
                             "runs next, so nothing starts by itself: ") + f"{gh_reason(e)}. Give the command again once "
                            "GitHub answers.")
        if rec.get("role") == "worker":
            # The pull request is opened after the record is written, so the worker's sentence links it only now.
            try:
                pr = agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
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
        if undecided:
            # GitHub refused the decision, so the board step must not wait on GitHub's state to show Needs you.
            open(os.path.join(out, "undecided"), "w").write("")
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
        if rec.get("role") == "cancelled" or os.path.exists(os.path.join(argv[3], "board.txt")) and (rec.get("check") or {"passed": True}).get("passed") \
                and not os.path.exists(os.path.join(argv[3], "undecided")):
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
        # The run failed, or deciding what follows did, so the river stopped: its own stage's column with Needs you, at once.
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
            labels = {l["name"] for l in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{said_on}")).get("labels", [])}
            name = autopilot_label()
            if name in labels:
                agent_github.gh("api", "-X", "DELETE", f"repos/{repo}/issues/{said_on}/labels/{urllib.parse.quote(name, safe='')}")
                switched.append(int(said_on))
        pick, dead = None, None
        if switch == "start":
            # A last run that ended with no record (its live card still up, its run over) starts that stage again.
            dead = unrecorded_run(repo, number)
            if dead:
                agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next",
                   "-f", f"client_payload[role]={dead[0]}", "-f", f"client_payload[stage]={dead[1] or 'plan'}",
                   "-f", f"client_payload[issue]={number}")
        if switch == "start" and len(argv) > 4 and not dead:
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
        if dead:
            picked = f"{who(*dead)}'s last run on #{number} ended with no record, so it starts again."
        started = []
        if switch == "start":
            # The issue itself starts its planner when it waits on nothing open and nothing started on it yet.
            started = [] if dead else start_waiting(repo, [int(number)], line=AUTOPILOT_START_LINE)
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
    if argv[1] == "labeled":
        # A person put the autopilot label on by hand: the issue starts its planner as `/autopilot start` would start it,
        # when it waits on nothing open and nothing started on it yet.
        # The label's name is the repo's own, from its settings; any other label starts nothing on this issue (#811).
        repo = os.environ["GITHUB_REPOSITORY"]
        if os.environ.get("LABEL", "") == autopilot_label():
            started = start_waiting(repo, [int(argv[2])], line=AUTOPILOT_START_LINE)
            print(f"started the planner for #{argv[2]}" if started else f"#{argv[2]} on autopilot: nothing to start yet.")
        else:
            print(f"#{argv[2]} got a label other than {autopilot_label()!r}: nothing to start on it.")
        # Labels put on together share one queue, where GitHub keeps one waiting run and cancels the rest, so this
        # run also starts every other issue on autopilot that waits on nothing and never started (#843).
        others = start_waiting(repo, [n for n in open_on_autopilot(repo) if n != int(argv[2])], line=AUTOPILOT_START_LINE)
        for n in others:
            print(f"started the planner for #{n}, whose own label run GitHub dropped")
        # A close waiting in the same queue was dropped too, so this run also does what autopilot does on a close (#853).
        for line in autopilot_closed(repo):
            print(line)
        return 0
    if argv[1] == "queue-failed":
        # A merge queue run failed (#830): put the pull request back once, then send it back to its worker.
        repo = os.environ["GITHUB_REPOSITORY"]
        owners = [o for o in os.environ.get("OWNERS", "").split(",") if o] or sorted(repo_approvers(repo.split("/")[0]))
        print(queue_failed(repo, os.environ.get("HEAD_REF", ""), os.environ.get("FAILED_RUN", ""),
                           os.environ.get("FAILED_RUN_URL", ""), owners))
        return 0
    if argv[1] == "route":
        on_pr = os.environ.get("ON_PR") == "true"
        head, pr_body = os.environ.get("HEAD", ""), ""
        if on_pr:
            p = json.loads(agent_github.gh("pr", "view", os.environ["NUMBER"], "-R", os.environ["GITHUB_REPOSITORY"], "--json", "headRefName,body"))
            head, pr_body = p["headRefName"], p["body"]
        r = hotfix_route(os.environ.get("GITHUB_REPOSITORY", ""),
                         route(os.environ.get("BODY", ""), on_pr, os.environ.get("NUMBER", ""), head, pr_body))
        for k, v in (r or {}).items():
            print(f"{k}={v}")
        return 0
    print(main.__doc__)
    return 2


# The other agent job files, imported last so the job files can use each other (#636).
from dokima import agent_github
from dokima.agent_github import (
    BOT, conversation, open_issues, BOT_LOGIN, parent_of, issue_of_pr, gh_reason, rate_limit_waited_once, pages)
from dokima.agent_records import (
    MARK, saved_records, save_record, RecordsUnreadable, name_of, records, latest, approved, raises_for, stamp_record, build_record, not_started, cancelled, live_card,
    unrecorded_run, unrecorded, queue, who, files_changed, render, jsonl_files, scrub, transcript, run_report,
    with_next, models_used, first_sentence, GATE_FAILED)
from dokima.agent_checks import problems_round, issue_url, check
from dokima.agent_autopilot import (
    file_split, AUTOPILOT, autopilot_label, issue_tree, switch_autopilot, autopilot_comment, AUTOPILOT_START_LINE, named,
    file_issues, record_links, set_title, rerun_checks, start_waiting, open_on_autopilot, open_blockers_of, close_done_parents,
    autopilot_closed, AUTOPILOT_LINES, UNREAD, on_autopilot, approves_work, merge_gate, open_pr, automerge,
    unconfirmed_comment, merge_tree, queue_failed)
from dokima.plan import repo_approvers
from dokima.agent_next import next_step, waiting, board_place, next_line, blocks_since_owner

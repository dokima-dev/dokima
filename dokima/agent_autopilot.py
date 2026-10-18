"""Autopilot and merging: switching autopilot, starting and closing issues, and the merge gate.

Also filing split stories and raised issues.

Split out of dokima/agent.py (#636).
"""
import json
import os
import re
import subprocess
import time
import urllib.parse

from dokima import body as issue_body, card, hotfix, manifest, raises, settings, upstream
from dokima.card import field_icon


def story_body(parent, i, story, parent_title):
    """A story's issue body, drawn by code from the approved plan, so the child planner
    starts from exactly what was agreed."""
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
    """File the stories of the newest approved split as sub-issues of the parent, in order,
    with their blocked-by links, each created with the given labels.

    Returns the record of what was filed. Filing twice files nothing new: a split record newer than the plan is returned
    instead. A re-plan approved after an earlier split was filed files only its new stories; a story already filed under
    the same title is kept as it is, marked kept."""
    splits = [i for i, r in enumerate(recs) if r.get("role") == "split" and r.get("check", {}).get("passed")]
    plans = [i for i, r in enumerate(recs) if r.get("role") == "planner" and r.get("check", {}).get("passed")]
    if splits and (not plans or splits[-1] > plans[-1]):
        return recs[splits[-1]]
    plan = latest(recs, "planner")["handback"]
    earlier = {f["title"]: f for i in splits for f in recs[i]["handback"].get("stories", [])}
    title = json.loads(agent_github.gh("issue", "view", str(parent), "-R", repo, "--json", "title"))["title"]
    filed = []
    for i, st in enumerate(plan["stories"], 1):
        if st["title"] in earlier:
            old = earlier[st["title"]]
            filed.append({"story": i, "issue": old["issue"], "title": st["title"], "id": old["id"],
                          "blocked_by": [d + 1 for d in st.get("depends_on", [])], "kept": True})
            continue
        extra = [x for label in labels for x in ("--label", label)]
        url = agent_github.gh("issue", "create", "-R", repo, "--title", st["title"], "--body", story_body(parent, i, st, title), *extra).strip()
        number = int(url.rstrip("/").split("/")[-1])
        node = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{number}"))["id"]
        agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={node}")
        filed.append({"story": i, "issue": number, "title": st["title"], "id": node,
                      "blocked_by": [d + 1 for d in st.get("depends_on", [])]})
    by_story = {f["story"]: f for f in filed}
    for f in filed:
        if f.get("kept"):
            continue
        for d in f["blocked_by"]:
            try:
                agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{f['issue']}/dependencies/blocked_by", "-F", f"issue_id={by_story[d]['id']}")
            except subprocess.CalledProcessError:
                f.setdefault("link_failed", []).append(by_story[d]["issue"])
    return {"role": "split", "stage": None, "handback": {"stories": filed}, "check": {"passed": True, "problems": []}}


AUTOPILOT = "autopilot"  # the autopilot label's default name; the repo's is in the labels setting (#787)


def autopilot_label():
    """The autopilot label's name in the labels setting."""
    return str((settings.read().get("labels") or {}).get("autopilot") or AUTOPILOT)


def issue_tree(repo, number):
    """The issue and every sub-issue under it, at every level, from GitHub's native sub-issues; parents first."""
    tree, todo = [], [int(number)]
    while todo:
        n = todo.pop(0)
        if n in tree:
            continue
        tree.append(n)
        # GitHub allows at most 100 sub-issues per parent, so one page holds them all.
        todo += [c["number"] for c in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}/sub_issues?per_page=100") or "[]")]
    return tree


def switch_autopilot(repo, number, switch):
    """Put the issue's tree on autopilot ("start") or take it off ("stop"), touching no other label; returns the
    issues switched: those whose autopilot label, by its name in settings, was added or removed."""
    switched, name = [], autopilot_label()
    for n in issue_tree(repo, number):
        labels = {l["name"] for l in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}")).get("labels", [])}
        if switch == "start" and name not in labels:
            # Adding a label GitHub does not have yet creates it.
            agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{n}/labels", "-f", f"labels[]={name}")
            switched.append(n)
        elif switch == "stop" and name in labels:
            agent_github.gh("api", "-X", "DELETE", f"repos/{repo}/issues/{n}/labels/{urllib.parse.quote(name, safe='')}")
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
# A hotfix starts its worker in place of its planner, with the line that says so (#863).
HOTFIX_LINES = {AUTOPILOT_LINE: "Autopilot: blockers merged, starting work",
                AUTOPILOT_START_LINE: "Autopilot: switched on, starting work"}


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


FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268), under its name in settings (#784)


def filed_label(repo):
    """The filed label's name in the labels setting, created in REPO when missing.

    It gets its color from the settings and its description from the manifest. A refused creation is left to the
    filing itself, which then says GitHub's reason."""
    got = settings.read()
    name = str((got.get("labels") or {}).get("filed") or FILED_LABEL)
    want = manifest.labels(got)[name]
    try:
        agent_github.gh("api", f"repos/{repo}/labels/{urllib.parse.quote(name, safe='')}")
    except subprocess.CalledProcessError:
        try:
            agent_github.gh("api", "-X", "POST", f"repos/{repo}/labels", "-f", f"name={name}",
                            "-f", f"color={want['color']}", "-f", f"description={want['description']}")
        except subprocess.CalledProcessError:
            pass
    return name


def file_issues(repo, number, rec, recs):
    """File every issue raise a passed review confirms as its own GitHub issue.

    It confirms its own, and each the planner or the worker raised that it answers done; `recs` are the records
    before it. Returns the record's lines naming each filed issue, or the finding and GitHub's reason when GitHub
    refuses it; a refusal never stops the run."""
    h = rec.get("handback") or {}
    if rec.get("role") != "reviewer" or not (rec.get("check") or {}).get("passed"):
        return []
    found = [(x, x) for x in card.raises_of(h) if x.get("kind") == "issue"]
    theirs = {x["id"]: x for x in open_raises(recs) if x.get("kind") == "issue" and raises.sent_to(x) == raises.CONFIRMS}
    found += [(theirs[a["raise"]], a) for a in card.answers_of(h)
              if a.get("answer") == "done" and isinstance(a["raise"], str) and a["raise"] in theirs]
    lines, label = [], None
    for x, decided in found:
        title = first_sentence(x.get("text") or x.get("label") or "An issue found")
        up = upstream.repo() if x.get(raises.FAULT) == "dokima" else ""
        if up:
            # Dokima's own problem goes to Dokima's repo, naming nothing of this one; this record links it (#745).
            try:
                n, again = upstream.file_problem(up, title, x.get("text") or title,
                                                 x["evidence"] if filled(x.get("evidence")) else None)
            except subprocess.CalledProcessError as e:
                lines.append(f"- Not filed in Dokima's repo: {card.escape(title)} GitHub refused it: "
                             f"{card.escape(gh_reason(e))}")
                continue
            said = "raised before, added as a comment" if again else "Dokima's own problem, filed in Dokima's repo"
            lines.append(f"- {card.ref(up, n)} · {said}")
            continue
        by = x.get("raised_by") or "reviewer"
        who = "The reviewer found it" if by == "reviewer" else f"The {by} raised it and the reviewer confirmed it"
        body = [x.get("text") or ""] + (["", f"**Evidence:** {x['evidence']}"] if filled(x.get("evidence")) else [])
        if x.get(raises.FAULT) == "unsure":
            body += ["", "**Whose fault:** Dokima cannot tell whether this is its own fault or the repo's, so it stays "
                         "here and nothing is filed in Dokima's repo."]
        run = os.environ.get("GITHUB_RUN_ID")
        where = f" ([run]({os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{run}))" if run else ""
        cause = decided.get(raises.CAUSE)
        if decided.get(raises.VERDICT) == "symptom" and raises.is_numbers([cause]):
            # A symptom joins its cause as a comment, and files no issue (#623).
            text = "\n".join(["**Symptom of this issue:**", ""] + body + ["", f"{who} on #{number}{where}."])
            try:
                agent_github.gh("issue", "comment", str(cause), "-R", repo, "--body", text)
            except subprocess.CalledProcessError as e:
                lines.append(f"- Not added to #{cause}: {card.escape(title)} GitHub refused it: {card.escape(gh_reason(e))}")
                continue
            lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), cause)} · a symptom, added as a comment")
            continue
        symptoms = decided.get(raises.SYMPTOMS)
        if decided.get(raises.VERDICT) == "root cause" and raises.is_numbers(symptoms) and symptoms:
            # A root cause files one issue marked as such, naming each symptom so GitHub links both ways (#623).
            title = f"Root cause found: {title}"
            body += ["", "**Symptoms:** " + ", ".join(f"#{n}" for n in symptoms)]
        if decided.get(raises.VERDICT) in raises.VERDICTS:
            body += ["", f"**Verdict:** {raises.VERDICTS[decided[raises.VERDICT]]}"]
        if raises.is_numbers(decided.get(raises.SEARCHED)) and decided[raises.SEARCHED]:
            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
        body += ["", f"{who} on #{number}{where}."]
        label = label or filed_label(repo)
        try:
            url = agent_github.gh("issue", "create", "-R", repo, "--title", title, "--body", "\n".join(body),
                     "--label", label).strip()
        except subprocess.CalledProcessError as e:
            lines.append(f"- Not filed: {card.escape(title)} GitHub refused it: {card.escape(gh_reason(e))}")
            continue
        n = url.rstrip("/").rsplit("/", 1)[-1]
        lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), n)} · the reviewer confirmed it")
    return ["", f"{field_icon(os.environ.get('GITHUB_REPOSITORY', ''), 'issue found')} **Filed as issues:**", ""] + lines \
        if lines else []


def record_links(repo, number, items):
    """Record the just approved plan's links on GitHub; card.yml redraws the cards they touch (#438).

    Code reads the plan from the issue's checked records only. Its blocked_by links become GitHub's own blocked-by
    links on this issue and its blocks links the other issue blocked by this one; a link GitHub already has is not
    added again, and a blocking link the previous approved plan had and this one dropped is removed first. A link
    no approved plan had, such as one a person made by hand, is left alone. Links that would make issues block each
    other record nothing. Returns why the river must stop for the owner, or None when all went through.
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
            agent_github.gh("api", "-X", "DELETE", f"repos/{repo}/issues/{a}/dependencies/blocked_by/{known[a][b]}")
        except subprocess.CalledProcessError as e:
            failed.append(f"GitHub failed to remove the link #{a} blocked by #{b}: {gh_reason(e)}.")
    if failed:
        # A link turned around is removed before it is added the other way, so nothing is added after a failure.
        return " ".join(failed) + " Code added none of the plan's new links." + after
    for a, b in add:
        try:
            node = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{b}"))["id"]
            agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{a}/dependencies/blocked_by", "-F", f"issue_id={node}")
        except subprocess.CalledProcessError as e:
            failed.append(f"GitHub refused to record the link #{a} blocked by #{b}: {gh_reason(e)}.")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            failed.append(f"GitHub's answer for #{b} could not be read, so #{a} blocked by #{b} was not recorded: {e}.")
    return " ".join(failed) + after if failed else None


def set_title(repo, number, items):
    """Set the issue's title to the approved plan's (#543); returns why it failed, or None.

    Code reads the title from the issue's checked records only; a plan with none, from before titles, renames nothing.
    The first rename keeps the owner's own title in the issue's Original issue fold, in the same write."""
    title = ((latest(records(items), "planner") or {}).get("handback") or {}).get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    title = " ".join(title.split())
    try:
        now = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{number}"))
        if now["title"] == title:
            return None
        kept = issue_body.keep_title(now.get("body") or "", now["title"])
        agent_github.gh("api", "-X", "PATCH", f"repos/{repo}/issues/{number}", "-f", f"title={title}",
           *(["-f", f"body={kept}"] if kept != (now.get("body") or "") else []))
    except subprocess.CalledProcessError as e:
        return f"GitHub refused to set the issue's title to the plan's: {gh_reason(e)}."
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return f"GitHub's answer for #{number} could not be read, so its title was not set: {e}."
    return None


PUSH_EVENTS = ("pull_request", "pull_request_target", "push")


def installations_link(repo):
    """Where the repo's owner accepts the app's new permissions: the organization's or the account's page."""
    owner = repo.split("/")[0]
    kind = agent_github.gh("api", f"users/{owner}", "-q", ".type").strip()
    if kind == "Organization":
        return f"https://github.com/organizations/{owner}/settings/installations"
    return "https://github.com/settings/installations"


def stop_run(repo, rid, polls=60, pause=5):
    """Stop a run still going and wait until it ends.

    Returns None, or why it did not end."""
    agent_github.gh("api", "-X", "POST", f"repos/{repo}/actions/runs/{rid}/cancel")
    for i in range(polls):
        if json.loads(agent_github.gh("api", f"repos/{repo}/actions/runs/{rid}")).get("status") == "completed":
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
    comment with GitHub's own words. After any refusal the pull request becomes a draft again, so its merge gate
    readies it and GitHub starts every check afresh (#620). Returns what happened, one line."""
    pr = agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
            "-q", ".[0].number").strip()
    if not pr.isdigit():
        return "No open pull request: no check to run again."
    sha = agent_github.gh("pr", "view", pr, "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip()
    found = json.loads(agent_github.gh("api", f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100"))
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
                agent_github.gh("api", "-X", "POST", f"repos/{repo}/actions/runs/{run['id']}/rerun")
                ran.append(name)
                continue
        except subprocess.CalledProcessError as e:
            why = gh_reason(e)
            if NO_PERMISSION in why:
                denied.append(name)
                continue
        refused.append(f"- {name} ({url}): {why}")
    drafted = ""
    if denied or refused:
        # A draft's checks start again when the merge gate readies it, so the gate never reads the ones from before.
        try:
            agent_github.gh("pr", "ready", pr, "-R", repo, "--undo")
            drafted = " It is a draft again, so its checks start afresh when its merge gate readies it."
        except subprocess.CalledProcessError as e:
            drafted = f" GitHub could not make it a draft again, so its old checks stay: {gh_reason(e)}"
    if denied:
        agent_github.gh("pr", "comment", pr, "-R", repo, "--body",
           f"The plan of #{number} is approved, but GitHub refused to run its checks on {sha[:7]} again: Dokima's GitHub "
           f"App may not re-run workflows. Set the app's Actions permission to Read and write, then accept the new "
           f"permission on its installation: {installations_link(repo)}" + (drafted if not refused else ""))
    if refused:
        agent_github.gh("pr", "comment", pr, "-R", repo, "--body",
           f"The plan of #{number} is approved, but these checks on {sha[:7]} could not run again, in GitHub's own "
           f"words:\n\n" + "\n".join(refused) + ("\n\n" + drafted.strip() if drafted else ""))
    did = f"Ran {len(ran)} check(s) on {sha[:7]} of PR #{pr} again"
    if denied or refused:
        did += f"; {len(denied) + len(refused)} could not run again, and PR #{pr} says why"
    return did + "."


def started_before(repo, number):
    """True when GitHub's records show something already started on the issue: a record, a live
    card or an Autopilot line the bot posted there. A planned, running or finished issue is never started again."""
    d = json.loads(agent_github.gh("issue", "view", str(number), "-R", repo, "--json", "comments"))
    for c in d.get("comments") or []:
        body = c.get("body") or ""
        if (c.get("author") or {}).get("login") in (BOT, f"{BOT}[bot]") and (
                MARK in body or LIVE in body or body.strip() in (AUTOPILOT_LINE, AUTOPILOT_START_LINE, *HOTFIX_LINES.values())):
            return True
    return False


def start_planner(repo, number, line=AUTOPILOT_LINE):
    """Start the issue's planner with the river's own signal, after one Autopilot line where the
    owner would have said /plan.

    The line goes first: it is the record that this issue was started, so no later close starts it again."""
    agent_github.gh("issue", "comment", str(number), "-R", repo, "--body", line)
    agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next", "-f", "client_payload[role]=planner",
       "-f", "client_payload[stage]=plan", "-f", f"client_payload[issue]={number}")


def start_worker(repo, number, line):
    """Start a hotfix's worker with the river's own signal, after one Autopilot line (#863).

    The line stands where the owner would have said /work. It goes first, so no later close starts it again."""
    agent_github.gh("issue", "comment", str(number), "-R", repo, "--body", line)
    agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next", "-f", "client_payload[role]=worker",
       "-f", "client_payload[stage]=plan", "-f", f"client_payload[issue]={number}")


def start_first(repo, number, line=AUTOPILOT_LINE):
    """Start an issue nothing started on yet: a hotfix's worker, else its planner (#863)."""
    if hotfix.labeled(repo, number):
        start_worker(repo, number, HOTFIX_LINES[line])
    else:
        start_planner(repo, number, line)


def start_waiting(repo, numbers, line=AUTOPILOT_LINE):
    """Start every open issue among `numbers` that waits on nothing and never started.

    Each has no sub-issues and nothing open blocking it; it starts its planner, or a hotfix its worker. Returns those
    started."""
    started = []
    for n in numbers:
        if json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}")).get("state") != "open" or sub_issues(repo, n):
            continue
        blockers = blocked_by(repo, n)
        if any(b.get("state") != "closed" for b in blockers):
            continue
        if started_before(repo, n):
            continue
        start_first(repo, n, line)
        started.append(n)
    return started


def open_on_autopilot(repo):
    """The numbers of every open issue on autopilot, oldest first."""
    found = json.loads(agent_github.gh(
        "api", f"repos/{repo}/issues?labels={urllib.parse.quote(autopilot_label(), safe='')}&state=open&per_page=100",
        "--paginate") or "[]")
    return sorted(i["number"] for i in found if "pull_request" not in i)


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
    lines = (AUTOPILOT_LINE, AUTOPILOT_START_LINE, *AUTOPILOT_LINES.values(), *HOTFIX_LINES.values())
    for c in items[at + 1:]:
        who, said = (c.get("author") or {}).get("login"), (c.get("body") or "").strip()
        if (who in owners and command_of(said)) or (who in (BOT, f"{BOT}[bot]") and (LIVE in said or said in lines)):
            return False
    step = next_step(items[:at], rec, owners, autopilot=lambda: True, body=body, number=number)
    return step[:2] == ("start", "worker") and step[3:] == ("autopilot",)


def start_unblocked(repo, numbers, owners):
    """Start a fresh planner on every issue among `numbers` whose blockers have all closed.

    A hotfix nothing started on yet starts its worker instead (#863).

    Each was blocked, and has nothing started on it yet or a plan approved while it was blocked; its old plan's worker
    never starts. Returns (the issues started, what was done as lines). When GitHub cannot list an issue's blockers nothing
    starts and the issue says why."""
    started, did = [], []
    for n in numbers:
        items = None
        if started_before(repo, n):
            d, items = conversation(repo, n)
            if not plans_again(items, owners, d.get("body") or "", n):
                continue
        try:
            blockers = blocked_by(repo, n)
        except subprocess.CalledProcessError as e:
            agent_github.gh("issue", "comment", str(n), "-R", repo, "--body",
               f"Autopilot did not start the planner: GitHub could not list the issues blocking #{n}: {gh_reason(e)}.")
            did.append(f"could not list the blockers of #{n}")
            continue
        if blockers and all(b.get("state") == "closed" for b in blockers):
            # Only an issue nothing started on yet can be a hotfix built from its text; one planned before plans again.
            hot = items is None and hotfix.labeled(repo, n)
            if hot:
                start_worker(repo, n, HOTFIX_LINES[AUTOPILOT_LINE])
            else:
                start_planner(repo, n)
            started.append(n)
            did.append(f"started the {'worker' if hot else 'planner'} for #{n}")
        elif not blockers and items is not None:
            # A story whose approved plan waited its turn to build plans again once the story it waited for merged (#668).
            from dokima import turns
            try:
                ended = turns.turn_ended(repo, n, records(items))
            except subprocess.CalledProcessError as e:
                agent_github.gh("issue", "comment", str(n), "-R", repo, "--body",
                   f"Autopilot did not start the planner: GitHub could not list the stories sharing files with #{n}: {gh_reason(e)}.")
                did.append(f"could not list the stories sharing files with #{n}")
                continue
            if ended:
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
    if json.loads(agent_github.gh("api", f"repos/{repo}/issues/{number}")).get("state") != "open":
        return False
    subs = sub_issues(repo, number)
    if not subs or any(c.get("state") != "closed" for c in subs):
        return False
    agent_github.gh("issue", "close", str(number), "-R", repo, "--reason", "completed", "--comment", tree_done_comment(number))
    return True


def close_done_parents(repo, number):
    """Close the closed issue's parent when that was its last open sub-issue, in turn.

    On autopilot or not. Returns what it did, as lines."""
    did, n = [], int(number)
    while True:
        up = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}")).get("parent_issue_url")
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
        items = [i for p in pages(agent_github.gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
        # GitHub counts each issue's sub-issues, open or closed, so only a parent is asked about them.
        parents = [i["number"] for i in items if "pull_request" not in i and (i.get("sub_issues_summary") or {}).get("total")]
        closed = [n for n in parents if close_if_done(repo, n)]
        did += [f"closed #{n}: its whole tree is done" for n in closed]
        if not closed:
            return did


def autopilot_closed(repo):
    """What autopilot does when an issue closes, worked out from GitHub's state of every issue
    on autopilot, so a close whose own run never went is still handled by the next one. Returns what it did, as lines.

    Every open parent on autopilot whose sub-issues are all closed closes as completed, saying its tree is done, and
    counts as a close one level up in turn. Every closed issue on autopilot with no parent on autopilot is the top of a
    done tree: the tree goes off autopilot. Then every open issue left on autopilot that was blocked and whose blockers
    have all closed starts a fresh planner, unless something already started on it since its plan, if any, was approved."""
    did = []
    while True:
        issues = {i["number"]: i for i in json.loads(agent_github.gh(
            "api", f"repos/{repo}/issues?labels={urllib.parse.quote(autopilot_label(), safe='')}&state=all&per_page=100", "--paginate") or "[]")
            if "pull_request" not in i}
        subs = {n: sub_issues(repo, n) for n in sorted(issues)}
        done = [p for p, cs in subs.items() if cs and issues[p]["state"] == "open" and all(c["state"] == "closed" for c in cs)]
        if not done:
            break
        for p in done:
            agent_github.gh("issue", "close", str(p), "-R", repo, "--reason", "completed", "--comment", tree_done_comment(p))
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


def on_autopilot(repo, number, strict=False):
    """True or False from the issue's own labels on GitHub; None when GitHub cannot say.

    With strict, a call GitHub refuses raises its error, so the caller can say GitHub's reason."""
    try:
        labels = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{number}")).get("labels")
    except subprocess.CalledProcessError:
        if strict:
            raise
        return None
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(labels, list):
        return None
    name = autopilot_label()
    return any((l.get("name") if isinstance(l, dict) else l) == name for l in labels)


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


# How long autopilot waits for checks still running on a head before it stops for the owner, and how often it looks;
# the gate's wait is the repo's in settings (#787).
CHECKS_WAIT, CHECKS_PAUSE = 45 * 60, 30


def checks_wait():
    """How many seconds the merge gate waits for checks still running, from the settings' minutes."""
    return int((settings.read().get("gate") or {}).get("checks_wait_min") or CHECKS_WAIT // 60) * 60


MERGE_METHODS = ("squash", "merge", "rebase")


def merge_method():
    """The merge method in settings: squash, merge or rebase; raises ValueError on any other."""
    method = str((settings.read().get("merge") or {}).get("method") or "squash")
    if method not in MERGE_METHODS:
        raise ValueError(f"merge.method in settings is {method!r}; it must be squash, merge or rebase")
    return method


def default_branch(repo):
    """The branch autopilot merges into: the settings' one, else GitHub's default branch (#787).

    Raises subprocess.CalledProcessError when GitHub refuses, and ValueError when it names none."""
    name = (settings.read().get("branch") or {}).get("default")
    if name:
        return str(name)
    name = json.loads(agent_github.gh("api", f"repos/{repo}")).get("default_branch")
    if not name:
        raise ValueError("the default branch is unknown: branch.default is empty and GitHub gave no default branch")
    return name


BOARD_WAIT = "board wait"  # board.yml's job that waits a minute, cancelled by a newer event about the issue (#533)


def superseded(run):
    """True for a card run or board wait cancelled by a newer one (#528, #533).

    It judges nothing."""
    return run.get("name") in ("card", BOARD_WAIT) and run.get("status") == "completed" and run.get("conclusion") == "cancelled"


def required_checks(repo, branch="main"):
    """The checks the branch's rule requires, by name, as GitHub gives them (#561).

    Read from the branch itself, which any token that reads the repo may see; the protection endpoint needs admin
    rights Dokima's app lacks. Only when the branch shows no rule is the protection endpoint asked."""
    rule = (json.loads(agent_github.gh("api", f"repos/{repo}/branches/{branch}")).get("protection") or {}).get("required_status_checks")
    if not rule:
        rule = json.loads(agent_github.gh("api", f"repos/{repo}/branches/{branch}/protection/required_status_checks"))
    return set(rule.get("contexts") or []) | {c.get("context") for c in rule.get("checks") or [] if c.get("context")}


def unproven(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
    """Why the commit is not proven by the checks the branch's rule requires, or None.

    Check runs and commit statuses count alike; a check the rule does not require judges nothing (#561). A
    required check still running or not yet on the commit is waited for, up to `wait` seconds, looking every `pause`
    seconds; a card run cancelled by a newer redraw, or a board wait cancelled by a newer event, is left out."""
    return proof(repo, sha, wait, pause, branch)[1]


def proof(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
    """What the checks the branch's rule requires say of the commit, as `unproven` reads them.

    ("passed", None), ("failed", why) when one of them failed, or ("stopped", why) when they never finished or GitHub
    could not say."""
    try:
        required = required_checks(repo, branch)
    except subprocess.CalledProcessError as e:
        return "stopped", f"GitHub did not give which checks {branch} requires: {gh_reason(e)}"
    if not required:
        return "stopped", f"{branch}'s branch rule requires no checks, so no check proves its head commit {sha[:7]}"
    deadline = time.monotonic() + wait
    while True:
        runs = [r for p in pages(agent_github.gh("api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100", "--paginate"))
                for r in p.get("check_runs", []) if not superseded(r) and r.get("name") in required]
        statuses = [s for p in pages(agent_github.gh("api", f"repos/{repo}/commits/{sha}/status?per_page=100", "--paginate"))
                    for s in p.get("statuses") or [] if s.get("context") in required]
        red = [f"{r['name']} ({r.get('conclusion')})" for r in runs if r.get("status") == "completed" and r.get("conclusion") not in PASSING]
        red += [f"{s.get('context')} ({s.get('state')})" for s in statuses if s.get("state") not in ("success", "pending")]
        running = [r["name"] for r in runs if r.get("status") != "completed"]
        running += [s.get("context") for s in statuses if s.get("state") == "pending"]
        # A check only skipped, as on a draft, has not run yet: it proves nothing (#597).
        ran = {r.get("name") for r in runs if r.get("conclusion") != "skipped"}
        missing = sorted(required - ran - {s.get("context") for s in statuses})
        if red:
            return "failed", f"not every check passed on its head commit {sha[:7]}: {', '.join(red)}"
        if not running and not missing:
            return "passed", None
        if time.monotonic() >= deadline:
            if running:
                return "stopped", (f"a check was still running on its head commit {sha[:7]} after {wait // 60} minutes: "
                                   f"{', '.join(running)}")
            return "stopped", (f"a check {branch} requires never ran on its head commit {sha[:7]} after {wait // 60} "
                               f"minutes: {', '.join(missing)}")
        time.sleep(pause)


UPDATE_WAIT, UPDATE_PAUSE = 5 * 60, 5


def merge_gate(repo, pr, branch=None):
    """The merge gate, run once the code review approved the pull request (#596).

    The branch is the default one, from settings or GitHub (#787); main below stands for it. A branch behind main is
    brought up to date with it first (GitHub's Update branch), so the checks main requires are read on the code as it
    would land; the checks get the settings' wait. A draft is then readied, which starts its tests: none ran during the code
    review (#597). Returns ("passed", head, None) once every one passed on that head,
    ("failed", head, why) when one failed there, or ("stopped", head, why) when GitHub would not update the branch, the
    checks never finished or GitHub could not say."""
    head = agent_github.gh("pr", "view", str(pr), "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip()
    draft = agent_github.gh("pr", "view", str(pr), "-R", repo, "--json", "isDraft", "-q", ".isDraft").strip() == "true"
    if not head:
        return "stopped", "", "GitHub did not say which commit is its head"
    try:
        branch = branch or default_branch(repo)
    except subprocess.CalledProcessError as e:
        return "stopped", head, f"GitHub did not give the repo's default branch: {gh_reason(e)}"
    except (ValueError, AttributeError) as e:
        return "stopped", head, str(e)
    try:
        behind = behind_main(repo, head, branch)
    except subprocess.CalledProcessError as e:
        return "stopped", head, f"GitHub could not compare it with {branch}, the default branch: {gh_reason(e)}"
    if behind:
        try:
            agent_github.gh("api", "-X", "PUT", f"repos/{repo}/pulls/{pr}/update-branch", "-f", f"expected_head_sha={head}")
        except subprocess.CalledProcessError as e:
            return "stopped", head, f"GitHub could not bring its branch up to date with {branch}: {gh_reason(e)}"
        # GitHub updates the branch after it answers: the new head is the commit that holds main's newest one.
        old, deadline = head, time.monotonic() + UPDATE_WAIT
        while head == old:
            if time.monotonic() >= deadline:
                return "stopped", old, (f"GitHub did not bring its branch up to date with {branch} within "
                                        f"{UPDATE_WAIT // 60} minutes")
            time.sleep(UPDATE_PAUSE)
            head = agent_github.gh("pr", "view", str(pr), "-R", repo, "--json", "headRefOid", "-q", ".headRefOid").strip() or old
    if draft:
        try:
            agent_github.gh("pr", "ready", str(pr), "-R", repo)
        except subprocess.CalledProcessError as e:
            return "stopped", head, f"GitHub could not mark it ready, so its tests never started: {gh_reason(e)}"
    state, why = proof(repo, head, wait=checks_wait(), branch=branch)
    return state, head, why


def behind_main(repo, head, branch="main"):
    """True when the commit misses the branch's newest commit, as GitHub's comparison with it says."""
    cmp = json.loads(agent_github.gh("api", f"repos/{repo}/compare/{branch}...{head}"))
    return cmp.get("status") in ("behind", "diverged") or (cmp.get("behind_by") or 0) > 0


def held_for_approval(e):
    """True when GitHub refused a merge for a missing approving review."""
    return "approving review" in f"{e.stderr} {e.stdout}"


def try_merge(repo, pr, tested=None):
    """Ask GitHub to merge the pull request at the head its merge gate tested.

    Only when it changes no workflow file and its merge gate passed: every check main requires passed on its head,
    brought up to date with main first. A head the gate already `tested` is merged without running it again. GitHub's own rules decide (#587):
    when it holds the merge for the owner's approval, Dokima's app asks it to merge directly, which GitHub allows only
    when the app may bypass that approval, and only when its branch holds main's newest commit; a direct merge GitHub refuses leaves it waiting for approval.
    Returns (True, the head) once GitHub took the merge, or (False, why not, in GitHub's words when GitHub refused)."""
    try:
        files = [f["filename"] for p in pages(agent_github.gh("api", f"repos/{repo}/pulls/{pr}/files?per_page=100", "--paginate")) for f in p]
        flows = [f for f in files if f.startswith(WORKFLOWS)]
        if flows:
            return False, f"it changes a workflow file ({', '.join(flows)}), and only the owner merges those"
        branch, method = default_branch(repo), merge_method()
        state, head, why = ("passed", tested, None) if tested else merge_gate(repo, pr, branch)
        if state != "passed":
            return False, why
        # Pinned to the head whose checks passed: a commit pushed since makes GitHub refuse.
        merge = ("pr", "merge", str(pr), "-R", repo, f"--{method}", "--match-head-commit", head)
        try:
            agent_github.gh(*merge)
            refused = False
        except subprocess.CalledProcessError as e:
            if not held_for_approval(e):
                raise
            refused = True
        if not refused and merge_outcome(repo, pr)[0] != "waits":
            return True, head
        if behind_main(repo, head, branch):
            return False, (f"its branch is behind {branch} and misses {branch}'s newest commit; "
                           f"bring it up to date with {branch}")
        try:
            agent_github.gh(*merge, "--admin")
        except subprocess.CalledProcessError as e:
            if not held_for_approval(e):
                raise
            if refused:
                agent_github.gh(*merge, "--auto")
        return True, head
    except subprocess.CalledProcessError as e:
        return False, " ".join((e.stderr or str(e)).split())
    except (json.JSONDecodeError, AttributeError, KeyError, TypeError) as e:
        return False, f"GitHub's answer could not be read: {e}"
    except ValueError as e:
        return False, str(e)


def open_pr(repo, number):
    """The number of the open pull request built for the issue, or ''."""
    return agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
              "-q", ".[0].number").strip()


AUTOPILOT_MERGE = {"merged": "Autopilot: merged PR #{pr}", "queued": "Autopilot: PR #{pr} joined the merge queue",
                   "waits": "Autopilot: PR #{pr} waits for your approval before it merges"}


MERGE_STATE = ("query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n)"
               "{state isInMergeQueue autoMergeRequest{mergeMethod} reviewDecision mergeStateStatus}}}")


def merge_outcome(repo, pr):
    """What GitHub reports after a merge it took, read from the pull request.

    ("merged" | "queued" | "waits", "") or ("unconfirmed", why, in GitHub's words when it gave any). `gh pr merge` exits 0 when it only queues the pull request or turns on
    auto-merge, so only GitHub's own state says whether it merged."""
    owner, name = repo.split("/", 1)
    try:
        # Asked through GitHub's API: the runners' `gh pr view --json` has no isInMergeQueue field (#467).
        st = json.loads(agent_github.gh("api", "graphql", "-f", f"query={MERGE_STATE}", "-f", f"o={owner}", "-f", f"r={name}",
                           "-F", f"n={pr}"))["data"]["repository"]["pullRequest"]
    except subprocess.CalledProcessError as e:
        return "unconfirmed", f"GitHub could not say whether it merged: {gh_reason(e)}"
    except (json.JSONDecodeError, TypeError, KeyError) as e:
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


def automerge(repo, number, tested=None):
    """On autopilot, merge the open pull request built for the issue.

    Once GitHub reports it merged, queued or waiting for the owner's approval, the issue gets that one Autopilot line. Returns (pull request or '', how, why): how is
    "merged", "queued" or "waits"; "unconfirmed" when GitHub took the merge but cannot confirm it, or '' when the
    merge was not made, each with why. A head its merge gate already `tested` merges without running the gate again."""
    try:
        pr = open_pr(repo, number)
    except subprocess.CalledProcessError as e:
        return "", "", " ".join((e.stderr or str(e)).split())
    if not pr:
        return "", "", "there is no open pull request built for it"
    asked, why = try_merge(repo, pr, tested)
    if not asked:
        return pr, "", why
    how, why = merge_outcome(repo, pr)
    if how in AUTOPILOT_MERGE:
        agent_github.gh("issue", "comment", str(number), "-R", repo, "--body", AUTOPILOT_MERGE[how].format(pr=pr))
    return pr, how, why


QUEUE_REF = re.compile(r"^(?:refs/heads/)?gh-readonly-queue/.+/pr-(\d+)-[0-9a-f]+$")


def failing_tests(repo, run_id):
    """The tests a finished run names as failed or errored, from its log; [] when GitHub cannot give the log yet."""
    try:
        log = agent_github.gh("run", "view", str(run_id), "-R", repo, "--log-failed")
    except subprocess.CalledProcessError:
        return []
    seen = []
    for m in re.finditer(r"(?m)(?:FAILED|ERROR) (\S+::\S+)", log):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen[:20]


def queue_failed(repo, head_ref, run_id, run_url, owners):
    """A merge queue run failed and GitHub took the pull request out of the queue (#830).

    The first failure on a pull request's head puts it back in the queue once, since a flaky test is the common cause.
    A second failure on the same head sends a Dokima pull request back to its worker with the failing tests named,
    counted as a block like a failed merge gate (#601); at three blocks, or for a pull request with no issue, or one
    that changes a workflow file (only the owner merges those), it stops and mentions the owner. Both required
    checks may fail on one queue run: the first to report acts, the other finds its mark and does nothing.
    Returns one line saying what it did."""
    m = QUEUE_REF.match(head_ref or "")
    if not m:
        return f"{head_ref!r} is not a merge queue branch: nothing to do."
    pr = m.group(1)
    p = json.loads(agent_github.gh("api", f"repos/{repo}/pulls/{pr}"))
    if p.get("state") != "open":
        return f"PR #{pr} is {p.get('state')}: nothing to do."
    head = (p.get("head") or {}).get("sha", "")
    marks = [c.get("body") or "" for page in pages(agent_github.gh("api", f"repos/{repo}/issues/{pr}/comments?per_page=100", "--paginate"))
             for c in page if QUEUE_FAILED in (c.get("body") or "")]
    if any(f"run={run_id}" in b for b in marks):
        return f"PR #{pr}: this queue run was handled already."
    tests = failing_tests(repo, run_id)
    named = ("Failing: " + ", ".join(f"`{t}`" for t in tests) + ".") if tests else "See the run for what failed."
    tag = f"{QUEUE_FAILED}<!-- head={head} run={run_id} -->"
    mention = " ".join(f"@{o}" for o in owners)
    issue = issue_of_branch(repo, p)
    if not any(f"head={head}" in b for b in marks):
        asked, why = requeue(repo, pr, head)
        said = (f"The merge queue's checks failed ([run]({run_url})), so GitHub took this pull request out of the queue. "
                f"{named} " + ("Code put it back in the queue once, in case a test is flaky." if asked else
                               f"Code could not put it back in the queue: {why}. {mention}"))
        agent_github.gh("pr", "comment", pr, "-R", repo, "--body", f"{tag}\n{said}")
        return f"PR #{pr}: " + ("re-queued once." if asked else f"not re-queued: {why}")
    # The same head failed in the queue again: not a flake.
    if issue is None:
        # A manual fix names the issue it fixes in its branch, fix/issue-N (#837); the failure is said there too, so it is traceable.
        fixes = manual_fix_issue((p.get("head") or {}).get("ref"))
        said = (f"{tag}\nThe merge queue's checks failed again on the same commit of PR #{pr} ([run]({run_url})). "
                f"{named} {mention} Dokima didn't build this pull request from a plan, so it starts nothing: fix its branch.")
        agent_github.gh("pr", "comment", pr, "-R", repo, "--body", said)
        if fixes:
            agent_github.gh("issue", "comment", str(fixes), "-R", repo, "--body", said)
        return f"PR #{pr}: failed twice; no plan, owner mentioned" + (f" on #{fixes}." if fixes else ".")
    on = on_autopilot(repo, issue, strict=True)
    owners_set = set(owners)
    d, items = conversation(repo, issue)
    blocks = blocks_since_owner(items, owners_set, "pr") + 1
    why = f"The merge queue's checks failed twice on PR #{pr}'s same commit ([run]({run_url})). {named}"
    if on and blocks < 3:
        agent_github.gh("issue", "comment", str(issue), "-R", repo, "--body",
                        f"{tag}\n{why}\n\n**Next:** {GATE_FAILED}: the worker fixes the failing tests.")
        agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next",
                        "-f", "client_payload[role]=worker", "-f", "client_payload[stage]=", "-f", f"client_payload[issue]={issue}")
        return f"PR #{pr}: failed twice; #{issue} back to the worker."
    stop = (f"{blocks} blocks in a row without agreement. Your call: `/plan`, `/work` or `/review` with your words."
            if on else "Say `/work` to send it back to the worker.")
    agent_github.gh("issue", "comment", str(issue), "-R", repo, "--body",
                    f"{tag}\n{why}\n\n**Next:** {GATE_FAILED}: {mention} {stop}")
    return f"PR #{pr}: failed twice; #{issue} stopped for the owner."


def issue_of_branch(repo, p):
    """Issue N for a pull request from this repo's try/issue-N branch, else None."""
    head = p.get("head") or {}
    m = re.fullmatch(r"try/issue-(\d+)", head.get("ref") or "")
    return int(m.group(1)) if m and ((head.get("repo") or {}).get("full_name") == repo) else None


def requeue(repo, pr, head):
    """Put the pull request back in the merge queue at the same head; (True, '') or (False, why)."""
    files = [f["filename"] for p in pages(agent_github.gh("api", f"repos/{repo}/pulls/{pr}/files?per_page=100", "--paginate")) for f in p]
    flows = [f for f in files if f.startswith(WORKFLOWS)]
    if flows:
        return False, f"it changes a workflow file ({', '.join(flows)}), and only the owner merges those"
    try:
        agent_github.gh("pr", "merge", str(pr), "-R", repo, f"--{merge_method()}", "--match-head-commit", head)
    except subprocess.CalledProcessError as e:
        return False, gh_reason(e)
    return True, ""


def unconfirmed_comment(repo, pr, why, mention):
    """Says on the pull request that autopilot cannot confirm its merge, mentioning the owner."""
    agent_github.gh("pr", "comment", str(pr), "-R", repo, "--body",
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
            agent_github.gh("pr", "comment", pr, "-R", repo, "--body",
               f"Autopilot did not merge this pull request: {why}. {mention} It waits for you to merge it.".replace("  ", " "))
    return done


# The other agent job files, imported last so the job files can use each other (#636).
from dokima import agent_github
from dokima.agent_github import BOT, conversation, sub_issues, blocked_by, gh_reason, NO_PERMISSION, pages, issue_of_pr, manual_fix_issue
from dokima.agent_records import (
    MARK, LIVE, HANDBACK, records, latest, approved_plan, is_record, open_raises, settled, owner_raises, plan_links,
    filled, first_sentence, GATE_FAILED, QUEUE_FAILED)
from dokima.agent_roles import command_of
from dokima.agent_next import next_step, blocks_since_owner

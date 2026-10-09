#!/usr/bin/env python3
"""Build the Dokima card and write it at the top of both the issue and its PR.

The card shows the plan's user story and criteria, each with GitHub's own verdict
from that criterion's check. It computes no verdicts itself: a pass appears only
when GitHub recorded the criterion's check as passed on the PR's latest commit.

It runs from the default branch, never from a PR's own code, so the work being
judged cannot change how it is reported. No AI writes the card. It is drawn only
from the agents' records and GitHub's checks and reviews, never from the issue's
text, so the issue and its PR show the same card.
"""
import ast
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import body, plan  # noqa: E402

ALL_TESTS = "All tests"
TODO = {"questions": "Answer the questions with /plan, or say /review",
        "plan approved": "Say /work to build the plan",
        "three blocks": "Three blocks in a row: your call",
        "rejected": "Fix the rejected hand-back",
        "not started": "Fix why nothing ran",
        "escalated": "Settle the escalation",
        "ready": "Ready for approval",
        "not every check passed": "See why not every check passed"}
STAGES = {"Backlog", "Plan", "Work", "Review", "Merged"}
ICON_FILE = {"passed": "passed", "failed": "failed", "running": "running", "not started": "none"}
# Every field a card or run comment shows, and its own Octicon in dokima/icons/. Fixed here, never chosen by an agent.
FIELD_ICONS = {"planner": "planner", "worker": "worker", "plan review": "plan-review", "code review": "code-review",
               "autopilot": "autopilot", "passed": "passed", "failed": "failed", "needs you": "needs-you",
               "owner approval": "owner-approval", "merged": "merged", "still open": "still-open",
               "acceptance criterion": "acceptance-criterion", "verified by": "verified-by",
               "files changed": "files-changed", "question": "question", "blocker": "blocker", "note": "note",
               "outside the plan": "outside-the-plan", "issue found": "issue-found", "related": "related",
               "blocked by": "blocked-by", "blocks": "blocks", "stats": "stats"}
CLOSES = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?) #\d+", re.I)


def icon(repo, name, alt=None):
    """One of GitHub's own circle icons (Octicons, MIT), served from this repo, centered on its line."""
    url = f"https://raw.githubusercontent.com/{repo}/main/dokima/icons/{name}.svg"
    return f'<img src="{url}" width="16" height="16" align="absmiddle" alt="{alt or name}">'


def field_icon(repo, field):
    """The fixed icon of a field, drawn in front of it, with the field's name as its alt text."""
    return icon(repo, FIELD_ICONS[field], alt=field)


def link_lines(repo, links):
    """One line per kind of link a plan has (Blocked by, Blocks, Relates to), each with its own icon; none for a kind
    with no links or a plan with no links field."""
    links = links if isinstance(links, dict) else {}
    out = []
    for kind, field, label in (("blocked_by", "blocked by", "Blocked by"), ("blocks", "blocks", "Blocks"),
                               ("relates_to", "related", "Relates to")):
        numbers = links.get(kind) if isinstance(links.get(kind), list) else []
        if numbers:
            out.append(f"{field_icon(repo, field)} **{label}:** " + ", ".join(f"#{n}" for n in numbers))
    return out


LINKED = re.compile(r"<!-- dokima-linked-from:([\d ,]*)-->")
SIDE = {"blocked_by": "blocks", "blocks": "blocked_by", "relates_to": "relates_to"}


def merged(*many):
    """Several links fields as one, each kind's numbers in order and once."""
    out = {}
    for links in many:
        for kind in SIDE:
            v = links.get(kind) if isinstance(links, dict) else None
            for n in v if isinstance(v, list) else []:
                if n not in out.setdefault(kind, []):
                    out[kind].append(n)
    return out


def linked_from(text):
    """The issues whose approved plans link here, as code noted them in the card part.

    Only an index of where to look: what each one links is read from its own records, never from this text. A body
    with no card part yet has none.
    """
    if body.MARKER not in (text or ""):
        return []
    m = LINKED.search(text.split(body.MARKER, 1)[0])
    return sorted({int(x) for x in re.findall(r"\d+", m.group(1))}) if m else []


def their_links(repo, number, sources, plans=None):
    """The links the approved plans of `sources` make here, seen from this side.

    `plans` gives, by issue, the links of a plan approved just now, before its review is on record. An issue that
    cannot be read is skipped with a warning in the run.
    """
    from dokima import agent
    mine = {k: [] for k in SIDE}
    for s in sources:
        if s in (plans or {}):
            links = plans[s]
        else:
            try:
                links = agent.plan_links(agent.approved_plan(agent.records(agent.conversation(repo, s)[1])))
            except (subprocess.CalledProcessError, ValueError, KeyError, TypeError) as e:
                print(f"::warning title=Links not read::the links of #{s} could not be read: {e}")
                continue
        for kind, other in SIDE.items():
            if int(number) in links.get(kind, []) and s not in mine[other]:
                mine[other].append(s)
    return mine


def state(check):
    """GitHub's verdict for one check run (already filtered to the PR's latest commit): passed, failed, running or not started."""
    if check is None:
        return "not started"
    if check["status"] == "completed":
        return "passed" if check["conclusion"] == "success" else "failed"
    return "running" if check["status"] == "in_progress" else "not started"


def circle(repo, st, url=None):
    """The verdict circle for state `st`, linked to its proof when there is one."""
    img = icon(repo, ICON_FILE[st], alt=st)
    return f'<a href="{url}">{img}</a>' if url else img


def fold(title, lines):
    """A long part folded under its title, so the card on top stays short: the issue card and every run comment use it."""
    return [f"<details><summary><b>{title}</b></summary>", "", *lines, "", "</details>"]


def escape(text):
    return html.escape(text or "", quote=False)


def checks_by_key(check_runs):
    """Index criterion checks by their key ('67.1') from names like '67.1 · ...'."""
    found = {}
    for run in check_runs:
        key = run["name"].split(" · ")[0]
        if re.fullmatch(r"\d+\.\d+", key):
            found[key] = run
    return found


def as_items(steps, owner=None):
    """Records (and an owner's words, as text) as the conversation the river reads, for a card drawn from records alone."""
    from dokima import agent
    return [{"author": {"login": owner}, "body": st} if isinstance(st, str) else
            {"author": {"login": agent.BOT}, "body": f"{agent.MARK}\n```json\n{json.dumps(st)}\n```"} for st in steps]


def checks_passed(number, h, check_runs):
    """True when every criterion's check of plan `h`, and All tests, passed on the PR's latest commit."""
    count = len(h.get("acceptance_criteria") or []) + len(h.get("non_functional") or []) if h else 0
    by_key = checks_by_key(check_runs)
    runs = [by_key.get(f"{number}.{k}") for k in range(1, count + 1)]
    runs.append(next((r for r in check_runs if r["name"] == ALL_TESTS), None))
    return count > 0 and all(state(r) == "passed" for r in runs)


def todo(issue, found, rec):
    """What the owner must do now that the river stopped for them on the record `rec`."""
    from dokima import agent
    role, h = rec.get("role"), rec.get("handback") or {}
    if role == "not-started":
        return TODO["not started"]
    if not rec.get("check", {}).get("passed"):
        return TODO["rejected"]
    if role == "planner" and h.get("questions"):
        return TODO["questions"]
    verdict = h.get("verdict") if role == "reviewer" else None
    if verdict == "escalate":
        return TODO["escalated"]
    if verdict == "block":
        return TODO["three blocks"]
    if verdict == "approve" and rec.get("stage") == "plan":
        return TODO["plan approved"]
    if verdict == "approve":
        planned = agent.latest(found["recs"], "planner")
        h = planned["handback"] if planned else None
        return TODO["ready"] if checks_passed(issue["number"], h, found["check_runs"]) else TODO["not every check passed"]
    return "See the newest record below"


def status(issue, found):
    """(stage, to-do): the board's column and, exactly when the board shows Needs you, what the owner must do; None
    when nothing is theirs. It follows the board's own rule on the newest record, as the river decided it."""
    from dokima import agent
    pr = found.get("pr")
    if pr and pr.get("merged"):
        return "Merged", None
    items = found.get("items")
    if items is None:
        items = as_items(found["recs"])
    at = [i for i, c in enumerate(items) if agent.is_record(c)]
    if not at:
        return "Backlog", None
    rec = agent.records([items[at[-1]]])[0]
    if rec.get("role") == "split":
        return "Work", None
    column, needs = agent.board_place(rec, agent.next_step(items[:at[-1]], rec, found.get("owners") or set()))
    return column, todo(issue, found, rec) if needs else None


def status_line(repo, stage, todo):
    """The small status line under the summary: the stage, then Needs you and the owner's to-do when there is one."""
    head = f"{field_icon(repo, 'merged')} **{stage}**" if stage == "Merged" else f"**{stage}**"
    return head + (f" · {field_icon(repo, 'needs you')} Needs you: {todo}" if todo else "")


def child_row(repo, child):
    """One child of a split: its link, its title and its stage, or unknown when its stage could not be read."""
    st = child.get("stage") if child.get("stage") in STAGES else "unknown"
    if st == "Merged":
        st = f"{field_icon(repo, 'merged')} {st}"
    n = child["number"]
    return f"- [#{n}](https://github.com/{repo}/issues/{n}) {escape(child.get('title'))} · {st}"


def links_row(repo, issue, pr, worker, check_runs):
    """The links that matter, the issue and its PR both included, so the card reads the same on either page."""
    links = []
    if worker:
        links.append(f"[latest run]({worker['html_url']})")
    links.append(f"[issue #{issue['number']}]({issue['url']})")
    if pr:
        links.append(f"[PR #{pr['number']}](https://github.com/{repo}/pull/{pr['number']})")
    if pr:
        links.append(f"{field_icon(repo, 'files changed')} [files changed](https://github.com/{repo}/pull/{pr['number']}/files)")
    return " · ".join(links)


def criterion_item(repo, label, c, check, tests):
    """One criterion as a bullet: its status circle, its label and its words, linked to its check when there is one;
    under it one italic Verified by line per test with a docstring, only the words Verified by linking to the test,
    then Source linking to where the owner asked for it, when it has one."""
    words = escape(c.get("text"))
    if check:
        words = f'<a href="{check["html_url"]}">{words}</a>'
    out = [f"- {circle(repo, state(check))} **{label}:** {words}"]
    for t in tests:
        if t and t.get("verified_by"):
            out.append(f'  - *<a href="{t["url"]}">{field_icon(repo, "verified by")} Verified by</a>: '
                       f'{escape(t["verified_by"])}*')
    if c.get("source"):
        out.append(f'  - <a href="{c["source"]}">Source</a>')
    return out


def criteria_list(repo, number, start, label, criteria, plan_tests, by_key, tests):
    """The bullet list of criteria numbered from `start`, each with its own check and tests."""
    out = []
    for k, c in enumerate(criteria, start):
        key = f"{number}.{k}"
        out += criterion_item(repo, label, c, by_key.get(key), [tests.get(t) for t in plan_tests.get(key, [])])
    return out


def code_review(recs):
    """The newest code review whose record passed its check, since the worker last built; None when there is none."""
    builds = [i for i, r in enumerate(recs) if r.get("role") == "worker"]
    after = recs[builds[-1] + 1:] if builds else recs
    reviews = [r for r in after if r.get("role") == "reviewer" and r.get("stage") == "pr" and r.get("check", {}).get("passed")]
    return reviews[-1] if reviews else None


def owner_review(reviews, owners):
    """The newest Approve or Request changes on the PR by a code owner; None when there is none."""
    found = [r for r in reviews if r.get("state") in ("APPROVED", "CHANGES_REQUESTED")
             and (r.get("user") or {}).get("login") in owners]
    return found[-1] if found else None


def owner_merge(pr, owners):
    """The PR when a code owner merged it, which counts as their approval; None otherwise."""
    merger = ((pr or {}).get("merged_by") or {}).get("login")
    return pr if pr and pr.get("merged") and merger in owners else None


def done_row(repo, found, all_tests):
    """The Definition of Done: All tests, the code review and the owner's approval, each with its verdict and proof.
    A code owner's merge is their approval, with or without an Approve review."""
    review = code_review(found["recs"])
    review_st = "not started" if not review else "passed" if review["handback"].get("verdict") == "approve" else "failed"
    merge = owner_merge(found["pr"], found["owners"])
    approval = {"state": "APPROVED", "html_url": merge.get("html_url")} if merge else owner_review(found["reviews"], found["owners"])
    approval_st = "not started" if not approval else "passed" if approval["state"] == "APPROVED" else "failed"
    return ("**Definition of Done:** "
            f"{circle(repo, state(all_tests), all_tests and all_tests['html_url'])} All tests · "
            f"{circle(repo, review_st, review and review.get('run'))} {field_icon(repo, 'code review')} Code review · "
            f"{circle(repo, approval_st, approval and approval.get('html_url'))} {field_icon(repo, 'owner approval')} "
            "Owner approval")


def render(repo, issue, found, page="issue"):
    """The card for `issue`, drawn only from `found`: the agents' records, the PR, its latest commit's checks, its
    reviews, the code owners, the plan's tests and the latest worker run. It is the same on either `page`."""
    from dokima import agent
    recs, pr, check_runs, worker = found["recs"], found["pr"], found["check_runs"], found["worker"]
    by_key = checks_by_key(check_runs)
    all_tests = next((r for r in check_runs if r["name"] == ALL_TESTS), None)
    planned = agent.latest(recs, "planner")
    h = planned["handback"] if planned else None
    lines = [plan.CARD_START]
    if found.get("sources"):
        lines += [f"<!-- dokima-linked-from: {', '.join(str(n) for n in found['sources'])} -->"]
    if h and isinstance(h.get("summary"), str) and h["summary"].strip():
        lines += [escape(h["summary"].strip()), ""]
    lines += [status_line(repo, *status(issue, found)), ""]
    links = links_row(repo, issue, pr, worker, check_runs)
    if links:
        lines += [links, ""]
    children = found.get("children") or []
    if children:
        lines += ["**Stories:**", ""] + [child_row(repo, c) for c in children] + [""]
    related = link_lines(repo, merged(h.get("links") if h else None, found.get("linked")))
    if related:
        lines += related + [""]
    if not h:
        lines += ["This issue has no plan yet.", ""]
    else:
        criteria, nfr = h.get("acceptance_criteria") or [], h.get("non_functional") or []
        tests, plan_tests = found["tests"], h.get("tests") or {}
        if h.get("user_story"):
            lines += [f"**User story:** {escape(h['user_story'])}", ""]
        lines += [f"{field_icon(repo, 'acceptance criterion')} **Acceptance criteria**", ""]
        lines += criteria_list(repo, issue["number"], 1, "Acceptance criterion", criteria, plan_tests, by_key, tests) + [""]
        if nfr:
            lines += fold("Non-functional requirements",
                          criteria_list(repo, issue["number"], len(criteria) + 1, "Non-functional requirement", nfr,
                                        plan_tests, by_key, tests)) + [""]
        lines += ["**Scope:**", ""] + [f"- {escape(s)}" for s in h.get("scope") or []] + [""]
        lines += ["**Out of scope:**", ""] + [f"- {escape(s)}" for s in h.get("out_of_scope") or []] + [""]
    lines += [done_row(repo, found, all_tests), "", plan.CARD_END]
    return "\n".join(lines)


def issue_body(card, notes):
    """The issue's text: the card, then any notes, kept as written."""
    return card + ("\n\n" + notes if notes else "")


def pr_body(card, body):
    """The PR's description: the card, then the line linking the issue, and nothing else."""
    found = CLOSES.search(body or "")
    return card + ("\n\n" + found.group(0) if found else "")


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def issue_pr(repo, n):
    """The PR built for issue n from its try or work branch, or None."""
    owner = repo.split("/")[0]
    for branch in (f"try/issue-{n}", f"work/issue-{n}"):
        prs = json.loads(gh("api", f"repos/{repo}/pulls?head={owner}:{branch}&state=all"))
        if prs:
            return prs[0]["number"]
    return None


def find_work(repo):
    """The issue and open PR this event is about, as (issue number, PR number or None)."""
    if os.environ.get("ISSUE_NUMBER"):
        n = int(os.environ["ISSUE_NUMBER"])
        return n, issue_pr(repo, n)
    title = re.match(r"worker for #(\d+)$", os.environ.get("RUN_TITLE", ""))
    if title:
        n = int(title.group(1))
        return n, issue_pr(repo, n)
    pr = os.environ.get("PR_NUMBER")
    if not pr:
        prs = json.loads(gh("api", f"repos/{repo}/commits/{os.environ['HEAD_SHA']}/pulls"))
        pr = prs[0]["number"] if prs else None
    if not pr:
        return None, None
    return plan.pr_issue_number(repo, pr), int(pr)


def latest_worker_run(repo, number):
    runs = json.loads(gh("api", f"repos/{repo}/actions/workflows/worker.yml/runs?per_page=50"))["workflow_runs"]
    run = next((r for r in runs if r["display_title"] == f"worker for #{number}"), None)
    return {"status": run["status"], "conclusion": run["conclusion"], "html_url": run["html_url"]} if run else None


def test_entry(repo, ref, path, source, name):
    """One test's Verified by (its docstring's first line, or None) and the link to the line it starts on at `ref`."""
    url = f"https://github.com/{repo}/blob/{ref}/{path}"
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"verified_by": None, "url": url}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            doc = (ast.get_docstring(node) or "").strip()
            return {"verified_by": doc.splitlines()[0] if doc else None, "url": f"{url}#L{node.lineno}"}
    return {"verified_by": None, "url": url}


def file_at(repo, path, ref=None):
    """A file's text at `ref` (the default branch when None), or None when GitHub has no such file."""
    target = f"repos/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    try:
        return gh("api", target, "-H", "Accept: application/vnd.github.raw")
    except subprocess.CalledProcessError:
        return None


def child_stage(repo, number, owners):
    """A child issue's stage, read from its own records and PR; unknown when GitHub cannot be read."""
    from dokima import agent
    try:
        _, items = agent.conversation(repo, number)
        pr = None
        for p in agent.linked_prs(repo, number):
            pr = json.loads(gh("api", f"repos/{repo}/pulls/{p}"))
            if pr.get("merged"):
                break
        found = {"recs": agent.records(items), "items": items, "pr": pr, "check_runs": [], "owners": owners}
        return status({"number": number}, found)[0]
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError):
        return "unknown"


def gather(repo, number, pr_number):
    """Everything the card is drawn from, fetched from GitHub: never the issue's text."""
    from dokima import agent
    _, items = agent.conversation(repo, number)
    recs = agent.records(items)
    pr, check_runs, reviews = None, [], []
    if pr_number:
        pr = json.loads(gh("api", f"repos/{repo}/pulls/{pr_number}"))
        check_runs = json.loads(gh("api", f"repos/{repo}/commits/{pr['head']['sha']}/check-runs?per_page=100"))["check_runs"]
        reviews = json.loads(gh("api", f"repos/{repo}/pulls/{pr_number}/reviews?per_page=100"))
    # Code owners are read from the default branch, never from the PR's own commit.
    owners = plan.approvers(file_at(repo, ".github/CODEOWNERS") or "", repo.split("/")[0])
    ref = pr["head"]["sha"] if pr else f"try/issue-{number}"
    planned = agent.latest(recs, "planner")
    tests, sources = {}, {}
    for t in sorted({t for ts in ((planned or {}).get("handback", {}).get("tests") or {}).values() for t in ts}):
        path, _, name = t.partition("::")
        if path not in sources:
            sources[path] = file_at(repo, path, ref)
        if sources[path] is not None:
            tests[t] = test_entry(repo, ref, path, sources[path], name)
    split = agent.latest(recs, "split")
    children = [{"number": st["issue"], "title": st.get("title"), "stage": child_stage(repo, st["issue"], owners)}
                for st in (split["handback"].get("stories") or [] if split else [])]
    return {"recs": recs, "items": items, "pr": pr, "check_runs": check_runs, "reviews": reviews, "owners": owners,
            "tests": tests, "worker": latest_worker_run(repo, number), "children": children}


def gallery(repo, out):
    """Draw the card of every situation the owner looks at on a throwaway issue and PR, one file each, into `out`."""
    from dokima import agent
    number, owner = 1, "owner"
    issue = {"number": number, "url": f"https://github.com/{repo}/issues/{number}"}

    def rec(role, stage=None, **handback):
        return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
                "run": f"https://github.com/{repo}/actions/runs/1"}

    def run(name, status="completed", conclusion="success"):
        return {"name": name, "status": status, "conclusion": conclusion, "html_url": f"https://github.com/{repo}/actions/runs/2"}

    src = issue["url"]
    story = {"kind": "user_story", "summary": "Slow calls hand back a job id instead of timing out.",
             "user_story": "Callers get a job id for a slow call and fetch its result later.",
             "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": src},
                                     {"text": "The job id fetches the result once it is ready.", "source": src}],
             "non_functional": [{"text": "A failed job says why.", "why": "nothing fails silently", "principle": "Fail closed"}],
             "scope": ["app/jobs.py"], "out_of_scope": ["Retrying failed jobs."], "tests": {}}
    feature = {"kind": "feature", "summary": "Slow calls run as jobs, in three stories.", "feature": "Slow calls run as jobs.",
               "stories": [{"title": t} for t in ("Jobs", "Results", "Failures")]}
    split = rec("split", stories=[{"story": i, "issue": n, "title": t, "blocked_by": []}
                                  for i, (n, t) in enumerate(((2, "Jobs"), (3, "Results"), (4, "Failures")), 1)])
    built = [rec("planner", **story), rec("reviewer", "plan", verdict="approve", blockers=[]), "/work", rec("worker")]
    approved = built + [rec("reviewer", "pr", verdict="approve", blockers=[])]
    names = [f"{number}.1 · A slow call returns a job id", f"{number}.2 · The job id fetches the result",
             f"{number}.3 · A failed job says why", ALL_TESTS]
    green = [run(n) for n in names]
    pr = {"number": 5, "merged": False, "state": "open"}
    done = {"status": "completed", "conclusion": "success", "html_url": f"https://github.com/{repo}/actions/runs/1"}
    situations = {
        "planned": (built[:2], None, [], done, []),
        "building": (built + [rec("reviewer", "pr", verdict="block", blockers=[{"id": "B1", "fixer": "worker"}])], pr,
                     [run(n, "in_progress", None) for n in names],
                     dict(done, status="in_progress", conclusion=None), []),
        "checks-failing": (approved, pr, green[:1] + [run(names[1], conclusion="failure")] + green[2:], done, []),
        "ready": (approved, pr, green, done, []),
        "merged": (approved, dict(pr, merged=True, state="closed"), green, done, []),
        "split": ([rec("planner", **feature), rec("reviewer", "plan", verdict="approve", blockers=[]), "/work", split],
                  None, [], None, [{"number": 2, "title": "Jobs", "stage": "Merged"},
                                   {"number": 3, "title": "Results", "stage": "Review"},
                                   {"number": 4, "title": "Failures", "stage": "Plan"}]),
        "no-plan": ([], None, [], None, []),
    }
    os.makedirs(out, exist_ok=True)
    for name, (steps, pr_, check_runs, worker, children) in situations.items():
        items = as_items(steps, owner)
        found = {"recs": agent.records(items), "items": items, "pr": pr_, "check_runs": check_runs, "reviews": [],
                 "owners": {owner}, "tests": {}, "worker": worker, "children": children}
        with open(os.path.join(out, f"{name}.md"), "w") as f:
            f.write(render(repo, issue, found) + "\n")
        print(f"Drew {name}.md")


def main():
    if sys.argv[1:2] == ["gallery"] and len(sys.argv) == 3:
        gallery(os.environ.get("REPO") or "dokima-dev/dokima", sys.argv[2])
        return
    repo = os.environ["REPO"]
    number, pr_number = find_work(repo)
    if not number:
        print("No issue for this event; nothing to write.")
        return
    draw(repo, number, pr_number)


def draw(repo, number, pr_number, plans=None, noted=None):
    """Write the card at the top of the issue and its PR.

    `plans` gives the links of a plan approved just now, by issue (see their_links). `noted` adds (True) or removes
    (False) issues from the index of those whose approved plans link here.
    """
    issue = plan.fetch_issue(repo, number)
    found = gather(repo, number, pr_number)
    sources = set(linked_from(issue["current_body"]))
    for s, on in (noted or {}).items():
        (sources.add if on else sources.discard)(s)
    found["sources"] = sorted(sources)
    found["linked"] = their_links(repo, number, found["sources"], plans)
    pr = found["pr"]
    # Only the part above the marker is code's; the owner's ask below it is saved as it is, or the save is refused.
    if body.save(repo, number, issue["current_body"] or "", render(repo, issue, found)):
        print(f"Card written into issue #{number}")
    # The PR gets the same card, open, merged or closed, so it never keeps an older card than the issue (#224).
    if pr:
        with open("pr.md", "w") as f:
            f.write(pr_body(render(repo, issue, found), pr.get("body")))
        gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{pr_number}", "-F", "body=@pr.md")
        print(f"Card written into PR #{pr_number}")


if __name__ == "__main__":
    main()

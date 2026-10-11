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
from dokima import body, plan, retry  # noqa: E402

ALL_TESTS = "all tests"
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
# A `#` right after a closing keyword, as GitHub reads one (fixes #99, Closes: #12, resolved o/r#7).
KEYWORD_HASH = re.compile(r"(\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+(?:[\w.-]+/[\w.-]+)?)#(?=\d)", re.I)
# An issue's full address right after a closing keyword (Fixes https://github.com/o/r/issues/98).
KEYWORD_URL = re.compile(r"(\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+)h(?=ttps://github\.com/[\w.-]+/[\w.-]+/issues/\d)", re.I)


def icon(repo, name, alt=None):
    """One of GitHub's own circle icons (Octicons, MIT), served from this repo, centered on its line."""
    url = f"https://raw.githubusercontent.com/{repo}/main/dokima/icons/{name}.svg"
    return f'<img src="{url}" width="16" height="16" align="absmiddle" alt="{alt or name}">'


def field_icon(repo, field):
    """The fixed icon of a field, drawn in front of it, with the field's name as its alt text."""
    return icon(repo, FIELD_ICONS[field], alt=field)


def ref(repo, n):
    """Issue or PR `n` by its full address, so GitHub shows its icon, title and number."""
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/issues/{n}"


SHORT_REF = re.compile(r"(?<![\w&/])#(\d+)\b")


def full_refs(repo, text):
    """`text` with every short #N written out as its full address."""
    return SHORT_REF.sub(lambda m: ref(repo, m.group(1)), text or "")


def link_lines(repo, links):
    """One block per kind of link a plan has (Blocked by, Blocks, Relates to): its icon and label, then one bullet per
    issue, since GitHub shows an issue's title and state only for a link that is a bullet of its own; none for a kind
    with no links or a plan with no links field."""
    links = links if isinstance(links, dict) else {}
    out = []
    for kind, field, label in (("blocked_by", "blocked by", "Blocked by"), ("blocks", "blocks", "Blocks"),
                               ("relates_to", "related", "Relates to")):
        numbers = links.get(kind) if isinstance(links.get(kind), list) else []
        if numbers:
            out.append(f"{field_icon(repo, field)} **{label}:**\n\n" + "\n".join(f"- {ref(repo, n)}" for n in numbers) + "\n")
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


BLOCKING = re.compile(r"<!-- dokima-blocking: (\{.*?\}) -->")
NO_LINKS = {"blocked_by": [], "blocks": [], "loop": []}


def reason(e):
    """GitHub's own words for a call that failed, on one line."""
    return " ".join((getattr(e, "stderr", None) or str(e)).split())


def blocking(repo, number, cache):
    """GitHub's own blocked-by links of the issue, read now.

    {"blocked_by": [...], "blocks": [...]}, kept in `cache` for this run, or the error GitHub answered with when it
    cannot list them."""
    from dokima import agent
    if number not in cache:
        try:
            cache[number] = {kind: sorted({i["number"] for p in agent.pages(gh(
                "api", f"repos/{repo}/issues/{number}/dependencies/{path}", "--paginate")) for i in p})
                for kind, path in (("blocked_by", "blocked_by"), ("blocks", "blocking"))}
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError) as e:
            cache[number] = e
    return cache[number]


def loop_of(repo, number, cache):
    """The issues blocking each other with this one on GitHub, this one among them.

    Directly or through others, sorted; [] when none. An issue whose links GitHub cannot list counts as blocked by
    nothing."""
    def by(i):
        got = blocking(repo, i, cache)
        return got["blocked_by"] if isinstance(got, dict) else []
    reach, todo = set(), list(by(number))
    while todo:
        i = todo.pop()
        if i not in reach:
            reach.add(i)
            todo += by(i)
    if number not in reach:
        return []
    back, todo = {number}, [number]
    while todo:
        j = todo.pop()
        for i in sorted(reach - back):
            if j in by(i):
                back.add(i)
                todo.append(i)
    return sorted(back)


def github_links(repo, number, cache):
    """What the card's Blocked by, Blocks and loop lines show, from GitHub now.

    {"unread": True} when GitHub cannot list the issue's links."""
    got = blocking(repo, number, cache)
    if not isinstance(got, dict):
        return {"unread": True}
    return {**got, "loop": loop_of(repo, number, cache)}


def shown_links(text):
    """The blocking links and loop the card was last drawn from.

    As code noted them in its card part; none when the issue has no such note yet."""
    if body.MARKER not in (text or ""):
        return dict(NO_LINKS)
    m = BLOCKING.search(text.split(body.MARKER, 1)[0])
    try:
        return json.loads(m.group(1)) if m else dict(NO_LINKS)
    except json.JSONDecodeError:
        return dict(NO_LINKS)


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


CODE = re.compile(r"((?:^|(?<=\n))```[^\n]*\n.*?\n```(?=\n|$)|(?<!\\)`[^`\n]+`)", re.S)


def escape(text):
    """`<`, `>` and `&` escaped so words draw no HTML, but left as written inside markdown code, where GitHub shows
    them as written: an inline `span` on one line, or a fenced block."""
    parts = CODE.split(text or "")
    return "".join(p if i % 2 else html.escape(p, quote=False) for i, p in enumerate(parts))


RAISE_ICON = {"question": "question", "blocker": "blocker", "issue": "issue found"}


def raises_of(h):
    """The raises a hand-back carries; none for a record posted before raises existed."""
    v = h.get("raises") if isinstance(h, dict) else None
    return [r for r in v if isinstance(r, dict) and r.get("kind") in RAISE_ICON] if isinstance(v, list) else []


def answers_of(h):
    """The answers a hand-back gives to earlier raises, by their IDs."""
    v = h.get("answers") if isinstance(h, dict) else None
    return [a for a in v if isinstance(a, dict) and a.get("raise")] if isinstance(v, list) else []


SHORT = re.compile(r"(?<![\w&/\[`])#(\d+)\b(?!\])")


def short_refs(repo, text):
    """Bare #N in prose written as a plain link, [#N](address): inside a bullet GitHub otherwise draws each one with its
    title and icon, which buries the sentence (tested on card-gallery #40). Code spans are left alone."""
    parts = re.split(r"(`[^`\n]*`)", text or "")
    return "".join(p if i % 2 else SHORT.sub(lambda m: f"[#{m.group(1)}]({ref(repo, m.group(1))})", p)
                   for i, p in enumerate(parts))


def raise_line(repo, r):
    """One raise as a list item: icon, label, words and who it is for.

    Its ID is never drawn."""
    words = lambda s: short_refs(repo, escape(" ".join(str(s).split())))
    label = f"**{words(r['label'])}:** " if isinstance(r.get("label"), str) and r["label"].strip() else ""
    who = ("filed as an issue" if r["kind"] == "issue" else
           "for you" if r.get("to") == "owner" else f"for the {words(r.get('to') or 'no one')}")
    return f"- {field_icon(repo, RAISE_ICON[r['kind']])} {label}{words(r.get('text') or '')} · {who}"


def asked(rec, url=None):
    """The owner's to-do for the questions and blockers `rec` raised for them.

    It reads "answer 2 questions", "answer 1 blocker" or "answer 1 question and 1 blocker", linked to the comment at
    `url`, then how to answer; None when it raised none. The same raise counts once, by its ID or its kind and words."""
    from dokima import agent
    seen, count = set(), {"question": 0, "blocker": 0}
    for r in agent.owner_raises(rec.get("handback") or {}):
        keys = {("id", r.get("id")), (r["kind"], " ".join(str(r.get("text") or "").split()))} - {("id", None)}
        if keys & seen:
            continue
        seen |= keys
        count[r["kind"]] += 1
    parts = [f"{n} {k}{'' if n == 1 else 's'}" for k, n in count.items() if n]
    if not parts:
        return None
    words = "answer " + " and ".join(parts)
    how = ("with `/plan`, `/work` or `/review`" if rec.get("role") == "reviewer" else
           "with `/plan`" if count["blocker"] else "with `/plan`, or say `/review`")
    return f"{f'[{words}]({url})' if url else words} {how}"


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


def todo(issue, found, rec, url=None):
    """What the owner must do now the river stopped on record `rec`, posted at `url`."""
    from dokima import agent
    role, h = rec.get("role"), rec.get("handback") or {}
    if role == "not-started":
        return TODO["not started"]
    if not rec.get("check", {}).get("passed"):
        return TODO["rejected"]
    if role in ("planner", "reviewer") and asked(rec, url):
        return asked(rec, url)
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
    owners = found.get("owners") or set()
    # A build started since the newest record is Work, with nothing for the owner, as on the board.
    begun = [s for s in (agent.started(c, owners) for c in items[at[-1] + 1:]) if s]
    if begun and begun[-1] == "Work":
        return "Work", None
    column, needs = agent.board_place(rec, agent.next_step(items[:at[-1]], rec, owners))
    # A pull request autopilot put in the merge queue is GitHub's to merge, so nothing is the owner's.
    needs = needs and not agent.queued_since(items, at[-1])
    return column, todo(issue, found, rec, items[at[-1]].get("url")) if needs else None


def status_line(repo, stage, todo):
    """The small status line under the summary: the stage, then Needs you and the owner's to-do when there is one."""
    head = f"{field_icon(repo, 'merged')} **{stage}**" if stage == "Merged" else f"**{stage}**"
    return head + (f" · {field_icon(repo, 'needs you')} Needs you: {todo}" if todo else "")


def child_row(repo, child):
    """One child of a split: its bare link, then its stage, or unknown when unread.

    GitHub draws the child's title from the bare link, so it is not written out."""
    st = child.get("stage") if child.get("stage") in STAGES else "unknown"
    if st == "Merged":
        st = f"{field_icon(repo, 'merged')} {st}"
    n = child["number"]
    return f"- https://github.com/{repo}/issues/{n} · {st}"


def links_row(repo, issue, pr, worker, check_runs, page="issue"):
    """The latest run, the issue on the PR's page, the PR and its files changed.

    On the issue's own page GitHub shortens a link to that page to a bare #N, so the issue leaves its own link out
    (#452). The issue and the PR are written out bare, so GitHub draws them as its own references."""
    links = []
    if worker:
        links.append(f"[latest run]({worker['html_url']})")
    if page == "pr":
        links.append(issue["url"])
    if pr:
        links.append(f"https://github.com/{repo}/pull/{pr['number']}")
    if pr:
        links.append(f"{field_icon(repo, 'files changed')} [files changed](https://github.com/{repo}/pull/{pr['number']}/files)")
    return " · ".join(links)


def criterion_item(repo, label, c, check, tests):
    """One criterion bullet: its status circle, its label linked to its check, its words plain.

    The label links only when there is a check. Under it one italic Verified by line per test with a docstring, only
    the words Verified by linking to the test, then Source: and the link to where the owner asked for it written out
    bare, so GitHub draws it as its own reference, when it has one."""
    if check:
        label = f'<a href="{check["html_url"]}">{label}</a>'
    out = [f"- {circle(repo, state(check))} **{label}:** {escape(c.get('text'))}"]
    for t in tests:
        if t and t.get("verified_by"):
            out.append(f'  - *<a href="{t["url"]}">{field_icon(repo, "verified by")} Verified by</a>: '
                       f'{escape(t["verified_by"])}*')
    if c.get("source"):
        out.append(f'  - Source: {full_refs(repo, c["source"])}')
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


def review_running(items):
    """True while the bot's code review run card since the newest build awaits its record."""
    from dokima import agent
    running = False
    for c in items or []:
        rs = agent.records([c])
        if rs:
            if rs[0].get("role") == "worker" or (rs[0].get("role") == "reviewer" and rs[0].get("stage") == "pr"):
                running = False
            continue
        if (c.get("author") or {}).get("login") in (agent.BOT, f"{agent.BOT}[bot]") and \
                re.match(re.escape(agent.LIVE) + r"[^*]*\*\*Reviewer \(pr\)\*\*", (c.get("body") or "").strip()):
            running = True
    return running


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
    review_st = ("running" if review_running(found.get("items")) else "not started" if not review else
                 "passed" if review["handback"].get("verdict") == "approve" else "failed")
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
    reviews, the code owners, the plan's tests and the latest worker run. It is the same on either `page`, but for the
    PR's top row, which also links the issue."""
    from dokima import agent
    recs, pr, check_runs, worker = found["recs"], found["pr"], found["check_runs"], found["worker"]
    by_key = checks_by_key(check_runs)
    all_tests = next((r for r in check_runs if r["name"] == ALL_TESTS), None)
    planned = agent.latest(recs, "planner")
    h = planned["handback"] if planned else None
    lines = [plan.CARD_START]
    if found.get("sources"):
        lines += [f"<!-- dokima-linked-from: {', '.join(str(n) for n in found['sources'])} -->"]
    gh_links = found.get("blocking")
    if gh_links is not None:
        lines += [f"<!-- dokima-blocking: {json.dumps(gh_links)} -->"]
    if h and isinstance(h.get("summary"), str) and h["summary"].strip():
        lines += [escape(h["summary"].strip()), ""]
    lines += [status_line(repo, *status(issue, found)), ""]
    links = links_row(repo, issue, pr, worker, check_runs, page)
    if links:
        lines += [links, ""]
    children = found.get("children") or []
    if children:
        lines += ["**Stories:**", ""] + [child_row(repo, c) for c in children] + [""]
    own = h.get("links") if h else None
    if gh_links is not None and isinstance(own, dict) and planned is agent.approved_plan(recs):
        # An approved plan's blocking links are on GitHub now, so the card shows GitHub's, as they are right then.
        own = {"relates_to": own.get("relates_to")}
    related = link_lines(repo, merged(own, found.get("linked")))
    if found.get("unread"):
        related.insert(0, f"{field_icon(repo, 'blocked by')} **Blocked by and Blocks:** GitHub could not list this "
                          f"issue's blocked-by links: {escape(found['unread'])}")
    if (gh_links or {}).get("loop"):
        related.append(f"{field_icon(repo, 'blocker')} {agent.named(gh_links['loop'])} block each other on GitHub: "
                       "removing one of their blocked-by links breaks the loop.")
    if related:
        lines += related + [""]
    if not h:
        # With no plan, the Definition of Done goes below the owner's text (#371): body.redraw puts it after the fold.
        return "\n".join(lines + [plan.CARD_END, "", body.DONE, done_row(repo, found, all_tests)])
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
        lines += [" ".join(["**Scope:**", ", ".join(f"`{s}`" for s in h.get("scope") or [])]).rstrip(), ""]
        if h.get("out_of_scope"):
            lines += fold("Out of scope", [f"- {full_refs(repo, escape(s))}" for s in h["out_of_scope"]]) + [""]
    # The Definition of Done goes last, below the Original issue fold: body.redraw puts it after the fold.
    return "\n".join(lines + [body.FOLDED, plan.CARD_END, "", body.DONE, done_row(repo, found, all_tests)])


def issue_body(card, notes):
    """The issue's text: the card, then any notes, kept as written."""
    return card + ("\n\n" + notes if notes else "")


def pr_body(card, text, ask, issue_url=None):
    """The PR's description: the card, then the owner's Original issue fold, with no Closes line (#416).

    The card links the issue, and card.yml closes it when the pull request merges. In the PR's copy a `#` after a
    closing keyword is written `&#35;`, and the `h` of a full address after one `&#104;`, which show the same, so the
    owner's words never close or name another issue (#373). `text` and `issue_url` are no longer read."""
    closing = None
    shown = KEYWORD_URL.sub(r"\1&#104;", KEYWORD_HASH.sub(r"\1&#35;", ask or ""))
    card, done = card.split(body.DONE, 1) if body.DONE in card else (card, "")
    return (card.rstrip("\n") + "\n\n" + body.MARKER + body.FOLD_START + shown + body.FOLD_END
            + (body.TRAILER + done.strip("\n") if done.strip() else "") + ("\n\n" + closing if closing else ""))


def shows(current, top):
    """True when the issue body already shows `top` above its marker, as saved."""
    try:
        return body.redraw(current, top) == current
    except body.Refused:
        return False


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
    if os.environ.get("ON_PR"):
        # A comment on a pull request carries the pull request's number as the issue's.
        pr = int(os.environ["ON_PR"])
        return plan.pr_issue_number(repo, pr), pr
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


def refresh(repo, numbers, cache, bodies=None):
    """Redraw each card whose blocking links or loop on GitHub differ from what it shows.

    One that cannot be updated is named in the run and the others still go on; returns how many failed."""
    failed = 0
    for n in numbers:
        try:
            text = (bodies or {}).get(n)
            if text is None:
                text = json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("body") or ""
            if github_links(repo, n, cache) != shown_links(text):
                draw(repo, n, issue_pr(repo, n), cache=cache)
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            print(f"::error title=Card not updated::the card of #{n} could not be updated: {reason(e)}")
            failed += 1
    return failed


def follow(repo, number, before, now, cache):
    """Update the cards of the issues linked to one just drawn, when their links changed.

    Every issue it blocks, is blocked by or loops with, on GitHub now or on its card before, so a link a person added
    or removed by hand shows on both sides."""
    others = {n for links in (before, now) for k in NO_LINKS for n in links.get(k) or []}
    return refresh(repo, sorted(others - {int(number)}), cache)


def last_sweep(repo):
    """When the last 15-minute sweep that succeeded started: (time, None), or (None, why).

    Only card.yml's scheduled runs count, never its runs on issue events, comments and merges. Counting from the
    start, not the end, keeps a change made while that sweep ran."""
    try:
        runs = json.loads(gh("api", f"repos/{repo}/actions/workflows/card.yml/runs?event=schedule&status=success"
                                    "&per_page=1"))["workflow_runs"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError) as e:
        return None, f"GitHub cannot list the earlier sweeps: {reason(e)}"
    started = [r.get("run_started_at") or r["created_at"] for r in runs]
    return (max(started), None) if started else (None, "no sweep has succeeded yet")


def stale_cards(repo, cache):
    """Redraw each issue and PR card that does not show its issue's state now.

    Open or closed, it looks only at the issues and PRs updated since the last sweep that succeeded, and every card
    when GitHub cannot say what changed; an update to either an issue or its PR redraws both. One that cannot be redrawn is named in the
    run and the others still go on; returns how many failed."""
    from dokima import agent
    since, why = last_sweep(repo)
    if why:
        print(f"::warning title=Every card rechecked::{why}, so every card is rechecked.")
    query = f"since={since}&state=all&per_page=100" if since else "state=all&per_page=100"
    try:
        items = [i for p in agent.pages(gh("api", f"repos/{repo}/issues?{query}", "--paginate")) for i in p]
    except (subprocess.CalledProcessError, json.JSONDecodeError, TypeError) as e:
        print(f"::error title=Cards not checked::GitHub cannot list the issues updated since {since or 'ever'}: "
              f"{reason(e)}")
        return 1
    failed, work = 0, {}
    for i in items:
        if "pull_request" not in i:
            work.setdefault(i["number"], None)
            continue
        try:
            n = plan.pr_issue_number(repo, i["number"])
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"::error title=Card not updated::the card of PR #{i['number']} could not be updated: {reason(e)}")
            failed += 1
            continue
        if n:
            work[n] = i["number"]
    for n, pr_number in sorted(work.items()):
        try:
            draw(repo, n, pr_number or issue_pr(repo, n), cache=cache, changed_only=True)
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            print(f"::error title=Card not updated::the card of #{n} could not be updated: {reason(e)}")
            failed += 1
    return failed


def sweep(repo):
    """The scheduled run: close finished parents, redraw cards whose links changed, then stale cards.

    A finished parent is an open one whose sub-issues are all closed (see agent.close_done_trees).

    The link check looks at every open issue and every issue linked to one; the stale cards are looked for only among
    the issues and PRs updated since the last sweep (see stale_cards)."""
    from dokima import agent
    cache, failed = {}, 0
    try:
        # The safety net for a close whose run never went: every open parent whose sub-issues are all closed closes.
        for line in agent.close_done_trees(repo):
            print(line)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        print(f"::error title=Parents not closed::the open parents whose sub-issues are all closed could not be closed: {reason(e)}")
        failed += 1
    bodies = {i["number"]: i["body"] for i in agent.open_issues(repo)}
    numbers = set(bodies)
    for n, text in bodies.items():
        got = blocking(repo, n, cache)
        numbers |= {m for links in (got if isinstance(got, dict) else {}, shown_links(text))
                    for k in NO_LINKS for m in links.get(k) or []}
    return failed + refresh(repo, sorted(numbers), cache, bodies) + stale_cards(repo, cache)


def stop_for_loop(repo, number, loop, owners):
    """On autopilot, a loop of issues blocking each other stops the river for the owner.

    One comment mentioning them, and the Needs you pill. Off autopilot nothing runs, so the card's loop line is all.
    When GitHub cannot say whether the issue is on autopilot, the river stops."""
    from dokima import agent
    if agent.on_autopilot(repo, number) is False:
        return
    mention = " ".join(f"@{o}" for o in sorted(owners or []))
    gh("issue", "comment", str(number), "-R", repo, "--body",
       f"{mention} {agent.named(loop)} block each other on GitHub, so the river stops here for you: remove one of "
       "their blocked-by links to break the loop.".strip())
    spec = os.environ.get("DOKIMA_BOARD")
    if spec:
        from dokima import board
        b = board.Board(spec, repo)
        b.set(b.item("issue", int(number)), "Action", "Needs you")


def main():
    if sys.argv[1:2] == ["gallery"] and len(sys.argv) == 3:
        gallery(os.environ.get("REPO") or "dokima-dev/dokima", sys.argv[2])
        return
    repo = os.environ["REPO"]
    if not os.environ.get("ISSUE_NUMBER") and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        # A sweep or redraw the empty API budget stopped runs once more, from scratch, after the budget resets.
        sys.exit(1 if retry.once_more("the card sweep", lambda: sweep(repo), failed=bool) else 0)
    number, pr_number = find_work(repo)
    if not number:
        print("No issue for this event; nothing to write.")
        return

    def redraw():
        cache = {}
        before, now = draw(repo, number, pr_number, cache=cache)
        return follow(repo, number, before, now, cache)

    if retry.once_more(f"the card of #{number}", redraw, failed=bool):
        sys.exit(1)


def draw(repo, number, pr_number, plans=None, noted=None, cache=None, changed_only=False):
    """Write the card at the top of the issue and its PR.

    Returns the blocking links and loop its card showed before and shows now. With `changed_only`, a card that
    already shows what it would be drawn as is not rewritten.
    `plans` gives the links of a plan approved just now, by issue (see their_links). `noted` adds (True) or removes
    (False) issues from the index of those whose approved plans link here. The Blocked by and Blocks lines are
    GitHub's own blocked-by links, read now; `cache` keeps what this run already read.
    """
    cache = {} if cache is None else cache
    issue = plan.fetch_issue(repo, number)
    found = gather(repo, number, pr_number)
    sources = set(linked_from(issue["current_body"]))
    for s, on in (noted or {}).items():
        (sources.add if on else sources.discard)(s)
    found["sources"] = sorted(sources)
    before, now = shown_links(issue["current_body"]), github_links(repo, int(number), cache)
    found["blocking"] = now
    if now.get("unread"):
        found["unread"] = reason(blocking(repo, int(number), cache))
    found["linked"] = {"relates_to": their_links(repo, number, found["sources"], plans)["relates_to"],
                       "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
    pr = found["pr"]
    # Only the part above the marker is code's; the owner's ask below it is saved as it is, or the save is refused.
    current, top = issue["current_body"] or "", render(repo, issue, found)
    if not (changed_only and shows(current, top)) and body.save(repo, number, current, top):
        print(f"Card written into issue #{number}")
    if now.get("loop") and now["loop"] != before.get("loop"):
        stop_for_loop(repo, number, now["loop"], found.get("owners"))
    # The PR gets the same card, open, merged or closed, so it never keeps an older card than the issue (#224); its
    # top row also links the issue, and it closes the issue by its full address (#452).
    ask = body.ask(current)
    described = pr and pr_body(render(repo, issue, found, page="pr"), pr.get("body"), ask, issue_url=issue["url"])
    if pr and not (changed_only and described == (pr.get("body") or "")):
        with open("pr.md", "w") as f:
            f.write(described)
        gh("api", "-X", "PATCH", f"repos/{repo}/pulls/{pr_number}", "-F", "body=@pr.md")
        print(f"Card written into PR #{pr_number}")
    return before, now


if __name__ == "__main__":
    main()

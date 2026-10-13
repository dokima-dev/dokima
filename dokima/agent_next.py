"""Next lines: what the river does after a record, and where the card goes.

Also the Next line every card ends with. Split out of dokima/agent.py (#636).
"""
import os
import re

from dokima import card


def agents_text():
    """AGENTS.md as the runtime has it, from main; empty when there is none."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AGENTS.md")
    try:
        return open(path).read()
    except OSError:
        return ""


def said_there(words, source, items, body, owners, number, parent=None):
    """True when the words appear word for word where the source says: the issue's own
    text, a code owner's comment on this issue, or AGENTS.md; given the parent (parent_words), also the parent's own
    text or a code owner's comment on it. Anything else, a comment by anyone else (the bot included) or one not found,
    is False."""
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
    """What `/autopilot start` picks up on the issue: "worker" for an approved plan waiting for
    `/work`, "split" for an approved split not yet filed, else None, decided by the river as if the approval came on
    autopilot. Nothing is picked up twice: not after the owner's `/work`, an Autopilot line, or a worker or split record
    since the approval."""
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
    """True when the newest plan is a re-plan a code review asked for with a
    test blocker, the owner has not spoken since that review, and its criteria are exactly those of the plan the owner
    approved with `/work`."""
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
    """Where the card goes after this run: the column of the stage now running, or
    of this stage when it stops for the owner, and the Needs you pill exactly when the river stops for the owner (not
    after a cancel)."""
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
        return f"**Next:** {step[4] + ' ' if len(step) > 4 else ''}{who} starts now."
    if step[0] in ("cancelled", "merged", "waiting", "queued"):
        return f"**Next:** {step[1]}"
    mention = " ".join(f"@{o}" for o in owners)
    return f"**Next:** {mention} {step[1]}".strip()


# The other agent job files, imported last so the job files can use each other (#636).
from dokima.agent_github import BOT
from dokima.agent_records import LIVE, records, latest, approved, is_record, settled, owner_raises, for_planner
from dokima.agent_checks import issue_url, owner_source
from dokima.agent_roles import command_of
from dokima.agent_autopilot import AUTOPILOT_LINES, UNREAD, AUTOPILOT_MERGE

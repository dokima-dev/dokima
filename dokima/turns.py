"""Build turns: stories of one parent sharing a code file take turns to build (#668).

A story holds the turn once its build has started (a worker ran on it, or its pull request is open), until its pull
request merges. Another open story of the same parent whose plan shares a code file with it waits; planning and plan
review never do, and markdown files never count. Each story's files are its own newest plan's, so a story whose planner
added files beyond its assigned ones is checked on its final list.
"""
import json

from dokima import agent_github
from dokima.agent_records import records, latest
from dokima.planner import code_files


def plan_code_files(recs):
    """The code files of the newest passed plan among these records."""
    plan = latest(recs, "planner")
    h = (plan or {}).get("handback") or {}
    return set().union(*(code_files(c) for c in h.get("acceptance_criteria", []) + h.get("non_functional", [])))


def building(repo, number, recs):
    """True when the issue's build has started and its pull request has not merged."""
    prs = json.loads(agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "all",
                                     "--json", "state"))
    if any(p.get("state") == "MERGED" for p in prs):
        return False
    return any(p.get("state") == "OPEN" for p in prs) or latest(recs, "worker", passed=False) is not None


def siblings(repo, number):
    """The other open stories of the issue's parent, with their records.

    None when it has no parent.

    GitHub failing to list them raises its error."""
    up = agent_github.parent_of(repo, number)
    if not up:
        return []
    out = []
    for s in agent_github.sub_issues(repo, up):
        if s["number"] == int(number) or s.get("state") == "closed":
            continue
        out.append((s["number"], records(agent_github.conversation(repo, s["number"])[1])))
    return out


def holder(repo, number, recs):
    """The open story holding the turn on a code file this plan changes.

    Returns (its number, the shared files), or None when no story holds it.

    GitHub failing to say raises its error."""
    mine = plan_code_files(recs)
    if not mine:
        return None
    for n, theirs in siblings(repo, number):
        shared = mine & plan_code_files(theirs)
        if shared and building(repo, n, theirs):
            return n, sorted(shared)
    return None


def waits_line(held):
    """Why the build waits, naming the story holding the turn and the shared files."""
    n, files = held
    return f"#{n} is building {', '.join(f'`{f}`' for f in files)}, which this story changes too, until its pull request merges."


def turn_ended(repo, number, recs):
    """True when a closed sibling shares a code file and no one holds the turn.

    So a story that waited its turn plans again once the story it waited for has merged."""
    mine = plan_code_files(recs)
    up = agent_github.parent_of(repo, number) if mine else None
    if not up:
        return False
    done = [s["number"] for s in agent_github.sub_issues(repo, up) if s["number"] != int(number) and s.get("state") == "closed"]
    ended = any(mine & plan_code_files(records(agent_github.conversation(repo, n)[1])) for n in done)
    return ended and holder(repo, number, recs) is None

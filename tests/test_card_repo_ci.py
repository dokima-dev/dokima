"""Tests for #859: the card follows the repo's own CI.

Two promises. When the repo's own CI (a workflow of the adopter's, not Dokima's) finishes on a pull request, the
issue's card is redrawn (859.1). And the card shows each check the branch rule requires, the repo's own included,
with its state (859.2).

859.1 is played the way GitHub plays it in an adopter's repo: the thin workflow `dokima/install/dokima.yml` must
start on the CI's workflow_run (its `workflows:` filter read as GitHub reads it, globs included), `entry.yml`'s card
job must take the event, and the card workflow it calls is then played with tests/card_player.py against a fake
GitHub, which must end with the issue's card redrawn.

859.2 plays a finished check against the same fake GitHub, with a branch rule on main that requires the repo's own
checks besides Dokima's. The fake's `gh` is wrapped so it also answers the branch rule (every way GitHub gives it:
the branch, its protection and its rulesets) and the commit's statuses. Nothing leaves the machine.
"""
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_player as cp  # noqa: E402
from test_start import NIL, Ctx, condition  # noqa: E402

ROOT = cp.ROOT
THIN = os.path.join(ROOT, "dokima", "install", "dokima.yml")
ENTRY = os.path.join(cp.WORKFLOWS, "entry.yml")
CI = "ci"  # the repo's own CI workflow, a name Dokima cannot know beforehand
REQUIRED = ["all tests", "Acceptance criteria", "lint", "build"]


# --- 859.1: playing the adopter's thin workflow, entry.yml and the card -------------------------------------------

def glob_matches(patterns, name):
    """True when a workflow_run `workflows:` filter lets workflow `name` through, as GitHub reads its globs.

    `**` matches anything, `*` anything but `/`, `\\` escapes the next character, and a later `!pattern` takes a
    name back out."""
    def regex(p):
        out, i = "", 0
        while i < len(p):
            if p[i] == "\\" and i + 1 < len(p):
                out, i = out + re.escape(p[i + 1]), i + 2
            elif p.startswith("**", i):
                out, i = out + ".*", i + 2
            elif p[i] == "*":
                out, i = out + "[^/]*", i + 1
            else:
                out, i = out + re.escape(p[i]), i + 1
        return re.compile(out + r"\Z")
    hit = False
    for p in [patterns] if isinstance(patterns, str) else list(patterns or []):
        p = str(p)
        if p.startswith("!"):
            hit = hit and not regex(p[1:]).match(name)
        elif regex(p).match(name):
            hit = True
    return hit


def thin_starts(event):
    """True when the adopter's thin workflow starts a run for this workflow_run event."""
    wf = yaml.safe_load(open(THIN).read()) or {}
    on = wf.get("on", wf.get(True)) or {}
    t = on.get("workflow_run") if isinstance(on, dict) else None
    if not isinstance(t, dict):
        return False
    types = t.get("types")
    if types and event["action"] not in ([types] if isinstance(types, str) else types):
        return False
    return glob_matches(t.get("workflows"), event["workflow"]["name"])


def evaluate(expr, ctx):
    """One GitHub expression of a job's `if:`, with `contains` and `fromJSON` as GitHub has them."""
    parts = re.split(r"('[^']*')", expr)
    for i in range(0, len(parts), 2):
        p = parts[i].replace("&&", " and ").replace("||", " or ").replace("!=", "\0")
        p = re.sub(r"!", " not ", p).replace("\0", "!=")
        p = re.sub(r"\bnull\b", "NIL", re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", p)))
        parts[i] = p

    def contains(s, x):
        if isinstance(s, list):
            return any(str(v).lower() == str(x).lower() for v in s)
        return str(x).lower() in str(s).lower()
    names = {**ctx, "NIL": NIL, "always": lambda: True, "success": lambda: True, "failure": lambda: False,
             "cancelled": lambda: False, "contains": contains, "fromJSON": json.loads,
             "startsWith": lambda s, p: str(s).lower().startswith(str(p).lower())}
    return bool(eval("".join(parts), {"__builtins__": {}}, names))


def entry_calls_card(event_name, event):
    """True when entry.yml's card job runs for this event."""
    job = (cp.load_yaml(open(ENTRY).read()).get("jobs") or {}).get("card") or {}
    ctx = {"github": Ctx({"event_name": event_name, "event": wrap(event)}), "vars": Ctx(), "secrets": Ctx()}
    cond = condition(job.get("if")).replace("success() && ", "", 1)
    return evaluate(cond, ctx)


def wrap(v):
    """A JSON value as an expression context, where a missing name is null."""
    if isinstance(v, dict):
        return Ctx({k: wrap(x) for k, x in v.items()})
    if isinstance(v, list):
        return [wrap(x) for x in v]
    return v


def ci_finished(n, p, conclusion="success"):
    """The event GitHub sends when the repo's own CI finishes on PR p."""
    run = {"name": CI, "head_sha": f"sha{p}", "head_branch": f"try/issue-{n}", "display_title": f"Issue {n}",
           "event": "pull_request", "status": "completed", "conclusion": conclusion,
           "pull_requests": [{"number": p, "head": {"ref": f"try/issue-{n}", "sha": f"sha{p}"}, "base": {"ref": "main"}}]}
    return "workflow_run", {"action": "completed", "workflow": {"name": CI}, "workflow_run": run,
                            "sender": cp.sender(cp.OWNER), "repository": cp.REPOSITORY}


def assert_ci_redraws(tmp_path, conclusion, k):
    """Play the repo's CI finishing on PR #260; fail naming k unless the card redraws."""
    event_name, event = ci_finished(246, 260, conclusion)
    assert thin_starts(event), \
        (f"{k}: the adopter's workflow does not start when the repo's own CI ({CI!r}) finishes, so its card is "
         f"never redrawn")
    assert entry_calls_card(event_name, event), \
        (f"{k}: the repo's own CI finishing on a pull request starts Dokima, but entry.yml's card job skips it, so "
         f"the card is not redrawn")
    hub = cp.Hub(tmp_path)
    # Called from entry.yml, the card workflow runs for the caller's event, whatever its own `on:` lists.
    card = dict(cp.workflow(), on={"workflow_run": {"workflows": [CI], "types": ["completed"]}})
    r = cp.Run(hub, event_name, event, card)
    assert r.card_ran(), f"{k}: the card workflow ran for the repo's CI but its card job was skipped"
    assert not r.failed(), f"{k}: the card workflow failed on the repo's CI finishing:\n{r.log[-3000:]}"
    assert "An old card, drawn before the last event." not in hub.issue_body(246), \
        f"{k}: issue #246 still shows its old card after the repo's own CI finished on its pull request"


def test_the_repos_own_ci_finishing_redraws_the_card(tmp_path, record_property):
    """When the repo's own CI finishes on a pull request, its issue's card is redrawn.

    Plays a workflow of the repo's own, named `ci` and started by the pull request, finishing on PR #260: the
    adopter's workflow must start on it, entry.yml must call the card on it, and issue #246's stale card must be
    replaced. Proves 859.1."""
    record_property("proves", "859.1")
    assert_ci_redraws(tmp_path, "success", "859.1")


def test_the_repos_own_ci_failing_redraws_the_card(tmp_path, record_property):
    """A failed run of the repo's own CI redraws the card too.

    The same play as the passing run, with the CI run ending in failure: the card must still be redrawn, so the
    owner sees the red check. Proves 859.1."""
    record_property("proves", "859.1")
    assert_ci_redraws(tmp_path, "failure", "859.1")


# --- 859.2: the card shows every check the branch rule requires --------------------------------------------------

WRAPPER = r'''
import json, os, re, sys
D = os.environ["FAKE_GH_DIR"]
RULE = json.load(open(os.path.join(D, "rule.json")))
a = sys.argv[1:]
pos = [x for x in a[1:] if not x.startswith("-")]
route = (pos[0] if a[:1] == ["api"] and pos else "").lstrip("/").partition("?")[0]


def out(v):
    print(json.dumps(v))
    sys.exit(0)


checks = {"strict": True, "contexts": RULE["required"], "checks": [{"context": c, "app_id": None} for c in RULE["required"]]}
if route == "repos/o/r/branches/main":
    out({"name": "main", "protected": True, "protection": {"enabled": True, "required_status_checks": dict(checks, enforcement_level="everyone")}})
if route in ("repos/o/r/branches/main/protection/required_status_checks", "repos/o/r/branches/main/protection/required_status_checks/contexts"):
    out(checks if route.endswith("checks") else RULE["required"])
if route == "repos/o/r/branches/main/protection":
    out({"required_status_checks": checks})
if route == "repos/o/r/rules/branches/main":
    out([{"type": "required_status_checks", "parameters": {"strict_required_status_checks_policy": True,
         "required_status_checks": [{"context": c} for c in RULE["required"]]}}])
if route == "repos/o/r/rulesets":
    out([])
m = re.fullmatch(r"repos/o/r/commits/([^/]+)/(status|statuses)", route)
if m:
    sts = RULE["statuses"].get(m.group(1), [])
    if m.group(2) == "statuses":
        out(sts)
    state = "failure" if any(s["state"] in ("failure", "error") for s in sts) else "pending" if any(s["state"] == "pending" for s in sts) else "success"
    out({"state": state, "statuses": sts, "total_count": len(sts), "sha": m.group(1)})
os.execv(sys.executable, [sys.executable, os.path.join(D, "bin", "gh-fake")] + a)
'''


def hub_with_rule(tmp_path, runs=(), statuses=()):
    """The fake GitHub, with main's rule requiring REQUIRED and PR #260 carrying given checks.

    `runs` are (name, status, conclusion) check runs added to the head commit, `statuses` (context, state) commit
    statuses on it."""
    hub = cp.Hub(tmp_path)
    s = hub.load()
    for name, status, conclusion in runs:
        s["checks"]["sha260"].append({"name": name, "status": status, "conclusion": conclusion, "head_sha": "sha260",
                                      "html_url": f"https://github.com/o/r/runs/{name}"})
    hub.save()
    sts = [{"context": c, "state": st, "target_url": f"https://ci.example/{c}", "description": st,
            "created_at": "2026-10-09T05:00:00Z", "updated_at": "2026-10-09T05:00:00Z"} for c, st in statuses]
    json.dump({"required": REQUIRED, "statuses": {"sha260": sts}}, open(os.path.join(hub.dir, "rule.json"), "w"))
    gh = os.path.join(hub.dir, "bin", "gh")
    os.rename(gh, os.path.join(hub.dir, "bin", "gh-fake"))
    open(gh, "w").write(f"#!{sys.executable}\n" + WRAPPER)
    os.chmod(gh, 0o755)
    return hub


def shown_state(card, name):
    """The state the card shows for check `name`, or None when the card lacks it."""
    for line in card.splitlines():
        for part in re.split(r" · |\|", line):
            text = re.sub(r"<[^>]+>", "", part).strip(" *:-")
            if text == name or text.endswith(" " + name) or text.endswith("**" + name):
                alt = re.search(r'alt="(passed|failed|running|not started)"', part)
                if alt:
                    return alt.group(1)
    return None


def drawn_card(hub, k):
    """Issue #246's card after the Acceptance criteria check finishes on PR #260."""
    cp.must_redraw(hub, cp.checks_finished(246, 260), k)
    body = hub.issue_body(246)
    assert "An old card, drawn before the last event." not in body, f"{k}: issue #246's card was not redrawn"
    return body


def test_a_required_repo_check_that_failed_shows_failed(tmp_path, record_property):
    """A required check of the repo's own that failed shows as failed.

    Main's rule requires the repo's own `lint` besides Dokima's checks; `lint` failed on the pull request's head,
    so the card must show `lint` with the failed circle. Proves 859.2."""
    record_property("proves", "859.2")
    hub = hub_with_rule(tmp_path, runs=[("lint", "completed", "failure"), ("build", "completed", "success")])
    card = drawn_card(hub, "859.2")
    got = shown_state(card, "lint")
    assert got == "failed", \
        f"859.2: the branch rule requires the repo's own check 'lint', which failed, but the card shows it as {got}:\n{card[-2500:]}"


def test_a_required_repo_check_that_passed_shows_passed(tmp_path, record_property):
    """The card shows a required check of the repo's own as passed when it passed.

    Main's rule requires `build`, which passed on the pull request's head, so the card must show `build` with the
    passed circle. Proves 859.2."""
    record_property("proves", "859.2")
    hub = hub_with_rule(tmp_path, runs=[("lint", "completed", "failure"), ("build", "completed", "success")])
    card = drawn_card(hub, "859.2")
    got = shown_state(card, "build")
    assert got == "passed", \
        f"859.2: the branch rule requires the repo's own check 'build', which passed, but the card shows it as {got}:\n{card[-2500:]}"


def test_a_required_check_not_yet_run_shows_not_started(tmp_path, record_property):
    """A required check that has not run yet shows as not started.

    Main's rule requires `build`, which is not on the pull request's head at all, so the card must still list
    `build`, with the not started circle. Proves 859.2."""
    record_property("proves", "859.2")
    hub = hub_with_rule(tmp_path, runs=[("lint", "completed", "success")])
    card = drawn_card(hub, "859.2")
    got = shown_state(card, "build")
    assert got == "not started", \
        f"859.2: the branch rule requires 'build', which has not run yet, but the card shows it as {got}:\n{card[-2500:]}"


def test_a_required_check_reported_as_a_commit_status_shows_its_state(tmp_path, record_property):
    """A required check the repo's CI reports as a commit status shows its state too.

    Main's rule requires `lint`, which an outside CI reports as a failed commit status, not a check run, so the card
    must show `lint` as failed. Proves 859.2."""
    record_property("proves", "859.2")
    hub = hub_with_rule(tmp_path, runs=[("build", "completed", "success")], statuses=[("lint", "failure")])
    card = drawn_card(hub, "859.2")
    got = shown_state(card, "lint")
    assert got == "failed", \
        f"859.2: the branch rule requires 'lint', reported as a failed commit status, but the card shows it as {got}:\n{card[-2500:]}"

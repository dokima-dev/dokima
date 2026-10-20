"""Nightly, the owner's journeys play on the sandbox, are cleaned up, failures filed (#258).

The play-through of #437 (dokima/playthrough.py, .github/workflows/playthrough.yml) plays one issue from opened to
merged on dokima-dev/card-gallery, and only from the Run workflow button. #258 asks for more: every night it plays
three journeys the owner walks (a new issue to merged, a question that stops for the owner, a split that files its
stories), acts as a test account standing in for the owner, checks what the owner would see on the cards, cleans up
what it opened, and files a bug on Dokima's own repo for each journey that failed. It gates nothing.

These tests run with no GitHub and no key. The journeys are played with `nightly()` on a fake sandbox that shows the
cards dokima/card.py draws for each step; the real `Sandbox`'s owner steps and clean-up run against a fake `gh` on
PATH; the bug is filed through a fake `gh` too; the workflow is read and its expressions evaluated with
tests/test_start.py's evaluator.
"""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from test_card_running import REPO, rec  # noqa: E402
from test_playthrough import (OWNER, ROOT, SANDBOX, SANDBOX_TOKEN, STEPS, issue_body, items_of, playthrough,  # noqa: E402
                              right_cards, steps_of, workflow)
from test_start import Ctx, condition, evaluate, fill  # noqa: E402
from dokima import agent, card  # noqa: E402

MERGE = "a new issue to merged"
QUESTION = "a question that stops for the owner"
SPLIT = "a split that files its stories"
JOURNEYS = {MERGE: STEPS,
            QUESTION: ("issue opened", "question posted"),
            SPLIT: ("issue opened", "split posted", "split approved", "stories filed")}
MAIN_SHA = "5ea1f00dcafe0123456789abcdef0123456789ab"
APP_TOKEN = "app-token-for-card-gallery-only"
BUG_TOKEN = "workflow-token-that-files-issues"


def draw_issue(steps, children=()):
    """The issue card drawn for issue #1 after `steps`, with these split stories as children."""
    items = items_of(steps)
    found = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "reviews": [],
             "owners": {OWNER}, "tests": {}, "worker": None, "children": list(children)}
    os.environ.setdefault("GITHUB_REPOSITORY", REPO)
    return issue_body(card.render(REPO, {"number": 1, "url": f"https://github.com/{REPO}/issues/1"}, found, "issue"))


def plan(**more):
    """A stand-in style user story plan, as the card reads it."""
    return {"kind": "user_story", "summary": "A thing is built.", "user_story": "The owner sees the thing.",
            "acceptance_criteria": [{"text": "The thing shows.", "source": f"https://github.com/{REPO}/issues/1",
                                     "files": ["app/x.py"]}],
            "non_functional": [], "tests": {}, **more}


QUESTION_RAISE = {"kind": "question", "to": "owner", "label": "Two readings", "text": "Which one do you mean?",
                  "id": "P1", "by": "planner"}


def feature(n):
    """A split into n stories, as the card reads it."""
    return {"kind": "feature", "title": "Play-through split", "summary": "A split.", "feature": "Two stories.",
            "stories": [{"title": f"Play-through story {i + 1}", "user_story": "The owner sees a story.",
                         "acceptance_criteria": [], "non_functional": [], "depends_on": []} for i in range(n)]}


def split_cards(n):
    """For each split journey step, the right issue card and the wrong, not redrawn, one."""
    approve = rec("reviewer", "plan", verdict="approve", blockers=[])
    filed = rec("split", stories=[{"story": i + 1, "issue": 7 + i, "title": f"Play-through story {i + 1}", "id": i + 1,
                                   "blocked_by": []} for i in range(n)])
    children = [{"number": 7 + i, "title": f"Play-through story {i + 1}", "stage": "Backlog"} for i in range(n)]
    f = rec("planner", **feature(n))
    return {"issue opened": (draw_issue([]), draw_issue([f])),
            "split posted": (draw_issue([f]), draw_issue([])),
            "split approved": (draw_issue([f, approve]), draw_issue([f])),
            "stories filed": (draw_issue([f, approve, "/work", filed], children), draw_issue([f, approve, "/work", filed]))}


def question_cards():
    """For every step of the question journey, the right issue card and the wrong one."""
    asked = rec("planner", **plan(raises=[QUESTION_RAISE]))
    return {"issue opened": (draw_issue([]), draw_issue([asked])),
            "question posted": (draw_issue([asked]), draw_issue([rec("planner", **plan(raises=[]))]))}


class NightSandbox:
    """A fake sandbox for nightly() that logs calls and shows each step's right cards.

    `begin(journey)` starts a journey; after each step the cards that step should leave are shown, except for the
    (journey, step) pairs in `stale`, which show the wrong card (the card not redrawn). Card runs finish on the second
    look. Each hand-back folder is read at once, every JSON file in it parsed."""

    def __init__(self, stale=()):
        self.stale = set(stale)
        self.calls, self.journey, self.step, self.looks, self.handbacks = [], None, None, 0, {}
        self.merge = right_cards()

    def install(self):
        """Install the played commit on the fake sandbox."""
        self.calls.append(("install", None, None))

    def begin(self, journey):
        """Start one journey on the fake sandbox."""
        self.calls.append(("begin", journey, None))
        self.journey = journey

    def do(self, step, handback):
        """Play one step of the current journey, noting the hand-back it was given."""
        self.calls.append(("do", self.journey, step))
        self.step, self.looks = step, 0
        got = None
        if handback is not None:
            got = {name: json.load(open(os.path.join(handback, name))) for name in os.listdir(handback)
                   if name.endswith(".json")}
        self.handbacks[(self.journey, step)] = got

    def pending(self):
        """How many card runs of the newest step are still running."""
        self.looks += 1
        return 1 if self.looks < 2 else 0

    def cards(self):
        """The issue and PR bodies as they stand after the newest step."""
        self.calls.append(("cards", self.journey, self.step))
        wrong = (self.journey, self.step) in self.stale
        if self.journey == MERGE:
            i = STEPS.index(self.step)
            return self.merge[STEPS[i - 1] if wrong and i else ("plan posted" if wrong else self.step)]
        if self.journey == QUESTION:
            return question_cards()[self.step][1 if wrong else 0], None
        posted = (self.handbacks.get((SPLIT, "split posted")) or {}).get("plan.json") or {}
        n = len(posted.get("stories") or []) or 2
        return split_cards(n)[self.step][1 if wrong else 0], None

    def clean(self):
        """Clean up the fake sandbox."""
        self.calls.append(("clean", None, None))


def nightly(p, sandbox, k):
    """Run nightly() on a fake sandbox, 1 s wait; return code, lines and bugs."""
    assert hasattr(p, "nightly"), f"{k}: dokima/playthrough.py has no nightly(), so no nightly run plays the journeys"
    lines, bugs = [], []
    start = time.monotonic()
    code = p.nightly(sandbox, 1, 0.01, lines.append, lambda journey, said: bugs.append((journey, list(said))))
    took = time.monotonic() - start
    assert took < 60, f"{k}: nightly() took {took:.0f} s on a fake sandbox with a 1 s wait"
    return code, lines, bugs


def journey_lines(lines, journey):
    """The lines logged for one journey: each names the journey."""
    return [line for line in lines if journey in line]


def check_journey(k, sandbox, lines, journey, stale=()):
    """The journey was begun, played in order, and logged PASS or FAIL per step."""
    steps = JOURNEYS[journey]
    assert ("begin", journey, None) in sandbox.calls, f"{k}: the nightly run never began the journey {journey!r}"
    done = [s for kind, j, s in sandbox.calls if kind == "do" and j == journey]
    assert done == list(steps), f"{k}: the journey {journey!r} should play {list(steps)} in order, not {done}"
    mine = journey_lines(lines, journey)
    assert len(mine) == len(steps), f"{k}: the journey {journey!r} should log one line per step, not {mine}"
    for step, line in zip(steps, mine):
        want = "FAIL: " if step in stale else "PASS: "
        assert line.startswith(want) and step in line, \
            f"{k}: at {journey!r} / {step!r}, the line should start {want!r} and name the step, not {line!r}"


def test_the_nightly_run_plays_a_new_issue_to_merged(record_property):
    """Every night, a new issue is played from opened to merged, judged at each step.

    Proves 258.3.
    Runs dokima/playthrough.py's nightly() on a fake sandbox showing the right cards: the journey `a new issue to
    merged` is begun and its eight steps played in order, each logged `PASS:` naming the journey and step, and the run
    returns 0. Then with the merged card left stale, that step logs `FAIL:` and the run returns 1."""
    record_property("proves", "258.3")
    p = playthrough("258.3")
    hub = NightSandbox()
    code, lines, _ = nightly(p, hub, "258.3")
    check_journey("258.3", hub, lines, MERGE)
    assert code == 0, f"258.3: with every card right, nightly() should return 0, not {code!r}: {lines}"
    hub = NightSandbox(stale={(MERGE, "merged")})
    code, lines, _ = nightly(p, hub, "258.3")
    check_journey("258.3", hub, lines, MERGE, stale={"merged"})
    assert code == 1, f"258.3: with the merged card stale, nightly() should return 1, not {code!r}"


def test_the_nightly_run_checks_a_question_stops_for_the_owner(record_property):
    """Every night, a plan asking the owner a question must show Needs you.

    Proves 258.4.
    Runs nightly() on a fake sandbox: the journey `a question that stops for the owner` opens an issue, then plays a
    stand-in plan whose plan.json raises a question to the owner. When the issue card shows Plan with Needs you:
    answer 1 question, both steps log `PASS:`. When the card shows the plan with no Needs you (the river did not stop
    for the owner), `question posted` logs `FAIL:` and the run returns 1."""
    record_property("proves", "258.4")
    p = playthrough("258.4")
    hub = NightSandbox()
    code, lines, _ = nightly(p, hub, "258.4")
    check_journey("258.4", hub, lines, QUESTION)
    handed = (hub.handbacks.get((QUESTION, "question posted")) or {}).get("plan.json") or {}
    asks = [r for r in handed.get("raises") or [] if r.get("kind") == "question" and r.get("to") == "owner"]
    assert asks, f"258.4: the stand-in plan at `question posted` raises no question to the owner: {handed!r}"
    assert code == 0, f"258.4: with every card right, nightly() should return 0, not {code!r}: {lines}"
    hub = NightSandbox(stale={(QUESTION, "question posted")})
    code, lines, _ = nightly(p, hub, "258.4")
    check_journey("258.4", hub, lines, QUESTION, stale={"question posted"})
    assert code == 1, f"258.4: a question that did not stop for the owner should make nightly() return 1, not {code!r}"


def test_the_nightly_run_checks_a_split_files_its_stories(record_property):
    """Every night, an approved split must list its stories once the owner starts it.

    Proves 258.5.
    Runs nightly() on a fake sandbox: the journey `a split that files its stories` opens an issue, plays a stand-in
    plan whose plan.json is a feature of 2 or more stories, a stand-in plan review that approves it, then the owner's
    /work (no hand-back). When the card shows Work with every story listed, every step logs `PASS:`. When the card
    shows Work with no stories, `stories filed` logs `FAIL:` and the run returns 1."""
    record_property("proves", "258.5")
    p = playthrough("258.5")
    hub = NightSandbox()
    code, lines, _ = nightly(p, hub, "258.5")
    check_journey("258.5", hub, lines, SPLIT)
    handed = (hub.handbacks.get((SPLIT, "split posted")) or {}).get("plan.json") or {}
    assert handed.get("kind") == "feature" and len(handed.get("stories") or []) >= 2, \
        f"258.5: the stand-in plan at `split posted` is not a split into 2 or more stories: {handed!r}"
    review = (hub.handbacks.get((SPLIT, "split approved")) or {}).get("review.json") or {}
    assert review.get("verdict") == "approve", f"258.5: the stand-in plan review at `split approved` does not approve: {review!r}"
    assert hub.handbacks.get((SPLIT, "stories filed"), "never played") is None, \
        "258.5: `stories filed` is the owner's /work, so it needs no agent hand-back"
    assert code == 0, f"258.5: with every card right, nightly() should return 0, not {code!r}: {lines}"
    hub = NightSandbox(stale={(SPLIT, "stories filed")})
    code, lines, _ = nightly(p, hub, "258.5")
    check_journey("258.5", hub, lines, SPLIT, stale={"stories filed"})
    assert code == 1, f"258.5: a split whose stories are not listed should make nightly() return 1, not {code!r}"


FAKE_GH = r'''
import json, os, re, shutil, subprocess, sys
D = os.environ["FAKE_GH_DIR"]
STATE = os.path.join(D, "state.json")
S = json.load(open(STATE))
a = sys.argv[1:]
body = None
for flag in ("--body-file", "-F"):
    if a[:2] == ["issue", "create"] and flag in a and os.path.isfile(a[a.index(flag) + 1]):
        body = open(a[a.index(flag) + 1]).read()
with open(os.path.join(D, "calls.jsonl"), "a") as f:
    f.write(json.dumps({"argv": a, "token": os.environ.get("GH_TOKEN"), "body_file": body}) + "\n")
REPO = S["repo"]


def out(value):
    jq = None
    if "--jq" in a or "-q" in a:
        jq = a[a.index("--jq" if "--jq" in a else "-q") + 1]
    text = json.dumps(value)
    if jq is not None:
        if not shutil.which("jq"):
            sys.exit("fake gh: --jq needs the jq tool, which this machine lacks")
        p = subprocess.run(["jq", "-r", jq], input=text, capture_output=True, text=True)
        sys.stdout.write(p.stdout)
        sys.exit(p.returncode)
    print(text)
    sys.exit(0)


def fail(msg):
    sys.stderr.write(f"fake gh: {msg}: {a}\n")
    sys.exit(1)


def save():
    json.dump(S, open(STATE, "w"), indent=1)


def opt(*names, default=None):
    for n in names:
        if n in a:
            return a[a.index(n) + 1]
    return default


def fields():
    got = {}
    for i, x in enumerate(a[:-1]):
        if x in ("-f", "-F", "--field", "--raw-field"):
            k, _, v = a[i + 1].partition("=")
            if v.startswith("@") and os.path.isfile(v[1:]):
                v = open(v[1:]).read()
            got[k] = v
    return got


def item(n):
    it = S["issues"].get(str(n))
    if not it:
        fail(f"no issue or pull request #{n}")
    return it


def num(x):
    return int(str(x).rstrip("/").rsplit("/", 1)[-1])


def state_of(it):
    return "MERGED" if it.get("merged") else it["state"].upper()


def close(n, delete=False):
    it = item(n)
    if it["state"] == "open":
        it["state"] = "closed"
    if delete and it.get("head") in S["branches"]:
        S["branches"].remove(it["head"])
    save()


def listed(kind, state):
    rows = []
    for n, it in sorted(S["issues"].items(), key=lambda kv: int(kv[0])):
        if (kind == "pr") != bool(it.get("pr")):
            continue
        st = state_of(it)
        if state == "open" and st != "OPEN" or state == "closed" and st == "OPEN" or state == "merged" and st != "MERGED":
            continue
        rows.append({"number": int(n), "title": it["title"], "state": st, "headRefName": it.get("head"),
                     "url": f"https://github.com/{REPO}/{'pull' if it.get('pr') else 'issues'}/{n}"})
    want = opt("--json")
    if want:
        rows = [{k: r.get(k) for k in want.split(",")} for r in rows]
    return rows


def rest(n, it):
    d = {"number": int(n), "title": it["title"], "state": it["state"], "id": 9000 + int(n),
         "html_url": f"https://github.com/{REPO}/{'pull' if it.get('pr') else 'issues'}/{n}"}
    if it.get("pr"):
        d.update(pull_request={"url": f"https://api.github.com/repos/{REPO}/pulls/{n}"},
                 head={"ref": it.get("head")}, merged=bool(it.get("merged")),
                 merged_at="2026-10-19T00:00:00Z" if it.get("merged") else None)
    return d


if a and a[0] in ("issue", "pr"):
    repo = opt("-R", "--repo", default=os.environ.get("GH_REPO"))
    if repo != REPO:
        fail(f"the call names {repo}, not {REPO}")
    if a[1] == "list":
        out(listed(a[0], opt("--state", "-s", default="open")))
    if a[1] == "close":
        close(num(a[2]), delete=a[0] == "pr" and ("--delete-branch" in a or "-d" in a))
        sys.exit(0)
    if a[1] == "view":
        it = item(num(a[2]))
        out({"number": num(a[2]), "title": it["title"], "state": state_of(it), "headRefName": it.get("head")})
    if a[:2] == ["issue", "create"]:
        n = max(int(k) for k in S["issues"]) + 1
        S["issues"][str(n)] = {"title": opt("--title", "-t", default=""), "state": "open"}
        save()
        print(f"https://github.com/{REPO}/issues/{n}")
        sys.exit(0)
    fail("unsupported issue or pr call")
if a and a[0] == "api":
    rest_args = [x for i, x in enumerate(a[1:], 1) if not x.startswith("-") and a[i - 1] not in (
        "-X", "--method", "-f", "-F", "--field", "--raw-field", "-H", "--header", "--jq", "-q", "--input")]
    path = rest_args[0].lstrip("/") if rest_args else ""
    method = (opt("-X", "--method") or ("POST" if fields() else "GET")).upper()
    path, _, query = path.partition("?")
    q = dict(kv.partition("=")[::2] for kv in query.split("&") if kv)
    prefix = f"repos/{REPO}/"
    if not path.startswith(prefix):
        fail(f"the call does not name {REPO}")
    tail = path[len(prefix):]
    if method == "GET" and tail in ("issues", "pulls"):
        want = q.get("state", "open")
        rows = [rest(n, it) for n, it in sorted(S["issues"].items(), key=lambda kv: int(kv[0]))
                if (tail == "issues" or it.get("pr")) and (want == "all" or it["state"] == want)]
        out(rows)
    m = re.fullmatch(r"(issues|pulls)/(\d+)", tail)
    if m and method == "GET":
        out(rest(m.group(2), item(m.group(2))))
    if m and method == "PATCH":
        if fields().get("state") == "closed":
            close(int(m.group(2)))
        out(rest(m.group(2), item(m.group(2))))
    m = re.fullmatch(r"issues/(\d+)/sub_issues", tail)
    if m and method == "GET":
        out([rest(c, item(c)) for c in S.get("subs", {}).get(m.group(1), [])])
    if method == "GET" and tail == "branches":
        out([{"name": b} for b in S["branches"]])
    m = re.fullmatch(r"git/(?:matching-refs|refs)/heads/?(.*)", tail)
    if m and method == "GET":
        out([{"ref": f"refs/heads/{b}"} for b in S["branches"] if b.startswith(m.group(1))])
    m = re.fullmatch(r"git/refs/heads/(.+)", tail)
    if m and method == "DELETE":
        if m.group(1) not in S["branches"]:
            fail("no such branch")
        S["branches"].remove(m.group(1))
        save()
        sys.exit(0)
    if method == "POST" and tail == "issues":
        n = max(int(k) for k in S["issues"]) + 1
        S["issues"][str(n)] = {"title": fields().get("title", ""), "state": "open"}
        save()
        out(rest(n, S["issues"][str(n)]))
    fail("unsupported api call")
fail("unsupported call")
'''


def fake_gh(tmp_path, monkeypatch, state):
    """Put a fake `gh` on PATH keeping issues, pull requests and branches in a file.

    It answers `gh issue|pr list|view|close` (`pr close --delete-branch` deletes the head branch) and `gh issue
    create`, and `gh api` reads of issues, pulls, sub-issues, branches and refs, a PATCH setting state=closed and a
    DELETE of a branch ref. `--jq` goes through the jq tool. It logs each call's arguments and GH_TOKEN, and refuses
    any call naming another repo. Returns (state file, calls file)."""
    d = tmp_path / "gh"
    (d / "bin").mkdir(parents=True)
    tool = d / "bin" / "gh"
    tool.write_text(f"#!{sys.executable}\n" + FAKE_GH)
    tool.chmod(0o755)
    (d / "state.json").write_text(json.dumps(state))
    monkeypatch.setenv("PATH", f"{d / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("FAKE_GH_DIR", str(d))
    return d / "state.json", d / "calls.jsonl"


def calls_of(path):
    """Every call the fake gh logged."""
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def test_the_owners_steps_are_taken_by_the_test_account(tmp_path, monkeypatch, record_property):
    """A journey's issue is opened with the test account's key, not Dokima's app key.

    Proves 258.2.
    Builds the real Sandbox of dokima/playthrough.py with SANDBOX_TOKEN (the test account's key, limited to
    card-gallery) while GH_TOKEN holds the app's key, and plays `issue opened` against a fake gh: the `issue create`
    call must carry the test account's key, so the issue on the sandbox is the owner's, as when they open one."""
    record_property("proves", "258.2")
    p = playthrough("258.2")
    _, calls = fake_gh(tmp_path, monkeypatch, {"repo": SANDBOX, "issues": {"40": {"title": "Card gallery", "state": "open"}},
                                               "branches": ["main"]})
    monkeypatch.setenv("GH_TOKEN", APP_TOKEN)
    monkeypatch.setattr(p, "SETTLE", 0)
    sb = p.Sandbox(SANDBOX, ROOT, "abc1234", SANDBOX_TOKEN)
    try:
        sb.do("issue opened", None)
    finally:
        shutil.rmtree(sb.work, ignore_errors=True)
    made = [c for c in calls_of(calls) if c["argv"][:2] == ["issue", "create"]]
    assert made, f"258.2: playing `issue opened` opened no issue: {calls_of(calls)}"
    who = {APP_TOKEN: "Dokima's app key", SANDBOX_TOKEN: "the test account's key"}
    for c in made:
        assert c["token"] == SANDBOX_TOKEN, \
            f"258.2: the journey's issue was opened with {who.get(c['token'], repr(c['token']))}, not the test account's key"


LEFTOVERS = {"repo": SANDBOX,
             "issues": {"40": {"title": "Card gallery: the plan card", "state": "open"},
                        "41": {"title": "Card gallery: a PR card", "state": "open", "pr": True, "head": "try/issue-40"},
                        "99": {"title": "Play-through of Dokima 0ldc0mm", "state": "closed"},
                        "100": {"title": "Play-through of Dokima 0ldc0mm", "state": "closed", "pr": True,
                                "merged": True, "head": "try/issue-99"},
                        "101": {"title": "Play-through of Dokima abc1234", "state": "open"},
                        "102": {"title": "Play-through of Dokima abc1234", "state": "open", "pr": True,
                                "head": "try/issue-101"},
                        "103": {"title": "Play-through of Dokima abc1234", "state": "open"},
                        "104": {"title": "Play-through story 1", "state": "open"},
                        "105": {"title": "Play-through story 2", "state": "open"}},
             "subs": {"103": [104, 105]},
             "branches": ["main", "try/issue-40", "try/issue-99", "try/issue-101"]}


def clean_sandbox(p, tmp_path, monkeypatch, k):
    """Run the real Sandbox's clean() against a fake gh; return the state after."""
    assert hasattr(p.Sandbox, "clean"), f"{k}: dokima/playthrough.py's Sandbox has no clean(), so nothing is cleaned up"
    state, calls = fake_gh(tmp_path, monkeypatch, LEFTOVERS)
    monkeypatch.setenv("GH_TOKEN", APP_TOKEN)
    sb = p.Sandbox(SANDBOX, ROOT, "abc1234", SANDBOX_TOKEN)
    try:
        sb.clean()
    finally:
        shutil.rmtree(sb.work, ignore_errors=True)
    return json.loads(state.read_text()), calls_of(calls)


def test_after_the_journeys_every_issue_and_pull_request_they_opened_is_closed(tmp_path, monkeypatch, record_property):
    """After the journeys, every issue and pull request they opened is closed.

    Proves 258.6.
    Runs nightly() on a fake sandbox, once with every card right and once with a journey failing: clean() is called
    after the last journey's last step both times. The stand-in split's stories are titled `Play-through ...`, as
    every issue a journey opens is. Then runs the real Sandbox's clean() against a fake gh holding the gallery's
    issue #40 and PR #41 and a night's play-through issues #101 and #103, PR #102 and the split's stories #104 and
    #105: all five play-through ones end closed, #40 and #41 stay open."""
    record_property("proves", "258.6")
    p = playthrough("258.6")
    for stale in ((), {(MERGE, "plan approved")}):
        hub = NightSandbox(stale=stale)
        nightly(p, hub, "258.6")
        kinds = [c[0] for c in hub.calls]
        assert "clean" in kinds, f"258.6: the nightly run never cleaned up (stale cards: {sorted(stale)})"
        last = max(i for i, c in enumerate(hub.calls) if c[0] == "do")
        assert kinds.index("clean") > last, f"258.6: the nightly run cleaned up before its last journey ended: {hub.calls}"
    stories = ((hub.handbacks.get((SPLIT, "split posted")) or {}).get("plan.json") or {}).get("stories") or []
    for st in stories:
        assert str(st.get("title", "")).startswith("Play-through"), \
            f"258.6: the stand-in split files a story titled {st.get('title')!r}, which clean-up cannot tell from the gallery's"
    after, made = clean_sandbox(p, tmp_path, monkeypatch, "258.6")
    still = sorted(int(n) for n, it in after["issues"].items() if it["state"] == "open")
    assert still == [40, 41], (f"258.6: after clean-up the open issues and pull requests should be the gallery's #40 and "
                               f"#41 only, not {still}; calls: {[c['argv'] for c in made][:12]}")


def test_after_the_journeys_every_branch_they_pushed_is_deleted(tmp_path, monkeypatch, record_property):
    """After the journeys, every branch they pushed is deleted.

    Proves 258.7.
    Runs the real Sandbox's clean() against a fake gh holding main, the gallery PR's branch try/issue-40, the branch
    of a merged play-through PR (try/issue-99) and of an open one (try/issue-101): only main and try/issue-40 are
    left."""
    record_property("proves", "258.7")
    p = playthrough("258.7")
    after, made = clean_sandbox(p, tmp_path, monkeypatch, "258.7")
    assert sorted(after["branches"]) == ["main", "try/issue-40"], \
        (f"258.7: after clean-up the branches should be main and the gallery's try/issue-40 only, not "
         f"{sorted(after['branches'])}; calls: {[c['argv'] for c in made][:12]}")


def test_a_failed_journey_files_a_bug_on_dokimas_repo(tmp_path, monkeypatch, record_property):
    """A failed journey files one bug on Dokima's repo, naming it and quoting what failed.

    Proves 258.8.
    Runs `main()` with the sandbox faked, BUG_REPO=dokima-dev/dokima and BUG_TOKEN set, and the split's stories never
    listed: file_bug() is asked once, for that journey, with its FAIL line, on dokima-dev/dokima with BUG_TOKEN. With
    every card right, no bug is filed. Then runs file_bug() against a fake gh: one issue is created on
    dokima-dev/dokima with BUG_TOKEN, its title naming the journey and its body quoting the FAIL line. Last,
    playthrough.yml hands the run BUG_REPO as the workflow's own repo and BUG_TOKEN as its own token, which may write
    issues."""
    record_property("proves", "258.8")
    p = playthrough("258.8")
    assert hasattr(p, "file_bug"), "258.8: dokima/playthrough.py has no file_bug(), so a failed journey files nothing"
    filed = []
    monkeypatch.setattr(p, "file_bug", lambda *args: filed.append(args))
    monkeypatch.setattr(p, "POLL", 0.01)
    for k, v in {"REPO": SANDBOX, "PLAYED": ROOT, "PLAYED_COMMIT": "abc1234", "SANDBOX_TOKEN": SANDBOX_TOKEN,
                 "BUG_REPO": "dokima-dev/dokima", "BUG_TOKEN": BUG_TOKEN, "PLAYTHROUGH_WAIT": "1"}.items():
        monkeypatch.setenv(k, v)
    for stale, want in (({(SPLIT, "stories filed")}, 1), ((), 0)):
        hub = NightSandbox(stale=stale)
        monkeypatch.setattr(p, "Sandbox", lambda *args, **kw: hub)
        filed.clear()
        code = p.main()
        assert code == want, f"258.8: main() should return {want} with stale cards {sorted(stale)}, not {code!r}"
        if not stale:
            assert filed == [], f"258.8: with every journey passing, no bug should be filed, yet {filed}"
            continue
        assert len(filed) == 1, f"258.8: one failed journey should file exactly one bug, not {filed}"
        repo, token, journey, said = filed[0]
        assert (repo, token) == ("dokima-dev/dokima", BUG_TOKEN), \
            f"258.8: the bug should be filed on dokima-dev/dokima with BUG_TOKEN, not on {repo!r} with {token!r}"
        assert journey == SPLIT, f"258.8: the bug should name the failed journey {SPLIT!r}, not {journey!r}"
        assert any(line.startswith("FAIL: ") and "stories filed" in line for line in said), \
            f"258.8: the bug should carry the journey's FAIL line for `stories filed`: {said}"
    monkeypatch.undo()
    p = playthrough("258.8")
    state, calls = fake_gh(tmp_path, monkeypatch, {"repo": "dokima-dev/dokima",
                                                   "issues": {"900": {"title": "An older issue", "state": "open"}},
                                                   "branches": ["main"]})
    monkeypatch.setenv("GH_TOKEN", APP_TOKEN)
    fail_line = f"FAIL: {SPLIT}: stories filed: the issue card showed Work with no stories"
    p.file_bug("dokima-dev/dokima", BUG_TOKEN, SPLIT, [f"PASS: {SPLIT}: issue opened", fail_line])
    made = [c for c in calls_of(calls) if c["argv"][:2] == ["issue", "create"]
            or (c["argv"][:1] == ["api"] and any(x.rstrip("/").endswith("repos/dokima-dev/dokima/issues") for x in c["argv"]))]
    assert len(made) == 1, f"258.8: file_bug() should create exactly one issue, not {[c['argv'] for c in calls_of(calls)]}"
    c = made[0]
    assert c["token"] == BUG_TOKEN, f"258.8: the bug was filed with {c['token']!r}, not BUG_TOKEN"
    new = json.loads(state.read_text())["issues"]
    title = next(it["title"] for n, it in new.items() if n != "900")
    assert SPLIT in title, f"258.8: the bug's title should name the journey {SPLIT!r}: {title!r}"
    text = " ".join(c["argv"]) + (c.get("body_file") or "")
    for i, x in enumerate(c["argv"]):
        if x.startswith("body=@") and os.path.isfile(x[6:]):
            text += open(x[6:]).read()
    assert fail_line in text, f"258.8: the bug's body should quote the FAIL line {fail_line!r}: {c['argv']}"
    wf = workflow("258.8")
    runs = [s for s in steps_of(wf) if "python3 -m dokima.playthrough" in str(s.get("run"))]
    assert runs, "258.8: no step runs `python3 -m dokima.playthrough`"
    for s in runs:
        job = next(j for j in wf["jobs"].values() if s in (j.get("steps") or []))
        env = {**(wf.get("env") or {}), **(job.get("env") or {}), **(s.get("env") or {})}
        assert str(env.get("BUG_REPO", "")).replace(" ", "") == "${{github.repository}}", \
            f"258.8: the run is not told to file bugs on its own repo: BUG_REPO is {env.get('BUG_REPO')!r}"
        assert str(env.get("BUG_TOKEN", "")).replace(" ", "") == "${{github.token}}", \
            f"258.8: the run is not handed its own token to file bugs: BUG_TOKEN is {env.get('BUG_TOKEN')!r}"
        perms = job.get("permissions") or wf.get("permissions") or {}
        assert isinstance(perms, dict) and perms.get("issues") == "write", \
            f"258.8: the run's own token may not write issues, so it cannot file a bug: {perms!r}"


def schedule_ctx():
    """The contexts GitHub gives a scheduled run on main."""
    return {"github": Ctx({"event_name": "schedule", "event": {}, "sha": MAIN_SHA, "ref": "refs/heads/main",
                           "repository": "dokima-dev/dokima", "workspace": "/w", "token": "t"}),
            "inputs": Ctx({}), "vars": Ctx({}), "secrets": Ctx({}), "steps": Ctx({}), "env": Ctx({}), "needs": Ctx({})}


def test_every_night_the_play_through_runs_on_mains_newest_commit(record_property):
    """Every night, the play-through starts on its own and plays main's newest commit.

    Proves 258.1.
    Reads playthrough.yml: it starts on a schedule with a cron line. Then evaluates it as GitHub does for a scheduled
    run on main: the job that runs `python3 -m dokima.playthrough` runs, the played commit's checkout checks out
    main's newest commit, and PLAYED_COMMIT names it."""
    record_property("proves", "258.1")
    wf = workflow("258.1")
    on = wf.get("on") or {}
    sched = on.get("schedule") if isinstance(on, dict) else None
    crons = [str((c or {}).get("cron", "")).strip() for c in (sched or []) if isinstance(c, dict)]
    assert any(len(c.split()) == 5 for c in crons), f"258.1: playthrough.yml starts on no schedule, so nothing plays nightly: {on!r}"
    ctx = schedule_ctx()
    runs = [s for s in steps_of(wf) if "python3 -m dokima.playthrough" in str(s.get("run"))]
    assert runs, "258.1: no step runs `python3 -m dokima.playthrough`"
    for s in runs:
        job = next(j for j in wf["jobs"].values() if s in (j.get("steps") or []))
        assert evaluate(condition(job.get("if")), ctx, {"failed": False}), \
            f"258.1: on a scheduled run the play-through's job is skipped: if {job.get('if')!r}"
        played = [c for c in job.get("steps") or [] if "actions/checkout" in str(c.get("uses"))
                  and (c.get("with") or {}).get("path")]
        assert played, "258.1: the play-through's job checks out no played commit into a folder of its own"
        for c in played:
            ref = fill(c["with"].get("ref", ""), ctx, {"failed": False})
            assert ref == MAIN_SHA, f"258.1: on a scheduled run the played checkout checks out {ref!r}, not main's newest commit"
        env = {**(wf.get("env") or {}), **(job.get("env") or {}), **(s.get("env") or {})}
        commit = fill(env.get("PLAYED_COMMIT", ""), ctx, {"failed": False})
        assert commit == MAIN_SHA, f"258.1: on a scheduled run PLAYED_COMMIT is {commit!r}, not main's newest commit"


def test_the_nightly_run_gates_nothing(record_property):
    """The nightly run starts on its schedule or by hand, never on a pull request.

    Proves 258.9.
    Reads playthrough.yml's triggers: a schedule must be among them (else there is no nightly run), and nothing
    but schedule and workflow_dispatch, so it never runs as a check on a pull request, the merge queue or a push, and
    no card's checks show it."""
    record_property("proves", "258.9")
    wf = workflow("258.9")
    on = wf.get("on") or {}
    triggers = set(on) if isinstance(on, dict) else {str(on)}
    assert "schedule" in triggers, f"258.9: playthrough.yml has no nightly schedule, so there is no nightly run: {sorted(triggers)}"
    extra = triggers - {"schedule", "workflow_dispatch"}
    assert not extra, f"258.9: the nightly run also starts on {sorted(extra)}, so it could gate a pull request or show on a card"

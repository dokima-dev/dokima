"""The reviewer settles raises between agents and confirms issues before code files them (#301).

Story 4 of #289. A worker's raise for the planner ("this test is broken") goes to the reviewer first. When the reviewer
answers it done, the planner starts with it as the reviewer's blocker; when the reviewer answers it disagree, the worker
starts again with the reviewer's why. Neither waits for the owner, and on autopilot neither merges the pull request.

An issue raise (a real problem outside this issue) becomes its own GitHub issue only once the reviewer confirms it: the
reviewer's own issue raises count as confirmed and are filed in its run, and its record says so; the planner's or the
worker's are listed for the reviewer's next run, filed when it answers done and never when it answers disagree, and
never in the planner's or worker's own run. Filing is done by `python3 -m dokima.agent next N OUT`, the step of
agent.yml that runs after the agent finished, holds the app's key and finishes the run's record (OUT/comment.md). An
issue GitHub refuses to file is named on the record with GitHub's reason, and the record and the river still stand.

The river tests call `agent.next_step` and `agent.raises_for` (what the pack writes to open_blockers.json) on records
built here. The filing tests run the real `agent next` as a subprocess against a fake GitHub: a `gh` program put first
on PATH that keeps its state in one JSON file and logs every call. It answers:
  - `gh issue view N [--json ...]`, `gh issue comment N --body/--body-file`, `gh pr list` (always none);
  - `gh issue create --title/-t T --body/-b B | --body-file/-F F [--label/-l L ...]`, printing the new issue's URL;
  - `gh issue list [...]` and `gh api repos/o/r/issues[?...]` (GET), listing every issue;
  - `gh api [-X POST] repos/o/r/issues -f title=.. -f body=.. [-f labels[]=..]` (or -F body=@file, or --input file),
    answering the new issue as GitHub's REST API does;
  - `gh api repos/o/r/issues/N` (GET), `gh api repos/o/r/issues/N/comments` (GET or POST body=),
    `gh api search/issues?...` (no hits), `gh api repos/o/r/labels[...]` and `gh label create`, which always succeed;
  - with "refuse" set in its state, every new issue is refused with that GitHub message on stderr and exit 1.
New issues are numbered from 500. Any other call fails, the way an unknown GitHub path does.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import agent, raises  # noqa: E402

N = 301
OWNER = "boss"
BOT = agent.BOT
REFUSED = "HTTP 502: Server Error (https://api.github.com/repos/o/r/issues)"

TEST_BROKEN = "The test for 301.1 reads a file that only exists on the planner's machine, so it can never pass."
TEST_EVIDENCE = "tests/test_x.py::test_a fails with FileNotFoundError: /home/planner/x.json"
WHY_NOT = "The file is made by the test's own fixture; the worker skipped the fixture."
WHY_YES = "The test opens an absolute path from the planner's machine; it cannot pass on CI."

FOUND = "The board ignores closed pull requests. Their cards stay in Review forever."
FOUND_TITLE = "The board ignores closed pull requests"
FOUND_EVIDENCE = "dokima/board.py asks only for OPEN pull requests"


# Records ---------------------------------------------------------------------------------------------------------------

def rec(role, stage, handback, run):
    """A record whose hand-back passed its check, the way `agent record` writes it."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{run}", "run_id": str(run)}


def plan_rec(raised=()):
    """The planner's plan for #301, with these stamped raises."""
    h = {"kind": "user_story", "summary": "Raises are settled.", "user_story": "The reviewer settles raises.",
         "acceptance_criteria": [{"text": "Raises are settled.", "source": f"https://github.com/o/r/issues/{N}"}],
         "non_functional": [], "scope": ["dokima/agent.py"], "out_of_scope": ["Prompts."], "tests": {},
         "test_changes": {}, "links": {"blocked_by": [], "blocks": [], "relates_to": []}, "raises": list(raised),
         "answers": []}
    return rec("planner", None, h, 1)


def plan_review_rec(answers=(), raised=()):
    """A plan review approving the plan, with these answers and raises."""
    return rec("reviewer", "plan", {"verdict": "approve", "summary": "Fine.", "raises": list(raised),
                                    "answers": list(answers)}, 2)


def work_rec(raised=()):
    """The worker's hand-back, with these stamped raises."""
    return rec("worker", "", {"summary": "Built it.", "criteria": {"301.1": "done"}, "evidence": "pytest -q: 1 failed",
                              "raises": list(raised), "answers": []}, 3)


def code_review_rec(verdict, answers=(), raised=(), run=4):
    """A code review of the pull request, with this verdict, these answers and these raises."""
    return rec("reviewer", "pr", {"verdict": verdict, "summary": "Reviewed.", "raises": list(raised),
                                  "answers": list(answers)}, run)


def worker_raise(rid="W1"):
    """The worker's raise for the planner: a test it judges broken, as code stamped it."""
    return {"kind": "blocker", "to": "planner", "label": "301.1", "text": TEST_BROKEN, "evidence": TEST_EVIDENCE,
            "raised_by": "worker", "id": rid}


def issue_raise(role, rid):
    """An issue raise, a problem outside #301, as code stamped it for this role."""
    return {"kind": "issue", "label": "Board", "text": FOUND, "evidence": FOUND_EVIDENCE, "raised_by": role, "id": rid}


def answer(rid, word, why):
    """An answer to a raise by its ID."""
    return {"raise": rid, "answer": word, "why": why}


def comment(r, i):
    """One comment holding a record, the way the bot posts it."""
    return {"author": {"login": BOT}, "body": f"{agent.MARK}\n**Record**\n\n```json\n{json.dumps(r)}\n```\n",
            "createdAt": f"2026-10-10T{i:02d}:00:00Z", "where": f"issue #{N}"}


def items_of(*recs):
    """The issue's conversation holding these records, oldest first."""
    return [comment(r, i) for i, r in enumerate(recs, 1)]


def step(earlier, newest, on=False):
    """What the river does after `newest`, with `earlier` already on the issue."""
    return agent.next_step(items_of(*earlier), newest, [OWNER], autopilot=lambda: on, number=str(N))


def listed(recs, role):
    """The open raises the pack lists for this role, as open_blockers.json gets them."""
    return agent.raises_for(recs, role)


# 301.1 -----------------------------------------------------------------------------------------------------------------

def test_a_worker_raise_for_the_planner_goes_to_the_reviewer_first(record_property):
    """A worker's raise for the planner reaches it only after the reviewer confirms it.

    The worker raises that a test is broken. The code review starts next, and its pack lists the raise for the
    reviewer, not for the planner. Once the review answers it done, the reviewer's pack no longer lists it and the
    planner's pack lists it as the reviewer's blocker for the planner, with the worker's words. Proves 301.1."""
    record_property("proves", "301.1")
    work = work_rec([worker_raise()])
    assert step([plan_rec(), plan_review_rec()], work)[:3] == ("start", "reviewer", "pr"), \
        "301.1: a worker's raise for the planner did not send the work to the code reviewer first"
    recs = [plan_rec(), plan_review_rec(), work]
    assert [r["id"] for r in listed(recs, "reviewer")] == ["W1"], \
        f"301.1: the reviewer's pack should list the worker's raise W1, lists {listed(recs, 'reviewer')}"
    assert listed(recs, "planner") == [], \
        f"301.1: the planner was handed a worker's raise the reviewer had not judged: {listed(recs, 'planner')}"
    review = code_review_rec("block", [answer("W1", "done", WHY_YES)])
    recs.append(review)
    assert listed(recs, "reviewer") == [], f"301.1: the reviewer is still asked to answer W1: {listed(recs, 'reviewer')}"
    mine = listed(recs, "planner")
    assert len(mine) == 1, f"301.1: the planner should start with exactly the confirmed raise, gets {mine}"
    r = mine[0]
    assert r.get("kind") == "blocker" and r.get("to") == "planner" and r.get("raised_by") == "reviewer", \
        f"301.1: the confirmed raise should reach the planner as the reviewer's blocker, reaches it as {r}"
    assert TEST_BROKEN in (r.get("text") or ""), f"301.1: the planner lost the worker's words: {r}"
    assert r.get("id"), f"301.1: the confirmed raise has no ID for the planner to answer: {r}"
    assert listed(recs, "worker") == [], f"301.1: the worker was handed the confirmed raise: {listed(recs, 'worker')}"


def test_a_confirmed_raise_starts_the_planner_even_when_the_code_is_approved(record_property):
    """A confirmed worker raise starts the planner, whatever the verdict on the code.

    The review answers the worker's raise done and approves the code, or blocks with a blocker of its own for the
    worker: in both cases the planner starts next, and nothing stops for the owner. Proves 301.1."""
    record_property("proves", "301.1")
    earlier = [plan_rec(), plan_review_rec(), work_rec([worker_raise()])]
    approve = code_review_rec("approve", [answer("W1", "done", WHY_YES)])
    assert step(earlier, approve)[:3] == ("start", "planner", ""), \
        f"301.1: an approving review that confirmed the worker's raise should start the planner, river says {step(earlier, approve)}"
    own = {"kind": "blocker", "to": "worker", "label": "301.2", "text": "The filing skips the evidence.",
           "raised_by": "reviewer", "id": "R1"}
    block = code_review_rec("block", [answer("W1", "done", WHY_YES)], [own])
    assert step(earlier, block)[:3] == ("start", "planner", ""), \
        f"301.1: a blocking review that confirmed the worker's raise should start the planner, river says {step(earlier, block)}"


def test_a_confirmed_raise_reaches_the_planner_beside_the_reviews_own_blocker_for_it(record_property):
    """A confirmed worker raise reaches the planner even when the review also blocks for it.

    The review answers the worker's raise done and raises a blocker of its own for the planner, once blocking and once
    approving. Each time the planner starts next and its pack lists both: the review's own blocker and the worker's
    raise as the reviewer's blocker, with the worker's words, under an ID of its own; the planner's hand-back is
    rejected unless it answers both. Proves 301.1."""
    record_property("proves", "301.1")
    earlier = [plan_rec(), plan_review_rec(), work_rec([worker_raise()])]
    own = {"kind": "blocker", "to": "planner", "label": "301.2", "text": "The second test proves a neighbour of the promise.",
           "raised_by": "reviewer", "id": "R1"}
    for verdict in ("block", "approve"):
        review = code_review_rec(verdict, [answer("W1", "done", WHY_YES)], [own])
        assert step(earlier, review)[:3] == ("start", "planner", ""), \
            f"301.1: a {verdict} review confirming the worker's raise and blocking for the planner should start the planner, river says {step(earlier, review)}"
        mine = listed(earlier + [review], "planner")
        ids = [r.get("id") for r in mine]
        assert "R1" in ids, f"301.1: the planner lost the review's own blocker R1 ({verdict} review): {mine}"
        passed_on = [r for r in mine if r.get("id") != "R1"]
        assert len(passed_on) == 1, \
            f"301.1: the planner should get the confirmed worker raise beside the review's own blocker ({verdict} review), gets {mine}"
        r = passed_on[0]
        assert r.get("kind") == "blocker" and r.get("to") == "planner" and r.get("raised_by") == "reviewer" \
            and TEST_BROKEN in (r.get("text") or "") and r.get("id") and r.get("id") != "W1", \
            f"301.1: the confirmed raise should reach the planner as the reviewer's blocker with the worker's words, reaches it as {r}"
        skipped = raises.check_answers("planner", [answer("R1", "done", "Fixed the second test.")], mine)
        assert any(r["id"] in p for p in skipped), \
            f"301.1: a planner hand-back answering only R1 was not rejected for skipping {r['id']}: {skipped}"
        assert listed(earlier + [review], "worker") == [], \
            f"301.1: the worker was handed a raise meant for the planner: {listed(earlier + [review], 'worker')}"


def test_the_planner_must_answer_the_confirmed_raise_and_answering_closes_it(record_property):
    """The planner must answer the confirmed raise, and once it does, nobody is asked again.

    Code rejects a planner hand-back that skips the confirmed raise, accepts one that answers it, and after that
    answer no one's pack lists it. Proves 301.1."""
    record_property("proves", "301.1")
    recs = [plan_rec(), plan_review_rec(), work_rec([worker_raise()]),
            code_review_rec("block", [answer("W1", "done", WHY_YES)])]
    mine = listed(recs, "planner")
    assert len(mine) == 1, f"301.1: the planner should be handed the confirmed raise, gets {mine}"
    rid = mine[0]["id"]
    skipped = raises.check_answers("planner", [], mine)
    assert any(rid in p for p in skipped), f"301.1: a planner hand-back skipping {rid} was not rejected: {skipped}"
    ok = [answer(rid, "done", "The test now builds its file in a temp folder.")]
    assert raises.check_answers("planner", ok, mine) == [], \
        f"301.1: a planner hand-back answering {rid} was rejected: {raises.check_answers('planner', ok, mine)}"
    replan = plan_rec()
    replan["handback"]["answers"] = ok
    after = recs + [replan]
    for role in ("planner", "reviewer", "worker"):
        assert listed(after, role) == [], f"301.1: after the planner answered {rid}, the {role} still gets {listed(after, role)}"


def test_a_raise_the_reviewer_disagrees_with_sends_the_worker_back_with_the_why(record_property):
    """A raise the reviewer disagrees with sends the worker back with the why.

    The review answers the worker's raise disagree: the worker starts next, its pack lists the reviewer's why, the
    planner's pack lists nothing, and nothing stops for the owner. This holds when the review approves the code and
    when it blocks with a blocker of its own for the worker. Proves 301.1."""
    record_property("proves", "301.1")
    earlier = [plan_rec(), plan_review_rec(), work_rec([worker_raise()])]
    own = {"kind": "blocker", "to": "worker", "label": "301.2", "text": "Run the fixture before the test.",
           "raised_by": "reviewer", "id": "R1"}
    for review in (code_review_rec("approve", [answer("W1", "disagree", WHY_NOT)]),
                   code_review_rec("block", [answer("W1", "disagree", WHY_NOT)], [own])):
        verdict = review["handback"]["verdict"]
        assert step(earlier, review)[:3] == ("start", "worker", ""), \
            f"301.1: the {verdict} review that disagreed with the worker's raise should start the worker, river says {step(earlier, review)}"
        recs = earlier + [review]
        texts = " ".join(str(r.get("text") or "") for r in listed(recs, "worker"))
        assert WHY_NOT in texts, \
            f"301.1: the worker starts again without the reviewer's why ({verdict} review); its pack lists {listed(recs, 'worker')}"
        assert listed(recs, "planner") == [], \
            f"301.1: the planner was handed a raise the reviewer disagreed with: {listed(recs, 'planner')}"


# The fake GitHub -------------------------------------------------------------------------------------------------------

FAKE_GH = r'''
import json, os, re, sys
D = os.environ["FAKE_GH_DIR"]
STATE = os.path.join(D, "state.json")
S = json.load(open(STATE))
a = sys.argv[1:]
S.setdefault("calls", []).append(a)
WITH_VALUE = {"-X", "--method", "-f", "-F", "--raw-field", "--field", "-H", "--header", "--input", "-q", "--jq",
              "-R", "--repo", "--json", "--body", "-b", "--body-file", "--head", "--state", "-s", "--title", "-t",
              "--label", "-l", "--template", "--search", "-S", "--limit", "-L", "--color", "--description", "-d",
              "-c", "--assignee", "-a"}


def save():
    json.dump(S, open(STATE, "w"), indent=1)


def flag(*names):
    for i, x in enumerate(a):
        if x in names and i + 1 < len(a):
            return a[i + 1]
    return None


def flags(*names):
    return [a[i + 1] for i, x in enumerate(a[:-1]) if x in names]


def fields():
    out = {}
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--raw-field", "--field") and i + 1 < len(a):
            k, _, v = a[i + 1].partition("=")
            if x in ("-F", "--field") and v.startswith("@"):
                v = sys.stdin.read() if v == "@-" else open(v[1:]).read()
            if k.endswith("[]"):
                out.setdefault(k[:-2], []).append(v)
            else:
                out[k] = v
    p = flag("--input")
    if p:
        out.update(json.load(sys.stdin if p == "-" else open(p)))
    return out


def positional():
    out, skip = [], False
    for x in a[1:]:
        if skip:
            skip = False
            continue
        if x in WITH_VALUE:
            skip = True
            continue
        if x.startswith("-"):
            continue
        out.append(x)
    return out


def fail(msg):
    S.setdefault("failed", []).append(a)
    save()
    sys.stderr.write(msg + "\n")
    sys.exit(1)


def issue(n):
    i = S["issues"].get(str(n))
    if i is None:
        fail(f"HTTP 404: Not Found (https://api.github.com/repos/o/r/issues/{n})")
    return i


def obj(n):
    i = issue(n)
    return {"number": int(n), "id": 900000 + int(n), "node_id": f"I_{n}", "title": i["title"], "body": i["body"],
            "state": i.get("state", "open"), "labels": [{"name": l} for l in i.get("labels", [])],
            "html_url": f"https://github.com/o/r/issues/{n}", "url": f"https://github.com/o/r/issues/{n}"}


def out(value):
    q = flag("-q", "--jq")
    if q:
        for name, idx in re.findall(r"\.(\w+)|\[(\d+)\]", q):
            try:
                value = value[int(idx)] if idx else value[name]
            except (KeyError, IndexError, TypeError):
                value = None
                break
        print("" if value is None else value if isinstance(value, (str, int)) else json.dumps(value))
    else:
        print(value if isinstance(value, str) else json.dumps(value))
    save()
    sys.exit(0)


def new_issue(title, text, labels):
    if S.get("refuse"):
        fail(S["refuse"])
    n = 500 + len(S["created"])
    S["issues"][str(n)] = {"title": title or "", "body": text or "", "labels": list(labels), "comments": []}
    S["created"].append(n)
    return n


def number(x):
    return int(str(x).rstrip("/").rsplit("/", 1)[-1].lstrip("#"))


def text_arg(body_flags, file_flags):
    text = flag(*body_flags)
    if text is None:
        p = flag(*file_flags)
        if p is not None:
            text = sys.stdin.read() if p == "-" else open(p).read()
    return text


if a[:2] == ["issue", "view"]:
    n = number(a[2])
    o = obj(n)
    o["comments"] = issue(n).get("comments", [])
    out(o)
if a[:2] == ["issue", "comment"]:
    n = number(a[2])
    issue(n).setdefault("comments", []).append({"author": {"login": BOT_LOGIN}, "body": text_arg(("--body", "-b"), ("--body-file", "-F")),
                                                "createdAt": "2026-10-10T23:59:00Z"})
    save()
    sys.exit(0)
if a[:2] == ["issue", "create"]:
    labels = [l.strip() for v in flags("--label", "-l") for l in v.split(",") if l.strip()]
    n = new_issue(flag("--title", "-t"), text_arg(("--body", "-b"), ("--body-file", "-F")), labels)
    print(f"https://github.com/o/r/issues/{n}")
    save()
    sys.exit(0)
if a[:2] == ["issue", "list"]:
    out([{**obj(k), "url": obj(k)["html_url"], "state": obj(k)["state"].upper()} for k in sorted(S["issues"], key=int)])
if a[:2] == ["label", "create"]:
    save()
    sys.exit(0)
if a[:2] == ["pr", "list"]:
    out([])
if a[:1] == ["api"]:
    pos = positional()
    path = (pos[0] if pos else "").lstrip("/")
    route = path.split("?", 1)[0]
    f = fields()
    method = (flag("-X", "--method") or ("POST" if f and route != "graphql" else "GET")).upper()
    if route == "repos/o/r/issues" and method == "POST":
        labels = [l["name"] if isinstance(l, dict) else l for l in f.get("labels") or []]
        out(obj(new_issue(f.get("title"), f.get("body"), labels)))
    if route == "repos/o/r/issues" and method == "GET":
        out([obj(int(k)) for k in sorted(S["issues"], key=int)])
    m = re.fullmatch(r"repos/o/r/issues/(\d+)", route)
    if m and method == "GET":
        out(obj(int(m.group(1))))
    m = re.fullmatch(r"repos/o/r/issues/(\d+)/comments", route)
    if m:
        n = int(m.group(1))
        if method == "POST":
            issue(n).setdefault("comments", []).append({"author": {"login": BOT_LOGIN}, "body": f.get("body", ""),
                                                        "createdAt": "2026-10-10T23:59:00Z"})
            out({"id": 1, "body": f.get("body", "")})
        out(issue(n).get("comments", []))
    if route == "search/issues":
        out({"total_count": 0, "items": []})
    if route.startswith("repos/o/r/labels"):
        out([] if method == "GET" and route == "repos/o/r/labels" else {"name": route.rsplit("/", 1)[-1]})
fail(f"fake gh: no such call {a}")
'''


class Hub:
    """A fake GitHub holding issue #301, and `agent next` run against it."""

    def __init__(self, tmp, autopilot=False, refuse=None):
        self.dir = str(tmp)
        bin_dir = os.path.join(self.dir, "bin")
        os.makedirs(bin_dir)
        gh = os.path.join(bin_dir, "gh")
        open(gh, "w").write(f"#!{sys.executable}\nBOT_LOGIN = {BOT!r}\n" + FAKE_GH)
        os.chmod(gh, 0o755)
        state = {"issues": {str(N): {"title": "The reviewer settles raises", "body": "The owner's ask.",
                                     "labels": ["autopilot"] if autopilot else [], "comments": []}},
                 "created": [], "refuse": refuse}
        json.dump(state, open(os.path.join(self.dir, "state.json"), "w"))
        self.recs = []
        self.env = {**os.environ, "PATH": bin_dir + os.pathsep + os.environ.get("PATH", ""), "FAKE_GH_DIR": self.dir,
                    "GITHUB_REPOSITORY": "o/r", "OWNERS": OWNER, "GH_TOKEN": "fake",
                    "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "9"}
        for k in ("DOKIMA_BOARD", "ISSUE_NUMBER", "PACK", "STAGE", "ROLE"):
            self.env.pop(k, None)

    def state(self):
        """The fake GitHub's state, as the commands left it."""
        return json.load(open(os.path.join(self.dir, "state.json")))

    def post(self, r):
        """Put a record on #301's conversation, as the workflow posts it after the river decided."""
        s = self.state()
        comments = s["issues"][str(N)]["comments"]
        comments.append({k: v for k, v in comment(r, len(comments) + 1).items() if k != "where"})
        json.dump(s, open(os.path.join(self.dir, "state.json"), "w"))
        self.recs.append(r)

    def next(self, r):
        """Run `agent next 301 OUT` on this record, as agent.yml does.

        Returns the river's word and OUT/comment.md once the command finished."""
        out = os.path.join(self.dir, f"out{len(os.listdir(self.dir))}")
        os.makedirs(out)
        json.dump(r, open(os.path.join(out, "record.json"), "w"))
        open(os.path.join(out, "comment.md"), "w").write(agent.render(r, earlier=list(self.recs)))
        p = subprocess.run([sys.executable, "-m", "dokima.agent", "next", str(N), out], cwd=ROOT, env=self.env,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, f"test setup: `agent next` crashed: {p.stderr[-2000:]}"
        said = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
        return said, open(os.path.join(out, "comment.md")).read()

    def run(self, r):
        """`agent next` on this record, then the record goes up on the issue."""
        said = self.next(r)
        self.post(r)
        return said

    def created(self):
        """Every issue the commands filed on GitHub, as {number: issue}."""
        s = self.state()
        return {n: s["issues"][str(n)] for n in s["created"]}

    def merges(self):
        """Every call that tried to merge a pull request."""
        return [c for c in self.state()["calls"] if c[:2] == ["pr", "merge"] or any("/merge" in str(x) for x in c)]


def filed_lines(text, n):
    """The lines of a record that name the filed issue #n."""
    return [l for l in text.splitlines() if re.search(rf"(?:#|/issues/){n}\b", l)]


def test_on_autopilot_a_settled_raise_neither_merges_nor_waits_for_the_owner(tmp_path, record_property):
    """On autopilot, a settled worker raise starts the next agent and merges nothing.

    The issue is on autopilot. The worker raises that a test is broken; the code review approves the code and answers
    the raise done: `agent next` starts the planner. On a second issue the review answers disagree: it starts the
    worker. Neither tries to merge the pull request, and neither card mentions the owner. Proves 301.1."""
    record_property("proves", "301.1")
    for word, why, who in (("done", WHY_YES, "planner"), ("disagree", WHY_NOT, "worker")):
        hub = Hub(tmp_path / word, autopilot=True)
        for r in (plan_rec(), plan_review_rec(), work_rec([worker_raise()])):
            hub.post(r)
        said, text = hub.run(code_review_rec("approve", [answer("W1", word, why)]))
        assert said == f"start {who}", \
            f"301.1: on autopilot, a review answering the worker's raise {word} should start the {who}, river said {said!r}"
        assert hub.merges() == [], f"301.1: a review answering the worker's raise {word} tried to merge: {hub.merges()}"
        assert f"@{OWNER}" not in text.rsplit("**Next:**", 1)[-1], \
            f"301.1: the card waits for the owner after the reviewer answered {word}: {text.rsplit('**Next:**', 1)[-1]!r}"


# 301.2 -----------------------------------------------------------------------------------------------------------------

def test_the_reviewers_own_issue_raise_is_filed_in_its_run_and_its_card_says_so(tmp_path, record_property):
    """The reviewer's own issue raise is filed in its run, and its card says so.

    A code review raises one issue outside #301. Its `agent next` files exactly one new issue, titled with the raise's
    first sentence, whose body holds the raise's words and evidence and names #301, where it was found. The review's
    record names the new issue by its number and says the reviewer confirmed it. Proves 301.2."""
    record_property("proves", "301.2")
    hub = Hub(tmp_path)
    for r in (plan_rec(), plan_review_rec(), work_rec()):
        hub.post(r)
    own = {"kind": "blocker", "to": "worker", "label": "301.1", "text": "Route the why.", "raised_by": "reviewer",
           "id": "R1"}
    said, text = hub.run(code_review_rec("block", raised=[own, issue_raise("reviewer", "R2")]))
    created = hub.created()
    assert len(created) == 1, f"301.2: the reviewer's one issue raise should file exactly one issue, filed {created}"
    (n, filed), = created.items()
    assert filed["title"].strip().rstrip(".") == FOUND_TITLE, \
        f"301.2: the filed issue should be titled {FOUND_TITLE!r}, is titled {filed['title']!r}"
    for part, what in ((FOUND, "the raise's words"), (FOUND_EVIDENCE, "its evidence")):
        assert part in filed["body"], f"301.2: the filed issue's body lacks {what}: {filed['body']!r}"
    assert re.search(rf"#{N}\b|/issues/{N}\b", filed["body"]), \
        f"301.2: the filed issue does not say it was found on #{N}: {filed['body']!r}"
    lines = filed_lines(text, n)
    assert lines, f"301.2: the reviewer's record does not name the filed issue #{n}:\n{text}"
    assert any("confirmed" in l.lower() for l in lines), \
        f"301.2: the reviewer's record names #{n} but does not say the reviewer confirmed it: {lines}"
    assert said == "start worker", f"301.2: filing changed what the river does next: {said!r}"


def test_a_planner_or_worker_issue_raise_waits_for_the_reviewer(tmp_path, record_property):
    """A planner's or worker's issue raise is never filed in its own run.

    The planner raises an issue: its `agent next` files nothing, and the plan reviewer's pack lists the raise, which
    code rejects a review for skipping. The same holds for an issue the worker raises and the code reviewer. Proves 301.2."""
    record_property("proves", "301.2")
    hub = Hub(tmp_path)
    planner = plan_rec([issue_raise("planner", "P1")])
    hub.run(planner)
    assert hub.created() == {}, f"301.2: the planner's issue was filed in its own run: {hub.created()}"
    mine = listed([planner], "reviewer")
    assert [r["id"] for r in mine] == ["P1"], f"301.2: the plan reviewer's pack should list the planner's issue P1, lists {mine}"
    skipped = raises.check_answers("reviewer", [], mine)
    assert any("P1" in p for p in skipped), f"301.2: a review that skips the planner's issue P1 was not rejected: {skipped}"
    review = plan_review_rec([answer("P1", "disagree", "Closed pull requests are dropped on purpose.")])
    hub.run(review)
    worker = work_rec([issue_raise("worker", "W1")])
    hub.run(worker)
    assert hub.created() == {}, f"301.2: the worker's issue was filed in its own run: {hub.created()}"
    mine = listed([planner, review, worker], "reviewer")
    assert [r["id"] for r in mine] == ["W1"], f"301.2: the code reviewer's pack should list the worker's issue W1, lists {mine}"
    skipped = raises.check_answers("reviewer", [], mine)
    assert any("W1" in p for p in skipped), f"301.2: a review that skips the worker's issue W1 was not rejected: {skipped}"


def test_an_issue_raise_the_reviewer_answers_done_is_filed_and_disagree_is_not(tmp_path, record_property):
    """An issue raise is filed when the reviewer answers done, never when it disagrees.

    The planner raises an issue; the plan review answers it disagree: nothing is filed and the review's card names no
    filed issue. The worker raises the same kind of issue; the code review answers it done: exactly one issue is
    filed, with the raise's words and evidence, and the code review's card names it by its number. Proves 301.2."""
    record_property("proves", "301.2")
    hub = Hub(tmp_path)
    hub.run(plan_rec([issue_raise("planner", "P1")]))
    _, text = hub.run(plan_review_rec([answer("P1", "disagree", "Closed pull requests are dropped on purpose.")]))
    assert hub.created() == {}, f"301.2: an issue the reviewer disagreed with was filed: {hub.created()}"
    assert not filed_lines(text, 500), f"301.2: the review's card names an issue it did not file: {filed_lines(text, 500)}"
    hub.run(work_rec([issue_raise("worker", "W1")]))
    _, text = hub.run(code_review_rec("block", [answer("W1", "done", "Real: closed PRs stay in Review.")],
                                      [{"kind": "blocker", "to": "worker", "text": "Finish 301.2.",
                                        "raised_by": "reviewer", "id": "R1"}]))
    created = hub.created()
    assert len(created) == 1, f"301.2: the worker's issue the reviewer confirmed should file exactly one issue, filed {created}"
    (n, filed), = created.items()
    assert FOUND in filed["body"] and FOUND_EVIDENCE in filed["body"], \
        f"301.2: the filed issue lacks the raise's words or evidence: {filed['body']!r}"
    assert filed_lines(text, n), f"301.2: the code review's card does not name the filed issue #{n}:\n{text}"


def test_a_plan_reviewer_confirming_the_planners_issue_files_it(tmp_path, record_property):
    """An issue the planner raised is filed when the plan reviewer answers it done.

    The planner raises an issue and the plan review answers it done: exactly one issue is filed, titled with the
    raise's first sentence, and the plan review's card names it. Proves 301.2."""
    record_property("proves", "301.2")
    hub = Hub(tmp_path)
    hub.run(plan_rec([issue_raise("planner", "P1")]))
    review = plan_review_rec([answer("P1", "done", "Real: closed PRs stay in Review.")])
    review["handback"]["verdict"] = "block"
    review["handback"]["raises"] = [{"kind": "blocker", "to": "planner", "text": "Add a test.", "raised_by": "reviewer",
                                     "id": "R1"}]
    _, text = hub.run(review)
    created = hub.created()
    assert len(created) == 1, f"301.2: the planner's issue the reviewer confirmed should file exactly one issue, filed {created}"
    (n, filed), = created.items()
    assert filed["title"].strip().rstrip(".") == FOUND_TITLE, f"301.2: the filed issue is titled {filed['title']!r}"
    assert filed_lines(text, n), f"301.2: the plan review's card does not name the filed issue #{n}:\n{text}"


# 301.3 -----------------------------------------------------------------------------------------------------------------

def test_an_issue_github_refuses_to_file_says_why_and_the_record_stands(tmp_path, record_property):
    """A refused filing says why on the issue, and the record and river still stand.

    GitHub refuses every new issue. A code review raises an issue: `agent next` still finishes, the record still holds
    its full JSON and its Next line, the river still starts the worker, and the record (or a comment on #301) names
    the finding and GitHub's reason. Proves 301.3."""
    record_property("proves", "301.3")
    hub = Hub(tmp_path, refuse=REFUSED)
    for r in (plan_rec(), plan_review_rec(), work_rec()):
        hub.post(r)
    own = {"kind": "blocker", "to": "worker", "text": "Finish 301.2.", "raised_by": "reviewer", "id": "R1"}
    said, text = hub.next(code_review_rec("block", raised=[own, issue_raise("reviewer", "R2")]))
    assert hub.created() == {}, "test setup: the fake GitHub filed an issue it was told to refuse"
    assert said == "start worker", f"301.3: a refused filing changed what the river does next: {said!r}"
    assert agent.MARK in text and "Full record" in text and "**Next:**" in text, \
        f"301.3: the run's record lost its full record or Next line when filing failed:\n{text}"
    said_on_issue = [c["body"] for c in hub.state()["issues"][str(N)]["comments"]]
    where = [t for t in [text] + said_on_issue if REFUSED in t and FOUND_TITLE in t]
    assert where, f"301.3: neither the record nor a comment on #{N} names the finding with GitHub's reason {REFUSED!r}"

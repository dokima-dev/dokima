"""A hotfix issue is built from its text, then reviewed and gated as usual (#863).

These tests run the agent workflow (.github/workflows/agent.yml) the way GitHub runs it, on the machine from
test_start.py, with the fake GitHub of test_autopilot_close.py (labels, sub-issues, blocked-by links, comments,
signals). A thin layer in front of that fake also answers what a hotfix's run needs: `gh pr create` (noted, and the
pull request #60 exists from then on), `gh run download` (a session log of the worker's run), the merge gate's reads
of pull request #60 (its head commit, its draft flag, `gh pr ready`), main's branch rule (it requires the `all tests`
check) and the check runs on the head commit (green, or red when the test asks). A `--jq` filter on an issue read is applied with jq.

The issue is #57 in repo o/r, labeled `hotfix`, its text the owner's ask: ASK. Main holds app.py (the title with a
typo), lib/ (nothing yet) and an older test, tests/test_old.py. The stand-in agent keeps a copy of its pack and its
prompt as it found them. As the worker it fixes app.py, adds lib/title.py, adds tests/test_app.py, changes
tests/test_old.py, and hands back a work.json whose one line is keyed `ask` (a hotfix has no plan to number its
criteria, so only the shape of its work.json is checked). As the code reviewer it hands back the review the test
chose: an approval, or a block raising a blocker for the planner because the change is bigger than the ask.

The autopilot test runs the close and command workflows on test_autopilot_close.py's machine, as its own tests do.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_autopilot_close as tac  # noqa: E402
import test_start as ts  # noqa: E402
from dokima import agent, agent_github, checks  # noqa: E402
from dokima.agent_records import GATE_FAILED  # noqa: E402

HOTFIX = "hotfix"
ISSUE = int(ts.N)
ASK = "The page title says Dokma; make it say Dokima."
HEAD = "ab" * 20
TOO_BIG = "The change rewrites the title module too, which is bigger than the one-line ask."

MAIN_FILES = {
    "app.py": '"""The app\'s page title."""\nTITLE = "Dokma"\n',
    "lib/__init__.py": '"""Helpers."""\n',
    "tests/test_old.py": '"""An older test."""\n\n\ndef test_old():\n    """An older check."""\n    assert True\n',
}
FIXED_APP = '"""The app\'s page title."""\nTITLE = "Dokima"\n'
NEW_LIB = '"""The title, in one place."""\nNAME = "Dokima"\n'
NEW_TEST = ('"""The title is spelled right."""\nimport os\nimport sys\n\n'
            'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\n\n'
            'def test_title():\n    """The title reads Dokima."""\n    import app\n    assert app.TITLE == "Dokima"\n')
CHANGED_OLD = '"""An older test."""\n\n\ndef test_old():\n    """An older check, now pinning the fix."""\n    assert 1 + 1 == 2\n'
WORK = {"summary": "Fixed the page title.", "criteria": {"ask": "`app.py` now says Dokima."},
        "evidence": "pytest -q: 2 passed", "raises": [], "answers": []}
APPROVE = {"previous_step": {"did": ["Fixed the page title in one file."], "decided": [], "open": []},
           "stage": "pr", "round": 1, "verdict": "approve", "summary": "The fix does exactly what the issue asks.",
           "raises": [], "answers": []}
BLOCK = {**APPROVE, "verdict": "block", "summary": "The change is bigger than the ask.",
         "raises": [{"kind": "blocker", "to": "planner", "label": "Bigger than the ask", "text": TOO_BIG,
                     "evidence": "`diff.patch` changes `app.py` and adds `lib/title.py`."}]}

GH = r'''#!/usr/bin/env python3
"""What a hotfix's run needs from GitHub beyond the issue tree fake (gh-inner), which answers everything else."""
import json, os, re, subprocess, sys
d = os.environ["FAKE_GH_DIR"]
a = sys.argv[1:]
inner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gh-inner")
HEAD = "%(head)s"
def flag(*names):
    for name in names:
        if name in a and a.index(name) + 1 < len(a):
            return a[a.index(name) + 1]
    return None
def noted():
    open(os.path.join(d, "calls.jsonl"), "a").write(json.dumps(a) + "\n")
api = next((x.lstrip("/") for x in a[1:] if x.lstrip("/").startswith("repos/o/r/")), "") if a[:1] == ["api"] else ""
path = api.split("?")[0]
if a[:2] == ["pr", "create"]:
    noted()
    opts_file = os.path.join(d, "options.json")
    opts = json.load(open(opts_file)) if os.path.exists(opts_file) else {}
    opts["pr_open"] = True
    json.dump(opts, open(opts_file, "w"))
    print("https://github.com/o/r/pull/60")
    sys.exit(0)
if a[:2] == ["run", "download"]:
    noted()
    dest = flag("-D", "--dir")
    os.makedirs(os.path.join(dest, "p"), exist_ok=True)
    open(os.path.join(dest, "p", "s.jsonl"), "w").write(json.dumps({"message": {"role": "assistant", "content": "Built it."}}) + "\n")
    sys.exit(0)
if a[:2] == ["pr", "view"] and flag("--json") in ("headRefOid", "isDraft"):
    noted()
    print(HEAD if flag("--json") == "headRefOid" else "true")
    sys.exit(0)
if a[:2] == ["pr", "ready"]:
    noted()
    sys.exit(0)
if re.fullmatch(r"repos/o/r/branches/[^/]+", path):
    noted()
    print(json.dumps({"name": "main", "protection": {"required_status_checks": {"contexts": ["all tests"]}}}))
    sys.exit(0)
if re.fullmatch(r"repos/o/r/commits/[0-9a-f]+/check-runs", path):
    noted()
    opts_file = os.path.join(d, "options.json")
    conclusion = (json.load(open(opts_file)) if os.path.exists(opts_file) else {}).get("checks", "success")
    print(json.dumps({"check_runs": [{"name": "all tests", "status": "completed", "conclusion": conclusion}]}))
    sys.exit(0)
if re.fullmatch(r"repos/o/r/commits/[0-9a-f]+/status", path):
    noted()
    print(json.dumps({"statuses": []}))
    sys.exit(0)
q = flag("-q", "--jq")
if q and not re.fullmatch(r"\.[A-Za-z_]+", q.strip()) and (a[:2] == ["issue", "view"] or re.fullmatch(r"repos/o/r/issues/\d+(/labels)?", path)):
    rest = [x for i, x in enumerate(a) if x not in ("-q", "--jq") and (i == 0 or a[i - 1] not in ("-q", "--jq"))]
    p = subprocess.run([sys.executable, inner] + rest, capture_output=True, text=True)
    sys.stderr.write(p.stderr)
    if p.returncode:
        sys.exit(p.returncode)
    j = subprocess.run(["jq", "-r", q], input=p.stdout, capture_output=True, text=True)
    sys.stdout.write("\n".join("" if l == "null" else l for l in j.stdout.splitlines()) + ("\n" if j.stdout else ""))
    sys.exit(j.returncode)
os.execv(sys.executable, [sys.executable, inner] + a)
''' % {"head": HEAD}

CLAUDE = r'''#!/usr/bin/env python3
"""A stand-in agent: keeps its pack and prompt as it found them, then works (worker) or hands back the review."""
import json, os, shutil, sys
d = os.environ["FAKE_GH_DIR"]
shutil.copytree(os.environ["PACK"], os.path.join(d, "pack-at-start"), dirs_exist_ok=True)
argv = sys.argv[1:]
open(os.path.join(d, "prompt.md"), "w").write(argv[argv.index("-p") + 1] if "-p" in argv[:-1] else "")
out = os.environ["OUT"]
if os.environ.get("ROLE") == "worker":
    files = json.load(open(os.path.join(d, "worker-files.json")))
    for p, text in files.items():
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        open(p, "w").write(text)
    shutil.copy(os.path.join(d, "work.json"), os.path.join(out, "work.json"))
else:
    shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(out, "review.json"))
model = argv[argv.index("--model") + 1] if "--model" in argv[:-1] else os.environ.get("MODEL", "")
logs = os.path.join(os.environ["HOME"], ".claude", "projects", "p")
os.makedirs(logs, exist_ok=True)
open(os.path.join(logs, "s.jsonl"), "w").write(json.dumps({"message": {"model": model, "role": "assistant", "content": "Done."}}) + "\n")
open(os.environ["FAKE_CLAUDE_MARK"], "w").write("started")
print(json.dumps({"num_turns": 1, "duration_ms": 1000, "usage": {}}))
'''


def worker_record():
    """A passed worker record for the hotfix, the way the workflow writes one."""
    return {"role": "worker", "stage": None, "run_id": "3", "run": "https://github.com/o/r/actions/runs/3",
            "models": ["claude-opus-5-5"], "handback": WORK, "check": {"passed": True, "problems": []}}


class Hotfix(ts.Machine):
    """One whole run of agent.yml on #57 for ROLE at STAGE, the issue carrying `labels`.

    With `built`, try/issue-57 already holds the worker's fix and pull request #60 is open, as when code review starts.
    With `try_branch`, the branch holds test_start's planner test, as for an approved plan. `checks` is the conclusion
    GitHub gives the required check on the pull request's head commit."""

    def __init__(self, tmp, role, stage="", labels=(HOTFIX,), comments=(), review=None, built=False, try_branch=False,
                 checks="success"):
        """Set up the repo, the fakes and the issue, then run the job."""
        options = {"pr_open": True, "checks": checks} if built else {"checks": checks}
        super().__init__(tmp, list(comments), options=options, files=MAIN_FILES)
        t, src = self.tmp, f"{self.tmp}/src"
        os.rename(f"{t}/bin/gh", f"{t}/bin/gh-unused")
        open(f"{t}/bin/gh-inner", "w").write(tac.fake_gh())
        open(f"{t}/bin/gh", "w").write(GH.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
        open(f"{t}/bin/claude", "w").write(CLAUDE.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
        for name in ("gh", "gh-inner", "claude"):
            os.chmod(f"{t}/bin/{name}", 0o755)
        issue = json.load(open(f"{t}/gh/issue.json"))
        json.dump({**issue, "title": "Page title typo", "body": ASK}, open(f"{t}/gh/issue.json", "w"))
        for name, value in (("tree.json", {}), ("deps.json", {}), ("states.json", {}),
                            ("labels.json", {str(ISSUE): list(labels)})):
            json.dump(value, open(f"{t}/gh/{name}", "w"))
        json.dump({"app.py": FIXED_APP, "lib/title.py": NEW_LIB, "tests/test_app.py": NEW_TEST,
                   "tests/test_old.py": CHANGED_OLD}, open(f"{t}/gh/worker-files.json", "w"))
        json.dump(WORK, open(f"{t}/gh/work.json", "w"))
        if review is not None:
            json.dump(review, open(f"{t}/review.json", "w"))
        if built or try_branch:
            ts.sh(src, "git", "checkout", "-q", "-B", f"try/issue-{ts.N}")
            done = (("app.py", FIXED_APP), ("lib/title.py", NEW_LIB), ("tests/test_app.py", NEW_TEST)) if built else \
                (("tests/test_x.py", 'def test_a():\n    """A."""\n'),)
            for p, text in done:
                open(f"{src}/{p}", "w").write(text)
            ts.sh(src, "git", "add", "-A")
            ts.sh(src, "git", "commit", "-qm", "worker for #57" if built else "tests")
            ts.sh(src, "git", "push", "-q", "origin", f"try/issue-{ts.N}")
            ts.sh(src, "git", "checkout", "-q", "main")
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": role, "stage": stage, "issue": ts.N}}))
        ctx = {"inputs": ts.Ctx(role=role, stage=stage, issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42",
                                run_attempt="1", server_url="https://github.com", repository="o/r",
                                token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        wf = ts.workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        self.failed = self.result == "failure"

    def pack_file(self, name):
        """A pack file as the agent found it at its start, or None when absent."""
        path = f"{self.tmp}/gh/pack-at-start/{name}"
        return open(path).read() if os.path.isfile(path) else None

    def prompt(self):
        """The prompt the agent was started with, or '' when it never started."""
        path = f"{self.tmp}/gh/prompt.md"
        return open(path).read() if os.path.exists(path) else ""

    def pushed(self, path):
        """A file's text on try/issue-57 in the origin after the run, or None when absent."""
        p = subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", "show", f"try/issue-{ts.N}:{path}"],
                           capture_output=True, text=True)
        return p.stdout if p.returncode == 0 else None

    def signals(self):
        """Every start signal sent with Dokima's app key: [(role, stage, issue)]."""
        path = f"{self.tmp}/gh/dispatches.jsonl"
        sent = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
        return [(s["payload"].get("role"), s["payload"].get("stage"), s["payload"].get("issue"))
                for s in sent if s["event_type"] == "dokima-next" and s["token"] == "fake-token"]

    def on(self, kind, number):
        """The bodies now of every comment the run wrote on issue or pr `number`."""
        return [c["versions"][-1] for c in self.comments() if c["kind"] == kind and c["number"] == int(number)]

    def records(self):
        """Every record the run posted, read back from its comments."""
        return agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in self.posted()])

    def why(self):
        """Where the run stopped and its last output, for a failure message."""
        return f"result {self.result}, failed step {self.failed_step!r}:\n{self.tail()}"


def test_work_on_a_hotfix_starts_its_worker_with_no_plan(record_property, tmp_path):
    """A code owner's `/work` on a hotfix issue with no plan starts its worker.

    Proves 863.1. Runs agent.yml for the worker, as `/work` starts it, on #57: labeled hotfix, never planned, no
    try branch. The agent must start and its pack must hold no plan.json. Beside it, the same
    issue without the hotfix label must still not start a worker, since it has no approved plan."""
    record_property("proves", "863.1")
    r = Hotfix(tmp_path / "hotfix", "worker")
    assert r.agent_started(), f"863.1: `/work` on a hotfix issue with no plan did not start its worker; {r.why()}"
    assert r.pack_file("plan.json") is None, "863.1: the hotfix worker's pack held a plan.json, though the issue has no plan"
    plain = Hotfix(tmp_path / "plain", "worker", labels=())
    assert not plain.agent_started(), "863.1: an unlabeled issue with no approved plan started a worker"


def test_autopilot_starts_a_hotfix_worker_instead_of_its_planner(record_property, tmp_path):
    """On autopilot, a hotfix that nothing open blocks starts its worker, not its planner.

    Proves 863.2. A tree on autopilot: #57 over #101 (hotfix), #102 (no label) and #103 (hotfix), #101 and #102
    blocked by #110, #103 by #111. When #110 closes, #101 must get one worker started and no planner, while #102 still
    gets its planner, and #103, still blocked by open #111, gets nothing. Then `/autopilot start` on a parent over one
    unblocked hotfix, #101, must start #101's worker and no planner."""
    record_property("proves", "863.2")
    labels = {57: [tac.LABEL], 101: [tac.LABEL, HOTFIX], 102: [tac.LABEL], 103: [tac.LABEL, HOTFIX]}
    m = tac.Repo(tmp_path / "close", {57: [101, 102, 103]}, labels, deps={101: [110], 102: [110], 103: [111]})
    m.close(110)
    assert not m.failed, f"863.2 (close): a workflow failed when #110 closed: {m.failures}\n{m.tail()}"
    workers = [int(s["payload"]["issue"]) for s in m.signals()
               if s["payload"].get("role") == "worker" and s["token"] == "fake-token"]
    planners = m.planners_started("863.2")
    assert workers == [101], f"863.2 (close): the unblocked hotfix #101 did not get exactly one worker; workers: {workers}"
    assert 101 not in planners, f"863.2 (close): the hotfix #101 got its planner started: {planners}"
    assert planners.get(102) == 1, f"863.2 (close): #102, not a hotfix, did not start its planner once: {planners}"
    assert 103 not in planners and 103 not in workers, "863.2 (close): #103, still blocked, started something"

    m = tac.Repo(tmp_path / "start", {57: [101]}, {101: [HOTFIX]})
    m.listen("/autopilot start")
    assert not m.failed, f"863.2 (/autopilot start): the listener failed:\n{m.tail()}"
    workers = [int(s["payload"]["issue"]) for s in m.signals()
               if s["payload"].get("role") == "worker" and s["token"] == "fake-token"]
    assert workers == [101], f"863.2 (/autopilot start): the hotfix #101 did not get exactly one worker: {m.signals()}"
    assert 101 not in m.planners_started("863.2"), "863.2 (/autopilot start): the hotfix #101 got its planner started"


def test_a_hotfix_worker_pack_gives_the_issue_text_as_the_ask(record_property, tmp_path):
    """A hotfix worker's pack gives the issue's text as its whole ask, no plan.

    Proves 863.3. Runs the hotfix worker on #57. When the agent starts, its pack must hold ask.md carrying the
    issue's text, word for word, and no plan.json; and its prompt must point it to ask.md."""
    record_property("proves", "863.3")
    r = Hotfix(tmp_path, "worker")
    assert r.agent_started(), f"863.3: the hotfix worker never started; {r.why()}"
    ask = r.pack_file("ask.md")
    assert ask is not None and ASK in ask, f"863.3: the pack's ask.md does not carry the issue's text {ASK!r}: {ask!r}"
    assert r.pack_file("plan.json") is None, "863.3: the hotfix worker's pack held a plan.json"
    assert "ask.md" in r.prompt(), "863.3: the hotfix worker's prompt never points it to ask.md"


def test_a_hotfix_worker_change_stays_on_the_pull_request(record_property, tmp_path):
    """A hotfix worker's code and test changes are pushed as written, nothing dropped.

    Proves 863.4. The hotfix worker fixes app.py, adds lib/title.py, adds tests/test_app.py and changes the older
    tests/test_old.py, with no plan naming any of them. After the run try/issue-57 must hold all four exactly as the
    worker wrote them, and the fence must list none as dropped."""
    record_property("proves", "863.4")
    r = Hotfix(tmp_path, "worker")
    assert not r.failed, f"863.4: the hotfix worker's run failed; {r.why()}"
    assert r.pushed("app.py") == FIXED_APP, f"863.4: the worker's fix to app.py was not pushed: {r.pushed('app.py')!r}"
    assert r.pushed("lib/title.py") == NEW_LIB, "863.4: the worker's new lib/title.py was not pushed"
    assert r.pushed("tests/test_app.py") == NEW_TEST, "863.4: the worker's new tests/test_app.py was not pushed"
    assert r.pushed("tests/test_old.py") == CHANGED_OLD, \
        f"863.4: the worker's change to tests/test_old.py was not pushed: {r.pushed('tests/test_old.py')!r}"
    dropped = os.path.join(r.env.get("OUT", ""), "dropped.txt")
    listed = open(dropped).read().split() if os.path.exists(dropped) else []
    assert not {"app.py", "lib/title.py", "tests/test_app.py", "tests/test_old.py"} & set(listed), \
        f"863.4: the fence listed the worker's changes as dropped: {listed}"


def test_a_finished_hotfix_worker_starts_code_review_on_its_pull_request(record_property, tmp_path):
    """When a hotfix worker finishes, its pull request opens and code review starts on it.

    Proves 863.5. After the hotfix worker's run on #57, a draft pull request must have been opened from
    try/issue-57, and exactly one signal with Dokima's app key must start the reviewer at the pr stage for #57."""
    record_property("proves", "863.5")
    r = Hotfix(tmp_path, "worker")
    assert not r.failed, f"863.5: the hotfix worker's run failed; {r.why()}"
    opened = [c for c in r.calls() if c[:2] == ["pr", "create"]]
    assert len(opened) == 1 and f"try/issue-{ts.N}" in opened[0] and "--draft" in opened[0], \
        f"863.5: the hotfix worker did not open one draft pull request from try/issue-57: {opened}"
    assert r.signals() == [("reviewer", "pr", ts.N)], f"863.5: code review did not start once on the pull request: {r.signals()}"


def test_code_review_of_a_hotfix_gets_the_issue_text_as_the_ask(record_property, tmp_path):
    """Code review of a hotfix judges the diff against the issue's text, with no plan.

    Proves 863.6. Runs agent.yml for the reviewer at the pr stage on #57, whose worker built the fix on try/issue-57
    and opened #60. The agent must start, its pack must hold ask.md carrying the issue's text, the diff, and no
    plan.json, and its prompt must point it to ask.md."""
    record_property("proves", "863.6")
    r = Hotfix(tmp_path, "reviewer", "pr", comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")],
               review=APPROVE, built=True)
    assert r.agent_started(), f"863.6: code review of the hotfix never started; {r.why()}"
    ask = r.pack_file("ask.md")
    assert ask is not None and ASK in ask, f"863.6: the review pack's ask.md does not carry the issue's text: {ask!r}"
    assert "Dokima" in (r.pack_file("diff.patch") or ""), "863.6: the review pack does not hold the worker's diff"
    assert r.pack_file("plan.json") is None, "863.6: the hotfix review pack held a plan.json"
    assert "ask.md" in r.prompt(), "863.6: the hotfix reviewer's prompt never points it to ask.md"


def test_an_approved_hotfix_passes_the_merge_gate_like_any_pull_request(record_property, tmp_path, monkeypatch, capsys):
    """An approved hotfix runs all tests and the merge gate, and passes when they pass.

    Proves 863.7. Code review approves #57's hotfix pull request #60, whose required check is green. The review's
    record must pass its check, the gate must mark #60 ready so its tests run, and the record's Next line must say all
    tests passed. Beside it, the same approval with the required check red must not pass the gate: the record says
    the merge gate failed and the worker starts again. Then the Acceptance criteria check list for #60, opened by
    Dokima's app from try/issue-57, must hold no "No approved plan found" row that can only fail; beside it, the same pull request without the label still
    gets that row."""
    record_property("proves", "863.7")
    r = Hotfix(tmp_path, "reviewer", "pr", comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")],
               review=APPROVE, built=True)
    recs = r.records()
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("reviewer", True)], \
        f"863.7: the approving hotfix review did not post one passed record: {[(x['role'], x['check']) for x in recs]}; {r.why()}"
    assert any(c[:3] == ["pr", "ready", ts.PR] and "--undo" not in c for c in r.calls()), \
        f"863.7: the merge gate never marked #60 ready, so its tests never ran; {r.why()}"
    assert any("All tests passed with main's newest commit" in b for b in r.on("pr", ts.PR)), \
        f"863.7: the record does not say all tests passed at the merge gate: {r.on('pr', ts.PR)}"
    red = Hotfix(tmp_path / "red", "reviewer", "pr", comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")],
                 review=APPROVE, built=True, checks="failure")
    said = red.on("pr", ts.PR) + red.on("issue", ISSUE)
    assert not any("All tests passed" in b for b in said), \
        f"863.7: an approved hotfix whose required check failed still passed the merge gate: {said}"
    assert any(GATE_FAILED in b for b in said), \
        f"863.7: an approved hotfix whose required check failed was not stopped by the merge gate; {red.why()}"
    assert [s[0] for s in red.signals()] == ["worker"], \
        f"863.7: a hotfix that failed the merge gate did not go back to its worker: {red.signals()}"

    def matrix(labels):
        issue = {"number": ISSUE, "title": "Page title typo", "body": ASK, "comments": [], "state": "OPEN",
                 "labels": [{"name": n} for n in labels]}

        def gh(*a):
            if a[:2] == ("issue", "view"):
                return json.dumps(issue)
            if a[:1] == ("api",) and any(x.rstrip("/").endswith(f"repos/o/r/issues/{ISSUE}") for x in a):
                return json.dumps({"number": ISSUE, "state": "open", "labels": issue["labels"]})
            if a[:1] == ("api",) and any(x.split("?")[0].endswith(f"repos/o/r/issues/{ISSUE}/labels") for x in a):
                return json.dumps(issue["labels"])
            if a[:2] == ("pr", "list"):
                return "[]"
            return "[]" if "--paginate" in a else "{}"
        event = tmp_path / f"event-{len(labels)}.json"
        event.write_text(json.dumps({"pull_request": {"number": int(ts.PR), "head": {"ref": f"try/issue-{ts.N}"},
                                                      "body": f"Closes #{ts.N}", "user": {"login": f"{agent.BOT}[bot]"}}}))
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
        monkeypatch.setattr(agent_github, "gh", gh)
        checks.main(["checks", "matrix"])
        line = capsys.readouterr().out.strip().splitlines()[-1]
        return json.loads(line.split("=", 1)[1])
    rows = matrix([HOTFIX])
    assert rows and all(x["id"] != "none" for x in rows) and all(x["id"] == "manual-fix" or x["tests"] for x in rows), \
        f"863.7: the hotfix pull request's Acceptance criteria check cannot pass: {rows}"
    assert [x["id"] for x in matrix([])] == ["none"], "863.7: a Dokima pull request with no plan and no label lost its failing row"


def test_code_review_sends_a_too_big_hotfix_to_the_planner(record_property, tmp_path):
    """Code review finding a hotfix bigger than its ask starts the planner on the issue.

    Proves 863.8. Code review of #57's hotfix blocks it, raising a blocker for the planner: the change is bigger than
    the ask. Its record must pass its check, and exactly one signal must start the planner for #57, with no worker.
    Then, once a plan for #57 is approved, its worker must build that plan: its pack holds the plan."""
    record_property("proves", "863.8")
    r = Hotfix(tmp_path / "review", "reviewer", "pr", comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")],
               review=BLOCK, built=True)
    recs = r.records()
    assert [(x["role"], x["check"]["passed"]) for x in recs] == [("reviewer", True)], \
        f"863.8: the blocking hotfix review did not post one passed record; {r.why()}"
    assert r.signals() == [("planner", "plan", ts.N)], f"863.8: the planner did not start once on #57: {r.signals()}"
    planned = Hotfix(tmp_path / "planned", "worker", comments=ts.STORY_APPROVED, try_branch=True)
    assert planned.agent_started(), f"863.8: the worker of the planned issue never started; {planned.why()}"
    plan = json.loads(planned.pack_file("plan.json") or "{}")
    assert plan.get("kind") == "user_story", "863.8: once planned, the hotfix's worker was not given the approved plan"


def test_a_hotfix_sent_back_to_planning_says_why_on_the_issue(record_property, tmp_path):
    """A hotfix sent back to planning gets a comment on the issue saying why.

    Proves 863.9. Code review of #57's hotfix blocks it with a blocker for the planner whose text says the change
    is bigger than the ask. Issue #57 itself, not only its pull request, must get a new comment carrying that text."""
    record_property("proves", "863.9")
    r = Hotfix(tmp_path, "reviewer", "pr", comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")],
               review=BLOCK, built=True)
    assert r.agent_started(), f"863.9: code review of the hotfix never started; {r.why()}"
    said = [b for b in r.on("issue", ISSUE) if TOO_BIG in b]
    assert said, f"863.9: issue #57 got no comment saying why it went back to planning: {r.on('issue', ISSUE)}"


# What only Dokima's own repo has: its GitHub home, its code and topic paths, its workflow file.
DOKIMA_OWN = re.compile(r"dokima-dev|(?<![\w-])dokima/|(?<![\w-])rules/[\w-]+\.md|agent\.yml")
# Issue numbers a prompt may name: the issue at hand, its pull request and the shared raising example.
OWN_NUMBERS = {ISSUE, int(ts.PR), 164}


def test_hotfix_prompts_name_nothing_from_dokimas_own_repo(record_property, tmp_path):
    """The hotfix worker's and code reviewer's prompts name nothing from Dokima's own repo.

    Proves 863.10. Runs the hotfix worker, then code review of its pull request, on #57 in repo o/r. Each agent must
    start with a prompt that points it to ask.md, so the hotfix lane's words are there to read. Neither prompt may
    name Dokima's GitHub home, a path into Dokima's code or topic files, its workflow file, or an issue number other
    than #57, its pull request #60 and the shared example #164."""
    record_property("proves", "863.10")
    worker = Hotfix(tmp_path / "worker", "worker")
    review = Hotfix(tmp_path / "review", "reviewer", "pr",
                    comments=[ts.record_comment(worker_record(), "2026-10-07T10:30:00Z")], review=APPROVE, built=True)
    for name, r in (("worker", worker), ("code reviewer", review)):
        text = r.prompt()
        assert r.agent_started() and "ask.md" in text, \
            f"863.10: the hotfix {name} never started with the hotfix lane's prompt; {r.why()}"
        own = sorted(set(DOKIMA_OWN.findall(text)))
        assert not own, f"863.10: the hotfix {name}'s prompt names Dokima's own repo: {own}"
        numbers = sorted({int(n) for n in re.findall(r"(?<![\w&])#(\d+)\b", text)} - OWN_NUMBERS)
        assert not numbers, f"863.10: the hotfix {name}'s prompt names Dokima's own issues: {numbers}"


def review_on_issue(monkeypatch, capsys, labels, pr="", recs=()):
    """Route `/review` on issue #57 as the command workflow does.

    Returns what it printed and the comments it posted.

    The fake GitHub gives the issue these labels and, from `gh pr list`, the open pull request `pr` ('' for none)."""
    import record_seed
    record_seed.use(monkeypatch, ISSUE, list(recs))
    said = []

    def gh(*args, **kw):
        if args[:2] == ("api", f"repos/o/r/issues/{ISSUE}"):
            return json.dumps({"labels": [{"name": n} for n in labels]})
        if args[:2] == ("pr", "list"):
            return f"{pr}\n"
        if args[:2] == ("issue", "comment"):
            said.append(args[args.index("--body") + 1])
            return ""
        raise AssertionError(f"unexpected gh call: {args}")

    monkeypatch.setattr(agent_github, "gh", gh)
    for k, v in {"GITHUB_REPOSITORY": "o/r", "BODY": "/review", "NUMBER": str(ISSUE), "ON_PR": "false"}.items():
        monkeypatch.setenv(k, v)
    assert agent.main(["agent", "route"]) == 0
    return dict(line.split("=", 1) for line in capsys.readouterr().out.split()), said


def test_review_on_a_hotfix_issue_reviews_its_pull_request(monkeypatch, capsys):
    """`/review` on a hotfix issue with an open pull request starts code review (#892)."""
    out, said = review_on_issue(monkeypatch, capsys, [HOTFIX], pr=ts.PR)
    assert out == {"role": "reviewer", "stage": "pr", "issue": str(ISSUE)}, f"892: not a code review: {out}"
    assert said == []


def test_review_on_a_hotfix_issue_with_no_pull_request_says_why(monkeypatch, capsys):
    """`/review` on a hotfix issue with no pull request starts nothing and says why (#892)."""
    out, said = review_on_issue(monkeypatch, capsys, [HOTFIX])
    assert out == {}, f"892: a run started with no pull request: {out}"
    assert len(said) == 1 and "no plan to review" in said[0] and "pull request opens" in said[0], said


def test_review_on_a_planned_or_unlabeled_issue_still_reviews_the_plan(monkeypatch, capsys):
    """`/review` on an issue outside the hotfix lane still starts a plan review (#892)."""
    out, _ = review_on_issue(monkeypatch, capsys, [], pr=ts.PR)
    assert out["stage"] == "plan", f"892: an unlabeled issue's /review left plan review: {out}"
    planner = {"role": "planner", "stage": None, "run_id": "2", "handback": {}, "check": {"passed": True, "problems": []}}
    out, _ = review_on_issue(monkeypatch, capsys, [HOTFIX], pr=ts.PR, recs=[planner])
    assert out["stage"] == "plan", f"892: a planned hotfix's /review left plan review: {out}"

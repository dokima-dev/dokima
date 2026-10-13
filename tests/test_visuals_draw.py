"""One command draws what Dokima would post on a real issue, with any branch's code.

#624.

Story 1 of #584. Our own tool, outside the `dokima/` package, run from the root of a checkout:

    python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME

It takes the drawing code from BRANCH (for example through a git worktree of that branch, so the checkout it runs
from is left as it is), reads the real issue from GitHub through `gh`, and prints to stdout what that branch's code
would post: the issue's top card (`card.render`), every run comment drawn from the issue's real records
(`agent.render`), and every autopilot comment of the issue (the `AUTOPILOT_*` lines and `agent.autopilot_comment`).
An issue GitHub cannot give (a mistyped number, or GitHub refusing) or a branch that does not exist ends the command
with a non-zero exit and one plain message naming it, never a traceback.

How the tests prove it: each test builds a throwaway git repo holding a copy of this repo's `dokima/` and `tools/`
on `main`, plus a branch `visual-test` whose drawing code differs in ways no real code shows (markers such as
BRANCH-CARD, changed autopilot lines). A fake `gh` on PATH answers for a real-looking issue #7 with real records and
autopilot comments posted by the bot, and refuses every write. The command runs from the throwaway repo's root; a
marker in its output can only come from the branch's own code, and a run with `--branch main` shows today's drawing.
"""
import json
import os
import shutil
import subprocess
import sys
import textwrap

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dokima import agent  # noqa: E402

REPO = "dokima-dev/dokima"
BOT = "dokima-runtime"
ISSUE = 7
PLAN_SUMMARY = "Slow calls hand back a job id instead of timing out."
PLANNED = "The planner planned this issue."
REVIEWED = "The reviewer passed the plan."

FAKE_GH = r'''#!/usr/bin/env python3
"""A fake `gh` for the visuals tests: answers reads of the world in VISUALS_WORLD, logs every call, refuses writes."""
import json, os, re, sys

world = json.load(open(os.environ["VISUALS_WORLD"]))
argv = sys.argv[1:]
with open(os.environ["VISUALS_LOG"], "a") as f:
    f.write(json.dumps(argv) + "\n")


def out(value):
    print(json.dumps(value))
    sys.exit(0)


def refuse(reason):
    print(f"gh: {reason}", file=sys.stderr)
    sys.exit(1)


def issue(n):
    n = str(n)
    if n in world["refused"]:
        refuse(world["refused"][n])
    if n not in world["issues"]:
        refuse("Not Found (HTTP 404)")
    return world["issues"][n]


method = next((argv[i + 1] for i, a in enumerate(argv) if a in ("-X", "--method") and i + 1 < len(argv)), "GET")
if method.upper() != "GET" or argv[:2] in (["issue", "comment"], ["issue", "edit"], ["pr", "comment"], ["pr", "edit"]):
    refuse("fake gh refuses every write (HTTP 403)")
if argv[:2] == ["issue", "view"]:
    i = issue(argv[2])
    out({**i, "comments": i["comments"]})
if argv[:2] == ["pr", "list"]:
    out([])
if argv[:2] == ["pr", "view"]:
    out({"comments": [], "reviews": []})
if argv[:2] == ["api", "graphql"]:
    q = " ".join(argv)
    if "issue(number" in q:
        n = next(a.split("=", 1)[1] for a in argv if re.fullmatch(r"i=\d+", a))
        i = issue(n)
        out({"data": {"repository": {"issue": {"number": i["number"], "title": i["title"], "body": i["body"],
                                               "url": i["url"], "state": i["state"], "userContentEdits": {"nodes": []}}}}})
    if "pullRequest" in q:
        out({"data": {"repository": {"pullRequest": {"closingIssuesReferences": {"nodes": []}}}}})
    refuse("fake gh does not answer this query (HTTP 400)")
if argv[:1] == ["api"]:
    path = next(a for a in argv[1:] if not a.startswith("-") and a.startswith(("repos/", "/repos/"))).lstrip("/")
    path = path.split("?")[0]
    m = re.fullmatch(r"repos/[^/]+/[^/]+/issues/(\d+)(/.*)?", path)
    if m:
        i, rest = issue(m.group(1)), m.group(2) or ""
        if rest == "":
            out({"number": i["number"], "title": i["title"], "body": i["body"], "html_url": i["url"],
                 "state": i["state"].lower(), "labels": i["labels"], "user": {"login": "reza"}})
        if rest == "/comments":
            out([{"id": k + 1, "user": {"login": c["author"]["login"]}, "body": c["body"], "created_at": c["createdAt"],
                  "html_url": c["url"]} for k, c in enumerate(i["comments"])])
        if rest in ("/events", "/timeline", "/sub_issues", "/labels", "/dependencies/blocked_by",
                    "/dependencies/blocking"):
            out([])
    if re.fullmatch(r"repos/[^/]+/[^/]+/contents/.*", path):
        refuse("Not Found (HTTP 404)")
    if re.fullmatch(r"repos/[^/]+/[^/]+/actions/.*", path):
        out({"total_count": 0, "workflow_runs": []})
    if re.fullmatch(r"repos/[^/]+/[^/]+/(pulls|commits)(/.*)?", path):
        out([])
refuse("fake gh does not answer this call (HTTP 400): " + " ".join(argv))
'''

# Appended to the branch's copies, so only that branch's code draws these markers and lines.
BRANCH_CARD = '''

_visual_test_render = render


def render(*a, **k):
    """The branch's card: today's card under a marker."""
    return "BRANCH-CARD\\n" + _visual_test_render(*a, **k)
'''
BRANCH_AGENT = '''

_visual_test_render = render


def render(*a, **k):
    """The branch's run comment: today's comment under a marker."""
    return "BRANCH-RUN\\n" + _visual_test_render(*a, **k)


_visual_test_switch = autopilot_comment


def autopilot_comment(*a, **k):
    """The branch's /autopilot reply: today's reply after a marker."""
    return "BRANCH-SWITCH " + _visual_test_switch(*a, **k)


AUTOPILOT_LINE = "Autopilot: BRANCH blockers line"
AUTOPILOT_LINES = {"worker": "Autopilot: BRANCH work line", "split": "Autopilot: BRANCH split line"}
AUTOPILOT_START_LINE = "Autopilot: BRANCH switch line"
AUTOPILOT_MERGE = {"merged": "Autopilot: BRANCH merged PR #{pr}", "queued": "Autopilot: BRANCH PR #{pr} queued",
                   "waits": "Autopilot: BRANCH PR #{pr} waits"}
'''


def git(cwd, *args):
    """Run git in `cwd`, failing the test with git's own words."""
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r.stdout


def records():
    """A planner record and its approving plan review, as Dokima keeps them."""
    run = f"https://github.com/{REPO}/actions/runs/1"
    src = f"https://github.com/{REPO}/issues/{ISSUE}"
    planner = {"role": "planner", "stage": None, "run": run, "check": {"passed": True, "problems": []},
               "handback": {"kind": "user_story", "title": "Slow calls return a job id", "summary": PLAN_SUMMARY,
                            "user_story": "Callers get a job id for a slow call and fetch its result later.",
                            "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": src}],
                            "non_functional": [], "scope": ["app/jobs.py"],
                            "tests": {f"{ISSUE}.1": ["tests/test_jobs.py::test_job_id"]}}}
    review = {"role": "reviewer", "stage": "plan", "run": run, "check": {"passed": True, "problems": []},
              "handback": {"verdict": "approve", "blockers": []}}
    return planner, review


def comment(k, login, body):
    """One comment of the issue, in the shape `gh issue view --json comments` gives."""
    return {"author": {"login": login}, "body": body, "createdAt": f"2026-10-13T10:{k:02d}:00Z",
            "url": f"https://github.com/{REPO}/issues/{ISSUE}#issuecomment-{100 + k}"}


def world():
    """The fake GitHub: issue 7 with two records and five autopilot comments.

    Every comment but the owner's `/plan` is by the bot; issue 8 is refused."""
    planner, review = records()
    comments = [comment(1, "reza", "/plan"),
                comment(2, BOT, "Autopilot: blockers merged, starting plan"),
                comment(7, BOT, "Autopilot: switched on, starting plan"),
                comment(3, BOT, agent.render(planner)),
                comment(4, BOT, agent.render(review)),
                comment(5, BOT, "Autopilot: plan approved, starting work"),
                comment(6, BOT, f"Autopilot is on for #{ISSUE}. No stage was started.\n"),
                comment(8, BOT, "Autopilot: merged PR #9")]
    body = "Slow calls time out. Make them hand back a job id instead."
    return {"issues": {str(ISSUE): {"number": ISSUE, "title": "Slow calls time out", "body": body, "state": "OPEN",
                                     "url": f"https://github.com/{REPO}/issues/{ISSUE}", "labels": [],
                                     "comments": comments}},
            "refused": {"8": "Server Error (HTTP 502)"}}


@pytest.fixture(scope="module")
def place(tmp_path_factory):
    """A throwaway checkout on main, a branch with changed drawing code, and a fake `gh`.

    The branch is `visual-test`; the fake `gh` goes first on PATH."""
    base = tmp_path_factory.mktemp("visuals")
    repo = base / "checkout"
    shutil.copytree(os.path.join(ROOT, "dokima"), repo / "dokima", ignore=shutil.ignore_patterns("__pycache__"))
    if os.path.isdir(os.path.join(ROOT, "tools")):
        shutil.copytree(os.path.join(ROOT, "tools"), repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "main")
    git(repo, "checkout", "-q", "-b", "visual-test")
    with open(repo / "dokima" / "card.py", "a") as f:
        f.write(BRANCH_CARD)
    with open(repo / "dokima" / "agent.py", "a") as f:
        f.write(BRANCH_AGENT)
    git(repo, "commit", "-q", "-am", "branch drawing")
    git(repo, "checkout", "-q", "main")
    bin_dir = base / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(FAKE_GH)
    (bin_dir / "gh").chmod(0o755)
    (base / "world.json").write_text(json.dumps(world()))
    return {"repo": repo, "bin": bin_dir, "world": base / "world.json", "log": base / "gh.log"}


def draw(place, number, branch):
    """Run the command from the throwaway checkout's root; returns the finished process."""
    if not (place["repo"] / "tools" / "visuals.py").exists():
        pytest.fail("624: tools/visuals.py does not exist yet, so there is no command to draw an issue's posts")
    env = {k: v for k, v in os.environ.items() if k not in ("DOKIMA_BOT", "GITHUB_REPOSITORY", "REPO")}
    env.update(PATH=f"{place['bin']}{os.pathsep}{env.get('PATH', '')}", VISUALS_WORLD=str(place["world"]),
               VISUALS_LOG=str(place["log"]))
    return subprocess.run([sys.executable, "tools/visuals.py", "draw", str(number), "--branch", branch, "--repo", REPO],
                          cwd=place["repo"], env=env, capture_output=True, text=True, timeout=120)


def drawn(place, branch, criterion):
    """The command's output for issue 7 drawn from `branch`.

    Fails the test with the command's own words when it does not finish."""
    r = draw(place, ISSUE, branch)
    assert r.returncode == 0, f"{criterion}: drawing #{ISSUE} from {branch} exited {r.returncode}:\n{r.stdout}\n{r.stderr}"
    return r.stdout


def test_card_from_branch(place, record_property):
    """The top card of a real issue is drawn by the chosen branch's code.

    Draws issue 7 from a branch whose card code adds a marker, and checks the marker and the issue's own plan
    summary are both there; drawn from main, the summary shows with no marker. Proves 624.1."""
    record_property("proves", "624.1")
    out = drawn(place, "visual-test", "624.1")
    assert "BRANCH-CARD" in out, f"624.1: the card was not drawn by the branch's code:\n{out}"
    assert PLAN_SUMMARY in out, f"624.1: the card does not show the real issue's plan:\n{out}"
    main = drawn(place, "main", "624.1")
    assert PLAN_SUMMARY in main, f"624.1: drawn from main, the card does not show the real issue's plan:\n{main}"
    assert "BRANCH-CARD" not in main, f"624.1: drawn from main, the card still shows the other branch's code:\n{main}"


def test_mistyped_issue_says_so(place, record_property):
    """A mistyped issue number ends the command with a plain message naming the issue.

    Asks for issue 9999, which GitHub does not have, and checks the command fails naming the issue and GitHub's
    reason, with no traceback. Proves 624.1."""
    record_property("proves", "624.1")
    r = draw(place, 9999, "visual-test")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"624.1: drawing a missing issue did not fail:\n{said}"
    assert "#9999" in said and "HTTP 404" in said, f"624.1: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"624.1: a missing issue crashed the command instead of saying why:\n{said}"


def test_unreadable_issue_says_so(place, record_property):
    """An issue GitHub refuses ends the command with a plain message naming the issue.

    Asks for issue 8, which the fake GitHub answers with a server error, and checks the command fails naming the
    issue and GitHub's reason, with no traceback. Proves 624.1."""
    record_property("proves", "624.1")
    r = draw(place, 8, "visual-test")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"624.1: drawing an unreadable issue did not fail:\n{said}"
    assert "#8" in said and "HTTP 502" in said, f"624.1: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"624.1: an unreadable issue crashed the command instead of saying why:\n{said}"


def test_unknown_branch_says_so(place, record_property):
    """A missing branch ends the command with a plain message naming the branch.

    Asks for a misspelled branch and checks the command fails naming it, with no traceback. Proves 624.1."""
    record_property("proves", "624.1")
    r = draw(place, ISSUE, "no-such-branch")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"624.1: drawing from a missing branch did not fail:\n{said}"
    assert "no-such-branch" in said, f"624.1: the message does not name the missing branch:\n{said}"
    assert "Traceback" not in said, f"624.1: a missing branch crashed the command instead of saying why:\n{said}"


def test_run_comments_from_records(place, record_property):
    """Every run comment is drawn again from its real record by the branch's code.

    Issue 7 holds a plan and its plan review; the branch's run comment code adds a marker. Checks the marker shows
    once per record and each record's own summary follows one. Proves 624.2."""
    record_property("proves", "624.2")
    out = drawn(place, "visual-test", "624.2")
    chunks = out.split("BRANCH-RUN\n")[1:]
    assert len(chunks) == 2, f"624.2: expected 2 run comments drawn by the branch's code, found {len(chunks)}:\n{out}"
    assert any(PLANNED in c.split("BRANCH-")[0] for c in chunks), \
        f"624.2: no run comment drawn from the planner's record:\n{out}"
    assert any(REVIEWED in c.split("BRANCH-")[0] for c in chunks), \
        f"624.2: no run comment drawn from the plan review's record:\n{out}"


def test_run_comments_none(place, record_property):
    """An issue with no records draws no run comment and still draws its card.

    Draws issue 7 with every record removed and checks no run comment is drawn while the card still is. Proves 624.2."""
    record_property("proves", "624.2")
    w = json.loads(place["world"].read_text())
    w["issues"][str(ISSUE)]["comments"] = [c for c in w["issues"][str(ISSUE)]["comments"] if agent.MARK not in c["body"]]
    bare = place["world"].parent / "bare.json"
    bare.write_text(json.dumps(w))
    r = draw({**place, "world": bare}, ISSUE, "visual-test")
    assert r.returncode == 0, f"624.2: an issue with no records did not draw:\n{r.stdout}\n{r.stderr}"
    assert "BRANCH-RUN" not in r.stdout, f"624.2: run comments were drawn for an issue with no records:\n{r.stdout}"
    assert "BRANCH-CARD" in r.stdout, f"624.2: an issue with no records drew no card:\n{r.stdout}"


def test_autopilot_comments_from_branch(place, record_property):
    """Every autopilot comment of the issue is drawn by the chosen branch's code.

    Issue 7 holds four autopilot lines (blockers merged, switched on, plan approved, merged PR) and one autopilot
    switch reply. The branch changes every line and marks the reply; checks each shows as the branch draws it, and
    as today's when drawn from main. Proves 624.3."""
    record_property("proves", "624.3")
    out = drawn(place, "visual-test", "624.3")
    for line in ("Autopilot: BRANCH blockers line", "Autopilot: BRANCH switch line", "Autopilot: BRANCH work line",
                 "Autopilot: BRANCH merged PR #9",
                 f"BRANCH-SWITCH Autopilot is on for #{ISSUE}. No stage was started."):
        assert line in out, f"624.3: the branch's code did not draw the autopilot comment {line!r}:\n{out}"
    main = drawn(place, "main", "624.3")
    for line in ("Autopilot: blockers merged, starting plan", "Autopilot: switched on, starting plan",
                 "Autopilot: plan approved, starting work", "Autopilot: merged PR #9",
                 f"Autopilot is on for #{ISSUE}. No stage was started."):
        assert line in main, f"624.3: drawn from main, the autopilot comment {line!r} is missing:\n{main}"
    assert "BRANCH" not in main, f"624.3: drawn from main, an autopilot comment shows the other branch's code:\n{main}"

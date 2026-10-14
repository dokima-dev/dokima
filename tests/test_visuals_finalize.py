"""Approving a preview saves its inputs and output, and posts its record on its issue.

#627.

Story 4 of #584. Builds on story 1's `tools/visuals.py draw` and story 2's `preview`. The new subcommand, run from
the root of a checkout once the owner approves a preview:

    python3 tools/visuals.py finalize ISSUE --branch BRANCH --repo OWNER/NAME

draws exactly what `draw` prints for ISSUE and BRANCH and freezes it in this checkout, under `tests/fixtures/cards/`,
in the shape of branch `fixture/card-557`:

- `ISSUE.inputs.json`: the top card's inputs, `{"repo", "issue", "found", ...}`, so that
  `card.render(repo, issue, found)` redraws the card offline.
- `ISSUE.card.md`: the top card exactly as BRANCH's `card.render` drew it.
- `ISSUE.comments.inputs.json`: the run and autopilot comments' inputs, `{"repo", "issue", "pr", "posts"}`, where
  `posts` is the list `draw` hands its painter: `{"kind": "record", "rec": ..., "url": ...}` for a run record and
  `{"kind": ..., "url": ...}` for an autopilot comment.
- `ISSUE.comments.md`: those comments exactly as `draw` prints them after the card.

It then posts the whole drawing on ISSUE of OWNER/NAME as one comment whose first line is the hidden marker
`<!-- visuals-fixture -->`, so the comment is found again as that visual's fixture record. An issue GitHub cannot
give, or a post GitHub refuses, ends the command with a non-zero exit and one plain message, never a traceback.

How the tests prove it: the throwaway checkout, its `visual-test` branch and the fake GitHub of story 1's tests
(`tests/test_visuals_draw.py`) are reused. In front of that fake `gh` sits a small fake that accepts comment writes
to OWNER/NAME's issues, keeps them in a state file and refuses them on issue 11; reads fall through to story 1's fake.
"""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tests import test_visuals_draw as story1  # noqa: E402
from tests.test_visuals_draw import ISSUE, PLAN_SUMMARY, REPO  # noqa: E402

MARKER = "<!-- visuals-fixture -->"
REFUSED = 11
FIXTURES = os.path.join("tests", "fixtures", "cards")

# Takes comment writes to REPO's issues itself; every other call falls through to story 1's fake below it.
FAKE_HERE = r'''#!/usr/bin/env python3
"""A fake `gh`: comments written on REPO's issues land in VISUALS_HERE; every other call goes to story 1's fake."""
import json, os, re, sys

REPO = "dokima-dev/dokima"
argv = sys.argv[1:]


def opt(names):
    for i, a in enumerate(argv):
        for n in names:
            if a == n and i + 1 < len(argv):
                return argv[i + 1]
            if n.startswith("--") and a.startswith(n + "="):
                return a.split("=", 1)[1]
    return None


def text_of(value):
    if value == "-":
        return sys.stdin.read()
    return open(value).read()


def body_given():
    for i, a in enumerate(argv):
        nxt = argv[i + 1] if i + 1 < len(argv) else ""
        if a in ("-f", "--raw-field", "-F", "--field") and nxt.startswith("body="):
            v = nxt.split("=", 1)[1]
            return text_of(v[1:]) if a in ("-F", "--field") and v.startswith("@") else v
        if a == "--input":
            return json.loads(text_of(nxt))["body"]
        if a in ("-b", "--body"):
            return nxt
        if a == "--body-file":
            return text_of(nxt)
        if a.startswith("--body="):
            return a.split("=", 1)[1]
        if a.startswith("--body-file="):
            return text_of(a.split("=", 1)[1])
    print("gh: fake gh found no body (HTTP 422)", file=sys.stderr)
    sys.exit(1)


def write_target():
    """The issue number a comment write to REPO aims at, else None."""
    if argv[:2] == ["issue", "comment"] and (opt(["-R", "--repo"]) or REPO) == REPO:
        return re.sub(r"\D", "", argv[2].rsplit("/", 1)[-1])
    if argv[:1] == ["api"]:
        method = (opt(["-X", "--method"]) or "").upper()
        fields = any(a in ("-f", "-F", "--field", "--raw-field", "--input") for a in argv)
        if (method or ("POST" if fields else "GET")) == "GET":
            return None
        for a in argv[1:]:
            m = re.fullmatch(rf"/?repos/{REPO}/issues/(\d+)/comments", a.split("?")[0])
            if m:
                return m.group(1)
    return None


target = write_target()
if target is not None:
    with open(os.environ["VISUALS_LOG"], "a") as f:
        f.write(json.dumps(argv) + "\n")
    state_file = os.environ["VISUALS_HERE"]
    state = json.load(open(state_file))
    if target == str(state["refuse"]):
        print("gh: Resource not accessible by integration (HTTP 403)", file=sys.stderr)
        sys.exit(1)
    body = body_given()
    state["next"] += 1
    url = f"https://github.com/{REPO}/issues/{target}#issuecomment-{state['next']}"
    state["posted"].setdefault(target, []).append({"id": state["next"], "body": body})
    with open(state_file, "w") as f:
        json.dump(state, f)
    if argv[:1] == ["api"]:
        print(json.dumps({"id": state["next"], "body": body, "html_url": url}))
    else:
        print(url)
    sys.exit(0)
'''


@pytest.fixture(scope="module")
def place(tmp_path_factory):
    """Story 1's throwaway checkout and fake GitHub, plus the comment fake and issue 11.

    Issue 11 is a copy of issue 7 whose comments GitHub refuses to take."""
    base = tmp_path_factory.mktemp("finalize")
    repo = base / "checkout"
    shutil.copytree(os.path.join(ROOT, "dokima"), repo / "dokima", ignore=shutil.ignore_patterns("__pycache__"))
    if os.path.isdir(os.path.join(ROOT, "tools")):
        shutil.copytree(os.path.join(ROOT, "tools"), repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    story1.git(repo, "init", "-q", "-b", "main")
    story1.git(repo, "config", "user.name", "Test")
    story1.git(repo, "config", "user.email", "test@example.com")
    story1.git(repo, "add", "-A")
    story1.git(repo, "commit", "-q", "-m", "main")
    story1.git(repo, "checkout", "-q", "-b", "visual-test")
    with open(repo / "dokima" / "card.py", "a") as f:
        f.write(story1.BRANCH_CARD)
    with open(repo / "dokima" / "agent.py", "a") as f:
        f.write(story1.BRANCH_AGENT)
    story1.git(repo, "commit", "-q", "-am", "branch drawing")
    story1.git(repo, "checkout", "-q", "main")
    bin_dir = base / "bin"
    bin_dir.mkdir()
    rest = story1.FAKE_GH.split("\n", 1)[1]
    (bin_dir / "gh").write_text(FAKE_HERE + "\n" + rest)
    (bin_dir / "gh").chmod(0o755)
    w = story1.world()
    seven = w["issues"][str(ISSUE)]
    w["issues"][str(REFUSED)] = {**seven, "number": REFUSED, "title": "Another visual",
                                 "url": f"https://github.com/{REPO}/issues/{REFUSED}"}
    (base / "world.json").write_text(json.dumps(w))
    return {"repo": repo, "bin": bin_dir, "world": base / "world.json", "base": base}


def fresh(place, name):
    """A clean start for one test: no fixtures, no comments, a new log."""
    shutil.rmtree(place["repo"] / "tests" / "fixtures", ignore_errors=True)
    here = place["base"] / f"{name}.here.json"
    here.write_text(json.dumps({"next": 900, "refuse": REFUSED, "posted": {}}))
    log = place["base"] / f"{name}.log"
    log.write_text("")
    return {**place, "here": here, "log": log}


def env_of(place):
    """The command's environment: the fake `gh` first on PATH, with this test's files."""
    env = {k: v for k, v in os.environ.items() if k not in ("DOKIMA_BOT", "GITHUB_REPOSITORY", "REPO")}
    env.update(PATH=f"{place['bin']}{os.pathsep}{env.get('PATH', '')}", VISUALS_WORLD=str(place["world"]),
               VISUALS_LOG=str(place["log"]), VISUALS_HERE=str(place["here"]))
    return env


def finalize(place, number, branch, criterion):
    """Run `finalize` from the throwaway checkout's root; returns the finished process."""
    if not (place["repo"] / "tools" / "visuals.py").exists():
        pytest.fail(f"{criterion}: tools/visuals.py does not exist, so there is no command to finalize with")
    return subprocess.run([sys.executable, "tools/visuals.py", "finalize", str(number), "--branch", branch,
                           "--repo", REPO], cwd=place["repo"], env=env_of(place), capture_output=True, text=True,
                          timeout=120)


def finalized(place, number, branch, criterion):
    """Finalize the issue from the branch; fails the test when the command fails."""
    r = finalize(place, number, branch, criterion)
    assert r.returncode == 0, \
        f"{criterion}: finalizing #{number} from {branch} exited {r.returncode}:\n{r.stdout}\n{r.stderr}"
    return r


def drawing(place, number, branch, criterion):
    """What `draw` prints for the issue and branch, split into its card and its comments.

    The card is what follows the `# Card of #N` heading, up to the first comment's heading."""
    r = subprocess.run([sys.executable, "tools/visuals.py", "draw", str(number), "--branch", branch, "--repo", REPO],
                       cwd=place["repo"], env=env_of(place), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"{criterion}: drawing #{number} from {branch} failed:\n{r.stdout}\n{r.stderr}"
    head = f"# Card of #{number}\n\n"
    assert r.stdout.startswith(head), f"{criterion}: `draw` no longer starts with the card:\n{r.stdout}"
    card, _, comments = r.stdout[len(head):].partition("\n\n\n# ")
    return {"all": r.stdout, "card": card, "comments": ("# " + comments) if comments else ""}


def saved(place, name, criterion):
    """One saved fixture file's text; fails the test when it is missing."""
    path = place["repo"] / FIXTURES / name
    assert path.is_file(), f"{criterion}: finalizing saved no {FIXTURES}/{name}; the folder holds " \
                           f"{sorted(os.listdir(path.parent)) if path.parent.is_dir() else 'nothing'}"
    return path.read_text()


def posted(place, number):
    """The comments the command posted on the issue, oldest first."""
    return json.loads(place["here"].read_text())["posted"].get(str(number), [])


def redraw_card(place, inputs):
    """Draw the card from saved inputs with main's code, with no `gh` reachable."""
    code = ("import json, sys\nfrom dokima import card\nd = json.load(open(sys.argv[1]))\n"
            "sys.stdout.write(card.render(d['repo'], d['issue'], d['found']))")
    env = {"PATH": "", "HOME": str(place["base"]), "PYTHONPATH": str(place["repo"])}
    r = subprocess.run([sys.executable, "-c", code, str(inputs)], cwd=place["repo"], env=env, capture_output=True,
                       text=True, timeout=60)
    return r


def test_finalize_saves_card_inputs(place, record_property):
    """The card's saved inputs draw the same card again, offline.

    Finalizes issue 7 from main, then draws the card from the saved inputs file alone, with no `gh` on the path, and
    checks it names the issue and repo, holds the issue's plan, and draws byte for byte the saved card. Proves 627.1."""
    record_property("proves", "627.1")
    p = fresh(place, "card-inputs")
    finalized(p, ISSUE, "main", "627.1")
    inputs = json.loads(saved(p, f"{ISSUE}.inputs.json", "627.1"))
    assert inputs.get("repo") == REPO, f"627.1: the saved inputs do not name the repo {REPO}:\n{inputs.get('repo')}"
    assert (inputs.get("issue") or {}).get("number") == ISSUE, \
        f"627.1: the saved inputs do not hold issue {ISSUE}:\n{inputs.get('issue')}"
    r = redraw_card(p, p["repo"] / FIXTURES / f"{ISSUE}.inputs.json")
    assert r.returncode == 0, f"627.1: the saved inputs could not draw the card offline:\n{r.stderr}"
    assert PLAN_SUMMARY in r.stdout, f"627.1: the card drawn from the saved inputs lacks the issue's plan:\n{r.stdout}"
    card = saved(p, f"{ISSUE}.card.md", "627.1")
    assert r.stdout == card, f"627.1: the saved inputs draw a different card than the one saved.\n" \
                             f"Drawn:\n{r.stdout}\nSaved:\n{card}"


def test_finalize_saves_comment_inputs(place, record_property):
    """Every record and autopilot comment of the issue is saved as input, whole.

    Finalizes issue 7 and checks the saved comment inputs hold its two real records, as recorded, and each of its
    five autopilot comments with everything the painter needs to word it again: its kind, link, key, pull request
    number or reply arguments, in the issue's order. Proves 627.1."""
    record_property("proves", "627.1")
    p = fresh(place, "comment-inputs")
    finalized(p, ISSUE, "visual-test", "627.1")
    inputs = json.loads(saved(p, f"{ISSUE}.comments.inputs.json", "627.1"))
    assert inputs.get("repo") == REPO and inputs.get("issue") == ISSUE, \
        f"627.1: the comment inputs do not name {REPO} issue {ISSUE}:\n{inputs.get('repo')} {inputs.get('issue')}"
    posts = inputs.get("posts")
    assert isinstance(posts, list), f"627.1: the comment inputs hold no list of posts:\n{inputs}"
    recs = [x.get("rec") for x in posts if x.get("kind") == "record"]
    assert recs == list(story1.records()), f"627.1: the saved records are not the issue's two records:\n{recs}"

    def url(k):
        return f"https://github.com/{REPO}/issues/{ISSUE}#issuecomment-{100 + k}"

    # What `draw` hands its painter for each autopilot comment of story 1's issue 7, oldest first.
    auto = [{"kind": "line", "url": url(2)},
            {"kind": "start", "url": url(7)},
            {"kind": "lines", "key": "worker", "url": url(5)},
            {"kind": "reply", "args": [ISSUE, "start", [ISSUE], [], "No stage was started."], "url": url(6)},
            {"kind": "merge", "key": "merged", "pr": 9, "url": url(8)}]
    got = [x for x in posts if x.get("kind") != "record"]
    assert got == auto, f"627.1: the saved autopilot posts cannot word the issue's autopilot comments again.\n" \
                        f"Wanted: {json.dumps(auto, indent=1)}\nSaved: {json.dumps(got, indent=1)}"


def test_finalize_unreadable_issue_saves_nothing(place, record_property):
    """An issue GitHub cannot give saves no fixture, posts nothing, and says why.

    Finalizes issue 8, which the fake GitHub refuses, and checks the command fails naming it and GitHub's reason,
    with no traceback, no fixture file and no comment. Proves 627.1."""
    record_property("proves", "627.1")
    p = fresh(place, "unreadable")
    r = finalize(p, 8, "visual-test", "627.1")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"627.1: finalizing an unreadable issue did not fail:\n{said}"
    assert "#8" in said and "HTTP 502" in said, f"627.1: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"627.1: an unreadable issue crashed the command instead of saying why:\n{said}"
    folder = p["repo"] / FIXTURES
    left = sorted(os.listdir(folder)) if folder.is_dir() else []
    assert not [f for f in left if f.startswith("8.")], f"627.1: fixtures were saved for an unreadable issue: {left}"
    assert not posted(p, 8), f"627.1: a comment was posted for an issue that could not be drawn:\n{posted(p, 8)}"


def test_finalize_saves_card_output(place, record_property):
    """The card is saved exactly as the chosen branch drew it.

    Finalizes issue 7 from a branch whose card code adds a marker, and checks the saved card is the card `draw`
    prints for that branch, marker and plan included. Proves 627.2."""
    record_property("proves", "627.2")
    p = fresh(place, "card-output")
    want = drawing(p, ISSUE, "visual-test", "627.2")
    finalized(p, ISSUE, "visual-test", "627.2")
    card = saved(p, f"{ISSUE}.card.md", "627.2")
    assert card.startswith("BRANCH-CARD\n") and PLAN_SUMMARY in card, \
        f"627.2: the saved card is not the branch's drawing of the issue:\n{card}"
    assert card.rstrip("\n") == want["card"].rstrip("\n"), \
        f"627.2: the saved card differs from the drawn one.\nDrawn:\n{want['card']}\nSaved:\n{card}"


def test_finalize_saves_comment_output(place, record_property):
    """Run and autopilot comments are saved beside the card, as the branch drew them.

    Finalizes issue 7 from a branch whose run comment code and autopilot lines differ, and checks the saved comments
    are what `draw` prints after the card, with both run comments and the branch's autopilot line. Proves 627.2."""
    record_property("proves", "627.2")
    p = fresh(place, "comment-output")
    want = drawing(p, ISSUE, "visual-test", "627.2")
    finalized(p, ISSUE, "visual-test", "627.2")
    comments = saved(p, f"{ISSUE}.comments.md", "627.2")
    assert comments.count("BRANCH-RUN\n") == 2 and "Autopilot: BRANCH work line" in comments, \
        f"627.2: the saved comments are not the branch's drawing of the issue's comments:\n{comments}"
    assert comments.strip("\n") == want["comments"].strip("\n"), \
        f"627.2: the saved comments differ from the drawn ones.\nDrawn:\n{want['comments']}\nSaved:\n{comments}"


def test_finalize_issue_with_no_records(place, record_property):
    """An issue with no run records still saves its card, with no run comment.

    Finalizes issue 7 with every record removed and checks the card is saved as drawn and the saved comments
    hold no run comment. Proves 627.2."""
    record_property("proves", "627.2")
    w = json.loads(place["world"].read_text())
    from dokima import agent
    w["issues"][str(ISSUE)]["comments"] = [c for c in w["issues"][str(ISSUE)]["comments"] if agent.MARK not in c["body"]]
    bare = place["base"] / "bare.json"
    bare.write_text(json.dumps(w))
    p = fresh({**place, "world": bare}, "bare")
    want = drawing(p, ISSUE, "visual-test", "627.2")
    finalized(p, ISSUE, "visual-test", "627.2")
    card = saved(p, f"{ISSUE}.card.md", "627.2")
    assert card.startswith("BRANCH-CARD\n") and card.rstrip("\n") == want["card"].rstrip("\n"), \
        f"627.2: an issue with no records did not save its card as drawn:\n{card}"
    comments = saved(p, f"{ISSUE}.comments.md", "627.2")
    assert "BRANCH-RUN" not in comments, f"627.2: run comments were saved for an issue with no records:\n{comments}"


def test_finalize_posts_fixture_record(place, record_property):
    """The final drawing is posted on its issue as one marked fixture record.

    Finalizes issue 7 from the branch and checks exactly one comment was posted on issue 7 of this repo, that it
    opens with the fixture marker, and that it holds the whole drawing `draw` prints. Proves 627.3."""
    record_property("proves", "627.3")
    p = fresh(place, "post")
    want = drawing(p, ISSUE, "visual-test", "627.3")
    finalized(p, ISSUE, "visual-test", "627.3")
    cs = posted(p, ISSUE)
    assert len(cs) == 1, f"627.3: expected one fixture record on issue {ISSUE}, found {len(cs)}:\n{cs}"
    body = cs[0]["body"]
    assert body.split("\n", 1)[0] == MARKER, f"627.3: the comment does not open with the marker {MARKER}:\n{body}"
    assert want["all"].strip() in body, \
        f"627.3: the comment does not hold the final drawing.\nWanted:\n{want['all']}\nPosted:\n{body}"
    others = {k: v for k, v in json.loads(p["here"].read_text())["posted"].items() if k != str(ISSUE)}
    assert not others, f"627.3: finalizing #{ISSUE} posted on other issues too:\n{others}"


def test_finalize_refused_post_says_so(place, record_property):
    """A fixture record GitHub refuses to take ends the command with a plain message.

    Finalizes issue 11, whose comments the fake GitHub refuses, and checks the command fails naming the issue and
    GitHub's reason, with no traceback. Proves 627.3."""
    record_property("proves", "627.3")
    p = fresh(place, "refused")
    r = finalize(p, REFUSED, "visual-test", "627.3")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"627.3: a refused fixture record did not fail the command:\n{said}"
    assert f"#{REFUSED}" in said and "HTTP 403" in said, \
        f"627.3: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"627.3: a refused post crashed the command instead of saying why:\n{said}"

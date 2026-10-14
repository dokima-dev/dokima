"""The command previews its drawing as one gallery comment, and keeps editing it.

#625.

Story 2 of #584. Builds on story 1's `tools/visuals.py draw`. The new subcommand, run from the root of a checkout:

    python3 tools/visuals.py preview ISSUE --branch BRANCH --repo OWNER/NAME --gallery-issue N

draws exactly what `draw` prints for ISSUE and BRANCH, and posts it, with the caller's own `gh` login, as one comment
on issue N of `dokima-dev/card-gallery`. The comment carries a hidden marker naming the real issue, so a later
preview of the same issue edits that same comment instead of posting another; comments of other previews and plain
notes on the gallery issue are left alone. Nothing is written to OWNER/NAME or to the real issue. A gallery issue
GitHub cannot give, or a real issue it cannot give, ends the command with a non-zero exit and one plain message,
never a traceback.

How the tests prove it: the throwaway checkout, its `visual-test` branch and the fake GitHub of story 1's tests
(`tests/test_visuals_draw.py`) are reused. In front of that fake `gh` sits a small fake of the gallery repo: it keeps
the gallery issue's comments in a state file, answers `gh api` reads and writes of `repos/dokima-dev/card-gallery/...`
(list, post and edit comments) and `gh issue comment` on that repo, and logs every call. Every other write is refused
and logged by story 1's fake, so the log shows any write that reached this repo.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tests import test_visuals_draw as story1  # noqa: E402
from tests.test_visuals_draw import ISSUE, PLAN_SUMMARY, REPO  # noqa: E402

GALLERY = "dokima-dev/card-gallery"
GALLERY_ISSUE = 3
OTHER = 11
NOTE = "Looks right on my phone too."

# Answers the gallery repo's calls itself; every other call falls through to story 1's fake below it.
FAKE_GALLERY = r'''#!/usr/bin/env python3
"""A fake `gh`: the gallery repo's comments live in VISUALS_GALLERY; every other call goes to story 1's fake."""
import json, os, re, sys

GALLERY = "dokima-dev/card-gallery"
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


def gallery_call():
    if argv[:1] == ["api"]:
        paths = [a.lstrip("/") for a in argv[1:] if a.lstrip("/").startswith(f"repos/{GALLERY}/")]
        return paths[0].split("?")[0] if paths else None
    if argv[:1] in (["issue"], ["pr"]) and (opt(["-R", "--repo"]) or "") == GALLERY:
        return "cli"
    return None


path = gallery_call()
if path is None:
    pass  # story 1's fake follows
else:
    with open(os.environ["VISUALS_LOG"], "a") as f:
        f.write(json.dumps(argv) + "\n")
    state_file = os.environ["VISUALS_GALLERY"]
    state = json.load(open(state_file))

    def save():
        with open(state_file, "w") as f:
            json.dump(state, f)

    def out(value):
        print(json.dumps(value))
        sys.exit(0)

    def refuse(reason):
        print(f"gh: {reason}", file=sys.stderr)
        sys.exit(1)

    def comments_of(n):
        n = str(n)
        if n not in state["issues"]:
            refuse("Not Found (HTTP 404)")
        return state["issues"][n]

    def shown(c, n):
        return {"id": c["id"], "body": c["body"], "user": {"login": c["login"]}, "author": {"login": c["login"]},
                "html_url": f"https://github.com/{GALLERY}/issues/{n}#issuecomment-{c['id']}",
                "url": f"https://github.com/{GALLERY}/issues/{n}#issuecomment-{c['id']}"}

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
            if a in ("--body-file",):
                return text_of(nxt)
            if a.startswith("--body="):
                return a.split("=", 1)[1]
            if a.startswith("--body-file="):
                return text_of(a.split("=", 1)[1])
        refuse("fake gh found no body (HTTP 422)")

    def post(n, body):
        cs = comments_of(n)
        state["next"] += 1
        c = {"id": state["next"], "body": body, "login": "reza"}
        cs.append(c)
        save()
        return shown(c, n)

    if path == "cli":
        if argv[:2] == ["issue", "comment"]:
            n = argv[2]
            body = body_given()
            if "--edit-last" in argv:
                mine = [c for c in comments_of(n) if c["login"] == "reza"]
                if not mine:
                    refuse("no comment to edit (HTTP 404)")
                mine[-1]["body"] = body
                save()
                print(shown(mine[-1], n)["url"])
                sys.exit(0)
            print(post(n, body)["url"])
            sys.exit(0)
        if argv[:2] == ["issue", "view"]:
            n = argv[2]
            i = {"number": int(n), "title": "Gallery", "body": "", "state": "OPEN",
                 "url": f"https://github.com/{GALLERY}/issues/{n}",
                 "comments": [shown(c, n) for c in comments_of(n)]}
            out(i)
        refuse("fake gallery does not answer this call (HTTP 400): " + " ".join(argv))
    explicit = opt(["-X", "--method"])
    fields = any(a in ("-f", "-F", "--field", "--raw-field", "--input") for a in argv)
    method = (explicit or ("POST" if fields else "GET")).upper()
    m = re.fullmatch(rf"repos/{GALLERY}/issues/(\d+)", path)
    if m and method == "GET":
        comments_of(m.group(1))
        out({"number": int(m.group(1)), "title": "Gallery", "state": "open"})
    m = re.fullmatch(rf"repos/{GALLERY}/issues/(\d+)/comments", path)
    if m and method == "GET":
        out([shown(c, m.group(1)) for c in comments_of(m.group(1))])
    if m and method == "POST":
        out(post(m.group(1), body_given()))
    m = re.fullmatch(rf"repos/{GALLERY}/issues/comments/(\d+)", path)
    if m:
        for n, cs in state["issues"].items():
            for c in cs:
                if str(c["id"]) == m.group(1):
                    if method == "GET":
                        out(shown(c, n))
                    if method == "PATCH":
                        c["body"] = body_given()
                        save()
                        out(shown(c, n))
        refuse("Not Found (HTTP 404)")
    refuse("fake gallery does not answer this call (HTTP 400): " + " ".join(argv))
'''


def write_call(argv):
    """The repo a logged `gh` call writes to, or None when the call only reads.

    `gh api` writes when its method is not GET (a field with no method means POST), or when it sends a GraphQL
    mutation; `gh issue`, `gh pr`, `gh label` and friends write unless they only view or list."""
    if argv[:1] == ["api"]:
        method = next((argv[i + 1] for i, a in enumerate(argv) if a in ("-X", "--method") and i + 1 < len(argv)), None)
        method = method or next((a.split("=", 1)[1] for a in argv if a.startswith("--method=")), None)
        fields = any(a in ("-f", "-F", "--field", "--raw-field", "--input") for a in argv)
        target = next((a.lstrip("/") for a in argv[1:] if a.lstrip("/").startswith("repos/")), "")
        if "graphql" in argv[1:2]:
            return REPO if "mutation" in " ".join(argv) else None
        if (method or ("POST" if fields else "GET")).upper() == "GET":
            return None
        return "/".join(target.split("/")[1:3]) or "?"
    if len(argv) >= 2 and argv[1] in ("view", "list", "status", "diff", "checks"):
        return None
    if argv[:1] in (["auth"], ["--version"], ["version"]):
        return None
    repo = next((argv[i + 1] for i, a in enumerate(argv) if a in ("-R", "--repo") and i + 1 < len(argv)), None)
    return repo or next((a.split("=", 1)[1] for a in argv if a.startswith("--repo=")), None) or "?"


@pytest.fixture(scope="module")
def place(tmp_path_factory):
    """Story 1's throwaway checkout and fake GitHub, with the gallery fake and an issue 11.

    The gallery fake sits in front of story 1's fake `gh`; issue 11 is a copy of issue 7."""
    base = tmp_path_factory.mktemp("preview")
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
    (bin_dir / "gh").write_text(FAKE_GALLERY + "\n" + rest)
    (bin_dir / "gh").chmod(0o755)
    w = story1.world()
    seven = w["issues"][str(ISSUE)]
    w["issues"][str(OTHER)] = {**seven, "number": OTHER, "title": "Another visual",
                               "url": f"https://github.com/{REPO}/issues/{OTHER}"}
    (base / "world.json").write_text(json.dumps(w))
    return {"repo": repo, "bin": bin_dir, "world": base / "world.json", "base": base}


def fresh(place, name):
    """A new gallery and a new call log, for one test.

    Gallery issue 3 starts with one plain note of the caller's."""
    gallery = place["base"] / f"{name}.gallery.json"
    gallery.write_text(json.dumps({"next": 500, "issues": {str(GALLERY_ISSUE): [
        {"id": 500, "body": NOTE, "login": "reza"}]}}))
    log = place["base"] / f"{name}.log"
    log.write_text("")
    return {**place, "gallery": gallery, "log": log}


def env_of(place):
    """The command's environment: the fake `gh` first on PATH, with this test's files."""
    env = {k: v for k, v in os.environ.items() if k not in ("DOKIMA_BOT", "GITHUB_REPOSITORY", "REPO")}
    env.update(PATH=f"{place['bin']}{os.pathsep}{env.get('PATH', '')}", VISUALS_WORLD=str(place["world"]),
               VISUALS_LOG=str(place["log"]), VISUALS_GALLERY=str(place["gallery"]))
    return env


def preview(place, number, branch, criterion, gallery_issue=GALLERY_ISSUE):
    """Run `preview` from the throwaway checkout's root; returns the finished process."""
    if not (place["repo"] / "tools" / "visuals.py").exists():
        pytest.fail(f"{criterion}: tools/visuals.py does not exist, so there is no command to preview with")
    return subprocess.run([sys.executable, "tools/visuals.py", "preview", str(number), "--branch", branch,
                           "--repo", REPO, "--gallery-issue", str(gallery_issue)],
                          cwd=place["repo"], env=env_of(place), capture_output=True, text=True, timeout=120)


def drawing(place, number, branch, criterion):
    """What `draw` prints for the issue and branch: the drawing a preview must post."""
    r = subprocess.run([sys.executable, "tools/visuals.py", "draw", str(number), "--branch", branch, "--repo", REPO],
                       cwd=place["repo"], env=env_of(place), capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"{criterion}: drawing #{number} from {branch} failed:\n{r.stdout}\n{r.stderr}"
    return r.stdout.strip()


def previewed(place, number, branch, criterion):
    """Preview the issue from the branch; fails the test when the command fails."""
    r = preview(place, number, branch, criterion)
    assert r.returncode == 0, \
        f"{criterion}: previewing #{number} from {branch} exited {r.returncode}:\n{r.stdout}\n{r.stderr}"
    return r


def comments(place):
    """The gallery issue's comments now, oldest first."""
    return json.loads(place["gallery"].read_text())["issues"][str(GALLERY_ISSUE)]


def calls(place):
    """Every `gh` call the command made, in order."""
    return [json.loads(line) for line in place["log"].read_text().splitlines() if line.strip()]


def test_preview_posts_one_comment(place, record_property):
    """The drawing shows as one comment on the gallery issue.

    Previews issue 7 from a branch with changed drawing code onto a gallery issue holding one note, and checks
    exactly one comment was added and it holds everything `draw` prints for that branch. Proves 625.1."""
    record_property("proves", "625.1")
    p = fresh(place, "posts")
    want = drawing(p, ISSUE, "visual-test", "625.1")
    previewed(p, ISSUE, "visual-test", "625.1")
    cs = comments(p)
    assert len(cs) == 2, f"625.1: expected the note and one preview on the gallery issue, found {len(cs)}:\n{cs}"
    assert cs[0]["body"] == NOTE, f"625.1: the note already on the gallery issue was changed:\n{cs[0]['body']}"
    assert want in cs[1]["body"], f"625.1: the gallery comment does not hold the drawing.\nWanted:\n{want}\n" \
                                  f"Posted:\n{cs[1]['body']}"
    assert "BRANCH-CARD" in cs[1]["body"] and PLAN_SUMMARY in cs[1]["body"], \
        f"625.1: the gallery comment is not the branch's drawing of the real issue:\n{cs[1]['body']}"


def test_preview_missing_gallery_issue_says_so(place, record_property):
    """A missing gallery issue ends the command with a plain message naming it.

    Previews onto gallery issue 404, which the fake gallery does not have, and checks the command fails naming the
    issue and GitHub's reason, with no traceback. Proves 625.1."""
    record_property("proves", "625.1")
    p = fresh(place, "missing")
    r = preview(p, ISSUE, "visual-test", "625.1", gallery_issue=404)
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"625.1: previewing onto a missing gallery issue did not fail:\n{said}"
    assert "#404" in said and "HTTP 404" in said, \
        f"625.1: the message does not name the gallery issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"625.1: a missing gallery issue crashed the command instead of saying why:\n{said}"


def test_preview_unreadable_issue_posts_nothing(place, record_property):
    """An issue GitHub cannot give posts nothing to the gallery and says why.

    Previews issue 8, which the fake GitHub refuses, and checks the command fails naming it and GitHub's reason,
    with no traceback, and the gallery issue still holds only its note. Proves 625.1."""
    record_property("proves", "625.1")
    p = fresh(place, "unreadable")
    r = preview(p, 8, "visual-test", "625.1")
    said = r.stdout + r.stderr
    assert r.returncode != 0, f"625.1: previewing an unreadable issue did not fail:\n{said}"
    assert "#8" in said and "HTTP 502" in said, f"625.1: the message does not name the issue and GitHub's reason:\n{said}"
    assert "Traceback" not in said, f"625.1: an unreadable issue crashed the command instead of saying why:\n{said}"
    assert [c["body"] for c in comments(p)] == [NOTE], \
        f"625.1: something was posted to the gallery for an issue that could not be drawn:\n{comments(p)}"


def test_preview_again_edits_same_comment(place, record_property):
    """A second preview of the same issue edits its comment instead of posting another.

    Previews issue 7 from the branch, then again from main, and checks the gallery issue still holds one preview,
    with the same comment id, now showing main's drawing and none of the branch's. Proves 625.2."""
    record_property("proves", "625.2")
    p = fresh(place, "again")
    previewed(p, ISSUE, "visual-test", "625.2")
    first = comments(p)
    assert len(first) == 2, f"625.2: the first preview did not add one comment:\n{first}"
    previewed(p, ISSUE, "main", "625.2")
    then = comments(p)
    assert len(then) == 2, f"625.2: the second preview posted another comment instead of editing:\n{then}"
    assert then[1]["id"] == first[1]["id"], f"625.2: the preview comment was replaced, not edited:\n{then}"
    want = drawing(p, ISSUE, "main", "625.2")
    assert want in then[1]["body"] and "BRANCH" not in then[1]["body"], \
        f"625.2: the edited comment does not show the new drawing:\n{then[1]['body']}"
    assert then[0]["body"] == NOTE, f"625.2: the note on the gallery issue was edited:\n{then[0]['body']}"


def test_preview_other_issue_gets_its_own_comment(place, record_property):
    """Each real issue keeps its own preview comment on a shared gallery issue.

    Previews issue 7, then issue 11, then issue 7 again from main, and checks the gallery issue holds the note and
    two previews: 11's left as it was, 7's edited to main's drawing. Proves 625.2."""
    record_property("proves", "625.2")
    p = fresh(place, "shared")
    previewed(p, ISSUE, "visual-test", "625.2")
    previewed(p, OTHER, "visual-test", "625.2")
    before = comments(p)
    assert len(before) == 3, f"625.2: two issues did not get a preview comment each:\n{before}"
    previewed(p, ISSUE, "main", "625.2")
    after = comments(p)
    assert len(after) == 3, f"625.2: previewing issue 7 again posted another comment:\n{after}"
    assert after[2] == before[2], f"625.2: previewing issue 7 edited issue 11's preview:\n{after[2]['body']}"
    assert after[0]["body"] == NOTE, f"625.2: the note on the gallery issue was edited:\n{after[0]['body']}"
    assert "BRANCH" not in after[1]["body"] and PLAN_SUMMARY in after[1]["body"], \
        f"625.2: issue 7's preview was not edited to main's drawing:\n{after[1]['body']}"


def test_preview_writes_nothing_here(place, record_property):
    """Previewing writes only to the gallery repo, never to this repo or the real issue.

    Logs every `gh` call of two previews of issue 7 (a post, then an edit) and checks each call that writes goes to
    the gallery repo, and that the gallery was in fact written to. Proves 625.3."""
    record_property("proves", "625.3")
    p = fresh(place, "nothing")
    previewed(p, ISSUE, "visual-test", "625.3")
    previewed(p, ISSUE, "main", "625.3")
    log = calls(p)
    here = [shlex.join(["gh", *c]) for c in log if write_call(c) not in (None, GALLERY)]
    assert not here, "625.3: previewing wrote outside the gallery repo:\n" + "\n".join(here)
    assert any(write_call(c) == GALLERY for c in log), \
        "625.3: no write reached the gallery repo, so this check proves nothing:\n" + \
        "\n".join(shlex.join(["gh", *c]) for c in log)


def test_failed_preview_writes_nothing_here(place, record_property):
    """A preview the gallery refuses still writes nothing to this repo.

    Previews onto a gallery issue that does not exist and checks no logged `gh` call wrote anywhere, so a refused
    gallery never falls back to the real issue. Proves 625.3."""
    record_property("proves", "625.3")
    p = fresh(place, "refused")
    r = preview(p, ISSUE, "visual-test", "625.3", gallery_issue=404)
    assert r.returncode != 0, f"625.3: previewing onto a missing gallery issue did not fail:\n{r.stdout}\n{r.stderr}"
    log = calls(p)
    assert any(GALLERY in " ".join(c) for c in log), \
        f"625.3: the command never asked the gallery repo, so this check proves nothing:\n{r.stdout}\n{r.stderr}"
    here = [shlex.join(["gh", *c]) for c in log if write_call(c) not in (None, GALLERY)]
    assert not here, "625.3: a refused preview wrote outside the gallery repo:\n" + "\n".join(here)

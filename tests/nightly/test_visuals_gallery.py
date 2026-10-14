"""Our drawing tool's checks against real GitHub: they read and post on the card gallery.

#626, criterion 626.2.

These checks call the real `gh`, as whoever runs them, so `tests/conftest.py` leaves them out of every run that does
not name `tests/nightly`: only the nightly workflow (`.github/workflows/visuals-nightly.yml`) runs them, with a GitHub
token that may write to the gallery repo. They never skip: when GitHub refuses a call, the check fails and its message carries GitHub's own reason.

1. The gallery issue can be read: `gh api` lists the comments of issue 1 of `dokima-dev/card-gallery`.
2. `tools/visuals.py preview` posts main's drawing of a real Dokima issue on that gallery issue, and the comment it
   names can be read back with its hidden marker on top.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GALLERY = "dokima-dev/card-gallery"
GALLERY_ISSUE = 1
REPO = "dokima-dev/dokima"
ISSUE = 584


def gh(*args):
    """`gh api` on real GitHub; fails the check with GitHub's reason when refused."""
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"GitHub refused `gh api {' '.join(args)}`: {' '.join((r.stderr or r.stdout).split())}"
    return r.stdout


def test_gallery_issue_can_be_read(record_property):
    """The gallery issue's comments can be read from real GitHub.

    Lists the comments of the gallery issue and checks GitHub answers with a list. Proves 626.2."""
    record_property("proves", "626.2")
    comments = json.loads(gh(f"repos/{GALLERY}/issues/{GALLERY_ISSUE}/comments", "--per-page", "1"))
    assert isinstance(comments, list), f"626.2: {GALLERY}#{GALLERY_ISSUE} answered with no list of comments: {comments!r}"


def test_preview_posts_on_gallery(record_property):
    """The command posts a real issue's drawing on the gallery, readable back.

    Runs `preview` with main's code on a real Dokima issue, then reads the comment whose link it printed and checks
    it starts with the marker naming that issue. Proves 626.2."""
    record_property("proves", "626.2")
    r = subprocess.run([sys.executable, "tools/visuals.py", "preview", str(ISSUE), "--branch", "main", "--repo", REPO,
                        "--gallery-issue", str(GALLERY_ISSUE)], cwd=ROOT, capture_output=True, text=True, timeout=600)
    said = " ".join((r.stderr + r.stdout).split())
    assert r.returncode == 0, f"626.2: preview of {REPO}#{ISSUE} on {GALLERY}#{GALLERY_ISSUE} failed: {said}"
    url = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    assert "#issuecomment-" in url, f"626.2: preview printed no comment link: {said}"
    comment = json.loads(gh(f"repos/{GALLERY}/issues/comments/{url.rsplit('-', 1)[1]}"))
    marker = f"<!-- visuals-preview: {REPO}#{ISSUE} -->"
    assert (comment.get("body") or "").startswith(marker + "\n"), \
        f"626.2: the gallery comment {url} does not start with {marker!r}"

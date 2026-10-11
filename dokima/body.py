"""The issue body: code's card above one marker, the owner's ask below, never rewritten.

Once planned, every ask sits folded under Original issue (#373). While an issue has no plan, the owner's own ask
shows open, with the card's Definition of Done after it, after its own marker (#371, #407); a split's story, quoted by
code from the parent's approved plan, stays folded with the Definition of Done after the fold (#237). Reading accepts
every layout, and the next redraw moves the ask to the one its card calls for.

Every code path that redraws an issue body (the card and the planner) saves it through `save`, which keeps the
owner's part byte for byte or refuses, leaves the body as it was and says why in a comment on the issue.
"""
import re
import subprocess

MARKER = "<!-- dokima-ask -->"
FOLD_START = "\n<details><summary>Original issue</summary>\n\n"
FOLD_END = "\n\n</details>"
OPEN_START = "\n\n"
DONE = "<!-- dokima-done -->"
# In a planned card: the owner's part stays folded, with the Definition of Done after the fold.
FOLDED = "<!-- dokima-folded -->"
TRAILER = "\n\n" + DONE + "\n"
# The head of a split's story, as agent.story_body quotes it from the parent's approved plan.
STORY = re.compile(r"<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #\d+, ")


class Refused(Exception):
    """A redraw that would change the owner's part; its message says why."""


def trailer(below):
    """`below` split into the owner's fold and the Definition of Done line after it.

    Only the last DONE marker counts, and only when one line follows it and the fold closes right before it, so the
    owner's own copy of the marker never ends their text early. The owner's part is folded, or open (#407)."""
    i = below.rfind(TRAILER)
    if i < 0 or "\n" in below[i + len(TRAILER):]:
        return below, ""
    folded = below[:i].endswith(FOLD_END) and below.startswith(FOLD_START) and i >= len(FOLD_START) + len(FOLD_END)
    if not folded and not below.startswith(OPEN_START):
        return below, ""
    return below[:i], below[i:]


def ask(body):
    """The owner's part below the first marker, byte for byte; the whole body when there is no marker yet."""
    body = body or ""
    if MARKER not in body:
        return body
    below = trailer(body.split(MARKER, 1)[1])[0]
    if below.startswith(FOLD_START) and below.endswith(FOLD_END) and len(below) >= len(FOLD_START) + len(FOLD_END):
        return below[len(FOLD_START):len(below) - len(FOLD_END)]
    if below.startswith(OPEN_START):
        return below[len(OPEN_START):]
    return below


def redraw(body, top):
    """The new body: `top` above the marker, the owner's part below; Refused if it changes.

    What `top` holds after its DONE marker (a card with no plan's Definition of Done) goes below the owner's part,
    which then shows open unless it is a split's story (#407); with a plan, the owner's part is folded."""
    body = body or ""
    owner = ask(body)
    top, done = top.split(DONE, 1) if DONE in top else (top, None)
    folded = STORY.match(owner) or FOLDED in top
    shown = OPEN_START + owner if done is not None and not folded else FOLD_START + owner + FOLD_END
    below = shown + ("" if done is None else TRAILER + done.strip("\n"))
    new = top.rstrip("\n") + "\n\n" + MARKER + below
    if ask(new) != ask(body) or new.split(MARKER, 1)[1] != below or (done is not None and not trailer(below)[1]):
        raise Refused("the owner's part below the marker would change: the new card holds the marker "
                      f"`{MARKER}` itself, so the owner's original ask would no longer read back as written")
    return new


def gh(*args, **kw):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, **kw).stdout


def save(repo, number, current, top):
    """Save `top` above the owner's part on issue `number` and return True; when refused, leave the body as it was,
    comment why on the issue and return False."""
    try:
        new = redraw(current, top)
    except Refused as e:
        gh("issue", "comment", str(number), "-R", repo, "--body",
           f"**Issue text not updated:** {e}. The issue text was left as it was.")
        print(f"::error title=Issue text not updated::{e}")
        return False
    gh("issue", "edit", str(number), "-R", repo, "--body-file", "-", input=new)
    return True

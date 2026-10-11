"""The issue body: code's card above one fixed marker, the owner's ask below it, never rewritten.

Issue #179. One helper, dokima/body.py, owns the issue body:

    MARKER                      the fixed marker that splits the body in two
    ask(body)                   the owner's part below the first marker, byte for byte (the whole body when there
                                is no marker yet)
    redraw(body, top)           the new body: `top` above the marker, the owner's part below it (open or folded: #237, tests/test_open_ask.py);
                                raises Refused(reason) when the owner's part would change
    save(repo, number, current, top)
                                saves redraw(current, top) on the issue and returns True, or, when refused,
                                leaves the body alone, comments the reason on the issue and returns False
    Refused                     the exception redraw raises, its message saying why

Every code path that redraws the issue body goes through it: the card (dokima/card.py main) and the planner's
post (dokima/planner.py render, saved by planner.main "post"). GitHub is faked in every test by a recorder standing in
for the `gh` calls; the planner's post runs inside a temp git repo holding the plan's tests, as a real run does.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import card, plan, planner  # noqa: E402

REPO = "o/r"
NUMBER = 40

# An owner's ask the card cannot read: Windows line ends, trailing spaces, blank lines at both ends, old plan
# checkboxes, a card marker, a stray closing fold, a quote and a "Not checked" line.
TRICKY = ("\r\n\r\nPlease make the card keep my words.  \r\n"
          "- [ ] Goal: an old goal\r\n"
          "  - [ ] Done when: an old criterion\r\n"
          "    Verified by: nothing\r\n"
          "<!-- dokima-card -->\r\n"
          "</details>\r\n"
          "> quoted line\r\n"
          "**Not checked:** speed.\r\n"
          "Ünïcødé — and a trailing blank line\r\n\r\n   ")

PLAN_TOP = ("- [ ] Objective: show a card\n"
            "  - [ ] Acceptance criteria: first thing works\n"
            "    Verified by: a test\n\n"
            "**Scope:**\n- `dokima/card.py`\n")


def helper(k):
    """The body helper, or a plain failure naming criterion k when it does not exist yet."""
    try:
        from dokima import body
    except ImportError:
        pytest.fail(f"{k}: dokima/body.py, the one helper that owns the issue body, does not exist yet")
    for name in ("MARKER", "ask", "redraw", "save", "Refused"):
        assert hasattr(body, name), f"{k}: dokima/body.py has no {name}"
    return body


def text_of(args, kw):
    """The text a faked gh call carries: --body, body=..., body=@file or --body-file (a file or stdin)."""
    for i, a in enumerate(args):
        if a in ("--body", "-b") and i + 1 < len(args):
            return args[i + 1]
        if a == "--body-file" and i + 1 < len(args):
            return kw.get("input") if args[i + 1] == "-" else open(args[i + 1], newline="").read()
        if a.startswith("body="):
            v = a[len("body="):]
            if v.startswith("@"):
                return kw.get("input") if v == "@-" else open(v[1:], newline="").read()
            return v
    return kw.get("input")


class FakeGitHub:
    """Stands in for every gh call: records saves of the issue body and comments on the issue."""

    def __init__(self):
        self.saves, self.comments, self.calls = [], [], []
        self.body = ""

    def __call__(self, *args, **kw):
        args = [str(a) for a in args]
        self.calls.append(args)
        is_comment = "comment" in args or any(a.endswith(f"issues/{NUMBER}/comments") for a in args)
        is_save = not is_comment and ("PATCH" in args or "edit" in args) and \
            any(a == str(NUMBER) or a.endswith(f"issues/{NUMBER}") for a in args)
        if is_comment:
            self.comments.append((args, text_of(args, kw)))
        elif is_save:
            self.saves.append(text_of(args, kw))
        elif "view" in args:
            return self.body
        return "{}"


@pytest.fixture
def github(monkeypatch, tmp_path):
    """A faked GitHub for the body helper and the card, run in a temp folder."""
    fake = FakeGitHub()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    try:
        from dokima import body
        monkeypatch.setattr(body, "gh", fake, raising=False)
    except ImportError:
        pass
    monkeypatch.setattr(card, "gh", fake)
    monkeypatch.setattr(planner, "gh", fake)
    return fake


def run_card(monkeypatch, github, current):
    """Run the card's main on an issue whose body is `current`, with no PR and no worker run; the saved body or None."""
    issue = {"number": NUMBER, "title": "t", "url": f"https://github.com/{REPO}/issues/{NUMBER}", "approved_at": None,
             "changes": [], "plan": plan.parse(current), "current_body": current, "body": current}
    monkeypatch.setattr(card, "find_work", lambda repo: (NUMBER, None))
    monkeypatch.setattr(card, "latest_worker_run", lambda repo, n: None)
    monkeypatch.setattr(plan, "fetch_issue", lambda repo, n: issue)
    # The card is drawn from the agents' records (#180): the plan record holds the same criterion as PLAN_TOP.
    planned = {"role": "planner", "stage": None, "check": {"passed": True}, "run": "https://github.com/o/r/actions/runs/1",
               "handback": {"kind": "user_story", "user_story": "Owners see a card.", "non_functional": [],
                            "acceptance_criteria": [{"text": "first thing works", "source": issue["url"]}],
                            "scope": ["dokima/card.py"], "out_of_scope": [], "tests": {}}}
    found = {"recs": [planned], "pr": None, "check_runs": [], "reviews": [], "owners": set(), "tests": {}, "worker": None}
    monkeypatch.setattr(card, "gather", lambda repo, n, pr: found, raising=False)
    before = len(github.saves)
    try:
        card.main()
    except (SystemExit, Exception):
        pass
    return github.saves[-1] if len(github.saves) > before else None


REASON = "the owner's part below the marker would change"

PLAN_TESTS = ('def test_card(record_property):\n    """The card shows.\n\n    Proves 40.1.\n    """\n'
              '    record_property("proves", "40.1")\n    assert False\n')
PLAN = {"kind": "user_story", "summary": "Every issue shows a card.", "user_story": "Owners see a card on every issue.",
        "acceptance_criteria": [{"text": "The issue shows a card on top.", "source": f"https://github.com/{REPO}/issues/{NUMBER}"}],
        "non_functional": [], "scope": ["dokima/card.py"], "out_of_scope": [],
        "tests": {"40.1": ["tests/test_cardshow.py::test_card"]}, "test_changes": {}}


def run_planner_post(monkeypatch, tmp_path, github, current):
    """Run the planner's post, as the planner workflow does, on an issue whose body is `current`.

    Builds a temp git repo whose planner run added one named test, hands back a good plan for issue #40, and runs
    planner.main "post" against the faked GitHub. Returns what the run raised, or None; GitHub's record holds the rest.
    """
    repo, out = tmp_path / "repo", tmp_path / "out"
    repo.mkdir(parents=True)
    out.mkdir(parents=True)
    git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, text=True).stdout
    git("init", "-q")
    git("config", "user.name", "t")
    git("config", "user.email", "t@t")
    (repo / "README.md").write_text("repo\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").strip()
    monkeypatch.setenv("PLANNER_BASE", base)
    monkeypatch.setenv("PLANNER_RUN_BASE", base)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_cardshow.py").write_text(PLAN_TESTS)
    (out / "plan.json").write_text(json.dumps(PLAN))
    monkeypatch.chdir(repo)
    github.body = current
    try:
        planner.main(["x", "post", str(NUMBER), str(out)])
    except (SystemExit, Exception) as e:
        return e
    return None


def refuse(monkeypatch, body):
    """Make the helper find that the owner's part would change, so every redraw through it is refused."""
    def refused(current, top):
        raise body.Refused(REASON)
    monkeypatch.setattr(body, "redraw", refused)


# 179.1: two parts split by one fixed marker, the card above, the owner's ask below

def test_the_marker_is_the_same_after_every_redraw(record_property):
    """The marker is one fixed string: every redraw leaves exactly that one marker, never a second.

    Redraws the same issue three times with different cards and checks the body always holds the marker once."""
    record_property("proves", "179.1")
    body = helper("179.1")
    current = "Fresh ask."
    for k in range(3):
        current = body.redraw(current, f"card number {k}")
        assert current.count(body.MARKER) == 1, f"179.1: redraw {k + 1} left {current.count(body.MARKER)} markers"
        assert current.split(body.MARKER)[0].strip() == f"card number {k}", f"179.1: redraw {k + 1} kept an old card above"


def test_the_card_writes_its_card_above_the_marker(record_property, monkeypatch, github):
    """When the card is drawn on an issue, the card sits at the top and the owner's ask below the marker.

    Runs the card's main on an issue that already has a plan above the marker, and checks the saved body starts with
    the card, shows the plan's criterion, and keeps the ask folded below the one marker."""
    record_property("proves", "179.1")
    body = helper("179.1")
    current = body.redraw("Please show a card.", PLAN_TOP)
    saved = run_card(monkeypatch, github, current)
    assert saved is not None, "179.1: the card saved nothing on the issue"
    assert saved.startswith(plan.CARD_START), "179.1: the card is not at the top of the issue"
    assert saved.count(body.MARKER) == 1, "179.1: the saved body does not have exactly one marker"
    above = saved.split(body.MARKER)[0]
    assert "first thing works" in above and plan.CARD_END in above, "179.1: the card above the marker lost the plan"
    assert body.ask(saved) == "Please show a card.", "179.1: the owner's ask is not below the marker as written"


# 179.2: every redraw changes only the part above the marker; the owner's part is byte-for-byte the same

def test_owner_part_is_byte_for_byte_the_same_after_many_redraws(record_property):
    """The owner's part never changes, however many times code redraws, even text the card cannot read.

    Redraws an ask full of Windows line ends, trailing spaces, old checkboxes and stray markup five times with
    different cards, and checks the ask and every byte below the marker stay identical."""
    record_property("proves", "179.2")
    body = helper("179.2")
    current = body.redraw(TRICKY, "first card")
    below = current.split(body.MARKER, 1)[1]
    for k in range(5):
        current = body.redraw(current, f"card {k}\n- [ ] Objective: goal {k}")
        assert body.ask(current) == TRICKY, f"179.2: redraw {k + 1} changed the owner's ask"
        assert current.split(body.MARKER, 1)[1] == below, f"179.2: redraw {k + 1} changed the part below the marker"
        assert current.split(body.MARKER, 1)[0].startswith(f"card {k}"), f"179.2: redraw {k + 1} did not change the part above"


def test_the_card_never_changes_the_owner_part(record_property, monkeypatch, github):
    """Redrawing the card again and again leaves the owner's part byte for byte as it was.

    Runs the card's main three times on an issue with an ask the card cannot read, each time on the body it saved
    before, and checks the ask and every byte below the marker never change."""
    record_property("proves", "179.2")
    body = helper("179.2")
    current = body.redraw(TRICKY, PLAN_TOP)
    current = run_card(monkeypatch, github, current)  # the first real redraw moves Done below the fold (#416)
    below = current.split(body.MARKER, 1)[1]
    for k in range(3):
        # Every change now redraws (#438), so a run that finds the card current may save nothing and keeps the body.
        saved = run_card(monkeypatch, github, current)
        assert saved is not None or k > 0, "179.2: the first card run saved nothing"
        saved = current if saved is None else saved
        assert body.ask(saved) == TRICKY, f"179.2: card run {k + 1} changed the owner's ask"
        assert saved.split(body.MARKER, 1)[1] == below, f"179.2: card run {k + 1} changed the part below the marker"
        assert "first thing works" in saved.split(body.MARKER, 1)[0], f"179.2: card run {k + 1} lost the plan above"
        current = saved
    assert not github.comments, "179.2: a good redraw was refused"


def test_replanning_never_changes_the_owner_part(record_property):
    """Writing a plan into the issue, again and again, leaves the owner's part byte for byte as it was.

    Runs the planner's render three times on an issue with an ask the card cannot read, and checks the ask and every
    byte below the marker never change while the plan above it does."""
    record_property("proves", "179.2")
    body = helper("179.2")
    story = {"objective": "Slow calls return a job id", "criteria": ["A slow call returns a job id within 20 s"],
             "non_goals": [], "scope": ["dokima/jobs.py"], "test_changes": {}}
    current = planner.render("9", TRICKY, story, {})
    below = current.split(body.MARKER, 1)[1] if body.MARKER in current else None
    assert body.ask(current) == TRICKY, "179.2: the first plan changed the owner's ask"
    for k in range(3):
        current = planner.render("9", current, dict(story, objective=f"Plan {k}"), {})
        assert current.count(body.MARKER) == 1, f"179.2: re-plan {k + 1} does not have exactly one marker"
        assert body.ask(current) == TRICKY, f"179.2: re-plan {k + 1} changed the owner's ask"
        assert current.split(body.MARKER, 1)[1] == below, f"179.2: re-plan {k + 1} changed the part below the marker"
        assert f"Plan {k}" in current.split(body.MARKER, 1)[0], f"179.2: re-plan {k + 1} did not write the plan above"


# 179.3: when the owner's part would change, code refuses, says why on the issue, and leaves the body alone

def test_a_redraw_that_would_change_the_owner_part_is_refused(record_property):
    """A redraw that would move the owner's words is refused with a reason, and a good one goes through.

    Draws a card that itself contains the marker, which would push part of the card into the owner's part, and
    checks the redraw is refused with a reason; the same card without it redraws fine."""
    record_property("proves", "179.3")
    body = helper("179.3")
    current = body.redraw("My ask.", "old card")
    with pytest.raises(body.Refused) as refused:
        body.redraw(current, f"a card that quotes {body.MARKER} in a criterion")
    assert str(refused.value).strip(), "179.3: the refusal gives no reason"
    assert body.ask(body.redraw(current, "a card that quotes nothing")) == "My ask.", "179.3: a good redraw was refused"


def test_a_refused_save_leaves_the_body_and_comments_why(record_property, github):
    """When the owner's part would change, nothing is saved and the issue gets a comment saying why.

    Saves a card that contains the marker: checks the body is never written, one comment carrying the reason is posted
    on the issue and the save reports False; then saves a good card and checks it is written with no comment."""
    record_property("proves", "179.3")
    body = helper("179.3")
    current = body.redraw("My ask.", "old card")
    bad = f"a card that quotes {body.MARKER}"
    with pytest.raises(body.Refused) as refused:
        body.redraw(current, bad)
    assert body.save(REPO, NUMBER, current, bad) is False, "179.3: a refused save did not report False"
    assert github.saves == [], "179.3: the body was written although the owner's part would change"
    assert len(github.comments) == 1, f"179.3: expected one comment saying why, got {len(github.comments)}"
    assert str(refused.value) in (github.comments[0][1] or ""), "179.3: the comment does not say why the save was refused"
    assert body.save(REPO, NUMBER, current, "good card") is True, "179.3: a good save did not report True"
    assert github.saves == [body.redraw(current, "good card")], "179.3: a good save did not write the redrawn body"
    assert len(github.comments) == 1, "179.3: a good save posted a refusal"


def test_the_card_refuses_rather_than_change_the_owner_part(record_property, monkeypatch, github):
    """The card never saves a body that would change the owner's part; it comments why instead.

    Runs the card's main on an issue where the helper finds the owner's part would change, and checks the body is not
    written and the issue gets a comment carrying the helper's reason."""
    record_property("proves", "179.3")
    body = helper("179.3")
    current = body.redraw("My ask.", PLAN_TOP)
    refuse(monkeypatch, body)
    saved = run_card(monkeypatch, github, current)
    assert saved is None, "179.3: the card saved a body that changes the owner's part"
    assert github.comments, "179.3: the card refused silently, with no comment on the issue"
    assert REASON in (github.comments[0][1] or ""), "179.3: the card's comment does not say why it refused"


# 179.4: a fresh ask with no marker gets the marker on its first redraw, the whole body kept below it

def test_a_fresh_ask_gets_the_marker_and_keeps_the_whole_body(record_property):
    """An issue with no marker yet gets one on its first redraw, with its whole body kept below as the owner's ask.

    Redraws three bodies with no marker (plain words, an ask the card cannot read, and a body that already carries an
    empty card) and checks each gets exactly one marker with the whole body, byte for byte, below it."""
    record_property("proves", "179.4")
    body = helper("179.4")
    story = "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From #1</summary>\n\nA story.\n\n</details>\n"
    for fresh in ("Please add a card.", TRICKY, story):
        new = body.redraw(fresh, "the card")
        assert new.count(body.MARKER) == 1, f"179.4: a fresh ask got {new.count(body.MARKER)} markers"
        assert new.split(body.MARKER)[0].strip() == "the card", "179.4: the card is not alone above the marker"
        assert body.ask(new) == fresh, "179.4: the whole existing body was not kept below the marker as written"
        assert fresh in new.split(body.MARKER)[1], "179.4: the existing body is not below the marker"


def test_the_card_adds_the_marker_to_a_fresh_ask(record_property, monkeypatch, github):
    """The first card drawn on a fresh issue adds the marker and keeps the whole ask below it.

    Runs the card's main on an issue with no marker and checks the saved body has the card on top, one marker, and
    the whole original body, byte for byte, as the owner's ask."""
    record_property("proves", "179.4")
    body = helper("179.4")
    saved = run_card(monkeypatch, github, TRICKY)
    assert saved is not None, "179.4: the card saved nothing on a fresh issue"
    assert saved.startswith(plan.CARD_START), "179.4: the card is not at the top of a fresh issue"
    assert saved.count(body.MARKER) == 1, "179.4: a fresh issue did not get exactly one marker"
    assert body.ask(saved) == TRICKY, "179.4: the fresh issue's whole body was not kept as the owner's ask"


def test_a_first_plan_adds_the_marker_to_a_fresh_ask(record_property):
    """The first plan written into a fresh issue adds the marker and keeps the whole ask below it.

    Runs the planner's render on an issue with no marker and checks one marker and the whole original body, byte
    for byte, as the owner's ask."""
    record_property("proves", "179.4")
    body = helper("179.4")
    story = {"objective": "Slow calls return a job id", "criteria": ["A slow call returns a job id within 20 s"],
             "non_goals": [], "scope": ["dokima/jobs.py"], "test_changes": {}}
    new = planner.render("9", TRICKY, story, {})
    assert new.count(body.MARKER) == 1, "179.4: the first plan did not add exactly one marker"
    assert body.ask(new) == TRICKY, "179.4: the first plan did not keep the whole body as the owner's ask"


# 179.5: a refused save always says why on the issue, never only in a log

def test_a_refusal_is_a_comment_on_the_issue(record_property, github, capsys):
    """A refused save always lands as a comment on the issue itself, not only in the run's log.

    Saves a card that would change the owner's part and checks a comment is posted to this issue's number, with the
    reason in it."""
    record_property("proves", "179.5")
    body = helper("179.5")
    current = body.redraw("My ask.", "old card")
    body.save(REPO, NUMBER, current, f"bad {body.MARKER}")
    assert len(github.comments) == 1, "179.5: the refusal was not posted on the issue"
    args, text = github.comments[0]
    assert any(a == str(NUMBER) or f"issues/{NUMBER}/" in a for a in args), "179.5: the refusal was posted somewhere other than this issue"
    assert (text or "").strip(), "179.5: the refusal comment is empty"


def test_the_card_posts_its_refusal_on_the_issue(record_property, monkeypatch, github):
    """When the card refuses to save, the reason is a comment on the issue, not only a line in the log.

    Runs the card's main where the save would change the owner's part and checks one non-empty comment is posted to
    this issue."""
    record_property("proves", "179.5")
    body = helper("179.5")
    current = body.redraw("My ask.", PLAN_TOP)
    refuse(monkeypatch, body)
    run_card(monkeypatch, github, current)
    assert len(github.comments) == 1, f"179.5: expected one refusal comment on the issue, got {len(github.comments)}"
    args, text = github.comments[0]
    assert any(a == str(NUMBER) or f"issues/{NUMBER}/" in a for a in args), "179.5: the refusal was posted somewhere other than this issue"
    assert (text or "").strip(), "179.5: the refusal comment is empty"


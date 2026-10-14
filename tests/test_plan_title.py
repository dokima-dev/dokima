"""#543: the planner names the issue, and each approved plan sets that title.

The planner's plan.json carries a `title`, held to the same word cap and plain-words rule as a story's title (ten
words, no code). The plan check (`python3 -m dokima.planner check N OUT`) rejects a plan without one, or with one that
breaks those rules. When the plan review approves a plan, `python3 -m dokima.agent next N OUT` sets the issue's title
to the plan's title, and again on every approved re-plan. The owner's original title stays visible in the issue's
Original issue fold, which card.yml's redraw (`python3 dokima/card.py`) draws.

The approval tests reuse the fake GitHub of tests/test_plan_links_recorded.py, taught here to change an issue's title
as GitHub does, through `gh api -X PATCH repos/o/r/issues/N -f title=...` or `gh issue edit N --title ...`.
"""
import json
import os
import re
import subprocess
import sys

import test_plan_links_recorded as tpl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import body  # noqa: E402

OLD_PATCH = '''        if method == "PATCH":
            if "body" not in f:
                fail(f"fake gh: no such call {a}")
            issue(n)["body"] = f["body"]
            write({"op": "body", "issue": n})
            save()
'''
NEW_PATCH = '''        if method == "PATCH":
            if "body" not in f and "title" not in f:
                fail(f"fake gh: no such call {a}")
            if "body" in f:
                issue(n)["body"] = f["body"]
                write({"op": "body", "issue": n})
            if "title" in f:
                issue(n)["title"] = f["title"]
                write({"op": "title", "issue": n})
            save()
'''
OLD_EDIT = '''if a[:2] == ["issue", "edit"]:
    n = number(a[2])
    text = flag("--body")
'''
NEW_EDIT = '''if a[:2] == ["issue", "edit"] and flag("--title") is not None:
    n = number(a[2])
    issue(n)["title"] = flag("--title")
    write({"op": "title", "issue": n})
    if flag("--body") is None and flag("--body-file") is None:
        save()
        sys.exit(0)
if a[:2] == ["issue", "edit"]:
    n = number(a[2])
    text = flag("--body")
'''
ORIGINAL = "Record the links"  # the owner's own title of the fake issue, as tests/test_plan_links_recorded.py files it


class Hub(tpl.Hub):
    """The fake GitHub of tests/test_plan_links_recorded.py, which can also change an issue's title."""

    def __init__(self, tmp, **kw):
        super().__init__(tmp, **kw)
        assert OLD_PATCH in tpl.FAKE_GH and OLD_EDIT in tpl.FAKE_GH, \
            "test setup: the fake GitHub of tests/test_plan_links_recorded.py changed; update this test's patch of it"
        fake = tpl.FAKE_GH.replace(OLD_PATCH, NEW_PATCH).replace(OLD_EDIT, NEW_EDIT)
        open(os.path.join(self.dir, "bin", "gh"), "w").write(
            f"#!{sys.executable}\nBOT_LOGIN = {tpl.BOT!r}\nOWNER_LOGIN = {tpl.OWNER!r}\n" + fake)

    def title(self, n=tpl.N):
        """Issue #n's title as it stands on GitHub."""
        return self.load()["issues"][str(n)]["title"]

    def approve_titled(self, title, verdict="approve"):
        """Post a plan with this title (none when None), then run `next` on its review."""
        extra = {} if title is None else {"title": title}
        self.post(tpl.plan(tpl.links(), **extra))
        rec = tpl.review(verdict)
        self.next(rec)
        self.post(rec)
        self.redraw(tpl.N)


def original_fold(text):
    """The Original issue fold of an issue body, summary and contents; None without one."""
    for summary, inside in re.findall(r"<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>", text, re.S):
        if "Original issue" in summary:
            return summary + "\n" + inside
    return None


# 543.1 ---------------------------------------------------------------------------------------------------------------

def plan_json(**title):
    """A well-formed one-criterion plan of issue #543, with the given title, if any."""
    return {"kind": "user_story", "summary": "The issue gets a readable title.",
            "user_story": "Owners read a plain title on every planned issue.",
            "acceptance_criteria": [{"text": "Approving a plan sets the issue's title.",
                                     "source": "https://github.com/o/r/issues/543",
                                     "no_edge_cases": "One plain step.", "files": ["dokima/agent.py"]}],
            "non_functional": [], "tests": {"543.1": ["tests/test_a.py::test_a"]},
            "test_changes": {}, "links": {"blocked_by": [], "blocks": [], "relates_to": []}, **title}


def title_problems(tmp_path, name, plan):
    """Run the plan check on PLAN and return what its rejection says about the title.

    The repo holds one committed test, so the check sees no new tests; any other problem it names is about the
    rest of the plan, so only the parts that mention the title are returned."""
    repo = tmp_path / name
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_a.py").write_text('def test_a():\n    """A test."""\n')
    git = lambda *a: subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                    check=True, capture_output=True)
    git("init", "-q")
    git("add", "-A")
    git("commit", "-qm", "start")
    out = tmp_path / f"{name}-out"
    out.mkdir()
    (out / "plan.json").write_text(json.dumps(plan))
    env = {k: v for k, v in os.environ.items() if k not in ("STYLE_SOFT", "PACK", "PLANNER_BASE", "PLANNER_RUN_BASE")}
    env.update(PYTHONPATH=ROOT, GITHUB_REPOSITORY="o/r", GITHUB_SERVER_URL="https://github.com")
    p = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "543", str(out)], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=60)
    assert "Traceback" not in p.stderr, f"test setup: the plan check crashed: {p.stderr[-2000:]}"
    rejected = out / "rejected.txt"
    why = rejected.read_text() if rejected.exists() else ""
    return [part for part in why.split("; ") if "title" in part.lower()]


def test_a_plan_passes_its_check_only_with_a_short_plain_title(tmp_path, record_property):
    """A missing, too long or code-naming title is rejected; a short plain one passes.

    Runs the real plan check on four plans that differ only in their title, and reads what the check says about
    the title: nothing for "Links show on both issues", a problem for each of the other three. Proves 543.1."""
    record_property("proves", "543.1")
    good = title_problems(tmp_path, "good", plan_json(title="Links show on both issues"))
    assert not good, f"543.1: a plain title of five words was rejected: {good}"
    missing = title_problems(tmp_path, "missing", plan_json())
    assert missing, "543.1: a plan with no title passed its check; the planner must hand back a title"
    long = title_problems(tmp_path, "long", plan_json(title=" ".join(["word"] * 11)))
    assert long, "543.1: a title of eleven words passed its check; a title holds ten words at most"
    code = title_problems(tmp_path, "code", plan_json(title="Fix the redraw in `card.py`"))
    assert code, "543.1: a title naming code passed its check; a title is plain words only"


# 543.2 ---------------------------------------------------------------------------------------------------------------

def test_each_approved_plan_sets_the_issue_title(tmp_path, record_property):
    """Each time a plan review approves a plan, the issue's title becomes that plan's title.

    On a fake GitHub: an approved plan with no title, and a blocked plan with one, leave the owner's title alone;
    an approved plan renames the issue, and an approved re-plan renames it again. Proves 543.2."""
    record_property("proves", "543.2")
    hub = Hub(tmp_path)
    hub.approve_titled(None)
    assert hub.title() == ORIGINAL, f"543.2: an approved plan with no title renamed the issue to {hub.title()!r}"
    hub.approve_titled("Blocked plans keep the old title", verdict="block")
    assert hub.title() == ORIGINAL, f"543.2: a blocked plan renamed the issue to {hub.title()!r}"
    hub.approve_titled("Links show on both issues")
    assert hub.title() == "Links show on both issues", \
        f"543.2: the approved plan's title was not set on the issue; its title is {hub.title()!r}"
    hub.approve_titled("Links show on every linked issue")
    assert hub.title() == "Links show on every linked issue", \
        f"543.2: the approved re-plan's title was not set on the issue; its title is {hub.title()!r}"


# 543.3 ---------------------------------------------------------------------------------------------------------------

def test_the_original_issue_fold_shows_the_owners_title(tmp_path, record_property):
    """Once a plan renames the issue, its Original issue fold shows the owner's title.

    On a fake GitHub, approves a titled plan and redraws the card as card.yml does, then approves a re-plan with
    another title and redraws again. Each time the fold shows the owner's first title, not a plan's, and the
    owner's ask reads back exactly as written. Proves 543.3."""
    record_property("proves", "543.3")
    hub = Hub(tmp_path)
    for title in ("Links show on both issues", "Links show on every linked issue"):
        hub.approve_titled(title)
        text = hub.body(tpl.N)
        fold = original_fold(text)
        assert fold is not None, "543.3: the planned issue has no Original issue fold"
        assert ORIGINAL in fold, \
            f"543.3: after approving the plan titled {title!r} the Original issue fold does not show the owner's title {ORIGINAL!r}"
        assert body.ask(text) == tpl.ASK, "543.3: the owner's ask no longer reads back exactly as written"

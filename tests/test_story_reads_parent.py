"""Every role reads the parent's ask; the owner's commits count as words (#708).

A story split from a parent holds a planner's text, not the owner's. Before #708 only the planner's starting pack held
the parent's original issue and the owner's comments on it (owner_words.json); the worker and the reviewers worked
from the story alone. These tests build each role's starting pack the way a run does, with GitHub faked in one place
(`dokima.agent_github.gh`), and look for the parent's words in any file of the pack, so the file's name and shape are
the worker's choice.

The last test fakes an owner's commit on the issue's branch, try/issue-7, and checks the planner's hand-back check
accepts a criterion quoting the committed text with the commit's link as its source. GitHub answers the branch's
commits the ways the API offers: `repos/o/r/compare/BASE...try/issue-7`, `repos/o/r/commits?sha=try/issue-7` and each
commit's own `repos/o/r/commits/SHA`, which carries its author's login and its files' patches.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent  # noqa: E402
from dokima import agent_github  # noqa: E402
from dokima import planner  # noqa: E402
import record_seed  # noqa: E402

N, PARENT, OWNER = 9, 5, "boss"
PARENT_ASK = "Every story keeps the detail of the parent, word for word."
OWNER_ON_PARENT = "Keep the old card for one week after the switch."
STORY_BODY = ("<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #5, story 1"
              "</summary>\n\nPlanner text for the story.\n</details>")
STORY = {"kind": "user_story", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/5"}],
         "non_functional": [], "tests": {"9.1": ["tests/test_x.py::test_a"]}}
REVIEW_OK = {"verdict": "approve", "summary": "s", "blockers": [], "asks": []}


def rec(role, stage="", handback=None, run_id="1"):
    """A passed record built the way the workflow builds one, from a temp hand-back folder."""
    out = tempfile.mkdtemp()
    json.dump(handback or {}, open(os.path.join(out, agent.HANDBACK[role]), "w"))
    return agent.build_record(role, stage, out, "", True, {"run_id": run_id, "run": f"https://x/run/{run_id}"})


STORY_COMMENTS = [{"author": {"login": OWNER}, "body": "/work", "createdAt": "2026-10-07T09:00:00Z",
                   "url": "https://github.com/o/r/issues/9#issuecomment-90"}]


def fake_github(monkeypatch, recs, story_comments=STORY_COMMENTS):
    """Fake GitHub: story 9 is split from issue 5, which the owner commented on."""
    parent_comments = [
        {"author": {"login": OWNER}, "body": OWNER_ON_PARENT, "createdAt": "2026-10-01T10:00:00Z",
         "url": "https://github.com/o/r/issues/5#issuecomment-55"},
        {"author": {"login": "passerby"}, "body": "Nice idea.", "createdAt": "2026-10-01T11:00:00Z",
         "url": "https://github.com/o/r/issues/5#issuecomment-56"}]

    def gh(*args):
        if args[:2] == ("issue", "view") and str(args[2]) == str(PARENT):
            return json.dumps({"number": PARENT, "title": "Parent", "body": PARENT_ASK, "comments": parent_comments})
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": N, "title": "Story", "body": STORY_BODY, "comments": story_comments})
        if args[:2] in (("pr", "list"), ("issue", "list")):
            return "[]"
        if args[:2] == ("run", "download"):
            os.makedirs(args[args.index("-D") + 1], exist_ok=True)
            return ""
        if args[0] == "api" and re.match(r"/?repos/o/r/issues/9/parent$", args[1]):
            return json.dumps({"number": PARENT})
        if args[0] == "api" and re.match(r"/?repos/o/r/issues/5/parent$", args[1]):
            raise subprocess.CalledProcessError(1, ["gh", *args], "", "HTTP 404: Not Found")
        if args[0] == "api" and re.match(r"/?repos/o/r/issues/5/sub_issues", args[1]):
            return json.dumps([{"number": N, "state": "open"}])
        if args[0] == "api" and re.match(r"/?repos/o/r/issues(\?|$)", args[1]):
            return "[]"
        raise AssertionError(f"unexpected GitHub call: gh {' '.join(map(str, args))}")
    monkeypatch.setattr(agent_github, "gh", gh)
    monkeypatch.setenv("OWNERS", OWNER)
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    record_seed.use(monkeypatch, N, recs)


def pack_text(dest):
    """Every file of the starting pack as one text, whatever file holds the words."""
    parts = []
    for root, _, names in os.walk(dest):
        for name in names:
            try:
                parts.append(open(os.path.join(root, name), encoding="utf-8").read())
            except (OSError, UnicodeDecodeError):
                continue
    return "\n".join(parts)


def worker_pack(monkeypatch, tmp_path):
    """The worker's starting pack for story 9, built after its plan was approved."""
    fake_github(monkeypatch, [rec("planner", handback=STORY), rec("reviewer", "plan", REVIEW_OK, run_id="2")])
    dest = str(tmp_path / "worker")
    agent.pack("o/r", N, "worker", "", dest)
    return dest


def reviewer_packs(monkeypatch, tmp_path):
    """The plan reviewer's and the code reviewer's starting packs for story 9, by stage."""
    recs = [rec("planner", handback=STORY), rec("reviewer", "plan", REVIEW_OK, run_id="2"),
            rec("worker", handback={"summary": "s"}, run_id="3")]
    out = {}
    for stage in ("plan", "pr"):
        fake_github(monkeypatch, recs)
        out[stage] = str(tmp_path / f"reviewer-{stage}")
        agent.pack("o/r", N, "reviewer", stage, out[stage])
    return out


def test_a_worker_on_a_split_story_finds_the_parents_original_issue(record_property, monkeypatch, tmp_path):
    """The worker's starting pack holds the parent's original issue, word for word.

    Builds the worker's pack for a story split from issue 5, with GitHub faked, and looks for the parent's ask, word for
    word, in every file of the pack. Proves 708.1."""
    record_property("proves", "708.1")
    text = pack_text(worker_pack(monkeypatch, tmp_path))
    assert PARENT_ASK in text, "708.1: the worker's starting pack does not hold the parent's original issue"


def test_a_worker_on_a_split_story_finds_the_owners_comments_on_the_parent(record_property, monkeypatch, tmp_path):
    """The worker's starting pack holds the owner's comment on the parent, word for word.

    Builds the worker's pack for a story split from issue 5, whose owner commented on it, and looks for that comment,
    word for word, in every file of the pack. Proves 708.2."""
    record_property("proves", "708.2")
    text = pack_text(worker_pack(monkeypatch, tmp_path))
    assert OWNER_ON_PARENT in text, "708.2: the worker's starting pack does not hold the owner's comment on the parent"


def test_a_reviewer_on_a_split_story_finds_the_parents_original_issue(record_property, monkeypatch, tmp_path):
    """Both reviewers' starting packs hold the parent's original issue, word for word.

    Builds the plan reviewer's and the code reviewer's packs for a story split from issue 5, with GitHub faked, and
    looks for the parent's ask, word for word, in every file of each pack. Proves 708.3."""
    record_property("proves", "708.3")
    for stage, dest in reviewer_packs(monkeypatch, tmp_path).items():
        assert PARENT_ASK in pack_text(dest), \
            f"708.3: the {stage} reviewer's starting pack does not hold the parent's original issue"


def test_a_reviewer_on_a_split_story_finds_the_owners_comments_on_the_parent(record_property, monkeypatch, tmp_path):
    """Both reviewers' starting packs hold the owner's comment on the parent, word for word.

    Builds the plan reviewer's and the code reviewer's packs for a story split from issue 5, whose owner commented on
    it, and looks for that comment, word for word, in every file of each pack. Proves 708.4."""
    record_property("proves", "708.4")
    for stage, dest in reviewer_packs(monkeypatch, tmp_path).items():
        assert OWNER_ON_PARENT in pack_text(dest), \
            f"708.4: the {stage} reviewer's starting pack does not hold the owner's comment on the parent"


OWNER_LINE = "Cards fold the long text under a toggle."
STRANGER_LINE = "Cards show every word at once."
COMMITS = {
    "abc123": {"login": OWNER, "line": OWNER_LINE},
    "def456": {"login": "stranger", "line": STRANGER_LINE},
}


def commit(sha, full=False):
    """A commit on try/issue-7 as GitHub's API returns it; full adds its files' patches."""
    c = COMMITS[sha]
    out = {"sha": sha, "html_url": f"https://github.com/o/r/commit/{sha}", "author": {"login": c["login"]},
           "committer": {"login": c["login"]}, "commit": {"message": "Add a test", "author": {"name": c["login"]}}}
    if full:
        out["files"] = [{"filename": f"tests/test_{sha}.py", "status": "added",
                         "patch": f'@@ -0,0 +1,3 @@\n+def test_{sha}():\n+    """{c["line"]}"""\n+    assert True'}]
    return out


def fake_branch(monkeypatch):
    """Fake GitHub: branch try/issue-7 holds one commit by the owner, one by a stranger."""
    def gh(*args):
        path = next((str(a).lstrip("/") for a in args[1:] if str(a).lstrip("/").startswith("repos/")), "") \
            if args[0] == "api" else ""
        many = [commit(s) for s in COMMITS]
        if re.match(r"repos/o/r/issues/7/parent$", path):
            raise subprocess.CalledProcessError(1, ["gh", *args], "", "HTTP 404: Not Found")
        if re.match(r"repos/o/r/compare/[^?]*\.\.\.try(/|%2F)issue-7", path):
            return json.dumps({"commits": many, "files": [f for s in COMMITS for f in commit(s, True)["files"]]})
        if re.match(r"repos/o/r/commits\?", path) and re.search(r"sha=try(/|%2F)issue-7", path):
            return json.dumps([many] if "--slurp" in args else many)
        m = re.match(r"repos/o/r/commits/(\w+)$", path)
        if m and m.group(1) in COMMITS:
            return json.dumps(commit(m.group(1), True))
        if args[:2] == ("pr", "list"):
            return "[]"
        raise AssertionError(f"unexpected GitHub call: gh {' '.join(map(str, args))}")
    monkeypatch.setattr(agent_github, "gh", gh)
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")


def plan_quoting(words, source):
    """A plan for issue 7 with one criterion quoting these words at this source."""
    return {"kind": "user_story", "title": "Fold long text", "summary": "Cards fold long text.",
            "user_story": "Owners read short cards.",
            "acceptance_criteria": [{"text": "Cards fold long text.", "words": words, "source": source,
                                     "files": ["dokima/card.py"], "no_edge_cases": "a sample criterion"}],
            "non_functional": [], "tests": {"7.1": ["tests/t.py::t"]}}


def test_text_the_owner_committed_on_the_branch_counts_as_their_words(record_property, monkeypatch, tmp_path):
    """A criterion may quote a line the owner committed, citing the commit as its source.

    Fakes an owner's commit and a stranger's on try/issue-7, builds the owner's words the way the planner's pack does,
    and runs the planner's hand-back check on a plan quoting each commit's line: the owner's is accepted, the
    stranger's refused, so the check is not a blanket yes. Proves 708.5."""
    record_property("proves", "708.5")
    fake_branch(monkeypatch)
    said = agent.owner_words("o/r", 7, {"body": "The ask."}, [], [OWNER])
    pack, out = tmp_path / "pack", tmp_path / "out"
    pack.mkdir()
    out.mkdir()
    (pack / "owner_words.json").write_text(json.dumps(said))
    monkeypatch.setenv("PACK", str(pack))
    (out / "plan.json").write_text(json.dumps(plan_quoting(OWNER_LINE, "https://github.com/o/r/commit/abc123")))
    try:
        planner.read_output(str(out), 7)
    except planner.Garbled as e:
        pytest.fail(f"708.5: a criterion quoting the owner's committed line was refused: {e}")
    (out / "plan.json").write_text(json.dumps(plan_quoting(STRANGER_LINE, "https://github.com/o/r/commit/def456")))
    with pytest.raises(planner.Garbled):
        planner.read_output(str(out), 7)
        pytest.fail("708.5: a line a stranger committed was accepted as the owner's words")


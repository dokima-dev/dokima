import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dokima import checks  # noqa: E402
import test_start as ts  # noqa: E402

BOT = "dokima-runtime[bot]"
DEFAULT_TYPES = ("opened", "synchronize", "reopened")  # GitHub's pull_request_target types when none are listed
FILTERS = ("branches", "branches-ignore", "paths", "paths-ignore")  # trigger filters push_runs_all_tests does not play


def real_owner():
    """The owner's real login, read from the repo's own `.github/CODEOWNERS`.

    716.1 plays the owner by this login, so a rule that skips the owner by name is caught, not just a made-up one."""
    path = os.path.join(os.path.dirname(__file__), "..", ".github", "CODEOWNERS")
    for line in open(path):
        words = line.split("#")[0].split()
        if len(words) > 1 and words[0] == "*":
            return words[1].lstrip("@")
    raise AssertionError("716.1: .github/CODEOWNERS names no owner for every file")


def push_runs_all_tests(pusher, owner):
    """Whether all tests run when `pusher` pushes to a Dokima pull request in `owner`'s repo.

    Plays GitHub's part the way test_one_order.py does: reads the workflow's own `on:` and the all tests job's `if:`
    (with test_start.py's expression reader) against a synchronize event sent by `pusher`, with `owner` as the
    repository's owner. Returns (runs, why): why names what stopped it, in plain words, when it does not run."""
    wf = ts.workflow("full-suite.yml")
    on = wf.get("on") or wf.get(True) or {}
    if "pull_request_target" not in on:
        return False, "full-suite.yml no longer runs on pull request events"
    spec = on.get("pull_request_target") or {}
    spec = spec if isinstance(spec, dict) else {}
    filters = [f for f in FILTERS if f in spec]
    if filters:
        return False, f"full-suite.yml's pull request trigger now filters on {filters}, so some pushes skip it"
    types = spec.get("types") or DEFAULT_TYPES
    types = [types] if isinstance(types, str) else types
    if "synchronize" not in types:
        return False, "full-suite.yml no longer runs when a pull request gets a new push"
    repo = f"{owner}/dokima"
    sender = {"login": pusher, "type": "Bot" if pusher.endswith("[bot]") else "User"}
    pr = {"number": 60, "draft": False, "state": "open", "labels": [], "user": {"login": BOT},
          "author_association": "NONE",
          "head": {"sha": "a1" * 20, "ref": f"try/issue-{ts.N}", "repo": {"full_name": repo}},
          "base": {"ref": "main", "repo": {"full_name": repo}}, "merged": False}
    event = {"action": "synchronize", "number": 60, "pull_request": pr, "sender": sender,
             "repository": {"full_name": repo, "owner": {"login": owner}}}
    github = ts.Ctx(event_name="pull_request_target", event=event, repository=repo, repository_owner=owner,
                    sha="a1" * 20, actor=pusher, triggering_actor=pusher, ref="refs/heads/main")
    job = next((j for j in wf["jobs"].values() if (j.get("name") or "") == "all tests"), None)
    if job is None:
        return False, "full-suite.yml has no job named all tests"
    ctx = {"github": github, "inputs": ts.Ctx(), "vars": ts.Ctx(), "secrets": ts.Ctx(), "needs": ts.Ctx()}
    if not ts.evaluate(ts.condition(job.get("if")), ctx, {"failed": False, "success": True}):
        return False, f"the all tests job's condition {job.get('if')!r} skips a push by {pusher}"
    return True, ""


def test_long_criteria_get_short_check_names(record_property):
    record_property("proves", "29.1")
    assert checks.check_name("40.1", "x" * 100) == "40.1 · " + "x" * 57 + "..."


def test_annotation_links_permanently_to_the_tests_first_line(record_property):
    record_property("proves", "29.2")
    xml = ('<testsuites><testsuite>'
           '<testcase file="tests/t.py" line="4" name="test_ok"/>'
           '<testcase file="tests/t.py" line="9" name="test_bad"><failure/></testcase>'
           '</testsuite></testsuites>')
    ok, bad = checks.annotations(xml, "o/r", "abc123", "40.1")
    assert ok.startswith("::notice file=tests/t.py,line=5,title=40.1 passed::")
    assert ok.endswith("view the test: https://github.com/o/r/blob/abc123/tests/t.py#L5")
    assert bad.startswith("::error file=tests/t.py,line=10,title=40.1 failed::")


def test_full_suite_runs_every_test_on_every_pull_request(record_property):
    """The merge gate still runs every test, in parallel, exactly as today.

    Proves 29.4, 539.3 and 716.1. Reads full-suite.yml and checks it still installs only pytest and pytest-xdist,
    still runs every test spread over all cores with `-n auto`, and never uses testmon, which only code reviews use.
    For 716.1 it plays GitHub's part on a new push to a ready Dokima pull request, once by Dokima's bot and once by
    the owner, and checks the all tests job runs for both: no trigger filter or condition on who pushed skips the
    owner. The owner is played by their real login from `.github/CODEOWNERS`, as the repository's owner, so a rule
    naming them or `github.repository_owner` is caught. The bot's push is the good case beside it, so a workflow that
    ran for no one fails too."""
    record_property("proves", "29.4")
    record_property("proves", "539.3")
    record_property("proves", "716.1")
    owner = real_owner()
    runs, why = push_runs_all_tests(BOT, owner)
    assert runs, f"716.1: a push by Dokima to its pull request no longer runs all tests: {why}"
    runs, why = push_runs_all_tests(owner, owner)
    assert runs, f"716.1: a push by the owner to a Dokima pull request does not run all tests: {why}"
    path = os.path.join(os.path.dirname(__file__), "..", ".github/workflows/full-suite.yml")
    lines = [line.strip() for line in open(path)]
    assert "name: full suite" in lines
    assert "pull_request_target:" in lines
    assert "name: all tests" in lines
    assert any(line.startswith("- run: pytest") and line.endswith(" tests") for line in lines)
    assert "- run: pip install -q pytest pytest-xdist" in lines, "539.3: the merge gate no longer installs exactly pytest and pytest-xdist"
    assert "- run: pytest -q -p no:cacheprovider -n auto tests" in lines, \
        "539.3: the merge gate no longer runs every test in parallel with -n auto"
    assert not any("testmon" in line for line in lines), "539.3: the merge gate uses testmon, so it may skip tests"

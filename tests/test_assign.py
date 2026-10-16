import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "assign.yml")


def approvers(cwd):
    """What `python3 -m dokima.plan approvers` prints when run in `cwd`, for the repository owner `the-owner`."""
    env = dict(os.environ, PYTHONPATH=os.path.abspath(ROOT), GITHUB_REPOSITORY_OWNER="the-owner")
    run = subprocess.run([sys.executable, "-m", "dokima.plan", "approvers"], cwd=cwd, env=env,
                         capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, f"760.7: listing the code owners failed:\n{run.stderr}"
    return run.stdout.strip()


def test_new_issues_are_assigned_to_the_code_owners(record_property, tmp_path):
    """New issues go to the code owners, and listing them still works as before.

    Proves 90.1 and 760.7. Checks assign.yml assigns every opened issue to what `python3 -m dokima.plan approvers`
    prints. Then runs that command in a temp repo whose CODEOWNERS names the owners of every file, and in one with no
    CODEOWNERS, and checks it prints those owners, then the repository owner, as before."""
    record_property("proves", "90.1")
    record_property("proves", "760.7")
    text = open(WORKFLOW).read()
    assert "issues:" in text and "types: [opened]" in text, "90.1: assign.yml does not run on issue opened"
    assert "sender.type" not in text, "90.1: assign.yml filters out bots, so bot-opened issues stay unassigned"
    assert '--add-assignee "$(python3 -m dokima.plan approvers)"' in text, "90.1: assign.yml does not assign the CODEOWNERS approvers"
    named = tmp_path / "named"
    (named / ".github").mkdir(parents=True)
    (named / ".github" / "CODEOWNERS").write_text("# owners\ndocs/ @docs-team\n* @bob @alice\n")
    assert approvers(named) == "alice,bob", "760.7: listing the code owners no longer prints the owners of every file"
    bare = tmp_path / "bare"
    bare.mkdir()
    assert approvers(bare) == "the-owner", "760.7: with no CODEOWNERS, listing the code owners no longer prints the repository owner"

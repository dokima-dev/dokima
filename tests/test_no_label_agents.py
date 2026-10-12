"""No label starts an agent any more: agents start only through /plan and /work (#433).

The old planner.yml and worker.yml started the planner and the worker when a code owner added the plan or work label,
and pushed to work/issue-N. AGENTS.md now says agents start with /plan and /work, through commands.yml and agent.yml.
These tests read every workflow under .github/workflows (without a YAML library, as tests/test_keys.py does) and fail
while any workflow still starts an agent on a label change or pushes to the old work branch.
"""
import glob
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")

# What the old planner.yml looked like, cut down: the detector must flag it, or a passing test proves nothing.
OLD_PLANNER = """name: planner
on:
  issues:
    types: [labeled]
jobs:
  plan:
    if: github.event.label.name == 'plan'
    steps:
      - run: claude -p "$(cat dokima/roles/plan-grade.md dokima/roles/planner.md)"
      - run: git push origin "HEAD:work/issue-$N"
"""
OLD_WORKER = OLD_PLANNER.replace("'plan'", "'work'").replace("roles/planner.md", "roles/worker.md").replace(
    "[labeled]", "[labeled, unlabeled]")


def workflows():
    """Every workflow in the repo, as {file name: text}."""
    return {os.path.basename(p): open(p).read() for p in sorted(glob.glob(os.path.join(WORKFLOWS, "*.y*ml")))}


def triggers(text):
    """The workflow's `on:` section, up to its next top-level key."""
    if "\non:\n" not in "\n" + text:
        return ""
    on = ("\n" + text).split("\non:\n", 1)[1]
    return re.split(r"(?m)^[a-z]", on, 1)[0]


def runs_on_labels(text):
    """True when adding or removing an issue's label runs this workflow."""
    block = re.search(r"(?m)^  issues:[^\n]*\n((?:    [^\n]*\n|\s*\n)*)", triggers(text) + "\n")
    if not block:
        return False
    types = re.search(r"types:\s*\[([^\]]*)\]", block.group(1))
    if not types:  # no types: every issue event, labels included
        return True
    return bool({"labeled", "unlabeled"} & {t.strip() for t in types.group(1).split(",")})


def starts_an_agent(text):
    """True when the workflow runs an agent itself or hands one to agent.yml."""
    return ("claude -p" in text or "event_type=dokima-next" in text
            or "uses: ./.github/workflows/agent.yml" in text)


def label_starts(text, label, prompt):
    """True when a label change runs this workflow and it starts that label's agent."""
    if not (runs_on_labels(text) and starts_an_agent(text)):
        return False
    named = re.search(rf"label\.name\s*[!=]=\s*'{label}'", text)
    return bool(named or prompt in text or "agent.yml" in text or "dokima-next" in text)


def test_adding_the_plan_label_no_longer_starts_the_planner(record_property):
    """Adding the plan label to an issue starts no planner.

    Proves 433.1. Reads every workflow: none that runs on a label change may start an agent for the plan label. The same check flags the
    old planner.yml, so it would catch it coming back, and commands.yml still starts agents from a comment."""
    record_property("proves", "433.1")
    assert label_starts(OLD_PLANNER, "plan", "roles/planner.md"), "433.1: the check missed the old label-driven planner"
    commands = workflows()["commands.yml"]
    assert starts_an_agent(commands) and not runs_on_labels(commands), \
        "433.1: commands.yml should still start agents from /plan and /work, not from labels"
    found = [name for name, text in workflows().items() if label_starts(text, "plan", "roles/planner.md")]
    assert not found, f"433.1: adding the plan label still starts the planner through {', '.join(found)}"


def test_adding_the_work_label_no_longer_starts_the_worker(record_property):
    """Adding the work label to an issue starts no worker.

    Proves 433.2. Reads every workflow: none that runs on a label change may start an agent for the work label. The same check flags the
    old worker.yml, so it would catch it coming back, and commands.yml still starts agents from a comment."""
    record_property("proves", "433.2")
    assert label_starts(OLD_WORKER, "work", "roles/worker.md"), "433.2: the check missed the old label-driven worker"
    commands = workflows()["commands.yml"]
    assert starts_an_agent(commands) and not runs_on_labels(commands), \
        "433.2: commands.yml should still start agents from /plan and /work, not from labels"
    found = [name for name, text in workflows().items() if label_starts(text, "work", "roles/worker.md")]
    assert not found, f"433.2: adding the work label still starts the worker through {', '.join(found)}"


def test_no_workflow_pushes_to_the_old_work_branch(record_property):
    """No workflow pushes an agent's work to the old work/issue-N branch.

    Proves 433.3. Reads every workflow for a push to work/issue-N. The same check flags the old planner.yml, and agent.yml still pushes
    the agents' work to try/issue-N, so the check is not passing on a repo that pushes nothing."""
    record_property("proves", "433.3")

    def pushes_work(text):
        return any("git push" in line and "work/issue-" in line and "try/issue-" not in line for line in text.splitlines())

    assert pushes_work(OLD_PLANNER), "433.3: the check missed a push to work/issue-N"
    assert any("git push" in line and "HEAD:try/issue-$N" in line for line in workflows()["agent.yml"].splitlines()), \
        "433.3: agent.yml no longer pushes the agents' work to try/issue-N"
    found = [name for name, text in workflows().items() if pushes_work(text)]
    assert not found, f"433.3: {', '.join(found)} still push to the old work/issue-N branch"

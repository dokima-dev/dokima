"""Workflow changes merge like any other change, and keys open only from main (#126).

GitHub runs a PR's own copy of the workflow files before anyone reviews it. These tests
prove that every job holding a key takes it from the "keys" environment (which only main
can open), that nothing else names a key, and that the old approval gate is gone.
"""
import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
TEXT = {os.path.basename(p): open(p).read() for p in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml"))}


def jobs():
    """Each job as (workflow, job name, its text), read without a YAML library."""
    for name, text in TEXT.items():
        body = text.split("\njobs:\n", 1)[1]
        parts = re.split(r"(?m)^  ([A-Za-z0-9_-]+):\n", body)
        for job_name, job_text in zip(parts[1::2], parts[2::2]):
            yield name, job_name, job_text


def triggers(text):
    """The workflow's trigger section, up to its first other top-level key."""
    on = text.split("\non:\n", 1)[1]
    return re.split(r"(?m)^[a-z]", on, 1)[0]


def test_agents_may_push_workflow_files_and_no_extra_approval_exists(record_property):
    """The bot can push workflow files, and no approval step or pending-build handoff remains."""
    record_property("proves", "126.1")
    perms = json.load(open(os.path.join(ROOT, "dokima", "app.json")))["default_permissions"]
    assert perms.get("workflows") == "write", "126.1: the bot can't push workflow changes"
    text = "".join(TEXT.values())
    for gone in ("workflow-changes", "DOKIMA_WORKFLOW_TOKEN", "dokima.gate", "push-workflow-changes"):
        assert gone not in text, f"126.1: the old approval gate is still there ({gone})"
    assert not os.path.exists(os.path.join(ROOT, "dokima", "gate.py"))


def test_every_job_that_uses_a_key_takes_it_from_the_main_only_safe(record_property):
    """Any job that mentions a secret declares the "keys" environment; no other job does.

    A job calling a shared workflow cannot declare an environment, so its one `secrets:` line handing keys on by
    name (#897) opens none itself: the called job reads them under the keys environment, whose secrets win.
    """
    record_property("proves", "126.2")
    for name, job_name, job in jobs():
        if re.search(r"(?m)^    uses: \./\.github/workflows/", job):
            job = re.sub(r"(?m)^    secrets: \{.*$", "", job)
        if "secrets." in job:
            assert "\n    environment: keys\n" in "\n" + job, f"126.2: {name}:{job_name} reads a key outside the safe"


def test_pr_triggered_workflows_hold_no_keys(record_property):
    """Workflows that run on a PR's own copy (pull_request, push to branches) never name a key."""
    record_property("proves", "126.2")
    for name, text in TEXT.items():
        if re.search(r"(?m)^  pull_request:", triggers(text)):
            assert "secrets." not in text, f"126.2: {name} runs on PRs and names a key"


def test_a_build_starts_from_todays_main(record_property):
    """An issue branch made before main changed is brought up to date before the build.

    Without this, a branch the planner created earlier runs old code, so newer
    steps are missing and the build fails.
    """
    record_property("proves", "123.1")
    agent = TEXT["agent.yml"]
    # Since #795 the default branch comes from the settings; 795.7 proves it is the one they name.
    merge = next((line for line in agent.splitlines() if re.search(r'merge -q --no-edit "?origin/', line)
                  and '"$ROLE" = worker' in line), None)
    assert merge, "123.1: the worker's branch is not brought up to today's main"
    assert '"$ROLE" = worker' in merge, "123.1: the worker's branch is not brought up to today's main"

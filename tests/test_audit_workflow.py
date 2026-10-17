"""Tests for #285: one workflow runs the drift audit daily and on Run workflow.

The audit itself (`python3 -m dokima.audit OWNER/REPO`, #283) is proven in tests/test_audit.py and
tests/test_audit_cli.py. These prove the workflow that runs it: `.github/workflows/audit.yml`, read with the repo's
own YAML reader (tests/test_start.py's load_yaml, no YAML library). The workflow's own audit step is run the way GitHub
would run it: its `${{ }}` filled in, its env set, its script run with `bash -e` against the fake `gh` of
tests/fake_gh.py, from a folder holding .github/CODEOWNERS, with the dokima package on PYTHONPATH.
"""
import copy
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import test_start as ts  # noqa: E402
from dokima import agent, manifest  # noqa: E402

WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
AUDIT = os.path.join(WORKFLOWS, "audit.yml")
REPO = "acme/widgets"
TOKEN = "fake-app-token"


def workflow(criterion):
    """The audit workflow, read; fails naming the criterion when it is missing."""
    if not os.path.exists(AUDIT):
        pytest.fail(f"{criterion}: there is no .github/workflows/audit.yml to run the audit")
    return ts.load_yaml(open(AUDIT).read())


def triggers(wf):
    """The workflow's `on:` as a dict of event name to its settings."""
    on = wf.get("on")
    if isinstance(on, str):
        return {on: ""}
    if isinstance(on, list):
        return {e: "" for e in on}
    return on or {}


def audit_steps(wf):
    """Every (job name, job, step index, step) whose script runs `dokima.audit`."""
    return [(name, job, i, step) for name, job in (wf.get("jobs") or {}).items()
            for i, step in enumerate(job.get("steps") or []) if "dokima.audit" in str(step.get("run") or "")]


def the_audit_step(wf, criterion):
    """The one step that runs the audit; fails when there is none or several."""
    found = audit_steps(wf)
    assert len(found) == 1, (f"{criterion}: audit.yml should run `python3 -m dokima.audit` in exactly one step, "
                             f"found {len(found)}")
    return found[0]


def context(event):
    """The expression contexts of a run that `event` started.

    Every step's outputs.token is the app token."""
    return {"github": ts.Ctx(repository=REPO, repository_owner="acme", event_name=event, ref="refs/heads/main",
                             run_id="1", server_url="https://github.com", event={}),
            "vars": ts.Ctx(DOKIMA_BOARD="acme/1", DOKIMA_APP_ID="1"),
            "secrets": ts.Ctx(DOKIMA_APP_KEY="k", GITHUB_TOKEN="workflow-token"),
            "inputs": ts.Ctx(), "env": ts.Ctx(), "needs": ts.Ctx(), "runner": ts.Ctx(os="Linux", temp="/tmp"),
            "steps": ts.Ctx(app=ts.Ctx(outputs=ts.Ctx(token=TOKEN)))}


def step_context(job, event):
    """The contexts at the audit step, with every step id's token output set.

    Every step with an id answers outputs.token with the app token."""
    ctx = context(event)
    ctx["steps"] = ts.Ctx({s["id"]: {"outputs": {"token": TOKEN}, "outcome": "success", "conclusion": "success"}
                           for s in job.get("steps") or [] if s.get("id")})
    return ctx


def clean():
    """A fake GitHub whose settings match the manifest, with no issues."""
    return {"repo": REPO, "labels": copy.deepcopy(manifest.LABELS), "fields": copy.deepcopy(manifest.FIELDS),
            "views": copy.deepcopy(manifest.VIEWS),
            "protection": {b: list(r["required_checks"]) for b, r in manifest.BRANCH_RULES.items()},
            "permissions": copy.deepcopy(manifest.PERMISSIONS), "fail": {}, "issues": {}, "next": 100,
            "items": {}, "calls": [], "writes": []}


def run_the_step(tmp_path, state, criterion):
    """Run audit.yml's audit step as a scheduled run would, against a fake GitHub.

    Returns (process, state).

    The env holds only what any runner has plus the fake: no DOKIMA_BOARD or token unless the workflow sets them."""
    wf = workflow(criterion)
    name, job, _, step = the_audit_step(wf, criterion)
    ctx = step_context(job, "schedule")
    env = dict(os.environ)
    for k in ("DOKIMA_BOARD", "GH_TOKEN", "GITHUB_TOKEN"):
        env.pop(k, None)
    for scope in (wf.get("env") or {}, job.get("env") or {}, step.get("env") or {}):
        env.update({k: ts.fill(v, ctx, {"failed": False}) for k, v in scope.items()})
    root = tmp_path / "repo"
    (root / ".github").mkdir(parents=True)
    (root / ".github" / "CODEOWNERS").write_text("* @alice\n")
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    gh = bin_ / "gh"
    gh.write_text(f"#!{sys.executable}\n" + open(os.path.join(HERE, "fake_gh.py")).read())
    gh.chmod(0o755)
    py = bin_ / "python3"
    py.write_text(f"#!/bin/sh\nexec {sys.executable} \"$@\"\n")
    py.chmod(0o755)
    file = tmp_path / "github.json"
    file.write_text(json.dumps(state))
    env.update(PATH=f"{bin_}{os.pathsep}{os.environ.get('PATH', '')}", PYTHONPATH=ROOT, FAKE_GH_STATE=str(file),
               GITHUB_REPOSITORY=REPO, GITHUB_REPOSITORY_OWNER="acme", GITHUB_EVENT_NAME="schedule",
               GITHUB_WORKSPACE=str(root), GITHUB_OUTPUT=str(tmp_path / "out"), GITHUB_ENV=str(tmp_path / "env"))
    script = ts.fill(step["run"], ctx, {"failed": False})
    p = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert "Traceback" not in p.stderr, f"{criterion}: the workflow's audit command crashed:\n{p.stderr}"
    return p, json.loads(file.read_text())


def test_one_workflow_runs_the_audit_once_a_day(record_property):
    """One workflow runs the audit once a day on a schedule.

    Proves 285.1. Reads .github/workflows/audit.yml: its `on.schedule` holds exactly one cron line that fires once a day (one fixed
    minute and one fixed hour, every day of every month), one of its steps runs `python3 -m dokima.audit`, and no
    other workflow runs the audit."""
    record_property("proves", "285.1")
    wf = workflow("285.1")
    on = triggers(wf)
    assert "schedule" in on, f"285.1: audit.yml has no schedule; its triggers are {sorted(on)}"
    crons = on["schedule"] if isinstance(on["schedule"], list) else []
    assert len(crons) == 1 and isinstance(crons[0], dict) and crons[0].get("cron"), \
        f"285.1: audit.yml should have exactly one cron line, found {on['schedule']!r}"
    fields = str(crons[0]["cron"]).split()
    assert len(fields) == 5, f"285.1: the cron line {crons[0]['cron']!r} should have five fields"
    minute, hour, day, month, weekday = fields
    assert re.fullmatch(r"\d+", minute) and int(minute) < 60 and re.fullmatch(r"\d+", hour) and int(hour) < 24 \
        and (day, month, weekday) == ("*", "*", "*"), \
        f"285.1: the cron line {crons[0]['cron']!r} does not fire exactly once every day"
    the_audit_step(wf, "285.1")
    others = [f for f in sorted(os.listdir(WORKFLOWS)) if f.endswith((".yml", ".yaml")) and f != "audit.yml"
              and "dokima.audit" in open(os.path.join(WORKFLOWS, f)).read()]
    assert not others, f"285.1: only audit.yml should run the audit, but so do {others}"


def test_the_audit_runs_on_a_schedule_or_the_run_workflow_button_and_nothing_else(record_property):
    """The audit starts on its schedule or the Run workflow button, and on nothing else.

    Proves 285.2. Reads audit.yml: its triggers are exactly `schedule` and `workflow_dispatch` (no settings-change events, no
    comments), besides the call from entry.yml (#812), which it makes on those two events alone; the button needs no input, and the audit job and step run for both a scheduled and a button run with
    the board set. It also checks that no comment, such as `/audit`, starts anything: the comment commands are still
    only /plan, /work and /review."""
    record_property("proves", "285.2")
    wf = workflow("285.2")
    on = triggers(wf)
    assert set(on) - {"workflow_call"} == {"schedule", "workflow_dispatch"}, \
        f"285.2: audit.yml should start only on schedule and workflow_dispatch, it starts on {sorted(on)}"
    # Since #812 an adopter's one workflow calls audit.yml through entry.yml: on those same two events alone.
    entry = ts.load_yaml(open(os.path.join(ROOT, ".github", "workflows", "entry.yml")).read())
    called = set(re.findall(r"github\.event_name == '(\w+)'", str(entry["jobs"]["audit"].get("if"))))
    assert called == {"schedule", "workflow_dispatch"}, \
        f"285.2: entry.yml should call audit.yml only on schedule and workflow_dispatch, it calls it on {sorted(called)}"
    inputs = (on["workflow_dispatch"] or {}).get("inputs") if isinstance(on["workflow_dispatch"], dict) else None
    required = [k for k, v in (inputs or {}).items() if isinstance(v, dict) and str(v.get("required")) == "true"]
    assert not required, f"285.2: the Run workflow button should need no input, it requires {required}"
    name, job, i, step = the_audit_step(wf, "285.2")
    for event in ("schedule", "workflow_dispatch"):
        ctx = context(event)
        assert ts.evaluate(ts.condition(job.get("if")), ctx, {"failed": False}), \
            f"285.2: the audit job {name!r} is skipped on a {event} run"
        assert ts.evaluate(ts.condition(step.get("if")), step_context(job, event), {"failed": False}), \
            f"285.2: the audit step is skipped on a {event} run"
    assert set(agent.COMMANDS) == {"/plan", "/work", "/review"}, \
        f"285.2: a new comment command was added: {sorted(agent.COMMANDS)}"
    for said in ("/audit", "/drift", "/setup"):
        assert agent.route(said, False, "5") is None, f"285.2: the comment {said!r} starts {agent.route(said, False, '5')}"


def test_the_workflow_reports_a_missing_branch_rule_on_a_new_setup_issue(record_property, tmp_path):
    """The workflow's audit opens a pinned Setup issue for a missing branch rule.

    Proves 285.3. Runs audit.yml's audit step, its `${{ }}` filled and its env set by the workflow alone, against a fake GitHub
    that matches the manifest except that main has no branch rule. It must exit 0, open exactly one issue, pin it,
    and list main's missing rule on it."""
    record_property("proves", "285.3")
    state = clean()
    del state["protection"]["main"]
    p, after = run_the_step(tmp_path, state, "285.3")
    assert p.returncode == 0, f"285.3: the workflow's audit step failed ({p.returncode}):\n{p.stdout}\n{p.stderr}"
    made = [w["number"] for w in after["writes"] if w["kind"] == "create"]
    assert len(made) == 1, f"285.3: the step should open exactly one Setup issue, it opened {made}\n" \
                           f"unsupported: {after.get('unsupported', [])}\n{p.stdout}\n{p.stderr}"
    issue = after["issues"][str(made[0])]
    lines = [l for l in issue["body"].splitlines() if "`main`" in l and "no rule" in l]
    assert len(lines) == 1, f"285.3: the Setup issue should name main's missing rule once:\n{issue['body']}"
    assert issue.get("pinned") or any(w["kind"] == "pin" for w in after["writes"]), \
        f"285.3: the Setup issue #{made[0]} was not pinned; writes: {after['writes']}"


def test_the_workflow_posts_nothing_on_a_clean_repo(record_property, tmp_path):
    """The workflow's audit, run as GitHub runs it, posts nothing when every setting matches.

    Proves 285.3. Runs audit.yml's audit step against a fake GitHub that matches the manifest and has no Setup issue. It must
    exit 0 and write nothing: no issue, comment, edit, pin or board change."""
    record_property("proves", "285.3")
    p, after = run_the_step(tmp_path, clean(), "285.3")
    assert p.returncode == 0, f"285.3: the workflow's audit step failed ({p.returncode}):\n{p.stdout}\n{p.stderr}"
    assert after["writes"] == [], f"285.3: a clean repo should get no writes, got {after['writes']}"
    assert not after.get("unsupported"), f"285.3: the step made calls GitHub would refuse: {after['unsupported']}"


def test_audit_runs_wait_in_one_queue_for_the_repo(record_property):
    """A second audit waits for the one running, in one queue for the whole repo.

    Proves 285.4. Reads audit.yml: it sets a concurrency group (on the workflow, or on the audit job) that is one fixed name with no
    `${{ }}` in it, never cancels a run in progress, and is shared with no other workflow, so an audit never cancels
    or waits on another kind of run."""
    record_property("proves", "285.4")
    wf = workflow("285.4")
    name, job, _, _ = the_audit_step(wf, "285.4")
    conc = job.get("concurrency") or wf.get("concurrency")
    assert conc, "285.4: audit.yml sets no concurrency, so two audits can run at once"
    group = conc if isinstance(conc, str) else conc.get("group")
    assert group and "${{" not in str(group), \
        f"285.4: the concurrency group {group!r} should be one fixed name for the repo"
    cancel = "false" if isinstance(conc, str) else str(conc.get("cancel-in-progress", "false")).lower()
    assert cancel == "false", f"285.4: cancel-in-progress is {cancel!r}; a second run must wait, not cancel"
    shared = []
    for f in sorted(os.listdir(WORKFLOWS)):
        if f == "audit.yml" or not f.endswith((".yml", ".yaml")):
            continue
        other = ts.load_yaml(open(os.path.join(WORKFLOWS, f)).read())
        groups = [other.get("concurrency")] + [j.get("concurrency") for j in (other.get("jobs") or {}).values()]
        groups = [g if isinstance(g, str) else (g or {}).get("group") for g in groups]
        if str(group) in [str(g) for g in groups if g]:
            shared.append(f)
    assert not shared, f"285.4: the concurrency group {group!r} is also used by {shared}"


def test_the_audit_acts_as_the_dokima_app(record_property):
    """The audit reads and writes GitHub as the Dokima app, never the workflow.

    Proves 285.5. Reads audit.yml: the audit step's GH_TOKEN is the token output of an earlier step in its job that runs
    actions/create-github-app-token with the DOKIMA_APP_ID variable and DOKIMA_APP_KEY secret, the job opens the keys
    environment that holds the key, and the step sets DOKIMA_BOARD from the repo variable."""
    record_property("proves", "285.5")
    wf = workflow("285.5")
    name, job, i, step = the_audit_step(wf, "285.5")
    token = str((step.get("env") or {}).get("GH_TOKEN") or "")
    m = re.fullmatch(r"\$\{\{\s*steps\.([\w-]+)\.outputs\.token\s*\}\}", token.strip())
    assert m, f"285.5: the audit step's GH_TOKEN is {token!r}, not the app token of an earlier step"
    makers = [s for s in (job.get("steps") or [])[:i] if s.get("id") == m.group(1)]
    assert makers and str(makers[0].get("uses", "")).startswith("actions/create-github-app-token@"), \
        f"285.5: step {m.group(1)!r} before the audit does not mint the app token"
    w = makers[0].get("with") or {}
    assert "vars.DOKIMA_APP_ID" in str(w.get("app-id")) and "secrets.DOKIMA_APP_KEY" in str(w.get("private-key")), \
        f"285.5: the token step should use DOKIMA_APP_ID and DOKIMA_APP_KEY, it has {w}"
    assert str(job.get("environment")) == "keys", f"285.5: the audit job should open the keys environment"
    board_ = str((step.get("env") or {}).get("DOKIMA_BOARD") or "")
    assert "vars.DOKIMA_BOARD" in board_, f"285.5: the audit step's DOKIMA_BOARD is {board_!r}, not the repo variable"

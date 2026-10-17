"""In the merge queue, main's copy of Dokima's code judges a queued pull request (#388).

On the merge queue's event GitHub hands acceptance-criteria.yml the queued commit: the pull request on top of the latest main.
A checkout with no `ref:` then copies that commit, so a pull request that edits dokima/checks.py would make its own
check list in the queue. These tests play GitHub's part. They build four tiny trees: main, the pull request's head,
the queued commit, and another pull request queued ahead of it. In the queue the event's base_sha is the commit just
ahead (here that other pull request's queued commit), never main, so only a checkout of main itself finds main's code.
Each tree holds a stand-in dokima/checks.py that notes whose copy ran; main's lists the plan's one check, while the
other three are "edited" to list one always-passing Text only check. Each tree also holds app.py and the test that
checks it, its code working or broken.

Every job of the real acceptance-criteria.yml (list, check once per row of the list's matrix, gate) then runs step by step:
`actions/checkout` copies the tree its `ref` names on that event (the queued commit by default on merge_group, main
by default on pull_request_target), other `uses:` steps are skipped, every `run:` script runs with bash, its `${{ }}`
filled in, with a `pip` that does nothing and a `pytest` that runs this machine's pytest. The repo is Dokima's own, so
a checkout of dokima-dev/dokima (#812) copies these trees too, only the folders a sparse checkout names; the commit
of the workflow file that runs (`github.workflow_sha`, and the called file's own `job.workflow_sha` as no other repo
calls it) is the event's own commit, as GitHub gives it. Each step
sees a runner temp folder and the values earlier steps of its job wrote to GITHUB_ENV.
"""
import json
import os
import shutil
import subprocess
import sys

import test_start as ts

ROOT = ts.ROOT
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "acceptance-criteria.yml")
MAIN_SHA = "3" * 40
PR_SHA = "1" * 40
QUEUE_SHA = "2" * 40
AHEAD_SHA = "4" * 40
N = 7

APP_GOOD = "def value():\n    return 1\n"
APP_BAD = "def value():\n    return 2\n"
TEST_APP = '''"""The tiny project's one test."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app  # noqa: E402


def test_value():
    assert app.value() == 1
'''

# A stand-in for dokima/checks.py: notes whose copy ran and what for, then answers like the real one.
CHECKS = '''"""A stand-in for Dokima's check list, noting whose copy ran."""
import json
import sys

with open({log!r}, "a") as f:
    f.write({who!r} + " " + sys.argv[1] + "\\n")
if sys.argv[1] == "matrix":
    print("matrix=" + json.dumps({rows!r}))
'''
PLAN_ROWS = [{"id": "388.9", "name": "388.9 · The value is one", "tests": "tests/test_app.py::test_value"}]
EDITED_ROWS = [{"id": "text-only", "name": "Text only: no plan needed", "tests": ""}]


def tree(where, who, app, rows, log):
    """Write one tiny tree: a stand-in dokima package, app.py and its test."""
    os.makedirs(os.path.join(where, "dokima"))
    os.makedirs(os.path.join(where, "tests"))
    open(os.path.join(where, "dokima", "__init__.py"), "w").write("")
    open(os.path.join(where, "dokima", "checks.py"), "w").write(CHECKS.format(log=log, who=who, rows=rows))
    open(os.path.join(where, "app.py"), "w").write(app)
    open(os.path.join(where, "tests", "test_app.py"), "w").write(TEST_APP)


def context(event, needs=None, matrix=None):
    """The `${{ }}` contexts GitHub gives acceptance-criteria.yml on this event."""
    if event == "merge_group":
        # Another pull request is queued ahead: the queued commit is built on its queued commit, not on main.
        ev = {"action": "checks_requested", "merge_group": {
            "head_sha": QUEUE_SHA, "head_ref": f"refs/heads/gh-readonly-queue/main/pr-{N}-{AHEAD_SHA}",
            "base_sha": AHEAD_SHA, "base_ref": "refs/heads/main"}}
        sha, ref, base_ref = QUEUE_SHA, f"refs/heads/gh-readonly-queue/main/pr-{N}-{AHEAD_SHA}", ""
    else:
        ev = {"action": "synchronize", "number": N, "pull_request": {
            "number": N, "head": {"sha": PR_SHA, "ref": "work/issue-1"}, "base": {"sha": MAIN_SHA, "ref": "main"}}}
        sha, ref, base_ref = MAIN_SHA, "refs/heads/main", "main"
    return ts.Ctx({k: ts.Ctx(v) for k, v in {
        "github": {"event_name": event, "repository": "o/r", "token": "ghs_x", "sha": sha, "ref": ref,
                   "base_ref": base_ref, "event": ev, "workflow_sha": sha, "job_workflow_sha": sha},
        "job": {"workflow_sha": sha},
        "secrets": {}, "vars": {}, "env": {}, "steps": {}, "needs": needs or {}, "matrix": matrix or {},
        "inputs": {}}.items()})


def tree_for(ref, event, trees):
    """The tree a checkout of this ref copies on this event."""
    if ref in ("", None):
        return trees["queued"] if event == "merge_group" else trees["main"]
    if ref in (MAIN_SHA, "main", "refs/heads/main"):
        return trees["main"]
    if ref in (QUEUE_SHA, f"refs/heads/gh-readonly-queue/main/pr-{N}-{AHEAD_SHA}"):
        return trees["queued"]
    if ref in (AHEAD_SHA, f"refs/heads/gh-readonly-queue/main/pr-{N - 1}-{MAIN_SHA}"):
        return trees["ahead"]
    if ref in (PR_SHA, "work/issue-1", f"refs/pull/{N}/head"):
        return trees["pr"]
    raise AssertionError(f"the tests do not know which tree the checkout ref {ref!r} names on {event}")


def run_job(job, wf, ctx, event, trees, ws, bin_dir, out_file):
    """Run one job's steps the way GitHub would; returns 'success' or 'failure', and the log."""
    status = {"failed": False}
    shutil.rmtree(ws, ignore_errors=True)
    os.makedirs(ws)
    log, added = [], {}
    # The runner's own temp folder, outside the workspace, where a step may move Dokima's checked-out code.
    temp = os.path.join(ws, "..", "runner-temp")
    os.makedirs(temp, exist_ok=True)
    for step in job.get("steps") or []:
        scond = str(step.get("if") or "").replace("${{", "").replace("}}", "").strip()
        if not ts.evaluate(ts.condition(scond), ctx, status):
            continue
        uses = str(step.get("uses") or "")
        if uses.startswith("actions/checkout"):
            w = {k: ts.fill(v, ctx, status) for k, v in (step.get("with") or {}).items()}
            assert w.get("repository", "") in ("", "o/r", ts.DOKIMA_REPO), \
                f"the tests do not know the repo {w.get('repository')!r} a checkout names"
            dest = os.path.join(ws, w.get("path") or ".")
            src = tree_for(w.get("ref") or "", event, trees)
            log.append(f"checkout {w.get('ref') or '(no ref)'} -> {os.path.basename(src)} into {w.get('path') or '.'}")
            if w.get("sparse-checkout"):
                for part in str(w["sparse-checkout"]).split():
                    shutil.copytree(os.path.join(src, part), os.path.join(dest, part), dirs_exist_ok=True)
            else:
                shutil.copytree(src, dest, dirs_exist_ok=True)
            continue
        if uses or "run" not in step:
            continue
        script = ts.fill(step["run"], ctx, status)
        senv = {k: ts.fill(v, ctx, status) for k, v in {**(job.get("env") or {}), **(step.get("env") or {})}.items()}
        cwd = os.path.join(ws, ts.fill(step.get("working-directory") or ".", ctx, status))
        path = os.path.join(ws, "..", f"step-{len(log)}.sh")
        open(path, "w").write(script)
        env_file = os.path.join(ws, "..", "github-env")
        open(env_file, "w").close()
        p = subprocess.run(ts.github_shell(step, job, wf.get("defaults")) + [path], cwd=cwd, capture_output=True,
                           text=True, timeout=120,
                           env={"PATH": bin_dir + os.pathsep + os.environ["PATH"], "HOME": os.path.join(ws, ".."),
                                "PYTHONDONTWRITEBYTECODE": "1", "GITHUB_OUTPUT": out_file,
                                "GITHUB_REPOSITORY": "o/r", "RUNNER_TEMP": temp, "GITHUB_ENV": env_file,
                                **added, **senv})
        added.update(line.split("=", 1) for line in open(env_file).read().splitlines() if "=" in line)
        log.append(f"$ {script.strip()}\n{p.stdout}{p.stderr}")
        if p.returncode != 0:
            status["failed"] = True
            return "failure", "\n".join(log)
    return "success", "\n".join(log)


def queue(tmp_path, event, app):
    """Run every job of acceptance-criteria.yml on this event for a pull request with this code.

    The pull request's and the queued commit's app.py is `app`. Main's code is always the working one. Returns whether the gate passed, which copies of dokima/checks.py ran
    (as 'who what' lines), and the log of every job."""
    tmp_path = str(tmp_path)
    log_file = os.path.join(tmp_path, "who-ran.log")
    trees = {"main": os.path.join(tmp_path, "main"), "pr": os.path.join(tmp_path, "pr"),
             "queued": os.path.join(tmp_path, "queued"), "ahead": os.path.join(tmp_path, "ahead")}
    tree(trees["main"], "main", APP_GOOD, PLAN_ROWS, log_file)
    tree(trees["pr"], "pull-request", app, EDITED_ROWS, log_file)
    tree(trees["queued"], "queued", app, EDITED_ROWS, log_file)
    tree(trees["ahead"], "queued-ahead", APP_GOOD, EDITED_ROWS, log_file)
    bin_dir = os.path.join(tmp_path, "bin")
    os.makedirs(bin_dir)
    open(os.path.join(bin_dir, "pip"), "w").write("#!/bin/sh\nexit 0\n")
    open(os.path.join(bin_dir, "pytest"), "w").write(f'#!/bin/sh\nexec "{sys.executable}" -m pytest "$@"\n')
    for name in ("pip", "pytest"):
        os.chmod(os.path.join(bin_dir, name), 0o755)
    wf = ts.load_yaml(open(WORKFLOW).read())
    jobs = wf["jobs"]
    logs = []

    def one(key, needs=None, matrix=None):
        out_file = os.path.join(tmp_path, f"out-{len(logs)}")
        open(out_file, "w").close()
        ws = os.path.join(tmp_path, f"run{len(logs)}", "ws")
        os.makedirs(os.path.dirname(ws))
        end, log = run_job(jobs[key], wf, context(event, needs, matrix), event, trees, ws, bin_dir, out_file)
        logs.append(f"--- {key} {matrix.get('id') if matrix else ''}: {end}\n{log[-2500:]}")
        outs = dict(line.split("=", 1) for line in open(out_file).read().splitlines() if "=" in line)
        return end, outs

    end, outs = one("list")
    rows_text = outs.get("matrix", "")
    rows = json.loads(rows_text) if end == "success" and rows_text else []
    results = [one("check", {"list": {"outputs": {"matrix": rows_text}}}, row)[0] for row in rows]
    result = "skipped" if not rows else ("success" if all(r == "success" for r in results) else "failure")
    gate, _ = one("gate", {"list": {"outputs": {"matrix": rows_text}, "result": end},
                           "check": {"result": result}})
    ran = open(log_file).read().splitlines() if os.path.exists(log_file) else []
    return gate == "success", ran, "\n".join(logs)


def test_the_queue_makes_its_check_list_with_mains_copy_of_dokimas_code(record_property, tmp_path):
    """In the merge queue, main's copy of Dokima's code lists and annotates the checks.

    Proves 388.1. Queues a pull request whose dokima/checks.py was edited, runs every job of acceptance-criteria.yml on the merge queue's
    event with another pull request queued ahead whose dokima/checks.py was edited too, and checks that main's copy
    listed the checks and annotated the tests while neither the queued commit's copy nor the one queued ahead ever
    ran. Then opens the same pull request (pull_request_target) and checks the same holds there, as before."""
    record_property("proves", "388.1")
    for event in ("merge_group", "pull_request_target"):
        _, ran, logs = queue(tmp_path / event, event, APP_GOOD)
        theirs = [r for r in ran if not r.startswith("main ")]
        assert not theirs, (f"388.1: on {event} a copy of dokima/checks.py other than main's ran "
                            f"({', '.join(theirs)}), so a pull request's edit judges it:\n{logs}")
        assert "main matrix" in ran, f"388.1: on {event} main's copy of Dokima's code never made the check list:\n{logs}"
        assert "main annotate" in ran, \
            f"388.1: on {event} main's copy of Dokima's code never annotated the tests that ran:\n{logs}"


def test_the_queue_still_tests_the_queued_commits_code(record_property, tmp_path):
    """In the merge queue, working code passes its checks and broken code fails them.

    Proves 388.2. Queues a pull request whose dokima/checks.py was edited to list one always-passing check. With working code the
    gate must pass, so the queue still runs the plan's checks on the queued commit. With broken code the gate must
    fail though main's code works, so the tests that ran were the queued commit's, and the edited check list did not
    wave it through. The same two cases on the pull request itself must give the same verdicts."""
    record_property("proves", "388.2")
    for event in ("merge_group", "pull_request_target"):
        passed, _, logs = queue(tmp_path / f"{event}-good", event, APP_GOOD)
        assert passed, f"388.2: on {event} a pull request with working code did not pass its acceptance criteria:\n{logs}"
        passed, ran, logs = queue(tmp_path / f"{event}-bad", event, APP_BAD)
        assert not passed, (f"388.2: on {event} a pull request with broken code that edits dokima/checks.py passed "
                            f"its acceptance criteria (copies that ran: {', '.join(ran) or 'none'}):\n{logs}")
        assert "main matrix" in ran and "1 failed" in logs, \
            f"388.2: on {event} the broken pull request did not fail on the plan's own test:\n{logs}"

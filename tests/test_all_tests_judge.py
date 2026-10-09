"""The all tests check is judged by main's copy of its workflow, so a pull request cannot rewrite its own judge (#260).

These tests play GitHub's part when a pull request is opened or updated. GitHub runs a workflow from the pull
request's own branch when that copy listens on `pull_request`, and main's copy when main's copy listens on
`pull_request_target`; both can run at once. Every workflow of this repo with a job named "All tests" is copied into a
temp "main" tree, next to a tiny project (app.py and its test). The pull request's tree holds the same project, its
code fixed or broken, and its own copy of those workflows, kept, edited or deleted. Each "All tests" job GitHub would
start is then run step by step: `actions/checkout` copies the tree its `ref` names (main's by default on
pull_request_target, the pull request's on pull_request) and, unless told `persist-credentials: false`, leaves the token
in the checkout's .git/config the way the real action does; other `uses:` steps are skipped; every `run:` script runs
with bash, its `${{ }}` filled in, with a `pip` that does nothing. The check counts as passed only when every
"All tests" run on the pull request passed or was skipped, the same rule autopilot reads before it merges
(dokima/agent.py, unproven()).
"""
import json
import os
import re
import shutil
import subprocess

import test_start as ts

ROOT = ts.ROOT
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
CHECK = "All tests"
HEAD_SHA = "1111111111111111111111111111111111111111"
BASE_SHA = "2222222222222222222222222222222222222222"
HEAD_REF = "work/issue-1"
TOKEN = "ghs_TOKENvalue260xyz"
SECRET = "SECRETkey260xyz"

APP_GOOD = "def value():\n    return 1\n"
APP_BAD = "def value():\n    return 2\n"
TEST_APP = '''"""The tiny project's one test; it also notes everything the run lets it see."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import app  # noqa: E402


def seen():
    """Every environment value and the text of every file in the machine's workspace."""
    files = {}
    for top, dirs, names in os.walk(os.environ.get("DOKIMA_TEST_WORKSPACE", HERE)):
        for n in names:
            try:
                files[os.path.join(top, n)] = open(os.path.join(top, n), errors="replace").read()
            except OSError:
                pass
    return {"env": dict(os.environ), "files": files}


def test_value():
    with open(DUMP, "a") as f:
        f.write(json.dumps(seen()) + "\\n")
    assert app.value() == 1
'''


def judge_files():
    """The names of this repo's workflow files that hold a job named "All tests"."""
    out = []
    for name in sorted(os.listdir(WORKFLOWS)):
        if name.endswith((".yml", ".yaml")):
            jobs = ts.load_yaml(open(os.path.join(WORKFLOWS, name)).read()).get("jobs") or {}
            if any(isinstance(j, dict) and j.get("name") == CHECK for j in jobs.values()):
                out.append(name)
    assert out, "the repo has no workflow with a job named 'All tests'"
    return out


def project(where, app, dump, workflows):
    """Write the tiny project into a tree: app.py, its test, and the given workflow files (name -> text)."""
    os.makedirs(os.path.join(where, "tests"), exist_ok=True)
    os.makedirs(os.path.join(where, ".github", "workflows"), exist_ok=True)
    open(os.path.join(where, "app.py"), "w").write(app)
    open(os.path.join(where, "tests", "test_app.py"), "w").write(TEST_APP.replace("open(DUMP", f"open({dump!r}"))
    for name, text in workflows.items():
        open(os.path.join(where, ".github", "workflows", name), "w").write(text)


def triggers(wf):
    """The events a workflow listens on, with their `types:` filter (None when it takes every type)."""
    on = wf.get("on", wf.get(True, ""))
    if isinstance(on, str):
        return {on: None} if on else {}
    if isinstance(on, list):
        return {e: None for e in on}
    return {e: (v.get("types") if isinstance(v, dict) else None) for e, v in on.items()}


def listens(wf, event):
    """Whether GitHub starts this workflow when a pull request is opened or updated, for this event name."""
    t = triggers(wf)
    return event in t and (not t[event] or {"opened", "synchronize"} & set(t[event]))


def tree_for(ref, event, base, head):
    """The tree a checkout of this ref gives on this event."""
    if ref in ("", None):
        return base if event == "pull_request_target" else head
    if ref in (HEAD_SHA, HEAD_REF, "refs/pull/7/head", "refs/pull/7/merge"):
        return head
    if ref in (BASE_SHA, "main", "refs/heads/main"):
        return base
    raise AssertionError(f"the tests do not know which tree the checkout ref {ref!r} names")


def context(event):
    """The `${{ }}` contexts GitHub gives a pull request's run on this event."""
    return ts.Ctx({k: ts.Ctx(v) for k, v in {
        "github": {"event_name": event, "repository": "o/r", "token": TOKEN, "head_ref": HEAD_REF, "base_ref": "main",
                   "sha": BASE_SHA if event == "pull_request_target" else HEAD_SHA, "server_url": "https://github.com",
                   "run_id": "1", "workspace": "", "event": {
                       "number": 7, "repository": {"default_branch": "main"},
                       "pull_request": {"number": 7, "head": {"sha": HEAD_SHA, "ref": HEAD_REF},
                                        "base": {"sha": BASE_SHA, "ref": "main"}}}},
        "secrets": {"GITHUB_TOKEN": TOKEN, "DOKIMA_APP_KEY": SECRET},
        "vars": {"DOKIMA_APP_ID": "1"}, "env": {}, "steps": {}, "needs": {}, "matrix": {}, "inputs": {}}.items()})


def run_job(job, wf, event, base, head, ws, bin_dir):
    """Run one job the way GitHub would; returns 'success', 'failure' or 'skipped', and the log."""
    ctx = context(event)
    status = {"failed": False}
    cond = str(job.get("if") or "").replace("${{", "").replace("}}", "").strip()
    if not ts.evaluate(ts.condition(cond), ctx, status):
        return "skipped", ""
    assert "strategy" not in job, "the tests do not run matrix jobs"
    shutil.rmtree(ws, ignore_errors=True)
    os.makedirs(ws)
    env = {**(wf.get("env") or {}), **(job.get("env") or {})}
    workdir = ((job.get("defaults") or {}).get("run") or {}).get("working-directory") or \
        ((wf.get("defaults") or {}).get("run") or {}).get("working-directory") or "."
    log = []
    for step in job.get("steps") or []:
        scond = str(step.get("if") or "").replace("${{", "").replace("}}", "").strip()
        if not ts.evaluate(ts.condition(scond), ctx, status):
            continue
        uses = str(step.get("uses") or "")
        if uses.startswith("actions/checkout"):
            w = {k: ts.fill(v, ctx, status) for k, v in (step.get("with") or {}).items()}
            dest = os.path.join(ws, w.get("path") or ".")
            if os.path.abspath(dest) == os.path.abspath(ws):
                for n in os.listdir(ws):
                    p = os.path.join(ws, n)
                    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
                os.rmdir(ws)
            else:
                shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(tree_for(w.get("ref") or "", event, base, head), dest)
            os.makedirs(os.path.join(dest, ".git"), exist_ok=True)
            if str(w.get("persist-credentials", "true")).lower() != "false":
                open(os.path.join(dest, ".git", "config"), "w").write(
                    f'[http "https://github.com/"]\n\textraheader = AUTHORIZATION: basic x-access-token:{w.get("token") or TOKEN}\n')
            continue
        if uses:
            continue
        if "run" not in step:
            continue
        script = ts.fill(step["run"], ctx, status)
        senv = {k: ts.fill(v, ctx, status) for k, v in {**env, **(step.get("env") or {})}.items()}
        cwd = os.path.join(ws, ts.fill(step.get("working-directory") or workdir, ctx, status))
        path = os.path.join(ws, "..", f"step-{len(log)}.sh")
        open(path, "w").write(script)
        p = subprocess.run(ts.github_shell(step, job, wf.get("defaults")) + [path], cwd=cwd, capture_output=True,
                           text=True, timeout=120,
                           env={"PATH": bin_dir + os.pathsep + os.environ["PATH"], "HOME": os.path.join(ws, ".."),
                                "DOKIMA_TEST_WORKSPACE": ws, "PYTHONDONTWRITEBYTECODE": "1", **senv})
        log.append(f"$ {script.strip()}\n{p.stdout}{p.stderr}")
        if p.returncode != 0:
            status["failed"] = True
            return "failure", "\n".join(log)
    return "success", "\n".join(log)


def pull_request(tmp_path, app, edit=None):
    """Open a pull request on the tiny project and run every "all tests" job GitHub would start for it.

    `app` is the pull request's app.py (main's is always the good one); `edit` turns main's text of a workflow file
    into the pull request's copy, or returns None to delete it. Returns [(whose copy, conclusion, log)] and the dump
    file every test run of the project appended what it saw to."""
    tmp_path = str(tmp_path)
    names = judge_files()
    real = {n: open(os.path.join(WORKFLOWS, n)).read() for n in names}
    theirs = {}
    for n, text in real.items():
        new = edit(text) if edit else text
        if new is not None:
            theirs[n] = new
    dump = os.path.join(tmp_path, "seen.jsonl")
    base, head = os.path.join(tmp_path, "main"), os.path.join(tmp_path, "pr")
    project(base, APP_GOOD, dump, real)
    project(head, app, dump, theirs)
    bin_dir = os.path.join(tmp_path, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    open(os.path.join(bin_dir, "pip"), "w").write("#!/bin/sh\nexit 0\n")
    os.chmod(os.path.join(bin_dir, "pip"), 0o755)
    runs = []
    for whose, tree, event in (("the pull request's", head, "pull_request"), ("main's", base, "pull_request_target")):
        for n in sorted(os.listdir(os.path.join(tree, ".github", "workflows"))):
            wf = ts.load_yaml(open(os.path.join(tree, ".github", "workflows", n)).read())
            if not isinstance(wf, dict) or not listens(wf, event):
                continue
            for job in (wf.get("jobs") or {}).values():
                if isinstance(job, dict) and job.get("name") == CHECK:
                    ws = os.path.join(tmp_path, f"run{len(runs)}", "ws")
                    os.makedirs(os.path.dirname(ws), exist_ok=True)
                    end, log = run_job(job, wf, event, base, head, ws, bin_dir)
                    runs.append((f"{whose} copy of {n}", end, log))
    return runs, dump


def green(runs):
    """Whether the pull request's all tests check counts as passed: at least one run, and every run passed or skipped."""
    return bool(runs) and all(end in ("success", "skipped") for _, end, _ in runs)


def show(runs):
    """The runs, in a line each, with the log of each run that did not pass."""
    return "\n".join(f"- {who}: {end}" + ("" if end == "success" else f"\n{log[-1500:]}") for who, end, log in runs) \
        or "(GitHub would start no all tests run)"


def always_passes(text):
    """A pull request's copy of the workflow whose every pytest command is replaced by `true`."""
    new = re.sub(r"(?m)\b(?:python3? -m )?pytest\b(?!\s*$)[^\n]*$", "true", text)
    assert new != text, "test setup: found no pytest command to replace in the all tests workflow"
    return new


def on_block(text, events):
    """A copy of the workflow listening only on the given events."""
    return re.sub(r"(?ms)^on:.*?(?=^[A-Za-z])", "on:\n" + "".join(f"  {e}:\n" for e in events), text, count=1)


def test_all_tests_runs_mains_workflow_on_the_pull_requests_code(record_property, tmp_path):
    """The all tests check runs main's copy of its workflow, and the code it tests is the pull request's.

    Plays out GitHub opening a pull request that leaves the workflow alone. Main's copy must be among the all tests
    runs GitHub starts, and it must be the only one: GitHub may not also start the pull request's own copy, which the
    pull request could rewrite. A pull request whose code is right passes; one whose code is broken fails, though
    main's code is right, so the check tests the pull request's code and not main's."""
    record_property("proves", "260.1")
    runs, _ = pull_request(tmp_path / "good", APP_GOOD)
    assert any(who.startswith("main's") for who, _, _ in runs), \
        f"260.1: GitHub would not run main's copy of the all tests workflow on a pull request, only:\n{show(runs)}"
    theirs = [who for who, _, _ in runs if not who.startswith("main's")]
    assert not theirs, \
        f"260.1: GitHub also runs {', '.join(theirs)}, so the pull request's own copy still judges it:\n{show(runs)}"
    assert green(runs), f"260.1: a pull request with working code did not pass all tests:\n{show(runs)}"
    runs, _ = pull_request(tmp_path / "bad", APP_BAD)
    assert any(who.startswith("main's") for who, _, _ in runs), \
        f"260.1: GitHub would not run main's copy of the all tests workflow on a pull request, only:\n{show(runs)}"
    assert not green(runs), \
        f"260.1: a pull request with broken code passed all tests, so its own code was not tested:\n{show(runs)}"


def test_all_tests_sees_no_secret_and_no_token(record_property, tmp_path):
    """While the pull request's tests run, they can find no key and no GitHub token, anywhere on the machine.

    Runs main's all tests job on a pull request whose test writes down every environment value and every file in the
    workspace, and checks neither the app's key nor the run's GitHub token is among them (the checkout must not leave
    the token behind). Also checks the all tests run actually happened, so a run that saw nothing cannot pass. Then
    reads the workflow: it may name no key and open no keyed environment, and its token must be limited to read."""
    record_property("proves", "260.2")
    runs, dump = pull_request(tmp_path, APP_GOOD)
    mains = [r for r in runs if r[0].startswith("main's")]
    assert mains, f"260.2: GitHub would not run main's copy of the all tests workflow:\n{show(runs)}"
    assert os.path.exists(dump), f"260.2: the pull request's tests never ran:\n{show(runs)}"
    for line in open(dump):
        seen = json.loads(line)
        for value, what in ((SECRET, "the app's key"), (TOKEN, "the run's GitHub token")):
            for k, v in seen["env"].items():
                assert value not in v, f"260.2: the pull request's tests can read {what} in the environment ({k})"
            for path, text in seen["files"].items():
                assert value not in text, f"260.2: the pull request's tests can read {what} in the file {path}"
    no_key_and_read_only()


def permissions_read_only(inline, block):
    """Whether a `permissions:` setting grants only read or none: `read-all`, `{}`, or a list of read/none entries."""
    if inline:
        return inline in ("read-all", "{}")
    entries = [line.split(":", 1) for line in block.splitlines() if line.strip() and not line.strip().startswith("#")]
    return bool(entries) and all(len(e) == 2 and e[1].split("#")[0].strip() in ("read", "none") for e in entries)


def no_key_and_read_only():
    """Fail unless the all tests workflow names no key, opens no keyed environment and asks GitHub only for read access.

    Reads main's copy of every workflow holding the all tests job. On pull_request_target GitHub hands a workflow the
    repo's default token, which can write, unless the workflow limits it, so a top-level `permissions:` of only read or
    none is required, and any job's own `permissions:` may only say read or none. No `secrets.` and no `environment:`
    (an environment is how this repo's other workflows reach their keys) may appear in it."""
    for name in judge_files():
        text = open(os.path.join(WORKFLOWS, name)).read()
        assert "secrets." not in text, f"260.2: {name} names a key while it runs the pull request's code"
        assert not re.search(r"(?m)^\s+environment:", text), \
            f"260.2: {name} opens an environment, which hands out its keys, while it runs the pull request's code"
        assert not re.search(r"(?m)^\s+[a-z-]+:\s*write\b", text) and "write-all" not in text, \
            f"260.2: {name} asks for write access while it runs the pull request's code"
        top = re.search(r"(?m)^permissions:[ \t]*(\S*)[ \t]*\n((?:[ \t]+.*\n)*)", text)
        assert top and permissions_read_only(top.group(1), top.group(2)), \
            f"260.2: {name} does not limit its token to read, so the pull request's tests could get write access"
        for job in re.finditer(r"(?m)^    permissions:[ \t]*(\S*)[ \t]*\n((?:      .*\n)*)", text):
            assert permissions_read_only(job.group(1), job.group(2)), \
                f"260.2: a job in {name} does not limit its token to read"


ATTACKS = {
    "makes its copy always pass": always_passes,
    "makes its copy always pass and run on pull_request": lambda t: on_block(always_passes(t), ["pull_request"]),
    "makes its copy always pass and run on pull_request_target":
        lambda t: on_block(always_passes(t), ["pull_request_target"]),
    "deletes the workflow": lambda t: None,
}


def test_a_pull_request_cannot_rewrite_how_its_own_tests_are_judged(record_property, tmp_path):
    """A pull request that edits the all tests workflow to pass no matter what still fails when its tests fail.

    The pull request breaks the code its tests check, then edits its copy of the workflow four ways: every pytest
    command replaced by `true`, the same while listening on pull_request, the same on pull_request_target, and the file
    deleted. Each time main's all tests run must still happen and fail, so the check fails. A pull request that edits
    the workflow harmlessly and whose code works still passes, so editing the file is not punished in itself."""
    record_property("proves", "260.3")
    for i, (how, edit) in enumerate(ATTACKS.items()):
        runs, _ = pull_request(tmp_path / f"a{i}", APP_BAD, edit)
        mains = [end for who, end, _ in runs if who.startswith("main's")]
        assert mains and "failure" in mains, \
            f"260.3: a pull request that {how} kept main's all tests run from failing on its broken code:\n{show(runs)}"
        assert not green(runs), \
            f"260.3: a pull request that {how} passed all tests with broken code:\n{show(runs)}"
    runs, _ = pull_request(tmp_path / "harmless", APP_GOOD, lambda t: t + "# a note\n")
    assert green(runs), f"260.3: a pull request that only adds a comment to the workflow did not pass:\n{show(runs)}"

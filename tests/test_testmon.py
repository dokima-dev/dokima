"""Code reviews run only affected tests, picked by testmon from main's baseline (issue #539).

Before each code review, `.github/workflows/agent.yml` runs the tests on the reviewer's machine and writes
`$PACK/tests.txt` and `$PACK/tests.xml`. With this issue that run uses pytest-testmon: a workflow on every push to main
(`.github/workflows/testmon.yml`) runs every test with `--testmon` and saves `.testmondata` to GitHub's cache, and
agent.yml restores it before the run, so only the tests the change can affect run. With no usable baseline (none
restored, or a file testmon cannot read) the machine runs every test.

CI has neither testmon nor PyYAML, so these tests read the workflow files line by line, and run the shell of the
agent.yml step that writes `tests.txt`, cut out of the workflow GitHub runs, with a fake `python3` and `pytest` on PATH.
The fake behaves as pytest-testmon 2.2 really does (checked by hand): with `--testmon` and a readable baseline it runs
only the affected test; with `--testmon` and no baseline it runs every test; with `--testmon` and a file that is not a
database it stops at once with an INTERNALERROR and exit code 3. Without `--testmon` it runs every test. Each call is
logged, so the tests see which run produced the files the reviewer reads.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_settings_test_setup import SetupRun  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AGENT = os.path.join(ROOT, ".github", "workflows", "agent.yml")
BASELINE = os.path.join(ROOT, ".github", "workflows", "testmon.yml")

FAKE = '''#!%(python)s
"""A stand-in for pytest with pytest-testmon: logs each call and acts as testmon does on the baseline it finds."""
import json, os, sys
args = sys.argv[1:]
if os.path.basename(sys.argv[0]) == "python3":
    if args[:2] != ["-m", "pytest"]:
        os.execv(%(python)r, [%(python)r] + args)
    args = args[2:]
data = os.environ.get("TESTMON_DATAFILE") or os.path.join(os.getcwd(), ".testmondata")
select = "--testmon" in args or "--testmon-forceselect" in args
uses = select or "--testmon-noselect" in args
readable = os.path.isfile(data) and open(data, "rb").read(16) == b"SQLite format 3\\x00"
xml = next((a.split("=", 1)[1] for a in args if a.startswith("--junitxml=")), None)
if xml is None and "--junitxml" in args:
    xml = args[args.index("--junitxml") + 1]
if uses and os.path.isfile(data) and not readable:
    mode, code = "crashed", 3
    print("INTERNALERROR> sqlite3.DatabaseError: file is not a database")
elif select and readable:
    mode, code = "affected", 0
    print("PASSED tests/test_changed.py::test_changed")
    print("1 passed, 41 deselected in 0.10s")
else:
    mode, code = "all", 0
    print("PASSED tests/test_changed.py::test_changed")
    print("42 passed in 1.00s")
if xml and code == 0:
    open(xml, "w").write('<testsuites><testsuite name="%%s"/></testsuites>' %% mode)
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"args": args, "mode": mode}) + "\\n")
sys.exit(code)
'''


def workflow_lines(path):
    """The lines of a workflow file, failing with its name when it is missing."""
    assert os.path.isfile(path), f"{os.path.relpath(path, ROOT)} does not exist"
    return open(path).read().splitlines()


def review_step(lines):
    """The shell of the agent.yml step that writes `$PACK/tests.txt`, and that step's line number."""
    for i, line in enumerate(lines):
        if line.strip() != "run: |":
            continue
        indent = len(line) - len(line.lstrip())
        body = []
        for later in lines[i + 1:]:
            if later.strip() and len(later) - len(later.lstrip()) <= indent:
                break
            body.append(later)
        script = "\n".join(body)
        if "tests.txt" in script and "pytest" in script:
            return script, i
    raise AssertionError("agent.yml has no step that runs pytest into $PACK/tests.txt")


def run_tests_step(tmp_path, baseline):
    """Run agent.yml's test step in a fake checkout holding `baseline` ("good", "broken" or None).

    Returns (the logged pytest calls, tests.txt, whether tests.xml exists, the step's exit code and output)."""
    script, _ = review_step(workflow_lines(AGENT))
    work = tmp_path / "work"
    pack = tmp_path / "pack"
    bin_dir = tmp_path / "bin"
    for d in (work, pack, bin_dir):
        d.mkdir(parents=True)
    if baseline == "good":
        db = sqlite3.connect(work / ".testmondata")
        db.execute("CREATE TABLE metadata (dataid TEXT PRIMARY KEY, data TEXT)")
        db.commit()
        db.close()
    elif baseline == "broken":
        (work / ".testmondata").write_text("garbage\n")
    for name in ("python3", "pytest"):
        (bin_dir / name).write_text(FAKE % {"python": sys.executable})
        (bin_dir / name).chmod(0o755)
    log = tmp_path / "calls.jsonl"
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "PACK": str(pack),
           "FAKE_LOG": str(log), "STAGE": "pr", "GITHUB_WORKSPACE": str(work)}
    env.pop("TESTMON_DATAFILE", None)
    p = subprocess.run(["bash", "-e", "-c", script], cwd=work, env=env, capture_output=True, text=True, timeout=30)
    calls = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    txt = (pack / "tests.txt").read_text() if (pack / "tests.txt").exists() else None
    return calls, txt, (pack / "tests.xml").exists(), f"exit {p.returncode}\n{p.stdout}{p.stderr}"


def static_key(value):
    """The fixed start of a cache key, before its first `${{ }}` expression."""
    return value.strip().strip("'\"").split("${{")[0]


def cache_step(lines, action):
    """The path and keys of the first step using this cache action, and its line."""
    start = next((i for i, l in enumerate(lines) if f"uses: {action}@" in l), None)
    if start is None:
        return None, None
    indent = len(lines[start]) - len(lines[start].lstrip())
    found = {"restore-keys": []}
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if line.strip() and len(line) - len(line.lstrip()) <= indent and line.strip().startswith("- "):
            break
        m = re.match(r"\s*(path|key|restore-keys):\s*(.*)$", line)
        if m and m.group(1) == "restore-keys":
            rest = m.group(2).strip()
            if rest in ("|", ">", ""):
                deeper = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) > deeper:
                    found["restore-keys"].append(static_key(lines[i]))
                    i += 1
                continue
            found["restore-keys"].append(static_key(rest))
        elif m:
            found[m.group(1)] = m.group(2).strip().strip("'\"")
        i += 1
    return found, start


def test_code_review_runs_only_affected_tests(tmp_path, record_property):
    """A code review runs only the tests its change can affect, using main's testmon baseline.

    Proves 539.1. Checks that a workflow on every push to main runs the tests with testmon and saves `.testmondata`
    to GitHub's cache, that agent.yml installs testmon (both installs seen by running each job with the default
    settings) and restores that cache, under a matching key, before its test
    step, and then runs that step with a readable baseline in place: the run that writes `tests.txt` and `tests.xml`
    must be testmon's, choosing only the affected test, not every test."""
    record_property("proves", "539.1")
    base = workflow_lines(BASELINE)
    text = "\n".join(base)
    assert re.search(r"^\s*push:", text, re.M) and re.search(r"branches:\s*\[\s*main\s*\]", text), \
        "539.1: testmon.yml does not run on every push to main, so no baseline is recorded there"
    got = SetupRun(tmp_path / "base", "testmon.yml", "baseline", None).installed("539.1")
    assert "pytest-testmon" in got, f"539.1: testmon.yml does not install pytest-testmon before its tests; it installs {got}"
    assert any("pytest" in l and "--testmon" in l for l in base), \
        "539.1: testmon.yml does not run the tests with --testmon, so it records no baseline"
    saved, _ = cache_step(base, "actions/cache/save")
    assert saved and saved.get("path") == ".testmondata", \
        "539.1: testmon.yml does not save .testmondata with actions/cache/save"

    agent = workflow_lines(AGENT)
    got = SetupRun(tmp_path / "agent", "agent.yml", "run", None).installed("539.1")
    assert "pytest-testmon" in got, \
        f"539.1: agent.yml does not install pytest-testmon on the code review's machine; it installs {got}"
    restored, at = cache_step(agent, "actions/cache/restore")
    assert restored and restored.get("path") == ".testmondata", \
        "539.1: agent.yml does not restore .testmondata with actions/cache/restore"
    _, step_at = review_step(agent)
    assert at < step_at, "539.1: agent.yml restores the baseline only after its test step has run"
    prefixes = [static_key(restored.get("key", ""))] + restored["restore-keys"]
    assert any(p and static_key(saved.get("key", "")).startswith(p) for p in prefixes), \
        f"539.1: agent.yml restores keys {prefixes}, none of which matches the key testmon.yml saves ({saved.get('key')})"

    calls, txt, xml, out = run_tests_step(tmp_path, "good")
    assert calls, f"539.1: the test step never ran pytest\n{out}"
    assert calls[-1]["mode"] == "affected", \
        f"539.1: with a readable baseline the code review still ran every test: pytest {calls[-1]['args']}\n{out}"
    assert txt is not None and "41 deselected" in txt, \
        f"539.1: tests.txt does not hold testmon's run of the affected tests\n{txt}\n{out}"
    assert xml, f"539.1: tests.xml is missing after testmon's run\n{out}"


def test_no_usable_baseline_runs_every_test(tmp_path, record_property):
    """With no usable baseline, the code review's machine runs every test.

    Proves 539.2. Runs agent.yml's test step three times: with no baseline restored and with a `.testmondata` that is
    not a database, each must end in a run of every test whose output is in `tests.txt` and `tests.xml`, not in
    testmon's crash; beside them, a readable baseline must run only the affected tests, so a step that always runs
    every test fails."""
    record_property("proves", "539.2")
    for baseline, why in ((None, "no baseline was restored"), ("broken", "the baseline is not a database")):
        calls, txt, xml, out = run_tests_step(tmp_path / (baseline or "none"), baseline)
        assert calls, f"539.2: when {why}, the test step never ran pytest\n{out}"
        assert calls[-1]["mode"] == "all", \
            f"539.2: when {why}, the last run did not run every test ({calls[-1]['mode']}): pytest {calls[-1]['args']}\n{out}"
        assert txt is not None and "42 passed" in txt and "INTERNALERROR" not in txt, \
            f"539.2: when {why}, tests.txt does not hold the run of every test\n{txt}\n{out}"
        assert xml, f"539.2: when {why}, tests.xml is missing\n{out}"
        assert out.startswith("exit 0"), f"539.2: when {why}, the test step failed\n{out}"
    calls, _, _, out = run_tests_step(tmp_path / "good", "good")
    assert calls and calls[-1]["mode"] == "affected", \
        f"539.2: with a readable baseline the step still runs every test, so it never picks affected tests\n{out}"

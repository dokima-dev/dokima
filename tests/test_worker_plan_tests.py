"""The worker's end check runs the plan's tests; a red one blocks it (#595).

The worker runs `python3 -m dokima.agent check work FILE PLAN N` itself before it stops, and agent.yml runs the same
command again once the agent is done ("Code checks the hand-back"), both with ROLE=worker in the job's environment.
Each test here runs that real command from outside, with ROLE=worker, from a temp folder that stands in for the
worker's branch: it holds its own tests/ and the plan for issue 9 (criteria 9.1 to 9.3) lists tests there. Nothing of
the repo's own suite is run by these checks, so they finish in seconds.

Outside a worker's run (ROLE unset, as tests/conftest.py makes it for every test) the check stays a shape check, so the
older tests that check made-up plans keep passing.
"""
import json
import os
import subprocess
import sys

from dokima import agent
from tests.test_handback_check import STORY, WORK

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# A test that notes its own name in the file named by $MARK, then passes or fails.
PASSING = "import os\n\ndef {name}():\n    open(os.environ['MARK'], 'a').write('{name}\\n')\n\n"
FAILING = "import os\n\ndef {name}():\n    open(os.environ['MARK'], 'a').write('{name}\\n')\n    assert False, 'red on purpose'\n\n"


def branch(tmp_path, files, tests):
    """A temp folder standing in for the worker's branch, with plan 9 and a hand-back.

    `files` maps a path under the folder to its test functions, each (name, passes). Returns the folder."""
    root = tmp_path / "branch"
    (root / "tests").mkdir(parents=True)
    for path, funcs in files.items():
        (root / path).write_text("".join((PASSING if ok else FAILING).format(name=n) for n, ok in funcs))
    (root / "plan.json").write_text(json.dumps({**STORY, "tests": tests}))
    (root / "work.json").write_text(json.dumps(WORK))
    return root


def run_check(root):
    """Run the worker's end check as its run does; return exit code, output, marks.

    `marks` lists the name of every test that actually ran, as each wrote it to $MARK."""
    mark = root / "ran.txt"
    env = {**os.environ, "PYTHONPATH": ROOT, "ROLE": "worker", "MARK": str(mark)}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE"):
        env.pop(k, None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "check", "work", str(root / "work.json"),
                        str(root / "plan.json"), "9"], cwd=root, env=env, capture_output=True, text=True, timeout=120)
    ran = mark.read_text().split() if mark.exists() else []
    return p.returncode, p.stdout + p.stderr, ran


def test_end_check_runs_every_plan_test(record_property, tmp_path):
    """The worker's end check runs every test the approved plan lists.

    Proves 595.1.
    The plan lists three tests across two files on the branch, all green. The check must run each one (each writes
    its name to a marker file) and exit 0. Today the check reads only the shape of work.json, so no test runs."""
    record_property("proves", "595.1")
    root = branch(tmp_path, {"tests/test_x.py": [("test_a", True), ("test_b", True)], "tests/test_y.py": [("test_c", True)]},
                  {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_y.py::test_c"]})
    code, out, ran = run_check(root)
    assert "Traceback" not in out, f"595.1: the worker's check crashed:\n{out[-800:]}"
    missing = [t for t in ("test_a", "test_b", "test_c") if t not in ran]
    assert not missing, f"595.1: the worker's end check did not run the plan's tests {missing}; it ran {ran}.\n{out[-800:]}"
    assert code == 0, f"595.1: every plan test passed, yet the worker's check failed (exit {code}):\n{out[-800:]}"


def test_failing_plan_test_refuses_hand_back_naming_it(record_property, tmp_path):
    """A failing or missing plan test refuses the worker's hand-back, named.

    Proves 595.2.
    Plan 9 lists test_a (green), test_b and test_c (both red) and test_gone, which the branch does not have. The check
    must exit 1 and print each of test_b, test_c and test_gone by its full id. The same hand-back with every listed
    test green passes, so the refusal comes from the tests, not the hand-back."""
    record_property("proves", "595.2")
    tests = {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b", "tests/test_x.py::test_gone"],
             "9.3": ["tests/test_x.py::test_c"]}
    root = branch(tmp_path, {"tests/test_x.py": [("test_a", True), ("test_b", False), ("test_c", False)]}, tests)
    code, out, ran = run_check(root)
    assert code == 1, f"595.2: plan tests failed, yet the worker's hand-back was accepted (exit {code}):\n{out[-800:]}"
    for t in ("tests/test_x.py::test_b", "tests/test_x.py::test_c", "tests/test_x.py::test_gone"):
        assert t in out, f"595.2: the refusal does not name the failing plan test {t}; it said:\n{out[-1200:]}"

    green = branch(tmp_path / "green", {"tests/test_x.py": [("test_a", True), ("test_b", True), ("test_c", True), ("test_gone", True)]}, tests)
    code, out, ran = run_check(green)
    assert code == 0, f"595.2: with every plan test green the worker's check still refused (exit {code}):\n{out[-800:]}"


def test_run_ending_red_hands_back_blocked(record_property, tmp_path):
    """A worker still red at its run's end is recorded as blocked, naming the tests.

    Proves 595.3.
    Runs the real end check on a branch where test_b fails, then builds the run's record from that check's output the
    way agent.yml does (`agent record`, through build_record) and draws its comment. The comment's opening sentence
    must say the worker is blocked, the comment must name the failing test, and the river must stop rather than start
    the code review. A worker whose tests pass is not called blocked."""
    record_property("proves", "595.3")
    tests = {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_a"]}
    root = branch(tmp_path, {"tests/test_x.py": [("test_a", True), ("test_b", False)]}, tests)
    code, out, _ = run_check(root)
    assert code == 1, f"595.3: the end check passed a branch whose plan test fails (exit {code}):\n{out[-800:]}"
    outdir = tmp_path / "out"
    outdir.mkdir()
    (outdir / "work.json").write_text(json.dumps(WORK))
    rec = agent.build_record("worker", "", str(outdir), out, False, {})
    first = agent.opening(rec)
    assert "blocked" in first.lower(), f"595.3: a worker whose plan tests still fail opens its record with {first!r}, not as blocked"
    body = agent.render(rec)
    assert "tests/test_x.py::test_b" in body, f"595.3: the blocked worker's record does not name its failing test:\n{body[:1500]}"
    step = agent.next_step([], rec, set())
    assert step[0] == "stop", f"595.3: a worker blocked on failing plan tests went on as done: {step}"

    good = agent.build_record("worker", "", str(outdir), "", True, {})
    assert "blocked" not in agent.opening(good).lower(), \
        f"595.3: a worker whose tests pass is called blocked: {agent.opening(good)!r}"

"""A command that hit GitHub's spent hourly request budget says so, and when to try again (#368).

Replays the real "Say why the command started nothing" step of commands.yml with bash, with a fake gh that answers
how much budget is left and logs every other call, and a python3 that must not run while the budget is spent.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_start import load_yaml  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
STEP = "Say why the command started nothing, where it was written"
RESET = 1791750852
AT = __import__("datetime").datetime.fromtimestamp(RESET, __import__("datetime").timezone.utc).strftime("%H:%M UTC")


def step():
    wf = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "commands.yml")).read())
    return next(s for s in wf["jobs"]["say-why"]["steps"] if s.get("name") == STEP)["run"]


def play(tmp_path, graphql_left, rest_left, card="77"):
    bin_dir, log = tmp_path / "bin", tmp_path / "calls"
    bin_dir.mkdir()
    limits = json.dumps([graphql_left, RESET, rest_left, RESET])
    (bin_dir / "gh").write_text(
        "#!/bin/sh\n"
        f"if [ \"$2\" = rate_limit ]; then echo '{limits}' | python3 -c 'import json,sys; print(*json.load(sys.stdin), sep=chr(9))'; exit 0; fi\n"
        f"printf '%s\\n' \"$*\" >> '{log}'\n")
    (bin_dir / "gh").chmod(0o755)
    (bin_dir / "python3").write_text(f"#!/bin/sh\necho \"python3 $*\" >> '{log}'\nexit 0\n")
    (bin_dir / "python3").chmod(0o755)
    real_py = sys.executable
    gh = (bin_dir / "gh").read_text().replace("python3 -c", f"{real_py} -c")
    (bin_dir / "gh").write_text(gh)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": "o/r",
           "NUMBER": "5", "CARD_ID": card, "WHY": "x", "ROLE": "planner", "STAGE": "", "ON_PR": "false"}
    p = subprocess.run(["bash", "-e", "-c", step()], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    return p, (log.read_text() if log.exists() else "")


def test_a_spent_budget_edits_the_card_into_why_and_when_to_try_again(tmp_path):
    p, calls = play(tmp_path, graphql_left=0, rest_left=4000)
    assert p.returncode == 0, p.stderr
    assert "python3" not in calls, f"#368: with the budget spent, code that needs it still ran:\n{calls}"
    assert "api -X PATCH repos/o/r/issues/comments/77" in calls and AT in calls, \
        f"#368: the card does not say the budget is spent and when it refills:\n{calls}"


def test_a_spent_budget_with_no_card_comments_on_the_issue(tmp_path):
    p, calls = play(tmp_path, graphql_left=4000, rest_left=0, card="")
    assert p.returncode == 0, p.stderr
    assert "api repos/o/r/issues/5/comments" in calls and "used up" in calls, \
        f"#368: with no card, nothing says the budget is spent:\n{calls}"


def test_with_budget_left_the_step_says_why_as_before(tmp_path):
    p, calls = play(tmp_path, graphql_left=4000, rest_left=4000)
    assert "python3 -m dokima.agent not-started" in calls and "used up" not in calls, \
        f"#368: with budget left, the usual reason was not written:\n{calls}"

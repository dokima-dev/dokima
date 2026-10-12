"""A code review's record says when every test ran without a usable baseline (#540).

Before a code review, `.github/workflows/agent.yml` runs the tests the change can affect, picked by pytest-testmon
from main's baseline (#539). With no usable baseline (none restored, or one testmon cannot read) it runs every test
instead. The owner only learns that from the run's log; this issue makes the code review's record say so.

These tests run the real thing end to end: the agent.yml step that writes `tests.txt`, cut out of the workflow with
`test_testmon.run_tests_step` (a fake pytest that acts as testmon does), then the workflow's own record step,
`python3 -m dokima.agent record reviewer pr OUT check.txt true LOGS`, on the same pack, and read the comment it writes.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_testmon import run_tests_step  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REPO = "dokima-dev/dokima"
SAYS = re.compile(r"every test ran.*baseline", re.I)


def review_comment(tmp_path, baseline):
    """Run the test step on `baseline`, then the record step; return its comment.

    `baseline` is "good", "broken" or None."""
    calls, _, _, out = run_tests_step(tmp_path, baseline)
    assert calls, f"the test step never ran pytest\n{out}"
    pack = tmp_path / "pack"
    hand, logs = tmp_path / "out", tmp_path / "logs"
    for d in (hand, logs):
        d.mkdir(parents=True)
    review = {"verdict": "approve", "summary": "The work holds.", "raises": [], "answers": [], "asks": []}
    (hand / "review.json").write_text(json.dumps(review))
    (hand / "check.txt").write_text("")
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": REPO,
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "STAGE": "pr", "N": "540"}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "record", "reviewer", "pr", str(hand),
                        str(hand / "check.txt"), "true", str(logs)], cwd=ROOT, env=env, capture_output=True,
                       text=True, timeout=30)
    assert r.returncode == 0 and (hand / "comment.md").exists(), \
        f"the record step failed on a passed code review (exit {r.returncode}):\n{r.stderr[-800:]}"
    return (hand / "comment.md").read_text()


def visible(text):
    """The part of the comment the owner sees without opening a fold."""
    return text.split("<details", 1)[0]


def test_record_says_every_test_ran_without_a_baseline(tmp_path, record_property):
    """With no usable baseline, the code review says every test ran, and why.

    Proves 540.1. Runs the workflow's test step and then its record step, once with no baseline restored and once
    with a baseline testmon cannot read: each comment must show, outside any fold, one line saying every test ran
    because no baseline was usable. Beside them, a readable baseline (only the affected tests ran) must show no such
    line, so a comment that always says it fails."""
    record_property("proves", "540.1")
    for baseline, why in ((None, "no baseline was restored"), ("broken", "the baseline could not be read")):
        text = review_comment(tmp_path / (baseline or "none"), baseline)
        lines = [l for l in visible(text).splitlines() if SAYS.search(l)]
        assert len(lines) == 1, \
            f"540.1: when {why}, the code review's comment does not say, in one line, that every test ran " \
            f"because no baseline was usable:\n{visible(text)}"
    text = review_comment(tmp_path / "good", "good")
    assert not SAYS.search(text), \
        f"540.1: with a readable baseline only the affected tests ran, yet the comment says every test ran:\n{text}"

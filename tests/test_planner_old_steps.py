"""The planner keeps only its check; its old steps, writer and text builder are gone.

Covers #761 (story 2 of #739). Workflows call only `python3 -m dokima.planner check`; the `post` and `rejected`
actions, `render` (which wrote a plan into the issue's text) and `plan_text` (which built that text) are left from the
old label flow. The step tests run the planner's command from the repo root with a fake `gh` first on PATH that logs
every call to a file, so a step that still posts to GitHub is caught without any network.
"""
import json
import os
import re
import stat
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TESTS = os.path.join(ROOT, "tests")
SRC = "https://github.com/o/r/issues/9"


def fake_gh(tmp_path):
    """A folder with a fake `gh` that logs its arguments, and its log file."""
    bin_dir, log = tmp_path / "bin", tmp_path / "gh.log"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(f"#!{sys.executable}\nimport sys\nopen({str(log)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return bin_dir, log


def run(action, out, bin_dir):
    """Run the planner command from the repo root with the fake gh first on PATH."""
    env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", GITHUB_REPOSITORY="o/r",
               GITHUB_RUN_ID="42")
    env.pop("PACK", None)
    return subprocess.run([sys.executable, "-m", "dokima.planner", action, "9", str(out)], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=30)


def logged(log):
    """Every gh call the fake logged, one per line."""
    return log.read_text().splitlines() if log.exists() else []


def feature():
    """A well-formed split the planner's check accepts, so a post step would reach GitHub."""
    def story(title):
        return {"title": title, "user_story": f"Owners get {title}.", "non_functional": [], "depends_on": [],
                "acceptance_criteria": [{"text": f"{title} works.", "source": SRC,
                                         "files": [f"dokima/{title.lower()}.py"]}]}
    return {"kind": "feature", "title": "Slow calls run as jobs", "summary": "Slow calls run as jobs.",
            "feature": "A split.", "stories": [story("First"), story("Second")]}


def test_the_post_step_posts_nothing(record_property, tmp_path):
    """Asking the planner to post a good plan no longer posts anything on the issue.

    Hands back a well-formed split, checks the fake gh logs a call made through it and the planner's check accepts
    the hand-back, then runs the planner's old `post` step on it: the fake gh must log no call. Proves 761.1.
    """
    record_property("proves", "761.1")
    bin_dir, log = fake_gh(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "plan.json").write_text(json.dumps(feature()))
    subprocess.run(["gh", "probe"], env=dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}"), check=True)
    assert logged(log) == ["probe"], f"761.1: the fake gh did not log a call made through it: {logged(log)}"
    log.unlink()
    checked = run("check", out, bin_dir)
    assert checked.returncode == 0, f"761.1: the planner's check rejected the sample split: {checked.stdout}{checked.stderr}"
    run("post", out, bin_dir)
    assert logged(log) == [], f"761.1: the planner's old post step still posted on the issue: {logged(log)}"


def test_the_reject_step_posts_nothing(record_property, tmp_path):
    """Asking the planner to report a rejected plan no longer posts anything on the issue.

    Saves a rejection reason as the check does, checks the fake gh logs a call made through it, then runs the
    planner's old `rejected` step: the fake gh must log no call. Proves 761.2.
    """
    record_property("proves", "761.2")
    bin_dir, log = fake_gh(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "rejected.txt").write_text("plan.json is not valid JSON")
    subprocess.run(["gh", "probe"], env=dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}"), check=True)
    assert logged(log) == ["probe"], f"761.2: the fake gh did not log a call made through it: {logged(log)}"
    log.unlink()
    run("rejected", out, bin_dir)
    assert logged(log) == [], f"761.2: the planner's old reject step still posted on the issue: {logged(log)}"


def test_the_plan_writer_is_gone(record_property):
    """The planner no longer has the old writer of a plan into the issue's text.

    Imports the planner and checks it has no `render`, while its check, `read_output`, is still there. Proves 761.3.
    """
    record_property("proves", "761.3")
    assert hasattr(planner, "read_output"), "761.3: the planner's check went with the old writer"
    assert not hasattr(planner, "render"), "761.3: the planner still has render, the old writer of a plan into the issue"


def test_the_plan_text_builder_is_gone(record_property):
    """The planner no longer has the old plan text builder.

    Imports the planner and checks it has no `plan_text`, while its check, `read_output`, is still there. Proves 761.4.
    """
    record_property("proves", "761.4")
    assert hasattr(planner, "read_output"), "761.4: the planner's check went with the old text builder"
    assert not hasattr(planner, "plan_text"), "761.4: the planner still has plan_text, the old plan text builder"


OLD = re.compile(r"planner\.(render|plan_text)\b|planner\.main\(\[[^\]]*[\"'](post|rejected)[\"']"
                 r"|dokima\.planner[\"'], [\"'](post|rejected)[\"']|run_planner_post")


def test_no_test_reaches_the_old_steps(record_property):
    """No test is left that exercises the planner's old steps, now that they are gone.

    Scans every test file but this one for a call to `render`, `plan_text`, or the `post` or `rejected` step, and
    checks none is left. A sample line calling `planner.render` is caught, so the scan is not blind. The steps
    themselves must be gone too: until they are, no test can show they are unused. Proves 761.5.
    """
    record_property("proves", "761.5")
    assert OLD.search('    new = planner.render("9", ask, story, {})'), "761.5: the scan misses a call to render"
    here = os.path.basename(__file__)
    found = [f"{name}:{k}" for name in sorted(os.listdir(TESTS)) if name.endswith(".py") and name != here
             for k, line in enumerate(open(os.path.join(TESTS, name)), 1) if OLD.search(line)]
    assert found == [], f"761.5: these tests still exercise the planner's deleted steps: {found}"
    left = [name for name in ("render", "plan_text") if hasattr(planner, name)]
    assert left == [], f"761.5: the planner's old steps {left} are still there, so their tests' deletion is unproven"

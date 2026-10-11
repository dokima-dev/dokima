"""#486: failing text goes back to its writer, up to 3 times.

After the agent ends, the workflow runs `python3 -m dokima.restyle OUT FILE`. It checks the hand-back OUT/FILE with
the style checks (word caps and plain words, `dokima.words`). On a failure it resumes the same Claude session (the
`session_id` in OUT/claude.json) with `claude -p --resume SESSION_ID` and a message naming each failing field and why,
then checks again: at most 3 style retries, counted on their own. Whatever still fails after them is written to
OUT/style.txt, one line per failing field, and `python3 -m dokima.agent record` flags it in the run's record and
comment, while the hand-back still posts.

Each test puts a fake `claude` on PATH that logs every call (its arguments and its input) and, when told, rewrites
the hand-back on a given call, so the loop runs for real without any model.
"""
import json
import os
import subprocess
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SESSION = "sess-486-abc"
LONG = " ".join(["word"] * 40)  # 40 words: far over the user_story cap of 20

FAKE = textwrap.dedent("""\
    #!{python}
    import json, os, shutil, sys
    log = os.environ["FAKE_CLAUDE_LOG"]
    calls = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
    stdin = "" if sys.stdin.isatty() else sys.stdin.read()
    calls.append({{"argv": sys.argv[1:], "stdin": stdin}})
    open(log, "w").write("".join(json.dumps(c) + "\\n" for c in calls))
    fix_at, fixed = os.environ.get("FAKE_FIX_AT"), os.environ.get("FAKE_FIXED")
    if fix_at and fixed and len(calls) >= int(fix_at):
        shutil.copy(fixed, os.environ["FAKE_HANDBACK"])
    print(json.dumps({{"type": "result", "session_id": "{session}", "result": "done", "num_turns": 1}}))
    """)


def good_plan():
    """A planner hand-back that passes every style check."""
    return {"kind": "user_story", "summary": "Long texts go back to their writer.",
            "user_story": "Owners only read short plain texts.",
            "acceptance_criteria": [{"text": "Text failing a style check goes back to its writer.",
                                     "words": "sends it back", "source": "https://github.com/o/r/issues/486"}],
            "non_functional": [], "scope": ["dokima/restyle.py"], "out_of_scope": ["The reviewer's own rounds."],
            "tests": {"486.1": ["tests/test_style_retry.py::test_x"]}, "test_changes": {},
            "links": {"blocked_by": [], "blocks": [], "relates_to": []}}


def setup(tmp_path, plan, fix_at=None):
    """An OUT folder with plan.json, claude.json and a fake claude on PATH.

    Returns (out, env, log)."""
    out, bin_dir = tmp_path / "out", tmp_path / "bin"
    out.mkdir(parents=True)
    bin_dir.mkdir()
    (out / "plan.json").write_text(json.dumps(plan))
    (out / "claude.json").write_text(json.dumps({"type": "result", "session_id": SESSION, "num_turns": 3}))
    fake = bin_dir / "claude"
    fake.write_text(FAKE.format(python=sys.executable, session=SESSION))
    fake.chmod(0o755)
    fixed = tmp_path / "fixed.json"
    fixed.write_text(json.dumps(good_plan()))
    log = tmp_path / "calls.jsonl"
    env = {k: v for k, v in os.environ.items() if k not in ("STYLE_SOFT", "PACK")}
    env.update({"PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}", "FAKE_CLAUDE_LOG": str(log),
                "FAKE_HANDBACK": str(out / "plan.json"), "FAKE_FIXED": str(fixed), "PYTHONPATH": ROOT,
                "ROLE": "planner", "N": "486", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "1"})
    if fix_at:
        env["FAKE_FIX_AT"] = str(fix_at)
    return out, env, log


def restyle(out, env):
    """Run the style retry loop the workflow runs after the agent ends."""
    return subprocess.run([sys.executable, "-m", "dokima.restyle", str(out), "plan.json"], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=60)


def calls(log):
    """Every call the fake claude received, oldest first."""
    return [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []


def said(call):
    """Everything one call told the agent: its arguments and its input."""
    return " ".join(call["argv"]) + "\n" + call["stdin"]


def test_failing_text_goes_back_to_its_writer_naming_each_field_and_why(tmp_path, record_property):
    """Long or code-filled text goes back to its session, naming each field and why.

    Proves 486.1.
    The hand-back has a 40-word user story and a criterion naming a code file. The loop must resume the session
    from claude.json and its message must name both fields: the user story's word count over its cap, and the
    criterion naming code. A hand-back that passes every style check is never sent back."""
    record_property("proves", "486.1")
    bad = good_plan()
    bad["user_story"] = LONG
    bad["acceptance_criteria"][0]["text"] = "Editing redraws `dokima/card.py` output."
    out, env, log = setup(tmp_path, bad, fix_at=1)
    run = restyle(out, env)
    got = calls(log)
    assert got, f"486.1: the failing text was never sent back to its writer ({run.stdout}{run.stderr})"
    first = got[0]
    assert "--resume" in first["argv"] and SESSION in first["argv"], \
        f"486.1: the text did not go back to the same session {SESSION}: {first['argv']}"
    msg = said(first)
    assert "user_story" in msg and "40 words" in msg and "cap of 20" in msg, \
        f"486.1: the message does not name the too-long user story and why: {msg}"
    assert "acceptance criterion 1" in msg and "code" in msg, \
        f"486.1: the message does not name the criterion naming code and why: {msg}"

    clean_out, clean_env, clean_log = setup(tmp_path / "clean", good_plan())
    restyle(clean_out, clean_env)
    assert not calls(clean_log), "486.1: a hand-back passing every style check was still sent back"


def test_style_retries_have_their_own_budget_of_three(tmp_path, record_property):
    """Style retries stop at 3, stop early once fixed, and other failures never use them.

    Proves 486.2.
    A writer who never fixes the text is sent back exactly 3 times; one who fixes it on the second try exactly 2.
    A hand-back that passes the style checks but fails another check (no scope, no tests) is never sent back by
    the style loop: other failures do not use the style budget."""
    record_property("proves", "486.2")
    bad = good_plan()
    bad["user_story"] = LONG
    out, env, log = setup(tmp_path / "never", bad)
    run = restyle(out, env)
    assert len(calls(log)) == 3, \
        f"486.2: a text that never passes went back {len(calls(log))} times, not 3 ({run.stdout}{run.stderr})"

    out, env, log = setup(tmp_path / "second", bad, fix_at=2)
    restyle(out, env)
    assert len(calls(log)) == 2, f"486.2: a text fixed on the second try went back {len(calls(log))} times, not 2"

    other = good_plan()
    other["scope"], other["tests"] = [], {}
    out, env, log = setup(tmp_path / "other", other)
    restyle(out, env)
    assert not calls(log), "486.2: a failure of another check used the style retries"


def record(out, env):
    """Write the run's record the way the workflow does, with the code check passed."""
    (out / "check.txt").write_text("")
    logs = out.parent / "logs"
    logs.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "dokima.agent", "record", "planner", "", str(out), str(out / "check.txt"),
                    "true", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60, check=True)
    return json.loads((out / "record.json").read_text()), (out / "comment.md").read_text()


def test_after_three_failed_style_retries_it_posts_flagged_naming_each_field(tmp_path, record_property):
    """After 3 failed style retries it still posts, naming each field still failing.

    Proves 486.3.
    The writer never fixes a 40-word user story. After the loop, the run's record keeps the hand-back as passed,
    lists the user story's failure under check.style, and the comment shows it above its JSON record. A run whose texts pass carries
    no such flag."""
    record_property("proves", "486.3")
    bad = good_plan()
    bad["user_story"] = LONG
    out, env, log = setup(tmp_path / "flagged", bad)
    restyle(out, env)
    rec, comment = record(out, env)
    assert rec["check"]["passed"] is True, "486.3: a hand-back failing only style after 3 retries did not post"
    flags = rec["check"].get("style") or []
    assert any("user_story" in f and "40 words" in f for f in flags), \
        f"486.3: the record does not flag the user story still failing: {rec['check']}"
    shown = comment.split("```json")[0]  # what the owner reads, above the full JSON record's fold
    assert any("user_story" in line and "40 words" in line for line in shown.splitlines()), \
        "486.3: the run's comment does not name the user story still failing, outside its JSON record"

    out, env, log = setup(tmp_path / "clean", good_plan())
    restyle(out, env)
    rec, comment = record(out, env)
    assert not rec["check"].get("style"), f"486.3: a run whose texts pass was flagged: {rec['check']}"

"""The agent code sits in one file per job, with GitHub faked in one place.

Issue #636 (story 1 of #581). `dokima/agent.py` held every job of the agent code in one file of over 3,000 lines, so
issues that touched different jobs queued on the same file. These tests pin the split:

- each job has its own file (`dokima/agent_github.py`, `agent_records.py`, `agent_checks.py`, `agent_roles.py`,
  `agent_autopilot.py`, `agent_next.py`), and every function the old file defined now lives in one of them;
- every name the old file offered (listed below, as `dir(dokima.agent)` gave them at 61faa9e) still loads from
  `dokima.agent`, as the very object its job file holds;
- every call the agent code makes to GitHub goes through `dokima.agent_github.gh`, so patching that one name fakes
  GitHub for all of it, including the board's and the checks' calls through `agent.gh`.

No behavior changes: the whole suite proves that; these tests also run `python3 -m dokima.agent`, which the workflows
call, and import every module that imports the agent code in a fresh interpreter.
"""
import ast
import importlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import agent  # noqa: E402

# Each job's file and a few of the functions it carries, as #581's approved plan named them.
JOBS = {
    "dokima.agent_github": ("gh", "gh_reason", "rate_limited", "linked_prs", "conversation"),
    "dokima.agent_records": ("records", "latest", "approved", "open_raises", "build_record", "render",
                             "render_as_posted"),
    "dokima.agent_checks": ("check", "load", "problems_old", "problems_raised"),
    "dokima.agent_roles": ("pack", "problems_pack", "command_of", "route"),
    "dokima.agent_autopilot": ("switch_autopilot", "merge_gate", "try_merge", "automerge", "merge_tree"),
    "dokima.agent_next": ("next_step", "waiting", "next_line", "board_place"),
}

# Every name `dokima.agent` offered at 61faa9e, before the split: the functions and classes it defined, its
# constants, and the modules and names it imported.
DEFINED = (
    'agents_text', 'answered_lines', 'approved', 'approved_plan', 'approves_work', 'automerge', 'autopilot_closed',
    'autopilot_comment', 'autopilot_of', 'behind_main', 'blocked_by', 'board_place', 'bot_cards', 'build_record',
    'bullets', 'cancelled', 'card_stage', 'check', 'clash_pending', 'close_done_parents', 'close_done_trees',
    'close_if_done', 'command_of', 'conversation', 'criteria_texts', 'criterion_of', 'details', 'details_as_posted',
    'escape_line', 'failed_rows', 'failing_plan_tests', 'file_issues', 'file_split', 'files_changed', 'filled',
    'first_sentence', 'footnote', 'for_planner', 'gh', 'gh_reason', 'held_for_approval', 'installations_link',
    'is_record', 'issue_of_pr', 'issue_text', 'issue_tree', 'issue_url', 'jsonl_files', 'latest', 'link_edges',
    'linked_prs', 'live_card', 'load', 'loop_through', 'main', 'merge_gate', 'merge_outcome', 'merge_tree',
    'models_used', 'name_of', 'named', 'next_line', 'next_step', 'not_accepted', 'not_started', 'old_blocker',
    'on_autopilot', 'open_blockers', 'open_blockers_of', 'open_issue_summary', 'open_issues', 'open_pr',
    'open_raises', 'opening', 'opening_as_posted', 'owner_raises', 'owner_source', 'owner_words', 'pack',
    'pack_issue', 'pack_parent', 'pack_records', 'pages', 'pairs', 'parent_of', 'parent_words', 'plan_criteria',
    'plan_links', 'plan_rows', 'plan_tests', 'plans_again', 'posted_before_raises', 'problems_asks',
    'problems_edge_cases', 'problems_for_owner', 'problems_items', 'problems_links', 'problems_old',
    'problems_pack', 'problems_plan', 'problems_raised', 'problems_review', 'problems_round', 'problems_searched',
    'problems_shape', 'problems_size', 'problems_tests', 'problems_work', 'proof', 'queue', 'queued_since',
    'quoted', 'raised_by', 'raised_lines', 'raises_for', 'rate_limit_waited_once', 'rate_limited', 'record_fold',
    'record_links', 'records', 'render', 'render_as_posted', 'required_checks', 'rerun_checks', 'review_lines',
    'review_name', 'reviewer_open_issues', 'role_icon', 'route', 'run_ahead', 'run_report', 'said', 'said_there',
    'scrub', 'set_title', 'settled', 'short', 'stamp_record', 'start_planner', 'start_unblocked', 'start_waiting',
    'started', 'started_before', 'stats_line', 'stats_tail', 'stop_run', 'story_body', 'sub_issues', 'superseded',
    'switch_autopilot', 'taken_ids', 'test_fix', 'transcript', 'tree_done_comment', 'try_merge', 'unanswered',
    'unconfirmed_comment', 'unproven', 'unrecorded', 'unrecorded_run', 'waiting', 'waits_on_owner', 'where_card',
    'who', 'with_next', 'words_link', 'work_approved', 'worker_docstring_caps')
CONSTANTS = (
    'AUTOPILOT', 'AUTOPILOT_LINE', 'AUTOPILOT_LINES', 'AUTOPILOT_MERGE', 'AUTOPILOT_START_LINE', 'BOARD_WAIT',
    'BOT', 'BOT_LOGIN', 'CARD_HEADS', 'CHECKS_PAUSE', 'CHECKS_WAIT', 'COMMANDS', 'FILED_LABEL', 'FIXERS', 'GOING',
    'HANDBACK', 'HEADS', 'LINKS', 'LIVE', 'MARK', 'MAX_QUESTIONS', 'MERGE_STATE', 'NEEDS', 'NO_PERMISSION',
    'OLD_FIELDS', 'PASSING', 'PLAN_TEST_FAILS', 'PUSH_EVENTS', 'STAGE_COLUMN', 'STATS', 'UNREAD', 'UNRECORDED',
    'UPDATE_PAUSE', 'UPDATE_WAIT', 'VERDICTS', 'WORKFLOWS')
IMPORTED = (
    'card', 'contextlib', 'glob', 'issue_body', 'json', 'manifest', 'os', 'raises', 're', 'shutil', 'subprocess',
    'sys', 'time', 'words', 'field_icon', 'icon')


def job_modules(key):
    """Each job file's module by name; a missing one fails naming its criterion."""
    out = {}
    for name in JOBS:
        try:
            out[name] = importlib.import_module(name)
        except ModuleNotFoundError as e:
            raise AssertionError(f"{key}: there is no job file {name.replace('.', '/')}.py ({e})")
    return out


def run_agent(*args):
    """Runs `python3 -m dokima.agent` from the repo root, the way the workflows do."""
    return subprocess.run([sys.executable, "-m", "dokima.agent", *args], cwd=ROOT, capture_output=True, text=True,
                          timeout=60)


def test_agent_code_lives_in_job_files(record_property, tmp_path):
    """The agent code sits in one file per job, and the agent command still works.

    Each job file must exist and carry the functions #581 named for its job, and every other function or class the
    old agent file defined must now be defined in one of the job files, not in `dokima/agent.py`. Then it runs
    `python3 -m dokima.agent` twice, as the workflows do, and checks the answers are the ones it gave before the split.
    Proves 636.1.
    """
    record_property("proves", "636.1")
    mods = job_modules("636.1")
    for mod, names in JOBS.items():
        for n in names:
            where = getattr(getattr(agent, n), "__module__", None)
            assert where == mod, f"636.1: {n} should live in {mod.replace('.', '/')}.py, but it is defined in {where}"
    left = [n for n in DEFINED if n != "gh" and getattr(getattr(agent, n), "__module__", None) not in mods]
    assert not left, f"636.1: these are still defined outside the job files: {', '.join(left)}"
    empty = tmp_path / "pack"
    empty.mkdir()
    r = run_agent("check-pack", "planner", "issue", str(empty))
    assert (r.returncode, r.stdout.strip()) == (1, "issue.md is missing"), \
        f"636.1: `python3 -m dokima.agent check-pack` no longer answers as before: {r.returncode} {r.stdout}{r.stderr}"
    r = run_agent("check", "review", "x")
    assert r.returncode == 1 and "the check needs plan.json and the issue number" in r.stdout, \
        f"636.1: `python3 -m dokima.agent check` no longer explains a short call: {r.returncode} {r.stdout}{r.stderr}"


def test_every_old_name_loads_from_agent(record_property):
    """Every name the old agent file offered still loads from it.

    Checks each function, class, constant and imported name `dokima.agent` offered before the split is still there;
    that each function and class is the very object its job file defines; and that each constant is the same object
    a job file holds. Then it imports every module that imports the agent code in a fresh interpreter, so a broken
    import order fails here too. Proves 636.2.
    """
    record_property("proves", "636.2")
    mods = job_modules("636.2")
    missing = [n for n in DEFINED + CONSTANTS + IMPORTED if not hasattr(agent, n)]
    assert not missing, f"636.2: these names no longer load from dokima.agent: {', '.join(missing)}"
    for n in DEFINED:
        if n == "gh":
            continue  # gh reaches the one helper however it is offered; 636.3 proves it.
        obj = getattr(agent, n)
        where = getattr(obj, "__module__", None)
        assert where in mods and getattr(mods[where], n, None) is obj, \
            f"636.2: dokima.agent.{n} is not re-exported from a job file (it is defined in {where})"
    for n in CONSTANTS:
        assert any(getattr(m, n, object()) is getattr(agent, n) for m in mods.values()), \
            f"636.2: dokima.agent.{n} is not the same object any job file holds"
    code = ("from dokima.agent import pack_parent, problems_old, problems_raised\n"
            "import dokima.planner, dokima.board, dokima.card, dokima.checks, dokima.uptodate\n")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"636.2: an importer of the agent code no longer loads: {r.stderr.strip()[-600:]}"


def test_github_is_faked_in_one_place(record_property, tmp_path, monkeypatch):
    """Patching the one GitHub helper fakes every GitHub call the agent code makes.

    A `gh` on the path that fails loudly stands in for the real one. The test patches only
    `dokima.agent_github.gh`, then calls the agent code from several job files, and `agent.gh` the way the board and
    the checks do, and checks every call reached the fake. It also reads every agent job file and fails on any that
    runs `gh` itself or calls a `gh` of its own instead of the helper's. Proves 636.3.
    """
    record_property("proves", "636.3")
    job_modules("636.3")
    from dokima import agent_github
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(f"#!/bin/sh\ntouch {tmp_path}/real-gh-ran\nexit 1\n")
    (bin_dir / "gh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    seen = []

    def fake(*args):
        seen.append(args)
        return json.dumps({"status": "identical", "behind_by": 0}) if "compare" in " ".join(args) else \
            ("" if args[:2] == ("pr", "list") and "-q" in args else "[]")

    monkeypatch.setattr(agent_github, "gh", fake)
    calls = {
        "agent.gh": lambda: agent.gh("api", "repos/o/r"),
        "linked_prs": lambda: agent.linked_prs("o/r", 5),
        "sub_issues": lambda: agent.sub_issues("o/r", 5),
        "behind_main": lambda: agent.behind_main("o/r", "abc"),
        "open_issues": lambda: agent.open_issues("o/r"),
        "where_card": lambda: agent.where_card("o/r", 5, "worker", "issue"),
    }
    for name, call in calls.items():
        before = len(seen)
        try:
            call()
        except Exception as e:  # noqa: BLE001 - the failure names the call that missed the fake
            raise AssertionError(f"636.3: {name} did not go through the one GitHub helper: {e!r}")
        assert len(seen) > before, f"636.3: {name} made no call through dokima.agent_github.gh"
    assert not (tmp_path / "real-gh-ran").exists(), "636.3: the real gh ran although the helper was faked"
    bad = []
    for f in sorted(os.listdir(os.path.join(ROOT, "dokima"))):
        if not (f.startswith("agent") and f.endswith(".py")) or f == "agent_github.py":
            continue
        tree = ast.parse(open(os.path.join(ROOT, "dokima", f)).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "gh":
                bad.append(f"{f}:{node.lineno} calls a gh of its own")
            if isinstance(node, ast.List) and node.elts and isinstance(node.elts[0], ast.Constant) \
                    and node.elts[0].value == "gh":
                bad.append(f"{f}:{node.lineno} runs gh itself")
    assert not bad, "636.3: GitHub calls bypass dokima.agent_github.gh: " + "; ".join(bad)

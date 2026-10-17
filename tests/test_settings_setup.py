"""Tests for #794: setup saves settings safely; the agents section picks each role's agent.

A repo's settings file is `.dokima/settings.yaml`; its `agents:` section holds what `.dokima/agents.yml` held:

    agents:
      subscriptions:
        SUB:
          agent: AGENT
          key: SECRET
      roles:
        ROLE:
          subscription: SUB
          model: MODEL

`python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE --key` stores the key read
from standard input as a repo secret (through `gh secret set`) and saves the subscription and the role into that
section. These tests run the real commands from outside in a temp repo folder, with a stub `gh` first on PATH that
logs every call, and stub `claude`, `npm`, `kimi` and `codex` commands that log every call. Nothing leaves the machine.
The workflow test reads every file in .github/workflows/ and checks each job that runs Dokima installs PyYAML first.
"""
import glob
import json
import os
import re
import subprocess
import sys
import textwrap

import yaml

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from test_start import Run, SPLIT_PROPOSED  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STUB = textwrap.dedent('''\
    #!{python}
    """A stand-in for `{name}` that logs each call and exits 0."""
    import json, os, sys
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps({{"cmd": "{name}", "argv": sys.argv[1:]}}) + "\\n")
''')

# A repo's settings file with full-line comments, comments at the end of lines, lists, other groups and an agents
# section that already names a subscription and two roles.
SETTINGS = textwrap.dedent('''\
    # Our repo's Dokima settings: only what differs from the defaults.
    tests:
      dir: spec  # our tests live in spec/
      file_pattern: check_*.py
    setup:
      python: "3.11"
      install: pip install -e .  # the package itself
    protected_paths:
      - .github/
      - ops/
    gates:
      required: [all tests, Lint]
    # Who runs each role.
    agents:  # moved here from agents.yml
      subscriptions:
        old:
          agent: claude  # the first subscription
          key: OLD_KEY
      roles:
        # The reviewer stays on Claude.
        reviewer:
          subscription: old
          model: claude-opus-5-5  # keep the strongest
        planner:
          subscription: old
          model: claude-haiku-5-5
    labels:
      plan: plan  # a comment after the agents section
''')

FULL_LINE_COMMENTS = ["# Our repo's Dokima settings: only what differs from the defaults.", "# Who runs each role.",
                      "# The reviewer stays on Claude."]
END_OF_LINE_COMMENTS = [("dir: spec", "# our tests live in spec/"), ("install: pip install -e .", "# the package itself"),
                        ("agents:", "# moved here from agents.yml"), ("agent: claude", "# the first subscription"),
                        ("model: claude-opus-5-5", "# keep the strongest"),
                        ("plan: plan", "# a comment after the agents section")]


class Repo:
    """A temp repo folder with logging stub commands first on PATH."""

    def __init__(self, tmp_path):
        """Make the repo folder, the stubs and their call log."""
        self.root = tmp_path / "repo"
        self.bin = tmp_path / "bin"
        for d in (self.root, self.bin):
            d.mkdir(parents=True)
        self.log = tmp_path / "calls.jsonl"
        self.log.write_text("")
        for name in ("gh", "claude", "npm", "kimi", "codex"):
            p = self.bin / name
            p.write_text(STUB.format(python=sys.executable, name=name))
            p.chmod(0o755)
        self.settings = self.root / ".dokima" / "settings.yaml"

    def write(self, text):
        """Write TEXT as the repo's settings file."""
        self.settings.parent.mkdir(parents=True, exist_ok=True)
        self.settings.write_text(text)

    def env(self):
        """The command's environment: the stubs first on PATH, this checkout's dokima importable, no runner settings."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("DOKIMA_SETTINGS", "CLAUDE_CODE_OAUTH_TOKEN", "DOKIMA_AGENT_KEY", "PYTHONSAFEPATH")}
        env.update({"PATH": f"{self.bin}:{os.environ['PATH']}", "PYTHONPATH": ROOT, "FAKE_LOG": str(self.log)})
        return env

    def run(self, module, *args, stdin=""):
        """Run `python3 -m dokima.MODULE ARGS` in the repo folder; return the finished process."""
        return subprocess.run([sys.executable, "-m", f"dokima.{module}", *args], cwd=self.root, env=self.env(),
                              input=stdin, capture_output=True, text=True, timeout=60)

    def add_team_planner(self):
        """Save through setup a Codex subscription named team, the planner on it with gpt-test-1."""
        return self.run("setup", "add", "team", "--agent", "codex", "--secret", "TEAM_KEY", "--model", "gpt-test-1",
                        "--role", "planner", "--key", stdin="sk-test-key\n")

    def calls(self):
        """Every stub call, oldest first, as {cmd, argv}."""
        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]

    def saved(self):
        """The settings file's text now, or '' when there is none."""
        return self.settings.read_text() if self.settings.exists() else ""


def said(p):
    """A finished process's exit code and output, for a failure message."""
    return f"exit {p.returncode}; stdout: {p.stdout.strip()[-400:]!r}; stderr: {p.stderr.strip()[-400:]!r}"


def with_team_planner(settings):
    """SETTINGS as they should read once setup saved the team subscription and planner."""
    want = json.loads(json.dumps(settings))
    agents = want.setdefault("agents", {})
    agents.setdefault("subscriptions", {})["team"] = {"agent": "codex", "key": "TEAM_KEY"}
    agents.setdefault("roles", {})["planner"] = {"subscription": "team", "model": "gpt-test-1"}
    return want


def saved_the_setting(crit, repo, p):
    """Fail naming CRIT unless setup saved the team subscription and planner into the file."""
    assert p.returncode == 0, f"{crit}: setup add failed: {said(p)}"
    text = repo.saved()
    got = yaml.safe_load(text) or {} if text else {}
    agents = got.get("agents") if isinstance(got, dict) else None
    agents = agents if isinstance(agents, dict) else {}
    assert (agents.get("subscriptions") or {}).get("team") == {"agent": "codex", "key": "TEAM_KEY"} \
        and (agents.get("roles") or {}).get("planner") == {"subscription": "team", "model": "gpt-test-1"}, \
        (f"{crit}: setup did not save the team subscription and the planner into the agents section of "
         f".dokima/settings.yaml; the file now reads:\n{text}")
    return text


def test_a_settings_file_holding_lists_is_read_in_full(record_property):
    """A settings file with lists on one line is read with every item.

    Proves 794.1. Gives setup's settings reader a file holding lists written on one line beside groups and comments,
    and checks it reads exactly what a YAML reader reads: every list whole, every group, no comment text."""
    record_property("proves", "794.1")
    from dokima.setup import read_settings
    text = textwrap.dedent('''\
        # settings
        protected_paths: [.github/, ops/, "docs/private/"]
        gates:
          required: [all tests, Lint]  # two checks
        fence:
          test_setup_files: [conftest.py, pytest.ini]
        tests:
          dir: spec
        ''')
    got = read_settings(text)
    assert got == yaml.safe_load(text), f"794.1: the settings file's lists were not read in full; got {got!r}"


def test_a_list_written_one_item_per_line_is_read_in_full(record_property):
    """A settings file with lists written one item per line is read with every item.

    Proves 794.1. Gives setup's settings reader lists written as indented dash lines, at the top and inside a group,
    and checks it reads exactly what a YAML reader reads."""
    record_property("proves", "794.1")
    from dokima.setup import read_settings
    text = textwrap.dedent('''\
        protected_paths:
          - .github/
          - ops/
        gate:
          exclude:
            - card
            - board wait
          checks_wait_min: 30
        ''')
    got = read_settings(text)
    assert got == yaml.safe_load(text), f"794.1: lists written one item per line were not read in full; got {got!r}"


DOKIMA_RUNS = re.compile(r"python3? -m dokima\.|from dokima|import dokima")
INSTALLS_YAML = re.compile(r"pip3? install[^\n]*\bpyyaml\b", re.I)


def test_every_machine_that_runs_dokima_can_read_the_settings_file(record_property):
    """Every workflow job that runs Dokima installs the YAML reader before its first Dokima step.

    Proves 794.1. Reads every workflow in .github/workflows/; for each job whose steps run Dokima's code, it finds the
    first such step and checks an earlier step of the same job installs PyYAML, so the settings file can be read
    there. Lists every job that does not."""
    record_property("proves", "794.1")
    missing, seen = [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml"))):
        jobs = (yaml.safe_load(open(path)) or {}).get("jobs") or {}
        for name, job in jobs.items():
            steps = job.get("steps") or []
            runs = [str(s.get("run") or "") for s in steps]
            first = next((i for i, r in enumerate(runs) if DOKIMA_RUNS.search(r)), None)
            if first is None:
                continue
            seen += 1
            if not any(INSTALLS_YAML.search(r) for r in runs[:first]):
                step = steps[first].get("name") or runs[first].strip().splitlines()[0]
                missing.append(f"{os.path.basename(path)} job {name} (first Dokima step: {step!r})")
    assert seen, "794.1: no workflow job runs Dokima, so nothing was checked"
    assert not missing, ("794.1: these jobs run Dokima before installing PyYAML, so they cannot read a settings file "
                         "holding lists: " + "; ".join(missing))


def test_saving_a_setting_keeps_the_files_comments(record_property, tmp_path):
    """Saving a setting through setup keeps every comment line of the settings file.

    Proves 794.2. Writes a settings file with comment lines at the top, between groups and inside the agents section,
    saves a subscription and a role through setup, and checks the setting was saved and every comment line is still
    there, in the same order."""
    record_property("proves", "794.2")
    repo = Repo(tmp_path)
    repo.write(SETTINGS)
    text = saved_the_setting("794.2", repo, repo.add_team_planner())
    lines = [l.strip() for l in text.splitlines()]
    kept = [c for c in FULL_LINE_COMMENTS if c in lines]
    assert kept == FULL_LINE_COMMENTS, f"794.2: setup dropped comment lines {sorted(set(FULL_LINE_COMMENTS) - set(kept))}"
    at = [lines.index(c) for c in FULL_LINE_COMMENTS]
    assert at == sorted(at), f"794.2: setup moved the comment lines out of their order; the file now reads:\n{text}"


def test_saving_a_setting_keeps_comments_at_the_end_of_lines(record_property, tmp_path):
    """Saving a setting through setup keeps every comment written at the end of a line.

    Proves 794.3. Writes a settings file with comments at the end of setting lines, in other groups and inside the
    agents section, saves a subscription and a role through setup, and checks the setting was saved and each comment
    is still at the end of its own setting's line."""
    record_property("proves", "794.3")
    repo = Repo(tmp_path)
    repo.write(SETTINGS)
    text = saved_the_setting("794.3", repo, repo.add_team_planner())
    lines = [l.strip() for l in text.splitlines()]
    lost = [f"{line}  {comment}" for line, comment in END_OF_LINE_COMMENTS
            if not any(l.startswith(line) and l.endswith(comment) for l in lines)]
    assert not lost, f"794.3: setup dropped the comments at the end of these lines: {lost}; the file now reads:\n{text}"


def test_saving_one_setting_leaves_every_other_setting_as_it_was(record_property, tmp_path):
    """Saving one setting through setup changes only that setting.

    Proves 794.4. Writes a settings file holding groups, lists, a quoted version, other subscriptions and roles, and
    the planner on an old subscription; saves a new subscription with the planner on it through setup; and checks the
    file now reads exactly as before with only the new subscription added and the planner's two lines changed."""
    record_property("proves", "794.4")
    repo = Repo(tmp_path)
    repo.write(SETTINGS)
    text = saved_the_setting("794.4", repo, repo.add_team_planner())
    want = with_team_planner(yaml.safe_load(SETTINGS))
    assert yaml.safe_load(text) == want, \
        f"794.4: saving the planner changed other settings; want {want!r}, the file now reads:\n{text}"


def test_saving_into_a_file_with_no_agents_section_leaves_the_rest(record_property, tmp_path):
    """Saving into a file with no agents section adds one and keeps every other setting.

    Proves 794.4. Writes a settings file with groups and lists but no agents section, saves a subscription and a role
    through setup, and checks the file reads as before plus the new agents section."""
    record_property("proves", "794.4")
    repo = Repo(tmp_path)
    before = "tests:\n  dir: spec\nprotected_paths:\n  - .github/\n  - ops/\n"
    repo.write(before)
    text = saved_the_setting("794.4", repo, repo.add_team_planner())
    want = with_team_planner(yaml.safe_load(before))
    assert yaml.safe_load(text) == want, \
        f"794.4: saving into a file with no agents section changed other settings; the file now reads:\n{text}"


def test_saving_with_no_settings_file_yet_creates_it(record_property, tmp_path):
    """In a repo with no settings file yet, setup creates it holding the saved setting.

    Proves 794.4. Runs setup in a repo with no .dokima folder and checks .dokima/settings.yaml now holds the new
    subscription and the planner on it, and nothing else."""
    record_property("proves", "794.4")
    repo = Repo(tmp_path)
    text = saved_the_setting("794.4", repo, repo.add_team_planner())
    assert yaml.safe_load(text) == with_team_planner({}), \
        f"794.4: a new settings file should hold only the saved setting; it reads:\n{text}"


AGENTS_SECTION = textwrap.dedent('''\
    tests:
      dir: tests
    agents:
      subscriptions:
        team:
          agent: codex
          key: TEAM_KEY
      roles:
        planner:
          subscription: team
          model: gpt-test-1
    ''')


def test_the_agents_section_picks_each_roles_agent_and_model(record_property, tmp_path):
    """The agents section of the settings file decides each role's agent and model.

    Proves 794.5. With only .dokima/settings.yaml in the repo, its agents section putting the planner on Codex with
    model gpt-test-1 and key TEAM_KEY, checks the interface names that model and key, and that installing the
    planner's agent installs Codex. The reviewer, left out, stays on today's Claude Code model."""
    record_property("proves", "794.5")
    repo = Repo(tmp_path)
    repo.write(AGENTS_SECTION)
    p = repo.run("agents", "model", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "gpt-test-1", \
        f"794.5: the planner's model should be gpt-test-1, from the agents section: {said(p)}"
    p = repo.run("agents", "key", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "TEAM_KEY", \
        f"794.5: the planner's key should be TEAM_KEY, from the agents section: {said(p)}"
    p = repo.run("agents", "install", "planner")
    npm = [c["argv"] for c in repo.calls() if c["cmd"] == "npm"]
    assert p.returncode == 0 and npm and "@openai/codex" in npm[-1], \
        f"794.5: installing the planner's agent should install Codex, the agent the section names: {said(p)}; npm {npm}"
    p = repo.run("agents", "model", "reviewer")
    assert p.returncode == 0 and p.stdout.strip() == "claude-opus-5-5", \
        f"794.5: the reviewer, left out of the agents section, should stay on claude-opus-5-5: {said(p)}"


def test_a_run_on_github_starts_the_model_the_agents_section_names(record_property, tmp_path):
    """A workflow run starts the agent on the model main's agents section names.

    Proves 794.5. Runs the agent workflow for a plan review, the way GitHub runs it, with only .dokima/settings.yaml
    on main putting the reviewer on claude-sonnet-5-5, and the key secret it names (TEAM_KEY) set on the repo, as a
    run that starts needs since #812. The fake Claude Code must start with that model."""
    record_property("proves", "794.5")
    text = AGENTS_SECTION.replace("codex", "claude").replace("planner:", "reviewer:").replace("gpt-test-1",
                                                                                               "claude-sonnet-5-5")
    assert "TEAM_KEY" in text, "test setup: the agents section no longer names the TEAM_KEY secret"
    r = Run(tmp_path / "run", "reviewer", "plan", SPLIT_PROPOSED, files={".dokima/settings.yaml": text},
            secrets={"TEAM_KEY": "team-key"})
    assert r.agent_started(), f"794.5: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
    path = os.path.join(r.tmp, "gh", "agent-argv.json")
    argv = json.load(open(path)) if os.path.exists(path) else []
    got = argv[argv.index("--model") + 1] if "--model" in argv[:-1] else None
    assert got == "claude-sonnet-5-5", \
        f"794.5: the reviewer started on {got!r}, not claude-sonnet-5-5 from the agents section of main's settings file"


# A settings file that tries to change the order of steps, the ways a repo might guess at, and puts each role on its
# own model, so each run shows it read the file.
REORDER = textwrap.dedent('''\
    river:
      order: [plan, build, merge]  # skip the reviews
    stages: [build, merge]
    agents:
      subscriptions:
        main:
          agent: claude
          key: CLAUDE_CODE_OAUTH_TOKEN
      roles:
        planner:
          subscription: main
          model: claude-haiku-5-5
        worker:
          subscription: main
          model: claude-fable-5-1
        reviewer:
          subscription: main
          model: claude-sonnet-5-5
    ''')

# The test the stand-in planner writes: it needs x.py, which only the stand-in worker builds.
PLANNER_TEST = ('def test_a(record_property):\n    """x.value() is 1.\n\n    Proves 57.1."""\n'
                '    record_property("proves", "57.1")\n    import x\n    assert x.value() == 1\n')

# The plan the stand-in planner hands back: one criterion on issue #57 ("Fix it."), proved by PLANNER_TEST.
ORDER_PLAN = {"kind": "user_story", "title": "Fix it", "summary": "Fixes the stuck issue.",
              "user_story": "The stuck issue is fixed.",
              "acceptance_criteria": [{"text": "The stuck issue is fixed.", "words": "Fix it.",
                                       "source": "https://github.com/o/r/issues/57", "files": ["x.py"],
                                       "no_edge_cases": "One fix."}],
              "non_functional": [], "tests": {"57.1": ["tests/test_x.py::test_a"]}, "test_changes": {},
              "links": {"blocked_by": [], "blocks": [], "relates_to": []}}

# A stand-in for Claude Code that plays whichever role the run gives it: the planner hands back ORDER_PLAN with its
# test, the worker builds x.py and hands back its work, the reviewer hands back the review the test chose. Each keeps
# its arguments (agent-argv.json), so the test sees the model it was started on.
STAND_IN = r'''#!/usr/bin/env python3
"""A stand-in planner, worker or reviewer."""
import json, os, shutil, sys
d, out, role = os.environ["FAKE_GH_DIR"], os.environ["OUT"], os.environ["ROLE"]
json.dump(sys.argv[1:], open(os.path.join(d, "agent-argv.json"), "w"))
if role == "planner":
    open("tests/test_x.py", "w").write(__TEST__)
    json.dump(__PLAN__, open(os.path.join(out, "plan.json"), "w"))
elif role == "worker":
    open("x.py", "w").write("def value():\n    return 1\n")
    json.dump({"summary": "Built it.", "criteria": {"57.1": "x.py, value()"}, "evidence": "pytest -q: 1 passed",
               "raises": [], "answers": []}, open(os.path.join(out, "work.json"), "w"))
else:
    shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(out, "review.json"))
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv[:-1] else os.environ.get("MODEL", "")
logs = os.path.join(os.environ["HOME"], ".claude", "projects", "p")
os.makedirs(logs, exist_ok=True)
open(os.path.join(logs, "s.jsonl"), "w").write(json.dumps({"message": {"model": model, "role": "assistant", "content": "Done."}}) + "\n")
open(os.environ["FAKE_CLAUDE_MARK"], "w").write("started")
print(json.dumps({"num_turns": 1, "duration_ms": 1000, "usage": {}}))
'''.replace("__TEST__", repr(PLANNER_TEST)).replace("__PLAN__", repr(ORDER_PLAN))


def next_steps(r):
    """Every next step the run started, as (role, stage).

    Only a reviewer's stage tells two steps apart (plan or pr), so other roles show an empty stage."""
    out = []
    for c in r.dispatches():
        f = dict(x.split("=", 1) for i, x in enumerate(c) if i and c[i - 1] in ("-f", "-F") and "=" in x)
        if f.get("event_type") == "dokima-next":
            role = f.get("client_payload[role]", "")
            out.append((role, f.get("client_payload[stage]", "") if role == "reviewer" else ""))
    return out


def test_no_setting_changes_the_order_of_steps(record_property, tmp_path, monkeypatch):
    """Settings that try to skip the reviews leave the order plan, review, build, review, merge.

    Proves 794.10. Runs the planner, the plan review and the worker of an issue on autopilot, one after the other, the
    way GitHub runs them, with main's settings file asking to skip the reviews and go straight to build and merge.
    In each run it first checks the agent started on the model the file names for its role, so the file was really
    read in that run; without that the order check would prove nothing. Then each run must start exactly the next
    step of the order: the planner starts the plan review, the approved plan starts the build, and the build starts
    the code review. Nothing is skipped and no merge is started."""
    record_property("proves", "794.10")
    import test_autopilot_river as river
    import test_start as ts
    monkeypatch.setattr(ts, "FAKE_CLAUDE", STAND_IN)
    files = {".dokima/settings.yaml": REORDER}
    runs = (("planner", "", [ts.owner_comment("/plan", "2026-10-07T10:00:00Z")], "claude-haiku-5-5",
             [("reviewer", "plan")], "the plan review"),
            ("reviewer", "plan", ts.STORY_PLANNED, "claude-sonnet-5-5", [("worker", "")], "the build, one worker"),
            ("worker", "", ts.STORY_APPROVED, "claude-fable-5-1", [("reviewer", "pr")], "the code review"))
    for role, stage, comments, model, want, name in runs:
        step = f"{role} {stage}".strip()
        r = river.run(monkeypatch, tmp_path / step.replace(" ", "-"), role, stage, comments, river.ON,
                      try_branch=True, review=river.APPROVE, files=files)
        assert r.agent_started(), f"794.10: the {step} run never started its agent; it stopped at '{r.failed_step}':\n{r.tail()}"
        path = os.path.join(r.tmp, "gh", "agent-argv.json")
        argv = json.load(open(path)) if os.path.exists(path) else []
        got = argv[argv.index("--model") + 1] if "--model" in argv[:-1] else None
        assert got == model, \
            (f"794.10: the {step} run did not read main's settings file (its agent started on {got!r}, not {model}), "
             "so it cannot show the file leaves the order alone")
        assert next_steps(r) == want, \
            f"794.10: after the {step} run the next step must be {name}, {want}; the run started {next_steps(r)}\n{r.tail()}"

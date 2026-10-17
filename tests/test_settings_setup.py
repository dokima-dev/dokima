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
    on main putting the reviewer on claude-sonnet-5-5. The fake Claude Code must start with that model."""
    record_property("proves", "794.5")
    text = AGENTS_SECTION.replace("codex", "claude").replace("planner:", "reviewer:").replace("gpt-test-1",
                                                                                               "claude-sonnet-5-5")
    r = Run(tmp_path / "run", "reviewer", "plan", SPLIT_PROPOSED, files={".dokima/settings.yaml": text})
    assert r.agent_started(), f"794.5: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
    path = os.path.join(r.tmp, "gh", "agent-argv.json")
    argv = json.load(open(path)) if os.path.exists(path) else []
    got = argv[argv.index("--model") + 1] if "--model" in argv[:-1] else None
    assert got == "claude-sonnet-5-5", \
        f"794.5: the reviewer started on {got!r}, not claude-sonnet-5-5 from the agents section of main's settings file"

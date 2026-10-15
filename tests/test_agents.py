"""Tests for #698: one settings file picks each role's agent and model, behind one interface.

The settings file is `.dokima/agents.yml` in the repo's root, in the shape `python3 -m dokima.setup add` writes:

    subscriptions:
      SUB:
        agent: AGENT      # the adapter dokima/agent_AGENT.py runs it
        key: SECRET       # the repo secret holding the subscription's key or sign-in
    roles:
      ROLE:               # planner, worker or reviewer
        subscription: SUB
        model: MODEL

With no file, or for a role the file leaves out, a role runs on Claude Code with today's model, `claude-opus-5-5`, and
today's secret, CLAUDE_CODE_OAUTH_TOKEN. There is no fallback: a bad name stops the run, and a failed agent fails it.

The one interface, `dokima/agents.py`, reads the file under the current folder:

    python3 -m dokima.agents model ROLE              prints the model the role runs on
    python3 -m dokima.agents key ROLE                prints the name of the secret holding the role's key
    python3 -m dokima.agents install ROLE            installs the role's agent
    python3 -m dokima.agents run ROLE PROMPT_FILE OUT
        starts the role's agent with the prompt, the role's model and the key from DOKIMA_AGENT_KEY; its output goes
        into OUT, and its exit code is the agent's.
Each exits 1 with a message naming the bad name when the role names an unknown subscription or agent, before any agent
starts. In Python: `agents.run(role, prompt, out)`, `agents.models(role, out, log_dir)`, `agents.report(role, out)` and
`agents.transcript(role, log_dir, secrets)`. An agent's adapter is the module `dokima.agent_AGENT`, loaded with
`importlib.import_module`; it offers `install()`, `run(prompt, model, out)` (returns the exit code),
`models(out, log_dir)`, `report(out)` and `transcript(log_dir, secrets)`. Claude Code's is `dokima/agent_claude.py`.

The command-line tests run the real command from outside in a temp repo folder, with stub `claude`, `npm`, `kimi` and
`codex` commands first on PATH that log every call. The workflow tests run `.github/workflows/agent.yml` the way GitHub
does, through tests/test_start.py's machine, with its fake Claude Code. Nothing leaves the machine.
"""
import importlib
import json
import os
import subprocess
import sys
import textwrap
import types

import pytest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from test_start import Run, SPLIT_PROPOSED  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TODAY_MODEL = "claude-opus-5-5"
TODAY_KEY = "CLAUDE_CODE_OAUTH_TOKEN"

STUB = textwrap.dedent('''\
    #!{python}
    """A stand-in for `{name}` that logs each call, with the Claude key it was given, and exits with FAKE_EXIT."""
    import json, os, sys
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps({{"cmd": "{name}", "argv": sys.argv[1:],
                            "token": os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")}}) + "\\n")
    if "{name}" == "claude":
        print(json.dumps({{"num_turns": 4, "duration_ms": 5000, "usage": {{"input_tokens": 10, "output_tokens": 3}}}}))
    sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
''')


def settings(subscriptions, roles, before="", after=""):
    """The settings file's text: each subscription's agent and key, then each role's subscription and model."""
    lines = [before.rstrip("\n")] if before else []
    lines.append("subscriptions:")
    for name, (agent_name, key) in subscriptions.items():
        lines += [f"  {name}:", f"    agent: {agent_name}", f"    key: {key}"]
    lines.append("roles:")
    for role, (sub, model) in roles.items():
        lines += [f"  {role}:", f"    subscription: {sub}", f"    model: {model}"]
    if after:
        lines.append(after.rstrip("\n"))
    return "\n".join(lines) + "\n"


class Box:
    """A temp repo folder with stub agent commands first on PATH."""

    def __init__(self, tmp_path):
        """Make the repo folder, the stubs and their call log."""
        self.repo = tmp_path / "repo"
        self.bin = tmp_path / "bin"
        self.out = tmp_path / "out"
        for d in (self.repo, self.bin, self.out):
            d.mkdir(parents=True)
        self.log = tmp_path / "calls.jsonl"
        self.log.write_text("")
        for name in ("claude", "npm", "kimi", "codex"):
            p = self.bin / name
            p.write_text(STUB.format(python=sys.executable, name=name))
            p.chmod(0o755)

    def write_settings(self, text, path=".dokima/agents.yml"):
        """Write the settings text at PATH under the repo."""
        f = self.repo / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)

    def env(self, **extra):
        """The command's environment: the stubs first on PATH, this checkout's dokima importable, no real keys."""
        env = {k: v for k, v in os.environ.items() if k not in (TODAY_KEY, "DOKIMA_AGENT_KEY", "FAKE_EXIT")}
        env.update({"PATH": f"{self.bin}:{os.environ['PATH']}", "PYTHONPATH": ROOT, "FAKE_LOG": str(self.log)})
        env.update(extra)
        return env

    def cli(self, *args, **extra):
        """Run `python3 -m dokima.agents ARGS` in the repo folder; return the finished process."""
        return subprocess.run([sys.executable, "-m", "dokima.agents", *args], cwd=self.repo, env=self.env(**extra),
                              capture_output=True, text=True, timeout=60)

    def run(self, role, prompt="Plan issue 1.", **extra):
        """Start ROLE's agent through the interface with PROMPT; return the finished process."""
        f = self.repo.parent / "prompt.txt"
        f.write_text(prompt)
        return self.cli("run", role, str(f), str(self.out), **extra)

    def calls(self):
        """Every stub call, oldest first, as {cmd, argv, token}."""
        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]


def said(p):
    """A finished process's exit code and output, for a failure message."""
    return f"exit {p.returncode}; stdout: {p.stdout.strip()[-500:]!r}; stderr: {p.stderr.strip()[-500:]!r}"


def model_flag(call):
    """The value a stub call was given after --model, or None."""
    a = call["argv"]
    return a[a.index("--model") + 1] if "--model" in a[:-1] else None


def agents_module(crit):
    """The one agent interface, dokima/agents.py, or a failure naming the criterion."""
    try:
        return importlib.import_module("dokima.agents")
    except ImportError as e:
        pytest.fail(f"{crit}: dokima/agents.py, the one agent interface, cannot be loaded: {e}")


def fake_adapter(monkeypatch, calls, models=("zeta-1",), report=None):
    """Install a stand-in adapter for an agent named zeta, logging every call."""
    m = types.ModuleType("dokima.agent_zeta")
    m.install = lambda *a, **k: calls.append(("install", a, k)) or 0
    m.run = lambda prompt, model, out: calls.append(("run", (prompt, model, str(out)), {})) or 0
    m.models = lambda *a, **k: calls.append(("models", a, k)) or list(models)
    m.report = lambda *a, **k: calls.append(("report", a, k)) or dict(report or {})
    m.transcript = lambda *a, **k: calls.append(("transcript", a, k)) or "**Agent:** zeta\n"
    monkeypatch.setitem(sys.modules, "dokima.agent_zeta", m)
    return m


def workflow_settings(sub, agent_name, key, model):
    """Settings naming one subscription and putting the reviewer on it."""
    return settings({sub: (agent_name, key)}, {"reviewer": (sub, model)})


def fake_claude_saw(r, what):
    """The arguments ('argv') or environment ('env') the workflow's fake Claude Code started with."""
    path = os.path.join(r.tmp, "gh", f"agent-{what}.json")
    return json.load(open(path)) if os.path.exists(path) else None


def test_settings_come_from_one_file_in_the_dokima_folder(record_property, tmp_path):
    """The settings file in the repo's Dokima folder decides a role's model.

    Proves 698.1. Writes the settings file in the Dokima folder putting the planner on claude-sonnet-5-5, and checks
    the interface says the planner runs on it. Then moves the same file to the repo's root, outside the Dokima folder,
    and checks it is no longer read: the planner is back on today's model."""
    record_property("proves", "698.1")
    box = Box(tmp_path)
    text = settings({"team": ("claude", "TEAM_KEY")}, {"planner": ("team", "claude-sonnet-5-5")})
    box.write_settings(text)
    p = box.cli("model", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "claude-sonnet-5-5", \
        f"698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: {said(p)}"
    os.remove(box.repo / ".dokima" / "agents.yml")
    box.write_settings(text, path="agents.yml")
    p = box.cli("model", "planner")
    assert p.returncode == 0 and p.stdout.strip() == TODAY_MODEL, \
        f"698.1: a settings file outside the Dokima folder was read; the planner should stay on {TODAY_MODEL}: {said(p)}"


def test_a_run_gets_its_key_from_the_secret_its_subscription_names(record_property, tmp_path):
    """A run's agent gets the key held in the secret its role's subscription names.

    Proves 698.2. Runs the agent workflow for a plan review, with a settings file on main putting the reviewer on a
    subscription whose key is the repo secret TEAM_CLAUDE_KEY. The fake Claude Code must start with that secret's
    value as its key, not the value of today's CLAUDE_CODE_OAUTH_TOKEN."""
    record_property("proves", "698.2")
    files = {".dokima/agents.yml": workflow_settings("team", "claude", "TEAM_CLAUDE_KEY", TODAY_MODEL)}
    r = Run(tmp_path / "run", "reviewer", "plan", SPLIT_PROPOSED, files=files,
            secrets={"TEAM_CLAUDE_KEY": "team-key-value-698"})
    assert r.agent_started(), f"698.2: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
    env = fake_claude_saw(r, "env") or {}
    assert env.get(TODAY_KEY) == "team-key-value-698", \
        (f"698.2: Claude Code started with key {env.get(TODAY_KEY)!r}, not the value of TEAM_CLAUDE_KEY, the secret "
         f"the reviewer's subscription names")


def test_each_role_has_its_own_subscription_and_model(record_property, tmp_path):
    """Each of the three roles runs on the subscription and model the file gives it.

    Proves 698.3. Writes a settings file giving the three roles three subscriptions, each with its own secret, and
    three models, and checks the interface names each role's own model and secret."""
    record_property("proves", "698.3")
    box = Box(tmp_path)
    box.write_settings(settings(
        {"plan-sub": ("claude", "PLAN_KEY"), "work-sub": ("claude", "WORK_KEY"), "review-sub": ("claude", "REVIEW_KEY")},
        {"planner": ("plan-sub", "claude-sonnet-5-5"), "worker": ("work-sub", "claude-haiku-5-5"),
         "reviewer": ("review-sub", "claude-fable-5-1")}))
    for role, model, key in (("planner", "claude-sonnet-5-5", "PLAN_KEY"), ("worker", "claude-haiku-5-5", "WORK_KEY"),
                             ("reviewer", "claude-fable-5-1", "REVIEW_KEY")):
        p = box.cli("model", role)
        assert p.returncode == 0 and p.stdout.strip() == model, f"698.3: the {role}'s model should be {model}: {said(p)}"
        p = box.cli("key", role)
        assert p.returncode == 0 and p.stdout.strip() == key, \
            f"698.3: the {role}'s key should come from {key}, its own subscription's secret: {said(p)}"


def test_any_model_the_role_names_is_passed_to_its_agent(record_property, tmp_path):
    """A model Dokima has never heard of reaches the agent as named.

    Proves 698.4. Puts the planner on a made-up model, claude-unreleased-9-9, starts the planner through the interface
    and checks Claude Code was started with exactly that model and the run did not stop."""
    record_property("proves", "698.4")
    box = Box(tmp_path)
    box.write_settings(settings({"team": ("claude", "TEAM_KEY")}, {"planner": ("team", "claude-unreleased-9-9")}))
    p = box.run("planner")
    claude = [c for c in box.calls() if c["cmd"] == "claude"]
    assert p.returncode == 0 and len(claude) == 1, \
        f"698.4: a model outside any list stopped the run instead of starting Claude Code: {said(p)}; calls {box.calls()}"
    assert model_flag(claude[0]) == "claude-unreleased-9-9", \
        f"698.4: Claude Code got model {model_flag(claude[0])!r}, not the role's claude-unreleased-9-9"


def test_a_run_starts_with_the_model_the_file_names(record_property, tmp_path):
    """A workflow run starts the role's agent on the model the settings file names.

    Proves 698.5. Runs the agent workflow for a plan review with a settings file on main putting the reviewer on
    claude-sonnet-5-5. The fake Claude Code must be started with that model, and the run must pass its model check,
    which fails any run whose session names a model other than the one it should run on."""
    record_property("proves", "698.5")
    files = {".dokima/agents.yml": workflow_settings("team", "claude", TODAY_KEY, "claude-sonnet-5-5")}
    r = Run(tmp_path / "run", "reviewer", "plan", SPLIT_PROPOSED, files=files)
    assert r.agent_started(), f"698.5: the agent never started; the run stopped at '{r.failed_step}':\n{r.tail()}"
    argv = fake_claude_saw(r, "argv") or []
    got = argv[argv.index("--model") + 1] if "--model" in argv[:-1] else None
    assert got == "claude-sonnet-5-5", f"698.5: the reviewer's agent started on {got!r}, not the file's claude-sonnet-5-5"
    assert not r.failed, f"698.5: the run on the file's model failed at '{r.failed_step}':\n{r.tail()}"


def test_with_no_settings_file_a_run_starts_claude_code_as_today(record_property, tmp_path):
    """With no settings file, the planner runs on Claude Code with today's model and key.

    Proves 698.6. In a repo with no settings file, checks the planner's key is today's CLAUDE_CODE_OAUTH_TOKEN, then
    starts the planner through the interface and checks Claude Code started once, on claude-opus-5-5."""
    record_property("proves", "698.6")
    box = Box(tmp_path)
    p = box.cli("key", "planner")
    assert p.returncode == 0 and p.stdout.strip() == TODAY_KEY, \
        f"698.6: with no settings file the planner's key should be {TODAY_KEY}: {said(p)}"
    p = box.run("planner")
    calls = box.calls()
    assert p.returncode == 0 and [c["cmd"] for c in calls] == ["claude"], \
        f"698.6: with no settings file the planner did not start Claude Code once: {said(p)}; calls {calls}"
    assert model_flag(calls[0]) == TODAY_MODEL, \
        f"698.6: with no settings file Claude Code started on {model_flag(calls[0])!r}, not {TODAY_MODEL}"


def test_a_role_the_file_leaves_out_starts_claude_code_as_today(record_property, tmp_path):
    """A role the file leaves out runs on Claude Code with today's model and key.

    Proves 698.7. Writes a settings file that names only the worker, on claude-haiku-5-5 with its own secret. The
    planner must run on Claude Code with claude-opus-5-5 and CLAUDE_CODE_OAUTH_TOKEN, while the worker keeps the
    file's model, so the file is read."""
    record_property("proves", "698.7")
    box = Box(tmp_path)
    box.write_settings(settings({"team": ("claude", "TEAM_KEY")}, {"worker": ("team", "claude-haiku-5-5")}))
    p = box.cli("model", "worker")
    assert p.returncode == 0 and p.stdout.strip() == "claude-haiku-5-5", \
        f"698.7: the worker the file names should run on claude-haiku-5-5: {said(p)}"
    p = box.cli("key", "planner")
    assert p.returncode == 0 and p.stdout.strip() == TODAY_KEY, \
        f"698.7: the planner the file leaves out should use {TODAY_KEY}: {said(p)}"
    p = box.run("planner")
    calls = box.calls()
    assert p.returncode == 0 and [c["cmd"] for c in calls] == ["claude"], \
        f"698.7: the planner the file leaves out did not start Claude Code once: {said(p)}; calls {calls}"
    assert model_flag(calls[0]) == TODAY_MODEL, \
        f"698.7: the planner the file leaves out started on {model_flag(calls[0])!r}, not {TODAY_MODEL}"


def test_an_unknown_subscription_stops_the_run_before_any_agent_and_names_it(record_property, tmp_path):
    """An unknown subscription stops the run before its agent, and the issue names it.

    Proves 698.8. Runs the agent workflow for a plan review with a settings file putting the reviewer on
    no-such-sub, which the file does not list. Claude Code must never start, the run must fail, and the record posted
    on the issue must name no-such-sub."""
    record_property("proves", "698.8")
    files = {".dokima/agents.yml": settings({"team": ("claude", TODAY_KEY)}, {"reviewer": ("no-such-sub", TODAY_MODEL)})}
    r = Run(tmp_path / "run", "reviewer", "plan", SPLIT_PROPOSED, files=files)
    assert not r.agent_started(), "698.8: Claude Code started though the reviewer names an unknown subscription"
    assert r.failed, "698.8: the run passed though the reviewer names an unknown subscription"
    bodies = "\n".join(p["body"] for p in r.posted())
    assert "no-such-sub" in bodies, \
        f"698.8: nothing posted on the issue names the bad subscription no-such-sub:\n{bodies[-1500:]}\n{r.tail()}"


def test_an_unknown_agent_stops_before_any_agent_and_names_it(record_property, tmp_path):
    """An agent with no adapter stops the run before any agent starts, naming it.

    Proves 698.8, edge case: an unknown agent. Puts the planner on a subscription whose agent is no-such-agent and
    starts it through the interface: it must exit 1 naming no-such-agent, with no agent command run. A known agent in
    the same file still starts, so the check is not refusing everything."""
    record_property("proves", "698.8")
    box = Box(tmp_path)
    box.write_settings(settings({"odd": ("no-such-agent", "ODD_KEY"), "team": ("claude", TODAY_KEY)},
                                {"planner": ("odd", "m-1"), "worker": ("team", TODAY_MODEL)}))
    p = box.run("planner")
    assert p.returncode == 1 and "no-such-agent" in p.stdout + p.stderr, \
        f"698.8: an unknown agent should stop with exit 1 naming no-such-agent: {said(p)}"
    assert box.calls() == [], f"698.8: an agent command ran though the planner's agent is unknown: {box.calls()}"
    p = box.run("worker")
    assert p.returncode == 0 and [c["cmd"] for c in box.calls()] == ["claude"], \
        f"698.8: the worker, on a known agent, did not start: {said(p)}"


def test_a_role_starts_through_its_agents_own_adapter(record_property, tmp_path, monkeypatch):
    """The interface starts a role's agent through that agent's own adapter, on its model.

    Proves 698.9. Puts the planner on a subscription whose agent is zeta, a stand-in adapter loaded as
    dokima.agent_zeta, and starts the planner through the interface. The zeta adapter must be asked to run the prompt
    on zeta-1, the role's model, into the run's folder, and no Claude Code may start."""
    record_property("proves", "698.9")
    box = Box(tmp_path)
    box.write_settings(settings({"z": ("zeta", "ZETA_KEY")}, {"planner": ("z", "zeta-1")}))
    monkeypatch.chdir(box.repo)
    monkeypatch.setenv("PATH", f"{box.bin}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_LOG", str(box.log))
    calls = []
    fake_adapter(monkeypatch, calls)
    agents = agents_module("698.9")
    code = agents.run("planner", "Plan issue 1.", str(box.out))
    runs = [c for c in calls if c[0] == "run"]
    assert runs == [("run", ("Plan issue 1.", "zeta-1", str(box.out)), {})], \
        f"698.9: the zeta adapter was not asked once to run the prompt on zeta-1 into the run's folder: {calls}"
    assert code == 0, f"698.9: the interface did not pass on the adapter's exit code 0: {code!r}"
    assert box.calls() == [], f"698.9: another agent's command ran for a role on zeta: {box.calls()}"


def test_claude_code_is_installed_through_the_interface_as_today(record_property, tmp_path):
    """With no settings file, installing the planner's agent installs Claude Code as today.

    Proves 698.10. Runs the interface's install for the planner with no settings file and checks it ran
    `npm install -g @anthropic-ai/claude-code`, once, and succeeded."""
    record_property("proves", "698.10")
    box = Box(tmp_path)
    p = box.cli("install", "planner")
    npm = [c["argv"] for c in box.calls() if c["cmd"] == "npm"]
    assert p.returncode == 0 and npm == [["install", "-g", "@anthropic-ai/claude-code"]], \
        f"698.10: installing the planner's agent did not install Claude Code as today: {said(p)}; npm calls {npm}"


def test_a_failed_install_fails(record_property, tmp_path):
    """When installing Claude Code fails, the install through the interface fails too.

    Proves 698.10, edge case: the install fails. The stub npm exits 1, as it does when the package cannot be fetched;
    the interface's install must exit non-zero, so the run stops there."""
    record_property("proves", "698.10")
    box = Box(tmp_path)
    p = box.cli("install", "planner", FAKE_EXIT="1")
    assert [c["cmd"] for c in box.calls()] == ["npm"], f"698.10: the install never ran npm: {box.calls()}"
    assert p.returncode != 0, f"698.10: a failed Claude Code install still exited 0: {said(p)}"


def test_claude_code_starts_with_todays_command(record_property, tmp_path):
    """Claude Code starts behind the interface with exactly today's command, flags and key.

    Proves 698.11. Starts the planner through the interface with no settings file and a key in DOKIMA_AGENT_KEY.
    Claude Code must get today's arguments, in today's order, the key as CLAUDE_CODE_OAUTH_TOKEN, and its printed
    report must land in the run's folder as claude.json, where the record reads it today."""
    record_property("proves", "698.11")
    box = Box(tmp_path)
    p = box.run("planner", prompt="Plan issue 1.\nRead the pack.", DOKIMA_AGENT_KEY="key-value-698")
    calls = box.calls()
    assert p.returncode == 0 and [c["cmd"] for c in calls] == ["claude"], \
        f"698.11: the planner did not start Claude Code once: {said(p)}; calls {calls}"
    assert calls[0]["argv"] == ["-p", "Plan issue 1.\nRead the pack.", "--model", TODAY_MODEL,
                                "--dangerously-skip-permissions", "--max-turns", "60", "--output-format", "json"], \
        f"698.11: Claude Code's arguments differ from today's: {calls[0]['argv']}"
    assert calls[0]["token"] == "key-value-698", \
        f"698.11: Claude Code got key {calls[0]['token']!r}, not the run's key, as CLAUDE_CODE_OAUTH_TOKEN"
    report = box.out / "claude.json"
    assert report.exists() and json.loads(report.read_text()).get("num_turns") == 4, \
        "698.11: Claude Code's printed report was not kept in the run's folder as claude.json"


def test_a_runs_record_reads_its_agent_through_the_interface(record_property, tmp_path, monkeypatch):
    """A run's record names the models and stats its own agent reports.

    Proves 698.12. Puts the planner on the stand-in agent zeta, whose adapter reports model zeta-1
    and its own stats, then writes the planner's record the way the workflow does. The record must name zeta-1 and
    zeta's stats, not what Claude Code's logs would say."""
    record_property("proves", "698.12")
    box = Box(tmp_path)
    box.write_settings(settings({"z": ("zeta", "ZETA_KEY")}, {"planner": ("z", "zeta-1")}))
    for k in ("PACK", "BASE", "LOG_URL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.chdir(box.repo)
    calls = []
    stats = {"duration_ms": 7000, "turns": 7, "cost_usd": None, "tokens_in": 70, "tokens_out": 7}
    fake_adapter(monkeypatch, calls, models=("zeta-1",), report=stats)
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "s.jsonl").write_text(json.dumps({"message": {"model": TODAY_MODEL}}) + "\n")
    (box.out / "plan.json").write_text(json.dumps({"kind": "user_story"}))
    (box.out / "check.txt").write_text("")
    from dokima import agent
    agent.main(["agent", "record", "planner", "", str(box.out), str(box.out / "check.txt"), "true", str(logs)])
    rec = json.load(open(box.out / "record.json"))
    assert rec.get("models") == ["zeta-1"], f"698.12: the record names models {rec.get('models')}, not zeta's zeta-1"
    assert rec.get("report") == stats, f"698.12: the record's stats {rec.get('report')} are not the ones zeta reported"


def test_claude_codes_record_reads_as_today(record_property, tmp_path, monkeypatch):
    """Behind the interface, Claude Code's run still yields today's models, stats and transcript.

    Proves 698.13. With no settings file, gives the planner a Claude session log naming two models and a Claude report,
    and checks the interface reads the models, the stats and the readable transcript (secret removed) the way the
    record reads them today."""
    record_property("proves", "698.13")
    box = Box(tmp_path)
    monkeypatch.chdir(box.repo)
    logs = tmp_path / "logs" / ".claude" / "projects" / "p"
    logs.mkdir(parents=True)
    (logs / "s.jsonl").write_text(
        json.dumps({"message": {"model": "claude-opus-5-5", "role": "assistant", "content": "Hello secret-value-698."}})
        + "\n" + json.dumps({"message": {"model": "claude-haiku-5-5", "role": "assistant", "content": "Bye."}}) + "\n")
    (box.out / "claude.json").write_text(json.dumps(
        {"duration_ms": 240000, "num_turns": 23, "total_cost_usd": 3.2,
         "usage": {"input_tokens": 100, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 3, "output_tokens": 9}}))
    agents = agents_module("698.13")
    models = agents.models("planner", str(box.out), str(tmp_path / "logs"))
    assert models == ["claude-haiku-5-5", "claude-opus-5-5"], f"698.13: Claude's models read as {models}"
    report = agents.report("planner", str(box.out))
    assert report == {"duration_ms": 240000, "turns": 23, "cost_usd": 3.2, "tokens_in": 123, "tokens_out": 9}, \
        f"698.13: Claude's stats read as {report}"
    text = agents.transcript("planner", str(tmp_path / "logs"), ["secret-value-698"])
    assert "**Agent:** Hello [secret removed]." in text and "secret-value-698" not in text, \
        f"698.13: Claude's transcript does not read as today, secret removed:\n{text[:600]}"


def test_claude_codes_record_with_no_report_has_no_stats(record_property, tmp_path, monkeypatch):
    """A Claude Code run that left no report has no stats, as today.

    Proves 698.13, edge case: the agent stopped before printing its report. With no claude.json in the run's folder
    the interface's stats are empty, as the record's are today, while the models still read from the log."""
    record_property("proves", "698.13")
    box = Box(tmp_path)
    monkeypatch.chdir(box.repo)
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "s.jsonl").write_text(json.dumps({"message": {"model": TODAY_MODEL}}) + "\n")
    agents = agents_module("698.13")
    assert agents.report("planner", str(box.out)) == {}, "698.13: a run with no Claude report should have no stats"
    assert agents.models("planner", str(box.out), str(logs)) == [TODAY_MODEL], \
        "698.13: a run with no Claude report lost the models its log names"


def test_a_model_runs_only_in_its_subscriptions_own_agent(record_property, tmp_path):
    """A role on a Claude subscription starts only Claude Code, whatever the model is called.

    Proves 698.14. Puts the planner on a Claude subscription with a model named like another vendor's,
    kimi-for-coding, and starts it through the interface. Only Claude Code may start: neither Kimi Code CLI nor Codex
    CLI is run, and nothing picks the agent from the model's name."""
    record_property("proves", "698.14")
    box = Box(tmp_path)
    box.write_settings(settings({"team": ("claude", TODAY_KEY)}, {"planner": ("team", "kimi-for-coding")}))
    box.run("planner")
    cmds = [c["cmd"] for c in box.calls()]
    assert cmds == ["claude"], f"698.14: a role on a Claude subscription started {cmds}, not only Claude Code"


def test_moving_a_role_takes_one_edit_of_its_own_lines(record_property, tmp_path):
    """Changing only the worker's subscription line moves the worker, and nothing else changes.

    Proves 698.15. Writes a settings file with two subscriptions, the planner and the worker both on the first. Then
    edits only the worker's subscription line to the second. The worker must now use the second subscription's
    secret, while the planner keeps the first's."""
    record_property("proves", "698.15")
    box = Box(tmp_path)
    subs = {"first": ("claude", "FIRST_KEY"), "second": ("claude", "SECOND_KEY")}
    before = settings(subs, {"planner": ("first", TODAY_MODEL), "worker": ("first", "claude-haiku-5-5")})
    box.write_settings(before)
    p = box.cli("key", "worker")
    assert p.returncode == 0 and p.stdout.strip() == "FIRST_KEY", f"698.15: the worker should start on FIRST_KEY: {said(p)}"
    after = before.replace("  worker:\n    subscription: first\n", "  worker:\n    subscription: second\n")
    assert after != before and after.count("\n") == before.count("\n")
    box.write_settings(after)
    p = box.cli("key", "worker")
    assert p.returncode == 0 and p.stdout.strip() == "SECOND_KEY", \
        f"698.15: after editing only its line the worker should use SECOND_KEY: {said(p)}"
    p = box.cli("key", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "FIRST_KEY", \
        f"698.15: moving the worker moved the planner too: {said(p)}"


def test_a_failed_agent_fails_the_run_with_no_fallback(record_property, tmp_path):
    """When a role's agent fails, the run fails, and no other subscription is tried.

    Proves 698.16. Writes a settings file with two Claude subscriptions, the planner on the first. Claude Code exits 3;
    starting the planner through the interface must fail with that exit code, after exactly one agent start."""
    record_property("proves", "698.16")
    box = Box(tmp_path)
    box.write_settings(settings({"first": ("claude", "FIRST_KEY"), "spare": ("claude", "SPARE_KEY")},
                                {"planner": ("first", TODAY_MODEL), "worker": ("spare", TODAY_MODEL)}))
    p = box.run("planner", FAKE_EXIT="3")
    calls = box.calls()
    assert len(calls) == 1 and calls[0]["cmd"] == "claude", \
        f"698.16: a failed agent was followed by another start, or none ran: {calls}"
    assert p.returncode == 3, f"698.16: the run did not fail with the agent's exit code 3: {said(p)}"


def test_other_sections_can_join_the_settings_file(record_property, tmp_path):
    """Other sections in the settings file leave each role's settings as written.

    Proves 698.17. Writes a settings file with a section before and one after the subscriptions and roles, each with
    nested settings that look like a role's. The planner must still get its own model and secret."""
    record_property("proves", "698.17")
    box = Box(tmp_path)
    box.write_settings(settings(
        {"team": ("claude", "TEAM_KEY")}, {"planner": ("team", "claude-sonnet-5-5")},
        before="later:\n  planner:\n    model: not-this-one\n",
        after="checks:\n  planner:\n    subscription: not-this-one\n    model: nor-this-one\n"))
    p = box.cli("model", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "claude-sonnet-5-5", \
        f"698.17: another section changed the planner's model: {said(p)}"
    p = box.cli("key", "planner")
    assert p.returncode == 0 and p.stdout.strip() == "TEAM_KEY", \
        f"698.17: another section changed the planner's secret: {said(p)}"

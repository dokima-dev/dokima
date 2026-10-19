"""Tests for #907: a rejected key is reported as such, not a missing plan.

When the agent cannot log in (its provider answers 401 or 403, or says the token is invalid or expired), the run
leaves no hand-back, and the record used to blame the agent ("found no plan.json"). These tests write a run's record
the way the agent workflow does, from a fake agent output in the run's folder, and check what the owner reads. Each
shipped agent (Claude Code, Codex, Kimi) gets its own case, in the output file its adapter keeps. The setup audit's
key check is run against fake `claude`, `codex` and `kimi` commands on the PATH, so no real provider is ever called.
"""
import base64
import io
import json
import os
import subprocess
import sys
import tarfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from test_audit import REPO, GitHub, audit  # noqa: E402
from test_start import load_yaml  # noqa: E402

MISSING_PLAN = ("found no plan.json: the planner always hands back a plan, a plan.json of kind user_story or feature, "
                "raising its questions for the owner in raises")
REJECTED_401 = "Failed to authenticate. API Error: 401 OAuth access token is invalid."
KEY = "sk-ant-oat01-907secretvalueABCDEFGHIJKLMNOP"
CODEX_KEY = "sk-proj-907codexsecretQRSTUVWXYZabcdefgh"
DECLARED = ("CLAUDE_CODE_OAUTH_TOKEN", "CODEX_API_KEY", "KIMI_API_KEY")


def kimi_sign_in():
    """A stored Kimi sign-in as setup keeps it: a base64 gzip tar of one file."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        data = b'{"access_token": "907kimisecretTOKENvalue1234567890"}'
        info = tarfile.TarInfo(".kimi/credentials/kimi-code.json")
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    return base64.b64encode(buf.getvalue()).decode()


KIMI_KEY = kimi_sign_in()
KEYS = {"CLAUDE_CODE_OAUTH_TOKEN": KEY, "CODEX_API_KEY": CODEX_KEY, "KIMI_API_KEY": KIMI_KEY}


def claude_output(text, error=True):
    """Claude Code's printed report (claude.json) for a run that ended with TEXT."""
    return json.dumps({"type": "result", "subtype": "success", "is_error": error, "result": text, "num_turns": 1,
                       "duration_ms": 500, "total_cost_usd": 0, "usage": {"input_tokens": 0, "output_tokens": 0}})


def codex_output(text, error=True):
    """Codex's event stream (codex.jsonl): a run failing with TEXT, or answering TEXT."""
    events = [{"type": "thread.started", "thread_id": "t907"}, {"type": "turn.started"}]
    if error:
        events += [{"type": "error", "message": text}, {"type": "turn.failed", "error": {"message": text}}]
    else:
        events += [{"type": "item.completed", "item": {"id": "i0", "type": "agent_message", "text": text}},
                   {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}}]
    return "\n".join(json.dumps(e) for e in events) + "\n"


def kimi_output(text, error=True):
    """Kimi's stream (kimi.jsonl): a run failing with TEXT, or answering TEXT."""
    if error:
        return json.dumps({"type": "error", "message": text}) + "\n"
    return json.dumps({"role": "assistant", "content": text}) + "\n"


OUTPUTS = {"claude": ("claude.json", claude_output), "codex": ("codex.jsonl", codex_output),
           "kimi": ("kimi.jsonl", kimi_output)}
CODEX_401 = "unexpected status 401 Unauthorized: Incorrect API key provided: sk-proj-****efgh."
KIMI_401 = "Error code: 401 - {'error': {'message': 'Invalid Authentication', 'type': 'invalid_authentication_error'}}"


def planner_on(agent, key):
    """Settings that run the planner on AGENT with the secret KEY."""
    return (f"agents:\n  subscriptions:\n    mine:\n      agent: {agent}\n      key: {key}\n"
            f"  roles:\n    planner:\n      subscription: mine\n      model: m907\n")


def write_record(tmp_path, output, settings=None, extra_env=None, agent="claude"):
    """Write the planner's record after a run of AGENT that left OUTPUT and no plan.

    Returns (comment.md, record.json) as text. The code check found no plan.json, as it does today."""
    out, pack, logs = tmp_path / "out", tmp_path / "pack", tmp_path / "logs"
    for d in (out, pack / "in", logs):
        d.mkdir(parents=True)
    if output is not None:
        (out / OUTPUTS[agent][0]).write_text(output)
    (out / "check.txt").write_text(MISSING_PLAN + "\n")
    settings_file = tmp_path / "settings.yaml"
    if settings:
        settings_file.write_text(settings)
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "DOKIMA_SETTINGS": str(settings_file), **(extra_env or {})}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "STAGE", "BASE", "LOG_URL"):
        env.pop(k, None)
    for k in [k for k in env if k.startswith("SCRUB_")]:
        env.pop(k)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "record", "planner", "", str(out), str(out / "check.txt"),
                        "false", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"the record step failed:\n{(p.stdout + p.stderr)[-800:]}"
    return (out / "comment.md").read_text(), (out / "record.json").read_text()


def assert_key_rejected(comment, criterion, what):
    """Fail naming CRITERION unless the comment reports a rejected key and not a missing plan."""
    assert "Model key rejected" in comment, \
        f"{criterion}: {what} did not end the run as \"Model key rejected\":\n{comment[:600]}"
    assert "found no plan.json" not in comment and "hand-back rejected" not in comment, \
        f"{criterion}: {what} is still reported as a missing or rejected hand-back:\n{comment[:600]}"


def test_a_401_from_the_provider_reads_model_key_rejected(record_property, tmp_path):
    """A 401 reads "Model key rejected"; a plain missing plan still says so.

    Writes the record of a planner run whose agent printed the provider's 401 and left no plan, and checks the card
    says "Model key rejected" with no word of a missing plan. Then writes one whose agent ran fine but left no plan,
    and checks that one still says the plan is missing.

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path / "bad-key", claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.1", "a 401 from the provider")
    comment, _ = write_record(tmp_path / "no-plan", claude_output("I finished.", error=False))
    assert "found no plan.json" in comment and "Model key rejected" not in comment, \
        f"907.1: a run that really left no plan no longer says the plan is missing:\n{comment[:600]}"


def test_a_403_from_the_provider_reads_model_key_rejected(record_property, tmp_path):
    """A run whose agent was refused with a 403 ends as "Model key rejected".

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path, claude_output("API Error: 403 Forbidden: this key may not use this model."))
    assert_key_rejected(comment, "907.1", "a 403 from the provider")


def test_an_expired_token_reads_model_key_rejected(record_property, tmp_path):
    """A run whose agent says its token expired ends as "Model key rejected".

    Proves 907.1."""
    record_property("proves", "907.1")
    comment, _ = write_record(tmp_path, claude_output("OAuth token has expired. Please obtain a new token."))
    assert_key_rejected(comment, "907.1", "an expired token")


def test_a_refused_codex_key_reads_model_key_rejected(record_property, tmp_path):
    """A refused Codex key reads "Model key rejected"; a missing Codex plan still says so.

    Runs the planner on Codex by settings and writes its stream as Codex keeps it, `codex.jsonl`.

    Proves 907.1."""
    record_property("proves", "907.1")
    codex = planner_on("codex", "CODEX_API_KEY")
    comment, _ = write_record(tmp_path / "bad-key", codex_output(CODEX_401), settings=codex, agent="codex")
    assert_key_rejected(comment, "907.1", "a 401 refusing the Codex key")
    comment, _ = write_record(tmp_path / "no-plan", codex_output("I finished.", error=False), settings=codex,
                              agent="codex")
    assert "found no plan.json" in comment and "Model key rejected" not in comment, \
        f"907.1: a Codex run that really left no plan no longer says the plan is missing:\n{comment[:600]}"


def test_a_refused_kimi_key_reads_model_key_rejected(record_property, tmp_path):
    """A refused Kimi sign-in reads "Model key rejected"; a missing Kimi plan still says so.

    Runs the planner on Kimi by settings and writes its stream as Kimi keeps it, `kimi.jsonl`.

    Proves 907.1."""
    record_property("proves", "907.1")
    kimi = planner_on("kimi", "KIMI_API_KEY")
    comment, _ = write_record(tmp_path / "bad-key", kimi_output(KIMI_401), settings=kimi, agent="kimi")
    assert_key_rejected(comment, "907.1", "a 401 refusing the Kimi sign-in")
    comment, _ = write_record(tmp_path / "no-plan", kimi_output("I finished.", error=False), settings=kimi,
                              agent="kimi")
    assert "found no plan.json" in comment and "Model key rejected" not in comment, \
        f"907.1: a Kimi run that really left no plan no longer says the plan is missing:\n{comment[:600]}"


def test_the_record_names_the_secret_the_settings_use(record_property, tmp_path):
    """The rejected-key card names the repo secret the planner's settings use for its key.

    With no settings it must name `CLAUDE_CODE_OAUTH_TOKEN`, today's secret; with settings naming
    `CODEX_API_KEY` for the planner, it must name that one instead.

    Proves 907.2."""
    record_property("proves", "907.2")
    comment, _ = write_record(tmp_path / "default", claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.2", "a 401 from the provider")
    assert "CLAUDE_CODE_OAUTH_TOKEN" in comment, \
        f"907.2: the card does not name the secret CLAUDE_CODE_OAUTH_TOKEN the settings use:\n{comment[:600]}"
    other = planner_on("claude", "CODEX_API_KEY")
    comment, _ = write_record(tmp_path / "other", claude_output(REJECTED_401), settings=other)
    assert "CODEX_API_KEY" in comment and "CLAUDE_CODE_OAUTH_TOKEN" not in comment, \
        f"907.2: with settings naming CODEX_API_KEY, the card does not name that secret alone:\n{comment[:600]}"


def test_each_agents_record_names_its_own_secret(record_property, tmp_path):
    """A refused Codex key names `CODEX_API_KEY`; a refused Kimi sign-in names `KIMI_API_KEY`.

    Proves 907.2."""
    record_property("proves", "907.2")
    for agent, secret, text in (("codex", "CODEX_API_KEY", CODEX_401), ("kimi", "KIMI_API_KEY", KIMI_401)):
        comment, _ = write_record(tmp_path / agent, OUTPUTS[agent][1](text), settings=planner_on(agent, secret),
                                  agent=agent)
        assert_key_rejected(comment, "907.2", f"a 401 refusing the {agent} key")
        others = [s for s in DECLARED if s != secret and s in comment]
        assert secret in comment and not others, \
            f"907.2: the {agent} card does not name {secret} alone (also names {others}):\n{comment[:600]}"


def test_the_record_says_to_make_a_new_key_and_replace_the_repo_secret(record_property, tmp_path):
    """The card says the provider refused the key: make a new one, replace the secret.

    Proves 907.3."""
    record_property("proves", "907.3")
    comment, _ = write_record(tmp_path, claude_output(REJECTED_401))
    assert_key_rejected(comment, "907.3", "a 401 from the provider")
    low = comment.lower()
    missing = [w for w in ("refused", "new one", "replace", "repo secret") if w not in low]
    assert not missing, (f"907.3: the card does not tell the owner the provider refused the key and to make a new one "
                         f"and replace the repo secret; it lacks {missing}:\n{comment[:600]}")


def test_the_record_never_prints_any_part_of_the_key(record_property, tmp_path):
    """No piece of the key reaches the rejected-key card or its record.

    The key sits in the run's environment under both names the agent step uses; the card and record must not hold
    any 8 characters of it in a row.

    Proves 907.4."""
    record_property("proves", "907.4")
    comment, record = write_record(tmp_path, claude_output(REJECTED_401),
                                   extra_env={"DOKIMA_AGENT_KEY": KEY, "CLAUDE_CODE_OAUTH_TOKEN": KEY})
    assert_key_rejected(comment, "907.4", "a 401 from the provider")
    pieces = {KEY[i:i + 8] for i in range(len(KEY) - 7)}
    leaked = sorted(p for p in pieces if p in comment or p in record)
    assert not leaked, f"907.4: part of the key was printed on the card or its record: {leaked[:3]}"


def test_a_codex_refusal_never_prints_the_keys_tail(record_property, tmp_path):
    """A refused Codex key's card never repeats the key's tail the provider echoed.

    Codex's refusal quotes the key masked, as `sk-proj-****efgh`. The planner runs on Codex with the key in its
    environment; the card and record must hold neither the key's last 4 characters nor any 8 of it in a row, so
    quoting the provider's message fails.

    Proves 907.4."""
    record_property("proves", "907.4")
    comment, record = write_record(tmp_path, codex_output(CODEX_401), settings=planner_on("codex", "CODEX_API_KEY"),
                                   extra_env={"DOKIMA_AGENT_KEY": CODEX_KEY, "CODEX_API_KEY": CODEX_KEY},
                                   agent="codex")
    assert_key_rejected(comment, "907.4", "a 401 refusing the Codex key")
    pieces = {CODEX_KEY[-4:]} | {CODEX_KEY[i:i + 8] for i in range(len(CODEX_KEY) - 7)}
    leaked = sorted(p for p in pieces if p in comment or p in record)
    assert not leaked, f"907.4: part of the Codex key the provider echoed was printed on the card or record: {leaked[:3]}"


THREE_AGENTS = """agents:
  subscriptions:
    c: {agent: claude, key: CLAUDE_CODE_OAUTH_TOKEN}
    x: {agent: codex, key: CODEX_API_KEY}
    k: {agent: kimi, key: KIMI_API_KEY}
  roles:
    planner: {subscription: c, model: claude-opus-5-5}
    worker: {subscription: x, model: gpt-5-codex}
    reviewer: {subscription: k, model: kimi-k2}
"""
REFUSALS = {"claude": REJECTED_401, "codex": CODEX_401, "kimi": KIMI_401}


def fake_agents(tmp_path, monkeypatch, settings=None, refuse=()):
    """Put fake `claude`, `codex` and `kimi` on the PATH; those in REFUSE print a 401.

    The repo at tmp_path/repo holds SETTINGS (also named by DOKIMA_SETTINGS); home is a temp folder. Returns
    (repo root, call log): each start of a fake agent writes its name on one line of the log."""
    root, bin_dir, calls, home = tmp_path / "repo", tmp_path / "bin", tmp_path / "calls.txt", tmp_path / "home"
    for d in (root / ".dokima", bin_dir, home):
        d.mkdir(parents=True, exist_ok=True)
    settings_file = root / ".dokima" / "settings.yaml"
    if settings:
        settings_file.write_text(settings)
    for agent, (_, output) in OUTPUTS.items():
        bad = agent in refuse
        text = output(REFUSALS[agent], True) if bad else output("OK", False)
        script = bin_dir / agent
        script.write_text(f"#!/bin/sh\necho {agent} >> '{calls}'\ncat <<'EOF'\n{text.rstrip()}\nEOF\n"
                          f"exit {1 if bad else 0}\n")
        script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("DOKIMA_SETTINGS", str(settings_file))
    monkeypatch.chdir(root)
    for k in [k for k in os.environ if k.startswith("DOKIMA_KEY_") or k in DECLARED or k == "DOKIMA_AGENT_KEY"]:
        monkeypatch.delenv(k)
    return root, calls


def give_keys(monkeypatch, *names):
    """Give the audit the value of each secret in NAMES, as the audit workflow does."""
    for name in names:
        monkeypatch.setenv(f"DOKIMA_KEY_{name}", KEYS[name])


def calls_made(calls, agent):
    """How many times the fake AGENT was started."""
    return calls.read_text().split().count(agent) if calls.exists() else 0


def run_audit(a, root):
    """The audit's lines for a clean repo holding every declared secret."""
    github = GitHub()
    github.secret_names |= set(DECLARED)
    return a.compare(github, REPO, root=str(root))


def test_the_audit_calls_each_set_key_once(record_property, tmp_path, monkeypatch):
    """The setup audit starts each set key's agent once.

    With the planner on Claude Code and the worker on Codex, both keys set, each agent is started exactly once and
    nothing is reported. With no settings, all three roles share Claude Code's key, so Claude Code starts once. The
    test also checks the audit workflow installs the agents before the audit runs, so a call can be made.

    Proves 907.5."""
    record_property("proves", "907.5")
    a = audit("907.5")
    root, calls = fake_agents(tmp_path / "three", monkeypatch, THREE_AGENTS)
    give_keys(monkeypatch, "CLAUDE_CODE_OAUTH_TOKEN", "CODEX_API_KEY")
    lines = run_audit(a, root)
    made = {agent: calls_made(calls, agent) for agent in ("claude", "codex")}
    assert made == {"claude": 1, "codex": 1}, f"907.5: with both keys set, the audit started the agents {made} times"
    assert lines == [], f"907.5: keys the providers accepted are reported: {lines}"
    root, calls = fake_agents(tmp_path / "default", monkeypatch)
    give_keys(monkeypatch, "CLAUDE_CODE_OAUTH_TOKEN")
    run_audit(a, root)
    assert calls_made(calls, "claude") == 1, \
        f"907.5: three roles on one key started Claude Code {calls_made(calls, 'claude')} times, not once"
    steps = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "audit.yml")).read())["jobs"]["audit"]["steps"]
    run_step = next(s for s in steps if "python3 -m dokima.audit" in str(s.get("run", "")))
    assert any("dokima.agents install" in str(s.get("run", "")) for s in steps[:steps.index(run_step)]), \
        "907.5: the audit workflow never installs the agents before the audit runs, so no call can be made"


def test_the_audit_skips_a_key_that_is_not_set(record_property, tmp_path, monkeypatch):
    """A key the settings use but that is not set starts no agent at setup.

    With the three agents in the settings and only Claude Code's key set, Codex and Kimi are never started; with no
    key set, no agent is started at all.

    Proves 907.7."""
    record_property("proves", "907.7")
    a = audit("907.7")
    root, calls = fake_agents(tmp_path / "none", monkeypatch, THREE_AGENTS)
    run_audit(a, root)
    total = sum(calls_made(calls, agent) for agent in OUTPUTS)
    assert total == 0, f"907.7: with no key set, the audit still started an agent {total} times"
    root, calls = fake_agents(tmp_path / "one", monkeypatch, THREE_AGENTS)
    give_keys(monkeypatch, "CLAUDE_CODE_OAUTH_TOKEN")
    run_audit(a, root)
    skipped = {agent: calls_made(calls, agent) for agent in ("codex", "kimi")}
    assert calls_made(calls, "claude") == 1 and skipped == {"codex": 0, "kimi": 0}, \
        f"907.7: with only Claude Code's key set, the audit started claude {calls_made(calls, 'claude')} times and {skipped}"


def test_the_audit_reports_a_rejected_key_as_one_line(record_property, tmp_path, monkeypatch):
    """A key refused at setup is one audit line naming only its secret.

    Claude Code alone, its key refused: one line naming `CLAUDE_CODE_OAUTH_TOKEN`. Three agents, all keys set, only
    Codex's refused: one line naming `CODEX_API_KEY` and no other secret.

    Proves 907.6."""
    record_property("proves", "907.6")
    a = audit("907.6")
    root, _ = fake_agents(tmp_path / "claude", monkeypatch, refuse=("claude",))
    give_keys(monkeypatch, "CLAUDE_CODE_OAUTH_TOKEN")
    lines = run_audit(a, root)
    assert len(lines) == 1 and "CLAUDE_CODE_OAUTH_TOKEN" in lines[0], \
        f"907.6: a refused Claude Code key is not one line naming CLAUDE_CODE_OAUTH_TOKEN: {lines}"
    root, _ = fake_agents(tmp_path / "codex", monkeypatch, THREE_AGENTS, refuse=("codex",))
    give_keys(monkeypatch, *DECLARED)
    lines = run_audit(a, root)
    assert len(lines) == 1 and "CODEX_API_KEY" in lines[0], \
        f"907.6: a refused Codex key is not one line naming CODEX_API_KEY: {lines}"
    others = [s for s in DECLARED if s != "CODEX_API_KEY" and s in lines[0]]
    assert not others, f"907.6: the refused Codex key's line also names {others}: {lines[0]}"


def test_the_audit_job_gets_each_declared_agent_key_by_name(record_property):
    """The audit job is handed every declared agent key by name.

    `entry.yml` passes each of the three keys to the audit job, `audit.yml` declares each one, and the audit step
    reads each as `DOKIMA_KEY_<NAME>` from the secret of that name.

    Proves 907.8."""
    record_property("proves", "907.8")
    entry = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "entry.yml")).read())
    passed = str(entry["jobs"]["audit"].get("secrets"))
    missing = [k for k in DECLARED if f"secrets.{k}" not in passed]
    assert not missing, f"907.8: entry.yml never passes these agent keys to the audit job: {missing}"
    wf = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "audit.yml")).read())
    on = wf.get("on") or wf.get(True)
    declared = (on.get("workflow_call") or {}).get("secrets") or {}
    missing = [k for k in DECLARED if k not in declared]
    assert not missing, f"907.8: audit.yml does not declare these agent keys: {missing}"
    run_step = next(s for s in wf["jobs"]["audit"]["steps"] if "python3 -m dokima.audit" in str(s.get("run", "")))
    env = run_step.get("env") or {}
    missing = [k for k in DECLARED if f"secrets.{k}" not in str(env.get(f"DOKIMA_KEY_{k}"))]
    assert not missing, f"907.8: the audit step is not given these keys as DOKIMA_KEY_<name>: {missing}"


def test_the_audit_never_prints_any_part_of_a_key(record_property, tmp_path, monkeypatch, capsys):
    """No piece of any refused key reaches what the audit prints.

    Proves 907.9."""
    record_property("proves", "907.9")
    a = audit("907.9")
    root, _ = fake_agents(tmp_path, monkeypatch, THREE_AGENTS, refuse=tuple(OUTPUTS))
    give_keys(monkeypatch, *DECLARED)
    lines = run_audit(a, root)
    assert len(lines) == 3, f"907.9: three refused keys were not reported, so nothing was checked: {lines}"
    shown = "\n".join(lines) + "".join(capsys.readouterr())
    leaked = sorted({k for k, v in KEYS.items() for i in range(len(v) - 7) if v[i:i + 8] in shown})
    assert not leaked, f"907.9: part of these keys was printed by the audit: {leaked}"

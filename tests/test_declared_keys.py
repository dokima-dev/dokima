"""Tests for #896: the settings may name only the agent keys entry.yml declares.

GitHub hands a reusable workflow in another account's repo only the secrets it declares by name, so a key outside
entry.yml's list never reaches the jobs. The setup audit reports such a key in one line, a job naming it fails with that
same line rather than as a missing key, and the install docs say so. The declared keys are read from entry.yml itself,
so the tests follow it when a release declares another.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_settings_workflows as sw  # noqa: E402
from test_audit import REPO, GitHub, audit  # noqa: E402
from test_thin_install import everything_said, read_yaml, with_context  # noqa: E402

ENTRY = os.path.join(ROOT, ".github", "workflows", "entry.yml")
DOCS = ("README.md", os.path.join("docs", "wiki", "Installing.md"))


def declared():
    """The agent keys entry.yml declares: every secret it takes, less the app's own key."""
    return sorted(set(read_yaml(ENTRY)["on"]["workflow_call"]["secrets"]) - {"DOKIMA_APP_KEY"})


def settings(key, role="worker"):
    """A settings file putting ROLE on a Claude subscription whose key is the secret KEY."""
    return (f"agents:\n  subscriptions:\n    mine:\n      agent: claude\n      key: {key}\n"
            f"  roles:\n    {role}:\n      subscription: mine\n      model: claude-opus-5-5\n")


def write(root, key):
    """Write settings naming KEY into ROOT's .dokima folder."""
    os.makedirs(root / ".dokima", exist_ok=True)
    (root / ".dokima" / "settings.yaml").write_text(settings(key))


def worker_key(root):
    """Ask Dokima, from ROOT, which key the worker's settings name, the way a job does."""
    env = {**os.environ, "PYTHONPATH": ROOT}
    env.pop("DOKIMA_SETTINGS", None)
    return subprocess.run([sys.executable, "-m", "dokima.agents", "key", "worker"], cwd=root, env=env,
                          capture_output=True, text=True)


def says_the_rule(line, key):
    """True when LINE names KEY, says it never reaches jobs, and what to do."""
    return (key in line and "never reach the jobs" in line and "use a declared name" in line
            and "declared in a release" in line)


def audit_lines(tmp_path, key, live):
    """Every audit line naming KEY, for settings naming KEY and repo secrets LIVE."""
    write(tmp_path, key)
    g = GitHub()
    g.secret_names = set(live)
    return [l for l in audit("896").compare(g, REPO, root=str(tmp_path)) if key in l]


def test_only_the_agent_keys_entry_yml_declares_are_accepted(record_property, tmp_path):
    """Settings may name each agent key entry.yml declares, and no other.

    Proves 896.1. For every agent key entry.yml declares, settings naming it give the worker that key. Then settings
    naming MY_KEY, which entry.yml does not declare, must stop with a non-zero exit."""
    record_property("proves", "896.1")
    keys = declared()
    assert keys, "896.1: entry.yml declares no agent keys"
    for key in keys:
        write(tmp_path / key, key)
        p = worker_key(tmp_path / key)
        assert p.returncode == 0 and p.stdout.strip() == key, \
            f"896.1: settings naming the declared key {key} were refused: exit {p.returncode}, said {p.stderr!r}"
    write(tmp_path / "mine", "MY_KEY")
    p = worker_key(tmp_path / "mine")
    assert p.returncode != 0, \
        f"896.1: settings naming MY_KEY, which entry.yml does not declare ({keys}), were accepted: {p.stdout!r}"


def test_the_audit_reports_an_undeclared_key_in_one_line(record_property, tmp_path):
    """The setup audit reports an undeclared agent key in one line.

    Proves 896.2. Settings name MY_KEY, set as a repo secret: the audit must give exactly one line naming it, saying it
    will never reach the jobs, to use a declared name or ask for it to be declared in a release. Settings naming the
    declared CODEX_API_KEY, set as a repo secret, must get no line at all."""
    record_property("proves", "896.2")
    lines = audit_lines(tmp_path / "mine", "MY_KEY", {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "MY_KEY"})
    assert len(lines) == 1 and says_the_rule(lines[0], "MY_KEY"), \
        (f"896.2: for settings naming MY_KEY the audit should give one line saying it will never reach the jobs, "
         f"to use a declared name or ask for it to be declared in a release; it said {lines}")
    lines = audit_lines(tmp_path / "codex", "CODEX_API_KEY", {"DOKIMA_APP_KEY", "CODEX_API_KEY"})
    assert lines == [], f"896.2: the declared key CODEX_API_KEY, which is set, was reported: {lines}"


def test_a_job_naming_an_undeclared_key_fails_with_the_audit_line(record_property, tmp_path):
    """A job naming an undeclared key fails with the audit's line, not as missing.

    Proves 896.3. Runs agent.yml's planner run with settings naming MY_KEY, a secret that never reaches the job. The
    run must fail, what it says must hold the very line the audit gives for MY_KEY, and nothing it says may call MY_KEY
    missing."""
    record_property("proves", "896.3")
    box = sw.Box(tmp_path / "box", settings("MY_KEY", "planner"))
    with_context(box, drop_secrets=("MY_KEY",))
    result = box.run("agent.yml", "run", name="planner", role="planner")
    said = everything_said(box)
    assert result == "failure", f"896.3: a run naming the undeclared key MY_KEY did not fail; job {result}"
    missing = [l for l in said.splitlines() if "MY_KEY" in l and "missing" in l]
    assert not missing, f"896.3: the run called MY_KEY missing instead of undeclared: {missing}"
    lines = audit_lines(tmp_path / "audit", "MY_KEY", {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "MY_KEY"})
    assert len(lines) == 1 and says_the_rule(lines[0], "MY_KEY") and lines[0] in said, \
        f"896.3: the run did not say the audit's line for MY_KEY ({lines}); it said:\n{box.tail()}"


def sentences(text):
    """TEXT cut into sentences."""
    return re.split(r"(?<=[.:;])\s+", text)


def lists_only(text, keys):
    """True when one sentence of TEXT says "only" and names every key in KEYS."""
    return any("only" in s and all(k in s for k in keys) for s in sentences(text))


def test_the_install_docs_say_only_declared_keys_reach_the_jobs(record_property):
    """The docs say settings may name only the declared agent keys.

    Proves 896.4. In README.md and docs/wiki/Installing.md, one sentence must name every agent key entry.yml declares
    and say "only", and one sentence must say another key never reaches the jobs and that the audit says so. The
    settings format written at the top of dokima/agents.py must also say its key is only one of those keys."""
    record_property("proves", "896.4")
    keys = declared()
    for doc in DOCS:
        text = open(os.path.join(ROOT, doc)).read()
        assert lists_only(text, [f"`{k}`" for k in keys]), \
            f"896.4: {doc} has no sentence saying settings may name only {keys}"
        never = [s for s in sentences(text) if "never reach" in s and "jobs" in s and "audit" in s]
        assert never, f"896.4: {doc} never says another agent key never reaches the jobs and the audit says so"
    from dokima import agents
    assert lists_only(agents.__doc__ or "", keys), \
        f"896.4: the settings format at the top of dokima/agents.py never says a key may be only one of {keys}"

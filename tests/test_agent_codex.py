"""Tests for #700: a Codex role runs in Codex CLI, on the file's model.

The settings file `.dokima/agents.yml` names a subscription whose agent is `codex`; the one agent interface
(`python3 -m dokima.agents run ROLE PROMPT_FILE OUT`, from #698) then loads the adapter `dokima/agent_codex.py`.
Setup stores a Codex subscription by key (#697), and the run's key arrives in DOKIMA_AGENT_KEY.

Codex CLI runs unattended as `codex exec PROMPT`. Each test runs the real interface from outside in a temp repo folder,
with a stand-in `codex` first on PATH that logs its arguments and the key it was handed, then exits FAKE_EXIT.
Nothing leaves the machine.
"""
import json
import os
import subprocess
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CODEX = textwrap.dedent('''\
    #!{python}
    """A stand-in Codex CLI: logs its arguments and key, then exits FAKE_EXIT."""
    import json, os, sys
    keys = {{k: os.environ[k] for k in ("CODEX_API_KEY", "OPENAI_API_KEY") if k in os.environ}}
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps({{"argv": sys.argv[1:], "keys": keys}}) + "\\n")
    print(json.dumps({{"type": "item.completed", "item": {{"type": "agent_message", "text": "done"}}}}))
    sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
''')

SETTINGS = textwrap.dedent('''\
    subscriptions:
      codex-pro:
        agent: codex
        key: CODEX_API_KEY
    roles:
      worker:
        subscription: codex-pro
        model: gpt-5-codex
''')

PROMPT = "Build issue 700."
KEY = "sk-codex-test-123"


class Box:
    """A temp repo whose worker is on Codex, and a stand-in Codex."""

    def __init__(self, tmp_path):
        """Make the folders, the stand-in and the settings file."""
        self.tmp = tmp_path
        self.repo, self.bin, self.out, self.home = (tmp_path / n for n in ("repo", "bin", "out", "home"))
        for d in (self.repo / ".dokima", self.bin, self.out, self.home):
            d.mkdir(parents=True)
        (self.repo / ".dokima" / "agents.yml").write_text(SETTINGS)
        codex = self.bin / "codex"
        codex.write_text(CODEX.format(python=sys.executable))
        codex.chmod(0o755)
        self.log = tmp_path / "codex-calls.jsonl"
        self.log.write_text("")

    def run(self, **extra):
        """Start the worker through the agent interface; return the process."""
        prompt = self.tmp / "prompt.md"
        prompt.write_text(PROMPT)
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLAUDE_CODE_OAUTH_TOKEN", "DOKIMA_AGENT_KEY", "DOKIMA_SETTINGS", "FAKE_EXIT",
                            "CODEX_API_KEY", "OPENAI_API_KEY")}
        env.update({"PATH": f"{self.bin}:{os.environ['PATH']}", "PYTHONPATH": ROOT, "HOME": str(self.home),
                    "FAKE_LOG": str(self.log), "DOKIMA_AGENT_KEY": KEY})
        env.update(extra)
        return subprocess.run([sys.executable, "-m", "dokima.agents", "run", "worker", str(prompt), str(self.out)],
                              cwd=self.repo, env=env, capture_output=True, text=True, timeout=60)

    def starts(self):
        """Every start of the stand-in Codex, oldest first, as {argv, keys}."""
        return [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]


def said(p):
    """A finished process's exit code and output, for a failure message."""
    return f"exit {p.returncode}; stdout: {p.stdout.strip()[-400:]!r}; stderr: {p.stderr.strip()[-400:]!r}"


def after(argv, *flags):
    """The value given after the first of FLAGS in ARGV, or None."""
    for flag in flags:
        if flag in argv[:-1]:
            return argv[argv.index(flag) + 1]
    return None


def test_a_codex_role_runs_in_codex_cli_with_its_model(record_property, tmp_path):
    """A Codex role starts Codex CLI unattended, with its prompt and the file's model.

    Proves 700.1. Puts the worker on a Codex subscription with model gpt-5-codex and starts it through the one agent
    interface. Codex CLI must start once, as `codex exec` with the prompt, gpt-5-codex as its model and the
    subscription's key; and the run must end with Codex's exit code 0."""
    record_property("proves", "700.1")
    box = Box(tmp_path)
    p = box.run()
    starts = box.starts()
    assert len(starts) == 1, f"700.1: Codex CLI should start once, it started {len(starts)} times: {said(p)}"
    argv = starts[0]["argv"]
    assert argv[:1] == ["exec"], f"700.1: Codex was not started unattended as `codex exec`: {argv}"
    assert PROMPT in argv, f"700.1: Codex did not get the prompt: {argv}"
    assert after(argv, "-m", "--model") == "gpt-5-codex", f"700.1: Codex did not run the file's model gpt-5-codex: {argv}"
    assert KEY in starts[0]["keys"].values(), \
        f"700.1: Codex was not handed the subscription's key as CODEX_API_KEY or OPENAI_API_KEY: {starts[0]['keys']}"
    assert p.returncode == 0, f"700.1: the run did not end with Codex's exit code 0: {said(p)}"


def test_a_codex_run_may_change_files(record_property, tmp_path):
    """A Codex role may change files, so a worker on Codex can build.

    Proves 700.1. Codex CLI's unattended run is read-only unless told otherwise. Starts the worker on its Codex
    subscription and checks Codex was started with write access: `--full-auto`, `--sandbox workspace-write` or
    `danger-full-access`, or `--dangerously-bypass-approvals-and-sandbox`."""
    record_property("proves", "700.1")
    box = Box(tmp_path)
    p = box.run()
    starts = box.starts()
    assert starts, f"700.1: Codex CLI never started: {said(p)}"
    argv = starts[0]["argv"]
    writes = ("--full-auto" in argv or "--dangerously-bypass-approvals-and-sandbox" in argv
              or after(argv, "-s", "--sandbox") in ("workspace-write", "danger-full-access"))
    assert writes, f"700.1: Codex was started read-only, so a worker on Codex cannot change files: {argv}"


def test_a_failed_codex_run_fails_the_run(record_property, tmp_path):
    """When Codex CLI fails, the run fails with Codex's own exit code.

    Proves 700.1. Starts the worker on its Codex subscription with the stand-in Codex exiting 3. Codex must have
    started, and the run must end with exit code 3, so a failed Codex run is never taken for a good one."""
    record_property("proves", "700.1")
    box = Box(tmp_path)
    p = box.run(FAKE_EXIT="3")
    assert len(box.starts()) == 1, f"700.1: Codex CLI never started: {said(p)}"
    assert p.returncode == 3, f"700.1: a failed Codex run did not fail the run with Codex's exit code 3: {said(p)}"

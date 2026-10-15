"""Tests for #699: a Kimi role runs in Kimi Code CLI, signed in from storage.

The settings file `.dokima/agents.yml` names a subscription whose agent is `kimi`; the one agent interface
(`python3 -m dokima.agents run ROLE PROMPT_FILE OUT`, from #698) then loads the adapter `dokima/agent_kimi.py`.
The run's key arrives in DOKIMA_AGENT_KEY. For a sign-in it is what `python3 -m dokima.setup add ... --sign-in`
stored (#697): the base64 text of a gzip tar of the files Kimi's login saved, each named by its path under the home
folder. Runs start on a fresh machine, so those files must be back under the home folder before Kimi starts.

The owner's tested command is `kimi -p PROMPT --output-format stream-json`, Kimi Code CLI 2.2.0. Each test runs the
real interface from outside in a temp repo folder, with a stand-in `kimi` first on PATH: it logs its arguments and
what it finds under the home folder at the moment it starts. The stored sign-in is made by setup's own sign-in step
against the same stand-in's login, so the round trip is the real one. Nothing leaves the machine.
"""
import json
import os
import subprocess
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from dokima import setup  # noqa: E402

KIMI = textwrap.dedent('''\
    #!{python}
    """A stand-in for Kimi Code CLI: `login` saves a sign-in; any other call logs what it saw and exits FAKE_EXIT."""
    import json, os, sys
    home = os.path.expanduser("~")
    if sys.argv[1:2] == ["login"]:
        os.makedirs(os.path.join(home, ".kimi", "credentials"), exist_ok=True)
        open(os.path.join(home, ".kimi", "credentials", "kimi-code.json"), "w").write('{{"access_token": "tok-123"}}')
        open(os.path.join(home, ".kimi", "config.toml"), "w").write('default_model = "kimi-for-coding"\\n')
        sys.exit(0)
    seen = {{}}
    for d, _, files in os.walk(os.path.join(home, ".kimi")):
        for name in files:
            p = os.path.join(d, name)
            seen[os.path.relpath(p, home)] = open(p).read()
    with open(os.environ["FAKE_LOG"], "a") as f:
        f.write(json.dumps({{"argv": sys.argv[1:], "home": seen}}) + "\\n")
    print(json.dumps({{"role": "assistant", "content": "done"}}))
    sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
''')

SETTINGS = textwrap.dedent('''\
    subscriptions:
      moon:
        agent: kimi
        key: KIMI_SIGN_IN
    roles:
      planner:
        subscription: moon
        model: kimi-k3
''')

PROMPT = "Plan issue 699."


class Box:
    """A temp repo on Kimi, a stand-in Kimi, and two home folders."""

    def __init__(self, tmp_path):
        """Make the folders, the stand-in, the settings file and the stored sign-in."""
        self.tmp = tmp_path
        self.repo, self.bin, self.out = tmp_path / "repo", tmp_path / "bin", tmp_path / "out"
        self.owner_home, self.runner_home = tmp_path / "owner-home", tmp_path / "runner-home"
        for d in (self.repo / ".dokima", self.bin, self.out, self.owner_home, self.runner_home):
            d.mkdir(parents=True)
        (self.repo / ".dokima" / "agents.yml").write_text(SETTINGS)
        kimi = self.bin / "kimi"
        kimi.write_text(KIMI.format(python=sys.executable))
        kimi.chmod(0o755)
        self.log = tmp_path / "kimi-calls.jsonl"
        self.log.write_text("")
        self.secret = self.stored_sign_in()

    def stored_sign_in(self):
        """The repo secret setup stores after Kimi's login on the owner's machine."""
        old = {k: os.environ.get(k) for k in ("HOME", "PATH")}
        os.environ.update({"HOME": str(self.owner_home), "PATH": f"{self.bin}:{old['PATH']}"})
        try:
            return setup.sign_in("kimi", "global")
        finally:
            for k, v in old.items():
                os.environ[k] = v

    def run(self, **extra):
        """Start the planner through the agent interface on the fresh home; return the process."""
        prompt = self.tmp / "prompt.md"
        prompt.write_text(PROMPT)
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLAUDE_CODE_OAUTH_TOKEN", "DOKIMA_AGENT_KEY", "DOKIMA_SETTINGS", "FAKE_EXIT")}
        env.update({"PATH": f"{self.bin}:{os.environ['PATH']}", "PYTHONPATH": ROOT, "HOME": str(self.runner_home),
                    "FAKE_LOG": str(self.log), "DOKIMA_AGENT_KEY": self.secret})
        env.update(extra)
        return subprocess.run([sys.executable, "-m", "dokima.agents", "run", "planner", str(prompt), str(self.out)],
                              cwd=self.repo, env=env, capture_output=True, text=True, timeout=60)

    def starts(self):
        """Every start of the stand-in Kimi, oldest first, as {argv, home}."""
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


def test_a_kimi_role_runs_in_kimi_code_cli_with_its_model(record_property, tmp_path):
    """A Kimi role starts Kimi Code CLI with its prompt and the file's model.

    Proves 699.1. Puts the planner on a Kimi subscription with model kimi-k3 and starts it through the one agent interface. Kimi
    Code CLI must start once, as the owner tested it: the prompt after -p, kimi-k3 as its model, stream-json output;
    and the run must end with Kimi's exit code 0."""
    record_property("proves", "699.1")
    box = Box(tmp_path)
    p = box.run()
    starts = box.starts()
    assert len(starts) == 1, f"699.1: Kimi Code CLI should start once, it started {len(starts)} times: {said(p)}"
    argv = starts[0]["argv"]
    assert after(argv, "-p") == PROMPT, f"699.1: Kimi did not get the prompt after -p: {argv}"
    assert after(argv, "-m", "--model") == "kimi-k3", f"699.1: Kimi did not run the file's model kimi-k3: {argv}"
    assert after(argv, "--output-format") == "stream-json", f"699.1: Kimi's output is not stream-json: {argv}"
    assert p.returncode == 0, f"699.1: the run did not end with Kimi's exit code 0: {said(p)}"


def test_a_failed_kimi_run_fails_the_run(record_property, tmp_path):
    """When Kimi Code CLI fails, the run fails with Kimi's own exit code.

    Proves 699.1. Starts the planner on its Kimi subscription with the stand-in Kimi exiting 3. Kimi must have started, and the run
    must end with exit code 3, so a failed Kimi run is never taken for a good one."""
    record_property("proves", "699.1")
    box = Box(tmp_path)
    p = box.run(FAKE_EXIT="3")
    assert len(box.starts()) == 1, f"699.1: Kimi Code CLI never started: {said(p)}"
    assert p.returncode == 3, f"699.1: a failed Kimi run did not fail the run with Kimi's exit code 3: {said(p)}"


def test_a_kimi_run_writes_the_stored_sign_in_back_before_kimi_starts(record_property, tmp_path):
    """On a fresh machine, Kimi starts already signed in, so no one signs in again.

    Proves 699.2. Makes the stored sign-in the way setup does, from Kimi's login on the owner's machine. Then starts the planner on
    a fresh machine whose home has no Kimi folder, with that sign-in as the run's key. When Kimi starts, every file
    the login saved must already be in the home folder, each the same as on the owner's machine."""
    record_property("proves", "699.2")
    box = Box(tmp_path)
    p = box.run()
    starts = box.starts()
    assert starts, f"699.2: Kimi Code CLI never started: {said(p)}"
    saved = {}
    for d, _, files in os.walk(box.owner_home / ".kimi"):
        for name in files:
            f = os.path.join(d, name)
            saved[os.path.relpath(f, box.owner_home)] = open(f).read()
    assert starts[0]["home"] == saved, \
        f"699.2: when Kimi started, the home held {sorted(starts[0]['home'])}, not the stored sign-in {sorted(saved)}"

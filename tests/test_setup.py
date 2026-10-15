"""Tests for #697: setup gathers a subscription's inputs and puts each where runs find it.

Setup is a command the owner runs once per subscription on their own machine, from the repo's root:

    python3 -m dokima.setup needs
        lists the inputs a subscription needs.
    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE [--role ROLE ...] --key
        reads the key from standard input and stores it as the repo secret SECRET.
    python3 -m dokima.setup add SUB --agent kimi --secret SECRET --model MODEL --role ROLE --sign-in --region REGION
        runs the agent's own login with the region, then stores the files it saved as the repo secret SECRET.

Either way it writes `.dokima/agents.yml` in the shape #698 reads, block style:

    subscriptions:
      SUB:
        agent: AGENT
        key: SECRET
    roles:
      ROLE:
        subscription: SUB
        model: MODEL

A stored sign-in is the base64 text of a gzip tar of the files the login saved, each named by its path under the home
folder (for Kimi `.kimi/credentials/...` and `.kimi/config.toml`, where Kimi's login keeps them), so a run can unpack it
into its own home folder before the agent starts (#699).

Each test runs the real command from outside in a temp folder, with HOME pointed at a temp home and stub `gh` and
`kimi` commands first on PATH. The stubs log every call (arguments and standard input) to a JSON-lines file, and the
stub login writes sign-in files the way Kimi's does. Nothing reaches GitHub or Kimi.
"""
import base64
import io
import json
import os
import subprocess
import sys
import tarfile
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STUB = textwrap.dedent('''\
    #!{python}
    """A stand-in for `{name}` that logs each call and, for a login, saves sign-in files like Kimi's."""
    import json, os, sys
    data = "" if sys.stdin.isatty() else sys.stdin.read()
    with open(os.environ["STUB_LOG"], "a") as f:
        f.write(json.dumps({{"cmd": "{name}", "argv": sys.argv[1:], "stdin": data}}) + "\\n")
    if "{name}" == "gh" and os.environ.get("GH_FAIL"):
        sys.stderr.write("HTTP 403: Resource not accessible by integration\\n")
        sys.exit(1)
    if "{name}" == "kimi" and sys.argv[1:2] == ["login"]:
        if os.environ.get("KIMI_FAIL"):
            sys.stderr.write("Device code expired\\n")
            sys.exit(1)
        home = os.environ["HOME"]
        os.makedirs(os.path.join(home, ".kimi", "credentials"), exist_ok=True)
        with open(os.path.join(home, ".kimi", "credentials", "kimi-code.json"), "w") as f:
            f.write('{{"access_token": "tok-123"}}')
        with open(os.path.join(home, ".kimi", "config.toml"), "w") as f:
            f.write('default_model = "kimi-for-coding"\\n')
''')

KEY = "sk-secret-value-42"


class Box:
    """One temp repo folder, temp home and stub commands where setup runs."""

    def __init__(self, tmp_path):
        """Make the folders, the stubs and the call log."""
        tmp_path.mkdir(parents=True, exist_ok=True)
        self.repo = tmp_path / "repo"
        self.home = tmp_path / "home"
        self.bin = tmp_path / "bin"
        for d in (self.repo, self.home, self.bin):
            d.mkdir()
        self.log = tmp_path / "calls.jsonl"
        self.log.write_text("")
        for name in ("gh", "kimi"):
            p = self.bin / name
            p.write_text(STUB.format(python=sys.executable, name=name))
            p.chmod(0o755)

    def run(self, *args, stdin="", **env):
        """Run `python3 -m dokima.setup ARGS` from the repo folder; return the finished process."""
        e = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}", HOME=str(self.home),
                 PYTHONPATH=ROOT, STUB_LOG=str(self.log), **env)
        return subprocess.run([sys.executable, "-m", "dokima.setup", *args], cwd=self.repo, env=e, input=stdin,
                              capture_output=True, text=True, timeout=30)

    def calls(self, cmd):
        """Every logged call to CMD, oldest first."""
        return [c for c in map(json.loads, self.log.read_text().splitlines()) if c["cmd"] == cmd]

    def secrets(self):
        """Each repo secret set through `gh secret set`: its name -> its value.

        The value is taken from --body or, failing that, standard input."""
        out = {}
        for c in self.calls("gh"):
            a = c["argv"]
            if a[:2] != ["secret", "set"] or len(a) < 3:
                continue
            value = c["stdin"]
            for i, x in enumerate(a):
                if x in ("--body", "-b") and i + 1 < len(a):
                    value = a[i + 1]
                elif x.startswith("--body="):
                    value = x.partition("=")[2]
            out[a[2]] = value
        return out

    def settings(self):
        """The settings file read as nested maps, or None when setup wrote none."""
        p = self.repo / ".dokima" / "agents.yml"
        return read_yaml(p.read_text()) if p.exists() else None


def read_yaml(text):
    """Read the small YAML subset the settings file uses, into nested maps.

    Handles nested block maps, plain or quoted scalars and `{a: b, c: d}` flow maps, so either way of writing a
    subscription is read alike."""
    def scalar(v):
        v = v.strip()
        return v[1:-1] if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"" else v

    def value(v):
        v = v.strip()
        if v.startswith("{") and v.endswith("}"):
            return {scalar(k): scalar(x) for k, _, x in
                    (part.partition(":") for part in v[1:-1].split(",") if part.strip())}
        return scalar(v)

    root, stack = {}, [(-1, None)]
    stack[0] = (-1, root)
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, rest = line.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if rest.strip():
            parent[scalar(key)] = value(rest)
        else:
            parent[scalar(key)] = {}
            stack.append((indent, parent[scalar(key)]))
    return root


def add_with_key(box, *extra, stdin=KEY + "\n", **env):
    """Add a Codex subscription by key, for the worker and the reviewer."""
    return box.run("add", "codex-pro", "--agent", "codex", "--secret", "CODEX_KEY", "--model", "gpt-5-codex",
                   "--role", "worker", "--role", "reviewer", "--key", *extra, stdin=stdin, **env)


def add_with_sign_in(box, **env):
    """Add a Kimi subscription signed in with region cn, for the planner."""
    return box.run("add", "kimi-max", "--agent", "kimi", "--secret", "KIMI_SIGN_IN", "--model", "kimi-for-coding",
                   "--role", "planner", "--sign-in", "--region", "cn", **env)


def said(p):
    """The command's output and errors, for failure messages."""
    return f"exit {p.returncode}\nstdout: {p.stdout}\nstderr: {p.stderr}"


def test_lists_inputs(tmp_path, record_property):
    """Setup names every input a subscription needs: membership, region, sign-in or key, and model.

    Runs `python3 -m dokima.setup needs` and checks it ends well and names each of the four inputs. Proves 697.1."""
    record_property("proves", "697.1")
    box = Box(tmp_path)
    p = box.run("needs")
    assert p.returncode == 0, f"697.1: setup could not list the inputs a subscription needs.\n{said(p)}"
    out = p.stdout.lower()
    for word in ("membership", "region", "sign-in", "key", "model"):
        assert word in out, f"697.1: setup's list of inputs leaves out {word!r}.\n{said(p)}"


def test_key_stored_as_secret(tmp_path, record_property):
    """A key the owner gives is saved as a repo secret under the chosen name.

    Pipes a key into setup and checks the stub `gh` was asked to set the secret CODEX_KEY to exactly that key.
    Proves 697.2."""
    record_property("proves", "697.2")
    box = Box(tmp_path)
    p = add_with_key(box)
    assert p.returncode == 0, f"697.2: setup failed while storing a key.\n{said(p)}"
    secrets = box.secrets()
    assert "CODEX_KEY" in secrets, f"697.2: setup never set the repo secret CODEX_KEY; gh calls: {box.calls('gh')}"
    assert secrets["CODEX_KEY"].strip() == KEY, \
        f"697.2: the repo secret CODEX_KEY holds {secrets['CODEX_KEY']!r}, not the key the owner gave."


def test_empty_key_stores_nothing(tmp_path, record_property):
    """An empty key is refused: setup fails and stores no secret.

    First checks a real key is stored, so the refusal is setup's own; then pipes nothing into a fresh setup and checks
    it exits with an error and never asks `gh` to set a secret. Proves 697.2."""
    record_property("proves", "697.2")
    good = Box(tmp_path / "good")
    add_with_key(good)
    assert good.secrets(), "697.2: setup stores no secret even for a real key."
    box = Box(tmp_path / "empty")
    p = add_with_key(box, stdin="")
    assert p.returncode != 0, f"697.2: setup accepted an empty key.\n{said(p)}"
    assert not box.secrets(), f"697.2: setup stored a secret from an empty key: {box.secrets()}"


def test_secret_refused_fails(tmp_path, record_property):
    """When GitHub refuses the secret, setup fails and names the secret it could not store.

    The stub `gh` answers 403; checks setup exits with an error whose output names CODEX_KEY. Proves 697.2."""
    record_property("proves", "697.2")
    box = Box(tmp_path)
    p = add_with_key(box, GH_FAIL="1")
    assert box.calls("gh"), f"697.2: setup never tried to store the key with gh.\n{said(p)}"
    assert p.returncode != 0, f"697.2: setup ended well though GitHub refused the secret.\n{said(p)}"
    assert "CODEX_KEY" in p.stdout + p.stderr, f"697.2: setup's failure does not name the secret CODEX_KEY.\n{said(p)}"


def test_settings_name_key_secret(tmp_path, record_property):
    """The settings file names the subscription's agent and secret, never the key.

    Adds a subscription with a key and checks `.dokima/agents.yml` has codex-pro with agent codex and key CODEX_KEY,
    and that the key itself is nowhere in the file. Proves 697.3."""
    record_property("proves", "697.3")
    box = Box(tmp_path)
    p = add_with_key(box)
    s = box.settings()
    assert s is not None, f"697.3: setup wrote no .dokima/agents.yml.\n{said(p)}"
    sub = (s.get("subscriptions") or {}).get("codex-pro")
    assert sub == {"agent": "codex", "key": "CODEX_KEY"}, \
        f"697.3: the settings file lists the subscription as {sub!r}, not agent codex with key CODEX_KEY."
    assert KEY not in (box.repo / ".dokima" / "agents.yml").read_text(), \
        "697.3: the settings file holds the key itself, not just its secret's name."


def test_settings_keep_other_subscription(tmp_path, record_property):
    """Adding a second subscription keeps the first one in the settings file.

    Adds Kimi by sign-in, then Codex by key, and checks both subscriptions are there with their agents and secrets.
    Proves 697.3."""
    record_property("proves", "697.3")
    box = Box(tmp_path)
    first = add_with_sign_in(box)
    assert first.returncode == 0, f"697.3: adding the first subscription failed.\n{said(first)}"
    p = add_with_key(box)
    assert p.returncode == 0, f"697.3: adding a second subscription failed.\n{said(p)}"
    s = box.settings() or {}
    subs = s.get("subscriptions") or {}
    assert subs.get("kimi-max") == {"agent": "kimi", "key": "KIMI_SIGN_IN"}, \
        f"697.3: adding Codex dropped or changed the Kimi subscription: {subs!r}"
    assert subs.get("codex-pro") == {"agent": "codex", "key": "CODEX_KEY"}, \
        f"697.3: the Codex subscription is missing or wrong: {subs!r}"


def test_sign_in_uses_region(tmp_path, record_property):
    """Setup signs the agent in through its own login, with the region the owner gave.

    Adds a Kimi subscription with region cn and checks the stub `kimi` was run as `kimi login --region cn`.
    Proves 697.4."""
    record_property("proves", "697.4")
    box = Box(tmp_path)
    p = add_with_sign_in(box)
    logins = [c["argv"] for c in box.calls("kimi")]
    assert ["login", "--region", "cn"] in logins, \
        f"697.4: setup never ran `kimi login --region cn`; kimi calls: {logins}\n{said(p)}"


def test_sign_in_stored_as_secret(tmp_path, record_property):
    """The files Kimi's login saved are stored as one repo secret.

    After the stub login saves its files, checks the secret KIMI_SIGN_IN unpacks (base64, gzip tar) into those same
    files with the same content, named by their path under the home folder. Proves 697.5."""
    record_property("proves", "697.5")
    box = Box(tmp_path)
    p = add_with_sign_in(box)
    assert p.returncode == 0, f"697.5: setup failed while signing in.\n{said(p)}"
    secrets = box.secrets()
    assert "KIMI_SIGN_IN" in secrets, \
        f"697.5: setup never stored the sign-in as the repo secret KIMI_SIGN_IN; gh calls: {box.calls('gh')}"
    try:
        raw = base64.b64decode(secrets["KIMI_SIGN_IN"].strip(), validate=True)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
            files = {m.name.removeprefix("./"): t.extractfile(m).read().decode() for m in t.getmembers() if m.isfile()}
    except Exception as e:  # noqa: BLE001 - any unreadable secret is this criterion's failure
        raise AssertionError(f"697.5: the stored sign-in is not base64 of a gzip tar: {e}") from e
    want = {".kimi/credentials/kimi-code.json": '{"access_token": "tok-123"}',
            ".kimi/config.toml": 'default_model = "kimi-for-coding"\n'}
    for name, content in want.items():
        assert files.get(name) == content, \
            f"697.5: the stored sign-in lacks {name} as Kimi's login saved it; it holds {sorted(files)}"


def test_failed_sign_in_stores_nothing(tmp_path, record_property):
    """When the login fails, setup fails and stores no sign-in.

    The stub login exits with an error; checks setup exits with an error and never asks `gh` to set a secret.
    Proves 697.5."""
    record_property("proves", "697.5")
    box = Box(tmp_path)
    p = add_with_sign_in(box, KIMI_FAIL="1")
    assert box.calls("kimi"), f"697.5: setup never ran Kimi's login.\n{said(p)}"
    assert p.returncode != 0, f"697.5: setup ended well though the login failed.\n{said(p)}"
    assert not box.secrets(), f"697.5: setup stored a secret after a failed login: {box.secrets()}"


def test_settings_give_roles(tmp_path, record_property):
    """The settings file gives each named role the owner's subscription and model.

    Adds Codex for the worker and the reviewer and checks both roles name codex-pro with model gpt-5-codex.
    Proves 697.6."""
    record_property("proves", "697.6")
    box = Box(tmp_path)
    p = add_with_key(box)
    s = box.settings()
    assert s is not None, f"697.6: setup wrote no .dokima/agents.yml.\n{said(p)}"
    roles = s.get("roles") or {}
    for role in ("worker", "reviewer"):
        assert roles.get(role) == {"subscription": "codex-pro", "model": "gpt-5-codex"}, \
            f"697.6: the settings file gives the {role} {roles.get(role)!r}, not codex-pro with gpt-5-codex."


def test_settings_keep_other_roles(tmp_path, record_property):
    """Adding a second subscription keeps the roles given to the first one.

    Adds Kimi for the planner by sign-in, then Codex for the worker and the reviewer by key, and checks the planner
    still names kimi-max with model kimi-for-coding. Proves 697.6."""
    record_property("proves", "697.6")
    box = Box(tmp_path)
    first = add_with_sign_in(box)
    assert first.returncode == 0, f"697.6: adding the first subscription failed.\n{said(first)}"
    p = add_with_key(box)
    assert p.returncode == 0, f"697.6: adding a second subscription failed.\n{said(p)}"
    roles = (box.settings() or {}).get("roles") or {}
    assert roles.get("planner") == {"subscription": "kimi-max", "model": "kimi-for-coding"}, \
        f"697.6: adding Codex dropped or changed the planner's role: {roles!r}"

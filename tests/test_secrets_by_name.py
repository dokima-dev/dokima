"""Tests for #894, #897: each secret shared jobs read reaches them in adopters' repos.

A reusable workflow in another account's repo gets only the secrets it declares under `on.workflow_call.secrets`,
each mapped by name by its caller; `secrets: inherit` carries none across. So `entry.yml` declares every secret a
shared job reads and passes them on, and the install file maps each by name instead of inheriting.
"""
import glob
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
ENTRY = os.path.join(WORKFLOWS, "entry.yml")
INSTALL = os.path.join(ROOT, "dokima", "install", "dokima.yml")
OWN = ("playthrough.yml", "wiki.yml")
# `secrets.NAME`, and the name a `secrets[...]` lookup falls back to.
READS = re.compile(r"secrets\.([A-Za-z_][A-Za-z0-9_]*)|secrets\[[^\]]*'([A-Za-z_][A-Za-z0-9_]*)'\s*\]")


def load(path):
    """The workflow at PATH, with `on` kept as a name."""
    data = yaml.safe_load(open(path).read()) or {}
    if True in data:
        data["on"] = data.pop(True)
    return data


def read_secrets(text):
    """The secret names TEXT reads."""
    return {a or b for a, b in READS.findall(text)}


def shared_reads():
    """Each secret a shared workflow's job reads, with the workflows reading it."""
    found = {}
    for path in sorted(glob.glob(os.path.join(WORKFLOWS, "*.yml"))):
        name = os.path.basename(path)
        if name in OWN or name == "entry.yml":
            continue
        # A job's `secrets:` passing them on to an inner workflow (#897) reads none itself.
        text = re.sub(r"(?m)^    secrets: \{.*$", "", open(path).read())
        for s in read_secrets(text):
            found.setdefault(s, []).append(name)
    return found


def declared(entry):
    """The secrets ENTRY declares it takes."""
    call = (entry.get("on") or {}).get("workflow_call") or {}
    return set(call.get("secrets") or {})


def mapped(install):
    """The secrets the install file hands Dokima, each from its same-named repo secret."""
    names = set()
    for job in (install.get("jobs") or {}).values():
        given = job.get("secrets")
        if isinstance(given, dict):
            names |= {k for k, v in given.items() if str(v).replace(" ", "") == "${{secrets.%s}}" % k}
    return names


def test_the_reader_finds_both_forms():
    """The reader finds a named read and a lookup's fallback, and nothing elsewhere."""
    text = "a: ${{ secrets.DOKIMA_APP_KEY }}\nb: ${{ secrets[env.AGENT_KEY || 'CLAUDE_CODE_OAUTH_TOKEN'] }}\n"
    assert read_secrets(text) == {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN"}
    assert read_secrets("run: echo ${{ vars.DOKIMA_APP_ID }}\n") == set()


def test_entry_declares_every_secret_a_shared_job_reads():
    """`entry.yml` declares each secret a shared job reads, the app key required, the others optional."""
    reads = shared_reads()
    assert "DOKIMA_APP_KEY" in reads and "CLAUDE_CODE_OAUTH_TOKEN" in reads, f"894: shared jobs read only {reads}"
    secrets = (load(ENTRY)["on"]["workflow_call"] or {}).get("secrets") or {}
    missing = {s: w for s, w in reads.items() if s not in secrets}
    assert not missing, f"894: entry.yml does not declare secrets shared jobs read: {missing}"
    assert secrets["DOKIMA_APP_KEY"].get("required") is True, "894: entry.yml does not require DOKIMA_APP_KEY"
    optional = [s for s in secrets if s != "DOKIMA_APP_KEY" and secrets[s].get("required")]
    assert not optional, f"894: entry.yml requires agent keys that should be optional: {optional}"


def inner_calls(path):
    """Each job at PATH calling a workflow here: name, target and secrets given."""
    return [(n, os.path.basename(j["uses"]), j.get("secrets"))
            for n, j in (load(path).get("jobs") or {}).items() if str(j.get("uses", "")).startswith("./.github/workflows/")]


def call_faults(path):
    """Each way the calls in the workflow at PATH drop a secret (#897).

    `inherit`, a secret the target does not declare, or one the target reads that is not passed by name."""
    faults = []
    for job, target, given in inner_calls(path):
        if given == "inherit":
            faults.append(f"{job} says `secrets: inherit`")
            continue
        given = given or {}
        takes = declared(load(os.path.join(WORKFLOWS, target)))
        if set(given) - takes:
            faults.append(f"{job} passes {sorted(set(given) - takes)}, which {target} does not declare")
        reads = read_secrets(open(os.path.join(WORKFLOWS, target)).read())
        if reads - takes:
            faults.append(f"{target} reads {sorted(reads - takes)} without declaring them")
        unmapped = [s for s in takes if str(given.get(s, "")).replace(" ", "") != "${{secrets.%s}}" % s]
        if unmapped:
            faults.append(f"{job} does not pass {sorted(unmapped)} to {target} by name")
    return faults


def test_entry_passes_secrets_by_name_to_every_inner_workflow():
    """No `entry.yml` call inherits; each passes by name exactly what its target declares."""
    calls = inner_calls(ENTRY)
    assert any(t == "uptodate.yml" for _, t, _ in calls), f"897: entry.yml calls only {calls}"
    faults = call_faults(ENTRY)
    assert not faults, f"897: entry.yml's inner calls drop secrets: {faults}"


def test_inner_workflows_pass_secrets_by_name_too():
    """A shared workflow calling another, as `commands.yml` calls `agent.yml`, passes its secrets by name too."""
    faults = {os.path.basename(p): f for p in sorted(glob.glob(os.path.join(WORKFLOWS, "*.yml")))
              if os.path.basename(p) not in OWN and (f := call_faults(p))}
    assert not faults, f"897: shared workflows' inner calls drop secrets: {faults}"


def test_a_dropped_inner_secret_is_caught(tmp_path, monkeypatch):
    """Inherit, an undeclared secret or a missing one is caught; passing by name passes."""
    monkeypatch.setattr(__import__(__name__), "WORKFLOWS", str(tmp_path))
    (tmp_path / "inner.yml").write_text(
        "on:\n  workflow_call:\n    secrets:\n      DOKIMA_APP_KEY: {required: true}\n"
        "jobs:\n  a:\n    steps:\n      - run: echo ${{ secrets.DOKIMA_APP_KEY }}\n")
    caller = tmp_path / "caller.yml"
    def faults(given):
        caller.write_text("jobs:\n  x:\n    uses: ./.github/workflows/inner.yml\n    secrets: " + given + "\n")
        return call_faults(str(caller))
    assert faults("inherit") == ["x says `secrets: inherit`"]
    assert "x passes ['KIMI_API_KEY'], which inner.yml does not declare" in faults(
        '{DOKIMA_APP_KEY: "${{ secrets.DOKIMA_APP_KEY }}", KIMI_API_KEY: "${{ secrets.KIMI_API_KEY }}"}')
    assert faults("{}") == ["x does not pass ['DOKIMA_APP_KEY'] to inner.yml by name"]
    assert faults('{DOKIMA_APP_KEY: "${{ secrets.DOKIMA_APP_KEY }}"}') == []


def test_install_maps_every_secret_by_name():
    """The install file maps each secret a shared job reads by name, and never inherits."""
    install = load(INSTALL)
    inherit = [n for n, j in install["jobs"].items() if j.get("secrets") == "inherit"]
    assert not inherit, f"894: the install file still uses `secrets: inherit` in {inherit}"
    missing = set(shared_reads()) - mapped(install)
    assert not missing, f"894: the install file does not map {sorted(missing)} by name"
    undeclared = mapped(install) - declared(load(ENTRY))
    assert not undeclared, f"894: the install file maps {sorted(undeclared)}, which entry.yml does not declare"


def test_a_missing_mapping_is_caught():
    """Mapping only the app key misses Claude Code's token; mapping both passes."""
    one = {"jobs": {"dokima": {"secrets": {"DOKIMA_APP_KEY": "${{ secrets.DOKIMA_APP_KEY }}"}}}}
    assert {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN"} - mapped(one) == {"CLAUDE_CODE_OAUTH_TOKEN"}
    one["jobs"]["dokima"]["secrets"]["CLAUDE_CODE_OAUTH_TOKEN"] = "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
    assert {"DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN"} - mapped(one) == set()

"""Tests for #894: every secret Dokima's shared jobs read reaches them from an adopter's repo.

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
        for s in read_secrets(open(path).read()):
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


def test_entry_passes_secrets_to_every_shared_workflow_reading_one():
    """Each `entry.yml` job calling a shared workflow that reads a secret passes the secrets on."""
    reading = {w for ws in shared_reads().values() for w in ws}
    jobs = load(ENTRY)["jobs"]
    dropped = [n for n, j in jobs.items()
               if os.path.basename(j.get("uses", "")) in reading and j.get("secrets") != "inherit"]
    assert not dropped, f"894: entry.yml jobs call workflows reading secrets without passing them: {dropped}"


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

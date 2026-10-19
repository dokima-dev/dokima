"""Tests for #876: Dokima's keys are repo secrets, and the audit checks they are there.

With the thin install, Dokima's jobs run from Dokima's own repo, so a secret kept only in the adopter's `keys`
environment never reaches them; a repo secret does. The audit reads the names of the repo's own secrets (never their
values) and reports each key Dokima's jobs need that is missing. The install docs say to add the keys as repo secrets.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from test_audit import FORBIDDEN, REPO, GitHub, audit  # noqa: E402


def secret_lines(lines):
    return [l for l in lines if "secret" in l.lower()]


def test_a_key_missing_from_the_repo_secrets_is_reported(record_property, tmp_path):
    """The audit names each missing repo secret, and says nothing when both keys are there."""
    record_property("proves", "876")
    a = audit("876")
    g = GitHub()
    assert secret_lines(a.compare(g, REPO, root=str(tmp_path))) == [], "876: both keys are repo secrets, yet reported"
    g.secret_names = {"DOKIMA_APP_KEY"}
    lines = secret_lines(a.compare(g, REPO, root=str(tmp_path)))
    assert len(lines) == 1 and "`CLAUDE_CODE_OAUTH_TOKEN`" in lines[0] and "repo secret" in lines[0], \
        f"876: the missing agent key is not reported as a missing repo secret: {lines}"
    g.secret_names = set()
    lines = secret_lines(a.compare(g, REPO, root=str(tmp_path)))
    assert any("`DOKIMA_APP_KEY`" in l for l in lines), f"876: the missing app key is not reported: {lines}"


def test_the_audit_checks_the_key_the_settings_name(record_property, tmp_path):
    """A role whose settings name another secret needs that one as a repo secret."""
    record_property("proves", "876")
    a = audit("876")
    os.makedirs(tmp_path / ".dokima")
    (tmp_path / ".dokima" / "settings.yaml").write_text(
        "agents:\n  subscriptions:\n    mine:\n      agent: claude\n      key: MY_KEY\n"
        "  roles:\n    worker:\n      subscription: mine\n      model: claude-opus-5-5\n")
    lines = secret_lines(a.compare(GitHub(), REPO, root=str(tmp_path)))
    assert len(lines) == 1 and "`MY_KEY`" in lines[0], f"876: the worker's own key MY_KEY is not checked: {lines}"


def test_unreadable_repo_secrets_say_why(record_property, tmp_path):
    """When GitHub refuses to list the repo secrets, the audit says so with GitHub's reason."""
    record_property("proves", "876")
    a = audit("876")
    lines = secret_lines(a.compare(GitHub(fail={"secrets": FORBIDDEN}), REPO, root=str(tmp_path)))
    assert any("could not be verified" in l and "HTTP 403" in l for l in lines), \
        f"876: a refused secrets read is not reported with GitHub's reason: {lines}"


def test_the_install_docs_say_repo_secrets_not_the_keys_environment(record_property):
    """The README and the install page tell adopters to add the keys as repo secrets."""
    record_property("proves", "876")
    for path in ("README.md", os.path.join("docs", "wiki", "Installing.md")):
        text = open(os.path.join(ROOT, path)).read()
        assert not re.search(r"environment\W+named `keys`", text), f"876: {path} still says to use the keys environment"
        assert "repo secret" in text or "**repo** secrets" in text, f"876: {path} does not say to use repo secrets"

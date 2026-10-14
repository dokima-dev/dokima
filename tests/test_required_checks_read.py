"""Dokima reads which checks main requires from the branch itself, so its app needs no admin rights to merge."""
import json

from dokima import agent
from dokima import agent_github  # noqa: E402


def test_required_checks_come_from_the_branch_when_the_protection_endpoint_refuses(monkeypatch):
    """The app's token reads the branch's rule from the branch; the admin-only protection endpoint is never needed.

    Verified by: a fake GitHub that answers the branch with its rule and refuses the protection endpoint with the
    403 GitHub gave Dokima's app on #576."""
    calls = []

    def gh(*args):
        calls.append(args[1])
        if args[1].endswith("/protection/required_status_checks"):
            raise AssertionError("Resource not accessible by integration (HTTP 403)")
        return json.dumps({"name": "main", "protection": {"required_status_checks": {
            "contexts": ["all tests", "Acceptance criteria"],
            "checks": [{"context": "all tests"}, {"context": "Acceptance criteria"}]}}})

    monkeypatch.setattr(agent_github, "gh", gh)
    assert agent.required_checks("o/r") == {"all tests", "Acceptance criteria"}
    assert calls == ["repos/o/r/branches/main"]

"""Patches one name of the agent code in every job file that holds it.

For tests that fake a record, the bot or the conversation.

Since #636 the agent code is split into job files (`dokima/agent_*.py`) that `dokima.agent` re-exports, so a name
patched on `dokima.agent` alone no longer reaches a job file that holds its own copy. `patch_agent` sets the name on
`dokima.agent` and on every loaded agent job file that holds it. GitHub itself is faked in one place instead, on
`dokima.agent_github.gh`.
"""
import sys


def patch_agent(monkeypatch, name, value):
    """Sets the name on the agent module and on every agent job file holding it."""
    for key, mod in sorted(sys.modules.items()):
        if (key == "dokima.agent" or key.startswith("dokima.agent_")) and mod is not None and hasattr(mod, name):
            monkeypatch.setattr(mod, name, value)

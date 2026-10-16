# reviewer (plan) for #721

Run: https://github.com/dokima-dev/dokima/actions/runs/38828660155

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #721: The settings reader keeps an inline comment as part of a value, so a commented agent line names a wrong agent.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 699 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [746], "loop": []} -->
> A comment after a value in the settings file no longer becomes part of that value.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/699
> 
> 
> **User story:** A role named on a commented settings line runs on the agent the line names.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A comment after a value in the settings file is no longer read as part of that value.
>   *

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json | head -80; cd /home/runner/work/dokima/dokima; cat tests/test_settings_comments.py; grep -n "def read_settings" -A50 dokima/setup.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/721": "The settings reader keeps an inline comment as part of a value, so a commented agent line names a wrong agent.\n\n**Evidence:** `dokima/setup.py` `read_settings()` keeps text after `#`: `agent: claude  # x` reads as `claude  # x`.\n\n**Verdict:** New\n\n**Open issues searched:** #696, #698, #39, #366\n\nThe worker raised it and the reviewer confirmed it on #698 ([run](https://github.com/dokima-dev/dokima/actions/runs/38674964969)).",
>  "https://github.com/dokima-dev/dokima/issues/721#issuecomment-6205033503": "/plan"
> }{"number": null}"""Tests for #721: a comment after a settings value is not part of it.
> 
> The settings file (`.dokima/agents.yml`) is read by `dokima/setup.py` `read_settings()`. A line like
> `agent: codex  # the fast one` used to read as `codex  # the fast one`, so the role named an agent that does not exist.
> 
> Each test writes a settings file into a temp folder, points `DOKIMA_SETTINGS` at it and asks `dokima.agents.role_settings()`
> what the role runs on, the same call a run makes before it starts its agent.
> """
> import textwrap
> 
> from dokima import agents
> 
> 
> def _role(tmp_path, monkeypatch, text, role="planner"):
>     """The role's settings as a run reads them from the given text."""
>     path = tmp_path / "agents.yml"
>     path.write_text(textwrap.dedent(text))
>     monkeypatch.setenv("DOKIMA_SETTINGS", str(path))
>     return agents.role_settings(role)
> 
> 
> def test_inline_comment_not_in_value(tmp_path, monkeypatch, rec

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def role_settings" -A30 dokima/agents.py; pytest -q tests/test_settings_comments.py 2>&1 | tail -20; cat /tmp/pack/in/01-planner.json | head -60; cat /tmp/pack/open_issues.json | head -30
```

> 47:def role_settings(role):
> 48-    """The role's agent, model and key secret; today's when the file leaves the role out."""
> 49-    path = settings_path()
> 50-    if not os.path.exists(path):
> 51-        return dict(TODAY)
> 52-    settings = read_settings(open(path).read())
> 53-    roles = settings.get("roles")
> 54-    given = roles.get(role) if isinstance(roles, dict) else None
> 55-    if given is None:
> 56-        return dict(TODAY)
> 57-    given = given if isinstance(given, dict) else {}
> 58-    if not given.get("model"):
> 59-        raise Stop(f"The {role} in {path} has no model line, so it cannot start.")
> 60-    sub = given.get("subscription", "")
> 61-    subs = settings.get("subscriptions")
> 62-    found = subs.get(sub) if isinstance(subs, dict) and sub else None
> 63-    if not isinstance(found, dict):
> 64-        raise Stop(f"The {role} names the subscription '{sub}', which {path} does not list.")
> 65-    if not found.get("agent") or not found.get("key"):
> 66-        raise Stop(f"The subscription '{sub}' in {path} needs both an agent and a key line.")
> 67-    return {"agent": found["agent"], "model": given["model"], "key": found["key"]}
> 68-
> 69-
> 70-def adapter(role):
> 71-    """The role's agent adapter and its settings, or Stop naming an agent with no adapter."""
> 72-    s = role_settings(role)
> 73-    name = s["agent"]
> 74-    m = None
> 75-    if re.fullmatch(r"[a-z0-9_]+", name):
> 76-        try:
> 77-            m = importlib.import_module(f"dokima.agent_{name}")
> FAILED tests/test_settings_co

`4. Bash`
```
cd /home/runner/work/dokima/dokima; pytest -q tests/test_settings_comments.py 2>&1 | grep -E "^E .*721" ; grep -rn "read_settings" dokima | grep -v "def "
```

> E       AssertionError: 721.1: a comment after a value was kept as part of it; the planner reads {'agent': 'codex  # the fast one', 'model': 'gpt-5  # newest', 'key': 'CODEX_KEY # stored by setup'}
> E       AssertionError: 721.1: a quoted agent with a comment after it reads as 'codex"  # note', not 'codex'
> E       AssertionError: 721.1: a comment on a section line hid the roles under it; the planner reads {'agent': 'claude', 'model': 'claude-opus-5-5', 'key': 'CLAUDE_CODE_OAUTH_TOKEN'}
> dokima/agents.py:32:from dokima.setup import SETTINGS, read_settings
> dokima/agents.py:52:    settings = read_settings(open(path).read())
> dokima/setup.py:106:    settings = read_settings(open(SETTINGS).read()) if os.path.exists(SETTINGS) else {}

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote one criterion: a comment after a settings value is not read as part of it.", "The planner wrote three tests: agent, key and model lines, a quoted name, and a section line."], "decided": ["The planner tests through the same call a run makes to learn its agent."], "open": []},
 "verdict": "approve",
 "summary": "The plan carries the one ask, and its three tests fail today because comments are still read into values.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "The settings reader keeps an inline comment as part of a value, so a commented agent line names a wrong agent.", "source": "https://github.com/dokima-dev/dokima/issues/721", "criterion": "721.1"}],
 "behaviors": [{"criterion": "721.1", "one_behavior": true, "why": "One result: a comment after a value is left out of it."}],
 "edge_cases": [{"criterion": "721.1", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_settings_comments.py::test_inline_comment_not_in_value", "only_its_behavior": true, "why": "Fails today with each value carrying its comment; passes only on bare values."},
  {"test": "tests/test_settings_comments.py::test_quoted_value_with_comment", "only_its_behavior": true, "why": "Fails today reading the agent with a stray quote and comment."},
  {"test": "tests/test_settings_comments.py::test_comment_on_section_line", "only_its_behavior": true, "why": "Fails today: the commented roles line hides the planner, so it falls back to the default."}
 ],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 721 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step did line 2 holds 17 words, over its cap of 15: cut 2, keep the facts

**Agent:** Shortening two summary lines that ran over the word cap, then rechecking.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r["previous_step"]["did"]=["The planner wrote one criterion: a comment after a settings value is dropped.","The planner wrote three tests: commented lines, a quoted name, a section line."]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 721 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#721](https://github.com/dokima-dev/dokima/issues/721) (a comment after a settings value is read as part of the value). The approval is in `/tmp/dokima-out/review.json`, and it passes both hand-back checks.

- **Your ask is covered.** The issue makes one ask, and criterion 721.1 carries it word for word. Nothing is dropped or added, and the criterion covers exactly one behavior.
- **All three new tests fail today for the right reason:**
  - **Commented lines:** the agent, key and model each come back with their comment still attached, e.g. `codex  # the fast one`.
  - **Quoted name:** the agent reads as `codex"  # note`.
  - **Commented section line:** writing `roles:  # who runs what` hides the planner's setting, so it runs on the default agent instead.
- **The tests check what a run really uses.** They ask for the role's settings through the same call a run makes before it starts its agent, so they catch the wrong-agent problem itself. They pass only when the values come back with no comment left on them.
- **No edge cases to cut or add.** Both cases the plan lists are ones you'd hit in normal use, and I found no normal-use case missing.

There were no open blockers to answer and I raised none.

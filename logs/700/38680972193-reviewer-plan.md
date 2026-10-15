# reviewer (plan) for #700

Run: https://github.com/dokima-dev/dokima/actions/runs/38680972193

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #700: A role can run on Codex CLI
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 697, 698, 699 -->
> <!-- dokima-blocking: {"blocked_by": [698, 699], "blocks": [], "loop": []} -->
> Any role named for a Codex subscription runs in Codex CLI, on the model the settings file gives.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/698
> - https://github.com/dokima-dev/dokima/issues/699
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/39
> - https://github.com/dokima-dev/dokima/issues/697
> 
> 
> **User story:** The owner moves any role to Codex by naming a Codex subscription for it.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-700/tests/test_agent_codex.py#L92"><img src="ht

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/01-planner.json | head -c 6000; echo; cat tests/test_agent_codex.py; ls dokima | grep -i agent; git show --stat HEAD | head -30
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38680691282",
>  "commit_before": "f71d144d2bd98ab2068596b1eb49ecf40534e27a",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 143059,
>   "turns": 14,
>   "cost_usd": 0.5871114000000001,
>   "tokens_in": 529446,
>   "tokens_out": 8166
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/700/38680691282-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38680691282",
>  "handback": {
>   "kind": "user_story",
>   "title": "A role can run on Codex CLI",
>   "summary": "Any role named for a Codex subscription runs in Codex CLI, on the model the settings file gives.",
>   "user_story": "The owner moves any role to Codex by naming a Codex subscription for it.",
>   "acceptance_criteria": [
>    {
>     "text": "A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.",
>     "words": "Codex in Codex CLI",
>     "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>     "files": [
>      "dokima/agent_codex.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "Codex fails, so the run fails with its exit code.",
>       "test": "tests/test_agent_codex.py::test_a_failed_codex_run_fails_the_run"
>      },
>      {
>       "case": "Codex starts read-only unless told, so a worker could not build.",
>       "test": "tests/test_agent_codex.py::test_a_codex_run_may_change_files"
>      }
>     ]
>    }
>   ],
>   "non_functional": [],
>   "tests":

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/agent_kimi.py | head -250; ls tests | grep -i -E "kimi|agent"
```

> """Kimi Code CLI behind the one agent interface (dokima/agents.py) (#699).
> 
> It installs Kimi's command line, puts the stored sign-in back under the home folder, starts with the owner's tested
> command `kimi -p PROMPT --output-format stream-json` and the role's model, and keeps the stream as `kimi.jsonl` in the
> run's folder, where its models and transcript are read from.
> 
> The run's key arrives in DOKIMA_AGENT_KEY: what `python3 -m dokima.setup add ... --sign-in` stored, the base64 text of
> a gzip tar of the files Kimi's login saved, each named by its path under the home folder.
> """
> import base64
> import binascii
> import io
> import json
> import os
> import subprocess
> import sys
> import tarfile
> 
> from dokima.agent_records import scrub
> 
> STREAM = "kimi.jsonl"
> MODEL = "kimi-model.txt"
> 
> 
> def install():
>     """Install Kimi Code CLI; return the install's exit code."""
>     return subprocess.run(["uv", "tool", "install", "--python", "3.13", "kimi-cli"]).returncode
> 
> 
> def restore_sign_in(key):
>     """Unpack the stored sign-in KEY into the home folder; False, saying why, when it cannot."""
>     try:
>         data = base64.b64decode(key, validate=True)
>         with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
>             t.extractall(os.path.expanduser("~"), filter="data")
>     except (binascii.Error, ValueError, tarfile.TarError, OSError) as e:
>         print(f"The stored Kimi sign-in could not be put back, so Kimi was not started: {e}", file=sys.stderr)
>         return False
>     return True

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/01-planner.json | head -c 6000; echo; cat tests/test_agent_codex.py; ls dokima | grep -i agent; git show --stat HEAD | head -30
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/agent_kimi.py | head -250; ls tests | grep -i -E "kimi|agent"
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38680691282",
>  "commit_before": "f71d144d2bd98ab2068596b1eb49ecf40534e27a",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 143059,
>   "turns": 14,
>   "cost_usd": 0.5871114000000001,
>   "tokens_in": 529446,
>   "tokens_out": 8166
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/700/38680691282-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38680691282",
>  "handback": {
>   "kind": "user_story",
>   "title": "A role can run on Codex CLI",
>   "summary": "Any role named for a Codex subscription runs in Codex CLI, on the model the settings file gives.",
>   "user_story": "The owner moves any role to Codex by naming a Codex subscription for it.",
>   "acceptance_criteria": [
>    {
>     "text": "A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.",
>     "words": "Codex in Codex CLI",
>     "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>     "files": [
>      "dokima/agent_codex.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "Codex fails, so the run fails with its exit code.",
>       "test": "tests/test_agent_codex.py::test_a_failed_codex_run_fails_the_run"
>      },
>      {
>       "case": "Codex starts read-only unless told, so a worker could not build.",
>       "test": "tests/test_agent_codex.py::test_a_codex_run_may_change_files"
>      }
>     ]
>    }
>   ],
>   "non_functional": [],
>   "tests":

> """Kimi Code CLI behind the one agent interface (dokima/agents.py) (#699).
> 
> It installs Kimi's command line, puts the stored sign-in back under the home folder, starts with the owner's tested
> command `kimi -p PROMPT --output-format stream-json` and the role's model, and keeps the stream as `kimi.jsonl` in the
> run's folder, where its models and transcript are read from.
> 
> The run's key arrives in DOKIMA_AGENT_KEY: what `python3 -m dokima.setup add ... --sign-in` stored, the base64 text of
> a gzip tar of the files Kimi's login saved, each named by its path under the home folder.
> """
> import base64
> import binascii
> import io
> import json
> import os
> import subprocess
> import sys
> import tarfile
> 
> from dokima.agent_records import scrub
> 
> STREAM = "kimi.jsonl"
> MODEL = "kimi-model.txt"
> 
> 
> def install():
>     """Install Kimi Code CLI; return the install's exit code."""
>     return subprocess.run(["uv", "tool", "install", "--python", "3.13", "kimi-cli"]).returncode
> 
> 
> def restore_sign_in(key):
>     """Unpack the stored sign-in KEY into the home folder; False, saying why, when it cannot."""
>     try:
>         data = base64.b64decode(key, validate=True)
>         with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
>             t.extractall(os.path.expanduser("~"), filter="data")
>     except (binascii.Error, ValueError, tarfile.TarError, OSError) as e:
>         print(f"The stored Kimi sign-in could not be put back, so Kimi was not started: {e}", file=sys.stderr)
>         return False
>     return True

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/agents.py | head -150; python -m pytest -q tests/test_agent_codex.py 2>&1 | tail -15; grep -rn "6181290061" --include=*.py --include=*.md . | head
```

> """The one agent interface: each role runs the agent and model the settings name (#698).
> 
> The settings file is `.dokima/agents.yml` under the current folder (or the path in DOKIMA_SETTINGS, where the
> workflow keeps main's copy, so a branch never picks its own agent or secret):
> 
>     subscriptions:
>       SUB:
>         agent: AGENT      # the adapter dokima/agent_AGENT.py runs it
>         key: SECRET       # the repo secret holding the subscription's key or sign-in
>     roles:
>       ROLE:               # planner, worker or reviewer
>         subscription: SUB
>         model: MODEL
> 
> With no file, or for a role the file leaves out, the role runs on Claude Code with today's model and secret. There is
> no fallback: a bad name stops the run before any agent starts, and a failed agent fails it. Any model name passes;
> the agent itself refuses one it lacks.
> 
>     python3 -m dokima.agents model ROLE
>     python3 -m dokima.agents key ROLE
>     python3 -m dokima.agents install ROLE
>     python3 -m dokima.agents run ROLE PROMPT_FILE OUT
> 
> An agent's adapter is the module dokima.agent_AGENT, offering install(), run(prompt, model, out), models(out, log_dir),
> report(out) and transcript(log_dir, secrets). Claude Code's is dokima/agent_claude.py.
> """
> import importlib
> import os
> import re
> import sys
> 
> from dokima.setup import SETTINGS, read_settings
> 
> TODAY = {"agent": "claude", "model": "claude-opus-5-5", "key": "CLAUDE_CODE_OAUTH_TOKEN"}
> ADAPTER = ("install", "run", "models", "report", "transcript")
> 
> 
> class S

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -i -E "codex|sign.in|sign_in" dokima/setup.py | head -40; grep -rn -i codex rules/ dokima/ --include=*.md --include=*.py | grep -v setup.py | head
```

> 5:A key goes into a repo secret. A sign-in is done once by the agent's own login, with the region the owner gives, and
> 13:    python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE --sign-in --region REGION
> 25:# Per agent: its login command (the region follows it) and where that login saves the sign-in, under the home folder.
> 27:SIGN_IN = {"kimi": [".kimi/credentials", ".kimi/config.toml"]}
> 30:- membership: the plan you pay for, and the agent it runs (for example kimi or codex).
> 31:- region: where the agent's login signs you in (for a sign-in only, for example global).
> 32:- sign-in or key: sign in once through the agent's own login, or give an API key; either is stored as a repo secret.
> 48:def sign_in(agent, region):
> 51:        raise Failed(f"Setup cannot sign in {agent}; it knows {', '.join(sorted(LOGIN))}. Give a key instead.")
> 53:        raise Failed(f"The {agent} login failed, so no sign-in was stored.")
> 55:    saved = [p for p in SIGN_IN[agent] if os.path.exists(os.path.join(home, p))]
> 57:        raise Failed(f"The {agent} login saved none of {', '.join(SIGN_IN[agent])}, so no sign-in was stored.")
> 96:    """Store the key or sign-in as a repo secret, then write the settings file."""
> 103:            raise Failed("A sign-in needs --region, the region the agent's login signs you in to.")
> 104:        value = sign_in(a.agent, a.region)
> 123:    p = sub.add_parser("add", help="store a subscription's key or sign-in and write the settings file")
> 1

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote one criterion: a Codex role runs in Codex CLI on the file's model.",
          "The planner wrote three tests that start a stand-in Codex through the agent interface."],
  "decided": ["A Codex run gets its key, since setup stores Codex by key only.",
              "A Codex run may change files, and a failed Codex run fails the run."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries the one ask, and its three tests fail today because no Codex adapter exists.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "A role on a Codex subscription runs in Codex CLI, with the Codex model the file names.",
           "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
           "criterion": "700.1"}],
 "behaviors": [{"criterion": "700.1", "one_behavior": true, "why": "One action, starting a Codex role, with one result: Codex runs on that model."}],
 "edge_cases": [{"criterion": "700.1", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_agent_codex.py::test_a_codex_role_runs_in_codex_cli_with_its_model", "only_its_behavior": true, "why": "Checks Codex starts once, unattended, with the prompt, the model and the key."},
  {"test": "tests/test_agent_codex.py::test_a_codex_run_may_change_files", "only_its_behavior": true, "why": "Checks Codex starts with write access, which a worker needs to build."},
  {"test": "tests/test_agent_codex.py::test_a_failed_codex_run_fails_the_run", "only_its_behavior": true, "why": "Checks a failing Codex ends the run with its own exit code."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 700 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> rc=1

**Agent:** One summary line is a word over its limit; I'm shortening it and running the check again.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote one criterion: a Codex role runs in Codex CLI on the file.s model./The planner wrote one criterion: a Codex role runs in Codex CLI, on its model./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 700 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#700](https://github.com/dokima-dev/dokima/issues/700) (a role can run on Codex CLI), with no blockers. The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **The ask is covered:** the owner asked that "a role on a Codex subscription runs in Codex CLI, with the Codex model the file names". Criterion 700.1 carries those words exactly.
- **Each test fails today for the right reason:** I ran the three tests in `tests/test_agent_codex.py` and all three fail because Dokima has no Codex adapter yet, not because of a crash or a bad path. Each test runs the real agent interface against a stand-in Codex. Between them they check:
  - Codex starts once, without anyone watching, with the prompt, the model from the settings file and the key.
  - Codex is allowed to change files, which a worker needs to build.
  - A failed Codex run fails the whole run with Codex's own exit code.
- **Choice I checked:** the tests expect the Codex key to be passed in. That matches setup, which can only sign in Kimi and tells Codex users to give a key.

I didn't raise any questions or issues, and there were no open blockers to answer.

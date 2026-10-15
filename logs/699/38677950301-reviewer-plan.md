# reviewer (plan) for #699

Run: https://github.com/dokima-dev/dokima/actions/runs/38677950301

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #699: A role can run on Kimi Code CLI
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 697, 698 -->
> <!-- dokima-blocking: {"blocked_by": [697, 698], "blocks": [700], "loop": []} -->
> Any role named on a Kimi subscription runs in Kimi Code CLI, signed in from the stored sign-in.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/697
> - https://github.com/dokima-dev/dokima/issues/698
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/700
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/696
> - https://github.com/dokima-dev/dokima/issues/39
> - https://github.com/dokima-dev/dokima/issues/706
> - https://github.com/dokima-dev/dokima/issues/721
> 
> 
> **User story:** The owner moves any role to Kimi by naming a Kimi subscription for it, and spends Kimi's credit.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddl

`2. Bash`
```
cd /tmp/pack; cat in/01-planner.json | head -c 6000; echo; cat parent.json | head -c 5000; echo; cd /home/runner/work/dokima/dokima; cat tests/test_agent_kimi.py; ls dokima; git show --stat HEAD
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38677700025",
>  "commit_before": "f6be5b28019051ad9bc8728411fb6527f33e917f",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 115719,
>   "turns": 13,
>   "cost_usd": 0.8197329999999999,
>   "tokens_in": 633490,
>   "tokens_out": 12487
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/699/38677700025-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38677700025",
>  "handback": {
>   "kind": "user_story",
>   "title": "A role can run on Kimi Code CLI",
>   "summary": "Any role named on a Kimi subscription runs in Kimi Code CLI, signed in from the stored sign-in.",
>   "user_story": "The owner moves any role to Kimi by naming a Kimi subscription for it, and spends Kimi's credit.",
>   "acceptance_criteria": [
>    {
>     "text": "A role on a Kimi subscription starts Kimi Code CLI with the Kimi model the settings file names.",
>     "words": "Kimi models in Kimi Code CLI",
>     "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>     "files": [
>      "dokima/agent_kimi.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "Kimi fails: the run fails with Kimi's own exit code.",
>       "test": "tests/test_agent_kimi.py::test_a_failed_kimi_run_fails_the_run"
>      }
>     ]
>    },
>    {
>     "text": "A Kimi run puts the stored sign-in back in place before Kimi starts, so no one signs in again.",
>     "words": "signed in with `kimi login --region 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_agent_kimi.py 2>&1 | tail -30; wc -l dokima/agents.py dokima/setup.py; grep -n "def \|kimi\|agent_\|import" dokima/agents.py | head -60
```

> record_property = <function record_property.<locals>.append_property at 0x7f23addb0fe0>
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_a_kimi_run_writes_the_sto0')
> 
>     def test_a_kimi_run_writes_the_stored_sign_in_back_before_kimi_starts(record_property, tmp_path):
>         """On a fresh machine, Kimi starts already signed in, so no one signs in again.
>     
>         Proves 699.2. Makes the stored sign-in the way setup does, from Kimi's login on the owner's machine. Then starts the planner on
>         a fresh machine whose home has no Kimi folder, with that sign-in as the run's key. When Kimi starts, every file
>         the login saved must already be in the home folder, each the same as on the owner's machine."""
>         record_property("proves", "699.2")
>         box = Box(tmp_path)
>         p = box.run()
>         starts = box.starts()
> >       assert starts, f"699.2: Kimi Code CLI never started: {said(p)}"
> E       AssertionError: 699.2: Kimi Code CLI never started: exit 1; stdout: ''; stderr: "The planner's subscription names the agent 'kimi', which Dokima has no adapter for."
> E       assert []
> 
> tests/test_agent_kimi.py:158: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_agent_kimi.py::test_a_kimi_role_runs_in_kimi_code_cli_with_its_model - AssertionError: 699.1: Kimi Code CLI should start once, it started 0 times: exit 1; stdout: ''; stderr: "The planner's subscription names the agent 'kimi', which Doki

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/agents.py; cat dokima/setup.py; sed -n 1,80p dokima/agent_claude.py
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

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Planned two criteria: a Kimi role starts Kimi with the file's model, and starts signed in.",
   "Wrote three tests that run the real agent interface with a stand-in Kimi."
  ],
  "decided": [
   "A failed Kimi run fails the whole run with Kimi's own exit code."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "The plan carries both asks, each with a test that fails today because no Kimi adapter exists yet.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A role on a Kimi subscription runs in Kimi Code CLI, with the Kimi model the file names.", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "699.1"},
  {"ask": "A Kimi run writes the stored sign-in back before Kimi starts, so no one signs in again.", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "699.2"}
 ],
 "behaviors": [
  {"criterion": "699.1", "one_behavior": true, "why": "One action, starting Kimi, with one result: the file's model."},
  {"criterion": "699.2", "one_behavior": true, "why": "One result: the stored sign-in is in place when Kimi starts."}
 ],
 "edge_cases": [
  {"criterion": "699.1", "cut": [], "missing": []},
  {"criterion": "699.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_agent_kimi.py::test_a_kimi_role_runs_in_kimi_code_cli_with_its_model", "only_its_behavior": true, "why": "Checks Kimi starts once with the prompt and the file's model, as the owner tested it."},
  {"test": "tests/test_agent_kimi.py::test_a_failed_kimi_run_fails_the_run", "only_its_behavior": true, "why": "Checks a failed Kimi run fails the run with Kimi's exit code."},
  {"test": "tests/test_agent_kimi.py::test_a_kimi_run_writes_the_stored_sign_in_back_before_kimi_starts", "only_its_behavior": true, "why": "Checks the sign-in files setup stored are in the fresh home when Kimi starts."}
 
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

**Agent:** The check says one line of the summary is too long, so I'm shortening it and running the check again.

`6. Bash`
```
sed -i 's/Planned two criteria: a Kimi role starts Kimi with the file.s model, and starts signed in./Planned two criteria: a Kimi role starts with the file'"'"'s model, already signed in./' /tmp/dokima-out/review.json && grep -n Planned /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 699 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> 4:   "Planned two criteria: a Kimi role starts with the file's model, already signed in.",
> exit 0

**Agent:** The check says one line of the summary is too long, so I'm shortening it and running the check again.

`7. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/Planned two criteria: a Kimi role starts Kimi with the file.s model, and starts signed in./Planned two criteria: a Kimi role starts with the file'"'"'s model, already signed in./' /tmp/dokima-out/review.json && grep -n Planned /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 699 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

**Agent:** I approved the plan for [#699](https://github.com/dokima-dev/dokima/issues/699) (a role can run on Kimi Code CLI), with nothing for the planner to fix. The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Both asks are covered.** Each criterion carries one of the owner's two asks.
  - **699.1:** A role on a Kimi subscription starts Kimi with the model the settings file names.
  - **699.2:** The stored sign-in is back in place before Kimi starts, so no one signs in again.
- **The tests fail today for the right reason.** I ran all three. Each fails because Dokima has no Kimi adapter yet, not because of a crash or a bad path.
- **The tests prove the promise.** They start a run the same way a real run starts it, against a stand-in Kimi.
  - The model test needs the prompt, the file's model and the owner's tested output format, so a stub can't pass it.
  - A failed Kimi run must fail the whole run with Kimi's own exit code.
  - The sign-in test makes the stored sign-in through setup's own sign-in step. It checks that the same files are in the fresh machine's home folder when Kimi starts.

The issue's background notes also say the adapter should read Kimi's output, so the record names the model used and the run's stats show. Neither criterion covers this, and neither did the two criteria the parent plan [#696](https://github.com/dokima-dev/dokima/issues/696) (settings file picks each role's agent) approved. I didn't treat it as a dropped ask. If you want it, it needs its own criterion.

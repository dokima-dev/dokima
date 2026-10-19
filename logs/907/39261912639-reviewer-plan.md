# reviewer (plan) for #907

Run: https://github.com/dokima-dev/dokima/actions/runs/39261912639

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> total 116
> drwxr-xr-x  3 runner runner  4096 Oct 19 13:39 .
> drwxrwxrwt 18 root   root    4096 Oct 19 13:39 ..
> drwxr-xr-x  2 runner runner  4096 Oct 19 13:39 in
> -rw-r--r--  1 runner runner 13424 Oct 19 13:39 issue.md
> -rw-r--r--  1 runner runner   395 Oct 19 13:39 open_blockers.json
> -rw-r--r--  1 runner runner 65934 Oct 19 13:39 open_issues.json
> -rw-r--r--  1 runner runner  1359 Oct 19 13:39 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 19 13:39 parent.json
> -rw-r--r--  1 runner runner  5522 Oct 19 13:39 plan.json
> 
> in:
> total 20
> drwxr-xr-x 2 runner runner 4096 Oct 19 13:39 .
> drwxr-xr-x 3 runner runner 4096 Oct 19 13:39 ..
> -rw-r--r-- 1 runner runner 1445 Oct 19 13:39 01-worker.json
> -rw-r--r-- 1 runner runner 6308 Oct 19 13:39 02-planner.json
> # Issue #907: A rejected model key is reported as a missing plan
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses the agent's key, the owner is told to replace the key, not shown a planner bug.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/907#issuecomment-6268469826) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://g

`2. Bash`
```
cd /tmp/pack; cat in/02-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:3000])"; cat owner_words.json parent.json; cd /home/runner/work/dokima/dokima; cat tests/test_key_rejected.py
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39261121079",
>  "commit_before": "5695a04e7410571b3dc1bb3f11295a78131e5c35",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 262089,
>   "turns": 31,
>   "cost_usd": 1.6397026,
>   "tokens_in": 2067270,
>   "tokens_out": 24384
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/907/39261121079-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39261121079",
>  "handback": {
>   "kind": "user_story",
>   "title": "A rejected model key is reported as a rejected key",
>   "summary": "When the provider refuses the agent's key, the owner is told to replace the key, not shown a planner bug.",
>   "user_story": "When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.",
>   "acceptance_criteria": [
>    {
>     "text": "When the agent's output shows a login or key failure, the run ends as Model key rejected, not missing hand-back.",
>     "words": "After the agent step, if its output shows a login or key failure (401/403, invalid or expired token, failed to authenticate), end the run as \"Model key rejected\" instead of checking for the hand-back file.",
>     "source": "https://github.com/dokima-dev/dokima/issues/907",
>     "files": [
>      "dokima/agent_roles.py",
>      "dokima/agent_records.py",
>      "dokima/agents.py"
>     ],
>     "edge_cases": [
>      {
>       "case": "The provider answers 403 instead of 401.",
>       "test":

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "^(FAILED|ERROR|E  )|passed|failed" | head -40
```

> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://github.com/o/r/actions/runs/42)\n'
> E       AssertionError: 907.1: a 401 from the provider did not end the run as "Model key rejected":
> E         <!-- dokima-record -->
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" height="16" align="absmiddle" alt="failed"> <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/planner.svg" width="16" height="16" align="absmiddle" alt="planner"> The planner's run ended with its hand-back rejected by code.
> E         
> E         - found no plan.json: the planner always hands back a plan, a plan.json of kind user_story or feature, raising its questions for the owner in raises
> E         
> E         <details><summary>Full record</summary>
> E         
> E         ```json
> E         {
> E          "role": "planner",
> E          "stage": null,
> E          "run_id":
> E       assert 'Model key rejected' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://github.com/o/r/actions/runs/42)\n'
> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> mode

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "^E   +AssertionError|^(FAILED|ERROR)|passed|failed" | head -40
```

> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://github.com/o/r/actions/runs/42)\n'
> E       AssertionError: 907.1: a 401 from the provider did not end the run as "Model key rejected":
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" height="16" align="absmiddle" alt="failed"> <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/planner.svg" width="16" height="16" align="absmiddle" alt="planner"> The planner's run ended with its hand-back rejected by code.
> E       assert 'Model key rejected' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://github.com/o/r/actions/runs/42)\n'
> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://github.com/o/r/actions/runs/42)\n'
> E       AssertionError: 907.1: a 403 from the provider did not end the run as "Model key rejected":
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" height="16" align="absmiddle" alt="failed"> <img src="https://raw.githubusercont

`5. Bash`
```
cd /home/runner/work/dokima/dokima; ls .github/workflows; grep -n "claude.json\|is_error\|SCRUB_\|DOKIMA_AGENT_KEY" -r dokima .github/workflows | head -40; grep -n "audit" -A25 .github/workflows/entry.yml | head -60
```

> acceptance-criteria.yml
> agent.yml
> assign.yml
> audit.yml
> autopilot.yml
> board.yml
> card.yml
> commands.yml
> entry.yml
> fix.yml
> full-suite.yml
> playthrough.yml
> release.yml
> reviews.yml
> testmon.yml
> uptodate.yml
> wiki.yml
> dokima/agent_claude.py:3:It installs with npm, starts with today's command and flags, keeps its printed report as `claude.json` in the run's
> dokima/agent_claude.py:18:    """Start Claude Code on PROMPT with MODEL, its report into OUT/claude.json; return its exit code.
> dokima/agent_claude.py:20:    The run's key, given in DOKIMA_AGENT_KEY, reaches Claude Code as CLAUDE_CODE_OAUTH_TOKEN."""
> dokima/agent_claude.py:22:    if "DOKIMA_AGENT_KEY" in env:
> dokima/agent_claude.py:23:        env["CLAUDE_CODE_OAUTH_TOKEN"] = env.pop("DOKIMA_AGENT_KEY")
> dokima/agent_claude.py:24:    with open(os.path.join(str(out), "claude.json"), "w") as f:
> dokima/agent_claude.py:36:    return run_report(os.path.join(str(out), "claude.json"))
> dokima/agent_kimi.py:7:The run's key arrives in DOKIMA_AGENT_KEY: what `python3 -m dokima.setup add ... --sign-in` stored, the base64 text of
> dokima/agent_kimi.py:49:    key = env.pop("DOKIMA_AGENT_KEY", "")
> dokima/agent_roles.py:385:        # The record is public: every secret the step was given to remove (SCRUB_*) shows as [secret removed].
> dokima/agent_roles.py:386:        secrets = [v for k, v in os.environ.items() if k.startswith("SCRUB_")]
> dokima/agent_roles.py:404:        rec = scrubbed(rec, [v for k, v in os.environ.items() if k.startswith("SCRUB_")])
> do

**Agent:** Tests all fail for the right reason. Now checking how other agents (Codex, Kimi) leave their output, to judge whether the plan covers them.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/agent_*.py; grep -n "json\|out" dokima/agent_codex.py | head -20; grep -n "def \|key" dokima/audit.py | head -50; sed -n 1,80p .github/workflows/audit.yml
```

> dokima/agent_autopilot.py
> dokima/agent_checks.py
> dokima/agent_claude.py
> dokima/agent_codex.py
> dokima/agent_github.py
> dokima/agent_kimi.py
> dokima/agent_next.py
> dokima/agent_records.py
> dokima/agent_roles.py
> 4:to the repo (`--full-auto`; Codex is read-only otherwise), and keeps its event stream (`--json`) as `codex.jsonl` in
> 9:import json
> 15:STREAM = "codex.jsonl"
> 24:def run(prompt, model, out):
> 25:    """Start Codex on PROMPT with MODEL, its stream into OUT/codex.jsonl; return Codex's exit code."""
> 29:    with open(os.path.join(str(out), MODEL), "w") as f:
> 31:    with open(os.path.join(str(out), STREAM), "w") as f:
> 32:        return subprocess.run(["codex", "exec", "--model", model, "--full-auto", "--json", prompt],
> 33:                              stdout=f, env=env).returncode
> 36:def events(out):
> 39:        lines = open(os.path.join(str(out), STREAM)).read().splitlines()
> 45:            e = json.loads(line)
> 46:        except json.JSONDecodeError:
> 53:def models(out, log_dir):
> 56:        return sorted({open(os.path.join(str(out), MODEL)).read().strip()} - {""})
> 61:def report(out):
> 63:    turns = [e for e in events(out) if e.get("type") == "turn.completed"]
> 69:            "tokens_out": sum((u.get("output_tokens") or 0) for u in usage)}
> 27:def reason(e):
> 35:def unverified(what, e):
> 39:def compare_labels(live, wanted=None):
> 58:def compare_fields(live, wanted=None):
> 82:def compare_views(live):
> 97:def compare_rule(branch, live, want):
> 109:def compare_permissions(live):
> 125:def needed_

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "codex\|kimi" rules/*.md README* docs 2>/dev/null | head -15; grep -n "TODAY\|AGENTS\b\|def install" dokima/agents.py | head
```

> README.md:122:3. Add the repo secrets `DOKIMA_APP_KEY` (the app's private key) and `CLAUDE_CODE_OAUTH_TOKEN`. Make them repo secrets: secrets kept only in an environment never reach δokima's jobs. `dokima.yml` hands each secret to δokima by name; settings naming another agent key (`CODEX_API_KEY` or `KIMI_API_KEY`) must add its line there too.
> docs/wiki/Installing.md:35:`dokima.yml` hands each secret to δokima by name. If your settings name another agent key (`CODEX_API_KEY` or `KIMI_API_KEY`), add its line under `secrets:` in `dokima.yml` too.
> 38:TODAY = {"agent": "claude", "model": "claude-opus-5-5", "key": "CLAUDE_CODE_OAUTH_TOKEN"}
> 79:        return dict(TODAY)
> 118:def install(role):

**Agent:** The plan's tests all fail today for the right reason. One gap: they only cover Claude, and Codex and Kimi are documented agents too. Writing the review now.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner wrote six criteria and eight failing tests from the issue.",
   "The planner asked the owner whether the worker may change the audit workflows."
  ],
  "decided": [
   "The audit checks one key with one call to the Claude agent.",
   "Rejected-key detection reads the Claude agent's printed report."
  ],
  "open": [
   "The owner's answer on changing the audit workflows."
  ]
 },
 "verdict": "block",
 "summary": "The plan proves a rejected key only for the Claude agent; Codex and Kimi runs stay untested.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "907.1: other agents",
   "text": "The owner asked about the agent's output for any agent, but every 907.1 test fakes Claude's report only. Code reading only Claude's report passes, so a refused Codex key still reads as a missing plan. Smallest fix: add a 907.1 test where the settings name Codex for the planner and its stream shows a 401; it must end as Model key rejected naming `CODEX_API_KEY`.",
   "evidence": "`tests/test_key_rejected.py::write_record` writes only `claude.json`; `dokima/agent_codex.py` keeps output as `codex.jsonl`; `README.md:122` lists `CODEX_API_KEY` and `KIMI_API_KEY` as supported keys."
  }
 ],
 "answers": [
  {
   "raise": "W1",
   "answer": "done",
   "why": "The plan picks the call and how the key reaches the audit, and asks the owner about the workflow change."
  }
 ],
 "asks": [
  {"ask": "After the agent step, if its output shows a login or key failure (401/403, invalid or expired token, failed to authenticate), end the run as \"Model key rejected\" instead of checking for the hand-back file.", "source": "https://github.com/dokima-dev/dokima/issues/907", "criterion": "907.1"},
  {"ask": "The issue comment names the secret the settings use for that agent (e.g. `CLAUDE_CODE_OAUTH_TOKEN`)", "source": "https://github.com/dokima-dev/dokima/issues/907", "c
```

> Exit code 1
> raise 1's text holds 64 words, over its cap of 30: cut 34, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['raises'][0]['text']="907.1 tests fake only Claude's report, so a refused Codex key can still read as a missing plan. Fix: add a Codex 401 case naming its secret."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 907 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan and sent it back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What's good:**
- Each of the owner's 8 asks maps to one of the 6 criteria; none is missing.
- Each criterion is one behavior, so the size is ok.
- I ran all 8 new tests. Each fails today for the right reason: the feature isn't there yet, rather than a crash or a bad path.

**Blocker for the planner, on criterion 907.1:** the rejected-key tests only fake Claude's output. Code that reads only Claude's output would pass them, so a refused Codex or Kimi key would still be reported as a missing plan. The issue says "the agent's output", and the README lists `CODEX_API_KEY` and `KIMI_API_KEY` as supported keys. The smallest fix is one more test: a Codex run whose output shows a 401 must end as "Model key rejected" and name `CODEX_API_KEY`.

**Other items:**
- I answered the worker's blocker [W1] as done. The plan picks how the audit reads the key and which call it makes, and asks the owner about changing the audit workflows.
- I left the planner's question [P1] for the owner: may the worker change the audit workflows? Changing them alters how the system works, and the issue doesn't explicitly ask for it, so I can't answer it on the owner's behalf.

# reviewer (plan) for #907

Run: https://github.com/dokima-dev/dokima/actions/runs/39332128745

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (29.8KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/5d8b8117-10d5-4ac8-ab93-8b9f8afb7b5c/tool-results/bhh5tuoue.txt
> 
> Preview (first 2KB):
> # Issue #907: A rejected model key is reported as a missing plan
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/860
> 
> 
> **User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L115"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg

`2. Bash`
```
cd /tmp/pack; sed -n '/^## \|^### /p;' issue.md | head -50; grep -n "Comment\|^---" issue.md | head -40; wc -l issue.md; ls in; cat open_blockers.json
```

> ## Comments
> ### dokima-runtime on issue #907 (2026-10-19T13:30:49Z)
> ### dokima-runtime on issue #907 (2026-10-19T13:31:07Z)
> ### dokima-runtime on issue #907 (2026-10-19T13:32:45Z)
> ### dokima-runtime on issue #907 (2026-10-19T13:33:01Z)
> ### dokima-runtime on issue #907 (2026-10-19T13:38:37Z)
> ### RezaSoleymanifar on issue #907 (2026-10-19T21:56:36Z)
> ### dokima-runtime on issue #907 (2026-10-19T21:57:00Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:02:52Z)
> 77:## Comments
> 212 issue.md
> 01-worker.json
> 02-planner.json
> 03-reviewer-plan.json
> 04-planner.json
> [
>  {
>   "kind": "issue",
>   "label": "Adopter keys dropped",
>   "fault": "dokima",
>   "text": "An adopter's installed workflow passes only Claude Code's key, so Codex and Kimi keys never reach Dokima's jobs.",
>   "evidence": "`dokima/install/dokima.yml` line 20 passes only `DOKIMA_APP_KEY` and `CLAUDE_CODE_OAUTH_TOKEN` to `entry.yml`.",
>   "raised_by": "planner",
>   "id": "P2",
>   "to": "reviewer"
>  }
> ]
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /tmp/pack; sed -n 1,212p issue.md | cut -c1-1500
```

> # Issue #907: A rejected model key is reported as a missing plan
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/860
> 
> 
> **User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L115"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: A 401 reads "Model key rejected"; a plain missing plan still says so.*
>   <details><summary><picture><img src="https://raw.githubuserc

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1))" | head -300
```

> {
>  "kind": "user_story",
>  "title": "A rejected model key is reported as a rejected key",
>  "summary": "When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.",
>  "user_story": "When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.",
>  "acceptance_criteria": [
>   {
>    "text": "When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.",
>    "words": "A refused key for Claude Code, Codex and Kimi each ends as \"Model key rejected\"",
>    "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-6278270923",
>    "files": [
>     "dokima/agent_roles.py",
>     "dokima/agent_records.py",
>     "dokima/agents.py",
>     "dokima/agent_claude.py",
>     "dokima/agent_codex.py",
>     "dokima/agent_kimi.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "The provider answers 403 instead of 401.",
>      "test": "tests/test_key_rejected.py::test_a_403_from_the_provider_reads_model_key_rejected"
>     },
>     {
>      "case": "The provider says the token expired.",
>      "test": "tests/test_key_rejected.py::test_an_expired_token_reads_model_key_rejected"
>     },
>     {
>      "case": "A Codex key is refused.",
>      "test": "tests/test_key_rejected.py::test_a_refused_codex_key_reads_model_key_rejected"
>     },
>     {
>      "case": "A Kimi sign-in is refused.",
>      "test": "tests/test_key_rejected.py::test_a_refused_kimi_key_reads_model_key_rejected"
>     },
>     {
>      "case"

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head; cat -n tests/test_key_rejected.py
```

> commit 12cc0499867989b24e238d37dba88c92d938d14a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 22:02:35 2026 +0000
> 
>     planner for #907 (run 39331365511)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_key_rejected.py | 315 ++++++++++++++++++++++++++++++++++++---------
>  1 file changed, 252 insertions(+), 63 deletions(-)
>      1	"""Tests for #907: a rejected key is reported as such, not a missing plan.
>      2	
>      3	When the agent cannot log in (its provider answers 401 or 403, or says the token is invalid or expired), the run
>      4	leaves no hand-back, and the record used to blame the agent ("found no plan.json"). These tests write a run's record
>      5	the way the agent workflow does, from a fake agent output in the run's folder, and check what the owner reads. Each
>      6	shipped agent (Claude Code, Codex, Kimi) gets its own case, in the output file its adapter keeps. The setup audit's
>      7	key check is run against fake `claude`, `codex` and `kimi` commands on the PATH, so no real provider is ever called.
>      8	"""
>      9	import base64
>     10	import io
>     11	import json
>     12	import os
>     13	import subprocess
>     14	import sys
>     15	import tarfile
>     16	
>     17	ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
>     18	sys.path.insert(0, ROOT)
>     19	sys.path.insert(0, os.path.join(ROOT, "tests"))
>     20	from test_audit import REP

**Agent:** Reading the planner's tests; next I run them to see each fails for the right reason.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "^(FAILED|ERROR|E  .*907|[0-9]+ (passed|failed))|AssertionError|Error" | head -60
```

> E       AssertionError: 907.1: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
>         comment, _ = write_record(tmp_path, claude_output("API Error: 403 Forbidden: this key may not use this model."))
> E       AssertionError: 907.1: a 403 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: an expired token did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: a 401 refusing the Codex key did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: a 401 refusing the Kimi sign-in did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.2: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.2: a 401 refusing the codex key did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.3: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.4: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.5: with both keys

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "is_error\|\"result\"\|turn.failed\|error_text\|last_message" dokima/agent_records.py dokima/agent_roles.py dokima/agent_codex.py dokima/agent_kimi.py dokima/agent_claude.py | head -30; sed -n 1,40p dokima/install/dokima.yml; grep -n "audit" -A15 .github/workflows/entry.yml | head -40
```

> # Dokima, run from Dokima's own repo at a release tag (#812). Copy this file to .github/workflows/dokima.yml.
> name: dokima
> on:
>   issues:
>   issue_comment:
>   pull_request_target:
>   pull_request_review:
>   pull_request_review_comment:
>   merge_group:
>   push:
>   schedule: [{cron: "*/15 * * * *"}, {cron: "17 6 * * *"}]
>   # Every workflow, the repo's own CI included, so the card redraws when it finishes (#859).
>   workflow_run: {workflows: ["*"], types: [in_progress, completed]}
>   repository_dispatch: {types: [dokima-next]}
>   workflow_dispatch:
> permissions: {contents: read, issues: write, pull-requests: read, actions: read, checks: read}
> jobs:
>   dokima:
>     uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.6
>     secrets: {DOKIMA_APP_KEY: "${{ secrets.DOKIMA_APP_KEY }}", CLAUDE_CODE_OAUTH_TOKEN: "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"}
> 101:  audit:
> 102-    if: github.event_name == 'workflow_dispatch' || (github.event_name == 'schedule' && github.event.schedule == '17 6 * * *')
> 103:    uses: ./.github/workflows/audit.yml
> 104-    secrets: {DOKIMA_APP_KEY: "${{ secrets.DOKIMA_APP_KEY }}"}

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "claude.json\|codex.jsonl\|kimi.jsonl" dokima/*.py | head; grep -n "def \|result" dokima/agent_claude.py | head -30
```

> dokima/agent_claude.py:3:It installs with npm, starts with today's command and flags, keeps its printed report as `claude.json` in the run's
> dokima/agent_claude.py:18:    """Start Claude Code on PROMPT with MODEL, its report into OUT/claude.json; return its exit code.
> dokima/agent_claude.py:24:    with open(os.path.join(str(out), "claude.json"), "w") as f:
> dokima/agent_claude.py:36:    return run_report(os.path.join(str(out), "claude.json"))
> dokima/agent_kimi.py:4:command `kimi -p PROMPT --output-format stream-json` and the role's model, and keeps the stream as `kimi.jsonl` in the
> dokima/agent_kimi.py:21:STREAM = "kimi.jsonl"
> dokima/agent_kimi.py:45:    """Put the sign-in back, then start Kimi on PROMPT with MODEL, its stream into OUT/kimi.jsonl.
> dokima/agent_codex.py:4:to the repo (`--full-auto`; Codex is read-only otherwise), and keeps its event stream (`--json`) as `codex.jsonl` in
> dokima/agent_codex.py:15:STREAM = "codex.jsonl"
> dokima/agent_codex.py:25:    """Start Codex on PROMPT with MODEL, its stream into OUT/codex.jsonl; return Codex's exit code."""
> 12:def install():
> 17:def run(prompt, model, out):
> 29:def models(out, log_dir):
> 34:def report(out):
> 39:def transcript(log_dir, secrets):

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote nine criteria and fourteen tests from the owner's answers.", "Each of the three agents now has a refused key case and its own secret case."],
  "decided": ["The setup audit receives each declared key by name and calls each set key's agent once."],
  "open": ["The installed workflow passes only Claude Code's key, raised as its own issue."]
 },
 "verdict": "block",
 "summary": "One gap: the key-leak test for a failed run misses the provider's own message, which can echo part of the key.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "907.4: provider echo", "text": "907.4 only checks Claude's refusal, which holds no key. Codex's refusal echoes the key's tail, so quoting it passes. Fix: add a Codex case checking the tail.", "evidence": "`CODEX_401` holds `sk-proj-****efgh`; `test_the_record_never_prints_any_part_of_the_key` uses only `REJECTED_401`."}
 ],
 "answers": [
  {"raise": "P2", "answer": "done", "why": "Confirmed: the installed workflow passes only two secrets. It is a real problem outside this issue."}
 ],
 "asks": [
  {"ask": "end the run as \"Model key rejected\" instead of checking for the hand-back file", "source": "https://github.com/dokima-dev/dokima/issues/907", "criterion": "907.1"},
  {"ask": "A refused key for Claude Code, Codex and Kimi each ends as \"Model key rejected\"", "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-6278270923", "criterion": "907.1"},
  {"ask": "a run with a real missing plan still gives the missing-plan one", "source": "https://github.com/dokima-dev/dokima/issues/907", "criterion": "907.1"},
  {"ask": "The issue comment names the secret the settings use for that agent", "source": "https://github.com/dokima-dev/dokima/issues/907", "criterion": "907.2"},
  {"ask": "names that agent's secret", "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-627827092
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> previous_step did line 2 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`10. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';r=json.load(open(p))
r["summary"]="One gap: the failed-run key-leak test misses the provider's own message, which can echo part of the key."
r["previous_step"]["did"][1]="Each of the three agents now has a refused-key case and a secret case."
r["previous_step"]["decided"][0]="The setup audit receives each declared key by name and calls each set key's agent."
json.dump(r,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 907 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P2 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P2 files an issue, so verdict must be symptom, root cause or new, not None

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "searched" dokima/agent*.py | head; gh issue list --state open --search "install workflow key" 2>&1 | head; gh issue list --state open --limit 60 2>&1 | grep -i "key\|secret\|install" | head
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_autopilot.py:243:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}

**Agent:** Fixing the check's last complaint: the issue answer must name which open issues were searched.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 14,60p dokima/agent_checks.py; ls /tmp/pack
```

> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(open(path)) if os.path.exists(path) else []
>     theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
>               and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
>     confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
>                  and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
>     filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
>     if not filed:
>         return []
>     bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
>     named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
>              for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numbers([d.get(f)]))]
>     if not named:

`13. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "SEARCHED\|SYMPTOMS\|CAUSE\|VERDICT\|def filing_problems" -A2 dokima/raises.py | head -40; python3 -c "
import json;[print(i['number'],i.get('title')) for i in json.load(open('/tmp/pack/open_issues.json'))]" | grep -i "key\|secret\|install\|adopt\|codex\|kimi"
```

> 23:SEARCHED = "searched"
> 24-# Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
> 25:VERDICT = "verdict"
> 26:VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> 27-# A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
> 28:CAUSE = "cause"
> 29:SYMPTOMS = "symptoms"
> 30-# An issue may say whose fault it is: Dokima's, filed in the upstream repo the settings name, or unclear (#745).
> 31-FAULT = "fault"
> --
> 43:    names = list(VERDICTS)
> 44-    return ", ".join(names[:-1]) + " or " + names[-1]
> 45-
> --
> 47:def filing_problems(where, decided):
> 48-    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> 49-    problems = []
> 50:    searched = decided.get(SEARCHED)
> 51-    if not is_numbers(searched) or not searched:
> 52:        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
> 53-                        f"cause, not {searched!r}")
> 54:    if decided.get(VERDICT) not in VERDICTS:
> 55:        problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
> 56:    cause = decided.get(CAUSE)
> 57:    if decided.get(VERDICT) == "symptom" and not (isinstance(cause, int) and not isinstance(cause, bool)):
> 58:        problems.append(f"{where} is a symptom, so {CAUSE} must name its cause, an open issue by num

`14. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';r=json.load(open(p))
r["answers"][0].update({"searched":[913,747],"verdict":"new"})
json.dump(r,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 907 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#907](https://github.com/dokima-dev/dokima/issues/907) (a rejected model key is reported as a missing plan) over one gap. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**Blocked on criterion 907.4 (never show any part of the key on a failed run's comment):**
- The test only fakes Claude Code refusing a key, and that refusal message contains no part of the key.
- Codex's refusal message shows the end of the key (`sk-proj-****efgh` in the test data).
- So a comment that copies the provider's message would leak those last four characters for Codex and still pass.
- Fix for the planner: add a Codex refusal case and check the key's start and end don't appear.

**Everything else:**
- Each of the owner's asks, in the issue and in their later answers, matches one of the nine criteria. None are missing.
- Each criterion is one behavior.
- All 14 new tests fail today because the feature is missing, not because of a crash or a bad path. Each failure names its criterion.
- The owner said yes to changing the audit workflow, so changing the workflow files is allowed here.

**The planner's issue raise:** I agreed it's real. The workflow file adopters install still passes only Claude Code's key, so Codex and Kimi keys never reach Dokima's jobs. Open issues [#913](https://github.com/dokima-dev/dokima/issues/913) (setup stores any secret name) and [#747](https://github.com/dokima-dev/dokima/issues/747) (one shared GitHub App) cover something else, so this one is marked new.

That problem also means criterion 907.8 can't fully work in adopters' repos until it's fixed. I left it to the separate issue rather than block on it.

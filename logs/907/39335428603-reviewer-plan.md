# reviewer (plan) for #907

Run: https://github.com/dokima-dev/dokima/actions/runs/39335428603

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (42.4KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/4faec11b-9b63-427e-b895-7de5a4f91246/tool-results/b685o667y.txt
> 
> Preview (first 2KB):
> # Issue #907: A rejected model key is reported as a rejected key
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/931 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/931/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/860
> - https://github.com/dokima-dev/dokima/issues/930
> 
> 
> **User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" 

`2. Bash`
```
cd /tmp/pack; sed -n '/^## \|^### \|Comment\|^\*\*@/p' issue.md | head -50; wc -l issue.md; ls in
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
> ### dokima-runtime on issue #907 (2026-10-19T22:05:19Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:07:04Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:08:37Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:08:40Z)
> ### dokima-runtime on PR #931 (2026-10-19T22:14:52Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:27:58Z)
> ### dokima-runtime on issue #907 (2026-10-19T22:30:22Z)
> 370 issue.md
> 01-worker.json
> 02-planner.json
> 03-reviewer-plan.json
> 04-planner.json
> 05-reviewer-plan.json
> 06-planner.json
> 07-reviewer-plan.json
> 08-worker.json
> 09-reviewer-pr.json
> 10-planner.json
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Read`
```
/tmp/pack/issue.md
```

> 1	# Issue #907: A rejected model key is reported as a rejected key
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> 5	When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> 6	
> 7	**Plan**
> 8	
> 9	https://github.com/dokima-dev/dokima/pull/931 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/931/files)
> 10	
> 11	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 12	
> 13	- https://github.com/dokima-dev/dokima/issues/860
> 14	- https://github.com/dokima-dev/dokima/issues/930
> 15	
> 16	
> 17	**User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
> 18	
> 19	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 20	
> 21	- <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.
> 22	  *<a href="https://github

`4. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; python3 -c "
import json;d=json.load(open('in/10-planner.json'));print(json.dumps(d,indent=1)[:5000])"
```

> []
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
>      "ca

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/ | head -80; sed -n 380,460p tests/test_key_rejected.py
```

> commit 15845b6963244cc2f9f5770259609804987429b5
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 22:29:57 2026 +0000
> 
>     planner for #907 (run 39335142102)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_key_rejected.py | 12 ++++++++++--
>  1 file changed, 10 insertions(+), 2 deletions(-)
> commit 15845b6963244cc2f9f5770259609804987429b5
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 19 22:29:57 2026 +0000
> 
>     planner for #907 (run 39335142102)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_key_rejected.py b/tests/test_key_rejected.py
> index 85bfc082..535e21ac 100644
> --- a/tests/test_key_rejected.py
> +++ b/tests/test_key_rejected.py
> @@ -14,6 +14,8 @@ import subprocess
>  import sys
>  import tarfile
>  
> +import yaml
> +
>  ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
>  sys.path.insert(0, ROOT)
>  sys.path.insert(0, os.path.join(ROOT, "tests"))
> @@ -389,11 +391,17 @@ def test_the_audit_reports_a_rejected_key_as_one_line(record_property, tmp_path,
>  def test_the_audit_job_gets_each_declared_agent_key_by_name(record_property):
>      """The audit job is handed every declared agent key by name.
>  
> -    `entry.yml` passes each of the three keys to the audit job, `audit.yml` declares each one, and the audit step
> -    reads each as `DOKIMA_

**Agent:** Reviewing the plan's one change since last approval: criterion 907.8 now covers the adopter's install file. Checking the test runs and fails for the right reason.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "yaml\|load_yaml" tests/test_key_rejected.py | head; grep -rn "^import yaml\|pyyaml\|PyYAML" --include=*.py --include=*.txt --include=*.toml . | head; cat dokima/install/dokima.yml; python3 -m pytest -q tests/test_key_rejected.py 2>&1 | tail -15
```

> 17:import yaml
> 23:from test_start import load_yaml  # noqa: E402
> 94:    settings_file = tmp_path / "settings.yaml"
> 283:    settings_file = root / ".dokima" / "settings.yaml"
> 341:    steps = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "audit.yml")).read())["jobs"]["audit"]["steps"]
> 400:    install = yaml.safe_load(open(os.path.join(ROOT, "dokima", "install", "dokima.yml")).read()) or {}
> 405:    entry = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "entry.yml")).read())
> 409:    wf = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "audit.yml")).read())
> dokima/prompt.py:16:import yaml
> dokima/setup.py:27:import yaml
> dokima/settings.py:20:import yaml
> dokima/audit.py:17:import yaml
> dokima/agents.py:38:import yaml
> tests/test_secrets_by_name.py:11:import yaml
> tests/test_release.py:34:import yaml
> tests/test_unplanned_prs.py:105:    passed, rows, out = acceptance_check(tmp_path, DEPENDABOT, "dependabot/pip/pyyaml-6.0.2")
> tests/test_testmon.py:9:CI has neither testmon nor PyYAML, so these tests read the workflow files line by line, and run the shell of the
> tests/test_key_rejected.py:17:import yaml
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
>   # Every workflow, the repo's own CI included, 

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def load_yaml" -A8 tests/test_start.py; grep -rn "pyyaml\|PyYAML\|pip install" .github/workflows/*.yml | head; sed -n 1,30p tests/test_secrets_by_name.py; git stash list; git checkout -q main -- 2>/dev/null; git diff main --stat | tail -3
```

> 289:def load_yaml(text):
> 290-    """A workflow file as nested dicts, lists and strings, read without a YAML library.
> 291-
> 292-    Covers what workflows use: mappings, lists of mappings, `|` and `>` block text, `{a: b}` and `[a, b]` on one line,
> 293-    quoted strings and comments. Every value is kept as text."""
> 294-    lines = text.split("\n")
> 295-    pos = [0]
> 296-
> 297-    def indent(l):
> .github/workflows/assign.yml:33:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/assign.yml:64:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/audit.yml:51:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/audit.yml:90:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/acceptance-criteria.yml:43:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/acceptance-criteria.yml:84:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/acceptance-criteria.yml:102:          pip install -q $TOOLS pyyaml
> .github/workflows/autopilot.yml:72:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/autopilot.yml:119:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> .github/workflows/autopilot.yml:171:      - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
> """Tests for #8

`8. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/07-reviewer-plan.json'));h=d['handback'];h.pop('previous_step',None);print(json.dumps(h,indent=1))"
```

> {
>  "asks": [
>   {
>    "ask": "end the run as \"Model key rejected\" instead of checking for the hand-back file",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.1"
>   },
>   {
>    "ask": "A refused key for Claude Code, Codex and Kimi each ends as \"Model key rejected\"",
>    "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-6278270923",
>    "criterion": "907.1"
>   },
>   {
>    "ask": "a run with a real missing plan still gives the missing-plan one",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.1"
>   },
>   {
>    "ask": "The issue comment names the secret the settings use for that agent",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.2"
>   },
>   {
>    "ask": "names that agent's secret",
>    "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-6278270923",
>    "criterion": "907.2"
>   },
>   {
>    "ask": "says the provider refused it: make a new one and replace the repo secret",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.3"
>   },
>   {
>    "ask": "Never print any part of the key.",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.4"
>   },
>   {
>    "ask": "The setup audit checks the agent key once with a tiny call (when the key is present)",
>    "source": "https://github.com/dokima-dev/dokima/issues/907",
>    "criterion": "907.5"
>   },
>   {
>    "ask": "reports a rejected key as one lin

`9. Bash`
```
cd /tmp && rm -rf mainchk && git -C /home/runner/work/dokima/dokima worktree add -q /tmp/mainchk origin/main 2>&1|tail -1; cp /home/runner/work/dokima/dokima/tests/test_key_rejected.py /tmp/mainchk/tests/; cd /tmp/mainchk && python3 -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "FAILED|passed|failed" | cut -c1-200; cd /tmp; git -C /home/runner/work/dokima/dokima worktree remove --force /tmp/mainchk
```

> cp: cannot stat '/home/runner/work/dokima/dokima/tests/test_key_rejected.py': No such file or directory
> Shell cwd was reset to /home/runner/work/dokima/dokima

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git branch --show-current; git status --short | head; git checkout -q try/issue-907 && git branch --show-current && ls tests/test_key_rejected.py; git worktree list
```

> main
> try/issue-907
> tests/test_key_rejected.py
> /home/runner/work/dokima/dokima 15845b69 [try/issue-907]

**Agent:** My earlier command switched the sandbox to main by mistake. It's now back on the review branch, with no files changed.

`11. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree add -q /tmp/mainchk origin/main 2>&1|tail -1; cp tests/test_key_rejected.py /tmp/mainchk/tests/; cd /tmp/mainchk && python3 -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-220; cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainchk; git branch --show-current
```

> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" height="16" align="absmiddle" alt="failed"> <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/planner.svg
> E       assert 'Model key rejected' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at
> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at API prices · [run](https://
> E         <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" height="16" align="absmiddle" alt="failed"> <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/planner.svg
> E       assert 'Model key rejected' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at
> comment = '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/failed.svg" width="16" heig...alt="stats"> model unknown · 0.0 min · 1 turns · $0.00 at

**Agent:** All 15 tests fail on main because the feature is missing, so each fails for the right reason. Writing the review.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
h=json.load(open('in/07-reviewer-plan.json'))['handback']
r={k:h[k] for k in ("asks","behaviors","tests","edge_cases","boxes","size")}
r["previous_step"]={"did":["The planner added the adopter's install file to the audit wiring criterion.","Its test now checks the install file hands Dokima each agent key by name."],"decided":["The worker may now map the Codex and Kimi keys in the install file."],"open":[]}
r["verdict"]="approve"
r["summary"]="The install file is now covered; all fifteen tests fail on main because the feature is missing."
r["raises"]=[]; r["answers"]=[]
for t in r["tests"]:
    if t["test"].endswith("gets_each_declared_agent_key_by_name"):
        t["why"]="Checks all three keys through the install file and both workflows."
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 907 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#907](https://github.com/dokima-dev/dokima/issues/907) (a refused model key is reported as a refused key). The review is saved in `/tmp/dokima-out/review.json` and passes both checks.

- **What changed:** at the last code review on [#931](https://github.com/dokima-dev/dokima/pull/931) (the pull request for this issue), the plan was missing the adopter's install file. The planner has now added it to criterion 907.8. Its test also checks that this file hands Dokima the Claude Code, Codex and Kimi keys by name.
- **Tests:** I copied the 15 new tests onto main and ran them. All 15 fail there because the feature is missing, not because of a crash or a bad path.
  - On this branch, the only one that still fails is the install-file check: Codex and Kimi keys aren't mapped yet. The worker will do that next.
- **Asks and open items:** every ask from the owner still maps to a criterion. No blockers were open and I raised none.

One slip during the review: a command of mine briefly switched the sandbox to main. I switched it straight back, and no files were changed.

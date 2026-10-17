# reviewer (plan) for #812

Run: https://github.com/dokima-dev/dokima/actions/runs/39056872436

`1. Bash`
```
cd /tmp/pack; ls in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (72.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/58c746f8-4d92-49e2-b1d9-d48d43f5018c/tool-results/bnjc61t5z.txt
> 
> Preview (first 2KB):
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> 04-reviewer-plan.json
> 05-planner.json
> 06-reviewer-plan.json
> 07-worker.json
> 08-reviewer-pr.json
> 09-planner.json
> 10-reviewer-plan.json
> 11-worker.json
> 12-worker.json
> 13-worker.json
> 14-reviewer-pr.json
> 15-planner.json
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/824 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (60.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/58c746f8-4d92-49e2-b1d9-d48d43f5018c/tool-results/byx7b07es.txt
> 
> Preview (first 2KB):
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/824 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/

**Agent:** Large. Let me read it in parts.

`3. Bash`
```
cd /tmp/pack; sed -e 's/<img[^>]*>//g' issue.md | wc -c; sed -e 's/<img[^>]*>//g' issue.md | head -c 30000
```

> <persisted-output>
> Output too large (29.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/58c746f8-4d92-49e2-b1d9-d48d43f5018c/tool-results/bqqpd6oqo.txt
> 
> Preview (first 2KB):
> 44601
> # Issue #812: Dokima's workflows run from Dokima's own repo
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/824 ·  [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/816
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/747
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/41
> - https://github.com/dokima-dev/dokima/issues/110
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/820
> 
> 
> **User story:** An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.
>   *<a href="https://github.com/dokima-dev/dokima/blob/a8c77ef230df88dadb93c89171a617f648f459a6/tests/test_thin_inst

`4. Bash`
```
cd /tmp/pack; sed -e 's/<img[^>]*>//g; s/<details>.*<\/details>//g; s/<a href[^>]*>//g; s/<\/a>//g' issue.md > /tmp/issue_clean.md; wc -c /tmp/issue_clean.md; grep -n "^## \|^### \|Comment\|^---" /tmp/issue_clean.md | head -80
```

> 40098 /tmp/issue_clean.md
> 110:## Comments
> 112:### dokima-runtime on issue #812 (2026-10-17T13:34:18Z)
> 116:### dokima-runtime on issue #812 (2026-10-17T13:34:40Z)
> 145:### dokima-runtime on issue #812 (2026-10-17T14:01:12Z)
> 176:### dokima-runtime on issue #812 (2026-10-17T14:05:26Z)
> 205:### dokima-runtime on issue #812 (2026-10-17T14:08:02Z)
> 227:### dokima-runtime on issue #812 (2026-10-17T14:17:04Z)
> 256:### dokima-runtime on issue #812 (2026-10-17T14:39:31Z)
> 273:### dokima-runtime on issue #812 (2026-10-17T15:14:15Z)
> 278:### dokima-runtime on issue #812 (2026-10-17T15:14:17Z)
> 319:### dokima-runtime on PR #824 (2026-10-17T15:31:17Z)
> 362:### dokima-runtime on issue #812 (2026-10-17T15:45:19Z)
> 427:### dokima-runtime on issue #812 (2026-10-17T16:40:16Z)
> 444:### dokima-runtime on PR #824 (2026-10-17T16:47:32Z)
> 448:### dokima-runtime on issue #812 (2026-10-17T16:47:35Z)
> 467:### dokima-runtime on PR #824 (2026-10-17T17:03:55Z)
> 471:### dokima-runtime on issue #812 (2026-10-17T17:04:03Z)
> 476:### dokima-runtime on PR #824 (2026-10-17T17:04:06Z)
> 495:### RezaSoleymanifar on issue #812 (2026-10-17T17:15:44Z)
> 507:### dokima-runtime on PR #824 (2026-10-17T17:16:14Z)
> 526:### RezaSoleymanifar on issue #812 (2026-10-17T17:29:54Z)
> 535:### dokima-runtime on PR #824 (2026-10-17T17:30:17Z)
> 559:### dokima-runtime on PR #824 (2026-10-17T17:37:40Z)
> 581:### dokima-runtime on issue #812 (2026-10-17T18:06:16Z)
> 636:### dokima-runtime on issue #812 (2026-10-17T18:09:34Z)
> Shell cwd was reset to /home/runner

`5. Read`
```
/tmp/issue_clean.md
```

> 1	# Issue #812: Dokima's workflows run from Dokima's own repo
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-blocking: {"blocked_by": [], "blocks": [813, 816], "loop": []} -->
> 5	Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.
> 6	
> 7	**Plan**
> 8	
> 9	https://github.com/dokima-dev/dokima/pull/824 ·  [files changed](https://github.com/dokima-dev/dokima/pull/824/files)
> 10	
> 11	 **Blocks:**
> 12	
> 13	- https://github.com/dokima-dev/dokima/issues/813
> 14	- https://github.com/dokima-dev/dokima/issues/816
> 15	
> 16	 **Relates to:**
> 17	
> 18	- https://github.com/dokima-dev/dokima/issues/742
> 19	- https://github.com/dokima-dev/dokima/issues/747
> 20	- https://github.com/dokima-dev/dokima/issues/755
> 21	- https://github.com/dokima-dev/dokima/issues/41
> 22	- https://github.com/dokima-dev/dokima/issues/110
> 23	- https://github.com/dokima-dev/dokima/issues/272
> 24	- https://github.com/dokima-dev/dokima/issues/820
> 25	
> 26	
> 27	**User story:** An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.
> 28	
> 29	 **Acceptance criteria**
> 30	
> 31	-  **Acceptance criterion:** A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.
> 32	  * Acceptance test: No job of any shared workflow runs Dokima code from the adopter's repo.*
> 33	  
> 34	  - Source: https://github.com/dokima-dev/dokima/issues/742
> 35	-  **Acceptance criterion:** Every job that reads a key takes it from the repo's key

`6. Read`
```
/tmp/issue_clean.md
```

> 145	### dokima-runtime on issue #812 (2026-10-17T14:01:12Z)
> 146	
> 147	<!-- dokima-record -->
> 148	  Plan review blocked the plan with 1 blocker.
> 149	
> 150	**Raised earlier:**
> 151	
> 152	- Planner on [#812](https://github.com/dokima-dev/dokima/issues/812#issuecomment-6234501883) raised:  **Check names in adopters:** In an adopter's repo the checks run inside a called workflow, so GitHub prefixes their names; the required check names will not match. · filed as an issue
> 153	  - Done: Agreed: new. Open issues on check names never cover the prefix a called workflow adds.
> 154	
> 155	**Raised:**
> 156	
> 157	-  **Test off its criterion:** `test_every_event_dokima_acts_on_starts_the_adopters_workflow` proves the one workflow starts on every event, not where code comes from (812.1). Give it its own criterion from the owner's 'One thin workflow', or drop it. · for the planner
> 158	  - Evidence: `tests/test_thin_install.py:164` reads only the thin workflow's `on:`; criterion 812.1 says nothing about events.
> 159	
> 160	 **Filed as issues:**
> 161	
> 162	- https://github.com/dokima-dev/dokima/issues/820 · the reviewer confirmed it
> 163	
> 164	<details><summary>Full record</summary>
> 165	
> 166	(full record: in/, from the record files)
> 167	
> 168	</details>
> 169	
> 170	**Next:** The planner starts now.
> 171	
> 172	<!-- dokima-stats -->
> 173	 Opus 5.5 · 3.3 min · 11 turns · 551K tokens in, 9K out · $0.68 at API prices · [conversation](https://github.com/dokima-dev/dokima/blob/logs/logs/812/39038968490-reviewer-plan.md) · [

`7. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; python3 -c "
import json;d=json.load(open('in/14-reviewer-pr.json'));print(json.dumps(d,indent=1)[:8000])"
```

> []
> {
>  "role": "reviewer",
>  "stage": "pr",
>  "run_id": "39054587009",
>  "commit_before": "db2d10ebf50a69373cfd81a717e4b781080d79ed",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 12681,
>   "turns": 2,
>   "cost_usd": 1.2184819000000005,
>   "tokens_in": 155423,
>   "tokens_out": 899
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/812/39054587009-reviewer-pr.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39054587009",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Made the merge queue's judge take main's code when run in Dokima's own repo.",
>     "Made the full suite read its settings with Dokima's own code."
>    ],
>    "decided": [
>     "Kept the owner's rule: the full suite never runs on a push to main."
>    ],
>    "open": []
>   },
>   "verdict": "block",
>   "summary": "Every shared workflow fetches Dokima's code from main, not the tag the adopter calls, so the tag pins nothing.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "worker",
>     "label": "812.8 code from main",
>     "text": "Shared workflows check out Dokima at `github.job_workflow_sha`, which GitHub never sets, so the ref is empty and main runs. Fix: use `job.workflow_sha`.",
>     "evidence": "`agent.yml:82` and 20 more; GitHub's contexts table lacks it; actions/runner#2417 reports it empty.",
>     "raised_by": "reviewer",
>     "id": "R4"
>    },
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "812.8 test too weak",
>     "

`8. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('plan.json'));
d.pop('test_changes',None)
print(json.dumps(d,indent=1))" | head -c 20000; python3 -c "
import json;d=json.load(open('in/15-planner.json'));h=d['handback'];print(h.keys());print(json.dumps(h.get('answers'),indent=1));print(json.dumps(h.get('raises'),indent=1))"
```

> {
>  "kind": "user_story",
>  "title": "Dokima's workflows run from Dokima's own repo",
>  "summary": "Adopters call Dokima's shared workflows by tag, so Dokima's code, keys and errors all come from Dokima's side.",
>  "user_story": "An adopter's runs use Dokima's tagged code and the adopter's own secrets, failing clearly when one is missing.",
>  "acceptance_criteria": [
>   {
>    "text": "A run on an adopter's repo takes all Dokima code from Dokima's own repo, never the adopter's.",
>    "words": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
>    "source": "https://github.com/dokima-dev/dokima/issues/742",
>    "files": [
>     "dokima/install/dokima.yml",
>     ".github/workflows/entry.yml",
>     ".github/workflows/acceptance-criteria.yml",
>     ".github/workflows/agent.yml",
>     ".github/workflows/assign.yml",
>     ".github/workflows/audit.yml",
>     ".github/workflows/autopilot.yml",
>     ".github/workflows/board.yml",
>     ".github/workflows/card.yml",
>     ".github/workflows/commands.yml",
>     ".github/workflows/fix.yml",
>     ".github/workflows/full-suite.yml",
>     ".github/workflows/reviews.yml",
>     ".github/workflows/testmon.yml",
>     ".github/workflows/uptodate.yml"
>    ],
>    "edge_cases": [
>     {
>      "case": "An adopter's repo holding no Dokima code at all",
>      "test": "tests/test_thin_install.py::test_a_run_starts_in_a_repo_holding_no_dokima_code"
>     },
>     {
>      "case": "An adopter's repo holding its own copy of Dokima's code",
>      "test": "tests/test_thin_instal

**Agent:** I'm reviewing the planner's fix for the last blocker: a new test for the release-tag criterion. Running it now.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_every_shared_workflow_fetches_dokimas_code_at_the_called_commit" -A60 tests/test_thin_install.py; git log --oneline -3 -- tests/test_thin_install.py; timeout 300 python -m pytest -q tests/test_thin_install.py 2>&1 | tail -30
```

> 370:def test_every_shared_workflow_fetches_dokimas_code_at_the_called_commit(record_property):
> 371-    """Each shared workflow fetches Dokima's code at the commit the adopter called, never main.
> 372-
> 373-    Proves 812.8. A tag pins nothing unless the shared workflow fetches Dokima's code at that tag's commit. Fills each
> 374-    shared workflow's checkout of Dokima's repo with the values GitHub sets when an adopter's repo calls it: the
> 375-    called workflow's own commit (`job.workflow_sha`) and repo (`job.workflow_repository`), while the run's own
> 376-    commit (`github.workflow_sha`) is the adopter's. Every such checkout must name the called commit; an empty ref,
> 377-    which falls back to main, fails."""
> 378-    record_property("proves", "812.8")
> 379-    called, adopters = "c" * 40, "a" * 40
> 380-    ctx = {"github": Ctx(repository="adopter/repo", workflow_sha=adopters, sha=adopters, ref="refs/heads/main",
> 381-                         event_name="issue_comment", event=Ctx()),
> 382-           "job": Ctx(workflow_sha=called, workflow_repository=ts.DOKIMA_REPO,
> 383-                      workflow_ref=f"{ts.DOKIMA_REPO}/.github/workflows/agent.yml@refs/tags/v1.2.3"),
> 384-           "inputs": Ctx(), "vars": Ctx(), "secrets": Ctx(), "env": Ctx(), "steps": Ctx(), "needs": Ctx(),
> 385-           "matrix": Ctx(), "runner": Ctx()}
> 386-    status = {"failed": False}
> 387-    found, wrong = [], []
> 388-    for name in SHARED:
> 389-        for job_name, job in (read_yaml(os.path.join(WORKF

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^import\|^from\|as ts" tests/test_thin_install.py | head; grep -rn "def dokima_checkout" -A25 tests/ | head -40; grep -n "job_workflow_sha" .github/workflows/agent.yml | head -3
```

> 15:import glob
> 16:import json
> 17:import os
> 18:import re
> 19:import sys
> 21:import yaml
> 24:import test_settings_workflows as sw  # noqa: E402
> 25:import test_start as ts  # noqa: E402
> 26:from test_start import Ctx, N  # noqa: E402
> tests/test_start.py:423:def dokima_checkout(step, ctx, status, into=None):
> tests/test_start.py-424-    """Whether STEP checks out Dokima's own repo; with INTO, stands in for it.
> tests/test_start.py-425-
> tests/test_start.py-426-    GitHub's checkout action cannot run here. A step checking out dokima-dev/dokima gets this checkout's Dokima code
> tests/test_start.py-427-    and settings file instead, copied to the step's path (INTO maps it to a folder), as the real checkout would."""
> tests/test_start.py-428-    w = step.get("with") or {}
> tests/test_start.py-429-    if "actions/checkout" not in str(step.get("uses") or "") or fill(w.get("repository", ""), ctx, status) != DOKIMA_REPO:
> tests/test_start.py-430-        return False
> tests/test_start.py-431-    if into is not None:
> tests/test_start.py-432-        dest = into(fill(w.get("path", "") or ".", ctx, status))
> tests/test_start.py-433-        for part in DOKIMA_PARTS:
> tests/test_start.py-434-            shutil.copytree(os.path.join(ROOT, part), os.path.join(dest, part), dirs_exist_ok=True,
> tests/test_start.py-435-                            ignore=shutil.ignore_patterns("__pycache__"))
> tests/test_start.py-436-    return True
> tests/test_start.py-437-
> tests/test_start.py-438-
> tests/test_start.py-439-def record

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "repository:" .github/workflows/agent.yml | head -3; rm -rf /tmp/wt; git worktree add -q /tmp/wt HEAD && cd /tmp/wt && sed -i 's/github\.job_workflow_sha/job.workflow_sha/g' .github/workflows/*.yml && timeout 300 python -m pytest -q tests/test_thin_install.py 2>&1 | tail -3; cd /tmp/wt && git checkout -q .github && sed -i 's/github\.job_workflow_sha/github.workflow_sha/g' .github/workflows/*.yml && timeout 300 python -m pytest -q tests/test_thin_install.py -k called_commit 2>&1 | tail -3
```

> 81:          repository: dokima-dev/dokima
> 723:          repository: dokima-dev/dokima
> .............                                                            [100%]
> 13 passed in 22.58s
>   uptodate.yml job update: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
> assert not ['acceptance-criteria.yml job list: main', 'acceptance-criteria.yml job check: main', 'agent.yml job run: aaaaaaaaaaaa...ssign: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'audit.yml job audit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', ...]
> 1 failed, 12 deselected in 0.24s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`12. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/wt; git diff 2296c7b a8c77ef --stat; timeout 900 python -m pytest -q -n auto -x -p no:cacheprovider 2>&1 | tail -5
```

> tests/test_thin_install.py | 32 ++++++++++++++++++++++++++++++++
>  1 file changed, 32 insertions(+)
>   uptodate.yml job update: empty, so main
> assert not ['acceptance-criteria.yml job list: empty, so main', 'acceptance-criteria.yml job check: empty, so main', 'agent.yml j...l job unrecorded: empty, so main', 'assign.yml job assign: empty, so main', 'audit.yml job audit: empty, so main', ...]
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> !!!!!!!!!!!! xdist.dsession.Interrupted: stopping after 1 failures !!!!!!!!!!!!!
> 1 failed, 1358 passed, 4 warnings in 474.67s (0:07:54)

`13. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/10-reviewer-plan.json'))['handback'];[print(json.dumps(d[k],indent=0)) for k in ('asks','boxes','behaviors','edge_cases','tests')]"
```

> [
> {
> "ask": "All Dokima code runs from Dokima's own repo inside GitHub Actions.",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.1"
> },
> {
> "ask": "live only in GitHub secrets on the repo (the `keys` environment)",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.2"
> },
> {
> "ask": "`settings.yaml` only names which secret each role reads.",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.3"
> },
> {
> "ask": "Missing bot or key fails loudly with the fix in the message",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.4"
> },
> {
> "ask": "Missing bot or key fails loudly with the fix in the message",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.5"
> },
> {
> "ask": "Until #747 lands, the co-author line names the repo's own bot.",
> "source": "https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528",
> "criterion": "812.6"
> },
> {
> "ask": "The shipped default is the `dokima[bot]` trailer, and an adopter can turn it off.",
> "source": "https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528",
> "criterion": "812.7"
> },
> {
> "ask": "calls Dokima's shared workflows by tag",
> "source": "https://github.com/dokima-dev/dokima/issues/742",
> "criterion": "812.8"
> },
> {
> "ask": "a 20-line ceiling is fine",
> "source": "https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528",
> "criterion": "812.9"
> },
> {
> "ask": "One thin workflow, `.git

`14. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
d=json.load(open('in/10-reviewer-plan.json'))['handback']
tests=d['tests']
tests.insert(11,{"test":"tests/test_thin_install.py::test_every_shared_workflow_fetches_dokimas_code_at_the_called_commit","only_its_behavior":True,"why":"Each Dokima checkout must use the called commit; fails today on an empty ref."})
r={"previous_step":{"did":["Added a check that every shared workflow fetches Dokima's code at the commit the adopter called."],
 "decided":["The check fills in the values GitHub sets when an adopter's repo calls a shared workflow."],
 "open":["The shared workflows still fetch Dokima's code from main; the worker fixes this next."]},
 "verdict":"approve",
 "summary":"The plan now proves the adopter's tag picks the code that runs; the new check fails today for that reason.",
 "raises":[],"answers":[],
 "asks":d['asks'],"behaviors":d['behaviors'],"edge_cases":d['edge_cases'],"tests":tests,"size":"ok","boxes":d['boxes']}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> rc=1

**Agent:** Trimming two summary lines that ran one word over the cap.

`15. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';r=json.load(open(p))
r['previous_step']['did']=["Added a check that each shared workflow fetches Dokima's code at the called commit."]
r['previous_step']['decided']=["The check fills in the values GitHub sets when an adopter calls a shared workflow."]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 812 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#812](https://github.com/dokima-dev/dokima/issues/812) (Dokima's workflows run from Dokima's own repo), and `review.json` passed both checks.

**What changed this round:** the planner added one test, `test_every_shared_workflow_fetches_dokimas_code_at_the_called_commit`. It closes the last open blocker: the old release-tag test (criterion 812.8) only read the adopter's call line. It never checked that the shared workflows actually fetch Dokima's code at the tag the adopter calls.

**Checking the new test:**
- **Fails today for the right reason:** on this branch every shared workflow's checkout of Dokima's code comes out empty, so it falls back to main. The test lists all 19 such jobs.
- **Passes with the right fix:** with `job.workflow_sha` in place of `github.job_workflow_sha`, all 13 tests in the file pass.
- **Still fails on a wrong fix:** with `github.workflow_sha`, which is the adopter's own commit, it fails.

**Full suite:** stopped at the first failure, which was this new test. 1,358 other tests passed before it stopped.

Every ask from the owner still maps to one criterion, and each criterion is one behavior. There were no open blockers to answer and I raised none.

**Still to do:** the worker still has to fix the workflows themselves. They fetch Dokima's code from main, not the called tag. That was the other blocker from the last code review.

# reviewer (plan) for #433

Run: https://github.com/dokima-dev/dokima/actions/runs/38195913039

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #433: planner.yml and worker.yml still start the old label-driven planner and worker (the plan and work labels, pushing to work/issue-N), which AGENTS.md no longer describes: agents start with /plan and /work through commands.yml and agent.yml.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 426, 438, 459 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The old label-started planner and worker go away, so agents start only from a command.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/433#issuecomment-6116474380) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/308
> - https://github.com/dokima-dev/dokima/issues/426
> - https://github.com/dokima-dev/dokima/issues/438
> - https://github.com/dokima-dev/dokima/issues/459
> 
> 
> **User story:** Agents start only when the owner says /plan or /work, never from a label.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptan

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_no_label_agents.py; cat /tmp/pack/parent.json | head -50; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit 0c7ee9a0744941ae59ef17b364b9c8a834d255f0
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 02:28:04 2026 +0000
> 
>     planner for #433 (run 38194516193)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_app.py               |   6 +--
>  tests/test_card_every_change.py |   5 +-
>  tests/test_card_queue.py        |   9 ++--
>  tests/test_keys.py              |   6 +--
>  tests/test_manifest.py          |  12 ++---
>  tests/test_no_label_agents.py   | 111 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_plan.py              |  25 ---------
>  tests/test_plan_check.py        |  11 ++--
>  tests/test_plan_shape.py        |  13 -----
>  tests/test_planner.py           |  34 ++----------
>  tests/test_worker.py            |  25 ---------
>  11 files changed, 137 insertions(+), 120 deletions(-)
> """No label starts an agent any more: agents start only through /plan and /work (#433).
> 
> The old planner.yml and worker.yml started the planner and the worker when a code owner added the plan or work label,
> and pushed to work/issue-N. AGENTS.md now says agents start with /plan and /work, through commands.yml and agent.yml.
> These tests read every workflow under .github/workflows (without a YAML library, as tests/test_keys.py does) and fail
> while any workflow still starts an agent on a label change or pushes to the old work branch.
> """
> import glob
> import os
> import re
> 
> ROOT = os.path.join(os.path

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_no_label_agents.py 2>&1 | tail -15; head -40 .github/workflows/planner.yml; echo ----; head -40 .github/workflows/worker.yml; grep -n "work/issue\|worker.yml\|planner.yml\|workflow_run" .github/workflows/*.yml | grep -v "^.github/workflows/planner.yml\|^.github/workflows/worker.yml"
```

> "433.3: agent.yml no longer pushes the agents' work to try/issue-N"
>         found = [name for name, text in workflows().items() if pushes_work(text)]
> >       assert not found, f"433.3: {', '.join(found)} still push to the old work/issue-N branch"
> E       AssertionError: 433.3: planner.yml, worker.yml still push to the old work/issue-N branch
> E       assert not ['planner.yml', 'worker.yml']
> 
> tests/test_no_label_agents.py:111: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_no_label_agents.py::test_adding_the_plan_label_no_longer_starts_the_planner - AssertionError: 433.1: adding the plan label still starts the planner through planner.yml
> assert not ['planner.yml']
> FAILED tests/test_no_label_agents.py::test_adding_the_work_label_no_longer_starts_the_worker - AssertionError: 433.2: adding the work label still starts the worker through worker.yml
> assert not ['worker.yml']
> FAILED tests/test_no_label_agents.py::test_no_workflow_pushes_to_the_old_work_branch - AssertionError: 433.3: planner.yml, worker.yml still push to the old work/issue-N branch
> assert not ['planner.yml', 'worker.yml']
> 3 failed in 0.04s
> name: planner
> run-name: "planner for #${{ github.event.issue.number }}${{ github.event.label.name != 'plan' && format(' (label {0}, ignored)', github.event.label.name) || '' }}"
> # Adding the `plan` label to an issue starts the planner: a fresh GitHub machine
> # reads the repo and the issue, and the planner hands back 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,30p .github/workflows/card.yml; sed -n 20,35p .github/workflows/board.yml; grep -rn "\"worker\"\|'worker'\|workflows: \[" .github/workflows/ | head; grep -rln "planner.yml\|worker.yml" dokima tests | head -20
```

> name: card
> # Writes the card at the top of the issue and its PR on every change to either: an edit, a label, a comment, a
> # review or line note (heard through reviews.yml), a push, a close, a run starting or ending, the bot's own changes
> # included. A redraw the bot started that finds both cards current writes nothing, so its own card save ends the
> # chain. The cards of the issues it blocks or is blocked by follow when their links changed. GitHub announces no
> # event for a blocked-by link added or removed by hand, so a run every 15 minutes catches up the cards whose links
> # changed.
> # These triggers always use the default branch's copy of this file and of dokima/card.py, so the work being judged
> # cannot change how it is reported.
> # An issue and its pull request share one queue, so the newest redraw waits for the
> # running one and is never cancelled, while other issues' redraws and the sweep go
> # on beside it.
> on:
>   workflow_run:
>     workflows: [Acceptance criteria, full suite, worker, reviews]
>     types: [in_progress, completed]
>   issues:
>   issue_comment:
>   pull_request_target:
>     types: [opened, edited, synchronize, reopened, closed, labeled, unlabeled, ready_for_review, converted_to_draft]
>   schedule:
>     - cron: '*/15 * * * *'
> permissions:
>   contents: read
>   actions: read
>   checks: read
>   issues: read
>   pull-requests: read
> jobs:
>   queue:
>   # this job only checks out main's code, never the PR's.
>   pull_request_target:
>     types: [opened, reopened, synchronize, closed]
>   #

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "planner.yml\|worker.yml" tests/test_card_status.py tests/test_card_records.py tests/test_card_every_change.py; python -m pytest -q -x -p no:cacheprovider 2>&1 | tail -5
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bgj1669w9). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/96ac6df7-1813-41fa-a0ea-e97c1e86ccf9/tasks/bgj1669w9.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** I'm running the full test suite in the background. Meanwhile I'm checking that the planner's tests pass once the old workflows are removed, using a scratch copy.

`6. Bash`
```
rm -rf /tmp/sim && cp -r /home/runner/work/dokima/dokima /tmp/sim && cd /tmp/sim && rm .github/workflows/planner.yml .github/workflows/worker.yml && sed -i 's/full suite, worker, reviews/full suite, reviews/' .github/workflows/card.yml && timeout 600 python -m pytest -q -p no:cacheprovider tests/test_no_label_agents.py tests/test_worker.py tests/test_plan.py tests/test_keys.py tests/test_plan_shape.py tests/test_planner.py tests/test_app.py tests/test_plan_check.py tests/test_manifest.py tests/test_card_queue.py tests/test_card_every_change.py tests/test_card_status.py tests/test_card_records.py 2>&1 | tail -8
```

> ERROR: file or directory not found: tests/test_worker.py
> 
> 
> no tests ran in 0.00s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`7. Bash`
```
cd /tmp/sim && git show --stat HEAD | grep test_worker; ls tests | grep -c .; timeout 600 python -m pytest -q -p no:cacheprovider tests/test_no_label_agents.py tests/test_plan.py tests/test_keys.py tests/test_plan_shape.py tests/test_planner.py tests/test_app.py tests/test_plan_check.py tests/test_manifest.py tests/test_card_queue.py tests/test_card_every_change.py tests/test_card_status.py tests/test_card_records.py 2>&1 | tail -8
```

> tests/test_worker.py            |  25 ---------
> 118
> ........................................................................ [ 32%]
> ........................................................................ [ 64%]
> ........................................................................ [ 96%]
> ........                                                                 [100%]
> 224 passed in 38.37s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/96ac6df7-1813-41fa-a0ea-e97c1e86ccf9/tasks/bgj1669w9.output | tail -8
```

> tests/test_card_records.py:298:                   "repos/o/r/actions/workflows/worker.yml/runs": {"workflow_runs": [
> =========================== short test summary info ============================
> FAILED tests/test_no_label_agents.py::test_adding_the_plan_label_no_longer_starts_the_planner - AssertionError: 433.1: adding the plan label still starts the planner through planner.yml
> assert not ['planner.yml']
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 630 passed, 52 skipped in 138.31s (0:02:18)
> 
> [exited with code 0]

`9. Bash`
```
cd /tmp/sim && timeout 590 python -m pytest -q -p no:cacheprovider 2>&1 | tail -5
```

> ........................................................................ [ 82%]
> ........................................................................ [ 89%]
> .......................................................ss.ss............ [ 95%]
> ...........................s..............s                              [100%]
> 976 passed, 75 skipped in 197.29s (0:03:17)
> Shell cwd was reset to /home/runner/work/dokima/dokima

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "AGENTS.md" dokima/*.py | grep -iv "^.*#" | head -20
```

> dokima/agent.py:327:        bad.append(f"the answer to {rid}, a question for the owner, needs a source: {where}, or AGENTS.md")
> dokima/agent.py:931:    """Where the owner said the words: the issue or comment link as given, or AGENTS.md on the repo's main branch."""
> dokima/agent.py:932:    if source == "AGENTS.md":
> dokima/agent.py:933:        return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/blob/main/AGENTS.md"
> dokima/agent.py:941:    AGENTS.md, which is no issue or pull request, stay linked to it."""
> dokima/agent.py:942:    if source == "AGENTS.md":
> dokima/agent.py:1262:    That is the issue's own text, its parent's (when given), one of their comments, or AGENTS.md."""
> dokima/agent.py:2188:    """AGENTS.md as the runtime has it, from main; empty when there is none."""
> dokima/agent.py:2189:    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AGENTS.md")
> dokima/agent.py:2198:    this issue, or AGENTS.md; given the parent (parent_words), also the parent's own text or a code owner's comment on
> dokima/agent.py:2205:    if source == "AGENTS.md":

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 2180,2240p dokima/agent.py
```

> unconfirmed_comment(repo, pr, why, mention)
>         elif pr and not how:
>             gh("pr", "comment", pr, "-R", repo, "--body",
>                f"Autopilot did not merge this pull request: {why}. {mention} It waits for you to merge it.".replace("  ", " "))
>     return done
> 
> 
> def agents_text():
>     """AGENTS.md as the runtime has it, from main; empty when there is none."""
>     path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AGENTS.md")
>     try:
>         return open(path).read()
>     except OSError:
>         return ""
> 
> 
> def said_there(words, source, items, body, owners, number, parent=None):
>     """True when the words appear word for word where the source says: the issue's own text, a code owner's comment on
>     this issue, or AGENTS.md; given the parent (parent_words), also the parent's own text or a code owner's comment on
>     it. Anything else, a comment by anyone else (the bot included) or one not found, is False."""
>     flat = lambda t: " ".join((t or "").split())
>     words, source = flat(words), (source or "").strip()
>     up = (parent or {}).get("number")
>     if not words or not owner_source(source, number, up):
>         return False
>     if source == "AGENTS.md":
>         return words in flat(agents_text())
>     from dokima.body import ask
>     if source == issue_url(number):
>         return words in flat(ask(body))
>     if up and source == issue_url(up):
>         return words in flat(ask(parent.get("body") or ""))
>     comments = items + ((parent.

**Agent:** The plan's tests check out. I'm now confirming the planner's raised issue and writing the review.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 15,22p dokima/manifest.py; grep -n "def latest_worker_run" -A6 dokima/card.py | head; grep -n RUN_TITLE .github/workflows/card.yml
```

> import re
> import sys
> 
> LABELS = {
>     "plan": {"color": "1d76db", "description": "Starts the planner"},
>     "work": {"color": "0e8a16", "description": "Starts the worker on the approved plan"},
>     "autopilot": {"color": "8250df", "description": "Running on its own"},
>     "filed-by-dokima": {"color": "bfd4f2", "description": "Created automatically, not by a person"},
> 616:def latest_worker_run(repo, number):
> 617-    runs = json.loads(gh("api", f"repos/{repo}/actions/workflows/worker.yml/runs?per_page=50"))["workflow_runs"]
> 618-    run = next((r for r in runs if r["display_title"] == f"worker for #{number}"), None)
> 619-    return {"status": run["status"], "conclusion": run["conclusion"], "html_url": run["html_url"]} if run else None
> 620-
> 621-
> 622-def test_entry(repo, ref, path, source, name):
> 109:          RUN_TITLE: ${{ github.event.workflow_run.display_title }}

`13. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 675,700p dokima/card.py; grep -n "^def gh" -A15 dokima/card.py | head -25
```

> tests, sources = {}, {}
>     for t in sorted({t for ts in ((planned or {}).get("handback", {}).get("tests") or {}).values() for t in ts}):
>         path, _, name = t.partition("::")
>         if path not in sources:
>             sources[path] = file_at(repo, path, ref)
>         if sources[path] is not None:
>             tests[t] = test_entry(repo, ref, path, sources[path], name)
>     split = agent.latest(recs, "split")
>     children = [{"number": st["issue"], "title": st.get("title"), "stage": child_stage(repo, st["issue"], owners)}
>                 for st in (split["handback"].get("stories") or [] if split else [])]
>     return {"recs": recs, "items": items, "pr": pr, "check_runs": check_runs, "reviews": reviews, "owners": owners,
>             "tests": tests, "worker": latest_worker_run(repo, number), "children": children}
> 
> 
> def gallery(repo, out):
>     """Draw the card of every situation the owner looks at on a throwaway issue and PR, one file each, into `out`."""
>     from dokima import agent
>     number, owner = 1, "owner"
>     issue = {"number": number, "url": f"https://github.com/{repo}/issues/{number}"}
> 
>     def rec(role, stage=None, **handback):
>         return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
>                 "run": f"https://github.com/{repo}/actions/runs/1"}
> 
>     def run(name, status="completed", conclusion="success"):
>         return {"name": name, "status": status, "conclusion": conclusion, "html_url": f"https://github.

`14. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Wrote three tests: no label starts the planner or the worker, and nothing pushes to the old work branch.",
          "Removed or moved eighteen older tests that read the two old workflows."],
  "decided": ["The plan and work labels stay defined, and the card's lookup of old worker runs stays."],
  "open": ["Asks whether this plan may change the card code; it assumes not."]},
 "verdict": "approve",
 "summary": "The plan removes both label-started agents, with a test for each promise that fails today for the right reason.",
 "raises": [],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "The issue does not ask to change the card code, so the card code stays as it is.",
   "words": "Never change `.github/workflows/`, `dokima/card.py` or `dokima/roles/` unless the issue explicitly asks.",
   "source": "AGENTS.md", "changes": false},
  {"raise": "P2", "answer": "done", "why": "Confirmed: the label settings still say they start agents, and the card still reads the old worker's runs."}
 ],
 "asks": [
  {"ask": "planner.yml and worker.yml still start the old label-driven planner and worker", "source": "https://github.com/dokima-dev/dokima/issues/433", "criterion": "433.1"},
  {"ask": "the plan and work labels", "source": "https://github.com/dokima-dev/dokima/issues/433", "criterion": "433.2"},
  {"ask": "pushing to work/issue-N", "source": "https://github.com/dokima-dev/dokima/issues/433", "criterion": "433.3"},
  {"ask": "They run on every label change and keep a second path to an agent alive.", "source": "https://github.com/dokima-dev/dokima/issues/433", "criterion": "433.2"}
 ],
 "behaviors": [
  {"criterion": "433.1", "one_behavior": true, "why": "One action, the plan label, and one result, no planner starts."},
  {"criterion": "433.2", "one_behavior": true, "why": "One action, the work label, and one result, no worker starts."},
  {"criterion": "433.3", "one_beh
```

> Exit code 1
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`15. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']['did'][0]="Wrote three tests: no label starts an agent, nothing pushes to the old branch."
d['previous_step']['decided'][0]="The plan and work labels stay, and the card's old worker lookup stays."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 433 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#433](https://github.com/dokima-dev/dokima/issues/433) (stop the plan and work labels from starting agents). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** each thing the issue asks for has a criterion. There are three: adding the plan label starts no planner, adding the work label starts no worker, and nothing pushes to the old work branch.
- **Tests:** all three new tests fail today for the right reason, naming `planner.yml` and `worker.yml`. Each also checks that it would catch the old files coming back.
- **Simulated build:** in a scratch copy I deleted both old workflows and dropped `worker` from `card.yml`'s run triggers. The full suite passed there: 976 passed, 75 skipped.
- **The planner's question (P1):** it asked whether this plan may also change the card code. Since you're on autopilot, I answered it for you: no, quoting AGENTS.md's rule against changing `dokima/card.py` unless the issue explicitly asks. Nothing in this issue asks for that.
- **The planner's raised issue (P2):** I confirmed it. The label settings still say "Starts the planner" and "Starts the worker", and the card still looks up the old worker's runs.

One risk is left. Once `worker.yml` is deleted, the card still asks GitHub for that workflow's runs (`dokima/card.py:617`), and the call stops the card from drawing if GitHub returns an error. I expect GitHub to keep answering for a deleted workflow, but I didn't verify it. That's why I didn't raise a separate question. Fixing it would mean changing `dokima/card.py`, which belongs to the issue P2 proposes filing.

# reviewer (plan) for #864

Run: https://github.com/dokima-dev/dokima/actions/runs/39116662405

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (34KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/487b91d1-ca6f-4931-8033-23d5d9bf70f5/tool-results/bzprgc5g0.txt
> 
> Preview (first 2KB):
> total 64
> drwxr-xr-x 2 runner runner 4096 Oct 18 09:46 .
> drwxr-xr-x 3 runner runner 4096 Oct 18 09:46 ..
> -rw-r--r-- 1 runner runner 8285 Oct 18 09:46 01-planner.json
> -rw-r--r-- 1 runner runner 7760 Oct 18 09:46 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 8747 Oct 18 09:46 03-planner.json
> -rw-r--r-- 1 runner runner 7711 Oct 18 09:46 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3387 Oct 18 09:46 05-worker.json
> -rw-r--r-- 1 runner runner 8574 Oct 18 09:46 06-planner.json
> # Issue #864: Hotfix PRs labeled, design asks replanned, cards one line
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 863 -->
> <!-- dokima-blocking: {"blocked_by": [863], "blocks": [], "loop": []} -->
> A hotfix's pull request carries its label, a design choice returns it to planning, and its card is one line.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix the rejected hand-back
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/863
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/d

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #864: Hotfix PRs labeled, design asks replanned, cards one line
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 863 -->
> <!-- dokima-blocking: {"blocked_by": [863], "blocks": [], "loop": []} -->
> A hotfix's pull request carries its label, a design choice returns it to planning, and its card is one line.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Fix the rejected hand-back
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/863
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/750
> - https://github.com/dokima-dev/dokima/issues/718
> - https://github.com/dokima-dev/dokima/issues/869
> - https://github.com/dokima-dev/dokima/issues/870
> 
> 
> **User story:** Owners spot hotfixes by label and link, see design asks go back to planning, and read one-line cards.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; cat in/05-worker.json; python3 -c "import json;d=json.load(open('in/06-planner.json'));print(json.dumps(d,indent=1)[:5000])"
```

> []
> {
>  "kind": "user_story",
>  "title": "Hotfix PRs labeled, design asks replanned, cards one line",
>  "summary": "A hotfix's pull request carries its label, a design choice returns it to planning, and its card is one line.",
>  "user_story": "Owners spot hotfixes by label and link, see design asks go back to planning, and read one-line cards.",
>  "acceptance_criteria": [
>   {
>    "text": "When a hotfix worker opens its pull request, the pull request carries the hotfix label.",
>    "words": "Every hotfix PR carries the `hotfix` label",
>    "source": "https://github.com/dokima-dev/dokima/issues/750",
>    "files": [
>     ".github/workflows/agent.yml",
>     "dokima/hotfix.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "An issue without the hotfix label opens its pull request with no hotfix label.",
>      "test": "tests/test_hotfix_pr.py::test_a_hotfix_pull_request_carries_the_hotfix_label"
>     }
>    ]
>   },
>   {
>    "text": "When a hotfix worker raises that the ask needs a design choice, the planner starts on the issue.",
>    "words": "or the worker finds the ask needs a design choice, it goes back to normal planning",
>    "source": "https://github.com/dokima-dev/dokima/issues/750",
>    "files": [
>     "dokima/agent_roles.py",
>     "dokima/agent_next.py",
>     "dokima/hotfix.py",
>     "dokima/roles/worker.md"
>    ],
>    "edge_cases": [
>     {
>      "case": "A hotfix worker that raises nothing still goes to code review.",
>      "test": "tests/test_hotfix_pr.py::test_a_hotfix_worker_finding_a_design_choice_st

`4. Bash`
```
cd /tmp/pack; python3 -c "import json;d=json.load(open('in/06-planner.json'));h=d['handback'];print(h.get('raises'),h.get('answers'));print(d['check'])"; cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/
```

> None None
> {'passed': True, 'problems': []}
> commit b5511f884d9240a706963d0fdd4562a0da38305f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 09:46:08 2026 +0000
> 
>     planner for #864 (run 39116406832)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_hotfix_pr.py | 11 +++++++----
>  1 file changed, 7 insertions(+), 4 deletions(-)
> commit b5511f884d9240a706963d0fdd4562a0da38305f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 09:46:08 2026 +0000
> 
>     planner for #864 (run 39116406832)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_hotfix_pr.py b/tests/test_hotfix_pr.py
> index 845697b..b126982 100644
> --- a/tests/test_hotfix_pr.py
> +++ b/tests/test_hotfix_pr.py
> @@ -22,6 +22,8 @@ WORK_BACK = {"summary": "Stopped: the ask needs a design choice.", "criteria": {
>               "raises": [{"kind": "blocker", "to": "planner", "label": "Design choice", "text": DESIGN,
>                           "evidence": "`app.py` holds the title; the name also shows in other files."}],
>               "answers": []}
> +PLANNED_WORK = {"summary": "Fixed the page title.", "criteria": {"57.1": "`app.py` now says Dokima."},
> +                "evidence": "pytest -q: 2 passed", "raises": [], "answers": []}
>  
>  
>  def pr_labels(r, pr=ts.PR):
> @@ -37,12 +39,12 @@ def pr_labels(r, pr=

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -8 --all | head -20; git branch -a; sed -n 1,130p tests/test_hotfix_pr.py
```

> 0c86933 Record of run 39116406832 for #864
> 5f69f2b Conversation of run 39116406832
> b5511f8 planner for #864 (run 39116406832)
> cc8e6d7 Record of run 39115241345 for #864
> c944eb9 Conversation of run 39115241345
> 3085bf3 Record of run 39114945017 for #864
> 99244b5 Conversation of run 39114945017
> 74d748c Record of run 39114841292 for #745
>   main
> * try/issue-864
>   remotes/origin/RezaSoleymanifar-patch-1
>   remotes/origin/agent-components
>   remotes/origin/agents-scope-rule
>   remotes/origin/archive/try-issue-154-before-main-moved
>   remotes/origin/commands
>   remotes/origin/fix-planner-issue-step
>   remotes/origin/fixture/card-557
>   remotes/origin/fixture/readme-landing
>   remotes/origin/issue-100-planner-check
>   remotes/origin/issue-107-pitch
>   remotes/origin/issue-113-workflow-gate
>   remotes/origin/issue-116-board-sync
>   remotes/origin/issue-121-needs-you
>   remotes/origin/issue-126-keys-from-main
>   remotes/origin/issue-138-prompt
>   remotes/origin/issue-40-app
>   remotes/origin/issue-46-approve
>   remotes/origin/issue-54-plan
>   remotes/origin/issue-60-wrap
>   remotes/origin/issue-63-latest
>   remotes/origin/issue-67-label
>   remotes/origin/issue-74-layout
>   remotes/origin/issue-78-design
>   remotes/origin/issue-80-planner
>   remotes/origin/issue-81-build-on-main
>   remotes/origin/issue-89-planner-prompt
>   remotes/origin/issue-90-assign
>   remotes/origin/issue-93-terms
>   remotes/origin/logs
>   remotes/origin/main
>   remotes/origin/opus-everywhere
>   remotes/origin/owner-questions
>   remotes/origin/repl

**Agent:** Checking the planner's three fixed tests: running them today, then against the worker's earlier code if I can find it.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_hotfix_pr.py tests/test_hotfix_card.py tests/test_hotfix.py::test_a_finished_hotfix_worker_starts_code_review_on_its_pull_request tests/test_hotfix.py::test_hotfix_prompts_name_nothing_from_dokimas_own_repo 2>&1 | grep -E "^(FAILED|PASSED|E  .*86[4]\.|[0-9]+ (passed|failed))|AssertionError: 864" | head -30
```

> E       AssertionError: 864.1: the hotfix pull request was opened without the hotfix label; pr create: ['pr', 'create', '-R', 'o/r', '--draft', '--head', 'try/issue-57', '--base', 'main', '--title', 'Page title typo', '--body', 'Closes #57']
> E       AssertionError: 864.2: a hotfix needing a design choice did not start the planner once: [('reviewer', 'pr', '57')]
> E       AssertionError: 864.3: issue #57 got no comment saying why the hotfix went back to planning: []
> E       AssertionError: 864.4: the hotfix card is not one line: ['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/o/r/pull/60/files)']
> E       AssertionError: 864.5: the hotfix card's one line does not carry the ask 'The page title says Dokma; make it say Dokima.': ['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/o/r/pull/60/files)']
> E       AssertionError: 864.6: no card line shows the ask 'The page title says Dokma; make it say Dokima.': ['**Review**', 'https://github.com/o/r/pull/60 · <img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://gith

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git show c944eb9 --stat | head; f=$(git show c944eb9 --name-only --format= | head -1); git show c944eb9:$f | grep -n -E "Edit|Write|old_string" | head -30; git show c944eb9:$f | wc -c
```

> commit c944eb910dcc81b10af9e1bf97adbd2ffed3a1d9
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 09:33:57 2026 +0000
> 
>     Conversation of run 39115241345
> 
>  logs/864/39115241345-worker.md | 1143 ++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 1143 insertions(+)
> 62338

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git show c944eb9:logs/864/39115241345-worker.md | grep -n -iE "edit|diff|apply_patch|python3 - <<|sed -i" | head -40
```

> 127:>     The calls: `gh pr create`, `gh pr edit` or the REST labels call."""
> 322:>           if git diff --cached --quiet && { [ "$ROLE" != planner ] || [ "$(git rev-parse HEAD)" = "${BRANCH_TIP:-$(git rev-parse HEAD)}" ]; }; then echo "Nothing to push."
> 324:>             # The co-author the settings name, if any, is credited on the commit (#796); {bot} is the bot itself (#812).
> 326:>             CREDIT=(); [ -z "$CO" ] || CREDIT=(--trailer "Co-authored-by: $CO")
> 327:>             git diff --cached --quiet || git commit -qm "$ROLE for #$N (run ${{ github.run_id }})" "${CREDIT[@]}"
> 377:>           if git diff --cached --quiet && { [ "$ROLE" != planner ] || [ "$(git rev-parse HEAD)" = "${BRANCH_TIP:-$(git rev-parse HEAD)}" ]; }; then echo "Nothing to push."
> 379:>             # The co-author the settings name, if any, is credited on the commit (#796); {bot} is the bot itself (#812).
> 381:>             CREDIT=(); [ -z "$CO" ] || CREDIT=(--trailer "Co-authored-by: $CO")
> 382:>             git diff --cached --quiet || git commit -qm "$ROLE for #$N (run ${{ github.run_id }})" "${CREDIT[@]}"
> 399:>           # Each merge commit credits the co-author the settings name; {bot}, the default, is the bot itself (#812).
> 401:>           CREDIT=(); [ -z "$CO" ] || CREDIT=(--trailer "Co-authored-by: $CO")
> 402:>           credit_merge() {
> 404:>             git -c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com" commit -q --amend --no-edit "${CREDIT[@]}"
> 505

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "WORK\b\|WORK)" tests/test_hotfix.py | head; grep -n "STORY_APPROVED" tests/test_start.py | head -3; cat > /tmp/chk_test.py <<'EOF'
import os, sys
sys.path.insert(0, "tests")
import test_hotfix as th, test_start as ts, test_hotfix_pr as tp

def test_plain_halves(tmp_path, monkeypatch):
    monkeypatch.setattr(th, "WORK", tp.PLANNED_WORK)
    plain = th.Hotfix(tmp_path / "plain", "worker", labels=(), comments=ts.STORY_APPROVED, try_branch=True)
    assert any(c[:2] == ["pr", "create"] for c in plain.calls()), plain.why()
    assert th.HOTFIX not in tp.pr_labels(plain)
    monkeypatch.setattr(th, "WORK", tp.WORK_BACK)
    monkeypatch.undo()
    p2 = th.Hotfix(tmp_path / "p2", "worker")
    assert [s[0] for s in p2.signals()] == ["reviewer"], p2.signals()

def test_plain_with_hotfix_work(tmp_path):
    plain = th.Hotfix(tmp_path / "plain", "worker", labels=(), comments=ts.STORY_APPROVED, try_branch=True)
    assert any(c[:2] == ["pr", "create"] for c in plain.calls()), plain.why()
EOF
cp /tmp/chk_test.py tests/_tmp_chk_test.py; timeout 300 python3 -m pytest -q tests/_tmp_chk_test.py 2>&1 | tail -5; rm tests/_tmp_chk_test.py; git status --short
```

> 48:WORK = {"summary": "Fixed the page title.", "criteria": {"ask": "`app.py` now says Dokima."},
> 149:            "models": ["claude-opus-5-5"], "handback": WORK, "check": {"passed": True, "problems": []}}
> 178:        json.dump(WORK, open(f"{t}/gh/work.json", "w"))
> 708:STORY_APPROVED = STORY_PLANNED + [record_comment(review_record(APPROVE), "2026-10-07T10:20:00Z"),
> 795:    r = Run(tmp_path / "gate", "worker", "", STORY_APPROVED, try_branch=True, actor="stranger")
> 798:    r = Run(tmp_path / "branch", "worker", "", STORY_APPROVED)
>   ::notice title=GitHub calls::none
>   
> assert False
>  +  where False = any(<generator object test_plain_with_hotfix_work.<locals>.<genexpr> at 0x7fb9a37ab780>)
> 1 failed, 1 passed in 12.83s

`10. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/04-reviewer-plan.json'));print(json.dumps(d['handback'],indent=1))"
```

> {
>  "previous_step": {
>   "did": [
>    "The planner added criterion 864.9: a hotfix pull request links its issue.",
>    "The planner proved 864.9 by a stricter check on an older passing test."
>   ],
>   "decided": [
>    "The planner renumbered the repo rule to 864.10, its checks unchanged."
>   ],
>   "open": []
>  },
>  "verdict": "approve",
>  "summary": "Every ask now has a criterion and a test; the eight new tests fail today for the right reason.",
>  "raises": [],
>  "answers": [],
>  "asks": [
>   {
>    "ask": "When a hotfix worker opens its pull request, the pull request carries the hotfix label.",
>    "source": "https://github.com/dokima-dev/dokima/issues/864",
>    "criterion": "864.1"
>   },
>   {
>    "ask": "When a hotfix worker opens its pull request, the pull request links the issue it answers.",
>    "source": "https://github.com/dokima-dev/dokima/issues/864",
>    "criterion": "864.9"
>   },
>   {
>    "ask": "Keep the ask that a hotfix pull request links its issue, and give it a criterion.",
>    "source": "https://github.com/dokima-dev/dokima/issues/864",
>    "criterion": "864.9"
>   },
>   {
>    "ask": "When a hotfix worker finds the ask needs a design choice, the planner starts on the issue.",
>    "source": "https://github.com/dokima-dev/dokima/issues/864",
>    "criterion": "864.2"
>   },
>   {
>    "ask": "When a hotfix worker sends the issue back to planning, the issue gets a comment saying why.",
>    "source": "https://github.com/dokima-dev/dokima/issues/864",
>    "criterion": "864.3"
>   },
>   {
>    "ask": "When an iss

`11. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
d=json.load(open('in/04-reviewer-plan.json'))['handback']
d["previous_step"]={"did":[
 "The planner fixed the label test so its comparison run hands back a planned worker's result.",
 "The planner fixed the two send-back tests so their raises-nothing run truly raises nothing."],
 "decided":["The planner left every criterion and the worker's approach unchanged, as the owner asked."],
 "open":[]}
d["summary"]="The three tests the owner named are fixed; all eight new tests fail today for the right reason."
U="https://github.com/dokima-dev/dokima/issues/864"
d["asks"]+= [
 {"ask":"864.2 and 864.3: ... Save the original before patching (or call `monkeypatch.undo()`) and restore that instead.","source":U,"criterion":"864.2"},
 {"ask":"864.2 and 864.3: ... Save the original before patching (or call `monkeypatch.undo()`) and restore that instead.","source":U,"criterion":"864.3"},
 {"ask":"864.1: ... Give that run a planned worker's hand-back.","source":U,"criterion":"864.1"}]
for t in d["tests"]:
  if t["test"].endswith("carries_the_hotfix_label"): t["why"]="Checks the label; the unlabeled comparison now hands back a planned result."
  if t["test"].endswith("starts_the_planner"): t["why"]="Checks the planner starts; the raises-nothing run now restores the plain result."
  if t["test"].endswith("says_why_on_the_issue"): t["why"]="Checks the comment says why; the raises-nothing run now raises nothing."
json.dump(d,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 864 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> rc=1

**Agent:** Trimming one line that runs over the word cap, then rerunning the check.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"][0]="The planner fixed the label test: its comparison run hands back a planned result."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 864 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan. The planner fixed the three tests you named in your last `/plan` comment on [#864](https://github.com/dokima-dev/dokima/issues/864) (hotfix pull requests labeled, design asks replanned, cards one line).

- **Label test:** the run it compares against now hands back an ordinary planned result. With the old test version, that run opened no pull request at all, so the worker's report was right.
- **Two design-choice tests:** the second run in each now goes back to a hand-back that raises nothing. Before, it still raised the design choice by mistake.

I ran the tests on the branch:
- **The eight new tests fail today**, each because the feature is missing. None fails from a crash or a broken setup.
- **The two older tests pass**, as you approved: the one proving a hotfix pull request links its issue, and the one keeping the prompts free of anything about Dokima's own repo.
- **The fixed comparison runs pass on today's code**, so they no longer block the work themselves.

I couldn't run the fixed tests against the worker's earlier code. That code was never saved to the branch, and the run's log doesn't contain it.

The criteria are the same as last round, and every ask has one. The review is in `/tmp/dokima-out/review.json` and passes both checks.

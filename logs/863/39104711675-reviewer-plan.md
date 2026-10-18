# reviewer (plan) for #863

Run: https://github.com/dokima-dev/dokima/actions/runs/39104711675

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #863: Hotfix issues build from their text and get reviewed
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [864], "loop": []} -->
> An issue labeled hotfix is built from its own text, then code-reviewed and gated, with no plan.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/864
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/748
> - https://github.com/dokima-dev/dokima/issues/857
> 
> 
> **User story:** A small fix labeled hotfix is built straight from its text, reviewed and gated, with no plan.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a code owner says work on an issue labeled hotfix, the worker starts with no plan.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-863/tests/test_hotfix.py#L232"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('01-planner.json'));print(list(d.keys()));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; ls /tmp/pack; ls /home/runner/work/dokima/dokima; grep -rl "hotfix" /home/runner/work/dokima/dokima --include=*.md | head
```

> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39103774786",
>  "commit_before": "ccbebe20951336dbdfb7da7800bf77e892c34308",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 869622,
>   "turns": 56,
>   "cost_usd": 4.738848399999999,
>   "tokens_in": 8160167,
>   "tokens_out": 63001
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/863/39103774786-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39103774786",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/863#issuecomment-6246514046"
> }
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> AGENTS.md
> CHANGELOG.md
> CLAUDE.md
> LICENSE
> README.md
> docs
> dokima
> rules
> tests
> tools
> /home/runner/work/dokima/dokima/dokima/roles/planner.md
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /tmp/pack; cat owner_words.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:12000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/750": "Owner decision 2026-10-15, rescoped by the owner 2026-10-18 (\"yes 750 hotfix\"): the fast lane is a **label**, not a verb, so it works on autopilot now, before the `@dokima` grammar (#748). #748 can later add `@dokima hotfix` as one more way to put the label on.\n\n**What**\n- An issue labeled `hotfix` skips planning and plan review. When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text: the text is the whole ask.\n- Code review still runs and judges the diff against the issue's text; it is the judgment gate. All tests and the merge gate still run, as for any pull request.\n- The worker may add or change a small test that pins the fix (as #856 pinned the install docs' check names).\n- Only small asks take the lane: a change the issue names in a sentence or two, touching few files. When code review finds the change bigger than the ask, or the worker finds the ask needs a design choice, it goes back to normal planning, saying why.\n- The card shows one line: the ask, the PR, the review verdict, the gate.\n- Every hotfix PR carries the `hotfix` label and links the issue it answers.\n\n**The loop it completes:** a worker raises a problem; the raise files as an issue that blocks the parent (#268); someone labels it `hotfix`; it lands; the parent restarts by itself when its blocker merges (#213). Hotfixes accumulate as a labeled, linked record; many in one 

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'));
for i in d: print(i.get('number'), i.get('title'))
for i in d:
  if i.get('number')==864: print(json.dumps(i,indent=1)[:5000])
"
```

> 864 Hotfix pull requests labeled, linked and shown in one line
> 863 Hotfix issues build from their text and get reviewed
> 862 Every test is tagged merge gate, nightly or archive, and plan review checks the tag
> 860 The audit workflow's comment still says the audit fails without a board, which stops being true here.
> 859 The card follows the repo's own CI
> 858 The audit spares the repo's checks and a missing board
> 857 Pull requests with no plan pass unless Dokima opened them
> 855 A parent not on autopilot stays open when its last sub-issue's close run is dropped, since only autopilot parents are swept.
> 842 The card says Needs you while autopilot waits for blockers
> 836 A test's push to its temp repo fails at random on the runner
> 834 Criteria sharing only a markdown file become separate stories, so a docs-only story cannot hold two.
> 826 The reviewer's prompt never says the edges box is an object keyed by criterion, so reviewers may guess wrong and be rejected.
> 825 The wiki sync writes the bot placeholder as it is, and commits on the logs branch credit no co-author.
> 800 Any-size input: break documents into features, stories and criteria, with caps the planner knows
> 799 Leaner tests: study, fix brittle tests, one shared test surface, then reviewer rules for test quality
> 791 No shipped default value is left in Dokima's code
> 790 Word caps come from settings
> 789 The bot Dokima recognizes comes from settings
> 788 An agent's turn limit comes from settings
> 786 Updating pull requests waits on t

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git branch -a; git log --oneline -3 --all | head; git show --stat HEAD | head -20; ls docs rules
```

> main
> * try/issue-863
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
>   remotes/origin/replan-base
>   remotes/origin/replan-own-changes
>   remotes/origin/reviewer-role
>   remotes/origin/river
>   remotes/origin/runtime-from-main
>   remotes/origin/split-filing
>   remotes/origin/try/issue-135
>   remotes/origin/try/issue-139
>   remotes/origin/try/issue-154
>   remotes/origin/try/issue-156
>   remotes/origin/try/issue-157
>   remotes/origin/tr

**Agent:** Reviewing the plan for #863: reading the planner's tests now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_hotfix.py
```

> """A hotfix issue is built from its text, then reviewed and gated as usual (#863).
> 
> These tests run the agent workflow (.github/workflows/agent.yml) the way GitHub runs it, on the machine from
> test_start.py, with the fake GitHub of test_autopilot_close.py (labels, sub-issues, blocked-by links, comments,
> signals). A thin layer in front of that fake also answers what a hotfix's run needs: `gh pr create` (noted, and the
> pull request #60 exists from then on), `gh run download` (a session log of the worker's run), the merge gate's reads
> of pull request #60 (its head commit, its draft flag, `gh pr ready`), main's branch rule (it requires the `all tests`
> check) and the check runs on the head commit (all green). A `--jq` filter on an issue read is applied with jq.
> 
> The issue is #57 in repo o/r, labeled `hotfix`, its text the owner's ask: ASK. Main holds app.py (the title with a
> typo), lib/ (nothing yet) and an older test, tests/test_old.py. The stand-in agent keeps a copy of its pack and its
> prompt as it found them. As the worker it fixes app.py, adds lib/title.py, adds tests/test_app.py, changes
> tests/test_old.py, and hands back a work.json whose one line is keyed `ask` (a hotfix has no plan to number its
> criteria, so only the shape of its work.json is checked). As the code reviewer it hands back the review the test
> chose: an approval, or a block raising a blocker for the planner because the change is bigger than the ask.
> 
> The autopilot test runs the close and command workflows on t

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_hotfix.py -x -q 2>&1 | tail -5; timeout 900 python -m pytest -q tests/test_hotfix.py 2>&1 | grep -E "^E .*863|passed|failed" | head -40
```

> assert False
>  +  where False = agent_started()
>  +    where agent_started = <test_hotfix.Hotfix object at 0x7f2893b0f740>.agent_started
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> E       AssertionError: 863.1: `/work` on a hotfix issue with no plan did not start its worker; result failure, failed step 'Starting branch':
>         assert not m.failed, f"863.2 (close): a workflow failed when #110 closed: {m.failures}\n{m.tail()}"
> E       AssertionError: 863.2 (close): the unblocked hotfix #101 did not get exactly one worker; workers: []
> E       AssertionError: 863.3: the hotfix worker never started; result failure, failed step 'Starting branch':
> >       assert not r.failed, f"863.4: the hotfix worker's run failed; {r.why()}"
> E       AssertionError: 863.4: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E        +  where True = <test_hotfix.Hotfix object at 0x7f15b4893cb0>.failed
> >       assert not r.failed, f"863.5: the hotfix worker's run failed; {r.why()}"
> E       AssertionError: 863.5: the hotfix worker's run failed; result failure, failed step 'Starting branch':
> E        +  where True = <test_hotfix.Hotfix object at 0x7f15b4abac30>.failed
> E       AssertionError: 863.6: code review of the hotfix never started; result failure, failed step 'Build the starting pack':
> E         ::error title=No pack::No passed plan on the issue yet, or (for the worker) no plan review approving the newest plan.
> E         ::error ti

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "boxes\|edges\|poor_tests" dokima/agent*.py | head -30
```

> dokima/agent.py:49:    AUTOPILOT_START_LINE, link_edges, loop_through, named, FILED_LABEL, file_issues, record_links, set_title,
> dokima/agent_autopilot.py:129:def link_edges(number, links):
> dokima/agent_autopilot.py:251:    want, had = link_edges(n, new), link_edges(n, old)
> dokima/agent_checks.py:227:         "conflicts": ("a", "b", "ask"), "edges": (), "poor_tests": ("test", "passes_with", "fix")}
> dokima/agent_checks.py:230:def problems_boxes(r, ids):
> dokima/agent_checks.py:231:    """Everything wrong with a review's six boxes (#819), each reason naming its box.
> dokima/agent_checks.py:233:    Every box is there, "none" or a list of whole entries (edges a line per criterion of the plan, covered or
> dokima/agent_checks.py:235:    boxes = r.get("boxes")
> dokima/agent_checks.py:236:    if not isinstance(boxes, dict):
> dokima/agent_checks.py:237:        return ["boxes must be an object holding the six boxes: " + ", ".join(BOXES) + "; a box with nothing in it says none"]
> dokima/agent_checks.py:240:        if box not in boxes:
> dokima/agent_checks.py:241:            bad.append(f"boxes has no {box} box: write none when there is nothing in it")
> dokima/agent_checks.py:243:        v = boxes[box]
> dokima/agent_checks.py:244:        if box == "edges":
> dokima/agent_checks.py:245:            bad += problems_edges(r, v, ids)
> dokima/agent_checks.py:252:        bad += problems_items(boxes, box, keys)
> dokima/agent_checks.py:264:def problems_edges(r, v, ids):
> dokima/agent_checks.py:265:    """Everyt

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote ten criteria for the hotfix lane, each with one test.", "All ten tests fail today because a hotfix still needs a plan."],
  "decided": ["A hotfix worker and its code review read the issue's text from the pack, with no plan."],
  "open": []
 },
 "verdict": "block",
 "summary": "Two gaps: no test shows failing tests stop a hotfix, and the any-repo prompt rule has no criterion.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "863.7: gate unproven", "text": "The test for 863.7 only runs with green checks, so a hotfix that skips its tests still passes. Add a red-check run beside it that must not pass the gate.", "evidence": "`tests/test_hotfix.py::test_an_approved_hotfix_passes_the_merge_gate_like_any_pull_request`; the fake gh always answers check runs `success`."},
  {"kind": "blocker", "to": "planner", "label": "No criterion: prompts", "text": "The owner asked to keep the prompts free of anything about Dokima's own repo. This plan edits the worker and reviewer prompts, and no criterion carries it.", "evidence": "Owner comment on #750 (issuecomment-6246479912); criteria 863.3, 863.6, 863.9 list `dokima/roles/worker.md` and `dokima/roles/reviewer.md`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "An issue labeled `hotfix` skips planning and plan review.", "source": "https://github.com/dokima-dev/dokima/issues/750", "criterion": "863.2"},
  {"ask": "By hand, the owner's `/work` starts a hotfix's worker.", "source": "https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246479912", "criterion": "863.1"},
  {"ask": "When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text", "source": "https://github.com/dokima-dev/dokima/issues/750", "criterion": "863.2"},
  {"ask": "the text is the whole ask.", "source": "https://github.com/dokima-dev/dokima/issues/750", "criterion": 
```

> Exit code 1
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/A hotfix worker and its code review read the issue.s text from the pack, with no plan./The hotfix worker and its code review read the issue text, no plan./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 863 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#863](https://github.com/dokima-dev/dokima/issues/863) (hotfix issues built from their text). It goes back to the planner with two fixes to make. The review is in `/tmp/dokima-out/review.json` and passes both checks.

I ran the planner's tests: all 10 fail today for the right reason. A hotfix still can't start without an approved plan.

**What's wrong:**
1. **Criterion 863.7 (the merge gate):** the test only runs with every check passing. So a hotfix path that skipped its tests would still pass. The fix is to run it again with the "all tests" check failing and require that the gate does not pass.
2. **An ask with no criterion:** in the [#750](https://github.com/dokima-dev/dokima/issues/750) (hotfix label builds a small fix) comment, the owner asked to "keep the prompts free of anything about Dokima's own repo, so they fit any repo". This plan changes the worker and reviewer prompts, but no criterion carries that rule.

The other nine criteria are each one behavior, and their tests check them by actually running the workflow.

These asks are left to [#864](https://github.com/dokima-dev/dokima/issues/864) (hotfix pull requests labeled, linked, shown in one line): the label and link on the pull request, the one-line card, and the worker handing back an ask that needs a design choice. I couldn't read #864's criteria, so I flagged the prompt rule here because this plan is the one editing those prompts.

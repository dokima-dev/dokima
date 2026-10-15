# reviewer (plan) for #668

Run: https://github.com/dokima-dev/dokima/actions/runs/38662971957

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #668: Stories sharing a code file take turns to build
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 667 -->
> <!-- dokima-blocking: {"blocked_by": [667], "blocks": [559], "loop": []} -->
> A story's build waits while another story sharing a code file is building, until that one merges.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/668#issuecomment-6181791562) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/667
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/665
> 
> 
> **User story:** Two stories never build the same code file at once, while planning and review go on freely.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-

`2. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; git show --stat HEAD; cat tests/test_build_turns.py
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38662178361",
>  "commit_before": "a2e94e1e645c47ea2f3ca54a3e7e441bb8f510c5",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 457808,
>   "turns": 36,
>   "cost_usd": 2.6452748000000006,
>   "tokens_in": 3404126,
>   "tokens_out": 43819
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/668/38662178361-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38662178361",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/668#issuecomment-6181791562"
> }
> commit a4c10e8eb5fe27065469f936a1dcc5bb721c5027
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 00:57:19 2026 +0000
> 
>     planner for #668 (run 38662178361)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_build_turns.py | 436 ++++++++++++++++++++++++++++++++++++++++++++++
>  tests/test_worker_pr.py   |   4 +-
>  2 files changed, 439 insertions(+), 1 deletion(-)
> """Stories sharing a code file take turns to build (#668, story 4 of #661).
> 
> A split files its stories as sub-issues of one parent, and each goes through the river on its own. Before #668 no
> build waited on another, so two stories changing the same code file could build it at once and clash. Now a story's
> build waits while another open story of the same parent that shares a code file w

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python3 -m pytest -q tests/test_build_turns.py 2>&1 | tail -30; sed -n 1,140p tests/test_worker_pr.py
```

> crit = '668.5', case = "#702's plan added dokima/shared.py"
> 
>     def assert_waits(t, n, holder, said, crit, case):
>         """#n's approval started no build, and its Next line names the holder of the turn."""
>         step, comment, out = said
> >       assert not step.startswith("start"), f"{crit} ({case}): #{n}'s build started while #{holder} holds the turn: {step!r}"
> E       AssertionError: 668.5 (#702's plan added dokima/shared.py): #702's build started while #701 holds the turn: 'start worker'
> E       assert not True
> E        +  where True = <built-in method startswith of str object at 0x7fe403472cb0>('start')
> E        +    where <built-in method startswith of str object at 0x7fe403472cb0> = 'start worker'.startswith
> 
> tests/test_build_turns.py:313: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_build_turns.py::test_a_story_sharing_a_code_file_builds_only_after_the_other_story_merges - AssertionError: 668.1 (autopilot): #702's build started while #701 holds the turn: 'start worker'
> assert not True
>  +  where True = <built-in method startswith of str object at 0x7fe40341c730>('start')
>  +    where <built-in method startswith of str object at 0x7fe40341c730> = 'start worker'.startswith
> FAILED tests/test_build_turns.py::test_planning_and_plan_review_never_wait_on_another_story - AssertionError: 668.2 (setup): #702's build was not held, so this test cannot show that only the build waits: 'start worker'
> assert not T

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; git show --stat HEAD; cat tests/test_build_turns.py
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python3 -m pytest -q tests/test_build_turns.py 2>&1 | tail -30; sed -n 1,140p tests/test_worker_pr.py
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38662178361",
>  "commit_before": "a2e94e1e645c47ea2f3ca54a3e7e441bb8f510c5",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 457808,
>   "turns": 36,
>   "cost_usd": 2.6452748000000006,
>   "tokens_in": 3404126,
>   "tokens_out": 43819
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/668/38662178361-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38662178361",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/668#issuecomment-6181791562"
> }
> commit a4c10e8eb5fe27065469f936a1dcc5bb721c5027
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 00:57:19 2026 +0000
> 
>     planner for #668 (run 38662178361)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_build_turns.py | 436 ++++++++++++++++++++++++++++++++++++++++++++++
>  tests/test_worker_pr.py   |   4 +-
>  2 files changed, 439 insertions(+), 1 deletion(-)
> """Stories sharing a code file take turns to build (#668, story 4 of #661).
> 
> A split files its stories as sub-issues of one parent, and each goes through the river on its own. Before #668 no
> build waited on another, so two stories changing the same code file could build it at once and clash. Now a story's
> build waits while another open story of the same parent that shares a code file w

> crit = '668.5', case = "#702's plan added dokima/shared.py"
> 
>     def assert_waits(t, n, holder, said, crit, case):
>         """#n's approval started no build, and its Next line names the holder of the turn."""
>         step, comment, out = said
> >       assert not step.startswith("start"), f"{crit} ({case}): #{n}'s build started while #{holder} holds the turn: {step!r}"
> E       AssertionError: 668.5 (#702's plan added dokima/shared.py): #702's build started while #701 holds the turn: 'start worker'
> E       assert not True
> E        +  where True = <built-in method startswith of str object at 0x7fe403472cb0>('start')
> E        +    where <built-in method startswith of str object at 0x7fe403472cb0> = 'start worker'.startswith
> 
> tests/test_build_turns.py:313: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_build_turns.py::test_a_story_sharing_a_code_file_builds_only_after_the_other_story_merges - AssertionError: 668.1 (autopilot): #702's build started while #701 holds the turn: 'start worker'
> assert not True
>  +  where True = <built-in method startswith of str object at 0x7fe40341c730>('start')
>  +    where <built-in method startswith of str object at 0x7fe40341c730> = 'start worker'.startswith
> FAILED tests/test_build_turns.py::test_planning_and_plan_review_never_wait_on_another_story - AssertionError: 668.2 (setup): #702's build was not held, so this test cannot show that only the build waits: 'start worker'
> assert not T

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "turn\b\|takes turns\|take turns\|clash" rules/ | head -30; ls dokima | head -80
```

> __pycache__
> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_github.py
> agent_next.py
> agent_records.py
> agent_roles.py
> app.json
> audit.py
> board.py
> body.py
> card.py
> checks.py
> fence.py
> icons
> manifest.py
> plan.py
> planner.py
> playthrough.py
> raises.py
> retry.py
> roles
> scan.py
> uptodate.py
> words.py

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "start worker\|def next_step\|def start_waiting\|def pack\|def closed\|\"closed\"" dokima/*.py | head -30
```

> dokima/agent_next.py:100:def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
> dokima/agent_autopilot.py:387:def start_waiting(repo, numbers, line=AUTOPILOT_LINE):
> dokima/agent_autopilot.py:395:        if any(b.get("state") != "closed" for b in blockers):
> dokima/agent_autopilot.py:406:    return sorted(b["number"] for b in blocked_by(repo, number) if b.get("state") != "closed")
> dokima/agent_autopilot.py:448:        if blockers and all(b.get("state") == "closed" for b in blockers):
> dokima/agent_autopilot.py:468:    if not subs or any(c.get("state") != "closed" for c in subs):
> dokima/agent_autopilot.py:518:        done = [p for p, cs in subs.items() if cs and issues[p]["state"] == "open" and all(c["state"] == "closed" for c in cs)]
> dokima/agent_autopilot.py:527:        if issues[n]["state"] == "closed" and n not in under:
> dokima/board.py:128:        """"open" or "closed" (a merged pull request is closed); raises subprocess.CalledProcessError when GitHub cannot say."""
> dokima/board.py:130:        return "closed" if self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues/{int(number)}").get("state") == "closed" else "open"
> dokima/board.py:146:                            "action": (it.get("fieldValueByName") or {}).get("name"), "closed": c["state"] != "OPEN",
> dokima/board.py:262:        place = DONE if board.state("issue", n) == "closed" else where(repo, owners, n, board.autopilot("issue", n))
> dokima/board.py:264:

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 100,200p dokima/agent_next.py | grep -n "worker\|parent" ; grep -n "next_step(" dokima/*.py; sed -n 600,630p dokima/agent_roles.py; sed -n 430,480p dokima/agent_autopilot.py
```

> 1:def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
> 5:    questions for the owner and the issue is not on autopilot. A worker hands to the reviewer. A review raising a
> 9:    plan goes to the worker and an approved split is filed, each ("start", role, stage, "autopilot"), once the plan
> 11:    as `parent()` gives them, its parent (a plan posted before #300: accepted every assumption); any other stops.
> 36:    if role == "worker":
> 61:            left = not_accepted(items, h, owners, body, number, parent) if plan.get("questions") else []
> 62:            left += unanswered(asked, items, h, owners, body, number, parent)
> 69:    # A worker's raise for the planner the code review settled goes on by itself, whatever the verdict on the code:
> 70:    # confirmed, to the planner; disagreed, back to the worker with the reviewer's why.
> 73:        return ("start", "planner" if "done" in words_ else "worker", "")
> 75:        return ("start", "worker", "")
> 79:            return ("start", "split" if plan.get("kind") == "feature" else "worker", "", "autopilot")
> 91:    return ("start", "planner" if stage == "plan" or for_planner(h) or "done" in words_ else "worker", "")
> dokima/agent_next.py:100:def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
> dokima/agent_next.py:215:    step = next_step(items[:at], records([items[at]])[0], owners, autopilot=lambda: True, body=body, number=number

**Agent:** Plan tests fail for the right reason; now checking the "replan after merge" choice against the rules.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "fresh planner\|blockers have all closed\|blocker.*merge\|plans again" rules/ AGENTS.md | head
```

> rules/flow.md:7:5. **Code review.** The reviewer starts by itself when the worker finishes. Every blocker names who fixes it: the worker for code, the planner for a test shown too weak. A block sends it back to the worker by itself, or to the planner when any blocker is the planner's; that test fix goes planner, plan review, worker, code review, and an approved re-plan whose criteria are unchanged goes straight to the worker, while one that changes any criterion, or comes after the owner spoke, waits for `/work`. No test runs on the pull request while it is a draft, so none races the code review. An approval runs the merge gate: a branch behind main is brought up to date with it, the pull request is marked ready, and every check main requires runs on that head; a check only skipped proves nothing. A new build turns it back into a draft first. Any check failing sends it back to the worker by itself, and counts toward the three blocks in a row like a blocking review; checks that never finish, or a branch GitHub will not update, stop for the owner and say why. Only a passed gate asks the owner to approve.
> rules/flow.md:10:On autopilot, the river runs a whole issue tree end to end and stops for the owner only where the owner must decide (planned, story 2 of #205); `/autopilot start` and `/autopilot stop` switch it on and off. On an issue on autopilot (its own `autopilot` label), an approved plan starts the worker and an approved split files its stories by themselves, each with on

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "plans again\|open blocker" dokima/*.py | head; sed -n 400,450p dokima/agent_roles.py
```

> dokima/agent_roles.py:482:                            # Nothing is built from a plan written before its blockers landed: the issue plans again.
> dokima/agent_roles.py:483:                            step = ("waiting", f"Nothing is built: the issue plans again by itself when {named(left)} close.")
> dokima/agent_records.py:857:        so = {True: "so the planner re-plans against the new main", False: "so the issue needs a re-plan",
>         repo = os.environ["GITHUB_REPOSITORY"]
>         # A run that never started stops for the owner, and a cancelled one stops, whatever the conversation says,
>         # so it is not read.
>         d, items, unread, undecided = {}, [], [], False
>         try:
>             with rate_limit_waited_once():
>                 d, items = ({}, []) if rec.get("role") in ("not-started", "cancelled") else conversation(repo, number)
>                 read, unread = [], []
> 
>                 def autopilot():
>                     # Read once, and only when the river's decision turns on it.
>                     if not read:
>                         unread.append(True)
>                         read.append(on_autopilot(repo, number, strict=True))
>                         unread.clear()
>                     return read[0]
>                 ups = []
> 
>                 def parent():
>                     # The parent's words, read once and only when an assumption cites somewhere other than this issue.
>                     if not ups:
>                         ups.append(parent_words(repo, numb

`11. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote five criteria and four new tests that fail today.", "It pinned the own pull request into main with an existing test."],
  "decided": ["After the other story merges, the waiting story plans again rather than building its old plan."],
  "open": ["It asked whether pinning the already true pull request rule is enough."]},
 "verdict": "approve",
 "summary": "The plan carries every ask, each with a test that fails today because the wait is missing.",
 "raises": [],
 "answers": [{"raise": "P1", "answer": "done", "why": "The owner asked only to keep it so and pin it, which the existing test does.", "words": "Each story already merges to main on its own pull request with no parent branch; keep it so and pin it.", "source": "https://github.com/dokima-dev/dokima/issues/668", "changes": false}],
 "asks": [
  {"ask": "The owner settled it: a story's turn ends when its pull request merges.", "source": "https://github.com/dokima-dev/dokima/issues/668", "criterion": "668.1"},
  {"ask": "planner and plan-review starts must not be touched by the wait.", "source": "https://github.com/dokima-dev/dokima/issues/668", "criterion": "668.2"},
  {"ask": "Markdown files never cause a wait.", "source": "https://github.com/dokima-dev/dokima/issues/668", "criterion": "668.3"},
  {"ask": "Each story already merges to main on its own pull request with no parent branch; keep it so and pin it.", "source": "https://github.com/dokima-dev/dokima/issues/668", "criterion": "668.4"},
  {"ask": "before the worker starts, the clash check runs again on the story's final file list.", "source": "https://github.com/dokima-dev/dokima/issues/668", "criterion": "668.5"}],
 "behaviors": [
  {"criterion": "668.1", "one_behavior": true, "why": "One wait, ending when the other story's pull request merges."},
  {"criterion": "668.2", "one_behavior": true, "why": "Planning and plan review start despite a 
```

> Exit code 1
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/After the other story merges, the waiting story plans again rather than building its old plan./Once the other story merges, the waiting story plans again, not building its old plan./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 668 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#668](https://github.com/dokima-dev/dokima/issues/668) (stories sharing a code file take turns to build). The hand-back is in `/tmp/dokima-out/review.json`, and both checks pass on it.

- **Asks:** each of the five asks in the issue maps to one criterion. None is missing.
- **Tests:** I ran the four new tests in `tests/test_build_turns.py`. All four fail today for the right reason: the second story's build starts while the first story is still building the shared file. The fifth criterion is already true, and an existing test in `tests/test_worker_pr.py` pins it: it fails if a story's pull request goes anywhere but main.
- **Size:** every criterion is one behavior, and each test checks only its own.
- **The planner's question:** it asked whether pinning "each story merges to main on its own pull request" with the existing test is enough. I answered yes for you, quoting your words from the issue: "keep it so and pin it." The answer changes nothing in how the system works or what it costs.
- **One choice the planner made:** once the other story merges, the waiting story plans again instead of building its old plan. You didn't ask for this. I accepted it because it follows the existing rule for blocked issues in `rules/flow.md`, which keeps plans from going stale while they wait.

I raised no blockers.

# reviewer (plan) for #601

Run: https://github.com/dokima-dev/dokima/actions/runs/38522013592

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> # Issue #601: A merge gate that keeps failing sends work to the worker again and again; the three-blocks stop counts only reviews.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 597, 600 -->
> <!-- dokima-blocking: {"blocked_by": [600], "blocks": [381, 602], "loop": []} -->
> Merge gate failures now count toward the three-blocks stop, so repeated failures reach the owner.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/600
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/381
> - https://github.com/dokima-dev/dokima/issues/602
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/620
> - https://github.com/dokima-dev/dokima/issues/597
> 
> 
> **User story:** A merge gate that keeps failing stops and asks the owner, instead of sending work back forever.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="accep

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_gate_stop.py; cat /tmp/pack/parent.json | head -50; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"
```

> """Merge gate failures count toward the three-blocks stop, so repeated failures reach the owner.
> 
> Today a merge gate that fails after the code review approved always starts the worker again, however many times it
> failed before, and the three-blocks stop counts only code reviews whose verdict blocks. So a gate that keeps failing
> sends the work to the worker again and again, and never reaches the owner (#601).
> 
> These tests chain real `python3 -m dokima.agent next 57 OUT` runs, in-process, against the fake GitHub of
> `tests/test_merge_gate.py`: each earlier run's record comment (OUT/comment.md, with the Next line `next` wrote) is
> posted on the issue as the bot, then a worker record after it, so the history holds earlier gate failures exactly as
> the real river leaves them. The owner's last word is the `/work` before the first build, unless a test says otherwise.
> """
> import json
> import os
> import sys
> import time
> 
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
> sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
> from dokima import agent  # noqa: E402
> from dokima import agent_github  # noqa: E402
> from test_merge_gate import CODE_REVIEW, N, OLD, OWNER, REPO, WORKER, FakeGitHub, red  # noqa: E402
> 
> BLOCK = {**CODE_REVIEW, "run_id": "40", "run": "https://github.com/o/r/actions/runs/40",
>          "handback": {**CODE_REVIEW["handback"], "verdict": "block", "summary": "The code misses a case."}}
> 
> 
> class History:
>     """The issue's conversation as

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "three\|gate\|def next_step\|blocking" dokima/agent_next.py | head -60; grep -rn "merge gate\|three blocks\|Three blocks" rules/*.md | head -20
```

> 100:def next_step(items, rec, owners, rounds=3, autopilot=lambda: False, body="", number="", parent=lambda: None):
> 105:    question or a blocker for the owner stops. A blocking review sends the work back to the agent its blockers name
> 106:    (any blocker for the planner sends it to the planner), until three blocks in a row at that stage since the owner
> 191:        return ("stop", f"{blocks} blocking reviews in a row without agreement. Your call: `/plan`, `/work` or `/review` with your words.")
> rules/decisions.md:8:- A pull request that changes card, board or workflow code (`.github/workflows/`, `dokima/card.py`, `dokima/body.py`, `dokima/board.py`) runs the play-through on its head by itself; it is not a merge gate.
> rules/raising.md:13:- **Three blocks in a row**: three blocking reviews at one stage since the owner last spoke stop the river for the owner. Example: the code reviewer blocks the third build in a row, so the owner decides with `/plan`, `/work` or `/review`.
> rules/flow.md:7:5. **Code review.** The reviewer starts by itself when the worker finishes. Every blocker names who fixes it: the worker for code, the planner for a test shown too weak. A block sends it back to the worker by itself, or to the planner when any blocker is the planner's; that test fix goes planner, plan review, worker, code review, and an approved re-plan whose criteria are unchanged goes straight to the worker, while one that changes any criterion, or comes after the owner spoke, waits for `/wo

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_gate_stop.py 2>&1 | grep -E "AssertionError|601\.|passed|failed" | head -20; sed -n 100,200p dokima/agent_next.py
```

> Proves 601.1.
>         record_property("proves", "601.1")
>         h.gate_failed()
>             f"601.1: the second merge gate failure in a row should still start the worker, and printed {second[0]!r} (Next: {second[1]!r})"
>             (f"601.1: the merge gate failed a third time in a row with no word from the owner, and the run did not stop "
> E       AssertionError: 601.1: the merge gate failed a third time in a row with no word from the owner, and the run did not stop for the owner: printed 'start worker', Next '**Next:** The merge gate failed: not every check passed on its head commit a1a1a1a: all tests (failure). The worker starts now.', board 'Work none'
> E        +  where False = stopped_for_owner(('start worker', '**Next:** The merge gate failed: not every check passed on its head commit a1a1a1a: all tests (failu....svg" width="16" height="16" align="absmiddle" alt="stats"> Opus 5.5 · [run](https://github.com/o/r/actions/runs/4)\n'))
> tests/test_gate_stop.py:105: AssertionError
>         Proves 601.2.
>         record_property("proves", "601.2")
>             (f"601.2: a blocking code review then one merge gate failure is two in a row and should start the worker, "
>             (f"601.2: a blocking code review then two merge gate failures is three in a row, and the run did not stop for "
> E       AssertionError: 601.2: a blocking code review then two merge gate failures is three in a row, and the run did not stop for the owner: printed 'start worker', Next '**Next:** The merge gate

`5. Bash`
```
cd /home/runner/work/dokima/dokima; mkdir -p /tmp/rv && cat > /tmp/rv/t.py <<'EOF'
import sys; sys.path.insert(0,"tests")
from test_gate_stop import *
def test_b(tmp_path, monkeypatch, capsys):
    h = History(tmp_path, monkeypatch, capsys)
    h.gate_failed(); h.gate_failed()
    r = h.decide(BLOCK)
    assert stopped_for_owner(r), r[:3]
EOF
python3 -m pytest -q /tmp/rv/t.py --rootdir=. -p no:cacheprovider 2>&1 | grep -E "^E|passed|failed" | head -5; git log --oneline -3 -- tests/test_gate_stop.py
```

> h.gate_failed()
>             (f"601.1: the merge gate failed a third time in a row with no word from the owner, and the run did not stop "
> E       AssertionError: 601.1: the merge gate failed a third time in a row with no word from the owner, and the run did not stop for the owner: printed 'start worker', Next '**Next:** The merge gate failed: not every check passed on its head commit a1a1a1a: all tests (failure). The worker starts now.', board 'Work none'
> E       assert False
> E        +  where False = stopped_for_owner(('start worker', '**Next:** The merge gate failed: not every check passed on its head commit a1a1a1a: all tests (failu....svg" width="16" height="16" align="absmiddle" alt="stats"> Opus 5.5 · [run](https://github.com/o/r/actions/runs/4)\n'))
> a1d9128 planner for #601 (run 38521688150)

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q /tmp/rv/t.py::test_b --rootdir=. -p no:cacheprovider 2>&1 | grep -E "^E|passed|failed" | head -5; rm -rf /tmp/rv
```

> h.gate_failed(); h.gate_failed()
> E       AssertionError: ('start worker', '**Next:** The worker starts now.', 'Work none')
> E       assert False
> E        +  where False = stopped_for_owner(('start worker', '**Next:** The worker starts now.', 'Work none', '<!-- dokima-record -->\n<img src="https://raw.githu...svg" width="16" height="16" align="absmiddle" alt="stats"> Opus 5.5 · [run](https://github.com/o/r/actions/runs/40)\n'))
> 1 failed in 0.04s

**Agent:** Both new tests fail today for the right reason: the worker starts again on a third gate failure. I'm writing the review now.

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria and two tests that replay real gate failures on the issue."],
  "decided": ["Gate failures and blocking code reviews count together toward the three-in-a-row stop.",
              "The count starts over when the owner speaks."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries both asks, and both tests fail today because a third gate failure still starts the worker.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A merge gate that keeps failing sends work to the worker again and again", "source": "https://github.com/dokima-dev/dokima/issues/601", "criterion": "601.1"},
  {"ask": "the three-blocks stop counts only reviews", "source": "https://github.com/dokima-dev/dokima/issues/601", "criterion": "601.2"}
 ],
 "behaviors": [
  {"criterion": "601.1", "one_behavior": true, "why": "One result: the third gate failure in a row stops for the owner."},
  {"criterion": "601.2", "one_behavior": true, "why": "One rule: both kinds of block share one count."}
 ],
 "edge_cases": [
  {"criterion": "601.1", "cut": [], "missing": []},
  {"criterion": "601.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_gate_stop.py::test_a_third_merge_gate_failure_in_a_row_stops_for_the_owner", "only_its_behavior": true, "why": "Checks the third failure stops, with the second and post-owner cases still starting the worker."},
  {"test": "tests/test_gate_stop.py::test_gate_failures_and_blocking_code_reviews_count_together", "only_its_behavior": true, "why": "Mixes reviews and gate failures both ways; two in a row still starts the worker."}
 ],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 601 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote two criteria and two tests that replay real gate failures on the issue./The planner wrote two criteria and two tests that replay real gate failures./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 601 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#601](https://github.com/dokima-dev/dokima/issues/601) (repeated merge gate failures should stop for the owner). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** the issue asks for two things, and each has its own criterion:
  - 601.1: a third gate failure in a row, with no word from the owner, stops for the owner instead of starting the worker.
  - 601.2: gate failures and blocking code reviews add up toward the same three-in-a-row stop.
- **Tests fail today for the right reason:** I ran both. Each one fails because a third failure still starts the worker. Nothing crashes and no setup is broken.
- **Last case checked separately:** in test 601.2, the case "two gate failures then a blocking review" never runs today, because the test stops at its first failure. I ran that case on its own, and it also fails for the right reason.
- **Code that cheats can't pass:** each test also checks the good cases. A second failure, or a failure after the owner has spoken, must still start the worker.
- **Size:** each criterion is one behavior, and nothing is raised.

The issue card says this issue blocks [#381](https://github.com/dokima-dev/dokima/issues/381) and [#602](https://github.com/dokima-dev/dokima/issues/602). The plan's links name only #381. That doesn't affect the criteria or tests, so I didn't block on it.

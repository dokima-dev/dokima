# reviewer (plan) for #540

Run: https://github.com/dokima-dev/dokima/actions/runs/38292937766

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat plan.json; cat open_blockers.json
```

> # Issue #540: The record says when every test ran
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 539 -->
> <!-- dokima-blocking: {"blocked_by": [539], "blocks": [], "loop": []} -->
> A code review's record says when every test ran because no baseline was usable.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/539
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/535
> - https://github.com/dokima-dev/dokima/issues/548
> 
> 
> **User story:** When a code review had to run every test, its record tells you why.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** With no usable baseline, the code review's record says every test ran because no baseline was usable.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-540/tests/test_all_tests_note.py#L54"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dok

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_all_tests_note.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:3000])"; git show --stat HEAD
```

> """A code review's record says when every test ran without a usable baseline (#540).
> 
> Before a code review, `.github/workflows/agent.yml` runs the tests the change can affect, picked by pytest-testmon
> from main's baseline (#539). With no usable baseline (none restored, or one testmon cannot read) it runs every test
> instead. The owner only learns that from the run's log; this issue makes the code review's record say so.
> 
> These tests run the real thing end to end: the agent.yml step that writes `tests.txt`, cut out of the workflow with
> `test_testmon.run_tests_step` (a fake pytest that acts as testmon does), then the workflow's own record step,
> `python3 -m dokima.agent record reviewer pr OUT check.txt true LOGS`, on the same pack, and read the comment it writes.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
> from test_testmon import run_tests_step  # noqa: E402
> 
> ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
> REPO = "dokima-dev/dokima"
> SAYS = re.compile(r"every test ran.*baseline", re.I)
> 
> 
> def review_comment(tmp_path, baseline):
>     """Run the test step on `baseline`, then the record step; return its comment.
> 
>     `baseline` is "good", "broken" or None."""
>     calls, _, _, out = run_tests_step(tmp_path, baseline)
>     assert calls, f"the test step never ran pytest\n{out}"
>     pack = tmp_path / "pack"
>     hand, logs = tmp_path / "out", tmp_path / "logs"
>     for d in (hand, logs)

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_all_tests_note.py 2>&1 | tail -30; grep -n "def run_tests_step" -A60 tests/test_testmon.py | head -90
```

> Proves 540.1. Runs the workflow's test step and then its record step, once with no baseline restored and once
>         with a baseline testmon cannot read: each comment must show, outside any fold, one line saying every test ran
>         because no baseline was usable. Beside them, a readable baseline (only the affected tests ran) must show no such
>         line, so a comment that always says it fails."""
>         record_property("proves", "540.1")
>         for baseline, why in ((None, "no baseline was restored"), ("broken", "the baseline could not be read")):
>             text = review_comment(tmp_path / (baseline or "none"), baseline)
>             lines = [l for l in visible(text).splitlines() if SAYS.search(l)]
> >           assert len(lines) == 1, \
>                 f"540.1: when {why}, the code review's comment does not say, in one line, that every test ran " \
>                 f"because no baseline was usable:\n{visible(text)}"
> E           AssertionError: 540.1: when no baseline was restored, the code review's comment does not say, in one line, that every test ran because no baseline was usable:
> E             <!-- dokima-record -->
> E             <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/passed.svg" width="16" height="16" align="absmiddle" alt="passed"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review passed the work.
> E       

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "agent record\|PACK" .github/workflows/agent.yml | head -30; grep -n "PACK\|environ" dokima/agent.py | head -20; python3 - <<'E'
import sys,pathlib,tempfile;sys.path.insert(0,'tests')
from test_all_tests_note import review_comment
t=pathlib.Path(tempfile.mkdtemp())
print(review_comment(t,"good")[:300])
E
```

> 5:# conversation (comments, reviews, line notes) and every earlier agent record. The agent runs its own check before it
> 53:      PACK: /tmp/pack
> 175:          python3 -m dokima.agent pack "$N" "$ROLE" "$STAGE" "$PACK" 2> /tmp/pack-err.txt || {
> 182:          if [ "$STAGE" = pr ]; then git diff origin/main...HEAD > "$PACK/diff.patch"; fi
> 183:          ls -R "$PACK" | head -60
> 203:            PYTHONPATH= PYTHONSAFEPATH= python3 -m pytest -q -rA --testmon --junitxml="$PACK/tests.xml" > "$PACK/tests.txt" 2>&1 || code=$?
> 208:            rm -f "$PACK/tests.xml"
> 209:            PYTHONPATH= PYTHONSAFEPATH= python3 -m pytest -q -rA --junitxml="$PACK/tests.xml" > "$PACK/tests.txt" 2>&1 || true
> 211:          tail -5 "$PACK/tests.txt"
> 214:          python3 -m dokima.agent check-pack "$ROLE" "$STAGE" "$PACK" > /tmp/pack-check.txt \
> 246:            reviewerplan) GRADE=plan-grade;   FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.json $N" ;;
> 247:            reviewerpr)   GRADE=result-grade; FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.json $N" ;;
> 248:            worker)       GRADE=result-grade; FILE=work.json;   CHECK="python3 -m dokima.agent check work $OUT/work.json $PACK/plan.json $N" ;;
> 250:          CHECK="$CHECK && python3 -m dokima.agent check-round $ROLE $OUT/$FILE $PACK"
> 255:          - $PACK/issue.md: issue #$N as it stands, with every comment (the owner's words and answers are here).
> 256:      

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'E'
{"previous_step": {"did": ["Wrote one criterion: with no usable baseline, the code review's record says every test ran, and why.", "Added one test that runs the real test step and record step, with no baseline, a broken one and a good one."], "decided": ["The change stays in the agent workflow and the agent's record code."], "open": []},
 "verdict": "approve",
 "summary": "The plan carries the one ask, and its test fails today because the record says nothing about the baseline.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "With no usable baseline, the code review's record says every test ran because no baseline was usable.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "540.1"}],
 "behaviors": [{"criterion": "540.1", "one_behavior": true, "why": "One case, no usable baseline, and one result, a line on the record."}],
 "tests": [{"test": "tests/test_all_tests_note.py::test_record_says_every_test_ran_without_a_baseline", "only_its_behavior": true, "why": "Runs the real steps; missing and broken baselines must show the line, a good one must not."}],
 "size": "ok"}
E
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 540 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step did line 2 holds 22 words, over its cap of 15: cut 7, keep the facts

**Agent:** Checking my review against Dokima's word limits; two lines were too long, so I'm cutting them.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'E'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d["previous_step"]["did"]=["Wrote one criterion: with no usable baseline, the record says every test ran.","Added one test running the real steps with no, broken and good baselines."]
json.dump(d,open(p,'w'),indent=1)
E
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 540 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#540](https://github.com/dokima-dev/dokima/issues/540) (code review record says when every test ran) and raised nothing. My review is written to `/tmp/dokima-out/review.json` and passes both of Dokima's checks.

- **The ask is covered.** The issue is story 2 of the split of [#535](https://github.com/dokima-dev/dokima/issues/535) (agents run only the tests their change can affect). It has one ask: with no usable baseline, the code review's record says every test ran. The plan's only criterion, 540.1, carries it, and no owner comments have come in since.
- **The test fails today for the right reason.** I ran `tests/test_all_tests_note.py::test_record_says_every_test_ran_without_a_baseline`. It fails because the code review's comment says only "Code review passed the work." and has no line about the baseline. It doesn't crash, and no tool or path is missing.
- **The test is strong enough.** It runs the real test step from the workflow, then the real record step on the same files. It checks both cases: no baseline at all, and one that can't be read. It also checks that a readable baseline produces no such line, so a record that always says "every test ran" would fail. I ran the readable-baseline case by hand and it completes without error.
- **Size is fine:** one criterion, one behavior, one test.

The planner put two files in scope: the agent workflow (`.github/workflows/agent.yml`) and `dokima/agent.py`. Because the workflow file is one of them, the pull request will stop for your approval before it merges.

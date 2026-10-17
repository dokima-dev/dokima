# reviewer (plan) for #819

Run: https://github.com/dokima-dev/dokima/actions/runs/39049271534

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> total 116
> drwxr-xr-x  3 runner runner  4096 Oct 17 16:24 .
> drwxrwxrwt 18 root   root    4096 Oct 17 16:25 ..
> drwxr-xr-x  2 runner runner  4096 Oct 17 16:24 in
> -rw-r--r--  1 runner runner 13912 Oct 17 16:24 issue.md
> -rw-r--r--  1 runner runner   376 Oct 17 16:24 open_blockers.json
> -rw-r--r--  1 runner runner 63207 Oct 17 16:24 open_issues.json
> -rw-r--r--  1 runner runner  5707 Oct 17 16:24 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 17 16:24 parent.json
> -rw-r--r--  1 runner runner  6284 Oct 17 16:24 plan.json
> 
> in:
> total 16
> drwxr-xr-x 2 runner runner 4096 Oct 17 16:24 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 16:24 ..
> -rw-r--r-- 1 runner runner 7092 Oct 17 16:24 01-planner.json
> # Issue #819: Code checks the reviewer's required boxes
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 818 -->
> <!-- dokima-blocking: {"blocked_by": [818], "blocks": [], "loop": []} -->
> A review that skips a box, leaves a field out or approves past a blocking entry is rejected.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/818
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> 
> 
> **User story:** A review that skips a duty, or claims a weak test withou

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/741": "Phase 1 of #272. Replaces #42 (closed, superseded by the YAML settings decision).\n\n**What**\n- Role prompts ship with Dokima and contain no example from Dokima's own code. Today every example uses `dokima/card.py` or `dokima/board.py` (`roles/planner.md:99-170`), the planner says pytest in `tests/` is the only runner (`planner.md:115`), and AGENTS.md is assumed in `planner.md:146`, `worker.md:58`, `reviewer.md:49,75`.\n- The 50-line \"raising\" block copied into planner, worker and reviewer moves to one shared `roles/raising.md` with neutral examples.\n- Numbers written into prompts (\"more than 3 questions\", \"three blocks in a row\", word caps) are read from settings.\n- A repo appends house rules through `prompts.append` in `settings.yaml`, per role or for all. Appending only; a repo never replaces a shipped prompt, so Dokima upgrades do not break it.\n- Default criterion style in the planner prompt: \"When X, Y\". A style convention, not a rule code enforces. Repos may override it in house rules.\n- Rewrite size: planner about 45%, worker about 55%, reviewer about 40%; the two grade prompts stay as they are.\n\n**Done when:** acceptance items 5 and 6 on #272 pass: a scan finds no Dokima file name in any shipped prompt; a repo's house rules appear after the shipped prompt for each role.\n",
>  "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6204381975": "Owner 2026-10-15: the reviewer's four duties, writ

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/test_handback_check.py; cat tests/test_review_boxes.py
```

> commit 668a6da3520689cd662f8fae043952bc4b75812d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 16:24:13 2026 +0000
> 
>     planner for #819 (run 39046865155)
> 
>  tests/samples/132/review-pr.json |  15 +++-
>  tests/test_automerge.py          |   3 +-
>  tests/test_autopilot_river.py    |   2 +-
>  tests/test_failed_run_card.py    |   2 +-
>  tests/test_fixer.py              |   2 +-
>  tests/test_handback_check.py     |   4 +-
>  tests/test_live_queue.py         |   2 +-
>  tests/test_raise_handbacks.py    |   3 +-
>  tests/test_review_asks.py        |   2 +-
>  tests/test_review_boxes.py       | 185 +++++++++++++++++++++++++++++++++++++++
>  tests/test_start.py              |   2 +-
>  11 files changed, 210 insertions(+), 12 deletions(-)
> commit 668a6da3520689cd662f8fae043952bc4b75812d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 16:24:13 2026 +0000
> 
>     planner for #819 (run 39046865155)
> 
> diff --git a/tests/test_handback_check.py b/tests/test_handback_check.py
> index 25a2813..3fec7d3 100644
> --- a/tests/test_handback_check.py
> +++ b/tests/test_handback_check.py
> @@ -35,7 +35,7 @@ REVIEW = {"previous_step": {"did": ["Wrote three criteria."], "decided": [], "op
>                       {"kind": "issue", "text": "t: w", "evidence": "e"}],
>            "answers": [{"raise": "W1", "answer": "done", "why": "The test is weak."}], "asks": ASKS,
>            "size": "ok",
> -          "behaviors": [{"criterio

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/samples tests/test_automerge.py tests/test_autopilot_river.py tests/test_failed_run_card.py tests/test_fixer.py tests/test_live_queue.py tests/test_raise_handbacks.py tests/test_review_asks.py tests/test_start.py | head -200
```

> commit 668a6da3520689cd662f8fae043952bc4b75812d
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 16:24:13 2026 +0000
> 
>     planner for #819 (run 39046865155)
> 
> diff --git a/tests/samples/132/review-pr.json b/tests/samples/132/review-pr.json
> index c4b573a..2dbc3e4 100644
> --- a/tests/samples/132/review-pr.json
> +++ b/tests/samples/132/review-pr.json
> @@ -10,5 +10,16 @@
>    "open": []
>   },
>   "verdict": "approve",
> - "summary": "A failed run now always leaves its card, and its open pull request's, in its stage's column with Needs you."
> -}
> \ No newline at end of file
> + "summary": "A failed run now always leaves its card, and its open pull request's, in its stage's column with Needs you.",
> + "boxes": {
> +  "dropped": "none",
> +  "added": "none",
> +  "superseded": "none",
> +  "conflicts": "none",
> +  "edges": {
> +   "132.1": "covered",
> +   "132.2": "covered"
> +  },
> +  "poor_tests": "none"
> + }
> +}
> diff --git a/tests/test_automerge.py b/tests/test_automerge.py
> index 3aa85a1..65bda84 100644
> --- a/tests/test_automerge.py
> +++ b/tests/test_automerge.py
> @@ -364,7 +364,8 @@ def review_pr(verdict):
>      """A code review's hand-back: an approval, or a block with one blocker for the worker."""
>      h = {"previous_step": {"did": ["Built the fix."], "decided": [], "open": []}, "verdict": verdict,
>           "summary": "Every criterion's test passes." if verdict == "approve" else "57.1's test fails.",
> -         "raises": [], "answers": []}
> +         "raises

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,140p tests/test_review_asks.py | grep -n "def \|SPLIT\|PLAN\b\|STAGE" | head -40; timeout 600 python -m pytest -q tests/test_review_boxes.py 2>&1 | grep -E "^(FAILED|E  )|passed|failed" | head -30
```

> 8:Every check here runs the real commands the workflow runs on a review (`agent check review FILE PLAN N`, then
> 9:`agent check-round reviewer FILE PACK`) on a starting pack built in a temp folder, with STAGE set as the workflow's job
> 26:SPLIT = {"kind": "feature", "feature": "f", "stories": [
> 41:def run(*args, stage=None):
> 44:    Given a stage, the command sees it as the workflow's job does, in STAGE ('plan' or 'pr')."""
> 46:    env.pop("STAGE", None)
> 48:        env["STAGE"] = stage
> 57:def make_pack(where, plan, stage):
> 74:def check_review(tmp_path, review, plan=STORY, stage="plan", number="9"):
> 90:def assert_passes(tmp_path, review, crit, why, **kw):
> 97:def assert_rejected(tmp_path, review, pattern, crit, why, **kw):
> 106:def test_the_reviewer_prompt_asks_for_every_ask_in_the_owners_words(record_property):
> 127:def test_a_plan_review_must_list_every_ask_well_formed(record_property, tmp_path):
> E       AssertionError: 819.1: a review with no dropped box (plan) was let through (exit 0); it must be rejected
> E       assert 0 == 1
> E                       AssertionError: 819.2: a dropped entry without words (plan) was let through; it must be rejected
> E                       assert 0 == 1
> E       AssertionError: 819.3: a weak test entry without the wrong code that still passes (plan) was let through (exit 0); it must be rejected
> E       assert 0 == 1
> E       AssertionError: 819.4: an approve whose dropped box holds a blocking entry (plan) was let through (exit 0); it must be rejected
> E

**Agent:** Running the new tests showed all six fail today for the right reason. Now checking the shared helpers and how naming is asserted.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 18,105p tests/test_review_asks.py; grep -n "edges\|boxes" dokima/roles/reviewer.md
```

> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> SAMPLES = os.path.join(ROOT, "tests", "samples")
> 
> STORY = {"kind": "user_story", "user_story": "u",
>          "acceptance_criteria": [{"text": "a", "source": "https://x/9", "no_edge_cases": "a sample criterion"}, {"text": "b", "source": "https://x/9", "no_edge_cases": "a sample criterion"}],
>          "non_functional": [{"text": "c", "why": "w", "principle": "Fail closed", "no_edge_cases": "a sample criterion"}],
>          "out_of_scope": [],
>          "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_c"]}}
> SPLIT = {"kind": "feature", "feature": "f", "stories": [
>     {"title": "One", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
>      "non_functional": [], "depends_on": []},
>     {"title": "Two", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://x/9"}],
>      "non_functional": [], "depends_on": [0]}]}
> 
> ASKS = [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"},
>         {"ask": "Oil the hinges", "source": "https://github.com/o/r/issues/9#issuecomment-12", "criterion": "9.2"}]
> APPROVE = {"previous_step": {"did": ["Wrote three criteria."], "decided": [], "open": []},
>            "verdict": "approve", "summary": "Every ask has a criterion and a test.", "asks": ASKS, "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("te

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q -x tests/test_handback_check.py tests/test_automerge.py tests/test_autopilot_river.py tests/test_failed_run_card.py tests/test_fixer.py tests/test_live_queue.py tests/test_raise_handbacks.py tests/test_review_asks.py tests/test_start.py 2>&1 | tail -3
```

> Command did not complete within its 120s timeout and was moved to the background (ID: beuh47au4). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/7fca03e1-a020-477c-87df-aeacee85371c/tasks/beuh47au4.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

**Agent:** While the older tests run, I'll write the review.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote six criteria, one test each, for the six review boxes.",
          "The planner added the boxes to sample reviews in older tests."],
  "decided": ["Boxes are checked at plan review and at code review alike."],
  "open": ["The planner filed a proposal: the reviewer's prompt never shows the edges box shape."]
 },
 "verdict": "block",
 "summary": "Two tests pass when the wrong box is named, and a blank edges case is never tested.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "819.1 names any box",
   "text": "The test for 819.1 passes when every rejection lists all six boxes, so it never proves the missing box is the one named. Fix: also assert the reason does not name the boxes still present.",
   "evidence": "`tests/test_review_boxes.py::test_a_review_missing_any_of_the_six_boxes_is_rejected_naming_the_box` only matches `\\b{box}\\b` in any line."},
  {"kind": "blocker", "to": "planner", "label": "819.4 names any box",
   "text": "The test for 819.4 passes when any approve with an entry prints one fixed reason listing all six boxes. Fix: assert the reason does not name the boxes left clear.",
   "evidence": "`tests/test_review_boxes.py::test_a_review_that_approves_while_a_box_holds_a_blocking_entry_is_rejected` only matches `\\b{box}\\b`."},
  {"kind": "blocker", "to": "planner", "label": "819.2 edges line shape",
   "text": "No test checks an edges line that names no case, or reads neither covered nor missing. Fix: add both to the 819.2 test on a block.",
   "evidence": "`ENTRIES` in `tests/test_review_boxes.py` has no edges shape; the owner's shape is `covered | missing: <named case>`."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "Confirmed: the prompt shows the edges line but not its keyed shape. It stays a proposal for the owner."}
 ],
 "asks": [
  {"ask": "One per duty, every box present", "source": "https://gi
```

> raise 1's text holds 35 words, over its cap of 30: cut 5, keep the facts
> rc=1

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['raises'][0]['text']="The test for 819.1 passes when every rejection lists all six boxes. Fix: also assert the reason names none of the boxes still present."
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 819 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None
> rc=1

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent_checks.py | head -20; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(type(d),len(d))
for i in d: print(i.get('number'),i.get('title'))" | grep -i "edge\|box\|prompt\|review" 
```

> 14:def problems_searched(h, pack_dir):
> 15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> 120:        bad += problems_searched(h, pack_dir)
> 819 Code checks the reviewer's required boxes
> 799 Leaner tests: study, fix brittle tests, one shared test surface, then reviewer rules for test quality
> 750 @dokima hotfix: a PR from one sentence, review kept, planning skipped
> 741 Shipped prompts fit any repo, with clear reviewer duties
> 732 Output family: Plan, Work and Review, each drawing its own card section
> 714 The worker's prompt explains the Verified by line
> 713 The planner's prompt explains the Verified by line
> 712 Plan review compares each docstring with what its test does
> 711 Plan review compares each short text with its full text
> 686 Merging after code review stops paying for a 5-minute wait
> 676 A merge is not tied to the commit the code review approved
> 656 The role prompts tell agents to read `AGENTS.md` only; after the split they should also read the topic files it links.
> 652 Live cards never show an edge case's source: no record holds one, only the saved 557 data does.
> 632 The reviewer's prompt never mentions its open issues list, searched or verdict, so it learns them only from rejections.
> 551 The prompt asks a split's criteria to carry edge cases too, but the plan check never reads them on a split.
> 492 The reviewer's prompt says it may leave a 

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 14,45p dokima/agent_checks.py
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

`12. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['answers'][0].update({"searched":[741,632],"verdict":"new"})
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 819 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`13. Bash`
```
sleep 100; tail -3 /tmp/claude-1001/-home-runner-work-dokima-dokima/7fca03e1-a020-477c-87df-aeacee85371c/tasks/beuh47au4.output
```

> <tool_use_error>Blocked: sleep 100 followed by: tail -3 /tmp/claude-1001/-home-runner-work-dokima-dokima/7fca03e1-a020-477c-87df-aeacee85371c/tasks/beuh47au4.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

**Agent:** The review file passes both checks. I'm waiting on the older tests the plan changed.

`14. Bash`
```
until grep -qE "passed|failed|error" /tmp/claude-1001/-home-runner-work-dokima-dokima/7fca03e1-a020-477c-87df-aeacee85371c/tasks/beuh47au4.output; do sleep 5; done; tail -3 /tmp/claude-1001/-home-runner-work-dokima-dokima/7fca03e1-a020-477c-87df-aeacee85371c/tasks/beuh47au4.output
```

> 61 passed in 214.83s (0:03:34)
> 
> [exited with code 0]

**Agent:** I blocked the plan for [#819](https://github.com/dokima-dev/dokima/issues/819) (code checks the reviewer's required boxes) and sent it back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**What I checked:**
- **Owner's asks:** every one of the owner's asks on [#741](https://github.com/dokima-dev/dokima/issues/741) (shipped prompts and reviewer duties) for this story has a criterion. None is missing.
- **New tests:** all six fail today for the right reason, because the check doesn't exist yet. Each one also passes its good case first.
- **Older tests:** the 9 older test files the plan edited still pass (61 tests). The edits only add the new boxes to sample reviews. The plan's list of test changes names just one of these files.

**Blockers for the planner:**
1. **819.1, a review missing a box:** the test still passes if the check prints one fixed reason that lists all six boxes. It never proves the box named is the one missing. Fix: also check the reason doesn't name the boxes that are present.
2. **819.4, an approve past a blocking entry:** the same gap. A check that prints all six box names on any such approve would pass. Same fix.
3. **819.2, a box entry missing a field:** no test covers an edges line that names no case, or that says neither "covered" nor "missing". Fix: add both cases to the 819.2 test.

**The planner's one raise, P1:** I agreed. The reviewer's prompt never shows that the edges box is written per criterion. I had to guess that shape myself. I searched the open issues ([#741](https://github.com/dokima-dev/dokima/issues/741) and [#632](https://github.com/dokima-dev/dokima/issues/632), the reviewer's prompt missing its open-issues fields) and marked it a new issue. It stays a proposal until you file it.

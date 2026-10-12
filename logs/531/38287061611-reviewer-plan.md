# reviewer (plan) for #531

Run: https://github.com/dokima-dev/dokima/actions/runs/38287061611

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat plan.json; cat open_blockers.json
```

> # Issue #531: Plans list each criterion's edge cases, and reviews judge each list
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Plans list each criterion's edge cases with their tests, reviews judge each list, and the card shows them.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/173
> - https://github.com/dokima-dev/dokima/issues/143
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:**
> 
> <!-- dokima-folded -->
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> In Reza's words: "error, timeout, bad data, empty use these as guide lines with examples for planner and reviewer prompts but don't limit to those categories" and "edge cases should be answered structurally and reviewed structurally".
> 
> Every real bug we hit (#514 a run dying unrecorded, #528 a cancelled or still-running check, a crash on a malformed hand-back field) was a normal-use edge case no test fed in, though the prompts already asked for normal-use edge cases.
> 
> Done when
> - The planner lists, for each criterion, the edge cases its tests cover, each with the test that covers it, or says why there are non

`2. Bash`
```
cd /tmp/pack; python3 -c "import json;d=json.load(open('in/01-planner.json'));print({k:v for k,v in d.items() if k!='handback'} if isinstance(d,dict) else d)" | head -50; grep -n "edge\|Edge" /home/runner/work/dokima/dokima/dokima/roles/*.md | head; grep -n "def criterion_item" -A30 /home/runner/work/dokima/dokima/dokima/card.py | head -40
```

> {'role': 'planner', 'stage': None, 'run_id': '38286860308', 'commit_before': 'd5bdd79262c8068b9f8fc13b20fd4c555d81d28d', 'started_by': 'dokima-runtime[bot]', 'models': ['claude-opus-5-5'], 'report': {'duration_ms': 65929, 'turns': 10, 'cost_usd': 0.5611430000000001, 'tokens_in': 465819, 'tokens_out': 6881}, 'log': 'https://github.com/dokima-dev/dokima/blob/logs/logs/531/38286860308-planner.md', 'run': 'https://github.com/dokima-dev/dokima/actions/runs/38286860308', 'check': {'passed': True, 'problems': []}, 'url': 'https://github.com/dokima-dev/dokima/issues/531#issuecomment-6129600022'}
> /home/runner/work/dokima/dokima/dokima/roles/result-grade.md:12:Edge cases: test the ones the owner named and the failures a user hits in normal use (empty input, the error they
> /home/runner/work/dokima/dokima/dokima/roles/result-grade.md:31:7. Now that code exists, a test is shown to be too weak: the code passes it while its criterion's behavior, or an edge
> /home/runner/work/dokima/dokima/dokima/roles/reviewer.md:136:In tests, judge every test the plan names: does it check only its criterion's behavior, with the edge cases the owner
> /home/runner/work/dokima/dokima/dokima/roles/plan-grade.md:12:Edge cases: test the ones the owner named and the failures a user hits in normal use (empty input, the error they
> 415:def criterion_item(repo, label, c, check, tests, number=None):
> 416-    """One criterion bullet: its status circle, its label linked to its check, its words plain.
> 417-
> 418-    The label

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Proposed a split into three stories: plans list edge cases, plan reviews judge them, the card shows them."],
  "decided": ["Read the reviewer's judging as the plan review, which grades the plan's lists.", "Gave each prompt its own criterion for the guiding kinds."],
  "open": []},
 "verdict": "approve",
 "summary": "The split carries every ask in three stories of two or three criteria each; approved.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The planner lists, for each criterion, the edge cases its tests cover, each with the test that covers it, or says why there are none", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S1.1"},
  {"ask": "code rejects a criterion with neither", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S1.2"},
  {"ask": "The planner and reviewer prompts give error, timeout, bad data and empty as guidelines with examples, and say other kinds count too.", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S1.3"},
  {"ask": "The planner and reviewer prompts give error, timeout, bad data and empty as guidelines with examples, and say other kinds count too.", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S2.1"},
  {"ask": "The reviewer judges each criterion's list in its hand-back: exotic cases nobody would hit are cut, and missing normal-use cases are named", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S2.2"},
  {"ask": "code rejects a review that skips a criterion", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S2.3"},
  {"ask": "each criterion shows its edge cases on one line between Verified by and Source, separated by dots", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "S3.1"},
  {"ask": "or \"none, because ...\"", "source": "https://github
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`4. Bash`
```
sed -i 's/Proposed a split into three stories: plans list edge cases, plan reviews judge them, the card shows them./Split the issue into three stories: plans, plan reviews, and the card./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 531 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#531](https://github.com/dokima-dev/dokima/issues/531) (plans list each criterion's edge cases), and the hand-back passes both checks. It is saved as `/tmp/dokima-out/review.json`.

The planner split the issue into three stories with eight criteria:

1. **Plans list edge cases (3 criteria):**
   - Each criterion lists its edge cases with the test for each, or says why there are none.
   - A plan with a criterion that has neither is rejected.
   - The planner's prompt gives error, timeout, bad data and empty as guides, with examples, and says other kinds count.
2. **Plan reviews judge each list (3 criteria):**
   - The same guiding kinds go in the reviewer's prompt.
   - The review judges each criterion's list: exotic cases are cut, and missing normal-use cases are named.
   - A review that skips a criterion is rejected.
3. **The card shows edge cases (2 criteria):**
   - Each criterion shows its edge cases on one line between Verified by and Source, separated by dots.
   - A criterion with none shows "none, because" and the reason.

Each of the owner's eight asks matches exactly one criterion. I raised no blockers or questions.

Three things are worth knowing:

- **Which review judges the lists:** the planner read "the reviewer judges each criterion's list" as the plan review only, since the lists are part of the plan. That fits the issue, so I didn't send it back.
- **One behavior per criterion:** three criteria have an "and" in them (the two prompt criteria and the review's judgment). The size rule could be read strictly as two behaviors each. I counted each as one, because each is a single piece of prompt text or one field in the review.
- **No tests yet:** this is a split, so it has no tests of its own. Each story's tests get graded when that story is planned.

The size rule holds: eight criteria gives three stories.

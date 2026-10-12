# reviewer (plan) for #538

Run: https://github.com/dokima-dev/dokima/actions/runs/38294827318

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> # Issue #538: The card shows each criterion's edge cases
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 536 -->
> <!-- dokima-blocking: {"blocked_by": [536], "blocks": [], "loop": []} -->
> Each criterion on the card shows its edge cases, or why it has none.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/536
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/531
> - https://github.com/dokima-dev/dokima/issues/537
> - https://github.com/dokima-dev/dokima/issues/546
> 
> 
> **User story:** Owners see each criterion's edge cases on its card, or why it has none.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Each criterion on the card shows its edge cases on one line between Verified by and Source, separated by dots.
>   - *<a href="https://github.com/dok

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps(d,indent=1)[:4000])"; cat /home/runner/work/dokima/dokima/tests/test_card_edge_cases.py
```

> {"number": 531}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38294606074",
>  "commit_before": "5290204bd12936b756b0103e2208349eea97a2af",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 65680,
>   "turns": 10,
>   "cost_usd": 0.5832843999999999,
>   "tokens_in": 471345,
>   "tokens_out": 7044
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/538/38294606074-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38294606074",
>  "handback": {
>   "kind": "user_story",
>   "summary": "Each criterion on the card shows its edge cases, or why it has none.",
>   "user_story": "Owners see each criterion's edge cases on its card, or why it has none.",
>   "acceptance_criteria": [
>    {
>     "text": "Each criterion on the card shows its edge cases on one line between Verified by and Source, separated by dots.",
>     "words": "each criterion shows its edge cases on one line between Verified by and Source, separated by dots",
>     "source": "https://github.com/dokima-dev/dokima/issues/531",
>     "no_edge_cases": "The cases are text the plan check already requires; nothing else feeds this line."
>    },
>    {
>     "text": "A criterion with no edge cases shows \"none, because\" and its reason on that line.",
>     "words": "or \"none, because ...\"",
>     "source": "https://github.com/dokima-dev/dokima/issues/531",
>     "edge_cases": [
>      {
>       "case": "An older plan with neither edge cases nor a reason shows no such line."

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_card_edge_cases.py 2>&1 | tail -15; grep -rn "none, because\|between Verified by" --include=*.py --include=*.md . | grep -v test_card_edge | head; git show 5290204 --stat | head -30
```

> tests/test_card_edge_cases.py:105: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_card_edge_cases.py::test_edge_cases_show_on_one_line_between_verified_by_and_source[issue] - AssertionError: 538.1: on the issue card the edge cases are not one line between Verified by and Source: []
> assert 0 == 1
>  +  where 0 = len([])
> FAILED tests/test_card_edge_cases.py::test_edge_cases_show_on_one_line_between_verified_by_and_source[pr] - AssertionError: 538.1: on the pr card the edge cases are not one line between Verified by and Source: []
> assert 0 == 1
>  +  where 0 = len([])
> FAILED tests/test_card_edge_cases.py::test_no_edge_cases_shows_none_because_and_the_reason[issue] - AssertionError: 538.2: on the issue card the line for no edge cases is missing or split: []
> assert 0 == 1
>  +  where 0 = len([])
> FAILED tests/test_card_edge_cases.py::test_no_edge_cases_shows_none_because_and_the_reason[pr] - AssertionError: 538.2: on the pr card the line for no edge cases is missing or split: []
> assert 0 == 1
>  +  where 0 = len([])
> 4 failed in 0.10s
> commit 5290204bd12936b756b0103e2208349eea97a2af
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 18:53:22 2026 +0000
> 
>     Plans list each criterion's edge cases (#550)
>     
>     * planner for #536 (run 38287243382)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * worker for #536 (run 

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote two criteria from the parent plan's story 3, each with a test drawing both cards."],
  "decided": ["An older plan with neither edge cases nor a reason shows no edge case line.", "Only the card drawing changes."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan keeps both asks, each with a test that fails today because the card lacks the line.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Each criterion on the card shows its edge cases on one line between Verified by and Source, separated by dots.", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "538.1"},
  {"ask": "A criterion with no edge cases shows \"none, because\" and its reason on that line.", "source": "https://github.com/dokima-dev/dokima/issues/531", "criterion": "538.2"}
 ],
 "behaviors": [
  {"criterion": "538.1", "one_behavior": true, "why": "One line of edge cases, placed and joined one way."},
  {"criterion": "538.2", "one_behavior": true, "why": "One line reading none, because, with the reason."}
 ],
 "tests": [
  {"test": "tests/test_card_edge_cases.py::test_edge_cases_show_on_one_line_between_verified_by_and_source", "only_its_behavior": true, "why": "Checks one line between Verified by and Source holding the cases joined by dots, on both cards; fails today with no line."},
  {"test": "tests/test_card_edge_cases.py::test_no_edge_cases_shows_none_because_and_the_reason", "only_its_behavior": true, "why": "Checks the reason line, and that an older plan shows no empty line; fails today with no line."}
 ],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 538 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/The planner wrote two criteria from the parent plan's story 3, each with a test drawing both cards./The planner wrote two criteria from the parent's story, each tested on both cards./" /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 538 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#538](https://github.com/dokima-dev/dokima/issues/538) (edge cases shown on the card) and raised no blockers. The hand-back passes both checks and is in `/tmp/dokima-out/review.json`.

- **Asks:** I found two in the source story from [#531](https://github.com/dokima-dev/dokima/issues/531) (plans list edge cases). One is the edge-case line between Verified by and Source, separated by dots. The other is "none, because" plus a reason when a criterion has no edge cases. Each maps to one criterion, 538.1 and 538.2, and neither is missing. #538 has no comments from the owner. I had no GitHub access, so I took both asks from the parent plan's text copied into this issue, not from #531's own page.
- **Tests:** I ran the four new tests and all of them fail today for the right reason. The card draws its Verified by and Source lines, but nothing appears between them yet. Each test checks only its own criterion, on both the issue card and the pull request card.
- **One edge case added by the planner:** an older plan that has neither edge cases nor a reason must show no line at all. Existing plans are like this, so that is normal use, not an extra.
- **Size:** fine. Each criterion is one behavior with one test.

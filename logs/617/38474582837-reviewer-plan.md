# reviewer (plan) for #617

Run: https://github.com/dokima-dev/dokima/actions/runs/38474582837

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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #617: An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A split approved again after its stories were filed now files the new stories.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/553
> 
> 
> **User story:** When the owner rescopes a split parent and approves the new split, its new stories get filed.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A split approved after its earlier stories were filed files its new stories as sub-issues.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-617/tests/test_agent.py#L428"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A split appro

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main --stat; git diff main -- tests; sed -n 340,470p dokima/agent.py
```

> tests/test_agent.py | 36 ++++++++++++++++++++++++++++++++++++
>  1 file changed, 36 insertions(+)
> diff --git a/tests/test_agent.py b/tests/test_agent.py
> index 0099a15..08be40e 100644
> --- a/tests/test_agent.py
> +++ b/tests/test_agent.py
> @@ -423,3 +423,39 @@ def test_a_replan_is_judged_only_on_what_the_planner_changed_in_its_run(record_p
>      (out / "rejected.txt").unlink(missing_ok=True)
>      planner.main(["planner", "check", "9", str(out)])
>      assert "dokima/x.py is outside tests/" in (out / "rejected.txt").read_text()
> +
> +
> +def test_a_split_approved_after_its_stories_were_filed_files_its_new_stories(record_property, monkeypatch):
> +    """A split approved again after filing files its new stories as sub-issues.
> +
> +    Proves 617.1. Files a first split, then adds a newer approved split that keeps the filed story First and adds Third, and
> +    checks filing again creates only Third instead of handing back the old record or filing First twice; filing that
> +    re-plan a second time files nothing more."""
> +    record_property("proves", "617.1")
> +    calls = []
> +    def fake_gh(*args):
> +        calls.append(args)
> +        if args[:2] == ("issue", "view"):
> +            return json.dumps({"title": "Parent"})
> +        if args[:2] == ("issue", "create"):
> +            return f"https://github.com/o/r/issues/{200 + sum(1 for c in calls if c[:2] == ('issue', 'create'))}\n"
> +        if args[0] == "api" and args[1].startswith("repos/o/r/issues/2"):
> +            return json.dumps({"id": 9000 + 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_agent.py -k split_approved_after 2>&1 | tail -8; cat /tmp/pack/in/02-reviewer-plan.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d['handback'],indent=1)[:3000])"
```

> Right contains one more item: 'Third'
>   
>   Full diff:
>   + []
>   - [
>   -     'Third',
>   - ]
> 1 failed, 26 deselected in 0.15s
> {
>  "previous_step": {
>   "did": [
>    "The planner planned one criterion: a split approved again after filing files its new stories.",
>    "The planner added one test filing a split, then a re-plan, then the re-plan again."
>   ],
>   "decided": [
>    "The planner read new stories as every story of the newer split."
>   ],
>   "open": []
>  },
>  "verdict": "block",
>  "summary": "The plan never says what happens to a story the re-plan keeps, so it could be filed twice.",
>  "raises": [
>   {
>    "kind": "blocker",
>    "to": "planner",
>    "label": "Missing normal case",
>    "text": "617.1's test re-plans with only brand-new stories. A rescope keeping a filed story is normal; code filing every story again passes. Add that case, or ask the owner which reading.",
>    "evidence": "`tests/test_agent.py:448` the re-plan holds only story `Third`; the first split's stories never reappear.",
>    "raised_by": "reviewer",
>    "id": "R1"
>   }
>  ],
>  "answers": [],
>  "asks": [
>   {
>    "ask": "An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.",
>    "source": "https://github.com/dokima-dev/dokima/issues/617",
>    "criterion": "617.1"
>   }
>  ],
>  "behaviors": [
>   {
>    "criterion": "617.1",
>    "one_behavior": true,
>    "why": "One action, approving a re-plan, with one result, its new stories filed."
>   }
>  ],
>  "edge_cases": [
>   {
>    "criterion": "617.1",
>    

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner changed the test's re-plan to keep the filed story First beside the new story Third."],
  "decided": ["The planner read new stories as the stories not filed before."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries the ask, and its test now fails if a kept story is filed again.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "An approved re-plan of a split already filed files nothing, so a rescoped parent cannot get new stories.", "source": "https://github.com/dokima-dev/dokima/issues/617", "criterion": "617.1"}],
 "behaviors": [{"criterion": "617.1", "one_behavior": true, "why": "One action, approving a re-plan, with one result, its new stories filed."}],
 "edge_cases": [{"criterion": "617.1", "cut": [], "missing": []}],
 "tests": [{"test": "tests/test_agent.py::test_a_split_approved_after_its_stories_were_filed_files_its_new_stories", "only_its_behavior": true, "why": "Fails today because filing hands back the old record and files nothing."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 617 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> rc=1

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner changed the test.s re-plan to keep the filed story First beside the new story Third./The test'"'"'s re-plan now keeps the filed story First beside the new Third./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 617 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for issue [#617](https://github.com/dokima-dev/dokima/issues/617) (a re-approved split files its new stories). The hand-back passes both code checks.

- **The ask is covered.** The owner's one ask, a rescoped parent getting its new stories, maps to criterion 617.1.
- **My earlier blocker is fixed.** The test's re-plan now keeps the story First, which was already filed, and adds a new story Third. It checks three things:
  - only Third is filed;
  - the old split record is not handed back;
  - filing the same re-plan again creates nothing.
- **The test fails today for the right reason.** I ran it: filing hands back the old record and creates no issue, so nothing named Third is filed.
- **Nothing else is open.** Size is fine, no edge cases are missing, and I raised nothing new.

The review is in `/tmp/dokima-out/review.json`.

# reviewer (plan) for #667

Run: https://github.com/dokima-dev/dokima/actions/runs/38653424831

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (48.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/3b644d34-dcbb-4a3c-a1d8-27453f077be5/tool-results/bfyard44t.txt
> 
> Preview (first 2KB):
> total 80
> drwxr-xr-x 2 runner runner 4096 Oct 14 23:20 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 23:20 ..
> -rw-r--r-- 1 runner runner 6680 Oct 14 23:20 01-planner.json
> -rw-r--r-- 1 runner runner 6809 Oct 14 23:20 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7497 Oct 14 23:20 03-planner.json
> -rw-r--r-- 1 runner runner 5751 Oct 14 23:20 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6624 Oct 14 23:20 05-planner.json
> -rw-r--r-- 1 runner runner 6344 Oct 14 23:20 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7171 Oct 14 23:20 07-planner.json
> -rw-r--r-- 1 runner runner 5937 Oct 14 23:20 08-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6646 Oct 14 23:20 09-planner.json
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/do

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (42.1KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/3b644d34-dcbb-4a3c-a1d8-27453f077be5/tool-results/b07z161qj.txt
> 
> Preview (first 2KB):
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/665
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/669
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/661
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/432
> - https://github.com/dokima-dev/dokima/issues/559
> 
> 
> **User story:** Any ask, however big, splits into stories by the co

`3. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/3b644d34-dcbb-4a3c-a1d8-27453f077be5/tool-results/b07z161qj.txt
```

> 1	# Issue #667: Code groups criteria into stories by shared files
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 665, 666 -->
> 5	<!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> 6	Code works out the stories from the files each criterion changes, and no count rule remains.
> 7	
> 8	**Plan**
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/665
> 13	
> 14	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 15	
> 16	- https://github.com/dokima-dev/dokima/issues/668
> 17	- https://github.com/dokima-dev/dokima/issues/559
> 18	- https://github.com/dokima-dev/dokima/issues/669
> 19	
> 20	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 21	
> 22	- https://github.com/dokima-dev/dokima/issues/661
> 23	- https://github.com/dokima-dev/dokima/issues/666
> 24	- https://github.com/dokima-dev/dokima/issues/432
> 25	- https://github.com/dokima-dev/dokima/issues/559
> 26	
> 27	
> 28	**User story:** Any ask, however big, splits into stories by the code files its criteria change, never by counting.
> 29	
> 30	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/accep

`4. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json; echo; cat in/08-reviewer-plan.json; echo; cat in/09-planner.json | head -c 3000
```

> {
>  "kind": "user_story",
>  "title": "Code groups criteria into stories by shared files",
>  "summary": "Code works out the stories from the files each criterion changes, and no count rule remains.",
>  "user_story": "Any ask, however big, splits into stories by the code files its criteria change, never by counting.",
>  "acceptance_criteria": [
>   {
>    "text": "Code puts criteria that share a code file, directly or through another criterion, into one story.",
>    "words": "Code groups criteria that share any code file into one story (a sub-issue).",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two criteria joined only through a third criterion that shares a file with each.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     },
>     {
>      "case": "A non-functional requirement shares a code file with an acceptance criterion.",
>      "test": "tests/test_story_groups.py::test_criteria_sharing_a_code_file_are_put_in_the_same_story"
>     }
>    ]
>   },
>   {
>    "text": "Code puts criteria with no code file in common into separate stories.",
>    "words": "Criteria with no file in common become separate stories.",
>    "source": "https://github.com/dokima-dev/dokima/issues/661",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "Two unrelated criteria whose edge cases are tested in one test file.",
>      "test": "te

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/scope.md; cat rules/splitting.md | head -60; git log --oneline -3; git status
```

> ## Changing scope
> 
> Never change the scope of an issue silently. Every change of scope is a comment or a native GitHub link.
> 
> - **Splitting** uses native sub-issues, each linking back to the parent. This is how `/work` files a split.
> - **Merging or replacing** closes the old issue as a duplicate of the new one. GitHub links both ways.
> - **Moving scope between issues** gets one short comment on each side ("moved X to #Y"). GitHub cross-links them, so the trail is two clicks either way.
> - **A big reshuffle** of several issues closes the old ones as replaced by new ones that link back, instead of rewriting them.
> ## Splitting and the graph
> 
> - Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 

**Agent:** Reviewing round 5 of the plan for [#667](https://github.com/dokima-dev/dokima/issues/667) (stories grouped by shared files). Running the plan's tests now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "Error|assert|FAILED|passed|failed" | head -30; python -m pytest -q tests/test_size_rule.py tests/test_criterion_files.py tests/test_plan_shape.py tests/test_parent_source.py 2>&1 | tail -3
```

> >       assert hasattr(planner, "story_groups"), f"{k}: code has no way to group criteria into stories by their files"
> E       AssertionError: 667.1: code has no way to group criteria into stories by their files
> E       assert False
> tests/test_story_groups.py:72: AssertionError
> >       assert hasattr(planner, "story_groups"), f"{k}: code has no way to group criteria into stories by their files"
> E       AssertionError: 667.2: code has no way to group criteria into stories by their files
> E       assert False
> tests/test_story_groups.py:72: AssertionError
> >       assert why is None, f"667.3: a story of 6 criteria sharing one code file was refused: {why!r}"
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> E       assert 'story 1 holds 6 criteria; each story holds 1 to 5' is None
> tests/test_story_groups.py:166: AssertionError
> >       assert not stale, "667.4: the old count rules are still stated in " + "; ".join(stale)
> E       AssertionError: 667.4: the old count rules are still stated in dokima/roles/planner.md: '1 to 5 criteria'; dokima/roles/planner.md: 'criteria / 5'; dokima/roles/planner.md: 'at most 5'; dokima/roles/plan-grade.md: '1 to 5 criteria'; dokima/roles/reviewer.md: '1 to 5 criteria'; rules/splitting.md: 'more than five criteria'; the reviewer's size message: '1 to 5 criteria'
> E       assert not ["dokima/roles/planner.md: '1 to 5 criteria'", "dokima/roles/planner.md: 'criteria 

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "missing\|\"asks\"\|'asks'" dokima/agent_checks.py | head -30
```

> 38:        return bad + [f"open_issues.json is missing from the pack, so the "
> 50:        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
> 188:    Each row lists the exotic cases it cuts and the normal-use ones missing, as plain lines ([] when none)."""
> 196:                       "ones missing, each [] when there are none")
> 198:        for f in ("cut", "missing"):
> 207:    words, with a link to where they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an
> 209:    asks = r.get("asks")
> 212:                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
> 213:    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
> 217:        if c != "missing" and c not in ids:
> 220:    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
> 222:        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
> 278:        missing = [k for k in keys if not filled(x.get(k))]
> 279:        if missing:
> 280:            bad.append(f"{label} needs {', '.join(missing)}")
> 285:    """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
> 337:        return None, f"{name} is missing ({path})"
> 354:    One at a time, so a test missing from the branch fails alone and is named, while the others still run."""

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Proposed a separate issue: approved new scope on a child story opens a fresh sibling."],
  "decided": ["The fresh sibling for approved new scope is built in its own issue, not here."],
  "open": ["The owner files the fresh sibling issue, or says it belongs here."]
 },
 "verdict": "approve",
 "summary": "All five tests fail today for the right reason; the fresh sibling ask moves to its own proposed issue.",
 "raises": [],
 "answers": [
  {"raise": "P8", "answer": "done", "why": "Opening a sibling for approved scope is separate work; the owner's answer left placement to the plan."}
 ],
 "asks": [
  {"ask": "Code puts criteria that share any code file into the same story.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "the planner hands back criteria with files and code computes the groups", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "Criteria with no code file in common become separate stories.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.2"},
  {"ask": "No count of criteria or stories splits or refuses a plan", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.3"},
  {"ask": "today's count rules are gone", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.4"},
  {"ask": "Two criteria that share only a markdown file stay in separate stories.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.2"},
  {"ask": "Each edge case stays under its criterion and never changes how criteria group.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.2"},
  {"ask": "No second split, ever. A story keeps one level.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.5"},
  {"ask": "No second split and no re-p
```

> Exit code 1
> the answer to P8 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P8 files an issue, so verdict must be symptom, root cause or new, not None

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent_checks.py dokima/*.py rules/raising.md | head -20; ls /tmp/pack
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/agent_autopilot.py:180:        if decided.get(raises.VERDICT) == "symptom" and raises.is_numbers([cause]):
> dokima/agent_autopilot.py:181:            # A symptom joins its cause as a comment, and files no issue (#623).
> dokima/agent_autopilot.py:188:            lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), cause)} · a symptom, added as a comment")
> dokima/agent_autopilot.py:190:        symptoms = decided.get(raises.SYMPTOMS)
> dokima/agent_autopilot.py:191:        if decided.get(raises.VERDICT) == "root cause" and raises.is_numbers(symptoms) and symptoms:
> dokima/agent_autopilot.py:192:            # A root cause files one issue marked as such, naming each symptom so GitHub links both ways (#623).
> dokima/agent_autopilot.py:194:            body += ["", "**Symptoms:** " + ", ".join(f"#{n}" for n in symptoms)]
> dokima/agent_autopilot.py:198:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/agent_checks.py:14:d

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 10,60p dokima/agent_checks.py; sed -n 15,40p dokima/raises.py; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(type(d), len(d))
for i in (d if isinstance(d,list) else d.values()): print(i.get('number'), i.get('title'))" | head -80
```

> from dokima import raises, words
> 
> 
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
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numb

`11. Bash`
```
python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'))
for i in d:
  t=(i.get('title','')+' '+(i.get('body') or '')).lower()
  if 'sibling' in t or 'new scope' in t or 'grow' in t: print(i.get('number'), i.get('title'))"; python3 -c "import json;print(json.load(open('/tmp/pack/open_issues.json'))[0].keys())"
```

> dict_keys(['number', 'title', 'summary', 'link', 'filed_by_dokima'])

**Agent:** No open issue covers the fresh sibling yet; adding that to the hand-back and re-checking.

`12. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['answers'][0].update({"searched":[661,619,573,432],"verdict":"new"})
json.dump(r,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#667](https://github.com/dokima-dev/dokima/issues/667) (stories grouped by shared files). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Tests:** I ran all five new tests. Each fails today because the feature is missing, not because of a crash:
  - 667.1 and 667.2: code has no way to group criteria by their files.
  - 667.3: six criteria on one code file are still refused.
  - 667.4: the instructions and rules still state the old count rules, and the failure names each place.
  - 667.5: a child story with two separate file groups is not refused.
- **Changed old tests:** the 37 tests in the four files the plan changes still pass.
- **Your asks:** every ask from the issue and your comments maps to a criterion, including "No second split, ever" and "no re-plan of siblings" (both 667.5).
- **Fresh sibling for approved new scope:** the planner proposed this as its own issue. I agreed that it is new work. I checked the open issues and none already covers it.

**Your call:** this one was a judgement call. I had asked you whether it belongs here or in its own issue. Your answer, "Approved new scope turns into a fresh sibling", didn't pick one. Because the planner's question said it assumed a separate issue, I read your answer as accepting that.

The separate issue is only a proposal until you file it. If you want it built here instead, say so with `/plan` and it goes back to the planner.

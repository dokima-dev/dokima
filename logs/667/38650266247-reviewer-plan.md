# reviewer (plan) for #667

Run: https://github.com/dokima-dev/dokima/actions/runs/38650266247

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; echo ====; cat plan.json; echo ===; cat open_blockers.json
```

> <persisted-output>
> Output too large (43.2KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tool-results/b14kfzt90.txt
> 
> Preview (first 2KB):
> total 64
> drwxr-xr-x 2 runner runner 4096 Oct 14 22:50 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 22:50 ..
> -rw-r--r-- 1 runner runner 6680 Oct 14 22:50 01-planner.json
> -rw-r--r-- 1 runner runner 6809 Oct 14 22:50 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7497 Oct 14 22:50 03-planner.json
> -rw-r--r-- 1 runner runner 5751 Oct 14 22:50 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 6624 Oct 14 22:50 05-planner.json
> -rw-r--r-- 1 runner runner 6344 Oct 14 22:50 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 7171 Oct 14 22:50 07-planner.json
> # Issue #667: Code groups criteria into stories by shared files
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 665, 666 -->
> <!-- dokima-blocking: {"blocked_by": [665], "blocks": [559, 668, 669], "loop": []} -->
> Code works out the stories from the files each criterion changes, and no count rule remains.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6179743464) with `/plan`, `/work` or `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="

`2. Bash`
```
cd /tmp/pack; sed -n 1,400p issue.md | tail -n +25
```

> <persisted-output>
> Output too large (35KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tool-results/b2d3rgfj5.txt
> 
> Preview (first 2KB):
> **User story:** Any ask, however big, splits into stories by the code files its criteria change, never by counting.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Code puts criteria that share a code file, directly or through another criterion, into one story.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-667/tests/test_story_groups.py#L85"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: Code puts criteria sharing a code file in one story, even through a third criterion.*
>   <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandbox/demo-icons/icons/bug.svg" width="16" height="16" align="absmiddle" alt="edge cases"></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-667/tests/test_story_groups.py#L85

`3. Bash`
```
cd /tmp/pack; python3 -c "
import re,sys
t=open('issue.md').read()
t=re.sub(r'<img[^>]*>','',t); t=re.sub(r'<[^>]+>','',t)
print(t)" > /tmp/issue_clean.txt; wc -c /tmp/issue_clean.txt; head -c 15000 /tmp/issue_clean.txt | tail -c +1500
```

> 23199 /tmp/issue_clean.txt
> stories, whatever their edge cases.*
>    Edge casesTwo unrelated criteria whose edge cases are tested in one test file.
>   - Source: https://github.com/dokima-dev/dokima/issues/661
> -  **Acceptance criterion:** No count of criteria or stories refuses a plan.
>   * Acceptance test: No count of criteria or stories refuses a plan; an empty story still is.*
>    Edge casesA story with no criteria is still refused.A story of a parent holds six criteria on one code file.
>   - Source: https://github.com/dokima-dev/dokima/issues/661
> -  **Acceptance criterion:** The planner's and reviewer's instructions no longer state the old count rules.
>   * Acceptance test: The planner's and reviewer's instructions and the rules no longer state the old count rules.*
>   - Edge cases: none, because It is fixed text with no input, so nothing varies.
>   - Source: https://github.com/dokima-dev/dokima/issues/661
> -  **Acceptance criterion:** Two criteria that share only a markdown file stay in separate stories.
>    Edge casesTwo criteria list only the same markdown file and no code file.
>   - Source: https://github.com/dokima-dev/dokima/issues/661
> 
> **Scope:** `dokima/planner.py`, `dokima/roles/planner.md`, `dokima/roles/plan-grade.md`, `dokima/roles/reviewer.md`, `rules/splitting.md`, `dokima/agent_checks.py`
> 
> 
> 
> 
> 
> Original issue
> 
> 
> 
> 
> From the approved plan of #661, story 3
> 
> **Part of:** #661 Work splits into stories by the files it changes
> 
> **User story:** Any ask, however big, splits into s

`4. Bash`
```
tail -c +15000 /tmp/issue_clean.txt; cat /tmp/pack/open_blockers.json
```

> ### dokima-runtime on issue #667 (2026-10-14T22:06:00Z)
> 
> 
>   The planner planned this issue.
> 
> **Raised earlier:**
> 
> - Plan review on [#667](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6178527181) raised:  **667.4: misses a rule:** The test for 667.4 passes while the planner's instructions still say a story of a parent holds at most 5. Add `at most 5` to its phrases. · for the planner
>   - Done: The test for 667.4 now also fails on 'at most 5' and 'at most five criteria'.
> - Plan review on [#667](https://github.com/dokima-dev/dokima/issues/667#issuecomment-6178527181) raised:  **667.1: requirements untested:** Criteria include non-functional requirements, but no test groups one sharing a code file with an acceptance criterion. Add that case to 667.1's test. · for the planner
>   - Done: The test for 667.1 now groups a non-functional requirement with the criterion it shares a code file with.
> 
> **Raised:**
> 
> -  **Regroup on scope growth:** Regrouping a grown story's new criteria under its parent is new work. File it separately? The plan assumes so. · for you
>   - Evidence: Owner's comment of 2026-10-14 on [#667](https://github.com/dokima-dev/dokima/issues/667) asks it; this story already holds five criteria, today's most.
> 
> Test changes
> 
> - `tests/test_size_rule.py::test_a_story_over_five_or_empty_is_refused`: Only the empty cases stay, since caps go; the name stays for the moved list.
> - `tests/test_size_rule.py::test_the_right_number_of_stories_passes`: Docstring no longe

`5. Bash`
```
cd /tmp/pack; cat plan.json; echo; python3 -c "
import json;d=json.load(open('in/06-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; ls in
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

**Agent:** Reviewing round 4 of the plan for #667: reading the new tests and running them now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git diff --stat main...HEAD; cat tests/test_story_groups.py
```

> tests/test_card_status.py     |   2 +-
>  tests/test_criterion_files.py |  12 +--
>  tests/test_feature_check.py   |   2 +-
>  tests/test_plan_check.py      |   4 +-
>  tests/test_plan_shape.py      |   3 +-
>  tests/test_size_rule.py       |  18 ++--
>  tests/test_story_groups.py    | 238 ++++++++++++++++++++++++++++++++++++++++++
>  7 files changed, 259 insertions(+), 20 deletions(-)
> """Code groups a plan's criteria into stories by the code files they share.
> 
> Covers #667 (story 3 of #661). `planner.story_groups(criteria)` computes the stories from a list of criteria, each with
> its `files`: it returns one list per story, each the 0-based indexes of its criteria in ascending order, the stories in
> the order of their first criterion. Criteria that share a code file, directly or through another criterion, are one
> story; criteria with no code file in common are separate stories. Files ending in `.md` never join criteria, and edge
> cases never change the groups. The plan check holds every plan to code's groups: a user story, or one story of a split,
> whose criteria form more than one group is rejected with a reason saying "separate stories"; a split that puts criteria
> of one group into different stories is rejected with a reason naming the shared file and saying "same story". No count
> of criteria or stories refuses a plan any more, and the instructions no longer state the old count rules.
> """
> import json
> import os
> import sys
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "Error|assert|passed|failed" | head -30; python3 -m pytest -q -x --ignore=tests/test_story_groups.py 2>&1 | tail -3
```

> Command did not complete within its 120s timeout and was moved to the background (ID: bduftaju7). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tasks/bduftaju7.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 100 python3 -m pytest -q tests/test_story_groups.py 2>&1 | grep -E "^E .*(667|Error)|passed|failed" | head -20
```

> E       AssertionError: 667.1: code has no way to group criteria into stories by their files
> E       AssertionError: 667.2: code has no way to group criteria into stories by their files
> E       AssertionError: 667.3: a story of 6 criteria sharing one code file was refused: 'story 1 holds 6 criteria; each story holds 1 to 5'
> E       AssertionError: 667.4: the old count rules are still stated in dokima/roles/planner.md: '1 to 5 criteria'; dokima/roles/planner.md: 'criteria / 5'; dokima/roles/planner.md: 'at most 5'; dokima/roles/plan-grade.md: '1 to 5 criteria'; dokima/roles/reviewer.md: '1 to 5 criteria'; rules/splitting.md: 'more than five criteria'; the reviewer's size message: '1 to 5 criteria'
> E       AssertionError: 667.5: a story of a split whose criteria share no code file was not refused saying 'never splits again': None
> 5 failed in 0.13s

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "def problems_size" dokima/; grep -n "1 to 5\|PER_STORY" dokima/*.py | head; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tasks/bduftaju7.output | tail -3
```

> dokima/agent_checks.py:160:def problems_size(r, ids=()):
> dokima/agent_checks.py:178:        return ['size is empty: write "ok" if every story holds 1 to 5 criteria, each one behavior; otherwise '
> dokima/planner.py:131:PER_STORY = 5
> dokima/planner.py:140:    """Garbled unless every story holds 1 to 5 criteria, in at least as many stories as the count needs.
> dokima/planner.py:142:    The size rule: each story holds 1 to 5 criteria, so an issue needs at least criteria / 5 stories, rounded up. There
> dokima/planner.py:145:    total, need = sum(sizes), -(-sum(sizes) // PER_STORY)
> dokima/planner.py:146:    if nested and (len(stories) > 1 or total > PER_STORY):
> dokima/planner.py:148:                      f"most {PER_STORY} criteria (acceptance criteria and non-functional requirements together), and "
> dokima/planner.py:150:    big = [n for n, k in enumerate(sizes, 1) if not 1 <= k <= PER_STORY]
> dokima/planner.py:152:        raise Garbled(f"story {big[0]} holds {sizes[big[0] - 1]} criteria; each story holds 1 to {PER_STORY}")
> dokima/planner.py:155:                      f"({PER_STORY} at most each), not {len(stories)}")
> assert not ["dokima/roles/planner.md: '1 to 5 criteria'", "dokima/roles/planner.md: 'criteria / 5'", "dokima/roles/planner.md: 'a...1 to 5 criteria'", "dokima/roles/reviewer.md: '1 to 5 criteria'", "rules/splitting.md: 'more than five criteria'", ...]
> FAILED tests/test_story_groups.py::test_a_story_of_a_split_never_splits_again - AssertionError: 667.5: a story of a split

`10. Bash`
```
grep -E "passed|failed" /tmp/claude-1001/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tasks/bduftaju7.output
```

> (Bash completed with no output)

`11. Bash`
```
cd /home/runner/work/dokima/dokima; git diff main...HEAD -- tests/test_size_rule.py tests/test_card_status.py tests/test_feature_check.py tests/test_plan_check.py
```

> diff --git a/tests/test_card_status.py b/tests/test_card_status.py
> index 9d79dad..ff8d919 100644
> --- a/tests/test_card_status.py
> +++ b/tests/test_card_status.py
> @@ -164,7 +164,7 @@ STORY_PLAN = {"kind": "user_story", "title": "Slow calls return a job id", "summ
>                "non_functional": [], "scope": ["dokima/jobs.py"], "out_of_scope": [],
>                "tests": {"9.1": ["tests/test_jobs.py::test_id"]}, "test_changes": {}}
>  FEATURE_PLAN = {"kind": "feature", "title": "Slow calls run as jobs", "summary": SUMMARY, "feature": "Slow calls run as jobs.", "stories": [
> -    {"title": t, "user_story": f"Owners get {t}.", "acceptance_criteria": [{"text": f"{t} works {k}.", "source": "https://github.com/o/r/issues/9", "files": ["dokima/jobs.py"]} for k in (1, 2, 3)],
> +    {"title": t, "user_story": f"Owners get {t}.", "acceptance_criteria": [{"text": f"{t} works {k}.", "source": "https://github.com/o/r/issues/9", "files": [f"dokima/{t.lower()}.py"]} for k in (1, 2, 3)],
>       "non_functional": [], "depends_on": []} for t in ("Jobs", "Results")]}
>  
>  
> diff --git a/tests/test_feature_check.py b/tests/test_feature_check.py
> index 988ef03..fd1c573 100644
> --- a/tests/test_feature_check.py
> +++ b/tests/test_feature_check.py
> @@ -23,7 +23,7 @@ SRC = "https://github.com/o/r/issues/9"
>  def story(title, deps):
>      """One well-formed story with the given title and dependencies."""
>      return {"title": title, "user_story": f"Owners get {title}.",
> -            "acceptance_criteria": [{"text": 

**Agent:** Tests all fail for the right reasons; now checking a few old-test edits the plan doesn't list.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline main..HEAD -- tests/test_card_status.py tests/test_feature_check.py tests/test_plan_check.py; grep -n "test_changes" dokima/planner.py | head
```

> 0e16331 planner for #667 (run 38629946648)
> 11:test_changes. Every new test has a one-sentence summary, names each criterion it proves by number below it, and fails
> 291:    tc = p.get("test_changes", {})
> 293:        raise Garbled("plan.json test_changes must map each changed older test to a non-empty reason")
> 301:                    "scope": p["scope"], "test_changes": tc,
> 340:def test_changes(paths, before, after):
> 398:    out += [f"{t} is an older test the planner changed or deleted, with no reason in test_changes"
> 399:            for t in older if t not in plan["test_changes"]]
> 559:        lines += [f"- `{t}`: {plan['test_changes'].get(t, 'no reason given')}" for t in older]
> 612:            tc = test_changes(paths, read_at(base), read_now)

`13. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 335,405p dokima/planner.py
```

> if name:
>             block.append(line)
>     return out
> 
> 
> def test_changes(paths, before, after):
>     """Tests the planner touched, by path::name: added, changed (with their old keys) and deleted.
> 
>     A test whose source is unchanged apart from its name is a rename: a change, filed under its old name, with its
>     new name under renamed (old -> new), a key that is there only when something was renamed.
>     """
>     added, changed, deleted, renamed = {}, {}, {}, {}
>     for path in paths:
>         old, new = test_functions(before(path)), test_functions(after(path))
>         gone = [name for name in old if name not in new]
>         for name, (src, keys) in new.items():
>             if name not in old:
>                 was = next((o for o in gone if old[o][0].replace(f"def {o}(", f"def {name}(", 1) == src), None)
>                 if was:
>                     gone.remove(was)
>                     changed[f"{path}::{was}"] = (old[was][1], keys)
>                     renamed[f"{path}::{was}"] = f"{path}::{name}"
>                 else:
>                     added[f"{path}::{name}"] = keys
>             elif old[name][0] != src:
>                 changed[f"{path}::{name}"] = (old[name][1], keys)
>         for name in gone:
>             deleted[f"{path}::{name}"] = old[name][1]
>     return dict({"added": added, "changed": changed, "deleted": deleted}, **({"renamed": renamed} if renamed else {}))
> 
> 
> def proving(tc):
>     """Each added or changed test with the keys it proves now."""
>     return dict(tc["added"],

**Agent:** Tests check out. Now checking how the hand-back checker treats asks marked missing while a question is pending.

`14. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "missing" dokima/agent_checks.py | head -30
```

> 38:        return bad + [f"open_issues.json is missing from the pack, so the "
> 50:        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
> 188:    Each row lists the exotic cases it cuts and the normal-use ones missing, as plain lines ([] when none)."""
> 196:                       "ones missing, each [] when there are none")
> 198:        for f in ("cut", "missing"):
> 207:    words, with a link to where they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an
> 212:                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
> 217:        if c != "missing" and c not in ids:
> 220:    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
> 222:        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
> 278:        missing = [k for k in keys if not filled(x.get(k))]
> 279:        if missing:
> 280:            bad.append(f"{label} needs {', '.join(missing)}")
> 285:    """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
> 337:        return None, f"{name} is missing ({path})"
> 354:    One at a time, so a test missing from the branch fails alone and is named, while the others still run."""

`15. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/scope.md | head -60; grep -n "sibling" -r rules dokima/*.py | head
```

> ## Changing scope
> 
> Never change the scope of an issue silently. Every change of scope is a comment or a native GitHub link.
> 
> - **Splitting** uses native sub-issues, each linking back to the parent. This is how `/work` files a split.
> - **Merging or replacing** closes the old issue as a duplicate of the new one. GitHub links both ways.
> - **Moving scope between issues** gets one short comment on each side ("moved X to #Y"). GitHub cross-links them, so the trail is two clicks either way.
> - **A big reshuffle** of several issues closes the old ones as replaced by new ones that link back, instead of rewriting them.
> rules/splitting.md:4:- 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> rules/splitting.md:6:- When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.

`16. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "block" dokima/agent_checks.py | head -40
```

> 21:    path = os.path.join(pack_dir, "open_blockers.json")
> 102:    path = os.path.join(pack_dir, "open_blockers.json")
> 128:        bad.append("verdict must be approve, block or escalate")
> 136:    blocks = [x for x in r.get("raises") or [] if isinstance(x, dict) and x.get("kind") == "blocker"] \
> 138:    if r.get("verdict") == "approve" and blocks:
> 139:        bad.append("an approve raises no blocker")
> 140:    if r.get("verdict") == "block" and not blocks:
> 141:        bad.append("a block needs at least one blocker in raises")
> 294:            bad.append("verdict must be approve, block or escalate")

**Agent:** Writing the review now: the tests are sound, but one owner ask (opening a new sibling issue for approved new scope) has no criterion and waits on the owner.

`17. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Added criterion 667.5: a story of a split is refused, never split again, with a new test."],
  "decided": ["Markdown never grouping is proven as an edge case of 667.2."],
  "open": ["Asks the owner whether opening a fresh sibling for approved new scope is its own issue.", "Asks the owner whether folding markdown under 667.2 is fine."]
 },
 "verdict": "block",
 "summary": "All five tests fail today for the right reason; one owner ask waits on the owner's answer.",
 "raises": [
  {"kind": "blocker", "to": "owner", "label": "New scope: no criterion",
   "text": "No criterion opens a fresh sibling when you approve new scope for a child story. Answer the planner's question: here, or its own issue?",
   "evidence": "Owner's comments of 2026-10-14T22:22 and 22:25 on #667; plan.json criteria 667.1 to 667.5 open no issue; question P6 is open."}
 ],
 "answers": [
  {"raise": "P7", "answer": "done", "why": "A shared markdown file is no shared code file, so 667.2 already covers it.",
   "words": "Files ending in .md are ignored when grouping.", "source": "https://github.com/dokima-dev/dokima/issues/667", "changes": false}
 ],
 "asks": [
  {"ask": "Code puts criteria that share any code file into the same story.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "the planner hands back criteria with files and code computes the groups", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.1"},
  {"ask": "Criteria with no code file in common become separate stories.", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.2"},
  {"ask": "No count of criteria or stories splits or refuses a plan", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterion": "667.3"},
  {"ask": "today's count rules are gone", "source": "https://github.com/dokima-dev/dokima/issues/667", "criterio
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`18. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Added criterion 667.5: a story of a split is refused, never split again, with a new test./Added 667.5: a story of a split is refused, never split again./; s/Asks the owner whether opening a fresh sibling for approved new scope is its own issue./Asks the owner whether a fresh sibling for approved new scope is its own issue./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 667 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`19. Bash`
```
tail -c 600 /tmp/claude-1001/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tasks/bduftaju7.output
```

> s/reviewer.md: '1 to 5 criteria'; rules/splitting.md: 'more than five criteria'; the reviewer's size message: '1 to 5 criteria'
> assert not ["dokima/roles/planner.md: '1 to 5 criteria'", "dokima/roles/planner.md: 'criteria / 5'", "dokima/roles/planner.md: 'a...1 to 5 criteria'", "dokima/roles/reviewer.md: '1 to 5 criteria'", "rules/splitting.md: 'more than five criteria'", ...]
> FAILED tests/test_story_groups.py::test_a_story_of_a_split_never_splits_again - AssertionError: 667.5: a story of a split whose criteria share no code file was not refused saying 'never splits again': None
> assert (None)

**Agent:** I blocked the plan for [#667](https://github.com/dokima-dev/dokima/issues/667) (code groups criteria into stories by shared files). The plan is sound, but one of your asks has no criterion and needs your answer. The review passed both hand-back checks and is in `/tmp/dokima-out/review.json`.

**The tests:** I ran all five new tests and each fails today for the right reason. They fail because the feature is missing, not because of a crash or a bad path:
- **667.1 and 667.2:** code has no way yet to group criteria by the files they change.
- **667.3:** a story of 6 criteria is still refused by today's cap of 5.
- **667.4:** the old count rules are still written in the planner's and reviewer's instructions, the splitting rules and the reviewer's size message.
- **667.5:** a child story whose criteria share no code file is still accepted.

Each test also has a case that should pass beside the ones that should be refused. Each criterion is one behavior, and no edge cases are missing.

**The blocker (for you):** you said a child story can never grow its scope, and that if you approve new scope, a fresh sibling issue is opened. No criterion does that. The planner asked whether it should be its own issue; that question is still open. Please answer it with `/plan`.

**Answered for you:** the planner asked whether folding "markdown never groups" in as an edge case of 667.2 is fine. I said yes, quoting your words "Files ending in .md are ignored when grouping." A criterion that shares only a markdown file shares no code file, so 667.2 already covers it.

**Still open:**
- I raised a question last round that you haven't answered. By the new grouping rule this plan would be two stories, because 667.4 shares no code file with the others.
- The planner also changed sample data in three older test files (`tests/test_card_status.py`, `tests/test_feature_check.py`, `tests/test_plan_check.py`) without listing them in the plan's test changes. The edits only make sample stories use different files, as the new grouping needs, so I didn't block on them.
- I didn't wait for the rest of the test suite to finish, so I haven't checked that the older tests pass on this branch.

`20. Bash`
```
tail -n 4 /tmp/claude-1001/-home-runner-work-dokima-dokima/98222742-6188-4339-80ad-d7f7284e0df3/tasks/bduftaju7.output
```

> -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
> 1194 passed, 1 warning in 686.99s (0:11:26)
> 
> [exited with code 0]

**Agent:** The rest of the test suite has now finished on this branch: all 1,194 older tests pass. The planner's edits to the older tests broke nothing.

The review stays as it was: blocked, waiting for your answer with `/plan` on whether opening a sibling issue for approved new scope is part of this issue or its own issue.

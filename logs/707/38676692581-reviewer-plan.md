# reviewer (plan) for #707

Run: https://github.com/dokima-dev/dokima/actions/runs/38676692581

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (29.9KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/2039779b-8cb6-411d-91bb-b9935c795e9a/tool-results/bk6otq66s.txt
> 
> Preview (first 2KB):
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
> # Issue #707: The plan check locks my tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/707#issuecomment-6183397749) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/710
> - https://github.com/dokima-dev/dokima/issues/712
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/dokima-dev/dokima/issues/714
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/do

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #707: The plan check locks my tests and checks test docstrings
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [710, 712, 713, 714], "loop": []} -->
> The plan check keeps the owner's tests as written and holds new tests to one docstring shape.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/707#issuecomment-6183397749) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/710
> - https://github.com/dokima-dev/dokima/issues/712
> - https://github.com/dokima-dev/dokima/issues/713
> - https://github.com/dokima-dev/dokima/issues/714
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/559
> 
> 
> **User story:** Tests the owner commits stay exactly as written, and every new test explains itself in one shape.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Ac

`3. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json; echo; cat parent.json | head -c 6000; echo; cat open_issues.json | head -c 2000
```

> {
>  "kind": "user_story",
>  "title": "Plan check locks owner tests and checks test docstrings",
>  "summary": "The plan check keeps the owner's tests as written and holds new tests to one docstring shape.",
>  "user_story": "Tests the owner commits stay exactly as written, and every new test explains itself in one shape.",
>  "acceptance_criteria": [
>   {
>    "text": "A plan that changes a test the owner committed is rejected, naming that test.",
>    "words": "A plan built on my tests keeps every one unchanged",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One change to one test; the owner named no other case."
>   },
>   {
>    "text": "A plan that deletes a test the owner committed is rejected, naming that test.",
>    "words": "agents may propose more but never change or drop mine",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One deleted test; the owner named no other case."
>   },
>   {
>    "text": "A plan that files no criterion for a test the owner committed is rejected, naming that test.",
>    "words": "maps each to a criterion",
>    "source": "https://github.com/dokima-dev/dokima/issues/559",
>    "files": [
>     "dokima/planner.py"
>    ],
>    "no_edge_cases": "One test left out; the owner named no other case."
>   },
>   {
>    "text": "A new or changed test with no User line in its docstring is rejected, naming the test.",
>    "words": "

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; gh issue view 559 --repo dokima-dev/dokima --comments 2>&1 | head -5
```

> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38673931942",
>  "commit_before": "cfb11e4519569d5ea3fdade9e1ce41dad37b38bd",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1781867,
>   "turns": 47,
>   "cost_usd": 2.8603251999999992,
>   "tokens_in": 4513946,
>   "tokens_out": 46556
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/707/38673931942-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38673931942",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/707#issuecomment-6183397749"
> }
> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -20; cat tests/test_owner_tests_and_docstrings.py
```

> commit 1b90279db90c47195e27a721c96dd7c2eec2bf75
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 03:30:55 2026 +0000
> 
>     planner for #707 (run 38673931942)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_body.py                       |   5 +-
>  tests/test_new_test_check.py             |  43 ++--
>  tests/test_owner_tests_and_docstrings.py | 381 +++++++++++++++++++++++++++++++
>  tests/test_plan_check.py                 |   8 +-
>  tests/test_replan_check.py               |  15 +-
>  tests/test_word_caps.py                  |  17 +-
>  6 files changed, 436 insertions(+), 33 deletions(-)
> """User: The plan check locks the owner's tests and holds new tests to one shape.
> 
> Agent: Every test here runs the check the way the agent workflow runs it, `python3 -m dokima.planner check 9 OUT`,
> through `planner.main`, inside a temp git repo built like a real branch: a starting commit (PLANNER_BASE) holding one
> older test in the old docstring shape, then a commit by the owner (author "Owner", not `dokima-runtime[bot]`) adding
> `tests/test_owner.py::test_owner_id`, at which the planner's run starts (PLANNER_RUN_BASE). The planner then writes its
> own tests on top, uncommitted. A good plan passes (exit 0); each broken one fails (exit 1) and its reason, saved to
> OUT/rejected.txt, is read back and split on "; " into one problem each, so a test can check one problem names both
> the test and what

**Agent:** Reading the plan's tests; next I run them to confirm each fails for the right reason.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_owner_tests_and_docstrings.py 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed" | head -40
```

> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_changes_the_owners_test_is_rejected_naming_it - AssertionError: 707.1: a plan that changes a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_deletes_the_owners_test_is_rejected_naming_it - AssertionError: 707.2: a plan that deletes a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_plan_that_files_no_criterion_for_the_owners_test_is_rejected_naming_it - AssertionError: 707.3: a plan that files no criterion for a test the owner committed was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it[new test] - AssertionError: 707.4: a new test with no User part in its docstring was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it[changed older test] - AssertionError: 707.4: a changed test with no User part in its docstring was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_verified_by_line_is_rejected_naming_it[new test] - AssertionError: 707.5: a new test with no Verified by part in its docstring was accepted
> FAILED tests/test_owner_tests_and_docstrings.py::test_a_new_or_changed_test_with_no_verified_by_line_is_rejected_naming_it[changed older test] - AssertionError: 707.5: a changed test with no Verified by part in its docstr

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "test_changes\|RUN_BASE\|PLANNER_BASE\|deleted\|dropped\|removed" dokima/planner.py | head -50
```

> 11:test_changes. Every new test has a one-sentence summary, names each criterion it proves by number below it, and fails
> 335:    tc = p.get("test_changes", {})
> 337:        raise Garbled("plan.json test_changes must map each changed older test to a non-empty reason")
> 345:                    "scope": fence.scope_from(p), "test_changes": tc,
> 384:def test_changes(paths, before, after):
> 385:    """Tests the planner touched, by path::name: added, changed (with their old keys) and deleted.
> 390:    added, changed, deleted, renamed = {}, {}, {}, {}
> 406:            deleted[f"{path}::{name}"] = old[name][1]
> 407:    return dict({"added": added, "changed": changed, "deleted": deleted}, **({"renamed": renamed} if renamed else {}))
> 441:    older = [t for t in tc["changed"] if not set(tc["changed"][t][0]) <= keys] + list(tc["deleted"])
> 442:    out += [f"{t} is an older test the planner changed or deleted, with no reason in test_changes"
> 443:            for t in older if t not in plan["test_changes"]]
> 603:        lines += [f"- `{t}`: {plan['test_changes'].get(t, 'no reason given')}" for t in older]
> 650:            base = os.environ.get("PLANNER_BASE", "HEAD")
> 656:            tc = test_changes(paths, read_at(base), read_now)
> 661:            run_base = os.environ.get("PLANNER_RUN_BASE")
> 680:            older = sorted(t for t in tc["changed"] if not set(tc["changed"][t][0]) <= {f"{number}.{k}" for k in range(1, len(result["criteria"]) + 1)}) + sorted(tc["deleted"])

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 410,460p dokima/planner.py; sed -n 640,700p dokima/planner.py
```

> def proving(tc):
>     """Each added or changed test with the keys it proves now."""
>     return dict(tc["added"], **{t: new for t, (_, new) in tc["changed"].items()})
> 
> 
> def missing_tests(names):
>     """The named tests (path::name) that are not in the repo: no such file, or no such test in it."""
>     return [t for t in names if t.partition("::")[2] not in test_functions(read_now(t.partition("::")[0]))]
> 
> 
> def problems(number, plan, files, tc, declared=None):
>     """What is wrong with a plan and the tests it touched; empty when it can be posted.
> 
>     Given the tests the plan declares, each must be in the repo and filed under one of the plan's criteria, and an
>     older test already in the repo counts as proof of the criteria it is filed under.
>     """
>     out = [f"{p} is outside tests/; the planner may only write tests" for p in files if not p.startswith("tests/")]
>     if not tc["added"] and not tc["changed"]:
>         out.append("the plan came with no tests")
>     keys = {f"{number}.{k}" for k in range(1, len(plan["criteria"]) + 1)}
>     proven = {k for ks in proving(tc).values() for k in ks}
>     if declared is not None:
>         names = sorted(declared_by_test(declared))
>         out += [f"the plan names {t}, which is not in the repo" for t in missing_tests(names)]
>         out += [f"tests are filed under {k}, which is not a criterion of this plan ({number}.1 to {number}.{len(keys)})"
>                 for k in sorted(declared) if k not in keys]
>         proven |= {k for k, ts in declare

`9. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1 HEAD -- tests/test_body.py tests/test_plan_check.py tests/test_replan_check.py tests/test_word_caps.py
```

> diff --git a/tests/test_body.py b/tests/test_body.py
> index 6d8c7ac..6b14d1d 100644
> --- a/tests/test_body.py
> +++ b/tests/test_body.py
> @@ -135,7 +135,10 @@ def run_card(monkeypatch, github, current):
>  
>  REASON = "the owner's part below the marker would change"
>  
> -PLAN_TESTS = ('def test_card(record_property):\n    """The card shows.\n\n    Proves 40.1.\n    """\n'
> +# The planner's new test file, in the docstring shape #707 asks for: User and Verified by lines, then an Agent part.
> +PLAN_TESTS = ('"""User: Sample tests for the card.\n\nAgent: They fail until the card exists.\n"""\n\n\n'
> +              'def test_card(record_property):\n    """User: The card shows.\n    Verified by: drawing the card.\n\n'
> +              '    Agent: Proves 40.1.\n    """\n'
>                '    record_property("proves", "40.1")\n    assert False\n')
>  PLAN = {"kind": "user_story", "title": "Every issue shows a card", "summary": "Every issue shows a card.", "user_story": "Owners see a card on every issue.",
>          "acceptance_criteria": [{"text": "The issue shows a card on top.", "source": f"https://github.com/{REPO}/issues/{NUMBER}", "no_edge_cases": "a sample criterion", "files": ["dokima/card.py"]}],
> diff --git a/tests/test_plan_check.py b/tests/test_plan_check.py
> index 94a83a4..22c5bd1 100644
> --- a/tests/test_plan_check.py
> +++ b/tests/test_plan_check.py
> @@ -23,9 +23,13 @@ ISSUE = "https://github.com/o/r/issues/9"
>  OLD_TESTS = ('def test_old(record_property):\n    """An older test, already in the 

`10. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x tests/test_body.py tests/test_plan_check.py tests/test_replan_check.py tests/test_word_caps.py tests/test_new_test_check.py 2>&1 | tail -5
```

> ?                                    ++++++++++++++++++
>     ::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)
>     plan
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 68 passed in 15.91s

`11. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q tests/test_body.py tests/test_plan_check.py tests/test_replan_check.py tests/test_word_caps.py tests/test_new_test_check.py 2>&1 | grep -E "^FAILED|passed|failed"
```

> FAILED tests/test_word_caps.py::test_a_docstring_the_planner_adds_is_held_to_15_words_in_its_first_line - AssertionError: 239.2: a docstring within its cap was listed: '::warning title=Over the word cap::tests/test_jobs.py has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)\n::warning title=Over the word cap::tests/test_jobs.py::test_id has a docstring whose first line holds 16 words, over its cap of 15 (up to 18 passes)\nplan\n'
> 1 failed, 90 passed in 44.52s

**Agent:** Plan's 18 new test runs all fail today for the right reason. One gap found: the owner-test lock can be bypassed by giving a reason. Writing the review.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/559"
C=I+"#issuecomment-6131843348"
asks=[("A plan that changes a test the owner committed is rejected, naming that test.",I,"707.1"),
("A plan that deletes a test the owner committed is rejected, naming that test.",I,"707.2"),
("A plan that files no criterion for a test the owner committed is rejected, naming that test.",I,"707.3"),
("A new or changed test with no User line in its docstring is rejected, naming the test.",C,"707.4"),
("A new or changed test with no Verified by line is rejected, naming the test.",C,"707.5"),
("A new or changed test with no Agent paragraph is rejected, naming the test.",C,"707.6"),
("An Agent paragraph of any length that names code passes the check.",C,"707.7"),
("A User line over its word cap is rejected, naming the test and its word count.",C,"707.8"),
("A Verified by line over its word cap is rejected, naming the test and its word count.",C,"707.9"),
("An Edge line over its word cap is rejected, naming the test and its word count.",C,"707.10"),
("A new test file whose opening docstring has no user line is rejected.",C,"707.11"),
("A new test file whose opening docstring has no agent detail after its user line is rejected.",C,"707.12"),
("An older test left unchanged passes the check without the new docstring shape.",C,"707.13"),
("Any plain sentence passes as a Verified by line; no list of test kinds is required.",C,"707.14")]
T="tests/test_owner_tests_and_docstrings.py::"
names={"707.1":"test_a_plan_that_changes_the_owners_test_is_rejected_naming_it",
"707.2":"test_a_plan_that_deletes_the_owners_test_is_rejected_naming_it",
"707.3":"test_a_plan_that_files_no_criterion_for_the_owners_test_is_rejected_naming_it",
"707.4":"test_a_new_or_changed_test_with_no_user_line_is_rejected_naming_it",
"707.5":"test_a_new_or_changed_test_with_no_verified_by_line_is_rejected_naming_it",
"707.6":"test_a_new_or_changed_test_with_no_agent_p
```

> raise 1's text holds 50 words, over its cap of 30: cut 20, keep the facts
> rc=1

`13. Bash`
```
cd /tmp; python3 - <<'EOF'
import json
p="/tmp/dokima-out/review.json";r=json.load(open(p))
r["raises"][0]["text"]="Code letting a stated reason unlock your tests passes both. Fix: also give the owner's test a reason, and still expect rejection."
json.dump(r,open(p,"w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 707 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I blocked the plan for [#707](https://github.com/dokima-dev/dokima/issues/707) (locking the owner's tests and checking test docstrings). It sends one fix back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**What holds up**
- Every ask from the approved plan of [#559](https://github.com/dokima-dev/dokima/issues/559) (tests are the spec) has its own criterion, 14 in all. None is missing.
- Each criterion is one behavior, so size is ok.
- I ran the plan's new tests: all 18 cases fail today because the feature isn't built yet. None fails from a crash or a bad path.
- The plan's edits to older test files leave the other tests passing, except one. That one changed test, the 15-word first-line cap test, fails today. It now expects the "User:" label not to be counted, so it should pass once the feature is built.

**The blocker (criteria 707.1 and 707.2: changing or deleting the owner's test)**
- Today the plan check lets an older test be changed or deleted if the plan gives a reason.
- If the new code treats the owner's tests the same way, both tests still pass. Its rejection message (`dokima/planner.py:442`) contains both "changed" and "deleted", which is all the tests look for.
- That would let the planner change or drop the owner's tests just by giving a reason. The owner asked that their tests are never changed or dropped.
- Fix: in each test, also give a reason for the change and still expect the plan to be rejected.

**Left for the owner**
- I didn't answer the planner's question: should the owner's own tests skip the new docstring rules? The owner's words don't settle it, so it waits for them.
- The planner set the User, Verified by and Edge lines to 15 words each. The approved plan only says "its word cap"; the planner took 15 from the docstring cap set in #239. I didn't block on it.

# reviewer (plan) for #559

Run: https://github.com/dokima-dev/dokima/actions/runs/38673347184

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (43.4KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/3b017e93-05ba-4ea4-b2cc-5b18bc8cf5ea/tool-results/b5jlz81bu.txt
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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #559: Tests are the spec: I write tests, the planner maps them, every text is a short and full pair
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 560, 667, 668 -->
> <!-- dokima-blocking: {"blocked_by": [666, 667, 668, 670], "blocks": [], "loop": []} -->
> The owner's tests lead the plan, stay locked, and every text the owner reads comes short with full detail folded.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/667
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/670
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/470
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/335
> - https://github.com/dok

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #559: Tests are the spec: I write tests, the planner maps them, every text is a short and full pair
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 560, 667, 668 -->
> <!-- dokima-blocking: {"blocked_by": [666, 667, 668, 670], "blocks": [], "loop": []} -->
> The owner's tests lead the plan, stay locked, and every text the owner reads comes short with full detail folded.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/666
> - https://github.com/dokima-dev/dokima/issues/667
> - https://github.com/dokima-dev/dokima/issues/668
> - https://github.com/dokima-dev/dokima/issues/670
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/470
> - https://github.com/dokima-dev/dokima/issues/517
> - https://github.com/dokima-dev/dokima/issues/546
> - https://github.com/dokima-dev/dokima/issues/335
> - https://github.com/dokima-dev/dokima/issues/560
> - https://github.com/dokima-dev/dokima/issues/612
> - https://github.com/dokima-dev/dokima/issues/435
> - https://github.com/dokima-dev/dokima/issues/667
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; cat plan.json; cat parent.json | head -50; cat open_issues.json | head -30
```

> []{
>  "kind": "feature",
>  "title": "Tests are the spec, and every text has two halves",
>  "summary": "The owner's tests lead the plan, stay locked, and every text the owner reads comes short with full detail folded.",
>  "feature": "Stories: (1) tests locked. (2) every role reads the ask. (3, 4) short and full texts. (5, 6, 7, 8) prompts. (9, 10) owner's commits.",
>  "stories": [
>   {
>    "title": "The plan check locks my tests and checks test docstrings",
>    "user_story": "Tests the owner writes stay exactly as written, and every new test explains itself in one shape.",
>    "context": "Owner's tests are tests added by commits on the branch whose author is not the bot (agent commits are authored by dokima-runtime[bot] and only co-credit the owner). The check lives in dokima/planner.py (problems, unsummarized, unnumbered, docstring_caps); agent_checks.worker_docstring_caps reuses planner.docstring_caps. The worker's fence already restores every test file. The Edge line is optional and capped when present. Newer words here win over open issue 546, which asked for fixed rigor kinds.",
>    "acceptance_criteria": [
>     {
>      "text": "A plan that changes a test the owner committed is rejected, naming that test.",
>      "words": "My tests are locked: agents may propose more but never change or drop mine.",
>      "source": "https://github.com/dokima-dev/dokima/issues/559",
>      "files": [
>       "dokima/planner.py"
>      ],
>      "edge_cases": [
>       {
>        "case": "A branch with no commits by

`4. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['01-planner.json','02-reviewer-plan.json','03-planner.json']:
    d=json.load(open(f)); print(f, list(d.keys()))
"; python3 -c "
import json;d=json.load(open('03-planner.json'));print(json.dumps({k:v for k,v in d.items() if k not in ('handback',)},indent=1)[:3000])"
```

> 01-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 02-reviewer-plan.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 03-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38673093201",
>  "commit_before": "cfb11e4519569d5ea3fdade9e1ce41dad37b38bd",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 90323,
>   "turns": 15,
>   "cost_usd": 0.7756149999999999,
>   "tokens_in": 769966,
>   "tokens_out": 9001
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/559/38673093201-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38673093201",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/559#issuecomment-6183278645"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git status; ls tests | grep -E "owner|docstring|parent_detail|text_pairs|card_pairs|owner_commits|owner_edits"; grep -n "edge_cases\|\"test\"" dokima/planner.py | head -40
```

> cfb11e4 Setup gathers and stores a subscription's inputs (#702)
> c5c273b Stories sharing a code file take turns to build (#701)
> a2e94e1 Code groups criteria into stories by shared files (#695)
> On branch try/issue-559
> Your branch is up to date with 'origin/main'.
> 
> nothing to commit, working tree clean
> test_criteria_quote_owner.py
> 259:def check_edge_cases(where, c, filed):
> 261:    cases, why = c.get("edge_cases"), c.get("no_edge_cases")
> 264:            raise Garbled(f"{where} needs its edge_cases, each with the test covering it, or no_edge_cases saying "
> 268:        raise Garbled(f"{where} needs edge_cases as a list of cases, each with the test covering it")
> 272:        if not isinstance(e.get("test"), str) or not e["test"].strip():
> 274:        if e["test"].strip() not in filed:
> 341:        check_edge_cases(where, c, filed)

**Agent:** Reading the plan check code to see whether a split plan needs tests yet.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 240,420p dokima/planner.py; grep -n "split\|stories" rules/splitting.md | head -40
```

> if d == n - 1:
>                 raise Garbled(f"story {n} depends on itself")
>     state = {}  # index -> "open" while on the path, "done" once every story it waits on is clear
> 
>     def visit(i, path):
>         state[i] = "open"
>         for d in stories[i]["depends_on"]:
>             if state.get(d) == "open":
>                 loop = path[path.index(d):]
>                 raise Garbled("stories wait on each other in a loop: " + ", ".join(f"story {j + 1}" for j in loop))
>             if d not in state:
>                 visit(d, path + [d])
>         state[i] = "done"
> 
>     for i in range(len(stories)):
>         if i not in state:
>             visit(i, [i])
> 
> 
> def check_edge_cases(where, c, filed):
>     """Garbled unless C lists edge cases, each with a FILED test, or why none."""
>     cases, why = c.get("edge_cases"), c.get("no_edge_cases")
>     if cases is None or cases == []:
>         if not isinstance(why, str) or not why.strip():
>             raise Garbled(f"{where} needs its edge_cases, each with the test covering it, or no_edge_cases saying "
>                           f"why it has none")
>         return
>     if not isinstance(cases, list):
>         raise Garbled(f"{where} needs edge_cases as a list of cases, each with the test covering it")
>     for e in cases:
>         if not isinstance(e, dict) or not isinstance(e.get("case"), str) or not e["case"].strip():
>             raise Garbled(f"{where} has an edge case with no case saying what it is")
>         if not isinstance(e.get("test"), str) or not 

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "test" dokima/fence.py | head -30; grep -n "owner_words" dokima/agent_roles.py | head; grep -n "def route" -A30 dokima/agent_roles.py | grep -n "review" | head
```

> 1:"""The fence: after the worker stops, only in-scope changes survive and the planner's tests are exactly as committed.
> 3:The judges (all tests, each criterion's check) run on fresh machines from what gets pushed, so nothing the worker does to
> 4:its own machine reaches them. What gets pushed is decided here, by code: every test file and test setup file is put back
> 14:TEST_SETUP = {"conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"}
> 34:    """A plan's scope: every file its criteria list, plus its tests' files, sorted."""
> 37:    return sorted(files | {t.split("::")[0].strip() for names in plan.get("tests", {}).values() for t in names})
> 40:def is_test(path):
> 41:    """Say whether a path is a test or test setup file, which the worker may never change."""
> 43:    return path.startswith("tests/") or "/tests/" in path or name.startswith("test_") or name in TEST_SETUP
> 52:    """Undo every change since base that is a test file or outside scope; return the dropped paths, sorted.
> 58:    dropped = sorted(p for p in changed if (is_test(p) and p not in TEST_SETUP & set(scope)) or p not in allowed)
> 105:def owner_words(repo, number, d, items, owners):
> 143:        json.dump(owner_words(repo, number, d, items, owners), open(os.path.join(dest, "owner_words.json"), "w"), indent=1)
> 4:242-    /review on an issue grades the plan; on a pull request it grades the work. A pull request routes to its issue.
> 14:252-    stage = ("pr" if on_pr else "plan") if role == "reviewer" else ""
> 20

**Agent:** Writing the review now.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/559"
C1=I+"#issuecomment-6131843348"; C2=I+"#issuecomment-6132026430"; C3=I+"#issuecomment-6183274943"
asks=[
("I write tests, as many or as few as I like, or none.",I,"S1.3"),
("The planner groups tests into criteria, fills gaps with its own tests, and splits work that is too big.",I,"S1.3"),
("My tests are locked: agents may propose more but never change or drop mine.",I,"S1.1"),
("A short text for me (capped, plain, no code)",I,"S3.7"),
("a full text for agents (uncapped, may name code)",I,"S3.8"),
("raises, stories, Context and questions live in the record as pairs.",I,"S3.1"),
("Cards show short texts and fold full ones.",I,"S4.1"),
("The plan reviewer checks each short text matches its full text",I,"S5.1"),
("each docstring matches what its test does",I,"S6.1"),
("Every role working on a split story gets the parent's original issue and my comments",I,"S2.3"),
("I can add, change or delete tests, plan and code on Dokima's branches, then say /review.",I,"S2.6"),
("Anything I write counts as my words",I,"S2.5"),
("a re-plan keeps my commits",I,"S9.1"),
("My work goes through the same reviews and checks as agent work.",I,"S10.1"),
("A plan built on my tests keeps every one unchanged and maps each to a criterion.",I,"S1.3"),
("A worker on a split story reads the parent's original issue and my comments.",I,"S2.1"),
("my tests cannot be changed by an agent",I,"S1.2"),
("those json models should print out user facing and agent facing information",I,"S4.2"),
("tests should have structure: file docstring.",C1,"S1.11"),
("acceptance criteria docstring: user facing and agent facing",C1,"S4.3"),
("test docstrings user facing and agent facing",C1,"S1.6"),
("user facing for tests of course the methodology of testing so you know the rigor of test right of the bat.",C1,"S4.4"),
("edge cases too have user facing and agent facing texts",C1,"S1.10"),
("enforce this as a 
```

> rc=0

**Agent:** I blocked the plan for issue [#559](https://github.com/dokima-dev/dokima/issues/559) (tests are the spec, short and full texts) again, on round two. Every ask from you now has a criterion, but three criteria still pack two things into one. The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**What the planner fixed since my last review:**
- It added criteria for the asks that had none:
  - saying /review after you edit;
  - editing plans by comment;
  - a re-plan keeping your commits;
  - your commits getting the same code review and all-tests run.
- It split the old short-or-full checks into one criterion each.
- The planner prompt and the worker prompt now each have their own criterion for the Verified by line.

**Two blockers, both for the planner:**
- **S1.11** (a new test file must open with a user line, then agent detail) covers two cases: no user line, or no agent detail. It should be two criteria, the way S1.4 and S1.6 already are.
- **S4.1 and S4.2** (raises on the issue card and on run comments) each promise two results: the short half shown and the full half folded. Each should be two criteria, the way S4.4 and S4.5 already are.

**What I checked and accepted:**
- I matched 33 of your asks, from the issue, your comments and your answers, to criteria. None is missing.
- This plan proposes a split into stories, so no test files exist yet. Each story's own plan writes its tests later, so I graded no tests.
- I raised no edge-case gaps.
- No questions or earlier blockers were waiting on me.

**For you to know:** stories 9 and 10 name two workflow files only to pin behaviour that already works today; the plan expects no workflow change. If a build does touch a workflow file, it stops for your approval anyway.

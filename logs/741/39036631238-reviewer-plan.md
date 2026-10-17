# reviewer (plan) for #741

Run: https://github.com/dokima-dev/dokima/actions/runs/39036631238

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat plan.json; cat open_blockers.json
```

> total 24
> drwxr-xr-x 2 runner runner  4096 Oct 17 13:27 .
> drwxr-xr-x 3 runner runner  4096 Oct 17 13:27 ..
> -rw-r--r-- 1 runner runner 13653 Oct 17 13:27 01-planner.json
> # Issue #741: Generic role prompts with repo-appended house rules
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 781, 784, 787, 793, 796 -->
> <!-- dokima-blocking: {"blocked_by": [779, 781, 784, 787], "blocks": [746], "loop": []} -->
> The shipped role prompts drop Dokima's own examples, share one raising text, and spell out planner questions and reviewer duties.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234407130) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/784
> - https://github.com/dokima-dev/dokima/issues/787
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icon

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:4000]); print(d.keys())"; cd /home/runner/work/dokima/dokima; git status; git log --oneline -3; ls tests | grep -i -E "role|box|prompt"
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39036402042",
>  "commit_before": "edf1c0e0800fbd616670940fb81b53445a839682",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 152420,
>   "turns": 16,
>   "cost_usd": 1.0984703999999998,
>   "tokens_in": 958865,
>   "tokens_out": 16055
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/741/39036402042-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39036402042",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/741#issuecomment-6234407130"
> }
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> On branch try/issue-741
> Your branch is up to date with 'origin/main'.
> 
> nothing to commit, working tree clean
> edf1c0e Autopilot merges by the repo's branch, method and labels (#810)
> 840c660 Required checks, labels and the audit follow settings (#809)
> 17b9275 Planner's test limits and docstrings follow settings (#808)
> test_planner_prompt.py
> test_settings_prompts.py

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; grep -n -i "split" rules/flow.md rules/raising.md | head -40; python3 -m dokima.agent --help 2>&1 | head; grep -n "def check_review\|asks\|S<s>\|split" dokima/agent_checks.py | head -60
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> rules/flow.md:4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. I

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 300,460p dokima/agent_checks.py
```

> crit = h.get("criteria")
>     if not isinstance(crit, dict) or not crit:
>         bad.append("criteria must be an object giving one line per criterion")
>     else:
>         bad += [f"criteria: the line for {k} must be non-empty text" for k, v in crit.items() if not filled(v)]
>     if not filled(h.get("evidence")):
>         bad.append("evidence must name the last test command and its result line")
>     return bad
> 
> 
> def plan_criteria(plan, number):
>     """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each
>     story of a split."""
>     count = lambda p: sum(len(p.get(k)) for k in ("acceptance_criteria", "non_functional") if isinstance(p.get(k), list))
>     if plan.get("kind") == "feature":
>         stories = plan.get("stories") if isinstance(plan.get("stories"), list) else []
>         return [f"S{s}.{k}" for s, st in enumerate(stories, 1) if isinstance(st, dict) for k in range(1, count(st) + 1)]
>     return [f"{number}.{k}" for k in range(1, count(plan) + 1)]
> 
> 
> def problems_plan(kind, h, plan, number):
>     """Everything in a work.json that does not match the plan: one line per criterion."""
>     ids = plan_criteria(plan, number)
>     bad = []
>     if kind == "work":
>         crit = h.get("criteria")
>         if isinstance(crit, dict):
>             bad += [f"criteria has no line for {c}, a criterion of the plan" for c in ids if c not in crit]
>             bad += [f"criteria gives a line for {c}, which the plan does not have" for c in crit if c not

`5. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/roles; wc -l dokima/roles/*; grep -n -E "max_questions|max_blocks|append" dokima/settings*.py dokima/*.yaml 2>/dev/null | head -20; grep -n -E "AGENTS|pytest|tests/|more than 3|three blocks|\{" dokima/roles/planner.md dokima/roles/worker.md dokima/roles/reviewer.md | head -40
```

> plan-grade.md
> planner.md
> result-grade.md
> reviewer.md
> style.md
> worker.md
>    58 dokima/roles/plan-grade.md
>   228 dokima/roles/planner.md
>    34 dokima/roles/result-grade.md
>   150 dokima/roles/reviewer.md
>    30 dokima/roles/style.md
>   104 dokima/roles/worker.md
>   604 total
> dokima/settings.py:25:BY_NAME = {"gates.required", "prompts.append"}  # lists that merge with the default ones by name
> dokima/settings.py:56:            out.append(entry)
> dokima/settings.py:98:        lines.append(f"{name}={value}")
> dokima/settings.py:143:        lines.append(f"{name}={value}")
> dokima/defaults.yaml:52:  max_blocks: 3
> dokima/defaults.yaml:54:  max_questions: 3
> dokima/defaults.yaml:94:  append:
> dokima/roles/planner.md:19:ticket, against the code and AGENTS.md:
> dokima/roles/planner.md:23:- Does it contradict AGENTS.md or another open issue? Does it use one word for two things?
> dokima/roles/planner.md:56:- **Definition of Done:** one global checklist in AGENTS.md (every criterion has a passing test, all tests pass,
> dokima/roles/planner.md:99:- Scope: `dokima/card.py`, `tests/test_card.py`.
> dokima/roles/planner.md:115:Current runner (the only one Dokima supports today): python3 -m pytest, tests in tests/, and each test names its criterion with
> dokima/roles/planner.md:142:  {"raise": "R1", "answer": "done" | "disagree", "why": "..."}. Done means you did what it asks; disagree needs
> dokima/roles/planner.md:147:  {"raise": "P1", "answer": "done", "why": "...", "words": "the owner's words", "source": "t

**Agent:** Checking whether the runner line and AGENTS.md mentions are already swapped by the prompt builder.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -E "AGENTS|runner|Current runner|replace|append|max_questions|max_blocks|caps" dokima/prompt.py | head -40; sed -n 40,60p dokima/defaults.yaml; sed -n 85,100p dokima/defaults.yaml
```

> 4:GRADE.md, ROLE.md) with the settings drawn in: the owner docs file in place of AGENTS.md, the protected paths in the
> 5:worker's never-edit line, the test settings in the planner's runner line and the caps setting in the caps table.
> 20:# Each cap's row in the style prompt's caps table.
> 27:RUNNER = re.compile(r"^Current runner .*\n.*\n", re.M)
> 37:def caps_table(text, caps):
> 38:    """TEXT with each caps table row showing its cap from CAPS."""
> 40:        if key in caps:
> 41:            text = re.sub(rf"^\| {re.escape(label)} \| \d+ \|$", f"| {label} | {caps[key]} |", text, flags=re.M)
> 45:def runner_line(tests):
> 46:    """The planner's runner line, drawn from the test settings."""
> 47:    return (f"Current runner: `{tests['run_all']}` runs every test and `{tests['run_one']}` one, tests in "
> 54:    text = caps_table(text, got["style"]["caps"])
> 55:    text = RUNNER.sub(lambda m: runner_line(got["tests"]), text)
> 58:    return text.replace("AGENTS.md", str(got["owner_docs"]))
> 63:    return [str(a["file"]) for a in got["prompts"]["append"] or [] if isinstance(a, dict) and a.get("file")]
> 83:                out.append(rules)
>     story_title: 10
>     story_user_story: 20
>     raise_label: 4
>     question: 20
>     blocker: 30
>     issue: 25
>     evidence: 20
>     answer_why: 20
>     previous_step: 15
>     work_evidence: 15
>     test_change: 15
> river:
>   max_blocks: 3
> planner:
>   max_questions: 3
> gates:
>   required: [all tests, Acceptance criteria]
> gate:
>   checks_wait_min: 45
>   exclude: [card, board wa

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 58,95p dokima/prompt.py; grep -n "796.7\|796.8\|def test" tests/test_settings_prompts.py | head -30; python3 -m pytest -q tests/test_settings_prompts.py 2>&1 | tail -2
```

> return text.replace("AGENTS.md", str(got["owner_docs"]))
> 
> 
> def files(got):
>     """The prompt additions' files, as the settings name them."""
>     return [str(a["file"]) for a in got["prompts"]["append"] or [] if isinstance(a, dict) and a.get("file")]
> 
> 
> def for_role(text, role):
>     """House rules TEXT for ROLE, less other roles' `## <role>` sections."""
>     parts = re.split(r"^(?=## )", text, flags=re.M)
>     keep = [p for p in parts if not (p.startswith("## ") and p[3:].split("\n")[0].strip().lower() in ROLES
>                                       and p[3:].split("\n")[0].strip().lower() != role)]
>     return "".join(keep).strip()
> 
> 
> def house(role, got, root="."):
>     """ROLE's house rules from every prompt addition file under ROOT; empty when none."""
>     out = []
>     for path in files(got):
>         full = os.path.join(root, path)
>         if os.path.isfile(full):
>             with open(full) as f:
>                 rules = for_role(f.read(), role)
>             if rules:
>                 out.append(rules)
>     return "\n\n".join(out)
> 
> 
> def main(argv):
>     """Prints a prompt, a role's house rules or the addition files; exits 1 saying why."""
>     try:
>         got = settings.read()
>         if argv[:1] == ["files"]:
>             print("\n".join(files(got)))
>         elif argv[:1] == ["house"] and len(argv) == 2:
>             rules = house(argv[1], got)
>             if rules:
> 42:    box.commit(f"try/issue-{N}", {"tests/test_x.py": 'def test_a():\n    """A."""\n', **(branch_files or {})},
> 73:  

**Agent:** Now drafting the review; checking what the checker requires for the tests field.

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def problems_tests" -A25 dokima/agent_checks.py; grep -n "def problems_size" -A20 dokima/agent_checks.py | head -30
```

> 145:def problems_tests(r, plan):
> 146-    """A plan review must judge every test the plan names: does it check only its
> 147-    criterion's behavior, with the edge cases the owner named or normal use hits? A false one never approves."""
> 148-    named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if isinstance(ts, list) for t in ts})
> 149-    rows = r.get("tests") if isinstance(r.get("tests"), list) else []
> 150-    seen = {str(x.get("test")): x for x in rows if isinstance(x, dict)}
> 151-    bad = [f"tests has no judgment of `{t}`: say only_its_behavior true or false, and why in one line"
> 152-           for t in named if not (isinstance(seen.get(t, {}).get("only_its_behavior"), bool)
> 153-                                  and str(seen.get(t, {}).get("why") or "").strip())]
> 154-    wide = [t for t, x in seen.items() if x.get("only_its_behavior") is False]
> 155-    if wide and r.get("verdict") == "approve":
> 156-        bad.append(", ".join("`" + t + "`" for t in wide) + f" check more than their criterion's behavior, so the verdict cannot be approve")
> 157-    return bad
> 158-
> 159-
> 160-def problems_size(r, ids=()):
> 161-    """A plan review must judge each criterion one behavior or not, in `behaviors`, and say
> 162-    whether the plan keeps the size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks
> 163-    it; a plan that breaks it is never approved."""
> 164-    bad = []
> 165-    rows = r.get("behaviors") if isinstance(r.get("behaviors")

**Agent:** Writing the hand-back.

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner proposes three stories: generic prompts, reviewer duties in its prompt, code checks for the boxes."],
  "decided": ["House rules per role count as already done, so no criterion carries them.", "The boxes apply at both review stages."],
  "open": ["Three questions for the owner: rewrite size, house rules already done, which review stage."]
 },
 "verdict": "block",
 "summary": "Blocked: house rules from the owner's done line have no criterion, and two criteria bundle two behaviors.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion",
   "text": "The owner's done line asks that house rules appear after the shipped prompt for each role. No criterion carries it. Smallest fix: one criterion, proved by the existing tests on main.",
   "evidence": "Issue body, Done when; `tests/test_settings_prompts.py` 796.7 and 796.8 pass on main."},
  {"kind": "blocker", "to": "planner", "label": "Two behaviors",
   "text": "S1.7 bundles what a criterion needs with turning each gap into a question. S2.2 bundles later words win with confirming or retiring a flagged criterion. Split each in two.",
   "evidence": "plan.json, story 1 criterion 7 and story 2 criterion 2 each join two rules with a semicolon or and."},
  {"kind": "blocker", "to": "planner", "label": "Missing normal case",
   "text": "S3.2 tests only a missing field. An entry with a wrong value, such as an added kind other than creep or needed, is normal use. Add it.",
   "evidence": "Owner's comment shapes kind as creep or needed; S3.2 lists no edge cases."},
  {"kind": "question", "to": "owner", "label": "Boxes beside or instead",
   "text": "Do the six boxes replace the review's existing asks, edge case and test lists, or sit beside them? The plan seems to add them beside.",
   "evidence": "`dokima/roles/reviewer.md` already asks for asks, edge_cases and tests; story 3 says nothing about t
```

> Exit code 1
> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts
> raise 4's text holds 25 words, over its cap of 20: cut 5, keep the facts
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`10. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d['previous_step']['did'][0]="The planner proposes three stories: generic prompts, reviewer duties, code checking the boxes."
d['raises'][0]['text']="The owner's done line asks that house rules appear after the shipped prompt for each role. No criterion carries it. Smallest fix: one criterion, proved by existing tests."
d['raises'][3]['text']="Do the six boxes replace the review's asks, edge case and test lists, or sit beside them? The plan reads beside."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; STAGE=plan python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 741 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> raise 4's text holds 21 words, over its cap of 20: cut 1, keep the facts
> exit 1

`11. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;p='review.json';d=json.load(open(p))
d['raises'][3]['text']="Do the six boxes replace the review's asks, edge case and test lists, or sit beside them? Plan reads beside."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; STAGE=plan python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 741 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo exit $?
```

> exit 0

**Agent:** I blocked the planner's proposed split for [#741](https://github.com/dokima-dev/dokima/issues/741) (shipped prompts that fit any repo). The review is in `/tmp/dokima-out/review.json` and passes both checks.

The planner proposes three stories:
1. Generic prompts and the planner's questions.
2. The reviewer's duties and boxes written into its prompt.
3. Code that checks those boxes.

**What goes back to the planner:**
- **A done item has no criterion.** The owner's "Done when" line says a repo's house rules appear after the shipped prompt for each role, and no criterion carries it. It already works on main: the existing tests 796.7 and 796.8 pass when I run them. The smallest fix is one criterion proved by those tests.
- **Two criteria each hold two behaviors.** S1.7 combines "what a criterion needs" with "each gap becomes a question". S2.2 combines "later words win" with "confirm or retire a criterion flagged as stale". Each needs splitting in two.
- **A normal case is missing.** S3.2 tests only a box entry with a missing field. It should also reject an entry with a wrong value, such as an added entry whose kind is neither "creep" nor "needed".

**My question for you:** do the six new boxes replace the review's current asks, edge case and test lists, or sit beside them? The plan reads them as sitting beside, but never says so.

The planner's three questions are still waiting for you: whether the rewrite percentages are estimates, whether house rules count as already done, and whether the boxes apply at both review stages. I answered none of them for you, because your own words don't settle them.

Two of your asks have no criterion: house rules, which the first blocker covers, and the rewrite size with the grade prompts staying as they are. The planner's questions cover both. The split itself follows the story rules, and story 3 is separate because it changes a different file. There are no tests to run yet: each story gets its own plan and tests once the split is approved.

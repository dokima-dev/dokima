# reviewer (plan) for #750

Run: https://github.com/dokima-dev/dokima/actions/runs/39103677808

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 116
> drwxr-xr-x  3 runner runner  4096 Oct 18 06:20 .
> drwxrwxrwt 18 root   root    4096 Oct 18 06:20 ..
> drwxr-xr-x  2 runner runner  4096 Oct 18 06:20 in
> -rw-r--r--  1 runner runner 13403 Oct 18 06:20 issue.md
> -rw-r--r--  1 runner runner     2 Oct 18 06:20 open_blockers.json
> -rw-r--r--  1 runner runner 63088 Oct 18 06:20 open_issues.json
> -rw-r--r--  1 runner runner  3164 Oct 18 06:20 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 18 06:20 parent.json
> -rw-r--r--  1 runner runner 10774 Oct 18 06:20 plan.json
> 
> in:
> total 44
> drwxr-xr-x 2 runner runner  4096 Oct 18 06:20 .
> drwxr-xr-x 3 runner runner  4096 Oct 18 06:20 ..
> -rw-r--r-- 1 runner runner 10708 Oct 18 06:20 01-planner.json
> -rw-r--r-- 1 runner runner  9304 Oct 18 06:20 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 11671 Oct 18 06:20 03-planner.json
> # Issue #750: Hotfix label: a small fix builds from its issue text, planning skipped, review kept
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A hotfix label lets a small fix skip planning, while code review, all tests and the merge gate still run.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/748
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmidd

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:9000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/750": "Owner decision 2026-10-15, rescoped by the owner 2026-10-18 (\"yes 750 hotfix\"): the fast lane is a **label**, not a verb, so it works on autopilot now, before the `@dokima` grammar (#748). #748 can later add `@dokima hotfix` as one more way to put the label on.\n\n**What**\n- An issue labeled `hotfix` skips planning and plan review. When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text: the text is the whole ask.\n- Code review still runs and judges the diff against the issue's text; it is the judgment gate. All tests and the merge gate still run, as for any pull request.\n- The worker may add or change a small test that pins the fix (as #856 pinned the install docs' check names).\n- Only small asks take the lane: a change the issue names in a sentence or two, touching few files. When code review finds the change bigger than the ask, or the worker finds the ask needs a design choice, it goes back to normal planning, saying why.\n- The card shows one line: the ask, the PR, the review verdict, the gate.\n- Every hotfix PR carries the `hotfix` label and links the issue it answers.\n\n**The loop it completes:** a worker raises a problem; the raise files as an issue that blocks the parent (#268); someone labels it `hotfix`; it lands; the parent restarts by itself when its blocker merges (#213). Hotfixes accumulate as a labeled, linked record; many in one 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/agent_roles.py dokima/agent_autopilot.py dokima/agent_next.py dokima/agent_checks.py dokima/fence.py dokima/agent_records.py dokima/plan.py dokima/card.py dokima/roles/worker.md dokima/roles/reviewer.md .github/workflows/agent.yml .github/workflows/commands.yml; grep -n "S<s>\|split" rules/specs.md rules/splitting.md | head -30
```

> .github/workflows/agent.yml
> .github/workflows/commands.yml
> dokima/agent_autopilot.py
> dokima/agent_checks.py
> dokima/agent_next.py
> dokima/agent_records.py
> dokima/agent_roles.py
> dokima/card.py
> dokima/fence.py
> dokima/plan.py
> dokima/roles/reviewer.md
> dokima/roles/worker.md
> rules/splitting.md:5:- The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/750"
C=I+"#issuecomment-6246479912"
ids=[f"S1.{k}" for k in range(1,11)]+[f"S2.{k}" for k in range(1,10)]+["S2.N1"]
why={
"S1.1":"One result: the work command starts the worker with no plan.",
"S1.2":"One result: on autopilot the worker starts instead of the planner.",
"S1.3":"One result: the worker's pack holds the issue text as the ask.",
"S1.4":"One result: the worker's code change stays on the pull request.",
"S1.5":"One result: code review starts.",
"S1.6":"One result: the review's pack holds the issue text as the ask.",
"S1.7":"One result: the usual checks run on the pull request.",
"S1.8":"One result: the worker's test change stays.",
"S1.9":"One result: the planner starts.",
"S1.10":"One result: a comment saying why.",
"S2.1":"One result: the hotfix label on the pull request.",
"S2.2":"One result: the pull request links its issue.",
"S2.3":"One result: the planner starts.",
"S2.4":"One result: a comment saying why.",
"S2.5":"One result: the card state fits one line.",
"S2.6":"One result: the line shows the ask.",
"S2.7":"One result: the line links the pull request.",
"S2.8":"One result: the line shows the verdict.",
"S2.9":"One result: the line shows the gate.",
"S2.N1":"One result: hotfix prompt parts name nothing of this repo.",
}
asks=[
("An issue labeled `hotfix` skips planning and plan review.",I,"S1.2"),
("When its turn comes (by hand, or on autopilot once nothing open blocks it)",I,"S1.2"),
("By hand, the owner's `/work` starts a hotfix's worker.",C,"S1.1"),
("the worker builds straight from the issue's text: the text is the whole ask.",I,"S1.3"),
("Fix the review's two blockers.",C,"S1.4"),
("Code review still runs",I,"S1.5"),
("judges the diff against the issue's text; it is the judgment gate.",I,"S1.6"),
("All tests and the merge gate still run, as for any pull request.",I,"S1.7"),
("The worker may add or change a small test tha
```

> Exit code 1
> the edges box has no line for criterion S2.10: say covered or missing: the case
> the ask "keep the prompts free of anything about Dokima's own repo, so they fit any repo." is matched to S2.N1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S1.4, S1.5, S1.6, S1.7, S1.8, S1.9, S1.10, S2.1, S2.2, S2.3, S2.4, S2.5, S2.6, S2.7, S2.8, S2.9, S2.10)
> behaviors has no judgment of criterion S2.10: say one_behavior true or false, and why in one line
> edge_cases has no judgment of criterion S2.10: list the exotic cases it cuts and the normal-use ones missing, each [] when there are none

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/S2\.N1/S2.10/g' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 750 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#750](https://github.com/dokima-dev/dokima/issues/750) (hotfix label: a small fix skips planning). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's two blockers are fixed.** A new criterion keeps the worker's fix on the pull request, and code review starting is now split from what it judges the change against.
- **Your answer is in the plan.** Your `/work` command starts a hotfix's worker by hand. One criterion keeps the worker and reviewer instructions free of anything about Dokima's own repo.
- **Every ask now has a criterion.** That covers the label, the link to the issue, the one-line card, and going back to planning with a reason why.
- **Each criterion is one behavior,** and each story has 10 criteria, which is the limit.
- **Size is ok.**
- **I raised nothing.** No blockers were open for me to answer.

The plan has no tests yet: each story's own planner writes them when it plans that story.

The plan changes `dokima/card.py` and the worker and reviewer instructions in `dokima/roles/`. `AGENTS.md` protects those files unless the issue asks for the change. I let it through: you approved the instruction changes, and the issue itself asks for the one-line card.

Your issue says to keep hotfixes apart from `/work`. Your later comment, which wins, says `/work` starts one by hand. So I didn't raise this as a conflict.

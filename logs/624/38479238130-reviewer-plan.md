# reviewer (plan) for #624

Run: https://github.com/dokima-dev/dokima/actions/runs/38479238130

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
> # Issue #624: One command draws Dokima's posts from any branch
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [625, 626], "loop": []} -->
> Our own command draws a real issue's card, run comments and autopilot comments with any branch's code.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/625
> - https://github.com/dokima-dev/dokima/issues/626
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/584
> - https://github.com/dokima-dev/dokima/issues/627
> - https://github.com/dokima-dev/dokima/issues/628
> 
> 
> **User story:** We see exactly what Dokima would post on a real issue, drawn by any branch's code.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The command draws a real issue's top card with t

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:6000])"; cat parent.json | head -c 3000; cd /home/runner/work/dokima/dokima; git diff HEAD~1 --stat; ls tools
```

> Exit code 2
> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38478905164",
>  "commit_before": "40071025f46464673292dc01930597c79bde1457",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 53425,
>   "turns": 10,
>   "cost_usd": 0.5294388,
>   "tokens_in": 472914,
>   "tokens_out": 5476
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/624/38478905164-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38478905164",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote one command's plan with three criteria and seven tests.",
>     "The tests run the command against a throwaway repo and a fake GitHub."
>    ],
>    "decided": [
>     "The command lives in our own tools folder, outside Dokima itself."
>    ],
>    "open": [
>     "No questions for the owner."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan is right, but the autopilot test skips the merge lines every autopilot issue gets.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "3: merge lines untested",
>     "text": "Criterion 3's test skips merge lines, so code ignoring `AUTOPILOT_MERGE` passes. Fix: add an `Autopilot: merged PR #9` comment, override `AUTOPILOT_MERGE` in `BRANCH_AGENT`, assert it shows.",
>     "evidence": "`tests/test_visuals_draw.py::test_autopilot_comments_from_branch` checks three lines; `dokima/agent.py:2361` posts merge lines on every autopilot merge.",
>     "raised_by": 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git diff HEAD~1; sed -n 320,400p tests/test_visuals_draw.py; timeout 300 python -m pytest -q tests/test_visuals_draw.py 2>&1 | tail -15
```

> diff --git a/tests/test_visuals_draw.py b/tests/test_visuals_draw.py
> index 0c3556a..cfd294c 100644
> --- a/tests/test_visuals_draw.py
> +++ b/tests/test_visuals_draw.py
> @@ -142,6 +142,9 @@ def autopilot_comment(*a, **k):
>  
>  AUTOPILOT_LINE = "Autopilot: BRANCH blockers line"
>  AUTOPILOT_LINES = {"worker": "Autopilot: BRANCH work line", "split": "Autopilot: BRANCH split line"}
> +AUTOPILOT_START_LINE = "Autopilot: BRANCH switch line"
> +AUTOPILOT_MERGE = {"merged": "Autopilot: BRANCH merged PR #{pr}", "queued": "Autopilot: BRANCH PR #{pr} queued",
> +                   "waits": "Autopilot: BRANCH PR #{pr} waits"}
>  '''
>  
>  
> @@ -174,16 +177,18 @@ def comment(k, login, body):
>  
>  
>  def world():
> -    """The fake GitHub: issue 7 with two records and three autopilot comments.
> +    """The fake GitHub: issue 7 with two records and five autopilot comments.
>  
>      Every comment but the owner's `/plan` is by the bot; issue 8 is refused."""
>      planner, review = records()
>      comments = [comment(1, "reza", "/plan"),
>                  comment(2, BOT, "Autopilot: blockers merged, starting plan"),
> +                comment(7, BOT, "Autopilot: switched on, starting plan"),
>                  comment(3, BOT, agent.render(planner)),
>                  comment(4, BOT, agent.render(review)),
>                  comment(5, BOT, "Autopilot: plan approved, starting work"),
> -                comment(6, BOT, f"Autopilot is on for #{ISSUE}. No stage was started.\n")]
> +                comment(6, BOT, f"Autopilot is on for #{

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^AUTOPILOT\|AUTOPILOT_MERGE\[" dokima/agent.py | head; sed -n 120,160p tests/test_visuals_draw.py
```

> 1643:AUTOPILOT = "autopilot"
> 1690:AUTOPILOT_LINE = "Autopilot: blockers merged, starting plan"
> 1691:AUTOPILOT_START_LINE = "Autopilot: switched on, starting plan"
> 2154:AUTOPILOT_LINES = {"worker": "Autopilot: plan approved, starting work", "split": "Autopilot: split approved, filing its stories"}
> 2361:AUTOPILOT_MERGE = {"merged": "Autopilot: merged PR #{pr}", "queued": "Autopilot: PR #{pr} joined the merge queue",
> 2413:        gh("issue", "comment", str(number), "-R", repo, "--body", AUTOPILOT_MERGE[how].format(pr=pr))
> 2631:    line = re.compile(re.escape(AUTOPILOT_MERGE["queued"]).replace(r"\{pr\}", r"\d+"))
> 
> def render(*a, **k):
>     """The branch's card: today's card under a marker."""
>     return "BRANCH-CARD\\n" + _visual_test_render(*a, **k)
> '''
> BRANCH_AGENT = '''
> 
> _visual_test_render = render
> 
> 
> def render(*a, **k):
>     """The branch's run comment: today's comment under a marker."""
>     return "BRANCH-RUN\\n" + _visual_test_render(*a, **k)
> 
> 
> _visual_test_switch = autopilot_comment
> 
> 
> def autopilot_comment(*a, **k):
>     """The branch's /autopilot reply: today's reply after a marker."""
>     return "BRANCH-SWITCH " + _visual_test_switch(*a, **k)
> 
> 
> AUTOPILOT_LINE = "Autopilot: BRANCH blockers line"
> AUTOPILOT_LINES = {"worker": "Autopilot: BRANCH work line", "split": "Autopilot: BRANCH split line"}
> AUTOPILOT_START_LINE = "Autopilot: BRANCH switch line"
> AUTOPILOT_MERGE = {"merged": "Autopilot: BRANCH merged PR #{pr}", "queued": "Autopilot: BRANCH PR #{pr} queued",
>               

**Agent:** Fix is in. Write the review.

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner added a merged pull request line and a switched on line to the autopilot test."],
  "decided": ["Both new lines are changed by the branch and checked as drawn from main too."],
  "open": ["No questions for the owner."]},
 "verdict": "approve",
 "summary": "The plan covers card, run comments and autopilot comments, and every test now fails only because the command is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "using the real drawing code from any branch", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.1"},
  {"ask": "the real records of a real issue", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.2"},
  {"ask": "That covers the top card, run comments and autopilot comments.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.3"}],
 "behaviors": [
  {"criterion": "624.1", "one_behavior": true, "why": "Draws the top card from the chosen branch."},
  {"criterion": "624.2", "one_behavior": true, "why": "Draws run comments from records."},
  {"criterion": "624.3", "one_behavior": true, "why": "Draws autopilot comments."}],
 "edge_cases": [
  {"criterion": "624.1", "cut": [], "missing": []},
  {"criterion": "624.2", "cut": [], "missing": []},
  {"criterion": "624.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_visuals_draw.py::test_card_from_branch", "only_its_behavior": true, "why": "Marker proves the branch's card code drew the real issue."},
  {"test": "tests/test_visuals_draw.py::test_mistyped_issue_says_so", "only_its_behavior": true, "why": "Checks the issue, GitHub's reason and no crash."},
  {"test": "tests/test_visuals_draw.py::test_unreadable_issue_says_so", "only_its_behavior": true, "why": "Checks the issue, GitHub's reason and no crash."},
  {"test": "t
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`6. Bash`
```
sed -i 's/The planner added a merged pull request line and a switched on line to the autopilot test./The planner added merged and switched on lines to the autopilot test./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 624 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#624](https://github.com/dokima-dev/dokima/issues/624) (one command draws Dokima's posts from any branch). The hand-back is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Last round's blocker is fixed.** The autopilot test now includes an `Autopilot: merged PR #9` line and an `Autopilot: switched on, starting plan` line. The branch's code changes both lines, including the merge lines, and the test checks each one drawn from the branch and from main.
- **Every new test fails for the right reason.** I ran all 7 tests and each failed with "`tools/visuals.py` does not exist yet", meaning the command hasn't been built. None failed from a crash or a bad path.
- **Every ask is covered.** The owner's comment on [#584](https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768) (preview every visual) asks for three things: the top card, run comments and autopilot comments, drawn by any branch's code. Each is one of the plan's three criteria, each criterion is one behavior, and size is ok.

There are no questions for the owner and no open raises to answer.

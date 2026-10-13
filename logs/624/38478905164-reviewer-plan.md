# reviewer (plan) for #624

Run: https://github.com/dokima-dev/dokima/actions/runs/38478905164

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

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
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The command draws a real issue's top card with the drawing code of a chosen branch.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-624/tests/test_

`2. Bash`
```
cat tests/test_visuals_draw.py; ls tools; git show --stat HEAD | head -20
```

> """One command draws what Dokima would post on a real issue, with any branch's code.
> 
> #624.
> 
> Story 1 of #584. Our own tool, outside the `dokima/` package, run from the root of a checkout:
> 
>     python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME
> 
> It takes the drawing code from BRANCH (for example through a git worktree of that branch, so the checkout it runs
> from is left as it is), reads the real issue from GitHub through `gh`, and prints to stdout what that branch's code
> would post: the issue's top card (`card.render`), every run comment drawn from the issue's real records
> (`agent.render`), and every autopilot comment of the issue (the `AUTOPILOT_*` lines and `agent.autopilot_comment`).
> An issue GitHub cannot give (a mistyped number, or GitHub refusing) or a branch that does not exist ends the command
> with a non-zero exit and one plain message naming it, never a traceback.
> 
> How the tests prove it: each test builds a throwaway git repo holding a copy of this repo's `dokima/` and `tools/`
> on `main`, plus a branch `visual-test` whose drawing code differs in ways no real code shows (markers such as
> BRANCH-CARD, changed autopilot lines). A fake `gh` on PATH answers for a real-looking issue #7 with real records and
> autopilot comments posted by the bot, and refuses every write. The command runs from the throwaway repo's root; a
> marker in its output can only come from the branch's own code, and a run with `--branch main` shows today's drawing.
> """
> import json
> import

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "AUTOPILOT_\|^def autopilot_comment\|^def render\|^MARK" dokima/agent.py | head -30; grep -n "^def render\|^def gather" dokima/card.py; timeout 300 python -m pytest -q tests/test_visuals_draw.py 2>&1 | tail -15; gh issue view 584 --repo dokima-dev/dokima --comments 2>&1 | tail -80
```

> 35:MARK = "<!-- dokima-record -->"
> 783:def render(rec, pr=None, plan=None, earlier=None):
> 920:def render_as_posted(rec, pr=None, plan=None, earlier=None):
> 1675:def autopilot_comment(number, switch, switched, started=(), picked=""):
> 1690:AUTOPILOT_LINE = "Autopilot: blockers merged, starting plan"
> 1691:AUTOPILOT_START_LINE = "Autopilot: switched on, starting plan"
> 1986:                MARK in body or LIVE in body or body.strip() in (AUTOPILOT_LINE, AUTOPILOT_START_LINE)):
> 1991:def start_planner(repo, number, line=AUTOPILOT_LINE):
> 2000:def start_waiting(repo, numbers, line=AUTOPILOT_LINE):
> 2033:    lines = (AUTOPILOT_LINE, AUTOPILOT_START_LINE, *AUTOPILOT_LINES.values())
> 2154:AUTOPILOT_LINES = {"worker": "Autopilot: plan approved, starting work", "split": "Autopilot: split approved, filing its stories"}
> 2361:AUTOPILOT_MERGE = {"merged": "Autopilot: merged PR #{pr}", "queued": "Autopilot: PR #{pr} joined the merge queue",
> 2412:    if how in AUTOPILOT_MERGE:
> 2413:        gh("issue", "comment", str(number), "-R", repo, "--body", AUTOPILOT_MERGE[how].format(pr=pr))
> 2631:    line = re.compile(re.escape(AUTOPILOT_MERGE["queued"]).replace(r"\{pr\}", r"\d+"))
> 2685:    if who in owners and command_of(body) == "worker" and "(approved)" not in c.get("where", "") or who in (BOT, f"{BOT}[bot]") and body == AUTOPILOT_LINES["worker"]:
> 2974:            open(os.path.join(out, "autopilot.md"), "w").write(AUTOPILOT_LINES[step[1]] + "\n")
> 3049:                open(os.path.join(argv[4], "autopilot.

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1670,1695p dokima/agent.py; python3 -c "
from dokima import agent;print(repr(agent.autopilot_comment(7,'start',[7])))"; grep -n "AUTOPILOT_MERGE\|merged PR" tests/test_visuals_draw.py
```

> gh("api", "-X", "DELETE", f"repos/{repo}/issues/{n}/labels/{AUTOPILOT}")
>             switched.append(n)
>     return switched
> 
> 
> def autopilot_comment(number, switch, switched, started=(), picked=""):
>     """The one comment `/autopilot start|stop` leaves where it was said: every issue it switched, every issue whose
>     planner it started, and what of the issue's own waiting work it picked up."""
>     names = ", ".join(f"#{n}" for n in switched)
>     if switch == "start":
>         said = f"Autopilot is on for {names}." if switched else f"#{number} and every issue under it were already on autopilot."
>     else:
>         said = f"Autopilot is off for {names}." if switched else f"No issue in #{number}'s tree was on autopilot."
>     if started:
>         said += f" Planning started for {', '.join(f'#{n}' for n in started)}, which wait on nothing open."
>     if picked:
>         said += f" {picked}"
>     return said + ("\n" if started or picked else " No stage was started.\n")
> 
> 
> AUTOPILOT_LINE = "Autopilot: blockers merged, starting plan"
> AUTOPILOT_START_LINE = "Autopilot: switched on, starting plan"
> 
> 
> def sub_issues(repo, number):
>     """The issue's own sub-issues, one level down, each with its state."""
> 'Autopilot is on for #7. No stage was started.\n'

`5. Bash`
```
cd /home/runner/work/dokima/dokima; mkdir -p /tmp/rv/bin && python3 - <<'EOF'
import sys,json,os
sys.path.insert(0,'.')
import tests.test_visuals_draw as t
open('/tmp/rv/bin/gh','w').write(t.FAKE_GH); os.chmod('/tmp/rv/bin/gh',0o755)
open('/tmp/rv/world.json','w').write(json.dumps(t.world()))
EOF
cat > /tmp/rv/run.py <<'EOF'
import sys; sys.path.insert(0,'.')
from dokima import card
f=card.gather("dokima-dev/dokima",7,None)
out=card.render("dokima-dev/dokima",7,f) if not isinstance(f,tuple) else card.render("dokima-dev/dokima",7,f)
print(out[:3000] if isinstance(out,str) else out)
EOF
env -u DOKIMA_BOT -u GITHUB_REPOSITORY PATH=/tmp/rv/bin:$PATH VISUALS_WORLD=/tmp/rv/world.json VISUALS_LOG=/tmp/rv/log python3 -I /tmp/rv/run.py 2>&1 | head -40; cat /tmp/rv/log
```

> Traceback (most recent call last):
>   File "/tmp/rv/run.py", line 4, in <module>
>     out=card.render("dokima-dev/dokima",7,f) if not isinstance(f,tuple) else card.render("dokima-dev/dokima",7,f)
>         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>   File "/home/runner/work/dokima/dokima/dokima/card.py", line 551, in render
>     lines += criteria_list(repo, issue["number"], 1, "Acceptance criterion", criteria, plan_tests, by_key, tests) + [""]
>                                  ~~~~~^^^^^^^^^^
> TypeError: 'int' object is not subscriptable
> ["issue", "view", "7", "-R", "dokima-dev/dokima", "--json", "number,title,body,comments"]
> ["pr", "list", "-R", "dokima-dev/dokima", "--head", "work/issue-7", "--state", "all", "--json", "number"]
> ["pr", "list", "-R", "dokima-dev/dokima", "--head", "try/issue-7", "--state", "all", "--json", "number"]
> ["api", "repos/dokima-dev/dokima/contents/.github/CODEOWNERS", "-H", "Accept: application/vnd.github.raw"]
> ["api", "repos/dokima-dev/dokima/contents/tests/test_jobs.py?ref=try/issue-7", "-H", "Accept: application/vnd.github.raw"]
> ["api", "repos/dokima-dev/dokima/actions/workflows/worker.yml/runs?per_page=50"]

**Agent:** Checking that the planner's tests can pass against the real drawing code; gather works against the fake GitHub, so far so good.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 500,512p dokima/card.py; grep -n "card.render(" dokima/*.py | head -5
```

> f"{circle(repo, approval_st, approval and approval.get('html_url'))} {field_icon(repo, 'owner approval')} "
>             "Owner approval")
> 
> 
> def render(repo, issue, found, page="issue"):
>     """The card for `issue`, drawn only from `found`: the agents' records, the PR, its latest commit's checks, its
>     reviews, the code owners, the plan's tests and the latest worker run. It is the same on either `page`, but for the
>     PR's top row, which also links the issue."""
>     from dokima import agent
>     recs, pr, check_runs, worker = found["recs"], found["pr"], found["check_runs"], found["worker"]
>     by_key = checks_by_key(check_runs)
>     all_tests = next((r for r in check_runs if r["name"] == ALL_TESTS), None)
>     planned = agent.latest(recs, "planner")
> dokima/scan.py:37:    return issue, found, card.render(repo, issue, found)
> dokima/scan.py:45:    return card.render(repo, issue, found, page="pr")
> dokima/scan.py:77:        top = card.render(repo, got, found, page="pr")

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 25,40p dokima/scan.py; cat > /tmp/rv/run.py <<'EOF'
import sys; sys.path.insert(0,'.')
from dokima import card
f=card.gather("dokima-dev/dokima",7,None)
print(card.render("dokima-dev/dokima",{"number":7,"title":"t","html_url":"u","state":"open","labels":[]},f)[:1500])
EOF
env -u DOKIMA_BOT -u GITHUB_REPOSITORY PATH=/tmp/rv/bin:$PATH VISUALS_WORLD=/tmp/rv/world.json VISUALS_LOG=/tmp/rv/log python3 -I /tmp/rv/run.py 2>&1 | grep -c "Slow calls hand back"
```

> def drawn(repo, number, pr_number):
>     """(issue, everything gathered, card) as dokima.card.draw would write it on issue `number` now, without saving."""
>     issue = plan.fetch_issue(repo, number)
>     found = card.gather(repo, number, pr_number)
>     found["sources"] = card.linked_from(issue["current_body"])
>     cache = {}
>     now = card.github_links(repo, int(number), cache)
>     found["blocking"] = now
>     if now.get("unread"):
>         found["unread"] = card.reason(card.blocking(repo, int(number), cache))
>     found["linked"] = {"relates_to": card.their_links(repo, number, found["sources"])["relates_to"],
>                        "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
>     return issue, found, card.render(repo, issue, found)
> 
> 
> def card_now(repo, kind, number):
> 1

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote one command's plan with three criteria and seven tests.", "The tests run the command against a throwaway repo and a fake GitHub."], "decided": ["The command lives in our own tools folder, outside Dokima itself."], "open": ["No questions for the owner."]},
 "verdict": "block",
 "summary": "The plan is right, but the autopilot test skips the merge lines every autopilot issue gets.",
 "raises": [{"kind": "blocker", "to": "planner", "label": "3: merge lines untested", "text": "Criterion 3 promises each autopilot comment, but the test only covers the blockers line, the work line and the switch reply. A command that ignores `AUTOPILOT_MERGE` lines (`Autopilot: merged PR #N`, queue, waits) and `AUTOPILOT_START_LINE` still passes. Smallest fix: add a `Autopilot: merged PR #9` comment to issue 7 and override `AUTOPILOT_MERGE` in `BRANCH_AGENT`, then assert the branch's line shows.", "evidence": "`tests/test_visuals_draw.py::test_autopilot_comments_from_branch` checks three lines; `dokima/agent.py:2361` posts merge lines on every autopilot merge."}],
 "answers": [],
 "asks": [{"ask": "using the real drawing code from any branch", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.1"},
          {"ask": "the real records of a real issue", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.2"},
          {"ask": "That covers the top card, run comments and autopilot comments.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "624.3"}],
 "behaviors": [{"criterion": "624.1", "one_behavior": true, "why": "Draws one thing, the top card, from the chosen branch."},
               {"criterion": "624.2", "one_behavior": true, "why": "Draws run comments from records."},
               {"criterion": "624.3", "one_behavior": t
```

> Exit code 1
> raise 1's text holds 60 words, over its cap of 30: cut 30, keep the facts

`9. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["raises"][0]["text"]="Criterion 3's test skips merge lines, so code ignoring `AUTOPILOT_MERGE` passes. Fix: add an `Autopilot: merged PR #9` comment, override `AUTOPILOT_MERGE` in `BRANCH_AGENT`, assert it shows."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 624 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for [#624](https://github.com/dokima-dev/dokima/issues/624) (one command draws Dokima's posts from any branch) and sent it back to the planner. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**Why it's blocked:** criterion 3 promises the command draws each autopilot comment. Its test only checks three of them: the "blockers merged" line, the "starting work" line and the `/autopilot` switch reply. Every issue merged on autopilot also gets an `Autopilot: merged PR #N` line, and the test never checks it. So code that skips those lines would still pass. I logged it as a missing normal-use case for that criterion.

The smallest fix is to add an `Autopilot: merged PR #9` comment to the test issue, change the merge lines in the test's branch, and check the branch's version shows.

**What I checked:**
- **Asks:** all three of the owner's asks from the source comment on [#584](https://github.com/dokima-dev/dokima/issues/584) (the parent tool that previews every visual) map to a criterion. None are missing.
- **Size:** fine. Each criterion is one behavior.
- **Tests fail today:** all 7 new tests fail for the right reason, because `tools/visuals.py` doesn't exist yet.
- **Tests can pass:** today's card code draws the test issue's real plan against the planner's fake GitHub, so the tests aren't blocked by the fake.
- **Other tests:** the other six each check only their own criterion. A wrong branch, a missing issue or GitHub refusing ends with a plain message, not a crash.

The plan has no questions for the owner and no earlier blockers to answer.

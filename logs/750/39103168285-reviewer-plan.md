# reviewer (plan) for #750

Run: https://github.com/dokima-dev/dokima/actions/runs/39103168285

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 108
> drwxr-xr-x  3 runner runner  4096 Oct 18 06:11 .
> drwxrwxrwt 18 root   root    4096 Oct 18 06:12 ..
> drwxr-xr-x  2 runner runner  4096 Oct 18 06:11 in
> -rw-r--r--  1 runner runner  7653 Oct 18 06:11 issue.md
> -rw-r--r--  1 runner runner     2 Oct 18 06:11 open_blockers.json
> -rw-r--r--  1 runner runner 62685 Oct 18 06:11 open_issues.json
> -rw-r--r--  1 runner runner  2711 Oct 18 06:11 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 18 06:11 parent.json
> -rw-r--r--  1 runner runner  9840 Oct 18 06:11 plan.json
> 
> in:
> total 20
> drwxr-xr-x 2 runner runner  4096 Oct 18 06:11 .
> drwxr-xr-x 3 runner runner  4096 Oct 18 06:11 ..
> -rw-r--r-- 1 runner runner 10708 Oct 18 06:11 01-planner.json
> # Issue #750: Hotfix label: a small fix builds from its issue text, planning skipped, review kept
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A hotfix label lets a small fix skip planning, while code review, all tests and the merge gate still run.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/750#issuecomment-6246391019) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/do

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cat /home/runner/work/dokima/dokima/rules/splitting.md; grep -n -i "split\|S<s>" /home/runner/work/dokima/dokima/rules/raising.md | head -30
```

> {
>  "https://github.com/dokima-dev/dokima/issues/750": "Owner decision 2026-10-15, rescoped by the owner 2026-10-18 (\"yes 750 hotfix\"): the fast lane is a **label**, not a verb, so it works on autopilot now, before the `@dokima` grammar (#748). #748 can later add `@dokima hotfix` as one more way to put the label on.\n\n**What**\n- An issue labeled `hotfix` skips planning and plan review. When its turn comes (by hand, or on autopilot once nothing open blocks it), the worker builds straight from the issue's text: the text is the whole ask.\n- Code review still runs and judges the diff against the issue's text; it is the judgment gate. All tests and the merge gate still run, as for any pull request.\n- The worker may add or change a small test that pins the fix (as #856 pinned the install docs' check names).\n- Only small asks take the lane: a change the issue names in a sentence or two, touching few files. When code review finds the change bigger than the ask, or the worker finds the ask needs a design choice, it goes back to normal planning, saying why.\n- The card shows one line: the ask, the PR, the review verdict, the gate.\n- Every hotfix PR carries the `hotfix` label and links the issue it answers.\n\n**The loop it completes:** a worker raises a problem; the raise files as an issue that blocks the parent (#268); someone labels it `hotfix`; it lands; the parent restarts by itself when its blocker merges (#213). Hotfixes accumulate as a labeled, linked record; many in one 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "no_edge_cases" -r dokima/*.py | head; grep -n "def check_review\|split\|S<s>" dokima/agent_checks.py | head -40; sed -n 1,80p dokima/fence.py
```

> dokima/planner.py:297:    cases, why = c.get("edge_cases"), c.get("no_edge_cases")
> dokima/planner.py:300:            raise Garbled(f"{where} needs its edge_cases, each with the test covering it, or no_edge_cases saying "
> dokima/card.py:478:    elif c.get("no_edge_cases"):
> dokima/card.py:479:        out.append(f'  - Edge cases: none, because {escape(c["no_edge_cases"])}')
> 372:    """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each
> 373:    story of a split."""
> """The fence: after the worker stops, only in-scope changes survive and the planner's tests are exactly as committed.
> 
> The judges (all tests, each criterion's check) run on fresh machines from what gets pushed, so nothing the worker does to
> its own machine reaches them. What gets pushed is decided here, by code: every test file and test setup file is put back
> to the build's starting commit, and every other change outside the plan's scope is undone. The dropped paths are listed
> so the owner sees them.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> 
> TEST_SETUP = {"conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"}
> 
> 
> def scope_from(plan):
>     """A plan's scope: every file its criteria list, plus its tests' files, sorted."""
>     files = {f.strip() for c in plan.get("acceptance_criteria", []) + plan.get("non_functional", [])
>              for f in c.get("files", [])}
>     return sorted(files | {t.split("::")[0].strip() for names in plan.ge

`4. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima; grep -rn -i "merge gate\|def gate" dokima/*.py | head -20; grep -n "fence" .github/workflows/agent.yml | head
```

> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_claude.py
> agent_codex.py
> agent_github.py
> agent_kimi.py
> agent_next.py
> agent_records.py
> agent_roles.py
> agents.py
> app.json
> audit.py
> board.py
> body.py
> card.py
> checks.py
> defaults.yaml
> fence.py
> icons
> install
> manifest.py
> plan.py
> planner.py
> playthrough.py
> prompt.py
> raises.py
> release.py
> retry.py
> roles
> scan.py
> settings.py
> setup.py
> turns.py
> uptodate.py
> words.py
> dokima/agent_autopilot.py:1:"""Autopilot and merging: switching autopilot, starting and closing issues, and the merge gate.
> dokima/agent_autopilot.py:345:    comment with GitHub's own words. After any refusal the pull request becomes a draft again, so its merge gate
> dokima/agent_autopilot.py:380:        # A draft's checks start again when the merge gate readies it, so the gate never reads the ones from before.
> dokima/agent_autopilot.py:383:            drafted = " It is a draft again, so its checks start afresh when its merge gate readies it."
> dokima/agent_autopilot.py:645:    """How many seconds the merge gate waits for checks still running, from the settings' minutes."""
> dokima/agent_autopilot.py:744:    """The merge gate, run once the code review approved the pull request (#596).
> dokima/agent_autopilot.py:800:    """Ask GitHub to merge the pull request at the head its merge gate tested.
> dokima/agent_autopilot.py:802:    Only when it changes no workflow file and its merge gate passed: every check main requires passed on its head,
> dokima/agent_autopilot.py:892:    merge was not mad

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner split the hotfix lane into two stories of 10 and 7 criteria."],
  "decided": ["The owner's work command starts a hotfix worker by hand.", "The lane may change the guarded workflow and prompt files."],
  "open": ["Two questions wait for the owner: the work command, and the guarded files."]
 },
 "verdict": "block",
 "summary": "No criterion keeps the hotfix's own fix on the pull request, and one criterion holds two behaviors.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "No criterion: fix lands",
   "text": "No criterion says the worker's fix itself stays on the pull request. With no plan the fence keeps nothing, so every hotfix PR would be empty. Fix: add a criterion that a hotfix worker's code change survives the fence.",
   "evidence": "`dokima/fence.py` `scope_from` builds scope from the plan; empty scope drops every change. S1.6 covers only tests."},
  {"kind": "blocker", "to": "planner", "label": "S1.4 is two behaviors",
   "text": "S1.4 bundles two results: code review starts, and it judges the diff against the issue's text. Fix: split it into two criteria.",
   "evidence": "S1.4 reads: code review starts and judges the diff against the issue's text."},
  {"kind": "question", "to": "owner", "label": "Doubt: work command",
   "text": "Your issue keeps hotfixes apart from the work command. Should a hotfix still start by hand with it, as question P1 assumes?",
   "evidence": "The issue says: Why separate from /work, keeping them apart keeps the contract path clean."}
 ],
 "answers": [],
 "asks": [
  {"ask": "An issue labeled `hotfix` skips planning and plan review.", "source": "https://github.com/dokima-dev/dokima/issues/750", "criterion": "S1.1"},
  {"ask": "When its turn comes (by hand, or on autopilot once nothing open blocks it)", "source": "https://github.com/dokima-dev/dokima/issues/750", "criterion": "S1.2"},
  {"ask": "the work
```

> Exit code 1
> raise 1's text holds 39 words, over its cap of 30: cut 9, keep the facts
> raise 3's text holds 22 words, over its cap of 20: cut 2, keep the facts

**Agent:** Review written; trimming two raises that ran over the word cap.

`6. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="No criterion keeps the worker's fix on the pull request; with no plan the fence drops it. Fix: add a criterion that the fix survives the fence."
d['raises'][2]['text']="Your issue keeps hotfixes apart from the work command. Should the work command still start one by hand, as P1 assumes?"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 750 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> raise 3's text holds 21 words, over its cap of 20: cut 1, keep the facts

**Agent:** Review written; trimming two raises that ran over the word cap.

`7. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="No criterion keeps the worker's fix on the pull request; with no plan the fence drops it. Fix: add a criterion that the fix survives the fence."
d['raises'][2]['text']="Your issue keeps hotfixes apart from the work command. Should the work command still start one by hand, as P1 assumes?"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 750 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

`8. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][2]['text']="Your issue keeps hotfixes apart from the work command. Should that command still start one by hand, as P1 assumes?"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 750 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`9. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][2]['text']="Your issue keeps hotfixes apart from the work command. Should that command still start one by hand, as P1 assumes?"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 750 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

**Agent:** I blocked the plan for [#750](https://github.com/dokima-dev/dokima/issues/750) (the hotfix label lane) and sent it back to the planner. The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

**What the planner did:** split the lane into two stories. The first has 10 criteria: start, build, review, tests, label and link. The second has 7: going back to planning when a design choice is needed, and the one-line card.

**Two blockers for the planner:**
- **The fix itself would never reach the pull request.** No criterion says the worker's code change stays on it. With no plan, the fence keeps no files, so it undoes everything except the tests (`dokima/fence.py`, `scope_from`). Criterion S1.6 keeps only the test the worker adds. The fix is to add a criterion that the hotfix's code change gets past the fence.
- **Criterion S1.4 holds two behaviors:** code review starts, and it judges the diff against the issue's text. It should be split into two criteria.

**One question for the owner:** the issue says hotfixes are kept apart from the work command. Yet the planner's own question P1 assumes that command starts a hotfix by hand. I pointed this out so the owner can settle it together with P1.

**Left for the owner:** I didn't answer either of the planner's two questions. P1 is about the work command. P2 asks whether the lane may change the workflow and role prompt files, which are protected. Both wait for the owner.

Every other ask in the issue maps to a criterion.

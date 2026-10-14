# reviewer (plan) for #381

Run: https://github.com/dokima-dev/dokima/actions/runs/38526071710

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

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
> # Issue #381: Issues run in parallel only when they change different functions; otherwise the later one waits
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 581, 601 -->
> <!-- dokima-blocking: {"blocked_by": [581, 601], "blocks": [], "loop": []} -->
> Stories of a split name their files, and one waits unplanned while another in-flight change touches the same file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/381#issuecomment-6162834709) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/581
> - https://github.com/dokima-dev/dokima/issues/601
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/111
> - https://github.com/dokima-dev/dokima/issues/389
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria*

`2. Bash`
```
cd /tmp/pack; cat parent.json; head -c 1500 open_issues.json; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:2000])"; cat /home/runner/work/dokima/dokima/rules/splitting.md
```

> {"number": null}[
>  {
>   "number": 658,
>   "title": "The issue card shows All tests as failed when GitHub only skipped it on a draft pull request.",
>   "summary": "The issue card shows All tests as failed when GitHub only skipped it on a draft pull request.",
>   "link": "https://github.com/dokima-dev/dokima/issues/658",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 656,
>   "title": "The role prompts tell agents to read `AGENTS.md` only; after the split they should also read the topic files it links.",
>   "summary": "The role prompts tell agents to read `AGENTS.md` only; after the split they should also read the topic files it links.",
>   "link": "https://github.com/dokima-dev/dokima/issues/656",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 653,
>   "title": "AGENTS.md says the Definition of Done shows All tests; once this lands the card says Test suite.",
>   "summary": "AGENTS.md says the Definition of Done shows All tests; once this lands the card says Test suite.",
>   "link": "https://github.com/dokima-dev/dokima/issues/653",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 652,
>   "title": "Live cards never show an edge case's source: no record holds one, only the saved 557 data does.",
>   "summary": "Live cards never show an edge case's source: no record holds one, only the saved 557 data does.",
>   "link": "https://github.com/dokima-dev/dokima/issues/652",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 651,
>   "title": "A card with no plan still says All tests, while planned cards will say Tes

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def check_stories\|def start_waiting\|def start_unblocked\|def autopilot_closed\|def file_split" -r dokima | head; ls dokima/fence.py; git status --short; grep -n "scope" dokima/planner.py | head -20
```

> dokima/planner.py:150:def check_stories(stories, issue=None, said=None):
> dokima/agent_autopilot.py:31:def file_split(repo, parent, recs, labels=()):
> dokima/agent_autopilot.py:387:def start_waiting(repo, numbers, line=AUTOPILOT_LINE):
> dokima/agent_autopilot.py:429:def start_unblocked(repo, numbers, owners):
> dokima/agent_autopilot.py:504:def autopilot_closed(repo):
> dokima/fence.py
> 274:    if not strings(p.get("scope")) or not p["scope"]:
> 275:        raise Garbled("a story needs scope as a non-empty list of files")
> 288:                    "scope": p["scope"], "test_changes": tc,
> 549:    lines += [f"- `{s.strip()}`" for s in plan["scope"]]

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner split the issue into four stories from the owner's newest design.",
          "The planner raised three questions for the owner."],
  "decided": ["Only split stories are checked; issues never split are not.",
              "Approved pull requests hold a story back, autopilot or not."],
  "open": ["The owner answers whether single issues, owner commands and approved pull requests change the wait."]
 },
 "verdict": "approve",
 "summary": "The split carries every ask of the newest design; three questions wait for the owner.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Issues run in parallel only when their changes cannot clash", "source": "https://github.com/dokima-dev/dokima/issues/381", "criterion": "2.1"},
  {"ask": "A split's parent plan gives every child story a mandatory `scope` (files it will change, new files marked new)", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "1.1"},
  {"ask": "code checks it is non-empty", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "1.2"},
  {"ask": "each file exists or is marked new", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "1.3"},
  {"ask": "running work (its plan's scope)", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "2.1"},
  {"ask": "open pull requests at the merge gate (the files they change)", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "2.2"},
  {"ask": "Before a child plans, code compares its scope with everything in flight in the repo", "source": "https://github.com/dokima-dev/dokima/issues/381#issuecomment-6138002372", "criterion": "2.3"},
  {"ask": "Siblings that share nothing are still checked against all in-flight work, not started 
```

> Exit code 1
> the ask "Issues run in parallel only when their changes cannot clash" is matched to 2.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "A split's parent plan gives every child story a mandatory `scope` (files it will change, new files marked new)" is matched to 1.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "code checks it is non-empty" is matched to 1.2, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "each file exists or is marked new" is matched to 1.3, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "running work (its plan's scope)" is matched to 2.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "open pull requests at the merge gate (the files they change)" is matched to 2.2, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "Before a child plans, code compares its scope with everything in flight in the repo" is matched to 2.3, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1, S2.2, S2.3, S2.4, S2.5, S3.1, S3.2, S4.1, S4.2)
> the ask "Siblings that share nothing are still checked against all in-flight work, not started blindly to

`5. Bash`
```
cd /tmp/dokima-out && sed -i -E 's/"criterion": "([0-9])\.([0-9])"/"criterion": "S\1.\2"/' review.json && cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 381 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#381](https://github.com/dokima-dev/dokima/issues/381) (files waiting while other work is in flight). The review file is in `/tmp/dokima-out/review.json` and passes both checks.

- **What the plan does:** it splits the issue into four stories that cover every ask in your 2026-10-12 rewrite:
  1. Each story lists the files it will change, and code checks that list.
  2. A story waits, without planning, while another running change or open pull request is changing one of its files. Its card says what it waits on.
  3. A waiting story starts planning on the new main once that work merges or closes.
  4. If a story's full plan needs an extra file that other work is changing, it is checked again before its worker starts.
- **Tests:** this plan only splits the issue, so it has no tests to run yet. Each story's own planner writes its tests and edge cases later.
- **Code claims:** the parts of the code the plan names exist where it says they do.
- **Raises:** I raised no blockers of my own.

The planner's three questions still need your answer:
- Should an issue that is never split skip the file check?
- Should your own `/plan` or `/work` start a waiting story right away?
- Should every approved pull request hold a story back, whether or not it is on autopilot?

Each of these changes how the system works, so I left them for you rather than answering on your behalf.

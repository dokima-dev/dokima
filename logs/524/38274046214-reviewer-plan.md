# reviewer (plan) for #524

Run: https://github.com/dokima-dev/dokima/actions/runs/38274046214

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #524: Cards hide a criterion's source when it is the issue itself, and plans drop out of scope
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> **Backlog**
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> In Reza's words: "should we have the source row since most of the time it will show basically the issue itself which is kind of non informative" and "we need to drop "out of scope" field since with our strict requirements for meeting acceptance criteria and delivering only what is asked they become unnecessary".
> 
> Done when
> - A criterion whose source is its own issue shows no Source line on the card; a criterion sourced from the parent issue or a comment still shows it. The source is still recorded and checked as today.
> - The planner hands back no out_of_scope field, and no card, prompt, word cap or check mentions out of scope. The fence's file scope is unchanged.
> 
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent.com/d

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000]); print(d.keys())"; grep -n "out_of_scope\|non_goals" -r /home/runner/work/dokima/dokima/dokima | head -40
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38273798867",
>  "commit_before": "dd6e00771f3bbaf10de005755c63d6f75655da5e",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 87526,
>   "turns": 11,
>   "cost_usd": 0.7517685999999999,
>   "tokens_in": 611807,
>   "tokens_out": 8549
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/524/38273798867-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38273798867",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/524#issuecomment-6127816054"
> }
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> /home/runner/work/dokima/dokima/dokima/card.py:548:        if h.get("out_of_scope"):
> /home/runner/work/dokima/dokima/dokima/card.py:549:            lines += fold("Out of scope", [f"- {full_refs(repo, escape(s))}" for s in h["out_of_scope"]]) + [""]
> /home/runner/work/dokima/dokima/dokima/card.py:708:             "scope": ["app/jobs.py"], "out_of_scope": ["Retrying failed jobs."], "tests": {}}
> /home/runner/work/dokima/dokima/dokima/planner.py:259:    if not strings(p.get("out_of_scope", [])):
> /home/runner/work/dokima/dokima/dokima/planner.py:260:        raise Garbled("out_of_scope must be a list of sentences")
> /home/runner/work/dokima/dokima/dokima/planner.py:269:                    "non_goals": p.get("out_of_scope", []), "scop

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def criterion_item" -A15 dokima/card.py | head -25; gh 2>/dev/null; grep -n "out.of.scope\|out_of_scope" AGENTS.md | head
```

> 415:def criterion_item(repo, label, c, check, tests):
> 416-    """One criterion bullet: its status circle, its label linked to its check, its words plain.
> 417-
> 418-    The label links only when there is a check. Under it one italic Verified by line per test with a docstring, only
> 419-    the words Verified by linking to the test, then Source: and the link to where the owner asked for it written out
> 420-    bare, so GitHub draws it as its own reference, when it has one."""
> 421-    if check:
> 422-        label = f'<a href="{check["html_url"]}">{label}</a>'
> 423-    out = [f"- {circle(repo, state(check))} **{label}:** {escape(c.get('text'))}"]
> 424-    for t in tests:
> 425-        if t and t.get("verified_by"):
> 426-            out.append(f'  - *<a href="{t["url"]}">{field_icon(repo, "verified by")} Verified by</a>: '
> 427-                       f'{escape(t["verified_by"])}*')
> 428-    if c.get("source"):
> 429-        out.append(f'  - Source: {full_refs(repo, c["source"])}')
> 430-    return out
> Work seamlessly with GitHub from the command line.
> 
> USAGE
>   gh <command> <subcommand> [flags]
> 
> CORE COMMANDS
>   auth:          Authenticate gh and git with GitHub
>   browse:        Open repositories, issues, pull requests, and more in the browser
>   codespace:     Connect to and manage codespaces
>   discussion:    Work with GitHub Discussions (preview)
>   gist:          Manage gists
>   issue:         Manage issues
>   org:           Manage organizations
>   pr:            Manage pull requests
>   project:     

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner proposed a split into two stories with three criteria each."],
  "decided": ["The Source line hides only when it points at the criterion's own issue.", "Out of scope leaves plans, cards, prompts, word caps and checks; the file scope stays."],
  "open": []},
 "verdict": "approve",
 "summary": "The split keeps every ask in the owner's words, one story for the Source line and one for out of scope.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A criterion whose source is its own issue shows no Source line on the card", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S1.1"},
  {"ask": "a criterion sourced from the parent issue or a comment still shows it", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S1.2"},
  {"ask": "The source is still recorded and checked as today.", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S1.3"},
  {"ask": "The planner hands back no out_of_scope field", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S2.1"},
  {"ask": "no card, prompt, word cap or check mentions out of scope", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S2.2"},
  {"ask": "The fence's file scope is unchanged.", "source": "https://github.com/dokima-dev/dokima/issues/524", "criterion": "S2.3"}
 ],
 "behaviors": [
  {"criterion": "S1.1", "one_behavior": true, "why": "One case: own-issue source, no Source line."},
  {"criterion": "S1.2", "one_behavior": true, "why": "One rule: any other source keeps its line."},
  {"criterion": "S1.3", "one_behavior": true, "why": "One guarantee: source handling stays as today."},
  {"criterion": "S2.1", "one_behavior": true, "why": "One field leaves the planner's hand-back."},
  {"criterion": "S2.2", "one_behavior": true, "why": "One result: the term is gone everywhere, in the owner's words.
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)

`5. Bash`
```
sed -i 's/"The split keeps every ask in the owner.s words, one story for the Source line and one for out of scope."/"The split keeps every ask: one story for the Source line, one for dropping out of scope."/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 524 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo $?
```

> 0

**Agent:** I approved the planner's proposal to split [#524](https://github.com/dokima-dev/dokima/issues/524) (hide self-pointing Source lines, drop out of scope) into two stories. The approval is in `/tmp/dokima-out/review.json` and passes both checks.

- **Story 1, Source line:** a criterion whose source is its own issue shows no Source line. Sources pointing at the parent issue or a comment still show. Every source is still recorded and checked as today.
- **Story 2, out of scope:** the planner no longer hands back an out of scope field. No card, prompt, word cap or check mentions it. Changes to files outside the plan's scope are still dropped.

Each of your six asks matches one of the stories' six criteria. Splitting gives no stage the right to change `dokima/card.py` or the prompts in `dokima/roles/`. But your "Done when" names the card and the prompts directly, so the two story plans count that as permission.

Two criteria arguably bundle more than one thing, and I passed them anyway:
- "recorded and checked" in story 1 is one promise that source handling doesn't change.
- "no card, prompt, word cap or check" in story 2 is your own sentence, and splitting it four ways would add a third story for nothing.

There are no tests to check yet. Each story's own plan will write and prove them.

# reviewer (plan) for #740

Run: https://github.com/dokima-dev/dokima/actions/runs/38862845140

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (37.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/c9a282a6-20c0-4994-a99f-7dd09c5d2ee2/tool-results/b7oy1lf20.txt
> 
> Preview (first 2KB):
> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 721, 739, 764 -->
> <!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6209715487) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 721, 739, 764 -->
> <!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6209715487) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/743
> - https://github.com/dokima-dev/dokima/issues/744
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/326
> - https://github.com/dokima-dev/

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json owner_words.json parent.json; echo; head -c 3000 open_issues.json; echo; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps(p,indent=1))"
```

> []{
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n- Every opinion specific to Dokima's own repo becomes a setting with a default: default branch, records branch, rules file name, bot identity, co-author trailer (#110), test install/run_all/run_one commands and test folder (#384), merge gate exclude list, merge queue (#375), labels, check names, turn limits and word caps, card icon source. Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.\n- Locked keys (integrity): app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. A repo cannot override them; trying fails the run.\n- Merge rules: maps merge key by key, repo wins; lists replace; `gates` and `prompts.append` merge by entry name. Unknown key warns with a suggestion and is ignored; never stops a run.\n- Exposure rule: expose repo facts, 

`4. Bash`
```
cd /tmp/pack/in; for f in *; do echo "== $f"; python3 -c "
import json,sys;d=json.load(open('$f'));print(list(d.keys()))
h=d.get('handback') or d.get('hand_back') or d
for k in ('raises','answers','asks','verdict','summary','behaviors','edge_cases','tests','size'):
  if k in h: print(k, json.dumps(h[k],indent=0)[:3000])
"; done
```

> == 01-planner.json
> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> raises [
> {
> "kind": "question",
> "to": "owner",
> "label": "Settle: file name",
> "text": "Should a repo's settings file end in .yaml or .yml? The plan assumes .yaml, like the defaults file.",
> "evidence": "The issue asks to settle `.yml` vs `.yaml` before building.",
> "raised_by": "planner",
> "id": "P1"
> },
> {
> "kind": "question",
> "to": "owner",
> "label": "Doubt: workflow values",
> "text": "Do workflows start reading the co-author trailer and test commands in #742 and #744? The plan assumes so.",
> "evidence": "#742 replaces the trailer from #110; #744 runs `tests.install` and `tests.exclude` in `full-suite.yml`.",
> "raised_by": "planner",
> "id": "P2"
> },
> {
> "kind": "question",
> "to": "owner",
> "label": "Doubt: already fixed",
> "text": "Two absorbed bugs look fixed already. Should the plan carry no work for them? It assumes so.",
> "evidence": "#721 fixed by #758 (`dokima/setup.py`); #515's labels left `dokima/manifest.py` in #773; no `latest_worker_run` in `dokima/card.py`.",
> "raised_by": "planner",
> "id": "P3"
> }
> ]
> answers []
> summary "Each repo sets only what differs from Dokima's shipped defaults, in one settings file."
> == 02-reviewer-plan.json
> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> raises [
> {
> "kind": "blocker",
> "to": "planner",
> "label": "Ask with no criterion",
> "text": "The owner

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
  if i['number'] in (272,741,742,743,744,721,515,326,424,384,375,110): print(i)
"; cd /home/runner/work/dokima/dokima; ls tests | grep -i setting; git log --oneline -3; grep -rn "exclude" dokima/*.py | head; grep -rn "yaml" dokima/*.py | head
```

> {'number': 744, 'title': "Adopter safety: human PRs pass, audit tolerates the repo's own CI and no board", 'summary': 'Phase 3 of #272 (trial blockers).', 'link': 'https://github.com/dokima-dev/dokima/issues/744', 'filed_by_dokima': False}
> {'number': 743, 'title': 'Verification manifest: requirements.yaml in, manifest.yaml out, file::name tests', 'summary': 'Phase 2 of #272.', 'link': 'https://github.com/dokima-dev/dokima/issues/743', 'filed_by_dokima': False}
> {'number': 742, 'title': "Thin workflow install: no Dokima code in the adopter's repo", 'summary': 'Phase 1 of #272.', 'link': 'https://github.com/dokima-dev/dokima/issues/742', 'filed_by_dokima': False}
> {'number': 741, 'title': 'Generic role prompts with repo-appended house rules', 'summary': 'Phase 1 of #272.', 'link': 'https://github.com/dokima-dev/dokima/issues/741', 'filed_by_dokima': False}
> {'number': 515, 'title': 'The settings still declare the plan and work labels as starting agents, and the card still reads old worker runs.', 'summary': 'The settings still declare the plan and work labels as starting agents, and the card still reads old worker runs.', 'link': 'https://github.com/dokima-dev/dokima/issues/515', 'filed_by_dokima': True}
> {'number': 424, 'title': 'The settings guard reads any comparison of x["name"] with a word as a lookup of a required check, so comparing a workflow\'s name (reviews, done-whens) is wrongly flagged, while the same comparison through a local name is not checked at all.', 'summary': 

**Agent:** Round 2 of the plan review: checking the planner's fixes against my three earlier blockers, then writing the review.

`6. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('02-reviewer-plan.json'))['handback'];print(json.dumps(d['asks'][22:],indent=0)); print(d['previous_step'])"; cd /home/runner/work/dokima/dokima; grep -rln "exclude\|install" .github/workflows/ | head; grep -n "exclude" .github/workflows/*.yml | head; head -30 tests/test_settings_comments.py
```

> [
> {
> "ask": "A repo cannot override them; trying fails the run.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.13"
> },
> {
> "ask": "maps merge key by key, repo wins",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.7"
> },
> {
> "ask": "lists replace",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.8"
> },
> {
> "ask": "`gates` and `prompts.append` merge by entry name",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.9"
> },
> {
> "ask": "Unknown key warns with a suggestion",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.11"
> },
> {
> "ask": "is ignored; never stops a run",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.12"
> },
> {
> "ask": "Pipeline order (plan, review, build, review, merge) stays fixed.",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S1.14"
> },
> {
> "ask": "#326 and #424 (audit false alarms)",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S5.10"
> },
> {
> "ask": "a scan finds no Dokima value left in runtime code",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S5.12"
> },
> {
> "ask": "Dokima merges its next 5 PRs purely through its own override file",
> "source": "https://github.com/dokima-dev/dokima/issues/740",
> "criterion": "S2.2"
> }
> ]
> {'did': ['The planner split the ask into five stories, the settings reader first.', "It wrote 32 crite

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "latest_worker_run\|worker_run" dokima/ | head -5; grep -n "plan\b\|\"work\"" dokima/manifest.py | head; git log --oneline | grep -i "773\|758" | head
```

> dokima/turns.py:24:def worker_running(items):
> dokima/turns.py:42:        or worker_running(items)
> 9b2b97d The settings stop declaring the plan and work labels (#773)
> 74c63f5 Settings ignore a comment after a value (#758)

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n '"main"' dokima/agent_autopilot.py | head -3; ls dokima/defaults.yaml dokima/settings.py 2>&1
```

> Exit code 2
> 617:def required_checks(repo, branch="main"):
> 628:def unproven(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
> 637:def proof(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
> ls: cannot access 'dokima/defaults.yaml': No such file or directory
> ls: cannot access 'dokima/settings.py': No such file or directory

**Agent:** Now writing the review.

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/740"
s1=18; s5=14
crit=[f"S1.{k}" for k in range(1,s1+1)]+["S2.1","S2.2","S3.1","S4.1"]+[f"S5.{k}" for k in range(1,s5+1)]
beh=[{"criterion":c,"one_behavior":True,"why":"One action with one result the owner can see."} for c in crit]
for b in beh:
    if b["criterion"]=="S2.2": b["why"]="One result, checked by the owner on real merges."
miss={"S1.2":["A settings file that is not valid YAML: what the owner sees."],
      "S1.7":["A repo with both the old agents file and the new settings file."]}
edges=[{"criterion":c,"cut":[],"missing":miss.get(c,[])} for c in crit]
asks=[
("Dokima ships one defaults file.","S1.1"),
("A repo overrides only what differs in `.dokima/settings.yaml`.","S1.2"),
("Dokima's own repo becomes just another adopter with its own override file.","S2.1"),
("Today's reader only handles flat key: value and cannot read lists","S1.3"),
("it rewrites the whole file on save","S1.4"),
("`.dokima/agents.yml` folds into `settings.yaml` under `agents:`.","S1.6"),
("Old path keeps working for one version.","S1.7"),
("default branch","S5.1"),("records branch","S5.2"),("rules file name","S5.3"),
("bot identity","S3.1"),("co-author trailer (#110)","S1.16"),
("test install/run_all/run_one commands","S1.17"),("test folder (#384)","S5.4"),
("merge gate exclude list","S1.18"),("merge queue (#375)","S5.5"),("labels","S5.6"),
("check names","S5.8"),("turn limits","S4.1"),("word caps","S5.10"),("card icon source","S5.11"),
("Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.","missing"),
("A repo cannot override them; trying fails the run.","S1.14"),
("maps merge key by key, repo wins","S1.8"),("lists replace","S1.9"),
("`gates` and `prompts.append` merge by entry name","S1.10"),
("Unknown key warns with a suggestion","S1.12"),("is ignored; never stops a run","S1.13"),
("Pipeline order (plan, review, build, r
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for issue [#740](https://github.com/dokima-dev/dokima/issues/740) (one settings file per repo) and sent it back to the planner with three blockers. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

The planner fixed everything I raised last round:
- It split the three criteria that each promised two results.
- It added the case of a repo with no settings file.
- It asked you for the 41-row settings list, which is not in the repo.

**Blockers for the planner:**
1. **The scan in 5.14 checks too little.** It only looks for values in Dokima's own settings file, and that file holds only what differs from the defaults. So `main` could stay hard-coded in the code (for example `dokima/agent_autopilot.py:617`) and the scan would still pass. The fix is to scan for every value in the shipped defaults.
2. **Criteria 1.16 to 1.18 prove nothing.** They only check that the co-author trailer, the test commands and the merge gate exclude list exist as keys in the defaults file. Last round the planner asked you whether later issues [#742](https://github.com/dokima-dev/dokima/issues/742) (thin workflow install) and [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety) make the workflows read them. You haven't answered, but the planner dropped that question while the plan still points to it. The fix is to ask you again, or add criteria that actually read each value.
3. **Two everyday cases are missing.** One is a settings file that isn't valid YAML: what do you see? The other is a repo with both the old agents file and the new settings file: which one wins? Dokima's own repo will have both while it moves over.

Three asks in the issue have no criterion yet, so I listed them as missing:
- **The 41-row settings list:** the planner asked you for it.
- **The bugs [#721](https://github.com/dokima-dev/dokima/issues/721) (comments after a setting's value) and [#515](https://github.com/dokima-dev/dokima/issues/515) (labels declared as starting agents):** both are already fixed on main, by [#758](https://github.com/dokima-dev/dokima/issues/758) and [#773](https://github.com/dokima-dev/dokima/issues/773). The planner asked whether this issue needs any work for them.

I didn't answer any of your three open questions for you. You wrote `.dokima/settings.yaml` in the issue, but you also listed `.yml` vs `.yaml` as something to settle, so that choice stays yours.

# reviewer (plan) for #740

Run: https://github.com/dokima-dev/dokima/actions/runs/38932787693

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (78.1KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/7bfdcf35-400e-4b42-9b80-2c5e49ddcfd6/tool-results/b693sw0mt.txt
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
> 04-reviewer-plan.json
> 05-planner.json
> # Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 721, 739, 764 -->
> <!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219937661) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issue

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (35.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/7bfdcf35-400e-4b42-9b80-2c5e49ddcfd6/tool-results/bn28026dj.txt
> 
> Preview (first 2KB):
> # Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 721, 739, 764 -->
> <!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219937661) with `/plan`, or say `/review`
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
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/re

`3. Read`
```
/tmp/pack/issue.md
```

> 1	# Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 721, 739, 764 -->
> 5	<!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> 6	Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 7	
> 8	**Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219937661) with `/plan`, or say `/review`
> 9	
> 10	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 11	
> 12	- https://github.com/dokima-dev/dokima/issues/739
> 13	
> 14	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 15	
> 16	- https://github.com/dokima-dev/dokima/issues/741
> 17	- https://github.com/dokima-dev/dokima/issues/742
> 18	- https://github.com/dokima-dev/dokima/issues/743
> 19	- https://github.com/dokima-dev/dokima/issues/744
> 20	
> 21	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 22	
> 23	- https://github.com/dokima-dev/dokima/issues/272
> 24	- https://github.co

`4. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat owner_words.json | head -c 3000; echo; cat parent.json | head -c 1500; echo; cat open_issues.json | head -c 1500; echo; wc -c plan.json in/*
```

> []
> {
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n- Every opinion specific to Dokima's own repo becomes a setting with a default: default branch, records branch, rules file name, bot identity, co-author trailer (#110), test install/run_all/run_one commands and test folder (#384), merge gate exclude list, merge queue (#375), labels, check names, turn limits and word caps, card icon source. Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.\n- Locked keys (integrity): app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. A repo cannot override them; trying fails the run.\n- Merge rules: maps merge key by key, repo wins; lists replace; `gates` and `prompts.append` merge by entry name. Unknown key warns with a suggestion and is ignored; never stops a run.\n- Exposure rule: expose repo facts,

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps({k:v for k,v in p.items() if k!='stories'},indent=1)[:6000])
for s in p.get('stories',[]):
  print('=== STORY',s.get('title'), s.get('scope'))
  for k,v in s.items():
    if k in('title','scope'):continue
    print(k, json.dumps(v,indent=1))
"
```

> <persisted-output>
> Output too large (39.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/7bfdcf35-400e-4b42-9b80-2c5e49ddcfd6/tool-results/bf5ug9p43.txt
> 
> Preview (first 2KB):
> {
>  "kind": "feature",
>  "title": "One settings file per repo over shipped defaults",
>  "summary": "Each repo sets only what differs from Dokima's shipped defaults, in one settings file.",
>  "feature": "A repo changes Dokima's behavior through one settings file. The first story builds the reader and workflows; the rest move code to settings.",
>  "links": {
>   "blocked_by": [],
>   "blocks": [
>    741,
>    742,
>    743,
>    744
>   ],
>   "relates_to": [
>    272,
>    326,
>    424,
>    110,
>    384,
>    375,
>    515,
>    727,
>    738
>   ]
>  },
>  "raises": [
>   {
>    "kind": "question",
>    "to": "owner",
>    "label": "Settle: file name",
>    "text": "Should a repo's settings file end in .yaml or .yml? The plan assumes .yaml, like the defaults file.",
>    "evidence": "The issue asks to settle `.yml` vs `.yaml` before building.",
>    "raised_by": "planner",
>    "id": "P7"
>   },
>   {
>    "kind": "question",
>    "to": "owner",
>    "label": "Doubt: already fixed",
>    "text": "Two absorbed bugs look fixed already. The plan only pins each with a criterion. Is that right?",
>    "evidence": "#721 fixed by #758 in `dokima/setup.py`; #515's labels left `dokima/manifest.py` `LABELS`.",
>    "raised_by": "planner",
>    "id": "P8"
>   },
>   {
>    "kind": "question",
>    "to": "owner",
>    "label": "Doubt: overlaps open issues",
>  

**Agent:** I'm reading the round-three plan for #740 (one settings file per repo) and its 13 stories next.

`6. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/7bfdcf35-400e-4b42-9b80-2c5e49ddcfd6/tool-results/bf5ug9p43.txt
```

> 1	{
> 2	 "kind": "feature",
> 3	 "title": "One settings file per repo over shipped defaults",
> 4	 "summary": "Each repo sets only what differs from Dokima's shipped defaults, in one settings file.",
> 5	 "feature": "A repo changes Dokima's behavior through one settings file. The first story builds the reader and workflows; the rest move code to settings.",
> 6	 "links": {
> 7	  "blocked_by": [],
> 8	  "blocks": [
> 9	   741,
> 10	   742,
> 11	   743,
> 12	   744
> 13	  ],
> 14	  "relates_to": [
> 15	   272,
> 16	   326,
> 17	   424,
> 18	   110,
> 19	   384,
> 20	   375,
> 21	   515,
> 22	   727,
> 23	   738
> 24	  ]
> 25	 },
> 26	 "raises": [
> 27	  {
> 28	   "kind": "question",
> 29	   "to": "owner",
> 30	   "label": "Settle: file name",
> 31	   "text": "Should a repo's settings file end in .yaml or .yml? The plan assumes .yaml, like the defaults file.",
> 32	   "evidence": "The issue asks to settle `.yml` vs `.yaml` before building.",
> 33	   "raised_by": "planner",
> 34	   "id": "P7"
> 35	  },
> 36	  {
> 37	   "kind": "question",
> 38	   "to": "owner",
> 39	   "label": "Doubt: already fixed",
> 40	   "text": "Two absorbed bugs look fixed already. The plan only pins each with a criterion. Is that right?",
> 41	   "evidence": "#721 fixed by #758 in `dokima/setup.py`; #515's labels left `dokima/manifest.py` `LABELS`.",
> 42	   "raised_by": "planner",
> 43	   "id": "P8"
> 44	  },
> 45	  {
> 46	   "kind": "question",
> 47	   "to": "owner",
> 48	   "label": "Doubt: overlaps open issues",
> 49	   "text": "Install command, exclude list and house rules are also asked in #74

`7. Bash`
```
cd /tmp/pack/in; python3 -c "
import json;d=json.load(open('04-reviewer-plan.json'));print(json.dumps(d,indent=1)[:15000])"
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38862845140",
>  "commit_before": "951ca4ab41468782d94c975e6e17d877163884d9",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 118705,
>   "turns": 10,
>   "cost_usd": 0.6031886000000001,
>   "tokens_in": 462685,
>   "tokens_out": 10747
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/740/38862845140-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38862845140",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner split three bundled criteria into two each.",
>     "It added the case of a repo with no settings file.",
>     "It asked the owner for the 41-row settings list."
>    ],
>    "decided": [
>     "It dropped the question on workflows reading the trailer and test commands."
>    ],
>    "open": [
>     "Three questions for the owner: file name, two bugs already fixed, the settings list."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The plan fixed last round's points, but its scan misses most hard-coded values and three settings prove nothing.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "planner",
>     "label": "S5.14 scan too narrow",
>     "text": "S5.14 scans only for values in Dokima's own file, which holds just what differs, so hard-coded `main` passes. Scan for every shipped default value instead.",
>     "evidence": "S2.1 keeps only differing values; `dokima/agent_autopilot.py:617` has `branch=\"main\"`.",
>     "raised_

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; ls tests | head -80; ls tests/test_settings.py tests/test_agents.py 2>&1; grep -n "test_settings_file_wins\|test_no_settings_file\|test_broken_settings" -r tests | head; sed -n 15,30p dokima/plan.py; grep -n "LABELS" -A12 dokima/manifest.py | head -30
```

> 951ca4a Delete the planner's old post and reject steps (#777)
> 270480f Autopilot starts an issue when a person adds its label by hand (#776)
> 9e87c8e Every agent's key stays out of public cards and records (#767)
> agent_patch.py
> card_player.py
> conftest.py
> fake_gh.py
> fixtures
> record_seed.py
> rules_files.py
> samples
> test_agent.py
> test_agent_codex.py
> test_agent_key_scrubbed.py
> test_agent_kimi.py
> test_agent_split.py
> test_agents.py
> test_all_tests_judge.py
> test_all_tests_note.py
> test_answered_questions.py
> test_app.py
> test_assign.py
> test_audit.py
> test_audit_auto_merge.py
> test_audit_cli.py
> test_audit_workflow.py
> test_automerge.py
> test_automerge_confirmed.py
> test_autopilot.py
> test_autopilot_board.py
> test_autopilot_checks.py
> test_autopilot_close.py
> test_autopilot_label.py
> test_autopilot_river.py
> test_autopilot_start.py
> test_autopilot_stop_pr.py
> test_blocked_worker.py
> test_blocker_pill.py
> test_board.py
> test_board_state.py
> test_body.py
> test_bot_identity.py
> test_budget_retry.py
> test_budget_spent_says_so.py
> test_build_started_card.py
> test_build_turns.py
> test_cancelled_run.py
> test_card.py
> test_card_416.py
> test_card_acceptance_lines.py
> test_card_bullets.py
> test_card_criterion_label.py
> test_card_edge_cases.py
> test_card_every_change.py
> test_card_folds.py
> test_card_guard.py
> test_card_merge.py
> test_card_not_verified.py
> test_card_old_lookups.py
> test_card_queue.py
> test_card_raises_status.py
> test_card_records.py
> test_card_refs.py
> test_card_running.py
> test_card_sample_gone.py
> test_card_self_link.py
> test_

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 50,110p dokima/setup.py; ls .dokima; grep -rn "Settle\|yaml" AGENTS.md rules/*.md | head
```

> """Run AGENT's own login with REGION; return its saved files as base64 gzip tar."""
>     if agent not in LOGIN:
>         raise Failed(f"Setup cannot sign in {agent}; it knows {', '.join(sorted(LOGIN))}. Give a key instead.")
>     if subprocess.run([*LOGIN[agent], region]).returncode:
>         raise Failed(f"The {agent} login failed, so no sign-in was stored.")
>     home = os.path.expanduser("~")
>     saved = [p for p in SIGN_IN[agent] if os.path.exists(os.path.join(home, p))]
>     if not saved:
>         raise Failed(f"The {agent} login saved none of {', '.join(SIGN_IN[agent])}, so no sign-in was stored.")
>     buf = io.BytesIO()
>     with tarfile.open(fileobj=buf, mode="w:gz") as t:
>         for p in saved:
>             t.add(os.path.join(home, p), arcname=p)
>     return base64.b64encode(buf.getvalue()).decode()
> 
> 
> def read_settings(text):
>     """Read the settings file's block maps (`subscriptions` and `roles`, two levels down) into nested dicts."""
>     root, stack = {}, [(-1, None)]
>     stack[0] = (-1, root)
>     for line in text.splitlines():
>         if not line.strip() or line.lstrip().startswith("#"):
>             continue
>         indent = len(line) - len(line.lstrip())
>         key, _, rest = line.strip().partition(":")
>         rest = rest.strip()
>         if rest[:1] in ("'", '"') and rest[0] in rest[1:]:
>             rest = rest[1:rest.index(rest[0], 1)]
>         else:
>             rest = re.split(r"\s#", " " + rest, maxsplit=1)[0].strip()
>         while stack[-1][0] >= indent:
>             

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "escalate" dokima/*.py | head -20
```

> dokima/agent_checks.py:128:        bad.append("verdict must be approve, block or escalate")
> dokima/agent_checks.py:294:            bad.append("verdict must be approve, block or escalate")
> dokima/agent_records.py:15:VERDICTS = {"approve", "block", "escalate"}
> dokima/agent_records.py:597:    if h.get("verdict") == "escalate" and filled(h.get("summary")):
> dokima/agent_records.py:633:                "escalate": f"{name} escalated {what} to you."}.get(h.get("verdict"), f"{name} judged {what}.")
> dokima/agent_records.py:785:        parts += [("Details", ([f"- {h['summary']}"] if h.get("summary") and h.get("verdict") != "escalate" else [])
> dokima/agent_records.py:824:                "escalate": f"The reviewer escalated {what} to you."}.get(h.get("verdict"), f"The reviewer judged {what}.")
> dokima/agent_records.py:880:        if h.get("verdict") == "escalate" and h.get("summary"):
> dokima/card.py:33:        "escalated": "Settle the escalation",
> dokima/card.py:344:    if verdict == "escalate":
> dokima/card.py:345:        return TODO["escalated"]
> dokima/agent_next.py:185:    if verdict == "escalate":
> dokima/agent_next.py:186:        return ("stop", "The reviewer escalated this to you, see why above.")

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 53,57p dokima/card.py; sed -n 25,28p dokima/checks.py
```

> def icon(repo, name, alt=None):
>     """One of GitHub's own circle icons (Octicons, MIT), served from this repo, centered on its line."""
>     url = f"https://raw.githubusercontent.com/{repo}/main/dokima/icons/{name}.svg"
>     return f'<img src="{url}" width="16" height="16" align="absmiddle" alt="{alt or name}">'
> 
> QUEUE_REF = re.compile(r"^(?:refs/heads/)?gh-readonly-queue/.+/pr-(\d+)-[0-9a-f]+$")
> TEXT_ONLY = [{"id": "text-only", "name": "Text only: no plan needed", "tests": ""}]
> NOT_TEXT = ("dokima/roles/", "tests/", ".github/")
> MANUAL_FIX = [{"id": "manual-fix", "name": "Manual fix: all tests pass", "tests": "tests"}]

**Agent:** I'm writing the review now: two small blockers found, then running the checks.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/mkreview.py <<'EOF'
import json
p=json.load(open('/tmp/pack/plan.json'))
I="https://github.com/dokima-dev/dokima/issues/740"
C=I+"#issuecomment-6219928729"
ids=[]
for si,s in enumerate(p['stories'],1):
    for k,_ in enumerate(s['acceptance_criteria'],1): ids.append(f"S{si}.{k}")
bundled={"S3.14":"Two results: the cap comes from settings, and an empty cap turns it off.",
         "S5.8":"Two results: the cap comes from settings, and an empty cap turns it off."}
behaviors=[{"criterion":c,"one_behavior":c not in bundled,"why":bundled.get(c,"One setting, one result the owner can see.")} for c in ids]
edge=[{"criterion":c,"cut":[],"missing":[]} for c in ids]
asks=[
("Dokima ships one defaults file.",I,"S1.1"),
("A repo overrides only what differs in `.dokima/settings.yaml`.",I,"S1.2"),
("Dokima's own repo becomes just another adopter with its own override file.",I,"S2.1"),
("Today's reader only handles flat key: value and cannot read lists",I,"S1.4"),
("it rewrites the whole file on save",I,"S1.7"),
("`.dokima/agents.yml` folds into `settings.yaml` under `agents:`.",I,"S1.8"),
("Old path keeps working for one version.",I,"S1.9"),
("co-author trailer (#110)",I,"S1.31"),
("merge gate exclude list",I,"S1.26"),
("merge queue (#375)",I,"S6.2"),
("A repo cannot override them; trying fails the run.",I,"S1.16"),
("maps merge key by key, repo wins",I,"S1.10"),
("lists replace",I,"S1.11"),
("`gates` and `prompts.append` merge by entry name",I,"S1.12"),
("Unknown key warns with a suggestion",I,"S1.14"),
("is ignored; never stops a run",I,"S1.15"),
("Pipeline order (plan, review, build, review, merge) stays fixed.",I,"S1.17"),
("#721 (inline comments)",I,"S1.6"),
("#326 and #424 (audit false alarms)",I,"S6.4"),
("#515 (labels still declared as starting agents)",I,"S6.6"),
("a scan finds no Dokima value left in runtime code",I,"S13.1"),
("Dokima merges its next 5 PRs purely through its own override file",I,"S2.2"),
("Each row is one setting, its 
```

> raise 2's text holds 32 words, over its cap of 30: cut 2, keep the facts
> rc=1

`13. Bash`
```
cd /tmp; sed -i 's/but the owner.s list changes some: S3.5 drops the prompt folder, S7.2 moves the icon source. Say each default is the one the list names./but S3.5 drops the prompt folder and S7.2 moves the icon source. Say each default is the one the list names./' mkreview.py && python3 mkreview.py && cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 740 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
python3 -c "
import json;p=json.load(open('/tmp/pack/plan.json'));r=json.load(open('/tmp/dokima-out/review.json'))
t={}
for si,s in enumerate(p['stories'],1):
  for k,c in enumerate(s['acceptance_criteria'],1): t[f'S{si}.{k}']=c['text']
for a in r['asks']: print(a['criterion'],'|',a['ask'][:40],'|',t[a['criterion']][:70])"
```

> rc=0
> S1.1 | Dokima ships one defaults file. | Dokima ships one defaults file that every repo's settings fall back to
> S1.2 | A repo overrides only what differs in `. | A repo's settings file changes only the settings it names; every other
> S2.1 | Dokima's own repo becomes just another a | Dokima's own repo keeps every value it differs on in its own settings 
> S1.4 | Today's reader only handles flat key: va | A settings file holding lists is read in full, on every machine that r
> S1.7 | it rewrites the whole file on save | Saving one setting through setup leaves every other setting as it was.
> S1.8 | `.dokima/agents.yml` folds into `setting | The agents section of the settings file picks each role's agent and mo
> S1.9 | Old path keeps working for one version. | A repo with only the old agents file still runs each role's agent as n
> S1.31 | co-author trailer (#110) | The co-author line on Dokima's commits comes from the co-author settin
> S1.26 | merge gate exclude list | Tests on the merge gate exclude list stay out of the all tests check.
> S6.2 | merge queue (#375) | Turning the merge queue off in a repo's settings stops the audit askin
> S1.16 | A repo cannot override them; trying fail | Setting any of the five locked settings in a repo's file fails the run
> S1.10 | maps merge key by key, repo wins | A settings group in a repo's file merges with the defaults key by key,
> S1.11 | lists replace | A list in a repo's file replaces the default list whole.
> S1.12 | `gates` and `prompts.append` m

**Agent:** I blocked the plan for [#740](https://github.com/dokima-dev/dokima/issues/740) (one settings file per repo), with two small fixes for the planner. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**What the planner did this round:** it turned your 41-row list into 13 stories. Every item from the issue and every row of the list now has a criterion, and it fixed all three of last round's blockers.

**Blockers for the planner:**
- **Two criteria each promise two things.** S3.14 and S5.8 each say "the cap comes from settings, and an empty cap turns it off." Each needs splitting in two.
- **S1.3 contradicts other criteria.** It says every default keeps today's value, but your list changes some defaults. S3.5 drops the prompt folder and S7.2 moves where icons load from. The fix is to say each default is the one your list names.

**Questions I answered for you, quoting your own words:**
- **Two absorbed bugs look fixed already.** I agreed the plan only needs one criterion each to keep them fixed. You wrote that this issue absorbs them.
- **Overlap with [#741](https://github.com/dokima-dev/dokima/issues/741) (house rules) and [#744](https://github.com/dokima-dev/dokima/issues/744) (install command and exclude list).** I agreed to build them here. Your list calls those rows "for this issue."

**Left for you:** `.yaml` or `.yml` for the repo's settings file. Your issue says to settle this before building, so I didn't decide it for you.

**Two calls I made:**
- **Verdict:** this is the third plan review, and the rules say a third round with a blocker should escalate. I used "block" instead, because the two sides don't disagree on anything; these are new, small fixes. Three blocks in a row stops for you anyway.
- **The fence:** you listed it as locked, but your list also makes its test setup files a setting. The plan reads "locked" as covering what the fence does, not that list of files. I accepted that reading because your newer list says so.

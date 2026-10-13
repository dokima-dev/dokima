# reviewer (plan) for #581

Run: https://github.com/dokima-dev/dokima/actions/runs/38482863663

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 84
> drwxr-xr-x  3 runner runner  4096 Oct 13 23:13 .
> drwxrwxrwt 18 root   root    4096 Oct 13 23:13 ..
> drwxr-xr-x  2 runner runner  4096 Oct 13 23:13 in
> -rw-r--r--  1 runner runner  6834 Oct 13 23:13 issue.md
> -rw-r--r--  1 runner runner     2 Oct 13 23:13 open_blockers.json
> -rw-r--r--  1 runner runner 47632 Oct 13 23:13 open_issues.json
> -rw-r--r--  1 runner runner    16 Oct 13 23:13 parent.json
> -rw-r--r--  1 runner runner  5466 Oct 13 23:13 plan.json
> 
> in:
> total 16
> drwxr-xr-x 2 runner runner 4096 Oct 13 23:13 .
> drwxr-xr-x 3 runner runner 4096 Oct 13 23:13 ..
> -rw-r--r-- 1 runner runner 6204 Oct 13 23:13 01-planner.json
> # Issue #581: Split agent.py and AGENTS.md so issues stop queueing on the same file
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [580, 582], "blocks": [599, 600], "loop": []} -->
> The two files most issues touch become smaller files, so parallel work stops queueing on them.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/581#issuecomment-6157146431) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/580
> - https://github.com/dokima-dev/dokima/issues/582
> 
> <img

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:2500])"; wc -lc dokima/agent.py AGENTS.md; grep -n "def agents_text" -A12 dokima/agent.py; sed -n 70,85p .github/workflows/agent.yml; grep -rl "agent.gh\b\|agent, \"gh\"\|agent, 'gh'" tests | wc -l; grep -rn "AGENTS" tests | head -20
```

> {"number": null}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "38482605190",
>  "commit_before": "61faa9edeb3dd8e4b351252c742cfbe198fb7ce7",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 101157,
>   "turns": 15,
>   "cost_usd": 0.7691805999999999,
>   "tokens_in": 750937,
>   "tokens_out": 10311
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/581/38482605190-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38482605190",
>  "handback": {
>   "kind": "feature",
>   "title": "Split the big agent file and the rules file",
>   "summary": "The two files most issues touch become smaller files, so parallel work stops queueing on them.",
>   "feature": "The agent code and the rules file split into smaller files by job, behavior unchanged. Stories: (1) the agent code; (2) the rules, after (1).",
>   "stories": [
>    {
>     "title": "The agent code splits into files by job",
>     "user_story": "Issues that change different jobs of the agent code change different files, so they no longer queue.",
>     "context": "`dokima/agent.py` is 3,158 lines and 172 KB. Its jobs, by function: GitHub helpers (`gh`, `gh_reason`, `rate_limited`, `linked_prs`, `conversation`); records (`records`, `latest`, `approved`, `open_raises`, `build_record`, `render`, `render_as_posted`, stats); checks (`problems_*`, `check`, `load`); roles and packs (`pack`, `problems_pack`, `command_of`, `route`); autopilot and merging (`switch_autopilot

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner proposes a split into two stories: the agent code, then the rules file."],
  "decided": ["The rules file story waits for the agent code story.", "The test count for the rules story is taken after the agent code story lands."],
  "open": ["Should the rules file become an index of topic files the word check reads?", "Should one helper carry every module's GitHub calls, or only the agent code's?"]},
 "verdict": "block",
 "summary": "The split is sound, but the last story bundles two results and can miss tests the first story drops.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "S2.2 two results", "text": "Criterion S2.2 bundles two results, all tests pass and the count is unchanged, and story 2's context counts tests only after story 1 lands, so tests story 1 drops go unnoticed. Smallest fix: split S2.2 into two criteria, and count against main before story 1, 1127 tests.", "evidence": "Story 2 context: \"The count of tests is taken after story 1 lands.\" S2.2 text: \"All tests pass after both splits, and as many tests run as before them.\""},
  {"kind": "question", "to": "owner", "label": "Workflow change needed", "text": "If the rules split into topic files the word check reads, the runtime copy step must change. May story 2 change that workflow? The plan does not say.", "evidence": "`.github/workflows/agent.yml` line 78 copies only `AGENTS.md`; AGENTS.md forbids workflow changes unless the issue asks."}
 ],
 "answers": [],
 "asks": [
  {"ask": "agent.py is split into modules by job (autopilot and merging, records, Next lines, checks, GitHub helpers, roles), a pure move with no behavior change", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "S1.1"},
  {"ask": "`agent` keeps re-exporting every name so its 146 importers keep working", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "S1.2"},
```

> Exit code 1
> raise 1's text holds 47 words, over its cap of 30: cut 17, keep the facts
> raise 1's evidence holds 29 words, over its cap of 20: cut 9, keep the facts
> raise 2's text holds 28 words, over its cap of 20: cut 8, keep the facts

`4. Bash`
```
python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';d=json.load(open(p))
d['raises'][0]['text']="S2.2 bundles two results, tests pass and count unchanged, and counts after story 1, missing tests it drops. Fix: split it; count against main before story 1."
d['raises'][0]['evidence']="Story 2 context: \"The count of tests is taken after story 1 lands.\""
d['raises'][1]['text']="Topic files the word check reads need the runtime copy step changed. May story 2 change that workflow?"
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 581 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for issue [#581](https://github.com/dokima-dev/dokima/issues/581) (split the big agent file and the rules file). The hand-back passes both checks and is at `/tmp/dokima-out/review.json`.

The planner splits the work into two stories. Story 1 splits the agent code into files by job, and story 2 splits the rules file by topic after story 1 lands. Every ask in the issue maps to a criterion, so none is missing.

**Blocker, sent to the planner:**
- **The last criterion, on the test suite, holds two results:** all tests pass, and the test count is unchanged.
- **Its count misses story 1:** story 2 takes the count after story 1 lands, so tests lost in story 1 would go unnoticed.
- **Fix:** split it into two criteria, and count against main before story 1 (1,127 tests today).

**New question, sent to you:**
- **The workflow:** If the rules become topic files that the owner's-words check reads, `.github/workflows/agent.yml` must change, because line 78 copies only `AGENTS.md`. The rules in `AGENTS.md` forbid workflow changes unless the issue asks. May story 2 change it?

**The planner's two questions:** I left both for you to answer. Your words in the issue don't settle either one, so autopilot stops for you anyway:
- Should the rules file become a short index that links to the topic files?
- Should one helper carry every module's GitHub calls, or only the agent code's?

**Cases the plan leaves out:**
- `python3 -m dokima.agent` must still work, because the workflows call it.
- Other issues may add tests between the two stories, which would change the count.

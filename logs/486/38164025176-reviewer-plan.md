# reviewer (plan) for #486

Run: https://github.com/dokima-dev/dokima/actions/runs/38164025176

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
> # Issue #486: Text that fails the style checks goes back to its writer in the same run, up to 3 times
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 482 -->
> <!-- dokima-blocking: {"blocked_by": [482, 483], "blocks": [], "loop": []} -->
> Text failing the style checks goes back to its writer in the same run, up to 3 times.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/486#issuecomment-6112234879) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/482
> - https://github.com/dokima-dev/dokima/issues/483
> 
> 
> **User story:** Agents rewrite their own long or code-filled text before it posts; what still fails is flagged.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Text failing a style check goes b

`2. Bash`
```
cd /home/runner/work/dokima/dokima; head -c 3000 /tmp/pack/parent.json; echo; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cat tests/test_style_retry.py; ls dokima/restyle.py; git log --oneline -3 --stat | head -20
```

> {"number": 470}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38163782727",
>  "commit_before": "0d1a479251bafe38341a2c050d382e38ded8e4af",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 160270,
>   "turns": 24,
>   "cost_usd": 1.1301584000000002,
>   "tokens_in": 1406665,
>   "tokens_out": 16113
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/486/38163782727-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38163782727",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/486#issuecomment-6112234879"
> }
> """#486: failing text goes back to its writer, up to 3 times.
> 
> After the agent ends, the workflow runs `python3 -m dokima.restyle OUT FILE`. It checks the hand-back OUT/FILE with
> the style checks (word caps and plain words, `dokima.words`). On a failure it resumes the same Claude session (the
> `session_id` in OUT/claude.json) with `claude -p --resume SESSION_ID` and a message naming each failing field and why,
> then checks again: at most 3 style retries, counted on their own. Whatever still fails after them is written to
> OUT/style.txt, one line per failing field, and `python3 -m dokima.agent record` flags it in the run's record and
> comment, while the hand-back still posts.
> 
> Each test puts a fake `claude` on PATH that logs every call (its arguments and its input) and, when told, rewrites
> the hand-back on a given call, so the loop runs for 

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 20 curl -s https://api.github.com/repos/dokima-dev/dokima/issues/comments/6102982172 | head -c 6000; python3 -m pytest -q tests/test_style_retry.py 2>&1 | tail -15
```

> {
>   "url": "https://api.github.com/repos/dokima-dev/dokima/issues/comments/6102982172",
>   "html_url": "https://github.com/dokima-dev/dokima/issues/470#issuecomment-6102982172",
>   "issue_url": "https://api.github.com/repos/dokima-dev/dokima/issues/470",
>   "id": 6102982172,
>   "node_id": "IC_kwDOU1yWRs8AAAABa8QeHA",
>   "user": {
>     "login": "RezaSoleymanifar",
>     "id": 34189616,
>     "node_id": "MDQ6VXNlcjM0MTg5NjE2",
>     "avatar_url": "https://avatars.githubusercontent.com/u/34189616?u=4add81f4c4e41c9c9f7a2aa432cffa96eddd5d0b&v=4",
>     "gravatar_id": "",
>     "url": "https://api.github.com/users/RezaSoleymanifar",
>     "html_url": "https://github.com/RezaSoleymanifar",
>     "followers_url": "https://api.github.com/users/RezaSoleymanifar/followers",
>     "following_url": "https://api.github.com/users/RezaSoleymanifar/following{/other_user}",
>     "gists_url": "https://api.github.com/users/RezaSoleymanifar/gists{/gist_id}",
>     "starred_url": "https://api.github.com/users/RezaSoleymanifar/starred{/owner}{/repo}",
>     "subscriptions_url": "https://api.github.com/users/RezaSoleymanifar/subscriptions",
>     "organizations_url": "https://api.github.com/users/RezaSoleymanifar/orgs",
>     "repos_url": "https://api.github.com/users/RezaSoleymanifar/repos",
>     "events_url": "https://api.github.com/users/RezaSoleymanifar/events{/privacy}",
>     "received_events_url": "https://api.github.com/users/RezaSoleymanifar/received_events",
>     "type": "User",
>     "user_view_type": "public",
>     "site_adm

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "never splits\|parent" dokima/agent.py | grep -in "split\|stor" | head -20; grep -rn "def.*size\|/ 3\|ceil" dokima/*.py | head
```

> 6:dokima/agent.py:359:def story_body(parent, i, story, parent_title):
> 7:dokima/agent.py:362:             f"<details open><summary>From the approved plan of #{parent}, story {i}</summary>", "",
> 8:dokima/agent.py:363:             f"**Part of:** #{parent} {parent_title}", "", f"**User story:** {story.get('user_story', '')}", ""]
> 9:dokima/agent.py:373:def file_split(repo, parent, recs, labels=()):
> 10:dokima/agent.py:374:    """File the stories of the newest approved split as sub-issues of the parent, in order, with their blocked-by links,
> 12:dokima/agent.py:386:        url = gh("issue", "create", "-R", repo, "--title", st["title"], "--body", story_body(parent, i, st, title), *extra).strip()
> 26:dokima/agent.py:1126:    # A story split from a parent holds a planner's text, not the owner's: only the parent's ask counts as theirs.
> 61:dokima/agent.py:2382:        # Filing a split puts the parent in Work, as `/work` does.
> 65:dokima/agent.py:2508:        rec = file_split(repo, parent, recs, [AUTOPILOT] if on else [])
> dokima/agent.py:1208:def problems_size(r, ids=()):
> dokima/planner.py:131:def check_size(stories, nested=False):
> dokima/planner.py:134:    The size rule (#416): stories = criteria / 3, rounded up. 1 to 3 criteria is one story; 4 to 6 two; and so on, up to

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1200,1250p dokima/agent.py; sed -n 125,175p dokima/planner.py
```

> for t in named if not (isinstance(seen.get(t, {}).get("only_its_behavior"), bool)
>                                   and str(seen.get(t, {}).get("why") or "").strip())]
>     wide = [t for t, x in seen.items() if x.get("only_its_behavior") is False]
>     if wide and r.get("verdict") == "approve":
>         bad.append(", ".join("`" + t + "`" for t in wide) + f" check more than their criterion's behavior, so the verdict cannot be approve")
>     return bad
> 
> 
> def problems_size(r, ids=()):
>     """A plan review must judge each criterion one behavior or not, in `behaviors`, and say whether the plan keeps the
>     size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks it; a plan that breaks
>     it is never approved."""
>     bad = []
>     rows = r.get("behaviors") if isinstance(r.get("behaviors"), list) else []
>     seen = {str(b.get("criterion")): b for b in rows if isinstance(b, dict)}
>     for k in ids:
>         b = seen.get(str(k))
>         if not b or not isinstance(b.get("one_behavior"), bool) or not str(b.get("why") or "").strip():
>             bad.append(f"behaviors has no judgment of criterion {k}: say one_behavior true or false, and why in one line")
>     bundled = [k for k, b in seen.items() if b.get("one_behavior") is False]
>     size = str(r.get("size") or "").strip()
>     if bundled and size.lower() == "ok":
>         bad.append(f"criteria {', '.join(bundled)} bundle more than one behavior, so size cannot be ok")
>     if bad:
>         return bad
>     if not s

**Agent:** Checking how today's hand-back check treats style failures, to see whether the "still posts" test proves anything.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "check\b\|dokima.agent check\|STYLE_SOFT\|claude -p\|record " .github/workflows/agent.yml | head -30; grep -rn "STYLE_SOFT" dokima | head; grep -n "def problems_words\|words\.\|import.*words" dokima/agent.py | head
```

> 5:# conversation (comments, reviews, line notes) and every earlier agent record. The agent runs its own check before it
> 12:# Every step before the agent that fails writes why to /tmp/why.txt; when no agent started, the record says that instead.
> 84:      # live on this machine while the branch's code, its tests, the agent or the hand-back check run. Every stage
> 102:          # Where the record will go: the PR once there is one, for the worker and the PR reviewer.
> 109:            echo "::warning title=No live card::the card could not be put up; the record is posted at the end"
> 189:          python3 -m dokima.agent check-pack "$ROLE" "$STAGE" "$PACK" > /tmp/pack-check.txt \
> 190:            || { echo "Incomplete pack: $(paste -sd'; ' /tmp/pack-check.txt)" > /tmp/why.txt
> 220:            planner)      GRADE=plan-grade;   FILE=plan.json;   CHECK="python3 -m dokima.planner check $N $OUT" ;;
> 221:            reviewerplan) GRADE=plan-grade;   FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.json $N" ;;
> 222:            reviewerpr)   GRADE=result-grade; FILE=review.json; CHECK="python3 -m dokima.agent check review $OUT/review.json $PACK/plan.json $N" ;;
> 223:            worker)       GRADE=result-grade; FILE=work.json;   CHECK="python3 -m dokima.agent check work $OUT/work.json $PACK/plan.json $N" ;;
> 225:          CHECK="$CHECK && python3 -m dokima.agent check-round $ROLE $OUT/$FILE $PACK"
> 227:          claude -p "$(cat /tmp/runtime/dokima/roles/styl

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 255,300p .github/workflows/agent.yml; sed -n 110,140p dokima/words.py; sed -n 1375,1400p dokima/agent.py; grep -n "too_long\|style" dokima/agent.py | sed -n 1,40p
```

> SCRUB_GITHUB: ${{ github.token }}
>         run: |
>           python3 -m dokima.agent card "$ROLE" "$STAGE" checking > /tmp/card.md
>           gh api -X PATCH "repos/$GITHUB_REPOSITORY/issues/comments/$CARD_ID" -F body=@/tmp/card.md --silent \
>             || echo "::warning title=Card not updated::the card could not say checking"
>           gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
>       - name: Code checks the hand-back
>         if: always() && env.STARTED == 'true'
>         # The agent ran this check itself and cut its texts; here word caps only flag what is still over (#470).
>         env:
>           STYLE_SOFT: "1"
>         run: |
>           set +e; bash -c "$CHECK" > "$OUT/check.txt" 2>&1; rc=$?; set -e
>           cat "$OUT/check.txt"
>           echo "PASSED=$([ $rc = 0 ] && echo true || echo false)" >> "$GITHUB_ENV"
>       - name: Fence - only in-scope changes, the planner's tests as committed
>         if: env.ROLE == 'worker'
>         run: |
>           # A clashed file still holding conflict markers fails the hand-back, saying which, so nothing is pushed.
>           if ! python3 -m dokima.fence "$BASE" "$PACK/plan.json" /tmp/clashed.txt > "$OUT/dropped.txt" 2> /tmp/fence-err.txt; then
>             cat /tmp/fence-err.txt | tee -a "$OUT/check.txt"; echo "PASSED=false" >> "$GITHUB_ENV"
>             echo "::error title=Fence::$(paste -sd' ' /tmp/fence-err.txt)"
>           fi
>           [ -s "$OUT/dropped.txt" ] &&

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1400,1420p dokima/agent.py; grep -n "listed\|Style:\|over its cap" dokima/agent.py dokima/card.py | head -20; grep -rn "STYLE_SOFT" tests | head
```

> bad += problems_plan(kind, data, plan, number)
>             if kind == "review" and os.environ.get("STAGE") == "plan":
>                 bad += problems_asks(data, plan_criteria(plan, number))
>                 bad += problems_size(data, plan_criteria(plan, number))
>                 bad += problems_tests(data, plan)
>     for line in listed + bad:
>         print(line)
>     return 1 if bad else 0
> 
> 
> def worker_docstring_caps(base):
>     """(listed, rejected) for each Python docstring added or rewritten since `base`.
> 
>     Older docstrings whose first line is unchanged are left alone; a base git cannot read fails closed.
>     """
>     from dokima import planner  # planner imports this module, so it is read only when needed
>     try:
>         paths = [p for p in planner.changed_files(base) if p.endswith(".py")]
>     except subprocess.CalledProcessError as e:
>         return [], [f"the docstrings the worker added can't be read: git can't compare with {base} ({e.stderr.strip()})"]
>     return planner.docstring_caps(paths, planner.read_at(base), planner.read_now)
> dokima/agent.py:154:    the worker raised is listed for the reviewer to confirm (raises.for_review), only until the reviewer's next run.
> dokima/agent.py:157:    newest review at each stage, unless it approved, are listed under their old IDs, and an old reply by ID answers one."""
> dokima/agent.py:334:    """Everything wrong with how a hand-back answers the raises listed for its role.
> dokima/agent.py:340:    listed = json.load(open(path)) if os

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "claude.json\|output-format\|--resume" .github/workflows/agent.yml | head
```

> 240:            --model "$MODEL" --dangerously-skip-permissions --max-turns 60 --output-format json > "$OUT/claude.json"

**Agent:** Writing the plan review: block on two bundled criteria and on missing proof that the workflow runs the loop.

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned three criteria: send text back naming fields, a budget of three, post and flag.",
          "Wrote three tests that fake the agent and run the retry loop."],
  "decided": ["Merged the parent's five criteria into three, and dropped its rule that other failures are rejected."],
  "open": ["Asks the owner whether to drop the rule that other failures are rejected."]},
 "verdict": "block",
 "summary": "Two criteria bundle two behaviors each, and no test proves the run itself uses the retry loop.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Bundled criterion",
   "text": "486.2 bundles a cap of three with a separate count; its test checks three things. Split it, and ask the owner what to drop, as the size check says.",
   "evidence": "`tests/test_style_retry.py::test_style_retries_have_their_own_budget_of_three`; `dokima/planner.py` `check_size` nested rule."},
  {"kind": "blocker", "to": "planner", "label": "Bundled, weak test",
   "text": "486.3 bundles posting with flagging. Posting already happens today, and the test hands `record` passed=true itself, so posting is unproven. Keep only the flag.",
   "evidence": "`dokima/words.py` `style` with `STYLE_SOFT`; `tests/test_style_retry.py` `record()` passes `\"true\"`."},
  {"kind": "blocker", "to": "planner", "label": "No proof of wiring",
   "text": "No test proves the run calls the retry loop after the agent ends. A loop never called from `agent.yml` passes every test. Add one.",
   "evidence": "`.github/workflows/agent.yml` has no `dokima.restyle` step; no test reads or runs it."}
 ],
 "answers": [],
 "asks": [
  {"ask": "it sends it back to the agent that wrote it, inside the same run", "source": "https://github.com/dokima-dev/dokima/issues/470#issuecomment-6102982172", "criterion": "486.1"},
  {"ask": "naming each failing field and why", "source": "https://github.com/dokima-dev/dokima/issues/47
```

> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> rc=1

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/Merged the parent's five criteria into three, and dropped/Merged the parent's five criteria into three; dropped/" /tmp/dokima-out/review.json; STAGE=plan python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 486 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 486; echo rc=$?
```

> rc=0
> rc=0

**Agent:** I blocked the plan for [#486](https://github.com/dokima-dev/dokima/issues/486) (style failures go back to their writer, up to 3 times). It goes back to the planner. The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass on it.

All three new tests fail today for the right reason: the retry loop doesn't exist yet and nothing is flagged. Every ask in your comment on [#470](https://github.com/dokima-dev/dokima/issues/470#issuecomment-6102982172) (plain, terse text everywhere) has a criterion.

**Blockers for the planner:**
1. **Criterion 486.2 covers two behaviors.** It combines the cap of 3 with keeping style retries separate from other failures, and its test checks three things. The size check limits a story split from a parent to 3 criteria. So the planner has to split this one and ask you which criterion to drop.
2. **Criterion 486.3 covers two behaviors, and half of it is unproven.** It promises the run still posts and is flagged. Posting after style failures already happens today. The test passes "posted" to the record step itself, so it proves nothing about posting. It should cover only the flag.
3. **Nothing proves the run actually calls the loop.** The workflow file has no retry step, and no test checks one. A loop that is never called would pass every test.

The planner's own question to you is still open: whether to drop the parent plan's rule that other failed checks are still rejected. I didn't answer it on autopilot because none of your words support dropping it, so it waits for you.

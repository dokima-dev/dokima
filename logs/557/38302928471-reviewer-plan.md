# reviewer (plan) for #557

Run: https://github.com/dokima-dev/dokima/actions/runs/38302928471

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #557: A repo setting lets a passed code review approve the merge; owner approval stays the default
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> A repo setting lets a passed code review approve the pull request, so autopilot can merge alone.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/557#issuecomment-6131749557) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/413
> - https://github.com/dokima-dev/dokima/issues/363
> - https://github.com/dokima-dev/dokima/issues/378
> - https://github.com/dokima-dev/dokima/issues/561
> 
> 
> **User story:** Owners choose per repo whether autopilot merges alone or waits for their approval, which stays the default.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmidd

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/parent.json | head -50; git show --stat HEAD; cat tests/test_merge_approval.py
```

> {"number": null}commit 7f414403e5d89da533dfbecd44b1ad8139c11df3
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 20:14:21 2026 +0000
> 
>     planner for #557 (run 38302101193)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_merge_approval.py | 241 +++++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 241 insertions(+)
> """A repo setting lets a passed code review approve the pull request (#557).
> 
> By default a pull request waits for the owner's approval before it merges, as today. The repo's Actions variable
> `DOKIMA_MERGE_APPROVAL`, set to `true`, turns the setting on: a code review that passes then approves the pull request
> on GitHub as Dokima's bot, and autopilot merges it with no owner step. A pull request that changes a workflow file
> still waits for the owner, whatever the setting.
> 
> These tests run the code review through the whole agent workflow (agent.yml), as test_automerge.py does, on the fake
> GitHub of test_automerge_confirmed.py where #60 is protected the way main is: `gh pr merge` only turns on auto-merge
> waiting on an approval ("accepts": "approval"). This file teaches that fake three more things:
>   - the setting: `gh api repos/o/r/actions/variables/DOKIMA_MERGE_APPROVAL` (with or without -q/--jq `.value`) and
>     `gh variable get DOKIMA_MERGE_APPROVAL` answer the value the test chose, 404 when it is unset, or a failure;
>   - an approving review: `gh

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_merge_approval.py 2>&1 | tail -40
```

> m = runs("on-workflow")
>         started(m, "557.3", "on, workflow file")
>         assert m.approvals() == [], f"557.3: Dokima approved #60 though it changes a workflow file: {m.approvals()}"
>         assert m.merged() is None, "557.3: #60 merged though it changes a workflow file"
>         assert not any(l.startswith("Autopilot: merged") for l in m.lines()), f"557.3: #57 says #60 merged: {m.lines()}"
>         on_pr = [ta.visible(b) for b in m.new_comments("pr", PR)]
>         assert any(f"@{OWNER}" in b and ".github/workflows" in b for b in on_pr), \
>             f"557.3: no comment on #60 names .github/workflows and mentions @{OWNER}: {[b[-400:] for b in on_pr]}\n{m.tail()}"
>         c = runs("on")
> >       assert c.approvals() and c.merged() == ta.HEAD, \
>             f"557.3: test setup: with no workflow file and the setting on, #60 was not approved and merged, so this proves nothing"
> E       AssertionError: 557.3: test setup: with no workflow file and the setting on, #60 was not approved and merged, so this proves nothing
> E       assert ([])
> E        +  where [] = approvals()
> E        +    where approvals = <test_merge_approval.SettingReview object at 0x7fd5470e8890>.approvals
> 
> tests/test_merge_approval.py:240: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_merge_approval.py::test_by_default_a_pull_request_waits_for_the_owners_approval - AssertionError: 557.1: test setup: with the setting `true` Dokima approved nothi

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat .github/CODEOWNERS; grep -n "token\|gh pr create\|app-id\|client-id" .github/workflows/agent.yml | head -40; grep -rn "approval\|reviews" dokima/agent.py | grep -i "merge\|approv" | head -30
```

> # Code owners: their approving review is needed to merge, and only their approval starts a build.
> * @RezaSoleymanifar
> 97:        uses: actions/create-github-app-token@v2
> 99:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 101:          skip-token-revoke: true
> 105:          GH_TOKEN: ${{ steps.card-key.outputs.token }}
> 107:          SCRUB_GITHUB: ${{ github.token }}
> 118:          gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
> 122:        uses: actions/create-github-app-token@v2
> 124:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 126:          skip-token-revoke: true
> 130:          GH_TOKEN: ${{ steps.setup-key.outputs.token }}
> 132:          SCRUB_GITHUB: ${{ github.token }}
> 137:          gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
> 140:          GH_TOKEN: ${{ github.token }}
> 172:          GH_TOKEN: ${{ github.token }}
> 224:        uses: actions/create-github-app-token@v2
> 226:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 228:          skip-token-revoke: true
> 232:          GH_TOKEN: ${{ steps.working-key.outputs.token }}
> 234:          SCRUB_GITHUB: ${{ github.token }}
> 239:          gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
> 273:        uses: actions/create-github-app-token@v2
> 275:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 277:          skip-token-revoke: tru

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 2730,2760p dokima/agent.py; sed -n 310,342p .github/workflows/agent.yml; grep -n "approv" AGENTS.md | head
```

> read.append(on_autopilot(repo, number, strict=True))
>                         unread.clear()
>                     return read[0]
>                 ups = []
> 
>                 def parent():
>                     # The parent's words, read once and only when an assumption cites somewhere other than this issue.
>                     if not ups:
>                         ups.append(parent_words(repo, number))
>                     return ups[0]
>                 step = next_step(items, rec, owners, autopilot=autopilot, body=d.get("body") or "", number=number, parent=parent)
>                 if approves_work(rec) and step[0] != "start":
>                     # On autopilot the code review's approval stands in for the owner's: the pull request merges by itself.
>                     on = autopilot()
>                     if on is None:
>                         step = ("stop", f"{UNREAD} {step[1]}")
>                     elif on:
>                         pr, how, why = automerge(repo, number)
>                         if how == "merged":
>                             step = ("merged", f"Autopilot merged PR #{pr}; what it unblocks starts when the issue closes.")
>                         elif how == "queued":
>                             step = ("queued", f"PR #{pr} is in the merge queue; GitHub merges it when the queue's checks pass.")
>                         elif how == "waits":
>                             step = ("stop", f"PR #{pr} waits for your approval before it merges. Approve it on GitHub, or "
>               

**Agent:** I ran the plan's tests: all three fail today because the feature is missing. Now I'm writing the review, which blocks on how the bot would approve.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote three criteria and three tests for an off-by-default merge approval setting."],
  "decided": ["The bot itself approves the pull request when the setting is on.", "An unreadable setting counts as off."],
  "open": ["Whether the earlier issue asking the same closes as a duplicate.", "Whether GitHub lets the bot approve its own pull request."]
 },
 "verdict": "block",
 "summary": "The plan's tests let the bot approve its own pull request, which GitHub refuses, so passing them proves nothing.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Weak test",
   "text": "557.2's fake GitHub lets the pull request's author, Dokima's bot, approve it and counts that as a code owner's review. Real GitHub refuses both. Fix the fake to match GitHub, then re-plan once the owner answers P2.",
   "evidence": "`tests/test_merge_approval.py` `approve()` accepts `fake-token` and lifts `accepts`; `agent.yml:340` opens the PR with the app key; `.github/CODEOWNERS` lists only the owner."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Missing edge case",
   "text": "557.2 has no case for GitHub refusing the bot's approval, the error a user will hit; it must wait for the owner and say why. Add it to `test_with_the_setting_on_a_passed_code_review_approves_and_autopilot_merges`.",
   "evidence": "In the fake, `approve()` answers 403 for any other key; no test drives that path."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "By default a pull request waits for the owner's approval before it merges, as today.", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "thats why i thought default behavior is hitl and you can turn on autopilot approval setting", "source": "https://github.com/dokima-dev/dokima/issues/557", "criterion": "557.1"},
  {"ask": "With the repo's merge approval setting turned on, a 
```

> Exit code 1
> raise 1's text holds 37 words, over its cap of 30: cut 7, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d["raises"][0]["text"]="557.2's fake GitHub lets the bot approve its own pull request as a code owner; real GitHub refuses both. Make the fake match GitHub, then re-plan after P2."
json.dump(d,open(p,"w"),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 557 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for [#557](https://github.com/dokima-dev/dokima/issues/557) (a repo setting that lets a passed code review approve the merge). Its tests would pass, but they wouldn't prove the setting works on real GitHub. The review is saved in `/tmp/dokima-out/review.json` and passes both hand-back checks.

**What's fine**
- All three of your "Done when" asks have a matching criterion, and each criterion covers one thing.
- I ran the planner's 3 tests and all fail today because the feature is missing, which is the right reason.
- With the setting off, a pull request still waits for you. That holds whether the setting is unset, false or unreadable. A pull request that changes a workflow file also already waits for you.

**Blockers, both sent back to the planner**
1. **The test's fake GitHub allows something real GitHub refuses.** In the test, Dokima's bot approves its own pull request and the fake counts that as your code-owner review. On real GitHub this fails twice:
   - The bot opens the pull request with its app key (`agent.yml:340`), and GitHub doesn't let an author approve their own pull request.
   - `.github/CODEOWNERS` lists only you, so the bot's approval wouldn't count as a code owner's review anyway.

   The fix is to make the fake behave like GitHub, then re-plan once you answer the planner's question below.
2. **A likely failure is untested.** Nothing covers GitHub refusing the bot's approval. The pull request should then wait for you and say why.

**Two planner questions are left for you; I couldn't answer them from your own words:**
- Should [#413](https://github.com/dokima-dev/dokima/issues/413) (asks for the same setting) close as a duplicate of this one?
- If GitHub refuses the bot's approval, should Dokima get around the branch rule some other way? The blocker above shows this refusal will happen with today's setup, so the plan can't work as written until you decide how the approval gets made.

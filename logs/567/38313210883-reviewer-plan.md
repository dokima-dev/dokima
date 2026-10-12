# reviewer (plan) for #567

Run: https://github.com/dokima-dev/dokima/actions/runs/38313210883

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 36
> drwxr-xr-x  3 runner runner 4096 Oct 12 21:51 .
> drwxrwxrwt 18 root   root   4096 Oct 12 21:51 ..
> drwxr-xr-x  2 runner runner 4096 Oct 12 21:51 in
> -rw-r--r--  1 runner runner 9159 Oct 12 21:51 issue.md
> -rw-r--r--  1 runner runner    2 Oct 12 21:51 open_blockers.json
> -rw-r--r--  1 runner runner   16 Oct 12 21:51 parent.json
> -rw-r--r--  1 runner runner 3208 Oct 12 21:51 plan.json
> 
> in:
> total 12
> drwxr-xr-x 2 runner runner 4096 Oct 12 21:51 .
> drwxr-xr-x 3 runner runner 4096 Oct 12 21:51 ..
> -rw-r--r-- 1 runner runner 3934 Oct 12 21:51 01-planner.json
> # Issue #567: Stop crediting the unrelated GitHub user "dokima" on commits
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Dokima's own commits are credited to its bot, never to the unrelated GitHub user named dokima.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/567#issuecomment-6133225533) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/110
> 
> 
> **User story:** The stranger called dokima no longer shows up as a contributor; every Dokima commit is credited to its bot.
> 
> <img src="https://raw.githubus

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_bot_identity.py; grep -rn "users.noreply\|user.email\|user.name\|bot@dokima" --include=* -r . --exclude-dir=.git | grep -v "^./tests/test_bot_identity" | head -50; ls .github/workflows
```

> """Dokima's own commits are credited to its bot, never to the unrelated GitHub user "dokima".
> 
> GitHub maps a `<name>@users.noreply.github.com` address to the account called `<name>`, so a commit made as
> `dokima@users.noreply.github.com` credits the stranger at github.com/dokima as a contributor (#567). These tests
> check every place Dokima commits: the worker's merge of main, the play-through, and every other file in the repo.
> """
> 
> import os
> import re
> import subprocess
> import tempfile
> 
> import pytest
> 
> ROOT = os.path.join(os.path.dirname(__file__), "..")
> BOT_NAMES = {"dokima-runtime[bot]", "${SLUG}[bot]"}
> BOT_EMAILS = {"337511017+dokima-runtime[bot]@users.noreply.github.com",
>               "${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"}
> REZA_EMAIL = "34189616+RezaSoleymanifar@users.noreply.github.com"
> NOREPLY = re.compile(r"[^\s\"'<>=`(),:;]+@users\.noreply\.github\.com")
> 
> 
> def starting_branch_step():
>     """Returns the lines of agent.yml's step that merges main into the worker's branch."""
>     text = open(os.path.join(ROOT, ".github/workflows/agent.yml")).read()
>     start = text.index("- name: Starting branch")
>     end = text.index("\n      - name:", start + 1)
>     return text[start:end].splitlines()
> 
> 
> def identity_in_effect(lines, i):
>     """Returns the git name and email in effect for line i of the step.
> 
>     Either is None when the step never sets it. A `-c user.name=` / `-c user.email=` on the line itself wins; otherwise the last `git config user.name/email`
>     above it

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 120,165p .github/workflows/agent.yml; grep -n "SLUG\|BOT_ID" .github/workflows/agent.yml | head -30; sed -n 190,210p dokima/playthrough.py; python -m pytest -q tests/test_bot_identity.py 2>&1 | tail -20
```

> if: env.CARD_ID != ''
>         continue-on-error: true
>         uses: actions/create-github-app-token@v2
>         with:
>           app-id: ${{ vars.DOKIMA_APP_ID }}
>           private-key: ${{ secrets.DOKIMA_APP_KEY }}
>           skip-token-revoke: true
>       - name: The card says setting up
>         if: env.CARD_ID != ''
>         env:
>           GH_TOKEN: ${{ steps.setup-key.outputs.token }}
>           SCRUB_CLAUDE: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
>           SCRUB_GITHUB: ${{ github.token }}
>         run: |
>           python3 -m dokima.agent card "$ROLE" "$STAGE" setting-up > /tmp/card.md
>           gh api -X PATCH "repos/$GITHUB_REPOSITORY/issues/comments/$CARD_ID" -F body=@/tmp/card.md --silent \
>             || echo "::warning title=Card not updated::the card could not say setting up"
>           gh api -X DELETE installation/token --silent || echo "::warning title=Key not revoked::the card's key could not be revoked"
>       - name: Starting branch
>         env:
>           GH_TOKEN: ${{ github.token }}
>         run: |
>           if git ls-remote --exit-code --heads origin "try/issue-$N" >/dev/null; then
>             git fetch -q origin "try/issue-$N" && git checkout -q -B "try/issue-$N" FETCH_HEAD
>             # A worker's branch that clashes with main still starts: the merge is committed with its conflict markers,
>             # the clashed files are listed for the fence, and the worker resolves them. Main's changes are in BASE.
>             if [ "$ROLE" = worker ] && ! git -c user.name=do

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_bot_identity.py 2>&1 | grep FAILED; sed -n 300,330p .github/workflows/agent.yml; grep -n "Starting branch\|app-slug\|id: app" .github/workflows/agent.yml
```

> FAILED tests/test_bot_identity.py::test_worker_merge_of_main_is_credited_to_the_bot - AssertionError: 567.1: the worker's merge of main commits as 'dokima@users.noreply.github.com', not the bot's address
> FAILED tests/test_bot_identity.py::test_worker_conflict_commit_is_credited_to_the_bot - AssertionError: 567.1: the clash commit is made as 'dokima@users.noreply.github.com', not the bot's address
> FAILED tests/test_bot_identity.py::test_bot_identity_in_step_is_defined - AssertionError: 567.1: the Starting branch step still names dokima@users.noreply.github.com
> FAILED tests/test_bot_identity.py::test_playthrough_commits_as_the_bot - AssertionError: 567.2: the play-through's commit is authored by dokima-playthrough <dokima-playthrough@users.noreply.github.com>, not dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> FAILED tests/test_bot_identity.py::test_no_file_commits_as_anyone_but_the_bot_or_reza - AssertionError: 567.3: files commit as someone other than the bot or Reza: 41898282+github-actions[bot]@users.noreply.github.com in .github/workflows/wiki.yml; dokima-playthrough@users.noreply.github.com in dokima/playthrough.py; dokima@users.noreply.github.com in .github/workflows/agent.yml
>         run: |
>           # A clashed file still holding conflict markers fails the hand-back, saying which, so nothing is pushed.
>           if ! python3 -m dokima.fence "$BASE" "$PACK/plan.json" /tmp/clashed.txt > "$OUT/dropped.txt" 2> /tmp/fence-err.txt; then
>         

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat .github/workflows/wiki.yml; grep -rn "git commit\|git -C.*commit\|\"commit\"\|'commit'" .github dokima --include=*.yml --include=*.py | grep -v "^tests" | head -20; grep -n "setup-key\|id: " .github/workflows/agent.yml | head
```

> name: wiki
> on:
>   push:
>     branches: [main]
>     paths: ["docs/wiki/**"]
>   workflow_dispatch:
> permissions:
>   contents: write
> jobs:
>   sync:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>       - name: Copy docs/wiki to the GitHub wiki
>         env:
>           TOKEN: ${{ github.token }}
>         run: |
>           git clone "https://x-access-token:${TOKEN}@github.com/${GITHUB_REPOSITORY}.wiki.git" wiki
>           rsync -a --delete --exclude .git docs/wiki/ wiki/
>           cd wiki
>           git config user.name "github-actions[bot]"
>           git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
>           git add -A
>           if git diff --cached --quiet; then
>             echo "Wiki already up to date"
>           else
>             git commit -m "Sync from ${GITHUB_SHA::7}" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
>             git push
>           fi
> .github/workflows/wiki.yml:27:            git commit -m "Sync from ${GITHUB_SHA::7}" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> .github/workflows/agent.yml:326:            git commit -qm "$ROLE for #$N (run ${{ github.run_id }})" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> .github/workflows/agent.yml:401:          git -C "$W" -c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com" commit -qm "Con

**Agent:** I've checked the plan and run its tests; all 5 fail today for the right reason. Next I'm checking whether the blank-address test can be fooled.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import re, tests.test_bot_identity as t
lines = t.starting_branch_step()
text = "\n".join(lines)
text = text.replace("GH_TOKEN: ${{ github.token }}", "GH_TOKEN: ${{ github.token }}\n          SLUG: ${{ steps.app.outputs.app-slug }}\n          BOT_ID: ${{ steps.app.outputs.app-slug }}")
text = text.replace("git -c user.name=dokima -c user.email=dokima@users.noreply.github.com", 'git -c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"')
t.starting_branch_step = lambda: text.splitlines()
for f in (t.test_worker_merge_of_main_is_credited_to_the_bot, t.test_worker_conflict_commit_is_credited_to_the_bot, t.test_bot_identity_in_step_is_defined):
    f(lambda *a: None); print(f.__name__, "PASSES")
EOF
```

> Exit code 1
> Traceback (most recent call last):
>   File "<stdin>", line 1, in <module>
> ModuleNotFoundError: No module named 'tests'

`7. Bash`
```
cd /home/runner/work/dokima/dokima; PYTHONPATH=tests python3 - <<'EOF'
import re, test_bot_identity as t
lines = t.starting_branch_step()
text = "\n".join(lines)
text = text.replace("GH_TOKEN: ${{ github.token }}", "GH_TOKEN: ${{ github.token }}\n          SLUG: ${{ steps.app.outputs.app-slug }}\n          BOT_ID: ${{ steps.app.outputs.app-slug }}")
text = text.replace("git -c user.name=dokima -c user.email=dokima@users.noreply.github.com", 'git -c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"')
t.starting_branch_step = lambda: text.splitlines()
for f in (t.test_worker_merge_of_main_is_credited_to_the_bot, t.test_worker_conflict_commit_is_credited_to_the_bot, t.test_bot_identity_in_step_is_defined):
    f(lambda *a: None); print(f.__name__, "PASSES")
EOF
```

> test_worker_merge_of_main_is_credited_to_the_bot PASSES
> test_worker_conflict_commit_is_credited_to_the_bot PASSES
> test_bot_identity_in_step_is_defined PASSES

**Agent:** The blank-address test passes even when the bot's name comes from a step that runs later, so it would come out blank. Writing the review.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria: the worker's merge of main, the play-through, and no stranger's address in any file.",
          "The planner wrote five tests; all fail today because the old addresses are still there."],
  "decided": ["The wiki sync moves to Dokima's bot too.", "Old commits in history stay as they are."],
  "open": ["Two questions for the owner: the wiki sync and history."]},
 "verdict": "block",
 "summary": "One test can pass while the merge still commits with a blank bot address; the planner must tighten it.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "567.1 weak test",
   "text": "`test_bot_identity_in_step_is_defined` passes when the step takes `SLUG`/`BOT_ID` from `steps.app`, which runs later, so the address is blank. Fix: reject values from steps after Starting branch.",
   "evidence": "Patching the step to `SLUG: ${{ steps.app.outputs.app-slug }}` passes all three 567.1 tests; `id: app` is at `agent.yml` line 308."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "The owner wants no other noreply address in any file, which includes the wiki sync's.",
   "words": "no file in the repo commits with a `<name>@users.noreply.github.com` address other than the bot or Reza",
   "source": "https://github.com/dokima-dev/dokima/issues/567", "changes": false},
  {"raise": "P2", "answer": "done", "why": "The owner's acceptance names files only, so history is left alone.",
   "words": "Acceptance: no file in the repo commits with a `<name>@users.noreply.github.com` address other than the bot or Reza.",
   "source": "https://github.com/dokima-dev/dokima/issues/567", "changes": false}
 ],
 "asks": [
  {"ask": "commit as the bot identity `dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>` everywhere", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.3"},
  {"ask": ".githu
```

> Exit code 1
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/The planner wrote three criteria: the worker's merge of main, the play-through, and no stranger's address in any file./The planner wrote three criteria: worker merges, the play-through, and every file./; s/The planner wrote five tests; all fail today because the old addresses are still there./The planner wrote five tests; all fail today on the old addresses./" /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 567 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I blocked the plan for [#567](https://github.com/dokima-dev/dokima/issues/567) (stop crediting the stranger "dokima" on commits). One test is too weak and goes back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**The blocker:** the test meant to catch a blank bot address in the worker's merge of main can be fooled.
- If the merge step takes the bot's name and number from the step that makes the bot's key, both come out blank, because that step (`id: app`, `agent.yml` line 308) runs later.
- The commit would then be credited to an empty address. I made that change in memory, without touching any file, and all three tests for this criterion still passed.
- The fix: the test should reject values taken from a step that runs after the merge.

**The rest of the plan holds up:**
- I ran all 5 new tests. Each fails today only because the old addresses are still there.
- Every ask in the issue maps to one of the 3 criteria. `worker.yml` no longer exists; its merge of main now lives in `agent.yml`.
- Each criterion is one behavior and the size is fine. Two of the tests do the real thing: one makes a real commit and reads back who made it, and one scans every file.

**I answered the planner's two questions for you, using your words in the issue:** "no file in the repo commits with a `<name>@users.noreply.github.com` address other than the bot or Reza".
- **Wiki sync:** it moves to Dokima's bot too. The wiki workflow has no bot key, so the worker will likely write the bot's name and address in by hand.
- **History:** old commits keep their old names. Your acceptance names files only, and rewriting history would rewrite main.

If you meant history to be cleaned up as well, say so with `/plan`.

Once the planner fixes that test, the plan goes back to the plan reviewer.

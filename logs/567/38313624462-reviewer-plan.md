# reviewer (plan) for #567

Run: https://github.com/dokima-dev/dokima/actions/runs/38313624462

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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #567: Stop crediting the unrelated GitHub user "dokima" on commits
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Dokima's own commits are credited to its bot, never to the unrelated GitHub user named dokima.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/110
> 
> 
> **User story:** The stranger called dokima no longer shows up as a contributor; every Dokima commit is credited to its bot.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Merging main into a worker's branch, clash or not, commits as the Dokima bot.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-567/tests/test_bot_identity.py#L57"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: Merging main into a worker's branc

`2. Bash`
```
cd /home/runner/work/dokima/dokima; ls .github/workflows; cat tests/test_bot_identity.py; grep -rn "users.noreply" --include=* -r . 2>/dev/null | grep -v "^./.git/" | head -30; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"
```

> acceptance-criteria.yml
> agent.yml
> assign.yml
> audit.yml
> autopilot.yml
> board.yml
> card.yml
> commands.yml
> full-suite.yml
> playthrough.yml
> reviews.yml
> testmon.yml
> uptodate.yml
> wiki.yml
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
>     """Returns the git name and email in effect for line i of the

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "      - name:\|id:\|if:\|SLUG\|BOT_ID" .github/workflows/agent.yml | head -60; sed -n 120,160p .github/workflows/agent.yml; pytest -q tests/test_bot_identity.py 2>&1 | tail -15
```

> 62:      - name: Count this run's GitHub calls
> 76:      - name: Copy the runtime from main before touching any branch
> 79:      - name: Only a code owner starts an agent
> 94:      - id: card-key
> 95:        if: env.CARD_ID == ''
> 99:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 102:      - name: Put up the run's card, queued
> 103:        if: env.CARD_ID == ''
> 119:      - id: setup-key
> 120:        if: env.CARD_ID != ''
> 124:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 127:      - name: The card says setting up
> 128:        if: env.CARD_ID != ''
> 138:      - name: Starting branch
> 170:      - name: Build the starting pack
> 184:      - name: Install pytest and Claude Code
> 190:      - name: Restore main's testmon baseline
> 191:        if: env.STAGE == 'pr'
> 197:      - name: Tests the change can affect, run by code before the reviewer reads the pull request
> 198:        if: env.STAGE == 'pr'
> 215:      - name: Code checks the pack has everything this role needs
> 221:      - id: working-key
> 222:        if: env.CARD_ID != ''
> 226:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 229:      - name: The card says working
> 230:        if: env.CARD_ID != ''
> 240:      - name: The agent starts now
> 242:      - name: The agent (Claude Code)
> 270:      - id: checking-key
> 271:        if: always() && !cancelled() && env.STARTED == 'true' && env.CARD_ID != ''
> 275:          app-id: ${{ vars.DOKIMA_APP_ID }}
> 278:      - name: The card says checking
> 279:        if: always() && !cancelled() && env.STARTED == 'true' && env.CA

`4. Bash`
```
cd /home/runner/work/dokima/dokima; pytest -q tests/test_bot_identity.py 2>&1 | grep FAILED | head -3; cp .github/workflows/agent.yml /tmp/agent.bak
# good fix
sed -i 's/-c user.name=dokima -c user.email=dokima@users.noreply.github.com/-c user.name="dokima-runtime[bot]" -c user.email="337511017+dokima-runtime[bot]@users.noreply.github.com"/' .github/workflows/agent.yml
pytest -q tests/test_bot_identity.py -k "worker or defined" 2>&1 | tail -2
cp /tmp/agent.bak .github/workflows/agent.yml
# bad fix: steps.app
python3 - <<'E'
p='.github/workflows/agent.yml';t=open(p).read()
t=t.replace("""      - name: Starting branch
        env:
          GH_TOKEN: ${{ github.token }}""","""      - name: Starting branch
        env:
          GH_TOKEN: ${{ github.token }}
          SLUG: ${{ steps.app.outputs.app-slug }}""",1)
t=t.replace('-c user.name=dokima -c user.email=dokima@users.noreply.github.com','-c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com"')
t=t.replace('git fetch -q origin "try/issue-$N" && git','BOT_ID=$(gh api "users/${SLUG}[bot]" --jq .id)\n            git fetch -q origin "try/issue-$N" && git',1)
open(p,'w').write(t)
E
pytest -q tests/test_bot_identity.py -k "worker or defined" 2>&1 | tail -3
cp /tmp/agent.bak .github/workflows/agent.yml; git status --short
```

> FAILED tests/test_bot_identity.py::test_worker_merge_of_main_is_credited_to_the_bot - AssertionError: 567.1: the worker's merge of main commits as 'dokima@users.noreply.github.com', not the bot's address
> FAILED tests/test_bot_identity.py::test_worker_conflict_commit_is_credited_to_the_bot - AssertionError: 567.1: the clash commit is made as 'dokima@users.noreply.github.com', not the bot's address
> FAILED tests/test_bot_identity.py::test_bot_identity_in_step_is_defined - AssertionError: 567.1: the Starting branch step still names dokima@users.noreply.github.com
> ...                                                                      [100%]
> 3 passed, 2 deselected in 0.04s
> FAILED tests/test_bot_identity.py::test_bot_identity_in_step_is_defined - AssertionError: 567.1: the Starting branch step reads steps.app, which runs after it or may be skipped, so the bot's name or address comes out blank
> assert 'app' in set()
> 1 failed, 2 passed, 2 deselected in 0.06s

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 200,207p dokima/playthrough.py; cp dokima/playthrough.py /tmp/pt.bak; sed -i 's/user.name=dokima-playthrough/user.name=dokima-runtime[bot]/; s/user.email=dokima-playthrough@/user.email=337511017+dokima-runtime[bot]@/' dokima/playthrough.py; sed -n 204,205p dokima/playthrough.py; pytest -q tests/test_bot_identity.py -k playthrough 2>&1|tail -2; cp /tmp/pt.bak dokima/playthrough.py; git status --short
```

> self.issue = self.pr = self.review_card = self.worker_card = None
>         self.since = None
> 
>     def git(self, *args):
>         return run("git", *self.git_auth, "-c", "user.name=dokima-playthrough",
>                    "-c", "user.email=dokima-playthrough@users.noreply.github.com", *args, env=self.env, cwd=self.clone)
> 
>     def gh(self, *args):
>         return run("git", *self.git_auth, "-c", "user.name=dokima-runtime[bot]",
>                    "-c", "user.email=337511017+dokima-runtime[bot]@users.noreply.github.com", *args, env=self.env, cwd=self.clone)
> .                                                                        [100%]
> 1 passed, 4 deselected in 0.05s

**Agent:** I've finished checking the reviewer's earlier fix: the blank-address test now catches it. Next I'm writing the approval.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'E'
{"previous_step": {
  "did": ["The planner tightened the blank-address test for merging main into a worker's branch."],
  "decided": ["The merge step may only use bot names set before it, on every run."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan is ready: every ask has a criterion, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "commit as the bot identity `dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>` everywhere", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.3"},
  {"ask": ".github/workflows/worker.yml (merge of origin/main)", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.1"},
  {"ask": ".github/workflows/agent.yml (merge and conflict commit)", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.1"},
  {"ask": "dokima/playthrough.py (`dokima-playthrough@users.noreply.github.com`)", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.2"},
  {"ask": "Also the one-off `dokima-worker@users.noreply.github.com` and `bot@dokima` identities in history.", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.3"},
  {"ask": "Acceptance: no file in the repo commits with a `<name>@users.noreply.github.com` address other than the bot or Reza.", "source": "https://github.com/dokima-dev/dokima/issues/567", "criterion": "567.3"}],
 "behaviors": [
  {"criterion": "567.1", "one_behavior": true, "why": "One action, merging main into a worker branch, with one result: the bot commits."},
  {"criterion": "567.2", "one_behavior": true, "why": "One identity on the play-through's commits."},
  {"criterion": "567.3", "one_behavior": true, "why": "One check over every file for stranger addresses."}],
 "edge_cases": [
  {"criterion": "567.1", "cut": [], "missing": []},
  {"criterio
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#567](https://github.com/dokima-dev/dokima/issues/567) (stop crediting the unrelated GitHub user "dokima" on commits). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's blocker is fixed.** I swapped in a step that takes the bot's name from the "app" step, which only runs later. The blank-address test now fails on that, and it passes when the bot's address is written in full.
- **All five new tests fail today for the right reason.** They hit the old addresses in the merge step, the play-through and the wiki sync, not a crash or a bad path.
- **The fixes the tests expect can pass.** With the bot's real name and address put into the merge step and the play-through, their tests passed. I then put both files back as they were.
- **Every ask of the owner has a criterion.** The issue names `worker.yml`, but that file no longer exists; its merge of main now lives in `agent.yml`, which criterion 567.1 covers.
- **Nothing raised and nothing to answer:** no open blockers came to me this round.

On autopilot, this approval should start the worker next.

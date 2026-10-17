# reviewer (plan) for #787

Run: https://github.com/dokima-dev/dokima/actions/runs/39023853094

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (30.4KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/b6685a23-443a-49cc-a174-fab4b6537e3c/tool-results/bfeji1kf5.txt
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
> # Issue #787: Autopilot merges by the repo's branch, method and labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 784 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> # Issue #787: Autopilot merges by the repo's branch, method and labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 784 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/791
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/784
> 
> 
> **User story:** Autopilot merges into my repo's branch, my way, using my label names.
> 
> <img src="https://raw.githubus

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json owner_words.json parent.json
```

> []{
>  "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232040687": "/plan Take the plan review's two test gaps as given: a test where adding the label named in settings moves the board card, and a test that turning autopilot off removes the settings' label.\n\n(Answered by Claude for Reza, at his request.)",
>  "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232347057": "/plan On the default-branch question: ship the default branch setting empty, not \"main\". Empty means ask GitHub for the repo's default branch; a repo that names a branch in its settings gets that one. Shipped defaults reach every repo that installs Dokima, and not every repo calls its default branch main.\n\n(Answered by Claude for Reza, at his request, from his standing rule that Dokima is built for other repos and never tuned to its own.)",
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n

`4. Bash`
```
cd /tmp/pack; cat issue.md
```

`5. Bash`
```
cd /tmp/pack; cat open_blockers.json owner_words.json parent.json
```

> # Issue #787: Autopilot merges by the repo's branch, method and labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779, 784 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/791
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/783
> - https://github.com/dokima-dev/dokima/issues/784
> 
> 
> **User story:** Autopilot merges into my repo's branch, my way, using my label names.
> 
> <img src="https://raw.githubus

> []{
>  "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232040687": "/plan Take the plan review's two test gaps as given: a test where adding the label named in settings moves the board card, and a test that turning autopilot off removes the settings' label.\n\n(Answered by Claude for Reza, at his request.)",
>  "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232347057": "/plan On the default-branch question: ship the default branch setting empty, not \"main\". Empty means ask GitHub for the repo's default branch; a repo that names a branch in its settings gets that one. Shipped defaults reach every repo that installs Dokima, and not every repo calls its default branch main.\n\n(Answered by Claude for Reza, at his request, from his standing rule that Dokima is built for other repos and never tuned to its own.)",
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n

`6. Bash`
```
cd /tmp/pack; cat plan.json; python3 -c "
import json
for f in ['in/04-reviewer-plan.json','in/05-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"
```

> {
>  "kind": "user_story",
>  "title": "Autopilot merges by the repo's branch, method and labels",
>  "summary": "Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.",
>  "user_story": "Autopilot merges into my repo's branch, my way, using my label names.",
>  "acceptance_criteria": [
>   {
>    "text": "Autopilot merges pull requests into the default branch the settings name.",
>    "words": "`branch.default: main`",
>    "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
>    "files": [
>     "dokima/agent_autopilot.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "The settings name a branch GitHub does not have: nothing merges, and the reason names it.",
>      "test": "tests/test_settings_autopilot.py::test_a_default_branch_github_lacks_stops_saying_which"
>     }
>    ]
>   },
>   {
>    "text": "With the default branch setting left empty, autopilot merges into the repo's default branch on GitHub.",
>    "words": "better: read repo default_branch",
>    "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729",
>    "files": [
>     "dokima/agent_autopilot.py",
>     "dokima/settings.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "The setting is empty text rather than no value.",
>      "test": "tests/test_settings_autopilot.py::test_an_empty_text_default_branch_also_uses_githubs"
>     }
>    ]
>   },
>   {
>    "text": "Autopilot merges with the merge method the settings name.",
>    "words": "`merge.method: squash`"

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 833ec1f HEAD --stat; git diff 833ec1f HEAD -- tests/test_settings_merge.py tests/test_start.py dokima/
```

> tests/test_settings_autopilot.py | 110 +++++++++++++++++++++++++++++++++++++--
>  tests/test_settings_merge.py     |   2 +-
>  tests/test_start.py              |   5 +-
>  3 files changed, 112 insertions(+), 5 deletions(-)
> diff --git a/tests/test_settings_merge.py b/tests/test_settings_merge.py
> index 8513d8b..e7aeafa 100644
> --- a/tests/test_settings_merge.py
> +++ b/tests/test_settings_merge.py
> @@ -133,7 +133,7 @@ def test_the_shipped_defaults_hold_the_owners_list(tmp_path, record_property):
>          "setup.python": "3.12",
>          "fence.test_setup_files": ["conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"],
>          "protected_paths": [".github/"],
> -        "branch.default": "main",
> +        "branch.default": "",
>          "records.branch": "logs",
>          "owner_docs": "AGENTS.md",
>          "style.docstrings": "required",
> diff --git a/tests/test_start.py b/tests/test_start.py
> index f22c2fe..3a7260b 100644
> --- a/tests/test_start.py
> +++ b/tests/test_start.py
> @@ -52,7 +52,8 @@ version of its body, oldest first, the way GitHub keeps a comment that is edited
>  or by `gh api` on repos/o/r/issues/N/comments (creates) and repos/o/r/issues/comments/ID (reads, or edits with PATCH),
>  the body given as -f/-F/--field/--raw-field body=..., body=@file, or --input with a JSON file. `-q`/`--jq` with a
>  plain `.field` picks that field. The author is Dokima's bot for the app's token and github-actions for the workflow's
> -own token. `gh issue view` and `gh pr view` show these comm

`8. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 833ec1f HEAD -- tests/test_settings_autopilot.py; sed -n 1,120p tests/test_settings_autopilot.py
```

> diff --git a/tests/test_settings_autopilot.py b/tests/test_settings_autopilot.py
> index b7cb445..d6903d0 100644
> --- a/tests/test_settings_autopilot.py
> +++ b/tests/test_settings_autopilot.py
> @@ -3,14 +3,15 @@
>  The settings live in `.dokima/settings.yaml` in the repo the run works in, over Dokima's shipped defaults in
>  `dokima/defaults.yaml`. This story reads these of them:
>  
> -    branch: {default: main}          # the branch autopilot merges into; empty or unset asks GitHub for the repo's own
> +    branch: {default: main}          # the branch autopilot merges into; empty (as shipped) asks GitHub for the repo's own
>      merge: {method: squash}          # how autopilot merges: squash, merge or rebase
>      gate: {checks_wait_min: 45}      # how many minutes the merge gate waits for checks still running
>      labels: {autopilot: autopilot, filed: filed-by-dokima}   # the autopilot label and the label on issues Dokima files
>  
>  Each test writes a settings file into a temp folder, runs there, and calls autopilot's or the board's own code
> -against a fake GitHub in memory standing in for `gh`. Time is faked, so a 45-minute wait costs nothing. Nothing
> -leaves the machine.
> +against a fake GitHub in memory standing in for `gh`. Time is faked, so a 45-minute wait costs nothing. The tests
> +of 787.8 and 787.9 run `python3 -m dokima.settings` itself, with a fake `gh` program first on the PATH and a fake
> +GitHub event file. Nothing leaves the machine.
>  """
>  import json
>  import os
> @@ -24,6 +25,7 

**Agent:** I'm reviewing the plan for issue 787. Next I check the new tests for criteria 8 and 9, then run them.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; ls dokima/settings.py dokima/defaults.yaml; grep -n "default" dokima/defaults.yaml | head; grep -n "def \|__main__\|env\|DEFAULT_BRANCH" dokima/settings.py | head -60; grep -rn "DEFAULT_BRANCH" .github/workflows | head
```

> dokima/defaults.yaml
> dokima/settings.py
> 1:# Dokima's shipped defaults (#779). A repo's .dokima/settings.yaml names only what differs; dokima/settings.py merges
> 23:  default: main
> 6:`python3 -m dokima.settings env` prints the test commands, test folder, branches, bot, co-author and owner docs file as `NAME=value` lines for a
> 31:def load(path):
> 44:def entry_name(entry):
> 49:def by_name(base, mine):
> 61:def merge(base, mine, warn, path=""):
> 79:def read(repo=".", warn=None):
> 90:def setup_lines(got):
> 101:def env_lines(got):
> 110:              "TESTS_DIR": tests["dir"], "DEFAULT_BRANCH": got["branch"]["default"],
> 122:def main(argv=()):
> 129:        if list(argv) == ["env"]:
> 130:            print(env_lines(got))
> 142:if __name__ == "__main__":
> .github/workflows/agent.yml:94:          if ! grep -q '^DEFAULT_BRANCH=' /tmp/env.txt; then
> .github/workflows/agent.yml:96:            printf 'TESTS_AFFECTED=testmon\nTESTS_DIR=tests\nDEFAULT_BRANCH=main\nRECORDS_BRANCH=logs\nBOT_SLUG=dokima-runtime\n' > /tmp/env.txt
> .github/workflows/agent.yml:200:            if [ "$ROLE" = worker ] && ! git -c user.name="${SLUG}[bot]" -c user.email="${BOT_ID}+${SLUG}[bot]@users.noreply.github.com" merge -q --no-edit "origin/$DEFAULT_BRANCH"; then
> .github/workflows/agent.yml:208:              MB=$(git merge-base HEAD "origin/$DEFAULT_BRANCH")
> .github/workflows/agent.yml:211:                MAINS=$(git rev-parse -q --verify "origin/$DEFAULT_BRANCH:$f" || true)
> .github/workflows/agent.yml:228:            if [ "$ROLE

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 80,100p .github/workflows/agent.yml; grep -rn "dokima.settings" .github/workflows | head; sed -n 95,142p dokima/settings.py
```

> - name: Copy the runtime from main before touching any branch
>         # Main's test commands, test folder, branches, bot, co-author and owner docs file, over Dokima's defaults, for
>         # every later step (#795, #796); a settings reader with no env mode (before #795) gives Dokima's own.
>         # The owner docs file the settings name (AGENTS.md by default) and the topic files it links come too: the river
>         # checks the owner's words a plan reviewer quotes from them. So do main's house rules files (#796).
>         run: |
>           mkdir -p /tmp/runtime && cp -r dokima /tmp/runtime/dokima
>           for f in settings.yaml agents.yml; do
>             if [ -f ".dokima/$f" ]; then mkdir -p /tmp/runtime/.dokima && cp ".dokima/$f" /tmp/runtime/.dokima/; fi
>           done
>           (cd /tmp/runtime && python3 -m dokima.settings env) > /tmp/env.txt 2> /tmp/env-err.txt \
>             || { echo "The settings file stopped the run: $(paste -sd' ' /tmp/env-err.txt)" > /tmp/why.txt
>                  echo "::error title=Bad settings::$(cat /tmp/why.txt)"; exit 1; }
>           cat /tmp/env-err.txt >&2
>           if ! grep -q '^DEFAULT_BRANCH=' /tmp/env.txt; then
>             echo "::notice title=Old settings::No settings reader with an env mode here, so Dokima's own branches and bot are used."
>             printf 'TESTS_AFFECTED=testmon\nTESTS_DIR=tests\nDEFAULT_BRANCH=main\nRECORDS_BRANCH=logs\nBOT_SLUG=dokima-runtime\n' > /tmp/env.txt
>           fi
>           cat /tmp/env.txt >> "$GITHUB_ENV"

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "\"branch\"\]\|branch.default\|\['branch'\]" dokima --include=*.py | grep -v "^dokima/settings.py:110" | head -20
```

> dokima/agent_roles.py:348:            rec["branch"] = f"try/issue-{os.environ.get('N', '')}"
> dokima/settings.py:111:              "RECORDS_BRANCH": got["records"]["branch"], "BOT_SLUG": got["bot"]["slug"],

`12. Bash`
```
cd /home/runner/work/dokima/dokima; env -u TESTS_RUN_ONE python3 -m pytest -q -p no:cacheprovider tests/test_settings_autopilot.py tests/test_settings_merge.py tests/test_start.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed|AssertionError: 787" | head -40
```

> E       AssertionError: 787.1: autopilot did not merge into trunk, the settings' default branch: HTTP 404: Not Found
> E       AssertionError: 787.1: autopilot merged although GitHub has no trunk branch
> E       AssertionError: 787.2: autopilot did not merge into develop, GitHub's default branch: HTTP 404: Not Found
> E       AssertionError: 787.2: an empty default branch setting did not fall back to GitHub's develop: HTTP 404: Not Found
> E       AssertionError: 787.3: autopilot merged with ['--squash'], not --rebase as the settings say
> E       AssertionError: 787.3: merges used [('pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'), ('pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', '--admin')]
> E       AssertionError: 787.4: the gate waited 2700 s, not the 2 minutes the settings say
> E       AssertionError: 787.5: an issue carrying dokima-auto is not on autopilot
> E       AssertionError: 787.5: the sweep asked for ['repos/o/r/issues?labels=autopilot&state=all&per_page=100']
> E       AssertionError: 787.5: the board does not count an issue carrying dokima-auto
> E       AssertionError: 787.5: the board skips adding dokima-auto, so the card never moves
> E       AssertionError: 787.6: the issue now carries ['autopilot'], not dokima-auto
> E       AssertionError: 787.6: the board labelled the pull request with [('POST', 'repos/o/r/issues/60/labels', {'labels[]': 'autopilo

`13. Bash`
```
cd /home/runner/work/dokima/dokima; env -u TESTS_RUN_ONE python3 -m pytest -q -p no:cacheprovider tests/test_settings_merge.py tests/test_start.py 2>&1 | tail -3
```

> branch.default: 'main', not ''
> assert not ["branch.default: 'main', not ''"]
> 1 failed, 21 passed in 38.22s

`14. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner added two criteria for shipping the default branch setting empty.",
          "The planner added four tests for the empty default branch, for autopilot and for workflows.",
          "The planner changed the shipped defaults test to expect an empty default branch."],
  "decided": ["When GitHub gives no default branch, the run stops and says so."],
  "open": []},
 "verdict": "approve",
 "summary": "The owner's answer is carried: the default branch ships empty, and every new test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "`branch.default: main`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.1"},
  {"ask": "better: read repo default_branch", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.2"},
  {"ask": "`merge.method: squash`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.3"},
  {"ask": "`gate.checks_wait_min: 45`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.4"},
  {"ask": "autopilot: autopilot", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.5"},
  {"ask": "filed: filed-by-dokima", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.7"},
  {"ask": "a test where adding the label named in settings moves the board card", "source": "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232040687", "criterion": "787.5"},
  {"ask": "a test that turning autopilot off removes the settings' label", "source": "https://github.com/dokima-dev/dokima/issues/787#issuecomment-6232040687", "criterion": "787.6"},
  {"ask": "ship the default branch setting empty, not \"main\"", "source": "htt
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#787](https://github.com/dokima-dev/dokima/issues/787) (autopilot uses the repo's own branch, merge method and labels). The review is saved in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Your default-branch answer is in the plan.** Dokima will ship the default branch setting empty, and empty means Dokima asks GitHub for the repo's default branch. A repo that names a branch gets that one. That's two new criteria, 787.8 and 787.9.
- **Every new test fails today for the right reason.** I ran all 19. Each fails because the feature isn't built yet, not because of a crash or a bad setup.
- **The two changed tests keep what they proved.** The shipped-settings test now expects an empty default branch instead of `main`, as you asked. The fake GitHub used in older tests now also reports a default branch, which is what real GitHub does.
- **Every ask is covered.** I found 11 asks across the parent issue and your two comments here, and each maps to a criterion. Each criterion is one behavior.

The planner added one rule you didn't ask for: if GitHub returns no default branch, the run stops and says why. I checked the workflow, and when that settings step fails, the run does stop there. I didn't raise anything and had no open blockers to answer.

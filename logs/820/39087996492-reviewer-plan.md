# reviewer (plan) for #820

Run: https://github.com/dokima-dev/dokima/actions/runs/39087996492

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

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
> # Issue #820: In an adopter's repo the checks run inside a called workflow, so GitHub prefixes their names; the required check names will not match.
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 812, 816 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [816], "loop": []} -->
> In an adopter's repo, Dokima's checks carry their callers' names, so the audit must ask for those names.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/820#issuecomment-6244402155) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/785
> - https://github.com/dokima-dev/dokima/issues/786
> - https://github.com/dokima-dev/dokima/issues/812
> 
> 
> **User story:** An adopter's Setup issue asks main to require Dokima's checks under the exact names GitHub shows there.
> 
> <img src="https://raw.githubusercontent.com/dok

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; head -c 1500 open_issues.json; echo; cd /home/runner/work/dokima/dokima; cat tests/test_adopter_check_names.py; git show --stat HEAD; cat dokima/install/settings.yaml; cat dokima/install/dokima.yml; ls dokima/install
```

> {
>  "https://github.com/dokima-dev/dokima/issues/820": "In an adopter's repo the checks run inside a called workflow, so GitHub prefixes their names; the required check names will not match.\n\n**Evidence:** `dokima/defaults.yaml` gates.required names `all tests`; called jobs show as `caller / job`.\n\n**Verdict:** New\n\n**Open issues searched:** #786, #785, #744\n\nThe planner raised it and the reviewer confirmed it on #812 ([run](https://github.com/dokima-dev/dokima/actions/runs/39038968490))."
> }{"number": null}[
>  {
>   "number": 843,
>   "title": "Labeling several issues at once starts only some",
>   "summary": "Putting the autopilot label on several issues at once starts only some of them.",
>   "link": "https://github.com/dokima-dev/dokima/issues/843",
>   "filed_by_dokima": false
>  },
>  {
>   "number": 842,
>   "title": "The card says Needs you while autopilot waits for blockers",
>   "summary": "An issue on autopilot that waits for its blockers says \"Needs you: Say /work to build the plan\".",
>   "link": "https://github.com/dokima-dev/dokima/issues/842",
>   "filed_by_dokima": false
>  },
>  {
>   "number": 836,
>   "title": "A test's push to its temp repo fails at random on the runner",
>   "summary": "A test's setup push to its own temp bare repo fails at random on GitHub's runner, which fails the all tests check.",
>   "link": "https://github.com/dokima-dev/dokima/issues/836",
>   "filed_by_dokima": false
>  },
>  {
>   "number": 834,
>   "title": "Criteria sharing only a markdown file become separate stor

`3. Bash`
```
cd /home/runner/work/dokima/dokima; ls .github/workflows; grep -n "^  [a-z-]*:\|name:\|uses:" .github/workflows/entry.yml | head -60; grep -n "name:" .github/workflows/full-suite.yml .github/workflows/acceptance*.yml 2>/dev/null | head; grep -rn "all tests\|Acceptance criteria" dokima/defaults.yaml dokima/audit.py dokima/settings.py dokima/manifest.py | head -30
```

> acceptance-criteria.yml
> agent.yml
> assign.yml
> audit.yml
> autopilot.yml
> board.yml
> card.yml
> commands.yml
> entry.yml
> fix.yml
> full-suite.yml
> playthrough.yml
> reviews.yml
> testmon.yml
> uptodate.yml
> wiki.yml
> 1:name: entry
> 11:  agent:
> 13:    uses: ./.github/workflows/agent.yml
> 20:  commands:
> 24:    uses: ./.github/workflows/commands.yml
> 26:  reviews:
> 28:    uses: ./.github/workflows/reviews.yml
> 29:  assign:
> 31:    uses: ./.github/workflows/assign.yml
> 33:  autopilot:
> 35:    uses: ./.github/workflows/autopilot.yml
> 37:  board:
> 47:    uses: ./.github/workflows/board.yml
> 49:  card:
> 58:    uses: ./.github/workflows/card.yml
> 60:  acceptance-criteria:
> 65:    uses: ./.github/workflows/acceptance-criteria.yml
> 66:  full-suite:
> 72:    uses: ./.github/workflows/full-suite.yml
> 73:  queue-failed:
> 79:    uses: ./.github/workflows/autopilot.yml
> 81:  testmon:
> 83:    uses: ./.github/workflows/testmon.yml
> 84:  uptodate:
> 86:    uses: ./.github/workflows/uptodate.yml
> 88:  audit:
> 90:    uses: ./.github/workflows/audit.yml
> .github/workflows/acceptance-criteria.yml:1:name: Acceptance criteria
> .github/workflows/acceptance-criteria.yml:19:    name: list acceptance criteria
> .github/workflows/acceptance-criteria.yml:31:      - name: Dokima's code from Dokima's own repo
> .github/workflows/acceptance-criteria.yml:39:      - name: Every Dokima step runs Dokima's code
> .github/workflows/acceptance-criteria.yml:52:    name: ${{ matrix.name }}
> .github/workflows/acceptance-criteria.yml:70:      - name: Dokima's code from Doki

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 55,80p .github/workflows/entry.yml; sed -n 1,30p .github/workflows/acceptance-criteria.yml; sed -n 115,200p .github/workflows/acceptance-criteria.yml; grep -n "name:\|^  [a-z-]*:" .github/workflows/full-suite.yml | head; sed -n 30,80p dokima/manifest.py; grep -n "required\|manifest\|CHECKS" dokima/audit.py dokima/settings.py | head -30
```

> contains(fromJSON('["opened", "edited", "synchronize", "reopened", "closed", "labeled", "unlabeled", "ready_for_review", "converted_to_draft"]'), github.event.action)) ||
>       (github.event_name == 'workflow_run' &&
>        contains(fromJSON('["pull_request_target", "merge_group", "push", "pull_request_review", "pull_request_review_comment"]'), github.event.workflow_run.event))
>     uses: ./.github/workflows/card.yml
>     secrets: inherit
>   acceptance-criteria:
>     if: >-
>       github.event_name == 'merge_group' ||
>       (github.event_name == 'pull_request_target' &&
>        contains(fromJSON('["opened", "synchronize", "reopened", "ready_for_review"]'), github.event.action))
>     uses: ./.github/workflows/acceptance-criteria.yml
>   full-suite:
>     # Not on a push to main: the merge queue already ran every test on that exact merge (owner, 2026-10-17).
>     if: >-
>       github.event_name == 'merge_group' ||
>       (github.event_name == 'pull_request_target' &&
>        contains(fromJSON('["opened", "synchronize", "reopened", "ready_for_review"]'), github.event.action))
>     uses: ./.github/workflows/full-suite.yml
>   queue-failed:
>     # A failed merge queue run: put the pull request back once, then send it back to its worker (#830).
>     needs: [acceptance-criteria, full-suite]
>     if: >-
>       always() && github.event_name == 'merge_group' &&
>       (needs.full-suite.result == 'failure' || needs.acceptance-criteria.result == 'failure')
>     uses: ./.github/workflows/autopilot.yml
>     secret

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def branch_rules" -A15 dokima/manifest.py; grep -rn "gates" dokima/settings.py | head; sed -n 50,62p dokima/defaults.yaml; python -m pytest -q tests/test_adopter_check_names.py 2>&1 | grep -E "820\.|passed|failed|Error" | head -20
```

> 85:def branch_rules(got):
> 86-    """BRANCH_RULES with main requiring exactly the checks the merged settings GOT name."""
> 87-    required = [e.get("name") if isinstance(e, dict) else e for e in (got.get("gates") or {}).get("required") or []]
> 88-    return {branch: {**rule, "required_checks": required} if branch == "main" else rule
> 89-            for branch, rule in BRANCH_RULES.items()}
> 90-
> 91-
> 92-LEVEL = {"read": 1, "write": 2}
> 93-NONE = ""  # a call that needs no app permission
> 94-
> 95-# gh's own commands: (command, subcommand) -> (permission, level)
> 96-GH_COMMANDS = {
> 97-    **{("issue", s): ("issues", "read") for s in ("view", "list", "status")},
> 98-    **{("issue", s): ("issues", "write") for s in ("comment", "create", "edit", "close", "reopen", "delete", "lock",
> 99-                                                   "unlock", "pin", "unpin", "transfer")},
> 100-    **{("pr", s): ("pull_requests", "read") for s in ("view", "list", "status", "diff", "checks")},
> --
> 243:    def branch_rules(self, path, text):
> 244-        for m in BRANCH_RULE.finditer(text):
> 245-            branch = m.group(1) or m.group(2)
> 246-            if branch not in BRANCH_RULES:
> 247-                self.add(path, f"branch rule of {branch!r} is not in the manifest's branch rules")
> 248-
> 249-
> 250-# Python
> 251-
> 252-class Scope:
> 253-    """String names assigned once in a function or module, read by text()."""
> 254-
> 255-    def __init__(self, body, up=None):
> 256-        self.up, self.names, seen = up, {}, set()
> 

**Agent:** Tests fail for the right reason. Writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote two criteria and two tests, one per check Dokima requires."],
  "decided": ["An adopter's audit wants both checks under their full caller names."],
  "open": ["Asks the owner whether checks carry both caller names.", "Asks the owner whether the card and branch updates wait for their own issues."]},
 "verdict": "approve",
 "summary": "The plan covers both required checks, and each test fails today because the audit wants the plain names.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "GitHub prefixes their names; the required check names will not match", "source": "https://github.com/dokima-dev/dokima/issues/820", "criterion": "820.1"},
  {"ask": "the required check names will not match", "source": "https://github.com/dokima-dev/dokima/issues/820", "criterion": "820.2"}
 ],
 "behaviors": [
  {"criterion": "820.1", "one_behavior": true, "why": "One check, one wanted name, in an adopter's repo."},
  {"criterion": "820.2", "one_behavior": true, "why": "One check, one wanted name, in an adopter's repo."}
 ],
 "edge_cases": [
  {"criterion": "820.1", "cut": [], "missing": []},
  {"criterion": "820.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_adopter_check_names.py::test_adopter_audit_wants_all_tests_as_github_shows_it", "only_its_behavior": true, "why": "Runs the real audit; checks only lines naming all tests, both ways."},
  {"test": "tests/test_adopter_check_names.py::test_adopter_audit_wants_acceptance_criteria_as_github_shows_it", "only_its_behavior": true, "why": "Runs the real audit; checks only lines naming Acceptance criteria, both ways."}
 ],
 "size": "ok",
 "boxes": {
  "dropped": "none", "added": "none", "superseded": "none", "conflicts": "none",
  "edges": {"820.1": "covered", "820.2": "covered"},
  "poor_tests": "none"}
}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#820](https://github.com/dokima-dev/dokima/issues/820) (adopter repos need the full check names). The hand-back passes both checks.

- **What the plan asks for:** In an adopter's repo, the audit wants `dokima / full-suite / all tests` and `dokima / acceptance-criteria / Acceptance criteria`. Today it wants the plain names, `all tests` and `Acceptance criteria`. There is one criterion and one test per check.
- **Tests fail today for the right reason:** I ran both. Each fails because the audit flags the full names as checks Dokima doesn't declare and asks for the plain names. Neither fails from a crash or a bad path.
- **The tests can't be passed by faking it:** each runs the real audit command against a copy of the settings file the install ships. Each checks both ways: the full name passes, and the plain name gets a line saying main does not require the full name.
- **Your two questions are still open.** I didn't answer them for you:
  - Does GitHub put both caller names in front of each check? The workflow chain suggests so, but nothing you've written settles it.
  - Should the card and branch updates, which still look for the plain names, wait for [#785](https://github.com/dokima-dev/dokima/issues/785) and [#786](https://github.com/dokima-dev/dokima/issues/786) (moving those names into settings)? This repo's rules forbid touching the card code unless the issue asks, but they say nothing about the branch updates.
- **One thing for the builder:** settings merge the required checks by name, so the defaults add the plain names back. Just adding the full names to the shipped settings file won't make the tests pass. The plan already lists the settings code in its files.

The review is in `/tmp/dokima-out/review.json`.

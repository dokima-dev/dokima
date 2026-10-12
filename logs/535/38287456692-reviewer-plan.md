# reviewer (plan) for #535

Run: https://github.com/dokima-dev/dokima/actions/runs/38287456692

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #535: Agents run only the tests their change can affect (testmon); the merge gate still runs every test
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Code reviews run only the tests a change can affect, while the merge gate keeps running every test.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/148
> - https://github.com/dokima-dev/dokima/issues/341
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:**
> 
> <!-- dokima-folded -->
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> In Reza's words: "let's just have testmon for agents isn't that less conflict prone with xdist? their checks are pretty quick anyways. start the testmon please."
> 
> Agents' machines run the whole suite before each code review, though the merge gate already runs every test on every core (#521).
> 
> Done when
> - An agent's machine runs only the tests its change can affect, chosen by pytest-testmon from a baseline recorded on main.
> - With no usable baseline, the agent's machine runs every test, and its record says so.
> - The merge gate still runs every test, in parallel, unchanged.
> 
> 
> </details>
> 
> 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "pytest\|STAGE\|tests.txt\|tests.xml" .github/workflows/agent.yml | head -50; ls .github/workflows; grep -n "pytest\|-n auto" .github/workflows/full-suite.yml; grep -n "def test_full_suite_runs_every_test_on_every_pull_request" -A30 tests/test_checks.py
```

> 52:      STAGE: ${{ (inputs.role || github.event.client_payload.role) == 'reviewer' && (inputs.stage || github.event.client_payload.stage) || '' }}
> 111:          WHERE=$N; if [ -n "$PR" ] && { [ "$ROLE" = worker ] || [ "$STAGE" = pr ]; }; then WHERE=$PR; fi
> 112:          python3 -m dokima.agent card "$ROLE" "$STAGE" queued > /tmp/card.md
> 134:          python3 -m dokima.agent card "$ROLE" "$STAGE" setting-up > /tmp/card.md
> 155:          elif [ "$ROLE" = planner ] || [ "$STAGE" = plan ]; then
> 167:          LOG="logs/$N/${{ github.run_id }}-$ROLE${STAGE:+-$STAGE}.md"
> 175:          python3 -m dokima.agent pack "$N" "$ROLE" "$STAGE" "$PACK" 2> /tmp/pack-err.txt || {
> 182:          if [ "$STAGE" = pr ]; then git diff origin/main...HEAD > "$PACK/diff.patch"; fi
> 184:      - name: Install pytest and Claude Code
> 187:          { pip install pytest pytest-xdist && npm install -g @anthropic-ai/claude-code; } 2>&1 | tee /tmp/install.txt \
> 188:            || { echo "The step 'Install pytest and Claude Code' failed: $(tail -3 /tmp/install.txt | paste -sd' ')" > /tmp/why.txt; exit 1; }
> 190:        if: env.STAGE == 'pr'
> 192:          PYTHONPATH= PYTHONSAFEPATH= python3 -m pytest -q -rA --junitxml="$PACK/tests.xml" > "$PACK/tests.txt" 2>&1 || true
> 193:          tail -5 "$PACK/tests.txt"
> 196:          python3 -m dokima.agent check-pack "$ROLE" "$STAGE" "$PACK" > /tmp/pack-check.txt \
> 215:          python3 -m dokima.agent card "$ROLE" "$STAGE" working > /tmp/card.md
> 226:          case "$ROLE$STAGE

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "pytest" dokima/roles/ | head; grep -n "S1\|story" dokima/agent.py | grep -i "asks\|behavior" | head
```

> dokima/roles/planner.md:102:Current runner (the only one Dokima supports today): python3 -m pytest, tests in tests/, and each test names its criterion with
> 1293:        return ['size is empty: write "ok" if every story holds 1 to 3 criteria, each one behavior, in as few stories as '

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner proposed a split into two stories, with four criteria in all."],
  "decided": ["Story one: testmon picks a code review's tests, every test without a baseline, merge gate unchanged.", "Story two: the record says when every test ran; it waits on story one."],
  "open": []},
 "verdict": "approve",
 "summary": "The split carries all three asks, each criterion is one behavior, and two stories fit the size rule.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "An agent's machine runs only the tests its change can affect, chosen by pytest-testmon from a baseline recorded on main.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "S1.1"},
  {"ask": "With no usable baseline, the agent's machine runs every test", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "S1.2"},
  {"ask": "and its record says so.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "S2.1"},
  {"ask": "The merge gate still runs every test, in parallel, unchanged.", "source": "https://github.com/dokima-dev/dokima/issues/535", "criterion": "S1.3"}
 ],
 "behaviors": [
  {"criterion": "S1.1", "one_behavior": true, "why": "One result: a code review runs only the affected tests."},
  {"criterion": "S1.2", "one_behavior": true, "why": "One case, no baseline, one result: every test runs."},
  {"criterion": "S1.3", "one_behavior": true, "why": "One result: the merge gate runs every test in parallel."},
  {"criterion": "S2.1", "one_behavior": true, "why": "One result: the record names the full run and its reason."}
 ],
 "tests": [],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 535 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Story one: testmon picks a code review.s tests, every test without a baseline, merge gate unchanged./Story one: testmon picks review tests, every test without a baseline, merge gate unchanged./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 535 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for issue [#535](https://github.com/dokima-dev/dokima/issues/535) (testmon picks the tests for agents' runs). The review is written to `/tmp/dokima-out/review.json` and passes both checks.

The planner proposed splitting it into two stories with four criteria:
- **Story 1:**
  - A code review runs only the tests its change can affect, picked by testmon from a baseline recorded on main.
  - With no usable baseline, it runs every test.
  - The merge gate still runs every test in parallel, unchanged.
- **Story 2:** when every test ran because no baseline was usable, the code review's record says so. It waits on story 1.

Why it passes:
- **Every ask is covered.** All three of the owner's points map to a criterion, and none is marked missing.
- **One behavior each.** No criterion bundles two cases or two results.
- **Size is right.** Four criteria make two stories.
- **"Agent's machine" means the code review.** That is the only place code runs the whole suite on an agent's machine today, in `.github/workflows/agent.yml`. Workers run tests through their prompt, not a fixed step.

Two things to know:
- **No tests yet.** A split doesn't name tests. Each story writes and gets reviewed on its own tests when it is planned.
- **Story 1 changes workflow files.** It adds a new workflow on main and edits `agent.yml`. So even on autopilot, its pull request will stop for your approval before it merges.

I raised no blockers or questions.

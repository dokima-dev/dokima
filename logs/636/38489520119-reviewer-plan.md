# reviewer (plan) for #636

Run: https://github.com/dokima-dev/dokima/actions/runs/38489520119

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/plan.json; cat /tmp/pack/open_blockers.json
```

> # Issue #636: The agent code splits into files by job
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [637, 638], "loop": []} -->
> The big agent file splits into one file per job, with nothing changing in how it works.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/640 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/640/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/637
> - https://github.com/dokima-dev/dokima/issues/638
> 
> 
> **User story:** Issues that change different jobs of the agent code change different files, so they no longer queue.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The agent code lives in one file per job, moved as it is, with no change in behavior.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/814b7dd3cf696f102260bcf67f686c42df971c62/tests/test_agent_split.py#

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -8; git show 6e93f88 --stat; git show 6e93f88 -- tests/test_manifest.py | head -80; python3 -c "import json;d=json.load(open('/tmp/pack/in/02-reviewer-plan.json'));print(json.dumps(d.get('handback',d),indent=1)[:5000])"
```

> 6e93f88 planner for #636 (run 38488284094)
> 814b7dd Merge branch 'main' into try/issue-636
> a582346 The command previews its drawing on the gallery repo (#635)
> c0202b8 worker for #636 (run 38485714674)
> 42d65bb Merge remote-tracking branch 'origin/main' into try/issue-636
> fd524c1 planner for #636 (run 38484254280)
> 9f35cbc The reviewer records its search and verdict (#634)
> 61faa9e One command draws Dokima's posts from any branch (#630)
> commit 6e93f88597f7bda7af49043c6f8830ebae307e3f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:19:14 2026 +0000
> 
>     planner for #636 (run 38488284094)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_manifest.py | 12 ++++++------
>  1 file changed, 6 insertions(+), 6 deletions(-)
> commit 6e93f88597f7bda7af49043c6f8830ebae307e3f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:19:14 2026 +0000
> 
>     planner for #636 (run 38488284094)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_manifest.py b/tests/test_manifest.py
> index 878dd06..684c0ac 100644
> --- a/tests/test_manifest.py
> +++ b/tests/test_manifest.py
> @@ -399,12 +399,12 @@ def test_the_guard_passes_settings_the_manifest_declares(record_property, tmp_pa
>      assert m.undeclared(ROOT) == [], f"282.3: code or workflows in this repo rely on settings the mani

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_manifest.py tests/test_agent_split.py 2>&1 | tail -5; grep -n "statuses\|/merges\|dispatches" dokima/agent*.py | head; sed -n 410,425p tests/test_manifest.py; sed -n 610,625p tests/test_manifest.py
```

> ...............................................................          [100%]
> 63 passed in 3.38s
> dokima/agent_autopilot.py:367:    agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next", "-f", "client_payload[role]=planner",
> dokima/agent_autopilot.py:591:    Check runs and commit statuses count alike; a check the rule does not require judges nothing (#561). A
> dokima/agent_autopilot.py:612:        statuses = [s for p in pages(agent_github.gh("api", f"repos/{repo}/commits/{sha}/status?per_page=100", "--paginate"))
> dokima/agent_autopilot.py:613:                    for s in p.get("statuses") or [] if s.get("context") in required]
> dokima/agent_autopilot.py:615:        red += [f"{s.get('context')} ({s.get('state')})" for s in statuses if s.get("state") not in ("success", "pending")]
> dokima/agent_autopilot.py:617:        running += [s.get("context") for s in statuses if s.get("state") == "pending"]
> dokima/agent_autopilot.py:620:        missing = sorted(required - ran - {s.get("context") for s in statuses})
> dokima/agent_roles.py:567:                agent_github.gh("api", "-X", "POST", f"repos/{repo}/dispatches", "-f", "event_type=dokima-next",
>     monkeypatch.delitem(m.LABELS, label)
>     lines = m.undeclared(ROOT)
>     assert reported(lines, label, path), \
>         f"282.3: with {label} left out of the manifest, the guard did not name it and {path}: {lines}"
> 
> 
> def test_the_guard_catches_a_check_taken_out_of_the_manifest(record_property, monke

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python3 -m pytest -q -x -n auto 2>&1 | tail -5 || timeout 900 python3 -m pytest -q 2>&1 | tail -5
```

> ........................................................................ [ 81%]
> ........................................................................ [ 88%]
> ........................................................................ [ 94%]
> ...............................................................          [100%]
> 1143 passed in 169.77s (0:02:49)

`5. Bash`
```
cd /tmp && rm -rf mainwt && git -C /home/runner/work/dokima/dokima worktree add -q /tmp/mainwt origin/main 2>&1|tail -1; cp /home/runner/work/dokima/dokima/tests/test_agent_split.py /tmp/mainwt/tests/; cd /tmp/mainwt && python3 -m pytest -q tests/test_agent_split.py 2>&1 | grep -E "^E .*636|passed|failed" | head; cd /tmp; git -C /home/runner/work/dokima/dokima worktree remove --force /tmp/mainwt
```

> E               AssertionError: 636.1: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> E               AssertionError: 636.2: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> E               AssertionError: 636.3: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> 3 failed in 18.50s
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Writing my review now: the fix checks out and the full suite passes.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Changed three guard test cases to expect the autopilot job file instead of the agent file.",
   "Kept the three criteria and their tests as before."
  ],
  "decided": [
   "The guard now names the job file that holds the moved calls."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "The fix to the three guard tests holds, and the whole suite passes on the branch.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "agent.py is split into modules by job (autopilot and merging, records, Next lines, checks, GitHub helpers, roles), a pure move with no behavior change", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.1"},
  {"ask": "`agent` keeps re-exporting every name so its 146 importers keep working.", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.2"},
  {"ask": "GitHub calls go through one helper module that tests patch in one place", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.3"}
 ],
 "behaviors": [
  {"criterion": "636.1", "one_behavior": true, "why": "Code moves into job files unchanged, and the command answers as before."},
  {"criterion": "636.2", "one_behavior": true, "why": "Every old name still loads from the agent module."},
  {"criterion": "636.3", "one_behavior": true, "why": "Faking one helper fakes every GitHub call of the agent code."}
 ],
 "edge_cases": [
  {"criterion": "636.1", "cut": [], "missing": []},
  {"criterion": "636.2", "cut": [], "missing": []},
  {"criterion": "636.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_agent_split.py::test_agent_code_lives_in_job_files", "only_its_behavior": true, "why": "On main it fails because the job files are missing; it passes on the branch."},
  {"test": "tests/test_agent_split.py::test_every_old_name_loads_from_agent", "only_its_behavior": true, "why": "Fails on any missi
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Changed three guard test cases to expect the autopilot job file instead of the agent file./Changed three guard test cases to expect the autopilot job file, not the agent file./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 636 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the re-plan for [#636](https://github.com/dokima-dev/dokima/issues/636) (splitting the big agent file into one file per job), and nothing is open for you.

**What was blocking:** the code review on [#640](https://github.com/dokima-dev/dokima/pull/640) (the pull request that does the split) stopped the work because three test cases still expected the moved code to live in the old agent file. The planner changed them to expect the new autopilot file instead, which is where that code now lives.

**What I checked on the branch:**
- Those three cases and the rest of their test file pass: 60 tests.
- The three tests for this issue pass on the branch. On main they fail for the right reason: the new files don't exist there yet.
- The whole suite passes: 1143 tests.

**The plan itself:**
- Each of the three things you asked for has one criterion and one test.
- No ask is missing.
- No edge case needs adding or cutting.

My review is saved in `/tmp/dokima-out/review.json` and passes both hand-back checks.

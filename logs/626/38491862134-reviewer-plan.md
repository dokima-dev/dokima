# reviewer (plan) for #626

Run: https://github.com/dokima-dev/dokima/actions/runs/38491862134

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 92
> drwxr-xr-x  3 runner runner  4096 Oct 14 00:44 .
> drwxrwxrwt 18 root   root    4096 Oct 14 00:45 ..
> drwxr-xr-x  2 runner runner  4096 Oct 14 00:44 in
> -rw-r--r--  1 runner runner 18960 Oct 14 00:44 issue.md
> -rw-r--r--  1 runner runner     2 Oct 14 00:44 open_blockers.json
> -rw-r--r--  1 runner runner 47252 Oct 14 00:44 open_issues.json
> -rw-r--r--  1 runner runner    15 Oct 14 00:44 parent.json
> -rw-r--r--  1 runner runner  3368 Oct 14 00:44 plan.json
> 
> in:
> total 44
> drwxr-xr-x 2 runner runner 4096 Oct 14 00:44 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 00:44 ..
> -rw-r--r-- 1 runner runner 3436 Oct 14 00:44 01-planner.json
> -rw-r--r-- 1 runner runner 4712 Oct 14 00:44 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3965 Oct 14 00:44 03-planner.json
> -rw-r--r-- 1 runner runner 3834 Oct 14 00:44 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 2023 Oct 14 00:44 05-worker.json
> -rw-r--r-- 1 runner runner 2040 Oct 14 00:44 06-worker.json
> -rw-r--r-- 1 runner runner 4097 Oct 14 00:44 07-planner.json
> # Issue #626: The command shows what changed, and real checks run nightly
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 625, 627 -->
> <!-- dokima-blocking: {"blocked_by": [624, 625], "blocks": [], "loop": []} -->
> Our drawing tool shows only the lines a branch changes, and its real GitHub checks run at night.
> 
> **Work** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: 

`2. Bash`
```
cd /tmp/pack; cat in/04-reviewer-plan.json in/06-worker.json in/07-planner.json parent.json; cd /home/runner/work/dokima/dokima; git show --stat HEAD; ls tests/nightly 2>&1; ls tools
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38488656862",
>  "commit_before": "b7f5652fa81645a856a55ba5892427e089d0daa4",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 34509,
>   "turns": 7,
>   "cost_usd": 0.44535020000000003,
>   "tokens_in": 329284,
>   "tokens_out": 2959
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/626/38488656862-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38488656862",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner made the nightly test fail unless a check calls the card gallery repo.",
>     "The planner added a test: a missing branch fails, names the branch, shows no crash."
>    ],
>    "decided": [],
>    "open": []
>   },
>   "verdict": "approve",
>   "summary": "Both blockers are fixed; every test fails today because the feature is missing.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "shows which lines differ from today's card",
>     "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924",
>     "criterion": "626.1"
>    },
>    {
>     "ask": "Anything that posts to or reads from real GitHub (the card-gallery previews) runs nightly, not in the suite that runs on every pull request.",
>     "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156300577",
>     "criterion": "626.2"
>    },
>    {
>     "ask": "never shipped with Dokima and never a Dokima command or feature",
>     "source"

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/conftest.py tests/test_visuals_diff.py; cat tests/nightly/test_visuals_gallery.py; ls nightly 2>&1; cat pytest.ini setup.cfg pyproject.toml 2>/dev/null | head -40
```

> commit 67592853db2c5cc243a56c78ec0750dcd9b618bb
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 00:44:08 2026 +0000
> 
>     planner for #626 (run 38490115385)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/conftest.py b/tests/conftest.py
> index 684eeca..270952a 100644
> --- a/tests/conftest.py
> +++ b/tests/conftest.py
> @@ -10,3 +10,16 @@ for k in ("STAGE", "ROLE", "N", "PACK", "OUT", "CARD_ID", "GITHUB_REPOSITORY", "
>      os.environ.pop(k, None)
>  os.environ["PYTHONPATH"] = ROOT
>  sys.path[:] = [ROOT] + [x for x in sys.path if os.path.abspath(x or ".") != "/tmp/runtime"]
> +
> +
> +def pytest_ignore_collect(collection_path, config):
> +    """Leave out the real GitHub checks in tests/nightly unless a run names that folder (#626).
> +
> +    They post to and read from real GitHub, so only the nightly workflow runs them, by naming tests/nightly; the all
> +    tests check (`pytest tests`) and a bare `pytest` from the root never collect them."""
> +    nightly = os.path.join(ROOT, "tests", "nightly")
> +    path = str(collection_path)
> +    if path != nightly and not path.startswith(nightly + os.sep):
> +        return None
> +    asked = any(os.path.abspath(str(a).split("::")[0]).startswith(nightly) for a in config.args)
> +    return None if asked else True
> diff --git a/tests/test_visuals_diff.py b/tests/test_visuals_diff.py
> index bd7df73..3ffe595 100644
> --- a/tests/test_visuals_diff.py
> +

`4. Bash`
```
cd /home/runner/work/dokima/dokima; head -12 tests/conftest.py; ls tools; git log --oneline -3 -- tools; timeout 600 python -m pytest -q tests/test_visuals_diff.py 2>&1 | tail -30
```

> """Every test judges this checkout's code, never the machine it runs on (#449, #385)."""
> import os
> import sys
> 
> 
> # Tests judge this checkout's code on any machine (#449, #385). The agent's machine points Python at a runtime
> # copy of Dokima and sets its own run's settings; none of that may reach a test or a subprocess it starts.
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> for k in ("STAGE", "ROLE", "N", "PACK", "OUT", "CARD_ID", "GITHUB_REPOSITORY", "PYTHONSAFEPATH"):
>     os.environ.pop(k, None)
> os.environ["PYTHONPATH"] = ROOT
> sys.path[:] = [ROOT] + [x for x in sys.path if os.path.abspath(x or ".") != "/tmp/runtime"]
> visuals.py
> a582346 The command previews its drawing on the gallery repo (#635)
> 61faa9e One command draws Dokima's posts from any branch (#630)
> tests/test_visuals_diff.py:167: Failed
> =========================== short test summary info ============================
> FAILED tests/test_visuals_diff.py::test_diff_shows_changed_lines - AssertionError: 626.1: comparing #7 from visual-test with main exited 2:
>   
>   usage: tools/visuals.py [-h] {draw,preview} ...
>   tools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)
>   
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python', 'tools/visuals.py', 'diff', '7', '--branc...] {draw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'diff' (choose from draw, preview)\n").returncode
> FAILED tests/test_

`5. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/sim; git worktree add -q /tmp/sim HEAD 2>&1; cd /tmp/sim; cat > .github/workflows/visuals-nightly.yml <<'EOF'
name: visuals nightly
on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:
jobs:
  real:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Real checks
        env:
          GH_TOKEN: ${{ secrets.GALLERY_TOKEN }}
        run: python -m pytest -q tests/nightly
EOF
grep -n "suite_paths\|def runs" -A8 tests/test_visuals_diff.py | head -40; timeout 900 python -m pytest -q tests/test_visuals_diff.py -k nightly 2>&1 | tail -15; python -m pytest --collect-only -q 2>/dev/null | grep -c nightly; python -m pytest --collect-only -q tests/nightly 2>&1 | tail -3
```

> 171:def runs(wf):
> 172-    """Every step of every job: (its run text, its env)."""
> 173-    out = []
> 174-    for job in (wf.get("jobs") or {}).values():
> 175-        for step in job.get("steps") or []:
> 176-            out.append((step.get("run") or "", step.get("env") or {}))
> 177-    return out
> 178-
> 179-
> 180:def suite_paths():
> 181-    """The paths the all tests check hands pytest, read from full-suite.yml."""
> 182-    wf = ts.load_yaml(open(os.path.join(WORKFLOWS, "full-suite.yml")).read())
> 183-    paths = []
> 184-    for text, _ in runs(wf):
> 185-        for line in text.splitlines():
> 186-            words = line.split()
> 187-            if "pytest" in words:
> 188-                after = words[words.index("pytest") + 1:]
> --
> 220:    for name, paths in (("the all tests check", suite_paths()), ("a bare pytest from the root", [])):
> 221-        r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", *paths],
> 222-                           cwd=ROOT, capture_output=True, text=True, timeout=300)
> 223-        collected = [line for line in r.stdout.splitlines() if line.startswith("tests/nightly/")]
> 224-        assert not collected, f"626.2: {name} collects real GitHub checks, so they run on every pull request: {collected[:3]}"
> 225-
> 226-
> 227-def test_nightly_checks_fail_when_github_refuses(tmp_path, record_property):
> 228-    """The nightly checks really call GitHub, and fail saying why when it refuses.
> ..                                             

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "approve\b\|\"approve\"\|'approve'" dokima/agent.py dokima/raises.py 2>/dev/null | head -20; grep -rn "issuecomment" /tmp/pack/issue.md | head; grep -n "Not a priority" -B3 /tmp/pack/issue.md
```

> dokima/agent.py:21:VERDICTS = {"approve", "block", "escalate"}
> dokima/agent.py:113:    return bool(reviews) and reviews[-1]["handback"].get("verdict") == "approve"
> dokima/agent.py:121:                and (r.get("handback") or {}).get("verdict") == "approve":
> dokima/agent.py:138:            return [] if r["handback"].get("verdict") == "approve" else r["handback"].get("blockers", [])
> dokima/agent.py:192:        if r["role"] == "reviewer" and newest.get(stage) == i and h.get("verdict") != "approve":
> dokima/agent.py:785:        return {"approve": f"{name} passed {what}.",
> dokima/agent.py:976:        return {"approve": f"The reviewer passed {what}.",
> dokima/agent.py:1325:        bad.append("verdict must be approve, block or escalate")
> dokima/agent.py:1335:    if r.get("verdict") == "approve" and blocks:
> dokima/agent.py:1336:        bad.append("an approve raises no blocker")
> dokima/agent.py:1352:    if wide and r.get("verdict") == "approve":
> dokima/agent.py:1353:        bad.append(", ".join("`" + t + "`" for t in wide) + f" check more than their criterion's behavior, so the verdict cannot be approve")
> dokima/agent.py:1377:    if size.lower() != "ok" and r.get("verdict") == "approve":
> dokima/agent.py:1378:        return [f"size says the plan breaks the size rule ({size}), so the verdict cannot be approve"]
> dokima/agent.py:1404:    they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an approve keeps every ask."""
> dokima/agent.py:1417:    if r.get("verdict"

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/sim; mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner committed the real GitHub checks in a folder only the nightly run collects.",
   "The planner made the refusal test run the nightly workflow's own command."
  ],
  "decided": [
   "The planner kept the real checks out of every pull request's run by default."
  ],
  "open": [
   "The owner said this issue is not a priority now."
  ]
 },
 "verdict": "approve",
 "summary": "The plan is sound and its tests fail today for the right reason; the owner decides whether to build it now.",
 "raises": [
  {
   "kind": "question",
   "to": "owner",
   "label": "Doubt: not now",
   "text": "You said this is not a priority now. Should the worker wait until you say /work? The review assumes it waits.",
   "evidence": "Owner's comment on #626, 2026-10-14 00:32: \"Not a priority now\"."
  }
 ],
 "answers": [],
 "asks": [
  {
   "ask": "shows which lines differ from today's card",
   "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924",
   "criterion": "626.1"
  },
  {
   "ask": "Anything that posts to or reads from real GitHub (the card-gallery previews) runs nightly, not in the suite that runs on every pull request.",
   "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156300577",
   "criterion": "626.2"
  },
  {
   "ask": "never shipped with Dokima and never a Dokima command or feature",
   "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924",
   "criterion": "626.3"
  },
  {
   "ask": "Add it to the plan.",
   "source": "https://github.com/dokima-dev/dokima/issues/626",
   "criterion": "626.2"
  }
 ],
 "behaviors": [
  {"criterion": "626.1", "one_behavior": true, "why": "One command result: the lines that differ from main's drawing."},
  {"criterion": "626.2", "one_behavior": true, "why": "One rule: where the
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> raise 1's text holds 21 words, over its cap of 20: cut 1, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The plan is sound and its tests fail today for the right reason; the owner decides whether to build it now./The plan is sound and its tests fail today for the right reason; the owner decides when to build it./; s/You said this is not a priority now. Should the worker wait until you say \/work? The review assumes it waits./You said this is not a priority now. Should the worker wait for your \/work? The review assumes it waits./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 626 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for issue [#626](https://github.com/dokima-dev/dokima/issues/626) (line diff and nightly real checks). I also raised one question for you, so the worker will not start on its own.

**The plan holds up:**
- **Fix carried out:** you asked the planner to add the nightly test file to the plan. The planner committed it in `tests/nightly/`, which is the file the worker could not write itself.
- **Kept off pull requests:** a change to `tests/conftest.py` stops the all-tests check and a plain `pytest` from picking up the real GitHub checks. Only a run that names `tests/nightly` picks them up.
- **Tests fail today, for the right reason:** all 7 of the plan's tests fail because the feature is missing (no `diff` command, no nightly workflow), not because of a crash.
- **Tests can pass:** with a sample nightly workflow added in a throwaway copy, both nightly tests passed. A plain `pytest` did not pick up any nightly check.
- **Nothing dropped:** every ask is matched to a criterion.

**Question for you:** after this plan was written, you commented "Not a priority now". I asked whether the worker should wait for your `/work`. The review assumes it waits, so the issue now stops for you. Say `/work` when you want it built.

The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

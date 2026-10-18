# reviewer (plan) for #857

Run: https://github.com/dokima-dev/dokima/actions/runs/39103909518

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #857: Pull requests with no plan pass unless Dokima opened them
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> People and Dependabot can merge without a Dokima plan; Dokima's own pull requests still need one.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/744
> 
> 
> **User story:** People and Dependabot merge pull requests without a Dokima plan, while Dokima's own stay held to theirs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When a person opens a pull request with no approved plan, the Acceptance criteria check passes.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-857/tests/test_unplanned_prs.py#L82"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: A person's pull request with no approved plan passes the Acceptance criteria check.*
>   <details><summary><picture><img src="https://r

`2. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000]);print(json.dumps(d.get('handback',{}).get('raises'),indent=1))"; git show --stat HEAD; git show HEAD -- tests/test_manual_fix_check.py tests/test_test_settings.py
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39102757741",
>  "commit_before": "ccbebe20951336dbdfb7da7800bf77e892c34308",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 1122613,
>   "turns": 34,
>   "cost_usd": 1.3836914,
>   "tokens_in": 2090844,
>   "tokens_out": 19996
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/857/39102757741-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39102757741",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/857#issuecomment-6246376786"
> }
> null
> commit 0ac83904b54c6081d3e5d03f9e559df3ddb99e50
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 06:23:57 2026 +0000
> 
>     planner for #857 (run 39102757741)
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> 
>  tests/test_manual_fix_check.py |  10 +--
>  tests/test_test_settings.py    |  13 ++--
>  tests/test_unplanned_prs.py    | 143 +++++++++++++++++++++++++++++++++++++++++
>  3 files changed, 156 insertions(+), 10 deletions(-)
> commit 0ac83904b54c6081d3e5d03f9e559df3ddb99e50
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 06:23:57 2026 +0000
> 
>     planner for #857 (run 39102757741)
>     
>     Co-authored-by: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> 
> diff --git a/tests/

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_unplanned_prs.py; python3 -m pytest -q tests/test_unplanned_prs.py tests/test_manual_fix_check.py tests/test_test_settings.py 2>&1 | tail -30
```

> """Pull requests with no approved plan pass unless Dokima opened them (#857, from #744).
> 
> The required Acceptance criteria check used to fail every pull request without an approved Dokima plan, so a person's
> or Dependabot's pull request could never merge. The `merge.unplanned_prs` setting, `allow` by default, lets them
> through; only Dokima's own pull requests are held to the plan, and any other value keeps today's failing check.
> 
> Each test runs the real command the Acceptance criteria workflow runs, `python3 -m dokima.checks matrix`, from a temp
> git repo (with or without its own settings file) and GitHub faked by a stub `gh`: the pull request changes
> `app/main.py`, so the text-only shortcut never applies, and issue #77, when named, has no plan. It then runs that
> workflow's own "Run this criterion's tests" step for every row it got, with a passing fake `pytest` on PATH, and its
> "gate" step. The check passes only when every step does. Nothing here touches the network.
> """
> import json
> import os
> import subprocess
> import sys
> 
> from test_test_settings import make_repo
> from test_text_only import ROOT, STUB_GH, step_script
> 
> PR = 902
> PERSON = "octocat"
> DEPENDABOT = "dependabot[bot]"
> DOKIMA = "dokima-runtime[bot]"
> 
> 
> def run_step(tmp_path, name, env):
>     """Run one Acceptance criteria workflow step with a passing fake pytest; return (exit code, output)."""
>     bin_dir = tmp_path / "stepbin"
>     bin_dir.mkdir(exist_ok=True)
>     fake = bin_dir / "pytest"
>     fake.write_text("#!/bin/sh\nex

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "step_script" -A25 tests/test_text_only.py | head -50; grep -rn "manual-fix\|text-only" .github/workflows/*.yml | head; grep -n "unplanned\|merge:" -A5 dokima/defaults.yaml | head -30
```

> 77:def step_script(name):
> 78-    """The shell one Acceptance criteria workflow step runs, found by step name or job key."""
> 79-    lines = open(WORKFLOW).read().splitlines()
> 80-    start = next(i for i, l in enumerate(lines) if l.strip() in (f"- name: {name}", f"{name}:"))
> 81-    run = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
> 82-    indent = None
> 83-    body = []
> 84-    for line in lines[run + 1:]:
> 85-        if line.strip() == "":
> 86-            body.append("")
> 87-            continue
> 88-        here = len(line) - len(line.lstrip())
> 89-        if indent is None:
> 90-            indent = here
> 91-        if here < indent:
> 92-            break
> 93-        body.append(line[indent:])
> 94-    return "\n".join(body) + "\n"
> 95-
> 96-
> 97-def run_step(tmp_path, name, env):
> 98-    """Run a workflow step's shell with bash and a fake `pytest` that logs being run.
> 99-
> 100-    Returns (exit code, output, whether pytest ran)."""
> 101-    bin_dir = tmp_path / "stepbin"
> 102-    bin_dir.mkdir(exist_ok=True)
> --
> 107:    p = subprocess.run(["bash", "-e", "-c", step_script(name)], cwd=tmp_path, capture_output=True, text=True,
> 108-                       timeout=30, env={**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", **env})
> 109-    return p.returncode, p.stdout + p.stderr, marker.exists()
> 110-
> 111-
> 112-def is_shortcut(rows):
> 113-    """True when the check list is exactly the one text-only check, which runs no tests."""
> 114-    return rows is not None 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 60,200p .github/workflows/acceptance-criteria.yml; grep -n "No approved plan\|def build_matrix" dokima/checks.py
```

> with:
>           ref: ${{ github.event.merge_group.base_ref }}
>           persist-credentials: false
>       - uses: actions/checkout@v5
>         with:
>           ref: ${{ github.event.pull_request.head.sha || github.event.merge_group.head_sha }}
>           path: pr
>           persist-credentials: false
>       # Dokima's code from Dokima's own repo, at this shared workflow's commit, never the repo's own copy (#812). Run
>       # directly, Dokima's own repo names main: in its merge queue that commit is the queued one (#388).
>       - name: Dokima's code from Dokima's own repo
>         uses: actions/checkout@v5
>         with:
>           repository: dokima-dev/dokima
>           ref: ${{ job.workflow_sha == github.workflow_sha && 'main' || job.workflow_sha }}
>           path: .dokima-code
>           sparse-checkout: dokima
>           persist-credentials: false
>       # Only Dokima's own steps run its code: the repo's tests import the repo's own.
>       - name: Where Dokima's code is
>         run: rm -rf "$RUNNER_TEMP/dokima" && mv .dokima-code "$RUNNER_TEMP/dokima" && echo "DOKIMA_CODE=$RUNNER_TEMP/dokima" >> "$GITHUB_ENV"
>       - uses: actions/setup-python@v6
>         with:
>           python-version: "3.12"
>       - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
>       # The repo's Python, test tools and install command, from its settings file over Dokima's defaults (#794).
>       # A checkout whose settings reader has no setup mode (main before #794) sets up as this workflow did bef

**Agent:** Checking done: all four new tests fail for the right reason. One gap: the plan leaves out the workflow file that must change. Writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote four criteria and four new tests, one per criterion.", "The planner loosened three older tests so unplanned pull requests may pass."],
  "decided": ["Only the setting value allow lets unplanned pull requests through; block is tested as the other value."],
  "open": ["The plan names no change to the merge check's workflow file."]
 },
 "verdict": "block",
 "summary": "The tests are right, but the plan leaves out the workflow file the issue says must change.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Scope misses a file",
   "text": "For 857.1 and 857.2, a passing no-plan row needs its own exit in the workflow, as the issue says. Add `.github/workflows/acceptance-criteria.yml` to those criteria's files.",
   "evidence": "`.github/workflows/acceptance-criteria.yml:118` fails any row with no tests except `text-only` and `manual-fix`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "When a person opens a pull request with no approved plan, the Acceptance criteria check passes.", "source": "https://github.com/dokima-dev/dokima/issues/857", "criterion": "857.1"},
  {"ask": "When Dependabot opens a pull request with no approved plan, the Acceptance criteria check passes.", "source": "https://github.com/dokima-dev/dokima/issues/857", "criterion": "857.2"},
  {"ask": "When Dokima opens an issue's pull request with no approved plan, the Acceptance criteria check still fails.", "source": "https://github.com/dokima-dev/dokima/issues/857", "criterion": "857.3"},
  {"ask": "When the unplanned pull requests setting is not allow, a person's unplanned pull request fails the check.", "source": "https://github.com/dokima-dev/dokima/issues/857", "criterion": "857.4"},
  {"ask": "Add merge.unplanned_prs to dokima/defaults.yaml with allow as the default", "source": "https://github.com/dokima-dev/dokima/issues/857", "criterion": "857.1"},
  {"ask": "any othe
```

> Exit code 1
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/"Only the setting value allow lets unplanned pull requests through; block is tested as the other value."/"Only the value allow lets unplanned pull requests through; block is the tested other."/' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 857 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/block is the tested other\./block is the value tested against it./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 857 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/block is the value tested against it\./block is tested as another value./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 857 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#857](https://github.com/dokima-dev/dokima/issues/857) (pull requests with no plan pass unless Dokima opened them). It goes back to the planner for one fix.

**The problem:** the merge check's workflow file, `.github/workflows/acceptance-criteria.yml`, has to change, and the plan doesn't list it.
- Line 118 of that file fails any check row with no tests, unless the row is the text-only shortcut or a manual fix.
- So a passing "no plan" row needs its own way out in that file, as the issue's Context says.
- Without the file in scope, the worker's change to it would be undone. The work could then only pass through a workaround, such as pretending to be the text-only shortcut.
- The fix is to add that file to criteria 1 and 2. Because it's a workflow file, the pull request will stop for your approval.

**What's fine:**
- Each of your four criteria is one behavior and has its own test.
- I ran all four new tests: each fails today for the right reason, because the feature is missing, not because the test is broken.
- The three older tests the planner loosened still prove what they promised: no shortcut for the `.github/` and listed folders, and the manual fix check only for Dokima's own app. They pass today.
- No ask is missing and nothing extra was added.

The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

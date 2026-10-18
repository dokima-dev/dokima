# reviewer (plan) for #745

Run: https://github.com/dokima-dev/dokima/actions/runs/39103919650

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 112
> drwxr-xr-x  3 runner runner  4096 Oct 18 06:24 .
> drwxrwxrwt 18 root   root    4096 Oct 18 06:24 ..
> drwxr-xr-x  2 runner runner  4096 Oct 18 06:24 in
> -rw-r--r--  1 runner runner 13365 Oct 18 06:24 issue.md
> -rw-r--r--  1 runner runner     2 Oct 18 06:24 open_blockers.json
> -rw-r--r--  1 runner runner 63705 Oct 18 06:24 open_issues.json
> -rw-r--r--  1 runner runner   948 Oct 18 06:24 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 18 06:24 parent.json
> -rw-r--r--  1 runner runner  7719 Oct 18 06:24 plan.json
> 
> in:
> total 20
> drwxr-xr-x 2 runner runner 4096 Oct 18 06:24 .
> drwxr-xr-x 3 runner runner 4096 Oct 18 06:24 ..
> -rw-r--r-- 1 runner runner 8578 Oct 18 06:24 01-planner.json
> # Issue #745: Trial problems file themselves into Dokima's repo
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 742 -->
> <!-- dokima-blocking: {"blocked_by": [742], "blocks": [746], "loop": []} -->
> Problems that are Dokima's fault, and failed runs, on a trial repo file themselves into Dokima's repo.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/745#issuecomment-6246247889) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-d

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_upstream.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/745": "Phase 3 of #272. Dokima's problems found on a trial repo must land in dokima-dev/dokima by themselves, with a link back. Narrow slice of #273.\n\n**What**\n- A setting names the upstream repo where Dokima's own problems go (default: none, so an adopter's issues stay local).\n- The existing end-of-turn filing (#268) gains a tag agents put on problems that are Dokima's fault, not the repo's. Tagged problems file upstream.\n- A failed run files nothing today. A final step in each shared workflow files the failure upstream with the run link.\n- Repeats become comments on the existing upstream issue, never a second issue.\n- The App's key already covers every repo it is installed on in the org, so no new credential.\n\n**Done when:** acceptance item 19 on #272 passes: forcing the same Dokima-caused failure twice on the trial repo yields one upstream issue with two linked comments.\n"
> }{"number": null}{
>  "role": "planner",
>  "stage": null,
>  "run_id": "39101790236",
>  "commit_before": "ccbebe20951336dbdfb7da7800bf77e892c34308",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 2133289,
>   "turns": 36,
>   "cost_usd": 2.7338629999999995,
>   "tokens_in": 3283144,
>   "tokens_out": 50895
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/745/39101790236-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39101790236",
>  "check": {
>   "passed": true,
>   "p

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_upstream.py 2>&1 | grep -E "^(FAILED|ERROR|E  )|passed|failed" | cut -c1-400 | head -60
```

> The trial repo has no settings file, so the shipped default names no upstream repo. A passed review raises one
> E       AssertionError: 745.1: the hand-back check rejects a raise tagged as Dokima's fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> E         
> E         Left contains one more item: 'raise 1 carries fields no raise has: fault'
> E         
> E         Full diff:
> E         - []
> E         + [
> E         +     'raise 1 carries fields no raise has: fault',
> E         + ]
>         The trial repo's settings name dokima-dev/dokima. A passed review raises one problem tagged as Dokima's fault;
> E       AssertionError: 745.2: the hand-back check rejects a raise tagged as Dokima's fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> E         
> E         Left contains one more item: 'raise 1 carries fields no raise has: fault'
> E         
> E         Full diff:
> E         - []
> E         + [
> E         +     'raise 1 carries fields no raise has: fault',
> E         + ]
>         The trial repo's settings name dokima-dev/dokima. A passed review raises two problems, one tagged as Dokima's
> E       AssertionError: 745.2: the hand-back check rejects a raise tagged as Dokima's fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> E         
> E         Left contains one more item: 'raise 1 carries fields no raise has: fault'
> E         
> E     

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_upstream.py 2>&1 | grep -E "^E   +AssertionError|passed|failed" | cut -c1-300 | tail -14
```

> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[autopilot.yml] - AssertionError: 745.7: in autopilot.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstream failed` on failure: queue-failed, clos
> assert not ['queue-failed', 'closed']
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[board.yml] - AssertionError: 745.7: in board.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstream failed` on failure: queue, settle, sync
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[card.yml] - AssertionError: 745.7: in card.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstream failed` on failure: queue, card
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[commands.yml] - AssertionError: 745.7: in commands.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstream failed` on failure: route, queue, split,
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[full-suite.yml] - AssertionError: 745.7: in full-suite.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstream failed` on failure

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_upstream.py 2>&1 | grep -E "^FAILED" | cut -c1-250 | grep -E "745.9|mints|acceptance|agent.yml|entry|assign|audit"; grep -rhoE "secrets\.[A-Za-z_0-9]+" .github/workflows | sort | uniq -c; grep -n "def file_issues" -r dokima; grep -n "file_issues" dokima/*.py | head; ls dokima/roles; grep -n "raising" dokima/prompt.py | head
```

> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[acceptance-criteria.yml] - AssertionError: 745.7: in acceptance-criteria.yml, a failure of these jobs files nothing upstream, as no final step r
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[agent.yml] - AssertionError: 745.7: in agent.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstr
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[assign.yml] - AssertionError: 745.7: in assign.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.ups
> FAILED tests/test_upstream.py::test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream[audit.yml] - AssertionError: 745.7: in audit.yml, a failure of these jobs files nothing upstream, as no final step runs `python3 -m dokima.upstr
> FAILED tests/test_upstream.py::test_filing_upstream_mints_its_key_from_the_apps_own_key - AssertionError: 745.9: these steps file upstream without DOKIMA_UPSTREAM_TOKEN minted from the App's own key for the upstream repo's owner: agent.yml job run st
>       7 secrets.CLAUDE_CODE_OAUTH_TOKEN
>      19 secrets.DOKIMA_APP_KEY
>       1 secrets.SANDBOX_TOKEN
> dokima/agent_autopilot.py:184:def file_issues(repo, number, rec, recs):
> dokima/agent.py:49:    AUTOPILOT_START_LINE, link_edges, loop_through, n

**Agent:** Plan tests all fail today for missing-feature reasons. Now checking the existing filing code and the fake GitHub the tests use.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 150,260p dokima/agent_autopilot.py; sed -n 1,60p tests/upstream_gh.py
```

> continue
>             seen.add(path[-1])
>             stack += [path + [c] for c in sorted(blockers(path[-1]))]
>     return []
> 
> 
> def named(numbers):
>     """Issue numbers as words: #1, #2 and #3."""
>     ns = [f"#{n}" for n in numbers]
>     return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]
> 
> 
> FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268), under its name in settings (#784)
> 
> 
> def filed_label(repo):
>     """The filed label's name in the labels setting, created in REPO when missing.
> 
>     It gets its color from the settings and its description from the manifest. A refused creation is left to the
>     filing itself, which then says GitHub's reason."""
>     got = settings.read()
>     name = str((got.get("labels") or {}).get("filed") or FILED_LABEL)
>     want = manifest.labels(got)[name]
>     try:
>         agent_github.gh("api", f"repos/{repo}/labels/{urllib.parse.quote(name, safe='')}")
>     except subprocess.CalledProcessError:
>         try:
>             agent_github.gh("api", "-X", "POST", f"repos/{repo}/labels", "-f", f"name={name}",
>                             "-f", f"color={want['color']}", "-f", f"description={want['description']}")
>         except subprocess.CalledProcessError:
>             pass
>     return name
> 
> 
> def file_issues(repo, number, rec, recs):
>     """File every issue raise a passed review confirms as its own GitHub issue.
> 
>     It confirms its own, and each the planner or the worker raised that it answers done; `recs` are th

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -ln "steps\]\[-1\]\|\[\"steps\"\]\[-1\]\|carries fields no raise has" tests/*.py | head; grep -n "^upstream\|^  repo" dokima/defaults.yaml | head
```

> tests/test_upstream.py

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Wrote nine criteria and their tests: tagged problems and failed runs file upstream, linking back, repeats as comments.",
          "Added a fake GitHub holding the trial repo and Dokima's repo side by side."],
  "decided": ["Every job of every shared workflow ends with a step filing its failure upstream.",
              "The first failure also posts a comment, so two failures give two linked comments."],
  "open": ["Asks the owner whether failed test checks should file upstream too."]},
 "verdict": "approve",
 "summary": "The plan carries every ask with a test that fails today because the feature is missing; one question waits for the owner.",
 "raises": [],
 "answers": [
  {"raise": "P2", "answer": "done", "why": "The owner asks for two linked comments after two failures, so the first failure comments too.",
   "words": "forcing the same Dokima-caused failure twice on the trial repo yields one upstream issue with two linked comments",
   "source": "https://github.com/dokima-dev/dokima/issues/745", "changes": false}
 ],
 "asks": [
  {"ask": "A setting names the upstream repo where Dokima's own problems go", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.2"},
  {"ask": "default: none, so an adopter's issues stay local", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.1"},
  {"ask": "gains a tag agents put on problems that are Dokima's fault, not the repo's", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.4"},
  {"ask": "Tagged problems file upstream.", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.2"},
  {"ask": "must land in dokima-dev/dokima by themselves, with a link back", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.3"},
  {"ask": "A final step in each shared workflow files the failure upstream with the ru
```

> summary holds 22 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> rc=1

`9. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json;d=json.load(open('review.json'))
d['summary']="Every ask has a criterion and a test that fails today for the missing feature; one owner question waits."
d['previous_step']['did'][0]="Wrote nine criteria with tests: tagged problems and failed runs file upstream, linking back."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 745 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I approved the plan for [#745](https://github.com/dokima-dev/dokima/issues/745) (Dokima's own problems file themselves upstream). The review is in `/tmp/dokima-out/review.json`, and both checks pass.

- **Asks covered:** each of the owner's asks has a criterion:
  - the upstream setting, and its default of none
  - the tag that marks a problem as Dokima's fault
  - filing tagged problems upstream, with a link back
  - a final step that files failed runs upstream
  - repeats as comments, never a second issue
  - no new credential
  - the "Done when" test: the same failure twice gives one upstream issue with two linked comments
- **Tests:** I ran all 26 test cases from the plan's 12 tests. They all fail today, and for the right reason: the feature is missing. The tag isn't accepted yet, the failure-filing command doesn't exist, the workflows have no failure step, and no step uses an upstream key yet.
- **Each test checks what it should:** each one would fail if its behaviour were wrong. They run against a fake GitHub holding both repos and record which key each call used. Each criterion is one behaviour, and no edge cases are missing.
- **Workflow files:** the plan changes files under `.github/workflows/`, which needs an explicit ask. The issue does ask for "a final step in each shared workflow", so that is allowed.
- **Planner question P2 (should the first failure also post a comment?):** I answered yes on autopilot. The owner's words are "yields one upstream issue with two linked comments", which only works if the first failure comments too.
- **Planner question P1 (should failed test checks also file upstream?):** I left this for the owner. Those checks usually fail on the repo's own code, so filing them would change how much lands in Dokima's repo. The issue stays waiting on the owner's answer.

I raised no blockers.

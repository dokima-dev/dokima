# reviewer (plan) for #896

Run: https://github.com/dokima-dev/dokima/actions/runs/39275583836

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (45KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/9569f2f9-225d-4cde-b333-97dc1bf4054d/tool-results/bj2tho3ns.txt
> 
> Preview (first 2KB):
> # Issue #896: Settings may name only declared agent keys
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [913], "loop": []} -->
> A setting naming an agent key the shared workflow never receives is refused with one clear line.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/911 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/911/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/913
> 
> 
> **User story:** Owners who name an unusable agent key learn why in one line, from the audit and the run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Settings may name only the agent keys the entry wo

`2. Bash`
```
cd /tmp/pack; sed -e 's/<img[^>]*>//g' issue.md | head -c 30000
```

> # Issue #896: Settings may name only declared agent keys
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [913], "loop": []} -->
> A setting naming an agent key the shared workflow never receives is refused with one clear line.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/911 ·  [files changed](https://github.com/dokima-dev/dokima/pull/911/files)
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/913
> 
> 
> **User story:** Owners who name an unusable agent key learn why in one line, from the audit and the run.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** Settings may name only the agent keys the entry workflow declares; a job refuses any other.
>   *<a href="https://github.com/dokima-dev/dokima/blob/e4d3b876df31d8c82fb769318a31e74cf5cc2aec/tests/test_declared_keys.py#L63"> Acceptance test</a>: Settings may name each agent key entry.yml declares, and no other.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/e4d3b876df31d8c82fb769318a31e74cf5cc2aec/tests/test_declared_keys.py#L63">A declared key other than Claude's still works.</a></em></li></ul></details>
>   - Source: https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634
> -  **Acceptance criterion:** When settings name an undeclared key, the setup audit reports it in one line saying what to do.
>   *<a href="https://github.com/dokima-dev/dokima/blob/e4d3b876df31d8c82fb769318a31e74cf5cc2

`3. Bash`
```
cd /tmp/pack; ls in; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'));print(json.dumps({k:v for k,v in p.items() if k!='test_changes'},indent=1))"
```

> 01-worker.json
> 02-not-started-pr.json
> 03-worker.json
> 04-reviewer-pr.json
> 05-planner.json
> 06-reviewer-plan.json
> 07-planner.json
> 08-reviewer-plan.json
> 09-worker.json
> 10-reviewer-pr.json
> 11-planner.json
> []{
>  "kind": "user_story",
>  "title": "Settings may name only declared agent keys",
>  "summary": "A setting naming an agent key the shared workflow never receives is refused with one clear line.",
>  "user_story": "Owners who name an unusable agent key learn why in one line, from the audit and the run.",
>  "acceptance_criteria": [
>   {
>    "text": "Settings may name only the agent keys the entry workflow declares; a job refuses any other.",
>    "words": "The settings may name only agent keys `entry.yml` declares",
>    "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634",
>    "files": [
>     "dokima/agents.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "A declared key other than Claude's still works.",
>      "test": "tests/test_declared_keys.py::test_only_the_agent_keys_entry_yml_declares_are_accepted"
>     }
>    ]
>   },
>   {
>    "text": "When settings name an undeclared key, the setup audit reports it in one line saying what to do.",
>    "words": "The setup audit reports, in one line, a setting that names any other key: it will never reach the jobs; use a declared name, or ask for that name to be declared in a release.",
>    "source": "https://github.com/dokima-dev/dokima/issues/896#issuecomment-6268955634",
>    "files": [
>     "dokima/audit.py",
>     "dokima/agents.py"

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git fetch -q origin main 2>&1|tail -2; git diff --stat origin/main...HEAD; cat tests/test_declared_keys.py; python3 -c "
import json;r=json.load(open('/tmp/pack/in/08-reviewer-plan.json'));print(json.dumps(r,indent=1)[:5000])"
```

> README.md                       |   2 +-
>  docs/wiki/Installing.md         |   2 +-
>  dokima/agents.py                |  19 +++++-
>  dokima/audit.py                 |  12 +++-
>  tests/test_agent_codex.py       |   2 +-
>  tests/test_agent_kimi.py        |   2 +-
>  tests/test_agents.py            |  44 ++++++-------
>  tests/test_audit_secrets.py     |   4 +-
>  tests/test_declared_keys.py     | 142 ++++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_comments.py |  10 +--
>  tests/test_settings_setup.py    |  20 +++---
>  tests/test_thin_install.py      |  18 ++---
>  12 files changed, 220 insertions(+), 57 deletions(-)
> """Tests for #896: the settings may name only the agent keys entry.yml declares.
> 
> GitHub hands a reusable workflow in another account's repo only the secrets it declares by name, so a key outside
> entry.yml's list never reaches the jobs. The setup audit reports such a key in one line, a job naming it fails with that
> same line rather than as a missing key, and the install docs say so. The declared keys are read from entry.yml itself,
> so the tests follow it when a release declares another.
> """
> import os
> import re
> import subprocess
> import sys
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> sys.path.insert(0, ROOT)
> sys.path.insert(0, os.path.join(ROOT, "tests"))
> import test_settings_workflows as sw  # noqa: E402
> from test_audit import REPO, GitHub, audit  # noqa: E402
> from test_thin_install import everything_said, read_yaml, with_context  # noqa: E40

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git diff origin/main...HEAD -- tests/test_agent_codex.py tests/test_agent_kimi.py; python3 -m pytest -q tests/test_agent_codex.py tests/test_agent_kimi.py tests/test_declared_keys.py 2>&1|tail -3; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt origin/main 2>&1|tail -1; cp tests/test_declared_keys.py /tmp/mainwt/tests/; cd /tmp/mainwt && python3 -m pytest -q tests/test_declared_keys.py 2>&1|grep -E "^(FAILED|E  +AssertionError)|passed|failed"|head
```

> diff --git a/tests/test_agent_codex.py b/tests/test_agent_codex.py
> index 362cf210..2536a4cb 100644
> --- a/tests/test_agent_codex.py
> +++ b/tests/test_agent_codex.py
> @@ -31,7 +31,7 @@ SETTINGS = textwrap.dedent('''\
>      subscriptions:
>        codex-pro:
>          agent: codex
> -        key: CODEX_KEY
> +        key: CODEX_API_KEY
>      roles:
>        worker:
>          subscription: codex-pro
> diff --git a/tests/test_agent_kimi.py b/tests/test_agent_kimi.py
> index 9a8e69c8..553ef939 100644
> --- a/tests/test_agent_kimi.py
> +++ b/tests/test_agent_kimi.py
> @@ -47,7 +47,7 @@ SETTINGS = textwrap.dedent('''\
>      subscriptions:
>        moon:
>          agent: kimi
> -        key: KIMI_SIGN_IN
> +        key: KIMI_API_KEY
>      roles:
>        planner:
>          subscription: moon
> ..........                                                               [100%]
> 10 passed in 1.60s
> E       AssertionError: 896.1: settings naming MY_KEY, which entry.yml does not declare (['CLAUDE_CODE_OAUTH_TOKEN', 'CODEX_API_KEY', 'KIMI_API_KEY']), were accepted: 'MY_KEY\n'
> E       AssertionError: 896.2: for settings naming MY_KEY the audit should give one line saying it will never reach the jobs, to use a declared name or ask for it to be declared in a release; it said []
> E       AssertionError: 896.3: the run called MY_KEY missing instead of undeclared: ["::error title=No model key::The secret MY_KEY, which holds the planner's model key, is missing: add it as a repo secret (Settings, Secrets and variables, Actions), not only in 

**Agent:** Checks done: all four new tests fail on main for the right reason, and the two added Codex and Kimi test files only rename the key. Writing the review now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainwt; mkdir -p /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open('/tmp/pack/in/08-reviewer-plan.json'))['handback']
r['previous_step']={"did":["The planner added six older Codex and Kimi tests to its list of test changes.","Each now uses a declared key name, with the same checks."],"decided":["The four criteria and their tests stay as approved before."],"open":[]}
r['summary']="The plan now lists every older test it changes; all four new tests still fail on main for the right reason."
r['answers']=[]; r['raises']=[]
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 896 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json';r=json.load(open(p))
r['summary']="The plan now lists every older test it changes; the four new tests still fail on main as they should."
r['summary']="The plan now lists every older test it changes; all four new tests still fail on main correctly."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 896 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#896](https://github.com/dokima-dev/dokima/issues/896) (settings may name only declared agent keys), with no blockers. The hand-back passes both checks.

- **What changed since the last approved plan:** at code review's request, the planner added six older Codex and Kimi tests to the list of tests it changes. Each test only swaps a made-up key name for a declared one (`CODEX_KEY` becomes `CODEX_API_KEY`, `KIMI_SIGN_IN` becomes `KIMI_API_KEY`), and the checks stay the same. Those tests pass on the branch.
- **The four new tests:** I ran them against main, and each fails because the feature is missing:
  - an undeclared key is accepted;
  - the setup audit says nothing about it;
  - the job calls it a missing key;
  - the docs never list the allowed keys.
- **Your asks:** all four points in your decision comment still each have their own criterion. That includes updating the earlier promise that any key name works.
- **Open raises:** none were waiting for an answer.

The review is in `/tmp/dokima-out/review.json`.

# reviewer (plan) for #907

Run: https://github.com/dokima-dev/dokima/actions/runs/39332643579

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (33.6KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/446d8173-8095-49be-b134-7dde1afdc7fd/tool-results/bq5m812th.txt
> 
> Preview (first 2KB):
> total 64
> drwxr-xr-x 2 runner runner 4096 Oct 19 22:07 .
> drwxr-xr-x 3 runner runner 4096 Oct 19 22:07 ..
> -rw-r--r-- 1 runner runner 1445 Oct 19 22:07 01-worker.json
> -rw-r--r-- 1 runner runner 6308 Oct 19 22:07 02-planner.json
> -rw-r--r-- 1 runner runner 7248 Oct 19 22:07 03-reviewer-plan.json
> -rw-r--r-- 1 runner runner 9098 Oct 19 22:07 04-planner.json
> -rw-r--r-- 1 runner runner 9402 Oct 19 22:07 05-reviewer-plan.json
> -rw-r--r-- 1 runner runner 8773 Oct 19 22:07 06-planner.json
> # Issue #907: A rejected model key is reported as a missing plan
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/860
> 
> 
> **User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acce

`2. Bash`
```
cd /tmp/pack; sed -n '/^#/,$p' issue.md | grep -v '^$' | sed 's/<img[^>]*>//g' | head -300
```

> # Issue #907: A rejected model key is reported as a missing plan
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.
> **Plan**
>  **Relates to:**
> - https://github.com/dokima-dev/dokima/issues/860
> **User story:** When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.
>  **Acceptance criteria**
> -  **Acceptance criterion:** When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L115"> Acceptance test</a>: A 401 reads "Model key rejected"; a plain missing plan still says so.*
>   <details><summary><picture></picture> <em>Edge cases</em></summary><ul><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L131">The provider answers 403 instead of 401.</a></em></li><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L140">The provider says the token expired.</a></em></li><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L149">A Codex key is refused.</a></em></li><li><em><a href="https://github.com/dokima-dev/dokima/blob/try/issue-907/tests/test_key_rejected.py#L165">A Kimi sign-in is refused.</a></em></li><li><em><a href="ht

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; echo; cat plan.json; echo; cat in/05-reviewer-plan.json; cat in/06-planner.json | head -c 3000
```

> []
> {
>  "kind": "user_story",
>  "title": "A rejected model key is reported as a rejected key",
>  "summary": "When the provider refuses an agent's key, the owner is told which secret to replace, not shown a planner bug.",
>  "user_story": "When a model key stops working, the owner learns which secret to replace, at setup and on every failed run.",
>  "acceptance_criteria": [
>   {
>    "text": "When Claude Code, Codex or Kimi is refused its key, the run ends as Model key rejected.",
>    "words": "A refused key for Claude Code, Codex and Kimi each ends as \"Model key rejected\"",
>    "source": "https://github.com/dokima-dev/dokima/issues/907#issuecomment-6278270923",
>    "files": [
>     "dokima/agent_roles.py",
>     "dokima/agent_records.py",
>     "dokima/agents.py",
>     "dokima/agent_claude.py",
>     "dokima/agent_codex.py",
>     "dokima/agent_kimi.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "The provider answers 403 instead of 401.",
>      "test": "tests/test_key_rejected.py::test_a_403_from_the_provider_reads_model_key_rejected"
>     },
>     {
>      "case": "The provider says the token expired.",
>      "test": "tests/test_key_rejected.py::test_an_expired_token_reads_model_key_rejected"
>     },
>     {
>      "case": "A Codex key is refused.",
>      "test": "tests/test_key_rejected.py::test_a_refused_codex_key_reads_model_key_rejected"
>     },
>     {
>      "case": "A Kimi sign-in is refused.",
>      "test": "tests/test_key_rejected.py::test_a_refused_kimi_key_reads_model_key_rejected"
>     },
>     {
>      "ca

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 12cc0499 a8b66063 --stat; git diff 12cc0499 a8b66063 -- tests | head -80; timeout 300 python -m pytest -q tests/test_key_rejected.py 2>&1 | tail -30
```

> tests/test_key_rejected.py | 18 ++++++++++++++++++
>  1 file changed, 18 insertions(+)
> diff --git a/tests/test_key_rejected.py b/tests/test_key_rejected.py
> index a683df3c..85bfc082 100644
> --- a/tests/test_key_rejected.py
> +++ b/tests/test_key_rejected.py
> @@ -239,6 +239,24 @@ def test_the_record_never_prints_any_part_of_the_key(record_property, tmp_path):
>      assert not leaked, f"907.4: part of the key was printed on the card or its record: {leaked[:3]}"
>  
>  
> +def test_a_codex_refusal_never_prints_the_keys_tail(record_property, tmp_path):
> +    """A refused Codex key's card never repeats the key's tail the provider echoed.
> +
> +    Codex's refusal quotes the key masked, as `sk-proj-****efgh`. The planner runs on Codex with the key in its
> +    environment; the card and record must hold neither the key's last 4 characters nor any 8 of it in a row, so
> +    quoting the provider's message fails.
> +
> +    Proves 907.4."""
> +    record_property("proves", "907.4")
> +    comment, record = write_record(tmp_path, codex_output(CODEX_401), settings=planner_on("codex", "CODEX_API_KEY"),
> +                                   extra_env={"DOKIMA_AGENT_KEY": CODEX_KEY, "CODEX_API_KEY": CODEX_KEY},
> +                                   agent="codex")
> +    assert_key_rejected(comment, "907.4", "a 401 refusing the Codex key")
> +    pieces = {CODEX_KEY[-4:]} | {CODEX_KEY[i:i + 8] for i in range(len(CODEX_KEY) - 7)}
> +    leaked = sorted(p for p in pieces if p in comment or p in record)
> +    assert not leaked, f"90

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 300 python -m pytest -q tests/test_key_rejected.py 2>&1 | grep -E "^FAILED|Error" | head -40; grep -n "CODEX_401\s*=" -A5 tests/test_key_rejected.py; grep -n "def assert_key_rejected" -A12 tests/test_key_rejected.py
```

> E       AssertionError: 907.1: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
>         comment, _ = write_record(tmp_path, claude_output("API Error: 403 Forbidden: this key may not use this model."))
> E       AssertionError: 907.1: a 403 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: an expired token did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: a 401 refusing the Codex key did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.1: a 401 refusing the Kimi sign-in did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.2: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.2: a 401 refusing the codex key did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.3: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.4: a 401 from the provider did not end the run as "Model key rejected":
> tests/test_key_rejected.py:109: AssertionError
> E       AssertionError: 907.4: a 401 refusing

**Agent:** All 15 new tests fail today, each for the right reason (the feature is missing). Now checking the Codex key's tail, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^CODEX_KEY\|^CLAUDE_KEY\|^KIMI_KEY" tests/test_key_rejected.py
```

> 27:CODEX_KEY = "sk-proj-907codexsecretQRSTUVWXYZabcdefgh"
> 42:KIMI_KEY = kimi_sign_in()

`7. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
prev=json.load(open('in/05-reviewer-plan.json'))['handback']
r={k:prev[k] for k in ['asks','behaviors','tests','size']}
r['previous_step']={"did":["The planner added a Codex case checking the card never shows the key's tail."],
 "decided":["Nine criteria and fifteen tests stand; the rest of the plan is unchanged."],
 "open":["The installed workflow passes only Claude Code's key, filed as its own issue."]}
r['verdict']='approve'
r['summary']="The plan now proves every ask; all fifteen new tests fail today because the feature is missing."
r['raises']=[]; r['answers']=[]
r['edge_cases']=[{"criterion":f"907.{i}","cut":[],"missing":[]} for i in range(1,10)]
for t in r['tests']:
    if t['test'].endswith('test_the_record_never_prints_any_part_of_the_key'):
        t['why']="Claude refusal; card and record scanned for key pieces."
r['tests'].insert(9,{"test":"tests/test_key_rejected.py::test_a_codex_refusal_never_prints_the_keys_tail","only_its_behavior":True,"why":"Codex echoes the key's tail; quoting it fails."})
b=prev['boxes']; b['edges']={f"907.{i}":"covered" for i in range(1,10)}; b['poor_tests']="none"
r['boxes']=b
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 907 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#907](https://github.com/dokima-dev/dokima/issues/907) (a refused model key is reported as a missing plan). The hand-back is in `/tmp/dokima-out/review.json`, and it passed both checks.

- **Last blocker is fixed.** The new Codex test fails if the card or record shows any part of the key. That includes the last four characters (`efgh`), which Codex's error message repeats. So a card that just copies the provider's message can't pass.
- **All 15 new tests fail today, for the right reason.** Each fails because the feature isn't built yet, not because of a crash, a missing tool or a bad path.
- **Every ask is covered.** Everything from the original issue and the owner's answer in the comments has a criterion: all three agents, a real missing plan still reported as missing, the secret's name, the setup check, skipping keys that aren't set, the workflow change, and never printing a key.
- **Nothing left open.** No new raises, and no open blockers to answer.

One thing is still open outside this issue: the workflow adopters install passes only Claude Code's key, not the Codex or Kimi keys. It was already filed as [#930](https://github.com/dokima-dev/dokima/issues/930) (adopter keys dropped).

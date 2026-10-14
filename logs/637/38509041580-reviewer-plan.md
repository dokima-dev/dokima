# reviewer (plan) for #637

Run: https://github.com/dokima-dev/dokima/actions/runs/38509041580

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #637: The word check reads every rules topic file
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 636 -->
> <!-- dokima-blocking: {"blocked_by": [636], "blocks": [638], "loop": []} -->
> Owner words quoted from the rules pass the word check when they sit in a linked topic file.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/636
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/638
> 
> 
> **User story:** Owner words a plan reviewer quotes from any rules topic file still pass the word check.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Owner words quoted from the rules pass the word check when they sit only in a linked topic file.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-637/tests/test_rules_topics.py#L51"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-b

`2. Bash`
```
cat tests/test_rules_topics.py; grep -n "agents_text\|def said_there\|AGENTS.md" dokima/*.py | head -40; sed -n 60,100p .github/workflows/agent.yml; ls dokima
```

> """The word check reads every rules topic file the rules file links (#637).
> 
> The rules file (`AGENTS.md`) is becoming a short index that links topic files (#581). A plan reviewer may quote the
> owner's words with source "AGENTS.md"; the word check (`said_there`) must find them in `AGENTS.md` or in any repo
> markdown file it links. A run reads the rules from its runtime copy (`/tmp/runtime`, made by agent.yml's "Copy the
> runtime" step), so that step must bring the linked topic files too.
> 
> Both tests run the real thing: the word check from a runtime copy of `dokima/` in a temp folder, and the workflow's
> own copy step cut out of `.github/workflows/agent.yml` and run by bash in a temp checkout.
> """
> import os
> import shutil
> import subprocess
> import sys
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> TOPIC = "Needs you is a pill on the card, sorted to the top of each column."
> INDEX_LINE = "Only a code owner's commands count."
> INDEX = f"""# Rules
> 
> The rules live in topic files.
> 
> - [The board](rules/board.md)
> - An example issue: [#289](https://github.com/dokima-dev/dokima/issues/289)
> 
> {INDEX_LINE}
> """
> 
> 
> def write_rules(where):
>     """Write a temp rules file linking one topic file, both under `where`."""
>     (where / "rules").mkdir(parents=True, exist_ok=True)
>     (where / "AGENTS.md").write_text(INDEX)
>     (where / "rules" / "board.md").write_text(f"# The board\n\n{TOPIC}\n")
> 
> 
> def word_check(runtime, words, cwd):
>     """Run the word check from the runtime copy on wo

`3. Bash`
```
pytest -q tests/test_rules_topics.py 2>&1 | tail -15; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:1500])"
```

> E       AssertionError: 637.2: the copy step leaves out the topic file the rules file links, so the word check cannot read it
> E       assert (False)
> E        +  where False = exists()
> E        +    where exists = PosixPath('/tmp/pytest-of-runner/pytest-0/test_runtime_copy_holds_linked0/runtime/rules/board.md').exists
> 
> tests/test_rules_topics.py:116: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_rules_topics.py::test_word_check_reads_linked_topic_files - AssertionError: 637.1: words found only in a topic file the rules file links do not pass the word check
> assert False
>  +  where False = word_check(PosixPath('/tmp/pytest-of-runner/pytest-0/test_word_check_reads_linked_t0/runtime'), 'Needs you is a pill on the card, sorted to the top of each column.', PosixPath('/tmp/pytest-of-runner/pytest-0/test_word_check_reads_linked_t0/elsewhere'))
> FAILED tests/test_rules_topics.py::test_runtime_copy_holds_linked_topic_files - AssertionError: 637.2: the copy step leaves out the topic file the rules file links, so the word check cannot read it
> assert (False)
>  +  where False = exists()
>  +    where exists = PosixPath('/tmp/pytest-of-runner/pytest-0/test_runtime_copy_holds_linked0/runtime/rules/board.md').exists
> 2 failed in 0.16s
> dict_keys(['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url'])
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38508855226",
>  "com

`4. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner planned two criteria: the word check reads linked topic files, and each run copies them.",
          "The planner wrote one test for each, both failing today because the feature is missing."],
  "decided": ["The planner kept the copy step change, which the owner allowed for this story."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries the owner's ask and the copy it needs, and both tests fail today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Owner words quoted from the rules pass the word check when they sit only in a linked topic file.", "source": "https://github.com/dokima-dev/dokima/issues/637", "criterion": "637.1"},
  {"ask": "this story may change that copy step", "source": "https://github.com/dokima-dev/dokima/issues/581#issuecomment-6157254121", "criterion": "637.2"}
 ],
 "behaviors": [
  {"criterion": "637.1", "one_behavior": true, "why": "One check: words in a linked topic file pass."},
  {"criterion": "637.2", "one_behavior": true, "why": "One result: the run's copy holds the linked topic files."}
 ],
 "edge_cases": [
  {"criterion": "637.1", "cut": [], "missing": []},
  {"criterion": "637.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_rules_topics.py::test_word_check_reads_linked_topic_files", "only_its_behavior": true, "why": "Runs the real word check from a runtime copy; a pass-everything check fails it."},
  {"test": "tests/test_rules_topics.py::test_runtime_copy_holds_linked_topic_files", "only_its_behavior": true, "why": "Runs the workflow's own copy step; fails today because the topic file is not copied."}
 ],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 637 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`5. Bash`
```
sed -i 's/The planner planned two criteria: the word check reads linked topic files, and each run copies them./Planned two criteria: the word check reads linked topic files; each run copies them./; s/The planner wrote one test for each, both failing today because the feature is missing./Wrote one test for each; both fail today because the feature is missing./; s/The planner kept the copy step change, which the owner allowed for this story./Kept the copy step change, which the owner allowed for this story./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 637 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#637](https://github.com/dokima-dev/dokima/issues/637) (the word check reads every rules topic file). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass on it.

- **Criteria:** Both match what the owner asked for.
  - 637.1: owner words quoted from the rules pass when they sit only in a linked topic file. This is the issue's own ask.
  - 637.2: each run's copy of the rules holds those topic files. The owner allowed changing that copy step for this story in a [comment on #581](https://github.com/dokima-dev/dokima/issues/581#issuecomment-6157254121) (splitting the big agent file and the rules file).
- **Tests:** I ran both, and both fail today because the feature is missing, not because the tests are broken.
  - The word check misses words that are only in the linked topic file.
  - The copy step leaves the topic file out.
- **Checks that a pass means something:** The first test also checks that words found in no rules file still fail, so a check that passes everything can't get through. The second test runs the workflow's real copy step, not a copy of it.
- **Raises:** none, and there were no open blockers to answer.

Two loose spots, neither enough to block:
- The first test would also pass if the code read every markdown file in the folder, not only the linked ones.
- The second would pass if the copy step copied the whole repo.

Both still meet what the criteria promise.

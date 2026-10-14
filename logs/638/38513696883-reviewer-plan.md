# reviewer (plan) for #638

Run: https://github.com/dokima-dev/dokima/actions/runs/38513696883

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #638: The rules file splits by topic
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 636, 637 -->
> <!-- dokima-blocking: {"blocked_by": [636, 637], "blocks": [], "loop": []} -->
> The rules file becomes a short index, with each topic in its own linked file.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/636
> - https://github.com/dokima-dev/dokima/issues/637
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/581
> - https://github.com/dokima-dev/dokima/issues/379
> - https://github.com/dokima-dev/dokima/issues/400
> - https://github.com/dokima-dev/dokima/issues/432
> 
> 
> **User story:** Issues that change different rules change different files, and no test is lost along the way.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** T

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_rules_split.py; cat /tmp/pack/parent.json | head -c 4000; git show --stat HEAD | head -30
```

> """The rules file splits into a short index and topic files, losing no test (#638).
> 
> Story 3 of #581. Issues that change different rules kept clashing on `AGENTS.md`, one file of 29 KB, so the owner
> decided it becomes a short index linking topic files, all read by the word check (#581, comment 6157254121). Story 2
> (#637) already made the word check and agent.yml's runtime copy read every repo markdown file `AGENTS.md` links.
> 
> The index keeps its opening and the "Working in this repo" rules, which every agent must see first since `CLAUDE.md`
> loads only `AGENTS.md`; each other section moves, under its own `## ` heading, to a file the index links. Tests that
> read a rule find it through `tests/rules_files.py`, wherever the split puts it.
> 
> The last two tests hold "after both splits": each first checks the rules file is split, then proves its promise.
> """
> import os
> import subprocess
> import sys
> from collections import Counter
> 
> from rules_files import ROOT, rules_files
> 
> # Every section of AGENTS.md before the split, except "Working in this repo", which stays in the index.
> TOPICS = ("The picture", "The core rule", "Principles", "Roles", "The flow (the river)", "Commands",
>           "Raising and answering", "Where specs go", "The board", "The issue body", "Agent records and cards",
>           "Splitting and the graph", "Changing scope", "Identity and safety", "Decisions log")
> SHORT = 4000  # bytes; the rules file was 29 KB before the split.
> 
> # The tests that read the rules, each of whic

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests/ ':!tests/test_rules_split.py'; ls tests/samples/tests_before_split.txt; wc -l tests/samples/tests_before_split.txt; git log --oneline -3 -- tests/samples/tests_before_split.txt
```

> commit f360453668002c261befb74e1c648e8d31cb564a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Wed Oct 14 04:52:36 2026 +0000
> 
>     planner for #638 (run 38512135826)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/rules_files.py b/tests/rules_files.py
> new file mode 100644
> index 0000000..5818e30
> --- /dev/null
> +++ b/tests/rules_files.py
> @@ -0,0 +1,31 @@
> +"""The rules as tests read them: `AGENTS.md` and every topic file it links.
> +
> +The rules file (`AGENTS.md`) becomes a short index that links one file per topic (#638, story 3 of #581). Tests that
> +check a rule is written down read the rules through here, so they find a section wherever the split puts it. Topic
> +files follow the index's links in order, as the word check (`dokima.agent_next.rules_texts`) and agent.yml's runtime
> +copy read them: only repo markdown files, never a web link or a file outside the repo.
> +"""
> +import os
> +import re
> +
> +ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> +LINK = re.compile(r"\]\(([^)#\s:]+\.md)(?:#[^)]*)?\)")
> +
> +
> +def rules_files(root=ROOT):
> +    """`AGENTS.md`, then every existing repo markdown file it links, as repo paths."""
> +    index = open(os.path.join(root, "AGENTS.md"), encoding="utf-8").read()
> +    out = ["AGENTS.md"]
> +    for link in LINK.findall(index):
> +        path = os.path.normpath(link)
> +        if os.path.isabs(path) or path.split(os.sep)[0] =

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q -p no:cacheprovider tests/test_rules_split.py 2>&1 | tail -15; python3 - <<'EOF'
import sys; sys.path.insert(0,'tests')
import test_rules_split as t
from collections import Counter
before = Counter(l.strip().split("[")[0] for l in open(t.BEFORE) if l.strip())
now = Counter(n.split("[")[0] for n in t.collected())
lost=[(x,k,now[x]) for x,k in before.items() if x not in t.MOVED and now[x]<k]
print("lost",lost, sum(now.values()))
EOF
python3 - <<'EOF'
s=open('AGENTS.md').read()
i=s.index('## The picture'); print(len(s[:i].encode()))
EOF
```

> E        +    where ['AGENTS.md'] = rules_files()
> 
> tests/test_rules_split.py:61: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_rules_split.py::test_the_rules_file_is_a_short_index_linking_one_file_per_topic - AssertionError: 638.1: the rules file still holds these topics instead of linking them: ['The picture', 'The core rule', 'Principles', 'Roles', 'The flow (the river)', 'Commands', 'Raising and answering', 'Where specs go', 'The board', 'The issue body', 'Agent records and cards', 'Splitting and the graph', 'Changing scope', 'Identity and safety', 'Decisions log']
> assert not ['The picture', 'The core rule', 'Principles', 'Roles', 'The flow (the river)', 'Commands', ...]
> FAILED tests/test_rules_split.py::test_the_tests_that_read_the_rules_pass_after_the_split - AssertionError: 638.2: the rules file is not split yet: AGENTS.md links no topic file
> assert 1 > 1
>  +  where 1 = len(['AGENTS.md'])
>  +    where ['AGENTS.md'] = rules_files()
> FAILED tests/test_rules_split.py::test_every_test_from_before_the_first_split_still_runs - AssertionError: 638.3: the rules file is not split yet: AGENTS.md links no topic file
> assert 1 > 1
>  +  where 1 = len(['AGENTS.md'])
>  +    where ['AGENTS.md'] = rules_files()
> 3 failed in 0.04s
> lost [] 1166
> 888

`5. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/sim; mkdir /tmp/sim; git archive HEAD | tar -x -C /tmp/sim; cd /tmp/sim; python3 - <<'EOF'
import re,os
s=open('AGENTS.md').read()
parts=re.split(r'(?m)^(?=## )',s)
head=parts[0]+parts[1]  # opening + Working
names=["picture","core-rule","principles","roles","flow","commands","raising","specs","board","issue-body","records","splitting","scope","identity","decisions"]
os.makedirs('rules',exist_ok=True)
links=[]
for n,p in zip(names,parts[2:]):
    open(f'rules/{n}.md','w').write(p.rstrip()+"\n")
    links.append(f"- [{p.splitlines()[0][3:]}](rules/{n}.md)")
open('AGENTS.md','w').write(head.rstrip()+"\n\n## Topics\n\n"+"\n".join(links)+"\n")
print(os.path.getsize('AGENTS.md'))
EOF
timeout 900 python3 -m pytest -q -p no:cacheprovider tests/test_rules_split.py 2>&1 | tail -8
```

> 1464
> ...                                                                      [100%]
> 3 passed in 3.67s
> Shell cwd was reset to /home/runner/work/dokima/dokima

**Agent:** Simulated split passes the three new tests; now running the full suite on the simulated split to check nothing else breaks.

`6. Bash`
```
cd /tmp/sim && git init -q && git -c user.email=a@b -c user.name=a add -A >/dev/null && git -c user.email=a@b -c user.name=a commit -qm x; timeout 1200 python3 -m pytest -q -p no:cacheprovider -x -n auto tests 2>&1 | tail -5 || true
```

> ........................................................................ [ 86%]
> ........................................................................ [ 92%]
> ........................................................................ [ 98%]
> ..............                                                           [100%]
> 1166 passed in 181.30s (0:03:01)
> Shell cwd was reset to /home/runner/work/dokima/dokima

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 9p dokima/roles/worker.md; sed -n 19p dokima/roles/planner.md
```

> 1. Orient before touching anything. Read the plan on the issue, AGENTS.md, then the code the plan's scope points to and
> ticket, against the code and AGENTS.md:

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Wrote three tests: the rules file is a short index, rule tests pass, no test is lost.",
          "Made the tests that read the rules also read the linked topic files."],
  "decided": ["Each topic moves to its own file in a rules folder; the repo rules stay in the index."],
  "open": ["Raised that role prompts name only the rules file."]
 },
 "verdict": "approve",
 "summary": "The plan keeps all three asks, and each test fails today and passes on a trial split.",
 "raises": [],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "Confirmed: the worker and planner prompts point agents to the rules file only, so topic files go unread."}
 ],
 "asks": [
  {"ask": "The rules file becomes a short index that links one file per topic.", "source": "https://github.com/dokima-dev/dokima/issues/581#issuecomment-6157254121", "criterion": "638.1"},
  {"ask": "All tests pass after both splits.", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "638.2"},
  {"ask": "Every test that ran on main before the first split still runs after both splits.", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "638.3"}
 ],
 "behaviors": [
  {"criterion": "638.1", "one_behavior": true, "why": "One result: a short index with one linked file per topic."},
  {"criterion": "638.2", "one_behavior": true, "why": "One result: the rule tests pass; the All tests check covers the rest."},
  {"criterion": "638.3", "one_behavior": true, "why": "One result: no test from before the first split is lost."}
 ],
 "edge_cases": [
  {"criterion": "638.1", "cut": [], "missing": []},
  {"criterion": "638.2", "cut": [], "missing": []},
  {"criterion": "638.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_rules_split.py::test_the_rules_file_is_a_short_index_linking_one_file_per_topic", "only_its_behavior": true, "why": "Fails today naming the 15 top
```

> Exit code 1
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step decided line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["previous_step"]["did"][0]="Wrote three tests: a short index, rule tests passing, no test lost."
r["previous_step"]["decided"][0]="Each topic gets its own file in a rules folder; repo rules stay."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 638 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(type(d), len(d))
for i in d: print(i if not isinstance(i,dict) else (i.get('number'), i.get('title')))
" | head -60; grep -n "searched\|symptom" dokima/agent*.py | head -20
```

> <class 'list'> 131
> (653, 'AGENTS.md says the Definition of Done shows All tests; once this lands the card says Test suite.')
> (652, "Live cards never show an edge case's source: no record holds one, only the saved 557 data does.")
> (651, 'A card with no plan still says All tests, while planned cards will say Test suite after this lands.')
> (638, 'The rules file splits by topic')
> (632, "The reviewer's prompt never mentions its open issues list, searched or verdict, so it learns them only from rejections.")
> (631, "The command copies how the card collects its data instead of calling the branch's own step, so a branch changing that step is not shown.")
> (628, 'A test holds the drawing code to every fixture')
> (620, 'A check that ran before plan approval stays failed when the app cannot re-run workflows, so every merge gate fails again.')
> (619, 'A story filed by an earlier split and left out of the re-plan stays an open sub-issue, so the parent never closes.')
> (614, 'The board follows stage changes, with no sweeps')
> (613, 'The card is drawn from record files at stage changes')
> (612, "The owner's words are quoted and kept as first written")
> (611, 'Run comments show the record, never its raw data')
> (610, "Each run's record is saved as its own file")
> (609, 'Follow-up to #560: latest comment wins, split stories stay in records, byte-exact ask fold, one-write card, queue removal, stage-bound API use, trigger test cleanup.')
> (605, 'Other tests still fake the `DOKIMA_AUTO_MERGE` variable read

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 10,60p dokima/agent_checks.py; grep -n "SEARCHED\|VERDICT\|SYMPTOMS\|CAUSE" dokima/raises.py | head; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'))
for i in d:
  t=json.dumps(i).lower()
  if 'agents.md' in t or 'prompt' in t or 'rules' in t: print(i.get('number'), i.get('title')[:150])"
```

> from dokima import raises, words
> 
> 
> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(open(path)) if os.path.exists(path) else []
>     theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
>               and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
>     confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
>                  and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
>     filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
>     if not filed:
>         return []
>     bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
>     named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
>              for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numb

**Agent:** Fixing the hand-back so it lists which open issues I searched and gives a verdict for the issue the planner raised.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["answers"][0].update({"searched":[581,42,39,88],"verdict":"new"})
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 638 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#638](https://github.com/dokima-dev/dokima/issues/638) (the rules file splits by topic). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** the three asks from the approved plan of [#581](https://github.com/dokima-dev/dokima/issues/581) (split the big agent file and the rules file) each have a criterion. Your comments on #638 are only the autopilot commands.
- **The new tests fail today for the right reason:** the first says the rules file still holds all 15 topics. The other two say the rules file is not split yet.
- **The split can pass:** I tried a quick split in a scratch copy, putting each topic in its own file under `rules/` with a 1.5 KB index. All three new tests passed, and so did the full suite (1166 tests). No test from before the first split is lost, apart from the one rename the plan already records.
- **The planner's raise:** I confirmed it. The worker and planner prompts point agents only to `AGENTS.md`, so after the split they would not read the topic files. It goes to you as a new issue. I searched [#581](https://github.com/dokima-dev/dokima/issues/581) (the parent split), [#42](https://github.com/dokima-dev/dokima/issues/42) (role prompts), [#39](https://github.com/dokima-dev/dokima/issues/39) (one adapter per agent) and [#88](https://github.com/dokima-dev/dokima/issues/88) (what each role sees), and none of them covers it.

One thing I let through without blocking: criterion 638.2 says "every test that reads the rules still passes", while the ask says "all tests pass". Its own test runs only the tests that read the rules. The full suite is still proven, by the All tests check before merge.

# reviewer (plan) for #815

Run: https://github.com/dokima-dev/dokima/actions/runs/39067955899

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #815: Wiki install page uses the thin workflow
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 813 -->
> <!-- dokima-blocking: {"blocked_by": [813], "blocks": [816], "loop": []} -->
> The wiki's install page stops telling adopters to copy Dokima's workflows and code.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/815#issuecomment-6240688293) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/814
> - https://github.com/dokima-dev/dokima/issues/272
> 
> 
> **User story:** Adopters following the wiki install page no longer copy Dokima's workflows and code into their repo.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dok

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_wiki_install.py; cat -n docs/wiki/Installing.md; python -m pytest -q tests/test_wiki_install.py 2>&1 | tail -15; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps(d,indent=1)[:3000])"
```

> """The wiki's install page never tells adopters to copy Dokima's workflows or code.
> 
> Issue #815, story 4 of #742. An adopter's repo holds only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`;
> all Dokima code runs from Dokima's own repo. This test reads `docs/wiki/Installing.md`, the page adopters follow.
> """
> 
> import re
> from pathlib import Path
> 
> PAGE = Path(__file__).parent.parent / "docs" / "wiki" / "Installing.md"
> 
> 
> def page():
>     """Returns the install page's text."""
>     return PAGE.read_text()
> 
> 
> def test_the_install_page_never_tells_adopters_to_copy_dokimas_workflows_or_code(record_property):
>     """The install page never tells adopters to copy Dokima's workflows folder or its code.
> 
>     Finds every line of the page that says to copy something and fails on any that names the whole workflows folder
>     or the `dokima/` folder (or package), as the page's step 4 does today. Copying the single `dokima.yml` is fine.
> 
>     Proves 815.1."""
>     record_property("proves", "815.1")
>     folders = re.compile(r"`\.github/workflows/?`|`dokima/?`(?!\S)|`dokima/?` package|the dokima package", re.I)
>     bad = [line for line in page().splitlines() if "copy" in line.lower() and folders.search(line)]
>     assert not bad, f"815.1: the install page still tells adopters to copy Dokima's workflows or code: {bad}"
> 
>      1	# Installing
>      2	
>      3	**Honest status:** δokima runs on its own repo, [dokima-dev/dokima](https://github.com/dokima-dev/dokima). Onboarding other repos (one link

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner wrote one criterion: the install page never tells adopters to copy Dokima's workflows or code.", "The planner wrote one test that fails today on the page's step 4."], "decided": ["The plan leaves the page's workflow table and the two files to add out of scope."], "open": ["The planner asks the owner whether the page should also name the two files to add."]},
 "verdict": "block",
 "summary": "The one test only looks for the word copy, so a reworded step 4 still passes.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "815.1 weak test", "text": "The test for 815.1 only flags lines with the word copy, so rewording step 4 to put or add both folders still passes. Fix: drop the copy filter and fail on any line naming the whole workflows folder or the `dokima/` package.", "evidence": "`tests/test_wiki_install.py:27` keeps only lines where `\"copy\" in line.lower()`."},
  {"kind": "blocker", "to": "planner", "label": "Story ask not carried", "text": "The approved story says the page tells adopters to add the one workflow and settings file; no criterion carries it. Add criteria, unless the owner's answer to P1 says no.", "evidence": "Issue body, story 4 of #742: tells adopters to add the one workflow and settings file, not to copy Dokima."}
 ],
 "answers": [],
 "asks": [
  {"ask": "The wiki's install page no longer tells adopters to copy Dokima's workflows and code.", "source": "https://github.com/dokima-dev/dokima/issues/815", "criterion": "815.1"},
  {"ask": "The wiki's install page tells adopters to add the one workflow and settings file, not to copy Dokima.", "source": "https://github.com/dokima-dev/dokima/issues/815", "criterion": "missing"}
 ],
 "behaviors": [{"criterion": "815.1", "one_behavior": true, "why": "One page, one thing it must never say."}],
 "edge_cases": [{"criterion": "815.1", "cut": [], "missing": ["The same instruction worded withou
```

> Exit code 1
> raise 1's text holds 42 words, over its cap of 30: cut 12, keep the facts
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`4. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']={"did":["The planner wrote one criterion: the install page never says to copy Dokima's workflows or code.","The planner wrote one test that fails today on step 4."],"decided":["The plan leaves the workflow table and the two files to add out of scope."],"open":["The planner asks the owner whether the page should name the two files to add."]}
d['raises'][0]['text']="The test for 815.1 only flags lines saying copy, so step 4 reworded to put or add still passes. Fix: drop the copy filter; fail on any line naming either folder."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 815 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> Exit code 1
> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`5. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']['did'][0]="The planner wrote one criterion: the page never says to copy Dokima's workflows or code."
d['raises'][0]['text']="The test for 815.1 only flags lines saying copy, so step 4 reworded to put or add still passes. Fix: drop the copy filter; fail on lines naming either folder."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 815 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#815](https://github.com/dokima-dev/dokima/issues/815) (wiki install page uses the thin workflow). The review is in `/tmp/dokima-out/review.json`, and both checks pass on it.

**Two blockers, both for the planner:**
- **The test is too weak.** It only flags lines that contain the word "copy" (`tests/test_wiki_install.py:27`). If step 4 were reworded to say "put" or "add" both folders, the test would still pass. The fix is to drop that filter and fail on any line that names the whole workflows folder or the `dokima/` package.
- **One ask has no criterion.** The approved story from [#742](https://github.com/dokima-dev/dokima/issues/742) (thin install, no Dokima code in the adopter's repo) says the page should tell adopters to add the one workflow and settings file. No criterion covers that. The planner should add criteria for it unless the owner says no to the planner's question.

**What I checked:**
- The plan's one test fails today for the right reason: step 4 still says to copy `.github/workflows/` and the `dokima/` package.
- The plan has one criterion, and it is one behavior.

**Left for the owner:** the planner's question P1 asks whether the page should also stop listing Dokima's own two workflows and name the two files to add. I didn't answer it, because the answer changes what gets built.

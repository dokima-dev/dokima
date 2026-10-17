# reviewer (plan) for #815

Run: https://github.com/dokima-dev/dokima/actions/runs/39071646670

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> total 40
> drwxr-xr-x 2 runner runner 4096 Oct 17 21:36 .
> drwxr-xr-x 3 runner runner 4096 Oct 17 21:36 ..
> -rw-r--r-- 1 runner runner 2157 Oct 17 21:36 01-planner.json
> -rw-r--r-- 1 runner runner 3790 Oct 17 21:36 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5812 Oct 17 21:36 03-planner.json
> -rw-r--r-- 1 runner runner 5199 Oct 17 21:36 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5322 Oct 17 21:36 05-planner.json
> # Issue #815: Wiki install page uses the thin workflow
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 813, 814 -->
> <!-- dokima-blocking: {"blocked_by": [813], "blocks": [816], "loop": []} -->
> The wiki's install page tells adopters to add one workflow and one settings file, never a copy of Dokima.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/813
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="rel

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_wiki_install.py; cat docs/wiki/Installing.md; python -m pytest -q tests/test_wiki_install.py 2>&1 | tail -30; cat /tmp/pack/in/05-planner.json | head -80
```

> """The wiki install page asks for one workflow and one settings file, never Dokima's code.
> 
> Issue #815, story 4 of #742. An adopter's repo holds only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`;
> all Dokima code runs from Dokima's own repo. These tests read `docs/wiki/Installing.md`, the page adopters follow.
> """
> 
> import re
> from pathlib import Path
> 
> ROOT = Path(__file__).parent.parent
> PAGE = ROOT / "docs" / "wiki" / "Installing.md"
> WORKFLOW = ".github/workflows/dokima.yml"
> SETTINGS = ".dokima/settings.yaml"
> ADD = re.compile(r"\b(add|adds|added|create|commit|put)\b", re.I)
> 
> 
> def page():
>     """Returns the install page's text."""
>     return PAGE.read_text()
> 
> 
> def dokimas_own_workflows():
>     """Returns the names of Dokima's own workflow files, every one but the thin `dokima.yml`."""
>     return sorted(p.name for p in (ROOT / ".github" / "workflows").glob("*.yml") if p.name != "dokima.yml")
> 
> 
> def test_the_install_page_never_tells_adopters_to_put_dokimas_folders_in_their_repo(record_property):
>     """The install page never tells adopters to add Dokima's workflows folder or code folder.
> 
>     Fails on any line naming the whole `.github/workflows/` folder or the `dokima/` folder (or package), whatever
>     the verb, as the page's step 4 does today. A single file inside them, like `dokima.yml`, is fine.
> 
>     Proves 815.1."""
>     record_property("proves", "815.1")
>     folders = re.compile(
>         r"\.github/workflows/?(?![\w./-])|(?<![\w./-])dokima/(?![\w.-])|`dokima` pac

`3. Bash`
```
cd /tmp/pack; python3 -c "import json;print(json.dumps(json.load(open('in/04-reviewer-plan.json'))['handback'],indent=1))" | head -80; cat open_blockers.json
```

> {
>  "previous_step": {
>   "did": [
>    "The planner wrote five criteria for the install page, one test each.",
>    "The planner made the folder test fail whatever the verb, as the owner asked."
>   ],
>   "decided": [
>    "The plan keeps the code owners step on the page."
>   ],
>   "open": [
>    "The planner asks the owner whether the code owners step should stay."
>   ]
>  },
>  "verdict": "approve",
>  "summary": "All five tests fail today for the right reason; only the code owners question waits for the owner.",
>  "raises": [],
>  "answers": [
>   {
>    "raise": "P3",
>    "answer": "done",
>    "why": "Confirmed: markdown never joins criteria, so the test file joins them. Fine as a separate issue.",
>    "searched": [
>     800,
>     725,
>     551,
>     432
>    ],
>    "verdict": "new"
>   }
>  ],
>  "asks": [
>   {
>    "ask": "The wiki's install page no longer tells adopters to copy Dokima's workflows and code.",
>    "source": "https://github.com/dokima-dev/dokima/issues/815",
>    "criterion": "815.1"
>   },
>   {
>    "ask": "The 815.1 test must fail on any line telling adopters to put Dokima's `.github/workflows/` or `dokima/` folders in their repo, whatever the verb.",
>    "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967",
>    "criterion": "815.1"
>   },
>   {
>    "ask": "the page tells adopters to add the one workflow",
>    "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967",
>    "criterion": "815.2"
>   },
>   {
>    "ask": "and the settings file",
>    "source": "https://gi

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cp docs/wiki/Installing.md /tmp/orig.md; python3 - <<'E'
import re
p='docs/wiki/Installing.md'; t=open(p).read()
s=t.index('## 3. Code owners'); e=t.index('## 5. Branch')
t=t[:s]+"""## 3. Files to add

Add `.github/workflows/dokima.yml` and add `.dokima/settings.yaml`.

You add only `.github/workflows/dokima.yml` and `.dokima/settings.yaml`, nothing else.

A code owners file, `CODEOWNERS`, is optional, to name approvers other than the owner.

"""+t[e:]
open(p,'w').write(t)
E
python -m pytest -q tests/test_wiki_install.py 2>&1 | tail -3; cp /tmp/orig.md docs/wiki/Installing.md; git status --short
```

> ......                                                                   [100%]
> 6 passed in 0.06s

**Agent:** Good case passes, all six fail today for the right reason. Writing the review.

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'E'
{
 "previous_step": {
  "did": [
   "The planner added a sixth criterion: the code owners file is never a file to add.",
   "The planner added a test that fails on the code owners step today."
  ],
  "decided": [
   "The page may name the code owners file once, only as optional."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "All six tests fail today for the right reason and pass on a fixed page; nothing waits for the owner.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "The wiki's install page no longer tells adopters to copy Dokima's workflows and code.", "source": "https://github.com/dokima-dev/dokima/issues/815", "criterion": "815.1"},
  {"ask": "The 815.1 test must fail on any line telling adopters to put Dokima's `.github/workflows/` or `dokima/` folders in their repo, whatever the verb.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.1"},
  {"ask": "the page tells adopters to add the one workflow", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.2"},
  {"ask": "and the settings file", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.3"},
  {"ask": "The page names those two files as the whole install.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.4"},
  {"ask": "It stops listing Dokima's own workflows, including `playthrough.yml` and `wiki.yml`, as things to add.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.5"},
  {"ask": "don't keep it as an install step.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241461863", "criterion": "815.6"},
  {"ask": "The page may mention it once as optional, for naming approvers other than the owner, but never among the files to add.", "so
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner added a sixth criterion: the code owners file is never a file to add./The planner added a sixth criterion: code owners is never a file to add./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 815 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for issue #815 (wiki install page uses the thin workflow). It has no open questions, and both checks on my `review.json` pass.

- **Code owners file:** the planner added a sixth criterion from your last comment. The page must never list the code owners file as a file to add. It may mention it once, as optional.
- **Tests fail today:** I ran all six, and each fails for the right reason. The page still says to copy the workflows folder and the code folder. It doesn't name the two files to add, and doesn't say they are the whole install. It still lists Dokima's own workflows, and it still has a code owners step.
- **Tests pass on a fixed page:** I briefly rewrote the page the way you asked. All six tests passed, then I put the page back as it was.
- **Your asks:** each request from the issue and your two comments maps to one of the six criteria. Nothing is missing, and the plan adds nothing you didn't ask for.

I raised nothing, and there were no earlier blockers to answer. Say `/work` to build it.

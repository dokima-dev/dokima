# reviewer (plan) for #815

Run: https://github.com/dokima-dev/dokima/actions/runs/39070921034

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #815: Wiki install page uses the thin workflow
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 813, 814 -->
> <!-- dokima-blocking: {"blocked_by": [813], "blocks": [816], "loop": []} -->
> The wiki's install page tells adopters to add one workflow and one settings file, never a copy of Dokima.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241300938) with `/plan`, or say `/review`
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

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_wiki_install.py; cat docs/wiki/Installing.md; python3 -m pytest -q tests/test_wiki_install.py 2>&1 | tail -40; git diff HEAD~2 --stat; cat /tmp/pack/owner_words.json | head -50
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
cd /home/runner/work/dokima/dokima; ls .github/workflows; grep -n "def code_files\|def check_groups" -A15 dokima/planner.py | head -60; cat /tmp/pack/in/02-reviewer-plan.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d.get('handback',d),indent=1)[:3000])"
```

> acceptance-criteria.yml
> agent.yml
> assign.yml
> audit.yml
> autopilot.yml
> board.yml
> card.yml
> commands.yml
> entry.yml
> fix.yml
> full-suite.yml
> playthrough.yml
> reviews.yml
> testmon.yml
> uptodate.yml
> wiki.yml
> 163:def code_files(c):
> 164-    """The code files a criterion changes: its files, less markdown, which never joins criteria."""
> 165-    return {f.strip() for f in c.get("files") or [] if not f.strip().lower().endswith(".md")}
> 166-
> 167-
> 168-def story_groups(criteria):
> 169-    """The stories these criteria make: criteria sharing a code file are one story.
> 170-
> 171-    Sharing may be direct or through another criterion. Returns one list per story, each the 0-based indexes of its criteria in ascending order, the stories in the order
> 172-    of their first criterion. Edge cases never change the groups."""
> 173-    root = list(range(len(criteria)))
> 174-
> 175-    def find(i):
> 176-        while root[i] != i:
> 177-            root[i] = root[root[i]]
> 178-            i = root[i]
> --
> 192:def check_groups(stories, nested=False):
> 193-    """Garbled unless the stories follow code's groups of criteria by shared code files.
> 194-
> 195-    Each story's criteria lie in one group. A group of at most MAX_CRITERIA criteria is one story; a larger group is
> 196-    cut into consecutive stories of at most MAX_CRITERIA each, every later one depending on the one before, so stories
> 197-    sharing code files take turns."""
> 198-    crits, story_of = [], []
> 199-    for n, s in enumerate(stories, 1):
> 200-        for c in 

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner wrote five criteria for the install page, one test each.",
   "The planner made the folder test fail whatever the verb, as the owner asked."
  ],
  "decided": [
   "The plan keeps the code owners step on the page."
  ],
  "open": [
   "The planner asks the owner whether the code owners step should stay."
  ]
 },
 "verdict": "approve",
 "summary": "All five tests fail today for the right reason and carry every ask; only the code owners question waits for the owner.",
 "raises": [],
 "answers": [
  {"raise": "P3", "answer": "done", "why": "Confirmed: markdown never joins criteria, so the test file joins them. Fine as a separate issue."}
 ],
 "asks": [
  {"ask": "The wiki's install page no longer tells adopters to copy Dokima's workflows and code.", "source": "https://github.com/dokima-dev/dokima/issues/815", "criterion": "815.1"},
  {"ask": "The 815.1 test must fail on any line telling adopters to put Dokima's `.github/workflows/` or `dokima/` folders in their repo, whatever the verb.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.1"},
  {"ask": "the page tells adopters to add the one workflow", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.2"},
  {"ask": "and the settings file", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.3"},
  {"ask": "The page names those two files as the whole install.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.4"},
  {"ask": "It stops listing Dokima's own workflows, including `playthrough.yml` and `wiki.yml`, as things to add.", "source": "https://github.com/dokima-dev/dokima/issues/815#issuecomment-6241293967", "criterion": "815.5"}
 ],
 "behaviors": [
  {"criterion": "815.1", "one_behavior": true,
```

> Exit code 1
> summary holds 22 words, over its cap of 20 (up to 24 passes)
> the answer to P3 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P3 files an issue, so verdict must be symptom, root cause or new, not None

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'));print(type(d), len(d));print(json.dumps(d,indent=0)[:3000])"; grep -rn "searched" /home/runner/work/dokima/dokima/dokima/agent.py | head; grep -rln "searched" /home/runner/work/dokima/dokima/rules/
```

> <class 'list'> 188
> [
> {
> "number": 832,
> "title": "A failed merge queue run is handled, and every hand fix names its issue",
> "summary": "Two gaps the owner asked to close by hand fix on 2026-10-17.",
> "link": "https://github.com/dokima-dev/dokima/issues/832",
> "filed_by_dokima": false
> },
> {
> "number": 829,
> "title": "The sandbox already holds the old copied Dokima code and workflows; a new install leaves them there, still running.",
> "summary": "The sandbox already holds the old copied Dokima code and workflows; a new install leaves them there, still running.",
> "link": "https://github.com/dokima-dev/dokima/issues/829",
> "filed_by_dokima": true
> },
> {
> "number": 826,
> "title": "The reviewer's prompt never says the edges box is an object keyed by criterion, so reviewers may guess wrong and be rejected.",
> "summary": "The reviewer's prompt never says the edges box is an object keyed by criterion, so reviewers may guess wrong and be rejected.",
> "link": "https://github.com/dokima-dev/dokima/issues/826",
> "filed_by_dokima": true
> },
> {
> "number": 825,
> "title": "The wiki sync writes the bot placeholder as it is, and commits on the logs branch credit no co-author.",
> "summary": "The wiki sync writes the bot placeholder as it is, and commits on the logs branch credit no co-author.",
> "link": "https://github.com/dokima-dev/dokima/issues/825",
> "filed_by_dokima": true
> },
> {
> "number": 820,
> "title": "In an adopter's repo the checks run inside a called workflow, so GitHub prefixes their names; the required check

**Agent:** Draft review is written; fixing two checker complaints (summary length, and the issue answer needs a search of open issues).

`6. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('open_issues.json'))
for i in d:
  t=(i['title']+i['summary']).lower()
  if any(k in t for k in ['markdown','story','stories','docs-only','group','split']): print(i['number'],i['title'])"; grep -n "searched" -B3 -A20 /home/runner/work/dokima/dokima/rules/raising.md | head -60
```

> 800 Any-size input: break documents into features, stories and criteria, with caps the planner knows
> 756 Standard repo files and settings
> 755 First release: tag v0.1.0 with a changelog
> 754 A picture of the product: screenshot or GIF of the card on the README and website
> 753 One tagline everywhere: repo description, README and website
> 732 Output family: Plan, Work and Review, each drawing its own card section
> 725 No step carries a split story's full halves into the issue its planner reads.
> 724 Recovery: restart or flag work that stalled with no run alive
> 723 Run: one agent job as a real object with a clear outcome
> 722 Dispatcher: one place decides the river's next step
> 709 Every raise and story has a short and full half
> 694 When the owner approves new scope raised on a child story, code opens a fresh sibling issue under its parent.
> 673 The fence lets odd file names and renamed tests through
> 656 The role prompts tell agents to read `AGENTS.md` only; after the split they should also read the topic files it links.
> 619 A story filed by an earlier split and left out of the re-plan stays an open sub-issue, so the parent never closes.
> 609 Follow-up to #560: latest comment wins, split stories stay in records, byte-exact ask fold, one-write card, queue removal, stage-bound API use, trigger test cleanup.
> 573 A split issue's acceptance criteria are its stories merging, in the same criterion shape as every card
> 551 The prompt asks a split's criteria to carry edge cases too, but the plan c

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def problems_searched" -A30 dokima/agent.py | head -45
```

> (Bash completed with no output)

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "searched must list" dokima/ | head; grep -rn "symptom, root cause or new" -B25 dokima/*.py | grep -n "searched\|verdict\|def " | head -20
```

> (Bash completed with no output)

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "root cause or new\|\"searched\"\|'searched'" --include=*.py . | head
```

> dokima/raises.py:23:SEARCHED = "searched"
> tests/test_symptoms_join_cause.py:4:symptom, root cause or new (#622). This story makes the first two verdicts do what the owner asked:
> tests/test_symptoms_join_cause.py:46:    found = {**settles.issue_raise("reviewer", "R1"), "searched": SEARCHED, **fields}
> tests/test_symptoms_join_cause.py:55:    yes = {**settles.answer("W1", "done", "Real: closed PRs stay in Review."), "searched": SEARCHED, **fields}
> tests/test_reviewer_open_issues.py:15:- An issue raise in a review may carry "searched", a list of issue numbers. `agent check review FILE PLAN N` accepts
> tests/test_reviewer_open_issues.py:16:  it, and `agent check-round reviewer FILE PACK` rejects (exit 1) a review whose "searched" names a number that is
> tests/test_reviewer_open_issues.py:17:  not in PACK/open_issues.json, naming that number and saying it is not in the pack; it rejects "searched" that is not
> tests/test_reviewer_open_issues.py:199:    return review("approve", "pr", raises=[{**FOUND, "searched": searched, "verdict": "new"}])
> tests/test_reviewer_open_issues.py:249:        assert code == 1 and "searched" in out, \
> tests/test_reviewer_verdict.py:9:- A reviewer's own issue raise carries "searched", a non-empty list of open issue numbers from its pack (#621 already

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['summary']="All five tests fail today for the right reason; only the code owners question waits for the owner."
d['answers'][0].update({"searched":[800,725,551,432],"verdict":"new"})
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 815 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#815](https://github.com/dokima-dev/dokima/issues/815) (wiki install page uses the thin workflow). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Criteria:** the plan now has five, one for each of the owner's asks on the issue. Two are new since the last round: the folder rule now fails whatever the verb, and the page must list none of Dokima's own workflows.
- **Tests:** I ran all five. Each fails today because the page hasn't changed yet, not because the test is broken, and each failure names its criterion.
- **Earlier blockers:** both of my last-round blockers are done. The folder test no longer only looks for the word "copy", and criteria 815.2 to 815.5 now cover what the story asks for.
- **Planner's issue (P3):** I answered it done and marked it new. The planner reported that criteria sharing only a markdown file can't be grouped into one story, and that is true in the planner code. I checked open issues [#800](https://github.com/dokima-dev/dokima/issues/800) (breaking documents into stories), [#725](https://github.com/dokima-dev/dokima/issues/725) (split stories), [#551](https://github.com/dokima-dev/dokima/issues/551) (edge cases on a split) and [#432](https://github.com/dokima-dev/dokima/issues/432) (split depth), and none covers it.
- **Still waiting for the owner:** the planner's question P2, whether the code owners step stays on the page. I left it unanswered because the owner's words lean against it ("Nothing else"), and dropping it would change how Dokima works.

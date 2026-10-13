# reviewer (plan) for #622

Run: https://github.com/dokima-dev/dokima/actions/runs/38481444489

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
> # Issue #622: The reviewer records its search and verdict
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 621 -->
> <!-- dokima-blocking: {"blocked_by": [621], "blocks": [623], "loop": []} -->
> Every issue the reviewer files names the open issues it searched and its verdict, or is rejected.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/622#issuecomment-6156951015) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/621
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/623
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/615
> 
> 
> **User story:** Every issue the reviewer files names the open issues it searched and why it was filed.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/doki

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 12000; echo; head -c 3000 open_issues.json; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(d.keys());print(json.dumps(d.get('check') or d.get('verdict'),indent=1)[:2000])"
```

> {"number": 615}
> [
>  {
>   "number": 631,
>   "title": "The command copies how the card collects its data instead of calling the branch's own step, so a branch changing that step is not shown.",
>   "summary": "The command copies how the card collects its data instead of calling the branch's own step, so a branch changing that step is not shown.",
>   "link": "https://github.com/dokima-dev/dokima/issues/631",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 628,
>   "title": "A test holds the drawing code to every fixture",
>   "summary": "An approved visual stays exactly as approved, because a test fails on any difference.",
>   "link": "https://github.com/dokima-dev/dokima/issues/628",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 627,
>   "title": "Approving a preview freezes it as a fixture",
>   "summary": "An approved drawing is kept with the data it came from, and its approval is on record.",
>   "link": "https://github.com/dokima-dev/dokima/issues/627",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 626,
>   "title": "The command shows what changed, and real checks run nightly",
>   "summary": "We see only the lines a change moves, and real GitHub checks never slow a pull request.",
>   "link": "https://github.com/dokima-dev/dokima/issues/626",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 625,
>   "title": "The command previews its drawing on the gallery repo",
>   "summary": "We see GitHub's real rendering of a change on the private gallery, with no noise here.",
>   "link": "https://github.com/dokima-dev/d

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -15; git show --stat HEAD | head -30; grep -rn "615\|621" --include=*.py tests dokima | head -20
```

> 98d6a0b planner for #622 (run 38481018187)
> 25d6bd8 The reviewer's pack lists the open issues (#629)
> 71e8ad3 A re-approved split files its new stories (#618)
> a9701dc The planner starts from its branch with main merged in (#607)
> 9748f5a Merge gate tests the combined code, then the owner approves (#606)
> eab04bf The setup audit says whether auto-merge is on (#603)
> 9fd9fcb The worker cannot finish until its plan tests pass (#598)
> 10c8ac3 Autopilot only tries to merge; GitHub decides (#592)
> 9be16aa An agent's manual fix opens as Dokima's app (#590)
> 507df86 The planner names the issue: its hand-back carries a title that code sets on approval (#576)
> ec45283 Autopilot reads main's required checks from the branch, which the app may read (#578)
> 3d03385 A repo setting lets a passed code review approve the merge; owner approval stays the default (#570)
> 827ab8d Stop crediting the unrelated GitHub user "dokima" on commits (#568)
> 8ca3d57 The pitch test checks the pitch, not the project's spelling (#575)
> 98b622b Update branding from Dokima to δokima (#565)
> commit 98d6a0bae9178eb1aec32f6e698cc1d68df4ff0c
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 22:59:41 2026 +0000
> 
>     planner for #622 (run 38481018187)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_reviewer_open_issues.py |   4 +-
>  tests/test_reviewer_verdict.py     | 198 +++++++++++++++++++++++++++++++++++++
>  2 files c

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_reviewer_verdict.py; git show HEAD -- tests/test_reviewer_open_issues.py
```

> """Every issue the reviewer files names the open issues it searched and its verdict (#622).
> 
> Story 2 of #615. Before an issue is filed from a raise, the owner wants the reviewer to record two decisions in its
> JSON hand-back, and code to reject a filing without them: the open issues it searched for the same cause, and its
> verdict, one of symptom (of a known cause), root cause (found) or new. The verdict and its evidence then show on the
> filed issue, so the owner sees why it was filed.
> 
> What the code these tests run must do, as the plan pins it:
> - A reviewer's own issue raise carries "searched", a non-empty list of open issue numbers from its pack (#621 already
>   checks each number is in the pack), and "verdict", exactly one of "symptom", "root cause" or "new".
> - A review that answers done to an issue the planner or the worker raised files that issue, so its answer carries the
>   same two fields; an answer of disagree files nothing and needs neither.
> - The checks a review's run does (`agent check review FILE PLAN N`, then `agent check-round reviewer FILE PACK`) reject
>   (exit 1) a review that files an issue without them, naming the missing or wrong field, and never crash. A review
>   that files nothing needs neither field.
> - The issue code files shows the verdict on a line naming it ("Symptom of a known cause", "Root cause found" or "New"),
>   the searched issues as #N on a line naming them, and the raise's evidence.
> 
> The checks run as subprocesses against a pack built from a fake

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_reviewer_verdict.py tests/test_reviewer_open_issues.py 2>&1 | grep -E "^(FAILED|PASSED|E  )|passed|failed" | head -40
```

> >       passed(tmp_path, own(searched=SEARCHED, verdict="new"), pack, "622.1", "a review naming the issues it searched")
>     def passed(tmp_path, handback, pack, criterion, what):
> E       AssertionError: 622.1: a review naming the issues it searched was rejected:
> E         raise 1 carries fields no raise has: verdict
> E         
> E       assert 1 == 0
>         passed(tmp_path, confirming(searched=SEARCHED, verdict="new"), pack, "622.1",
>         passed(tmp_path, confirming("disagree"), pack, "622.1", "a review disagreeing with W1, filing nothing")
> >       assert code == 1, f"{criterion}: {what} passed the review's checks"
> E       AssertionError: 622.1: a review confirming W1 with no searched issues passed the review's checks
> E       assert 0 == 1
> >           passed(tmp_path, own(searched=SEARCHED, verdict=verdict), pack, "622.2", f"the verdict {verdict!r}")
>     def passed(tmp_path, handback, pack, criterion, what):
> E       AssertionError: 622.2: the verdict 'symptom' was rejected:
> E         raise 1 carries fields no raise has: verdict
> E         
> E       assert 1 == 0
>         passed(tmp_path, confirming(searched=SEARCHED, verdict="root cause"), pack, "622.2",
> >       assert code == 1, f"{criterion}: {what} passed the review's checks"
> E       AssertionError: 622.2: a review confirming W1 with no verdict passed the review's checks
> E       assert 0 == 1
> E       AssertionError: 622.3: the filed issue does not show why it was filed: ["no line shows the verdict 'new' (verdict lines: [])

**Agent:** Tests fail today for the right reason. Now checking the owner's words in #615 and the planner's question.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,30p tests/test_reviewer_open_issues.py; git log --all --format=%B | grep -n -i "same cause\|symptom" | head; grep -rn "def file_issues" -A40 dokima/agent.py | head -60
```

> """The reviewer starts with every open issue, and names only those as searched (#621).
> 
> Story 1 of #615. Before the reviewer files an issue it must search the open issues for the same cause; the owner asked
> that code build what this needs before the run: the open issues with their titles, summaries and links, and which ones
> Dokima filed, so the reviewer searches that and not GitHub live.
> 
> What the code these tests run must do, as the plan pins it:
> - `agent.pack(repo, n, "reviewer", stage, dest)`, for the plan review (stage "plan") and the code review (stage "pr"),
>   writes dest/open_issues.json: a list with one object per open issue of the repo (pull requests left out, every page),
>   each with "number", "title", "summary", "link" (the issue's page on GitHub) and "filed_by_dokima" (true or false).
> - An issue's summary is the sentence its card opens with, the plan's summary, when its card has one; otherwise the
>   user story of a split's story; otherwise the first sentence of the owner's ask; an empty body gives "".
> - An issue counts as filed by Dokima when Dokima's bot opened it (its author is `dokima-runtime[bot]`).
> - When GitHub cannot list the open issues, the reviewer's pack fails with GitHub's error and writes no open_issues.json.
> - An issue raise in a review may carry "searched", a list of issue numbers. `agent check review FILE PLAN N` accepts
>   it, and `agent check-round reviewer FILE PACK` rejects (exit 1) a review whose "searched" names a number that is
>   not in PACK/

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -i "open_issues\|searched\|verdict" dokima/roles/reviewer.md | head; ls dokima/roles; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'))
for i in d: print(i['number'],i['title'][:110])"
```

> 15:The issue as the owner wrote it, with its Context; the planner's plan.json; the checker's verdict on it; the repo with the
> 113:   "verdict": "approve" | "block" | "escalate",
> plan-grade.md
> planner.md
> result-grade.md
> reviewer.md
> style.md
> worker.md
> 631 The command copies how the card collects its data instead of calling the branch's own step, so a branch changi
> 628 A test holds the drawing code to every fixture
> 627 Approving a preview freezes it as a fixture
> 626 The command shows what changed, and real checks run nightly
> 625 The command previews its drawing on the gallery repo
> 624 One command draws Dokima's posts from any branch
> 623 Symptoms join their cause instead of a new issue
> 622 The reviewer records its search and verdict
> 620 A check that ran before plan approval stays failed when the app cannot re-run workflows, so every merge gate f
> 619 A story filed by an earlier split and left out of the re-plan stays an open sub-issue, so the parent never clo
> 615 Reviewer checks if a raised issue shares a known cause
> 614 The board follows stage changes, with no sweeps
> 613 The card is drawn from record files at stage changes
> 612 The owner's words are quoted and kept as first written
> 611 Run comments show the record, never its raw data
> 610 Each run's record is saved as its own file
> 609 Follow-up to #560: latest comment wins, split stories stay in records, byte-exact ask fold, one-write card, qu
> 605 Other tests still fake the `DOKIMA_AUTO_MERGE` variable read, which no code makes now

**Agent:** The plan holds up. Writing the hand-back.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria, each with two tests, or one plus a second case.",
           "The planner updated three older tests so their sample reviews give a verdict."],
  "decided": ["Issues the reviewer confirms for the planner or worker also need the search and verdict."],
  "open": ["The planner asked whether confirmed issues need the search and verdict too."]},
 "verdict": "approve",
 "summary": "The plan covers all three asks, and every new test fails today because the feature is missing.",
 "raises": [],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "The owner wants any filing without these decisions rejected, and a confirmed issue is a filing too.",
   "words": "Its hand-back records these decisions, and code rejects a filing without them",
   "source": "https://github.com/dokima-dev/dokima/issues/615", "changes": false},
  {"raise": "P2", "answer": "done", "why": "Confirmed: the reviewer's prompt never names the open issues list, searched or verdict, and this issue may not edit it."}
 ],
 "asks": [
  {"ask": "the open issues it checked for the same cause, listed.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "622.1"},
  {"ask": "Its hand-back records these decisions, and code rejects a filing without them", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "622.2"},
  {"ask": "The verdict and its evidence show on the issue, so I can see why it was filed, linked or grouped.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "622.3"}
 ],
 "behaviors": [
  {"criterion": "622.1", "one_behavior": true, "why": "One rejection: a filing with no searched issues."},
  {"criterion": "622.2", "one_behavior": true, "why": "One rejection: a filing with no valid verdict."},
  {"criterion": "622.3", "one_behavior": true, "why": "One filed issue body showing why it was filed."}
 ],
```

> exit 0

**Agent:** I approved the plan for #622 (the reviewer records which open issues it searched and its verdict). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Tests:** I ran all six new tests and each fails today only because the feature is missing. They reject a review that leaves out the searched issues or gives no valid verdict, and they check that the filed issue's text shows the verdict, the searched issues and the evidence. Each rejection test also checks that a correct review still passes.
- **Older tests:** three tests from [#621](https://github.com/dokima-dev/dokima/issues/621) (the reviewer's pack lists the open issues) also fail on this branch for now. The planner edited them on purpose to add a verdict to their sample reviews, so they will pass once the work is built.
- **Owner's asks:** the three asks quoted from [#615](https://github.com/dokima-dev/dokima/issues/615) (checking whether a raised issue shares a known cause) each map to one criterion. Each criterion is one behaviour, and the size is ok.
- **The planner's question:** it asked whether issues the reviewer confirms for the planner or worker must also carry the search and verdict. The issue is on autopilot, so I answered it for you as "yes": [#615](https://github.com/dokima-dev/dokima/issues/615) says "code rejects a filing without them", and a confirmed issue is a filing too. One caveat: I couldn't open #615 from here, so the quote is the one the planner used, which code checked when it accepted the plan. Code checks the quote again when it reads this review.
- **The planner's raised issue:** I confirmed it. The reviewer's prompt never mentions the open-issues list, the searched issues or the verdict. This issue isn't allowed to change that prompt, so it should be its own issue.

I raised no blockers.

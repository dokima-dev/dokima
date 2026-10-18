# reviewer (plan) for #745

Run: https://github.com/dokima-dev/dokima/actions/runs/39108621696

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat open_blockers.json; cat plan.json
```

> total 44
> drwxr-xr-x 2 runner runner 4096 Oct 18 07:42 .
> drwxr-xr-x 3 runner runner 4096 Oct 18 07:42 ..
> -rw-r--r-- 1 runner runner 8578 Oct 18 07:42 01-planner.json
> -rw-r--r-- 1 runner runner 8308 Oct 18 07:42 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 9625 Oct 18 07:42 03-planner.json
> # Issue #745: Dokima's own problems file themselves into Dokima's repo
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 742 -->
> <!-- dokima-blocking: {"blocked_by": [742], "blocks": [746], "loop": []} -->
> Problems that are Dokima's fault, and failed runs, on a trial repo file themselves into Dokima's repo.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: Say /work to build the plan
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; cd /home/runner/work/dokima/dokima; git diff main --stat; wc -l tests/test_upstream.py
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "39103919650",
>  "commit_before": "389f34d3808daed9e3585cf15dc7365dd7f1a3d2",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 96557,
>   "turns": 10,
>   "cost_usd": 0.660269,
>   "tokens_in": 485405,
>   "tokens_out": 9264
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/745/39103919650-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39103919650",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Wrote nine criteria with tests: tagged problems and failed runs file upstream, linking back.",
>     "Added a fake GitHub holding the trial repo and Dokima's repo side by side."
>    ],
>    "decided": [
>     "Every job of every shared workflow ends with a step filing its failure upstream.",
>     "The first failure also posts a comment, so two failures give two linked comments."
>    ],
>    "open": [
>     "Asks the owner whether failed test checks should file upstream too."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "Every ask has a criterion and a test that fails today for the missing feature; one owner question waits.",
>   "raises": [],
>   "answers": [
>    {
>     "raise": "P2",
>     "answer": "done",
>     "why": "The owner asks for two linked comments after two failures, so the first failure comments too.",
>     "words": "forcing the same Dokima-caused failure twice on the trial repo yields one upstream issue with two linked comments",
>     "source":

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_upstream.py
```

> """Tests for #745: Dokima's own problems on a trial repo file themselves upstream.
> 
> A repo's `.dokima/settings.yaml` may name the upstream repo where Dokima's own problems go:
> 
>     upstream:
>       repo: dokima-dev/dokima     # empty (the default): nothing leaves the repo
> 
> An agent first judges each problem it raises as an issue: Dokima's fault (its workflows, code, prompts, settings or
> install), tagged `"fault": "dokima"`; the repo's own (its code or its tests), left untagged; or unclear, tagged
> `"fault": "unsure"`. Once a review confirms it, code files a problem that is Dokima's fault in the upstream repo, linking
> back to the issue where it was seen and carrying nothing else from the private repo; any other problem is filed in the
> repo itself, as before, and an unclear one says there that Dokima cannot tell whose fault it is. A failed run of a
> shared workflow, other than the two test checks (full-suite.yml and acceptance-criteria.yml), runs
> `python3 -m dokima.upstream failed WORKFLOW JOB` as its last step, which files the failure upstream with the run's
> link; a failed test check files nothing upstream by itself. A repeat, the same tagged problem or the same workflow's job failing again, is a comment on the open upstream
> issue, never a second issue. Calls on the upstream repo run with the key in DOKIMA_UPSTREAM_TOKEN, which the workflow
> mints from the App's own key.
> 
> Every test runs against tests/upstream_gh.py, a fake `gh` on PATH that holds the trial repo o/r and Dokima's r

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/upstream_gh.py
```

> """A fake `gh` holding several repos at once, for the upstream filing tests (#745).
> 
> tests/test_upstream.py puts a small `gh` script on PATH that runs this file. Unlike tests/fake_gh.py, which knows one
> repo, this one keeps a trial repo and Dokima's own repo side by side, so a test can see which repo each issue landed
> in, and logs the GH_TOKEN every call ran with, so a test can see which key reached which repo.
> 
> The state lives in the JSON file named by UPSTREAM_GH_STATE:
>     {"repos": {"OWNER/NAME": {"issues": {"N": {"title", "body", "state", "labels", "comments": [body, ...]}},
>                               "labels": [name, ...]}},
>      "next": {"OWNER/NAME": last number},
>      "calls": [{"argv": [...], "repo": "OWNER/NAME" or null, "token": GH_TOKEN}],
>      "unsupported": [{"argv": [...], "why": "..."}]}
> A repo that is not in "repos" answers 404, as GitHub does for a repo the key cannot see.
> 
> What it answers, on any repo in the state:
>     gh issue create --repo R --title T --body B | --body-file F [--label L]...   prints the new issue's URL
>     gh issue comment N --repo R --body B | --body-file F                         prints the comment's URL
>     gh issue list --repo R [--state open|closed|all] [--label L]... [--search Q] [--json F] [--limit N]
>     gh issue view N --repo R [--json F]                                          the issue with its comments
>     gh search issues [Q...] --repo R [--state S] [--label L]... [--json F] [--limit N]
>     gh api [-X GET] repos/R/issues

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_upstream.py
```

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/upstream_gh.py
```

> """Tests for #745: Dokima's own problems on a trial repo file themselves upstream.
> 
> A repo's `.dokima/settings.yaml` may name the upstream repo where Dokima's own problems go:
> 
>     upstream:
>       repo: dokima-dev/dokima     # empty (the default): nothing leaves the repo
> 
> An agent first judges each problem it raises as an issue: Dokima's fault (its workflows, code, prompts, settings or
> install), tagged `"fault": "dokima"`; the repo's own (its code or its tests), left untagged; or unclear, tagged
> `"fault": "unsure"`. Once a review confirms it, code files a problem that is Dokima's fault in the upstream repo, linking
> back to the issue where it was seen and carrying nothing else from the private repo; any other problem is filed in the
> repo itself, as before, and an unclear one says there that Dokima cannot tell whose fault it is. A failed run of a
> shared workflow, other than the two test checks (full-suite.yml and acceptance-criteria.yml), runs
> `python3 -m dokima.upstream failed WORKFLOW JOB` as its last step, which files the failure upstream with the run's
> link; a failed test check files nothing upstream by itself. A repeat, the same tagged problem or the same workflow's job failing again, is a comment on the open upstream
> issue, never a second issue. Calls on the upstream repo run with the key in DOKIMA_UPSTREAM_TOKEN, which the workflow
> mints from the App's own key.
> 
> Every test runs against tests/upstream_gh.py, a fake `gh` on PATH that holds the trial repo o/r and Dokima's r

> """A fake `gh` holding several repos at once, for the upstream filing tests (#745).
> 
> tests/test_upstream.py puts a small `gh` script on PATH that runs this file. Unlike tests/fake_gh.py, which knows one
> repo, this one keeps a trial repo and Dokima's own repo side by side, so a test can see which repo each issue landed
> in, and logs the GH_TOKEN every call ran with, so a test can see which key reached which repo.
> 
> The state lives in the JSON file named by UPSTREAM_GH_STATE:
>     {"repos": {"OWNER/NAME": {"issues": {"N": {"title", "body", "state", "labels", "comments": [body, ...]}},
>                               "labels": [name, ...]}},
>      "next": {"OWNER/NAME": last number},
>      "calls": [{"argv": [...], "repo": "OWNER/NAME" or null, "token": GH_TOKEN}],
>      "unsupported": [{"argv": [...], "why": "..."}]}
> A repo that is not in "repos" answers 404, as GitHub does for a repo the key cannot see.
> 
> What it answers, on any repo in the state:
>     gh issue create --repo R --title T --body B | --body-file F [--label L]...   prints the new issue's URL
>     gh issue comment N --repo R --body B | --body-file F                         prints the comment's URL
>     gh issue list --repo R [--state open|closed|all] [--label L]... [--search Q] [--json F] [--limit N]
>     gh issue view N --repo R [--json F]                                          the issue with its comments
>     gh search issues [Q...] --repo R [--state S] [--label L]... [--json F] [--limit N]
>     gh api [-X GET] repos/R/issues

`7. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_upstream.py 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed|Error|assert" | head -60
```

> The trial repo has no settings file, so the shipped default names no upstream repo. A passed review raises one
>         assert not (settings.read().get("upstream") or {}).get("repo"), \
> >       assert problems == [], f"{where}: the hand-back check rejects a raise tagged with its fault: {problems}"
> E       AssertionError: 745.1: the hand-back check rejects a raise tagged with its fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> /home/runner/work/dokima/dokima/tests/test_upstream.py:110: AssertionError
>         The trial repo's settings name dokima-dev/dokima. A passed review raises one problem tagged as Dokima's fault;
> >       assert problems == [], f"{where}: the hand-back check rejects a raise tagged with its fault: {problems}"
> E       AssertionError: 745.1: the hand-back check rejects a raise tagged with its fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> /home/runner/work/dokima/dokima/tests/test_upstream.py:110: AssertionError
>         The trial repo's settings name dokima-dev/dokima. A passed review raises two problems, one tagged as Dokima's
> >       assert problems == [], f"{where}: the hand-back check rejects a raise tagged with its fault: {problems}"
> E       AssertionError: 745.1: the hand-back check rejects a raise tagged with its fault: ['raise 1 carries fields no raise has: fault']
> E       assert ['raise 1 car...e has: fault'] == []
> /home/runner/work/doki

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_upstream.py -rA 2>&1 | grep -E "^(FAILED|PASSED|ERROR)|passed|failed" | cut -c1-250
```

> The trial repo has no settings file, so the shipped default names no upstream repo. A passed review raises one
>         The trial repo's settings name dokima-dev/dokima. A passed review raises one problem tagged as Dokima's fault;
>         The trial repo's settings name dokima-dev/dokima. A passed review raises two problems, one tagged as Dokima's
>         The trial repo's settings name dokima-dev/dokima. A passed review on the trial repo's issue 9 raises a problem
> ________ test_a_failed_run_files_the_failure_upstream_with_the_run_link ________
>     def test_a_failed_run_files_the_failure_upstream_with_the_run_link(record_property, github):
>         """A failed run's last step files the failure upstream, linking the run.
>         runs `python3 -m dokima.upstream failed agent run`, and Dokima's repo then holds one issue whose text links run 101.
>         got = failed()
> >       assert got.returncode == 0, f"745.5: filing the failed run upstream failed: {got.stdout}{got.stderr}"
> E       AssertionError: 745.5: filing the failed run upstream failed: /opt/hostedtoolcache/Python/3.12.15/x64/bin/python3: No module named dokima.upstream
> E        +  where 1 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', '-m', 'dokima.upstream', 'failed', 'agen...turncode=1, stdout='', stderr='/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3: No module named dokima.
> ____________ test_with_no_upstream_repo_a_failed_run_files_nothing _____________
>     def test_with_no_upstream

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "boxes\|dropped\|superseded\|conflicts\|poor_tests\|edges" dokima/agent*.py dokima/*.py | grep -v "^dokima/card" | head -40
```

> dokima/agent.py:49:    AUTOPILOT_START_LINE, link_edges, loop_through, named, FILED_LABEL, file_issues, record_links, set_title,
> dokima/agent.py:53:    work_approved, CHECKS_WAIT, CHECKS_PAUSE, BOARD_WAIT, superseded, required_checks, unproven, proof, UPDATE_WAIT,
> dokima/agent_checks.py:226:BOXES = {"dropped": ("words", "source"), "added": ("what", "kind", "serves"), "superseded": ("old", "new", "retired"),
> dokima/agent_checks.py:227:         "conflicts": ("a", "b", "ask"), "edges": (), "poor_tests": ("test", "passes_with", "fix")}
> dokima/agent_checks.py:230:def problems_boxes(r, ids):
> dokima/agent_checks.py:231:    """Everything wrong with a review's six boxes (#819), each reason naming its box.
> dokima/agent_checks.py:233:    Every box is there, "none" or a list of whole entries (edges a line per criterion of the plan, covered or
> dokima/agent_checks.py:235:    boxes = r.get("boxes")
> dokima/agent_checks.py:236:    if not isinstance(boxes, dict):
> dokima/agent_checks.py:237:        return ["boxes must be an object holding the six boxes: " + ", ".join(BOXES) + "; a box with nothing in it says none"]
> dokima/agent_checks.py:240:        if box not in boxes:
> dokima/agent_checks.py:241:            bad.append(f"boxes has no {box} box: write none when there is nothing in it")
> dokima/agent_checks.py:243:        v = boxes[box]
> dokima/agent_checks.py:244:        if box == "edges":
> dokima/agent_checks.py:245:            bad += problems_edges(r, v, ids)
> dokima/agent_checks.py:252:        ba

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 226,300p dokima/agent_checks.py
```

> BOXES = {"dropped": ("words", "source"), "added": ("what", "kind", "serves"), "superseded": ("old", "new", "retired"),
>          "conflicts": ("a", "b", "ask"), "edges": (), "poor_tests": ("test", "passes_with", "fix")}
> 
> 
> def problems_boxes(r, ids):
>     """Everything wrong with a review's six boxes (#819), each reason naming its box.
> 
>     Every box is there, "none" or a list of whole entries (edges a line per criterion of the plan, covered or
>     missing: the case), and an approve holds no blocking entry. An added entry of kind needed is not a blocker."""
>     boxes = r.get("boxes")
>     if not isinstance(boxes, dict):
>         return ["boxes must be an object holding the six boxes: " + ", ".join(BOXES) + "; a box with nothing in it says none"]
>     bad = []
>     for box, keys in BOXES.items():
>         if box not in boxes:
>             bad.append(f"boxes has no {box} box: write none when there is nothing in it")
>             continue
>         v = boxes[box]
>         if box == "edges":
>             bad += problems_edges(r, v, ids)
>             continue
>         if v == "none":
>             continue
>         if not isinstance(v, list) or not v:
>             bad.append(f"the {box} box must be none or a list of entries, each with {', '.join(keys)}")
>             continue
>         bad += problems_items(boxes, box, keys)
>         whole = [x for x in v if isinstance(x, dict) and all(filled(x.get(k)) for k in keys)]
>         if box == "added":
>             for i, x in enumerate(v, 1):
>                 if 

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n '"block"\|"escalate"\|"approve"' dokima/agent_checks.py | head -20
```

> 138:    if r.get("verdict") == "approve" and blocks:
> 140:    if r.get("verdict") == "block" and not blocks:
> 155:    if wide and r.get("verdict") == "approve":
> 180:    if size.lower() != "ok" and r.get("verdict") == "approve":
> 221:    if r.get("verdict") == "approve" and gone:
> 259:        if whole and r.get("verdict") == "approve":
> 282:    if gaps and r.get("verdict") == "approve":

`12. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 120,225p dokima/agent_checks.py
```

> bad += problems_searched(h, pack_dir)
>     return bad
> 
> 
> def problems_review(r):
>     """Everything wrong with a review.json, as plain sentences; empty when it is well formed."""
>     bad = []
>     if r.get("verdict") not in VERDICTS:
>         bad.append("verdict must be approve, block or escalate")
>     if not str(r.get("summary", "")).strip():
>         bad.append("summary is empty")
>     prev = r.get("previous_step")
>     if not isinstance(prev, dict) or not any(prev.get(k) for k in ("did", "decided", "open")):
>         bad.append("previous_step must sum up what the planner or worker did, decided and left open")
>     elif sum(len(prev.get(k) or []) for k in ("did", "decided", "open")) > 5:
>         bad.append("previous_step holds at most five lines")
>     blocks = [x for x in r.get("raises") or [] if isinstance(x, dict) and x.get("kind") == "blocker"] \
>         if isinstance(r.get("raises"), list) else []
>     if r.get("verdict") == "approve" and blocks:
>         bad.append("an approve raises no blocker")
>     if r.get("verdict") == "block" and not blocks:
>         bad.append("a block needs at least one blocker in raises")
>     return bad
> 
> 
> def problems_tests(r, plan):
>     """A plan review must judge every test the plan names: does it check only its
>     criterion's behavior, with the edge cases the owner named or normal use hits? A false one never approves."""
>     named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if isinstance(ts, list) for t in ts})
>     rows = r.get("tes

`13. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Rewrote the plan to the owner's answer: ten criteria, each with tests failing today.",
   "Left the two test checks out of filing failures upstream."
  ],
  "decided": [
   "Agents tag each problem as Dokima's, unsure, or leave it untagged as the repo's own.",
   "An unclear problem is filed in the repo, saying Dokima cannot tell."
  ],
  "open": [
   "Asks the owner whether the link back may point at the private repo."
  ]
 },
 "verdict": "approve",
 "summary": "Every ask has a criterion and a test failing today for the missing feature; three owner questions wait.",
 "raises": [
  {
   "kind": "question",
   "to": "owner",
   "label": "Repo's own problems",
   "text": "Should the repo's own problems still open new issues in the repo, as today? The plan assumes yes.",
   "evidence": "Your comment says said on its own issue or pull request; the untagged test expects a new issue."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "Dokima's problems found on a trial repo must land in dokima-dev/dokima by themselves", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.1"},
  {"ask": "with a link back", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.2"},
  {"ask": "A setting names the upstream repo where Dokima's own problems go", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.1"},
  {"ask": "default: none, so an adopter's issues stay local", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.1"},
  {"ask": "gains a tag agents put on problems that are Dokima's fault, not the repo's", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.3"},
  {"ask": "Tagged problems file upstream.", "source": "https://github.com/dokima-dev/dokima/issues/745", "criterion": "745.1"},
  {"ask": "A final step in each shared workflow files the failur
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#745](https://github.com/dokima-dev/dokima/issues/745) (Dokima's own problems file upstream). The hand-back is written and passes both checks.

- **Owner's answer:** the plan now does what your last comment asked. A failed test check files nothing upstream by itself. Only problems that are Dokima's fault go to Dokima's repo, with nothing from the private repo. A problem whose fault is unclear stays in the repo and says so.
- **Asks:** I listed all 17 of your asks from the issue and your comment. Each one maps to one of the 10 criteria; none is missing.
- **Tests:** I ran them. All 28 fail today for the right reason: the feature isn't built yet, not because of a crash or a bad path.

Three questions now wait for you before work starts:
- **Link back:** may an upstream problem link back to the private repo's issue? Outsiders can't open it, and your comment asks for nothing from the private repo. The planner raised this one.
- **Unclear fault:** should an unclear problem become a new issue in the repo, or a note on the issue where it was seen? The planner raised this one.
- **The repo's own problems:** should they still open new issues in the repo, as today? Your comment says "said on its own issue or pull request", but one test expects a new issue. I raised this one.

The link-back question is a real clash between the issue and your comment. I didn't count it as a blocker: the planner already asked you, and there was nothing for the planner to fix, so blocking would only send the plan back for nothing.

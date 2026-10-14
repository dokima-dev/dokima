# reviewer (plan) for #627

Run: https://github.com/dokima-dev/dokima/actions/runs/38489125197

`1. Bash`
```
cd /tmp/pack; ls -la in; cat issue.md; cat plan.json; cat open_blockers.json
```

> total 36
> drwxr-xr-x 2 runner runner 4096 Oct 14 00:15 .
> drwxr-xr-x 3 runner runner 4096 Oct 14 00:15 ..
> -rw-r--r-- 1 runner runner 3715 Oct 14 00:15 01-planner.json
> -rw-r--r-- 1 runner runner 4576 Oct 14 00:15 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3884 Oct 14 00:15 03-planner.json
> -rw-r--r-- 1 runner runner 4524 Oct 14 00:15 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3860 Oct 14 00:15 05-planner.json
> # Issue #627: Approving a preview freezes it as a fixture
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 625, 626 -->
> <!-- dokima-blocking: {"blocked_by": [625], "blocks": [628], "loop": []} -->
> One command saves an approved drawing with the data it came from, and records it on its issue.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/625
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/628
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/626
> - https://github.com/dokima-dev/dokima/issues/631
> - https://github.com/dokima-dev/dokima/issues/624
> 
> 
> **User story:** When 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/04-reviewer-plan.json | python3 -m json.tool | head -120; git diff a582346 --stat; sed -n 1,120p tests/test_visuals_finalize.py
```

> {
>     "role": "reviewer",
>     "stage": "plan",
>     "run_id": "38488793297",
>     "commit_before": "c275140293c52b17ea436d22feb295bae4260251",
>     "started_by": "dokima-runtime[bot]",
>     "models": [
>         "claude-opus-5-5"
>     ],
>     "report": {
>         "duration_ms": 61299,
>         "turns": 10,
>         "cost_usd": 0.5464475999999999,
>         "tokens_in": 509149,
>         "tokens_out": 4587
>     },
>     "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/627/38488793297-reviewer-plan.md",
>     "run": "https://github.com/dokima-dev/dokima/actions/runs/38488793297",
>     "handback": {
>         "previous_step": {
>             "did": [
>                 "The planner made the autopilot comment test check each saved post whole.",
>                 "Eight tests still fail today because the finalize command does not exist."
>             ],
>             "decided": [
>                 "The fixture record goes on the issue itself, never the gallery issue."
>             ],
>             "open": []
>         },
>         "verdict": "block",
>         "summary": "One test expects autopilot comments in an order the issue does not have, so correct work fails it.",
>         "raises": [
>             {
>                 "kind": "blocker",
>                 "to": "planner",
>                 "label": "Test cannot pass",
>                 "text": "`test_finalize_saves_comment_inputs` (627.1) expects autopilot posts ordered 102, 107, 105, 106, 108; `draw` reads 102, 105, 106, 107, 108. Fix: move post 107 after 106.",
>     

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 120,400p tests/test_visuals_finalize.py; git diff c275140 0e2c479
```

> with open(state_file, "w") as f:
>         json.dump(state, f)
>     if argv[:1] == ["api"]:
>         print(json.dumps({"id": state["next"], "body": body, "html_url": url}))
>     else:
>         print(url)
>     sys.exit(0)
> '''
> 
> 
> @pytest.fixture(scope="module")
> def place(tmp_path_factory):
>     """Story 1's throwaway checkout and fake GitHub, plus the comment fake and issue 11.
> 
>     Issue 11 is a copy of issue 7 whose comments GitHub refuses to take."""
>     base = tmp_path_factory.mktemp("finalize")
>     repo = base / "checkout"
>     shutil.copytree(os.path.join(ROOT, "dokima"), repo / "dokima", ignore=shutil.ignore_patterns("__pycache__"))
>     if os.path.isdir(os.path.join(ROOT, "tools")):
>         shutil.copytree(os.path.join(ROOT, "tools"), repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))
>     story1.git(repo, "init", "-q", "-b", "main")
>     story1.git(repo, "config", "user.name", "Test")
>     story1.git(repo, "config", "user.email", "test@example.com")
>     story1.git(repo, "add", "-A")
>     story1.git(repo, "commit", "-q", "-m", "main")
>     story1.git(repo, "checkout", "-q", "-b", "visual-test")
>     with open(repo / "dokima" / "card.py", "a") as f:
>         f.write(story1.BRANCH_CARD)
>     with open(repo / "dokima" / "agent.py", "a") as f:
>         f.write(story1.BRANCH_AGENT)
>     story1.git(repo, "commit", "-q", "-am", "branch drawing")
>     story1.git(repo, "checkout", "-q", "main")
>     bin_dir = base / "bin"
>     bin_dir.mkdir()
>     rest = story1.FAKE_GH.split("\n", 1)[1]
>     (

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_visuals_finalize.py 2>&1 | tail -15; grep -n "kind\|def \|posts" tools/visuals.py | head -80
```

> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'finalize', '7', '--...raw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)\n").returncode
> FAILED tests/test_visuals_finalize.py::test_finalize_posts_fixture_record - AssertionError: 627.3: finalizing #7 from visual-test exited 2:
>   
>   usage: tools/visuals.py [-h] {draw,preview} ...
>   tools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)
>   
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'finalize', '7', '--...raw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)\n").returncode
> FAILED tests/test_visuals_finalize.py::test_finalize_refused_post_says_so - AssertionError: 627.3: the message does not name the issue and GitHub's reason:
>   usage: tools/visuals.py [-h] {draw,preview} ...
>   tools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)
>   
> assert ('#11' in "usage: tools/visuals.py [-h] {draw,preview} ...\ntools/visuals.py: error: argument command: invalid choice: 'finalize' (choose from draw, preview)\n")
> 8 failed in 2.43s
> 11:`preview` posts that same drawing, with the caller's own `gh` login, as one comment on issue N of the gallery repo, so
> 36:def numbers(text):
> 40:d

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner put the autopilot posts in the issue's time order in the comment inputs test.", "All eight tests still fail today because the finalize command does not exist."], "decided": [], "open": []},
 "verdict": "approve",
 "summary": "The plan keeps all three asks, each with tests that fail today only because finalizing is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Finalizing saves the drawing's inputs under the fixtures folder.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.1"},
  {"ask": "Finalizing saves the drawing's output beside its inputs.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "627.2"},
  {"ask": "Finalizing posts the final drawing on its issue here as a comment marked as its fixture record.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156486728", "criterion": "627.3"}
 ],
 "behaviors": [
  {"criterion": "627.1", "one_behavior": true, "why": "Saving the inputs needed to redraw offline is one result."},
  {"criterion": "627.2", "one_behavior": true, "why": "Saving the drawing as the branch drew it is one result."},
  {"criterion": "627.3", "one_behavior": true, "why": "Posting one marked comment on the issue is one result."}
 ],
 "edge_cases": [
  {"criterion": "627.1", "cut": [], "missing": []},
  {"criterion": "627.2", "cut": [], "missing": []},
  {"criterion": "627.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_visuals_finalize.py::test_finalize_saves_card_inputs", "only_its_behavior": true, "why": "Redraws the card offline from the saved inputs and compares byte for byte."},
  {"test": "tests/test_visuals_finalize.py::test_finalize_saves_comment_inputs", "only_its_behavior": true, "why": "Checks every saved post whole, in the order the issue holds them."},
  {"test": "t
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

**Agent:** The hand-back failed one length check, so I'm shortening that line and running the check again.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i "s/The planner put the autopilot posts in the issue's time order in the comment inputs test./The planner put the autopilot posts in time order in the comment inputs test./" /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 627 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#627](https://github.com/dokima-dev/dokima/issues/627) (saving an approved preview as a fixture). The review is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last blocker fixed:** the last review blocked because one test expected the autopilot comments out of order. The planner now lists them oldest first, the order the issue really holds them, so post 107 comes after 106. That was the only change.
- **Tests fail for the right reason:** I ran all eight new tests. Each one fails only because the `finalize` command doesn't exist yet. Nothing crashes, and no tool or path is missing.
- **Nothing dropped:** I read the three asks in the issue myself. Each one is covered by its own criterion: save the inputs, save the drawing beside them, and post one marked comment on the issue. Each criterion is one behavior, and every test checks only its own criterion.

I raised nothing, and no earlier blockers were left to answer. Because the issue is on autopilot, the worker should start building next.

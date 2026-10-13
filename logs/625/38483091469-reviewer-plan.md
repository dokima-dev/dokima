# reviewer (plan) for #625

Run: https://github.com/dokima-dev/dokima/actions/runs/38483091469

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
> # Issue #625: The command previews its drawing on the gallery repo
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624 -->
> <!-- dokima-blocking: {"blocked_by": [624], "blocks": [626, 627], "loop": []} -->
> Our drawing tool posts its drawing to the private gallery repo and keeps editing that one comment.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/624
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/626
> - https://github.com/dokima-dev/dokima/issues/627
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/584
> - https://github.com/dokima-dev/dokima/issues/631
> 
> 
> **User story:** We see GitHub's real rendering of a change on the private gallery, with no noise here.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubuser

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {"number": 584}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38482621140",
>  "commit_before": "61faa9edeb3dd8e4b351252c742cfbe198fb7ce7",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 206637,
>   "turns": 15,
>   "cost_usd": 1.0867368,
>   "tokens_in": 872992,
>   "tokens_out": 19105
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/625/38482621140-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38482621140",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/625#issuecomment-6157150453"
> }
> Shell cwd was reset to /home/runner/work/dokima/dokima

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; wc -l tools/visuals.py tests/test_visuals_preview.py; git show HEAD -- tests/ | head -400
```

> commit d6b9a796af29a36dbc364839f4fdfa36e9422c89
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 23:14:56 2026 +0000
> 
>     planner for #625 (run 38482621140)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_visuals_preview.py | 414 ++++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 414 insertions(+)
>   176 tools/visuals.py
>   414 tests/test_visuals_preview.py
>   590 total
> commit d6b9a796af29a36dbc364839f4fdfa36e9422c89
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 23:14:56 2026 +0000
> 
>     planner for #625 (run 38482621140)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_visuals_preview.py b/tests/test_visuals_preview.py
> new file mode 100644
> index 0000000..94acf36
> --- /dev/null
> +++ b/tests/test_visuals_preview.py
> @@ -0,0 +1,414 @@
> +"""The command previews its drawing as one gallery comment, and keeps editing it.
> +
> +#625.
> +
> +Story 2 of #584. Builds on story 1's `tools/visuals.py draw`. The new subcommand, run from the root of a checkout:
> +
> +    python3 tools/visuals.py preview ISSUE --branch BRANCH --repo OWNER/NAME --gallery-issue N
> +
> +draws exactly what `draw` prints for ISSUE and BRANCH, and posts it, with the caller's own `gh` login, as one comment
> +on issue N of `dokima-dev/card-gallery`. The comment carries a hidden marker na

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 380,414p tests/test_visuals_preview.py; cat tools/visuals.py | head -80; grep -n "FAKE_GH\|HTTP 502\|def world\|BRANCH_CARD\|refuse\|write" tests/test_visuals_draw.py | head -40
```

> assert "BRANCH" not in after[1]["body"] and PLAN_SUMMARY in after[1]["body"], \
>         f"625.2: issue 7's preview was not edited to main's drawing:\n{after[1]['body']}"
> 
> 
> def test_preview_writes_nothing_here(place, record_property):
>     """Previewing writes only to the gallery repo, never to this repo or the real issue.
> 
>     Logs every `gh` call of two previews of issue 7 (a post, then an edit) and checks each call that writes goes to
>     the gallery repo, and that the gallery was in fact written to. Proves 625.3."""
>     record_property("proves", "625.3")
>     p = fresh(place, "nothing")
>     previewed(p, ISSUE, "visual-test", "625.3")
>     previewed(p, ISSUE, "main", "625.3")
>     log = calls(p)
>     here = [shlex.join(["gh", *c]) for c in log if write_call(c) not in (None, GALLERY)]
>     assert not here, "625.3: previewing wrote outside the gallery repo:\n" + "\n".join(here)
>     assert any(write_call(c) == GALLERY for c in log), \
>         "625.3: no write reached the gallery repo, so this check proves nothing:\n" + \
>         "\n".join(shlex.join(["gh", *c]) for c in log)
> 
> 
> def test_failed_preview_writes_nothing_here(place, record_property):
>     """A preview the gallery refuses still writes nothing to this repo.
> 
>     Previews onto a gallery issue that does not exist and checks no logged `gh` call wrote anywhere, so a refused
>     gallery never falls back to the real issue. Proves 625.3."""
>     record_property("proves", "625.3")
>     p = fresh(place, "refused")
>     r = preview(p, IS

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_visuals_preview.py 2>&1 | tail -20; python3 -m pytest -q tests/test_visuals_draw.py 2>&1 | tail -3
```

> usage: tools/visuals.py [-h] {draw} ...
>   tools/visuals.py: error: argument command: invalid choice: 'preview' (choose from draw)
>   
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'preview', '7', '--b...visuals.py [-h] {draw} ...\ntools/visuals.py: error: argument command: invalid choice: 'preview' (choose from draw)\n").returncode
> FAILED tests/test_visuals_preview.py::test_preview_writes_nothing_here - AssertionError: 625.3: previewing #7 from visual-test exited 2:
>   
>   usage: tools/visuals.py [-h] {draw} ...
>   tools/visuals.py: error: argument command: invalid choice: 'preview' (choose from draw)
>   
> assert 2 == 0
>  +  where 2 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', 'tools/visuals.py', 'preview', '7', '--b...visuals.py [-h] {draw} ...\ntools/visuals.py: error: argument command: invalid choice: 'preview' (choose from draw)\n").returncode
> FAILED tests/test_visuals_preview.py::test_failed_preview_writes_nothing_here - AssertionError: 625.3: the command never asked the gallery repo, so this check proves nothing:
>   
>   usage: tools/visuals.py [-h] {draw} ...
>   tools/visuals.py: error: argument command: invalid choice: 'preview' (choose from draw)
>   
> assert False
>  +  where False = any(<generator object test_failed_preview_writes_nothing_here.<locals>.<genexpr> at 0x7fe8eec4bd80>)
> 7 failed in 1.27s
> .......                                                              

**Agent:** Running the plan's tests to confirm each fails because the feature is missing; then I'll write the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_visuals_preview.py 2>&1 | grep -E "^FAILED"
```

> FAILED tests/test_visuals_preview.py::test_preview_posts_one_comment - AssertionError: 625.1: previewing #7 from visual-test exited 2:
> FAILED tests/test_visuals_preview.py::test_preview_missing_gallery_issue_says_so - AssertionError: 625.1: the message does not name the gallery issue and GitHub's reason:
> FAILED tests/test_visuals_preview.py::test_preview_unreadable_issue_posts_nothing - AssertionError: 625.1: the message does not name the issue and GitHub's reason:
> FAILED tests/test_visuals_preview.py::test_preview_again_edits_same_comment - AssertionError: 625.2: previewing #7 from visual-test exited 2:
> FAILED tests/test_visuals_preview.py::test_preview_other_issue_gets_its_own_comment - AssertionError: 625.2: previewing #7 from visual-test exited 2:
> FAILED tests/test_visuals_preview.py::test_preview_writes_nothing_here - AssertionError: 625.3: previewing #7 from visual-test exited 2:
> FAILED tests/test_visuals_preview.py::test_failed_preview_writes_nothing_here - AssertionError: 625.3: the command never asked the gallery repo, so this check proves nothing:

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner planned three criteria for previewing a drawing on the gallery repo, each with tests."],
  "decided": ["A new preview command posts one gallery comment per real issue and edits it on later runs.", "Tests fake GitHub and log every call to prove nothing is written here."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan keeps all three asks of story 2, and each test fails today because the preview command is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "it posts that rendering as one comment on an issue in the private dokima-dev/card-gallery repo", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "625.1"},
  {"ask": "keeps editing that same comment", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "625.2"},
  {"ask": "so I see GitHub's real rendering with no noise on this repo", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6155799768", "criterion": "625.3"}
 ],
 "behaviors": [
  {"criterion": "625.1", "one_behavior": true, "why": "One action: post the drawing as one gallery comment."},
  {"criterion": "625.2", "one_behavior": true, "why": "One result: a rerun edits the same comment."},
  {"criterion": "625.3", "one_behavior": true, "why": "One result: nothing is written to this repo or the real issue."}
 ],
 "edge_cases": [
  {"criterion": "625.1", "cut": [], "missing": []},
  {"criterion": "625.2", "cut": [], "missing": []},
  {"criterion": "625.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_visuals_preview.py::test_preview_posts_one_comment", "only_its_behavior": true, "why": "Checks exactly one new comment holding what draw prints for the branch."},
  {"test": "tests/test_visuals_preview.py::test_preview_missing_gallery_issue_says_so", "only_its_behavior": true, "why": "Checks a mi
```

> Exit code 1
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`8. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
d=json.load(open('review.json'))
d['previous_step']['did']=["The planner planned three criteria for previewing a drawing on the gallery, with tests."]
d['previous_step']['decided'][0]="A new preview command posts one gallery comment per issue, edited on reruns."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 625 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#625](https://github.com/dokima-dev/dokima/issues/625) (previewing a drawing on the gallery repo). The review is in `/tmp/dokima-out/review.json`, and it passes both hand-back checks.

- **Asks:** all three of story 2's asks from [#584](https://github.com/dokima-dev/dokima/issues/584) (previewing visuals and freezing approved fixtures) have their own criterion: post one gallery comment, edit that same comment on later runs, and write nothing to this repo. None is missing.
- **Tests:** I ran all 7 new tests on this branch. Each fails because the `preview` command doesn't exist yet in `tools/visuals.py`, not because of a crash or a bad path. Story 1's tests still pass.
- **Strength:**
  - One test previews two issues onto one gallery issue. Code that just edits its last comment would fail it, so the work has to use a marker for each issue.
  - The two "writes nothing here" tests also check that a write did reach the gallery, so they can't pass when nothing happens.
- **Size:** fine. Each criterion is one behavior, and I found no edge cases to cut or add.

I raised nothing and had no open blockers to answer.

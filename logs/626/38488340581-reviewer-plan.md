# reviewer (plan) for #626

Run: https://github.com/dokima-dev/dokima/actions/runs/38488340581

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
> # Issue #626: The command shows what changed, and real checks run nightly
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 624, 625 -->
> <!-- dokima-blocking: {"blocked_by": [624, 625], "blocks": [], "loop": []} -->
> Our drawing tool shows only the lines a branch changes, and its real GitHub checks run at night.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/624
> - https://github.com/dokima-dev/dokima/issues/625
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/627
> - https://github.com/dokima-dev/dokima/issues/631
> - https://github.com/dokima-dev/dokima/issues/258
> 
> 
> **User story:** We see only the lines a change moves, and real GitHub checks never slow a pull request.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The comma

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; cat tests/test_visuals_diff.py; ls tools nightly .github/workflows
```

> Exit code 2
> {"number": 584}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38487907894",
>  "commit_before": "a582346d2600cca5a72a2db43ee59f4bc2ff41f9",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 214911,
>   "turns": 22,
>   "cost_usd": 1.3954143999999997,
>   "tokens_in": 1595083,
>   "tokens_out": 21548
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/626/38487907894-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38487907894",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/626#issuecomment-6157803035"
> }
> """The command shows what a branch changes; real GitHub checks run only at night.
> 
> #626.
> 
> Story 3 of #584. Builds on `tools/visuals.py draw` (#624) and `preview` (#625).
> 
> 1. A new subcommand, run from the root of a checkout:
> 
>        python3 tools/visuals.py diff ISSUE --branch BRANCH --repo OWNER/NAME
> 
>    draws the issue exactly as `draw` does twice, once with main's code and once with BRANCH's, and prints only the
>    lines that differ as a unified diff: main's lines start with `-`, BRANCH's with `+`, every line both drawings share
>    is left unmarked or out. When nothing differs it prints `No line differs from main.` and exits 0. An issue GitHub
>    cannot give ends it with a non-zero exit and one plain message naming the issue, never a traceback.
> 
> 2. Checks that post to or read from real GitHub (the card-gallery previews) l

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 60,200p tests/test_visuals_diff.py; timeout 600 python3 -m pytest -q tests/test_visuals_diff.py 2>&1 | tail -30
```

> """#624's throwaway checkout, its `visual-test` branch and its fake `gh`."""
>     base = tmp_path_factory.mktemp("diff")
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
>     (bin_dir / "gh").write_text(story1.FAKE_GH)
>     (bin_dir / "gh").chmod(0o755)
>     (base / "world.json").write_text(json.dumps(story1.world()))
>     return {"repo": repo, "bin": bin_dir, "world": base / "world.json", "log": base / "gh.log"}
> 
> 
> def diff(place, number, branch):
>     """Run `diff` from the throwaway checkout's root; returns the finished process."""
>     if not (place["repo"] / "tools" / "visuals.py").exists

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -lE "visuals|nightly/|tools/" .github/workflows/* dokima -r; ls tests | grep -i visual; grep -n "card-gallery\|gallery" -r tests/*.py | head -20; grep -n "def \|add_parser\|gallery" tools/visuals.py | head -60; cat .github/workflows/full-suite.yml | grep -n pytest
```

> test_visuals_diff.py
> test_visuals_draw.py
> test_visuals_preview.py
> tests/test_card_self_link.py:6:tested it on dokima-dev/card-gallery), so the PR's description ends with that line, and it is the only closing
> tests/test_card_status.py:29:`python3 dokima/card.py gallery DIR` draws the card of every situation the owner looks at on a real throwaway issue
> tests/test_card_status.py:594:def test_the_gallery_draws_every_situation_for_the_owner_to_look_at(record_property, tmp_path):
> tests/test_card_status.py:597:    Runs `python3 dokima/card.py gallery DIR` from the repo root and checks it writes one card per situation, each
> tests/test_card_status.py:603:    out = subprocess.run([sys.executable, os.path.join("dokima", "card.py"), "gallery", str(tmp_path)], cwd=ROOT, env=env,
> tests/test_card_status.py:606:    assert out.returncode == 0, f"181.5: `python3 dokima/card.py gallery DIR` did not draw the gallery (exit {out.returncode}): {said_}"
> tests/test_card_status.py:610:        assert path.exists(), f"181.5: the gallery did not draw the {s} situation ({s}.md)"
> tests/test_playthrough.py:7:one issue on dokima-dev/card-gallery with stand-in agents that call no model, and judges both cards after each step.
> tests/test_playthrough.py:31:SANDBOX = "dokima-dev/card-gallery"
> tests/test_playthrough.py:32:SANDBOX_TOKEN = "sandbox-token-only-for-card-gallery-7f3e"
> tests/test_playthrough.py:269:    """The app token the play-through holds is minted for dokima-dev/card-gallery alone.
> tests/test_playth

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_\|branch" tests/test_visuals_draw.py | head -40; sed -n 60,115p tools/visuals.py
```

> 1:"""One command draws what Dokima would post on a real issue, with any branch's code.
> 7:    python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME
> 9:It takes the drawing code from BRANCH (for example through a git worktree of that branch, so the checkout it runs
> 10:from is left as it is), reads the real issue from GitHub through `gh`, and prints to stdout what that branch's code
> 13:An issue GitHub cannot give (a mistyped number, or GitHub refusing) or a branch that does not exist ends the command
> 17:on `main`, plus a branch `visual-test` whose drawing code differs in ways no real code shows (markers such as
> 20:marker in its output can only come from the branch's own code, and a run with `--branch main` shows today's drawing.
> 115:# Appended to the branch's copies, so only that branch's code draws these markers and lines.
> 122:    """The branch's card: today's card under a marker."""
> 131:    """The branch's run comment: today's comment under a marker."""
> 139:    """The branch's /autopilot reply: today's reply after a marker."""
> 201:    """A throwaway checkout on main, a branch with changed drawing code, and a fake `gh`.
> 203:    The branch is `visual-test`; the fake `gh` goes first on PATH."""
> 219:    git(repo, "commit", "-q", "-am", "branch drawing")
> 229:def draw(place, number, branch):
> 236:    return subprocess.run([sys.executable, "tools/visuals.py", "draw", str(number), "--branch", branch, "--repo", REPO],
> 240:def drawn(place, branch, criterion):
> 241:    """Th

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria: the diff command, nightly real checks, and the tool staying outside Dokima.", "The planner wrote six tests, all failing today because the feature is missing."],
  "decided": ["Real gallery checks live in a nightly folder that the pull request suite never runs."],
  "open": []},
 "verdict": "block",
 "summary": "The plan is close; the nightly test passes without any gallery check, and a mistyped branch goes untested.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Weak test", "text": "626.2: `test_nightly_checks_fail_when_github_refuses` passes when `nightly/` holds any `gh` call, such as `gh api user`, so the card-gallery previews the owner named may never run nightly. Smallest fix: assert a logged `gh` call names `dokima-dev/card-gallery`.", "evidence": "tests/test_visuals_diff.py:228-235 checks only that the log is non-empty, exit 1 and `HTTP 401`."},
  {"kind": "blocker", "to": "planner", "label": "Missing edge case", "text": "626.1: no test runs `diff` with a branch that does not exist, an error users hit by mistyping. Add a test like `test_unknown_branch_says_so` in `tests/test_visuals_draw.py`: non-zero exit, names the branch, no traceback.", "evidence": "`tests/test_visuals_draw.py::test_unknown_branch_says_so` covers this for `draw` only; `tests/test_visuals_diff.py` has no such test."}
 ],
 "answers": [],
 "asks": [
  {"ask": "The command shows which lines differ from what main's code draws.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6148182924", "criterion": "626.1"},
  {"ask": "Checks that post to or read from real GitHub run nightly, never in each pull request's tests.", "source": "https://github.com/dokima-dev/dokima/issues/584#issuecomment-6156300577", "criterion": "626.2"},
  {"ask": "The tool is never a Dokima command or shipped feature.", "source": "https://github.com/doki
```

> Exit code 1
> raise 1's text holds 34 words, over its cap of 30: cut 4, keep the facts
> raise 2's text holds 32 words, over its cap of 30: cut 2, keep the facts
> previous_step did line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`7. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d["previous_step"]["did"][0]="The planner wrote three criteria: the diff command, nightly real checks, the tool kept apart."
d["raises"][0]["text"]="626.2: `test_nightly_checks_fail_when_github_refuses` passes when `nightly/` makes any `gh` call, like `gh api user`, so no gallery check need exist. Fix: assert a logged call names `dokima-dev/card-gallery`."
d["raises"][1]["text"]="626.1: no test runs `diff` with a missing branch, a common typo. Add one like `draw`'s `test_unknown_branch_says_so`: non-zero exit, names the branch, no traceback."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 626 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "log.read_text().strip()\|HTTP 401\" in said" tests/test_visuals_diff.py
```

> 241:    assert log.read_text().strip(), f"626.2: the nightly checks never called gh, so they do not reach real GitHub:\n{said}"
> 243:    assert "HTTP 401" in said, f"626.2: the failing nightly checks do not say GitHub's reason:\n{said}"

`9. Bash`
```
cd /tmp/dokima-out; sed -i 's/tests\/test_visuals_diff.py:228-235/tests\/test_visuals_diff.py:239-243/' review.json; cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 626 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I've sent the plan for [#626](https://github.com/dokima-dev/dokima/issues/626) (diff command and nightly real checks) back to the planner. My verdict is **block**, with two fixes, both for the planner.

**Blockers:**
1. **The nightly test is too weak (criterion 626.2).** `test_nightly_checks_fail_when_github_refuses` passes as long as the nightly folder makes any GitHub call at all, even a trivial one like `gh api user`. So the card-gallery checks you named could be missing and the test would still pass. Fix: also require that a logged GitHub call names `dokima-dev/card-gallery`.
2. **No test for a mistyped branch (criterion 626.1).** No test runs `diff` with a branch that doesn't exist, which is an easy mistake to make. The existing `draw` command already has this test (`test_unknown_branch_says_so`); the diff needs one like it: it fails, names the branch, and shows no traceback.

**What's fine:**
- I ran the six new tests; all fail today because the feature doesn't exist yet, which is the right reason.
- Your three asks from [#584](https://github.com/dokima-dev/dokima/issues/584) (the parent story) each have a matching criterion, none dropped. I matched them from the asks quoted in the issue, since I couldn't open #584's comments themselves.
- Each criterion covers one behavior, and the size is within the rule.

The hand-back is in `/tmp/dokima-out/review.json`, and Dokima's own format and round checks pass on it.

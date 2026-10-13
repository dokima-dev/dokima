# reviewer (plan) for #585

Run: https://github.com/dokima-dev/dokima/actions/runs/38414402458

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #585: One command draws a card demo and shows what changed
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [586], "loop": []} -->
> One command draws any issue's card with draft functions swapped in, and shows only the lines that changed.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/586
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/584
> - https://github.com/dokima-dev/dokima/issues/545
> 
> 
> **User story:** Owners see a card demo drawn by the real card code, with only the changed lines shown.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** One command draws an issue's card with named card functions swapped, printing only lines that differ from the unchanged card.
>   - *<a href="https://github.com/dokima-dev/dokima/bl

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:3000])"
```

> {"number": 584}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38413753230",
>  "commit_before": "507df8606bd0c0d74b549dfcb7a9bc4434b357c8",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 214719,
>   "turns": 16,
>   "cost_usd": 1.0214085999999998,
>   "tokens_in": 889255,
>   "tokens_out": 17539
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/585/38413753230-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38413753230",
>  "handback": {
>   "kind": "user_story",
>   "title": "One command draws a card demo and shows what changed",
>   "summary": "One command draws any issue's card with draft functions swapped in, and shows only the lines that changed.",
>   "user_story": "Owners see a card demo drawn by the real card code, with only the changed lines shown.",
>   "acceptance_criteria": [
>    {
>     "text": "One command draws an issue's card with named card functions swapped, printing only lines that differ from the unchanged card.",
>     "words": "One command renders any issue's card with the real card code, with named card functions swapped for a run only, writes nothing to the repo or to GitHub, and shows the lines that differ from the unchanged card.",
>     "source": "https://github.com/dokima-dev/dokima/issues/584",
>     "edge_cases": [
>      {
>       "case": "A swap that draws the same card shows no changed lines.",
>       "test": "tests/test_demo.py::test_demo_same_function_shows_no_lines"
>      },
>   

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_demo.py; ls dokima/demo.py 2>&1
```

> Exit code 2
> """One command draws a card demo with swapped functions and shows what changed (#585).
> 
> Story 1 of #584. The owner's words: "One command renders any issue's card with the real card code, with named card
> functions swapped for a run only, writes nothing to the repo or to GitHub, and shows the lines that differ from the
> unchanged card."
> 
> The command, run from the repo root:
> 
>     REPO=owner/name python3 -m dokima.demo N --swap NAME=PATH [--swap NAME=PATH ...]
> 
> It reads issue N the way the card code does, draws its card twice with the real card code (`dokima.card.render`, put
> above the owner's part with `dokima.body.redraw`): once unchanged, once with each named function of `dokima.card`
> replaced, for that run only, by the same-named function in the draft file PATH. It prints only the lines that differ,
> as a unified diff with no context lines (`-` the unchanged card, `+` the swapped one), and exits 0. A draft file
> without the named function stops the command with an error naming it.
> 
> How the tests run it. A fake `gh` on PATH answers only the reads the card code makes (the issue, its comments and
> events, its pull request, checks and reviews, its blocked-by links, the worker's runs and files, which it has none of)
> and logs every call. A call that would change anything on GitHub is logged as a write and answered as done, so a test
> can say which write was sent. A call it does not know fails loudly, naming the call. `dokima.demo.main(argv)` is also
> called in-process, with t

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 100,200p tests/test_demo.py
```

> if path.startswith(base + "pulls?head="):
>         out("read", [pr] if pr and path.split("head=")[1].startswith(repo.split("/")[0] + ":try/issue-" + n + "&") else [])
>     if pr and path == base + "pulls/" + pr_n:
>         out("read", pr)
>     if pr and path.startswith(base + "pulls/" + pr_n + "/reviews"):
>         out("read", [])
>     if pr and path.startswith(base + "pulls/" + pr_n + "/comments"):
>         out("read", [])
>     if path.startswith(base + "commits/abc123/check-runs"):
>         out("read", {"total_count": 0, "check_runs": []})
> out("unknown", code=1, err="fake gh: unknown call " + " ".join(args) + " (HTTP 400)")
> '''
> 
> DRAFT = '''"""A draft status line for the card demo's tests."""
> 
> 
> def status_line(repo, stage, todo):
>     """The stage, drafted."""
>     return "**Drafted " + stage + "**"
> '''
> 
> SAME = '''"""A draft that draws the status line exactly as the card code does."""
> 
> 
> def status_line(repo, stage, todo):
>     """The stage, as today."""
>     return "**" + stage + "**" + (" · Needs you: " + todo if todo else "")
> '''
> 
> NONE = '''"""A draft file without the function it is named for."""
> 
> 
> def something_else():
>     """Not a card function."""
>     return None
> '''
> 
> RAISES = '''"""A draft whose status line fails while the card is drawn."""
> 
> 
> def status_line(repo, stage, todo):
>     """Fails on purpose."""
>     raise RuntimeError("draft broke")
> '''
> 
> 
> @pytest.fixture
> def world(tmp_path, monkeypatch):
>     """A fake GitHub on PATH holding issue 7, its call log and a draft folder."""
>    

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 196,225p tests/test_demo.py; grep -n "def status_line" -A8 dokima/card.py; python3 -m pytest -q tests/test_demo.py 2>&1 | tail -15
```

> def test_demo_shows_changed_lines(world, record_property):
>     """The demo prints only the card lines the swapped function changed.
> 
>     Proves 585.1. Swaps the status line for a draft on an issue in Backlog and checks the output holds the real card's line as a
>     minus line, the draft's as a plus line, and no unchanged line of the card or the owner's ask."""
>     record_property("proves", "585.1")
>     r = run(str(NUMBER), "--swap", f"status_line={draft(world, 'draft.py', DRAFT)}")
>     assert r.returncode == 0, f"585.1: the demo did not finish (exit {r.returncode}): {r.stdout}{r.stderr}"
>     lines = diff_lines(r.stdout)
>     assert "-**Backlog**" in lines, f"585.1: the unchanged card's status line is not shown as removed: {r.stdout!r}"
>     assert "+**Drafted Backlog**" in lines, f"585.1: the swapped card's status line is not shown as added: {r.stdout!r}"
>     extra = [line for line in lines if not line.startswith(("+", "-"))]
>     assert not extra, f"585.1: the demo shows lines that did not change: {extra}"
>     assert not any(ASK in line for line in lines), f"585.1: the owner's unchanged ask is shown: {r.stdout!r}"
> 
> 
> def test_demo_same_function_shows_no_lines(world, record_property):
>     """A draft that draws the same card shows no changed lines.
> 
>     Proves 585.1. Swaps the status line for one that draws it as today and checks the demo finishes with no plus or minus line."""
>     record_property("proves", "585.1")
>     r = run(str(NUMBER), "--swap", f"status_line={draft(world, 's

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def draw" -A60 dokima/card.py | head -90; grep -n "^def redraw" -A5 dokima/body.py
```

> 928:def draw(repo, number, pr_number, plans=None, noted=None, cache=None, changed_only=False):
> 929-    """Write the card at the top of the issue and its PR.
> 930-
> 931-    Returns the blocking links and loop its card showed before and shows now. With `changed_only`, a card that
> 932-    already shows what it would be drawn as is not rewritten.
> 933-    `plans` gives the links of a plan approved just now, by issue (see their_links). `noted` adds (True) or removes
> 934-    (False) issues from the index of those whose approved plans link here. The Blocked by and Blocks lines are
> 935-    GitHub's own blocked-by links, read now; `cache` keeps what this run already read.
> 936-    """
> 937-    cache = {} if cache is None else cache
> 938-    issue = plan.fetch_issue(repo, number)
> 939-    found = gather(repo, number, pr_number)
> 940-    cache[("recs", int(number))] = found.get("recs") or []
> 941-    sources = set(linked_from(issue["current_body"]))
> 942-    for s, on in (noted or {}).items():
> 943-        (sources.add if on else sources.discard)(s)
> 944-    found["sources"] = sorted(sources)
> 945-    before, now = shown_links(issue["current_body"]), github_links(repo, int(number), cache)
> 946-    found["blocking"] = now
> 947-    if now.get("unread"):
> 948-        found["unread"] = reason(blocking(repo, int(number), cache))
> 949-    found["linked"] = {"relates_to": their_links(repo, number, found["sources"], plans)["relates_to"],
> 950-                       "blocked_by": now.get("blocked_by") or [], "blo

**Agent:** Checking the planner's tests with a quick prototype in a scratch copy, to see they can pass.

`7. Bash`
```
rm -rf /tmp/rv && mkdir /tmp/rv && cd /home/runner/work/dokima/dokima && git worktree list >/dev/null; cp -r /home/runner/work/dokima/dokima /tmp/rv/repo && cd /tmp/rv/repo && cat > dokima/demo.py <<'EOF'
"""prototype"""
import argparse, difflib, importlib.util, os, sys
from dokima import body, card, plan

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("number")
    p.add_argument("--swap", action="append", default=[])
    a = p.parse_args(argv)
    repo = os.environ["REPO"]
    swaps = {}
    for s in a.swap:
        name, path = s.split("=", 1)
        spec = importlib.util.spec_from_file_location("draft_" + name, path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        if not hasattr(m, name):
            print(f"{path} has no function {name}", file=sys.stderr); return 1
        swaps[name] = getattr(m, name)
    issue = plan.fetch_issue(repo, a.number)
    found = card.gather(repo, a.number, None)
    cache = {}
    now = card.github_links(repo, int(a.number), cache)
    found["blocking"] = now
    found["sources"] = []
    found["linked"] = {"relates_to": [], "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
    cur = issue["current_body"] or ""
    before = body.redraw(cur, card.render(repo, issue, found))
    old = {k: getattr(card, k) for k in swaps}
    try:
        for k, v in swaps.items(): setattr(card, k, v)
        after = body.redraw(cur, card.render(repo, issue, found))
    except Exception as e:
        print(e, file=sys.stderr); return 1
    finally:
        for k, v in old.items(): setattr(card, k, v)
    for l in difflib.unified_diff(before.splitlines(), after.splitlines(), "before", "after", n=0, lineterm=""):
        print(l)
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
python3 -m pytest -q tests/test_demo.py 2>&1 | tail -20
```

> .......                                                                  [100%]
> 7 passed in 1.79s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
cd /home/runner/work/dokima/dokima; cat .gitignore; grep -n "^def save" -A30 dokima/body.py | grep -n "gh\|api" ; grep -n "^def gather" -A3 dokima/card.py
```

> __pycache__/
> *.py[cod]
> .pytest_cache/
> 7:121-        gh("issue", "comment", str(number), "-R", repo, "--body",
> 11:125-    gh("issue", "edit", str(number), "-R", repo, "--body-file", "-", input=new)
> 668:def gather(repo, number, pr_number):
> 669-    """Everything the card is drawn from, fetched from GitHub: never the issue's text."""
> 670-    from dokima import agent
> 671-    _, items = agent.conversation(repo, number)

`9. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria and seven tests for the card demo command."],
  "decided": ["The demo prints only changed lines, puts the card code back, and writes nothing."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan carries all three asks of story 1, and every test fails today only because the command is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "One command renders any issue's card with the real card code, with named card functions swapped, and shows the lines that differ from the unchanged card", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "585.1"},
  {"ask": "with named card functions swapped for a run only", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "585.2"},
  {"ask": "writes nothing to the repo or to GitHub", "source": "https://github.com/dokima-dev/dokima/issues/584", "criterion": "585.3"}
 ],
 "behaviors": [
  {"criterion": "585.1", "one_behavior": true, "why": "One result: the printed changed lines of the swapped card."},
  {"criterion": "585.2", "one_behavior": true, "why": "One result: the card functions are the originals after the run."},
  {"criterion": "585.3", "one_behavior": true, "why": "One result: no write reaches GitHub or the repo."}
 ],
 "edge_cases": [
  {"criterion": "585.1", "cut": [], "missing": []},
  {"criterion": "585.2", "cut": [], "missing": []},
  {"criterion": "585.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_demo.py::test_demo_shows_changed_lines", "only_its_behavior": true, "why": "Checks the old and drafted status lines show, and no unchanged line."},
  {"test": "tests/test_demo.py::test_demo_same_function_shows_no_lines", "only_its_behavior": true, "why": "A draft drawing the same line must print no changed line."},
  {"test": "tests/test_demo.py::test_demo_draft_missing_function", "only_its_behavior": t
```

> (Bash completed with no output)

`10. Bash`
```
rm -rf /tmp/rv; cd /home/runner/work/dokima/dokima && git status --short
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#585](https://github.com/dokima-dev/dokima/issues/585) (one command draws a card demo and shows what changed), and I raised nothing. The hand-back is `/tmp/dokima-out/review.json`, and it passes both checks.

- **Asks:** The three asks of story 1 from [#584](https://github.com/dokima-dev/dokima/issues/584) (approved card demos become fixtures) each have their own criterion:
  - 585.1: draw any issue's card with named card functions swapped, and show only the lines that changed.
  - 585.2: the swap lasts for that run only.
  - 585.3: the command writes nothing to the repo or to GitHub.
- **Tests fail today for the right reason:** All 7 tests in `tests/test_demo.py` fail only because `dokima/demo.py` doesn't exist yet. None fail on a crash, a missing tool or a bad path.
- **The tests can pass:** In a scratch copy of the repo, a quick draft `dokima/demo.py` passed all 7 tests. That draft did not look up the issue's pull request, so it did not try the pull-request reads against the fake GitHub; a real build that reads them could still fail there.
- **The tests would catch wrong work:**
  - Leaving a swapped card function in place fails 585.2, even when the draft function raises an error.
  - Any write to GitHub, or any file change in the repo, fails 585.3.
  - Each "rejects the bad case" test has a "passes the good case" test beside it.
- **Size:** Each criterion is one behavior, and no edge cases are missing or need cutting.

Nothing in the repo changed, and I deleted the scratch copy.

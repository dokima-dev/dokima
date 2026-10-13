# reviewer (plan) for #636

Run: https://github.com/dokima-dev/dokima/actions/runs/38485530800

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
> # Issue #636: The agent code splits into files by job
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [637, 638], "loop": []} -->
> The big agent file splits into one file per job, with nothing changing in how it works.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/637
> - https://github.com/dokima-dev/dokima/issues/638
> 
> 
> **User story:** Issues that change different jobs of the agent code change different files, so they no longer queue.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** The agent code lives in one file per job, moved as it is, with no change in behavior.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-636/tests/test_agent_split.py#L93"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: The agent code sits in one file

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_agent_split.py; cat /tmp/pack/parent.json | head -c 3000; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit fd524c130a2615e7c0ca939a5d9b8668fc85850a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 23:38:51 2026 +0000
> 
>     planner for #636 (run 38484254280)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/agent_patch.py                 |   17 +
>  tests/samples/tests_before_split.txt | 1127 ++++++++++++++++++++++++++++++++++
>  tests/test_agent.py                  |    7 +-
>  tests/test_agent_split.py            |  198 ++++++
>  tests/test_autopilot_board.py        |   14 +-
>  tests/test_autopilot_checks.py       |    3 +-
>  tests/test_blocker_pill.py           |    3 +-
>  tests/test_board.py                  |    3 +-
>  tests/test_board_state.py            |    9 +-
>  tests/test_budget_retry.py           |    3 +-
>  tests/test_build_started_card.py     |    3 +-
>  tests/test_card_records.py           |    7 +-
>  tests/test_card_status.py            |    6 +-
>  tests/test_criteria_quote_owner.py   |    3 +-
>  tests/test_fixer.py                  |    3 +-
>  tests/test_issue_links.py            |    3 +-
>  tests/test_merge_gate.py             |    7 +-
>  tests/test_needs_you.py              |    3 +-
>  tests/test_next_rate_limit.py        |    7 +-
>  tests/test_quiet_board.py            |    3 +-
>  tests/test_raise_handbacks.py        |    3 +-
>  tests/test_raised_cards.py           |    3 +-
>  tests/test_raised_earlier_by.py      |    3 +-
>  tests/test_required_checks.py        |    3 +-
>  tes

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/agent_patch.py; git show HEAD -- tests/test_agent.py tests/test_board_state.py tests/test_run_cards.py tests/test_merge_gate.py tests/test_autopilot_board.py tests/test_fixer.py | head -250
```

> """Patches one name of the agent code in every job file that holds it.
> 
> For tests that fake a record, the bot or the conversation.
> 
> Since #636 the agent code is split into job files (`dokima/agent_*.py`) that `dokima.agent` re-exports, so a name
> patched on `dokima.agent` alone no longer reaches a job file that holds its own copy. `patch_agent` sets the name on
> `dokima.agent` and on every loaded agent job file that holds it. GitHub itself is faked in one place instead, on
> `dokima.agent_github.gh`.
> """
> import sys
> 
> 
> def patch_agent(monkeypatch, name, value):
>     """Sets the name on the agent module and on every agent job file holding it."""
>     for key, mod in sorted(sys.modules.items()):
>         if (key == "dokima.agent" or key.startswith("dokima.agent_")) and mod is not None and hasattr(mod, name):
>             monkeypatch.setattr(mod, name, value)
> commit fd524c130a2615e7c0ca939a5d9b8668fc85850a
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 23:38:51 2026 +0000
> 
>     planner for #636 (run 38484254280)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_agent.py b/tests/test_agent.py
> index 02b07da..a5308ea 100644
> --- a/tests/test_agent.py
> +++ b/tests/test_agent.py
> @@ -6,6 +6,7 @@ import sys
>  
>  sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
>  from dokima import agent, fence  # noqa: E402
> +from dokima import agent_github  # noqa: E402
>  
>  GO

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn 'setattr(agent, \|agent\.gh\b\|setattr(agent\.' tests | grep -v test_agent_split | head -40; grep -rn 'from dokima.agent import\|from dokima import.*agent\|import dokima.agent' dokima | head
```

> tests/test_issue_links.py:48:    """Fake GitHub for agent.gh: issue 250 with no comments and no pull request, and these open issues and PRs.
> tests/test_autopilot_board.py:135:    """A stand-in for agent.gh that answers from the world."""
> tests/test_autopilot_board.py:200:    """agent.gh for an issue with no record yet: no comments, no reviews."""
> tests/test_autopilot_board.py:208:    """Wire a world into dokima.board.Board and dokima.agent.gh, and return it."""
> tests/test_needs_you.py:126:    """agent.gh, answering from the world: pull requests, states, labels, sub-issues and records."""
> tests/test_needs_you.py:195:    """Wire a world into dokima.board.Board and dokima.agent.gh, and return it."""
> tests/test_reviewer_open_issues.py:79:    """Fake GitHub for agent.gh: issue 9 alone, and the open issues above.
> tests/test_card_records.py:16:        It reads GitHub only through `gh` (card.gh, or agent.gh / plan.gh when it reuses their helpers): the REST API
> tests/test_card_records.py:231:    """Fake GitHub for issue #40 and its PR #5, serving card.gh, agent.gh and plan.gh; returns the calls it saw.
> tests/test_review_relay.py:96:    """Wire test_needs_you's world into dokima.board.Board and dokima.agent.gh, and return it."""
> tests/test_card_status.py:399:    """Fake GitHub for parent #40, filed into children #41 to #45, serving card.gh, agent.gh and plan.gh.
> tests/test_budget_retry.py:130:    """Wire a board world into dokima.board.Board and dokima.agent.gh, and return it."""
> dokim

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_agent_split.py 2>&1 | grep -E "Error|636|passed|failed" | head -20; python3 -m pytest -q --co 2>&1 | tail -30
```

> key = '636.1'
> E   ModuleNotFoundError: No module named 'dokima.agent_github'
> <frozen importlib._bootstrap>:1324: ModuleNotFoundError
>         Proves 636.1.
>         record_property("proves", "636.1")
> >       mods = job_modules("636.1")
> key = '636.1'
>             except ModuleNotFoundError as e:
> >               raise AssertionError(f"{key}: there is no job file {name.replace('.', '/')}.py ({e})")
> E               AssertionError: 636.1: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> tests/test_agent_split.py:83: AssertionError
> key = '636.2'
> E   ModuleNotFoundError: No module named 'dokima.agent_github'
> <frozen importlib._bootstrap>:1324: ModuleNotFoundError
>         import order fails here too. Proves 636.2.
>         record_property("proves", "636.2")
> >       mods = job_modules("636.2")
> key = '636.2'
>             except ModuleNotFoundError as e:
> >               raise AssertionError(f"{key}: there is no job file {name.replace('.', '/')}.py ({e})")
> ERROR tests/test_merge_gate.py
> ERROR tests/test_needs_you.py
> ERROR tests/test_next_rate_limit.py
> ERROR tests/test_one_order.py
> ERROR tests/test_parent_close.py
> ERROR tests/test_parent_source.py
> ERROR tests/test_parent_sweep.py
> ERROR tests/test_plan_check_rerun.py
> ERROR tests/test_planner_starts_with_main.py
> ERROR tests/test_playthrough.py
> ERROR tests/test_progress_card.py
> ERROR tests/test_queue_judge.py
> ERROR tests/test_quiet_board.py
> ERROR tests/test_quiet_cards.py
> ERROR tests/test_raise_handbacks.py
> ERRO

**Agent:** Reviewing the plan for issue #636: the new tests fail today because the job files are missing, which is the right reason. Next I'm checking how strong each test is.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_agent_split.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed"; python3 -m dokima.agent check-pack planner issue /tmp/emptyx 2>&1; mkdir -p /tmp/emptyy; python3 -m dokima.agent check-pack planner issue /tmp/emptyy; echo $?; python3 -m dokima.agent check review x; echo $?; grep -rn "BOT\|parent_words" tests/*.py | grep -i "setattr\|patch_agent" | head
```

> FAILED tests/test_agent_split.py::test_agent_code_lives_in_job_files - AssertionError: 636.1: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> FAILED tests/test_agent_split.py::test_every_old_name_loads_from_agent - AssertionError: 636.2: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> FAILED tests/test_agent_split.py::test_github_is_faked_in_one_place - AssertionError: 636.3: there is no job file dokima/agent_github.py (No module named 'dokima.agent_github')
> 3 failed in 0.10s
> issue.md is missing
> issue.md is missing
> 1
> the check needs plan.json and the issue number: agent check review|work FILE PLAN N
> 1
> tests/test_build_started_card.py:28:    patch_agent(monkeypatch, "BOT", tcs.BOT)
> tests/test_card_records.py:309:    patch_agent(monkeypatch, "BOT", BOT_LOGIN)
> tests/test_card_status.py:157:    patch_agent(monkeypatch, "BOT", BOT)
> tests/test_criteria_quote_owner.py:47:    patch_agent(monkeypatch, "parent_words", lambda repo, n: {"number": 5, "body": "Cards update right away.", "comments": []})

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "agent\.[A-Za-z_]* *= " dokima | grep -v "==" | head; grep -n "^def gh\|^BOT\b\|^BOT =" dokima/agent.py; grep -rn "global " dokima/agent.py | head
```

> 30:def gh(*args):
> 37:BOT = os.environ.get("DOKIMA_BOT", "dokima-runtime")
> 1795:def gh_reason(e):
> dokima/agent.py:1813:    global gh

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1800,1835p dokima/agent.py
```

> def rate_limited(e):
>     """The rate limit that refused a call, "graphql" or "core" (REST); else None."""
>     text = gh_reason(e)
>     if "rate limit" not in text.lower():
>         return None
>     return "graphql" if "graphql" in text.lower() else "core"
> 
> 
> @contextlib.contextmanager
> def rate_limit_waited_once():
>     """Inside it, a call refused by GitHub's rate limit waits once, then retries.
> 
>     A second refusal, or any other, raises at once, so a run never hangs on a limit that does not lift."""
>     global gh
>     plain, waited = gh, []
> 
>     def patient(*args):
>         try:
>             return plain(*args)
>         except subprocess.CalledProcessError as e:
>             limit = rate_limited(e)
>             if waited or not limit:
>                 raise
>             try:
>                 reset = int(json.loads(plain("api", "rate_limit"))["resources"][limit]["reset"])
>             except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, ValueError):
>                 raise e
>             waited.append(limit)
>             print(f"GitHub's {limit} rate limit ran out; waiting until it resets: {gh_reason(e)}", file=sys.stderr)
>             time.sleep(max(0, reset - time.time()) + 1)
>             return plain(*args)
>     gh = patient
>     try:
>         yield
>     finally:
>         gh = plain

`9. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["Planned three criteria: job files, every old name still loads, one GitHub helper.",
          "Wrote three new tests and pointed old tests' GitHub fakes at the new helper.",
          "Saved the list of 1127 test names for story 2's count."],
  "decided": ["Other modules keep their own GitHub calls, as the owner decided."],
  "open": ["Only five of about 25 changed test files carry a reason the owner sees."]},
 "verdict": "approve",
 "summary": "The plan carries all three asks of story 1, and each test fails today because the job files are missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "agent.py is split into modules by job (autopilot and merging, records, Next lines, checks, GitHub helpers, roles), a pure move with no behavior change", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.1"},
  {"ask": "`agent` keeps re-exporting every name so its 146 importers keep working.", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.2"},
  {"ask": "GitHub calls go through one helper module that tests patch in one place", "source": "https://github.com/dokima-dev/dokima/issues/581", "criterion": "636.3"}
 ],
 "behaviors": [
  {"criterion": "636.1", "one_behavior": true, "why": "Code moves into job files unchanged; the full suite and the command checks prove no change."},
  {"criterion": "636.2", "one_behavior": true, "why": "Every old name still loads from the agent module."},
  {"criterion": "636.3", "one_behavior": true, "why": "Faking one helper fakes every GitHub call of the agent code."}
 ],
 "edge_cases": [
  {"criterion": "636.1", "cut": [], "missing": []},
  {"criterion": "636.2", "cut": [], "missing": []},
  {"criterion": "636.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_agent_split.py::test_agent_code_lives_in_job_files", "only_its_behavior": true, "why": "Fails if any old 
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#636](https://github.com/dokima-dev/dokima/issues/636) (splitting the big agent file into one file per job). The review is in `/tmp/dokima-out/review.json` and both hand-back checks pass.

**Why it passes:**
- **Every ask has a criterion.** The three asks from story 1 of [#581](https://github.com/dokima-dev/dokima/issues/581) (splitting the agent file and the rules file) each map to one: the code moves into job files with no change in behavior, every old name still loads from the agent file, and every GitHub call goes through one helper.
- **The tests fail for the right reason.** I ran the three new tests and each fails because `dokima/agent_github.py` does not exist yet, not because of a crash or a bad path. The test for the one helper puts a fake `gh` on the path that fails loudly, so any sampled call that skips the helper fails the test.
- **The command still works.** `python3 -m dokima.agent check-pack` and `check` with too few words give the same answers today that the new test expects, so the workflows' use is covered.
- **The old test count is saved.** The list of 1127 test names is in `tests/samples/tests_before_split.txt` for story 2.
- **The owner's decision holds.** Other modules keep their own GitHub calls, as the owner chose on #581.

**Things to know:**
- **Only 5 test-change reasons.** The planner's commit edits test files across about 25 files, but only five changes carry a reason the owner sees. The extra edits just point existing GitHub fakes at the new helper. This isn't on the plan grade's blocker list, so I noted it in the summary instead of blocking.
- **Most of the suite won't load until the worker builds.** Because those test files now import the new helper, 68 test files fail to load on this branch today, and only 642 tests are collected.
- **One small gap in the helper test.** A job file could rename the helper on import and slip past its file scan. That would be a deliberate dodge, and the rest of the suite fakes the helper anyway, so I didn't raise it.

The worker is next: an approved plan on autopilot starts the build by itself.

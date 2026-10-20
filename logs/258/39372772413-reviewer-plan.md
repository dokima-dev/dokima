# reviewer (plan) for #258

Run: https://github.com/dokima-dev/dokima/actions/runs/39372772413

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> # Issue #258: A nightly run uses Dokima for real on a sandbox repo and files what breaks
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 425, 437, 584, 626, 829 -->
> <!-- dokima-blocking: {"blocked_by": [746], "blocks": [], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/425
> - https://github.com/dokima-dev/dokima/issues/437
> - https://github.com/dokima-dev/dokima/issues/584
> - https://github.com/dokima-dev/dokima/issues/626
> - https://github.com/dokima-dev/dokima/issues/829
> 
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> Parked for later. A product built with Dokima, not part of its flow: it gates nothing and never shows on cards.
> 
> What I want:
> - A sandbox repo running the same Dokima app and workflows from main, and a test account standing in for me, with a token limited to that repo.
> - A nightly workflow plays me through a few real journeys: a new issue to merged, a question that stops for me, a split that files its stories. It checks what I would see, then clea

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/test_playthrough.py; cat /tmp/pack/owner_words.json /tmp/pack/parent.json | head -50; wc -l dokima/playthrough.py .github/workflows/playthrough.yml tests/test_nightly_journeys.py
```

> commit 437dcacb55b6ac8f84ef1d35543d8bf0cd6c8016
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 20 05:02:16 2026 +0000
> 
>     planner for #258 (run 39371728203)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_nightly_journeys.py | 657 +++++++++++++++++++++++++++++++++++++++++
>  tests/test_playthrough.py      |   6 +-
>  2 files changed, 661 insertions(+), 2 deletions(-)
> commit 437dcacb55b6ac8f84ef1d35543d8bf0cd6c8016
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 20 05:02:16 2026 +0000
> 
>     planner for #258 (run 39371728203)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_playthrough.py b/tests/test_playthrough.py
> index df1efb96..2d2d3eff 100644
> --- a/tests/test_playthrough.py
> +++ b/tests/test_playthrough.py
> @@ -271,7 +271,8 @@ def test_the_key_is_minted_for_the_sandbox_repo_only(record_property):
>      Proves 437.6.
>      Reads playthrough.yml: every app token step names owner dokima-dev and repositories card-gallery and nothing else,
>      there is at least one, none asks for permission to write workflows (Dokima's app never gets it; the install uses
> -    SANDBOX_TOKEN), and the workflow's own GitHub token may write nothing."""
> +    SANDBOX_TOKEN), and the workflow's own GitHub token may write nothing but issues, which it needs to file the bug
> +

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat .github/workflows/playthrough.yml; cat dokima/playthrough.py
```

> name: playthrough
> run-name: "play-through of ${{ inputs.commit || github.event.pull_request.head.sha }}"
> # Plays one issue on the sandbox repo dokima-dev/card-gallery from opened to merged with the Dokima commit given, and
> # says after each step whether both cards showed what had just happened (dokima/playthrough.py). Stand-in agents
> # call no model. The play-through installs the commit on the sandbox with SANDBOX_TOKEN, its own key that can write
> # only to card-gallery; Dokima's app key is minted for card-gallery alone and never gets workflow write.
> # It runs only from the Run workflow button: on every pull request it took 8 to 17 minutes and a burst of API calls,
> # and it moves to a nightly run with the shared surface (#517, #258).
> on:
>   workflow_dispatch:
>     inputs:
>       commit:
>         description: The Dokima commit to play
>         required: true
> permissions:
>   contents: read
> concurrency:
>   group: playthrough
>   cancel-in-progress: false
> jobs:
>   play:
>     # A pull request from someone's own copy of the repo never opens the keys: only branches of this repo play on
>     # their own. The Run workflow button still plays any commit.
>     if: github.event_name != 'pull_request_target' || github.event.pull_request.head.repo.full_name == github.repository
>     environment: keys
>     runs-on: ubuntu-24.04
>     steps:
>       - uses: actions/checkout@v5
>         with:
>           persist-credentials: false
>       - name: The Dokima commit to play, in a folder of its own
>         uses: actions

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_nightly_journeys.py
```

> <persisted-output>
> Output too large (34.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/3e5e3dee-71ee-41b0-862a-f8079ec667be/tool-results/bvzbd212x.txt
> 
> Preview (first 2KB):
> """Nightly, the owner's journeys play on the sandbox, are cleaned up, failures filed (#258).
> 
> The play-through of #437 (dokima/playthrough.py, .github/workflows/playthrough.yml) plays one issue from opened to
> merged on dokima-dev/card-gallery, and only from the Run workflow button. #258 asks for more: every night it plays
> three journeys the owner walks (a new issue to merged, a question that stops for the owner, a split that files its
> stories), acts as a test account standing in for the owner, checks what the owner would see on the cards, cleans up
> what it opened, and files a bug on Dokima's own repo for each journey that failed. It gates nothing.
> 
> These tests run with no GitHub and no key. The journeys are played with `nightly()` on a fake sandbox that shows the
> cards dokima/card.py draws for each step; the real `Sandbox`'s owner steps and clean-up run against a fake `gh` on
> PATH; the bug is filed through a fake `gh` too; the workflow is read and its expressions evaluated with
> tests/test_start.py's evaluator.
> """
> import json
> import os
> import shutil
> import sys
> import time
> 
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
> sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
> from test_card_running import REPO, rec  # noqa:

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat .github/workflows/playthrough.yml; cat dokima/playthrough.py
```

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_nightly_journeys.py
```

> name: playthrough
> run-name: "play-through of ${{ inputs.commit || github.event.pull_request.head.sha }}"
> # Plays one issue on the sandbox repo dokima-dev/card-gallery from opened to merged with the Dokima commit given, and
> # says after each step whether both cards showed what had just happened (dokima/playthrough.py). Stand-in agents
> # call no model. The play-through installs the commit on the sandbox with SANDBOX_TOKEN, its own key that can write
> # only to card-gallery; Dokima's app key is minted for card-gallery alone and never gets workflow write.
> # It runs only from the Run workflow button: on every pull request it took 8 to 17 minutes and a burst of API calls,
> # and it moves to a nightly run with the shared surface (#517, #258).
> on:
>   workflow_dispatch:
>     inputs:
>       commit:
>         description: The Dokima commit to play
>         required: true
> permissions:
>   contents: read
> concurrency:
>   group: playthrough
>   cancel-in-progress: false
> jobs:
>   play:
>     # A pull request from someone's own copy of the repo never opens the keys: only branches of this repo play on
>     # their own. The Run workflow button still plays any commit.
>     if: github.event_name != 'pull_request_target' || github.event.pull_request.head.repo.full_name == github.repository
>     environment: keys
>     runs-on: ubuntu-24.04
>     steps:
>       - uses: actions/checkout@v5
>         with:
>           persist-credentials: false
>       - name: The Dokima commit to play, in a folder of its own
>         uses: actions

> <persisted-output>
> Output too large (34.3KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/3e5e3dee-71ee-41b0-862a-f8079ec667be/tool-results/bvzbd212x.txt
> 
> Preview (first 2KB):
> """Nightly, the owner's journeys play on the sandbox, are cleaned up, failures filed (#258).
> 
> The play-through of #437 (dokima/playthrough.py, .github/workflows/playthrough.yml) plays one issue from opened to
> merged on dokima-dev/card-gallery, and only from the Run workflow button. #258 asks for more: every night it plays
> three journeys the owner walks (a new issue to merged, a question that stops for the owner, a split that files its
> stories), acts as a test account standing in for the owner, checks what the owner would see on the cards, cleans up
> what it opened, and files a bug on Dokima's own repo for each journey that failed. It gates nothing.
> 
> These tests run with no GitHub and no key. The journeys are played with `nightly()` on a fake sandbox that shows the
> cards dokima/card.py draws for each step; the real `Sandbox`'s owner steps and clean-up run against a fake `gh` on
> PATH; the bug is filed through a fake `gh` too; the workflow is read and its expressions evaluated with
> tests/test_start.py's evaluator.
> """
> import json
> import os
> import shutil
> import sys
> import time
> 
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
> sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
> from test_card_running import REPO, rec  # noqa:

`7. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 40,400p tests/test_nightly_journeys.py
```

> """The issue card drawn for issue #1 after `steps`, with these split stories as children."""
>     items = items_of(steps)
>     found = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "reviews": [],
>              "owners": {OWNER}, "tests": {}, "worker": None, "children": list(children)}
>     os.environ.setdefault("GITHUB_REPOSITORY", REPO)
>     return issue_body(card.render(REPO, {"number": 1, "url": f"https://github.com/{REPO}/issues/1"}, found, "issue"))
> 
> 
> def plan(**more):
>     """A stand-in style user story plan, as the card reads it."""
>     return {"kind": "user_story", "summary": "A thing is built.", "user_story": "The owner sees the thing.",
>             "acceptance_criteria": [{"text": "The thing shows.", "source": f"https://github.com/{REPO}/issues/1",
>                                      "files": ["app/x.py"]}],
>             "non_functional": [], "tests": {}, **more}
> 
> 
> QUESTION_RAISE = {"kind": "question", "to": "owner", "label": "Two readings", "text": "Which one do you mean?",
>                   "id": "P1", "by": "planner"}
> 
> 
> def feature(n):
>     """A split into n stories, as the card reads it."""
>     return {"kind": "feature", "title": "Play-through split", "summary": "A split.", "feature": "Two stories.",
>             "stories": [{"title": f"Play-through story {i + 1}", "user_story": "The owner sees a story.",
>                          "acceptance_criteria": [], "non_functional": [], "depends_on": []} for i in range(n)]}
> 
> 
> def split_cards(n):
>   

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 400,660p tests/test_nightly_journeys.py
```

> fail("no such branch")
>         S["branches"].remove(m.group(1))
>         save()
>         sys.exit(0)
>     if method == "POST" and tail == "issues":
>         n = max(int(k) for k in S["issues"]) + 1
>         S["issues"][str(n)] = {"title": fields().get("title", ""), "state": "open"}
>         save()
>         out(rest(n, S["issues"][str(n)]))
>     fail("unsupported api call")
> fail("unsupported call")
> '''
> 
> 
> def fake_gh(tmp_path, monkeypatch, state):
>     """Put a fake `gh` on PATH keeping issues, pull requests and branches in a file.
> 
>     It answers `gh issue|pr list|view|close` (`pr close --delete-branch` deletes the head branch) and `gh issue
>     create`, and `gh api` reads of issues, pulls, sub-issues, branches and refs, a PATCH setting state=closed and a
>     DELETE of a branch ref. `--jq` goes through the jq tool. It logs each call's arguments and GH_TOKEN, and refuses
>     any call naming another repo. Returns (state file, calls file)."""
>     d = tmp_path / "gh"
>     (d / "bin").mkdir(parents=True)
>     tool = d / "bin" / "gh"
>     tool.write_text(f"#!{sys.executable}\n" + FAKE_GH)
>     tool.chmod(0o755)
>     (d / "state.json").write_text(json.dumps(state))
>     monkeypatch.setenv("PATH", f"{d / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}")
>     monkeypatch.setenv("FAKE_GH_DIR", str(d))
>     return d / "state.json", d / "calls.jsonl"
> 
> 
> def calls_of(path):
>     """Every call the fake gh logged."""
>     return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else [

**Agent:** Reading the plan's tests done; now running them to see each fails for the right reason.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_nightly_journeys.py tests/test_playthrough.py 2>&1 | grep -E "^(FAILED|ERROR|E  .*258|[0-9]+ (passed|failed))|passed|failed" | head -40
```

> E       AssertionError: 258.3: dokima/playthrough.py has no nightly(), so no nightly run plays the journeys
> E       AssertionError: 258.4: dokima/playthrough.py has no nightly(), so no nightly run plays the journeys
> E       AssertionError: 258.5: dokima/playthrough.py has no nightly(), so no nightly run plays the journeys
> E           AssertionError: 258.2: the journey's issue was opened with Dokima's app key, not the test account's key
> E       AssertionError: 258.6: dokima/playthrough.py has no nightly(), so no nightly run plays the journeys
> E       AssertionError: 258.7: dokima/playthrough.py's Sandbox has no clean(), so nothing is cleaned up
> ______________ test_a_failed_journey_files_a_bug_on_dokimas_repo _______________
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_a_failed_journey_files_a_0')
>     def test_a_failed_journey_files_a_bug_on_dokimas_repo(tmp_path, monkeypatch, record_property):
>         """A failed journey files one bug on Dokima's repo, naming it and quoting what failed.
> >       assert hasattr(p, "file_bug"), "258.8: dokima/playthrough.py has no file_bug(), so a failed journey files nothing"
> E       AssertionError: 258.8: dokima/playthrough.py has no file_bug(), so a failed journey files nothing
> E       AssertionError: 258.1: playthrough.yml starts on no schedule, so nothing plays nightly: {'workflow_dispatch': {'inputs': {'commit': {'description': 'The Dokima commit to play', 'required': 'true'}}}}
> E       AssertionError: 258.9: playthrough.yml ha

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -i -E "owner|bot|command" rules/identity.md | head -30; grep -rn "def owners\|is_owner\|OWNERS" dokima/*.py | head
```

> 3:- Agents act as the repo's own GitHub App (bot), never as a person. The bot can't approve, can't push workflow changes, and can't change settings.
> 4:- A build that changes a workflow file pauses until the owner approves it on GitHub; only then does a key held behind that approval push it (planned).
> 5:- Every run happens on a fresh, isolated machine with no access to the owner's computer. Agents hold no GitHub key while they work; code checks their output, then posts it.
> 6:- A chat agent may act as the owner's proxy with the owner's token, logged; the bot's own comments never start anything.
> 7:- Agent commits credit the owner as co-author (planned).
> dokima/agent_autopilot.py:638:    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o] or \
> dokima/agent_roles.py:165:    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
> dokima/agent_roles.py:494:        owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
> dokima/agent_roles.py:710:            owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
> dokima/agent_roles.py:730:            merge_tree(repo, number, [o for o in os.environ.get("OWNERS", "").split(",") if o])
> dokima/agent_roles.py:760:        owners = [o for o in os.environ.get("OWNERS", "").split(",") if o] or sorted(repo_approvers(repo.split("/")[0]))
> dokima/agent_records.py:462:    owners = [o for o in os.environ.get("OWNERS", "").split(",") if o]
> dokima/audit.py:3:    python3 -m dokima.audit OWNER/REPO   # rea

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def test_\|Sandbox(" tests/test_playthrough.py | head -40
```

> 94:def test_the_play_through_plays_every_step_from_a_new_issue_to_a_merge_in_order(record_property):
> 107:def test_each_step_passes_only_when_both_cards_show_what_it_should(record_property):
> 152:def test_the_run_workflow_button_starts_the_play_through_for_a_given_dokima_commit(record_property):
> 189:def test_the_stand_in_agents_call_no_model_and_their_records_show_no_tokens(tmp_path, record_property):
> 249:def test_all_tests_keep_every_fake_github_card_check(record_property):
> 268:def test_the_key_is_minted_for_the_sandbox_repo_only(record_property):
> 346:def test_the_play_through_touches_only_the_sandbox_repo(tmp_path, record_property):
> 370:def test_a_step_whose_card_runs_do_not_finish_in_time_fails_naming_the_step_and_the_wait(record_property):
> 451:def test_one_run_plays_every_step_waits_judges_both_cards_and_logs_one_line_each(record_property):
> 462:    hub = FakeSandbox()
> 474:    hub = FakeSandbox(stale=("plan approved", "code review record posted"))
> 485:def test_the_run_plays_its_agent_steps_with_stand_ins_that_leave_no_token_report(record_property):
> 494:    hub = FakeSandbox()
> 508:def test_a_hung_step_fails_the_run_naming_the_wait_and_the_run_plays_on(record_property):
> 517:    hub = FakeSandbox(hung=("code review started",))
> 529:def test_the_play_through_installs_the_played_commit_on_the_sandbox_before_the_first_step(tmp_path, record_property):
> 550:                      ("tests/test_a.py", "def test_a(): pass"), ("README.md", "readme")):
> 560:    hub = FakeSandbox()
> 564:    hu

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote nine criteria and nine failing tests for nightly journeys on the sandbox.",
          "The planner let the run's own key write issues, to file bugs."],
  "decided": ["Journeys keep stand-in agents that call no model.", "Bugs are filed on Dokima's own repo every night a journey fails."],
  "open": ["Three questions wait for the owner: real agents, repeat bugs, and whether to plan a parked issue."]},
 "verdict": "block",
 "summary": "The plan proves only the issue opening is the test account's; the owner's start of a split is unproven.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "258.2: owner's start unproven",
   "text": "The owner asked for a test account standing in for them, but 258.2 proves only the issue opening. The split's start (/work) is the owner's step too, and the bot's comments never start anything, so a start posted with the app key breaks the journey while every test passes. Smallest fix: widen 258.2 to every owner step and make its test also play the split's start on the real sandbox against the fake gh, checking the comment carries the test account's key.",
   "evidence": "`rules/identity.md:6` says bot comments never start anything; `test_the_owners_steps_are_taken_by_the_test_account` plays only `issue opened`."},
  {"kind": "blocker", "to": "planner", "label": "258.4, 258.5: sandbox steps unplayed",
   "text": "The question and split steps are only played on a fake sandbox, so a real sandbox that posts nothing for them passes every test. Smallest fix: in the tests for 258.4 and 258.5, also play each new step on the real sandbox against the fake gh and check it posts the stand-in's record on the journey's issue.",
   "evidence": "`tests/test_nightly_journeys.py` uses `NightSandbox` for 258.4 and 258.5; no test calls `Sandbox.do` with `question posted` or `split posted`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "i
```

> Exit code 1
> raise 1's text holds 82 words, over its cap of 30: cut 52, keep the facts
> raise 2's label holds 5 words, over its cap of 4: cut 1, keep the facts
> raise 2's text holds 57 words, over its cap of 30: cut 27, keep the facts
> previous_step open line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`13. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open("review.json"))
r["raises"][0]["text"]="258.2 proves only the issue opening. The split's /work is the owner's step too; bot comments start nothing. Fix: test that /work also uses the test account's key."
r["raises"][1]["label"]="258.4, 258.5: real steps unplayed"
r["raises"][1]["text"]="Question and split steps run only on a fake sandbox, so a real one posting nothing passes. Fix: also play them on the real sandbox against the fake gh."
r["previous_step"]["open"]=["Three owner questions wait: real agents, repeat bugs, planning a parked issue."]
json.dump(r,open("review.json","w"),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 258 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> raise 2's label holds 5 words, over its cap of 4: cut 1, keep the facts

`14. Bash`
```
cd /tmp/dokima-out; python3 -c "
import json;r=json.load(open('review.json'));r['raises'][1]['label']='258.4/258.5: steps unplayed';json.dump(r,open('review.json','w'),indent=1)"
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 258 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> raise 2's label names code (a file, path, function or code span): say it in plain words

**Agent:** Still fixing the word limits on the review file so it passes the check.

`15. Bash`
```
cd /tmp/dokima-out; python3 -c "
import json;r=json.load(open('review.json'));r['raises'][1]['label']='258.4, 258.5: unplayed';json.dump(r,open('review.json','w'),indent=1)"
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 258 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#258](https://github.com/dokima-dev/dokima/issues/258) (nightly journeys on the sandbox repo); both fixes go back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What's sound:** every ask in your issue has a criterion. All 9 new tests fail today for the right reason, because the feature is missing, not because the test is broken. The one older test the plan loosens now lets the nightly run's own key write issues. It needs that to file a bug, so that change is allowed.

**Blockers:**
- **258.2, the test account standing in for you:** the test only checks that the test account opens the issue. Starting the split with `/work` is also your step. The bot's own comments never start anything (`rules/identity.md:6`), so a `/work` posted with Dokima's app key would break that journey on the real sandbox while every test still passes. Fix: the test also checks that the split's `/work` uses the test account's key.
- **258.4 and 258.5, the question and split journeys:** both are only run against a pretend sandbox. A real sandbox that posts nothing for those steps would still pass. Fix: also run those steps through the real sandbox code against the fake GitHub.

**Waiting on you:** the planner asked you three questions, and I left them for you because your words don't settle them:
- Should journeys run real agents that call a model? The plan keeps today's free stand-ins.
- Should a journey that stays broken file a new bug every night? The plan says yes.
- Your issue says "Parked for later", but autopilot started it once its blockers merged. Should it be planned now? The plan assumes yes.

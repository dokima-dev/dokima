# reviewer (plan) for #534

Run: https://github.com/dokima-dev/dokima/actions/runs/38301376362

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #534: Cards are rewritten only when they change
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 533 -->
> <!-- dokima-blocking: {"blocked_by": [533], "blocks": [], "loop": []} -->
> Cards on issues and pull requests are saved only when what they show changes.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/534#issuecomment-6131481821) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/533
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/380
> 
> 
> **User story:** A person's comment no longer rewrites cards that already show what code draws, so fewer GitHub calls are spent.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_quiet_cards.py; git show HEAD -- tests/test_body.py; gh label list 2>/dev/null | head -1
```

> {"number": 380}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38300146263",
>  "commit_before": "c837f39b5fe13440613a68945149ea589028b9e0",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 625510,
>   "turns": 41,
>   "cost_usd": 1.9513409999999998,
>   "tokens_in": 3349857,
>   "tokens_out": 23223
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/534/38300146263-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38300146263",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/534#issuecomment-6131481821"
> }
> commit 6425ca42d16751b33d8ed021b07ff8b6c3804bb7
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 20:00:06 2026 +0000
> 
>     planner for #534 (run 38300146263)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_body.py        |  4 +--
>  tests/test_quiet_cards.py | 71 +++++++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 73 insertions(+), 2 deletions(-)
> """Cards are rewritten only when they change (#534, story 2 of #380).
> 
> GitHub's GraphQL budget (5,000 calls an hour, shared by every Dokima workflow) ran out on 2026-10-09, and card.yml
> used about a fifth of it. The owner asked on #380: "Same rule for card.yml where it applies: a card is redrawn only
> when something it shows changed."
> 
> card.yml keeps running on every eve

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_quiet_cards.py tests/test_body.py 2>&1 | tail -15; grep -n "changed_only\|BY_BOT" dokima/card.py | head -30; gh issue view 380 --json body,comments 2>&1 | head -c 300
```

> issue_w, pr_w = run(monkeypatch, github, issue_now, pr_now, by_bot)
> >           assert issue_w is None, f"534.1: a person's change ({who}) rewrote the issue's card, though it already showed what code draws"
> E           AssertionError: 534.1: a person's change (BY_BOT=false) rewrote the issue's card, though it already showed what code draws
> E           assert '<!-- dokima-card -->\n<!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->\nCards link what matters.../r/main/dokima/icons/owner-approval.svg" width="16" height="16" align="absmiddle" alt="owner approval"> Owner approval' is None
> 
> /home/runner/work/dokima/dokima/tests/test_quiet_cards.py:63: AssertionError
> ----------------------------- Captured stdout call -----------------------------
> Card written into issue #40
> Card written into PR #5
> Card written into issue #40
> Card written into PR #5
> =========================== short test summary info ============================
> FAILED tests/test_quiet_cards.py::test_a_card_is_written_only_when_what_code_draws_differs - AssertionError: 534.1: a person's change (BY_BOT=false) rewrote the issue's card, though it already showed what code draws
> assert '<!-- dokima-card -->\n<!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->\nCards link what matters.../r/main/dokima/icons/owner-approval.svg" width="16" height="16" align="absmiddle" alt="owner approval"> Owner approval' is None
> 1 failed, 13 passed in 0.42s
> 791:            draw(repo, m, issue_pr(repo, 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; rm -rf /tmp/rv && cp -r . /tmp/rv && cd /tmp/rv && sed -i '920s/changed_only=os.environ.get("BY_BOT") == "true"/changed_only=True/' dokima/card.py && sed -n 920p dokima/card.py && python3 -m pytest -q tests/ 2>&1 | tail -5; sed -n 940,970p dokima/card.py
```

> Command did not complete within its 120s timeout and was moved to the background (ID: b17zt3dtz). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/41370748-916e-4699-be1b-8874cc5db71c/tasks/b17zt3dtz.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`5. Bash`
```
cd /tmp/rv && sed -n 920p dokima/card.py; python3 -m pytest -q tests/test_quiet_cards.py tests/test_body.py 2>&1 | tail -3; sed -n 940,970p dokima/card.py
```

> before, now = draw(repo, number, pr_number, cache=cache, changed_only=True)
> ..............                                                           [100%]
> 14 passed in 0.10s
>     sources = set(linked_from(issue["current_body"]))
>     for s, on in (noted or {}).items():
>         (sources.add if on else sources.discard)(s)
>     found["sources"] = sorted(sources)
>     before, now = shown_links(issue["current_body"]), github_links(repo, int(number), cache)
>     found["blocking"] = now
>     if now.get("unread"):
>         found["unread"] = reason(blocking(repo, int(number), cache))
>     found["linked"] = {"relates_to": their_links(repo, number, found["sources"], plans)["relates_to"],
>                        "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
>     pr = found["pr"]
>     # Only the part above the marker is code's; the owner's ask below it is saved as it is, or the save is refused.
>     current, top = issue["current_body"] or "", render(repo, issue, found)
>     if not (changed_only and shows(current, top)) and body.save(repo, number, current, top):
>         print(f"Card written into issue #{number}")
>     if now.get("loop") and now["loop"] != before.get("loop"):
>         stop_for_loop(repo, number, now["loop"], found.get("owners"))
>     # The PR gets the same card, open, merged or closed, so it never keeps an older card than the issue (#224); its
>     # top row also links the issue, and it closes the issue by its full address (#452).
>     ask = body.ask(current)

**Agent:** Plan's test fails today for the right reason and passes with the one-line fix. Now checking the planner's claim that the second criterion is already covered.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat c837f39 | head -20; grep -rln "555\|skip" tests/ | head; 
```

> commit c837f39b5fe13440613a68945149ea589028b9e0
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Mon Oct 12 19:44:08 2026 +0000
> 
>     Board runs only when a card can move (#555)
>     
>     * planner for #533 (run 38285898763)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * planner for #533 (run 38291913626)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * worker for #533 (run 38294906863)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     ---------
>     
> tests/test_text_only.py
> tests/test_plan_links_recorded.py
> tests/test_playthrough.py
> tests/test_unrecorded_run.py
> tests/test_quiet_board.py
> tests/test_answered_questions.py
> tests/test_queue_judge.py
> tests/test_autopilot_close.py
> tests/test_autopilot_river.py
> tests/test_uptodate.py

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def test\|proves\|record_property(\"proves" tests/test_quiet_board.py | head -30; python3 -m pytest -q tests/test_quiet_board.py 2>&1 | tail -2; cat /tmp/claude-1001/-home-runner-work-dokima-dokima/41370748-916e-4699-be1b-8874cc5db71c/tasks/b17zt3dtz.output | tail -5
```

> 328:def test_an_event_that_cannot_move_a_card_no_longer_starts_a_board_update(record_property, monkeypatch, tmp_path):
> 340:    record_property("proves", "533.1")
> 371:def test_events_about_one_issue_within_a_minute_cause_one_board_update(record_property, monkeypatch, tmp_path):
> 382:    record_property("proves", "533.2")
> 414:def test_autopilot_ignores_a_bursts_cancelled_waits(record_property, monkeypatch):
> 421:    record_property("proves", "533.3")
> ...                                                                      [100%]
> 3 passed in 0.37s
>         before, now = draw(repo, number, pr_number, cache=cache, changed_only=True)

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 328,370p tests/test_quiet_board.py
```

> def test_an_event_that_cannot_move_a_card_no_longer_starts_a_board_update(record_property, monkeypatch, tmp_path):
>     """Comments, line notes, new commits, finished checks and other labels start no board update.
> 
>     Plays board.yml, its jobs' `if:` evaluated as GitHub does with the queue step's real outputs, on each event about
>     #57 or its PR #60 that cannot change a column or pill: a stranger's comment, the code owner's comment with no
>     command, a comment on the PR, a bot comment that is no record, run card or Autopilot line, a line note, a review
>     that only comments, an Approve with or without words, new commits, the Acceptance criteria checks passing or
>     failing, the label bug added or removed, the card redrawn above the marker, the first card on a fresh ask and a
>     title edit. On none of them may the job running `python3 -m dokima.board` run. Beside them, on every event that
>     can move a card (the issue opened, closed or reopened, the owner's ask edited, each command, a record, a run card,
>     each Autopilot line, a review with /work or the bot's record, the PR opened, reopened, merged or closed, the
>     autopilot label, the sweep), and on events the queue step cannot read, it must still run. Proves 533.1."""
>     record_property("proves", "533.1")
>     jobs = jobs_of()
>     s = sync_job(jobs)
>     wrong_run = [w for w, (e, p) in skipped_events().items() if play(e, p, monkeypatch, tmp_path, "533.1")[s]["ran"]]
>     assert not wrong_run, f"533.1: these events 

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "skipped_events" tests/ | head; curl -s https://raw.githubusercontent.com/dokima-dev/dokima/logs/logs/534/38300146263-planner.md 2>/dev/null | grep -n "8 river\|replay\|river states" | head
```

> tests/test_quiet_board.py:154:def skipped_events(n=57, pr=60):
> tests/test_quiet_board.py:343:    wrong_run = [w for w, (e, p) in skipped_events().items() if play(e, p, monkeypatch, tmp_path, "533.1")[s]["ran"]]
> tests/test_quiet_board.py:406:    bad = [w for w, (e, p) in skipped_events().items()
> 917:   "evidence": "A test replaying each skipped event in 8 river states passes on main since #555; new tests must fail."}],
> 1043:**Second criterion: one question for you.** The issue's second criterion says the board's skipped events would never have moved a card. That is already true on main since [#555](https://github.com/dokima-dev/dokima/pull/555) (board runs only when a card can move). I wrote a test that replays every skipped event in 8 states an issue can be in, and none of them moves a card. But that test passes today, and the plan check refuses any new test that passes before the work is done. So the plan leaves that criterion out and asks you whether that's right. It assumes yes.

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "missing" dokima/agent.py | head -30
```

> 249:    """A plan record's links as three lists of issue numbers, empty when missing."""
> 268:        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
> 409:        handback = {"missing": f"{HANDBACK[role]}: {e}"}
> 685:        if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing":
> 1304:    they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an approve keeps every ask."""
> 1308:                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
> 1313:        if c != "missing" and c not in ids:
> 1316:    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
> 1318:        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
> 1379:        missing = [k for k in keys if not filled(x.get(k))]
> 1380:        if missing:
> 1381:            bad.append(f"{label} needs {', '.join(missing)}")
> 1386:    """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
> 1437:        return None, f"{name} is missing ({path})"
> 1501:    """Everything missing or broken in an agent's starting pack, checked by code before the agent starts."""
> 1509:            bad.append(f"{name} is missing")

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 675,700p dokima/agent.py
```

> lines += ["", escape_line(h["summary"])]
>     rows = plan_rows(plan) if isinstance(plan, dict) else {}
>     blockers = [r for r in card.raises_of(h) if r["kind"] == "blocker"]
>     failing = []
>     for k, c in rows.items():
>         on = [r for r in blockers if criterion_of(r, rows) == k]
>         if on:
>             why = [f"  - {field_icon(repo, 'blocker')} {card.escape(escape_line(r.get('text')))}" for r in on]
>             failing += failed_rows(repo, c.get("text"), why, c.get("source"))
>     for a in h.get("asks") or []:
>         if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing":
>             failing += failed_rows(repo, a.get("ask"), ["  - Nothing covers this"], a.get("source"))
>     return lines + ([""] + failing if failing else [])
> 
> 
> def opening(rec):
>     """The one plain sentence a run comment opens with: what the run did."""
>     role, h, passed = rec["role"], rec["handback"], rec["check"]["passed"]
>     if rec.get("unrecorded"):
>         return f"{who(role, rec.get('stage'))}'s run ended before posting its record."
>     if not passed and role == "worker":
>         return "The worker stopped early with its hand-back rejected by code."
>     if not passed:
>         return f"{who(role, rec.get('stage'))}'s run ended with its hand-back rejected by code."
>     if role == "planner" and h.get("kind") == "feature":
>         return f"The planner proposes a split into {len(h.get('stories') or [])} stories."

**Agent:** The plan's one test is sound. The second ask is dropped pending the owner's answer, so the plan can't be approved. Writing the hand-back now.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Planned one criterion: a card is saved only when what code draws differs.",
          "Changed an older card test: a current card now saves nothing on every run."],
  "decided": ["Left out the second criterion, saying skipped board events already never move a card."],
  "open": ["Asks the owner whether the second criterion can be left out."]
 },
 "verdict": "block",
 "summary": "The card criterion is well proven; the second ask has no criterion until you decide on the planner's question.",
 "raises": [
  {"kind": "blocker", "to": "owner", "label": "Second ask dropped",
   "text": "The ask that skipped board events never move a card has no criterion. A test for it already passes, which the plan check refuses. Keep it pinned anyway, or drop it?",
   "evidence": "Issue body lists two criteria; `plan.json` keeps one. `tests/test_quiet_board.py` 533.1 proves only the skip, not the columns."}
 ],
 "answers": [],
 "asks": [
  {"ask": "A card is written on an issue or pull request only when what code draws differs from it.", "source": "https://github.com/dokima-dev/dokima/issues/534", "criterion": "534.1"},
  {"ask": "Every event the board update skips would have left every card's column and pill unchanged today.", "source": "https://github.com/dokima-dev/dokima/issues/534", "criterion": "missing"}
 ],
 "behaviors": [
  {"criterion": "534.1", "one_behavior": true, "why": "One result: a card is saved only when its drawn text differs."}
 ],
 "edge_cases": [
  {"criterion": "534.1", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_quiet_cards.py::test_a_card_is_written_only_when_what_code_draws_differs", "only_its_behavior": true, "why": "Fails today on a person's change; passes when the save always skips a current card; never writes fails it."}
 ],
 "size": "ok"
}
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/revie
```

> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts
> rc=1

`13. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/A test for it already passes, which the plan check refuses. Keep it pinned anyway, or drop it?/Its test already passes, which the plan check refuses. Keep it pinned anyway, or drop it?/' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 534 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?; rm -rf /tmp/rv
```

> rc=0

**Agent:** I blocked the plan for [#534](https://github.com/dokima-dev/dokima/issues/534) (cards are rewritten only when they change), and the next step is yours. The plan has a good criterion and test for card saving, but it leaves out the issue's second ask. Code's check accepts the hand-back, which is in `/tmp/dokima-out/review.json`.

**The one criterion is well proven.**
- The test `tests/test_quiet_cards.py::test_a_card_is_written_only_when_what_code_draws_differs` fails today for the right reason: a person's change rewrites a card that is already current.
- In a scratch copy, making that check apply to every run (a one-line change in `dokima/card.py`) made it pass, along with the changed test in `tests/test_body.py`. The test also fails if a card is never written.
- It covers a fresh ask, only the issue's card being out of date, and only the pull request's card being out of date. Its scope (`dokima/card.py` and `AGENTS.md`) is right.

**The second ask has no criterion: "every event the board update skips would have left every card's column and pill unchanged today."**
- The planner says this is already true on main since [#555](https://github.com/dokima-dev/dokima/issues/555) (board runs only when a card can move).
- Its run log says it wrote a test for this that passes today. The plan check refuses new tests that already pass, so it dropped the criterion and asked you about it.
- No test in the repo proves it: the [#555](https://github.com/dokima-dev/dokima/issues/555) test only checks that those events are skipped, not that columns and pills stay the same.
- A plan review can't approve with an ask that nothing covers, so I sent the block to you. Sending it back to the planner would only bring the same question back.
- I couldn't answer the planner's question for you. I had no GitHub access to look for your own words in [#380](https://github.com/dokima-dev/dokima/issues/380) (cards and board update only when something can change).

**Decision for you:** keep the second ask with a test that already passes, or drop it. Reply `/plan` with your answer, or `/review` to go on without it.

**Agent:** The background job that failed was a full test-suite run in my scratch copy. It broke because I deleted that copy while it was still running, so it says nothing about the plan. The review only relies on the targeted run, where the new test and `tests/test_body.py` passed with the fix applied. The full suite was never finished. The review hand-back is unchanged, and the next step is still yours.

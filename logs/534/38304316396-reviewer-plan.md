# reviewer (plan) for #534

Run: https://github.com/dokima-dev/dokima/actions/runs/38304316396

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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #534: Cards are rewritten only when they change
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 533 -->
> <!-- dokima-blocking: {"blocked_by": [533], "blocks": [], "loop": []} -->
> Cards on issues and pull requests are saved only when what they show changes.
> 
> **Plan**
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
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A card on an issue or pull request is written only when what code draws differs from it.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-534/te

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:5000])"; python3 -c "
import json;d=json.load(open('in/03-planner.json'));print(json.dumps(d,indent=1)[:3000])"; head -c 1500 parent.json
```

> {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38301376362",
>  "commit_before": "6425ca42d16751b33d8ed021b07ff8b6c3804bb7",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 2216,
>   "turns": 1,
>   "cost_usd": 0.5610656,
>   "tokens_in": 51583,
>   "tokens_out": 167
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/534/38301376362-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38301376362",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "Planned one criterion: a card is saved only when what code draws differs.",
>     "Changed an older card test: a current card now saves nothing on every run."
>    ],
>    "decided": [
>     "Left out the second criterion, saying skipped board events already never move a card."
>    ],
>    "open": [
>     "Asks the owner whether the second criterion can be left out."
>    ]
>   },
>   "verdict": "block",
>   "summary": "The card criterion is well proven; the second ask has no criterion until you decide on the planner's question.",
>   "raises": [
>    {
>     "kind": "blocker",
>     "to": "owner",
>     "label": "Second ask dropped",
>     "text": "The ask that skipped board events never move a card has no criterion. Its test already passes, which the plan check refuses. Keep it pinned anyway, or drop it?",
>     "evidence": "Issue body lists two criteria; `plan.json` keeps one. `tests/test_quiet_board.py` 533.1 proves only the skip, not the columns.",
>     "raised_by": "re

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "asks\|\"missing\"\|'missing'" dokima/agent.py | head -40; ls dokima
```

> 409:        handback = {"missing": f"{HANDBACK[role]}: {e}"}
> 684:    for a in h.get("asks") or []:
> 685:        if isinstance(a, dict) and str(a.get("criterion", "")).strip() == "missing":
> 866:                  ("The owner's asks", bullets(h.get("asks"), lambda a: f"{a.get('ask', '')} ({a.get('criterion', '')}, {a.get('source', '')})"))]
> 888:        return f"The planner proposes a split into {n} stories" + (" and asks you questions." if h.get("questions") else ".")
> 891:        return f"The planner planned this issue and asks you {q} question{'s' if q > 1 else ''}." if q else "The planner planned this issue."
> 1302:def problems_asks(r, ids):
> 1303:    """Everything wrong with a plan review's asks list: every ask the owner made, in their words, with a link to where
> 1304:    they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an approve keeps every ask."""
> 1305:    asks = r.get("asks")
> 1306:    if not isinstance(asks, list) or not asks:
> 1307:        return ["asks must list every ask in the owner's issue and comments, each {\"ask\": \"the owner's words\", "
> 1309:    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
> 1310:    good = [a for a in asks if isinstance(a, dict) and all(filled(a.get(k)) for k in ("ask", "source", "criterion"))]
> 1313:        if c != "missing" and c not in ids:
> 1316:    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
> 1471:                bad += problems_asks(data, plan_criteria(plan, 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_quiet_cards.py; git show HEAD -- tests/test_body.py; python3 -m pytest -q tests/test_quiet_cards.py tests/test_body.py 2>&1 | tail -30
```

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
> card.yml keeps running on every event, because GitHub sends no event for a blocked-by link a person adds by hand and
> the card must still show it at once. What changes is the write: `card.main` saves the issue's card, and writes the
> pull request's description, only when what code draws now differs from what is there. Until now that held only when
> the bot's own change started the run (card.yml sets `BY_BOT`); a person's comment or change rewrote both every time.
> 
> These tests run `card.main` as card.yml runs it for a person's change (`BY_BOT` "false" or unset), with GitHub faked
> by tests/test_body.py's recorder, and count the writes it makes.
> """
> import os
> import sys
> 
> sys.path.inse

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "changed_only\|BY_BOT" dokima/card.py | head
```

> 791:            draw(repo, m, issue_pr(repo, m), noted={int(number): m in now}, cache=cache, changed_only=True)
> 853:            draw(repo, n, pr_number or issue_pr(repo, n), cache=cache, changed_only=True)
> 920:        before, now = draw(repo, number, pr_number, cache=cache, changed_only=os.environ.get("BY_BOT") == "true")
> 927:def draw(repo, number, pr_number, plans=None, noted=None, cache=None, changed_only=False):
> 930:    Returns the blocking links and loop its card showed before and shows now. With `changed_only`, a card that
> 953:    if not (changed_only and shows(current, top)) and body.save(repo, number, current, top):
> 961:    if pr and not (changed_only and described == (pr.get("body") or "")):

**Agent:** Checking the test against a quick fix in a scratch copy, then writing the review.

`6. Bash`
```
rm -rf /tmp/mut && cp -r /home/runner/work/dokima/dokima /tmp/mut && cd /tmp/mut && sed -i '920s/changed_only=os.environ.get("BY_BOT") == "true"/changed_only=True/' dokima/card.py && sed -n 920p dokima/card.py && python3 -m pytest -q tests/ 2>&1 | tail -3; sed -i '953s/changed_only and shows(current, top)/True/' dokima/card.py; python3 -m pytest -q tests/test_quiet_cards.py 2>&1 | tail -2
```

> Command did not complete within its 120s timeout and was moved to the background (ID: b0uhtxlni). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/96c3d325-e68e-40d2-b23b-b67e8b8fdff7/tasks/b0uhtxlni.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.
> Session cwd remains /home/runner/work/dokima/dokima; directory changes made by the backgrounded command do not apply to subsequent commands.

`7. Bash`
```
rm -rf /tmp/mut2 && cp -r /home/runner/work/dokima/dokima /tmp/mut2 && cd /tmp/mut2 && sed -i '920s/changed_only=os.environ.get("BY_BOT") == "true"/changed_only=True/' dokima/card.py && python3 -m pytest -q tests/test_quiet_cards.py tests/test_body.py tests/test_card*.py 2>&1 | tail -3; sed -i '953s/changed_only and shows(current, top)/True/' dokima/card.py; python3 -m pytest -q tests/test_quiet_cards.py 2>&1 | tail -2
```

> ........................................................................ [ 81%]
> .................................                                        [100%]
> 177 passed in 59.05s
> assert None is not None
> 1 failed in 0.09s
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
mkdir -p /tmp/dokima-out && cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Planned one criterion: a card is saved only when what code draws differs.",
          "Kept the older card test change: a current card now saves nothing on every run."],
  "decided": ["Dropped the board criterion, as the owner said."],
  "open": []
 },
 "verdict": "approve",
 "summary": "The plan keeps the one ask left after your answer, and its test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A card is written on an issue or pull request only when what code draws differs from it.",
   "source": "https://github.com/dokima-dev/dokima/issues/534",
   "criterion": "534.1"}
 ],
 "behaviors": [
  {"criterion": "534.1", "one_behavior": true, "why": "One result: a card is saved only when its drawn text differs."}
 ],
 "edge_cases": [
  {"criterion": "534.1", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_quiet_cards.py::test_a_card_is_written_only_when_what_code_draws_differs",
   "only_its_behavior": true,
   "why": "Fails today on a person's change; passes once every run skips a current card; fails if nothing is ever written."}
 ],
 "size": "ok"
}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 534 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#534](https://github.com/dokima-dev/dokima/issues/534) (cards are saved only when they change). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Your answer was followed:** you said to drop the board criterion, and the planner dropped it. The one remaining ask is covered by criterion 534.1: a card on an issue or pull request is written only when what code draws differs from it.
- **The test fails today for the right reason:** a person's change still rewrites a card that is already current (`tests/test_quiet_cards.py:63`).
- **The test proves the right thing:** in a scratch copy, I made every run skip a card that is already current. The new test then passed, and so did the card and body tests (177 passed). When I made the code never write a card, the new test failed.
- **The test covers the expected cases:** a new issue still gets its card. When only one card is out of date, only that one is rewritten.

I raised no blockers, and no earlier blocker was waiting on me. The plan includes `AGENTS.md` in its scope. That file still says only the bot's own changes skip a card that is already current, so the worker can correct that line.

I also started a full test run in a second scratch copy. I didn't wait for its results, and the approval doesn't depend on them.

`9. Bash`
```
cat /tmp/claude-1001/-home-runner-work-dokima-dokima/96c3d325-e68e-40d2-b23b-b67e8b8fdff7/tasks/b0uhtxlni.output
```

> before, now = draw(repo, number, pr_number, cache=cache, changed_only=True)
> ........................................................................ [ 93%]
> ...................................................................      [100%]
> 1075 passed in 563.72s (0:09:23)
> assert None is not None
> 1 failed in 12.14s
> 
> [exited with code 0]

**Agent:** The full test run finished: all 1075 tests passed in the scratch copy where every run skips a card that is already current. So the change the plan asks for doesn't break any other test. That copy also confirmed that the new test fails when the code never writes a card.

My approval of the plan for [#534](https://github.com/dokima-dev/dokima/issues/534) (cards are saved only when they change) stands, and `/tmp/dokima-out/review.json` is unchanged.

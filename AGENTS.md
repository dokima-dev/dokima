# Dokima

*The one place for how Dokima works, for people and for every agent (Claude, Codex and others read this file; their own files just point here). Decisions land here once they're made; the issues hold how we got there. Items marked (planned) are decided but not built yet.*

## Working in this repo

- Python 3.12. Run the tests with `pytest -q`; tests live in `tests/`.
- Never change `.github/workflows/`, `dokima/card.py` or `dokima/roles/` unless the issue explicitly asks.
- Keep changes small. Add no dependencies unless the issue asks.
- Read this whole file before changing how Dokima works.
- Whenever an agent or assistant refers the owner to an issue or pull request, it writes the number as a clickable link followed by a few plain words saying what it is about, e.g. [#289](https://github.com/dokima-dev/dokima/issues/289) (raises and answers). Never a bare number.

## The picture

Dokima is Jira for agent teams. You are the project manager: you define the work, define what "done" means, and set priorities. Your team is remote engineers: agents that each take one narrow task, do it on their own machine, and hand back work you can check. They plan, build and review in the open on GitHub, the way people already work. You approve the plan before work starts and the result before it merges.

GitHub is the office: issues are the tasks, pull requests are the work, comments and reviews are the conversation, checks are the proof, and the project board is the overview. Nothing new to learn.

## The core rule

**A stage never edits what another stage owns. It proposes, and the owner routes it with a command.**

- The plan (criteria and their tests) belongs to the planner, approved by the owner.
- The code belongs to the worker.
- The reviewer owns nothing; it judges and proposes.
- A command depends only on the stage it starts, never on the stage it comes from: every run rebuilds its starting pack from the issue's full history, so any stage can be re-entered at any time.

## Principles

- **Nothing merges until it's proven.** Every promise in a plan has its own check, and GitHub's verdict on that check is the proof. No model's say-so counts.
- **Code owns the structure; models fill in content.** Everything that must be exact (freezing plans, posting stage comments, building starting packs, drawing cards, setting labels and board fields) is done by code. Models write only the plan, the code and their findings.
- **Use what GitHub already has.** Comments, reviews, checks, branch protection, CODEOWNERS, project boards, merge queue. Build only the thin glue GitHub lacks.
- **Humans are free; bots are compliant.** People can do anything, on the record. Agents work inside fixed rules: they can't approve, can't change the workflows that judge them, and can't widen their own scope.
- **Everything lives on GitHub.** One permanent history per issue, across every agent and device: plans, attempts, failures, reviews.
- **Fail closed.** Missing proof, a missing reviewer or a broken check blocks; nothing is waved through, and a failure always says why on the issue.
- **Agent-neutral and language-neutral.** No hard-coded people, vendors or languages. Approvers come from CODEOWNERS; each agent plugs in through a small adapter; instructions (including how many sub-agents to use) live in prompts, not code.
- **Match the output to the human brain bottleneck.** The owner's attention is the scarcest thing in the river: whatever the JSON holds, a card shows only what the owner needs at a glance, and the rest goes in folds.
- **Small and lean.** One issue, one PR. Fold related things together. Extras (the board, merge queue) are optional and never required.

## Roles

- **Owner:** decides. Approves plans and results, routes proposals. Only a code owner's commands count.
- **Planner:** turns a rough issue into a plan: an objective, acceptance criteria, scope, and a test for every criterion written before any code. It judges the ask first and raises a doubt only with evidence, as a question for the owner. It may change or delete an older test when the plan makes it wrong, with a reason the owner sees. It proposes splits; it never writes code.
- **Worker:** builds what the approved plan says, on a fresh machine, within scope, until its tests pass. It never changes the plan's tests.
- **Reviewer:** checks the plan, then the result (a real PR review). It blocks only on a promise with no proof or a proof that proves nothing, and raises the issues it finds outside this one.
- **Code:** everything that must be exact (see the principles).

## The flow (the river)

1. **Issue.** The owner writes what they want, in plain words, rough or detailed.
2. **`/plan`.** The planner always plans, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. If the plan has questions, the river stops and mentions the owner, who answers with `/plan` and their words, or says `/review` to go on with the planner's assumptions. Otherwise the reviewer starts by itself.
3. **Plan review.** A block sends it back to the planner by itself. An approval stops for the owner.
4. **`/work`.** The owner's approval. An approved split files its stories as sub-issues with blocked-by links; each story then goes through the flow on its own. Otherwise the worker builds on a fresh machine and opens the PR.
5. **Code review.** The reviewer starts by itself when the worker finishes. Every blocker names who fixes it: the worker for code, the planner for a test shown too weak. A block sends it back to the worker by itself, or to the planner when any blocker is the planner's; that test fix goes planner, plan review, worker, code review, and an approved re-plan whose criteria are unchanged goes straight to the worker, while one that changes any criterion, or comes after the owner spoke, waits for `/work`. An approval stops for the owner.
6. **Merge.** The owner approves and merges. On autopilot, the reviewer's approval with every check green on the pull request's head merges it by itself, and the issue gets one line, `Autopilot: merged PR #N`; a pull request that changes a workflow file, or a merge that cannot happen, stops for the owner and says why on the pull request.

On autopilot, the river runs a whole issue tree end to end and stops for the owner only where the owner must decide (planned, story 2 of #205); `/autopilot start` and `/autopilot stop` switch it on and off. On an issue on autopilot (its own `autopilot` label), an approved plan starts the worker and an approved split files its stories by themselves, each with one line on the issue where the owner would have typed `/work` (`Autopilot: plan approved, starting work`, `Autopilot: split approved, filing its stories`). On autopilot a blocked issue plans only after its blockers merge, so no plan goes stale while it waits: an issue with an open blocker never starts its planner by itself, and when a plan is approved while a blocker is open, nothing is built, no line stands in for `/work`, and its card names the open blockers and says it plans again when they close, mentioning no one; when GitHub cannot list the blockers, nothing starts and the issue says why. A plan with questions goes to the plan reviewer, which judges each question's assumption: it goes on only when the assumption changes neither how the system works nor what it costs and matches the owner's own words, word for word, in the issue, a code owner's comment on it or AGENTS.md; any other question stops for the owner. When GitHub cannot say whether the issue is on autopilot, the river stops and says so. When an issue closes, every issue on autopilot whose blocked-by issues have now all closed starts a fresh planner, once and never the old plan's worker, with one line `Autopilot: blockers merged, starting plan` where the owner would have said `/plan`, unless something started on it since its plan was approved, such as the owner's own `/plan` or `/work`; and when the top issue closes, its whole tree goes off autopilot. Closes are handled one at a time, in one queue for the repo (autopilot.yml), and an issue already planned, running or started is never started again.

Agents work things out between themselves. The river stops and mentions the owner only on questions, approvals, an escalation, a hand-back code rejected, or three blocking reviews in a row at one stage since the owner last spoke. Every card ends with a **Next** line saying what happens next or what is the owner's to do.

## Commands

A command is the first word of an owner's comment on the issue or its PR, or of a PR review's summary submitted as a comment or a change request. Everything after it, and every other comment, review and line note, reaches the agent.

- `/plan`: the planner (re)plans. `/work`: the worker builds, or an approved split is filed. `/review`: the reviewer looks again; on an issue it grades the plan, on a PR the work.
- `/autopilot start` / `/autopilot stop`: put the issue, or the issue a PR was built for, and every sub-issue under it at every level on or off autopilot (the `autopilot` label). It leaves one comment where it was said naming every issue it switched. `/autopilot start` picks up what is waiting: an approved plan of that issue still waiting for `/work` starts the worker, and an approved split not yet filed is filed, as on autopilot; the issue itself, with no sub-issues, no plan and nothing open to wait for, starts its planner with one line `Autopilot: switched on, starting plan` where the owner would have said `/plan`; every issue under it, at every level, with no sub-issues, no plan and nothing open to wait for starts its planner; and every pull request in the tree its code review approved merges as in step 6. A split filed by `/work` on autopilot puts its stories on autopilot and starts the ones with nothing to wait for.
- `/issue`: file the issues the agents raised (planned).
- No command, nothing starts. Bots never start anything. An Approve never starts anything: it only ever means merge.
- Reviewers never start on the owner's command alone except `/review`; otherwise the river starts them.

## Raising and answering

The planner, the worker and the reviewer raise and answer only through two fields of their hand-back, raises and answers. Each agent starts with the open raises sent to it, each with its ID, and code rejects a hand-back that leaves one unanswered. Code stamps who raised each one and its ID; agents never write either.

What code detects and raises itself, never an agent:

- **Work outside the plan**: a change outside the plan's scope is undone before the judges see it, and the owner sees what was dropped. Example: the worker edits `dokima/board.py` on an issue whose scope is `dokima/card.py`.
- **A failing test**: the full suite or a criterion's check goes red on GitHub, and the work goes back to the worker. Example: `tests/test_card.py::test_next_line` fails on the pull request's head commit.
- **Red main**: a required check fails on main itself, not on a pull request. Example: the all tests check fails on main right after a merge.
- **A merge conflict**: GitHub cannot bring a pull request up to date with main, and code says why on it. Example: main changed the same lines of `dokima/card.py`, so the branch cannot be updated.
- **A rejected hand-back**: the checker refuses a hand-back, says why on the issue, and nothing is posted. Example: a worker's `work.json` leaves a raise sent to it unanswered.
- **A workflow file change**: a pull request that changes a workflow file stops for the owner. Example: a build touches `.github/workflows/board.yml`, so it waits for the owner's approval.
- **Three blocks in a row**: three blocking reviews at one stage since the owner last spoke stop the river for the owner. Example: the code reviewer blocks the third build in a row, so the owner decides with `/plan`, `/work` or `/review`.

What agents raise by judgment, one of three kinds:

- A **question** is something only the one it is for can decide, and says the reading the agent went on. The planner asks the owner only where the owner's words allow two readings and no principle or earlier decision settles it; it plans on its reading, so the owner may skip answering. A doubt about the ask (already fixed, patching a symptom, overlapping an open issue) is a question for the owner that carries its evidence.
- A **blocker** is something that must be fixed before the work goes on, sent to whoever fixes it: the planner for a weak test, a test that cannot pass as written, a wrong plan or an ask with no criterion; the worker for the code. The worker never asks the owner: the plan is the contract, and disagreements reach the owner by escalation.
- An **issue** is a real problem outside this issue, worth its own issue; it is for no one.

Who may send a question or a blocker to whom is code's table (`dokima/raises.py`), row for row:

| Raised by | To |
|---|---|
| planner | owner |
| worker | planner (through the reviewer, who answers it first) |
| reviewer | planner, worker or owner |

Two tiers of autonomy:

- **Always on:** the reviewer settles anything addressed to an agent before it goes on, and confirms the issues the planner or the worker raised before they are filed.
- **On autopilot only:** the plan reviewer answers a planner's question for the owner only with the owner's own words as evidence, quoted with where they said them, which code checks are really there; anything else waits for the owner (see the flow).

## Where specs go

Every spec, answer or scope change the owner gives lands on GitHub, never only in chat, so every session, human or agent, finds it there.

- On an existing issue it goes in as a comment: a `/plan` comment when the planner should pick it up, a plain comment on a parked issue.
- An issue's original text is frozen: nobody edits it, and changes are comments. This is the owner's ask below the marker; code still redraws the card above it (see the issue body).
- A new idea becomes a new issue, with the spec in its body.

Example: the owner says in chat that a card's Next line should name the owner. On the open issue that becomes a comment `/plan The Next line names the owner`; on a parked issue, a plain comment saying the same; an unrelated idea from the same chat becomes a new issue with the spec in its body.

## The board

- Columns are stages: Backlog, Plan, Work, Review, Done. Every new item lands in Backlog. Each card's column and pill are computed from its issue's state on GitHub now, never from the event that started the board run: every event about an issue or its pull request and the end of every run that did not fail put both cards there, so the next event fixes a dropped or late one, and an issue and its pull requests share one board queue that keeps the newest recompute. An open issue with no record is in Backlog. Otherwise it is in the column of the newest stage started since its newest record, else where the river placed it after that record, but never ahead in a stage not started yet: an approved plan stays in Plan until its worker starts, and a built one stays in Work until its code review starts. A worker starts with a code owner's `/work`, the bot's Autopilot line that starts it, or its run card; a code review starts once the bot puts up its run card, even queued, or its record; the same words from anyone else start nothing. An open pull request goes with its issue. A closed issue, and a merged or closed pull request, sits in Done with no pill, whatever its labels. Every 15 minutes a sweep rechecks the issues and pull requests updated since the last sweep that succeeded, each with its pull request or issue, and every card when GitHub cannot say what changed. A card whose state GitHub cannot give keeps its column and pill, and the run fails naming it; a failed run shows Needs you on its cards at once, in its own stage's column, even when GitHub cannot be read.
- "Needs you" is a pill on the card, sorted to the top of each column, set exactly when the river stops for the owner and cleared otherwise. No swimlanes. New commits and finished checks never set or clear it; a code owner's `/plan`, `/work` or `/review`, on the issue or its pull request or as a review's summary (never an Approve), clears it at once on both cards, leaving them in their columns. A closed issue or a merged or closed pull request never shows it. A parent shows it only for its own stop, never for its stories'.
- Every merge's board run sweeps each issue and pull request on the board: Needs you where the river's last word on its issue stopped for the owner and no code owner has answered with a command since (a pull request follows its issue), Autopilot on every other open item on autopilot, and no pill on the rest. A card whose history cannot be read keeps its pill, and the run fails naming it.
- "Autopilot" is a pill in the same place, on every card of an issue on autopilot and of its open pull request, set and cleared with the `autopilot` label; Needs you takes its place while the river stops for the owner, so a card never shows both. A pull request built for an issue on autopilot carries the label too.
- One Autopilot view, a table filtered to `label:autopilot is:open`, lists every open issue and pull request on autopilot; merged and closed ones keep the label but leave the view. Code adds it the first time a tree goes on autopilot, from the board run of the tree's top issue only, and a refused view fails that run naming it. The board run of a merge changes an Autopilot view still filtered to the old `label:autopilot` to `label:autopilot is:open`, leaves any other filter alone, and fails naming the view if GitHub refuses. The Autopilot option of the Action field is a one-time step on the board, like Needs you; code never edits the field's options.
- `DOKIMA_BOARD=org/number REPO=owner/name python3 -m dokima.scan` names every closed card outside Done or with a pill, every open card in the wrong column or in none, every issue or PR card that does not show the card Dokima draws for its issue now, and every card GitHub will not give, with its reason, and exits 1; otherwise it prints `All N cards on the board match their state.` and exits 0. It only reads, and never puts anything right.
- Priority is a field (Blocker, High, Parked). Blocker is set by code, never by hand, on every open issue that blocks another open issue by GitHub's blocked-by links, read when an issue closes or reopens and every 15 minutes; otherwise the pill follows the issue's high or parked label, and with both, High wins. When GitHub cannot list an issue's links, its pill stays and the board run fails naming it.

## The issue body

The body has two parts split by a fixed marker. Above it, the current-state card, redrawn by code every round. Below it, the owner's original ask, exactly as written. While an issue has no plan, its card shows no plan line, the owner's ask shows open so it reads first, and its Definition of Done sits below the ask instead, the one line code writes below the marker. Once planned, the ask moves into a fold titled Original issue, closed by default, and the Definition of Done is the card's last line again; a split's sub-issue, whose text code quotes from the parent's approved plan, is folded the same way even before its own plan, with its Definition of Done below the fold. An ask saved the other way is redrawn this way next time. The pull request carries the same Original issue fold between its card and its Closes line, where a `#` right after a closing keyword in the owner's words is written `&#35;`, so only the Closes line closes an issue. Code only writes above the marker, apart from that line, and checks the owner's part is unchanged before saving, or refuses, leaves the body as it was and says why in a comment on the issue. A fresh ask gets the marker on its first redraw, with its whole body kept below it. The card and the planner both save through `dokima/body.py`.

## Agent records and cards

Every agent run posts one comment, written by code: one plain sentence on top saying what the run did, the short version the owner needs (the plan, its questions or the split; the worker's own words on what it changed, linking its pull request, or why it stopped; the criteria a review blocks on and its proposed issues), the long parts in folds drawn by the same code as the issue card, the full JSON record in the last fold, and a footnote with the model, time, turns, tokens, API-equivalent cost and a one-click link to the run's whole conversation. Those comments are the permanent records; only comments the bot posted count as records. The card on top of the issue is drawn from them (planned). Its Blocked by and Blocks lines are GitHub's own blocked-by links, read each time the card is drawn, so a link a person adds or removes by hand shows on both issues' cards with no comment; when GitHub cannot list them, the card says GitHub's reason. GitHub announces no event for such a link, so card.yml redraws on every change or comment a person makes on an issue, along with the card of every issue it is linked to whose links changed, and every 15 minutes rewrites the cards whose links changed, and every issue card and PR card that does not show its issue's state now, open or closed, looking only at the issues and pull requests updated since the last 15-minute sweep that succeeded started (an update to either redraws both); when GitHub cannot list earlier sweeps, or none has succeeded yet, it rechecks every card and its log says why, and a card it cannot redraw is named and fails the run while the rest are still put right. The Definition of Done shows Code review running, with the card's in-progress icon, from the bot's code review run card after the newest build until its record, and All tests running while the full suite runs; card.yml redraws the issue and PR cards when the full suite starts and when that run card goes up, in the issue's own queue, and no other comment the bot posts redraws them. Issues that block each other, directly or through others, are named on every card in the loop; on autopilot each gets one comment mentioning the owner and the Needs you pill. Each run also gets one live card from queued to done (planned, #164).

## Splitting and the graph

- Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
- 2 to 5 children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
- The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
- When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
- When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.

## Changing scope

Never change the scope of an issue silently. Every change of scope is a comment or a native GitHub link.

- **Splitting** uses native sub-issues, each linking back to the parent. This is how `/work` files a split.
- **Merging or replacing** closes the old issue as a duplicate of the new one. GitHub links both ways.
- **Moving scope between issues** gets one short comment on each side ("moved X to #Y"). GitHub cross-links them, so the trail is two clicks either way.
- **A big reshuffle** of several issues closes the old ones as replaced by new ones that link back, instead of rewriting them.

## Identity and safety

- Agents act as the repo's own GitHub App (bot), never as a person. The bot can't approve, can't push workflow changes, and can't change settings.
- A build that changes a workflow file pauses until the owner approves it on GitHub; only then does a key held behind that approval push it (planned).
- Every run happens on a fresh, isolated machine with no access to the owner's computer. Agents hold no GitHub key while they work; code checks their output, then posts it.
- A chat agent may act as the owner's proxy with the owner's token, logged; the bot's own comments never start anything.
- Agent commits credit the owner as co-author (planned).

## Decisions log

- No hidden tests: in a public repo nothing stays hidden; the planner writing the tests covers most of the need.
- Approve on a PR only means "approve the result to merge".
- Tests map to criteria by the criterion number inside each test; criterion numbers are never reused.
- One PR per issue; replaced issues close as duplicates of what replaces them.
- Real GitHub reviews for code; comments for plans.
- Each repo declares its own setup and test command; Dokima never needs to understand a language (planned).
- Dokima lives in the `dokima-dev` organization so its bot can keep the project board and use the merge queue; on personal repos those extras fall back or are skipped.
- Onboarding is a few minutes from one link, never overwrites existing labels or files, and Dokima onboards itself first (planned).

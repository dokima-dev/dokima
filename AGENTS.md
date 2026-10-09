# Dokima

*The one place for how Dokima works, for people and for every agent (Claude, Codex and others read this file; their own files just point here). Decisions land here once they're made; the issues hold how we got there. Items marked (planned) are decided but not built yet.*

## Working in this repo

- Python 3.12. Run the tests with `pytest -q`; tests live in `tests/`.
- Never change `.github/workflows/`, `dokima/card.py` or `dokima/roles/` unless the issue explicitly asks.
- Keep changes small. Add no dependencies unless the issue asks.
- Read this whole file before changing how Dokima works.

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
- **Planner:** turns a rough issue into a plan: an objective, acceptance criteria, scope, and a test for every criterion written before any code. It judges the ask first and raises a concern only with evidence. It may change or delete an older test when the plan makes it wrong, with a reason the owner sees. It proposes splits; it never writes code.
- **Worker:** builds what the approved plan says, on a fresh machine, within scope, until its tests pass. It never changes the plan's tests.
- **Reviewer:** checks the plan, then the result (a real PR review). It blocks only on a promise with no proof or a proof that proves nothing, and ends with a list of proposed issues.
- **Code:** everything that must be exact (see the principles).

## The flow (the river)

1. **Issue.** The owner writes what they want, in plain words, rough or detailed.
2. **`/plan`.** The planner always plans, on its best reading, and lists any questions with the reading it planned for. Too big: it proposes a split. If the plan has questions, the river stops and mentions the owner, who answers with `/plan` and their words, or says `/review` to go on with the planner's assumptions. Otherwise the reviewer starts by itself.
3. **Plan review.** A block sends it back to the planner by itself. An approval stops for the owner.
4. **`/work`.** The owner's approval. An approved split files its stories as sub-issues with blocked-by links; each story then goes through the flow on its own. Otherwise the worker builds on a fresh machine and opens the PR.
5. **Code review.** The reviewer starts by itself when the worker finishes. Every blocker names who fixes it: the worker for code, the planner for a test shown too weak. A block sends it back to the worker by itself, or to the planner when any blocker is the planner's; that test fix goes planner, plan review, worker, code review, and an approved re-plan whose criteria are unchanged goes straight to the worker, while one that changes any criterion, or comes after the owner spoke, waits for `/work`. An approval stops for the owner.
6. **Merge.** The owner approves and merges. On autopilot, the reviewer's approval with every check green on the pull request's head merges it by itself, and the issue gets one line, `Autopilot: merged PR #N`; a pull request that changes a workflow file, or a merge that cannot happen, stops for the owner and says why on the pull request.

On autopilot, the river runs a whole issue tree end to end and stops for the owner only where the owner must decide (planned, story 2 of #205); `/autopilot start` and `/autopilot stop` switch it on and off. On an issue on autopilot (its own `autopilot` label), an approved plan starts the worker and an approved split files its stories by themselves, each with one line on the issue where the owner would have typed `/work` (`Autopilot: plan approved, starting work`, `Autopilot: split approved, filing its stories`). On autopilot a blocked issue still plans, but its worker waits until every blocker closes, with one line `Autopilot: plan approved, waiting for #A and #B to close` naming the open ones, and then starts by itself with `Autopilot: blockers closed, starting work`, once, and only while its newest plan is approved; when GitHub cannot list the blockers, the worker does not start and the issue says why. A plan with questions goes to the plan reviewer, which judges each question's assumption: it goes on only when the assumption changes neither how the system works nor what it costs and matches the owner's own words, word for word, in the issue, a code owner's comment on it or AGENTS.md; any other question stops for the owner. When GitHub cannot say whether the issue is on autopilot, the river stops and says so. When an issue closes, every issue on autopilot whose blocked-by issues have now all closed starts its planner, with one line `Autopilot: blockers merged, starting plan` where the owner would have said `/plan`; a parent whose last sub-issue closes closes too, saying its whole tree is done, which counts as a close one level up; and when the top issue closes, its whole tree goes off autopilot. Closes are handled one at a time, in one queue for the repo (autopilot.yml), and an issue already planned, running or started is never started again.

Agents work things out between themselves. The river stops and mentions the owner only on questions, approvals, an escalation, a hand-back code rejected, or three blocking reviews in a row at one stage since the owner last spoke. Every card ends with a **Next** line saying what happens next or what is the owner's to do.

## Commands

A command is the first word of an owner's comment on the issue or its PR, or of a PR review's summary submitted as a comment or a change request. Everything after it, and every other comment, review and line note, reaches the agent.

- `/plan`: the planner (re)plans. `/work`: the worker builds, or an approved split is filed. `/review`: the reviewer looks again; on an issue it grades the plan, on a PR the work.
- `/autopilot start` / `/autopilot stop`: put the issue, or the issue a PR was built for, and every sub-issue under it at every level on or off autopilot (the `autopilot` label). It leaves one comment where it was said naming every issue it switched. `/autopilot start` picks up what is waiting: an approved plan of that issue still waiting for `/work` starts the worker, and an approved split not yet filed is filed, as on autopilot; the issue itself, with no sub-issues, no plan and nothing open to wait for, starts its planner with one line `Autopilot: switched on, starting plan` where the owner would have said `/plan`; every issue under it, at every level, with no sub-issues, no plan and nothing open to wait for starts its planner; and every pull request in the tree its code review approved merges as in step 6. A split filed by `/work` on autopilot puts its stories on autopilot and starts the ones with nothing to wait for.
- `/issue`: file the reviewer's proposed issues (planned).
- No command, nothing starts. Bots never start anything. An Approve never starts anything: it only ever means merge.
- Reviewers never start on the owner's command alone except `/review`; otherwise the river starts them.

## Questions

Only the planner asks the owner, as a plain list inside its plan, and only where the owner's words allow two readings and no principle or earlier decision settles it. Each question says which reading it planned for, so the owner may skip answering. The worker and the reviewer never ask: the plan is the contract, and disagreements reach the owner by escalation. On autopilot the plan reviewer judges each question's assumption against the owner's words (see the flow).

## The checks

- A pull request's checks follow its Definition of Done, in order: All tests (every test in the repo), Acceptance criteria (passes only when every criterion's own check, named by its number and words, passed), then Acceptance test (the End-to-end test on a feature, once #233 adds it), then Code review and Owner approval.
- main's branch rule requires the checks All tests and Acceptance criteria, and autopilot merges only when both passed on the pull request's head. When the rename to these names merges, the owner must switch the rule from all tests and all done-whens passed to All tests and Acceptance criteria.

## The board

- Columns are stages: Backlog, Plan, Work, Review, Done. Every new item lands in Backlog.
- "Needs you" is a pill on the card, sorted to the top of each column, set exactly when the river stops for the owner and cleared otherwise. No swimlanes.
- "Autopilot" is a pill in the same place, on every card of an issue on autopilot and of its open pull request, set and cleared with the `autopilot` label; Needs you takes its place while the river stops for the owner, so a card never shows both. A pull request built for an issue on autopilot carries the label too.
- One Autopilot view, a table filtered to `label:autopilot is:open`, lists every open issue and pull request on autopilot; merged and closed ones keep the label but leave the view. Code adds it the first time a tree goes on autopilot, from the board run of the tree's top issue only, and a refused view fails that run naming it. The board run of a merge changes an Autopilot view still filtered to the old `label:autopilot` to `label:autopilot is:open`, leaves any other filter alone, and fails naming the view if GitHub refuses. The Autopilot option of the Action field is a one-time step on the board, like Needs you; code never edits the field's options.
- The river moves each card to the stage now running. Priority is a field (Blocker, High, Parked) that follows the issue's blocker, high or parked label; with two, the higher wins.

## The issue body

The body has two parts split by a fixed marker. Above it, the current-state card, redrawn by code every round. Below it, the owner's original ask, open, exactly as written; only a split's sub-issue, whose text code quotes from the parent's approved plan, keeps it folded under Original issue. An ask folded before this opens on its next redraw. Code only writes above the marker and checks the owner's part is unchanged before saving, or refuses, leaves the body as it was and says why in a comment on the issue. A fresh ask gets the marker on its first redraw, with its whole body kept below it. The card and the planner both save through `dokima/body.py`.

## Agent records and cards

Every agent run posts one comment, written by code: one plain sentence on top saying what the run did, the short version the owner needs (the plan, its questions or the split; the worker's own words on what it changed, linking its pull request, or why it stopped; the criteria a review blocks on and its proposed issues), the long parts in folds drawn by the same code as the issue card, the full JSON record in the last fold, and a footnote with the model, time, turns, tokens, API-equivalent cost and a one-click link to the run's whole conversation. Those comments are the permanent records; only comments the bot posted count as records. The card on top of the issue is drawn from them (planned). Each run also gets one live card from queued to done (planned, #164).

## Splitting and the graph

- Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
- 2 to 5 children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
- The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
- When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.

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

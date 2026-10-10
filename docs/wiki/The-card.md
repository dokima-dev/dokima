# The card

This page explains every part of the card on top of an issue and of the records each run posts below it.

## Where you see it

The card sits at the top of the issue and at the top of its pull request, so you see one status in both places. Code draws it from the run records and from GitHub's own checks and reviews, never from what an agent says.

## The status line

Under the plan's summary, the card shows the stage the issue is in:

- **Backlog**: no agent has run yet.
- **Plan**: the planner or the plan review is running or done.
- **Work**: the worker is building, or a split's stories are filed.
- **Review**: the code review is running or done.
- **Merged**: the pull request merged, shown with the merged icon.

When it is your turn, the line adds Needs you and what you must do, for example "Say /work to build the plan".

Below it, a links row leads to the latest run, the issue, the pull request and its files changed.

## Pills on the board

On the project board, a card can carry a pill:

- **Needs you**: you must decide something.
- **Autopilot**: the issue is on autopilot.

A card never shows both. Needs you takes Autopilot's place while it waits for you.

## Links to other issues

- **Related**: issues that touch the same thing.
- **Blocked by**: issues that must close first.
- **Blocks**: issues waiting on this one.

## Acceptance criteria

Each acceptance criterion has a circle that shows GitHub's verdict on its check:

- **passed**: its check went green on the pull request's latest commit.
- **failed**: its check went red.
- **running**: its check is still running.
- **not started**: no check has run yet.

The words of the criterion link to its check. Under it, one Verified by line per test says in plain words what the test proves, and links to the test. A Source link leads to where you asked for it.

Non-functional requirements follow in a fold, drawn the same way.

## Definition of Done

The last row shows three circles:

- **All tests**: the whole test suite passed.
- **Code review**: the reviewer's code review passed or failed.
- **Owner approval**: a code owner approved the pull request, or merged it.

You approve a plan by saying `/work`. You approve the result with Approve on the pull request, and merging it counts the same.

## Run records

Each run posts one comment below the issue. Its icon names who ran: the planner, the worker, the plan review or the code review. A passed or failed icon says whether code accepted the run's hand-back.

Its first sentence says what the run did. Then comes the short version you need:

- **Question**: what the planner asks you, with the reading it planned for.
- **Blocker**: what a review blocks on, and who fixes it.
- **Note**: what a review noticed that blocks nothing.
- **Outside the plan**: a change no criterion asked for.
- **Issue found**: a problem outside this issue, proposed for you to file.
- **Still open**: what the run says the previous step left open.

A step taken on autopilot posts no record. It posts one plain line in place of your command, such as "Autopilot: plan approved, starting work".

The long parts sit in folds, with the full record in the last one.

The **Next** line says what happens next, or what is yours to do.

The footnote, marked with the stats icon, gives the model, time, turns, tokens and cost at API prices. It links to the run's whole conversation.

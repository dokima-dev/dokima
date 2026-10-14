# Autopilot

Autopilot lets a whole issue tree run end to end, stopping only where you must decide. It is opt-in, per tree, and still traces every step to you: your `/autopilot start`, and your own words for any question it settles.

## Switching it on and off

| Command | Effect |
|---|---|
| `/autopilot start` | Adds the `autopilot` label to the issue and every sub-issue at every level. Leaves one comment naming each issue it switched. |
| `/autopilot stop` | Removes the label from the whole tree. Starts nothing. |

The `autopilot` label is the switch. No other label starts or steers anything.

## What `/autopilot start` picks up

- An approved plan waiting for `/work` → the worker starts.
- An approved split not yet filed → its stories are filed.
- An issue with no plan, no sub-issues and nothing open blocking it → its planner starts.
- A last run that died with no record → that stage starts again.
- Any PR in the tree whose code review approved → the merge gate runs and it merges.

## What changes on autopilot

Where you'd have typed a command, the bot posts one line instead, so the trail shows it:

| Moment | Line on the issue |
|---|---|
| Plan approved | `Autopilot: plan approved, starting work` |
| Split approved | `Autopilot: split approved, filing its stories` |
| Switched on, nothing to wait for | `Autopilot: switched on, starting plan` |
| Its blockers all closed | `Autopilot: blockers merged, starting plan` |
| Merge gate passed | `Autopilot: merged PR #N` |
| Joined the merge queue | `Autopilot: PR #N joined the merge queue` |
| GitHub holds it for review | `Autopilot: PR #N waits for your approval before it merges` |

## Questions on autopilot

The plan reviewer may answer a planner's question for you, but only when:

- it quotes **your own words, word for word**, from the issue, a code owner's comment on it, or `AGENTS.md`, and code finds them there, and
- the reading changes neither how the system works nor what it costs.

Anything else stops for you. More than 3 questions always stops.

## Blocked issues

- An issue with an open blocker never starts its planner by itself.
- A plan approved while a blocker is open builds nothing. The card says it plans again when the blockers close.
- When an issue closes, every autopilot issue whose blockers are now all closed starts a fresh planner, once.
- When the top issue closes, its whole tree goes off autopilot.

## Merging

After the gate passes, autopilot asks GitHub to merge the exact head it tested. GitHub's own branch rules decide. Autopilot never merges:

- a PR that changes a file under `.github/workflows/`,
- when GitHub can't say which checks main requires,
- past a required approval, unless GitHub lets δokima's app bypass it.

Each of those stops for you and says why on the PR.

## Still stops for you

A question or blocker it can't settle on your words, an escalation, a rejected hand-back, three blocks in a row, a failed or stuck gate, a merge GitHub refuses, or GitHub failing to say whether the issue is on autopilot.

## On the board

Every card in the tree shows the **Autopilot** pill (replaced by **Needs you** while it waits on you). An **Autopilot** view lists every open item with the label.

# Commands

A command is the **first word of the first line** of a comment, on the issue or on its pull request. A PR review whose summary starts with a command counts too, when submitted as **Comment** or **Request changes**.

Everything after the command, and every other comment, review and line note, reaches the agent as context.

## Who may use them

Only **code owners**: the users on the `*` line of `.github/CODEOWNERS` (or the repo owner when there is none). Anyone else's command is ignored. Bots never start anything.

## The commands

| Command | On an issue | On its PR |
|---|---|---|
| `/plan [words]` | The planner plans, or re-plans with your words. | Same, for the issue the PR was built for. |
| `/work [words]` | Approves the plan (it needs a plan the reviewer approved). The worker builds and opens a draft PR. On an approved split, files the stories as sub-issues instead. | The worker builds again. |
| `/review [words]` | The reviewer grades the **plan**. Also: go on with the planner's assumptions instead of answering its questions. | The reviewer grades the **code**, then the merge gate runs. |
| `/autopilot start` | Puts this issue and every sub-issue under it on autopilot, and picks up what's waiting. See [[Autopilot]]. | Same, for the PR's issue tree. |
| `/autopilot stop` | Takes the whole tree off autopilot. Starts nothing. | Same; the PR loses the label too. |

Commands are case-insensitive. A PR is matched to its issue by its branch (`try/issue-N`) or its `Closes #N` line.

## What you see

1. Within seconds, a **queued card** goes up where the run's record will land.
2. The card moves through *setting up → agent working → checking*.
3. The same comment becomes the run's **record**: what it did, what it raised, a Stats fold, and the full JSON.
4. The last line, **Next:**, says what runs now or what's yours to do.

A command that can't start says why in that same comment and mentions you. If GitHub's hourly API budget is spent, it says when to try again.

## What is not a command

| Action | Effect |
|---|---|
| **Approve** on a PR | Only ever means "merge". Starts nothing. |
| A plain comment | Read by agents on their next run. Starts nothing. |
| Adding a label by hand | Starts nothing. (`autopilot` is set by `/autopilot`.) |
| A command from a non-code-owner | Ignored. |

## Manual runs (Actions tab)

| Workflow | Use |
|---|---|
| **agent** → Run workflow | Start a role (planner, reviewer, worker) on an issue number. Code owners only. |
| **fix** → Run workflow | Open a PR, as δokima's app, from a branch an agent pushed by hand. It merges only after all tests pass and you approve. |
| **audit** → Run workflow | Compare the repo's settings with what δokima needs; report drift on a pinned **Setup** issue. Also runs daily. |

## Planned

- `/issue`: file the issues agents raised.

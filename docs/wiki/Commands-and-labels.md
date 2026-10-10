# Commands and labels

This page lists every command and label Dokima reads today, what each does and who may use it.

## Who may use them

Only a code owner's commands count. Code owners are the people the repo's CODEOWNERS file names. Anyone else's command, and every comment a bot posts, starts nothing.

You give a command as the first word of a comment on the issue or its pull request. You may also give it as the first word of a pull request review's summary, submitted as a comment or a change request. Everything after the command, and every other comment, review and line note, reaches the agent.

An Approve on a pull request never starts anything. It only ever means merge.

## Commands

| Command | What it does |
|---|---|
| `/plan` | Starts the planner, which plans or re-plans the issue. Words after it reach the planner, so you answer its questions this way. |
| `/work` | Approves the newest plan and starts the worker, which builds it and opens the pull request. On an approved split it files the stories as sub-issues instead. |
| `/review` | Starts the reviewer again. On an issue it grades the plan; on a pull request it grades the work. |
| `/autopilot start` | Puts the issue, or the issue a pull request was built for, and every sub-issue under it on autopilot. It picks up what is waiting: an approved plan starts its worker, an approved split is filed, an issue with no plan starts its planner, and an approved pull request merges. |
| `/autopilot stop` | Takes the issue and every sub-issue under it off autopilot. It leaves one comment naming every issue it switched. |
| `/issue` | Files the reviewer's proposed issues. Planned: not built yet. |

With no command, nothing starts.

## Labels

You create these labels in your repo; the drift audit reports any that are missing. You add them on the issue's sidebar.

| Label | What it does |
|---|---|
| `plan` | Starts the planner, the same as `/plan`. Only a code owner's label counts; anyone else's starts nothing. |
| `work` | Starts the worker on the issue's plan as it stands. Removing it stops a running build. Only a code owner's label counts; anyone else's starts nothing. |
| `autopilot` | Marks an issue or pull request on autopilot and shows its Autopilot pill. `/autopilot start` and `/autopilot stop` set and clear it across a whole tree. Anyone with triage or write access adds it. |
| `high` | Sets the issue's Priority on the board to High. Anyone with triage or write access adds it. |
| `parked` | Sets the issue's Priority on the board to Parked. Anyone with triage or write access adds it. |

There is no Blocker label. Code sets the Blocker priority on every open issue that blocks another open issue by GitHub's blocked-by links, never by hand. Otherwise Priority follows the high or parked label; with both, High wins. Priority needs the optional project board; see [Configuration](Configuration).

To approve a plan, say `/work`.

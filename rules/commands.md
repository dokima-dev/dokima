## Commands

A command is the first word of an owner's comment on the issue or its PR, or of a PR review's summary submitted as a comment or a change request. Everything after it, and every other comment, review and line note, reaches the agent.

- `/plan`: the planner (re)plans. `/work`: the worker builds, or an approved split is filed. `/review`: the reviewer looks again; on an issue it grades the plan, on a PR the work.
- `/autopilot start` / `/autopilot stop`: put the issue, or the issue a PR was built for, and every sub-issue under it at every level on or off autopilot (the `autopilot` label). It leaves one comment where it was said naming every issue it switched. `/autopilot start` picks up what is waiting: an approved plan of that issue still waiting for `/work` starts the worker, and an approved split not yet filed is filed, as on autopilot; the issue itself, with no sub-issues, no plan and nothing open to wait for, starts its planner with one line `Autopilot: switched on, starting plan` where the owner would have said `/plan`; every issue under it, at every level, with no sub-issues, no plan and nothing open to wait for starts its planner; and every pull request in the tree its code review approved merges as in step 6. When the issue's last run ended with no record (its live card still up, its run over), `/autopilot start` starts that run's stage again instead. A split filed by `/work` on autopilot puts its stories on autopilot and starts the ones with nothing to wait for.
- `/issue`: file the issues the agents raised (planned).
- No command, nothing starts. Bots never start anything. An Approve never starts anything: it only ever means merge.
- Reviewers never start on the owner's command alone except `/review`; otherwise the river starts them.

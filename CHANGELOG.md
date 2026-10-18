# Changelog

What each version of Dokima does.

## v0.1.0

Dokima's first version.

- Installing adds only one small workflow and a settings file; Dokima's code stays in Dokima's repo.
- One settings file per repo, merged over the shipped defaults.
- Plan, plan review, work and code review, each a separate agent on its own machine, routed by code.
- Commands from code owners only: `/plan`, `/work`, `/review`, `/autopilot start` and `/autopilot stop`.
- The planner writes a test for every acceptance criterion; each criterion gets its own check on GitHub.
- The fence puts back every edit to a test and undoes every change outside the plan's scope.
- A merge gate waits for every required check on the up-to-date head before asking to merge.
- Large asks split into sub-issues with blocked-by links.
- Agents raise questions to the owner, blockers to each other, and issues they find outside their own.
- A card on every issue and its pull request, a record of every agent run, and an optional project board.
- Autopilot across an issue and every sub-issue under it.
- A daily audit compares the repo's settings with what Dokima needs and reports drift on a pinned Setup issue.

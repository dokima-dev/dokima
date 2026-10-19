# Changelog

What each version of Dokima does.

## v0.1.2

Onboarding fixes for repos beyond Dokima's own.

- The install file starts on a push to any branch, so repos whose default branch is not `main` work (#874).
- Keys go in repo secrets, since environment secrets never reach jobs run from this repo; the audit reports a missing key by name (#876).
- The testmon baseline runs only the tests folder the settings name (#877).
- The testmon baseline passes on a repo with no tests yet (#886).
- The all tests check passes on a repo with no tests yet (#887).

## v0.1.1

Fixes merged since v0.1.0.

- Card and branch updates find checks by the names GitHub shows (#852).
- The install docs name the full checks, so an empty repo reaches its first merge (#856).
- The audit spares the repo's own checks and a missing board (#861).
- The card follows the repo's own CI (#866).
- Each release takes its version from the changelog's newest version heading (#867).

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

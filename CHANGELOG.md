# Changelog

What each version of Dokima does.

## v0.1.7

Test baseline on repos with no tests yet, and rejected model keys.

- The test baseline passes, with a notice, on a repo with no tests folder yet, and runs scoped to the settings' tests folder and file pattern (#929, #928).
- A model key the provider refuses ends the run as "Model key rejected", naming the secret to replace, instead of a missing plan; the setup audit tries each set agent key once (#931, #907).

## v0.1.6

Scoped test runs, private-repo logs, declared keys and upstream filing.

- The all tests check and code review's test run collect only the settings' tests folder and file pattern; a repo with no tests folder passes as having no tests yet (#924, #923).
- In a private repo, saving a run's conversation reads the records branch with the app's key, so logs append instead of being lost (#921, #917).
- The test seed no longer leaves background git work or shared scratch folders, ending random "unable to write file" failures (#918, #915).
- Settings may name only the agent keys entry.yml declares; any other name stops the run and gets one audit line (#911, #896).
- δokima's own problems on a repo can be filed to δokima's repo when the settings name an upstream repo, off by default (#872, #745).

## v0.1.5

Private repos, labels and key errors.

- In a private repo, runs read the issue's branch with the app's key; a remote that cannot answer stops the run (#916, #914).
- The setup audit creates every label δokima needs that a repo lacks: autopilot, filed-by-dokima and hotfix (#908, #881).
- Autopilot starts no code review after a worker hands back with no change and no branch (#910, #909).
- Missing-key errors tell adopters to add a repo secret, not the keys environment (#906, #884).
- δokima's own repo is no longer told to add repo secrets it keeps in its keys environment (#905, #885).
- Hotfix pull requests are labeled, hotfix asks needing a design choice go back to planning, and cards are one line (#873, #864).

## v0.1.4

Secrets reach Dokima's inner jobs in repos owned by another account.

- Every shared workflow declares the secrets it reads, and each call hands them over by name (#897).

## v0.1.3

Secrets reach Dokima's jobs in repos owned by another account.

- The entry workflow declares the secrets it takes, and the install file hands each over by name (#894).

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

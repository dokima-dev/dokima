# Configuration

This page lists every setting Dokima needs in your repository, as the code reads it today.

## Secrets and variables

You set these under Settings, Secrets and variables, Actions. The workflows that hold keys read them from the `keys` environment.

| Name | Kind | What it is |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | secret | The token the agents run Claude Code with. |
| `DOKIMA_APP_KEY` | secret | The private key of your Dokima GitHub App. |
| `DOKIMA_APP_ID` | variable | The ID of your Dokima GitHub App. |
| `DOKIMA_BOARD` | variable | The project board, as `org/number`. Leave it unset and the board workflow does nothing. |

## CODEOWNERS

The CODEOWNERS file names your code owners. Only their commands and their plan and work labels count. Outside autopilot, you approve and merge the pull request yourself; the branch rule asks only for the two checks below.

## Branch rule

The branch `main` needs a rule that blocks merging until these checks pass:

- `all tests`: the whole test suite.
- `all done-whens passed`: every criterion's check of the plan.

## App permissions

Your Dokima GitHub App needs these repository and organization permissions:

| Permission | Level |
|---|---|
| `contents` | write |
| `pull_requests` | write |
| `issues` | write |
| `checks` | read |
| `actions` | write |
| `statuses` | read |
| `metadata` | read |
| `workflows` | write |
| `administration` | read |
| `organization_projects` | write |

## Project board

The project board is optional. Without it, everything else works; only the board and Priority are skipped.

The board has three single-select fields:

| Field | Options |
|---|---|
| Status | Backlog, Plan, Work, Review, Done |
| Action | Needs you, Autopilot |
| Priority | Blocker, High, Parked |

You add the Needs you and Autopilot options of the Action field once, by hand. Code never edits a field's options.

The Autopilot view is a table filtered to `label:autopilot is:open`. Code adds it the first time a tree goes on autopilot.

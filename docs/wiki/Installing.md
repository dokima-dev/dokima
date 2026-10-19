# Installing

**Honest status:** δokima runs on its own repo, [dokima-dev/dokima](https://github.com/dokima-dev/dokima). Onboarding other repos (one link, a few minutes, never overwriting your labels or files) is **in progress**: [#272](https://github.com/dokima-dev/dokima/issues/272). Until then, setup is manual and the steps below describe what the code expects.

Nothing to host: it all runs in GitHub Actions. You do need a GitHub App, secrets, one workflow file and one settings file.

## Requirements

- A GitHub repo, ideally in an **organization** (the project board and merge queue need one; on personal repos those extras are skipped).
- A Claude subscription: runs use Claude Code with an OAuth token.
- Python 3.12 and `pytest`. Other languages are **Planned**.

## 1. GitHub App

Create an app from `dokima/app.json` and install it on the repo. Permissions it asks for:

| Permission | Level |
|---|---|
| contents, pull requests, issues, actions, workflows, organization projects | write |
| checks, statuses, metadata, administration, secrets | read |

The app posts every comment, card and PR. It never approves.

## 2. Secrets and variables

Add these as **repo** secrets and variables (Settings, Secrets and variables, Actions). δokima runs from its own repo, so a secret kept only in an environment never reaches its jobs.

| Name | Kind | Holds |
|---|---|---|
| `DOKIMA_APP_ID` | variable | The app's ID |
| `DOKIMA_APP_KEY` | secret | The app's private key |
| `CLAUDE_CODE_OAUTH_TOKEN` | secret | Claude Code token for the agents |
| `DOKIMA_BOARD` | variable, optional | Project board as `org/number` |

`dokima.yml` hands each secret to δokima by name. If your settings name another agent key (`CODEX_API_KEY` or `KIMI_API_KEY`), add its line under `secrets:` in `dokima.yml` too.

Secrets are scrubbed from cards and saved conversations. Agents hold no GitHub key while they work.

## 3. Workflow and settings

`.github/workflows/dokima.yml` and `.dokima/settings.yaml` are the only files you add; nothing else of δokima lands in your repo.

1. Add [`dokima/install/dokima.yml`](https://github.com/dokima-dev/dokima/blob/main/dokima/install/dokima.yml) to your repo as `.github/workflows/dokima.yml`. It runs δokima from its own repo at the newest release, `v0.1.3`.
2. Add [`dokima/install/settings.yaml`](https://github.com/dokima-dev/dokima/blob/main/dokima/install/settings.yaml) to your repo as `.dokima/settings.yaml`, naming only what differs from the defaults.

Your repo's owner gives commands and approves. Optional: a `.github/CODEOWNERS` file with a `*` line names other approvers.

## 4. Branch rule on main

Require these checks: **`dokima / full-suite / all tests`** and **`dokima / acceptance-criteria / Acceptance criteria`**. GitHub shows them under these full names, since they run inside `dokima.yml`. Without a required check the merge gate refuses to pass anything. Enforcing it on private repos needs a paid GitHub plan.

## 5. Board (optional)

A Project with single-select fields:

| Field | Options |
|---|---|
| Status | Backlog, Plan, Work, Review, Done |
| Action | Needs you, Autopilot |
| Priority | Blocker |

## 6. Labels

`autopilot` is created on first use. `filed-by-dokima` marks issues δokima files itself. The manifest also declares `plan` and `work` labels, so the audit expects them, but they start nothing: commands do.

## Checking your setup

`python3 -m dokima.manifest` lists every label, field, check and permission the code relies on. The **audit** workflow reports drift on a pinned **Setup** issue, including a key missing from the repo secrets. The app reads secret names only, never their values.

## Cost

Actions minutes come from your GitHub plan. Model use comes from your Claude subscription; each record shows its API-equivalent cost.

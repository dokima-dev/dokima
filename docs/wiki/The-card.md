# The card

The card is what you read instead of the code. Code draws it, never an AI, from the agents' records and GitHub's own check results. The same card sits at the top of the issue and of its PR.

It runs from `main` (`dokima/card.py`), so the work being judged can't change how it is reported. It is redrawn on every change to the issue or PR, and every 15 minutes.

## Example

A real card, drawn by `card.py`'s gallery: the PR passed its checks and code review, and waits for you.

> Slow calls hand back a job id instead of timing out.
>
> **Review** · 🟡 Needs you: Ready for approval
>
> latest run · #5 · files changed
>
> **User story:** Callers get a job id for a slow call and fetch its result later.
>
> **Acceptance criteria**
> - ✅ **Acceptance criterion:** A slow call returns a job id within 20 s.
> - ✅ **Acceptance criterion:** The job id fetches the result once it is ready.
>
> ▸ Non-functional requirements
>
> **Scope:** `app/jobs.py`
>
> ▸ Original issue
>
> **Definition of Done:** ✅ All tests · ✅ Code review · ⚪ Owner approval

*(Emoji stand in for the card's GitHub icons.)*

## Sections, top to bottom

| Section | What it shows |
|---|---|
| **Summary** | One plain sentence from the plan. |
| **Status line** | The stage (Backlog, Plan, Work, Review, Merged), then **Needs you** and your to-do when the loop waits on you. |
| **Links row** | Latest run · the PR · files changed. On the PR's card, the issue too. |
| **Stories** | On a split: each sub-issue with its stage. |
| **Blocked by / Blocks / Relates to** | GitHub's own blocked-by links, read live. A loop of issues blocking each other is named. |
| **User story** | One sentence: what changes for you. |
| **Acceptance criteria** | Each with its verdict icon. The label links to its GitHub check. Under it: **Verified by** (the test's first docstring line, linked to the test), **Edge cases**, **Source** (where you asked for it). |
| **Non-functional requirements** | Folded. Same layout. |
| **Scope** | Files the worker may change. |
| **Original issue** | Your text, folded, exactly as written. Before a plan exists it shows open. |
| **Definition of Done** | Always last: All tests · Code review · Owner approval. |

Each verdict comes only from GitHub: a criterion shows passed only when its check passed on the PR's latest commit.

## Verdict icons

| Icon | Meaning |
|---|---|
| passed (green) | GitHub recorded the check as successful. Links to the proof. |
| failed (red) | The check failed. Links to the run. |
| running (amber) | In progress. |
| none (grey) | Not started yet. |

## Needs you: the to-dos

| Card says | Do |
|---|---|
| answer N questions … with `/plan`, or say `/review` | Answer the planner, or accept its assumptions |
| answer N blockers … with `/plan` | Answer the planner's blocker |
| answer N questions and N blockers … with `/plan`, `/work` or `/review` | Answer the reviewer |
| Say /work to build the plan | Approve the plan |
| Three blocks in a row: your call | Decide with `/plan`, `/work` or `/review` |
| Settle the escalation | Read the reviewer's reason, then decide |
| Fix the rejected hand-back | Code refused an agent's output; see the record |
| Fix why nothing ran | A command failed to start; see the record |
| Ready for approval | Approve and merge the PR |
| See why not every check passed | Read the failing check |

The to-do links to the comment it's about.

## Run records

Every agent run posts one comment, written by code:

- One sentence on what the run did.
- Only what it changed, decided or raised (questions, blockers, issues found, files changed, dropped paths).
- A **Stats** fold: model, time, turns, tokens, API-equivalent cost, links to the full conversation and the run.
- The **Full record** JSON, last. Later runs are built from these records.
- **Next:** what happens now, mentioning you when it's your turn.

These comments are the audit trail. Only comments the bot posted count as records.

## The board

With a GitHub Project board set up, each card also sits in a column: **Backlog, Plan, Work, Review, Done**. A **Needs you** or **Autopilot** pill sits on top, never both. **Priority: Blocker** is set by code on any open issue blocking another. Optional; without a board nothing fails.

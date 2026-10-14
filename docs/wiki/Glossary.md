# Glossary

| Term | Meaning |
|---|---|
| **Autopilot** | An issue tree carrying the `autopilot` label: approved plans build, approved splits file, passed gates merge, without your command. See [[Autopilot]]. |
| **Blocker** | (1) A raise that must be fixed before work goes on, sent to whoever fixes it. (2) The board's **Priority: Blocker**, set by code on an open issue that blocks another open issue. |
| **Board** | An optional GitHub Project. Columns Backlog, Plan, Work, Review, Done; pills Needs you and Autopilot. Kept by code. |
| **Card** | The status block code draws at the top of the issue and its PR: summary, stage, criteria with GitHub's verdicts, Definition of Done. See [[The card|The-card]]. |
| **Code owner** | A user named on the `*` line of `.github/CODEOWNERS`. Only their commands count. |
| **Criterion** | One acceptance criterion: one observable behavior, ≤20 words, quoting your words with a source link, proven by one test. Numbered `N.k` (issue N). |
| **Definition of Done** | The card's last line: All tests · Code review · Owner approval. |
| **Feature** | A plan too big for one PR (4–15 criteria), split into 2–5 stories. |
| **Fence** | The step after the worker stops: restores every test file and undoes changes outside scope before anything is pushed. |
| **Merge gate** | After code review approves: update the branch with main, mark the PR ready, wait for every required check. |
| **Needs you** | The loop is waiting on you. Shown on the card (amber icon) and the board. |
| **Raise** | What an agent hands up: a question, a blocker or an issue. Answered by ID. |
| **Record** | The bot's comment for one agent run: what it did, raised, Stats, full JSON. The audit trail. |
| **Round** | One pass of a stage. Three blocking reviews in a row at one stage stop for you. |
| **Scope** | The files the plan lets the worker change. |
| **Story** | A plan of 1–3 criteria, built as one PR. A split's stories are sub-issues and never split again. |

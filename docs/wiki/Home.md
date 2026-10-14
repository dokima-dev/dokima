# δokima

**Coding agents now out-code us on narrow tasks. The bottleneck is knowing their work is actually done.**

δokima turns a GitHub issue into merged code, takes grading away from the agent that did the work, and moves your effort from writing code to verifying it.

*δ is the first letter of δοκιμασία, Greek for "test" or "trial".*

## What it is

- **Verification is the product.** Every promise in a plan gets its own test, and GitHub's verdict on that test is the proof. No model's word counts.
- **Your words are the contract.** Each acceptance criterion quotes what you wrote, with a link to where you wrote it. Code checks the quote is really there.
- **You own what "done" means.** You approve the plan before any code is written and the result before it merges.
- **Not fully autonomous.** Every decision traces back to a human approval: a command you gave, or your own words quoted on autopilot.
- **GitHub-native, nothing to host.** Issues, pull requests, comments, checks and Actions are the whole system. No server, no database.
- **A full audit trail.** Every agent run posts one comment with what it did, why, and links to its full conversation and run.

## The loop in one line

You open an issue → the planner writes criteria and tests → a reviewer grades the plan → you say `/work` → the worker builds → the reviewer grades the code → the merge gate runs every check → you approve and merge.

Details: [[How it works|How-it-works]].

## Start here

| If you want to… | Read |
|---|---|
| Understand the flow | [[How it works|How-it-works]] |
| File your first task | [[Writing issues|Writing-issues]] |
| Know what to type | [[Commands]] |
| Read what δokima shows you | [[The card|The-card]] |
| Let a whole tree run by itself | [[Autopilot]] |
| Set it up | [[Installing]] |
| Look up a word | [[Glossary]] |

## Status

In active development. δokima builds itself: every feature since the first slice went through its own loop. It runs on [dokima-dev/dokima](https://github.com/dokima-dev/dokima) today; onboarding other repos is in progress ([#272](https://github.com/dokima-dev/dokima/issues/272)). Anything not built yet is marked **Planned**.

License: Apache-2.0.

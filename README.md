# δokima

**Coding agents now out-code us on narrow tasks. The bottleneck is knowing their work is actually done.**

δokima moves your effort from writing code to verifying it: you assign, agents build, and nothing merges until it's proven. That clears the bottleneck, so you can hand off more work and run a fleet of agents with confidence.

## A management structure for agents

Remote engineering teams work because of structure: tickets, plans, reviews, and a rule that nothing ships unchecked. δokima gives agents that same structure. It is the organization around your agents that makes sure they deliver the work they were asked for, proven.

## One history, any agent, any device

Today the story of a codebase is scattered across chat sessions, coding agents and devices, with no single place to see it. δokima writes everything into native Git and GitHub: issues, plans, tests, failed attempts and lessons learned. Whatever agent or device you use next, it builds on the full history, permanently, with zero setup.

## Project management for agents

**δokima is Jira for agent teams.** You define the work, define what "done" means, and assign it. Agents plan, build and test it, and you get it back verified, every time. Run many at once and follow everything on one GitHub project board, all with GitHub's own tools.

## Unattended until it's actually done

Coding agents tend to stop before the work is finished, and leaving them running on your own machine is risky. δokima runs each step on a fresh, isolated machine with no access to your system or keys, and the work isn't done until its checks pass. Every plan, attempt and result is written back to the issue, so the next run picks up exactly where the last one stopped.

δokima is an agent runtime that uses GitHub Actions as its orchestrator. You describe a task in a GitHub issue; isolated AI sessions plan it, build it and review it; and nothing reaches your main branch until it is proven.

No servers to run. No database. Your repo, its issues and its pull requests are the whole system.

> Status: in active development. The first slice is being built now; see [Roadmap](#roadmap). Full documentation: the [δokima wiki](https://github.com/δokima-dev/δokima/wiki).

## You check the verification, not the work

Coding agents like Claude Code are strong, but someone still has to watch every step. δokima moves you from checking the work to checking the verification. You approve the plan, you accept the result, and the runtime guarantees everything in between.

## How it works

```
issue ──► Planner ──► you approve ──► Worker ──► Reviewer ──► Gate ──► main
            plan +                      code       read-only     tests
            tests                                  judgment      pass
```

1. **You open an issue** in plain words: what you want and what "done" looks like.
2. **The planner** turns it into a plan and the tests that will prove it, then waits for your go.
3. **The worker** writes the code to make those tests pass. It cannot change them.
4. **The reviewer**, a fresh session that never talked to the worker, checks the change against the plan.
5. **The gate** merges only when the full test suite passes on the latest main.

Each role is its own GitHub Actions job on its own clean machine. Labels on the issue say whose turn it is.

## Production-grade by design

- **Separation of duties.** Planner, worker and reviewer run as separate sessions on separate machines. None can see, steer or vouch for another.
- **Tamper-proof grading.** The tests are the contract. They are written before the work and locked during it; a change that edits them fails, even if everything passes.
- **Independent review.** A read-only reviewer blocks gamed tests and damage outside the task's scope.
- **A merge gate.** Main never breaks. Nothing lands until it is green against the latest main, and merges happen on their own.
- **Durable execution.** The worker commits after every step. A crash, timeout or cancelled job resumes from the last commit instead of starting over, and stalled tasks restart themselves.
- **Fast verification.** Large test suites split across many machines at once, so checking never becomes the bottleneck.
- **Full audit trail.** Every plan, step, review and decision is a commit, comment or log on GitHub. Nothing happens off the record.
- **Least privilege.** Each role gets only the permissions its job needs. Secrets live in GitHub's encrypted store, never in the repo.

## Plug in any repo

One command connects a repository: it adds a small workflow file, a starter `AGENTS.md` for the repo's own rules, the labels, and the branch protection that makes the gate binding. Your code and data stay in your repo; δokima only holds the pipeline.

The same flow works beyond code. A job application or a research brief is a task too: the reviewer checks facts and fit, and anything that leaves your hands, like sending or submitting, waits for your yes.

## Roadmap

δokima is built through itself: a minimal pipeline is assembled by hand, then every capability below arrives as an issue run through that pipeline.

- [ ] **Slice 1:** issue in, tested pull request out, merged only when green
- [ ] **Plan:** you approve intent and tests before any work starts
- [ ] **Review:** independent, read-only reviewer
- [ ] **Locked tests:** the worker cannot touch what it is graded on
- [ ] **Gate:** automatic, ordered merges against the latest main
- [ ] **Resume:** crashes and stalls never lose work
- [ ] **Fast tests:** suites split across many machines
- [ ] **Any repo, any task:** one-command onboarding

## Requirements

- A GitHub account. Public repos work on the free plan; enforcing the gate on private repos needs GitHub Pro.
- A Claude subscription or API key.

---

Built by Reza Soleymanifar.

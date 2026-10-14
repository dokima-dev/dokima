<p align="center">
  <img src="logo.svg" width="96" alt="δokima logo">
</p>

<h1 align="center">δokima</h1>

<p align="center">
  <b>Your words are the contract. Agents do the work. Nothing merges until it's proven.</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-black" alt="Apache 2.0"></a>
  <img src="https://img.shields.io/badge/status-early%20access-F4EBD0?labelColor=111" alt="early access">
  <img src="https://img.shields.io/badge/runs%20on-GitHub%20Actions-black" alt="runs on GitHub Actions">
</p>

---

Coding agents now out-code most of us on narrow tasks. What they still can't do is prove their own work is done. δokima is an agent runtime that fixes that: you say what you want and what "done" means, agents plan, build and review it, and nothing reaches main until it passes the checks you approved.

**Verification is the product. You own what done means.**

## How it works

```
issue → plan → you approve → work → review → merged
```

1. **Open an issue** in plain words.
2. **The planner** splits it into small stories and writes the tests that will prove each one.
3. **You approve** the plan and its tests. This is your one real job.
4. **The worker** writes code until those tests pass. It cannot edit them.
5. **A fresh reviewer**, who never spoke to the worker, checks the change against your plan.
6. **It merges** only when everything is green on the latest main.

Every step shows up as one card at the top of the issue, readable on your phone.

## Why δokima

- **You stay accountable**: Every merge traces back to something you approved. Not autonomous by design.
- **Tests you can't fake**: Written before the work and locked during it.
- **Separate roles**: Planner, worker and reviewer run on separate, isolated machines. None can vouch for another.
- **All on GitHub**: Issues, plans, attempts and decisions live in your repo. No servers, no database.
- **Any agent**: The runtime is agent-agnostic; swap models without changing your workflow.
- **Resumes on its own**: Crashes and timeouts pick up from the last commit.
- **Costs in plain sight**: Every card shows the time, tokens and cost of that run.

## Get started

```sh
pip install dokima
dokima connect owner/repo
```

`connect` adds one workflow file, a starter `AGENTS.md`, the labels, and the branch protection that makes the gate binding. Then open an issue.

**You need:** a GitHub repo and a Claude subscription or API key. Enforcing the gate on private repos needs GitHub Pro.

## Learn more

- [Writing issues](https://github.com/dokima-dev/dokima/wiki/Writing-issues): how to say what done means
- [The card](https://github.com/dokima-dev/dokima/wiki/The-card): reading an issue at a glance
- [FAQ](https://github.com/dokima-dev/dokima/wiki/FAQ)

## Status

Early access. δokima is built by δokima: every feature after the first slice landed as an issue through its own pipeline.

---

<p align="center">Apache 2.0 · built by <a href="https://github.com/soleymanifar">Reza Soleymanifar</a></p>

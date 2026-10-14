# FAQ

### Is it fully autonomous?
No. Every decision traces to a human approval: your `/work` on the plan, your merge of the result, or, on [[Autopilot]], your `/autopilot start` plus your own words quoted for any question it settles.

### What stops an agent from cheating?
- The planner writes the tests before any code exists; each must fail today.
- The [fence](How-it-works#the-fence) restores every test file and undoes changes outside scope before anything is pushed.
- A separate reviewer, who never talks to the worker, blocks gamed tests and hard-coded answers, and reads the worker's session log.
- Each criterion's check runs from `main`'s copy of the workflow; the PR can't rewrite its judge.
- Merging needs GitHub's required checks to pass. That's GitHub's rule, not the agent's.

### Why GitHub Actions instead of a server?
GitHub already has clean machines, storage (issues, comments), permissions, secrets, logs and merge rules. δokima adds only the rules on top. Nothing to host or keep in sync.

### Where is the state?
On GitHub. Each run's record is a bot comment with its full JSON. Every run rebuilds its starting point from the issue's whole history, so any stage can be re-entered at any time. Full agent conversations are saved, secrets removed, on the repo's `logs` branch.

### What if a run crashes?
A run that dies before posting its record gets a failed record anyway, mentions you and shows **Needs you**. Give the command again; `/autopilot start` restarts it too. Resuming mid-run from a commit is **not built**.

### Why does every change go through a pull request?
A PR is where tests run, reviews happen and history is kept. Agents are treated like outside contributors: trusted to propose, never to merge on their own word.

### Can I edit my issue after filing?
Don't edit the text; comment instead. Your original text stays frozen below the card, and agents read every comment. Use `/plan <words>` to have the planner pick it up.

### What does Approve mean?
Only "merge this". It never starts a stage. Approve plans with `/work`.

### What if agents disagree forever?
Three blocking reviews in a row at one stage stop the loop for you.

### Which languages?
Python with `pytest` today. Per-repo setup and test commands are **Planned**.

### Can I use it on my repo?
Not with one click yet. See [[Installing]] and [#272](https://github.com/dokima-dev/dokima/issues/272).

### Which model runs?
Claude, via Claude Code. Each record's Stats fold names the model, and a run fails if any other model was used.

### Where do these docs come from?
`docs/wiki/` in the repo, synced to this wiki on every merge to main.

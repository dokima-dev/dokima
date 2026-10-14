## Principles

- **Nothing merges until it's proven.** Every promise in a plan has its own check, and GitHub's verdict on that check is the proof. No model's say-so counts.
- **Code owns the structure; models fill in content.** Everything that must be exact (freezing plans, posting stage comments, building starting packs, drawing cards, setting labels and board fields) is done by code. Models write only the plan, the code and their findings.
- **Use what GitHub already has.** Comments, reviews, checks, branch protection, CODEOWNERS, project boards, merge queue. Build only the thin glue GitHub lacks.
- **Humans are free; bots are compliant.** People can do anything, on the record. Agents work inside fixed rules: they can't approve, can't change the workflows that judge them, and can't widen their own scope.
- **Everything lives on GitHub.** One permanent history per issue, across every agent and device: plans, attempts, failures, reviews.
- **Fail closed.** Missing proof, a missing reviewer or a broken check blocks; nothing is waved through, and a failure always says why on the issue.
- **Agent-neutral and language-neutral.** No hard-coded people, vendors or languages. Approvers come from CODEOWNERS; each agent plugs in through a small adapter; instructions (including how many sub-agents to use) live in prompts, not code.
- **Match the output to the human brain bottleneck.** The owner's attention is the scarcest thing in the river: whatever the JSON holds, a card shows only what the owner needs at a glance, and the rest goes in folds.
- **Small and lean.** One issue, one PR. Fold related things together. Extras (the board, merge queue) are optional and never required.

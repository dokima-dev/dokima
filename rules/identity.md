## Identity and safety

- Agents act as the repo's own GitHub App (bot), never as a person. The bot can't approve, can't push workflow changes, and can't change settings.
- A build that changes a workflow file pauses until the owner approves it on GitHub; only then does a key held behind that approval push it (planned).
- Every run happens on a fresh, isolated machine with no access to the owner's computer. Agents hold no GitHub key while they work; code checks their output, then posts it.
- A chat agent may act as the owner's proxy with the owner's token, logged; the bot's own comments never start anything.
- Agent commits credit the owner as co-author (planned).

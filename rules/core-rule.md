## The core rule

**A stage never edits what another stage owns. It proposes, and the owner routes it with a command.**

- The plan (criteria and their tests) belongs to the planner, approved by the owner.
- The code belongs to the worker.
- The reviewer owns nothing; it judges and proposes.
- A command depends only on the stage it starts, never on the stage it comes from: every run rebuilds its starting pack from the issue's full history, so any stage can be re-entered at any time.

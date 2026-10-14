## Roles

- **Owner:** decides. Approves plans and results, routes proposals. Only a code owner's commands count.
- **Planner:** turns a rough issue into a plan: an objective, acceptance criteria, scope, and a test for every criterion written before any code. It judges the ask first and raises a doubt only with evidence, as a question for the owner. It may change or delete an older test when the plan makes it wrong, with a reason the owner sees. It proposes splits; it never writes code.
- **Worker:** builds what the approved plan says, on a fresh machine, within scope, until its tests pass. It never changes the plan's tests.
- **Reviewer:** checks the plan, then the result (a real PR review). It blocks only on a promise with no proof or a proof that proves nothing, and raises the issues it finds outside this one.
- **Code:** everything that must be exact (see the principles).

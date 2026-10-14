## Splitting and the graph

- Split when an issue has more than one independent objective, more than five criteria, or work in unrelated parts of the code. Don't split parts that can't land separately.
- 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
- The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
- When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
- When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.

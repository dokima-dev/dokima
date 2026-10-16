## Splitting and the graph

- Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
- 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
- The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
- When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
- When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.

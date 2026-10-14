## Raising and answering

The planner, the worker and the reviewer raise and answer only through two fields of their hand-back, raises and answers. Each agent starts with the open raises sent to it, each with its ID, and code rejects a hand-back that leaves one unanswered. Code stamps who raised each one and its ID; agents never write either.

What code detects and raises itself, never an agent:

- **Work outside the plan**: a change outside the plan's scope is undone before the judges see it, and the owner sees what was dropped. Example: the worker edits `dokima/board.py` on an issue whose scope is `dokima/card.py`.
- **A failing test**: the full suite or a criterion's check goes red on GitHub, and the work goes back to the worker. Example: `tests/test_card.py::test_next_line` fails on the pull request's head commit.
- **Red main**: a required check fails on main itself, not on a pull request. Example: the all tests check fails on main right after a merge.
- **A merge conflict**: GitHub cannot bring a pull request up to date with main, and code says why on it. Example: main changed the same lines of `dokima/card.py`, so the branch cannot be updated.
- **A rejected hand-back**: the checker refuses a hand-back, says why on the issue, and nothing is posted. Example: a worker's `work.json` leaves a raise sent to it unanswered.
- **A workflow file change**: a pull request that changes a workflow file stops for the owner. Example: a build touches `.github/workflows/board.yml`, so it waits for the owner's approval.
- **Three blocks in a row**: three blocks in a row at one stage since the owner last spoke stop the river for the owner; at the code review a failed merge gate counts as a block. Example: the code reviewer blocks the third build in a row, so the owner decides with `/plan`, `/work` or `/review`.

What agents raise by judgment, one of three kinds:

- A **question** is something only the one it is for can decide, and says the reading the agent went on. The planner asks the owner only where the owner's words allow two readings and no principle or earlier decision settles it; it plans on its reading, so the owner may skip answering. A doubt about the ask (already fixed, patching a symptom, overlapping an open issue) is a question for the owner that carries its evidence.
- A **blocker** is something that must be fixed before the work goes on, sent to whoever fixes it: the planner for a weak test, a test that cannot pass as written, a wrong plan or an ask with no criterion; the worker for the code. The worker never asks the owner: the plan is the contract, and disagreements reach the owner by escalation.
- An **issue** is a real problem outside this issue, worth its own issue; it is for no one.

Who may send a question or a blocker to whom is code's table (`dokima/raises.py`), row for row:

| Raised by | To |
|---|---|
| planner | owner |
| worker | planner (through the reviewer, who answers it first) |
| reviewer | planner, worker or owner |

Two tiers of autonomy:

- **Always on:** the reviewer settles anything addressed to an agent before it goes on, and confirms the issues the planner or the worker raised before they are filed.
- **On autopilot only:** the plan reviewer answers a planner's question for the owner only with the owner's own words as evidence, quoted with where they said them, which code checks are really there; anything else waits for the owner (see the flow).

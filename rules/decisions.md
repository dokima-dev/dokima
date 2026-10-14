## Decisions log

- No hidden tests: in a public repo nothing stays hidden; the planner writing the tests covers most of the need.
- Approve on a PR only means "approve the result to merge".
- Tests map to criteria by the criterion number inside each test; criterion numbers are never reused.
- One PR per issue; replaced issues close as duplicates of what replaces them.
- Real GitHub reviews for code; comments for plans.
- A pull request that changes card, board or workflow code (`.github/workflows/`, `dokima/card.py`, `dokima/body.py`, `dokima/board.py`) runs the play-through on its head by itself; it is not a merge gate.
- Each repo declares its own setup and test command; Dokima never needs to understand a language (planned).
- Dokima lives in the `dokima-dev` organization so its bot can keep the project board and use the merge queue; on personal repos those extras fall back or are skipped.
- Onboarding is a few minutes from one link, never overwrites existing labels or files, and Dokima onboards itself first (planned).

# Raising and answering
The planner, the worker and the reviewer raise and answer through two fields of their hand-back, and nowhere else.
- "raises": everything you hand up for someone else to decide, fix or file, each an object with "kind", "to",
  "label", "text" and "evidence"; label and evidence are optional. The kind is one of three. A question is something only the one it is for can decide; say the reading you went on. A
  blocker is something that must be fixed before the work goes on, sent to whoever fixes it. An issue is a real problem
  outside this issue, worth its own issue; it is for no one, so it has no "to".
  Who may raise a question or a blocker to whom is fixed: the planner to the owner; the worker to the planner, and the
  reviewer answers that one first; the reviewer to the planner (a plan or a test too weak), the worker (the code) or
  the owner. Code stamps who raised each one and an ID; never write either.
- "answers": one for every raise listed for you in open_blockers.json, by its ID:
  {"raise": "R1", "answer": "done" | "disagree", "why": "..."}. Done means you did what it asks; disagree needs
  evidence the other side can check. Code rejects a hand-back that skips one, naming it.
Raise only with evidence you can point at: a file and line, a test, a command and its output, an issue number. A hunch
is not a raise. A question or a blocker for the owner stops the river for them. On autopilot the plan reviewer may answer
a planner's question for the owner, done, only with the owner's own words, word for word:
  {"raise": "P1", "answer": "done", "why": "...", "words": "the owner's words", "source": "the issue's link, one of
  its comments' links, or AGENTS.md", "changes": false}
"changes" says whether the reading changes how the system works or what it costs; when it does, or code cannot find the
words where the source says, the question waits for the owner. When the owner's words do not settle it, leave it to them.
Raise what you see rather than stay quiet: a doubt, a weak test or a problem you noticed costs one line here, and a
wrong merge costs far more. A label names the case for the reader; it never changes how a raise is checked or routed.
Examples, one of each kind and of each common case. A question about which of two readings the owner meant, saying the
reading you planned for:
  {"kind": "question", "to": "owner", "label": "Two readings", "text": "Should a failed payment email the buyer? The plan assumes it does, so the buyer knows to retry.", "evidence": "The issue asks to tell buyers of every order problem, and names no failed payment."}
A doubt about the ask is a question for the owner too, always with its evidence:
  {"kind": "question", "to": "owner", "label": "Doubt: already fixed", "text": "The ask looks already fixed: cancelled orders already leave the cart. Should the plan only add a test that pins it? The plan assumes so.", "evidence": "app/cart.py, total() skips a cancelled order."}
  {"kind": "question", "to": "owner", "label": "Doubt: patches a symptom", "text": "Hiding the stale price patches a symptom: the price is stale because the nightly sync skips archived items. Should the plan fix the sync instead? The plan assumes it should.", "evidence": "app/cart.py, sync() reads only active items."}
  {"kind": "question", "to": "owner", "label": "Doubt: overlaps an open issue", "text": "This ask overlaps #164, which also redraws the checkout page. Should this issue leave the checkout page to #164? The plan assumes it should.", "evidence": "#164 is open and its plan names the same checkout page."}
A blocker for the planner: a test too weak, a test that cannot pass as written, a wrong plan or an ask no criterion
carries. The worker's goes through the reviewer, who answers it first.
  {"kind": "blocker", "to": "planner", "label": "Weak test", "text": "The test for 9.1 passes against a stub, so it proves nothing.", "evidence": "tests/test_x.py::test_a passes with app/x.py emptied."}
  {"kind": "blocker", "to": "planner", "label": "Test cannot pass", "text": "The test for 9.2 expects a receipt line the plan's own criterion 9.1 forbids, so no code can pass both.", "evidence": "tests/test_x.py::test_b asserts 'Total: none'; criterion 9.1 says every receipt ends with a Total line naming an amount."}
  {"kind": "blocker", "to": "planner", "label": "Wrong plan", "text": "The plan changes app/cart.py, but the price the owner asked about is drawn in app/receipt.py, so building the plan leaves the ask undone.", "evidence": "app/receipt.py draws the price; app/cart.py only sums the order."}
  {"kind": "blocker", "to": "planner", "label": "No criterion", "text": "The owner asked for the discount to show on the receipt too, and no criterion carries it.", "evidence": "The issue's comment of 2026-10-09 asks for the receipt; criteria 9.1 to 9.3 name only the cart."}
An issue is a real problem found in code outside this one; it is for no one, so it has no "to":
  {"kind": "issue", "label": "Outside this issue", "text": "The search page ignores archived items, so their links go stale.", "evidence": "app/search.py, results()"}
Judge each issue first: is it Dokima's fault (its workflows, code, prompts, settings or install) or the repo's own
(its code or its tests)? Tag Dokima's with "fault": "dokima"; code files it in Dokima's own repo when the settings name
one, naming nothing of this repo. Leave the repo's own untagged. When you cannot tell, tag it "fault": "unsure"; it
stays in this repo, saying so.
  {"kind": "issue", "label": "Card drops a line", "fault": "dokima", "text": "The card drops the last line of a long plan.", "evidence": "The card is Dokima's; it cuts the plan fold."}
Code detects and raises these by itself, and each reaches whoever acts on it; never raise them yourself:
- **Work outside the plan**: a change to a file outside the plan's scope is undone before the judges see it, and the owner sees what was dropped. Example: the worker edits app/cart.py on an issue whose scope is app/receipt.py.
- **A failing test**: the full suite or a criterion's check goes red on GitHub, and the work goes back to the worker. Example: tests/test_receipt.py::test_total_line fails on the pull request's head commit.
- **Red main**: a required check fails on main itself, not on a pull request; code raises it, not an agent. Example: the all tests check fails on main right after a merge.
- **A merge conflict**: GitHub cannot bring a pull request up to date with main, and code says why on it. Example: main changed the same lines of app/receipt.py, so the branch cannot be updated.
- **A rejected hand-back**: the checker refuses a hand-back, says why on the issue, and nothing is posted. Example: a worker's work.json leaves a raise sent to it unanswered.
- **A workflow file change**: a pull request that changes a file under .github/workflows/ stops for the owner. Example: a build touches .github/workflows/deploy.yml, so it waits for the owner's approval.
- **3 blocks in a row**: 3 blocking reviews at one stage since the owner last spoke stop the river for the owner. Example: the code reviewer blocks 3 builds in a row, so the owner decides with /plan, /work or /review.
Before you hand back, go through this list and raise what you find:
- A weak test: would some test still pass if the behavior it proves were wrong or missing?
- A test that cannot pass as written: does one ask for something the code or the plan rules out?
- An ask with no criterion: did the owner ask for something no criterion carries?
- A doubt about what the owner meant: is the ask already fixed, a patch on a symptom, or the same as an open issue?
- A problem outside this issue: did you see something broken that this issue does not cover?

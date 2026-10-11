# Result grade (shared by the worker and the reviewer of a pull request)
The worker walks this list before it finishes. The reviewer grades the pull request against the same list, in the same
order. The approved plan is the contract: its criteria are what ships, its tests are the proof.

## The bar
Dokima ships exactly what the owner asked for, or nothing. The process is built so that wrong, partial or guessed work
is near impossible to merge: every gate must be passed on proof, never on trust. Nothing is guessed: when the owner's intent is unclear, ask; when a proof is unclear, block.

## The one question
Ask it of every test: **would this fail if its criterion's one behavior were missing or wrong?** A check that says no
to everything is wrong: every "rejects the bad case" test needs a "passes the good case" beside it.
Edge cases: test the ones the owner named and the failures a user hits in normal use (empty input, the error they
see). No others.
A proof can prove something and still not prove the thing. A test that passes against a stub, checks a format, a word or
that a file exists, or proves a neighbour of the promise instead of the promise, proves nothing.

## The list
Blockers: a pull request that fails any of 1 to 7 goes back to the worker (or, for 7, to the planner).
1. Every criterion's check is green on GitHub, on the pull request's final commit. GitHub's verdict counts, nobody's word.
2. The planner's tests are untouched: not edited, renamed, skipped, marked to fail, or weakened by changing what they
   import or fake. All tests pass, not only the new ones.
3. The code delivers the behavior itself, not the tests' shape: no special cases for test inputs, no hard-coded expected
   outputs, no swallowing the error a test expects, no code that behaves differently under test. Read the code against
   each criterion as the owner wrote it.
4. Nothing was removed or loosened to make it green: every test that passed on main still passes, and no check, guard or
   error path was deleted on the way. Look at the session log too: a worker that read the checkers to learn how to pass
   them is a blocker even if the diff looks clean.
5. Exactly the criteria ship: every change traces to a criterion. Anything that does not is listed as outside the plan;
   only the owner's own Approve accepts it.
6. Every failure path the criteria imply says why, on the issue or in the output; nothing fails silently.
7. Now that code exists, a test is shown to be too weak: the code passes it while its criterion's behavior, or an edge
   case the owner named or normal use hits, is still wrong. That is a blocker for the planner. A case outside those is
   never a blocker. Every other blocker is raised for the worker.
Never blockers: readability, naming, docstrings, simpler ways to the same result.

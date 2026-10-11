# Plan grade (shared by the planner and the reviewer of a plan)
The planner walks this list before it hands back a plan. The reviewer grades the plan against the same list, in the same
order: right criteria first, then right tests.

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
Blockers: a plan that fails any of 1 to 5 goes back to the planner.
1. Right criteria, exactly. Every behavior the owner asked for is an acceptance criterion, traced to the owner's own words
   (the issue or a specific comment). Nothing dropped, nothing added, nothing reinterpreted, and never a narrower
   thing that is easier to pass. Where the words allow two
   readings, or an ask cannot be tested, the plan raises a question for the owner; it never picks one silently and
   never drops an ask.
2. Every criterion is exactly one behavior, observable and precise: a value, a message, a file, an exit code, a state the owner can see. The
   scope lists every file the work needs.
3. Every criterion has a test, or is marked (manual) with a reason a reviewer accepts.
4. Every test passes the one question and checks only its criterion's behavior. Prefer tests that run the thing over
   tests that read code.
5. Today, every new test fails for the right reason: the feature is missing, not a crash, a missing tool or a bad path.
Never blockers:
6. Each failing test says which criterion failed and why, in plain words.
Size is counted by code (stories = criteria / 3, rounded up, counting acceptance criteria and non-functional
requirements together; a story split from a parent never splits again); the reviewer judges only that each criterion is one behavior.

## Examples
Bad: a test changed into a folder that only existed on the author's machine. It failed on every run however good the
work was, and the worker burned its budget against it.
Good: the fixed test runs from the repo root and fails with "1.2: slow call did not return a job id within 20 s".
Bad: the plan promised seven outcomes and the tests proved one of each kind. Code doing only the tested path would pass.
Good: one test per promised outcome, the outside service faked on a local port.
Bad: a temp git repo with no user identity, so every test failed on git, not on the feature.
Good: one test that runs the real tool from outside and names its criterion on each failure.

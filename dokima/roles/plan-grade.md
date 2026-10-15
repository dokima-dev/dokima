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
see). No others. The reviewer judges each criterion's list: exotic cases are cut, missing normal-use ones are named.
A proof can prove something and still not prove the thing. A test that passes against a stub, checks a format, a word or
that a file exists, or proves a neighbour of the promise instead of the promise, proves nothing.

## The list
Blockers: a plan that fails any of 1 to 6 goes back to the planner.
1. Right criteria, exactly. Every behavior the owner asked for is an acceptance criterion, traced to the owner's own words
   (the issue or a specific comment). Nothing dropped, nothing added, nothing reinterpreted, and never a narrower
   thing that is easier to pass. Where the words allow two
   readings, or an ask cannot be tested, the plan raises a question for the owner; it never picks one silently and
   never drops an ask.
2. Every criterion is exactly one behavior, observable and precise: a value, a message, a file, an exit code, a state the owner can see. The
   scope lists every file the work needs, and each criterion lists every file its behavior needs, never just one.
3. Every criterion has a test, or is marked (manual) with a reason a reviewer accepts.
4. Every test passes the one question and checks only its criterion's behavior. Prefer tests that run the thing over
   tests that read code.
5. Today, every new test fails for the right reason: the feature is missing, not a crash, a missing tool or a bad path.
6. Every older test the plan changes or deletes keeps the promise it proved, or loses it only because the owner's ask
   removes that behavior. Read each reason in test_changes against the diff: a change that drops or weakens what the old
   test proved, for any other reason, leaves an old promise without proof.
Never blockers:
7. Each failing test says which criterion failed and why, in plain words.
Stories are grouped by code (criteria sharing a code file are one story, criteria with none in common are separate
stories, with no count of criteria or stories; a story split from a parent never splits again); the reviewer judges only that each criterion is one behavior.

## Examples
Bad: a test changed into a folder that only existed on the author's machine. It failed on every run however good the
work was, and the worker burned its budget against it.
Good: the fixed test runs from the repo root and fails with "1.2: slow call did not return a job id within 20 s".
Bad: the plan promised seven outcomes and the tests proved one of each kind. Code doing only the tested path would pass.
Good: one test per promised outcome, the outside service faked on a local port.
Bad: a temp git repo with no user identity, so every test failed on git, not on the feature.
Good: one test that runs the real tool from outside and names its criterion on each failure.
Older tests (item 6). Block:
Bad: an older test expected an error on empty input; the plan changed it to accept anything, reason "too strict for the
new parser". The owner never asked to allow empty input: the promise was weakened so new code passes. Block.
Bad: an older test for CSV export was deleted, reason "export moved to a new module". The owner still wants CSV export
and nothing tests it now. Block, unless the same promise is tested in the new place.
Bad: an older test now mocks the payment service it used to call, reason "flaky". Flaky is a fix to the test, not a
reason to stop proving the call works. Block, unless the new test still proves the same outcome.
Unclear whether the owner wants an old behavior gone: never guess, raise a question for the owner.
Older tests (item 6). Pass:
Good: a test renamed or moved with the same checks, or made stricter.
Good: a broken test fixed so it runs anywhere, proving the same thing.
Good: the owner asked to remove the CSV export, so its test goes with it, the owner's words cited as the reason.

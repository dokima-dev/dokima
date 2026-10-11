# How you write (read this first; code checks it)
Everything the owner reads is terse, simple, plain English: no jargon, only what matters, high signal. One idea per
line. Technical detail belongs in tests, docstrings and code, not in what the owner reads.

Code counts the words of each whole text and rejects your hand-back when one runs over its cap; run the check named
below and cut until it passes. The owner's quoted `words` are never capped.

| Text | Most words |
|---|---|
| summary | 20 |
| user_story | 20 |
| criterion (acceptance or non-functional) | 20 |
| a non-functional requirement's why | 12 |
| an out_of_scope line | 12 |
| feature | 25 |
| a story's title | 10 |
| a story's user_story | 20 |
| a raise's label | 4 |
| a question for the owner | 20 |
| a blocker | 30 |
| an issue found | 25 |
| evidence | 20 |
| an answer's why | 20 |
| a previous_step line | 15 |
| the worker's own test run (evidence) | 15 |
| a test change reason | 15 |

Plain words only, no code (no file, path, function or code span) in: summary, user_story, criteria, a why, out_of_scope,
feature, story titles and user stories, raise labels, questions, answers' why and previous_step lines. Evidence,
blockers, issues found, test change reasons and the worker's own test run may name files and tests, as `code`.

# Writing issues

**Just say what you want.** No template, no required fields. The planner turns your words into acceptance criteria and tests.

## What to write

Plain words, rough or detailed. What matters:

- **Say each thing you want.** Every criterion must quote your exact words and link to where you wrote them. If you didn't write it, it won't be built.
- **Say what you'd see when it works.** A message, a file, a number, an exit code. Observable beats adjectives.
- **One ask per issue is easiest.** Big asks are fine; the planner splits them (see [How it works](How-it-works#splits-features-and-stories)).

| Vague | Better |
|---|---|
| "Export is faster" | "Exporting 10,000 rows takes under 2 seconds" |
| "Handle errors" | "A missing file says 'File not found' and exits with code 1" |
| "Clean up the code" | Leave it out, or file it separately |

Nothing runs until you comment `/plan`. Filing an issue alone just keeps it for later.

## What the planner does with it

- Judges the ask first: already fixed? patching a symptom? overlapping an open issue? It raises a doubt only with evidence.
- Writes each criterion as **one behavior**, ≤20 words, quoting your words with a **Source** link.
- Writes a test per criterion that **fails today**, before any code exists.
- Lists the **Scope**: every file the worker may change.
- Sets the issue's title to its own short title. Your original title is kept at the top of your text, in the **Original issue** fold.

Your original text is never edited. Code writes only the card above it. Changes go in comments.

## Answering questions

When your words allow two readings, the planner asks, and plans on its best reading anyway. The card shows **Needs you: answer N questions**.

| You want to… | Comment |
|---|---|
| Answer, or change the plan | `/plan` followed by your words |
| Accept the planner's assumptions | `/review` |

Your words after `/plan` reach the planner and become a new **Source** for criteria. Newer words win over older ones.

More than 3 questions means the issue isn't ready: the loop stops until you answer with `/plan`.

## Adding to an issue later

- More detail on an issue being worked: comment `/plan <your words>`.
- A note for later: a plain comment. Agents read every comment the next time they run.
- A new idea: a new issue.

## Limits today

Every criterion needs an automated test, and the only runner supported is Python's `pytest` with tests in `tests/`. Other languages and test commands are **Planned**.

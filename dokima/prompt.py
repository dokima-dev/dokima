"""An agent's prompt, as the repo's settings say (#796).

`python3 -m dokima.prompt ROLE GRADE`, run in the runtime folder, prints the shipped prompt (dokima/roles/style.md,
GRADE.md, ROLE.md, with the shared raising rules of raising.md in place of each role's marker) with the settings drawn
in: the owner docs file in place of AGENTS.md, the protected paths in the worker's never-edit line, the test settings
in the planner's runner line, the caps setting in the caps table, the questions setting in the planner's question
limit and the blocks setting in the blocks-in-a-row line (#817).
`python3 -m dokima.prompt house ROLE` prints the house rules for ROLE: each prompt addition's file, less the
`## <role>` sections of the other roles. `python3 -m dokima.prompt files` prints the addition files, one a line, so
the workflow copies them from main.
"""
import os
import re
import sys

import yaml

from dokima import settings

ROLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roles")
ROLES = ("planner", "worker", "reviewer")
# Each cap's row in the style prompt's caps table.
LABELS = {"summary": "summary", "user_story": "user_story", "criterion": "criterion (acceptance or non-functional)",
          "nfr_why": "a non-functional requirement's why", "feature": "feature", "story_title": "a story's title",
          "story_user_story": "a story's user_story", "raise_label": "a raise's label",
          "question": "a question for the owner", "blocker": "a blocker", "issue": "an issue found",
          "evidence": "evidence", "answer_why": "an answer's why", "previous_step": "a previous_step line",
          "work_evidence": "the worker's own test run (evidence)", "test_change": "a test change reason"}
RUNNER = re.compile(r"^Current runner .*\n.*\n", re.M)
NEVER_EDIT = re.compile(r"^Never edit `\.github/`", re.M)
RAISING = "<!-- raising -->"  # where a role file takes the shared raising rules
QUESTIONS = re.compile(r"\b(more than)(\s+)\d+(\s+questions)\b", re.I)
BLOCKS = re.compile(r"^- \*\*\d+ blocks in a row\*\*.*$", re.M)


def shipped(name):
    """The shipped role file NAME.md."""
    with open(os.path.join(ROLES_DIR, f"{name}.md")) as f:
        return f.read()


def caps_table(text, caps):
    """TEXT with each caps table row showing its cap from CAPS."""
    for key, label in LABELS.items():
        if key in caps:
            text = re.sub(rf"^\| {re.escape(label)} \| \d+ \|$", f"| {label} | {caps[key]} |", text, flags=re.M)
    return text


def runner_line(tests):
    """The planner's runner line, drawn from the test settings."""
    return (f"Current runner: `{tests['run_all']}` runs every test and `{tests['run_one']}` one, tests in "
            f"{tests['dir']}/, and each test names its criterion with\n    {tests['tag']}(\"proves\", \"N.k\")\n")


def build(role, grade, got):
    """The shipped prompt for ROLE with grade GRADE, with the settings GOT drawn in."""
    text = "".join(shipped(n) for n in ("style", grade, role)).replace(RAISING, shipped("raising").rstrip("\n"))
    text = caps_table(text, got["style"]["caps"])
    text = RUNNER.sub(lambda m: runner_line(got["tests"]), text)
    text = QUESTIONS.sub(lambda m: f"{m[1]}{m[2]}{got['planner']['max_questions']}{m[3]}", text)
    text = BLOCKS.sub(lambda m: re.sub(r"\b\d+\b", str(got["river"]["max_blocks"]), m[0]), text)
    paths = ", ".join(f"`{p}`" for p in got["protected_paths"] or [])
    text = NEVER_EDIT.sub(lambda m: f"Never edit {paths}" if paths else "Never edit", text)
    return text.replace("AGENTS.md", str(got["owner_docs"]))


def files(got):
    """The prompt additions' files, as the settings name them."""
    return [str(a["file"]) for a in got["prompts"]["append"] or [] if isinstance(a, dict) and a.get("file")]


def for_role(text, role):
    """House rules TEXT for ROLE, less other roles' `## <role>` sections."""
    parts = re.split(r"^(?=## )", text, flags=re.M)
    keep = [p for p in parts if not (p.startswith("## ") and p[3:].split("\n")[0].strip().lower() in ROLES
                                      and p[3:].split("\n")[0].strip().lower() != role)]
    return "".join(keep).strip()


def house(role, got, root="."):
    """ROLE's house rules from every prompt addition file under ROOT; empty when none."""
    out = []
    for path in files(got):
        full = os.path.join(root, path)
        if os.path.isfile(full):
            with open(full) as f:
                rules = for_role(f.read(), role)
            if rules:
                out.append(rules)
    return "\n\n".join(out)


def main(argv):
    """Prints a prompt, a role's house rules or the addition files; exits 1 saying why."""
    try:
        got = settings.read()
        if argv[:1] == ["files"]:
            print("\n".join(files(got)))
        elif argv[:1] == ["house"] and len(argv) == 2:
            rules = house(argv[1], got)
            if rules:
                print(rules)
        elif len(argv) == 2:
            print(build(argv[0], argv[1], got))
        else:
            print("usage: python3 -m dokima.prompt ROLE GRADE | house ROLE | files", file=sys.stderr)
            return 1
    except settings.Locked as e:
        print(f"::error title=Locked setting::{e}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as e:
        print(f"::error title=Prompt not built::{e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""The hotfix lane (#863): a labeled issue is built from its text, with no plan.

It is still code-reviewed and gated as any pull request. An issue is in the lane while it carries the hotfix label and no planner has run on it.
Its worker and its code reviewer get ask.md, the issue's text as the whole ask, in place of plan.json. Once a code
review sends it back to planning, the planner runs and the issue follows the normal flow from then on.

    python3 -m dokima.hotfix labeled N         # exits 0 when issue N carries the hotfix label, 1 otherwise
    python3 -m dokima.hotfix prompt on|off F   # keeps the prompt's hotfix sections in file F, or drops them
    python3 -m dokima.hotfix label             # prints the hotfix label's name
"""
import json
import os
import re
import subprocess
import sys

from dokima import agent_github, settings
from dokima.body import ask

LABEL = "hotfix"  # the hotfix label's name, unless a repo's labels setting names its own
ASK = "ask.md"
SECTION = re.compile(r"<!-- hotfix -->\n?(.*?)<!-- /hotfix -->\n?", re.S)


def label():
    """The hotfix label's name: the labels setting's hotfix entry, else hotfix."""
    return str((settings.read().get("labels") or {}).get("hotfix") or LABEL)


def labeled(repo, number):
    """True when the issue carries the hotfix label on GitHub.

    False when it does not, or GitHub cannot say."""
    try:
        labels = json.loads(agent_github.gh("api", f"repos/{repo}/issues/{number}")).get("labels")
    except (subprocess.CalledProcessError, json.JSONDecodeError, AttributeError):
        return False
    name = label()
    return isinstance(labels, list) and any((l.get("name") if isinstance(l, dict) else l) == name for l in labels)


def planned(recs):
    """True once a planner has run on the issue.

    From then on it follows the normal flow."""
    return any(r.get("role") == "planner" for r in recs)


def in_lane(repo, number, recs):
    """True when the issue is labeled hotfix and was never planned."""
    return not planned(recs) and labeled(repo, number)


def write_ask(dest, body):
    """Write ask.md into the pack: the owner's ask, as written, is the whole ask."""
    text = ask(body or "").strip()
    open(os.path.join(dest, ASK), "w").write(f"# The ask\n\n{text}\n")


def lane_prompt(text, on):
    """The prompt with its hotfix sections kept, markers removed (on), or dropped (off)."""
    return SECTION.sub(lambda m: m.group(1) if on else "", text)


def back_to_planning(repo, number, rec):
    """Say on the issue why its hotfix goes back to planning.

    The comment lists the blockers for the planner: the code review's, or the worker's when the ask needs a design
    choice (#864)."""
    why = "the worker found the ask needs a design choice" if rec.get("role") == "worker" else \
        "code review found the change bigger than the ask"
    blockers = [r.get("text", "") for r in (rec.get("handback") or {}).get("raises") or []
                if isinstance(r, dict) and r.get("kind") == "blocker" and r.get("to") == "planner"]
    lines = "\n".join(f"- {t}" for t in blockers if t)
    agent_github.gh("issue", "comment", str(number), "-R", repo, "--body",
                    f"This hotfix goes back to normal planning: {why}.\n\n{lines}\n")


def main(argv):
    """labeled N | prompt on|off FILE | label."""
    if argv == ["label"]:
        print(label())
        return 0
    if argv[:1] == ["labeled"] and len(argv) == 2:
        return 0 if labeled(os.environ["GITHUB_REPOSITORY"], argv[1]) else 1
    if argv[:1] == ["prompt"] and len(argv) == 3:
        text = open(argv[2]).read()
        open(argv[2], "w").write(lane_prompt(text, argv[1] == "on"))
        return 0
    print(main.__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

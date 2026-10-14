"""The rules as tests read them: `AGENTS.md` and every topic file it links.

The rules file (`AGENTS.md`) becomes a short index that links one file per topic (#638, story 3 of #581). Tests that
check a rule is written down read the rules through here, so they find a section wherever the split puts it. Topic
files follow the index's links in order, as the word check (`dokima.agent_next.rules_texts`) and agent.yml's runtime
copy read them: only repo markdown files, never a web link or a file outside the repo.
"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LINK = re.compile(r"\]\(([^)#\s:]+\.md)(?:#[^)]*)?\)")


def rules_files(root=ROOT):
    """`AGENTS.md`, then every existing repo markdown file it links, as repo paths."""
    index = open(os.path.join(root, "AGENTS.md"), encoding="utf-8").read()
    out = ["AGENTS.md"]
    for link in LINK.findall(index):
        path = os.path.normpath(link)
        if os.path.isabs(path) or path.split(os.sep)[0] == "..":
            continue
        if path not in out and os.path.isfile(os.path.join(root, path)):
            out.append(path)
    return out


def rules_text(root=ROOT):
    """The whole rules as one text: `AGENTS.md`, then each topic file it links."""
    return "\n\n".join(open(os.path.join(root, f), encoding="utf-8").read().rstrip("\n") + "\n"
                       for f in rules_files(root))

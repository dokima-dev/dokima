"""Each "Raised earlier" item says who raised it, linked to where (#478).

The owner's words: each item under "Raised earlier" says who raised it, with a link, e.g. "Code review on #462
raised:". A run comment's Raised earlier section lists the earlier raises its run answered; until now an item showed
only the raise itself, so the owner could not tell which step raised it or find the comment it came from.

What the code these tests run must do, as the plan pins it:
- An item under "Raised earlier" opens, right after "- ", with who raised it: "Planner", "Worker", "Plan review" or
  "Code review", from the role and stage of the record whose hand-back holds the raise; then " on [#N](URL)", where URL
  is the GitHub comment that record was posted as and N the number of the issue or pull request that comment is on;
  then " raised: ", then the raise as before: its kind's icon, label, words and who it is for. Its answer stays under it.
- The record step (`python3 -m dokima.agent record ...`) finds those comments through the starting pack that
  `agent.pack()` built from GitHub's comments, which carry each comment's "url".
- When the comment a raise came from is not known (an earlier record with no place on GitHub), the item still names
  who raised it, "Planner raised: ", with no link: a wrong or empty link is never drawn.

The tests fake GitHub (gh) in-process for the pack and run the real record step as the workflow does.
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
N, PR = 9, 12
SRC = f"https://github.com/{REPO}/issues/{N}"
FULL = re.compile(r"<details><summary>Full record</summary>.*?</details>", re.S)
META = {"run_id": "7", "run": f"https://github.com/{REPO}/actions/runs/7", "log": "https://x/log",
        "models": ["claude-opus-5-5"],
        "report": {"duration_ms": 1000, "turns": 2, "cost_usd": 0.5, "tokens_in": 100, "tokens_out": 20}}
ICON_OF = {"question": "question", "blocker": "blocker", "issue": "issue found"}

PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id.", "user_story": "Owners get a job id.",
        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": SRC}],
        "non_functional": [{"text": "Nothing leaks.", "why": "safety", "principle": "Fail closed"}],
        "scope": ["dokima/agent.py"], "out_of_scope": ["The board."],
        "tests": {f"{N}.1": ["tests/test_a.py::test_one"]}, "test_changes": {},
        "links": {"blocked_by": [], "blocks": [], "relates_to": []}}

# One raise from each of the four steps, as code stamps them; every text and why is unique.
P1 = {"kind": "question", "to": "owner", "label": "Column qx", "text": "Should a cancelled run keep its column qx?",
      "evidence": "dokima/board.py", "raised_by": "planner", "id": "P1"}
R2 = {"kind": "question", "to": "owner", "label": "Timeout qx", "text": "Is twenty seconds the right timeout qx?",
      "raised_by": "reviewer", "id": "R2"}
W3 = {"kind": "blocker", "to": "planner", "label": "Kept test qx", "text": "The kept test reads a missing file qx.",
      "evidence": "tests/test_a.py", "raised_by": "worker", "id": "W3"}
R4 = {"kind": "blocker", "to": "worker", "label": "Speed qx", "text": "submit() still blocks for a minute qx.",
      "evidence": "dokima/agent.py", "raised_by": "reviewer", "id": "R4"}

# Where each raise was posted: (who raised it, the issue or PR number, the comment's link).
WHERE = {"P1": ("Planner", N, f"https://github.com/{REPO}/issues/{N}#issuecomment-101"),
         "R2": ("Plan review", N, f"https://github.com/{REPO}/issues/{N}#issuecomment-102"),
         "W3": ("Worker", PR, f"https://github.com/{REPO}/pull/{PR}#issuecomment-203"),
         "R4": ("Code review", PR, f"https://github.com/{REPO}/pull/{PR}#issuecomment-204")}
RAISE = {"P1": P1, "R2": R2, "W3": W3, "R4": R4}
WHY = {k: f"The answer to {k} is settled qx{k}." for k in RAISE}


def rec(role, stage, **handback):
    """One record as the record step builds it, passed."""
    return {"role": role, "stage": stage, **META, "handback": handback, "check": {"passed": True, "problems": []}}


PLANNER = rec("planner", None, **dict(PLAN, raises=[P1], answers=[]))
PLAN_REVIEW = rec("reviewer", "plan", verdict="approve", summary="The plan holds.", asks=[], raises=[R2], answers=[])
WORKER = rec("worker", None, summary="Built the job id.", criteria={f"{N}.1": "returns a job id"}, evidence="3 passed",
             raises=[W3], answers=[])
CODE_REVIEW = rec("reviewer", "pr", verdict="block", summary="The job id is slow.", asks=[], raises=[R4], answers=[])


def posted(r, url, at):
    """A comment as GitHub's CLI returns it, carrying a record the bot posted."""
    return {"author": {"login": agent.BOT}, "body": agent.render(r), "createdAt": at, "url": url}


def fake_github(monkeypatch):
    """Fake GitHub: records on issue #9 and its pull request #12, each with its link.

    The issue holds the planner's and the plan review's records, the pull request the worker's and the code review's."""
    on_issue = [posted(PLANNER, WHERE["P1"][2], "2026-10-09T10:00:00Z"),
                posted(PLAN_REVIEW, WHERE["R2"][2], "2026-10-09T11:00:00Z")]
    on_pr = [posted(WORKER, WHERE["W3"][2], "2026-10-09T12:00:00Z"),
             posted(CODE_REVIEW, WHERE["R4"][2], "2026-10-09T13:00:00Z")]

    def gh(*args):
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": N, "title": "T", "body": "B", "comments": on_issue})
        if args[:2] == ("pr", "list"):
            return json.dumps([{"number": PR}] if f"try/issue-{N}" in args else [])
        if args[:2] == ("pr", "view"):
            return json.dumps({"comments": on_pr, "reviews": []})
        if args[:2] == ("run", "download"):
            return ""
        if args[0] == "api" and "/parent" in args[1]:
            raise subprocess.CalledProcessError(1, "gh", stderr="HTTP 404: Not Found")
        if args[0] == "api" and "/pulls/" in args[1] and args[1].rstrip("/").endswith("/comments"):
            return "[]"
        if args[0] == "api" and args[1].lstrip("/").startswith(f"repos/{REPO}/issues"):
            return "[]"
        raise AssertionError(f"unexpected gh call {args}")
    monkeypatch.setattr(agent, "gh", gh)


def record_step(pack, role, stage, handback, out):
    """Run the workflow's record step on this hand-back and pack; return the comment."""
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    (out / {"planner": "plan.json", "worker": "work.json", "reviewer": "review.json"}[role]).write_text(json.dumps(handback))
    (out / "check.txt").write_text("")
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_REPOSITORY": REPO,
           "GITHUB_RUN_ID": "42", "PACK": str(pack), "STAGE": stage or ""}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "record", role, stage or "", str(out), str(out / "check.txt"),
                        "true", str(logs)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and (out / "comment.md").exists(), \
        f"the record step failed (exit {r.returncode}):\n{r.stderr[-800:]}"
    return FULL.sub("", (out / "comment.md").read_text())


def earlier_items(text):
    """The items under the "Raised earlier:" heading; None without that heading."""
    lines = text.splitlines()
    at = [i for i, l in enumerate(lines) if re.fullmatch(r"\s*(<img[^>]*>\s*)*\*\*Raised earlier:\*\*\s*", l)]
    if not at:
        return None
    items = []
    for l in lines[at[0] + 1:]:
        if l.startswith("- "):
            items.append([l])
        elif l[:1].isspace() and l.strip() and items:
            items[-1].append(l)
        elif l.strip():
            break
    return ["\n".join(i) for i in items]


def item_for(items, rid):
    """The one item showing the raise `rid`."""
    found = [i for i in items if RAISE[rid]["text"] in i]
    assert len(found) == 1, f"expected one Raised earlier item showing {RAISE[rid]['text']!r}, found {len(found)}:\n" \
        + "\n".join(items)
    return found[0]


FINAL = [("reviewer", "pr", ["P1", "R2", "W3", "R4"], "a code review"),
         ("reviewer", "plan", ["P1"], "a plan review"),
         ("worker", None, ["R4"], "a worker"),
         ("planner", None, ["R2", "W3"], "a planner")]


@pytest.mark.parametrize("role, stage, answered, who", FINAL)
def test_each_earlier_raise_says_who_raised_it_and_links_where(record_property, monkeypatch, tmp_path, role, stage,
                                                                answered, who):
    """Each Raised earlier item opens with who raised it, linked to that comment.

    Fakes GitHub so the issue holds a planner's and a plan review's records and its pull request a worker's and a
    code review's, each raising one thing; builds the starting pack as the workflow does and runs the record step for
    a run answering them. Checks every item opens with "Planner", "Plan review", "Worker" or "Code review" on the
    issue or pull request number, linked to that exact comment, then "raised:" and the raise, with its answer under it.

    Proves 478.1."""
    record_property("proves", "478.1")
    fake_github(monkeypatch)
    pack = tmp_path / "pack"
    agent.pack(REPO, N, role, stage or "", str(pack))
    answers = [{"raise": k, "answer": "done", "why": WHY[k]} for k in answered]
    if role == "reviewer":
        handback = dict(verdict="approve", summary="All holds.", asks=[], raises=[], answers=answers)
    elif role == "worker":
        handback = dict(summary="Sped it up.", criteria={f"{N}.1": "fast"}, evidence="3 passed", raises=[], answers=answers)
    else:
        handback = dict(PLAN, raises=[], answers=answers)
    text = record_step(pack, role, stage, handback, tmp_path / "out")
    items = earlier_items(text)
    assert items is not None and len(items) == len(answered), \
        f"478.1: {who}'s comment answered {len(answered)} raises but its Raised earlier section shows {items}:\n{text}"
    for k in answered:
        name, number, url = WHERE[k]
        item = item_for(items, k)
        first = item.splitlines()[0]
        want = f"- {name} on [#{number}]({url}) raised: " + card.field_icon(REPO, ICON_OF[RAISE[k]["kind"]])
        assert first.startswith(want), (f"478.1: in {who}'s comment, the raise {k} must open with who raised it and "
                                        f"where, {want!r}; it reads:\n{first}")
        assert WHY[k] in item, f"478.1: in {who}'s comment, the answer to {k} is no longer shown under it:\n{item}"


def test_a_raise_whose_comment_is_unknown_names_who_raised_it_with_no_link(record_property, monkeypatch):
    """A raise whose comment is not known still says who raised it, with no link.

    Draws a code review answering a planner's and a worker's raises found in earlier records that carry no place on
    GitHub, and checks each item opens with "Planner raised:" or "Worker raised:" and the raise's icon, with no
    "on #" and no link before the raise.

    Proves 478.2."""
    record_property("proves", "478.2")
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    answers = [{"raise": k, "answer": "disagree", "why": WHY[k]} for k in ("P1", "W3")]
    review = rec("reviewer", "pr", verdict="approve", summary="All holds.", asks=[], raises=[], answers=answers)
    items = earlier_items(FULL.sub("", agent.render(review, earlier=[PLANNER, WORKER])))
    assert items is not None and len(items) == 2, f"478.2: the review's Raised earlier section shows {items}"
    for k, name in (("P1", "Planner"), ("W3", "Worker")):
        first = item_for(items, k).splitlines()[0]
        want = f"- {name} raised: " + card.field_icon(REPO, ICON_OF[RAISE[k]["kind"]])
        assert first.startswith(want), (f"478.2: a raise from a record with no known comment must open {want!r}, "
                                        f"naming who raised it with no link; it reads:\n{first}")

"""Tests for #746: problems filed in Dokima's public repo show none of the private code.

On the job-hunt trial, Dokima's own problems file themselves in dokima-dev/dokima (#745), which is public. An agent's
problem may quote the repo it ran on: a path to one of its files, or a line of its code. The owner wants nothing of the
private repo there, its code included (#746). Each test stands in a git checkout of the trial repo holding a private
file, files a problem tagged as Dokima's fault that quotes it, and reads what Dokima's repo then holds. Dokima's own
words and paths, which the trial repo does not hold, must still reach Dokima's repo, so the cut is not a blanket one.

Every test runs against tests/upstream_gh.py, the fake `gh` of tests/test_upstream.py. Nothing leaves the machine.
"""
import os
import subprocess

from test_upstream import UPSTREAM, checked_and_filed, everything, github, issues, name_upstream  # noqa: F401

PRIVATE_PATH = "src/leads_ranker.py"
PRIVATE_LINE = "weight = HIRING_SIGNAL_WEIGHTS['acme-recruiting']"


def private_checkout():
    """Make the current folder a git checkout holding one committed private file."""
    os.makedirs("src", exist_ok=True)
    with open(PRIVATE_PATH, "w") as f:
        f.write(f"def rank(lead):\n    {PRIVATE_LINE}\n    return lead.score * weight\n")
    for args in (["init", "-q"], ["config", "user.name", "Trial Owner"], ["config", "user.email", "owner@example.com"],
                 ["add", "-A"], ["commit", "-q", "-m", "private code"]):
        subprocess.run(["git", *args], check=True, capture_output=True)


def filed_text(github, problem):
    """File PROBLEM from issue 9 and return everything Dokima's repo then holds.

    PROBLEM is a raise tagged as Dokima's fault."""
    name_upstream()
    checked_and_filed("746", 9, [problem])
    up = issues(github(), UPSTREAM)
    assert len(up) == 1, f"the problem should be filed once in {UPSTREAM}; it holds {up}"
    return "\n".join(i["title"] + "\n" + everything(i) for i in up.values())


def test_a_private_file_path_never_reaches_dokimas_repo(record_property, github):
    """A problem naming a private file shows no such path in Dokima's repo.

    The trial checkout holds `src/leads_ranker.py`. A confirmed problem tagged as Dokima's fault says the card breaks
    on that file, with evidence naming it beside Dokima's own `dokima/card.py`. Dokima's repo must not hold the private
    path, and must still hold Dokima's own path and the problem's words.
    Proves 746.1."""
    record_property("proves", "746.1")
    private_checkout()
    problem = {"kind": "issue", "label": "Card breaks on a file", "fault": "dokima",
               "text": "The card breaks when a plan names a deep file.",
               "evidence": f"`{PRIVATE_PATH}` in the plan made `dokima/card.py` cut the fold.",
               "verdict": "new", "searched": [3]}
    text = filed_text(github, problem)
    assert PRIVATE_PATH not in text and "leads_ranker" not in text, \
        f"746.1: Dokima's public repo shows a file path of the private repo: {text!r}"
    assert "dokima/card.py" in text, \
        f"746.1: Dokima's own file path, which the private repo does not hold, was cut too: {text!r}"
    assert "The card breaks when a plan names a deep file." in text, \
        f"746.1: the problem's own words should still reach Dokima's repo: {text!r}"


def test_a_line_of_the_private_code_never_reaches_dokimas_repo(record_property, github):
    """A problem quoting a line of private code shows no such line in Dokima's repo.

    The trial checkout's `src/leads_ranker.py` holds a line naming a hiring weight for a company. A confirmed problem
    tagged as Dokima's fault quotes that line in its text and evidence. Dokima's repo must not hold the line or the
    company it names, and must still hold the problem's own words.
    Proves 746.2."""
    record_property("proves", "746.2")
    private_checkout()
    problem = {"kind": "issue", "label": "Worker misreads a line", "fault": "dokima",
               "text": f"The worker misreads a dictionary lookup such as `{PRIVATE_LINE}` as a call.",
               "evidence": f"The worker's run quoted `{PRIVATE_LINE}` as a function call.",
               "verdict": "new", "searched": [3]}
    text = filed_text(github, problem)
    assert PRIVATE_LINE not in text and "acme-recruiting" not in text and "HIRING_SIGNAL_WEIGHTS" not in text, \
        f"746.2: Dokima's public repo shows a line of the private repo's code: {text!r}"
    assert "The worker misreads a dictionary lookup" in text, \
        f"746.2: the problem's own words should still reach Dokima's repo: {text!r}"

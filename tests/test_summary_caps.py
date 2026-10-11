"""Every card opens on one short sentence, and worker docstrings are capped too.

Issue #240 (story 2 of #229). The planner's, worker's and reviewer's summaries are each one sentence of at most 25
words; every docstring the worker adds or changes opens with a line of at most 15 words. As in story 1 (#239,
dokima/words.py), a text up to 20% over its cap (30 words for 25, 18 for 15) passes and is listed; one past that is
rejected, naming it and its word count. A summary with a second sentence is rejected however short it is.

The planner's tests run `python3 -m dokima.planner check 9 OUT` through the `check` fixture of tests/test_plan_check.py.
The worker's and reviewer's tests run the real command the workflow runs, `python3 -m dokima.agent check work|review
FILE PLAN N`, from a temp git repo whose base commit is PLANNER_BASE, as the workflow sets it for every run; the
worker's code there lives in app/, so nothing in the temp repo shadows Dokima's own package.
"""
import copy
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent  # noqa: E402
from tests.test_handback_check import REVIEW, STORY as PLAN_9, WORK  # noqa: E402
from tests.test_plan_check import FEATURE, STORY, check  # noqa: E402,F401
from tests.test_run_cards import PR, names_pr, plain, rec, shown  # noqa: E402
from tests.test_word_caps import jobs, run as run_planner, words  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TWO_SENTENCES = "Slow calls blocked the server. They now run as jobs."
OLD_DOC = words(20)  # an older docstring, already on main, far over the 15-word cap


@pytest.fixture
def repo(tmp_path):
    """A temp git repo with app/x.py as its base, and an agent check runner.

    The base holds `old`, whose docstring opens with 25 words, and `kept`, with a short one. The returned function
    writes the hand-back and plan 9, runs `agent check KIND` with PLANNER_BASE at the base, and returns
    (exit code, stdout + stderr).
    """
    root = tmp_path / "repo"
    (root / "app").mkdir(parents=True)
    git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, text=True).stdout
    git("init", "-q")
    git("config", "user.name", "t")
    git("config", "user.email", "t@t")
    (root / "app" / "x.py").write_text(base_x())
    git("add", "-A")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").strip()

    def run(kind, handback, plan=PLAN_9):
        f, p = tmp_path / f"{kind}.json", tmp_path / "plan.json"
        f.write_text(json.dumps(handback))
        p.write_text(json.dumps(plan))
        env = {**os.environ, "PYTHONPATH": ROOT, "PLANNER_BASE": base}
        for k in ("PYTHONSAFEPATH", "STAGE"):
            env.pop(k, None)
        r = subprocess.run([sys.executable, "-m", "dokima.agent", "check", kind, str(f), str(p), "9"], cwd=root,
                           env=env, capture_output=True, text=True, timeout=30)
        assert "Traceback" not in r.stdout + r.stderr, f"the {kind} check crashed:\n{r.stderr[-800:]}"
        return r.returncode, r.stdout + r.stderr
    run.root, run.git, run.base = root, git, base
    return run


def base_x(extra=""):
    """app/x.py as the base has it (old and kept), plus `extra` at the end."""
    return (f'def old():\n    """{OLD_DOC}"""\n    return 1\n\n\n'
            f'def kept():\n    """Kept short."""\n    return 2\n' + extra)


def fn(name, doc):
    """A function `name` whose docstring opens with `doc`, a 40-word paragraph below."""
    return f'\n\ndef {name}():\n    """{doc}\n\n    {words(40)}\n    """\n    return 3\n'


def reset(run):
    """Put the temp repo back to its base, with no commits, changes or new files."""
    run.git("reset", "-q", "--hard", run.base)
    run.git("clean", "-qfd")


def line_naming(out, where, n):
    """The output line naming `where` with its n words, or None."""
    return next((l for l in out.splitlines() if where in l and f"{n} words" in l), None)


def test_the_planners_summary_is_one_sentence_of_at_most_25_words(record_property, check, capsys):
    """The planner's summary is one sentence of at most 25 words.

    Proves 240.1. A 20-word summary passes unlisted, in a story and a split; a 24-word one passes and is listed with
    its word count. A 25-word summary is rejected naming the summary and its 31 words, in a story and a split. A
    summary of two short sentences is rejected naming the summary.
    """
    record_property("proves", "240.1")
    for plan in (dict(STORY, summary=words(20)), dict(FEATURE, summary=words(20))):
        rc, why, printed = run_planner(check, capsys, plan, jobs(), "240.1")
        assert rc == 0 and not why, f"240.1: a 20-word one-sentence summary got the plan rejected: {why!r}"
        assert "summary" not in printed, f"240.1: a summary within its cap was listed as over it: {printed!r}"
    rc, why, printed = run_planner(check, capsys, dict(STORY, summary=words(24)), jobs(), "240.1")
    assert rc == 0 and not why, f"240.1: a 24-word summary, within 20% of its cap, got the plan rejected: {why!r}"
    assert line_naming(printed, "summary", 24), f"240.1: the 24-word summary is not listed as over its cap: {printed!r}"
    for plan in (dict(STORY, summary=words(25)), dict(FEATURE, summary=words(25))):
        rc, why, _ = run_planner(check, capsys, plan, jobs(), "240.1")
        assert rc == 1, f"240.1: a {plan['kind']} with a 25-word summary was accepted; the cap is 25 (30 at most)"
        assert "summary" in why and "31 words" in why, f"240.1: the reason does not name the summary and its 31 words: {why!r}"
    rc, why, _ = run_planner(check, capsys, dict(STORY, summary=TWO_SENTENCES), jobs(), "240.1")
    assert rc == 1 and "summary" in why, f"240.1: a summary of two sentences was not rejected naming the summary: {why!r}"


def test_the_worker_card_opens_with_its_one_sentence_summary(record_property, repo):
    """The worker's card opens with its whole summary: one sentence, 25 words at most.

    Proves 240.2. The worker's check passes a 20-word one-sentence summary unlisted, and rejects a 25-word one and a
    summary of two short sentences, each naming the summary. A passed worker card shows the summary, word for word,
    as its one line on top, with the pull request linked. The worker's prompt asks for one sentence of at most 25
    words, never for two sentences.
    """
    record_property("proves", "240.2")
    rc, out = repo("work", dict(WORK, summary=words(20)))
    assert rc == 0, f"240.2: a 20-word one-sentence worker summary was rejected:\n{out}"
    assert "summary" not in out, f"240.2: a worker summary within its cap was listed as over it:\n{out}"
    rc, out = repo("work", dict(WORK, summary=words(25)))
    assert rc == 1 and line_naming(out, "summary", 25), f"240.2: a 25-word worker summary was not rejected naming it:\n{out}"
    rc, out = repo("work", dict(WORK, summary=TWO_SENTENCES))
    assert rc == 1 and any("summary" in l for l in out.splitlines()), \
        f"240.2: a worker summary of two sentences was not rejected naming the summary:\n{out}"
    summary = "Slow calls now run as jobs and return an id at once."
    lines = shown(agent.render(rec("worker", handback=dict(WORK, summary=summary)), pr=PR))
    assert len(lines) == 1 and plain(lines[0]).startswith(summary), \
        f"240.2: the worker card does not open with its whole summary, word for word ({summary!r}): {lines!r}"
    assert names_pr(lines[0]), f"240.2: the worker card's opening line does not name its pull request:\n{lines[0]}"
    prompt = open(os.path.join(ROOT, "dokima", "roles", "worker.md"), encoding="utf-8").read()
    shape = next((l for l in prompt.splitlines() if '"summary"' in l), "")
    assert "two" not in shape.lower() and "one" in shape.lower() and "20 words" in shape, \
        f"240.2: the worker's prompt does not ask for a summary of one sentence of at most 25 words: {shape!r}"


def test_the_reviewers_summary_is_one_sentence_of_at_most_25_words(record_property, repo):
    """The reviewer's summary is one sentence of at most 25 words.

    Proves 240.3. The reviewer's check passes a 20-word one-sentence summary unlisted, and rejects a 25-word one
    naming it and its 31 words, and a summary of two short sentences naming the summary.
    """
    record_property("proves", "240.3")
    rc, out = repo("review", dict(REVIEW, summary=words(20)))
    assert rc == 0, f"240.3: a 20-word one-sentence review summary was rejected:\n{out}"
    assert "summary" not in out, f"240.3: a review summary within its cap was listed as over it:\n{out}"
    rc, out = repo("review", dict(REVIEW, summary=words(25)))
    assert rc == 1 and line_naming(out, "summary", 25), f"240.3: a 25-word review summary was not rejected naming it:\n{out}"
    rc, out = repo("review", dict(REVIEW, summary=TWO_SENTENCES))
    assert rc == 1 and any("summary" in l for l in out.splitlines()), \
        f"240.3: a review summary of two sentences was not rejected naming the summary:\n{out}"


def test_each_docstring_the_worker_adds_or_changes_opens_with_at_most_15_words(record_property, repo):
    """Each docstring the worker adds or changes opens with 15 words at most.

    Proves 240.4. New docstrings of 15 words (a function, a method, a new file) pass unlisted, and the older 20-word
    docstring the worker left alone is never named. A 19-word first line is rejected by name and word count when
    added in a commit, added uncommitted, in a method, in a new file's module docstring, or in an older docstring
    the worker rewrote; the 40-word paragraph below a first line never counts.
    """
    record_property("proves", "240.4")
    root = repo.root
    (root / "app" / "x.py").write_text(base_x(fn("fresh", words(15)) + f'\n\nclass Box:\n    def fresh(self):\n'
                                              f'        """{words(15)}"""\n        return 4\n'))
    (root / "app" / "y.py").write_text(f'"""{words(15)}"""\n')
    rc, out = repo("work", WORK)
    assert rc == 0, f"240.4: docstrings of 15 words, with long paragraphs below, were rejected:\n{out}"
    assert "app/" not in out, f"240.4: a docstring within its cap, or an older one left alone, was named:\n{out}"
    cases = [("committed", lambda: (root / "app" / "x.py").write_text(base_x(fn("fresh", words(19)))), "app/x.py::fresh"),
             ("uncommitted", lambda: (root / "app" / "x.py").write_text(base_x(fn("fresh", words(19)))), "app/x.py::fresh"),
             ("method", lambda: (root / "app" / "x.py").write_text(base_x(
                 f'\n\nclass Box:\n    def fresh(self):\n        """{words(19)}"""\n        return 4\n')), "app/x.py::Box.fresh"),
             ("new file", lambda: (root / "app" / "y.py").write_text(f'"""{words(19)}"""\n'), "app/y.py"),
             ("rewritten", lambda: (root / "app" / "x.py").write_text(
                 base_x().replace('"""Kept short."""', f'"""{words(19)}"""')), "app/x.py::kept")]
    for name, write, where in cases:
        reset(repo)
        write()
        if name == "committed":
            repo.git("commit", "-qam", "the worker's change")
        rc, out = repo("work", WORK)
        assert rc == 1 and line_naming(out, where, 19), \
            f"240.4: a 19-word docstring first line ({name}, {where}) was not rejected naming it and its 19 words:\n{out}"
        assert "app/x.py::old" not in out, f"240.4: the older docstring the worker left alone was named:\n{out}"


def test_the_worker_and_reviewer_checks_list_every_text_over_its_cap_and_reject_only_past_20_percent(record_property, repo):
    """Worker and reviewer checks list every text over its cap, rejecting only past 20%.

    Proves 240.5. A 24-word worker summary beside a 17-word docstring passes, and the check lists both with their word
    counts; a 30-word review summary passes and is listed. A 25-word worker summary beside a 19-word docstring is
    rejected naming both; a 25-word review summary is rejected naming it.
    """
    record_property("proves", "240.5")
    root = repo.root
    (root / "app" / "x.py").write_text(base_x(fn("fresh", words(17))))
    rc, out = repo("work", dict(WORK, summary=words(24)))
    assert rc == 0, f"240.5: a 24-word worker summary and a 17-word docstring, within 20%, were rejected:\n{out}"
    for where, n in (("summary", 24), ("app/x.py::fresh", 17)):
        assert line_naming(out, where, n), f"240.5: the worker's check does not list {where} with its {n} words:\n{out}"
    (root / "app" / "x.py").write_text(base_x(fn("fresh", words(19))))
    rc, out = repo("work", dict(WORK, summary=words(25)))
    assert rc == 1, f"240.5: a 25-word worker summary and a 19-word docstring were accepted:\n{out}"
    for where, n in (("summary", 25), ("app/x.py::fresh", 19)):
        assert line_naming(out, where, n), f"240.5: the worker's rejection does not name {where} and its {n} words:\n{out}"
    reset(repo)
    rc, out = repo("review", dict(REVIEW, summary=words(24)))
    assert rc == 0 and line_naming(out, "summary", 24), \
        f"240.5: a 24-word review summary was not passed and listed with its word count:\n{out}"
    rc, out = repo("review", dict(REVIEW, summary=words(25)))
    assert rc == 1 and line_naming(out, "summary", 25), f"240.5: a 25-word review summary was not rejected naming it:\n{out}"

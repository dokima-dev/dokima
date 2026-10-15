"""Every raise and split story has a short plain half and a full half (#709).

The owner reads short halves: capped, plain words, no code. Agents read full halves: uncapped, and they may name code
(#559, and the owner's answer on #709). These tests run the real checks the workflow runs, from outside, the way a run
sees them: `python3 -m dokima.planner check 9 OUT` on a planner's plan.json, and `python3 -m dokima.agent check review
FILE PLAN 9` on a reviewer's review.json. Each reads back the exit code and the reasons given.

The shapes these tests pin, so the worker knows them exactly:
- A raise keeps its short half in "text" and holds its full half in a new field, "full": each non-empty text.
- A split story's "user_story" and its optional "context" are each a pair, {"short": ..., "full": ...}, both halves
  non-empty text. A plain string is no longer a pair.
- A short half that names code is rejected, whatever the raise's kind; a full half is never capped and may name code.
- A rejection names the raise ("raise 2") or the story ("story 2"), and says which half is missing ("short half" or
  "full half") or that the text names code ("names code"), in one reason.
The last two tests read the role prompts: every example raise there passes the new check, and the planner prompt's
split story shape shows both halves.
"""
import copy
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import raises, words  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISSUE = "https://github.com/o/r/issues/9"
CODE = "`dokima/raises.py`, `check_raises()` and `tests/test_x.py::test_a`"
LONG = " ".join(["word"] * 300)  # longer than every word cap the owner set

QUESTION = {"kind": "question", "to": "owner", "label": "Two readings",
            "text": "Should ids be numbers? The plan assumes strings.",
            "full": "Job ids are strings today in the stand-in job store, so the plan keeps them strings.",
            "evidence": "The issue names no id type."}
BLOCKER = {"kind": "blocker", "to": "worker", "label": "No test",
           "text": "Criterion 9.1 has no passing test yet.",
           "full": "The test for 9.1 still fails on the branch: the job store never returns an id.",
           "evidence": "plan.json"}
ISSUE_FOUND = {"kind": "issue", "label": "Outside this issue",
               "text": "The board ignores closed pull requests, so their cards go stale.",
               "full": "The board's column logic reads only open pull requests, so a closed one keeps its old column.",
               "evidence": "e"}


def pair(short, full):
    """A short and full pair, as a split story's user story and context are written."""
    return {"short": short, "full": full}


FEATURE = {"kind": "feature", "title": "Slow calls run as jobs", "summary": "Slow calls hand back a job id instead of timing out.",
           "feature": "Slow calls run as jobs.",
           "stories": [{"title": "Job ids",
                        "user_story": pair("Slow calls return a job id.", "A slow call hands back a job id at once."),
                        "context": pair("The job store is new.", "No job store exists yet; the worker writes one."),
                        "acceptance_criteria": [{"text": "A slow call returns a job id.", "source": ISSUE, "files": ["dokima/jobs.py"]},
                                                {"text": "A fast call returns its result.", "source": ISSUE, "files": ["dokima/jobs.py"]}],
                        "non_functional": [], "depends_on": []},
                       {"title": "Job status",
                        "user_story": pair("Owners see each job's status.", "Each job's status shows on its issue."),
                        "context": pair("Status shows on the card.", "The card draws each job's status from its record."),
                        "acceptance_criteria": [{"text": "A job's status is shown.", "source": ISSUE, "files": ["dokima/status.py"]},
                                                {"text": "A finished job shows its result.", "source": ISSUE, "files": ["dokima/status.py"]}],
                        "non_functional": [], "depends_on": [0]}],
           "links": {"blocked_by": [], "blocks": [], "relates_to": []},
           "raises": [QUESTION], "answers": []}

STORY_PLAN = {"kind": "user_story", "user_story": "u",
              "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
              "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
              "tests": {"9.1": ["tests/test_x.py::test_a"]}}
REVIEW = {"previous_step": {"did": ["Read the plan."], "decided": [], "open": []},
          "verdict": "block", "summary": "One proof is missing.",
          "raises": [BLOCKER, ISSUE_FOUND], "answers": [],
          "asks": [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"}],
          "size": "ok",
          "behaviors": [{"criterion": "9.1", "one_behavior": True, "why": "one result"}],
          "edge_cases": [{"criterion": "9.1", "cut": [], "missing": []}],
          "tests": [{"test": "tests/test_x.py::test_a", "only_its_behavior": True, "why": "one result"}]}


def env():
    """The environment a check runs in: issue 9 of o/r, nothing else set."""
    e = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r"}
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE", "PLANNER_RUN_BASE", "PACK", "STAGE", "STYLE_SOFT"):
        e.pop(k, None)
    return e


def plan_check(tmp_path, plan):
    """Run the planner's check on a plan.json; return its exit code and reasons."""
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    for old in out.iterdir():
        old.unlink()
    (out / "plan.json").write_text(json.dumps(plan))
    p = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(out)], cwd=ROOT, env=env(),
                       capture_output=True, text=True, timeout=60)
    assert "Traceback" not in p.stderr, f"the planner's check crashed:\n{p.stderr[-800:]}"
    why = (out / "rejected.txt").read_text() if (out / "rejected.txt").exists() else ""
    return p.returncode, [s.strip() for s in re.split(r";\s|\n", why) if s.strip()]


def review_check(tmp_path, review):
    """Run the reviewer's hand-back check on a review.json against a one-criterion plan for issue 9.

    Returns (exit code, its reasons, one per line)."""
    f, p = tmp_path / "review.json", tmp_path / "plan.json"
    f.write_text(json.dumps(review))
    p.write_text(json.dumps(STORY_PLAN))
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "check", "review", str(f), str(p), "9"], cwd=ROOT,
                       env=env(), capture_output=True, text=True, timeout=60)
    assert "Traceback" not in r.stderr + r.stdout, f"the reviewer's check crashed:\n{r.stderr[-800:]}"
    return r.returncode, [line.strip() for line in r.stdout.splitlines() if line.strip()]


def feature(change):
    """A copy of the good feature with one change applied."""
    f = copy.deepcopy(FEATURE)
    change(f)
    return f


def review(change):
    """A copy of the good review with one change applied."""
    r = copy.deepcopy(REVIEW)
    change(r)
    return r


def named(reasons, *parts):
    """True when one reason holds every part."""
    return any(all(p in r for p in parts) for r in reasons)


def assert_good(crit, tmp_path, plan=None, rev=None, case="the good hand-back"):
    """Both checks pass the given plan and review; fails naming the criterion and case."""
    if plan is not None:
        rc, why = plan_check(tmp_path, plan)
        assert rc == 0 and not why, f"{crit}: the planner's check rejected {case}: {why}"
    if rev is not None:
        rc, why = review_check(tmp_path, rev)
        assert rc == 0, f"{crit}: the reviewer's check rejected {case}: {why}"


def assert_rejected(crit, tmp_path, case, *parts, plan=None, rev=None):
    """The check rejects the hand-back with one reason holding every part."""
    rc, why = plan_check(tmp_path, plan) if plan is not None else review_check(tmp_path, rev)
    who = "planner's" if plan is not None else "reviewer's"
    assert rc != 0, f"{crit}: the {who} check passed {case}"
    assert named(why, *parts), f"{crit}: the {who} check rejected {case}, but no reason names {' and '.join(map(repr, parts))}: {why}"


def without(d, key):
    """A copy of the object with one key left out."""
    return {k: v for k, v in d.items() if k != key}


def test_a_raise_with_no_short_half_is_rejected_naming_it(record_property, tmp_path):
    """A raise with no short half is rejected, and the reason names the raise.

    Runs the planner's and the reviewer's real checks: a raise with both halves passes first. Then a second raise with
    its short half left out, or blank, is rejected with a reason naming raise 2 and its short half; the same holds for
    a reviewer's raise.

    Proves 709.1."""
    record_property("proves", "709.1")
    assert_good("709.1", tmp_path, plan=FEATURE, rev=REVIEW, case="raises with both halves")
    for case, bad in (("a raise with its short half left out", without(QUESTION, "text")),
                      ("a raise with a blank short half", dict(QUESTION, text="   "))):
        assert_rejected("709.1", tmp_path, case, "raise 2", "short half",
                        plan=feature(lambda f: f.update(raises=[QUESTION, bad])))
    assert_rejected("709.1", tmp_path, "a reviewer's raise with no short half", "raise 2", "short half",
                    rev=review(lambda r: r.update(raises=[BLOCKER, without(BLOCKER, "text")])))


def test_a_raise_with_no_full_half_is_rejected_naming_it(record_property, tmp_path):
    """A raise with no full half is rejected, and the reason names the raise.

    Runs the planner's and the reviewer's real checks: a raise with both halves passes first. Then a second raise with
    its full half left out, empty, or a list instead of text is rejected with a reason naming raise 2 and its full
    half; the same holds for a reviewer's raise.

    Proves 709.2."""
    record_property("proves", "709.2")
    assert_good("709.2", tmp_path, plan=FEATURE, rev=REVIEW, case="raises with both halves")
    for case, bad in (("a raise with its full half left out", without(QUESTION, "full")),
                      ("a raise with an empty full half", dict(QUESTION, full="")),
                      ("a raise whose full half is a list", dict(QUESTION, full=["Job ids are strings."]))):
        assert_rejected("709.2", tmp_path, case, "raise 2", "full half",
                        plan=feature(lambda f: f.update(raises=[QUESTION, bad])))
    assert_rejected("709.2", tmp_path, "a reviewer's raise with no full half", "raise 2", "full half",
                    rev=review(lambda r: r.update(raises=[BLOCKER, without(BLOCKER, "full")])))


def test_a_split_story_with_no_short_half_is_rejected_naming_it(record_property, tmp_path):
    """A split story whose user story has no short half is rejected, naming the story.

    Runs the planner's real check: a split whose stories' user stories are short and full pairs passes first. Then
    story 2's user story with its short half left out, blank, or no user story at all is rejected with a reason
    naming story 2 and its short half.

    Proves 709.3."""
    record_property("proves", "709.3")
    assert_good("709.3", tmp_path, plan=FEATURE, case="a split whose user stories have both halves")
    full = "Each job's status shows on its issue."
    for case, change in (("a user story with its short half left out", lambda s: s.update(user_story={"full": full})),
                         ("a user story with a blank short half", lambda s: s.update(user_story=pair("  ", full))),
                         ("a story with no user story at all", lambda s: s.pop("user_story"))):
        assert_rejected("709.3", tmp_path, case, "story 2", "short half",
                        plan=feature(lambda f: change(f["stories"][1])))


def test_a_split_story_with_no_full_half_is_rejected_naming_it(record_property, tmp_path):
    """A split story whose user story has no full half is rejected, naming the story.

    Runs the planner's real check: a split whose user stories are short and full pairs passes first. Then story 2's
    user story with its full half left out, empty, or written as one plain sentence as before is rejected with a
    reason naming story 2 and its full half.

    Proves 709.4."""
    record_property("proves", "709.4")
    assert_good("709.4", tmp_path, plan=FEATURE, case="a split whose user stories have both halves")
    short = "Owners see each job's status."
    for case, change in (("a user story with its full half left out", lambda s: s.update(user_story={"short": short})),
                         ("a user story with an empty full half", lambda s: s.update(user_story=pair(short, ""))),
                         ("a user story written as one plain sentence", lambda s: s.update(user_story=short))):
        assert_rejected("709.4", tmp_path, case, "story 2", "full half",
                        plan=feature(lambda f: change(f["stories"][1])))


def test_a_split_storys_context_with_no_short_half_is_rejected_naming_it(record_property, tmp_path):
    """A split story whose context has no short half is rejected, naming the story.

    Runs the planner's real check: a split whose stories' contexts are short and full pairs passes first. Then story
    2's context with its short half left out or empty is rejected with a reason naming story 2, its context and the
    short half.

    Proves 709.5."""
    record_property("proves", "709.5")
    assert_good("709.5", tmp_path, plan=FEATURE, case="a split whose contexts have both halves")
    full = "The card draws each job's status from its record."
    for case, ctx in (("a context with its short half left out", {"full": full}),
                      ("a context with an empty short half", pair("", full))):
        assert_rejected("709.5", tmp_path, case, "story 2", "context", "short half",
                        plan=feature(lambda f: f["stories"][1].update(context=ctx)))


def test_a_split_storys_context_with_no_full_half_is_rejected_naming_it(record_property, tmp_path):
    """A split story whose context has no full half is rejected, naming the story.

    Runs the planner's real check: a split whose contexts are short and full pairs passes first. Then story 2's
    context with its full half left out, blank, or written as one plain sentence as before is rejected with a reason
    naming story 2, its context and the full half.

    Proves 709.6."""
    record_property("proves", "709.6")
    assert_good("709.6", tmp_path, plan=FEATURE, case="a split whose contexts have both halves")
    short = "Status shows on the card."
    for case, ctx in (("a context with its full half left out", {"short": short}),
                      ("a context with a blank full half", pair(short, "   ")),
                      ("a context written as one plain sentence", short)):
        assert_rejected("709.6", tmp_path, case, "story 2", "context", "full half",
                        plan=feature(lambda f: f["stories"][1].update(context=ctx)))


def test_a_short_half_that_names_code_is_rejected_naming_the_text(record_property, tmp_path):
    """A short half that names code is rejected, naming the text, whatever its kind.

    Runs the planner's and the reviewer's real checks: the good plan and review, all in plain words, pass first. Then
    code is put in one short half at a time: a question's, a reviewer's blocker's, an issue found's, story 2's user
    story's and story 2's context's. Each is rejected with a reason naming that text and saying it names code.

    Proves 709.7."""
    record_property("proves", "709.7")
    assert_good("709.7", tmp_path, plan=FEATURE, rev=REVIEW, case="short halves in plain words")
    assert_rejected("709.7", tmp_path, "a question that names code", "raise 1", "names code",
                    plan=feature(lambda f: f.update(raises=[dict(QUESTION, text=f"Should {CODE} return numbers?")])))
    assert_rejected("709.7", tmp_path, "a blocker that names code", "raise 1", "names code",
                    rev=review(lambda r: r.update(raises=[dict(BLOCKER, text=f"{CODE} fails."), ISSUE_FOUND])))
    assert_rejected("709.7", tmp_path, "an issue found that names code", "raise 2", "names code",
                    rev=review(lambda r: r.update(raises=[BLOCKER, dict(ISSUE_FOUND, text=f"{CODE} goes stale.")])))
    us = pair(f"Owners see {CODE}.", "Each job's status shows on its issue.")
    assert_rejected("709.7", tmp_path, "a story's user story that names code", "story 2", "names code",
                    plan=feature(lambda f: f["stories"][1].update(user_story=us)))
    ctx = pair(f"Status lives in {CODE}.", "The card draws each job's status from its record.")
    assert_rejected("709.7", tmp_path, "a story's context that names code", "story 2", "context", "names code",
                    plan=feature(lambda f: f["stories"][1].update(context=ctx)))


def test_a_full_half_that_names_code_passes_the_check(record_property, tmp_path):
    """A full half that names code passes the check.

    Runs the planner's and the reviewer's real checks on hand-backs whose short halves are plain words and whose full
    halves name files, functions and tests: a question's, a reviewer's blocker's, an issue found's, and story 2's user
    story's and context's. Each passes.

    Proves 709.8."""
    record_property("proves", "709.8")
    plan = feature(lambda f: (f.update(raises=[dict(QUESTION, full=f"The ids come from {CODE}.")]),
                              f["stories"][1].update(user_story=pair("Owners see each job's status.", f"Status is drawn by {CODE}."),
                                                     context=pair("Status shows on the card.", f"See {CODE}."))))
    assert_good("709.8", tmp_path, plan=plan, case="a plan whose full halves name code")
    rev = review(lambda r: r.update(raises=[dict(BLOCKER, full=f"{CODE} still fails on the branch."),
                                            dict(ISSUE_FOUND, full=f"{CODE} reads only open pull requests.")]))
    assert_good("709.8", tmp_path, rev=rev, case="a reviewer's blocker and issue whose full halves name code")


def test_a_full_half_longer_than_every_cap_passes_the_check(record_property, tmp_path):
    """A full half longer than every word cap passes the check.

    Runs the planner's and the reviewer's real checks on hand-backs whose full halves hold 300 words, more than any
    cap the owner set: a question's, a reviewer's blocker's and issue found's, and story 2's user story's and
    context's. Each passes.

    Proves 709.9."""
    record_property("proves", "709.9")
    plan = feature(lambda f: (f.update(raises=[dict(QUESTION, full=LONG)]),
                              f["stories"][1].update(user_story=pair("Owners see each job's status.", LONG),
                                                     context=pair("Status shows on the card.", LONG))))
    assert_good("709.9", tmp_path, plan=plan, case="a plan whose full halves hold 300 words")
    rev = review(lambda r: r.update(raises=[dict(BLOCKER, full=LONG), dict(ISSUE_FOUND, full=LONG)]))
    assert_good("709.9", tmp_path, rev=rev, case="a reviewer's blocker and issue whose full halves hold 300 words")


def prompt_examples():
    """Every example raise in the role prompts and raising rules, as (where, raise)."""
    found, dec = [], json.JSONDecoder()
    files = [os.path.join("dokima", "roles", f"{r}.md") for r in ("planner", "worker", "reviewer")]
    for path in files + [os.path.join("rules", "raising.md")]:
        text = open(os.path.join(ROOT, path)).read()
        for m in re.finditer(r'\{\s*"kind"\s*:\s*"(?:question|blocker|issue)"', text):
            obj, _ = dec.raw_decode(text, m.start())
            found.append((path, obj))
    return found


def test_every_example_raise_in_the_role_prompts_passes_the_two_halves_check(record_property, monkeypatch):
    """Every example raise agents learn from has a plain short half and a full half.

    Parses every example raise in the planner, worker and reviewer prompts and in the raising rules, and runs each
    through code's raise check and through the plain-words check. Each must carry a full half, code's raise check
    must accept it for some role, and no plain text in it may name code. Word caps are not judged here: one example's
    label is pinned by an older test.

    Proves 709.10."""
    record_property("proves", "709.10")
    monkeypatch.delenv("STYLE_SOFT", raising=False)
    found = prompt_examples()
    assert len(found) >= 9, f"709.10: found only {len(found)} example raises in the role prompts and the raising rules"
    for path, e in found:
        assert isinstance(e.get("full"), str) and e["full"].strip(), \
            f"709.10: an example raise in {path} has no full half: {e.get('label')!r}"
        accepted = [role for role in raises.TABLE if not raises.check_raises(role, [e])]
        assert accepted, f"709.10: code's raise check rejects the example {e.get('label')!r} in {path}: " \
                         f"{raises.check_raises('reviewer', [e])}"
        _, bad = words.style({"raises": [e]})
        code = [b for b in bad if "names code" in b]
        assert not code, f"709.10: the example {e.get('label')!r} in {path} names code in a plain text: {code}"


def test_the_planner_prompt_shows_a_split_storys_two_halves(record_property):
    """The planner prompt writes a split story's user story and context as two halves.

    Reads the planner prompt's hand-back shape for a feature and checks it writes each story's user story and context
    as a pair with a short and a full half, the shape the planner's check now needs.

    Proves 709.11."""
    record_property("proves", "709.11")
    text = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
    at = text.find("- A feature:")
    assert at >= 0, "709.11: the planner prompt has no hand-back shape for a feature"
    shape = re.sub(r"\s+", "", text[at:text.find("\n- ", at + 1) if text.find("\n- ", at + 1) > 0 else len(text)])
    for field in ("user_story", "context"):
        assert re.search(rf'"{field}":\{{"short":"[^"]*","full":', shape), \
            f"709.11: the planner prompt's split story shape does not write {field} as a short and full pair"

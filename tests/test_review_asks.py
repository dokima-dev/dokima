"""A plan review lists every ask of the owner, and real hand-backs are kept as samples that pass their checkers.

The planner writes the criteria from the owner's words, so it cannot check itself for an ask it dropped. The reviewer
reads the issue on its own and hands back an asks list in review.json: each ask in the owner's words, a link to where
they said it, and the plan's criterion it maps to, or "missing". Code rejects a plan review without that list, and a
plan review that marks an ask missing cannot approve.

Every check here runs the real commands the workflow runs on a review (`agent check review FILE PLAN N`, then
`agent check-round reviewer FILE PACK`) on a starting pack built in a temp folder, with STAGE set as the workflow's job
sets it: a plan review's pack, or a code review's pack, which also holds the PR's diff. A plan for issue 9 with criteria 9.1 to 9.3 stands in for the plan.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAMPLES = os.path.join(ROOT, "tests", "samples")

STORY = {"kind": "user_story", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://x/9"}, {"text": "b", "source": "https://x/9"}],
         "non_functional": [{"text": "c", "why": "w", "principle": "Fail closed"}],
         "scope": ["dokima/x.py"], "out_of_scope": [],
         "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_c"]}}
SPLIT = {"kind": "feature", "feature": "f", "stories": [
    {"title": "One", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://x/9"}],
     "non_functional": [], "depends_on": []},
    {"title": "Two", "user_story": "u2", "acceptance_criteria": [{"text": "b", "source": "https://x/9"}],
     "non_functional": [], "depends_on": [0]}]}

ASKS = [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"},
        {"ask": "Oil the hinges", "source": "https://github.com/o/r/issues/9#issuecomment-12", "criterion": "9.2"}]
APPROVE = {"previous_step": {"did": ["Wrote three criteria."], "decided": [], "open": []},
           "verdict": "approve", "summary": "Every ask has a criterion and a test.", "asks": ASKS, "tests": [{"test": t, "only_its_behavior": True, "why": "one result"} for t in ("tests/test_x.py::test_a", "tests/test_x.py::test_b", "tests/test_x.py::test_c")], "size": "ok", "behaviors": [{"criterion": c, "one_behavior": True, "why": "one result"} for c in ("9.1", "9.2", "9.3", "57.1", "57.2", "57.3", "S1.1", "S1.2", "S1.3", "S2.1", "S2.2", "S2.3")]}
BLOCK = {**APPROVE, "verdict": "block", "summary": "One ask has no criterion.",
         "raises": [{"kind": "blocker", "to": "planner", "label": "9.1", "text": "An ask is dropped.",
                     "evidence": "issue #9"}]}


def run(*args, stage=None):
    """Run Dokima's agent command from the repo root, the way the workflow does; return (exit code, stdout, stderr).

    Given a stage, the command sees it as the workflow's job does, in STAGE ('plan' or 'pr')."""
    env = {**os.environ, "PYTHONPATH": ROOT}
    env.pop("STAGE", None)
    if stage:
        env["STAGE"] = stage
    # A worker's or reviewer's run sets PLANNER_BASE, and the worker's check then reads the branch's docstrings (#240);
    # these hand-backs are judged on their own, whatever branch the tests run on.
    for k in ("PYTHONSAFEPATH", "PLANNER_BASE"):
        env.pop(k, None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout, p.stderr


def make_pack(where, plan, stage):
    """A reviewer's starting pack as the workflow builds it: a plan review's, or a code review's with the PR's diff."""
    pack = where / f"pack-{stage}"
    pack.mkdir(exist_ok=True)
    (pack / "in").mkdir(exist_ok=True)
    (pack / "issue.md").write_text("# Issue #9: Fix the door\n\nPaint the door blue.\n\n## Comments\n\nOil the hinges.\n")
    (pack / "plan.json").write_text(json.dumps(plan))
    (pack / "open_blockers.json").write_text("[]")
    if stage == "pr":
        (pack / "diff.patch").write_text("--- a/dokima/x.py\n+++ b/dokima/x.py\n@@ -1 +1 @@\n-a\n+b\n")
        (pack / "tests.txt").write_text("3 passed\n")
        (pack / "tests.xml").write_text("<testsuites/>\n")
        (pack / "worker-run").mkdir(exist_ok=True)
        (pack / "worker-run" / "s.jsonl").write_text("{}\n")
    return pack


def check_review(tmp_path, review, plan=STORY, stage="plan", number="9"):
    """Run the workflow's review check (`check review` and, if it passes, `check-round reviewer`) on one review.

    Returns (exit code, every printed reason, stderr), the exit code being 0 only when both commands pass."""
    pack = make_pack(tmp_path, plan, stage)
    out = tmp_path / f"out-{stage}"
    out.mkdir(exist_ok=True)
    f = out / "review.json"
    f.write_text(json.dumps(review))
    code, text, err = run("check", "review", str(f), str(pack / "plan.json"), number, stage=stage)
    if code == 0:
        code, more, err2 = run("check-round", "reviewer", str(f), str(pack), stage=stage)
        text, err = text + more, err + err2
    return code, text, err


def assert_passes(tmp_path, review, crit, why, **kw):
    """The review check passes the review with nothing printed; fails naming the criterion and the case."""
    code, out, err = check_review(tmp_path, review, **kw)
    assert "Traceback" not in err, f"{crit}: the review check crashed on {why}:\n{err[-600:]}"
    assert (code, out.strip()) == (0, ""), f"{crit}: {why} was rejected, but it is well formed: {out}{err[-400:]}"


def assert_rejected(tmp_path, review, pattern, crit, why, **kw):
    """The review check exits 1 with no crash, and one printed reason matches `pattern` (what it must name)."""
    code, out, err = check_review(tmp_path, review, **kw)
    assert "Traceback" not in err and "Traceback" not in out, f"{crit}: the review check crashed on {why}:\n{err[-600:]}"
    assert code == 1, f"{crit}: {why} was let through (exit {code}); it must be rejected"
    assert any(re.search(pattern, line) for line in out.splitlines()), \
        f"{crit}: {why} was rejected, but no reason names {pattern!r}; the reasons were:\n{out}"


def test_the_reviewer_prompt_asks_for_every_ask_in_the_owners_words(record_property):
    """The reviewer's prompt has it read the owner's issue and comments itself and hand back every ask, matched or missing.

    Reads dokima/roles/reviewer.md. Its review.json shape must carry an asks list whose items hold the ask, its source
    and its criterion, with "missing" as the value for an ask no criterion keeps. Its instructions must have one
    paragraph that tells the reviewer to list every ask from the owner's issue text and comments, in the owner's words
    with a link, each matched to one of the plan's criteria or marked missing."""
    record_property("proves", "158.1")
    prompt = open(os.path.join(ROOT, "dokima", "roles", "reviewer.md")).read()
    shape = prompt.partition("# What you hand back")[2]
    assert shape, "158.1: reviewer.md has no '# What you hand back' section with the review.json shape"
    assert re.search(r'"asks"\s*:\s*\[\s*\{\s*"ask"\s*:.*?"source"\s*:.*?"criterion"\s*:[^}\n]*"missing"', shape, re.S), \
        ('158.1: the review.json shape in reviewer.md has no asks list of {"ask": ..., "source": ..., '
         '"criterion": "N.k" | "missing"}')
    paragraphs = [p.lower() for p in re.split(r"\n\s*\n|\n(?=#)", prompt)]
    told = [p for p in paragraphs if "every ask" in p and "comment" in p and "owner" in p and "link" in p
            and "missing" in p and "criterion" in p]
    assert told, ("158.1: no paragraph of reviewer.md tells the reviewer to list every ask from the owner's issue text "
                  "and comments, in the owner's words with a link, each matched to a criterion or marked missing")


def test_a_plan_review_must_list_every_ask_well_formed(record_property, tmp_path):
    """A plan review with no asks list, an empty one, or an ask missing its words, link or match is rejected, naming it.

    First the good cases pass: a plan review whose asks are all matched to the plan's criteria, one with an ask marked
    missing that blocks, one on a split whose asks name its stories' criteria (S1.1, S2.1), and a code review with no
    asks list at all, since only a plan review must list them. Then each malformed list is rejected with a reason that
    names the missing field: no asks, an empty list, a list of bare strings, and an ask without (or with blank) ask,
    source or criterion. An ask matched to a criterion the plan does not have (9.7 on a plan with 9.1 to 9.3, 9.1 or
    S3.1 on a two-story split) is rejected with a reason naming the ask's words."""
    record_property("proves", "158.2")
    missing = {**ASKS[1], "criterion": "missing"}
    assert_passes(tmp_path, APPROVE, "158.2", "a plan review with every ask matched")
    assert_passes(tmp_path, {**BLOCK, "asks": [ASKS[0], missing]}, "158.2", "a blocking plan review with an ask marked missing")
    split_asks = [{**ASKS[0], "criterion": "S1.1"}, {**ASKS[1], "criterion": "S2.1"}]
    assert_passes(tmp_path, {**APPROVE, "asks": split_asks}, "158.2", "a plan review of a split naming S1.1 and S2.1", plan=SPLIT)
    no_asks = {k: v for k, v in APPROVE.items() if k != "asks"}
    assert_passes(tmp_path, no_asks, "158.2", "a code review with no asks list", stage="pr")

    assert_rejected(tmp_path, no_asks, r"\basks\b", "158.2", "a plan review with no asks list")
    assert_rejected(tmp_path, {**APPROVE, "asks": []}, r"\basks\b", "158.2", "a plan review with an empty asks list")
    assert_rejected(tmp_path, {**APPROVE, "asks": ["Paint the door blue"]}, r"\basks?\b", "158.2",
                    "a plan review whose asks are bare strings")
    for field in ("ask", "source", "criterion"):
        for value in (None, "", "  "):
            item = {k: v for k, v in ASKS[1].items() if k != field} if value is None else {**ASKS[1], field: value}
            why = f"a plan review with an ask {'without' if value is None else 'with a blank'} {field}"
            assert_rejected(tmp_path, {**APPROVE, "asks": [ASKS[0], item]}, rf"\b{field}\b", "158.2", why)

    unknown = {"ask": "Hang a bell", "source": "https://github.com/o/r/issues/9", "criterion": "9.7"}
    assert_rejected(tmp_path, {**APPROVE, "asks": [ASKS[0], unknown]}, "Hang a bell", "158.2",
                    "a plan review matching an ask to 9.7, which the plan does not have")
    for crit in ("9.1", "S3.1"):
        wrong = {**unknown, "criterion": crit}
        assert_rejected(tmp_path, {**APPROVE, "asks": [split_asks[0], wrong]}, "Hang a bell", "158.2",
                        f"a plan review of a two-story split matching an ask to {crit}", plan=SPLIT)


def test_a_plan_review_with_a_missing_ask_cannot_approve(record_property, tmp_path):
    """A plan review that marks any ask missing cannot approve, and the reason names each missing ask.

    An approve whose asks are all matched passes, and so does a block with an ask marked missing. An approve with one
    ask marked missing is rejected naming that ask's words; an approve with two asks marked missing is rejected naming
    both."""
    record_property("proves", "158.3")
    first, second = {**ASKS[0], "criterion": "missing"}, {**ASKS[1], "criterion": "missing"}
    assert_passes(tmp_path, APPROVE, "158.3", "an approve with every ask matched")
    assert_passes(tmp_path, {**BLOCK, "asks": [ASKS[0], second]}, "158.3", "a block with an ask marked missing")
    assert_rejected(tmp_path, {**APPROVE, "asks": [ASKS[0], second]}, "Oil the hinges", "158.3",
                    "an approve with the ask 'Oil the hinges' marked missing")
    code, out, err = check_review(tmp_path, {**APPROVE, "asks": [first, second]})
    assert code == 1, f"158.3: an approve with two asks marked missing was let through (exit {code}): {out}{err[-400:]}"
    for words in ("Paint the door blue", "Oil the hinges"):
        assert words in out, f"158.3: an approve with two asks marked missing was rejected, but no reason names {words!r}:\n{out}"


def load_json(path):
    """A JSON file's content, or a failure naming the sample that cannot be read."""
    try:
        return json.load(open(path))
    except (OSError, ValueError) as e:
        raise AssertionError(f"158.4: the sample {os.path.relpath(path, ROOT)} cannot be read as JSON: {e}")


def test_real_hand_backs_are_kept_as_samples_and_pass_their_checkers(record_property, tmp_path):
    """Real plan.json, work.json and review.json hand-backs are kept under tests/samples/, and each passes its checker.

    Each folder tests/samples/N/ holds one issue's hand-backs, copied from the bot's record comments (with the fields
    #300 retired turned into raises, a concern into a question for the owner, and empty or dropped ones left out): plan.json, and
    any of work.json, review-plan.json and review-pr.json, with sources.json giving, for every one of them, the link
    to the record comment on GitHub it was copied from. Across all folders there is at least one plan, one work and
    one review. Each plan passes the plan checker's reading of plan.json for issue N in dokima-dev/dokima; each work.json passes `agent check work` against its plan; each review passes the workflow's review
    check in the pack and STAGE of its stage, a plan review's or a code review's. The format is the settled one: each
    review sample, graded as a review of its plan with its asks list taken away, is rejected for the missing list."""
    record_property("proves", "158.4")
    folders = sorted(d for d in os.listdir(SAMPLES) if os.path.isdir(os.path.join(SAMPLES, d))) if os.path.isdir(SAMPLES) else []
    assert folders, "158.4: tests/samples/ holds no samples: keep real hand-backs there, one folder per issue"
    kinds = set()
    link = re.compile(r"https://github\.com/dokima-dev/dokima/(issues|pull)/\d+#issuecomment-\d+")
    for n in folders:
        where = os.path.join(SAMPLES, n)
        assert n.isdigit(), f"158.4: tests/samples/{n} is not named after an issue number"
        files = sorted(f for f in os.listdir(where) if f != "sources.json")
        extra = [f for f in files if f not in ("plan.json", "work.json", "review-plan.json", "review-pr.json")]
        assert not extra, f"158.4: tests/samples/{n} holds {extra}; a sample is plan.json, work.json, review-plan.json or review-pr.json"
        assert "plan.json" in files, f"158.4: tests/samples/{n} has no plan.json to check its other hand-backs against"
        sources = load_json(os.path.join(where, "sources.json")) if os.path.exists(os.path.join(where, "sources.json")) else {}
        for f in files:
            assert isinstance(sources, dict) and isinstance(sources.get(f), str) and link.fullmatch(sources[f].strip()), \
                f"158.4: tests/samples/{n}/sources.json gives no link to the record comment {f} was copied from"

        plan = load_json(os.path.join(where, "plan.json"))
        code = ("import sys\nfrom dokima.planner import read_output, Garbled\n"
                "try:\n    read_output(sys.argv[1], sys.argv[2])\nexcept Garbled as e:\n    print(e); sys.exit(1)\n")
        env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "dokima-dev/dokima", "GITHUB_SERVER_URL": "https://github.com"}
        env.pop("PYTHONSAFEPATH", None)
        p = subprocess.run([sys.executable, "-c", code, where, n], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
        assert p.returncode == 0, f"158.4: the sample tests/samples/{n}/plan.json fails the plan checker: {p.stdout}{p.stderr[-400:]}"
        kinds.add("plan")
        if "work.json" in files:
            code, out, err = run("check", "work", os.path.join(where, "work.json"), os.path.join(where, "plan.json"), n)
            assert (code, out.strip()) == (0, ""), f"158.4: the sample tests/samples/{n}/work.json fails its checker: {out}{err[-400:]}"
            kinds.add("work")
        for stage in ("plan", "pr"):
            if f"review-{stage}.json" in files:
                review = load_json(os.path.join(where, f"review-{stage}.json"))
                code, out, err = check_review(tmp_path, review, plan=plan, stage=stage, number=n)
                assert (code, out.strip()) == (0, ""), \
                    f"158.4: the sample tests/samples/{n}/review-{stage}.json fails its checker: {out}{err[-400:]}"
                kinds.add("review")
                # The samples are graded in the settled format: the same review, graded as a review of this plan with
                # no asks list, is turned away for it, so a sample recorded before asks existed cannot pass as a plan review.
                bare = {k: v for k, v in review.items() if k != "asks"}
                code, out, err = check_review(tmp_path, bare, plan=plan, stage="plan", number=n)
                assert code != 0 and "asks" in out, \
                    f"158.4: tests/samples/{n}/review-{stage}.json graded as a plan review with no asks list passes; " \
                    f"the samples are not checked in the settled format: {out}{err[-400:]}"
    lacking = sorted({"plan", "work", "review"} - kinds)
    assert not lacking, f"158.4: tests/samples/ keeps no real {', '.join(lacking)} hand-back; it needs a plan, a work and a review"

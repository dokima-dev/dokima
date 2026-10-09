"""A code review's blocker says who fixes it, and the river sends it there: tests to the planner, code to the worker.

Found on issue 154 and PR 165: a code reviewer found a planner's test too weak, the river sent the block to the worker,
who may not touch tests, and three rounds later it reached the owner. Each test here drives Dokima's own code the way
the workflow does (the hand-back check from outside, the river's next_step, the starting pack with GitHub faked) and
names its criterion on every failure. A plan for issue 9 with criteria 9.1 to 9.3 stands in for the approved plan.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORY = {"kind": "user_story", "user_story": "u",
         "acceptance_criteria": [{"text": "a", "source": "https://x/9"}, {"text": "b", "source": "https://x/9"},
                                 {"text": "c", "source": "https://x/9"}],
         "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
         "tests": {"9.1": ["tests/test_x.py::test_a"], "9.2": ["tests/test_x.py::test_b"], "9.3": ["tests/test_x.py::test_c"]}}


def blocker(id_, fixer, criterion="9.1"):
    """One well-formed blocker; fixer None leaves the field out."""
    b = {"id": id_, "criterion": criterion, "test": None, "problem": f"problem {id_}", "evidence": "e", "fix": "f"}
    if fixer is not None:
        b["fixer"] = fixer
    return b


def review(*blockers, verdict="block"):
    """A well-formed review.json holding these blockers, listing the owner's one ask matched to 9.1.

    A plan review must list every ask and a code review may, so the sample passes code's check on any stage (#244)."""
    return {"previous_step": {"did": ["Built it."], "decided": [], "open": []}, "verdict": verdict,
            "summary": "s", "blockers": list(blockers), "notes": [], "outside_plan": [], "resolved": [],
            "asks": [{"ask": "Paint the door blue", "source": "https://github.com/o/r/issues/9", "criterion": "9.1"}]}


def rec(role, stage="", handback=None):
    """A passed record built the way the workflow builds one, from a temp hand-back folder."""
    out = tempfile.mkdtemp()
    json.dump(handback or {}, open(os.path.join(out, agent.HANDBACK[role]), "w"))
    return agent.build_record(role, stage, out, "", True, {"run_id": "1", "run": "https://x/run/1"})


def comment(r, who="dokima-runtime"):
    """A comment as GitHub returns it, carrying a record rendered by code."""
    return {"author": {"login": who}, "body": agent.render(r), "createdAt": "2026-10-07T10:00:00Z", "where": "issue #9"}


OWNER_WORK = {"author": {"login": "owner"}, "body": "/work", "createdAt": "2026-10-07T09:00:00Z", "where": "issue #9"}
OWNER_PLAN = {"author": {"login": "owner"}, "body": "/plan make the test stronger", "createdAt": "2026-10-07T11:00:00Z", "where": "issue #9"}
PLAN = rec("planner", handback=STORY)
PLAN_OK = rec("reviewer", "plan", review(verdict="approve"))


def check_review(tmp_path, handback):
    """Run `python3 -m dokima.agent check review FILE PLAN 9` from the repo root; return (exit code, stdout, stderr)."""
    f, p = tmp_path / "review.json", tmp_path / "plan.json"
    f.write_text(json.dumps(handback))
    p.write_text(json.dumps(STORY))
    env = {**os.environ, "PYTHONPATH": ROOT}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "check", "review", str(f), str(p), "9"],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout, r.stderr


def test_every_review_blocker_names_the_worker_or_the_planner(record_property, tmp_path, monkeypatch):
    """A review passes its check only when every blocker says who fixes it, the worker or the planner.

    Runs the real hand-back check: a blocker for the worker, one for the planner, and both together pass, on every
    stage a machine may run on (STAGE unset, plan or pr), since the sample review lists the owner's asks (#244). A
    blocker with no fixer, an empty one, one naming the reviewer or the owner, and a number are each rejected with
    exit 1, a reason naming the blocker's id and the fixer field, and no crash, also when the other blocker is well formed."""
    record_property("proves", "166.1")
    record_property("proves", "244.1")
    for stage in ("", "plan", "pr"):
        if stage:
            monkeypatch.setenv("STAGE", stage)
        else:
            monkeypatch.delenv("STAGE", raising=False)
        for case in (review(blocker("B1", "worker")), review(blocker("B1", "planner")),
                     review(blocker("B1", "worker"), blocker("B2", "planner"))):
            code, out, err = check_review(tmp_path, case)
            assert (code, out.strip()) == (0, ""), \
                f"166.1, 244.1: a review whose blockers name their fixer was rejected with STAGE={stage or 'unset'}: {out}{err[-400:]}"
    monkeypatch.delenv("STAGE", raising=False)
    for bad in (None, "", "reviewer", "owner", 5):
        code, out, err = check_review(tmp_path, review(blocker("B1", "worker"), blocker("B2", bad)))
        assert "Traceback" not in err + out, f"166.1: the check crashed on fixer {bad!r}:\n{err[-600:]}"
        assert code == 1, f"166.1: a blocker with fixer {bad!r} passed the check; it must name the worker or the planner"
        assert any("B2" in line and "fixer" in line for line in out.splitlines()), \
            f"166.1: no reason names blocker B2 and its fixer for fixer {bad!r}; reasons were:\n{out}"
        assert not any("B1" in line for line in out.splitlines()), f"166.1: the well-formed blocker B1 was named too:\n{out}"


def test_a_code_review_block_goes_to_whoever_fixes_it(record_property):
    """A blocking code review with any blocker for the planner starts the planner; one with only worker blockers starts the worker.

    Asks the river what follows a blocking code review: a weak-test blocker alone, and a weak-test blocker beside a code
    blocker, each start the planner; code blockers alone, one or two, start the worker. A blocking plan review still
    starts the planner."""
    record_property("proves", "166.2")
    items = [OWNER_WORK, comment(PLAN), comment(PLAN_OK), comment(rec("worker", handback={"summary": "s"}))]
    for blockers in ([blocker("B1", "planner")], [blocker("B1", "worker"), blocker("B2", "planner", "9.2")]):
        step = agent.next_step(items, rec("reviewer", "pr", review(*blockers)), ["owner"])
        assert step == ("start", "planner", ""), f"166.2: a code review with a test blocker started {step}, not the planner"
    for blockers in ([blocker("B1", "worker")], [blocker("B1", "worker"), blocker("B2", "worker", "9.2")]):
        step = agent.next_step(items, rec("reviewer", "pr", review(*blockers)), ["owner"])
        assert step == ("start", "worker", ""), f"166.2: a code review with only code blockers started {step}, not the worker"
    step = agent.next_step(items[:2], rec("reviewer", "plan", review(blocker("B1", "planner"))), ["owner"])
    assert step == ("start", "planner", ""), f"166.2: a blocking plan review started {step}, not the planner"


def fake_github(monkeypatch, recs):
    """Fake GitHub so the issue's conversation holds the owner's /work and then these records, all posted by the bot."""
    comments = [OWNER_WORK] + [comment(r) for r in recs]
    def gh(*args):
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": 9, "title": "T", "body": "B", "comments": comments})
        if args[:2] == ("pr", "list"):
            return "[]"
        if args[:2] == ("issue", "list") or (args[0] == "api" and args[1].lstrip("/").startswith("repos/o/r/issues")
                                             and "/comments" not in args[1]):
            return "[]"  # the repo's open issues, which the planner's pack lists
        raise AssertionError(f"unexpected gh call {args}")
    monkeypatch.setattr(agent, "gh", gh)


def test_the_planner_answers_the_test_blockers_and_the_worker_the_code_ones(record_property, tmp_path, monkeypatch):
    """The planner sent by a code review gets its test blockers to answer by id; the worker after it gets only the code blockers.

    Builds the starting packs from a faked issue whose code review blocked with B1 for the planner and B2 for the
    worker. The planner's open_blockers.json holds exactly B1. After the planner re-plans and the plan review approves,
    the worker's open_blockers.json holds exactly B2. The planner's round check then rejects a hand-back that skips B1."""
    record_property("proves", "166.3")
    pr_block = rec("reviewer", "pr", review(blocker("B1", "planner"), blocker("B2", "worker", "9.2")))
    base = [PLAN, PLAN_OK, rec("worker", handback={"summary": "s"}), pr_block]
    fake_github(monkeypatch, base)
    agent.pack("o/r", 9, "planner", "", str(tmp_path / "p"))
    got = [b.get("id") for b in json.load(open(tmp_path / "p" / "open_blockers.json"))]
    assert got == ["B1"], f"166.3: the planner was handed blockers {got}, not exactly the test blocker B1"
    assert agent.problems_round("planner", {"replies": [], "links": {"blocked_by": [], "blocks": [], "relates_to": []}}, str(tmp_path / "p")) == ["blocker B1 is not answered"], \
        "166.3: the planner's hand-back may skip the code review's test blocker B1"
    fake_github(monkeypatch, base + [rec("planner", handback=STORY), PLAN_OK])
    agent.pack("o/r", 9, "worker", "", str(tmp_path / "w"))
    got = [b.get("id") for b in json.load(open(tmp_path / "w" / "open_blockers.json"))]
    assert got == ["B2"], f"166.3: the worker was handed blockers {got}, not exactly the code blocker B2"


def with_criteria(criteria, non_functional=()):
    """STORY with these criterion texts and stronger tests, as a re-plan that a code review asked for would hand back."""
    return {**STORY, "acceptance_criteria": [{"text": t, "source": "https://x/9"} for t in criteria],
            "non_functional": [{"text": t, "why": "w", "principle": "p"} for t in non_functional],
            "tests": {f"9.{k}": [f"tests/test_x.py::test_stronger_{k}"] for k in range(1, len(criteria) + len(non_functional) + 1)}}


def test_an_approved_test_fix_goes_straight_back_to_the_worker(record_property):
    """An approved re-plan that only strengthens tests goes straight to the worker; one that changes any criterion waits for /work.

    The river after a plan approval, when the owner approved a plan with /work, the worker built it and a code review
    sent a weak test to the planner: a re-plan with the same criteria and stronger tests starts the worker. A re-plan
    that rewrites a criterion, adds one, drops one or adds a non-functional requirement stops and asks the owner for
    /work. So do a first plan, a re-plan after a code review whose blockers were all for the worker, and a re-plan after
    the owner spoke since the code review."""
    record_property("proves", "166.4")
    work = rec("worker", handback={"summary": "s"})
    test_block = rec("reviewer", "pr", review(blocker("B1", "planner")))
    code_block = rec("reviewer", "pr", review(blocker("B1", "worker")))
    same = rec("planner", handback=with_criteria(["a", "b", "c"]))
    built = [comment(PLAN), comment(PLAN_OK), OWNER_WORK, comment(work)]
    step = agent.next_step(built + [comment(test_block), comment(same)], PLAN_OK, ["owner"])
    assert step == ("start", "worker", ""), \
        f"166.4: an approved test fix with unchanged criteria, asked for by a code review, gave {step}, not the worker"
    changed = {"a criterion rewritten": with_criteria(["a", "b, but more", "c"]),
               "a criterion added": with_criteria(["a", "b", "c", "d"]),
               "a criterion dropped": with_criteria(["a", "b"]),
               "a non-functional requirement added": with_criteria(["a", "b", "c"], ["n"])}
    for name, plan in changed.items():
        step = agent.next_step(built + [comment(test_block), comment(rec("planner", handback=plan))], PLAN_OK, ["owner"])
        assert step[0] == "stop" and "/work" in step[1], \
            f"166.4: a re-plan with {name} went on without the owner's /work: {step}"
    others = {"a first plan": [comment(PLAN)],
              "a code-only block": built + [comment(code_block), comment(same)],
              "the owner's own /plan": built + [comment(test_block), OWNER_PLAN, comment(same)]}
    for name, items in others.items():
        step = agent.next_step(items, PLAN_OK, ["owner"])
        assert step[0] == "stop" and "/work" in step[1], f"166.4: after {name} a plan approval gave {step}, not a stop asking for /work"


def test_the_reviewer_is_told_to_name_who_fixes_each_blocker(record_property):
    """The reviewer's instructions show the fixer on every blocker and say tests go to the planner, code to the worker.

    Reads the reviewer prompt code hands to every review: its hand-back shape gives each blocker a fixer of worker or
    planner, and the result grade's weak-test rule tells the reviewer to name the planner as the fixer."""
    record_property("proves", "166.5")
    roles = os.path.join(ROOT, "dokima", "roles")
    prompt = open(os.path.join(roles, "reviewer.md")).read()
    assert '"fixer": "worker" | "planner"' in prompt, "166.5: the reviewer's hand-back shape gives blockers no fixer of worker or planner"
    grade = open(os.path.join(roles, "result-grade.md")).read()
    weak = [p for p in grade.split("\n7.")[1:]]
    assert weak and '"fixer": "planner"' in weak[0].split("\nNotes")[0], \
        "166.5: the result grade's weak-test rule does not tell the reviewer to set the fixer to the planner"


def test_three_blocks_on_the_test_fix_route_still_stop_for_the_owner(record_property):
    """On the new route, the third blocking code review in a row stops the river and asks the owner.

    Walks the route after the owner's /work: a code review blocks a weak test, the river starts the planner, the plan
    review approves the re-plan and the river starts the worker, who builds, and the code review blocks again. The first
    and second blocks each go on to the planner, and each approved re-plan straight to the worker; the third block stops
    and names three blocking reviews, whether it is for the planner or only for the worker. A one-off check that the
    owner's own words since the blocks start the count again, so the third block then goes on to the planner."""
    record_property("proves", "166.6")
    work = rec("worker", handback={"summary": "s"})
    same = rec("planner", handback=with_criteria(["a", "b", "c"]))
    items = [comment(PLAN), comment(PLAN_OK), OWNER_WORK, comment(work)]
    for n in (1, 2):
        block = rec("reviewer", "pr", review(blocker("B1", "planner")))
        step = agent.next_step(items, block, ["owner"])
        assert step == ("start", "planner", ""), f"166.6: code review block {n} with a test blocker gave {step}, not the planner"
        items += [comment(block), comment(same)]
        step = agent.next_step(items, PLAN_OK, ["owner"])
        assert step == ("start", "worker", ""), f"166.6: the approved re-plan after block {n} gave {step}, not the worker"
        items += [comment(PLAN_OK), comment(work)]
    for name, third in {"a test blocker": review(blocker("B1", "planner")),
                        "only a code blocker": review(blocker("B1", "worker"))}.items():
        step = agent.next_step(items, rec("reviewer", "pr", third), ["owner"])
        assert step[0] == "stop" and "3 blocking reviews" in step[1], \
            f"166.6: the third blocking code review in a row, with {name}, gave {step}, not a stop for the owner"
    spoke = items + [{**OWNER_PLAN, "body": "keep going"}]
    step = agent.next_step(spoke, rec("reviewer", "pr", review(blocker("B1", "planner"))), ["owner"])
    assert step == ("start", "planner", ""), \
        f"166.6: after the owner spoke, a code review block gave {step}; the count must start again and go to the planner"

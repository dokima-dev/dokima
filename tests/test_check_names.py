"""The pull request checks are named All tests and Acceptance criteria, with no done-whens (#291).

Story 1 of #262. The check that runs every test, and its workflow, are named All tests; the check that passes only when
every criterion's check passed, and its workflow, are named Acceptance criteria; each criterion keeps its own check
named "N.k · <words>". The card and the board start through `workflow_run` by workflow name, so the tests read those
names out of card.yml and board.yml and match them against the workflows the repo really has. The card is drawn with
the new and the old check names, and autopilot's merge is played through the fake GitHub of test_automerge.py with
heads that lack either check. One test reads every file in the repo for the old word; the exceptions are the owner's
older "Done when:" plan lines Dokima still reads, copies of past records in tests/samples, and the one AGENTS.md
sentence naming the old check, so the owner knows which branch rule entry to switch.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card, checks  # noqa: E402

import test_automerge as tam  # noqa: E402
import test_card_records as tcr  # noqa: E402
import test_start as ts  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
ALL_TESTS, CRITERIA = "All tests", "Acceptance criteria"
OLD_WORD = re.compile(r"done[\s_-]*whens?", re.I)


def workflows():
    """Every workflow file of the repo, as {file name: parsed workflow}."""
    out = {}
    for name in sorted(os.listdir(WORKFLOWS)):
        if name.endswith((".yml", ".yaml")):
            out[name] = ts.load_yaml(open(os.path.join(WORKFLOWS, name)).read())
    return out


def named(name, k):
    """The one workflow named `name`, as (file name, parsed workflow); fails naming criterion k otherwise."""
    found = [(f, w) for f, w in workflows().items() if w.get("name") == name]
    assert len(found) == 1, (f"{k}: expected one workflow named {name!r}, found {[f for f, _ in found]}; the workflows "
                             f"are named {[w.get('name') for w in workflows().values()]}")
    return found[0]


def job_names(flow):
    """The names GitHub shows for a workflow's jobs, in file order."""
    return [j.get("name") for j in (flow.get("jobs") or {}).values() if isinstance(j, dict)]


def started_by(file_name):
    """The workflow names whose finishing starts the workflow in `file_name` (its workflow_run trigger)."""
    on = workflows()[file_name].get("on") or {}
    listed = (on.get("workflow_run") or {}).get("workflows") or []
    return [listed] if isinstance(listed, str) else list(listed)


def plan_of(recs):
    """The newest plan's hand-back in the records."""
    return agent.latest(recs, "planner")["handback"]


# 291.1: the check that runs every test, and its workflow, are named All tests; the card still shows and redraws on it

def test_the_check_running_every_test_and_its_workflow_are_named_all_tests(record_property):
    """The workflow running every test, and its one check, are named All tests.

    Proves 291.1. Finds the workflow named All tests among the repo's workflows, checks it runs pytest on the whole tests folder on
    every pull request, that its one job is named All tests, and that no workflow or job is still named all tests or
    full suite."""
    record_property("proves", "291.1")
    name, flow = named(ALL_TESTS, "291.1")
    assert job_names(flow) == [ALL_TESTS], f"291.1: the jobs of {name} are named {job_names(flow)}, not [{ALL_TESTS!r}]"
    text = open(os.path.join(WORKFLOWS, name)).read()
    assert "pull_request_target:" in text and re.search(r"(?m)^\s*- run: pytest .* tests$", text), \
        f"291.1: the workflow named All tests ({name}) no longer runs every test on every pull request"
    for f, w in workflows().items():
        for n in [w.get("name")] + job_names(w):
            assert n not in ("all tests", "full suite"), f"291.1: {f} still names a workflow or check {n!r}"


def test_the_card_shows_the_all_tests_verdict_in_its_definition_of_done_row(record_property):
    """The Definition of Done row shows the All tests verdict; the old name counts for nothing.

    Proves 291.1. Draws the card with a check named All tests passed, then failed: the row's first circle says passed, then failed.
    Then the same check under the old name all tests: the row says not started, and the card does not count the checks
    as passed."""
    record_property("proves", "291.1")
    rest = [r for r in tcr.GREEN if r["name"].split(" · ")[0] != r["name"]]
    for conclusion, want in (("success", "passed"), ("failure", "failed")):
        runs = rest + [tcr.run(ALL_TESTS, conclusion=conclusion, n=4)]
        row = tcr.dod(tcr.draw(check_runs=runs), "291.1")
        assert tcr.alts(row)[:1] == [want], f"291.1: a check named All tests that ended {conclusion} shows {tcr.alts(row)[:1]}"
        assert card.checks_passed(40, plan_of(tcr.RECS), runs) is (conclusion == "success"), \
            f"291.1: the card does not read the All tests check that ended {conclusion}"
    old = rest + [tcr.run("all tests", n=4)]
    row = tcr.dod(tcr.draw(check_runs=old), "291.1")
    assert tcr.alts(row)[:1] == ["not started"], f"291.1: a check under the old name all tests still shows {tcr.alts(row)[:1]}"
    assert card.checks_passed(40, plan_of(tcr.RECS), old) is False, \
        "291.1: the card counts a check under the old name all tests as All tests"


def test_the_card_redraws_when_the_all_tests_workflow_finishes(record_property):
    """The card redraws when All tests finishes, and waits on no workflow that is missing.

    Proves 291.1. Reads the names in card.yml's workflow_run trigger: All tests must be one of them, and each must be the name of a
    workflow in the repo, since GitHub silently never starts on a name no workflow has."""
    record_property("proves", "291.1")
    listed, have = started_by("card.yml"), [w.get("name") for w in workflows().values()]
    assert ALL_TESTS in listed, f"291.1: the card does not redraw when All tests finishes; it waits on {listed}"
    for n in listed:
        assert n in have, f"291.1: card.yml waits on a workflow named {n!r}, and no workflow has that name: {have}"


# 291.2: the gate check and its workflow are named Acceptance criteria; each criterion keeps its own check

def test_the_criteria_workflow_and_its_gate_check_are_named_acceptance_criteria(record_property):
    """The criteria workflow and its gate are named Acceptance criteria; each criterion keeps its check.

    Proves 291.2. Finds the workflow named Acceptance criteria, checks it runs on pull_request_target, that its gate job is named
    Acceptance criteria, waits on the per-criterion checks and passes only when they all succeeded, and that each
    criterion's check is still named by its number and words. The old file done-whens.yml and the old gate name are gone."""
    record_property("proves", "291.2")
    name, flow = named(CRITERIA, "291.2")
    jobs = {k: j for k, j in (flow.get("jobs") or {}).items() if isinstance(j, dict)}
    gates = [k for k, j in jobs.items() if j.get("name") == CRITERIA]
    assert len(gates) == 1, f"291.2: {name} has no single job named Acceptance criteria: {job_names(flow)}"
    per = [k for k, j in jobs.items() if j.get("name") == "${{ matrix.name }}"]
    assert len(per) == 1, f"291.2: {name} no longer gives each criterion its own check named from the plan: {job_names(flow)}"
    needs = jobs[gates[0]].get("needs") or []
    assert per[0] in ([needs] if isinstance(needs, str) else needs), \
        f"291.2: the Acceptance criteria check does not wait on each criterion's check (needs: {needs})"
    text = open(os.path.join(WORKFLOWS, name)).read()
    assert "pull_request_target:" in text and 'test "$RESULT" = "success"' in text, \
        f"291.2: the Acceptance criteria check ({name}) no longer passes only when every criterion's check passed"
    assert not os.path.exists(os.path.join(WORKFLOWS, "done-whens.yml")), "291.2: .github/workflows/done-whens.yml is still there"
    for f, w in workflows().items():
        assert "all done-whens passed" not in job_names(w), f"291.2: {f} still has a check named all done-whens passed"
    rows = checks.build_matrix(40, tcr.RECS)
    assert [r["name"] for r in rows] == ["40.1 · First thing works", "40.2 · Second thing works", "40.3 · Nothing leaks out"], \
        f"291.2: each criterion's check is no longer named by its number and words: {[r['name'] for r in rows]}"


def test_the_card_and_the_board_update_when_the_acceptance_criteria_checks_finish(record_property):
    """The card and board update when Acceptance criteria finishes, and wait on nothing missing.

    Proves 291.2. Reads the workflow_run trigger of card.yml and of board.yml: each must list Acceptance criteria, and every name they
    list must be a workflow the repo has, so a rename never silently stops either one."""
    record_property("proves", "291.2")
    have = [w.get("name") for w in workflows().values()]
    for f in ("card.yml", "board.yml"):
        listed = started_by(f)
        assert CRITERIA in listed, f"291.2: {f} does not start when Acceptance criteria finishes; it waits on {listed}"
        for n in listed:
            assert n in have, f"291.2: {f} waits on a workflow named {n!r}, and no workflow has that name: {have}"


# 291.3: no text a person reads says done-when, outside the named exceptions

def repo_files():
    """Every file of the repo on this machine, tracked or new, by its path."""
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True,
                         check=True).stdout.splitlines()
    return sorted(p for p in set(out) if os.path.isfile(os.path.join(ROOT, p)))


def allowed(path, line, match):
    """Whether this one use of the old word is one of the exceptions.

    In the tests, the owner's older plan lines ("Done when: ...") that Dokima still reads, and a check that the word is
    gone ("done when" not in ...). In AGENTS.md, only the old check's name, all done-whens passed (its one sentence is
    checked by 291.4)."""
    word, after = match.group(0), line[match.end():]
    if path.startswith("tests/") and path.endswith(".py"):
        if word == "Done when" and after.startswith(":"):
            return True
        if line[match.start() - 1:match.start()] == '"' and re.match(r'"\s+not in\b', after):
            return True
    if path == "AGENTS.md":
        return line[max(0, match.start() - 4):match.end() + 7] == "all done-whens passed"
    return False


def scan_self_check():
    """Fail unless the scan flags the old word and lets only the named exceptions through.

    Feeds the scan's rule lines it must flag (a workflow step, a docstring, a test name, a README line, AGENTS.md
    naming it otherwise) and lines it must pass (a test's Done when: plan line, a "not in" check, and AGENTS.md's
    all done-whens passed), so a scan that flags nothing or everything fails here."""
    flag = [(".github/workflows/x.yml", "      - name: Run this done-when's tests"),
            ("dokima/checks.py", '    """One annotation per done_when."""'),
            ("tests/test_x.py", "def test_long_done_whens_get_short_check_names(record_property):"),
            ("tests/test_x.py", '    """Reads the issue in the old done-when format."""'),
            ("README.md", "Every Done when is checked."),
            ("AGENTS.md", "Each done-when has its check.")]
    keep = [("tests/test_x.py", '    "  - [ ] Done when: first thing works\\n"'),
            ("tests/test_x.py", '    assert "done when" not in text.lower()'),
            ("AGENTS.md", "When it merges, the rule must switch from all tests and all done-whens passed to All tests.")]
    for path, line in flag:
        assert not all(allowed(path, line, m) for m in OLD_WORD.finditer(line)), f"291.3: the scan lets through {path}: {line}"
    for path, line in keep:
        assert all(allowed(path, line, m) for m in OLD_WORD.finditer(line)), f"291.3: the scan flags an exception in {path}: {line}"


def test_no_text_a_person_reads_says_done_when(record_property):
    """No file a person reads says done-when, outside the named exceptions.

    Proves 291.3. Reads every file in the repo, its path and every line, for done-when, done-whens, done when and done_when in any
    case. Skipped: dokima/plan.py, which still reads an owner's older Done when: lines, copies of past records in
    tests/samples, and this test. Allowed: the tests' Done when: plan lines and their "not in" checks, and in AGENTS.md
    exactly one mention of the old check all done-whens passed. Each leftover is listed with its file and line. The
    scan's rule is first tried on lines it must flag and lines it must pass, so a scan that flags nothing proves nothing."""
    record_property("proves", "291.3")
    scan_self_check()
    skip = {"dokima/plan.py", "tests/test_check_names.py"}
    left, agents_mentions = [], 0
    for path in repo_files():
        if path in skip or path.startswith("tests/samples/"):
            continue
        if OLD_WORD.search(path):
            left.append(f"{path}: the file's name")
        try:
            text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in OLD_WORD.finditer(line):
                if allowed(path, line, m):
                    agents_mentions += path == "AGENTS.md"
                else:
                    left.append(f"{path} line {i}: {line.strip()[:120]}")
    assert not left, "291.3: the old word done-when is still where a person reads it:\n" + "\n".join(left)
    assert agents_mentions <= 1, f"291.3: AGENTS.md names the old check all done-whens passed {agents_mentions} times, not once"


# 291.4: AGENTS.md lists the checks in Definition of Done order and says how the branch rule switches

def agents_md():
    """AGENTS.md's text, as one line per paragraph and one item per sentence."""
    text = open(os.path.join(ROOT, "AGENTS.md")).read()
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n|\n(?=\s*[-*] )", text)]
    sentences = [s for p in paragraphs for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`*])", p)]
    return paragraphs, sentences


def test_agents_md_lists_the_checks_in_definition_of_done_order(record_property):
    """AGENTS.md lists the pull request checks in Definition of Done order.

    Proves 291.4. Finds the AGENTS.md paragraph that names All tests, Acceptance criteria, Acceptance test, Code review and Owner
    approval, and checks they come in that order, with Acceptance test explained as the End-to-end test on a feature
    that #233 adds."""
    record_property("proves", "291.4")
    order = [ALL_TESTS, CRITERIA, "Acceptance test", "Code review", "Owner approval"]
    paragraphs, _ = agents_md()
    found = [p for p in paragraphs if all(n in p for n in order)]
    assert found, f"291.4: no paragraph of AGENTS.md lists the checks {order}"
    p = found[0]
    at = [p.index(n) for n in order]
    assert at == sorted(at), f"291.4: AGENTS.md lists the checks out of Definition of Done order: {p}"
    assert "End-to-end test on a feature" in p and "#233" in p, \
        f"291.4: AGENTS.md does not say Acceptance test is the End-to-end test on a feature that #233 adds: {p}"


def test_agents_md_names_the_required_checks_and_the_branch_rule_switch(record_property):
    """AGENTS.md names the checks the branch rule requires, and says plainly how it switches.

    Proves 291.4. Finds a sentence naming main's branch rule that requires All tests and Acceptance criteria, and exactly one
    sentence that names the old checks all tests and all done-whens passed and says the rule switches to All tests and
    Acceptance criteria when the rename merges."""
    record_property("proves", "291.4")
    _, sentences = agents_md()
    rule = [s for s in sentences if "branch rule" in s and "require" in s and ALL_TESTS in s and CRITERIA in s
            and "main" in s]
    assert rule, "291.4: AGENTS.md does not name All tests and Acceptance criteria as the checks main's branch rule requires"
    switch = [s for s in sentences if "all done-whens passed" in s]
    assert len(switch) == 1, f"291.4: AGENTS.md has {len(switch)} sentences naming the old check all done-whens passed, not one"
    s = switch[0]
    assert "switch" in s and "all tests" in s and ALL_TESTS in s and CRITERIA in s and "merge" in s, \
        f"291.4: AGENTS.md's sentence does not say the rule switches from all tests and all done-whens passed to All tests and Acceptance criteria when the rename merges: {s}"
    assert s.index("all done-whens passed") < s.index(CRITERIA), f"291.4: the sentence does not switch from the old to the new: {s}"


# 291.5: autopilot merges only when checks named All tests and Acceptance criteria both passed on the head

def check(name, state="SUCCESS"):
    """One check run on the pull request's head, as the fake GitHub keeps it."""
    return {"name": name, "kind": "run", "state": state}


def says_on_pr(m, words):
    """Whether a new comment on pull request #60 holds every one of `words`."""
    return any(all(w in tam.visible(b) for w in words) for b in m.new_comments("pr", tam.PR))


def test_autopilot_merges_only_when_all_tests_and_acceptance_criteria_both_passed(record_property, tmp_path):
    """Autopilot waits for the owner when All tests or Acceptance criteria is missing.

    Proves 291.5. Runs the code review of #60 on autopilot, approving, and `/autopilot start` on it, with every check on the head
    green but: Acceptance criteria missing; All tests missing; and only the old names all tests and all done-whens
    passed. Each must leave #60 open with a comment naming the missing check in its exact words and mentioning the
    owner. Beside them, a head with both checks green merges, so the test is not passing on a merge that never happens."""
    record_property("proves", "291.5")
    crit = check("57.1 · First thing works")
    cases = (("Acceptance criteria missing", [check(ALL_TESTS), crit], [CRITERIA]),
             ("All tests missing", [check(CRITERIA), crit], [ALL_TESTS]),
             ("only the old names", [check("all tests"), check("all done-whens passed"), crit], [ALL_TESTS, CRITERIA]))
    for case, runs, missing in cases:
        slug = case.replace(" ", "-")
        m = tam.Review(tmp_path / f"review-{slug}", tam.PR_APPROVE, tam.ON, runs)
        assert m.agent_started(), f"291.5 ({case}): test setup: the code review never ran:\n{m.tail()}"
        tam.assert_waits(m, "291.5", f"code review, {case}", missing[0])
        assert says_on_pr(m, missing + [f"@{tam.OWNER}"]), \
            f"291.5 (code review, {case}): no comment on #60 names {missing}: {m.new_comments('pr', tam.PR)}"
        m = tam.Command(tmp_path / f"command-{slug}", {60: tam.pr_state(57, runs)}, {57: "approve"})
        m.listen("/autopilot start")
        tam.assert_waits(m, "291.5", f"/autopilot start, {case}", missing[0])
        assert says_on_pr(m, missing + [f"@{tam.OWNER}"]), \
            f"291.5 (/autopilot start, {case}): no comment on #60 names {missing}: {m.new_comments('pr', tam.PR)}"
    both = [check(ALL_TESTS), check(CRITERIA), crit]
    m = tam.Review(tmp_path / "review-both", tam.PR_APPROVE, tam.ON, both)
    assert m.merged() == tam.HEAD, f"291.5 (code review, both green): #60 was not merged at its head:\n{m.tail()}"
    m = tam.Command(tmp_path / "command-both", {60: tam.pr_state(57, both)}, {57: "approve"})
    m.listen("/autopilot start")
    assert m.merged() == tam.HEAD, f"291.5 (/autopilot start, both green): #60 was not merged at its head:\n{m.tail()}"

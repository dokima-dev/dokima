"""Tests for #745: Dokima's own problems on a trial repo file themselves upstream.

A repo's `.dokima/settings.yaml` may name the upstream repo where Dokima's own problems go:

    upstream:
      repo: dokima-dev/dokima     # empty (the default): nothing leaves the repo

An agent tags a problem as Dokima's fault, not the repo's, by giving its issue raise `"fault": "dokima"`. Once a
review confirms it, code files a tagged problem in the upstream repo, linking back to the issue where it was seen, and
any other problem in the repo itself, as before. A failed run of a shared workflow runs
`python3 -m dokima.upstream failed WORKFLOW JOB` as its last step, which files the failure upstream with the run's
link. A repeat, the same tagged problem or the same workflow's job failing again, is a comment on the open upstream
issue, never a second issue. Calls on the upstream repo run with the key in DOKIMA_UPSTREAM_TOKEN, which the workflow
mints from the App's own key.

Every test runs against tests/upstream_gh.py, a fake `gh` on PATH that holds the trial repo o/r and Dokima's repo
dokima-dev/dokima side by side, logging the key each call ran with. Nothing leaves the machine.
"""
import json
import os
import re
import subprocess
import sys

import pytest
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from dokima import agent, prompt, raises, settings  # noqa: E402

TRIAL, UPSTREAM = "o/r", "dokima-dev/dokima"
LOCAL_KEY, UPSTREAM_KEY = "trial-key", "upstream-key"
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
# The secrets the workflows name before #745; no new credential may join them.
SECRETS_BEFORE = {"CLAUDE_CODE_OAUTH_TOKEN", "DOKIMA_APP_KEY", "SANDBOX_TOKEN", "GITHUB_TOKEN"}

TAGGED = {"kind": "issue", "label": "Card drops a line", "fault": "dokima",
          "text": "The card drops the last line of a long plan.", "evidence": "`dokima/card.py` cuts the plan fold.",
          "verdict": "new", "searched": [3]}
UNTAGGED = {"kind": "issue", "label": "Search ignores archive",
            "text": "The search page ignores archived jobs, so their links go stale.", "evidence": "`app/search.py`",
            "verdict": "new", "searched": [3]}


@pytest.fixture
def github(tmp_path, monkeypatch):
    """A fake GitHub with the trial repo and Dokima's repo, its `gh` first on PATH.

    The test runs in a temp folder standing in for the trial repo's checkout, with no settings file until the test
    writes one. Returns a reader of the fake's state."""
    state = tmp_path / "gh-state.json"
    state.write_text(json.dumps({"repos": {TRIAL: {"issues": {}, "labels": ["filed-by-dokima"]},
                                           UPSTREAM: {"issues": {}, "labels": ["filed-by-dokima"]}},
                                 "next": {}, "calls": [], "unsupported": []}))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{os.path.join(ROOT, "tests", "upstream_gh.py")}" "$@"\n')
    gh.chmod(0o755)
    work = tmp_path / "trial"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("UPSTREAM_GH_STATE", str(state))
    monkeypatch.setenv("GH_TOKEN", LOCAL_KEY)
    monkeypatch.setenv("DOKIMA_UPSTREAM_TOKEN", UPSTREAM_KEY)
    monkeypatch.setenv("GITHUB_REPOSITORY", TRIAL)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_RUN_ID", "101")
    return lambda: json.loads(state.read_text())


def name_upstream(repo=UPSTREAM):
    """Write the trial repo's settings file naming REPO as the upstream repo."""
    os.makedirs(".dokima", exist_ok=True)
    with open(os.path.join(".dokima", "settings.yaml"), "w") as f:
        f.write(f"upstream:\n  repo: {repo}\n")


def issues(state, repo):
    """The issues of REPO in the fake's state, by number."""
    return {int(n): i for n, i in state["repos"][repo]["issues"].items()}


def everything(issue):
    """An issue's body and every comment on it, as one text."""
    return "\n".join([issue["body"]] + issue["comments"])


def review(raise_list):
    """A passed review's record carrying RAISE_LIST, each a fresh copy."""
    return {"role": "reviewer", "check": {"passed": True, "problems": []},
            "handback": {"raises": [dict(r) for r in raise_list]}}


def checked_and_filed(where, number, raise_list):
    """Run the reviewer's raises through the hand-back check, then file them as from issue NUMBER.

    The tag must pass the check first, as on a real run, or nothing is filed."""
    problems = raises.check_raises("reviewer", [dict(r) for r in raise_list])
    assert problems == [], f"{where}: the hand-back check rejects a raise tagged as Dokima's fault: {problems}"
    return agent.file_issues(TRIAL, number, review(raise_list), [])


def failed(workflow="agent", job="run", run="101"):
    """Run the failure step, `python3 -m dokima.upstream failed WORKFLOW JOB`, on run RUN."""
    env = dict(os.environ, GITHUB_RUN_ID=run, PYTHONPATH=ROOT, PYTHONSAFEPATH="1")
    return subprocess.run([sys.executable, "-m", "dokima.upstream", "failed", workflow, job], env=env,
                          capture_output=True, text=True, timeout=30)


def run_link(run):
    """The trial repo's link to run RUN."""
    return f"https://github.com/{TRIAL}/actions/runs/{run}"


def test_with_no_upstream_repo_a_tagged_problem_is_filed_in_the_repo_itself(record_property, github):
    """With no upstream repo set, a problem that is Dokima's fault stays in the repo.

    The trial repo has no settings file, so the shipped default names no upstream repo. A passed review raises one
    problem tagged as Dokima's fault; code files it in the trial repo, and Dokima's repo gets nothing. Proves 745.1."""
    record_property("proves", "745.1")
    assert not (settings.read().get("upstream") or {}).get("repo"), \
        f"745.1: the shipped settings should name no upstream repo, yet they name {settings.read().get('upstream')}"
    lines = checked_and_filed("745.1", 9, [TAGGED])
    state = github()
    assert issues(state, UPSTREAM) == {}, \
        f"745.1: no upstream repo is set, yet Dokima's repo got issues: {issues(state, UPSTREAM)}"
    mine = issues(state, TRIAL)
    assert len(mine) == 1 and "drops the last line" in next(iter(mine.values()))["body"], \
        f"745.1: the tagged problem should be filed once in the repo itself; it holds {mine}; the record says {lines}"


def test_with_an_upstream_repo_a_tagged_problem_is_filed_there(record_property, github):
    """With an upstream repo set, a problem that is Dokima's fault is filed there.

    The trial repo's settings name dokima-dev/dokima. A passed review raises one problem tagged as Dokima's fault;
    code files it in Dokima's repo, with the key minted for it, and the trial repo gets nothing. Proves 745.2."""
    record_property("proves", "745.2")
    name_upstream()
    lines = checked_and_filed("745.2", 9, [TAGGED])
    state = github()
    up = issues(state, UPSTREAM)
    assert len(up) == 1 and "drops the last line" in next(iter(up.values()))["body"], \
        f"745.2: the tagged problem should be filed once in {UPSTREAM}; it holds {up}; the record says {lines}"
    assert issues(state, TRIAL) == {}, \
        f"745.2: the tagged problem should leave the trial repo alone, yet it holds {issues(state, TRIAL)}"
    keys = {c["token"] for c in state["calls"] if c["repo"] == UPSTREAM}
    assert keys == {UPSTREAM_KEY}, \
        f"745.2: every call on {UPSTREAM} should use the upstream key {UPSTREAM_KEY!r}; they used {sorted(map(str, keys))}"


def test_with_an_upstream_repo_an_untagged_problem_stays_in_the_repo_itself(record_property, github):
    """An untagged problem still files in the repo, while the tagged one goes upstream.

    The trial repo's settings name dokima-dev/dokima. A passed review raises two problems, one tagged as Dokima's
    fault and one not; the untagged one is filed in the trial repo only. Proves 745.2."""
    record_property("proves", "745.2")
    name_upstream()
    checked_and_filed("745.2", 9, [TAGGED, UNTAGGED])
    state = github()
    mine, up = issues(state, TRIAL), issues(state, UPSTREAM)
    assert len(mine) == 1 and "archived jobs" in next(iter(mine.values()))["body"], \
        f"745.2: the untagged problem should be filed once in the trial repo; it holds {mine}"
    assert all("archived jobs" not in everything(i) for i in up.values()), \
        f"745.2: the untagged problem is the repo's own, yet it reached {UPSTREAM}: {up}"
    assert len(up) == 1, f"745.2: the tagged problem beside it should still go upstream once; {UPSTREAM} holds {up}"


def test_a_problem_filed_upstream_links_back_to_the_issue_where_it_was_seen(record_property, github):
    """A problem filed upstream links back to the issue where it was seen.

    The trial repo's settings name dokima-dev/dokima. A passed review on the trial repo's issue 9 raises a problem
    tagged as Dokima's fault; the upstream issue, its body or a comment on it, links to o/r's issue 9. Proves 745.3."""
    record_property("proves", "745.3")
    name_upstream()
    checked_and_filed("745.3", 9, [TAGGED])
    up = issues(github(), UPSTREAM)
    back = f"https://github.com/{TRIAL}/issues/9"
    assert len(up) == 1, f"745.3: the tagged problem should be filed once in {UPSTREAM}; it holds {up}"
    assert back in everything(next(iter(up.values()))), \
        f"745.3: the upstream issue should link back to {back}; it says: {everything(next(iter(up.values())))!r}"


@pytest.mark.parametrize("role,grade", [("planner", "plan-grade"), ("worker", "result-grade"),
                                        ("reviewer", "plan-grade"), ("reviewer", "result-grade")])
def test_every_agent_is_told_how_to_tag_a_problem_as_dokimas_fault(record_property, role, grade):
    """Every agent's instructions show the tag for a problem that is Dokima's fault.

    Builds each agent's prompt as a run does, and checks it shows the tag `"fault": "dokima"` on an issue raise, the
    same tag the hand-back check lets through. Proves 745.4."""
    record_property("proves", "745.4")
    text = prompt.build(role, grade, settings.read(ROOT))
    assert '"fault": "dokima"' in text, \
        f"745.4: the {role}'s prompt ({grade}) never shows the tag \"fault\": \"dokima\" for a problem that is Dokima's fault"
    assert raises.check_raises(role, [dict(TAGGED)]) == [], \
        f"745.4: the {role}'s instructions name a tag the hand-back check rejects: {raises.check_raises(role, [dict(TAGGED)])}"


def test_a_tagged_problem_raised_again_is_a_comment_on_the_upstream_issue(record_property, github):
    """The same problem raised again is a comment on its upstream issue.

    The trial repo's settings name dokima-dev/dokima. The same problem, tagged as Dokima's fault, is confirmed on the
    trial repo's issue 9 and then on its issue 10; Dokima's repo holds one issue, and a comment on it links to issue 10. Proves 745.5."""
    record_property("proves", "745.5")
    name_upstream()
    checked_and_filed("745.5", 9, [TAGGED])
    checked_and_filed("745.5", 10, [TAGGED])
    up = issues(github(), UPSTREAM)
    assert len(up) == 1, f"745.5: a repeat should never open a second issue; {UPSTREAM} holds {len(up)}: {up}"
    again = f"https://github.com/{TRIAL}/issues/10"
    got = next(iter(up.values()))["comments"]
    assert any(again in c for c in got), \
        f"745.5: the repeat should be a comment linking {again}; the comments are {got}"


def test_a_failed_run_files_the_failure_upstream_with_the_run_link(record_property, github):
    """A failed run's last step files the failure upstream, linking the run.

    The trial repo's settings name dokima-dev/dokima. The agent workflow's run job fails on run 101; its last step
    runs `python3 -m dokima.upstream failed agent run`, and Dokima's repo then holds one issue whose text links run 101.
    Proves 745.6.
    """
    record_property("proves", "745.6")
    name_upstream()
    got = failed()
    assert got.returncode == 0, f"745.6: filing the failed run upstream failed: {got.stdout}{got.stderr}"
    state = github()
    up = issues(state, UPSTREAM)
    assert len(up) == 1, f"745.6: the failed run should open one issue in {UPSTREAM}; it holds {up}"
    assert run_link(101) in everything(next(iter(up.values()))), \
        f"745.6: the upstream issue should link the failed run {run_link(101)}; it says {everything(next(iter(up.values())))!r}"
    assert issues(state, TRIAL) == {}, f"745.6: the failure belongs upstream, yet the trial repo got {issues(state, TRIAL)}"
    keys = {c["token"] for c in state["calls"] if c["repo"] == UPSTREAM}
    assert keys == {UPSTREAM_KEY}, \
        f"745.6: every call on {UPSTREAM} should use the upstream key {UPSTREAM_KEY!r}; they used {sorted(map(str, keys))}"


def test_with_no_upstream_repo_a_failed_run_files_nothing(record_property, github):
    """With no upstream repo set, a failed run files nothing and the step passes.

    The trial repo has no settings file. The failure step runs and exits 0, and neither repo gets an issue or a call. Proves 745.6."""
    record_property("proves", "745.6")
    got = failed()
    assert got.returncode == 0, f"745.6: with no upstream repo the failure step should pass quietly: {got.stdout}{got.stderr}"
    state = github()
    assert issues(state, UPSTREAM) == {} and issues(state, TRIAL) == {}, \
        f"745.6: with no upstream repo nothing should be filed; got {issues(state, UPSTREAM)} and {issues(state, TRIAL)}"
    assert state["calls"] == [], f"745.6: with no upstream repo the step should call GitHub not at all: {state['calls']}"


def shared_workflows():
    """The shared workflows entry.yml hands events to, by file name."""
    with open(os.path.join(WORKFLOWS, "entry.yml")) as f:
        jobs = yaml.safe_load(f)["jobs"]
    found = {os.path.basename(j["uses"]) for j in jobs.values() if str(j.get("uses", "")).startswith("./.github/workflows/")}
    assert found, "745.7: entry.yml hands events to no shared workflow"
    return sorted(found)


def workflow(name):
    """The workflow file NAME, parsed."""
    with open(os.path.join(WORKFLOWS, name)) as f:
        return yaml.safe_load(f)


def files_failure(step):
    """True for a step that runs on failure and files the failure upstream."""
    return "failure()" in str(step.get("if", "")) and "dokima.upstream failed" in str(step.get("run", ""))


@pytest.mark.parametrize("name", shared_workflows())
def test_every_job_of_each_shared_workflow_ends_by_filing_its_failure_upstream(record_property, name):
    """Every job of each shared workflow ends with a step filing its failure upstream.

    Reads each workflow entry.yml calls. A job is covered when its own last step runs on failure and runs
    `python3 -m dokima.upstream failed`, or when a later job that needs it does so on failure. Proves 745.7."""
    record_property("proves", "745.7")
    jobs = workflow(name)["jobs"]
    final = {k for k, j in jobs.items() if "failure()" in str(j.get("if", ""))
             and any(files_failure(s) for s in j.get("steps") or [])}
    missing = []
    for k, j in jobs.items():
        if not j.get("steps") or k in final:
            continue
        needs = lambda f: k in ([jobs[f]["needs"]] if isinstance(jobs[f].get("needs"), str) else jobs[f].get("needs") or [])
        if not files_failure(j["steps"][-1]) and not any(needs(f) for f in final):
            missing.append(k)
    assert not missing, (f"745.7: in {name}, a failure of these jobs files nothing upstream, as no final step runs "
                         f"`python3 -m dokima.upstream failed` on failure: {', '.join(missing)}")


def test_the_same_failure_twice_gives_one_upstream_issue_with_two_linked_comments(record_property, github):
    """The same failure twice leaves one upstream issue with two comments, each linking its run.

    The trial repo's settings name dokima-dev/dokima. The agent workflow's run job fails on run 101, then again on
    run 102; Dokima's repo holds one issue, with exactly two comments, one linking each run. Proves 745.8."""
    record_property("proves", "745.8")
    name_upstream()
    for run in ("101", "102"):
        got = failed(run=run)
        assert got.returncode == 0, f"745.8: filing failed run {run} upstream failed: {got.stdout}{got.stderr}"
    up = issues(github(), UPSTREAM)
    assert len(up) == 1, f"745.8: the same failure twice should leave one upstream issue; {UPSTREAM} holds {len(up)}: {up}"
    comments = next(iter(up.values()))["comments"]
    assert len(comments) == 2, f"745.8: the upstream issue should hold two comments, one a run; it holds {comments}"
    for run, c in zip((101, 102), comments):
        assert run_link(run) in c, f"745.8: the comment for run {run} should link {run_link(run)}; it says {c!r}"


def test_a_different_failure_opens_its_own_upstream_issue(record_property, github):
    """A different job's failure is not a repeat: it opens its own upstream issue.

    The trial repo's settings name dokima-dev/dokima. The agent workflow's run job fails, then the card workflow's
    draw job; Dokima's repo holds two issues, each linking its own run. Proves 745.8."""
    record_property("proves", "745.8")
    name_upstream()
    for workflow_, job, run in (("agent", "run", "101"), ("card", "draw", "102")):
        got = failed(workflow_, job, run)
        assert got.returncode == 0, f"745.8: filing failed run {run} upstream failed: {got.stdout}{got.stderr}"
    up = issues(github(), UPSTREAM)
    assert len(up) == 2, f"745.8: two different failures should be two upstream issues; {UPSTREAM} holds {len(up)}: {up}"
    texts = [everything(i) for i in up.values()]
    for run in (101, 102):
        assert sum(run_link(run) in t for t in texts) == 1, \
            f"745.8: run {run} should be linked from exactly one upstream issue; the issues say {texts}"


def test_filing_upstream_mints_its_key_from_the_apps_own_key(record_property):
    """Every step filing upstream mints its key from the App's own key; no new secret.

    Reads every workflow file. Each step that files a failure upstream, and the agent workflow's step that files the
    review's problems, takes DOKIMA_UPSTREAM_TOKEN from an earlier step of its job that mints it with
    actions/create-github-app-token from the App's id and key, for the upstream repo's owner. The workflows name no
    secret beyond those named before. Proves 745.9."""
    record_property("proves", "745.9")
    seen, wrong, secrets = 0, [], set()
    for name in sorted(os.listdir(WORKFLOWS)):
        if not name.endswith(".yml"):
            continue
        with open(os.path.join(WORKFLOWS, name)) as f:
            text = f.read()
        secrets |= set(re.findall(r"secrets\.([A-Za-z_][A-Za-z0-9_]*)", text))
        for k, job in (yaml.safe_load(text).get("jobs") or {}).items():
            steps = job.get("steps") or []
            for at, step in enumerate(steps):
                run = str(step.get("run", ""))
                if "dokima.upstream failed" not in run and not (name == "agent.yml" and "dokima.agent next" in run):
                    continue
                seen += 1
                ref = re.fullmatch(r"\$\{\{\s*steps\.([\w-]+)\.outputs\.token\s*\}\}",
                                   str((step.get("env") or {}).get("DOKIMA_UPSTREAM_TOKEN", "")).strip())
                mint = next((s for s in steps[:at] if ref and s.get("id") == ref.group(1)), None)
                w = (mint or {}).get("with") or {}
                if not (mint and str(mint.get("uses", "")).startswith("actions/create-github-app-token")
                        and "vars.DOKIMA_APP_ID" in str(w.get("app-id")) and "secrets.DOKIMA_APP_KEY" in str(w.get("private-key"))
                        and w.get("owner")):
                    wrong.append(f"{name} job {k} step {step.get('name') or at + 1}")
    assert seen, "745.9: no workflow step files anything upstream yet"
    assert not wrong, ("745.9: these steps file upstream without DOKIMA_UPSTREAM_TOKEN minted from the App's own key "
                       f"for the upstream repo's owner: {'; '.join(wrong)}")
    new = sorted(secrets - SECRETS_BEFORE)
    assert not new, f"745.9: filing upstream should need no new credential, yet the workflows name new secrets: {new}"

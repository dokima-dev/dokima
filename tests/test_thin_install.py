"""Tests for #812: Dokima's workflows run from Dokima's own repo, called by one short workflow.

An adopter's repo holds one thin workflow that calls Dokima's shared workflows at a release tag; every run takes
Dokima's code from Dokima's own repo, its keys from the repo's `keys` environment, and fails saying how to fix a
missing bot or model key. Dokima's commits credit Dokima's bot unless the settings turn that off.

The thin workflow adopters install is `dokima/install/dokima.yml`; the shared workflows are this repo's
`.github/workflows/`, less the two that are Dokima's own (`playthrough.yml`, `wiki.yml`).

Most tests run real workflow steps through tests/test_settings_workflows.py's Box: a temp repo standing in for the
adopter's, a fake GitHub and a fake Claude Code. A step checking out dokima-dev/dokima gets this checkout's Dokima
code (tests/test_start.py's dokima_checkout). To prove the adopter's own code never runs, the adopter's repo holds a
`dokima/` folder whose every module only writes a mark file. Nothing leaves the machine.
"""
import glob
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(__file__))
import test_settings_workflows as sw  # noqa: E402
import test_start as ts  # noqa: E402
from test_start import Ctx, N  # noqa: E402

ROOT = ts.ROOT
THIN = os.path.join(ROOT, "dokima", "install", "dokima.yml")
WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
OWN = ("playthrough.yml", "wiki.yml")
SHARED = sorted(os.path.basename(p) for p in glob.glob(os.path.join(WORKFLOWS, "*.yml")) if os.path.basename(p) not in OWN)
CALL = re.compile(r"^dokima-dev/dokima/\.github/workflows/([\w.-]+\.ya?ml)@(.+)$")
RELEASE = re.compile(r"^v\d+\.\d+\.\d+$")
# The bot line the fake run writes (bot id 1); built from parts so the repo scan for stray addresses skips it.
BOT_LINE = "Co-authored-by: dokima-runtime[bot] <1+dokima-runtime[bot]@users." + "noreply.github.com>"
MODEL = "claude-opus-5-5"
# Every event one of Dokima's shared workflows starts on today, outside a manual start.
EVENTS = {"issues", "issue_comment", "pull_request_target", "pull_request_review", "pull_request_review_comment",
          "merge_group", "push", "schedule", "workflow_run", "repository_dispatch"}


def read_yaml(path):
    """The workflow at PATH, read with `on` kept as a name."""
    data = yaml.safe_load(open(path).read()) or {}
    if True in data:
        data["on"] = data.pop(True)
    return data


def thin(crit):
    """The thin workflow adopters install; fails naming criterion CRIT when it is missing."""
    assert os.path.isfile(THIN), f"{crit}: there is no thin workflow for adopters at dokima/install/dokima.yml"
    return read_yaml(THIN)


def calls(wf):
    """Every reusable workflow WF's jobs call, as written."""
    return [str(j["uses"]) for j in (wf.get("jobs") or {}).values() if isinstance(j, dict) and "uses" in j]


def poisoned(mark):
    """An adopter's `dokima/` folder whose every module only writes its name to MARK."""
    code = f"open({mark!r}, 'a').write(__name__ + '\\n')\n"
    out = {}
    for path in glob.glob(os.path.join(ROOT, "dokima", "**", "*.py"), recursive=True):
        out[os.path.relpath(path, ROOT)] = code
    return out


def ran_marks(mark):
    """The adopter's modules that ran, from MARK; empty when none did."""
    return open(mark).read().split() if os.path.exists(mark) else []


def without_dokima(box):
    """Remove the `dokima/` folder from the adopter's main, so the repo holds no Dokima code."""
    ts.sh(box.src, "git", "checkout", "-q", "main")
    ts.sh(box.src, "git", "rm", "-rq", "dokima")
    ts.sh(box.src, "git", "commit", "-qm", "no Dokima code here")
    ts.sh(box.src, "git", "push", "-q", "origin", "main")


def with_context(box, secrets=None, drop_secrets=(), drop_vars=()):
    """Make BOX's runs see SECRETS added, and DROP_SECRETS and DROP_VARS missing.

    A repo without those secrets or variables runs this way."""
    base = box.context

    def context(**kw):
        """The box's contexts with the repo's secrets and variables changed."""
        c = base(**kw)
        s = {k: v for k, v in c["secrets"].items() if k not in drop_secrets}
        c["secrets"] = Ctx({**s, **(secrets or {})})
        c["vars"] = Ctx({k: v for k, v in c["vars"].items() if k not in drop_vars})
        return c
    box.context = context


def everything_said(box):
    """The run's whole log and every comment it left, as one text."""
    return "\n".join(box.log + [c["body"] for c in box.posted()])


# 812.1 ------------------------------------------------------------------------------------------------------------

def test_an_adopters_own_dokima_folder_never_runs(record_property, tmp_path):
    """A run never runs Dokima code from the adopter's repo, only Dokima's own.

    Proves 812.1. The adopter's repo holds a `dokima/` folder whose every module only writes a mark. Runs agent.yml's
    planner run through its starting branch and checks no module of the adopter's ran, while the run read its model
    from Dokima's real code."""
    record_property("proves", "812.1")
    mark = str(tmp_path / "adopter-ran.txt")
    box = sw.Box(tmp_path / "box", None, files=poisoned(mark))
    _, steps = sw.steps_of("agent.yml", "run")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch"), name="planner", role="planner")
    ran = ran_marks(mark)
    assert not ran, f"812.1: the run ran Dokima code from the adopter's repo, not Dokima's own: {sorted(set(ran))}"
    assert result == "success", f"812.1: the planner's run did not get through its start with Dokima's code\n{box.tail()}"
    assert box.env.get("MODEL") == MODEL, \
        f"812.1: the run did not read its model through Dokima's code; MODEL is {box.env.get('MODEL')!r}"


def test_a_run_starts_in_a_repo_holding_no_dokima_code(record_property, tmp_path):
    """A run starts in an adopter's repo that holds no Dokima code at all.

    Proves 812.1. The adopter's main has no `dokima/` folder. Runs agent.yml's planner run through its starting branch
    and checks it succeeds with the model Dokima's code reads."""
    record_property("proves", "812.1")
    box = sw.Box(tmp_path, None)
    without_dokima(box)
    _, steps = sw.steps_of("agent.yml", "run")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch"), name="planner", role="planner")
    assert result == "success", f"812.1: a run in a repo with no Dokima code failed to start\n{box.tail()}"
    assert box.env.get("MODEL") == MODEL, f"812.1: the run read no model; MODEL is {box.env.get('MODEL')!r}"


def test_no_shared_workflow_runs_the_adopters_dokima_folder(record_property, tmp_path):
    """No job of any shared workflow runs Dokima code from the adopter's repo.

    Proves 812.1. The adopter's repo holds a `dokima/` folder whose every module only writes a mark. Runs every job of
    every shared workflow that names Dokima, on the first event it starts on, and checks no job ran any module of the
    adopter's."""
    record_property("proves", "812.1")
    mark = str(tmp_path / "adopter-ran.txt")
    box = sw.Box(tmp_path / "box", None, files=poisoned(mark))
    found = {}
    for name in SHARED:
        wf = ts.workflow(name)
        on = wf.get("on") or {}
        event = next(iter(on)) if isinstance(on, dict) and on else "workflow_dispatch"
        event = "workflow_dispatch" if event == "workflow_call" else event
        for job, body in (wf.get("jobs") or {}).items():
            if "dokima" not in yaml.safe_dump(body):
                continue  # a job that never names Dokima runs none of its code, such as the board's one-minute wait
            before = len(ran_marks(mark))
            box.run(name, job, name=f"{name}-{job}", event=event)
            after = ran_marks(mark)
            if len(after) > before:
                found[f"{name}:{job}"] = sorted(set(after[before:]))
    assert not found, f"812.1: these jobs ran Dokima code from the adopter's repo, not Dokima's own: {found}"


# 812.2 ------------------------------------------------------------------------------------------------------------

def reached():
    """Every shared workflow the thin workflow reaches, by file name, through calls of calls."""
    todo = [CALL.match(u) for u in calls(thin("812.2"))]
    assert todo and all(todo), f"812.2: the thin workflow calls no shared workflow of Dokima's: {calls(thin("812.2"))}"
    seen, todo = set(), [m.group(1) for m in todo]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        assert os.path.isfile(os.path.join(WORKFLOWS, name)), f"812.2: the thin workflow reaches {name}, which Dokima lacks"
        for u in calls(read_yaml(os.path.join(WORKFLOWS, name))):
            m = CALL.match(u) or re.match(r"^\./\.github/workflows/([\w.-]+\.ya?ml)$", u)
            if m:
                todo.append(m.group(1))
    return seen


def test_every_shared_job_that_reads_a_key_takes_it_from_the_keys_environment(record_property):
    """Every shared job that reads a key takes it from the keys environment.

    Proves 812.2. Follows the thin workflow to every shared workflow it calls, and the ones they call, and checks each
    is callable from another repo and each job naming a secret, by name or by a name from the settings, runs in the
    `keys` environment. At least one reached job must read a key, so the agent's run is among them."""
    record_property("proves", "812.2")
    keyed, outside = [], []
    for name in sorted(reached()):
        wf = read_yaml(os.path.join(WORKFLOWS, name))
        on = wf.get("on")
        assert isinstance(on, dict) and "workflow_call" in on, \
            f"812.2: {name} is reached by the adopter's workflow but cannot be called from another repo"
        for job_name, job in (wf.get("jobs") or {}).items():
            text = yaml.safe_dump(job)
            if "secrets." not in text and "secrets[" not in text:
                continue
            keyed.append(f"{name}:{job_name}")
            env = job.get("environment")
            env = env.get("name") if isinstance(env, dict) else env
            if env != "keys":
                outside.append(f"{name}:{job_name}")
    assert keyed, "812.2: no job the adopter's workflow reaches reads a key, so the agents could never run"
    assert not outside, f"812.2: these shared jobs read a key outside the keys environment: {outside}"


def agent_step_env(tmp, settings, secrets):
    """The environment the agent saw in a planner run from a repo without Dokima code."""
    box = sw.Box(tmp, settings)
    without_dokima(box)
    with_context(box, secrets=secrets)
    _, steps = sw.steps_of("agent.yml", "run")
    agent = sw.step_named(steps, "The agent (Claude Code)")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch") + [agent], name="planner", role="planner")
    path = f"{box.tmp}/gh/agent-env.json"
    assert os.path.exists(path), f"812.3: the agent never started; job {result}\n{box.tail()}"
    return json.load(open(path))


# 812.3 ------------------------------------------------------------------------------------------------------------

MY_KEY = """agents:
  subscriptions:
    mine: {agent: claude, key: MY_KEY}
  roles:
    planner: {subscription: mine, model: claude-opus-5-5}
"""


def test_each_role_reads_its_model_key_from_the_secret_its_settings_name(record_property, tmp_path):
    """A role's agent gets its key from the secret the adopter's settings name.

    Proves 812.3. The adopter's repo holds no Dokima code; its settings give the planner a subscription whose key is the
    secret MY_KEY. Runs agent.yml's planner run up to its agent and checks the agent got MY_KEY's value, not the
    default secret's. Then settings naming no agents: the agent gets the default secret's value."""
    record_property("proves", "812.3")
    env = agent_step_env(tmp_path / "named", MY_KEY, {"MY_KEY": "fake-my-key"})
    assert env.get("CLAUDE_CODE_OAUTH_TOKEN") == "fake-my-key", \
        (f"812.3: the planner's agent did not get the key from MY_KEY, the secret its settings name; "
         f"it got {env.get('CLAUDE_CODE_OAUTH_TOKEN')!r}")
    env = agent_step_env(tmp_path / "default", None, {"MY_KEY": "fake-my-key"})
    assert env.get("CLAUDE_CODE_OAUTH_TOKEN") == "fake-claude-token", \
        (f"812.3: with no agents in the settings, the agent did not get the default secret's key; "
         f"it got {env.get('CLAUDE_CODE_OAUTH_TOKEN')!r}")


# 812.4 ------------------------------------------------------------------------------------------------------------

def test_a_run_with_no_bot_set_up_fails_saying_how_to_set_it_up(record_property, tmp_path):
    """A run with no bot fails, and its error says how to set it up.

    Proves 812.4. Runs agent.yml's planner run in a repo with no app id variable and no app key secret, then in one
    with the app id but no key. Each run must fail, with an error naming the DOKIMA_APP_ID variable, the
    DOKIMA_APP_KEY secret and the keys environment they go in."""
    record_property("proves", "812.4")
    for case, drop_secrets, drop_vars in (("no bot", ("DOKIMA_APP_KEY",), ("DOKIMA_APP_ID",)),
                                          ("no app key", ("DOKIMA_APP_KEY",), ())):
        box = sw.Box(tmp_path / case.replace(" ", "-"), None)
        with_context(box, drop_secrets=drop_secrets, drop_vars=drop_vars)
        result = box.run("agent.yml", "run", name="planner", role="planner")
        assert result == "failure", f"812.4: with {case} set up, the run did not fail; job {result}"
        errors = [l for l in "\n".join(box.log).splitlines() if "::error" in l]
        said = [l for l in errors if "DOKIMA_APP_ID" in l and "DOKIMA_APP_KEY" in l and "keys" in l]
        assert said, (f"812.4: with {case} set up, no error says to add DOKIMA_APP_ID and DOKIMA_APP_KEY to the keys "
                      f"environment; its errors: {errors}")


# 812.5 ------------------------------------------------------------------------------------------------------------

def test_a_run_with_no_model_key_fails_naming_the_secret_and_how_to_add_it(record_property, tmp_path):
    """A run with no model key fails, and says which secret to add and where.

    Proves 812.5. Runs agent.yml's planner run in a repo with no CLAUDE_CODE_OAUTH_TOKEN secret: it must fail, and the
    run's log or its record on the issue must name that secret and the keys environment it goes in. Then settings
    naming the secret MY_KEY, which the repo lacks: the run fails naming MY_KEY."""
    record_property("proves", "812.5")
    for case, settings, secret in (("default", None, "CLAUDE_CODE_OAUTH_TOKEN"), ("named", MY_KEY, "MY_KEY")):
        box = sw.Box(tmp_path / case, settings)
        with_context(box, drop_secrets=("CLAUDE_CODE_OAUTH_TOKEN", "MY_KEY"))
        result = box.run("agent.yml", "run", name="planner", role="planner")
        assert result == "failure", f"812.5: with no {secret} secret, the run did not fail; job {result}"
        said = [l for l in everything_said(box).splitlines() if secret in l and "keys" in l]
        assert said, (f"812.5: with no {secret} secret, nothing the run said names {secret} and the keys environment "
                      f"to add it to\n{box.tail()}")


# 812.6 ------------------------------------------------------------------------------------------------------------

def planner_commit(tmp, settings):
    """The message of the commit agent.yml's push saves for a stand-in planner."""
    message, _ = __import__("test_settings_prompts").planner_push(tmp, settings)
    return message


def worker_commits(tmp, settings):
    """Every commit message a worker's run adds to its branch, main's own left out.

    Main moved on since the branch split off, so the run merges main in before a stand-in worker's change is pushed."""
    box = sw.Box(tmp, settings)
    box.commit(f"try/issue-{N}", {"app.py": "a = 1\n"}, "the work", start="main")
    box.commit("main", {"other.py": "o = 1\n"}, "main moves on")
    _, before = box.origin("rev-parse", f"try/issue-{N}")
    _, steps = sw.steps_of("agent.yml", "run")
    work = sw.stand_in("The worker", "echo 'b = 2' > b.py\n")
    push = sw.step_named(steps, "Push the planner's tests")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch") + [work, sw.app_step(steps), push],
                     name="worker", role="worker", env={"PASSED": "true", "STARTED": "true"})
    _, shas = box.origin("rev-list", f"try/issue-{N}", f"^{before}", "^main")
    assert shas, f"812.6: the worker's run added no commit to its branch; job {result}\n{box.tail()}"
    return {sha: box.origin("log", "-1", "--format=%B", sha)[1] for sha in shas.split()}


def test_every_commit_dokima_makes_credits_its_bot_by_default(record_property, tmp_path):
    """With no co-author setting, every commit Dokima makes credits Dokima's bot.

    Proves 812.6. In a repo with no settings file, runs agent.yml's planner push, then a worker's run that merges main
    in and pushes its change, and checks the planner's commit and each commit the worker's run added carry
    'Co-authored-by: dokima-runtime[bot]' with the bot's noreply address."""
    record_property("proves", "812.6")
    message = planner_commit(tmp_path / "planner", None)
    assert BOT_LINE in message, f"812.6: the planner's commit does not credit Dokima's bot; its message:\n{message}"
    bare = {sha: m for sha, m in worker_commits(tmp_path / "worker", None).items() if BOT_LINE not in m}
    assert not bare, f"812.6: these commits of the worker's run do not credit Dokima's bot: {bare}"


# 812.7 ------------------------------------------------------------------------------------------------------------

def test_turning_the_co_author_line_off_leaves_commits_with_none(record_property, tmp_path):
    """A repo whose settings turn the co-author line off gets commits that carry none.

    Proves 812.7. First, with no settings file, the planner's commit credits Dokima's bot, so the line is on by
    default. Then with `co_author: ""` in the settings, runs the planner's push and a worker's run that merges main in,
    and checks no commit carries a co-author line."""
    record_property("proves", "812.7")
    on = planner_commit(tmp_path / "on", None)
    assert BOT_LINE in on, f"812.7: with no settings the planner's commit has no bot line to turn off:\n{on}"
    off = 'co_author: ""\n'
    message = planner_commit(tmp_path / "planner", off)
    assert "Co-authored-by" not in message, f"812.7: with the co-author line off, the planner's commit has one:\n{message}"
    lined = {sha: m for sha, m in worker_commits(tmp_path / "worker", off).items() if "Co-authored-by" in m}
    assert not lined, f"812.7: with the co-author line off, these commits of the worker's run still carry one: {lined}"


# 812.8 ------------------------------------------------------------------------------------------------------------

def test_the_adopters_workflow_calls_dokimas_shared_workflows_at_a_release_tag(record_property):
    """The adopter's workflow calls only Dokima's shared workflows, each at a release tag.

    Proves 812.8. Reads the thin workflow and checks it calls at least one workflow, that each call names a workflow
    in Dokima's repo that exists here, at a ref shaped like a release tag (v1.2.3), and that no job runs steps of
    its own. A call at main, or any branch name, fails."""
    record_property("proves", "812.8")
    wf = thin("812.8")
    jobs = wf.get("jobs") or {}
    assert jobs, "812.8: the adopter's workflow has no jobs, so it calls nothing"
    for name, job in jobs.items():
        uses = str((job or {}).get("uses", ""))
        m = CALL.match(uses)
        assert m, f"812.8: job {name} of the adopter's workflow does not call a shared workflow of Dokima's: {uses!r}"
        assert os.path.isfile(os.path.join(WORKFLOWS, m.group(1))), f"812.8: job {name} calls {m.group(1)}, which Dokima lacks"
        assert RELEASE.match(m.group(2)), f"812.8: job {name} calls Dokima at {m.group(2)!r}, not a release tag"
        assert "steps" not in (job or {}), f"812.8: job {name} of the adopter's workflow runs steps of its own"


# 812.9 ------------------------------------------------------------------------------------------------------------

def test_the_adopters_workflow_is_at_most_twenty_lines(record_property):
    """The adopter's workflow is 20 lines long at most.

    Proves 812.9. Counts every line of the thin workflow, blank and comment lines too, and checks there are 20 or
    fewer."""
    record_property("proves", "812.9")
    assert os.path.isfile(THIN), "812.9: there is no thin workflow for adopters at dokima/install/dokima.yml"
    lines = open(THIN).read().splitlines()
    assert len(lines) <= 20, f"812.9: the adopter's workflow is {len(lines)} lines long, over 20"


# 812.10 -----------------------------------------------------------------------------------------------------------

def test_every_event_dokima_acts_on_starts_the_adopters_workflow(record_property):
    """The adopter's one workflow starts on every event Dokima acts on.

    Proves 812.10. An adopter installs one workflow and nothing else, so it alone must start Dokima. Reads the thin
    workflow and checks its triggers name every event Dokima's shared workflows start on today: issues, comments, pull
    requests, reviews, line notes, the merge queue, pushes, the schedule, finished runs and the river's own signal."""
    record_property("proves", "812.10")
    on = thin("812.10").get("on")
    names = set(on) if isinstance(on, dict) else set(on or []) if isinstance(on, list) else {on}
    missing = sorted(EVENTS - names)
    assert not missing, f"812.10: the adopter's workflow never starts on {missing}, so Dokima never runs on them"

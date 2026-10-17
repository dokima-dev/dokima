"""Tests for #796: co-author, owner docs and agent prompts follow the repo's settings.

The settings live in `.dokima/settings.yaml` on the default branch, over Dokima's shipped defaults in
`dokima/defaults.yaml`. This story reads these of them:

    co_author: Ann Example <ann@example.com>    # the Co-authored-by line on Dokima's commits; empty for none
    owner_docs: AGENTS.md                       # the owner docs file agents copy, read and are told about
    protected_paths: [.github/]                 # paths the worker's prompt says it may never change
    tests: {run_all: ..., dir: tests, tag: record_property}   # what the planner's runner line says
    style: {caps: {summary: 20, ...}}           # the caps table of the style prompt
    prompts: {append: [{name: house-rules, file: .dokima/house-rules.md}]}   # house rules after the shipped prompt

A house rules file's text goes to every role; a `## planner`, `## worker` or `## reviewer` section of it, running to
the next `## ` heading, goes only to that role's prompt.

Each test runs real steps of a workflow the way GitHub runs them, through tests/test_settings_workflows.py's Box: a
temp repo whose default branch holds the settings file, a fake GitHub and a fake Claude Code. The prompt tests run
agent.yml's checkout steps and its agent step, then read the prompt the step wrote for the agent. Nothing leaves the
machine.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_settings_workflows as sw  # noqa: E402
import test_start as ts  # noqa: E402
from test_start import N  # noqa: E402

ANN = "Ann Example <ann@example.com>"
TODAY = "Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"


def prompt_of(tmp, role, stage="", settings=None, files=None, branch_files=None):
    """The prompt agent.yml writes for ROLE at STAGE, and the job's result.

    SETTINGS and FILES go on main. The agent's branch try/issue-N exists, as the worker and reviewer need it, holding
    a planner's test and BRANCH_FILES, which are only on that branch. Runs agent.yml's steps through its checkout,
    then its agent step, with fake Claude Code."""
    box = sw.Box(tmp, settings, files=files)
    box.commit(f"try/issue-{N}", {"tests/test_x.py": 'def test_a():\n    """A."""\n', **(branch_files or {})},
               "the branch", start="main")
    _, steps = sw.steps_of("agent.yml", "run")
    agent = sw.step_named(steps, "The agent (Claude Code)")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch") + [agent], name=role + stage,
                     role=role, stage=stage)
    path = f"{box.tmp}/prompt.md"
    return (open(path).read() if os.path.exists(path) else ""), result, box


def section(text, heading):
    """TEXT's `# HEADING` section, up to the next `# ` heading; empty when none."""
    m = re.search(rf"^# {re.escape(heading)}.*?$(.*?)(?=^# |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def caps_rows(text):
    """The caps table of a prompt, as {row label: number written}."""
    return dict(re.findall(r"^\| (.+?) \| (\d+) \|$", text, re.M))


def pushed_message(box, ref):
    """The newest commit message on REF in the box's origin; empty when none."""
    code, out = box.origin("log", "-1", "--format=%B", ref)
    return out if code == 0 else ""


def planner_push(tmp, settings):
    """Run a stand-in planner and agent.yml's push; the pushed commit's message and the box."""
    box = sw.Box(tmp, settings)
    _, steps = sw.steps_of("agent.yml", "run")
    write = sw.stand_in("The planner", "mkdir -p tests\nprintf 'def test_n():\\n    assert 0\\n' > tests/test_new.py\n")
    push = sw.step_named(steps, "Push the planner's tests")
    result = box.run("agent.yml", "run", sw.through(steps, "Starting branch") + [write, sw.app_step(steps), push],
                     name="planner", role="planner", env={"PASSED": "true", "STARTED": "true"})
    message = pushed_message(box, f"try/issue-{N}")
    assert message, f"796.1: the planner's push saved no commit to check; job {result}\n{box.tail()}"
    return message, box


def wiki_sync(tmp, settings):
    """Run wiki.yml against a local wiki repo; the message of the commit it pushed."""
    box = sw.Box(tmp, settings, files={"docs/wiki/Home.md": "# Home\n"})
    ts.sh(box.tmp, "git", "init", "-q", "--bare", "-b", "master", f"{box.tmp}/wiki.git")
    seed = f"{box.tmp}/wiki-seed"
    ts.sh(box.tmp, "git", "init", "-q", "-b", "master", seed)
    open(f"{seed}/Old.md", "w").write("old\n")
    ts.sh(seed, "git", "add", "-A")
    ts.sh(seed, "git", "commit", "-qm", "old")
    ts.sh(seed, "git", "push", "-q", f"{box.tmp}/wiki.git", "master")
    results = box.run_workflow("wiki.yml", event="push")
    out = subprocess.run(["git", "--git-dir", f"{box.tmp}/wiki.git", "log", "-1", "--format=%B", "master"],
                         capture_output=True, text=True).stdout.strip()
    assert out and out != "old", f"796.1: the wiki sync pushed nothing to check: {results}\n{box.tail()}"
    return out


# 796.1 ------------------------------------------------------------------------------------------------------------

def test_the_co_author_line_on_dokimas_commits_comes_from_the_co_author_setting(record_property, tmp_path):
    """Dokima's commits credit the co-author the settings name, and no one else.

    Proves 796.1. The settings name Ann Example as co-author. Runs agent.yml's planner push and wiki.yml's sync, and
    checks each pushed commit carries 'Co-authored-by: Ann Example <ann@example.com>' and not today's fixed line.
    Then an empty co-author setting: the planner's commit carries no co-author line at all."""
    record_property("proves", "796.1")
    settings = f"co_author: {ANN}\n"
    message, _ = planner_push(tmp_path / "planner", settings)
    assert f"Co-authored-by: {ANN}" in message, \
        f"796.1: the planner's commit does not credit the co-author the settings name; its message:\n{message}"
    assert TODAY not in message, f"796.1: the planner's commit still credits the fixed co-author; its message:\n{message}"
    wiki = wiki_sync(tmp_path / "wiki", settings)
    assert f"Co-authored-by: {ANN}" in wiki, \
        f"796.1: the wiki sync's commit does not credit the co-author the settings name; its message:\n{wiki}"
    assert TODAY not in wiki, f"796.1: the wiki sync's commit still credits the fixed co-author; its message:\n{wiki}"
    empty, _ = planner_push(tmp_path / "empty", 'co_author: ""\n')
    assert "Co-authored-by" not in empty, \
        f"796.1: with the co-author setting empty, the planner's commit still has a co-author line:\n{empty}"



# 796.9 ------------------------------------------------------------------------------------------------------------

def test_with_no_co_author_setting_commits_carry_no_co_author_line(record_property, tmp_path):
    """A repo that names no co-author gets commits that credit no one.

    Proves 796.9. Dokima's shipped defaults reach every repo, so they credit no one. Runs agent.yml's planner push
    and wiki.yml's sync in a repo with no settings file, and checks neither pushed commit has a co-author line. Then
    a settings file that names other settings but no co-author: the planner's commit still has none."""
    record_property("proves", "796.9")
    default, _ = planner_push(tmp_path / "default", None)
    assert "Co-authored-by" not in default, \
        f"796.9: with no settings file, the planner's commit still has a co-author line:\n{default}"
    wiki = wiki_sync(tmp_path / "wiki", None)
    assert "Co-authored-by" not in wiki, \
        f"796.9: with no settings file, the wiki sync's commit still has a co-author line:\n{wiki}"
    other, _ = planner_push(tmp_path / "other", "owner_docs: AGENTS.md\n")
    assert "Co-authored-by" not in other, \
        f"796.9: with settings that name no co-author, the planner's commit has a co-author line:\n{other}"


# 796.10 -----------------------------------------------------------------------------------------------------------

def test_dokimas_own_settings_file_keeps_the_owners_co_author_line(record_property, tmp_path):
    """Dokima's own repo still credits its owner on every commit, from its own settings file.

    Proves 796.10. Reads this repo's own .dokima/settings.yaml, puts it on main of a temp repo, runs agent.yml's
    planner push and checks the pushed commit credits the owner with today's exact co-author line."""
    record_property("proves", "796.10")
    path = os.path.join(ts.ROOT, ".dokima", "settings.yaml")
    assert os.path.isfile(path), "796.10: Dokima's own repo has no .dokima/settings.yaml to hold the co-author line"
    message, _ = planner_push(tmp_path / "own", open(path).read())
    assert f"Co-authored-by: {TODAY}" in message, \
        f"796.10: with Dokima's own settings file, the planner's commit does not credit the owner:\n{message}"

# 796.2 ------------------------------------------------------------------------------------------------------------

def runtime_after_copy(tmp, settings, files=None):
    """Run agent.yml through its runtime copy; the runtime folder, result and box."""
    box = sw.Box(tmp, settings, files=files)
    _, steps = sw.steps_of("agent.yml", "run")
    result = box.run("agent.yml", "run", sw.through(steps, "Copy the runtime"), name="planner", role="planner")
    return f"{box.tmp}/runtime", result, box


def test_agents_copy_the_owner_docs_file_the_settings_name_in_place_of_the_rules_file(record_property, tmp_path):
    """Agents copy the owner docs file the settings name, not AGENTS.md.

    Proves 796.2. Main holds AGENTS.md and RULES.md, which links house/topic.md; the settings name RULES.md as the
    owner docs. Runs agent.yml's runtime copy and checks the runtime holds RULES.md and house/topic.md, and no
    AGENTS.md. Then settings naming a file main lacks: the copy still succeeds, with no AGENTS.md. Then no settings
    file: AGENTS.md is copied, as today."""
    record_property("proves", "796.2")
    files = {"RULES.md": "# Our rules\n\n- [Topic](house/topic.md)\n", "house/topic.md": "# Topic\n"}
    runtime, result, box = runtime_after_copy(tmp_path / "set", "owner_docs: RULES.md\n", files)
    assert result == "success", f"796.2: the runtime copy failed\n{box.tail()}"
    assert os.path.isfile(f"{runtime}/RULES.md"), \
        f"796.2: the runtime holds no RULES.md, the owner docs file the settings name: {sorted(os.listdir(runtime))}"
    assert os.path.isfile(f"{runtime}/house/topic.md"), \
        "796.2: the topic file RULES.md links, house/topic.md, was not copied with it"
    assert not os.path.exists(f"{runtime}/AGENTS.md"), \
        "796.2: the runtime still holds AGENTS.md, though the settings name RULES.md as the owner docs"
    runtime, result, box = runtime_after_copy(tmp_path / "missing", "owner_docs: NOPE.md\n")
    assert result == "success", f"796.2: settings naming an owner docs file main lacks failed the run\n{box.tail()}"
    assert not os.path.exists(f"{runtime}/AGENTS.md"), \
        "796.2: with the owner docs file missing, AGENTS.md was copied in its place"
    runtime, result, box = runtime_after_copy(tmp_path / "default", None)
    assert os.path.isfile(f"{runtime}/AGENTS.md"), f"796.2: with no settings file, AGENTS.md is no longer copied\n{box.tail()}"


# 796.3 ------------------------------------------------------------------------------------------------------------

def test_the_planner_and_worker_prompts_name_the_owner_docs_file_the_settings_name(record_property, tmp_path):
    """The planner's and the worker's prompts point to the owner docs file the settings name.

    Proves 796.3. The settings name docs/RULES.md as the owner docs. Builds the planner's and the worker's prompts
    through agent.yml and checks each names docs/RULES.md and never AGENTS.md. Then no settings file: the planner's
    prompt names AGENTS.md, as today."""
    record_property("proves", "796.3")
    files = {"docs/RULES.md": "# Our rules\n"}
    for role in ("planner", "worker"):
        prompt, result, box = prompt_of(tmp_path / role, role, settings="owner_docs: docs/RULES.md\n", files=files)
        assert prompt, f"796.3: the {role}'s prompt was not built; job {result}\n{box.tail()}"
        assert "docs/RULES.md" in prompt, f"796.3: the {role}'s prompt does not name docs/RULES.md, the owner docs file"
        assert "AGENTS.md" not in prompt, \
            f"796.3: the {role}'s prompt still names AGENTS.md, though the settings name docs/RULES.md"
    prompt, result, box = prompt_of(tmp_path / "default", "planner")
    assert "AGENTS.md" in prompt, f"796.3: with no settings file, the planner's prompt no longer names AGENTS.md\n{box.tail()}"


# 796.4 ------------------------------------------------------------------------------------------------------------

def test_the_workers_prompt_lists_the_protected_paths_the_settings_name(record_property, tmp_path):
    """The worker's prompt lists every protected path the settings name.

    Proves 796.4. The settings name ops/deploy/ and vault/ as protected paths. Builds the worker's prompt through
    agent.yml and checks it names both. Then no settings file: the prompt still names .github/, the default."""
    record_property("proves", "796.4")
    prompt, result, box = prompt_of(tmp_path / "set", "worker", settings="protected_paths: [ops/deploy/, vault/]\n")
    assert prompt, f"796.4: the worker's prompt was not built; job {result}\n{box.tail()}"
    missing = [p for p in ("ops/deploy/", "vault/") if p not in prompt]
    assert not missing, f"796.4: the worker's prompt does not list the protected paths the settings name: {missing}"
    prompt, result, box = prompt_of(tmp_path / "default", "worker")
    assert ".github/" in prompt, f"796.4: with no settings file, the worker's prompt no longer lists .github/\n{box.tail()}"


# 796.5 ------------------------------------------------------------------------------------------------------------

def test_the_planner_prompts_runner_line_is_drawn_from_the_test_settings(record_property, tmp_path):
    """The planner's runner line names the repo's test command, test folder and criterion tag.

    Proves 796.5. The settings name make check-all and make check-one {test} as the test commands, checks_here as
    the test folder and criterion_tag as the tag. Builds the planner's prompt through agent.yml and checks its
    'Where your tests run' section names make check, checks_here and criterion_tag, and no longer says pytest in
    tests/. Then no settings file: the section still names record_property, the default tag."""
    record_property("proves", "796.5")
    settings = ("tests:\n  run_all: make check-all\n  run_one: make check-one {test}\n  dir: checks_here\n"
                "  tag: criterion_tag\n")
    prompt, result, box = prompt_of(tmp_path / "set", "planner", settings=settings)
    where = section(prompt, "Where your tests run")
    assert where, f"796.5: the planner's prompt has no 'Where your tests run' section; job {result}\n{box.tail()}"
    missing = [w for w in ("make check", "checks_here", "criterion_tag") if w not in where]
    assert not missing, f"796.5: the planner's runner line does not name the test settings {missing}:\n{where}"
    assert "python3 -m pytest, tests in tests/" not in where, \
        f"796.5: the planner's runner line still names pytest in tests/, not the test settings:\n{where}"
    where = section(prompt_of(tmp_path / "default", "planner")[0], "Where your tests run")
    assert "record_property" in where, f"796.5: with no settings file, the runner line lost record_property:\n{where}"


# 796.6 ------------------------------------------------------------------------------------------------------------

def test_the_style_prompts_caps_table_is_drawn_from_the_caps_setting(record_property, tmp_path):
    """The caps table every agent reads shows the caps the settings name.

    Proves 796.6. The settings set the summary cap to 33 and the blocker cap to 44. Builds the planner's prompt
    through agent.yml and checks the caps table says 33 for summary and 44 for a blocker, while user_story keeps its
    default 20. Then no settings file: summary shows 20, as today."""
    record_property("proves", "796.6")
    prompt, result, box = prompt_of(tmp_path / "set", "planner", settings="style:\n  caps:\n    summary: 33\n    blocker: 44\n")
    rows = caps_rows(prompt)
    assert rows, f"796.6: the planner's prompt has no caps table; job {result}\n{box.tail()}"
    want = {"summary": "33", "a blocker": "44", "user_story": "20"}
    wrong = {k: rows.get(k) for k, v in want.items() if rows.get(k) != v}
    assert not wrong, f"796.6: the caps table does not follow the caps setting; want {want}, got {wrong}"
    rows = caps_rows(prompt_of(tmp_path / "default", "planner")[0])
    assert rows.get("summary") == "20", f"796.6: with no settings file, the summary cap shows {rows.get('summary')}, not 20"


# 796.7 ------------------------------------------------------------------------------------------------------------

HOUSE = ".dokima/house-rules.md"


def test_a_repos_house_rules_file_is_added_after_the_shipped_prompt(record_property, tmp_path):
    """A repo's house rules reach the agent, after the whole shipped prompt.

    Proves 796.7. Main holds a house rules file with the line HOUSE-RULE-ON-MAIN. Builds the planner's prompt through
    agent.yml and checks the line is there, after the last line of the shipped planner prompt. Then the planner's
    branch changes the file to HOUSE-RULE-ON-BRANCH: the prompt keeps main's line, never the branch's. Then a repo
    with no house rules file: the prompt is still built and the agent starts."""
    record_property("proves", "796.7")
    shipped = open(os.path.join(ts.ROOT, "dokima", "roles", "planner.md")).read().strip().splitlines()[-1]
    prompt, result, box = prompt_of(tmp_path / "set", "planner", files={HOUSE: "HOUSE-RULE-ON-MAIN\n"})
    assert "HOUSE-RULE-ON-MAIN" in prompt, \
        f"796.7: the planner's prompt does not hold the repo's house rules; job {result}\n{box.tail()}"
    assert shipped in prompt and prompt.index("HOUSE-RULE-ON-MAIN") > prompt.index(shipped), \
        "796.7: the house rules do not come after the shipped planner prompt"
    prompt, result, box = prompt_of(tmp_path / "branch", "planner", files={HOUSE: "HOUSE-RULE-ON-MAIN\n"},
                                    branch_files={HOUSE: "HOUSE-RULE-ON-BRANCH\n"})
    assert "HOUSE-RULE-ON-BRANCH" not in prompt, "796.7: the prompt took house rules from the agent's branch, not main"
    assert "HOUSE-RULE-ON-MAIN" in prompt, f"796.7: with the branch changing them, main's house rules were lost\n{box.tail()}"
    prompt, result, box = prompt_of(tmp_path / "none", "planner")
    assert result == "success" and box.agent_started(), \
        f"796.7: with no house rules file, the agent did not start; job {result}\n{box.tail()}"


# 796.8 ------------------------------------------------------------------------------------------------------------

def test_a_house_rules_section_named_for_a_role_is_added_only_to_that_roles_prompt(record_property, tmp_path):
    """A role's house rules section reaches that role only; the rest reaches all.

    Proves 796.8. Main's house rules file holds FOR-EVERY-ROLE, then a '## planner' section with FOR-THE-PLANNER and
    a '## worker' section with FOR-THE-WORKER. Builds the planner's, the worker's and the plan reviewer's prompts
    through agent.yml and checks each holds FOR-EVERY-ROLE, its own section's line, and no other role's line."""
    record_property("proves", "796.8")
    rules = "FOR-EVERY-ROLE\n\n## planner\n\nFOR-THE-PLANNER\n\n## worker\n\nFOR-THE-WORKER\n"
    own = {"planner": "FOR-THE-PLANNER", "worker": "FOR-THE-WORKER", "reviewer": None}
    for role, stage in (("planner", ""), ("worker", ""), ("reviewer", "plan")):
        prompt, result, box = prompt_of(tmp_path / role, role, stage, files={HOUSE: rules})
        assert "FOR-EVERY-ROLE" in prompt, \
            f"796.8: the {role}'s prompt lacks the house rules meant for every role; job {result}\n{box.tail()}"
        if own[role]:
            assert own[role] in prompt, f"796.8: the {role}'s prompt lacks its own house rules section"
        others = [line for r, line in own.items() if r != role and line and line in prompt]
        assert not others, f"796.8: the {role}'s prompt holds another role's house rules: {others}"

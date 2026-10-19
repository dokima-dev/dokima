"""A run's work and log survive a branch that moved while the run worked (#912).

Seen on an adopter repo: two runs overlapped, the planner's push to try/issue-N was rejected (non-fast-forward), so
was its push of its conversation to the logs branch (fetch first), and the run's work and log were thrown away.

The pushes are played from the real agent workflow, against a local copy of GitHub, with no git identity set outside
what the workflow sets itself, as on GitHub's own machines. A stand-in `git` on PATH makes the remote gain a commit
from someone else right before the run's push, as when another run pushed first; every other git call is the real git.

- The branch push is the real "Push the planner's tests or the worker's code to try/issue-N" step, run with bash in a
  clone of try/issue-7, given the environment the earlier steps of the run give it.
- The log push and the start of the next stage are a whole plan review run of agent.yml on #57 (test_start.py's
  machine) that blocks the plan, so it starts the planner again, as in the adopter's case.
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_start as ts  # noqa: E402
from test_start import N, STORY_PLANNED, load_yaml  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AGENT_YML = os.path.join(ROOT, ".github", "workflows", "agent.yml")
PUSH_STEP = "Push the planner's tests or the worker's code to try/issue-N"
URL = "https://x-access-token:T@github.com/o/r.git"
REAL_GIT = shutil.which("git")
ID = ["-c", "user.name=someone", "-c", "user.email=someone@example.com"]
# A plan review that blocks the plan, so the run starts the planner again.
BLOCK = {**ts.APPROVE, "verdict": "block", "summary": "One test is missing.",
         "asks": [{**ts.APPROVE["asks"][0], "criterion": f"{N}.1"}],
         "raises": [{"kind": "blocker", "to": "planner", "label": "57.1", "text": "No good-case test.",
                     "evidence": "The plan has one test for the bad case only."}]}

# The stand-in git: before each of the first MOVES pushes to the watched branch, someone else pushes to it first.
SHIM = """#!/bin/sh
P=; B=
for a in "$@"; do
  case "$a" in
    push) P=1 ;;
    {branch}|*:{branch}|*/heads/{branch}) B=1 ;;
  esac
done
if [ -n "$P" ] && [ -n "$B" ]; then
  n=$(cat '{count}' 2>/dev/null || echo 0)
  if [ "$n" -lt {moves} ]; then echo $((n + 1)) > '{count}'; sh '{mover}' $((n + 1)) >> '{mover}.log' 2>&1; fi
fi
exec '{git}' "$@"
"""

# Someone else's push: catch up with the remote's branch, commit one file, push it, and note the commit.
MOVER = """set -e
cd '{clone}'
'{git}' fetch -q origin '{branch}'
'{git}' reset -q --hard FETCH_HEAD
mkdir -p "$(dirname '{path}')"
echo "moved $1" > '{path}'
'{git}' add -A
'{git}' {ident} commit -qm "someone else's push $1"
'{git}' push -q origin 'HEAD:{branch}'
'{git}' rev-parse HEAD > '{note}'
"""


def git(cwd, *args):
    """Run the real git with an identity, for the test's own setup."""
    p = subprocess.run([REAL_GIT, *ID, *args], cwd=cwd, capture_output=True, text=True)
    assert p.returncode == 0, f"test setup: git {' '.join(args)} failed: {p.stderr}"
    return p.stdout.strip()


def no_identity(env):
    """ENV with no git identity, and git told never to guess one."""
    env = {k: v for k, v in env.items() if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
    n = int(env.get("GIT_CONFIG_COUNT") or 0)
    env[f"GIT_CONFIG_KEY_{n}"], env[f"GIT_CONFIG_VALUE_{n}"] = "user.useConfigOnly", "true"
    env["GIT_CONFIG_COUNT"] = str(n + 1)
    env["GIT_CONFIG_GLOBAL"], env["GIT_CONFIG_NOSYSTEM"] = os.devnull, "1"
    return env


def install_mover(tmp, origin, branch, moves, path):
    """Put in the stand-in git, which moves BRANCH before the run's first pushes.

    Returns (the shim folder, the file holding the newest commit someone else pushed)."""
    name = branch.replace("/", "-")
    clone, shim = os.path.join(tmp, f"someone-{name}"), os.path.join(tmp, "shim")
    git(tmp, "clone", "-q", "-b", branch, str(origin), clone)
    os.makedirs(shim, exist_ok=True)
    note, mover = os.path.join(tmp, f"moved-{name}"), os.path.join(tmp, f"mover-{name}.sh")
    open(mover, "w").write(MOVER.format(clone=clone, git=REAL_GIT, branch=branch, path=path, note=note,
                                        ident=" ".join(ID)))
    open(os.path.join(shim, "git"), "w").write(SHIM.format(branch=branch, count=os.path.join(tmp, f"count-{name}"),
                                                           moves=moves, mover=mover, git=REAL_GIT))
    os.chmod(os.path.join(shim, "git"), 0o755)
    return shim, note


def push_step():
    """The branch push step's shell, with GitHub's ${{ }} expressions filled in."""
    wf = load_yaml(open(AGENT_YML).read())
    step = next((s for s in wf["jobs"]["run"]["steps"] if s.get("name") == PUSH_STEP), None)
    assert step is not None, f"agent.yml has no step named {PUSH_STEP!r}"
    return re.sub(r"\$\{\{\s*github\.run_id\s*\}\}", "1", step["run"])


def play_branch_push(tmp, moves=1, clash=(), merge_main=False):
    """A planner on #7 changes tests/t.py while try/issue-7 moves on GitHub.

    Someone else's pushes change the files in CLASH, or a file of their own when CLASH is empty. With MERGE_MAIN, main
    gained a commit before the run, and the run merged main in at its start, as every planner run does. Returns a dict:
    code, output, env (what the step wrote to GITHUB_ENV), check (OUT/check.txt), out (OUT), origin, moved (the newest
    commit someone else pushed) and main (main's tip)."""
    tmp = str(tmp)
    origin, start, run = os.path.join(tmp, "origin.git"), os.path.join(tmp, "start"), os.path.join(tmp, "run")
    git(tmp, "init", "-q", "--bare", "-b", "main", origin)
    git(tmp, "clone", "-q", origin, start)
    os.makedirs(os.path.join(start, "tests"))
    open(os.path.join(start, "tests", "t.py"), "w").write("a = 1\n")
    open(os.path.join(start, "tests", "u.py"), "w").write("u = 1\n")
    git(start, "add", "-A"); git(start, "commit", "-qm", "start")
    git(start, "push", "-q", "origin", "HEAD:main", "HEAD:try/issue-7")
    if merge_main:
        # The branch holds an earlier round's tests, so merging main in makes a merge commit, as on a later round.
        open(os.path.join(start, "tests", "v.py"), "w").write("v = 1\n")
        git(start, "add", "-A"); git(start, "commit", "-qm", "earlier round")
        git(start, "push", "-q", "origin", "HEAD:try/issue-7")
        git(start, "reset", "-q", "--hard", "HEAD~1")
        open(os.path.join(start, "main.py"), "w").write("m = 1\n")
        git(start, "add", "-A"); git(start, "commit", "-qm", "main moved")
        git(start, "push", "-q", "origin", "HEAD:main")
    git(tmp, "clone", "-q", "-b", "try/issue-7", origin, run)
    tip = git(run, "rev-parse", "HEAD")
    if merge_main:
        git(run, "merge", "-q", "--no-edit", "origin/main")
    base = git(run, "rev-parse", "HEAD")
    # The planner's own edit.
    open(os.path.join(run, "tests", "t.py"), "w").write("a = 3\n")
    for f in clash:
        if f != "tests/t.py":
            open(os.path.join(run, f), "w").write("u = 3\n")
    paths = list(clash) or ["other.py"]
    shim, note = install_mover(tmp, origin, "try/issue-7", moves, paths[0])
    if len(paths) > 1:
        # Every clashing file is changed by someone else's one push.
        mover = os.path.join(tmp, "mover-try-issue-7.sh")
        text = open(mover).read()
        extra = "".join(f"echo \"theirs $1\" > '{p}'\n" for p in paths[1:])
        open(mover, "w").write(text.replace("'" + REAL_GIT + "' add -A", extra + "'" + REAL_GIT + "' add -A"))
    bin_dir, out = os.path.join(tmp, "bin"), os.path.join(tmp, "out")
    os.makedirs(bin_dir); os.makedirs(out)
    open(os.path.join(bin_dir, "gh"), "w").write('#!/bin/sh\ncase "$*" in *users/*) echo 1 ;; esac\nexit 0\n')
    os.chmod(os.path.join(bin_dir, "gh"), 0o755)
    env_file = os.path.join(tmp, "github_env")
    open(env_file, "w").close()
    home = os.path.join(tmp, "home")
    os.makedirs(home)
    env = no_identity({**{k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG")}, "HOME": home, "PATH": f"{shim}{os.pathsep}{bin_dir}{os.pathsep}{os.environ['PATH']}",
                       "PYTHONPATH": ROOT, "ROLE": "planner", "STAGE": "", "N": "7", "OUT": out, "GITHUB_ENV": env_file,
                       "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "1", "GH_TOKEN": "T", "SLUG": "bot",
                       "PASSED": "true", "TESTS_DIR": "tests", "DEFAULT_BRANCH": "main", "CO_AUTHOR": "",
                       "HOTFIX": "", "BRANCH_TIP": tip, "BASE": base, "PLANNER_BASE": tip, "PLANNER_RUN_BASE": base,
                       "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": f"url.{origin}.insteadOf", "GIT_CONFIG_VALUE_0": URL})
    p = subprocess.run(["bash", "-e", "-c", push_step()], cwd=run, env=env, capture_output=True, text=True, timeout=60)
    check = os.path.join(out, "check.txt")
    return {"code": p.returncode, "output": p.stdout + p.stderr, "env": open(env_file).read(), "out": out,
            "check": open(check).read() if os.path.exists(check) else "", "origin": origin,
            "moved": open(note).read().strip() if os.path.exists(note) else "",
            "main": git(tmp, "--git-dir", origin, "rev-parse", "main")}


def branch_log(r):
    """The subjects on try/issue-7 on GitHub, newest first."""
    return git(r["origin"], "log", "--format=%s", "try/issue-7").splitlines()


def assert_run_commit_on_top(r, crit, moves, merged=False):
    """The branch on GitHub ends with the run's own commit on top.

    The run's commit sits right on that push; with MERGED, the run's own merge of main sits between them."""
    assert r["moved"], f"{crit}: setup: the remote never moved:\n{r['output']}"
    assert r["code"] == 0 and "PASSED=false" not in r["env"] and not r["check"], \
        (f"{crit}: after try/issue-7 moved {moves} time(s) the run was marked failed, so its work was thrown away: "
         f"{r['check']!r} {r['env']!r}\n{r['output']}")
    top = git(r["origin"], "log", "-1", "--format=%s%n%P", "try/issue-7").splitlines()
    assert top[0].startswith("planner for #7"), \
        f"{crit}: the run's commit is not on top of try/issue-7 after it moved; the top is {top[0]!r}:\n{branch_log(r)}"
    below = top[1].split()
    if merged:
        below = git(r["origin"], "log", "-1", "--format=%P", below[0]).split() if len(below) == 1 else below
        below = below[:1]
    assert below == [r["moved"]], \
        (f"{crit}: the run's commit was not put on top of the branch's new tip {r['moved'][:7]}; it sits on "
         f"{below!r}:\n{branch_log(r)}")
    t = git(r["origin"], "show", "try/issue-7:tests/t.py")
    assert t == "a = 3", f"{crit}: the run's own change to tests/t.py is not on the branch: {t!r}"


def test_a_branch_that_moved_ends_with_the_runs_commit_on_top(record_property, tmp_path):
    """When the run's branch moved, the run's commit still ends on top.

    Someone else pushes to try/issue-7 right before the run's push, which is then rejected. The run catches up and
    pushes again: the branch ends with the run's commit, its only parent the other push, and the run is not failed. Proves 912.1."""
    record_property("proves", "912.1")
    assert_run_commit_on_top(play_branch_push(tmp_path, moves=1), "912.1", 1)


def test_a_branch_that_moves_again_during_the_retry_still_gets_the_runs_commit(record_property, tmp_path):
    """When the branch moves again during the retry, the run's commit still lands.

    Someone else pushes to try/issue-7 right before each of the run's first two pushes, so the first retry is rejected
    too; the run's third try lands, on top of the newest push. Proves 912.1."""
    record_property("proves", "912.1")
    assert_run_commit_on_top(play_branch_push(tmp_path, moves=2), "912.1 (moved twice)", 2)


def test_a_planner_that_merged_main_keeps_main_merged_after_catching_up(record_property, tmp_path):
    """A planner that merged main keeps main merged once after catching up.

    Main gained a commit, the planner merged it in, and try/issue-7 moved before the push. After the run catches up,
    main's own commit is part of the branch, exactly once, and the run's commit is on top. Proves 912.1."""
    record_property("proves", "912.1")
    r = play_branch_push(tmp_path, moves=1, merge_main=True)
    assert_run_commit_on_top(r, "912.1 (main merged in)", 1, merged=True)
    p = subprocess.run([REAL_GIT, "--git-dir", r["origin"], "merge-base", "--is-ancestor", r["main"], "try/issue-7"])
    assert p.returncode == 0, "912.1 (main merged in): main's commit is no longer part of try/issue-7 after catching up"
    copies = [s for s in branch_log(r) if s == "main moved"]
    assert len(copies) == 1, f"912.1 (main merged in): main's commit shows {len(copies)} times on the branch:\n{branch_log(r)}"


def record_problems(r):
    """The record the next step writes from this run's check, as its list of problems."""
    out = r["out"]
    env = {**os.environ, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "1", "N": "7"}
    env.pop("PACK", None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "record", "planner", "", out, os.path.join(out, "check.txt"),
                        "false", os.path.join(out, "no-logs")], env=env, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"setup: the record could not be written: {p.stdout}{p.stderr}"
    rec = json.load(open(os.path.join(out, "record.json")))
    return "\n".join(str(x) for x in (rec.get("check") or {}).get("problems") or [])


def assert_fails_naming(r, crit, files):
    """The run fails, nothing reaches the branch, and its record names every clashing file."""
    assert r["moved"], f"{crit}: setup: the remote never moved:\n{r['output']}"
    assert not any(s.startswith("planner for #7") for s in branch_log(r)), \
        f"{crit}: a commit that clashes with the branch was pushed:\n{branch_log(r)}"
    assert "PASSED=false" in r["env"], f"{crit}: a run whose changes clash with the branch was not failed: {r['env']!r}"
    problems = record_problems(r)
    missing = [f for f in files if f not in problems]
    assert not missing, f"{crit}: the failed run's record does not name the clashing files {missing}: {problems!r}"


def test_a_clash_with_the_moved_branch_fails_the_run_naming_the_file(record_property, tmp_path):
    """A clash with the moved branch fails the run, its record naming the file.

    Someone else changes tests/t.py on try/issue-7 while the run changes it too. Nothing reaches the branch, the run is
    marked failed, and the record written from its check names tests/t.py. Proves 912.2."""
    record_property("proves", "912.2")
    assert_fails_naming(play_branch_push(tmp_path, moves=1, clash=("tests/t.py",)), "912.2", ["tests/t.py"])


def test_a_clash_in_two_files_names_both(record_property, tmp_path):
    """When two files clash, the failed run's record names both.

    Someone else changes tests/t.py and tests/u.py on try/issue-7 while the run changes both too. Proves 912.2."""
    record_property("proves", "912.2")
    assert_fails_naming(play_branch_push(tmp_path, moves=1, clash=("tests/t.py", "tests/u.py")), "912.2 (two files)",
                        ["tests/t.py", "tests/u.py"])


class ReviewRun(ts.Run):
    """A whole plan review run on #57 that blocks, with no git identity.

    SETUP(machine) runs once the local GitHub is ready, right before the run starts: a test makes the logs branch
    move there, or makes GitHub refuse some pushes to it."""

    def __init__(self, tmp, setup):
        self.setup = setup
        super().__init__(tmp, "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BLOCK)

    def base_env(self, event_name):
        """The machine's environment, with no git identity and the stand-in git first."""
        env = no_identity(super().base_env(event_name))
        shim = os.path.join(self.tmp, "shim")
        if os.path.isdir(shim):
            env["PATH"] = f"{shim}:{env['PATH']}"
        return env

    def run_job(self, *args, **kwargs):
        """Run the setup, then the job."""
        self.setup(self)
        return super().run_job(*args, **kwargs)

    def logs_files(self):
        """Every file on the logs branch on GitHub."""
        return git(self.tmp, "--git-dir", f"{self.tmp}/origin.git", "ls-tree", "-r", "--name-only", "logs").splitlines()

    def logs_commit_of(self, path):
        """The commit on the logs branch that added PATH, with its parents, as 'sha parent...'."""
        return git(self.tmp, "--git-dir", f"{self.tmp}/origin.git", "log", "--diff-filter=A", "--format=%H %P", "logs",
                   "--", path)


CONVERSATION = f"logs/{N}/42-reviewer-plan.md"


def assert_log_on_top(m, crit):
    """The run's conversation is on the logs branch, right on top of the move."""
    note = open(m.note).read().strip() if os.path.exists(m.note) else ""
    assert note, f"{crit}: setup: the logs branch never moved:\n{m.tail()}"
    assert CONVERSATION in m.logs_files(), \
        f"{crit}: the run's conversation never reached the logs branch after it moved:\n{m.tail()}"
    added = m.logs_commit_of(CONVERSATION).split()
    assert added[1:] == [note], \
        (f"{crit}: the commit saving the conversation is not right on top of the logs branch's new tip "
         f"{note[:7]}; its parents are {added[1:]}")


def moving_logs(moves):
    """A setup that moves the logs branch before the run's first pushes to it."""
    def setup(m):
        _, m.note = install_mover(m.tmp, f"{m.tmp}/origin.git", "logs", moves, "logs/someone-else/moved.md")
    return setup


def test_a_logs_branch_that_moved_still_gets_the_runs_log(record_property, tmp_path):
    """When the logs branch moved, the run's conversation log still lands on top.

    Someone else pushes to the logs branch right before the run's push of its conversation, which is then rejected.
    The run catches up and pushes again: its conversation is on the logs branch, right on top of the other push. Proves 912.3."""
    record_property("proves", "912.3")
    assert_log_on_top(ReviewRun(tmp_path, moving_logs(1)), "912.3")


def test_a_logs_branch_that_moves_again_during_the_retry_still_gets_the_runs_log(record_property, tmp_path):
    """When the logs branch moves again during the retry, the log still lands.

    Someone else pushes to the logs branch right before each of the run's first two pushes to it. Proves 912.3."""
    record_property("proves", "912.3")
    assert_log_on_top(ReviewRun(tmp_path, moving_logs(2)), "912.3 (moved twice)")


# GitHub refusing every push to the logs branch that adds a file matching PATTERN.
REFUSE = """#!/bin/sh
while read old new ref; do
  [ "$ref" = refs/heads/logs ] || continue
  if git diff --name-only "$old" "$new" | grep -qE '{pattern}'; then echo "refused: {why}" >&2; exit 1; fi
done
exit 0
"""


def refusing(pattern, why):
    """A setup where GitHub refuses pushes to logs adding a matching file."""
    def setup(m):
        hook = f"{m.tmp}/origin.git/hooks/pre-receive"
        open(hook, "w").write(REFUSE.format(pattern=pattern, why=why))
        os.chmod(hook, 0o755)
    return setup


def planner_starts(m):
    """The signals the run sent to start the planner on #57."""
    return [d for d in m.dispatches() if "client_payload[role]=planner" in d and f"client_payload[issue]={N}" in d]


def test_the_next_agent_starts_only_once_the_runs_pushes_landed(record_property, tmp_path):
    """The next agent starts only after the run's own pushes landed.

    The plan review blocks the plan, so it starts the planner. With every push to the logs branch refused, the planner
    is never started; with nothing refused, the same run starts it exactly once. Proves 912.4."""
    record_property("proves", "912.4")
    ok = ReviewRun(tmp_path / "landed", lambda m: None)
    assert len(planner_starts(ok)) == 1, \
        f"912.4: setup: with every push landed the run did not start the planner once: {ok.dispatches()}\n{ok.tail()}"
    m = ReviewRun(tmp_path / "refused", refusing(r"^logs/", "every push to logs"))
    assert planner_starts(m) == [], \
        f"912.4: the run started the planner though its pushes to the logs branch never landed: {m.dispatches()}"


def test_a_conversation_that_never_landed_starts_no_next_agent(record_property, tmp_path):
    """When the conversation log never landed, no next agent starts.

    Proves 912.4."""
    record_property("proves", "912.4")
    m = ReviewRun(tmp_path, refusing(r"^logs/[0-9]+/[^/]+\.md$", "the conversation"))
    assert CONVERSATION not in m.logs_files(), f"912.4: setup: the conversation was not refused:\n{m.tail()}"
    assert planner_starts(m) == [], \
        f"912.4: the run started the planner though its conversation never reached the logs branch: {m.dispatches()}"


def test_a_record_that_never_landed_starts_no_next_agent(record_property, tmp_path):
    """When only the run's record could not be pushed, the next agent is not started.

    Proves 912.4."""
    record_property("proves", "912.4")
    m = ReviewRun(tmp_path, refusing(r"^logs/[0-9]+/records/", "the record"))
    assert planner_starts(m) == [], \
        f"912.4: the run started the planner though its record never reached the logs branch: {m.dispatches()}"

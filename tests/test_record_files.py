"""Each run saves its record as its own file, read back only from files (#610).

Today a record lives as JSON inside the bot's comment, and anyone with write access can edit or delete a comment. The
owner's words (#560, comment of 2026-10-12): "Each agent's JSON hand-back is saved as its own file on a protected
branch (one file per record, never edited)", and "Starting packs build every earlier record from record files with no
API call, and no code reads a record from a comment." On this issue the owner left the card's readers to #613.

What the code these tests run must do, as the plan pins it:
- `python3 -m dokima.agent save-record N OUT` saves OUT/record.json as one new file under `logs/N/records/` on the
  `logs` branch of the logs remote, and pushes it. It never changes a file already there, even for a run that saves
  twice. A remote with no `logs` branch yet gets one. The logs remote is the git URL in DOKIMA_LOGS_REMOTE when set,
  else the repo itself on GitHub.
- `agent.pack()` reads every earlier record of issue N from those files, fetched from the logs remote with git, oldest
  saved first (by the commit that added each file), and makes no GitHub call for them. It writes each record to in/
  as the file holds it. A bot comment carrying a record's JSON counts for nothing. The card's own readers move to #613,
  as the owner decided on this issue.
- agent.yml's run job saves the record in a step that always runs, after the record is written; its unrecorded job
  saves the failed record it writes.

The tests use a local bare git repo as the logs remote and fake GitHub (gh) in-process for the pack.
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent  # noqa: E402
try:  # main keeps `gh` in its own file (#640); this branch merges main when the worker starts
    from dokima import agent_github  # noqa: E402
except ImportError:  # before that merge, `gh` is still in agent.py; test_start's import below needs the name too
    import dokima
    agent_github = dokima.agent_github = sys.modules["dokima.agent_github"] = agent
from test_start import load_yaml  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = "o/r"
N = 9
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

PLAN = {"kind": "user_story", "title": "Slow calls hand back a job id", "summary": "Slow calls hand back a job id.",
        "user_story": "Owners get a job id.", "acceptance_criteria": [], "non_functional": [], "scope": [],
        "tests": {}, "test_changes": {}, "links": {"blocked_by": [], "blocks": [], "relates_to": []}}
PLANNER = {"role": "planner", "stage": "", "run_id": "80", "handback": PLAN, "check": {"passed": True, "problems": []}}
REVIEW = {"role": "reviewer", "stage": "plan", "run_id": "79",
          "handback": {"verdict": "approve", "summary": "The plan holds.", "raises": [], "answers": []},
          "check": {"passed": True, "problems": []}}


def git(*args, cwd=None):
    """Run git with an identity and return its output; a failure shows git's own words."""
    r = subprocess.run(["git", *args], cwd=cwd, env={**os.environ, **IDENTITY}, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} failed: {r.stderr}"
    return r.stdout


def bare_remote(tmp_path, with_main=False):
    """A local bare git repo standing in for GitHub, with no logs branch.

    It has a main branch when asked."""
    remote = tmp_path / "remote.git"
    git("init", "-q", "--bare", "-b", "main", str(remote))
    if with_main:
        work = tmp_path / "main-work"
        git("init", "-q", "-b", "main", str(work))
        (work / "README.md").write_text("main\n")
        git("add", "-A", cwd=work)
        git("commit", "-qm", "main", cwd=work)
        git("push", "-q", str(remote), "main", cwd=work)
    return remote


def save(tmp_path, remote, rec, name, crit="610.1"):
    """Run the save step on one record, as agent.yml does.

    A failure fails the test naming the criterion."""
    out = tmp_path / name
    out.mkdir()
    (out / "record.json").write_text(json.dumps(rec, indent=1))
    env = {**os.environ, **IDENTITY, "PYTHONPATH": ROOT, "GITHUB_REPOSITORY": REPO, "DOKIMA_LOGS_REMOTE": str(remote),
           "GH_TOKEN": "fake"}
    env.pop("PYTHONSAFEPATH", None)
    r = subprocess.run([sys.executable, "-m", "dokima.agent", "save-record", str(N), str(out)], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"{crit}: `dokima.agent save-record` failed (exit {r.returncode}): {r.stderr[-800:]}"


def logs_branch(tmp_path, remote, name="logs-checkout"):
    """A fresh clone of the remote's logs branch, or None when it has none."""
    if not git("ls-remote", "--heads", str(remote), "logs").strip():
        return None
    co = tmp_path / name
    git("clone", "-q", "-b", "logs", str(remote), str(co))
    return co


def record_files(co):
    """Every record file of issue N on a logs checkout, by path."""
    return sorted(glob.glob(os.path.join(str(co), "logs", str(N), "records", "*.json")))


def holds(path, rec):
    """True when the file at `path` holds the record `rec`.

    Code may add fields, never change one."""
    got = json.load(open(path))
    return isinstance(got, dict) and all(got.get(k) == v for k, v in rec.items())


def fake_github(monkeypatch, comments=()):
    """Fake GitHub for the pack: issue #9 with these comments; returns the list of calls."""
    calls = []

    def gh(*args):
        calls.append(args)
        if args[:2] == ("issue", "view"):
            return json.dumps({"number": N, "title": "T", "body": "B", "comments": list(comments)})
        if args[:2] == ("pr", "list"):
            return "[]"
        if args[0] == "api" and "/parent" in args[1]:
            raise subprocess.CalledProcessError(1, "gh", stderr="HTTP 404: Not Found")
        if args[0] == "api":
            return "[]"
        raise AssertionError(f"unexpected gh call {args}")
    monkeypatch.setattr(agent_github, "gh", gh)
    return calls


def packed(dest):
    """The records the pack put in in/, oldest first."""
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(str(dest), "in", "*.json")))]


def same(got, rec):
    """True when a packed record is `rec`; the pack may add fields."""
    return all(got.get(k) == v for k, v in rec.items())


def bot_comment(rec, at="2026-10-13T10:00:00Z"):
    """A bot comment carrying a record's JSON, as records were posted before #610."""
    return {"author": {"login": agent.BOT}, "body": f"{agent.MARK}\n**Planner**\n\n```json\n{json.dumps(rec)}\n```\n",
            "createdAt": at, "url": f"https://github.com/{REPO}/issues/{N}#issuecomment-1"}


# 610.1 ---------------------------------------------------------------------------------------------------------------

def test_each_run_saves_its_record_as_a_new_file_never_editing_an_older_one(record_property, tmp_path):
    """Each run's record is a new file on the logs branch; older files never change.

    Saves a planner's record, then a second record from the same run (a re-run), through the save step agent.yml
    runs, into a local stand-in for the repo. Checks the logs branch then holds two record files for the issue, each
    holding its own record, and the first file's bytes and history are exactly as they were after the first save.

    Proves 610.1."""
    record_property("proves", "610.1")
    remote = bare_remote(tmp_path)
    save(tmp_path, remote, PLANNER, "out1")
    co = logs_branch(tmp_path, remote, "after-first")
    assert co is not None, "610.1: no logs branch after the first record was saved"
    first = record_files(co)
    assert len(first) == 1 and holds(first[0], PLANNER), \
        f"610.1: the first run's record is not its own file under logs/{N}/records/: {first}"
    rel = os.path.relpath(first[0], co)
    before = open(first[0], "rb").read()

    again = {**PLANNER, "handback": {**PLAN, "summary": "Slow calls hand back a job id, second try."}}
    save(tmp_path, remote, again, "out2")
    co2 = logs_branch(tmp_path, remote, "after-second")
    files = record_files(co2)
    assert len(files) == 2, f"610.1: two runs should leave two record files, found {len(files)}: {files}"
    assert open(os.path.join(co2, rel), "rb").read() == before, "610.1: saving a later record changed an older file"
    commits = git("log", "--format=%H", "--", rel, cwd=co2).split()
    assert len(commits) == 1, f"610.1: the older record file was written in {len(commits)} commits, not once"
    newer = [f for f in files if os.path.relpath(f, co2) != rel]
    assert holds(newer[0], again), "610.1: the second run's file does not hold its own record"


def test_the_first_record_starts_the_logs_branch(record_property, tmp_path):
    """A repo with no logs branch gets one holding the first record.

    Saves one record into a stand-in repo that has only main, then checks the logs branch exists with that one record
    file and main still points at the same commit.

    Proves 610.1."""
    record_property("proves", "610.1")
    remote = bare_remote(tmp_path, with_main=True)
    main_before = git("rev-parse", "main", cwd=remote).strip()
    save(tmp_path, remote, PLANNER, "out")
    co = logs_branch(tmp_path, remote)
    assert co is not None, "610.1: saving the first record did not start the logs branch"
    files = record_files(co)
    assert len(files) == 1 and holds(files[0], PLANNER), f"610.1: the logs branch should hold the one record: {files}"
    assert git("rev-parse", "main", cwd=remote).strip() == main_before, "610.1: saving a record changed main"


def test_every_run_saves_its_record_whatever_happened(record_property):
    """A run saves its record even when it failed, was cancelled or died.

    Reads agent.yml: the run job must save the record in a step that always runs, after the step that writes the
    record; the unrecorded job, which writes the failed record of a run that died, must save that record after it.

    Proves 610.1."""
    record_property("proves", "610.1")
    jobs = load_yaml(open(os.path.join(ROOT, ".github", "workflows", "agent.yml")).read())["jobs"]

    def at(steps, words):
        return [i for i, s in enumerate(steps) if words in str(s.get("run") or "")]

    run = jobs["run"]["steps"]
    writes = [i for i, s in enumerate(run) if s.get("name") == "Write this run's record"]
    saves = at(run, "dokima.agent save-record")
    assert writes and saves, "610.1: agent.yml's run job has no step running `dokima.agent save-record`"
    assert saves[-1] > writes[0], "610.1: the run job saves the record before the step that writes it"
    assert str(run[saves[-1]].get("if") or "").strip() == "always()", \
        f"610.1: the save step runs only `if: {run[saves[-1]].get('if')}`, so a failed or skipped run loses its record"
    late = jobs["unrecorded"]["steps"]
    writes, saves = at(late, "dokima.agent unrecorded"), at(late, "dokima.agent save-record")
    assert writes and saves and saves[-1] > writes[0], \
        "610.1: the unrecorded job never saves the failed record it writes for a run that died"


# 610.2 ---------------------------------------------------------------------------------------------------------------

def test_a_starting_pack_holds_every_earlier_record_from_record_files(record_property, monkeypatch, tmp_path):
    """The starting pack holds every earlier record from record files, with no GitHub call.

    Saves a planner's record and then a plan review's record (whose run number is lower) to a stand-in logs branch,
    fakes an issue whose comments carry no record, and builds a worker's pack. Checks in/ holds both records in the
    order they were saved and plan.json is the plan; then builds the same pack on a repo with no logs branch yet and
    checks it holds no record and made the same GitHub calls, so reading the records cost none.

    Proves 610.2."""
    record_property("proves", "610.2")
    remote = bare_remote(tmp_path)
    save(tmp_path, remote, PLANNER, "out1", "610.2")
    save(tmp_path, remote, REVIEW, "out2", "610.2")
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", str(remote))
    calls = fake_github(monkeypatch)
    dest = tmp_path / "pack"
    has_plan = agent.pack(REPO, N, "worker", "", str(dest))
    got = packed(dest)
    assert len(got) == 2 and same(got[0], PLANNER) and same(got[1], REVIEW), \
        f"610.2: the pack should hold the planner's then the plan review's record, from the files; it holds " \
        f"{[(r.get('role'), r.get('stage')) for r in got]}"
    assert has_plan and json.load(open(dest / "plan.json")) == PLAN, "610.2: the pack's plan.json is not the saved plan"

    (tmp_path / "e").mkdir()
    empty = bare_remote(tmp_path / "e")
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", str(empty))
    calls_without = fake_github(monkeypatch)
    agent.pack(REPO, N, "worker", "", str(tmp_path / "pack-empty"))
    assert packed(tmp_path / "pack-empty") == [], "610.2: a pack for an issue with no record file holds records"
    assert calls == calls_without, \
        f"610.2: reading the record files made GitHub calls: {[c for c in calls if c not in calls_without]}"


def test_a_pack_that_cannot_read_the_record_files_fails_saying_why(record_property, monkeypatch, tmp_path):
    """A pack that cannot read the record files stops, saying why, never starting without history.

    Points the logs remote at a place that is not a git repo, so the record files cannot be fetched, and builds a
    worker's pack. Checks the pack fails with its own message naming the records, not a bare git or test error, so
    a run never treats unreadable records as none. Its good case is the test above: an empty logs remote packs fine.

    Proves 610.2."""
    record_property("proves", "610.2")
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", str(tmp_path / "missing.git"))
    fake_github(monkeypatch)
    dest = tmp_path / "pack"
    try:
        agent.pack(REPO, N, "worker", "", str(dest))
    except (subprocess.CalledProcessError, AssertionError) as e:
        raise AssertionError(f"610.2: an unreadable logs remote failed the pack without saying why: {e!r}") from e
    except Exception as e:
        assert "record" in str(e).lower(), f"610.2: the pack failed without naming the records: {e}"
        return
    raise AssertionError(f"610.2: the pack treated unreadable record files as no records, holding {len(packed(dest))}")


# 610.3 ---------------------------------------------------------------------------------------------------------------

def test_a_run_never_reads_a_record_from_a_comment(record_property, monkeypatch, tmp_path):
    """A record in the bot's comment counts for nothing: a run reads only record files.

    Fakes an issue whose bot comment carries a passed plan's JSON, the way records were posted until now, with no
    record file saved, and builds a plan review's starting pack. Checks the pack holds no record and no plan. Then
    saves the same record as a file and checks the pack holds it, so the pack does read records, only never from a
    comment. The card's own readers move to #613, as the owner decided on this issue.

    Proves 610.3."""
    record_property("proves", "610.3")
    remote = bare_remote(tmp_path)
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", str(remote))
    fake_github(monkeypatch, [bot_comment(PLANNER)])
    dest = tmp_path / "pack"
    agent.pack(REPO, N, "reviewer", "plan", str(dest))
    assert packed(dest) == [], "610.3: the pack read a record from the bot's comment"
    assert not (dest / "plan.json").exists(), "610.3: the pack took its plan from the bot's comment"
    save(tmp_path, remote, PLANNER, "out", "610.3")
    again = tmp_path / "pack-again"
    agent.pack(REPO, N, "reviewer", "plan", str(again))
    got = packed(again)
    assert len(got) == 1 and same(got[0], PLANNER), "610.3: with the record saved as a file, the pack still lacks it"


def test_an_edited_record_comment_changes_nothing_a_run_reads(record_property, monkeypatch, tmp_path):
    """Editing the bot's record comment by hand changes nothing the next run reads.

    Saves a planner's record as a file, then fakes the bot's comment for it edited by hand to say a different plan.
    Checks the pack holds the saved record and plan, never the edited one.

    Proves 610.3."""
    record_property("proves", "610.3")
    remote = bare_remote(tmp_path)
    save(tmp_path, remote, PLANNER, "out", "610.3")
    monkeypatch.setenv("DOKIMA_LOGS_REMOTE", str(remote))
    edited = {**PLANNER, "handback": {**PLAN, "summary": "Someone edited this record by hand."}}
    fake_github(monkeypatch, [bot_comment(edited)])
    dest = tmp_path / "pack"
    agent.pack(REPO, N, "reviewer", "plan", str(dest))
    got = packed(dest)
    assert len(got) == 1 and same(got[0], PLANNER), \
        f"610.3: the pack should hold only the saved record, holds {[r.get('handback', {}).get('summary') for r in got]}"
    assert json.load(open(dest / "plan.json")) == PLAN, "610.3: the pack's plan came from the edited comment"

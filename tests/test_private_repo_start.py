"""In a private repo every run after the first starts from the issue's branch (#914).

On a private repo origin refuses anonymous reads, and the "Starting branch" step of .github/workflows/agent.yml used to
read that refusal as "no branch yet". These tests run the real steps on the machine from test_start.py, with origin
refusing anonymous reads: only the app's key reaches it, as on GitHub.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_start as ts  # noqa: E402

# Origin as the checkout left it, with no key: on a private repo every anonymous ask fails.
REFUSE = {"name": "Origin refuses anonymous reads", "run": "git remote set-url origin file:///nonexistent/private.git\n"}
# The app's key no longer reaches origin either: GitHub itself could not be asked.
UNREACHABLE = {"name": "Origin cannot be reached", "run":
               'echo "GIT_CONFIG_KEY_0=url.file:///nonexistent/private.git.insteadOf" >> "$GITHUB_ENV"\n'}


class Private(ts.Machine):
    """Issue #57's branch on a private repo, with its test tests/test_x.py."""

    def __init__(self, tmp):
        super().__init__(tmp, [], try_branch=True)
        self.wf = ts.workflow("agent.yml")
        self.job = self.wf["jobs"]["run"]
        named = {s.get("name"): s for s in self.job["steps"]}
        self.head = [named["Dokima's code from Dokima's own repo"], named["Copy the runtime from main before touching any branch"]]
        self.start = [next(s for s in self.job["steps"] if s.get("id") == "start-key"), named["Starting branch"]]
        self.app = next(s for s in self.job["steps"] if s.get("id") == "app")
        self.push = next(s for s in self.job["steps"] if str(s.get("name", "")).startswith("Push the planner's tests"))

    def run_as(self, role, stage, steps, name):
        """Run the given steps of agent.yml for `role` on a fresh clone; the job's result."""
        t = self.tmp
        open(f"{t}/event.json", "w").write('{"inputs": {"role": "%s", "stage": "%s", "issue": "%s"}}' % (role, stage, ts.N))
        ctx = {"inputs": ts.Ctx(role=role, stage=stage, issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42", run_attempt="1",
                                server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        job = {**self.job, "env": {**(self.job.get("env") or {}), "PASSED": "true", "STARTED": "true"}, "steps": steps}
        self.failed_step = None
        result, _ = self.run_job(name, job, ctx, "workflow_dispatch",
                                 [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], self.wf.get("defaults"))
        return result

    def planner(self, k):
        """A planner round: it lists the tests it found, adds tests/test_round{k}.py, and pushes."""
        found = {"name": "The planner adds a test", "run":
                 f"ls tests > /tmp/found{k}.txt\nprintf 'def test_r():\\n    assert True\\n' > tests/test_round{k}.py\n"}
        return self.run_as("planner", "", self.head + [REFUSE] + self.start + [found, self.app, self.push], f"planner{k}")

    def found(self, k):
        path = f"{self.tmp}/found{k}.txt"
        return open(path).read().split() if os.path.exists(path) else None

    def tip(self):
        return ts.sh(f"{self.tmp}/origin.git", "git", "rev-parse", f"try/issue-{ts.N}")

    def why(self):
        path = f"{self.tmp}/why.txt"
        return open(path).read() if os.path.exists(path) else ""


def test_a_planner_rerun_starts_from_the_existing_branch_and_its_push_lands_on_top(tmp_path):
    m = Private(tmp_path)
    assert m.planner(1) == "success", f"the first planner run failed at {m.failed_step}:\n" + "\n".join(m.log)
    first = m.tip()
    assert first != m.try_sha, "the first planner run pushed nothing to try/issue-57"
    assert m.planner(2) == "success", f"the planner rerun failed at {m.failed_step}:\n" + "\n".join(m.log)
    assert m.found(2) == ["test_round1.py", "test_x.py"], f"the rerun did not start from try/issue-57; it found {m.found(2)}"
    tip = m.tip()
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", first, tip], cwd=f"{tmp_path}/origin.git").returncode
    assert tip != first and ancestor == 0, "the rerun's push did not land on top of the branch"
    files = ts.sh(f"{tmp_path}/origin.git", "git", "ls-tree", "--name-only", f"{tip}:tests").split()
    assert files == ["test_round1.py", "test_round2.py", "test_x.py"], f"the branch holds {files}"


def test_a_plan_review_sees_the_plans_tests(tmp_path):
    m = Private(tmp_path)
    look = {"name": "The reviewer looks", "run": "ls tests > /tmp/seen.txt\n"}
    assert m.run_as("reviewer", "plan", m.head + [REFUSE] + m.start + [look], "review") == "success", "\n".join(m.log)
    assert open(f"{tmp_path}/seen.txt").read().split() == ["test_x.py"], "the plan review did not see the plan's tests"


def test_a_remote_error_is_reported_not_taken_for_no_branch(tmp_path):
    m = Private(tmp_path)
    look = {"name": "The reviewer looks", "run": "touch /tmp/started\n"}
    result = m.run_as("reviewer", "plan", m.head + [REFUSE, UNREACHABLE] + m.start + [look], "review")
    assert result == "failure" and m.failed_step == "Starting branch", f"the run did not stop at its start: {m.failed_step}"
    assert not os.path.exists(f"{tmp_path}/started"), "the run went on from main after origin could not be asked"
    assert "could not" in m.why().lower() and "fake-token" not in m.why(), f"the run did not say why: {m.why()!r}"


def test_a_second_runs_conversation_lands_on_top_of_the_first_on_the_records_branch(tmp_path):
    """Saving the conversation reads the records branch with the app's key, not anonymously (#917)."""
    m = Private(tmp_path)
    save = next(s for s in m.job["steps"] if str(s.get("name", "")).startswith("Save the conversation"))
    logs = f"{tmp_path}/origin.git"
    tips = []
    for run in ("1", "2"):
        given = {"name": "The run so far", "run": "rm -rf /tmp/logs-branch\n"
                 f'printf "RECORDS_BRANCH=logs\\nLOG=logs/{ts.N}/{run}-planner.md\\n" >> "$GITHUB_ENV"\n'}
        result = m.run_as("planner", "", m.head + [REFUSE, given, m.app, save], f"save{run}")
        assert result == "success", f"run {run} failed at {m.failed_step}:\n" + "\n".join(m.log)
        said = "\n".join(m.log)
        assert "[rejected]" not in said, f"run {run} started the records branch fresh and its push was rejected:\n{said}"
        tips.append(ts.sh(logs, "git", "rev-parse", "logs"))
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", tips[0], tips[1]], cwd=logs).returncode
    assert tips[1] != tips[0] and ancestor == 0, "the second run's conversation did not land on top of the first"
    files = ts.sh(logs, "git", "ls-tree", "-r", "--name-only", "logs").split()
    assert {f"logs/{ts.N}/1-planner.md", f"logs/{ts.N}/2-planner.md"} <= set(files), f"the records branch holds {files}"


def test_a_records_branch_origin_cannot_be_asked_about_stops_the_save_and_says_why(tmp_path):
    m = Private(tmp_path)
    save = next(s for s in m.job["steps"] if str(s.get("name", "")).startswith("Save the conversation"))
    given = {"name": "The run so far", "run": f'printf "RECORDS_BRANCH=logs\\nLOG=logs/{ts.N}/1-planner.md\\n" >> "$GITHUB_ENV"\n'}
    result = m.run_as("planner", "", m.head + [REFUSE, UNREACHABLE, given, m.app, save], "save")
    assert result == "failure" and m.failed_step == save["name"], f"the save did not stop: {m.failed_step}"
    said = m.log[-1]
    assert "could not ask whether logs exists" in said and "fake-token" not in said, f"the save did not say why: {said}"

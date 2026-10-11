"""One play-through on the sandbox repo, judging both cards after every step (#437).

It plays a new issue to a merge.

    REPO=dokima-dev/card-gallery PLAYED=<folder> PLAYED_COMMIT=<sha> SANDBOX_TOKEN=... GH_TOKEN=... \
        python3 -m dokima.playthrough

Before the first step it installs the played commit on the sandbox: the dokima/ and .github/workflows/ files of the
PLAYED folder are pushed to the sandbox's default branch with SANDBOX_TOKEN, a key of the play-through's own that can
write only there, so the cards it judges are drawn by that commit's card.yml and dokima/card.py. Then it plays one
issue through STEPS. Stand-in agents call no model: each writes its role's hand-back and no model report, and the
played commit's own `dokima.agent record` turns it into the record posted on the sandbox. After each step it waits up
to PLAYTHROUGH_WAIT seconds for the sandbox's card runs, reads both cards and logs `PASS: <step>` or
`FAIL: <step>: ...` quoting what the wrong card showed. Every step is played even after one fails; the run exits 1
when any step failed, 0 when all passed. It refuses any repository but the sandbox before calling GitHub.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

SANDBOX = "dokima-dev/card-gallery"
STEPS = ("issue opened", "plan posted", "plan approved", "build started", "pull request opened",
         "code review started", "code review record posted", "merged")
# The steps an agent's record makes, and the stand-in that hands it back: role, stage and hand-back file.
STANDINS = {"plan posted": ("planner", ""), "plan approved": ("reviewer", "plan"),
            "pull request opened": ("worker", ""), "code review record posted": ("reviewer", "pr")}
HANDBACK = {"planner": "plan.json", "reviewer": "review.json", "worker": "work.json"}
WAIT = 600
POLL = 10
# How long after a step the sandbox is given to queue the card runs that step starts.
SETTLE = 15
STAGE = re.compile(r"^(?:<img[^>]*>\s*)?\*\*(Backlog|Plan|Work|Review|Merged)\*\*")


def card_of(text):
    """The card part of an issue or pull request body.

    It is the first card block, else everything above the ask."""
    text = text or ""
    if "<!-- dokima-card -->" in text:
        done = text.rsplit("<!-- dokima-done -->", 1)[1].strip().split("\n")[0] if "<!-- dokima-done -->" in text else ""
        return text.split("<!-- dokima-card -->", 1)[1].split("<!-- /dokima-card -->", 1)[0] + done
    return text.split("<!-- dokima-ask -->", 1)[0]


def shown(text):
    """What a card shows: its stage, its /work ask and Code review's state.

    Code review's state is read from its Definition of Done."""
    c = card_of(text)
    line = next((l for l in c.splitlines() if STAGE.match(l.strip())), "")
    stage = STAGE.match(line.strip()).group(1) if line else None
    done = next((l for l in c.splitlines() if "**Definition of Done:**" in l), "")
    part = next((p for p in done.split(" · ") if re.sub(r"<[^>]*>", "", p).strip().endswith("Code review")), "")
    alts = re.findall(r'alt="([^"]*)"', part)
    return {"stage": stage, "work": "/work" in line, "review": alts[0] if alts else None}


def quote(s, review):
    """What a card showed, in words.

    Its stage, and Code review's state at the review steps."""
    said = s["stage"] or "no stage"
    if s["work"]:
        said += " asking for /work"
    if review:
        said += f", Code review {s['review'] or 'missing'}"
    return said


def judge(step, issue, pr):
    """`PASS: <step>` when both cards show what `step` should, else a FAIL line.

    The FAIL line names the wrong card and quotes what it showed. Before the pull request only the issue card is judged; from it on, a missing PR card fails."""
    review = step in ("code review started", "code review record posted")
    cards = [("issue card", issue)] + ([("PR card", pr)] if STEPS.index(step) >= STEPS.index("pull request opened") else [])
    wrong = []
    for name, text in cards:
        if not text or not card_of(text).strip():
            wrong.append(f"the {name} is missing")
            continue
        s = shown(text)
        ok = {"issue opened": s["stage"] == "Backlog",
              "plan posted": s["stage"] == "Plan",
              "plan approved": s["stage"] == "Plan" and s["work"],
              "build started": s["stage"] == "Work" and not s["work"],
              "pull request opened": s["stage"] in ("Work", "Review"),
              "code review started": s["stage"] == "Review" and s["review"] == "running",
              "code review record posted": s["stage"] == "Review" and s["review"] == "passed",
              "merged": s["stage"] == "Merged"}[step]
        if not ok:
            wrong.append(f"the {name} showed {quote(s, review)}")
    return f"PASS: {step}" if not wrong else f"FAIL: {step}: " + "; ".join(wrong)


def wait_for_cards(step, pending, wait, poll):
    """None once `pending()` says no card run is left, else a FAIL line.

    The FAIL line names the step and the wait, once the card runs outlast it."""
    end = time.monotonic() + wait
    while pending():
        if time.monotonic() >= end:
            return f"FAIL: {step}: its card runs were still running after the wait of {wait:g} s"
        time.sleep(poll)
    return None


def standin(role, stage, out):
    """Write a stand-in agent's hand-back into `out`, calling no model.

    It writes its role's file and no model report, so its record shows no tokens."""
    if role == "planner":
        h = {"kind": "user_story", "summary": "The play-through's stand-in plan.",
             "user_story": "The owner sees the play-through's issue go from opened to merged.",
             "acceptance_criteria": [{"text": "The play-through's change is merged.", "source": "the play-through"}],
             "non_functional": [], "scope": ["playthrough/"], "out_of_scope": ["Everything else."], "tests": {},
             "raises": [], "answers": []}
    elif role == "worker":
        h = {"summary": "The stand-in worker added the play-through's file.", "criteria": {},
             "evidence": "No tests: a stand-in agent.", "raises": [], "answers": []}
    else:
        h = {"verdict": "approve", "summary": f"The stand-in {stage} review approves.", "blockers": [],
             "raises": [], "answers": []}
    with open(os.path.join(out, HANDBACK[role]), "w") as f:
        json.dump(h, f, indent=1)


def play(sandbox, wait, poll, log):
    """Install the played commit, then play every step on `sandbox`, logging one line each.

    After each step it waits for its card runs and judges both cards. Returns 1 when the install or any step failed, else 0."""
    try:
        sandbox.install()
    except Exception as e:
        log(f"FAIL: install: {e}")
        return 1
    failed = False
    for step in STEPS:
        out = tempfile.mkdtemp(prefix="standin-") if step in STANDINS else None
        try:
            if out:
                standin(*STANDINS[step], out)
            sandbox.do(step, out)
            line = wait_for_cards(step, sandbox.pending, wait, poll) or judge(step, *sandbox.cards())
        except Exception as e:
            line = f"FAIL: {step}: {e}"
        finally:
            if out:
                shutil.rmtree(out, ignore_errors=True)
        failed = failed or not line.startswith("PASS: ")
        log(line)
    return 1 if failed else 0


def install_files(played):
    """Every file of the played folder's dokima/ and .github/workflows/, with its content.

    Keyed by path relative to the folder."""
    files = {}
    for top in ("dokima", os.path.join(".github", "workflows")):
        for d, _, names in os.walk(os.path.join(played, top)):
            for n in names:
                if "__pycache__" in d or n.endswith(".pyc"):
                    continue
                path = os.path.join(d, n)
                with open(path, "rb") as f:
                    files[os.path.relpath(path, played).replace(os.sep, "/")] = f.read()
    return files


def run(*args, env=None, cwd=None):
    """Run one command; its output, or an error with what it said when it fails."""
    p = subprocess.run(list(args), capture_output=True, text=True, env=env, cwd=cwd)
    if p.returncode:
        said = (p.stderr or p.stdout).strip().splitlines()
        raise RuntimeError(f"{args[0]} failed: {said[-1] if said else f'exit {p.returncode}'}")
    return p.stdout


class Sandbox:
    """The sandbox on real GitHub, played with gh and git.

    gh acts with GH_TOKEN (the app's key for the sandbox only); git pushes with SANDBOX_TOKEN."""

    def __init__(self, repo, played, commit, token):
        self.repo, self.played, self.commit = repo, played, commit
        auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        self.git_auth = ["-c", f"http.extraheader=AUTHORIZATION: basic {auth}"]
        self.url = f"https://github.com/{repo}.git"
        self.work = tempfile.mkdtemp(prefix="playthrough-")
        self.clone = os.path.join(self.work, "sandbox")
        self.env = {k: v for k, v in os.environ.items() if k not in ("SANDBOX_TOKEN", "PLAYED", "PLAYED_COMMIT")}
        self.env.update(GITHUB_REPOSITORY=repo, GIT_TERMINAL_PROMPT="0")
        self.issue = self.pr = self.review_card = self.worker_card = None
        self.since = None

    def git(self, *args):
        return run("git", *self.git_auth, "-c", "user.name=dokima-playthrough",
                   "-c", "user.email=dokima-playthrough@users.noreply.github.com", *args, env=self.env, cwd=self.clone)

    def gh(self, *args):
        return run("gh", *args, env=self.env)

    def install(self):
        """Push the played commit's dokima/ and .github/workflows/ to the sandbox's default branch."""
        try:
            run("git", *self.git_auth, "clone", "-q", self.url, self.clone, env=self.env)
            for rel, data in install_files(self.played).items():
                path = os.path.join(self.clone, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
            self.git("add", "-A")
            if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=self.clone).returncode:
                self.git("commit", "-qm", f"Play-through installs Dokima {self.commit}")
                self.git("push", "-q", "origin", "HEAD")
            self.base = self.git("rev-parse", "HEAD").strip()
        except Exception as e:
            raise RuntimeError(f"Dokima {self.commit} could not be installed on {self.repo}: {e}")

    def record(self, role, stage, out):
        """The record the played commit's code writes for a stand-in's hand-back.

    It is written into `out`, as agent.yml would."""
        open(os.path.join(out, "check.txt"), "w").close()
        env = dict(self.env, PYTHONPATH=self.played, PYTHONSAFEPATH="1", PACK=os.path.join(self.work, "pack"),
                   N=str(self.issue), BASE=self.base)
        run(sys.executable, "-m", "dokima.agent", "record", role, stage, out, os.path.join(out, "check.txt"), "true",
            os.path.join(self.work, "no-logs"), env=env, cwd=self.clone)
        if role == "planner":
            os.makedirs(os.path.join(self.work, "pack"), exist_ok=True)
            shutil.copy(os.path.join(out, "plan.json"), os.path.join(self.work, "pack", "plan.json"))
        return os.path.join(out, "comment.md")

    def live(self, role, stage, state):
        """A run's live card, as the played commit draws it."""
        env = dict(self.env, PYTHONPATH=self.played, PYTHONSAFEPATH="1")
        return run(sys.executable, "-m", "dokima.agent", "card", role, stage, state, env=env)

    def comment(self, number, body):
        """Post a comment on issue or pull request `number`; its id."""
        return self.gh("api", "-X", "POST", f"repos/{self.repo}/issues/{number}/comments", "-f", f"body={body}",
                       "--jq", ".id").strip()

    def edit(self, cid, path):
        """Edit comment `cid` into the file at `path`, as a run's card becomes its record."""
        self.gh("api", "-X", "PATCH", f"repos/{self.repo}/issues/comments/{cid}", "-F", f"body=@{path}", "--silent")

    def do(self, step, handback):
        """Play one step on the sandbox, as the river does it.

    An agent's step gets the stand-in's hand-back."""
        self.since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if step == "issue opened":
            url = self.gh("issue", "create", "-R", self.repo, "--title", f"Play-through of Dokima {self.commit}",
                          "--body", f"The play-through's issue for Dokima {self.commit}.").strip()
            self.issue = int(url.rstrip("/").rsplit("/", 1)[1])
        elif step in ("plan posted", "plan approved"):
            self.gh("issue", "comment", str(self.issue), "-R", self.repo, "--body-file",
                    self.record(*STANDINS[step], handback))
        elif step == "build started":
            self.gh("issue", "comment", str(self.issue), "-R", self.repo, "--body", "Autopilot: plan approved, starting work")
            self.worker_card = self.comment(self.issue, self.live("worker", "", "working"))
        elif step == "pull request opened":
            branch = f"try/issue-{self.issue}"
            self.git("checkout", "-q", "-B", branch, self.base)
            os.makedirs(os.path.join(self.clone, "playthrough"), exist_ok=True)
            with open(os.path.join(self.clone, "playthrough", f"{self.issue}.md"), "w") as f:
                f.write(f"Played Dokima {self.commit} on issue #{self.issue}.\n")
            self.git("add", "-A")
            self.git("commit", "-qm", f"worker for #{self.issue}")
            self.git("push", "-q", "origin", f"HEAD:{branch}")
            url = self.gh("pr", "create", "-R", self.repo, "--head", branch, "--title",
                          f"Play-through of Dokima {self.commit}", "--body", f"Closes #{self.issue}").strip()
            self.pr = int(url.rstrip("/").rsplit("/", 1)[1])
            self.edit(self.worker_card, self.record("worker", "", handback))
        elif step == "code review started":
            self.review_card = self.comment(self.pr, self.live("reviewer", "pr", "queued"))
        elif step == "code review record posted":
            self.edit(self.review_card, self.record("reviewer", "pr", handback))
        elif step == "merged":
            self.gh("pr", "merge", str(self.pr), "-R", self.repo, "--merge")
        time.sleep(SETTLE)

    def pending(self):
        """How many card runs started since the newest step are still queued or running."""
        return int(self.gh("api", f"repos/{self.repo}/actions/runs?created=%3E%3D{self.since}&per_page=100", "--jq",
                           '[.workflow_runs[] | select(.name == "card" and .status != "completed")] | length').strip() or 0)

    def cards(self):
        """The issue's body and its pull request's, None while there is no pull request."""
        issue = self.gh("api", f"repos/{self.repo}/issues/{self.issue}", "--jq", ".body")
        pr = self.gh("api", f"repos/{self.repo}/pulls/{self.pr}", "--jq", ".body") if self.pr else None
        return issue, pr


def main():
    repo = os.environ.get("REPO", "")
    if repo != SANDBOX:
        print(f"The play-through runs only on {SANDBOX}, not {repo or 'no repository'}: it stopped before calling GitHub.",
              file=sys.stderr)
        return 2
    played = os.environ.get("PLAYED", "")
    if not os.path.isdir(os.path.join(played, "dokima")):
        print(f"The played folder {played or '(PLAYED is not set)'} holds no dokima/ folder, so there is no Dokima to play.",
              file=sys.stderr)
        return 2
    commit = os.environ.get("PLAYED_COMMIT", "") or "(PLAYED_COMMIT is not set)"
    token = os.environ.get("SANDBOX_TOKEN", "")
    if not token:
        print(f"FAIL: install: SANDBOX_TOKEN is missing or empty, so Dokima {commit} cannot be pushed to {SANDBOX}; "
              "add it to the keys environment.", flush=True)
        return 1
    wait = float(os.environ.get("PLAYTHROUGH_WAIT") or WAIT)
    return play(Sandbox(repo, played, commit, token), wait, POLL, lambda line: print(line, flush=True))


if __name__ == "__main__":
    sys.exit(main())

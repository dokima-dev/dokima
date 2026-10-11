"""The sandbox play-through checks both cards after every step, from new issue to merge (#437).

#419: the code review had passed, yet the card said Code review running for 30 minutes. The review's record is the
bot's edit of its live run card, and card.yml skips every edit the bot makes, so nothing redrew the card. The fake
GitHub of tests/card_player.py plays card.yml one event at a time, but only a run on real GitHub proves what the owner
sees. So `python3 -m dokima.playthrough`, started by .github/workflows/playthrough.yml's Run workflow button, plays
one issue on dokima-dev/card-gallery with stand-in agents that call no model, and judges both cards after each step.

These tests run with no GitHub and no key. They prove the parts that decide the verdict: the steps in order, the
judge of each step's cards (drawn by dokima/card.py), the #419 moment replayed through today's card.yml, the wait
that fails a hung step, the guard that keeps the play-through on the sandbox, the stand-in agents' empty usage, and
the workflow's button, key and permissions.
"""
import ast
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from card_player import OWNER, Hub, issue_comment, must_redraw, pr_comment, record, review_record  # noqa: E402
from test_card_running import REPO, built, items_of, live, rec, review_queued  # noqa: E402
from test_start import load_yaml  # noqa: E402
from dokima import agent, body, card  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "playthrough.yml")
SANDBOX = "dokima-dev/card-gallery"
SANDBOX_TOKEN = "sandbox-token-only-for-card-gallery-7f3e"
STEPS = ("issue opened", "plan posted", "plan approved", "build started", "pull request opened",
         "code review started", "code review record posted", "merged")


def playthrough(k):
    """The play-through module; fails naming criterion k when it does not exist yet."""
    try:
        from dokima import playthrough as p
    except ImportError as e:
        raise AssertionError(f"{k}: dokima/playthrough.py does not exist yet, so there is no play-through: {e}")
    return p


def draw(steps, page="issue", pr=True, merged=False):
    """The card dokima/card.py draws for issue #1 after `steps` (records, owner words and live cards)."""
    items = items_of(steps)
    found = {"recs": agent.records(items), "items": items,
             "pr": {"number": 5, "merged": merged, "state": "closed" if merged else "open"} if pr else None,
             "check_runs": [], "reviews": [], "owners": {OWNER}, "tests": {}, "worker": None, "children": []}
    os.environ.setdefault("GITHUB_REPOSITORY", REPO)
    return card.render(REPO, {"number": 1, "url": f"https://github.com/{REPO}/issues/1"}, found, page)


def issue_body(card_text):
    """An issue body with this card above the marker and the owner's ask below it."""
    return f"{card_text}\n\n{body.MARKER}\n\nThe owner's ask."


def pr_body(card_text):
    """A pull request body with this card and its closing line."""
    return f"{card_text}\n\nCloses #1"


def as_work(card_text):
    """The approved plan's card as it should read once its build started."""
    out = []
    for line in card_text.splitlines():
        out.append("**Work**" if re.match(r"\*\*Plan\*\*", line) else line)
    text = "\n".join(out)
    assert "**Work**" in text and "/work" not in text, "test setup: the approved card has no **Plan** status line"
    return text


def right_cards():
    """For every step, the issue and PR bodies that show it."""
    b = built()
    approve = rec("reviewer", "pr", verdict="approve", blockers=[])
    return {
        "issue opened": (issue_body(draw([], pr=False)), None),
        "plan posted": (issue_body(draw(b[:1], pr=False)), None),
        "plan approved": (issue_body(draw(b[:2], pr=False)), None),
        "build started": (issue_body(as_work(draw(b[:2], pr=False))), None),
        "pull request opened": (issue_body(draw(b)), pr_body(draw(b, "pr"))),
        "code review started": (issue_body(draw(b + [live("reviewer", "pr", "working")])),
                                pr_body(draw(b + [live("reviewer", "pr", "working")], "pr"))),
        "code review record posted": (issue_body(draw(b + [live("reviewer", "pr", "working"), approve])),
                                      pr_body(draw(b + [live("reviewer", "pr", "working"), approve], "pr"))),
        "merged": (issue_body(draw(b + [approve], merged=True)), pr_body(draw(b + [approve], "pr", merged=True))),
    }


def test_the_play_through_plays_every_step_from_a_new_issue_to_a_merge_in_order(record_property):
    """The play-through plays every step from a new issue to a merge, in order.

    Proves 437.1.
    Reads dokima/playthrough.py's STEPS and checks it holds exactly these steps in this order: issue opened, plan
    posted, plan approved, build started, pull request opened, code review started, code review record posted,
    merged. A missing, extra or reordered step turns it red."""
    record_property("proves", "437.1")
    p = playthrough("437.1")
    got = tuple(getattr(p, "STEPS", ()))
    assert got == STEPS, f"437.1: the play-through's steps should be {STEPS}, in that order, not {got}"


def test_each_step_passes_only_when_both_cards_show_what_it_should(record_property):
    """A step passes only when both cards show it, and fails quoting what they showed.

    Proves 437.1.
    Draws with dokima/card.py the issue and PR cards each step should leave, and checks judge() gives
    `PASS: <step>` for them. Then gives every step the cards the step before it left (the card not redrawn), and a
    missing PR card from the pull request onwards, and checks each gives a line starting `FAIL: <step>` that names
    what the card showed. A right issue card beside a stale PR card fails too, so both cards are checked."""
    record_property("proves", "437.1")
    p = playthrough("437.1")
    right = right_cards()
    for step in STEPS:
        line = p.judge(step, *right[step])
        assert line == f"PASS: {step}", f"437.1: at {step!r}, cards that show that step should give 'PASS: {step}', not {line!r}"
    stale = {"issue opened": ("**Plan**", right["plan posted"]),
             "plan posted": ("Backlog", right["issue opened"]),
             "plan approved": ("Plan", right["plan posted"]),
             "build started": ("Plan", right["plan approved"]),
             "pull request opened": ("PR", (right["pull request opened"][0], None)),
             "code review started": ("Code review not started", right["pull request opened"]),
             "code review record posted": ("Code review running", right["code review started"]),
             "merged": ("Review", right["code review record posted"])}
    for step, (shown, cards) in stale.items():
        line = p.judge(step, *cards)
        assert line.startswith(f"FAIL: {step}"), \
            f"437.1: at {step!r}, cards left from the step before should give a line starting 'FAIL: {step}', not {line!r}"
        assert shown.strip("*") in line, f"437.1: the FAIL line at {step!r} should say the card showed {shown!r}: {line!r}"
    issue_ok, _ = right["code review record posted"]
    _, pr_stale = right["code review started"]
    line = p.judge("code review record posted", issue_ok, pr_stale)
    assert line.startswith("FAIL: code review record posted") and "PR" in line, \
        f"437.1: a stale PR card beside a right issue card should fail naming the PR card: {line!r}"


def workflow(k):
    """.github/workflows/playthrough.yml as nested dicts; fails naming criterion k when it does not exist."""
    assert os.path.exists(WORKFLOW), f"{k}: .github/workflows/playthrough.yml does not exist, so there is no play-through to start"
    return load_yaml(open(WORKFLOW).read())


def steps_of(wf):
    """Every step of every job in the workflow."""
    return [s for job in (wf.get("jobs") or {}).values() for s in (job.get("steps") or [])]


def test_the_run_workflow_button_starts_the_play_through_for_a_given_dokima_commit(record_property):
    """The Run workflow button starts the play-through for a given Dokima commit.

    Proves 437.3.
    Reads .github/workflows/playthrough.yml and checks it starts on workflow_dispatch with a required `commit` input,
    checks that commit out into a folder of its own, and runs `python3 -m dokima.playthrough` with PLAYED naming
    that folder and PLAYED_COMMIT the commit, so the play-through knows what to install on the sandbox. That job
    opens the keys environment and hands the play-through the SANDBOX_TOKEN secret as SANDBOX_TOKEN, the key it
    installs with."""
    record_property("proves", "437.3")
    wf = workflow("437.3")
    on = wf.get("on") or {}
    dispatch = on.get("workflow_dispatch") if isinstance(on, dict) else None
    assert isinstance(on, dict) and "workflow_dispatch" in on, "437.3: playthrough.yml does not start on workflow_dispatch"
    commit = ((dispatch or {}).get("inputs") or {}).get("commit") or {}
    assert str(commit.get("required")).lower() == "true", "437.3: the Run workflow button has no required `commit` input"
    steps = steps_of(wf)
    played = [s for s in steps if "actions/checkout" in str(s.get("uses"))
              and "inputs.commit" in str((s.get("with") or {}).get("ref")) and (s.get("with") or {}).get("path")]
    assert played, "437.3: no checkout step checks out `inputs.commit` into a folder of its own"
    runs = [s for s in steps if "python3 -m dokima.playthrough" in str(s.get("run"))]
    assert runs, "437.3: no step runs `python3 -m dokima.playthrough`"
    folders = {str(s["with"]["path"]).strip("./") for s in played}
    for s in runs:
        job = next(j for j in wf["jobs"].values() if s in (j.get("steps") or []))
        envname = job.get("environment")
        envname = envname.get("name") if isinstance(envname, dict) else envname
        assert envname == "keys", f"437.3: the job that runs the play-through opens environment {envname!r}, not keys, so SANDBOX_TOKEN is not there"
        env = {**(wf.get("env") or {}), **(job.get("env") or {}), **(s.get("env") or {})}
        assert re.fullmatch(r"\$\{\{\s*secrets\.SANDBOX_TOKEN\s*\}\}", str(env.get("SANDBOX_TOKEN", "")).strip()), \
            f"437.3: the play-through is not handed the SANDBOX_TOKEN secret as SANDBOX_TOKEN: {env.get('SANDBOX_TOKEN')!r}"
        assert str(env.get("PLAYED", "")).replace("${{ github.workspace }}", "").strip("./") in folders, \
            f"437.3: the play-through is not told the played commit's folder: PLAYED is {env.get('PLAYED')!r}, the checkout is in {sorted(folders)}"
        assert "inputs.commit" in str(env.get("PLAYED_COMMIT")), \
            f"437.3: the play-through is not told the played commit: PLAYED_COMMIT is {env.get('PLAYED_COMMIT')!r}"


def test_the_stand_in_agents_call_no_model_and_their_records_show_no_tokens(tmp_path, record_property):
    """The run holds no model key, and the stand-in agents' records show no tokens.

    Proves 437.4.
    Reads playthrough.yml: no model key or model CLI anywhere, and DOKIMA_APP_KEY and SANDBOX_TOKEN its only secrets. Then writes each
    stand-in agent's hand-back with dokima/playthrough.py's standin() and checks it holds the role's JSON file and
    no claude.json, so the record's footnote, drawn by dokima/agent.py, shows no tokens."""
    record_property("proves", "437.4")
    text = open(WORKFLOW).read() if os.path.exists(WORKFLOW) else ""
    assert text, "437.4: .github/workflows/playthrough.yml does not exist"
    for word in ("anthropic", "claude", "openai"):
        assert word not in text.lower(), f"437.4: playthrough.yml mentions {word!r}, so the run may hold a model key or call a model"
    secrets = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", text))
    assert secrets == {"DOKIMA_APP_KEY", "SANDBOX_TOKEN"}, \
        f"437.4: playthrough.yml should hold only DOKIMA_APP_KEY and SANDBOX_TOKEN, not {sorted(secrets)}"
    p = playthrough("437.4")
    for role, stage, name in (("planner", "", "plan.json"), ("reviewer", "plan", "review.json"),
                              ("worker", "", "work.json"), ("reviewer", "pr", "review.json")):
        out = tmp_path / f"{role}-{stage or 'none'}"
        out.mkdir()
        p.standin(role, stage, str(out))
        assert (out / name).exists(), f"437.4: the stand-in {role} {stage} wrote no {name}"
        json.load(open(out / name))
        assert not (out / "claude.json").exists(), f"437.4: the stand-in {role} {stage} left a model report (claude.json)"
        foot = agent.footnote({"role": role, "report": agent.run_report(str(out / "claude.json")), "run": "x"})
        assert "tokens" not in foot, f"437.4: the stand-in {role} {stage}'s record shows tokens: {foot}"


KEPT = {
    "test_card_queue.py": [
        "test_every_redraw_about_an_issue_or_its_pr_waits_in_a_queue_of_its_own_that_keeps_the_newest",
        "test_a_redraw_for_one_issue_never_shares_a_queue_with_another_issue_or_the_sweep",
    ],
    "test_card_running.py": [
        "test_code_review_shows_running_from_its_queued_card_until_its_record",
        "test_all_tests_shows_running_once_the_full_suite_starts",
        "test_the_code_reviews_queued_card_redraws_the_issue_and_pr_cards",
        "test_the_redraw_on_the_queued_card_waits_in_the_issues_own_queue",
    ],
    "test_card_sweep.py": [
        "test_the_sweep_redraws_every_stale_card_updated_since_the_last_sweep_open_or_closed",
        "test_an_issue_updated_since_the_last_sweep_gets_its_pr_card_redrawn_too",
        "test_a_card_that_already_shows_its_state_is_not_rewritten",
        "test_the_sweep_only_looks_at_issues_and_prs_updated_since_the_last_sweep",
        "test_a_failed_sweep_does_not_count_as_the_last_sweep",
        "test_only_a_scheduled_sweep_counts_as_the_last_sweep",
        "test_a_change_made_while_the_last_sweep_ran_is_not_missed",
        "test_when_github_cannot_say_what_changed_every_card_is_rechecked",
        "test_with_no_sweep_that_succeeded_yet_every_card_is_rechecked",
        "test_the_sweep_names_a_card_it_cannot_redraw_fails_and_puts_the_rest_right",
    ],
    "test_parent_sweep.py": [
        "test_the_sweep_closes_an_open_parent_whose_sub_issues_are_all_closed",
        "test_the_sweep_counts_a_sub_issue_closed_as_not_planned_as_done",
        "test_the_sweep_closes_one_level_up_in_turn",
        "test_the_sweep_leaves_a_closed_parent_alone_and_closes_nothing_twice",
    ],
}


def test_all_tests_keep_every_fake_github_card_check(record_property):
    """All tests keep every fake-GitHub card check of tests/card_player.py.

    Proves 437.5.
    Checks tests/card_player.py is still there, and that each of the 20 tests that play card.yml with it is still
    defined in its file, which still imports card_player, now that dokima/playthrough.py stands beside them."""
    record_property("proves", "437.5")
    playthrough("437.5")
    assert os.path.exists(os.path.join(ROOT, "tests", "card_player.py")), "437.5: tests/card_player.py was removed"
    for name, tests in KEPT.items():
        path = os.path.join(ROOT, "tests", name)
        assert os.path.exists(path), f"437.5: tests/{name}, a fake-GitHub card check, was removed"
        text = open(path).read()
        assert "card_player" in text, f"437.5: tests/{name} no longer plays card.yml with tests/card_player.py"
        defined = {n.name for n in ast.walk(ast.parse(text)) if isinstance(n, ast.FunctionDef)}
        for t in tests:
            assert t in defined, f"437.5: the fake-GitHub card check tests/{name}::{t} was removed"


def test_the_key_is_minted_for_the_sandbox_repo_only(record_property):
    """The app token the play-through holds is minted for dokima-dev/card-gallery alone.

    Proves 437.6.
    Reads playthrough.yml: every app token step names owner dokima-dev and repositories card-gallery and nothing else,
    there is at least one, none asks for permission to write workflows (Dokima's app never gets it; the install uses
    SANDBOX_TOKEN), and the workflow's own GitHub token may write nothing."""
    record_property("proves", "437.6")
    wf = workflow("437.6")
    tokens = [s for s in steps_of(wf) if "create-github-app-token" in str(s.get("uses"))]
    assert tokens, "437.6: playthrough.yml mints no app token, so it cannot act on the sandbox"
    for s in tokens:
        w = s.get("with") or {}
        assert w.get("owner") == "dokima-dev", f"437.6: an app token step does not name owner dokima-dev: {w}"
        repos = [r.strip() for r in re.split(r"[,\n]", str(w.get("repositories") or "")) if r.strip()]
        assert repos == ["card-gallery"], f"437.6: an app token is minted for {repos or 'every repository'}, not card-gallery only"
        asks = {k: v for k, v in w.items() if "workflow" in str(k).lower()}
        assert not asks, f"437.6: an app token asks for workflow permissions {asks}, but Dokima's app never gets workflow write"
    perms = [wf.get("permissions")] + [j.get("permissions") for j in (wf.get("jobs") or {}).values()]
    for p in perms:
        if isinstance(p, dict):
            assert "write" not in p.values(), f"437.6: playthrough.yml's own token may write: {p}"
        else:
            assert p in (None, "read-all", "{}"), f"437.6: playthrough.yml's own token has permissions {p!r}"
    assert wf.get("permissions") is not None, "437.6: playthrough.yml sets no permissions, so its own token gets the defaults"


FAKE_TOOL = """
import base64, json, os, re, sys
TOKEN = {token!r}
said = sys.argv[1:] + [v for k, v in os.environ.items() if k != "SANDBOX_TOKEN"]
def carries(text):
    if not TOKEN:
        return False
    if TOKEN in text:
        return True
    for chunk in re.findall(r"[A-Za-z0-9+/=_-]{{16,}}", text):
        try:
            if TOKEN in base64.b64decode(chunk + "=" * (-len(chunk) % 4), altchars=b"-_" if "-" in chunk or "_" in chunk else None).decode("utf-8", "replace"):
                return True
        except Exception:
            pass
    return False
with open({calls!r}, "a") as f:
    f.write(json.dumps({{"argv": [{tool!r}] + sys.argv[1:], "sandbox_token": any(carries(x) for x in said)}}) + "\\n")
sys.stderr.write("HTTP 403: refused by the fake GitHub\\n")
sys.exit(1)
"""


def run_playthrough(tmp_path, repo, played=ROOT, commit="f7340db", sandbox_token=SANDBOX_TOKEN, with_calls=False):
    """Run the play-through for `repo` with gh and git faked; return the result and calls.

    The fake gh and git log their arguments, and whether the call carries the sandbox token (in its arguments or
    environment, as is or base64-encoded as git's auth header is; the SANDBOX_TOKEN variable every call inherits does
    not count), then fail every call, as a GitHub that refuses
    everything. `sandbox_token` None leaves SANDBOX_TOKEN unset. Calls come back as argument lists, or as the logged
    records when `with_calls` is set."""
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    calls = tmp_path / "calls.jsonl"
    for tool in ("gh", "git"):
        f = bin_ / tool
        f.write_text(f"#!{sys.executable}\n" + FAKE_TOOL.format(token=sandbox_token or "", calls=str(calls), tool=tool))
        f.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "GH_", "SANDBOX_"))}
    env.update(PATH=f"{bin_}{os.pathsep}{env.get('PATH', '')}", REPO=repo, GH_TOKEN="fake", PLAYED=str(played), PLAYED_COMMIT=commit,
               PLAYTHROUGH_WAIT="3", GIT_TERMINAL_PROMPT="0", PYTHONPATH=ROOT)
    if sandbox_token is not None:
        env["SANDBOX_TOKEN"] = sandbox_token
    out = subprocess.run([sys.executable, "-m", "dokima.playthrough"], cwd=str(tmp_path), env=env,
                         capture_output=True, text=True, timeout=120)
    made = [json.loads(l) for l in calls.read_text().splitlines()] if calls.exists() else []
    return out, (made if with_calls else [c["argv"] for c in made])


def test_the_play_through_touches_only_the_sandbox_repo(tmp_path, record_property):
    """The play-through refuses any repo but dokima-dev/card-gallery before calling GitHub.

    Proves 437.7.
    Runs `python3 -m dokima.playthrough` with REPO=dokima-dev/dokima, gh and git faked: it exits non-zero naming
    dokima-dev/dokima and makes no gh or git call. With REPO=dokima-dev/card-gallery it does call out, every call
    naming card-gallery and none dokima-dev/dokima."""
    record_property("proves", "437.7")
    playthrough("437.7")
    (tmp_path / "real").mkdir()
    out, made = run_playthrough(tmp_path / "real", "dokima-dev/dokima")
    said = out.stdout + out.stderr
    assert out.returncode != 0, f"437.7: the play-through ran on dokima-dev/dokima (exit 0): {said[-1000:]}"
    assert "dokima-dev/dokima" in said, f"437.7: refusing dokima-dev/dokima, the play-through should name it: {said[-1000:]}"
    assert made == [], f"437.7: given dokima-dev/dokima, the play-through still called {made[:3]}"
    (tmp_path / "sandbox").mkdir()
    out, made = run_playthrough(tmp_path / "sandbox", SANDBOX)
    said = out.stdout + out.stderr
    assert made, f"437.7: given {SANDBOX}, the play-through made no gh or git call: {said[-1000:]}"
    assert any("card-gallery" in " ".join(c) for c in made), f"437.7: no call names card-gallery: {made[:5]}"
    for c in made:
        assert "dokima-dev/dokima" not in " ".join(c), f"437.7: a call reaches dokima-dev/dokima: {c}"


def test_a_step_whose_card_runs_do_not_finish_in_time_fails_naming_the_step_and_the_wait(record_property):
    """A step whose card runs outlast the fixed wait fails, naming the step and wait.

    Proves 437.8.
    Calls dokima/playthrough.py's wait_for_cards() with card runs that never finish and a 1 s wait: it must come back
    within a few seconds with `FAIL: plan posted` and `1 s`. Runs that finish give None at once."""
    record_property("proves", "437.8")
    p = playthrough("437.8")
    start = time.monotonic()
    got = p.wait_for_cards("plan posted", lambda: 1, 1, 0.1)
    took = time.monotonic() - start
    assert took < 10, f"437.8: with a 1 s wait, wait_for_cards() took {took:.0f} s, so a hung run hangs the play-through"
    assert isinstance(got, str) and got.startswith("FAIL: plan posted") and "1 s" in got, \
        f"437.8: card runs still running after the 1 s wait should fail naming the step and the wait, not {got!r}"
    left = iter([2, 1, 0])
    assert p.wait_for_cards("plan posted", lambda: next(left, 0), 5, 0.01) is None, \
        "437.8: card runs that finish within the wait should let the step go on (None)"


STANDINS = {"plan posted": ("planner", "", "plan.json"), "plan approved": ("reviewer", "plan", "review.json"),
            "pull request opened": ("worker", "", "work.json"),
            "code review record posted": ("reviewer", "pr", "review.json")}


class FakeSandbox:
    """A fake sandbox for play() that logs calls and shows each step's right cards.

    After each step it shows the cards that step should leave.
    `stale` names steps whose cards stay as the step before left them; `hung` names steps whose card runs never
    finish; `refuse` is the reason the sandbox refuses to install the played commit. Card runs of every other step
    finish on the second look. Each hand-back folder play() passes is read
    at once, before play() may remove it."""

    def __init__(self, stale=(), hung=(), refuse=None):
        self.right = right_cards()
        self.refuse = refuse
        self.stale, self.hung = set(stale), set(hung)
        self.calls, self.step, self.looks, self.handbacks = [], None, 0, {}

    def install(self):
        """Install the played commit on the fake sandbox; raises when the sandbox refuses it."""
        self.calls.append(("install", None))
        if self.refuse:
            raise RuntimeError(self.refuse)

    def do(self, step, handback):
        """Play one step on the fake sandbox, noting the stand-in hand-back it was given."""
        self.calls.append(("do", step))
        self.step, self.looks = step, 0
        if handback is not None:
            self.handbacks[step] = {"files": sorted(os.listdir(handback)),
                                    "report": agent.run_report(os.path.join(handback, "claude.json"))}
            for name in os.listdir(handback):
                if name.endswith(".json") and name != "claude.json":
                    json.load(open(os.path.join(handback, name)))
        else:
            self.handbacks[step] = None

    def pending(self):
        """How many card runs of the newest step are still queued or running."""
        self.calls.append(("pending", self.step))
        self.looks += 1
        return 1 if self.step in self.hung or self.looks < 2 else 0

    def cards(self):
        """The issue and PR bodies as they stand after the newest step."""
        self.calls.append(("cards", self.step))
        i = STEPS.index(self.step)
        return self.right[STEPS[i - 1] if self.step in self.stale and i else self.step]


def play(p, sandbox, k):
    """Run p.play() on a fake sandbox with a 1 s wait; return code and lines."""
    lines = []
    start = time.monotonic()
    code = p.play(sandbox, 1, 0.01, lines.append)
    took = time.monotonic() - start
    assert took < 30, f"{k}: play() took {took:.0f} s on a fake sandbox with a 1 s wait"
    return code, lines


def test_one_run_plays_every_step_waits_judges_both_cards_and_logs_one_line_each(record_property):
    """One run plays all eight steps, waiting, checking both cards and logging a line each.

    Proves 437.1.
    Runs dokima/playthrough.py's play() on a fake sandbox whose cards always show the step just played: it must
    play the eight steps in order, after each look at the card runs until they finish and then read the cards before
    the next step, log exactly `PASS: <step>` for each in order, and return 0. Then, with the cards of plan approved
    and code review record posted left stale, it must still play all eight steps, log `FAIL: <step>` for those two
    and PASS for the rest, and return 1, so one failure never stops the run."""
    record_property("proves", "437.1")
    p = playthrough("437.1")
    hub = FakeSandbox()
    code, lines = play(p, hub, "437.1")
    done = [s for kind, s in hub.calls if kind == "do"]
    assert done == list(STEPS), f"437.1: play() should play the eight steps in order, not {done}"
    for i, step in enumerate(STEPS):
        mine = [kind for kind, s in hub.calls if s == step]
        assert mine[0] == "do" and "pending" in mine and mine[-1] == "cards" and mine.index("pending") < mine.index("cards"), \
            f"437.1: at {step!r}, play() should play it, wait for its card runs, then read both cards: {mine}"
        assert mine.count("pending") >= 2, f"437.1: at {step!r}, play() read the cards before its card runs finished"
    assert lines == [f"PASS: {s}" for s in STEPS], \
        f"437.1: with every card right, play() should log one PASS line per step in order, not {lines}"
    assert code == 0, f"437.1: with every step passing, play() should return 0, not {code!r}"
    hub = FakeSandbox(stale=("plan approved", "code review record posted"))
    code, lines = play(p, hub, "437.1")
    assert [s for kind, s in hub.calls if kind == "do"] == list(STEPS), \
        "437.1: after a failed step, play() should still play every step to the end"
    assert len(lines) == len(STEPS), f"437.1: play() should log one line per step, not {lines}"
    for step, line in zip(STEPS, lines):
        want = "FAIL: " if step in hub.stale else "PASS: "
        assert line.startswith(want + step), f"437.1: at {step!r}, play() should log a line starting {want + step!r}, not {line!r}"
    assert code == 1, f"437.1: with two failed steps, play() should return 1, not {code!r}"


def test_the_run_plays_its_agent_steps_with_stand_ins_that_leave_no_token_report(record_property):
    """The run hands its agent steps the stand-ins' hand-backs, each with no model report.

    Proves 437.4.
    Runs play() on a fake sandbox and checks each agent step (plan posted, plan approved, pull request opened, code
    review record posted) is played with a hand-back folder holding its role's file and no claude.json, so its
    record shows no tokens, and that every other step is played with no hand-back."""
    record_property("proves", "437.4")
    p = playthrough("437.4")
    hub = FakeSandbox()
    play(p, hub, "437.4")
    for step in STEPS:
        got = hub.handbacks.get(step, "never played")
        if step in STANDINS:
            role, stage, name = STANDINS[step]
            assert isinstance(got, dict), f"437.4: {step!r} was played with no stand-in {role} {stage} hand-back: {got!r}"
            assert name in got["files"], f"437.4: the stand-in {role} {stage} hand-back at {step!r} holds no {name}: {got['files']}"
            assert "claude.json" not in got["files"] and not got["report"], \
                f"437.4: the stand-in {role} {stage} at {step!r} left a model report, so its record shows tokens"
        else:
            assert got is None, f"437.4: {step!r} needs no agent, yet play() handed it {got!r}"


def test_a_hung_step_fails_the_run_naming_the_wait_and_the_run_plays_on(record_property):
    """A hung step fails naming the step and the wait, and the run plays on.

    Proves 437.8.
    Runs play() with a 1 s wait on a fake sandbox whose card runs never finish after code review started: the line
    for that step must start `FAIL: code review started` and name `1 s`, the steps after it must still be played
    and pass, and play() must return 1 within seconds."""
    record_property("proves", "437.8")
    p = playthrough("437.8")
    hub = FakeSandbox(hung=("code review started",))
    code, lines = play(p, hub, "437.8")
    assert len(lines) == len(STEPS), f"437.8: play() should log one line per step, not {lines}"
    hung = lines[STEPS.index("code review started")]
    assert hung.startswith("FAIL: code review started") and "1 s" in hung, \
        f"437.8: a step whose card runs outlast the 1 s wait should fail naming it and the wait, not {hung!r}"
    assert [s for kind, s in hub.calls if kind == "do"] == list(STEPS), "437.8: after a hung step, play() should play on"
    assert lines[-2:] == ["PASS: code review record posted", "PASS: merged"], \
        f"437.8: the steps after the hung one should still pass: {lines[-2:]}"
    assert code == 1, f"437.8: a hung step should make play() return 1, not {code!r}"


def test_the_play_through_installs_the_played_commit_on_the_sandbox_before_the_first_step(tmp_path, record_property):
    """Before the first step, the play-through puts the played commit's Dokima on the sandbox.

    Proves 437.3.
    card.yml always runs the default branch's copy of itself and of dokima/card.py, so the cards on card-gallery are
    drawn by the commit played only once that commit is installed there. Checks install_files() picks every file of
    the played folder's dokima/ and .github/workflows/, with its content, and nothing else; that play() installs
    before it plays any step; that a refused install plays no step and returns 1 with one `FAIL: install` line giving
    the reason; that a played folder with no dokima/ fails naming it before any gh or git call; that a real run
    on the sandbox pushes with SANDBOX_TOKEN and, when GitHub refuses, exits 1 naming the commit and plays no step;
    and that with SANDBOX_TOKEN unset or empty, as GitHub gives a secret that does not exist, the run makes no gh or
    git call, logs one `FAIL: install` line naming SANDBOX_TOKEN, plays no step and exits 1."""
    record_property("proves", "437.3")
    p = playthrough("437.3")
    played = tmp_path / "played"
    for rel, text in (("dokima/card.py", "CARD of the played commit"), ("dokima/icons/x.svg", "<svg/>"),
                      (".github/workflows/card.yml", "name: card of the played commit"),
                      ("tests/test_a.py", "def test_a(): pass"), ("README.md", "readme")):
        (played / rel).parent.mkdir(parents=True, exist_ok=True)
        (played / rel).write_text(text)
    got = {k.replace(os.sep, "/"): (v.decode() if isinstance(v, bytes) else v) for k, v in p.install_files(str(played)).items()}
    want = {"dokima/card.py": "CARD of the played commit", "dokima/icons/x.svg": "<svg/>",
            ".github/workflows/card.yml": "name: card of the played commit"}
    assert got == want, f"437.3: install_files() should give the played commit's dokima/ and .github/workflows/ files, not {sorted(got)}"
    hub = FakeSandbox()
    code, lines = play(p, hub, "437.3")
    assert hub.calls[0] == ("install", None), f"437.3: play() should install the played commit before any step: {hub.calls[:3]}"
    assert code == 0 and lines == [f"PASS: {s}" for s in STEPS], f"437.3: after an install, the steps play as usual: {lines}"
    hub = FakeSandbox(refuse="HTTP 403: workflows permission refused")
    code, lines = play(p, hub, "437.3")
    assert [c for c in hub.calls if c[0] != "install"] == [], f"437.3: after a refused install, play() still played {hub.calls}"
    assert len(lines) == 1 and lines[0].startswith("FAIL: install") and "workflows permission refused" in lines[0], \
        f"437.3: a refused install should log one line starting 'FAIL: install' with GitHub's reason, not {lines}"
    assert code == 1, f"437.3: a refused install should make play() return 1, not {code!r}"
    (tmp_path / "empty").mkdir()
    (tmp_path / "run1").mkdir()
    out, made = run_playthrough(tmp_path / "run1", SANDBOX, played=tmp_path / "empty")
    said = out.stdout + out.stderr
    assert out.returncode != 0 and str(tmp_path / "empty") in said, \
        f"437.3: a played folder with no dokima/ should fail naming it: exit {out.returncode}, {said[-1000:]}"
    assert made == [], f"437.3: with nothing to install, the play-through still called {made[:3]}"
    (tmp_path / "run2").mkdir()
    out, made = run_playthrough(tmp_path / "run2", SANDBOX, commit="0123abcd4567", with_calls=True)
    said = out.stdout + out.stderr
    assert made and made[0]["sandbox_token"], \
        f"437.3: the install should push to card-gallery with SANDBOX_TOKEN, yet its first call does not carry it: {made[:3]}"
    assert out.returncode == 1, f"437.3: an install GitHub refuses should exit 1, not {out.returncode}: {said[-1000:]}"
    assert "FAIL: install" in said and "0123abcd4567" in said, \
        f"437.3: a refused install should say 'FAIL: install' naming the commit 0123abcd4567: {said[-1000:]}"
    for step in STEPS:
        assert f"PASS: {step}" not in said and f"FAIL: {step}" not in said, \
            f"437.3: with the played commit not installed, the play-through still judged {step!r}: {said[-1000:]}"
    for case, token in (("unset", None), ("empty", "")):
        run = tmp_path / f"no-token-{case}"
        run.mkdir()
        out, made = run_playthrough(run, SANDBOX, sandbox_token=token)
        said = out.stdout + out.stderr
        fails = [l for l in said.splitlines() if "FAIL: install" in l]
        assert out.returncode == 1, f"437.3: with SANDBOX_TOKEN {case}, the run should exit 1, not {out.returncode}: {said[-1000:]}"
        assert len(fails) == 1 and "SANDBOX_TOKEN" in fails[0], \
            f"437.3: with SANDBOX_TOKEN {case}, the run should log one 'FAIL: install' line naming SANDBOX_TOKEN: {said[-1000:]}"
        assert made == [], f"437.3: with SANDBOX_TOKEN {case}, the run still called {made[:3]}"
        for step in STEPS:
            assert f"PASS: {step}" not in said and f"FAIL: {step}" not in said, \
                f"437.3: with SANDBOX_TOKEN {case}, the play-through still judged {step!r}: {said[-1000:]}"

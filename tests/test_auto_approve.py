"""Tests for #934: an opted-in repo has Dokima approve and merge its own pull requests.

With `merge: {auto_approve: true}` in `.dokima/settings.yaml`, a pull request Dokima built merges by itself once its
code review approved and the merge gate passed (every check main requires green on its head), off autopilot too, with
one line on the pull request naming the code review's record and the green checks. Off, the shipped default, a passed
gate still waits for the owner's approval. A blocked review or a red check is never approved. `integrity` stays
locked. The audit, with the setting on, says when main's branch rule still requires a review Dokima's app cannot give, and setup applies the
change when the owner turns the setting on.

The river's tests run `python3 -m dokima.agent next 57 OUT` in-process, on the fake GitHub of
tests/test_merge_gate.py, from a temp folder holding the settings file. The audit's test runs the audit command from
outside on tests/fake_gh.py, as tests/test_audit_cli.py does. The setup test runs `python3 -m dokima.setup
auto-approve acme/widgets` from outside, with its own fake `gh` program first on the PATH that logs every call.
Nothing leaves the machine.
"""
import json
import os
import re
import subprocess
import sys
import time

import pytest
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent, agent_github, settings  # noqa: E402
import test_merge_gate as mg  # noqa: E402
from test_audit_cli import Audit, body_lines, clean  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RECORD_RUN = mg.CODE_REVIEW["run"]  # the code review record's run link: https://github.com/o/r/actions/runs/4
BLOCK = {**mg.CODE_REVIEW, "handback": {**mg.APPROVAL, "verdict": "block", "summary": "A proof is missing.",
                                        "raises": [{"kind": "blocker", "to": "worker", "text": "Test 57.1 fails.",
                                                    "id": "R1", "by": "reviewer"}]}}


def settings_dir(tmp_path, name, merge=None):
    """A temp repo folder; with MERGE, its settings file sets that merge group."""
    d = tmp_path / name
    (d / ".dokima").mkdir(parents=True)
    if merge is not None:
        (d / ".dokima" / "settings.yaml").write_text(yaml.safe_dump({"merge": merge}))
    return d


def decide(tmp_path, monkeypatch, capsys, fake, where, record=None, name="out"):
    """Runs `next 57` from WHERE on the code review RECORD against the fake.

    Returns (what it printed last, its Next line, any error that escaped it)."""
    record = record or mg.CODE_REVIEW
    out = tmp_path / f"out-{name}"
    out.mkdir()
    json.dump(record, open(out / "record.json", "w"))
    (out / "comment.md").write_text(agent.render(record))
    monkeypatch.chdir(where)
    monkeypatch.setattr(agent_github, "gh", fake.gh)
    monkeypatch.setattr(time, "sleep", fake.sleep)
    monkeypatch.setattr(time, "time", lambda: fake.clock)
    monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    monkeypatch.setenv("GITHUB_REPOSITORY", mg.REPO)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("OWNERS", mg.OWNER)
    monkeypatch.delenv("PACK", raising=False)
    escaped = None
    capsys.readouterr()
    try:
        agent.main(["dokima.agent", "next", mg.N, str(out)])
    except Exception as e:  # noqa: BLE001 - any escape is reported by the test that asked
        escaped = f"{type(e).__name__}: {(getattr(e, 'stderr', None) or str(e)).strip()}"
    finally:
        monkeypatch.undo()
    text = (out / "comment.md").read_text()
    line = next((l for l in text.splitlines() if l.startswith("**Next:**")), "")
    said = capsys.readouterr().out.strip().splitlines()
    return (said[-1].strip() if said else ""), line, escaped


def pr_notes(fake):
    """Every text Dokima posted on pull request #60: comments and reviews, however it asked GitHub."""
    notes = []
    for a in fake.calls:
        flag = lambda *names: next((a[i + 1] for i, x in enumerate(a[:-1]) if x in names), None)
        fields = {x.split("=", 1)[0]: x.split("=", 1)[1] for x in a if "=" in x and not x.startswith("repos")}
        on_pr = (a[:2] in (["pr", "comment"], ["pr", "review"], ["issue", "comment"]) and str(mg.PR) in a[2:3]) or any(
            re.fullmatch(rf"/?repos/o/r/(issues/{mg.PR}/comments|pulls/{mg.PR}/(reviews|comments))", x) for x in a)
        body = flag("--body", "-b") or fields.get("body")
        if on_pr and body:
            notes.append(body)
    return notes


def approval_notes(fake):
    """The notes on #60 naming the code review record's run link: Dokima's approval lines."""
    return [n for n in pr_notes(fake) if RECORD_RUN in n]


# 934.1: on, a passed merge gate merges the pull request with no person waited on

def test_with_auto_approve_on_a_passed_gate_merges_with_no_person(record_property, tmp_path, monkeypatch, capsys):
    """With the setting on, a reviewed pull request with green checks merges by itself.

    Proves 934.1. Off autopilot, the code review approved #60 and every check main requires is green on its head. With
    `merge.auto_approve: true`, the run must merge #60 at that head and not stop for the owner; today it stops and asks
    the owner to approve. A branch behind main merges only at the head brought up to date and green, never the old
    one. Beside it, the same pull request with the setting off must not merge, so the merge comes from the setting."""
    record_property("proves", "934.1")
    on = settings_dir(tmp_path, "on", {"auto_approve": True})
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, on, name="on")
    assert escaped is None, f"934.1: deciding what follows the code review failed: {escaped}"
    assert [m["head"] for m in fake.merges] == [mg.OLD], \
        (f"934.1: with merge.auto_approve on, the code review passed and every check is green, yet #60 did not merge "
         f"once at its tested head: merges {fake.merges}, printed {said!r}, Next {line!r}")
    assert said != "stop" and f"@{mg.OWNER}" not in line, \
        f"934.1: with merge.auto_approve on, the run still waited for the owner: printed {said!r}, Next {line!r}"

    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD), mg.NEW: mg.green(mg.NEW)}, behind=True)
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, on, name="behind")
    assert escaped is None, f"934.1: deciding what follows the code review failed: {escaped}"
    assert [m["head"] for m in fake.merges] == [mg.NEW], \
        (f"934.1: a branch behind main must merge only at the head brought up to date and green ({mg.NEW[:7]}): "
         f"merges {fake.merges}")

    off = settings_dir(tmp_path, "off", {"auto_approve": False})
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, off, name="off")
    assert escaped is None, f"934.1: deciding what follows the code review failed: {escaped}"
    assert fake.merges == [], f"934.1: with merge.auto_approve off, #60 merged with no person: {fake.merges}"


# 934.2: the approval leaves one line on the pull request naming the code review record and the green checks

def test_the_approval_leaves_one_line_naming_the_review_and_the_green_checks(record_property, tmp_path, monkeypatch, capsys):
    """Dokima's approval leaves one line naming the code review and the green checks.

    Proves 934.2. With `merge.auto_approve: true`, off autopilot, the code review approved #60 and both checks main requires are
    green. Dokima must post one note on #60, on one line, linking the code review record's run and naming each green
    check, `all tests` and `Acceptance criteria`; today it posts nothing there. Beside it, with the setting off, no
    such note is posted."""
    record_property("proves", "934.2")
    on = settings_dir(tmp_path, "on", {"auto_approve": True})
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, on, name="on")
    assert escaped is None, f"934.2: deciding what follows the code review failed: {escaped}"
    notes = approval_notes(fake)
    assert len(notes) == 1, \
        (f"934.2: Dokima's approval should leave exactly one note on #60 linking the code review record "
         f"({RECORD_RUN}); found {notes}; everything posted on #60: {pr_notes(fake)}")
    note = notes[0].strip()
    assert "\n" not in note, f"934.2: the approval note is not one line: {note!r}"
    missing = [c for c in mg.REQUIRED if c not in note]
    assert not missing, f"934.2: the approval note does not name the green checks {missing}: {note!r}"

    off = settings_dir(tmp_path, "off")
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    decide(tmp_path, monkeypatch, capsys, fake, off, name="off")
    assert approval_notes(fake) == [], f"934.2: with the setting off, an approval note was posted: {approval_notes(fake)}"


# 934.3: a pull request whose code review blocked is never approved

def test_a_blocked_code_review_is_never_approved(record_property, tmp_path, monkeypatch, capsys):
    """A pull request whose code review blocked is never approved, even with the setting on.

    Proves 934.3. With `merge.auto_approve: true` and every check green, a code review that blocks #60 must leave it unmerged and
    post no approval note; the work goes back instead. Beside it, the same pull request whose code review approved
    merges, so the test is not passed by a run that never approves anything."""
    record_property("proves", "934.3")
    on = settings_dir(tmp_path, "on", {"auto_approve": True})
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, on, record=BLOCK, name="blocked")
    assert escaped is None, f"934.3: deciding what follows the blocking code review failed: {escaped}"
    assert fake.merges == [] and approval_notes(fake) == [], \
        (f"934.3: the code review blocked, yet #60 was approved or merged: merges {fake.merges}, "
         f"notes {approval_notes(fake)}")

    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    decide(tmp_path, monkeypatch, capsys, fake, on, name="approved")
    assert [m["head"] for m in fake.merges] == [mg.OLD], \
        f"934.3: with the code review approving and the setting on, #60 did not merge: {fake.merges}"


# 934.4: a pull request whose checks are red is never approved

def test_red_checks_are_never_approved(record_property, tmp_path, monkeypatch, capsys):
    """A pull request with a red check is never approved, even with the setting on.

    Proves 934.4. With `merge.auto_approve: true`, the code review approved #60 but `all tests` failed on its head: it must stay
    unmerged with no approval note. A branch behind main, green on its old head but red
    once brought up to date, is not approved either. Beside it, all green merges."""
    record_property("proves", "934.4")
    on = settings_dir(tmp_path, "on", {"auto_approve": True})
    fake = mg.FakeGitHub({mg.OLD: mg.red(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, on, name="red")
    assert escaped is None, f"934.4: deciding what follows the code review failed: {escaped}"
    assert fake.merges == [] and approval_notes(fake) == [], \
        f"934.4: all tests failed, yet #60 was approved or merged: merges {fake.merges}, notes {approval_notes(fake)}"

    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD), mg.NEW: mg.red(mg.NEW, "Acceptance criteria")}, behind=True)
    decide(tmp_path, monkeypatch, capsys, fake, on, name="behind-red")
    assert fake.merges == [] and approval_notes(fake) == [], \
        (f"934.4: Acceptance criteria failed once brought up to date with main, yet #60 was approved or merged: "
         f"merges {fake.merges}, notes {approval_notes(fake)}")

    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    decide(tmp_path, monkeypatch, capsys, fake, on, name="green")
    assert [m["head"] for m in fake.merges] == [mg.OLD], \
        f"934.4: with every check green and the setting on, #60 did not merge: {fake.merges}"


# 934.5: off by default, a passed gate still waits for the owner's approval

def test_auto_approve_is_off_by_default_and_the_owner_still_approves(record_property, tmp_path, monkeypatch, capsys):
    """Auto approve is off by default, so a passed gate still waits for the owner.

    Proves 934.5. The shipped settings, with no repo file, must hold `merge.auto_approve` as false; today they have no such setting.
    Run with no settings file, a code review that approved #60 with every check green must stop for the owner,
    asking them to approve, merge nothing and post no approval note, as today."""
    record_property("proves", "934.5")
    plain = settings_dir(tmp_path, "plain")
    got = settings.read(str(plain), warn=lambda m: None)
    assert (got.get("merge") or {}).get("auto_approve") is False, \
        f"934.5: the shipped settings should hold merge.auto_approve false; the merge group is {got.get('merge')}"
    fake = mg.FakeGitHub({mg.OLD: mg.green(mg.OLD)})
    said, line, escaped = decide(tmp_path, monkeypatch, capsys, fake, plain, name="default")
    assert escaped is None, f"934.5: deciding what follows the code review failed: {escaped}"
    assert fake.merges == [] and approval_notes(fake) == [], \
        f"934.5: with no setting, #60 was approved or merged: merges {fake.merges}, notes {approval_notes(fake)}"
    assert said == "stop" and mg.APPROVE_ASK.search(line) and f"@{mg.OWNER}" in line, \
        f"934.5: with no setting, the run did not wait for the owner's approval: printed {said!r}, Next {line!r}"


# 934.6 (owner approval stays locked, even with auto approve on) is proven in tests/test_settings_merge.py.


# 934.7: merge.auto_approve is the opt-in a repo sets

def test_auto_approve_is_the_setting_a_repo_opts_in_with(record_property, tmp_path):
    """A repo opts in by setting auto approve on, with no warning.

    Proves 934.7. A file setting only `merge.auto_approve: true` must read as true with no unknown-setting warning; today
    the setting is unknown, warned of and dropped."""
    record_property("proves", "934.7")
    opted = settings_dir(tmp_path, "opted", {"auto_approve": True})
    warned = []
    got = settings.read(str(opted), warn=warned.append)
    assert (got.get("merge") or {}).get("auto_approve") is True and not warned, \
        (f"934.7: merge.auto_approve true should read as the opt-in; got merge {got.get('merge')}, "
         f"warnings {warned}")


# 934.8: the audit says, in one line, when main's rule needs a review the bot cannot give, and what to change

def review_lines(text):
    """The Setup issue's lines about a review the app cannot give."""
    return [l for l in body_lines(text) if "review" in l.lower() and re.search(r"code.owner|bypass", l, re.I)]


def audit_review_lines(tmp_path, name, merge, **state_changes):
    """Runs the audit with MERGE settings and a changed main rule; returns its review lines.

    STATE_CHANGES change the fake's main rule; the lines are those `review_lines` picks from the Setup issue."""
    state = clean()
    state.update(state_changes)
    a = Audit(tmp_path / name, state)
    settings_dir(tmp_path / name, "repo", merge)
    a.run("934.8")
    bodies = [i["body"] for i in a.state()["issues"].values()]
    return [l for b in bodies for l in review_lines(b)], bodies, a


def test_the_audit_says_when_main_needs_a_review_the_bot_cannot_give(record_property, tmp_path):
    """The audit says in one line which review blocks the bot, and the fix.

    Proves 934.8. The repo opts in (`merge.auto_approve: true`, no merge queue). Main's rule requires an approving review
    from code owners and its review exemption lists only another app: the Setup issue must hold exactly one line saying
    so and naming the change, dropping code owner review or letting the app bypass reviews. The same holds for a plain
    required review, not from code owners. Beside it, with Dokima's app on that exemption, or with auto approve off, no
    such line is written."""
    record_property("proves", "934.8")
    on = {"auto_approve": True, "queue": False}
    lines, bodies, a = audit_review_lines(tmp_path, "owners", on, review_bypass_apps=[42])
    assert len(lines) == 1, \
        (f"934.8: main requires a code owner review the app cannot give, and the Setup issue should say so on exactly "
         f"one line naming code owners or a bypass; found {lines} in {bodies}\n{a.why()}")

    lines, bodies, a = audit_review_lines(tmp_path, "plain", on, review_bypass_apps=[42], code_owner_reviews=False)
    assert len(lines) == 1, \
        (f"934.8: main requires a plain review the app cannot give, and the Setup issue should say so on exactly one "
         f"line naming a bypass; found {lines} in {bodies}\n{a.why()}")

    lines, bodies, a = audit_review_lines(tmp_path, "exempt", on, review_bypass_apps=[1])  # the fake's app id is 1
    assert not lines, \
        f"934.8: Dokima's app is on main's review exemption, yet the audit still reports a review it cannot give: {bodies}"

    lines, bodies, a = audit_review_lines(tmp_path, "off", {"auto_approve": False, "queue": False},
                                          review_bypass_apps=[42])
    assert not lines, f"934.8: auto approve is off, yet the audit reports a review the app cannot give: {bodies}"


# 934.9: setup applies the change when the owner turns the setting on

FAKE_SETUP_GH = r'''
import json, os, sys
a = sys.argv[1:]
stdin = "" if sys.stdin.isatty() else sys.stdin.read()
log = os.environ["FAKE_GH_LOG"]
open(log, "a").write(json.dumps({"args": a, "stdin": stdin}) + "\n")
path = next((x.strip("/") for x in a[1:] if x.lstrip("/").startswith("repos/")), "")
method = next((a[i + 1] for i, x in enumerate(a[:-1]) if x in ("-X", "--method")), "GET").upper()
if a[:2] == ["repo", "view"]:
    print("acme/widgets" if "-q" in a or "--jq" in a else json.dumps({"nameWithOwner": "acme/widgets"}))
    sys.exit(0)
state_file = log + ".checks"
checks = json.load(open(state_file)) if os.path.exists(state_file) else ["all tests", "Acceptance criteria"]
if path.startswith("repos/acme/widgets/branches/main/protection") and method == "GET":
    reviews = {"required_approving_review_count": 1, "require_code_owner_reviews": True,
               "bypass_pull_request_allowances": {"users": [], "teams": [], "apps": []}}
    if path.endswith("required_pull_request_reviews"):
        print(json.dumps(reviews))
    else:
        print(json.dumps({"required_status_checks": {"strict": True, "contexts": checks},
                          "required_pull_request_reviews": reviews, "enforce_admins": {"enabled": False}}))
    sys.exit(0)
if path.startswith("repos/acme/widgets/branches/main/protection") and method in ("PATCH", "PUT", "POST"):
    if os.environ.get("FAKE_GH_REFUSE"):
        sys.stderr.write("gh: Must have admin rights to Repository. (HTTP 403)\n")
        sys.exit(1)
    # Keeps main's required checks as GitHub would: a write to the whole rule or to its checks replaces them.
    sub = path[len("repos/acme/widgets/branches/main/protection"):].strip("/")
    if sub in ("", "required_status_checks"):
        try:
            body = json.loads(stdin) if stdin.strip() else {}
        except ValueError:
            body = {}
        fields = [x.split("=", 1) for x in a if "=" in x and not x.startswith("repos")]
        if sub == "":
            body = body.get("required_status_checks") or {}
        checks = list(body.get("contexts") or []) + [c.get("context") for c in body.get("checks") or []]
        checks += [v for k, v in fields if "contexts" in k or "[context]" in k]
    json.dump(checks, open(state_file, "w"))
    print("{}")
    sys.exit(0)
if path.startswith("repos/acme/widgets/branches/main/protection") and method == "DELETE":
    if path.rstrip("/").endswith("required_status_checks") or path.rstrip("/").endswith("protection"):
        json.dump([], open(state_file, "w"))
    print("{}")
    sys.exit(0)
sys.stderr.write("gh: Not Found (HTTP 404)\n")
sys.exit(1)
'''


def run_setup(tmp_path, name, refuse=False):
    """Runs `python3 -m dokima.setup auto-approve acme/widgets` in a temp repo.

    Returns (process, repo folder, gh calls, the checks main requires afterwards)."""
    repo = tmp_path / name / "repo"
    repo.mkdir(parents=True)
    bindir = tmp_path / name / "bin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text(f"#!{sys.executable}\n" + FAKE_SETUP_GH)
    gh.chmod(0o755)
    log = tmp_path / name / "gh.jsonl"
    env = dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}", PYTHONPATH=ROOT,
               FAKE_GH_LOG=str(log), GH_TOKEN="fake")
    env.pop("FAKE_GH_REFUSE", None)
    if refuse:
        env["FAKE_GH_REFUSE"] = "1"
    p = subprocess.run([sys.executable, "-m", "dokima.setup", "auto-approve", "acme/widgets"], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    calls = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    kept = tmp_path / name / "gh.jsonl.checks"
    checks = json.loads(kept.read_text()) if kept.exists() else ["all tests", "Acceptance criteria"]
    return p, repo, calls, checks


def test_setup_turns_auto_approve_on_and_lets_the_app_bypass_reviews(record_property, tmp_path):
    """Turning the setting on through setup lets the bot past main's required review.

    Proves 934.9. Runs `python3 -m dokima.setup auto-approve acme/widgets` in a temp repo whose main requires a code owner review.
    It must exit 0, leave `merge.auto_approve: true` in `.dokima/settings.yaml`, and ask GitHub to change main's
    protection so its review bypass lists Dokima's app (`dokima-runtime`, the bot in settings), while main still
    requires `all tests` and `Acceptance criteria`. When GitHub refuses the change, setup must exit non-zero and show
    GitHub's reason."""
    record_property("proves", "934.9")
    p, repo, calls, checks = run_setup(tmp_path, "ok")
    assert p.returncode == 0, f"934.9: setup auto-approve failed (exit {p.returncode}): {p.stdout}{p.stderr}"
    got = settings.read(str(repo), warn=lambda m: None)
    assert (got.get("merge") or {}).get("auto_approve") is True, \
        f"934.9: setup did not turn merge.auto_approve on in the settings file; merge is {got.get('merge')}"
    writes = [c for c in calls if any("branches/main/protection" in x for x in c["args"])
              and any(x.upper() in ("PATCH", "PUT", "POST") for x in c["args"])]
    asked = " ".join(" ".join(c["args"]) + " " + c["stdin"] for c in writes)
    assert writes and "bypass_pull_request_allowances" in asked and "dokima-runtime" in asked, \
        (f"934.9: setup did not ask GitHub to let dokima-runtime bypass main's required review; protection writes: "
         f"{writes}; every call: {calls}")
    dropped = [c for c in ("all tests", "Acceptance criteria") if c not in checks]
    assert not dropped, \
        (f"934.9: setup dropped main's required checks {dropped}; main now requires {checks}; protection writes: "
         f"{writes}")

    p, repo, calls, checks = run_setup(tmp_path, "refused", refuse=True)
    assert p.returncode != 0 and "Must have admin rights" in p.stdout + p.stderr, \
        (f"934.9: GitHub refused the protection change, and setup did not fail with GitHub's reason: exit "
         f"{p.returncode}, said {p.stdout}{p.stderr}")

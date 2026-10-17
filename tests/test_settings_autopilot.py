"""Tests for #787: autopilot merges by the repo's branch, method, checks wait and labels.

The settings live in `.dokima/settings.yaml` in the repo the run works in, over Dokima's shipped defaults in
`dokima/defaults.yaml`. This story reads these of them:

    branch: {default: main}          # the branch autopilot merges into; empty or unset asks GitHub for the repo's own
    merge: {method: squash}          # how autopilot merges: squash, merge or rebase
    gate: {checks_wait_min: 45}      # how many minutes the merge gate waits for checks still running
    labels: {autopilot: autopilot, filed: filed-by-dokima}   # the autopilot label and the label on issues Dokima files

Each test writes a settings file into a temp folder, runs there, and calls autopilot's or the board's own code
against a fake GitHub in memory standing in for `gh`. Time is faked, so a 45-minute wait costs nothing. Nothing
leaves the machine.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent_autopilot as ap  # noqa: E402
from dokima import agent_github  # noqa: E402
from dokima import board as board_mod  # noqa: E402

REPO = "o/r"
PR = 60
HEAD = "a1" * 20


class FakeGitHub:
    """A fake GitHub for one repo: branch rules, one pull request, checks, issues, labels.

    BRANCHES names each branch GitHub has, with the checks its rule requires; any other branch answers 404. Every
    call is kept in `calls`, so a test can say which branch, method or label autopilot used."""

    def __init__(self, branches=None, github_default="main", running=(), labels=None):
        """A repo with BRANCHES, GitHub's own default branch, checks still RUNNING and each issue's LABELS."""
        self.branches = branches if branches is not None else {"main": ["all tests"]}
        self.github_default = github_default
        self.running = set(running)
        self.labels = labels or {}
        self.calls = []
        self.created = []
        self.merges = []

    def refuse(self, args, why="HTTP 404: Not Found"):
        """Raise the error `gh` raises when GitHub refuses a call."""
        raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr=why)

    def __call__(self, *args):
        """Answer one `gh` call the way GitHub would."""
        self.calls.append(args)
        if args[:2] == ("pr", "view"):
            field = args[args.index("--json") + 1]
            return {"headRefOid": HEAD, "isDraft": "false"}[field]
        if args[:2] == ("pr", "merge"):
            self.merges.append(args)
            return ""
        if args[:2] == ("issue", "create"):
            self.created.append(args)
            return f"https://github.com/{REPO}/issues/900\n"
        if args[:2] == ("api", "graphql"):
            return json.dumps({"data": {"repository": {"pullRequest": {"state": "MERGED", "isInMergeQueue": False}}}})
        rest = [a for a in args[1:] if not a.startswith("-")]
        method = args[args.index("-X") + 1] if "-X" in args else "GET"
        path = next(a for a in rest if a.startswith("repos/")) if any(a.startswith("repos/") for a in rest) else ""
        if path == f"repos/{REPO}":
            return json.dumps({"full_name": REPO, "default_branch": self.github_default})
        if path.startswith(f"repos/{REPO}/branches/"):
            name = path.split("/branches/", 1)[1].split("/protection")[0]
            if name not in self.branches:
                self.refuse(args, "HTTP 404: Branch not found")
            rule = {"required_status_checks": {"contexts": self.branches[name]}}
            return json.dumps({"name": name, "protection": rule})
        if path.startswith(f"repos/{REPO}/compare/"):
            base = path.split("/compare/", 1)[1].split("...")[0]
            if base not in self.branches:
                self.refuse(args)
            return json.dumps({"status": "ahead", "behind_by": 0})
        if path.startswith(f"repos/{REPO}/commits/") and "/check-runs" in path:
            names = {c for cs in self.branches.values() for c in cs}
            return json.dumps({"check_runs": [
                {"name": c, "head_sha": HEAD, "status": "in_progress" if c in self.running else "completed",
                 "conclusion": None if c in self.running else "success"} for c in sorted(names)]})
        if path.startswith(f"repos/{REPO}/commits/") and "/status" in path:
            return json.dumps({"statuses": []})
        if path.startswith(f"repos/{REPO}/pulls/{PR}/files"):
            return json.dumps([{"filename": "dokima/x.py"}])
        if path.startswith(f"repos/{REPO}/issues/") and path.endswith("/sub_issues?per_page=100"):
            return "[]"
        if path.startswith(f"repos/{REPO}/issues?labels="):
            name = path.split("labels=", 1)[1].split("&")[0]
            return json.dumps([{"number": n, "state": "open", "labels": [{"name": x} for x in ls]}
                               for n, ls in sorted(self.labels.items()) if name in ls])
        if path.startswith(f"repos/{REPO}/issues/") and path.count("/") == 4 and method == "GET":
            n = int(path.rsplit("/", 1)[1])
            return json.dumps({"number": n, "state": "open", "labels": [{"name": x} for x in self.labels.get(n, [])]})
        if path.startswith(f"repos/{REPO}/issues/") and "/labels" in path:
            n = int(path.split("/issues/", 1)[1].split("/")[0])
            if method == "POST":
                field = next(a for a in args if a.startswith("labels[]="))
                self.labels.setdefault(n, []).append(field.split("=", 1)[1])
            elif method == "DELETE":
                self.labels[n] = [x for x in self.labels.get(n, []) if x != path.rsplit("/", 1)[1]]
            return "[]"
        self.refuse(args, f"the fake GitHub has no answer for: gh {' '.join(args)}")

    def branches_asked(self):
        """Every branch name autopilot asked GitHub about: rules read and comparisons made."""
        out = []
        for args in self.calls:
            for a in args:
                if a.startswith(f"repos/{REPO}/branches/"):
                    out.append(a.split("/branches/", 1)[1].split("/protection")[0])
                elif a.startswith(f"repos/{REPO}/compare/"):
                    out.append(a.split("/compare/", 1)[1].split("...")[0])
        return out


class Clock:
    """A fake clock: sleeping only moves it forward."""

    def __init__(self):
        """Starts at zero seconds."""
        self.now = 0.0

    def sleep(self, s):
        """Moves the clock S seconds on at once."""
        self.now += s

    def monotonic(self):
        """The fake time in seconds."""
        return self.now


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Runs the test inside a temp repo folder; returns a function writing its `.dokima/settings.yaml`."""
    monkeypatch.chdir(tmp_path)
    clock = Clock()
    monkeypatch.setattr(ap.time, "sleep", clock.sleep)
    monkeypatch.setattr(ap.time, "monotonic", clock.monotonic)

    def settings(text=None):
        """Writes TEXT as the repo's settings file; None leaves the repo with no settings file."""
        if text is not None:
            os.makedirs(".dokima", exist_ok=True)
            with open(os.path.join(".dokima", "settings.yaml"), "w") as f:
                f.write(text)
    settings.clock = clock
    return settings


def fake(monkeypatch, **kw):
    """Puts a FakeGitHub with KW in place of `gh`, and returns it."""
    gh = FakeGitHub(**kw)
    monkeypatch.setattr(agent_github, "gh", gh)
    return gh


def merge_flag(args):
    """The merge method flag a `gh pr merge` call passed: --squash, --merge or --rebase."""
    flags = [a for a in args if a in ("--squash", "--merge", "--rebase")]
    return flags[0] if len(flags) == 1 else flags


# 787.1 ---------------------------------------------------------------------------------------------------------


def test_autopilot_merges_into_the_default_branch_the_settings_name(record_property, repo, monkeypatch):
    """Autopilot merges into the default branch the settings name.

    With `branch.default: trunk`, a GitHub repo whose only branch is trunk, and a green pull request, autopilot
    merges it, and every branch rule it read and every comparison it made names trunk, never main. Proves 787.1."""
    record_property("proves", "787.1")
    repo("branch:\n  default: trunk\n")
    gh = fake(monkeypatch, branches={"trunk": ["all tests"]}, github_default="trunk")
    asked, why = ap.try_merge(REPO, PR)
    assert asked, f"787.1: autopilot did not merge into trunk, the settings' default branch: {why}"
    assert gh.merges, "787.1: autopilot never asked GitHub to merge the pull request"
    used = set(gh.branches_asked())
    assert used == {"trunk"}, f"787.1: autopilot read branches {sorted(used)}, not only trunk as the settings name"


def test_a_default_branch_github_lacks_stops_saying_which(record_property, repo, monkeypatch):
    """A default branch setting GitHub does not have stops the merge, naming that branch.

    With `branch.default: trunk` and a repo that only has main, nothing merges and the reason names trunk.
    Proves 787.1."""
    record_property("proves", "787.1")
    repo("branch:\n  default: trunk\n")
    gh = fake(monkeypatch, branches={"main": ["all tests"]})
    asked, why = ap.try_merge(REPO, PR)
    assert not asked and not gh.merges, "787.1: autopilot merged although GitHub has no trunk branch"
    assert "trunk" in (why or ""), f"787.1: the reason does not name trunk, the branch the settings name: {why!r}"


# 787.2 ---------------------------------------------------------------------------------------------------------


def test_with_no_default_branch_setting_autopilot_uses_githubs_default_branch(record_property, repo, monkeypatch):
    """With the default branch setting empty, autopilot merges into GitHub's default branch.

    The settings file gives `branch.default` no value; GitHub says the repo's default branch is develop. Autopilot
    merges, and every branch rule it read and every comparison it made names develop. Proves 787.2."""
    record_property("proves", "787.2")
    repo("branch:\n  default:\n")
    gh = fake(monkeypatch, branches={"develop": ["all tests"]}, github_default="develop")
    asked, why = ap.try_merge(REPO, PR)
    assert asked, f"787.2: autopilot did not merge into develop, GitHub's default branch: {why}"
    used = set(gh.branches_asked())
    assert used == {"develop"}, f"787.2: autopilot read branches {sorted(used)}, not GitHub's default branch develop"


def test_an_empty_text_default_branch_also_uses_githubs(record_property, repo, monkeypatch):
    """A default branch setting of empty text also means GitHub's default branch.

    With `branch.default: ""` and GitHub's default branch develop, autopilot merges into develop. Proves 787.2."""
    record_property("proves", "787.2")
    repo('branch:\n  default: ""\n')
    gh = fake(monkeypatch, branches={"develop": ["all tests"]}, github_default="develop")
    asked, why = ap.try_merge(REPO, PR)
    assert asked, f"787.2: an empty default branch setting did not fall back to GitHub's develop: {why}"
    assert set(gh.branches_asked()) == {"develop"}, f"787.2: autopilot read {sorted(set(gh.branches_asked()))}"


# 787.3 ---------------------------------------------------------------------------------------------------------


def test_autopilot_merges_with_the_merge_method_the_settings_name(record_property, repo, monkeypatch):
    """Autopilot merges with the merge method the settings name.

    With `merge.method: rebase`, the merge autopilot asks GitHub for passes --rebase, not --squash. Proves 787.3."""
    record_property("proves", "787.3")
    repo("merge:\n  method: rebase\n")
    gh = fake(monkeypatch)
    asked, why = ap.try_merge(REPO, PR)
    assert asked and gh.merges, f"787.3: autopilot did not merge: {why}"
    flags = [merge_flag(m) for m in gh.merges]
    assert flags == ["--rebase"] * len(flags), f"787.3: autopilot merged with {flags}, not --rebase as the settings say"


def test_a_direct_merge_after_a_held_one_keeps_the_settings_method(record_property, repo, monkeypatch):
    """A direct merge after GitHub holds one keeps the settings' merge method.

    GitHub refuses the first merge for a missing approving review; the retry with --admin still passes --merge.
    Proves 787.3."""
    record_property("proves", "787.3")
    repo("merge:\n  method: merge\n")
    gh = fake(monkeypatch)
    plain = gh.__call__

    def held(*args):
        """Refuses the first plain merge, as GitHub does awaiting an approving review."""
        if args[:2] == ("pr", "merge") and "--admin" not in args and not gh.merges:
            gh.merges.append(args)
            gh.refuse(args, "At least 1 approving review is required by reviewers with write access.")
        return plain(*args)
    monkeypatch.setattr(agent_github, "gh", held)
    asked, why = ap.try_merge(REPO, PR)
    assert asked, f"787.3: autopilot did not merge directly: {why}"
    admin = [m for m in gh.merges if "--admin" in m]
    assert admin, "787.3: autopilot never asked for a direct merge after GitHub held the first one"
    assert [merge_flag(m) for m in gh.merges] == ["--merge"] * len(gh.merges), f"787.3: merges used {gh.merges}"


# 787.4 ---------------------------------------------------------------------------------------------------------


def test_the_merge_gate_waits_for_checks_as_many_minutes_as_the_settings_say(record_property, repo, monkeypatch):
    """The merge gate waits for checks as many minutes as the settings say.

    With `gate.checks_wait_min: 2` and a required check that never finishes, the gate stops after 2 minutes of
    fake time, and says so, instead of waiting 45. Proves 787.4."""
    record_property("proves", "787.4")
    repo("gate:\n  checks_wait_min: 2\n")
    fake(monkeypatch, running={"all tests"})
    state, _, why = ap.merge_gate(REPO, PR)
    assert state == "stopped", f"787.4: the gate did not stop on a check that never finished: {state} {why}"
    waited = repo.clock.now
    assert 120 <= waited < 180, f"787.4: the gate waited {waited:.0f} s, not the 2 minutes the settings say"
    assert "after 2 minutes" in (why or ""), f"787.4: the reason does not say it waited 2 minutes: {why!r}"


# 787.5 ---------------------------------------------------------------------------------------------------------


def test_autopilot_reads_its_label_by_the_name_in_the_labels_setting(record_property, repo, monkeypatch):
    """Autopilot treats an issue as on autopilot by the label name the settings give.

    With `labels.autopilot: dokima-auto`, an issue carrying dokima-auto is on autopilot, and one carrying only the
    old autopilot label is not. Proves 787.5."""
    record_property("proves", "787.5")
    repo("labels:\n  autopilot: dokima-auto\n")
    fake(monkeypatch, labels={5: ["dokima-auto"], 6: ["autopilot"]})
    assert ap.on_autopilot(REPO, 5) is True, "787.5: an issue carrying dokima-auto is not on autopilot"
    assert ap.on_autopilot(REPO, 6) is False, "787.5: an issue carrying only the old autopilot label is on autopilot"


def test_the_sweep_lists_issues_by_the_named_label(record_property, repo, monkeypatch):
    """The autopilot sweep asks GitHub for issues by the label the settings name.

    Proves 787.5."""
    record_property("proves", "787.5")
    repo("labels:\n  autopilot: dokima-auto\n")
    gh = fake(monkeypatch, labels={5: ["dokima-auto"]})
    monkeypatch.setenv("OWNERS", "owner-person")
    monkeypatch.setattr(ap, "start_unblocked", lambda repo, waiting, owners: ([], []))
    ap.autopilot_closed(REPO)
    asked = [a for args in gh.calls for a in args if "issues?labels=" in a]
    assert asked and all("labels=dokima-auto&" in a for a in asked), f"787.5: the sweep asked for {asked}"


def test_the_board_reads_autopilot_by_the_named_label(record_property, repo):
    """The board counts an issue as on autopilot by the label name the settings give.

    With `labels.autopilot: dokima-auto`, the board says an issue carrying dokima-auto is on autopilot, and one
    carrying only the old autopilot label is not. Proves 787.5."""
    record_property("proves", "787.5")
    repo("labels:\n  autopilot: dokima-auto\n")
    labels = {5: ["dokima-auto"], 6: ["autopilot"]}

    def q(query, **v):
        """A fake GitHub GraphQL: an empty board, and each issue's labels."""
        if "projectV2(number:$n){id fields" in query:
            return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": []}}}}
        return {"repository": {"issue": {"labels": {"nodes": [{"name": x} for x in labels[v["n"]]]}}}}
    b = board_mod.Board("o/1", REPO, q=q, rest=lambda *a, **k: {})
    assert b.autopilot("issue", 5) is True, "787.5: the board does not count an issue carrying dokima-auto"
    assert b.autopilot("issue", 6) is False, "787.5: the board counts the old autopilot label"


def test_adding_the_named_label_on_github_moves_the_board_card(record_property, repo, monkeypatch):
    """Adding the label the settings name on GitHub moves the board card.

    With `labels.autopilot: dokima-auto`, adding dokima-auto to an issue is an event the board runs on, and the run
    switches that issue's card on autopilot; adding the old autopilot label is skipped. Proves 787.5."""
    record_property("proves", "787.5")
    repo("labels:\n  autopilot: dokima-auto\n")
    switched = []
    monkeypatch.setattr(board_mod, "switch", lambda b, n: switched.append(n))
    monkeypatch.setattr(board_mod, "rebuild", lambda *a, **k: [])
    monkeypatch.setattr(board_mod.plan, "repo_approvers", lambda owner: [])

    def event(name):
        """The event GitHub sends when label NAME is added to issue #5."""
        return {"action": "labeled", "label": {"name": name},
                "issue": {"number": 5, "state": "open", "labels": [{"name": name}]}}

    def q(query, **v):
        """A fake GitHub GraphQL holding an empty board."""
        return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": []}}}}
    assert board_mod.can_move("issues", event("dokima-auto")) is True, \
        "787.5: the board skips adding dokima-auto, so the card never moves"
    assert board_mod.can_move("issues", event("autopilot")) is False, \
        "787.5: the board still runs on the old autopilot label"
    board_mod.sync("issues", event("dokima-auto"), "o/1", REPO, q=q, rest=lambda *a, **k: {})
    assert switched == [5], f"787.5: adding dokima-auto switched {switched}, not issue #5's card"


# 787.6 ---------------------------------------------------------------------------------------------------------


def test_turning_autopilot_on_puts_the_named_label_on(record_property, repo, monkeypatch):
    """Turning autopilot on puts the label the settings name on the issue.

    Proves 787.6."""
    record_property("proves", "787.6")
    repo("labels:\n  autopilot: dokima-auto\n")
    gh = fake(monkeypatch, labels={5: []})
    assert ap.switch_autopilot(REPO, 5, "start") == [5], "787.6: turning autopilot on switched nothing"
    assert gh.labels[5] == ["dokima-auto"], f"787.6: the issue now carries {gh.labels[5]}, not dokima-auto"


def test_the_board_puts_the_named_label_on_a_pull_request(record_property, repo):
    """The board puts the label the settings name on a pull request.

    Proves 787.6."""
    record_property("proves", "787.6")
    repo("labels:\n  autopilot: dokima-auto\n")
    calls = []

    def q(query, **v):
        """A fake GitHub GraphQL holding an empty board."""
        return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": []}}}}
    b = board_mod.Board("o/1", REPO, q=q, rest=lambda method, path, **f: calls.append((method, path, f)) or {})
    b.label("pr", 60, True)
    assert calls == [("POST", f"repos/{REPO}/issues/60/labels", {"labels[]": "dokima-auto"})], \
        f"787.6: the board labelled the pull request with {calls}, not dokima-auto"


def test_turning_autopilot_off_removes_the_named_label(record_property, repo, monkeypatch):
    """Turning autopilot off takes the label the settings name off the issue.

    With `labels.autopilot: dokima-auto`, an issue carrying dokima-auto and bug keeps only bug. Proves 787.6."""
    record_property("proves", "787.6")
    repo("labels:\n  autopilot: dokima-auto\n")
    gh = fake(monkeypatch, labels={5: ["dokima-auto", "bug"]})
    assert ap.switch_autopilot(REPO, 5, "stop") == [5], "787.6: turning autopilot off switched nothing"
    assert gh.labels[5] == ["bug"], f"787.6: the issue still carries {gh.labels[5]} after autopilot was turned off"


# 787.7 ---------------------------------------------------------------------------------------------------------


def reviewer_finding():
    """A passed review record that raises one issue found outside its own."""
    return {"role": "reviewer", "stage": "pr", "check": {"passed": True, "problems": []},
            "handback": {"verdict": "approve", "raises": [{"id": "R1", "kind": "issue", "raised_by": "reviewer",
                                                           "text": "The board ignores closed pull requests."}]}}


def test_issues_dokima_files_carry_the_filed_label_named_in_settings(record_property, repo, monkeypatch):
    """An issue Dokima files carries the filed label the settings name.

    With `labels.filed: found-by-bot`, the issue a review files is created with found-by-bot, not filed-by-dokima.
    Proves 787.7."""
    record_property("proves", "787.7")
    repo("labels:\n  filed: found-by-bot\n")
    gh = fake(monkeypatch)
    lines = ap.file_issues(REPO, 57, reviewer_finding(), [])
    assert gh.created, f"787.7: no issue was filed: {lines}"
    got = [args[args.index("--label") + 1] for args in gh.created]
    assert got == ["found-by-bot"], f"787.7: the filed issue carries {got}, not found-by-bot as the settings say"

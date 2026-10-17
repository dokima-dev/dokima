"""Tests for #784: the audit judges required checks, labels and colors by the settings.

The daily audit (`python3 -m dokima.audit OWNER/REPO`) compares the repo's live labels, board pills, branch rule and
auto-merge lists with what Dokima needs. Here what Dokima needs comes from the merged settings: the shipped defaults
(`dokima/defaults.yaml`) with the repo's own `.dokima/settings.yaml` over them, read where the audit runs. Each audit
test runs the real command from outside against the fake `gh` of tests/fake_gh.py, through tests/test_audit_cli.py's
Audit helper, with a settings file written in the repo folder it runs in.

The settings these tests write, beside the ones the shipped defaults already hold:
    gates.required            check names; a repo's list merges with the default one by name
    merge.queue               false: the repo uses no merge queue (the default, true, keeps today's audit)
    labels.<key>              the name of each of Dokima's labels (autopilot, filed)
    colors.labels.<key>       each label's color, by the same key, as GitHub writes it (rrggbb)
    colors.pills.<field>.<option>  each board pill's color, as GitHub names it (GRAY, BLUE, RED ...)

The settings guard (`dokima.manifest.undeclared(root)`) is run on a temp repo root holding one code file and one
workflow file.
"""
import os
import re
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))
from test_audit_cli import Audit, FORBIDDEN, body_lines, clean, one_line  # noqa: E402

APP = 1  # the fake gh's app id
QUEUE = re.compile(r"merge queue", re.I)


def audit(tmp_path, name, state, settings, criterion):
    """Runs the audit once beside the settings text; returns the fake and Setup issue lines.

    The lines are every line of every Setup issue body the run opened or edited; none when it wrote no issue."""
    a = Audit(tmp_path / name, state)
    if settings is not None:
        (a.root / ".dokima").mkdir()
        (a.root / ".dokima" / "settings.yaml").write_text(textwrap.dedent(settings))
    a.run(criterion)
    s = a.state()
    touched = {str(w["number"]) for w in s["writes"] if w["kind"] in ("create", "edit")}
    lines = [l for n in sorted(touched) for l in body_lines(s["issues"][n]["body"])]
    return a, lines


def created(a):
    """The issues the run opened."""
    return [w["number"] for w in a.state()["writes"] if w["kind"] == "create"]


def word(w):
    """A pattern matching W as a whole word or name."""
    return re.compile(rf"(?<![\w-]){re.escape(w)}(?![\w-])")


# 784.1: the checks required on the default branch come from the required checks setting

def test_the_branch_rule_is_checked_against_the_required_checks_setting(record_property, tmp_path):
    """The audit wants main to require exactly the checks the required checks setting names.

    The repo's settings add a Lint check to the required checks. Where main requires all tests, Acceptance criteria and
    Lint, the audit says nothing about Lint; where main requires only the first two, it says, on one line, that main
    does not require Lint. Proves 784.1.
    """
    record_property("proves", "784.1")
    settings = """\
        gates:
          required: [Lint]
        """
    s = clean()
    s["protection"]["main"] = ["all tests", "Acceptance criteria", "Lint"]
    a, lines = audit(tmp_path, "required", s, settings, "784.1")
    flagged = [l for l in lines if word("Lint").search(l)]
    assert not flagged, (f"784.1: main requires Lint, which the required checks setting names, yet the audit "
                         f"flagged it: {flagged}\n{a.why()}")

    s = clean()
    s["protection"]["main"] = ["all tests", "Acceptance criteria"]
    a, lines = audit(tmp_path, "missing", s, settings, "784.1")
    one_line(lines, "784.1", "main not requiring the Lint check the settings name", "main", "Lint")


# 784.2: turning the merge queue off in a repo's settings stops the audit asking for one

def test_with_the_merge_queue_off_the_audit_never_asks_for_one(record_property, tmp_path):
    """With the merge queue off in settings, the Setup issue never mentions a merge queue.

    Dokima's app is on main's review exemption and the repo has no merge queue; one label is missing, so a Setup issue
    always opens. With the default settings the audit asks for the app on the merge queue's bypass list. With
    `merge.queue: false` no line of the Setup issue mentions a merge queue, and neither does it when GitHub refuses to
    list the repo's rulesets. Proves 784.2.
    """
    record_property("proves", "784.2")

    def repo(fail=None):
        s = clean()
        s["review_bypass_apps"] = [APP]
        s["rulesets"] = []
        del s["labels"]["filed-by-dokima"]
        if fail:
            s["fail"] = {"rulesets": fail}
        return s

    a, lines = audit(tmp_path, "default", repo(), None, "784.2")
    assert created(a), f"784.2: a missing label should open a Setup issue\n{a.why()}"
    assert any(QUEUE.search(l) for l in lines), \
        f"784.2: with the default settings the audit should still ask about the merge queue: {lines}\n{a.why()}"

    off = """\
        merge:
          queue: false
        """
    a, lines = audit(tmp_path, "off", repo(), off, "784.2")
    assert created(a), f"784.2: a missing label should open a Setup issue\n{a.why()}"
    asked = [l for l in lines if QUEUE.search(l)]
    assert not asked, f"784.2: with the merge queue off in settings, the audit still asks about one: {asked}\n{a.why()}"

    a, lines = audit(tmp_path, "refused", repo(FORBIDDEN), off, "784.2")
    assert created(a), f"784.2: a missing label should open a Setup issue\n{a.why()}"
    asked = [l for l in lines if QUEUE.search(l)]
    assert not asked, (f"784.2: with the merge queue off, a refused rulesets list still made the audit talk of a "
                       f"merge queue: {asked}\n{a.why()}")


# 784.3: Dokima's labels go by the names in the labels setting

def test_the_audit_wants_each_label_under_its_name_in_settings(record_property, tmp_path):
    """The audit looks for Dokima's autopilot label under the name the labels setting gives it.

    The repo's settings name the autopilot label dokima-autopilot. A repo holding dokima-autopilot, with the autopilot
    label's color and description, and no label called autopilot, gets no line about labels. A repo holding only a
    label called autopilot gets one line saying dokima-autopilot is missing. Proves 784.3.
    """
    record_property("proves", "784.3")
    settings = """\
        labels:
          autopilot: dokima-autopilot
        """
    s = clean()
    s["labels"]["dokima-autopilot"] = s["labels"].pop("autopilot")
    a, lines = audit(tmp_path, "renamed", s, settings, "784.3")
    flagged = [l for l in lines if l.startswith("Label")]
    assert not flagged, (f"784.3: the repo holds dokima-autopilot, the name its settings give the autopilot label, "
                         f"yet the audit flagged labels: {flagged}\n{a.why()}")

    a, lines = audit(tmp_path, "old-name", clean(), settings, "784.3")
    line = one_line(lines, "784.3", "the missing dokima-autopilot label", "dokima-autopilot")
    assert "missing" in line, f"784.3: the line about dokima-autopilot should say it is missing: {line}"


# 784.4: label colors that match the repo's settings are not flagged

def test_a_label_color_matching_settings_is_not_flagged(record_property, tmp_path):
    """The audit takes each label's color from the settings, not from code.

    The repo's settings give the autopilot label the color 0e8a16. A repo whose autopilot label is 0e8a16 gets no line
    about that label; one whose autopilot label still has the shipped 8250df gets one line naming both colors. Proves 784.4.
    """
    record_property("proves", "784.4")
    settings = """\
        colors:
          labels:
            autopilot: 0e8a16
        """
    s = clean()
    s["labels"]["autopilot"]["color"] = "0e8a16"
    a, lines = audit(tmp_path, "match", s, settings, "784.4")
    flagged = [l for l in lines if word("autopilot").search(l) and l.startswith("Label")]
    assert not flagged, (f"784.4: the autopilot label's color matches the settings, yet the audit flagged it: "
                         f"{flagged}\n{a.why()}")

    s = clean()
    s["labels"]["autopilot"]["color"] = "8250df"
    a, lines = audit(tmp_path, "differs", s, settings, "784.4")
    one_line(lines, "784.4", "the autopilot label's color off from the settings", "autopilot", "8250df", "0e8a16")


# 784.5: pill colors that match the repo's settings are not flagged

def test_a_pill_color_matching_settings_is_not_flagged(record_property, tmp_path):
    """The audit takes each board pill's color from the settings, not from code.

    The repo's settings make the Needs you pill blue. A board whose Needs you option is BLUE gets no line about it; one
    whose Needs you option is still the shipped RED gets one line naming both colors. Proves 784.5.
    """
    record_property("proves", "784.5")
    settings = """\
        colors:
          pills:
            Action:
              Needs you: BLUE
        """
    s = clean()
    s["fields"]["Action"]["Needs you"]["color"] = "BLUE"
    a, lines = audit(tmp_path, "match", s, settings, "784.5")
    flagged = [l for l in lines if "Needs you" in l]
    assert not flagged, (f"784.5: the Needs you pill's color matches the settings, yet the audit flagged it: "
                         f"{flagged}\n{a.why()}")

    s = clean()
    s["fields"]["Action"]["Needs you"]["color"] = "RED"
    a, lines = audit(tmp_path, "differs", s, settings, "784.5")
    one_line(lines, "784.5", "the Needs you pill's color off from the settings", "Needs you", "RED", "BLUE")


# 784.6: the settings guard no longer flags a workflow's name, compared in code, as a missing check

def guard_root(tmp_path, name, code):
    """The guard's lines on a repo holding a board workflow and one code file."""
    from dokima import manifest
    root = tmp_path / name
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "board.yml").write_text(textwrap.dedent("""\
        name: board
        on:
          workflow_dispatch:
        jobs:
          move:
            runs-on: ubuntu-24.04
            steps:
              - run: echo moving
        """))
    (root / "dokima").mkdir()
    (root / "dokima" / "look.py").write_text(textwrap.dedent(code))
    return manifest.undeclared(str(root))


def test_the_guard_passes_a_workflow_name_compared_in_code(record_property, tmp_path):
    """The settings guard tells a workflow's name from a check's name.

    Code that finds a run by the name of a workflow the repo holds, board, gets no line from the guard; code that finds
    a run by lint, which is neither a workflow nor a required check, is still named. Proves 784.6.
    """
    record_property("proves", "784.6")
    lines = guard_root(tmp_path, "workflow", """\
        def last(runs):
            return next(r for r in runs if r["name"] == "board")
        """)
    assert lines == [], f"784.6: the guard flagged the board workflow's name as a missing check: {lines}"

    lines = guard_root(tmp_path, "check", """\
        def last(runs):
            return next(r for r in runs if r["name"] == "lint")
        """)
    assert any(word("lint").search(l) and "dokima/look.py" in l for l in lines), \
        f"784.6: lint is neither a workflow nor a required check, and the guard no longer names it: {lines}"


# 784.7: the settings declare no label as one that starts an agent

def test_the_shipped_settings_declare_no_plan_or_work_label(record_property, tmp_path):
    """The shipped settings no longer name a plan or work label.

    Comments start the planner and the worker, not labels. Reads the settings of a repo with no settings file and
    checks the labels setting holds neither plan nor work. Proves 784.7.
    """
    record_property("proves", "784.7")
    from dokima import settings
    labels = settings.read(str(tmp_path), warn=lambda message: None).get("labels") or {}
    starting = sorted(k for k in ("plan", "work") if k in labels or k in labels.values())
    assert not starting, f"784.7: the shipped settings still declare labels that started agents: {starting} in {labels}"

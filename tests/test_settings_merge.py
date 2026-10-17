"""Dokima reads its shipped defaults, merges a repo's settings over them, and checks them (#793).

Story 1 of #779, part of #740. Every test runs the settings reader the way a workflow will, from outside:
`python3 -m dokima.settings` in a temp repo prints the merged settings as JSON on standard output and its warnings on
standard error; a locked setting makes it exit non-zero, naming the setting. The repo's file is
`.dokima/settings.yaml`; the defaults are `dokima/defaults.yaml`, shipped beside the reader. Tests write the YAML as
plain text, so no test needs PyYAML itself, and each failure names its criterion.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCKED = ("app_only_identity", "keys_from_main", "fence", "judge_runs_main_copy", "owner_approval")


def settings(repo, text=None, package=ROOT):
    """(exit code, merged settings or None, standard error) of the reader run in REPO.

    TEXT, when given, is written as the repo's `.dokima/settings.yaml` first. PACKAGE is the folder Python finds
    `dokima` in: this checkout, or a copy with its own defaults file."""
    os.makedirs(repo, exist_ok=True)
    if text is not None:
        os.makedirs(os.path.join(repo, ".dokima"), exist_ok=True)
        with open(os.path.join(repo, ".dokima", "settings.yaml"), "w") as f:
            f.write(text)
    env = {**os.environ, "PYTHONPATH": str(package)}
    p = subprocess.run([sys.executable, "-m", "dokima.settings"], cwd=repo, env=env, capture_output=True, text=True,
                       timeout=60)
    try:
        got = json.loads(p.stdout) if p.returncode == 0 else None
    except ValueError:
        got = None
    return p.returncode, got, p.stderr


def merged(crit, repo, text=None, package=ROOT):
    """The merged settings for REPO; fails the test, naming CRIT, when none are printed."""
    code, got, err = settings(repo, text, package)
    assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
    return got


def defaults(crit, tmp_path):
    """The settings a repo with no settings file gets: the shipped defaults alone."""
    got = merged(crit, str(tmp_path / "bare"))
    assert len(got) >= 10, f"{crit}: the shipped defaults hold only {sorted(got)}"
    return got


def name(entry):
    """An entry's name: the text itself, or a map's name field."""
    return entry.get("name") if isinstance(entry, dict) else entry


def probe_package(tmp_path, text):
    """A copy of Dokima whose defaults file holds TEXT; returns the folder for Python's path."""
    pkg = tmp_path / "pkg"
    shutil.copytree(os.path.join(ROOT, "dokima"), pkg / "dokima",
                    ignore=shutil.ignore_patterns("__pycache__", "icons", "roles"))
    (pkg / "dokima" / "defaults.yaml").write_text(text)
    return str(pkg)


PROBE = "branch:\n  default: trunk\nprobe:\n  value: 7\n"


def test_a_repo_with_no_settings_file_runs_on_the_shipped_defaults_file(tmp_path, record_property):
    """A repo with no settings file gets exactly what Dokima's shipped defaults file says.

    Swaps the shipped defaults file, in a copy of Dokima, for a two-setting probe, runs the reader in a repo with no
    settings file, and checks it prints the probe's settings and nothing else. Proves 793.1."""
    record_property("proves", "793.1")
    got = merged("793.1", str(tmp_path / "repo"), None, probe_package(tmp_path, PROBE))
    assert got == {"branch": {"default": "trunk"}, "probe": {"value": 7}}, \
        f"793.1: with no settings file the repo did not get the shipped defaults file's settings: {got}"


def test_an_empty_settings_file_falls_back_to_the_shipped_defaults(tmp_path, record_property):
    """An empty settings file changes nothing: the repo still gets the shipped defaults.

    Same probe as the main test, with an empty settings file in the repo. Proves 793.1."""
    record_property("proves", "793.1")
    got = merged("793.1", str(tmp_path / "repo"), "", probe_package(tmp_path, PROBE))
    assert got == {"branch": {"default": "trunk"}, "probe": {"value": 7}}, \
        f"793.1: an empty settings file did not fall back to the shipped defaults: {got}"


def test_a_repo_file_changes_only_the_setting_it_names(tmp_path, record_property):
    """A repo that sets one setting changes it and leaves every other at its default.

    Reads the shipped defaults, then a repo that sets only the records branch, and compares every other setting. Proves 793.2."""
    record_property("proves", "793.2")
    want = defaults("793.2", tmp_path)
    got = merged("793.2", str(tmp_path / "repo"), "records:\n  branch: history\n")
    assert got.get("records", {}).get("branch") == "history", f"793.2: the named setting was not changed: {got}"
    assert sorted(got) == sorted(want), f"793.2: the groups changed: {sorted(got)} != {sorted(want)}"
    changed = sorted(k for k in want if k != "records" and got[k] != want[k])
    assert not changed, f"793.2: settings the repo did not name changed: {changed}"
    others = {k: v for k, v in got["records"].items() if k != "branch"}
    assert others == {k: v for k, v in want["records"].items() if k != "branch"}, \
        f"793.2: the other records settings changed: {others}"


def test_the_shipped_defaults_hold_the_owners_list(tmp_path, record_property):
    """The shipped defaults hold each setting of the owner's list, with its listed default.

    Reads the shipped defaults with no settings file and checks each setting rebuilt from the owner's list on #740,
    one by one, naming every one that is missing or wrong. Proves 793.3."""
    record_property("proves", "793.3")
    d = defaults("793.3", tmp_path)
    assert os.path.isfile(os.path.join(ROOT, "dokima", "defaults.yaml")), "793.3: no shipped dokima/defaults.yaml"

    def at(path):
        v = d
        for part in path.split("."):
            if not isinstance(v, dict) or part not in v:
                return KeyError
            v = v[part]
        return v

    want = {
        "tests.tag": "record_property",
        "tests.dir": "tests",
        "tests.file_pattern": "test_*.py",
        "tests.run_one": "python -m pytest -q -p no:cacheprovider {test}",
        "tests.run_all": "pytest -q -p no:cacheprovider -n auto tests",
        "tests.new_test_timeout_s": 60,
        "tests.affected": "testmon",
        "setup.test_tools": "pytest pytest-xdist pytest-testmon",
        "setup.python": "3.12",
        "fence.test_setup_files": ["conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"],
        "protected_paths": [".github/"],
        "branch.default": "",
        "records.branch": "logs",
        "owner_docs": "AGENTS.md",
        "style.docstrings": "required",
        "style.docstring_cap": 15,
        "style.code_docstring_cap": 15,
        "style.caps": {"summary": 20, "user_story": 20, "criterion": 20, "nfr_why": 12, "feature": 25,
                       "story_title": 10, "story_user_story": 20, "raise_label": 4, "question": 20, "blocker": 30,
                       "issue": 25, "evidence": 20, "answer_why": 20, "previous_step": 15, "work_evidence": 15,
                       "test_change": 15},
        "river.max_blocks": 3,
        "planner.max_questions": 3,
        "gates.required": ["all tests", "Acceptance criteria"],
        "labels": {"autopilot": "autopilot", "filed": "filed-by-dokima"},  # no plan or work label (#784, #515)
        "merge.method": "squash",
        "gate.checks_wait_min": 45,
        "roles.planner.max_turns": 100,
        "roles.worker.max_turns": 100,
        "roles.reviewer.max_turns": 100,
    }
    wrong = [f"{k}: {at(k)!r}, not {v!r}" for k, v in want.items() if at(k) != v]
    not_text = at("text_only.not_text")
    if not (isinstance(not_text, list) and ".github/" in not_text and {"tests", "tests/"} & set(not_text)
            and not any("dokima/roles" in str(x) for x in not_text)):
        wrong.append(f"text_only.not_text: {not_text!r}, not the test folder and .github/ without dokima/roles/")
    append = at("prompts.append")
    if not (isinstance(append, list) and ".dokima/house-rules.md" in json.dumps(append)):
        wrong.append(f"prompts.append: {append!r}, not the house rules file .dokima/house-rules.md")
    for k in ("setup.install", "bot.slug", "card.icon_base", "gate.exclude"):
        if at(k) is KeyError:
            wrong.append(f"{k}: missing")
    assert not wrong, "793.3: the shipped defaults miss or change settings of the owner's list:\n" + "\n".join(wrong)


def test_a_group_in_the_repo_file_merges_key_by_key(tmp_path, record_property):
    """Setting one key of a group keeps the group's other keys at their defaults.

    Sets only the test folder in the tests group and checks the group is the default group with that one key changed. Proves 793.4."""
    record_property("proves", "793.4")
    want = defaults("793.4", tmp_path)
    got = merged("793.4", str(tmp_path / "repo"), "tests:\n  dir: spec\n")
    assert got.get("tests") == {**want["tests"], "dir": "spec"}, \
        f"793.4: the tests group did not merge key by key with the repo winning: {got.get('tests')}"


def test_a_group_two_levels_down_merges_key_by_key(tmp_path, record_property):
    """Setting one word cap keeps every other cap and style setting at its default.

    Sets only the summary cap inside the style group's caps and checks both levels kept their other keys. Proves 793.4."""
    record_property("proves", "793.4")
    want = defaults("793.4", tmp_path)
    got = merged("793.4", str(tmp_path / "repo"), "style:\n  caps:\n    summary: 30\n")
    style = got.get("style", {})
    assert style.get("caps") == {**want["style"]["caps"], "summary": 30}, \
        f"793.4: the caps did not merge key by key: {style.get('caps')}"
    assert {k: v for k, v in style.items() if k != "caps"} == {k: v for k, v in want["style"].items() if k != "caps"}, \
        f"793.4: the other style settings changed: {style}"


def test_a_list_in_the_repo_file_replaces_the_default_list(tmp_path, record_property):
    """A repo's protected paths list replaces the default list whole, keeping nothing of it.

    The default list holds .github/; the repo names only infra/, and the merged list must be exactly that. Proves 793.5."""
    record_property("proves", "793.5")
    want = defaults("793.5", tmp_path)
    assert want.get("protected_paths") and want["protected_paths"] != ["infra/"], \
        f"793.5: the defaults hold no protected paths list to replace: {want.get('protected_paths')}"
    got = merged("793.5", str(tmp_path / "repo"), "protected_paths:\n  - infra/\n")
    assert got.get("protected_paths") == ["infra/"], \
        f"793.5: the repo's list did not replace the default whole: {got.get('protected_paths')}"


def test_an_empty_list_in_the_repo_file_empties_the_setting(tmp_path, record_property):
    """A repo that writes an empty list gets an empty list, not the default one.

    Empties the fence's test setup files and checks the merged list is empty. Proves 793.5."""
    record_property("proves", "793.5")
    want = defaults("793.5", tmp_path)
    assert want.get("fence", {}).get("test_setup_files"), "793.5: the defaults hold no test setup files to empty"
    got = merged("793.5", str(tmp_path / "repo"), "fence:\n  test_setup_files: []\n")
    assert got.get("fence", {}).get("test_setup_files") == [], \
        f"793.5: an empty list did not replace the default: {got.get('fence')}"


def test_gates_in_the_repo_file_merge_with_the_default_gates_by_name(tmp_path, record_property):
    """Adding a gate keeps every default gate, and a repeated gate appears once.

    The repo names one default gate again and one new gate; the merged gates are the defaults then the new one, in
    order, with no gate twice and none dropped. Proves 793.6."""
    record_property("proves", "793.6")
    want = defaults("793.6", tmp_path)
    assert want.get("gates", {}).get("required") == ["all tests", "Acceptance criteria"], \
        f"793.6: the default gates are not all tests and Acceptance criteria: {want.get('gates')}"
    got = merged("793.6", str(tmp_path / "repo"), "gates:\n  required:\n    - Acceptance criteria\n    - lint\n")
    assert got.get("gates", {}).get("required") == ["all tests", "Acceptance criteria", "lint"], \
        f"793.6: the gates did not merge by name: {got.get('gates')}"


def test_a_gate_named_like_a_default_replaces_it_in_place(tmp_path, record_property):
    """A repo gate named like a default gate takes its place; the others stay.

    The repo writes the all tests gate as a map with its own command; it replaces the default all tests gate in the
    first place, and Acceptance criteria stays second. Proves 793.6."""
    record_property("proves", "793.6")
    defaults("793.6", tmp_path)
    got = merged("793.6", str(tmp_path / "repo"),
                 "gates:\n  required:\n    - name: all tests\n      run: make test\n")
    assert got.get("gates", {}).get("required") == [{"name": "all tests", "run": "make test"}, "Acceptance criteria"], \
        f"793.6: a gate named like a default did not replace it in place: {got.get('gates')}"


def test_prompt_additions_in_the_repo_file_merge_with_the_default_ones_by_name(tmp_path, record_property):
    """A repo's new prompt addition comes after every default one, which all stay.

    The repo names one new addition; the merged additions are the default ones, unchanged, then the new one. Proves 793.7."""
    record_property("proves", "793.7")
    want = defaults("793.7", tmp_path)
    base = want.get("prompts", {}).get("append")
    assert isinstance(base, list) and base, f"793.7: the defaults hold no prompt additions: {base}"
    got = merged("793.7", str(tmp_path / "repo"),
                 "prompts:\n  append:\n    - name: team-style\n      file: docs/style.md\n")
    assert got.get("prompts", {}).get("append") == base + [{"name": "team-style", "file": "docs/style.md"}], \
        f"793.7: the prompt additions did not merge by name: {got.get('prompts')}"


def test_a_prompt_addition_named_like_a_default_replaces_it(tmp_path, record_property):
    """A prompt addition named like a default one takes its place; none appears twice.

    Writes an addition under the first default one's name, pointing at another file, and checks it replaced that
    default in place. Proves 793.7."""
    record_property("proves", "793.7")
    want = defaults("793.7", tmp_path)
    base = want.get("prompts", {}).get("append")
    assert isinstance(base, list) and base, f"793.7: the defaults hold no prompt additions: {base}"
    first = name(base[0])
    got = merged("793.7", str(tmp_path / "repo"),
                 f"prompts:\n  append:\n    - name: \"{first}\"\n      file: docs/rules.md\n")
    assert got.get("prompts", {}).get("append") == [{"name": first, "file": "docs/rules.md"}] + base[1:], \
        f"793.7: an addition named like a default did not replace it: {got.get('prompts')}"


def test_an_unknown_setting_warns_with_the_closest_known_name(tmp_path, record_property):
    """A misspelt setting shows a warning naming it and the closest known setting.

    The repo writes branch.defualt; the warning must name branch.defualt and suggest branch.default. Proves 793.8."""
    record_property("proves", "793.8")
    code, _, err = settings(str(tmp_path / "repo"), "branch:\n  defualt: trunk\n")
    assert "No module named" not in err, f"793.8: the settings reader does not exist:\n{err[-800:]}"
    assert "branch.defualt" in err, f"793.8: no warning names the unknown setting branch.defualt:\n{err[-800:]}"
    assert "branch.default" in err, f"793.8: the warning does not suggest branch.default:\n{err[-800:]}"


def test_an_unknown_group_warns_with_the_closest_known_group(tmp_path, record_property):
    """A misspelt group name shows a warning naming it and the closest known group.

    The repo writes recrods in place of records; the warning must name recrods and suggest records. Proves 793.8."""
    record_property("proves", "793.8")
    code, _, err = settings(str(tmp_path / "repo"), "recrods:\n  branch: history\n")
    assert "No module named" not in err, f"793.8: the settings reader does not exist:\n{err[-800:]}"
    assert "recrods" in err, f"793.8: no warning names the unknown group recrods:\n{err[-800:]}"
    assert "records" in err.replace("recrods", ""), f"793.8: the warning does not suggest records:\n{err[-800:]}"


def test_an_unknown_setting_is_ignored_and_the_run_goes_on(tmp_path, record_property):
    """A misspelt setting is left out and the reader still succeeds with the defaults.

    The repo writes branch.defualt; the reader must exit 0 and print exactly the shipped defaults. Proves 793.9."""
    record_property("proves", "793.9")
    want = defaults("793.9", tmp_path)
    got = merged("793.9", str(tmp_path / "repo"), "branch:\n  defualt: trunk\n")
    assert got == want, f"793.9: the unknown setting was not ignored: branch is {got.get('branch')}"


def test_an_unknown_group_is_ignored_and_the_run_goes_on(tmp_path, record_property):
    """A whole unknown group is left out and the reader still succeeds with the defaults.

    The repo writes a group Dokima does not know; the reader must exit 0 and print exactly the shipped defaults. Proves 793.9."""
    record_property("proves", "793.9")
    want = defaults("793.9", tmp_path)
    got = merged("793.9", str(tmp_path / "repo"), "zzz_unknown:\n  a: 1\n  b: [x]\n")
    assert got == want, f"793.9: the unknown group was not ignored: {sorted(set(got) - set(want))}"


def test_setting_a_locked_setting_fails_the_run_naming_it(tmp_path, record_property):
    """Each of the five locked settings, set by a repo, fails the run naming it.

    Sets each locked setting in turn and checks the reader exits non-zero and names it; a repo setting an open
    setting beside it still passes, so the check is not a refusal of every file. Proves 793.10."""
    record_property("proves", "793.10")
    merged("793.10", str(tmp_path / "open"), "records:\n  branch: history\n")
    missed = []
    for key in LOCKED:
        code, _, err = settings(str(tmp_path / key), f"integrity:\n  {key}: false\n")
        if code == 0 or f"integrity.{key}" not in err:
            missed.append(f"integrity.{key}: exit {code}, said {err.strip()[-300:]!r}")
    assert not missed, "793.10: a locked setting did not fail the run, naming it:\n" + "\n".join(missed)

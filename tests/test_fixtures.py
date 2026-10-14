"""Every approved fixture is drawn again offline and must match byte for byte.

#628, story 5 of #584.

A fixture is what the owner approved, frozen under `tests/fixtures/cards/` by `tools/visuals.py finalize`:

- `N.card.md`, the top card exactly as `card.render` drew it, beside `N.inputs.json`, `{"repo", "issue", "found"}`,
  the data it was drawn from;
- `N.comments.md`, the run and autopilot comments exactly as `draw` printed them, beside `N.comments.inputs.json`,
  `{"repo", "issue", "pr", "posts"}`.

`test_every_fixture_matches_its_approved_drawing` draws each one again with the real code and fails on any
difference, naming the fixture and its first differing line. The card is drawn by `card.render`; the comments by
`visuals.comments(inputs)` in `tools/visuals.py`, the same step `draw` and `finalize` use, so the test holds the very
code that made the fixture.

The first fixture is the card of issue 557 the owner approved, from branch `fixture/card-557` (commit e98dee4). There
it was saved as the whole issue text; here it is saved in finalize's shape: the card and its Definition of Done, as
`card.render` draws them, without the Original issue fold (the owner's own words, which the card code never draws)
and without the trailing blank line. Its `edge_case_sources`, which that branch kept beside `found`, sit inside
`found`, so `card.render(repo, issue, found)` alone draws it.

The folder the test reads can be pointed elsewhere with `DOKIMA_FIXTURES`, which is how the tests below run the real
fixture test on a copy they change.
"""
import difflib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dokima import agent, card  # noqa: E402

FOLDER = os.environ.get("DOKIMA_FIXTURES") or os.path.join(ROOT, "tests", "fixtures", "cards")
FIXTURE_TEST = "tests/test_fixtures.py::test_every_fixture_matches_its_approved_drawing"


def visuals():
    """The `tools/visuals.py` module of this checkout."""
    spec = importlib.util.spec_from_file_location("visuals", os.path.join(ROOT, "tools", "visuals.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saved(folder):
    """Every approved drawing in `folder`: the names of its `.card.md` and `.comments.md` files."""
    if not os.path.isdir(folder):
        return []
    return sorted(n for n in os.listdir(folder) if n.endswith(".card.md") or n.endswith(".comments.md"))


def first_difference(want, got):
    """Where `got` first differs from `want`, in plain words; None when they match."""
    if want == got:
        return None
    a, b = want.split("\n"), got.split("\n")
    for k, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            return f"line {k} differs.\n  approved: {x!r}\n  drawn:    {y!r}"
    k = min(len(a), len(b)) + 1
    if len(a) > len(b):
        return f"line {k} is missing from the drawing.\n  approved: {a[k - 1]!r}"
    return f"line {k} is extra in the drawing.\n  drawn:    {b[k - 1]!r}"


def redraw(folder, name):
    """Draw the fixture `name` of `folder` again from its saved inputs, with today's code."""
    stem = name[:-len(".comments.md")] if name.endswith(".comments.md") else name[:-len(".card.md")]
    if name.endswith(".comments.md"):
        with open(os.path.join(folder, f"{stem}.comments.inputs.json")) as f:
            inputs = json.load(f)
        tool = visuals()
        if not hasattr(tool, "comments"):
            pytest.fail(f"{name}: tools/visuals.py cannot draw comments offline yet: it has no comments(inputs)")
        return tool.comments(inputs)
    with open(os.path.join(folder, f"{stem}.inputs.json")) as f:
        inputs = json.load(f)
    return card.render(inputs["repo"], inputs["issue"], inputs["found"])


@pytest.mark.parametrize("name", saved(FOLDER))
def test_every_fixture_matches_its_approved_drawing(name):
    """Each approved fixture is drawn again from its saved data and matches byte for byte.

    Reads the fixture's saved inputs, draws it with today's code and compares it with the approved drawing; any
    difference fails, naming the fixture and its first differing line."""
    with open(os.path.join(FOLDER, name)) as f:
        want = f.read()
    where = first_difference(want, redraw(FOLDER, name))
    assert where is None, f"{name} no longer matches its approved drawing: {where}"


def comments_fixture(folder):
    """Save a small approved comments fixture, issue 9's two autopilot lines, in `folder`."""
    posts = [{"kind": "line", "url": "https://github.com/o/r/issues/9#issuecomment-1"},
             {"kind": "start", "url": "https://github.com/o/r/issues/9#issuecomment-2"}]
    with open(os.path.join(folder, "9.comments.inputs.json"), "w") as f:
        json.dump({"repo": "o/r", "issue": 9, "pr": None, "posts": posts}, f, indent=1)
    text = (f"# Autopilot comment {posts[0]['url']}\n\n{agent.AUTOPILOT_LINE}\n\n\n"
            f"# Autopilot comment {posts[1]['url']}\n\n{agent.AUTOPILOT_START_LINE}\n")
    with open(os.path.join(folder, "9.comments.md"), "w") as f:
        f.write(text)


def good_copy(tmp_path):
    """A folder with a copy of the 557 card fixture and a comments fixture."""
    folder = tmp_path / "fixtures"
    folder.mkdir()
    for name in ("557.card.md", "557.inputs.json"):
        shutil.copy(os.path.join(ROOT, "tests", "fixtures", "cards", name), folder / name)
    comments_fixture(str(folder))
    return folder


def change_line(path, k):
    """Change line k of the file at `path` by one character."""
    lines = path.read_text().split("\n")
    lines[k - 1] += "x"
    path.write_text("\n".join(lines))


def run_fixture_test(folder, env=None):
    """Run the real fixture test on `folder`; its exit code and output."""
    env = dict(os.environ, DOKIMA_FIXTURES=str(folder), PYTHONPATH=ROOT, **(env or {}))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", FIXTURE_TEST], cwd=ROOT,
                       env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def test_a_changed_fixture_fails_naming_its_first_differing_line(record_property, tmp_path):
    """A changed fixture fails the test, which names its first differing line.

    Proves 628.1. Runs the real fixture test on a copy of the approved fixtures: it must pass as they are. Then
    changes line 12 of the 557 card, and line 3 of a comments fixture, and checks each run fails naming that fixture
    and that line."""
    record_property("proves", "628.1")
    folder = good_copy(tmp_path)
    code, out = run_fixture_test(folder)
    assert code == 0, f"628.1: the fixture test failed on fixtures that match the code:\n{out[-3000:]}"
    change_line(folder / "557.card.md", 12)
    code, out = run_fixture_test(folder)
    assert code != 0, "628.1: the fixture test passed with line 12 of the 557 card changed"
    assert "557.card.md" in out and "line 12 differs" in out, \
        f"628.1: the failure does not name the 557 card's line 12:\n{out[-3000:]}"
    shutil.copy(os.path.join(ROOT, "tests", "fixtures", "cards", "557.card.md"), folder / "557.card.md")
    change_line(folder / "9.comments.md", 3)
    code, out = run_fixture_test(folder)
    assert code != 0, "628.1: the fixture test passed with line 3 of a comments fixture changed"
    assert "9.comments.md" in out and "line 3 differs" in out, \
        f"628.1: the failure does not name the comments fixture's line 3:\n{out[-3000:]}"


NO_NETWORK = '''"""Loaded with -p: any network call or `gh` run fails loudly, and is noted in USED."""
import os
import socket
import subprocess


def refuse(*args, **kwargs):
    open(os.environ["USED"], "a").write("network\\n")
    raise OSError("no network in the fixture test")


socket.socket.connect = refuse
socket.socket.connect_ex = refuse
socket.create_connection = refuse
socket.getaddrinfo = refuse
'''

FAKE_GH = '''#!/bin/sh
echo "gh $*" >> "$USED"
exit 1
'''


def test_the_fixture_test_runs_with_no_network(record_property, tmp_path):
    """The fixture test passes with the network cut off and no way to reach GitHub.

    Proves 628.2. Runs the real fixture test on a copy of the approved fixtures in a fresh Python whose sockets
    refuse to connect, with a `gh` first on the path that refuses too. Checks it passes, and that nothing tried the
    network or `gh`."""
    record_property("proves", "628.2")
    folder = good_copy(tmp_path)
    plug, bin_ = tmp_path / "plug", tmp_path / "bin"
    plug.mkdir()
    bin_.mkdir()
    (plug / "nonet.py").write_text(NO_NETWORK)
    (bin_ / "gh").write_text(FAKE_GH)
    (bin_ / "gh").chmod(0o755)
    used = tmp_path / "used.txt"
    env = {"PYTHONPATH": f"{plug}{os.pathsep}{ROOT}", "USED": str(used),
           "PATH": f"{bin_}{os.pathsep}{os.environ.get('PATH', '')}"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "nonet", FIXTURE_TEST],
                       cwd=ROOT, env=dict(os.environ, DOKIMA_FIXTURES=str(folder), **env), capture_output=True,
                       text=True, timeout=120)
    out = r.stdout + r.stderr
    tried = used.read_text() if used.exists() else ""
    assert not tried, f"628.2: the fixture test reached for the network or gh: {tried}"
    assert r.returncode == 0, f"628.2: the fixture test did not pass offline:\n{out[-3000:]}"


def test_todays_card_code_redraws_the_approved_557_card(record_property):
    """Today's card code draws the approved card of issue 557 exactly, byte for byte.

    Proves 628.3. Draws issue 557's card from its saved data with the real card code and compares it with the card
    the owner approved; any difference fails, naming the first differing line."""
    record_property("proves", "628.3")
    folder = os.path.join(ROOT, "tests", "fixtures", "cards")
    with open(os.path.join(folder, "557.card.md")) as f:
        want = f.read()
    where = first_difference(want, redraw(folder, "557.card.md"))
    assert where is None, f"628.3: today's card code does not draw the approved 557 card: {where}"

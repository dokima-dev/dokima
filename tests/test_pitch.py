import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
LEAD = "**Coding agents now out-code us on narrow tasks. The bottleneck is knowing their work is actually done.**"


def test_readme_and_wiki_lead_with_the_pitch(record_property):
    record_property("proves", "107.1")
    for path in ("README.md", "docs/wiki/Home.md"):
        lines = [l for l in open(os.path.join(ROOT, path)).read().splitlines() if l.strip()]
        assert lines[0].startswith("# ") and lines[1] == LEAD, f"107.1: {path} does not open with the pitch"
        assert "moves your effort from writing code to verifying it" in lines[2], f"107.1: {path} lacks the verification line"

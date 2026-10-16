"""A secret cut in half by the transcript's length limit never shows its start (#680).

The transcript cuts each tool's input to 2000 characters and each tool's result to 1500. Secrets must be removed
before that cut: a token cut in half no longer matches its full value, so its start would be published. Each test
places a 40-character token across the cut and checks that none of it shows, and that the cut itself still holds.
"""
import json

from dokima.agent_records import transcript

TOKEN = "ghs_Q7mK2pP9vL4nR8tW3bZ6cC1dF5hJ0aE2uI7o"


def write_log(tmp_path, entries):
    """Write one Claude session log holding ENTRIES; return the log root."""
    log = tmp_path / ".claude" / "p"
    log.mkdir(parents=True)
    (log / "s.jsonl").write_text("\n".join(json.dumps(x) for x in entries) + "\n")
    return str(tmp_path)


def test_a_secret_across_the_tool_input_cut_shows_none_of_its_start(record_property, tmp_path):
    """A token across the 2000-character tool input cut shows none of its characters.

    The command holds 1990 x's, then the 40-character token, then 3000 y's. Cutting first leaves the token's first
    ten characters in the transcript; removing secrets first leaves none. The y's must still be cut away. Proves 680.1."""
    record_property("proves", "680.1")
    assert len(TOKEN) == 40
    command = "x" * 1990 + TOKEN + "y" * 3000
    root = write_log(tmp_path, [{"message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": command}}]}}])
    t = transcript(root, [TOKEN])
    assert TOKEN[:10] not in t, "680.1: the start of a secret cut by the 2000-character tool input limit shows in the transcript"
    assert "x" * 1990 in t, "680.1: the tool input before the secret is missing from the transcript"
    assert "y" not in t.split("```")[1], "680.1: the tool input is no longer cut to 2000 characters"


def test_a_secret_across_the_tool_result_cut_shows_none_of_its_start(record_property, tmp_path):
    """A token across the 1500-character tool result cut shows none of its characters.

    The result holds 1490 x's, then the 40-character token, then 3000 y's. Cutting first leaves the token's first
    ten characters in the transcript; removing secrets first leaves none. The y's must still be cut away. Proves 680.2."""
    record_property("proves", "680.2")
    assert len(TOKEN) == 40
    result = "x" * 1490 + TOKEN + "y" * 3000
    root = write_log(tmp_path, [{"message": {"role": "user", "content": [
        {"type": "tool_result", "content": result}]}}])
    t = transcript(root, [TOKEN])
    assert TOKEN[:10] not in t, "680.2: the start of a secret cut by the 1500-character tool result limit shows in the transcript"
    assert "x" * 1490 in t, "680.2: the tool result before the secret is missing from the transcript"
    assert "y" not in t, "680.2: the tool result is no longer cut to 1500 characters"

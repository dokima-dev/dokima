"""Merge gate failures count toward the three-blocks stop, so repeated failures reach the owner.

Today a merge gate that fails after the code review approved always starts the worker again, however many times it
failed before, and the three-blocks stop counts only code reviews whose verdict blocks. So a gate that keeps failing
sends the work to the worker again and again, and never reaches the owner (#601).

These tests chain real `python3 -m dokima.agent next 57 OUT` runs, in-process, against the fake GitHub of
`tests/test_merge_gate.py`: each earlier run's record comment (OUT/comment.md, with the Next line `next` wrote) is
posted on the issue as the bot, then a worker record after it, so the history holds earlier gate failures exactly as
the real river leaves them. The owner's last word is the `/work` before the first build, unless a test says otherwise.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent  # noqa: E402
from dokima import agent_github  # noqa: E402
from test_merge_gate import CODE_REVIEW, N, OLD, OWNER, REPO, WORKER, FakeGitHub, red  # noqa: E402

BLOCK = {**CODE_REVIEW, "run_id": "40", "run": "https://github.com/o/r/actions/runs/40",
         "handback": {**CODE_REVIEW["handback"], "verdict": "block", "summary": "The code misses a case."}}


class History:
    """The issue's conversation as runs add to it, each record then its rebuild."""

    def __init__(self, tmp_path, monkeypatch, capsys):
        """Starts from the fake issue: plan, approval, the owner's `/work` and first build."""
        self.tmp, self.mp, self.cap = tmp_path, monkeypatch, capsys
        self.fake = FakeGitHub({OLD: red(OLD)})
        self.runs, self.minute = 0, 0

    def post(self, who, body):
        """Adds one comment to the issue, after every earlier one."""
        self.minute += 1
        self.fake.issue["comments"].append({"author": {"login": who}, "body": body,
                                            "createdAt": f"2026-10-13T11:{self.minute:02d}:00Z"})

    def decide(self, rec):
        """Runs `next 57` on the record and returns its output, Next line, board and comment."""
        self.runs += 1
        out = self.tmp / f"run{self.runs}"
        out.mkdir()
        json.dump(rec, open(out / "record.json", "w"))
        (out / "comment.md").write_text(agent.render(rec))
        fake = self.fake
        self.mp.setattr(agent_github, "gh", fake.gh)
        self.mp.setattr(time, "sleep", fake.sleep)
        self.mp.setattr(time, "time", lambda: fake.clock)
        self.mp.setattr(time, "monotonic", lambda: fake.clock)
        self.mp.setenv("GITHUB_REPOSITORY", REPO)
        self.mp.setenv("GITHUB_SERVER_URL", "https://github.com")
        self.mp.setenv("OWNERS", OWNER)
        self.cap.readouterr()
        try:
            agent.main(["dokima.agent", "next", N, str(out)])
        except Exception as e:  # noqa: BLE001 - reported by the test that asked
            raise AssertionError(f"deciding what follows the run crashed: {type(e).__name__}: {e}") from e
        finally:
            self.mp.undo()
        text = (out / "comment.md").read_text()
        line = next((l for l in text.splitlines() if l.startswith("**Next:**")), "")
        board = (out / "board.txt").read_text().strip() if (out / "board.txt").exists() else ""
        said = (self.cap.readouterr().out.strip().splitlines() or [""])[-1].strip()
        return said, line, board, text

    def sent_back(self, rec, why):
        """Runs `next` on a record that sends work back, then posts it and a rebuild."""
        said, line, _, text = self.decide(rec)
        assert said == "start worker", f"setup: {why} should start the worker, and printed {said!r} (Next: {line!r})"
        self.post(agent.BOT, text)
        self.post(agent.BOT, agent.render({**WORKER, "run_id": f"9{self.runs}"}))

    def gate_failed(self):
        """Posts an approving code review whose merge gate fails, then the worker's rebuild."""
        self.sent_back(CODE_REVIEW, "a failed merge gate")


def stopped_for_owner(result):
    """True when the run stopped, mentioned the owner and put the card in Needs you."""
    said, line, board, _ = result
    return said == "stop" and f"@{OWNER}" in line and board.endswith("needs")


def test_a_third_merge_gate_failure_in_a_row_stops_for_the_owner(record_property, tmp_path, monkeypatch, capsys):
    """A third merge gate failure in a row stops for the owner, not the worker.

    Proves 601.1.
    Two earlier gate failures, each followed by the worker's rebuild, sit in the history with no word from the owner
    since; the third failure must stop and mention the owner with Needs you, and not print `start worker`. Beside it,
    a second failure must still start the worker, so the stop is not "never send back", and a third failure after the
    owner spoke must start the worker too, since the count starts over when the owner speaks."""
    record_property("proves", "601.1")
    h = History(tmp_path, monkeypatch, capsys)
    h.gate_failed()
    second = h.decide(CODE_REVIEW)
    assert second[0] == "start worker", \
        f"601.1: the second merge gate failure in a row should still start the worker, and printed {second[0]!r} (Next: {second[1]!r})"
    h.post(agent.BOT, second[3])
    h.post(agent.BOT, agent.render({**WORKER, "run_id": "95"}))
    third = h.decide(CODE_REVIEW)
    assert stopped_for_owner(third), \
        (f"601.1: the merge gate failed a third time in a row with no word from the owner, and the run did not stop "
         f"for the owner: printed {third[0]!r}, Next {third[1]!r}, board {third[2]!r}")
    assert h.fake.merges == [], f"601.1: a pull request whose merge gate failed was merged: {h.fake.merges}"

    h = History(tmp_path / "spoke", monkeypatch, capsys)
    (tmp_path / "spoke").mkdir()
    h.gate_failed()
    h.gate_failed()
    h.post(OWNER, "/work")
    after = h.decide(CODE_REVIEW)
    assert after[0] == "start worker", \
        (f"601.1: the owner spoke after two merge gate failures, and the next failure did not start the worker: "
         f"printed {after[0]!r}, Next {after[1]!r}")


def test_gate_failures_and_blocking_code_reviews_count_together(record_property, tmp_path, monkeypatch, capsys):
    """Merge gate failures and blocking code reviews add up to the same three-blocks stop.

    Proves 601.2.
    A blocking code review, then a gate failure, then a third gate failure: three in a row, so the run must stop for
    the owner. Two gate failures, then a blocking code review: three in a row too, so the review must stop for the
    owner, not start the worker. Beside them, one blocking code review and then one gate failure, two in a row, must
    still start the worker."""
    record_property("proves", "601.2")
    h = History(tmp_path, monkeypatch, capsys)
    h.sent_back(BLOCK, "a blocking code review")
    two = h.decide(CODE_REVIEW)
    assert two[0] == "start worker", \
        (f"601.2: a blocking code review then one merge gate failure is two in a row and should start the worker, "
         f"and printed {two[0]!r} (Next: {two[1]!r})")
    h.post(agent.BOT, two[3])
    h.post(agent.BOT, agent.render({**WORKER, "run_id": "96"}))
    three = h.decide(CODE_REVIEW)
    assert stopped_for_owner(three), \
        (f"601.2: a blocking code review then two merge gate failures is three in a row, and the run did not stop for "
         f"the owner: printed {three[0]!r}, Next {three[1]!r}, board {three[2]!r}")

    h = History(tmp_path / "b", monkeypatch, capsys)
    (tmp_path / "b").mkdir()
    h.gate_failed()
    h.gate_failed()
    review = h.decide(BLOCK)
    assert stopped_for_owner(review), \
        (f"601.2: two merge gate failures then a blocking code review is three in a row, and the review did not stop "
         f"for the owner: printed {review[0]!r}, Next {review[1]!r}, board {review[2]!r}")

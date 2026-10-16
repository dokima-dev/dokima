"""#766: the unused card sample for issue 455 is deleted.

The file `docs/rendered/455.json` was a card fixture that nothing in the code,
tests or workflows read. This test checks it no longer exists in the repo.
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_unused_card_sample_is_deleted(record_property):
    """The card sample for issue 455 is no longer in the repo.

    Looks for `docs/rendered/455.json` from the repo root and fails while it is still there. Proves 766.1."""
    record_property("proves", "766.1")
    path = os.path.join(ROOT, "docs", "rendered", "455.json")
    assert not os.path.exists(path), "766.1: the unused card sample docs/rendered/455.json is still in the repo"

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import plan  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")


def read(path):
    return open(os.path.join(ROOT, path)).read()


def test_approve_only_means_merge(record_property):
    record_property("proves", "67.5")
    workflows = os.path.join(ROOT, ".github", "workflows")
    assert not os.path.exists(os.path.join(workflows, "build.yml"))
    import test_review_relay as trr
    relays = trr.review_relays()
    for name in os.listdir(workflows):
        if name == "board.yml":  # only moves board cards on a review; it never starts a build
            continue
        if name in relays:  # only tells board.yml a review came (#396); it starts nothing
            text = read(f".github/workflows/{name}")
            assert "uses: ./" not in text and "workflow run" not in text and "workflow_dispatch" not in text
            continue
        if name == "commands.yml":  # a review's command starts a stage, but never an Approve
            assert "github.event.review.state != 'approved'" in read(f".github/workflows/{name}")
            continue
        assert "pull_request_review" not in read(f".github/workflows/{name}")
    assert "Approve the plan" not in read("dokima/card.py")
    assert not hasattr(plan, "starts_build")

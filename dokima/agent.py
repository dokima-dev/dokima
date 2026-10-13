"""Packs and hand-back checks for running one agent by hand on a fresh machine.

`pack` builds the agent's starting pack from GitHub's records: the issue as it stands (body and every comment) and the
JSON hand-backs of earlier runs, downloaded from those runs. `check` is the deterministic check an agent runs on its own
hand-back before it finishes, and that code runs again after it: a malformed hand-back never reaches the next agent.
The plan's own check lives in dokima/planner.py; this module adds review.json and work.json.

Since #636 the code lives in one file per job, and this module re-exports every name, so importers and
`python3 -m dokima.agent` keep working as before: dokima/agent_github.py (the one GitHub helper), agent_records.py,
agent_checks.py, agent_roles.py, agent_autopilot.py and agent_next.py.
"""
import contextlib
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

from dokima import body as issue_body, card, manifest, raises, words
from dokima.card import field_icon, icon
from dokima import agent_github
from dokima.agent_github import (  # noqa: F401
    BOT, linked_prs, conversation, open_issues, BOT_LOGIN, parent_of, issue_of_pr, sub_issues, blocked_by,
    gh_reason, rate_limited, rate_limit_waited_once, NO_PERMISSION, pages)
from dokima.agent_records import (  # noqa: F401
    VERDICTS, FIXERS, OLD_FIELDS, PLAN_TEST_FAILS, MARK, LIVE, HANDBACK, name_of, records, latest, approved,
    approved_plan, is_record, open_blockers, old_blocker, open_raises, raises_for, settled, taken_ids, stamp_record,
    owner_raises, for_planner, LINKS, plan_links, build_record, not_started, cancelled, live_card, GOING,
    CARD_HEADS, UNRECORDED, card_stage, bot_cards, unrecorded_run, unrecorded, where_card, run_ahead, queue,
    role_icon, HEADS, review_name, who, bullets, pairs, files_changed, posted_before_raises, plan_rows,
    criterion_of, failed_rows, details, review_lines, opening, record_fold, answered_lines, raised_by, raised_lines,
    render, details_as_posted, opening_as_posted, render_as_posted, words_link, said, escape_line, jsonl_files,
    scrub, transcript, run_report, STATS, stats_tail, with_next, short, stats_line, footnote, models_used, filled,
    first_sentence)
from dokima.agent_checks import (  # noqa: F401
    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
    problems_size, problems_edge_cases, problems_asks, issue_url, owner_source, problems_work, problems_old,
    problems_raised, problems_items, problems_shape, plan_criteria, problems_plan, load, plan_tests,
    failing_plan_tests, check, worker_docstring_caps)
from dokima.agent_roles import (  # noqa: F401
    issue_text, open_issue_summary, reviewer_open_issues, pack_records, pack_issue, parent_words, pack_parent,
    owner_words, pack, NEEDS, problems_pack, COMMANDS, command_of, autopilot_of, route, main)
from dokima.agent_autopilot import (  # noqa: F401
    story_body, file_split, AUTOPILOT, issue_tree, switch_autopilot, autopilot_comment, AUTOPILOT_LINE,
    AUTOPILOT_START_LINE, link_edges, loop_through, named, FILED_LABEL, file_issues, record_links, set_title,
    PUSH_EVENTS, installations_link, stop_run, rerun_checks, started_before, start_planner, start_waiting,
    open_blockers_of, plans_again, start_unblocked, tree_done_comment, close_if_done, close_done_parents,
    close_done_trees, autopilot_closed, AUTOPILOT_LINES, UNREAD, on_autopilot, WORKFLOWS, PASSING, approves_work,
    work_approved, CHECKS_WAIT, CHECKS_PAUSE, BOARD_WAIT, superseded, required_checks, unproven, proof, UPDATE_WAIT,
    UPDATE_PAUSE, merge_gate, behind_main, held_for_approval, try_merge, open_pr, AUTOPILOT_MERGE, MERGE_STATE,
    merge_outcome, automerge, unconfirmed_comment, merge_tree)
from dokima.agent_next import (  # noqa: F401
    agents_text, said_there, not_accepted, quoted, unanswered, clash_pending, MAX_QUESTIONS, next_step, waiting,
    queued_since, waits_on_owner, criteria_texts, test_fix, STAGE_COLUMN, started, board_place, next_line)


def __getattr__(name):
    """`gh` is always the one helper's current `dokima.agent_github.gh`, so faking it there fakes `agent.gh` too."""
    if name == "gh":
        return agent_github.gh
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except subprocess.CalledProcessError as e:
        # GitHub's own error, so the step that failed can say why.
        sys.stderr.write((e.stderr or str(e)).strip() + "\n")
        sys.exit(1)

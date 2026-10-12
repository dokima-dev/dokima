"""Temporary: skip the slow tests (each 1 second or more) so the suite runs in about a minute.

Five end-to-end replays stay: a command starts its agent or says why, a card goes queued to done,
autopilot stops where the owner must decide, a failed run gets Needs you, a cancelled run says so.
The parked test-speed issue makes the rest fast and deletes this file. DOKIMA_ALL_TESTS=1 runs everything.
"""
import os
import sys

import pytest

# Tests judge this checkout's code on any machine (#449, #385). The agent's machine points Python at a runtime
# copy of Dokima and sets its own run's settings; none of that may reach a test or a subprocess it starts.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for k in ("STAGE", "ROLE", "N", "PACK", "OUT", "CARD_ID", "GITHUB_REPOSITORY", "PYTHONSAFEPATH"):
    os.environ.pop(k, None)
os.environ["PYTHONPATH"] = ROOT
sys.path[:] = [ROOT] + [x for x in sys.path if os.path.abspath(x or ".") != "/tmp/runtime"]

SLOW = {
    "test_automerge.py::test_a_pull_request_changing_a_workflow_file_never_merges_by_autopilot",
    "test_automerge.py::test_a_refused_merge_stops_for_the_owner_and_says_why",
    "test_automerge.py::test_autopilot_start_merges_a_pull_request_already_approved",
    "test_automerge.py::test_autopilot_start_merges_the_approved_pull_requests_of_the_whole_tree",
    "test_automerge.py::test_nothing_merges_unless_every_check_on_the_merging_commit_is_green",
    "test_automerge.py::test_on_autopilot_an_approved_pull_request_with_green_checks_merges_and_says_so",
    "test_automerge.py::test_without_autopilot_an_approved_pull_request_waits_for_the_owner",
    "test_autopilot.py::test_autopilot_start_puts_the_issue_and_every_sub_issue_at_every_level_on_autopilot",
    "test_autopilot.py::test_autopilot_starts_no_stage_and_says_which_issues_it_switched",
    "test_autopilot.py::test_autopilot_stop_takes_the_same_tree_off_autopilot",
    "test_autopilot.py::test_only_a_code_owners_autopilot_counts",
    "test_autopilot_close.py::test_a_child_planned_running_or_done_is_never_started_again",
    "test_autopilot_close.py::test_a_close_deep_in_the_tree_starts_its_waiting_siblings",
    "test_autopilot_close.py::test_a_close_off_autopilot_does_nothing",
    "test_autopilot_close.py::test_a_close_starts_every_sibling_whose_blockers_have_all_merged",
    "test_autopilot_close.py::test_a_close_whose_run_github_drops_from_the_queue_still_counts",
    "test_autopilot_close.py::test_a_split_filed_on_autopilot_starts_its_unblocked_stories",
    "test_autopilot_close.py::test_a_tree_two_levels_deep_closes_level_by_level_and_goes_off_autopilot",
    "test_autopilot_close.py::test_autopilot_goes_off_for_the_whole_tree_when_it_is_done",
    "test_autopilot_close.py::test_autopilot_start_on_a_parent_picks_up_the_children_waiting",
    "test_autopilot_close.py::test_autopilot_start_picks_up_waiting_issues_at_every_level",
    "test_autopilot_close.py::test_the_parent_closes_when_its_last_sub_issue_closes",
    "test_autopilot_river.py::test_an_assumption_is_accepted_only_on_words_the_owner_really_said",
    "test_autopilot_river.py::test_autopilot_start_starts_the_worker_on_a_plan_already_waiting_for_work",
    "test_autopilot_river.py::test_off_autopilot_an_approved_plan_or_split_still_stops_for_the_owner",
    "test_autopilot_river.py::test_on_autopilot_an_accepted_assumption_goes_on_and_one_not_accepted_stops",
    "test_autopilot_river.py::test_on_autopilot_an_approved_plan_starts_the_worker_with_one_autopilot_line",
    "test_autopilot_river.py::test_on_autopilot_an_approved_split_files_its_stories_with_one_autopilot_line",
    "test_autopilot_river.py::test_when_autopilot_cannot_be_read_the_river_stops_and_says_why",
    "test_autopilot_start.py::test_a_new_issue_on_autopilot_ends_merged_with_no_command_from_the_owner",
    "test_autopilot_start.py::test_autopilot_start_never_starts_the_issue_itself_where_it_must_not",
    "test_autopilot_start.py::test_autopilot_start_still_picks_up_what_waits_in_the_tree",
    "test_autopilot_start.py::test_saying_autopilot_start_twice_starts_the_planner_once",
    "test_blocked_worker.py::test_a_worker_already_started_is_never_started_again",
    "test_blocked_worker.py::test_on_autopilot_a_blocked_plan_waits_with_one_line_and_mentions_no_one",
    "test_blocked_worker.py::test_only_an_approved_newest_plan_starts_its_worker",
    "test_blocked_worker.py::test_the_last_blocker_closing_starts_the_waiting_worker_once",
    "test_hand_links.py::test_a_card_says_when_github_cannot_list_its_links",
    "test_hand_links.py::test_a_link_removed_by_hand_leaves_both_cards_on_a_change_to_either_issue",
    "test_hand_links.py::test_a_link_removed_by_hand_leaves_both_cards_with_no_comment",
    "test_hand_links.py::test_a_loop_through_other_issues_names_every_issue_on_every_card_in_it",
    "test_hand_links.py::test_a_run_for_one_issue_rewrites_no_other_card_whose_links_did_not_change",
    "test_hand_links.py::test_any_redraw_shows_the_links_github_has_right_then",
    "test_hand_links.py::test_on_autopilot_a_hand_made_loop_stops_the_river_for_the_owner_once",
    "test_hand_links.py::test_the_loop_line_stays_on_a_later_redraw_and_leaves_once_the_loop_is_gone",
    "test_hand_links.py::test_the_scheduled_run_goes_on_when_one_issue_cannot_be_read",
    "test_hand_links.py::test_the_scheduled_run_redraws_only_cards_whose_links_changed",
    "test_hand_links.py::test_two_issues_blocking_each_other_by_hand_are_named_on_both_cards",
    "test_handback_check.py::test_every_blocker_is_about_one_of_the_plans_criteria_and_its_tests",
    "test_handback_check.py::test_well_formed_hand_backs_pass_and_every_malformed_field_is_named",
    "test_live_card.py::test_the_card_says_working_with_its_start_time_when_the_agent_starts",
    "test_live_queue.py::test_a_card_says_it_is_waiting_for_the_run_ahead_of_it",
    "test_live_queue.py::test_a_code_owners_command_puts_up_a_queued_card_that_the_run_then_updates",
    "test_live_queue.py::test_every_hand_off_and_split_uses_the_same_one_card",
    "test_live_queue.py::test_only_a_code_owners_command_puts_up_a_card",
    "test_new_test_check.py::test_a_new_test_that_hangs_is_stopped_and_rejected_naming_it",
    "test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so[marked",
    "test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so[passes]",
    "test_new_test_check.py::test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so[skips",
    "test_new_test_check.py::test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it[blank]",
    "test_new_test_check.py::test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it[empty]",
    "test_new_test_check.py::test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it[no",
    "test_new_test_check.py::test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it[two",
    "test_new_test_check.py::test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it[wrapped",
    "test_new_test_check.py::test_a_renamed_older_test_needs_a_reason_under_its_old_name_and_nothing_more",
    "test_parent_source.py::test_on_autopilot_the_owners_words_in_the_parent_count_as_really_said",
    "test_plan_check.py::test_a_source_outside_this_issue_is_rejected_and_named[other",
    "test_plan_check.py::test_anything_but_a_story_or_a_feature_is_rejected_saying_the_planner_always_hands_back_a_plan[no",
    "test_plan_check_rerun.py::test_a_reapproved_plan_with_no_new_commit_ends_with_a_passing_plan_check",
    "test_plan_check_rerun.py::test_only_an_approval_with_an_open_pull_request_runs_the_plan_check_again",
    "test_plan_check_rerun.py::test_the_plan_check_runs_again_only_with_the_apps_key_after_the_agent_finished",
    "test_plan_links_recorded.py::test_a_blocking_link_the_new_approved_plan_dropped_is_removed",
    "test_plan_links_recorded.py::test_a_dropped_link_leaves_both_cards",
    "test_plan_links_recorded.py::test_a_link_github_already_has_is_not_added_twice",
    "test_plan_links_recorded.py::test_a_link_github_fails_to_remove_stops_the_river_and_says_why",
    "test_plan_links_recorded.py::test_a_plan_the_review_blocks_records_nothing",
    "test_plan_links_recorded.py::test_a_relates_to_link_switched_to_blocks_moves_on_the_other_card",
    "test_plan_links_recorded.py::test_a_replan_the_review_blocks_removes_nothing",
    "test_plan_links_recorded.py::test_an_approved_plan_records_its_blocking_links_on_github",
    "test_plan_links_recorded.py::test_both_cards_show_every_new_link_from_their_own_side",
    "test_plan_links_recorded.py::test_links_with_no_loop_are_recorded_and_autopilot_goes_on",
    "test_plan_links_recorded.py::test_recorded_links_let_autopilot_go_on",
    "test_plan_links_recorded.py::test_the_other_card_keeps_the_link_after_its_own_redraw",
    "test_plan_links_recorded.py::test_turning_a_link_around_is_not_a_loop",
    "test_questions.py::test_a_question_that_is_anything_else_is_rejected_saying_which_and_why[a",
    "test_questions.py::test_a_question_that_is_anything_else_is_rejected_saying_which_and_why[an",
    "test_questions.py::test_a_question_that_is_anything_else_is_rejected_saying_which_and_why[no",
    "test_questions.py::test_a_question_with_its_assumption_passes_the_check[story]",
    "test_start.py::test_a_failed_command_says_why_and_stops_for_the_owner",
    "test_start.py::test_a_reviewed_split_stops_for_the_owner_and_files_nothing_before_work",
    "test_start.py::test_a_start_failure_still_fails_the_run",
    "test_start.py::test_the_plan_reviewer_starts_on_a_split_with_no_try_branch",
    "test_summary_caps.py::test_the_planners_summary_is_one_sentence_of_at_most_25_words",
    "test_word_caps.py::test_a_criterion_over_25_words_in_its_first_sentence_is_held_to_the_cap",
    "test_word_caps.py::test_a_docstring_the_planner_adds_is_held_to_15_words_in_its_first_line",
    "test_word_caps.py::test_a_new_test_must_name_its_criterion_by_number[no",
    "test_worker_pr.py::test_only_a_finished_worker_opens_a_pull_request_and_only_when_none_is_open",
}


def pytest_collection_modifyitems(config, items):
    if os.environ.get("DOKIMA_ALL_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="slow, parked until the test-speed issue")
    for item in items:
        if item.nodeid.split("[")[0].removeprefix("tests/") in SLOW:
            item.add_marker(skip)

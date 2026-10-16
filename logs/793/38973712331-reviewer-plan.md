# reviewer (plan) for #793

Run: https://github.com/dokima-dev/dokima/actions/runs/38973712331

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> owner_words.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #793: Settings read from shipped defaults, merged and checked
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [794], "loop": []} -->
> Dokima reads its shipped defaults, merges a repo's settings over them, warns on typos and refuses locked settings.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/793#issuecomment-6225481830) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/794
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/741
> 
> 
> **User story:** A repo writes only what differs, and Dokima merges it over its defaults, warning on typos.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance crit

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('owner_words.json'));print(json.dumps(d,indent=1)[:8000])"; echo; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:6000])"; head -c 1500 open_issues.json; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(list(d.keys())); print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/779": "<!-- dokima-card -->\n<!-- /dokima-card -->\n\n<details open><summary>From the approved plan of #740, story 1</summary>\n\n**Part of:** #740 One settings file per repo over shipped defaults\n\n**User story:** A repo writes only what differs into one settings file, and every workflow follows it.\n\n**Context:** New `dokima/settings.py` reads `dokima/defaults.yaml` and `.dokima/settings.yaml` with PyYAML (owner allowed it). Today `dokima/setup.py` `read_settings()` reads only nested maps and `write_settings()` rewrites the file; `dokima/agents.py` reads `.dokima/agents.yml`. Workflow rows of the owner's list (A13 to A19, B3, B5, C3, C4, E1, E2, E4, E8, E11, E15) live in `.github/workflows/agent.yml`, `full-suite.yml`, `acceptance-criteria.yml`, `testmon.yml`, `fix.yml`, `wiki.yml`; the co-author trailer sits at `agent.yml:408` and `wiki.yml:27`. Locked keys: app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. The owner's newer comment makes the fence's test setup files a setting (row A5); newer words win, so the fence's lock covers what it does, not that list.\n\n**Acceptance criteria:**\n- Dokima ships one defaults file that every repo's settings fall back to. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- A repo's settings file changes only the settings it names; every other keeps its default. ([source](https://github.com/dokima-dev/dokima/issues/740))\n- The d

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_settings_merge.py
```

> commit ff3f3efe6572a21c7cfd7102b99ecedfe2f9903f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 22:06:03 2026 +0000
> 
>     planner for #793 (run 38972830830)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_settings_merge.py | 331 +++++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 331 insertions(+)
> """Dokima reads its shipped defaults, merges a repo's settings over them, and checks them (#793).
> 
> Story 1 of #779, part of #740. Every test runs the settings reader the way a workflow will, from outside:
> `python3 -m dokima.settings` in a temp repo prints the merged settings as JSON on standard output and its warnings on
> standard error; a locked setting makes it exit non-zero, naming the setting. The repo's file is
> `.dokima/settings.yaml`; the defaults are `dokima/defaults.yaml`, shipped beside the reader. Tests write the YAML as
> plain text, so no test needs PyYAML itself, and each failure names its criterion.
> """
> import json
> import os
> import shutil
> import subprocess
> import sys
> 
> ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
> LOCKED = ("app_only_identity", "keys_from_main", "fence", "judge_runs_main_copy", "owner_approval")
> 
> 
> def settings(repo, text=None, package=ROOT):
>     """(exit code, merged settings or None, standard error) of the reader run in REPO.
> 
>     TEXT, when given, is written as the repo's `.dokima/settings.yaml` first. PACKA

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q -p no:cacheprovider tests/test_settings_merge.py 2>&1 | grep -E "^(FAILED|E  .*79)|passed|failed" | head -40; python3 -c "import yaml" ; ls dokima | head -50
```

> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.1: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.1: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.2: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.3: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.4: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.4: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.5: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.5: reading the settin

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "41-row\|6219928729" --include=*.md --include=*.py --include=*.json . | grep -v "^./tests/test_settings_merge" | head; grep -rn "max_turns\|60 turns\|100" dokima/agent_claude.py | head; grep -rn "app_only_identity\|keys_from_main\|integrity" -r dokima rules | head
```

> dokima/agent_claude.py:26:                               "--max-turns", os.environ.get("DOKIMA_MAX_TURNS") or "100", "--output-format", "json"], stdout=f, env=env).returncode

**Agent:** I'm checking the owner's words for the turn limit and the YAML install, then I'll write the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "turns" AGENTS.md rules/ | head; grep -rn -i "pyyaml\|yaml" AGENTS.md rules/ | head; sed -n 20,35p .github/workflows/full-suite.yml; ls .dokima 2>/dev/null
```

> rules/splitting.md:3:- Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> rules/flow.md:7:5. **Code review.** The reviewer starts by itself when the worker finishes. Every blocker names who fixes it: the worker for code, the planner for a test shown too weak. A block sends it back to the worker by itself, or to the planner when any blocker is the planner's; that test fix goes planner, plan review, worker, code review, and an approved re-plan whose criteria are unchanged goes straight to the worker, while one that changes any criterion, or comes after the owner spoke, waits for `/work`. No test runs on the pull request while it is a draft, so none races the code review. An approval runs the merge gate: a branch behind main is brought up to date with it, the pull request is marked ready, and every check main requires runs on that head; a check only skipped proves nothing. A new build turns it back into a draft first. Any check failing sends it back to the worker by itself, and counts toward the three blocks in a row like a blocking review; checks that never finish, or a branch GitHub will not update, stop fo

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/740"
C=I+"#issuecomment-6219928729"
asks=[("Dokima ships one defaults file that every repo's settings fall back to.",I,"793.1"),
("A repo's settings file changes only the settings it names; every other keeps its default.",I,"793.2"),
("The defaults file holds every setting of the owner's 41-row list, each with the default the list names.",C,"793.3"),
("A settings group in a repo's file merges with the defaults key by key, the repo winning.",I,"793.4"),
("A list in a repo's file replaces the default list whole.",I,"793.5"),
("Gates in a repo's file merge with the default gates by name.",I,"793.6"),
("Prompt additions in a repo's file merge with the default ones by name.",I,"793.7"),
("An unknown setting shows a warning that suggests the closest known name.",I,"793.8"),
("An unknown setting is ignored and the run goes on.",I,"793.9"),
("Setting any of the five locked settings in a repo's file fails the run, naming it.",I,"793.10")]
T="tests/test_settings_merge.py::"
tests=[
("test_a_repo_with_no_settings_file_runs_on_the_shipped_defaults_file","Swaps the shipped defaults file and checks the reader prints exactly it."),
("test_an_empty_settings_file_falls_back_to_the_shipped_defaults","Empty repo file still gives exactly the swapped defaults."),
("test_a_repo_file_changes_only_the_setting_it_names","One named setting changes; every other group and key is compared."),
("test_the_shipped_defaults_hold_the_owners_list","Checks each listed default by name; the list's reach is the owner's question."),
("test_a_group_in_the_repo_file_merges_key_by_key","One key set; the rest of the group must equal the defaults."),
("test_a_group_two_levels_down_merges_key_by_key","Nested caps merge key by key at both levels."),
("test_a_list_in_the_repo_file_replaces_the_default_list","Merged list must be exactly the repo's list."),
("test_an_empty_list_in_the_repo_file_empties_the
```

> Exit code 1
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
sed -i 's/Three questions wait for the owner: installing the YAML reader, the full list, the turn limit./Three questions wait for the owner: the YAML reader, the full list, the turn limit./' /tmp/gen.py; python3 /tmp/gen.py; cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 793 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#793](https://github.com/dokima-dev/dokima/issues/793) (settings read from shipped defaults, merged and checked). It still stops for you, because the planner asked you three questions.

- **Every ask is covered.** All ten asks from the parent plan of [#779](https://github.com/dokima-dev/dokima/issues/779) (settings file over shipped defaults) match one criterion each. Each criterion is a single behavior.
- **The tests fail for the right reason.** I ran all 17 new tests and each one fails today. The cause is that the settings reader doesn't exist yet, not a crash or a missing tool.
- **The tests test the right thing.** Each one runs the reader from outside in a temporary repo and names its criterion when it fails. The "rejects" checks have a "passes" case next to them, for example the locked-settings test also checks that an unlocked setting still goes through.

I couldn't answer the three questions with your own words, so they wait for you:
1. **Installing the YAML reader:** the plan changes four test workflow files so the test machines install it. This repo's rules forbid workflow changes unless the issue asks, so it needs your yes.
2. **Your 41-row list:** the planner didn't have it. The defaults test checks only 32 settings rebuilt from earlier quotes, so criterion 3 is only partly proven until you say whether that is enough.
3. **Turn limit:** your list says 60 turns, but a later merged change ([#792](https://github.com/dokima-dev/dokima/issues/792), which raised it to 100) set 100. The plan uses 100.

The review is in `/tmp/dokima-out/review.json` and passes both hand-back checks.

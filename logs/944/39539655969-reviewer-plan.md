# reviewer (plan) for #944

Run: https://github.com/dokima-dev/dokima/actions/runs/39539655969

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #944: The board works only with organization projects, so repos on personal accounts get no board
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The board works with a personal account's project, not only an organization's.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/944#issuecomment-6307380443) with `/plan`, or say `/review`
> 
> https://github.com/dokima-dev/dokima/pull/945 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/945/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/942
> - https://github.com/dokima-dev/dokima/issues/946
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> 
> **Scope:**
> 
> <!-- dokima-folded -->
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> `dokima/board.py` reads the board only as `organiza

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('in/03-planner.json'));print(json.dumps(d,indent=1)[:6000])"; cd /home/runner/work/dokima/dokima; git log --oneline -3; git status; ls tests/test_user_board.py; git diff main --stat
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39539304474",
>  "commit_before": "0e29c966e7f13733bd15d7478bf200c96c3fda7a",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 161173,
>   "turns": 21,
>   "cost_usd": 1.0207495999999998,
>   "tokens_in": 1145760,
>   "tokens_out": 14920
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/944/39539304474-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39539304474",
>  "handback": {
>   "kind": "feature",
>   "title": "The board works on personal accounts too",
>   "summary": "The board works with a personal account's project, not only an organization's.",
>   "links": {
>    "blocked_by": [],
>    "blocks": [],
>    "relates_to": [
>     942,
>     946
>    ]
>   },
>   "raises": [
>    {
>     "kind": "question",
>     "to": "owner",
>     "label": "Doubt: app access",
>     "text": "GitHub may refuse the app access to a personal account's board. Build it as asked anyway? The plan assumes yes.",
>     "evidence": "`.github/workflows/board.yml` uses the app token; `dokima/manifest.py` grants only `organization_projects`.",
>     "raised_by": "planner",
>     "id": "P1"
>    }
>   ],
>   "answers": [],
>   "feature": "Personal account boards work like organization boards: the board code reads them, then the install guide says so.",
>   "stories": [
>    {
>     "title": "Board code reads a personal account's project",
>     "user_story": "Owners on a personal account get card moves and a passing board a

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_user_board.py; grep -n '"test"\|\[.test.\]\|"tests"' dokima/agent*.py dokima/plan*.py 2>/dev/null | head -30
```

> """#944: DOKIMA_BOARD names an organization's project (`org/number`) or a user's project (`user:login/number`), and
> every board read asks GitHub for it under that owner."""
> import os
> import re
> import sys
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> import pytest  # noqa: E402
> 
> from dokima import audit, board  # noqa: E402
> 
> FIELDS = [{"id": "S", "name": "Status", "options": [{"id": "s-work", "name": "Work", "color": "BLUE", "description": ""}]},
>           {"id": "A", "name": "Action", "options": [{"id": "a-you", "name": "Needs you", "color": "RED", "description": ""}]},
>           {"id": "P", "name": "Priority", "options": [{"id": "p-b", "name": "Blocker", "color": "RED", "description": ""}]}]
> ITEM = {"fieldValueByName": {"name": "Needs you"}, "status": {"name": "Work"},
>         "content": {"__typename": "Issue", "number": 5, "state": "OPEN", "labels": {"nodes": []}}}
> 
> 
> class FakeGitHub:
>     """Answers board reads only under the owner type and login that own the board."""
> 
>     def __init__(self, kind, login):
>         self.kind, self.login, self.roots, self.rest_calls = kind, login, [], []
> 
>     def __call__(self, query, **v):
>         root = re.search(r"\{(\w+)\(login:\$o\)", query).group(1)
>         self.roots.append(root)
>         if root != self.kind or v["o"] != self.login or v["n"] != 3:
>             return {root: None}
>         return {root: {"projectV2": {"id": "PROJ", "fields": {"nodes": FIELDS},
>                                      "items": {"pageInfo":

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 290,320p dokima/planner.py; sed -n 360,400p dokima/planner.py
```

> for i in range(len(stories)):
>         if i not in state:
>             visit(i, [i])
> 
> 
> def check_edge_cases(where, c, filed):
>     """Garbled unless C lists edge cases, each with a FILED test, or why none."""
>     cases, why = c.get("edge_cases"), c.get("no_edge_cases")
>     if cases is None or cases == []:
>         if not isinstance(why, str) or not why.strip():
>             raise Garbled(f"{where} needs its edge_cases, each with the test covering it, or no_edge_cases saying "
>                           f"why it has none")
>         return
>     if not isinstance(cases, list):
>         raise Garbled(f"{where} needs edge_cases as a list of cases, each with the test covering it")
>     for e in cases:
>         if not isinstance(e, dict) or not isinstance(e.get("case"), str) or not e["case"].strip():
>             raise Garbled(f"{where} has an edge case with no case saying what it is")
>         if not isinstance(e.get("test"), str) or not e["test"].strip():
>             raise Garbled(f"{where}: its edge case {e['case'].strip()!r} names no test covering it")
>         if e["test"].strip() not in filed:
>             raise Garbled(f"{where}: its edge case {e['case'].strip()!r} names {e['test'].strip()}, which the plan "
>                           f"does not file under this criterion in tests")
> 
> 
> def from_kind(p, issue=None, said=None):
>     """Read a plan.json written in the agreed shape (user_story or feature) into what the rest of the code uses.
> 
>     A story becomes a plan: its acceptance criteria come

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git grep -n "organization(\|orgs/\|DOKIMA_BOARD\|board.Board\|projectV2" main -- dokima/ | grep -v "^main:dokima/roles" | head -40; git diff main -- dokima/scan.py docs/wiki/Installing.md
```

> main:dokima/agent_roles.py:469:        spec = os.environ.get("DOKIMA_BOARD", "").strip()
> main:dokima/agent_roles.py:472:            b = board.Board(spec, repo, board.gql)
> main:dokima/agent_roles.py:657:        spec, repo = os.environ.get("DOKIMA_BOARD", "").strip(), os.environ.get("GITHUB_REPOSITORY", "")
> main:dokima/agent_roles.py:671:                    board.Board(spec, repo), repo, plan.repo_approvers(repo.split("/")[0]), int(argv[2])))
> main:dokima/agent_roles.py:683:            retry.once_more("the board step", lambda: board.stopped(board.Board(spec, repo), repo, argv[2], column),
> main:dokima/audit.py:3:    python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number", optional) and .github/CODEOWNERS where it runs
> main:dokima/audit.py:378:BOARD_QUERY = 'query($o:String!,$n:Int!){organization(login:$o){projectV2(number:$n){id fields(first:50){nodes{... on ProjectV2SingleSelectField{id name options{id name color description}}}} views(first:50){nodes{id name layout filter}}}}}'
> main:dokima/audit.py:392:            p = board.gql(BOARD_QUERY, o=self.owner, n=self.number)["organization"]["projectV2"]
> main:dokima/audit.py:476:        b = board.Board(self.spec, repo)
> main:dokima/audit.py:484:    spec = os.environ.get("DOKIMA_BOARD", "").strip()
> main:dokima/board.py:6:    python3 -m dokima.board         # reads GITHUB_EVENT_NAME, GITHUB_EVENT_PATH and DOKIMA_BOARD ("org/number"), if set
> main:dokima/board.py:44:        p = q('query($o:String!,$n:Int!){organization(login

**Agent:** I'm checking the plan for #944 against the owner's asks. Next I'll check the README and the tests on main.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; git show main:README.md | grep -n -i "personal\|organi\|board" | head; git show main:docs/wiki/Installing.md | grep -n -i "personal\|org/number"; git grep -n -i "personal" main -- docs/ | head; mkdir -p /tmp/t && git show main:dokima/board.py >/dev/null; git stash list | head -1; git worktree add -q /tmp/mainwt main 2>&1|tail -1; cp tests/test_user_board.py /tmp/mainwt/tests/; cd /tmp/mainwt && python3 -m pytest -q tests/test_user_board.py 2>&1 | tail -8
```

> 36:- **GitHub-native.** Nothing to host, no new dashboard. Issues, pull requests and Actions are the whole interface.
> 50:Every issue carries a live card drawn by code from GitHub's own check results, and an optional project board follows along.
> 54:> One-link onboarding is in progress ([#272](https://github.com/dokima-dev/dokima/issues/272)). The steps below are the setup by hand.
> 61:4. Set the repo variable `DOKIMA_APP_ID`. Optionally set `DOKIMA_BOARD` to a project board.
> 9:- A GitHub repo, ideally in an **organization** (the project board and merge queue need one; on personal repos those extras are skipped).
> 33:| `DOKIMA_BOARD` | variable, optional | Project board as `org/number` |
> main:docs/wiki/Installing.md:9:- A GitHub repo, ideally in an **organization** (the project board and merge queue need one; on personal repos those extras are skipped).
> E           AttributeError: module 'dokima.board' has no attribute 'parse'
> 
> tests/test_user_board.py:65: AttributeError
> =========================== short test summary info ============================
> FAILED tests/test_user_board.py::test_every_board_read_asks_for_the_project_under_its_owner[user:ann/3-user-ann] - TypeError: 'NoneType' object is not subscriptable
> FAILED tests/test_user_board.py::test_the_audit_checks_the_board_fields_the_same_way_on_both[user:ann/3-user-ann] - TypeError: 'NoneType' object is not subscriptable
> FAILED tests/test_user_board.py::test_a_board_spec_with_an_unknown_owner_type_is_refused - AttributeError:

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git worktree remove --force /tmp/mainwt; mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner re-planned after the pull request clashed with main.", "It split the work into two stories: board code, then the install guide."],
  "decided": ["A personal account's board is named as user, login and number."],
  "open": ["The owner is asked whether the app can reach a personal account's board."]},
 "verdict": "approve",
 "summary": "The plan carries every ask; only the owner's question on app access stays open.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "`DOKIMA_BOARD` names either an organization's project or a user's project (for example `user:<login>/<number>`, or found by owner type), and every board query reads it either way.", "source": "https://github.com/dokima-dev/dokima/issues/944", "criterion": "1.1"},
  {"ask": "The board fields (Status, Action, Priority) are checked the same way on both.", "source": "https://github.com/dokima-dev/dokima/issues/944", "criterion": "1.3"},
  {"ask": "The install docs stop saying personal repos skip the board.", "source": "https://github.com/dokima-dev/dokima/issues/944", "criterion": "2.1"},
  {"ask": "Tests for an org board and a user board.", "source": "https://github.com/dokima-dev/dokima/issues/944", "criterion": "1.1"}
 ],
 "behaviors": [
  {"criterion": "1.1", "one_behavior": true, "why": "One setting form, one result: board reads find the personal project."},
  {"criterion": "1.2", "one_behavior": true, "why": "One case, a missing view, created under the right owner."},
  {"criterion": "1.3", "one_behavior": true, "why": "One check, the audit's field check, alike on both board kinds."},
  {"criterion": "2.1", "one_behavior": true, "why": "One sentence removed from the install guide."}
 ],
 "edge_cases": [
  {"criterion": "1.1", "cut": [], "missing": []},
  {"criterion": "1.2", "cut": [], "missing": []},
  {"criterion":
```

> Exit code 1
> the edges box has no line for criterion S1.1: say covered or missing: the case
> the edges box has no line for criterion S1.2: say covered or missing: the case
> the edges box has no line for criterion S1.3: say covered or missing: the case
> the edges box has no line for criterion S2.1: say covered or missing: the case
> the ask "`DOKIMA_BOARD` names either an organization's project or a user's project (for example `user:<login>/<number>`, or found by owner type), and every board query reads it either way." is matched to 1.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1)
> the ask "The board fields (Status, Action, Priority) are checked the same way on both." is matched to 1.3, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1)
> the ask "The install docs stop saying personal repos skip the board." is matched to 2.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1)
> the ask "Tests for an org board and a user board." is matched to 1.1, which is not a criterion of the plan (S1.1, S1.2, S1.3, S2.1)
> behaviors has no judgment of criterion S1.1: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.2: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S1.3: say one_behavior true or false, and why in one line
> behaviors has no judgment of criterion S2.1: say one_behavior true or false, and why in one line
> edge_cases has no judgment of criterion S1.1: list the exotic

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i -E 's/"(criterion|serves)": "([12]\.[0-9])"/"\1": "S\2"/g; s/"([12]\.[0-9])": "covered"/"S\1": "covered"/g' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 944 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#944](https://github.com/dokima-dev/dokima/issues/944) (board on personal accounts), and the hand-back passes both checks. It's in `/tmp/dokima-out/review.json`.

- **Every ask is covered.** Each of the owner's four asks matches a criterion:
  - reading a personal account's board → S1.1
  - checking the board fields the same way on both kinds of board → S1.3
  - the install guide no longer saying personal repos skip the board → S2.1
  - tests for both kinds of board → S1.1
- **One extra criterion, and it's needed.** S1.2 creates a missing board view under the right owner, which is part of the board reads working.
- **Each criterion is one behavior.** Size is ok, and I raised no blockers.
- **One question still waits for the owner.** The planner asked whether GitHub will let the app reach a personal account's board at all. I didn't answer it for them: the owner's words don't settle it, and the answer changes how the system works. It's a real doubt, since the app is only granted organization project access today.
- **The existing tests don't prove anything yet.** The plan is split into stories, so it lists no tests of its own yet; each story's planner writes them. I ran the earlier build's test file, `tests/test_user_board.py`, against main. The three personal-account tests fail because the feature is missing, and the two organization tests pass.
- **One test name is off.** S1.1's edge case names `test_a_board_setting_with_an_unknown_owner_type_is_refused`, but the file has `test_a_board_spec_with_an_unknown_owner_type_is_refused`. The story planner should fix that when it writes the story's tests.

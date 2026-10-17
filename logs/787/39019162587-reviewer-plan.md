# reviewer (plan) for #787

Run: https://github.com/dokima-dev/dokima/actions/runs/39019162587

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #787: Autopilot merges by the repo's branch, method and labels
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> Autopilot merges into the repo's own branch, its own way, and reads its own labels, all from settings.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/787#issuecomment-6231944826) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/791
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://githu

`2. Bash`
```
cd /tmp/pack; cat owner_words.json | head -c 6000; echo; cat parent.json | head -c 3000; echo; cat open_issues.json | head -c 1500; echo; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='plan'},indent=1)[:3000])"
```

> {
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n- Every opinion specific to Dokima's own repo becomes a setting with a default: default branch, records branch, rules file name, bot identity, co-author trailer (#110), test install/run_all/run_one commands and test folder (#384), merge gate exclude list, merge queue (#375), labels, check names, turn limits and word caps, card icon source. Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.\n- Locked keys (integrity): app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. A repo cannot override them; trying fails the run.\n- Merge rules: maps merge key by key, repo wins; lists replace; `gates` and `prompts.append` merge by entry name. Unknown key warns with a suggestion and is ignored; never stops a run.\n- Exposure rule: expose repo facts, ta

**Agent:** Let me see the relevant inventory rows B3, B6, B8, D1.

`3. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('owner_words.json'))
t=d['https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729']
for l in t.splitlines():
  if l.startswith(('| B','| D')) or 'default_branch' in l or 'label' in l.lower(): print(l)
"; python3 -c "
import json;d=json.load(open('owner_words.json'));print(list(d.keys()))"
```

> | B1 | Required checks "all tests", "Acceptance criteria" on `main` | `gates.required: ["all tests", "Acceptance criteria"]` (+ any repo checks, see G) | manifest.py:47 `CHECKS`, :49 `BRANCH_RULES` |
> | B2 | Same check names as literals | read from `gates.required` / check names | card.py:24-25, uptodate.py:20 |
> | B3 | Default branch is `main` everywhere | `branch.default: main` (better: read repo default_branch; workflow `branches:` filters stay YAML) | agent_autopilot.py:608,619,628 `branch="main"`, :701 `compare/main...`; agent.yml origin/main (165,192,195,213,230,237,257,423 `--base main`); fix.yml:35-37; agent_records.py:735,927 `blob/main`; card.py:55 `/main/`; full-suite.yml:10, testmon.yml:8, uptodate.yml:7, wiki.yml:4 |
> | B5 | Records saved on branch `logs` | `records.branch: logs` (adopters may already own a `logs` branch; suggest `dokima-logs`) | agent_records.py:55 `LOGS_BRANCH = "logs"`; agent.yml:242-244,479-487 |
> | B6 | Autopilot merge method | `merge.method: squash` | agent_autopilot.py:730 `--squash` |
> | B8 | How long the merge gate waits for checks | `gate.checks_wait_min: 45` (slow suites elsewhere) | agent_autopilot.py:595 `CHECKS_WAIT 45 min`, :665 `UPDATE_WAIT 5 min` |
> | B9 | Three blocks in a row stops for the owner | `river.max_blocks: 3` | agent_next.py:100 `rounds=3`, agent_roles.py:448 |
> | B10 | More questions than this = plan not ready | `planner.max_questions: 3` | agent_next.py:97 `MAX_QUESTIONS = 3` |
> | B11 | Claude turn budget | `roles.<role>.ma

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('owner_words.json'))
for k in list(d)[3:]: print(k, '\n', d[k][:2500], '\n---')
"
```

> https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219931236 
>  /plan 
> ---
> https://github.com/dokima-dev/dokima/issues/740#issuecomment-6220234858 
>  /plan 
> ---
> https://github.com/dokima-dev/dokima/issues/740#issuecomment-6220864176 
>  /work yaml 
> ---
> Shell cwd was reset to /home/runner/work/dokima/dokima

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head -20; cat tests/test_settings_autopilot.py
```

> commit d00951690f119cf8e55e5256753fd0a2a2a354f2
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 08:54:51 2026 +0000
> 
>     planner for #787 (run 39018824171)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_settings_autopilot.py | 387 +++++++++++++++++++++++++++++++++++++++
>  1 file changed, 387 insertions(+)
> """Tests for #787: autopilot merges by the repo's branch, method, checks wait and labels.
> 
> The settings live in `.dokima/settings.yaml` in the repo the run works in, over Dokima's shipped defaults in
> `dokima/defaults.yaml`. This story reads these of them:
> 
>     branch: {default: main}          # the branch autopilot merges into; empty or unset asks GitHub for the repo's own
>     merge: {method: squash}          # how autopilot merges: squash, merge or rebase
>     gate: {checks_wait_min: 45}      # how many minutes the merge gate waits for checks still running
>     labels: {autopilot: autopilot, filed: filed-by-dokima}   # the autopilot label and the label on issues Dokima files
> 
> Each test writes a settings file into a temp folder, runs there, and calls autopilot's or the board's own code
> against a fake GitHub in memory standing in for `gh`. Time is faked, so a 45-minute wait costs nothing. Nothing
> leaves the machine.
> """
> import json
> import os
> import subprocess
> import sys
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q -p no:cacheprovider tests/test_settings_autopilot.py 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed|Error" | head -40
```

> E       AssertionError: 787.1: autopilot did not merge into trunk, the settings' default branch: HTTP 404: Not Found
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:181: AssertionError
> E       AssertionError: 787.1: autopilot merged although GitHub has no trunk branch
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:196: AssertionError
> E       AssertionError: 787.2: autopilot did not merge into develop, GitHub's default branch: HTTP 404: Not Found
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:212: AssertionError
> E       AssertionError: 787.2: an empty default branch setting did not fall back to GitHub's develop: HTTP 404: Not Found
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:225: AssertionError
> E       AssertionError: 787.3: autopilot merged with ['--squash'], not --rebase as the settings say
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:242: AssertionError
> E       AssertionError: 787.3: merges used [('pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1'), ('pr', 'merge', '60', '-R', 'o/r', '--squash', '--match-head-commit', 'a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1', '--admin')]
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:266: AssertionError
> E       AssertionError: 787.4: the gate waited 2700 s, not the 2 minutes the settings say
> /home/runner/work/dokima/dokima/tests/test_settings_autopilot.py:283: Assertio

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -nE "^(branch|merge|gate|labels)|^  (default|method|checks_wait_min|autopilot|filed|plan|work):" dokima/defaults.yaml; ls dokima | head -80; grep -n "def \|^[A-Z_]* =" dokima/settings.py 2>/dev/null | head -30
```

> 22:branch:
> 23:  default: main
> 54:gates:
> 56:gate:
> 57:  checks_wait_min: 45
> 59:merge:
> 60:  method: squash
> 61:labels:
> 62:  plan: plan
> 63:  work: work
> 64:  autopilot: autopilot
> 65:  filed: filed-by-dokima
> __pycache__
> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_claude.py
> agent_codex.py
> agent_github.py
> agent_kimi.py
> agent_next.py
> agent_records.py
> agent_roles.py
> agents.py
> app.json
> audit.py
> board.py
> body.py
> card.py
> checks.py
> defaults.yaml
> fence.py
> icons
> manifest.py
> plan.py
> planner.py
> playthrough.py
> prompt.py
> raises.py
> retry.py
> roles
> scan.py
> settings.py
> setup.py
> turns.py
> uptodate.py
> words.py
> 21:DEFAULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.yaml")
> 22:REPO_FILE = os.path.join(".dokima", "settings.yaml")
> 23:LOCKED = "integrity"  # the group a repo may never set
> 24:BY_NAME = {"gates.required", "prompts.append"}  # lists that merge with the default ones by name
> 31:def load(path):
> 44:def entry_name(entry):
> 49:def by_name(base, mine):
> 61:def merge(base, mine, warn, path=""):
> 79:def read(repo=".", warn=None):
> 90:def setup_lines(got):
> 101:def env_lines(got):
> 122:def main(argv=()):

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "main\|squash\|AUTOPILOT\|FILED_LABEL\|CHECKS_WAIT\|def \|settings" dokima/agent_autopilot.py | head -120; grep -n "AUTOPILOT\|def autopilot\|def label\|settings" dokima/board.py
```

> 16:def story_body(parent, i, story, parent_title):
> 31:def file_split(repo, parent, recs, labels=()):
> 71:AUTOPILOT = "autopilot"
> 74:def issue_tree(repo, number):
> 87:def switch_autopilot(repo, number, switch):
> 93:        if switch == "start" and AUTOPILOT not in labels:
> 95:            agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{n}/labels", "-f", f"labels[]={AUTOPILOT}")
> 97:        elif switch == "stop" and AUTOPILOT in labels:
> 98:            agent_github.gh("api", "-X", "DELETE", f"repos/{repo}/issues/{n}/labels/{AUTOPILOT}")
> 103:def autopilot_comment(number, switch, switched, started=(), picked=""):
> 118:AUTOPILOT_LINE = "Autopilot: blockers merged, starting plan"
> 119:AUTOPILOT_START_LINE = "Autopilot: switched on, starting plan"
> 122:def link_edges(number, links):
> 128:def loop_through(add, drop, has):
> 134:    def blockers(i):
> 149:def named(numbers):
> 155:FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> 158:def file_issues(repo, number, rec, recs):
> 202:                     "--label", FILED_LABEL).strip()
> 212:def record_links(repo, number, items):
> 228:    def has(i):
> 263:def set_title(repo, number, items):
> 289:def installations_link(repo):
> 294:        return f"https://github.com/organizations/{owner}/settings/installations"
> 295:    return "https://github.com/settings/installations"
> 298:def stop_run(repo, rid, polls=60, pause=5):
> 310:def rerun_checks(repo, number):
> 374:def started_before(repo, number):
> 381:                MARK in 

**Agent:** Tests all fail today for the right reasons; now checking how the settings reader handles an empty branch value.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 25,100p dokima/settings.py; cd /tmp && mkdir -p t787/.dokima && cd t787 && printf 'branch:\n  default:\n' > .dokima/settings.yaml && python3 -c "
import sys;sys.path.insert(0,'/home/runner/work/dokima/dokima')
from dokima import settings;g=settings.read();print(repr(g['branch']),g['labels'])"
```

> class Locked(Exception):
>     """A repo's settings file sets a locked setting."""
> 
> 
> def load(path):
>     """The settings map in the YAML file at PATH; empty when missing or empty."""
>     if not os.path.isfile(path):
>         return {}
>     with open(path) as f:
>         got = yaml.safe_load(f)
>     if got is None:
>         return {}
>     if not isinstance(got, dict):
>         raise ValueError(f"{path} must hold a map of settings, not {type(got).__name__}")
>     return got
> 
> 
> def entry_name(entry):
>     """An entry's name: the text itself, or a map's name field."""
>     return entry.get("name") if isinstance(entry, dict) else entry
> 
> 
> def by_name(base, mine):
>     """BASE's entries with MINE's merged in by name, a same-named one taking its place."""
>     out = list(base)
>     for entry in mine:
>         at = next((i for i, e in enumerate(out) if entry_name(e) == entry_name(entry)), None)
>         if at is None:
>             out.append(entry)
>         else:
>             out[at] = entry
>     return out
> 
> 
> def merge(base, mine, warn, path=""):
>     """BASE with MINE merged over it key by key; unknown keys warned of, dropped."""
>     out = dict(base)
>     for key, value in mine.items():
>         name = f"{path}{key}"
>         if key not in base:
>             near = difflib.get_close_matches(str(key), [str(k) for k in base], n=1)
>             hint = f"; did you mean {path}{near[0]}?" if near else "."
>             warn(f"Dokima does not know the setting {name}{hint} It is ignored.")
>         elif isinstance(base[ke

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 60,82p dokima/board.py; sed -n 115,150p dokima/board.py; sed -n 195,206p dokima/board.py; sed -n 312,322p dokima/board.py; sed -n 400,415p dokima/board.py
```

> return
>         fid, options = self.fields[field]
>         if option is None:
>             self.q('mutation($p:ID!,$i:ID!,$f:ID!){clearProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f}){projectV2Item{id}}}', p=self.id, i=iid, f=fid)
>         elif option in options:
>             self.q('mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}}}', p=self.id, i=iid, f=fid, o=options[option])
> 
>     def value(self, iid, field):
>         """The card's current option of that field, or None."""
>         node = self.q('query($i:ID!,$f:String!){node(id:$i){... on ProjectV2Item{fieldValueByName(name:$f){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}', i=iid, f=field)["node"]
>         return ((node or {}).get("fieldValueByName") or {}).get("name")
> 
>     def labels(self, kind, number):
>         """The names of the labels the issue or PR carries."""
>         field = "issue" if kind == "issue" else "pullRequest"
>         node = self.q(f'query($o:String!,$r:String!,$n:Int!){{repository(owner:$o,name:$r){{{field}(number:$n){{labels(first:100){{nodes{{name}}}}}}}}}}', o=self.repo_owner, r=self.repo_name, n=int(number))["repository"][field]
>         return {label["name"] for label in node["labels"]["nodes"]}
> 
>     def autopilot(self, kind, number):
>         """Whether the issue or PR carries the autopilot label."""
>         return AUTOPILOT in self.labels(kind, number)
> 
>     def depen

`11. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 628,676p dokima/agent_autopilot.py; sed -n 85,100p dokima/agent_autopilot.py
```

> def unproven(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
>     """Why the commit is not proven by the checks the branch's rule requires, or None.
> 
>     Check runs and commit statuses count alike; a check the rule does not require judges nothing (#561). A
>     required check still running or not yet on the commit is waited for, up to `wait` seconds, looking every `pause`
>     seconds; a card run cancelled by a newer redraw, or a board wait cancelled by a newer event, is left out."""
>     return proof(repo, sha, wait, pause, branch)[1]
> 
> 
> def proof(repo, sha, wait=CHECKS_WAIT, pause=CHECKS_PAUSE, branch="main"):
>     """What the checks the branch's rule requires say of the commit, as `unproven` reads them.
> 
>     ("passed", None), ("failed", why) when one of them failed, or ("stopped", why) when they never finished or GitHub
>     could not say."""
>     try:
>         required = required_checks(repo, branch)
>     except subprocess.CalledProcessError as e:
>         return "stopped", f"GitHub did not give which checks {branch} requires: {gh_reason(e)}"
>     if not required:
>         return "stopped", f"{branch}'s branch rule requires no checks, so no check proves its head commit {sha[:7]}"
>     deadline = time.monotonic() + wait
>     while True:
>         runs = [r for p in pages(agent_github.gh("api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100", "--paginate"))
>                 for r in p.get("check_runs", []) if not superseded(r) and r.get("name") in required]
>         sta

**Agent:** Plan reads clean except two label paths with no test. Writing the hand-back.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote seven criteria and thirteen tests for the branch, merge method, checks wait and two labels.",
          "Every new test fails today because autopilot still uses its fixed values."],
  "decided": ["Only an empty branch setting asks GitHub for the repo's own default branch."],
  "open": ["The owner decides whether a repo setting nothing should get main or ask GitHub."]},
 "verdict": "block",
 "summary": "Sound plan, but turning autopilot off and the board's label events have no test.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "787.5: board event untested",
   "text": "The board still reacts only to a label named autopilot when one is added or removed, and no test sees it. Smallest fix: a test where adding the settings' label moves the card.",
   "evidence": "`dokima/board.py:407` and `:203` compare to `AUTOPILOT`; only `Board.autopilot` is tested."},
  {"kind": "blocker", "to": "planner", "label": "787.6: off switch untested",
   "text": "Turning autopilot off must remove the settings' label, or the issue stays on autopilot. Smallest fix: one test that switches off and checks the named label is gone.",
   "evidence": "`dokima/agent_autopilot.py:97-98` and `dokima/board.py:125` remove `AUTOPILOT`; no test runs stop."}
 ],
 "answers": [],
 "asks": [
  {"ask": "`branch.default: main`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.1"},
  {"ask": "better: read repo default_branch", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.2"},
  {"ask": "`merge.method: squash`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.3"},
  {"ask": "`gate.checks_wait_min: 45`", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "787.4"},
  {"ask
```

> Exit code 1
> raise 1's text holds 33 words, over its cap of 30: cut 3, keep the facts
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`13. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json;d=json.load(open('review.json'))
d['previous_step']['did'][0]="The planner wrote seven criteria and thirteen tests for branch, method, wait and labels."
d['raises'][0]['text']="The board still reacts only to a label named autopilot being added or removed, untested. Smallest fix: a test where adding the settings' label moves the card."
json.dump(d,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 787 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I've blocked the plan for [#787](https://github.com/dokima-dev/dokima/issues/787) (autopilot merges by the repo's branch, method and labels). It goes back to the planner over two missing tests. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

**What holds up:**
- I ran all 13 new tests and every one fails today for the right reason: autopilot still uses its fixed branch, merge method, wait time and labels.
- Each criterion carries one of the owner's asks from the #740 settings list, and each covers one behavior.
- On the default branch, each test pairs a case that should merge with one that should not, so code that ignores the setting would still fail.

**The two blockers:**
- **Criterion 787.5:** the board only notices the old fixed name when someone adds or removes the autopilot label on GitHub (`dokima/board.py:407` and `:203`). No test covers this, so a build could rename the label and the board would stop reacting. The fix is one test where adding the settings' label moves the card.
- **Criterion 787.6:** turning autopilot off still removes the old fixed name (`dokima/agent_autopilot.py:97-98` and `dokima/board.py:125`), and no test turns it off. The fix is one test that switches autopilot off and checks the settings' label is gone.

**Still waiting for you:** the planner's question P1. The shipped settings name `main`, so a repo that sets nothing gets `main`, and only an empty setting asks GitHub for the repo's own default branch. I didn't answer it for you: your words "better: read repo default_branch" could mean always asking GitHub, and that changes how Dokima works.

# reviewer (plan) for #784

Run: https://github.com/dokima-dev/dokima/actions/runs/39019710086

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #784: Required checks, labels and the audit follow settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 779 -->
> <!-- dokima-blocking: {"blocked_by": [779], "blocks": [741, 742, 744, 791], "loop": []} -->
> The daily audit and its guard judge a repo by its own settings, not by Dokima's own values.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/784#issuecomment-6231944437) with `/plan`, or say `/review`
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
> - https://github.com/dokima-dev/dokima/issues/326
> - https://github.com/dokima-dev/dokima/issues/424
> - https://github.com/dokima-dev/dokima/is

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; cat tests/test_settings_audit.py; git show HEAD -- tests/test_settings_merge.py
```

> commit 960a2dadb5e8b3bbb930998bf3397190932dfd96
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sat Oct 17 09:03:42 2026 +0000
> 
>     planner for #784 (run 39018821717)
> 
>  tests/test_settings_audit.py | 263 +++++++++++++++++++++++++++++++++++++++++++
>  tests/test_settings_merge.py |   2 +-
>  2 files changed, 264 insertions(+), 1 deletion(-)
> """Tests for #784: the audit judges required checks, labels and colors by the settings.
> 
> The daily audit (`python3 -m dokima.audit OWNER/REPO`) compares the repo's live labels, board pills, branch rule and
> auto-merge lists with what Dokima needs. Here what Dokima needs comes from the merged settings: the shipped defaults
> (`dokima/defaults.yaml`) with the repo's own `.dokima/settings.yaml` over them, read where the audit runs. Each audit
> test runs the real command from outside against the fake `gh` of tests/fake_gh.py, through tests/test_audit_cli.py's
> Audit helper, with a settings file written in the repo folder it runs in.
> 
> The settings these tests write, beside the ones the shipped defaults already hold:
>     gates.required            check names; a repo's list merges with the default one by name
>     merge.queue               false: the repo uses no merge queue (the default, true, keeps today's audit)
>     labels.<key>              the name of each of Dokima's labels (autopilot, filed)
>     colors.labels.<key>       each label's color, by the same key, as GitHub writes it (rrggbb)
>     colors.pills.<fi

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_settings_audit.py tests/test_settings_merge.py 2>&1 | grep -E "^E  .*78[0-9]\.|passed|failed|Error" | head -40
```

> E       AssertionError: 784.1: main requires Lint, which the required checks setting names, yet the audit flagged it: ['Branch rule of `main` requires `Lint`, a check Dokima does not declare.']
> tests/test_settings_audit.py:76: AssertionError
> E       AssertionError: 784.2: with the merge queue off in settings, the audit still asks about one: ["Auto-merge is half set up: Dokima's app is missing from the merge queue ruleset's bypass list for pull requests. Add it there for auto-merge, or take it off the other list to keep your approval."]
> tests/test_settings_audit.py:118: AssertionError
> E       AssertionError: 784.3: the repo holds dokima-autopilot, the name its settings give the autopilot label, yet the audit flagged labels: ['Label `autopilot` is missing; Dokima needs it with color `8250df` and description `Running on its own`.']
> tests/test_settings_audit.py:145: AssertionError
> E       AssertionError: 784.4: the autopilot label's color matches the settings, yet the audit flagged it: ['Label `autopilot` has color `0e8a16`; Dokima needs `8250df`.']
> tests/test_settings_audit.py:171: AssertionError
> E       AssertionError: 784.5: the Needs you pill's color matches the settings, yet the audit flagged it: ['Option `Needs you` of the board field `Action` has color `BLUE`; Dokima needs `RED`.']
> tests/test_settings_audit.py:199: AssertionError
> E       AssertionError: 784.6: the guard flagged the board workflow's name as a missing check: ["dokima/look.py: check 'board' is not in the mani

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "label create\|/labels\"\|labels\", \"-f\|-X POST.*label\|def compare_labels\|def auto_merge\|LABELS\b" dokima | head -20; grep -n "queue\|required\|labels\|colors\|pills" dokima/defaults.yaml | head -30
```

> dokima/board.py:121:        path = f"repos/{self.repo_owner}/{self.repo_name}/issues/{number}/labels"
> dokima/audit.py:37:def compare_labels(live):
> dokima/audit.py:39:    for name, want in manifest.LABELS.items():
> dokima/audit.py:121:def auto_merge(github, repo, rule):
> dokima/prompt.py:21:LABELS = {"summary": "summary", "user_story": "user_story", "criterion": "criterion (acceptance or non-functional)",
> dokima/prompt.py:39:    for key, label in LABELS.items():
> dokima/agent_autopilot.py:95:            agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{n}/labels", "-f", f"labels[]={AUTOPILOT}")
> dokima/manifest.py:18:LABELS = {
> dokima/manifest.py:211:        if name not in LABELS:
> 30:  docstrings: required
> 55:  required: [all tests, Acceptance criteria]
> 61:labels:

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 80,100p dokima/agent_autopilot.py; grep -rn "AUTOPILOT\s*=\|filed-by-dokima\|FILED\s*=" dokima | head; sed -n 110,130p dokima/board.py
```

> continue
>         tree.append(n)
>         # GitHub allows at most 100 sub-issues per parent, so one page holds them all.
>         todo += [c["number"] for c in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}/sub_issues?per_page=100") or "[]")]
>     return tree
> 
> 
> def switch_autopilot(repo, number, switch):
>     """Put the issue's tree on autopilot ("start") or take it off ("stop"), touching no other label; returns the
>     issues switched: those whose `autopilot` label was added or removed."""
>     switched = []
>     for n in issue_tree(repo, number):
>         labels = {l["name"] for l in json.loads(agent_github.gh("api", f"repos/{repo}/issues/{n}")).get("labels", [])}
>         if switch == "start" and AUTOPILOT not in labels:
>             # Adding a label GitHub does not have yet creates it.
>             agent_github.gh("api", "-X", "POST", f"repos/{repo}/issues/{n}/labels", "-f", f"labels[]={AUTOPILOT}")
>             switched.append(n)
>         elif switch == "stop" and AUTOPILOT in labels:
>             agent_github.gh("api", "-X", "DELETE", f"repos/{repo}/issues/{n}/labels/{AUTOPILOT}")
>             switched.append(n)
>     return switched
> dokima/board.py:16:AUTOPILOT = "autopilot"
> dokima/manifest.py:20:    "filed-by-dokima": {"color": "bfd4f2", "description": "Created automatically, not by a person"},
> dokima/agent_autopilot.py:71:AUTOPILOT = "autopilot"
> dokima/agent_autopilot.py:155:FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> dokima/defau

**Agent:** Tests all fail today for the right reason. One problem found: the plan says no Dokima code creates labels, but `agent_autopilot.py` does. Writing the review now.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "FILED_LABEL" dokima | head -5; grep -rln "784\|labels setting" rules | head
```

> dokima/agent.py:49:    AUTOPILOT_START_LINE, link_edges, loop_through, named, FILED_LABEL, file_issues, record_links, set_title,
> dokima/agent_autopilot.py:155:FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> dokima/agent_autopilot.py:202:                     "--label", FILED_LABEL).strip()

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote seven criteria and seven tests, each failing today for the right reason.",
          "The planner dropped plan and work from the shipped defaults test."],
  "decided": ["The audit, not Dokima, asks for each label by its setting name."],
  "open": ["Three questions wait for the owner: merge queue, plan and work labels, label creation."]},
 "verdict": "block",
 "summary": "Dokima does create labels, so the plan's label criterion covers only the audit and drops the owner's ask.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "784.3: labels Dokima creates",
   "text": "The owner asked that Dokima create its labels under the setting names. Dokima does: it adds `autopilot` and `filed-by-dokima` by fixed names, and GitHub creates a missing label. With autopilot renamed, the audit wants the new name while Dokima still adds the old one. Smallest fix: add a criterion and test that switching autopilot on and filing an issue use the setting names, or show which open issue carries it, and correct question P3.",
   "evidence": "`dokima/agent_autopilot.py:94` says adding a missing label creates it; `:71` and `:155` hard-code the names; `dokima/board.py:16`."}
 ],
 "answers": [],
 "asks": [
  {"ask": "The checks required on the default branch come from the required checks setting.", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "784.1"},
  {"ask": "Turning the merge queue off in a repo's settings stops the audit asking for one.", "source": "https://github.com/dokima-dev/dokima/issues/740", "criterion": "784.2"},
  {"ask": "Dokima creates its labels under the names in the labels setting.", "source": "https://github.com/dokima-dev/dokima/issues/740#issuecomment-6219928729", "criterion": "784.3"},
  {"ask": "The daily audit no longer flags label and pill colors that match the repo's settings.", "source":
```

> Exit code 1
> raise 1's text holds 74 words, over its cap of 30: cut 44, keep the facts

`8. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; r=json.load(open(p))
r["raises"][0]["text"]="Dokima itself adds autopilot and filed labels by fixed names, creating them. Add a criterion and test that it uses the setting names, or name the issue carrying it."
json.dump(r,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 784 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've blocked the plan for [#784](https://github.com/dokima-dev/dokima/issues/784) (the audit follows a repo's settings) and sent it back to the planner. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**The blocker (criterion 784.3, label names):** the owner asked that "Dokima creates its labels under the names in the labels setting." The planner's question P3 says no Dokima code creates labels, so the plan only makes the audit look for labels under their setting names. That claim is wrong:
- `dokima/agent_autopilot.py:94` puts the `autopilot` label on issues by a fixed name, and its own comment says adding a label GitHub doesn't have yet creates it.
- `dokima/agent_autopilot.py:155` files issues with a fixed `filed-by-dokima` label.
- `dokima/board.py:16` also holds the `autopilot` name as a fixed value.

So if a repo renames its autopilot label, the audit would ask for the new name while Dokima keeps adding the old one. The fix I asked for: add a criterion and test that Dokima uses the setting names when it adds these labels, or name the open issue that already covers it, and correct P3.

**The rest of the plan:**
- I ran the seven new tests and the one changed older test: all eight fail today, each because the feature is missing.
- I matched each of the owner's six asks to a criterion. Each criterion is one behavior and each test checks only its own criterion, so size is ok.
- The changed older test drops the plan and work labels from the shipped defaults. That goes against the owner's settings list in [#740](https://github.com/dokima-dev/dokima/issues/740) (one settings file per repo), but follows their note in [#515](https://github.com/dokima-dev/dokima/issues/515). The planner raised this conflict as question P2, so I didn't block on it.

**The planner's three questions** (P1 merge queue, P2 plan and work labels, P3 label creation) stay with the owner. None of them could be settled with the owner's exact words without changing how the system works.

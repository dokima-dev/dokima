# reviewer (plan) for #858

Run: https://github.com/dokima-dev/dokima/actions/runs/39102923570

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #858: The audit spares the repo's checks and a missing board
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The daily audit stops flagging the repo's own required checks and works when no board is set.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/744
> - https://github.com/dokima-dev/dokima/issues/326
> 
> 
> **User story:** The Setup issue no longer flags the repo's own required checks or a missing board.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the branch rule requires a check the repo added, the Setup issue lists no line about it.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-858/tests/test_audit_no_board.py#L59"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: A required check the repo added gets no line on the Setup issue.*
>   <details><summary><picture><img src="https://

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/test_audit.py; cat tests/test_audit_no_board.py; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> commit 9425c59d11fedbf55e9b220317dbc555c276209e
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 06:07:09 2026 +0000
> 
>     planner for #858 (run 39102760298)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_audit.py          |   7 +--
>  tests/test_audit_no_board.py | 129 +++++++++++++++++++++++++++++++++++++++++++
>  2 files changed, 132 insertions(+), 4 deletions(-)
> commit 9425c59d11fedbf55e9b220317dbc555c276209e
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Sun Oct 18 06:07:09 2026 +0000
> 
>     planner for #858 (run 39102760298)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_audit.py b/tests/test_audit.py
> index a506cdc..cb23d2c 100644
> --- a/tests/test_audit.py
> +++ b/tests/test_audit.py
> @@ -224,10 +224,10 @@ def test_each_difference_gets_one_line_saying_what_is_off_and_what_dokima_needs(
>  
>  
>  def test_too_much_is_a_difference_too(record_property):
> -    """A broader permission, a missing one and an extra required check each get a line.
> +    """Broader and missing permissions each get a line; a repo's own check gets none.
>  
>      Proves 283.1. The faked app has administration: write where Dokima needs read, and no workflows permission; main's rule also
> -    requires a lint check Dokima does not declare. The audit returns three lines, one for each."""
> +

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 20 gh issue view 744 --comments 2>&1 | head -80; python3 -m pytest -q tests/test_audit_no_board.py tests/test_audit.py 2>&1 | tail -30
```

> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}
> FAILED tests/test_audit_no_board.py::test_a_check_the_repo_added_gets_no_line - AssertionError: 858.1: the repo's own lint check is still listed as drift: ['Branch rule of `main` requires `lint`, a check Dokima does not declare.']
> assert not ['Branch rule of `main` requires `lint`, a check Dokima does not declare.']
> FAILED tests/test_audit_no_board.py::test_the_audit_with_no_board_exits_0 - AssertionError: 858.2: with DOKIMA_BOARD empty, the audit exited 1, not 0
>   stdout: ::error::No DOKIMA_BOARD set; the audit needs the board to check it and mark the Setup issue.
>   
>   stderr: 
> assert 1 == 0
>  +  where 1 = CompletedProcess(args=['/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3', '-m', 'dokima.audit', 'acme/widgets'], r...1, stdout='::error::No DOKIMA_BOARD set; the audit needs the board to check it and mark the Setup issue.\n', stderr='').returncode
> FAILED tests/test_audit_no_board.py::test_the_audit_with_no_board_lists_no_board_lines - AssertionError: 858.3: the audit should open exactly one Setup issue, it opened []
>   exit 1
>   stdout: ::error::No DOKIMA_BOARD set; the audit needs the board to check it and mark the Setup issue.
>   
>   stderr: 
>   unsupported calls: []
>   writes: []
> assert 0 == 1
>  +  where 0 = len([])
> FAILED tests/test_audit_no_board.py::test_the_audit_with_no_board_lists_a_missing_needed_check - AssertionError: 858.4: t

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "Label\|label\b\|def \|BOARD\|board" dokima/audit.py | head -80
```

> 3:    python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number") and .github/CODEOWNERS where it runs
> 18:from dokima import board, manifest, settings
> 27:def reason(e):
> 35:def unverified(what, e):
> 39:def compare_labels(live, wanted=None):
> 40:    """One line per label in WANTED that LIVE lacks or holds otherwise.
> 47:            lines.append(f"Label `{name}` is missing; Dokima needs it with color `{want['color']}` and description "
> 51:            lines.append(f"Label `{name}` has color `{have.get('color')}`; Dokima needs `{want['color']}`.")
> 53:            lines.append(f"Label `{name}` has description `{have.get('description') or ''}`; Dokima needs "
> 58:def compare_fields(live, wanted=None):
> 59:    """One line per board field or option in WANTED that LIVE lacks or differs on."""
> 70:                lines.append(f"Option `{option}` of the board field `{field}` is missing; Dokima needs it with color "
> 74:                lines.append(f"Option `{option}` of the board field `{field}` has color `{have.get('color')}`; "
> 77:                lines.append(f"Option `{option}` of the board field `{field}` has description "
> 82:def compare_views(live):
> 87:            lines.append(f"View `{view}` is missing on the board; Dokima needs a `{want['layout']}` view filtered to "
> 97:def compare_rule(branch, live, want):
> 111:def compare_permissions(live):
> 127:def auto_merge(github, repo, rule, queue=True):
> 162:def check(github, repo, root="."):
> 169:    def rule(branch):
> 173:    reads = [("

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 39,56p dokima/audit.py; sed -n 160,245p dokima/audit.py; sed -n 345,370p dokima/audit.py
```

> def compare_labels(live, wanted=None):
>     """One line per label in WANTED that LIVE lacks or holds otherwise.
> 
>     WANTED defaults to the manifest's labels."""
>     lines = []
>     for name, want in (wanted or manifest.LABELS).items():
>         have = live.get(name)
>         if have is None:
>             lines.append(f"Label `{name}` is missing; Dokima needs it with color `{want['color']}` and description "
>                          f"`{want['description']}`.")
>             continue
>         if (have.get("color") or "").lower() != want["color"].lower():
>             lines.append(f"Label `{name}` has color `{have.get('color')}`; Dokima needs `{want['color']}`.")
>         if (have.get("description") or "") != want["description"]:
>             lines.append(f"Label `{name}` has description `{have.get('description') or ''}`; Dokima needs "
>                          f"`{want['description']}`.")
>     return lines
> 
> 
> 
> def check(github, repo, root="."):
>     """(lines, notes): compare()'s lines, and the auto-merge state, which is no drift.
> 
>     What Dokima needs comes from the merged settings of the repo at root."""
>     got = settings.read(root)
>     rules = {}
> 
>     def rule(branch):
>         rules[branch] = github.branch_rule(repo, branch)
>         return rules[branch]
> 
>     reads = [("Labels", lambda: github.labels(repo), lambda live: compare_labels(live, manifest.labels(got))),
>              ("Board fields", github.fields, lambda live: compare_fields(live, manifest.fields(got))),
>              ("Board

**Agent:** Tests all fail for the right reason today; checking one label text, then writing the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n -A3 "filed-by-dokima" dokima/manifest.py | head; sed -n 1,12p .github/workflows/audit.yml
```

> 20:    "filed-by-dokima": {"color": "bfd4f2", "description": "Created automatically, not by a person"},
> 21-}
> 22-# Each label's key in the settings' labels and colors.labels groups, by its shipped name.
> 23:LABEL_KEYS = {"autopilot": "autopilot", "filed-by-dokima": "filed"}
> 24-
> 25-FIELDS = {
> 26-    "Status": {
> name: audit
> # The drift audit (dokima/audit.py): compares the repo's settings with what Dokima needs (dokima/manifest.py) and
> # reports anything off on one pinned Setup issue, marked Needs you on the board; a clean repo gets no writes. It runs
> # once a day by itself, and whenever the owner presses Run workflow; nothing else starts it. Every audit waits in one
> # queue for the repo, shared with no other workflow and never cancelled by a newer run, so two audits never post
> # twice. It acts as the Dokima app and reads the board from DOKIMA_BOARD; without the board it fails and says why.
> on:
>   schedule:
>     - cron: "17 6 * * *"
>   workflow_dispatch:
>   # Called by the one workflow an adopter installs (dokima/install/dokima.yml), through entry.yml (#812).
>   workflow_call:

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote four criteria and four new tests that run the audit from outside.",
          "The planner changed one older test so a repo's own check is no longer drift."],
  "decided": ["Board fields and views are skipped when no board is set; other drift is still reported."],
  "open": ["The audit workflow's comment still says the audit fails without a board."]},
 "verdict": "approve",
 "summary": "The plan carries all four asks, each with one test that fails today for the right reason.",
 "raises": [],
 "answers": [{"raise": "P1", "answer": "done", "why": "The stale comment is real and outside this issue, since workflow files stay untouched here."}],
 "asks": [
  {"ask": "When the branch rule requires a check the repo added, the Setup issue lists no line about it.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "858.1"},
  {"ask": "When no board is set, the audit finishes with exit code 0.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "858.2"},
  {"ask": "When no board is set, the Setup issue lists no line about board fields or views.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "858.3"},
  {"ask": "When no board is set and the branch rule lacks a check Dokima needs, the Setup issue lists that check.", "source": "https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246343182", "criterion": "858.4"}],
 "behaviors": [
  {"criterion": "858.1", "one_behavior": true, "why": "One case: a repo's own required check gets no line."},
  {"criterion": "858.2", "one_behavior": true, "why": "One result: exit code 0 with no board."},
  {"criterion": "858.3", "one_behavior": true, "why": "One result: no board field or view lines with no board."},
  {"criterion": "858.4", "one_behavior": true, "why": "One result: a missing needed check is still listed with no board."}],
 "edge_cases
```

> Exit code 1
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Board fields and views are skipped when no board is set; other drift is still reported./With no board, board fields and views are skipped; other drift is still reported./' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 858 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "searched" dokima/agent*.py dokima/*.py | head -20; ls /tmp/pack
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/agent_autopilot.py:224:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/agent_autopilot.py:224:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/raises.py:22:# An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> dokima/raises.py:23:SEARCHED = "searched"
> dokima/raises.py:45:    """What a reviewer's filing lac

`10. Bash`
```
cd /tmp/pack; cat owner_words.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:5000])"; python3 -c "
import json;d=json.load(open('open_issues.json'));
for i in d: print(i.get('number'), i.get('title'))" | grep -i -E "audit|board|workflow" 
```

> {
>  "https://github.com/dokima-dev/dokima/issues/744": "Phase 3 of #272 (trial blockers). Things that would bite an adopter on day one.\n\n**What**\n- The required \"Acceptance criteria\" check fails every PR without an approved Dokima plan, including human and Dependabot PRs. Setting `merge.unplanned_prs: allow` (default) lets them through; only Dokima's own PRs are held to the plan.\n- The daily audit (`audit.py:99`) reports any extra required check on the branch rule as drift, so an adopter's own CI reads as a problem. Checks the repo added are not drift.\n- The audit fails when no board is set; boards are optional and only exist for organizations. No board means nothing to report.\n- The card redraws only when Dokima's own workflows finish, not when the adopter's CI does. The merge gate already waits on every required check; the card must show them.\n- Nothing installs the target repo's own dependencies; only pytest is installed (`full-suite.yml:27`, `agent.yml:262`). The `tests.install` setting runs first.\n- `tests.exclude` keeps tests the repo marks (for example live network tests) off the merge gate. Owner note: #341 said everything runs at the gate; this is the repo's own choice in settings, default empty.\n\n**Done when:** acceptance items 16 and 17 on #272 pass: a human PR merges on a trial repo; the repo's own CI is neither flagged nor broken.\n",
>  "https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246343182": "/plan Yes: leave both out, since they alre

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d["answers"][0].update({"searched":[326,280,284],"verdict":"new"})
u="https://github.com/dokima-dev/dokima/issues/744"
d["asks"]=[
 {"ask":"Checks the repo added are not drift.","source":u,"criterion":"858.1"},
 {"ask":"The audit fails when no board is set; boards are optional and only exist for organizations.","source":u,"criterion":"858.2"},
 {"ask":"No board means nothing to report.","source":u,"criterion":"858.3"},
 {"ask":"Fix the review's two blockers.","source":u+"#issuecomment-6246343182","criterion":"858.4"}]
json.dump(d,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 858 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#858](https://github.com/dokima-dev/dokima/issues/858) (the audit spares the repo's checks and a missing board). The review is in `/tmp/dokima-out/review.json`, and it passes both hand-back checks.

- **Asks covered:** each ask in [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety: human pull requests pass, audit spares repo checks) that falls in this story has its own criterion:
  - checks the repo added are not drift;
  - the audit no longer fails when no board is set;
  - no board means no board lines;
  - a check Dokima needs that the branch rule lacks is still listed.
- **Tests:** the four new tests and the one changed older test fail today for the right reasons:
  - the repo's own `lint` check is still listed as drift;
  - with no board set, the audit stops with exit code 1;
  - so with no board, no Setup issue gets opened.
- **Changed older test:** it only drops the line for the repo's own extra check, which the owner asked to remove. Its two permission lines are still checked.
- **Planner's issue (P1):** I agreed it should be filed. The audit workflow's comment still says the audit fails without a board, which this change makes untrue. Workflow files are off-limits for this issue, so it needs its own issue. I checked [#326](https://github.com/dokima-dev/dokima/issues/326) (daily audit flags only real drift), [#280](https://github.com/dokima-dev/dokima/issues/280) (drift audit) and [#284](https://github.com/dokima-dev/dokima/issues/284) (audit fixes harmless gaps); none of them covers it, so it is new.

I raised no blockers.

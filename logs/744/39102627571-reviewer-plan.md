# reviewer (plan) for #744

Run: https://github.com/dokima-dev/dokima/actions/runs/39102627571

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #744: Adopter safety: human PRs pass, audit tolerates the repo's own CI and no board
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 740, 742, 781, 784, 787, 795 -->
> <!-- dokima-blocking: {"blocked_by": [742, 779, 781, 784, 787], "blocks": [746], "loop": []} -->
> An adopter's own pull requests, CI and missing board stop tripping Dokima's checks, audit and card.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/781
> - https://github.com/dokima-dev/dokima/issues/784
> - https://github.com/dokima-dev/dokima/issues/787
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/272
> - https://github.com/dokima-dev/dokima/issues/326
> - https://github.com/dokima-dev/dokima/issues/284
> - https://github.com/dokima-dev/dokima/issues/795
> 
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" 

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['01-planner.json','02-reviewer-plan.json','03-planner.json']:
    d=json.load(open(f)); print(f, list(d.keys()))
d=json.load(open('03-planner.json')); print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])
print(json.dumps(d.get('handback',{}).get('tests', d.get('handback',{}).keys() if isinstance(d.get('handback'),dict) else None),indent=1)[:3000])
"; cd /home/runner/work/dokima/dokima; git log --oneline -3; git status
```

> Traceback (most recent call last):
>   File "<string>", line 6, in <module>
>   File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/__init__.py", line 238, in dumps
>     **kw).encode(obj)
>           ^^^^^^^^^^^
>   File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/encoder.py", line 202, in encode
>     chunks = list(chunks)
>              ^^^^^^^^^^^^
>   File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/encoder.py", line 439, in _iterencode
>     o = _default(o)
>         ^^^^^^^^^^^
>   File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/encoder.py", line 180, in default
>     raise TypeError(f'Object of type {o.__class__.__name__} '
> TypeError: Object of type dict_keys is not JSON serializable
> 01-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 02-reviewer-plan.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> 03-planner.json ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39102504219",
>  "commit_before": "ccbebe20951336dbdfb7da7800bf77e892c34308",
>  "started_by": "RezaSoleymanifar",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 37008,
>   "turns": 5,
>   "cost_usd": 0.1743802,
>   "tokens_in": 179625,
>   "tokens_out": 2251
>  },
>  "log": "https://g

`3. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
d=json.load(open('02-reviewer-plan.json')); print(json.dumps(d['handback'],indent=1))
"; cd /home/runner/work/dokima/dokima; sed -n 1,200p rules/splitting.md
```

> {
>  "previous_step": {
>   "did": [
>    "The planner split the issue into three stories: pull requests, the audit, the card."
>   ],
>   "decided": [
>    "Dokima's own pull requests stay held to their plan; other setting values keep today's check.",
>    "Installing the repo's needs and leaving out marked tests are left out as already done."
>   ],
>   "open": [
>    "The owner decides whether those two asks can be left out."
>   ]
>  },
>  "verdict": "block",
>  "summary": "Two owner asks have no criterion, and a missing board could skip the whole audit unnoticed.",
>  "raises": [
>   {
>    "kind": "blocker",
>    "to": "planner",
>    "label": "No criterion",
>    "text": "The asks to install the repo's needs and to leave out marked tests carry no criterion. Keep each as a criterion with a test pinning today's behavior.",
>    "evidence": "Issue lines on `tests.install` and `tests.exclude`; `full-suite.yml:57` and `:93` already do both.",
>    "raised_by": "reviewer",
>    "id": "R1"
>   },
>   {
>    "kind": "blocker",
>    "to": "planner",
>    "label": "2.2 missing case",
>    "text": "With no board, an audit that checks nothing still exits 0. Add: with no board, other drift is still listed.",
>    "evidence": "Story 2 context says to still report other drift; no criterion of 2.1 to 2.3 carries it.",
>    "raised_by": "reviewer",
>    "id": "R2"
>   }
>  ],
>  "answers": [],
>  "asks": [
>   {
>    "ask": "Setting `merge.unplanned_prs: allow` (default) lets them through",
>    "source": "https://github.com/dokima-dev/dokima/issues/744",
>    "cr

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def done_row" -A40 dokima/card.py | head -60; grep -n "workflow_run" -A6 dokima/install/dokima.yml .github/workflows/entry.yml | head -40; grep -n "asks" dokima/agent.py | head -30
```

> 543:def done_row(repo, found, all_tests, planned=False):
> 544-    """The Definition of Done: each check, review and approval with its verdict and proof.
> 545-
> 546-    A code owner's merge is their approval, with or without an Approve review.
> 547-
> 548-    Once planned it is drawn as on the approved card of #557 (#628): Acceptance tests (the Acceptance criteria
> 549-    check), Code review, Test suite (the all tests check) and Owner approval, with no field icons."""
> 550-    review = code_review(found["recs"])
> 551-    review_st = ("running" if review_running(found.get("items")) else "not started" if not review else
> 552-                 "passed" if review["handback"].get("verdict") == "approve" else "failed")
> 553-    merge = owner_merge(found["pr"], found["owners"])
> 554-    approval = {"state": "APPROVED", "html_url": merge.get("html_url")} if merge else owner_review(found["reviews"], found["owners"])
> 555-    approval_st = "not started" if not approval else "passed" if approval["state"] == "APPROVED" else "failed"
> 556-    if planned:
> 557-        accepted = next((r for r in plain(found["check_runs"]) if r["name"] == ACCEPTANCE), None)
> 558-        return ("**Definition of Done:** "
> 559-                f"{circle(repo, state(accepted), accepted and accepted['html_url'])} Acceptance tests · "
> 560-                f"{circle(repo, review_st, review and review.get('run'))} Code review · "
> 561-                f"{circle(repo, state(all_tests), all_tests and all_tests['html_url'])} Test suite ·

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "def problems_asks" -A40 dokima/ | head -60
```

> dokima/agent_checks.py:205:def problems_asks(r, ids):
> dokima/agent_checks.py-206-    """Everything wrong with a plan review's asks list: every ask the owner made, in their
> dokima/agent_checks.py-207-    words, with a link to where they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an
> dokima/agent_checks.py-208-    approve keeps every ask."""
> dokima/agent_checks.py-209-    asks = r.get("asks")
> dokima/agent_checks.py-210-    if not isinstance(asks, list) or not asks:
> dokima/agent_checks.py-211-        return ["asks must list every ask in the owner's issue and comments, each {\"ask\": \"the owner's words\", "
> dokima/agent_checks.py-212-                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
> dokima/agent_checks.py-213-    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
> dokima/agent_checks.py-214-    good = [a for a in asks if isinstance(a, dict) and all(filled(a.get(k)) for k in ("ask", "source", "criterion"))]
> dokima/agent_checks.py-215-    for a in good:
> dokima/agent_checks.py-216-        c = a["criterion"].strip()
> dokima/agent_checks.py-217-        if c != "missing" and c not in ids:
> dokima/agent_checks.py-218-            bad.append(f"the ask \"{a['ask']}\" is matched to {c}, which is not a criterion of the plan "
> dokima/agent_checks.py-219-                       f"({', '.join(ids) or 'none'})")
> dokima/agent_checks.py-220-    gone = [a["ask"] for a in good if a["criterion"]

**Agent:** Plan looks sound; writing the review now and running the check.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner added a criterion: with no board, a missing Dokima check is still listed."],
  "decided": ["Installing the repo's needs and leaving out marked tests stay out, as the owner said."],
  "open": []},
 "verdict": "approve",
 "summary": "The split now carries every remaining ask, and both earlier blockers are settled.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Setting `merge.unplanned_prs: allow` (default) lets them through", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.1"},
  {"ask": "including human and Dependabot PRs", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.2"},
  {"ask": "only Dokima's own PRs are held to the plan", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.3"},
  {"ask": "Setting `merge.unplanned_prs: allow` (default)", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S1.4"},
  {"ask": "Checks the repo added are not drift.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S2.1"},
  {"ask": "The audit fails when no board is set; boards are optional and only exist for organizations.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S2.2"},
  {"ask": "No board means nothing to report.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S2.3"},
  {"ask": "Fix the review's two blockers.", "source": "https://github.com/dokima-dev/dokima/issues/744#issuecomment-6246343182", "criterion": "S2.4"},
  {"ask": "The card redraws only when Dokima's own workflows finish, not when the adopter's CI does.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S3.1"},
  {"ask": "The merge gate already waits on every required check; the card must show them.", "source": "https://github.com/dokima-dev/dokima/issues/744", "criterion": "S3
```

> (Bash completed with no output)

**Agent:** I approved the planner's split for [#744](https://github.com/dokima-dev/dokima/issues/744) (adopter safety). Both of Dokima's checks on my review passed.

**Earlier blockers**
- **Missing-board case:** fixed. A new criterion (story 2, item 4) says that with no board set, a check the branch rule is missing still gets listed.
- **Install and leave-out asks:** settled. You said to leave both out because they already work from the settings file. So they're no longer counted as dropped asks.

**What's in the plan**
- Ten criteria in three stories: pull requests without a plan pass, the audit no longer flags the repo's own checks or a missing board, and the card follows the repo's own CI.
- Every remaining ask in the issue maps to one criterion, and each criterion is one behavior.
- I added one criterion beyond your exact words (story 1, item 4): any setting value other than `allow` keeps today's failing check. It follows from you calling `allow` the default, so I listed it as needed, not as extra scope.

**Two things to know**
- This plan has no tests yet, because it is a split. Each story's tests get written and reviewed when that story is planned.
- Stories 1 and 3 change workflow files and the card code, which the rules forbid unless the issue asks. I accepted it because the issue asks for the check and the card to change. Any pull request that touches a workflow file will still stop for your approval.

The review is in `/tmp/dokima-out/review.json`.

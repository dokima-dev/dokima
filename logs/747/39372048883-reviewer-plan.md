# reviewer (plan) for #747

Run: https://github.com/dokima-dev/dokima/actions/runs/39372048883

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (30.1KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/128f7b78-7503-4541-98c7-63d5360dcbcf/tool-results/bz5b5t3cb.txt
> 
> Preview (first 2KB):
> .:
> total 132
> drwxr-xr-x  3 runner runner  4096 Oct 20 04:54 .
> drwxrwxrwt 18 root   root    4096 Oct 20 04:54 ..
> drwxr-xr-x  2 runner runner  4096 Oct 20 04:54 in
> -rw-r--r--  1 runner runner 13057 Oct 20 04:54 issue.md
> -rw-r--r--  1 runner runner     2 Oct 20 04:54 open_blockers.json
> -rw-r--r--  1 runner runner 66928 Oct 20 04:54 open_issues.json
> -rw-r--r--  1 runner runner  6882 Oct 20 04:54 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 20 04:54 parent.json
> -rw-r--r--  1 runner runner 17056 Oct 20 04:54 plan.json
> 
> in:
> total 28
> drwxr-xr-x 2 runner runner  4096 Oct 20 04:54 .
> drwxr-xr-x 3 runner runner  4096 Oct 20 04:54 ..
> -rw-r--r-- 1 runner runner 18128 Oct 20 04:54 01-planner.json
> # Issue #747: One shared GitHub App: dokima[bot] everywhere, one-click install
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 742, 812 -->
> <!-- dokima-blocking: {"blocked_by": [746], "blocks": [749], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle

`2. Bash`
```
cd /tmp/pack; cat issue.md; cat open_blockers.json parent.json; cat owner_words.json
```

> # Issue #747: One shared GitHub App: dokima[bot] everywhere, one-click install
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 742, 812 -->
> <!-- dokima-blocking: {"blocked_by": [746], "blocks": [749], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/749
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/812
> 
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> After the Vintage trial, before release. Replaces the "each adopter creates their own App" step from #41 with a one-click install, while keeping self-made Apps as a fallback for teams that refuse a shared one.
> 
> **What**
> - One GitHub App named `dokima` (the name is free as of 2026-10-15), owned by dokima-dev. Everything it does shows as `dokima[bot]` on every repo: comments, PRs, cards, commits.
> - Install journey: click Install on github.com/apps/dokima and pick repos; Dokima opens a PR adding the thin workflow and `sett

`3. Bash`
```
cd /tmp/pack; cat plan.json; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k not in ('handback','plan')},indent=1)[:3000])"
```

> {
>  "kind": "feature",
>  "title": "One shared Dokima App with a one-click install",
>  "summary": "Every repo runs Dokima through one shared App, set up fully by its install.",
>  "feature": "Installing one shared App onboards a repo fully; runs get tokens from a small service, and self-made Apps still work.",
>  "stories": [
>   {
>    "title": "Register the shared App from a prefilled manifest",
>    "user_story": "The owner registers Dokima's shared App with one click, and never handles its private key.",
>    "acceptance_criteria": [
>     {
>      "text": "The shared App's manifest asks for write access to workflows, secrets and administration.",
>      "words": "The cost is broader App permissions (workflows, secrets, administration)",
>      "source": "https://github.com/dokima-dev/dokima/issues/747#issuecomment-6254370728",
>      "files": [
>       "dokima/app.json",
>       "dokima/register.py"
>      ],
>      "no_edge_cases": "Its own planner lists them with its tests."
>     },
>     {
>      "text": "When the owner runs registration, GitHub's new App page opens prefilled, so one Create click registers it.",
>      "words": "a prefilled App manifest, so the owner clicks Create once",
>      "source": "https://github.com/dokima-dev/dokima/issues/747#issuecomment-6254370728",
>      "files": [
>       "dokima/app.json",
>       "dokima/register.py"
>      ],
>      "no_edge_cases": "Its own planner lists them with its tests."
>     },
>     {
>      "text": "When the owner clicks Create, the App's private key is stored in t

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat rules/splitting.md; grep -n "split\|S<s>\|no_edge_cases" -i dokima/agent.py | head -60; ls dokima
```

> ## Splitting and the graph
> 
> - Code works out the stories from the files each criterion changes: criteria sharing a code file, directly or through another criterion, are one story; criteria with no code file in common are separate stories. Markdown files never join criteria. A story holds at most 10 criteria: a larger group is cut into consecutive stories of at most 10, each later one depending on the one before, so they take turns on their shared files.
> - 2 or more children, one level; every promise owned by exactly one child; children may depend on siblings, with no cycles.
> - The planner proposes; code checks the rules and files real GitHub sub-issues. `/work` on the parent approves the split and every child's plan.
> - When a child merges, every sibling whose needs have landed starts; independent children run in parallel. GitHub is the state.
> - When the last open sub-issue of a parent closes, on autopilot or not, the parent closes as completed with one line saying its whole tree is done, which counts as a close one level up; a sub-issue closed as not planned counts as done, and a parent already closed is left alone. Every 15-minute card sweep closes the same way any open parent whose sub-issues are all closed, so a missed close never leaves a finished parent in Work.
> 48:    story_body, file_split, AUTOPILOT, issue_tree, switch_autopilot, autopilot_comment, AUTOPILOT_LINE,
> agent.py
> agent_autopilot.py
> agent_checks.py
> agent_claude.py
> agent_codex.py
> agent_github.py
> agent_kimi.py
> 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/install/dokima.yml | head -80; ls dokima/install; cat dokima/app.json; head -30 dokima/manifest.py dokima/setup.py; grep -n "environment\|DOKIMA_APP" .github/workflows/entry.yml | head -20
```

> # Dokima, run from Dokima's own repo at a release tag (#812). Copy this file to .github/workflows/dokima.yml.
> name: dokima
> on:
>   issues:
>   issue_comment:
>   pull_request_target:
>   pull_request_review:
>   pull_request_review_comment:
>   merge_group:
>   push:
>   schedule: [{cron: "*/15 * * * *"}, {cron: "17 6 * * *"}]
>   # Every workflow, the repo's own CI included, so the card redraws when it finishes (#859).
>   workflow_run: {workflows: ["*"], types: [in_progress, completed]}
>   repository_dispatch: {types: [dokima-next]}
>   workflow_dispatch:
> permissions: {contents: read, issues: write, pull-requests: read, actions: read, checks: read}
> jobs:
>   dokima:
>     uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.8
>     secrets: {DOKIMA_APP_KEY: "${{ secrets.DOKIMA_APP_KEY }}", CLAUDE_CODE_OAUTH_TOKEN: "${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}", CODEX_API_KEY: "${{ secrets.CODEX_API_KEY }}", KIMI_API_KEY: "${{ secrets.KIMI_API_KEY }}"}
> dokima.yml
> settings.yaml
> {
>   "name": "Dokima Runtime",
>   "description": "Dokima's bot. Opens PRs, posts the card, never approves. Nothing merges until it's proven.",
>   "url": "https://github.com/RezaSoleymanifar/dokima",
>   "hook_attributes": {
>     "url": "https://github.com/RezaSoleymanifar/dokima",
>     "active": false
>   },
>   "public": false,
>   "default_permissions": {
>     "contents": "write",
>     "pull_requests": "write",
>     "issues": "write",
>     "checks": "read",
>     "actions": "write",
>     "statuses": "read",
>     "metadata": "read",
>     "workflows": "w

**Agent:** Reading the plan against the owner's comments; next I check the repo's install docs and app permissions.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "PERMISSIONS\|administration\|secrets" dokima/manifest.py | head; ls docs 2>/dev/null; grep -rln "DOKIMA_APP_KEY\|Create.*App\|install" --include=*.md . | grep -v node_modules | head; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(type(d), len(d))
for i in (d if isinstance(d,list) else d.values()):
  n=i.get('number') if isinstance(i,dict) else None
  if n in (746,749,876,877,874,745,942,930,272): print(n,i.get('title'),i.get('state'))
"
```

> 54:PERMISSIONS = {
> 63:    "administration": "read",
> 65:    "secrets": "read",  # the names of the repo secrets, never their values: the audit checks the keys are set (#876)
> 118:    (r"branches/[^/]+/protection|rulesets(/|$)", "administration"),
> 126:    (r"actions/secrets(/|$)", "secrets"),
> 192:        have = PERMISSIONS.get(perm)
> brand
> favicon.svg
> index.html
> wiki
> README.md
> dokima/roles/raising.md
> CHANGELOG.md
> docs/wiki/Installing.md
> <class 'list'> 199
> 942 Auto approve setup reports success on personal repos, where GitHub drops the app's review bypass None
> 930 An adopter's installed workflow passes only Claude Code's key, so Codex and Kimi keys never reach Dokima's jobs. None
> 749 Opt-in usage ping from the shared workflow None
> 272 Dokima can be onboarded onto any new repo, starting with dokima-mcp None

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rln "app.json" tests dokima | head; grep -n "app.json" dokima/*.py | head; head -40 docs/wiki/Installing.md
```

> tests/test_text_only.py
> tests/test_manifest.py
> tests/test_audit_auto_merge.py
> tests/test_keys.py
> tests/fixtures/cards/557.card.md
> tests/fixtures/cards/557.inputs.json
> tests/test_plan_check_rerun.py
> tests/test_app.py
> # Installing
> 
> **Honest status:** δokima runs on its own repo, [dokima-dev/dokima](https://github.com/dokima-dev/dokima). Onboarding other repos (one link, a few minutes, never overwriting your labels or files) is **in progress**: [#272](https://github.com/dokima-dev/dokima/issues/272). Until then, setup is manual and the steps below describe what the code expects.
> 
> Nothing to host: it all runs in GitHub Actions. You do need a GitHub App, secrets, one workflow file and one settings file.
> 
> ## Requirements
> 
> - A GitHub repo, ideally in an **organization** (the project board and merge queue need one; on personal repos those extras are skipped).
> - A Claude subscription: runs use Claude Code with an OAuth token.
> - Python 3.12 and `pytest`. Other languages are **Planned**.
> 
> ## 1. GitHub App
> 
> Create an app from `dokima/app.json` and install it on the repo. Permissions it asks for:
> 
> | Permission | Level |
> |---|---|
> | contents, pull requests, issues, actions, workflows, organization projects | write |
> | checks, statuses, metadata, administration, secrets | read |
> 
> The app posts every comment, card and PR. It never approves.
> 
> ## 2. Secrets and variables
> 
> Add these as **repo** secrets and variables (Settings, Secrets and variables, Actions). δokima runs from its own repo, so a

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "app.json\|PERMISSIONS" tests/test_manifest.py tests/test_app.py | head
```

> tests/test_manifest.py:9:    PERMISSIONS   {app permission: "read" | "write"}, the same as dokima/app.json's default_permissions
> tests/test_manifest.py:141:    assert m.PERMISSIONS, "282.1: the manifest declares no app permissions"
> tests/test_manifest.py:142:    for name, level in m.PERMISSIONS.items():
> tests/test_manifest.py:462:        mp.delitem(m.PERMISSIONS, "administration")
> tests/test_manifest.py:468:# 282.4: the manifest's app permissions match dokima/app.json, with Administration read
> tests/test_manifest.py:471:    """The manifest's app permissions equal dokima/app.json's, with Administration read and Organization projects write.
> tests/test_manifest.py:477:    app = json.load(open(os.path.join(ROOT, "dokima", "app.json")))["default_permissions"]
> tests/test_manifest.py:479:        f"282.4: dokima/app.json asks for Administration {app.get('administration')!r}, not read"
> tests/test_manifest.py:480:    assert m.PERMISSIONS.get("administration") == "read", \
> tests/test_manifest.py:481:        f"282.4: the manifest asks for Administration {m.PERMISSIONS.get('administration')!r}, not read"

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "boxes\|superseded\|conflicts\|poor_tests\|\"edges\"\|'edges'" dokima/agent_checks.py | head -40
```

> 226:BOXES = {"dropped": ("words", "source"), "added": ("what", "kind", "serves"), "superseded": ("old", "new", "retired"),
> 227:         "conflicts": ("a", "b", "ask"), "edges": (), "poor_tests": ("test", "passes_with", "fix")}
> 230:def problems_boxes(r, ids):
> 231:    """Everything wrong with a review's six boxes (#819), each reason naming its box.
> 235:    boxes = r.get("boxes")
> 236:    if not isinstance(boxes, dict):
> 237:        return ["boxes must be an object holding the six boxes: " + ", ".join(BOXES) + "; a box with nothing in it says none"]
> 240:        if box not in boxes:
> 241:            bad.append(f"boxes has no {box} box: write none when there is nothing in it")
> 243:        v = boxes[box]
> 244:        if box == "edges":
> 252:        bad += problems_items(boxes, box, keys)
> 449:                bad += problems_boxes(data, plan_criteria(plan, number))

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 200,300p dokima/agent_checks.py
```

> if not isinstance(v, list) or not all(filled(x) for x in v):
>                 bad.append(f"edge_cases' {f} for criterion {k} must be a list of plain lines, [] when there are none")
>     return bad
> 
> 
> def problems_asks(r, ids):
>     """Everything wrong with a plan review's asks list: every ask the owner made, in their
>     words, with a link to where they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an
>     approve keeps every ask."""
>     asks = r.get("asks")
>     if not isinstance(asks, list) or not asks:
>         return ["asks must list every ask in the owner's issue and comments, each {\"ask\": \"the owner's words\", "
>                 "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
>     bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
>     good = [a for a in asks if isinstance(a, dict) and all(filled(a.get(k)) for k in ("ask", "source", "criterion"))]
>     for a in good:
>         c = a["criterion"].strip()
>         if c != "missing" and c not in ids:
>             bad.append(f"the ask \"{a['ask']}\" is matched to {c}, which is not a criterion of the plan "
>                        f"({', '.join(ids) or 'none'})")
>     gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
>     if r.get("verdict") == "approve" and gone:
>         bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
>     return bad
> 
> 
> BOXES = {"dropped": ("words", "

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
from dokima.agent_checks import plan_criteria; import json
print(plan_criteria(json.load(open('/tmp/pack/plan.json')),747))"
```

> ['S1.1', 'S1.2', 'S1.3', 'S2.1', 'S2.2', 'S2.3', 'S2.4', 'S2.5', 'S3.1', 'S3.2', 'S3.3', 'S4.1', 'S4.2', 'S4.3', 'S4.4', 'S4.5', 'S4.6', 'S4.7', 'S4.8', 'S5.1', 'S5.2', 'S5.3', 'S5.4', 'S6.1', 'S6.2', 'S6.3', 'S6.4', 'S7.1', 'S7.2', 'S8.1', 'S8.2']

**Agent:** Writing the review now: four blockers for the planner, then running the checker.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/747"
C1=I+"#issuecomment-6203494000"; C2=I+"#issuecomment-6203583734"; C3=I+"#issuecomment-6254370728"
C4=I+"#issuecomment-6257060752"; C5=I+"#issuecomment-6257614785"
ids=['S1.1','S1.2','S1.3','S2.1','S2.2','S2.3','S2.4','S2.5','S3.1','S3.2','S3.3','S4.1','S4.2','S4.3','S4.4','S4.5','S4.6','S4.7','S4.8','S5.1','S5.2','S5.3','S5.4','S6.1','S6.2','S6.3','S6.4','S7.1','S7.2','S8.1','S8.2']
two={"S1.3":"Two results: the key is stored in the service, and never saved to disk.",
"S2.3":"Three cases in one: forged, expired and another repo's identity.",
"S2.5":"Two results: the key is read only in the service, and no reply carries it.",
"S4.6":"Two results: missing labels are made, and existing labels stay unchanged.",
"S4.8":"Two results: onboarding finishes, and the first issue asks where tests live.",
"S5.4":"Two results: onboarding finishes unprotected, and it says what is lost and how to get it.",
"S6.4":"Two results: the page has no key field, and the service never receives one.",
"S8.1":"Two results: the repo joins the install, and it gets onboarded."}
beh=[{"criterion":k,"one_behavior":k not in two,"why":two.get(k,"One action, one result the owner can see.")} for k in ids]
edges={k:"covered" for k in ids}
ec=[{"criterion":k,"cut":[],"missing":[]} for k in ids]
r={
"previous_step":{"did":["The planner proposed splitting the issue into eight stories with 31 criteria.","It left each story's tests and edge cases to that story's own planner."],
 "decided":["Installing the App onboards the repo directly, with no setup pull request.","The command line path stays; the chat tool path stays parked."],
 "open":["Three questions wait for the owner: the manifest, setup as a pull request, bug report contents."]},
"verdict":"block",
"summary":"Blocked: eight criteria bundle two results, one names the wrong key, docs are missing, one criterion misses a file.",
"raises":[

```

> Exit code 1
> previous_step open line 1 holds 16 words, over its cap of 15: cut 1, keep the facts

`13. Bash`
```
sed -i 's/Three questions wait for the owner: the manifest, setup as a pull request, bug report contents./Three questions wait for the owner: manifest, setup as pull request, bug report contents./' /tmp/gen.py; python3 /tmp/gen.py && cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 747 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

**Agent:** I've blocked the plan for [#747](https://github.com/dokima-dev/dokima/issues/747) (one shared App, one-click install). The review file is in `/tmp/dokima-out/review.json` and passes both checks.

The planner proposed eight stories with 31 criteria. It left each story's tests and edge cases to that story's own planner.

**Four blockers, all for the planner:**
1. **Two results in one criterion.** S1.3, S2.3, S2.5, S4.6, S4.8, S5.4, S6.4 and S8.1 each bundle two results or cases. For example, S4.6 says missing labels are created and existing labels stay unchanged. Each needs splitting into one criterion per result.
2. **S2.4 names the wrong key.** It says the service returns a key for the run's own repo. Filing a bug upstream needs a key for Dokima's own repo, which is what the owner described in the 2026-10-18 comment.
3. **No criterion for docs.** The owner listed "the bug-report checkbox and docs" as part of this work. Nothing covers it, and `docs/wiki/Installing.md` still tells adopters to create their own App.
4. **S1.1 misses a file.** It changes the App's permissions, but the same list is kept in `dokima/manifest.py`. An older test (`tests/test_manifest.py:468`) also requires the administration permission to stay read-only. S1.1 needs that file added.

**Waiting for the owner:** the planner's three questions:
- whether the prefilled manifest is still wanted now that the App is registered as `dokima-dev`;
- whether teams that refuse the broad permissions get the setup as a pull request;
- whether bug reports filed upstream carry only Dokima's step, its error and the version.

I didn't answer any of them for the owner. The owner left the second and third open, and the first changes how the App gets set up.

Every other ask in the issue and its comments maps to a criterion.

There were no open blockers from earlier rounds to answer, and I raised no outside issues.

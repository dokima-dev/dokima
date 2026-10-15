# reviewer (plan) for #716

Run: https://github.com/dokima-dev/dokima/actions/runs/38674702249

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #716: All tests run on the owner's commits
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Pins that the owner's pushes to a Dokima pull request run all tests, like agent pushes.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/715
> 
> 
> **User story:** The owner's pushes to a Dokima pull request get the same all tests check as agent work.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A push by the owner to a Dokima pull request runs all tests, with no rule skipping the owner.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-716/tests/test_checks.py#L66"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: The merge gate still runs every test, in parallel, exactly as today.*
>   - Edge cases: none, be

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests | head -80; sed -n 1,140p tests/test_checks.py; cat .github/workflows/full-suite.yml; cat /tmp/pack/parent.json | head -50; cat /tmp/pack/open_issues.json | head -30
```

> commit 9356fce79847b06a69e6354e2de92e0f8da9fbce
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 03:08:05 2026 +0000
> 
>     planner for #716 (run 38673949021)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_checks.py | 53 ++++++++++++++++++++++++++++++++++++++++++++++++++--
>  1 file changed, 51 insertions(+), 2 deletions(-)
> commit 9356fce79847b06a69e6354e2de92e0f8da9fbce
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 03:08:05 2026 +0000
> 
>     planner for #716 (run 38673949021)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_checks.py b/tests/test_checks.py
> index ae0582b..18ef1d2 100644
> --- a/tests/test_checks.py
> +++ b/tests/test_checks.py
> @@ -2,7 +2,48 @@ import os
>  import sys
>  
>  sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> +sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
>  from dokima import checks  # noqa: E402
> +import test_start as ts  # noqa: E402
> +
> +BOT = "dokima-runtime[bot]"
> +DEFAULT_TYPES = ("opened", "synchronize", "reopened")  # GitHub's pull_request_target types when none are listed
> +FILTERS = ("branches", "branches-ignore", "paths", "paths-ignore")  # trigger filters push_runs_all_tests does not play
> +
> +
> +def push_runs_all_tests(pusher):
> +    """Whether all tests run when `pusher` pushes to a

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "passing_today" -r dokima | head; grep -n "def passing_today" -A40 dokima/planner.py; cat /tmp/pack/in/01-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> dokima/planner.py:568:def passing_today(added, base="HEAD"):
> dokima/planner.py:666:            bad += unsummarized(tc["added"]) + unnumbered(tc["added"]) + passing_today(tc["added"], base)
> 568:def passing_today(added, base="HEAD"):
> 569-    """Run each new test (path::name) on main's code (`base`) with the planner's tests on top; the ones that pass or
> 570-    are skipped, or run past the limit."""
> 571-    out = []
> 572-    if not added:
> 573-        return out
> 574-    with tempfile.TemporaryDirectory() as into:
> 575-        main_with_tests(base, into)
> 576-        for t in sorted(added):
> 577-            try:
> 578-                r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", t], cwd=into,
> 579-                                   capture_output=True, text=True, timeout=NEW_TEST_TIMEOUT)
> 580-            except subprocess.TimeoutExpired:
> 581-                out.append(f"{t} is a new test still running after {NEW_TEST_TIMEOUT} s on today's code; it was stopped")
> 582-                continue
> 583-            if r.returncode in (0, 5):  # 0: passed or skipped, 5: nothing ran
> 584-                out.append(f"{t} is a new test that passes today (or is skipped); every new test must fail on today's code")
> 585-    return out
> 586-
> 587-
> 588-def render(number, body, plan, tags, older=()):
> 589-    """The issue body for a plan, in the format dokima.plan reads, with the owner's part kept below the marker."""
> 590-    return issue_body.redraw(body, plan_text(number, 

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q -p no:cacheprovider tests/test_checks.py 2>&1 | tail -3; grep -n "^OWNER\|^N =\|def workflow" -A3 tests/test_start.py | head -20
rm -rf /tmp/m && mkdir /tmp/m && git archive HEAD | tar -x -C /tmp/m
cd /tmp/m; f=.github/workflows/full-suite.yml
for mut in 's/if: "!github.event.pull_request.draft"/if: "!github.event.pull_request.draft \&\& github.actor != '"'"'RezaSoleymanifar'"'"'"/' \
  's/if: "!github.event.pull_request.draft"/if: "!github.event.pull_request.draft \&\& github.event.sender.type == '"'"'Bot'"'"'"/' \
  's/types: \[opened, synchronize, reopened, ready_for_review\]/types: [opened, reopened, ready_for_review]/' \
  's/if: "!github.event.pull_request.draft"/if: "!github.event.pull_request.draft \&\& github.actor == '"'"'nobody'"'"'"/' ; do
  git -C /tmp/m checkout -q -- 2>/dev/null; cp /home/runner/work/dokima/dokima/$f $f; sed -i "$mut" $f; grep -n "if:\|types:" $f
  python -m pytest -q -p no:cacheprovider tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request 2>&1 | grep -E "716|passed|failed" | head -3; done
```

> ...                                                                      [100%]
> 3 passed in 0.18s
> 31:OWNER = "owner-person"
> 32:N = "57"
> 33-PR = "60"
> 34-SPLIT = {"kind": "feature", "feature": "Stuck issues get unstuck.", "stories": [
> 35-    {"title": "First", "user_story": "u1", "acceptance_criteria": [{"text": "a", "source": "https://github.com/o/r/issues/57"}],
> --
> 364:def workflow(name):
> 365-    """One of this repo's workflows, read."""
> 366-    return load_yaml(open(os.path.join(ROOT, ".github", "workflows", name)).read())
> 367-
> 8:    types: [opened, synchronize, reopened, ready_for_review]
> 17:    if: "!github.event.pull_request.draft && github.actor != 'RezaSoleymanifar'"
> 1 passed in 0.17s
> 8:    types: [opened, synchronize, reopened, ready_for_review]
> 17:    if: "!github.event.pull_request.draft && github.event.sender.type == 'Bot'"
>         Proves 29.4, 539.3 and 716.1. Reads full-suite.yml and checks it still installs only pytest and pytest-xdist,
>         For 716.1 it plays GitHub's part on a new push to a ready Dokima pull request, once by Dokima's bot and once by
>         record_property("proves", "716.1")
> 8:    types: [opened, reopened, ready_for_review]
> 17:    if: "!github.event.pull_request.draft"
>         Proves 29.4, 539.3 and 716.1. Reads full-suite.yml and checks it still installs only pytest and pytest-xdist,
>         For 716.1 it plays GitHub's part on a new push to a ready Dokima pull request, once by Dokima's bot and once by
>         record_property("proves", "716.

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "RezaSoleymanifar\|OWNER\b\|owner_login\|repository_owner" dokima .github | head -15
```

> dokima/agent_autopilot.py:550:        sorted(repo_approvers(os.environ.get("GITHUB_REPOSITORY_OWNER", repo.split("/")[0])))
> dokima/audit.py:3:    python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number") and .github/CODEOWNERS where it runs
> dokima/audit.py:328:        print("usage: python3 -m dokima.audit OWNER/REPO", file=sys.stderr)
> dokima/plan.py:209:        print(",".join(sorted(repo_approvers(os.environ["GITHUB_REPOSITORY_OWNER"]))))
> dokima/app.json:4:  "url": "https://github.com/RezaSoleymanifar/dokima",
> dokima/app.json:6:    "url": "https://github.com/RezaSoleymanifar/dokima",
> dokima/roles/planner.md:190:   "acceptance_criteria": [{"text": "...", "words": "the owner's exact words this delivers", "source": "https://github.com/OWNER/REPO/issues/N or #issuecomment-...",
> .github/CODEOWNERS:2:* @RezaSoleymanifar
> .github/workflows/wiki.yml:27:            git commit -m "Sync from ${GITHUB_SHA::7}" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"
> .github/workflows/agent.yml:394:            git diff --cached --quiet || git commit -qm "$ROLE for #$N (run ${{ github.run_id }})" --trailer "Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>"

**Agent:** Still reviewing the plan for [#716](https://github.com/dokima-dev/dokima/issues/716) (owner's pushes run all tests). I'm checking whether its test catches a rule that skips the owner.

`6. Bash`
```
cd /tmp/m; f=.github/workflows/full-suite.yml; cp /home/runner/work/dokima/dokima/$f $f; sed -i 's/if: "!github.event.pull_request.draft"/if: "!github.event.pull_request.draft \&\& github.actor != github.repository_owner"/' $f; grep -n "if:" $f; python -m pytest -q -p no:cacheprovider tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request 2>&1 | tail -1
cp /home/runner/work/dokima/dokima/$f $f; sed -i 's/pip install -q pytest pytest-xdist/pip install -q pytest pytest-xdist rich/' $f; python -m pytest -q -p no:cacheprovider tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request 2>&1 | grep -E "^E.*(539|716)" | head -2; cd /; rm -rf /tmp/m
```

> 17:    if: "!github.event.pull_request.draft && github.actor != github.repository_owner"
> 1 passed in 0.05s
> E       AssertionError: 539.3: the merge gate no longer installs exactly pytest and pytest-xdist
> Shell cwd was reset to /home/runner/work/dokima/dokima

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote one criterion: the owner's push to a Dokima pull request runs all tests.",
          "The planner extended the older merge gate check to play a push by the bot and by the owner."],
  "decided": ["The planner reused an older check, since the plan check rejects a new test that passes today."],
  "open": ["The planner proposed an issue: a behavior already true cannot get its own new test."]},
 "verdict": "block",
 "summary": "The check misses a rule that skips the owner by their real name, so it does not yet pin the promise.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "716.1 weak test",
   "text": "The check for 716.1 plays the owner as a made-up name, so a rule skipping the real owner still passes. Smallest fix: play the owner as the login in `.github/CODEOWNERS`, and set the repository owner in the played event.",
   "evidence": "Adding `github.actor != github.repository_owner` or the owner's login to the job's `if:` in a copy: test still passes."}
 ],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "Confirmed: the plan check fails any new test that passes today, so a pin must reuse an older check."}
 ],
 "asks": [
  {"ask": "A push by the owner to a Dokima pull request runs all tests, with no rule skipping the owner.",
   "source": "https://github.com/dokima-dev/dokima/issues/716", "criterion": "716.1"}
 ],
 "behaviors": [
  {"criterion": "716.1", "one_behavior": true, "why": "One push by the owner, one result: all tests run."}
 ],
 "edge_cases": [
  {"criterion": "716.1", "cut": [], "missing": ["A rule that skips the owner by their real login or as repository owner."]}
 ],
 "tests": [
  {"test": "tests/test_checks.py::test_full_suite_runs_every_test_on_every_pull_request", "only_its_behavior": false,
   "why": "It also checks 29.4 and 539.3; forced by the plan check, raised as P1."}
 ],
 "size": "ok"
}
EOF
cd /home/runner/
```

> Exit code 1
> summary holds 21 words, over its cap of 20 (up to 24 passes)
> raise 1's text holds 39 words, over its cap of 30: cut 9, keep the facts
> previous_step did line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step did line 2 holds 19 words, over its cap of 15: cut 4, keep the facts
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`8. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d["previous_step"]["did"]=["The planner wrote one criterion: the owner's push runs all tests.",
 "The planner extended the older merge gate check to play bot and owner pushes."]
d["previous_step"]["decided"]=["The planner reused an older check, since new tests passing today are rejected."]
d["summary"]="The check misses a rule skipping the owner by real name, so it does not pin the promise."
d["raises"][0]["text"]="The 716.1 check plays the owner as a made-up name, so a rule skipping the real owner passes. Fix: play the `.github/CODEOWNERS` login and set the repository owner."
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 716 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`9. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom" dokima/agent*.py | head -20; grep -i "pin\|passes today\|passing" /tmp/pack/open_issues.json | head
```

> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/agent_autopilot.py:180:        if decided.get(raises.VERDICT) == "symptom" and raises.is_numbers([cause]):
> dokima/agent_autopilot.py:181:            # A symptom joins its cause as a comment, and files no issue (#623).
> dokima/agent_autopilot.py:188:            lines.append(f"- {card.ref(os.environ.get('GITHUB_REPOSITORY', ''), cause)} · a symptom, added as a comment")
> dokima/agent_autopilot.py:190:        symptoms = decided.get(raises.SYMPTOMS)
> dokima/agent_autopilot.py:191:        if decided.get(raises.VERDICT) == "root cause" and raises.is_numbers(symptoms) and symptoms:
> dokima/agent_autopilot.py:192:            # A root cause files one issue marked as such, naming each symptom so GitHub links both ways (#623).
> dokima/agent_autopilot.py:194:            body += ["", "**Symptoms:** " + ", ".join(f"#{n}" for n in symptoms)]
> dokima/agent_autopilot.py:198:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]
> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
>   "summary": "Pins that the

`10. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 14,60p dokima/agent_checks.py; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'));print(len(d))
for i in d:
  s=(i['title']+' '+i['summary']).lower()
  if any(w in s for w in ['new test','already true','pin','fail today','fails today','passes today']): print(i['number'],i['title'])"
```

> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(open(path)) if os.path.exists(path) else []
>     theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
>               and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
>     confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
>                  and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
>     filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
>     if not filed:
>         return []
>     bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
>     named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
>              for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numbers([d.get(f)]))]
>     if not named:

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'))
for i in d:
  if i['number'] in (707,458,207): print(i['number'],i['summary'])"; grep -n "SEARCHED\s*=\|VERDICT\s*=\|CAUSE\s*=" dokima/raises.py
```

> 707 Tests the owner writes stay exactly as written, and every new test explains itself in one shape.
> 458 Twice on 10-10 (#302, #417) a planner's new test file loaded fine in All tests but not in each criterion's own check, which runs the file on its own: "No module named dokima".
> 207 <!-- dokima-card --> ### Plan: add `work` to start **Objective: the re-plan check judges every new test on main correctly, including tests that use git** <dl><dd> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.sv
> 23:SEARCHED = "searched"
> 25:VERDICT = "verdict"
> 28:CAUSE = "cause"

**Agent:** No open issue covers the planner's proposal, so I'm marking it as new and re-running the check.

`12. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
p='review.json'; d=json.load(open(p))
d["answers"][0].update({"searched":[707,458,207],"verdict":"new"})
json.dump(d,open(p,'w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 716 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#716](https://github.com/dokima-dev/dokima/issues/716) (owner's pushes run all tests). The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What the planner did:** they wrote one criterion: a push by the owner to a Dokima pull request runs all tests. They had to prove it by extending the older check `test_full_suite_runs_every_test_on_every_pull_request`, because the plan check rejects any new test that already passes. The extended check acts out a push by the bot and a push by the owner, and both must run all tests.

**Why I blocked:** the check uses a made-up name for the owner (`owner-person`). I tried each change below on a scratch copy of the merge gate's job:
- Skipping pushes by the owner's real login: the check still passes.
- Skipping pushes by the repository owner: the check still passes.
- Running only for bots: the check fails, as it should.
- Dropping the "new push" trigger: the check fails, as it should.

So the check does not yet prove "no rule skipping the owner". The smallest fix, sent to the planner: act out the owner as the login in `.github/CODEOWNERS`, and set the repository owner in the acted-out push.

**Also noted, not a blocker:**
- The planner proposed a new issue: something already true cannot get its own new test, because the plan check rejects any new test that passes today. I confirmed that. I searched [#707](https://github.com/dokima-dev/dokima/issues/707) (the owner's tests stay as written), [#458](https://github.com/dokima-dev/dokima/issues/458) (the plan check runs tests like their own check) and [#207](https://github.com/dokima-dev/dokima/issues/207) (the re-plan check and tests that use git). None covers it, so I marked it new. It stays a proposal until you file it.
- Because of that, the check for this criterion also checks two older promises (29.4 and 539.3). If either of those breaks, this criterion's check goes red too. I marked the test as not checking only its own promise. The planner can't fix that until the plan check changes, so I didn't block on it.

The plan keeps your one ask, as a single promise.

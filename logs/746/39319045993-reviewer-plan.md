# reviewer (plan) for #746

Run: https://github.com/dokima-dev/dokima/actions/runs/39319045993

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 104
> drwxr-xr-x  3 runner runner  4096 Oct 19 20:24 .
> drwxrwxrwt 18 root   root    4096 Oct 19 20:25 ..
> drwxr-xr-x  2 runner runner  4096 Oct 19 20:24 in
> -rw-r--r--  1 runner runner  7874 Oct 19 20:24 issue.md
> -rw-r--r--  1 runner runner     2 Oct 19 20:24 open_blockers.json
> -rw-r--r--  1 runner runner 65723 Oct 19 20:24 open_issues.json
> -rw-r--r--  1 runner runner  2660 Oct 19 20:24 owner_words.json
> -rw-r--r--  1 runner runner    16 Oct 19 20:24 parent.json
> -rw-r--r--  1 runner runner  3093 Oct 19 20:24 plan.json
> 
> in:
> total 12
> drwxr-xr-x 2 runner runner 4096 Oct 19 20:24 .
> drwxr-xr-x 3 runner runner 4096 Oct 19 20:24 ..
> -rw-r--r-- 1 runner runner 3831 Oct 19 20:24 01-planner.json
> # Issue #746: Trial: run Dokima end to end on the owner's job-hunt repo
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 620, 680, 706, 721, 741, 742, 744, 745, 816, 867 -->
> <!-- dokima-blocking: {"blocked_by": [620, 680, 706, 721, 741, 742, 744, 745, 867], "blocks": [258, 309, 747, 748], "loop": []} -->
> **Backlog**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/620
> - https://github.com/dokima-dev/dokima/issues/680
> - https://github.com/dokima-dev/dokima/issues/706
> - https://github.com/dokima-dev/dokima/issues/721
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://git

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/owner_words.json /tmp/pack/parent.json; cat /tmp/pack/in/01-planner.json | head -c 2000; echo; git show --stat HEAD; cat tests/test_upstream_private_code.py
```

> {
>  "https://github.com/dokima-dev/dokima/issues/746": "Phase 4 of #272. The first real run of Dokima on a repo that is not Dokima: the owner's own private job-hunt repo, RezaSoleymanifar/job-hunt (owner, 2026-10-17: \"run this trial on my job-hunt repo ... instead of a copy of Vintage\").\n\n**Setup**\n- job-hunt: Python and Node (Playwright), tests in tests/, no CI workflow, an AGENTS.md, no CODEOWNERS. It lives on the owner's account, not the dokima-dev org.\n- Onboard it through the thin workflow install only. Count every manual step; the target is two (install the App on the repo, add its key).\n- The install must cope with no CI and no CODEOWNERS.\n\n**Trial issues** (drafts from job-hunt's own TODO; owner writes the final wording)\n1. Small: a health floor rule for quiet job sources.\n2. Medium: fix judge score compression (16 of 21 verdicts were 7).\n3. Large: smarter crawl that stops rescanning every source.\n\n**Pass**\n- All 3 merged with zero manual fixes after onboarding.\n- Tests that hit the network stay off the merge gate through settings.\n- Every problem hit lands in dokima-dev/dokima by itself.\n- job-hunt stays private: nothing from it (resumes, profile, leads, companies, people, its code) appears in Dokima's public repo; a filed problem names only what Dokima did wrong.\n- The owner's only actions are approving plans and merges.\n\n**After the trial:** the nightly sandbox (#258) runs on a disposable copy, never on job-hunt itself.\n\n<!-- dokima-done -->\n

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_upstream_private_code.py 2>&1 | tail -30; grep -n "def scrub\|def _scrub\|scrub" dokima/upstream.py | head -30
```

> E         
> E         "weight = HIRING_SI...['acme-recruiting']" is contained here:
> E            such as `weight = HIRING_SIGNAL_WEIGHTS['acme-recruiting']` as a call.
> E           The worker misreads a dictionary lookup such as `weight = HIRING_SIGNAL_WEIGHTS['acme-recruiting']` as a call.
> E           
> E           **Evidence:** The worker's run quoted `weight = HIRING_SIGNAL_WEIGHTS['acme-recruiting']` as a function call.
> E           
> E           Dokima found this problem in its own work on a repo it runs on.)
> 
> /home/runner/work/dokima/dokima/tests/test_upstream_private_code.py:77: AssertionError
> =========================== short test summary info ============================
> FAILED tests/test_upstream_private_code.py::test_a_private_file_path_never_reaches_dokimas_repo - AssertionError: 746.1: Dokima's public repo shows a file path of the private repo: 'The card breaks when a plan names a deep file.\nThe card breaks when a plan names a deep file.\n\n**Evidence:** `src/leads_ranker.py` in the plan made `dokima/card.py` cut the fold.\n\nDokima found this problem in its own work on a repo it runs on.'
> assert ('src/leads_ranker.py' not in 'The card br... it runs on.'
>   
>   'src/leads_ranker.py' is contained here:
>     dence:** `src/leads_ranker.py` in the plan made `dokima/card.py` cut the fold.
>   ?           +++++++++++++++++++
>     
>     Dokima found this problem in its own work on a repo it runs on.)
> FAILED tests/test_upstream_private_code.py::test_a_line_of_the_private_code_never

`4. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 1,120p dokima/upstream.py; grep -n "def github\|chdir\|tmp_path\|def checked_and_filed\|def name_upstream" -A6 tests/test_upstream.py | head -60
```

> """Filing Dokima's own problems in the upstream repo the settings name, such as dokima-dev/dokima (#745).
> 
> A repo's `.dokima/settings.yaml` may name it as `upstream.repo`; empty, the default, keeps everything in the repo.
> Two things file there: a problem a review confirms and tags as Dokima's fault, and a failed run of a shared workflow:
> 
>     python3 -m dokima.upstream failed WORKFLOW JOB    files the failure of JOB in WORKFLOW.yml
>     python3 -m dokima.upstream failed WORKFLOW        files each job RESULTS names as failed, as `JOB=RESULT ...`
>     python3 -m dokima.upstream owner                  prints the upstream repo's owner, empty for none
> 
> A failed test check or review relay files nothing: its failure is usually the repo's own. A repeat, the same title
> already open upstream, is a comment on that issue, never a second one. Nothing filed names or links the repo it came
> from, not even its name, nor any of its issues by number. Calls on the upstream repo run with DOKIMA_UPSTREAM_TOKEN,
> which the workflow mints from the App's own key.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> import time
> import urllib.parse
> 
> from dokima import manifest, settings
> 
> # The workflows whose failures file nothing upstream: the two test checks and the review relay, which holds no key.
> NOT_FILED = ("full-suite", "acceptance-criteria", "reviews")
> 
> 
> def repo():
>     """The upstream repo the settings name, as OWNER/NAME; empty for none or this repo."""
>     got = str((settings.read(

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "def file_issues\|file_problem(" dokima/ | head; grep -n "exclude" dokima/settings.py | head -5; grep -rn "CODEOWNERS" dokima/plan.py | head -5
```

> dokima/upstream.py:95:def file_problem(up, title, text, evidence=None):
> dokima/agent_autopilot.py:187:def file_issues(repo, number, rec, recs):
> dokima/agent_autopilot.py:207:                n, again = upstream.file_problem(up, title, x.get("text") or title,
> 147:    The all-tests command leaves out each test on the exclude list; the per-criterion command must name {test}. An
> 150:    run_all = " ".join([str(tests["run_all"])] + [f"--deselect {shlex.quote(str(t))}" for t in tests.get("exclude") or []])
> dokima/plan.py:4:Approvers are the code owners in CODEOWNERS (the owners of `*`), or the repository owner when there is no such
> dokima/plan.py:17:    """The people whose approval counts: the owners of `*` in CODEOWNERS, else the repository owner."""
> dokima/plan.py:26:    path = os.path.join(root, ".github", "CODEOWNERS")

**Agent:** Both new tests fail today for the right reason. I'm writing the review now: the plan drops most of the owner's trial asks, so it blocks.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote two tests: filed problems must not show the private repo's file paths or code lines."],
  "decided": ["The plan carries only the privacy fix and leaves the rest of the trial out."],
  "open": ["The planner asks the owner three questions: privacy fix only, manual sign off, and an agent rule for names."]
 },
 "verdict": "block",
 "summary": "Both privacy tests are sound, but seven of the owner's trial asks have no criterion, not even a manual one.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "Trial asks dropped",
   "text": "Seven owner asks have no criterion: install only, two manual steps, no CI or CODEOWNERS, all three merged, network tests off the gate, problems filed by themselves, owner only approves. Add each as a criterion: a test where code already does it, or (manual) with a reason.",
   "evidence": "Issue body, Setup and Pass lists; `plan.json` holds only 746.1 and 746.2."},
  {"kind": "blocker", "to": "planner", "label": "Sandbox ask dropped",
   "text": "The owner says the nightly sandbox runs on a disposable copy, never on job-hunt. Add a criterion for it, or mark it not a requirement here because #258 carries it.",
   "evidence": "Issue body, After the trial line; no criterion or plan note covers it."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Onboard it through the thin workflow install only.", "source": "https://github.com/dokima-dev/dokima/issues/746", "criterion": "missing"},
  {"ask": "Count every manual step; the target is two (install the App on the repo, add its key).", "source": "https://github.com/dokima-dev/dokima/issues/746", "criterion": "missing"},
  {"ask": "The install must cope with no CI and no CODEOWNERS.", "source": "https://github.com/dokima-dev/dokima/issues/746", "criterion": "missing"},
  {"ask": "All 3 merged with zero manual fixes after onboarding.", "source": "https://github.com/dokima-dev/do
```

> Exit code 1
> raise 1's text holds 47 words, over its cap of 30: cut 17, keep the facts
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts
> previous_step open line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

`7. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['raises'][0]['text']="Seven owner asks have no criterion: setup, install, no CI or CODEOWNERS, three merges, network tests, self filing, owner only approves. Add each, tested or manual."
r['previous_step']['did']=["The planner wrote two tests: filed problems hide the private repo's paths and code."]
r['previous_step']['open']=["Three owner questions: privacy fix only, manual sign off, agent rule for names."]
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 746 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for issue [#746](https://github.com/dokima-dev/dokima/issues/746) (the job-hunt trial). The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What holds up**
- The plan has two criteria, both about privacy: a problem Dokima files in its public repo must not show the private repo's file paths (746.1) or lines of its code (746.2).
- I ran both new tests and both fail today for the right reason: the private path and code line do reach the public repo.
- The tests also check that Dokima's own file path and the problem's own words still get through, so a fix that deletes everything can't pass.

**Why it blocks**
- Seven of the owner's asks have no criterion, not even a hand-checked one:
  - onboard through the install only
  - count the manual steps, with two as the target
  - cope with no CI and no CODEOWNERS
  - all three trial issues merged with no manual fixes
  - network tests kept off the merge gate
  - problems filed in Dokima's repo by themselves
  - the owner only approves plans and merges
- The planner's own evidence says code already handles some of these (approvers when there's no CODEOWNERS, the setting that leaves tests out, upstream filing). Those need a test that pins them. The rest can be marked as checked by hand, with a reason.
- The line about the nightly sandbox running on a disposable copy is also dropped. It needs a criterion, or a note that [#258](https://github.com/dokima-dev/dokima/issues/258) (the nightly sandbox) covers it.

I left the planner's three questions for the owner, because nothing the owner has written settles them:
- carry only the privacy fix?
- sign off the live trial results by hand?
- is the agents' rule enough to keep companies, people and resume text out?

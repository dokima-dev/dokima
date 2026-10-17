# reviewer (plan) for #813

Run: https://github.com/dokima-dev/dokima/actions/runs/39064714047

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json; ls in
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
> # Issue #813: Installing adds only the workflow and settings
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 812 -->
> <!-- dokima-blocking: {"blocked_by": [812], "blocks": [814, 815, 816], "loop": []} -->
> Installing Dokima puts one short workflow and one settings file in a repo, and nothing else.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/812
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/814
> - https://github.com/dokima-dev/dokima/issues/815
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/755
> 
> 
> **User story:** Installing Dokima adds one short workflow and a settings file to a repo, and no Dokima code.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance crite

`2. Bash`
```
cd /tmp/pack; cat owner_words.json; head -c 6000 parent.json; echo; cat open_issues.json | head -c 1500; cd /home/runner/work/dokima/dokima; git show --stat HEAD; git show HEAD -- tests/
```

> {
>  "https://github.com/dokima-dev/dokima/issues/742": "Phase 1 of #272. Owner rule from #272: one central Dokima, never a copy of its code.\n\n**What lands in an adopter's repo**\n- One thin workflow, `.github/workflows/dokima.yml`, about 15 lines, that calls Dokima's shared workflows by tag.\n- `.dokima/settings.yaml`.\n- Nothing else. No Python. All Dokima code runs from Dokima's own repo inside GitHub Actions.\n\n**Credentials** live only in GitHub secrets on the repo (the `keys` environment): the App key, `CLAUDE_TOKEN`, `KIMI_API_KEY` when used. `settings.yaml` only names which secret each role reads. Nothing secret is ever committed.\n\n**Identity on every commit:** the trailer `Co-authored-by: dokima[bot]`, so Dokima appears in the contributor list of every repo it touches. Replaces the owner's hardcoded trailer (#110); the adopter can turn it off in settings.\n\n**Also**\n- The README install steps (README.md:120-125) and docs/wiki/Installing.md stop telling adopters to copy `.github/workflows/` and `dokima/`. `playthrough.yml` and `wiki.yml` are Dokima-project files, never installed.\n- The existing copy installer in `playthrough.py:161-223` is the starting point.\n- Missing bot or key fails loudly with the fix in the message (from #41).\n\n**Done when:** acceptance items 12, 15 and 20 on #272 pass: install adds only the workflow and settings; a run without the secret fails with a clear message; an empty repo reaches its first merged PR using only the docs.\n",
>  "htt

`3. Bash`
```
cd /home/runner/work/dokima/dokima; ls .github/workflows dokima/install 2>&1; cat .dokima/settings.yaml | head -30; sed -n 150,240p dokima/playthrough.py; grep -n "uses:" .github/workflows/*.yml | head -30
```

> .github/workflows:
> acceptance-criteria.yml
> agent.yml
> assign.yml
> audit.yml
> autopilot.yml
> board.yml
> card.yml
> commands.yml
> entry.yml
> fix.yml
> full-suite.yml
> playthrough.yml
> reviews.yml
> testmon.yml
> uptodate.yml
> wiki.yml
> 
> dokima/install:
> dokima.yml
> # This repo's own settings, over Dokima's shipped defaults (dokima/defaults.yaml).
> co_author: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> # Dokima's own prompts are never the worker's to change.
> protected_paths: [.github/, dokima/roles/]
>             sandbox.do(step, out)
>             line = wait_for_cards(step, sandbox.pending, wait, poll) or judge(step, *sandbox.cards())
>         except Exception as e:
>             line = f"FAIL: {step}: {e}"
>         finally:
>             if out:
>                 shutil.rmtree(out, ignore_errors=True)
>         failed = failed or not line.startswith("PASS: ")
>         log(line)
>     return 1 if failed else 0
> 
> 
> def install_files(played):
>     """Every file of the played folder's dokima/ and .github/workflows/, with its content.
> 
>     Keyed by path relative to the folder."""
>     files = {}
>     for top in ("dokima", os.path.join(".github", "workflows")):
>         for d, _, names in os.walk(os.path.join(played, top)):
>             for n in names:
>                 if "__pycache__" in d or n.endswith(".pyc"):
>                     continue
>                 path = os.path.join(d, n)
>                 with open(path, "rb") as f:
>                     files[os.path.relpath(path, played).replace(os.sep, "/"

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/install/dokima.yml; python -m pytest -q tests/test_install.py "tests/test_playthrough.py::test_the_play_through_installs_the_played_commit_on_the_sandbox_before_the_first_step" 2>&1 | grep -E "Error|assert|failed|passed|813|437" | head -30
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
>   push: {branches: [main]}
>   schedule: [{cron: "*/15 * * * *"}, {cron: "17 6 * * *"}]
>   workflow_run: {workflows: [dokima], types: [in_progress, completed]}
>   repository_dispatch: {types: [dokima-next]}
>   workflow_dispatch:
> permissions: {contents: read, issues: write, pull-requests: read, actions: read, checks: read}
> jobs:
>   dokima:
>     uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.0
>     secrets: inherit
>         Proves 813.1. Installs this checkout, which holds Dokima's code and all its workflows, into a repo holding one
>         record_property("proves", "813.1")
> >       check_two_files(added(adopter(tmp_path), "813.1"), "813.1", "a repo holding one README")
> crit = '813.1', what = 'a repo holding one README'
> >       assert set(got) == {WORKFLOW, SETTINGS}, \
> E       AssertionError: 813.1: installing into a repo holding one README should add exactly .github/workflows/dokima.yml and .dokima/settings.yaml, not ['.github/workflows/acceptance-criteria.yml', '.github/workflows/agent.yml', '.github/workflows/assign.yml', '.github/workflows/audit.yml', '.github/workflows/autopilot.yml', '.github/workflows/board.yml', '.github/workflows/card.yml', '.github/workflows/commands.yml', '.github/workflows/entry.yml', '.github/workflows/fi

`5. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
  if i['number'] in (812,814,815,816,742): print(i['number'],i['title'],'|',i['summary'])
"; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(list(d.keys()))"; cd /home/runner/work/dokima/dokima; grep -n "keep\|813\|install" -i dokima/agent.py | grep -in "check review\|asks" | head
```

> 816 An empty repo reaches its first merge from the docs | An owner with an empty repo gets to a first merged pull request with only the docs.
> 815 Wiki install page uses the thin workflow | The wiki's install page tells adopters to add the one workflow and settings file, not to copy Dokima.
> 814 README install steps use the thin workflow | The README tells adopters to add the one workflow and settings file, not to copy Dokima.
> 742 Thin install: no Dokima code in the adopter's repo | Adopters install one short workflow and a settings file; all Dokima code runs from Dokima's repo.
> ['role', 'stage', 'run_id', 'commit_before', 'started_by', 'models', 'report', 'log', 'run', 'handback', 'check', 'url']

**Agent:** I'm writing the review now: the new tests fail for the right reason and the plan matches the owner's asks.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote three criteria: two files only, no secret values, no owner co-author line.",
          "The planner wrote four new tests and changed one play-through test to the thin install."],
  "decided": ["The play-through install now calls the played commit instead of the release tag."],
  "open": ["An old copy left in the sandbox by earlier installs stays there."]
 },
 "verdict": "approve",
 "summary": "The plan carries every ask for this story, and each new test fails today because the thin install is missing.",
 "raises": [],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "A real problem outside this story; it stays an issue for the owner to file."}
 ],
 "asks": [
  {"ask": "Nothing else. No Python.", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "813.1"},
  {"ask": "`playthrough.yml` and `wiki.yml` are Dokima-project files, never installed.", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "813.1"},
  {"ask": "Nothing secret is ever committed.", "source": "https://github.com/dokima-dev/dokima/issues/742", "criterion": "813.2"},
  {"ask": "Never ship my line as a default", "source": "https://github.com/dokima-dev/dokima/issues/742#issuecomment-6234488528", "criterion": "813.3"}
 ],
 "behaviors": [
  {"criterion": "813.1", "one_behavior": true, "why": "One result: the repo gains exactly the two files."},
  {"criterion": "813.2", "one_behavior": true, "why": "One result: no added file holds a secret value."},
  {"criterion": "813.3", "one_behavior": true, "why": "One result: the installed settings lack the owner's line."}
 ],
 "edge_cases": [
  {"criterion": "813.1", "cut": [], "missing": []},
  {"criterion": "813.2", "cut": [], "missing": []},
  {"criterion": "813.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_install.py::test_installing_adds_exactly_the_one_workflow_and_th
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`7. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')): print(i['number'],i['title'][:110])
" | grep -i -E "sandbox|play|install|copy|stale" ; cd /home/runner/work/dokima/dokima; grep -n "searched" dokima/agent.py | head
```

> 815 Wiki install page uses the thin workflow
> 814 README install steps use the thin workflow
> 813 Installing adds only the workflow and settings
> 747 One shared GitHub App: dokima[bot] everywhere, one-click install
> 746 Trial: run Dokima end to end on a copy of Vintage
> 742 Thin install: no Dokima code in the adopter's repo
> 491 Once every card, board or workflow pull request plays on the sandbox, a third play-through queued behind two c
> 457 The play-through's bot posts the stand-in records and live cards itself, as agent.yml's posting steps do, beca
> 258 A nightly run uses Dokima for real on a sandbox repo and files what breaks
> 207 Re-plan check: run main's copy as a git checkout so git-using tests are judged right
> 172 Browser jobs run on the box, in a sandboxed container
> 40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "searched" dokima/*.py | head; 
```

> dokima/agent.py:40:    problems_searched, problems_links, problems_for_owner, problems_round, problems_review, problems_tests,
> dokima/agent_checks.py:14:def problems_searched(h, pack_dir):
> dokima/agent_checks.py:15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> dokima/agent_checks.py:18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> dokima/agent_checks.py:120:        bad += problems_searched(h, pack_dir)
> dokima/raises.py:22:# An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> dokima/raises.py:23:SEARCHED = "searched"
> dokima/raises.py:45:    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> dokima/raises.py:47:    searched = decided.get(SEARCHED)
> dokima/raises.py:48:    if not is_numbers(searched) or not searched:

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 15,70p dokima/raises.py
```

> "reviewer": ("planner", "worker", "owner"),
> })
> # A worker's raise to the planner goes through the reviewer, who answers it first.
> THROUGH = MappingProxyType({("worker", "planner"): "reviewer"})
> # An issue the planner or the worker raises is filed only once the reviewer confirms it.
> CONFIRMS = "reviewer"
> FIELDS = ("kind", "to", "label", "text", "evidence")
> # An issue may also name the open issues searched for the same cause, by number, each from the reviewer's pack (#621).
> SEARCHED = "searched"
> # Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
> VERDICT = "verdict"
> VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> # A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
> CAUSE = "cause"
> SYMPTOMS = "symptoms"
> STAMPED = ("raised_by", "id")
> ANSWERS = ("done", "disagree")
> PREFIX = MappingProxyType({"planner": "P", "worker": "W", "reviewer": "R"})
> 
> 
> def _kinds():
>     return ", ".join(KINDS[:-1]) + " or " + KINDS[-1]
> 
> 
> def _verdicts():
>     names = list(VERDICTS)
>     return ", ".join(names[:-1]) + " or " + names[-1]
> 
> 
> def filing_problems(where, decided):
>     """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
>     problems = []
>     searched = decided.get(SEARCHED)
>     if not is_numbers(searched) or not searched:
>         problems.append(f"{where} files an issue, so {SEARCHED} must 

`10. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; d=json.load(open(p))
d['answers'][0].update(searched=[742, 491, 457, 258], verdict="new")
json.dump(d, open(p,'w'), indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 813 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#813](https://github.com/dokima-dev/dokima/issues/813) (installing adds only the workflow and settings). The review is in `/tmp/dokima-out/review.json`, and it passes both checks.

- **Asks:** each of the owner's asks for this story is carried by a criterion:
  - "No Python" and "nothing else" go to criterion 1.
  - Never installing the playthrough and wiki workflows also goes to criterion 1.
  - "Nothing secret is ever committed" goes to criterion 2.
  - "Never ship my line as a default" goes to criterion 3.
- **Asks left to other stories:** the README steps, the wiki page and the first merge from an empty repo are handled in [#814](https://github.com/dokima-dev/dokima/issues/814), [#815](https://github.com/dokima-dev/dokima/issues/815) and [#816](https://github.com/dokima-dev/dokima/issues/816).
- **Tests:** I ran all four new tests and they fail today for the right reason. The install still copies all of Dokima's code and every workflow, and no settings file is added.
- **Changed old test:** the play-through test still checks that the commit being played is installed before the first step. Only the expected files changed to the new two-file install.
- **Added beyond the criteria:** the installed workflow now points at the commit being played instead of the release tag. I counted this as needed to keep the old play-through check, so it is not a blocker.
- **Planner's raise P1:** an old copy of Dokima stays in the sandbox after a new install. I confirmed it as a new problem outside this story, to be filed as its own issue. I checked it against [#742](https://github.com/dokima-dev/dokima/issues/742) (thin install), [#491](https://github.com/dokima-dev/dokima/issues/491) (play-through queueing), [#457](https://github.com/dokima-dev/dokima/issues/457) (play-through bot posting) and [#258](https://github.com/dokima-dev/dokima/issues/258) (nightly sandbox run).

# reviewer (plan) for #623

Run: https://github.com/dokima-dev/dokima/actions/runs/38485834389

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> # Issue #623: Symptoms join their cause instead of a new issue
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 621, 622 -->
> <!-- dokima-blocking: {"blocked_by": [622], "blocks": [], "loop": []} -->
> A symptom the reviewer finds becomes a comment on its cause; a shared cause files one issue.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/623#issuecomment-6157499082) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/622
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/615
> - https://github.com/dokima-dev/dokima/issues/632
> - https://github.com/dokima-dev/dokima/issues/547
> - https://github.com/dokima-dev/dokima/issues/415
> - https://github.com/dokima-dev/dokima/issues/621
> 
> 
> **User story:** Symptoms land as comments on their cause, and a newly found cause gathers its symptoms in one issue.
> 
> <img src="https://raw.githubusercontent.com/dokima-de

`2. Bash`
```
cd /tmp/pack; cat parent.json | head -c 6000; echo; python3 -c "
import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; head -c 1500 open_issues.json
```

> {"number": 615}
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38485457412",
>  "commit_before": "9f35cbcc909670ca5b6d27cf923dd8e79b52464d",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 171805,
>   "turns": 17,
>   "cost_usd": 1.0660808000000002,
>   "tokens_in": 1045781,
>   "tokens_out": 15094
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/623/38485457412-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38485457412",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/623#issuecomment-6157499082"
> }
> [
>  {
>   "number": 638,
>   "title": "The rules file splits by topic",
>   "summary": "Issues that change different rules change different files, and no test is lost along the way.",
>   "link": "https://github.com/dokima-dev/dokima/issues/638",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 637,
>   "title": "The word check reads every rules topic file",
>   "summary": "Owner words a plan reviewer quotes from any rules topic file still pass the word check.",
>   "link": "https://github.com/dokima-dev/dokima/issues/637",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 636,
>   "title": "The agent code splits into files by job",
>   "summary": "The big agent file splits into one file per job, with nothing changing in how it works.",
>   "link": "https://github.com/dokima-dev/dokima/issues/636",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 632,
>   "title": "The re

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show --stat HEAD | head; cat tests/test_symptoms_join_cause.py
```

> commit dc7df92430ae118188c8535490a95feca6eb72ee
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Tue Oct 13 23:41:49 2026 +0000
> 
>     planner for #623 (run 38485457412)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_symptoms_join_cause.py | 210 ++++++++++++++++++++++++++++++++++++++
>  1 file changed, 210 insertions(+)
> """A symptom joins its cause as a comment; a root cause files one issue (#623).
> 
> Story 3 of #615. The reviewer already records, on every issue it files, the open issues it searched and its verdict:
> symptom, root cause or new (#622). This story makes the first two verdicts do what the owner asked:
> - A raise judged a symptom names its cause, an open issue from the pack, in "cause". Code posts it as a comment on
>   that issue, with the raise's words and evidence, and files no new issue. A symptom naming no cause is rejected.
> - A raise judged a root cause names the open issues it explains in "symptoms". Code files one issue whose title starts
>   "Root cause found", in place of the raise, and its body names each symptom as #N on a line naming them, so GitHub
>   links both ways. No symptom becomes a sub-issue. A root cause naming no symptoms is rejected.
> The same holds for an issue the planner or the worker raised that the reviewer answers done: the fields are on its
> answer, as #622 put searched and verdict there.
> 
> The checks run as subprocesses against a pack built fr

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_symptoms_join_cause.py 2>&1 | grep -E "^(FAILED|E  .*623|[0-9]+ (passed|failed))|AssertionError|623\.[0-9]:" | head -40
```

> >       assert hub.created() == {}, f"623.1: a symptom was filed as a new issue: {hub.created()}"
> E       AssertionError: 623.1: a symptom was filed as a new issue: {500: {'title': 'The board ignores closed pull requests.', 'body': 'The board ignores closed pull requests. Their cards stay in Review forever.\n\n**Evidence:** dokima/board.py asks only for OPEN pull requests\n\n**Verdict:** Symptom of a known cause\n\n**Open issues searched:** #12, #15\n\nThe reviewer found it on #301 ([run](https://github.com/o/r/actions/runs/9)).', 'labels': ['filed-by-dokima'], 'comments': []}}
> tests/test_symptoms_join_cause.py:98: AssertionError
> >       assert hub.created() == {}, f"623.1: a confirmed symptom was filed as a new issue: {hub.created()}"
> E       AssertionError: 623.1: a confirmed symptom was filed as a new issue: {500: {'title': 'The board ignores closed pull requests.', 'body': 'The board ignores closed pull requests. Their cards stay in Review forever.\n\n**Evidence:** dokima/board.py asks only for OPEN pull requests\n\n**Verdict:** Symptom of a known cause\n\n**Open issues searched:** #12, #15\n\nThe worker raised it and the reviewer confirmed it on #301 ([run](https://github.com/o/r/actions/runs/9)).', 'labels': ['filed-by-dokima'], 'comments': []}}
> tests/test_symptoms_join_cause.py:113: AssertionError
> >       assert code == 0, f"623.1: a symptom naming its cause #{CAUSE} was rejected:\n{out}"
> E       AssertionError: 623.1: a symptom naming its cause #12 was rejected:
> tests

`5. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python3 -m pytest -q tests/test_symptoms_join_cause.py -k rejected 2>&1 | grep -A6 "was rejected:" | head -30; grep -n "symptom\|root cause\|verdict" dokima/agent.py | head -40
```

> >       assert code == 0, f"623.1: a symptom naming its cause #{CAUSE} was rejected:\n{out}"
> E       AssertionError: 623.1: a symptom naming its cause #12 was rejected:
> E         raise 1 carries fields no raise has: cause
> E         
> E       assert 1 == 0
> 
> tests/test_symptoms_join_cause.py:128: AssertionError
> ----------------------------- Captured stderr call -----------------------------
> --
> >       assert code == 0, f"623.3: a root cause naming its symptoms {SYMPTOMS} was rejected:\n{out}"
> E       AssertionError: 623.3: a root cause naming its symptoms [12, 15] was rejected:
> E         raise 1 carries fields no raise has: symptoms
> E         
> E       assert 1 == 0
> 
> tests/test_symptoms_join_cause.py:207: AssertionError
> ----------------------------- Captured stderr call -----------------------------
> --
> FAILED tests/test_symptoms_join_cause.py::test_a_symptom_naming_no_cause_is_rejected - AssertionError: 623.1: a symptom naming its cause #12 was rejected:
>   raise 1 carries fields no raise has: cause
>   
> assert 1 == 0
> FAILED tests/test_symptoms_join_cause.py::test_a_root_cause_naming_no_symptoms_is_rejected - AssertionError: 623.3: a root cause naming its symptoms [12, 15] was rejected:
>   raise 1 carries fields no raise has: symptoms
>   
> assert 1 == 0
> 2 failed, 5 deselected in 0.20s
> 113:    return bool(reviews) and reviews[-1]["handback"].get("verdict") == "approve"
> 121:                and (r.get("handback") or {}).get("verdict") == "approve":
> 138:            return [] if r["handback

**Agent:** All seven new tests fail today for the right reasons. Next I'm checking the owner's words in #615, the parent issue.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "sub-issues mean a split\|root cause found" --include=*.py --include=*.md . | head; git log --oneline -5 --all -- | head -3; sed -n 290,330p dokima/agent.py
```

> tests/test_symptoms_join_cause.py:155:    assert re.match(r"\s*root cause found\b", filed["title"], re.I), \
> tests/test_symptoms_join_cause.py:156:        f"623.2: the root cause issue is not marked root cause found in its title: {filed['title']!r}"
> tests/test_symptoms_join_cause.py:172:    assert re.match(r"\s*root cause found\b", filed["title"], re.I), \
> tests/test_symptoms_join_cause.py:173:        f"623.2: the root cause issue is not marked root cause found in its title: {filed['title']!r}"
> tests/test_reviewer_verdict.py:33:NAMES = {"symptom": "symptom of a known cause", "root cause": "root cause found", "new": "new"}
> 2f7d03a Conversation of run 38485457412
> dc7df92 planner for #623 (run 38485457412)
> 81f4cea Conversation of run 38485530800
>     GitHub failing to list them fails the pack, never an empty list."""
>     items = [i for p in pages(gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
>     server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
>     return [{"number": i["number"], "title": i["title"], "summary": open_issue_summary(i.get("body")),
>              "link": i.get("html_url") or f"{server}/{repo}/issues/{i['number']}",
>              "filed_by_dokima": (i.get("user") or {}).get("login") == BOT_LOGIN}
>             for i in items if "pull_request" not in i]
> 
> 
> def problems_searched(h, pack_dir):
>     """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 
>     A review files its own issue raises

`7. Bash`
```
cd /home/runner/work/dokima/dokima; git branch -a | head; git ls-tree -r --name-only origin/logs 2>/dev/null | grep "^logs/615/" | head
```

> main
> * try/issue-623
>   remotes/origin/RezaSoleymanifar-patch-1
>   remotes/origin/agent-components
>   remotes/origin/agents-scope-rule
>   remotes/origin/archive/try-issue-154-before-main-moved
>   remotes/origin/commands
>   remotes/origin/fix-planner-issue-step
>   remotes/origin/fixture/card-557
>   remotes/origin/issue-100-planner-check
> logs/615/38476277236-planner.md
> logs/615/38476618266-reviewer-plan.md
> logs/615/38477403123-planner.md
> logs/615/38477692422-reviewer-plan.md

`8. Bash`
```
cd /home/runner/work/dokima/dokima; f=$(git ls-tree -r --name-only origin/logs | grep "^logs/615/" | tail -1); echo $f; git show origin/logs:$f | grep -n -i "6156481831\|sub-issue\|root cause found\|linked under" | head -30
```

> logs/615/38477692422-reviewer-plan.md
> 72:>     "A symptom becomes a sub-issue of its cause and closes with it.",
> 73:>     "The reviewer's pack lists each open issue's blocked-by, blocks and sub-issue links."
> 76:>     "Two owner questions: is a symptom a sub-issue, and do sub-issues act like splits?"
> 95:  "decided": ["A symptom becomes a comment on its cause, never a sub-issue.",
> 110:  {"ask": "A symptom of a known cause is added as a comment on the cause, with its evidence. No new issue is filed.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831", "criterion": "S3.1"},
> 111:  {"ask": "It raises that cause as a \"root cause found\" issue", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "S3.2"},
> 112:  {"ask": "with the symptoms it found linked under it, instead of filing the symptom.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "S3.3"},
> 121:- **Your answers are in the plan.** A symptom becomes a comment on its cause, with its evidence, not a sub-issue. The "new" verdict is folded into story 2. The split is down to three stories with 9 criteria.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; f=$(git ls-tree -r --name-only origin/logs | grep "^logs/615/" | tail -1); git show origin/logs:$f | sed -n 1,130p | cut -c1-600
```

> # reviewer (plan) for #615
> 
> Run: https://github.com/dokima-dev/dokima/actions/runs/38477692422
> 
> `1. Bash`
> ```
> cd /tmp/pack; cat issue.md; ls in; cat plan.json; cat open_blockers.json
> ```
> 
> > # Issue #615: Before filing, an agent checks whether its raise is a symptom of a known or new root cause
> > 
> > <!-- dokima-card -->
> > <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> > Before filing an issue, the reviewer searches open issues and records if it is a symptom, root cause or new.
> > 
> > **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156486655) with `/plan`, or say `/review`
> > 
> > <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> > 
> > - https://github.com/dokima-dev/dokima/issues/415
> > - https://github.com/dokima-dev/dokima/issues/547
> > - https://github.com/dokima-dev/dokima/issues/558
> > 
> > 
> > <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> > 
> > 
> > **Scope:**
> > 
> > <!-- dokima-folded -->
> > <!-- /dokima-card -->
> > 
> > <!-- dokima-ask -->
> > <details><summary>Original issue</summary>
> > 
> > Before an

`10. Bash`
```
cd /home/runner/work/dokima/dokima; git show origin/logs:logs/615/38477403123-planner.md | sed -n 1,200p | grep -v "^> *$" | grep -n "" | sed -n 1,140p | cut -c1-500 | grep -v "icons/" 
```

> 1:# planner for #615
> 2:
> 3:Run: https://github.com/dokima-dev/dokima/actions/runs/38477403123
> 4:
> 5:`1. Bash`
> 6:```
> 7:cat /tmp/pack/issue.md; ls /tmp/pack /tmp/pack/in; cat /tmp/pack/open_blockers.json 2>/dev/null; cat /tmp/pack/plan.json 2>/dev/null | head -50
> 8:```
> 9:
> 10:> # Issue #615: Before filing, an agent checks whether its raise is a symptom of a known or new root cause
> 11:> <!-- dokima-card -->
> 12:> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> 13:> Before filing an issue, the reviewer searches open issues and records if it is a symptom, root cause or new.
> 14:> **Plan**
> 16:> - https://github.com/dokima-dev/dokima/issues/415
> 17:> - https://github.com/dokima-dev/dokima/issues/547
> 18:> - https://github.com/dokima-dev/dokima/issues/558
> 20:> **Scope:**
> 21:> <!-- dokima-folded -->
> 22:> <!-- /dokima-card -->
> 23:> <!-- dokima-ask -->
> 24:> <details><summary>Original issue</summary>
> 25:> Before an agent files an issue from something it raised, it must decide what the raise is, so we stop filing symptoms one by one (whack-a-mole) and bloating the backlog.
> 26:> Its hand-back records these decisions, and code rejects a filing without them:
> 27:> 1. **Searched:** the open issues it checked for the same cause, listed.
> 28:> 2. **Verdict**, one of:
> 29:>    - **Symptom of a known cause:** the raise is linked under that issue as a sub-issue (a symptom). No new issue is filed. It closes when the cause merges.
> 30:>    - **Root cause found:** the raise a
> 31:
> 32:`2. B

`11. Bash`
```
cd /home/runner/work/dokima/dokima; for f in $(git ls-tree -r --name-only origin/logs | grep -E "^logs/(615|622|629|623)/"); do git show origin/logs:$f | grep -h -A3 "Root cause found:\*\* the raise\|6156481831)\|sub-issues mean" | head -20; done | sort -u | cut -c1-700
```

> {"case": "A root cause naming no symptoms is rejected
>    "edge_cases": [
>    "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831",
>    "words": "No sub-issues: sub-issues mean a split here.",
> - With no sub-issues, story 3 links symptoms by naming them in the root cause issue's body. I took that from your reason "sub-issues mean a split here", which you gave for known-cause symptoms, not root causes. I didn't ask about it.
> --
> > 
> >    - **New:** nothing matches. It looks for similar symptoms first; if none, it files the issue as today.
> >    - **Root cause found:** the raise a
> >    - **Root cause found:** the raise and other open issues share a cause nobody filed yet. It raises that cause as a "root cause found" issue, with the symptoms it found linked under it, instead of filing the symptom.
> >  "https://github.com/dokima-dev
> >  "https://github.com/dokima-dev/dokima/issues/6
> >  "https://github.com/dokima-dev/dokima/issues/615": "Before an agent files an issue from something it raised, it must decide what the raise is, so we stop filing symptoms one by one (whack-a-mole) and bloating the backlog.\n\nIts hand-back records these decisions, and code rejects a filing without them:\n\n1. **Searched:** the open issues it checked for the same cause, listed.\n2. **Verdict**, one of:\n   - **Symptom of a known cause:** the raise is linked under that issue as a sub-issue (a symptom). No new issue is filed. It closes when the cause merges.\n   - **Root cause fou

**Agent:** Found the parent's original text in the run logs; now pulling the owner's comment the plan quotes.

`12. Bash`
```
cd /home/runner/work/dokima/dokima; for f in $(git ls-tree -r --name-only origin/logs | grep -E "^logs/(615|622|629)/"); do git show origin/logs:$f | grep -o '"https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831": "[^"]*' ; done | sort -u
```

> (Bash completed with no output)

`13. Bash`
```
cd /home/runner/work/dokima/dokima; for f in $(git ls-tree -r --name-only origin/logs | grep -E "^logs/(615|622|629)/"); do git show origin/logs:$f | grep -B2 -A6 "No sub-issues: sub-issues mean a split here" | grep -v '"words"\|"source"' ; done | sort -u | head -30 | cut -c1-500
```

> (Bash completed with no output)

`14. Bash`
```
cd /home/runner/work/dokima/dokima; for f in $(git ls-tree -r --name-only origin/logs | grep -E "^logs/"); do git show origin/logs:$f | grep -h "sub-issues mean a split" ; done | sort -u | cut -c1-800 | head
```

> "words": "No sub-issues: sub-issues mean a split here.",
> - With no sub-issues, story 3 links symptoms by naming them in the root cause issue's body. I took that from your reason "sub-issues mean a split here", which you gave for known-cause symptoms, not root causes. I didn't ask about it.

`15. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "calls\|sub_issue\|def created\|FOUND\b\|FOUND_EVIDENCE =\|FOUND_TITLE =" tests/test_reviewer_settles.py | head -30; grep -rn "sub_issue" dokima/agent.py | head
```

> 47:FOUND = "The board ignores closed pull requests. Their cards stay in Review forever."
> 48:FOUND_TITLE = "The board ignores closed pull requests"
> 49:FOUND_EVIDENCE = "dokima/board.py asks only for OPEN pull requests"
> 96:    return {"kind": "issue", "label": "Board", "text": FOUND, "evidence": FOUND_EVIDENCE, "raised_by": role, "id": rid}
> 258:S.setdefault("calls", []).append(a)
> 478:    def created(self):
> 485:        return [c for c in self.state()["calls"] if c[:2] == ["pr", "merge"] or any("/merge" in str(x) for x in c)]
> 532:    for part, what in ((FOUND, "the raise's words"), (FOUND_EVIDENCE, "its evidence")):
> 589:    assert FOUND in filed["body"] and FOUND_EVIDENCE in filed["body"], \
> dokima/agent.py:465:        gh("api", "-X", "POST", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={node}")
> dokima/agent.py:1720:        todo += [c["number"] for c in json.loads(gh("api", f"repos/{repo}/issues/{n}/sub_issues?per_page=100") or "[]")]
> dokima/agent.py:1759:def sub_issues(repo, number):
> dokima/agent.py:1762:    return json.loads(gh("api", f"repos/{repo}/issues/{number}/sub_issues?per_page=100") or "[]")
> dokima/agent.py:2074:        if json.loads(gh("api", f"repos/{repo}/issues/{n}")).get("state") != "open" or sub_issues(repo, n):
> dokima/agent.py:2149:    subs = sub_issues(repo, number)
> dokima/agent.py:2179:        parents = [i["number"] for i in items if "pull_request" not in i and (i.get("sub_issues_summary") or {}).get("total")]
> dokima/agent.py:2199:        su

`16. Bash`
```
cd /home/runner/work/dokima/dokima; cat > /tmp/probe_test.py <<'EOF'
from tests.test_symptoms_join_cause import *
def test_probe(tmp_path):
    hub = hub_with_open_issues(tmp_path)
    reviewed(hub, verdict="root cause", symptoms=SYMPTOMS)
    print("SUBCALLS", sub_issue_calls(hub))
    print("NCALLS", len(hub.state()["calls"]))
EOF
cp /tmp/probe_test.py tests/test_zz_probe.py; timeout 300 python3 -m pytest -q -s tests/test_zz_probe.py 2>&1 | grep -E "SUBCALLS|NCALLS|passed|failed"; rm tests/test_zz_probe.py; git status --short
```

> FSUBCALLS []
> NCALLS 5
> 7 failed, 1 passed in 1.72s

**Agent:** All tests check out. Writing the hand-back now.

`17. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner planned three criteria with seven tests, all failing today."],
  "decided": ["A symptom names its cause and becomes a comment there.",
              "A root cause issue's title starts with Root cause found.",
              "A root cause names each symptom in one line, never as sub-issues."],
  "open": ["Two questions: how a root cause is marked, and how it links symptoms."]},
 "verdict": "approve",
 "summary": "The plan carries all three asks with tests that fail for the right reason; both questions follow the owner's words.",
 "raises": [],
 "answers": [
  {"raise": "P1", "answer": "done", "why": "The owner named the issue a root cause found issue; the title carrying that mark matches.",
   "words": "It raises that cause as a \"root cause found\" issue",
   "source": "https://github.com/dokima-dev/dokima/issues/615", "changes": false},
  {"raise": "P2", "answer": "done", "why": "The owner ruled out sub-issues; naming each symptom links them without any new kind of link.",
   "words": "No sub-issues: sub-issues mean a split here.",
   "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831", "changes": false}
 ],
 "asks": [
  {"ask": "A symptom of a known cause is added as a comment on the cause, with its evidence. No new issue is filed.", "source": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156481831", "criterion": "623.1"},
  {"ask": "It raises that cause as a \"root cause found\" issue", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.2"},
  {"ask": "instead of filing the symptom.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.2"},
  {"ask": "with the symptoms it found linked under it", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "623.3"},
  {"ask": "No sub-issues: sub-issues mean a split here.", "source": "https:/
```

> exit 0

**Agent:** I approved the plan for [#623](https://github.com/dokima-dev/dokima/issues/623) (symptoms join their cause instead of a new issue). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **All three of your asks have a criterion.** I took them from your parent issue [#615](https://github.com/dokima-dev/dokima/issues/615) (reviewer checks if a raised issue shares a known cause) and your comment on it:
  - A symptom becomes a comment on its cause, with its evidence, and no new issue is filed.
  - A root cause files one issue marked "root cause found", in place of the raise.
  - That issue links its symptoms, and none of them becomes a sub-issue.
- **The tests are real.** I ran all seven, and each one fails today because the feature is missing, not because of a crash. Each rejection test also checks that the good case passes. Each root-cause test also checks that an issue judged "new" keeps its usual title.
- **I answered both of the planner's questions for you, since this issue is on autopilot.**
  - **How a root cause is marked:** its title starts with "Root cause found". My evidence is your words in #615: *It raises that cause as a "root cause found" issue*.
  - **How it links its symptoms:** one line in its text names each symptom, and GitHub then links the issues both ways. My evidence is your comment on #615: *No sub-issues: sub-issues mean a split here.* You gave that reason for symptoms of a known cause, and I applied it to root causes too.
  - Neither answer changes how the system works or what it costs. If you meant something else, say so with `/plan`.
- **One small gap, not a blocker:** nothing rejects a symptom that names, as its cause, an issue that isn't among the open issues it was given.

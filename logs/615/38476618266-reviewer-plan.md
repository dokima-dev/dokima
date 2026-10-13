# reviewer (plan) for #615

Run: https://github.com/dokima-dev/dokima/actions/runs/38476618266

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #615: Before filing, an agent checks whether its raise is a symptom of a known or new root cause
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Before filing an issue, the reviewer searches open issues and records if it is a symptom, root cause or new.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156313347) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/415
> - https://github.com/dokima-dev/dokima/issues/547
> - https://github.com/dokima-dev/dokima/issues/558
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
> Before an agent files an issue from something it raised, it must decide what the raise is, so we stop filing symptoms one by one (whack-a-mole) and bloating the backlog.
> 
> Its hand-back records these decisions, and code rejects a filing without them:
> 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; grep -rn "label" dokima/*.py | grep -i "raised\|filed\|dokima-raised\|from-review" | head; grep -n "def file_issues\|def file_raise\|/issue" dokima/*.py | head
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38476277236",
>  "commit_before": "a9701dcd1c18343e8c700132dc6cc7d5d53232bd",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 113295,
>   "turns": 15,
>   "cost_usd": 0.8505592000000001,
>   "tokens_in": 766608,
>   "tokens_out": 11806
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/615/38476277236-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38476277236",
>  "check": {
>   "passed": true,
>   "problems": []
>  },
>  "url": "https://github.com/dokima-dev/dokima/issues/615#issuecomment-6156313347"
> }
> dokima/agent.py:1804:                     "--label", FILED_LABEL).strip()
> dokima/board.py:87:            got = self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues/{number}/dependencies/{side}?per_page=100&page={page}")
> dokima/board.py:103:            got = self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues?state=open&per_page=100&page={page}")
> dokima/board.py:111:        nodes = self.q('query($o:String!,$r:String!,$h:String!){repository(owner:$o,name:$r){pullRequests(headRefName:$h,states:[OPEN],first:1){nodes{number}}}}', o=self.repo_owner, r=self.repo_name, h=f"try/issue-{number}")["repository"]["pullRequests"]["nodes"]
> dokima/board.py:121:        path = f"repos/{self.repo_owner}/{self.repo_name}/issues/{number}/labels"
> dokima/board.py:130:        return "closed" if self.rest("GET", f"repos/{self.repo_owner}/{self.repo_n

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "FILED_LABEL" dokima/*.py | head; sed -n 1770,1830p dokima/agent.py; grep -n "def start_waiting\|def close_if_done" -A15 dokima/agent.py | grep -n "sub_issue\|subIssues\|sub-issue" | head
```

> dokima/agent.py:1777:FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> dokima/agent.py:1804:                     "--label", FILED_LABEL).strip()
> def first_sentence(text):
>     """A raise's first sentence, on one line, as a filed issue's title."""
>     text = escape_line(text)
>     m = re.match(r"(.+?[.!?])(\s|$)", text)
>     return (m.group(1) if m else text)[:250]
> 
> 
> FILED_LABEL = "filed-by-dokima"  # every issue Dokima files itself carries it (#268)
> 
> 
> def file_issues(repo, number, rec, recs):
>     """File every issue raise a passed review confirms as its own GitHub issue.
> 
>     It confirms its own, and each the planner or the worker raised that it answers done; `recs` are the records
>     before it. Returns the record's lines naming each filed issue, or the finding and GitHub's reason when GitHub
>     refuses it; a refusal never stops the run."""
>     h = rec.get("handback") or {}
>     if rec.get("role") != "reviewer" or not (rec.get("check") or {}).get("passed"):
>         return []
>     found = [x for x in card.raises_of(h) if x.get("kind") == "issue"]
>     theirs = {x["id"]: x for x in open_raises(recs) if x.get("kind") == "issue" and raises.sent_to(x) == raises.CONFIRMS}
>     found += [theirs[a["raise"]] for a in card.answers_of(h)
>               if a.get("answer") == "done" and isinstance(a["raise"], str) and a["raise"] in theirs]
>     lines = []
>     for x in found:
>         title = first_sentence(x.get("text") or x.get("label") or "An issue found")
>    

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner proposed a split into five stories for the reviewer's search and verdict."],
  "decided": ["A symptom becomes a sub-issue of its cause, and closes when its cause closes as completed.",
              "The reviewer's pack lists each open issue's blocked-by, blocks and sub-issue links."],
  "open": ["Two questions for the owner: whether a symptom is a sub-issue, and whether sub-issues act like splits."]},
 "verdict": "block",
 "summary": "The plan reads the owner's \"links\" as issue relationships without asking, and never lists each issue's own link.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "S1.2: links misread",
   "text": "The owner asked for open issues \"with their titles, summaries and links\"; the plain reading is each issue's own link, which no criterion carries. The plan reads it as blocked-by, blocks and sub-issue links without asking. Smallest fix: S1.1 lists each issue's link, and a question asks whether relationship links are meant too.",
   "evidence": "Comment 6156300936; plan S1.1 lists only title and summary, S1.2 relationships."},
  {"kind": "blocker", "to": "planner", "label": "S1.1: all open issues",
   "text": "S1.1 promises every open issue, but its edge cases skip a repo with more than one page of open issues, which this repo hits in normal use. Smallest fix: add that edge case, every open issue listed.",
   "evidence": "`dokima/board.py:103` reads open issues 100 per page; this repo has over 600 issues."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Searched: the open issues it checked for the same cause, listed.", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "S2.1"},
  {"ask": "code rejects a filing without them", "source": "https://github.com/dokima-dev/dokima/issues/615", "criterion": "S2.2"},
  {"ask": "Verdict, one of: Symptom of a known cause, Root cause found, New", "source": "https
```

> Exit code 1
> raise 1's text holds 53 words, over its cap of 30: cut 23, keep the facts
> raise 2's text holds 37 words, over its cap of 30: cut 7, keep the facts
> previous_step decided line 1 holds 16 words, over its cap of 15: cut 1, keep the facts
> previous_step open line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`5. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r["raises"][0]["text"]="S1.1 omits each issue's own link, the plain reading of \"links\". S1.2 reads it as relationship links without asking. Fix: S1.1 lists each link; ask whether relationships are meant too."
r["raises"][1]["text"]="S1.1 promises every open issue, but no edge case covers more than one page of them, which this repo hits. Fix: add that edge case."
r["previous_step"]["decided"][0]="A symptom becomes a sub-issue of its cause and closes with it."
r["previous_step"]["open"][0]="Two owner questions: is a symptom a sub-issue, and do sub-issues act like splits?"
r["asks"][10]["source"]="https://github.com/dokima-dev/dokima/issues/615"
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 615 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I've handed back a **block** on the plan for [#615](https://github.com/dokima-dev/dokima/issues/615) (filing symptoms under their root cause). It passes both checks.

**Two blockers, both sent back to the planner:**
1. **"Links" read one way without asking.** The owner asked for open issues "with their titles, summaries and links". The plainest reading is each issue's own link, but no criterion includes it. Instead, the plan reads "links" as blocked-by, blocks and sub-issue links and doesn't raise a question about it. Fix: list each issue's link, and ask whether the relationship links are wanted too.
2. **Only the first page of open issues.** The first criterion promises every open issue, but no edge case covers more than one page of them. This repo has over 600 issues, so it will likely hit that. Fix: add that edge case.

**The planner's two questions are left for the owner.** I didn't answer them on autopilot because the plan's reading changes how the system works:
- Is a symptom filed as a sub-issue of its cause?
- If so, should it act like a split? I confirmed the planner's evidence in `dokima/agent.py`: autopilot never starts the planner on an issue with sub-issues (around line 1994). An issue also closes itself once all its sub-issues close (around line 2069). So a cause with symptoms under it would never be planned on autopilot, and closing a symptom by hand could close the cause.

**The rest of the plan looks fine:**
- Every other ask maps to a criterion.
- Each criterion is one behavior.
- The size is ok: 14 criteria in 5 stories.
- The "which ones Dokima filed" criterion can use the existing `filed-by-dokima` label.
- The plan is a split, so it names no tests yet and I had none to run.

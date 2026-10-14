# reviewer (plan) for #642

Run: https://github.com/dokima-dev/dokima/actions/runs/38491438568

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #642: No cap on stories; up to five acceptance criteria per story
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Each story may hold up to five criteria, and an issue may split into any number of stories.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/553
> - https://github.com/dokima-dev/dokima/issues/432
> 
> 
> **User story:** The owner gets narrow stories of at most five criteria, in as many stories as the work needs.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A story of four or five criteria passes the plan check; a story of six is refused.
>   - *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-642/tests/test_story_cap.py#L39"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Verified by</a>: A story of four or five criteria passes; a story of six is refused.*
>   - Edge cases: A story of six beside a story of

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_story_cap.py; git show --stat HEAD; grep -n "stories\|/ 3\|ceil\|STORY\|criteria_per" dokima/planner.py | head -50
```

> """Each story holds up to five criteria, with no cap on stories (#642).
> 
> The owner wants narrow tasks: a story never holds more than five criteria, but there is no cap on how many stories an
> issue splits into. These tests run the plan check itself and read the rules every agent is given."""
> import os
> import sys
> 
> import pytest
> 
> ROOT = os.path.join(os.path.dirname(__file__), "..")
> sys.path.insert(0, ROOT)
> from dokima import agent, planner  # noqa: E402
> 
> SRC = "https://github.com/dokima-dev/dokima/issues/642"
> C = {"text": "a", "source": SRC}
> 
> 
> def sized(k):
>     """A story holding k acceptance criteria."""
>     return {"acceptance_criteria": [C] * k, "non_functional": []}
> 
> 
> def feature(*sizes):
>     """A split whose stories hold the given numbers of criteria, none waiting on another."""
>     return {"kind": "feature", "title": "t", "summary": "s", "feature": "f",
>             "stories": [{"title": f"s{n}", "user_story": "u", "acceptance_criteria": [C] * k, "non_functional": [],
>                          "depends_on": []} for n, k in enumerate(sizes)]}
> 
> 
> def refused(stories, nested=False):
>     """The size check's refusal of these stories, or None when it lets them through."""
>     try:
>         planner.check_size(stories, nested)
>     except planner.Garbled as e:
>         return str(e)
>     return None
> 
> 
> def test_a_story_holds_up_to_five_criteria(record_property):
>     """A story of four or five criteria passes; a story of six is refused.
> 
>     Runs the size check on one story of 4, one of 5,

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_story_cap.py 2>&1 | grep -E "642\.|passed|failed|Error" | head -20; git diff HEAD~1 -- tests/test_size_rule.py tests/test_plan_shape.py tests/test_card_status.py; sed -n 225,260p dokima/planner.py; python -m pytest -q -x tests/test_size_rule.py tests/test_plan_shape.py tests/test_card_status.py 2>&1 | tail -5
```

> Proves 642.1."""
>         record_property("proves", "642.1")
> >           assert why is None, f"642.1: one story of {k} criteria was refused, though up to five are allowed: {why}"
> E           AssertionError: 642.1: one story of 4 criteria was refused, though up to five are allowed: 4 criteria make 2 stories (3 at most each), not 1: split into exactly 2
> tests/test_story_cap.py:49: AssertionError
>         Proves 642.2."""
>         record_property("proves", "642.2")
>         Proves 642.2."""
>         record_property("proves", "642.2")
> >               pytest.fail(f"642.2: a split into {len(sizes)} stories of {list(sizes)} criteria was refused: {e}")
> E               Failed: 642.2: a split into 7 stories of [5, 5, 5, 5, 5, 5, 1] criteria was refused: a feature needs 2 to 5 stories
>         Proves 642.3."""
>         record_property("proves", "642.3")
> >           assert "1 to 5 criteria" in text, f"642.3: {name} never says a story holds 1 to 5 criteria"
> E           AssertionError: 642.3: planner.md never says a story holds 1 to 5 criteria
> tests/test_story_cap.py:89: AssertionError
> FAILED tests/test_story_cap.py::test_a_story_holds_up_to_five_criteria - AssertionError: 642.1: one story of 4 criteria was refused, though up to five are allowed: 4 criteria make 2 stories (3 at most each), not 1: split into exactly 2
> FAILED tests/test_story_cap.py::test_a_split_may_have_any_number_of_stories - Failed: 642.2: a split into 7 stories of [5, 5, 5, 5, 5, 5, 1] criteria was refused: a feature needs 2 t

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "check_size" dokima/*.py; grep -n "def problems_size" -A12 dokima/agent.py
```

> dokima/planner.py:131:def check_size(stories, nested=False):
> dokima/planner.py:248:        check_size(stories, isinstance(issue, tuple))
> dokima/planner.py:268:    check_size([p], isinstance(issue, tuple))
> 1360:def problems_size(r, ids=()):
> 1361-    """A plan review must judge each criterion one behavior or not, in `behaviors`, and say whether the plan keeps the
> 1362-    size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks it; a plan that breaks
> 1363-    it is never approved."""
> 1364-    bad = []
> 1365-    rows = r.get("behaviors") if isinstance(r.get("behaviors"), list) else []
> 1366-    seen = {str(b.get("criterion")): b for b in rows if isinstance(b, dict)}
> 1367-    for k in ids:
> 1368-        b = seen.get(str(k))
> 1369-        if not b or not isinstance(b.get("one_behavior"), bool) or not str(b.get("why") or "").strip():
> 1370-            bad.append(f"behaviors has no judgment of criterion {k}: say one_behavior true or false, and why in one line")
> 1371-    bundled = [k for k, b in seen.items() if b.get("one_behavior") is False]
> 1372-    size = str(r.get("size") or "").strip()

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote three criteria: five criteria per story, any number of stories, and the agents' rules saying so.",
          "The planner updated four older tests and deleted one that refused small splits."],
  "decided": ["Small splits, even one criterion per story, now pass; a split still needs two stories."],
  "open": ["The planner flagged an older issue that still says three per story."]},
 "verdict": "approve",
 "summary": "The plan keeps both asks, five criteria per story and no cap on stories, and each test fails today for the right reason.",
 "raises": [],
 "answers": [{"raise": "P1", "answer": "done", "why": "Confirmed: that issue still hands extras past three criteria to a new story, which this rule changes."}],
 "asks": [
  {"ask": "Stories, you can create as many as you want.", "source": "https://github.com/dokima-dev/dokima/issues/642", "criterion": "642.2"},
  {"ask": "you can have up to five acceptance criteria per story", "source": "https://github.com/dokima-dev/dokima/issues/642", "criterion": "642.1"}],
 "behaviors": [
  {"criterion": "642.1", "one_behavior": true, "why": "One cap of five, with its pass and refuse sides."},
  {"criterion": "642.2", "one_behavior": true, "why": "One result: a split of many stories passes."},
  {"criterion": "642.3", "one_behavior": true, "why": "One result: the agents' rules state the new size rule."}],
 "edge_cases": [
  {"criterion": "642.1", "cut": [], "missing": []},
  {"criterion": "642.2", "cut": [], "missing": []},
  {"criterion": "642.3", "cut": [], "missing": []}],
 "tests": [
  {"test": "tests/test_story_cap.py::test_a_story_holds_up_to_five_criteria", "only_its_behavior": true, "why": "Runs the size check at four, five and six, alone and as a parent's story."},
  {"test": "tests/test_story_cap.py::test_a_split_may_have_any_number_of_stories", "only_its_behavior": true, "why": "Runs the plan check on seven
```

> Exit code 1
> summary holds 23 words, over its cap of 20 (up to 24 passes)
> previous_step did line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

**Agent:** Shortening two lines that run over the word cap, then re-running the check.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r["summary"]="The plan keeps both asks, five criteria per story and no cap on stories; each test fails today correctly."
r["summary"]="The plan keeps both asks: five criteria per story, no cap on stories. Each new test fails today."
r["previous_step"]["did"][0]="The planner wrote three criteria: five per story, any number of stories, rules saying so."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 642 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> summary holds more than one sentence: make it one sentence of at most 20 words saying what the run did

`7. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r["summary"]="The plan keeps both asks, five criteria per story and no cap on stories, and each new test fails today."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 642 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P1 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P1 files an issue, so verdict must be symptom, root cause or new, not None

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "searched\|symptom, root cause" dokima/agent.py | head -20; grep -n -i "searched" dokima/roles/reviewer.md | head
```

> 299:def problems_searched(h, pack_dir):
> 300:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 303:    names the open issues it searched and its verdict, on the raise or on the answer."""
> 425:        bad += problems_searched(h, pack_dir)
> 1899:            body += ["", "**Open issues searched:** " + ", ".join(f"#{n}" for n in decided[raises.SEARCHED])]

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 280,340p dokima/agent.py; ls /tmp/pack
```

> if issue_body.STORY.match(owner):
>         story = re.search(r"^\*\*User story:\*\* (.*)$", owner, re.M)
>         if story:
>             return story.group(1).strip()
>     return first_sentence(owner) if owner.strip() else ""
> 
> 
> def reviewer_open_issues(repo):
>     """Every open issue for the reviewer: number, title, summary, link and whether Dokima filed it.
> 
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
>     A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
>     names the open issues it searched and its verdict, on the raise or on the answer."""
>     own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
>         if isinstance(h.get("raises"), list) else []
>     path = os.path.join(pack_dir, "open_blockers.json")
>     listed = json.load(op

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def filing_problems" -A30 dokima/raises.py; grep -n "^SEARCHED\|^SYMPTOMS\|^CAUSE\|^VERDICT" dokima/raises.py; python3 -c "
import json;d=json.load(open('/tmp/pack/open_issues.json'))
for i in d:
  t=(i['title']+' '+i['summary']).lower()
  if any(w in t for w in ['stor','criteri','split','size']): print(i['number'],i['title'],'|',i['summary'][:120])"
```

> 44:def filing_problems(where, decided):
> 45-    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> 46-    problems = []
> 47-    searched = decided.get(SEARCHED)
> 48-    if not is_numbers(searched) or not searched:
> 49-        problems.append(f"{where} files an issue, so {SEARCHED} must list the open issues searched for the same "
> 50-                        f"cause, not {searched!r}")
> 51-    if decided.get(VERDICT) not in VERDICTS:
> 52-        problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
> 53-    cause = decided.get(CAUSE)
> 54-    if decided.get(VERDICT) == "symptom" and not (isinstance(cause, int) and not isinstance(cause, bool)):
> 55-        problems.append(f"{where} is a symptom, so {CAUSE} must name its cause, an open issue by number, not {cause!r}")
> 56-    symptoms = decided.get(SYMPTOMS)
> 57-    if decided.get(VERDICT) == "root cause" and (not is_numbers(symptoms) or not symptoms):
> 58-        problems.append(f"{where} is a root cause, so {SYMPTOMS} must list the open issues it explains, not "
> 59-                        f"{symptoms!r}")
> 60-    return problems
> 61-
> 62-
> 63-def is_numbers(v):
> 64-    """True for a list of whole numbers, true and false left out."""
> 65-    return isinstance(v, list) and all(isinstance(n, int) and not isinstance(n, bool) for n in v)
> 66-
> 67-
> 68-def check_raises(role, raises):
> 69-    """The problems with the raises an agent of `role` wrote; empty when they are fine

`11. Bash`
```
cd /home/runner/work/dokima/dokima; python3 - <<'EOF'
import json;p='/tmp/dokima-out/review.json';r=json.load(open(p))
r["answers"]=[{"raise":"P1","answer":"disagree","why":"No new issue is needed: #553 is already open, and its own re-plan can move to five."}]
r["previous_step"]["open"]=["The planner flagged that open issue #553 still says three per story."]
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 642 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#642](https://github.com/dokima-dev/dokima/issues/642) (up to five criteria per story, no cap on stories) and raised no blockers. The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Asks:** both of the owner's asks have a criterion. "Up to five acceptance criteria per story" is covered by 642.1, and "as many [stories] as you want" by 642.2.
- **Tests:** I ran the three new tests on this branch and each fails for the right reason, because the feature is missing:
  - a story of four criteria is still refused under today's limit of three per story;
  - a split into seven stories is refused because today's check allows only 2 to 5;
  - the planner's rules don't say "1 to 5 criteria" yet.
- **Older tests:** one of the older tests the planner rewrote fails until the code changes, which is expected. That's the one checking a parent's story may now hold five criteria.
- **Size:** I judged each criterion to be one behavior. 642.3 is the closest call, since it checks that the rules say both "one to five per story" and "no cap on stories"; I counted that as one result, the rules stating the new size rule.
- **The planner's choice:** the planner read "as many as you want" to mean even one criterion per story is fine, so it deleted the old test that refused small splits. That fits the owner's words, so I didn't raise a question about it.
- **The planner's flag about the old three-per-story rule:** I answered "disagree", so no new issue gets filed. That rule lives in [#553](https://github.com/dokima-dev/dokima/issues/553) (extras past three criteria go to a new story), which is already open. It can be re-planned to say five, or closed.

Autopilot was switched off on this issue before the review started, so the plan now waits for the owner's `/work`.

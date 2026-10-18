# reviewer (plan) for #853

Run: https://github.com/dokima-dev/dokima/actions/runs/39094914009

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #853: Every label a person adds now queues an autopilot run; a waiting close run it replaces loses its close work.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> **Backlog**
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> 
> Every label a person adds now queues an autopilot run; a waiting close run it replaces loses its close work.
> 
> **Evidence:** `dokima/agent_roles.py` `labeled` branch never calls `autopilot_closed`; `autopilot.yml` queue keeps one waiting run.
> 
> **Verdict:** New
> 
> **Open issues searched:** #491, #386, #111
> 
> The reviewer found it on #811 ([run](https://github.com/dokima-dev/dokima/actions/runs/39092471468)).
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/owner-approval.svg" width="16" height="16" align="absmiddle" 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat /tmp/pack/in/01-planner.json | head -50; git show --stat HEAD; cat tests/test_autopilot_label_close.py; grep -n "autopilot_closed\|labeled" dokima/agent_roles.py | head -40
```

> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "39094720553",
>  "commit_before": "c68db07f49b74f1109fbcbd2fa85633369cf5092",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 135473,
>   "turns": 19,
>   "cost_usd": 0.9134158,
>   "tokens_in": 1020725,
>   "tokens_out": 10368
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/853/39094720553-planner.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/39094720553",
>  "handback": {
>   "kind": "user_story",
>   "title": "A label run also does a dropped close's work",
>   "summary": "Adding the autopilot label by hand no longer loses the work of a close it pushed out of the queue.",
>   "user_story": "When a label replaces a waiting close run, the close's autopilot work still happens.",
>   "acceptance_criteria": [
>    {
>     "text": "When a label run follows a dropped close, a parent whose last sub-issue closed closes, saying its tree is done.",
>     "words": "a waiting close run it replaces loses its close work",
>     "source": "https://github.com/dokima-dev/dokima/issues/853",
>     "files": [
>      "dokima/agent_roles.py",
>      "rules/flow.md"
>     ],
>     "edge_cases": [
>      {
>       "case": "The parent still has an open sub-issue, so it stays open with no comment.",
>       "test": "tests/test_autopilot_label_close.py::test_a_label_run_closes_the_done_parent_of_a_dropped_close"
>      }
>     ]
>    },
>    {
>     "text": "When a label run follows a dropped close, every issue of a

`3. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 560,720p dokima/agent_roles.py
```

> "GitHub answers.")
>         if rec.get("role") == "worker":
>             # The pull request is opened after the record is written, so the worker's sentence links it only now.
>             try:
>                 pr = agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
>                         "-q", ".[0].number").strip()
>             except subprocess.CalledProcessError:
>                 pr = ""
>             if pr.isdigit():
>                 url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/pull/{pr}"
>                 open(os.path.join(out, "comment.md"), "w").write(render(rec, url))
>         filed = file_issues(repo, number, rec, records(items))
>         if filed:
>             # The issues filed in this run go on its record, above the full record, whatever GitHub answered.
>             text = open(os.path.join(out, "comment.md")).read()
>             fold = "\n<details><summary>Full record</summary>"
>             at = text.find(fold)
>             at = len(text.rstrip("\n")) if at < 0 else at
>             open(os.path.join(out, "comment.md"), "w").write(text[:at] + "\n".join(filed) + "\n" + text[at:])
>         path = os.path.join(out, "comment.md")
>         text = open(path).read() if os.path.exists(path) else ""
>         open(path, "w").write(with_next(text, next_line(step, owners)) if text else "\n" + next_line(step, owners) + "\n")
>         if step[3:] == ("autopilot",):
>             # The line the owner would ha

`4. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_autopilot_label_close.py 2>&1 | grep -E "853\.|passed|failed|Error" | head -30
```

> Proves 853.1.
>         record_property("proves", "853.1")
>             f"853.1: #59 is {m.state(59)} after the label run, though its only sub-issue #301 closed; the dropped close's work was lost\n{m.tail()}"
> E       AssertionError: 853.1: #59 is ('open', None) after the label run, though its only sub-issue #301 closed; the dropped close's work was lost
> tests/test_autopilot_label_close.py:33: AssertionError
>         Proves 853.2.
>         record_property("proves", "853.2")
>         assert not m.failed, f"853.2: a workflow failed when #60 was labeled: {m.failures}\n{m.tail()}"
>             f"853.2: these issues of done trees stayed on autopilot after the label run, so the dropped closes were lost: {sorted(left)}\n{m.tail()}"
> E       AssertionError: 853.2: these issues of done trees stayed on autopilot after the label run, so the dropped closes were lost: [59, 61, 301]
> tests/test_autopilot_label_close.py:61: AssertionError
>         Proves 853.3.
>         record_property("proves", "853.3")
> >       bw.assert_plans_again_once(m, "853.3", "label run after a dropped close")
> m = <test_autopilot_close.Repo object at 0x7fa2bbbfa9f0>, crit = '853.3'
>         assert not m.failed, f"{crit} ({case}): a workflow failed: {m.failures}\n{m.tail()}"
> E       AssertionError: 853.3 (label run after a dropped close): #57's planner started 0 times, expected once
> tests/test_blocked_worker.py:188: AssertionError
> FAILED tests/test_autopilot_label_close.py::test_a_label_run_closes_the_done_parent_of_a_dropped_clo

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 560,720p dokima/agent_roles.py
```

`6. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 600 python -m pytest -q tests/test_autopilot_label_close.py 2>&1 | grep -E "853\.|passed|failed|Error" | head -30
```

> "GitHub answers.")
>         if rec.get("role") == "worker":
>             # The pull request is opened after the record is written, so the worker's sentence links it only now.
>             try:
>                 pr = agent_github.gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "open", "--json", "number",
>                         "-q", ".[0].number").strip()
>             except subprocess.CalledProcessError:
>                 pr = ""
>             if pr.isdigit():
>                 url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/pull/{pr}"
>                 open(os.path.join(out, "comment.md"), "w").write(render(rec, url))
>         filed = file_issues(repo, number, rec, records(items))
>         if filed:
>             # The issues filed in this run go on its record, above the full record, whatever GitHub answered.
>             text = open(os.path.join(out, "comment.md")).read()
>             fold = "\n<details><summary>Full record</summary>"
>             at = text.find(fold)
>             at = len(text.rstrip("\n")) if at < 0 else at
>             open(os.path.join(out, "comment.md"), "w").write(text[:at] + "\n".join(filed) + "\n" + text[at:])
>         path = os.path.join(out, "comment.md")
>         text = open(path).read() if os.path.exists(path) else ""
>         open(path, "w").write(with_next(text, next_line(step, owners)) if text else "\n" + next_line(step, owners) + "\n")
>         if step[3:] == ("autopilot",):
>             # The line the owner would ha

> Proves 853.1.
>         record_property("proves", "853.1")
>             f"853.1: #59 is {m.state(59)} after the label run, though its only sub-issue #301 closed; the dropped close's work was lost\n{m.tail()}"
> E       AssertionError: 853.1: #59 is ('open', None) after the label run, though its only sub-issue #301 closed; the dropped close's work was lost
> tests/test_autopilot_label_close.py:33: AssertionError
>         Proves 853.2.
>         record_property("proves", "853.2")
>         assert not m.failed, f"853.2: a workflow failed when #60 was labeled: {m.failures}\n{m.tail()}"
>             f"853.2: these issues of done trees stayed on autopilot after the label run, so the dropped closes were lost: {sorted(left)}\n{m.tail()}"
> E       AssertionError: 853.2: these issues of done trees stayed on autopilot after the label run, so the dropped closes were lost: [59, 61, 301]
> tests/test_autopilot_label_close.py:61: AssertionError
>         Proves 853.3.
>         record_property("proves", "853.3")
> >       bw.assert_plans_again_once(m, "853.3", "label run after a dropped close")
> m = <test_autopilot_close.Repo object at 0x7fa2bbbfa9f0>, crit = '853.3'
>         assert not m.failed, f"{crit} ({case}): a workflow failed: {m.failures}\n{m.tail()}"
> E       AssertionError: 853.3 (label run after a dropped close): #57's planner started 0 times, expected once
> tests/test_blocked_worker.py:188: AssertionError
> FAILED tests/test_autopilot_label_close.py::test_a_label_run_closes_the_done_parent_of_a_dropped_clo

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def close_quietly\|def add_label\|def new_comments\|def on_autopilot\|def state" -A12 tests/test_autopilot_close.py | head -90; grep -n "def close_done_parents\|def autopilot_closed" -A30 dokima/*.py | grep -n "tree\|done\|def " | head -30
```

> 295:    def on_autopilot(self):
> 296-        """The issues that carry the autopilot label now."""
> 297-        return {n for n, ls in self.labels().items() if LABEL in ls}
> 298-
> 299:    def state(self, n):
> 300-        """("open", None) or ("closed", reason) for issue n, as GitHub holds it now."""
> 301-        st = self._json("states.json").get(str(n)) or {}
> 302-        return st.get("state", "open"), st.get("reason")
> 303-
> 304-    def issue_event(self, n):
> 305-        """The issue as GitHub puts it in the event payload."""
> 306-        parent = next((int(p) for p, cs in self._json("tree.json").items() if int(n) in cs), None)
> 307-        state, reason = self.state(n)
> 308-        return {"number": int(n), "title": f"Issue {n}", "state": state, "state_reason": reason,
> 309-                "html_url": f"https://github.com/o/r/issues/{n}",
> 310-                "parent_issue_url": f"https://api.github.com/repos/o/r/issues/{parent}" if parent else None,
> 311-                "labels": [{"name": l} for l in self.labels().get(int(n), [])], "user": {"login": OWNER, "type": "User"}}
> --
> 313:    def close_quietly(self, n):
> 314-        """Issue n closes as completed, but its close workflows never run: GitHub cancelled them while they waited."""
> 315-        states = self._json("states.json")
> 316-        states[str(n)] = {"state": "closed", "reason": "completed"}
> 317-        json.dump(states, open(f"{self.tmp}/gh/states.json", "w"))
> 318-
> 319-    def close_context(self, n):
> 320-        """The contexts 

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "The planner wrote three criteria for the close work a label run must now do.",
   "The planner added three tests, each failing today because the close work is lost."
  ],
  "decided": [
   "A label run does a dropped close's work: done parents close, done trees leave autopilot, unblocked issues plan again."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "The plan makes a label run do the close work it pushed out, with a failing test for each part.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "a waiting close run it replaces loses its close work", "source": "https://github.com/dokima-dev/dokima/issues/853", "criterion": "853.1"},
  {"ask": "`labeled` branch never calls `autopilot_closed`", "source": "https://github.com/dokima-dev/dokima/issues/853", "criterion": "853.2"}
 ],
 "behaviors": [
  {"criterion": "853.1", "one_behavior": true, "why": "One result: the done parent closes with its tree-done note."},
  {"criterion": "853.2", "one_behavior": true, "why": "One result: a done tree goes off autopilot."},
  {"criterion": "853.3", "one_behavior": true, "why": "One result: the unblocked issue's planner starts once."}
 ],
 "edge_cases": [
  {"criterion": "853.1", "cut": [], "missing": []},
  {"criterion": "853.2", "cut": [], "missing": []},
  {"criterion": "853.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_autopilot_label_close.py::test_a_label_run_closes_the_done_parent_of_a_dropped_close", "only_its_behavior": true, "why": "Runs the real label workflow; fails today with the parent still open."},
  {"test": "tests/test_autopilot_label_close.py::test_a_label_run_switches_a_dropped_closes_done_tree_off_autopilot", "only_its_behavior": true, "why": "Fails today with the done trees still on autopilot; checks open trees stay on."},
  {"test": "tests/test_autopilot_label_close.py::test_a_label_run_plans_again_an_issue_a_dropped_c
```

> Exit code 1
> previous_step decided line 1 holds 19 words, over its cap of 15: cut 4, keep the facts

**Agent:** Plan review is written; one summary line ran over its word limit, so I'm trimming it and checking again.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/"A label run does a dropped close.s work: done parents close, done trees leave autopilot, unblocked issues plan again."/"A label run now also does the work of any close it pushed out."/' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 853 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#853](https://github.com/dokima-dev/dokima/issues/853) (a label run that pushes out a waiting close run loses that close's work). The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What the plan promises:** when a person adds the autopilot label and that drops a waiting close run, the label run still does the close's work:
- **853.1:** A parent whose last sub-issue closed is closed, with a note saying its tree is done.
- **853.2:** Every issue in a finished tree goes off autopilot.
- **853.3:** An issue whose last open blocker just closed has its planner start exactly once.

**Tests:** I ran the three new tests on this branch. All three fail today for the right reason:
- the parent stays open;
- the issues #59, #61 and #301 stay on autopilot;
- the planner starts 0 times instead of once.

Each test also checks the case that must not change: a tree that isn't finished stays as it is, and an issue still waiting on another blocker doesn't start.

**Why the plan holds up:** the code that runs after a close already does all three things. The label run just never calls it, as the issue says. So calling it from the label run will make all three tests pass.

**Nothing raised:**
- I found no missing asks, weak tests or criteria bundling two behaviors.
- The plan also updates the written flow rules. I counted that as needed, not extra scope.
- There were no open blockers from earlier rounds to answer.

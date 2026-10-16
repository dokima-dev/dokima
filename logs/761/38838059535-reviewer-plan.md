# reviewer (plan) for #761

Run: https://github.com/dokima-dev/dokima/actions/runs/38838059535

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> .:
> total 116
> drwxr-xr-x  3 runner runner  4096 Oct 16 01:59 .
> drwxrwxrwt 18 root   root    4096 Oct 16 01:59 ..
> drwxr-xr-x  2 runner runner  4096 Oct 16 01:59 in
> -rw-r--r--  1 runner runner 21885 Oct 16 01:59 issue.md
> -rw-r--r--  1 runner runner   350 Oct 16 01:59 open_blockers.json
> -rw-r--r--  1 runner runner 59502 Oct 16 01:59 open_issues.json
> -rw-r--r--  1 runner runner  1987 Oct 16 01:59 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 16 01:59 parent.json
> -rw-r--r--  1 runner runner  4663 Oct 16 01:59 plan.json
> 
> in:
> total 44
> drwxr-xr-x 2 runner runner 4096 Oct 16 01:59 .
> drwxr-xr-x 3 runner runner 4096 Oct 16 01:59 ..
> -rw-r--r-- 1 runner runner 5305 Oct 16 01:59 01-planner.json
> -rw-r--r-- 1 runner runner 4734 Oct 16 01:59 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 4649 Oct 16 01:59 03-planner.json
> -rw-r--r-- 1 runner runner 3827 Oct 16 01:59 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 5420 Oct 16 01:59 05-planner.json
> # Issue #761: Delete the planner's old post and reject steps
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 760, 762, 765 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Deletes the planner's unused post and reject steps and its old plan writer, with their tests.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/761#issuecommen

`2. Bash`
```
cd /tmp/pack; cat owner_words.json parent.json; for f in in/*; do echo "== $f"; cat $f; echo; done
```

> {
>  "https://github.com/dokima-dev/dokima/issues/761#issuecomment-6205927207": "/plan drop it if it is useless",
>  "https://github.com/dokima-dev/dokima/issues/739": "Part of the portability plan (#272).\n\nCode left over from the old label flow (removed in #516) and from Dokima's own repo. Nothing on main calls it; each item was checked with a grep of dokima/, .github/workflows/ and tests/ at f71d144. Delete it, plus the tests that only exercise it.\n\n**Old label flow**\n- `dokima/plan.py:22,141-157,164-178`: label approval (`LABEL = \"work\"`, `approved_at`, `approved_version`). `fetch_issue` still makes a paginated events call and parses edit history on every card draw and scan, and no caller reads `plan`, `changes` or `approved_at`. Keep the body and url fetch.\n- `dokima/plan.py:23`: `WORK_BRANCH`, never used.\n- `dokima/plan.py:28-124,191-203,210-213`: the checkbox plan parser (`parse`, `lines`, `changes`), `as_text` and the `plan issue` command. No workflow calls them; only tests do. Keep `approvers`.\n- `dokima/planner.py:588-607,632-640,676-685`: the `post` and `rejected` actions, `render` and `plan_text`. Workflows call only `planner check`.\n- `dokima/fence.py:17-30` and the `scope_of` branch at `:80`: reads Scope from issue text; agent.yml always passes plan.json.\n- `dokima/agent_github.py:26,72`, `dokima/card.py:655`: lookups of `work/issue-N` branches. Keep `try/issue-N`.\n- `dokima/card.py:671-673,684-687,754`: `RUN_TITLE \"worker for #N\"` and the `worker.yml`

`3. Bash`
```
sed -n 420,460p dokima/planner.py; grep -n "manual" dokima/roles/planner.md dokima/planner.py | head -20; python -m pytest -q tests/test_planner_old_steps.py 2>&1 | tail -15; cat tests/test_planner_old_steps.py
```

> return [t for t in names if t.partition("::")[2] not in test_functions(read_now(t.partition("::")[0]))]
> 
> 
> def problems(number, plan, files, tc, declared=None):
>     """What is wrong with a plan and the tests it touched; empty when it can be posted.
> 
>     Given the tests the plan declares, each must be in the repo and filed under one of the plan's criteria, and an
>     older test already in the repo counts as proof of the criteria it is filed under.
>     """
>     out = [f"{p} is outside tests/; the planner may only write tests" for p in files if not p.startswith("tests/")]
>     if not tc["added"] and not tc["changed"]:
>         out.append("the plan came with no tests")
>     keys = {f"{number}.{k}" for k in range(1, len(plan["criteria"]) + 1)}
>     proven = {k for ks in proving(tc).values() for k in ks}
>     if declared is not None:
>         names = sorted(declared_by_test(declared))
>         out += [f"the plan names {t}, which is not in the repo" for t in missing_tests(names)]
>         out += [f"tests are filed under {k}, which is not a criterion of this plan ({number}.1 to {number}.{len(keys)})"
>                 for k in sorted(declared) if k not in keys]
>         proven |= {k for k, ts in declared.items() if ts}
>     out += [f"criterion {k} has no test" for k in sorted(keys - proven)]
>     out += [f"{t} proves {k}, which is not a criterion of this plan" for t, ks in tc["added"].items() for k in ks if k not in keys]
>     out += [f"{t} now proves {k}, which is neither a criterion of this plan n

`4. Bash`
```
git diff --stat origin/main...HEAD 2>/dev/null || git diff --stat main...HEAD; grep -rn "planner.render\|plan_text\|\"post\"\|'post'\|rejected" tests/ | grep -v test_planner_old_steps | grep -i "planner" | head
```

> tests/test_body.py               |  84 ++----------------------------
>  tests/test_card_every_change.py  |  39 +++-----------
>  tests/test_card_folds.py         |  15 +++---
>  tests/test_open_ask.py           |  28 ++--------
>  tests/test_open_until_planned.py |  17 +-----
>  tests/test_planner.py            |  63 ++--------------------
>  tests/test_planner_old_steps.py  | 110 +++++++++++++++++++++++++++++++++++++++
>  tests/test_rules_split.py        |  19 +++++--
>  tests/test_scope_from_files.py   |   4 +-
>  9 files changed, 152 insertions(+), 227 deletions(-)
> tests/test_new_issue_card.py:49:NO_PLAN = {"no record": [], "only a rejected plan": [rec("planner", passed=False, **PLAN)]}
> tests/test_card_raises_status.py:248:    ("a rejected plan carrying a question waits for you", (rec("planner", passed=False, **dict(PLAN, raises=[Q1])),),
> tests/test_card_raises_status.py:249:     card.TODO["rejected"], (planner(Q1),), 0),
> tests/test_plan_shape.py:115:    assert planner.problems("9", p, ["tests/t.py"], tc) == [], "138.3: a declared plan was still rejected"
> tests/test_scope_from_files.py:82:    """The planner's instructions no longer ask for the rejected scope field.
> tests/test_raises.py:116:    rejected; checks a worker's raise to the planner goes to the reviewer first and every other raise to its target.
> tests/test_raises.py:284:    and the planner skip its own; checks each is rejected naming every skipped ID, while raises sent to others are not
> tests/test_raises.py:301:    assert m.check_

`5. Bash`
```
grep -rnE "planner\.(render|plan_text)|plan_text\(|\"post\"|'rejected'|\"rejected\"," tests/ | grep -v old_steps | head; python -m pytest -q -x 2>&1 | tail -5
```

> tests/test_autopilot_river.py:374:    r = run(monkeypatch, tmp_path / "rejected", "reviewer", "plan", ts.STORY_PLANNED, ON, try_branch=True,
> tests/test_cancelled_run.py:48:    out["rejected"] = Run(t / "rejected", "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BAD_REVIEW)
> tests/test_cancelled_run.py:112:    for name in ("rejected", "no-tools", "blocked"):
> tests/test_cancelled_run.py:163:    for name in ("rejected", "no-tools"):
> tests/test_cancelled_run.py:191:    for name in ("rejected", "no-tools"):
> tests/test_field_icons.py:338:              ("rejected", "failed", agent.render(built(role, stage, hb, passed=False, problems="a problem"))),
> tests/test_visuals_finalize.py:364:    p = fresh(place, "post")
> tests/test_run_comment_fields.py:262:                  ("rejected", run("reviewer", stage, BLOCK, passed=False, problems="a problem\n")[0]),
>   ?         -----
>   + claude-opus-5-5
>   ?        +++)
> !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
> 1 failed, 36 passed, 1 warning in 5.01s

**Agent:** Still on the plan review: the planner's tests check out. Now checking one failing test in the full suite to see whether this plan caused it.

`6. Bash`
```
python -m pytest -q 2>&1 | grep -E "^FAILED|passed|failed" | tail -15; git stash list | head -1
```

> Command did not complete within its 120s timeout and was moved to the background (ID: b2y78hpkn). Output is being written to: /tmp/claude-1001/-home-runner-work-dokima-dokima/70ccd95f-db6e-4e9f-935e-81c2f3c28ca3/tasks/b2y78hpkn.output. You will be notified when it completes. If it is still running after 10m in the background, it will be stopped and you will be notified. To check interim output, use Read on that file path.

`7. Bash`
```
grep -n "escalate" dokima/*.py | head -20
```

> dokima/agent_next.py:185:    if verdict == "escalate":
> dokima/agent_next.py:186:        return ("stop", "The reviewer escalated this to you, see why above.")
> dokima/agent_checks.py:128:        bad.append("verdict must be approve, block or escalate")
> dokima/agent_checks.py:294:            bad.append("verdict must be approve, block or escalate")
> dokima/card.py:33:        "escalated": "Settle the escalation",
> dokima/card.py:344:    if verdict == "escalate":
> dokima/card.py:345:        return TODO["escalated"]
> dokima/agent_records.py:15:VERDICTS = {"approve", "block", "escalate"}
> dokima/agent_records.py:597:    if h.get("verdict") == "escalate" and filled(h.get("summary")):
> dokima/agent_records.py:633:                "escalate": f"{name} escalated {what} to you."}.get(h.get("verdict"), f"{name} judged {what}.")
> dokima/agent_records.py:785:        parts += [("Details", ([f"- {h['summary']}"] if h.get("summary") and h.get("verdict") != "escalate" else [])
> dokima/agent_records.py:824:                "escalate": f"The reviewer escalated {what} to you."}.get(h.get("verdict"), f"The reviewer judged {what}.")
> dokima/agent_records.py:880:        if h.get("verdict") == "escalate" and h.get("summary"):

`8. Bash`
```
sed -n 280,340p dokima/agent_checks.py
```

> bad.append(f"{label} needs {', '.join(missing)}")
>     return bad
> 
> 
> def problems_shape(kind, h):
>     """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
>     bad = problems_old(h) + problems_raised("reviewer" if kind == "review" else "worker", h)
>     if kind == "review":
>         prev = h.get("previous_step")
>         if not isinstance(prev, dict):
>             bad.append("previous_step must be an object with did, decided and open")
>         elif not all(isinstance(prev.get(k, []), list) and all(filled(x) for x in prev.get(k, [])) for k in ("did", "decided", "open")):
>             bad.append("previous_step: did, decided and open must each be a list of lines")
>         if h.get("verdict") not in VERDICTS:
>             bad.append("verdict must be approve, block or escalate")
>         if not filled(h.get("summary")):
>             bad.append("summary must be one non-empty sentence")
>         return bad
>     if not filled(h.get("summary")):
>         bad.append("summary must be one non-empty sentence")
>     crit = h.get("criteria")
>     if not isinstance(crit, dict) or not crit:
>         bad.append("criteria must be an object giving one line per criterion")
>     else:
>         bad += [f"criteria: the line for {k} must be non-empty text" for k, v in crit.items() if not filled(v)]
>     if not filled(h.get("evidence")):
>         bad.append("evidence must name the last test command and its result line")
>     return bad
> 
> 
> def plan_criter

`9. Bash`
```
sleep 100; tail -15 /tmp/claude-1001/-home-runner-work-dokima-dokima/70ccd95f-db6e-4e9f-935e-81c2f3c28ca3/tasks/b2y78hpkn.output
```

> <tool_use_error>Blocked: sleep 100 followed by: tail -15 /tmp/claude-1001/-home-runner-work-dokima-dokima/70ccd95f-db6e-4e9f-935e-81c2f3c28ca3/tasks/b2y78hpkn.output. To wait for a condition, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`). To wait for a command you started, use run_in_background: true. Do not chain shorter sleeps to work around this block.</tool_use_error>

**Agent:** I'll write the review while the suite runs.

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["Kept the four criteria and their tests unchanged."],
  "decided": ["Did not restore the criterion for deleting old tests, since the check refuses one without a test."],
  "open": ["Asks the owner if the list of deleted old tests is enough for that ask."]
 },
 "verdict": "escalate",
 "summary": "The planner and reviewer disagree whether deleting the old tests needs its own criterion; only you can settle it.",
 "raises": [],
 "answers": [
  {"raise": "P3", "answer": "done", "why": "Confirmed: the planner role allows a manual criterion, but the plan check refuses any criterion without a test."}
 ],
 "asks": [
  {"ask": "the `post` and `rejected` actions", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.1"},
  {"ask": "the `post` and `rejected` actions (rejected)", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.2"},
  {"ask": "`render` and `plan_text` (render)", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.3"},
  {"ask": "`render` and `plan_text` (plan_text)", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "761.4"},
  {"ask": "Delete it, plus the tests that only exercise it.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "missing"}
 ],
 "behaviors": [
  {"criterion": "761.1", "one_behavior": true, "why": "One step asked for, one result: nothing posted."},
  {"criterion": "761.2", "one_behavior": true, "why": "One step asked for, one result: nothing posted."},
  {"criterion": "761.3", "one_behavior": true, "why": "One piece of code gone."},
  {"criterion": "761.4", "one_behavior": true, "why": "One piece of code gone."}
 ],
 "edge_cases": [
  {"criterion": "761.1", "cut": [], "missing": []},
  {"criterion": "761.2", "cut": [], "missing": []},
  {"criterion": "761.3", "cut": [], "missing": []},
  {"criterion": "761.4", "cu
```

> Exit code 1
> previous_step decided line 1 holds 17 words, over its cap of 15: cut 2, keep the facts

`11. Bash`
```
cd /tmp/dokima-out && sed -i 's/Did not restore the criterion for deleting old tests, since the check refuses one without a test./Left out the old-tests criterion, since the check refuses one without a test./' review.json && cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 761 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> Exit code 1
> the answer to P3 files an issue, so searched must list the open issues searched for the same cause, not None
> the answer to P3 files an issue, so verdict must be symptom, root cause or new, not None

`12. Bash`
```
cd /tmp/pack; python3 -c "
import json
for i in json.load(open('open_issues.json')):
    t=json.dumps(i).lower()
    if 'manual' in t: print(i.get('number'), i.get('title'))
" ; head -c 600 open_issues.json; grep -n "searched\|symptom" /home/runner/work/dokima/dokima/dokima/agent_checks.py | head
```

> [
>  {
>   "number": 771,
>   "title": "The card shows a skipped check as failed, so a draft's unrun acceptance check looks red.",
>   "summary": "The card shows a skipped check as failed, so a draft's unrun acceptance check looks red.",
>   "link": "https://github.com/dokima-dev/dokima/issues/771",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 766,
>   "title": "Delete the unused card sample",
>   "summary": "The card sample for issue 455, which nothing uses, is deleted.",
>   "link": "https://github.com/dokima-dev/dokima/issues/766",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 765,
>   "title": "Delete the un14:def problems_searched(h, pack_dir):
> 15:    """What each filed issue lacks (#622), and each searched issue not open in the pack.
> 18:    names the open issues it searched and its verdict, on the raise or on the answer."""
> 120:        bad += problems_searched(h, pack_dir)
> Shell cwd was reset to /home/runner/work/dokima/dokima

`13. Bash`
```
sed -n 10,50p dokima/agent_checks.py; python3 -c "
import json
for i in json.load(open('/tmp/pack/open_issues.json')):
    t=(i['title']+i['summary']).lower()
    if any(w in t for w in ('test','criterion','planner','check')): print(i['number'], i['title'])"
```

> from dokima import raises, words
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
>              if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numb

`14. Bash`
```
grep -n "SEARCHED\s*=\|SYMPTOMS\s*=\|CAUSE\s*=\|VERDICT\|def filing_problems" -A3 dokima/raises.py | head -40
```

> 23:SEARCHED = "searched"
> 24-# Every issue the reviewer files, its own or one it confirms, also gives its verdict, one of these (#622).
> 25:VERDICT = "verdict"
> 26:VERDICTS = MappingProxyType({"symptom": "Symptom of a known cause", "root cause": "Root cause found", "new": "New"})
> 27-# A symptom names its cause, one open issue; a root cause names its symptoms, the open issues it explains (#623).
> 28:CAUSE = "cause"
> 29:SYMPTOMS = "symptoms"
> 30-STAMPED = ("raised_by", "id")
> 31-ANSWERS = ("done", "disagree")
> 32-PREFIX = MappingProxyType({"planner": "P", "worker": "W", "reviewer": "R"})
> --
> 40:    names = list(VERDICTS)
> 41-    return ", ".join(names[:-1]) + " or " + names[-1]
> 42-
> 43-
> 44:def filing_problems(where, decided):
> 45-    """What a reviewer's filing lacks: the open issues it searched, and a verdict."""
> 46-    problems = []
> 47-    searched = decided.get(SEARCHED)
> --
> 51:    if decided.get(VERDICT) not in VERDICTS:
> 52:        problems.append(f"{where} files an issue, so {VERDICT} must be {_verdicts()}, not {decided.get(VERDICT)!r}")
> 53-    cause = decided.get(CAUSE)
> 54:    if decided.get(VERDICT) == "symptom" and not (isinstance(cause, int) and not isinstance(cause, bool)):
> 55-        problems.append(f"{where} is a symptom, so {CAUSE} must name its cause, an open issue by number, not {cause!r}")
> 56-    symptoms = decided.get(SYMPTOMS)
> 57:    if decided.get(VERDICT) == "root cause" and (not is_numbers(symptoms) or not symptoms):
> 58-        problems.append(f"{where} is a root cause,

`15. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['answers'][0].update({"searched":[718,173,233],"verdict":"new"})
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 761 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK; tail -8 /tmp/claude-1001/-home-runner-work-dokima-dokima/70ccd95f-db6e-4e9f-935e-81c2f3c28ca3/tasks/b2y78hpkn.output
```

> OK

**Agent:** The hand-back passes its checks. Last thing: seeing which test failed in the quick run of the full suite.

`16. Bash`
```
timeout 100 python -m pytest -q -x 2>&1 | grep -E "^FAILED|Error" | head -3
```

> E       AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''
> tests/test_agents.py:220: AssertionError
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the planner's model should be claude-sonnet-5-5: exit 0; stdout: 'claude-opus-5-5'; stderr: ''

**Agent:** I escalated issue [#761](https://github.com/dokima-dev/dokima/issues/761) (delete the planner's old post and reject steps) to you. The plan review can't approve it, and only you can settle the one open question.

**What's settled:**
- The four criteria for deleting the post step, the reject step, the old plan writer and the old plan text builder are each one behavior.
- Each of the four has a test that fails today because the old code is still there.
- The plan's own changes already delete the old tests that only checked that code. No remaining test calls the deleted code.

**What's open:** your ask in [#739](https://github.com/dokima-dev/dokima/issues/739) (the parent cleanup issue), "Delete it, plus the tests that only exercise it."
- My last review asked the planner to put this ask back as a manual criterion. I've now dropped that. The planner was right: the plan check refuses any criterion with no test, so a manual one can't pass.
- No test can fail today for "old tests are deleted", so the ask has no criterion.
- The planner's question for you: is the plan's list of deleted tests enough to cover this ask? Your earlier "drop it if it is useless" could mean drop the test, or the ask too. I left that for you.
- Answer with `/plan`. If the list is enough, say so and the plan can go ahead as is.

**Proposed new issue:** the planner role allows a manual criterion, but the plan check refuses one. I confirmed this and found no open issue with the same cause; [#718](https://github.com/dokima-dev/dokima/issues/718) (new tests that pass today are rejected) is close but different.

One test in the full suite fails: the planner model comes out as Opus where Sonnet was expected. This branch only touches tests, and this looks like the settings leak in open issue [#727](https://github.com/dokima-dev/dokima/issues/727) (runner settings leak into tests). I didn't confirm that by running it on main. The full suite didn't finish within the time limit.

The review is in `/tmp/dokima-out/review.json` and passes both checks.

**Agent:** The full test run I started in the background was stopped at its time limit, so I never got a full result.

The review doesn't depend on it. I ran the planner's four new tests myself, and each fails today for the right reason: the old code is still there. The quick run stopped at its first failure, a model-name test that looks like the settings leak in [#727](https://github.com/dokima-dev/dokima/issues/727) (runner settings leak into tests). I haven't confirmed that, and other failures may come after it.

The escalation in `/tmp/dokima-out/review.json` stands as written and passes its checks.

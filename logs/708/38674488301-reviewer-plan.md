# reviewer (plan) for #708

Run: https://github.com/dokima-dev/dokima/actions/runs/38674488301

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/plan.json; cat /tmp/pack/open_blockers.json
```

> # Issue #708: Every role reads the parent's ask and the owner's commands
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Workers and reviewers on a story read the parent's ask and the owner's comments; the owner's commits count as words.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 2 questions](https://github.com/dokima-dev/dokima/issues/708#issuecomment-6183399175) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/559
> - https://github.com/dokima-dev/dokima/issues/707
> - https://github.com/dokima-dev/dokima/issues/715
> - https://github.com/dokima-dev/dokima/issues/335
> 
> 
> **User story:** Every role on a story sees the parent's ask, and the owner's comments and commits steer the work.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A worker on a split story finds the parent's original 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_story_reads_parent.py; git show --stat HEAD | head -30; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> """Every role reads the parent's ask; the owner's commits count as words (#708).
> 
> A story split from a parent holds a planner's text, not the owner's. Before #708 only the planner's starting pack held
> the parent's original issue and the owner's comments on it (owner_words.json); the worker and the reviewers worked
> from the story alone. These tests build each role's starting pack the way a run does, with GitHub faked in one place
> (`dokima.agent_github.gh`), and look for the parent's words in any file of the pack, so the file's name and shape are
> the worker's choice.
> 
> The last test fakes an owner's commit on the issue's branch, try/issue-7, and checks the planner's hand-back check
> accepts a criterion quoting the committed text with the commit's link as its source. GitHub answers the branch's
> commits the ways the API offers: `repos/o/r/compare/BASE...try/issue-7`, `repos/o/r/commits?sha=try/issue-7` and each
> commit's own `repos/o/r/commits/SHA`, which carries its author's login and its files' patches.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> import tempfile
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from dokima import agent  # noqa: E402
> from dokima import agent_github  # noqa: E402
> from dokima import planner  # noqa: E402
> import record_seed  # noqa: E402
> 
> N, PARENT, OWNER = 9, 5, "boss"
> PARENT_ASK = "Every story keeps the detail of the parent, word for word."
> OWNER_ON_PARENT = "Keep the old card for one week after t

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_story_reads_parent.py 2>&1 | tail -40; python -m pytest -q tests/test_agent.py -k "a_command_starts_its_stage or the_pack_reads_the_issue_and_its_pr" 2>&1 | tail -5
```

> monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff44be35640>
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_text_the_owner_committed_0')
> 
>     def test_text_the_owner_committed_on_the_branch_counts_as_their_words(record_property, monkeypatch, tmp_path):
>         """A criterion may quote a line the owner committed, citing the commit as its source.
>     
>         Fakes an owner's commit and a stranger's on try/issue-7, builds the owner's words the way the planner's pack does,
>         and runs the planner's hand-back check on a plan quoting each commit's line: the owner's is accepted, the
>         stranger's refused, so the check is not a blanket yes. Proves 708.5."""
>         record_property("proves", "708.5")
>         fake_branch(monkeypatch)
>         said = agent.owner_words("o/r", 7, {"body": "The ask."}, [], [OWNER])
>         pack, out = tmp_path / "pack", tmp_path / "out"
>         pack.mkdir()
>         out.mkdir()
>         (pack / "owner_words.json").write_text(json.dumps(said))
>         monkeypatch.setenv("PACK", str(pack))
>         (out / "plan.json").write_text(json.dumps(plan_quoting(OWNER_LINE, "https://github.com/o/r/commit/abc123")))
>         try:
>             planner.read_output(str(out), 7)
>         except planner.Garbled as e:
> >           pytest.fail(f"708.5: a criterion quoting the owner's committed line was refused: {e}")
> E           Failed: 708.5: a criterion quoting the owner's committed line was refused: acceptance criterion 1 has the source https://gi

`4. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_story_reads_parent.py; git show --stat HEAD | head -30; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(d.keys());print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_story_reads_parent.py 2>&1 | tail -40; python -m pytest -q tests/test_agent.py -k "a_command_starts_its_stage or the_pack_reads_the_issue_and_its_pr" 2>&1 | tail -5
```

> """Every role reads the parent's ask; the owner's commits count as words (#708).
> 
> A story split from a parent holds a planner's text, not the owner's. Before #708 only the planner's starting pack held
> the parent's original issue and the owner's comments on it (owner_words.json); the worker and the reviewers worked
> from the story alone. These tests build each role's starting pack the way a run does, with GitHub faked in one place
> (`dokima.agent_github.gh`), and look for the parent's words in any file of the pack, so the file's name and shape are
> the worker's choice.
> 
> The last test fakes an owner's commit on the issue's branch, try/issue-7, and checks the planner's hand-back check
> accepts a criterion quoting the committed text with the commit's link as its source. GitHub answers the branch's
> commits the ways the API offers: `repos/o/r/compare/BASE...try/issue-7`, `repos/o/r/commits?sha=try/issue-7` and each
> commit's own `repos/o/r/commits/SHA`, which carries its author's login and its files' patches.
> """
> import json
> import os
> import re
> import subprocess
> import sys
> import tempfile
> 
> import pytest
> 
> sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
> from dokima import agent  # noqa: E402
> from dokima import agent_github  # noqa: E402
> from dokima import planner  # noqa: E402
> import record_seed  # noqa: E402
> 
> N, PARENT, OWNER = 9, 5, "boss"
> PARENT_ASK = "Every story keeps the detail of the parent, word for word."
> OWNER_ON_PARENT = "Keep the old card for one week after t

> monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7ff44be35640>
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_text_the_owner_committed_0')
> 
>     def test_text_the_owner_committed_on_the_branch_counts_as_their_words(record_property, monkeypatch, tmp_path):
>         """A criterion may quote a line the owner committed, citing the commit as its source.
>     
>         Fakes an owner's commit and a stranger's on try/issue-7, builds the owner's words the way the planner's pack does,
>         and runs the planner's hand-back check on a plan quoting each commit's line: the owner's is accepted, the
>         stranger's refused, so the check is not a blanket yes. Proves 708.5."""
>         record_property("proves", "708.5")
>         fake_branch(monkeypatch)
>         said = agent.owner_words("o/r", 7, {"body": "The ask."}, [], [OWNER])
>         pack, out = tmp_path / "pack", tmp_path / "out"
>         pack.mkdir()
>         out.mkdir()
>         (pack / "owner_words.json").write_text(json.dumps(said))
>         monkeypatch.setenv("PACK", str(pack))
>         (out / "plan.json").write_text(json.dumps(plan_quoting(OWNER_LINE, "https://github.com/o/r/commit/abc123")))
>         try:
>             planner.read_output(str(out), 7)
>         except planner.Garbled as e:
> >           pytest.fail(f"708.5: a criterion quoting the owner's committed line was refused: {e}")
> E           Failed: 708.5: a criterion quoting the owner's committed line was refused: acceptance criterion 1 has the source https://gi

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "Anything I write\|my comments, which only\|then say /review\|I edit them by comment" --include=*.md --include=*.py . | head; ls /tmp/pack
```

> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json

`7. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:200]);
s=json.dumps(d)
for w in ['Anything I write','my comments, which only','then say /review','I edit them by comment']: print(w, w in s)
"; python3 -c "
import json;d=json.load(open('parent.json'));print(d.keys() if isinstance(d,dict) else type(d))"
```

> {
>  "number": 559
> }
> Anything I write False
> my comments, which only False
> then say /review False
> I edit them by comment False
> dict_keys(['number'])
> Shell cwd was reset to /home/runner/work/dokima/dokima

`8. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def owner_words\|def pack\b\|def pack(" -A25 dokima/agent_roles.py | head -90; grep -n "owner_words" dokima/*.py | head -20
```

> 105:def owner_words(repo, number, d, items, owners):
> 106-    """Where the owner said things, as {link: text}: the issue's own ask, each code owner's
> 107-    comment, and the same on its parent issue. Every criterion of a plan must quote words found at its source link
> 108-    (#416)."""
> 109-    from dokima.body import ask
> 110-    mine = lambda c: (c.get("author") or {}).get("login") in owners and c.get("url")
> 111-    from dokima.body import STORY
> 112-    # A story split from a parent holds a planner's text, not the owner's: only the parent's ask counts as theirs.
> 113-    own = ask(d.get("body") or "")
> 114-    out = {} if STORY.match(own) else {issue_url(number): own}
> 115-    out.update({c["url"]: c.get("body") or "" for c in items if mine(c)})
> 116-    up = parent_words(repo, number)
> 117-    if up:
> 118-        out[issue_url(up["number"])] = ask(up["body"])
> 119-        out.update({c["url"]: c.get("body") or "" for c in up["comments"] if mine(c)})
> 120-    return out
> 121-
> 122-
> 123-class TurnHeld(Exception):
> 124-    """The worker's pack is not built: another story holds the turn on a shared file."""
> 125-
> 126-
> 127:def pack(repo, number, role, stage, dest):
> 128-    """Build the starting pack for one role and stage.
> 129-
> 130-    The issue and its PRs' conversation from GitHub, every agent record so far from the record files (#610),
> 131-    the open raises this role must answer (open_blockers.json), the newest passed plan, the issue's parent on GitHub (parent.json, naming none when it 

**Agent:** Tests 708.1–708.5 fail today for the right reason. Now checking the two older tests that pin 708.6 and 708.7.

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 170,240p tests/test_agent.py
```

> (d / "in" / "01-planner.json").unlink()
>     (d / "issue.md").write_text("   \n")
>     assert agent.problems_pack("planner", "", str(d)) == ["issue.md is empty", "issue.md has no comments section"]
> 
> 
> def test_the_pack_reads_the_issue_and_its_pr_as_one_conversation(record_property, tmp_path, monkeypatch):
>     """Comments from the issue, its PR, PR reviews and line notes on the code arrive in time order, each labeled with where it was written; records come from both."""
>     record_property("proves", "agent.12")
>     plan = rec("planner", handback={"kind": "user_story", "user_story": "s"})
>     def fake_gh(*args):
>         if args[:2] == ("issue", "view"):
>             return json.dumps({"number": 7, "title": "T", "body": "B", "comments": [
>                 {"author": {"login": "owner"}, "body": "/plan first", "createdAt": "2026-01-01T00:00:01Z"},
>                 {"author": {"login": "dokima-runtime"}, "body": agent.render(plan), "createdAt": "2026-01-01T00:00:03Z"}]})
>         if args[:2] == ("pr", "list"):
>             return json.dumps([{"number": 9}] if "try/issue-7" in args else [])
>         if args[:2] == ("pr", "view"):
>             return json.dumps({"comments": [{"author": {"login": "owner"}, "body": "/work change it", "createdAt": "2026-01-01T00:00:04Z"}],
>                                "reviews": [{"author": {"login": "owner"}, "body": "line note", "submittedAt": "2026-01-01T00:00:02Z", "state": "COMMENTED"}]})
>         if args[0] == "api" and args[1].endswith("/pulls/9/comments"

**Agent:** Next: writing the review. The 708.7 test builds the reviewer's pack instead of the planner's. The 708.6 test checks many other commands too.

`10. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner wrote seven criteria from the parent story's list.", "The planner wrote five new tests that fail today.", "The planner pinned two already-built criteria with older tests."],
  "decided": ["Committed text counts as the owner's words only when the owner made the commit."],
  "open": ["The planner asks the owner whether two already-built asks need only the older tests."]},
 "verdict": "block",
 "summary": "Two criteria lean on older tests that prove a neighbour or much more than their one behavior.",
 "raises": [
  {"kind": "blocker", "to": "planner", "label": "708.7 wrong role", "text": "The test for 708.7 builds the reviewer's pack, not the planner's, so it never shows the next planner gets the /plan comment. Fix: a test that builds the planner's pack and finds the owner's /plan comment word for word.", "evidence": "`tests/test_agent.py::test_the_pack_reads_the_issue_and_its_pr_as_one_conversation` calls `agent.pack(\"o/r\", 7, \"reviewer\", \"plan\", ...)` (line 194)."},
  {"kind": "blocker", "to": "planner", "label": "708.6 test too broad", "text": "The test for 708.6 checks /plan, /work, prose and unlinked pull requests too, not only /review on a pull request. Fix: a new test for /review on a pull request, with /review on a later line starting nothing.", "evidence": "`tests/test_agent.py::test_a_command_starts_its_stage_and_anything_else_starts_nothing` has nine asserts; one covers /review on a pull request (line 211)."}
 ],
 "answers": [],
 "asks": [
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559", "criterion": "708.1"},
  {"ask": "Every role working on a split story gets the parent's original issue and my comments, which only the planner gets today.", "source": "https://github.com/dokima-dev/dokima/issues/559"
```

> Exit code 1
> raise 1's text holds 39 words, over its cap of 30: cut 9, keep the facts
> raise 2's text holds 38 words, over its cap of 30: cut 8, keep the facts

`11. Bash`
```
cd /tmp/dokima-out && python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r['raises'][0]['text']="The 708.7 test builds the reviewer's pack, not the planner's. Fix: a test building the planner's pack that finds the owner's /plan comment word for word."
r['raises'][1]['text']="The 708.6 test also checks /plan, /work, prose and unlinked pull requests. Fix: a test for /review on a pull request, and /review on a later line."
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 708 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I've blocked the plan for [#708](https://github.com/dokima-dev/dokima/issues/708) (every role reads the parent's ask). Two of its seven criteria rely on older tests that don't prove their one behavior. The review is in `/tmp/dokima-out/review.json` and passes both checks.

**What works:** I ran the five new tests and all fail today for the right reason:
- **708.1 to 708.4:** the worker's and reviewers' starting packs don't hold the parent's issue or the owner's comments on it.
- **708.5:** a quote from the owner's commit is refused. The test also confirms a line someone else committed stays refused, so a check that accepts everything would fail it.

All seven of the owner's asks from [#559](https://github.com/dokima-dev/dokima/issues/559) (tests are the spec) have a criterion, and each criterion is one behavior. I couldn't open #559 itself, but the planner's quotes passed the planner's word check.

**Blockers, both sent back to the planner:**
- **708.7, the /plan comment reaching the next planner:** the test builds the reviewer's starting pack, not the planner's (`tests/test_agent.py:194`). It proves the comment reaches a different role. The fix is a test that builds the planner's pack and finds the comment word for word.
- **708.6, /review on a pull request starting code review:** the test also checks /plan, /work, plain prose and unlinked pull requests; only one line covers /review on a pull request (`tests/test_agent.py:211`). The fix is a dedicated test that also checks /review on a later line starts nothing.

**For the owner:** the planner's two questions are still waiting on you, both about 708.6 and 708.7, which already work today:
- **P1:** is pinning /review with the older test enough?
- **P2:** is pinning the /plan comment with the older test enough?

I didn't answer them on your behalf because nothing you've written settles either one.

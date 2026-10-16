# reviewer (plan) for #680

Run: https://github.com/dokima-dev/dokima/actions/runs/38828691204

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat open_blockers.json; cat plan.json
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
> # Issue #680: The start of a secret token can leak into run transcripts
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [746], "loop": []} -->
> Run transcripts cut tool text before removing secrets, so a cut token's start gets published.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/706
> 
> 
> **User story:** No part of a secret token ever shows in a published run transcript.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A secret running across the cut of a tool's input shows none of its start in the transcript.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-680/tests/test_transcript_cut.py#L22"><img src="https://raw.githu

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_transcript_cut.py; sed -n 940,1010p dokima/agent_records.py; python -m pytest -q tests/test_transcript_cut.py 2>&1 | tail -30; cat /tmp/pack/owner_words.json /tmp/pack/parent.json | head -50
```

> """A secret cut in half by the transcript's length limit never shows its start (#680).
> 
> The transcript cuts each tool's input to 2000 characters and each tool's result to 1500. Secrets must be removed
> before that cut: a token cut in half no longer matches its full value, so its start would be published. Each test
> places a 40-character token across the cut and checks that none of it shows, and that the cut itself still holds.
> """
> import json
> 
> from dokima.agent_records import transcript
> 
> TOKEN = "ghs_Q7mK2pP9vL4nR8tW3bZ6cC1dF5hJ0aE2uI7o"
> 
> 
> def write_log(tmp_path, entries):
>     """Write one Claude session log holding ENTRIES; return the log root."""
>     log = tmp_path / ".claude" / "p"
>     log.mkdir(parents=True)
>     (log / "s.jsonl").write_text("\n".join(json.dumps(x) for x in entries) + "\n")
>     return str(tmp_path)
> 
> 
> def test_a_secret_across_the_tool_input_cut_shows_none_of_its_start(record_property, tmp_path):
>     """A token across the 2000-character tool input cut shows none of its characters.
> 
>     The command holds 1990 x's, then the 40-character token, then 3000 y's. Cutting first leaves the token's first
>     ten characters in the transcript; removing secrets first leaves none. The y's must still be cut away. Proves 680.1."""
>     record_property("proves", "680.1")
>     assert len(TOKEN) == 40
>     command = "x" * 1990 + TOKEN + "y" * 3000
>     root = write_log(tmp_path, [{"message": {"role": "assistant", "content": [
>         {"type": "tool_use", "name": "Bash", "input": {"c

`3. Bash`
```
cd /home/runner/work/dokima/dokima; cp dokima/agent_records.py /tmp/ar.bak; python3 - <<'E'
p='dokima/agent_records.py';s=open(p).read()
s=s.replace("{str(what)[:2000]}","{scrub(str(what), secrets)[:2000]}").replace('r.strip()[:1500]','scrub(r.strip(), secrets)[:1500]')
open(p,'w').write(s)
E
python -m pytest -q tests/test_transcript_cut.py 2>&1|tail -2; cp /tmp/ar.bak dokima/agent_records.py; git status --short
```

> ..                                                                       [100%]
> 2 passed in 0.05s

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'E'
{"previous_step": {"did": ["The planner wrote two criteria: a secret across the tool input cut, and across the tool result cut.", "The planner wrote one test for each, placing a 40-character token across the cut."], "decided": ["Secrets are removed before the cut, and the cut lengths stay the same."], "open": []},
 "verdict": "approve",
 "summary": "The plan covers both cuts the owner named, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "cuts tool input and results to 2000 and 1500 characters before secrets are removed. A token cut in half no longer matches and its start gets published. Reproduced with a 40-character token. Remove secrets first, then cut.", "source": "https://github.com/dokima-dev/dokima/issues/680", "criterion": "680.1"},
  {"ask": "cuts tool input and results to 2000 and 1500 characters before secrets are removed. A token cut in half no longer matches and its start gets published. Remove secrets first, then cut.", "source": "https://github.com/dokima-dev/dokima/issues/680", "criterion": "680.2"}
 ],
 "behaviors": [
  {"criterion": "680.1", "one_behavior": true, "why": "One cut, tool input; one result, no part of the secret shows."},
  {"criterion": "680.2", "one_behavior": true, "why": "One cut, tool result; one result, no part of the secret shows."}
 ],
 "edge_cases": [
  {"criterion": "680.1", "cut": [], "missing": []},
  {"criterion": "680.2", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_transcript_cut.py::test_a_secret_across_the_tool_input_cut_shows_none_of_its_start", "only_its_behavior": true, "why": "Fails today showing the token's start; passes once secrets go first; also checks the cut still holds."},
  {"test": "tests/test_transcript_cut.py::test_a_secret_across_the_tool_result_cut_shows_none_of_its_start", "only_its_behavior": true, "why": "Fails today showing the token's start; passes once secre
```

> Exit code 1
> previous_step did line 1 holds 18 words, over its cap of 15: cut 3, keep the facts

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/The planner wrote two criteria: a secret across the tool input cut, and across the tool result cut./The planner wrote two criteria: a secret across the input cut, and the result cut./' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 680 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I approved the plan for [#680](https://github.com/dokima-dev/dokima/issues/680) (secret token start leaking into run transcripts), with no blockers.

- **What the owner asked:** remove secrets first, then cut the text. Two criteria carry that: one for the tool's input, one for the tool's result. Nothing is missing.
- **Tests fail today for the right reason:** both show the token's first characters in the transcript.
- **Tests pass with the right fix:** I tried removing secrets before each cut, and both passed. I then put the file back, so nothing in the repo changed.
- **The cut still has to hold:** each test also fails if the text is no longer cut.

The review is saved in `/tmp/dokima-out/review.json`, and it passes both checks.

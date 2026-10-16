# reviewer (plan) for #766

Run: https://github.com/dokima-dev/dokima/actions/runs/38831799788

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #766: Delete the unused card sample
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> **Backlog**
> 
> <!-- /dokima-card -->
> 
> <!-- dokima-ask -->
> <details><summary>Original issue</summary>
> 
> <!-- dokima-card -->
> <!-- /dokima-card -->
> 
> <details open><summary>From the approved plan of #739, story 7</summary>
> 
> **Part of:** #739 Delete dead code from the old label flow
> 
> **User story:** The card sample for issue 455 that nothing uses is gone.
> 
> **Context:** `docs/rendered/455.json` is the only file in `docs/rendered/`. Nothing in `dokima/`, `tests/` or `.github/` names it.
> 
> **Acceptance criteria:**
> - The unused card sample for issue 455 is deleted. ([source](https://github.com/dokima-dev/dokima/issues/739))
> 
> </details>
> 
> 
> </details>
> 
> <!-- dokima-done -->
> **Definition of Done:** <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> All tests · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/code-review.svg" width="16" height="16" align="absmiddle" alt="code review"> Code review · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> <img src="https://raw.githubusercontent

`2. Bash`
```
cat tests/test_card_sample_gone.py; ls docs/rendered; grep -rn "455.json\|docs/rendered" --include=*.py --include=*.yml --include=*.md . | grep -v "^./tests/test_card_sample_gone" | head; python -m pytest -q tests/test_card_sample_gone.py 2>&1 | tail -5; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps(d,indent=1)[:2500])"
```

> """#766: the unused card sample for issue 455 is deleted.
> 
> The file `docs/rendered/455.json` was a card fixture that nothing in the code,
> tests or workflows read. This test checks it no longer exists in the repo.
> """
> import os
> 
> ROOT = os.path.join(os.path.dirname(__file__), "..")
> 
> 
> def test_unused_card_sample_is_deleted(record_property):
>     """The card sample for issue 455 is no longer in the repo.
> 
>     Looks for `docs/rendered/455.json` from the repo root and fails while it is still there. Proves 766.1."""
>     record_property("proves", "766.1")
>     path = os.path.join(ROOT, "docs", "rendered", "455.json")
>     assert not os.path.exists(path), "766.1: the unused card sample docs/rendered/455.json is still in the repo"
> 455.json
> tests/test_card_sample_gone.py:3:The file `docs/rendered/455.json` was a card fixture that nothing in the code,
> tests/test_card_sample_gone.py:14:    Looks for `docs/rendered/455.json` from the repo root and fails while it is still there. Proves 766.1."""
> tests/test_card_sample_gone.py:16:    path = os.path.join(ROOT, "docs", "rendered", "455.json")
> tests/test_card_sample_gone.py:17:    assert not os.path.exists(path), "766.1: the unused card sample docs/rendered/455.json is still in the repo"
> assert not True
>  +  where True = <function exists at 0x7f47b5def600>('/home/runner/work/dokima/dokima/tests/../docs/rendered/455.json')
>  +    where <function exists at 0x7f47b5def600> = <module 'posixpath' (frozen)>.exists
>  +      where <module 'posixpath' (frozen

`3. Bash`
```
grep -rn "rendered" dokima .github tests --include=* 2>/dev/null | grep -v test_card_sample_gone | head
```

> tests/test_raise_handbacks.py:114:    """A comment as GitHub returns it, carrying a record rendered by code."""
> tests/test_fixer.py:53:    """A comment as GitHub returns it, carrying a record rendered by code."""
> tests/test_agent.py:78:    """A comment as GitHub returns it, carrying a record rendered by code."""
> tests/test_agent.py:91:    """A record rendered into a comment reads back exactly; the same text posted by anyone else, or broken JSON, is not a record."""

`4. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner planned one criterion: the unused card sample for issue 455 is deleted.", "The planner added one test that fails while the sample is still there."], "decided": ["Nothing else in the repo uses the sample, so only that file changes."], "open": []},
 "verdict": "approve",
 "summary": "The plan deletes the one unused card sample, and its test fails today because the sample still exists.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "The unused card sample for issue 455 is deleted.", "source": "https://github.com/dokima-dev/dokima/issues/739", "criterion": "766.1"}],
 "behaviors": [{"criterion": "766.1", "one_behavior": true, "why": "One file is removed; nothing else changes."}],
 "edge_cases": [{"criterion": "766.1", "cut": [], "missing": []}],
 "tests": [{"test": "tests/test_card_sample_gone.py::test_unused_card_sample_is_deleted", "only_its_behavior": true, "why": "Fails only while the sample exists; passes once it is deleted."}],
 "size": "ok"}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 766 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#766](https://github.com/dokima-dev/dokima/issues/766) (delete the unused card sample). The approval is in `/tmp/dokima-out/review.json`, and both hand-back checks passed.

- **The ask is covered:** the issue makes one ask, to delete the unused card sample for issue 455. The plan's only criterion, 766.1, matches it word for word.
- **Nothing else uses the file:** I searched the code, tests and workflows. Only the planner's new test names `docs/rendered/455.json`, so deleting it should break nothing.
- **The test proves the ask:** `tests/test_card_sample_gone.py::test_unused_card_sample_is_deleted` fails today, saying the sample is still there. It will pass once the file is deleted.
- **Size and edge cases:** the plan has one criterion with one behavior. Deleting one file has no inputs, so it has no edge cases.

There were no open blockers to answer and no planner questions, so I raised nothing.

# reviewer (plan) for #849

Run: https://github.com/dokima-dev/dokima/actions/runs/39092025066

`1. Bash`
```
cat /tmp/pack/issue.md; ls /tmp/pack/in; cat /tmp/pack/open_blockers.json; cat /tmp/pack/plan.json
```

> # Issue #849: The owner moved the changelog listing what v0.1.0 does to its own issue.
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> The repo gains a changelog whose v0.1.0 section lists what that version does.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/849#issuecomment-6244949027) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/755
> - https://github.com/dokima-dev/dokima/issues/752
> 
> 
> **User story:** Owners read in one changelog what Dokima's first version, v0.1.0, does.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the changes land, the repo's changelog has a v0.1.0 section listing what that version does.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-849/tests/test_changelog.py#L32"><img src="ht

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_changelog.py; ls CHANGELOG* ; python -m pytest -q tests/test_changelog.py 2>&1 | tail -15; python3 -c "import json;d=json.load(open('/tmp/pack/in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; grep -rn "0.1.0\|changelog" --include=*.md --include=*.py --include=*.toml . | grep -v tests/test_changelog | head -20
```

> """The repo's changelog lists what v0.1.0 does (#849).
> 
> The owner moved the changelog out of the release story (#755) into this issue. That story's release workflow reads
> CHANGELOG.md at the repo root and uses the section under the heading naming v0.1.0 as the release notes, so this test
> reads the same file the same way: a heading naming v0.1.0, then the lines up to the next heading as high. The section
> must list at least one thing, as a markdown list item; a heading with nothing listed under it fails.
> """
> import os
> import re
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
> 
> 
> def changelog_section(text, version):
>     """The lines under the heading naming version, up to the next as high, else None."""
>     lines = text.splitlines()
>     heading = re.compile(r"^(#{1,6})\s+.*" + re.escape(version) + r"(?![0-9])")
>     for i, line in enumerate(lines):
>         m = heading.match(line)
>         if m:
>             out = []
>             for later in lines[i + 1:]:
>                 h = re.match(r"^(#{1,6})\s", later)
>                 if h and len(h.group(1)) <= len(m.group(1)):
>                     break
>                 out.append(later)
>             return out
>     return None
> 
> 
> def test_changelog_lists_v010(record_property):
>     """The changelog has a v0.1.0 section listing what that version does.
> 
>     849.1: reads CHANGELOG.md at the repo root, finds the heading naming v0.1.0 the way the release reads it, and
>     checks at least

`3. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {"did": ["The planner planned one criterion: the changelog has a v0.1.0 section listing what it does.", "The planner wrote one test that reads the changelog's v0.1.0 section."], "decided": ["The test checks the section lists at least one thing, not what it says."], "open": ["The owner decides if reading the list at approval is enough to judge it true."]},
 "verdict": "approve",
 "summary": "The plan carries the one ask; the owner still decides if reading the list at approval is enough.",
 "raises": [],
 "answers": [],
 "asks": [{"ask": "the changelog listing what v0.1.0 does", "source": "https://github.com/dokima-dev/dokima/issues/849", "criterion": "849.1"}],
 "behaviors": [{"criterion": "849.1", "one_behavior": true, "why": "One file with one section that lists what v0.1.0 does."}],
 "edge_cases": [{"criterion": "849.1", "cut": [], "missing": []}],
 "tests": [{"test": "tests/test_changelog.py::test_changelog_lists_v010", "only_its_behavior": true, "why": "Fails today because the changelog is missing; checks only the v0.1.0 section's list."}],
 "size": "ok",
 "boxes": {"dropped": "none", "added": "none", "superseded": "none", "conflicts": "none", "edges": {"849.1": "covered"}, "poor_tests": "none"}}
EOF
cd /home/runner/work/dokima/dokima && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 849 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#849](https://github.com/dokima-dev/dokima/issues/849) (changelog listing what v0.1.0 does). One question still waits for you before work starts.

- **What the plan covers:** You asked for one thing, "the changelog listing what v0.1.0 does", and the plan has one criterion for it, 849.1. Nothing is missing and nothing extra was added.
- **The test:** It reads the changelog's v0.1.0 section. It fails today for the right reason: the repo has no changelog yet.
- **Edge cases:** The test also fails when the changelog has no v0.1.0 heading, or when that heading lists nothing.
- **Your question:** The test only checks that the v0.1.0 section lists something, not what it says. The planner asked whether reading the list yourself at approval is enough to judge it true, and assumed yes. I left this for you to answer, because nothing you've written settles it.

The review passed both of Dokima's own checks. It is saved as `/tmp/dokima-out/review.json`.

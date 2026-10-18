# reviewer (plan) for #755

Run: https://github.com/dokima-dev/dokima/actions/runs/39092665065

`1. Bash`
```
cd /tmp/pack; ls -la . in; cat issue.md; cat open_blockers.json; cat plan.json
```

> <persisted-output>
> Output too large (33.8KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/1cc1e9b9-6c56-43ca-9a5d-3c0b6d91dd76/tool-results/bl08zvtnr.txt
> 
> Preview (first 2KB):
> .:
> total 124
> drwxr-xr-x  3 runner runner  4096 Oct 18 03:10 .
> drwxrwxrwt 18 root   root    4096 Oct 18 03:10 ..
> drwxr-xr-x  2 runner runner  4096 Oct 18 03:10 in
> -rw-r--r--  1 runner runner 30103 Oct 18 03:10 issue.md
> -rw-r--r--  1 runner runner     2 Oct 18 03:10 open_blockers.json
> -rw-r--r--  1 runner runner 62615 Oct 18 03:10 open_issues.json
> -rw-r--r--  1 runner runner  2377 Oct 18 03:10 owner_words.json
> -rw-r--r--  1 runner runner    15 Oct 18 03:10 parent.json
> -rw-r--r--  1 runner runner  3137 Oct 18 03:10 plan.json
> 
> in:
> total 72
> drwxr-xr-x 2 runner runner 4096 Oct 18 03:10 .
> drwxr-xr-x 3 runner runner 4096 Oct 18 03:10 ..
> -rw-r--r-- 1 runner runner 4115 Oct 18 03:10 01-planner.json
> -rw-r--r-- 1 runner runner 4292 Oct 18 03:10 02-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3776 Oct 18 03:10 03-planner.json
> -rw-r--r-- 1 runner runner 5105 Oct 18 03:10 04-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3782 Oct 18 03:10 05-planner.json
> -rw-r--r-- 1 runner runner 5173 Oct 18 03:10 06-reviewer-plan.json
> -rw-r--r-- 1 runner runner 3802 Oct 18 03:10 07-planner.json
> -rw-r--r-- 1 runner runner 4375 Oct 18 03:10 08-reviewer-plan.json
> -rw-r--r-- 1 runner runner 1689 Oct 18 03:10 09-worker.json
> -rw-r--r-- 1 runner runner 2641 Oct 18 03:10 10-reviewer-pr.json
> -rw-r--r--

`2. Bash`
```
cd /tmp/pack; cat issue.md
```

> <persisted-output>
> Output too large (29.4KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/1cc1e9b9-6c56-43ca-9a5d-3c0b6d91dd76/tool-results/b52l64lx1.txt
> 
> Preview (first 2KB):
> # Issue #755: First release v0.1.0 with a changelog
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 742, 812, 813, 816, 849 -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [816], "loop": []} -->
> Dokima gets its first version, v0.1.0, with a tag, a GitHub release and a changelog.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/850 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/850/files)
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/816
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/752
> - https://github.com/dokima-dev/dokima/issues/812
> - https://github.com/dokima-dev/dokima/issues/813
> - https://github.com/dokima-dev/dokima/issues/849
> 
> 
> **User story:** Owners see Dokima as a product with versions: a v0.1.0 release 

`3. Read`
```
/home/runner/.claude/projects/-home-runner-work-dokima-dokima/1cc1e9b9-6c56-43ca-9a5d-3c0b6d91dd76/tool-results/b52l64lx1.txt
```

> 1	# Issue #755: First release v0.1.0 with a changelog
> 2	
> 3	<!-- dokima-card -->
> 4	<!-- dokima-linked-from: 742, 812, 813, 816, 849 -->
> 5	<!-- dokima-blocking: {"blocked_by": [], "blocks": [816], "loop": []} -->
> 6	Dokima gets its first version, v0.1.0, with a tag, a GitHub release and a changelog.
> 7	
> 8	**Plan**
> 9	
> 10	https://github.com/dokima-dev/dokima/pull/850 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/850/files)
> 11	
> 12	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 13	
> 14	- https://github.com/dokima-dev/dokima/issues/816
> 15	
> 16	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 17	
> 18	- https://github.com/dokima-dev/dokima/issues/742
> 19	- https://github.com/dokima-dev/dokima/issues/752
> 20	- https://github.com/dokima-dev/dokima/issues/812
> 21	- https://github.com/dokima-dev/dokima/issues/813
> 22	- https://github.com/dokima-dev/dokima/issues/849
> 23	
> 24	
> 25	**User story:** Owners see Dokima as a product with versions: a v0.1.0 release and a changelog saying what it does.
> 26	
> 27	<img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" 

`4. Bash`
```
cd /tmp/pack; cat plan.json; echo; cat open_blockers.json owner_words.json parent.json; echo; cat in/08-reviewer-plan.json in/10-reviewer-pr.json in/11-planner.json
```

> {
>  "kind": "user_story",
>  "title": "First release v0.1.0 with a changelog",
>  "summary": "Dokima gets its first version, v0.1.0, with a tag, a GitHub release and a changelog.",
>  "user_story": "Owners see Dokima as a product with versions: a v0.1.0 release and a changelog saying what it does.",
>  "acceptance_criteria": [
>   {
>    "text": "When the changelog reaches main, the v0.1.0 tag is made at that commit.",
>    "words": "A workflow makes the tag and the release when the changelog merges",
>    "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244761525",
>    "files": [
>     "dokima/release.py",
>     ".github/workflows/release.yml",
>     "dokima/manifest.py"
>    ],
>    "edge_cases": [
>     {
>      "case": "A later push to main, once v0.1.0 exists, makes nothing new.",
>      "test": "tests/test_release.py::test_release_skips_when_tagged"
>     },
>     {
>      "case": "Main has no changelog yet, so nothing is made.",
>      "test": "tests/test_release.py::test_release_waits_for_changelog"
>     },
>     {
>      "case": "The changelog has no v0.1.0 section yet, so nothing is made.",
>      "test": "tests/test_release.py::test_release_waits_for_version_section"
>     }
>    ]
>   },
>   {
>    "text": "When the changelog reaches main, a GitHub release named v0.1.0 is made.",
>    "words": "A workflow makes the tag and the release when the changelog merges",
>    "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244761525",
>    "files": [
>     "dokima/release.py",
>     ".github/

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -3; git diff main --stat; ls dokima/release.py .github/workflows/release.yml; python -m pytest -q tests/test_release.py 2>&1 | tail -15; python -m pytest -q tests/test_manifest.py tests/test_settings_setup.py 2>&1 | tail -8
```

> 2c3594d Merge remote-tracking branch 'origin/main' into try/issue-755
> 79d4fd1 worker for #755 (run 39091603383)
> 5212e7d planner for #755 (run 39091382896)
>  .github/workflows/release.yml |  19 +++
>  dokima/release.py             |  68 ++++++++++
>  tests/test_release.py         | 304 ++++++++++++++++++++++++++++++++++++++++++
>  3 files changed, 391 insertions(+)
> .github/workflows/release.yml
> dokima/release.py
> .......                                                                  [100%]
> 7 passed in 0.50s
>   +     'dokima/release.py: gh release view is a GitHub call the manifest cannot '
>   +     'tie to an app permission',
>   +     'dokima/release.py: gh release create is a GitHub call the manifest cannot '
>   +     'tie to an app permission',
>   + ]
> FAILED tests/test_settings_setup.py::test_every_machine_that_runs_dokima_can_read_the_settings_file - AssertionError: 794.1: these jobs run Dokima before installing PyYAML, so they cannot read a settings file holding lists: release.yml job release (first Dokima step: 'Release from the changelog')
> assert not ["release.yml job release (first Dokima step: 'Release from the changelog')"]
> 2 failed, 71 passed in 25.25s

**Agent:** I'm checking that the new tests still fail on main for the right reason, then I'll write the review.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat dokima/release.py; rm -rf /tmp/m && mkdir /tmp/m && git archive main | tar -x -C /tmp/m && cp tests/test_release.py /tmp/m/tests/ && cd /tmp/m && python -m pytest -q tests/test_release.py 2>&1 | grep -E "Error|passed|failed" | sort | uniq -c | head
```

> """Make Dokima's release from the changelog, after each push to main (#755).
> 
>     python3 -m dokima.release <owner/repo> <commit>     # run from the repo root
> 
> When CHANGELOG.md holds a section for VERSION and GitHub has no VERSION release yet, makes the VERSION tag and its
> GitHub release at the commit, with that section as the release notes. With no changelog, no section, or the release
> already made, it makes nothing and exits 0. When GitHub refuses, it exits 1 and says why.
> """
> import re
> import subprocess
> import sys
> 
> VERSION = "v0.1.0"
> CHANGELOG = "CHANGELOG.md"
> 
> 
> def section(text, version):
>     """The lines under the heading naming version, up to the next as high; else None."""
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
>             return "\n".join(out).strip() + "\n"
>     return None
> 
> 
> def gh(*args):
>     """Runs gh, returning the finished process."""
>     return subprocess.run(["gh", *args], capture_output=True, text=True)
> 
> 
> def run(repo, sha, path=CHANGELOG, version=VERSION):
>     """Makes the release when it is due; returns the exit code."""
>     try:
>         with open(path) as f:
>             note

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner let the tag and release criteria change the permission list."],
  "decided": ["Release calls get a permission so the safety check accepts them."],
  "open": []
 },
 "verdict": "approve",
 "summary": "The plan now lets the worker give release calls a permission; every check still fails on main for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "A v0.1.0 tag", "source": "https://github.com/dokima-dev/dokima/issues/755", "criterion": "755.1"},
  {"ask": "GitHub release", "source": "https://github.com/dokima-dev/dokima/issues/755", "criterion": "755.2"},
  {"ask": "A workflow makes the tag ... when the changelog merges, not by hand", "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244761525", "criterion": "755.1"},
  {"ask": "A workflow makes ... the release when the changelog merges, not by hand", "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244761525", "criterion": "755.2"},
  {"ask": "the release notes are the changelog's v0.1.0 section", "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244761525", "criterion": "755.3"},
  {"ask": "this story keeps the workflow that tags and releases", "source": "https://github.com/dokima-dev/dokima/issues/755#issuecomment-6244851037", "criterion": "755.1"}
 ],
 "behaviors": [
  {"criterion": "755.1", "one_behavior": true, "why": "One result: the v0.1.0 tag at the pushed commit."},
  {"criterion": "755.2", "one_behavior": true, "why": "One result: a GitHub release named v0.1.0."},
  {"criterion": "755.3", "one_behavior": true, "why": "One result: the notes equal the v0.1.0 section."}
 ],
 "edge_cases": [
  {"criterion": "755.1", "cut": [], "missing": []},
  {"criterion": "755.2", "cut": [], "missing": []},
  {"criterion": "755.3", "cut": [], "missing": []}
 ],
 "tests": [
  {"test": "tests/test_release.py::test_release_mak
```

> summary holds 21 words, over its cap of 20 (up to 24 passes)

`8. Bash`
```
sed -i 's/"The plan now lets the worker give release calls a permission; every check still fails on main for the right reason."/"The plan now lets release calls get a permission; every check still fails on main for the right reason."/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 755 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

> rc=0

`9. Bash`
```
cd /home/runner/work/dokima/dokima && sed -i 's/"The plan now lets the worker give release calls a permission; every check still fails on main for the right reason."/"The plan now lets release calls get a permission; every check still fails on main for the right reason."/' /tmp/dokima-out/review.json && python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 755 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack; echo rc=$?
```

**Agent:** I approved the plan for [#755](https://github.com/dokima-dev/dokima/issues/755) (first release v0.1.0). The review is in `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **What changed since the last approval:** the code review on [#850](https://github.com/dokima-dev/dokima/pull/850) (the release pull request) found that release calls had no permission. The planner fixed that one thing: the tag and release criteria may now change the permission list (`dokima/manifest.py`). I logged the change as needed, not creep.
- **The owner's asks:** all six map to a criterion. These are the tag, the release, both made by a workflow when the changelog merges, and notes taken from the changelog's v0.1.0 section. The changelog itself moved to its own issue, [#849](https://github.com/dokima-dev/dokima/issues/849) (writing the changelog), as the owner asked.
- **Tests on main:** all 7 new tests fail for the right reason. Each one names its criterion and says the release workflow is missing.
- **Tests on this branch:** the 7 release tests pass. Two older tests fail:
  - `test_manifest.py`: the release calls aren't in the permission list yet. That's the gap this plan change lets the worker fill.
  - `test_settings_setup.py`: the workflow runs Dokima before installing the YAML reader. That's the worker's open blocker R4 from the code review.

There were no open blockers to answer, and I raised nothing new.

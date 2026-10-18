# reviewer (plan) for #867

Run: https://github.com/dokima-dev/dokima/actions/runs/39108066002

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #867: Adopters run v0.1.0 forever: Dokima can release nothing newer
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [746], "loop": []} -->
> Dokima can release only v0.1.0, so adopters never get later fixes.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/746
> 
> 
> **User story:** Adding a new version section to the changelog and merging it makes that release, and adopters run it.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the changelog's newest version heading names a version, a push to main makes that release.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-867/tests/test_newest_release.py#L46"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" align="absmiddle" alt="verified by"> Acceptance test</a>: With v0.2.0 newest in the changelog, a push to main releases v0.2.0.*
>   <details><summary><picture><img src="https://raw.githubusercontent.com/dokima-dev/merge-sandb

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_newest_release.py; cat dokima/release.py; python -m pytest -q tests/test_newest_release.py 2>&1 | tail -30; head -30 CHANGELOG.md; grep -n "v0.1" README.md docs/wiki/Installing.md dokima/install/dokima.yml; cat /tmp/pack/in/02-reviewer-plan.json | head -80
```

> """Tests for #867: each release takes its version from the changelog's newest version heading.
> 
> Before #867 the release command knew one version, v0.1.0, so Dokima could release nothing newer and adopters, whose
> install file calls Dokima at a release tag, never got a fix merged after it. Now the newest version heading of
> CHANGELOG.md (the top-most heading naming a version like v0.1.1) names the release, so adding a `## v0.1.1` section
> and merging it makes v0.1.1. The install file and the install docs name that same newest version.
> 
> The release tests run the command release.yml runs, against the fake `gh` of tests/test_release.py, in a temp folder
> holding a changelog, so nothing leaves the machine. The other tests read the repo's own CHANGELOG.md, install file,
> README and wiki install page, and check they agree on the newest version.
> """
> import os
> import re
> 
> import yaml
> 
> from tests.test_release import SHA, run_release
> 
> ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
> VERSION = re.compile(r"v(\d+)\.(\d+)\.(\d+)(?![0-9])")
> HEADING = re.compile(r"^(#{1,6})\s+.*?\b(v\d+\.\d+\.\d+)(?![0-9])")
> TWO = ("# Changelog\n\n## v0.1.1\n\n- Card updates find checks by the names GitHub shows.\n\n"
>        "## v0.1.0\n\n- Dokima's first version.\n")
> 
> 
> def read(rel):
>     """The text of a file in the repo, by its path from the root."""
>     with open(os.path.join(ROOT, rel)) as f:
>         return f.read()
> 
> 
> def newest_version(crit):
>     """The version named by CHANGELOG.md's top-mo

`3. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_newest_release.py 2>&1 | grep -E "^(FAILED|E )" | head -30; grep -n "^## " README.md; ls docs/wiki/Installing.md; grep -n "entry.yml\|@v\|release" README.md docs/wiki/Installing.md | head; grep -n "def run_release" -A30 tests/test_release.py | head -50; git diff main --stat
```

> E       AssertionError: 867.1: the changelog's newest version is v0.2.0, yet the release command made [], not v0.2.0
> E       assert [] == [('v0.2.0', '...def01234567')]
> E         
> E         Right contains one more item: ('v0.2.0', '0123456789abcdef0123456789abcdef01234567')
> E         
> E         Full diff:
> E         + []
> E         - [
> E         -     (
> E         -         'v0.2.0',
> E         -         '0123456789abcdef0123456789abcdef01234567',
> E         -     ),
> E         - ]
> E       AssertionError: 867.1: the changelog's newest version is v0.1.1, yet the release command made [], not v0.1.1
> E       assert [] == [('v0.1.1', '...def01234567')]
> E         
> E         Right contains one more item: ('v0.1.1', '0123456789abcdef0123456789abcdef01234567')
> E         
> E         Full diff:
> E         + []
> E         - [
> E         -     (
> E         -         'v0.1.1',
> E         -         '0123456789abcdef0123456789abcdef01234567',
> E         -     ),
> E         - ]
> E       AssertionError: 867.1: with Unreleased above v0.1.1, the release command made [], not v0.1.1
> E       assert [] == [('v0.1.1', '...def01234567')]
> E         
> E         Right contains one more item: ('v0.1.1', '0123456789abcdef0123456789abcdef01234567')
> 14:## Why δokima
> 20:## How it works
> 52:## What you see
> 96:## δokima builds itself
> 107:## Install
> 130:## Principles
> 143:## Status and roadmap
> 169:## License
> docs/wiki/Installing.md
> 186:def run_release(tmp_path, crit, releases=(), refuse=False, changelog=SAMPLE):
> 187-    """Run re

`4. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "^def test_\|SAMPLE = \|releases=\|changelog=" tests/test_release.py; grep -rn "VERSION\|v0\.1\.0" tests/*.py | grep -v test_newest_release | head -20
```

> 41:SAMPLE = "# Changelog\n\n## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n"
> 186:def run_release(tmp_path, crit, releases=(), refuse=False, changelog=SAMPLE):
> 212:def test_release_notes_are_changelog_section(tmp_path, record_property):
> 220:    done, state = run_release(tmp_path, "755.3", changelog=changelog)
> 232:def test_release_makes_tag(tmp_path, record_property):
> 245:def test_release_skips_when_tagged(tmp_path, record_property):
> 251:    done, state = run_release(tmp_path, "755.1", releases=["v0.1.0"])
> 257:def test_release_makes_github_release(tmp_path, record_property):
> 270:def test_release_refused_fails_the_run(tmp_path, record_property):
> 283:def test_release_waits_for_changelog(tmp_path, record_property):
> 289:    done, state = run_release(tmp_path, "755.1", changelog=None)
> 295:def test_release_waits_for_version_section(tmp_path, record_property):
> 301:    done, state = run_release(tmp_path, "755.1", changelog="# Changelog\n\n## Unreleased\n\n- A draft line.\n")
> tests/test_changelog.py:1:"""The repo's changelog lists what v0.1.0 does (#849).
> tests/test_changelog.py:4:CHANGELOG.md at the repo root and uses the section under the heading naming v0.1.0 as the release notes, so this test
> tests/test_changelog.py:5:reads the same file the same way: a heading naming v0.1.0, then the lines up to the next heading as high. The section
> tests/test_changelog.py:33:    """The changelog has a v0.1.0 section listing what that version does.

`5. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 530,575p tests/test_playthrough.py; grep -rn "v0\.1\.0\|0\.1\.0" dokima/ --include=*.py --include=*.yml | grep -v "^dokima/release.py" | head
```

> Proves 437.3.
>     card.yml always runs the default branch's copy of itself and of dokima/card.py, so the cards on card-gallery are
>     drawn by the commit played only once that commit is installed there. Since #813 an install is the thin workflow
>     and a settings file: checks install_files() gives the played folder's `dokima/install/dokima.yml` as
>     `.github/workflows/dokima.yml`, calling the played commit instead of its release tag, and its
>     `dokima/install/settings.yaml` as `.dokima/settings.yaml`, and nothing else; that play() installs
>     before it plays any step; that a refused install plays no step and returns 1 with one `FAIL: install` line giving
>     the reason; that a played folder with no dokima/ fails naming it before any gh or git call; that a real run
>     on the sandbox pushes with SANDBOX_TOKEN and, when GitHub refuses, exits 1 naming the commit and plays no step;
>     and that with SANDBOX_TOKEN unset or empty, as GitHub gives a secret that does not exist, the run makes no gh or
>     git call, logs one `FAIL: install` line naming SANDBOX_TOKEN, plays no step and exits 1."""
>     record_property("proves", "437.3")
>     p = playthrough("437.3")
>     played = tmp_path / "played"
>     thin = "jobs:\n  dokima:\n    uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.0\n    secrets: inherit\n"
>     for rel, text in (("dokima/card.py", "CARD of the played commit"), ("dokima/icons/x.svg", "<svg/>"),
>                       ("dokima/install/dokima.yml", thin), ("doki

**Agent:** I'm checking whether any other code hardcodes v0.1.0, which would break once the install file moves to a newer tag.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "0\.1\.0\|entry.yml@" --include=*.py --include=*.yml --include=*.md . | grep -v "^./tests/\|CHANGELOG\|^./\.git/" | head -20
```

> dokima/release.py:13:VERSION = "v0.1.0"
> dokima/install/dokima.yml:19:    uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.0
> tests/test_changelog.py:1:"""The repo's changelog lists what v0.1.0 does (#849).
> tests/test_changelog.py:5:reads the same file the same way: a heading naming v0.1.0, then the lines up to the next heading as high. The section
> tests/test_changelog.py:33:    """The changelog has a v0.1.0 section listing what that version does.
> tests/test_changelog.py:42:    section = changelog_section(text, "v0.1.0")
> tests/test_playthrough.py:544:    thin = "jobs:\n  dokima:\n    uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.0\n    secrets: inherit\n"
> tests/test_playthrough.py:554:    want = {".github/workflows/dokima.yml": thin.replace("@v0.1.0", "@" + commit),
> tests/test_release.py:1:"""Tests for #755: Dokima's first release, v0.1.0, with a changelog.
> tests/test_release.py:4:section becomes the notes of the v0.1.0 GitHub release.
> tests/test_release.py:8:with the changelog's v0.1.0 section as the release notes.
> tests/test_release.py:41:SAMPLE = "# Changelog\n\n## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n"
> tests/test_release.py:213:    """The v0.1.0 release's notes are the changelog's v0.1.0 section.
> tests/test_release.py:215:    755.3: runs the command release.yml runs on a changelog holding an Unreleased section above v0.1.0, and checks
> tests/test_release.py:216:    the notes it sends GitHub carry ev

`7. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Widened the release criterion to any newest version; its main test releases v0.2.0.",
   "Made the changelog test check the v0.1.1 section names #852, #856 and #861."
  ],
  "decided": [
   "Adds the v0.1.1 section in this change, as the owner answered."
  ],
  "open": []
 },
 "verdict": "approve",
 "summary": "Both blockers are fixed; every ask has a criterion and every new test fails today because the feature is missing.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "each release names its version from the changelog's newest version heading, so adding a `## v0.1.1` section and merging it makes v0.1.1", "source": "https://github.com/dokima-dev/dokima/issues/867", "criterion": "867.1"},
  {"ask": "Yes: this change also adds the v0.1.1 section, so merging it releases the fixes since v0.1.0.", "source": "https://github.com/dokima-dev/dokima/issues/867#issuecomment-6247154689", "criterion": "867.2"},
  {"ask": "the install file and the install docs name the newest release, and a test checks they match the changelog's newest version (install file)", "source": "https://github.com/dokima-dev/dokima/issues/867", "criterion": "867.3"},
  {"ask": "the install docs name the newest release (README install steps)", "source": "https://github.com/dokima-dev/dokima/issues/867", "criterion": "867.4"},
  {"ask": "the install docs name the newest release (wiki install page)", "source": "https://github.com/dokima-dev/dokima/issues/867", "criterion": "867.5"}
 ],
 "behaviors": [
  {"criterion": "867.1", "one_behavior": true, "why": "One action, a push, makes the newest changelog version's release."},
  {"criterion": "867.2", "one_behavior": true, "why": "One fixed state: v0.1.1 on top naming three fixes."},
  {"criterion": "867.3", "one_behavior": true, "why": "The install file's tag equals the newest version."},
  {"criterion": "867.4", "one_behavior": true, "why": "The REA
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#867](https://github.com/dokima-dev/dokima/issues/867) (Dokima can release nothing newer than v0.1.0). The hand-back is in `/tmp/dokima-out/review.json` and passes both checks.

- **Last round's two blockers are fixed.**
  - The release criterion now covers any newest version. Its main test releases v0.2.0, so a release hardcoded to one version would fail it.
  - The changelog test now checks that the v0.1.1 section names #852, #856 and #861.
- **The owner's answer is in the plan.** The plan adds the v0.1.1 section in this change, as the owner asked.
- **Every ask has a criterion.** The five criteria cover:
  - releasing from the changelog's newest version
  - the v0.1.1 section
  - the install file
  - the README's install steps
  - the wiki's install page
- **All 8 new tests fail today, each because the feature is missing.** None fails from a crash or a bad path.
- **No older test needs to change.** Nothing else in the code hardcodes v0.1.0. The playthrough test's v0.1.0 text is a made-up sample, not the real install file.

I raised nothing, and no open blockers were waiting for an answer.

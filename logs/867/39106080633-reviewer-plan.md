# reviewer (plan) for #867

Run: https://github.com/dokima-dev/dokima/actions/runs/39106080633

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
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 1 question](https://github.com/dokima-dev/dokima/issues/867#issuecomment-6246810853) with `/plan`, or say `/review`
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
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the changelog's newest version heading is v0.1.1, a push to main makes the v0.1.1 release.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-867/tests/test_newest_release.py#L46"><img src="https://raw.githubusercontent.com/dokima-de

`2. Bash`
```
cd /home/runner/work/dokima/dokima; cat tests/test_newest_release.py; cat dokima/release.py; head -40 CHANGELOG.md; cat dokima/install/dokima.yml; grep -n "v0.1" README.md docs/wiki/Installing.md; ls tests | grep -i release
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
cd /home/runner/work/dokima/dokima; grep -n "@v\|v0\.\|release" README.md docs/wiki/Installing.md | head -30; sed -n '/^## Install/,/^## /p' README.md | head -40; grep -n "def run_release" -A40 tests/test_release.py; grep -rn "release" .github/workflows/*.yml | head
```

> ## Install
> 
> > **Onboarding other repositories is in progress**, tracked in [#272](https://github.com/dokima-dev/dokima/issues/272) (one-link onboarding for any repo). Today δokima runs on its own repository. The list below is what that setup uses, for those who want to try it by hand.
> 
> Requirements:
> 
> - A GitHub repository with Actions enabled. Runs use your GitHub Actions minutes.
> - A GitHub App installed on the repo, with the permissions in [`dokima/app.json`](dokima/app.json). Agents act as this app, never as a person; it cannot approve.
> - A Claude subscription. Agents run Claude Code on GitHub-hosted runners.
> - Today the test runner is `pytest` on Python 3.12.
> 
> Setup:
> 
> 1. Add [`dokima/install/dokima.yml`](dokima/install/dokima.yml) to the repo as `.github/workflows/dokima.yml`. It runs δokima from this repo; nothing else of δokima is copied.
> 2. Add [`dokima/install/settings.yaml`](dokima/install/settings.yaml) to the repo as `.dokima/settings.yaml`, naming only what differs from the defaults.
> 3. Create an Actions environment named `keys` holding the secrets `DOKIMA_APP_KEY` (the app's private key) and `CLAUDE_CODE_OAUTH_TOKEN`.
> 4. Set the repo variable `DOKIMA_APP_ID`. Optionally set `DOKIMA_BOARD`.
> 5. Add `.github/CODEOWNERS` with a `*` line naming who may give commands and approve.
> 6. Protect `main`, requiring the checks `dokima / full-suite / all tests` and `dokima / acceptance-criteria / Acceptance criteria`. GitHub shows them under these full names, since they run ins

`4. Bash`
```
cd /home/runner/work/dokima/dokima; ls docs/wiki; grep -n "v0\|@\|tag" docs/wiki/Installing.md | head; python -m pytest -q tests/test_newest_release.py 2>&1 | tail -20; python -m pytest -q tests/test_release.py 2>&1 | tail -3
```

> Autopilot.md
> Commands.md
> FAQ.md
> Glossary.md
> Home.md
> How-it-works.md
> Installing.md
> The-card.md
> Writing-issues.md
> _Footer.md
> _Sidebar.md
>   - []
>   + [
>   +     (
>   +         'v0.1.0',
>   +         '0123456789abcdef0123456789abcdef01234567',
>   +     ),
>   + ]
> FAILED tests/test_newest_release.py::test_changelog_has_v011_on_top - AssertionError: 867.2: CHANGELOG.md has no v0.1.1 section; its version headings are ['v0.1.0']
> assert 'v0.1.1' in ['v0.1.0']
> FAILED tests/test_newest_release.py::test_install_file_calls_newest_version - AssertionError: 867.3: the install file still calls Dokima at v0.1.0, so adopters miss every fix merged since v0.1.0
> assert (<re.Match object; span=(0, 6), match='v0.1.0'> and (0, 1, 0) > (0, 1, 0))
>  +  where (0, 1, 0) = tuple(<map object at 0x7f73a12433a0>)
>  +    where <map object at 0x7f73a12433a0> = map(int, ('0', '1', '0'))
>  +      where ('0', '1', '0') = <built-in method groups of re.Match object at 0x7f73a122b8a0>()
>  +        where <built-in method groups of re.Match object at 0x7f73a122b8a0> = <re.Match object; span=(0, 6), match='v0.1.0'>.groups
> FAILED tests/test_newest_release.py::test_readme_names_newest_release - AssertionError: 867.4: the README's Install section never names v0.1.0, the newest release the install file calls
> assert 'v0.1.0' in []
> FAILED tests/test_newest_release.py::test_wiki_names_newest_release - AssertionError: 867.5: the wiki's Installing page never names v0.1.0, the newest release the install file calls
> assert 'v0.1.0' in []
> 7 

`5. Bash`
```
cd /home/runner/work/dokima/dokima; python -m pytest -q tests/test_newest_release.py 2>&1 | grep -E "FAILED|Error" | head -20; grep -n "def release_command" -A15 tests/test_release.py; cat .github/workflows/release.yml 2>/dev/null | tail -15
```

> E       AssertionError: 867.1: the changelog's newest version is v0.1.1, yet the release command made [], not v0.1.1
> tests/test_newest_release.py:55: AssertionError
> E       AssertionError: 867.1: with Unreleased above v0.1.1, the release command made [], not v0.1.1
> tests/test_newest_release.py:69: AssertionError
> E       AssertionError: 867.1: v0.1.1, the newest version, is already released, yet the command made [('v0.1.0', '0123456789abcdef0123456789abcdef01234567')]
> tests/test_newest_release.py:84: AssertionError
> E       AssertionError: 867.2: CHANGELOG.md has no v0.1.1 section; its version headings are ['v0.1.0']
> tests/test_newest_release.py:96: AssertionError
> E       AssertionError: 867.3: the install file still calls Dokima at v0.1.0, so adopters miss every fix merged since v0.1.0
> tests/test_newest_release.py:122: AssertionError
> E       AssertionError: 867.4: the README's Install section never names v0.1.0, the newest release the install file calls
> tests/test_newest_release.py:130: AssertionError
> E       AssertionError: 867.5: the wiki's Installing page never names v0.1.0, the newest release the install file calls
> tests/test_newest_release.py:130: AssertionError
> FAILED tests/test_newest_release.py::test_release_names_newest_version - AssertionError: 867.1: the changelog's newest version is v0.1.1, yet the release command made [], not v0.1.1
> FAILED tests/test_newest_release.py::test_release_newest_below_unreleased - AssertionError: 867.1: with Unreleased above v0.1.1, the 

**Agent:** Tests all fail for the right reasons. Checking the release workflow and the older release tests for conflicts.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; cat .github/workflows/release.yml | head -40; grep -n "def test_\|SAMPLE =" -A3 tests/test_release.py | head -60; grep -rn "VERSION\|release.run\|from dokima.release\|dokima import release" tests dokima --include=*.py | grep -v test_newest | head
```

> name: release
> on:
>   push:
>     branches: [main]
> permissions:
>   contents: write
> jobs:
>   release:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>       # Dokima's code from Dokima's own repo, at this workflow's commit, never the repo's own copy (#812).
>       - name: Dokima's code from Dokima's own repo
>         uses: actions/checkout@v5
>         with:
>           repository: dokima-dev/dokima
>           ref: ${{ job.workflow_sha }}
>           path: .dokima-code
>           sparse-checkout: dokima
>           persist-credentials: false
>       - name: Every Dokima step runs Dokima's code
>         run: |
>           rm -rf "$RUNNER_TEMP/dokima" && mv .dokima-code "$RUNNER_TEMP/dokima"
>           printf 'PYTHONPATH=%s\nPYTHONSAFEPATH=1\n' "$RUNNER_TEMP/dokima" >> "$GITHUB_ENV"
>       - uses: actions/setup-python@v6
>         with:
>           python-version: "3.12"
>       - run: python3 -m pip install -q pyyaml  # the settings reader (#794)
>       # Makes the tag and GitHub release once the changelog holds their section (#755).
>       - name: Release from the changelog
>         env:
>           GH_TOKEN: ${{ github.token }}
>         run: python3 -m dokima.release "${{ github.repository }}" "${{ github.sha }}"
> 41:SAMPLE = "# Changelog\n\n## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n"
> 42-
> 43-FAKE_GH = textwrap.dedent('''
> 44-    """A fake gh keeping GitHub's releases in the JSON file named by FAKE_GH_STATE."""
> --
> 212:def test_release_no

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn "v0\.1\.0" --include=* . 2>/dev/null | grep -v "^./.git/" | grep -v tests/test_newest | head -30
```

> CHANGELOG.md:5:## v0.1.0
> dokima/release.py:13:VERSION = "v0.1.0"
> dokima/install/dokima.yml:18:    uses: dokima-dev/dokima/.github/workflows/entry.yml@v0.1.0
> tests/test_release.py:1:"""Tests for #755: Dokima's first release, v0.1.0, with a changelog.
> tests/test_release.py:3:The changelog is CHANGELOG.md at the repo root, with a section for v0.1.0 listing what that version does; that
> tests/test_release.py:4:section becomes the notes of the v0.1.0 GitHub release.
> tests/test_release.py:7:reads CHANGELOG.md and, when its v0.1.0 has no release yet, makes the v0.1.0 tag and GitHub release at that commit,
> tests/test_release.py:8:with the changelog's v0.1.0 section as the release notes.
> tests/test_release.py:41:SAMPLE = "# Changelog\n\n## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n"
> tests/test_release.py:213:    """The v0.1.0 release's notes are the changelog's v0.1.0 section.
> tests/test_release.py:215:    755.3: runs the command release.yml runs on a changelog holding an Unreleased section above v0.1.0, and checks
> tests/test_release.py:216:    the notes it sends GitHub carry every v0.1.0 line and nothing from the other section."""
> tests/test_release.py:219:                 "## v0.1.0\n\n- Work starts with a comment: /plan, /work and /review.\n- One card on every issue.\n")
> tests/test_release.py:227:    assert not missing, f"755.3: the v0.1.0 release notes leave out these changelog lines: {missing}"
> tests/test_release.py:229:        

**Agent:** The new tests fail for the right reasons. I found two weak points to block on. Writing the review now.

`8. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": [
   "Wrote five criteria: release from the newest changelog version, v0.1.1 section, install file, README, wiki.",
   "Wrote seven new tests; all fail today because the feature is missing."
  ],
  "decided": [
   "Plans to add a v0.1.1 section so merging this ships the fixes."
  ],
  "open": [
   "Asks the owner whether this change should also ship v0.1.1."
  ]
 },
 "verdict": "block",
 "summary": "Release criterion only covers v0.1.1, not any newest version; the changelog test passes with any three lines.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "867.1 too narrow",
   "text": "The owner asked that each release take the newest changelog version; 867.1 and its tests only try v0.1.1. Code that hardcodes v0.1.1 passes all three. Fix: word 867.1 for any newest version and add a test where v0.2.0 sits above v0.1.1 and v0.1.0, expecting v0.2.0.",
   "evidence": "Issue: `each release names its version from the changelog's newest version heading`. Every changelog in `tests/test_newest_release.py` tops out at v0.1.1."
  },
  {
   "kind": "blocker",
   "to": "planner",
   "label": "867.2 weak test",
   "text": "The test for 867.2 passes with any three bullet lines under v0.1.1, so it does not prove the section lists the fixes. Fix: check the section names 852, 856 and 861, or mark 867.2 manual with a reason.",
   "evidence": "`tests/test_newest_release.py::test_changelog_has_v011_on_top` only counts items: `assert len(items) >= 3`."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "each release names its version from the changelog's newest version heading, so adding a `## v0.1.1` section and merging it makes v0.1.1", "source": "https://github.com/dokima-dev/dokima/issues/867", "criterion": "867.1"},
  {"ask": "every fix merged after v0.1.0 never reaches an adopter ... The trial (#746) would run without them.", "source": "https://github.com/dokima-dev
```

> Exit code 1
> raise 1's text holds 45 words, over its cap of 30: cut 15, keep the facts
> raise 2's text holds 38 words, over its cap of 30: cut 8, keep the facts

`9. Bash`
```
python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['text']="867.1 and its tests only try v0.1.1, so hardcoding v0.1.1 passes. Fix: word 867.1 for any newest version; test v0.2.0 above v0.1.1 makes v0.2.0."
r['raises'][1]['text']="The 867.2 test passes with any three bullet lines under v0.1.1. Fix: check the section names 852, 856 and 861, or mark it manual."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 867 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

`10. Bash`
```
cd /home/runner/work/dokima/dokima && python3 - <<'EOF'
import json
p='/tmp/dokima-out/review.json'; r=json.load(open(p))
r['raises'][0]['text']="867.1 and its tests only try v0.1.1, so hardcoding v0.1.1 passes. Fix: word 867.1 for any newest version; test v0.2.0 above v0.1.1 makes v0.2.0."
r['raises'][1]['text']="The 867.2 test passes with any three bullet lines under v0.1.1. Fix: check the section names 852, 856 and 861, or mark it manual."
json.dump(r,open(p,'w'),indent=1)
EOF
python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 867 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

**Agent:** I've blocked the plan for [#867](https://github.com/dokima-dev/dokima/issues/867) (Dokima can release nothing newer than v0.1.0) and sent it back to the planner with two fixes. The review is written to `/tmp/dokima-out/review.json` and passes both hand-back checks.

All seven new tests fail today because the feature is missing, not because of a crash or a bad path. The older release tests still pass and stay valid under the new behaviour.

**Blockers for the planner:**
1. **The release rule covers only v0.1.1.** You asked that each release take its version from the changelog's newest version heading. Criterion 867.1 and its three tests only try v0.1.1, so release code that simply hardcodes v0.1.1 would pass them. Fix: word the criterion for any newest version, and add a test where v0.2.0 sits above v0.1.1 and v0.1.0 and the release made is v0.2.0.
2. **The changelog test only counts lines.** `test_changelog_has_v011_on_top` passes with any three bullet lines under v0.1.1, so it doesn't prove the section lists the fixes. Fix: check the section names [#852](https://github.com/dokima-dev/dokima/issues/852) (checks found by shown names), [#856](https://github.com/dokima-dev/dokima/issues/856) (install docs) and [#861](https://github.com/dokima-dev/dokima/issues/861) (audit fix), or mark this criterion as checked by hand.

**Still waiting for you:** I didn't answer the planner's question for you: should this change also add the v0.1.1 section, so merging it ships the fixes? The plan assumes yes, but your issue gives "adding a `## v0.1.1` section" as an example, not an instruction. Shipping a release also changes what adopters run, so you need to decide. Criterion 867.2 depends on your answer. So does the part of 867.3 that requires the install file to call a version newer than v0.1.0.

Every other ask in the issue is carried by a criterion: the install file, the README and the wiki install page each name the changelog's newest version, with a test that checks they match. Each criterion is one behaviour and the size is fine.

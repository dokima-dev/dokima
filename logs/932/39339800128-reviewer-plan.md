# reviewer (plan) for #932

Run: https://github.com/dokima-dev/dokima/actions/runs/39339800128

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
> 01-worker.json
> 02-reviewer-pr.json
> 03-planner.json
> # Issue #932: Release v0.1.7: test baseline without tests, rejected-key message
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [], "loop": []} -->
> Cut release v0.1.7 naming both fixes merged since v0.1.6, so adopters can pin them.
> 
> **Plan**
> 
> https://github.com/dokima-dev/dokima/pull/933 · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/files-changed.svg" width="16" height="16" align="absmiddle" alt="files changed"> [files changed](https://github.com/dokima-dev/dokima/pull/933/files)
> 
> **User story:** Adopters pin v0.1.7 and get the test baseline fix and the rejected model key fix.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** When the changelog is read, its newest section is v0.1.7, right above v0.1.6.
>   *<a href="https://github.com/dokima-dev/dokima/blob/9f9ec289f5dec61faf5c310dde435d53a6bef75e/tests/test_newest_release.py#L179"><img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/verified-by.svg" width="16" height="16" 

`2. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -15 origin/main 2>/dev/null || git log --oneline -15 main; git tag | tail -3; git log --oneline v0.1.6..origin/main 2>&1 | head -20; cat /tmp/pack/owner_words.json | head -50; cat /tmp/pack/in/03-planner.json | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"
```

> c8826014 A rejected model key is reported as a rejected key (#931)
> 5583ee74 worker for #928 (run 39328705458) (#929)
> d40191a9 worker for #925 (run 39320267127) (#926)
> 4ecb8893 worker for #915 (run 39273974254) (#918)
> fd9b2ab4 Settings may name any agent key, but only declared names reach jobs; others fail as a missing key. (#911)
> c43cb768 Dokima's own problems file themselves into Dokima's repo (#872)
> 543002b4 Saving the conversation still asks origin for the records branch with no key, so private repos start an orphan branch each run. (#921)
> e12c2345 worker for #923 (run 39288577369) (#924)
> b64ba4cf worker for #919 (run 39276540907) (#920)
> 4f641e7d worker for #914 (run 39268948566) (#916)
> 73ba7bf3 The setup audit does not create the hotfix label, so a new repo lacks it. (#908)
> 37656f3a worker for #909 (run 39264571958) (#910)
> 24e6aa94 worker for #884 (run 39258793083) (#906)
> d9061dad worker for #885 (run 39258799651) (#905)
> 5695a04e Hotfix PRs labeled, design asks replanned, cards one line (#873)
> v0.1.4
> v0.1.5
> v0.1.6
> c8826014 A rejected model key is reported as a rejected key (#931)
> 5583ee74 worker for #928 (run 39328705458) (#929)
> {
>  "https://github.com/dokima-dev/dokima/issues/932": "Cut release v0.1.7 with the fixes merged since v0.1.6, so adopters can pin them:\n\n- #929 (#928): the test baseline passes, with a notice, on a repo that has no tests folder yet, and runs scoped to the settings' folder and file pattern.\n- #931 (#907): a model key the provider refuses ends th

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git log --oneline -6; git merge-base --is-ancestor c8826014 HEAD && echo has931; git diff 5583ee74 HEAD --stat; head -30 CHANGELOG.md; cat tests/test_newest_release.py
```

> 9f9ec289 planner for #932 (run 39339502317)
> d9aa3a27 Main's tests for the planner of #932
> 702b3d7e worker for #932 (run 39338486807)
> 5583ee74 worker for #928 (run 39328705458) (#929)
> d40191a9 worker for #925 (run 39320267127) (#926)
> 4ecb8893 worker for #915 (run 39273974254) (#918)
>  CHANGELOG.md                 |   6 +
>  README.md                    |   2 +-
>  docs/wiki/Installing.md      |   2 +-
>  dokima/install/dokima.yml    |   2 +-
>  tests/test_key_rejected.py   | 432 +++++++++++++++++++++++++++++++++++++++++++
>  tests/test_newest_release.py |  76 +++++++-
>  6 files changed, 515 insertions(+), 5 deletions(-)
> # Changelog
> 
> What each version of Dokima does.
> 
> ## v0.1.7
> 
> Test baseline on repos with no tests yet.
> 
> - The test baseline passes, with a notice, on a repo with no tests folder yet, and runs scoped to the settings' tests folder and file pattern (#929, #928).
> 
> ## v0.1.6
> 
> Scoped test runs, private-repo logs, declared keys and upstream filing.
> 
> - The all tests check and code review's test run collect only the settings' tests folder and file pattern; a repo with no tests folder passes as having no tests yet (#924, #923).
> - In a private repo, saving a run's conversation reads the records branch with the app's key, so logs append instead of being lost (#921, #917).
> - The test seed no longer leaves background git work or shared scratch folders, ending random "unable to write file" failures (#918, #915).
> - Settings may name only the agent keys entry.yml declares; any other name sto

`4. Bash`
```
cd /home/runner/work/dokima/dokima; git diff 5583ee74 HEAD -- tests/test_newest_release.py | head -60; python3 -m pytest -q tests/test_newest_release.py 2>&1 | tail -8; git diff 5583ee74 c8826014 --stat; git diff 5583ee74 c8826014 -- dokima/install/dokima.yml
```

> diff --git a/tests/test_newest_release.py b/tests/test_newest_release.py
> index 0a29804b..05a67592 100644
> --- a/tests/test_newest_release.py
> +++ b/tests/test_newest_release.py
> @@ -168,13 +168,85 @@ def test_changelog_has_v015_on_top():
>  
>  
>  def test_changelog_has_v016_on_top():
> -    """The changelog's newest section is v0.1.6, above v0.1.5, naming every fix merged since v0.1.5."""
> +    """The changelog's v0.1.6 section sits right above v0.1.5, naming every fix merged since v0.1.5."""
>      names, text = section("925", "v0.1.6")
> -    assert names[:2] == ["v0.1.6", "v0.1.5"], f"925: CHANGELOG.md's newest headings are not v0.1.6 then v0.1.5: {names}"
> +    i = names.index("v0.1.6")
> +    assert names[i + 1:i + 2] == ["v0.1.5"], f"925: CHANGELOG.md's v0.1.6 section is not right above v0.1.5: {names}"
>      missing = unnamed(text, ("#924", "#921", "#918", "#911", "#872"))
>      assert not missing, f"925: the v0.1.6 section does not name {missing}, fixes merged since v0.1.5"
>  
>  
> +def test_changelog_has_v017_on_top(record_property):
> +    """The changelog's newest section is v0.1.7, right above v0.1.6.
> +
> +    Proves 932.1: reads CHANGELOG.md's version headings in order and checks the first two are v0.1.7 then v0.1.6."""
> +    record_property("proves", "932.1")
> +    names, _ = section("932.1", "v0.1.7")
> +    assert names[:2] == ["v0.1.7", "v0.1.6"], \
> +        f"932.1: CHANGELOG.md's newest headings are not v0.1.7 then v0.1.6: {names}"
> +
> +
> +def fix_line(crit, numbers, others):
> +    """The on

`5. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "install" tests/test_key_rejected.py | head; grep -rln "CODEX_API_KEY" tests | head; rm -rf /tmp/mainwt; git worktree add -q /tmp/mainwt c8826014 && cp tests/test_newest_release.py /tmp/mainwt/tests/ && cd /tmp/mainwt && python3 -m pytest -q tests/test_newest_release.py 2>&1 | grep -E "FAILED|passed|failed"; cd -; git worktree remove --force /tmp/mainwt
```

> 325:    test also checks the audit workflow installs the agents before the audit runs, so a call can be made.
> 343:    assert any("dokima.agents install" in str(s.get("run", "")) for s in steps[:steps.index(run_step)]), \
> 344:        "907.5: the audit workflow never installs the agents before the audit runs, so no call can be made"
> 394:    The adopter's install file maps each of the three keys to Dokima by name, `entry.yml` passes each to the audit
> 400:    install = yaml.safe_load(open(os.path.join(ROOT, "dokima", "install", "dokima.yml")).read()) or {}
> 401:    given = {k: str(v).replace(" ", "") for j in (install.get("jobs") or {}).values()
> 404:    assert not missing, f"907.8: the adopter's install file never hands Dokima these agent keys by name: {missing}"
> tests/test_key_rejected.py
> tests/test_upstream.py
> tests/test_audit_secrets.py
> tests/test_agents.py
> tests/test_settings_setup.py
> tests/test_agent_codex.py
> tests/test_declared_keys.py
> tests/test_thin_install.py
> tests/test_settings_comments.py
> FAILED tests/test_newest_release.py::test_changelog_has_v017_on_top - AssertionError: 932.1: CHANGELOG.md has no v0.1.7 section; its headings are ['v0.1.6', 'v0.1.5', 'v0.1.4', 'v0.1.3', 'v0.1.2', 'v0.1.1', 'v0.1.0']
> FAILED tests/test_newest_release.py::test_changelog_v017_names_baseline_fix - AssertionError: 932.2: CHANGELOG.md has no v0.1.7 section; its headings are ['v0.1.6', 'v0.1.5', 'v0.1.4', 'v0.1.3', 'v0.1.2', 'v0.1.1', 'v0.1.0']
> FAILED tests/test_newest_release.py::test_change

**Agent:** Every new test fails on main for the right reason (no v0.1.7 yet), and the one older test was changed only to allow v0.1.7 on top. Writing the review now.

`6. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{"previous_step": {
  "did": ["The planner re-planned after the rejected key fix merged to main.",
          "It added a criterion for the rejected key fix line in the changelog."],
  "decided": ["Both fixes get their own changelog line, since both are now on main.",
              "The old newest-release check now lets v0.1.7 sit above v0.1.6."],
  "open": []},
 "verdict": "approve",
 "summary": "The plan covers every ask for release v0.1.7, and each test fails today for the right reason.",
 "raises": [],
 "answers": [],
 "asks": [
  {"ask": "Cut release v0.1.7 with the fixes merged since v0.1.6", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.1"},
  {"ask": "#929 (#928): the test baseline passes, with a notice, on a repo that has no tests folder yet", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.2"},
  {"ask": "#931 (#907): a model key the provider refuses ends the run as \"Model key rejected\"", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.3"},
  {"ask": "Anything else merged to main by the time this is built.", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.1"},
  {"ask": "a `## v0.1.7` heading at the top of CHANGELOG.md, newest above v0.1.6", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.1"},
  {"ask": "one line per fix", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.2"},
  {"ask": "the install file `dokima/install/dokima.yml`", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.4"},
  {"ask": "README", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.5"},
  {"ask": "docs/wiki/Installing.md point at `entry.yml@v0.1.7`", "source": "https://github.com/dokima-dev/dokima/issues/932", "criterion": "932.6"},
  {"ask": "the newest-release test names v
```

> (Bash completed with no output)

**Agent:** I approved the plan for release v0.1.7 ([#932](https://github.com/dokima-dev/dokima/issues/932), cut release v0.1.7). The review is in `/tmp/dokima-out/review.json` and passed both checks.

- **Every ask is covered.** All of the owner's asks map to one of the plan's six criteria: the v0.1.7 heading on top, one line each for the two fixes, and v0.1.7 named in the install file, the readme and the wiki install page.
- **Nothing else needs listing.** Only [#929](https://github.com/dokima-dev/dokima/pull/929) (test baseline fix) and [#931](https://github.com/dokima-dev/dokima/pull/931) (rejected model key fix) have merged to main since v0.1.6. So "anything else merged" adds no lines, and #931 is now on main, so it belongs in the release.
- **The new tests fail for the right reason.** On main, all six fail because there is no v0.1.7 yet. On this branch, only the rejected key line test fails, because that line is still missing.
- **The changed older test keeps its promise.** It now lets v0.1.7 sit on top, and still checks that v0.1.6 is right above v0.1.5 and names its fixes.
- **The install file conflict is guarded.** An existing test (907.8) fails if the worker drops the agent keys #931 added to the install file while fixing the clash.

I raised no blockers or questions.

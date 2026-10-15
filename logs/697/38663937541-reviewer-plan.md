# reviewer (plan) for #697

Run: https://github.com/dokima-dev/dokima/actions/runs/38663937541

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json; for f in in/*; do echo "== $f"; head -c 4000 $f; done
```

> .:
> in
> issue.md
> open_blockers.json
> open_issues.json
> parent.json
> plan.json
> 
> ./in:
> 01-planner.json
> # Issue #697: Setup gathers and stores a subscription's inputs
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [698, 699], "loop": []} -->
> A setup command takes a subscription's inputs once and puts each where runs find it.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/698
> - https://github.com/dokima-dev/dokima/issues/699
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/700
> 
> 
> **User story:** The owner gives a subscription's inputs once; setup stores the key or sign-in and writes the settings file.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** Setup lists the inputs a subscription needs: membership, region, sign-in or key, and model.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-697/te

`2. Bash`
```
cd /tmp/pack; python3 -c "
import json;d=json.load(open('parent.json'));print(json.dumps(d,indent=1)[:12000])"; cat open_issues.json | head -c 1500
```

> {
>  "number": 696
> }
> [
>  {
>   "number": 700,
>   "title": "A role can run on Codex CLI",
>   "summary": "The owner moves any role to Codex by naming a Codex subscription for it.",
>   "link": "https://github.com/dokima-dev/dokima/issues/700",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 699,
>   "title": "A role can run on Kimi Code CLI",
>   "summary": "The owner moves any role to Kimi by naming a Kimi subscription for it, and spends Kimi's credit.",
>   "link": "https://github.com/dokima-dev/dokima/issues/699",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 698,
>   "title": "One settings file and one agent interface",
>   "summary": "Each role runs on the subscription and model the owner declares in one file; Claude Code works as today.",
>   "link": "https://github.com/dokima-dev/dokima/issues/698",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 697,
>   "title": "Setup gathers and stores a subscription's inputs",
>   "summary": "A setup command takes a subscription's inputs once and puts each where runs find it.",
>   "link": "https://github.com/dokima-dev/dokima/issues/697",
>   "filed_by_dokima": true
>  },
>  {
>   "number": 696,
>   "title": "A settings file picks each role's agent and model",
>   "summary": "One settings file per repo says which subscription and model the planner, worker and reviewer use; Kimi first, then Codex.",
>   "link": "https://github.com/dokima-dev/dokima/issues/696",
>   "filed_by_dokima": false
>  },
>  {
>   "number": 694,
>   "title": "When the owner approves new scope raised on a child story

`3. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 20 gh issue view 696 --comments 2>&1 | head -150; git diff a2e94e1 --stat; cat tests/test_setup.py
```

> gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable. Example:
>   env:
>     GH_TOKEN: ${{ github.token }}
>  tests/test_setup.py | 328 ++++++++++++++++++++++++++++++++++++++++++++++++++++
>  1 file changed, 328 insertions(+)
> """Tests for #697: setup gathers a subscription's inputs and puts each where runs find it.
> 
> Setup is a command the owner runs once per subscription on their own machine, from the repo's root:
> 
>     python3 -m dokima.setup needs
>         lists the inputs a subscription needs.
>     python3 -m dokima.setup add SUB --agent AGENT --secret SECRET --model MODEL --role ROLE [--role ROLE ...] --key
>         reads the key from standard input and stores it as the repo secret SECRET.
>     python3 -m dokima.setup add SUB --agent kimi --secret SECRET --model MODEL --role ROLE --sign-in --region REGION
>         runs the agent's own login with the region, then stores the files it saved as the repo secret SECRET.
> 
> Either way it writes `.dokima/agents.yml` in the shape #698 reads, block style:
> 
>     subscriptions:
>       SUB:
>         agent: AGENT
>         key: SECRET
>     roles:
>       ROLE:
>         subscription: SUB
>         model: MODEL
> 
> A stored sign-in is the base64 text of a gzip tar of the files the login saved, each named by its path under the home
> folder (for Kimi `.kimi/credentials/...` and `.kimi/config.toml`, where Kimi's login keeps them), so a run can unpack it
> into its own home folder before the agent starts (#699).
> 
> Each test runs the real

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q tests/test_setup.py 2>&1 | grep -E "^E  .*69|passed|failed" | head -30; ls dokima/setup.py; ls .dokima 2>&1; grep -rn "agents.yml\|setup" rules/*.md | head
```

> E       AssertionError: 697.1: setup could not list the inputs a subscription needs.
> >       assert p.returncode == 0, f"697.2: setup failed while storing a key.\n{said(p)}"
> E       AssertionError: 697.2: setup failed while storing a key.
> E       AssertionError: 697.2: setup stores no secret even for a real key.
> E       AssertionError: 697.2: setup never tried to store the key with gh.
> E       AssertionError: 697.3: setup wrote no .dokima/agents.yml.
> >       assert first.returncode == 0, f"697.3: adding the first subscription failed.\n{said(first)}"
> E       AssertionError: 697.3: adding the first subscription failed.
> E       AssertionError: 697.4: setup never ran `kimi login --region cn`; kimi calls: []
> >       assert p.returncode == 0, f"697.5: setup failed while signing in.\n{said(p)}"
> E       AssertionError: 697.5: setup failed while signing in.
> ______________________ test_failed_sign_in_stores_nothing ______________________
> tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_failed_sign_in_stores_not0')
>     def test_failed_sign_in_stores_nothing(tmp_path, record_property):
> E       AssertionError: 697.5: setup never ran Kimi's login.
> E       AssertionError: 697.6: setup wrote no .dokima/agents.yml.
> FAILED tests/test_setup.py::test_key_stored_as_secret - AssertionError: 697.2: setup failed while storing a key.
> FAILED tests/test_setup.py::test_settings_keep_other_subscription - AssertionError: 697.3: adding the first subscription failed.
> FAILED tests/test_setup.py::tes

`5. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/dokima-out/review.json <<'EOF'
{
 "previous_step": {
  "did": ["The planner wrote six criteria and ten tests for a new setup command.", "All ten tests fail today because the setup command does not exist yet."],
  "decided": ["A sign-in is stored as one packed secret that a run can unpack.", "The settings file holds each secret's name, never the key."],
  "open": ["Nothing was raised for the owner."]
 },
 "verdict": "block",
 "summary": "One test for the subscription criterion also checks role lines, which belong to the roles criterion; move that check.",
 "raises": [
  {
   "kind": "blocker",
   "to": "planner",
   "label": "Test checks two criteria",
   "text": "The 697.3 test `test_settings_keep_other_subscription` also asserts the planner's role line survives, which is 697.6's behavior. Fix: move that assertion into a new 697.6 test, and list it as 697.6's edge case.",
   "evidence": "`tests/test_setup.py` lines 259-260 assert `roles.get(\"planner\")` inside a test that proves 697.3."
  }
 ],
 "answers": [],
 "asks": [
  {"ask": "grabbing the inputs a user needs for a subscription (membership, region, sign-in or key, model)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.1"},
  {"ask": "sign-in or key, model) and putting them in place (key)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.2"},
  {"ask": "`subscriptions` (agent, key)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.3"},
  {"ask": "signed in with `kimi login --region global`", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.4"},
  {"ask": "region, sign-in or key, model) and putting them in place (sign-in)", "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061", "criterion": "697.5"},
  {"ask": "`roles` (planner, 
```

> Exit code 1
> raise 1's text holds 31 words, over its cap of 30: cut 1, keep the facts

**Agent:** The review file is one word over the length limit, so I'm trimming it and running the check again.

`6. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/Fix: move that assertion into a new 697.6 test, and list/Fix: move that assertion into a new 697.6 test; list/' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 697 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n 'roles.get("planner")' tests/test_setup.py
```

> 260:    assert roles.get("planner") == {"subscription": "kimi-max", "model": "kimi-for-coding"}, \

`8. Bash`
```
cd /home/runner/work/dokima/dokima; sed -i 's/lines 259-260 assert/line 260 asserts/' /tmp/dokima-out/review.json; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 697 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I'm sending the plan for [#697](https://github.com/dokima-dev/dokima/issues/697) (setup gathers and stores a subscription's inputs) back to the planner with one blocker. The review is saved in `/tmp/dokima-out/review.json` and passes both checks.

**The blocker:** the test `test_settings_keep_other_subscription` belongs to criterion 697.3, which covers the subscription's entry in the settings file. At `tests/test_setup.py:260` it also checks that the planner's role entry is kept. Keeping roles is criterion 697.6's job, and the review rules say a plan can't be approved while a test checks another criterion's behavior.

- **Fix:** move that role check into a new test for 697.6.
- **Why it matters:** adding a second subscription without losing the roles set earlier is something the owner will normally do. 697.6 currently has no test of its own for it, so I listed it as a missing edge case there.

**What passed:**
- I ran all 10 new tests. Each fails today for the right reason: the setup command doesn't exist yet. None fail because of a crash or a bad path.
- Each of the six criteria is one behavior.
- Each test except the one above would fail if its behavior were missing or wrong. The empty-key test also runs a good key first as a control.
- Each owner ask I listed maps to a criterion, and none is missing. The planner raised no questions and there were no open blockers to answer.

**Not verified:**
- The owner's words are in a comment on parent issue [#696](https://github.com/dokima-dev/dokima/issues/696) (settings file picks each role's agent and model), which isn't in my pack. I couldn't reach GitHub, so I took the asks from the planner's quotes and the parent plan's story. I didn't read the owner's comment myself.
- The sign-in tests only cover Kimi. That fits "Kimi first, then Codex" in #696's summary, but I couldn't confirm whether the owner also expects Codex sign-in here. I didn't raise it, since I had no evidence either way.

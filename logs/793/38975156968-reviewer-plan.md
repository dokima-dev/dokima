# reviewer (plan) for #793

Run: https://github.com/dokima-dev/dokima/actions/runs/38975156968

`1. Bash`
```
cd /tmp/pack; cat issue.md; ls in; cat open_blockers.json; cat plan.json
```

> # Issue #793: Settings read from shipped defaults, merged and checked
> 
> <!-- dokima-card -->
> <!-- dokima-blocking: {"blocked_by": [], "blocks": [794], "loop": []} -->
> Dokima reads its shipped defaults, merges a repo's settings over them, warns on typos and refuses locked settings.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/794
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/779
> - https://github.com/dokima-dev/dokima/issues/740
> - https://github.com/dokima-dev/dokima/issues/741
> 
> 
> **User story:** A repo writes only what differs, and Dokima merges it over its defaults, warning on typos.
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/acceptance-criterion.svg" width="16" height="16" align="absmiddle" alt="acceptance criterion"> **Acceptance criteria**
> 
> - <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/none.svg" width="16" height="16" align="absmiddle" alt="not started"> **Acceptance criterion:** A repo with no settings file runs on Dokima's one shipped defaults file.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-793/tests/test_settings_merge.py#L70"><img src="https://

`2. Bash`
```
cd /tmp/pack/in; python3 -c "
import json
for f in ['02-reviewer-plan.json','03-planner.json']:
  d=json.load(open(f)); print(f, json.dumps(d,indent=1)[:5000])
"; cd /home/runner/work/dokima/dokima; git show --stat HEAD HEAD~1 | head -40
```

> 02-reviewer-plan.json {
>  "role": "reviewer",
>  "stage": "plan",
>  "run_id": "38973712331",
>  "commit_before": "ff3f3efe6572a21c7cfd7102b99ecedfe2f9903f",
>  "started_by": "dokima-runtime[bot]",
>  "models": [
>   "claude-opus-5-5"
>  ],
>  "report": {
>   "duration_ms": 74192,
>   "turns": 9,
>   "cost_usd": 0.5635076000000001,
>   "tokens_in": 417610,
>   "tokens_out": 6495
>  },
>  "log": "https://github.com/dokima-dev/dokima/blob/logs/logs/793/38973712331-reviewer-plan.md",
>  "run": "https://github.com/dokima-dev/dokima/actions/runs/38973712331",
>  "handback": {
>   "previous_step": {
>    "did": [
>     "The planner wrote ten criteria and seventeen tests for reading and merging settings.",
>     "Every test fails today because the settings reader does not exist."
>    ],
>    "decided": [
>     "The defaults test checks 32 settings rebuilt from earlier quotes of the owner's list.",
>     "The turn limit default is taken as 100."
>    ],
>    "open": [
>     "Three questions wait for the owner: the YAML reader, the full list, the turn limit."
>    ]
>   },
>   "verdict": "approve",
>   "summary": "The plan carries every ask with tests that fail for the right reason; three questions wait for you.",
>   "raises": [],
>   "answers": [],
>   "asks": [
>    {
>     "ask": "Dokima ships one defaults file that every repo's settings fall back to.",
>     "source": "https://github.com/dokima-dev/dokima/issues/740",
>     "criterion": "793.1"
>    },
>    {
>     "ask": "A repo's settings file changes only the settings it names; every other keeps its default."

`3. Bash`
```
cd /home/runner/work/dokima/dokima; git show HEAD -- tests | head -30; python3 -c "
import json;d=json.load(open('/tmp/pack/in/03-planner.json'));h=d['handback'];print(json.dumps({k:v for k,v in h.items() if k not in ('acceptance_criteria','tests')},indent=1)); print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:2000])"; cat tests/test_settings_merge.py
```

> commit 84dff82e10ec800fcef15e1145e629d3d140b920
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Fri Oct 16 22:20:06 2026 +0000
> 
>     planner for #793 (run 38974967291)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
> diff --git a/tests/test_settings_merge.py b/tests/test_settings_merge.py
> index 5c3f609..8513d8b 100644
> --- a/tests/test_settings_merge.py
> +++ b/tests/test_settings_merge.py
> @@ -56,7 +56,7 @@ def name(entry):
>  
>  
>  def probe_package(tmp_path, text):
> -    """A copy of Dokima whose defaults file holds TEXT; the folder to put on Python's path."""
> +    """A copy of Dokima whose defaults file holds TEXT; returns the folder for Python's path."""
>      pkg = tmp_path / "pkg"
>      shutil.copytree(os.path.join(ROOT, "dokima"), pkg / "dokima",
>                      ignore=shutil.ignore_patterns("__pycache__", "icons", "roles"))
> {
>  "kind": "user_story",
>  "title": "Settings read from shipped defaults, merged and checked",
>  "summary": "Dokima reads its shipped defaults, merges a repo's settings over them, warns on typos and refuses locked settings.",
>  "user_story": "A repo writes only what differs, and Dokima merges it over its defaults, warning on typos.",
>  "non_functional": [],
>  "test_changes": {},
>  "links": {
>   "blocked_by": [],
>   "blocks": [
>    794
>   ],
>   "relates_to": [
>    779,
>    740,
>    741
>   ]
>  },
>  "answers": []
> }
> {
>  "role": "planner",
>  "stage": null,
>  "run_id": "38974967291",
>  "co

`4. Bash`
```
cd /home/runner/work/dokima/dokima; python3 -m pytest -q -p no:cacheprovider tests/test_settings_merge.py 2>&1 | grep -E "^E .*79[0-9]\.|passed|failed" | head -40; python3 -c "import yaml" ; ls dokima/settings.py dokima/defaults.yaml
```

> Exit code 2
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.1: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.1: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.2: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.3: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.4: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.4: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.5: reading the settings failed (exit 1):
> >       assert code == 0 and isinstance(got, dict), f"{crit}: reading the settings failed (exit {code}):\n{err[-1500:]}"
> E       AssertionError: 793.5: readin

`5. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/pack; python3 - <<'EOF'
import json
prev=json.load(open('in/02-reviewer-plan.json'))['handback']
plan=json.load(open('plan.json'))
r={
 "previous_step":{
  "did":["The planner kept the same ten criteria and seventeen tests after the owner's answers.",
         "Only one test helper's description changed."],
  "decided":["The owner approved installing the YAML reader, the 32 rebuilt settings and 100 turns."],
  "open":[]},
 "verdict":"approve",
 "summary":"The plan carries every ask; all seventeen tests fail today because the settings reader does not exist.",
 "raises":[],"answers":[],
 "asks":prev["asks"],
 "behaviors":prev["behaviors"],
 "edge_cases":[{"criterion":f"793.{i}","cut":[],"missing":[]} for i in range(1,11)],
 "tests":[{"test":t,"only_its_behavior":True,"why":f"Runs the reader from outside and checks only {c}'s result."} for c,ts in plan["tests"].items() for t in ts],
 "size":"ok"}
json.dump(r,open('/tmp/dokima-out/review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 793 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack
```

> (Bash completed with no output)

**Agent:** I approved the plan for [#793](https://github.com/dokima-dev/dokima/issues/793) (settings read from shipped defaults, merged and checked). The review is in `/tmp/dokima-out/review.json`, and it passes both hand-back checks.

- **What changed since the last review:** you answered yes to all three questions, so the plan stands as it was. The planner made no real change; it only reworded the description of one test helper.
- **Tests:** I ran all seventeen. Every one fails today for the right reason: the settings reader `dokima/settings.py` and the defaults file `dokima/defaults.yaml` don't exist yet. Each failure names its criterion.
- **Your asks:** each of the ten is carried by exactly one criterion, and each criterion is one behavior.
- **Edge cases:** I found none missing and none to cut.
- **Size:** fine.
- **Raises:** I raised nothing new, and no earlier blockers were waiting for an answer.

One thing to expect at build time: criterion 793.1 lists four files under `.github/workflows/` to install the YAML reader. You approved that, but a pull request that touches those files will still stop for your approval.

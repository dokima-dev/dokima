# reviewer (plan) for #740

Run: https://github.com/dokima-dev/dokima/actions/runs/38860395665

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
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
> # Issue #740: One settings.yaml per repo over Dokima's shipped defaults
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 721, 739, 764 -->
> <!-- dokima-blocking: {"blocked_by": [739], "blocks": [741, 742, 743, 744], "loop": []} -->
> Each repo sets only what differs from Dokima's shipped defaults, in one settings file.
> 
> **Plan** · <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/needs-you.svg" width="16" height="16" align="absmiddle" alt="needs you"> Needs you: [answer 3 questions](https://github.com/dokima-dev/dokima/issues/740#issuecomment-6209321469) with `/plan`, or say `/review`
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/739
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/741
> - https://github.com/dokima-dev/dokima/issues/742
> - https://github.com/dokima-dev/dokima/issues/743
> - https://github.com/dokima-dev/dokima/issues/744
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.co

`2. Bash`
```
cd /tmp/pack; cat owner_words.json | head -50; cat parent.json | head -30; python3 -c "import json;d=json.load(open('in/01-planner.json'));print(json.dumps({k:v for k,v in d.items() if k!='handback'},indent=1)[:3000])"; cat /home/runner/work/dokima/dokima/rules/splitting.md
```

> {
>  "https://github.com/dokima-dev/dokima/issues/740": "Phase 1 of the portability plan (#272). Owner decisions of 2026-10-15.\n\n**What**\n- Dokima ships one defaults file. A repo overrides only what differs in `.dokima/settings.yaml`. Dokima's own repo becomes just another adopter with its own override file.\n- PyYAML is allowed (owner decision; lifts the no-new-dependency rule for this one library). Today's reader only handles flat key: value and cannot read lists (`setup.py:65`), and it rewrites the whole file on save (`setup.py:84`).\n- `.dokima/agents.yml` folds into `settings.yaml` under `agents:`. Old path keeps working for one version.\n- Every opinion specific to Dokima's own repo becomes a setting with a default: default branch, records branch, rules file name, bot identity, co-author trailer (#110), test install/run_all/run_one commands and test folder (#384), merge gate exclude list, merge queue (#375), labels, check names, turn limits and word caps, card icon source. Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.\n- Locked keys (integrity): app-only identity, keys only from main, fence, judge runs main's copy, owner approval by default. A repo cannot override them; trying fails the run.\n- Merge rules: maps merge key by key, repo wins; lists replace; `gates` and `prompts.append` merge by entry name. Unknown key warns with a suggestion and is ignored; never stops a run.\n- Exposure rule: expose repo facts, ta

`3. Bash`
```
cd /home/runner/work/dokima/dokima; grep -rn -i "split" rules/*.md | grep -v "^rules/splitting" | head -30; grep -rn -i "workflow" rules/identity.md rules/principles.md | head
```

> rules/commands.md:5:- `/plan`: the planner (re)plans. `/work`: the worker builds, or an approved split is filed. `/review`: the reviewer looks again; on an issue it grades the plan, on a PR the work.
> rules/commands.md:6:- `/autopilot start` / `/autopilot stop`: put the issue, or the issue a PR was built for, and every sub-issue under it at every level on or off autopilot (the `autopilot` label). It leaves one comment where it was said naming every issue it switched. `/autopilot start` picks up what is waiting: an approved plan of that issue still waiting for `/work` starts the worker, and an approved split not yet filed is filed, as on autopilot; the issue itself, with no sub-issues, no plan and nothing open to wait for, starts its planner with one line `Autopilot: switched on, starting plan` where the owner would have said `/plan`; every issue under it, at every level, with no sub-issues, no plan and nothing open to wait for starts its planner; and every pull request in the tree its code review approved merges as in step 6. When the issue's last run ended with no record (its live card still up, its run over), `/autopilot start` starts that run's stage again instead. A split filed by `/work` on autopilot puts its stories on autopilot and starts the ones with nothing to wait for.
> rules/flow.md:4:2. **`/plan`.** The planner always plans, naming the issue in ten plain words at most, on its best reading, and lists any questions with the reading it planned for. Too big: it propose

`4. Bash`
```
cd /home/runner/work/dokima/dokima; ls /tmp/study 2>&1; sed -n 55,100p dokima/setup.py; ls .dokima; cat .dokima/*; grep -n "dokima-runtime" dokima/*.py | head; grep -n "max-turns" dokima/*.py; git log --oneline | grep -E "#758|#773" ; cat /tmp/pack/open_issues.json | head -c 1500
```

> ls: cannot access '/tmp/study': No such file or directory
>     home = os.path.expanduser("~")
>     saved = [p for p in SIGN_IN[agent] if os.path.exists(os.path.join(home, p))]
>     if not saved:
>         raise Failed(f"The {agent} login saved none of {', '.join(SIGN_IN[agent])}, so no sign-in was stored.")
>     buf = io.BytesIO()
>     with tarfile.open(fileobj=buf, mode="w:gz") as t:
>         for p in saved:
>             t.add(os.path.join(home, p), arcname=p)
>     return base64.b64encode(buf.getvalue()).decode()
> 
> 
> def read_settings(text):
>     """Read the settings file's block maps (`subscriptions` and `roles`, two levels down) into nested dicts."""
>     root, stack = {}, [(-1, None)]
>     stack[0] = (-1, root)
>     for line in text.splitlines():
>         if not line.strip() or line.lstrip().startswith("#"):
>             continue
>         indent = len(line) - len(line.lstrip())
>         key, _, rest = line.strip().partition(":")
>         rest = rest.strip()
>         if rest[:1] in ("'", '"') and rest[0] in rest[1:]:
>             rest = rest[1:rest.index(rest[0], 1)]
>         else:
>             rest = re.split(r"\s#", " " + rest, maxsplit=1)[0].strip()
>         while stack[-1][0] >= indent:
>             stack.pop()
>         if rest:
>             stack[-1][1][key.strip()] = rest.strip("'\"")
>         else:
>             stack[-1][1][key.strip()] = {}
>             stack.append((indent, stack[-1][1][key.strip()]))
>     return root
> 
> 
> def write_settings(settings):
>     """The settings as block-style YAML text.""

`5. Bash`
```
mkdir -p /tmp/dokima-out; cd /tmp/dokima-out; python3 - <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/740"
plan=json.load(open('/tmp/pack/plan.json'))
false={("1",4):"Two results: comments kept, and other settings kept.",("5",6):"Two actions: adding the label, and reading it.",("5",7):"Two results: the merge gate follows, and the card follows."}
beh=[];edge=[]
for s,st in enumerate(plan["stories"],1):
    for k,c in enumerate(st["acceptance_criteria"],1):
        key=(str(s),k); cid=f"S{s}.{k}"
        if key in false: beh.append({"criterion":cid,"one_behavior":False,"why":false[key]})
        else: beh.append({"criterion":cid,"one_behavior":True,"why":"One action with one result the owner can see."})
        miss=["A repo with no settings file runs on the defaults alone."] if cid=="S1.2" else []
        edge.append({"criterion":cid,"cut":[],"missing":miss})
asks=[
("Dokima ships one defaults file.","S1.1"),
("A repo overrides only what differs in `.dokima/settings.yaml`.","S1.2"),
("Dokima's own repo becomes just another adopter with its own override file.","S2.1"),
("Today's reader only handles flat key: value and cannot read lists","S1.3"),
("it rewrites the whole file on save","S1.4"),
("`.dokima/agents.yml` folds into `settings.yaml` under `agents:`.","S1.5"),
("Old path keeps working for one version.","S1.6"),
("default branch","S5.1"),("records branch","S5.2"),("rules file name","S5.3"),("bot identity","S3.1"),
("co-author trailer (#110)","S1.15"),("test install/run_all/run_one commands","S1.16"),("test folder (#384)","S5.4"),
("merge gate exclude list","S1.17"),("merge queue (#375)","S5.5"),("labels","S5.6"),("check names","S5.7"),
("turn limits","S4.1"),("word caps","S5.8"),("card icon source","S5.9"),
("Full inventory: 41 OPTION rows in the sweep at /tmp/study/port/opinions.md and files_py.md on the box.","missing"),
("A repo cannot override them; trying fails the run.","S1.13"),
("maps merge key by key, repo wins","S1.7"),("lists repl
```

> Exit code 1
> raise 1's text holds 36 words, over its cap of 30: cut 6, keep the facts

**Agent:** Shortening one blocker that runs over the word cap, then checking again.

`6. Bash`
```
cd /tmp/dokima-out; python3 - <<'EOF'
import json
r=json.load(open('review.json'))
r["raises"][0]["text"]="The owner's 41-row settings list has no criterion; the plan carries only the named settings. Ask the owner for it, or carry each row."
r["raises"][1]["text"]="S1.4, S5.6 and S5.7 each promise two results. Split each: comments and settings kept; label added and read; merge gate and card."
json.dump(r,open('review.json','w'),indent=1)
EOF
cd /home/runner/work/dokima/dokima; python3 -m dokima.agent check review /tmp/dokima-out/review.json /tmp/pack/plan.json 740 && python3 -m dokima.agent check-round reviewer /tmp/dokima-out/review.json /tmp/pack && echo OK
```

> OK

**Agent:** I blocked the plan for [#740](https://github.com/dokima-dev/dokima/issues/740) (one settings file per repo). The review is in `/tmp/dokima-out/review.json` and passes both checks.

The planner split the work into five stories with 32 criteria. Each story's own planner writes its tests later, so this plan names no tests for me to run.

**Blockers sent back to the planner:**
1. **A list the owner gave is missing.** The issue points to a full list of 41 settings, but the plan only covers the settings the issue names one by one. That list sits outside the repo on a machine I can't see, so the planner should ask the owner for it or cover each item.
2. **Three criteria each promise two things.** Each needs to become two:
   - Saving keeps the comments, and saving keeps the other settings.
   - A renamed label is added, and it is read.
   - A renamed check is followed by the merge gate, and by the card.
3. **A common case is missing.** The default-handling criterion never mentions a repo that has no settings file at all, which every new repo starts as. It should run on the defaults alone.

**The planner's three questions are left for the owner.** The issue says to settle the file name itself, and the other two change how the system works. They are:
- Whether the file ends in `.yaml` or `.yml`.
- Whether the workflows start reading the co-author trailer and the test commands in [#742](https://github.com/dokima-dev/dokima/issues/742) (replaces the trailer) and [#744](https://github.com/dokima-dev/dokima/issues/744) (test commands in the workflows).
- Whether to plan no work for [#721](https://github.com/dokima-dev/dokima/issues/721) (inline comments) and [#515](https://github.com/dokima-dev/dokima/issues/515) (labels still starting agents). From the commit names, they look already fixed by [#758](https://github.com/dokima-dev/dokima/issues/758) and [#773](https://github.com/dokima-dev/dokima/issues/773).

Every other ask in the issue maps to a criterion.

# reviewer (plan) for #698

Run: https://github.com/dokima-dev/dokima/actions/runs/38674031695

`1. Bash`
```
cd /tmp/pack; ls -R; cat issue.md; cat plan.json; cat open_blockers.json
```

> <persisted-output>
> Output too large (44.5KB). Full output saved to: /home/runner/.claude/projects/-home-runner-work-dokima-dokima/5727170c-1d32-4e40-8ea3-bbd3d261cb6f/tool-results/bux3q29mc.txt
> 
> Preview (first 2KB):
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
> 02-reviewer-plan.json
> 03-planner.json
> # Issue #698: One settings file and one agent interface
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 697 -->
> <!-- dokima-blocking: {"blocked_by": [697], "blocks": [699, 700], "loop": []} -->
> A settings file names each role's subscription and model, and every agent runs behind one interface.
> 
> **Plan**
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocked-by.svg" width="16" height="16" align="absmiddle" alt="blocked by"> **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/697
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/blocks.svg" width="16" height="16" align="absmiddle" alt="blocks"> **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/699
> - https://github.com/dokima-dev/dokima/issues/700
> 
> <img src="https://raw.githubusercontent.com/dokima-dev/dokima/main/dokima/icons/related.svg" width="16" height="16" align="absmiddle" alt="related"> **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/696
> - https://github.com/dokima-dev/dokima/issues/39
> 
> 
> **User story:** Each role runs on the subscription and model the owner names in one file; Clau

`2. Bash`
```
cd /tmp/pack; sed -e 's/<img[^>]*>//g' issue.md
```

> # Issue #698: One settings file and one agent interface
> 
> <!-- dokima-card -->
> <!-- dokima-linked-from: 697 -->
> <!-- dokima-blocking: {"blocked_by": [697], "blocks": [699, 700], "loop": []} -->
> A settings file names each role's subscription and model, and every agent runs behind one interface.
> 
> **Plan**
> 
>  **Blocked by:**
> 
> - https://github.com/dokima-dev/dokima/issues/697
> 
>  **Blocks:**
> 
> - https://github.com/dokima-dev/dokima/issues/699
> - https://github.com/dokima-dev/dokima/issues/700
> 
>  **Relates to:**
> 
> - https://github.com/dokima-dev/dokima/issues/696
> - https://github.com/dokima-dev/dokima/issues/39
> 
> 
> **User story:** Each role runs on the subscription and model the owner names in one file; Claude Code works as today.
> 
>  **Acceptance criteria**
> 
> -  **Acceptance criterion:** Each repo keeps its agent settings in one file in its Dokima folder.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-698/tests/test_agents.py#L168"> Acceptance test</a>: The settings file in the repo's Dokima folder decides a role's model.*
>   - Edge cases: none, because Having no file at all is its own criterion.
>   - Source: https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061
> -  **Acceptance criterion:** A run's agent gets its key from the secret its role's subscription names.
>   *<a href="https://github.com/dokima-dev/dokima/blob/try/issue-698/tests/test_agents.py#L188"> Acceptance test</a>: A run's agent gets the key held in the secret its role's subscription names.*
>   - E

`3. Bash`
```
cd /tmp/pack; cat open_blockers.json; python3 -c "
import json;p=json.load(open('plan.json'))
print(json.dumps({k:v for k,v in p.items() if k not in ('criteria','acceptance_criteria')},indent=1)[:6000])
"; python3 -c "import json;print(list(json.load(open('plan.json')).keys()))"
```

> []{
>  "kind": "user_story",
>  "title": "One settings file picks each role's agent and model",
>  "summary": "A settings file names each role's subscription and model, and every agent runs behind one interface.",
>  "user_story": "Each role runs on the subscription and model the owner names in one file; Claude Code works as today.",
>  "non_functional": [
>   {
>    "text": "Subscriptions and roles sit in their own sections, so other settings can join the file.",
>    "why": "The owner expects the file to hold other settings later.",
>    "words": "Later it may expand into other settings.",
>    "source": "https://github.com/dokima-dev/dokima/issues/696",
>    "files": [
>     "dokima/agents.py"
>    ],
>    "no_edge_cases": "Other sections are the case itself."
>   }
>  ],
>  "tests": {
>   "698.1": [
>    "tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder"
>   ],
>   "698.2": [
>    "tests/test_agents.py::test_a_run_gets_its_key_from_the_secret_its_subscription_names"
>   ],
>   "698.3": [
>    "tests/test_agents.py::test_each_role_has_its_own_subscription_and_model"
>   ],
>   "698.4": [
>    "tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent"
>   ],
>   "698.5": [
>    "tests/test_agents.py::test_a_run_starts_with_the_model_the_file_names"
>   ],
>   "698.6": [
>    "tests/test_agents.py::test_with_no_settings_file_a_run_starts_claude_code_as_today"
>   ],
>   "698.7": [
>    "tests/test_agents.py::test_a_role_the_file_leaves_out_starts_claude_code_as_today"
>   ],
>   "698.8": [
>    "tests/test_ag

`4. Bash`
```
cd /tmp/pack; python3 -c "
import json;p=json.load(open('plan.json'))
for i,c in enumerate(p['acceptance_criteria'],1): print(i, json.dumps(c,indent=1))
"; cat parent.json | head -c 3000; echo; python3 -c "import json;d=json.load(open('in/02-reviewer-plan.json'));print(json.dumps(d,indent=1)[:8000])"
```

> 1 {
>  "text": "Each repo keeps its agent settings in one file in its Dokima folder.",
>  "words": "One structured file per repo, `.dokima/agents.yml`",
>  "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>  "files": [
>   "dokima/agents.py"
>  ],
>  "no_edge_cases": "Having no file at all is its own criterion."
> }
> 2 {
>  "text": "A run's agent gets its key from the secret its role's subscription names.",
>  "words": "`subscriptions` (agent, key)",
>  "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>  "files": [
>   "dokima/agents.py",
>   "dokima/agent_claude.py",
>   ".github/workflows/agent.yml"
>  ],
>  "no_edge_cases": "A missing secret fails inside the agent, as today."
> }
> 3 {
>  "text": "The planner, the worker and the reviewer each get their own subscription and model from the file.",
>  "words": "`roles` (planner, worker, reviewer: which subscription and model)",
>  "source": "https://github.com/dokima-dev/dokima/issues/696#issuecomment-6181290061",
>  "files": [
>   "dokima/agents.py"
>  ],
>  "no_edge_cases": "Left-out roles and bad names are their own criteria."
> }
> 4 {
>  "text": "A role may name any model; Dokima keeps no list of allowed models.",
>  "words": "Any agent, any model: planner, worker and reviewer each pick theirs.",
>  "source": "https://github.com/dokima-dev/dokima/issues/696",
>  "files": [
>   "dokima/agents.py",
>   "dokima/agent_claude.py"
>  ],
>  "no_edge_cases": "Any name passes; the agent itself refuses a model it lacks."
> }
> 5 {
>  "te

`5. Bash`
```
cd /home/runner/work/dokima/dokima; git log --stat -3 | head -40; wc -l tests/test_agents.py; ls dokima | head -80
```

> commit b152caa4ccb06c7d5ff9c5fa5e38d2bfdb8966b3
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 03:00:41 2026 +0000
> 
>     planner for #698 (run 38673559162)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_agents.py | 325 +++++++++++++++++++++++++++++++++++----------------
>  1 file changed, 226 insertions(+), 99 deletions(-)
> 
> commit 2b65f78a91042d81feed3ab9fc958efb8e91210f
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 02:51:24 2026 +0000
> 
>     planner for #698 (run 38671435872)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
> 
>  tests/test_agents.py     | 545 +++++++++++++++++++++++++++++++++++++++++++++++
>  tests/test_live_queue.py |   4 +-
>  tests/test_one_order.py  |   4 +-
>  tests/test_start.py      |  28 ++-
>  4 files changed, 569 insertions(+), 12 deletions(-)
> 
> commit cfb11e4519569d5ea3fdade9e1ce41dad37b38bd
> Author: dokima-runtime[bot] <337511017+dokima-runtime[bot]@users.noreply.github.com>
> Date:   Thu Oct 15 02:26:27 2026 +0000
> 
>     Setup gathers and stores a subscription's inputs (#702)
>     
>     * planner for #697 (run 38663459407)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.github.com>
>     
>     * planner for #697 (run 38664135620)
>     
>     Co-authored-by: Reza Soleymanifar <34189616+RezaSoleymanifar@users.noreply.gith

**Agent:** Reviewing the revised plan for #698: reading its tests now, then running them.

`6. Read`
```
/home/runner/work/dokima/dokima/tests/test_agents.py
```

> 1	"""Tests for #698: one settings file picks each role's agent and model, behind one interface.
> 2	
> 3	The settings file is `.dokima/agents.yml` in the repo's root, in the shape `python3 -m dokima.setup add` writes:
> 4	
> 5	    subscriptions:
> 6	      SUB:
> 7	        agent: AGENT      # the adapter dokima/agent_AGENT.py runs it
> 8	        key: SECRET       # the repo secret holding the subscription's key or sign-in
> 9	    roles:
> 10	      ROLE:               # planner, worker or reviewer
> 11	        subscription: SUB
> 12	        model: MODEL
> 13	
> 14	With no file, or for a role the file leaves out, a role runs on Claude Code with today's model, `claude-opus-5-5`, and
> 15	today's secret, CLAUDE_CODE_OAUTH_TOKEN. There is no fallback: a bad name stops the run, and a failed agent fails it.
> 16	
> 17	The one interface, `dokima/agents.py`, reads the file under the current folder:
> 18	
> 19	    python3 -m dokima.agents model ROLE              prints the model the role runs on
> 20	    python3 -m dokima.agents key ROLE                prints the name of the secret holding the role's key
> 21	    python3 -m dokima.agents install ROLE            installs the role's agent
> 22	    python3 -m dokima.agents run ROLE PROMPT_FILE OUT
> 23	        starts the role's agent with the prompt, the role's model and the key from DOKIMA_AGENT_KEY; its output goes
> 24	        into OUT, and its exit code is the agent's.
> 25	Each exits 1 with a message naming the bad name when the role names an unknown subscription or agent, or namin

`7. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "def __init__\|broken\|secrets\|def agent_started\|def posted\|agent-env\|agent-argv" tests/test_start.py | head -40; timeout 900 python -m pytest -q tests/test_agents.py -x -p no:cacheprovider 2>&1 | tail -5; timeout 1200 python -m pytest -q tests/test_agents.py -p no:cacheprovider 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed" | head -40
```

> 194:its own environment (agent-env.json), its arguments (agent-argv.json) and the time it started (agent-started-at), so
> 202:json.dump(dict(os.environ), open(os.path.join(d, "agent-env.json"), "w"))
> 203:json.dump(sys.argv[1:], open(os.path.join(d, "agent-argv.json"), "w"))
> 427:    def __init__(self, tmp, comments, try_branch=False, actor=OWNER, gh_fail="", broken=None, options=None, cancel_at=None,
> 438:        for name, message in (broken or {}).items():
> 570:    def posted(self):
> 584:    def agent_started(self):
> 597:    def __init__(self, tmp, role, stage, comments, try_branch=False, actor=OWNER, broken=None, options=None, review=None,
> 598:                 cancel_at=None, files=None, secrets=None):
> 599:        """Run agent.yml for ROLE at STAGE, with extra main files and repo secrets."""
> 600:        super().__init__(tmp, comments, try_branch, actor, broken=broken, options=options, cancel_at=cancel_at,
> 609:               "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k", **(secrets or {})),
> 626:    def __init__(self, tmp, body, comments, actor=OWNER, on_pr=False, gh_fail=""):
> 647:                       "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
> 765:    r = Run(tmp_path / "install", "worker", "", STORY_APPROVED, try_branch=True, broken={"pip": PIP_BROKEN})
> FAILED tests/test_agents.py::test_settings_come_from_one_file_in_the_dokima_folder - AssertionError: 698.1: with the settings file in .dokima/agents.yml the p

`8. Bash`
```
cd /home/runner/work/dokima/dokima; timeout 900 python -m pytest -q tests/test_agents.py -p no:cacheprovider 2>&1 | grep -E "^FAILED.*(19|20|21|22|model_runs|moving|failed_agent|other_sections)|passed|failed in"; sed -n 420,470p tests/test_start.py; sed -n 595,625p tests/test_start.py; grep -n "def evaluate\|\[\s*'\|def expr\|index\|__getitem__" tests/test_start.py | head -20
```

> _____________ test_any_model_the_role_names_is_passed_to_its_agent _____________
>     def test_any_model_the_role_names_is_passed_to_its_agent(record_property, tmp_path):
> E           "passed": true,
> E       assert 'no-such-sub' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" heig...ation](https://github.com/o/r/blob/logs/logs/57/42-reviewer-plan.md) · [run](https://github.com/o/r/actions/runs/42)\n'
> E           "passed": true,
> E       assert 'no-such-agent' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" heig...ation](https://github.com/o/r/blob/logs/logs/57/42-reviewer-plan.md) · [run](https://github.com/o/r/actions/runs/42)\n'
> FAILED tests/test_agents.py::test_any_model_the_role_names_is_passed_to_its_agent - AssertionError: 698.4: a model outside any list stopped the run instead of starting Claude Code: exit 1; stdout: ''; stderr: '/opt/hostedtoolcache/Python/3.12.15/x64/bin/python: No module named dokima.agents'; calls []
>     "passed": true,
> assert 'no-such-sub' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/passed.svg" width="16" heig...ation](https://github.com/o/r/blob/logs/logs/57/42-reviewer-plan.md) · [run](https://github.com/o/r/actions/runs/42)\n'
>     "passed": true,
> assert 'no-such-agent' in '<!-- dokima-record -->\n<img src="https://raw.githubusercontent.com/o/r/main/dokima/icons/p

`9. Bash`
```
cd /home/runner/work/dokima/dokima; sed -n 235,300p tests/test_start.py; git diff 2b65f78~1 -- tests/test_start.py | head -80
```

> NIL = Nil()
> 
> 
> class Ctx(dict):
>     """A GitHub expression context: dotted access, a missing key is Nil."""
>     def __getattr__(self, k):
>         v = self.get(k, NIL)
>         return Ctx(v) if isinstance(v, dict) and not isinstance(v, Ctx) else v
> 
>     def __getitem__(self, k):
>         """A name with a dash (`steps.card-key`), read the same way as a dotted one."""
>         return self.__getattr__(k)
> 
> 
> def evaluate(expr, ctx, status):
>     """Evaluate one GitHub expression against the contexts and the status so far (a step's job, or a job's needs)."""
>     parts = re.split(r"('[^']*')", expr)
>     for i in range(0, len(parts), 2):
>         p = parts[i].replace("&&", " and ").replace("||", " or ").replace("!=", "\0")
>         p = re.sub(r"!", " not ", p).replace("\0", "!=")
>         p = re.sub(r"\.([A-Za-z_]\w*(?:-\w+)+)", lambda m: f"[{m.group(1)!r}]", p)
>         p = re.sub(r"\bnull\b", "NIL", re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", p)))
>         parts[i] = p
>     names = {**ctx, "NIL": NIL, "always": lambda: True,
>              "success": lambda: status.get("success", not status["failed"] and not status.get("cancelled")),
>              "failure": lambda: status["failed"], "cancelled": lambda: bool(status.get("cancelled")),
>              "startsWith": lambda s, p: str(s).lower().startswith(str(p).lower()),
>              "contains": lambda s, p: str(p).lower() in str(s).lower(),
>              "format": lambda f, *xs: re.sub(r"\{(\d+)\}", lambda m: str(xs[int(m.group(1))]), f)}

`10. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "self.log\b\|self.log =\|self.log.append\|def tail\|failed_step" tests/test_start.py | head; grep -n "FAKE_REVIEW\|FAKE_GH_DIR" .github/workflows/agent.yml tests/test_start.py | head
```

> 479:        self.log, self.failed_step, self.cancelled_step = [], None, None
> 534:                self.log.append(f"## {name}: {label} (exit {p.returncode})\n{p.stdout[-1500:]}{p.stderr[-1500:]}")
> 544:                    self.log[-1] = self.log[-1].replace(f"(exit {p.returncode})", "(cancelled)", 1)
> 547:                    self.failed_step = self.failed_step or label
> 588:    def tail(self):
> 590:        first = [l for l in self.log if self.failed_step and f": {self.failed_step} (" in l.split("\n")[0]][:1]
> 591:        return "\n".join(first + self.log[-3:])[-3000:]
> 684:                               f"it stopped at '{r.failed_step}':\n{r.tail()}")
> 685:    assert not r.failed, f"176.1: the plan review of a split failed at '{r.failed_step}':\n{r.tail()}"
> 708:    assert r.agent_started(), f"176.2: the reviewer never reviewed the proposed split; it stopped at '{r.failed_step}':\n{r.tail()}"
> tests/test_start.py:62:d = os.environ["FAKE_GH_DIR"]
> tests/test_start.py:199:d = os.environ["FAKE_GH_DIR"]
> tests/test_start.py:209:shutil.copy(os.environ["FAKE_REVIEW"], os.path.join(os.environ["OUT"], "review.json"))
> tests/test_start.py:484:        return git_env({"PATH": f"{t}/bin:" + os.environ["PATH"], "HOME": f"{t}/home", "FAKE_GH_DIR": f"{t}/gh",
> tests/test_start.py:485:                        "FAKE_GH_FAIL": self.gh_fail, "FAKE_REVIEW": f"{t}/review.json", "FAKE_CLAUDE_MARK": f"{t}/claude-started",

`11. Bash`
```
cd /home/runner/work/dokima/dokima; grep -n "claude -p\|--max-turns\|npm install\|MODEL:\|claude.json" .github/workflows/agent.yml | head
```

> 59:      MODEL: claude-opus-5-5
> 253:          { pip install pytest pytest-xdist pytest-testmon && npm install -g @anthropic-ai/claude-code; } 2>&1 | tee /tmp/install.txt \
> 321:          claude -p "$(cat /tmp/runtime/dokima/roles/style.md /tmp/runtime/dokima/roles/$GRADE.md /tmp/runtime/dokima/roles/$ROLE.md)
> 334:            --model "$MODEL" --dangerously-skip-permissions --max-turns 60 --output-format json > "$OUT/claude.json"

**Agent:** Every new test fails today because the feature is missing. Writing the review now.

`12. Bash`
```
mkdir -p /tmp/dokima-out; cat > /tmp/gen.py <<'EOF'
import json
I="https://github.com/dokima-dev/dokima/issues/696"
C1=I+"#issuecomment-6181290061"; C2=I+"#issuecomment-6181845677"
p=json.load(open('/tmp/pack/plan.json'))
asks=[
("Each repo keeps its agent settings in one YAML file in its Dokima folder.",C1,"698.1"),
("The file lists subscriptions, each naming its agent and the secret holding its key.",C1,"698.2"),
("The file gives the planner, the worker and the reviewer each a subscription and a model.",C1,"698.3"),
("A role may name any model its agent takes; Dokima keeps no list of allowed models.",I,"698.4"),
("Each run starts the agent of its role's subscription, with the model the file names.",C2,"698.5"),
("With no settings file, every run starts Claude Code with today's model, as now.",C1,"698.6"),
("A role the file leaves out starts Claude Code with today's model, as now.",C1,"698.7"),
("A role naming an unknown subscription or agent stops before any agent starts, and the run names the bad name.",C2,"698.8"),
("Claude Code runs behind the one agent interface with the same command, record and stats as today.",C1,"698.14"),
("A model always runs in its own vendor's agent, never inside another vendor's agent.",C1,"698.19"),
("Moving a role to another subscription takes one edit: that role's lines in the file.",I,"698.20"),
("When a role's agent fails, the run fails; no other subscription takes over.",C2,"698.21"),
("Later it may expand into other settings.",I,"698.22"),
]
why={
"698.1":"The file's place decides the settings.","698.2":"The key comes from the named secret.",
"698.3":"One lookup per role.","698.4":"Any model name passes through.","698.5":"A run starts on the file's model.",
"698.6":"No file gives today's start.","698.7":"A left-out role gives today's start.",
"698.8":"An unknown subscription stops the run.","698.9":"The issue names the bad subscription.",
"698.10":"An unknown agent stops the run.","698.11":"The issue names the bad agent.",
"698.
```

> rc=0

**Agent:** I approved the revised plan for [#698](https://github.com/dokima-dev/dokima/issues/698) (one settings file picks each role's agent and model). The approval is saved to `/tmp/dokima-out/review.json`, and both hand-back checks pass.

- **Earlier blockers:** all four from the last review are fixed in the plan.
  - A real run now starts its agent through a stand-in agent's own adapter, and Claude Code never starts.
  - A real run now installs through the interface, and the old install step is not used.
  - The two criteria that each covered more than one thing are now split, one behavior and one test each.
  - A role with no model line now stops the run and names the role, and a fully written role in the same file still starts.
- **Tests:** I ran all 25 new tests on the branch, and all 25 fail. Each fails because the feature isn't built yet, not because of a crash or a broken setup.
- **Owner's asks:** I found 13 in [#696](https://github.com/dokima-dev/dokima/issues/696) (the parent issue) and its two comments. Each has a matching criterion, so none is missing.
- **Size:** each of the 22 criteria is one behavior. I found no unusual edge cases to cut and no everyday ones missing.

There were no open blockers to answer, and I raised nothing new. The problem the planner flagged earlier is already filed as [#706](https://github.com/dokima-dev/dokima/issues/706) (logs hide only Claude's key).

"""Run comments show only what carries weight for that step, with no codes (#236).

A run comment is what code posts when a planner, worker or reviewer run ends: `agent record ROLE STAGE OUT CHECK PASSED
LOGS` in dokima/agent.py writes OUT/record.json and OUT/comment.md. These tests draw comments with `agent.render`, and
run that command the way the workflow does (from the run's checkout, with $PACK, $BASE and $N set), then read the
comment the way the owner does. Every hand-back here has the shape the agents' prompts give today: raises and answers,
never a field retired by #300.

    a review            is called Plan review or Code review everywhere
    the planner's       never repeats the issue card (user story, criteria, scope, out of scope, tests, links); it
                        shows its sentence, its raises, its answers and its changes to older tests
    a review's          opens with passed, blocked or escalated, then each failing criterion of the plan (its sentence
                        behind the failed circle, each blocker's words behind the blocker icon, then its Source), then
                        each ask nothing covers, then Raised: its blockers, its questions, then its issues
    the worker's        shows the files it changed since $BASE as links on one line, never its per-criterion sentences
    answers             of the planner and the worker show in the same Raised earlier section as a review's
    every comment       folds its stats in a Stats fold right above the Full record fold, which stays last; token
                        counts read short (950, 12K, 3M)

"Visible" below means the comment without its Full record fold: the record holds every ID and number by design.
"""
import copy
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, card  # noqa: E402

REPO = "o/r"
SRC1 = "https://github.com/o/r/issues/77"
SRC2 = "https://github.com/o/r/issues/77#issuecomment-501"
SRC3 = "https://github.com/o/r/issues/77#issuecomment-502"
RECORD_FOLD = "<details><summary>Full record</summary>"
FOLD = re.compile(r"<details>.*?</details>", re.S)
META = {"run_id": "1", "run": "https://github.com/o/r/actions/runs/1", "log": "https://g/log.md",
        "models": ["claude-opus-5-5"],
        "report": {"duration_ms": 240000, "turns": 23, "cost_usd": 3.2, "tokens_in": 401000, "tokens_out": 18000}}
REPORT = {"duration_ms": 240000, "num_turns": 23, "total_cost_usd": 3.2,
          "usage": {"input_tokens": 1000, "cache_read_input_tokens": 400000, "output_tokens": 18000}}

PLAN = {"kind": "user_story", "summary": "Slow calls hand back a job id zq.",
        "user_story": "Callers get a job id for a slow call zq.",
        "acceptance_criteria": [{"text": "A slow call returns a job id within 2 s.", "source": SRC1},
                                {"text": "The job's result is kept for a day.", "source": SRC2},
                                {"text": "A finished job says done on its page.", "source": SRC3}],
        "non_functional": [{"text": "Jobs survive a restart of the server.", "why": "work is never lost zq",
                            "principle": "Fail closed"}],
        "scope": ["app/jobs.py"], "out_of_scope": ["Cancelling a job zq."],
        "tests": {"77.1": ["tests/test_jobs.py::test_fast"], "77.2": ["tests/test_jobs.py::test_kept"],
                  "77.3": ["tests/test_jobs.py::test_done"], "77.4": ["tests/test_jobs.py::test_restart"]},
        "test_changes": {}, "links": {"blocked_by": [14], "blocks": [15], "relates_to": [12]},
        "raises": [], "answers": []}
SENTENCES = [c["text"] for c in PLAN["acceptance_criteria"]] + [n["text"] for n in PLAN["non_functional"]]
PREVIOUS = {"did": ["Built the jobs queue zq."], "decided": ["Kept the old endpoint zq."], "open": ["The retry rule zq."]}
ASKS = [{"ask": "Give back a job id at once zq", "source": SRC1, "criterion": "77.1"},
        {"ask": "Keep each result for a day zq", "source": SRC2, "criterion": "77.2"},
        {"ask": "Email me when a job fails zq", "source": SRC3, "criterion": "missing"}]


def raised(kind, text, to=None, label=None, i="R1", by="reviewer"):
    """One raise as code stamps it: who raised it and its ID."""
    r = {"kind": kind, "text": text, "evidence": f"evidence of {i.lower()} zq", "raised_by": by, "id": i}
    if to:
        r["to"] = to
    if label:
        r["label"] = label
    return r


ON_2 = raised("blocker", "The test never waits a day, so a result dropped at noon still passes.", "worker", "77.2", "R1")
ON_2_TOO = raised("blocker", "Only one result is ever stored, so side by side is not tried.", "planner",
                  "Criterion 77.2", "R2")
ON_4 = raised("blocker", "No restart happens in the test, so a lost queue still passes.", "worker", "77.4", "R3")
OUTSIDE = raised("blocker", "app/extra.py changed, which the plan never names.", "worker", "Outside the plan", "R4")
QUESTION = raised("question", "Should a failed job retry by itself?", "owner", "Retries", "R5")
ISSUE = raised("issue", "The README still names the old endpoint.", None, "Docs", "R6")
ON_CRITERIA = [ON_2, ON_2_TOO, ON_4]
BLOCK = {"previous_step": PREVIOUS, "verdict": "block", "summary": "The plan misses an ask and two proofs are weak zq.",
         "raises": [ISSUE, ON_2, QUESTION, ON_2_TOO, OUTSIDE, ON_4], "answers": [], "asks": ASKS}
APPROVE = {"previous_step": PREVIOUS, "verdict": "approve", "summary": "Every ask is kept and proven zq.",
           "raises": [], "answers": [], "asks": ASKS[:2]}
ESCALATE = dict(BLOCK, verdict="escalate", summary="The two sides disagree on whether a day means 24 hours zq.")
WORK = {"summary": "The calls blocked the server, so they now run as jobs.",
        "criteria": {"77.1": "submit() returns the id at once zq"}, "evidence": "python3 -m pytest -q: 12 passed in 3.1s",
        "raises": [], "answers": []}


def rec(role, stage, handback, passed=True, problems=()):
    """One record as the record step builds it."""
    return {"role": role, "stage": stage or None, **copy.deepcopy(META), "handback": copy.deepcopy(handback),
            "check": {"passed": passed, "problems": list(problems) if not passed else []}}


@pytest.fixture
def env(monkeypatch):
    """The repo and run the workflow sets, which icons and links are drawn from."""
    for k, v in {"GITHUB_REPOSITORY": REPO, "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "1"}.items():
        monkeypatch.setenv(k, v)


def git(cwd, *args):
    """Run git in `cwd` and return what it printed."""
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def run(tmp_path, monkeypatch, env):
    """A run's machine: a checkout on try/issue-77, a pack with the plan, the record step.

    Returns a function that writes a hand-back as an agent writes it (no stamped raise fields), runs `agent record`
    the way the workflow does and gives back the
    comment and the record."""
    repo = tmp_path / "repo"
    (repo / "app").mkdir(parents=True)
    for name in ("jobs.py", "keep.py", "page.py"):
        (repo / "app" / name).write_text(f"# {name}\n")
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "checkout", "-q", "-b", "try/issue-77")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "start")
    pack = tmp_path / "pack"
    (pack / "in").mkdir(parents=True)
    (pack / "plan.json").write_text(json.dumps(PLAN))
    for k, v in {"PACK": str(pack), "BASE": git(repo, "rev-parse", "HEAD"), "N": "77",
                 "LOG_URL": "https://g/log.md"}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.chdir(repo)
    count = [0]

    def record(role, stage, handback, passed=True, problems=""):
        count[0] += 1
        monkeypatch.setenv("STAGE", stage)
        out, logs = tmp_path / f"out{count[0]}", tmp_path / f"logs{count[0]}"
        out.mkdir()
        logs.mkdir()
        (logs / "s.jsonl").write_text(json.dumps({"message": {"model": "claude-opus-5-5"}}) + "\n")
        handback = copy.deepcopy(handback)
        for r in handback.get("raises") or []:
            for stamped in ("raised_by", "id"):
                r.pop(stamped, None)
        (out / agent.HANDBACK[role]).write_text(json.dumps(handback))
        (out / "claude.json").write_text(json.dumps(REPORT))
        (out / "check.txt").write_text(problems)
        agent.main(["agent", "record", role, stage, str(out), str(out / "check.txt"), "true" if passed else "false",
                    str(logs)])
        return (out / "comment.md").read_text(), json.load(open(out / "record.json"))
    record.repo, record.pack = repo, pack
    return record


def visible(body):
    """The comment as the owner reads it: everything but the Full record fold."""
    head, _, rest = body.partition(RECORD_FOLD)
    return head + rest.partition("</details>")[2]


def plain(text):
    """Text as plain words: no tags, bold, code marks or link targets."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text.replace("**", "").replace("`", "")).strip()


def first_line(body):
    """The comment's first line after its marker, as plain words."""
    lines = [l for l in body.split(agent.MARK, 1)[-1].splitlines() if l.strip()]
    return plain(lines[0]) if lines else ""


def img(field):
    """A field's icon exactly as code draws it."""
    return card.field_icon(REPO, field)


def failed_circle():
    """The failed circle exactly as the issue card draws it."""
    return card.circle(REPO, "failed")


def headings(text, title):
    """The indexes of every heading line whose bold text is exactly `title`.

    Icons are allowed in front of the bold text."""
    pat = re.compile(r"\s*(<img[^>]*>\s*)*\*\*" + re.escape(title) + r"\*\*\s*")
    return [i for i, l in enumerate(text.splitlines()) if pat.fullmatch(l)]


def section(text, title):
    """The items under the heading `title`, each as its lines; None without that heading."""
    lines, at = text.splitlines(), headings(text, title)
    if not at:
        return None
    items = []
    for l in lines[at[0] + 1:]:
        if l.startswith("- "):
            items.append([l])
        elif l[:1].isspace() and l.strip() and items:
            items[-1].append(l)
        elif l.strip():
            break
    return items


def item_of(text, needle):
    """The list item whose first line holds `needle`, as its lines.

    An item is a "- " line with the lines indented under it."""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.lstrip().startswith("- ") and needle in l:
            out, depth = [l], len(l) - len(l.lstrip())
            for m in lines[i + 1:]:
                if m.strip() and len(m) - len(m.lstrip()) > depth:
                    out.append(m)
                elif m.strip():
                    break
            return out
    return None


def stats_fold(body):
    """The stats line, the comment's last line (#416), and what lies between the Full record fold and it, Next aside.

    Both are None when there is no stats line."""
    if agent.STATS not in body:
        return None, None
    head, _, tail = body.rpartition(agent.STATS)
    between = head.partition(RECORD_FOLD)[2].partition("</details>")[2]
    between = re.sub(r"\*\*Next:\*\*.*", "", between)
    return tail.strip(), between


# 236.1: Plan review and Code review

def test_review_runs_are_called_plan_review_and_code_review(record_property, run):
    """A review's live card and run comment say Plan review or Code review.

    Draws the live card of a plan review and a code review in every state, and the run comment of each review that
    passes, blocks, escalates, is rejected, is cancelled after or before its agent started, and never starts; each
    names its own review and never the other, Reviewer (...) or The reviewer, where the owner reads it. A planner's
    and a worker's live cards keep their names. A code review's queued live card still makes the card show Code
    review running, as dokima/card.py and .github/workflows/card.yml read it, and a plan review's never does.

    Proves 236.1."""
    record_property("proves", "236.1")
    for stage, name, other in (("plan", "Plan review", "Code review"), ("pr", "Code review", "Plan review")):
        for state, ahead in (("queued", None), ("queued", "https://x/run/0"), ("handoff", None), ("setup", None),
                             ("working", None), ("checking", None)):
            live = agent.live_card("reviewer", stage, state, ahead)
            seen = re.sub(r"<!--.*?-->", "", live, flags=re.S)
            assert f"**{name}**" in seen, f"236.1: the {state} live card of a {stage} review does not say {name}:\n{live}"
            assert "Reviewer (" not in seen and other not in seen, \
                f"236.1: the {state} live card of a {stage} review still says Reviewer (...) or {other}:\n{live}"
        bodies = [("passing", run("reviewer", stage, APPROVE)[0]), ("blocking", run("reviewer", stage, BLOCK)[0]),
                  ("escalating", run("reviewer", stage, ESCALATE)[0]),
                  ("rejected", run("reviewer", stage, BLOCK, passed=False, problems="a problem\n")[0]),
                  ("cancelled", agent.render(agent.cancelled("reviewer", stage, True, META))),
                  ("cancelled before it started", agent.render(agent.cancelled("reviewer", stage, False, META))),
                  ("never started", agent.render(agent.not_started("reviewer", stage, "the pack failed", META)))]
        for what, body in bodies:
            first = first_line(body)
            assert name in first, f"236.1: the {what} {stage} review's comment does not open naming {name}: {first!r}"
            words = plain(visible(body))
            for wrong in ("Reviewer (", "The reviewer", "the reviewer", other):
                assert wrong not in words, f"236.1: the {what} {stage} review's comment still says {wrong!r}:\n{words}"
    queued = agent.live_card("reviewer", "pr", "queued")
    bot = {"author": {"login": agent.BOT}, "body": queued}
    assert card.review_running([bot]), "236.1: the card no longer sees a code review running from its queued live card"
    yml = open(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "card.yml")).read()
    for wanted in re.findall(r"\*'(\*\*[^']+\*\*)'\*", yml):
        assert wanted in queued, f"236.1: card.yml looks for {wanted} on a code review's live card, which no longer holds it"
    assert not card.review_running([{"author": {"login": agent.BOT}, "body": agent.live_card("reviewer", "plan", "queued")}]), \
        "236.1: the card takes a plan review's live card for a code review running"
    assert "**Planner**" in agent.live_card("planner", "", "working"), "236.1: the planner's live card lost its name"
    assert "**Worker**" in agent.live_card("worker", "", "working"), "236.1: the worker's live card lost its name"


# 236.2: the planner's comment never repeats the card

def test_the_planners_comment_never_repeats_the_card(record_property, env):
    """The planner's comment shows what this run changed and raised, never the card.

    Draws a plan with a user story, criteria, a non-functional requirement, scope, out of scope, tests, links, one
    raise and one change to an older test, and checks the visible comment shows none of the card's parts (no user
    story, no criterion, no scope or out of scope, no test it lists, no Blocked by, Blocks or Relates to line) while it
    does show the raise and the change to the older test with its reason. A split still lists its stories.

    Proves 236.2."""
    record_property("proves", "236.2")
    hb = dict(PLAN, raises=[raised("question", "Should a job expire after a day zq?", "owner", "Expiry", "P1", "planner")],
              test_changes={"tests/test_old.py::test_waits": "It waited an hour; the owner asked for a day zq."})
    body = agent.render(rec("planner", "", hb))
    text = visible(body)
    words = plain(text)
    for part, said in [("user story", PLAN["user_story"]), ("scope", "app/jobs.py"), ("out of scope", "Cancelling a job zq."),
                       ("the non-functional reason", "work is never lost zq")] + \
                      [("criterion", s) for s in SENTENCES] + \
                      [("test", t.partition("::")[2]) for ts in PLAN["tests"].values() for t in ts]:
        assert said not in words, f"236.2: the planner's comment repeats the card's {part}: {said!r}\n{text}"
    for label in ("Blocked by", "Blocks", "Relates to", "Acceptance criteria", "User story", "Scope", "Out of scope",
                  "Non-functional requirements", "Definition of Done"):
        assert not re.search(r"\*\*" + label + r":?\*\*|<b>" + label + r"</b>", text), \
            f"236.2: the planner's comment repeats the card's {label}:\n{text}"
    for n in ("#12", "#14", "#15"):
        assert n not in words, f"236.2: the planner's comment repeats the card's link to {n}:\n{text}"
    for said in ("Should a job expire after a day zq?", "tests/test_old.py::test_waits",
                 "It waited an hour; the owner asked for a day zq."):
        assert said in words, f"236.2: the planner's comment does not show what this run raised or changed: {said!r}\n{text}"
    split = {"kind": "feature", "summary": "Jobs split in two zq.", "feature": "Jobs zq.", "raises": [], "answers": [],
             "stories": [{"title": "Queue the jobs zq", "user_story": "x", "acceptance_criteria": [], "depends_on": []},
                         {"title": "Show the jobs zq", "user_story": "y", "acceptance_criteria": [], "depends_on": [0]}]}
    words = plain(visible(agent.render(rec("planner", "", split))))
    assert "Queue the jobs zq" in words and "Show the jobs zq" in words, f"236.2: a split no longer lists its stories:\n{words}"


def test_a_planners_comment_with_nothing_raised_or_changed_shows_no_empty_part(record_property, env):
    """A plan that raised and changed nothing shows no heading or fold for them.

    Draws a plan with no raises, no answers and no changes to older tests, and checks its visible comment holds no
    Raised heading, no Test changes words and no fold but the Stats fold and the Full record.

    Proves 236.2."""
    record_property("proves", "236.2")
    body = agent.render(rec("planner", "", PLAN))
    text = visible(body)
    assert not headings(text, "Raised:") and not headings(text, "Raised earlier:"), \
        f"236.2: a plan that raised and answered nothing shows a Raised heading:\n{text}"
    assert "Test changes" not in text, f"236.2: a plan with no changes to older tests shows Test changes:\n{text}"
    folds = re.findall(r"<summary>(.*?)</summary>", body, re.S)
    assert folds == ["Full record"] and stats_fold(body)[0], \
        f"236.2: a plan with nothing to fold shows folds other than Stats and Full record: {folds}\n{body}"


# 236.3: a review shows its verdict, then only what fails

def test_a_blocking_review_lists_only_the_failing_criteria_with_why_and_source(record_property, env):
    """A blocking review lists each failing criterion with why it fails and its Source.

    Draws a code review that blocks on 77.2 twice and on 77.4, and checks each failing criterion shows once, as an
    item opening with the failed circle and its sentence from the plan, with each of its blockers' words behind the
    blocker icon under it and then its Source (none for the non-functional 77.4); 77.1 and 77.3, which pass, never
    show; and no criterion number, raise ID or label naming a criterion shows anywhere visible.

    Proves 236.3."""
    record_property("proves", "236.3")
    body = agent.render(rec("reviewer", "pr", BLOCK), plan=PLAN)
    text = visible(body)
    for sentence, blockers, source in ((SENTENCES[1], [ON_2, ON_2_TOO], SRC2), (SENTENCES[3], [ON_4], None)):
        assert text.count(sentence) == 1, f"236.3: the failing criterion {sentence!r} must show exactly once:\n{text}"
        item = item_of(text, sentence)
        assert item and failed_circle() in item[0], \
            f"236.3: the failing criterion {sentence!r} does not open with the failed circle:\n{item}"
        under = item[1:]
        for b in blockers:
            assert any(b["text"] in l and img("blocker") in l for l in under), \
                f"236.3: under {sentence!r} there is no line with the blocker icon and why it fails ({b['text']!r}):\n{item}"
        sources = [l for l in under if "Source:" in l]
        if source:
            assert len(sources) == 1 and source in sources[0], f"236.3: {sentence!r} does not end with its Source {source}:\n{item}"
            assert under.index(sources[0]) == len(under) - 1, f"236.3: the Source of {sentence!r} is not its last line:\n{item}"
        else:
            assert not sources, f"236.3: the non-functional {sentence!r} shows a Source it does not have:\n{item}"
    for passing in (SENTENCES[0], SENTENCES[2]):
        assert passing not in text, f"236.3: the review lists {passing!r}, which passed:\n{text}"
    assert not re.search(r"(?<![\d.])77\.\d(?![\d])", text), f"236.3: a criterion number shows in the review:\n{text}"
    assert not re.search(r"\bR\d\b|\bB\d\b", text), f"236.3: a raise ID or blocker code shows in the review:\n{text}"
    assert "Criterion 77.2" not in text, f"236.3: a blocker's label naming a criterion shows:\n{text}"


def test_a_review_opens_with_its_verdict_then_the_owners_order(record_property, env):
    """A review opens with its verdict, then failing criteria, uncovered asks and Raised.

    Draws a blocking plan review and checks its first line says blocked (and neither passed nor escalated), then the
    failing criteria come before the ask nothing covers (the ask, Nothing covers this and its Source), which comes
    before Raised; Raised holds only the review's other raises, its blocker first, then its question, then its issue,
    though the hand-back lists them the other way; the asks the plan keeps never show. A passing and an escalating
    review open with passed and escalated. A blocker naming no criterion of the plan, or any blocker when there is
    no plan to read, still shows in Raised behind the blocker icon.

    Proves 236.3."""
    record_property("proves", "236.3")
    for verdict, hb, word in (("block", BLOCK, "blocked"), ("approve", APPROVE, "passed"), ("escalate", ESCALATE, "escalated")):
        first = first_line(agent.render(rec("reviewer", "plan", hb), plan=PLAN))
        said = [w for w in ("passed", "blocked", "escalated") if re.search(r"\b" + w + r"\b", first)]
        assert said == [word], f"236.3: a review that says {verdict} must open with {word!r} only, it opens: {first!r}"
    text = visible(agent.render(rec("reviewer", "plan", BLOCK), plan=PLAN))
    lines = text.splitlines()
    ask = item_of(text, "Email me when a job fails zq")
    assert ask, f"236.3: the ask nothing covers is not shown:\n{text}"
    assert "Nothing covers this" in "\n".join(ask) and SRC3 in "\n".join(ask), \
        f"236.3: the ask nothing covers must say Nothing covers this and link its Source {SRC3}:\n{ask}"
    for kept in ("Give back a job id at once zq", "Keep each result for a day zq"):
        assert kept not in text, f"236.3: the review lists the ask {kept!r}, which a criterion keeps:\n{text}"
    at = {name: next((i for i, l in enumerate(lines) if needle in l), -1) for name, needle in
          (("failing criterion", SENTENCES[1]), ("uncovered ask", "Email me when a job fails zq"))}
    rs = headings(text, "Raised:")
    assert len(rs) == 1, f"236.3: the review must show one Raised section for its other raises:\n{text}"
    assert -1 < at["failing criterion"] < at["uncovered ask"] < rs[0], \
        f"236.3: the order must be failing criteria, then asks nothing covers, then Raised; got {at}, Raised at {rs[0]}:\n{text}"
    items = section(text, "Raised:")
    texts = ["\n".join(i) for i in items]
    order = [next((k for k, t in enumerate(texts) if r["text"] in t), -1) for r in (OUTSIDE, QUESTION, ISSUE)]
    assert len(items) == 3 and order == [0, 1, 2], \
        f"236.3: Raised must hold the blocker, then the question, then the issue, and nothing else:\n{texts}"
    for b in ON_CRITERIA:
        assert not any(b["text"] in t for t in texts), f"236.3: a blocker shown under its criterion is in Raised too:\n{texts}"
    lost = raised("blocker", "The retry rule has no test at all zq.", "worker", "77.9", "R7")
    bare = raised("blocker", "A helper was copied, not shared zq.", "worker", None, "R8")
    for plan, which, shown in ((PLAN, "with the plan", [lost, bare]), (None, "with no plan to read", [lost, bare, ON_2])):
        items = section(visible(agent.render(rec("reviewer", "pr", dict(BLOCK, raises=shown)), plan=plan)), "Raised:") or []
        for b in shown:
            item = next(("\n".join(i) for i in items if b["text"] in "\n".join(i)), "")
            assert item and img("blocker") in item, \
                f"236.3: a review {which} dropped the blocker it cannot place, {b['text']!r}, from Raised:\n{items}"


def test_a_passing_review_lists_nothing_that_passed(record_property, env):
    """A review that passes lists no criterion and no ask.

    Draws a passing plan review and a passing code review whose asks all have a criterion, and checks no criterion's
    sentence, no ask, no failed circle and no Nothing covers this shows.

    Proves 236.3."""
    record_property("proves", "236.3")
    for stage in ("plan", "pr"):
        text = visible(agent.render(rec("reviewer", stage, APPROVE), plan=PLAN))
        for said in SENTENCES + [a["ask"] for a in ASKS[:2]] + ["Nothing covers this", failed_circle()]:
            assert said not in text, f"236.3: the passing {stage} review shows {said!r}:\n{text}"


def test_the_posted_code_review_reads_the_plan_from_the_pack(record_property, run):
    """The posted code review shows its failing criterion from the plan in the pack.

    Runs the workflow's record step for a code review that blocks on 77.2, with the plan in $PACK/plan.json, and
    checks the posted comment shows that criterion's sentence behind the failed circle with its Source, and no 77.2.

    Proves 236.3."""
    record_property("proves", "236.3")
    body = run("reviewer", "pr", dict(BLOCK, raises=[ON_2]))[0]
    text = visible(body)
    item = item_of(text, SENTENCES[1])
    assert item and failed_circle() in item[0] and SRC2 in "\n".join(item), \
        f"236.3: the posted code review does not show its failing criterion from the pack's plan:\n{text}"
    assert "77.2" not in text, f"236.3: the posted code review shows the criterion number 77.2:\n{text}"


# 236.4: a review drops Details, What the previous step did, Notes and The owner's asks

def test_a_review_comment_drops_details_the_previous_step_notes_and_asks(record_property, run):
    """A review's comment no longer shows Details, the previous step, Notes or the owner's asks.

    Runs the record step for a plan review and a code review that approve and that block, each with a previous step,
    a summary and asks, and checks none of those headings or their words show, nor a raise's evidence under a
    criterion; an escalation's summary still shows, since it says why it reaches the owner.

    Proves 236.4."""
    record_property("proves", "236.4")
    for stage in ("plan", "pr"):
        for name, hb in (("passing", APPROVE), ("blocking", BLOCK)):
            text = visible(run("reviewer", stage, hb)[0])
            words = plain(text)
            for gone in ("What the previous step did", "Details", "Notes", "Still open", "The owner's asks",
                         "Built the jobs queue zq.", "Kept the old endpoint zq.", "The retry rule zq.", hb["summary"],
                         "Give back a job id at once zq", "evidence of r1 zq"):
                assert gone not in words, f"236.4: the {name} {stage} review's comment still shows {gone!r}:\n{text}"
            assert img("still open") not in text, f"236.4: the {name} {stage} review still shows the still open icon"
    words = plain(visible(run("reviewer", "pr", ESCALATE)[0]))
    assert ESCALATE["summary"] in words, f"236.4: an escalation lost its summary, the reason it reaches you:\n{words}"


# 236.5: what the worker built, as links on one line

def test_the_worker_shows_the_files_it_changed_as_links_on_one_line(record_property, run):
    """The worker's comment links the files it changed, on one line, not its sentences.

    Runs the record step for a worker that committed a change to app/jobs.py, left app/keep.py changed and added
    app/new.py, and checks one line with the files changed icon links all three to the file on try/issue-77, and
    app/page.py, which it did not touch, never shows. Its per-criterion sentence never shows, its test result line
    does, and the record keeps the hand-back exactly with the files beside it.

    Proves 236.5."""
    record_property("proves", "236.5")
    repo = run.repo
    (repo / "app" / "jobs.py").write_text("# jobs, now queued\n")
    git(repo, "commit", "-q", "-am", "queue the jobs")
    (repo / "app" / "keep.py").write_text("# keep, changed\n")
    (repo / "app" / "new.py").write_text("# new\n")
    body, record = run("worker", "", WORK)
    text = visible(body)
    links = {p: f"https://github.com/o/r/blob/try/issue-77/{p}" for p in ("app/jobs.py", "app/keep.py", "app/new.py")}
    lines = [l for l in text.splitlines() if any(u in l for u in links.values())]
    assert len(lines) == 1, f"236.5: the files the worker changed must be links on one line, found {len(lines)}:\n{text}"
    for p, url in links.items():
        assert f"]({url})" in lines[0] or f'href="{url}"' in lines[0], f"236.5: {p} is not linked to {url}:\n{lines[0]}"
    assert img("files changed") in lines[0], f"236.5: the files line does not show the files changed icon:\n{lines[0]}"
    assert "app/page.py" not in text, f"236.5: app/page.py, which the worker never touched, shows:\n{text}"
    assert "submit() returns the id at once zq" not in text, \
        f"236.5: the worker's comment still lists what it built as sentences:\n{text}"
    assert WORK["evidence"] in plain(text), f"236.5: the worker's test result line is not shown:\n{text}"
    assert record["handback"] == WORK, f"236.5: the record no longer keeps the hand-back exactly: {record['handback']}"
    beside = json.dumps({k: v for k, v in record.items() if k != "handback"})
    assert all(p in beside for p in links), f"236.5: the record does not keep the files the worker changed: {beside}"


def test_a_worker_that_changed_nothing_and_ran_no_test_shows_neither_line(record_property, run):
    """A worker that changed no file and gave no test result shows neither line.

    Runs the record step for a worker that changed nothing and whose test result line is blank, and checks the
    comment shows no files changed icon, no link to the branch and no empty test result line.

    Proves 236.5."""
    record_property("proves", "236.5")
    text = visible(run("worker", "", dict(WORK, evidence=" "))[0])
    assert img("files changed") not in text and "blob/try/issue-77" not in text, \
        f"236.5: a worker that changed nothing shows a files line:\n{text}"
    assert "test run" not in text.lower() and "pytest" not in text, \
        f"236.5: a worker with no test result shows its test result line:\n{text}"


# 236.6: answers look the same from every agent

def test_every_agents_answers_show_in_the_same_raised_earlier_section(record_property, env):
    """The planner's, the worker's and a review's answers look the same.

    Draws a review, a planner and a worker that each answer the same earlier raises the same way (one done, one
    disagree), and checks each comment shows one Raised earlier section whose items are exactly the same lines; and
    that a planner and a worker that answer nothing show no Raised earlier section.

    Proves 236.6."""
    record_property("proves", "236.6")
    w1 = raised("blocker", "The kept test reads a file that never exists zq.", "planner", "Kept test", "W1", "worker")
    r9 = raised("blocker", "submit() still blocks for a minute zq.", "worker", "Speed", "R9")
    earlier = [rec("worker", "", dict(WORK, raises=[w1])), rec("reviewer", "pr", dict(APPROVE, raises=[r9]))]
    answers = [{"raise": "W1", "answer": "done", "why": "The test now makes the file itself zq."},
               {"raise": "R9", "answer": "disagree", "why": "It returns in 0.1 s, see the test result zq."}]
    drawn = {role: section(visible(agent.render(rec(role, stage, dict(hb, answers=answers)), earlier=earlier)),
                           "Raised earlier:")
             for role, stage, hb in (("reviewer", "pr", APPROVE), ("planner", "", PLAN), ("worker", "", WORK))}
    assert drawn["reviewer"] and len(drawn["reviewer"]) == 2, f"236.6: the review's answers are not shown: {drawn['reviewer']}"
    for role in ("planner", "worker"):
        assert drawn[role] == drawn["reviewer"], (f"236.6: the {role}'s answers must look exactly like the review's:\n"
                                                  f"{role}: {drawn[role]}\nreview: {drawn['reviewer']}")
    for role, hb in (("planner", PLAN), ("worker", WORK)):
        text = visible(agent.render(rec(role, "", hb), earlier=earlier))
        assert not headings(text, "Raised earlier:"), f"236.6: a {role} that answered nothing shows Raised earlier:\n{text}"


# 236.7: the stats fold

CASES = [("planner", "", PLAN, True), ("worker", "", WORK, True), ("reviewer", "plan", APPROVE, True),
         ("reviewer", "pr", BLOCK, True), ("rejected planner", "", PLAN, False)]


def test_the_stats_sit_in_a_fold_right_above_the_full_record(record_property, env):
    """Every run comment folds its stats right above the full record.

    Draws a planner, a worker, a plan review, a code review, a rejected plan and a run cancelled after its agent
    started, and checks the fold right above the Full record is a Stats fold with the stats icon holding the model,
    time, turns, tokens, cost and the links to the conversation and the run, with nothing between the two folds,
    and that no stats line is left open outside it.

    Proves 236.7."""
    record_property("proves", "236.7")
    bodies = [(role, agent.render(rec(role.split()[-1], stage, hb, passed, ["a problem"]))) for role, stage, hb, passed in CASES]
    bodies.append(("cancelled", agent.render(agent.cancelled("worker", "", True, META))))
    for what, body in bodies:
        fold, between = stats_fold(body)
        assert fold, f"236.7: the {what} comment has no fold right above the Full record:\n{body}"
        assert fold.startswith(img("stats")), f"236.7: the {what} comment's stats line does not open with the stats icon: {fold}"
        assert not between.strip(), f"236.7: something sits between the Stats fold and the Full record: {between!r}"
        for said in ("Opus 5.5", "4.0 min", "23 turns", "401K", "18K", "$3.20", "https://g/log.md",
                     "https://github.com/o/r/actions/runs/1"):
            assert said in fold, f"236.7: the {what} comment's Stats fold does not hold {said!r}:\n{fold}"
        outside = FOLD.sub("", body).replace(fold, "")
        assert "turns" not in outside and img("stats") not in outside, \
            f"236.7: the {what} comment still shows its stats outside the fold:\n{outside}"


def test_a_split_says_no_model_ran_and_a_run_no_agent_started_keeps_its_line(record_property, env):
    """A split's Stats fold says no model ran; runs with no agent keep No agent ran.

    Draws a filed split and checks its Stats fold says no model and links the run; then a run that never started and
    one cancelled before its agent started, and checks each keeps its No agent ran line and shows no Stats fold.

    Proves 236.7."""
    record_property("proves", "236.7")
    split = {"role": "split", "stage": None, "run": "https://github.com/o/r/actions/runs/1",
             "handback": {"stories": [{"story": 1, "issue": 201, "title": "First", "blocked_by": []}]},
             "check": {"passed": True, "problems": []}}
    fold, _ = stats_fold(agent.render(split))
    assert fold and img("stats") in fold and "no model" in fold.lower() and "actions/runs/1" in fold, \
        f"236.7: a filed split's Stats fold does not say no model ran:\n{fold}"
    for what, r in (("never started", agent.not_started("worker", "", "main is red", META)),
                    ("cancelled before it started", agent.cancelled("worker", "", False, META))):
        body = agent.render(r)
        assert "No agent ran" in body, f"236.7: a run {what} lost its No agent ran line:\n{body}"
        assert "Stats" not in plain(body.partition(RECORD_FOLD)[0]), f"236.7: a run {what} shows a Stats fold:\n{body}"


# 236.8: token counts read short

@pytest.mark.parametrize("count, short", [(950, "950"), (1000, "1K"), (1499, "1K"), (1500, "2K"), (12345, "12K"),
                                          (401000, "401K"), (999499, "999K"), (999500, "1M"), (2500000, "3M"),
                                          (3489308, "3M")])
def test_token_counts_read_short(record_property, env, count, short):
    """Token counts read short: K from a thousand, M from a million, no decimals.

    Draws a run whose tokens in and out are both the given count and checks its Stats fold shows the short form twice,
    rounded to the nearest with halves up, and never the count with commas or a decimal.

    Proves 236.8."""
    record_property("proves", "236.8")
    r = rec("worker", "", WORK)
    r["report"].update(tokens_in=count, tokens_out=count)
    fold, _ = stats_fold(agent.render(r))
    assert fold, "236.8: the run comment has no Stats fold to read the tokens from"
    found = re.findall(r"(?<![\w.,$])" + re.escape(short) + r"(?![\w.,]\d|\w)", fold)
    assert len(found) == 2, f"236.8: {count:,} tokens in and out must read {short} twice in the Stats fold:\n{fold}"
    for long in (f"{count:,}", str(count)) if count >= 1000 else ():
        assert long not in fold, f"236.8: the Stats fold still shows {long} tokens:\n{fold}"
    assert not re.search(r"\d\.\d+\s*[KM]\b", fold), f"236.8: a token count shows a decimal:\n{fold}"


# 236.9: the full record stays last and reads back

def test_the_full_record_stays_the_last_fold_and_reads_back(record_property, run):
    """The full record stays the last fold of every run comment and reads back exactly.

    Runs the record step for a planner, a worker and both reviews, and checks the Full record fold ends the comment,
    right under the Stats fold, and that reading the posted comment back as the bot's gives the record written to
    record.json, unchanged.

    Proves 236.9."""
    record_property("proves", "236.9")
    for role, stage, hb in (("planner", "", PLAN), ("worker", "", WORK), ("reviewer", "plan", BLOCK), ("reviewer", "pr", BLOCK)):
        body, record = run(role, stage, hb)
        assert RECORD_FOLD in body, f"236.9: the {role} {stage} comment has no Full record fold"
        after = body.partition(RECORD_FOLD)[2].partition("</details>")[2]
        assert after.strip().endswith(stats_fold(body)[0] or "?"), \
            f"236.9: the {role} {stage} comment does not end with its stats line: {after!r}"
        fold, between = stats_fold(body)
        assert fold and not between.strip(), \
            f"236.9: the Full record of the {role} {stage} comment is not right under the Stats fold:\n{body}"
        back = agent.records([{"author": {"login": agent.BOT}, "body": body}])
        assert back == [record], f"236.9: the {role} {stage} comment does not read back as its record"

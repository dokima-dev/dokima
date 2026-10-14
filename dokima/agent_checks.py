"""The deterministic checks of an agent's hand-back: `check`, `load` and every `problems_*` but the pack's.

Split out of dokima/agent.py (#636).
"""
import json
import os
import re
import subprocess
import sys

from dokima import raises, words


def problems_searched(h, pack_dir):
    """What each filed issue lacks (#622), and each searched issue not open in the pack.

    A review files its own issue raises and each issue it answers done that the planner or the worker raised; each
    names the open issues it searched and its verdict, on the raise or on the answer."""
    own = [r for r in h.get("raises", []) if isinstance(r, dict) and r.get("kind") == "issue"] \
        if isinstance(h.get("raises"), list) else []
    path = os.path.join(pack_dir, "open_blockers.json")
    listed = json.load(open(path)) if os.path.exists(path) else []
    theirs = {r.get("id") for r in listed if isinstance(r, dict) and r.get("kind") == "issue"
              and raises.sent_to(r) == raises.CONFIRMS} if isinstance(listed, list) else set()
    confirmed = [a for a in h.get("answers", []) if isinstance(a, dict) and a.get("answer") == "done"
                 and a.get("raise") in theirs] if isinstance(h.get("answers"), list) else []
    filed = [(f"raise {n}", r) for n, r in enumerate(own, 1)] + [(f"the answer to {a['raise']}", a) for a in confirmed]
    if not filed:
        return []
    bad = [p for where, d in filed for p in raises.filing_problems(where, d)]
    named = [(f, d[f] if f != raises.CAUSE else [d[f]]) for _, d in filed
             for f in (raises.SEARCHED, raises.SYMPTOMS, raises.CAUSE)
             if (raises.is_numbers(d.get(f)) and d.get(f)) or (f == raises.CAUSE and raises.is_numbers([d.get(f)]))]
    if not named:
        return bad
    path = os.path.join(pack_dir, "open_issues.json")
    if not os.path.exists(path):
        return bad + [f"open_issues.json is missing from the pack, so the "
                      f"{', '.join(dict.fromkeys(f for f, _ in named))} issues cannot be checked"]
    known = {i.get("number") for i in json.load(open(path)) if isinstance(i, dict)}
    return bad + [f"{f} names #{n}, which is not an open issue in the pack" for f, ns in named for n in ns
                  if n not in known]


def problems_links(h, pack_dir):
    """Everything wrong with a plan's links: three lists of open issue numbers from the pack,
    never the issue itself, and no issue in two lists."""
    path = os.path.join(pack_dir, "open_issues.json")
    if not os.path.exists(path):
        return ["open_issues.json is missing from the pack, so the links cannot be checked"]
    links = h.get("links")
    if not isinstance(links, dict):
        return ["links must be an object with three lists: " + ", ".join(LINKS)]
    issue = os.path.join(pack_dir, "issue.md")
    m = re.match(r"# Issue #(\d+)", open(issue).read()) if os.path.exists(issue) else None
    me = int(m.group(1)) if m else None
    known = {i.get("number") for i in json.load(open(path)) if isinstance(i, dict)}
    bad, seen = [], {}
    for k in LINKS:
        v = links.get(k)
        if not isinstance(v, list) or not all(isinstance(n, int) and not isinstance(n, bool) for n in v):
            bad.append(f"links.{k} must be a list of issue numbers")
            continue
        for n in v:
            if n == me:
                bad.append(f"links.{k} links #{n}, the issue itself")
            elif n not in known:
                bad.append(f"links.{k} links #{n}, which is not an open issue")
            seen.setdefault(n, [])
            if k not in seen[n]:
                seen[n].append(k)
    bad += [f"#{n} sits in more than one list of links: {', '.join(ks)}" for n, ks in seen.items() if len(ks) > 1]
    return bad


def problems_for_owner(a, number, parent):
    """Everything wrong with a reviewer's answer to a question for the owner.

    Done needs the owner's words, where they said them, and whether the reading changes how the system works or what
    it costs."""
    rid, bad = a.get("raise"), []
    if a.get("answer") != "done":
        return bad
    if not filled(a.get("words")):
        bad.append(f"the answer to {rid}, a question for the owner, needs words: the owner's own words, word for word")
    where = f"{issue_url(number)}, its parent {issue_url(parent)}, one of their comments' links" if parent \
        else f"{issue_url(number)}, one of its comments' links"
    if not filled(a.get("source")) or not owner_source(a["source"].strip(), number, parent):
        bad.append(f"the answer to {rid}, a question for the owner, needs a source: {where}, or AGENTS.md")
    if not isinstance(a.get("changes"), bool):
        bad.append(f"the answer to {rid}, a question for the owner, needs changes: true or false, whether the reading "
                   "changes how the system works or what it costs")
    return bad


def problems_round(role, h, pack_dir):
    """Everything wrong with how a hand-back answers the raises listed for its role.

    The reviewer may also answer a question for the owner still open in the pack's records, with the owner's words,
    where they said them and whether the reading changes anything; the planner's links must name open issues in the
    pack."""
    path = os.path.join(pack_dir, "open_blockers.json")
    listed = json.load(open(path)) if os.path.exists(path) else []
    listed = [r for r in listed if isinstance(r, dict)] if isinstance(listed, list) else []
    answers = h.get("answers", [])
    questions = []
    if role == "reviewer":
        questions = [r for r in open_raises(pack_records(pack_dir))
                     if r.get("kind") == "question" and r.get("to") == "owner" and r.get("raised_by") == "planner"]
    bad = raises.check_answers(role, answers, listed + questions)
    if questions and isinstance(answers, list):
        asked = {r["id"] for r in questions}
        number, parent = pack_issue(pack_dir), pack_parent(pack_dir)
        for a in answers:
            if isinstance(a, dict) and a.get("raise") in asked:
                bad += problems_for_owner(a, number, parent)
    if role == "planner":
        bad += problems_links(h, pack_dir)
    if role == "reviewer":
        bad += problems_searched(h, pack_dir)
    return bad


def problems_review(r):
    """Everything wrong with a review.json, as plain sentences; empty when it is well formed."""
    bad = []
    if r.get("verdict") not in VERDICTS:
        bad.append("verdict must be approve, block or escalate")
    if not str(r.get("summary", "")).strip():
        bad.append("summary is empty")
    prev = r.get("previous_step")
    if not isinstance(prev, dict) or not any(prev.get(k) for k in ("did", "decided", "open")):
        bad.append("previous_step must sum up what the planner or worker did, decided and left open")
    elif sum(len(prev.get(k) or []) for k in ("did", "decided", "open")) > 5:
        bad.append("previous_step holds at most five lines")
    blocks = [x for x in r.get("raises") or [] if isinstance(x, dict) and x.get("kind") == "blocker"] \
        if isinstance(r.get("raises"), list) else []
    if r.get("verdict") == "approve" and blocks:
        bad.append("an approve raises no blocker")
    if r.get("verdict") == "block" and not blocks:
        bad.append("a block needs at least one blocker in raises")
    return bad


def problems_tests(r, plan):
    """A plan review must judge every test the plan names: does it check only its
    criterion's behavior, with the edge cases the owner named or normal use hits? A false one never approves."""
    named = sorted({t for ts in ((plan or {}).get("tests") or {}).values() if isinstance(ts, list) for t in ts})
    rows = r.get("tests") if isinstance(r.get("tests"), list) else []
    seen = {str(x.get("test")): x for x in rows if isinstance(x, dict)}
    bad = [f"tests has no judgment of `{t}`: say only_its_behavior true or false, and why in one line"
           for t in named if not (isinstance(seen.get(t, {}).get("only_its_behavior"), bool)
                                  and str(seen.get(t, {}).get("why") or "").strip())]
    wide = [t for t, x in seen.items() if x.get("only_its_behavior") is False]
    if wide and r.get("verdict") == "approve":
        bad.append(", ".join("`" + t + "`" for t in wide) + f" check more than their criterion's behavior, so the verdict cannot be approve")
    return bad


def problems_size(r, ids=()):
    """A plan review must judge each criterion one behavior or not, in `behaviors`, and say
    whether the plan keeps the size rule: size is "ok", or the rule it breaks. A criterion bundling two behaviors breaks
    it; a plan that breaks it is never approved."""
    bad = []
    rows = r.get("behaviors") if isinstance(r.get("behaviors"), list) else []
    seen = {str(b.get("criterion")): b for b in rows if isinstance(b, dict)}
    for k in ids:
        b = seen.get(str(k))
        if not b or not isinstance(b.get("one_behavior"), bool) or not str(b.get("why") or "").strip():
            bad.append(f"behaviors has no judgment of criterion {k}: say one_behavior true or false, and why in one line")
    bundled = [k for k, b in seen.items() if b.get("one_behavior") is False]
    size = str(r.get("size") or "").strip()
    if bundled and size.lower() == "ok":
        bad.append(f"criteria {', '.join(bundled)} bundle more than one behavior, so size cannot be ok")
    if bad:
        return bad
    if not size:
        return ['size is empty: write "ok" if every story holds 1 to 3 criteria, each one behavior, in as few stories as '
                "the count needs; otherwise say which part breaks it"]
    if size.lower() != "ok" and r.get("verdict") == "approve":
        return [f"size says the plan breaks the size rule ({size}), so the verdict cannot be approve"]
    return []


def problems_edge_cases(r, ids=()):
    """A plan review must judge each criterion's edge cases, in `edge_cases`.

    Each row lists the exotic cases it cuts and the normal-use ones missing, as plain lines ([] when none)."""
    rows = r.get("edge_cases") if isinstance(r.get("edge_cases"), list) else []
    seen = {str(e.get("criterion")): e for e in rows if isinstance(e, dict)}
    bad = []
    for k in ids:
        e = seen.get(str(k))
        if not e:
            bad.append(f"edge_cases has no judgment of criterion {k}: list the exotic cases it cuts and the normal-use "
                       "ones missing, each [] when there are none")
            continue
        for f in ("cut", "missing"):
            v = e.get(f)
            if not isinstance(v, list) or not all(filled(x) for x in v):
                bad.append(f"edge_cases' {f} for criterion {k} must be a list of plain lines, [] when there are none")
    return bad


def problems_asks(r, ids):
    """Everything wrong with a plan review's asks list: every ask the owner made, in their
    words, with a link to where they said it and the plan's criterion (one of ids) that keeps it, or "missing"; an
    approve keeps every ask."""
    asks = r.get("asks")
    if not isinstance(asks, list) or not asks:
        return ["asks must list every ask in the owner's issue and comments, each {\"ask\": \"the owner's words\", "
                "\"source\": \"a link to where they said it\", \"criterion\": \"N.k\" or \"missing\"}"]
    bad = problems_items(r, "asks", ("ask", "source", "criterion"), name="ask")
    good = [a for a in asks if isinstance(a, dict) and all(filled(a.get(k)) for k in ("ask", "source", "criterion"))]
    for a in good:
        c = a["criterion"].strip()
        if c != "missing" and c not in ids:
            bad.append(f"the ask \"{a['ask']}\" is matched to {c}, which is not a criterion of the plan "
                       f"({', '.join(ids) or 'none'})")
    gone = [a["ask"] for a in good if a["criterion"].strip() == "missing"]
    if r.get("verdict") == "approve" and gone:
        bad.append("an approve keeps every ask, but these are marked missing: " + "; ".join(f'"{g}"' for g in gone))
    return bad


def issue_url(number):
    """The link of the issue on GitHub."""
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{number}"


def owner_source(source, number, parent=None):
    """True when a source names owner's words Dokima can check.

    That is the issue's own text, its parent's (when given), one of their comments, or AGENTS.md."""
    return source == "AGENTS.md" or any(re.fullmatch(re.escape(issue_url(n)) + r"(#issuecomment-\d+)?", source)
                                        for n in ([number, parent] if parent else [number]))


def problems_work(w):
    """Everything wrong with a work.json, as plain sentences; empty when it is well formed."""
    bad = []
    if not str(w.get("summary", "")).strip():
        bad.append("summary is empty")
    if not isinstance(w.get("criteria"), dict) or not w["criteria"]:
        bad.append("criteria must give one line per criterion")
    if not str(w.get("evidence", "")).strip():
        bad.append("evidence is empty: name the last test command and its result line")
    return bad


def problems_old(h):
    """Each field retired by #300 the hand-back still holds, even empty, named."""
    return [f"{f} is a retired field: raise and answer only through raises and answers" for f in OLD_FIELDS if f in h]


def problems_raised(role, h):
    """Everything wrong with a hand-back's raises and answers, each raise checked against the table."""
    bad = raises.check_raises(role, h["raises"]) if "raises" in h else []
    if not isinstance(h.get("answers", []), list):
        bad.append("the answers must be a list, each {\"raise\": ID, \"answer\": \"done\" or \"disagree\", \"why\": ...}")
    else:
        bad += [f"answer {i} is not an object with raise, answer and why"
                for i, a in enumerate(h.get("answers", []), 1) if not isinstance(a, dict)]
    return bad


def problems_items(h, field, keys, name=None):
    """Everything wrong with an optional list of objects that each need some non-empty text fields, naming the field."""
    v = h.get(field, [])
    if not isinstance(v, list):
        return [f"{field} must be a list"]
    bad = []
    for i, x in enumerate(v, 1):
        label = f"{field} item {i}" + (f" ({x.get(name)})" if name and isinstance(x, dict) and filled(x.get(name)) else "")
        if not isinstance(x, dict):
            bad.append(f"{label} must be an object with {', '.join(keys)}")
            continue
        missing = [k for k in keys if not filled(x.get(k))]
        if missing:
            bad.append(f"{label} needs {', '.join(missing)}")
    return bad


def problems_shape(kind, h):
    """Everything missing, wrongly typed or wrongly shaped in a hand-back against its prompt's shape, each naming the field."""
    bad = problems_old(h) + problems_raised("reviewer" if kind == "review" else "worker", h)
    if kind == "review":
        prev = h.get("previous_step")
        if not isinstance(prev, dict):
            bad.append("previous_step must be an object with did, decided and open")
        elif not all(isinstance(prev.get(k, []), list) and all(filled(x) for x in prev.get(k, [])) for k in ("did", "decided", "open")):
            bad.append("previous_step: did, decided and open must each be a list of lines")
        if h.get("verdict") not in VERDICTS:
            bad.append("verdict must be approve, block or escalate")
        if not filled(h.get("summary")):
            bad.append("summary must be one non-empty sentence")
        return bad
    if not filled(h.get("summary")):
        bad.append("summary must be one non-empty sentence")
    crit = h.get("criteria")
    if not isinstance(crit, dict) or not crit:
        bad.append("criteria must be an object giving one line per criterion")
    else:
        bad += [f"criteria: the line for {k} must be non-empty text" for k, v in crit.items() if not filled(v)]
    if not filled(h.get("evidence")):
        bad.append("evidence must name the last test command and its result line")
    return bad


def plan_criteria(plan, number):
    """The plan's criteria ids: N.k for a story (acceptance criteria, then non-functional), S<s>.<k> for each
    story of a split."""
    count = lambda p: sum(len(p.get(k)) for k in ("acceptance_criteria", "non_functional") if isinstance(p.get(k), list))
    if plan.get("kind") == "feature":
        stories = plan.get("stories") if isinstance(plan.get("stories"), list) else []
        return [f"S{s}.{k}" for s, st in enumerate(stories, 1) if isinstance(st, dict) for k in range(1, count(st) + 1)]
    return [f"{number}.{k}" for k in range(1, count(plan) + 1)]


def problems_plan(kind, h, plan, number):
    """Everything in a work.json that does not match the plan: one line per criterion."""
    ids = plan_criteria(plan, number)
    bad = []
    if kind == "work":
        crit = h.get("criteria")
        if isinstance(crit, dict):
            bad += [f"criteria has no line for {c}, a criterion of the plan" for c in ids if c not in crit]
            bad += [f"criteria gives a line for {c}, which the plan does not have" for c in crit if c not in ids]
    return bad


def load(path, name):
    """Read a JSON object from a file; return (object, None) or (None, the reason naming the file)."""
    try:
        data = json.load(open(path))
    except FileNotFoundError:
        return None, f"{name} is missing ({path})"
    except (OSError, json.JSONDecodeError) as e:
        return None, f"{name} is not valid JSON ({path}): {e}"
    if not isinstance(data, dict):
        return None, f"{name} is not a JSON object ({path})"
    return data, None


def plan_tests(plan):
    """Every test the plan lists for its criteria, each once, in the plan's order."""
    tests = plan.get("tests") if isinstance(plan.get("tests"), dict) else {}
    return list(dict.fromkeys(t for ts in tests.values() if isinstance(ts, list) for t in ts if filled(t)))


def failing_plan_tests(plan):
    """Run each plan test alone on this branch; return those that do not pass.

    One at a time, so a test missing from the branch fails alone and is named, while the others still run."""
    env = {**os.environ, "PYTHONPATH": os.getcwd()}
    env.pop("PYTHONSAFEPATH", None)
    return [t for t in plan_tests(plan)
            if subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", t],
                              env=env, capture_output=True, text=True).returncode != 0]


def check(kind, path, plan_path=None, number=None):
    """Check one hand-back file against its prompt's shape and, when given, the approved plan and the issue's number.
    Print every problem and return 1 if there are any, else 0."""
    data, err = load(path, os.path.basename(path))
    if err:
        print(err)
        return 1
    bad = problems_shape(kind, data) or (problems_review if kind == "review" else problems_work)(data)
    listed = []
    if filled(data.get("summary")):
        listed, too_long = words.summary_caps(data["summary"])
        bad += too_long
    more, too_long = words.style({k: v for k, v in data.items() if k != "summary"})
    listed, bad = listed + more, bad + too_long
    if kind == "work" and os.environ.get("PLANNER_BASE"):
        more, too_long = worker_docstring_caps(os.environ["PLANNER_BASE"])
        listed, bad = listed + more, bad + too_long
    if plan_path is not None:
        plan, err = load(plan_path, "plan.json")
        if err:
            bad.append(f"{err}: the hand-back can't be checked against the plan")
        elif not str(number or "").isdigit():
            bad.append(f"the issue number {number!r} is not a number: the hand-back can't be checked against the plan")
        else:
            bad += problems_plan(kind, data, plan, number)
            if kind == "work" and os.environ.get("ROLE") == "worker":
                bad += [PLAN_TEST_FAILS + t for t in failing_plan_tests(plan)]
            if kind == "review" and os.environ.get("STAGE") == "plan":
                bad += problems_asks(data, plan_criteria(plan, number))
                bad += problems_size(data, plan_criteria(plan, number))
                bad += problems_edge_cases(data, plan_criteria(plan, number))
                bad += problems_tests(data, plan)
    for line in listed + bad:
        print(line)
    return 1 if bad else 0


def worker_docstring_caps(base):
    """(listed, rejected) for each Python docstring added or rewritten since `base`.

    Older docstrings whose first line is unchanged are left alone; a base git cannot read fails closed.
    """
    from dokima import planner  # planner imports this module, so it is read only when needed
    try:
        paths = [p for p in planner.changed_files(base) if p.endswith(".py")]
    except subprocess.CalledProcessError as e:
        return [], [f"the docstrings the worker added can't be read: git can't compare with {base} ({e.stderr.strip()})"]
    return planner.docstring_caps(paths, planner.read_at(base), planner.read_now)


# The other agent job files, imported last so the job files can use each other (#636).
from dokima.agent_records import VERDICTS, OLD_FIELDS, PLAN_TEST_FAILS, open_raises, LINKS, filled
from dokima.agent_roles import pack_records, pack_issue, pack_parent

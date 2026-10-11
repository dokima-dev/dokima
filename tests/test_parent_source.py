"""A split story may cite the owner's words in its parent issue (#334).

On #331 the planner linked its criteria to #330, the parent where the owner wrote them, and code rejected the plan
twice: a source had to be the story's own issue or one of its comments. These tests hold code to the new rule: a
criterion's source may be the story's own issue, its parent issue (GitHub's native sub-issue parent), or a comment
on either; any other issue is still rejected, naming the criterion and the source; and the reviewer's check that the
owner's words were really said there accepts the parent too.

How the parent reaches each check:
- The starting pack (`python3 -m dokima.agent pack N ROLE STAGE DEST`, built while the run holds a GitHub key) writes
  `parent.json` holding {"number": P}, P the issue's parent on GitHub. With no parent, or when GitHub cannot say,
  parent.json is absent or holds {"number": null}.
- The planner's check (`python3 -m dokima.planner check N OUT`) and the plan review's check (`python3 -m dokima.agent
  check review FILE PLAN N`) hold no key: they read parent.json from the pack named by $PACK (the plan review's
  check also finds it beside PLAN, which sits in the pack).
- The river (`python3 -m dokima.agent next N OUT`) asks GitHub for the parent and its words itself.

GitHub is faked by a `gh` on PATH. It answers the parent the ways GitHub gives it: REST `repos/o/r/issues/N/parent`
(the parent issue, or 404 when there is none), and GraphQL queries naming `parent` (repository.issue.parent with its
number, title, body, url and comments). The parent's words come from `gh issue view P`, REST `repos/o/r/issues/P` and
`repos/o/r/issues/P/comments`, or that GraphQL answer. With fail_parent set, every parent lookup fails as GitHub
does (HTTP 502).
"""
import json
import os
import subprocess
import sys

import test_autopilot_river as tr
import test_start as ts

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def url(n):
    """An issue's link on the fake GitHub."""
    return f"https://github.com/o/r/issues/{n}"


# --- The planner's check: a story (#331) of a split parent (#330); #329 is any other issue. -------------------------

STORY_N, PARENT_N, OTHER_N = 331, 330, 329


def story(sources):
    """A one-story plan of #331 whose acceptance criteria cite these sources, one criterion each."""
    return {"kind": "user_story", "summary": "Cards show what is true now.", "user_story": "Cards show what is true now.",
            "acceptance_criteria": [{"text": f"Criterion {k} holds.", "source": s} for k, s in enumerate(sources, 1)],
            "non_functional": [], "scope": ["dokima/x.py"], "out_of_scope": [],
            "tests": {f"{STORY_N}.{k}": [f"tests/test_x.py::test_{k}"] for k in range(1, len(sources) + 1)},
            "links": {"blocked_by": [], "blocks": [], "relates_to": []}}


def feature(sources):
    """A two-story split of #331 whose first story's criteria cite these sources."""
    return {"kind": "feature", "summary": "Two stories.", "feature": "Cards show what is true now.",
            "stories": [{"title": "One", "user_story": "u1", "non_functional": [], "depends_on": [],
                         "acceptance_criteria": [{"text": f"Criterion {k} holds.", "source": s}
                                                 for k, s in enumerate(sources[:3], 1)]},
                        {"title": "Two", "user_story": "u2", "non_functional": [], "depends_on": [0],
                         "acceptance_criteria": [{"text": f"Criterion {k} holds.", "source": s}
                                                 for k, s in enumerate(sources[3:], 4)]
                                                + [{"text": "Two holds.", "source": url(STORY_N)}]}],
            "links": {"blocked_by": [], "blocks": [], "relates_to": []}}


def planner_check(tmp, plan, parent):
    """Run the planner's check on a plan of #331, the pack naming this parent.

    With parent None the pack has no parent.json.
    Runs from an empty temp git repo, so the check finds no changed tests of its own and never runs this test file.
    Returns (exit code, everything it printed and its rejected.txt)."""
    t = str(tmp)
    out, pack, repo = f"{t}/out", f"{t}/pack", f"{t}/repo"
    for d in (out, pack, repo):
        os.makedirs(d, exist_ok=True)
    json.dump(plan, open(f"{out}/plan.json", "w"))
    if parent is not None:
        json.dump({"number": parent}, open(f"{pack}/parent.json", "w"))
    for cmd in (["init", "-q"], ["config", "user.name", "Test"], ["config", "user.email", "test@example.com"],
                ["commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, capture_output=True)
    env = {k: v for k, v in os.environ.items() if k not in ("PLANNER_BASE", "PLANNER_RUN_BASE", "PACK")}
    env.update(PACK=pack, GITHUB_REPOSITORY="o/r", GITHUB_SERVER_URL="https://github.com", PYTHONPATH=ROOT)
    p = subprocess.run([sys.executable, "-m", "dokima.planner", "check", str(STORY_N), out], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=60)
    rejected = open(f"{out}/rejected.txt").read() if os.path.exists(f"{out}/rejected.txt") else ""
    return p.returncode, p.stdout + p.stderr + rejected


def assert_source_accepted(text, k, source, crit, case):
    """The check raised nothing about acceptance criterion k; it may reject other things."""
    assert f"acceptance criterion {k} " not in text, \
        f"{crit} ({case}): the planner's check rejected acceptance criterion {k}, whose source is {source}:\n{text[-1500:]}"


def test_a_criterion_may_cite_its_own_issue_its_parent_or_a_comment_on_either(record_property, tmp_path):
    """A criterion may cite its own issue, its parent, or a comment on either.

    Runs the real planner check on plans of #331, whose pack names #330 as its parent. A story and a split citing
    #331, #331's comment, #330 and #330's comment must raise nothing about any source (a split passes outright).
    The same parent links in a pack with no parent must still be rejected, so the parent comes from the pack. Proves 334.1."""
    record_property("proves", "334.1")
    sources = [url(STORY_N), url(STORY_N) + "#issuecomment-3311", url(PARENT_N), url(PARENT_N) + "#issuecomment-3301"]
    code, text = planner_check(tmp_path / "story", story(sources), PARENT_N)
    for k, s in enumerate(sources, 1):
        assert_source_accepted(text, k, s, "334.1", "a story")
    code, text = planner_check(tmp_path / "split", feature(sources), PARENT_N)
    # Its sources pass; since #416 a story of a parent never splits again, so the split itself is refused for that alone.
    assert code != 0 and "never splits again" in text and "source" not in text.split("never splits again")[0][-300:], \
        f"334.1: a split whose criteria cite #331, #330 or their comments was refused for its sources:\n{text[-1500:]}"
    code, text = planner_check(tmp_path / "no-parent", story([url(STORY_N), url(PARENT_N)]), None)
    assert code != 0 and url(PARENT_N) in text, \
        f"334.1: with no parent in the pack, the check accepted #330 as a source; the parent must come from GitHub:\n{text[-1500:]}"


def test_any_other_issue_is_still_rejected_naming_the_criterion_and_the_source(record_property, tmp_path):
    """A criterion citing any other issue is rejected, naming the criterion and source.

    Runs the real planner check on plans of #331 (parent #330). Criterion 1 cites the parent and must raise nothing;
    criterion 2 cites another issue (#329, a comment on #329, #3301 whose number starts like the parent's, the
    parent's own repo path under another repo) and must be rejected, the problem naming "acceptance criterion 2"
    and that source. A split's story is held to the same rule, naming "story 1". Proves 334.2."""
    record_property("proves", "334.2")
    for case, bad in (("another issue", url(OTHER_N)),
                      ("a comment on another issue", url(OTHER_N) + "#issuecomment-3291"),
                      ("a number that starts like the parent's", url(PARENT_N) + "1"),
                      ("the parent's number in another repo", f"https://github.com/x/r/issues/{PARENT_N}")):
        code, text = planner_check(tmp_path / case.replace(" ", "-").replace("'", ""), story([url(PARENT_N), bad]), PARENT_N)
        assert code != 0, f"334.2 ({case}): the planner's check passed a criterion citing {bad}"
        assert "acceptance criterion 2" in text and bad in text, \
            f"334.2 ({case}): the rejection does not name acceptance criterion 2 and its source {bad}:\n{text[-1500:]}"
        assert "acceptance criterion 1 " not in text, \
            f"334.2 ({case}): criterion 1, which cites the parent #330, was rejected too:\n{text[-1500:]}"
    code, text = planner_check(tmp_path / "split", feature([url(PARENT_N), url(OTHER_N)]), PARENT_N)
    assert code != 0 and "story 1" in text and "acceptance criterion 2" in text and url(OTHER_N) in text, \
        f"334.2: a split citing #329 was not rejected naming story 1, its criterion 2 and the source:\n{text[-1500:]}"
    assert "acceptance criterion 1 " not in text, \
        f"334.2: a split's criterion 1, which cites the parent #330, was rejected too:\n{text[-1500:]}"


# --- The fake GitHub that knows each issue's parent. ----------------------------------------------------------------

def parent_snippet(parents, issues):
    """Fake-gh code answering parents and the parents' words; parents {child: parent}, issues {n: {body, comments}}."""
    return r'''
PARENTS = __PARENTS__
ISSUES = __ISSUES__
joined = " ".join(a)
def _num(x):
    try:
        return int(str(x).rstrip("/").rsplit("/", 1)[-1].lstrip("#"))
    except ValueError:
        return None
def _url(n):
    return "https://github.com/o/r/issues/%d" % n
def _node(n):
    i = ISSUES.get(str(n), {"body": "", "comments": []})
    return {"number": n, "title": "Issue %d" % n, "body": i["body"], "url": _url(n),
            "comments": {"nodes": [{"url": c["url"], "author": {"login": c["login"]}, "body": c["body"],
                                    "createdAt": "2026-10-01T00:00:00Z"} for c in i["comments"]]}}
def _rest(n):
    i = ISSUES.get(str(n), {"body": "", "comments": []})
    return {"id": n * 10, "node_id": "I_%d" % n, "number": n, "title": "Issue %d" % n, "body": i["body"], "state": "open",
            "html_url": _url(n), "url": "https://api.github.com/repos/o/r/issues/%d" % n, "user": {"login": "someone"}}
_lookup = (a[:2] == ["api", "graphql"] and "parent" in joined) or \
    (a[:1] == ["api"] and any(re.fullmatch(r"/?repos/o/r/issues/\d+/parent", x) for x in a))
if _lookup and opts.get("fail_parent"):
    sys.stderr.write("HTTP 502: Server Error (https://api.github.com/graphql)\n")
    sys.exit(1)
if a[:2] == ["api", "graphql"] and "parent" in joined:
    _m = re.search(r"issue\(\s*number\s*:\s*(\d+)", joined)
    _ns = [int(_m.group(1))] if _m else []
    for _i, _x in enumerate(a):
        if _i and a[_i - 1] in ("-f", "-F", "--field", "--raw-field") and "=" in _x and _x.split("=", 1)[1].isdigit():
            _ns.append(int(_x.split("=", 1)[1]))
    _n = next((x for x in _ns if str(x) in PARENTS or str(x) in ISSUES), _ns[0] if _ns else 0)
    _p = PARENTS.get(str(_n))
    print(json.dumps({"data": {"repository": {"issue": dict(_node(_n), parent=_node(_p) if _p else None)}}}))
    sys.exit(0)
_pp = next((x for x in a if re.fullmatch(r"/?repos/o/r/issues/\d+/parent", x)), None) if a[:1] == ["api"] else None
if _pp:
    _p = PARENTS.get(str(_num(_pp.rstrip("/").rsplit("/", 1)[0])))
    if not _p:
        sys.stderr.write("gh: Not Found (HTTP 404)\n")
        sys.exit(1)
    print(json.dumps(_rest(_p)))
    sys.exit(0)
_ip = next((x for x in a if re.fullmatch(r"/?repos/o/r/issues/\d+(/comments)?(\?.*)?", x)), None) if a[:1] == ["api"] else None
if _ip and (flag("-X", "--method") or "GET").upper() == "GET":
    _n = int(re.search(r"issues/(\d+)", _ip).group(1))
    if str(_n) in ISSUES:
        if "/comments" in _ip:
            print(json.dumps([{"id": i + 1, "html_url": c["url"], "user": {"login": c["login"]}, "body": c["body"],
                               "created_at": "2026-10-01T00:00:00Z"} for i, c in enumerate(ISSUES[str(_n)]["comments"])]))
        else:
            print(json.dumps(_rest(_n)))
        sys.exit(0)
if a[:2] == ["issue", "view"] and len(a) > 2 and not a[2].startswith("-") and str(_num(a[2])) in ISSUES:
    _n = _num(a[2])
    _i = ISSUES[str(_n)]
    print(json.dumps({"number": _n, "title": "Issue %d" % _n, "body": _i["body"], "url": _url(_n), "state": "OPEN",
                      "labels": [], "comments": [{"author": {"login": c["login"]}, "body": c["body"], "url": c["url"],
                                                  "createdAt": "2026-10-01T00:00:00Z"} for c in _i["comments"]]}))
    sys.exit(0)
'''.replace("__PARENTS__", repr({str(k): v for k, v in parents.items()})).replace("__ISSUES__", repr({str(k): v for k, v in issues.items()}))


# --- The plan review and the river: issue #57 (test_start's issue) is a story of parent #56; #58 is any other issue.

N, PARENT, OTHER = int(ts.N), 56, 58
PARENT_ASK = "Every card names the step that failed, in plain words."
PARENT_ISSUES = {
    PARENT: {"body": PARENT_ASK, "comments": [
        {"url": url(PARENT) + "#issuecomment-501", "login": ts.OWNER, "body": "The card should name the failing step, always."},
        {"url": url(PARENT) + "#issuecomment-502", "login": "stranger", "body": "Cards should name the step that broke."}]},
    OTHER: {"body": "Every card names the step that failed, in plain words.", "comments": []}}


def fake_with_parent(labels):
    """test_autopilot_river's fake GitHub, also knowing that #57's parent is #56, and #56's and #58's words."""
    base = tr.fake_gh(labels)
    marker = "INITIAL_LABELS = "
    assert marker in base, "test setup: could not find where to teach the fake GitHub about parents"
    return base.replace(marker, parent_snippet({N: PARENT}, PARENT_ISSUES) + marker, 1)


def decide(tmp, rec, comments, labels, fail_parent=False):
    """Decide what follows a run's record on #57, whose parent the fake GitHub knows.

    Runs `python3 -m dokima.agent next 57`.
    Returns what it printed, the card with its Next line, where it put the card on the board, and its stderr."""
    t = str(tmp)
    for d in ("bin", "gh", "out"):
        os.makedirs(f"{t}/{d}")
    open(f"{t}/bin/gh", "w").write(fake_with_parent(labels).replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    os.chmod(f"{t}/bin/gh", 0o755)
    json.dump({"fail_parent": fail_parent}, open(f"{t}/gh/options.json", "w"))
    json.dump({"number": N, "title": "Stuck issue", "body": "Fix it.", "comments": comments}, open(f"{t}/gh/issue.json", "w"))
    json.dump(rec, open(f"{t}/out/record.json", "w"))
    open(f"{t}/out/comment.md", "w").write(tr.agent.render(rec))
    env = {k: v for k, v in os.environ.items() if k != "PACK"}
    env.update(PATH=f"{t}/bin:" + os.environ["PATH"], FAKE_GH_DIR=f"{t}/gh", GITHUB_REPOSITORY="o/r",
               GITHUB_SERVER_URL="https://github.com", OWNERS=ts.OWNER, GH_TOKEN="fake-github-token", PYTHONPATH=ROOT)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "next", str(N), f"{t}/out"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=60)
    board = open(f"{t}/out/board.txt").read().strip() if os.path.exists(f"{t}/out/board.txt") else ""
    return p.stdout.strip(), open(f"{t}/out/comment.md").read(), board, p.stderr


def judged(**second):
    """An approving plan review of #57; its second assumption takes these fields."""
    return {**tr.APPROVE, "assumptions": [tr.ACCEPT_1, {**tr.ACCEPT_2, **second}]}


def round_review(tmp, source, parent):
    """Run the plan review's round check on #57, its answer citing this source.

    The pack names this parent and holds #57's plan with one question for the owner."""
    t = str(tmp)
    os.makedirs(os.path.join(t, "in"), exist_ok=True)
    question = {"kind": "question", "to": "owner", "text": "Should the card name the step that failed?",
                "raised_by": "planner", "id": "P1"}
    plan = {"role": "planner", "stage": None, "handback": {**ts.STORY, "raises": [question]},
            "check": {"passed": True, "problems": []}}
    json.dump(plan, open(os.path.join(t, "in", "01-planner.json"), "w"))
    json.dump([], open(os.path.join(t, "open_blockers.json"), "w"))
    open(os.path.join(t, "issue.md"), "w").write(f"# Issue #{N}: T\n\nFix it.\n\n## Comments\n")
    if parent is not None:
        json.dump({"number": parent}, open(os.path.join(t, "parent.json"), "w"))
    review = {**tr.APPROVE, "answers": [{"raise": "P1", "answer": "done", "why": "Your words settle it.",
                                         "words": "names the step that failed", "source": source, "changes": False}]}
    json.dump(review, open(os.path.join(t, "review.json"), "w"))
    env = {**os.environ, "STAGE": "plan", "PACK": t, "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com",
           "PYTHONPATH": ROOT}
    env.pop("PYTHONSAFEPATH", None)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "check-round", "reviewer", os.path.join(t, "review.json"), t],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr


def test_the_plan_reviews_check_accepts_the_owners_words_in_the_parent(record_property, tmp_path):
    """A plan review may cite the owner's words in the parent issue or its comments.

    Runs the real round check of a plan review of #57, whose pack names #56 as its parent, answering the plan's
    question for the owner. An answer whose source is #56 or a comment on #56 must pass. One whose source is #58, a
    comment on #58, or #56 when the pack names no parent must be rejected, the problem naming the question. Proves
    334.3."""
    record_property("proves", "334.3")
    for case, source in (("the parent", url(PARENT)), ("a comment on the parent", url(PARENT) + "#issuecomment-501")):
        code, out = round_review(tmp_path / case.replace(" ", "-"), source, PARENT)
        assert code == 0, f"334.3 ({case}): the plan review's check rejected the owner's words sourced to {source}:\n{out}"
    for case, source, parent in (("another issue", url(OTHER), PARENT),
                                 ("a comment on another issue", url(OTHER) + "#issuecomment-581", PARENT),
                                 ("the parent link with no parent in the pack", url(PARENT), None)):
        code, out = round_review(tmp_path / case.replace(" ", "-"), source, parent)
        assert code != 0 and "P1" in out, \
            f"334.3 ({case}): the plan review's check accepted words sourced to {source}:\n{out}"


def test_on_autopilot_the_owners_words_in_the_parent_count_as_really_said(record_property, tmp_path):
    """On autopilot, the owner's words in the parent issue let the river go on.

    Decides what follows an approving plan review of #57 (parent #56) with two questions, on autopilot. The worker
    must start when the second question's words are word for word in #56's own text, or in a code owner's comment
    on #56 that the source links. It must stop for the owner, naming that question, when the words are not in #56's
    text, when the comment on #56 is by someone who is not a code owner, and when the source is #58, even though
    #58's text holds the same words. Proves 334.3."""
    record_property("proves", "334.3")
    q2 = tr.QUESTIONS[1]["question"]
    good = (("the parent's own text", judged(matched="names the step that failed", source=url(PARENT))),
            ("a code owner's comment on the parent", judged(matched="name the failing step, always",
                                                          source=url(PARENT) + "#issuecomment-501")))
    for case, review in good:
        out, card, board, err = decide(tmp_path / case.replace(" ", "-").replace("'", ""), ts.review_record(review),
                                       tr.STORY_Q_PLANNED, tr.ON)
        assert out == "start worker", \
            f"334.3 ({case}): the owner's words in the parent did not let the worker start: {out!r} {tr.next_of(card)!r}\n{err[-800:]}"
        assert board == "Work none", f"334.3 ({case}): the card should be in Work without Needs you, not {board!r}"
    bad = (("words not in the parent's text", judged(matched="Show the cost of every run.", source=url(PARENT))),
           ("a stranger's comment on the parent", judged(matched="Cards should name the step that broke.",
                                                          source=url(PARENT) + "#issuecomment-502")),
           ("another issue holding the words", judged(matched="names the step that failed", source=url(OTHER))))
    for case, review in bad:
        out, card, board, err = decide(tmp_path / case.replace(" ", "-").replace("'", ""), ts.review_record(review),
                                       tr.STORY_Q_PLANNED, tr.ON)
        nxt = tr.next_of(card)
        assert out == "stop" and q2 in nxt and board == "Plan needs", \
            f"334.3 ({case}): words the owner did not say there let the river go on: {out!r} {nxt!r} {board!r}\n{err[-800:]}"


# --- The starting pack. -------------------------------------------------------------------------------------------

PACK_GH = r'''#!/usr/bin/env python3
"""A fake gh for building #331's starting pack: no comments, no pull requests, open issues 329 to 331."""
import json, os, re, sys
a = sys.argv[1:]
d = os.environ["FAKE_GH_DIR"]
opts = json.load(open(os.path.join(d, "options.json")))
def flag(*names):
    for name in names:
        if name in a:
            i = a.index(name)
            return a[i + 1] if i + 1 < len(a) else ""
    return None
''' + "__SNIPPET__" + r'''
if a[:2] == ["issue", "view"]:
    print(json.dumps({"number": 331, "title": "Story", "body": "the story", "url": "https://github.com/o/r/issues/331",
                      "state": "OPEN", "labels": [], "comments": []}))
elif a[:2] == ["pr", "list"]:
    print("" if (flag("-q") or flag("--jq")) else "[]")
elif a[:2] == ["issue", "list"]:
    print(json.dumps([{"number": n, "title": "Issue %d" % n, "body": "", "state": "OPEN"} for n in (329, 330, 331)]))
elif a[:1] == ["api"] and any(re.match(r"/?repos/o/r/issues(\?|$)", x) for x in a):
    items = [{"number": n, "title": "Issue %d" % n, "body": "", "state": "open"} for n in (329, 330, 331)]
    print(json.dumps([items] if "--slurp" in a else items))
elif a[:1] == ["api"] and "--paginate" in a:
    print("[]")
else:
    sys.stderr.write("fake gh: unsupported call: gh %s\n" % " ".join(a))
    sys.exit(1)
'''


def build_pack(tmp, role, stage, parents, fail_parent=False):
    """Build #331's starting pack against a fake GitHub with these parents.

    Runs `python3 -m dokima.agent pack`.
    Returns (the parent number parent.json names, or None when it is absent or names none; the command's stderr)."""
    t = str(tmp)
    for d in ("bin", "gh"):
        os.makedirs(f"{t}/{d}")
    script = PACK_GH.replace("__SNIPPET__", parent_snippet(parents, {PARENT_N: {"body": "the parent", "comments": []}}))
    open(f"{t}/bin/gh", "w").write(script.replace("#!/usr/bin/env python3", f"#!{sys.executable}"))
    os.chmod(f"{t}/bin/gh", 0o755)
    json.dump({"fail_parent": fail_parent}, open(f"{t}/gh/options.json", "w"))
    env = {k: v for k, v in os.environ.items() if k != "PACK"}
    env.update(PATH=f"{t}/bin:" + os.environ["PATH"], FAKE_GH_DIR=f"{t}/gh", GITHUB_REPOSITORY="o/r",
               GITHUB_SERVER_URL="https://github.com", GH_TOKEN="fake-github-token", PYTHONPATH=ROOT)
    p = subprocess.run([sys.executable, "-m", "dokima.agent", "pack", str(STORY_N), role, stage, f"{t}/pack"], cwd=ROOT,
                       env=env, capture_output=True, text=True, timeout=60)
    path = f"{t}/pack/parent.json"
    if not os.path.exists(path):
        return None, p.stderr
    return json.load(open(path)).get("number"), p.stderr


def test_the_starting_pack_names_the_issues_parent_from_github(record_property, tmp_path):
    """The planner's and plan reviewer's packs name the story's parent from GitHub.

    Builds #331's pack the way a run does, against a fake GitHub where #330 is #331's parent: the planner's pack and
    the plan reviewer's pack must hold parent.json naming 330. Where #331 has no parent, parent.json must name none. Proves 334.1."""
    record_property("proves", "334.1")
    for role, stage in (("planner", ""), ("reviewer", "plan")):
        number, err = build_pack(tmp_path / f"{role}-{stage}", role, stage, {STORY_N: PARENT_N})
        assert number == PARENT_N, f"334.1: the {role} {stage}'s pack does not name #330 as #331's parent: {number!r}\n{err[-800:]}"
    number, err = build_pack(tmp_path / "no-parent", "planner", "", {})
    assert number is None, f"334.1: the pack of an issue with no parent names #{number} as its parent"


def test_when_github_cannot_say_the_parent_only_the_own_issue_counts(record_property, tmp_path):
    """When GitHub cannot say the parent, no other issue counts as a source.

    Builds #331's pack while every parent lookup fails as GitHub does (HTTP 502): parent.json must name no parent,
    while the same pack built with GitHub answering names #330. Then decides what follows an approving plan review
    of #57 on autopilot whose assumption cites words in the parent #56: with the lookup failing the river must stop
    for the owner naming that question, and with GitHub answering the worker starts. Proves 334.4."""
    record_property("proves", "334.4")
    number, err = build_pack(tmp_path / "pack-ok", "planner", "", {STORY_N: PARENT_N})
    assert number == PARENT_N, f"334.4: setup: with GitHub answering, the pack does not name #330: {number!r}\n{err[-800:]}"
    number, err = build_pack(tmp_path / "pack-fail", "planner", "", {STORY_N: PARENT_N}, fail_parent=True)
    assert number is None, f"334.4: with GitHub failing to say the parent, the pack still names #{number} as the parent"
    review = ts.review_record(judged(matched="names the step that failed", source=url(PARENT)))
    out, card, board, err = decide(tmp_path / "river-ok", review, tr.STORY_Q_PLANNED, tr.ON)
    assert out == "start worker", f"334.4: setup: with GitHub answering, the parent's words did not count: {out!r}\n{err[-800:]}"
    out, card, board, err = decide(tmp_path / "river-fail", review, tr.STORY_Q_PLANNED, tr.ON, fail_parent=True)
    nxt = tr.next_of(card)
    assert out == "stop" and tr.QUESTIONS[1]["question"] in nxt and board == "Plan needs", \
        f"334.4: with GitHub failing to say the parent, the river went on on the parent's words: {out!r} {nxt!r} {board!r}"

"""The planner's hand-back: check its shape, then write it into the issue.

    python3 -m dokima.planner check N OUT   # fail loudly unless OUT holds a well-formed plan
    python3 -m dokima.planner post N OUT    # write the plan into issue N, or post the proposed split
    python3 -m dokima.planner rejected N OUT  # say on issue N why the run was rejected

The planner holds no GitHub key. It ends by writing one plan.json to OUT, of kind user_story or feature (see
dokima/roles/planner.md), raising its questions for the owner in its raises, plus its tests in tests/. Every
criterion's source is issue N, its parent issue named in the pack, or a comment on either; every test it names is in
the repo, filed under one of the plan's criteria. Every older test it changes, renames or deletes needs a reason in
test_changes. Every new test has a one-sentence summary, names each criterion it proves by number below it, and fails
on today's code. Criteria and the docstrings the planner adds are held to word caps (dokima/words.py): a little over
is listed, far over is rejected.
Nothing is posted unless `check` passes.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

from dokima import body as issue_body
from dokima import words
from dokima.checks import PROVES, TEST_DEF
from dokima.agent import pack_parent, problems_old, problems_raised  # noqa: E402

NEW_TEST_TIMEOUT = 60  # seconds one new test may run on today's code before it is stopped and rejected
CRITERION_CAP = 25  # words in a criterion's first sentence
DOCSTRING_CAP = 15  # words in the first line of a docstring the planner adds


class Garbled(Exception):
    pass


ALWAYS = ("the planner always hands back a plan, a plan.json of kind user_story or feature, "
          "raising its questions for the owner in raises")


def issue_link(number):
    """This issue's link on GitHub, from the repo the check runs in."""
    server = os.environ.get("GITHUB_SERVER_URL") or "https://github.com"
    return f"{server}/{os.environ.get('GITHUB_REPOSITORY', '')}/issues/{number}"


def read_output(out, number=None):
    """('plan', dict) or ('feature', str); Garbled if OUT holds anything else.

    Given the issue number, every criterion's source must be that issue's link, its parent's (named by parent.json in
    the pack $PACK), or one of their comment links.
    """
    if os.path.exists(os.path.join(out, "question.md")):
        raise Garbled(f"found question.md: {ALWAYS}")
    if not os.path.exists(os.path.join(out, "plan.json")):
        raise Garbled(f"found no plan.json: {ALWAYS}")
    try:
        p = json.load(open(os.path.join(out, "plan.json")))
    except ValueError as e:
        raise Garbled(f"plan.json is not valid JSON: {e}")
    if not isinstance(p, dict):
        raise Garbled(f"plan.json must be an object, not a {type(p).__name__}: {ALWAYS}")
    if "kind" not in p:
        raise Garbled(f"plan.json has no kind: {ALWAYS}")
    if number is None:
        return from_kind(p)
    parent = pack_parent(os.environ.get("PACK"))
    return from_kind(p, (issue_link(number), issue_link(parent)) if parent else issue_link(number),
                     pack_words(os.environ.get("PACK")))


def pack_words(pack_dir):
    """The owner's words by link (owner_words.json in the pack), or None when the pack has none."""
    path = os.path.join(pack_dir or "", "owner_words.json")
    if not pack_dir or not os.path.exists(path):
        return None
    try:
        v = json.load(open(path))
    except (OSError, ValueError):
        return None
    return v if isinstance(v, dict) else None


def check_words(where, c, said):
    """Garbled unless the criterion quotes, in `words`, the owner's own words found at its source.

    A criterion must deliver something the owner asked for; one with no words of theirs behind it is not a criterion.
    With no record of the owner's words (said is None), nothing is checked."""
    if said is None:
        return
    flat = lambda t: " ".join(str(t or "").split())
    words = flat(c.get("words"))
    if not words:
        raise Garbled(f"{where} has no words: quote the owner's exact words it delivers, copied from its source")
    if words not in flat(said.get((c.get("source") or "").strip())):
        raise Garbled(f"{where} quotes \"{words}\", which the owner did not write at {c.get('source')}: "
                      "quote their exact words from that issue or comment, or drop the criterion")


def strings(v):
    return isinstance(v, list) and all(isinstance(x, str) and x.strip() for x in v)


def check_source(where, source, issue):
    """Garbled unless the source is this issue's link or one of its comment links; no issue given, nothing to check.

    The issue may be a pair (this issue's link, its parent's link): then a link to the parent or its comments counts too."""
    if not issue:
        return
    links = (issue,) if isinstance(issue, str) else tuple(issue)
    if any(re.fullmatch(re.escape(link) + r"(#issuecomment-\d+)?", source.strip()) for link in links):
        return
    if len(links) == 1:
        raise Garbled(f"{where} has the source {source}, which is not this issue ({links[0]}) or one of its comments")
    raise Garbled(f"{where} has the source {source}, which is not this issue ({links[0]}), its parent ({links[1]}) "
                  "or a comment on either")


PER_STORY = 3


def count(s):
    """How many criteria a story holds: its acceptance criteria and non-functional requirements."""
    return len(s.get("acceptance_criteria") or []) + len(s.get("non_functional") or [])


def check_size(stories, nested=False):
    """Garbled unless the stories hold their criteria at 1 to 3 each, in exactly as many stories as the count needs.

    The size rule (#416): stories = criteria / 3, rounded up. 1 to 3 criteria is one story; 4 to 6 two; and so on, up to
    five stories. More than 15 criteria is too big for one issue: the owner breaks it up."""
    sizes = [count(s) for s in stories]
    total, need = sum(sizes), -(-sum(sizes) // PER_STORY)
    if nested and (len(stories) > 1 or total > PER_STORY):
        raise Garbled(f"this issue is already a story of its parent, so it never splits again: hand back one story of at "
                      f"most {PER_STORY} criteria (acceptance criteria and non-functional requirements together), and "
                      "ask the owner, in a question, which of the rest to drop")
    if need > 5:
        raise Garbled(f"the issue holds {total} criteria, more than 15, too big for one issue: hand back one story that "
                      "asks the owner, in a question, to break the issue up")
    if len(stories) != need:
        raise Garbled(f"{total} criteria make {need} {'story' if need == 1 else 'stories'} (3 at most each), not "
                      f"{len(stories)}: " + ("hand back one user_story" if need == 1 else f"split into exactly {need}"))
    big = [n for n, k in enumerate(sizes, 1) if k > PER_STORY]
    if big:
        raise Garbled(f"story {big[0]} holds {sizes[big[0] - 1]} criteria; each story holds 1 to 3")


def check_stories(stories, issue=None, said=None):
    """Garbled unless every story of a split is complete, its criteria cite this issue, and its dependencies point at
    the split's own stories with no loop. Stories are named counting from 1, as the split's card numbers them;
    depends_on counts from 0."""
    for n, s in enumerate(stories, 1):
        if not isinstance(s, dict):
            raise Garbled(f"story {n} must be an object with its title, user_story, acceptance_criteria and depends_on")
        for key in ("title", "user_story"):
            if not isinstance(s.get(key), str) or not s[key].strip():
                raise Garbled(f"story {n} has no {key}")
        ac = s.get("acceptance_criteria")
        if not isinstance(ac, list) or not ac:
            raise Garbled(f"story {n} needs acceptance_criteria as a non-empty list")
        for k, c in enumerate(ac, 1):
            if not isinstance(c, dict):
                raise Garbled(f"story {n}: acceptance criterion {k} must be an object with its text and source")
            for key in ("text", "source"):
                if not isinstance(c.get(key), str) or not c[key].strip():
                    raise Garbled(f"story {n}: acceptance criterion {k} has no {key}")
            check_source(f"story {n}: acceptance criterion {k}", c["source"], issue)
            check_words(f"story {n}: acceptance criterion {k}", c, said)
        nfr = s.get("non_functional", [])
        if not isinstance(nfr, list):
            raise Garbled(f"story {n} needs non_functional as a list (empty for none)")
        for k, c in enumerate(nfr, 1):
            if not isinstance(c, dict):
                raise Garbled(f"story {n}: non-functional requirement {k} must be an object with its text and why")
            for key in ("text", "why"):
                if not isinstance(c.get(key), str) or not c[key].strip():
                    raise Garbled(f"story {n}: non-functional requirement {k} needs its text and why as non-empty "
                                  f"text, and its {key} is not")
        if not isinstance(s.get("depends_on"), list):
            raise Garbled(f"story {n} needs depends_on as a list (empty for no dependencies)")
    last = len(stories) - 1
    for n, s in enumerate(stories, 1):
        for d in s["depends_on"]:
            if not isinstance(d, int) or isinstance(d, bool) or not 0 <= d <= last:
                raise Garbled(f"story {n} depends on {d!r}, which is no story index of this split (0 to {last})")
            if d == n - 1:
                raise Garbled(f"story {n} depends on itself")
    state = {}  # index -> "open" while on the path, "done" once every story it waits on is clear

    def visit(i, path):
        state[i] = "open"
        for d in stories[i]["depends_on"]:
            if state.get(d) == "open":
                loop = path[path.index(d):]
                raise Garbled("stories wait on each other in a loop: " + ", ".join(f"story {j + 1}" for j in loop))
            if d not in state:
                visit(d, path + [d])
        state[i] = "done"

    for i in range(len(stories)):
        if i not in state:
            visit(i, [i])


def from_kind(p, issue=None, said=None):
    """Read a plan.json written in the agreed shape (user_story or feature) into what the rest of the code uses.

    A story becomes a plan: its acceptance criteria come first, then its non-functional requirements, numbered N.1,
    N.2 ... in that order. A feature is shown to the owner as handed back, as a comment. Given this issue's link (or
    the pair of it and its parent's link), every criterion's source must be one of them or one of their comment links.
    """
    kind = p["kind"]
    bad = problems_old(p) + problems_raised("planner", p) if kind in ("feature", "user_story") else []
    if bad:
        raise Garbled("; ".join(bad))
    if kind in ("feature", "user_story") and (not isinstance(p.get("summary"), str) or not p["summary"].strip()):
        raise Garbled("plan.json needs a summary: one plain sentence saying what the issue is about")
    if kind == "feature":
        stories = p.get("stories")
        if not isinstance(stories, list) or not 2 <= len(stories) <= 5:
            raise Garbled("a feature needs 2 to 5 stories")
        check_stories(stories, issue, said)
        check_size(stories, isinstance(issue, tuple))
        return "feature", json.dumps(p, indent=2)
    if kind != "user_story":
        raise Garbled(f"plan.json kind is {kind!r}: {ALWAYS}")
    if not isinstance(p.get("user_story"), str) or not p["user_story"].strip():
        raise Garbled("a story needs a non-empty user_story")
    ac, nfr = p.get("acceptance_criteria"), p.get("non_functional", [])
    if not isinstance(ac, list) or not ac:
        raise Garbled("a story needs a non-empty list of acceptance_criteria")
    for k, c in enumerate(ac, 1):
        if not isinstance(c, dict):
            raise Garbled(f"acceptance criterion {k} must be an object with its text and source")
        for key in ("text", "source"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                raise Garbled(f"acceptance criterion {k} has no {'source link' if key == 'source' else key}: "
                              f"its {key} must be non-empty text")
        check_source(f"acceptance criterion {k}", c["source"], issue)
        check_words(f"acceptance criterion {k}", c, said)
    if not isinstance(nfr, list):
        raise Garbled("a story needs non_functional as a list (empty for none)")
    check_size([p], isinstance(issue, tuple))
    for k, c in enumerate(nfr, 1):
        if not isinstance(c, dict):
            raise Garbled(f"non-functional requirement {k} must be an object with its text and why")
        for key in ("text", "why"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                raise Garbled(f"non-functional requirement {k} needs its text and why as non-empty text, "
                              f"and its {key} is not")
        check_words(f"non-functional requirement {k}", c, said)
    if not strings(p.get("scope")) or not p["scope"]:
        raise Garbled("a story needs scope as a non-empty list of files")
    if not strings(p.get("out_of_scope", [])):
        raise Garbled("out_of_scope must be a list of sentences")
    tests = p.get("tests")
    if not isinstance(tests, dict) or not all(isinstance(k, str) and strings(v) for k, v in tests.items()):
        raise Garbled("a story needs tests as a map from each criterion (N.k) to its tests")
    tc = p.get("test_changes", {})
    if not isinstance(tc, dict) or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in tc.items()):
        raise Garbled("plan.json test_changes must map each changed older test to a non-empty reason")
    return "plan", {"objective": p["user_story"].strip(),
                    "criteria": [c["text"].strip() for c in ac] + [f"{c['text'].strip()} ({c['why'].strip()})" for c in nfr],
                    "non_goals": p.get("out_of_scope", []), "scope": p["scope"], "test_changes": tc,
                    "declared": tests, "raw": p}


def declared_by_test(declared):
    """Each test the plan names -> the criterion keys it is filed under."""
    by_test = {}
    for key, names in declared.items():
        for t in names:
            by_test.setdefault(t, []).append(key)
    return by_test


def declared_labels(tc, declared):
    """Use the criteria the plan declares for each test, never labels guessed from the test's text."""
    by_test = declared_by_test(declared)
    added = {t: by_test.get(t, []) for t in tc["added"]}
    renamed = tc.get("renamed", {})
    changed = {t: (old, by_test.get(renamed.get(t, t), old)) for t, (old, _) in tc["changed"].items()}
    return dict(tc, added=added, changed=changed)


def test_functions(text):
    """Each test function in a file: name -> (its source, the criterion keys it proves)."""
    out, name, block = {}, None, []
    for line in (text or "").splitlines() + ["\x00end"]:
        top = line[:1] not in ("", " ", "\t")
        if top and name:
            src = "\n".join(block).rstrip()
            out[name] = (src, PROVES.findall(src))
            name, block = None, []
        found = TEST_DEF.match(line)
        if found:
            name = found.group(1)
        if name:
            block.append(line)
    return out


def test_changes(paths, before, after):
    """Tests the planner touched, by path::name: added, changed (with their old keys) and deleted.

    A test whose source is unchanged apart from its name is a rename: a change, filed under its old name, with its
    new name under renamed (old -> new), a key that is there only when something was renamed.
    """
    added, changed, deleted, renamed = {}, {}, {}, {}
    for path in paths:
        old, new = test_functions(before(path)), test_functions(after(path))
        gone = [name for name in old if name not in new]
        for name, (src, keys) in new.items():
            if name not in old:
                was = next((o for o in gone if old[o][0].replace(f"def {o}(", f"def {name}(", 1) == src), None)
                if was:
                    gone.remove(was)
                    changed[f"{path}::{was}"] = (old[was][1], keys)
                    renamed[f"{path}::{was}"] = f"{path}::{name}"
                else:
                    added[f"{path}::{name}"] = keys
            elif old[name][0] != src:
                changed[f"{path}::{name}"] = (old[name][1], keys)
        for name in gone:
            deleted[f"{path}::{name}"] = old[name][1]
    return dict({"added": added, "changed": changed, "deleted": deleted}, **({"renamed": renamed} if renamed else {}))


def proving(tc):
    """Each added or changed test with the keys it proves now."""
    return dict(tc["added"], **{t: new for t, (_, new) in tc["changed"].items()})


def missing_tests(names):
    """The named tests (path::name) that are not in the repo: no such file, or no such test in it."""
    return [t for t in names if t.partition("::")[2] not in test_functions(read_now(t.partition("::")[0]))]


def problems(number, plan, files, tc, declared=None):
    """What is wrong with a plan and the tests it touched; empty when it can be posted.

    Given the tests the plan declares, each must be in the repo and filed under one of the plan's criteria, and an
    older test already in the repo counts as proof of the criteria it is filed under.
    """
    out = [f"{p} is outside tests/; the planner may only write tests" for p in files if not p.startswith("tests/")]
    if not tc["added"] and not tc["changed"]:
        out.append("the plan came with no tests")
    keys = {f"{number}.{k}" for k in range(1, len(plan["criteria"]) + 1)}
    proven = {k for ks in proving(tc).values() for k in ks}
    if declared is not None:
        names = sorted(declared_by_test(declared))
        out += [f"the plan names {t}, which is not in the repo" for t in missing_tests(names)]
        out += [f"tests are filed under {k}, which is not a criterion of this plan ({number}.1 to {number}.{len(keys)})"
                for k in sorted(declared) if k not in keys]
        proven |= {k for k, ts in declared.items() if ts}
    out += [f"criterion {k} has no test" for k in sorted(keys - proven)]
    out += [f"{t} proves {k}, which is not a criterion of this plan" for t, ks in tc["added"].items() for k in ks if k not in keys]
    out += [f"{t} now proves {k}, which is neither a criterion of this plan nor what it proved before"
            for t, (old, new) in tc["changed"].items() for k in new if k not in keys and k not in old]
    older = [t for t in tc["changed"] if not set(tc["changed"][t][0]) <= keys] + list(tc["deleted"])
    out += [f"{t} is an older test the planner changed or deleted, with no reason in test_changes"
            for t in older if t not in plan["test_changes"]]
    return out


def unreadable(paths):
    """Each test file that cannot be read as Python, with why."""
    out = []
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                ast.parse(f.read(), path)
        except (SyntaxError, ValueError) as e:
            out.append(f"{path} cannot be read as Python ({type(e).__name__}: {e})")
    return out


def one_sentence(line):
    """True when the line is one sentence ending in '.', '?' or '!', with no other sentence end inside it."""
    return bool(line) and line[-1] in ".?!" and not re.search(r"[.?!]\s", line)


def unsummarized(added):
    """The new tests (path::name) whose docstring's first line is not one sentence on one line."""
    out = []
    for path in sorted({t.partition("::")[0] for t in added}):
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
        for node in tree.body:
            t = f"{path}::{getattr(node, 'name', '')}"
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and t in added:
                doc = ast.get_docstring(node, clean=False) or ""
                if not one_sentence(doc.split("\n")[0].strip()):
                    out.append(f"{t} is a new test with no one-sentence summary: the first line of its docstring must "
                               f"be one sentence on one line, ending in '.', '?' or '!'")
    return out


def criterion_texts(p):
    """Each criterion of a plan or of a split's stories, as (how the check names it, its text)."""
    def of(owner, prefix=""):
        out = [(f"{prefix}acceptance criterion {k}", c["text"]) for k, c in enumerate(owner.get("acceptance_criteria", []), 1)]
        return out + [(f"{prefix}non-functional requirement {k}", c["text"])
                      for k, c in enumerate(owner.get("non_functional", []), 1)]
    if p.get("kind") == "feature":
        return [t for n, s in enumerate(p["stories"], 1) for t in of(s, f"story {n}: ")]
    return of(p)


def criterion_caps(p):
    """(listed, rejected) for each criterion whose first sentence runs over its cap."""
    return words.check([(where, words.first_sentence(text)) for where, text in criterion_texts(p)], CRITERION_CAP,
                       "opens with a sentence of")


def docstrings(path, text):
    """Each docstring in a file's source, by how the check names it (path, or path::name) -> its first line of text."""
    try:
        tree = ast.parse(text or "", path)
    except (SyntaxError, ValueError):
        return {}
    out = {}

    def visit(node, name):
        doc = ast.get_docstring(node, clean=False)
        if doc is not None:
            out[name] = next((line.strip() for line in doc.split("\n") if line.strip()), "")
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, f"{name}.{child.name}" if node is not tree else f"{path}::{child.name}")
    visit(tree, path)
    return out


def docstring_caps(paths, before, after):
    """(listed, rejected) for each docstring the planner added or rewrote whose first line runs over its cap.

    A docstring whose first line is the same as before is an older one left alone, and is not held to the cap.
    """
    texts = []
    for path in paths:
        old = docstrings(path, before(path))
        texts += [(where, line) for where, line in docstrings(path, after(path)).items() if old.get(where) != line]
    return words.check(texts, DOCSTRING_CAP, "has a docstring whose first line holds")


def unnumbered(added):
    """The new tests (path::name) whose docstring does not name, below its first line, each criterion it proves."""
    out = []
    for path in sorted({t.partition("::")[0] for t in added}):
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
        for node in tree.body:
            t = f"{path}::{getattr(node, 'name', '')}"
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and t in added:
                below = (ast.get_docstring(node, clean=False) or "").partition("\n")[2]
                for k in sorted(set(added[t])):
                    if not re.search(r"(?<![\d.])" + re.escape(k) + r"(?!\d|\.\d)", below):
                        out.append(f"{t} is a new test whose docstring does not name {k}, a criterion it proves, below "
                                   f"its first line: add 'Proves {k}.' to the paragraph under it")
    return out


def main_with_tests(base, into):
    """Lay main's code (`base`) into the folder `into`, with the branch's tests/ as they stand now on top.

    On a re-plan the branch may already hold the worker's code, so new tests are judged on main's code instead. The
    copy lives outside the repo, so the branch, its worktrees and its files stay exactly as they were.
    """
    tar = subprocess.run(["git", "archive", "--format=tar", base], check=True, capture_output=True).stdout
    with tempfile.TemporaryFile() as f:
        f.write(tar)
        f.seek(0)
        with tarfile.open(fileobj=f) as t:
            t.extractall(into, filter="data")
    shutil.rmtree(os.path.join(into, "tests"), ignore_errors=True)
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "tests"],
                            check=True, capture_output=True, text=True).stdout.split("\n")
    for p in listed:
        if p and os.path.isfile(p):
            os.makedirs(os.path.dirname(os.path.join(into, p)), exist_ok=True)
            shutil.copyfile(p, os.path.join(into, p))


def passing_today(added, base="HEAD"):
    """Run each new test (path::name) on main's code (`base`) with the planner's tests on top; the ones that pass or
    are skipped, or run past the limit."""
    out = []
    if not added:
        return out
    with tempfile.TemporaryDirectory() as into:
        main_with_tests(base, into)
        for t in sorted(added):
            try:
                r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", t], cwd=into,
                                   capture_output=True, text=True, timeout=NEW_TEST_TIMEOUT)
            except subprocess.TimeoutExpired:
                out.append(f"{t} is a new test still running after {NEW_TEST_TIMEOUT} s on today's code; it was stopped")
                continue
            if r.returncode in (0, 5):  # 0: passed or skipped, 5: nothing ran
                out.append(f"{t} is a new test that passes today (or is skipped); every new test must fail on today's code")
    return out


def render(number, body, plan, tags, older=()):
    """The issue body for a plan, in the format dokima.plan reads, with the owner's part kept below the marker."""
    return issue_body.redraw(body, plan_text(number, plan, tags, older))


def plan_text(number, plan, tags, older=()):
    """The plan's part of the issue body, written above the marker."""
    lines = [f"- [ ] Objective: {plan['objective'].strip()}"]
    for k, c in enumerate(plan["criteria"], 1):
        tests = sorted(t for t, ks in tags.items() if f"{number}.{k}" in ks)
        lines.append(f"  - [ ] Acceptance criteria: {c.strip()}")
        lines.append("    Verified by: " + (", ".join(f"`{t}`" for t in tests) or "no test"))
    lines.append("")
    if plan["non_goals"]:
        lines.append("**Out of scope:** " + "; ".join(x.strip() for x in plan["non_goals"]))
        lines.append("")
    if older:
        lines.append("**Changes to older tests:**")
        lines += [f"- `{t}`: {plan['test_changes'].get(t, 'no reason given')}" for t in older]
        lines.append("")
    lines.append("**Scope:**")
    lines += [f"- `{s.strip()}`" for s in plan["scope"]]
    return "\n".join(lines) + "\n"


def changed_files(base):
    """Every file the planner added or changed since `base`, committed or not, ignoring git-ignored files."""
    run = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout.split("\n")
    return sorted({p for p in run("diff", "--name-only", base) + run("ls-files", "--others", "--exclude-standard") if p})


def gh(*args, **kw):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, **kw).stdout


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def read_at(base):
    return lambda path: (lambda r: r.stdout if r.returncode == 0 else "")(git("show", f"{base}:{path}"))


def read_now(path):
    return open(path).read() if os.path.exists(path) else ""


def main(argv):
    action, number, out = argv[1], argv[2], argv[3]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if action == "rejected":
        path = os.path.join(out, "rejected.txt")
        why = open(path).read().strip() if os.path.exists(path) else "the planner run failed before handing anything back"
        run = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
        gh("issue", "comment", number, "-R", repo, "--body", f"**Plan rejected:** {why}\n\n[See the run]({run})")
        return 0
    try:
        kind, result = read_output(out, number)
        raw = result["raw"] if kind == "plan" else json.loads(result)
        listed, bad = words.style({k: v for k, v in raw.items() if k != "summary"})
        more, too_long = words.summary_caps(raw["summary"])
        listed, bad = more + listed, too_long + bad
        if kind == "plan":
            base = os.environ.get("PLANNER_BASE", "HEAD")
            files = changed_files(base)
            paths = [p for p in files if p.startswith("tests/") and p.endswith(".py")]
            broken = unreadable(paths)
            if broken:
                raise Garbled("; ".join(broken))
            tc = test_changes(paths, read_at(base), read_now)
            if "declared" in result:
                tc = declared_labels(tc, result["declared"])
            # Only what the planner changed in this run counts against "tests only": on a re-plan the branch may
            # already hold the worker's code, which is not the planner's doing.
            run_base = os.environ.get("PLANNER_RUN_BASE")
            own = changed_files(run_base) if run_base else files
            bad = problems(number, result, own, tc, result.get("declared")) + bad
            more, too_long = docstring_caps(paths, read_at(base), read_now)
            listed, bad = listed + more, bad + too_long
            bad += unsummarized(tc["added"]) + unnumbered(tc["added"]) + passing_today(tc["added"], base)
        for line in listed:
            print(f"::warning title=Over the word cap::{line}")
        if bad:
            raise Garbled("; ".join(bad))
    except Garbled as e:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "rejected.txt"), "w").write(str(e))
        print(f"::error title=Planner output rejected::{e}")
        return 1
    if action == "post":
        if kind == "feature":
            gh("issue", "comment", number, "-R", repo, "--body", f"**Planner proposes a split**\n\n```json\n{result}\n```")
        else:
            older = sorted(t for t in tc["changed"] if not set(tc["changed"][t][0]) <= {f"{number}.{k}" for k in range(1, len(result["criteria"]) + 1)}) + sorted(tc["deleted"])
            body = gh("issue", "view", number, "-R", repo, "--json", "body", "-q", ".body")
            body = body[:-1] if body.endswith("\n") else body  # gh ends its output with a newline of its own
            tags = dict(proving(tc), **declared_by_test(result["declared"]))
            if not issue_body.save(repo, number, body, plan_text(number, result, tags, older)):
                return 1
            gh("issue", "comment", number, "-R", repo, "--body",
               f"Plan written above, tests on `work/issue-{number}`. Add `work` to approve it.")
    print(kind)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

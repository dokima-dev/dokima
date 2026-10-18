"""A fake `gh` holding several repos at once, for the upstream filing tests (#745).

tests/test_upstream.py puts a small `gh` script on PATH that runs this file. Unlike tests/fake_gh.py, which knows one
repo, this one keeps a trial repo and Dokima's own repo side by side, so a test can see which repo each issue landed
in, and logs the GH_TOKEN every call ran with, so a test can see which key reached which repo.

The state lives in the JSON file named by UPSTREAM_GH_STATE:
    {"repos": {"OWNER/NAME": {"issues": {"N": {"title", "body", "state", "labels", "comments": [body, ...]}},
                              "labels": [name, ...]}},
     "next": {"OWNER/NAME": last number},
     "calls": [{"argv": [...], "repo": "OWNER/NAME" or null, "token": GH_TOKEN}],
     "unsupported": [{"argv": [...], "why": "..."}]}
A repo that is not in "repos" answers 404, as GitHub does for a repo the key cannot see.

What it answers, on any repo in the state:
    gh issue create --repo R --title T --body B | --body-file F [--label L]...   prints the new issue's URL
    gh issue comment N --repo R --body B | --body-file F                         prints the comment's URL
    gh issue list --repo R [--state open|closed|all] [--label L]... [--search Q] [--json F] [--limit N]
    gh issue view N --repo R [--json F]                                          the issue with its comments
    gh search issues [Q...] --repo R [--state S] [--label L]... [--json F] [--limit N]
    gh api [-X GET] repos/R/issues[?state=..&labels=..]                          list
    gh api -X POST repos/R/issues -f title=.. -f body=.. [-f labels[]=..]        create
    gh api [-X GET] repos/R/issues/N                                             one issue
    gh api [-X GET|POST] repos/R/issues/N/comments [-f body=..]                  list or add a comment
    gh api [-X GET] repos/R/labels[/NAME]; gh api -X POST repos/R/labels -f name=..
    gh api [-X GET] search/issues?q=..                                           {"items": [...]}
A search query matches an issue when every plain word is in its title or body, case left aside; the qualifiers
repo:, is:open, is:closed, is:issue, state:, label:, in:title and in:body narrow it as GitHub's do. `--json` returns
every field this fake knows, whatever fields were asked. `--jq`, `-q` and `--template` are refused: read the JSON in
code. Every other call is logged under "unsupported" and refused with exit 1.
"""
import json
import os
import re
import sys
import urllib.parse

STATE = os.environ["UPSTREAM_GH_STATE"]
SERVER = "https://github.com"


def load():
    """The fake GitHub's state."""
    with open(STATE) as f:
        return json.load(f)


def save(state):
    """Keep the state for the next call and for the test."""
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)


def done(state, out=None):
    """Save, print OUT (JSON unless text) and exit 0."""
    save(state)
    if out is not None:
        print(out if isinstance(out, str) else json.dumps(out))
    sys.exit(0)


def refuse(state, reason):
    """Answer as gh does when GitHub refuses: its reason on stderr, exit 1."""
    save(state)
    print(f"gh: {reason}", file=sys.stderr)
    sys.exit(1)


def unsupported(state, why):
    """Log a call this fake does not understand, and refuse it."""
    state.setdefault("unsupported", []).append({"argv": sys.argv[1:], "why": why})
    refuse(state, f"fake gh does not support this call: {why} (HTTP 400)")


def repo_of(state, name):
    """The repo NAME in the state, or a 404 when the key cannot see it."""
    if name not in state["repos"]:
        refuse(state, f"Could not resolve to a Repository with the name '{name}'. (HTTP 404)")
    return state["repos"][name]


def issue_json(name, n, i):
    """One issue as GitHub answers it, comments included."""
    return {"number": int(n), "id": int(n), "node_id": f"I_{n}", "title": i["title"], "body": i["body"],
            "state": i["state"], "labels": [{"name": l} for l in i.get("labels", [])],
            "url": f"{SERVER}/{name}/issues/{n}", "html_url": f"{SERVER}/{name}/issues/{n}",
            "repository_url": f"https://api.github.com/repos/{name}",
            "repository": {"nameWithOwner": name},
            "comments": [{"body": c} for c in i["comments"]], "comments_count": len(i["comments"]),
            "user": {"login": "dokima-runtime[bot]", "type": "Bot"}, "author": {"login": "app/dokima-runtime"}}


def create(state, name, title, body, labels):
    """Open an issue in repo NAME; returns its number."""
    r = repo_of(state, name)
    n = state.setdefault("next", {}).get(name, 0) + 1
    state["next"][name] = n
    r["issues"][str(n)] = {"title": title or "", "body": body or "", "state": "open", "labels": list(labels or []),
                           "comments": []}
    return n


def add_comment(state, name, n, body):
    """Comment on issue N of repo NAME."""
    r = repo_of(state, name)
    if str(n) not in r["issues"]:
        refuse(state, "Not Found (HTTP 404)")
    r["issues"][str(n)]["comments"].append(body or "")


def matches(i, query, want_state="open"):
    """True when issue I matches the search QUERY and the wanted state."""
    words, where, labels = [], ("title", "body"), []
    for tok in re.findall(r'"[^"]*"|\S+', query or ""):
        tok = tok.strip('"')
        low = tok.lower()
        if low.startswith(("repo:", "is:issue", "type:issue", "sort:", "author:", "user:", "org:")):
            continue
        if low in ("is:open", "state:open"):
            want_state = "open"
        elif low in ("is:closed", "state:closed"):
            want_state = "closed"
        elif low.startswith("label:"):
            labels.append(tok[6:].strip('"'))
        elif low.startswith("in:"):
            where = tuple(w for w in low[3:].split(",") if w in ("title", "body")) or where
        elif tok:
            words.append(low)
    if want_state not in ("all", i["state"]):
        return False
    if any(l not in i.get("labels", []) for l in labels):
        return False
    text = " ".join(i[w] for w in where).lower()
    return all(w in text for w in words)


def listed(state, name, want_state="open", labels=(), query=""):
    """The issues of repo NAME a list or search answers, oldest first."""
    r = repo_of(state, name)
    return [issue_json(name, n, i) for n, i in sorted(r["issues"].items(), key=lambda x: int(x[0]))
            if all(l in i.get("labels", []) for l in labels) and matches(i, query, want_state)]


def read_body(flags):
    """The --body or --body-file text of a gh call."""
    if "--body-file" in flags:
        path = flags["--body-file"][0]
        return sys.stdin.read() if path == "-" else open(path).read()
    return flags.get("--body", [None])[0]


SHORT = {"-R": "--repo", "-t": "--title", "-b": "--body", "-F": "--body-file", "-l": "--label", "-L": "--limit",
         "-s": "--state", "-S": "--search", "-q": "--jq"}
NO_VALUE = ("--web", "--paginate")


def parse(args):
    """(flags, positional) of a gh subcommand's arguments."""
    flags, positional, i = {}, [], 0
    while i < len(args):
        a = SHORT.get(args[i], args[i])
        if a.startswith("--") and "=" in a:
            k, _, v = a.partition("=")
            flags.setdefault(k, []).append(v)
            i += 1
        elif a.startswith("--") and a not in NO_VALUE:
            flags.setdefault(a, []).append(args[i + 1] if i + 1 < len(args) else "")
            i += 2
        elif a.startswith("--"):
            i += 1
        else:
            positional.append(a)
            i += 1
    return flags, positional


def issue_command(state, sub, args):
    """Answer `gh issue SUB ...`."""
    flags, positional = parse(args)
    if any(k in flags for k in ("--jq", "--template")):
        unsupported(state, "--jq and --template are not answered: read the JSON in code")
    name = flags.get("--repo", [None])[0]
    if not name:
        unsupported(state, f"gh issue {sub} without --repo")
    log(state, name)
    if sub == "create":
        n = create(state, name, flags.get("--title", [""])[0], read_body(flags),
                   [l for v in flags.get("--label", []) for l in v.split(",") if l])
        done(state, f"{SERVER}/{name}/issues/{n}")
    if sub == "list":
        labels = [l for v in flags.get("--label", []) for l in v.split(",") if l]
        done(state, listed(state, name, flags.get("--state", ["open"])[0], labels, flags.get("--search", [""])[0]))
    m = re.search(r"(\d+)$", positional[0]) if positional else None
    if not m:
        unsupported(state, f"gh issue {sub} without an issue number")
    n, r = m.group(1), repo_of(state, name)
    if n not in r["issues"]:
        refuse(state, f"Could not resolve to an issue with the number of {n}. (HTTP 404)")
    if sub == "view":
        done(state, issue_json(name, n, r["issues"][n]))
    if sub == "comment":
        add_comment(state, name, n, read_body(flags))
        done(state, f"{SERVER}/{name}/issues/{n}#issuecomment-{len(r['issues'][n]['comments'])}")
    unsupported(state, f"gh issue {sub}")


def search_command(state, args):
    """Answer `gh search issues ...`."""
    flags, positional = parse(args)
    if any(k in flags for k in ("--jq", "--template")):
        unsupported(state, "--jq and --template are not answered: read the JSON in code")
    name = flags.get("--repo", [None])[0]
    if not name:
        unsupported(state, "gh search issues without --repo")
    log(state, name)
    labels = [l for v in flags.get("--label", []) for l in v.split(",") if l]
    query = " ".join(positional) + "".join(f" in:{v}" for v in flags.get("--match", []))
    done(state, listed(state, name, flags.get("--state", ["all"])[0], labels, query))


def api_args(args):
    """(method, path, fields) of a `gh api` call."""
    method, path, fields, i = None, None, {}, 0
    while i < len(args):
        a = args[i]
        if a in ("-X", "--method"):
            method = args[i + 1].upper()
            i += 2
        elif a in ("-f", "--raw-field", "-F", "--field"):
            k, _, v = args[i + 1].partition("=")
            if a in ("-F", "--field") and v.startswith("@"):
                v = sys.stdin.read() if v == "@-" else open(v[1:]).read()
            if k.endswith("[]"):
                fields.setdefault(k[:-2], []).append(v)
            else:
                fields[k] = v
            i += 2
        elif a == "--input":
            fields.update(json.load(sys.stdin if args[i + 1] == "-" else open(args[i + 1])))
            i += 2
        elif a in ("--jq", "-q", "--template", "-t"):
            return None, None, None
        elif a in ("-H", "--header", "--hostname", "-p", "--preview", "--cache"):
            i += 2
        elif a.startswith("-"):
            i += 1
        elif path is None:
            path = a
            i += 1
        else:
            i += 1
    return method or ("POST" if fields else "GET"), path, fields


def api(state, args):
    """Answer `gh api ...`."""
    method, path, fields = api_args(args)
    if path is None:
        unsupported(state, "--jq and --template are not answered: read the JSON in code")
    path, _, query = path.lstrip("/").partition("?")
    params = {k: v for k, v in urllib.parse.parse_qsl(query)}
    if path == "search/issues" and method == "GET":
        q = params.get("q", fields.get("q", ""))
        m = re.search(r"\brepo:(\S+)", q)
        if not m:
            unsupported(state, "search/issues without repo:")
        log(state, m.group(1))
        done(state, {"total_count": 0, "items": listed(state, m.group(1), "all", (), q)})
    m = re.fullmatch(r"repos/([^/]+/[^/]+)/(.+)", path)
    if not m:
        unsupported(state, f"{method} {path}")
    name, rest = m.group(1), m.group(2)
    log(state, name)
    r = repo_of(state, name)
    if rest == "issues" and method == "GET":
        labels = [l for l in params.get("labels", "").split(",") if l]
        done(state, listed(state, name, params.get("state", "open"), labels))
    if rest == "issues" and method == "POST":
        labels = fields.get("labels") or []
        n = create(state, name, fields.get("title"), fields.get("body"), labels if isinstance(labels, list) else [labels])
        done(state, issue_json(name, n, r["issues"][str(n)]))
    im = re.fullmatch(r"issues/(\d+)(/comments)?", rest)
    if im:
        n = im.group(1)
        if n not in r["issues"]:
            refuse(state, "Not Found (HTTP 404)")
        if im.group(2) and method == "POST":
            add_comment(state, name, n, fields.get("body", ""))
            done(state, {"id": len(r["issues"][n]["comments"]), "body": fields.get("body", ""),
                         "html_url": f"{SERVER}/{name}/issues/{n}#issuecomment-{len(r['issues'][n]['comments'])}"})
        if im.group(2):
            done(state, [{"id": k, "body": c} for k, c in enumerate(r["issues"][n]["comments"], 1)])
        if method == "GET":
            done(state, issue_json(name, n, r["issues"][n]))
    if rest == "labels" and method == "POST":
        r.setdefault("labels", []).append(fields.get("name", ""))
        done(state, {"name": fields.get("name", "")})
    if rest == "labels" and method == "GET":
        done(state, [{"name": l} for l in r.get("labels", [])])
    lm = re.fullmatch(r"labels/(.+)", rest)
    if lm and method == "GET":
        label = urllib.parse.unquote(lm.group(1))
        if label not in r.get("labels", []):
            refuse(state, "Not Found (HTTP 404)")
        done(state, {"name": label})
    unsupported(state, f"{method} {path}")


def log(state, name):
    """Log this call with the repo it is on and the key it ran with."""
    state.setdefault("calls", []).append({"argv": sys.argv[1:], "repo": name, "token": os.environ.get("GH_TOKEN")})


def main(argv):
    """Answer one gh call."""
    state = load()
    if argv[:1] == ["issue"] and len(argv) > 1:
        issue_command(state, argv[1], argv[2:])
    if argv[:2] == ["search", "issues"]:
        search_command(state, argv[2:])
    if argv[:1] == ["api"]:
        api(state, argv[1:])
    log(state, None)
    unsupported(state, " ".join(argv[:2]))


if __name__ == "__main__":
    main(sys.argv[1:])

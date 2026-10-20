"""A fake `gh` for the drift audit's command tests, keeping GitHub in one JSON file.

tests/test_audit_cli.py copies this file onto PATH as `gh` and runs `python3 -m dokima.audit OWNER/REPO` against it.
The state lives in the file named by FAKE_GH_STATE; every call is logged there under "calls", every write under
"writes" (kind, repo, number), and every call this fake does not understand under "unsupported", where it also exits 1
so the audit sees a refused call. A read listed under "fail" answers as GitHub does when it refuses: GitHub's reason on
stderr ("gh: ... (HTTP 403)") and exit 1.

What it answers (OWNER/REPO is the state's repo; any other repo is logged as unsupported):
    gh api [-X GET] repos/OWNER/REPO/labels[?...]                       labels, as GitHub's REST list
    gh api -X POST repos/OWNER/REPO/labels -f name=.. -f color=.. -f description=..   creates a label (write "label");
                                                                        "fail" key "create_label"
    gh api [-X GET] repos/OWNER/REPO/branches/main/protection[/required_status_checks]
                                                                        main's rule; 404 "Branch not protected" if none
                                        its "strict" (must be up to date) is the state's "strict"[branch], true when absent
                                        the full rule lists the state's "review_bypass_apps" (app ids) as
                                        required_pull_request_reviews.bypass_pull_request_allowances.apps,
                                        requiring code owners unless the state's "code_owner_reviews" is false
    gh api [-X GET] repos/OWNER/REPO/rulesets[?...]                     the state's "rulesets" (none when absent), listed
    gh api [-X GET] repos/OWNER/REPO/rulesets/ID                        one of them in full; "fail" key "rulesets"
    gh api [-X GET] repos/OWNER/REPO/installation                       the app's {"app_id": 1, "permissions": {...}}
    gh api [-X GET] repos/OWNER/REPO/actions/variables/NAME             the state's "variables"[NAME]; 404 when unset
    gh api [-X GET] repos/OWNER/REPO/actions/secrets[?...]              the state's "secrets" (names), Dokima's two keys
                                                                        when absent; "fail" key "secrets"
    gh api [-X GET] repos/OWNER/REPO/issues[?state=...&labels=...]      issues (open unless state says otherwise)
    gh api [-X GET] repos/OWNER/REPO/issues/N[/comments]
    gh api [-X POST] repos/OWNER/REPO/issues -f title=.. -f body=.. [-f labels[]=..]   opens an issue
    gh api -X PATCH repos/OWNER/REPO/issues/N -f body=.. | -f state=closed            edits or closes it
    gh api [-X POST] repos/OWNER/REPO/issues/N/comments -f body=..                     comments on it
        (fields may also come as -F key=@file or --input file.json)
    gh issue create|edit|close|comment|pin|list|view ... --repo OWNER/REPO   the same, the gh way
    gh api graphql -f query=...  answering organization{projectV2{id fields{nodes{id name options{id name color
        description}}} views{nodes{id name layout filter}}}} and repository{issue(number:){id number title body state
        isPinned projectItems{nodes{id project{id}}}}}, and the mutations addProjectV2ItemById,
        updateProjectV2ItemPosition, updateProjectV2ItemFieldValue and pinIssue.
Ids: an issue's node id is I_<number>, its board item PVTI_I_<number>, a field F_<Field>, an option
O_<Field>_<Option with spaces as _>, the project PVT_1. Views come back with GitHub's layouts (TABLE_LAYOUT, ...).
No --jq, --template or --paginate output shaping: the audit reads the JSON itself.
"""
import json
import os
import re
import sys

STATE = os.environ["FAKE_GH_STATE"]


def load():
    """The fake GitHub's state."""
    with open(STATE) as f:
        return json.load(f)


def save(state):
    """Keep the state for the next call and for the test."""
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)


def refuse(state, reason, body=None):
    """Answer as gh does when GitHub refuses a call: GitHub's reason on stderr, exit 1."""
    save(state)
    if body is not None:
        print(json.dumps(body))
    print(f"gh: {reason}", file=sys.stderr)
    sys.exit(1)


def unsupported(state, why):
    """Log a call this fake does not understand, and refuse it."""
    state.setdefault("unsupported", []).append({"argv": sys.argv[1:], "why": why})
    refuse(state, f"fake gh does not support this call: {why} (HTTP 400)")


def reply(state, value):
    """Print a JSON answer and keep the state."""
    save(state)
    print(json.dumps(value))
    sys.exit(0)


def opt_id(field, option):
    """The node id of a board option."""
    return f"O_{field}_{option.replace(' ', '_')}"


def issue_json(state, n):
    """One issue as GitHub's REST answers it."""
    i = state["issues"][str(n)]
    return {"number": int(n), "node_id": f"I_{n}", "id": int(n), "title": i["title"], "body": i["body"],
            "state": i["state"], "labels": [{"name": l} for l in i.get("labels", [])],
            "user": {"login": "dokima-runtime[bot]", "type": "Bot"},
            "html_url": f"https://github.com/{state['repo']}/issues/{n}"}


def create(state, title, body, labels):
    """Open an issue and log the write."""
    state["next"] += 1
    n = state["next"]
    state["issues"][str(n)] = {"title": title or "", "body": body or "", "state": "open", "pinned": False,
                               "labels": list(labels or []), "comments": []}
    state["writes"].append({"kind": "create", "repo": state["repo"], "number": n})
    return n


def edit(state, n, changes):
    """Change an issue's body, title or state and log each write."""
    i = state["issues"].get(str(n))
    if i is None:
        unsupported(state, f"issue {n} does not exist")
    if "body" in changes:
        i["body"] = changes["body"]
        state["writes"].append({"kind": "edit", "repo": state["repo"], "number": int(n)})
    if "title" in changes:
        i["title"] = changes["title"]
        state["writes"].append({"kind": "edit", "repo": state["repo"], "number": int(n)})
    if "state" in changes:
        i["state"] = changes["state"]
        state["writes"].append({"kind": "close" if changes["state"] == "closed" else "reopen",
                                "repo": state["repo"], "number": int(n)})


def comment(state, n, body):
    """Comment on an issue and log the write."""
    i = state["issues"].get(str(n))
    if i is None:
        unsupported(state, f"issue {n} does not exist")
    i["comments"].append(body)
    state["writes"].append({"kind": "comment", "repo": state["repo"], "number": int(n)})


def pin(state, n):
    """Pin an issue and log the write."""
    if str(n) not in state["issues"]:
        unsupported(state, f"issue {n} does not exist")
    state["issues"][str(n)]["pinned"] = True
    state["writes"].append({"kind": "pin", "repo": state["repo"], "number": int(n)})


def value(raw, typed):
    """A -f/-F field's value: -F reads @file and turns numbers and booleans into JSON values."""
    if typed and raw.startswith("@"):
        return sys.stdin.read() if raw == "@-" else open(raw[1:]).read()
    if typed and re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if typed and raw in ("true", "false", "null"):
        return json.loads(raw)
    return raw


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
            v = value(v, a in ("-F", "--field"))
            if k.endswith("[]"):
                fields.setdefault(k[:-2], []).append(v)
            else:
                fields[k] = v
            i += 2
        elif a == "--input":
            fields.update(json.load(sys.stdin if args[i + 1] == "-" else open(args[i + 1])))
            i += 2
        elif a in ("-H", "--header", "--hostname", "-p", "--preview", "--cache"):
            i += 2
        elif a in ("--paginate", "--silent", "-i", "--include", "--verbose", "--slurp"):
            i += 1
        elif a in ("--jq", "-q", "--template", "-t"):
            return None, None, {"unsupported": a}
        elif path is None and not a.startswith("-"):
            path = a
            i += 1
        else:
            i += 1
    return method or ("POST" if fields else "GET"), path, fields


def rest(state, method, path, fields):
    """Answer one REST call on the state's repo."""
    path, _, query = path.lstrip("/").partition("?")
    params = dict(p.partition("=")[::2] for p in query.split("&") if p)
    prefix = f"repos/{state['repo']}/"
    if not path.startswith(prefix):
        unsupported(state, f"{method} {path} is not on the repo {state['repo']}")
    rest_path, fail = path[len(prefix):], state.get("fail", {})
    if method == "GET" and rest_path == "labels":
        if "labels" in fail:
            refuse(state, fail["labels"])
        reply(state, [{"id": k, "name": n, "color": l["color"], "description": l["description"], "default": False}
                      for k, (n, l) in enumerate(state["labels"].items())])
    if method == "POST" and rest_path == "labels":
        if "create_label" in fail:
            refuse(state, fail["create_label"])
        state["labels"][fields["name"]] = {"color": fields["color"], "description": fields.get("description", "")}
        state["writes"].append({"kind": "label", "repo": state["repo"], "number": None})
        reply(state, {"name": fields["name"], "color": fields["color"], "description": fields.get("description", "")})
    b = re.fullmatch(r"branches/([^/]+)", rest_path)
    if method == "GET" and b:
        if "protection" in fail:
            refuse(state, fail["protection"])
        checks = state["protection"].get(b.group(1))
        rule = None if checks is None else {"strict": state.get("strict", {}).get(b.group(1), True), "contexts": list(checks),
                                            "checks": [{"context": c, "app_id": None} for c in checks]}
        reply(state, {"name": b.group(1), "protected": rule is not None,
                      "protection": {"enabled": rule is not None, **({"required_status_checks": rule} if rule else {})}})
    m = re.fullmatch(r"branches/([^/]+)/protection(/required_status_checks)?", rest_path)
    if method == "GET" and m:
        if "protection" in fail:
            refuse(state, fail["protection"])
        checks = state["protection"].get(m.group(1))
        if checks is None:
            refuse(state, "Branch not protected (HTTP 404)",
                   {"message": "Branch not protected", "status": "404"})
        inner = {"strict": state.get("strict", {}).get(m.group(1), True), "contexts": list(checks), "checks": [{"context": c, "app_id": None} for c in checks]}
        if m.group(2):
            reply(state, inner)
        full = {"required_status_checks": inner}
        apps = state.get("review_bypass_apps")
        if apps is not None:
            full["required_pull_request_reviews"] = {
                "required_approving_review_count": 1,
                "require_code_owner_reviews": state.get("code_owner_reviews", True),
                "bypass_pull_request_allowances": {"users": [], "teams": [],
                                                   "apps": [{"id": a, "slug": f"app-{a}", "name": f"App {a}"}
                                                            for a in apps]}}
        reply(state, full)
    if method == "GET" and re.fullmatch(r"rulesets(/\d+)?", rest_path):
        if "rulesets" in fail:
            refuse(state, fail["rulesets"])
        have = state.get("rulesets", [])
        if rest_path == "rulesets":
            reply(state, [{"id": r["id"], "name": r["name"], "target": r["target"], "enforcement": r["enforcement"]}
                          for r in have])
        found = [r for r in have if str(r["id"]) == rest_path.split("/")[1]]
        if not found:
            refuse(state, "Not Found (HTTP 404)", {"message": "Not Found", "status": "404"})
        reply(state, found[0])
    if method == "GET" and rest_path == "installation":
        if "permissions" in fail:
            refuse(state, fail["permissions"])
        reply(state, {"id": 1, "app_id": 1, "app_slug": "dokima-runtime", "permissions": state["permissions"]})
    m = re.fullmatch(r"actions/variables/([A-Za-z0-9_]+)", rest_path)
    if method == "GET" and m:
        if "variables" in fail:
            refuse(state, fail["variables"])
        have = state.get("variables", {})
        if m.group(1) not in have:
            refuse(state, "Not Found (HTTP 404)", {"message": "Not Found", "status": "404"})
        reply(state, {"name": m.group(1), "value": have[m.group(1)], "created_at": "2026-10-01T00:00:00Z",
                      "updated_at": "2026-10-01T00:00:00Z"})
    if method == "GET" and rest_path == "actions/secrets":
        if "secrets" in fail:
            refuse(state, fail["secrets"])
        names = state.get("secrets", ["DOKIMA_APP_KEY", "CLAUDE_CODE_OAUTH_TOKEN"])
        reply(state, {"total_count": len(names), "secrets": [{"name": n, "created_at": "2026-10-01T00:00:00Z",
                                                              "updated_at": "2026-10-01T00:00:00Z"} for n in names]})
    if rest_path == "issues":
        if method == "GET":
            want = params.get("state", "open")
            labels = [l for l in params.get("labels", "").split(",") if l]
            reply(state, [issue_json(state, n) for n, i in sorted(state["issues"].items(), key=lambda x: int(x[0]))
                          if want in ("all", i["state"]) and all(l in i.get("labels", []) for l in labels)])
        if method == "POST":
            n = create(state, fields.get("title"), fields.get("body"), fields.get("labels"))
            reply(state, issue_json(state, n))
    m = re.fullmatch(r"issues/(\d+)(/comments)?", rest_path)
    if m and m.group(1) in state["issues"]:
        n = m.group(1)
        if m.group(2) and method == "GET":
            reply(state, [{"id": k, "body": c} for k, c in enumerate(state["issues"][n]["comments"])])
        if m.group(2) and method == "POST":
            comment(state, n, fields.get("body", ""))
            reply(state, {"id": 1, "body": fields.get("body", "")})
        if method == "GET":
            reply(state, issue_json(state, n))
        if method == "PATCH":
            edit(state, n, fields)
            reply(state, issue_json(state, n))
    unsupported(state, f"{method} {path}")


def project(state):
    """The board as GitHub's GraphQL answers it."""
    return {"id": "PVT_1", "number": 1, "title": "Board",
            "fields": {"nodes": [{"id": f"F_{f}", "name": f, "dataType": "SINGLE_SELECT",
                                  "options": [{"id": opt_id(f, o), "name": o, "color": v["color"],
                                               "description": v["description"]} for o, v in options.items()]}
                                 for f, options in state["fields"].items()]},
            "views": {"nodes": [{"id": f"PVTV_{k}", "name": n, "layout": v["layout"].upper() + "_LAYOUT",
                                 "filter": v["filter"], "number": k + 1}
                                for k, (n, v) in enumerate(state["views"].items())]}}


def graphql(state, fields):
    """Answer one GraphQL query or mutation."""
    q = fields.pop("query", "")
    every = q + " " + " ".join(str(v) for v in fields.values())
    if re.match(r"\s*mutation", q):
        if "addProjectV2ItemById" in q:
            m = re.search(r"\bI_(\d+)\b", every)
            if not m:
                unsupported(state, "addProjectV2ItemById without an issue id")
            item = f"PVTI_I_{m.group(1)}"
            state["items"].setdefault(item, {})
            state["writes"].append({"kind": "board", "repo": state["repo"], "number": int(m.group(1))})
            reply(state, {"data": {"addProjectV2ItemById": {"item": {"id": item}}}})
        if "updateProjectV2ItemPosition" in q:
            reply(state, {"data": {"updateProjectV2ItemPosition": {"clientMutationId": None}}})
        if "updateProjectV2ItemFieldValue" in q:
            item = re.search(r"\bPVTI_I_\d+\b", every)
            field = re.search(r"\bF_([A-Za-z]+)\b", every)
            option = re.search(r"\bO_[A-Za-z]+_[A-Za-z_]+\b", every)
            if not (item and field and option) or item.group(0) not in state["items"]:
                unsupported(state, "updateProjectV2ItemFieldValue without an item on the board, a field and an option")
            state["items"][item.group(0)][field.group(1)] = option.group(0)
            state["writes"].append({"kind": "board", "repo": state["repo"], "number": int(item.group(0)[7:])})
            reply(state, {"data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": item.group(0)}}}})
        if "pinIssue" in q:
            m = re.search(r"\bI_(\d+)\b", every)
            if not m:
                unsupported(state, "pinIssue without an issue id")
            pin(state, m.group(1))
            reply(state, {"data": {"pinIssue": {"issue": {"id": m.group(0)}}}})
        unsupported(state, f"mutation {q[:80]!r}")
    data = {}
    if "organization" in q or "projectV2" in q:
        if "board" in state.get("fail", {}):
            refuse(state, state["fail"]["board"])
        data["organization"] = {"projectV2": project(state)}
    if "repository" in q:
        repo = {"id": "R_1", "nameWithOwner": state["repo"]}
        m = re.search(r"issue\(\s*number:\s*(?:\$(\w+)|(\d+))", q)
        if m:
            n = str(fields.get(m.group(1)) if m.group(1) else m.group(2))
            if n not in state["issues"]:
                unsupported(state, f"issue {n} does not exist")
            i = state["issues"][n]
            item = f"PVTI_I_{n}"
            repo["issue"] = {"id": f"I_{n}", "number": int(n), "title": i["title"], "body": i["body"],
                             "state": i["state"].upper(), "isPinned": i["pinned"],
                             "projectItems": {"nodes": [{"id": item, "project": {"id": "PVT_1"}}]
                                              if item in state["items"] else []}}
        data["repository"] = repo
    if not data:
        unsupported(state, f"query {q[:80]!r}")
    reply(state, {"data": data})


def issue_command(state, sub, args):
    """Answer `gh issue <sub> ...` the way gh does."""
    flags, positional, i = {}, [], 0
    short = {"-R": "--repo", "-t": "--title", "-b": "--body", "-F": "--body-file", "-l": "--label",
             "-c": "--comment", "-L": "--limit", "-s": "--state", "-S": "--search", "-r": "--reason"}
    while i < len(args):
        a = short.get(args[i], args[i])
        if a.startswith("--") and "=" in a:
            k, _, v = a.partition("=")
            flags.setdefault(k, []).append(v)
            i += 1
        elif a.startswith("--") and a not in ("--web",):
            flags.setdefault(a, []).append(args[i + 1] if i + 1 < len(args) else "")
            i += 2
        else:
            positional.append(a)
            i += 1
    if flags.get("--repo", [None])[0] != state["repo"]:
        unsupported(state, f"gh issue {sub} on {flags.get('--repo')}, not --repo {state['repo']}")
    body = flags.get("--body", [None])[0]
    if "--body-file" in flags:
        path = flags["--body-file"][0]
        body = sys.stdin.read() if path == "-" else open(path).read()
    n = re.search(r"(\d+)$", positional[0]).group(1) if positional else None
    if sub == "create":
        n = create(state, flags.get("--title", [""])[0], body, flags.get("--label", []))
        save(state)
        print(f"https://github.com/{state['repo']}/issues/{n}")
        sys.exit(0)
    if n is None or n not in state["issues"]:
        if sub == "list":
            want = flags.get("--state", ["open"])[0]
            labels = flags.get("--label", [])
            reply(state, [dict(issue_json(state, k), id=f"I_{k}", state=i["state"].upper(), isPinned=i["pinned"])
                          for k, i in sorted(state["issues"].items(), key=lambda x: int(x[0]))
                          if want in ("all", i["state"]) and all(l in i.get("labels", []) for l in labels)])
        unsupported(state, f"gh issue {sub} without an existing issue")
    if sub == "view":
        i = state["issues"][n]
        reply(state, dict(issue_json(state, n), id=f"I_{n}", state=i["state"].upper(), isPinned=i["pinned"],
                          comments=[{"body": c} for c in i["comments"]]))
    if sub == "edit":
        changes = {}
        if body is not None:
            changes["body"] = body
        if "--title" in flags:
            changes["title"] = flags["--title"][0]
        edit(state, n, changes)
        reply(state, {})
    if sub == "comment":
        comment(state, n, body or "")
        save(state)
        print(f"https://github.com/{state['repo']}/issues/{n}#issuecomment-1")
        sys.exit(0)
    if sub == "close":
        if "--comment" in flags:
            comment(state, n, flags["--comment"][0])
        edit(state, n, {"state": "closed"})
        reply(state, {})
    if sub == "pin":
        pin(state, n)
        reply(state, {})
    unsupported(state, f"gh issue {sub}")


def main(argv):
    """Log the call, then answer it from the state."""
    state = load()
    state["calls"].append(argv)
    if argv[:2] == ["api", "graphql"]:
        method, path, fields = api_args(argv[2:])
        if "unsupported" in fields:
            unsupported(state, f"gh api {fields['unsupported']}")
        graphql(state, fields)
    if argv[:1] == ["api"]:
        method, path, fields = api_args(argv[1:])
        if "unsupported" in fields or path is None:
            unsupported(state, "gh api without a path, or with output shaping")
        if path.lstrip("/") == "graphql":
            graphql(state, fields)
        rest(state, method, path, fields)
    if argv[:1] == ["issue"] and len(argv) > 1:
        issue_command(state, argv[1], argv[2:])
    unsupported(state, " ".join(argv[:2]))


if __name__ == "__main__":
    main(sys.argv[1:])

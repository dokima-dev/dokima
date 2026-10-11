"""Everything Dokima needs from GitHub, declared in one place.

Labels, board fields and options, views, required checks, branch rules and the app's permissions. Plain data; nothing
here calls GitHub.

    python3 -m dokima.manifest [root]   # prints every setting the code or workflows rely on that is left out here

undeclared(root) reads the Python under dokima/ and the workflows under .github/workflows/ and names, with the file,
every label, field, option, view, check or branch rule they rely on that is not declared below, and every GitHub call
made as the app whose permission, at the level it needs, is not granted below. A call it cannot tie to a permission is
named too, so a new kind of call never slips through.
"""
import ast
import os
import re
import sys

LABELS = {
    "plan": {"color": "1d76db", "description": "Starts the planner"},
    "work": {"color": "0e8a16", "description": "Starts the worker on the approved plan"},
    "autopilot": {"color": "8250df", "description": "Running on its own"},
    "high": {"color": "d93f0b", "description": "Priority: high"},
    "parked": {"color": "c5c5c5", "description": "Priority: parked for later"},
}

FIELDS = {
    "Status": {
        "Backlog": {"color": "GRAY", "description": "Not started"},
        "Plan": {"color": "BLUE", "description": "Being planned"},
        "Work": {"color": "YELLOW", "description": "Being built"},
        "Review": {"color": "ORANGE", "description": "Being reviewed"},
        "Done": {"color": "GREEN", "description": "Merged or closed"},
    },
    "Action": {
        "Needs you": {"color": "RED", "description": "Waiting for the owner"},
        "Autopilot": {"color": "PURPLE", "description": "Running on its own"},
    },
    "Priority": {
        "Blocker": {"color": "RED", "description": "Blocks other work"},
        "High": {"color": "ORANGE", "description": "High priority"},
        "Parked": {"color": "GRAY", "description": "Parked for later"},
    },
}

# Merged and closed items keep their label, so the Autopilot view shows only open ones.
VIEWS = {
    "Autopilot": {"layout": "table", "filter": "label:autopilot is:open"},
}

CHECKS = ["all tests", "Acceptance criteria"]

BRANCH_RULES = {
    "main": {"required_checks": ["all tests", "Acceptance criteria"]},
}

PERMISSIONS = {
    "contents": "write",
    "pull_requests": "write",
    "issues": "write",
    "checks": "read",
    "actions": "write",
    "statuses": "read",
    "metadata": "read",
    "workflows": "write",
    "administration": "read",
    "organization_projects": "write",
}

LEVEL = {"read": 1, "write": 2}
NONE = ""  # a call that needs no app permission

# gh's own commands: (command, subcommand) -> (permission, level)
GH_COMMANDS = {
    **{("issue", s): ("issues", "read") for s in ("view", "list", "status")},
    **{("issue", s): ("issues", "write") for s in ("comment", "create", "edit", "close", "reopen", "delete", "lock",
                                                   "unlock", "pin", "unpin", "transfer")},
    **{("pr", s): ("pull_requests", "read") for s in ("view", "list", "status", "diff", "checks")},
    **{("pr", s): ("pull_requests", "write") for s in ("comment", "create", "edit", "close", "reopen", "review",
                                                       "ready", "lock", "unlock")},
    ("pr", "merge"): ("contents", "write"),
    **{("run", s): ("actions", "read") for s in ("view", "list", "download", "watch")},
    **{("run", s): ("actions", "write") for s in ("rerun", "cancel", "delete")},
}

# REST paths inside a repo (after repos/<owner>/<name>/), first match wins: (pattern, permission)
REPO_PATHS = [
    (r"branches/[^/]+/protection", "administration"),
    (r"rules/branches/", "metadata"),
    (r"commits/[^/]+/check-runs|check-runs|check-suites", "checks"),
    (r"commits/[^/]+/status(es)?$|statuses/", "statuses"),
    (r"commits/[^/]+/pulls$", "pull_requests"),
    (r"issues(/|$)|labels(/|$)|milestones(/|$)", "issues"),
    (r"pulls(/|$)", "pull_requests"),
    (r"actions/", "actions"),
    (r"commits(/|$)|compare/|contents/|git/|dispatches$|branches(/[^/]+)?$|merges$", "contents"),
    (r"installation$", NONE),  # the app's own installation: GitHub answers it to the app's key, not a permission
]
# REST paths outside a repo: (pattern, permission)
OTHER_PATHS = [
    (r"orgs/[^/]+/projectsV2(/|$)", "organization_projects"),
    (r"users/|installation/token$", NONE),
]
# What a GraphQL query or mutation touches: (pattern, permission)
GRAPHQL = [
    (r"projectV2|ProjectV2|projectItems", "organization_projects"),
    (r"\bissues?\s*\(|\blabels\s*\(", "issues"),
    (r"\bpullRequests?\s*\(", "pull_requests"),
]
GRAPHQL_OP = re.compile(r"\s*(query|mutation)\s*(\w+\s*)?[({]")
VALUE_FLAGS = {"-f", "-F", "--field", "--raw-field", "-H", "--header", "--jq", "-q", "--template", "-t", "--input",
               "--cache", "-p", "--preview", "--hostname"}
FIELD_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}
BRANCH_RULE = re.compile(r"(?:rules/branches/([\w.\-]+)|branches/([\w.\-]+)/protection)")
LABEL_FIELD = re.compile(r"labels\[\]=([^\s\"'{}]+)")


def normalize(path):
    """The path with every variable as {} and no query string."""
    path = re.sub(r"\$\{\{[^}]*\}\}|\$\{\w+\}|\$\w+", "{}", path)
    return path.split("?")[0].strip("/")


def permission(path):
    """(permission, known) behind a REST path; permission is NONE for calls that need none."""
    segs = path.split("/")
    if segs[0] == "repos" and len(segs) > 2:
        rest = segs[3:] if segs[1] == "{}" and segs[2] == "{}" or segs[1] != "{}" else segs[2:]
        rest = "/".join(rest)
        for pattern, perm in REPO_PATHS:
            if re.match(pattern, rest):
                return perm, True
        return None, False
    for pattern, perm in OTHER_PATHS:
        if re.match(pattern, path):
            return perm, True
    return None, False


def graphql(text):
    """[(permission, level)] a GraphQL query or mutation needs; empty when it touches nothing known."""
    level = "write" if GRAPHQL_OP.match(text).group(1) == "mutation" else "read"
    return [(perm, level) for pattern, perm in GRAPHQL if re.search(pattern, text)]


class Report:
    def __init__(self):
        self.lines = []

    def add(self, path, line):
        line = f"{path}: {line}"
        if line not in self.lines:
            self.lines.append(line)

    def need(self, path, call, perm, level):
        """Name the call when the manifest grants its permission below the level it needs."""
        if perm == NONE:
            return
        have = PERMISSIONS.get(perm)
        if LEVEL.get(have, 0) < LEVEL[level]:
            self.add(path, f"{call} needs the app permission {perm}: {level}, and the manifest grants "
                           f"{perm + ': ' + have if have else 'none'}")

    def unknown(self, path, call):
        self.add(path, f"{call} is a GitHub call the manifest cannot tie to an app permission")

    def rest(self, path, method, url):
        """A REST call: its branch rule and the permission behind it."""
        url = normalize(url)
        if url == "graphql":
            return  # the query or mutation itself is checked where it is written
        call = f"{method} {url}"
        perm, known = permission(url)
        if not known:
            return self.unknown(path, call)
        self.need(path, call, perm, "read" if method == "GET" else "write")

    def gh_api(self, path, args):
        """`gh api` with its arguments, None for a value the code does not write out."""
        method, url, fields, i = None, None, False, 0
        while i < len(args):
            a = args[i]
            if a in ("-X", "--method"):
                method = args[i + 1] if i + 1 < len(args) else None
                method = method.upper() if method else "PATCH"  # unknown: count it as a write
                i += 2
                continue
            if a in VALUE_FLAGS:
                fields = fields or a in FIELD_FLAGS
                i += 2
                continue
            if url is None and not (a or "").startswith("-"):
                if a is None:
                    return  # a wrapper passing on a path it was given
                url = a
            i += 1
        if url is None or url.startswith("{"):
            return
        self.rest(path, method or ("POST" if fields else "GET"), url)

    def gh_command(self, path, command, sub):
        call = f"gh {command} {sub or '?'}"
        if (command, sub) not in GH_COMMANDS:
            return self.unknown(path, call)
        self.need(path, call, *GH_COMMANDS[(command, sub)])

    def graphql(self, path, text):
        op = GRAPHQL_OP.match(text).group(1)
        needs = graphql(text)
        if not needs:
            return self.unknown(path, f"GraphQL {op} {text[:60]!r}")
        for perm, level in needs:
            self.need(path, f"GraphQL {op}", perm, level)

    def label(self, path, name):
        if name not in LABELS:
            self.add(path, f"label {name!r} is not in the manifest's labels")

    def branch_rules(self, path, text):
        for m in BRANCH_RULE.finditer(text):
            branch = m.group(1) or m.group(2)
            if branch not in BRANCH_RULES:
                self.add(path, f"branch rule of {branch!r} is not in the manifest's branch rules")


# Python

class Scope:
    """String names assigned once in a function or module, read by text()."""

    def __init__(self, body, up=None):
        self.up, self.names, seen = up, {}, set()
        for node in body:
            for n in ast.walk(node) if up else [node]:
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                    name = n.targets[0].id
                    if name in seen:
                        self.names[name] = None
                    else:
                        seen.add(name)
                        ok = isinstance(n.value, ast.JoinedStr) or (isinstance(n.value, ast.Constant)
                                                                   and isinstance(n.value.value, str))
                        self.names[name] = n.value if ok else None

    def get(self, name):
        if name in self.names:
            return self.names[name]
        return self.up.get(name) if self.up else None


def text(node, scope, depth=0):
    """The string a node writes, unreadable values as {}; None when it writes none."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        out = ""
        for part in node.values:
            if isinstance(part, ast.Constant):
                out += str(part.value)
            else:
                inner = text(part.value, scope, depth + 1) if isinstance(part.value, ast.Name) else None
                out += inner if inner is not None and depth < 3 else "{}"
        return out
    if isinstance(node, ast.Name) and depth < 3:
        value = scope.get(node.id)
        return text(value, scope, depth + 1) if value is not None else None
    return None


def called(node):
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def check_python(report, path, source):
    tree = ast.parse(source)
    module = Scope(tree.body)
    scopes = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = Scope(fn.body, module)
            for n in ast.walk(fn):
                scopes.setdefault(id(n), scope)
    parts = {id(p) for n in ast.walk(tree) if isinstance(n, ast.JoinedStr) for p in n.values}
    for node in ast.walk(tree):
        scope = scopes.get(id(node), module)
        if isinstance(node, (ast.Constant, ast.JoinedStr)) and id(node) not in parts:
            s = text(node, scope)
            if s is None:
                continue
            report.branch_rules(path, s)
            for name in LABEL_FIELD.findall(s):
                report.label(path, name)
            if GRAPHQL_OP.match(s):
                report.graphql(path, s)
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "labels[]":
                    name = text(v, scope)
                    if name:
                        report.label(path, name)
        elif isinstance(node, ast.Compare):
            left = node.left
            if (isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name)
                    and isinstance(left.slice, ast.Constant) and left.slice.value == "name"
                    and len(node.ops) == 1 and isinstance(node.ops[0], (ast.Eq, ast.NotEq))):
                name = text(node.comparators[0], scope)
                # A name compared with a declared view's is the view being looked up, not a check.
                if name is not None and name not in CHECKS and name not in VIEWS:
                    report.add(path, f"check {name!r} is not in the manifest's required checks")
        elif isinstance(node, ast.Call):
            python_call(report, path, node, scope)
    return report


def python_call(report, path, node, scope):
    name, args = called(node), node.args
    strings = [text(a, scope) for a in args]
    if name == "set" and isinstance(node.func, ast.Attribute) and len(args) == 3 and strings[1] is not None:
        field = strings[1]
        if field not in FIELDS:
            report.add(path, f"board field {field!r} is not in the manifest's fields")
        else:
            option = args[2]
            options = [option.body, option.orelse] if isinstance(option, ast.IfExp) else [option]
            for o in options:
                o = text(o, scope)
                if o is not None and o not in FIELDS[field]:
                    report.add(path, f"option {o!r} of the board field {field} is not in the manifest's fields")
    elif name == "add_view" and args and strings[0] is not None:
        if strings[0] not in VIEWS:
            report.add(path, f"view {strings[0]!r} is not in the manifest's views")
    elif name == "gh" and args and strings[0] is not None:
        if strings[0] == "api":
            report.gh_api(path, strings[1:])
        else:
            report.gh_command(path, strings[0], strings[1] if len(args) > 1 else None)
    elif name in ("rest", "api") and len(args) >= 2 and strings[1] is not None and not strings[1].startswith("{"):
        method = strings[0].upper() if strings[0] else "PATCH"  # a method the code does not write out counts as a write
        report.rest(path, method, strings[1])


# Workflows

APP_TOKEN = re.compile(r"GH_TOKEN:\s*\$\{\{\s*steps\.[\w-]+\.outputs\.token\s*\}\}")
STARTS = r"(?:^|[;&|(]|\$\(|\bthen\b|\bdo\b|\belse\b|\bif\b|!)\s*"
GH = re.compile(STARTS + r"gh\s+([\w-]+)")
PUSH = re.compile(STARTS + r"git\s+push\b")
TOKEN = re.compile(r"\"[^\"]*\"|'[^']*'|[^\s)]+")


def steps(lines):
    """Each list item of the workflow, with the lines under it."""
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"(\s*)- ", lines[i])
        if not m:
            i += 1
            continue
        indent, block = len(m.group(1)), [lines[i]]
        i += 1
        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
            block.append(lines[i])
            i += 1
        out.append(block)
    return out


def check_workflow(report, path, source):
    for name in re.findall(r"github\.event\.label\.name\s*==\s*'([^']+)'", source):
        report.label(path, name)
    for name in LABEL_FIELD.findall(source):
        report.label(path, name)
    for perm, level in re.findall(r"permission-([\w-]+):\s*['\"]?(read|write)", source):
        report.need(path, f"the app token's permission-{perm}", perm.replace("-", "_"), level)
    report.branch_rules(path, source)
    for block in steps(source.splitlines()):
        app = any(APP_TOKEN.search(l) for l in block)
        script = "\n".join(l for l in block if not l.strip().startswith("#")).replace("\\\n", " ")
        for line in script.splitlines():
            if PUSH.search(line) and (app or re.search(r"steps\.[\w-]+\.outputs\.token", line)):
                report.need(path, "git push", "contents", "write")
            if not app:
                continue
            for m in GH.finditer(line):
                command, args = m.group(1), [t.strip("\"'") for t in TOKEN.findall(line[m.end():])]
                if command != "api":
                    report.gh_command(path, command, args[0] if args else None)
                elif args and args[0] == "graphql":
                    q = re.search(r"(query|mutation)\s*(\w+\s*)?[({].*", line[m.end():])
                    report.graphql(path, q.group(0)) if q else report.unknown(path, "gh api graphql")
                else:
                    report.gh_api(path, args)


def undeclared(root):
    """One line, naming the file, per setting under root the manifest leaves out."""
    report = Report()
    code = os.path.join(root, "dokima")
    for folder, dirs, files in sorted(os.walk(code)):
        dirs.sort()
        for f in sorted(files):
            if f.endswith(".py"):
                full = os.path.join(folder, f)
                check_python(report, os.path.relpath(full, root).replace(os.sep, "/"), open(full).read())
    flows = os.path.join(root, ".github", "workflows")
    if os.path.isdir(flows):
        for f in sorted(os.listdir(flows)):
            if f.endswith((".yml", ".yaml")):
                check_workflow(report, f".github/workflows/{f}", open(os.path.join(flows, f)).read())
    return report.lines


if __name__ == "__main__":
    lines = undeclared(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("\n".join(lines) or "Everything the code and workflows rely on is in the manifest.")
    sys.exit(1 if lines else 0)

"""Compare the repo's live settings with the manifest; report drift on one pinned Setup issue.

    python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number") and .github/CODEOWNERS where it runs

compare() gives one plain line per setting that differs from dokima/manifest.py or could not be read; run() puts them
on the Setup issue (opened, pinned and marked Needs you, or updated), closes it with one line once nothing is off, and
writes nothing when nothing is off and none is open. Both take a GitHub object for every read and write; GitHub below
is the real one, through gh.
"""
import json
import os
import re
import subprocess
import sys

from dokima import board, manifest

TITLE = "Setup"
MARK = "<!-- dokima-setup -->"
NOTHING_OFF = "Nothing is off: every setting matches what Dokima needs."
RANK = {"read": 1, "write": 2, "admin": 3}
FAILED = (subprocess.CalledProcessError, RuntimeError)


def reason(e):
    """GitHub's reason for refusing a call, on one line."""
    if isinstance(e, subprocess.CalledProcessError):
        said = " ".join(str(e.stderr or "").split())
        return re.sub(r"^gh:\s*", "", said) or f"gh exited with {e.returncode}"
    return " ".join(str(e).split())


def unverified(what, e):
    return f"{what} could not be verified: GitHub said `{reason(e)}`."


def compare_labels(live):
    lines = []
    for name, want in manifest.LABELS.items():
        have = live.get(name)
        if have is None:
            lines.append(f"Label `{name}` is missing; Dokima needs it with color `{want['color']}` and description "
                         f"`{want['description']}`.")
            continue
        if (have.get("color") or "").lower() != want["color"].lower():
            lines.append(f"Label `{name}` has color `{have.get('color')}`; Dokima needs `{want['color']}`.")
        if (have.get("description") or "") != want["description"]:
            lines.append(f"Label `{name}` has description `{have.get('description') or ''}`; Dokima needs "
                         f"`{want['description']}`.")
    return lines


def compare_fields(live):
    lines = []
    for field, options in manifest.FIELDS.items():
        have_options = live.get(field)
        if have_options is None:
            lines.append(f"Board field `{field}` is missing; Dokima needs it with the options "
                         + ", ".join(f"`{o}` ({v['color']})" for o, v in options.items()) + ".")
            continue
        for option, want in options.items():
            have = have_options.get(option)
            if have is None:
                lines.append(f"Option `{option}` of the board field `{field}` is missing; Dokima needs it with color "
                             f"`{want['color']}` and description `{want['description']}`.")
                continue
            if (have.get("color") or "").upper() != want["color"].upper():
                lines.append(f"Option `{option}` of the board field `{field}` has color `{have.get('color')}`; "
                             f"Dokima needs `{want['color']}`.")
            if (have.get("description") or "") != want["description"]:
                lines.append(f"Option `{option}` of the board field `{field}` has description "
                             f"`{have.get('description') or ''}`; Dokima needs `{want['description']}`.")
    return lines


def compare_views(live):
    lines = []
    for view, want in manifest.VIEWS.items():
        have = live.get(view)
        if have is None:
            lines.append(f"View `{view}` is missing on the board; Dokima needs a `{want['layout']}` view filtered to "
                         f"`{want['filter']}`.")
            continue
        if (have.get("layout") or "").lower() != want["layout"].lower():
            lines.append(f"View `{view}` has layout `{have.get('layout')}`; Dokima needs `{want['layout']}`.")
        if (have.get("filter") or "") != want["filter"]:
            lines.append(f"View `{view}` has filter `{have.get('filter') or ''}`; Dokima needs `{want['filter']}`.")
    return lines


def compare_rule(branch, live, want):
    needed = want["required_checks"]
    if live is None:
        return [f"Branch `{branch}` has no rule; Dokima needs one requiring "
                + " and ".join(f"`{c}`" for c in needed) + "."]
    have = live.get("required_checks") or []
    return ([f"Branch rule of `{branch}` does not require `{c}`; Dokima needs it required." for c in needed
             if c not in have]
            + [f"Branch rule of `{branch}` requires `{c}`, a check Dokima does not declare." for c in have
               if c not in needed])


def compare_permissions(live):
    lines = []
    for perm, want in manifest.PERMISSIONS.items():
        have = live.get(perm)
        if have is None:
            lines.append(f"App permission `{perm}` is missing; Dokima needs `{want}`.")
        elif RANK.get(have, 0) < RANK[want]:
            lines.append(f"App permission `{perm}` is `{have}`; Dokima needs `{want}`.")
        elif RANK.get(have, 0) > RANK[want]:
            lines.append(f"App permission `{perm}` is `{have}`, broader than the `{want}` Dokima needs.")
    for perm, have in live.items():
        if perm not in manifest.PERMISSIONS:
            lines.append(f"App permission `{perm}` is `{have}`, broader than Dokima needs: it needs none.")
    return lines


def auto_merge(github, repo, rule):
    """Whether auto-merge is on, read from main's two pull-request-only exemption lists: (drift lines, note).

    On both lists it is on, on neither it is off (the default); neither is drift, so each comes back as the note. On
    only one list, or a list GitHub will not show, is a drift line. rule is main's rule as branch_rule() read it."""
    try:
        app = github.app_id(repo)
        queues = [r for r in github.rulesets(repo)
                  if any(x.get("type") == "merge_queue" for x in r.get("rules") or [])]
    except FAILED as e:
        return [f"Auto-merge is not verified: GitHub said `{reason(e)}` when the audit read the merge queue "
                f"ruleset's bypass list."], None
    review = app in ((rule or {}).get("review_bypass_apps") or [])
    queue = any(b.get("actor_type") == "Integration" and b.get("actor_id") == app
                and b.get("bypass_mode") == "pull_request" for r in queues for b in r.get("bypass_actors") or [])
    if review and queue:
        return [], ("Auto-merge is on: Dokima's app is on both of main's exemption lists, so a pull request whose "
                    "code review passed merges by itself.")
    if not review and not queue:
        return [], "Auto-merge is off, the default: every pull request waits for your approval before it merges."
    lacking = "main's review exemption" if queue else "the merge queue ruleset's bypass list for pull requests"
    return [f"Auto-merge is half set up: Dokima's app is missing from {lacking}. Add it there for auto-merge, or take "
            f"it off the other list to keep your approval."], None


def check(github, repo):
    """(lines, notes): compare()'s lines, and the auto-merge state, which is no drift."""
    rules = {}

    def rule(branch):
        rules[branch] = github.branch_rule(repo, branch)
        return rules[branch]

    reads = [("Labels", lambda: github.labels(repo), compare_labels),
             ("Board fields", github.fields, compare_fields),
             ("Board views", github.views, compare_views)]
    reads += [(f"Branch rule of `{branch}`", lambda branch=branch: rule(branch),
               lambda live, branch=branch, want=want: compare_rule(branch, live, want))
              for branch, want in manifest.BRANCH_RULES.items()]
    reads += [("App permissions", lambda: github.permissions(repo), compare_permissions)]
    lines = []
    for what, read, check_live in reads:
        try:
            live = read()
        except FAILED as e:
            lines.append(unverified(what, e))
            continue
        lines += check_live(live)
    notes = []
    if "main" in rules:  # an unreadable main rule already has its line
        drift, note = auto_merge(github, repo, rules["main"])
        lines += drift
        notes += [note] if note else []
    return lines, notes


def compare(github, repo):
    """One line per setting that differs from the manifest or could not be read."""
    return check(github, repo)[0]


def code_owners(root):
    """The owners of `*` in root/.github/CODEOWNERS; the last `*` line wins, as on GitHub."""
    owners = []
    try:
        text = open(os.path.join(root, ".github", "CODEOWNERS")).read()
    except FileNotFoundError:
        return owners
    for line in text.splitlines():
        parts = line.split("#")[0].split()
        if parts and parts[0] == "*":
            owners = [p for p in parts[1:] if p.startswith("@")]
    return owners


def setup_body(lines, owners, notes=()):
    who = " ".join(owners) + ", " if owners else ""
    return (f"{MARK}\n{who}the drift audit found settings on this repo that differ from what Dokima needs, or that it "
            f"could not verify:\n\n" + "".join(f"- {l}\n" for l in lines)
            + "".join(f"\n{n}\n" for n in notes)
            + "\nEach audit updates this issue, and closes it once nothing is off.\n")


def run(github, repo, root="."):
    """Report the audit on the Setup issue; returns the Setup issue it touched, or None."""
    lines, notes = check(github, repo)
    issue = github.setup_issue(repo)
    if not lines:
        if issue is None:
            return None
        github.comment(repo, issue["number"], NOTHING_OFF)
        github.close_issue(repo, issue["number"])
        return issue["number"]
    body = setup_body(lines, code_owners(root), notes)
    if issue is None:
        n = github.create_issue(repo, TITLE, body)
        github.pin_issue(repo, n)
    else:
        n = issue["number"]
        if issue["body"] != body:
            github.edit_issue(repo, n, body)
    github.needs_you(repo, n)
    return n


def gh(*args):
    """gh's output; raises subprocess.CalledProcessError, with GitHub's reason in stderr, when GitHub refuses."""
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def pages(out):
    """Every item of a paginated REST list (gh prints one JSON array per page)."""
    decoder, items, i, out = json.JSONDecoder(), [], 0, out.strip()
    while i < len(out):
        page, i = decoder.raw_decode(out, i)
        items += page
        while i < len(out) and out[i].isspace():
            i += 1
    return items


BOARD_QUERY = 'query($o:String!,$n:Int!){organization(login:$o){projectV2(number:$n){id fields(first:50){nodes{... on ProjectV2SingleSelectField{id name options{id name color description}}}} views(first:50){nodes{id name layout filter}}}}}'


class GitHub:
    """The live repo and board, read and written through gh."""

    def __init__(self, spec):
        self.spec = spec
        self.owner, number = spec.split("/")
        self.number = int(number)
        self.project = None

    def board(self):
        if self.project is None:
            p = board.gql(BOARD_QUERY, o=self.owner, n=self.number)["organization"]["projectV2"]
            if p is None:
                raise RuntimeError(f"no board {self.spec}")
            self.project = p
        return self.project

    def labels(self, repo):
        return {l["name"]: {"color": l["color"], "description": l.get("description") or ""}
                for l in pages(gh("api", "--paginate", f"repos/{repo}/labels?per_page=100"))}

    def fields(self):
        return {f["name"]: {o["name"]: {"color": o.get("color"), "description": o.get("description") or ""}
                            for o in f["options"]}
                for f in self.board()["fields"]["nodes"] if f and "options" in f}

    def views(self):
        return {v["name"]: {"layout": re.sub(r"_LAYOUT$", "", v.get("layout") or "").lower(),
                            "filter": v.get("filter") or ""}
                for v in self.board()["views"]["nodes"]}

    def branch_rule(self, repo, branch):
        try:
            rule = json.loads(gh("api", f"repos/{repo}/branches/{branch}/protection"))
        except subprocess.CalledProcessError as e:
            if "Branch not protected" in f"{e.stderr} {e.stdout}":
                return None
            raise
        checks = rule.get("required_status_checks") or {}
        exempt = ((rule.get("required_pull_request_reviews") or {}).get("bypass_pull_request_allowances") or {})
        return {"required_checks": checks.get("contexts") or [c["context"] for c in checks.get("checks") or []],
                "review_bypass_apps": [a["id"] for a in exempt.get("apps") or []]}

    def permissions(self, repo):
        return json.loads(gh("api", f"repos/{repo}/installation"))["permissions"]

    def rulesets(self, repo):
        listed = pages(gh("api", "--paginate", f"repos/{repo}/rulesets?per_page=100"))
        return [json.loads(gh("api", f"repos/{repo}/rulesets/{r['id']}")) for r in listed]

    def app_id(self, repo):
        return json.loads(gh("api", f"repos/{repo}/installation"))["app_id"]

    def setup_issue(self, repo):
        listed = json.loads(gh("issue", "list", "--repo", repo, "--state", "open", "--limit", "1000", "--json",
                               "number,title,body"))
        found = sorted((i for i in listed if MARK in (i.get("body") or "")), key=lambda i: i["number"])
        return {"number": found[0]["number"], "body": found[0]["body"]} if found else None

    def create_issue(self, repo, title, body):
        url = gh("issue", "create", "--repo", repo, "--title", title, "--body", body)
        return int(re.search(r"(\d+)\s*$", url).group(1))

    def edit_issue(self, repo, n, body):
        gh("issue", "edit", str(n), "--repo", repo, "--body", body)

    def comment(self, repo, n, text):
        gh("issue", "comment", str(n), "--repo", repo, "--body", text)

    def close_issue(self, repo, n):
        gh("issue", "close", str(n), "--repo", repo)

    def pin_issue(self, repo, n):
        gh("issue", "pin", str(n), "--repo", repo)

    def needs_you(self, repo, n):
        b = board.Board(self.spec, repo)
        b.set(b.item("issue", n), "Action", "Needs you")


def main(argv):
    if len(argv) != 1 or argv[0].count("/") != 1:
        print("usage: python3 -m dokima.audit OWNER/REPO", file=sys.stderr)
        return 2
    spec = os.environ.get("DOKIMA_BOARD", "").strip()
    if not spec:
        print("::error::No DOKIMA_BOARD set; the audit needs the board to check it and mark the Setup issue.")
        return 1
    try:
        n = run(GitHub(spec), argv[0])
    except FAILED as e:
        print(f"::error::The audit could not report on the Setup issue: {reason(e)}")
        return 1
    print(f"Setup issue: #{n}" if n else "Nothing is off.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

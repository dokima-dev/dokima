"""Compare the repo's live settings with the manifest; report drift on one pinned Setup issue.

    python3 -m dokima.audit OWNER/REPO   # reads DOKIMA_BOARD ("org/number", optional) and .github/CODEOWNERS where it runs

compare() first creates every label Dokima needs that the repo lacks, then gives one plain line per setting that
differs from dokima/manifest.py or could not be read; run() puts them
on the Setup issue (opened, pinned and marked Needs you, or updated), closes it with one line once nothing is off, and
writes nothing when nothing is off and none is open. Both take a GitHub object for every read and write; GitHub below
is the real one, through gh.
"""
import json
import os
import re
import subprocess
import sys

import yaml

from dokima import agents, board, manifest, prompt, settings

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


def compare_labels(live, wanted=None):
    """One line per label in WANTED that LIVE lacks or holds otherwise.

    WANTED defaults to the manifest's labels."""
    lines = []
    for name, want in (wanted or manifest.LABELS).items():
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


def create_labels(github, repo, live, wanted):
    """Create each label in WANTED that LIVE lacks; one line per label GitHub refused.

    Each gets its color and description from WANTED. LIVE then holds every label as it now stands, so
    compare_labels() reports only drift; a refused label keeps its one line here. An existing label is never
    overwritten."""
    lines = []
    for name, want in wanted.items():
        if name in live:
            continue
        try:
            github.create_label(repo, name, want["color"], want["description"])
        except FAILED as e:
            lines.append(f"Label `{name}` is missing and could not be created: GitHub said `{reason(e)}`; Dokima "
                         f"needs it with color `{want['color']}` and description `{want['description']}`.")
        live[name] = dict(want)
    return lines


def compare_fields(live, wanted=None):
    """One line per board field or option in WANTED that LIVE lacks or differs on."""
    lines = []
    for field, options in (wanted or manifest.FIELDS).items():
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
            + ([f"Branch rule of `{branch}` lets a branch behind it merge; Dokima needs it to demand an up-to-date "
                f"branch."] if want.get("up_to_date") and not live.get("up_to_date") else []))


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


def needed_secrets(got):
    """The repo secrets Dokima's jobs read: the app's key and each role's agent key.

    The merged settings GOT name each role's key; a role they leave out takes today's key."""
    section = got.get("agents") if isinstance(got.get("agents"), dict) else {}
    roles = section.get("roles") if isinstance(section.get("roles"), dict) else {}
    subs = section.get("subscriptions") if isinstance(section.get("subscriptions"), dict) else {}
    needed = ["DOKIMA_APP_KEY"]
    for role in prompt.ROLES:
        given = roles.get(role)
        if given is None:
            key = agents.TODAY["key"]
        else:
            found = subs.get((given or {}).get("subscription", "")) if isinstance(given, dict) else None
            key = found.get("key") if isinstance(found, dict) else None
        if key and str(key) not in needed:
            needed.append(str(key))
    return needed


def own_repo(root):
    """Whether the repo at ROOT is Dokima's own, holding the shared workflows themselves.

    Its jobs run in its `keys` environment, so its keys reach them from there and need not be repo secrets (#885)."""
    return os.path.isfile(os.path.join(root, ".github", "workflows", "entry.yml"))


def compare_secrets(live, needed):
    """One line per secret in NEEDED that LIVE lacks or that is undeclared (#896).

    Dokima runs from its own repo, so its jobs see only repo secrets; a key kept in the `keys` environment never
    reaches them (#876)."""
    lines = []
    for name in needed:
        if name != "DOKIMA_APP_KEY" and agents.undeclared(name):
            lines.append(agents.undeclared(name))
        elif name not in live:
            lines.append(f"Repo secret `{name}` is missing; Dokima needs it as a repo secret, since a secret kept "
                         f"only in the `keys` environment never reaches its jobs.")
    return lines


def auto_merge(github, repo, rule, queue=True):
    """Whether auto-merge is on, read from main's two pull-request-only exemption lists: (drift lines, note).

    On both lists it is on, on neither it is off (the default); neither is drift, so each comes back as the note. On
    only one list, or a list GitHub will not show, is a drift line. rule is main's rule as branch_rule() read it.
    With no merge queue (queue false) only main's review exemption counts, and rulesets are never read."""
    if not queue:
        try:
            app = github.app_id(repo)
        except FAILED as e:
            return [f"Auto-merge is not verified: GitHub said `{reason(e)}` when the audit read Dokima's app."], None
        if app in ((rule or {}).get("review_bypass_apps") or []):
            return [], ("Auto-merge is on: Dokima's app is on main's review exemption, so a pull request whose code "
                        "review passed merges by itself.")
        return [], "Auto-merge is off, the default: every pull request waits for your approval before it merges."
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


def check(github, repo, root=".", has_board=True):
    """(lines, notes): compare()'s lines, and the auto-merge state, which is no drift.

    What Dokima needs comes from the merged settings of the repo at root. With no board, its fields and views are
    not read."""
    got = settings.read(root)
    rules = {}

    def rule(branch):
        rules[branch] = github.branch_rule(repo, branch)
        return rules[branch]

    labels = manifest.labels(got)
    reads = [("Labels", lambda: github.labels(repo),
              lambda live: create_labels(github, repo, live, labels) + compare_labels(live, labels))]
    if has_board:
        reads += [("Board fields", github.fields, lambda live: compare_fields(live, manifest.fields(got))),
                  ("Board views", github.views, compare_views)]
    reads += [(f"Branch rule of `{branch}`", lambda branch=branch: rule(branch),
               lambda live, branch=branch, want=want: compare_rule(branch, live, want))
              for branch, want in manifest.branch_rules(got).items()]
    reads += [("App permissions", lambda: github.permissions(repo), compare_permissions)]
    if not own_repo(root):
        reads += [("Repo secrets", lambda: github.secrets(repo),
                   lambda live: compare_secrets(live, needed_secrets(got)))]
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
        drift, note = auto_merge(github, repo, rules["main"], (got.get("merge") or {}).get("queue", True) is not False)
        lines += drift
        notes += [note] if note else []
    return lines, notes


def compare(github, repo, root=".", has_board=True):
    """One line per setting that differs from the manifest or could not be read."""
    return check(github, repo, root, has_board)[0]


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


def run(github, repo, root=".", has_board=True):
    """Report the audit on the Setup issue; returns the Setup issue it touched, or None.

    With no board, the board is neither read nor marked."""
    lines, notes = check(github, repo, root, has_board)
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
    if has_board:
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
        self.owner, number = spec.split("/") if spec else ("", "0")
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

    def create_label(self, repo, name, color, description):
        gh("api", "-X", "POST", f"repos/{repo}/labels", "-f", f"name={name}", "-f", f"color={color}",
           "-f", f"description={description}")

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
                "review_bypass_apps": [a["id"] for a in exempt.get("apps") or []],
                "up_to_date": bool(checks.get("strict"))}

    def permissions(self, repo):
        return json.loads(gh("api", f"repos/{repo}/installation"))["permissions"]

    def secrets(self, repo):
        """The names of the repo's own secrets; GitHub never shows their values."""
        out = gh("api", "--paginate", f"repos/{repo}/actions/secrets?per_page=100").strip()
        decoder, names, i = json.JSONDecoder(), set(), 0
        while i < len(out):  # gh prints one JSON object per page
            page, i = decoder.raw_decode(out, i)
            names |= {s["name"] for s in page.get("secrets") or []}
            while i < len(out) and out[i].isspace():
                i += 1
        return names

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
    try:
        n = run(GitHub(spec), argv[0], has_board=bool(spec))
    except FAILED as e:
        print(f"::error::The audit could not report on the Setup issue: {reason(e)}")
        return 1
    except (settings.Locked, OSError, ValueError, yaml.YAMLError) as e:
        print(f"::error::The audit could not read the repo's settings: {e}")
        return 1
    print(f"Setup issue: #{n}" if n else "Nothing is off.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

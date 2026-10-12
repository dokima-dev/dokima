"""Keep the project board's Status, Action and Priority current, from GitHub's state.

Each event about an issue or its pull request, and a sweep every 15 minutes, put its cards where the issue's state
says now. Priority is Blocker on an open issue blocking an open issue (blocked-by links), else its label's.

    python3 -m dokima.board         # reads GITHUB_EVENT_NAME, GITHUB_EVENT_PATH and DOKIMA_BOARD ("org/number"), if set
    python3 -m dokima.board queue   # writes the event's board queue to GITHUB_OUTPUT as group=...
"""
import json
import os
import subprocess
import sys

from dokima import agent, manifest, plan, retry

AUTOPILOT = "autopilot"
DONE = ("Done", None)


def gql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    return json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)["data"]


def api(method, path, **fields):
    """One REST call; raises subprocess.CalledProcessError when GitHub refuses it."""
    args = ["gh", "api", "-X", method, path]
    for k, v in fields.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    out = subprocess.run(args, check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else {}


class Board:
    def __init__(self, spec, repo, q=gql, rest=api):
        self.q, self.rest = q, rest
        owner, number = spec.split("/")
        self.owner, self.number = owner, int(number)
        self.repo_owner, self.repo_name = repo.split("/")
        p = q('query($o:String!,$n:Int!){organization(login:$o){projectV2(number:$n){id fields(first:50){nodes{... on ProjectV2SingleSelectField{id name options{id name}}}}}}}', o=owner, n=int(number))["organization"]["projectV2"]
        self.id = p["id"]
        self.fields = {f["name"]: (f["id"], {o["name"]: o["id"] for o in f["options"]}) for f in p["fields"]["nodes"] if f}

    def item(self, kind, number):
        """The board item for an issue or PR, added at the top if it is not on the board yet."""
        field = "issue" if kind == "issue" else "pullRequest"
        node = self.q(f'query($o:String!,$r:String!,$n:Int!){{repository(owner:$o,name:$r){{{field}(number:$n){{id projectItems(first:20){{nodes{{id project{{id}}}}}}}}}}}}', o=self.repo_owner, r=self.repo_name, n=number)["repository"][field]
        for it in node["projectItems"]["nodes"]:
            if it["project"]["id"] == self.id:
                return it["id"]
        iid = self.q('mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}', p=self.id, c=node["id"])["addProjectV2ItemById"]["item"]["id"]
        self.q('mutation($p:ID!,$i:ID!){updateProjectV2ItemPosition(input:{projectId:$p,itemId:$i}){clientMutationId}}', p=self.id, i=iid)
        return iid

    def set(self, iid, field, option):
        if field not in self.fields:
            return
        fid, options = self.fields[field]
        if option is None:
            self.q('mutation($p:ID!,$i:ID!,$f:ID!){clearProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f}){projectV2Item{id}}}', p=self.id, i=iid, f=fid)
        elif option in options:
            self.q('mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}}}', p=self.id, i=iid, f=fid, o=options[option])

    def value(self, iid, field):
        """The card's current option of that field, or None."""
        node = self.q('query($i:ID!,$f:String!){node(id:$i){... on ProjectV2Item{fieldValueByName(name:$f){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}', i=iid, f=field)["node"]
        return ((node or {}).get("fieldValueByName") or {}).get("name")

    def labels(self, kind, number):
        """The names of the labels the issue or PR carries."""
        field = "issue" if kind == "issue" else "pullRequest"
        node = self.q(f'query($o:String!,$r:String!,$n:Int!){{repository(owner:$o,name:$r){{{field}(number:$n){{labels(first:100){{nodes{{name}}}}}}}}}}', o=self.repo_owner, r=self.repo_name, n=int(number))["repository"][field]
        return {label["name"] for label in node["labels"]["nodes"]}

    def autopilot(self, kind, number):
        """Whether the issue or PR carries the autopilot label."""
        return AUTOPILOT in self.labels(kind, number)

    def dependencies(self, number, side):
        """[{number, state}] of the issues this one blocks ("blocking") or is blocked by ("blocked_by"); raises
        subprocess.CalledProcessError when GitHub refuses, never answering none."""
        out, page = [], 1
        while True:
            got = self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues/{number}/dependencies/{side}?per_page=100&page={page}")
            out += [{"number": i["number"], "state": i["state"]} for i in got]
            if len(got) < 100:
                return out
            page += 1

    def blocking(self, number):
        return self.dependencies(number, "blocking")

    def blocked_by(self, number):
        return self.dependencies(number, "blocked_by")

    def open_issues(self):
        """The numbers of every open issue in the repo, pull requests left out."""
        out, page = [], 1
        while True:
            got = self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues?state=open&per_page=100&page={page}")
            out += [i["number"] for i in got if "pull_request" not in i]
            if len(got) < 100:
                return out
            page += 1

    def open_pr(self, number):
        """The open pull request built for the issue (from its try branch), or None."""
        nodes = self.q('query($o:String!,$r:String!,$h:String!){repository(owner:$o,name:$r){pullRequests(headRefName:$h,states:[OPEN],first:1){nodes{number}}}}', o=self.repo_owner, r=self.repo_name, h=f"try/issue-{number}")["repository"]["pullRequests"]["nodes"]
        return nodes[0]["number"] if nodes else None

    def parent(self, number):
        """The issue's parent issue, or None."""
        up = self.q('query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){parent{number}}}}', o=self.repo_owner, r=self.repo_name, n=int(number))["repository"]["issue"].get("parent")
        return up["number"] if up else None

    def label(self, kind, number, on):
        """Put the autopilot label on or off the issue or PR, leaving its other labels alone."""
        path = f"repos/{self.repo_owner}/{self.repo_name}/issues/{number}/labels"
        if on:
            self.rest("POST", path, **{"labels[]": AUTOPILOT})
        else:
            self.rest("DELETE", f"{path}/{AUTOPILOT}")

    def state(self, kind, number):
        """"open" or "closed" (a merged pull request is closed); raises subprocess.CalledProcessError when GitHub cannot say."""
        # The issues API answers for pull requests too.
        return "closed" if self.rest("GET", f"repos/{self.repo_owner}/{self.repo_name}/issues/{int(number)}").get("state") == "closed" else "open"

    def cards(self):
        """Every issue and pull request card on the board; drafts are skipped.

        Each is {kind, number, status, action, closed, autopilot}; a merged pull request counts as closed."""
        out, cursor = [], None
        while True:
            more = {"c": cursor} if cursor else {}
            items = self.q('query($o:String!,$n:Int!,$c:String){organization(login:$o){projectV2(number:$n){items(first:100,after:$c){pageInfo{hasNextPage endCursor} nodes{fieldValueByName(name:"Action"){... on ProjectV2ItemFieldSingleSelectValue{name}} status:fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}} content{__typename ... on Issue{number state labels(first:100){nodes{name}}} ... on PullRequest{number state labels(first:100){nodes{name}}}}}}}}}', o=self.owner, n=self.number, **more)["organization"]["projectV2"]["items"]
            for it in items["nodes"]:
                c = it.get("content") or {}
                if c.get("__typename") not in ("Issue", "PullRequest"):
                    continue
                out.append({"kind": "issue" if c["__typename"] == "Issue" else "pr", "number": c["number"],
                            "status": (it.get("status") or {}).get("name"),
                            "action": (it.get("fieldValueByName") or {}).get("name"), "closed": c["state"] != "OPEN",
                            "autopilot": AUTOPILOT in {label["name"] for label in c["labels"]["nodes"]}})
            if not items["pageInfo"]["hasNextPage"]:
                return out
            cursor = items["pageInfo"]["endCursor"]

    def views(self):
        return [v["name"] for v in self.view_nodes()]

    def view_nodes(self):
        """The board's views, each as {id, name, filter}."""
        p = self.q('query($o:String!,$n:Int!){organization(login:$o){projectV2(number:$n){views(first:50){nodes{id name filter}}}}}', o=self.owner, n=self.number)["organization"]["projectV2"]
        return p["views"]["nodes"]

    def set_view_filter(self, view_id, filter):
        self.q('mutation($v:ID!,$f:String!){updateProjectV2View(input:{viewId:$v,filter:$f}){projectV2View{id}}}', v=view_id, f=filter)

    def add_view(self, name, layout, filter):
        self.rest("POST", f"orgs/{self.owner}/projectsV2/{self.number}/views", name=name, layout=layout, filter=filter)


def about(event, p):
    """[(kind, number, head, body)] of the issue or pull requests an event is about."""
    if event in ("issues", "issue_comment"):
        return [("pr" if p["issue"].get("pull_request") else "issue", p["issue"]["number"], None, p["issue"].get("body"))]
    if event == "workflow_run":
        return [("pr", pr["number"], (pr.get("head") or {}).get("ref"), None) for pr in p["workflow_run"].get("pull_requests") or []]
    if "pull_request" in p:
        pr = p["pull_request"]
        return [("pr", pr["number"], (pr.get("head") or {}).get("ref"), pr.get("body"))]
    return []


def queue(event, p):
    """The event's board queue, from its payload alone: one per issue and its pull requests."""
    if event == "schedule":
        return "board-sweep"
    for kind, n, head, body in about(event, p):
        issue = n if kind == "issue" else agent.issue_of_pr(head, body)
        return f"board-{issue}" if issue else f"board-pr-{n}"
    return f"board-run-{os.environ.get('GITHUB_RUN_ID', '')}"


def reason(e):
    return (getattr(e, "stderr", None) or str(e)).strip()


def issue_of(repo, pr, head=None, body=None):
    """The issue a pull request was built for, or None; asks GitHub when needed."""
    n = agent.issue_of_pr(head, body)
    if not n:
        try:
            p = json.loads(agent.gh("pr", "view", str(pr), "-R", repo, "--json", "headRefName,body"))
        except (subprocess.CalledProcessError, ValueError) as e:
            raise RuntimeError(f"Could not read PR #{pr} ({reason(e)}), so its card was left as it was.") from e
        n = agent.issue_of_pr(p.get("headRefName"), p.get("body"))
    return int(n) if n else None


def where(repo, owners, n, on):
    """(column, pill) of open issue n, from its history now.

    Backlog with no record, else the newest stage started since its newest record, else where the river put it then but
    never in a worker or code review not yet started. Needs you while it waits on the owner, else Autopilot or none."""
    d, items = agent.conversation(repo, n)
    at = [i for i, c in enumerate(items) if agent.is_record(c)]
    body, pill = d.get("body") or "", "Autopilot" if on else None
    if not at:
        return "Backlog", pill
    step = agent.next_step(items[:at[-1]], rec := agent.records([items[at[-1]]])[0], owners, autopilot=lambda: on, body=body, number=str(n))
    held = ("stop",) if step[:2] == ("start", "worker") and rec.get("stage") == "plan" or step[1:3] == ("reviewer", "pr") else step
    column = "Work" if rec.get("role") == "split" else ([s for s in (agent.started(c, owners) for c in items[at[-1] + 1:]) if s] or [agent.board_place(rec, held)[0]])[-1]
    return column, "Needs you" if agent.waits_on_owner(items, owners, lambda: on, body, str(n)) else pill


def rebuild(board, repo, owners, n, prs=()):
    """Put issue n, its open pull request and `prs` where its state says.

    Closed ones go in Done; all is read first, so a card GitHub cannot read keeps its place and this fails naming it."""
    try:
        place = DONE if board.state("issue", n) == "closed" else where(repo, owners, n, board.autopilot("issue", n))
        prs = sorted(set(prs) | {board.open_pr(n)} - {None})
        todo = [("issue", n, place)] + [("pr", m, DONE if board.state("pr", m) == "closed" else place) for m in prs]
    except (subprocess.CalledProcessError, ValueError, KeyError) as e:
        raise RuntimeError(f"Could not read the state of #{n} ({reason(e)}), so its cards were left as they were.") from e
    for kind, m, place in todo:
        put(board, kind, m, place)
    return [(kind, m, column, pill) for kind, m, (column, pill) in todo]


def put(board, kind, n, place):
    iid = board.item(kind, n)
    for field, option in zip(("Status", "Action"), place):
        if board.value(iid, field) != option:
            board.set(iid, field, option)


def stopped(board, repo, n, column):
    """Show a failed run's issue and open pull request as Needs you in `column`."""
    def mark(kind, m):
        try:
            closed = board.state(kind, m) == "closed"
        except subprocess.CalledProcessError:
            closed = False
        put(board, kind, m, DONE if closed else (column, "Needs you"))
    mark("issue", int(n))
    pr = agent.gh("pr", "list", "-R", repo, "--head", f"try/issue-{n}", "--state", "open", "--json", "number", "-q", ".[0].number").strip()
    if pr.isdigit():
        mark("pr", int(pr))


def switch(board, number):
    """Follow the issue's autopilot label on its open PR, and add the Autopilot view."""
    on = board.autopilot("issue", number)
    pr = board.open_pr(number)
    if pr and board.autopilot("pr", pr) != on:
        board.label("pr", pr, on)
    if not on:
        return
    # Only the top of a tree switched on adds the view: its sub-issues' board runs may overlap it and read no view yet.
    up = board.parent(number)
    if up and board.autopilot("issue", up):
        return
    try:
        if "Autopilot" not in board.views():
            view = manifest.VIEWS["Autopilot"]
            board.add_view("Autopilot", view["layout"], view["filter"])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Could not add the Autopilot view to the board: {reason(e)}") from e


def fix_view(board):
    """Move an Autopilot view still on label:autopilot to the manifest's filter; others are the owner's."""
    new = manifest.VIEWS["Autopilot"]["filter"]
    try:
        for v in board.view_nodes():
            if v["name"] == "Autopilot" and v.get("filter") == f"label:{AUTOPILOT}":
                board.set_view_filter(v["id"], new)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Could not fix the Autopilot view's filter to {new}: {reason(e)}") from e


def changed(repo):
    """[(kind, number)] updated since the last sweep that succeeded, or None to recheck every card."""
    try:
        runs = json.loads(agent.gh("api", f"repos/{repo}/actions/workflows/board.yml/runs?event=schedule&status=success&per_page=1"))["workflow_runs"]
        found = json.loads(agent.gh("api", f"repos/{repo}/issues?state=all&since={runs[0]['run_started_at']}&per_page=100", "--paginate"))
        return [("pr" if "pull_request" in i else "issue", i["number"]) for i in found]
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError, IndexError) as e:
        print(f"GitHub could not say what changed since the last sweep ({reason(e)}), so every card is rechecked.")
        return None


def sweep(board, repo, owners, todo=None):
    """Put every card, or only `todo`'s, where its state says.

    Each comes with its pull request or issue. Closed cards go to Done with no pill from the board's list; the run
    fails naming any card it cannot read."""
    cards, failed, issues = board.cards(), [], {}
    for c in cards:
        if c["closed"] and (c.get("status"), c["action"]) != DONE:
            put(board, c["kind"], c["number"], DONE)
    for kind, n in [(c["kind"], c["number"]) for c in cards if not c["closed"]] if todo is None else todo:
        try:
            issues.setdefault(n if kind == "issue" else issue_of(repo, n), set()).update({n} if kind == "pr" else set())
        except RuntimeError as e:
            failed.append(str(e))
    for n, prs in sorted((n, prs) for n, prs in issues.items() if n):
        try:
            rebuild(board, repo, owners, n, prs)
        except RuntimeError as e:
            failed.append(str(e))
    if failed:
        raise RuntimeError(" ".join(failed))


def blockers(event, p):
    """What may have moved a Blocker pill, or None.

    "all" on schedule, or (number, state) of the issue that closed or reopened."""
    if event == "schedule":
        return "all"
    if event == "issues" and p["action"] in ("closed", "reopened"):
        return p["issue"]["number"], "closed" if p["action"] == "closed" else "open"
    return None


def recompute(board, touched):
    """Set Blocker on open issues blocking an open issue, and clear it elsewhere: priority comes only from links.

    Writes only pills that change: every open issue for "all", else the issue that closed or reopened and the issues
    blocking it. An issue whose links GitHub will not list keeps its pill; the rest are still set, then the run fails naming it."""
    failed = []

    def refused(n, e):
        failed.append(f"#{n}: {(e.stderr or str(e)).strip()}")

    if touched == "all":
        todo = {n: "open" for n in board.open_issues()}
    else:
        n, state = touched
        todo = {n: state}
        try:
            todo.update((m["number"], m["state"]) for m in board.blocked_by(n))
        except subprocess.CalledProcessError as e:
            refused(n, e)
    for n, state in todo.items():
        try:
            blocks = state == "open" and any(m["state"] == "open" for m in board.blocking(n))
        except subprocess.CalledProcessError as e:
            refused(n, e)
            continue
        want = "Blocker" if blocks else None
        iid = board.item("issue", n)
        if board.value(iid, "Priority") != want:
            board.set(iid, "Priority", want)
    if failed:
        raise RuntimeError("Could not list the blocked-by links of " + "; ".join(failed) + "; their pills were left as they are")


def sync(event, payload, spec, repo, q=gql, rest=api):
    """Put the cards an event is about where their state says, and keep Priority."""
    if not spec:
        return []
    touched = blockers(event, payload)
    on_off = event == "issues" and payload["action"] in ("labeled", "unlabeled") and payload["label"]["name"] == AUTOPILOT \
        and payload["issue"]["number"]
    merged = event in ("pull_request", "pull_request_target") and payload["action"] == "closed" and payload["pull_request"].get("merged")
    board, owners = Board(spec, repo, q, rest), plan.repo_approvers(repo.split("/")[0])
    placed, failed = [], []

    def attempt(step):
        try:
            return step()
        except RuntimeError as e:
            failed.append(str(e))

    if event == "schedule":
        attempt(lambda: sweep(board, repo, owners, changed(repo)))
    for kind, n, head, body in about(event, payload):
        issue = n if kind == "issue" else attempt(lambda: issue_of(repo, n, head, body))
        if issue and kind == "pr" and payload.get("action") in ("opened", "reopened") and "pull_request" in payload \
                and board.autopilot("issue", issue) and not board.autopilot("pr", n):
            # A pull request built for an issue on autopilot carries the label too, so the Autopilot view lists it.
            board.label("pr", n, True)
        if issue:
            placed += attempt(lambda: rebuild(board, repo, owners, issue, [n] if kind == "pr" else [])) or []
    if on_off:
        attempt(lambda: switch(board, on_off))
    if merged:
        # An old Autopilot view is fixed on the next merge; then every card on the board is swept.
        attempt(lambda: fix_view(board))
        attempt(lambda: sweep(board, repo, owners))
    if touched is not None and "Priority" in board.fields:
        attempt(lambda: recompute(board, touched))
    if failed:
        raise RuntimeError(" ".join(failed))
    return placed


def main(argv=()):
    if list(argv[1:2]) == ["queue"]:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"group={queue(os.environ['GITHUB_EVENT_NAME'], json.load(open(os.environ['GITHUB_EVENT_PATH'])))}\n")
        return 0
    spec = os.environ.get("DOKIMA_BOARD", "").strip()
    if not spec:
        print("No DOKIMA_BOARD set; nothing to sync.")
        return 0
    event, payload = os.environ["GITHUB_EVENT_NAME"], json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    try:
        # A run the empty API budget stopped runs once more, from scratch, after the budget resets.
        placed = retry.once_more("the board run", lambda: sync(event, payload, spec, os.environ["GITHUB_REPOSITORY"]))
    except RuntimeError as e:
        print(f"::error::{e}")
        return 1
    for change in placed:
        print("board:", *change)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

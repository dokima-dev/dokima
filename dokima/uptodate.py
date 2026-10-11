"""Bring every open PR that fell behind main up to date with GitHub's own Update branch, after each merge to main.

    python3 -m dokima.uptodate     # reads GITHUB_REPOSITORY, GITHUB_REF_NAME and GITHUB_SHA

Rules live in run() and clash(); the GitHub calls go through rest(method, path, **fields), shaped like dokima.board.api.
A clash on a Dokima PR (try/issue-N in this repo) leaves a record on issue N and starts its planner on autopilot, once
until the worker runs again; a clash on any other PR mentions the code owners on it and starts nothing.
"""
import json
import os
import re
import subprocess
import sys

from dokima import agent, plan
from dokima.board import api

PER_PAGE = 100
UPDATE_WORDS = ("This pull request could not be updated with ", "This pull request is up to date with ")


def open_prs(repo, base, rest):
    """Every open PR into base, drafts included."""
    out, page = [], 1
    while True:
        batch = rest("GET", f"repos/{repo}/pulls?state=open&base={base}&per_page={PER_PAGE}&page={page}")
        out += [p for p in batch if p.get("base", {}).get("ref") == base]
        if len(batch) < PER_PAGE:
            return out
        page += 1


def reason(e):
    """GitHub's own reason for refusing a call: its JSON message, else gh's one-line error."""
    try:
        message = json.loads(e.output or "").get("message")
    except (ValueError, AttributeError):
        message = None
    return message or (e.stderr or "").strip() or str(e)


def refusal_comments(repo, n, rest):
    """The bot's own update comments on PR n, oldest first.

    Nobody else's comment counts, whatever it says."""
    out, page = [], 1
    while True:
        batch = rest("GET", f"repos/{repo}/issues/{n}/comments?per_page={PER_PAGE}&page={page}")
        out += [c for c in batch if (c.get("user") or {}).get("login") == f"{agent.BOT}[bot]"
                and (c.get("body") or "").startswith(UPDATE_WORDS)]
        if len(batch) < PER_PAGE:
            return out
        page += 1


def say(repo, n, body, rest, refused):
    """Keeps one update comment on PR n, saying body.

    The newest is edited to body and the older ones deleted. A refusal posts it when there is none; a clean update
    with none says nothing."""
    *older, newest = refusal_comments(repo, n, rest) or [None]
    if newest is None:
        if refused:
            rest("POST", f"repos/{repo}/issues/{n}/comments", body=body)
        return
    if newest.get("body") != body:
        rest("PATCH", f"repos/{repo}/issues/comments/{newest['id']}", body=body)
    for c in older:
        rest("DELETE", f"repos/{repo}/issues/comments/{c['id']}")


def run(repo, base, sha, rest=api, on_clash=None, failed=None):
    """Update every open PR into base whose branch is behind it.

    A refused PR carries one comment saying why, edited in place on every later refusal and to say it is up to date
    once it updates cleanly.

    on_clash(pr, sha) is called for each PR GitHub refuses with a merge conflict. When GitHub cannot list or change a
    PR's comments, (number, reason) goes into `failed` and the rest go on; with no `failed` list it raises.
    Returns (updated, refused) numbers."""
    updated, refused = [], []
    for pr in open_prs(repo, base, rest):
        n, head = pr["number"], pr["head"]["sha"]
        if not rest("GET", f"repos/{repo}/compare/{base}...{head}").get("behind_by"):
            continue
        try:
            rest("PUT", f"repos/{repo}/pulls/{n}/update-branch", expected_head_sha=head)
        except subprocess.CalledProcessError as e:
            why = reason(e)
            refused.append(n)
            body = f"This pull request could not be updated with `{base}` ({sha[:7]}). GitHub said: {why}"
        else:
            why = None
            updated.append(n)
            body = f"This pull request is up to date with `{base}` ({sha[:7]})."
        try:
            say(repo, n, body, rest, why is not None)
        except subprocess.CalledProcessError as e:
            if failed is None:
                raise
            failed.append((n, reason(e)))
        if why is not None and on_clash and "merge conflict" in why.lower():
            on_clash(pr, sha)
    return updated, refused


def trial_merge(base, sha, pr):
    """The paths that clash when the PR's head merges with `sha`, from a trial merge in this checkout that leaves its
    files untouched; what it needs is fetched from the `origin` remote."""
    n = pr["number"]
    subprocess.run(["git", "fetch", "-q", "origin", f"+refs/heads/{base}:refs/remotes/origin/{base}",
                    f"+refs/pull/{n}/head:refs/dokima/pr-{n}"], check=True, capture_output=True, text=True)
    main = sha if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode == 0 \
        else f"origin/{base}"
    p = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", "--no-messages", f"refs/dokima/pr-{n}", main],
                       capture_output=True, text=True)
    if p.returncode not in (0, 1):
        raise subprocess.CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)
    return sorted(set(p.stdout.splitlines()[1:])) if p.returncode == 1 else []


def merged_pr(repo, sha, rest):
    """The PR whose merge put `sha` on main, or None when it came with no PR."""
    pulls = rest("GET", f"repos/{repo}/commits/{sha}/pulls")
    return next((p["number"] for p in pulls or [] if p.get("merged_at")), None)


def history(repo, number, rest):
    """The issue's comments, oldest first, shaped as the river reads them: the bot's REST login is its plain name."""
    out, page = [], 1
    while True:
        batch = rest("GET", f"repos/{repo}/issues/{number}/comments?per_page={PER_PAGE}&page={page}")
        for c in batch:
            login = (c.get("user") or {}).get("login")
            out.append({"author": {"login": agent.BOT if login == f"{agent.BOT}[bot]" else login},
                        "body": c.get("body") or "", "createdAt": c.get("created_at")})
        if len(batch) < PER_PAGE:
            return out
        page += 1


def dokima_issue(repo, pr):
    """Issue N when the PR is Dokima's own, from branch try/issue-N of this same repo; otherwise None."""
    head = pr.get("head") or {}
    m = re.fullmatch(r"try/issue-(\d+)", head.get("ref") or "")
    return int(m.group(1)) if m and ((head.get("repo") or {}).get("full_name") == repo) else None


def autopilot_of(repo, issue, rest):
    """True or False from the issue's own `autopilot` label; None when GitHub cannot say."""
    try:
        labels = (rest("GET", f"repos/{repo}/issues/{issue}") or {}).get("labels")
    except (subprocess.CalledProcessError, AttributeError):
        return None
    if not isinstance(labels, list):
        return None
    return any((l.get("name") if isinstance(l, dict) else l) == agent.AUTOPILOT for l in labels)


def clash(repo, base, sha, pr, rest=api, files=None, owners=None):
    """Handle one PR that clashes with base after merge `sha`.

    A Dokima PR whose issue has a clash sent back with no worker record since gets nothing more. Otherwise it leaves
    one record on its issue naming the merge, its PR, every clashed file and whether the issue is on autopilot, then
    starts the planner only on autopilot; off autopilot, or when GitHub cannot say, the record mentions the code owners
    and starts nothing. Any other PR gets one comment saying the same and mentioning the code owners; no agent starts."""
    n = pr["number"]
    issue = dokima_issue(repo, pr)
    if issue is not None and agent.clash_pending(agent.records(history(repo, issue, rest))):
        return
    try:
        clashed, why = sorted((files or (lambda p, s: trial_merge(base, s, p)))(pr, sha)), None
    except subprocess.CalledProcessError as e:
        clashed, why = [], f"Code could not list the clashed files: {(e.stderr or str(e)).strip()}"
    by = merged_pr(repo, sha, rest)
    who = sorted(owners if owners is not None else plan.repo_approvers(repo.split("/")[0]))
    if issue is None:
        lines = [f"This pull request clashes with `{base}` since {sha[:7]}" + (f" (#{by})" if by else "") + " merged, in:", ""]
        lines += [f"- `{f}`" for f in clashed] or [f"- {why}"]
        lines += ["", f"**Next:** {' '.join('@' + o for o in who)} Dokima didn't build this pull request, so it starts "
                      "nothing: resolve the clash on its branch."]
        rest("POST", f"repos/{repo}/issues/{n}/comments", body="\n".join(lines) + "\n")
        return
    on = autopilot_of(repo, issue, rest)
    server, run_id = os.environ.get("GITHUB_SERVER_URL", "https://github.com"), os.environ.get("GITHUB_RUN_ID")
    rec = {"role": "updater", "stage": None, **({"run": f"{server}/{repo}/actions/runs/{run_id}"} if run_id else {}),
           "handback": {"base": base, "merge": sha, "merged_pr": by, "pr": n, "files": clashed, "autopilot": on,
                        **({"why": why} if why else {})},
           "check": {"passed": True, "problems": []}}
    step = agent.next_step([], rec, set(who))
    rest("POST", f"repos/{repo}/issues/{issue}/comments", body=agent.with_next(agent.render(rec), agent.next_line(step, who)))
    if step[0] == "start":
        rest("POST", f"repos/{repo}/dispatches", event_type="dokima-next", **{
            "client_payload[role]": "planner", "client_payload[stage]": "plan", "client_payload[issue]": str(issue)})


def main():
    repo, base, sha = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REF_NAME"], os.environ["GITHUB_SHA"]
    failed = []

    def on_clash(pr, at):
        try:
            clash(repo, base, at, pr)
        except subprocess.CalledProcessError as e:
            failed.append(pr["number"])
            print(f"::error::uptodate: the clash on #{pr['number']} could not be handled: {reason(e)}")

    unsaid = []
    updated, refused = run(repo, base, sha, on_clash=on_clash, failed=unsaid)
    for n in updated:
        print(f"uptodate: updated #{n}")
    for n in refused:
        print(f"::warning::uptodate: #{n} could not be updated")
    for n, why in unsaid:
        print(f"::error::uptodate: the update comment on #{n} could not be listed or changed: {why}")
    return 1 if failed or unsaid else 0


if __name__ == "__main__":
    sys.exit(main())

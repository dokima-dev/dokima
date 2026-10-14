"""Draw what Dokima would post on a real issue, with any branch's code.

    python3 tools/visuals.py draw ISSUE --branch BRANCH --repo OWNER/NAME
    python3 tools/visuals.py preview ISSUE --branch BRANCH --repo OWNER/NAME --gallery-issue N

Run from the root of a checkout. The issue is read from GitHub through `gh`, and nothing is written there. The
drawing code is taken from BRANCH through a git worktree of it in a temporary folder, so this checkout is left as it
is. Printed to stdout: the issue's top card, every run comment drawn again from its record, and every autopilot
comment drawn again as BRANCH's code would word it. Autopilot comments are recognised by this checkout's own lines.

`preview` posts that same drawing, with the caller's own `gh` login, as one comment on issue N of the gallery repo, so
GitHub renders it. A hidden marker names the real issue, so a later preview of it edits that comment instead of posting
another. Nothing is written to OWNER/NAME.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY = "dokima-dev/card-gallery"
REPLY = re.compile(r"(?:Autopilot is (?P<on>on|off) for (?P<switched>#\d+(?:, #\d+)*)\."
                   r"|#\d+ and every issue under it were already on autopilot\.(?P<none_on>)"
                   r"|No issue in #\d+'s tree was on autopilot\.(?P<none_off>))"
                   r"(?: Planning started for (?P<started>#\d+(?:, #\d+)*), which wait on nothing open\.)?"
                   r"(?: (?P<rest>.*))?\n?", re.S)


class Stop(Exception):
    """Ends the command with one plain message."""


def numbers(text):
    return [int(n) for n in re.findall(r"\d+", text or "")]


def autopilot_post(agent, number, text):
    """An autopilot comment, recognised by this checkout's lines, for the branch to redraw; else None."""
    text = text.strip("\n")
    if text == agent.AUTOPILOT_LINE:
        return {"kind": "line"}
    if text == agent.AUTOPILOT_START_LINE:
        return {"kind": "start"}
    for key, line in agent.AUTOPILOT_LINES.items():
        if text == line:
            return {"kind": "lines", "key": key}
    for key, line in agent.AUTOPILOT_MERGE.items():
        m = re.fullmatch(re.escape(line).replace(r"\{pr\}", r"(\d+)"), text)
        if m:
            return {"kind": "merge", "key": key, "pr": int(m.group(1))}
    m = REPLY.fullmatch(text + "\n")
    if not m:
        return None
    switch = "stop" if m["on"] == "off" or m["none_off"] is not None else "start"
    rest = m["rest"] or ""
    picked = "" if rest == "No stage was started." else rest.rstrip("\n")
    args = [number, switch, numbers(m["switched"]), numbers(m["started"]), picked]
    # Only a reply this checkout's code would word exactly so counts.
    return {"kind": "reply", "args": args} if agent.autopilot_comment(*args).strip("\n") == text else None


def read(repo, number):
    """The issue's posts, oldest first, read with this checkout's code: run records and autopilot comments."""
    sys.path.insert(0, ROOT)
    from dokima import agent, card
    try:
        _, items = agent.conversation(repo, number)
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError) as e:
        raise Stop(f"GitHub could not give #{number} of {repo}: {card.reason(e)}")
    posts = []
    for c in items:
        rs = agent.records([c])
        if rs:
            posts.append({"kind": "record", "rec": rs[0], "url": c.get("url", "")})
        elif (c.get("author") or {}).get("login") == agent.BOT:
            post = autopilot_post(agent, number, c.get("body") or "")
            if post:
                posts.append({**post, "url": c.get("url", "")})
    return posts


def commit_of(branch):
    """The commit `branch` names here or on origin."""
    for ref in (branch, f"origin/{branch}"):
        r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
    raise Stop(f"No branch named {branch!r} here or on origin.")


def draw(number, branch, repo, stdout=None):
    """Draw what `branch`'s code would post on issue `number`, to `stdout` when given."""
    commit = commit_of(branch)
    posts = read(repo, number)
    with tempfile.TemporaryDirectory() as tmp:
        tree, job = os.path.join(tmp, "tree"), os.path.join(tmp, "job.json")
        r = subprocess.run(["git", "worktree", "add", "--detach", "--quiet", tree, commit], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise Stop(f"Could not check out {branch!r}: {' '.join(r.stderr.split())}")
        try:
            with open(job, "w") as f:
                json.dump({"repo": repo, "issue": number, "posts": posts}, f)
            env = dict(os.environ, PYTHONPATH=tree, GITHUB_REPOSITORY=repo)
            return subprocess.run([sys.executable, os.path.abspath(__file__), "paint", job], cwd=tree, env=env,
                                  stdout=stdout, text=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", tree], cwd=ROOT, capture_output=True)


def gallery(*args, stdin=None):
    """`gh api` on the gallery repo, as the caller; Stop with GitHub's reason when refused."""
    r = subprocess.run(["gh", "api", *args], input=stdin, capture_output=True, text=True)
    if r.returncode != 0:
        raise Stop(" ".join((r.stderr or r.stdout).split()))
    return r.stdout


def preview(number, branch, repo, gallery_issue):
    """Post the drawing as one gallery comment, editing the one an earlier preview left."""
    r = draw(number, branch, repo, stdout=subprocess.PIPE)
    if r.returncode != 0:
        return r.returncode
    marker = f"<!-- visuals-preview: {repo}#{number} -->"
    body = json.dumps({"body": f"{marker}\n{r.stdout.strip()}"})
    sys.path.insert(0, ROOT)
    from dokima import agent
    base = f"repos/{GALLERY}/issues"
    try:
        mine = [c for page in agent.pages(gallery(f"{base}/{gallery_issue}/comments", "--paginate")) for c in page
                if (c.get("body") or "").startswith(marker + "\n")]
        if mine:
            done = gallery("-X", "PATCH", f"{base}/comments/{mine[0]['id']}", "--input", "-", stdin=body)
        else:
            done = gallery("-X", "POST", f"{base}/{gallery_issue}/comments", "--input", "-", stdin=body)
    except Stop as e:
        raise Stop(f"GitHub could not give {GALLERY}#{gallery_issue}: {e}")
    print(json.loads(done).get("html_url", ""))
    return 0


def paint(job):
    """Draw the job with the dokima package on PYTHONPATH: the branch's own code."""
    from dokima import agent, card, plan
    with open(job) as f:
        job = json.load(f)
    repo, number = job["repo"], job["issue"]
    try:
        pr_number = card.issue_pr(repo, number)
        issue = plan.fetch_issue(repo, number)
        found = card.gather(repo, number, pr_number)
        cache = {}
        found["sources"] = sorted(card.linked_from(issue["current_body"]))
        now = card.github_links(repo, int(number), cache)
        found["blocking"] = now
        if now.get("unread"):
            found["unread"] = card.reason(card.blocking(repo, int(number), cache))
        found["linked"] = {"relates_to": card.their_links(repo, number, found["sources"])["relates_to"],
                           "blocked_by": now.get("blocked_by") or [], "blocks": now.get("blocks") or []}
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError) as e:
        raise Stop(f"GitHub could not give #{number} of {repo}: {card.reason(e)}")
    out = [f"# Card of #{number}", "", card.render(repo, issue, found)]
    pr_url = (found.get("pr") or {}).get("html_url")
    earlier = []
    for post in job["posts"]:
        out += ["", "", f"# {'Run' if post['kind'] == 'record' else 'Autopilot'} comment {post['url']}", ""]
        if post["kind"] == "record":
            rec = post["rec"]
            judged = agent.latest(earlier, "planner") if rec.get("role") == "reviewer" else None
            out.append(agent.render(rec, pr=pr_url if rec.get("role") == "worker" else None,
                                    plan=judged and judged.get("handback"), earlier=list(earlier)))
            earlier.append(rec)
        elif post["kind"] == "line":
            out.append(agent.AUTOPILOT_LINE)
        elif post["kind"] == "start":
            out.append(agent.AUTOPILOT_START_LINE)
        elif post["kind"] == "lines":
            out.append(agent.AUTOPILOT_LINES[post["key"]])
        elif post["kind"] == "merge":
            out.append(agent.AUTOPILOT_MERGE[post["key"]].format(pr=post["pr"]))
        else:
            out.append(agent.autopilot_comment(*post["args"]))
    print("\n".join(out))


def main(argv):
    if argv[:1] == ["paint"]:
        try:
            paint(argv[1])
        except Stop as e:
            print(f"visuals: {e}", file=sys.stderr)
            return 1
        return 0
    p = argparse.ArgumentParser(prog="tools/visuals.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("draw", help="Draw a real issue's posts with a branch's code.")
    d.add_argument("issue", type=int)
    d.add_argument("--branch", required=True)
    d.add_argument("--repo", required=True, help="OWNER/NAME")
    v = sub.add_parser("preview", help=f"Post that drawing as one comment on an issue of {GALLERY}.")
    v.add_argument("issue", type=int)
    v.add_argument("--branch", required=True)
    v.add_argument("--repo", required=True, help="OWNER/NAME")
    v.add_argument("--gallery-issue", required=True, type=int)
    a = p.parse_args(argv)
    try:
        if a.command == "preview":
            return preview(a.issue, a.branch, a.repo, a.gallery_issue)
        return draw(a.issue, a.branch, a.repo).returncode
    except Stop as e:
        print(f"visuals: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

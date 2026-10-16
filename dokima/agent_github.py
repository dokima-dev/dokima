"""The agent code's one GitHub helper and its plain GitHub reads.

Every call the agent code makes to GitHub goes through `gh` here, so a test fakes GitHub in one place by patching
`dokima.agent_github.gh`. Split out of dokima/agent.py (#636).
"""
import contextlib
import json
import os
import re
import subprocess
import sys
import time


def gh(*args):
    """Run the GitHub CLI and return its output."""
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


BOT = os.environ.get("DOKIMA_BOT", "dokima-runtime")


def linked_prs(repo, number):
    """Pull requests built for the issue: from its try branch."""
    found = json.loads(gh("pr", "list", "-R", repo, "--head", f"try/issue-{number}", "--state", "all", "--json", "number"))
    return sorted({p["number"] for p in found})


def conversation(repo, number):
    """The issue and its pull requests as one list of comments, oldest first, each saying
    where it was written."""
    d = json.loads(gh("issue", "view", str(number), "-R", repo, "--json", "number,title,body,comments"))
    items = [{**c, "where": f"issue #{number}"} for c in d["comments"]]
    for pr in linked_prs(repo, number):
        p = json.loads(gh("pr", "view", str(pr), "-R", repo, "--json", "comments,reviews"))
        items += [{**c, "where": f"PR #{pr}"} for c in p["comments"]]
        items += [{"author": r["author"], "body": r["body"], "createdAt": r["submittedAt"], "where": f"PR #{pr} review ({r['state'].lower()})"}
                  for r in p["reviews"] if r.get("body")]
        for n in json.loads(gh("api", f"repos/{repo}/pulls/{pr}/comments", "--paginate")):
            items.append({"author": {"login": n["user"]["login"]}, "body": n["body"], "createdAt": n["created_at"],
                          "where": f"PR #{pr} line note on {n['path']}:{n.get('line') or n.get('original_line')}"})
    items.sort(key=lambda c: c["createdAt"])
    return d, items


def open_issues(repo):
    """Every open issue of the repo, every page, with its number, title and body; pull
    requests are left out."""
    items = [i for p in pages(gh("api", f"repos/{repo}/issues?state=open&per_page=100", "--paginate")) for i in p]
    return [{"number": i["number"], "title": i["title"], "body": i.get("body") or ""} for i in items
            if "pull_request" not in i]


BOT_LOGIN = "dokima-runtime[bot]"  # Dokima's bot, which files issues from raises and split stories


def parent_of(repo, number):
    """The issue's parent number on GitHub; None when it has none or GitHub cannot say."""
    try:
        return json.loads(gh("api", f"repos/{repo}/issues/{number}/parent")).get("number")
    except Exception as e:  # noqa: BLE001 - any failure means GitHub did not say: no parent counts
        why = gh_reason(e) if isinstance(e, subprocess.CalledProcessError) else str(e)
        print(f"No parent issue of #{number} counts as a source: {why or 'GitHub named none'}", file=sys.stderr)
        return None


def issue_of_pr(head, body):
    """The issue a pull request was built for: from its branch, else its closing line.

    The branch is try/issue-N; the closing line is 'Closes' with the issue's full address or the old
    'Closes #N'."""
    m = re.match(r"try/issue-(\d+)$", head or "") or re.search(
        r"(?i)\b(?:closes|fixes|resolves) (?:#|https://github\.com/[\w.-]+/[\w.-]+/issues/)(\d+)\b", body or "")
    return m.group(1) if m else None


def sub_issues(repo, number):
    """The issue's own sub-issues, one level down, each with its state."""
    # GitHub allows at most 100 sub-issues per parent, so one page holds them all.
    return json.loads(gh("api", f"repos/{repo}/issues/{number}/sub_issues?per_page=100") or "[]")


def blocked_by(repo, number):
    """The issues blocking this one, from GitHub's native blocked-by links, each with its state."""
    return json.loads(gh("api", f"repos/{repo}/issues/{number}/dependencies/blocked_by", "--paginate") or "[]")


def gh_reason(e):
    """GitHub's own words for a call that failed, on one line."""
    return " ".join((e.stderr or str(e)).split())


def rate_limited(e):
    """The rate limit that refused a call, "graphql" or "core" (REST); else None."""
    text = gh_reason(e)
    if "rate limit" not in text.lower():
        return None
    return "graphql" if "graphql" in text.lower() else "core"


@contextlib.contextmanager
def rate_limit_waited_once():
    """Inside it, a call refused by GitHub's rate limit waits once, then retries.

    A second refusal, or any other, raises at once, so a run never hangs on a limit that does not lift."""
    global gh
    plain, waited = gh, []

    def patient(*args):
        try:
            return plain(*args)
        except subprocess.CalledProcessError as e:
            limit = rate_limited(e)
            if waited or not limit:
                raise
            try:
                reset = int(json.loads(plain("api", "rate_limit"))["resources"][limit]["reset"])
            except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                raise e
            waited.append(limit)
            print(f"GitHub's {limit} rate limit ran out; waiting until it resets: {gh_reason(e)}", file=sys.stderr)
            time.sleep(max(0, reset - time.time()) + 1)
            return plain(*args)
    gh = patient
    try:
        yield
    finally:
        gh = plain


NO_PERMISSION = "Resource not accessible by integration"


def pages(text):
    """Every JSON page `gh api --paginate` printed back to back."""
    out, at, dec = [], 0, json.JSONDecoder()
    while text[at:].strip():
        at += len(text[at:]) - len(text[at:].lstrip())
        page, at = dec.raw_decode(text, at)
        out.append(page)
    return out

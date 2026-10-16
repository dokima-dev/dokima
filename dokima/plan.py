#!/usr/bin/env python3
"""The issue as GitHub holds it, and who approves.

Approvers are the code owners in CODEOWNERS (the owners of `*`), or the repository owner when there is no such
file. The card and the scan read an issue's number, title, text and link from here.
"""
import json
import os
import subprocess
import sys

CARD_START = "<!-- dokima-card -->"
CARD_END = "<!-- /dokima-card -->"


def approvers(codeowners, repo_owner):
    """The people whose approval counts: the owners of `*` in CODEOWNERS, else the repository owner."""
    for line in (codeowners or "").splitlines():
        parts = line.split("#")[0].split()
        if parts and parts[0] == "*" and len(parts) > 1:
            return {name.lstrip("@") for name in parts[1:]}
    return {repo_owner}


def repo_approvers(repo_owner, root="."):
    path = os.path.join(root, ".github", "CODEOWNERS")
    return approvers(open(path).read() if os.path.exists(path) else "", repo_owner)


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def fetch_issue(repo, number):
    """The issue's number, title, text and link, in one call to GitHub."""
    owner, name = repo.split("/")
    query = ("query($o:String!,$n:String!,$i:Int!){repository(owner:$o,name:$n){issue(number:$i)"
             "{number title body url}}}")
    data = json.loads(gh("api", "graphql", "-f", f"query={query}", "-f", f"o={owner}", "-f", f"n={name}", "-F", f"i={number}"))
    issue = data["data"]["repository"]["issue"]
    issue["current_body"] = issue["body"]
    return issue


def pr_issue_number(repo, pr):
    """The issue a PR closes, or None."""
    owner, name = repo.split("/")
    query = ("query($o:String!,$n:String!,$p:Int!){repository(owner:$o,name:$n){pullRequest(number:$p)"
             "{closingIssuesReferences(first:1){nodes{number}}}}}")
    data = json.loads(gh("api", "graphql", "-f", f"query={query}", "-f", f"o={owner}", "-f", f"n={name}", "-F", f"p={pr}"))
    nodes = data["data"]["repository"]["pullRequest"]["closingIssuesReferences"]["nodes"]
    return nodes[0]["number"] if nodes else None


def main(argv):
    if argv[1] == "approvers":
        # Comma-separated approvers.
        print(",".join(sorted(repo_approvers(os.environ["GITHUB_REPOSITORY_OWNER"]))))


if __name__ == "__main__":
    main(sys.argv)

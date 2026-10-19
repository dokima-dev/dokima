"""Filing Dokima's own problems in the upstream repo the settings name, such as dokima-dev/dokima (#745).

A repo's `.dokima/settings.yaml` may name it as `upstream.repo`; empty, the default, keeps everything in the repo.
Two things file there: a problem a review confirms and tags as Dokima's fault, and a failed run of a shared workflow:

    python3 -m dokima.upstream failed WORKFLOW JOB    files the failure of JOB in WORKFLOW.yml
    python3 -m dokima.upstream failed WORKFLOW        files each job RESULTS names as failed, as `JOB=RESULT ...`
    python3 -m dokima.upstream owner                  prints the upstream repo's owner, empty for none

A failed test check or review relay files nothing: its failure is usually the repo's own. A repeat, the same title
already open upstream, is a comment on that issue, never a second one. Nothing filed names or links the repo it came
from, not even its name, nor any of its issues by number. Calls on the upstream repo run with DOKIMA_UPSTREAM_TOKEN,
which the workflow mints from the App's own key.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

from dokima import manifest, settings

# The workflows whose failures file nothing upstream: the two test checks and the review relay, which holds no key.
NOT_FILED = ("full-suite", "acceptance-criteria", "reviews")


def repo():
    """The upstream repo the settings name, as OWNER/NAME; empty for none or this repo."""
    got = str((settings.read().get("upstream") or {}).get("repo") or "").strip()
    return "" if got.lower() == os.environ.get("GITHUB_REPOSITORY", "").lower() else got


def gh(*args):
    """Run the GitHub CLI with the upstream repo's key and return its output."""
    env = dict(os.environ)
    if os.environ.get("DOKIMA_UPSTREAM_TOKEN"):
        env["GH_TOKEN"] = os.environ["DOKIMA_UPSTREAM_TOKEN"]
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, env=env).stdout


def scrub(text):
    """TEXT without the repo it came from: its name, links and issue numbers."""
    here = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in here:
        owner, name = here.split("/", 1)
        full = rf"{re.escape(owner)}(?:/|%2F){re.escape(name)}"
        text = re.sub(rf"\S*(?<![\w.-]){full}(?![\w.-])\S*", "the repo", text, flags=re.I)
        text = re.sub(rf"(?<![\w./-]){re.escape(name)}(?![\w-]|\.\w)", "the repo", text, flags=re.I)
    return re.sub(r"(?<![\w/&])#\d+\b", "an issue there", text)


def label(up):
    """The filed label's name in the labels setting, created in UP when missing."""
    got = settings.read()
    name = str((got.get("labels") or {}).get("filed") or "filed-by-dokima")
    want = manifest.labels(got)[name]
    try:
        gh("api", f"repos/{up}/labels/{urllib.parse.quote(name, safe='')}")
    except subprocess.CalledProcessError:
        try:
            gh("api", "-X", "POST", f"repos/{up}/labels", "-f", f"name={name}",
               "-f", f"color={want['color']}", "-f", f"description={want['description']}")
        except subprocess.CalledProcessError:
            pass  # a refused creation is left to the filing itself, which then says GitHub's reason
    return name


def now():
    """The time, as a comment says it."""
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())


def file(up, title, body, comment, first_too=False):
    """Open an issue in UP titled TITLE, or comment on the open one titled so.

    Returns (number, repeat). A repeat gets COMMENT; so does a first issue when FIRST_TOO. Raises CalledProcessError when GitHub refuses."""
    title, body = scrub(title), scrub(body)
    name = label(up)
    found = json.loads(gh("issue", "list", "--repo", up, "--state", "open", "--label", name,
                          "--search", f"{title.replace(chr(34), ' ')} in:title", "--json", "number,title",
                          "--limit", "100") or "[]")
    same = [i["number"] for i in found if i.get("title") == title]
    if same:
        n, repeat = min(same), True
    else:
        url = gh("issue", "create", "--repo", up, "--title", title, "--body", body, "--label", name).strip()
        n, repeat = int(url.rstrip("/").rsplit("/", 1)[-1]), False
    if repeat or first_too:
        gh("issue", "comment", str(n), "--repo", up, "--body", scrub(comment))
    return n, repeat


def file_problem(up, title, text, evidence=None):
    """File a problem a review tagged as Dokima's fault in UP; returns (number, repeat).

    Its body is the problem's own text and evidence, naming nothing of the repo it came from."""
    body = [text] + (["", f"**Evidence:** {evidence}"] if evidence else [])
    body += ["", "Dokima found this problem in its own work on a repo it runs on."]
    return file(up, title, "\n".join(body), f"Raised again on a repo Dokima runs on, {now()}.")


def failed(workflow, job):
    """File the failure of JOB in WORKFLOW upstream; returns the exit code."""
    workflow = workflow[:-len(".yml")] if workflow.endswith(".yml") else workflow
    up = repo()
    if not up:
        print("No upstream repo is set, so the failure is not filed upstream.")
        return 0
    if workflow in NOT_FILED:
        print(f"{workflow}.yml fails on the repo's own work as often as Dokima's, so its failure is not filed upstream.")
        return 0
    title = f"Failed run: the {job} job of {workflow}.yml"
    body = (f"The {job} job of Dokima's shared workflow {workflow}.yml failed on a repo Dokima runs on.\n\n"
            "Each later failure of the same job is a comment here.")
    try:
        n, _ = file(up, title, body, f"The {job} job of {workflow}.yml failed, {now()}.", True)
    except subprocess.CalledProcessError as e:
        why = " ".join((e.stderr or str(e)).split())
        print(f"::warning title=Failure not filed upstream::{title}: {why}")
        return 1
    print(f"Filed upstream: {up} issue {n}")
    return 0


def failed_results(workflow):
    """File each job RESULTS, `JOB=RESULT` pairs, names as failed; returns the exit code."""
    jobs = [job for job, _, result in (p.partition("=") for p in os.environ.get("RESULTS", "").split())
            if result == "failure"]
    return max((failed(workflow, job) for job in jobs), default=0)


def main(argv):
    """The command line; see the module's docstring."""
    if argv == ["owner"]:
        print(repo().split("/")[0])
        return 0
    if len(argv) == 3 and argv[0] == "failed":
        return failed(argv[1], argv[2])
    if len(argv) == 2 and argv[0] == "failed":
        return failed_results(argv[1])
    print("usage: python3 -m dokima.upstream failed WORKFLOW [JOB] | owner", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

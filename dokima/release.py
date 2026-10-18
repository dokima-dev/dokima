"""Make Dokima's release from the changelog, after each push to main (#755).

    python3 -m dokima.release <owner/repo> <commit>     # run from the repo root

When CHANGELOG.md holds a section for VERSION and GitHub has no VERSION release yet, makes the VERSION tag and its
GitHub release at the commit, with that section as the release notes. With no changelog, no section, or the release
already made, it makes nothing and exits 0. When GitHub refuses, it exits 1 and says why.
"""
import re
import subprocess
import sys

VERSION = "v0.1.0"
CHANGELOG = "CHANGELOG.md"


def section(text, version):
    """The lines under the heading naming version, up to the next as high; else None."""
    lines = text.splitlines()
    heading = re.compile(r"^(#{1,6})\s+.*" + re.escape(version) + r"(?![0-9])")
    for i, line in enumerate(lines):
        m = heading.match(line)
        if m:
            out = []
            for later in lines[i + 1:]:
                h = re.match(r"^(#{1,6})\s", later)
                if h and len(h.group(1)) <= len(m.group(1)):
                    break
                out.append(later)
            return "\n".join(out).strip() + "\n"
    return None


def gh(*args):
    """Runs gh, returning the finished process."""
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def run(repo, sha, path=CHANGELOG, version=VERSION):
    """Makes the release when it is due; returns the exit code."""
    try:
        with open(path) as f:
            notes = section(f.read(), version)
    except FileNotFoundError:
        print(f"No {path} yet, so no release.")
        return 0
    if notes is None:
        print(f"{path} has no {version} section yet, so no release.")
        return 0
    seen = gh("release", "view", version, "--repo", repo)
    if seen.returncode == 0:
        print(f"{version} is already released.")
        return 0
    if "not found" not in (seen.stderr or "").lower():
        print(f"Could not check for the {version} release: {seen.stderr.strip()}", file=sys.stderr)
        return 1
    made = gh("release", "create", version, "--repo", repo, "--target", sha, "--title", version, "--notes", notes)
    if made.returncode != 0:
        print(f"GitHub refused the {version} release: {made.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"Released {version} at {sha}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python3 -m dokima.release <owner/repo> <commit>")
    sys.exit(run(sys.argv[1], sys.argv[2]))

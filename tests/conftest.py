"""Every test judges this checkout's code, never the machine it runs on (#449, #385)."""
import os
import sys


# Tests judge this checkout's code on any machine (#449, #385). The agent's machine points Python at a runtime
# copy of Dokima and sets its own run's settings; none of that may reach a test or a subprocess it starts.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for k in ("STAGE", "ROLE", "N", "PACK", "OUT", "CARD_ID", "GITHUB_REPOSITORY", "PYTHONSAFEPATH"):
    os.environ.pop(k, None)
os.environ["PYTHONPATH"] = ROOT
sys.path[:] = [ROOT] + [x for x in sys.path if os.path.abspath(x or ".") != "/tmp/runtime"]

# Records live as files on the logs branch (#610). Tests never reach GitHub's: unless a test names its own, the logs
# remote is an empty local git repo, so a run reads no record file and saves none to GitHub.
if not os.environ.get("DOKIMA_LOGS_REMOTE"):
    import subprocess
    import tempfile
    _logs = os.path.join(tempfile.mkdtemp(prefix="dokima-logs-"), "logs.git")
    subprocess.run(["git", "init", "-q", "--bare", _logs], check=True)
    os.environ["DOKIMA_LOGS_REMOTE"] = _logs

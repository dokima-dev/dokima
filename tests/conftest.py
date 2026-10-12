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

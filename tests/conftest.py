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


def pytest_ignore_collect(collection_path, config):
    """Leave out the real GitHub checks in tests/nightly unless a run names that folder (#626).

    They post to and read from real GitHub, so only the nightly workflow runs them, by naming tests/nightly; the all
    tests check (`pytest tests`) and a bare `pytest` from the root never collect them."""
    nightly = os.path.join(ROOT, "tests", "nightly")
    path = str(collection_path)
    if path != nightly and not path.startswith(nightly + os.sep):
        return None
    asked = any(os.path.abspath(str(a).split("::")[0]).startswith(nightly) for a in config.args)
    return None if asked else True

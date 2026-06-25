import subprocess

from ..util.logger import logger
from .common import activity_state



def users_not_active() -> activity_state:
    try:
        res = subprocess.run(["who"], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"'who' exited with {res.returncode}: {res.stderr.strip()}.")

        lines = [line.strip() for line in (res.stdout or "").splitlines() if line.strip()]
        if lines:
            msg = f"logged-in sessions detected ({len(lines)})."
            return activity_state(False, "users", msg)

        msg = "no logged-in users."
        return activity_state(True, "users", msg)
    
    except Exception as e:
        logger.exception(f"users: error checking logged-in users: {e}")
        return activity_state(False, "users", "Error while checking state. See logs.")

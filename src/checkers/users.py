import subprocess

from ..util.logger import logger
from .common import activity_state


def users_not_active() -> activity_state:
    try:
        # -h - print no header info
        res = subprocess.run(["w", "-h"], check=True, capture_output=True, text=True)
        lines = [
            line.strip() for line in (res.stdout or "").splitlines() if line.strip()
        ]
        if lines:
            username = lines[0].split(" ")[0]
            ip = lines[0].split(" ")[2]
            msg = f"logged-in sessions detected ({username}@{ip})."
            return activity_state(False, "users", msg)

        msg = "no logged-in users."
        return activity_state(True, "users", msg)

    except subprocess.CalledProcessError as e:
        logger.error(f"'who' exited with {e.returncode}: {e.stderr.strip()}.")
        return activity_state(False, "users", "Error while checking state. See logs.")
    except Exception:
        logger.exception("users: error checking logged-in users")
        return activity_state(False, "users", "Error while checking state. See logs.")

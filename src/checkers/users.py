import subprocess

import jc
from jc.jc_types import Iterator, JSONDictType

from src.checkers.common import activity_state
from src.logger import logger


def users_not_active() -> activity_state:
    try:
        # -h - print no header info
        res = subprocess.run(["w"], check=True, capture_output=True, text=True)
        res_json = jc.parse("w", (res.stdout or "").splitlines())

        if not res_json:
            msg = "no logged-in users."
            return activity_state(True, "users", msg)

        if isinstance(res_json, Iterator):
            session = next(res_json)
        elif isinstance(res_json, list):
            session = res_json[0]
        else:
            session = res_json

        username = session["user"]
        ip = session["from"]
        msg = f"logged-in sessions detected ({username}@{ip})."
        return activity_state(False, "users", msg)

    except subprocess.CalledProcessError as e:
        logger.error(f"'who' exited with {e.returncode}: {e.stderr.strip()}.")
        return activity_state(False, "users", "Error while checking state. See logs.")
    except Exception:
        logger.exception("users: error checking logged-in users")
        return activity_state(False, "users", "Error while checking state. See logs.")

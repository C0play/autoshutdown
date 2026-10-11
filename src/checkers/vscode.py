import subprocess

from src.checkers.common import activity_state
from src.logger import logger


def vscode_not_active() -> activity_state:
    try:
        res = subprocess.run(
            ["pgrep", "-f", "extensionHost"], capture_output=True, text=True
        )
        if res.returncode == 0:
            pids = res.stdout.strip().split()

            msg = f"active extension host detected ({len(pids)} process{'es' if len(pids) > 1 else ''})."
            return activity_state(False, "vscode", msg)

        msg = "no active extension host."
        return activity_state(True, "vscode", msg)

    except Exception:
        logger.exception("vscode: error checking processes")
        return activity_state(False, "vscode", "Error while checking state. See logs.")

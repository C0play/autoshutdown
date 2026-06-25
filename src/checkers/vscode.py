import subprocess

from ..util.logger import logger
from .common import activity_state



def vscode_not_active() -> activity_state:
    try:
        res = subprocess.run(["pgrep", "-f", "extensionHost"], capture_output=True, text=True)
        if res.returncode == 0:
            pids = res.stdout.strip().split()

            msg = f"active extension host detected ({len(pids)} process{"es" if len(pids) > 1 else ""})."
            return activity_state(False, "vscode", msg)
        
        msg = "no active extension host."
        return activity_state(True, "vscode", msg)
    
    except Exception as e:
        logger.exception(f"vscode: error checking processes: {e}")
        return activity_state(False, "vscode", "Error while checking state. See logs.")
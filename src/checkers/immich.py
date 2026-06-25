import subprocess
import re

from ..util.logger import logger
from .common import activity_state
from ..config import ImmichConfig



def immich_not_active(cfg: ImmichConfig) -> activity_state:
    try:
        cmd = ["docker", "logs", "--since", f"{cfg.timeout}s", "immich_server"]
        logs = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        

        relevant_lines = [
            line for line in logs.splitlines() 
            if "GET /api/assets/" in line 
            or "GET /api/albums/" in line
            or "POST /api/sync/" in line
        ]
        
        if relevant_lines:
            # Get IP and clear ANSI escape sequences
            last_line = relevant_lines[-1].strip()
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_line = ansi_escape.sub('', last_line)
            
            ip = clean_line.split()[-1] if clean_line else "unknown"
            msg = f"active user detected in logs (IP: {ip}, {len(relevant_lines)} hits)."
            return activity_state(False, "immich", msg)

        msg = f"no activity in logs."
        return activity_state(True, "immich", msg)
    
    except Exception as e:
        logger.exception(f"immich: error checking status: {e}")
        return activity_state(False, "immich", "Error while checking state. See logs.")

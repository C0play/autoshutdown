import subprocess
import json

from ..util.logger import logger
from .common import activity_state



def minecraft_not_active() -> activity_state:
    """Zwraca: True jeśli Minecraft nie blokuje shutdown, inaczej False."""
    cmd = ["docker", "ps", "--filter", "name=mc_*", "--format", "json"]
    try:
        res = subprocess.run(cmd, capture_output=True, check=True, text=True)
        output = res.stdout.strip()
        
        if not output:
            msg = "no active containers detected."
            return activity_state(True, "minecraft", msg)
        else:
            containers = [json.loads(line) for line in output.splitlines() if line]
            names = ', '.join(c.get("Names", "unknown") for c in containers)
            if names:
                logger.debug(f"minecraft: containers online ({len(containers)}): {names}")
            
            return activity_state(False, "minecraft", f"{len(containers)} containers online")
        
    except Exception as e:
        logger.exception(f"minecraft: error checking containers: {e}")
        return activity_state(False, "minecraft", "Error while checking state. See logs.")

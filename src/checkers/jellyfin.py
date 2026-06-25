import requests
from datetime import (
    datetime,
    timezone,
    timedelta
)

from ..util.logger import logger
from .common import activity_state
from ..config import JellyfinConfig


def jellyfin_get_devices(cfg: JellyfinConfig):
    try:
        response = requests.get(
            f"{cfg.url}/Devices",
            headers={"X-Emby-Token": cfg.api_key}
        )
        response.raise_for_status()
        return response.json().get("Items", [])
    except requests.RequestException as e:
        logger.exception(f"error fetching devices: {e}")
        return []


def jellyfin_not_active(cfg: JellyfinConfig) -> activity_state:
    try:
        current_time = datetime.now(timezone.utc).timestamp()
        
        devices = jellyfin_get_devices(cfg)
        active_devices = []

        for device in devices:
            last_activity = device.get("DateLastActivity")
            username = device.get("LastUserName", "unknown")
            device_name = device.get("Name", "unknown")

            if last_activity:
                try:
                    dt_str = last_activity.replace('Z', '+00:00')
                    last_activity_time = datetime.fromisoformat(dt_str).timestamp()
                    
                    logger.debug(f"jellyfin: {device_name} last active {timedelta(seconds=int(current_time - last_activity_time))} ago.")
                    
                    if current_time - last_activity_time < cfg.timeout:
                        active_devices.append(f"{device_name}:{username}")

                except (ValueError, TypeError):
                    continue
        
        if active_devices:
            msg = f"active devices detected ({len(active_devices)}): {active_devices}"
            return activity_state(False, "jellyfin", msg)
        else:
            msg = f"no active devices detected."
            return activity_state(True, "jellyfin", msg)

    except Exception as e:
        logger.exception(f"jellyfin: error checking status: {e}")
        return activity_state(False, "jellyfin", "Error while checking state. See logs.")
    
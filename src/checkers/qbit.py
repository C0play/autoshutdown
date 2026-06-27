from typing import TypedDict, cast
import qbittorrentapi

from ..util.logger import logger
from .common import activity_state
from ..config import QbitConfig



class TorrentInfo(TypedDict):
    state: str
    progress: float
    name: str
    eta: int
    priority: int
    num_complete: int # all known seeders, including not connected



class TorrentProperties(TypedDict):
    dl_speed_avg: int
    dl_speed: int



def qbit_not_active(cfg: QbitConfig) -> activity_state:
    try:
        with qbittorrentapi.Client(host=cfg.url, username=cfg.user, password=cfg.password) as client:
            torrents_info = client.torrents.info()
            
            for torrent in torrents_info:
                info = cast(TorrentInfo, dict(torrent))
                properties = cast(TorrentProperties, dict(torrent.properties))
                
                # skip all torrents, that are not in a state, that would halt shutdown
                if not (torrent.get("state") in ["downloading", "checkingUP", "allocating"]):
                    continue
                
                progress = info.get("progress", 0) * 100
                priority = info.get("priority", -1)
                
                dl_speed_avg = properties.get("dl_speed_avg", 0)
                dl_speed = properties.get("dl_speed", 0)
                
                # if a torrent is experiencing a surge of down speed, suspend
                if dl_speed_avg > 0:
                    ratio = dl_speed / dl_speed_avg
                    if ratio > cfg.active_ratio:
                        msg = f"torrent {priority} is downloading (ratio={(ratio):.2f}, {progress:.1f}%)."
                        return activity_state(False, "qbit", msg)

                eta = info.get("eta", 864000)

                # if a torrent is about to finish, suspend
                if eta < cfg.max_eta:
                    msg = f"torrent {priority} will complete in {eta / 60:.1f}min."
                    return activity_state(False, "qbit", msg)
                
                # if a torrent is rare, suspend
                num_seeds_total = info.get("num_complete", 100)
                if num_seeds_total <= cfg.rare_limit and dl_speed > 0:
                    msg = f"torrent {priority} is rare and downloading (seeds: {num_seeds_total}, speed: {dl_speed/1024:.1f} KB/s)."
                    return activity_state(False, "qbit", msg)
            
            msg = f"no important downloads in progress."
            return activity_state(True, "qbit", msg)
        
    except Exception as e:
        logger.exception(f"qbit: error checking status: {e}")
        return activity_state(False, "qbit", "Error while checking state. See logs.")


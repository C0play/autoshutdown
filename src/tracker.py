import subprocess
import threading
import requests
import time
from functools import partial

from .checkers.jellyfin import jellyfin_not_active
from .checkers.vscode import vscode_not_active
from .checkers.minecraft import minecraft_not_active
from .checkers.users import users_not_active
from .checkers.qbit import qbit_not_active
from .checkers.immich import immich_not_active

from .util.logger import logger
from .util.prometheus import Metrics
from .config import Config



class ServiceTracker:

    def __init__(self, metrics: Metrics, config: Config, poll_rate: int) -> None:
        self.prometheus = metrics
        self.cfg = config
        self.poll_rate = poll_rate
        self.counter = 0

        self.services = [
            partial(immich_not_active, cfg=self.cfg.immich),
            partial(jellyfin_not_active, cfg=self.cfg.jellyfin),
            partial(qbit_not_active, cfg=self.cfg.qbit),
            vscode_not_active,
            minecraft_not_active,
            users_not_active,
        ]


    def run(self) -> None:
        threading.Thread(
            target=self.__start_loop,
            daemon=True
        ).start()


    def __start_loop(self) -> None:
        tries = self.poll_rate

        while True:
            time.sleep(self.cfg.common.shutdown_timeout / self.poll_rate)
            
            all_inactive = True
            for checker in self.services:

                res = checker()
                all_inactive &= res.not_active

                logger.info(f"{res.service_name}: {res.info}")

                (self.prometheus.service_states
                    .labels(service=res.service_name)
                    .set(not res.not_active)
                )

            if all_inactive:
                self.counter = self.counter + 1
                self.prometheus.shutdown_gauge.inc()
            else:
                self.counter = 0
                self.prometheus.shutdown_gauge.set(0)
            
            logger.info(f"===== Shutdown counter: {self.counter}/{tries} =====")

            if self.counter == tries:
                self.__init_shutdown()


    def __init_shutdown(self) -> None:
        try:
            self.__pre_shutdown()
            logger.info("Shutdown: all checks True, shutting down.")
            subprocess.run(["sudo", "shutdown"], check=True)
        except Exception as e:
            logger.exception(f"Shutdown: {e}")
    
    
    def __pre_shutdown(self) -> None:
        
        logger.info("Shutdown: all checks True, running pre-shutdown scripts.")

        if self.cfg.notification.ntfy_url:
            requests.post(
                self.cfg.notification.ntfy_url,
                data=f"**{self.cfg.common.hostname}** has been shut down",
                headers={
                    "Markdown": "1",
                    "Title": "Shutdown",
                    "Tags": "red_circle"
            })

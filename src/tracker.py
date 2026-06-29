import subprocess
import threading
import requests
import time
from functools import partial
from typing import Callable
from datetime import datetime

from .checkers.common import activity_state
from .util.logger import logger
from .util.prometheus import Metrics
from .config import Config



class ServiceTracker:

    def __init__(self, metrics: Metrics, config: Config) -> None:
        self.prometheus = metrics
        self.cfg = config
        
        self.counter = 0
        self.suspend_until = datetime.now()
        self.latest_info: list[dict] = []

        self.services: list[Callable[..., activity_state]] = []


    def add_service(
        self,
        is_inactive: Callable[..., activity_state],
        config = None
    ) -> 'ServiceTracker':
        
        if config:
            self.services.append(partial(is_inactive, cfg=config))
        else:
            self.services.append(is_inactive)
        
        logger.info(f"loaded {is_inactive.__name__.split("_", 1)[0]} service successfully")
        
        return self


    def run(self) -> None:
        threading.Thread(
            target=self.__start_loop,
            daemon=True
        ).start()


    def __start_loop(self) -> None:
        max_count = self.cfg.common.poll_rate

        while True:
            time.sleep(self.cfg.common.shutdown_timeout / self.cfg.common.poll_rate)
            self.latest_info = []
            all_inactive = True
            for checker in self.services:

                res = checker()
                all_inactive &= res.not_active
                self.latest_info.append({
                    "service": res.service_name,
                    "info": res.info
                })

                logger.info(f"{res.service_name}: {res.info}")

                (self.prometheus.service_states
                    .labels(service=res.service_name)
                    .set(not res.not_active)
                )

            if all_inactive and self.suspend_until <= datetime.now():
                self.counter = self.counter + 1
                self.prometheus.shutdown_gauge.inc()
            elif not all_inactive:
                self.counter = 0
                self.prometheus.shutdown_gauge.set(0)
            
            logger.info(f"===== Shutdown counter: {self.counter}/{max_count} =====")

            if self.counter == max_count:
                if self.suspend_until > datetime.now():
                    logger.info(f"shutdown suspended until: {self.suspend_until}")
                else:
                    self.init_shutdown()

            # time.sleep(self.cfg.common.shutdown_timeout / self.cfg.common.poll_rate)


    def init_shutdown(self) -> None:
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

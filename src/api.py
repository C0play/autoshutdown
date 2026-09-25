from datetime import UTC, datetime, timedelta

from flask import Flask
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from .tracker import ServiceTracker
from .util.prometheus import Metrics


class API:
    def __init__(self, metrics: Metrics, tracker: ServiceTracker) -> None:

        self.metrics = metrics
        self.tracker = tracker

        self.app = Flask(__name__)
        self.__register_routes()

    def __register_routes(self) -> None:

        @self.app.get("/info")
        def get_info():
            return self.tracker.latest_info, 200

        @self.app.post(f"/{self.tracker.cfg.common.shutdown_type}")
        def shutdown():
            self.tracker.init_poweroff()
            return "shutdown initiated", 200

        @self.app.post("/suspend/<time>")
        def set_suspend(time: int):
            self.tracker.suspend_until = datetime.now(UTC) + timedelta(
                minutes=max(int(time), 0)
            )
            return {"timestamp": self.tracker.suspend_until}, 200

        @self.app.get("/suspend")
        def get_suspend():
            is_suspended = self.tracker.suspend_until > datetime.now(UTC)
            time = 0 if not is_suspended else self.tracker.suspend_until
            return {"suspended": is_suspended, "timestamp": time}, 200

        @self.app.route("/metrics")
        def serve_metrics():
            return (
                generate_latest(self.metrics.registry),
                200,
                {"Content-Type": CONTENT_TYPE_LATEST},
            )

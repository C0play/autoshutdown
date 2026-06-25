from flask import Flask

from .util.prometheus import Metrics

from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)

class API:

    def __init__(self, metrics: Metrics) -> None:
        self.metrics = metrics
        self.app = Flask(__name__)
        self.__register_routes()


    def __register_routes(self) -> None:

        @self.app.route("/metrics")
        def serve_metrics():
            return generate_latest(self.metrics.registry), 200, {"Content-Type": CONTENT_TYPE_LATEST}

from prometheus_client import (
    CollectorRegistry,
    Gauge,
)

from ..config import Config


class Metrics:

    def __init__(self, service_names: list[str], config: Config) -> None:
        self.registry = CollectorRegistry()
        
        self.shutdown_gauge = Gauge(
            "shutdown_progress",
            "Current progress of the shutdown counter",
            registry=self.registry,
            namespace="autoshutdown",
            subsystem=config.common.hostname
        )

        self.service_states = Gauge(
            "service_state",
            "Whether a service is active or not",
            labelnames=["service"],
            registry=self.registry,
            namespace="autoshutdown",
            subsystem=config.common.hostname
        )

        for name in service_names:
            self.service_states.labels(service=name)

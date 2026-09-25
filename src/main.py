import os
from collections.abc import Callable
from dataclasses import dataclass

from src.api import API
from src.checkers.immich import immich_not_active
from src.checkers.jellyfin import jellyfin_not_active
from src.checkers.minecraft import minecraft_not_active
from src.checkers.qbit import qbit_not_active
from src.checkers.users import users_not_active
from src.checkers.vscode import vscode_not_active
from src.config import Config, EnvConfig, ImmichConfig, JellyfinConfig, QbitConfig
from src.logger import logger
from src.prometheus import Metrics
from src.tracker import ServiceTracker


@dataclass
class Service:
    func: Callable
    config: type[EnvConfig] | None = None


def main():

    services: dict[str, Service] = {
        "jellyfin": Service(jellyfin_not_active, JellyfinConfig),
        "immich": Service(immich_not_active, ImmichConfig),
        "minecraft": Service(minecraft_not_active),
        "qbit": Service(qbit_not_active, QbitConfig),
        "users": Service(users_not_active),
        "vscode": Service(vscode_not_active),
    }
    config = Config.from_env()
    metrics = Metrics(list(services.keys()), config.common.hostname)
    tracker = ServiceTracker(metrics, config)

    for name, service in services.items():
        if os.getenv(name.upper()) is None:
            logger.info(f"NOT adding service {name} to tracker.")
            continue
        logger.info(f"adding service {name} to tracker.")
        service_config = service.config.from_env() if service.config else None
        tracker.add_service(service.func, service_config)

    tracker.run()
    API(metrics, tracker).app.run(
        "0.0.0.0", config.common.port, debug=True, use_reloader=False
    )


if __name__ == "__main__":
    main()

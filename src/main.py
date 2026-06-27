from .config import load_configs
from .util.prometheus import Metrics
from .api import API
from .tracker import ServiceTracker

from .checkers.jellyfin import jellyfin_not_active
from .checkers.vscode import vscode_not_active
from .checkers.minecraft import minecraft_not_active
from .checkers.users import users_not_active
from .checkers.qbit import qbit_not_active
from .checkers.immich import immich_not_active



def main():

    services = ["jellyfin", "immich", "minecraft", "qbit", "users", "vscode"]
    config = load_configs()
    metrics = Metrics(services, config.common.hostname)

    tracker = (ServiceTracker(metrics, config)
                .add_service(jellyfin_not_active, config.jellyfin)
                .add_service(immich_not_active, config.immich)
                .add_service(qbit_not_active, config.qbit)
                .add_service(vscode_not_active)
                .add_service(minecraft_not_active)
                .add_service(users_not_active)
    )
    tracker.run()

    API(metrics, tracker).app.run("0.0.0.0", config.common.port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
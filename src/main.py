from .config import load_configs
from .util.prometheus import Metrics
from .api import API
from .tracker import ServiceTracker


def main():

    services = ["jellyfin", "immich", "minecraft", "qbit", "users", "vscode"]
    config = load_configs()
    metrics = Metrics(services, config)

    tracker = ServiceTracker(metrics, config, 5)
    tracker.run()

    api = API(metrics)
    api.app.run("0.0.0.0", 6677, debug=True, use_reloader=False)



if __name__ == "__main__":
    main()
import os
from typing import NamedTuple

from dotenv import find_dotenv, load_dotenv


class ImmichConfig(NamedTuple):
    timeout: int

    def from_env(self) -> "ImmichConfig":
        return ImmichConfig(
            timeout=10 * 60, # min * sec
        )

class JellyfinConfig(NamedTuple):
    api_key: str
    url: str
    timeout: int

    def from_env(self) -> "JellyfinConfig":
        return JellyfinConfig(
            api_key=os.getenv("JELLYFIN_API_KEY", ""),
            url=os.getenv("JELLYFIN_URL", ""),
            timeout=5 * 60,  # min * sec
        )


class QbitConfig(NamedTuple):
    url: str
    port: int
    user: str
    password: str
    active_ratio: float
    max_eta: int
    rare_limit: int

    def from_env(self) -> "QbitConfig":
        return QbitConfig(
            url=os.getenv("QBIT_URL", ""),
            port=int(os.getenv("QBIT_PORT", "8080")),
            user=os.getenv("QBIT_USER", ""),
            password=os.getenv("QBIT_PASSWD", ""),
            active_ratio=1.0,
            max_eta=15 * 60, # min * sec
            rare_limit=5,
        )


class NotificationConfig(NamedTuple):
    ntfy_url: str

    def from_env(self) -> "NotificationConfig":
        return NotificationConfig(
            ntfy_url=os.getenv("NTFY_URL", "")
        )


class CommonConfig(NamedTuple):
    shutdown_timeout: int
    poll_rate: int
    hostname: str
    port: int


class Config(NamedTuple):
    common: CommonConfig
    notification: NotificationConfig
    immich: ImmichConfig
    jellyfin: JellyfinConfig
    qbit: QbitConfig



def load_configs() -> Config:

    path = find_dotenv()
    if not path:
        raise ValueError("config: path to .env not found")

    load_dotenv(path)

    return Config(
        CommonConfig(
            shutdown_timeout= int(os.getenv("TIMEOUT", 600)),
            port=int(os.getenv("PORT", 6677)),
            poll_rate=int(os.getenv("POLL_RATE", 5)),
            hostname=os.getenv("HOSTNAME", "")
        ),
        NotificationConfig(
            ntfy_url=os.getenv("NTFY_URL", "")
        ),
        ImmichConfig(
            timeout=10 * 60, # min * sec
        ),
        JellyfinConfig(
            api_key=os.getenv("JELLYFIN_API_KEY", ""),
            url=os.getenv("JELLYFIN_URL", ""),
            timeout=5 * 60,  # min * sec

        ),
        QbitConfig(
            url=os.getenv("QBIT_URL", ""),
            port=int(os.getenv("QBIT_PORT", "8080")),
            user=os.getenv("QBIT_USER", ""),
            password=os.getenv("QBIT_PASSWD", ""),
            active_ratio=1.0,
            max_eta=15 * 60, # min * sec
            rare_limit=5,
        )
    )

def __is_set(name: str) -> bool:
    return os.getenv(name.upper()) is not None

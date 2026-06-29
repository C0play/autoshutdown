from typing import NamedTuple
from dotenv import load_dotenv, find_dotenv
import os


class ImmichConfig(NamedTuple):
    timeout: int


class JellyfinConfig(NamedTuple):
    api_key: str
    url: str
    timeout: int


class QbitConfig(NamedTuple):
    url: str
    port: int
    user: str
    password: str
    active_ratio: float
    max_eta: int
    rare_limit: int


class NotificationConfig(NamedTuple):
    ntfy_url: str


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
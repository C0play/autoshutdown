import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import cast

from dotenv import find_dotenv, load_dotenv

from src.types import ShutdownType


@dataclass
class EnvConfig(ABC):
    @classmethod
    @abstractmethod
    def from_env(cls) -> "EnvConfig":
        """
        Load config from .env file.

        Returns:
            "EnvConfig": NamedTuple containing the configured fields.
        """


@dataclass
class ImmichConfig(EnvConfig):
    timeout: int

    @classmethod
    def from_env(cls) -> "ImmichConfig":
        return ImmichConfig(
            timeout=10 * 60,  # min * sec
        )


@dataclass
class JellyfinConfig(EnvConfig):
    api_key: str
    url: str
    timeout: int

    @classmethod
    def from_env(cls) -> "JellyfinConfig":
        return JellyfinConfig(
            api_key=os.getenv("JELLYFIN_API_KEY", ""),
            url=os.getenv("JELLYFIN_URL", ""),
            timeout=5 * 60,  # min * sec
        )


@dataclass
class QbitConfig(EnvConfig):
    url: str
    port: int
    user: str
    password: str
    active_ratio: float
    max_eta: int
    rare_limit: int

    @classmethod
    def from_env(cls) -> "QbitConfig":
        return QbitConfig(
            url=os.getenv("QBIT_URL", ""),
            port=int(os.getenv("QBIT_PORT", "8080")),
            user=os.getenv("QBIT_USER", ""),
            password=os.getenv("QBIT_PASSWD", ""),
            active_ratio=1.0,
            max_eta=15 * 60,  # min * sec
            rare_limit=5,
        )


@dataclass
class NotificationConfig(EnvConfig):
    ntfy_url: str

    @classmethod
    def from_env(cls) -> "NotificationConfig":
        return NotificationConfig(ntfy_url=os.getenv("NTFY_URL", ""))


@dataclass
class CommonConfig(EnvConfig):
    shutdown_timeout: int
    shutdown_type: ShutdownType
    poll_rate: int
    hostname: str
    port: int
    mock_shutdown: bool

    @classmethod
    def from_env(cls) -> "CommonConfig":
        return CommonConfig(
            shutdown_timeout=int(os.getenv("TIMEOUT", "600")),
            shutdown_type=cast(ShutdownType, os.getenv("SHUTDOWN_TYPE")),
            port=int(os.getenv("PORT", "6677")),
            poll_rate=int(os.getenv("POLL_RATE", "5")),
            hostname=os.getenv("HOSTNAME", ""),
            mock_shutdown=os.getenv("MOCK_SHUTDOWN", "false").lower()
            in ["true", "yes", "1"],
        )


@dataclass
class Config(EnvConfig):
    common: CommonConfig
    notification: NotificationConfig

    @classmethod
    def from_env(cls) -> "Config":
        path = find_dotenv()
        if not path:
            raise ValueError("config: path to .env not found")

        load_dotenv(path)

        return Config(
            CommonConfig.from_env(),
            NotificationConfig.from_env(),
        )

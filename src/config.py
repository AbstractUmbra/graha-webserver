"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from typing import Literal

from litestar.config.allowed_hosts import AllowedHostsConfig as LitestarAllowedHostsConfig
from litestar.config.compression import CompressionConfig as LitestarCompressionConfig
from litestar.config.cors import CORSConfig as LitestarCORSConfig
from litestar.config.csrf import CSRFConfig as LitestarCSRFConfig
from litestar.config.response_cache import ResponseCacheConfig as LitestarResponseCacheConfig
from msgspec import Struct, field

from .utils import resolve_docker_secret

__all__ = ("Config",)

type HTTPMethod = Literal["GET", "POST", "DELETE", "PATCH", "PUT", "HEAD", "TRACE", "OPTIONS", "*"]


class AllowedHostsConfig(Struct):
    allowed_hosts: list[str] = field(default_factory=lambda: ["*"])
    exclude: list[str] | None = None
    exclude_opt_key: str | None = None
    www_redirect: bool = True

    def to_litestar(self) -> LitestarAllowedHostsConfig:
        return LitestarAllowedHostsConfig(
            allowed_hosts=self.allowed_hosts,
            exclude=self.exclude,
            exclude_opt_key=self.exclude_opt_key,
            www_redirect=self.www_redirect,
        )


class CompressionConfig(Struct):
    backend: str

    def to_litestar(self) -> LitestarCompressionConfig:
        return LitestarCompressionConfig(backend=self.backend)


class CORSConfig(Struct):
    allow_origins: list[str] = field(default_factory=lambda: ["*"])
    allow_methods: list[HTTPMethod] = field(default_factory=lambda: ["*"])
    allow_headers: list[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = False
    allow_origin_regex: str | None = None
    expose_headers: list[str] = []
    max_age: int = 600

    def to_litestar(self) -> LitestarCORSConfig:
        return LitestarCORSConfig(
            allow_origins=self.allow_origins,
            allow_methods=self.allow_methods,  # pyright: ignore[reportArgumentType] # msgspec can't handle the native type
            allow_headers=self.allow_headers,
            allow_credentials=self.allow_credentials,
            allow_origin_regex=self.allow_origin_regex,
            expose_headers=self.expose_headers,
            max_age=self.max_age,
        )


class CSRFConfig(Struct):
    secret: str | None

    def to_litestar(self) -> LitestarCSRFConfig:
        return LitestarCSRFConfig(secret=self.secret or resolve_docker_secret("CSRF_SECRET"))


class ResponseCacheConfig(Struct):
    default_expiration: int = field(default=60)

    def to_litestar(self) -> LitestarResponseCacheConfig:
        return LitestarResponseCacheConfig(default_expiration=self.default_expiration)


class DatabaseConfig(Struct):
    host: str
    user: str
    db: str

    def to_dsn(self) -> str:
        passwd = resolve_docker_secret("POSTGRES_PASSWORD")
        return f"postgres://{self.user}:{passwd}@{self.host}/{self.db}"


class Config(Struct):
    """Required config for backend server."""

    debug: bool
    version: str
    database: DatabaseConfig
    allowed_hosts: AllowedHostsConfig
    compression: CompressionConfig
    cors: CORSConfig
    csrf: CSRFConfig
    response_cache: ResponseCacheConfig

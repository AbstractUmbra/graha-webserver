"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from pathlib import Path

from litestar import Litestar
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import (
    JsonRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
    YamlRenderPlugin,
)
from litestar.openapi.spec import Components, Contact, License, SecurityScheme
from litestar.static_files import create_static_files_router
from litestar_asyncpg import AsyncpgConfig, AsyncpgPlugin, PoolConfig

from .config import Config
from .utils import load_config_type, resolve_docker_config

__all__ = ("app",)

CONFIG = load_config_type(resolve_docker_config(env_var_name="CONFIG_PATH"), Config)

STATIC_DIRECTORY = Path("static/").resolve()
RESOURCES_DIRECTORY = Path("resources/").resolve()

app = Litestar(
    debug=CONFIG.debug,
    route_handlers=[
        create_static_files_router(path="/", name="static", directories=[STATIC_DIRECTORY]),
        create_static_files_router(path="/resources", name="resources", directories=[RESOURCES_DIRECTORY]),
    ],
    allowed_hosts=CONFIG.allowed_hosts.to_litestar(),
    cors_config=CONFIG.cors.to_litestar(),
    csrf_config=CONFIG.csrf.to_litestar(),
    compression_config=CONFIG.compression.to_litestar(),
    response_cache_config=CONFIG.response_cache.to_litestar(),
    openapi_config=OpenAPIConfig(
        title="Graha T'ia API",
        path="/docs",
        contact=Contact(name="AbstractUmbra", url="https://github.com/AbstractUmbra", email="umbra@abstractumbra.dev"),
        license=License(
            name="Mozilla Public License 2.0", identifier="MPL-2.0", url="https://www.mozilla.org/en-US/MPL/2.0/"
        ),
        version=CONFIG.version,
        security=[{"API Token": []}],
        components=Components(
            security_schemes={
                "API Token": SecurityScheme(
                    type="apiKey", name="Authorization", scheme="bearer", security_scheme_in="header"
                )
            },
        ),
        render_plugins=[
            ScalarRenderPlugin(),
            JsonRenderPlugin(),
            RedocRenderPlugin(),
            SwaggerRenderPlugin(path="/"),
            YamlRenderPlugin(),
            RapidocRenderPlugin(),
            StoplightRenderPlugin(),
        ],
    ),
    logging_config=LoggingConfig(
        disable_stack_trace={404}, log_exceptions="always", root={"level": "INFO", "handlers": ["queue_listener"]}
    ),
    middleware=[LoggingMiddlewareConfig(include_compressed_body=True, response_log_fields=["body"]).middleware],
    plugins=[AsyncpgPlugin(config=AsyncpgConfig(pool_config=PoolConfig(dsn=CONFIG.database.to_dsn())))],
)

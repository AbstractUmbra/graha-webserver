"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import os
from pathlib import Path

import msgspec
from litestar import Litestar
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec import Components, Contact, License, SecurityScheme
from litestar.static_files import create_static_files_router

from .config import Config

_config_file_path = os.getenv("CONFIG_FILE", "configs/app.json")

CONFIG_FILE = Path(_config_file_path).resolve()
if not CONFIG_FILE.exists():
    _msg = f"Config file not found at {str(CONFIG_FILE)!r}"
    raise RuntimeError(_msg)

with CONFIG_FILE.open("rb") as fp:
    CONFIG = msgspec.json.decode(fp.read(), type=Config)

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
        license=License(name="MPL v2"),
        version="",
        security=[{"API Token": []}],
        components=Components(
            security_schemes={
                "API Token": SecurityScheme(
                    type="apiKey", name="Authorization", scheme="bearer", security_scheme_in="header"
                )
            },
        ),
        render_plugins=[ScalarRenderPlugin(path=["/docs"])],
    ),
)

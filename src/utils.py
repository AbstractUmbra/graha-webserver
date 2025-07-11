"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import logging
import os
import pathlib
from typing import Literal, overload

import msgspec

__all__ = ("resolve_docker_secret",)

LOGGER = logging.getLogger("graha-utils")


@overload
def resolve_docker_secret(secret_name: str, *, content: Literal[False]) -> pathlib.Path: ...


@overload
def resolve_docker_secret(secret_name: str, *, content: Literal[True] = ...) -> str: ...


def resolve_docker_secret(secret_name: str, *, content: bool = True) -> pathlib.Path | str:
    """
    Method to resolve a Docker ``secret`` type value.

    Parameters
    ----------
    secret_name: :class:`str`
        The name of the docker secret.
        This should be the secret name, not file path nor any other identifier.
    content: :class:`bool`
        Whether to return the secret file's content or path. Default to ``True``.

    Raises
    ------
    ValueError
        Could not resolve the passed secret name.

    Returns
    -------
    :class:`pathlib.Path` | :class:`str`
    """  # noqa: D401, DOC501 # not very appropriate here
    secret_file_docker_env = os.getenv(f"{secret_name.upper()}_FILE")

    if secret_file_docker_env:
        path = pathlib.Path(secret_file_docker_env)
        if not path.exists():
            msg = f"Docker standard path to secret ({secret_name}) file provided but the file does not exist."
            raise RuntimeError(msg)
        if content is True:
            return path.read_text("utf-8").strip()
        return path

    secret_file = pathlib.Path(f"/var/run/secrets/{secret_name}")
    if secret_file.exists():
        if content is True:
            return secret_file.read_text("utf-8").strip()
        return secret_file

    msg_ = f"Unable to find provided secret by name: {secret_name!r}."
    raise ValueError(msg_)


@overload
def load_config_type[ConfigT: msgspec.Struct](
    path: pathlib.Path, type_: type[ConfigT], *, required: Literal[False]
) -> ConfigT | None: ...


@overload
def load_config_type[ConfigT: msgspec.Struct](
    path: pathlib.Path, type_: type[ConfigT], *, required: Literal[True] = ...
) -> ConfigT: ...


def load_config_type[ConfigT: msgspec.Struct](
    path: pathlib.Path, type_: type[ConfigT], *, required: bool = True
) -> ConfigT | None:
    path = path.resolve()
    if not path.exists():
        if required:
            msg_ = f"Required config file not found at {path}."
            raise RuntimeError(msg_)
        LOGGER.warning("Config file not found at path %r, skipping.", str(path))
        return None

    with path.open("rb") as fp:
        return msgspec.json.decode(fp.read(), type=type_)

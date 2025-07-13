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

__all__ = ("load_config_type", "resolve_docker_config", "resolve_docker_secret")

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
    """  # noqa: D401 # not very appropriate here
    secret_file_docker_env = os.getenv(f"{secret_name.upper()}_FILE")

    path = (
        pathlib.Path(secret_file_docker_env) if secret_file_docker_env else pathlib.Path(f"/var/run/secrets/{secret_name}")
    )

    if not path.exists():
        msg = f"Docker standard path to secret ({secret_name}) file provided but the file does not exist."
        raise ValueError(msg)

    if content is True:
        return path.read_text("utf-8").strip()
    return path


def resolve_docker_config(*, config_name: str | None = None, env_var_name: str | None = None) -> pathlib.Path:
    """Utility for resolving a configuration item from docker-compose provided ``configs:``.

    Parameters
    ----------
    config_name: :class:`str` | None
        The name of the config key in docker-compose. NOT the path to the config file.
    env_var_name: :class:`str` | None
        The name of the env var which dictates the path to the config file, if any.

    Raises
    ------
    ValueError
        One of the provided values did not fully resolve to a configuration file or spec.
    RuntimeError
        The resolved path to the configuration file did not exist.

    Returns
    -------
    :class:`pathlib.Path`
    """  # noqa: D401
    if config_name:
        path = pathlib.Path(f"/{config_name}")
    elif env_var_name:
        env_var = os.getenv(env_var_name.upper())
        if not env_var:
            raise ValueError("The provided environment variable does not exist.")
        path = pathlib.Path(env_var)
    else:
        raise ValueError("At least one of `config_name` or `env_var_name` must be provided.")

    path = path.resolve()

    if not path.exists():
        raise RuntimeError("The provided configuration name or env var does not resolve to locatable file.")

    return path


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
    """
    Method to load a provided path and parse it as a JSONified msgspec.Struct.

    Parameters
    ----------
    path: :class:`pathlib.Path`
        The path to the file.
    type_ Type[:class:`msgspec.Struct`]
        The custom subclass of Struct to parse as.
    required: :class:`bool`
        Whether this configuration is required for the application, or allowed to not exist.
        Defaults to ``True``.

    Raises
    ------
    RuntimeError
        If the config is not required but could not be parsed or found.

    Returns
    -------
    :class:`msgspec.Struct`
        The custom struct type you passed for ``type_``.
    """  # noqa: D401
    path = path.resolve()
    if not path.exists():
        if required:
            msg_ = f"Required config file not found at {path}."
            raise RuntimeError(msg_)
        LOGGER.warning("Config file not found at path %r, skipping.", str(path))
        return None

    with path.open("rb") as fp:
        return msgspec.json.decode(fp.read(), type=type_)

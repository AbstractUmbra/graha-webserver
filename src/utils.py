"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import os
import pathlib
from typing import Literal, overload

__all__ = ("resolve_docker_secret",)


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

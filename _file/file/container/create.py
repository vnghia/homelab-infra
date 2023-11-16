import base64
import hashlib
import tarfile
import tempfile
from typing import cast

import docker
from docker.models.containers import Container

from _file.file.container.common import (
    DOCKER_COMMON_KWARGS,
    UPLOAD_FILE_PATH,
    VOLUME_BIND_PATH,
)


def to_tar_file(content: bytes, path: str):
    tar_file = tempfile.NamedTemporaryFile()
    with tarfile.open(mode="w", fileobj=tar_file) as tar:
        with tempfile.NamedTemporaryFile() as f:
            f.write(content)
            f.flush()
            tar.add(f.name, arcname=path)
    tar_file.seek(0)
    return tar_file


def main():
    volume_proxy_container = cast(
        Container, docker.from_env().containers.create(**DOCKER_COMMON_KWARGS)
    )

    content = base64.standard_b64decode(input())
    volume_proxy_container.put_archive(
        VOLUME_BIND_PATH, to_tar_file(content, UPLOAD_FILE_PATH)
    )
    volume_proxy_container.remove(force=True)

    print(hashlib.sha256(content).hexdigest())


if __name__ == "__main__":
    main()

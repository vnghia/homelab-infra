import hashlib
from typing import cast

import docker
from docker.models.containers import Container

from _file.file.container.common import (
    DOCKER_COMMON_KWARGS,
    UPLOAD_FILE_PATH,
    load_upload_content,
    upload_content,
)


def main():
    content = load_upload_content()
    content_sha256 = hashlib.sha256(content).hexdigest()

    volume_proxy_container = cast(
        Container,
        docker.from_env().containers.run(
            command=["sha256sum", UPLOAD_FILE_PATH],
            detach=True,
            remove=False,
            **DOCKER_COMMON_KWARGS,
        ),
    )

    exit_code = volume_proxy_container.wait()["StatusCode"]
    hash_output = cast(bytes, volume_proxy_container.logs()).decode()[:64]
    if exit_code or hash_output != content_sha256:
        upload_content(volume_proxy_container, content)
    volume_proxy_container.remove(force=True)

    print(content_sha256)


if __name__ == "__main__":
    main()

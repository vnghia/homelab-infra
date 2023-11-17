import hashlib
from typing import cast

import docker
from docker.models.containers import Container

from _file.file.container.common import (
    DOCKER_COMMON_KWARGS,
    load_upload_content,
    upload_content,
)


def main():
    volume_proxy_container = cast(
        Container, docker.from_env().containers.create(**DOCKER_COMMON_KWARGS)
    )

    content = load_upload_content()
    upload_content(volume_proxy_container, content)
    volume_proxy_container.remove(force=True)

    print(hashlib.sha256(content).hexdigest())


if __name__ == "__main__":
    main()

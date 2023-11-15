import base64
import hashlib
import os
import random
import string
import tarfile
import tempfile

import docker


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
    VOLUME_BIND_PATH = "/nmt/volume/"
    volume_proxy_container = docker.from_env().containers.create(
        image="busybox:1.35.0-uclibc",
        name="".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(32)
        ),
        network_mode="none",
        platform=os.environ["IMAGE_PLATFORM"],
        volumes={
            os.environ["DOCKER_ASSET_VOLUME"]: {"bind": VOLUME_BIND_PATH, "mode": "rw"}
        },
    )

    content = base64.standard_b64decode(input())
    volume_proxy_container.put_archive(
        VOLUME_BIND_PATH, to_tar_file(content, os.environ["FILE_PATH"])
    )
    volume_proxy_container.remove(force=True)

    print(hashlib.sha256(content).hexdigest())


if __name__ == "__main__":
    main()

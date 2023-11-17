import base64
import os
import random
import string
import tarfile
import tempfile

from docker.models.containers import Container

BUSYBOX_IMAGE_TAG = "busybox:1.35.0-uclibc"
VOLUME_BIND_PATH = "/nmt/volume/"

UPLOAD_FILE_PATH = os.environ["FILE_PATH"]

DOCKER_COMMON_KWARGS = {
    "image": BUSYBOX_IMAGE_TAG,
    "name": "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(32)
    ),
    "network_mode": "none",
    "platform": os.environ["IMAGE_PLATFORM"],
    "volumes": {
        os.environ["DOCKER_ASSET_VOLUME"]: {"bind": VOLUME_BIND_PATH, "mode": "rw"}
    },
    "working_dir": VOLUME_BIND_PATH,
}


def load_upload_content():
    return base64.standard_b64decode(input())


def to_tar_file(content: bytes, path: str):
    tar_file = tempfile.NamedTemporaryFile()
    with tarfile.open(mode="w", fileobj=tar_file) as tar:
        with tempfile.NamedTemporaryFile() as f:
            f.write(content)
            f.flush()
            tar.add(f.name, arcname=path)
    tar_file.seek(0)
    return tar_file


def upload_content(container: Container, content: bytes):
    container.put_archive(VOLUME_BIND_PATH, to_tar_file(content, UPLOAD_FILE_PATH))

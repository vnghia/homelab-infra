import os
import random
import string

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

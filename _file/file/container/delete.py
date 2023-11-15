import os
import random
import string

import docker


def main():
    VOLUME_BIND_PATH = "/nmt/volume/"
    docker.from_env().containers.run(
        image="busybox:1.35.0-uclibc",
        command=["rm", "-rf", os.environ["FILE_PATH"]],
        name="".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(32)
        ),
        network_mode="none",
        platform=os.environ["IMAGE_PLATFORM"],
        remove=True,
        volumes={
            os.environ["DOCKER_ASSET_VOLUME"]: {"bind": VOLUME_BIND_PATH, "mode": "rw"}
        },
        working_dir=VOLUME_BIND_PATH,
    )


if __name__ == "__main__":
    main()

import docker

from _file.file.container.common import DOCKER_COMMON_KWARGS, UPLOAD_FILE_PATH


def main():
    docker.from_env().containers.run(
        command=["rm", "-rf", UPLOAD_FILE_PATH], remove=True, **DOCKER_COMMON_KWARGS
    )


if __name__ == "__main__":
    main()

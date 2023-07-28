import os

import docker


def main():
    container = docker.from_env().containers.get(os.environ["NTFY_CONTAINER_ID"])
    container.exec_run(
        ["ntfy", "user", "del", os.environ["NTFY_USERNAME"]],
    )


if __name__ == "__main__":
    main()

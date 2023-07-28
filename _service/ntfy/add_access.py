import os

import docker


def main():
    container = docker.from_env().containers.get(os.environ["NTFY_CONTAINER_ID"])
    container.exec_run(
        ["ntfy", "user", "add", "--role=admin", os.environ["NTFY_USERNAME"]],
        environment={"NTFY_PASSWORD": os.environ["NTFY_PASSWORD"]},
    )
    container.exec_run(["ntfy", "access", "*", "up*", "write-only"])


if __name__ == "__main__":
    main()

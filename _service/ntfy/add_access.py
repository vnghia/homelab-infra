import os

import docker


def main():
    container = docker.from_env().containers.get(os.environ["NTFY_CONTAINER_ID"])
    container.exec_run(
        ["ntfy", "user", "add", "--role=admin", os.environ["NTFY_USERNAME"]],
        environment={"NTFY_PASSWORD": os.environ["NTFY_PASSWORD"]},
    )

    container.exec_run(
        ["ntfy", "user", "add", os.environ["NTFY_WRITE_ONLY_USERNAME"]],
        environment={"NTFY_PASSWORD": os.environ["NTFY_WRITE_ONLY_PASSWORD"]},
    )
    exit_code, token_output = container.exec_run(
        ["ntfy", "token", "add", os.environ["NTFY_WRITE_ONLY_USERNAME"]]
    )
    assert exit_code == 0
    print(token_output.decode().split(" ")[1])

    container.exec_run(
        ["ntfy", "access", os.environ["NTFY_WRITE_ONLY_USERNAME"], "*", "write-only"]
    )
    container.exec_run(["ntfy", "access", "*", "up*", "write-only"])


if __name__ == "__main__":
    main()

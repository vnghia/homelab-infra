import os

import docker


def main():
    container = docker.from_env().containers.get(os.environ["CROWDSEC_CONTAINER_ID"])
    container.exec_run(["cscli", "bouncers", "delete", os.environ["BOUNCER_NAME"]])


if __name__ == "__main__":
    main()

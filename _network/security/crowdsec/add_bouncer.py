import os

import docker


def main():
    container = docker.from_env().containers.get(os.environ["CROWDSEC_CONTAINER_ID"])
    print(
        container.exec_run(
            [
                "cscli",
                "bouncers",
                "add",
                os.environ["BOUNCER_NAME"],
                "-k",
                os.environ["BOUNCER_KEY"],
                "--output",
                "raw",
            ]
        ).output.decode()
    )


if __name__ == "__main__":
    main()

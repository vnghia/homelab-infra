import os

import docker
from docker.errors import ContainerError


def main():
    restic_repo = "s3:{}/{}/{}".format(
        os.environ["S3_ENDPOINT"],
        os.environ["S3_BUCKET"],
        os.environ["RESTIC_REPO_PREFIX"],
    )

    client = docker.from_env()
    restic_image_id = os.environ["RESTIC_IMAGE_ID"]
    env = {
        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
        "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
        "RESTIC_REPOSITORY": restic_repo,
        "RESTIC_PASSWORD": os.environ["RESTIC_PASSWORD"],
    }

    try:
        client.containers.run(
            restic_image_id,
            command=["cat", "config"],
            detach=False,
            remove=True,
            environment=env,
        )
    except ContainerError as e:
        if (
            b"Fatal: unable to open config file: Stat: The specified key does not exist.\n"
            b"Is there a repository at the following location?" in e.stderr
        ):
            client.containers.run(
                restic_image_id,
                command=["init"],
                detach=False,
                remove=True,
                environment=env,
            )
        else:
            raise e

    print(restic_repo)


if __name__ == "__main__":
    main()

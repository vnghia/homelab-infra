import os

import docker


def main():
    docker.from_env().containers.run(
        os.environ["AWSCLI_IMAGE_ID"],
        command=[
            "s3",
            "rm",
            "--endpoint-url",
            os.environ["S3_ENDPOINT"],
            "--recursive",
            "s3://{}/{}".format(os.environ["S3_BUCKET"], os.environ["S3_PREFIX"]),
        ],
        detach=False,
        remove=True,
        environment={
            "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
        },
    )


if __name__ == "__main__":
    main()

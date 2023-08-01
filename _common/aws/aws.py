from pathlib import Path

from pulumi import ResourceOptions

from _command import Command
from _common import constant, storage_config
from _image import docker_image

_aws_env = storage_config["aws"]


def build_cleanup(
    name: str, opts: ResourceOptions, prefix: str | None = None, **kwargs
):
    Command.build(
        name,
        opts=opts.merge(ResourceOptions(protect=constant.PROJECT_STACK != "dev")),
        delete=Path(__file__).parent / "cleanup.py",
        update="",
        environment={
            "AWSCLI_IMAGE_ID": docker_image.image_map["awscli"]["image_id"],
            "S3_PREFIX": prefix,
        }
        | _aws_env
        | kwargs.pop("environment", {}),
        **kwargs
    )

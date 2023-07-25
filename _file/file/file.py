import base64
from pathlib import Path

from pulumi import Input, Output, ResourceOptions

from _command import Command
from _container.image.image import docker_image
from _data.docker import volume_map


class File:
    @classmethod
    def build_container_file(
        cls,
        name: str,
        opts: ResourceOptions,
        volume: str,
        path: Input[str],
        content: Input[str],
    ):
        return cls.__build(
            "{}-file".format(name),
            opts=opts,
            path=path,
            content=content,
            create_path=Path(__file__).parent / "container" / "create.py",
            delete_path=Path(__file__).parent / "container" / "delete.py",
            environment={
                "DOCKER_ASSET_IMAGE": docker_image.image_map["workaround"]["image_id"],
                "DOCKER_ASSET_VOLUME": volume_map[volume],
            },
        )

    @classmethod
    def __build(
        cls,
        name: str,
        opts: ResourceOptions,
        path: Input[str],
        content: Input[str],
        create_path: Path,
        delete_path: Path,
        **kwargs
    ):
        # TODO: Checking for diff (the content of this file and does it still exist)
        # Blocked by: https://github.com/pulumi/pulumi-command/issues/20
        file = Command.build(
            name,
            opts=opts.merge(ResourceOptions(delete_before_replace=True)),
            create=create_path,
            delete=delete_path,
            stdin=Output.from_input(content).apply(
                lambda content: base64.standard_b64encode(content.encode()).decode(),
            ),
            environment={"FILE_PATH": path} | kwargs.pop("environment", {}),
            **kwargs
        )
        return {"file": file, "sha256": file.stdout}

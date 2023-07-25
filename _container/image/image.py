from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _command import Command
from _common import docker_config, server_config


class DockerImage(ComponentResource):
    def __init__(self) -> None:
        super().__init__("container:docker:Image", "image")
        self.__child_opts = ResourceOptions(parent=self)
        image_config = docker_config.get("image", {})
        platform = server_config["platform"]

        self.image_map: dict = {}

        for key, data in image_config.items():
            self.image_map[key] = self.__get_image_id(
                name=data["name"], tag=data["tag"], platform=platform
            )

    def __get_image_id(self, name: str, tag: str, platform: str):
        tag_ = tag
        try:
            tag = eval(tag_, {}, {"platform": platform})
        except Exception:
            tag = tag_
        else:
            if not isinstance(tag, str):
                tag = tag_
        full_name = "{}:{}".format(name, tag)
        return {
            "image_name": full_name,
            "image_id": Command.build(
                full_name,
                opts=self.__child_opts,
                create=Path(__file__).parent / "get.py",
                environment={
                    "IMAGE_NAME": full_name,
                    "IMAGE_PLATFORM": "linux/{}".format(platform),
                },
            ).stdout,
        }


docker_image = DockerImage()

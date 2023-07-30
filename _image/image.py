from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _command import Command
from _common import constant, docker_config, get_logical_name, server_config


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

        self.__build_image_build(platform)

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

    def __build_image_build(self, platform: str):
        build_config = docker_config.get("build", {})
        for key, data in build_config.items():
            context_path = (
                Path(data["context"])
                .resolve(True)
                .relative_to(constant.PROJECT_ROOT_DIR)
            )
            dockerfile = (
                (context_path / data.get("dockerfile", "Dockerfile"))
                .resolve(True)
                .relative_to(constant.PROJECT_ROOT_DIR)
            )

            image_full_name = "{}/{}:{}".format(
                constant.PROJECT_NAME, key, constant.PROJECT_STACK
            )
            self.image_map[key] = {
                "image_name": image_full_name,
                "image_id": docker.Image(
                    get_logical_name(key),
                    build=docker.DockerBuildArgs(
                        args=data.get("args"),
                        builder_version=docker.BuilderVersion.BUILDER_BUILD_KIT,
                        context=str(context_path),
                        dockerfile=str(dockerfile),
                        platform="linux/{}".format(platform),
                    ),
                    image_name=image_full_name,
                    skip_push=True,
                ).id,
            }


docker_image = DockerImage()

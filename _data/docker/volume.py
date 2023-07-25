import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _common import docker_config, get_logical_name
from _data.docker.label import DOCKER_VOLUME_LABELS


class DockerVolume(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:docker:Volume", "volume")
        self.__child_opts = ResourceOptions(parent=self)

        self.__volumes: dict[str, docker.Volume] = {}

        self.__build_local_volume()

        self.volume_map = {k: v.name for k, v in self.__volumes.items()}
        self.register_outputs({"volume_map": self.volume_map})

    def __build_local_volume(self):
        volume_config = docker_config.get("volume", {})
        local_volume_config = volume_config.get("local", [])

        for name in local_volume_config:
            self.__volumes[name] = docker.Volume(
                get_logical_name(name),
                opts=self.__child_opts,
                driver="local",
                labels=DOCKER_VOLUME_LABELS,
            )


docker_volume = DockerVolume()

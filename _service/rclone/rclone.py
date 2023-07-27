from pulumi import ComponentResource, ResourceOptions

from _common import rclone_config, storage_config
from _container import DockerContainer
from _data.docker import docker_volume
from _network.traefik import traefik_proxy
from _secret import secret
from _service.resource import child_opts


class Rclone(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Rclone", "rclone", None, child_opts)
        if "combine" in storage_config["rclone"]:
            self.__webdav_container = DockerContainer.build(
                "rclone-webdav",
                opts=ResourceOptions(parent=self),
                image="rclone",
                command=[
                    "--config",
                    "{}{}".format(
                        rclone_config["volume"]["config"]["dir"],
                        docker_volume.rclone_config_path,
                    ),
                    "-v",
                    "serve",
                    "webdav",
                    "combine:",
                    "--addr",
                    "0.0.0.0:{}".format(rclone_config["port"]),
                    "--user",
                    secret.accounts["rclone"]["username"],
                    "--pass",
                    secret.accounts["rclone"]["password"],
                ],
                volume_config=rclone_config["volume"],
                labels={
                    "traefik-config-sha256": traefik_proxy.dynamic_config["rclone"][
                        "sha256"
                    ],
                    "rclone-plugin-alias": docker_volume.rclone_plugin_alias,
                },
            )
            self.webdav_container_id = self.__webdav_container.id
            self.register_outputs({"webdav_container_id": self.webdav_container_id})
        else:
            self.register_outputs({})


rclone = Rclone()

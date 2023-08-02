from pulumi import ComponentResource, ResourceOptions

from _common import container_storage_config, service_config, volume_config
from _container import DockerContainer
from _data.docker import docker_volume
from _network.traefik import traefik_proxy
from _secret import secret
from _service.resource import child_opts

_rclone_webdav_config = service_config["rclone-webdav"]
_rclone_webdav_volume = container_storage_config["rclone-webdav"]


class RcloneWebdav(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Rclone", "rclone-webdav", None, child_opts)
        if "combine" in volume_config:
            self.__webdav_container = DockerContainer.build(
                "rclone-webdav",
                opts=ResourceOptions(
                    parent=self,
                    depends_on=[traefik_proxy.dynamic_config["rclone-webdav"]["file"]],
                ),
                image="rclone",
                command=[
                    "--config",
                    "{}{}".format(
                        _rclone_webdav_volume["config"]["dir"],
                        docker_volume.rclone_config_path,
                    ),
                    "-v",
                    "serve",
                    "webdav",
                    "combine:",
                    "--addr",
                    "0.0.0.0:{}".format(_rclone_webdav_config["port"]),
                    "--user",
                    secret.accounts["rclone-webdav"]["username"],
                    "--pass",
                    secret.accounts["rclone-webdav"]["password"],
                ],
                labels={"rclone-plugin-alias": docker_volume.rclone_plugin_alias},
            )
            self.webdav_container_id = self.__webdav_container.id
            self.register_outputs({"webdav_container_id": self.webdav_container_id})
        else:
            self.register_outputs({})


rclone_webdav = RcloneWebdav()

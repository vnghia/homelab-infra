import os
from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import container_storage_config, service_config, storage_config
from _container import DockerContainer
from _data.docker import docker_volume
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_password_storage_config = service_config["password-storage"]
_password_storage_volume = container_storage_config["password-storage"]


class PasswordStorage(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "service:index:PasswordStorage", "password-storage", None, child_opts
        )
        self.__container = DockerContainer.build(
            "password-storage",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["password-storage"]["file"]],
            ),
            image="rclone",
            command=[
                "--config",
                os.fspath(
                    Path(
                        _password_storage_volume["config"]["dir"],
                    )
                    / docker_volume.rclone_config_path
                ),
                "-v",
                "serve",
                "http",
                "crypt-{}-password:".format(storage_config["bucket"]),
                "--addr",
                "0.0.0.0:{}".format(_password_storage_config["port"]),
                "--read-only",
            ],
            labels={"rclone-plugin-alias": docker_volume.rclone_plugin_alias},
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


password_storage = PasswordStorage()

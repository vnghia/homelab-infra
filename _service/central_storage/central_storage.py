import os
from pathlib import Path

from pulumi import ComponentResource, Output, ResourceOptions

from _common import container_storage_config, service_config, storage_config
from _container import DockerContainer
from _data.docker import docker_volume
from _network.tailscale import tailscale_device
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_webdav_storage_config = service_config["webdav-storage"]

_webdav_storage_volume = container_storage_config["webdav-storage"]
_ftp_storage_volume = container_storage_config["ftp-storage"]


class CentralStorage(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "service:index:CentralStorage", "central-storage", None, child_opts
        )
        self.__child_opts = ResourceOptions(parent=self)

        self.__webdav_container = DockerContainer.build(
            "webdav-storage",
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[traefik_proxy.dynamic_config["webdav-storage"]["file"]],
                )
            ),
            image="rclone",
            command=[
                "--config",
                os.fspath(
                    Path(
                        _webdav_storage_volume["config"]["dir"],
                    )
                    / docker_volume.rclone_config_path
                ),
                "-v",
                "serve",
                "webdav",
                "crypt-{}-central:".format(storage_config["bucket"]),
                "--addr",
                "0.0.0.0:{}".format(_webdav_storage_config["port"]),
            ],
            labels={"rclone-plugin-alias": docker_volume.rclone_plugin_alias},
        )

        self.__ftp_container = DockerContainer.build(
            "ftp-storage",
            opts=self.__child_opts,
            image="rclone",
            command=[
                "--config",
                os.fspath(
                    Path(
                        _ftp_storage_volume["config"]["dir"],
                    )
                    / docker_volume.rclone_config_path
                ),
                "-v",
                "serve",
                "ftp",
                "crypt-{}-central:".format(storage_config["bucket"]),
                "--addr",
                "0.0.0.0:2121",
            ],
            network_mode=Output.concat("container:", tailscale_device.container_id),
            labels={"rclone-plugin-alias": docker_volume.rclone_plugin_alias},
        )

        self.webdav_container_id = self.__webdav_container.id
        self.ftp_container_id = self.__ftp_container.id
        self.register_outputs(
            {
                "webdav_container_id": self.webdav_container_id,
                "ftp_container_id": self.ftp_container_id,
            }
        )


central_storage = CentralStorage()

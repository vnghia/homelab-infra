import os
from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import container_storage_config, service_config, storage_config
from _container import DockerContainer
from _data.docker import docker_volume
from _network.traefik import traefik_proxy
from _secret import secret
from _service.resource import child_opts

_webdav_storage_config = service_config["webdav-storage"]
_webdav_storage_volume = container_storage_config["webdav-storage"]


class WebdavStorage(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "service:index:WebdavStorage", "webdav-storage", None, child_opts
        )
        self.__container = DockerContainer.build(
            "webdav-storage",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["webdav-storage"]["file"]],
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
                "bucket:{}/webdav/".format(storage_config["bucket"]),
                "--addr",
                "0.0.0.0:{}".format(_webdav_storage_config["port"]),
                "--user",
                secret.accounts["webdav-storage"]["username"],
                "--pass",
                secret.accounts["webdav-storage"]["password"],
            ],
            labels={"rclone-plugin-alias": docker_volume.rclone_plugin_alias},
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


webdav_storage = WebdavStorage()

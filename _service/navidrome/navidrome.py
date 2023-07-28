from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import container_storage_config
from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_navidrome_volume = container_storage_config["navidrome"]


class Navidrome(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Navidrome", "navidrome", None, child_opts)
        self.__child_opts = ResourceOptions(
            parent=self, depends_on=[traefik_proxy.dynamic_config["navidrome"]["file"]]
        )

        self.__navidrome_config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "config.py"
        )
        self.__container = DockerContainer.build(
            "navidrome",
            opts=self.__child_opts,
            envs={
                "ND_CONFIGFILE": "{}{}".format(
                    _navidrome_volume["data"]["dir"],
                    self.__navidrome_config["config"]["path"],
                )
            },
            labels={"navidrome-config-sha256": self.__navidrome_config["sha256"]},
            wait=True,
        )

        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


navidrome = Navidrome()

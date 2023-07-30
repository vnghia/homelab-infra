from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _network.resource import child_opts


class Wireguard(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:vpn:Wireguard", "wireguard", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__wireguard_config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "config.py"
        )

        self.__container = DockerContainer.build(
            "wireguard",
            opts=ResourceOptions(parent=self),
            capabilities=docker.ContainerCapabilitiesArgs(adds=["NET_ADMIN"]),
            sysctls={"net.ipv4.conf.all.src_valid_mark": "1"},
            uploads=[self.__wireguard_config["docker"]],
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


wireguard = Wireguard()

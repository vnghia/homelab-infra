from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _service.resource import child_opts


class Dendrite(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Dendrite", "dendrite", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__template = Template(self.__child_opts)

        self.__config = self.__template.build(
            module_path=Path(__file__).parent / "config.py"
        )
        self.__key = self.__template.build(module_path=Path(__file__).parent / "key.py")

        self.__container = DockerContainer.build(
            "dendrite",
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[traefik_proxy.dynamic_config["dendrite"]["file"]],
                )
            ),
            labels={
                "config-sha256": self.__config["sha256"],
                "key-sha256": self.__key["sha256"],
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


dendrite = Dendrite()

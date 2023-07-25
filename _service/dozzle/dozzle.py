from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts


class Dozzle(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Dozzle", "dozzle", None, child_opts)
        self.__container = DockerContainer.build(
            "dozzle",
            opts=ResourceOptions(parent=self),
            envs={"DOZZLE_BASE": "/log"},
            volumes={"/var/run/docker.sock": {"ro": True}},
            labels={
                "traefik-config-sha256": traefik_proxy.dynamic_config["dozzle"][
                    "sha256"
                ]
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


dozzle = Dozzle()

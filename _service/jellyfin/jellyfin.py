from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts


class Jellyfin(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Jellyfin", "jellyfin", None, child_opts)
        self.__container = DockerContainer.build(
            "jellyfin",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["jellyfin"]["file"]],
            ),
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


jellyfin = Jellyfin()

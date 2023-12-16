from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.navidrome.envs import envs
from _service.resource import child_opts


class Navidrome(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Navidrome", "navidrome", None, child_opts)
        self.__container = DockerContainer.build(
            "navidrome",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["navidrome"]["file"]],
            ),
            envs=envs,
            wait=True,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


navidrome = Navidrome()

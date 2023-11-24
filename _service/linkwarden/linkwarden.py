from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.linkwarden.envs import envs
from _service.resource import child_opts


class Linkwarden(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Linkwarden", "linkwarden", None, child_opts)
        self.__container = DockerContainer.build(
            "linkwarden",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["linkwarden"]["file"]],
            ),
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


linkwarden = Linkwarden()

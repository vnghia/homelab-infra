from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.monica.envs import envs
from _service.resource import child_opts


class Monica(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Monica", "monica", None, child_opts)
        self.__container = DockerContainer.build(
            "monica",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["monica"]["file"]],
            ),
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


monica = Monica()
